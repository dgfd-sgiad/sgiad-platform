# -*- coding: utf-8 -*-
import re

# ========= FIX 1 : fix_dates.py (convertir dates avant UPDATE) =========
fd = open('fix_dates.py', encoding='utf-8').read()
fd = fd.replace('\r\n', '\n')

old = """def fr_to_iso(d):
    d = str(d or '').strip()
    if not d:
        return ''
    if re.match(r'^\\d{4}-\\d{2}-\\d{2}', d):
        return d[:10]
    m = re.match(r'^(\\d{1,2})/(\\d{1,2})/(\\d{4})', d)
    return f'{m.group(3)}-{int(m.group(2)):02d}-{int(m.group(1)):02d}' if m else ''"""

new = """def fr_to_iso(d):
    d = str(d or '').strip()
    if not d:
        return ''
    if re.match(r'^\\d{4}-\\d{2}-\\d{2}', d):
        return d[:10]
    m = re.match(r'^(\\d{1,2})[/-](\\d{1,2})[/-](\\d{4})', d)
    return f'{m.group(3)}-{int(m.group(2)):02d}-{int(m.group(1)):02d}' if m else ''"""

if old in fd:
    fd = fd.replace(old, new, 1)
    print('✅ fix_dates.py : fr_to_iso amélioré (/ et -)')
else:
    print('ℹ️ fr_to_iso déjà correct')

old2 = """    d = str(best.get('date_cloture') or best.get('Date cloture') or '').strip()
    if s0 >= 0.45 and d:
        sb.table('accords_consolides').update({'date_cloture': d}).eq('code_projet', a['code_projet']).execute()"""

new2 = """    d_raw = str(best.get('date_cloture') or best.get('Date cloture') or best.get('Date de clôture') or '').strip()
    d = fr_to_iso(d_raw)
    if s0 >= 0.45 and d:
        sb.table('accords_consolides').update({'date_cloture': d}).eq('code_projet', a['code_projet']).execute()"""

if old2 in fd:
    fd = fd.replace(old2, new2, 1)
    print('✅ fix_dates.py : conversion ISO appliquée avant UPDATE')
else:
    print('ℹ️ UPDATE déjà corrigé')

open('fix_dates.py', 'w', encoding='utf-8').write(fd)

# ========= FIX 2 : audit_data.py (section C avec score flou) =========
ad = open('audit_data.py', encoding='utf-8').read()
ad = ad.replace('\r\n', '\n')

old_c = """print()
print('=' * 70)
print("C. PROJETS CAGD (2025) ABSENTS DE LA BANQUE D'ACCORDS")
print('=' * 70)
obj_accords = [(norm(a.get('objet_accord')), sigle(a.get('objet_accord'))) for a in accords]
manquants = []
for c in cagd:
    if c['periode'] != '2025':
        continue
    n = norm(c['projet']); sg = sigle(c['projet'])
    found = False
    for on, osg in obj_accords:
        if sg and len(sg) >= 4 and sg in on:
            found = True; break
        if n and on and (n[:25] in on or on[:25] in n):
            found = True; break
    if not found:
        manquants.append((c['projet'], float(c['montant_total_fcfa'] or 0), c['partenaire']))
for nom, m, p in manquants:
    print(f'❌ {str(p)[:10]:10s} {m:>18,.0f}  {nom[:80]}')
print(f'\\n→ {len(manquants)} projet(s) CAGD 2025 non retrouvés dans les accords')"""

new_c = """print()
print('=' * 70)
print("C. PROJETS CAGD (2025) VRAIMENT ABSENTS DE LA BANQUE (score flou)")
print('=' * 70)
STOP = {'DE','DU','DES','LA','LE','LES','AU','AUX','EN','POUR','ET','SUR','DANS','PAR','AVEC','PROJET','BENIN','D','L','A'}
def tokens(s):
    return set(w for w in norm(s).split() if len(w) >= 3 and w not in STOP)
def sigle_par(s):
    m = re.search(r'\\(([A-Za-z0-9\\- ]{3,})\\)', str(s or ''))
    return norm(m.group(1)).strip() if m else ''
def nums(s):
    return set(re.findall(r'\\b\\d{3,4}\\b', str(s or '')))
def score(nom, accord):
    ta, tb = tokens(nom), tokens(accord.get('objet_accord') or '')
    if not ta or not tb: return 0.0
    base = len(ta & tb) / min(len(ta), len(tb))
    sg, og = sigle_par(nom), sigle_par(accord.get('objet_accord') or '')
    if sg and og and (sg in og or og in sg): base += 0.3
    if nums(nom) & nums(accord.get('objet_accord') or ''): base += 0.15
    return base
manquants = []
for c in cagd:
    if c['periode'] != '2025': continue
    best = max(accords, key=lambda a: score(c['projet'], a))
    s0 = score(c['projet'], best)
    if s0 < 0.45:
        manquants.append((c['projet'], float(c['montant_total_fcfa'] or 0), c['partenaire'], s0))
for nom, m, p, s in manquants:
    print(f'❌ {str(p)[:10]:10s} {m:>18,.0f}  score {s:.2f}  {nom[:65]}')
print(f'\\n→ {len(manquants)} projet(s) CAGD 2025 VRAIMENT absents (les autres existent sous un nom différent)')"""

if old_c in ad:
    ad = ad.replace(old_c, new_c, 1)
    print('✅ audit_data.py : section C remplacée par score flou')
else:
    print('❌ audit_data.py section C introuvable — vérifier manuellement')

open('audit_data.py', 'w', encoding='utf-8').write(ad)
print('\nLes deux scripts sont corrigés.')