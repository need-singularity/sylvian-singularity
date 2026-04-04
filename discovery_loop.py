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
import signal
import subprocess
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
NEXUS_ROOT = os.path.expanduser('~/Dev/nexus6')
GROWTH_BUS = os.path.join(NEXUS_ROOT, 'shared', 'growth_bus.jsonl')

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
        self.consensus = 0  # n lenses agreeing (3-way validation)

    def to_dict(self):
        return {
            'formula': self.formula, 'value': self.value,
            'target': self.target, 'error': self.error,
            'engine': self.engine, 'domains': self.domains,
            'grade': self.grade, 'cycle': self.cycle,
            'timestamp': self.timestamp, 'is_novel': self.is_novel,
            'paper_worthy': self.paper_worthy, 'consensus': self.consensus,
        }

    @classmethod
    def from_dict(cls, d):
        disc = cls(d['formula'], d['value'], d['target'], d['error'],
                   d['engine'], d.get('domains', []), d.get('grade', ''),
                   d.get('cycle', 0), d.get('timestamp'))
        disc.is_novel = d.get('is_novel', True)
        disc.paper_worthy = d.get('paper_worthy', False)
        disc.consensus = d.get('consensus', 0)
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
# DISCOVERY GRAPH (from nexus6 OUROBOROS persistent graph)
# ═════════════════════════════════════════════════════════════════

GRAPH_FILE = os.path.join(RESULTS_DIR, 'discovery_graph.json')


class DiscoveryGraph:
    """Persistent graph where discoveries are nodes and relationships are edges.

    Mirrors nexus6 OUROBOROS graph: nodes = discoveries, edges = derives/supports/bridges.
    Internally stored as adjacency dict for efficient hub detection.
    """

    def __init__(self):
        self.nodes = {}       # id -> {value, grade, engine, cycle, target, formula}
        self.adjacency = {}   # id -> [{neighbor, relation}, ...]
        self._next_id = 0

    def add_node(self, discovery):
        """Add a discovery as a graph node. Returns the node id."""
        node_id = f"d{self._next_id}"
        self._next_id += 1
        self.nodes[node_id] = {
            'id': node_id,
            'value': discovery.value,
            'grade': discovery.grade,
            'engine': discovery.engine,
            'cycle': discovery.cycle,
            'target': discovery.target,
            'formula': discovery.formula,
        }
        self.adjacency[node_id] = []
        return node_id

    def add_edge(self, d1, d2, relation):
        """Add an undirected edge: d1 --relation-- d2.

        Relations:
          'derives'  -- d2 value derived from d1
          'supports' -- both target the same quantity
          'bridges'  -- cross-engine, same value within tolerance
        """
        if d1 not in self.nodes or d2 not in self.nodes:
            return
        edge_fwd = {'neighbor': d2, 'relation': relation}
        edge_rev = {'neighbor': d1, 'relation': relation}
        if edge_fwd not in self.adjacency[d1]:
            self.adjacency[d1].append(edge_fwd)
        if edge_rev not in self.adjacency[d2]:
            self.adjacency[d2].append(edge_rev)

    def auto_link(self, new_id, all_ids):
        """Automatically detect and add relationships for a new node.

        Rules:
          - Same target -> 'supports'
          - Different engines, values within 0.1% -> 'bridges'
          - One node's value appears in another's formula string -> 'derives'
        """
        new_node = self.nodes.get(new_id)
        if not new_node:
            return

        for other_id in all_ids:
            if other_id == new_id:
                continue
            other = self.nodes[other_id]

            # supports: same target
            if (new_node['target'] and other['target']
                    and new_node['target'] == other['target']):
                self.add_edge(new_id, other_id, 'supports')
                continue

            # bridges: different engines, values within 0.1%
            if new_node['engine'] != other['engine']:
                if other['value'] != 0:
                    rel_err = abs(new_node['value'] - other['value']) / abs(other['value'])
                    if rel_err < 0.001:
                        self.add_edge(new_id, other_id, 'bridges')
                        continue

            # derives: one's value string appears in other's formula
            val_str = f"{other['value']:.6g}"
            if len(val_str) >= 3 and val_str in new_node.get('formula', ''):
                self.add_edge(other_id, new_id, 'derives')

    def get_hubs(self, min_edges=3):
        """Return highly-connected nodes (hubs) sorted by edge count descending."""
        hubs = []
        for node_id, edges in self.adjacency.items():
            if len(edges) >= min_edges:
                hubs.append({
                    'id': node_id,
                    'edges': len(edges),
                    'node': self.nodes[node_id],
                    'relations': edges,
                })
        hubs.sort(key=lambda h: -h['edges'])
        return hubs

    def save(self, filepath=None):
        """Save graph to JSON."""
        filepath = filepath or GRAPH_FILE
        with open(filepath, 'w') as f:
            json.dump({
                'nodes': self.nodes,
                'adjacency': self.adjacency,
                'next_id': self._next_id,
            }, f, indent=2, ensure_ascii=False)

    def load(self, filepath=None):
        """Load graph from JSON."""
        filepath = filepath or GRAPH_FILE
        if not os.path.exists(filepath):
            return
        with open(filepath) as f:
            data = json.load(f)
        self.nodes = data.get('nodes', {})
        self.adjacency = data.get('adjacency', {})
        self._next_id = data.get('next_id', 0)


