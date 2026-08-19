import re
s = open('api.py', encoding='utf-8').read()
old = '    chemin = f"{agent_id}/{int(time.time())}_{f.filename}"'
new = """    import re, os
    ext = os.path.splitext(f.filename or '')[1] or '.bin'
    ext = re.sub(r"[^A-Za-z0-9.]+", "", ext)
    chemin = f"{agent_id}/{int(time.time())}_piece{ext}" """
if old in s:
    s = s.replace(old, new)
    open('api.py', 'w', encoding='utf-8').write(s)
    print('✅ PATCH APPLIQUE')
else:
    print('❌ ligne introuvable, voici les lignes "chemin" actuelles :')
    for i, l in enumerate(s.splitlines(), 1):
        if 'chemin' in l:
            print(i, l)
            