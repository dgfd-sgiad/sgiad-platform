# -*- coding: utf-8 -*-
"""Injection / mise à jour du personnel DGFD dans Supabase."""

from datetime import datetime
from db import get_supabase


# ============================================================
# CONFIGURATION
# ============================================================

TABLE_AGENTS = "conges_agents"
TABLE_DROITS = "conges_droits"

ANNEE_CONGES = 2026
DROIT_ANNUEL = 30

# Mettre True si les colonnes date_retraite, date_naissance, etc.
# sont de type DATE dans Supabase/PostgreSQL.
# Mettre False si tu veux conserver les dates exactement comme texte.
CONVERT_DATES = True

DATE_FIELDS = {
    "date_retraite",
    "date_naissance",
    "date_prise_service",
    "prise_service_structure",
    "date_formation",
}


# ============================================================
# DONNEES PERSONNEL
# ============================================================

D = [
    {
        "m": "64720",
        "nom": "ABIOU Franck Hervé Martial",
        "direction": "DGFD",
        "sexe": "M",
        "poste": "Chargé de Mission à la Mobilisation des Ressources Multilatérales",
        "statut_admin": "FE",
        "date_retraite": "01/07/2032",
        "annee_retraite": "2032",
        "date_naissance": "14/06/1972",
        "date_prise_service": "17/07/2009",
        "prise_service_structure": "17/09/2009",
        "anciennete_fp": "14ans 5ms 14jrs",
        "corps": "Administrateurs",
        "grade": "A1-8",
        "grade_paye": "A1-7",
        "cat_admin": "A",
        "contact": "97694887",
        "diplome": "DESS en Gestion de Projet et Developpement Local en 2006",
        "diplome_reconnu": "DESS en Gestion de Projet et Developpement Local",
        "service_interrompu": "07 ans 01 jours",
    },
    {
        "m": "104885",
        "nom": "ADAMMADO Caddys Espoir",
        "direction": "DMRB/DGFD",
        "sexe": "M",
        "poste": "Chef du Service de Mobilisation des Ressources Zone 2",
        "statut_admin": "ACDPE",
        "date_retraite": "01/07/2046",
        "annee_retraite": "2046",
        "date_naissance": "06/05/1986",
        "date_prise_service": "28/01/2015",
        "prise_service_structure": "24/08/2020",
        "anciennete_fp": "8ans 11ms 03jrs",
        "corps": "Administrateurs",
        "grade": "A1-2",
        "grade_paye": "A1-2",
        "cat_admin": "A",
        "contact": "97537987",
        "diplome": "Diplôme du cycle 2 ENAM en Management des Services Publics, obtenu le 27/05/2013",
        "diplome_reconnu": "Diplôme du cycle 2 ENAM en Management des Services Publics",
        "service_interrompu": "06 ans 18 jours",
    },
    {
        "m": "95603",
        "nom": "AGBAGAN Nonvignon Fermat",
        "direction": "DMRM/DGFD",
        "sexe": "M",
        "poste": "Chef Division des Banques et Institutions Régionales (BOAD, BIDC, UEMOA, CEDEAO)",
        "statut_admin": "ACDPE",
        "date_retraite": "01/01/2039",
        "annee_retraite": "2039",
        "date_naissance": "21/08/1980",
        "date_prise_service": "01/01/2008",
        "prise_service_structure": "27/04/2023",
        "anciennete_fp": "15 ans 11ms 30jrs",
        "corps": "Contrôleurs des Services Techniques des Travaux Publics",
        "grade": "B3-8",
        "grade_paye": "B3-8",
        "cat_admin": "B",
        "contact": "96202888",
        "diplome": "Administrateur en Gestion des projets",
        "diplome_reconnu": "Diplôme du Contrôleur des Services Techniques des TP",
        "service_interrompu": "10 ans",
    },
    {
        "m": "59696",
        "nom": "AMOUSSOU Hermann Wilfried",
        "direction": "DECAD/DGFD",
        "sexe": "M",
        "poste": "Chef Service Etudes et Synthèse",
        "statut_admin": "FE",
        "date_retraite": "01/10/2041",
        "annee_retraite": "2041",
        "date_naissance": "24/09/1981",
        "date_prise_service": "24/10/2011",
        "prise_service_structure": "24/10/2011",
        "anciennete_fp": "12ans 2ms 07jrs",
        "corps": "Ingénieurs de la Statistique",
        "grade": "A1-7",
        "grade_paye": "A1-7",
        "cat_admin": "A",
        "contact": "95223234",
        "diplome": "Diplôme d'Ingénieur Statisticien Economiste en 2007",
        "diplome_reconnu": "Diplôme d'Ingénieur Statisticien Economiste",
        "service_interrompu": "05 ans 15 jours",
    },
    {
        "m": "99263",
        "nom": "AMOUSSOUGA-AKPO Gblèlidji Amandine",
        "direction": "DGFD",
        "sexe": "F",
        "poste": "Chargé de Mission à la Mobilisation des ressources Bilatérales",
        "statut_admin": "FE",
        "date_retraite": "01/07/2039",
        "annee_retraite": "2039",
        "date_naissance": "12/06/1979",
        "date_prise_service": "10/02/2011",
        "prise_service_structure": "15/03/2011",
        "anciennete_fp": "12ans 10ms 21jrs",
        "corps": "Administrateurs",
        "grade": "A1-7",
        "grade_paye": "A1-7",
        "cat_admin": "A",
        "contact": "67258008",
        "diplome": "DESS en gestion des projets et developpement locale en 2008",
        "diplome_reconnu": "DESS en gestion des projets et developpement locale",
        "service_interrompu": "05 ans 03 jours",
    },
    {
        "m": "51191",
        "nom": "APLOGAN Towanou G. Vincent",
        "direction": "DGAR/DGFD",
        "sexe": "M",
        "poste": "Chef Division du Courrier",
        "statut_admin": "FE",
        "date_retraite": "01/04/2027",
        "annee_retraite": "2027",
        "date_naissance": "22/01/1972",
        "date_prise_service": "13/05/2003",
        "prise_service_structure": "30/03/2020",
        "anciennete_fp": "20ans 7ms 18jrs",
        "corps": "Préposés des Services Administratifs",
        "grade": "D3-9",
        "grade_paye": "D3-9",
        "cat_admin": "D",
        "contact": "97070079",
        "diplome": "CEFEB en 1988",
        "diplome_reconnu": "CEFEB",
        "service_interrompu": "11 ans 08 jours",
    },
    {
        "m": "104001",
        "nom": "ASSAVEDO Karl",
        "direction": "DMRM/DGFD",
        "sexe": "M",
        "poste": "Chef du Service des Banques et Institutions Régionales",
        "statut_admin": "ACDPE",
        "date_retraite": "01/07/2049",
        "annee_retraite": "2049",
        "date_naissance": "02/05/1989",
        "date_prise_service": "28/01/2015",
        "prise_service_structure": "01/03/2015",
        "anciennete_fp": "8ans 11ms 03jrs",
        "corps": "Techniciens Supérieurs de la Planification",
        "grade": "A3-3",
        "grade_paye": "A3-2",
        "cat_admin": "A",
        "contact": "96742291",
        "diplome": "Diplôme de Technicien Supérieur en économie/Planification en date du 20/03/2013",
        "diplome_reconnu": "Diplôme de Technicien Supérieur en économie",
        "service_interrompu": "07 ans 03 jours",
    },
    {
        "m": "106415",
        "nom": "ATCHADE Firmin",
        "direction": "DMRB/DGFD",
        "sexe": "M",
        "poste": "Chef du Service de Mobilisation des Ressources Zone 3",
        "statut_admin": "ACDPE",
        "date_retraite": "01/10/2047",
        "annee_retraite": "2047",
        "date_naissance": "18/08/1989",
        "date_prise_service": "02/04/2015",
        "prise_service_structure": "06/11/2019",
        "anciennete_fp": "08ans 08ms 29jrs",
        "corps": "Secrétaires des Services Administratifs",
        "grade": "B3-3",
        "grade_paye": "B3-2",
        "cat_admin": "B",
        "contact": "96098252",
        "diplome": "DESS en Finances et Contrôle de Gestion obtenu en 2021",
        "diplome_reconnu": "BAC D",
        "service_interrompu": "02 ans 08 jours",
    },
    {
        "m": "65695",
        "nom": "AVOGNON Apolinaire Wilfrid",
        "direction": "UGC-UNSDCF/DGFD",
        "sexe": "M",
        "poste": "Chargé de Programme de Coordination UNSDCF",
        "statut_admin": "ACDPE",
        "date_retraite": "01/04/2044",
        "annee_retraite": "2044",
        "date_naissance": "25/03/1984",
        "date_prise_service": "01/01/2008",
        "prise_service_structure": "03/11/2012",
        "anciennete_fp": "15ans 11ms 30jrs",
        "corps": "Professeur certifié",
        "grade": "A1-7",
        "grade_paye": "A1-7",
        "cat_admin": "A",
        "contact": "97717360",
        "diplome": "Master Gestion des Projets et Développement local en 2021",
        "diplome_reconnu": "Master/Sciences et Techniques Administratives et de Gestion (CAPET)",
        "date_formation": "01/10/2021",
        "service_interrompu": "01 an 23 jours",
    },
    {
        "m": "83300",
        "nom": "BABA Rahimatou",
        "direction": "DMRB/DGFD",
        "sexe": "F",
        "poste": "Directrice de la Mobilisation Ressources Bilaterales",
        "statut_admin": "FE",
        "date_retraite": "01/10/2038",
        "annee_retraite": "2038",
        "date_naissance": "23/08/1978",
        "date_prise_service": "06/06/2005",
        "prise_service_structure": "22/07/2019",
        "anciennete_fp": "18ans 6ms 25jrs",
        "corps": "Administrateurs",
        "grade": "A1-8",
        "grade_paye": "A1-7",
        "cat_admin": "A",
        "contact": "97877030",
        "diplome": "Diplôme du cycle 2 de l'ENAM en gestion de projets le 14/05/2013",
        "diplome_reconnu": "Diplôme du cycle 2 de l'ENAM en gestion de projets",
        "date_formation": "24/04/2013",
        "service_interrompu": "02 ans",
    },
    {
        "m": "89566",
        "nom": "BABADOUDOU Armel Landry De-Frunhor",
        "direction": "DMRB/DGFD",
        "sexe": "M",
        "poste": "Chef du Service de Mobilisation des Ressources Zone 1",
        "statut_admin": "FE",
        "date_retraite": "01/07/2041",
        "annee_retraite": "2041",
        "date_naissance": "25/04/1981",
        "date_prise_service": "28/09/2009",
        "prise_service_structure": "03/01/2022",
        "anciennete_fp": "14ans 3ms 3jrs",
        "corps": "Techniciens Supérieurs de la Planification",
        "grade": "A3-8",
        "grade_paye": "A3-7",
        "cat_admin": "A",
        "contact": "96302039",
        "diplome": "Master 2 du COFEB/BCEAO en finances et gestion bancaire obtenu le 14/04/2021",
        "diplome_reconnu": "DTS en Planification et Amenagement du Territoire",
        "service_interrompu": "03 ans 17 jours",
    },
    {
        "m": "104814",
        "nom": "CHICHE Baba Durotini Belgrande Y.",
        "direction": "DGAR/DGFD",
        "sexe": "F",
        "poste": "Chef Division Finances et Comptabilité",
        "statut_admin": "ACDPE",
        "date_retraite": "01/07/2048",
        "annee_retraite": "2048",
        "date_naissance": "08/06/1990",
        "date_prise_service": "02/02/2015",
        "prise_service_structure": "09/04/2018",
        "anciennete_fp": "8ans 6ms 25jrs",
        "corps": "Contrôleurs des Services Financiers",
        "grade": "B3-3",
        "grade_paye": "B3-2",
        "cat_admin": "B",
        "contact": "61656609",
        "diplome": "BAC D obtenu en 2010",
        "diplome_reconnu": "BAC D",
        "service_interrompu": "01 an 08 jours",
    },
    {
        "m": "100478",
        "nom": "COMAHOUE Coffi Cécé Rock",
        "direction": "DGFD",
        "sexe": "M",
        "poste": "Assistant du DGFD",
        "statut_admin": "ACDPE",
        "date_retraite": "01/04/2037",
        "annee_retraite": "2037",
        "date_naissance": "05/01/1979",
        "date_prise_service": "01/01/2008",
        "prise_service_structure": "25/09/2017",
        "anciennete_fp": "15ans 11ms 30jrs",
        "corps": "Administrateurs des Services Financiers",
        "grade": "A1-2",
        "grade_paye": "B3-2",
        "cat_admin": "A",
        "contact": "97087359",
        "diplome": "Master en Administration des Finances",
        "diplome_reconnu": "BAC D",
        "date_formation": "21/12/2020",
        "service_interrompu": "04 ans 13 jours",
    },
    {
        "m": "56494",
        "nom": "DASSI Bertin",
        "direction": "UGC-UNSDCF/DGFD",
        "sexe": "M",
        "poste": "Conducteurs de Véhicules Administratifs",
        "statut_admin": "ACDPE",
        "date_retraite": "01/10/2028",
        "annee_retraite": "2028",
        "date_naissance": "09/09/1973",
        "date_prise_service": "01/01/2008",
        "prise_service_structure": "06/06/2017",
        "anciennete_fp": "15ans 11ms 30jrs",
        "corps": "Conducteurs de Véhicules Administratifs",
        "grade": "D3-8",
        "grade_paye": "D3-8",
        "cat_admin": "D",
        "contact": "97725590",
        "diplome": "CAP AC en 2016",
        "diplome_reconnu": "CEFEB",
        "service_interrompu": "02 ans 15 jours",
    },
    {
        "m": "82025",
        "nom": "DENAKPO Adjouavi Emilie Chareth Carole",
        "direction": "DECAD/DGFD",
        "sexe": "F",
        "poste": "Chef Division Secrétariat de la DECAD",
        "statut_admin": "FE",
        "date_retraite": "01/01/2039",
        "annee_retraite": "2039",
        "date_naissance": "15/10/1983",
        "date_prise_service": "24/05/2004",
        "prise_service_structure": "18/08/2016",
        "anciennete_fp": "19ans 07ms 07jrs",
        "corps": "Secrétaires Adjoints des Services Administratifs",
        "grade": "C3-10",
        "grade_paye": "C3-10",
        "cat_admin": "C",
        "contact": "96310906",
        "diplome": "BAC G1 en 2016",
        "diplome_reconnu": "BEPC+ Attestation d'opérateur de saisie",
        "service_interrompu": "03 ans 15 jours",
    },
    {
        "m": "77055",
        "nom": "DJEGUEDE Mirène Carolle",
        "direction": "DGAR/DGFD",
        "sexe": "F",
        "poste": "Chef du Secrétariat Administratif",
        "statut_admin": "FE",
        "date_retraite": "01/01/2042",
        "annee_retraite": "2042",
        "date_naissance": "24/12/1983",
        "date_prise_service": "28/09/2009",
        "prise_service_structure": "13/05/2019",
        "anciennete_fp": "14ans 3ms 03jrs",
        "corps": "Secrétaires des Services Administratifs",
        "grade": "B1-8",
        "grade_paye": "B1-7",
        "cat_admin": "B",
        "contact": "97647925",
        "diplome": "BTS en secrétariat bureautique",
        "diplome_reconnu": "BTS en secrétariat bureautique",
        "service_interrompu": "06 ans 25 jours",
    },
    {
        "m": "56478",
        "nom": "DJOSSOU Yaovi Jerôme",
        "direction": "DGAR/DGFD",
        "sexe": "M",
        "poste": "Conducteurs de Véhicules Administratifs",
        "statut_admin": "ACDPE",
        "date_retraite": "01/01/2032",
        "annee_retraite": "2032",
        "date_naissance": "14/10/1976",
        "date_prise_service": "01/01/2008",
        "prise_service_structure": "01/03/2016",
        "anciennete_fp": "15ans 11ms 30jrs",
        "corps": "Conducteurs de Véhicules Administratifs",
        "grade": "D3-8",
        "grade_paye": "D3-8",
        "cat_admin": "D",
        "contact": "95445287",
        "diplome": "Permis de conduire obtenu en 1997",
        "diplome_reconnu": "CEFEB",
        "service_interrompu": "07 ans 12 jours",
    },
    {
        "m": "64716",
        "nom": "DJOTO SEHIZOUN Luc Antoine",
        "direction": "UGC-UNSDCF/DGFD",
        "sexe": "M",
        "poste": "Chargé de Programme Appropriation Capitalisation",
        "statut_admin": "FE",
        "date_retraite": "01/01/2030",
        "annee_retraite": "2030",
        "date_naissance": "12/11/1969",
        "date_prise_service": "17/07/2009",
        "prise_service_structure": "10/10/2017",
        "anciennete_fp": "14ans 5ms 14jrs",
        "corps": "Administrateurs",
        "grade": "A1-8",
        "grade_paye": "A1-7",
        "cat_admin": "A",
        "contact": "95573206",
        "diplome": "DESS en Gestion des Projets et developpement locale en 2007",
        "diplome_reconnu": "DESS en Gestion des Projets et developpement locale",
        "service_interrompu": "05 ans 15 jours",
    },
    {
        "m": "56532",
        "nom": "DOSSOU Mahougnon Sylvie",
        "direction": "UGC-UNSDCF/DGFD",
        "sexe": "F",
        "poste": "Chef Division du Secrétariat de l'UGC-UNSDCF",
        "statut_admin": "ACDPE",
        "date_retraite": "01/01/2030",
        "annee_retraite": "2030",
        "date_naissance": "12/10/1974",
        "date_prise_service": "01/01/2008",
        "prise_service_structure": "10/11/2011",
        "anciennete_fp": "15ans 11ms 30jrs",
        "corps": "Assistants des Services Informatiques",
        "grade": "D3-8",
        "grade_paye": "D3-8",
        "cat_admin": "D",
        "contact": "97692116",
        "diplome": "BAC B en 2016",
        "diplome_reconnu": "CEFEB + Diplôme d'Opérateur de saisie",
        "service_interrompu": "02 ans 05 jours",
    },
    {
        "m": "83154",
        "nom": "DOTOU Hortense Laure K.",
        "direction": "DGAR/DGFD",
        "sexe": "F",
        "poste": "Directrice de la Gestion Administrative et des ressources",
        "statut_admin": "FE",
        "date_retraite": "01/04/2036",
        "annee_retraite": "2036",
        "date_naissance": "11/01/1976",
        "date_prise_service": "04/04/2005",
        "prise_service_structure": "03/01/2022",
        "anciennete_fp": "18ans 8ms 27jrs",
        "corps": "Administrateurs des Services Financiers",
        "grade": "A1-8",
        "grade_paye": "A1-7",
        "cat_admin": "A",
        "contact": "97830747",
        "diplome": "Master 2 en Administration des Finances et Trésor obtenu le 14/02/2012",
        "diplome_reconnu": "Master 2 en Administration des Finances et Trésor",
        "date_formation": "20/04/2012",
        "service_interrompu": "08 ans 08 jours",
    },
    {
        "m": "56498",
        "nom": "GANHOUNOUTO Simon Romuald Codjo",
        "direction": "DECAD/DGFD",
        "sexe": "M",
        "poste": "Chef Division des Politiques et Stratégies de Promotion des Investissements Privés",
        "statut_admin": "ACDPE",
        "date_retraite": "01/01/2027",
        "annee_retraite": "2027",
        "date_naissance": "28/10/1968",
        "date_prise_service": "01/01/2008",
        "prise_service_structure": "26/09/2017",
        "anciennete_fp": "15ans 11ms 30jrs",
        "corps": "Secrétaires des Services Administratifs",
        "grade": "B3-8",
        "grade_paye": "B3-8",
        "cat_admin": "B",
        "contact": "95812377",
        "diplome": "BAC C en 2003",
        "diplome_reconnu": "BAC C",
        "service_interrompu": "05 ans 23 jours",
    },
    {
        "m": "35984",
        "nom": "GANSE Cohovi Georges",
        "direction": "UGC-UNSDCF/DGFD",
        "sexe": "M",
        "poste": "Assistant Administratif et Financier à l'UGC-UNSDCF",
        "statut_admin": "FE",
        "date_retraite": "01/07/2030",
        "annee_retraite": "2030",
        "date_naissance": "23/04/1970",
        "date_prise_service": "29/12/1995",
        "prise_service_structure": "02/05/2017",
        "anciennete_fp": "28ans 2jrs",
        "corps": "Administrateurs des Banques et Institutions Financières",
        "grade": "A1-9",
        "grade_paye": "A1-9",
        "cat_admin": "A",
        "contact": "97441449",
        "diplome": "DESBF obtenu le 02/11/2007",
        "diplome_reconnu": "DESBF",
        "date_formation": "02/11/2007",
        "service_interrompu": "13 ans 15 jours",
    },
    {
        "m": "84472",
        "nom": "GNACADJA Comlan Aristide Erick",
        "direction": "DECAD/DGFD",
        "sexe": "M",
        "poste": "Chef Division du Système de gestion de l'Information sur le Financement du Développement",
        "statut_admin": "FE",
        "date_retraite": "01/10/2036",
        "annee_retraite": "2036",
        "date_naissance": "30/09/1976",
        "date_prise_service": "11/07/2005",
        "prise_service_structure": "14/03/2018",
        "anciennete_fp": "18ans 5ms 20jrs",
        "corps": "Techniciens Supérieurs de la Statistique",
        "grade": "A3-7",
        "grade_paye": "A3-6",
        "cat_admin": "A",
        "contact": "95857799",
        "diplome": "Master2 en Statistique en 2010, Master 2 en Politique Economique et Développement en 2009",
        "diplome_reconnu": "Diplôme de Technicien Supérieur de la Statistique",
        "service_interrompu": "05 ans 08 jours",
    },
    {
        "m": "56499",
        "nom": "GNANMAKOU Félix Obossou",
        "direction": "DECAD/DGFD",
        "sexe": "M",
        "poste": "Chef Service des Bourses et Stage de Formation",
        "statut_admin": "ACDPE",
        "date_retraite": "01/04/2027",
        "annee_retraite": "2027",
        "date_naissance": "25/03/1967",
        "date_prise_service": "01/01/2008",
        "prise_service_structure": "01/04/2020",
        "anciennete_fp": "15ans 11ms 30jrs",
        "corps": "Attachés des Services Administratifs",
        "grade": "A1-6",
        "grade_paye": "A3-8",
        "cat_admin": "A",
        "contact": "97644848",
        "diplome": "DESS en Socio-Anthropologie de l'environnement en 2007, DESS en gestion des projet de developpement local en 2018",
        "diplome_reconnu": "Maitrise en sociologie",
        "date_formation": "2016",
        "service_interrompu": "04 ans",
    },
    {
        "m": "45872",
        "nom": "GUENDEHOU Francis Léo",
        "direction": "DMRB/DGFD",
        "sexe": "M",
        "poste": "Chef Division Amérique et Océanie",
        "statut_admin": "FE",
        "date_retraite": "01/01/2031",
        "annee_retraite": "2031",
        "date_naissance": "09/12/1971",
        "date_prise_service": "03/03/2003",
        "prise_service_structure": "14/11/2022",
        "anciennete_fp": "20ans 9ms 28jrs",
        "corps": "Administrateurs",
        "grade": "A1-4",
        "grade_paye": "B1-10",
        "cat_admin": "A",
        "contact": "97085034",
        "diplome": "Master 2 en management des ressources humaines",
        "diplome_reconnu": "BAC G1",
        "date_formation": "21/10/2017",
        "service_interrompu": "01 an 23 jours",
    },
    {
        "m": "75351",
        "nom": "HOUNDEGNON GBAï Judith",
        "direction": "UGC-UNSDCF/DGFD",
        "sexe": "F",
        "poste": "Coordonnateur de L'UGC-UNSDCF",
        "statut_admin": "FE",
        "date_retraite": "01/07/2044",
        "annee_retraite": "2044",
        "date_naissance": "25/05/1984",
        "date_prise_service": "17/08/2009",
        "prise_service_structure": "04/06/2015",
        "anciennete_fp": "2015",
        "corps": "Ingénieurs de la Planification",
        "grade": "A1-5",
        "grade_paye": "A1-4",
        "cat_admin": "A",
        "contact": "97646888",
        "diplome": "Maitrise en Administration des Affaires (MBA)/Gestion Stratégique de Projets obtenu le 31/05/2020",
        "diplome_reconnu": "Diplôme de Technicien Superieur de la Statistique",
        "date_formation": "31/08/2020",
        "service_interrompu": "03 ans 09 jours",
    },
    {
        "m": "42981",
        "nom": "HOUNKOUNTO ZIME Sémassè Alphonsine",
        "direction": "DMRM/DGFD",
        "sexe": "F",
        "poste": "Chef Division des Fonds Arabes",
        "statut_admin": "FE",
        "date_retraite": "01/10/2037",
        "annee_retraite": "2037",
        "date_naissance": "01/08/1977",
        "date_prise_service": "06/08/2001",
        "prise_service_structure": "27/04/2023",
        "anciennete_fp": "22ans 4ms 22jrs",
        "corps": "Inspecteurs du Trésor",
        "grade": "A3-7",
        "grade_paye": "A3-7",
        "cat_admin": "A",
        "contact": "67353239",
        "diplome": "Master en gestion des projets",
        "diplome_reconnu": "Attestation de formation de mise à niveau des APE admis au concours professionnels au titre de l'année 2012 corps des inspecteurs du trésor",
        "service_interrompu": "02 ans 15 jours",
    },
    {
        "m": "56576",
        "nom": "KEOUDA Valentin",
        "direction": "DGAR/DGFD",
        "sexe": "M",
        "poste": "Agents d'entretien et de Services",
        "statut_admin": "ACDPE",
        "date_retraite": "01/04/2029",
        "annee_retraite": "2029",
        "date_naissance": "14/02/1974",
        "date_prise_service": "01/01/2008",
        "prise_service_structure": "01/07/2022",
        "anciennete_fp": "15ans 11ms 30jrs",
        "corps": "Agents d'entretien et de Services",
        "grade": "E1-9",
        "grade_paye": "E1-8",
        "cat_admin": "E",
        "contact": "95064069",
        "diplome": "CEFEB en 1980+ Permis de Conduire en 2000",
        "diplome_reconnu": "CEFEB",
        "service_interrompu": "13 ans 08 jours",
    },
    {
        "m": "67736",
        "nom": "KOUHONTODE Adjimon Ernest",
        "direction": "DECAD/DGFD",
        "sexe": "M",
        "poste": "Chef Division des Politiques et Stratégies du Financement du Developpement",
        "statut_admin": "FE",
        "date_retraite": "01/10/2037",
        "annee_retraite": "2037",
        "date_naissance": "10/09/1982",
        "date_prise_service": "31/08/2009",
        "prise_service_structure": "05/03/2015",
        "anciennete_fp": "14ans 4ms",
        "corps": "Agents Techniques de la Statistique",
        "grade": "C3-8",
        "grade_paye": "C3-7",
        "cat_admin": "C",
        "contact": "97469461",
        "diplome": "Licence professionnelle en Statistique et Econométrie en 2012",
        "diplome_reconnu": "Diplôme d'Agent Technique de la Statistique",
        "service_interrompu": "04 ans 09 jours",
    },
    {
        "m": "56535",
        "nom": "MADEGNAN Bruno",
        "direction": "UGC-UNSDCF/DGFD",
        "sexe": "M",
        "poste": "Chargé de Programme Appui au suivi Evaluation de l'UGC-UNSDCF",
        "statut_admin": "ACDPE",
        "date_retraite": "01/01/2036",
        "annee_retraite": "2036",
        "date_naissance": "31/12/1974",
        "date_prise_service": "01/01/2008",
        "prise_service_structure": "29/11/2020",
        "anciennete_fp": "15ans 11ms 30jrs",
        "corps": "Attachés des Services Administratifs",
        "grade": "A3-8",
        "grade_paye": "A3-8",
        "cat_admin": "A",
        "contact": "97321288",
        "diplome": "Master 2 en Statistique Economique et Sociale obtenu en septembre 2020",
        "diplome_reconnu": "Maitrise en Sciences économiques",
        "service_interrompu": "07 ans 08 jours",
    },
    {
        "m": "73305",
        "nom": "MAMA-SIKA Rachid",
        "direction": "DGFD",
        "sexe": "M",
        "poste": "Directeur de la Mobilisation des Ressources Multilaterales",
        "statut_admin": "FE",
        "date_retraite": "01/04/2040",
        "annee_retraite": "2040",
        "date_naissance": "28/01/1980",
        "date_prise_service": "17/07/2009",
        "prise_service_structure": "17/07/2009",
        "anciennete_fp": "14ans 5ms 14jrs",
        "corps": "Administrateurs",
        "grade": "A1-8",
        "grade_paye": "A1-7",
        "cat_admin": "A",
        "contact": "97094746",
        "diplome": "Master/Gestion des Projet en 2008",
        "diplome_reconnu": "Master/Gestion des Projet",
        "service_interrompu": "03 ans 02 jours",
    },
    {
        "m": "56506",
        "nom": "METHO Pascal",
        "direction": "DGAR/DGFD",
        "sexe": "M",
        "poste": "Conducteurs de Véhicules Administratifs",
        "statut_admin": "ACDPE",
        "date_retraite": "01/01/2025",
        "annee_retraite": "2025",
        "date_naissance": "31/12/1969",
        "date_prise_service": "01/01/2008",
        "prise_service_structure": "03/03/2020",
        "anciennete_fp": "15ans 11ms 30jrs",
        "corps": "Conducteurs de Véhicules Administratifs",
        "grade": "D3-8",
        "grade_paye": "D3-8",
        "cat_admin": "D",
        "contact": "97018592",
        "diplome": "CEFEB en 1981+ Permis de Conduire",
        "diplome_reconnu": "CEFEB",
        "service_interrompu": "04 ans 13 jours",
    },
    {
        "m": "86883",
        "nom": "MONTCHO Hyacinthe",
        "direction": "DECAD/DGFD",
        "sexe": "M",
        "poste": "Directeur des Etudes et de la Coordination de l'Aide au Developpement",
        "statut_admin": "FE",
        "date_retraite": "01/07/2033",
        "annee_retraite": "2033",
        "date_naissance": "22/06/1973",
        "date_prise_service": "17/07/2009",
        "prise_service_structure": "17/07/2009",
        "anciennete_fp": "14ans 5ms 14jrs",
        "corps": "Administrateurs",
        "grade": "A1-8",
        "grade_paye": "A1-7",
        "cat_admin": "A",
        "contact": "66645134",
        "diplome": "DESS en gestion de la politique économique septembre 2004",
        "diplome_reconnu": "DESS en gestion de la politique économique",
        "service_interrompu": "01 an 10 jours",
    },
    {
        "m": "46312",
        "nom": "SALIFOU ALIDOU Raïnatou",
        "direction": "DMRM/DGFD",
        "sexe": "F",
        "poste": "Chef Division Secrétariat de la DMRM",
        "statut_admin": "FE",
        "date_retraite": "01/01/2033",
        "annee_retraite": "2033",
        "date_naissance": "18/11/1977",
        "date_prise_service": "28/03/2003",
        "prise_service_structure": "18/03/2014",
        "anciennete_fp": "20ans 9ms 3jrs",
        "corps": "Secrétaires Adjoints des Services Administratifs",
        "grade": "C1-7",
        "grade_paye": "C1-7",
        "cat_admin": "C",
        "contact": "97602486",
        "diplome": "Diplôme d'aptitude professionnelle (DAP) en 1999",
        "diplome_reconnu": "Attestation de formation de mise à niveau des APE admis au concours professionnels au titre de l'année 2011 (SAS",
        "service_interrompu": "04 ans 15 jours",
    },
    {
        "m": "39301",
        "nom": "TOHOU HONLONKOU Baï Elisée",
        "direction": "DGAR/DGFD",
        "sexe": "F",
        "poste": "Chef du Service des Ressources Humaines",
        "statut_admin": "FE",
        "date_retraite": "01/04/2035",
        "annee_retraite": "2035",
        "date_naissance": "08/03/1975",
        "date_prise_service": "01/03/1999",
        "prise_service_structure": "03/01/2022",
        "anciennete_fp": "24ans 09ms 30jrs",
        "corps": "Administrateurs",
        "grade": "A1-8",
        "grade_paye": "A1-7",
        "cat_admin": "A",
        "contact": "67145514",
        "diplome": "Master 2 en management des ressources humaines obtenu en 2017",
        "diplome_reconnu": "Master 2 en management des ressources humaines",
        "date_formation": "31/07/2017",
        "service_interrompu": "03 ans",
    },
    {
        "m": "45767",
        "nom": "TOKANNOU Edmond Claude",
        "direction": "DGAR/DGFD",
        "sexe": "M",
        "poste": "Conducteurs de Véhicules Administratifs",
        "statut_admin": "FE",
        "date_retraite": "01/01/2031",
        "annee_retraite": "2031",
        "date_naissance": "22/12/1975",
        "date_prise_service": "04/01/1999",
        "prise_service_structure": "28/08/2023",
        "corps": "Conducteurs de Véhicules Administratifs",
        "grade": "D3-11",
        "grade_paye": "D3-11",
        "cat_admin": "D",
        "contact": "90667740",
        "diplome": "Permis de conduire C1 en 2012",
        "diplome_reconnu": "Permis de conduire B obtenu en 1995",
        "service_interrompu": "02 ans",
    },
    {
        "m": "67112",
        "nom": "VODONOU Koïssé David",
        "direction": "DECAD/DGFD",
        "sexe": "M",
        "poste": "Chef Service de la Gestion de l'Information et de la Coordination de l'Aide au Développement",
        "statut_admin": "FE",
        "date_retraite": "01/10/2042",
        "annee_retraite": "2042",
        "date_naissance": "06/08/1982",
        "date_prise_service": "17/07/2009",
        "prise_service_structure": "17/07/2009",
        "anciennete_fp": "14ans 5ms 14jrs",
        "corps": "Ingénieurs et Analystes Concepteurs",
        "grade": "A1-5",
        "grade_paye": "A3-7",
        "cat_admin": "A",
        "contact": "97771957",
        "diplome": "Maîtrise en Informatique obtenu au Canada en 2020 (équivalent du Master)",
        "diplome_reconnu": "Diplôme de Technicien Supérieur en Informatique de Gestion",
        "date_formation": "05/10/2020",
        "service_interrompu": "04 ans 08 jours",
    },
    {
        "m": "56538",
        "nom": "WAMASSE Cokou Sagbo Jean-Patrick",
        "direction": "DGAR/DGFD",
        "sexe": "M",
        "poste": "Chef Division de la Documentation et des Archives",
        "statut_admin": "ACDPE",
        "date_retraite": "01/01/2026",
        "annee_retraite": "2026",
        "date_naissance": "14/10/1970",
        "date_prise_service": "01/01/2008",
        "prise_service_structure": "25/09/2017",
        "anciennete_fp": "15ans 11ms 30 jrs",
        "corps": "Préposés des Services Administratifs",
        "grade": "D3-8",
        "grade_paye": "D3-8",
        "cat_admin": "D",
        "contact": "97251585",
        "diplome": "CEFEB en 1984",
        "diplome_reconnu": "CEFEB",
        "service_interrompu": "06 ans 03 jours",
    },
    {
        "m": "56522",
        "nom": "ZINSOU Kouassi Germain",
        "direction": "DGFD",
        "sexe": "M",
        "poste": "Directeur Général Adjoint du Financement du Développement",
        "statut_admin": "ACDPE",
        "date_retraite": "01/07/2027",
        "annee_retraite": "2027",
        "date_naissance": "28/05/1967",
        "date_prise_service": "04/01/1999",
        "prise_service_structure": "04/01/1999",
        "anciennete_fp": "24ans 11ms 27jrs",
        "corps": "Administrateurs",
        "grade": "A1-8",
        "grade_paye": "A1-4",
        "cat_admin": "A",
        "contact": "97174227",
        "diplome": "Master en relation économique internationale en 1995",
        "diplome_reconnu": "Master en relation économique internationale",
        "service_interrompu": "05 ans 15 jours",
    },
    {
        "m": "45680",
        "nom": "OLYMPIO Hermine Afi Maximilienne",
        "direction": "DGFD",
        "sexe": "F",
        "poste": "Secrétaire Particulière/DGFD",
        "statut_admin": "FE",
        "date_retraite": "01/07/2029",
        "annee_retraite": "2029",
        "date_naissance": "30/04/1971",
        "date_prise_service": "04/01/1999",
        "prise_service_structure": "26/04/2024",
        "anciennete_fp": "24 ans",
        "corps": "Secrétaires des Services Administratifs",
        "grade": "B3-11",
        "grade_paye": "B3-11",
        "cat_admin": "B",
        "contact": "97777472",
        "diplome": "Licence en Administration et Gestion RH en 2021",
        "diplome_reconnu": "Licence en Administration et Gestion RH",
    },
    {
        "m": "98269",
        "nom": "KOBA Ayéman Lazare",
        "direction": "DMRM/DGFD",
        "sexe": "M",
        "poste": "Chef Service des Banques et Organisations Internationales",
        "statut_admin": "ACDPE",
        "date_retraite": "01/10/2037",
        "annee_retraite": "2037",
        "date_naissance": "09/01/1977",
        "date_prise_service": "24/07/2008",
        "prise_service_structure": "02/05/2024",
        "anciennete_fp": "15 ans",
        "corps": "Attachés des Services Financiers",
        "grade": "A3-9",
        "grade_paye": "A3-9",
        "cat_admin": "A",
        "contact": "96944041",
        "diplome": "Ingénieur en Planification et Gestion des Projets (Master 2) en 2017",
        "diplome_reconnu": "Maitrise en Science Economique",
    },
    {
        "m": "43003",
        "nom": "AFANOTIN Sèdami Benjamin",
        "direction": "CCI/DGFD",
        "sexe": "M",
        "poste": "Chef de Cellule contrôle interne",
        "statut_admin": "FE",
        "date_retraite": "01/04/2035",
        "annee_retraite": "2035",
        "date_naissance": "31/03/1975",
        "date_prise_service": "06/08/2001",
        "prise_service_structure": "08/07/2024",
        "anciennete_fp": "22 ans 10 mois",
        "corps": "Administrateurs du Trésor",
        "grade": "A1-10",
        "grade_paye": "A1-10",
        "cat_admin": "A",
        "contact": "97046509",
        "diplome": "Master en Marché public et partenariat public privé",
        "diplome_reconnu": "Master en Administration des Finances et du Trésor",
    },
    {
        "m": "11111",
        "nom": "DOSSOU YOVO Serge Oscar Gbènakpon",
        "direction": "DGFD",
        "sexe": "M",
        "poste": "Directeur Général du Financement du Développement",
        "statut_admin": "AGENT NOMME",
        "date_retraite": "01/10/2033",
        "annee_retraite": "2033",
        "date_naissance": "18/07/1973",
        "date_prise_service": "14/07/2023",
        "prise_service_structure": "14/07/2023",
        "anciennete_fp": "5 mois 15 jrs",
        "corps": "Administrateurs",
        "cat_admin": "A",
        "contact": "52530000",
        "diplome": "Master en Science de Gestion",
        "diplome_reconnu": "Master en Science de Gestion",
    },
    {
        "m": "86867",
        "nom": "SONOU Antoine",
        "direction": "DGFD",
        "sexe": "M",
        "poste": "CSMAF",
        "statut_admin": "FE",
        "date_prise_service": "01/10/2024",
    },
]


