#!/usr/bin/env bash
# Local dev server with the localhost URL override (so internal links
# stay on 127.0.0.1:4000 instead of jumping to the production site).
set -e

# Make sure rbenv's shims are on PATH so `bundle` and `jekyll` resolve to
# the project's rbenv-managed Ruby (3.3.5), not macOS system Ruby.
export PATH="/opt/homebrew/bin:$HOME/.rbenv/shims:$PATH"
eval "$(rbenv init - bash)"

# Filter two harmless internal warnings from the bleeding-edge Jekyll PR
# pinned in the Gemfile (jekyll@refs/pull/9248/head) under Ruby 3.3. They
# come from log_adapter.rb and stevenson.rb and are cosmetic. If you ever
# pin a stable Jekyll release, this filter can be removed.
exec bundle exec jekyll serve \
  --config _config.yml,_localhost.yml \
  --livereload "$@" 2>&1 \
  | grep -v -E 'Logger not initialized properly|Jekyll::Stevenson#initialize: does not call super'
