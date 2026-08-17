h = open('modules/login.html', encoding='utf-8').read()
mod = False

inp = '<input type="password" id="password" placeholder="Votre mot de passe" required minlength="6">'
if inp in h and 'eye-btn' not in h:
    bloc = ('<div style="position:relative">'
            '<input type="password" id="password" placeholder="Votre mot de passe" required minlength="6" style="width:100%;padding-right:40px">'
            '<button type="button" id="eye-btn" onclick="var p=document.getElementById(\'password\');if(p.type===\'password\'){p.type=\'text\';this.textContent=\'🙈\';}else{p.type=\'password\';this.textContent=\'👁️\';}" style="position:absolute;right:10px;top:50%;transform:translateY(-50%);border:none;background:none;cursor:pointer;font-size:16px">👁️</button>'
            '</div>'
            '<div style="text-align:right;margin:6px 0 2px"><a href="#" onclick="mdpOublie();return false;" style="font-size:12px;color:#1e5aa8;text-decoration:none;font-weight:600">Mot de passe oublié ?</a></div>')
    h = h.replace(inp, bloc)
    mod = True
    print('OK: oeil + lien mot de passe oublie ajoutes')

if 'function mdpOublie' not in h:
    fn = ("\nfunction mdpOublie(){\n"
          "  var em = prompt('Entrez votre adresse email professionnelle :');\n"
          "  if(!em) return;\n"
          "  alert('Demande de réinitialisation enregistrée pour ' + em + '.\\nVeuillez contacter le superviseur de la plateforme (Pôle de Suivi MEF) pour obtenir un nouveau mot de passe.');\n"
          "}\n")
    i = h.rfind('</script>')
    if i >= 0:
        h = h[:i] + fn + h[i:]
        mod = True
        print('OK: fonction mdpOublie ajoutee')

if mod:
    open('modules/login.html', 'w', encoding='utf-8').write(h)
    print('login.html mis a jour')
else:
    print('Rien a modifier ou structure differente -> envoie-moi les lignes autour du champ password')
    