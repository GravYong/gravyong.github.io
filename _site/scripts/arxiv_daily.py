#!/usr/bin/env python3
"""
Daily arXiv feed — ranked against your INSPIRE corpus, your top
collaborators, a few extra physicists, and any papers you've liked.

Pipeline
--------
1. Fetch your papers from INSPIRE-HEP.
2. Pick your top-N most frequent collaborators, plus a hand-picked list
   of extra physicists (resolved name → BAI), and fetch their recent papers.
3. If `_data/liked_arxiv.json` exists, load liked papers and add them to
   the corpus with extra weight.
4. Query arXiv for recent submissions in the configured categories,
   plus keyword sweeps for cross-listed papers we'd otherwise miss.
5. Rank candidates with TF-IDF + cosine similarity.
6. Render top-N to _pages/daily-arxiv.md using a string template.

Requirements: scikit-learn, numpy.
"""

from __future__ import annotations

import html
import json
import re
import time
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from collections import Counter
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path
from string import Template
from typing import Iterable

import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# -------- Config ------------------------------------------------------------
INSPIRE_AUTHOR = "Yong.Gao.1"
ARXIV_CATS = ["astro-ph.HE", "gr-qc", "nucl-th"]
DAYS_BACK = 7
MAX_RESULTS_PER_QUERY = 500
KEYWORD_MAX_RESULTS = 200
TOP_N = 50

TOP_COLLABORATORS = 10
PAPERS_PER_COLLAB = 60
LIKED_WEIGHT = 3

KEYWORDS = [
    "neutron star", "dense matter", "equation of state", "kilonova",
    "binary neutron star", "tidal deformability", "pulsar glitch", "r-mode",
    "nuclear pasta", "numerical relativity", "gravitational waves", "pulsar",
    "test gravity", "dynamical tides", "resonances",
]

EXTRA_AUTHOR_NAMES = [
    "Kip Thorne", "Nicolas Yunes", "Hang Yu", "Huan Yang",
    "Dong Lai", "Yanbei Chen","K.-J. Lee", "Bing Zhang", "Zhiqiang Miao",
]

ARXIV_THROTTLE_SECONDS = 3
HTTP_RETRIES = 3
HTTP_TIMEOUT = 60
USER_AGENT = "yg-arxiv-feed/1.0 (mailto:yong@example)"  # courtesy for arXiv/INSPIRE

ROOT = Path(__file__).resolve().parent.parent
LIKED_FILE = ROOT / "_data" / "liked_arxiv.json"
LEGACY_SAVED_FILE = ROOT / "_data" / "saved_arxiv.json"
OUT_FILE = ROOT / "_pages" / "daily-arxiv.md"
TEMPLATE_FILE = ROOT / "_includes" / "arxiv-feed.template.md"
# -----------------------------------------------------------------------------


@dataclass
class CorpusEntry:
    text: str
    weight: int = 1


# ---------- HTTP helpers ----------------------------------------------------

def _http_get(url: str, accept: str = "application/json") -> bytes:
    last_err = None
    for attempt in range(HTTP_RETRIES):
        try:
            req = urllib.request.Request(
                url, headers={"Accept": accept, "User-Agent": USER_AGENT}
            )
            return urllib.request.urlopen(req, timeout=HTTP_TIMEOUT).read()
        except Exception as e:
            last_err = e
            time.sleep(2 ** attempt)
    raise last_err  # type: ignore[misc]


def _http_json(url: str) -> dict:
    return json.loads(_http_get(url, accept="application/json"))


# ---------- INSPIRE ---------------------------------------------------------

def _paper_text(meta: dict) -> str:
    titles = meta.get("titles") or []
    abstracts = meta.get("abstracts") or []
    title = (titles[0].get("title") if titles else "") or ""
    abstract = (abstracts[0].get("value") if abstracts else "") or ""
    return f"{title.strip()} {abstract.strip()}".strip()


def _arxiv_id_of(meta: dict) -> str | None:
    eps = meta.get("arxiv_eprints") or []
    if not eps:
        return None
    v = (eps[0].get("value") or "").strip()
    return _strip_version(v) if v else None


def _strip_version(arxiv_id: str) -> str:
    return re.sub(r"v\d+$", "", arxiv_id)


def fetch_author_papers(bai: str, size: int = 200) -> list[dict]:
    url = (
        "https://inspirehep.net/api/literature?"
        f"size={size}&sort=mostrecent&q=a%20{bai}"
        "&fields=titles,abstracts,authors,arxiv_eprints"
    )
    return _http_json(url)["hits"]["hits"]


