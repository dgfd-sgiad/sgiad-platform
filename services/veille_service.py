# -*- coding: utf-8 -*-
"""Veille automatique des accords signés partagés en ligne.

Sources gratuites sans clé API :
  - GDELT DOC API (presse mondiale, quasi temps réel)
  - Google News RSS (flux de recherche)

IA optionnelle (gratuite) : variable d'environnement GEMINI_API_KEY
(clé gratuite Google AI Studio) -> résumé + extraction partenaire/montant.

Notification optionnelle (gratuite) : TELEGRAM_BOT_TOKEN + TELEGRAM_CHAT_ID.

Stockage : table Supabase `veille_alertes` (dédoublonnage par URL).
"""
import os
import re
import json
import time
import urllib.request
import urllib.parse
import urllib.error
import xml.etree.ElementTree as ET

# Suivi des erreurs pour éviter le spam dans les logs
_GDELT_429_LOGGED = False
_RLS_ERROR_LOGGED = False

# Requêtes de veille enrichies (mots-clés larges, sources officielles P1, instruments financiers et bailleurs)
REQUETES = [
    'Bénin financement',
    'Benin financing',
    'Bénin ressources financières',
    'Bénin financement développement',
    'Bénin mobilisation ressources',
    'Benin resource mobilization',
    'Bénin financement extérieur',
    'Bénin ressources extérieures',
    'Bénin nouveau financement',
    'Bénin financement approuvé',
    'Bénin financement accordé',
    'Bénin financement mobilisé',
    'Bénin prêt approuvé',
    'Bénin don approuvé',
    'Bénin financement additionnel',
    'Bénin décaissement',
    'Bénin tirage',
    'Bénin signe accord financement',
    'Bénin signe accord prêt',
    'Bénin convention financement',
    'Bénin accord prêt',
    'Bénin contrat financement',
    'Bénin convention crédit',
    'Bénin Banque mondiale financement',
    'Bénin BAD financement',
    'Bénin BOAD financement',
    'Bénin AFD financement',
    'Bénin BEI financement',
    'Bénin BID financement',
    'Bénin Union européenne financement',
    'Bénin FMI financement',
    'Bénin FIDA financement',
    'Bénin AIIB financement',
    'Bénin BADEA financement',
    '"accord de financement" Bénin',
    '"convention de financement" Bénin',
    '"accord de prêt" Bénin',
    '"convention de prêt" Bénin',
    'Benin "Financing Agreement"',
    'Benin "Loan Agreement"',
    'site:finances.bj "accord" OR "convention" OR "prêt" OR "financement"',
    'site:assemblee-nationale.bj "ratification" OR "accord" OR "prêt"',
    'site:sgg.gouv.bj "décret" OR "ratification" OR "accord"',
    '"Direction Générale du Budget" Bénin financement',
    '"Secrétariat Général du Gouvernement" Bénin accord',
]


def _http_text(url, timeout=20):
    req = urllib.request.Request(url, headers={'User-Agent': 'SGIAD-Veille/1.0'})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read().decode('utf-8', 'ignore')


def _http_json(url, timeout=20):
    return json.loads(_http_text(url, timeout))


