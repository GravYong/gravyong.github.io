#!/usr/bin/env python3
"""
Rebuild _pages/publication.md from your Inspire-HEP record.

Layout:
  - One continuous numbered list of all peer-reviewed papers (newest first
    by publication year, then by Inspire's mostrecent order within a year).
  - No visible year headings in the list itself; each <article> carries a
    data-year attribute for the year filter at the top.
  - The year-nav has buttons for "All", every year present, and a
    "Popular science" link that jumps to the popular-articles section
    at the bottom.
  - Popular-science articles are kept in a static block and always visible.

Run:
    python3 scripts/build_publications.py
"""

import html
import json
import re
import urllib.request
from collections import defaultdict
from pathlib import Path

INSPIRE_AUTHOR = "Yong.Gao.1"
ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "_pages" / "publication.md"


def fetch():
    url = (
        "https://inspirehep.net/api/literature?size=200&sort=mostrecent"
        f"&q=a%20{INSPIRE_AUTHOR}"
        "&fields=titles,authors,arxiv_eprints,dois,publication_info,preprint_date"
    )
    req = urllib.request.Request(url, headers={"Accept": "application/json"})
    return json.loads(urllib.request.urlopen(req, timeout=60).read())["hits"]["hits"]


def fmt_name(full):
    if "," not in full:
        return full
    last, given = [s.strip() for s in full.split(",", 1)]
    parts = []
    for p in given.split():
        sub = [s for s in p.split("-") if s]
        parts.append("-".join(s[0] + "." for s in sub))
    return " ".join(parts) + " " + last


def authors_html(authors):
    names = [fmt_name(a.get("full_name", "?")) for a in authors]
    rendered = []
    for n in names:
        if n.strip() == "Y. Gao":
            rendered.append("<strong>Y. Gao</strong>")
        else:
            rendered.append(html.escape(n))
    if len(rendered) > 10:
        return ", ".join(rendered[:10]) + ", et al."
    if len(rendered) == 1:
        return rendered[0]
    if len(rendered) == 2:
        return f"{rendered[0]} and {rendered[1]}"
    return ", ".join(rendered[:-1]) + ", and " + rendered[-1]


def clean_title(t):
    def repl(m):
        toks = re.findall(r"<(mi|mtext)>([^<]*)</\1>", m.group(1))
        return "".join(f"${v}$" if k == "mi" else v for k, v in toks)
    t = re.sub(r"<math[^>]*>(.*?)</math>", repl, t, flags=re.DOTALL)
    return html.unescape(t).strip()


def journal_html(pi, doi):
    if not pi:
        return ""
    j = (pi.get("journal_title") or "").strip()
    v = (pi.get("journal_volume") or "").strip()
    p = (pi.get("page_start") or pi.get("artid") or "").strip()
    y = pi.get("year", "")
    if not j:
        return f'<a href="https://doi.org/{doi}">DOI</a>' if doi else ""
    out = html.escape(j)
    if v:
        out += f" <strong>{html.escape(v)}</strong>"
    if p:
        out += f", {html.escape(p)}"
    if y:
        out += f" ({html.escape(str(y))})"
    if doi:
        out = f'<a href="https://doi.org/{doi}">{out}</a>'
    return out


def pub_year(m):
    pi = (m.get("publication_info") or [{}])[0]
    if pi.get("year"):
        return int(pi["year"])
    eps = m.get("arxiv_eprints", [])
    if eps:
        eid = eps[0].get("value") or ""
        if "." in eid:
            return 2000 + int(eid.split(".")[0][:2])
    pd = m.get("preprint_date", "")
    if pd:
        return int(pd[:4])
    return 0


def render_entry_html(m, year, num):
    title = clean_title(m["titles"][0]["title"])
    authors = authors_html(m.get("authors", []))
    arxiv = ((m.get("arxiv_eprints") or [{}])[0].get("value") or "")
    doi = ((m.get("dois") or [{}])[0].get("value") or "")
    j = journal_html((m.get("publication_info") or [{}])[0], doi)

    parts = [authors, f"<em>{html.escape(title)}</em>"]
    if j:
        parts.append(j)
    body = ", ".join(parts) + "."
    if arxiv:
        body += f' <a href="https://arxiv.org/abs/{arxiv}" style="color: #F48FB1;">[arXiv]</a>'
    return (
        f'<article class="pub-entry" data-year="{year}" data-num="{num}">'
        f"{body}</article>"
    )


POPULAR_SECTION = """\
<section class="pub-popular" id="popular-science-articles" style="display:none" markdown="1">

<hr style="border:1px solid gray">

# Popular science articles

1. **Y. Gao**, G. Desvignes, L. Shao (2024) [一颗自由进动的磁星](https://www.sciengine.com/cfs/files/pdfs/view/0023-074X/C9C2E28FCEC3452AB1A2AEF32A5DBB53.pdf) (an article about freely precessing magnetars, in Chinese).

2. **Y. Gao** (2022) [The structures of neutron stars](https://gravyong.github.io/files/NS_Structure_Popular.pdf) (an article about dense matter in neutron stars, in Chinese).

3. **Y. Gao**, L. Shao (2022) [Does Einstein's theory of gravity hold up to the latest LIGO/VIRGO/KAGRA observations?](https://www.ligo.org/science/Publication-O3bTGR/translations/science-summary-chinese-simplified.pdf) (translated from [the English version](https://www.ligo.org/science/Publication-O3bTGR/)).

4. **Y. Gao**, L. Shao, R.-X. Xu (2019) [The waltz of a binary neutron star system](https://gravyong.github.io/files/BNS_Popular.pdf) (an article about GW170817, in Chinese).

</section>
"""

