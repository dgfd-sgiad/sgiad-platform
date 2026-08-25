# -*- coding: utf-8 -*-
import re
p = 'modules/banque_projets.html'
s = open(p, encoding='utf-8').read()
s = s.replace('\r\n', '\n')

ok = []

# 1) Supprimer la carte "📊 Statut"
s, n = re.subn(r'<div class="dashboard-card" style="padding:8px;">\s*<h4 style="font-size:11px; margin-bottom:4px;">📊 Statut</h4>\s*<div id="chart-statut"></div>\s*</div>', '', s, count=1)
ok.append(('carte Statut supprimée', n))

# 2) Remplacer la carte "📌 En cours vs Clôturés" par le panneau "🎯 Projets en cours"
NEW_CARD = """<div class="dashboard-card" style="padding:10px; grid-column:1/-1;">
<div style="display:flex; justify-content:space-between; align-items:center; gap:8px; flex-wrap:wrap;">
<h4 style="margin:0; font-size:12px; color:var(--primary-blue);">🎯 Projets en cours — <span id="encours-count" style="font-weight:800;">0</span> projet(s)</h4>
<div style="display:flex; gap:6px; align-items:center; flex-wrap:wrap;">
<select id="filter-encours" onchange="applyFilters()" style="padding:4px 6px; font-size:10px; border:1px solid #ced4da; border-radius:4px;">
<option value="">Tous (en cours + clôturés)</option>
<option value="encours" selected>Projets en cours uniquement</option>
<option value="clotures">Projets clôturés uniquement</option>
</select>
<select id="annee-reference" onchange="applyFilters()" title="Année de référence" style="padding:4px 6px; font-size:10px; border:1px solid #ced4da; border-radius:4px;"></select>
<button onclick="exportEncoursExcel()" style="padding:5px 10px; background:var(--secondary-green); color:#fff; border:none; border-radius:4px; cursor:pointer; font-size:10px; font-weight:700;">📥 Excel</button>
<button onclick="exportEncoursPDF()" style="padding:5px 10px; background:#d5251f; color:#fff; border:none; border-radius:4px; cursor:pointer; font-size:10px; font-weight:700;">📄 PDF</button>
</div>
</div>
<div style="font-size:9.5px; color:#666; margin-top:5px;">Un projet est « en cours » si sa clôture (prorogation incluse) est postérieure au 1ᵉʳ janvier de l'année de référence. Ce filtre se combine avec tous les autres ; les exports reprennent la liste des projets en cours filtrés.</div>
</div>"""
s, n = re.subn(r'<div class="dashboard-card" style="padding:8px;">\s*<div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:4px;">\s*<h4 style="margin:0; font-size:11px;">📌 En cours vs Clôturés</h4>\s*<select id="annee-reference" onchange="updateStats\(\)" style="padding:2px 5px; font-size:10px;"></select>\s*</div>\s*<div id="chart-encours"></div>\s*</div>', NEW_CARD, s, count=1)
ok.append(('carte En cours vs Clôturés remplacée', n))

# 3) Fonction projetActifAnnee (avant projetActif)
FN_ACTIF = """function projetActifAnnee(p, refYear) {
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
s, n = re.subn(r'function projetActif\(p\) \{', FN_ACTIF, s, count=1)
ok.append(('fonction projetActifAnnee ajoutée', n))

# 4) Intégrer le filtre en cours dans getFilteredProjets
OLD_RET = "return matchTexte && matchSecteur && matchSousSecteur && matchPtf && matchStatut && matchApd &&"
NEW_RET = """const encoursSel = getEl('filter-encours')?.value || '';
const refYearEnc = parseInt(getEl('annee-reference')?.value, 10) || new Date().getFullYear();
const matchEncours = !encoursSel || (encoursSel === 'encours' ? projetActifAnnee(p, refYearEnc) : !projetActifAnnee(p, refYearEnc));
return matchTexte && matchSecteur && matchSousSecteur && matchPtf && matchStatut && matchApd &&"""
s, n = re.subn(re.escape(OLD_RET), NEW_RET, s, count=1)
ok.append(('filtre encours dans getFilteredProjets', n))
s, n = re.subn(r'matchTypeFinancement && matchTypeContributeur && matchModalite && matchNature && matchTutelle && matchAnnee && matchAnneeCloture && matchZone;',
               'matchTypeFinancement && matchTypeContributeur && matchModalite && matchNature && matchTutelle && matchAnnee && matchAnneeCloture && matchZone && matchEncours;', s, count=1)
ok.append(('matchEncours ajouté au return', n))

# 5) Compteur de projets en cours dans applyFilters
s, n = re.subn(r'function applyFilters\(\) \{\nconst rows = getFilteredProjets\(\);\nrenderFilteredTable\(rows\);',
               'function applyFilters() {\nconst rows = getFilteredProjets();\nrenderFilteredTable(rows);\nupdateEncoursCount();', s, count=1)
ok.append(('updateEncoursCount appelé', n))

# 6) Fonctions updateEncoursCount + exports Excel/PDF (avant importExcel)
FN_EXPORT = """function updateEncoursCount() {
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
doc.text('Exporté le ' + new Date().toLocaleString('fr-FR') + ' — ' + rows.length + ' projet(s) — Montant total : ' + new Intl.NumberFormat('fr-FR').format(rows.reduce((t, x) => t + parseNum(x['Montant_Total_FCFA']), 0)) + ' FCFA', 10, 16);
doc.autoTable({
startY: 22,
head: [['Code', 'Objet de l\\'accord', 'Partenaire', 'Secteur', 'Sous-secteur', 'Montant total (FCFA)', 'Clôture']],
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
showToast(`✅ PDF généré : ${rows.length} projet(s)`, 'success');
}
async function importExcel() {"""
s, n = re.subn(r'async function importExcel\(\) \{', FN_EXPORT, s, count=1)
ok.append(('exports Excel/PDF ajoutés', n))

# 7) CDN jsPDF (avant localisation_selector)
s, n = re.subn(r'<script src="\.\./js/localisation_selector\.js"></script>',
               '<script src="https://cdnjs.cloudflare.com/ajax/libs/jspdf/2.5.1/jspdf.umd.min.js"></script>\n<script src="https://cdnjs.cloudflare.com/ajax/libs/jspdf-autotable/3.5.28/jspdf.plugin.autotable.min.js"></script>\n<script src="../js/localisation_selector.js"></script>', s, count=1)
ok.append(('CDN jsPDF ajoutés', n))

open(p, 'w', encoding='utf-8').write(s)
for label, n in ok:
    print(('✅ ' if n == 1 else '❌ ') + label + f' ({n}/1)')
    