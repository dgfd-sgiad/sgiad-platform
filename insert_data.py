from db import get_supabase

sb = get_supabase()

# Vider les tables
sb.table("revues").delete().neq("id", 0).execute()
sb.table("recommandations").delete().neq("id", 0).execute()

# Insérer les revues
revues = [
  {"date_revue": "2026-09-05", "partenaire": "Banque Ouest Africaine de Développement", "type_revue": "Revue semestrielle", "lieu": "Cotonou", "statut": "Planifiée"},
  {"date_revue": "2026-09-15", "partenaire": "Banque mondiale", "type_revue": "Revue semestrielle", "lieu": "Cotonou", "statut": "Confirmée"},
  {"date_revue": "2026-09-22", "partenaire": "Agence Française de Développement", "type_revue": "Revue annuelle", "lieu": "Paris", "statut": "En préparation"},
  {"date_revue": "2026-09-29", "partenaire": "Union Européenne", "type_revue": "Revue annuelle", "lieu": "Cotonou", "statut": "En préparation"},
  {"date_revue": "2026-10-10", "partenaire": "Banque Africaine de Développement", "type_revue": "Revue semestrielle", "lieu": "Abidjan", "statut": "Planifiée"}
]
res1 = sb.table("revues").insert(revues).execute()
print(f"✅ {len(res1.data)} revues insérées")

# Insérer les recommandations
recos = [
  {"texte": "Accélérer les procédures de passation des marchés", "revue_origine": "Revue BM Nov. 2025", "partenaire": "Banque mondiale", "statut": "En cours", "echeance": "2026-09-30"},
  {"texte": "Renforcer le suivi environnemental et social des projets financés", "revue_origine": "Revue AFD Déc. 2025", "partenaire": "Agence Française de Développement", "statut": "En cours", "echeance": "2026-07-15"},
  {"texte": "Finaliser les études techniques des projets d'eau et assainissement", "revue_origine": "Revue BAD Oct. 2025", "partenaire": "Banque Africaine de Développement", "statut": "A démarrer", "echeance": "2026-08-31"},
  {"texte": "Mettre à jour la base des bénéficiaires des projets agricoles", "revue_origine": "Revue BOAD Déc. 2025", "partenaire": "Banque Ouest Africaine de Développement", "statut": "A démarrer", "echeance": "2026-08-15"},
  {"texte": "Améliorer la coordination entre les ministères pour la mise en œuvre", "revue_origine": "Revue UE Nov. 2025", "partenaire": "Union Européenne", "statut": "En cours", "echeance": "2026-10-15"}
]
res2 = sb.table("recommandations").insert(recos).execute()
print(f"✅ {len(res2.data)} recommandations insérées")