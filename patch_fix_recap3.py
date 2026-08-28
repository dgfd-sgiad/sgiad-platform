# -*- coding: utf-8 -*-
p = 'modules/recap.html'
s = open(p, encoding='utf-8').read()

rep = [
    # 1) Secteurs normalisés (fusion des doublons majuscules/minuscules)
    ("var sg=a.secteur_principal||'Non précisé';",
     "var sg=String(a.secteur_principal||'NON PRÉCISÉ').trim().toUpperCase();",
     'secteurs normalisés (doublons fusionnés)'),
    # 2) Périmètre : projets en cours signés 2021-2026
    ("if(ref&&ref<'2026-01-01')return;",
     "if(ref&&ref<'2026-01-01')return;var an=+a.annee_signature||0;if(an&&(an<2021||an>2026))return;",
     'périmètre limité aux signatures 2021-2026'),
    # 3) Index secteur normalisé dans les cells
    ("s:_secIdx[a.secteur_principal||'Non précisé']",
     "s:_secIdx[String(a.secteur_principal||'NON PRÉCISÉ').trim().toUpperCase()]",
     'index secteur cohérent'),
    # 4) Garde-fou recap() : plus de crash si conteneur absent
    ("document.getElementById('recap').innerHTML = tiles.map",
     "var _rc=document.getElementById('recap');if(_rc)_rc.innerHTML = tiles.map",
     'garde-fou recap (débloque KPIs + verdict + graphiques)'),
]

for old, new, label in rep:
    if old in s:
        s = s.replace(old, new, 1)
        print('✅', label)
    else:
        print('❌ introuvable :', label)

open(p, 'w', encoding='utf-8').write(s)
print('\n🎯 Ctrl + F5 sur http://127.0.0.1:5000/modules/recap.html')
