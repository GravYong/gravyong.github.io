# scripts/

Tools that generate pages on the site.

## `build_publications.py` — rebuild the publications page

Rebuilds `_pages/publication.md` from your Inspire-HEP record (`Yong.Gao.1`).

- One continuous numbered list of all peer-reviewed papers, newest first
  (by publication year, then Inspire's `mostrecent` order within a year).
- No visible year headings in the list. Each `<article>` carries a
  `data-year` attribute that drives the year filter at the top of the page.
- The year-nav has buttons for "All", every year present, and a
  "Popular science" link that jumps to the popular-articles section.
- Popular-science articles live in a static block and are always shown.

### Run it

```
python3 scripts/build_publications.py
```

It fetches up to 200 records from the Inspire-HEP API and overwrites
`_pages/publication.md`, so review the diff before committing.
