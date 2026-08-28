# -*- coding: utf-8 -*-
import py_compile, re

print('=== 1. suivi.py (serveur) ===')
try:
    py_compile.compile('suivi.py', doraise=True)
    print('  [OK] syntaxe Python valide')
except Exception as e:
    print('  [!!] ERREUR SYNTAXE :', e)

t = open('suivi.py', encoding='utf-8').read()
for k in ["/api/suivi/recap", 'projets_out = []', 'projets_out.append', "'projets': projets_out", 'code_projet']:
    print(('  [OK] ' if k in t else '  [!!] ABSENT : ') + k)

print('=== 2. recap.html (page) ===')
h = open('modules/recap.html', encoding='utf-8').read()
for k in ['function _fetchJSON', '/api/suivi/recap', 'const D=', 'function renderRail', 'id="rail"', 'renderRail();', 'function render(){']:
    print(('  [OK] ' if k in h else '  [!!] ABSENT : ') + k)
print('  nb "const D=" :', len(re.findall(r'const D\s*=', h)))

print('=== 3. endpoint en direct ===')
try:
    import requests
    r = requests.get('http://127.0.0.1:5000/api/suivi/recap', timeout=10)
    d = r.json()
    print('  HTTP', r.status_code, '· clés :', sorted(d.keys()))
    print('  projets :', len(d.get('projets', [])), '· cells :', len(d.get('cells', [])))
except Exception as e:
    print('  [!!] serveur injoignable :', e)
    