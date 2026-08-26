# -*- coding: utf-8 -*-
import re
p = 'modules/suivi.html'
s = open(p, encoding='utf-8').read()
s = s.replace('\r\n', '\n')

# Cherche dans le <thead> du tableau "Principaux projets" la cellule "Montant FCFA"
# et ajoute juste après "Décaissé %"
m = re.search(r'(<th[^>]*>\s*Montant FCFA\s*</th>)', s)
if m:
    s = s.replace(m.group(1), m.group(1) + '\n<th style="text-align:right; font-size:11px;">Décaissé %</th>', 1)
    print('✅ En-tête colonne ajouté')
else:
    print('⚠️ En-tête non trouvé')

# Cherche la cellule <td> qui affiche le montant et ajoute la cellule taux juste après
# Pattern typique : new Intl.NumberFormat('fr-FR').format(projet.montant_fcfa || 0)
patterns = [
    (r"(new Intl\.NumberFormat\('fr-FR'\)\.format\(projet\.montant_fcfa \|\| 0\))",
     r"\1</td>\n<td style='text-align:right; font-size:11px;'>{pct}</td>".format(pct="${projet.taux_fin_cagd != null ? projet.taux_fin_cagd.toFixed(1) + '%' : '—'}")),
    (r"projet\.montant_fcfa \? new Intl\.NumberFormat\('fr-FR'\)\.format\(projet\.montant_fcfa\) : '—'",
     r"projet.montant_fcfa ? new Intl.NumberFormat('fr-FR').format(projet.montant_fcfa) : '—'</td>\n<td style='text-align:right; font-size:11px;'>{pct}</td>".format(pct="${projet.taux_fin_cagd != null ? projet.taux_fin_cagd.toFixed(1) + '%' : '—'}"))
]

done = False
for pat, repl in patterns:
    if re.search(pat, s):
        s = re.sub(pat, repl, s, count=1)
        print('✅ Cellule taux ajoutée dans le tableau')
        done = True
        break

if not done:
    print('⚠️ Pattern cellule non trouvé, essaie Ctrl+H manuel')

open(p, 'w', encoding='utf-8').write(s)
