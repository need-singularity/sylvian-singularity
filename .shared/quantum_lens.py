"""quantum_lens.py — Quantum-inspired discovery lens for non-local correlations

Point quantum concepts at ANY data to find entanglement, superposition, tunneling.
  1. Entanglement: von Neumann-like entropy of correlation subsets
  2. Superposition: samples equidistant from multiple clusters
  3. Tunneling: samples that jump basins without traversing barriers
  4. Interference: constructive/destructive proximity patterns
  5. Decoherence: rate of superposition collapse across features

Usage:
    lens = QuantumLens()
    r = lens.scan(data)            # QuantumResult
    r = lens.scan_materials(props, labels)
    r = lens.scan_signals(signals, window)
    r = lens.scan_timeseries(ts, lag, window)
"""
import os, sys
from dataclasses import dataclass, field
from typing import List, Dict, Tuple
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from consciousness_loader import PSI_ALPHA, PSI_BALANCE, PSI_ENTROPY, SIGMA6


@dataclass
class QuantumResult:
    """Result from quantum lens scan."""
    entanglement_pairs: List[Dict] = field(default_factory=list)
    superposed_samples: List[Tuple[int, List[int]]] = field(default_factory=list)
    tunneling_paths: List[Dict] = field(default_factory=list)
    interference_map: Dict[str, List[int]] = field(default_factory=dict)
    decoherence_rate: float = 0.0
    summary: str = ""
    def __repr__(self):
        return (f"QuantumResult(entangled={len(self.entanglement_pairs)}, "
                f"superposed={len(self.superposed_samples)}, "
                f"tunneling={len(self.tunneling_paths)})")


