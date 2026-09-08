# -*- coding: utf-8 -*-
p = 'modules/recap.html'
s = open(p, encoding='utf-8').read()
ok = []

if 'data-v="recos"' not in s:
    print('❌ recap.html sans onglets → lance d\'abord : python gen_recap2.py')
    raise SystemExit

# Onglet Recommandations -> page dédiée recos.html (hook prioritaire)
hook = """<script>
document.addEventListener('click', function(e){
  var b = e.target.closest('[data-v="recos"]');
  if (b) { e.preventDefault(); e.stopImmediatePropagation(); window.location.href = '/modules/recos.html'; }
}, true);
</script>"""
if 'stopImmediatePropagation' not in s:
    s = s.replace('</body>', hook + '\n</body>', 1)
    ok.append('onglet Recommandations -> recos.html')

# Arriver depuis recos.html sur le bon onglet (?v=revues / ?v=partenaires)
if 'URLSearchParams' not in s:
    s = s.replace('init();', "init();\nsetTimeout(function(){var q=new URLSearchParams(location.search).get('v');if(q&&q!=='recos')switchView(q);},400);", 1)
    ok.append('support ?v=revues / ?v=partenaires')

open(p, 'w', encoding='utf-8').write(s)
for k in ok:
    print('✅', k)
print('\n🎯 Ctrl + F5 puis teste la boucle complète')