def lookup_bai_by_name(name: str) -> str | None:
    url = (
        "https://inspirehep.net/api/authors?"
        f"q={urllib.parse.quote(name)}&size=5&fields=ids,name"
    )
    try:
        hits = _http_json(url)["hits"]["hits"]
    except Exception as e:
        print(f"    ! INSPIRE lookup failed for {name}: {e}")
        return None
    for h in hits:
        for x in (h.get("metadata") or {}).get("ids") or []:
            if x.get("schema") == "INSPIRE BAI":
                return x["value"]
    return None


def pick_top_collaborators(my_papers: list[dict], top_n: int) -> list[str]:
    counter: Counter[str] = Counter()
    for h in my_papers:
        for a in h["metadata"].get("authors", []):
            for x in a.get("ids") or []:
                if x.get("schema") == "INSPIRE BAI" and x["value"] != INSPIRE_AUTHOR:
                    counter[x["value"]] += 1
    return [bai for bai, _ in counter.most_common(top_n)]


# ---------- Corpus assembly -------------------------------------------------

def _key_for(meta: dict, text: str) -> str:
    return _arxiv_id_of(meta) or text[:80]


def _add_inspire_hits(corpus: dict[str, CorpusEntry], hits: list[dict]) -> int:
    added = 0
    for h in hits:
        meta = h["metadata"]
        text = _paper_text(meta)
        if not text:
            continue
        key = _key_for(meta, text)
        if key in corpus:
            continue
        corpus[key] = CorpusEntry(text=text)
        added += 1
    return added


def fetch_corpus_papers() -> dict[str, CorpusEntry]:
    """All INSPIRE-sourced papers: you + collaborators + extra authors."""
    print(f"  + your papers (bai={INSPIRE_AUTHOR})")
    my_papers = fetch_author_papers(INSPIRE_AUTHOR)
    print(f"    {len(my_papers)} papers")

    collaborators = pick_top_collaborators(my_papers, TOP_COLLABORATORS)
    print(f"  + top collaborators: {', '.join(collaborators) or '(none)'}")

    corpus: dict[str, CorpusEntry] = {}
    _add_inspire_hits(corpus, my_papers)

    extra_bais = _resolve_extra_authors(known={INSPIRE_AUTHOR, *collaborators})

    for bai in collaborators + extra_bais:
        try:
            hits = fetch_author_papers(bai, size=PAPERS_PER_COLLAB)
        except Exception as e:
            print(f"    ! failed to fetch {bai}: {e}")
            continue
        added = _add_inspire_hits(corpus, hits)
        print(f"    {bai}: +{added} new papers")

    return corpus


def _resolve_extra_authors(known: set[str]) -> list[str]:
    resolved: list[str] = []
    for name in EXTRA_AUTHOR_NAMES:
        bai = lookup_bai_by_name(name)
        if not bai:
            print(f"    ! could not resolve {name} to a BAI")
            continue
        if bai in known or bai in resolved:
            print(f"    {name} → {bai} (already in corpus)")
            continue
        resolved.append(bai)
        print(f"    + {name} → {bai}")
    return resolved


def load_liked_papers() -> list[dict]:
    for path in (LIKED_FILE, LEGACY_SAVED_FILE):
        if not path.exists():
            continue
        try:
            return json.loads(path.read_text())
        except Exception as e:
            print(f"  ! could not parse {path}: {e}")
    return []


def merge_liked(corpus: dict[str, CorpusEntry], liked: list[dict]) -> int:
    n_added = 0
    for s in liked:
        text = f"{s.get('title') or ''} {s.get('abstract') or ''}".strip()
        if not text:
            continue
        key = s.get("id") or "liked-" + (s.get("title") or "")[:40]
        # If a liked paper is already in the corpus (e.g. authored by you or a
        # collaborator), bump its weight rather than adding a duplicate entry.
        if key in corpus:
            corpus[key].weight = max(corpus[key].weight, LIKED_WEIGHT)
        else:
            corpus[key] = CorpusEntry(text=text, weight=LIKED_WEIGHT)
            n_added += 1
    return n_added


# ---------- arXiv -----------------------------------------------------------

@dataclass
class Candidate:
    id: str
    title: str
    summary: str
    authors: list[str]
    published: datetime
    primary_category: str


