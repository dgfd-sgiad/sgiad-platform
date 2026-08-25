# -*- coding: utf-8 -*-
p = 'modules/banque_projets.html'
s = open(p, encoding='utf-8').read()

block = """const encoursSel = getEl('filter-encours')?.value || '';
const refYearEnc = parseInt(getEl('annee-reference')?.value, 10) || new Date().getFullYear();
const matchEncours = !encoursSel || (encoursSel === 'encours' ? projetActifAnnee(p, refYearEnc) : !projetActifAnnee(p, refYearEnc));
"""

n = s.count(block)
print('Blocs trouvés :', n)
if n > 1:
    while s.count(block) > 1:
        if (block + block) in s:
            s = s.replace(block + block, block, 1)
        else:
            s = s.replace(block, '', 1)
    open(p, 'w', encoding='utf-8').write(s)
    print('✅ Doublon supprimé — fichier réparé')
else:
    print('ℹ️ Rien à faire')