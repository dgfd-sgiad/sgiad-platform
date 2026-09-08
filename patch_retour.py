# -*- coding: utf-8 -*-
import os, re

# Page de repli si aucun historique (ouverture directe)
FALLBACK = {
    'modules/recap.html': '/suivi',
    'modules/recos.html': '/modules/recap.html',
    'modules/projets.html': '/modules/recap.html',
}

BTN_RE = re.compile(r'<button onclick="history\.back\(\)"([^>]*)>↩️ Retour immédiat</button>')

for p, fb in FALLBACK.items():
    if not os.path.exists(p):
        print('  (absent)', p)
        continue
    s = open(p, encoding='utf-8').read()
    onclick = "(history.length>1&&document.referrer)?history.back():location.href='" + fb + "'"
    new_btn = '<button onclick="' + onclick + '"\\1>↩️ Retour immédiat</button>'
    s2, n = BTN_RE.subn(new_btn, s)
    if n == 0:
        btn = ('<button onclick="' + onclick + '" title="Retour immédiat" '
               'style="position:fixed;bottom:20px;left:20px;z-index:99999;background:#0a2540;color:#fff;'
               'border:none;padding:10px 16px;border-radius:30px;font-size:12px;font-weight:700;'
               'cursor:pointer;box-shadow:0 4px 15px rgba(0,0,0,.3)">↩️ Retour immédiat</button>')
        s2 = s.replace('</body>', btn + '\n</body>', 1)
        print('  ✅ bouton ajouté :', p)
    else:
        print('  ✅ bouton corrigé :', p, '(', n, ')')
    open(p, 'w', encoding='utf-8').write(s2)

print('\n🎯 Ctrl + F5 puis teste le bouton sur chaque page')