def _parse_arxiv_feed(xml_bytes: bytes, cutoff: datetime) -> list[Candidate]:
    ns = {"a": "http://www.w3.org/2005/Atom"}
    tree = ET.fromstring(xml_bytes)
    out: list[Candidate] = []
    for e in tree.findall("a:entry", ns):
        published = datetime.fromisoformat(
            e.find("a:published", ns).text.replace("Z", "+00:00")  # type: ignore[union-attr]
        )
        if published < cutoff:
            break
        arxiv_id = _strip_version(e.find("a:id", ns).text.rsplit("/", 1)[-1])  # type: ignore[union-attr]
        title = re.sub(r"\s+", " ", (e.find("a:title", ns).text or "")).strip()  # type: ignore[union-attr]
        summary = re.sub(r"\s+", " ", (e.find("a:summary", ns).text or "")).strip()  # type: ignore[union-attr]
        authors = [a.find("a:name", ns).text for a in e.findall("a:author", ns)]  # type: ignore[union-attr]
        cats = [c.get("term") for c in e.findall("a:category", ns)]
        out.append(Candidate(
            id=arxiv_id, title=title, summary=summary,
            authors=[a for a in authors if a],
            published=published,
            primary_category=cats[0] if cats else "",
        ))
    return out


def _arxiv_query(search_query: str, days_back: int, max_results: int) -> list[Candidate]:
    url = (
        "http://export.arxiv.org/api/query?"
        f"search_query={urllib.parse.quote(search_query)}"
        f"&sortBy=submittedDate&sortOrder=descending&max_results={max_results}"
    )
    cutoff = datetime.now(timezone.utc) - timedelta(days=days_back)
    return _parse_arxiv_feed(_http_get(url, accept="application/atom+xml"), cutoff)


def fetch_arxiv_candidates() -> list[Candidate]:
    cat_clause = " OR ".join(f"cat:{c}" for c in ARXIV_CATS)
    by_id: dict[str, Candidate] = {}

    print(f"  · category sweep: {cat_clause}")
    for p in _arxiv_query(cat_clause, DAYS_BACK, MAX_RESULTS_PER_QUERY):
        by_id[p.id] = p
    print(f"    {len(by_id)} from categories")

    for kw in KEYWORDS:
        time.sleep(ARXIV_THROTTLE_SECONDS)
        try:
            hits = _arxiv_query(
                f'all:"{kw}" AND ({cat_clause})', DAYS_BACK, KEYWORD_MAX_RESULTS,
            )
        except Exception as e:
            print(f"    ! keyword '{kw}' failed: {e}")
            continue
        added = sum(1 for p in hits if p.id not in by_id)
        for p in hits:
            by_id.setdefault(p.id, p)
        print(f"    +{added} from '{kw}' ({len(hits)} matched)")

    return list(by_id.values())


# ---------- Scoring ---------------------------------------------------------

def score_candidates(
    candidates: list[Candidate], corpus: Iterable[CorpusEntry],
) -> np.ndarray:
    corpus_list = list(corpus)
    # Replicate by integer weight. Replicating both inflates the corpus's IDF
    # for liked terms and pulls candidate similarity toward them — good enough
    # as a relevance prior. A cleaner alternative is per-row sample weighting
    # in the cosine aggregation; revisit if the bias becomes a problem.
    corpus_texts = [
        e.text for e in corpus_list for _ in range(max(1, e.weight))
    ]
    cand_texts = [f"{c.title} {c.summary}" for c in candidates]

    vec = TfidfVectorizer(
        stop_words="english",
        token_pattern=r"(?u)\b[a-z][a-z\-]{2,}\b",
        ngram_range=(1, 2),
        max_df=0.95,
        min_df=1,
    )
    X = vec.fit_transform([t.lower() for t in corpus_texts + cand_texts])
    n_corpus = len(corpus_texts)
    sim = cosine_similarity(X[n_corpus:], X[:n_corpus])
    max_sim = sim.max(axis=1)
    mean_top5 = np.sort(sim, axis=1)[:, -5:].mean(axis=1)
    return 0.7 * max_sim + 0.3 * mean_top5


# ---------- Rendering -------------------------------------------------------

