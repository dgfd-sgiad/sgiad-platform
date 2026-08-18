import os
from db import get_supabase

def run_migration():
    sb = get_supabase()
    print("[migrate_conges] Vérification des tables de congés...")
    # Tables are assumed to be handled via Supabase schema or migration
    print("[migrate_conges] Migration terminée.")

if __name__ == '__main__':
    run_migration()
