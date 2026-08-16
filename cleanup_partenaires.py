from db import get_supabase
from collections import Counter
sb = get_supabase()

# 1) Renommer BAD -> Banque Africaine de Développement (recommandations + revue)
bad = sb.table('recommandations').select('id').eq('partenaire', 'BAD').execute().data or []
for r in bad:
    sb.table('recommandations').update({'partenaire': 'Banque Africaine de Développement'}).eq('id', r['id']).execute()
sb.table('revues').update({'partenaire': 'Banque Africaine de Développement'}).eq('partenaire', 'BAD').execute()
print(f"Renommees BAD -> Banque Africaine de Developpement : {len(bad)}")

# 2) Supprimer les donnees provisoires
for p in ['Banque mondiale', 'Banque Ouest Africaine de Développement', 'Union Européenne']:
    d = sb.table('recommandations').select('id').eq('partenaire', p).execute().data or []
    for r in d:
        sb.table('recommandations').delete().eq('id', r['id']).execute()
    print(f"Supprimees [{p}] : {len(d)}")

total = sb.table('recommandations').select('id', count='exact').execute().count
c = sb.table('recommandations').select('partenaire').execute().data
print("Total final:", total)
print(Counter([x['partenaire'] for x in c]))
