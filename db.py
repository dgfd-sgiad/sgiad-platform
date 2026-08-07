# -*- coding: utf-8 -*-
"""
DB.PY - Client Supabase et fonctions helper
=============================================
Remplace l'ancien systeme Excel (openpyxl) par Supabase (PostgreSQL cloud).
Toutes les operations de lecture/ecriture passent par ce module.

Variables d'environnement requises :
    SUPABASE_URL  = https://xxxxx.supabase.co
    SUPABASE_KEY  = eyJhbGciOi...  (anon key ou service_role key)
"""

import os
import re
import traceback
from datetime import datetime, date
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()

# ── Client Supabase (singleton) ──
_supabase: Client = None


def get_supabase() -> Client:
    """Retourne le client Supabase (cree a la premiere invocation)."""
    global _supabase
    if _supabase is None:
        url = os.environ.get('SUPABASE_URL')
        key = os.environ.get('SUPABASE_KEY')
        if not url or not key:
            raise RuntimeError(
                "Variables SUPABASE_URL et SUPABASE_KEY manquantes. "
                "Creez un fichier .env ou exportez-les dans l'environnement."
            )
        _supabase = create_client(url, key)
    return _supabase


# ══════════════════════════════════════════════════════════════════════
# MAPPING: noms affiches (Excel) <-> colonnes SQL
# ══════════════════════════════════════════════════════════════════════

# Accords consolides : nom affiche -> colonne SQL
ACCORDS_DISPLAY_TO_DB = {
    "Code Projet": "code_projet",
    "Annee de signature": "annee_signature",
    "Annee de cloture": "annee_cloture",
    "Modalité d'intervention": "modalite_intervention",
    "Objet de l'accord": "objet_accord",
    "Objectif général": "objectif_general",
    "Source vérifiable": "source_verifiable",
    "Partenaire": "partenaire",
    "Sigle_Part": "sigle_part",
    "Secteur principal": "secteur_principal",
    "Nature (Prêt/Don/Mixte)": "nature_pret_don_mixte",
    "Montant_Pret_FCFA": "montant_pret_fcfa",
    "Montant_Don_FCFA": "montant_don_fcfa",
    "Montant_Total_FCFA": "montant_total_fcfa",
    "Devise": "devise",
    "Montant total\n(devise)": "montant_total_devise",
    "Montant total (devise)": "montant_total_devise",
    "Instrument de\nfinancement": "instrument_financement",
    "Instrument de financement": "instrument_financement",
    "Date de\nsignature": "date_signature",
    "Date de signature": "date_signature",
    "Date d'approbation": "date_approbation",
    "Date de clôture": "date_cloture",
    "Date de cl\u00f4ture": "date_cloture",
    "Zone": "zone",
    "APD Oui/non": "apd_oui_non",
    "TYPE DE FINANCEMENT": "type_financement",
    "TYPE DE CONTRIBUTEUR": "type_contributeur",
    "SOUS SECTEUR": "sous_secteur",
    "AXE PAG": "axe_pag",
    "PILIER PAG": "pilier_pag",
    "ODD": "odd",
    "Cible_ODD": "cible_odd",
    "Pilier": "pilier",
    "STATUT (en cours, achevé, en approbation)": "statut",
    "Objectifs spécifiques": "objectifs_specifiques",
    "Resultats attendues": "resultats_attendues",
    "Principales composantes": "principales_composantes",
    "Bénéficiaires directes": "beneficiaires_directes",
    "Population cible": "population_cible",
    "Tutelle": "tutelle",
    "Agence Exécution": "agence_execution",
    # ── Colonnes ajoutees pour completer la fiche de projet ──
    "Duree_Initiale_Mois": "duree_initiale_mois",
    "Date_Demarrage": "date_demarrage",
    "Date entree en vigueur": "date_entree_vigueur",
    "Departement": "departement",
    "Commune": "commune",
    "Niveau": "niveau_intervention",
    "Co_Partenaire_1": "co_partenaire_1",
    "Co_Partenaire_2": "co_partenaire_2",
    "Co_Partenaire_3": "co_partenaire_3",
    "Co_Partenaire_4": "co_partenaire_4",
    "Co_Partenaire_5": "co_partenaire_5",
    "Co_Partenaire_6": "co_partenaire_6",
    "Co_Partenaire_7": "co_partenaire_7",
    "Adresse partenaire": "adresse_partenaire",
    "Contact partenaire": "contact_partenaire",
    "Site web partenaire": "site_web_partenaire",
    "Taux execution physique": "taux_execution_physique",
    "Taux de decaissement": "taux_decaissement",
    "Niveau de risque": "niveau_risque",
    "Nb avenants": "nb_avenants",
    "Nb prorogations": "nb_prorogations",
    "Responsable de suivi": "responsable_suivi",
    "Chef de projet": "chef_projet",
    "Coordonnees": "coordonnees_chef",
    "Observations": "observations",
}

