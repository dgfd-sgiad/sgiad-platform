# -*- coding: utf-8 -*-
import re
s = open('api.py', encoding='utf-8').read()
pats = ['/api/accords-financiers', '/api/banque/parametres', '/api/banque/secteur_sous_secteur']
for p in pats:
    print('=' * 70)
    print('ROUTES CONTENANT :', p)
    for m in re.finditer(re.escape(p), s):
        start = s.rfind('@app.route', 0, m.start())
        nxt = s.find('@app.route', m.start() + 1)
        end = nxt if nxt != -1 else len(s)
        print(s[start:end][:1800])
        print('-' * 50)
        