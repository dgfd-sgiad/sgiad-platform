# -*- coding: utf-8 -*-
import re, requests

BASE = 'http://127.0.0.1:5000'
accords = requests.get(BASE + '/api/accords/list', timeout=30).json()
cagd = requests.get(BASE + '/api/decaissements/cagd', timeout=30).json()

def norm(s):
    s = str(s or '').upper()
    for a, b in {'É':'E','È':'E','Ê':'E','À':'A','Â':'A','Î':'I','Ô':'O','Ù':'U','Û':'U','Ç':'C'}.items():
        s = s.replace(a, b)
    return re.sub(r'[^A-Z0-9 ]', ' ', s)

STOP = {'DE','DU','DES','LA','LE','LES','AU','AUX','EN','POUR','ET','SUR','DANS','PAR','AVEC','PROJET','BENIN','D','L','A'}
def tokens(s):
    return set(w for w in norm(s).split() if len(w) >= 3 and w not in STOP)

def sigle_par(s):
    m = re.search(r'\(([A-Za-z0-9\- ]{3,})\)', str(s or ''))
    return norm(m.group(1)).strip() if m else ''

def nums(s):
    return set(re.findall(r'\b\d{3,4}\b', str(s or '')))

obj_accords = [(norm(a.get('objet_accord')), sigle_par(a.get('objet_accord'))) for a in accords]

def strict_found(nom):
    n = norm(nom)
    sg = sigle_par(nom)
    for on, osg in obj_accords:
        if sg and len(sg) >= 4 and sg in on:
            return True
        if n and on and (n[:25] in on or on[:25] in n):
            return True
    return False

manquants = [c for c in cagd if c['periode'] == '2025' and not strict_found(c['projet'])]

def score(nom, accord):
    obj = accord.get('objet_accord') or ''
    ta, tb = tokens(nom), tokens(obj)
    if not ta or not tb:
        return 0.0
    base = len(ta & tb) / min(len(ta), len(tb))
    sg, og = sigle_par(nom), sigle_par(obj)
    if sg and og and (sg in og or og in sg):
        base += 0.3
    if nums(nom) & nums(obj):
        base += 0.15
    return base

print('=' * 95)
print(f'COMPARAISON INVERSÉE (corrigée) : {len(manquants)} projets "manquants" analysés')
print('=' * 95)
ex, ver, absents = [], [], []
for c in manquants:
    nom = c['projet']
    best = max(accords, key=lambda a: score(nom, a))
    s0 = score(nom, best)
    print(f"\n{str(c['partenaire'])[:10]:10s} {float(c['montant_total_fcfa'] or 0):>16,.0f}  {nom[:65]}")
    if s0 >= 0.45:
        ex.append(nom)
        print(f'   ✅ EXISTE sous un autre nom (score {s0:.2f}) → {best["code_projet"]} : {str(best["objet_accord"])[:70]}')
    elif s0 >= 0.25:
        ver.append(nom)
        print(f'   ⚠️  À VÉRIFIER (score {s0:.2f}) → {best["code_projet"]} : {str(best["objet_accord"])[:70]}')
    else:
        absents.append(nom)
        print(f'   ❌ VRAIMENT ABSENT (score {s0:.2f})')

print('\n' + '=' * 95)
print(f'SYNTHÈSE : {len(manquants)} "manquants" → {len(ex)} existent déjà · {len(ver)} à vérifier · {len(absents)} VRAIMENT ABSENTS')
print('=' * 95)
for n in absents:
    print('   →', n[:80])
    