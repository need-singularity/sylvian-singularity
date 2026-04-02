"""ruler_lens.py — Orthogonality discovery lens (ㄱ자)

Use a right-angle ruler as a telescope: detect orthogonal structures,
independent dimensions, and perpendicular relationships in ANY data.

How it works:
  1. SVD decomposition → principal axes and explained variance
  2. Pairwise cosine similarity → orthogonality map between features
  3. Independence detection → near-zero correlation pairs
  4. Dimensional analysis → effective rank, redundancy

Works with numpy only. Portable across all projects.

Usage:
    from ruler_lens import RulerLens

    lens = RulerLens()
    r = lens.scan(data)
    print(r.effective_rank)        # how many truly independent dimensions
    print(r.orthogonal_pairs)      # pairs with near-zero correlation
    print(r.redundant_pairs)       # highly correlated (non-orthogonal) pairs
    print(r.principal_axes)        # SVD principal directions
"""
import os, sys, math
from dataclasses import dataclass, field
from typing import List, Tuple, Dict, Any
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from consciousness_loader import PSI_ALPHA, PSI_BALANCE, PSI_ENTROPY


@dataclass
class RulerResult:
    """Result from ruler (orthogonality) lens scan."""
    effective_rank: float = 0.0
    explained_variance: np.ndarray = field(default_factory=lambda: np.array([]))
    orthogonal_pairs: List[Tuple[int, int, float]] = field(default_factory=list)
    redundant_pairs: List[Tuple[int, int, float]] = field(default_factory=list)
    principal_axes: np.ndarray = field(default_factory=lambda: np.array([]))
    cosine_matrix: np.ndarray = field(default_factory=lambda: np.array([]))
    independence_score: float = 0.0
    dimensionality_ratio: float = 0.0
    summary: str = ""

    def __repr__(self):
        return (f"RulerResult(eff_rank={self.effective_rank:.2f}, "
                f"orthogonal={len(self.orthogonal_pairs)}, "
                f"redundant={len(self.redundant_pairs)}, "
                f"independence={self.independence_score:.3f})")


