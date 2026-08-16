# -*- coding: utf-8 -*-
import sys
sys.path.insert(0, '.')
from db import get_supabase

sb = get_supabase()

# 1. Creer (ou recuperer) la revue BAD aout 2026
revues = sb.table('revues').select('id').eq('partenaire', 'BAD').eq('type_revue', 'Revue technique aout 2026').execute().data
if revues:
    revue_id = revues[0]['id']
    print(f"Revue BAD existante (id={revue_id})")
else:
    r = sb.table('revues').insert({
        'partenaire': 'BAD',
        'type_revue': 'Revue technique aout 2026',
        'date_revue': '2026-08-15',
    }).execute()
    revue_id = r.data[0]['id']
    print(f"Revue BAD creee (id={revue_id})")

MOIS = {'jan':1,'fev':2,'mar':3,'avr':4,'mai':5,'juin':6,'juil':7,'aout':8,'sep':9,'oct':10,'nov':11,'dec':12}
def parse_date(s):
    if not s: return None
    s = str(s).strip().lower().replace('û','u').replace('é','e').replace('è','e')
    if s in ('immediat', 'immediate', '-', ''): return None
    try:
        parts = s.split('-')
        if len(parts) == 3:
            j = int(parts[0]); m = MOIS.get(parts[1], 1); a = int(parts[2])
            if a < 100: a += 2000
            return f"{a:04d}-{m:02d}-{j:02d}"
    except: pass
    return None

