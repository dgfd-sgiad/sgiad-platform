# -*- coding: utf-8 -*-
"""
MIGRATE_TO_SUPABASE.PY
=======================
Migre les donnees de Banque_Projets.xlsx vers Supabase (PostgreSQL).

Usage:
    1. Creez un fichier .env avec SUPABASE_URL et SUPABASE_KEY
    2. Executez le schema.sql dans Supabase (SQL Editor)
    3. Lancez: python scripts/migrate_to_supabase.py
"""

import os
import sys
import re
import time
import pandas as pd
from datetime import datetime

# Ajouter le repertoire parent au path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from supabase import create_client
from dotenv import load_dotenv

load_dotenv()

# ── Configuration ──
SUPABASE_URL = os.environ.get('SUPABASE_URL')
SUPABASE_KEY = os.environ.get('SUPABASE_KEY')
EXCEL_FILE = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'Banque_Projets.xlsx')

if not SUPABASE_URL or not SUPABASE_KEY:
    print("ERREUR: Variables SUPABASE_URL et SUPABASE_KEY manquantes.")
    print("Creez un fichier .env a la racine du projet avec :")
    print("  SUPABASE_URL=https://xxxxx.supabase.co")
    print("  SUPABASE_KEY=eyJhbGciOi...")
    sys.exit(1)

sb = create_client(SUPABASE_URL, SUPABASE_KEY)

# ══════════════════════════════════════════════════════════════════════
# UTILITAIRES
# ══════════════════════════════════════════════════════════════════════

def clean_str(val):
    """Nettoie une valeur texte."""
    if val is None or pd.isna(val):
        return None
    s = str(val).strip()
    return s if s and s.lower() not in ('nan', 'none', 'nat') else None


def clean_num(val):
    """Nettoie une valeur numerique."""
    if val is None or pd.isna(val):
        return None
    try:
        s = str(val).replace(' ', '').replace(',', '.').strip()
        if not s or s.lower() in ('nan', 'none', ''):
            return None
        return float(s)
    except (ValueError, TypeError):
        return None


def clean_int(val):
    """Nettoie un entier."""
    n = clean_num(val)
    return int(n) if n is not None else None


def clean_date(val):
    """Nettoie une date et retourne au format ISO (YYYY-MM-DD)."""
    if val is None or pd.isna(val):
        return None
    try:
        if isinstance(val, datetime):
            return val.strftime('%Y-%m-%d')
        s = str(val).strip()
        if not s or s.lower() in ('nan', 'none', 'nat', ''):
            return None
        dt = pd.to_datetime(s, dayfirst=True)
        return dt.strftime('%Y-%m-%d')
    except Exception:
        return None


def clean_village(val):
    """Supprime le prefixe numerique des villages (ex: '1. Akoetchaou' -> 'Akoetchaou')."""
    s = clean_str(val)
    if s:
        return re.sub(r'^\d+\.\s*', '', s).strip()
    return None


def batch_insert(table_name, records, batch_size=50):
    """Insere par lots pour eviter les erreurs de taille."""
    total = len(records)
    inserted = 0
    for i in range(0, total, batch_size):
        batch = records[i:i + batch_size]
        try:
            sb.table(table_name).insert(batch).execute()
            inserted += len(batch)
            pct = min(100, int(inserted / total * 100))
            print(f"  {table_name}: {inserted}/{total} ({pct}%)")
        except Exception as e:
            print(f"  ERREUR lot {i}-{i+len(batch)}: {e}")
            # Essayer ligne par ligne pour ce lot
            for j, rec in enumerate(batch):
                try:
                    sb.table(table_name).insert(rec).execute()
                    inserted += 1
                except Exception as e2:
                    print(f"    Ligne {i+j+1} ignoree: {e2}")
    return inserted


# ══════════════════════════════════════════════════════════════════════
# MIGRATION: ACCORDS CONSOLIDES
# ══════════════════════════════════════════════════════════════════════

# Mapping: nom Excel -> colonne SQL
ACCORDS_COL_MAP = {
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
}

NUMBER_COLS = {
    'montant_pret_fcfa', 'montant_don_fcfa', 'montant_total_fcfa',
    'montant_total_devise',
}
INT_COLS = {'annee_signature', 'annee_cloture'}
DATE_COLS = {'date_signature', 'date_approbation', 'date_cloture'}


