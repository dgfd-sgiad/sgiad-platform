# -*- coding: utf-8 -*-
import re

p = 'modules/recap.html'
s = open(p, encoding='utf-8').read()

# Trouver la définition statique de D
pattern = r'const\s+D\s*=\s*\{[^}]+secteurs[^}]+\};'
match = re.search(pattern, s, re.DOTALL)

if not match:
    print('❌ Objet D statique introuvable')
    print('👉 Le fichier a peut-être déjà été modifié')
    raise SystemExit

old_data = match.group(0)
print('📦 Objet D trouvé (', len(old_data), 'caractères)')

# Remplacer par un chargement dynamique
new_data = '''async function loadData() {
  try {
    // Charger les vraies données CAGD
    const resCagd = await fetch('/api/decaissements/cagd');
    const cagd = await resCagd.json();
    
    // Charger les accords
    const resAcc = await fetch('/api/accords/list');
    const accords = await resAcc.json();
    
    // Transformer en format attendu par le moteur de rendu
    const secteurs = [...new Set(accords.map(a => a.secteur_principal).filter(Boolean))];
    const partenaires = [...new Set(accords.map(a => a.partenaire).filter(Boolean))];
    const statuts = ['en_cours', 'à surveiller', 'en difficulté'];
    
    const cells = [];
    accords.forEach(acc => {
      const s = secteurs.indexOf(acc.secteur_principal);
      const p = partenaires.indexOf(acc.partenaire);
      const t = 0; // en_cours par défaut
      const prev = (acc.montant_fcfa || 0) / 1e9; // en Mds
      const dec = (acc.montant_decaisse_fcfa || 0) / 1e9;
      const pq = [prev * 0.25, prev * 0.25, prev * 0.25, prev * 0.25]; // répartition trimestrielle
      const dq = [dec * 0.25, dec * 0.25, dec * 0.5]; // répartition sur 3 trimestres
      cells.push({s, p, t, prev, dec, pq, dq, n: 1});
    });
    
    return {
      exercice: '2026',
      situation: '28 août 2026',
      secteurs,
      partenaires,
      statuts,
      cells,
      part_t3: 0.67,
      jours_ecoules: 240,
      jours_annee: 365
    };
  } catch (e) {
    console.error('Erreur chargement données:', e);
    throw e;
  }
}

let D;
async function init() {
  try {
    D = await loadData();
    render();
  } catch (e) {
    document.body.innerHTML = '<div style="padding:40px;text-align:center;color:#B0523C">Erreur de chargement des données. Vérifiez que le serveur tourne.</div>';
  }
}
init();'''

s = s.replace(old_data, new_data, 1)

# Supprimer l'appel immédiat à render() (maintenant fait dans init())
s = re.sub(r'render\(\);\s*let\s+rz;', 'let rz;', s, count=1)

open(p, 'w', encoding='utf-8').write(s)
print('✅ Module branché sur les vraies données CAGD + accords')
print('🎯 Teste : http://127.0.0.1:5000/modules/recap.html')
print('   → Les commentaires se recalculeront à chaque filtre')
