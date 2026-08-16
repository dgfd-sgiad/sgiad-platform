# -*- coding: utf-8 -*-
import sys
sys.path.insert(0, '.')
from db import get_supabase
from collections import Counter

sb = get_supabase()

# Securite : ne pas reimporter si deja present
ex = sb.table('recommandations').select('id').eq('partenaire', 'Banque Mondiale').execute().data or []
if ex:
    print(f"Deja {len(ex)} recos Banque Mondiale -> import ignore")
    sys.exit(0)

# 1) Creer les 2 revues BM
def get_revue(type_rev, date_rev):
    r = sb.table('revues').select('id').eq('partenaire', 'Banque Mondiale').eq('type_revue', type_rev).execute().data
    if r: return r[0]['id']
    ins = sb.table('revues').insert({'partenaire': 'Banque Mondiale', 'type_revue': type_rev, 'date_revue': date_rev}).execute()
    return ins.data[0]['id']

rev_ipf = get_revue('Revue des projets IPF', '2026-07-28')
rev_pforr = get_revue('Revue des projets PforR', '2026-07-27')
print(f"Revues BM: IPF={rev_ipf}, PforR={rev_pforr}")

MOIS = {'jan':1,'feb':2,'mar':3,'apr':4,'may':5,'jun':6,'jul':7,'aug':8,'sep':9,'oct':10,'nov':11,'dec':12}
def parse_date(s):
    if not s: return None
    s = str(s).strip().lower()
    if s in ('en continu', '-', ''): return None
    try:
        p = s.split('-')
        if len(p) == 3:
            j = int(p[0]); m = MOIS.get(p[1], 1); a = int(p[2])
            if a < 100: a += 2000
            return f"{a:04d}-{m:02d}-{j:02d}"
    except: pass
    return None

