#!/bin/bash
# Sync math atlas across all repos
# Scans TECS-L, anima, SEDI hypothesis files → builds unified atlas
#
# Usage: bash .shared/sync-math-atlas.sh
# Run from TECS-L repo root

set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
BASE="$(cd "$SCRIPT_DIR/.." && pwd)"

echo "=== Math Atlas Sync ==="
echo ""

# Step 1: Build atlas
echo "[1/2] Building atlas..."
python3 "$SCRIPT_DIR/scan_math_atlas.py" --save --summary

echo ""

# Step 2: Commit generated files
echo "[2/2] Committing..."
cd "$BASE"
ATLAS_FILES=".shared/math_atlas.json .shared/math_atlas.db .shared/math_atlas.dot"

if git diff --quiet $ATLAS_FILES 2>/dev/null && \
   git diff --cached --quiet $ATLAS_FILES 2>/dev/null; then
    echo "  No changes"
else
    git add $ATLAS_FILES
    git commit -m "Update math atlas ($(date +%Y-%m-%d))"
    echo "  Committed!"
fi

echo ""
echo "Done!"
