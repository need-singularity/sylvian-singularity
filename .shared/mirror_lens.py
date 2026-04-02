"""mirror_lens.py — Symmetry discovery lens (거울)

Use a mirror as a telescope: detect symmetries, invariants, broken symmetries,
and group-theoretic structures in ANY data.

How it works:
  1. Reflection symmetry: check if f(x) ≈ f(-x) or f(x) ≈ -f(-x)
  2. Permutation symmetry: which column swaps leave statistics invariant?
  3. Palindrome / time-reversal symmetry in sequences
  4. Broken symmetry detection: near-symmetries with measurable deviation
  5. Divisor lattice symmetry for number-theoretic data

Works with numpy only. Portable across all projects.

Usage:
    from mirror_lens import MirrorLens

    lens = MirrorLens()
    r = lens.scan(data)
    print(r.reflection_scores)     # per-feature reflection symmetry
    print(r.permutation_symmetries) # column swap invariances
    print(r.broken_symmetries)     # near-symmetries with deviation
"""
import os, sys, math
from dataclasses import dataclass, field
from typing import List, Tuple, Dict, Any
import numpy as np
from itertools import combinations, permutations

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from consciousness_loader import PSI_ALPHA, PSI_BALANCE, PSI_ENTROPY


@dataclass
class SymmetryMatch:
    """A detected symmetry or broken symmetry."""
    kind: str           # "reflection", "permutation", "time_reversal", "scale"
    features: List[int]
    score: float        # 1.0 = perfect symmetry
    deviation: float    # how much it deviates from perfect
    description: str = ""


@dataclass
class MirrorResult:
    """Result from mirror (symmetry) lens scan."""
    reflection_scores: np.ndarray = field(default_factory=lambda: np.array([]))
    permutation_symmetries: List[SymmetryMatch] = field(default_factory=list)
    broken_symmetries: List[SymmetryMatch] = field(default_factory=list)
    time_reversal_score: float = 0.0
    distribution_symmetry: np.ndarray = field(default_factory=lambda: np.array([]))
    overall_symmetry: float = 0.0
    summary: str = ""

    def __repr__(self):
        return (f"MirrorResult(overall={self.overall_symmetry:.3f}, "
                f"permutations={len(self.permutation_symmetries)}, "
                f"broken={len(self.broken_symmetries)})")


