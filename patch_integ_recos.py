# -*- coding: utf-8 -*-
import glob

# 1) Retrouver le fichier design Recommandations
cible = None
for f in glob.glob('modules/*.html') + glob.glob('*.html'):
    try:
        t = open(f, encoding='utf-8', errors='ignore').read()
    except Exception:
        continue
    if ('Recommandations et alertes' in t) or ('D.recos' in t):
        cible = f
        break

if not cible:
    print('❌ Fichier design Recommandations introuvable.')
    print('👉 Enregistre le contenu collé sous modules/recos.html puis relance ce script.')
    raise SystemExit
print('📄 Fichier recos trouvé :', cible)

s = open(cible, encoding='utf-8').read()
ok = []

# 2) Bouton Retour immédiat
if 'Retour immédiat' not in s:
    btn = '<button onclick="history.back()" title="Retour immédiat" style="position:fixed;bottom:20px;left:20px;z-index:99999;background:#0a2540;color:#fff;border:none;padding:10px 16px;border-radius:30px;font-size:12px;font-weight:700;cursor:pointer;box-shadow:0 4px 15px rgba(0,0,0,.3)">↩️ Retour immédiat</button>'
    s = s.replace('</body>', btn + '\n</body>', 1)
    ok.append('bouton Retour immédiat')

# 3) Onglets du header recos -> navigation vers le Récapitulatif
old_rev = '<div class="tab"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><use href="#i-cal"/></svg>Revues &amp; missions</div>'
new_rev = '<div class="tab" onclick="window.location.href=\'/modules/recap.html?v=revues\'" style="cursor:pointer"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><use href="#i-cal"/></svg>Revues &amp; missions</div>'
if old_rev in s:
    s = s.replace(old_rev, new_rev, 1); ok.append('onglet Revues & missions câblé')

old_par = '<div class="tab"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><use href="#i-users"/></svg>Partenaires</div>'
new_par = '<div class="tab" onclick="window.location.href=\'/modules/recap.html?v=partenaires\'" style="cursor:pointer"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><use href="#i-users"/></svg>Partenaires</div>'
if old_par in s:
    s = s.replace(old_par, new_par, 1); ok.append('onglet Partenaires câblé')

open(cible, 'w', encoding='utf-8').write(s)
for k in ok:
    print('✅ recos :', k)

# 4) recap.html : l'onglet Recommandations ouvre la page dédiée + support ?v=
p = 'modules/recap.html'
h = open(p, encoding='utf-8').read()
ok2 = []

old_click = "if(b){switchView(b.getAttribute('data-v'));return;}"
new_click = "if(b){const v=b.getAttribute('data-v');if(v==='recos'){window.location.href='/modules/recos.html';return;}switchView(v);return;}"
if old_click in h:
    h = h.replace(old_click, new_click, 1); ok2.append('onglet Recommandations -> /modules/recos.html')

if 'URLSearchParams' not in h:
    h = h.replace('init();', "init();\nsetTimeout(function(){var q=new URLSearchParams(location.search).get('v');if(q)switchView(q);},400);", 1)
    ok2.append('support ?v=revues / ?v=partenaires')

open(p, 'w', encoding='utf-8').write(h)
for k in ok2:
    print('✅ recap :', k)

print('\n🎯 Ctrl + F5 sur /modules/recap.html → clique ☷ Recommandations')