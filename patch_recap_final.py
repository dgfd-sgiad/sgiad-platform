# -*- coding: utf-8 -*-

# ---------- A) Nouvel endpoint serveur : /api/suivi/recap ----------
p = 'suivi.py'
s = open(p, encoding='utf-8').read()
if '/api/suivi/recap' in s:
    print('ℹ️ Endpoint déjà présent dans suivi.py')
else:
    anchor = '# Creation auto de la table au demarrage'
    EP = r'''_RECAP_CACHE = {'t': 0.0, 'd': None}

@bp.route('/api/suivi/recap')
def suivi_recap():
    """Agregats reels (projets En cours uniquement) pour le module Recapitulatif."""
    import re as _re, difflib, time as _tm
    global _RECAP_CACHE
    now = _tm.time()
    if _RECAP_CACHE['d'] and now - _RECAP_CACHE['t'] < 300:
        return jsonify(_RECAP_CACHE['d'])
    try:
        sb = get_supabase()
        acc = sb.table('accords_consolides').select('objet_accord, partenaire, secteur_principal, montant_total_fcfa, statut, date_cloture, nouvelle_date_cloture').execute().data or []
        cagd = sb.table('decaissements_cagd').select('projet, periode, montant_total_fcfa').execute().data or []
    except Exception as e:
        return jsonify({'error': str(e)}), 500

    def _n(x):
        x = _strip_accents(str(x or '').upper())
        return _re.sub(r'[^A-Z0-9 ]', ' ', x)

    def _ac(x):
        m = _re.search(r'\(([A-Z0-9][A-Za-z0-9\- ]{2,})\)', str(x or ''))
        return _n(m.group(1)) if m else ''

    cum = {}
    for c in cagd:
        k = _n(c.get('projet'))
        y = int(c.get('periode') or 0)
        v = float(c.get('montant_total_fcfa') or 0)
        if k not in cum or y > cum[k][0]:
            cum[k] = (y, v, str(c.get('projet') or ''))
    crow = [(k, val[1], k, _ac(val[2])) for k, val in cum.items()]

    def _score(na, aa, cn, ca):
        if aa and ca and (aa in ca or ca in aa):
            return 0.8
        if not na or not cn:
            return 0.0
        return difflib.SequenceMatcher(None, na[:60], cn[:60]).ratio()

    PARTS = ['AFD', 'BAD', 'Banque mondiale', 'BID', 'Union européenne']
    def _pidx(pp):
        pp = _n(pp)
        if pp.startswith('AFD') or pp.startswith('AGENCE FRANCAISE'):
            return 0
        if 'BAD' in pp:
            return 1
        if ('BANQUE MONDIALE' in pp) or ('BIRD' in pp) or ('IDA' in pp) or ('AID' in pp):
            return 2
        if 'BID' in pp:
            return 3
        if 'UNION EUROPEENNE' in pp:
            return 4
        return 5

    secteurs, sec_idx, cells, nproj = [], {}, {}, 0
    for a in acc:
        if str(a.get('statut') or '').strip().lower() != 'en cours':
            continue
        prev = float(a.get('montant_total_fcfa') or 0) / 1e9
        if prev <= 0:
            continue
        nproj += 1
        na = _n(a.get('objet_accord')); aa = _ac(a.get('objet_accord'))
        best, bv = 0.0, 0.0
        for (ck, cv, cn, ca) in crow:
            sc = _score(na, aa, cn, ca)
            if sc > best:
                best, bv = sc, cv
            if best >= 0.8:
                break
        dec = min(prev, bv / 1e9) if best >= 0.45 else 0.0
        ref = str(a.get('nouvelle_date_cloture') or a.get('date_cloture') or '')[:10]
        taux = dec / prev * 100 if prev else 0
        proche = bool(ref) and ref <= '2027-08-28'
        t = 2 if (taux < 40 and proche) else (1 if (proche or taux < 50) else 0)
        sg = str(a.get('secteur_principal') or 'NON PRECISE').strip().upper()
        if sg not in sec_idx:
            sec_idx[sg] = len(secteurs); secteurs.append(sg)
        key = (sec_idx[sg], _pidx(a.get('partenaire')), t)
        cc = cells.setdefault(key, {'prev': 0.0, 'dec': 0.0, 'n': 0})
        cc['prev'] += prev; cc['dec'] += dec; cc['n'] += 1

    out = {
        'secteurs': secteurs,
        'partenaires': PARTS + ['Autres'],
        'statuts': ['En cours', 'À surveiller', 'En difficulté'],
        'cells': [{'s': k[0], 'p': k[1], 't': k[2],
                   'prev': round(v['prev'], 2), 'dec': round(v['dec'], 2),
                   'pq': [round(v['prev'] * .25, 2)] * 4,
                   'dq': [round(v['dec'] * .3, 2), round(v['dec'] * .3, 2), round(v['dec'] * .4, 2)],
                   'n': v['n']} for k, v in cells.items()],
        'exercice': '2026', 'situation': '28 août 2026', 'part_t3': 2 / 3,
        'jours_ecoules': 240, 'jours_annee': 365, 'nproj': nproj,
    }
    _RECAP_CACHE = {'t': now, 'd': out}
    return jsonify(out)

'''
    if anchor in s:
        s = s.replace(anchor, EP + anchor, 1)
        open(p, 'w', encoding='utf-8').write(s)
        print('✅ Endpoint /api/suivi/recap ajouté (projets En cours + matching difflib)')
    else:
        print('❌ Ancre suivi.py introuvable')

# ---------- B) recap.html : fetch simple sur l'endpoint ----------
p2 = 'modules/recap.html'
h = open(p2, encoding='utf-8').read()
start = h.find('function _fetchJSON')
endm = 'jours_annee:365};'
end = h.find(endm, start)
if start == -1 or end == -1:
    print('❌ Bloc builder introuvable dans recap.html')
else:
    end += len(endm)
    NEWJS = '''function _fetchJSON(u){try{var x=new XMLHttpRequest();x.open('GET',u,false);x.send(null);return x.status===200?JSON.parse(x.responseText):null;}catch(e){return null;}}
var _D=_fetchJSON('/api/suivi/recap');
if(!_D||!_D.cells){console.error('[SGIAD] /api/suivi/recap indisponible');_D={secteurs:[],partenaires:['AFD','BAD','Banque mondiale','BID','Union européenne','Autres'],statuts:['En cours','À surveiller','En difficulté'],cells:[],exercice:'2026',situation:'28 août 2026',part_t3:0.6667,jours_ecoules:240,jours_annee:365};}
const D=_D;
console.log('[SGIAD] projets En cours :', D.nproj);'''
    h = h[:start] + NEWJS + h[end:]
    open(p2, 'w', encoding='utf-8').write(h)
    print('✅ recap.html branché sur /api/suivi/recap')

print('\n👉 1) Redémarre le serveur : taskkill /F /IM python.exe puis python api.py')
print('👉 2) Ctrl + F5 sur http://127.0.0.1:5000/modules/recap.html')
