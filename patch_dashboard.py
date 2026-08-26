# -*- coding: utf-8 -*-
p = 'suivi.py'
s = open(p, encoding='utf-8').read()

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
    s = s.replace(old, '# [route obsolète supprimée - version complète conservée ligne ~608]', 1)
    open(p, 'w', encoding='utf-8').write(s)
    print('✅ Route minimaliste supprimée — la version complète est maintenant utilisée')
else:
    print('ℹ️ Route déjà supprimée ou modifiée')