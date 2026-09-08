# -*- coding: utf-8 -*-
p = 'modules/recap.html'
s = open(p, encoding='utf-8').read()
ok = []

if 'data-v="recos"' in s:
    # Version avec onglets (gen_recap2) : hook en phase capture, prioritaire
    hook = """<script>
document.addEventListener('click', function(e){
  var b = e.target.closest('[data-v="recos"]');
  if (b) { e.preventDefault(); e.stopImmediatePropagation(); window.location.href = '/modules/recos.html'; }
}, true);
</script>"""
    if 'stopImmediatePropagation' not in s:
        s = s.replace('</body>', hook + '\n</body>', 1)
        ok.append('hook capture : onglet Recommandations -> recos.html')
else:
    # Version ancienne (nav statique) : le span devient un lien
    old = '<span class="tab">☷ Recommandations</span>'
    new = '<span class="tab" style="cursor:pointer" onclick="window.location.href=\'/modules/recos.html\'">☷ Recommandations</span>'
    if old in s:
        s = s.replace(old, new, 1)
        ok.append('span Recommandations -> lien recos.html')
    else:
        print('❌ Onglet Recommandations introuvable dans recap.html')

open(p, 'w', encoding='utf-8').write(s)
for k in ok:
    print('✅', k)
print('\n🎯 Ctrl + F5 sur /modules/recap.html → clique ☷ Recommandations')
