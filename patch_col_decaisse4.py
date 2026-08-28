# -*- coding: utf-8 -*-
import re
p = 'modules/suivi.html'
s = open(p, encoding='utf-8').read()

pattern = r"(mds\(p\[i\]\.montant_fcfa\)\)+'</td>)(<td>'\+statutBadge\(p\[i\]\.statut\))"
new = r"\1<td>'+tauxBadge(p[i].taux_fin_cagd)+'</td>\2"
s2, n = re.subn(pattern, new, s, count=1)
if n == 1:
    open(p, 'w', encoding='utf-8').write(s2)
    print('✅ Cellule taux_fin_cagd ajoutée dans renderTopProjets')
else:
    print('❌ toujours non trouvé')