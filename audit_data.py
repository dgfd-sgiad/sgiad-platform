# -*- coding: utf-8 -*-
import re, requests
from collections import defaultdict

BASE = 'http://127.0.0.1:5000'
accords = requests.get(BASE + '/api/accords/list', timeout=30).json()
cagd = requests.get(BASE + '/api/decaissements/cagd', timeout=30).json()

def norm(s):
    return re.sub(r'[^A-Z0-9 ]', '', str(s or '').upper())

def sigle(nom):
    m = re.search(r'\(([A-Z0-9\- ]{3,})\)', norm(nom))
    return m.group(1).strip() if m else ''

print('=' * 70)
print(f'A. COMPLÉTUDE DES {len(accords)} ACCORDS (accords_consolides)')
print('=' * 70)
champs = ['code_projet', 'objet_accord', 'partenaire', 'secteur_principal', 'montant_total_fcfa', 'date_cloture', 'statut']
for c in champs:
    vide = sum(1 for a in accords if not str(a.get(c) or '').strip() or str(a.get(c)) in ('0', '0.0'))
    print(f'{c:22s} : {len(accords) - vide:4d} renseignés / {vide:4d} manquants')

print()
print('=' * 70)
print('B. TOTAUX DÉCAISSEMENTS IMPORTÉS vs TOTAUX OFFICIELS RCD')
print('=' * 70)
OFFICIEL = {'2023': 923011745883, '2024': 969731182680, '2025': 1053447604512, '2026': 653754378735}
tot = defaultdict(float)
for c in cagd:
    tot[c['periode']] += float(c['montant_total_fcfa'] or 0)
for an, off in OFFICIEL.items():
    cal = tot.get(an, 0)
    ecart = cal - off
    print(f"{an} : importé {cal:,.0f} | officiel {off:,.0f} | {'✅ OK' if abs(ecart) < 1 else '❌ écart ' + f'{ecart:,.0f}'}")

print()
print('=' * 70)
print("C. PROJETS CAGD (2025) VRAIMENT ABSENTS DE LA BANQUE (score flou)")
print('=' * 70)
STOP = {'DE','DU','DES','LA','LE','LES','AU','AUX','EN','POUR','ET','SUR','DANS','PAR','AVEC','PROJET','BENIN','D','L','A'}
def tokens(s):
    return set(w for w in norm(s).split() if len(w) >= 3 and w not in STOP)
def sigle_par(s):
    m = re.search(r'\(([A-Za-z0-9\- ]{3,})\)', str(s or ''))
    return norm(m.group(1)).strip() if m else ''
def nums(s):
    return set(re.findall(r'\b\d{3,4}\b', str(s or '')))
def score(nom, accord):
    ta, tb = tokens(nom), tokens(accord.get('objet_accord') or '')
    if not ta or not tb: return 0.0
    base = len(ta & tb) / min(len(ta), len(tb))
    sg, og = sigle_par(nom), sigle_par(accord.get('objet_accord') or '')
    if sg and og and (sg in og or og in sg): base += 0.3
    if nums(nom) & nums(accord.get('objet_accord') or ''): base += 0.15
    return base
manquants = []
for c in cagd:
    if c['periode'] != '2025': continue
    best = max(accords, key=lambda a: score(c['projet'], a))
    s0 = score(c['projet'], best)
    if s0 < 0.45:
        manquants.append((c['projet'], float(c['montant_total_fcfa'] or 0), c['partenaire'], s0))
for nom, m, p, s in manquants:
    print(f'❌ {str(p)[:10]:10s} {m:>18,.0f}  score {s:.2f}  {nom[:65]}')
print(f'\n→ {len(manquants)} projet(s) CAGD 2025 VRAIMENT absents (les autres existent sous un nom différent)')

print()
print('=' * 70)
print('D. DOUBLONS CAGD (même projet + même année)')
print('=' * 70)
d = defaultdict(int)
for c in cagd:
    d[(c['periode'], norm(c['projet'])[:60])] += 1
dups = [(k, v) for k, v in d.items() if v > 1]
for (an, n), v in dups:
    print(f'⚠️ {an} x{v} : {n[:70]}')
print(f'→ {len(dups)} doublon(s)' if dups else '✅ aucun doublon')