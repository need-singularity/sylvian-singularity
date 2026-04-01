#!/bin/bash
# Sync .shared/dse/ (Universal DSE) across all repos
# Source of truth: TECS-L/.shared/dse/
#
# Usage: bash .shared/sync-dse.sh
# Run from TECS-L repo root

set -e

SHARED_DIR="$(cd "$(dirname "$0")" && pwd)"
DSE_SRC="$SHARED_DIR/dse"
BASE="$(cd "$SHARED_DIR/.." && pwd)"
PARENT="$(cd "$BASE/.." && pwd)"

if [ ! -d "$DSE_SRC" ]; then
  echo "Error: $DSE_SRC not found"
  exit 1
fi

sync_dse() {
  local repo_dir="$1"
  local repo_name="$2"

  if [ ! -d "$repo_dir" ]; then
    echo "  SKIP: $repo_dir not found"
    return
  fi

  local target="$repo_dir/.shared/dse"
  mkdir -p "$target/domains"

  # Sync source + binary + domains
  cp "$DSE_SRC/main.rs" "$target/main.rs"
  cp "$DSE_SRC/universal-dse" "$target/universal-dse"
  chmod +x "$target/universal-dse"
  cp "$DSE_SRC/domains/"*.toml "$target/domains/"

  echo "  SYNCED: $target"
}

commit_and_push() {
  local repo_dir="$1"
  local repo_name="$2"

  cd "$repo_dir"
  if git diff --quiet .shared/dse/ 2>/dev/null && \
     [ -z "$(git ls-files --others --exclude-standard .shared/dse/)" ]; then
    echo "  No changes"
  else
    git add .shared/dse/
    git pull --rebase --quiet 2>/dev/null || true
    git commit -m "Sync DSE from TECS-L (.shared/dse/)"
    git push
    echo "  Pushed!"
  fi
  cd - > /dev/null
}

echo "=== Syncing Universal DSE ==="
echo "Source: $DSE_SRC"
echo "Files: main.rs + universal-dse + $(ls "$DSE_SRC/domains/"*.toml | wc -l | tr -d ' ') domains"
echo ""

for repo in anima sedi n6-architecture brainwire papers; do
  repo_dir="$PARENT/$repo"
  echo "[$repo]"
  sync_dse "$repo_dir" "$repo"
  commit_and_push "$repo_dir" "$repo"
done

echo ""
echo "Done! DSE synced to all repos."
echo "Usage: .shared/dse/universal-dse .shared/dse/domains/<domain>.toml"