# (cat, projet, point_attention, recommandation, delai, responsable, associe, statut, observations)
RECOS = [
    # ===== IPF =====
    ("IPF", "Tous les projets du portefeuille", "Amélioration des prévisions des décaissements au titre des premier et deuxième trimestres de l'année fiscale 2026-2027", "Echanger avec les projets pour l'amélioration des prévisions des décaissements au titre des premier et deuxième trimestres de l'année fiscale 2027", "31-Jul-26", "UGP", "Pool suivi", "Exécutée", "Les échanges ont eu lieu avec les UGP qui ont souhaité poursuivre la mise en œuvre des activités sur la base des prévisions actuelles et les réexaminer d'ici septembre 2026"),
    ("IPF", "Tous les projets du portefeuille", "Elaboration des documents de planification (PTBA et PPM) au titre de la gestion 2027", "Elaborer les PTBA et PPM au titre de la gestion 2027 en tenant compte des objectifs de décaissements de l'année fiscale 2026-2027", "30-Nov-26", "UGP", "Pool suivi", "En cours", "Poursuivre le suivi afin que les documents soient élaborés dans les délais requis"),
    ("IPF", "Tous les projets du portefeuille", "Lenteur dans le processus de la mise à disposition des projets du relevé du compte désigné", "Accélérer le processus de mise à disposition des projets, du relevé de leur compte désigné", "En continu", "CAGD", "DGFD UGP", "En cours", "Poursuivre le suivi pour une mise en œuvre continue de cette recommandation"),
    ("IPF", "FP2E", "Retard dans le processus d'obtention du Bon à lancer de la DNCMP sur l'AMI de recrutement des BET des LTA d'Adja-Ouèrè et de Djidja", "Finaliser la prise en compte des observations de la DNCMP et lui retourner l'AMI", "30-Jul-26", "UGP", "DGFD", "Exécutée", "L'AMI a été lancé le 28 juillet 2026 et l'ouverture des offres est prévue du 12 au 19 août 2026"),
    ("IPF", "FP2E", "Retard dans le processus de validation du CMR 2026-2027 du projet", "Relancer le TTL du projet", "29-Jul-26", "UGP", "Pool suivi", "Exécutée", "Le TTL a été relancé le 05 août 2026. Le TTL prévoit de valider le CMR à son retour de congés, fin août."),
    ("IPF", "FP2E", "Difficultés relatives à l'indemnisation des personnes affectées par la construction du LTA de Djidja et des EPFA de Zangnanando et d'Aplahoué", "Transmettre à la DGFD les décharges des courriers adressés aux préfets du Zou et de Couffo pour solliciter une dérogation pour la délivrance des Attestations de Détention Coutumière (ADC) pour faciliter l'indemnisation", "31-Jul-26", "UGP", "Pool suivi", "En cours", "Une décharge a été transmise à la DGFD le 04 août 2026. La 2ème lettre pourrait être finalisée dans la semaine du 17 août 2026"),
    ("IPF", "PACOFIDE", "Lenteur dans le processus d'approvisionnement du compte d'opérations du projet", "Echanger avec la BCEAO pour l'inviter à accélérer la recherche du paiement d'un montant de 479.394.607 FCFA versé par la Banque mondiale dans le compte désigné, le 29 mai 2026", "29-Jul-26", "DGFD", "CAGD", "En cours", "Pas de retour de la BCEAO selon la CAGD (Rappel à faire au DG)"),
    ("IPF", "PACOFIDE", "Retard dans le processus de validation du CMR 2026-2027 du projet", "Relancer le TTL du projet.", "29-Jul-26", "UGP", "Pool suivi", "Exécutée", "Le CMR prenant en compte les dernières observations de la Banque est celui validé"),
    ("IPF", "P2AE", "Retard dans le processus de validation du CMR 2026-2027 du projet", "Transmettre à la Banque le projet du CMR 2026-2027 en mettant le DGFD en copie", "31-Jul-26", "UGP", "DGFD", "Exécutée", "Le CMR a été transmis à la Banque le 04 août 2026. La clôture du projet est prévue pour le 31 décembre 2026"),
    ("IPF", "P2AE", "Poursuite des travaux complétaires", "Solliciter la Banque pour l'obtention de l'ANO relatif à l'avenant aux travaux complémentaires confiés à la société LRA", "31-Jul-26", "DGFD", "BM", "En cours", "Relancer le TTL (Rappel à faire au DG)"),
    ("IPF", "P2AE", "Poursuite des travaux complétaires", "Solliciter la Banque pour l'obtention de l'ANO relatif à l'avenant aux travaux complémentaires confiés à la société RMT", "31-Jul-26", "DGFD", "BM", "En cours", "Relancer le TTL (Rappel à faire au DG)"),
    ("IPF", "ProDIJ", "Lenteur dans le processus d'approvisionnement du compte d'opérations du projet", "Accélérer le processus d'approvisionnement du compte d'opérations du projet", "31-Jul-26", "CAGD", "DGFD", "Exécutée", "Le compte d'opération du projet a été approvisionné le 30 juin 2026"),
    ("IPF", "ProDIJ", "Difficulté d'obtention des relevés du compte désigné", "Echanger avec la BCEAO pour solliciter la mise à disposition rapide des relevés du compte désigné du projet", "29-Jul-26", "DGFD", "CAGD", "En cours", "Le relevé du compte désigné du projet a été obtenu le 05 août 2026"),
    ("IPF", "ProDIJ", "Difficulté de séparation des marchés de travaux et d'équipement de la phase pilote (Atlantique et Ouémé) de la phase générale", "Organiser une réunion avec la Banque (Martin, Brahim) pour accélérer le lancement de ce marché", "29-Jul-26", "DGFD (Pool suivi)", "BM", "Exécutée", "Accord de la Banque pour la séparation des marchés de la phase pilote de celle de la phase générale"),
    ("IPF", "Dorsale Nord", "Opérationnalisation du Comité national de coordination (CNCS) de la sécurité", "Echanger avec le SGM/MEEM pour solliciter l'accélération du processus de nomination des membres du CNCS", "31-Jul-26", "DGFD", "MEEM", "En cours", "Rappel à faire au DGFD"),
    ("IPF", "PFC1-Benin", "Assurer une bonne exécution des activités de clôture du projet prévue pour le 30 novembre 2026", "Prendre les dispositions pour assurer une bonne exécution des activités de clôture du projet", "30-Nov-26", "UGP", "Pool suivi", "En cours", "Les dispositions sont en cours au niveau de l'UGP pour une bonne clôture du projet le 30 novembre 2026"),
    ("IPF", "PFC2-Benin", "Signature de l'accord de financement additionnel (volet SCALE) du PFC2", "Transmettre au DGFD un résumé du document à signer", "31-Jul-26", "UGP", "Pool suivi", "Exécutée", "Le résumé sur les activités du financement additionnel du PFC-B2 a été transmis le jeudi 30 juillet 2026"),
    ("IPF", "PMUD-GN", "Retard dans la transmission à la Banque du CMR 2026-2027", "Transmettre à la Banque le projet du CMR 2026-2027 en mettant le DGFD en copie", "29-Jul-26", "UGP", "DGFD", "Exécutée", "Le CMR a été transmis le 29 juillet 2026"),
    ("IPF", "PMUD-GN", "Acquisition des motos électriques et structuration de la gestion des déchets issus de l'utilisation de ces motos", "Echanger avec le BASE/PR pour la validation du mécanisme d'acquisition et de gestion des déchets", "31-Jul-26", "DGFD", "UGP", "En cours", "Action DGFD pour échange avec BASE PR afin de faire avancer le processus (Rappel à faire au DG)"),
    ("IPF", "PMUD-GN", "Mise en place de la structure d'Assistance à maîtrise d'ouvrage (AMO)", "Communiquer à la DGFD un créneau horaire pour une réunion avec le DG/SIRAT", "31-Jul-26", "UGP", "DGFD", "En cours", "Les échanges se poursuivent entre le coordonnateur du projet et le DG SIRAT pour convenir d'un créneau horaire à communiquer au DGFD."),
    ("IPF", "WACA+", "Mise en vigueur de l'accord de financement du projet", "Solliciter auprès de la Banque une prorogation du délai de mise en vigueur", "18-Aug-26", "UGP CAGD", "Pool suivi", "En cours", "La demande de prorogation a été transmise au MEF le 06 août 2026. Le décret de ratification a été pris, il reste l'avis juridique de la Cour Suprême."),
    ("IPF", "PHASAOC", "Retard dans la mise en oeuvre des activités du projet", "Elaborer un plan d'accélération de mise en œuvre des activités du projet", "5-Aug-26", "UGP", "Pool suivi", "Exécutée", "Le plan d'accélération prenant en compte les observations de la DGFD a été retransmis le 13 août 2026."),
    ("IPF", "PHASAOC", "Retard dans la mise en oeuvre des activités du projet", "Regrouper en deux phases le reste des activités à exécuter sur le projet au titre de 2027 et 2028", "15-Aug-26", "UGP", "Pool suivi", "En cours", "Le regroupement des activités au titre des gestions 2027 et 2028 est en cours et sera finalisé le 15 août 2026 au plus tard"),
    # ===== PforR =====
    ("PFORR", "BRIC", "Mobilisation des ressources des Programmes P4R", "Initier une réunion avec DGFD et DGB. Préparer un tableau comparatif des ressources mobilisées et les ressources prévues au cadre de dépense des programmes, en intégrant une planification des besoins de ressources pour terminer l'année", "5-Aug-26", "CAMO", "CTA-SEP", "Exécutée", "La réunion a eu lieu le mardi 04 Août 2026. La DGD doit faire un retour à la DGFD le Jeudi 06 Août 2026 sur la possibilité d'un crédit additionel aux programmes BRIC et Terra Bénin pour un montant de 55 Milliards."),
    ("PFORR", "Gbéssoké", "Amélioration de l'éfficacité du ciblage grâce à l'utilisation du RSU", "Demander à l'ANPS de nous faire suivre le Budget et le chronogramme de la Mise à Jour du Régime Social Unique", "28-Jul-26", "CAMO", "CTA-SEP", "En cours", "La demande a été formulée le 28 juillet 2026 et la CAMO est attente des documents. Des mails de relance sont envoyés. Poursuivre le suivi avec la CAMO Gbéssoké"),
    ("PFORR", "Gbéssoké", "85 GUPS entièrement dotés en personnel et équipés", "Faire un point d'étape du dossier de la construction des GUPS", "28-Jul-26", "CAMO", "CTA-SEP", "En cours", "Les Offres relatives à la construction des GUPS ont été reçues et sont en attente des Orientations de la MFAS. Poursuivre le suivi avec la CAMO Gbéssoké"),
    ("PFORR", "Terra Bénin", "Recrutement des opérateurs fonciers", "Attribuer un lot par adjudicataire", "En continu", "CAMO", "CTA-SEP", "En cours", "Démarrage le 13/08/2026 de l'évaluation des offres à l'issue de l'AMI relatif au recrutement des ONG. Démarrage projeté pour le 17 août 2026 pour les opérateurs."),
]

n = 0
for (cat, projet, point, reco, delai, resp, assoc, statut, obs) in RECOS:
    rid = rev_ipf if cat == 'IPF' else rev_pforr
    st = 'executee' if statut == 'Exécutée' else 'en_cours'
    sb.table('recommandations').insert({
        'revue_id': rid,
        'partenaire': 'Banque Mondiale',
        'projet': projet,
        'difficulte': point,
        'texte': reco,
        'responsable_direct': resp,
        'associe': assoc,
        'echeance': parse_date(delai),
        'statut': st,
        'commentaires': obs,
        'avancement': 100 if st == 'executee' else 0,
        'executee': st == 'executee',
    }).execute()
    n += 1

print(f"✅ {n} recommandations Banque Mondiale importées")
c = sb.table('recommandations').select('partenaire').execute().data
print("Répartition:", Counter([x['partenaire'] for x in c]))
print("Total:", sb.table('recommandations').select('id', count='exact').execute().count)