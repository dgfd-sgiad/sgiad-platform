# -*- coding: utf-8 -*-
p = 'modules/recos.html'
s = open(p, encoding='utf-8').read()

hook = """<script>
/* correctif expert : garantit le rendu de "Nature des blocages" (#c-th) */
(function(){
  if (typeof chartThemes !== 'function') { console.warn('[fix] chartThemes absent'); return; }
  var _ct = chartThemes;
  function kwTheme(r){
    var t = (r.lb||r.txt||'') + ' ' + (r.nom||'');
    if (/passation|mach\\u00e9|marche|ami|appel d.offres|commission/i.test(t)) return 0;
    if (/contrepartie|budget|fonds propres/i.test(t)) return 1;
    if (/justificatif|drf|rapport|pi\\u00e8ce|piece/i.test(t)) return 2;
    if (/non.objection|ano/i.test(t)) return 3;
    if (/foncier|terrain|parcelle|indemnis|relogement/i.test(t)) return 4;
    if (/audit|contr\\u00f4le|controle/i.test(t)) return 5;
    return 6;
  }
  chartThemes = function(rows){
    if (rows && rows.length && rows.every(function(r){ return r.th == null; })) {
      rows = rows.map(function(r){ var c = {}; for (var k in r) c[k] = r[k]; c.th = kwTheme(r); return c; });
    }
    var n = 0;
    (function tryIt(){
      var el = document.getElementById('c-th');
      if (el) { _ct(rows); }
      else if (n++ < 12) { setTimeout(tryIt, 60); }
    })();
  };
  function ensure(){
    var el = document.getElementById('c-th');
    if (el && window.echarts && !echarts.getInstanceByDom(el)) {
      var rows = (window.D && D.recos ? D.recos : []).filter(function(r){
        return state.sec.has(r.s) && state.par.has(r.p) && state.st.has(r.st);
      });
      chartThemes(rows);
    }
  }
  if (typeof render === 'function') {
    var _r = render;
    render = function(){ var o = _r.apply(this, arguments); setTimeout(ensure, 90); return o; };
  }
  document.addEventListener('click', function(){ setTimeout(ensure, 150); }, true);
  addEventListener('load', function(){ setTimeout(ensure, 150); });
})();
</script>"""

if 'correctif expert' in s:
    print('ℹ️ correctif déjà présent')
else:
    s = s.replace('</body>', hook + '\n</body>', 1)
    open(p, 'w', encoding='utf-8').write(s)
    print('✅ correctif #c-th installé (re-dessin auto après chaque render/clic)')

print('🎯 Ctrl + F5 sur /modules/recos.html')
