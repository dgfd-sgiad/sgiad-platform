# -*- coding: utf-8 -*-
import re, glob
import requests

BASE = 'http://127.0.0.1:5000'
files = glob.glob('modules/*.html') + glob.glob('*.html')
routes = set()

for f in files:
    try:
        s = open(f, encoding='utf-8').read()
    except Exception:
        continue
    # routes directes /api/...
    for m in re.findall(r'/api/[A-Za-z0-9_\-/]+', s):
        routes.add(re.sub(r'\$\{[^}]*\}', '1', m))
    # routes via API_BASE
    bases = set(re.findall(r"API_BASE\s*=\s*[`'\"][^`'\"]*?(/api/[A-Za-z0-9_\-]+)", s))
    for suffix in re.findall(r"\$\{API_BASE\}(/[A-Za-z0-9_\-/]+)", s):
        for b in bases:
            routes.add(b + suffix)

ok, warn, ko = [], [], []
for r in sorted(routes):
    try:
        code = requests.get(BASE + r, timeout=15).status_code
    except Exception:
        code = 'ERR'
    line = f'{code}  {r}'
    if code == 200: ok.append('✅ ' + line)
    elif code in (401, 403, 405): warn.append('🔒 ' + line)
    else: ko.append('❌ ' + line)

print('=== ROUTES CASSÉES / MANQUANTES ===')
print('\n'.join(ko) or '(aucune)')
print('\n=== AUTH / AUTRE MÉTHODE (normal) ===')
print('\n'.join(warn) or '(aucune)')
print('\n=== OK ===')
print('\n'.join(ok) or '(aucune)')