def _pertinent(titre):
    """Évaluation élargie basée sur les mots-clés de mobilisation, d'action et le Bénin (score >= 4)."""
    t = (titre or '').lower()
    
    # Rejeter si le titre concerne un autre pays et ne mentionne pas le Bénin
    autres_pays = ('togo', 'guinée', 'côte d\'ivoire', 'cote d\'ivoire', 'sénégal', 'senegal', 'burkina', 'mali', 'niger', 'ghana', 'nigéria', 'nigeria')
    if any(p in t[:20] for p in autres_pays) and not ('bénin' in t or 'benin' in t):
        return False

    # Doit mentionner le Bénin (Groupe D)
    has_benin = any(k in t for k in ('bénin', 'benin', 'republique du bénin', 'republic of benin', 'government of benin'))
    if not has_benin:
        return False
        
    score = 0
    
    # Groupe A (Accord juridique / Financement) (+4)
    groupe_a = ('accord de financement', 'financing agreement', 'accord de prêt', 'loan agreement', 'accord de crédit', 'credit agreement', 'convention de financement', 'convention de prêt', 'convention de crédit', 'accord de don', 'grant agreement', 'protocole d\'accord', 'contrat de financement', 'project agreement', 'guarantee agreement')
    if any(k in t for k in groupe_a):
        score += 4
        
    # Groupe B (Verbes d'action / Mobilisation) (+3)
    groupe_b = ('mobilise', 'mobilisation', 'obtient', 'accorde', 'approuve', 'décaisse', 'débloque', 'signe', 'octroie', 'lève', 'emprunte', 'garantie', 'appui budgétaire', 'soutien budgétaire')
    if any(k in t for k in groupe_b):
        score += 3
        
    # Groupe C (Instruments / Ressources) (+2)
    groupe_c = ('prêt', 'loan', 'crédit', 'credit', 'don', 'grant', 'subvention', 'garantie', 'cofinancement', 'co-financing', 'financement conjoint', 'financement additionnel', 'additional financing', 'refinancement', 'tirage', 'ressources', 'financement', 'investissement', 'ressources concessionnelles')
    if any(k in t for k in groupe_c):
        score += 2
        
    # Bailleurs / Institutions (+2)
    bailleurs = ('banque mondiale', 'world bank', 'bad', 'afdb', 'boad', 'afd', 'bei', 'bid', 'fmi', 'imf', 'fida', 'aiib', 'badea', 'union européenne', 'ue')
    if any(k in t for k in bailleurs):
        score += 2
        
    return score >= 4


def _recent(date_str, max_days=90, titre=""):
    """Vérifie si l'article date de moins de max_days jours et ne mentionne pas une année ancienne dans le titre."""
    t = (titre or '').lower()
    # Rejeter si le titre mentionne explicitement une année ancienne (2010-2024)
    for y in range(2010, 2025):
        if str(y) in t:
            return False

    if not date_str:
        return True
    try:
        from email.utils import parsedate_to_datetime
        from datetime import datetime, timezone
        d_str = str(date_str).strip()
        dt = None
        if 'GMT' in d_str or ',' in d_str:
            dt = parsedate_to_datetime(d_str)
        else:
            if len(d_str) >= 10:
                dt = datetime.fromisoformat(d_str[:10].replace('Z', '+00:00')).replace(tzinfo=timezone.utc)
        if dt:
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=timezone.utc)
            age = (datetime.now(timezone.utc) - dt).days
            if age > max_days or age < -2:
                return False
    except Exception:
        pass
    return True


def _scan_gdelt(query):
    """Articles récents via GDELT DOC API (gratuit, sans clé)."""
    global _GDELT_429_LOGGED
    articles = []
    params = urllib.parse.urlencode({
        'query': query, 'mode': 'ArtList', 'format': 'JSON',
        'timespan': '7d', 'maxrecords': '50', 'sort': 'DateDesc',
    })
    try:
        data = _http_json('https://api.gdeltproject.org/api/v2/doc/doc?' + params)
        for a in data.get('articles', []):
            articles.append({
                'url': (a.get('url') or '').strip(),
                'titre': (a.get('title') or '').strip(),
                'source': (a.get('domain') or a.get('sourcecountry') or 'GDELT').strip(),
                'date_article': (a.get('seendate') or '').strip(),
            })
    except urllib.error.HTTPError as e:
        if e.code == 429:
            if not _GDELT_429_LOGGED:
                print("[veille] Scan ignoré : API GDELT surchargée (429)")
                _GDELT_429_LOGGED = True
        else:
            print(f'[veille] GDELT erreur HTTP {e.code} :', e)
    except Exception as e:
        if '429' in str(e) or 'Too Many Requests' in str(e):
            if not _GDELT_429_LOGGED:
                print("[veille] Scan ignoré : API GDELT surchargée (429)")
                _GDELT_429_LOGGED = True
        else:
            print('[veille] GDELT erreur :', e)
    return articles


