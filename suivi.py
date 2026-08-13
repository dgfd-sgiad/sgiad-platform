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


def _ensure_revues_tables():
    try:
        import psycopg2
        url = os.environ.get('SUPABASE_URL', '')
        project_ref = url.replace('https://', '').replace('.supabase.co', '').split('/')[0]
        db_password = os.environ.get('SUPABASE_DB_PASSWORD', '')
        conn = psycopg2.connect(host=f'db.{project_ref}.supabase.co', port=5432,
                                dbname='postgres', user='postgres', password=db_password)
        cur = conn.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS revues (
                id BIGSERIAL PRIMARY KEY,
                date_revue DATE NOT NULL,
                partenaire TEXT,
                type_revue TEXT,
                lieu TEXT,
                statut TEXT DEFAULT 'Planifiée'
            );
            CREATE TABLE IF NOT EXISTS recommandations (
                id BIGSERIAL PRIMARY KEY,
                texte TEXT NOT NULL,
                revue_origine TEXT,
                partenaire TEXT,
                statut TEXT DEFAULT 'A démarrer',
                echeance DATE,
                avancement INTEGER DEFAULT 0
            );
        """)
        cur.execute("SELECT COUNT(*) FROM revues")
        if cur.fetchone()[0] == 0:
            cur.execute("""INSERT INTO revues (date_revue, partenaire, type_revue, lieu, statut) VALUES
              ('2026-09-05','Banque Ouest Africaine de Développement','Revue semestrielle','Cotonou','Planifiée'),
              ('2026-09-15','Banque mondiale','Revue semestrielle','Cotonou','Confirmée'),
              ('2026-09-22','Agence Française de Développement','Revue annuelle','Paris','En préparation'),
              ('2026-09-29','Union Européenne','Revue annuelle','Cotonou','En préparation')""")
        cur.execute("SELECT COUNT(*) FROM recommandations")
        if cur.fetchone()[0] == 0:
            cur.execute("""INSERT INTO recommandations (texte, revue_origine, partenaire, statut, echeance) VALUES
              ('Accélérer les procédures de passation des marchés','Revue BM Nov. 2025','Banque mondiale','En cours','2026-09-30'),
              ('Renforcer le suivi environnemental et social des projets financés','Revue AFD Déc. 2025','Agence Française de Développement','En cours','2026-07-15'),
              ('Finaliser les études techniques des projets d''eau et assainissement','Revue BAD Oct. 2025','Banque Africaine de Développement','A démarrer','2026-08-31'),
              ('Mettre à jour la base des bénéficiaires des projets agricoles','Revue BOAD Déc. 2025','Banque Ouest Africaine de Développement','A démarrer','2026-08-15')""")
        conn.commit()
        cur.close(); conn.close()
    except Exception:
        traceback.print_exc()


@bp.route('/suivi')
def suivi_page():
    """Page HTML du module (sera construite au prochain prompt)."""
    return send_from_directory(os.path.join(BASE_DIR, 'modules'), 'suivi.html')


def _current_role():
    try:
        auth_header = request.headers.get('Authorization', '') or ''
        token = auth_header.replace('Bearer ', '').strip()
        if not token:
            return 'lecture', ''
        sb = get_supabase()
        resp = sb.auth.get_user(token)
        email = ((resp.user.email or '') if resp and resp.user else '').lower()
        if not email:
            return 'lecture', ''
        admins = [e.strip().lower() for e in os.environ.get('ADMIN_EMAILS', 'ekouhontode@finances.bj').split(',') if e.strip()]
        saisies = [e.strip().lower() for e in os.environ.get('SUIVI_SAISIE_EMAILS', '').split(',') if e.strip()]
        if email in admins:
            return 'admin', email
        if email in saisies:
            return 'saisie', email
        return 'lecture', email
    except Exception:
        traceback.print_exc()
        return 'lecture', ''


@bp.route('/api/suivi/role')
def suivi_role():
    role, email = _current_role()
    return jsonify({'role': role, 'email': email})


@bp.route('/api/suivi/revues', methods=['POST'])
def suivi_add_revue():
    role, email = _current_role()
    if role not in ('admin', 'saisie'):
        return jsonify({'error': 'Droit de saisie requis.'}), 403
    data = request.get_json(force=True) or {}
    if not data.get('date_revue'):
        return jsonify({'error': 'Date de revue requise.'}), 400
    validation = 'valide' if role == 'admin' else 'en_attente'
    try:
        sb = get_supabase()
        sb.table('revues').insert({
            'date_revue': data.get('date_revue'),
            'partenaire': data.get('partenaire') or '',
            'type_revue': data.get('type_revue') or 'Revue semestrielle',
            'lieu': data.get('lieu') or 'Cotonou',
            'statut': data.get('statut') or 'Planifiée',
            'statut_validation': validation,
        }).execute()
        msg = 'Revue ajoutée.' if role == 'admin' else 'Revue proposée (en attente de validation).'
        return jsonify({'ok': True, 'message': msg})
    except Exception as e:
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500


@bp.route('/api/suivi/recommandations', methods=['POST'])
def suivi_add_reco():
    role, email = _current_role()
    if role not in ('admin', 'saisie'):
        return jsonify({'error': 'Droit de saisie requis.'}), 403
    data = request.get_json(force=True) or {}
    if not data.get('texte'):
        return jsonify({'error': 'Texte de la recommandation requis.'}), 400
    validation = 'valide' if role == 'admin' else 'en_attente'
    try:
        sb = get_supabase()
        sb.table('recommandations').insert({
            'texte': data.get('texte'),
            'revue_origine': data.get('revue_origine') or '',
            'partenaire': data.get('partenaire') or '',
            'statut': data.get('statut') or 'A démarrer',
            'echeance': data.get('echeance') or None,
            'statut_validation': validation,
            'revue_id': (int(data['revue_id']) if data.get('revue_id') else None),
            'projet': data.get('projet') or '',
            'difficulte': data.get('difficulte') or '',
            'responsable_direct': data.get('responsable_direct') or '',
            'associe': data.get('associe') or '',
            'commentaires': data.get('commentaires') or '',
        }).execute()
        msg = 'Recommandation ajoutée.' if role == 'admin' else 'Recommandation proposée (en attente de validation).'
        return jsonify({'ok': True, 'message': msg})
    except Exception as e:
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500


@bp.route('/api/suivi/revues/executer', methods=['POST'])
def suivi_executer_revue():
    role, email = _current_role()
    if role not in ('admin', 'saisie'):
        return jsonify({'error': 'Droit de saisie requis.'}), 403
    data = request.get_json(force=True) or {}
    rid = data.get('id')
    if not rid:
        return jsonify({'error': 'Id manquant.'}), 400
    try:
        sb = get_supabase()
        sb.table('revues').update({'executee': True, 'date_reelle': data.get('date_reelle') or date.today().isoformat()}).eq('id', rid).execute()
        return jsonify({'ok': True, 'message': 'Revue marquee executee.'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/api/suivi/revues/annuler', methods=['POST'])
def suivi_annuler_revue():
    role, email = _current_role()
    if role not in ('admin', 'saisie'):
        return jsonify({'error': 'Droit de saisie requis.'}), 403
    data = request.get_json(force=True) or {}
    rid = data.get('id')
    if not rid:
        return jsonify({'error': 'Id manquant.'}), 400
    try:
        sb = get_supabase()
        sb.table('revues').update({'executee': False, 'date_reelle': None}).eq('id', rid).execute()
        return jsonify({'ok': True, 'message': 'Execution annulee. La revue revient dans le calendrier.'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


    
@bp.route('/api/suivi/recommandations/executer', methods=['POST'])
def suivi_executer_reco():
    role, email = _current_role()
    if role not in ('admin', 'saisie'):
        return jsonify({'error': 'Droit de saisie requis.'}), 403
    data = request.get_json(force=True) or {}
    rid = data.get('id')
    if not rid:
        return jsonify({'error': 'Id manquant.'}), 400
    try:
        sb = get_supabase()
        sb.table('recommandations').update({'executee': True}).eq('id', rid).execute()
        return jsonify({'ok': True, 'message': 'Recommandation marquee executee.'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/api/suivi/revues/update', methods=['POST'])
def suivi_update_revue():
    role, email = _current_role()
    if role not in ('admin', 'saisie'):
        return jsonify({'error': 'Droit de saisie requis.'}), 403
    d = request.get_json(force=True) or {}
    rid = d.get('id')
    if not rid:
        return jsonify({'error': 'Id manquant.'}), 400
    payload = {
        'date_revue': d.get('date_revue'),
        'date_reelle': d.get('date_reelle') or None,
        'partenaire': d.get('partenaire') or '',
        'type_revue': d.get('type_revue') or '',
        'lieu': d.get('lieu') or '',
        'statut': d.get('statut') or 'Planifiée',
    }
    try:
        sb = get_supabase()
        sb.table('revues').update(payload).eq('id', rid).execute()
        return jsonify({'ok': True, 'message': 'Revue modifiée.'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/api/suivi/recommandations/update', methods=['POST'])
def suivi_update_reco():
    role, email = _current_role()
    if role not in ('admin', 'saisie'):
        return jsonify({'error': 'Droit de saisie requis.'}), 403
    d = request.get_json(force=True) or {}
    rid = d.get('id')
    if not rid:
        return jsonify({'error': 'Id manquant.'}), 400
    payload = {
        'texte': d.get('texte'),
        'revue_id': (int(d['revue_id']) if d.get('revue_id') else None),
        'partenaire': d.get('partenaire') or '',
        'projet': d.get('projet') or '',
        'difficulte': d.get('difficulte') or '',
        'responsable_direct': d.get('responsable_direct') or '',
        'associe': d.get('associe') or '',
        'echeance': d.get('echeance') or None,
        'commentaires': d.get('commentaires') or '',
    }
    try:
        sb = get_supabase()
        sb.table('recommandations').update(payload).eq('id', rid).execute()
        return jsonify({'ok': True, 'message': 'Recommandation modifiée.'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/api/suivi/valider', methods=['POST'])
def suivi_valider():
    role, email = _current_role()
    if role != 'admin':
        return jsonify({'error': 'Réservé à l administrateur.'}), 403
    data = request.get_json(force=True) or {}
    table = data.get('table'); rid = data.get('id')
    if table not in ('revues', 'recommandations') or not rid:
        return jsonify({'error': 'Table ou id manquant.'}), 400
    try:
        sb = get_supabase()
        sb.table(table).update({'statut_validation': 'valide'}).eq('id', rid).execute()
        return jsonify({'ok': True, 'message': 'Validé.'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/api/suivi/rejeter', methods=['POST'])
def suivi_rejeter():
    role, email = _current_role()
    if role != 'admin':
        return jsonify({'error': 'Réservé à l administrateur.'}), 403
    data = request.get_json(force=True) or {}
    table = data.get('table'); rid = data.get('id')
    if table not in ('revues', 'recommandations') or not rid:
        return jsonify({'error': 'Table ou id manquant.'}), 400
    try:
        sb = get_supabase()
        sb.table(table).delete().eq('id', rid).execute()
        return jsonify({'ok': True, 'message': 'Proposition rejetée.'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


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
                    actif = int(r.get('annee_cloture')) >= today.year
                except (TypeError, ValueError):
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

        codes_critiques = set(a['code'] for a in alertes if a['niveau'] == 'critique')
        codes_eleves = set(a['code'] for a in alertes if a['niveau'] == 'eleve')
        av = {'en_preparation': 0, 'en_cours_execution': 0, 'en_difficulte': 0, 'a_surveiller': 0}
        for p in en_cours:
            st = str(p['statut']).lower()
            if p['code'] in codes_critiques:
                av['en_difficulte'] += 1
            elif p['code'] in codes_eleves:
                av['a_surveiller'] += 1
            elif 'cours' in st:
                av['en_cours_execution'] += 1
            else:
                av['en_preparation'] += 1
        av['clotures'] = max(0, total_projets - len(en_cours))

        # Tri des alertes : critiques d'abord
        ordre = {'critique': 0, 'eleve': 1, 'moyen': 2, 'information': 3}
        alertes.sort(key=lambda a: ordre.get(a.get('niveau'), 9))
        alertes = alertes[:50]

        revues = []
        try:
            revues = (sb.table('revues').select('*').order('date_revue').execute()).data or []
        except Exception:
            revues = []
        recos = []
        try:
            recos = (sb.table('recommandations').select('*').order('echeance').execute()).data or []
        except Exception:
            recos = []
        revues_a_venir = [r for r in revues if _iso(r.get('date_revue')) >= auj_iso][:6]
        reco_en_retard = [r for r in recos if _iso(r.get('echeance')) and _iso(r.get('echeance')) < auj_iso]
        revues_7j = [r for r in revues if auj_iso <= _iso(r.get('date_revue')) <= (today + timedelta(days=7)).isoformat()]
        codes_projets = [{'code': p['code'], 'objet': p['objet'], 'secteur': p['secteur'], 'partenaire': p['partenaire']} for p in sorted(en_cours, key=lambda x: x['montant_fcfa'], reverse=True)]

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
                'recommandations_en_retard': len(reco_en_retard),
                'revues_7_jours': len(revues_7j),
            },
            'projets': projets,
            'revues': revues,
            'recommandations': recos,
            'avancement': av,
            'partenaires_ptf': sorted(set(p['partenaire'] for p in en_cours if p['partenaire'])),
            'codes_projets': codes_projets,
        })

    except Exception as e:
        traceback.print_exc()
        return jsonify({'error': f'Erreur moteur suivi : {e}'}), 500


# Creation auto de la table au demarrage
_ensure_suivi_trimestriel_table()
_ensure_revues_tables()
