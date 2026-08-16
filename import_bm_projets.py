# -*- coding: utf-8 -*-
import sys, re, unicodedata
from db import get_supabase

def norm(s):
    s = (s or '').lower()
    return ''.join(c for c in unicodedata.normalize('NFD', s) if unicodedata.category(c) != 'Mn')

sb = get_supabase()
allrows = sb.table('accords_consolides').select('code_projet, objet_accord, partenaire').execute().data or []
pool = [r for r in allrows if '-BM-' in (r['code_projet'] or '').upper() or 'mondiale' in norm(r['partenaire'])]

USD = 600  # taux estimatif FCFA/USD pour les montants insérés

# (nom, secteur, approche, montant_MUSD, mise_en_vigueur, taux, clôture, règles)
P = [
 ("BRIC","Cadre de vie","PforR",200,"2023-03-13",50.19,"2028-06-30",[(["bric"],[])]),
 ("Gbéssoké","Protection sociale","PforR",100,"2023-07-10",44.48,"2027-12-31",[(["gbessoke"],[])]),
 ("Terra Bénin","Agriculture","PforR",100,"2025-12-22",36.32,"2030-09-30",[(["terra"],[])]),
 ("FP2E","Enseignement et formation professionnelle","Projet",300,"2022-05-27",44.00,"2027-03-31",[(["fp2e"],[]),(["formation professionnelle","entrepreneuriat"],[])]),
 ("PACOFIDE","Agriculture","Projet",310,"2020-10-22",59.31,"2030-04-30",[(["pacofide"],[])]),
 ("P2AE","Énergie","Projet",200,"2021-11-23",55.60,"2026-12-31",[(["p2ae"],[])]),
 ("ProDIJ","Entrepreneuriat","Projet",101.3,"2021-03-31",78.28,"2027-06-30",[(["prodij"],[]),(["inclusion des jeunes"],[])]),
 ("Dorsale Nord","Énergie","Projet",30.4,"2019-04-01",77.39,"2026-12-01",[(["dorsale"],[])]),
 ("PFC1","Environnement","Projet",90.1,"2019-10-01",93.20,"2026-11-30",[(["pfc1"],[]),(["forets classees","benin 1"],[])]),
 ("PFC2","Environnement","Projet",80.7,"2025-09-09",2.95,"2032-07-31",[(["pfc2"],[]),(["forets classees","benin 2"],[])]),
 ("PMUD-GN","Cadre de vie","Projet",200,"2025-12-18",11.62,"2030-12-31",[(["pmud"],[]),(["mobilite urbaine"],[])]),
 ("WACA+","Environnement","Projet",147,None,None,"2031-11-26",[(["waca"],[])]),
 ("PHASAOC","Gouvernance","Projet",30,"2023-09-29",20.11,"2028-12-15",[(["phasaoc"],[]),(["statistiques"],[])]),
]

def trouver(regles):
    for req, excl in regles:
        cands = []
        for r in pool:
            t = norm((r['objet_accord'] or '')) + ' | ' + norm((r['code_projet'] or ''))
            if all(k in t for k in req) and not any(k in t for k in excl):
                cands.append(r)
        if len(cands) == 1: return cands[0]
        if len(cands) > 1: return ('AMBIGU', cands)
    return None

APPLY = 'apply' in sys.argv
nums = []
for r0 in allrows:
    m = re.match(r'P-(\d+)-', r0['code_projet'] or '')
    if m: nums.append(int(m.group(1)))
nextn = (max(nums) + 1) if nums else 760

up, ins = 0, 0
for p in P:
    nom, sect, appr, musd, mev, taux, clot, regles = p
    m = trouver(regles)
    payload = {'secteur_detaille': sect, 'approche': appr, 'moa': 'publique', 'date_mise_vigueur': mev, 'date_cloture': clot, 'taux_decaissement': taux, 'nature_financement': 'Crédit IDA' if appr == 'Projet' else 'PforR'}
    if m and not isinstance(m, tuple):
        print(f"✅ UPDATE {nom} -> {m['code_projet']} | {(m['objet_accord'] or '')[:50]}")
        if APPLY:
            sb.table('accords_consolides').update(payload).eq('code_projet', m['code_projet']).execute(); up += 1
    elif isinstance(m, tuple):
        print(f"⚠️ AMBIGU {nom} -> {[c['code_projet'] for c in m[1]]}")
    else:
        code = f"P-{nextn:04d}-BM-2026"; nextn += 1
        print(f"➕ INSERT {nom} (absent) -> {code}")
        if APPLY:
            payload.update({'code_projet': code, 'objet_accord': nom, 'partenaire': 'Banque mondiale', 'secteur_principal': sect, 'montant_total_fcfa': int(musd * 1_000_000 * USD), 'statut': 'En cours'})
            try:
                sb.table('accords_consolides').insert(payload).execute(); ins += 1
            except Exception as e:
                print(f"❌ {code}: {e}")

print(f"\n📊 Mode {'APPLY' if APPLY else 'APERÇU'} : {up} updates, {ins} inserts.")
if not APPLY: print("👉 Vérifie, puis : python import_bm_projets.py apply")