# ═════════════════════════════════════════════════════════════════
# MUTATION ENGINE (from nexus6 ouroboros/mutation.rs)
# ═════════════════════════════════════════════════════════════════

# Domain transfer targets for Strategy 3
TRANSFER_DOMAINS = ['number_theory', 'topology', 'physics', 'information',
                    'biology', 'consciousness', 'quantum', 'thermodynamics']


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

        # Strategy 3: DomainTransfer — cross-engine hypothesis
        # Take a discovery and suggest testing in other domains
        d_domains = set(d.domains) if d.domains else set()
        for domain in TRANSFER_DOMAINS:
            if domain not in d_domains:
                key = f"transfer_{d.target}>{domain}"
                if key not in existing_targets:
                    new_targets[key] = v  # same value, new context

        # Strategy 4: Inversion — reciprocal and negation
        if v != 0:
            key_recip = f"inv_1/{d.target}"
            if key_recip not in existing_targets:
                recip = 1.0 / v
                if 1e-10 < abs(recip) < 1e10:
                    new_targets[key_recip] = recip
            key_neg = f"inv_-{d.target}"
            if key_neg not in existing_targets:
                new_targets[key_neg] = -v

    return new_targets


# ═════════════════════════════════════════════════════════════════
# ENGINE RUNNERS (wrap existing one-shot engines)
# ═════════════════════════════════════════════════════════════════

def run_with_timeout(func, timeout=30):
    """Run function with timeout — prevents engine blocking."""
    def handler(signum, frame):
        raise TimeoutError(f"Engine timed out after {timeout}s")

    old = signal.signal(signal.SIGALRM, handler)
    signal.alarm(timeout)
    try:
        result = func()
    except TimeoutError:
        result = []
        print(f"  ⏰ Timeout after {timeout}s")
    finally:
        signal.alarm(0)
        signal.signal(signal.SIGALRM, old)
    return result


def run_dfs(depth, threshold, augmented_islands=None):
    """Run DFS engine and return discoveries."""
    try:
        import tecsrs  # noqa: F401
    except ImportError:
        print("  [DFS] tecsrs not available, skipping")
        return []

    try:
        from dfs_engine import build_level, check_targets, filter_best, verify_all
    except ImportError as e:
        print(f"  [DFS] Import error: {e}")
        return []

    def _run():
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
                value=m.get('formula_val', m.get('value', 0)),
                target=m.get('target', m.get('target_name', '')),
                error=m.get('error', 1.0),
                engine='dfs',
                grade=m.get('grade', ''),
            )
            discoveries.append(d)
        return discoveries

    try:
        return run_with_timeout(_run, timeout=30)
    except Exception as e:
        print(f"  [DFS] Error: {e}")
        return []


