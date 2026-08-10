import re
import time
import urllib.request
import ssl
from datetime import datetime

LOCAL_PATH = 'accueil.html'
URL = 'https://sgiad-platform.onrender.com/'

with open(LOCAL_PATH, 'r', encoding='utf-8') as f:
    local = f.read()

m = re.search(r"<h1[^>]*class=[\"']hero-title[\"'][^>]*>(.*?)</h1>", local, re.S|re.I)
if m:
    hero = re.sub(r"\s+"," ", m.group(1)).strip()
else:
    m2 = re.search(r"<title>(.*?)</title>", local, re.S|re.I)
    hero = m2.group(1).strip() if m2 else ''

ctx = ssl.create_default_context()

print('Local hero to match:', hero)

for i in range(9):
    ts = datetime.utcnow().isoformat() + 'Z'
    try:
        req = urllib.request.Request(URL, headers={'User-Agent':'SGIAD-Poller/1.0'})
        with urllib.request.urlopen(req, timeout=15, context=ctx) as r:
            body = r.read().decode('utf-8', errors='replace')
            found = hero in body
            print(f"[{ts}] try {i+1}/9: status={r.status} found={found}")
            if found:
                print('MATCH FOUND — deployment updated.')
                break
    except Exception as e:
        print(f"[{ts}] try {i+1}/9: ERROR: {e}")
    if i < 8:
        time.sleep(20)

print('Done')