FILTER_SCRIPT = r"""<script>
(function () {
  function applyFilter(year) {
    document.querySelectorAll('.year-nav__btn[data-filter-year]').forEach(function (b) {
      b.classList.toggle('is-active', b.dataset.filterYear === year);
    });
    var isAll = year === 'all';
    var isPopular = year === 'popular';

    var pubList = document.querySelector('.pub-list');
    if (pubList) pubList.style.display = isPopular ? 'none' : '';
    var popSection = document.getElementById('popular-science-articles');
    if (popSection) popSection.style.display = isPopular ? '' : 'none';

    var visible = [];
    document.querySelectorAll('.pub-entry').forEach(function (e) {
      var match = !isPopular && (isAll || e.dataset.year === year);
      e.style.display = match ? '' : 'none';
      if (match) visible.push(e);
    });
    var total = visible.length;
    visible.forEach(function (e, i) {
      e.dataset.num = total - i;
    });
  }
  function readFromHash() {
    var h = (location.hash || '').replace(/^#/, '');
    return h || 'all';
  }
  function syncFromHash() { applyFilter(readFromHash()); }

  document.addEventListener('click', function (e) {
    var btn = e.target.closest('.year-nav__btn[data-filter-year]');
    if (!btn) return;
    e.preventDefault();
    var year = btn.dataset.filterYear;
    var newHash = (year === 'all') ? '' : ('#' + year);
    var curHash = location.hash || '';
    if (newHash !== curHash) {
      history.pushState({}, '', location.pathname + location.search + newHash);
    }
    applyFilter(year);
  });
  window.addEventListener('popstate', syncFromHash);
  window.addEventListener('hashchange', syncFromHash);
  syncFromHash();
})();
</script>
"""


def main():
    hits = fetch()
    print(f"  fetched {len(hits)} papers from Inspire-HEP")

    # Group by year first to preserve ordering, then flatten
    by_year = defaultdict(list)
    for h in hits:
        m = h["metadata"]
        by_year[pub_year(m)].append(m)

    years = sorted(by_year.keys(), reverse=True)
    flat = []
    for y in years:
        for m in by_year[y]:
            flat.append((y, m))

    # Render entries with running 1.. numbering
    entry_html = [
        render_entry_html(m, y, i + 1) for i, (y, m) in enumerate(flat)
    ]

    out = []
    out.append("---")
    out.append('title: "Publications"')
    out.append("date: 2022-10-16")
    out.append("permalink: /publication/")
    out.append("modified: 2026-04-25")
    out.append("mathjax: true")
    out.append("excerpt:")
    out.append("tags:")
    out.append("---")
    out.append("")
    out.append("<p>")
    out.append("In online databases:")
    out.append('<span class="archive__item-title">')
    out.append('<a href="https://inspirehep.net/search?p=exactauthor%3A{{ site.author.inspire }}"><i class="ai ai-fw ai-inspire" aria-hidden="true"></i> Inspire</a>,')
    out.append('<a href="https://orcid.org/{{ site.author.orcid }}"><i class="ai ai-fw ai-orcid" aria-hidden="true"></i> ORCID</a>,')
    out.append("and")
    out.append('<a href="https://scholar.google.com/citations?user={{ site.author.google-scholar }}"><i class="ai ai-fw ai-google-scholar" aria-hidden="true"></i> Google Scholar</a></span>.')
    out.append("<br>")
    out.append("Generated from my Inspire-HEP record. Click a year to filter; click <strong>All</strong> to restore the full list.")
    out.append("</p>")
    out.append('<hr style="border:1px solid gray">')
    out.append("")

    out.append('<nav class="year-nav">')
    out.append('  <a href="#" class="year-nav__btn is-active" data-filter-year="all">All</a>')
    for y in years:
        out.append(f'  <a href="#" class="year-nav__btn" data-filter-year="{y}">{y}</a>')
    out.append('  <a href="#" class="year-nav__btn year-nav__btn--anchor" data-filter-year="popular">Popular science</a>')
    out.append("</nav>")
    out.append("")

    out.append('<div class="pub-list">')
    for h in entry_html:
        out.append(h)
    out.append("</div>")
    out.append("")

    out.append(POPULAR_SECTION)
    out.append("")
    out.append(FILTER_SCRIPT)

    OUT.write_text("\n".join(out))
    print(f"  wrote {OUT}")
    print(f"  years present: {', '.join(str(y) for y in years)}")
    print(f"  total peer-reviewed: {len(entry_html)}")


if __name__ == "__main__":
    main()
