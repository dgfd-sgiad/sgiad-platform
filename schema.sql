-- ============================================================
-- SGIAD - Schema PostgreSQL pour Supabase
-- Migration depuis Excel (Banque_Projets.xlsx)
-- ============================================================

-- Activer l'extension pour les UUID
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ============================================================
-- NETTOYAGE: Supprimer les tables existantes (si re-execution)
-- ============================================================
DROP TRIGGER IF EXISTS trg_accords_updated_at ON accords_consolides;
DROP TRIGGER IF EXISTS trg_projets_updated_at ON projets;
DROP TABLE IF EXISTS suivi_trimestriel CASCADE;
DROP TABLE IF EXISTS colonnes_meta CASCADE;
DROP TABLE IF EXISTS taux_change_historique CASCADE;
DROP TABLE IF EXISTS secteur_sous_secteur CASCADE;
DROP TABLE IF EXISTS session_log CASCADE;
DROP TABLE IF EXISTS accords_consolides CASCADE;
DROP TABLE IF EXISTS projets CASCADE;
DROP TABLE IF EXISTS localisation CASCADE;
DROP TABLE IF EXISTS parametres CASCADE;
DROP FUNCTION IF EXISTS update_updated_at() CASCADE;

-- ============================================================
-- TABLE: accords_consolides (principale, 866 lignes, 36 colonnes)
-- Feuille Excel: Accords_consolides (header ligne 6, data ligne 7+)
-- ============================================================
CREATE TABLE accords_consolides (
    id              SERIAL PRIMARY KEY,
    code_projet     TEXT UNIQUE NOT NULL,

    -- Identification
    annee_signature         INTEGER,
    annee_cloture           INTEGER,
    modalite_intervention   TEXT,
    objet_accord            TEXT,
    objectif_general        TEXT,
    source_verifiable       TEXT,
    partenaire              TEXT,
    sigle_part              TEXT,
    secteur_principal       TEXT,

    -- Financement
    nature_pret_don_mixte   TEXT,
    montant_pret_fcfa       NUMERIC,
    montant_don_fcfa        NUMERIC,
    montant_total_fcfa      NUMERIC,
    devise                  TEXT,
    montant_total_devise    NUMERIC,
    instrument_financement  TEXT,

    -- Dates
    date_signature          DATE,
    date_approbation        DATE,
    date_cloture            DATE,

    -- Localisation
    zone                    TEXT,

    -- Classification
    apd_oui_non             TEXT,
    type_financement        TEXT,
    type_contributeur       TEXT,
    sous_secteur            TEXT,
    axe_pag                 TEXT,
    pilier_pag              TEXT,
    odd                     TEXT,
    cible_odd               TEXT,
    pilier                  TEXT,
    statut                  TEXT,

    -- Details
    objectifs_specifiques   TEXT,
    resultats_attendues     TEXT,
    principales_composantes TEXT,
    beneficiaires_directes  TEXT,
    population_cible        TEXT,

    -- Metadata
    created_at  TIMESTAMPTZ DEFAULT NOW(),
    updated_at  TIMESTAMPTZ DEFAULT NOW()
);

-- Index pour les recherches frequentes
CREATE INDEX idx_accords_secteur ON accords_consolides(secteur_principal);
CREATE INDEX idx_accords_partenaire ON accords_consolides(partenaire);
CREATE INDEX idx_accords_statut ON accords_consolides(statut);
CREATE INDEX idx_accords_annee ON accords_consolides(annee_signature);
CREATE INDEX idx_accords_sigle ON accords_consolides(sigle_part);

-- ============================================================
-- TABLE: colonnes_meta (metadata dynamique des colonnes)
-- Remplace get_columns_meta() qui lisait les en-tetes Excel
-- ============================================================
CREATE TABLE colonnes_meta (
    id          SERIAL PRIMARY KEY,
    table_name  TEXT NOT NULL,
    column_key  TEXT NOT NULL,       -- nom affiche (ex: "Code Projet")
    db_column   TEXT NOT NULL,       -- nom SQL (ex: "code_projet")
    col_type    TEXT DEFAULT 'text', -- 'text' | 'number' | 'date' | 'select'
    readonly    BOOLEAN DEFAULT FALSE,
    col_order   INTEGER NOT NULL,    -- ordre d'affichage
    options     JSONB DEFAULT '[]',  -- valeurs distinctes pour 'select'

    UNIQUE(table_name, column_key)
);

