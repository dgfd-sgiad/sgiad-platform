// js/app.js
document.addEventListener('DOMContentLoaded', () => {

    // --- Infos de session réelles (remplace les valeurs figées) ---
    fetch('/api/session/info')
        .then(res => res.json())
        .then(data => {
            if (data.error) return;

            const ipEl = document.getElementById('infoIP');
            if (ipEl) ipEl.textContent = data.ip || 'inconnue';

            const connexionEl = document.getElementById('infoConnexion');
            if (connexionEl) {
                const derniere = data.derniere_connexion
                    ? `Dernière connexion : ${data.derniere_connexion}`
                    : 'Première connexion';
                connexionEl.textContent = `${derniere} - Nombre total de connexions : ${data.total_connexions}`;
            }
        })
        .catch(() => {
            const connexionEl = document.getElementById('infoConnexion');
            if (connexionEl) connexionEl.textContent = 'Informations de connexion indisponibles (serveur API non joignable)';
        });

    const grid = document.getElementById('modulesGrid');

    if (grid && typeof modules !== 'undefined') {
        modules.forEach(mod => {
            const actif = mod.actif !== false;
            const card = document.createElement('div');
            card.className = 'module-card' + (actif ? '' : ' module-inactive');
            
            // Structure HTML qui correspond à votre CSS (.module-image, .module-title)
            // Le script cherche l'image dans assets/modules/[id].webp
            card.innerHTML = `
                <div class="module-image">
                    <img src="assets/modules/${mod.id}.webp" alt="${mod.title}" onerror="this.style.display='none'; this.nextElementSibling.style.display='block'">
                    <div class="placeholder-icon" style="display:none">${mod.icon}</div>
                    ${actif ? '' : '<span class="badge-non-actif">Non actif</span>'}
                </div>
                <h3 class="module-title">${mod.title}</h3>
            `;

            // Navigation vers le module au clic (bloquée si non actif)
            card.onclick = () => {
                if (!actif) {
                    alert(`Le module « ${mod.title} » n'est pas encore actif.`);
                    return;
                }
                window.location.href = mod.file;
            };

            grid.appendChild(card);
        });
    }
});