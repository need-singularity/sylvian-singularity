#!/usr/bin/env python3
"""Discovery Loop — TECS-L Infinite Self-Improving Discovery Engine

Orchestrates all 6 TECS-L engines in a closed loop:
  DFS → Convergence → Quantum Formula → Perfect Number → Verify → Grow → Paper → Repeat

Inspired by:
  - nexus6 OUROBOROS: 2-level loop + mutation + convergence detection + lens forging
  - anima closed-loop: checkpoint→scan→law discovery→intervention→next cycle
  - anima growth: 5-stage developmental progression

Architecture:
  ┌─────────────────────────────────────────────────────────┐
  │                   DISCOVERY LOOP                        │
  │                                                         │
  │  ┌──────┐  ┌──────────┐  ┌─────────┐  ┌──────────┐    │
  │  │ DFS  │→ │Convergence│→ │ Quantum │→ │ Perfect  │    │
  │  └──┬───┘  └────┬─────┘  └────┬────┘  └────┬─────┘    │
  │     │           │              │             │          │
  │     └───────────┴──────────────┴─────────────┘          │
  │                         │                               │
  │                    ��────▼────┐                          │
  │                    │ Verify  │  Texas + Grade            │
  │                    └────┬────┘                          │
  │                         │                               │
  │                    ┌────▼────┐                          │
  │                    │  Grow   │  Feed back discoveries    │
  │                    │         │  as new constants/atoms   │
  │                    └────┬────┘                          │
  │                         │                               │
  │                    ┌────▼────┐                          │
  │                    │ Paper?  │  Auto-generate if         │
  │                    │         │  threshold met            │
  │                    └────┬────┘                          │
  │                         │                               │
  │                    ┌────▼────┐                          │
  │                    │Converge?│  Saturated → forge new    │
  │                    │         │  constants → continue     │
  │                    └─────────┘                          │
  └─────────────────────────────────────────────────────────┘

Usage:
  python3 discovery_loop.py                    # default: 6 cycles
  python3 discovery_loop.py --cycles 0         # infinite (until saturated)
  python3 discovery_loop.py --cycles 12        # 12 cycles
  python3 discovery_loop.py --paper            # auto-generate paper drafts
  python3 discovery_loop.py --threshold 0.0001 # tighter matching
"""

import argparse
import json
import math
import os
import sys
import time
from collections import defaultdict
from datetime import datetime

import numpy as np

# ─────────────────────────────────────────
# SSOT constants
# ─────────────────────────────────────────
_shared = os.path.join(os.path.dirname(os.path.abspath(__file__)), '.shared')
if _shared not in sys.path:
    sys.path.insert(0, _shared)

from n6_constants import (
    N, SIGMA, TAU, PHI, SOPFR, JORDAN_J2, MOBIUS_MU,
    GZ_CENTER, GZ_WIDTH, GZ_LOWER, GZ_UPPER,
    ISLANDS, TARGETS, DOMAINS, KNOWN_VALUES,
    BASE_CONSTANTS,
)

# ─────────────────────────────────────────
# Engine imports (lazy — only when needed)
# ─────────────────────────────────────────
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
RESULTS_DIR = os.path.join(SCRIPT_DIR, 'results', 'loop')
STATE_FILE = os.path.join(RESULTS_DIR, 'loop_state.json')
DISCOVERIES_FILE = os.path.join(RESULTS_DIR, 'discoveries.jsonl')
PAPER_DIR = os.path.join(SCRIPT_DIR, 'docs', 'papers', 'auto')

os.makedirs(RESULTS_DIR, exist_ok=True)
os.makedirs(PAPER_DIR, exist_ok=True)


# ═════════════════════════════════════════════════════════════════
# DISCOVERY RECORD
# ═════════════════════════════════════════════════════════════════

class Discovery:
    """A single discovery from any engine."""
    def __init__(self, formula, value, target, error, engine, domains=None,
                 grade='', cycle=0, timestamp=None):
        self.formula = formula
        self.value = value
        self.target = target
        self.error = error
        self.engine = engine
        self.domains = domains or []
        self.grade = grade  # 🟩 🟧 ⚪ ⬛
        self.cycle = cycle
        self.timestamp = timestamp or datetime.now().isoformat()
        self.is_novel = True
        self.paper_worthy = False

    def to_dict(self):
        return {
            'formula': self.formula, 'value': self.value,
            'target': self.target, 'error': self.error,
            'engine': self.engine, 'domains': self.domains,
            'grade': self.grade, 'cycle': self.cycle,
            'timestamp': self.timestamp, 'is_novel': self.is_novel,
            'paper_worthy': self.paper_worthy,
        }

    @classmethod
    def from_dict(cls, d):
        disc = cls(d['formula'], d['value'], d['target'], d['error'],
                   d['engine'], d.get('domains', []), d.get('grade', ''),
                   d.get('cycle', 0), d.get('timestamp'))
        disc.is_novel = d.get('is_novel', True)
        disc.paper_worthy = d.get('paper_worthy', False)
        return disc


