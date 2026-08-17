import re

# --- 1) accueil.html : oeil + mot de passe oublie sur le modal ---
h = open('accueil.html', encoding='utf-8').read()
mod = False
pos = h.find('login-id')
m = re.search(r'<input[^>]*type=["\']password["\'][^>]*>', h[pos:] if pos >= 0 else h)
if m and 'eye-btn' not in h:
    tag = m.group(0)
    btn = ('<button type="button" id="eye-btn" onclick="var p=this.previousElementSibling;if(p.type===\'password\'){p.type=\'text\';this.textContent=\'🙈\';}else{p.type=\'password\';this.textContent=\'👁️\';}" '
           'style="position:absolute;right:10px;top:50%;transform:translateY(-50%);border:none;background:none;cursor:pointer;font-size:16px">👁️</button>')
    h = h.replace(tag, '<div style="position:relative">' + tag + btn + '</div>', 1)
    mod = True
    print('OK: oeil ajoute sur le modal de connexion')

if 'mdpOublie' not in h:
    i = h.find('eye-btn')
    if i >= 0:
        j = h.find('</div>', i)
        link = '\n                <div style="text-align:right;margin:6px 0 2px"><a href="#" onclick="mdpOublie();return false;" style="font-size:12px;color:#1e5aa8;text-decoration:none;font-weight:600">Mot de passe oublié ?</a></div>'
        h = h[:j+6] + link + h[j+6:]
    fn = ("\nfunction mdpOublie(){\n  var em = prompt('Entrez votre adresse email professionnelle :', (document.getElementById('login-id')||{}).value || '');\n"
          "  if(!em) return;\n"
          "  alert('Demande de réinitialisation enregistrée pour ' + em + '.\\nVeuillez contacter le superviseur de la plateforme (Pôle de Suivi MEF) pour obtenir un nouveau mot de passe.');\n}\n")
    k = h.rfind('</script>')
    if k >= 0:
        h = h[:k] + fn + h[k:]
    mod = True
    print('OK: lien + fonction mot de passe oublie ajoutes')

if mod:
    open('accueil.html', 'w', encoding='utf-8').write(h)
    print('accueil.html mis a jour')
else:
    print('accueil.html: deja en place ou structure introuvable')

# --- 2) api.py : /login redirige vers l'accueil ---
a = open('api.py', encoding='utf-8').read()
if '/login' not in a.split('@app.route')[-1] and "'/login')" not in a:
    route = ("\n@app.route('/login')\n"
             "def login_redirect():\n"
             "    from flask import redirect\n"
             "    return redirect('/')\n\n")
    k = a.rfind('if __name__')
    if k < 0: k = len(a)
    a = a[:k] + route + a[k:]
    open('api.py', 'w', encoding='utf-8').write(a)
    print('OK: route /login -> redirection accueil')
else:
    print('api.py: route /login deja presente')
    