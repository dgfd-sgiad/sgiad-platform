# -*- coding: utf-8 -*-
import re
p = 'modules/banque_projets.html'
s = open(p, encoding='utf-8').read()

new_func = """async function updateSousSecteurFilterForSecteur(secteur) {
const ssKey = window._sousSecteurKey || 'SOUS SECTEUR';
const ssSelect = document.querySelector(`#form-projet select[data-field-key="${ssKey}"]`);
if (!ssSelect) return;
const currentVal = ssSelect.value;
if (!secteur) {
const col0 = COLUMNS_BY_KEY[ssKey];
ssSelect.innerHTML = '<option value="">-- Sélectionner --</option>' + (col0?.options || []).slice().sort().map(o => `<option value="${o}">${o}</option>`).join('');
ssSelect.value = '';
return;
}
let sousSecteurs = [];
try {
const res = await fetchWithRetry(`${window.location.origin}/api/banque/secteur_sous_secteur/by_secteur?secteur=${encodeURIComponent(secteur)}`);
if (res.ok) {
const data = await res.json();
if (Array.isArray(data)) sousSecteurs = data;
}
} catch (e) { console.warn('Liens secteur/sous-secteur indisponibles — repli sur les projets existants'); }
if (sousSecteurs.length === 0) {
const sKey = window._secteurKey || 'Secteur principal';
sousSecteurs = [...new Set(allProjets.filter(x => String(x[sKey] || '').trim() === secteur).map(x => String(x[ssKey] || '').trim()).filter(Boolean))];
}
const col = COLUMNS_BY_KEY[ssKey];
const finalOptions = (sousSecteurs.length > 0 ? sousSecteurs : (col?.options || [])).slice().sort();
ssSelect.innerHTML = '<option value="">-- Sélectionner --</option>' + finalOptions.map(o => `<option value="${o}">${o}</option>`).join('');
if (finalOptions.includes(currentVal)) ssSelect.value = currentVal; else ssSelect.value = '';
}
// Listen for secteur changes in the form to update sous-secteur dropdown"""

s, n1 = re.subn(r"async function updateSousSecteurFilterForSecteur\(secteur\) \{.*?// Listen for secteur changes",
                lambda m: new_func, s, count=1, flags=re.S)

s, n2 = re.subn(r"if \(e\.target\.matches\('#form-projet select\[data-field-key=\"Secteur principal\"\]'\)\) \{\s*const secteur = e\.target\.value;\s*if \(secteur\) \{\s*updateSousSecteurFilterForSecteur\(secteur\);\s*\}\s*\}",
                """if (e.target.matches('#form-projet select[data-field-key="Secteur principal"]')) {
updateSousSecteurFilterForSecteur(e.target.value);
}""", s, count=1)

open(p, 'w', encoding='utf-8').write(s)
print(f'✅ Fonction remplacée : {n1}/1 · Écouteur simplifié : {n2}/1')