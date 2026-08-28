# -*- coding: utf-8 -*-
import re
p = 'modules/suivi.html'
s = open(p, encoding='utf-8').read()

start = s.find('function renderTopProjets')
end = s.find('function bientot', start)
if start == -1 or end == -1:
    print('❌ fonction renderTopProjets introuvable')
    raise SystemExit

block = s[start:end]

# Insère la cellule Décaissé % juste avant la cellule Statut, DANS cette fonction seulement
new_block, n = re.subn(
    r"<td>'\+statutBadge\(p\[i\]\.statut\)",
    "<td>'+tauxBadge(p[i].taux_fin_cagd)+'</td><td>'+statutBadge(p[i].statut)",
    block, count=1)

if n == 1:
    s = s[:start] + new_block + s[end:]
    open(p, 'w', encoding='utf-8').write(s)
    print('✅ Cellule "Décaissé %" insérée dans renderTopProjets')
else:
    print('❌ Pattern non trouvé — voici le code réel de la fonction :')
    print(repr(block))