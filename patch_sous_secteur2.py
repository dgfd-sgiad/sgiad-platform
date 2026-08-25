# -*- coding: utf-8 -*-
p = 'modules/banque_projets.html'
s = open(p, encoding='utf-8').read()

old = "if (secteur) {"
new = "if (secteur !== undefined) {"

if old in s:
    s = s.replace(old, new, 1)
    open(p, 'w', encoding='utf-8').write(s)
    print('✅ Écouteur corrigé : le sous-secteur se filtre même quand on vide le secteur')
else:
    print('❌ INTROUVABLE :', old)