#!/bin/bash
# Sync calculator registry tables across all repos
# Source of truth: auto-generated from scan-calculators.py
#
# Usage: bash .shared/sync-calculators.sh
# Run from TECS-L repo root

set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
BASE="$(cd "$SCRIPT_DIR/.." && pwd)"
PARENT="$(cd "$BASE/.." && pwd)"

MARKER_START="<!-- SHARED:CALCULATORS:START -->"
MARKER_END="<!-- SHARED:CALCULATORS:END -->"

echo "=== Calculator Registry Sync ==="
echo ""

# Step 1: Scan all repos
echo "[1/3] Scanning repos..."
CONTENT=$(python3 "$SCRIPT_DIR/scan-calculators.py" --markdown --save 2>/dev/null)

if [ -z "$CONTENT" ]; then
  echo "Error: scan produced no output"
  exit 1
fi

echo "  Registry saved to .shared/calculators.json"
echo ""

# Step 2: Sync to READMEs
sync_file() {
  local file="$1"
  local label="$2"

  echo "[$label]"

  if [ ! -f "$file" ]; then
    echo "  SKIP: $file not found"
    return
  fi

  if ! grep -q "$MARKER_START" "$file"; then
    echo "  SKIP: no markers in $file"
    echo "  Add these markers to README.md:"
    echo "    $MARKER_START"
    echo "    $MARKER_END"
    return
  fi

  python3 -c "
import sys

start_marker = '$MARKER_START'
end_marker = '$MARKER_END'

with open('$file', 'r') as f:
    text = f.read()

s = text.index(start_marker) + len(start_marker)
e = text.index(end_marker)

content = sys.stdin.read()
new_text = text[:s] + '\n' + content + '\n' + text[e:]

with open('$file', 'w') as f:
    f.write(new_text)
" <<< "$CONTENT"

  echo "  SYNCED: $file"
}

commit_and_push() {
  local repo_dir="$1"
  local repo_name="$2"

  cd "$repo_dir"
  if git diff --quiet README.md 2>/dev/null; then
    echo "  No changes"
  else
    git add README.md .shared/calculators.json 2>/dev/null || git add README.md
    git pull --rebase --quiet 2>/dev/null || true
    git commit -m "Sync calculator registry from TECS-L"
    git push
    echo "  Pushed!"
  fi
  cd - > /dev/null
}

echo "[2/3] Syncing README tables..."

# TECS-L
sync_file "$BASE/README.md" "TECS-L"
commit_and_push "$BASE" "TECS-L"

# Anima
sync_file "$PARENT/anima/README.md" "anima"
commit_and_push "$PARENT/anima" "anima"

# SEDI
sync_file "$PARENT/SEDI/README.md" "SEDI"
commit_and_push "$PARENT/SEDI" "SEDI"

# invest — copy TECS-L calc files + sync README
INVEST_CALC="$PARENT/invest/backend/backend/tecs_calc"
if [ -d "$PARENT/invest" ]; then
  echo "[invest] Syncing TECS-L calculators..."
  mkdir -p "$INVEST_CALC"
  cp "$BASE/calc/"*.py "$INVEST_CALC/"
  touch "$INVEST_CALC/__init__.py"
  echo "  Copied $(ls "$INVEST_CALC"/*.py 2>/dev/null | wc -l) calculators"
  sync_file "$PARENT/invest/README.md" "invest"
  cd "$PARENT/invest"
  if ! git diff --quiet 2>/dev/null; then
    git add backend/backend/tecs_calc/ README.md
    git pull --rebase --quiet 2>/dev/null || true
    git commit -m "sync: TECS-L calculators from shared registry"
    git push
    echo "  Pushed!"
  else
    echo "  No changes"
  fi
  cd - > /dev/null
fi

echo ""
echo "[3/3] Done!"
echo ""

# Summary
python3 "$SCRIPT_DIR/scan-calculators.py" --summary 2>/dev/null
