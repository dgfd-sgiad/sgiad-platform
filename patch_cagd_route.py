s = open('api.py', encoding='utf-8').read()
route = '''
@app.route('/api/decaissements/cagd', methods=['GET'])
def decaissements_cagd():
    from db import get_supabase
    try:
        sb = get_supabase()
        r = sb.table('decaissements_cagd').select('*').execute()
        return jsonify(r.data or [])
    except Exception as e:
        return jsonify({'error': str(e)}), 500
'''
if '/api/decaissements/cagd' not in s:
    marker = "if __name__ == '__main__':"
    s = s.replace(marker, route + '\n' + marker, 1)
    open('api.py', 'w', encoding='utf-8').write(s)
    print('✅ Route /api/decaissements/cagd ajoutée')
else:
    print('✅ Route déjà présente')
    