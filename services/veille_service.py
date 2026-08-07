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
import xml.etree.ElementTree as ET

# Requêtes de veille (mots-clés)
REQUETES = [
    '"accord de financement" Bénin',
    '"convention de financement" Bénin',
    'Bénin accord signé financement développement',
]


def _http_text(url, timeout=20):
    req = urllib.request.Request(url, headers={'User-Agent': 'SGIAD-Veille/1.0'})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read().decode('utf-8', 'ignore')


def _http_json(url, timeout=20):
    return json.loads(_http_text(url, timeout))


def _pertinent(titre):
    """Filtre léger : l'article doit parler du Bénin et d'un accord/financement."""
    t = (titre or '').lower()
    if not ('bénin' in t or 'benin' in t):
        return False
    return any(k in t for k in ('accord', 'convention', 'financement', 'signé', 'signe', 'don', 'prêt'))


def _scan_gdelt(query):
    """Articles récents via GDELT DOC API (gratuit, sans clé)."""
    articles = []
    params = urllib.parse.urlencode({
        'query': query, 'mode': 'ArtList', 'format': 'JSON',
        'timespan': '3d', 'maxrecords': '25', 'sort': 'DateDesc',
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
    except Exception as e:
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
    from db import get_supabase
    sb = get_supabase()
    existants = {r['url'] for r in (sb.table('veille_alertes').select('url').execute().data or [])}

    nouvelles = []
    for query in REQUETES:
        for art in _scan_gdelt(query) + _scan_google_news(query):
            url = art.get('url') or ''
            if not url or url in existants or not _pertinent(art.get('titre')):
                continue
            existants.add(url)
            nouvelles.append(art)
        time.sleep(1)  # politesse envers les APIs gratuites

    enregistrees = 0
    for art in nouvelles[:max_nouveautes]:
        resume = _gemini_resume(art['titre'], art['source'])
        partenaire, montant = _extraire_champs(resume)
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
    return enregistrees
