# -*- coding: utf-8 -*-
"""SGIAD - Module Suivi des Projets (Phase 1 - Fondations).
Tableau de bord, alertes, saisie trimestrielle (prochain prompt)."""
import os
import traceback
import unicodedata
from datetime import date, timedelta
from flask import Blueprint, jsonify, request, send_from_directory

from db import get_supabase

bp = Blueprint('suivi', __name__)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))


def _strip_accents(s):
    if not isinstance(s, str):
        return s
    return ''.join(c for c in unicodedata.normalize('NFD', s)
                   if unicodedata.category(c) != 'Mn')


def _to_int(v, default=0):
    try:
        return int(float(v))
    except (TypeError, ValueError):
        return default


def _to_float(v, default=0.0):
    try:
        return float(v)
    except (TypeError, ValueError):
        return default


def _iso(v):
    return str(v or '')[:10]


def _ensure_suivi_trimestriel_table():
    """Cree la table suivi_trimestriel si elle n'existe pas (schema professionnel)."""
    try:
        sb = get_supabase()
        sb.rpc('exec_sql', {'sql': """
            CREATE TABLE IF NOT EXISTS suivi_trimestriel (
                id              BIGSERIAL PRIMARY KEY,
                code_projet     TEXT NOT NULL,
                annee           INTEGER NOT NULL,
                trimestre       TEXT NOT NULL CHECK (trimestre IN ('T1','T2','T3','T4')),
                cible_physique         NUMERIC(5,2),
                realise_physique       NUMERIC(5,2),
                cible_financiere       NUMERIC(5,2),
                realise_financier      NUMERIC(5,2),
                montant_decaisse_trimestre BIGINT DEFAULT 0,
                montant_cumule         BIGINT DEFAULT 0,
                faits_marquants        TEXT,
                difficultes            TEXT,
                saisi_par              TEXT,
                saisi_le               TIMESTAMPTZ DEFAULT NOW(),
                UNIQUE(code_projet, annee, trimestre)
            );
            CREATE INDEX IF NOT EXISTS idx_suivi_code_projet
                ON suivi_trimestriel(code_projet);
            CREATE INDEX IF NOT EXISTS idx_suivi_annee_trim
                ON suivi_trimestriel(annee, trimestre);
        """}).execute()
    except Exception:
        # Fallback : creation via psycopg2 direct si exec_sql n'existe pas
        try:
            import psycopg2
            url = os.environ.get('SUPABASE_URL', '')
            project_ref = url.replace('https://', '').replace('.supabase.co', '').split('/')[0]
            db_password = os.environ.get('SUPABASE_DB_PASSWORD', '')
            conn = psycopg2.connect(
                host=f'db.{project_ref}.supabase.co',
                port=5432, dbname='postgres',
                user='postgres', password=db_password
            )
            cur = conn.cursor()
            cur.execute("""
                CREATE TABLE IF NOT EXISTS suivi_trimestriel (
                    id              BIGSERIAL PRIMARY KEY,
                    code_projet     TEXT NOT NULL,
                    annee           INTEGER NOT NULL,
                    trimestre       TEXT NOT NULL CHECK (trimestre IN ('T1','T2','T3','T4')),
                    cible_physique         NUMERIC(5,2),
                    realise_physique       NUMERIC(5,2),
                    cible_financiere       NUMERIC(5,2),
                    realise_financier      NUMERIC(5,2),
                    montant_decaisse_trimestre BIGINT DEFAULT 0,
                    montant_cumule         BIGINT DEFAULT 0,
                    faits_marquants        TEXT,
                    difficultes            TEXT,
                    saisi_par              TEXT,
                    saisi_le               TIMESTAMPTZ DEFAULT NOW(),
                    UNIQUE(code_projet, annee, trimestre)
                );
                CREATE INDEX IF NOT EXISTS idx_suivi_code_projet
                    ON suivi_trimestriel(code_projet);
                CREATE INDEX IF NOT EXISTS idx_suivi_annee_trim
                    ON suivi_trimestriel(annee, trimestre);
            """)
            conn.commit()
            cur.close(); conn.close()
        except Exception as e:
            traceback.print_exc()


@bp.route('/suivi')
def suivi_page():
    """Page HTML du module (sera construite au prochain prompt)."""
    return send_from_directory(os.path.join(BASE_DIR, 'modules'), 'suivi.html')


