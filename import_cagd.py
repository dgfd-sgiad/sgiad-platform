# -*- coding: utf-8 -*-
import re
from db import get_supabase

sb = get_supabase()
FICHIER = 'data/cagd_decaissements.txt'

def num(s):
    s = (s or '').strip().replace(' ', '').replace('\u00a0', '')
    if s in ('', '-', 'NA'):
        return 0
    try:
        return int(float(s))
    except Exception:
        return 0

def dclean(s):
    s = (s or '').strip()
    return s if s and s not in ('NA', '-') else None

lignes = open(FICHIER, encoding='utf-8').read().splitlines()
batch, total, par_annee = [], 0, {}

for an in ['2022','2023','2024','2025','2026']:
    sb.table('decaissements_cagd').delete().eq('periode', an).execute()

for l in lignes:
    cols = [c.strip() for c in l.split('\t')]
    if len(cols) < 12:
        continue
    annee = cols[1]
    if not re.match(r'^202[2-6]$', annee):
        continue
    intitule = cols[2]
    if not intitule or len(intitule) < 5:
        continue
    batch.append({
        'periode': annee,
        'projet': intitule,
        'date_demarrage': dclean(cols[3]),
        'date_cloture': dclean(cols[4]),
        'tutelle': cols[5],
        'partenaire': cols[6],
        'type_bailleur': cols[7],
        'montant_pret_fcfa': num(cols[8]),
        'montant_don_fcfa': num(cols[9]),
        'montant_total_fcfa': num(cols[10]),
        'secteur': cols[11],
    })
    par_annee[annee] = par_annee.get(annee, 0) + 1
    if len(batch) >= 100:
        sb.table('decaissements_cagd').insert(batch).execute()
        total += len(batch); batch = []

if batch:
    sb.table('decaissements_cagd').insert(batch).execute()
    total += len(batch)

print(f'✅ {total} lignes importées dans decaissements_cagd')
print(par_annee)
