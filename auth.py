# -*- coding: utf-8 -*-
"""
AUTH.PY - Authentification Supabase
=====================================
Middleware et routes pour l'authentification via Supabase Auth.

Routes:
    POST /api/auth/login       - Connexion email/mot de passe
    POST /api/auth/signup      - Inscription (optionnel)
    POST /api/auth/logout      - Deconnexion
    GET  /api/auth/user        - Infos utilisateur courant

Usage dans les routes protegees:
    from auth import require_auth

    @app.route('/api/protege')
    @require_auth
    def ma_route():
        user = request.current_user  # dict avec email, id, etc.
"""

import os
import functools
import traceback
from flask import Blueprint, request, jsonify

bp = Blueprint('auth', __name__)

# ── Controle des inscriptions ──
# Mettre SIGNUP_ENABLED=false (variable d'env Render) pour fermer les inscriptions.
SIGNUP_ENABLED = os.environ.get('SIGNUP_ENABLED', 'true').lower() in ('1', 'true', 'yes', 'oui')
# Domaines d'email autorises pour l'inscription (separes par des virgules)
ALLOWED_EMAIL_DOMAINS = [d.strip().lower().lstrip('@')
                         for d in os.environ.get('ALLOWED_EMAIL_DOMAINS', '@finances.bj').split(',')
                         if d.strip()]


def _email_domain_allowed(email):
    """Verifie que l'email appartient a un domaine autorise."""
    if '@' not in email:
        return False
    domain = email.rsplit('@', 1)[-1].strip().lower()
    return domain in ALLOWED_EMAIL_DOMAINS


def get_supabase():
    """Retourne le client Supabase (partage avec db.py)."""
    from db import get_supabase as _get_sb
    return _get_sb()


# ══════════════════════════════════════════════════════════════════════
# DECORATEUR: require_auth
# ══════════════════════════════════════════════════════════════════════

def require_auth(f):
    """Decorateur pour proteger une route.
    Verifie le token JWT Supabase dans le header Authorization."""
    @functools.wraps(f)
    def decorated(*args, **kwargs):
        auth_header = request.headers.get('Authorization', '')
        if not auth_header.startswith('Bearer '):
            return jsonify({'error': 'Token d\'authentification requis'}), 401

        token = auth_header.replace('Bearer ', '')
        try:
            sb = get_supabase()
            user_resp = sb.auth.get_user(token)
            if not user_resp or not user_resp.user:
                return jsonify({'error': 'Token invalide ou expire'}), 401

            # Stocker l'utilisateur pour usage dans la route
            request.current_user = {
                'id': user_resp.user.id,
                'email': user_resp.user.email,
                'role': getattr(user_resp.user, 'role', 'authenticated'),
            }
            return f(*args, **kwargs)
        except Exception as e:
            traceback.print_exc()
            return jsonify({'error': 'Erreur d\'authentification'}), 401

    return decorated


# ══════════════════════════════════════════════════════════════════════
# ROUTES AUTH
# ══════════════════════════════════════════════════════════════════════

@bp.route('/api/auth/login', methods=['POST'])
def login():
    """Connexion avec email et mot de passe."""
    try:
        data = request.get_json(force=True) or {}
        email = data.get('email', '').strip()
        password = data.get('password', '')

        if not email or not password:
            return jsonify({'error': 'Email et mot de passe requis'}), 400

        sb = get_supabase()
        resp = sb.auth.sign_in_with_password({
            'email': email,
            'password': password,
        })

        if not resp or not resp.session:
            return jsonify({'error': 'Identifiants incorrects'}), 401

        return jsonify({
            'access_token': resp.session.access_token,
            'refresh_token': resp.session.refresh_token,
            'expires_in': resp.session.expires_in,
            'user': {
                'id': resp.user.id,
                'email': resp.user.email,
            }
        })
    except Exception as e:
        traceback.print_exc()
        error_msg = str(e)
        if 'Invalid login credentials' in error_msg:
            return jsonify({'error': 'Email ou mot de passe incorrect'}), 401
        return jsonify({'error': 'Erreur de connexion, veuillez réessayer.'}), 500