# Reverse: colonne SQL -> nom affiche
ACCORDS_DB_TO_DISPLAY = {v: k for k, v in ACCORDS_DISPLAY_TO_DB.items()
                         if '\n' not in k}  # eviter les doublons avec \n


# ══════════════════════════════════════════════════════════════════════
# ACCORDS CONSOLIDES - CRUD
# ══════════════════════════════════════════════════════════════════════

def accords_list() -> list[dict]:
    """Retourne tous les accords, avec cles au format affiche (Excel-compatibles)."""
    sb = get_supabase()
    resp = sb.table('accords_consolides').select('*').order('code_projet').execute()
    return [_db_to_display(row) for row in resp.data]


def accords_get(code_projet: str) -> dict | None:
    """Retourne un accord par son code_projet."""
    sb = get_supabase()
    resp = sb.table('accords_consolides').select('*').eq(
        'code_projet', code_projet).execute()
    if not resp.data:
        return None
    return _db_to_display(resp.data[0])


def accords_insert(data: dict) -> dict:
    """Insere un nouvel accord. `data` utilise les cles affichees."""
    sb = get_supabase()
    db_row = _display_to_db(data)
    resp = sb.table('accords_consolides').insert(db_row).execute()
    return _db_to_display(resp.data[0]) if resp.data else {}


def accords_update(code_projet: str, data: dict) -> dict:
    """Met a jour un accord existant. `data` utilise les cles affichees."""
    sb = get_supabase()
    db_row = _display_to_db(data)
    db_row.pop('code_projet', None)  # ne pas modifier la cle primaire
    if not db_row:
        return {}
    resp = sb.table('accords_consolides').update(db_row).eq(
        'code_projet', code_projet).execute()
    return _db_to_display(resp.data[0]) if resp.data else {}


def accords_delete(code_projet: str) -> bool:
    """Supprime un accord par son code_projet."""
    sb = get_supabase()
    resp = sb.table('accords_consolides').delete().eq(
        'code_projet', code_projet).execute()
    return len(resp.data) > 0 if resp.data else False


# ══════════════════════════════════════════════════════════════════════
# METADATA COLONNES (remplace get_columns_meta())
# ══════════════════════════════════════════════════════════════════════

# ── Sync des valeurs depuis accords_consolides vers parametres ──
_SYNCED = False

def sync_parametres_from_data():
    """Synchronise les valeurs distinctes de accords_consolides vers parametres.
    Assure que chaque valeur d'un champ select dans les donnees existe dans
    parametres, pour que la gestion (ajout/modif/suppr) fonctionne toujours.
    Ne s'execute qu'une seule fois par demarrage.
    """
    global _SYNCED
    if _SYNCED:
        return
    _SYNCED = True

    SELECT_DISPLAY_TO_DB = {
        'Secteur principal': 'secteur_principal',
        'SOUS SECTEUR': 'sous_secteur',
        "Modalit\u00e9 d'intervention": 'modalite_intervention',
        'Nature (Pr\u00eat/Don/Mixte)': 'nature_pret_don_mixte',
        'Devise': 'devise',
        'APD Oui/non': 'apd_oui_non',
        'TYPE DE FINANCEMENT': 'type_financement',
        'TYPE DE CONTRIBUTEUR': 'type_contributeur',
        'Instrument de financement': 'instrument_financement',
        'Cible_ODD': 'cible_odd',
        'AXE PAG': 'axe_pag',
        'PILIER PAG': 'pilier_pag',
        'ODD': 'odd',
        'Pilier': 'pilier',
        'STATUT (en cours, achev\u00e9, en approbation)': 'statut',
        'Tutelle': 'tutelle',
        'Agence Ex\u00e9cution': 'agence_execution',
        'Partenaire': 'partenaire',
    }

    try:
        sb = get_supabase()
        # Recuperer toutes les valeurs existantes dans parametres
        param_resp = sb.table('parametres').select('categorie', 'valeur').execute()
        existing = set()
        for row in (param_resp.data or []):
            existing.add((str(row.get('categorie','')).strip(), str(row.get('valeur','')).strip()))

        # Recuperer TOUTES les colonnes select d'un seul coup (plus rapide)
        db_cols = list(SELECT_DISPLAY_TO_DB.values())
        try:
            resp = sb.table('accords_consolides').select(','.join(db_cols)).execute()
            rows_data = resp.data or []
        except Exception:
            rows_data = []

        to_insert = []
        for row in rows_data:
            for display_name, db_col in SELECT_DISPLAY_TO_DB.items():
                val = str(row.get(db_col, '')).strip()
                if val and (display_name, val) not in existing:
                    to_insert.append({'categorie': display_name, 'valeur': val})
                    existing.add((display_name, val))

        if to_insert:
            # Inserer par batch de 100
            for i in range(0, len(to_insert), 100):
                batch = to_insert[i:i+100]
                try:
                    sb.table('parametres').insert(batch).execute()
                except Exception:
                    # Inserer un par un si le batch echoue
                    for item in batch:
                        try:
                            sb.table('parametres').insert(item).execute()
                        except Exception:
                            pass
            print(f"[sync_parametres] {len(to_insert)} valeurs synchronisees vers parametres")
    except Exception as e:
        print(f"[sync_parametres] Erreur: {e}")


