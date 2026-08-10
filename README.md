# SGIAD - Plateforme Nationale de Suivi

## Présentation

Application Flask de suivi des accords financiers et de la coopération décentralisée.

- Backend principal : `api.py`
- Authentification : `auth.py` via Supabase Auth
- Module accords financiers : `accords_financiers.py`
- Frontend statique : `accueil.html`, `index.html`, `css/`, `js/`, `assets/`
- Déploiement prévu avec Render Cloud

## Prérequis

- Python 3.10+ installé
- `pip` disponible
- Compte Supabase avec projet créé
- Clé Supabase et URL de projet

## Installation locale

1. Ouvrir PowerShell dans le dossier du projet :
   ```powershell
   cd C:\Users\ERNEST\Desktop\SGIAD_Projet
   ```

2. Installer les dépendances :
   ```powershell
   pip install -r requirements.txt
   ```

3. Copier le fichier d'exemple d'environnement :
   ```powershell
   copy .env.example .env
   ```

4. Ouvrir `.env` et renseigner au minimum :
   - `SUPABASE_URL`
   - `SUPABASE_KEY`

5. Optionnel : exécuter le script de configuration locale :
   ```powershell
   .\setup_dev.ps1
   ```

6. Lancer le serveur local :
   ```powershell
   python api.py
   ```

6. Ouvrir l'application dans le navigateur :
   - `http://127.0.0.1:5000`

## Supabase

1. Créer un projet sur https://supabase.com.
2. Récupérer l'URL du projet et la clé **service_role** (Settings > API).
3. Exécuter `schema.sql` dans l'éditeur SQL Supabase (copier-coller tout le fichier).
4. Exécuter `schema_rls.sql` de la même manière (nouvel onglet SQL, copier-coller — **ne pas** utiliser `\i`, réservé au terminal psql).
5. Si besoin, migrer les données avec :
   ```powershell
   python scripts/migrate_to_supabase.py
   ```

> En production, utilisez la clé **service_role** dans `SUPABASE_KEY` côté serveur uniquement.
> Le fichier `schema_rls.sql` bloque l'accès direct anon aux données sensibles.

## Variables d'environnement

- `SUPABASE_URL` : URL du projet Supabase
- `SUPABASE_KEY` : clé **service_role** Supabase (backend Flask)
- `FLASK_ENV` (optionnel) : `development` ou `production`
- `FLASK_DEBUG` (optionnel) : `1` pour le développement local
- `SIGNUP_ENABLED` (optionnel) : `false` par défaut — mettre `true` pour autoriser les inscriptions
- `ALLOWED_EMAIL_DOMAINS` (optionnel) : domaines autorisés pour les inscriptions, vide = tous les domaines si inscriptions ouvertes

> Le fichier `.env` ne doit pas être versionné. Il est déjà ignoré par `.gitignore`.

## Déploiement sur Render

Le projet est déjà configuré pour Render avec :

- `render.yaml`
- `Procfile`
- `gunicorn_conf.py`

### Étapes Render

1. Créer un service web Render.
2. Connecter ton dépôt GitHub/GitLab.
3. Vérifier les commandes :
   - Build : `pip install -r requirements.txt`
   - Start : `gunicorn -c gunicorn_conf.py api:app`
4. Ajouter les variables d'environnement Render :
   - `SUPABASE_URL`
   - `SUPABASE_KEY`
   - `FLASK_DEBUG=0` (recommandé en production)
5. Activer `autoDeploy` si tu veux des mises à jour automatiques au push.

## Lancement en production locale

Tu peux tester en local avec Gunicorn :

```powershell
pip install gunicorn
gunicorn -c gunicorn_conf.py api:app
```

## Remarques

- Le frontend est servi via `accueil.html` et `index.html`.
- Les fichiers Excel (`.xlsx`) ne sont pas recommandés en production.
- Le point d'entrée principal est `api.py`.
