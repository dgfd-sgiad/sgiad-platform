# -*- coding: utf-8 -*-
import re, glob

cands = []
for f in glob.glob('*.html') + glob.glob('modules/*.html'):
    try:
        t = open(f, encoding='utf-8', errors='ignore').read()
    except Exception:
        continue
    if ('v-title' in t) or ('Fraunces' in t):
        cands.append((f, len(t), t))
if not cands:
    print('❌ aucun fichier design'); raise SystemExit
f, L, s = max(cands, key=lambda x: x[1])
print('📄 Fichier analysé :', f, '·', L, 'caractères')
print('⚠️ Ouvre EXACTEMENT : http://127.0.0.1:5000/' + f.replace('\\', '/'))

ids_html = set(re.findall(r'id="([^"]+)"', s))
ids_js = set(re.findall(r"getElementById\('([^']+)'\)", s))
ids_js |= set(re.findall(r"querySelector\('#([a-zA-Z0-9_-]+)", s))
print('\nIDs appelés par le JS mais ABSENTS du HTML :', sorted(ids_js - ids_html) or '✅ aucun')

print('\n--- conteneurs de commentaires ---')
for i in ['selinfo', 'v-title', 'v-text', 'figs', 'recap', 'i-cum', 'i-trim', 'i-sec', 'i-par', 'i-reco', 'alerts', 't-proj', 't-reco', 'tl-revues']:
    print(f'  {"✅" if ("id=' + chr(34) + i + chr(34)) in s else "❌ ABSENT"}  #{i}')

print('\n--- constantes de données ---')
for name in ['D', 'PROJETS', 'RECOS', 'REVUES']:
    if re.search(r'const ' + name + r'\s*=', s):
        print('  ✅ const', name)
    else:
        print('  ❌ const', name, 'MANQUANTE → erreur JS au chargement')
print('  fetch API :', re.findall(r"fetch\(['\"]([^'\"]+)", s) or '❌ aucun (données démo)')

print('\n--- textes codés en dur (à dynamiser) ---')
for pat in ['188 projets', '33 partenaires']:
    print(f'  {"⚠️ présent" if pat in s else "— absent"}  "{pat}"')
    