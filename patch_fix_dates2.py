# -*- coding: utf-8 -*-
p = 'fix_dates.py'
s = open(p, encoding='utf-8').read()
if 'def fr_to_iso' not in s:
    s = s.replace("from db import get_supabase", '''from db import get_supabase

def fr_to_iso(d):
    d = str(d or '').strip()
    if not d:
        return ''
    if re.match(r'^\\d{4}-\\d{2}-\\d{2}', d):
        return d[:10]
    m = re.match(r'^(\\d{1,2})[/-](\\d{1,2})[/-](\\d{4})', d)
    return f'{m.group(3)}-{int(m.group(2)):02d}-{int(m.group(1)):02d}' if m else ''
''', 1)
    open(p, 'w', encoding='utf-8').write(s)
    print('✅ fr_to_iso ajoutée à fix_dates.py')
else:
    print('ℹ️ fr_to_iso déjà présente')
    