@bp.route('/api/suivi/dashboard')
def suivi_dashboard():
    """Tableau de bord : KPIs, repartitions, alertes, projets en cours."""
    try:
        from auth import require_auth as _ra
    except Exception:
        _ra = None

    try:
        sb = get_supabase()

        # --- Projets (accords consolides) ---
        resp = sb.table('accords_consolides').select(
            'code_projet, objet_accord, partenaire, secteur_principal, '
            'montant_total_fcfa, date_signature, annee_signature, '
            'date_cloture, nouvelle_date_cloture, annee_cloture, statut'
        ).execute()
        rows = resp.data or []

        today = date.today()
        auj_iso = today.isoformat()
        dans_12_mois = (today + timedelta(days=365)).isoformat()

        # Trimestre civil en cours
        mois = today.month
        trimestre_courant = 'T' + str((mois - 1) // 3 + 1)
        annee_courante = today.year

        en_cours = []
        alertes = []
        partenaires_actifs = set()
        montant_total = 0.0
        total_projets = len(rows)

        for r in rows:
            partenaire = str(r.get('partenaire') or '').strip()
            emprunt = 'EMPRUNT OBLIGATAIRE' in _strip_accents(partenaire).upper()
            if emprunt:
                continue

            ref = _iso(r.get('nouvelle_date_cloture')) or _iso(r.get('date_cloture'))
            actif = False
            retard = False
            if ref:
                actif = ref >= auj_iso
                if ref < auj_iso:
                    retard = True
            else:
                try:
                    actif = int(r.get('annee_cloture') or 0) >= today.year
                except Exception:
                    actif = True

            if not actif:
                continue

            code = r.get('code_projet') or ''
            montant = _to_float(r.get('montant_total_fcfa'))
            en_cours.append({
                'code': code,
                'objet': (r.get('objet_accord') or code)[:60],
                'partenaire': partenaire,
                'secteur': r.get('secteur_principal') or 'Non precise',
                'montant_fcfa': montant,
                'statut': r.get('statut') or 'En cours',
                'date_cloture': ref,
                'retard': retard,
            })
            if partenaire:
                partenaires_actifs.add(partenaire)
            montant_total += montant

            # Alerte : retard (cloture depassee)
            if retard:
                alertes.append({
                    'code': code, 'partenaire': partenaire,
                    'type': 'Retard', 'niveau': 'critique',
                    'detail': f'Date de cloture depassee ({ref})'
                })
            # Alerte : cloture proche et faible execution (completee plus bas)
            elif ref and ref <= dans_12_mois:
                alertes.append({
                    'code': code, 'partenaire': partenaire,
                    'type': 'Cloture proche', 'niveau': 'eleve',
                    'detail': f'Cloture prevue le {ref}'
                })

            # Alerte : donnees manquantes
            manquants = []
            if not montant:
                manquants.append('montant')
            if not partenaire:
                manquants.append('partenaire')
            if not (r.get('secteur_principal') or '').strip():
                manquants.append('secteur')
            if not ref:
                manquants.append('date cloture')
            if manquants:
                alertes.append({
                    'code': code, 'partenaire': partenaire,
                    'type': 'Donnees manquantes', 'niveau': 'moyen',
                    'detail': 'Champs absents : ' + ', '.join(manquants)
                })

        # --- Suivi trimestriel ---
        try:
            resp2 = sb.table('suivi_trimestriel').select('*').execute()
            suivis = resp2.data or []
        except Exception:
            suivis = []

        # Dernier taux par projet (tri annee+trimestre)
        def _cle_tri(s):
            t = {'T1': 1, 'T2': 2, 'T3': 3, 'T4': 4}.get(s.get('trimestre'), 0)
            return (_to_int(s.get('annee')), t)

        par_code = {}
        for s in suivis:
            c = s.get('code_projet')
            if not c:
                continue
            par_code.setdefault(c, []).append(s)
        dernier_taux = {}
        for c, lst in par_code.items():
            lst.sort(key=_cle_tri)
            last = lst[-1]
            dernier_taux[c] = {
                'phys': _to_float(last.get('realise_physique')),
                'fin': _to_float(last.get('realise_financier')),
                'annee': _to_int(last.get('annee')),
                'trim': last.get('trimestre'),
            }

        # Alerte : rapport manquant pour le trimestre civil en cours
        if suivis:
            for p in en_cours:
                t = dernier_taux.get(p['code'])
                if not t or t['annee'] != annee_courante or t['trim'] != trimestre_courant:
                    alertes.append({
                        'code': p['code'], 'partenaire': p['partenaire'],
                        'type': 'Rapport manquant', 'niveau': 'moyen',
                        'detail': f'Aucune saisie pour {trimestre_courant} {annee_courante}'
                    })

        # Complete l'alerte "Cloture proche" si execution < 70 %
        for al in alertes:
            if al['type'] == 'Cloture proche':
                t = dernier_taux.get(al['code'])
                if t and t['phys'] < 70:
                    al['detail'] += f" et execution physique {t['phys']:.0f}% < 70%"
                    al['niveau'] = 'critique'

        # Taux moyens
        phys_vals = [t['phys'] for t in dernier_taux.values() if t['phys'] > 0]
        fin_vals = [t['fin'] for t in dernier_taux.values() if t['fin'] > 0]
        taux_phys_moyen = round(sum(phys_vals) / len(phys_vals), 1) if phys_vals else 0
        taux_fin_moyen = round(sum(fin_vals) / len(fin_vals), 1) if fin_vals else 0

        # Statuts (comptage)
        statuts = {}
        for p in en_cours:
            s = p['statut']
            statuts[s] = statuts.get(s, 0) + 1

        # Secteurs (top 6 + Autres)
        sect = {}
        for p in en_cours:
            s = p['secteur'] or 'Non precise'
            sect[s] = sect.get(s, 0) + p['montant_fcfa']
        sect_tries = sorted(sect.items(), key=lambda x: x[1], reverse=True)
        if len(sect_tries) > 6:
            top = sect_tries[:6]
            autres = sum(v for _, v in sect_tries[6:])
            top.append(('Autres secteurs', autres))
            sect_tries = top
        secteurs = [{'label': k, 'montant_mds': round(v / 1e9, 1)}
                    for k, v in sect_tries]

        # Evolution par annee de signature
        evol = {}
        for r in rows:
            a = _to_int(r.get('annee_signature'))
            if not a or a < 2010:
                continue
            evol[a] = evol.get(a, 0) + _to_float(r.get('montant_total_fcfa'))
        evolution = [{'annee': a, 'montant_mds': round(v / 1e9, 1)}
                     for a, v in sorted(evol.items())]
        cumul = 0.0
        for e in evolution:
            cumul += e['montant_mds']
            e['cumul_mds'] = round(cumul, 1)

        # Projets avec taux
        projets = []
        for p in sorted(en_cours, key=lambda x: x['montant_fcfa'], reverse=True)[:100]:
            t = dernier_taux.get(p['code'], {})
            projets.append({
                'code': p['code'],
                'objet': p['objet'],
                'secteur': p['secteur'],
                'partenaire': p['partenaire'],
                'montant_fcfa': p['montant_fcfa'],
                'taux_phys': t.get('phys', 0),
                'taux_fin': t.get('fin', 0),
                'statut': p['statut'],
                'date_cloture': p['date_cloture'],
            })

        # Tri des alertes : critiques d'abord
        ordre = {'critique': 0, 'eleve': 1, 'moyen': 2, 'information': 3}
        alertes.sort(key=lambda a: ordre.get(a.get('niveau'), 9))
        alertes = alertes[:50]

        return jsonify({
            'kpis': {
                'total_projets': total_projets,
                'projets_en_cours': len(en_cours),
                'montant_total_mds': round(montant_total / 1e9, 1),
                'partenaires_actifs': len(partenaires_actifs),
                'taux_physique_moyen': taux_phys_moyen,
                'taux_financier_moyen': taux_fin_moyen,
                'trimestre_courant': trimestre_courant,
                'annee_courante': annee_courante,
            },
            'statuts': statuts,
            'secteurs': secteurs,
            'evolution': evolution,
            'alertes': alertes,
            'alertes_count': {
                'total': len(alertes),
                'critique': sum(1 for a in alertes if a['niveau'] == 'critique'),
                'eleve': sum(1 for a in alertes if a['niveau'] == 'eleve'),
                'moyen': sum(1 for a in alertes if a['niveau'] == 'moyen'),
            },
            'projets': projets,
        })

    except Exception as e:
        traceback.print_exc()
        return jsonify({'error': f'Erreur moteur suivi : {e}'}), 500


# Creation auto de la table au demarrage
_ensure_suivi_trimestriel_table()
