/**
 * LocalisationSelector v2 — Arbre à puces dépliables
 * ─────────────────────────────────────────────────────────────────────────
 * Département > Commune > Arrondissement > Village, avec sélection multiple
 * à chaque niveau et affichage en cascade (les départements sont affichés
 * en rangée ; cliquer sur la flèche d'un département déplie ses communes
 * juste en dessous de lui, et ainsi de suite jusqu'au village).
 *
 * Format de stockage inchangé (une seule chaîne) :
 *   ATLANTIQUE(Abomey-Calavi(Akassato(Togba,Zinvié)),Ouidah);ALIBORI(Kandi,Malanville)
 *
 * API publique identique à la version précédente :
 *   const sel = new LocalisationSelector('#loc-container', { apiBase: '...' });
 *   await sel.init();
 *   sel.getEncodedString();
 *   sel.loadEncodedString(str);
 *   sel.getSelectionTree();
 *   sel.getFlatSelectionNames();
 *   sel.reset();
 */
(function (global) {
  'use strict';

  // ── Encodage / décodage (inchangés) ──────────────────────────────────────

  function encodeLocalisation(tree) {
    function encodeNode(node) {
      const parts = [];
      for (const name of Object.keys(node)) {
        const children = node[name];
        if (children && Object.keys(children).length > 0) {
          parts.push(`${name}(${encodeNode(children)})`);
        } else {
          parts.push(name);
        }
      }
      return parts.join(',');
    }
    const parts = [];
    for (const dep of Object.keys(tree)) {
      const children = tree[dep];
      if (children && Object.keys(children).length > 0) {
        parts.push(`${dep}(${encodeNode(children)})`);
      } else {
        parts.push(dep);
      }
    }
    return parts.join(';');
  }

  function splitTop(s, sep) {
    const parts = [];
    let depth = 0;
    let cur = '';
    for (const ch of s) {
      if (ch === '(') { depth++; cur += ch; }
      else if (ch === ')') { depth--; cur += ch; }
      else if (ch === sep && depth === 0) { parts.push(cur.trim()); cur = ''; }
      else { cur += ch; }
    }
    if (cur.trim()) parts.push(cur.trim());
    return parts;
  }

  function parseNode(item) {
    item = item.trim();
    if (item.endsWith(')') && item.includes('(')) {
      const idx = item.indexOf('(');
      const name = item.slice(0, idx).trim();
      const inner = item.slice(idx + 1, -1);
      const children = {};
      for (const childItem of splitTop(inner, ',')) {
        const [cname, cval] = parseNode(childItem);
        children[cname] = cval;
      }
      return [name, children];
    }
    return [item, {}];
  }

  // Supprime les accents/diacritiques pour comparer "OUEME" (tel que stocké,
  // sans accent, dans l'onglet Localisation) avec "Ouémé" (tel que saisi,
  // avec accents, dans la colonne Zone des accords).
  function stripAccents(s) {
    return String(s).normalize('NFD').replace(/[\u0300-\u036f]/g, '');
  }
  function normName(s) {
    return stripAccents(String(s).trim()).toUpperCase();
  }

  function decodeLocalisation(s) {
    if (!s || !String(s).trim()) return {};
    // Beaucoup de valeurs se terminent par un point final ("...Sakété)."),
    // qui casse sinon le parsing du dernier département/commune de la liste
    // (identique au comportement de decode_localisation côté Python).
    const cleaned = String(s).trim().replace(/\.+\s*$/, '').trim();
    const result = {};
    for (const depItem of splitTop(cleaned, ';')) {
      const [name, val] = parseNode(depItem);
      result[name] = val;
    }
    return result;
  }

  function zoneInterventionMatches(zoneStr, filterNames) {
    if (!zoneStr || !String(zoneStr).trim()) return false;
    if (!filterNames || filterNames.length === 0) return true;
    const filterSetUpper = new Set(filterNames.map((f) => normName(f)));
    const tree = decodeLocalisation(zoneStr);
    const names = new Set();
    const walk = (node) => {
      for (const name of Object.keys(node)) {
        names.add(normName(name));
        if (node[name] && Object.keys(node[name]).length) walk(node[name]);
      }
    };
    walk(tree);
    for (const n of names) if (filterSetUpper.has(n)) return true;
    return false;
  }

  // ── Normalisation : transforme dep>com>arr>[villages] en arbre 100% imbriqué
  //    (villages -> {}), pour que le rendu récursif soit identique à tous les niveaux.

  function normalizeHierarchy(raw) {
    const out = {};
    for (const dep of Object.keys(raw)) {
      out[dep] = {};
      for (const com of Object.keys(raw[dep])) {
        out[dep][com] = {};
        for (const arr of Object.keys(raw[dep][com])) {
          const villages = raw[dep][com][arr] || [];
          out[dep][com][arr] = {};
          for (const v of villages) out[dep][com][arr][v] = {};
        }
      }
    }
    return out;
  }

  // ── CSS (une seule injection) ─────────────────────────────────────────

  function injectStyles() {
    if (document.getElementById('loc-selector-v2-styles')) return;
    const style = document.createElement('style');
    style.id = 'loc-selector-v2-styles';
    style.textContent = `
      .loc-sel2 { --loc-accent:#2b6cb0; --loc-border:#d8dee5; --loc-chip-bg:#f8fafc;
        --loc-chip-checked:#e8f1fc; font-family: inherit; color:#1f2937; }
      .loc-sel2-toolbar { display:flex; gap:6px; margin-bottom:8px; align-items:center; flex-wrap:wrap; }
      .loc-sel2-search { flex:1; min-width:150px; padding:6px 10px; border:1px solid var(--loc-border);
        border-radius:6px; font-size:12px; outline:none; }
      .loc-sel2-search:focus { border-color:var(--loc-accent); }
      .loc-sel2-btn { border:1px solid var(--loc-border); background:#fff; color:#374151;
        padding:5px 10px; border-radius:6px; font-size:11px; cursor:pointer; white-space:nowrap; }
      .loc-sel2-btn:hover { background:#f3f4f6; }
      .loc-sel2-btn.active { background:var(--loc-accent); color:#fff; border-color:var(--loc-accent); }
      .loc-sel2-summary { display:flex; align-items:flex-start; justify-content:space-between;
        gap:8px; margin-bottom:10px; }
      .loc-sel2-summary-text { font-size:12.5px; color:#6b7280; flex:1; min-width:0;
        word-break:break-word; line-height:1.4; }
      .loc-sel2-reset { border:1px solid var(--loc-border); background:#fff; color:#374151;
        padding:5px 10px; border-radius:6px; font-size:12.5px; cursor:pointer; flex-shrink:0; }
      .loc-sel2-reset:hover { background:#f3f4f6; }
      .loc-tree-level { display:flex; flex-wrap:wrap; gap:6px; align-items:flex-start; }
      .loc-tree-level.loc-level-nested { margin-top:6px; padding-left:14px;
        border-left:2px solid var(--loc-border); }
      .loc-chip { border:1px solid var(--loc-border); background:var(--loc-chip-bg);
        border-radius:7px; }
      .loc-chip.checked { background:var(--loc-chip-checked); border-color:var(--loc-accent); }
      .loc-chip.loc-highlight { background:#fef3c7; border-color:#f59e0b; }
      .loc-chip-row { display:flex; align-items:center; gap:5px; padding:5px 9px;
        cursor:pointer; font-size:12.6px; white-space:nowrap; user-select:none; }
      .loc-chip-row input[type="checkbox"] { cursor:pointer; flex-shrink:0; margin:0; }
      .loc-chevron { border:none; background:none; cursor:pointer; font-size:10px;
        color:#6b7280; padding:0 2px; line-height:1; flex-shrink:0; }
      .loc-chevron:hover { color:var(--loc-accent); }
      .loc-chevron-spacer { width:12px; flex-shrink:0; display:inline-block; }
      .loc-panel { flex-basis:100%; width:100%; }
      .loc-tree-empty { font-size:12px; color:#9ca3af; font-style:italic; padding:4px 2px; }
      .loc-sel2-hint { font-size:11.5px; color:#9ca3af; margin-top:8px; }
      .loc-sel2-count { font-size:10px; color:#6b7280; }
    `;
    document.head.appendChild(style);
  }

  // ── Classe principale ─────────────────────────────────────────────────

  class LocalisationSelector {
    constructor(container, options = {}) {
      this.root = typeof container === 'string' ? document.querySelector(container) : container;
      if (!this.root) throw new Error('LocalisationSelector: conteneur introuvable');
      this.apiBase = options.apiBase || '';
      this.onChange = options.onChange || null;
      this.hierarchy = {};
      this.tree = {};
      this.expandedSet = new Set();
      this.searchTerm = '';
    }

    async init() {
      injectStyles();
      this._renderSkeleton();
      await this._loadHierarchy();
      // Start collapsed — user clicks ▸ to expand each level
      this._renderAll();
    }

    async _loadHierarchy() {
      const res = await fetch(`${this.apiBase}/api/localisation/hierarchie`);
      if (!res.ok) throw new Error('Impossible de charger la hiérarchie de localisation');
      const raw = await res.json();
      this.hierarchy = normalizeHierarchy(raw);
    }

    _renderSkeleton() {
      this.root.classList.add('loc-sel2');
      this.root.innerHTML = `
        <div class="loc-sel2-toolbar">
          <input type="text" class="loc-sel2-search" data-role="search" placeholder="🔍 Rechercher département, commune, village…">
          <button type="button" class="loc-sel2-btn" data-role="expand-all">Tout déplier</button>
          <button type="button" class="loc-sel2-btn" data-role="collapse-all">Tout replier</button>
          <span class="loc-sel2-count" data-role="count"></span>
        </div>
        <div class="loc-sel2-summary">
          <div class="loc-sel2-summary-text" data-role="summary">Chargement…</div>
          <button type="button" class="loc-sel2-reset" data-role="reset">Réinitialiser</button>
        </div>
        <div class="loc-tree-level" data-role="root-level" style="max-height:350px; overflow-y:auto;"></div>
        <div class="loc-sel2-hint">Cliquez sur ▸ pour déplier. Cocher un niveau = toute la zone incluse.</div>
      `;
      this.root.querySelector('[data-role="reset"]').addEventListener('click', () => this.reset());
      this.root.querySelector('[data-role="expand-all"]').addEventListener('click', () => this._expandAll());
      this.root.querySelector('[data-role="collapse-all"]').addEventListener('click', () => this._collapseAll());
      this.root.querySelector('[data-role="search"]').addEventListener('input', (e) => {
        this.searchTerm = e.target.value.trim().toLowerCase();
        if (this.searchTerm.length >= 2) this._autoExpandMatching();
        this._renderAll();
      });
    }

    _collectAllPaths(node, path) {
      const paths = [];
      for (const name of Object.keys(node)) {
        const p = [...path, name];
        if (Object.keys(node[name]).length > 0) {
          paths.push(p.join('>>'));
          paths.push(...this._collectAllPaths(node[name], p));
        }
      }
      return paths;
    }

    _expandAll() {
      this.expandedSet = new Set(this._collectAllPaths(this.hierarchy, []));
      this._renderAll();
    }

    _collapseAll() {
      this.expandedSet = new Set();
      this._renderAll();
    }

    _autoExpandMatching() {
      const term = this.searchTerm;
      const toExpand = new Set();
      const walk = (node, path) => {
        for (const name of Object.keys(node)) {
          const p = [...path, name];
          if (normName(name).includes(normName(term))) {
            // expand all ancestors
            for (let i = 1; i <= p.length - 1; i++) toExpand.add(p.slice(0, i).join('>>'));
          }
          if (Object.keys(node[name]).length > 0) walk(node[name], p);
        }
      };
      walk(this.hierarchy, []);
      this.expandedSet = toExpand;
    }

    // ── Sélection : navigation par chemin exact (dep, com, arr, village) ──

    _isPathSelected(path) {
      let node = this.tree;
      for (let i = 0; i < path.length; i++) {
        if (!Object.prototype.hasOwnProperty.call(node, path[i])) return false;
        if (i === path.length - 1) return true;
        node = node[path[i]];
      }
      return true;
    }

    _toggleSelection(path) {
      if (this._isPathSelected(path)) {
        let node = this.tree;
        for (let i = 0; i < path.length - 1; i++) node = node[path[i]];
        delete node[path[path.length - 1]];
      } else {
        let node = this.tree;
        for (let i = 0; i < path.length - 1; i++) {
          if (!Object.prototype.hasOwnProperty.call(node, path[i])) node[path[i]] = {};
          node = node[path[i]];
        }
        node[path[path.length - 1]] = {};
      }
      this._renderAll();
      if (this.onChange) this.onChange(this.getEncodedString());
    }

    _toggleExpand(key) {
      if (this.expandedSet.has(key)) this.expandedSet.delete(key);
      else this.expandedSet.add(key);
      this._renderAll();
    }

    // ── Rendu récursif : identique à chaque niveau ─────────────────────────

    _renderAll() {
      const rootLevel = this.root.querySelector('[data-role="root-level"]');
      rootLevel.className = 'loc-tree-level';
      this._renderLevel(this.hierarchy, [], rootLevel);
      this._renderSummary();
    }

    _renderLevel(hierNode, path, container) {
      container.innerHTML = '';
      let names = Object.keys(hierNode).sort();
      // Filter by search term if active
      if (this.searchTerm.length >= 2) {
        const term = normName(this.searchTerm);
        names = names.filter(name => {
          if (normName(name).includes(term)) return true;
          // Keep if any descendant matches
          return this._hasDescendantMatch(hierNode[name], term);
        });
      }
      if (names.length === 0) {
        container.innerHTML = '<span class="loc-tree-empty">Aucun élément</span>';
        return;
      }
      for (const name of names) {
        const path2 = [...path, name];
        const key = path2.join('>>');
        const childNode = hierNode[name];
        const hasChildren = Object.keys(childNode).length > 0;
        const checked = this._isPathSelected(path2);
        const expanded = this.expandedSet.has(key);

        const chip = document.createElement('div');
        const isMatch = this.searchTerm.length >= 2 && normName(name).includes(normName(this.searchTerm));
        chip.className = 'loc-chip' + (checked ? ' checked' : '') + (isMatch ? ' loc-highlight' : '');
        chip.innerHTML = `
          <span class="loc-chip-row">
            <input type="checkbox" ${checked ? 'checked' : ''}>
            ${hasChildren
              ? `<button type="button" class="loc-chevron">${expanded ? '▾' : '▸'}</button>`
              : '<span class="loc-chevron-spacer"></span>'}
            <span class="loc-chip-label">${name}</span>
          </span>
        `;
        const checkbox = chip.querySelector('input');
        checkbox.addEventListener('change', () => this._toggleSelection(path2));
        if (hasChildren) {
          const chevronBtn = chip.querySelector('.loc-chevron');
          chevronBtn.addEventListener('click', () => this._toggleExpand(key));
        }
        container.appendChild(chip);

        if (hasChildren && expanded) {
          const panel = document.createElement('div');
          panel.className = 'loc-panel';
          const subLevel = document.createElement('div');
          subLevel.className = 'loc-tree-level loc-level-nested';
          panel.appendChild(subLevel);
          container.appendChild(panel);
          this._renderLevel(childNode, path2, subLevel);
        }
      }
    }

    _hasDescendantMatch(node, term) {
      for (const name of Object.keys(node)) {
        if (normName(name).includes(term)) return true;
        if (Object.keys(node[name]).length > 0 && this._hasDescendantMatch(node[name], term)) return true;
      }
      return false;
    }

    _renderSummary() {
      const el = this.root.querySelector('[data-role="summary"]');
      const encoded = this.getEncodedString();
      el.textContent = encoded ? encoded : 'Aucune localisation sélectionnée';
      el.title = encoded;
      // Count total locations in hierarchy
      const countEl = this.root.querySelector('[data-role="count"]');
      if (countEl) {
        const total = Object.keys(this.hierarchy).length;
        const selected = Object.keys(this.tree).length;
        countEl.textContent = `${selected}/${total} dép.`;
      }
    }

    // ── Déplie automatiquement les branches d'un chemin donné ─────────────

    _expandPathsOf(node, path) {
      for (const name of Object.keys(node)) {
        const path2 = [...path, name];
        if (Object.keys(node[name]).length > 0) {
          this.expandedSet.add(path2.join('>>'));
          this._expandPathsOf(node[name], path2);
        }
      }
    }

    // ── API publique ──────────────────────────────────────────────────────

    getEncodedString() {
      return encodeLocalisation(this.tree);
    }

    getSelectionTree() {
      return JSON.parse(JSON.stringify(this.tree));
    }

    getFlatSelectionNames() {
      const names = new Set();
      const walk = (node) => {
        for (const name of Object.keys(node)) {
          names.add(name);
          if (node[name] && Object.keys(node[name]).length) walk(node[name]);
        }
      };
      walk(this.tree);
      return [...names];
    }

    loadEncodedString(str) {
      this.tree = decodeLocalisation(str || '');
      // Déplie automatiquement les branches sélectionnées pour qu'elles soient visibles
      this.expandedSet = new Set();
      this._expandPathsOf(this.tree, []);
      this._renderAll();
    }

    _expandFirstLevel() {
      // Expand all departments (first level) so user sees communes right away
      for (const dep of Object.keys(this.hierarchy)) {
        if (Object.keys(this.hierarchy[dep]).length > 0) {
          this.expandedSet.add(dep);
        }
      }
    }

    reset() {
      this.tree = {};
      this.expandedSet = new Set();
      this._renderAll();
      if (this.onChange) this.onChange('');
    }
  }

  global.LocalisationSelector = LocalisationSelector;
  global.encodeLocalisation = encodeLocalisation;
  global.decodeLocalisation = decodeLocalisation;
  global.zoneInterventionMatches = zoneInterventionMatches;
})(window);