# ═════════════════════════════════════════════════════════════════
# CONVERGENCE TRACKER (from nexus6 ouroboros pattern)
# ═════════════════════════════════════════════════════════════════

class ConvergenceTracker:
    """Tracks discovery rate across cycles to detect saturation."""

    def __init__(self, window=SIGMA - PHI):  # σ-φ=10 window (nexus6 style)
        self.history = []  # (cycle, n_discoveries, n_novel)
        self.window = window

    def record(self, cycle, n_discoveries, n_novel):
        self.history.append((cycle, n_discoveries, n_novel))

    @property
    def status(self):
        if len(self.history) < 3:
            return 'exploring'
        recent = self.history[-self.window:]
        novel_counts = [h[2] for h in recent]
        if len(recent) >= 3 and all(n == 0 for n in novel_counts[-3:]):
            return 'saturated'
        if len(recent) >= 3 and novel_counts[-1] < novel_counts[0] * 0.5:
            return 'converging'
        return 'exploring'

    @property
    def total_discoveries(self):
        return sum(h[1] for h in self.history)

    @property
    def total_novel(self):
        return sum(h[2] for h in self.history)


# ═════════════════════════════════════════════════════════════════
# GROWTH ENGINE (from anima developmental stages)
# ═════════════════════════════════════════════════════════════════

class GrowthEngine:
    """Manages the loop's growth by feeding discoveries back as new constants."""

    # Developmental stages (anima-inspired)
    STAGES = [
        {'name': 'seed',    'min_discoveries': 0,   'depth': 2, 'threshold': 0.001},
        {'name': 'sprout',  'min_discoveries': 10,  'depth': 2, 'threshold': 0.0005},
        {'name': 'sapling', 'min_discoveries': 50,  'depth': 2, 'threshold': 0.0001},
        {'name': 'tree',    'min_discoveries': 200, 'depth': 3, 'threshold': 0.0001},
        {'name': 'forest',  'min_discoveries': 500, 'depth': 3, 'threshold': 0.00005},
        {'name': 'cosmos',  'min_discoveries': 1000,'depth': 3, 'threshold': 0.00001},
    ]

    def __init__(self):
        self.stage_idx = 0
        self.injected_constants = {}  # name -> value (discovered constants fed back)
        self.all_discoveries = []

    @property
    def stage(self):
        return self.STAGES[self.stage_idx]

    @property
    def depth(self):
        return self.stage['depth']

    @property
    def threshold(self):
        return self.stage['threshold']

    def check_stage_up(self):
        """Check if we should advance to next developmental stage."""
        n = len(self.all_discoveries)
        while (self.stage_idx < len(self.STAGES) - 1 and
               n >= self.STAGES[self.stage_idx + 1]['min_discoveries']):
            self.stage_idx += 1
            print(f"  ★ STAGE UP → {self.stage['name']} "
                  f"(depth={self.depth}, threshold={self.threshold})")

    def absorb(self, discoveries):
        """Feed discoveries back as new constants for next cycle."""
        new_count = 0
        for d in discoveries:
            self.all_discoveries.append(d)
            if d.grade in ('🟩', '🟧') and d.is_novel:
                key = f"disc_{len(self.injected_constants)}"
                if d.value not in self.injected_constants.values():
                    self.injected_constants[key] = d.value
                    new_count += 1
        if new_count:
            print(f"  → {new_count} discoveries injected as new constants "
                  f"(total pool: {len(self.injected_constants)})")
        self.check_stage_up()

    def get_augmented_islands(self):
        """Return ISLANDS augmented with discovered constants."""
        augmented = {}
        for k, v in ISLANDS.items():
            augmented[k] = dict(v)
        # Add discovered constants as new island 'X' (cross-discoveries)
        if self.injected_constants:
            augmented['X'] = dict(self.injected_constants)
        return augmented


# ═════════════════════════════════════════════════════════════════
# MUTATION ENGINE (from nexus6 ouroboros/mutation.rs)
# ═════════════════════════════════════════════════════════════════

