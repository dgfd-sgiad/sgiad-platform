# -*- coding: utf-8 -*-
import re

p = 'modules/recap.html'
s = open(p, encoding='utf-8').read()

start = s.find('function chips(')
if start == -1:
    print('❌ function chips introuvable')
    raise SystemExit

m = re.search(r'\n\}(?=\s*\n)', s[start + 10:])
if m:
    end = start + 10 + m.end()
else:
    nxt = s.find('\nfunction ', start + 10)
    end = s.rfind('}', start, nxt) + 1

NEW = '''function chips(host, key, labels, cls){
const el = document.getElementById(host);
el.innerHTML = '';
labels.forEach((lb, i) => {
const b = document.createElement('button');
b.className = 'chip on' + (cls ? ' ' + (STCLS[i] || '') : '');
b.textContent = lb;
b.title = 'Clic : afficher uniquement · Re-clic : tout afficher';
b.onclick = () => {
const st = state[key];
const solo = st.size === 1 && st.has(i);
if (solo) { for (let j = 0; j < labels.length; j++) st.add(j); }
else { for (let j = 0; j < labels.length; j++) { if (j === i) st.add(j); else st.delete(j); } }
Array.from(el.children).forEach((btn, j) => { btn.classList.toggle('on', st.has(j)); btn.setAttribute('aria-pressed', String(st.has(j))); });
render();
};
el.appendChild(b);
});
}'''

s = s[:start] + NEW + s[end:]
open(p, 'w', encoding='utf-8').write(s)
print('✅ Chips en mode radio : clic = isoler · re-clic = tout')

# Cache serveur réduit (données toujours à jour)
sp = 'suivi.py'
t = open(sp, encoding='utf-8').read()
if "_RECAP_CACHE['t'] < 300" in t:
    t = t.replace("_RECAP_CACHE['t'] < 300", "_RECAP_CACHE['t'] < 60", 1)
    open(sp, 'w', encoding='utf-8').write(t)
    print('✅ Cache endpoint réduit à 60 s')