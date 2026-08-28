# -*- coding: utf-8 -*-
import os, glob

# 1) Trouver le fichier HTML du module Prévisions & Décaissements
cible = None
for f in glob.glob('modules/*.html'):
    try:
        t = open(f, encoding='utf-8').read()
    except Exception:
        continue
    if 'Prévisions & Décaissements' in t or 'Prévisions &amp; Décaissements' in t:
        cible = os.path.basename(f)
        break
print('📄 Fichier du module trouvé :', cible)

if not cible:
    print('❌ Aucun fichier trouvé — liste des modules :')
    for f in glob.glob('modules/*.html'):
        print('  ', os.path.basename(f))
else:
    p = 'modules/suivi.html'
    s = open(p, encoding='utf-8').read()
    anchor = '<button onclick="showView(\'financier\', this)">💰 Suivi financier</button>'
    btn = '    <button onclick="window.location.href=\'/modules/%s\'">📈 Prévisions & Décaissements</button>' % cible
    if ('/modules/%s' % cible) in s:
        print('ℹ️ Onglet déjà présent dans la sidebar')
    elif anchor in s:
        s = s.replace(anchor, anchor + '\n' + btn, 1)
        open(p, 'w', encoding='utf-8').write(s)
        print('✅ Onglet "Prévisions & Décaissements" ajouté dans la sidebar de /suivi')
    else:
        print('❌ Ancre sidebar introuvable')