def run_convergence(depth, threshold):
    """Run convergence engine and return discoveries."""
    try:
        from convergence_engine import (
            ConvergenceCluster, strategy_open_search,
            strategy_pair_scan, strategy_target_backtrack,
        )
    except ImportError as e:
        print(f"  [Convergence] Import error: {e}")
        return []

    def _run():
        cluster = ConvergenceCluster(threshold=threshold)
        # pair_scan + backtrack only (open_search too slow for loop timeout)
        strategy_pair_scan(cluster, threshold=threshold)
        strategy_target_backtrack(cluster, threshold=threshold)

        points = cluster.get_convergence_points(min_domains=2)
        discoveries = []
        for pt in points[:JORDAN_J2]:  # cap at J2=24
            best = pt['paths'][0] if pt.get('paths') else {}
            val = float(pt.get('center', pt.get('value', best.get('value', 0))))
            target_name = pt.get('best_target', f"conv_{len(discoveries)}")
            target_err = float(pt.get('target_error', pt.get('spread', 0)))
            domains = pt.get('domains', pt.get('independent_domains', []))
            if isinstance(domains, set):
                domains = list(domains)
            d = Discovery(
                formula=best.get('expr', f"convergence@{val:.6f}"),
                value=val,
                target=target_name,
                error=target_err,
                engine='convergence',
                domains=domains,
                grade='🟩' if len(domains) >= 3 else '🟧',
            )
            discoveries.append(d)
        return discoveries

    try:
        return run_with_timeout(_run, timeout=30)
    except Exception as e:
        print(f"  [Convergence] Error: {e}")
        return []


def run_quantum(depth, threshold):
    """Run quantum formula engine and return discoveries."""
    try:
        from quantum_formula_engine import search as qf_search
    except ImportError as e:
        print(f"  [Quantum] Import error: {e}")
        return []

    def _run():
        matches, total = qf_search(depth=depth, threshold=threshold)
        discoveries = []
        for m in matches[:SIGMA]:  # cap at sigma=12
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

    try:
        return run_with_timeout(_run, timeout=30)
    except Exception as e:
        print(f"  [Quantum] Error: {e}")
        return []


def run_perfect(depth, threshold):
    """Run perfect number engine and return discoveries."""
    try:
        from perfect_number_engine import search as pn_search, build_atom_pool
    except ImportError as e:
        print(f"  [Perfect] Import error: {e}")
        return []

    def _run():
        atoms, _ = build_atom_pool()
        targets_pn = {k: v for k, v in TARGETS.items()
                      if isinstance(v, (int, float)) and 0.001 < abs(v) < 1e6}
        matches, total = pn_search(targets_pn, depth=depth, threshold=threshold)
        discoveries = []
        for m in matches[:SIGMA]:  # cap at sigma=12
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

    try:
        return run_with_timeout(_run, timeout=30)
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
# 3-WAY VALIDATION (nexus6 lens consensus)
# ═════════════════════════════════════════════════════════════════

# Lazy nexus6 import — CDO rule: infra issues don't block work
_nexus6 = None
_nexus6_available = None

def _get_nexus6():
    """Lazy-load nexus6 module. Returns None if unavailable."""
    global _nexus6, _nexus6_available
    if _nexus6_available is not None:
        return _nexus6
    try:
        import nexus6 as _n6
        _nexus6 = _n6
        _nexus6_available = True
        return _nexus6
    except ImportError:
        _nexus6_available = False
        print("  [NEXUS-6] Not available — continuing without lens validation (CDO compliant)")
        return None


def validate_3way(discoveries):
    """3-way validation: run nexus6 lens consensus on each discovery.

    - scan_all on the discovery value (as small array)
    - Count lenses flagging it as significant
    - Set discovery.consensus = agreeing lens count
    - Adjust grade: consensus >= 3 → upgrade, consensus < 2 → downgrade

    Returns discoveries (modified in-place).
    """
    n6 = _get_nexus6()
    if n6 is None:
        return discoveries

    for d in discoveries:
        try:
            # Build a small array around the discovery value for scan
            val = float(d.value)
            arr = np.array([val, val * 1.001, val * 0.999, val])
            scan_result = n6.scan_all(arr)

            # Count lenses that flagged significance
            consensus = 0
            if isinstance(scan_result, dict):
                for lens_name, lens_result in scan_result.items():
                    if isinstance(lens_result, dict):
                        # Check common significance indicators
                        sig = lens_result.get('significant', False)
                        phi = lens_result.get('phi', 0)
                        score = lens_result.get('score', 0)
                        if sig or phi > 0.5 or score > 0.5:
                            consensus += 1
                    elif isinstance(lens_result, (int, float)):
                        if abs(lens_result) > 0.5:
                            consensus += 1

            d.consensus = consensus

            # Grade adjustment based on consensus
            if consensus >= 3 and d.grade == '🟧':
                d.grade = '🟩'  # upgrade: structural → exact (3+ lenses agree)
            elif consensus >= 7:
                d.paper_worthy = True  # high confidence → paper candidate
            elif consensus < 2 and d.grade == '🟩' and d.error > 1e-6:
                d.grade = '🟧'  # downgrade: not enough lens support

        except Exception as e:
            # Individual scan failure doesn't block the loop
            pass

    n_validated = sum(1 for d in discoveries if d.consensus > 0)
    if n_validated:
        print(f"  [3-WAY] Validated {n_validated}/{len(discoveries)} discoveries "
              f"(max consensus: {max((d.consensus for d in discoveries), default=0)})")

    return discoveries


