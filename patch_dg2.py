h = open('print_fix.js', encoding='utf-8').read()
i = h.find('var DG_PROJ=')
if i >= 0:
    h = h[:i]
    print('Ancien bloc DG supprime')
else:
    print('Aucun ancien bloc DG trouve')
h = h.rstrip() + '\n'

new = '''var DG_PER=[
 {lib:'En retard (échéance dépassée)', test:function(r){return enRetard(r);}},
 {lib:'Échéance dans les 7 prochains jours', test:function(r){return !enRetard(r)&&r.echeance&&daysTo(r.echeance)<=7;}},
 {lib:'Échéance dans les 30 prochains jours', test:function(r){return !enRetard(r)&&r.echeance&&daysTo(r.echeance)>7&&daysTo(r.echeance)<=30;}},
 {lib:'Échéance dans les 60 prochains jours', test:function(r){return !enRetard(r)&&r.echeance&&daysTo(r.echeance)>30&&daysTo(r.echeance)<=60;}}
];
var DG_PI=0, DG_HOVER2=false;
function daysTo(d){ if(!d)return 9999; var t=new Date(); t.setHours(0,0,0,0); var e=new Date(d); return Math.round((e-t)/86400000); }
function majDG(){
  var cards=document.querySelectorAll('.dg-card'); if(cards.length<3)return;
  var per=DG_PER[DG_PI];
  var list=RECOS.filter(per.test).sort(function(a,b){return String(a.echeance)<String(b.echeance)?-1:1;});
  var h="<div class='dg-title'><div class='card-title'>À L'ATTENTION DU DG</div><span class='action-required'>"+list.length+" action(s)</span></div>";
  h+='<div style="display:flex;align-items:center;justify-content:space-between;gap:6px;margin:4px 0 8px"><span onclick="dgPrev()" style="cursor:pointer;font-size:16px;color:#1260d9;font-weight:800;padding:0 6px">‹</span><div style="font-size:11px;font-weight:800;color:#1e3a5f;text-align:center;flex:1">'+per.lib+' ('+(DG_PI+1)+'/'+DG_PER.length+')</div><span onclick="dgNext()" style="cursor:pointer;font-size:16px;color:#1260d9;font-weight:800;padding:0 6px">›</span></div>';
  if(list.length){ list.slice(0,4).forEach(function(r){ h+='<div class="dg-item" style="cursor:pointer" onclick="ouvrirStatut('+r.id+')" title="Cliquer pour mettre à jour"><span class="dg-dot"></span><div class="dg-project">'+esc(r.projet||'')+'</div><div class="dg-text">'+esc((r.texte||'').slice(0,60))+'</div><span class="dg-label">'+dateFr(r.echeance)+' • '+esc(r.responsable_direct||'')+'</span></div>'; }); }
  else { h+='<div style="font-size:11px;color:#6b7280;padding:8px">Aucune recommandation dans cette période.</div>'; }
  h+='<div class="dg-footer" style="cursor:pointer" onclick="voirToutesActions()">Voir toutes les actions en retard →</div>';
  cards[0].innerHTML=h;
}
function dgNext(){ DG_PI=(DG_PI+1)%DG_PER.length; majDG(); }
function dgPrev(){ DG_PI=(DG_PI-1+DG_PER.length)%DG_PER.length; majDG(); }
document.addEventListener('mouseover',function(e){ if(e.target.closest&&e.target.closest('.dg-card'))DG_HOVER2=true; });
document.addEventListener('mouseout',function(e){ if(e.target.closest&&e.target.closest('.dg-card'))DG_HOVER2=false; });
setInterval(function(){ if(!DG_HOVER2&&!document.hidden){ DG_PI=(DG_PI+1)%DG_PER.length; majDG(); } },10000);
'''
open('print_fix.js', 'w', encoding='utf-8').write(h + new)
print('Nouveau bloc DG par periodes ajoute')
