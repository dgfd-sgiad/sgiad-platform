# -*- coding: utf-8 -*-
import re, glob

files = glob.glob('modules/*.html') + glob.glob('*.html') + glob.glob('js/*.js')

CIBLES = [
'/api/accords-financiers/add','/api/accords-financiers/delete','/api/accords-financiers/export','/api/accords-financiers/import','/api/accords-financiers/update',
'/api/accords/add','/api/accords/avenants','/api/accords/commissions','/api/accords/decaissements','/api/accords/delete','/api/accords/export','/api/accords/import','/api/accords/parametres','/api/accords/suivi','/api/accords/update',
'/api/accueil/login','/api/admin/users/delete','/api/admin/users/reset','/api/auth','/api/auth/signup',
'/api/banque/documents','/api/banque/documents/upload','/api/banque/parametres/add','/api/banque/parametres/delete','/api/banque/parametres/update','/api/banque/secteur_sous_secteur/add','/api/banque/secteur_sous_secteur/delete',
'/api/conges/nouvelle_annee','/api/coop_dec/delete','/api/coop_dec/export',
'/api/suivi/recommandations/commenter','/api/suivi/recommandations/executer','/api/suivi/recommandations/historique','/api/suivi/recommandations/statut','/api/suivi/recommandations/update',
'/api/suivi/rejeter','/api/suivi/revues','/api/suivi/revues/annuler','/api/suivi/revues/executer','/api/suivi/revues/update','/api/suivi/valider',
'/api/veille/scan',
]

def urls_du_fichier(f):
    s = open(f, encoding='utf-8').read()
    urls = set()
    consts = {}
    for m in re.finditer(r"(?:const|let|var)\s+([A-Za-z_]+)\s*=\s*[`'\"][^`'\"]*?(/api/[A-Za-z0-9_\-/]+)", s):
        consts[m.group(1)] = m.group(2)
    for m in re.finditer(r"[`'\"](/api/[A-Za-z0-9_\-/]+)", s):
        urls.add(m.group(1))
    for m in re.finditer(r"origin\s*\+\s*[`'\"]?(/api/[A-Za-z0-9_\-/]+)", s):
        urls.add(m.group(1))
    for name, base in consts.items():
        for m in re.finditer(r"\$\{" + re.escape(name) + r"\}([A-Za-z0-9_\-/]*)", s):
            urls.add(base + m.group(1))
    return urls

usage = {}
for f in files:
    try:
        us = urls_du_fichier(f)
    except Exception:
        continue
    for u in us:
        usage.setdefault(u.rstrip('/'), set()).add(f)

print("=== AUDIT D'USAGE DES ROUTES CASSÉES ===")
for c in CIBLES:
    cc = c.rstrip('/')
    callers = set()
    for u, fs in usage.items():
        if u == cc or u.startswith(cc + '/'):
            callers |= fs
    if not callers:
        for u, fs in usage.items():
            if cc.startswith(u + '/') and u.count('/') >= 3:
                callers |= fs
    if callers:
        print(f"✅ UTILISÉE   {c}  ->  {', '.join(sorted(callers))}")
    else:
        print(f"🗑️  ABANDONNÉE {c}")
        