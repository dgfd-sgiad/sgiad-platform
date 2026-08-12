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


@bp.route('/api/admin/contenu', methods=['GET'])
@admin_required
def admin_contenu_get():
    try:
        from api import _build_accueil_data
        return jsonify(_build_accueil_data())
    except Exception:
        traceback.print_exc()
        try:
            with open(DATA_JSON, 'r', encoding='utf-8') as f:
                return jsonify(json.load(f))
        except Exception as e2:
            return jsonify({'error': f'Erreur lecture contenu : {e2}'}), 500


ALLOWED_CONTENT_KEYS = {'STATS', 'TODAY_STATS', 'ACTUALITES', 'PROJETS_UNE', 'REPARTITION',
                        'REPARTITION_PARTENAIRES', 'DEPARTEMENTS', 'EVENEMENTS', 'ACCORDS',
                        'DOCUMENTS', 'MOTS_CLES'}


@bp.route('/api/admin/contenu', methods=['POST'])
@admin_required
def admin_contenu_save():
    data = request.get_json(force=True) or {}
    section = str(data.get('section') or '').strip()
    valeur = data.get('valeur')
    if section not in ALLOWED_CONTENT_KEYS:
        return jsonify({'error': f'Section inconnue : {section}'}), 400
    if valeur is None:
        return jsonify({'error': 'Valeur manquante.'}), 400
    try:
        with open(DATA_JSON, 'r', encoding='utf-8') as f:
            contenu = json.load(f)
        if not isinstance(contenu, dict) or not ALLOWED_CONTENT_KEYS.intersection(contenu.keys()):
            return jsonify({'error': 'Fichier de contenu invalide, sauvegarde refusee.'}), 500
        contenu[section] = valeur
        with open(DATA_JSON, 'w', encoding='utf-8') as f:
            json.dump(contenu, f, ensure_ascii=False, indent=2)
        # Invalide le cache de la page d'accueil pour voir les changements immediatement
        try:
            from api import _accueil_cache
            _accueil_cache['ts'] = 0
            _accueil_cache['data'] = None
        except Exception:
            pass
        return jsonify({'ok': True, 'message': f'Section {section} sauvegardee.'})
    except Exception as e:
        traceback.print_exc()
        return jsonify({'error': f'Erreur sauvegarde : {e}'}), 500
