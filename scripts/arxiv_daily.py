#!/usr/bin/env python3
"""
Daily arXiv feed — ranked against your INSPIRE corpus, your top
collaborators, and any papers you've liked.

Pipeline
--------
1. Fetch your papers from INSPIRE-HEP.
2. Pick your top-N most frequent collaborators, fetch their recent papers.
3. If `_data/liked_arxiv.json` exists, load liked papers and add them to
   the corpus with extra weight (positive-signal feedback from the user).
4. Query arXiv for recent submissions in astro-ph.HE, gr-qc, nucl-th.
5. Rank candidates with TF-IDF + cosine similarity (sklearn) or fall back
   to a log-weighted vocabulary profile if sklearn is unavailable.
6. Write the top-N to _pages/daily-arxiv.md, with collapsible Benty-Fields-
   style cards. The liked-papers shelf lives on its own page (/liked/),
   so this page stays clean.

Optional but recommended:
    python3 -m pip install --user scikit-learn
"""

import html
import json
import math
import re
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from collections import Counter
from datetime import datetime, timedelta, timezone
from pathlib import Path

# -------- Config ------------------------------------------------------------
INSPIRE_AUTHOR = "Yong.Gao.1"
ARXIV_CATS = ["astro-ph.HE", "gr-qc", "nucl-th"]
DAYS_BACK = 7
MAX_RESULTS_PER_QUERY = 500
TOP_N = 50

TOP_COLLABORATORS = 10
PAPERS_PER_COLLAB = 30
LIKED_WEIGHT = 3            # how many corpus copies each liked paper contributes

ROOT = Path(__file__).resolve().parent.parent
LIKED_FILE = ROOT / "_data" / "liked_arxiv.json"
LEGACY_SAVED_FILE = ROOT / "_data" / "saved_arxiv.json"   # one-time migration source
OUT_FILE = ROOT / "_pages" / "daily-arxiv.md"

STOPWORDS = {
    "the","a","an","of","in","to","and","or","for","on","at","by","with","are",
    "is","was","were","be","been","being","have","has","had","will","would",
    "we","our","us","this","that","these","those","which","where","when","they",
    "from","as","it","its","can","may","also","than","then","such","not","no",
    "but","if","so","do","does","only","other","one","two","three","their",
    "show","find","present","paper","results","model","models","method","methods",
    "use","used","using","study","studied","studies","here","however","approach",
    "demonstrate","new","recently","both","between","within","via","each","over",
    "while","shown","more","most","some","any","all","non","thus","into","out",
    "without","through","after","before","different","same","well","found","based",
}
# -----------------------------------------------------------------------------

try:
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.metrics.pairwise import cosine_similarity
    import numpy as np
    HAS_SKLEARN = True
except ImportError:
    HAS_SKLEARN = False


def _http_json(url):
    req = urllib.request.Request(url, headers={"Accept": "application/json"})
    return json.loads(urllib.request.urlopen(req, timeout=60).read())


def _paper_text(meta):
    t = (meta.get("titles") or [{}])[0].get("title", "") or ""
    a = ""
    if meta.get("abstracts"):
        a = meta["abstracts"][0].get("value", "") or ""
    return (t.strip() + " " + a.strip()).strip()


def _arxiv_id_of(meta):
    eps = meta.get("arxiv_eprints") or []
    if eps:
        v = (eps[0].get("value") or "").strip()
        return re.sub(r"v\d+$", "", v) if v else None
    return None


def fetch_author_papers(bai, size=200):
    url = (
        "https://inspirehep.net/api/literature?"
        f"size={size}&sort=mostrecent&q=a%20{bai}"
        "&fields=titles,abstracts,authors,arxiv_eprints"
    )
    return _http_json(url)["hits"]["hits"]


def pick_top_collaborators(yong_hits, top_n):
    counter = Counter()
    for h in yong_hits:
        for a in h["metadata"].get("authors", []):
            ids = a.get("ids") or []
            bai = next((x["value"] for x in ids if x.get("schema") == "INSPIRE BAI"), None)
            if bai and bai != INSPIRE_AUTHOR:
                counter[bai] += 1
    return [bai for bai, _ in counter.most_common(top_n)]


