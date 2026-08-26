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

def sigles(s):
    out = set()
    for m in re.findall(r'\(([A-Za-z0-9\- ]{3,})\)', str(s or '')):
        out.add(norm(m).strip())
    for w in norm(s).split():
        if len(w) >= 4 and w not in STOP:
            out.add(w)
    return out

def nums(s):
    return set(re.findall(r'\b\d{3,4}\b', str(s or '')))

def score(nom, accord):
    ta, tb = tokens(nom), tokens(accord.get('objet_accord') or '')
    if not ta or not tb:
        return 0.0
    base = len(ta & tb) / min(len(ta), len(tb))
    if sigles(nom) & sigles(accord.get('objet_accord') or ''):
        base += 0.3
    if nums(nom) & nums(accord.get('objet_accord') or ''):
        base += 0.15
    return base

# 1) Liste stricte des "manquants" (comme l'audit précédent)
obj_accords = [(norm(a.get('objet_accord')), sigles(a.get('objet_accord'))) for a in accords]
def strict_found(nom):
    n = norm(nom)
    sg = [g for g in sigles(nom) if len(g) >= 4]
    for on, osg in obj_accords:
        if any(g in on for g in sg):
            return True
        if n and on and (n[:25] in on or on[:25] in n):
            return True
    return False

manquants = [c for c in cagd if c['periode'] == '2025' and not strict_found(c['projet'])]

print('=' * 95)
print(f'COMPARAISON INVERSÉE : {len(manquants)} projets "manquants" recherchés en flou dans la banque')
print('=' * 95)
ex, ver, absents = [], [], []
for c in manquants:
    nom = c['projet']
    ranked = sorted(accords, key=lambda a: score(nom, a), reverse=True)[:1]
    best, s0 = ranked[0], score(nom, ranked[0])
    print(f"\n{str(c['partenaire'])[:10]:10s} {float(c['montant_total_fcfa'] or 0):>16,.0f}  {nom[:65]}")
    if s0 >= 0.45:
        ex.append(nom)
        print(f'   ✅ EXISTE sous un autre nom (score {s0:.2f}) → {best["code_projet"]} : {str(best["objet_accord"])[:70]}')
    elif s0 >= 0.25:
        ver.append(nom)
        print(f'   ⚠️  À VÉRIFIER (score {s0:.2f}) → {best["code_projet"]} : {str(best["objet_accord"])[:70]}')
    else:
        absents.append(nom)
        print(f'   ❌ VRAIMENT ABSENT (meilleur score {s0:.2f})')

print('\n' + '=' * 95)
print(f'SYNTHÈSE : {len(manquants)} "manquants" → {len(ex)} existent déjà · {len(ver)} à vérifier · {len(absents)} VRAIMENT ABSENTS')
print('=' * 95)
for n in absents:
    print('   →', n[:80])
    