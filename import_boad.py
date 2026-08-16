# -*- coding: utf-8 -*-
import sys
sys.path.insert(0, '.')
from db import get_supabase
from collections import Counter

sb = get_supabase()
PART = 'Banque Ouest Africaine de Développement'

ex = sb.table('recommandations').select('id').eq('partenaire', PART).execute().data or []
if ex:
    print(f"Deja {len(ex)} recos BOAD -> import ignore")
    sys.exit(0)

rev = sb.table('revues').select('id').eq('partenaire', PART).eq('type_revue', 'Revue technique août 2026').execute().data
if rev:
    revue_id = rev[0]['id']
else:
    ins = sb.table('revues').insert({'partenaire': PART, 'type_revue': 'Revue technique août 2026', 'date_revue': '2026-08-15'}).execute()
    revue_id = ins.data[0]['id']
print(f"Revue BOAD: id={revue_id}")

MOIS = {'jan':1,'feb':2,'mar':3,'apr':4,'may':5,'jun':6,'jul':7,'aug':8,'sep':9,'oct':10,'nov':11,'dec':12}
def parse_date(s):
    if not s: return None
    s = str(s).strip().lower()
    if s in ('immédiat','immediat','-',''): return None
    try:
        p = s.split('-')
        if len(p)==3:
            j=int(p[0]); m=MOIS.get(p[1],1); a=int(p[2])
            if a<100: a+=2000
            return f"{a:04d}-{m:02d}-{j:02d}"
    except: pass
    return None

