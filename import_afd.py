from db import get_supabase

sb = get_supabase()

# 23 projets AFD actifs (données du PDF au 30 juin 2026)
projets = [
    {"code": "CBI3030", "date_approbation": "2017-04-10", "date_mise_vigueur": None, "nature_financement": "Prêt", "montant_pret_fcfa": 20223154310, "montant_don_fcfa": 0, "approche": "Projet", "moa": "publique", "taux_decaissement": 91.00, "secteur_detaille": "Énergie"},
    {"code": "CBI3031", "date_approbation": "2017-04-10", "date_mise_vigueur": None, "nature_financement": "Prêt", "montant_pret_fcfa": 4623000000, "montant_don_fcfa": 0, "approche": "Projet", "moa": "publique", "taux_decaissement": 0.00, "secteur_detaille": "Énergie"},
    {"code": "CBI3100", "date_approbation": "2021-12-22", "date_mise_vigueur": None, "nature_financement": "Prêt", "montant_pret_fcfa": 14004681950, "montant_don_fcfa": 0, "approche": "Projet", "moa": "publique", "taux_decaissement": 2.45, "secteur_detaille": "Énergie"},
    {"code": "CBI3101", "date_approbation": "2021-12-22", "date_mise_vigueur": None, "nature_financement": "Prêt", "montant_pret_fcfa": 8953813050, "montant_don_fcfa": 0, "approche": "Projet", "moa": "publique", "taux_decaissement": 16.98, "secteur_detaille": "Énergie"},
    {"code": "CBI3085", "date_approbation": "2019-07-24", "date_mise_vigueur": None, "nature_financement": "Prêt", "montant_pret_fcfa": 26238280000, "montant_don_fcfa": 0, "approche": "Projet", "moa": "publique", "taux_decaissement": 100.00, "secteur_detaille": "Énergie"},
    {"code": "CBI3055", "date_approbation": "2018-03-05", "date_mise_vigueur": None, "nature_financement": "Prêt+Don", "montant_pret_fcfa": 32797850000, "montant_don_fcfa": 5247656000, "approche": "Projet", "moa": "publique", "taux_decaissement": 100.00, "secteur_detaille": "Cadre de vie"},
    {"code": "CBI3086", "date_approbation": "2019-09-26", "date_mise_vigueur": None, "nature_financement": "Prêt+Don", "montant_pret_fcfa": 22630516500, "montant_don_fcfa": 2295849500, "approche": "Projet", "moa": "publique", "taux_decaissement": 37.53, "secteur_detaille": "Cadre de vie"},
    {"code": "CBI3035", "date_approbation": "2017-06-10", "date_mise_vigueur": None, "nature_financement": "Prêt+Don", "montant_pret_fcfa": 13119140000, "montant_don_fcfa": 1967871000, "approche": "Projet", "moa": "publique", "taux_decaissement": 43.56, "secteur_detaille": "Enseignement et formation professionnelle"},
    {"code": "CBI3102", "date_approbation": "2021-12-22", "date_mise_vigueur": None, "nature_financement": "Prêt+Don", "montant_pret_fcfa": 9839355000, "montant_don_fcfa": 3279785000, "approche": "Projet", "moa": "publique", "taux_decaissement": 18.07, "secteur_detaille": "Enseignement et formation professionnelle"},
    {"code": "CBI3130", "date_approbation": "2023-03-30", "date_mise_vigueur": None, "nature_financement": "Prêt", "montant_pret_fcfa": 19678710000, "montant_don_fcfa": 0, "approche": "Projet", "moa": "publique", "taux_decaissement": 9.17, "secteur_detaille": "Enseignement et formation professionnelle"},
    {"code": "CBI3135", "date_approbation": "2023-11-27", "date_mise_vigueur": None, "nature_financement": "Prêt+Don", "montant_pret_fcfa": 45916990000, "montant_don_fcfa": 1967871000, "approche": "Appui budgétaire+PCT", "moa": "publique", "taux_decaissement": 66.44, "secteur_detaille": "Enseignement et formation professionnelle"},
    {"code": "CBI3110", "date_approbation": "2021-04-09", "date_mise_vigueur": None, "nature_financement": "Prêt+Don", "montant_pret_fcfa": 16398925000, "montant_don_fcfa": 6559570000, "approche": "Projet", "moa": "publique", "taux_decaissement": 24.81, "secteur_detaille": "Tourisme et culture"},
    {"code": "CBI3150", "date_approbation": "2025-05-27", "date_mise_vigueur": None, "nature_financement": "Prêt+Don", "montant_pret_fcfa": 16398925000, "montant_don_fcfa": 3279785000, "approche": "Projet", "moa": "publique", "taux_decaissement": 0.00, "secteur_detaille": "Tourisme et culture"},
    {"code": "CBI3155", "date_approbation": "2025-10-06", "date_mise_vigueur": None, "nature_financement": "Prêt+Don", "montant_pret_fcfa": 36077635000, "montant_don_fcfa": 3279785000, "approche": "Appui budgétaire+PCT", "moa": "publique", "taux_decaissement": 63.64, "secteur_detaille": "Tourisme et culture"},
    {"code": "CBI3120", "date_approbation": "2023-07-05", "date_mise_vigueur": None, "nature_financement": "Prêt+Don", "montant_pret_fcfa": 16398925000, "montant_don_fcfa": 2820615100, "approche": "Projet", "moa": "publique", "taux_decaissement": 22.00, "secteur_detaille": "Agriculture"},
    {"code": "CBI3090", "date_approbation": "2020-04-15", "date_mise_vigueur": None, "nature_financement": "Don+Avenant", "montant_pret_fcfa": 0, "montant_don_fcfa": 6559570000, "approche": "Projet", "moa": "publique", "taux_decaissement": 43.00, "secteur_detaille": "Agriculture"},
    {"code": "CBI3115", "date_approbation": "2022-11-14", "date_mise_vigueur": None, "nature_financement": "Prêt", "montant_pret_fcfa": 2636088492, "montant_don_fcfa": 0, "approche": "Projet", "moa": "publique", "taux_decaissement": 68.00, "secteur_detaille": "Gouvernance"},
    {"code": "CBI3036", "date_approbation": "2017-04-10", "date_mise_vigueur": None, "nature_financement": "Prêt", "montant_pret_fcfa": 12574695690, "montant_don_fcfa": 0, "approche": "Projet", "moa": "publique", "taux_decaissement": 78.00, "secteur_detaille": "Gouvernance"},
    {"code": "CBI3125", "date_approbation": "2022-07-27", "date_mise_vigueur": None, "nature_financement": "Prêt+Don", "montant_pret_fcfa": 9839355000, "montant_don_fcfa": 6559570000, "approche": "Projet", "moa": "publique", "taux_decaissement": 26.00, "secteur_detaille": "Entrepreneuriat"},
    {"code": "CBI3156", "date_approbation": "2025-07-18", "date_mise_vigueur": None, "nature_financement": "Don", "montant_pret_fcfa": 0, "montant_don_fcfa": 5247656000, "approche": "Projet", "moa": "publique", "taux_decaissement": 1.25, "secteur_detaille": "Sécurité publique"},
    {"code": "CBI3136", "date_approbation": "2023-04-06", "date_mise_vigueur": None, "nature_financement": "Don", "montant_pret_fcfa": 0, "montant_don_fcfa": 7871484000, "approche": "Projet", "moa": "privée", "taux_decaissement": 23.91, "secteur_detaille": "Agriculture"},
    {"code": "CBI3151", "date_approbation": "2025-03-15", "date_mise_vigueur": None, "nature_financement": "Don", "montant_pret_fcfa": 0, "montant_don_fcfa": 5641230200, "approche": "Projet", "moa": "privée", "taux_decaissement": 23.25, "secteur_detaille": "Enseignement et formation professionnelle"},
    {"code": "CBI3140", "date_approbation": "2024-03-20", "date_mise_vigueur": None, "nature_financement": "Don", "montant_pret_fcfa": 0, "montant_don_fcfa": 9839355000, "approche": "Projet", "moa": "privée", "taux_decaissement": 0.00, "secteur_detaille": "Santé"},
]

# Mise à jour des projets AFD existants
updated = 0
for p in projets:
    code = p["code"]
    data = {k: v for k, v in p.items() if k != "code"}
    try:
        res = sb.table("accords_consolides").update(data).eq("code_projet", code).execute()
        if res.data:
            updated += 1
            print(f"✅ {code} mis à jour")
        else:
            print(f"⚠️ {code} non trouvé dans la base")
    except Exception as e:
        print(f"❌ Erreur pour {code}: {e}")

print(f"\n📊 Total: {updated} projets AFD mis à jour sur {len(projets)}")