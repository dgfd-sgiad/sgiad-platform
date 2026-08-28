# -*- coding: utf-8 -*-
p = 'modules/prev_decaissements.html'
s = open(p, encoding='utf-8').read()

btn = '<button onclick="history.back()" title="Retour immédiat" style="position:fixed;bottom:20px;left:20px;z-index:99999;background:#0a2540;color:#fff;border:none;padding:10px 16px;border-radius:30px;font-size:12px;font-weight:700;cursor:pointer;box-shadow:0 4px 15px rgba(0,0,0,0.3);display:flex;align-items:center;gap:6px">↩️ Retour immédiat</button>'

if 'Retour immédiat' in s:
    print('ℹ️ Bouton déjà présent')
elif '</body>' in s:
    s = s.replace('</body>', btn + '\n</body>', 1)
    open(p, 'w', encoding='utf-8').write(s)
    print('✅ Bouton "Retour immédiat" ajouté à prev_decaissements.html')
else:
    print('❌ </body> introuvable')