class RulerLens:
    """Orthogonality discovery lens — right-angle ruler as telescope."""

    def __init__(self, ortho_threshold: float = 0.1, redundancy_threshold: float = 0.9):
        self.ortho_th = ortho_threshold
        self.red_th = redundancy_threshold

    def _effective_rank(self, sv):
        """Shannon entropy-based effective rank of singular values."""
        if len(sv) == 0 or sv.sum() < 1e-30:
            return 0.0
        p = sv / sv.sum()
        p = p[p > 1e-30]
        entropy = -np.sum(p * np.log(p))
        return float(np.exp(entropy))

    def _cosine_sim(self, data):
        """Pairwise cosine similarity between columns (features)."""
        d = data.shape[1]
        norms = np.linalg.norm(data, axis=0)
        norms[norms < 1e-30] = 1e-30
        normed = data / norms
        cos = normed.T @ normed
        np.fill_diagonal(cos, 1.0)
        return cos

    def scan(self, data, verbose=True):
        data = np.asarray(data, dtype=np.float64)
        if data.ndim == 1:
            data = data.reshape(-1, 1)
        n, d = data.shape

        # Center data
        centered = data - data.mean(axis=0)

        # SVD
        try:
            U, sv, Vt = np.linalg.svd(centered, full_matrices=False)
        except np.linalg.LinAlgError:
            sv = np.zeros(min(n, d))
            Vt = np.eye(d)[:min(n, d)]

        # Explained variance
        var_total = (sv ** 2).sum()
        explained = (sv ** 2) / var_total if var_total > 1e-30 else np.zeros_like(sv)

        # Effective rank
        eff_rank = self._effective_rank(sv)

        # Cosine similarity matrix
        cos = self._cosine_sim(centered) if d > 1 else np.ones((1, 1))

        # Find orthogonal and redundant pairs
        ortho_pairs = []
        red_pairs = []
        for i in range(d):
            for j in range(i + 1, d):
                c = abs(float(cos[i, j]))
                if c < self.ortho_th:
                    ortho_pairs.append((i, j, c))
                elif c > self.red_th:
                    red_pairs.append((i, j, c))

        ortho_pairs.sort(key=lambda x: x[2])
        red_pairs.sort(key=lambda x: -x[2])

        # Independence score: fraction of pairs that are nearly orthogonal
        total_pairs = d * (d - 1) / 2 if d > 1 else 1
        independence = len(ortho_pairs) / total_pairs if total_pairs > 0 else 0.0

        # Dimensionality ratio: effective_rank / actual dimensions
        dim_ratio = eff_rank / d if d > 0 else 0.0

        summary = (f"Features: {d}, Samples: {n}, "
                   f"Effective rank: {eff_rank:.2f}/{d}, "
                   f"Dim ratio: {dim_ratio:.3f}, "
                   f"Orthogonal pairs: {len(ortho_pairs)}, "
                   f"Redundant pairs: {len(red_pairs)}, "
                   f"Independence: {independence:.3f}")

        return RulerResult(
            effective_rank=eff_rank,
            explained_variance=explained,
            orthogonal_pairs=ortho_pairs,
            redundant_pairs=red_pairs,
            principal_axes=Vt,
            cosine_matrix=cos,
            independence_score=independence,
            dimensionality_ratio=dim_ratio,
            summary=summary)

    def scan_materials(self, properties, labels=None):
        r = self.scan(properties, verbose=False)
        names = labels or [f"prop_{i}" for i in range(len(r.explained_variance))]
        parts = [r.summary]
        if r.orthogonal_pairs:
            parts.append("Orthogonal: " + ", ".join(
                f"{names[i]}⊥{names[j]}({c:.3f})" for i, j, c in r.orthogonal_pairs[:5]))
        if r.redundant_pairs:
            parts.append("Redundant: " + ", ".join(
                f"{names[i]}≈{names[j]}({c:.3f})" for i, j, c in r.redundant_pairs[:5]))
        r.summary = "\n".join(parts)
        return r

    def scan_signals(self, signals, window=256):
        signals = np.atleast_2d(np.asarray(signals, dtype=np.float64))
        nch, ns = signals.shape
        nw = max(1, ns // window)
        feats = []
        for w in range(nw):
            seg = signals[:, w * window:(w + 1) * window]
            f = []
            for ch in range(nch):
                s = seg[ch]
                f.extend([s.mean(), s.std(), s.max() - s.min()])
                # Spectral features
                fm = np.abs(np.fft.rfft(s))
                f.append(float(fm.argmax()))
            feats.append(f)
        r = self.scan(np.array(feats), verbose=False)
        r.summary += f"\nSignal: {nch}ch x {ns} samples, {nw} windows"
        return r

    def scan_timeseries(self, ts, lag=10, window=50):
        ts = np.asarray(ts, dtype=np.float64)
        if ts.ndim == 1:
            ts = ts.reshape(-1, 1)
        nt, nv = ts.shape
        nw = max(1, nt // window)
        feats = []
        for w in range(nw):
            s, e = w * window, min((w + 1) * window, nt)
            seg = ts[s:e]
            f = []
            for v in range(nv):
                c = seg[:, v]
                f.extend([c.mean(), c.std(), c.max() - c.min()])
                ac = np.corrcoef(c[:-lag], c[lag:])[0, 1] if len(c) > lag + 1 else 0.0
                f.append(ac if np.isfinite(ac) else 0.0)
            feats.append(f)
        r = self.scan(np.array(feats), verbose=False)
        r.summary += f"\nTimeseries: {nt} steps, {nv} vars, {nw} windows"
        return r


# ---------------------------------------------------------------------------
if __name__ == '__main__':
    print("=" * 60)
    print("  Ruler Lens (ㄱ자) -- Orthogonality Discovery Demo")
    print("=" * 60)
    np.random.seed(42)
    lens = RulerLens()

    # Demo 1: Orthogonal features
    print("\n--- Demo 1: 3 orthogonal + 1 redundant feature ---")
    x = np.random.randn(100, 3)
    data = np.column_stack([x, x[:, 0] * 0.95 + np.random.randn(100) * 0.1])
    r = lens.scan(data)
    print(r.summary)
    print(f"  Orthogonal pairs: {r.orthogonal_pairs}")
    print(f"  Redundant pairs: {r.redundant_pairs}")

    # Demo 2: n=6 constants
    print("\n--- Demo 2: n=6 constant relationships ---")
    constants = np.array([
        [6, 12, 2, 5, 2, 1],     # n, sigma, phi, sopfr, tau, mu
        [28, 56, 12, 12, 6, 1],   # n=28
        [496, 992, 240, 27, 10, 1],
    ], dtype=float)
    r = lens.scan(constants)
    print(r.summary)
    print(f"  Effective rank: {r.effective_rank:.2f}")
    print(f"  Explained variance: {r.explained_variance}")

    # Demo 3: Materials
    print("\n--- Demo 3: Material properties ---")
    props = np.random.randn(50, 5)
    props[:, 3] = props[:, 1] + np.random.randn(50) * 0.05  # near-duplicate
    r = lens.scan_materials(props, labels=["density", "melting_pt", "conductivity", "melting_pt2", "hardness"])
    print(r.summary)