def get_columns_meta() -> list[dict]:
    """Retourne la metadata des colonnes pour le frontend.
    Remplace l'ancienne fonction qui lisait les en-tetes Excel.
    Lit depuis la table colonnes_meta si peuplee, sinon genere depuis
    ACCORDS_DISPLAY_TO_DB.
    Synchronise puis utilise parametres comme source unique des options select.
    """
    # Synchroniser les valeurs de accords_consolides vers parametres (one-time)
    try:
        sync_parametres_from_data()
    except Exception:
        pass

    sb = get_supabase()
    columns = None
    try:
        resp = sb.table('colonnes_meta').select('*').eq(
            'table_name', 'accords_consolides').order('col_order').execute()
        if resp.data:
            columns = [
                {
                    'key': r['column_key'],
                    'col_letter': '',
                    'type': r['col_type'],
                    'readonly': r['readonly'],
                    'options': [],  # sera rempli depuis parametres
                }
                for r in resp.data
            ]
    except Exception:
        pass

    if columns is None:
        # Fallback: generer depuis le mapping statique
        columns = _generate_columns_meta_fallback()

    # Utiliser parametres comme source unique des options pour les champs select
    try:
        param_resp = sb.table('parametres').select('categorie', 'valeur').execute()
        if param_resp.data:
            from collections import defaultdict
            param_by_cat = defaultdict(set)
            for row in param_resp.data:
                cat = str(row.get('categorie', '')).strip()
                val = str(row.get('valeur', '')).strip()
                if cat and val:
                    param_by_cat[cat].add(val)
            # Remplacer les options des colonnes select par les valeurs de parametres
            for col in columns:
                if col['type'] == 'select' and col['key'] in param_by_cat:
                    col['options'] = sorted(param_by_cat[col['key']])
    except Exception:
        pass

    return columns


def _generate_columns_meta_fallback() -> list[dict]:
    """Genere une metadata basique depuis le mapping si colonnes_meta est vide."""
    NUMBER_FIELDS = {
        'annee_signature', 'annee_cloture', 'montant_pret_fcfa',
        'montant_don_fcfa', 'montant_total_fcfa', 'montant_total_devise',
        'duree_initiale_mois', 'nb_avenants', 'nb_prorogations',
        'taux_execution_physique', 'taux_decaissement',
    }
    DATE_FIELDS = {'date_signature', 'date_approbation', 'date_cloture',
                   'date_demarrage', 'date_entree_vigueur'}
    READONLY_FIELDS = {'annee_cloture'}
    SELECT_FIELDS = {
        'modalite_intervention', 'secteur_principal', 'sous_secteur',
        'nature_pret_don_mixte', 'devise', 'apd_oui_non', 'type_financement',
        'type_contributeur', 'instrument_financement', 'cible_odd',
        'axe_pag', 'pilier_pag', 'odd', 'pilier', 'statut',
        'tutelle', 'agence_execution', 'partenaire',
    }

    # Pre-fetch distinct values for select fields
    select_options = {}
    sb = get_supabase()
    for db_col in SELECT_FIELDS:
        try:
            resp = sb.table('accords_consolides').select(db_col).execute()
            vals = sorted(set(
                str(r[db_col]).strip()
                for r in resp.data
                if r.get(db_col) and str(r[db_col]).strip()
            ))
            select_options[db_col] = vals
        except Exception:
            select_options[db_col] = []

    columns = []
    seen = set()
    order = 0
    for display_name, db_col in ACCORDS_DISPLAY_TO_DB.items():
        if db_col in seen or '\n' in display_name:
            continue
        seen.add(db_col)
        order += 1

        if db_col in NUMBER_FIELDS:
            col_type = 'number'
        elif db_col in DATE_FIELDS:
            col_type = 'date'
        elif db_col in SELECT_FIELDS:
            col_type = 'select'
        else:
            col_type = 'text'

        columns.append({
            'key': display_name,
            'col_letter': '',
            'type': col_type,
            'readonly': db_col in READONLY_FIELDS,
            'options': select_options.get(db_col, []) if col_type == 'select' else [],
        })
    return columns