def _scan_google_news(query):
    """Articles récents via Google News RSS (gratuit, sans clé)."""
    articles = []
    params = urllib.parse.urlencode({'q': query, 'hl': 'fr', 'gl': 'BJ', 'ceid': 'BJ:fr'})
    try:
        root = ET.fromstring(_http_text('https://news.google.com/rss/search?' + params))
        for item in root.iter('item'):
            src_el = item.find('source')
            articles.append({
                'url': (item.findtext('link') or '').strip(),
                'titre': (item.findtext('title') or '').strip(),
                'source': ((src_el.text if src_el is not None else '') or 'Google News').strip(),
                'date_article': (item.findtext('pubDate') or '').strip(),
            })
    except Exception as e:
        print('[veille] Google News erreur :', e)
    return articles


def _gemini_resume(titre, source):
    """Résumé IA via Gemini (gratuit). Renvoie None si aucune clé ou en cas d'erreur."""
    key = (os.environ.get('GEMINI_API_KEY') or '').strip()
    if not key:
        return None
    try:
        prompt = (
            "Tu es un analyste de la DGFD Bénin. Résume en 2 phrases maximum cet article "
            "sur un accord ou un financement du développement, puis ajoute sur des lignes "
            "séparées : PARTENAIRE: <nom du partenaire technique et financier>, "
            "MONTANT: <montant si mentionné, sinon 'non précisé'>, "
            "SECTEUR: <secteur si mentionné, sinon 'non précisé'>.\n"
            f"Titre : {titre}\nSource : {source}"
        )
        payload = json.dumps({'contents': [{'parts': [{'text': prompt}]}]}).encode()
        req = urllib.request.Request(
            'https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key=' + key,
            data=payload, headers={'Content-Type': 'application/json'})
        with urllib.request.urlopen(req, timeout=30) as r:
            data = json.loads(r.read().decode())
        return data['candidates'][0]['content']['parts'][0]['text'].strip()
    except Exception as e:
        print('[veille] Gemini erreur :', e)
        return None


def _extraire_champs(resume):
    """Extrait PARTENAIRE / MONTANT du résumé IA (lignes normalisées)."""
    partenaire, montant = '', ''
    if resume:
        m = re.search(r'PARTENAIRE\s*:\s*([^\n]+)', resume, re.I)
        if m:
            partenaire = m.group(1).strip()
        m = re.search(r'MONTANT\s*:\s*([^\n]+)', resume, re.I)
        if m:
            montant = m.group(1).strip()
    return partenaire, montant



PARTENAIRES_CONNUS = [
    ('AFD', ['afd', 'agence francaise de developpement', 'agence française de développement']),
    ('BAD', ['bad', 'banque africaine de developpement', 'banque africaine de développement', 'afdb']),
    ('Banque Mondiale', ['banque mondiale', 'world bank', 'bm']),
    ('BOAD', ['boad']),
    ('UEMOA', ['uemoa']),
    ('FMI', ['fmi', 'imf', 'fonds monetaire international']),
    ('Union Européenne', ['union europeenne', 'union européenne', 'ue']),
    ('KfW', ['kfw']),
    ('JICA', ['jica']),
    ('BID', ['banque islamique de developpement', 'bid']),
    ('FIDA', ['fida']),
    ('Chine', ['chine', 'eximbank', 'exim bank', 'rpc']),
    ('France', ['france', 'republique francaise', 'république française', 'paris']),
    ('Luxembourg', ['luxembourg']),
    ('Allemagne', ['allemagne', 'kfw', 'berlin']),
    ('Japon', ['japon', 'jica', 'tokyo']),
]

def _deviner_partenaire(titre):
    t = (titre or '').lower()
    trouv = [nom for nom, cles in PARTENAIRES_CONNUS if any(c in t for c in cles)]
    return ', '.join(trouv[:3])

_MONTANT_RE = re.compile(r'([\d\.,\s]+)\s*(milliards|milliard|millions|million|billion|mds)\s*(F CFA|FCFA|USD|US\$|\$|euros?|€)', re.I)

