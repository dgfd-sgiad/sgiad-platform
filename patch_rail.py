# -*- coding: utf-8 -*-

# ---------- A) suivi.py : l'endpoint renvoie aussi la liste des projets ----------
p = 'suivi.py'
s = open(p, encoding='utf-8').read()
ok = []

old1 = ".select('objet_accord, partenaire, secteur_principal, montant_total_fcfa, statut, date_cloture, nouvelle_date_cloture')"
new1 = ".select('code_projet, objet_accord, partenaire, secteur_principal, montant_total_fcfa, statut, date_cloture, nouvelle_date_cloture')"
if old1 in s:
    s = s.replace(old1, new1, 1); ok.append('select + code_projet')

old2 = "secteurs, sec_idx, cells, nproj = [], {}, {}, 0"
new2 = old2 + "\n    projets_out = []"
if old2 in s and 'projets_out = []' not in s:
    s = s.replace(old2, new2, 1); ok.append('init projets_out')

old3 = "cc['prev'] += prev; cc['dec'] += dec; cc['n'] += 1"
new3 = old3 + """
        projets_out.append({'code': a.get('code_projet'), 'nom': (a.get('objet_accord') or '')[:90],
                            's': sec_idx[sg], 'p': _pidx(a.get('partenaire')), 't': t,
                            'prev': round(prev, 2), 'dec': round(dec, 2), 'fin': ref})"""
if old3 in s and 'projets_out.append' not in s:
    s = s.replace(old3, new3, 1); ok.append('append projet')

old4 = "'exercice': '2026', 'situation': '28 août 2026', 'part_t3': 2 / 3,"
new4 = "'projets': projets_out,\n        'exercice': '2026', 'situation': '28 août 2026', 'part_t3': 2 / 3,"
if old4 in s and "'projets': projets_out" not in s:
    s = s.replace(old4, new4, 1); ok.append('champ projets dans out')

open(p, 'w', encoding='utf-8').write(s)
for k in ok:
    print('✅ suivi.py :', k)

# ---------- B) recap.html : panneau vertical droit ----------
h = open('modules/recap.html', encoding='utf-8').read()
ok2 = []

CSS = """
#rail{position:fixed;top:0;right:0;bottom:0;width:292px;background:#fff;border-left:1px solid var(--line);box-shadow:-6px 0 18px rgba(20,60,50,.07);overflow-y:auto;padding:16px 14px 24px;z-index:60}
#rail h3{font-family:Georgia,serif;font-size:13px;margin:0 0 3px;color:#17352f}
#rail .sub{font-size:9px;color:#6a756f;margin-bottom:10px}
.rrow{padding:9px 2px;border-bottom:1px solid #edf0ed;font-size:9.5px}
.rrow:last-child{border:0}
.rrow .nm{font-weight:700;color:#1d3e35;line-height:1.35}
.rrow .meta{color:#6b756f;margin-top:3px;display:flex;justify-content:space-between;gap:6px}
.rrow .fin{white-space:nowrap;font-weight:700;color:#5a6b66}
.rrow .fin.late{color:#9d433f}
@media(min-width:1100px){body{padding-right:292px}}
@media(max-width:1100px){#rail{display:none}}
"""
if '#rail{' not in h:
    h = h.replace('</style>', CSS + '</style>', 1); ok2.append('CSS rail')

ASIDE = '<aside id="rail"><h3 id="rail-title">Projets du périmètre</h3><div class="sub" id="rail-sub"></div><div id="rail-list"></div></aside>'
if 'id="rail"' not in h:
    h = h.replace('</body>', ASIDE + '\n</body>', 1); ok2.append('panneau HTML')

FN = """function renderRail(){
var el=document.getElementById('rail-list');var sub=document.getElementById('rail-sub');var ti=document.getElementById('rail-title');
if(!el||!D.projets){return;}
var rows=D.projets.filter(function(p){return state.sec.has(p.s)&&state.par.has(p.p)&&state.st.has(p.t);});
rows.sort(function(a,b){return (a.fin||'9999-12-31')<(b.fin||'9999-12-31')?-1:1;});
if(ti)ti.textContent = state.sec.size===1 ? 'Projets : ' + D.secteurs[Array.from(state.sec)[0]] : 'Projets du périmètre';
if(sub)sub.textContent = rows.length + ' projet(s) en cours · triés par échéance';
var html='';
for(var i=0;i<rows.length;i++){var p=rows[i];
var d=p.fin ? p.fin.slice(8,10)+'/'+p.fin.slice(5,7)+'/'+p.fin.slice(0,4) : '—';
var late=p.fin&&p.fin<='2027-08-28';
html+='<div class="rrow"><div class="nm">'+p.nom+'</div><div class="meta"><span>'+D.secteurs[p.s]+'</span><span class="fin'+(late?' late':'')+'">Clôture : '+d+'</span></div><div class="meta"><span>'+D.partenaires[p.p]+'</span><span>'+(p.prev?Math.round(p.dec/p.prev*100):0)+' % décaissé</span></div></div>';
}
el.innerHTML=html||'<div class="rrow">Aucun projet dans ce périmètre.</div>';
}
function render(){"""
if 'function renderRail' not in h:
    h = h.replace('function render(){', FN, 1); ok2.append('fonction renderRail')

if 'tables(a); renderRail();' not in h and 'tables(a);' in h:
    h = h.replace('tables(a);', 'tables(a); renderRail();', 1); ok2.append('appel dans render()')

open('modules/recap.html', 'w', encoding='utf-8').write(h)
for k in ok2:
    print('✅ recap.html :', k)

print('\n👉 1) taskkill /F /IM python.exe puis python api.py')
print('👉 2) Ctrl + F5 sur /modules/recap.html')