RECOS = [
    ("PRODEFILAV-PEL", "Recrutement du personnel", "Accélérer la publication de l'AMI pour le recrutement du Coordonnateur et de l'Expert Genre", "27-juil-26", "UGP MAEP", "Pôle de Suivi MEF", "- AMI lancé le 28 juillet 2026 - Réception et ouverture des plis le 10 août 2026 - Dépouillement et évaluation en cours - Transmission du rapport d'évaluation à la BAD pour ANO, fin août 2026 au plus tard."),
    ("PRODEFILAV-PEL", "Recrutement du personnel", "Transmettre les TDRs et AMI à la BAD pour le recrutement du SPM et de l'A/SPM", "31-juil-26", "UGP MAEP", "Pôle de Suivi MEF", "- TDRs et AMI transmis à la BAD le 3 août 2026, pour ANO. En attente de l'ANO de la BAD. - Relance faite le 12 août 2026 - Lancement de l'AMI projeté pour fin août 2026 au plus tard."),
    ("PRODEFILAV-PEL", "Restructuration du projet", "Organiser une réunion sur la restructuration du projet", "07-aout-26", "Pôle de Suivi MEF", "UGP MAEP", "- Réunion tenue le jeudi 06 août 2026 à 8H30."),
    ("PRODEFILAV-PEL", "Restructuration du projet", "Transmettre au Pôle de Suivi MEF la note de restructuration détaillée", "11-aout-26", "UGP", "Pôle de Suivi MEF", "- Note récapitulative transmise le 11 août 2026. - Note détaillée attendue le 17 août 2026. - Réunion de validation programmée pour début septembre 2026."),
    ("PRODEFILAV-PEL", "Désignation de l'Agent comptable public", "Procéder à la désignation du RAF ATDA2 comme agent public comptable du projet", "31-juil-26", "MAEP UGP", "Pôle de Suivi MEF", "- Lettre de désignation déjà signée par le MAEP, le 31 juillet 2026"),
    ("PRODEFILAV-PEL", "Avancement des travaux", "Organiser une réunion technique sur l'état d'avancement des activités du projet", "10-aout-26", "Pôle de Suivi MEF", "UGP DPAF/MAEP", "- Réunion technique tenue le 4 août 2026 avec le Chargé du projet au niveau de la BAD - Planning d'exécution en cours de finalisation pour transmission au Pôle de Suivi MEF, le 14 août 2026 au plus tard."),
    ("PRODEFILAV-PEL", "Specimen du Coordonnateur", "Transmettre à la CAGD les specimen de signature du Coordonnateur par intérim", "03-aout-26", "DGFD", "A/DG DMRM", "- Dossier transmis à la CAGD le 4 août 2026 - Transmission à la BAD le 11 août 2026."),
    ("PROMAC", "Signature des bons de commandes en instance", "Diligenter la signature par le MAEP des bons de commandes pour l'acquisition d'aliments granulés et la mise en place d'enclos piscicoles", "31-juil-26", "MAEP UGP", "Pôle de Suivi MEF", "- Bons de commande en instance de signature au niveau du MAEP (processus bloqué). - Coordonnateur et PRMP/MAEP relancés les 03 et 12 août 2026."),
    ("PROMAC", "Signature des bons de commandes en instance", "Transmettre les bons de commande à la CAGD pour signature et approbation par le MMG", "05-aout-26", "MAEP UGP", "Pôle de Suivi MEF", "- Bons de commande encore en instance de signature par le MAEP. Processus bloqué."),
    ("PROMAC", "Restructuration du projet", "Organiser une réunion sur la restructuration du projet", "07-aout-26", "Pôle de Suivi MEF", "UGP MAEP", "- Réunion tenue le jeudi 06 août 2026 à 8H30."),
    ("PROMAC", "Restructuration du projet", "Transmettre au Pôle de Suivi MEF la note de restructuration détaillée", "14-aout-26", "UGP", "Pôle de Suivi MEF", "- En attente d'une note détaillée avec indicateurs et délais précis. - Document attendu pour le 14 août 2026 au plus tard - Focus sur: (i) Villages aquacoles; (ii) embarcadères/débarcadères; (iii) marchés à poissons."),
    ("PROMAC", "Restructuration du projet", "Diligenter l'ANO de la BAD sur le PPM révisé", "14-aout-26", "BAD", "Pôle de Suivi MEF, UGP MAEP", "- Observations de la BAD sur le PPM, reçue le 12 août 2026 - Transmission du PPM révisé avec complément d'informations, le 13 août 2026 au plus tard."),
    ("PROMAC", "Recrutement du Consultant en charge du rapport de restructuration", "Faire un point au MAEP sur la situation du PROMAC et solliciter son appui pour accélérer le recrutement", "07-aout-26", "DGFD", "A/DG DMRM, C/SBIR", "- Proposition de message fait et envoyé au DG le 6 août 2026."),
    ("PROMAC", "Recrutement du Consultant en charge du rapport de restructuration", "Transmettre les TDRs et AMI à la BAD pour ANO", "17-aout-26", "UGP", "MAEP, Pôle de Suivi MEF", "- TDRs et AMI finalisés et en attente de l'ANO sur le PPM - Transmission projetée pour le 17 août 2026 au plus tard."),
    ("PAPVS", "Exécution des travaux sur Abomey Bohicon", "Transmettre au Pôle de Suivi MEF les plannings d'exécution des travaux des entreprises et de la MDC", "17-aout-26", "UGP Entreprises MDC", "Pôle de Suivi MEF", "- Mission de terrain en cours jusqu'au 7 août 2026. - Plannings d'exécution attendus le 17 août 2026 mais risque de non respect du délai car UGP en congés - Transmission projetée pour le 24 août 2026."),
    ("PAPVS", "Approbation du Contrat de la MDC des travaux Porto-Novo et Ouidah", "Reprendre le processus de signature du contrat et soumettre à la CAGD", "31-juil-26", "UGP SIRAT", "Pôle de Suivi MEF", "- Contrat déjà signé par le DG/SIRAT le 3 août 2026 et transmis à la CAGD le 4 août 2026 - En instance d'approbation par le MMG."),
    ("PAPVS", "Etude pour la gestion des déchets et l'entretien des ouvrages", "Accélérer la signature du rapport d'évaluation des offres", "05-aout-26", "UGP SIRAT", "Pôle de Suivi MEF", "- Rapport validé par la PRMP/SIRAT le 30 juillet 2026 - Transmis à la CCMP le 3 août 2026 pour avis (processus bloqué). Urgence d'appeler le DG/SIRAT pour instructions à donner à la CCMP."),
    ("PAPVS", "Acquisition d'équipements de pré-collecte et collecte", "Transmettre le rapport d'évaluation des offres à la BAD pour ANO", "29-juil-26", "UGP SIRAT", "Pôle de Suivi MEF", "- Rapport d'évaluation transmis à la BAD le 31 juillet 2026 - En attente de l'ANO de la Banque. Relance faite le 12 août 2026."),
    ("PRC", "Mise en oeuvre de la Composante B du projet", "Finaliser le DAO relatif aux travaux de pistes connexes et transmettre à la BAD pour ANO", "14-aout-26", "UGP SIRAT", "Pôle de Suivi MEF", "- Rapport APD validé le 27 juillet 2026 - Elaboration du DAO avec les spécifications en cours pour transmission à la BAD - Lancement du DAO prévu pour septembre 2026."),
    ("PRC", "Mise en oeuvre de la Composante B du projet", "Transmettre au Pôle de Suivi MEF le chronogramme d'exécution pour les infrastructures marchandes", "07-aout-26", "UGP SIRAT", "Pôle de Suivi MEF", "- Réunion avec le Cabinet le 31 juillet 2026. Livrables attendus: rapport d'identification des sites, APD et DAO - Chronogramme transmis le 11 août 2026. - Le délai d'exécution des travaux dépasse la date de clôture du projet (risque de non achèvement ou prorogation de 12 mois à envisager)."),
    ("PDSECP 1", "Recrutement des BET", "Transmettre le rapport d'évaluation des offres à la BAD pour ANO", "31-aout-26", "UGP ADET ACISE", "Pôle de Suivi MEF", "- Ouverture des offres faite le 28 juillet 2026 - Evaluation projetée du 10 au 31 août 2026 - Transmission du rapport d'évaluation prévue pour le 11 septembre 2026 au plus tard."),
    ("PDSECP 1", "Recrutement des BCT", "Transmettre les TDRs et la DP révisés à la BAD", "05-aout-26", "UGP ADET", "Pôle de Suivi MEF", "- TDRs et DP révisés transmis à la BAD le 30 juillet 2026, pour ANO. En attente du retour de la Banque - Relance faite le 12 août 2026."),
    ("PDSECP 1", "Passation de marchés", "Transmettre au Pôle de Suivi MEF le point actualisé du niveau d'avancement des marchés sur le projet", "14-aout-26", "UGP ADET", "Pôle de Suivi MEF", "- Mail envoyé au Coordonnateur le 13 août 2026 - Ces marchés concernent entre autres: DAOI, BCT, BET, Audit 2025, ONG Athiémé et Kpomassè, etc."),
    ("PRESREDI", "Annulation de l'activité relative au reboisement compensatoire", "Discuter avec le DG/SBEE pour programmer une séance de travail sur les points de blocage du projet", "07-aout-26", "DGFD", "A/DG DMRM", "- Réunion non tenue. Urgence de discuter avec le DG/SBEE - Nécessité de programmer la réunion pour discuter sur l'option retenue et relative à l'annulation de cette activité dont le délai d'exécution dépasse la date de clôture du projet, fixée au 30 septembre 2026."),
    ("PRESREDI", "Audit 2025 et de clôture", "Transmettre le rapport d'évaluation révisé des offres techniques à la BAD pour ANO", "30-juil-26", "UGP SBEE", "Pôle de Suivi MEF", "- Rapport révisé transmis à la BAD le 29 juillet 2026 - ANO de la BAD obtenu le 05 août 2026."),
    ("PRESREDI", "Audit 2025 et de clôture", "Notifier par écrit les résultats aux 02 consultants qualifiés et les inviter à l'ouverture publique des offres financières", "06-aout-26", "UGP SBEE", "Pôle de Suivi MEF", "- Notification faites et ouverture des offres financières faite le 13 août 2026."),
    ("PRESREDI", "Audit 2025 et de clôture", "Procéder aux négociations et élaborer le PV de négociations", "18-aout-26", "UGP SBEE", "Pôle de Suivi MEF", ""),
    ("PRESREDI", "Audit 2025 et de clôture", "Transmettre le rapport d'évaluation combinée à la BAD pour ANO", "25-aout-26", "UGP SBEE", "Pôle de Suivi MEF", "- Signature du contrat projetée pour le 25 septembre 2026 - Transmission du rapport à la BAD (exercices 2025, 2026 et clôture), le 13 novembre 2026."),
    ("PERU 1", "Recrutement du personnel clé du projet", "Diligenter la signature des contrats du Comptable, du SPM, de l'Environnementaliste, du Spécialiste Genre et du RAF", "03-aout-26", "UGP SBEE", "Pôle de Suivi MEF", "- Contrats signés par le DG/SBEE le 30 juillet 2026 - Prise de service le 03 août 2026 pour les 05 postes."),
    ("PERU 1", "Recrutement du personnel clé du projet", "Procéder au lancement de l'AMI pour le recrutement de l'Ingénieur Génie Civil", "03-aout-26", "UGP SBEE", "Pôle de Suivi MEF", "- AMI lancé et réception des offres prévue le 25 août 2026 - Evaluation prévue pour fin août et transmission à la BAD, du rapport d'évaluation projetée pour mi-septembre 2026 au plus tard."),
    ("PERU 1", "Recrutement du personnel clé du projet", "Prendre une note de service pour la nomination des trois (03) Ingénieurs électriciens mis à la disposition de l'UGP", "17-aout-26", "DG/SBEE", "Pôle de Suivi MEF", "- CV des trois Ingénieurs approuvés par la BAD - Note de service finalisée et soumise à la signature du DG/SBEE le 7 août 2026 - Transmission à la BAD le 18 août 2026 au plus tard."),
    ("PERU 1", "Réattribution du marché SOGETEC", "Transmettre le rapport d'évaluation des offres à la BAD pour ANO", "27-juil-26", "UGP PRMP/SBEE", "Pôle de Suivi MEF", "- Réception des offres le 15 juin 2026 et rapport d'évaluation non encore transmis à la BAD. - Lenteur au niveau de la PRMP/SBEE. Urgence de discuter avec le DG/SBEE pour instruire la PRMP/SBEE."),
    ("PERU 1", "Réactivation du contrat des bureaux de contrôle COLENCO", "Transmettre le PV de négociations et le projet de contrat paraphé à la BAD pour ANO", "17-aout-26", "UGP SBEE", "Pôle de Suivi MEF", "- Négociations tenues avec le Cabinet COLENCO et projet de contrat transmis au Cabinet pour paraphe le 13 août 2026 - Transmission du PV de négociations et du contrat paraphé à la BAD le 17 août 2026 au plus tard."),
    ("PERU 1", "Dossiers de passation en souffrance à la SBEE", "Retirer les dossiers au niveau de la PRMP/SBEE et transmettre à la BAD, via le SPM recruté", "14-aout-26", "UGP", "Pôle de Suivi MEF", "- Passation de service entre le SPM intérim et le SPM recruté, le 13 août 2026 et retrait des dossiers - Transmission à la BAD le 14 août 2026 au plus tard."),
    ("PROTAS P1", "Recrutement du personnel", "Accélérer la reprise du processus de recrutement du personnel du projet", "", "MAEP", "Pôle de Suivi MEF", "- TDRs et AMI révisés transmis à la BAD le 12 août 2026 (sur instruction du MAEP, quelques ajustements ont été proposés aux TDRs relatifs au recrutement du personnel clé). - Frais de publication à prendre en charge sur les ressources du PROMAC."),
    ("PROTAS P1", "Recrutement du personnel", "Echanger avec le MAEP sur les postes clés et la conduite du processus", "", "DGFD", "A/DG DMRM", "- Postes clés: Coordonnateur; SPM et RAF - MAEP en congés (échanges prévus dès la reprise)."),
    ("PreRAB", "Recrutement du personnel", "Accélérer la reprise du processus de recrutement du personnel du projet", "", "MAEP", "Pôle de Suivi MEF", "- TDRs et AMI révisés transmis à la BAD le 12 août 2026 (sur instruction du MAEP, quelques ajustements ont été proposés). - Frais de publication à prendre en charge sur les ressources du PROMAC."),
    ("PreRAB", "Recrutement du personnel", "Echanger avec le MAEP sur les postes clés et la conduite du processus", "", "DGFD", "A/DG DMRM", "- Postes clés: Coordonnateur; SPM et RAF - MAEP en congés (échanges prévus dès la reprise)."),
    ("PIDACC/BN", "Convention SoBAA", "Transmettre le projet de convention à la CAGD pour examen", "", "UGP", "Pôle de Suivi MEF", "- Projet de convention transmis à la CAGD le 06 août 2026, pour examen - En attente du retour de la CAGD, le 14 août 2026."),
    ("PIDACC/BN", "Convention SoBAA", "Transmettre le projet de convention à la BAD pour ANO", "18-aout-26", "UGP", "Pôle de Suivi MEF", ""),
    ("PIDACC/BN", "Dossiers en instance d'ANO au niveau de la BAD", "Envoyer un mail de relance à la BAD sur les dossiers en instance d'ANO", "27-juil-26", "Pôle de Suivi MEF", "UGP BAD", "- Mails de relance envoyés les 24 juillet et 3 août 2026. - Aucun retour à ce jour. Nécessité d'une réunion sur le projet."),
    ("PADECT", "Recrutement du spécialiste en gestion financière", "Accélérer le recrutement du RAF et le processus de nomination des autres membres de l'UGP", "", "C/SPEF", "Pôle de Suivi MEF", "- En attente de la programmation des réunions de la Commission de recrutement - Projet mis en vigueur le 4 avril 2026. Urgence de discuter avec CSPEF pour éviter que le projet soit flashé rouge (dépassement de la date limite). - Décaissement de 25% du financement global, après satisfaction des conditions préalables au premier décaissement."),
    ("Ouidah-Hillacondji", "Approbation du projet", "Accélérer la signature des fiches d'entente individuelles des PAPs", "07-aout-26", "UGP SIRAT", "Pôle de Suivi MEF", "- 2442 fiches d'entente ont été signées sur 3009 soit un taux de 81.15% à la date 04/05/2026."),
]

n = 0
for (projet, difficulte, texte, echeance_str, resp, associe, comm) in RECOS:
    sb.table('recommandations').insert({
        'revue_id': revue_id,
        'partenaire': 'BAD',
        'projet': projet,
        'difficulte': difficulte,
        'texte': texte,
        'responsable_direct': resp,
        'associe': associe,
        'echeance': parse_date(echeance_str),
        'statut': 'a_demarrer',
        'commentaires': comm,
        'avancement': 0,
        'executee': False,
    }).execute()
    n += 1

print(f"OK {n} recommandations BAD importées (revue_id={revue_id})")
total = sb.table('recommandations').select('id', count='exact').execute().count
print(f"Total global maintenant: {total}")
