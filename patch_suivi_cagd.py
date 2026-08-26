# -*- coding: utf-8 -*-
p = 'suivi.py'
s = open(p, encoding='utf-8').read()
s = s.replace('\r\n', '\n')
ok = []

# A) Index CAGD après le chargement des accords
old = "        rows = resp.data or []\n\n        today = date.today()"
new = """        rows = resp.data or []

        # --- Index CAGD : execution financiere reelle (decaissements cumules) ---
        import re as _re
        def _norm2(s):
            s = _strip_accents(str(s or '').upper())
            return _re.sub(r'[^A-Z0-9 ]', ' ', s)
        def _acro(s):
            m = _re.search(r'\\(([A-Za-z0-9\\- ]{3,})\\)', str(s or ''))
            return _norm2(m.group(1)).strip() if m else ''
        cum_cagd = {}
        try:
            cagd_rows = sb.table('decaissements_cagd').select('projet, periode, montant_total_fcfa').execute().data or []
        except Exception:
            cagd_rows = []
        for c in cagd_rows:
            n = _norm2(c.get('projet'))
            per = _to_int(c.get('periode'))
            val = _to_float(c.get('montant_total_fcfa'))
            cur = cum_cagd.get(n)
            if cur is None or per > cur[0]:
                cum_cagd[n] = (per, val)
        by_acro, by_pref = {}, {}
        for c in cagd_rows:
            n = _norm2(c.get('projet'))
            val = cum_cagd.get(n, (0, 0.0))[1]
            a = _acro(c.get('projet'))
            if a and len(a) >= 4 and a not in by_acro:
                by_acro[a] = val
            p25 = n.strip()[:25]
            if p25 and p25 not in by_pref:
                by_pref[p25] = val
        def _cum_cagd(objet):
            a = _acro(objet)
            if a and a in by_acro:
                return by_acro[a]
            p25 = _norm2(objet).strip()[:25]
            return by_pref.get(p25, 0.0)
        taux_cagd_by_code = {}

        today = date.today()"""
if old in s:
    s = s.replace(old, new, 1); ok.append('A index CAGD')

# B) taux par projet dans la boucle
old = "            code = r.get('code_projet') or ''\n            montant = _to_float(r.get('montant_total_fcfa'))"
new = old + """
            cum = _cum_cagd(r.get('objet_accord') or '')
            taux_fin_cagd = round(min(100.0, cum / montant * 100), 1) if montant > 0 and cum else None
            if taux_fin_cagd is not None:
                taux_cagd_by_code[code] = taux_fin_cagd"""
if old in s:
    s = s.replace(old, new, 1); ok.append('B taux par projet')

# C) champ dans en_cours
old = "                'date_cloture': ref,\n                'retard': retard,\n            })"
new = "                'date_cloture': ref,\n                'retard': retard,\n                'taux_fin_cagd': taux_fin_cagd,\n            })"
if old in s:
    s = s.replace(old, new, 1); ok.append('C champ en_cours')

# D) moyenne financière = repli CAGD
old = "        fin_vals = [t['fin'] for t in dernier_taux.values() if t['fin'] > 0]"
new = "        fin_vals = [t['fin'] for t in dernier_taux.values() if t['fin'] > 0] or [p['taux_fin_cagd'] for p in en_cours if p.get('taux_fin_cagd') is not None]"
if old in s:
    s = s.replace(old, new, 1); ok.append('D moyenne financière')

# E) champ dans projets
old = "                'taux_phys': t.get('phys', 0),\n                'taux_fin': t.get('fin', 0),"
new = old + "\n                'taux_fin_cagd': p.get('taux_fin_cagd'),"
if old in s:
    s = s.replace(old, new, 1); ok.append('E champ projets')

# F) alerte critique si décaissement < 40 %
old = """                if t and t['phys'] < 70:
                    al['detail'] += f" et execution physique {t['phys']:.0f}% < 70%"
                    al['niveau'] = 'critique'"""
new = old + """
                tc = taux_cagd_by_code.get(al['code'])
                if tc is not None and tc < 40:
                    al['detail'] += f" et decaissement {tc:.0f}% < 40%"
                    al['niveau'] = 'critique'"""
if old in s:
    s = s.replace(old, new, 1); ok.append('F alerte critique')

open(p, 'w', encoding='utf-8').write(s)
for k in ['A index CAGD', 'B taux par projet', 'C champ en_cours', 'D moyenne financière', 'E champ projets', 'F alerte critique']:
    print(('✅ ' if k in ok else '❌ ') + k)