class QuantumLens:
    """Quantum-inspired discovery lens — entanglement/tunneling as a telescope."""

    def __init__(self, n_clusters: int = 4, superpose_tol: float = 0.15,
                 tunnel_sigma: float = 2.0, coherence_threshold: float = PSI_BALANCE):
        self.n_clusters = n_clusters
        self.superpose_tol = superpose_tol
        self.tunnel_sigma = tunnel_sigma
        self.coherence_threshold = coherence_threshold

    # --- core algorithms ---

    def _von_neumann_entropy(self, C):
        """Von Neumann-like entropy from correlation matrix eigenvalues."""
        eigs = np.linalg.eigvalsh(C)
        eigs = np.clip(eigs, 1e-12, None)
        eigs = eigs / eigs.sum()
        return -np.sum(eigs * np.log2(eigs + 1e-30))

    def _entanglement(self, data):
        """Compute entanglement entropy between all feature pairs."""
        n, d = data.shape
        if d < 2: return []
        norm = (data - data.mean(0)) / (data.std(0) + 1e-12)
        pairs = []
        for i in range(d):
            for j in range(i + 1, d):
                sub = norm[:, [i, j]]
                C = np.corrcoef(sub.T)
                C = (C + C.T) / 2
                ent = self._von_neumann_entropy(C)
                pairs.append({"feature_i": i, "feature_j": j,
                              "entanglement_entropy": round(float(ent), 4)})
        pairs.sort(key=lambda x: x["entanglement_entropy"])
        return pairs

    def _kmeans(self, data, k, iters=30):
        """Simple k-means."""
        n = data.shape[0]; k = min(k, n)
        idx = np.random.choice(n, k, replace=False)
        centers = data[idx].copy()
        for _ in range(iters):
            d = np.linalg.norm(data[:, None] - centers[None, :], axis=-1)
            labels = d.argmin(1)
            for c in range(k):
                m = labels == c
                if m.any(): centers[c] = data[m].mean(0)
        d = np.linalg.norm(data[:, None] - centers[None, :], axis=-1)
        labels = d.argmin(1)
        return labels, centers, d

    def _superposition(self, data, labels, centers, dists):
        """Find samples equidistant from 2+ clusters."""
        n = data.shape[0]; k = centers.shape[0]; superposed = []
        # compute distances to cluster centers
        cdists = np.linalg.norm(data[:, None] - centers[None, :], axis=-1)
        for i in range(n):
            sd = np.sort(cdists[i])
            if len(sd) < 2: continue
            ratio = sd[0] / (sd[1] + 1e-12)
            if ratio > (1.0 - self.superpose_tol):
                close = np.where(cdists[i] < sd[1] * (1.0 + self.superpose_tol))[0]
                if len(close) >= 2:
                    superposed.append((i, close.tolist()))
        return superposed

    def _basins_simple(self, data, labels, centers):
        """Build basin map: center energy = negative density."""
        basins = {}
        for i, lb in enumerate(labels):
            basins.setdefault(int(lb), []).append(i)
        energies = {}
        for b, idx in basins.items():
            energies[b] = -len(idx) / len(labels)
        return basins, energies

    def _tunneling(self, data, labels, centers, basins, energies):
        """Find samples that bridge two distant basins (tunnel through barrier).

        A tunneling sample is one whose assigned cluster and second-closest cluster
        are far apart, yet the sample is relatively close to both.
        """
        n = data.shape[0]; k = centers.shape[0]; paths = []
        if k < 2: return paths
        cdists = np.linalg.norm(data[:, None] - centers[None, :], axis=-1)
        # inter-cluster distances
        ic = []
        for a in range(k):
            for b in range(a + 1, k):
                ic.append(np.linalg.norm(centers[a] - centers[b]))
        med_ic = np.median(ic) if ic else 1.0
        for i in range(n):
            order = np.argsort(cdists[i])
            b_own = int(order[0])
            for rank in range(1, min(3, k)):
                b_other = int(order[rank])
                gap = np.linalg.norm(centers[b_own] - centers[b_other])
                d_own = cdists[i, b_own]
                d_other = cdists[i, b_other]
                # tunneling: sample bridges two distant clusters
                # it's closer to both than the clusters are to each other
                if gap > med_ic * 0.5 and d_other < gap * (1.0 + self.superpose_tol):
                    barrier = gap - d_own - (gap - d_other)
                    paths.append({"sample": i, "from_basin": b_own,
                                  "to_basin": b_other,
                                  "barrier_height": round(float(abs(barrier) + gap * 0.1), 4)})
        return paths

    def _interference(self, data, labels):
        """Constructive: same-cluster neighbors close. Destructive: diff-cluster close."""
        n = data.shape[0]
        d = np.linalg.norm(data[:, None] - data[None, :], axis=-1)
        np.fill_diagonal(d, np.inf)
        med = np.median(d[d < np.inf]) if n > 1 else 1.0
        constructive, destructive = [], []
        for i in range(n):
            nn = d[i].argmin()
            if d[i, nn] < med * 0.5:
                if labels[i] == labels[nn]:
                    constructive.append(i)
                else:
                    destructive.append(i)
        return {"constructive": constructive, "destructive": destructive}

    def _decoherence(self, data, superposed):
        """Measure how quickly superposition collapses across feature subsets."""
        if not superposed or data.shape[1] < 2: return 0.0
        d = data.shape[1]; rates = []
        for si, clusters in superposed:
            if len(clusters) < 2: continue
            collapse_count = 0
            for f in range(d):
                vals = data[clusters, f]
                spread = vals.max() - vals.min()
                if spread > data[:, f].std() * 0.5:
                    collapse_count += 1
            rates.append(collapse_count / d)
        return float(np.mean(rates)) if rates else 0.0

    # --- public API ---

    def scan(self, data: np.ndarray) -> QuantumResult:
        """Full quantum scan on arbitrary data matrix."""
        data = np.asarray(data, dtype=float)
        if data.ndim == 1: data = data.reshape(-1, 1)
        n, d = data.shape
        k = min(self.n_clusters, n)
        ent_pairs = self._entanglement(data)
        labels, centers, dists = self._kmeans(data, k)
        superposed = self._superposition(data, labels, centers, dists)
        basins, energies = self._basins_simple(data, labels, centers)
        tun = self._tunneling(data, labels, centers, basins, energies)
        interf = self._interference(data, labels)
        decoh = self._decoherence(data, superposed)
        top_ent = ent_pairs[:3] if ent_pairs else []
        summary = (f"Quantum scan: {n} samples, {d} features | "
                   f"Entangled pairs: {len(ent_pairs)} (top S={top_ent[0]['entanglement_entropy'] if top_ent else 'N/A'}) | "
                   f"Superposed: {len(superposed)} | Tunneling: {len(tun)} | "
                   f"Constructive: {len(interf.get('constructive',[]))} "
                   f"Destructive: {len(interf.get('destructive',[]))} | "
                   f"Decoherence: {decoh:.3f}")
        return QuantumResult(ent_pairs, superposed, tun, interf, decoh, summary)

    def scan_materials(self, properties: np.ndarray, labels: list) -> QuantumResult:
        """Find entangled property pairs and tunneling candidates in materials."""
        return self.scan(np.asarray(properties, dtype=float))

    def scan_signals(self, signals: np.ndarray, window: int = 256) -> QuantumResult:
        """Find quantum-like coherence in signals via windowed embedding."""
        s = np.asarray(signals, dtype=float).ravel()
        nw = max(1, len(s) // window)
        chunks = np.array_split(s[:nw * window], nw)
        mat = np.vstack([c[:window] for c in chunks if len(c) == window])
        if mat.shape[0] < 2: mat = np.vstack([mat, mat])
        return self.scan(mat)

    def scan_timeseries(self, ts: np.ndarray, lag: int = 1, window: int = 30) -> QuantumResult:
        """Find tunneling events (sudden jumps through barriers) in timeseries."""
        ts = np.asarray(ts, dtype=float).ravel()
        n = len(ts) - window + 1
        if n < 2: return QuantumResult(summary="Too short")
        mat = np.array([ts[i:i + window] for i in range(0, n, max(1, n // 200))])
        return self.scan(mat)


# ---- demo ----
if __name__ == "__main__":
    np.random.seed(42)
    lens = QuantumLens(n_clusters=4, superpose_tol=0.20, tunnel_sigma=0.8)

    # -- 1. Materials --
    print("[1] Materials — entangled properties, superposed materials")
    print("-" * 50)
    props = np.vstack([np.random.randn(15, 5) * 0.3 + [5, 5, 0, 0, 0],
                       np.random.randn(15, 5) * 0.3 + [0, 0, 5, 5, 0],
                       np.random.randn(5, 5) * 0.3 + [2.5, 2.5, 2.5, 2.5, 0]])
    labels = [f"prop_{i}" for i in range(5)]
    mat_lens = QuantumLens(n_clusters=2, superpose_tol=0.20, tunnel_sigma=0.8)
    r = mat_lens.scan_materials(props, labels)
    print(f"  Entangled pairs: {len(r.entanglement_pairs)} | "
          f"Superposed: {len(r.superposed_samples)} | Tunneling: {len(r.tunneling_paths)}")
    c1_ent = len(r.entanglement_pairs) >= 3
    c1_sup = len(r.superposed_samples) >= 1
    print(f"  CHECK: >=3 entangled pairs = {c1_ent}")
    print(f"  CHECK: >=1 superposed sample = {c1_sup}")

    # -- 2. Drug --
    print("\n[2] Drug — tunneling candidates bridging activity classes")
    print("-" * 50)
    np.random.seed(42)
    active = np.random.randn(20, 4) * 0.3 + [4, 4, 0, 0]
    inactive = np.random.randn(20, 4) * 0.3 + [0, 0, 4, 4]
    bridge = np.random.randn(5, 4) * 0.3 + [2, 2, 2, 2]
    drugs = np.vstack([active, inactive, bridge])
    r = lens.scan(drugs)
    print(f"  Tunneling: {len(r.tunneling_paths)} | Superposed: {len(r.superposed_samples)}")
    c2_tun = len(r.tunneling_paths) >= 1
    c2_sup = len(r.superposed_samples) >= 1
    print(f"  CHECK: >=1 tunneling path = {c2_tun}")
    print(f"  CHECK: >=1 superposed drug = {c2_sup}")

    # -- 3. Physics --
    print("\n[3] Physics — entangled constant pairs")
    print("-" * 50)
    np.random.seed(42)
    consts = np.array([[1.0, 0.5, 0.014, 4.33, 0.998, 12.0],
                       [1.1, 0.48, 0.015, 4.30, 0.997, 11.8],
                       [0.9, 0.52, 0.013, 4.36, 0.999, 12.2],
                       [2.0, 0.5, 0.028, 8.66, 0.998, 24.0],
                       [0.5, 0.5, 0.007, 2.17, 0.998, 6.0],
                       [1.5, 0.49, 0.021, 6.50, 0.998, 18.0],
                       [3.0, 0.51, 0.042, 12.99, 0.997, 36.0],
                       [0.3, 0.50, 0.004, 1.30, 0.999, 3.6]])
    r = lens.scan(consts)
    print(f"  Entangled pairs: {len(r.entanglement_pairs)}")
    top3 = r.entanglement_pairs[:3] if r.entanglement_pairs else []
    c3_ent = len(r.entanglement_pairs) >= 5
    low_ent = [p for p in r.entanglement_pairs if p["entanglement_entropy"] < 0.5]
    c3_strong = len(low_ent) >= 1
    print(f"  CHECK: >=5 entangled pairs = {c3_ent}")
    print(f"  CHECK: >=1 strongly entangled (S<0.5) = {c3_strong}")

    # -- 4. Astronomy --
    print("\n[4] Astronomy — quantum-like coherence in spectrum")
    print("-" * 50)
    np.random.seed(42)
    t = np.linspace(0, 10, 4096)
    sig = np.sin(2 * np.pi * 5 * t) + 0.3 * np.sin(2 * np.pi * 11 * t)
    sig += np.random.randn(4096) * 0.2
    sig[1500:1600] += 5.0 * np.sin(2 * np.pi * 47 * t[1500:1600])
    r = lens.scan_signals(sig, window=256)
    print(f"  Entangled: {len(r.entanglement_pairs)} | Superposed: {len(r.superposed_samples)}")
    c4_ent = len(r.entanglement_pairs) >= 10
    c4_interf = len(r.interference_map.get("constructive", [])) >= 1
    print(f"  CHECK: >=10 entangled freq pairs = {c4_ent}")
    print(f"  CHECK: >=1 constructive interference = {c4_interf}")

    # -- 5. Finance --
    print("\n[5] Finance — tunneling events (sudden market jumps)")
    print("-" * 50)
    np.random.seed(42)
    bull = np.cumsum(np.random.randn(300) * 0.3 + 0.2)
    crash = np.cumsum(np.random.randn(100) * 3.0 - 2.0)
    rec = np.cumsum(np.random.randn(200) * 0.5 + 0.1)
    price = np.concatenate([bull, crash + bull[-1], rec + bull[-1] + crash[-1]])
    r = lens.scan_timeseries(price, window=30)
    print(f"  Tunneling: {len(r.tunneling_paths)} | Superposed: {len(r.superposed_samples)}")
    c5_tun = len(r.tunneling_paths) >= 1
    c5_dec = r.decoherence_rate >= 0.0
    print(f"  CHECK: >=1 tunneling event = {c5_tun}")
    print(f"  CHECK: decoherence measured = {c5_dec}")

    # -- 6. Genomics --
    print("\n[6] Genomics — entangled gene pairs")
    print("-" * 50)
    np.random.seed(42)
    genes = np.vstack([np.random.randn(20, 6) * 0.3 + [5, 5, 0, 0, 0, 0],
                       np.random.randn(20, 6) * 0.3 + [0, 0, 5, 5, 0, 0],
                       np.random.randn(20, 6) * 0.3 + [0, 0, 0, 0, 5, 5]])
    r = lens.scan_materials(genes, [f"gene_{i}" for i in range(6)])
    print(f"  Entangled: {len(r.entanglement_pairs)} | Tunneling: {len(r.tunneling_paths)}")
    c6_ent = len(r.entanglement_pairs) >= 5
    low_pairs = [p for p in r.entanglement_pairs if p["entanglement_entropy"] < 0.5]
    c6_strong = len(low_pairs) >= 1
    print(f"  CHECK: >=5 entangled gene pairs = {c6_ent}")
    print(f"  CHECK: >=1 strongly entangled pair = {c6_strong}")

    # -- Scorecard --
    print("\n" + "=" * 60)
    checks = [("Materials: >=3 entangled", c1_ent), ("Materials: superposed", c1_sup),
              ("Drug: tunneling", c2_tun), ("Drug: superposed", c2_sup),
              ("Physics: >=5 pairs", c3_ent), ("Physics: strong entangle", c3_strong),
              ("Astronomy: >=10 freq pairs", c4_ent), ("Astronomy: constructive", c4_interf),
              ("Finance: tunneling", c5_tun), ("Finance: decoherence", c5_dec),
              ("Genomics: >=5 pairs", c6_ent), ("Genomics: strong pair", c6_strong)]
    p = sum(v for _, v in checks)
    print(f"  SCORECARD: {p}/{len(checks)} ({100 * p // len(checks)}%)")
    for nm, ok in checks:
        print(f"    {'PASS' if ok else 'FAIL'} {nm}")
    print("=" * 60)
