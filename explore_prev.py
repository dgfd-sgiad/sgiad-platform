# -*- coding: utf-8 -*-
import re, glob

cands = []
for f in glob.glob('*.html') + glob.glob('modules/*.html'):
    try:
        t = open(f, encoding='utf-8', errors='ignore').read()
    except Exception:
        continue
    if ('v-title' in t) or ('Fraunces' in t) or ('i-cum' in t):
        cands.append((f, len(t), t))

if not cands:
    print('❌ Aucun fichier design trouvé (marqueurs v-title / Fraunces / i-cum absents)')
    raise SystemExit

f, L, s = max(cands, key=lambda x: x[1])
print('📄 FICHIER ANALYSÉ :', f, '·', L, 'caractères')

print('\n=== 1. RESSOURCES EXTERNES (polices, echarts) ===')
for m in re.findall(r'<(?:script src|link href)="([^"]+)"', s):
    print(' ·', m)
print('Polices Fraunces/Archivo :', '✅' if ('Fraunces' in s and 'Archivo' in s) else '❌ MANQUANTES → rendu différent')
print('ECharts présent :', '✅' if ('themeRiver' in s or 'echarts' in s.lower()) else '❌ ABSENT → graphiques vides')

print('\n=== 2. COHÉRENCE IDS (HTML vs JS) ===')
ids_html = set(re.findall(r'id="([^"]+)"', s))
ids_js = set(re.findall(r"getElementById\('([^']+)'\)", s))
manquants = sorted(ids_js - ids_html)
print('IDs appelés par le JS mais ABSENTS du HTML :', manquants if manquants else '✅ aucun')

print('\n=== 3. CONSTANTES DE DONNÉES ===')
for m in re.finditer(r'(?:const|let|var)\s+([A-Z][A-Z_0-9]*)\s*=\s*', s):
    line = s.count('\n', 0, m.start()) + 1
    snippet = s[m.end():m.end() + 100].replace('\n', ' ')
    print(f' · L{line} {m.group(1)} = {snippet}...')

print('\n=== 4. DONNÉES RÉELLES (fetch/API) ? ===')
api = re.findall(r"fetch\(['\"]([^'\"]+)", s)
print(api if api else '❌ AUCUN fetch → tourne sur données statiques (commentaires figés)')

print('\n=== 5. FONCTIONS DE RENDU ===')
for m in re.finditer(r'function\s+([a-zA-Z0-9_]+)\s*\(', s):
    print(' ·', m.group(1))

print('\n=== 6. VERBATIM : verdict / insights / figs / render ===')
for name in ['verdict', 'insights', 'figs', 'render', 'aggregate', 'agg', 'recap']:
    i = s.find('function ' + name + '(')
    if i >= 0:
        print('\n----- function ' + name + ' -----')
        print(s[i:i + 1500].replace('\r', ''))
        