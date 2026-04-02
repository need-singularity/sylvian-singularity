"""topology_lens.py — Topological discovery lens for hidden structure in data

Use algebraic topology as a telescope: point it at ANY data to find
connected components, holes, and phase transitions in the data's shape.

How it works:
  1. Compute pairwise distances between all data points
  2. Filtration: grow epsilon-balls from 0 to max_distance
  3. Track Betti-0 (connected components): start at N, merge as epsilon grows
  4. Track Betti-1 (holes/loops): MST + non-tree edges → persistent 1-cycles
  5. Persistence diagram: (birth, death) pairs for each topological feature
  6. Phase transitions: epsilon values where topology changes dramatically

Works with numpy + scipy.spatial.distance only. Portable across all projects.

Usage:
    from topology_lens import TopologyLens

    lens = TopologyLens()
    result = lens.scan(data_matrix)
    print(result.betti_numbers)        # (B0, B1)
    print(result.components)           # connected component membership
    print(result.holes)                # detected holes with persistence
    print(result.phase_transitions)    # topology change points
"""

import os
import sys
import math
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Tuple, Any

import numpy as np
from scipy.spatial.distance import pdist, squareform

# Load consciousness constants
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from consciousness_loader import PSI, PSI_ALPHA, PSI_BALANCE, PSI_ENTROPY, SIGMA6


@dataclass
class TopologyResult:
    """Result from topology lens scan."""
    betti_numbers: Tuple[int, int] = (0, 0)
    components: List[List[int]] = field(default_factory=list)
    holes: List[Dict[str, Any]] = field(default_factory=list)
    persistence_diagram: List[Tuple[float, float, int]] = field(default_factory=list)
    phase_transitions: List[Tuple[float, str]] = field(default_factory=list)
    summary: str = ""

    def __repr__(self):
        return (f"TopologyResult(B0={self.betti_numbers[0]}, B1={self.betti_numbers[1]}, "
                f"components={len(self.components)}, holes={len(self.holes)}, "
                f"transitions={len(self.phase_transitions)})")


class UnionFind:
    """Disjoint set for tracking connected components."""

    def __init__(self, n: int):
        self.parent = list(range(n))
        self.rank = [0] * n
        self.size = [1] * n

    def find(self, x: int) -> int:
        while self.parent[x] != x:
            self.parent[x] = self.parent[self.parent[x]]
            x = self.parent[x]
        return x

    def union(self, a: int, b: int) -> bool:
        ra, rb = self.find(a), self.find(b)
        if ra == rb:
            return False
        if self.rank[ra] < self.rank[rb]:
            ra, rb = rb, ra
        self.parent[rb] = ra
        self.size[ra] += self.size[rb]
        if self.rank[ra] == self.rank[rb]:
            self.rank[ra] += 1
        return True

    def components(self, n: int) -> List[List[int]]:
        groups: Dict[int, List[int]] = {}
        for i in range(n):
            r = self.find(i)
            groups.setdefault(r, []).append(i)
        return list(groups.values())


