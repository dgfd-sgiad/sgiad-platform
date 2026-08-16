import re
h = open('print_fix.js', encoding='utf-8').read()
m = re.search(r"if\(!curc\)\{.*?first=false; \}", h)
if m:
    new = "if(!curc){ curc=(first?'<h2>'+esc(proj)+'</h2>'+(pInfo(proj)?'<div class=\"pinfo\">'+pInfo(proj)+'</div>':''):'<h2>'+esc(proj)+' — suite</h2>')+TH; curm=(first&&pInfo(proj))?23:18; first=false; }"
    h = h[:m.start()] + new + h[m.end():]
    open('print_fix.js', 'w', encoding='utf-8').write(h)
    print('OK, ligne projet modifiee : pInfo insere sous chaque titre')
else:
    print('ERREUR : ligne if(!curc) introuvable')