def _deviner_montant(titre):
    m = _MONTANT_RE.search(titre or '')
    if m:
        return (m.group(1).strip() + ' ' + m.group(2) + ' ' + m.group(3)).replace('  ', ' ')
    return ''

def _notifier_telegram(texte):
    """Envoi optionnel via bot Telegram (gratuit). Renvoie False si non configuré."""
    token = (os.environ.get('TELEGRAM_BOT_TOKEN') or '').strip()
    chat = (os.environ.get('TELEGRAM_CHAT_ID') or '').strip()
    if not token or not chat:
        return False
    try:
        data = urllib.parse.urlencode({'chat_id': chat, 'text': texte}).encode()
        urllib.request.urlopen(f'https://api.telegram.org/bot{token}/sendMessage',
                               data=data, timeout=15)
        return True
    except Exception as e:
        print('[veille] Telegram erreur :', e)
        return False


def scan_and_notify(max_nouveautes=10):
    """Scan des sources, dédoublonnage Supabase, résumé IA, notification Telegram.

    Renvoie le nombre de nouvelles alertes enregistrées."""
    global _RLS_ERROR_LOGGED
    from db import get_supabase
    sb = get_supabase()
    
    try:
        existants_resp = sb.table('veille_alertes').select('url').execute()
        existants = {r['url'] for r in (existants_resp.data or [])}
    except Exception as e:
        err_msg = str(e)
        if 'violates row-level security policy' in err_msg or 'veille_alertes' in err_msg:
            if not _RLS_ERROR_LOGGED:
                print("[veille] Permission RLS manquante pour veille_alertes")
                _RLS_ERROR_LOGGED = True
        else:
            print('[veille] Erreur lecture veille_alertes :', e)
        return 0

    nouvelles = []
    doublons = 0
    non_pertinents = 0
    requetes_rapides = [
        '"accord de financement" Bénin',
        'Bénin Banque Mondiale approuve',
        'Bénin BAD approuve',
        'Bénin AFD signe',
        'Bénin FMI approuve',
        'Bénin BOAD financement',
        'Bénin financement',
        'Benin financing',
    ]
    for query in requetes_rapides:
        bruts = _scan_google_news(query)
        try:
            bruts += _scan_gdelt(query)
        except Exception:
            pass
        for art in bruts:
            url = art.get('url') or ''
            if not url or url in existants:
                doublons += 1
                continue
            if not _pertinent(art.get('titre')) or not _recent(art.get('date_article'), max_days=90, titre=art.get('titre')):
                non_pertinents += 1
                continue
            existants.add(url)
            nouvelles.append(art)
        time.sleep(0.5)  # politesse rapide
    print(f'[veille] TOTAL : {len(nouvelles)} nouveau(x), {doublons} doublon(s), {non_pertinents} non pertinent(s)')

    enregistrees = 0
    for art in nouvelles[:max_nouveautes]:
        resume = _gemini_resume(art['titre'], art['source'])
        partenaire, montant = _extraire_champs(resume)
        if not partenaire:
            partenaire = _deviner_partenaire(art['titre'])
        if not montant:
            montant = _deviner_montant(art['titre'])
        try:
            sb.table('veille_alertes').insert({
                'url': art['url'],
                'titre': art['titre'][:500],
                'source': (art.get('source') or '')[:200],
                'date_article': (art.get('date_article') or '')[:60],
                'resume': resume or '',
                'partenaire': partenaire[:200],
                'montant': montant[:200],
            }).execute()
            enregistrees += 1
            _notifier_telegram(
                "📡 Accord signé détecté en ligne\n"
                f"{art['titre']}\n"
                f"Source : {art['source']}\n"
                f"{art['url']}"
            )
        except Exception as e:
            err_msg = str(e)
            if 'violates row-level security policy' in err_msg or 'veille_alertes' in err_msg:
                if not _RLS_ERROR_LOGGED:
                    print("[veille] Permission RLS manquante pour veille_alertes")
                    _RLS_ERROR_LOGGED = True
            else:
                print('[veille] Erreur insertion veille_alertes :', e)
    return enregistrees
