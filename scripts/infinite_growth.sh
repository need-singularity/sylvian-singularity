#!/usr/bin/env bash
# TECS-L Infinite Growth Daemon — 12-phase cyclic growth engine
# Modeled after anima's growth pattern, tailored for the mathematical
# theory foundation: hypotheses, calculators, atlas, characterizations.
#
# Usage: bash scripts/infinite_growth.sh [--interval MIN] [--max-cycles N]
# PID:   /tmp/tecs_l_infinite_growth.pid
# Log:   /tmp/tecs_l_infinite_growth.log

set -euo pipefail
source "$(cd "$(dirname "$0")" && pwd)/lib/growth_common.sh"

# ── Config ──────────────────────────────────────────────────────────────
INTERVAL=3          # minutes between cycles
MAX_CYCLES=999      # effectively infinite
PID_FILE="/tmp/tecs_l_infinite_growth.pid"
LOG_FILE="/tmp/tecs_l_infinite_growth.log"
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
GROWTH_DIR="$ROOT/.growth"
SHARED_DIR="$ROOT/.shared"
CALC_DIR="$ROOT/calc"
HYPO_DIR="$ROOT/docs/hypotheses"
PAPER_DIR="$ROOT/docs/paper"
STATE_FILE="$GROWTH_DIR/growth_state.json"
NEXUS6_BUS="$HOME/Dev/nexus6/shared/growth_bus.jsonl"

# ── Parse args (bash 3.2 compatible) ───────────────────────────────────
while [ $# -gt 0 ]; do
    case "$1" in
        --interval)  INTERVAL="$2"; shift 2 ;;
        --max-cycles) MAX_CYCLES="$2"; shift 2 ;;
        --help|-h)
            echo "Usage: $0 [--interval MIN] [--max-cycles N]"
            echo "  --interval   Minutes between cycles (default: 3)"
            echo "  --max-cycles Max cycles before exit (default: 999)"
            exit 0
            ;;
        *) echo "Unknown arg: $1"; exit 1 ;;
    esac
done

# ── Functions ──────────────────────────────────────────────────────────

log() {
    local ts
    ts="$(date '+%Y-%m-%d %H:%M:%S')"
    echo "[$ts] $*" | tee -a "$LOG_FILE"
}

phase_log() {
    local phase="$1"; shift
    log "  Phase $phase: $*"
}

emit_bus() {
    # Write JSON line to nexus6 growth bus
    local msg="$1"
    local bus_dir
    bus_dir="$(dirname "$NEXUS6_BUS")"
    if [ -d "$bus_dir" ]; then
        local ts
        ts="$(date '+%Y-%m-%dT%H:%M:%S')"
        echo "{\"source\":\"tecs-l-daemon\",\"timestamp\":\"$ts\",\"phase\":\"$msg\"}" >> "$NEXUS6_BUS" 2>/dev/null || true
    fi
}

# Count files matching a glob pattern (bash 3.2 safe)
count_files() {
    local pattern="$1"
    local count=0
    # Use find instead of glob to be safe
    if [ -d "$(dirname "$pattern")" ]; then
        count=$(find "$(dirname "$pattern")" -maxdepth 1 -name "$(basename "$pattern")" 2>/dev/null | wc -l | tr -d ' ')
    fi
    echo "$count"
}

# ── PID guard ──────────────────────────────────────────────────────────
if [ -f "$PID_FILE" ]; then
    old_pid=$(cat "$PID_FILE" 2>/dev/null || echo "")
    if [ -n "$old_pid" ] && kill -0 "$old_pid" 2>/dev/null; then
        echo "Already running (PID $old_pid). Kill it first or remove $PID_FILE."
        exit 1
    fi
    rm -f "$PID_FILE"
fi
echo $$ > "$PID_FILE"

# ── Cleanup on exit ───────────────────────────────────────────────────
cleanup() {
    rm -f "$PID_FILE"
    log "Daemon stopped (PID $$)"
}
trap cleanup EXIT INT TERM