# ============================================================
# FONCTIONS UTILITAIRES
# ============================================================

def clean_value(value):
    """
    Nettoie les valeurs texte.
    '' devient None.
    """
    if value is None:
        return None

    if isinstance(value, str):
        value = value.strip()
        return value if value else None

    return value


def to_iso_date(value):
    """
    Convertit une date texte en format PostgreSQL YYYY-MM-DD.

    Exemples :
        '01/07/2032' -> '2032-07-01'
        '2032-07-01' -> '2032-07-01'
        '2016'       -> '2016-01-01'
    """
    value = clean_value(value)

    if value is None:
        return None

    value = str(value)

    formats = (
        "%d/%m/%Y",
        "%Y-%m-%d",
        "%d/%m/%y",
        "%m/%Y",
        "%Y",
    )

    for fmt in formats:
        try:
            return datetime.strptime(value, fmt).date().isoformat()
        except ValueError:
            continue

    print(f"⚠️ Date non convertie : {value}")
    return None


def normalize_agent(row):
    """
    Prépare les données avant insertion/mise à jour.
    """
    payload = {}

    for key, value in row.items():
        if key == "m":
            continue

        if CONVERT_DATES and key in DATE_FIELDS:
            payload[key] = to_iso_date(value)
        else:
            payload[key] = clean_value(value)

    # Si annee_retraite est absente mais date_retraite présente, on déduit l'année.
    if not payload.get("annee_retraite") and payload.get("date_retraite"):
        payload["annee_retraite"] = str(payload["date_retraite"])[:4]

    return payload


