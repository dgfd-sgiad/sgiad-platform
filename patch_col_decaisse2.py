# -*- coding: utf-8 -*-
p = 'modules/suivi.html'
s = open(p, encoding='utf-8').read()
s = s.replace('\r\n', '\n')

# 1) En-tête : ajouter <th>Décaissé %</th> entre Montant et Statut
old_head = '<tr><th>Code</th><th>Projet</th><th>Partenaire</th><th>Montant</th><th>Statut</th></tr></thead><tbody id="top-projets"></tbody>'
new_head = '<tr><th>Code</th><th>Projet</th><th>Partenaire</th><th>Montant</th><th>Décaissé %</th><th>Statut</th></tr></thead><tbody id="top-projets"></tbody>'
if old_head in s:
    s = s.replace(old_head, new_head, 1)
    print('✅ En-tête colonne "Décaissé %" ajouté')
else:
    print('❌ En-tête non trouvé')

# 2) renderTopProjets : ajouter cellule taux_fin_cagd entre montant et statut
old_func = """html += '<tr><td><a href="#" onclick="ouvrirFiche(\\''+esc(p[i].code)+'\\');return false;" style="color:#1e5aa8;font-weight:700">'+esc(p[i].code)+'</a></td><td>'+esc(p[i].objet)+'</td><td>'+esc(p[i].partenaire)+'</td><td>'+fmtMds(mds(p[i].montant_fcfa))+'</td><td>'+statutBadge(p[i].statut)+'</td></tr>';"""
new_func = """html += '<tr><td><a href="#" onclick="ouvrirFiche(\\''+esc(p[i].code)+'\\');return false;" style="color:#1e5aa8;font-weight:700">'+esc(p[i].code)+'</a></td><td>'+esc(p[i].objet)+'</td><td>'+esc(p[i].partenaire)+'</td><td>'+fmtMds(mds(p[i].montant_fcfa))+'</td><td>'+tauxBadge(p[i].taux_fin_cagd)+'</td><td>'+statutBadge(p[i].statut)+'</td></tr>';"""
if old_func in s:
    s = s.replace(old_func, new_func, 1)
    print('✅ Cellule taux_fin_cagd ajoutée dans renderTopProjets')
else:
    print('❌ Fonction non trouvée')

# 3) colspan 5 → 6
old_empty = "document.getElementById('top-projets').innerHTML = html || '<tr><td colspan=\"5\" class=\"empty\">Aucun projet.</td></tr>';"
new_empty = "document.getElementById('top-projets').innerHTML = html || '<tr><td colspan=\"6\" class=\"empty\">Aucun projet.</td></tr>';"
if old_empty in s:
    s = s.replace(old_empty, new_empty, 1)
    print('✅ colspan mis à jour')
else:
    print('ℹ️ colspan déjà correct ou introuvable')

open(p, 'w', encoding='utf-8').write(s)
print('Terminé.')