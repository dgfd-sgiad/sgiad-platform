# -*- coding: utf-8 -*-
p = 'modules/banque_projets.html'
s = open(p, encoding='utf-8').read()

repls = [
# 1) Coordination : index 5 -> 7
("if (i === 5) {", "if (i === 7) {"),
# 2) Maturité : index 6 -> 8
("} else if (i === 6) {", "} else if (i === 8) {"),
# 3) Localisation : index 1 -> 3 (sélecteur de zone + colonnes)
("""} else if (i === 1) {
html +=
`<div id="exp-loc-selector-container" style="background:#f8f9fa; padding:8px; border-radius:6px; border:1px solid #e9ecef;"></div>`;
} else {""",
"""} else if (i === 3) {
html += `<div id="exp-loc-selector-container" style="background:#f8f9fa; padding:8px; border-radius:6px; border:1px solid #e9ecef; margin-bottom:8px;"></div>`;
html += `<div style="border-top:1px dashed #eee; padding-top:8px;"><h5 style="font-size:10px; color:#666; margin:0 0 6px 0;">✅ Colonnes à exporter :</h5><div class="checkbox-grid">${fields.filter(k => k !== 'Zone').map(k => `<label><input type="checkbox" value="${k}" checked style="accent-color:var(--secondary-green);"> ${k}</label>`).join('')}</div></div>`;
} else {"""),
# 4) Filtres par année dans l'onglet Calendrier (4)
("if (i === 0 && fields.includes('Annee de signature')) yearFields.push('Annee de signature');",
 "if (i === 4 && fields.includes('Annee de signature')) yearFields.push('Annee de signature');"),
("if (i === 2 && fields.includes('Annee de cloture')) yearFields.push('Annee de cloture');",
 "if (i === 4 && fields.includes('Annee de cloture')) yearFields.push('Annee de cloture');"),
# 5) Plages de dates dans l'onglet Calendrier (4), clés réelles
("""const dateFields = [];
if (i === 2) {
dateFields.push('Date de signature', "Date d'approbation", 'Date de clôture', 'Date de mise en vigueur', 'Date de démarrage', 'Date de prorogation', 'Nouvelle date de clôture');
}""",
"""const dateFields = [];
if (i === 4) {
dateFields.push('Date de signature', "Date d'approbation", 'Date entree en vigueur', 'Date_Demarrage', 'Date de clôture', 'Nouvelle date de clôture');
}"""),
# 6) Initialisation du sélecteur de zone à l'onglet 3
("if (index === 1 && !exportLocSelectorReady) {", "if (index === 3 && !exportLocSelectorReady) {"),
# 7) Filtres dates (clés réelles) dans getCurrentExportFilters
("""const dateFields = ['Date de signature', "Date d'approbation", 'Date de clôture', 'Date de mise en vigueur', 'Date de démarrage', 'Date de prorogation', 'Nouvelle date de clôture'];""",
"""const dateFields = ['Date de signature', "Date d'approbation", 'Date entree en vigueur', 'Date_Demarrage', 'Date de clôture', 'Nouvelle date de clôture'];"""),
]

ok = 0
for old, new in repls:
    if old in s:
        s = s.replace(old, new, 1)
        ok += 1
        print('✅', old[:55].replace('\n', ' '))
    else:
        print('❌ INTROUVABLE :', old[:55].replace('\n', ' '))

open(p, 'w', encoding='utf-8').write(s)
print(f'Terminé : {ok}/{len(repls)} remplacements appliqués.')