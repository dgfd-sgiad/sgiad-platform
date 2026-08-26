# -*- coding: utf-8 -*-
import re
p = 'modules/banque_projets.html'
s = open(p, encoding='utf-8').read()
s = s.replace('\r\n', '\n')

print('--- DIAGNOSTIC INITIAL ---')
print('HTML encours-count :', 'id="encours-count"' in s)
print('HTML filter-encours :', 'id="filter-encours"' in s)
print('projetActifAnnee :', 'function projetActifAnnee(' in s)
print('updateEncoursCount def :', 'function updateEncoursCount()' in s)
print('appel updateEncoursCount :', 'updateEncoursCount();' in s)
print('bloc matchEncours :', "const encoursSel = getEl('filter-encours')" in s)
print('return matchEncours :', '&& matchEncours;' in s)
print('annees union :', '[...new Set([...years, ...yearsCloture])]' in s)

# 1) Supprimer les DOUBLONS du bloc const (SyntaxError)
block = """const encoursSel = getEl('filter-encours')?.value || '';
const refYearEnc = parseInt(getEl('annee-reference')?.value, 10) || new Date().getFullYear();
const matchEncours = !encoursSel || (encoursSel === 'encours' ? projetActifAnnee(p, refYearEnc) : !projetActifAnnee(p, refYearEnc));
"""
n = s.count(block)
if n > 1:
    while s.count(block) > 1:
        if (block + block) in s:
            s = s.replace(block + block, block, 1)
        else:
            s = s.replace(block, '', 1)
    print('✅ Doublons supprimés (1 seul bloc reste)')
elif n == 0:
    oldret = "return matchTexte && matchSecteur && matchSousSecteur && matchPtf && matchStatut && matchApd &&"
    if oldret in s:
        s = s.replace(oldret, block + oldret, 1)
        print('✅ Bloc matchEncours inséré')
else:
    print('✅ Bloc const présent (1)')

# 2) return ... && matchEncours
if '&& matchEncours;' not in s:
    tail = 'matchTypeFinancement && matchTypeContributeur && matchModalite && matchNature && matchTutelle && matchAnnee && matchAnneeCloture && matchZone;'
    if tail in s:
        s = s.replace(tail, tail.replace(';', ' && matchEncours;'), 1)
        print('✅ matchEncours ajouté au return')
else:
    print('✅ return matchEncours présent')

# 3) appel updateEncoursCount dans applyFilters
if 'updateEncoursCount();' not in s:
    anchor = "function applyFilters() {\nconst rows = getFilteredProjets();\nrenderFilteredTable(rows);"
    if anchor in s:
        s = s.replace(anchor, anchor + "\nupdateEncoursCount();", 1)
        print('✅ Appel updateEncoursCount ajouté')
else:
    print('✅ Appel updateEncoursCount présent')

# 4) fonctions manquantes
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
function getRowsEnCours() {
const sel = getEl('filter-encours');
const saved = sel ? sel.value : '';
if (sel) sel.value = 'encours';
const rows = getFilteredProjets();
if (sel) sel.value = saved;
return rows;
}
async function exportEncoursExcel() {
const rows = getRowsEnCours();
if (!rows.length) { showToast('Aucun projet en cours avec ces filtres', 'error'); return; }
const codes = rows.map(x => x['Code Projet']).filter(Boolean);
try {
const res = await fetch(`${API_BASE}/export`, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ filters: { 'Code Projet': codes }, selected_columns: [] }) });
if (!res.ok) throw new Error(`Le serveur a répondu : ${res.status}`);
const blob = await res.blob();
const url = URL.createObjectURL(blob);
const a = document.createElement('a'); a.href = url; a.download = `Projets_en_cours_${Date.now()}.xlsx`;
document.body.appendChild(a); a.click(); document.body.removeChild(a); URL.revokeObjectURL(url);
showToast(`✅ ${rows.length} projet(s) en cours exporté(s)`, 'success');
} catch (e) { showToast('Erreur export : ' + e.message, 'error'); }
}
function exportEncoursPDF() {
const rows = getRowsEnCours();
if (!rows.length) { showToast('Aucun projet en cours avec ces filtres', 'error'); return; }
const refYear = parseInt(getEl('annee-reference')?.value, 10) || new Date().getFullYear();
const doc = new jspdf.jsPDF({ orientation: 'landscape', unit: 'mm', format: 'a4' });
doc.setFontSize(13);
doc.text('SGIAD — Projets en cours (' + refYear + ')', 10, 10);
doc.setFontSize(9); doc.setTextColor(100);
doc.text('Exporté le ' + new Date().toLocaleString('fr-FR') + ' — ' + rows.length + ' projet(s)', 10, 16);
doc.autoTable({
startY: 22,
head: [['Code', 'Objet', 'Partenaire', 'Secteur', 'Sous-secteur', 'Montant (FCFA)', 'Clôture']],
body: rows.map(x => [
x['Code Projet'] || '',
x["Objet de l'accord"] || '',
x['Partenaire'] || '',
x[window._secteurKey || 'Secteur principal'] || '',
x[window._sousSecteurKey || 'SOUS SECTEUR'] || '',
x['Montant_Total_FCFA'] ? new Intl.NumberFormat('fr-FR').format(parseNum(x['Montant_Total_FCFA'])) : '',
x['Nouvelle date de clôture'] || x['Date de clôture'] || ''
]),
styles: { fontSize: 7.5 },
headStyles: { fillColor: [15, 76, 129] }
});
doc.save('projets_en_cours_' + refYear + '.pdf');
}
async function importExcel() {"""
    s = s.replace('async function importExcel() {', fn2, 1)
    print('✅ updateEncoursCount + exports ajoutés')

# 5) années étendues (union signature + clôture)
oldy = "sel.innerHTML = years.map(y => `<option value=\"${y}\">${y}</option>`).join('');"
newy = "sel.innerHTML = [...new Set([...years, ...yearsCloture])].sort((a, b) => b - a).map(y => `<option value=\"${y}\">${y}</option>`).join('');"
if oldy in s:
    s = s.replace(oldy, newy, 1)
    print('✅ Années étendues jusqu\'aux clôtures')
else:
    print('✅ Années déjà étendues')

# 6) CDN jsPDF si nécessaire
if 'function exportEncoursPDF()' in s and 'jspdf.umd.min.js' not in s:
    s = s.replace('<script src="../js/localisation_selector.js"></script>',
                  '<script src="https://cdnjs.cloudflare.com/ajax/libs/jspdf/2.5.1/jspdf.umd.min.js"></script>\n<script src="https://cdnjs.cloudflare.com/ajax/libs/jspdf-autotable/3.5.28/jspdf.plugin.autotable.min.js"></script>\n<script src="../js/localisation_selector.js"></script>', 1)
    print('✅ CDN jsPDF ajoutés')

open(p, 'w', encoding='utf-8').write(s)
print('--- TERMINÉ : fichier réécrit ---')