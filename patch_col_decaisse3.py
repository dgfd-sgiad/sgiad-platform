# -*- coding: utf-8 -*-
import re
p = 'modules/suivi.html'
s = open(p, encoding='utf-8').read()
s = s.replace('\r\n', '\n')

# 1) En-tête : insérer <th>Décaissé %</th> entre Montant et Statut
pattern_head = r'(<th>Montant</th>)(<th>Statut</th>)'
new_head = r'\1<th style="text-align:right; font-size:9px;">Décaissé %</th>\2'
s2, n = re.subn(pattern_head, new_head, s, count=1)
if n == 1:
    s = s2
    print('✅ En-tête colonne "Décaissé %" ajouté')
else:
    print('❌ En-tête non trouvé')

# 2) renderTopProjets : ajouter la cellule taux_fin_cagd entre montant et statut
# Pattern flexible qui matche le contenu de la cellule montant
pattern_func = r"(p\[i\]\.montant_fcfa\)\+'<\/td>)(<td>'\+statutBadge\(p\[i\]\.statut\))"
new_func = r"\1<td>'+tauxBadge(p[i].taux_fin_cagd)+'</td>\2"
s2, n = re.subn(pattern_func, new_func, s, count=1)
if n == 1:
    s = s2
    print('✅ Cellule taux_fin_cagd ajoutée dans renderTopProjets')
else:
    print('❌ Fonction non trouvée')

# 3) colspan 5 → 6 dans top-projets
s2, n = re.subn(r"(id=['\"]top-projets['\"][^>]*>.*?colspan=[\"'])5([\"'])", r'\g<1>6\2', s, count=1, flags=re.DOTALL)
if n == 1:
    s = s2
    print('✅ colspan mis à jour')
else:
    print('ℹ️ colspan introuvable ou déjà à 6')

open(p, 'w', encoding='utf-8').write(s)
