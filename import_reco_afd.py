# -*- coding: utf-8 -*-
import re, openpyxl
from datetime import datetime
from db import get_supabase

sb = get_supabase()
PART = 'Agence Française de Développement'

# 1. Revue AFD du 31/07/2026 (exécutée)
rev = sb.table('revues').select('id').eq('partenaire', PART).eq('date_revue', '2026-07-31').execute()
if rev.data:
    revue_id = rev.data[0]['id']
    print(f'ℹ️ Revue déjà présente (id={revue_id})')
else:
    r = sb.table('revues').insert({'date_revue': '2026-07-31', 'date_reelle': '2026-07-31', 'executee': True, 'partenaire': PART, 'type_revue': 'Revue technique', 'lieu': 'Cotonou', 'statut': 'Confirmée', 'statut_validation': 'valide'}).execute()
    revue_id = r.data[0]['id']
    print(f'✅ Revue créée (id={revue_id})')

# Idempotence : on repart propre
sb.table('recommandations').delete().eq('revue_id', revue_id).execute()

MOIS = {'jan':1,'fev':2,'mar':3,'avr':4,'mai':5,'juin':6,'juil':7,'aout':8,'sept':9,'oct':10,'nov':11,'dec':12,'aug':8}
def parse_delai(v):
    if v is None: return None
    if isinstance(v, datetime): return v.date().isoformat()
    s = str(v).strip()
    m = re.match(r'(\d{1,2})/(\d{1,2})/(\d{2})$', s)
    if m: return f'20{m.group(3)}-{int(m.group(1)):02d}-{int(m.group(2)):02d}'
    low = s.lower()
    for k, mo in MOIS.items():
        if low.startswith(k): return f'2026-{mo:02d}-01'
    return None

wb = openpyxl.load_workbook('Suivi recomm AFD à imprimer DG.xlsx', data_only=True)
ws = wb.worksheets[0]
rows = list(ws.iter_rows(values_only=True))
start = None
for i, r in enumerate(rows):
    if r and str(r[0]).strip() == 'N°':
        start = i + 1
        break
if start is None:
    print('❌ En-tête introuvable'); raise SystemExit

proj, diff, n = '', '', 0
for r in rows[start:]:
    if (r[0] is None or str(r[0]).strip() == '') and (r[3] is None or str(r[3]).strip() == ''):
        break
    if r[1]: proj = str(r[1]).strip()
    if r[2]: diff = str(r[2]).strip()
    action = str(r[3] or '').strip()
    if not action: continue
    n += 1
    sb.table('recommandations').insert({
        'revue_id': revue_id, 'partenaire': PART, 'projet': proj,
        'difficulte': diff, 'texte': action,
        'responsable_direct': str(r[4] or '').strip(), 'associe': str(r[5] or '').strip(),
        'echeance': parse_delai(r[6]),
        'executee': str(r[7] or '').strip().lower() == 'exécuté',
        'commentaires': str(r[8] or '').strip(),
        'statut_validation': 'valide',
    }).execute()

print(f'📊 {n} recommandations importées et liées à la revue du 31/07/2026.')