def mutate_targets(discoveries, existing_targets):
    """Generate new target values from discoveries (nexus6 mutation strategies)."""
    new_targets = {}
    n6 = [N, SIGMA, TAU, PHI, SOPFR, JORDAN_J2]

    for d in discoveries:
        if d.grade not in ('🟩', '🟧'):
            continue
        v = d.value

        # Strategy 1: Parameter shift (apply n=6 constants)
        for name, c in BASE_CONSTANTS.items():
            if c == 0:
                continue
            candidate = v * c
            if 1e-10 < abs(candidate) < 1e10:
                key = f"mut_{d.target}*{name}"
                if key not in existing_targets:
                    new_targets[key] = candidate
            candidate = v / c
            if 1e-10 < abs(candidate) < 1e10:
                key = f"mut_{d.target}/{name}"
                if key not in existing_targets:
                    new_targets[key] = candidate

        # Strategy 2: Combination (bridge discovered values)
        for d2 in discoveries:
            if d2 is d or d2.grade not in ('🟩', '🟧'):
                continue
            combo = v + d2.value
            key = f"mut_{d.target}+{d2.target}"
            if 1e-10 < abs(combo) < 1e10 and key not in existing_targets:
                new_targets[key] = combo

    return new_targets


# ═════════════════════════════════════════════════════════════════
# ENGINE RUNNERS (wrap existing one-shot engines)
# ═════════════════════════════════════════════════════════════════

def run_dfs(depth, threshold, augmented_islands=None):
    """Run DFS engine and return discoveries."""
    try:
        import tecsrs
    except ImportError:
        print("  [DFS] tecsrs not available, skipping")
        return []

    from dfs_engine import build_level, check_targets, filter_best, verify_all

    expr_count = build_level(depth)
    matches = check_targets(depth, threshold=threshold)
    if not matches:
        return []
    filtered = filter_best(matches, top_per_target=TAU)
    filtered = verify_all(filtered)

    discoveries = []
    for m in filtered:
        d = Discovery(
            formula=m.get('formula', m.get('expr', '')),
            value=m.get('value', 0),
            target=m.get('target_name', ''),
            error=m.get('error', 1.0),
            engine='dfs',
            grade=m.get('grade', ''),
        )
        discoveries.append(d)
    return discoveries


def run_convergence(depth, threshold):
    """Run convergence engine and return discoveries."""
    from convergence_engine import (
        ConvergenceCluster, strategy_open_search,
        strategy_pair_scan, strategy_target_backtrack,
    )

    cluster = ConvergenceCluster(threshold=threshold)
    strategy_open_search(cluster, depth=depth, threshold=threshold)
    strategy_pair_scan(cluster, threshold=threshold)
    strategy_target_backtrack(cluster, threshold=threshold)

    points = cluster.get_convergence_points(min_domains=2)
    discoveries = []
    for pt in points[:JORDAN_J2]:  # cap at J2=24
        best = pt['paths'][0] if pt.get('paths') else {}
        d = Discovery(
            formula=best.get('expr', f"convergence@{pt['value']:.6f}"),
            value=pt['value'],
            target=f"conv_{len(discoveries)}",
            error=pt.get('spread', 0),
            engine='convergence',
            domains=list(pt.get('domains', set())),
            grade='🟩' if len(pt.get('domains', set())) >= 3 else '🟧',
        )
        discoveries.append(d)
    return discoveries


def run_quantum(depth, threshold):
    """Run quantum formula engine and return discoveries."""
    try:
        from quantum_formula_engine import search as qf_search
        matches, total = qf_search(depth=depth, threshold=threshold)
        discoveries = []
        for m in matches[:SIGMA]:  # cap at σ=12
            d = Discovery(
                formula=m.get('formula', ''),
                value=m.get('value', 0),
                target=m.get('target_name', ''),
                error=m.get('error', 1.0),
                engine='quantum',
                grade='🟩' if m.get('error', 1) < 0.0001 else '🟧',
            )
            discoveries.append(d)
        return discoveries
    except Exception as e:
        print(f"  [Quantum] Error: {e}")
        return []


