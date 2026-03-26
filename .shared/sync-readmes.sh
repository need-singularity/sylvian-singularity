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
  local repo_name="$2"

  if [ ! -f "$file" ]; then
    echo "  SKIP: $file not found"
    return
  fi

  if ! grep -q "$MARKER_START" "$file"; then
    echo "  SKIP: $file has no markers (add $MARKER_START / $MARKER_END)"
    return
  fi

  # Replace content between markers
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

echo "=== Syncing project descriptions ==="
echo "Source: $SHARED"
echo ""

# TECS-L
echo "[TECS-L]"
sync_file "$(dirname "$SHARED")/../README.md" "TECS-L"

# Anima
echo "[Anima]"
sync_file "$(dirname "$SHARED")/../../anima/README.md" "anima"

# PH Training
echo "[PH Training]"
sync_file "$(dirname "$SHARED")/../../ph-training/README.md" "ph-training"

# SEDI
echo "[SEDI]"
sync_file "$(dirname "$SHARED")/../../sedi/README.md" "sedi"

echo ""
echo "Done! Review changes with: git diff"
echo "Then commit each repo separately."
