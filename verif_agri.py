# -*- coding: utf-8 -*-
import requests
BASE = 'http://127.0.0.1:5000'
acc = requests.get(BASE + '/api/accords/list').json()
agri = [a for a in acc if str(a.get('secteur_principal') or '').strip().lower().startswith('agric')]
enc = [a for a in agri if str(a.get('statut') or '').strip().lower() == 'en cours']
print('Agriculture (tous statuts) :', len(agri))
print('Agriculture "En cours"     :', len(enc))
r = requests.get(BASE + '/api/suivi/recap').json()
si = [i for i, k in enumerate(r['secteurs']) if k.startswith('AGRIC')]
if si:
    n = sum(c['n'] for c in r['cells'] if c['s'] == si[0])
    prev = sum(c['prev'] for c in r['cells'] if c['s'] == si[0])
    dec = sum(c['dec'] for c in r['cells'] if c['s'] == si[0])
    print('Module Récapitulatif       :', n, 'projets ·', round(prev, 1), 'Mds engagés ·', round(dec, 1), 'Mds décaissés')