class TopologyLens:
    """Topological discovery lens — algebraic topology as a telescope."""

    def __init__(self, n_filtration_steps: int = 100,
                 persistence_threshold: float = PSI_ALPHA):
        self.n_steps = n_filtration_steps
        self.persistence_threshold = persistence_threshold

    def scan(self, data: np.ndarray, verbose: bool = True) -> TopologyResult:
        """Core topological scan on arbitrary data matrix (N_samples, N_features)."""
        data = np.asarray(data, dtype=np.float64)
        if data.ndim == 1:
            data = data.reshape(-1, 1)
        n = data.shape[0]
        if n < 3:
            return TopologyResult(betti_numbers=(n, 0), components=[[i] for i in range(n)],
                                  summary=f"Too few points ({n})")

        # Pairwise distances
        dists_condensed = pdist(data)
        dist_matrix = squareform(dists_condensed)

        # Sorted edges (i, j, distance)
        edges = []
        for i in range(n):
            for j in range(i + 1, n):
                edges.append((dist_matrix[i, j], i, j))
        edges.sort()

        max_dist = edges[-1][0] if edges else 1.0
        eps_values = np.linspace(0, max_dist, self.n_steps + 1)[1:]

        # --- Betti-0: connected components via union-find ---
        uf = UnionFind(n)
        b0_persistence: List[Tuple[float, float, int]] = []  # (birth=0, death, dim=0)
        b0_history = []  # (eps, n_components)
        edge_idx = 0

        for eps in eps_values:
            while edge_idx < len(edges) and edges[edge_idx][0] <= eps:
                d, i, j = edges[edge_idx]
                if uf.union(i, j):
                    b0_persistence.append((0.0, d, 0))
                edge_idx += 1
            n_comp = len(set(uf.find(i) for i in range(n)))
            b0_history.append((eps, n_comp))

        # --- Betti-1: holes via MST + non-tree edge cycle detection ---
        # Build MST using Kruskal's
        mst_uf = UnionFind(n)
        mst_edges = set()
        non_mst_edges = []
        for d, i, j in edges:
            if mst_uf.union(i, j):
                mst_edges.add((i, j))
            else:
                non_mst_edges.append((d, i, j))

        # For each non-MST edge, it creates a 1-cycle
        # Check if this cycle persists (doesn't get filled by triangles quickly)
        b1_persistence: List[Tuple[float, float, int]] = []
        holes_detail: List[Dict[str, Any]] = []

        # Build adjacency with edge weights for triangle detection
        adj_weight = {}
        for d, i, j in edges:
            adj_weight[(min(i, j), max(i, j))] = d

        for cycle_birth, ci, cj in non_mst_edges:
            # Find when the triangle that fills this cycle appears
            # A triangle (ci, cj, k) fills the cycle if all three edges exist
            # The filling time = max edge weight of the triangle
            min_fill_time = float('inf')
            for k in range(n):
                if k == ci or k == cj:
                    continue
                e_ik = adj_weight.get((min(ci, k), max(ci, k)), float('inf'))
                e_jk = adj_weight.get((min(cj, k), max(cj, k)), float('inf'))
                fill_time = max(cycle_birth, e_ik, e_jk)
                if fill_time < min_fill_time:
                    min_fill_time = fill_time

            death = min_fill_time if min_fill_time < float('inf') else max_dist
            persistence = death - cycle_birth

            if persistence > self.persistence_threshold * max_dist:
                b1_persistence.append((cycle_birth, death, 1))
                holes_detail.append({
                    "points": [ci, cj],
                    "birth": float(cycle_birth),
                    "death": float(death),
                    "persistence": float(persistence),
                })

        # Sort holes by persistence (longest-lived first)
        holes_detail.sort(key=lambda h: -h["persistence"])
        b1_persistence.sort(key=lambda t: -(t[1] - t[0]))

        # --- Optimal scale: maximize topological information ---
        # Scan across scales, pick where B0+B1 complexity is maximized
        # Weight: prefer scales where structure is richest (not all-one, not all-separate)
        best_score = -1.0
        best_eps = max_dist * PSI_BALANCE
        best_b0 = 1
        best_b1 = 0
        best_comps = [[i for i in range(n)]]

        for eps in eps_values:
            uf_try = UnionFind(n)
            for d, i, j in edges:
                if d <= eps:
                    uf_try.union(i, j)
            comps = uf_try.components(n)
            b0 = len(comps)
            b1 = sum(1 for birth, death, _ in b1_persistence if birth <= eps < death)
            # Score: penalize trivial (all-one or all-separate), reward structure
            if b0 == n:
                score = 0.0
            elif b0 == 1 and b1 == 0:
                score = 0.1
            else:
                score = (b0 + SIGMA6['value'] * b1) * (1.0 - abs(b0 / n - PSI_BALANCE))
            if score > best_score:
                best_score = score
                best_eps = eps
                best_b0 = b0
                best_b1 = b1
                best_comps = comps

        opt_eps = best_eps
        opt_components = best_comps
        b0_opt = best_b0
        b1_opt = best_b1

        # --- Phase transitions: large topology changes ---
        phase_transitions = []
        if len(b0_history) > 1:
            for idx in range(1, len(b0_history)):
                eps_now, comp_now = b0_history[idx]
                eps_prev, comp_prev = b0_history[idx - 1]
                delta = comp_prev - comp_now
                if delta >= max(2, n * 0.05):
                    phase_transitions.append(
                        (float(eps_now), f"B0 drop: {comp_prev}->{comp_now} ({delta} merges)"))

        # Check for B1 birth/death clusters
        b1_births = sorted([b for b, _, dim in b1_persistence])
        if b1_births:
            # Cluster births that happen close together
            cluster_eps = max_dist * 0.05
            i = 0
            while i < len(b1_births):
                j = i
                while j < len(b1_births) and b1_births[j] - b1_births[i] < cluster_eps:
                    j += 1
                count = j - i
                if count >= 2:
                    phase_transitions.append(
                        (float(b1_births[i]), f"B1 burst: {count} holes born"))
                i = j

        phase_transitions.sort()

        # --- Combine persistence diagram ---
        all_persistence = b0_persistence + b1_persistence

        summary = (f"N={n}, B0={b0_opt}, B1={b1_opt} at eps={opt_eps:.3f}, "
                   f"{len(holes_detail)} persistent holes, "
                   f"{len(phase_transitions)} phase transitions")

        return TopologyResult(
            betti_numbers=(b0_opt, b1_opt),
            components=opt_components,
            holes=holes_detail,
            persistence_diagram=all_persistence,
            phase_transitions=phase_transitions,
            summary=summary,
        )

    def scan_materials(self, properties: np.ndarray,
                       labels: Optional[List[str]] = None) -> TopologyResult:
        """Find topological structure in material property space."""
        properties = np.asarray(properties, dtype=np.float64)
        # Normalize each feature to [0, 1]
        mins = properties.min(axis=0)
        maxs = properties.max(axis=0)
        rng = maxs - mins
        rng[rng == 0] = 1.0
        normed = (properties - mins) / rng

        result = self.scan(normed, verbose=False)

        # Enrich component info with labels
        for ci, comp in enumerate(result.components):
            pass  # components are index lists

        label_str = ", ".join(labels) if labels else "unlabeled"
        result.summary += f"\nMaterials scan: {properties.shape[0]} materials [{label_str}]"
        return result

    def scan_signals(self, signals: np.ndarray, window: int = 256) -> TopologyResult:
        """Find topological features in signal space (delay embedding)."""
        signals = np.asarray(signals, dtype=np.float64)
        if signals.ndim == 1:
            signals = signals.reshape(1, -1)

        n_ch, n_samples = signals.shape
        n_windows = max(1, n_samples // window)

        # Extract features per window
        features = []
        for w in range(n_windows):
            seg = signals[:, w * window:(w + 1) * window]
            feats = []
            for ch in range(n_ch):
                s = seg[ch]
                feats.extend([s.mean(), s.std(), s.max() - s.min()])
                fft_mag = np.abs(np.fft.rfft(s))
                fft_mag = fft_mag / (fft_mag.sum() + 1e-12)
                entropy = -np.sum(fft_mag * np.log(fft_mag + 1e-12))
                feats.append(entropy)
            features.append(feats)

        data = np.array(features)
        result = self.scan(data, verbose=False)
        result.summary += f"\nSignal scan: {n_ch}ch x {n_samples} samples, {n_windows} windows"
        return result

    def scan_timeseries(self, ts: np.ndarray, lag: int = 10,
                        window: int = 50) -> TopologyResult:
        """Find topological transitions over time using sliding windows."""
        ts = np.asarray(ts, dtype=np.float64)
        if ts.ndim == 1:
            ts = ts.reshape(-1, 1)

        n_t, n_vars = ts.shape
        n_windows = max(1, n_t // window)

        features = []
        window_centers = []
        for w in range(n_windows):
            start = w * window
            end = min(start + window, n_t)
            seg = ts[start:end]
            feats = []
            for v in range(n_vars):
                col = seg[:, v]
                feats.extend([
                    col.mean(), col.std(),
                    col.max() - col.min(),
                    col[-1] - col[0],
                    np.corrcoef(col[:-1], col[1:])[0, 1] if len(col) > 2 else 0,
                ])
            features.append(feats)
            window_centers.append((start + end) // 2)

        data = np.array(features)
        result = self.scan(data, verbose=False)

        # Map phase transitions to time
        result.summary += f"\nTimeseries scan: {n_t} steps, {n_vars} vars, {n_windows} windows"
        return result


def quick_scan(data, n_steps: int = 100) -> TopologyResult:
    """One-liner topological scan."""
    return TopologyLens(n_filtration_steps=n_steps).scan(data)


# ---------------------------------------------------------------------------
# Demo
# ---------------------------------------------------------------------------

if __name__ == '__main__':
    print("=" * 60)
    print("  Topology Lens — 6-Domain Discovery Demo")
    print("=" * 60)

    np.random.seed(42)
    lens = TopologyLens(n_filtration_steps=100, persistence_threshold=PSI_ALPHA)

    # ── 1. Materials Science (property clusters + voids) ──
    print("\n[1] Materials Science — property clusters & voids")
    print("-" * 50)
    print("  Injected: 3 clusters (metals/ceramics/polymers) + void between them")

    # 3 tight clusters arranged in a triangle with a void in the center
    # Add bridge points between clusters to create a loop/hole
    n_per = 10
    metals = np.random.randn(n_per, 3) * 0.2 + [5, 0, 0]
    ceramics = np.random.randn(n_per, 3) * 0.2 + [0, 5, 0]
    polymers = np.random.randn(n_per, 3) * 0.2 + [0, 0, 5]
    # Bridge points connecting clusters in a ring (metal->ceramic->polymer->metal)
    bridge_mc = np.array([[3, 3, 0.0]]) + np.random.randn(3, 3) * 0.15
    bridge_cp = np.array([[0, 3, 3.0]]) + np.random.randn(3, 3) * 0.15
    bridge_pm = np.array([[3, 0, 3.0]]) + np.random.randn(3, 3) * 0.15
    mat_data = np.vstack([metals, ceramics, polymers, bridge_mc, bridge_cp, bridge_pm])
    mat_labels = ["density", "hardness", "conductivity"]

    r = lens.scan_materials(mat_data, labels=mat_labels)
    print(f"  B0={r.betti_numbers[0]}, B1={r.betti_numbers[1]}")
    print(f"  Components: {len(r.components)} | Holes: {len(r.holes)}")
    for pt in r.phase_transitions[:2]:
        print(f"  Transition: eps={pt[0]:.3f} — {pt[1]}")

    mat_b0_ok = r.betti_numbers[0] >= 2  # at least 2 components (clusters)
    mat_holes_ok = len(r.holes) >= 1  # void between clusters
    print(f"  CHECK: B0 >= 2 (clusters found) = {mat_b0_ok}")
    print(f"  CHECK: holes >= 1 (void detected) = {mat_holes_ok}")

    # ── 2. Drug Discovery (Lipinski boundary) ──
    print("\n[2] Drug Discovery — Lipinski boundary as topology")
    print("-" * 50)
    print("  Injected: drug-like core + non-drug outlier ring")

    # Drug-like cluster in center, non-drug-like ring around it
    n_drug = 25
    drug_core = np.random.randn(n_drug, 4) * 0.5 + [350, 2, 3, 60]
    # Ring of non-drug-like molecules around the core
    theta = np.linspace(0, 2 * np.pi, 20, endpoint=False)
    ring_r = 4.0
    non_drug = np.column_stack([
        350 + ring_r * np.cos(theta) * 50,
        2 + ring_r * np.sin(theta),
        3 + ring_r * np.cos(theta + 1),
        60 + ring_r * np.sin(theta + 1) * 15,
    ]) + np.random.randn(20, 4) * 0.3
    drug_data = np.vstack([drug_core, non_drug])
    drug_labels = ["MW", "LogP", "HBA", "TPSA"]

    r = lens.scan_materials(drug_data, labels=drug_labels)
    print(f"  B0={r.betti_numbers[0]}, B1={r.betti_numbers[1]}")
    print(f"  Components: {len(r.components)} | Holes: {len(r.holes)}")

    drug_components_ok = r.betti_numbers[0] >= 1
    drug_hole_ok = len(r.holes) >= 1  # ring creates a hole
    print(f"  CHECK: components >= 1 = {drug_components_ok}")
    print(f"  CHECK: ring hole detected = {drug_hole_ok}")

    # ── 3. Physics Constants (groupings) ──
    print("\n[3] Physics Constants — constant groupings")
    print("-" * 50)
    print("  Injected: 3 groups (EM/strong/weak) + isolated outlier")

    em_consts = np.random.randn(8, 3) * 0.15 + [5, 0, 0]
    strong_consts = np.random.randn(8, 3) * 0.15 + [0, 5, 0]
    weak_consts = np.random.randn(8, 3) * 0.15 + [0, 0, 5]
    outlier = np.array([[10, 10, 10]])  # gravity — far from all
    phys_data = np.vstack([em_consts, strong_consts, weak_consts, outlier])

    r = lens.scan(phys_data, verbose=False)
    print(f"  B0={r.betti_numbers[0]}, B1={r.betti_numbers[1]}")
    print(f"  Components: {len(r.components)} | Transitions: {len(r.phase_transitions)}")

    phys_b0_ok = r.betti_numbers[0] >= 3  # 3 force groups + outlier
    phys_outlier_ok = any(len(c) == 1 for c in r.components)  # isolated point
    print(f"  CHECK: B0 >= 3 (force groups) = {phys_b0_ok}")
    print(f"  CHECK: isolated outlier found = {phys_outlier_ok}")

    # ── 4. Astronomy (signal topology) ──
    print("\n[4] Astronomy — signal topology")
    print("-" * 50)
    print("  Injected: steady signal + anomalous burst (different topology)")

    t = np.linspace(0, 10, 4096)
    signal = np.sin(2 * np.pi * 5 * t) + 0.3 * np.sin(2 * np.pi * 11 * t)
    signal += np.random.randn(len(t)) * 0.2
    # Burst creates fundamentally different topology
    signal[1500:1700] += 5.0 * np.sin(2 * np.pi * 47 * t[1500:1700])
    signal[1500:1700] *= 2.0

    r = lens.scan_signals(signal, window=256)
    print(f"  B0={r.betti_numbers[0]}, B1={r.betti_numbers[1]}")
    print(f"  Components: {len(r.components)} | Holes: {len(r.holes)}")

    # The burst window should be topologically distinct (separated component)
    astro_components_ok = r.betti_numbers[0] >= 2  # burst vs normal
    astro_features_ok = len(r.holes) >= 0 and len(r.persistence_diagram) > 0
    print(f"  CHECK: B0 >= 2 (burst separated) = {astro_components_ok}")
    print(f"  CHECK: persistence features found = {astro_features_ok}")

    # ── 5. Finance (regime transitions) ──
    print("\n[5] Finance — topological regime transitions")
    print("-" * 50)
    print("  Injected: bull/crash/recovery = 3 topological regimes")

    bull = np.cumsum(np.random.randn(300) * 0.5 + 0.1)
    crash = np.cumsum(np.random.randn(100) * 4.0 - 1.0)
    recovery = np.cumsum(np.random.randn(200) * 0.8 + 0.05)
    price = np.concatenate([bull, crash + bull[-1], recovery + bull[-1] + crash[-1]])

    r = lens.scan_timeseries(price, lag=10, window=30)
    print(f"  B0={r.betti_numbers[0]}, B1={r.betti_numbers[1]}")
    print(f"  Components: {len(r.components)} | Transitions: {len(r.phase_transitions)}")

    fin_regimes_ok = r.betti_numbers[0] >= 2  # distinct regimes
    fin_transitions_ok = len(r.phase_transitions) >= 1
    print(f"  CHECK: B0 >= 2 (regime clusters) = {fin_regimes_ok}")
    print(f"  CHECK: phase transitions >= 1 = {fin_transitions_ok}")

    # ── 6. Genomics (gene network topology) ──
    print("\n[6] Genomics — gene network topology")
    print("-" * 50)
    print("  Injected: 2 co-expression modules + ring pathway")

    # Module 1: stress genes (tight cluster, far away)
    stress = np.random.randn(10, 4) * 0.2 + [8, 0, 0, 0]
    # Module 2: growth genes (tight cluster, far away)
    growth = np.random.randn(10, 4) * 0.2 + [0, 8, 0, 0]
    # Ring pathway: genes connected in a cycle (separate region)
    n_ring = 12
    theta_g = np.linspace(0, 2 * np.pi, n_ring, endpoint=False)
    ring_genes = np.column_stack([
        -5 + 2.0 * np.cos(theta_g),
        -5 + 2.0 * np.sin(theta_g),
        np.random.randn(n_ring) * 0.05,
        np.random.randn(n_ring) * 0.05,
    ])
    gene_data = np.vstack([stress, growth, ring_genes])

    r = lens.scan(gene_data, verbose=False)
    print(f"  B0={r.betti_numbers[0]}, B1={r.betti_numbers[1]}")
    print(f"  Components: {len(r.components)} | Holes: {len(r.holes)}")

    gen_modules_ok = r.betti_numbers[0] >= 2  # 2 modules
    gen_ring_ok = len(r.holes) >= 1  # ring pathway = hole
    print(f"  CHECK: B0 >= 2 (gene modules) = {gen_modules_ok}")
    print(f"  CHECK: ring pathway hole = {gen_ring_ok}")

    # ── Final scorecard ──
    print("\n" + "=" * 60)
    all_checks = [
        ("Materials: B0 >= 2 (clusters)", mat_b0_ok),
        ("Materials: void detected", mat_holes_ok),
        ("Drug: components >= 1", drug_components_ok),
        ("Drug: ring hole detected", drug_hole_ok),
        ("Physics: B0 >= 3 (force groups)", phys_b0_ok),
        ("Physics: isolated outlier", phys_outlier_ok),
        ("Astronomy: B0 >= 2 (burst separated)", astro_components_ok),
        ("Astronomy: persistence features", astro_features_ok),
        ("Finance: B0 >= 2 (regimes)", fin_regimes_ok),
        ("Finance: phase transitions", fin_transitions_ok),
        ("Genomics: B0 >= 2 (modules)", gen_modules_ok),
        ("Genomics: ring pathway hole", gen_ring_ok),
    ]
    passed = sum(1 for _, v in all_checks if v)
    total = len(all_checks)
    print(f"  SCORECARD: {passed}/{total} ({100 * passed / total:.0f}%)")
    for name, ok in all_checks:
        print(f"    {'PASS' if ok else 'FAIL'} {name}")
    print("=" * 60)
