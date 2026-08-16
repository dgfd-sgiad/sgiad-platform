import os
t = open('app.py', encoding='utf-8').read()
q = chr(34)*3
a = t.find('HTML = r'+q) + len('HTML = r'+q)
b = t.find(q, a)
html = t[a:b]

js = open('new_script.js', encoding='utf-8').read()
js = js.replace('PAGE=1,TAILLE=10', 'PAGE=1,TAILLE=5')
layout = ('window.addEventListener("load",function(){'
 'var t=document.querySelector(".table-head");var se=document.getElementById("search");'
 'var fb=document.querySelector(".filter-btn");var eb=document.querySelector(".export-btn");'
 'if(!t||!se)return;'
 't.style.cssText="display:flex;align-items:center;justify-content:space-between;flex-wrap:wrap;gap:12px;margin-bottom:12px";'
 'var g=document.createElement("div");g.className="reco-tools";'
 'if(!document.getElementById("filter-instrument")){var sl=document.createElement("select");sl.id="filter-instrument";sl.onchange=renderTable;'
 '[["","Instrument : Tous"],["IPF","IPF"],["PforR","PforR"]].forEach(function(o){var op=document.createElement("option");op.value=o[0];op.textContent=o[1];sl.appendChild(op);});g.appendChild(sl);}'
 'g.appendChild(se);if(fb)g.appendChild(fb);if(eb)g.appendChild(eb);t.appendChild(g);'
 '});')
open('modules/suivi_recos.js', 'w', encoding='utf-8').write(js + '\n' + layout + '\n')

tags = '<script src="/assets/suivi_recos.js?v=10"></script>'
if os.path.exists('print_fix.js'):
    open('modules/suivi_print.js', 'w', encoding='utf-8').write(open('print_fix.js', encoding='utf-8').read())
    tags += '<script src="/assets/suivi_print.js?v=10"></script>'
    print('print_fix integre (paysage A4/A3)')

css = ('<style>'
 'table{width:100%!important;min-width:0!important;table-layout:auto!important}'
 'th{font-size:10px!important;padding:10px 8px!important;white-space:normal!important}'
 'td{font-size:12px!important;padding:10px 8px!important;line-height:1.45!important;word-break:break-word}'
 'td:nth-child(13){white-space:nowrap;width:70px}'
 '.pagination{font-size:13px!important}'
 '.pagination .pages span{font-size:13px!important;min-width:28px;height:28px;display:inline-flex;align-items:center;justify-content:center;border-radius:4px}'
 '.filters{flex-wrap:wrap!important;gap:8px!important}'
 '.filters .fbox{min-width:140px;flex:1}'
 '.table-title{white-space:nowrap!important;font-weight:800!important;letter-spacing:.3px}'
 '.reco-tools{display:flex;gap:10px;align-items:center;flex:1;justify-content:flex-end;margin-right:45px;min-width:340px}'
 '#filter-instrument{height:40px;border:1px solid #d7deea!important;border-radius:8px;padding:0 10px;font-size:12px;font-weight:700;color:#33415a;background:#f8fafc;outline:none}'
 '#search{height:40px!important;flex:1;max-width:300px;border:1px solid #d7deea!important;border-radius:8px!important;padding:0 14px!important;font-size:13px!important;color:#33415a;background:#f8fafc;outline:none}'
 '#search:focus{border-color:#1260d9!important;background:#fff;box-shadow:0 0 0 3px rgba(18,96,217,.12)}'
 '.filter-btn{height:40px!important;padding:0 26px!important;border:none!important;border-radius:8px!important;background:#1260d9!important;color:#ffffff!important;font-size:13px!important;font-weight:800!important;letter-spacing:.4px;cursor:pointer;box-shadow:0 3px 10px rgba(18,96,217,.4)}'
 '.filter-btn:hover{background:#0d4fa8!important}'
 '.export-btn{height:40px!important;padding:0 20px!important;border:2px solid #1260d9!important;border-radius:8px!important;background:#ffffff!important;color:#1260d9!important;font-size:13px!important;font-weight:800!important;cursor:pointer}'
 '.export-btn:hover{background:#eaf2fd!important}'
 '</style>')

i = html.find('<script>')
j = html.find('</script>')
if i != -1 and j != -1:
    html = html[:i] + html[j+9:]

html = html.replace('<option>10</option>', '<option>5</option>')
html = html.replace('</body>', css + tags + '</body>')
open('modules/suivi_recos.html', 'w', encoding='utf-8').write(html)
v = open('modules/suivi_recos.html', encoding='utf-8').read()
print('HTML final -> <script :', v.count('<script'), '| </script> :', v.count('</script>'))