def run_perfect(depth, threshold):
    """Run perfect number engine and return discoveries."""
    try:
        from perfect_number_engine import search as pn_search, build_atom_pool
        atoms, _ = build_atom_pool()
        targets_pn = {k: v for k, v in TARGETS.items()
                      if isinstance(v, (int, float)) and 0.001 < abs(v) < 1e6}
        matches, total = pn_search(targets_pn, depth=depth, threshold=threshold)
        discoveries = []
        for m in matches[:SIGMA]:
            d = Discovery(
                formula=m.get('formula', ''),
                value=m.get('value', 0),
                target=m.get('target_name', ''),
                error=m.get('error', 1.0),
                engine='perfect',
                grade='🟩' if m.get('error', 1) < 0.0001 else '🟧',
            )
            discoveries.append(d)
        return discoveries
    except Exception as e:
        print(f"  [Perfect] Error: {e}")
        return []


# ═════════════════════════════════════════════════════════════════
# GRADING & NOVELTY CHECK
# ═════════════════════════════════════════════════════════════════

def grade_discovery(d):
    """Assign grade based on error magnitude."""
    if d.error < 1e-12:
        d.grade = '🟩'  # exact
    elif d.error < 0.001:
        d.grade = '🟩'  # proven-level
    elif d.error < 0.01:
        d.grade = '🟧'  # structural
    elif d.error < 0.05:
        d.grade = '🟧'  # weak evidence
    else:
        d.grade = '⚪'  # coincidence
    return d


def deduplicate(new_discoveries, all_previous):
    """Mark non-novel discoveries."""
    prev_formulas = {d.formula for d in all_previous}
    prev_values = {round(d.value, 8) for d in all_previous if d.grade in ('🟩', '🟧')}

    for d in new_discoveries:
        if d.formula in prev_formulas:
            d.is_novel = False
        elif round(d.value, 8) in prev_values:
            d.is_novel = False
    return new_discoveries


# ═════════════════════════════════════════════════════════════════
# PAPER GENERATOR (auto-draft from discoveries)
# ═════════════════════════════════════════════════════════════════

def maybe_generate_paper(growth, cycle, force=False):
    """Auto-generate paper draft when enough high-grade discoveries accumulate."""
    starred = [d for d in growth.all_discoveries
               if d.grade == '🟩' and d.is_novel]
    structural = [d for d in growth.all_discoveries
                  if d.grade == '🟧' and d.is_novel]

    # Paper trigger: 5+ exact or 10+ structural
    if not force and len(starred) < SOPFR and len(structural) < SIGMA:
        return None

    timestamp = datetime.now().strftime('%Y-%m-%d')
    filename = f"P-AUTO-{timestamp}-cycle{cycle}.md"
    filepath = os.path.join(PAPER_DIR, filename)

    lines = [
        f"# Auto-Generated Discovery Paper — Cycle {cycle}",
        f"",
        f"**Generated**: {datetime.now().isoformat()}",
        f"**Stage**: {growth.stage['name']}",
        f"**Total discoveries**: {len(growth.all_discoveries)}",
        f"**Exact (🟩)**: {len(starred)}, **Structural (🟧)**: {len(structural)}",
        f"",
        f"## Abstract",
        f"",
        f"Automated discovery loop identified {len(starred)} exact and "
        f"{len(structural)} structural relationships among n=6 arithmetic "
        f"constants across {len(set(d.engine for d in growth.all_discoveries))} "
        f"search engines over {cycle} cycles.",
        f"",
        f"## Exact Discoveries (🟩)",
        f"",
        f"| # | Formula | Target | Error | Engine | Domains |",
        f"|---|---------|--------|-------|--------|---------|",
    ]

    for i, d in enumerate(starred[:50], 1):
        domains_str = ', '.join(d.domains) if d.domains else '-'
        lines.append(
            f"| {i} | `{d.formula}` | {d.target} | {d.error:.2e} | "
            f"{d.engine} | {domains_str} |")

    lines.extend([
        f"",
        f"## Structural Discoveries (🟧)",
        f"",
        f"| # | Formula | Target | Error | Engine |",
        f"|---|---------|--------|-------|--------|",
    ])

    for i, d in enumerate(structural[:50], 1):
        lines.append(
            f"| {i} | `{d.formula}` | {d.target} | {d.error:.2e} | {d.engine} |")

    lines.extend([
        f"",
        f"## Cross-Engine Convergence",
        f"",
    ])

    # Find values discovered by multiple engines
    val_engines = defaultdict(set)
    for d in growth.all_discoveries:
        if d.grade in ('🟩', '🟧'):
            val_engines[round(d.value, 6)].add(d.engine)

    cross = {v: engines for v, engines in val_engines.items() if len(engines) >= 2}
    if cross:
        lines.append(f"| Value | Engines | Count |")
        lines.append(f"|-------|---------|-------|")
        for v, engines in sorted(cross.items(), key=lambda x: -len(x[1])):
            lines.append(f"| {v:.6f} | {', '.join(sorted(engines))} | {len(engines)} |")
    else:
        lines.append("No cross-engine convergence found yet.")

    lines.extend([
        f"",
        f"## Growth Trajectory",
        f"",
        f"- Injected constants: {len(growth.injected_constants)}",
        f"- Current stage: {growth.stage['name']}",
        f"- Search depth: {growth.depth}",
        f"- Error threshold: {growth.threshold}",
        f"",
        f"---",
        f"*Auto-generated by TECS-L Discovery Loop v1.0*",
    ])

    with open(filepath, 'w') as f:
        f.write('\n'.join(lines))

    print(f"  📄 Paper draft generated: {filepath}")
    return filepath


