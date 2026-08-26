# -*- coding: utf-8 -*-
p = 'suivi.py'
s = open(p, encoding='utf-8').read()

# 1) Supprimer l'ancienne route simplifiée qui MASQUE le vrai dashboard
old = """@bp.route('/api/suivi/dashboard')
def get_dashboard():
    try:
        sb = get_supabase()
        revues = sb.table('revues').select('*').execute().data or []
        recommandations = sb.table('recommandations').select('*').execute().data or []
        return jsonify({'revues': revues, 'recommandations': recommandations})
    except Exception as e:
        return jsonify({'error': str(e)}), 500"""

if old in s:
    s = s.replace(old, "# (route dashboard simplifiee supprimee : elle masquait le vrai tableau de bord)", 1)
    print('✅ Ancienne route dashboard SIMPLIFIÉE supprimée → la version complète prend la main')
else:
    print('❌ Ancienne route introuvable')

# 2) Créer la table reco_historique (corrige le 500 de l'historique)
old2 = '        cur.execute("SELECT COUNT(*) FROM revues")'
new2 = '''        cur.execute("""
            CREATE TABLE IF NOT EXISTS reco_historique (
                id BIGSERIAL PRIMARY KEY,
                reco_id INTEGER,
                ancien_statut TEXT,
                nouveau_statut TEXT,
                commentaire TEXT,
                auteur TEXT,
                created_at TIMESTAMPTZ DEFAULT NOW()
            );
        """)
        cur.execute("SELECT COUNT(*) FROM revues")'''
if old2 in s:
    s = s.replace(old2, new2, 1)
    print("✅ Table reco_historique créée au démarrage (historique réparé)")
else:
    print('❌ Ancre reco_historique introuvable')

open(p, 'w', encoding='utf-8').write(s)
print('Terminé.')
