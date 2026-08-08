// js/auth_client.js
// ------------------------------------------------------------------
// Gestion du token d'authentification Supabase côté client :
//  - stockage des tokens après connexion (depuis la page d'accueil)
//  - injection automatique du header Authorization sur tous les
//    appels /api/... (fetch natif intercepté)
//  - rafraîchissement automatique du token expiré (1 tentative)
//  - redirection vers l'accueil si la session est invalide
// ------------------------------------------------------------------
(function () {
    const KEY_ACCESS = 'sgiad_access_token';
    const KEY_REFRESH = 'sgiad_refresh_token';
    const KEY_USER = 'sgiad_accueil_user';

    window.SGIADAuth = {
        saveTokens: function (accessToken, refreshToken) {
            if (accessToken) localStorage.setItem(KEY_ACCESS, accessToken);
            if (refreshToken) localStorage.setItem(KEY_REFRESH, refreshToken);
        },
        getAccessToken: function () {
            return localStorage.getItem(KEY_ACCESS);
        },
        logout: function (redirectTo) {
            localStorage.removeItem(KEY_ACCESS);
            localStorage.removeItem(KEY_REFRESH);
            localStorage.removeItem(KEY_USER);
            window.location.href = redirectTo || '/';
        }
    };

    function isApiUrl(url) {
        try {
            const u = new URL(url, window.location.origin);
            return u.origin === window.location.origin && u.pathname.indexOf('/api/') === 0;
        } catch (e) {
            return typeof url === 'string' && url.indexOf('/api/') === 0;
        }
    }

    const originalFetch = window.fetch.bind(window);

    async function tryRefreshToken() {
        const refreshToken = localStorage.getItem(KEY_REFRESH);
        if (!refreshToken) return false;
        try {
            const res = await originalFetch('/api/auth/refresh', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ refresh_token: refreshToken })
            });
            if (!res.ok) return false;
            const data = await res.json();
            window.SGIADAuth.saveTokens(data.access_token, data.refresh_token);
            return true;
        } catch (e) {
            return false;
        }
    }

    window.fetch = async function (input, init) {
        init = init || {};
        const url = (typeof input === 'string') ? input : (input && input.url) || '';

        // Seuls les appels vers notre propre API portent le token
        if (!isApiUrl(url)) return originalFetch(input, init);

        let token = window.SGIADAuth.getAccessToken();
        if (token) {
            init.headers = new Headers(init.headers || {});
            if (!init.headers.has('Authorization')) {
                init.headers.set('Authorization', 'Bearer ' + token);
            }
        }

        let res = await originalFetch(input, init);

        // Le 401 des endpoints de connexion est un refus d'identifiants, pas une session invalide
        const isAuthFlow = url.indexOf('/api/auth/') === 0 || url.indexOf('/api/accueil/login') === 0;
        if (res.status === 401 && !isAuthFlow) {
            // Pas de token du tout : retour a l'accueil pour se connecter
            if (!token) {
                window.SGIADAuth.logout('/');
                return res;
            }
            // Token expiré/invalid -> tentative de refresh puis nouvel essai
            if (await tryRefreshToken()) {
                init.headers = new Headers(init.headers || {});
                init.headers.set('Authorization', 'Bearer ' + window.SGIADAuth.getAccessToken());
                res = await originalFetch(input, init);
                if (res.status !== 401) return res;
            }
            // Session définitivement invalide : retour à l'accueil
            window.SGIADAuth.logout('/');
        }
        return res;
    };

    // Garde d'accès : les pages internes (/app, /modules/...) exigent une session
    const path = window.location.pathname;
    const pageInterne = path.indexOf('/app') === 0 || path.indexOf('/modules/') === 0;
    if (pageInterne && !localStorage.getItem(KEY_ACCESS) && !localStorage.getItem(KEY_USER)) {
        window.location.replace('/');
    }
})();