# (projet, point_attention, recommandation, delai, responsable, associe, observations)
RECOS = [
    ("Projets 3035 Logements Sociaux (791+944+1300)", "Contractualisation avec SGTM pour la poursuite des travaux", "Diligenter la réunion avec SGTM pour valider l'offre et finaliser le projet de contrat", "7-Aug-26", "SIMAU SGTM", "Pôle de Suivi MEF MCVT", "- Observations de la SIMAU sur la proposition d'offres de SGTM envoyées le 30 juillet 2026 concernant 1919 Logements - Réunion non tenue (SGTM et Koffi DIABATE en congés, reprise fin août 2026) - Appel du DGFD au DG/SIMAU pour convenir d'un chronogramme de signature du contrat"),
    ("Projets 3035 Logements Sociaux (791+944+1300)", "Contractualisation avec SGTM pour la poursuite des travaux", "Transmettre le projet de contrat à la BOAD pour ANO", "14-Aug-26", "SIMAU SGTM", "Pôle de Suivi MEF MCVT", "- Statu quo"),
    ("Projets 3035 Logements Sociaux (791+944+1300)", "Contractualisation avec SGTM pour la poursuite des travaux", "Procéder à la signature du contrat", "10-Sep-26", "SIMAU SGTM", "Pôle de Suivi MEF MCVT", "- Délai de 10 septembre compromis. Congés des équipes et reprise d'ici fin août 2026."),
    ("Projets 3035 Logements Sociaux (791+944+1300)", "Contractualisation avec SGTM pour la poursuite des travaux", "Transmettre à la BOAD, avec en copie le Pôle de Suivi MEF, le chronogramme détaillé des travaux restants des 1919 Logements confiés à SGTM", "31-Aug-26", "SIMAU SGTM", "Pôle de Suivi MEF MCVT", ""),
    ("Projets 3035 Logements Sociaux (791+944+1300)", "Préfinancement des travaux de charpente et de couverture en fibrociment de 401 logements", "Transmettre à la BOAD un mémo circonstancier sur le dossier de préfinancement", "20-Aug-26", "SIMAU", "Pôle de Suivi MEF MCVT", "- Finalisation du mémo le 18 août 2026 au plus tard - Transmission à la BOAD projetée le 20 août 2026 - Intégrer le coût des travaux complémentaires (charpente ~900 millions FCFA) - Préfinancement avoisinant 2.000.000.000 FCFA"),
    ("Projets 3035 Logements Sociaux (791+944+1300)", "Travaux de construction des 3035 logements, de viabilisation secondaire et tertiaire du site", "Transmettre à la BOAD la requête de prorogation de la Date Limite de Mobilisation au 31 décembre 2028", "5-Aug-26", "CAGD", "DGFD CTA-SEP SIMAU MCVT", "- Requête envoyée à la BOAD le 5 août 2026. En attente du retour de la Banque"),
    ("Projets 3035 Logements Sociaux (791+944+1300)", "Travaux de construction des 3035 logements, de viabilisation secondaire et tertiaire du site", "Transmettre à la BOAD la requête formelle d'annulation du reliquat de la tranche 1", "31-Aug-26", "CAGD", "DGFD CTA-SEP SIMAU MCVT", "- Mail envoyé le 3 août 2026 pour envoi du dossier complet - Aucun retour malgré les relances. Appel du DG au DG/SIMAU - Reliquat à annuler (viabilisation primaire) : 3.700.000.000 FCFA"),
    ("Projets 3035 Logements Sociaux (791+944+1300)", "Travaux de construction des 3035 logements, de viabilisation secondaire et tertiaire du site", "Transmettre à la BOAD la requête de financement complémentaire pour les travaux de logements et de viabilisation secondaire/tertiaire", "31-Aug-26", "Pôle de Suivi MEF", "SIMAU MCVT", "- Mail envoyé le 3 août 2026 - Aucun retour malgré les relances. Appel du DG au DG/SIMAU - Surcoûts estimés à 7.000.000.000 FCFA (gap à rechercher)"),
    ("Projets de construction de 06 LTP (phases 1 et 2)", "Finalisation des DAO et des DCE", "Organiser une réunion entre ACISE et ADET pour finaliser les arbitrages sur l'optimisation des coûts en dépassement des LTP", "7-Aug-26", "ADET", "ACISE", "- Réunion tenue entre ADET et ACISE le 5 août 2026 - Coûts harmonisés reversés aux 02 Architectes pour finaliser DCE et DAO attendus pour le 14 août 2026 au plus tard"),
    ("Projets de construction de 06 LTP (phases 1 et 2)", "Finalisation des DAO et des DCE", "Organiser si nécessaire une réunion technique avec les Architectes sur le chronogramme d'exécution des activités", "12-Aug-26", "Pôle de Suivi MEF", "ADET ACISE Architectes", "- Suivi fait avec l'UGP et ACISE - DCE et DAO en cours de finalisation. Risque de non respect du délai du 14 août 2026 - Appeler le DG/ACISE pour booster les Architectes"),
    ("Projets de construction de 06 LTP (phases 1 et 2)", "Finalisation des DAO et des DCE", "Accélérer et finaliser l'analyse des offres relatives à la préqualification des entreprises de travaux et des Bureaux d'études", "15-Aug-26", "ADET ACISE", "Pôle de Suivi MEF", "- Evaluation achevée, Listes restreintes en cours au niveau de ACISE - Appeler le DG ACISE pour transmettre les Listes restreintes à l'ADET en vue de la saisine de la BOAD le 18 août 2026 au plus tard"),
    ("Projets de construction de 06 LTP (phases 1 et 2)", "Recrutement des BET", "Transmettre la DP à la BOAD pour le recrutement des BET", "3-Aug-26", "ADET", "Pôle de Suivi MEF ACISE", "- DP envoyée à la BOAD le 31 juillet 2026 pour ANO. En attente du retour de la Banque"),
    ("Projets de construction de 06 LTP (phases 1 et 2)", "Recrutement des BCT", "Transmettre la DP révisée à la BOAD pour le recrutement des BCT", "4-Aug-26", "ADET", "Pôle de Suivi MEF ACISE", "- Observations de la BOAD prises en compte, DP révisée envoyée le 6 août 2026 pour ANO. En attente du retour de la Banque"),
    ("Projets de construction de 06 LTP (phases 1 et 2)", "Prise de service du SSES", "Accélérer le processus de recrutement du Spécialiste en Sauvegardes Environnementales et Sociales", "15-Aug-26", "ADET", "Pôle de Suivi MEF ACISE", "- Entretien tenu le 7 août 2026, négociations projetées le 25 août 2026 - Transmission du dossier à la BOAD le 28 août 2026 au plus tard - Prise de service début septembre 2026"),
    ("Projets de construction de 06 LTP (phases 1 et 2)", "Prise de service du SPM et du Technicien en Génie Civil au niveau de ACISE", "Finaliser le recrutement du SPM et du 3è technicien en génie Civil dans le cadre de l'assistance technique ACISE", "30-Aug-26", "ACISE", "Pôle de Suivi MEF ADET", "- Processus en cours au niveau de ACISE"),
    ("Projets de construction de 06 LTP (phases 1 et 2)", "Acquisition de véhicules", "Transmettre à la BOAD pour ANO la requête d'entente directe avec CFAO pour l'acquisition de véhicule", "30-Aug-26", "ADET", "Pôle de Suivi MEF ACISE", "- Transmission de la requête avec note argumentée projetée pour fin août 2026"),
    ("Projets de construction de 06 LTP (phases 1 et 2)", "Acquisition de mobiliers", "Diligenter la livraison des mobiliers", "31-Aug-26", "ADET", "Pôle de Suivi MEF ACISE", "- Conformément au contrat du prestataire, la livraison des mobiliers est pour fin août 2026."),
    ("PUR-ZEDAGA", "Transferts monétaires", "Appel du DG au DG/INSTAD et à GBESSOKE pour accélérer le processus", "Immédiat", "DGFD", "A/DG DMRM", "- Appel effectué pour booster le processus - Visite de terrain démarrée pour 1 mois - Liste disponible d'ici mi-septembre pour les premiers paiements"),
    ("PUR-ZEDAGA", "Acquisition de matériels et équipements agricoles", "Relancer les 03 prestataires pour introduire les factures", "30-Aug-26", "UGP", "Pôle de Suivi MEF", "- Réception déjà faite - Prestataires relancés les 31 juillet et 4 août 2026 - Décaissements de 653.000.000 FCFA attendus"),
    ("PUR-ZEDAGA", "Conseil Agricole", "Appel du DG à la DG/CAGD pour accélérer l'approbation des contrats des 09 prestataires agréés", "Immédiat", "DGFD", "A/DG DMRM", "- Contrats retirés le 4 août 2026 de la CAGD - Signature en cours au niveau du MAEP - Appeler le MAEP pour accélérer"),
    ("PAPC 1", "Contrat complémentaire relatif aux prestations de la MDC", "Transmettre le dossier relatif à la requête de contrat complémentaire à la CAGD pour traitement", "7-Aug-26", "UGP SIRAT", "Pôle de Suivi MEF", "- Dossier transmis à la CAGD le 6 août 2026, en cours de traitement - Angelo relancé les 7 et 14 août 2026"),
    ("PAPC 1", "Contrat complémentaire relatif aux prestations de la MDC", "Transmettre la requête relative au contrat complémentaire à la BOAD", "18-Aug-26", "CAGD", "UGP SIRAT Pôle de Suivi MEF", "- Dossier en cours de finalisation à la CAGD - Transmission à la BOAD le 18 août 2026 au plus tard"),
    ("PAPC 2", "Validation des rapports EIES et PAR des travaux", "Faire un mail de relance à la CMR sur le dossier", "3-Aug-26", "DGFD", "A/DG DMRM", "- Point actualisé des ANO transmis à Hafiz le 7 août 2026 (CMR et Task Manager en copie) - Relance sur l'ANO de la BOAD attendu (rapports EIES/PAR envoyés le 25 février 2026)"),
    ("PAPC 2", "Obtention du CCE", "Appel au DG/ABE pour accélérer le processus de validation des EIES et d'obtention du CCE", "Immédiat", "DGFD", "A/DG DMRM", "- Appel effectué - Validation des EIES en cours à l'ABE - CCE attendu d'ici fin août 2026"),
    ("PAPC 2", "Approbation du contrat de la MDC", "Reprendre le contrat et faire un mémo en annexe, conformément au contrat type déjà validé avec le PAPVS", "17-Aug-26", "UGP", "Pôle de Suivi MEF", "- Contact pris avec PAPVS, documents reçus le 6 août 2026 - Contrat réédité envoyé au Consultant pour signature. Retour attendu le 17 août 2026 au plus tard"),
    ("PAPC 2", "Approbation du contrat de la MDC", "Transmettre le contrat et le mémo à la CAGD pour signature", "26-Aug-26", "UGP SIRAT", "Pôle de Suivi MEF", "- Transmission à la CAGD le 26 août 2026 au plus tard (DG/SIRAT en congés 3 semaines, reprise le 24 août 2026)"),
    ("PRC Lot 4", "Revue de la structure de la chaussée", "Appel du DG au DG/SIRAT pour discuter sur la prise d'avenant relatif à la revue technique de la structure de la chaussée", "Immédiat", "DGFD", "A/DG DMRM", "- Réunion avec la BOAD programmée en septembre pour l'accord de principe - Avenant de 8.000.000.000 FCFA pour la revue de la structure de la chaussée"),
    ("PROMER", "DAO lot 4", "Appeler le DG/SBEE pour instruire la PRMP/SBEE pour accélérer le lancement du DAO du lot 4", "7-Aug-26", "DGFD", "A/DG DMRM", "- DAO finalisé et non encore lancé"),
    ("ProSeR 1", "Travaux d'aménagement sur le CPP", "Organiser une réunion avec l'entreprise CECO et l'UGP sur le dossier", "30-Jul-26", "Pôle de Suivi MEF", "UGP PRMP/MAEP CECO", "- Réunion faite le 30 juillet 2026 - Accélérer le traitement des décomptes - ANO de la BOAD sur l'avenant au contrat de CECO - Réunion projetée dernière semaine d'août 2026"),
    ("ProSeR 1", "Financement des travaux pour la réhabilitation de la piste d'accès au CPP", "Envoyer une correspondance à la SIRAT pour procéder à une évaluation du coût réel des travaux, sur la base des études existantes", "7-Aug-26", "UGP", "Pôle de Suivi MEF", "- Correspondance envoyée à la SIRAT le 3 août 2026 - Dossier en cours d'examen à la SIRAT"),
    ("ProSeR 2", "Indemnisation des PAPs", "Appel du DG au DGB pour diligenter l'avis sur le projet de communication en Conseil des Ministres", "Immédiat", "DGFD", "A/DG DMRM", "- Avis de la DGB obtenu le 22 juillet 2026 - Diligence en cours (UGP et MAEP) pour finaliser le projet de communication d'ici fin août 2026"),
    ("ProSeR 2", "Travaux sur les CPR", "Organiser une réunion technique avec les entreprises sur l'avancement des travaux", "6-Aug-26", "Pôle de Suivi MEF", "UGP Entreprises", "- Réunion tenue le 06 août 2026 - Note synthèse attendue le 17 août 2026 (difficultés des entreprises, sites à problème, plannings et ressources mobilisées)"),
    ("Projet d'appui à la digitalisation des services du MEF (FTD)", "Ouverture du compte d'opération au profit du projet", "Diligenter l'ouverture du compte d'opération au profit du projet", "14-Aug-26", "UGP", "Pôle de Suivi MEF", "- Processus achevé. Conditions de mise en vigueur et de premier décaissement satisfaites et notifiées par la BOAD"),
    ("Projet d'appui à la digitalisation des services du MEF (FTD)", "Mise en place de l'UGP", "Envoyer un mail à la BOAD pour obtenir l'accord de principe sur le processus de recrutement de l'UGP", "31-Jul-26", "UGP", "Pôle de Suivi MEF BOAD", "- Mail envoyé le 30 juillet 2026, accord de principe obtenu - Recrutement en cours"),
    ("Projet d'appui à la digitalisation des services du MEF (FTD)", "Mise en place de l'UGP", "Diligenter le recrutement du SPM", "12-Aug-26", "UGP", "Pôle de Suivi MEF", "- Recrutement en cours - Phase d'analyse des contrats"),
]

n = 0
for (projet, point, reco, delai, resp, assoc, obs) in RECOS:
    sb.table('recommandations').insert({
        'revue_id': revue_id,
        'partenaire': PART,
        'projet': projet,
        'difficulte': point,
        'texte': reco,
        'responsable_direct': resp,
        'associe': assoc,
        'echeance': parse_date(delai),
        'statut': 'a_demarrer',
        'commentaires': obs,
        'avancement': 0,
        'executee': False,
    }).execute()
    n += 1

print(f"✅ {n} recommandations BOAD importées")
c = sb.table('recommandations').select('partenaire').execute().data
print("Répartition:", Counter([x['partenaire'] for x in c]))
print("Total:", sb.table('recommandations').select('id', count='exact').execute().count)