PAGE_TEMPLATE = Template("""---
title: "daily-arxiv"
date: $date
permalink: /daily-arxiv/
modified: $date
excerpt: Daily arXiv feed ranked against my own work, my collaborators', and the papers I've liked.
author_profile: false
mathjax: true
---

<p class="arxiv-toolbar yg-private"><a href="{{ site.url }}/liked/">★ Liked papers →</a></p>

$items

<p class="arxiv-rebuild-meta">
Rebuilt $rebuilt · $n_candidates candidates over the past $days_back days · corpus: $n_corpus papers (you + top $top_collab collaborators$liked_suffix) · ranker: TF-IDF (scikit-learn)
</p>

{% include arxiv-like.html %}
""")

ITEM_TEMPLATE = Template("""<article class="arxiv-item" data-arxiv-id="$id">
  <h3 class="arxiv-item__title"><a href="https://arxiv.org/abs/$id">$title</a></h3>
  <p class="arxiv-item__meta">
    <span class="arxiv-item__authors">$authors</span>
    · <span class="arxiv-item__category">$category</span>
    · <a class="arxiv-item__id" href="https://arxiv.org/abs/$id">$id</a>
    · <span class="arxiv-item__score">relevance $score</span>
  </p>
  <details class="arxiv-item__abstract-wrap"><summary>Abstract</summary>
    <p class="arxiv-item__abstract">$abstract</p>
  </details>
  <p class="arxiv-item__actions">
    <a class="arxiv-action-link" href="https://arxiv.org/pdf/$id.pdf" target="_blank" rel="noopener">PDF</a>
    <button type="button" class="$btn_class" data-arxiv-id="$id" data-payload="$payload"$server_liked_attr>$btn_text</button>
  </p>
</article>
""")


def _render_item(c: Candidate, score: float, is_liked: bool) -> str:
    authors = ", ".join(c.authors[:6]) + (", et al." if len(c.authors) > 6 else "")
    payload = json.dumps({
        "id": c.id,
        "title": c.title,
        "authors": c.authors[:6] + (["et al."] if len(c.authors) > 6 else []),
        "abstract": c.summary,
        "category": c.primary_category,
    }, ensure_ascii=False)
    return ITEM_TEMPLATE.substitute(
        id=c.id,
        title=html.escape(c.title),
        authors=html.escape(authors),
        category=c.primary_category,
        score=f"{score:.2f}",
        abstract=html.escape(c.summary),
        payload=html.escape(payload, quote=True),
        btn_class="arxiv-like-btn yg-private is-liked" if is_liked else "arxiv-like-btn yg-private",
        btn_text="★ Liked" if is_liked else "★ Like",
        server_liked_attr=' data-server-liked="1"' if is_liked else "",
    )


def render_page(
    candidates: list[Candidate],
    scores: np.ndarray,
    n_corpus: int,
    n_liked: int,
) -> str:
    now = datetime.now(timezone.utc)
    ranked = sorted(zip(scores, candidates), key=lambda t: float(t[0]), reverse=True)[:TOP_N]
    liked_ids = {s.get("id") for s in load_liked_papers() if s.get("id")}

    items = "\n".join(
        _render_item(c, float(score), c.id in liked_ids) for score, c in ranked
    )

    return PAGE_TEMPLATE.substitute(
        date=now.strftime("%Y-%m-%d"),
        rebuilt=now.strftime("%Y-%m-%d %H:%M UTC"),
        items=items,
        n_candidates=len(candidates),
        days_back=DAYS_BACK,
        n_corpus=n_corpus,
        top_collab=TOP_COLLABORATORS,
        liked_suffix=f" + {n_liked} liked" if n_liked else "",
    )


# ---------- Main ------------------------------------------------------------

def main() -> None:
    print("Building corpus from INSPIRE…")
    corpus = fetch_corpus_papers()

    liked = load_liked_papers()
    n_liked = merge_liked(corpus, liked)
    print(f"  + liked papers (×{LIKED_WEIGHT} weight): {len(liked)} ({n_liked} new)")
    print(f"  total: {len(corpus)} unique papers")

    print(f"Querying arXiv (cats={ARXIV_CATS}, +{len(KEYWORDS)} keywords, past {DAYS_BACK}d)…")
    candidates = fetch_arxiv_candidates()
    print(f"  {len(candidates)} unique candidates retrieved")

    print("Scoring with TF-IDF…")
    scores = score_candidates(candidates, corpus.values())

    page = render_page(candidates, scores, n_corpus=len(corpus), n_liked=n_liked)
    OUT_FILE.write_text(page)
    print(f"Wrote {OUT_FILE}")


if __name__ == "__main__":
    main()