def migrate_accords():
    print("\n" + "=" * 60)
    print("MIGRATION: Accords consolides")
    print("=" * 60)

    df = pd.read_excel(EXCEL_FILE, sheet_name='Accords_consolides', header=5, dtype=str)
    df.columns = [str(c).strip() for c in df.columns]
    # Supprimer la premiere colonne si elle est unnamed (index)
    unnamed_cols = [c for c in df.columns if 'unnamed' in c.lower() or 'Unnamed' in c]
    if unnamed_cols:
        df = df.drop(columns=unnamed_cols)

    print(f"  Source: {len(df)} lignes, {len(df.columns)} colonnes")
    print(f"  Colonnes Excel: {list(df.columns)}")

    records = []
    for _, row in df.iterrows():
        rec = {}
        for excel_col, db_col in ACCORDS_COL_MAP.items():
            if excel_col in df.columns:
                val = row.get(excel_col)
                if db_col in NUMBER_COLS:
                    val = clean_num(val)
                elif db_col in INT_COLS:
                    val = clean_int(val)
                elif db_col in DATE_COLS:
                    val = clean_date(val)
                else:
                    val = clean_str(val)
                if val is not None:
                    rec[db_col] = val

        # Ignorer les lignes sans code_projet
        if rec.get('code_projet'):
            records.append(rec)

    print(f"  A inserer: {len(records)} enregistrements valides")

    # Vider la table avant migration
    try:
        sb.table('accords_consolides').delete().neq('id', 0).execute()
        print("  Table vidée.")
    except Exception as e:
        print(f"  Attention (vidage): {e}")

    inserted = batch_insert('accords_consolides', records)
    print(f"  RESULTAT: {inserted} accords migres")
    return inserted


# ══════════════════════════════════════════════════════════════════════
# MIGRATION: LOCALISATION
# ══════════════════════════════════════════════════════════════════════

def migrate_localisation():
    print("\n" + "=" * 60)
    print("MIGRATION: Localisation")
    print("=" * 60)

    df = pd.read_excel(EXCEL_FILE, sheet_name='Localisation', dtype=str)
    df.columns = [str(c).strip() for c in df.columns]
    print(f"  Source: {len(df)} lignes")

    records = []
    for _, row in df.iterrows():
        dep = clean_str(row.get('Département'))
        com = clean_str(row.get('Commune'))
        arr = clean_str(row.get('Arrondissement'))
        vil = clean_village(row.get('Village ou quartier de Ville'))

        if dep and com and arr and vil:
            records.append({
                'departement': dep,
                'commune': com,
                'arrondissement': arr,
                'village': vil,
            })

    print(f"  A inserer: {len(records)} villages valides")

    try:
        sb.table('localisation').delete().neq('id', 0).execute()
        print("  Table vidée.")
    except Exception as e:
        print(f"  Attention (vidage): {e}")

    inserted = batch_insert('localisation', records, batch_size=100)
    print(f"  RESULTAT: {inserted} localisations migrees")
    return inserted


# ══════════════════════════════════════════════════════════════════════
# MIGRATION: PARAMETRES
# ══════════════════════════════════════════════════════════════════════

def migrate_parametres():
    print("\n" + "=" * 60)
    print("MIGRATION: Parametres")
    print("=" * 60)

    df = pd.read_excel(EXCEL_FILE, sheet_name='Paramètres', dtype=str, header=None)
    df.columns = [str(i) for i in range(len(df.columns))]
    print(f"  Source: {len(df)} lignes, {len(df.columns)} categories")

    records = []
    # La premiere ligne contient les noms de categories
    categories = {}
    for col in df.columns:
        cat_name = clean_str(df.iloc[0][col])
        if cat_name:
            categories[col] = cat_name

    # Les lignes suivantes contiennent les valeurs
    for col, cat_name in categories.items():
        for idx in range(1, len(df)):
            val = clean_str(df.iloc[idx][col])
            if val:
                records.append({
                    'categorie': cat_name,
                    'valeur': val,
                    'ordre': idx,
                })

    print(f"  A inserer: {len(records)} parametres")

    try:
        sb.table('parametres').delete().neq('id', 0).execute()
        print("  Table vidée.")
    except Exception as e:
        print(f"  Attention (vidage): {e}")

    inserted = batch_insert('parametres', records)
    print(f"  RESULTAT: {inserted} parametres migres")
    return inserted


# ══════════════════════════════════════════════════════════════════════
# MIGRATION: METADATA COLONNES
# ══════════════════════════════════════════════════════════════════════

