function printPointDG(){
  if(!document.getElementById('printModal')){
    document.body.insertAdjacentHTML('beforeend','<div class="modal" id="printModal"><div class="modal-box"><div class="modal-header"><h2>🖨️ Imprimer le point DG</h2><span class="close" onclick="document.getElementById(\'printModal\').classList.remove(\'show\')">×</span></div><div class="modal-body"><div class="modal-info">Document officiel DGFD — orientation <b>paysage</b>, police Bookman Old Style 11, pages numérotées.</div><label class="modal-label">Format du papier</label><select id="print-format" style="width:100%;padding:8px;border:1px solid #d7deea;border-radius:5px"><option value="A4">A4 — 210 × 297 mm (paysage)</option><option value="A3">A3 — 297 × 420 mm (paysage)</option></select><div style="display:flex;gap:10px;margin-top:12px"><button class="save-btn" onclick="lancerImpression(false)">🖨️ Imprimer</button><button class="save-btn" style="background:#1260d9" onclick="lancerImpression(true)">⬇️ Télécharger en PDF</button></div></div><div class="modal-footer"><button class="cancel-btn" onclick="document.getElementById(\'printModal\').classList.remove(\'show\')">Annuler</button></div></div></div>');
  }
  document.getElementById('printModal').classList.add('show');
}
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
        if(!curc){ curc=(first?'<h2>'+esc(proj)+'</h2>':'<h2>'+esc(proj)+' — suite</h2>')+TH; curm=18; first=false; }
        if(curm+hm>CAP-3){ chunks.push({html:curc+'</table>',m:curm}); curc='<h2>'+esc(proj)+' — suite</h2>'+TH; curm=18; }
        curc+=row; curm+=hm;
      });
      if(curc){ chunks.push({html:curc+'</table>',m:curm}); }
      chunks.forEach(function(ck){ add(ck.html, ck.m); });
    }
  }
  flush();
  var total=pages.length;
  var head='<div class="head"><div class="l">RÉPUBLIQUE DU BÉNIN<br>MINISTÈRE DE L\'ÉCONOMIE ET DES FINANCES<br><b>DIRECTION GÉNÉRALE DU FINANCEMENT DU DÉVELOPPEMENT (DGFD)</b></div><div class="r">Fraternité – Justice – Travail<br>Cité Ministérielle – Porto-Novo<br>Pôle de Suivi des Projets &amp; Programmes</div></div>';
  var out='<html><head><meta charset="UTF-8"><title>Point des recommandations</title><style>@page{size:'+fmt+' landscape;margin:0}body{margin:0;font-family:"Bookman Old Style","Book Antiqua",Georgia,serif;font-size:11pt;color:#111}.page{width:'+W+'mm;height:'+(H-1)+'mm;padding:6mm 8mm 10mm;position:relative;box-sizing:border-box;page-break-after:always;overflow:hidden}.page:last-child{page-break-after:auto}.head{display:flex;justify-content:space-between;border-bottom:2px solid #1e3a5f;padding-bottom:4px;margin-bottom:5px}.head .l{font-size:9pt;line-height:1.25}.head .l b{font-size:11pt}.head .r{font-size:9pt;text-align:right;font-style:italic}h1{font-size:13pt;text-align:center;text-transform:uppercase;margin:3px 0 6px}h2{font-size:11pt;background:#1e3a5f;color:#fff;padding:3px 6px;margin:6px 0 3px}table{border-collapse:collapse;width:100%}td,th{border:1px solid #444;padding:2px 4px;vertical-align:top;font-size:11pt}th{background:#e8eef7;text-transform:uppercase;font-size:10pt}.foot{position:absolute;bottom:4mm;left:8mm;right:8mm;border-top:1px solid #999;padding-top:2px;font-size:9pt;display:flex;justify-content:space-between;color:#444}</style></head><body>';
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
  var head='<div class="head"><div class="l">RÉPUBLIQUE DU BÉNIN<br>MINISTÈRE DE L\'ÉCONOMIE ET DES FINANCES<br><b>DIRECTION GÉNÉRALE DU FINANCEMENT DU DÉVELOPPEMENT (DGFD)</b></div><div class="r">Fraternité – Justice – Travail<br>Cité Ministérielle – Porto-Novo<br>Pôle de Suivi des Projets &amp; Programmes</div></div>';
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