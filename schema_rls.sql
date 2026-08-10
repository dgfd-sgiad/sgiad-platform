-- ============================================================
-- SGIAD - Row Level Security (RLS)
-- ============================================================
-- A executer APRES schema.sql dans l'editeur SQL Supabase.
--
-- IMPORTANT :
--   - Le backend Flask doit utiliser la cle service_role (Settings > API)
--     dans SUPABASE_KEY : elle contourne le RLS cote serveur.
--   - Le RLS protege l'acces direct via la cle anon (PostgREST / client web).
-- ============================================================

-- Tables sensibles : acces reserve aux utilisateurs authentifies Supabase Auth
ALTER TABLE accords_consolides ENABLE ROW LEVEL SECURITY;
ALTER TABLE projets ENABLE ROW LEVEL SECURITY;
ALTER TABLE suivi_trimestriel ENABLE ROW LEVEL SECURITY;
ALTER TABLE parametres ENABLE ROW LEVEL SECURITY;
ALTER TABLE localisation ENABLE ROW LEVEL SECURITY;
ALTER TABLE colonnes_meta ENABLE ROW LEVEL SECURITY;
ALTER TABLE secteur_sous_secteur ENABLE ROW LEVEL SECURITY;
ALTER TABLE documents_projets ENABLE ROW LEVEL SECURITY;
ALTER TABLE veille_alertes ENABLE ROW LEVEL SECURITY;
ALTER TABLE session_log ENABLE ROW LEVEL SECURITY;
ALTER TABLE taux_change_historique ENABLE ROW LEVEL SECURITY;

-- Politiques lecture (SELECT) pour utilisateurs authentifies
DO $$
DECLARE
    t TEXT;
BEGIN
    FOREACH t IN ARRAY ARRAY[
        'accords_consolides', 'projets', 'suivi_trimestriel', 'parametres',
        'localisation', 'colonnes_meta', 'secteur_sous_secteur',
        'documents_projets', 'veille_alertes', 'session_log', 'taux_change_historique'
    ]
    LOOP
        EXECUTE format('DROP POLICY IF EXISTS "auth_select_%s" ON %I', t, t);
        EXECUTE format(
            'CREATE POLICY "auth_select_%s" ON %I FOR SELECT TO authenticated USING (true)',
            t, t
        );
        EXECUTE format('DROP POLICY IF EXISTS "auth_write_%s" ON %I', t, t);
        EXECUTE format(
            'CREATE POLICY "auth_write_%s" ON %I FOR ALL TO authenticated USING (true) WITH CHECK (true)',
            t, t
        );
    END LOOP;
END $$;

-- Refuser l'acces anon explicite (defense si cle publique exposee)
DO $$
DECLARE
    t TEXT;
BEGIN
    FOREACH t IN ARRAY ARRAY[
        'accords_consolides', 'projets', 'suivi_trimestriel', 'parametres',
        'localisation', 'colonnes_meta', 'secteur_sous_secteur',
        'documents_projets', 'veille_alertes', 'session_log', 'taux_change_historique'
    ]
    LOOP
        EXECUTE format('REVOKE ALL ON %I FROM anon', t);
    END LOOP;
END $$;