def load_liked_papers():
    if LIKED_FILE.exists():
        try:
            return json.loads(LIKED_FILE.read_text())
        except Exception as e:
            print(f"  ! could not parse {LIKED_FILE}: {e}")
            return []
    if LEGACY_SAVED_FILE.exists():
        try:
            return json.loads(LEGACY_SAVED_FILE.read_text())
        except Exception:
            pass
    return []


def build_corpus():
    print(f"  + your papers (bai={INSPIRE_AUTHOR})")
    yong_hits = fetch_author_papers(INSPIRE_AUTHOR)
    print(f"    {len(yong_hits)} papers")

    collabs = pick_top_collaborators(yong_hits, TOP_COLLABORATORS)
    print(f"  + top collaborators: {', '.join(collabs)}")

    seen = {}
    for h in yong_hits:
        txt = _paper_text(h["metadata"])
        if not txt:
            continue
        aid = _arxiv_id_of(h["metadata"])
        seen[aid or txt[:80]] = (txt, 1, "yong")

    for bai in collabs:
        try:
            hits = fetch_author_papers(bai, size=PAPERS_PER_COLLAB)
        except Exception as e:
            print(f"    ! failed to fetch {bai}: {e}")
            continue
        added = 0
        for h in hits:
            txt = _paper_text(h["metadata"])
            if not txt:
                continue
            aid = _arxiv_id_of(h["metadata"])
            key = aid or txt[:80]
            if key in seen:
                continue
            seen[key] = (txt, 1, bai)
            added += 1
        print(f"    {bai}: +{added} new papers")

    liked = load_liked_papers()
    if liked:
        for s in liked:
            aid = s.get("id") or "liked-" + (s.get("title") or "")[:40]
            text = ((s.get("title") or "") + " " + (s.get("abstract") or "")).strip()
            if not text:
                continue
            seen[aid] = (text, LIKED_WEIGHT, "liked")
        print(f"  + liked papers (×{LIKED_WEIGHT} weight): {len(liked)}")
    else:
        print(f"  + liked papers: 0  (export from /liked/ once you've liked some)")

    return [v for v in seen.values()]


def tokenize(text):
    text = re.sub(r"<[^>]+>", " ", text or "").lower()
    toks = re.findall(r"[a-z][a-z\-]{2,}", text)
    return [t for t in toks if t not in STOPWORDS]


def fetch_arxiv_recent(cats, days_back, max_results):
    q = " OR ".join(f"cat:{c}" for c in cats)
    url = (
        "http://export.arxiv.org/api/query?"
        f"search_query={urllib.parse.quote(q)}"
        f"&sortBy=submittedDate&sortOrder=descending&max_results={max_results}"
    )
    xml_bytes = urllib.request.urlopen(url, timeout=60).read()
    tree = ET.fromstring(xml_bytes)
    ns = {"a": "http://www.w3.org/2005/Atom"}
    cutoff = datetime.now(timezone.utc) - timedelta(days=days_back)

    papers = []
    for e in tree.findall("a:entry", ns):
        pub = datetime.fromisoformat(
            e.find("a:published", ns).text.replace("Z", "+00:00")
        )
        if pub < cutoff:
            break
        arxiv_id = e.find("a:id", ns).text.rsplit("/", 1)[-1]
        arxiv_id = re.sub(r"v\d+$", "", arxiv_id)
        title = re.sub(r"\s+", " ", (e.find("a:title", ns).text or "")).strip()
        summary = re.sub(r"\s+", " ", (e.find("a:summary", ns).text or "")).strip()
        authors = [a.find("a:name", ns).text for a in e.findall("a:author", ns)]
        cats_elem = [c.get("term") for c in e.findall("a:category", ns)]
        primary = cats_elem[0] if cats_elem else ""
        papers.append({
            "id": arxiv_id,
            "title": title,
            "summary": summary,
            "authors": authors,
            "published": pub,
            "primary_category": primary,
        })
    return papers


