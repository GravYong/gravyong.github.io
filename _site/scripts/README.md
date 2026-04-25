# scripts/

Tools that generate pages on the site.

## `arxiv_daily.py` — daily arXiv feed

Builds `/Users/yong/Desktop/website/_pages/daily-arxiv.md`: top recent arXiv submissions in **astro-ph.HE**, **gr-qc**, and **nucl-th**, ranked against your *and your collaborators'* research.

### How the ranking works

1. Pulls every paper listed under your INSPIRE-HEP author record (`Yong.Gao.1`).
2. Walks the author lists of those papers to find your **top 10 most frequent collaborators** (by INSPIRE BAI), then fetches each of their 15 most recent papers.
3. The combined corpus (~146 papers as of writing) becomes your "interest profile."
4. **If `scikit-learn` is installed**, candidates are scored with TF-IDF + cosine similarity. The score for a candidate is `0.7 × max(similarity to any corpus paper) + 0.3 × mean(similarity to top-5 corpus papers)`. This rewards both narrow and broad relevance.
5. **Otherwise**, falls back to a log-weighted vocabulary profile (stdlib only, slightly worse but always works).

To enable TF-IDF (recommended):

```
python3 -m pip install --user scikit-learn
```

### Save / hide / saved-list

Each candidate has a **★ Save** and a **Hide** button.

- **Save** stores `{id, title, authors, abstract, category, saved_at}` in `localStorage` under `yg-arxiv-saved`. The full payload means the [Saved](/saved/) page can render without re-fetching anything.
- **Hide** stores the arXiv ID in `localStorage` under `yg-arxiv-hidden`; hidden papers `display: none` on subsequent renders. (The hide list is separate from the save list, so a hidden paper can also be saved if you want.)

### Run it once

```
python3 scripts/arxiv_daily.py
```

### Run it daily and auto-commit

`scripts/arxiv_daily_auto.sh` regenerates the page and, if anything changed, commits and pushes it. Wire it up via:

**macOS launchd** — `~/Library/LaunchAgents/com.yong.arxiv-daily.plist`:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
  <key>Label</key><string>com.yong.arxiv-daily</string>
  <key>ProgramArguments</key>
  <array>
    <string>/Users/yong/Desktop/website/scripts/arxiv_daily_auto.sh</string>
  </array>
  <key>WorkingDirectory</key><string>/Users/yong/Desktop/website</string>
  <key>StartCalendarInterval</key>
  <dict><key>Hour</key><integer>8</integer><key>Minute</key><integer>30</integer></dict>
  <key>StandardOutPath</key><string>/tmp/arxiv-daily.log</string>
  <key>StandardErrorPath</key><string>/tmp/arxiv-daily.log</string>
</dict>
</plist>
```

Activate:

```
launchctl load ~/Library/LaunchAgents/com.yong.arxiv-daily.plist
```

**Plain cron** alternative:

```
30 8 * * * /Users/yong/Desktop/website/scripts/arxiv_daily_auto.sh >> /tmp/arxiv-daily.log 2>&1
```

The wrapper runs the generator, checks `git diff --quiet -- _pages/daily-arxiv.md`, and only commits + pushes when there's a real change.

### Tuning

Constants at the top of `scripts/arxiv_daily.py`:

| Knob | Default | What it does |
|------|---------|---|
| `INSPIRE_AUTHOR` | `Yong.Gao.1` | Your INSPIRE BAI |
| `ARXIV_CATS` | `astro-ph.HE`, `gr-qc`, `nucl-th` | Which arXiv categories to crawl |
| `DAYS_BACK` | `7` | Submission window |
| `TOP_N` | `25` | How many papers to surface |
| `TOP_COLLABORATORS` | `10` | How many co-authors to include |
| `PAPERS_PER_COLLAB` | `15` | Most-recent paper cap per collaborator |
| `STOPWORDS` | (built-in) | Extend if generic words dominate scores |
