import re
s = open('api.py', encoding='utf-8').read()
route = '''
@app.route('/api/decaissements/accords', methods=['GET'])
def decaissements_accords():
    from db import get_supabase
    try:
        sb = get_supabase()
        r = sb.table('accords_consolides').select('*').order('code_projet').execute()
        return jsonify(r.data or [])
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500
'''
if "@app.route('/api/decaissements/accords'" not in s:
    marker = "if __name__ == '__main__':"
    if marker in s:
        s = s.replace(marker, route + '\n' + marker)
        open('api.py', 'w', encoding='utf-8').write(s)
        print('✅ Route /api/decaissements/accords ajoutée')
    else:
        print('❌ Marqueur introuvable')
else:
    print('✅ Route déjà présente')
    