# -*- coding: utf-8 -*-
p = 'modules/banque_projets.html'
s = open(p, encoding='utf-8').read()
old = '''<div style="font-size:9.5px; color:#666; margin-top:5px;">Un projet est « en cours » si sa clôture (prorogation incluse) est postérieure au 1ᵉʳ janvier de l'année de référence. Ce filtre se combine avec tous les autres ; les exports reprennent la liste des projets en cours filtrés.</div>'''
if old in s:
    s = s.replace(old, '')
    open(p, 'w', encoding='utf-8').write(s)
    print('✅ Texte supprimé')
else:
    print('❌ Texte introuvable (déjà absent ?)')
    