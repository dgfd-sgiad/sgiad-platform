# -*- coding: utf-8 -*-
p = 'modules/banque_projets.html'
s = open(p, encoding='utf-8').read()
s = s.replace('\r\n', '\n')

repls = [
# 1) Onglet Localisation : index 1 -> 3
("} else if (i === 1) {", "} else if (i === 3) {"),
# 2) Le conteneur de zone affiche AUSSI les colonnes Dept/Commune/Niveau
("`<div id=\"exp-loc-selector-container\" style=\"background:#f8f9fa; padding:8px; border-radius:6px; border:1px solid #e9ecef;\"></div>`;",
 "`<div id=\"exp-loc-selector-container\" style=\"background:#f8f9fa; padding:8px; border-radius:6px; border:1px solid #e9ecef; margin-bottom:8px;\"></div>` +\n`<div style=\"border-top:1px dashed #eee; padding-top:8px;\"><h5 style=\"font-size:10px; color:#666; margin:0 0 6px 0;\">✅ Colonnes à exporter :</h5><div class=\"checkbox-grid\">${fields.filter(k => k !== 'Zone').map(k => `<label><input type=\"checkbox\" value=\"${k}\" checked style=\"accent-color:var(--secondary-green);\"> ${k}</label>`).join('')}</div></div>`;"),
# 3) Filtres dates dans l'onglet Calendrier (4)
("if (i === 2) {", "if (i === 4) {"),
# 4) Clés de dates réelles
("dateFields.push('Date de signature', \"Date d'approbation\", 'Date de clôture', 'Date de mise en vigueur', 'Date de démarrage', 'Date de prorogation', 'Nouvelle date de clôture');",
 "dateFields.push('Date de signature', \"Date d'approbation\", 'Date entree en vigueur', 'Date_Demarrage', 'Date de clôture', 'Nouvelle date de clôture');"),
]

ok = 0
for old, new in repls:
    if old in s:
        s = s.replace(old, new, 1)
        ok += 1
        print('✅', old[:60].replace('\n', ' '))
    else:
        print('❌ INTROUVABLE :', old[:60].replace('\n', ' '))

open(p, 'w', encoding='utf-8').write(s)
print(f'Terminé : {ok}/{len(repls)} remplacements appliqués.')