def nexus_scan_batch(discoveries, context="batch"):
    """NEXUS-6 CDO-compliant scan on a batch of discoveries.

    Runs scan_all on the collected values and reports anomalies.
    Used after engine output and after growth.absorb().

    Returns scan summary dict or None if nexus6 unavailable.
    """
    n6 = _get_nexus6()
    if n6 is None or not discoveries:
        return None

    try:
        # Collect all discovery values into an array
        values = [float(d.value) for d in discoveries
                  if isinstance(d.value, (int, float)) and np.isfinite(d.value)]
        if not values:
            return None

        arr = np.array(values)
        scan_result = n6.scan_all(arr)

        # Check for anomalies
        anomaly_count = 0
        if isinstance(scan_result, dict):
            for lens_name, lens_result in scan_result.items():
                if isinstance(lens_result, dict):
                    if lens_result.get('anomaly', False):
                        anomaly_count += 1

        if anomaly_count > 0:
            print(f"  [NEXUS-6] ⚠️  {context}: {anomaly_count} anomalies detected in scan")
        else:
            print(f"  [NEXUS-6] ✓ {context}: scan clean ({len(values)} values, 0 anomalies)")

        return {'context': context, 'n_values': len(values),
                'anomalies': anomaly_count, 'scan': scan_result}

    except Exception as e:
        print(f"  [NEXUS-6] Scan error ({context}): {e}")
        return None


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


def auto_publish(paper_path, cycle):
    """Auto-publish paper draft to Zenodo and OSF."""
    if not paper_path:
        return

    # Check tokens exist
    zenodo_token = os.path.join(SCRIPT_DIR, '.local', 'zenodo_token')
    osf_token = os.path.join(SCRIPT_DIR, '.local', 'osf_token')

    results = {}

    # Zenodo upload
    if os.path.exists(zenodo_token):
        try:
            cmd = [sys.executable, os.path.join(SCRIPT_DIR, 'zenodo', 'batch_upload.py'),
                   '--platform', 'zenodo', '--paper', os.path.basename(paper_path)]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
            results['zenodo'] = 'OK' if result.returncode == 0 else result.stderr[:200]
            print(f"  📤 Zenodo: {'✅' if result.returncode == 0 else '❌'}")
        except Exception as e:
            results['zenodo'] = str(e)
            print(f"  📤 Zenodo: ❌ {e}")

    # OSF upload
    if os.path.exists(osf_token):
        try:
            cmd = [sys.executable, os.path.join(SCRIPT_DIR, 'zenodo', 'batch_upload.py'),
                   '--platform', 'osf', '--paper', os.path.basename(paper_path)]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
            results['osf'] = 'OK' if result.returncode == 0 else result.stderr[:200]
            print(f"  📤 OSF: {'✅' if result.returncode == 0 else '❌'}")
        except Exception as e:
            results['osf'] = str(e)
            print(f"  📤 OSF: ❌ {e}")

    return results


# ═════════════════════════════════════════════════════════════════
# NEXUS-BRIDGE INTEGRATION
# ═════════════════════════════════════════════════════════════════

_bridge = None


def _get_bridge():
    """Lazy-load NexusBridge. Returns None if unavailable."""
    global _bridge
    if _bridge is not None:
        return _bridge
    try:
        bridge_pkg = os.path.join(NEXUS_ROOT, 'nexus-bridge')
        if bridge_pkg not in sys.path:
            sys.path.insert(0, bridge_pkg)
        from bridge import NexusBridge
        _bridge = NexusBridge(NEXUS_ROOT)
        return _bridge
    except Exception:
        return None


