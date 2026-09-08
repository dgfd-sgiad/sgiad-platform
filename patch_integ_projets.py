# -*- coding: utf-8 -*-
import glob

# 1) Retrouver le fichier design Projets
cible = None
for f in glob.glob('modules/*.html') + glob.glob('*.html'):
    try:
        t = open(f, encoding='utf-8', errors='ignore').read()
    except Exception:
        continue
    if ('Onglet Projets' in t) or ('fiche projet' in t and 'D.projets' in t):
        cible = f
        break
if not cible:
    print('❌ Fichier design Projets introuvable.')
    print('👉 Enregistre le contenu collé sous modules/projets.html puis relance.')
    raise SystemExit
print('📄 Fichier projets trouvé :', cible)
s = open(cible, encoding='utf-8').read()
ok = []

# 2) Bouton Retour immédiat
if 'Retour immédiat' not in s:
    btn = '<button onclick="history.back()" title="Retour immédiat" style="position:fixed;bottom:20px;left:20px;z-index:99999;background:#0a2540;color:#fff;border:none;padding:10px 16px;border-radius:30px;font-size:12px;font-weight:700;cursor:pointer;box-shadow:0 4px 15px rgba(0,0,0,.3)">↩️ Retour immédiat</button>'
    s = s.replace('</body>', btn + '\n</body>', 1)
    ok.append('bouton Retour immédiat')

# 3) Onglets du header -> navigation croisée
NAV = """<script>
/* nav projets : croisement vers les autres modules */
document.querySelectorAll('nav.tabs .tab').forEach(function(t){
  var v = (t.textContent || '').trim(); var url = null;
  if (v.indexOf('Tableau de bord') === 0) url = '/modules/recap.html';
  else if (v.indexOf('Recommandations') === 0) url = '/modules/recos.html';
  else if (v.indexOf('Revues') === 0) url = '/modules/recap.html?v=revues';
  else if (v.indexOf('Partenaires') === 0) url = '/modules/recap.html?v=partenaires';
  if (url) { t.style.cursor = 'pointer'; t.addEventListener('click', function(){ window.location.href = url; }); }
});
</script>"""
if 'nav projets : croisement' not in s:
    s = s.replace('</body>', NAV + '\n</body>', 1)
    ok.append('onglets header câblés')

open(cible, 'w', encoding='utf-8').write(s)
for k in ok:
    print('✅ projets :', k)

# 4) Dans recap.html et recos.html : onglet Projets -> page dédiée
for p in ['modules/recap.html', 'modules/recos.html']:
    try:
        h = open(p, encoding='utf-8').read()
    except Exception:
        continue
    if 'projets.html' in h:
        print('ℹ️', p, 'déjà câblé vers projets.html')
        continue
    hook = """<script>
/* onglet Projets -> page dédiée */
document.querySelectorAll('nav .tab, nav.tabs .tab, #tabs .tab').forEach(function(t){
  var v = (t.textContent || '').trim();
  if (v.indexOf('Projets') >= 0) {
    t.style.cursor = 'pointer';
    t.addEventListener('click', function(e){
      e.preventDefault(); e.stopImmediatePropagation();
      window.location.href = '/modules/projets.html';
    }, true);
  }
});
</script>"""
    h = h.replace('</body>', hook + '\n</body>', 1)
    open(p, 'w', encoding='utf-8').write(h)
    print('✅', p, ': onglet Projets -> /modules/projets.html')

print('\n🎯 Ctrl + F5 sur /modules/projets.html puis teste la navigation croisée')
