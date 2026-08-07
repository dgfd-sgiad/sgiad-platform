# -*- coding: utf-8 -*-
"""
SGIAD - API Flask (v2 Supabase)
================================
Serveur principal. Les donnees principales (accords, localisation,
parametres, suivi) viennent de Supabase (PostgreSQL cloud).
Les modules secondaires (coop decentralisee, anciens accords) restent
sur Excel jusqu'a leur migration.

Variables d'environnement:
    SUPABASE_URL  = https://xxxxx.supabase.co
    SUPABASE_KEY  = eyJhbGciOi...
"""

import re
import traceback
import unicodedata
import numpy as np
from flask import Flask, request, jsonify, send_from_directory, send_file, make_response
from flask_cors import CORS
from openpyxl import load_workbook
from werkzeug.utils import secure_filename
from io import BytesIO
from datetime import datetime
from urllib.parse import unquote
import pandas as pd
import json
import os
import time

app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": "*"}})

# ── Module Gestion des Accords Financiers (Supabase) ──
from accords_financiers import bp as accords_financiers_bp
app.register_blueprint(accords_financiers_bp)

# ── Module Authentification ──
from auth import bp as auth_bp
app.register_blueprint(auth_bp)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_FOLDER = os.path.join(BASE_DIR, 'uploads')
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

BANQUE_FILE   = os.path.join(BASE_DIR, 'Banque_Projets.xlsx')
ACCORDS_FILE  = os.path.join(BASE_DIR, 'Banque_Accords_V2.xlsx')

# ── Servir les fichiers statiques (HTML, CSS, JS, assets) ──
@app.route('/')
def index():
    return send_file(os.path.join(BASE_DIR, 'index.html'))

@app.route('/<path:filepath>')
def serve_static(filepath):
    """Sert les fichiers HTML, CSS, JS, images depuis le repertoire projet."""
    full_path = os.path.join(BASE_DIR, filepath)
    if os.path.isfile(full_path):
        resp = send_file(full_path)
        if filepath.endswith('.html'):
            resp.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
        return resp
    return jsonify({"error": "Fichier introuvable"}), 404

# ══════════════════════════════════════════════════════════════════════════════
# UTILITAIRES
# ══════════════════════════════════════════════════════════════════════════════

def strip_accents(s):
    if not isinstance(s, str):
        return s
    return ''.join(c for c in unicodedata.normalize('NFD', s) if unicodedata.category(c) != 'Mn')

def clean_date(val):
    if pd.isna(val) or str(val).strip() in ('', 'nan'):
        return None
    try:
        return pd.to_datetime(val, dayfirst=True).strftime('%Y-%m-%d')
    except Exception:
        return None

def load_wb_safe(path, retries=3):
    for attempt in range(retries):
        try:
            return load_workbook(path)
        except PermissionError:
            print(f"⚠️  Fichier verrouillé, tentative {attempt+1}/{retries}…")
            time.sleep(1)
    return None

PLACEHOLDERS = {"-- sélectionner --", "-- selectionner --", "tous", "tout", ""}

def normalize_filter_values(values):
    flat = []
    def _add(v):
        if v is None:
            return
        if isinstance(v, (list, tuple, set)):
            for sub in v: _add(sub)
        elif isinstance(v, dict):
            _add(v.get('value') or v.get('label') or str(v))
        else:
            s = str(v).strip()
            if s and s.lower() not in PLACEHOLDERS:
                flat.append(s)
    _add(values)
    seen, result = set(), []
    for x in flat:
        if x not in seen:
            seen.add(x); result.append(x)
    return result

# ══════════════════════════════════════════════════════════════════════════════
# SESSION / EN-TÊTE ACCUEIL (Supabase)
# ══════════════════════════════════════════════════════════════════════════════

@app.route('/api/session/info', methods=['GET'])
def get_session_info():
    try:
        from db import log_session
        result = log_session(request.remote_addr)
        return jsonify(result)
    except Exception as e:
        # Fallback: repondre avec des valeurs par defaut si Supabase indisponible
        traceback.print_exc()
        return jsonify({
            "ip": request.remote_addr,
            "derniere_connexion": None,
            "total_connexions": 0
        })

# ══════════════════════════════════════════════════════════════════════════════
# LOCALISATION HIÉRARCHIQUE (Supabase)
# ══════════════════════════════════════════════════════════════════════════════

@app.route('/api/localisation/hierarchie', methods=['GET'])
def get_localisation_hierarchie():
    try:
        from db import get_localisation_tree
        return jsonify(get_localisation_tree())
    except Exception as e:
        # Fallback Excel si Supabase indisponible
        try:
            tree = _get_localisation_from_excel()
            return jsonify(tree)
        except Exception as e2:
            traceback.print_exc()
            return jsonify({"error": str(e2)}), 500


