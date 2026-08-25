# -*- coding: utf-8 -*-
p = 'modules/banque_projets.html'
s = open(p, encoding='utf-8').read()
s = s.replace('\r\n', '\n')

# 1) Compteur dynamique : appeler updateEncoursCount() dans applyFilters
if 'updateEncoursCount();' not in s:
    old = "function applyFilters() {\nconst rows = getFilteredProjets();\nrenderFilteredTable(rows);"
    if old in s:
        s = s.replace(old, old + "\nupdateEncoursCount();", 1)
        print('✅ Appel updateEncoursCount() ajouté dans applyFilters')
    else:
        old2 = "renderFilteredTable(rows);\nif (window.activePortfolio) {"
        if old2 in s:
            s = s.replace(old2, "renderFilteredTable(rows);\nupdateEncoursCount();\nif (window.activePortfolio) {", 1)
            print('✅ Appel updateEncoursCount() ajouté (méthode 2)')
        else:
            print('❌ applyFilters introuvable')
else:
    print('✅ Appel updateEncoursCount() déjà présent')

# 2) Années de référence étendues jusqu'aux années de clôture (2027 → 2031)
old = "sel.innerHTML = years.map(y => `<option value=\"${y}\">${y}</option>`).join('');"
new = "sel.innerHTML = [...new Set([...years, ...yearsCloture])].sort((a, b) => b - a).map(y => `<option value=\"${y}\">${y}</option>`).join('');"
if old in s:
    s = s.replace(old, new, 1)
    print('✅ Années étendues : signature + clôture (jusqu\'à 2031)')
else:
    print('ℹ️ Ligne années déjà modifiée')

# 3) Fonctions manquantes éventuelles
if 'function projetActifAnnee(' not in s:
    fn = """function projetActifAnnee(p, refYear) {
const premierJanvier = refYear + '-01-01';
const dProrog = frToIso(p['Nouvelle date de clôture'] || '');
const dCloture = frToIso(p['Date de clôture'] || '');
const ref = dProrog || dCloture;
if (ref) return ref >= premierJanvier;
const anneeClot = parseInt(p['Annee de cloture'], 10);
if (!isNaN(anneeClot)) return anneeClot >= refYear;
return true;
}
function projetActif(p) {"""
    s = s.replace('function projetActif(p) {', fn, 1)
    print('✅ projetActifAnnee ajoutée')

if 'function updateEncoursCount()' not in s:
    fn2 = """function updateEncoursCount() {
const el = getEl('encours-count');
if (!el) return;
const sel = getEl('filter-encours');
const saved = sel ? sel.value : '';
if (sel) sel.value = '';
const base = getFilteredProjets();
if (sel) sel.value = saved;
const refYear = parseInt(getEl('annee-reference')?.value, 10) || new Date().getFullYear();
el.textContent = base.filter(x => projetActifAnnee(x, refYear)).length.toLocaleString('fr-BJ');
}
async function importExcel() {"""
    s = s.replace('async function importExcel() {', fn2, 1)
    print('✅ updateEncoursCount ajoutée')

open(p, 'w', encoding='utf-8').write(s)
print('Terminé.')