def bridge_export(discoveries, cycle):
    """Export high-grade discoveries to nexus-bridge growth_bus for cross-project routing."""
    worthy = [d for d in discoveries if d.grade in ('\U0001f7e9', '\U0001f7e7') and d.is_novel]
    if not worthy:
        return 0

    try:
        os.makedirs(os.path.dirname(GROWTH_BUS), exist_ok=True)
        with open(GROWTH_BUS, 'a') as f:
            for d in worthy:
                entry = {
                    'source': 'TECS-L',
                    'type': 'discovery',
                    'cycle': cycle,
                    'formula': d.formula,
                    'value': d.value,
                    'target': d.target,
                    'grade': d.grade,
                    'engine': d.engine,
                    'consensus': getattr(d, 'consensus', 0),
                    'timestamp': __import__('datetime').datetime.now().isoformat(),
                }
                f.write(__import__('json').dumps(entry, ensure_ascii=False) + '\n')
        print(f"  \U0001f309 Bridge: exported {len(worthy)} discoveries to growth_bus")
        return len(worthy)
    except Exception as e:
        print(f"  \U0001f309 Bridge export error: {e}")
        return 0


def bridge_import():
    """Import discoveries from other projects via growth_bus."""
    if not os.path.exists(GROWTH_BUS):
        return []

    imported = []
    try:
        with open(GROWTH_BUS) as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                entry = json.loads(line)
                if entry.get('source') == 'TECS-L':
                    continue  # skip our own
                if entry.get('type') != 'discovery':
                    continue
                d = Discovery(
                    formula=f"bridge:{entry.get('source', '?')}/{entry.get('formula', '')}",
                    value=entry.get('value', 0),
                    target=f"bridge_{entry.get('target', '')}",
                    error=0.0,
                    engine=f"bridge:{entry.get('source', '?')}",
                    grade=entry.get('grade', '\U0001f7e7'),
                )
                d.consensus = entry.get('consensus', 0)
                imported.append(d)
        if imported:
            print(f"  \U0001f309 Bridge: imported {len(imported)} cross-project discoveries")
    except Exception as e:
        print(f"  \U0001f309 Bridge import error: {e}")
    return imported


def bridge_sync():
    """Trigger nexus-bridge sync after loop completion."""
    bridge = _get_bridge()
    if bridge is None:
        return
    try:
        results = bridge.sync(targets=['readmes', 'math-atlas'], parallel=True)
        ok = sum(1 for v in results.values() if v.get('ok'))
        print(f"  \U0001f309 Bridge sync: {ok}/{len(results)} OK")
    except Exception as e:
        print(f"  \U0001f309 Bridge sync error: {e}")



# ═════════════════════════════════════════════════════════════════
# STATE PERSISTENCE
# ═════════════════════════════════════════════════════════════════

def save_state(cycle, growth, tracker, graph=None):
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
    # Persist discovery graph alongside state
    if graph is not None:
        graph.save()


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

def run_cycle(cycle, growth, tracker, engines=None, auto_paper=False, graph=None):
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

    # Import cross-project discoveries via nexus-bridge
    bridged = bridge_import()
    if bridged:
        bridged = deduplicate(bridged, growth.all_discoveries)
        novel_bridged = [d for d in bridged if d.is_novel]
        if novel_bridged:
            growth.absorb(novel_bridged)
            all_new.extend(novel_bridged)

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

    # NEXUS-6 scan on engine output (CDO compliance)
    nexus_scan_batch(all_new, context=f"cycle-{cycle}-engines")

    # 3-way validation: lens consensus adjusts grades
    all_new = validate_3way(all_new)

    n_novel = sum(1 for d in all_new if d.is_novel)
    n_exact = sum(1 for d in all_new if d.grade == '🟩' and d.is_novel)
    n_struct = sum(1 for d in all_new if d.grade == '🟧' and d.is_novel)

    print(f"\n  CYCLE {cycle} SUMMARY: {len(all_new)} total, "
          f"{n_novel} novel ({n_exact} 🟩, {n_struct} 🟧)")

    # Record convergence
    tracker.record(cycle, len(all_new), n_novel)

    # Growth: absorb discoveries as new constants
    novel_discoveries = [d for d in all_new if d.is_novel]
    growth.absorb(novel_discoveries)

    # NEXUS-6 scan after growth.absorb() — verify injected constants (CDO compliance)
    if growth.injected_constants:
        injected_discs = [Discovery(
            formula=f"injected:{k}", value=v, target=k,
            error=0, engine='growth'
        ) for k, v in growth.injected_constants.items()]
        nexus_scan_batch(injected_discs, context=f"cycle-{cycle}-injected")

    # Update discovery graph: add nodes and auto-link relationships
    if graph is not None:
        existing_ids = list(graph.nodes.keys())
        new_ids = []
        for d in all_new:
            nid = graph.add_node(d)
            new_ids.append(nid)
        for nid in new_ids:
            graph.auto_link(nid, existing_ids + new_ids)
        # Report hubs
        hubs = graph.get_hubs(min_edges=3)
        if hubs:
            top = hubs[0]
            print(f"  [GRAPH] {len(graph.nodes)} nodes, "
                  f"{sum(len(e) for e in graph.adjacency.values()) // 2} edges, "
                  f"top hub: {top['node']['target']} ({top['edges']} edges)")

    # Persist
    append_discoveries(all_new)
    save_state(cycle, growth, tracker, graph=graph)

    # Export discoveries to nexus-bridge growth_bus
    bridge_export(all_new, cycle)

    # Paper generation + auto-publish
    if auto_paper:
        paper_path = maybe_generate_paper(growth, cycle)
        if paper_path:
            auto_publish(paper_path, cycle)

    # Periodic dashboard report
    print_dashboard(cycle, growth, tracker, graph, engines)

    return all_new