# ══════════════════════════════════════════════════════════════════════
# LOCALISATION
# ══════════════════════════════════════════════════════════════════════

_localisation_cache = None


def get_localisation_tree(force_reload=False) -> dict:
    """Retourne l'arbre de localisation (Departement > Commune > Arr > Village)."""
    global _localisation_cache
    if _localisation_cache is not None and not force_reload:
        return _localisation_cache

    sb = get_supabase()

    # Supabase limits to 1000 rows per request — paginate to get all
    all_rows = []
    page_size = 1000
    offset = 0
    while True:
        resp = sb.table('localisation').select('*').order('departement').range(offset, offset + page_size - 1).execute()
        all_rows.extend(resp.data)
        if len(resp.data) < page_size:
            break
        offset += page_size

    tree = {}
    for row in all_rows:
        dep = row['departement']
        com = row['commune']
        arr = row['arrondissement']
        vil = row['village']
        tree.setdefault(dep, {}).setdefault(com, {}).setdefault(arr, [])
        tree[dep][com][arr].append(vil)

    _localisation_cache = tree
    return tree


# ══════════════════════════════════════════════════════════════════════
# PARAMETRES
# ══════════════════════════════════════════════════════════════════════

def get_parametres(categorie: str = None) -> dict | list:
    """Retourne les parametres, optionnellement filtres par categorie."""
    sb = get_supabase()
    query = sb.table('parametres').select('*').order('categorie, ordre')
    if categorie:
        query = query.eq('categorie', categorie)
    resp = query.execute()

    if categorie:
        return [r['valeur'] for r in resp.data]

    # Grouper par categorie
    result = {}
    for r in resp.data:
        result.setdefault(r['categorie'], []).append(r['valeur'])
    return result


# ══════════════════════════════════════════════════════════════════════
# SESSION LOG
# ══════════════════════════════════════════════════════════════════════

def log_session(ip_address: str, user_email: str = None) -> dict:
    """Enregistre une connexion et retourne les infos de session."""
    sb = get_supabase()
    now = datetime.now().isoformat()

    # Compter les connexions existantes
    resp = sb.table('session_log').select('total_connexions').order(
        'id', desc=True).limit(1).execute()
    total = (resp.data[0]['total_connexions'] + 1) if resp.data else 1

    # Inserer la nouvelle session
    sb.table('session_log').insert({
        'ip_address': ip_address,
        'user_email': user_email,
        'derniere_connexion': now,
        'total_connexions': total,
    }).execute()

    # Derniere connexion precedente
    prev = None
    if resp.data:
        prev_resp = sb.table('session_log').select('derniere_connexion').order(
            'id', desc=True).limit(1).offset(1).execute()
        if prev_resp.data:
            prev = prev_resp.data[0]['derniere_connexion']

    return {
        'ip': ip_address,
        'derniere_connexion': prev,
        'total_connexions': total,
    }


# ══════════════════════════════════════════════════════════════════════
# CONVERSION: display keys <-> db keys
# ══════════════════════════════════════════════════════════════════════

def _display_to_db(data: dict) -> dict:
    """Convertit un dict avec cles affichees -> cles SQL."""
    result = {}
    for key, value in data.items():
        db_col = ACCORDS_DISPLAY_TO_DB.get(key, key)
        # Nettoyer les valeurs vides
        if value is not None and str(value).strip() not in ('', 'nan', 'None'):
            # Colonnes DATE : convertir le format francais JJ/MM/AAAA en ISO
            if db_col.startswith('date_'):
                m = re.match(r'^(\d{1,2})/(\d{1,2})/(\d{4})$', str(value).strip())
                if m:
                    value = f"{m.group(3)}-{m.group(2).zfill(2)}-{m.group(1).zfill(2)}"
            result[db_col] = value
    return result


def _db_to_display(row: dict) -> dict:
    """Convertit un dict avec cles SQL -> cles affichees."""
    result = {}
    for db_col, value in row.items():
        if db_col in ('id', 'created_at'):
            continue
        # Date de derniere mise a jour (fiche de projet)
        if db_col == 'updated_at':
            if value:
                try:
                    dt = datetime.fromisoformat(str(value).replace('Z', '+00:00'))
                    result['Date_MAJ'] = dt.strftime('%d/%m/%Y')
                except (ValueError, TypeError):
                    result['Date_MAJ'] = value
            continue
        display_key = ACCORDS_DB_TO_DISPLAY.get(db_col, db_col)
        # Convertir les dates
        if isinstance(value, str) and 'T' in value and db_col.startswith('date_'):
            try:
                dt = datetime.fromisoformat(value.replace('Z', '+00:00'))
                value = dt.strftime('%d/%m/%Y')
            except (ValueError, TypeError):
                pass
        result[display_key] = value if value is not None else ''
    return result
