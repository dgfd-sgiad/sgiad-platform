#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
================================================================================
MANAGER DE SAUVEGARDES AUTOMATIQUES - DGFD Platform
================================================================================
Gère les sauvegardes automatiques du fichier JSON de données avec :
- Sauvegarde automatique à chaque modification
- Rotation (garde les N derniers backups)
- Restauration d'un backup depuis l'interface admin
- Sauvegarde planifiée via cron / tâche planifiée

Fichier : backup_manager.py
Version : 1.0
================================================================================
"""

import json
import os
import shutil
import gzip
from datetime import datetime, timedelta
from pathlib import Path

# =============================================================================
# CONFIGURATION
# =============================================================================

# Dossier racine (détecté automatiquement)
BASE_DIR = Path(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = BASE_DIR / "data"
BACKUP_DIR = BASE_DIR / "backups"
DATA_FILE = DATA_DIR / "dgfd_data.json"

# Paramètres de rotation
MAX_BACKUPS = 10           # Nombre max de backups à conserver
BACKUP_ON_SAVE = True      # Sauvegarder automatiquement à chaque save_data()
COMPRESS_BACKUPS = True    # Compresser les backups avec gzip

# =============================================================================
# UTILITAIRES
# =============================================================================

def ensure_backup_dir():
    """Crée le dossier de backups s'il n'existe pas."""
    BACKUP_DIR.mkdir(parents=True, exist_ok=True)


def get_backup_files():
    """Retourne la liste des fichiers de backup triés par date (plus récent d'abord)."""
    ensure_backup_dir()
    backups = []
    for f in BACKUP_DIR.iterdir():
        if f.name.startswith("dgfd_backup_") and (f.suffix == ".json" or f.suffix == ".gz"):
            backups.append(f)
    backups.sort(key=lambda x: x.stat().st_mtime, reverse=True)
    return backups


def get_backup_info(backup_path):
    """Retourne les informations d'un backup (taille, date, etc.)."""
    stat = backup_path.stat()
    size = stat.st_size
    date_str = datetime.fromtimestamp(stat.st_mtime).strftime("%d/%m/%Y %H:%M:%S")
    
    # Format taille
    if size < 1024:
        size_str = f"{size} o"
    elif size < 1024 * 1024:
        size_str = f"{size / 1024:.1f} Ko"
    else:
        size_str = f"{size / (1024 * 1024):.1f} Mo"
    
    return {
        "filename": backup_path.name,
        "date": date_str,
        "size": size_str,
        "size_bytes": size,
        "path": str(backup_path)
    }


# =============================================================================
# CRÉATION DE SAUVEGARDE
# =============================================================================

def create_backup(source_file=None, label=None):
    """
    Crée une sauvegarde du fichier de données.
    
    Args:
        source_file: Chemin du fichier à sauvegarder (défaut: DATA_FILE)
        label: Label optionnel pour identifier le backup (ex: 'manual', 'auto')
    
    Returns:
        dict: {'success': bool, 'backup_path': str, 'message': str}
    """
    ensure_backup_dir()
    
    src = Path(source_file) if source_file else DATA_FILE
    
    if not src.exists():
        return {
            "success": False,
            "backup_path": None,
            "message": f"❌ Fichier source introuvable : {src}"
        }
    
    # Générer le nom du fichier
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    label_part = f"_{label}" if label else ""
    ext = ".json.gz" if COMPRESS_BACKUPS else ".json"
    backup_name = f"dgfd_backup_{timestamp}{label_part}{ext}"
    backup_path = BACKUP_DIR / backup_name
    
    try:
        if COMPRESS_BACKUPS:
            # Compression gzip
            with open(src, 'rb') as f_in:
                with gzip.open(backup_path, 'wb') as f_out:
                    shutil.copyfileobj(f_in, f_out)
        else:
            # Copie simple
            shutil.copy2(src, backup_path)
        
        # Rotation : supprimer les anciens backups
        cleanup_old_backups()
        
        info = get_backup_info(backup_path)
        return {
            "success": True,
            "backup_path": str(backup_path),
            "message": f"✅ Sauvegarde créée : {backup_name} ({info['size']})"
        }
    
    except Exception as e:
        return {
            "success": False,
            "backup_path": None,
            "message": f"❌ Erreur lors de la sauvegarde : {str(e)}"
        }


def auto_backup():
    """Sauvegarde automatique déclenchée par data_manager.save_data()."""
    if BACKUP_ON_SAVE and DATA_FILE.exists():
        return create_backup(label="auto")
    return {"success": False, "message": "Sauvegarde auto désactivée ou fichier inexistant"}


# =============================================================================
# ROTATION DES BACKUPS
# =============================================================================

def cleanup_old_backups(max_count=None):
    """
    Supprime les backups les plus anciens pour ne garder que max_count.
    
    Args:
        max_count: Nombre max de backups à conserver (défaut: MAX_BACKUPS)
    """
    max_count = max_count or MAX_BACKUPS
    backups = get_backup_files()
    
    if len(backups) > max_count:
        to_delete = backups[max_count:]
        for backup in to_delete:
            try:
                backup.unlink()
                print(f"🗑️  Backup supprimé : {backup.name}")
            except Exception as e:
                print(f"⚠️  Impossible de supprimer {backup.name} : {e}")


# =============================================================================
# RESTAURATION
# =============================================================================

def restore_backup(backup_path, target_file=None):
    """
    Restaure un backup vers le fichier de données actif.
    
    Args:
        backup_path: Chemin du fichier de backup à restaurer
        target_file: Fichier de destination (défaut: DATA_FILE)
    
    Returns:
        dict: {'success': bool, 'message': str}
    """
    target = Path(target_file) if target_file else DATA_FILE
    backup = Path(backup_path)
    
    if not backup.exists():
        return {"success": False, "message": f"❌ Backup introuvable : {backup_path}"}
    
    try:
        # 1. Sauvegarder l'état actuel avant restauration
        pre_restore = create_backup(label="pre_restore")
        
        # 2. Restaurer le backup
        if backup.suffix == ".gz":
            with gzip.open(backup, 'rb') as f_in:
                with open(target, 'wb') as f_out:
                    shutil.copyfileobj(f_in, f_out)
        else:
            shutil.copy2(backup, target)
        
        return {
            "success": True,
            "message": f"✅ Données restaurées depuis {backup.name}"
        }
    
    except Exception as e:
        return {
            "success": False,
            "message": f"❌ Erreur lors de la restauration : {str(e)}"
        }


# =============================================================================
# EXPORT / IMPORT MANUEL
# =============================================================================

def export_data_json():
    """Retourne le contenu JSON actuel pour export manuel."""
    if DATA_FILE.exists():
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            return f.read()
    return None


def import_data_json(json_content):
    """
    Importe un contenu JSON en remplaçant le fichier actuel.
    
    Args:
        json_content: Chaîne JSON valide
    
    Returns:
        dict: {'success': bool, 'message': str}
    """
    try:
        # Valider le JSON
        data = json.loads(json_content)
        
        # Backup avant import
        create_backup(label="pre_import")
        
        # Écrire le nouveau fichier
        DATA_DIR.mkdir(parents=True, exist_ok=True)
        with open(DATA_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        return {"success": True, "message": "✅ Données importées avec succès"}
    
    except json.JSONDecodeError as e:
        return {"success": False, "message": f"❌ JSON invalide : {str(e)}"}
    except Exception as e:
        return {"success": False, "message": f"❌ Erreur : {str(e)}"}


# =============================================================================
# STATISTIQUES
# =============================================================================

def get_backup_stats():
    """Retourne les statistiques des backups."""
    backups = get_backup_files()
    
    if not backups:
        return {
            "count": 0,
            "total_size": "0 Ko",
            "oldest": None,
            "newest": None,
            "backups": []
        }
    
    total_size = sum(b.stat().st_size for b in backups)
    
    if total_size < 1024:
        size_str = f"{total_size} o"
    elif total_size < 1024 * 1024:
        size_str = f"{total_size / 1024:.1f} Ko"
    else:
        size_str = f"{total_size / (1024 * 1024):.1f} Mo"
    
    return {
        "count": len(backups),
        "total_size": size_str,
        "oldest": get_backup_info(backups[-1]),
        "newest": get_backup_info(backups[0]),
        "backups": [get_backup_info(b) for b in backups]
    }


# =============================================================================
# POINT D'ENTRÉE CLI (pour cron / tâches planifiées)
# =============================================================================

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Gestionnaire de backups DGFD")
    parser.add_argument("--backup", action="store_true", help="Créer une sauvegarde maintenant")
    parser.add_argument("--restore", type=str, help="Restaurer un backup (chemin du fichier)")
    parser.add_argument("--list", action="store_true", help="Lister les backups existants")
    parser.add_argument("--cleanup", action="store_true", help="Nettoyer les vieux backups")
    parser.add_argument("--stats", action="store_true", help="Afficher les statistiques")
    parser.add_argument("--max", type=int, default=MAX_BACKUPS, help=f"Nombre max de backups (défaut: {MAX_BACKUPS})")
    
    args = parser.parse_args()
    
    if args.backup:
        result = create_backup(label="scheduled")
        print(result["message"])
    elif args.restore:
        result = restore_backup(args.restore)
        print(result["message"])
    elif args.list:
        backups = get_backup_files()
        if not backups:
            print("Aucun backup trouvé.")
        else:
            print(f"{'#':<4} {'Fichier':<40} {'Date':<20} {'Taille':<10}")
            print("-" * 80)
            for i, b in enumerate(backups, 1):
                info = get_backup_info(b)
                print(f"{i:<4} {info['filename']:<40} {info['date']:<20} {info['size']:<10}")
    elif args.cleanup:
        cleanup_old_backups(args.max)
        print(f"✅ Rotation effectuée : {MAX_BACKUPS} backups conservés max")
    elif args.stats:
        stats = get_backup_stats()
        print(f"📊 Statistiques des backups")
        print(f"   Nombre : {stats['count']}")
        print(f"   Taille totale : {stats['total_size']}")
        if stats['newest']:
            print(f"   Dernier backup : {stats['newest']['date']}")
    else:
        print("Utilisez --backup, --restore, --list, --cleanup ou --stats")
        print("Exemple : python backup_manager.py --backup")
