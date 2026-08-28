# -*- coding: utf-8 -*-
import re

p = 'modules/recap.html'
s = open(p, encoding='utf-8').read()

print('=== Recherche des constantes de données ===\n')

# Chercher les déclarations de constantes principales
patterns = [
    ('RECOS', r'const\s+RECOS\s*='),
    ('REVUES', r'const\s+REVUES\s*='),
    ('D (objet principal)', r'const\s+D\s*=\s*\{'),
    ('cells', r'cells\s*[:=]'),
    ('secteurs', r'secteurs\s*[:=]'),
    ('partenaires', r'partenaires\s*[:=]'),
    ('projets', r'projets\s*[:=]'),
]

for name, pat in patterns:
    matches = list(re.finditer(pat, s))
    if matches:
        print(f'✅ {name} : {len(matches)} occurrence(s)')
        for m in matches[:3]:  # Max 3
            line_num = s[:m.start()].count('\n') + 1
            snippet = s[max(0, m.start()-20):min(len(s), m.end()+150)].replace('\n', ' ')
            print(f'   L{line_num} : ...{snippet}...')
    else:
        print(f'❌ {name} : introuvable')
    print()

# Chercher les appels fetch existants
fetches = re.findall(r"fetch\(['\"]([^'\"]+)['\"]", s)
print('=== Appels fetch existants ===')
print(fetches if fetches else '❌ Aucun fetch trouvé (données 100% statiques)')
