---
title: "Liked papers"
permalink: /liked/
date: 2026-04-25
modified: 2026-04-26
excerpt: Papers you've liked from the daily-arxiv feed, grouped by the week you liked them.
author_profile: false
sitemap: false
---

<p class="yg-locked-only" style="margin-top:2em; color:#777;">
  This page is private. If it's you, visit any page with <code>?me=1</code> in the URL once on this browser to unlock.
</p>

<div class="yg-private">

<p class="arxiv-toolbar">
  <a href="{{ site.url }}/daily-arxiv/">← Back to daily-arxiv</a>
</p>

<div id="liked-pending-banner" class="arxiv-toolbar" hidden style="background:#fff5d6; border:1px solid #e5c07b; padding:0.6em 0.9em; border-radius:4px; color:#5a4310;">
  <strong>⚠ <span id="liked-pending-count"></span> liked paper(s) live only in this browser.</strong>
  Click <em>Export JSON for ML</em>, paste the result into <code>_data/liked_arxiv.json</code>, and commit it so they survive a localStorage clear (Safari ITP, switching browsers/devices, etc.).
</div>

<p id="liked-empty" hidden>
  No papers liked yet. Visit <a href="{{ site.url }}/daily-arxiv/">daily-arxiv</a> and click <strong>★ Like</strong> on anything that catches your eye — they'll show up here, grouped by the week you liked them.
</p>

<div id="liked-toolbar" class="arxiv-toolbar" hidden>
  <span id="liked-count"></span>
  <button type="button" id="liked-export" class="arxiv-save-btn">Export JSON for ML</button>
  <button type="button" id="liked-clear" class="arxiv-save-btn">Clear pending</button>
</div>

