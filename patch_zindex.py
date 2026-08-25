# -*- coding: utf-8 -*-
p = 'modules/banque_projets.html'
s = open(p, encoding='utf-8').read()

repls = [
# 1) Confiner la carte Leaflet (ses z-index ne fuient plus au-dessus des modales)
("height: 400px;", "height: 400px; position: relative; z-index: 1;"),
# 2) Modale formulaire AU-DESSUS de tout (1200)
("z-index:200;", "z-index:1200;"),
# 3) Gestion des valeurs au-dessus de la modale (1400)
("z-index:300;", "z-index:1400;"),
# 4) Modale fiche projet au-dessus (1500)
("z-index:350;", "z-index:1500;"),
]

ok = 0
for old, new in repls:
    if old in s:
        s = s.replace(old, new, 1)
        ok += 1
        print('✅', old)
    else:
        print('❌ INTROUVABLE :', old)

open(p, 'w', encoding='utf-8').write(s)
print(f'Terminé : {ok}/{len(repls)} remplacements appliqués.')