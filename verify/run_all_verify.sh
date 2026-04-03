#!/usr/bin/env bash
# run_all_verify.sh — Run all verify_*.py and frontier_*_verify.py scripts
# Outputs a summary table with script name, status (PASS/FAIL/ERROR), and elapsed time.
# Results saved to verify/dashboard_results.txt

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
RESULTS_FILE="$SCRIPT_DIR/dashboard_results.txt"
TIMEOUT_SEC="${VERIFY_TIMEOUT:-120}"

# Detect timeout command (macOS: gtimeout via coreutils, Linux: timeout)
if command -v gtimeout &>/dev/null; then
  TIMEOUT_CMD="gtimeout"
elif command -v timeout &>/dev/null; then
  TIMEOUT_CMD="timeout"
else
  # Fallback: use Python-based timeout wrapper
  TIMEOUT_CMD=""
fi

run_with_timeout() {
  local secs="$1"
  shift
  if [ -n "$TIMEOUT_CMD" ]; then
    $TIMEOUT_CMD "$secs" "$@"
  else
    # Python-based timeout fallback for macOS without coreutils
    python3 -c "
import subprocess, sys
try:
    r = subprocess.run(sys.argv[1:], timeout=$secs, capture_output=True, text=True)
    sys.stdout.write(r.stdout)
    sys.stderr.write(r.stderr)
    sys.exit(r.returncode)
except subprocess.TimeoutExpired:
    sys.exit(124)
" "$@"
  fi
}

# Collect all verify scripts
SCRIPTS=()
while IFS= read -r f; do
  SCRIPTS+=("$f")
done < <(find "$SCRIPT_DIR" -maxdepth 1 \( -name 'verify_*.py' -o -name 'frontier_*_verify.py' \) | sort)

TOTAL=${#SCRIPTS[@]}
PASS=0
FAIL=0
ERROR=0
SKIP=0

# Header
{
  echo "======================================================================"
  echo "  Verify Dashboard — $(date '+%Y-%m-%d %H:%M:%S')"
  echo "  Scripts: $TOTAL"
  echo "  Timeout: ${TIMEOUT_SEC}s per script"
  echo "======================================================================"
  echo ""
  printf "%-55s | %-7s | %s\n" "Script" "Status" "Time"
  printf "%-55s-|-%s-|-%s\n" "-------------------------------------------------------" "-------" "--------"
} | tee "$RESULTS_FILE"

for script in "${SCRIPTS[@]}"; do
  name="$(basename "$script")"
  start_ts=$(python3 -c "import time; print(time.time())")

  # Run with timeout, capture exit code
  set +e
  output=$(cd "$PROJECT_ROOT" && PYTHONPATH=. run_with_timeout "$TIMEOUT_SEC" python3 "$script" 2>&1)
  exit_code=$?
  set -e

  end_ts=$(python3 -c "import time; print(time.time())")
  elapsed=$(python3 -c "print(f'{$end_ts - $start_ts:.1f}s')")

  if [ $exit_code -eq 0 ]; then
    status="PASS"
    PASS=$((PASS + 1))
  elif [ $exit_code -eq 124 ]; then
    status="TIMEOUT"
    ERROR=$((ERROR + 1))
  else
    # Check if it's a missing import / syntax error vs logic failure
    if echo "$output" | grep -q "ModuleNotFoundError\|ImportError\|SyntaxError"; then
      status="SKIP"
      SKIP=$((SKIP + 1))
    else
      status="FAIL"
      FAIL=$((FAIL + 1))
    fi
  fi

  printf "%-55s | %-7s | %s\n" "$name" "$status" "$elapsed" | tee -a "$RESULTS_FILE"
done

# Summary
{
  echo ""
  echo "======================================================================"
  echo "  Summary"
  echo "======================================================================"
  echo "  Total:   $TOTAL"
  echo "  PASS:    $PASS"
  echo "  FAIL:    $FAIL"
  echo "  ERROR:   $ERROR (timeout)"
  echo "  SKIP:    $SKIP (missing deps)"
  echo "  Rate:    $(python3 -c "print(f'{$PASS/$TOTAL*100:.1f}%' if $TOTAL > 0 else 'N/A')")"
  echo "======================================================================"
} | tee -a "$RESULTS_FILE"

echo ""
echo "Results saved to: $RESULTS_FILE"