REPORT_FILE = os.path.join(RESULTS_DIR, 'report.txt')


def print_dashboard(cycle, growth, tracker, graph, engines_used):
    """Print periodic dashboard report (anima-style). Also saves to report.txt."""
    now = datetime.now().strftime('%Y-%m-%d %H:%M')
    stage = growth.stage['name']
    total = tracker.total_discoveries
    novel = tracker.total_novel
    injected = len(growth.injected_constants)
    n_nodes = len(graph.nodes) if graph else 0
    n_edges = sum(len(e) for e in graph.adjacency.values()) // 2 if graph else 0
    hubs = graph.get_hubs(min_edges=3) if graph else []
    status = tracker.status

    # Grade counts
    all_d = growth.all_discoveries
    n_exact = sum(1 for d in all_d if d.grade == '🟩')
    n_struct = sum(1 for d in all_d if d.grade == '🟧')
    n_weak = sum(1 for d in all_d if d.grade == '⚪')

    # Stage progress bar
    stages = [s['name'] for s in GrowthEngine.STAGES]
    stage_bars = []
    for i, sn in enumerate(stages):
        if i < growth.stage_idx:
            stage_bars.append(f'{sn[:4]} ████ ✅')
        elif i == growth.stage_idx:
            stage_bars.append(f'{sn[:4]} ██░░ 🔄')
        else:
            stage_bars.append(f'{sn[:4]} ░░░░   ')

    # Discovery trend (last 6 cycles)
    hist = tracker.history[-6:]
    max_d = max((h[1] for h in hist), default=1) or 1
    trend_lines = []
    for h in hist:
        bar_len = int(h[1] / max_d * 20)
        trend_lines.append(f'    C{h[0]:>2} |{"█" * bar_len}{"░" * (20 - bar_len)}| {h[1]:>3} ({h[2]} novel)')

    # Engine stats
    eng_counts = defaultdict(int)
    for d in all_d:
        eng_counts[d.engine] += 1

    # Bridge stats
    bridge = _get_bridge()
    bridge_info = ""
    if bridge:
        try:
            bs = bridge.status()
            bridge_info = f'{bs["stage"]} | {bs["growth_points"]:,} pts | {bs["active"]} active'
        except Exception:
            bridge_info = "connected"

    w = 65
    print(f'\n  ┌{"─" * w}┐')
    print(f'  │  🔬 TECS-L Discovery Loop — {now:<{w - 34}}│')
    print(f'  ├{"─" * w}┤')
    print(f'  │{"":>{w}}│')
    print(f'  │  ■ 발견 루프{"":>{w - 15}}│')
    print(f'  │  Cycle: {cycle} | Stage: {stage} | Status: {status:<{w - 38}}│')
    print(f'  │  Discoveries: {total} (🟩{n_exact} 🟧{n_struct} ⚪{n_weak}) | Novel: {novel:<{w - 58 - len(str(total)) - len(str(n_exact)) - len(str(n_struct)) - len(str(n_weak)) - len(str(novel))}}│')
    print(f'  │  Injected: {injected} | Graph: {n_nodes}n/{n_edges}e | Hubs: {len(hubs):<{w - 50}}│')
    # Stage progress
    print(f'  │  {"─" * (w - 2)}│')
    print(f'  │  📈 발달 단계:{"":>{w - 17}}│')
    row1 = '  '.join(stage_bars[:3])
    row2 = '  '.join(stage_bars[3:])
    print(f'  │  {row1:<{w - 2}}│')
    print(f'  │  {row2:<{w - 2}}│')
    # Discovery trend
    print(f'  │{"":>{w}}│')
    print(f'  │  📊 발견 추이:{"":>{w - 17}}│')
    for tl in trend_lines:
        print(f'  │  {tl:<{w - 2}}│')
    if not trend_lines:
        print(f'  │  {"(no data yet)":<{w - 2}}│')
    # Engine breakdown
    print(f'  │{"":>{w}}│')
    print(f'  │  ⚙️  엔진별:{"":>{w - 14}}│')
    for eng, cnt in sorted(eng_counts.items(), key=lambda x: -x[1]):
        print(f'  │    {eng:<15} {cnt:>4} discoveries{"":>{w - 28 - len(eng)}}│')
    # Bridge
    if bridge_info:
        print(f'  │{"":>{w}}│')
        print(f'  │  🌉 NEXUS-BRIDGE: {bridge_info:<{w - 20}}│')
    print(f'  │{"":>{w}}│')
    print(f'  └{"─" * w}┘')

    # Auto-save to file for cross-session access
    import io, contextlib
    buf = io.StringIO()
    # Re-render into buffer (reuse locals already computed)
    lines = []
    lines.append(f'  ┌{"─" * w}┐')
    lines.append(f'  │  🔬 TECS-L Discovery Loop — {now:<{w - 34}}│')
    lines.append(f'  ├{"─" * w}┤')
    lines.append(f'  │  Cycle: {cycle} | Stage: {stage} | Status: {status}')
    lines.append(f'  │  Discoveries: {total} (🟩{n_exact} 🟧{n_struct} ⚪{n_weak}) | Novel: {novel}')
    lines.append(f'  │  Injected: {injected} | Graph: {n_nodes}n/{n_edges}e | Hubs: {len(hubs)}')
    lines.append(f'  │  Stages: {" → ".join(stage_bars)}')
    for tl in trend_lines:
        lines.append(f'  │  {tl}')
    for eng, cnt in sorted(eng_counts.items(), key=lambda x: -x[1]):
        lines.append(f'  │  {eng}: {cnt}')
    if bridge_info:
        lines.append(f'  │  🌉 NEXUS-BRIDGE: {bridge_info}')
    lines.append(f'  └{"─" * w}┘')
    try:
        with open(REPORT_FILE, 'w') as f:
            f.write('\n'.join(lines) + '\n')
    except Exception:
        pass


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