# ═════════════════════════════════════════════════════════════════
# STATE PERSISTENCE
# ═════════════════════════════════════════════════════════════════

def save_state(cycle, growth, tracker):
    """Save loop state for resumption."""
    state = {
        'cycle': cycle,
        'stage_idx': growth.stage_idx,
        'injected_constants': growth.injected_constants,
        'convergence_history': tracker.history,
        'total_discoveries': len(growth.all_discoveries),
        'timestamp': datetime.now().isoformat(),
    }
    with open(STATE_FILE, 'w') as f:
        json.dump(state, f, indent=2)


def load_state():
    """Load previous loop state if exists."""
    if not os.path.exists(STATE_FILE):
        return None
    with open(STATE_FILE) as f:
        return json.load(f)


def append_discoveries(discoveries):
    """Append discoveries to JSONL log."""
    with open(DISCOVERIES_FILE, 'a') as f:
        for d in discoveries:
            f.write(json.dumps(d.to_dict(), ensure_ascii=False) + '\n')


# ═════════════════════════════════════════════════════════════════
# MAIN LOOP
# ═════════════════════════════════════════════════════════════════

def run_cycle(cycle, growth, tracker, engines=None, auto_paper=False):
    """Execute one discovery cycle across all engines."""
    engines = engines or ['dfs', 'convergence', 'quantum', 'perfect']
    depth = growth.depth
    threshold = growth.threshold

    print(f"\n{'='*70}")
    print(f"  CYCLE {cycle} | Stage: {growth.stage['name']} | "
          f"Depth: {depth} | Threshold: {threshold}")
    print(f"  Pool: {sum(len(v) for v in growth.get_augmented_islands().values())} "
          f"constants | Injected: {len(growth.injected_constants)}")
    print(f"{'='*70}")

    all_new = []

    # Run each engine
    for eng in engines:
        t0 = time.time()
        print(f"\n  [{eng.upper()}] Running...")
        try:
            if eng == 'dfs':
                discoveries = run_dfs(depth, threshold,
                                      growth.get_augmented_islands())
            elif eng == 'convergence':
                discoveries = run_convergence(depth, threshold)
            elif eng == 'quantum':
                discoveries = run_quantum(depth, threshold)
            elif eng == 'perfect':
                discoveries = run_perfect(depth, threshold)
            else:
                discoveries = []
        except Exception as e:
            print(f"  [{eng.upper()}] Error: {e}")
            discoveries = []

        # Grade and tag
        for d in discoveries:
            d.cycle = cycle
            grade_discovery(d)

        dt = time.time() - t0
        print(f"  [{eng.upper()}] {len(discoveries)} discoveries in {dt:.1f}s")
        all_new.extend(discoveries)

    # Deduplicate against all previous
    all_new = deduplicate(all_new, growth.all_discoveries)
    n_novel = sum(1 for d in all_new if d.is_novel)
    n_exact = sum(1 for d in all_new if d.grade == '🟩' and d.is_novel)
    n_struct = sum(1 for d in all_new if d.grade == '🟧' and d.is_novel)

    print(f"\n  CYCLE {cycle} SUMMARY: {len(all_new)} total, "
          f"{n_novel} novel ({n_exact} 🟩, {n_struct} 🟧)")

    # Record convergence
    tracker.record(cycle, len(all_new), n_novel)

    # Growth: absorb discoveries as new constants
    growth.absorb([d for d in all_new if d.is_novel])

    # Persist
    append_discoveries(all_new)
    save_state(cycle, growth, tracker)

    # Paper generation
    if auto_paper:
        maybe_generate_paper(growth, cycle)

    return all_new