-- ============================================================
-- TABLE: localisation (5290 lignes)
-- Arbre: Departement > Commune > Arrondissement > Village
-- ============================================================
CREATE TABLE localisation (
    id              SERIAL PRIMARY KEY,
    departement     TEXT NOT NULL,
    commune         TEXT NOT NULL,
    arrondissement  TEXT NOT NULL,
    village         TEXT NOT NULL
);

CREATE INDEX idx_loc_dept ON localisation(departement);
CREATE INDEX idx_loc_commune ON localisation(departement, commune);

-- ============================================================
-- TABLE: parametres (valeurs de configuration, listes deroulantes)
-- Feuille Excel: Parametres (19 categories)
-- ============================================================
CREATE TABLE parametres (
    id          SERIAL PRIMARY KEY,
    categorie   TEXT NOT NULL,   -- SECTEUR, SOUS_SECTEUR, PARTENAIRE, etc.
    valeur      TEXT NOT NULL,
    ordre       INTEGER DEFAULT 0,

    UNIQUE(categorie, valeur)
);

-- ============================================================
-- TABLE: suivi_trimestriel (100 lignes)
-- Suivi financier et physique par trimestre
-- ============================================================
CREATE TABLE suivi_trimestriel (
    id                      SERIAL PRIMARY KEY,
    code_projet             TEXT NOT NULL REFERENCES accords_consolides(code_projet),
    annee_suivi             INTEGER,
    trimestre               TEXT,
    tef_trim                NUMERIC,
    montant_decaisse_usd    NUMERIC,
    montant_decaisse_fcfa   NUMERIC,
    tep_trim                NUMERIC,
    activites_realisees     TEXT,
    tef_cumule              NUMERIC,
    tep_cumule              NUMERIC,
    difficultes_rencontrees TEXT,
    approches_solution      TEXT,
    recommandations         TEXT,
    date_saisie             DATE,

    created_at  TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_suivi_code ON suivi_trimestriel(code_projet);

-- ============================================================
-- TABLE: projets (866 lignes, 115 colonnes)
-- Feuille Excel: Projets (header ligne 2)
-- ============================================================
CREATE TABLE projets (
    id                      SERIAL PRIMARY KEY,
    code_projet             TEXT UNIQUE NOT NULL,
    intitule_projet         TEXT,
    annee_collecte          INTEGER,
    categorie               TEXT,
    envergure               TEXT,
    secteur_activite_1      TEXT,
    secteur_activite_2      TEXT,
    secteur_activite_3      TEXT,
    sous_secteur            TEXT,
    tutelle                 TEXT,
    agence_execution        TEXT,
    contexte_justification  TEXT,
    problematique           TEXT,
    objectif_global         TEXT,
    objectifs_specifiques   TEXT,
    principaux_resultats    TEXT,
    composantes_projet      TEXT,
    activites_principales   TEXT,
    beneficiaires_directs   TEXT,
    beneficiaires_indirects TEXT,
    departement             TEXT,
    commune                 TEXT,
    arrondissement          TEXT,
    village_quartier        TEXT,
    coordonnees_gps         TEXT,
    date_approbation        DATE,
    date_signature          DATE,
    date_vigueur            DATE,
    date_demarrage          DATE,
    date_cloture            DATE,
    duree_initiale_mois     INTEGER,
    est_proroge             TEXT,
    date_prorogation        DATE,
    motif_prorogation       TEXT,
    nouvelle_date_cloture   DATE,
    nb_prorogations         INTEGER,
    cout_total_usd          NUMERIC,
    devise                  TEXT,
    taux_change             NUMERIC,
    cout_total_fcfa         NUMERIC,
    milliards_fcfa          NUMERIC,
    contrepartie_bn_usd     NUMERIC,
    contrepartie_bn_fcfa    NUMERIC,
    don_attendu_fcfa        NUMERIC,
    pret_attendu_fcfa       NUMERIC,
    ppp_attendu_fcfa        NUMERIC,
    contribution_benef_fcfa NUMERIC,
    gap_financement         NUMERIC,
    pourcentage_acquis      NUMERIC,
    source_financement      TEXT,
    apd_oui_non             TEXT,
    type_financement        TEXT,
    contributeur            TEXT,
    sigle_partenaire        TEXT,
    type_contributeur       TEXT,
    co_partenaire_1         TEXT,
    co_partenaire_2         TEXT,
    co_partenaire_3         TEXT,
    co_partenaire_4         TEXT,
    co_partenaire_5         TEXT,
    co_partenaire_6         TEXT,
    co_partenaire_7         TEXT,
    statut_projet           TEXT,
    secteur_pag             TEXT,
    pilier_pag              TEXT,
    axe_pag                 TEXT,
    odd                     TEXT,
    cible_odd               TEXT,
    pilier_national         TEXT,
    resp_banque_nom         TEXT,
    resp_banque_tel1        TEXT,
    resp_banque_tel2        TEXT,
    resp_banque_email       TEXT,
    coord_projet_nom        TEXT,
    coord_projet_tel1       TEXT,
    coord_projet_tel2       TEXT,
    coord_projet_email      TEXT,
    raf_nom                 TEXT,
    raf_tel1                TEXT,
    raf_tel2                TEXT,
    raf_email               TEXT,
    resp_se_nom             TEXT,
    resp_se_tel1            TEXT,
    resp_se_tel2            TEXT,
    resp_se_email           TEXT,
    niveau_maturite         INTEGER,
    etude_faisabilite       TEXT,
    etude_environnementale  TEXT,
    plan_affaires           TEXT,
    dossier_technique       TEXT,
    categorie_env           TEXT,
    theme_genre             TEXT,
    theme_inclusion         TEXT,
    theme_climat            TEXT,
    theme_emploi_jeunes     TEXT,
    risques_identifies      TEXT,
    mesures_attenuation     TEXT,
    niveau_risque           TEXT,
    date_soumission         DATE,
    avis_technique          TEXT,
    avis_dgfd               TEXT,
    avis_ministere          TEXT,
    decision_comite         TEXT,
    date_validation         DATE,
    note_conceptuelle       TEXT,
    cadre_logique           TEXT,
    budget_detaille         TEXT,
    cartographie            TEXT,
    lettre_demande          TEXT,
    zone_intervention       TEXT,
    modalite_intervention   TEXT,
    nature_financement      TEXT,
    instrument_financement  TEXT,
    source_verifiable       TEXT,
    montant_devise_origine  NUMERIC,

    created_at  TIMESTAMPTZ DEFAULT NOW(),
    updated_at  TIMESTAMPTZ DEFAULT NOW()
);

-- ============================================================
-- TABLE: secteur_sous_secteur (relation secteurs -> sous-secteurs)
-- Permet de lier des sous-secteurs à un secteur principal
-- ============================================================
CREATE TABLE secteur_sous_secteur (
    id              SERIAL PRIMARY KEY,
    secteur         TEXT NOT NULL,
    sous_secteur    TEXT NOT NULL,
    created_at      TIMESTAMPTZ DEFAULT NOW(),

    UNIQUE(secteur, sous_secteur)
);

CREATE INDEX idx_secteur_sous ON secteur_sous_secteur(secteur);

-- ============================================================
-- TABLE: session_log (historique de connexions)
-- ============================================================
CREATE TABLE session_log (
    id                  SERIAL PRIMARY KEY,
    ip_address          TEXT,
    user_email          TEXT,
    derniere_connexion  TIMESTAMPTZ,
    total_connexions    INTEGER DEFAULT 0,
    created_at          TIMESTAMPTZ DEFAULT NOW()
);

-- ============================================================
-- TABLE: taux_change_historique
-- ============================================================
CREATE TABLE taux_change_historique (
    id          SERIAL PRIMARY KEY,
    devise      TEXT NOT NULL,
    date_taux   DATE NOT NULL,
    taux        NUMERIC NOT NULL,
    created_at  TIMESTAMPTZ DEFAULT NOW(),

    UNIQUE(devise, date_taux)
);

-- ============================================================
-- FONCTION: auto-update updated_at
-- ============================================================
CREATE OR REPLACE FUNCTION update_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_accords_updated_at
    BEFORE UPDATE ON accords_consolides
    FOR EACH ROW EXECUTE FUNCTION update_updated_at();

CREATE TRIGGER trg_projets_updated_at
    BEFORE UPDATE ON projets
    FOR EACH ROW EXECUTE FUNCTION update_updated_at();

-- ============================================================
-- ROW LEVEL SECURITY (RLS) - a activer apres config Auth
-- ============================================================
-- ALTER TABLE accords_consolides ENABLE ROW LEVEL SECURITY;
-- ALTER TABLE projets ENABLE ROW LEVEL SECURITY;
-- ALTER TABLE suivi_trimestriel ENABLE ROW LEVEL SECURITY;
--
-- CREATE POLICY "Lecture pour utilisateurs authentifies"
--     ON accords_consolides FOR SELECT
--     USING (auth.role() = 'authenticated');
--
-- CREATE POLICY "Ecriture pour utilisateurs authentifies"
--     ON accords_consolides FOR ALL
--     USING (auth.role() = 'authenticated');
