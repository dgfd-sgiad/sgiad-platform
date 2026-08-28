# -*- coding: utf-8 -*-
import re

p = 'modules/recap.html'
s = open(p, encoding='utf-8').read()

m = re.search(r'const\s+D\s*=\s*\{', s)
if not m:
    print('❌ const D introuvable')
    raise SystemExit

# Comptage d'accolades pour trouver la fin exacte du bloc D
i = m.start()
j = s.find('{', m.end() - 1)
depth = 0
k = j
while k < len(s):
    c = s[k]
    if c == '{':
        depth += 1
    elif c == '}':
        depth -= 1
        if depth == 0:
            break
    k += 1
end = s.find(';', k) + 1
print('📦 Bloc D statique trouvé :', end - i, 'caractères')

BUILDER = '''function _fetchJSON(u){try{var x=new XMLHttpRequest();x.open('GET',u,false);x.send(null);return x.status===200?JSON.parse(x.responseText):null;}catch(e){return null;}}
function _nrm(s){s=String(s||'').toUpperCase();try{s=s.normalize('NFD').replace(/[\\u0300-\\u036f]/g,'');}catch(e){}return s.replace(/[^A-Z0-9 ]/g,' ');}
var _acc=_fetchJSON('/api/accords/list')||[];
var _cagd=_fetchJSON('/api/decaissements/cagd')||[];
var _secteurs=[];var _secIdx={};
_acc.forEach(function(a){var sg=a.secteur_principal||'Non précisé';if(!(sg in _secIdx)){_secIdx[sg]=_secteurs.length;_secteurs.push(sg);}});
var _PARTS=['AFD','BAD','Banque mondiale','BID','Union européenne'];
function _parIdx(pp){pp=_nrm(pp);for(var i2=0;i2<_PARTS.length;i2++){if(pp.indexOf(_nrm(_PARTS[i2]))>=0)return i2;}return 5;}
var _cum={};
_cagd.forEach(function(c){var kk=_nrm(c.projet);var yy=+c.periode||0;var vv=+c.montant_total_fcfa||0;if(!_cum[kk]||yy>_cum[kk].y)_cum[kk]={y:yy,v:vv};});
function _findCum(o){var on=_nrm(o);if(_cum[on])return _cum[on].v;var op=on.slice(0,25);for(var k2 in _cum){if(op&&k2.indexOf(op)===0)return _cum[k2].v;var kp=k2.slice(0,25);if(kp&&on.indexOf(kp)===0)return _cum[k2].v;}return 0;}
var _cells=[];
_acc.forEach(function(a){
  var prev=(+a.montant_total_fcfa||0)/1e9;if(prev<=0)return;
  var ref=String(a.nouvelle_date_cloture||a.date_cloture||'').slice(0,10);
  if(ref&&ref<'2026-01-01')return;
  var dec=Math.min(prev,_findCum(a.objet_accord)/1e9);
  var taux=prev?dec/prev*100:0;
  var proche=ref&&ref<='2027-08-28';
  var t=(taux<40&&proche)?2:((proche||taux<50)?1:0);
  _cells.push({s:_secIdx[a.secteur_principal||'Non précisé'],p:_parIdx(a.partenaire),t:t,prev:prev,dec:dec,pq:[prev*.25,prev*.25,prev*.25,prev*.25],dq:[dec*.3,dec*.3,dec*.4],n:1});
});
const D={exercice:'2026',situation:'28 août 2026',secteurs:_secteurs,partenaires:_PARTS.concat(['Autres']),statuts:['En cours','À surveiller','En difficulté'],cells:_cells,part_t3:2/3,jours_ecoules:240,jours_annee:365};'''

s = s[:i] + BUILDER + s[end:]

# Dynamiser les textes codés en dur
old1 = '188 projets \\u00b7 1\\u202f248,75 Mds FCFA'
new1 = "' + NB0.format(a.n) + ' projets \\u00b7 ' + f2(a.prev) + ' Mds FCFA"
if old1 in s:
    s = s.replace(old1, new1, 1)
    print('✅ selinfo dynamisé')
if "'33 partenaires'" in s:
    s = s.replace("'33 partenaires'", "D.partenaires.length + ' partenaires'", 1)
    print('✅ nb partenaires dynamisé')

open(p, 'w', encoding='utf-8').write(s)
print('✅ Module Récapitulatif branché sur les VRAIES données (accords + CAGD)')
print('🎯 Teste : http://127.0.0.1:5000/modules/recap.html')