# -*- coding: utf-8 -*-
import sys, re, unicodedata
from db import get_supabase

def norm(s):
    s = (s or '').lower()
    return ''.join(c for c in unicodedata.normalize('NFD', s) if unicodedata.category(c) != 'Mn')

sb = get_supabase()
allrows = sb.table('accords_consolides').select('code_projet, objet_accord, partenaire').execute().data or []
pool = [r for r in allrows if '-AFD-' in (r['code_projet'] or '').upper() or 'afd' in norm(r['partenaire']) or 'francaise' in norm(r['partenaire'])]

# (nom PDF, secteur, nature, approbation, clôture, prêt, don, approche, moa, taux, règles)
P = [
 ("BESS 5 MW","Énergie","Prêt","2017-04-10","2028-07-31",4623000000,0,"Projet","publique",0.00,[(["bess","5"],[]),(["bess"],[])]),
 ("FORSUN Distribution","Énergie","Prêt","2021-12-22","2027-03-20",14004681950,0,"Projet","publique",2.45,[(["forsun","distribution"],[]),(["distribution","hp"],[])]),
 ("FORSUN Solaire","Énergie","Prêt","2021-12-22","2027-03-20",8953813050,0,"Projet","publique",16.98,[(["forsun","solaire"],[]),(["forsun","centrale"],[]),(["forsun"],[])]),
 ("DEFISSOL SI","Gouvernance","Prêt","2017-04-10","2028-07-31",12574695690,0,"Projet","publique",78.00,[(["defissol","systeme"],[]),(["defissol","information"],[]),(["defissol","si"],[])]),
 ("DEFISSOL Solaire (centrale 25 MW Pobè)","Énergie","Prêt","2017-04-10","2028-07-31",20223154310,0,"Projet","publique",91.00,[(["defissol","pobe"],[]),(["defissol","centrale"],[]),(["defissol","solaire"],[]),(["defissol"],[])]),
 ("PEDER","Énergie","Prêt","2019-07-24","2026-11-30",26238280000,0,"Projet","publique",100.00,[(["peder"],[])]),
 ("PAVICC","Cadre de vie","Prêt+Don","2018-03-05","2026-12-31",32797850000,5247656000,"Projet","publique",100.00,[(["pavicc"],[]),(["villes","climat"],[])]),
 ("Réinventer Ganvié","Cadre de vie","Prêt+Don","2019-09-26","2027-12-31",22630516500,2295849500,"Projet","publique",37.53,[(["ganvie"],[])]),
 ("DEFI-Pro","Enseignement et formation professionnelle","Prêt+Don","2017-06-10","2026-12-31",13119140000,1967871000,"Projet","publique",43.56,[(["defi-pro"],[]),(["enseignement technique"],[])]),
 ("ProFAR 1","Enseignement et formation professionnelle","Prêt+Don","2021-12-22","2027-06-20",9839355000,3279785000,"Projet","publique",18.07,[(["profar1"],[]),(["profar 1"],[]),(["pro-far 1"],[])]),
 ("ProFAR 2","Enseignement et formation professionnelle","Prêt","2023-03-30","2027-12-20",19678710000,0,"Projet","publique",9.17,[(["pro-far 2"],[]),(["profar 2"],[]),(["profar2"],[])]),
 ("ProFAR 3 + PCT","Enseignement et formation professionnelle","Prêt+Don","2023-11-27","2027-11-24",45916990000,1967871000,"Appui budgétaire+PCT","publique",66.44,[(["pro-far 3"],[]),(["profar 3"],[]),(["profar3"],[]),(["profar","budgetaire"],[])]),
 ("Musée des Amazones / Site Palatial","Tourisme et culture","Prêt+Don","2021-04-09","2026-12-31",16398925000,6559570000,"Projet","publique",24.81,[(["amazones"],[])]),
 ("MACC","Tourisme et culture","Prêt+Don","2025-05-27","2030-12-31",16398925000,3279785000,"Projet","publique",0.00,[(["macc"],[]),(["art contemporain"],[])]),
 ("FBPP Culture + PCT","Tourisme et culture","Prêt+Don","2025-10-06","2030-01-01",36077635000,3279785000,"Appui budgétaire+PCT","publique",63.64,[(["fbpp"],[]),(["culture"],[])]),
 ("PADIAP","Agriculture","Prêt+Don","2023-07-05","2029-12-31",16398925000,2820615100,"Projet","publique",22.00,[(["padiap"],[])]),
 ("TAZCO 2","Agriculture","Don+Avenant","2020-04-15","2028-06-30",0,9839355000,"Projet","publique",43.00,[(["tazco 2"],[]),(["tazco2"],[]),(["tazco"],[])]),
 ("PAMSI","Gouvernance","Prêt","2022-11-14","2026-12-31",2636088492,0,"Projet","publique",68.00,[(["pamsi"],[])]),
 ("PAEB","Entrepreneuriat","Prêt+Don","2022-07-27","2028-01-27",9839355000,6559570000,"Projet","publique",26.00,[(["paeb"],[])]),
 ("PRPCB","Sécurité publique","Don","2025-07-18","2029-07-18",0,5247656000,"Projet","publique",1.25,[(["prpc"],[]),(["protection civile"],[])]),
 ("PASOA","Agriculture","Don","2023-04-06","2027-04-06",0,7871484000,"Projet","privée",23.91,[(["pasoa"],[])]),
 ("PRICS","Enseignement et formation professionnelle","Don","2025-03-15","2029-03-15",0,5641230200,"Projet","privée",23.25,[(["prics"],[]),(["cohesion"],[])]),
 ("Equité 2","Santé","Don","2024-03-20","2029-03-20",0,9839355000,"Projet","privée",0.00,[(["equite"],[])]),
]

