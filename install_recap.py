# -*- coding: utf-8 -*-
import glob

# 1) Retrouver le fichier design (le plus gros contenant les marqueurs)
cands = []
for f in glob.glob('*.html') + glob.glob('modules/*.html'):
    try:
        t = open(f, encoding='utf-8', errors='ignore').read()
    except Exception:
        continue
    if ('v-title' in t) or ('Fraunces' in t) or ('c-cum' in t):
        cands.append((f, len(t), t))

if not cands:
    print('AUCUN fichier design trouve dans modules/.')
    print('=> Enregistre le contenu colle sous modules/recap.html puis relance ce script.')
    raise SystemExit

f, L, s = max(cands, key=lambda x: x[1])
print('Fichier design :', f, '-', L, 'caracteres')

# 2) Validation d'integrite
checks = [
    ('balise </html>', '</html>' in s),
    ('function render', 'function render' in s),
    ('appel render();', 'render();' in s),
    ('echarts present', 'echarts' in s.lower()),
    ('donnees D = {', 'D = {' in s or 'cells' in s),
    ('conteneurs (#v-title,#figs,#c-cum)', all(x in s for x in ['v-title', 'figs', 'c-cum'])),
]
ok = True
for k, v in checks:
    print(('  [OK]   ' if v else '  [!!]   ') + k)
    ok = ok and v

# 3) Bouton Retour immediat (si absent)
if 'Retour immédiat' not in s:
    btn = '<button onclick="history.back()" title="Retour immédiat" style="position:fixed;bottom:20px;left:20px;z-index:99999;background:#0a2540;color:#fff;border:none;padding:10px 16px;border-radius:30px;font-size:12px;font-weight:700;cursor:pointer;box-shadow:0 4px 15px rgba(0,0,0,0.3)">↩️ Retour immédiat</button>'
    s = s.replace('</body>', btn + '\n</body>', 1)
    open(f, 'w', encoding='utf-8').write(s)
    print('  [OK]   bouton Retour immédiat ajouté')

# 4) Onglet dans la sidebar de suivi.html
sp = 'modules/suivi.html'
ss = open(sp, encoding='utf-8').read()
url = '/' + f.replace('\\', '/')
if url in ss:
    print('  [OK]   onglet déjà présent dans la sidebar')
else:
    anchor = '<button class="active" onclick="showView(\'dash\', this)">🏠 Tableau de bord</button>'
    if anchor in ss:
        ss = ss.replace(anchor, anchor + '\n    <button onclick="window.location.href=\'' + url + '\'">📊 Récapitulatif</button>', 1)
        open(sp, 'w', encoding='utf-8').write(ss)
        print('  [OK]   onglet "📊 Récapitulatif" ajouté dans la sidebar')
    else:
        print('  [!!]   ancre sidebar introuvable dans suivi.html')

print('\nTESTE : http://127.0.0.1:5000' + url)
if not ok:
    print('\n/!\\ Fichier INCOMPLET (copie tronquee) : colle-moi cette sortie,')
    print('    je te fournis la version RECONSTRUITE et fonctionnelle (ECharts via CDN).')
    