def score_tfidf(candidates, corpus_with_weights):
    corpus_texts = []
    for txt, weight, _ in corpus_with_weights:
        corpus_texts.extend([txt] * max(1, int(weight)))
    cand_texts = [f"{p['title']} {p['summary']}" for p in candidates]

    vec = TfidfVectorizer(
        stop_words=list(STOPWORDS),
        token_pattern=r"(?u)\b[a-z][a-z\-]{2,}\b",
        ngram_range=(1, 2),
        max_df=0.95,
        min_df=1,
    )
    X = vec.fit_transform([t.lower() for t in corpus_texts + cand_texts])
    nC = len(corpus_texts)
    sim = cosine_similarity(X[nC:], X[:nC])
    max_sim = sim.max(axis=1)
    mean_top5 = np.sort(sim, axis=1)[:, -5:].mean(axis=1)
    return 0.7 * max_sim + 0.3 * mean_top5


def score_profile(candidates, corpus_with_weights):
    profile = Counter()
    for txt, weight, _ in corpus_with_weights:
        toks = tokenize(txt)
        for t in toks:
            profile[t] += int(weight)
    out = []
    for p in candidates:
        toks = tokenize(f"{p['title']} {p['summary']}")
        if not toks:
            out.append(0.0); continue
        s = sum(math.log(1 + profile[t]) for t in toks if profile[t])
        out.append(s / math.sqrt(len(toks)))
    return out


