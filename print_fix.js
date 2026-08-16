function printPointDG(){
  if(!document.getElementById('printModal')){
    document.body.insertAdjacentHTML('beforeend','<div class="modal" id="printModal"><div class="modal-box"><div class="modal-header"><h2>🖨️ Imprimer le point DG</h2><span class="close" onclick="document.getElementById(\'printModal\').classList.remove(\'show\')">×</span></div><div class="modal-body"><div class="modal-info">Document officiel DGFD — orientation <b>paysage</b>, police Bookman Old Style 11, pages numérotées.</div><label class="modal-label">Format du papier</label><select id="print-format" style="width:100%;padding:8px;border:1px solid #d7deea;border-radius:5px"><option value="A4">A4 — 210 × 297 mm (paysage)</option><option value="A3">A3 — 297 × 420 mm (paysage)</option></select><div style="display:flex;gap:10px;margin-top:12px"><button class="save-btn" onclick="lancerImpression(false)">🖨️ Imprimer</button><button class="save-btn" style="background:#1260d9" onclick="lancerImpression(true)">⬇️ Télécharger en PDF</button></div></div><div class="modal-footer"><button class="cancel-btn" onclick="document.getElementById(\'printModal\').classList.remove(\'show\')">Annuler</button></div></div></div>');
  }
  document.getElementById('printModal').classList.add('show');
}
var PROJ_INFO={
'PRODEFILAV-PEL':'Approb. 02/12/2021 • Clôture 30/06/2029 (prorogée) • Décaissement : prêt 34,46% / don 16,2% • TEP 39% • 16,00 Mds FCFA',
'PROMAC':'Approb. 22/11/2023 • Clôture 31/12/2028 • Décaissement 9,02% • TEP 15,71% • 15,99 Mds FCFA',
'PAPVS':'Approb. 07/07/2023 • Clôture 31/12/2028 • Décaissement BAD 10,42% / AGTF 10,55% • TEP 9% • 112,90 Mds FCFA',
'PRC':'Clôture 31/12/2027 • Décaissement BAD 60,95% / AGTF 65,34% / UE 78,77% • TEP 70% • 117,42 Mds FCFA',
'PDSECP 1':'Approb. 15/12/2023 • Clôture 30/07/2029 • Décaissement BAD 1,68% / AGTF 1,74% • TEP 6,25% • 55,63 Mds FCFA',
'PRESREDI':'Approb. 12/12/2017 • Clôture 30/09/2026 (prorogée) • Décaissement prêt 57,79% / don 36,27% • TEP 92% • 9,28 Mds FCFA',
'PERU 1':'Clôture 30/06/2028 • Décaissement 55,42% • TEP 82% • 42,62 Mds FCFA',
'PROTAS P1':'Approb. 10/12/2025 • Clôture 31/12/2030 • 70,12 Mds FCFA • En attente conditions 1er décaissement',
'PreRAB':'Approb. 18/07/2025 • Clôture 31/12/2030 • 24,80 Mds FCFA • En attente conditions 1er décaissement',
'PIDACC/BN':'Approb. 07/11/2018 • Clôture 31/12/2027 • Décaissement FAD 43,09% / GCF 17,44% / UE 10,60% • TEP 31%',
'PADECT':'Approb. 24/10/2025 • Clôture 31/12/2030 • 80,17 Mds FCFA • En attente conditions 1er décaissement',
'Ouidah-Hillacondji':'Projet en attente d\'approbation • 81,15% des fiches d\'entente signées',
'FP2E':'300 M USD • Mise en vigueur 27/05/2022 • Décaissement 44% • Clôture 31/03/2027',
'PACOFIDE':'310 M USD • Mise en vigueur 22/10/2020 • Décaissement 59,31% • Clôture 30/04/2030',
'P2AE':'200 M USD • Mise en vigueur 23/11/2021 • Décaissement 55,6% • Clôture 31/12/2026',
'ProDIJ':'101,3 M USD • Mise en vigueur 31/03/2021 • Décaissement 78,28% • Clôture 30/06/2027',
'Dorsale Nord':'30,41 M USD • Mise en vigueur 01/04/2019 • Décaissement 77,39% • Clôture 01/12/2026',
'PFC1':'90,10 M USD • Mise en vigueur 01/10/2019 • Décaissement 93,20% • Clôture 30/11/2026',
'PFC2':'80,7 M USD • Mise en vigueur 09/09/2025 • Décaissement 2,95% • Clôture 31/07/2032',
'PMUD-GN':'500 M USD (dont BM 200 M) • Mise en vigueur 18/12/2025 • Décaissement 11,62% • Clôture 31/12/2030',
'WACA+':'147 M USD • Non encore en vigueur • Clôture 26/11/2031',
'PHASAOC':'30 M USD • Mise en vigueur 29/09/2023 • Décaissement 20,11% • Clôture 15/12/2028',
'BRIC':'200 M USD • Mise en vigueur 13/03/2023 • Décaissement 50,19% • Clôture 30/06/2028',
'Gbéssoké':'159 M USD (dont BM 100 M) • Mise en vigueur 10/07/2023 • Décaissement 44,48% • Clôture 31/12/2027',
'Terra Bénin':'100 M USD • Mise en vigueur 22/12/2025 • Décaissement 36,32% • Clôture 30/09/2030',
'3035':'Approb. 2017-2020 • Clôture prorogée 31/12/2028 • 60 Mds FCFA • Décaissement 72-90% • TEP 83%',
'LTP':'Approb. 27/06/2024 (ph.1) / 25/06/2025 (ph.2) • 60 Mds FCFA • Décaissement 1% / 0,3% • TEP 0%',
'PUR-ZEDAGA':'Mise en vigueur 15/05/2023 • 25 Mds FCFA • Décaissement 82,50% • TEP 78,15%',
'PAPC 1':'Approb. 21/03/2018 • Clôture 31/12/2027 (prorogée) • 20 Mds FCFA • Décaissement 79,7% • TEP 75,6%',
'PAPC 2':'Approb. 08/05/2023 • Clôture 09/11/2029 • 22 Mds FCFA • Décaissement 0%',
'PRC Lot 4':'Approb. 20/03/2019 • Clôture 31/12/2027 • 17 Mds FCFA • Décaissement 13,9%',
'PROMER':'Approb. 20/09/2022 • Clôture 12/02/2028 • 27 Mds FCFA • Décaissement 1,5% • TEP 17,5%',
'ProSeR 1':'Approb. 24/11/2020 • Clôture 01/07/2027 • 10 Mds FCFA • Décaissement 43,6% • TEP 57,83%',
'ProSeR 2':'Approb. 19/05/2022 • Clôture 05/02/2029 • 17,5 Mds FCFA • Décaissement 31,2% • TEP 30,33%',
'FTD':'Approb. 26/03/2025 • 19,5 Mds FCFA • Conditions de 1er décaissement satisfaites'
};
function pInfo(proj){ if(PROJ_INFO[proj])return PROJ_INFO[proj]; for(var k in PROJ_INFO){ if(proj.indexOf(k)>=0)return PROJ_INFO[k]; } return ''; }
function lancerImpression(telecharger){
  var fmt=document.getElementById('print-format').value;
  document.getElementById('printModal').classList.remove('show');
  var list=recosFiltrees();
  if(!list.length){flash('Aucune recommandation à imprimer',false);return;}
  var A3=(fmt==='A3');
  var W=A3?420:297, H=A3?297:210, CAP=A3?256:168;
  var pages=[], cur={html:'',h:0};
  function flush(){ if(cur.html){pages.push(cur); cur={html:'',h:0};} }
  function add(html,hm){ if(cur.h+hm>CAP){flush();} cur.html+=html; cur.h+=hm; }
  function rowH(r){
    var cT=A3?45:30, cC=A3?33:22, cD=A3?35:24;
    var lines=Math.max(1, Math.ceil((r.texte||'').length/cT), Math.ceil((r.commentaires||'').length/cC), Math.ceil((r.difficulte||'').length/cD));
    return Math.min(A3?44:56, 4 + lines*4.6);
  }
  var TH='<table><tr><th style="width:6mm">N°</th><th style="width:20%">Points d\'attention</th><th style="width:26%">Recommandations / décisions</th><th style="width:13mm">Échéance</th><th style="width:11%">Responsables</th><th style="width:11%">Associés</th><th>Observations</th></tr>';
  var byPart={}; list.forEach(function(r){var p=r.partenaire||'Divers';(byPart[p]=byPart[p]||[]).push(r);});
  for(var part in byPart){
    var L=byPart[part], c={ex:0,en:0,ne:0,ret:0};
    L.forEach(function(r){ if(r.statut==='executee')c.ex++; else if(r.statut==='non_executee'||r.statut==='annulee')c.ne++; else c.en++; if(enRetard(r))c.ret++; });
    add('<h1>Point des recommandations — '+esc(part)+'<br><span style="font-size:9pt;text-transform:none">édité le '+dateFr(new Date().toISOString())+'</span></h1>',14);
    add('<table><tr><th>Recommandations</th><th>Nombre</th><th>Taux (%)</th></tr><tr><td>Exécutées</td><td>'+c.ex+'</td><td>'+Math.round(c.ex/L.length*10000)/100+'</td></tr><tr><td>En cours</td><td>'+c.en+'</td><td>'+Math.round(c.en/L.length*10000)/100+'</td></tr><tr><td>Non exécutées</td><td>'+c.ne+'</td><td>'+Math.round(c.ne/L.length*10000)/100+'</td></tr><tr><td>Dont en retard</td><td>'+c.ret+'</td><td>'+Math.round(c.ret/L.length*10000)/100+'</td></tr><tr><td><b>Total</b></td><td><b>'+L.length+'</b></td><td><b>100</b></td></tr></table>',54);
    var byProj={}; L.forEach(function(r){var pj=r.projet||'Divers';(byProj[pj]=byProj[pj]||[]).push(r);});
    for(var proj in byProj){
      var lp=byProj[proj];
      var chunks=[], curc=null, curm=0, first=true;
      lp.forEach(function(r,i){
        var hm=rowH(r);
        var off=r.statut==='executee'?'Exécutée':(r.statut==='non_executee'||r.statut==='annulee'?'Non exécutée':'En cours');
        if(enRetard(r))off+=' (retard)';
        var row='<tr><td>'+(i+1)+'</td><td>'+esc(r.difficulte||'')+'</td><td>'+esc(r.texte||'')+'</td><td>'+dateFr(r.echeance)+'</td><td>'+esc(r.responsable_direct||'')+'</td><td>'+esc(r.associe||'')+'</td><td>'+esc(r.commentaires||'')+'</td></tr>';
        if(!curc){ curc=(first?'<h2>'+esc(proj)+'</h2>'+(pInfo(proj)?'<div class="pinfo">'+pInfo(proj)+'</div>':''):'<h2>'+esc(proj)+' — suite</h2>')+TH; curm=(first&&pInfo(proj))?23:18; first=false; }
        if(curm+hm>CAP-3){ chunks.push({html:curc+'</table>',m:curm}); curc='<h2>'+esc(proj)+' — suite</h2>'+TH; curm=18; }
        curc+=row; curm+=hm;
      });
      if(curc){ chunks.push({html:curc+'</table>',m:curm}); }
      chunks.forEach(function(ck){ add(ck.html, ck.m); });
    }
  }
  flush();
  var total=pages.length;
  var head='<div class="head"><div class="l">RÉPUBLIQUE DU BÉNIN<br>MINISTÈRE DE L\'ÉCONOMIE ET DES FINANCES<br><b>DIRECTION GÉNÉRALE DU FINANCEMENT DU DÉVELOPPEMENT (DGFD)</b></div><div class="r">Fraternité – Justice – Travail<br>Cité Ministérielle – Porto-Novo<br>Pôle de Suivi des Projets & Programmes</div></div>';
  var out='<html><head><meta charset="UTF-8"><title>Point des recommandations</title><style>@page{size:'+fmt+' landscape;margin:0}body{margin:0;font-family:"Bookman Old Style","Book Antiqua",Georgia,serif;font-size:11pt;color:#111}.page{width:'+W+'mm;height:'+(H-1)+'mm;padding:6mm 8mm 10mm;position:relative;box-sizing:border-box;page-break-after:always;overflow:hidden}.page:last-child{page-break-after:auto}.head{display:flex;justify-content:space-between;border-bottom:2px solid #1e3a5f;padding-bottom:4px;margin-bottom:5px}.head .l{font-size:9pt;line-height:1.25}.head .l b{font-size:11pt}.head .r{font-size:9pt;text-align:right;font-style:italic}h1{font-size:13pt;text-align:center;text-transform:uppercase;margin:3px 0 6px}h2{font-size:11pt;background:#1e3a5f;color:#fff;padding:3px 6px;margin:6px 0 3px}table{border-collapse:collapse;width:100%}td,th{border:1px solid #444;padding:2px 4px;vertical-align:top;font-size:11pt}th{background:#e8eef7;text-transform:uppercase;font-size:10pt}.pinfo{font-size:9pt;font-style:italic;color:#333;margin:0 0 3px}.foot{position:absolute;bottom:4mm;left:8mm;right:8mm;border-top:1px solid #999;padding-top:2px;font-size:9pt;display:flex;justify-content:space-between;color:#444}</style></head><body>';
  for(var i=0;i<total;i++){
    out+='<div class="page">'+head+pages[i].html+'<div class="foot"><span>DGFD — Suivi des recommandations des PTF</span><span>édité le '+dateFr(new Date().toISOString())+'</span><span>Page '+(i+1)+' / '+total+'</span></div></div>';
  }
  out+='</body></html>';
  var w=window.open('','_blank');
  if(!w){flash('Autorisez les popups pour imprimer',false);return;}
  w.document.write(out); w.document.close();
  setTimeout(function(){ w.focus(); w.print(); },600);
  if(telecharger) flash('Dans la fenêtre, choisissez « Enregistrer au format PDF »', true);
}
async function genererSynthese(){
  var now=new Date();
  var mois=['janvier','février','mars','avril','mai','juin','juillet','août','septembre','octobre','novembre','décembre'];
  var label=mois[now.getMonth()]+' '+now.getFullYear();
  var hist=[];
  try{ var rh=await fetch('/api/suivi/historique_mois'); hist=(await rh.json()).historique||[]; }catch(e){}
  var W=210,H=297,CAP=258;
  var pages=[],cur={html:'',h:0};
  function flush(){ if(cur.html){pages.push(cur);cur={html:'',h:0};} }
  function add(hm,html){ if(cur.h+hm>CAP)flush(); cur.html+=html; cur.h+=hm; }
  function tableChunked(headHtml, rows){
    var buf=null, curm=0;
    rows.forEach(function(rw){
      if(buf===null){ buf=headHtml; curm=10; }
      if(curm+rw.m>CAP-3){ add(curm, buf+'</table>'); buf=headHtml; curm=10; }
      buf+=rw.html; curm+=rw.m;
    });
    if(buf!==null) add(curm, buf+'</table>');
  }
  add(16,'<h1>Synthèse mensuelle du suivi des recommandations<br><span style="font-size:10pt;text-transform:none">'+label+' — éditée le '+dateFr(now.toISOString())+'</span></h1>');
  add(10,'<h2>1. Situation par partenaire</h2>');
  var byPart={}; RECOS.forEach(function(r){ var p=r.partenaire||'Divers'; (byPart[p]=byPart[p]||[]).push(r); });
  var rows1=[];
  for(var p in byPart){ var L=byPart[p]; var ex=0,en=0,ret=0; L.forEach(function(r){ if(r.statut==='executee')ex++; else if(enRetard(r))ret++; else en++; });
    rows1.push({m:8,html:'<tr><td>'+esc(p)+'</td><td>'+L.length+'</td><td>'+ex+'</td><td>'+en+'</td><td>'+ret+'</td><td>'+Math.round(ex/L.length*100)+'%</td></tr>'}); }
  tableChunked('<table><tr><th>Partenaire</th><th>Total</th><th>Exécutées</th><th>En cours</th><th>En retard</th><th>Taux d\'exécution</th></tr>', rows1);
  add(10,'<h2>2. Activité des 30 derniers jours</h2>');
  if(hist.length){ var rows2=hist.map(function(hh){ var r=trouver(hh.reco_id)||{}; var txt=(hh.nouveau_statut?('Statut : '+(LIB[hh.ancien_statut]||'-')+' → '+(LIB[hh.nouveau_statut]||'-')+'. '):'')+(hh.commentaire||'');
      return {m:Math.min(30,5+Math.ceil(txt.length/90)*4.6), html:'<tr><td>'+dateFr(hh.created_at)+'</td><td>'+esc(r.projet||'')+'</td><td>'+esc(txt)+'</td><td>'+esc(hh.auteur||'')+'</td></tr>'}; });
    tableChunked('<table><tr><th>Date</th><th>Projet</th><th>Changement / commentaire</th><th>Auteur</th></tr>', rows2);
  } else add(10,'<p>Aucune modification enregistrée sur la période.</p>');
  add(10,'<h2>3. Points d\'attention (recommandations en retard)</h2>');
  var rows3=RECOS.filter(enRetard).map(function(r){ return {m:Math.min(30,5+Math.ceil((r.texte||'').length/90)*4.6), html:'<tr><td>'+esc(r.projet||'')+'</td><td>'+esc(r.texte||'')+'</td><td>'+dateFr(r.echeance)+'</td><td>'+esc(r.responsable_direct||'')+'</td></tr>'}; });
  if(rows3.length) tableChunked('<table><tr><th>Projet</th><th>Recommandation</th><th>Échéance</th><th>Responsable</th></tr>', rows3);
  else add(10,'<p>Aucune recommandation en retard.</p>');
  flush();
  var total=pages.length;
  var head='<div class="head"><div class="l">RÉPUBLIQUE DU BÉNIN<br>MINISTÈRE DE L\'ÉCONOMIE ET DES FINANCES<br><b>DIRECTION GÉNÉRALE DU FINANCEMENT DU DÉVELOPPEMENT (DGFD)</b></div><div class="r">Fraternité – Justice – Travail<br>Cité Ministérielle – Porto-Novo<br>Pôle de Suivi des Projets & Programmes</div></div>';
  var out='<html><head><meta charset="UTF-8"><title>Synthèse mensuelle</title><style>@page{size:A4 portrait;margin:0}body{margin:0;font-family:"Bookman Old Style","Book Antiqua",Georgia,serif;font-size:11pt;color:#111}.page{width:210mm;height:296mm;padding:8mm 12mm 12mm;position:relative;box-sizing:border-box;page-break-after:always;overflow:hidden}.page:last-child{page-break-after:auto}.head{display:flex;justify-content:space-between;border-bottom:2px solid #1e3a5f;padding-bottom:4px;margin-bottom:6px}.head .l{font-size:9pt;line-height:1.25}.head .l b{font-size:11pt}.head .r{font-size:9pt;text-align:right;font-style:italic}h1{font-size:13pt;text-align:center;text-transform:uppercase;margin:3px 0 8px}h2{font-size:11pt;background:#1e3a5f;color:#fff;padding:3px 6px;margin:8px 0 4px}p{margin:6px 0}table{border-collapse:collapse;width:100%}td,th{border:1px solid #444;padding:2px 4px;vertical-align:top;font-size:10pt}th{background:#e8eef7;text-transform:uppercase;font-size:9pt}.foot{position:absolute;bottom:5mm;left:12mm;right:12mm;border-top:1px solid #999;padding-top:2px;font-size:9pt;display:flex;justify-content:space-between;color:#444}</style></head><body>';
  for(var i=0;i<total;i++){
    out+='<div class="page">'+head+pages[i].html+'<div class="foot"><span>DGFD — Synthèse mensuelle ('+label+')</span><span>éditée le '+dateFr(now.toISOString())+'</span><span>Page '+(i+1)+' / '+total+'</span></div></div>';
  }
  out+='</body></html>';
  var w=window.open('','_blank');
  if(!w){flash('Autorisez les popups pour imprimer',false);return;}
  w.document.write(out); w.document.close();
  setTimeout(function(){ w.focus(); w.print(); },600);
}
var DG_PER=[
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
setInterval(function(){ if(!DG_HOVER2&&!document.hidden){ DG_PI=(DG_PI+1)%DG_PER.length; majDG(); } },3000);
