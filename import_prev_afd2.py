# -*- coding: utf-8 -*-
from db import get_supabase

sb = get_supabase()
PART = 'Agence Française de Développement'

OPERATIONS = [
    {"projet": "ProFAR 1", "montant": 115648845, "operation": "Paiement avance de démarrage contrat AMO", "taux_cible": "18.84%", "date_prev": "2026-08-15", "cumul": 7148246326, "obs": "Demande de paiement transmise à l'AFD", "nd": False},
    {"projet": "ProFAR 1", "montant": 327978500, "operation": "Demande de renouvellement d'avance sur don", "taux_cible": "19.70%", "date_prev": "2026-09-15", "cumul": 7476224826, "obs": "Audits réalisés. Attente de l'avis de l'AFD (retard ANO sur rapports d'audit)", "nd": False},
    {"projet": "ProFAR 1", "montant": 112478625, "operation": "Paiement troisième tranche contrat LASDEL", "taux_cible": "20.00%", "date_prev": "2026-11-15", "cumul": 7588703451, "obs": "Atelier de pré-validation le 07 août. Validation prévue première quinzaine de septembre", "nd": False},
    {"projet": "ProFAR 1", "montant": 809716667, "operation": "Paiement avance de démarrage travaux EPFA Malanville", "taux_cible": "22.13%", "date_prev": None, "cumul": 8398420118, "obs": "Maturation insuffisante - démarrage janvier 2027", "nd": True},
    {"projet": "ProFAR 1", "montant": 809716667, "operation": "Paiement avance de démarrage travaux EPFA Ségbana", "taux_cible": "24.26%", "date_prev": None, "cumul": 9208136784, "obs": "Maturation insuffisante - démarrage janvier 2027", "nd": True},
    {"projet": "ProFAR 1", "montant": 33347667, "operation": "Paiement avance de démarrage contrat BCT", "taux_cible": "24.35%", "date_prev": None, "cumul": 9241484451, "obs": "Maturation insuffisante", "nd": True},
    {"projet": "ProFAR 1", "montant": 115981833, "operation": "Paiement avance de démarrage contrat BET", "taux_cible": "24.66%", "date_prev": None, "cumul": 9357466284, "obs": "Maturation insuffisante", "nd": True},
    {"projet": "ProFAR 2", "montant": 78714840, "operation": "Paiement premier décompte contrat AMO", "taux_cible": "24.86%", "date_prev": "2026-11-15", "cumul": 9436181124, "obs": "Validation du rapport S1 prévue octobre 2026", "nd": False},
    {"projet": "ProFAR 2", "montant": 809716667, "operation": "Paiement avance de démarrage travaux EPFA Adjohoun", "taux_cible": "27.00%", "date_prev": None, "cumul": 10245897791, "obs": "ANO donné mais BET/BCT pas prêts - démarrage 2027", "nd": True},
    {"projet": "ProFAR 2", "montant": 884616667, "operation": "Paiement avance de démarrage travaux LTA Avrankou", "taux_cible": "29.33%", "date_prev": None, "cumul": 11130514458, "obs": "DAOI annulé et repris - démarrage 2026 impossible", "nd": True},
    {"projet": "ProFAR 2", "montant": 1600000000, "operation": "Marché équipement EPFA Malanville/Ségbana/Adjohoun + LTA Avrankou", "taux_cible": "33.54%", "date_prev": None, "cumul": 12730514458, "obs": "DAOI en cours + travaux pas démarrés", "nd": True},
    {"projet": "ProFAR 2", "montant": 400000000, "operation": "Marché équipement LTA Ina", "taux_cible": "34.60%", "date_prev": None, "cumul": 13130514458, "obs": "Liste équipements en cours", "nd": True},
    {"projet": "PCT/FBPPC", "montant": 655957000, "operation": "1er Appel de fonds", "taux_cible": "36.33%", "date_prev": "2026-09-15", "cumul": 13786471458, "obs": "Demande de 1er versement transmise à l'AFD le 9 juillet 2026", "nd": False},
    {"projet": "DEFI-Pro", "montant": 3075478316, "operation": "Paiement contrat entreprise LT Sodohomè", "taux_cible": "44.43%", "date_prev": None, "cumul": 16861949774, "obs": "Retard avenant travaux - objectif non atteint", "nd": False},
    {"projet": "DEFI-Pro", "montant": 69798137, "operation": "Paiement MOE cabinet HIRAM", "taux_cible": "44.61%", "date_prev": None, "cumul": 16931747911, "obs": "Travaux au ralenti (avenant non signé)", "nd": False},
    {"projet": "DEFI-Pro", "montant": 45507830, "operation": "Paiement MOE LT Ina", "taux_cible": "44.73%", "date_prev": None, "cumul": 16977255741, "obs": "Livraison définitive prévue 03 octobre 2026", "nd": False},
    {"projet": "DEFI-Pro", "montant": 44119234, "operation": "BCT LT Sodohomè", "taux_cible": "44.85%", "date_prev": None, "cumul": 17021374975, "obs": "Factures présentées seront payées", "nd": False},
    {"projet": "DEFI-Pro", "montant": 14932890, "operation": "Acquisition mobilier LTA Ina", "taux_cible": "44.89%", "date_prev": None, "cumul": 17036307865, "obs": "Retenue de garantie à expiration du délai", "nd": False},
    {"projet": "DEFI-Pro", "montant": 2962806091, "operation": "Avance 30% équipements LTP BTP Sodohomè", "taux_cible": "52.70%", "date_prev": None, "cumul": 19999113956, "obs": "Contrats + ordre de démarrage ACISE requis", "nd": False},
    {"projet": "DEFI-Pro", "montant": 150842400, "operation": "Audits semestriels 2025-2026 + audit FAIJ", "taux_cible": "53.09%", "date_prev": None, "cumul": 20149956356, "obs": "Contrat prestataire avant fin août", "nd": False},
    {"projet": "PAEB", "montant": 3763960536, "operation": "Demande de retrait de fonds", "taux_cible": "63.01%", "date_prev": "2026-09-15", "cumul": 23913916892, "obs": "Pièces justificatives en instance à la CAGD", "nd": False},
    {"projet": "PRPC", "montant": 300000000, "operation": "Paiement avance sur travaux", "taux_cible": "63.80%", "date_prev": "2026-09-15", "cumul": 24213916892, "obs": "Procédure en cours de finalisation", "nd": False},
    {"projet": "PRPC", "montant": 80423000, "operation": "Recrutement d'une maîtrise d'œuvre", "taux_cible": "64.01%", "date_prev": "2026-10-10", "cumul": 24294339892, "obs": "Procédure en cours de finalisation", "nd": False},
    {"projet": "TAZCO 2", "montant": 542806626, "operation": "Composante 1: Paiement avance travaux", "taux_cible": "65.44%", "date_prev": None, "cumul": 24837146518, "obs": "Factures ONG, intercommunalités, acquisitions, salaires", "nd": False},
    {"projet": "TAZCO 2", "montant": 237129080, "operation": "Composante 2: Demande retrait fonds", "taux_cible": "66.07%", "date_prev": None, "cumul": 25074275598, "obs": "Factures semences, acquisitions, salaires", "nd": False},
    {"projet": "TAZCO 2", "montant": 222838773, "operation": "Composante 3: Acquisitions équipements lot 2", "taux_cible": "66.66%", "date_prev": None, "cumul": 25297114371, "obs": "Factures CA 17, ateliers, acquisitions", "nd": False},
    {"projet": "DEFISSOL SI", "montant": 255286119, "operation": "Paiement avance mise en œuvre SIG", "taux_cible": "67.33%", "date_prev": "2026-11-30", "cumul": 25552400490, "obs": "TDR validés, attente mise en place AMOA", "nd": False},
    {"projet": "DEFISSOL SI", "montant": 241694565, "operation": "Travaux interconnexions", "taux_cible": "67.97%", "date_prev": "2026-12-30", "cumul": 25794095055, "obs": "Travaux suspendus - avenant 2 changement RIB", "nd": False},
    {"projet": "DEFISSOL SI", "montant": 50000000, "operation": "Paiement avance Schéma Directeur", "taux_cible": "68.10%", "date_prev": "2026-12-30", "cumul": 25844095055, "obs": "En attente de l'ANO de l'AFD", "nd": False},
    {"projet": "DEFISSOL SI", "montant": 148426670, "operation": "Paiement avance recrutement AMOA", "taux_cible": "68.49%", "date_prev": None, "cumul": 25992521725, "obs": "Contrat en attente de validation", "nd": False},
    {"projet": "DEFISSOL SI", "montant": 15000000, "operation": "Paiement avance formation complémentaire", "taux_cible": "68.53%", "date_prev": "2026-12-30", "cumul": 26007521725, "obs": "AMI élaboré, attente AMOA", "nd": False},
    {"projet": "FORSUN SOLAIRE", "montant": 1942627807, "operation": "Travaux construction centrale", "taux_cible": "73.65%", "date_prev": "2026-08-30", "cumul": 27950149532, "obs": "Décompte EPC transmis à la CAGD", "nd": False},
    {"projet": "FORSUN SOLAIRE", "montant": 2007979629, "operation": "Décompte réception opérationnelle partielle", "taux_cible": "78.94%", "date_prev": "2026-08-30", "cumul": 29958129161, "obs": "Décompte EPC transmis à la CAGD", "nd": False},
    {"projet": "FORSUN SOLAIRE", "montant": 3865161, "operation": "Paiement n°15 suivi fin construction", "taux_cible": "78.95%", "date_prev": "2026-09-30", "cumul": 29961994322, "obs": "", "nd": False},
    {"projet": "FORSUN SOLAIRE", "montant": 9166343, "operation": "Paiement agence communication", "taux_cible": "78.97%", "date_prev": "2026-12-31", "cumul": 29971160665, "obs": "", "nd": False},
    {"projet": "FORSUN SOLAIRE", "montant": 9292287, "operation": "Travaux d'audit", "taux_cible": "79.00%", "date_prev": "2026-12-31", "cumul": 29980452952, "obs": "", "nd": False},
    {"projet": "DEFISSOL", "montant": 102909158, "operation": "Travaux remise en état RTU", "taux_cible": "79.27%", "date_prev": "2026-09-30", "cumul": 30083362110, "obs": "", "nd": False},
    {"projet": "DEFISSOL", "montant": 267064365, "operation": "Travaux supplémentaires poste CEB ONIGBOLO", "taux_cible": "79.97%", "date_prev": "2026-09-30", "cumul": 30350426475, "obs": "", "nd": False},
    {"projet": "DEFISSOL", "montant": 2490013, "operation": "Accompagnement contractualisation BESS 5MW", "taux_cible": "79.98%", "date_prev": "2026-09-30", "cumul": 30352916488, "obs": "", "nd": False},
    {"projet": "BESS 5 MW", "montant": 924659159, "operation": "Paiement avance démarrage", "taux_cible": "82.41%", "date_prev": "2026-08-30", "cumul": 31277575647, "obs": "", "nd": False},
    {"projet": "BESS 5 MW", "montant": 2773977476, "operation": "Mise FOB conteneurs batteries", "taux_cible": "89.72%", "date_prev": "2026-10-30", "cumul": 34051553123, "obs": "", "nd": False},
    {"projet": "BESS 5 MW", "montant": 10084158, "operation": "Paiement 1 suivi construction", "taux_cible": "89.75%", "date_prev": "2026-08-30", "cumul": 34061637281, "obs": "", "nd": False},
    {"projet": "BESS 5 MW", "montant": 25210395, "operation": "Paiement 2 avis techniques", "taux_cible": "89.82%", "date_prev": "2026-09-30", "cumul": 34086847677, "obs": "", "nd": False},
    {"projet": "FORSUN DISTRIBUTION", "montant": 5300000, "operation": "Facture rapport audit 2024", "taux_cible": "89.83%", "date_prev": "2026-09-30", "cumul": 34092147677, "obs": "", "nd": False},
    {"projet": "FORSUN DISTRIBUTION", "montant": 5300000, "operation": "Facture rapport audit 2025", "taux_cible": "89.84%", "date_prev": "2026-12-31", "cumul": 34097447677, "obs": "", "nd": False},
    {"projet": "FORSUN DISTRIBUTION", "montant": 10000000, "operation": "Facture HERAUS Sarl", "taux_cible": "89.87%", "date_prev": "2026-10-10", "cumul": 34107447677, "obs": "", "nd": False},
    {"projet": "FORSUN DISTRIBUTION", "montant": 444345000, "operation": "Facture MOE n°2 (renforcement capacités UGP)", "taux_cible": "91.04%", "date_prev": "2026-09-30", "cumul": 34551792677, "obs": "", "nd": False},
    {"projet": "PADIAP", "montant": 2400000000, "operation": "DRF subvention AFD", "taux_cible": "97.37%", "date_prev": "2026-09-30", "cumul": 36951792677, "obs": "Montant déclencheur atteint. DRF préparée, attente retour AFD sur audits", "nd": False},
    {"projet": "PADIAP", "montant": 1000000000, "operation": "DRF subvention UE", "taux_cible": "100.00%", "date_prev": "2026-10-30", "cumul": 37951792677, "obs": "Audit intercalaire UE + ANO AFD fin août", "nd": False},
]

sb.table('previsions_decaissements').delete().eq('partenaire', PART).execute()

n = 0
for op in OPERATIONS:
    sb.table('previsions_decaissements').insert({
        'partenaire': PART,
        'projet': op['projet'],
        'montant_fcfa': op['montant'],
        'operation': op['operation'],
        'taux_cible': op['taux_cible'],
        'date_previsionnelle': op['date_prev'],
        'delai_texte': '' if op['date_prev'] else 'Période non précisée',
        'montant_cumule_fcfa': op['cumul'],
        'observations': op['obs'],
        'non_decaissable_2026': op['nd'],
    }).execute()
    n += 1

total = sum(op['montant'] for op in OPERATIONS)
nd = sum(1 for op in OPERATIONS if op['nd'])
print(f'📊 {n} opérations de décaissement importées pour l\'AFD.')
print(f'💰 Total opérations août-décembre 2026 : {total:,} FCFA')
print(f'⚠️ {nd} opérations marquées non décaissables en 2026')