def render_page(papers, scores, top_n, n_candidates, n_corpus, n_liked):
    now = datetime.now(timezone.utc)
    scored = sorted(zip(scores, papers), key=lambda t: t[0], reverse=True)[:top_n]
    liked_ids = {s.get("id") for s in load_liked_papers() if s.get("id")}

    head = [
        "---",
        'title: "daily-arxiv"',
        f"date: {now.strftime('%Y-%m-%d')}",
        "permalink: /daily-arxiv/",
        f"modified: {now.strftime('%Y-%m-%d')}",
        "excerpt: Daily arXiv feed ranked against my own work, my collaborators', and the papers I've liked.",
        "author_profile: false",
        "mathjax: true",
        "---",
        "",
        '<p class="arxiv-toolbar yg-private"><a href="{{ site.url }}/liked/">★ Liked papers →</a></p>',
        "",
    ]

    body = []
    for score, p in scored:
        s = float(score)
        authors = ", ".join(p["authors"][:6]) + (", et al." if len(p["authors"]) > 6 else "")
        abstract = p["summary"]
        payload = json.dumps({
            "id": p["id"],
            "title": p["title"],
            "authors": p["authors"][:6] + (["et al."] if len(p["authors"]) > 6 else []),
            "abstract": abstract,
            "category": p["primary_category"],
        }, ensure_ascii=False)
        payload_attr = html.escape(payload, quote=True)
        is_saved = p["id"] in liked_ids
        btn_class = "arxiv-like-btn yg-private is-liked" if is_saved else "arxiv-like-btn yg-private"
        btn_attrs = f'data-arxiv-id="{p["id"]}" data-payload="{payload_attr}"'
        if is_saved:
            btn_attrs += ' data-server-liked="1"'
        btn_text = "★ Liked" if is_saved else "★ Like"
        body.extend([
            f'<article class="arxiv-item" data-arxiv-id="{p["id"]}">',
            f'  <h3 class="arxiv-item__title"><a href="https://arxiv.org/abs/{p["id"]}">{html.escape(p["title"])}</a></h3>',
            '  <p class="arxiv-item__meta">',
            f'    <span class="arxiv-item__authors">{html.escape(authors)}</span>',
            f'    · <span class="arxiv-item__category">{p["primary_category"]}</span>',
            f'    · <a class="arxiv-item__id" href="https://arxiv.org/abs/{p["id"]}">{p["id"]}</a>',
            f'    · <span class="arxiv-item__score">relevance {s:.2f}</span>',
            "  </p>",
            f'  <details class="arxiv-item__abstract-wrap"><summary>Abstract</summary>',
            f'    <p class="arxiv-item__abstract">{html.escape(abstract)}</p>',
            f'  </details>',
            '  <p class="arxiv-item__actions">',
            f'    <a class="arxiv-action-link" href="https://arxiv.org/pdf/{p["id"]}.pdf" target="_blank" rel="noopener">PDF</a>',
            f'    <button type="button" class="{btn_class}" {btn_attrs}>{btn_text}</button>',
            "  </p>",
            "</article>",
            "",
        ])

    foot = [
        "",
        '<p class="arxiv-rebuild-meta">',
        f"Rebuilt {now.strftime('%Y-%m-%d %H:%M UTC')} · "
        f"{n_candidates} candidates over the past {DAYS_BACK} days · "
        f"corpus: {n_corpus} papers (you + top {TOP_COLLABORATORS} collaborators"
        + (f" + {n_liked} liked" if n_liked else "")
        + f") · ranker: {'TF-IDF (scikit-learn)' if HAS_SKLEARN else 'vocabulary profile (stdlib)'}",
        "</p>",
        "",
    ]

    script = r"""<script>
(function () {
  var KEY = 'yg-arxiv-liked';
  var LEGACY = 'yg-arxiv-saved';

  // One-time migration: copy yg-arxiv-saved → yg-arxiv-liked if needed.
  function migrate() {
    if (localStorage.getItem(KEY)) return;
    var legacy = localStorage.getItem(LEGACY);
    if (legacy) {
      localStorage.setItem(KEY, legacy);
      // Keep legacy intact for safety; user can manually clear if they want.
    }
  }

  function load() { try { return JSON.parse(localStorage.getItem(KEY) || '[]'); } catch (e) { return []; } }
  function store(v) { localStorage.setItem(KEY, JSON.stringify(v)); }

  function refresh() {
    var likedIds = load().map(function (x) { return typeof x === 'string' ? x : x.id; });
    document.querySelectorAll('.arxiv-like-btn[data-arxiv-id]').forEach(function (btn) {
      var inLocal = likedIds.indexOf(btn.dataset.arxivId) !== -1;
      var inServer = btn.dataset.serverLiked === '1';
      var on = inLocal || inServer;
      btn.classList.toggle('is-liked', on);
      btn.textContent = on ? '★ Liked' : '★ Like';
    });
  }

  document.addEventListener('click', function (e) {
    var btn = e.target.closest('.arxiv-like-btn[data-arxiv-id]');
    if (!btn) return;
    // Server-committed papers can't be unliked from the browser.
    if (btn.dataset.serverLiked === '1') return;
    var id = btn.dataset.arxivId;
    var liked = load();
    var idx = liked.findIndex(function (x) { return (typeof x === 'string' ? x : x.id) === id; });
    if (idx === -1) {
      var payload = btn.dataset.payload ? JSON.parse(btn.dataset.payload) : { id: id };
      payload.saved_at = new Date().toISOString();
      liked.push(payload);
    } else {
      liked.splice(idx, 1);
    }
    store(liked);
    refresh();
  });

  migrate();
  refresh();
})();
</script>
"""
    return "\n".join(head + body + foot) + script


def main():
    print("Building corpus from INSPIRE…")
    corpus = build_corpus()
    n_corpus_papers = len(corpus)
    n_liked = sum(1 for _, _, src in corpus if src == "liked")
    print(f"  total: {n_corpus_papers} unique papers")

    print(f"Querying arXiv (cats={ARXIV_CATS}, past {DAYS_BACK}d)…")
    papers = fetch_arxiv_recent(ARXIV_CATS, DAYS_BACK, MAX_RESULTS_PER_QUERY)
    print(f"  {len(papers)} candidates retrieved")

    print(f"Scoring with {'TF-IDF' if HAS_SKLEARN else 'profile'}…")
    if HAS_SKLEARN:
        scores = score_tfidf(papers, corpus)
    else:
        scores = score_profile(papers, corpus)

    page = render_page(papers, scores, TOP_N, len(papers), n_corpus_papers, n_liked)
    OUT_FILE.write_text(page)
    print(f"Wrote {OUT_FILE}")


if __name__ == "__main__":
    main()