def migrate_colonnes_meta():
    print("\n" + "=" * 60)
    print("MIGRATION: Metadata colonnes")
    print("=" * 60)

    NUMBER_FIELDS = {
        'montant_pret_fcfa', 'montant_don_fcfa', 'montant_total_fcfa',
        'montant_total_devise',
    }
    INT_FIELDS = {'annee_signature', 'annee_cloture'}
    DATE_FIELDS = {'date_signature', 'date_approbation', 'date_cloture'}
    READONLY_FIELDS = {'annee_cloture'}
    SELECT_FIELDS = {
        'modalite_intervention', 'secteur_principal', 'nature_pret_don_mixte',
        'devise', 'apd_oui_non', 'type_financement', 'type_contributeur',
        'axe_pag', 'pilier_pag', 'odd', 'pilier', 'statut',
    }

    records = []
    order = 0
    seen = set()

    for display_name, db_col in ACCORDS_COL_MAP.items():
        if db_col in seen or '\n' in display_name:
            continue
        seen.add(db_col)
        order += 1

        if db_col in NUMBER_FIELDS or db_col in INT_FIELDS:
            col_type = 'number'
        elif db_col in DATE_FIELDS:
            col_type = 'date'
        elif db_col in SELECT_FIELDS:
            col_type = 'select'
        else:
            col_type = 'text'

        # Recuperer les options pour les selects
        options = []
        if col_type == 'select':
            try:
                resp = sb.table('accords_consolides').select(db_col).neq(
                    db_col, '').execute()
                opts = set()
                for r in resp.data:
                    v = r.get(db_col)
                    if v and str(v).strip():
                        opts.add(str(v).strip())
                options = sorted(opts)
            except Exception:
                pass

        records.append({
            'table_name': 'accords_consolides',
            'column_key': display_name,
            'db_column': db_col,
            'col_type': col_type,
            'readonly': db_col in READONLY_FIELDS,
            'col_order': order,
            'options': options,
        })

    print(f"  A inserer: {len(records)} definitions de colonnes")

    try:
        sb.table('colonnes_meta').delete().neq('id', 0).execute()
        print("  Table vidée.")
    except Exception as e:
        print(f"  Attention (vidage): {e}")

    inserted = batch_insert('colonnes_meta', records)
    print(f"  RESULTAT: {inserted} colonnes definies")
    return inserted


# ══════════════════════════════════════════════════════════════════════
# MIGRATION: SUIVI TRIMESTRIEL
# ══════════════════════════════════════════════════════════════════════

def migrate_suivi():
    print("\n" + "=" * 60)
    print("MIGRATION: Suivi Trimestriel")
    print("=" * 60)

    df = pd.read_excel(EXCEL_FILE, sheet_name='Suivi_Trimestriel', dtype=str)
    df.columns = [str(c).strip() for c in df.columns]
    print(f"  Source: {len(df)} lignes")

    records = []
    for _, row in df.iterrows():
        code = clean_str(row.get('Code_Projet'))
        if not code:
            continue
        rec = {
            'code_projet': code,
            'annee_suivi': clean_int(row.get('Annee_Suivi')),
            'trimestre': clean_str(row.get('Trimestre')),
            'tef_trim': clean_num(row.get('TEF_Trim')),
            'montant_decaisse_usd': clean_num(row.get('Montant_Decaisse_USD')),
            'montant_decaisse_fcfa': clean_num(row.get('Montant_Decaisse_FCFA')),
            'tep_trim': clean_num(row.get('TEP_Trim')),
            'activites_realisees': clean_str(row.get('Activites_Realisees')),
            'tef_cumule': clean_num(row.get('TEF_Cumule')),
            'tep_cumule': clean_num(row.get('TEP_Cumule')),
            'difficultes_rencontrees': clean_str(row.get('Difficultes_Rencontrees')),
            'approches_solution': clean_str(row.get('Approches_Solution')),
            'recommandations': clean_str(row.get('Recommandations')),
            'date_saisie': clean_date(row.get('Date_Saisie')),
        }
        records.append(rec)

    print(f"  A inserer: {len(records)} suivis")

    try:
        sb.table('suivi_trimestriel').delete().neq('id', 0).execute()
        print("  Table vidée.")
    except Exception as e:
        print(f"  Attention (vidage): {e}")

    inserted = batch_insert('suivi_trimestriel', records)
    print(f"  RESULTAT: {inserted} suivis migres")
    return inserted


# ══════════════════════════════════════════════════════════════════════
# PROGRAMME PRINCIPAL
# ══════════════════════════════════════════════════════════════════════

if __name__ == '__main__':
    print("=" * 60)
    print("  SGIAD - Migration Excel -> Supabase")
    print(f"  Fichier: {EXCEL_FILE}")
    print(f"  Supabase: {SUPABASE_URL}")
    print("=" * 60)

    start = time.time()
    stats = {}

    stats['accords'] = migrate_accords()
    stats['localisation'] = migrate_localisation()
    stats['parametres'] = migrate_parametres()
    stats['colonnes_meta'] = migrate_colonnes_meta()
    stats['suivi'] = migrate_suivi()

    elapsed = time.time() - start
    print("\n" + "=" * 60)
    print("  RESUME DE LA MIGRATION")
    print("=" * 60)
    for table, count in stats.items():
        print(f"  {table:25s} : {count} lignes")
    print(f"  {'Duree':25s} : {elapsed:.1f}s")
    print("=" * 60)
    print("  Migration terminee !")
    print("  Verifiez les donnees dans le dashboard Supabase.")
    print("=" * 60)
