# -*- coding: utf-8 -*-
s = open('modules/prev_decaissements.html', encoding='utf-8').read()
lines = s.split('\n')
print('TOTAL LIGNES :', len(lines))
print('--- appels fetch / API ---')
for i, l in enumerate(lines, 1):
    if 'fetch(' in l or '/api/' in l:
        print(f'{i}: {l.strip()[:160]}')
print('--- marqueurs démo / données dures ---')
for i, l in enumerate(lines, 1):
    low = l.lower()
    if 'demo' in low or 'démonstration' in low or 'sample' in low or 'P-2023-AFD' in l or 'Dassa' in l or 'const DEMO' in l or 'donneesDemo' in low:
        print(f'{i}: {l.strip()[:160]}')
        