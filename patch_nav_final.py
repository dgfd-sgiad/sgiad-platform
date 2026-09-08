# -*- coding: utf-8 -*-

# ---------- A) recos.html : câbler les 4 onglets du header ----------
p = 'modules/recos.html'
s = open(p, encoding='utf-8').read()
NAV = """<script>
/* navigation croisée : onglets du header recos -> recap */
document.querySelectorAll('nav.tabs .tab, nav .tab').forEach(function(t){
  var v = (t.textContent || '').trim();
  var url = null;
  if (v.indexOf('Tableau de bord') === 0) url = '/modules/recap.html';
  else if (v.indexOf('Projets') === 0) url = '/modules/recap.html?v=projets';
  else if (v.indexOf('Revues') === 0) url = '/modules/recap.html?v=revues';
  else if (v.indexOf('Partenaires') === 0) url = '/modules/recap.html?v=partenaires';
  if (url) { t.style.cursor = 'pointer'; t.onclick = function(){ window.location.href = url; }; }
});
</script>"""
if 'navigation croisée' not in s:
    s = s.replace('</body>', NAV + '\n</body>', 1)
    open(p, 'w', encoding='utf-8').write(s)
    print('✅ recos : onglets Tableau de bord / Projets / Revues / Partenaires câblés')
else:
    print('ℹ️ recos : déjà câblé')

# ---------- B) recap.html : gérer ?v= proprement (toutes versions) ----------
p2 = 'modules/recap.html'
s2 = open(p2, encoding='utf-8').read()

# 1) neutraliser l'ancien appel switchView non protégé (ReferenceError)
if 'if(q)switchView(q);' in s2:
    s2 = s2.replace('if(q)switchView(q);', "if(q&&typeof switchView==='function')switchView(q);", 1)
    print('✅ recap : ancien appel ?v= sécurisé')

# 2) gestion robuste de ?v= (switchView si présent, sinon scroll vers la section)
VH = """<script>
(function(){
  var q = new URLSearchParams(location.search).get('v');
  if (!q) return;
  setTimeout(function(){
    if (typeof switchView === 'function') { try { switchView(q); return; } catch(e){} }
    var ids = {projets:['view-projets','t-projets','t-proj'],
               revues:['view-revues','tl-revues'],
               partenaires:['view-partenaires','par-cards','par-rows']};
    var list = ids[q] || [];
    for (var i = 0; i < list.length; i++) {
      var el = document.getElementById(list[i]);
      if (el) { el.scrollIntoView({behavior:'smooth', block:'start'}); break; }
    }
  }, 500);
})();
</script>"""
if 'URLSearchParams(location.search).get' not in s2.split('navigation croisée')[0] and '?v= handler' not in s2:
    VH = VH.replace('(function(){', "/* ?v= handler */\n(function(){", 1)
    s2 = s2.replace('</body>', VH + '\n</body>', 1)
    open(p2, 'w', encoding='utf-8').write(s2)
    print('✅ recap : ?v= géré (onglet ou scroll selon la version)')
else:
    open(p2, 'w', encoding='utf-8').write(s2)
    print('ℹ️ recap : gestion ?v= déjà présente')

print('\n🎯 Ctrl + F5 sur /modules/recos.html puis teste les 4 onglets')
