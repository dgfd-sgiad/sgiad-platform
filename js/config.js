const modules = [
    {
        id: 'requetes_financement',
        title: 'Requêtes de Financement',
        icon: '💰',
        file: 'modules/requetes.html',
        actif: false
    },
    {
        id: 'suivi_financier_projets',
        title: 'Gestion des Accords Financiers',
        icon: '🏗️',
        // Interface principale (Supabase) — modules/banque_projets.html
        file: 'modules/banque_projets.html',
        actif: true
    },
    {
        id: 'coop_decentralisee',
        title: 'Coopération Décentralisée',
        icon: '🤝',
        file: 'modules/coop_dec.html',
        actif: false
    },
    {
        id: 'suivi_des_projets',
        title: 'Suivi des Projets & Revues',
        icon: '📊',
        file: '/suivi',
        actif: true
    },
    {
        id: 'investissements_etrangers',
        title: 'Investissements Étrangers',
        icon: '🌍',
        file: 'modules/ide.html',
        actif: false
    },
    {
        id: 'partenariat_public_prive',
        title: 'Partenariat Public-Privé',
        icon: '🏢',
        file: 'modules/ppp.html',
        actif: false
    },
    {
        id: 'fonds_specifiques',
        title: 'Fonds Spécifiques',
        icon: '💵',
        file: 'modules/fonds.html',
        actif: false
    },
    {
        id: 'cadres_cooperation',
        title: 'Cadres de Coopération',
        icon: '📑',
        file: 'modules/cadres.html',
        actif: false
    },
    {
        id: 'parametrage_systeme',
        title: 'Paramétrage Système',
        icon: '⚙️',
        file: 'modules/parametres.html',
        actif: false
    },
    {
        id: 'gestion_utilisateurs',
        title: 'Gestion des Utilisateurs',
        icon: '👥',
        file: '/admin/plateforme',
        actif: true
    },
    {
        id: 'generation_rapports',
        title: 'Génération de Rapports',
        icon: '📊',
        file: 'modules/rapports.html',
        actif: false
    },
    {
        id: 'veille_accords',
        title: 'Veille des Accords Signés',
        icon: '📡',
        img: 'veille_accords.png',
        file: 'modules/veille.html',
        actif: true
    }
];
const SECTEURS_SOUS_SECTEURS = {
  "ÉNERGIE": ["Production d'électricité","Électrification rurale","Énergies renouvelables"],
  "AGRICULTURE": ["Production végétale","Irrigation","Élevage","Pêche et aquaculture"],
  "CADRE DE VIE": ["Urbanisme","Assainissement pluvial","Gestion des déchets","Environnement et changements climatiques"],
  "CULTURE ET TOURISME": ["Patrimoine culturel","Arts et spectacles","Écotourisme","Hôtellerie et hébergement"],
  "DÉCENTRALISATION": ["Appui aux communes","Planification locale","Développement territorial"],
  "DÉVELOPPEMENT SOCIAL": ["Développement communautaire","Inclusion sociale","Promotion de la femme"],
  "DIVERS SECTEURS": ["Programmes multisectoriels","Développement intégré","Coordination intersectorielle"],
  "EAU ET ASSAINISSEMENT": ["Approvisionnement en eau potable","Hydraulique villageoise","Assainissement des eaux usées"],
  "ÉCONOMIE": ["Planification économique","Promotion des investissements","Entrepreneuriat"],
  "ÉDUCATION": ["Enseignement primaire","Enseignement secondaire","Formation professionnelle","Enseignement supérieur"],
  "FINANCES PUBLIQUES": ["Gestion budgétaire","Administration fiscale","Dette publique","Investissements publics"],
  "GOUVERNANCE": ["Réforme administrative","Transparence et redevabilité","État civil","Suivi-évaluation"],
  "INDUSTRIE ET COMMERCE": ["Développement industriel","Artisanat","Commerce intérieur","Commerce extérieur"],
  "INFRASTRUCTURES ROUTIERES ET TRANSPORT": ["Routes nationales","Pistes rurales","Transport urbain","Sécurité routière"],
  "JUSTICE": ["Réforme judiciaire","Accès à la justice","Administration pénitentiaire"],
  "MICROFINANCE": ["Inclusion financière","Épargne et crédit","Finance agricole"],
  "NUMÉRIQUE": ["Fibre optique","Gouvernement électronique","Cybersécurité","Transformation numérique"],
  "PROTECTION SOCIALE ET EMPLOI": ["Filets sociaux","Emploi des jeunes","Formation à l'emploi","Réinsertion socio-économique"],
  "SANTÉ": ["Santé maternelle et infantile","Vaccination","Infrastructures sanitaires","Santé communautaire"],
  "SÉCURITÉ ET DÉFENSE": ["Sécurité intérieure","Protection civile","Sécurité frontalière","Défense nationale"],
  "SPORTS ET LOISIRS": ["Infrastructures sportives","Sports scolaires","Centres de loisirs","Promotion de la jeunesse"]
};
