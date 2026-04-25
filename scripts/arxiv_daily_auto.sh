#!/usr/bin/env bash
# Run the daily-arxiv generator and commit/push if anything changed.
# Designed to be called from cron or launchd.
#
#   30 8 * * * /Users/yong/Desktop/website/scripts/arxiv_daily_auto.sh >> /tmp/arxiv-daily.log 2>&1
#
set -e

cd "$(dirname "$0")/.."

# Use Homebrew/user Python first.
export PATH="/opt/homebrew/bin:/usr/local/bin:$PATH"

python3 scripts/arxiv_daily.py

if git diff --quiet -- _pages/daily-arxiv.md; then
  echo "$(date -u '+%Y-%m-%dT%H:%M:%SZ') no changes"
  exit 0
fi

git add _pages/daily-arxiv.md
git commit -m "daily-arxiv: $(date -u +%Y-%m-%d) update"

if git remote get-url origin >/dev/null 2>&1; then
  git push
fi
