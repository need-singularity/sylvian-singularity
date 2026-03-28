#!/bin/bash
# Sync shared project descriptions across all repos
# Source of truth: TECS-L/.shared/projects.md
#
# Usage: bash .shared/sync-readmes.sh
# Run from TECS-L repo root

set -e

SHARED="$(cd "$(dirname "$0")" && pwd)/projects.md"
MARKER_START="<!-- SHARED:PROJECTS:START -->"
MARKER_END="<!-- SHARED:PROJECTS:END -->"

if [ ! -f "$SHARED" ]; then
  echo "Error: $SHARED not found"
  exit 1
fi

CONTENT=$(cat "$SHARED")

sync_file() {
  local file="$1"

  if [ ! -f "$file" ]; then
    echo "  SKIP: $file not found"
    return
  fi

  if ! grep -q "$MARKER_START" "$file"; then
    echo "  SKIP: $file has no markers"
    return
  fi

  python3 -c "
import sys
start_marker = '$MARKER_START'
end_marker = '$MARKER_END'
content = '''$CONTENT'''

with open('$file', 'r') as f:
    lines = f.read()

s = lines.index(start_marker) + len(start_marker)
e = lines.index(end_marker)
new = lines[:s] + '\n' + content + '\n' + lines[e:]

with open('$file', 'w') as f:
    f.write(new)
"
  echo "  SYNCED: $file"
}

commit_and_push() {
  local repo_dir="$1"
  local repo_name="$2"

  cd "$repo_dir"
  if git diff --quiet README.md 2>/dev/null; then
    echo "  No changes"
  else
    git add README.md
    git pull --rebase --quiet 2>/dev/null || true
    git commit -m "Sync project list from TECS-L"
    git push
    echo "  Pushed!"
  fi
  cd - > /dev/null
}

BASE="$(cd "$(dirname "$SHARED")/.." && pwd)"
PARENT="$(cd "$BASE/.." && pwd)"

echo "=== Syncing project descriptions ==="
echo "Source: $SHARED"
echo ""

# TECS-L
echo "[TECS-L]"
sync_file "$BASE/README.md"
commit_and_push "$BASE" "TECS-L"

# Anima
echo "[Anima]"
sync_file "$PARENT/anima/README.md"
commit_and_push "$PARENT/anima" "anima"

# PH Training
echo "[PH Training]"
sync_file "$PARENT/ph-training/README.md"
commit_and_push "$PARENT/ph-training" "ph-training"

# SEDI
echo "[SEDI]"
sync_file "$PARENT/sedi/README.md"
commit_and_push "$PARENT/sedi" "sedi"

# Golden MoE
echo "[Golden MoE]"
sync_file "$PARENT/golden-moe/README.md"
commit_and_push "$PARENT/golden-moe" "golden-moe"

# ConsciousLM
echo "[ConsciousLM]"
sync_file "$PARENT/conscious-lm/README.md"
commit_and_push "$PARENT/conscious-lm" "conscious-lm"

# Energy Efficiency
echo "[Energy Efficiency]"
sync_file "$PARENT/energy-efficiency/README.md"
commit_and_push "$PARENT/energy-efficiency" "energy-efficiency"

# BrainWire
echo "[BrainWire]"
sync_file "$PARENT/brainwire/README.md"
commit_and_push "$PARENT/brainwire" "brainwire"

# Papers
echo "[Papers]"
sync_file "$PARENT/papers/README.md"
commit_and_push "$PARENT/papers" "papers"

echo ""
echo "Done!"