# ── Banner ─────────────────────────────────────────────────────────────
cat <<'BANNER'

  ╔══════════════════════════════════════════════════════════╗
  ║                                                          ║
  ║   ████████╗███████╗ ██████╗███████╗      ██╗             ║
  ║   ╚══██╔══╝██╔════╝██╔════╝██╔════╝      ██║             ║
  ║      ██║   █████╗  ██║     ███████╗█████╗██║             ║
  ║      ██║   ██╔══╝  ██║     ╚════██║╚════╝██║             ║
  ║      ██║   ███████╗╚██████╗███████║      ███████╗        ║
  ║      ╚═╝   ╚══════╝ ╚═════╝╚══════╝      ╚══════╝        ║
  ║                                                          ║
  ║   Infinite Growth Engine  --  12 Phase Cycle             ║
  ║   sigma(n)*phi(n) = n*tau(n)  iff  n = 6                ║
  ║                                                          ║
  ╚══════════════════════════════════════════════════════════╝

BANNER

log "Starting TECS-L Infinite Growth (PID $$)"
log "  Root:       $ROOT"
log "  Interval:   ${INTERVAL}m"
log "  Max cycles: $MAX_CYCLES"
log ""

# ── Main Loop ──────────────────────────────────────────────────────────
cycle=0
while [ "$cycle" -lt "$MAX_CYCLES" ]; do
    cycle=$((cycle + 1))
    log "═══ Cycle $cycle/$MAX_CYCLES ═══════════════════════════════════"

    phase_ok=0
    phase_fail=0

    # ── Phase 1: Hypothesis scan ──────────────────────────────────────
    hypo_count=0
    if [ -d "$HYPO_DIR" ]; then
        hypo_count=$(find "$HYPO_DIR" -maxdepth 1 -name '*.md' 2>/dev/null | wc -l | tr -d ' ')
    fi
    # Count unverified (no EXACT/CLOSE/FAIL/WEAK marker)
    unverified=0
    if [ -d "$HYPO_DIR" ] && [ "$hypo_count" -gt 0 ]; then
        for f in "$HYPO_DIR"/*.md; do
            if [ -f "$f" ]; then
                if ! head -50 "$f" 2>/dev/null | grep -qE 'EXACT|CLOSE|FAIL|WEAK|VERIFIED'; then
                    unverified=$((unverified + 1))
                fi
            fi
        done
    fi
    phase_log 1 "Hypotheses: $hypo_count total, $unverified unverified"
    phase_ok=$((phase_ok + 1))

    # ── Phase 2: Calculator health ────────────────────────────────────
    calc_py=0
    calc_rs=0
    calc_broken=0
    if [ -d "$CALC_DIR" ]; then
        calc_py=$(find "$CALC_DIR" -maxdepth 1 -name '*.py' 2>/dev/null | wc -l | tr -d ' ')
        calc_rs=$(find "$CALC_DIR" -maxdepth 1 -name '*.rs' 2>/dev/null | wc -l | tr -d ' ')
        # Syntax check Python files (sample up to 50)
        checked=0
        for f in "$CALC_DIR"/*.py; do
            if [ -f "$f" ] && [ "$checked" -lt 50 ]; then
                if ! python3 -c "import py_compile; py_compile.compile('$f', doraise=True)" 2>/dev/null; then
                    calc_broken=$((calc_broken + 1))
                fi
                checked=$((checked + 1))
            fi
        done
    fi
    calc_total=$((calc_py + calc_rs))
    phase_log 2 "Calculators: $calc_total ($calc_py py + $calc_rs rs), $calc_broken broken"
    if [ "$calc_broken" -eq 0 ]; then
        phase_ok=$((phase_ok + 1))
    else
        phase_fail=$((phase_fail + 1))
    fi

    # ── Phase 3: Atlas integrity ──────────────────────────────────────
    atlas_entries=0
    atlas_constants=0
    if [ -f "$SHARED_DIR/math_atlas.json" ]; then
        atlas_entries=$(python3 -c "
import json, sys
try:
    d=json.load(open('$SHARED_DIR/math_atlas.json'))
    print(len(d.get('hypotheses',[])))
except: print(0)
" 2>/dev/null || echo 0)
        atlas_constants=$(python3 -c "
import json, sys
try:
    d=json.load(open('$SHARED_DIR/math_atlas.json'))
    print(len(d.get('constant_maps',[])))
except: print(0)
" 2>/dev/null || echo 0)
    fi
    phase_log 3 "Atlas: $atlas_entries hypotheses, $atlas_constants constant maps"
    phase_ok=$((phase_ok + 1))

    # ── Phase 4: NEXUS-6 telescope scan ───────────────────────────────
    if [ -f "$SHARED_DIR/scan_math_atlas.py" ]; then
        scan_result=$(python3 "$SHARED_DIR/scan_math_atlas.py" --save --summary 2>&1 | tail -1 || echo "scan failed")
        phase_log 4 "NEXUS-6 atlas scan: $scan_result"
        phase_ok=$((phase_ok + 1))
    else
        phase_log 4 "NEXUS-6 atlas scan: SKIP (scan_math_atlas.py not found)"
        phase_fail=$((phase_fail + 1))
    fi

    # ── Phase 5: Characterization progress ────────────────────────────
    char_count=0
    char_stale=0
    threshold=$(python3 -c "import time; print(int(time.time() - 30*86400))" 2>/dev/null || echo 0)
    for pat in "$ROOT/docs/"*"/characterization"*".md" "$ROOT/docs/characterizations/"*".md"; do
        # bash 3.2: iterate and check if file exists
        if [ -f "$pat" ]; then
            char_count=$((char_count + 1))
            mtime=$(python3 -c "import os; print(int(os.path.getmtime('$pat')))" 2>/dev/null || echo 0)
            if [ "$mtime" -lt "$threshold" ] 2>/dev/null; then
                char_stale=$((char_stale + 1))
            fi
        fi
    done
    phase_log 5 "Characterizations: $char_count total, $char_stale stale (30d+)"
    phase_ok=$((phase_ok + 1))

    # ── Phase 6: Growth scan (.growth/scan.py) ────────────────────────
    growth_delta=0
    opp_count=0
    if [ -f "$GROWTH_DIR/scan.py" ]; then
        scan_json=$(python3 "$GROWTH_DIR/scan.py" 2>/dev/null || echo '{"opportunities":[],"growth_delta":0}')
        opp_count=$(echo "$scan_json" | python3 -c "import json,sys; d=json.load(sys.stdin); print(len(d.get('opportunities',[])))" 2>/dev/null || echo 0)
        growth_delta=$(echo "$scan_json" | python3 -c "import json,sys; d=json.load(sys.stdin); print(d.get('growth_delta',0))" 2>/dev/null || echo 0)
        phase_log 6 "Growth scan: $opp_count opportunities, delta=$growth_delta"
        phase_ok=$((phase_ok + 1))
    else
        phase_log 6 "Growth scan: SKIP (scan.py not found)"
        phase_fail=$((phase_fail + 1))
    fi

    # ── Phase 7: Discovery check ──────────────────────────────────────
    # Look for recent discoveries (files modified in last cycle interval)
    new_discoveries=0
    interval_secs=$((INTERVAL * 60))
    if [ -d "$HYPO_DIR" ]; then
        new_discoveries=$(find "$HYPO_DIR" -maxdepth 1 -name '*.md' -newer "$PID_FILE" 2>/dev/null | wc -l | tr -d ' ')
    fi
    phase_log 7 "Discovery check: $new_discoveries new since last cycle"
    phase_ok=$((phase_ok + 1))

    # ── Phase 8: Tool registry sync ───────────────────────────────────
    if [ -f "$SHARED_DIR/sync-calculators.sh" ]; then
        sync_out=$(bash "$SHARED_DIR/sync-calculators.sh" 2>&1 | tail -1 || echo "sync failed")
        phase_log 8 "Tool registry sync: $sync_out"
        phase_ok=$((phase_ok + 1))
    else
        phase_log 8 "Tool registry sync: SKIP (script not found)"
        phase_fail=$((phase_fail + 1))
    fi

    # ── Phase 9: Cross-repo sync ──────────────────────────────────────
    if [ -f "$SHARED_DIR/sync-claude-rules.sh" ]; then
        # Run but don't block on failure (other repos may not be available)
        sync_rules=$(bash "$SHARED_DIR/sync-claude-rules.sh" 2>&1 | tail -1 || echo "sync skipped")
        phase_log 9 "Cross-repo sync: $sync_rules"
        phase_ok=$((phase_ok + 1))
    else
        phase_log 9 "Cross-repo sync: SKIP"
        phase_fail=$((phase_fail + 1))
    fi

    # ── Phase 10: Paper readiness ─────────────────────────────────────
    paper_count=0
    paper_draft=0
    if [ -d "$PAPER_DIR" ]; then
        paper_count=$(find "$PAPER_DIR" -maxdepth 1 \( -name '*.md' -o -name '*.tex' \) 2>/dev/null | wc -l | tr -d ' ')
        for f in "$PAPER_DIR"/*.md "$PAPER_DIR"/*.tex; do
            if [ -f "$f" ]; then
                if head -100 "$f" 2>/dev/null | grep -qE 'TODO|DRAFT|TBD'; then
                    paper_draft=$((paper_draft + 1))
                fi
            fi
        done
    fi
    phase_log 10 "Papers: $paper_count total, $paper_draft drafts"
    phase_ok=$((phase_ok + 1))

    # ── Phase 11: Growth tick ─────────────────────────────────────────
    if [ -f "$STATE_FILE" ]; then
        python3 -c "
import json, time
try:
    with open('$STATE_FILE') as f:
        state = json.load(f)
    state['interaction_count'] = state.get('interaction_count', 0) + 1
    state['stats']['calcs_total'] = $calc_total
    state['stats']['hypotheses_total'] = $hypo_count
    state['stats']['atlas_entries'] = $atlas_entries
    state['stats']['last_tick'] = time.strftime('%Y-%m-%dT%H:%M:%S')
    count = state['interaction_count']
    stages = [(4, 10000, 'forest'), (3, 2000, 'tree'), (2, 500, 'sapling'), (1, 100, 'sprout')]
    for idx, threshold, name in stages:
        if count >= threshold and state.get('stage_index', 0) < idx:
            state['stage_index'] = idx
            state['stage_name'] = name
            break
    with open('$STATE_FILE', 'w') as f:
        json.dump(state, f, indent=2, ensure_ascii=False)
    print(f'tick #{count}, stage={state[\"stage_name\"]}')
except Exception as e:
    print(f'tick failed: {e}')
" 2>/dev/null
        tick_out=$(python3 -c "
import json
try:
    d=json.load(open('$STATE_FILE'))
    print(f\"count={d['interaction_count']}, stage={d['stage_name']}\")
except: print('unknown')
" 2>/dev/null || echo "unknown")
        phase_log 11 "Growth tick: $tick_out"
        phase_ok=$((phase_ok + 1))
    else
        phase_log 11 "Growth tick: SKIP (state file not found)"
        phase_fail=$((phase_fail + 1))
    fi

    # ── Phase 12: Auto-commit ─────────────────────────────────────────
    cd "$ROOT"
    changes=$(git diff --stat 2>/dev/null | wc -l | tr -d ' ')
    untracked=$(git ls-files --others --exclude-standard 2>/dev/null | wc -l | tr -d ' ')
    if [ "$changes" -gt 0 ] || [ "$untracked" -gt 0 ]; then
        # Only auto-commit growth state and atlas changes
        git add -f "$STATE_FILE" 2>/dev/null || true
        git add "$SHARED_DIR/math_atlas.json" 2>/dev/null || true
        git add "$SHARED_DIR/installed_tools.json" 2>/dev/null || true
        if git diff --cached --quiet 2>/dev/null; then
            phase_log 12 "Auto-commit: nothing staged"
        else
            git commit -m "growth(tecs-l): cycle $cycle -- ${phase_ok}ok/${phase_fail}fail, delta=$growth_delta" 2>/dev/null || true
            git push origin main 2>/dev/null || true
            phase_log 12 "Auto-commit: committed cycle $cycle"
        fi
    else
        phase_log 12 "Auto-commit: no changes"
    fi
    phase_ok=$((phase_ok + 1))

    # ── Common Phases (paper loop, doc update, domain explore, emergence, bus sync) ──
    run_common_phases "TECS-L" $cycle

    # ── Emit to NEXUS-6 bus ───────────────────────────────────────────
    emit_bus "cycle=$cycle,ok=$phase_ok,fail=$phase_fail,delta=$growth_delta"

    # ── Cycle summary ─────────────────────────────────────────────────
    log "  Summary: $phase_ok/12 phases OK, $phase_fail failed, growth_delta=$growth_delta"
    log ""

    # ── Sleep until next cycle ────────────────────────────────────────
    if [ "$cycle" -lt "$MAX_CYCLES" ]; then
        log "  Sleeping ${INTERVAL}m until next cycle..."
        sleep "$((INTERVAL * 60))"
    fi
done

log "Reached max cycles ($MAX_CYCLES). Exiting."