<details id="liked-export-panel" hidden>
  <summary>JSON</summary>
  <p style="font-size:0.82em; color:#777;">Save as <code>_data/liked_arxiv.json</code> in the repo root and commit. <code>arxiv_daily.py</code> will treat these as positive examples (×3 corpus weight); the cards below will then be permanently visible (no longer dependent on this browser's localStorage).</p>
  <textarea id="liked-export-textarea" rows="12" style="width:100%; font-family:Monaco,Consolas,monospace; font-size:0.82em;"></textarea>
</details>

<script type="application/json" id="liked-server-data">{{ site.data.liked_arxiv | jsonify }}</script>

<div id="liked-list"></div>

</div><!-- /.yg-private -->

<script>
(function () {
  var KEY = 'yg-arxiv-liked';
  var LEGACY = 'yg-arxiv-saved';

  function migrate() {
    if (localStorage.getItem(KEY)) return;
    var legacy = localStorage.getItem(LEGACY);
    if (legacy) localStorage.setItem(KEY, legacy);
  }

  function load() { try { return JSON.parse(localStorage.getItem(KEY) || '[]'); } catch (e) { return []; } }
  function store(v) { localStorage.setItem(KEY, JSON.stringify(v)); }

  function loadServer() {
    var el = document.getElementById('liked-server-data');
    if (!el) return [];
    try {
      var v = JSON.parse(el.textContent || 'null');
      return Array.isArray(v) ? v : [];
    } catch (e) { return []; }
  }

  function escapeHtml(s) {
    return String(s == null ? '' : s).replace(/[&<>"]/g, function (c) {
      return {'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c];
    });
  }

  function weekStart(dateStr) {
    var d = new Date(dateStr);
    if (isNaN(d.getTime())) d = new Date();
    var day = d.getDay();
    var diff = (day === 0 ? -6 : 1 - day);  // back to Monday
    d.setDate(d.getDate() + diff);
    d.setHours(0, 0, 0, 0);
    return d;
  }

  function fmtDate(d) {
    return d.toLocaleDateString(undefined, { year: 'numeric', month: 'short', day: 'numeric' });
  }

  function shallowCopy(o) {
    var c = {};
    for (var k in o) if (Object.prototype.hasOwnProperty.call(o, k)) c[k] = o[k];
    return c;
  }

  // Merge server (canonical) + localStorage (pending) by id; server wins on metadata.
  function mergedAll() {
    var byId = {};
    loadServer().forEach(function (p) {
      if (typeof p === 'string') p = { id: p };
      if (!p || !p.id) return;
      var c = shallowCopy(p);
      c._source = 'saved';
      byId[c.id] = c;
    });
    load().forEach(function (p) {
      if (typeof p === 'string') p = { id: p };
      if (!p || !p.id) return;
      if (!byId[p.id]) {
        var c = shallowCopy(p);
        c._source = 'pending';
        byId[c.id] = c;
      }
    });
    var out = [];
    for (var id in byId) if (Object.prototype.hasOwnProperty.call(byId, id)) out.push(byId[id]);
    return out;
  }

  // Strip _source before exporting.
  function exportable() {
    return mergedAll().map(function (p) {
      var c = {};
      for (var k in p) if (k !== '_source' && Object.prototype.hasOwnProperty.call(p, k)) c[k] = p[k];
      return c;
    });
  }

  function formatPaper(p) {
    if (typeof p === 'string') p = { id: p };
    var authors = (p.authors || []).join(', ');
    var pending = p._source === 'pending';
    var html = '';
    html += '<article class="arxiv-item" data-arxiv-id="' + escapeHtml(p.id) + '" data-source="' + escapeHtml(p._source || 'saved') + '">';
    html += '  <h3 class="arxiv-item__title"><a href="https://arxiv.org/abs/' + escapeHtml(p.id) + '">' +
      escapeHtml(p.title || ('arXiv:' + p.id)) + '</a></h3>';
    html += '  <p class="arxiv-item__meta">';
    if (authors) html += '<span class="arxiv-item__authors">' + escapeHtml(authors) + '</span> · ';
    if (p.category) html += '<span class="arxiv-item__category">' + escapeHtml(p.category) + '</span> · ';
    html += '<a class="arxiv-item__id" href="https://arxiv.org/abs/' + escapeHtml(p.id) + '">' + escapeHtml(p.id) + '</a>';
    if (pending) {
      html += ' · <span class="arxiv-item__source" style="color:#b5841d;" title="Only in this browser — not yet saved to _data/liked_arxiv.json">● pending</span>';
    } else {
      html += ' · <span class="arxiv-item__source" style="color:#5a8e3a;" title="Saved in _data/liked_arxiv.json">✓ saved</span>';
    }
    html += '  </p>';
    if (p.abstract) {
      html += '  <details class="arxiv-item__abstract-wrap"><summary>Abstract</summary>';
      html += '    <p class="arxiv-item__abstract">' + escapeHtml(p.abstract) + '</p>';
      html += '  </details>';
    }
    html += '  <p class="arxiv-item__actions">';
    html += '    <a class="arxiv-action-link" href="https://arxiv.org/pdf/' + escapeHtml(p.id) + '.pdf" target="_blank" rel="noopener">PDF</a>';
    if (pending) {
      html += '    <button type="button" class="arxiv-like-btn is-liked" data-liked-remove="' + escapeHtml(p.id) + '">★ Liked — remove</button>';
    } else {
      html += '    <button type="button" class="arxiv-like-btn is-liked" data-liked-saved="1" title="Edit _data/liked_arxiv.json to remove">★ Liked — saved</button>';
    }
    html += '  </p>';
    html += '</article>';
    return html;
  }

  function render() {
    var liked = mergedAll();
    var pending = 0;
    liked.forEach(function (p) { if (p._source === 'pending') pending++; });
    var list = document.getElementById('liked-list');
    var empty = document.getElementById('liked-empty');
    var toolbar = document.getElementById('liked-toolbar');
    var count = document.getElementById('liked-count');
    var banner = document.getElementById('liked-pending-banner');
    var pendingCt = document.getElementById('liked-pending-count');

    list.innerHTML = '';
    if (!liked.length) {
      empty.hidden = false;
      toolbar.hidden = true;
      banner.hidden = true;
      return;
    }
    empty.hidden = true;
    toolbar.hidden = false;
    count.textContent = liked.length + ' paper' + (liked.length === 1 ? '' : 's') +
      (pending ? ' (' + pending + ' pending)' : '') + ' · ';

    if (pending) {
      banner.hidden = false;
      pendingCt.textContent = pending;
    } else {
      banner.hidden = true;
    }

    // Group by ISO week-start
    var groups = {};
    liked.forEach(function (p) {
      var when = (typeof p === 'object' && p.saved_at) ? p.saved_at : new Date(0).toISOString();
      var ws = weekStart(when);
      var key = ws.toISOString().slice(0, 10);
      if (!groups[key]) groups[key] = { date: ws, papers: [] };
      groups[key].papers.push(p);
    });

    // Newest week first
    Object.keys(groups).sort().reverse().forEach(function (k) {
      var g = groups[k];
      var section = document.createElement('section');
      section.className = 'liked-week';
      var header = '<h2 class="liked-week__title">Week of ' + fmtDate(g.date) +
        ' <small>(' + g.papers.length + ' paper' + (g.papers.length === 1 ? '' : 's') + ')</small></h2>';
      section.innerHTML = header + g.papers
        .slice()
        .sort(function (a, b) {
          return (b.saved_at || '').localeCompare(a.saved_at || '');
        })
        .map(formatPaper)
        .join('');
      list.appendChild(section);
    });
  }

  document.addEventListener('click', function (e) {
    var rm = e.target.closest('[data-liked-remove]');
    if (rm) {
      var id = rm.getAttribute('data-liked-remove');
      var liked = load().filter(function (p) {
        return (typeof p === 'string' ? p : p.id) !== id;
      });
      store(liked);
      render();
      return;
    }
    var saved = e.target.closest('[data-liked-saved]');
    if (saved) {
      alert('This paper is committed in _data/liked_arxiv.json. To remove it, edit that file and re-commit.');
      return;
    }
    if (e.target.id === 'liked-clear') {
      if (confirm('Clear all pending (uncommitted) likes from this browser? Saved entries are not affected.')) {
        store([]);
        render();
      }
      return;
    }
    if (e.target.id === 'liked-export') {
      var panel = document.getElementById('liked-export-panel');
      var ta = document.getElementById('liked-export-textarea');
      ta.value = JSON.stringify(exportable(), null, 2);
      panel.open = true;
      panel.hidden = false;
      ta.focus();
      ta.select();
    }
  });

  migrate();
  render();
})();
</script>