def execute_select(query):
    """
    Exécute une requête select Supabase et retourne toujours une liste.
    """
    result = query.execute()
    return getattr(result, "data", []) or []


def find_agent_by_matricule(sb, matricule):
    """
    Recherche un agent par matricule.
    """
    data = execute_select(
        sb.table(TABLE_AGENTS)
        .select("id, nom, matricule")
        .eq("matricule", matricule)
    )

    return data[0] if data else None


def find_agents_by_nom(sb, nom):
    """
    Recherche des agents par nom, sans distinguer majuscules/minuscules.
    """
    nom = clean_value(nom)

    if not nom:
        return []

    return execute_select(
        sb.table(TABLE_AGENTS)
        .select("id, nom, matricule")
        .ilike("nom", nom)
    )


def ensure_droits_conges(sb, agent_id, stats):
    """
    Crée le droit de congé pour l'année en cours si absent.
    """
    existing = execute_select(
        sb.table(TABLE_DROITS)
        .select("id")
        .eq("agent_id", agent_id)
        .eq("annee", ANNEE_CONGES)
    )

    if existing:
        return

    sb.table(TABLE_DROITS).insert(
        {
            "agent_id": agent_id,
            "annee": ANNEE_CONGES,
            "droit_annuel": DROIT_ANNUEL,
            "report": 0,
            "disponible": DROIT_ANNUEL,
            "consomme": 0,
            "solde": DROIT_ANNUEL,
        }
    ).execute()

    stats["droits"] += 1