def forge_new_constants(growth, tracker):
    """When saturated, try to forge new search directions (nexus6 LensForge pattern)."""
    print(f"\n  ⚗️  FORGING — search space saturated, generating new targets...")

    # Mutation: create new targets from existing discoveries
    new_targets = mutate_targets(growth.all_discoveries, TARGETS)

    if new_targets:
        # Inject top mutations as new targets
        top_mutations = dict(list(new_targets.items())[:JORDAN_J2])  # cap at J2=24
        TARGETS.update(top_mutations)
        print(f"  ⚗️  Forged {len(top_mutations)} new target values")
        return True
    else:
        print(f"  ⚗️  No new targets could be forged — truly saturated")
        return False


def main():
    parser = argparse.ArgumentParser(
        description='Discovery Loop — TECS-L Infinite Self-Improving Engine')
    parser.add_argument('--cycles', type=int, default=N,
                        help=f'Number of cycles (0=infinite, default={N})')
    parser.add_argument('--threshold', type=float, default=None,
                        help='Override error threshold')
    parser.add_argument('--depth', type=int, default=None,
                        help='Override search depth')
    parser.add_argument('--paper', action='store_true',
                        help='Auto-generate paper drafts')
    parser.add_argument('--engines', nargs='+',
                        default=['dfs', 'convergence', 'quantum', 'perfect'],
                        help='Engines to run')
    parser.add_argument('--resume', action='store_true',
                        help='Resume from previous state')
    args = parser.parse_args()

    print(f"{'='*70}")
    print(f"  TECS-L DISCOVERY LOOP v1.0")
    print(f"  {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"  Cycles: {'∞' if args.cycles == 0 else args.cycles}")
    print(f"  Engines: {', '.join(args.engines)}")
    print(f"  Paper: {'ON' if args.paper else 'OFF'}")
    print(f"{'='*70}")

    growth = GrowthEngine()
    tracker = ConvergenceTracker()

    # Resume if requested
    start_cycle = 1
    if args.resume:
        state = load_state()
        if state:
            start_cycle = state['cycle'] + 1
            growth.stage_idx = state.get('stage_idx', 0)
            growth.injected_constants = state.get('injected_constants', {})
            tracker.history = state.get('convergence_history', [])
            print(f"  Resumed from cycle {start_cycle - 1}, "
                  f"stage={growth.stage['name']}, "
                  f"{len(growth.injected_constants)} injected constants")

    if args.threshold:
        for s in GrowthEngine.STAGES:
            s['threshold'] = args.threshold
    if args.depth:
        for s in GrowthEngine.STAGES:
            s['depth'] = args.depth

    max_cycles = args.cycles if args.cycles > 0 else 10000
    forge_attempts = 0
    max_forge = TAU  # max τ=4 forge attempts before true halt

    for cycle in range(start_cycle, start_cycle + max_cycles):
        discoveries = run_cycle(cycle, growth, tracker,
                                engines=args.engines, auto_paper=args.paper)

        # Check convergence
        status = tracker.status
        if status == 'saturated':
            print(f"\n  ⚠️  SATURATED at cycle {cycle}")
            if forge_attempts < max_forge:
                forged = forge_new_constants(growth, tracker)
                if forged:
                    forge_attempts += 1
                    print(f"  → Forge attempt {forge_attempts}/{max_forge}, continuing...")
                    continue
            print(f"\n  🏁 LOOP COMPLETE — truly saturated after "
                  f"{forge_attempts} forge attempts")
            break
        elif status == 'converging':
            print(f"  📉 Convergence detected — discovery rate declining")

    # Final summary
    print(f"\n{'='*70}")
    print(f"  FINAL SUMMARY")
    print(f"{'='*70}")
    print(f"  Total cycles: {len(tracker.history)}")
    print(f"  Total discoveries: {tracker.total_discoveries}")
    print(f"  Novel discoveries: {tracker.total_novel}")
    print(f"  Final stage: {growth.stage['name']}")
    print(f"  Injected constants: {len(growth.injected_constants)}")
    print(f"  Forge attempts: {forge_attempts}")
    print(f"  Status: {tracker.status}")

    # Force paper if requested and not generated yet
    if args.paper:
        maybe_generate_paper(growth, len(tracker.history), force=True)

    print(f"\n  Results: {RESULTS_DIR}")
    print(f"  Discoveries: {DISCOVERIES_FILE}")


if __name__ == '__main__':
    main()