class MirrorLens:
    """Symmetry discovery lens — mirror as telescope."""

    def __init__(self, symmetry_threshold: float = 0.9,
                 broken_threshold: float = 0.7):
        self.sym_th = symmetry_threshold
        self.broken_th = broken_threshold

    def _reflection_symmetry(self, col):
        """Measure reflection symmetry of a 1D distribution around its median."""
        med = np.median(col)
        above = np.sort(col[col >= med] - med)
        below = np.sort(med - col[col < med])
        n = min(len(above), len(below))
        if n == 0:
            return 1.0
        a, b = above[:n], below[:n]
        denom = np.mean(np.abs(a) + np.abs(b)) + 1e-30
        diff = np.mean(np.abs(a - b))
        return max(0.0, 1.0 - diff / denom)

    def _distribution_symmetry(self, data):
        """Per-feature distribution symmetry (skewness-based)."""
        d = data.shape[1]
        scores = np.zeros(d)
        for j in range(d):
            col = data[:, j]
            mu = col.mean()
            std = col.std()
            if std < 1e-30:
                scores[j] = 1.0
                continue
            skew = float(np.mean(((col - mu) / std) ** 3))
            # Perfect symmetry = skew 0, map to 0-1 score
            scores[j] = max(0.0, 1.0 - abs(skew) / 3.0)
        return scores

    def _permutation_symmetry(self, data):
        """Find column pairs/triples where swapping preserves statistics."""
        d = data.shape[1]
        symmetries = []
        broken = []

        # Pairwise: check if columns i,j have similar distributions
        means = data.mean(axis=0)
        stds = data.std(axis=0)

        for i, j in combinations(range(d), 2):
            if stds[i] < 1e-30 or stds[j] < 1e-30:
                continue
            # Compare distributions via KS-like statistic
            si = np.sort((data[:, i] - means[i]) / stds[i])
            sj = np.sort((data[:, j] - means[j]) / stds[j])
            ks = float(np.max(np.abs(si - sj)))
            score = max(0.0, 1.0 - ks)

            if score >= self.sym_th:
                symmetries.append(SymmetryMatch(
                    kind="permutation", features=[i, j],
                    score=score, deviation=1 - score,
                    description=f"col{i}↔col{j} swap-invariant ({score:.3f})"))
            elif score >= self.broken_th:
                broken.append(SymmetryMatch(
                    kind="permutation", features=[i, j],
                    score=score, deviation=1 - score,
                    description=f"col{i}↔col{j} near-symmetric ({score:.3f}, broken by {1-score:.3f})"))

        # Also check mean/std symmetry (are columns "echoes" of each other?)
        for i, j in combinations(range(d), 2):
            if abs(means[i]) < 1e-30 and abs(means[j]) < 1e-30:
                continue
            # Check if mean[i]/mean[j] ≈ std[i]/std[j] (scale symmetry)
            if stds[j] > 1e-30 and abs(means[j]) > 1e-30:
                ratio_mean = means[i] / means[j]
                ratio_std = stds[i] / stds[j]
                if abs(ratio_mean) > 1e-30:
                    scale_sym = 1.0 - min(1.0, abs(ratio_mean - ratio_std) / abs(ratio_mean))
                    if scale_sym >= self.sym_th:
                        symmetries.append(SymmetryMatch(
                            kind="scale", features=[i, j],
                            score=scale_sym, deviation=1 - scale_sym,
                            description=f"col{i}:col{j} scale-symmetric ({scale_sym:.3f})"))

        return symmetries, broken

    def _time_reversal(self, data):
        """Check if rows are similar when reversed (palindrome structure)."""
        n = data.shape[0]
        if n < 4:
            return 0.0
        forward = data[:n//2]
        backward = data[n-1:n-1-n//2:-1]
        m = min(len(forward), len(backward))
        if m == 0:
            return 0.0
        diff = np.mean(np.abs(forward[:m] - backward[:m]))
        scale = np.mean(np.abs(data)) + 1e-30
        return max(0.0, 1.0 - diff / scale)

    def _number_symmetry(self, values):
        """Check number-theoretic symmetries for 1D array of values."""
        results = []
        vals = np.asarray(values, dtype=np.float64).flatten()
        n = len(vals)

        # Check: a + b = c relationships (additive symmetry)
        for i in range(n):
            for j in range(i + 1, n):
                s = vals[i] + vals[j]
                for k in range(n):
                    if k != i and k != j and abs(s - vals[k]) < 1e-10:
                        results.append(SymmetryMatch(
                            kind="additive", features=[i, j, k],
                            score=1.0, deviation=0.0,
                            description=f"v[{i}]+v[{j}]=v[{k}] ({vals[i]}+{vals[j]}={vals[k]})"))

        # Check: a * b = c relationships (multiplicative symmetry)
        for i in range(n):
            for j in range(i + 1, n):
                p = vals[i] * vals[j]
                for k in range(n):
                    if k != i and k != j and abs(p - vals[k]) / (abs(vals[k]) + 1e-30) < 1e-10:
                        results.append(SymmetryMatch(
                            kind="multiplicative", features=[i, j, k],
                            score=1.0, deviation=0.0,
                            description=f"v[{i}]*v[{j}]=v[{k}] ({vals[i]}*{vals[j]}={vals[k]})"))

        # Check: reciprocal pairs a * b = 1
        for i in range(n):
            for j in range(i + 1, n):
                if abs(vals[i] * vals[j] - 1.0) < 1e-10:
                    results.append(SymmetryMatch(
                        kind="reciprocal", features=[i, j],
                        score=1.0, deviation=0.0,
                        description=f"v[{i}]*v[{j}]=1 ({vals[i]}*{vals[j]}=1)"))

        return results

    def scan(self, data, verbose=True):
        data = np.asarray(data, dtype=np.float64)
        if data.ndim == 1:
            data = data.reshape(-1, 1)
        n, d = data.shape

        # Per-feature reflection symmetry
        refl = np.array([self._reflection_symmetry(data[:, j]) for j in range(d)])

        # Distribution symmetry (skewness)
        dist_sym = self._distribution_symmetry(data)

        # Permutation symmetries
        perm_sym, broken = self._permutation_symmetry(data)

        # Time reversal
        time_rev = self._time_reversal(data)

        # Overall symmetry score
        overall = float(np.mean(refl) * 0.4 + np.mean(dist_sym) * 0.3 +
                        time_rev * 0.1 +
                        (len(perm_sym) / max(d * (d-1) / 2, 1)) * 0.2)

        n_perfect = sum(1 for s in perm_sym if s.score > 0.95)
        summary = (f"Features: {d}, Samples: {n}, "
                   f"Reflection: {np.mean(refl):.3f}, "
                   f"Distribution sym: {np.mean(dist_sym):.3f}, "
                   f"Permutation sym: {len(perm_sym)} (perfect: {n_perfect}), "
                   f"Broken sym: {len(broken)}, "
                   f"Time reversal: {time_rev:.3f}, "
                   f"Overall: {overall:.3f}")

        return MirrorResult(
            reflection_scores=refl,
            permutation_symmetries=perm_sym,
            broken_symmetries=broken,
            time_reversal_score=time_rev,
            distribution_symmetry=dist_sym,
            overall_symmetry=overall,
            summary=summary)

    def scan_constants(self, constants, labels=None):
        """Specialized scan for mathematical constants — find algebraic symmetries."""
        constants = np.asarray(constants, dtype=np.float64).flatten()
        names = labels or [f"c{i}" for i in range(len(constants))]
        # Reshape for standard scan
        data = constants.reshape(1, -1)
        r = self.scan(data, verbose=False)

        # Add number-theoretic symmetries
        num_sym = self._number_symmetry(constants)

        parts = [r.summary]
        if num_sym:
            parts.append("Number symmetries:")
            for s in num_sym[:20]:
                feat_names = [names[i] for i in s.features]
                parts.append(f"  [{s.kind}] {' '.join(feat_names)}: {s.description}")
            r.permutation_symmetries.extend(num_sym)
        r.summary = "\n".join(parts)
        return r

    def scan_materials(self, properties, labels=None):
        r = self.scan(properties, verbose=False)
        parts = [r.summary]
        if r.permutation_symmetries:
            parts.append("Symmetric pairs: " + ", ".join(
                s.description for s in r.permutation_symmetries[:5]))
        if r.broken_symmetries:
            parts.append("Broken symmetries: " + ", ".join(
                s.description for s in r.broken_symmetries[:5]))
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
                f.extend([s.mean(), s.std()])
                # Even/odd decomposition
                n_half = len(s) // 2
                if n_half > 0:
                    even = (s[:n_half] + s[-n_half:][::-1]) / 2
                    odd = (s[:n_half] - s[-n_half:][::-1]) / 2
                    f.extend([float(np.std(even)), float(np.std(odd))])
                else:
                    f.extend([0.0, 0.0])
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
                f.extend([c.mean(), c.std()])
                # Time-reversal score per window
                rev = c[::-1]
                corr = np.corrcoef(c, rev)[0, 1] if len(c) > 1 else 0.0
                f.append(corr if np.isfinite(corr) else 0.0)
            feats.append(f)
        r = self.scan(np.array(feats), verbose=False)
        r.summary += f"\nTimeseries: {nt} steps, {nv} vars, {nw} windows"
        return r


# ---------------------------------------------------------------------------
if __name__ == '__main__':
    print("=" * 60)
    print("  Mirror Lens (거울) -- Symmetry Discovery Demo")
    print("=" * 60)
    np.random.seed(42)
    lens = MirrorLens()

    # Demo 1: Symmetric vs asymmetric distributions
    print("\n--- Demo 1: Symmetric vs skewed features ---")
    data = np.column_stack([
        np.random.randn(100),                    # symmetric (normal)
        np.random.exponential(1, 100),            # asymmetric (exponential)
        np.random.randn(100),                    # symmetric
        np.random.randn(100) * 2 + 5,            # symmetric (shifted+scaled)
    ])
    r = lens.scan(data)
    print(r.summary)
    print(f"  Reflection scores: {r.reflection_scores}")
    print(f"  Distribution sym: {r.distribution_symmetry}")

    # Demo 2: n=6 constants — algebraic symmetries
    print("\n--- Demo 2: n=6 algebraic symmetries ---")
    n6 = [6, 12, 2, 5, 2, 1, 720, 0.5, 1/3, 1/6]
    labels = ['n', 'sigma', 'phi', 'sopfr', 'tau', 'mu', 'n!',
              '1/2', '1/3', '1/6']
    r = lens.scan_constants(n6, labels)
    print(r.summary)

    # Demo 3: Palindrome data
    print("\n--- Demo 3: Time-reversal symmetry ---")
    forward = np.random.randn(25, 4)
    palindrome = np.vstack([forward, forward[::-1]])
    r = lens.scan(palindrome)
    print(r.summary)
    print(f"  Time reversal: {r.time_reversal_score:.4f}")
