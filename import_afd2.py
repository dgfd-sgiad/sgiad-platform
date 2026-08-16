# -*- coding: utf-8 -*-
import sys, unicodedata
from db import get_supabase

def norm(s):
    s = (s or '').lower()
    return ''.join(c for c in unicodedata.normalize('NFD', s) if unicodedata.category(c) != 'Mn')

sb = get_supabase()
rows = sb.table('accords_consolides').select('code_projet, objet_accord, partenaire').execute().data or []

# (nom PDF, secteur, nature, approbation, prêt, don, approche, moa, taux, règles [([mots requis],[mots exclus]), ...])
PROJETS = [
 ("BESS 5 MW","Énergie","Prêt","2017-04-10",4623000000,0,"Projet","publique",0.00, [(["bess"],[])]),
 ("FORSUN Distribution","Énergie","Prêt","2021-12-22",14004681950,0,"Projet","publique",2.45, [(["forsun","distribution"],[])]),
 ("FORSUN Solaire","Énergie","Prêt","2021-12-22",8953813050,0,"Projet","publique",16.98, [(["forsun","solaire"],[]),(["forsun"],["distribution"])]),
 ("DEFISSOL SI","Gouvernance","Prêt","2017-04-10",12574695690,0,"Projet","publique",78.00, [(["defissol","information"],[]),(["defissol","si"],[]),(["modernisation","sbee"],[])]),
 ("DEFISSOL Solaire (centrale 25 MW Pobè)","Énergie","Prêt","2017-04-10",20223154310,0,"Projet","publique",91.00, [(["pobe"],[]),(["centrale","25"],[]),(["defissol","solaire"],["bess"]),(["defissol"],["bess","information","si"])]),
 ("PEDER","Énergie","Prêt","2019-07-24",26238280000,0,"Projet","publique",100.00, [(["peder"],["+"]),(["densification"],[])]),
 ("PAVICC","Cadre de vie","Prêt+Don","2018-03-05",32797850000,5247656000,"Projet","publique",100.00, [(["pavicc"],[]),(["villes","climat"],[])]),
 ("Réinventer Ganvié","Cadre de vie","Prêt+Don","2019-09-26",22630516500,2295849500,"Projet","publique",37.53, [(["ganvie"],[])]),
 ("DEFI-Pro","Enseignement et formation professionnelle","Prêt+Don","2017-06-10",13119140000,1967871000,"Projet","publique",43.56, [(["defi-pro"],[]),(["enseignement technique"],[])]),
 ("ProFAR 1","Enseignement et formation professionnelle","Prêt+Don","2021-12-22",9839355000,3279785000,"Projet","publique",18.07, [(["profar 1"],[]),(["profar1"],[]),(["pro-far 1"],[]),(["profar","1"],[])]),
 ("ProFAR 2","Enseignement et formation professionnelle","Prêt","2023-03-30",19678710000,0,"Projet","publique",9.17, [(["profar 2"],[]),(["profar2"],[]),(["pro-far 2"],[]),(["profar","2"],[])]),
 ("ProFAR 3 + PCT","Enseignement et formation professionnelle","Prêt+Don","2023-11-27",45916990000,1967871000,"Appui budgétaire+PCT","publique",66.44, [(["profar 3"],[]),(["profar3"],[]),(["pro-far 3"],[]),(["profar","3"],[])]),
 ("Musée des Amazones / Site Palatial","Tourisme et culture","Prêt+Don","2021-04-09",16398925000,6559570000,"Projet","publique",24.81, [(["amazones"],[]),(["epopee"],[])]),
 ("MACC","Tourisme et culture","Prêt+Don","2025-05-27",16398925000,3279785000,"Projet","publique",0.00, [(["macc"],[]),(["art contemporain"],[])]),
 ("FBPP Culture + PCT","Tourisme et culture","Prêt+Don","2025-10-06",36077635000,3279785000,"Appui budgétaire+PCT","publique",63.64, [(["fbpp","culture"],[]),(["culture"],["macc","amazones","ganvie","musee"])]),
 ("PADIAP","Agriculture","Prêt+Don","2023-07-05",16398925000,2820615100,"Projet","publique",22.00, [(["padiap"],[])]),
 ("TAZCO 2","Agriculture","Don+Avenant","2020-04-15",0,9839355000,"Projet","publique",43.00, [(["tazco"],[]),(["agroecolog"],[])]),
 ("PAMSI","Gouvernance","Prêt","2022-11-14",2636088492,0,"Projet","publique",68.00, [(["pamsi"],[]),(["modernisation","dgi"],[])]),
 ("PAEB","Entrepreneuriat","Prêt+Don","2022-07-27",9839355000,6559570000,"Projet","publique",26.00, [(["paeb"],[]),(["entrepreneuriat"],[])]),
 ("PRPCB","Sécurité publique","Don","2025-07-18",0,5247656000,"Projet","publique",1.25, [(["prpc"],[]),(["protection civile"],[])]),
 ("PASOA","Agriculture","Don","2023-04-06",0,7871484000,"Projet","privée",23.91, [(["pasoa"],[]),(["savanes"],[])]),
 ("PRICS","Enseignement et formation professionnelle","Don","2025-03-15",0,5641230200,"Projet","privée",23.25, [(["prics"],[]),(["cohesion"],[])]),
 ("Equité 2","Santé","Don","2024-03-20",0,9839355000,"Projet","privée",0.00, [(["equite"],[])]),
]

def trouver(regles):
    global rows
    for req, excl in regles:
        cands = []
        for r in rows:
            t = norm((r['objet_accord'] or '')) + ' | ' + norm((r['code_projet'] or ''))
            if all(k in t for k in req) and not any(k in t for k in excl):
                cands.append(r)
        if len(cands) == 1:
            rows.remove(cands[0])
            return cands[0]
        if len(cands) > 1:
            return ('AMBIGU', cands)
    return None

APPLY = 'apply' in sys.argv
ok = 0
for p in PROJETS:
    nom, secteur, nature, appr, pret, don, approche, moa, taux, regles = p
    m = trouver(regles)
    if m is None:
        print(f"❌ NON TROUVÉ : {nom}")
        continue
    if isinstance(m, tuple):
        print(f"⚠️ AMBIGU : {nom} -> {[c['code_projet'] for c in m[1]]}")
        continue
    print(f"✅ {nom}  ->  {m['code_projet']} | {(m['objet_accord'] or '')[:60]}")
    if APPLY:
        payload = {
            'date_approbation': appr, 'nature_financement': nature,
            'montant_pret_fcfa': pret, 'montant_don_fcfa': don,
            'approche': approche, 'moa': moa,
            'taux_decaissement': taux, 'secteur_detaille': secteur,
        }
        sb.table('accords_consolides').update(payload).eq('code_projet', m['code_projet']).execute()
        ok += 1

if APPLY:
    print(f"\n📊 {ok} projets AFD mis à jour.")
else:
    print("\n👉 Vérifie le mapping ci-dessus, puis lance : python import_afd2.py apply")