def cmd_report():
    """Print current loop status from saved state (no loop needed)."""
    state = load_state()
    if not state:
        print("  No loop state found. Run the loop first.")
        return

    growth = GrowthEngine()
    growth.stage_idx = state.get('stage_idx', 0)
    growth.injected_constants = state.get('injected_constants', {})

    tracker = ConvergenceTracker()
    tracker.history = state.get('convergence_history', [])

    graph = DiscoveryGraph()
    graph.load()

    # Reconstruct discovery list from JSONL
    if os.path.exists(DISCOVERIES_FILE):
        with open(DISCOVERIES_FILE) as f:
            for line in f:
                line = line.strip()
                if line:
                    growth.all_discoveries.append(Discovery.from_dict(json.loads(line)))

    cycle = state.get('cycle', 0)
    engines = list({d.engine for d in growth.all_discoveries}) or ['convergence']
    print_dashboard(cycle, growth, tracker, graph, engines)


def main():
    # Handle subcommands: report
    if len(sys.argv) > 1 and sys.argv[1] == 'report':
        cmd_report()
        return

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
    graph = DiscoveryGraph()

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
        graph.load()  # load persisted graph if it exists

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
                                engines=args.engines, auto_paper=args.paper,
                                graph=graph)

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
    n_edges = sum(len(e) for e in graph.adjacency.values()) // 2
    print(f"  Graph: {len(graph.nodes)} nodes, {n_edges} edges, "
          f"{len(graph.get_hubs())} hubs")

    # Force paper if requested and not generated yet
    if args.paper:
        paper_path = maybe_generate_paper(growth, len(tracker.history), force=True)
        if paper_path:
            auto_publish(paper_path, len(tracker.history))

    # Sync nexus-bridge (readmes + atlas)
    bridge_sync()

    print(f"\n  Results: {RESULTS_DIR}")
    print(f"  Discoveries: {DISCOVERIES_FILE}")


if __name__ == '__main__':
    main()