def trouver(regles):
    for req, excl in regles:
        cands = []
        for r in pool:
            t = norm((r['objet_accord'] or '')) + ' | ' + norm((r['code_projet'] or ''))
            if all(k in t for k in req) and not any(k in t for k in excl):
                cands.append(r)
        if len(cands) == 1:
            return cands[0]
        if len(cands) > 1:
            return ('AMBIGU', cands)
    return None

APPLY = 'apply' in sys.argv
if APPLY:
    for bad in ('P-0273-BM-2023', 'P-0406-UE-2020'):
        sb.table('accords_consolides').update({'date_approbation': None, 'nature_financement': None, 'montant_pret_fcfa': None, 'montant_don_fcfa': None, 'approche': None, 'moa': None, 'taux_decaissement': None, 'secteur_detaille': None}).eq('code_projet', bad).execute()
    print('🧹 Rollback GBESSOKE + FORSUN-UE fait.')

nums = []
for r0 in allrows:
    m = re.match(r'P-(\d+)-', r0['code_projet'] or '')
    if m: nums.append(int(m.group(1)))
nextn = (max(nums) + 1) if nums else 700

updates, inserts = 0, 0
for p in P:
    nom, secteur, nature, appr, clot, pret, don, approche, moa, taux, regles = p
    m = trouver(regles)
    payload = {'date_approbation': appr, 'nature_financement': nature, 'montant_pret_fcfa': pret, 'montant_don_fcfa': don, 'approche': approche, 'moa': moa, 'taux_decaissement': taux, 'secteur_detaille': secteur}
    if m and not isinstance(m, tuple):
        print(f"✅ UPDATE {nom} -> {m['code_projet']} | {(m['objet_accord'] or '')[:50]}")
        if APPLY:
            sb.table('accords_consolides').update(payload).eq('code_projet', m['code_projet']).execute()
            updates += 1
    elif isinstance(m, tuple):
        print(f"⚠️ AMBIGU {nom} -> {[c['code_projet'] for c in m[1]]}")
    else:
        code = f"P-{nextn:04d}-AFD-2026"
        nextn += 1
        print(f"➕ INSERT {nom} (absent de la base) -> {code}")
        if APPLY:
            payload.update({'code_projet': code, 'objet_accord': nom, 'partenaire': 'Agence Française de Développement', 'secteur_principal': secteur, 'montant_total_fcfa': pret + don, 'statut': 'En cours', 'date_cloture': clot})
            try:
                sb.table('accords_consolides').insert(payload).execute()
                inserts += 1
            except Exception as e:
                print(f"❌ Erreur insert {code}: {e}")

print(f"\n📊 Mode {'APPLY' if APPLY else 'APERÇU'} : {updates} updates, {inserts} inserts.")
if not APPLY:
    print("👉 Vérifie ce mapping, puis lance : python import_afd3.py apply")
    