---
title: "Liked papers"
permalink: /liked/
date: 2026-04-25
modified: 2026-04-25
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

<p id="liked-empty" hidden>
  No papers liked yet. Visit <a href="{{ site.url }}/daily-arxiv/">daily-arxiv</a> and click <strong>★ Like</strong> on anything that catches your eye — they'll show up here, grouped by the week you liked them.
</p>

<div id="liked-toolbar" class="arxiv-toolbar" hidden>
  <span id="liked-count"></span>
  <button type="button" id="liked-export" class="arxiv-save-btn">Export JSON for ML</button>
  <button type="button" id="liked-clear" class="arxiv-save-btn">Clear all</button>
</div>

<details id="liked-export-panel" hidden>
  <summary>JSON</summary>
  <p style="font-size:0.82em; color:#777;">Save as <code>_data/liked_arxiv.json</code> in the repo root. Tomorrow's <code>arxiv_daily.py</code> run will treat these as positive examples (×3 corpus weight).</p>
  <textarea id="liked-export-textarea" rows="12" style="width:100%; font-family:Monaco,Consolas,monospace; font-size:0.82em;"></textarea>
</details>

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

  function formatPaper(p) {
    if (typeof p === 'string') p = { id: p };
    var authors = (p.authors || []).join(', ');
    var html = '';
    html += '<article class="arxiv-item" data-arxiv-id="' + escapeHtml(p.id) + '">';
    html += '  <h3 class="arxiv-item__title"><a href="https://arxiv.org/abs/' + escapeHtml(p.id) + '">' +
      escapeHtml(p.title || ('arXiv:' + p.id)) + '</a></h3>';
    html += '  <p class="arxiv-item__meta">';
    if (authors) html += '<span class="arxiv-item__authors">' + escapeHtml(authors) + '</span> · ';
    if (p.category) html += '<span class="arxiv-item__category">' + escapeHtml(p.category) + '</span> · ';
    html += '<a class="arxiv-item__id" href="https://arxiv.org/abs/' + escapeHtml(p.id) + '">' + escapeHtml(p.id) + '</a>';
    html += '  </p>';
    if (p.abstract) {
      html += '  <details class="arxiv-item__abstract-wrap"><summary>Abstract</summary>';
      html += '    <p class="arxiv-item__abstract">' + escapeHtml(p.abstract) + '</p>';
      html += '  </details>';
    }
    html += '  <p class="arxiv-item__actions">';
    html += '    <a class="arxiv-action-link" href="https://arxiv.org/pdf/' + escapeHtml(p.id) + '.pdf" target="_blank" rel="noopener">PDF</a>';
    html += '    <button type="button" class="arxiv-like-btn is-liked" data-liked-remove="' + escapeHtml(p.id) + '">★ Liked — remove</button>';
    html += '  </p>';
    html += '</article>';
    return html;
  }

  function render() {
    var liked = load();
    var list = document.getElementById('liked-list');
    var empty = document.getElementById('liked-empty');
    var toolbar = document.getElementById('liked-toolbar');
    var count = document.getElementById('liked-count');

    list.innerHTML = '';
    if (!liked.length) {
      empty.hidden = false;
      toolbar.hidden = true;
      return;
    }
    empty.hidden = true;
    toolbar.hidden = false;
    count.textContent = liked.length + ' paper' + (liked.length === 1 ? '' : 's') + ' · ';

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
      var weekEnd = new Date(g.date);
      weekEnd.setDate(weekEnd.getDate() + 6);
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
    if (e.target.id === 'liked-clear') {
      if (confirm('Clear all liked papers from this browser?')) { store([]); render(); }
      return;
    }
    if (e.target.id === 'liked-export') {
      var panel = document.getElementById('liked-export-panel');
      var ta = document.getElementById('liked-export-textarea');
      ta.value = JSON.stringify(load(), null, 2);
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
