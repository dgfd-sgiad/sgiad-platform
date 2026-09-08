# -*- coding: utf-8 -*-
import re

p = 'modules/recos.html'
s = open(p, encoding='utf-8').read()

# 1) Supprimer les anciens scripts de câblage (navigation croisée / nav recos v1-v3)
s = re.sub(r'<script>\s*/\* navigation croisée[\s\S]*?</script>\n?', '', s)
s = re.sub(r'<script>\s*/\* nav recos : Tableau de bord[\s\S]*?</script>\n?', '', s)
print('✅ anciens scripts de câblage supprimés')

# 2) Supprimer les onclick inline posés sur Revues & Partenaires
s = s.replace(" onclick=\"window.location.href='/modules/recap.html?v=revues'\"", '')
s = s.replace(" onclick=\"window.location.href='/modules/recap.html?v=partenaires'\"", '')
s = re.sub(r'(<div class="tab") style="cursor:pointer"(>)', r'\1\2', s)
print('✅ onclick inline Revues/Partenaires retirés')

# 3) Nouveau câblage propre : Tableau de bord actif, Revues/Partenaires inactifs
NAV = """<script>
/* nav recos v4 : Tableau de bord actif ; Revues & Partenaires inactifs */
document.querySelectorAll('nav.tabs .tab').forEach(function(t){
  var txt = (t.textContent || '').trim();
  var actif = txt.indexOf('Tableau de bord') === 0 || txt.indexOf('Projets') === 0;
  var vide  = txt.indexOf('Revues') === 0 || txt.indexOf('Partenaires') === 0;
  if (vide) {
    t.style.cursor = 'default';
    t.style.opacity = '0.55';
    t.title = 'Module en construction — bientôt disponible';
  } else if (actif) {
    t.style.cursor = 'pointer';
  }
  t.addEventListener('click', function(e){
    if (txt.indexOf('Tableau de bord') === 0) { window.location.href = '/modules/recap.html'; }
    else if (txt.indexOf('Projets') === 0) { window.location.href = '/modules/recap.html?v=projets'; }
    else if (vide) { e.preventDefault(); e.stopImmediatePropagation(); }
  }, true);
});
</script>"""

if 'nav recos v4' not in s:
    s = s.replace('</body>', NAV + '\n</body>', 1)
    print('✅ câblage v4 posé')

open(p, 'w', encoding='utf-8').write(s)
print('\n🎯 Ctrl + F5 sur /modules/recos.html')