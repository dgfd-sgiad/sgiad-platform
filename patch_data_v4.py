# -*- coding: utf-8 -*-
p = 'modules/recap.html'
s = open(p, encoding='utf-8').read()

start = s.find('function _fetchJSON')
endm = 'jours_annee:365};'
end = s.find(endm, start)
if start == -1 or end == -1:
    print('❌ Bloc builder introuvable')
    raise SystemExit
end += len(endm)
print('📦 Bloc builder trouvé :', end - start, 'caractères')

NEW = '''function _fetchJSON(u){try{var x=new XMLHttpRequest();x.open('GET',u,false);x.send(null);return x.status===200?JSON.parse(x.responseText):null;}catch(e){return null;}}
function _nrm(s){s=String(s||'').toUpperCase();try{s=s.normalize('NFD').replace(/[\\u0300-\\u036f]/g,'');}catch(e){}return s.replace(/[^A-Z0-9 ]/g,' ').replace(/\\s+/g,' ').trim();}
var _STOP={DE:1,DU:1,DES:1,LA:1,LE:1,LES:1,AU:1,AUX:1,EN:1,POUR:1,ET:1,SUR:1,DANS:1,PAR:1,AVEC:1,PROJET:1,PROGRAMME:1,BENIN:1,D:1,L:1,A:1};
function _tok(s){var o={};var a=_nrm(s).split(' ');for(var i=0;i<a.length;i++){if(a[i].length>=3&&!_STOP[a[i]])o[a[i]]=1;}return o;}
function _acr(s){var m=String(s||'').match(/\\(([A-Z0-9][A-Za-z0-9\\- ]{2,})\\)/);if(!m)return '';var t=_nrm(m[1]);return t.length>=3?t:'';}
var _acc=_fetchJSON('/api/accords/list')||[];
var _cagd=_fetchJSON('/api/decaissements/cagd')||[];
var _crow={};
_cagd.forEach(function(c){var k=_nrm(c.projet);var y=+c.periode||0;var v=+c.montant_total_fcfa||0;if(!_crow[k]||y>_crow[k].y)_crow[k]={y:y,v:v,raw:String(c.projet||'')};});
var _crows=Object.keys(_crow).map(function(k){return {k:k,v:_crow[k].v,tok:_tok(k),acr:_acr(_crow[k].raw)};});
function _score(ta,ca){var na=0,nb=0,k;for(k in ta)na++;for(k in ca)nb++;if(!na||!nb)return 0;var small=na<nb?ta:ca,big=small===ta?ca:ta,n=0;for(k in small)if(big[k])n++;return n/Math.min(na,nb);}
function _findCum(objet){
  var aO=_acr(objet);
  if(aO){for(var i=0;i<_crows.length;i++){if(_crows[i].acr&&(_crows[i].acr.indexOf(aO)===0||aO.indexOf(_crows[i].acr)===0))return _crows[i].v;}}
  var on=_nrm(objet);
  for(var i=0;i<_crows.length;i++){var ck=_crows[i].k;if(ck.length>=18&&on.indexOf(ck.slice(0,18))===0)return _crows[i].v;if(on.length>=18&&ck.indexOf(on.slice(0,18))===0)return _crows[i].v;}
  var tO=_tok(objet),best=0,bv=0;
  for(var i=0;i<_crows.length;i++){var sc=_score(tO,_crows[i].tok);if(sc>best){best=sc;bv=_crows[i].v;}}
  return best>=0.5?bv:0;
}
var _secteurs=[];var _secIdx={};
_acc.forEach(function(a){var sg=String(a.secteur_principal||'NON PRÉCISÉ').trim().toUpperCase();if(!(sg in _secIdx)){_secIdx[sg]=_secteurs.length;_secteurs.push(sg);}});
var _PARTS=['AFD','BAD','Banque mondiale','BID','Union européenne'];
function _parIdx(pp){pp=_nrm(pp);if(pp.indexOf('AFD')===0||pp.indexOf('AGENCE FRANCAISE')===0)return 0;if(pp.indexOf('BAD')>=0)return 1;if(pp.indexOf('BANQUE MONDIALE')>=0||pp.indexOf('BIRD')>=0||pp.indexOf('IDA')>=0||pp.indexOf('AID')>=0)return 2;if(pp.indexOf('BID')>=0)return 3;if(pp.indexOf('UNION EUROPEENNE')>=0)return 4;return 5;}
var _cells=[];var _matched=0;
_acc.forEach(function(a){
  var prev=(+a.montant_total_fcfa||0)/1e9;if(prev<=0)return;
  var st=String(a.statut||'').toLowerCase();
  if(st.indexOf('achev')>=0||st.indexOf('clotur')>=0||st.indexOf('clos')>=0)return;
  var ref=String(a.nouvelle_date_cloture||a.date_cloture||'').slice(0,10);
  if(ref&&ref<'2026-01-01')return;
  var dec=Math.min(prev,_findCum(a.objet_accord)/1e9);
  if(dec>0)_matched++;
  var taux=prev?dec/prev*100:0;
  var proche=ref&&ref<='2027-08-28';
  var t=(taux<40&&proche)?2:((proche||taux<50)?1:0);
  _cells.push({s:_secIdx[String(a.secteur_principal||'NON PRÉCISÉ').trim().toUpperCase()],p:_parIdx(a.partenaire),t:t,prev:prev,dec:dec,pq:[prev*.25,prev*.25,prev*.25,prev*.25],dq:[dec*.3,dec*.3,dec*.4],n:1});
});
const D={exercice:'2026',situation:'28 août 2026',secteurs:_secteurs,partenaires:_PARTS.concat(['Autres']),statuts:['En cours','À surveiller','En difficulté'],cells:_cells,part_t3:2/3,jours_ecoules:240,jours_annee:365};
console.log('[SGIAD] projets en cours :',_cells.length,'· dont matchés CAGD :',_matched);'''

s = s[:start] + NEW + s[end:]

# Libellés corrigés (engagements, pas "prévision")
for old, new in [
    ("'</em> de sa pr\\u00e9vision ' + D.exercice", "'</em> de ses engagements ' + D.exercice"),
    ("lb:'Pr\\u00e9vision ' + D.exercice", "lb:'Engagements ' + D.exercice"),
    ("Mds FCFA programm\\u00e9s", "Mds FCFA engag\\u00e9s"),
    ("de FCFA programm\\u00e9s", "de FCFA engag\\u00e9s"),
]:
    if old in s:
        s = s.replace(old, new, 1)
        print('✅ libellé :', new[:40])

open(p, 'w', encoding='utf-8').write(s)
print('✅ Patch v4 appliqué — Ctrl + F5 puis F12 (Console) pour voir le compteur de matching')
