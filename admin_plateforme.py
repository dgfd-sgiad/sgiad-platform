# -*- coding: utf-8 -*-
"""SGIAD - Administration de la plateforme (Blueprint Flask).
Acces reserve aux administrateurs (variable d'env ADMIN_EMAILS)."""
import os
import json
import traceback
from functools import wraps
from pathlib import Path

from flask import Blueprint, jsonify, request, send_from_directory, g

from db import get_supabase

bp = Blueprint('admin_plateforme', __name__)

BASE_DIR = Path(__file__).resolve().parent
DATA_JSON = BASE_DIR / 'dgfd_platform_complete' / 'data' / 'dgfd_data.json'

ADMIN_EMAILS = [e.strip().lower() for e in os.environ.get('ADMIN_EMAILS', 'ekouhontode@finances.bj').split(',') if e.strip()]


def _current_admin():
    """Renvoie l'email si l'appelant est un administrateur connecte, sinon None."""
    auth_header = request.headers.get('Authorization', '') or ''
    token = auth_header.replace('Bearer ', '').strip()
    if not token:
        return None
    try:
        sb = get_supabase()
        resp = sb.auth.get_user(token)
        email = (resp.user.email or '').lower() if resp and resp.user else ''
        if email and email in ADMIN_EMAILS:
            return email
    except Exception:
        pass
    return None


def admin_required(f):
    @wraps(f)
    def wrapped(*args, **kwargs):
        email = _current_admin()
        if not email:
            return jsonify({'error': 'Acces reserve a l\'administrateur.'}), 403
        g.admin_email = email
        return f(*args, **kwargs)
    return wrapped


@bp.route('/admin/plateforme')
def admin_page():
    return send_from_directory(BASE_DIR / 'modules', 'admin_plateforme.html')


@bp.route('/api/admin/me')
@admin_required
def admin_me():
    return jsonify({'email': g.admin_email, 'admin': True})


@bp.route('/api/admin/users')
@admin_required
def admin_users():
    try:
        sb = get_supabase()
        resp = sb.auth.admin.list_users()
        users = []
        for u in (resp.users or []):
            users.append({
                'id': u.id,
                'email': u.email,
                'created_at': (u.created_at or '')[:10],
                'last_sign_in_at': (u.last_sign_in_at or '')[:10],
                'confirmed': bool(u.email_confirmed_at),
            })
        users.sort(key=lambda x: x['created_at'], reverse=True)
        return jsonify({'users': users})
    except Exception as e:
        traceback.print_exc()
        return jsonify({'error': f'Erreur lecture utilisateurs : {e}'}), 500


@bp.route('/api/admin/users', methods=['POST'])
@admin_required
def admin_create_user():
    data = request.get_json(force=True) or {}
    email = (data.get('email') or '').strip().lower()
    password = data.get('password') or ''
    if not email or not email.endswith('@finances.bj'):
        return jsonify({'error': 'Email professionnel @finances.bj requis.'}), 400
    if len(password) < 8:
        return jsonify({'error': 'Mot de passe : 8 caracteres minimum.'}), 400
    try:
        sb = get_supabase()
        sb.auth.admin.create_user({'email': email, 'password': password, 'email_confirm': True})
        return jsonify({'ok': True, 'message': f'Compte {email} cree.'})
    except Exception as e:
        traceback.print_exc()
        return jsonify({'error': f'Erreur creation : {e}'}), 500


@bp.route('/api/admin/users/reset', methods=['POST'])
@admin_required
def admin_reset_user():
    data = request.get_json(force=True) or {}
    email = (data.get('email') or '').strip().lower()
    if not email:
        return jsonify({'error': 'Email requis.'}), 400
    try:
        sb = get_supabase()
        sb.auth.reset_password_for_email(email)
        return jsonify({'ok': True, 'message': f'Email de reinitialisation envoye a {email}.'})
    except Exception as e:
        traceback.print_exc()
        return jsonify({'error': f'Erreur reinitialisation : {e}'}), 500


@bp.route('/api/admin/users/delete', methods=['POST'])
@admin_required
def admin_delete_user():
    data = request.get_json(force=True) or {}
    uid = (data.get('id') or '').strip()
    if not uid:
        return jsonify({'error': 'ID utilisateur requis.'}), 400
    try:
        sb = get_supabase()
        sb.auth.admin.delete_user(uid)
        return jsonify({'ok': True, 'message': 'Utilisateur supprime.'})
    except Exception as e:
        traceback.print_exc()
        return jsonify({'error': f'Erreur suppression : {e}'}), 500


@bp.route('/api/admin/contenu', methods=['GET', 'POST'])
@admin_required
def admin_contenu():
    try:
        if not DATA_JSON.exists():
            DATA_JSON.parent.mkdir(parents=True, exist_ok=True)
            default_data = {
                "STATS": {
                    "accords": {"valeur": "945", "icone": "📄", "label": "Accords signés", "sublabel": "2016 - 2025"},
                    "projets": {"valeur": "623", "icone": "📁", "label": "Projets actifs", "sublabel": "En cours"},
                    "partenaires": {"valeur": "78", "icone": "👥", "label": "Partenaires", "sublabel": "T&F"},
                    "montant": {"valeur": "8 452", "icone": "🪙", "label": "Milliards FCFA", "sublabel": "Mobilisés"},
                    "departements": {"valeur": "12", "icone": "🏛️", "label": "Départements", "sublabel": "Couvert"},
                    "clotures": {"valeur": "212", "icone": "✅", "label": "Projets clôturés", "sublabel": "Depuis 2016"}
                },
                "TODAY_STATS": [],
                "ACTUALITES": [],
                "PROJETS_UNE": [],
                "REPARTITION": {"Secteurs": ["Infrastructure", "Santé", "Éducation", "Agriculture", "Autres"], "Pourcentages": [28, 20, 20, 17, 15], "Couleurs": ["#28a745", "#dc3545", "#1e5aa8", "#f2c94c", "#6c757d"], "Total": 128},
                "DEPARTEMENTS": {},
                "EVENEMENTS": [],
                "ACCORDS": [],
                "DOCUMENTS": [],
                "MOTS_CLES": []
            }
            DATA_JSON.write_text(json.dumps(default_data, ensure_ascii=False, indent=2), encoding='utf-8')
        
        if request.method == 'POST':
            payload = request.get_json(force=True) or {}
            DATA_JSON.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding='utf-8')
            return jsonify({'ok': True, 'message': 'Données enregistrées avec succès.'})
        else:
            content = json.loads(DATA_JSON.read_text(encoding='utf-8'))
            return jsonify(content)
    except Exception as e:
        traceback.print_exc()
        return jsonify({'error': f'Erreur contenu : {e}'}), 500
