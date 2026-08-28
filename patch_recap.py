# -*- coding: utf-8 -*-
import glob

marker = 'id="c-cum"'
cible = None
for f in glob.glob('modules/*.html'):
    t = open(f, encoding='utf-8').read()
    if marker in t and 'Fraunces' in t:
        cible = f
        break

if not cible:
    print('❌ Fichier du nouveau dashboard introuvable dans modules/.')
    print('👉 Enregistre le contenu collé sous modules/previsions.html puis relance ce script.')
    raise SystemExit

print('📄 Cible :', cible)
s = open(cible, encoding='utf-8').read()
s = s.replace('\r\n', '\n')
ok = []

# 1) CSS du bandeau récapitulatif
CSS = """
/* - recap haut - */
.recap{display:grid;grid-template-columns:repeat(6,1fr);gap:14px;margin:18px 0 4px}
.rtile{background:var(--paper);border:1px solid var(--line);border-radius:var(--radius);padding:13px 15px 12px;box-shadow:var(--shadow);min-width:0}
.rtile .lb{font-size:10.5px;letter-spacing:.07em;text-transform:uppercase;color:var(--ink-3);font-weight:600}
.rtile .vl{font-family:'Fraunces',Georgia,serif;font-size:21px;font-weight:600;margin-top:4px;letter-spacing:-.02em;font-variant-numeric:tabular-nums;color:var(--ink)}
.rtile .vl small{font-size:11px;font-family:'Archivo',sans-serif;color:var(--ink-3);font-weight:500;margin-left:3px}
.rtile .dt{font-size:11px;color:var(--ink-3);margin-top:3px}
.rtile.hl .vl{color:var(--dec)}
.rtile .gauge{height:4px;border-radius:2px;background:var(--solde);margin-top:8px;position:relative;overflow:hidden}
.rtile .gauge i{position:absolute;inset:0 auto 0 0;background:var(--dec);border-radius:2px}
@media (max-width:1000px){.recap{grid-template-columns:repeat(3,1fr)}}
@media (max-width:620px){.recap{grid-template-columns:1fr 1fr}}
"""
if '.recap{' not in s:
    s = s.replace('</style>', CSS + '</style>', 1)
    ok.append('CSS récap ajouté')

# 2) Emplacement en haut du <main>
old_html = '<main class="wrap"><section class="verdict">'
new_html = '<main class="wrap"><section class="recap" id="recap" aria-label="Récapitulatif"></section><section class="verdict">'
if 'id="recap"' not in s and old_html in s:
    s = s.replace(old_html, new_html, 1)
    ok.append('Emplacement haut de page ajouté')

# 3) Fonction recap + appel dans render()
FN = """function recap(a){
const ris = a.st[2] || {n:0}, vig = a.st[1] || {n:0};
const tiles = [
['Projets retenus', NB0.format(a.n), a.full ? 'portefeuille complet' : 'périmètre filtré', ''],
['Prévision ' + D.exercice, f1(a.prev), 'Mds FCFA programmés', ''],
['Décaissé', f1(a.dec), 'Mds FCFA versés', 'hl'],
['Taux de réalisation', pc(a.taux), 'de la prévision annuelle', 'gauge'],
['Solde à décaisser', f1(a.solde), 'Mds FCFA restants', ''],
['Risques', NB0.format(ris.n) + ' · ' + NB0.format(vig.n), 'en difficulté · à surveiller', '']
];
document.getElementById('recap').innerHTML = tiles.map(t =>
'<div class="rtile' + (t[3]==='hl' ? ' hl' : '') + '"><div class="lb">' + t[0] + '</div><div class="vl">' + t[1] + '</div>' +
(t[3]==='gauge' ? '<div class="gauge"><i style="width:' + Math.min(100, a.taux) + '%"></i></div>' : '') +
'<div class="dt">' + t[2] + '</div></div>').join('');
}
function render(){"""
if 'function recap(a)' not in s:
    s = s.replace('function render(){', FN, 1)
    ok.append('Fonction recap() ajoutée')

if 'recap(a); figs(a);' not in s and 'figs(a); verdict(a);' in s:
    s = s.replace('figs(a); verdict(a);', 'recap(a); figs(a); verdict(a);', 1)
    ok.append('Appel recap(a) inséré dans render()')

open(cible, 'w', encoding='utf-8').write(s)
for k in ok:
    print('✅', k)
print('Terminé.')