@bp.route('/api/auth/signup', methods=['POST'])
def signup():
    """Inscription d'un nouvel utilisateur (email @finances.bj uniquement)."""
    try:
        if not SIGNUP_ENABLED:
            return jsonify({'error': 'Les inscriptions sont fermées. Contactez l\'administrateur.'}), 403

        data = request.get_json(force=True) or {}
        email = data.get('email', '').strip()
        password = data.get('password', '')

        if not email or not password:
            return jsonify({'error': 'Email et mot de passe requis'}), 400
        if not _email_domain_allowed(email):
            domaines = ', '.join('@' + d for d in ALLOWED_EMAIL_DOMAINS)
            return jsonify({'error': f'Inscription réservée aux emails : {domaines}'}), 403
        if len(password) < 8:
            return jsonify({'error': 'Mot de passe: minimum 8 caracteres'}), 400

        sb = get_supabase()
        resp = sb.auth.sign_up({
            'email': email,
            'password': password,
        })

        if not resp or not resp.user:
            return jsonify({'error': 'Echec de l\'inscription'}), 500

        result = {
            'message': 'Inscription reussie',
            'user': {
                'id': resp.user.id,
                'email': resp.user.email,
            }
        }

        # Si la session est disponible (email confirm desactive)
        if resp.session:
            result['access_token'] = resp.session.access_token
            result['refresh_token'] = resp.session.refresh_token

        return jsonify(result), 201
    except Exception as e:
        traceback.print_exc()
        error_msg = str(e)
        if 'already registered' in error_msg:
            return jsonify({'error': 'Cet email est deja utilise'}), 409
        if 'rate limit' in error_msg.lower():
            return jsonify({'error': 'Trop de tentatives. Veuillez réessayer dans quelques minutes.'}), 429
        return jsonify({'error': 'Erreur d\'inscription, veuillez réessayer.'}), 500


@bp.route('/api/auth/logout', methods=['POST'])
def logout():
    """Deconnexion."""
    try:
        auth_header = request.headers.get('Authorization', '')
        if auth_header.startswith('Bearer '):
            # Supabase gere la deconnexion cote client (suppression du token)
            pass
        return jsonify({'message': 'Deconnecte'})
    except Exception:
        return jsonify({'error': 'Erreur de deconnexion'}), 500


@bp.route('/api/auth/user', methods=['GET'])
def get_user():
    """Retourne les infos de l'utilisateur courant."""
    auth_header = request.headers.get('Authorization', '')
    if not auth_header.startswith('Bearer '):
        return jsonify({'error': 'Non authentifie'}), 401

    token = auth_header.replace('Bearer ', '')
    try:
        sb = get_supabase()
        user_resp = sb.auth.get_user(token)
        if not user_resp or not user_resp.user:
            return jsonify({'error': 'Token invalide'}), 401

        return jsonify({
            'id': user_resp.user.id,
            'email': user_resp.user.email,
            'created_at': str(user_resp.user.created_at),
        })
    except Exception:
        return jsonify({'error': 'Token invalide'}), 401


@bp.route('/api/auth/refresh', methods=['POST'])
def refresh_token():
    """Rafraichit un token d'acces expire."""
    try:
        data = request.get_json(force=True) or {}
        refresh_token = data.get('refresh_token', '')

        if not refresh_token:
            return jsonify({'error': 'refresh_token requis'}), 400

        sb = get_supabase()
        resp = sb.auth.refresh_session(refresh_token)

        if not resp or not resp.session:
            return jsonify({'error': 'Token de rafraichissement invalide'}), 401

        return jsonify({
            'access_token': resp.session.access_token,
            'refresh_token': resp.session.refresh_token,
            'expires_in': resp.session.expires_in,
        })
    except Exception:
        traceback.print_exc()
        return jsonify({'error': 'Token de rafraichissement invalide'}), 401
