# -*- coding: utf-8 -*-
import re

# Le contenu du design est dans le clipboard ou un fichier
# On va le lire depuis le dernier upload
try:
    with open('Pasted_Text_1787931985040.txt', encoding='utf-8') as f:
        content = f.read()
except FileNotFoundError:
    print('❌ Fichier Pasted_Text_1787931985040.txt introuvable')
    print('👉 Colle le contenu HTML dans ce fichier avant de relancer')
    raise SystemExit

# 1) Remplacer la police base64 tronquée par Google Fonts
content = re.sub(
    r'@font-face\s*\{[^}]*Archivo[^}]*\}',
    '@import url("https://fonts.googleapis.com/css2?family=Archivo:wght@400;500;600;700&display=swap");',
    content,
    flags=re.DOTALL
)

# 2) Mettre à jour le titre
content = content.replace(
    '<title>SGIAD-Bénin — Suivi des projets & revues · Prévisions & décaissements</title>',
    '<title>SGIAD-Bénin — Récapitulatif</title>'
)

# 3) Ajouter le bouton "Retour immédiat"
if 'Retour immédiat' not in content:
    btn_retour = '<button onclick="history.back()" title="Retour immédiat" style="position:fixed;bottom:20px;left:20px;z-index:99999;background:#0a2540;color:#fff;border:none;padding:10px 16px;border-radius:30px;font-size:12px;font-weight:700;cursor:pointer;box-shadow:0 4px 15px rgba(0,0,0,0.3);display:flex;align-items:center;gap:6px">↩️ Retour immédiat</button>'
    content = content.replace('</body>', btn_retour + '\n</body>')

# 4) Écrire le nouveau fichier
with open('modules/recap.html', 'w', encoding='utf-8') as f:
    f.write(content)
print('✅ Fichier modules/recap.html créé (', len(content), 'caractères)')

# 5) Ajouter l'onglet dans la sidebar de suivi.html
try:
    with open('modules/suivi.html', encoding='utf-8') as f:
        suivi = f.read()
except FileNotFoundError:
    print('❌ modules/suivi.html introuvable')
    raise SystemExit

anchor = '<button class="active" onclick="showView(\'dash\', this)">🏠 Tableau de bord</button>'
if 'recap.html' not in suivi and anchor in suivi:
    recap_btn = '\n    <button onclick="window.location.href=\'/modules/recap.html\'">📊 Récapitulatif</button>'
    suivi = suivi.replace(anchor, anchor + recap_btn, 1)
    with open('modules/suivi.html', 'w', encoding='utf-8') as f:
        f.write(suivi)
    print('✅ Onglet "📊 Récapitulatif" ajouté dans la sidebar de suivi.html')
elif 'recap.html' in suivi:
    print('ℹ️ Onglet déjà présent')
else:
    print('⚠️ Ancre non trouvée dans la sidebar')

print('\n🎯 Teste : http://127.0.0.1:5000/modules/recap.html')
