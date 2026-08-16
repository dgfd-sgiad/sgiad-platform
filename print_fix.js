function printPointDG(){
  if(!document.getElementById('printModal')){
    document.body.insertAdjacentHTML('beforeend','<div class="modal" id="printModal"><div class="modal-box"><div class="modal-header"><h2>🖨️ Imprimer le point DG</h2><span class="close" onclick="document.getElementById(\'printModal\').classList.remove(\'show\')">×</span></div><div class="modal-body"><div class="modal-info">Document officiel DGFD — orientation <b>paysage</b>, en-tête de la Direction, pages numérotées.</div><label class="modal-label">Format du papier</label><select id="print-format" style="width:100%;padding:8px;border:1px solid #d7deea;border-radius:5px"><option value="A4">A4 — 210 × 297 mm (paysage)</option><option value="A3">A3 — 297 × 420 mm (paysage)</option></select><div style="display:flex;gap:10px;margin-top:12px"><button class="save-btn" onclick="lancerImpression(false)">🖨️ Imprimer</button><button class="save-btn" style="background:#1260d9" onclick="lancerImpression(true)">⬇️ Télécharger en PDF</button></div></div><div class="modal-footer"><button class="cancel-btn" onclick="document.getElementById(\'printModal\').classList.remove(\'show\')">Annuler</button></div></div></div>');
  }
  document.getElementById('printModal').classList.add('show');
}
function lancerImpression(telecharger){
  var fmt=document.getElementById('print-format').value;
  document.getElementById('printModal').classList.remove('show');
  var list=recosFiltrees();
  if(!list.length){flash('Aucune recommandation à imprimer',false);return;}
  var W=fmt==='A3'?420:297, H=fmt==='A3'?297:210, CAP=fmt==='A3'?255:165;
  var pages=[], cur={html:'',h:0};
  function flush(){ if(cur.html){pages.push(cur); cur={html:'',h:0};} }
  function add(html,hm){ if(cur.h+hm>CAP){flush();} cur.html+=html; cur.h+=hm; }
  var byPart={}; list.forEach(function(r){var p=r.partenaire||'Divers';(byPart[p]=byPart[p]||[]).push(r);});
  for(var part in byPart){
    var L=byPart[part], c={ex:0,en:0,ne:0,ret:0};
    L.forEach(function(r){ if(r.statut==='executee')c.ex++; else if(r.statut==='non_executee'||r.statut==='annulee')c.ne++; else c.en++; if(enRetard(r))c.ret++; });
    add('<h1>Point des recommandations — '+esc(part)+'<br><span style="font-size:8pt;text-transform:none">édité le '+dateFr(new Date().toISOString())+'</span></h1>',16);
    add('<table><tr><th>Recommandations</th><th>Nombre</th><th>Taux (%)</th></tr><tr><td>Exécutées</td><td>'+c.ex+'</td><td>'+Math.round(c.ex/L.length*10000)/100+'</td></tr><tr><td>En cours</td><td>'+c.en+'</td><td>'+Math.round(c.en/L.length*10000)/100+'</td></tr><tr><td>Non exécutées</td><td>'+c.ne+'</td><td>'+Math.round(c.ne/L.length*10000)/100+'</td></tr><tr><td>Dont en retard</td><td>'+c.ret+'</td><td>'+Math.round(c.ret/L.length*10000)/100+'</td></tr><tr><td><b>Total</b></td><td><b>'+L.length+'</b></td><td><b>100</b></td></tr></table>',45);
    var byProj={}; L.forEach(function(r){var pj=r.projet||'Divers';(byProj[pj]=byProj[pj]||[]).push(r);});
    for(var proj in byProj){
      var lp=byProj[proj];
      var TH='<table><tr><th style="width:6mm">N°</th><th style="width:20%">Points d\'attention</th><th style="width:26%">Recommandations / décisions</th><th style="width:13mm">Échéance</th><th style="width:11%">Responsables</th><th style="width:11%">Associés</th><th>Observations</th></tr>';
      var chunks=[], curc=null, curm=0;
      lp.forEach(function(r,i){
        var off=r.statut==='executee'?'Exécutée':(r.statut==='non_executee'||r.statut==='annulee'?'Non exécutée':'En cours');
        if(enRetard(r))off+=' (retard)';
        var txt=(r.difficulte||'')+(r.texte||'')+(r.commentaires||'');
        var hm=Math.min(60, 10+Math.floor(txt.length/70)*4);
        var row='<tr><td>'+(i+1)+'</td><td>'+esc(r.difficulte||'')+'</td><td>'+esc(r.texte||'')+'</td><td>'+dateFr(r.echeance)+'</td><td>'+esc(r.responsable_direct||'')+'</td><td>'+esc(r.associe||'')+'</td><td>'+esc(r.commentaires||'')+'</td></tr>';
        if(!curc){ curc=TH; curm=18; }
        if(curm+hm>CAP-5){ chunks.push({html:curc+'</table>',m:curm}); curc=TH; curm=18; }
        curc+=row; curm+=hm;
      });
      if(curc){ chunks.push({html:curc+'</table>',m:curm}); }
      chunks.forEach(function(ck,ci){
        add('<h2>'+esc(proj)+(ci>0?' — suite':'')+'</h2>',10);
        add(ck.html, ck.m);
      });
    }
  }
  flush();
  var total=pages.length;
  var head='<div class="head"><div class="l">RÉPUBLIQUE DU BÉNIN<br>MINISTÈRE DE L\'ÉCONOMIE ET DES FINANCES<br><b>DIRECTION GÉNÉRALE DU FINANCEMENT DU DÉVELOPPEMENT (DGFD)</b></div><div class="r">Fraternité – Justice – Travail<br>Cité Ministérielle – Porto-Novo<br>Pôle de Suivi des Projets &amp; Programmes</div></div>';
  var out='<html><head><meta charset="UTF-8"><title>Point des recommandations</title><style>@page{size:'+fmt+' landscape;margin:0}body{margin:0;font-family:Calibri,Arial,sans-serif;font-size:9pt;color:#111}.page{width:'+W+'mm;height:'+(H-1)+'mm;padding:7mm 9mm 12mm;position:relative;box-sizing:border-box;page-break-after:always;overflow:hidden}.page:last-child{page-break-after:auto}.head{display:flex;justify-content:space-between;border-bottom:2px solid #1e3a5f;padding-bottom:4px;margin-bottom:5px}.head .l{font-size:8pt;line-height:1.25}.head .l b{font-size:9.5pt}.head .r{font-size:8pt;text-align:right;font-style:italic}h1{font-size:11pt;text-align:center;text-transform:uppercase;margin:3px 0 6px}h2{font-size:9.5pt;background:#1e3a5f;color:#fff;padding:3px 6px;margin:6px 0 3px}table{border-collapse:collapse;width:100%}td,th{border:1px solid #444;padding:3px 5px;vertical-align:top;font-size:8.5pt}th{background:#e8eef7;text-transform:uppercase;font-size:7.5pt}.foot{position:absolute;bottom:4mm;left:9mm;right:9mm;border-top:1px solid #999;padding-top:2px;font-size:7.5pt;display:flex;justify-content:space-between;color:#444}</style></head><body>';
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