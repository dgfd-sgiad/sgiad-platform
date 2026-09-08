# -*- coding: utf-8 -*-
import re, os

CDN_ECHARTS = '<script src="https://cdn.jsdelivr.net/npm/echarts@5/dist/echarts.min.js"></script>'
FONTS = ('<link rel="preconnect" href="https://fonts.googleapis.com">'
         '<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>'
         '<link href="https://fonts.googleapis.com/css2?family=Archivo:wght@400;500;600;700'
         '&family=Fraunces:opsz,wght@9..144,500;9..144,600;9..144,700&display=swap" rel="stylesheet">')

for p in ['modules/recap.html', 'modules/recos.html', 'modules/projets.html']:
    if not os.path.exists(p):
        print('  (absent)', p); continue
    s = open(p, encoding='utf-8', errors='ignore').read()
    n0 = len(s)

    # 1) Polices base64 -> Google Fonts (gain de poids + affichage rapide)
    s = re.sub(r'@font-face\s*\{[^}]*base64[^}]*\}', '', s, flags=re.DOTALL)
    if 'fonts.googleapis.com' not in s:
        s = s.replace('<style>', FONTS + '\n<style>', 1)

    # 2) Bundle ECharts inline (>100 Ko) -> CDN
    def repl(m):
        return CDN_ECHARTS if len(m.group(0)) > 100000 else m.group(0)
    s = re.sub(r'<script[^>]*>.*?</script>', repl, s, flags=re.DOTALL)

    # 3) Fragment de JS qui fuit entre le dernier </script> et </body> -> supprimé
    i = s.rfind('</script>'); j = s.find('</body>')
    if i != -1 and j != -1 and j > i + len('</script>'):
        s = s[:i + len('</script>')] + '\n' + s[j:]

    open(p, 'w', encoding='utf-8').write(s)
    print('  ✅ nettoyé', p, ':', n0, '->', len(s), 'caractères')

print('\n🎯 Ctrl + F5 sur les 3 pages : affichage rapide + plus de texte parasite')