@app.route('/api/localisation/reload', methods=['POST'])
def reload_localisation_tree():
    try:
        from db import get_localisation_tree
        get_localisation_tree(force_reload=True)
        return jsonify({"message": "Arbre de localisation rechargé"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


def _get_localisation_from_excel():
    """Fallback: lit la localisation depuis Excel si Supabase echoue."""
    import re as _re
    def _clean_village(v):
        return _re.sub(r'^\d+\.\s*', '', str(v).strip())

    df = pd.read_excel(BANQUE_FILE, sheet_name='Localisation', dtype=str)
    df.columns = [str(c).strip() for c in df.columns]
    tree = {}
    for _, row in df.iterrows():
        dep = str(row['Département']).strip()
        com = str(row['Commune']).strip()
        arr = str(row['Arrondissement']).strip()
        vil = _clean_village(row['Village ou quartier de Ville'])
        tree.setdefault(dep, {}).setdefault(com, {}).setdefault(arr, [])
        tree[dep][com][arr].append(vil)
    return tree


# ══════════════════════════════════════════════════════════════════════════════
# MODULE BANQUE DE PROJETS (Projets - reste sur Excel pour l'instant)
# ══════════════════════════════════════════════════════════════════════════════

def decode_localisation(s):
    def split_top(text, sep):
        parts, depth, cur = [], 0, ""
        for ch in text:
            if ch == '(':
                depth += 1; cur += ch
            elif ch == ')':
                depth -= 1; cur += ch
            elif ch == sep and depth == 0:
                parts.append(cur.strip()); cur = ""
            else:
                cur += ch
        if cur.strip():
            parts.append(cur.strip())
        return parts

    def parse_node(item):
        item = item.strip()
        if item.endswith(')') and '(' in item:
            idx = item.index('(')
            name = item[:idx].strip()
            inner = item[idx + 1:-1]
            children = {}
            for child_item in split_top(inner, ','):
                cname, cval = parse_node(child_item)
                children[cname] = cval
            return name, children
        return item, {}

    if not s or not str(s).strip():
        return {}
    s = str(s).strip().rstrip('.').strip()
    result = {}
    for dep_item in split_top(s, ';'):
        name, val = parse_node(dep_item)
        result[name] = val
    return result

def flatten_localisation_names(tree):
    names = set()
    def walk(node):
        for name, children in node.items():
            names.add(name)
            if children:
                walk(children)
    walk(tree)
    return names

def zone_intervention_matches(zone_str, filter_set_upper):
    if not zone_str or str(zone_str).strip() == '':
        return False
    names = flatten_localisation_names(decode_localisation(zone_str))
    names_upper = {n.strip().upper() for n in names}
    return bool(names_upper & filter_set_upper)

def derive_localisation_columns(zone_str):
    tree = decode_localisation(zone_str)
    deps, coms, arrs, vils = [], [], [], []
    for dep, dep_children in tree.items():
        if dep and dep not in deps:
            deps.append(dep)
        for com, com_children in (dep_children or {}).items():
            if com and com not in coms:
                coms.append(com)
            for arr, arr_children in (com_children or {}).items():
                if arr and arr not in arrs:
                    arrs.append(arr)
                for vil in (arr_children or {}).keys():
                    if vil and vil not in vils:
                        vils.append(vil)
    return {
        'Departement': ', '.join(deps),
        'Commune': ', '.join(coms),
        'Arrondissement': ', '.join(arrs),
        'Village_Quartier': ', '.join(vils),
    }


@app.route('/api/banque/projets/list', methods=['GET'])
def get_projets_banque():
    try:
        if not os.path.exists(BANQUE_FILE):
            return jsonify({"error": "Fichier Banque_Projets.xlsx introuvable"}), 404
        df = pd.read_excel(BANQUE_FILE, sheet_name='Projets', dtype=str, header=1)
        df = df.dropna(subset=['Code_Projet'])
        df = df[df['Code_Projet'].astype(str).str.strip() != '']

        zone_params = request.args.getlist('zone')
        if zone_params and 'Zone_intervention' in df.columns:
            filter_set_upper = {z.strip().upper() for z in zone_params if z.strip()}
            if filter_set_upper:
                mask = df['Zone_intervention'].apply(
                    lambda s: zone_intervention_matches(s, filter_set_upper))
                df = df.loc[mask].copy()

        date_cols = ['Date_Approbation','Date_Signature','Date_Vigueur','Date_Demarrage',
                     'Date_Cloture','Date_Prorogation','Nouvelle_Date_Cloture',
                     'Date_Soumission','Date_Validation']
        for col in date_cols:
            if col in df.columns:
                df[col] = df[col].apply(clean_date)
        data = json.loads(df.to_json(orient='records', force_ascii=False))
        cleaned = [{k: v for k, v in r.items() if v is not None and str(v).strip() != ''} for r in data]

        for r in cleaned:
            zone_str = r.get('Zone_intervention')
            if zone_str and str(zone_str).strip() and not r.get('Departement'):
                for field, value in derive_localisation_columns(zone_str).items():
                    if value:
                        r[field] = value

        return jsonify(cleaned)
    except Exception as e:
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500


@app.route('/api/banque/projets/add', methods=['POST'])
def add_projet_banque():
    try:
        data = request.get_json(force=True) or {}
        zone_str = data.get('Zone_intervention') or data.get('Zone', '')
        if zone_str and str(zone_str).strip():
            for field, value in derive_localisation_columns(zone_str).items():
                if not data.get(field) and value:
                    data[field] = value
        wb = load_wb_safe(BANQUE_FILE)
        if wb is None:
            return jsonify({"error": "Fichier verrouillé. Fermez-le et réessayez."}), 503
        ws = wb['Projets']
        row_data = [
            data.get('Code_Projet'), data.get('Intitule_Projet'), data.get('Annee_Collecte'),
            data.get('Categorie'), data.get('Envergure'), data.get('Secteur_Activite_1'),
            data.get('Secteur_Activite_2'), data.get('Secteur_Activite_3'), data.get('Sous_Secteur'),
            data.get('Tutelle'), data.get('Agence_Exécution'), data.get('Contexte_Justification'),
            data.get('Problematique'), data.get('Objectif_Global'), data.get('Objectifs_Specifiques'),
            data.get('Principaux_Resultats'), data.get('Composantes_Projet'), data.get('Activites_Principales'),
            data.get('Beneficiaires_Directs'), data.get('Beneficiaires_Indirects'), data.get('Departement'),
            data.get('Commune'), data.get('Arrondissement'), data.get('Village_Quartier'),
            data.get('Coordonnees_GPS'), data.get('Date_Approbation'), data.get('Date_Signature'),
            data.get('Date_Vigueur'), data.get('Date_Demarrage'), data.get('Date_Cloture'),
            data.get('Duree_Initiale_Mois'), data.get('Est_Proroge'), data.get('Date_Prorogation'),
            data.get('Motif_Prorogation'), data.get('Nouvelle_Date_Cloture'), data.get('Nb_Prorogations'),
            data.get('Cout_Total_USD'), data.get('Devise'), data.get('Taux_Change'),
            data.get('Cout_Total_FCFA'), data.get('Milliards_FCFA'),
            data.get('Contrepartie_BN_USD'), data.get('Contrepartie_BN_FCFA'),
            data.get('Don_Attendu_FCFA'), data.get('Pret_Attendu_FCFA'), data.get('PPP_Attendu_FCFA'),
            data.get('Contribution_Benef_FCFA'), data.get('Gap_Financement'), data.get('Pourcentage_Acquis'),
            data.get('Source_Financement'), data.get('APD_Oui_Non'), data.get('Type_Financement'),
            data.get('Contributeur'), data.get('Sigle_Partenaire'), data.get('Type_Contributeur'),
            data.get('Co_Partenaire_1'), data.get('Co_Partenaire_2'), data.get('Co_Partenaire_3'),
            data.get('Co_Partenaire_4'), data.get('Co_Partenaire_5'), data.get('Co_Partenaire_6'),
            data.get('Co_Partenaire_7'), data.get('Statut_Projet'), data.get('Secteur_PAG'),
            data.get('Pilier_PAG'), data.get('Axe_PAG'), data.get('ODD'), data.get('Cible_ODD'),
            data.get('Pilier_National'), data.get('Resp_Banque_Nom'), data.get('Resp_Banque_Tel1'),
            data.get('Resp_Banque_Tel2'), data.get('Resp_Banque_Email'), data.get('Coord_Projet_Nom'),
            data.get('Coord_Projet_Tel1'), data.get('Coord_Projet_Tel2'), data.get('Coord_Projet_Email'),
            data.get('RAF_Nom'), data.get('RAF_Tel1'), data.get('RAF_Tel2'), data.get('RAF_Email'),
            data.get('Resp_SE_Nom'), data.get('Resp_SE_Tel1'), data.get('Resp_SE_Tel2'), data.get('Resp_SE_Email'),
            data.get('Niveau_Maturite'), data.get('Etude_Faisabilite'), data.get('Etude_Environnementale'),
            data.get('Plan_Affaires'), data.get('Dossier_Technique'), data.get('Categorie_Env'),
            data.get('Theme_Genre'), data.get('Theme_Inclusion'), data.get('Theme_Climat'),
            data.get('Theme_Emploi_Jeunes'), data.get('Risques_Identifies'), data.get('Mesures_Attenuation'),
            data.get('Niveau_Risque'), data.get('Date_Soumission'), data.get('Avis_Technique'),
            data.get('Avis_DGFD'), data.get('Avis_Ministere'), data.get('Decision_Comite'),
            data.get('Date_Validation'), data.get('Note_Conceptuelle'), data.get('Cadre_Logique'),
            data.get('Budget_Detaille'), data.get('Cartographie'), data.get('Lettre_Demande'),
            data.get('Zone_intervention'),
            data.get('Modalite_Intervention'), data.get('Nature_Financement'),
            data.get('Instrument_Financement'), data.get('Source_Verifiable'),
            data.get('Montant_Devise_Origine'),
        ]
        ws.append(row_data)
        wb.save(BANQUE_FILE); wb.close()
        return jsonify({"message": "Projet ajouté avec succès", "code": data.get('Code_Projet')}), 201
    except Exception as e:
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500


@app.route('/api/banque/projets/update/<code>', methods=['PUT'])
def update_projet_banque(code):
    try:
        code = unquote(code).strip()
        updated_data = request.get_json(force=True) or {}
        zone_str = updated_data.get('Zone_intervention') or updated_data.get('Zone', '')
        if zone_str and str(zone_str).strip():
            for field, value in derive_localisation_columns(zone_str).items():
                if not updated_data.get(field) and value:
                    updated_data[field] = value
        wb = load_wb_safe(BANQUE_FILE)
        if wb is None:
            return jsonify({"error": "Fichier verrouillé. Fermez-le et réessayez."}), 503
        ws = wb['Projets']
        row_idx = None
        for i, row in enumerate(ws.iter_rows(min_row=2, max_col=1, values_only=True), start=2):
            if str(row[0]).strip() == code:
                row_idx = i; break
        if not row_idx:
            return jsonify({"error": f"Projet {code} non trouvé"}), 404
        col_mapping = {
            'Code_Projet':1,'Intitule_Projet':2,'Annee_Collecte':3,'Categorie':4,'Envergure':5,
            'Secteur_Activite_1':6,'Secteur_Activite_2':7,'Secteur_Activite_3':8,'Sous_Secteur':9,
            'Tutelle':10,'Agence_Exécution':11,'Contexte_Justification':12,'Problematique':13,
            'Objectif_Global':14,'Objectifs_Specifiques':15,'Principaux_Resultats':16,
            'Composantes_Projet':17,'Activites_Principales':18,'Beneficiaires_Directs':19,
            'Beneficiaires_Indirects':20,'Departement':21,'Commune':22,'Arrondissement':23,
            'Village_Quartier':24,'Coordonnees_GPS':25,'Date_Approbation':26,'Date_Signature':27,
            'Date_Vigueur':28,'Date_Demarrage':29,'Date_Cloture':30,'Duree_Initiale_Mois':31,
            'Est_Proroge':32,'Date_Prorogation':33,'Motif_Prorogation':34,'Nouvelle_Date_Cloture':35,
            'Nb_Prorogations':36,'Cout_Total_USD':37,'Devise':38,'Taux_Change':39,
            'Cout_Total_FCFA':40,'Milliards_FCFA':41,
            'Contrepartie_BN_USD':42,'Contrepartie_BN_FCFA':43,'Don_Attendu_FCFA':44,'Pret_Attendu_FCFA':45,
            'PPP_Attendu_FCFA':46,'Contribution_Benef_FCFA':47,'Gap_Financement':48,'Pourcentage_Acquis':49,
            'Source_Financement':50,
            'APD_Oui_Non':51,'Type_Financement':52,'Contributeur':53,'Sigle_Partenaire':54,
            'Type_Contributeur':55,'Co_Partenaire_1':56,'Co_Partenaire_2':57,'Co_Partenaire_3':58,
            'Co_Partenaire_4':59,'Co_Partenaire_5':60,'Co_Partenaire_6':61,'Co_Partenaire_7':62,
            'Statut_Projet':63,'Secteur_PAG':64,'Pilier_PAG':65,'Axe_PAG':66,'ODD':67,
            'Cible_ODD':68,'Pilier_National':69,'Resp_Banque_Nom':70,'Resp_Banque_Tel1':71,
            'Resp_Banque_Tel2':72,'Resp_Banque_Email':73,'Coord_Projet_Nom':74,'Coord_Projet_Tel1':75,
            'Coord_Projet_Tel2':76,'Coord_Projet_Email':77,'RAF_Nom':78,'RAF_Tel1':79,
            'RAF_Tel2':80,'RAF_Email':81,'Resp_SE_Nom':82,'Resp_SE_Tel1':83,'Resp_SE_Tel2':84,
            'Resp_SE_Email':85,'Niveau_Maturite':86,'Etude_Faisabilite':87,
            'Etude_Environnementale':88,'Plan_Affaires':89,'Dossier_Technique':90,
            'Categorie_Env':91,'Theme_Genre':92,'Theme_Inclusion':93,'Theme_Climat':94,
            'Theme_Emploi_Jeunes':95,'Risques_Identifies':96,'Mesures_Attenuation':97,
            'Niveau_Risque':98,'Date_Soumission':99,'Avis_Technique':100,'Avis_DGFD':101,
            'Avis_Ministere':102,'Decision_Comite':103,'Date_Validation':104,
            'Note_Conceptuelle':105,'Cadre_Logique':106,'Budget_Detaille':107,
            'Cartographie':108,'Lettre_Demande':109,
            'Zone_intervention':110,
            'Modalite_Intervention':111,'Nature_Financement':112,'Instrument_Financement':113,
            'Source_Verifiable':114,'Montant_Devise_Origine':115,
        }
        numeric_fields = {'Cout_Total_USD','Taux_Change','Contrepartie_BN_USD','Don_Attendu_FCFA',
                          'Pret_Attendu_FCFA','PPP_Attendu_FCFA','Contribution_Benef_FCFA',
                          'Niveau_Maturite','Nb_Prorogations','Montant_Devise_Origine',
                          'Cout_Total_FCFA','Milliards_FCFA','Contrepartie_BN_FCFA','Gap_Financement'}
        for field, col_idx in col_mapping.items():
            if field in updated_data and updated_data[field] is not None:
                val = updated_data[field]
                if field in numeric_fields:
                    try:
                        val = float(val) if val else None
                    except (ValueError, TypeError):
                        pass
                ws.cell(row=row_idx, column=col_idx, value=val)
        wb.save(BANQUE_FILE); wb.close()
        return jsonify({"message": "Projet mis à jour"}), 200
    except Exception as e:
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500


@app.route('/api/banque/projets/delete/<code>', methods=['DELETE'])
def delete_projet_banque(code):
    try:
        code = unquote(code).strip()
        wb = load_wb_safe(BANQUE_FILE)
        if wb is None:
            return jsonify({"error": "Fichier verrouillé."}), 503
        ws = wb['Projets']
        for i, row in enumerate(ws.iter_rows(min_row=2, max_col=1, values_only=True), start=2):
            if str(row[0]).strip() == code:
                ws.delete_rows(i, 1); wb.save(BANQUE_FILE); wb.close()
                return jsonify({"message": "Projet supprimé"}), 200
        wb.close()
        return jsonify({"error": "Projet non trouvé"}), 404
    except Exception as e:
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500


@app.route('/api/banque/parametres', methods=['GET'])
def get_parametres_banque():
    """Retourne les parametres (Supabase avec fallback Excel).
    Supporte ?categorie=XXX pour filtrer par categorie."""
    categorie = request.args.get('categorie', '').strip() or None
    try:
        from db import get_parametres
        params = get_parametres(categorie=categorie)
        return jsonify(params)
    except Exception:
        # Fallback Excel
        try:
            df = pd.read_excel(BANQUE_FILE, sheet_name='Paramètres', dtype=str)
            params = {}
            for col in df.columns:
                params[col] = [x for x in df[col].dropna().unique().tolist() if str(x).strip() != '']
            if categorie and categorie in params:
                return jsonify(params[categorie])
            return jsonify(params)
        except Exception as e2:
            return jsonify({"error": str(e2)}), 500


@app.route('/api/banque/parametres/add', methods=['POST'])
def add_parametre_banque():
    try:
        data = request.json
        colonne = str(data.get('colonne', '')).strip()
        nouvelle_valeur = str(data.get('valeur', '')).strip()
        if not colonne or not nouvelle_valeur:
            return jsonify({"error": "Colonne et valeur requises"}), 400

        # Supabase
        try:
            from db import get_supabase
            sb = get_supabase()
            # Verifier doublon (case-insensitive)
            existing = sb.table('parametres').select('id', 'valeur').eq(
                'categorie', colonne).execute()
            for row in (existing.data or []):
                if str(row.get('valeur', '')).strip().lower() == nouvelle_valeur.lower():
                    return jsonify({"message": f"Cette valeur existe déjà : '{nouvelle_valeur}'", "doublon": True}), 409
            # Inserer
            sb.table('parametres').insert({
                'categorie': colonne,
                'valeur': nouvelle_valeur,
                'ordre': 999,
            }).execute()
            return jsonify({"message": "Valeur ajoutée", "colonne": colonne, "valeur": nouvelle_valeur}), 201
        except Exception as sb_err:
            traceback.print_exc()
            return jsonify({"error": f"Supabase: {str(sb_err)}"}), 500

        # Fallback Excel
        wb = load_wb_safe(BANQUE_FILE)
        if wb is None:
            return jsonify({"error": "Fichier verrouillé."}), 503
        ws = wb['Paramètres']
        col_idx = next((i for i, c in enumerate(ws[1], 1) if c.value and str(c.value).strip().upper() == colonne.upper()), None)
        if not col_idx:
            wb.close(); return jsonify({"error": f"Colonne '{colonne}' introuvable"}), 404
        existing = {str(r[0]).strip().upper() for r in ws.iter_rows(min_row=2, min_col=col_idx, max_col=col_idx, values_only=True) if r[0]}
        if nouvelle_valeur.upper() in existing:
            wb.close(); return jsonify({"message": "Doublon", "doublon": True}), 409
        next_row = 2
        while ws.cell(row=next_row, column=col_idx).value not in (None, ''):
            next_row += 1
        ws.cell(row=next_row, column=col_idx, value=nouvelle_valeur)
        wb.save(BANQUE_FILE); wb.close()
        return jsonify({"message": "Valeur ajoutée", "colonne": colonne, "valeur": nouvelle_valeur}), 201
    except Exception as e:
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500


@app.route('/api/banque/parametres/delete', methods=['POST'])
def delete_parametre_banque():
    try:
        data = request.json
        colonne = str(data.get('colonne', '')).strip()
        valeur  = str(data.get('valeur', '')).strip()
        if not colonne or not valeur:
            return jsonify({"error": "Colonne et valeur requises"}), 400

        # Supabase
        try:
            from db import get_supabase
            sb = get_supabase()
            sb.table('parametres').delete().eq(
                'categorie', colonne).eq('valeur', valeur).execute()
            return jsonify({"message": "Valeur supprimée"}), 200
        except Exception as sb_err:
            traceback.print_exc()
            return jsonify({"error": f"Supabase: {str(sb_err)}"}), 500

        # Fallback Excel
        wb = load_wb_safe(BANQUE_FILE)
        if wb is None:
            return jsonify({"error": "Fichier verrouillé."}), 503
        ws = wb['Paramètres']
        col_idx = next((i for i, c in enumerate(ws[1], 1) if c.value and str(c.value).strip().upper() == colonne.upper()), None)
        if not col_idx:
            wb.close(); return jsonify({"error": f"Colonne '{colonne}' introuvable"}), 404
        row_to_delete = next(
            (i for i, r in enumerate(ws.iter_rows(min_row=2, min_col=col_idx, max_col=col_idx, values_only=True), 2)
             if r[0] and str(r[0]).strip().upper() == valeur.upper()), None)
        if not row_to_delete:
            wb.close(); return jsonify({"message": "Valeur non trouvée"}), 404
        ws.delete_rows(row_to_delete, 1)
        wb.save(BANQUE_FILE); wb.close()
        return jsonify({"message": "Valeur supprimée"}), 200
    except Exception as e:
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500


@app.route('/api/banque/parametres/update', methods=['POST'])
def update_parametre_banque():
    try:
        data = request.json
        colonne = str(data.get('colonne', '')).strip()
        ancienne_valeur = str(data.get('ancienne_valeur', '')).strip()
        nouvelle_valeur = str(data.get('nouvelle_valeur', '')).strip()
        if not colonne or not ancienne_valeur or not nouvelle_valeur:
            return jsonify({"error": "Colonne, ancienne et nouvelle valeurs requises"}), 400

        # Supabase
        try:
            from db import get_supabase
            sb = get_supabase()
            # Verifier doublon
            existing = sb.table('parametres').select('id').eq(
                'categorie', colonne).eq('valeur', nouvelle_valeur).execute()
            if existing.data:
                return jsonify({"message": "Doublon", "doublon": True}), 409
            # Update
            sb.table('parametres').update({
                'valeur': nouvelle_valeur,
            }).eq('categorie', colonne).eq('valeur', ancienne_valeur).execute()
            return jsonify({"message": "Valeur modifiée", "colonne": colonne}), 200
        except Exception as sb_err:
            traceback.print_exc()
            return jsonify({"error": f"Supabase: {str(sb_err)}"}), 500

        # Fallback Excel
        wb = load_wb_safe(BANQUE_FILE)
        if wb is None:
            return jsonify({"error": "Fichier verrouillé."}), 503
        ws = wb['Paramètres']
        col_idx = next((i for i, c in enumerate(ws[1], 1) if c.value and str(c.value).strip().upper() == colonne.upper()), None)
        if not col_idx:
            wb.close(); return jsonify({"error": f"Colonne '{colonne}' introuvable"}), 404
        cell_to_update = next(
            (ws.cell(row=i, column=col_idx) for i in range(2, ws.max_row + 1)
             if ws.cell(row=i, column=col_idx).value and str(ws.cell(row=i, column=col_idx).value).strip().upper() == ancienne_valeur.upper()), None)
        if not cell_to_update:
            wb.close(); return jsonify({"message": "Valeur non trouvée"}), 404
        cell_to_update.value = nouvelle_valeur
        wb.save(BANQUE_FILE); wb.close()
        return jsonify({"message": "Valeur modifiée", "colonne": colonne}), 200
    except Exception as e:
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500


@app.route('/api/banque/projets/export', methods=['POST'])
def export_projets():
    try:
        req_data = request.get_json(force=True) or {}
        raw_filters = req_data.get('filters', {})
        selected_columns = req_data.get('selected_columns', [])
        if not os.path.exists(BANQUE_FILE):
            return jsonify({"error": "Fichier introuvable"}), 404
        df = pd.read_excel(BANQUE_FILE, sheet_name='Projets', dtype=str, header=1).reset_index(drop=True)
        if df.columns.duplicated().any():
            df = df.loc[:, ~df.columns.duplicated()].copy()
        df.columns = [str(c).strip() for c in df.columns]
        for col_name, raw_values in raw_filters.items():
            col_name = str(col_name).strip()
            if col_name not in df.columns: continue
            filter_list = normalize_filter_values(raw_values)
            if not filter_list: continue

            if col_name == 'Zone_intervention':
                filter_set_upper = {f.strip().upper() for f in filter_list}
                mask = df[col_name].apply(lambda s: zone_intervention_matches(s, filter_set_upper))
                df = df.loc[mask].copy()
                continue

            serie = df[col_name]
            if isinstance(serie, pd.DataFrame): serie = serie.iloc[:, 0]
            df = df.loc[serie.astype(str).str.strip().isin(filter_list)].copy()
        if len(df) == 0:
            return jsonify({"error": "Aucun résultat"}), 404

        if selected_columns:
            valid_cols = []
            for c in selected_columns:
                name = str(c.get('value') if isinstance(c, dict) else c).strip()
                if name in df.columns and name not in valid_cols:
                    valid_cols.append(name)
            if valid_cols: df = df[valid_cols].copy()
        output = BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name='Export')
        output.seek(0)
        return send_file(output, mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                         as_attachment=True, download_name=f'Rapport_Projets_{datetime.now().strftime("%Y%m%d_%H%M")}.xlsx')
    except Exception as e:
        traceback.print_exc()
        return jsonify({"error": f"{type(e).__name__}: {str(e)}"}), 500


# ══════════════════════════════════════════════════════════════════════════════
# SUIVI TRIMESTRIEL (Supabase avec fallback Excel)
# ══════════════════════════════════════════════════════════════════════════════

@app.route('/api/banque/suivi/list', methods=['GET'])
def get_suivi_trimestriel():
    try:
        from db import get_supabase
        sb = get_supabase()
        resp = sb.table('suivi_trimestriel').select('*').order('code_projet').execute()
        return jsonify(resp.data)
    except Exception:
        # Fallback Excel
        try:
            df = pd.read_excel(BANQUE_FILE, sheet_name='Suivi_Trimestriel', dtype=str)
            df = df.dropna(how='all')
            return jsonify(json.loads(df.to_json(orient='records', force_ascii=False)))
        except Exception as e2:
            traceback.print_exc()
            return jsonify({"error": str(e2)}), 500


# ══════════════════════════════════════════════════════════════════════════════
# SECTEURS <-> SOUS-SECTEURS
# ══════════════════════════════════════════════════════════════════════════════

_secteurs_tree_cache = None

def _norm_secteur(s):
    s = str(s or '').strip().upper().replace('&', 'ET')
    s = unicodedata.normalize('NFD', s)
    s = ''.join(c for c in s if unicodedata.category(c) != 'Mn')
    return re.sub(r'\s+', ' ', s).strip()

def get_secteurs_sous_secteurs(force_reload=False):
    global _secteurs_tree_cache
    if _secteurs_tree_cache is not None and not force_reload:
        return _secteurs_tree_cache

    display, tree, sub_display = {}, {}, {}

    # Essayer Supabase d'abord
    try:
        from db import get_supabase
        sb = get_supabase()
        resp = sb.table('accords_consolides').select('secteur_principal, sous_secteur').execute()
        for row in resp.data:
            sec = str(row.get('secteur_principal') or '').strip()
            if not sec or sec.lower() == 'nan':
                continue
            ksec = _norm_secteur(sec)
            display.setdefault(ksec, sec)
            tree.setdefault(ksec, set())
            sous = str(row.get('sous_secteur') or '').strip()
            if sous and sous.lower() != 'nan':
                for part in re.split(r'\s*/\s*', sous):
                    part = part.strip()
                    if part:
                        ksub = _norm_secteur(part)
                        sub_display.setdefault(ksub, part)
                        tree[ksec].add(ksub)
    except Exception:
        # Fallback Excel
        try:
            df = pd.read_excel(BANQUE_FILE, sheet_name='Projets', dtype=str, header=1)
            for _, row in df.iterrows():
                sec = str(row.get('Secteur_Activite_1') or '').strip()
                if not sec or sec.lower() == 'nan':
                    continue
                ksec = _norm_secteur(sec)
                display.setdefault(ksec, sec)
                tree.setdefault(ksec, set())
                sous = str(row.get('Sous_Secteur') or '').strip()
                if sous and sous.lower() != 'nan':
                    for part in re.split(r'\s*/\s*', sous):
                        part = part.strip()
                        if part:
                            ksub = _norm_secteur(part)
                            sub_display.setdefault(ksub, part)
                            tree[ksec].add(ksub)
        except Exception:
            traceback.print_exc()

    result = {}
    for ksec in sorted(display.keys()):
        result[display[ksec]] = sorted(
            (sub_display[k] for k in tree.get(ksec, set())),
            key=lambda x: str(x).upper()
        )
    _secteurs_tree_cache = result
    return result


@app.route('/api/banque/secteurs_sous_secteurs', methods=['GET'])
def get_secteurs_sous_secteurs_route():
    try:
        return jsonify(get_secteurs_sous_secteurs())
    except Exception as e:
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500


@app.route('/api/banque/secteurs_sous_secteurs/reload', methods=['POST'])
def reload_secteurs_sous_secteurs():
    try:
        get_secteurs_sous_secteurs(force_reload=True)
        return jsonify({"message": "Mapping secteurs/sous-secteurs rechargé"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ── CRUD: secteur_sous_secteur (table de relation explicite) ──

@app.route('/api/banque/secteur_sous_secteur/list', methods=['GET'])
def list_secteur_sous_secteur():
    """Retourne toutes les relations secteur -> sous-secteur."""
    try:
        from db import get_supabase
        sb = get_supabase()
        resp = sb.table('secteur_sous_secteur').select('*').order('secteur').order('sous_secteur').execute()
        return jsonify(resp.data or [])
    except Exception as e:
        # Table may not exist yet - return empty
        if 'relation' in str(e) and 'does not exist' in str(e):
            return jsonify([])
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500


@app.route('/api/banque/secteur_sous_secteur/by_secteur', methods=['GET'])
def get_sous_secteurs_by_secteur():
    """Retourne les sous-secteurs liés à un secteur donné."""
    secteur = request.args.get('secteur', '').strip()
    if not secteur:
        return jsonify({"error": "Parametre 'secteur' requis"}), 400
    try:
        from db import get_supabase
        sb = get_supabase()
        resp = sb.table('secteur_sous_secteur').select('sous_secteur').eq('secteur', secteur).order('sous_secteur').execute()
        sous_secteurs = [r['sous_secteur'] for r in (resp.data or [])]
        return jsonify(sous_secteurs)
    except Exception as e:
        if 'relation' in str(e) and 'does not exist' in str(e):
            return jsonify([])
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500


@app.route('/api/banque/secteur_sous_secteur/add', methods=['POST'])
def add_secteur_sous_secteur():
    """Ajoute une relation secteur -> sous-secteur."""
    try:
        data = request.json
        secteur = str(data.get('secteur', '')).strip()
        sous_secteur = str(data.get('sous_secteur', '')).strip()
        if not secteur or not sous_secteur:
            return jsonify({"error": "Secteur et sous-secteur requis"}), 400

        from db import get_supabase
        sb = get_supabase()
        # Verifier doublon
        existing = sb.table('secteur_sous_secteur').select('id').eq(
            'secteur', secteur).eq('sous_secteur', sous_secteur).execute()
        if existing.data:
            return jsonify({"message": f"Ce sous-secteur est déjà lié à '{secteur}'", "doublon": True}), 409
        # Inserer
        sb.table('secteur_sous_secteur').insert({
            'secteur': secteur,
            'sous_secteur': sous_secteur,
        }).execute()
        # Recharger le cache
        get_secteurs_sous_secteurs(force_reload=True)
        return jsonify({"message": "Sous-secteur lié", "secteur": secteur, "sous_secteur": sous_secteur}), 201
    except Exception as e:
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500


@app.route('/api/banque/secteur_sous_secteur/delete', methods=['POST'])
def delete_secteur_sous_secteur():
    """Supprime une relation secteur -> sous-secteur."""
    try:
        data = request.json
        secteur = str(data.get('secteur', '')).strip()
        sous_secteur = str(data.get('sous_secteur', '')).strip()
        if not secteur or not sous_secteur:
            return jsonify({"error": "Secteur et sous-secteur requis"}), 400

        from db import get_supabase
        sb = get_supabase()
        sb.table('secteur_sous_secteur').delete().eq(
            'secteur', secteur).eq('sous_secteur', sous_secteur).execute()
        # Recharger le cache
        get_secteurs_sous_secteurs(force_reload=True)
        return jsonify({"message": "Liaison supprimée"}), 200
    except Exception as e:
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500


# ══════════════════════════════════════════════════════════════════════════════
# MODULE ACCORDS (Banque_Accords_V2.xlsx) - NON MIGRE
# ══════════════════════════════════════════════════════════════════════════════

ACCORDS_HEADERS = {
    'ACCORDS': 2, 'PARAMETRES': 0, 'PARTENAIRES': 0,
    'SUIVI_ACCORDS': 2, 'DECAISSEMENTS': 2, 'AVENANTS': 1, 'COMMISSIONS_MIXTES': 1,
}

def read_accords_sheet(sheet_name):
    if not os.path.exists(ACCORDS_FILE):
        return None
    hdr = ACCORDS_HEADERS.get(sheet_name, 0)
    return pd.read_excel(ACCORDS_FILE, sheet_name=sheet_name, dtype=str, header=hdr)

@app.route('/api/partenaires/list', methods=['GET'])
def get_partenaires():
    try:
        df = read_accords_sheet('PARTENAIRES')
        if df is None: return jsonify([])
        df.columns = [str(c).strip() for c in df.columns]
        df = df.replace({np.nan: None})
        return jsonify(json.loads(df.to_json(orient='records', force_ascii=False)))
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ══════════════════════════════════════════════════════════════════════════════
# MODULE COOPÉRATION DÉCENTRALISÉE - NON MIGRE
# ══════════════════════════════════════════════════════════════════════════════

COOP_DEC_FILE = os.path.join(BASE_DIR, 'Cooperation_Decentralisee.xlsx')

def init_coop_dec_excel():
    if not os.path.exists(COOP_DEC_FILE):
        with pd.ExcelWriter(COOP_DEC_FILE, engine='openpyxl') as writer:
            headers_accords = ['Ref_Accord', 'Commune_Benin', 'Departement_Benin',
                'Collectivite_Partenaire', 'Pays_Partenaire', 'Type_Cooperation',
                'Date_Signature', 'Date_Debut', 'Date_Fin', 'Duree_Annees',
                'Secteurs_Intervention', 'Objectifs', 'Montant_Total', 'Devise',
                'Contributions_Benin', 'Contributions_Partenaire', 'Statut',
                'Point_Focal_Benin', 'Contact_Partenaire', 'Frequence_Reunions',
                'Derniere_Reunion', 'Prochaine_Reunion', 'Actions_Realisees',
                'Echanges_Effectues', 'Resultats_Obtenus', 'Difficultes',
                'Recommandations', 'Fichier_Convention', 'Observations']
            pd.DataFrame(columns=headers_accords).to_excel(writer, sheet_name='ACCORDS', index=False)
            headers_actions = ['Ref_Action', 'Ref_Accord', 'Commune_Benin', 'Titre_Action',
                'Secteur', 'Date_Debut', 'Date_Fin', 'Budget', 'Financeur_Principal',
                'Beneficiaires', 'Resultats', 'Statut']
            pd.DataFrame(columns=headers_actions).to_excel(writer, sheet_name='ACTIONS_PROJETS', index=False)
            headers_echanges = ['Ref_Echange', 'Ref_Accord', 'Type_Echange', 'Date',
                'Lieu', 'Participants_Benin', 'Participants_Partenaires', 'Objectifs', 'Resultats', 'Rapport']
            pd.DataFrame(columns=headers_echanges).to_excel(writer, sheet_name='ECHANGES_VISITES', index=False)
            params_data = {
                'TYPE_COOPERATION': ['Jumelage', 'Partenariat', "Accord d'amitié", 'Coopération triangulaire'],
                'STATUT_COOP': ['Actif', 'Expiré', 'Suspendu', 'En négociation'],
                'SECTEURS': ['Eau & Assainissement', 'Éducation', 'Santé', 'Agriculture', 'Gouvernance', 'Culture', 'Environnement'],
                'COMMUNES_BENIN': ['Cotonou', 'Porto-Novo', 'Parakou', 'Bohicon', 'Abomey-Calavi', 'Djougou'],
                'PAYS': ['France', 'Belgique', 'Canada', 'Allemagne', 'Sénégal', "Côte d'Ivoire"]
            }
            pd.DataFrame(dict([(k, pd.Series(v)) for k, v in params_data.items()])).to_excel(writer, sheet_name='PARAMETRES', index=False)

init_coop_dec_excel()

def read_coop_sheet(sheet_name):
    if not os.path.exists(COOP_DEC_FILE): return None
    return pd.read_excel(COOP_DEC_FILE, sheet_name=sheet_name, dtype=str, header=0)

@app.route('/api/coop_dec/list', methods=['GET'])
def get_coop_dec_list():
    try:
        df = read_coop_sheet('ACCORDS')
        if df is None or df.empty: return jsonify([])
        df = df.replace({np.nan: None})
        for col in ['Date_Signature', 'Date_Debut', 'Date_Fin', 'Derniere_Reunion', 'Prochaine_Reunion']:
            if col in df.columns: df[col] = df[col].apply(clean_date)
        return jsonify(json.loads(df.to_json(orient='records', force_ascii=False)))
    except Exception as e:
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

@app.route('/api/coop_dec/parametres', methods=['GET'])
def get_coop_dec_parametres():
    try:
        df = read_coop_sheet('PARAMETRES')
        if df is None: return jsonify({})
        params = {col: [str(v).strip() for v in df[col].dropna() if str(v).strip()] for col in df.columns}
        return jsonify(params)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/coop_dec/actions', methods=['GET'])
def get_coop_dec_actions():
    try:
        df = read_coop_sheet('ACTIONS_PROJETS')
        if df is None: return jsonify([])
        df = df.replace({np.nan: None})
        return jsonify(json.loads(df.to_json(orient='records', force_ascii=False)))
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/coop_dec/echanges', methods=['GET'])
def get_coop_dec_echanges():
    try:
        df = read_coop_sheet('ECHANGES_VISITES')
        if df is None: return jsonify([])
        df = df.replace({np.nan: None})
        return jsonify(json.loads(df.to_json(orient='records', force_ascii=False)))
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ══════════════════════════════════════════════════════════════════════════════
# AUTO-MIGRATION: Création des tables si elles n'existent pas
# ══════════════════════════════════════════════════════════════════════════════

def _get_pg_connection():
    """Connexion directe PostgreSQL via psycopg2 pour DDL."""
    import psycopg2
    url = os.environ.get('SUPABASE_URL', '')
    # Extraire le project_ref de l'URL Supabase
    # https://xxxxx.supabase.co -> xxxxx
    project_ref = url.replace('https://', '').replace('.supabase.co', '').split('/')[0]
    db_password = os.environ.get('SUPABASE_DB_PASSWORD', '')
    if not db_password:
        raise RuntimeError("SUPABASE_DB_PASSWORD manquant dans l'environnement")
    return psycopg2.connect(
        host=f'db.{project_ref}.supabase.co',
        port=5432,
        dbname='postgres',
        user='postgres',
        password=db_password
    )


@app.route('/api/setup/create-tables', methods=['POST'])
def setup_create_tables():
    """Crée les tables manquantes dans Supabase (one-time setup)."""
    try:
        conn = _get_PG_connection()
        cur = conn.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS secteur_sous_secteur (
                id              SERIAL PRIMARY KEY,
                secteur         TEXT NOT NULL,
                sous_secteur    TEXT NOT NULL,
                created_at      TIMESTAMPTZ DEFAULT NOW(),
                UNIQUE(secteur, sous_secteur)
            );
            CREATE INDEX IF NOT EXISTS idx_secteur_sous ON secteur_sous_secteur(secteur);
        """)
        conn.commit()
        cur.close()
        conn.close()
        return jsonify({"message": "Tables créées avec succès"}), 200
    except Exception as e:
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500


@app.route('/api/banque/parametres/diag', methods=['GET'])
def diag_parametres():
    """Diagnostic: verifie l'etat de la table parametres."""
    result = {"status": "unknown", "details": {}}
    try:
        from db import get_supabase
        sb = get_supabase()
        # Test SELECT
        resp = sb.table('parametres').select('id', 'categorie', 'valeur').limit(5).execute()
        result["details"]["select"] = "OK"
        result["details"]["sample"] = resp.data
        # Test INSERT (puis rollback)
        test_val = f"__diag_test_{int(time.time())}"
        try:
            sb.table('parametres').insert({'categorie': '__diag', 'valeur': test_val, 'ordre': 0}).execute()
            result["details"]["insert"] = "OK"
            # Nettoyer
            sb.table('parametres').delete().eq('categorie', '__diag').eq('valeur', test_val).execute()
            result["details"]["delete"] = "OK"
        except Exception as e2:
            result["details"]["insert"] = f"FAIL: {str(e2)}"
            result["status"] = "read_only"
        if result["status"] != "read_only":
            result["status"] = "ok"
    except Exception as e:
        result["status"] = "error"
        result["details"]["error"] = str(e)
    return jsonify(result)


# ══════════════════════════════════════════════════════════════════════════════
if __name__ == '__main__':
    import socket
    local_ip = socket.gethostbyname(socket.gethostname())
    print("=" * 60)
    print("  SGIAD - Serveur de la Plateforme Nationale")
    print("=" * 60)
    print(f"  Acces local   : http://127.0.0.1:5000")
    print(f"  Acces reseau  : http://{local_ip}:5000")
    print(f"  Partagez cette URL avec vos collegues :")
    print(f"  >>> http://{local_ip}:5000 <<<")
    print("=" * 60)
    app.run(host='0.0.0.0', debug=True, port=5000)
