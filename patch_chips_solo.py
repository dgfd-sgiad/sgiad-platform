# -*- coding: utf-8 -*-
p = 'modules/recap.html'
s = open(p, encoding='utf-8').read()

anchor = "b.setAttribute('aria-pressed', 'true');"
add = """b.setAttribute('aria-pressed', 'true');
b.title = 'Clic : inclure/exclure · Double-clic : isoler';
b.ondblclick = (ev) => { ev.preventDefault(); const s2 = state[key]; const solo = s2.size === 1 && s2.has(i); if (solo) { labels.forEach((_, j) => s2.add(j)); } else { labels.forEach((_, j) => { if (j === i) s2.add(j); else s2.delete(j); }); } Array.from(el.children).forEach((btn, j) => { btn.classList.toggle('on', s2.has(j)); btn.setAttribute('aria-pressed', String(s2.has(j))); }); render(); };"""

if 'ondblclick' in s:
    print('ℹ️ Double-clic déjà présent')
elif anchor in s:
    s = s.replace(anchor, add, 1)
    open(p, 'w', encoding='utf-8').write(s)
    print('✅ Double-clic = isoler (secteur / partenaire / statut)')
else:
    print('❌ Ancre introuvable')
    