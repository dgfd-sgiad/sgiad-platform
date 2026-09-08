# -*- coding: utf-8 -*-
import re

s = open('modules/recos.html', encoding='utf-8', errors='ignore').read()
print('TAILLE :', len(s))

idx = []
i = s.find('c-th')
while i != -1 and len(idx) < 6:
    idx.append(i)
    i = s.find('c-th', i + 1)
print('occurrences de c-th :', len(idx))

for k, pos in enumerate(idx):
    print('\n===== OCCURRENCE', k + 1, '(pos', pos, ') =====')
    print(s[max(0, pos - 400):pos + 600].replace('\r', ''))

print('\n===== fonctions liées aux thèmes =====')
cnt = 0
for m in re.finditer(r'function\s+\w*[Tt]h\w*\s*\(', s):
    print('\n---', m.group(0), '---')
    print(s[m.start():m.start() + 700].replace('\r', ''))
    cnt += 1
    if cnt >= 4:
        break
    