# ============================================================
# FONCTION PRINCIPALE
# ============================================================

def main():
    sb = get_supabase()

    stats = {
        "maj": 0,
        "insert": 0,
        "skipped": 0,
        "droits": 0,
    }

    seen_matricules = set()

    print(f"🚀 Démarrage injection : {len(D)} agents")

    for index, raw in enumerate(D, start=1):
        row = dict(raw)
        matricule = str(row.pop("m", "")).strip()

        try:
            # --------------------------------------------------
            # Vérification du matricule
            # --------------------------------------------------
            if not matricule:
                print(f"❌ Ligne {index} : matricule manquant")
                stats["skipped"] += 1
                continue

            if matricule in seen_matricules:
                print(f"⚠️ Ligne {index} : matricule {matricule} déjà traité, ligne ignorée")
                stats["skipped"] += 1
                continue

            seen_matricules.add(matricule)

            # --------------------------------------------------
            # Normalisation des données
            # --------------------------------------------------
            payload = normalize_agent(row)
            payload["matricule"] = matricule

            if not payload.get("nom"):
                print(f"❌ Ligne {index} : nom manquant pour le matricule {matricule}")
                stats["skipped"] += 1
                continue

            # --------------------------------------------------
            # Recherche par matricule
            # --------------------------------------------------
            agent = find_agent_by_matricule(sb, matricule)

            if agent:
                sb.table(TABLE_AGENTS).update(payload).eq("id", agent["id"]).execute()

                stats["maj"] += 1
                agent_id = agent["id"]

                print(f"🔁 Mise à jour par matricule : {matricule} - {payload.get('nom')}")

                ensure_droits_conges(sb, agent_id, stats)
                continue

            # --------------------------------------------------
            # Recherche par nom si matricule introuvable
            # --------------------------------------------------
            agents_meme_nom = find_agents_by_nom(sb, payload.get("nom"))

            if len(agents_meme_nom) > 1:
                print(
                    f"⚠️ Ligne {index} : {len(agents_meme_nom)} agents homonymes "
                    f"pour {payload.get('nom')}. Injection évitée par sécurité."
                )
                stats["skipped"] += 1
                continue

            if len(agents_meme_nom) == 1:
                agent_id = agents_meme_nom[0]["id"]

                sb.table(TABLE_AGENTS).update(payload).eq("id", agent_id).execute()

                stats["maj"] += 1

                print(f"🔁 Mise à jour par nom : {matricule} - {payload.get('nom')}")

                ensure_droits_conges(sb, agent_id, stats)
                continue

            # --------------------------------------------------
            # Insertion si agent inexistant
            # --------------------------------------------------
            insert_payload = dict(payload)

            # Valeurs par défaut uniquement pour les nouveaux agents.
            insert_payload.setdefault("statut", "actif")
            insert_payload.setdefault("categorie", "fonctionnaire")

            response = sb.table(TABLE_AGENTS).insert(insert_payload).execute()
            inserted = response.data or []

            if not inserted:
                print(f"❌ Ligne {index} : insertion échouée pour {payload.get('nom')}")
                stats["skipped"] += 1
                continue

            agent_id = inserted[0]["id"]
            stats["insert"] += 1

            print(f"➕ Insertion : {matricule} - {payload.get('nom')}")

            ensure_droits_conges(sb, agent_id, stats)

        except Exception as error:
            print(f"❌ Erreur ligne {index} - matricule {matricule or '??'}")
            print(f"   {error}")
            stats["skipped"] += 1

    # ============================================================
    # RÉSUMÉ
    # ============================================================

    print("\n✅ Résumé de l'injection")
    print(f"- Mises à jour        : {stats['maj']}")
    print(f"- Nouveaux agents     : {stats['insert']}")
    print(f"- Ignorés / erreurs   : {stats['skipped']}")
    print(f"- Droits congés créés : {stats['droits']}")


if __name__ == "__main__":
    main()