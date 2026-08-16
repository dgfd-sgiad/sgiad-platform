# -*- coding: utf-8 -*-
import re, openpyxl
from datetime import datetime
from db import get_supabase

sb = get_supabase()
PART = 'Agence Française de Développement'

def to_int(v):
    if v is None: return None
    if isinstance(v, (int, float)): return int(v)
    s = str(v).replace(',', '').replace(' ', '').strip()
    if s in ('', '-'): return None
    m = re.match(r'^([\d.]+)', s)
    try:
        return int(float(m.group(1))) if m else None
    except Exception:
        return None

def parse_date(v):
    if v is None: return None
    if isinstance(v, datetime): return v.date().isoformat()
    s = str(v).strip()
    m = re.match(r'(\d{1,2})/(\d{1,2})/(\d{2})$', s)
    if m: return f'20{m.group(3)}-{int(m.group(1)):02d}-{int(m.group(2)):02d}'
    return None

wb = openpyxl.load_workbook('Point global prévisions de décaissements AFD.xlsx', data_only=True)
ws = wb.worksheets[0]
rows = list(ws.iter_rows(values_only=True))

sb.table('previsions_decaissements').delete().eq('partenaire', PART).execute()

n = 0
for r in rows:
    if not r or r[0] is None: continue
    proj = str(r[0]).strip()
    low = proj.lower()
    if low in ('projets',) or 'taux' in low or 'prévision de' in low or 'montant' in low or 'opérations potentielles' in low or 'ordre' in low or 'point des' in low or 'total' in low:
        continue
    operation = str(r[2] or '').strip()
    if not operation or not re.search(r'[a-zA-Z]', operation): continue
    date_raw = str(r[4] or '').strip()
    sb.table('previsions_decaissements').insert({
        'partenaire': PART,
        'projet': proj,
        'montant_fcfa': to_int(r[1]),
        'operation': operation,
        'taux_cible': str(r[3] or '').strip(),
        'date_previsionnelle': parse_date(r[4]),
        'delai_texte': '' if parse_date(r[4]) else date_raw,
        'montant_cumule_fcfa': to_int(r[5]),
        'observations': str(r[6] or '').strip(),
        'non_decaissable_2026': 'ne pourra plus' in date_raw.lower(),
    }).execute()
    n += 1

print(f'📊 {n} opérations de décaissement importées.')
