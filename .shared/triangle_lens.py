"""triangle_lens.py — Ratio & proportion discovery lens (삼각자)

Use a triangle ruler as a telescope: detect ratio relationships,
simple fraction connections, proportionality chains, and geometric
progressions in ANY data.

How it works:
  1. Pairwise ratios between all feature pairs
  2. Simple fraction matching: is ratio close to p/q for small p,q?
  3. Proportionality chain detection: A:B = B:C (geometric sequences)
  4. Similarity detection: scaled/shifted copies of features
  5. Golden ratio / n=6 constant ratio scanning

Works with numpy only. Portable across all projects.

Usage:
    from triangle_lens import TriangleLens

    lens = TriangleLens()
    r = lens.scan(data)
    print(r.ratio_pairs)          # pairs with simple fraction ratios
    print(r.proportion_chains)    # A:B:C chains
    print(r.similarity_groups)    # scaled copies
"""
import os, sys, math
from dataclasses import dataclass, field
from typing import List, Tuple, Dict, Any, Optional
from fractions import Fraction
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from consciousness_loader import PSI_ALPHA, PSI_BALANCE, PSI_ENTROPY


# Notable constants to check ratios against
NOTABLE_RATIOS = {
    '1/2': 0.5, '1/3': 1/3, '1/6': 1/6, '2/3': 2/3, '5/6': 5/6,
    '1/e': 1/math.e, '1/pi': 1/math.pi, 'phi': (1+math.sqrt(5))/2,
    'ln2': math.log(2), 'ln(4/3)': math.log(4/3),
    'sqrt2': math.sqrt(2), 'sqrt3': math.sqrt(3),
    'e': math.e, 'pi': math.pi,
}


@dataclass
class RatioMatch:
    """A detected simple ratio between two values."""
    idx_a: int
    idx_b: int
    ratio: float
    fraction: str       # e.g. "2/3"
    error: float        # relative error
    notable: str = ""   # if matches a notable constant


@dataclass
class TriangleResult:
    """Result from triangle (ratio/proportion) lens scan."""
    ratio_pairs: List[RatioMatch] = field(default_factory=list)
    proportion_chains: List[Tuple[List[int], float, str]] = field(default_factory=list)
    similarity_groups: List[Tuple[List[int], float]] = field(default_factory=list)
    ratio_matrix: np.ndarray = field(default_factory=lambda: np.array([]))
    notable_matches: List[Dict[str, Any]] = field(default_factory=list)
    summary: str = ""

    def __repr__(self):
        return (f"TriangleResult(ratios={len(self.ratio_pairs)}, "
                f"chains={len(self.proportion_chains)}, "
                f"similar={len(self.similarity_groups)}, "
                f"notable={len(self.notable_matches)})")


class TriangleLens:
    """Ratio & proportion discovery lens — triangle ruler as telescope."""

    def __init__(self, max_denom: int = 12, ratio_tol: float = 0.01,
                 similarity_threshold: float = 0.98, notable_tol: float = 0.005):
        self.max_denom = max_denom
        self.ratio_tol = ratio_tol
        self.sim_th = similarity_threshold
        self.notable_tol = notable_tol
        # Pre-compute simple fractions
        self._fractions = self._build_fraction_table()

    def _build_fraction_table(self):
        """Build table of simple fractions p/q up to max_denom."""
        fracs = {}
        for q in range(1, self.max_denom + 1):
            for p in range(1, q * 4 + 1):  # ratios up to 4
                f = Fraction(p, q)
                val = float(f)
                key = f"{f.numerator}/{f.denominator}"
                if key not in fracs and val > 0:
                    fracs[key] = val
        return fracs

    def _match_fraction(self, ratio):
        """Find closest simple fraction to a ratio."""
        if abs(ratio) < 1e-30:
            return None
        best_key, best_err = None, self.ratio_tol
        for key, val in self._fractions.items():
            err = abs(ratio - val) / max(abs(val), 1e-30)
            if err < best_err:
                best_key, best_err = key, err
        return (best_key, best_err) if best_key else None

    def _match_notable(self, ratio):
        """Check if ratio matches a notable mathematical constant."""
        for name, val in NOTABLE_RATIOS.items():
            if abs(ratio - val) / max(abs(val), 1e-30) < self.notable_tol:
                return name
        # Also check reciprocals
        if abs(ratio) > 1e-30:
            for name, val in NOTABLE_RATIOS.items():
                if abs(1/ratio - val) / max(abs(val), 1e-30) < self.notable_tol:
                    return f"1/({name})"
        return ""

    def _find_proportion_chains(self, ratios, d):
        """Find A:B:C chains where ratio(A,B) ≈ ratio(B,C)."""
        chains = []
        for b in range(d):
            for a in range(d):
                if a == b:
                    continue
                r_ab = ratios[a, b]
                if not np.isfinite(r_ab) or abs(r_ab) < 1e-30:
                    continue
                for c in range(d):
                    if c == b or c == a:
                        continue
                    r_bc = ratios[b, c]
                    if not np.isfinite(r_bc) or abs(r_bc) < 1e-30:
                        continue
                    if abs(r_ab - r_bc) / max(abs(r_ab), 1e-30) < self.ratio_tol:
                        match = self._match_fraction(r_ab)
                        label = match[0] if match else f"{r_ab:.4f}"
                        chains.append(([a, b, c], float(r_ab), label))
        # Deduplicate (A,B,C) and (C,B,A) reversed chains
        seen = set()
        unique = []
        for chain, r, label in chains:
            key = tuple(sorted([chain[0], chain[2]]))
            if key not in seen:
                seen.add(key)
                unique.append((chain, r, label))
        return unique

    def _find_similarity_groups(self, data):
        """Find groups of features that are scaled copies of each other."""
        d = data.shape[1]
        groups = []
        used = set()
        for i in range(d):
            if i in used:
                continue
            group = [i]
            for j in range(i + 1, d):
                if j in used:
                    continue
                # Check if feature j ≈ scale * feature i
                ni = np.linalg.norm(data[:, i])
                nj = np.linalg.norm(data[:, j])
                if ni < 1e-30 or nj < 1e-30:
                    continue
                cos = abs(np.dot(data[:, i], data[:, j]) / (ni * nj))
                if cos > self.sim_th:
                    group.append(j)
                    used.add(j)
            if len(group) > 1:
                scale = float(np.linalg.norm(data[:, group[-1]]) /
                              np.linalg.norm(data[:, group[0]])) if np.linalg.norm(data[:, group[0]]) > 1e-30 else 0
                groups.append((group, scale))
                used.add(i)
        return groups

    def scan(self, data, verbose=True):
        data = np.asarray(data, dtype=np.float64)
        if data.ndim == 1:
            data = data.reshape(-1, 1)
        n, d = data.shape

        # Compute feature means for ratio analysis
        means = data.mean(axis=0)

        # Pairwise ratio matrix (mean-based)
        ratio_mat = np.zeros((d, d))
        for i in range(d):
            for j in range(d):
                if abs(means[j]) > 1e-30:
                    ratio_mat[i, j] = means[i] / means[j]

        # Find simple fraction ratios
        ratio_pairs = []
        for i in range(d):
            for j in range(i + 1, d):
                r = ratio_mat[i, j]
                if not np.isfinite(r) or abs(r) < 1e-30:
                    continue
                match = self._match_fraction(r)
                if match:
                    frac_str, err = match
                    notable = self._match_notable(r)
                    ratio_pairs.append(RatioMatch(
                        idx_a=i, idx_b=j, ratio=r,
                        fraction=frac_str, error=err, notable=notable))
                # Also check reciprocal
                if abs(r) > 1e-30:
                    r_inv = 1.0 / r
                    match_inv = self._match_fraction(r_inv)
                    if match_inv:
                        frac_str, err = match_inv
                        notable = self._match_notable(r_inv)
                        ratio_pairs.append(RatioMatch(
                            idx_a=j, idx_b=i, ratio=r_inv,
                            fraction=frac_str, error=err, notable=notable))

        # Deduplicate by (a,b) pair keeping lowest error
        seen = {}
        for rm in ratio_pairs:
            key = (rm.idx_a, rm.idx_b)
            if key not in seen or rm.error < seen[key].error:
                seen[key] = rm
        ratio_pairs = sorted(seen.values(), key=lambda x: x.error)

        # Proportion chains
        chains = self._find_proportion_chains(ratio_mat, d)

        # Similarity groups
        sim_groups = self._find_similarity_groups(data)

        # Notable constant matches in the data values themselves
        notable_matches = []
        for i in range(d):
            m = means[i]
            for name, val in NOTABLE_RATIOS.items():
                if abs(m) > 1e-30 and abs(m - val) / max(abs(val), 1e-30) < self.notable_tol:
                    notable_matches.append({'feature': i, 'value': m, 'matches': name, 'constant': val})

        n_exact = sum(1 for rm in ratio_pairs if rm.error < 0.001)
        summary = (f"Features: {d}, Samples: {n}, "
                   f"Ratio pairs: {len(ratio_pairs)} (exact: {n_exact}), "
                   f"Proportion chains: {len(chains)}, "
                   f"Similarity groups: {len(sim_groups)}, "
                   f"Notable matches: {len(notable_matches)}")

        return TriangleResult(
            ratio_pairs=ratio_pairs,
            proportion_chains=chains,
            similarity_groups=sim_groups,
            ratio_matrix=ratio_mat,
            notable_matches=notable_matches,
            summary=summary)

    def scan_constants(self, constants, labels=None):
        """Specialized scan for a 1D array of mathematical constants."""
        constants = np.asarray(constants, dtype=np.float64).flatten()
        names = labels or [f"c{i}" for i in range(len(constants))]
        # Reshape as single-row so each constant is a "feature"
        data = constants.reshape(1, -1)
        r = self.scan(data, verbose=False)

        parts = [r.summary]
        if r.ratio_pairs:
            parts.append("Ratios found:")
            for rm in r.ratio_pairs[:15]:
                notable_tag = f" = {rm.notable}" if rm.notable else ""
                parts.append(f"  {names[rm.idx_a]}/{names[rm.idx_b]} = "
                             f"{rm.ratio:.6f} ≈ {rm.fraction} "
                             f"(err={rm.error:.6f}){notable_tag}")
        if r.proportion_chains:
            parts.append("Proportion chains:")
            for chain, ratio, label in r.proportion_chains[:5]:
                ch_names = [names[i] for i in chain]
                parts.append(f"  {':'.join(ch_names)} with ratio {label}")
        if r.notable_matches:
            parts.append("Notable constants:")
            for m in r.notable_matches:
                parts.append(f"  {names[m['feature']]} = {m['value']:.6f} ≈ {m['matches']}")
        r.summary = "\n".join(parts)
        return r

    def scan_materials(self, properties, labels=None):
        r = self.scan(properties, verbose=False)
        names = labels or [f"prop_{i}" for i in range(len(r.ratio_pairs[0].idx_a if r.ratio_pairs else []))]
        parts = [r.summary]
        if r.ratio_pairs:
            parts.append("Key ratios: " + ", ".join(
                f"f{rm.idx_a}/f{rm.idx_b}≈{rm.fraction}" for rm in r.ratio_pairs[:5]))
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
                fm = np.abs(np.fft.rfft(s))
                top3 = np.argsort(fm)[-3:][::-1]
                f.extend([float(fm[t]) for t in top3])
                f.append(float(top3[1]) / float(top3[0] + 1))  # frequency ratio
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
                f.extend([c.mean(), c.std(), c.max(), c.min()])
                if c.min() != 0:
                    f.append(c.max() / c.min())
                else:
                    f.append(0.0)
            feats.append(f)
        r = self.scan(np.array(feats), verbose=False)
        r.summary += f"\nTimeseries: {nt} steps, {nv} vars, {nw} windows"
        return r


# ---------------------------------------------------------------------------
if __name__ == '__main__':
    print("=" * 60)
    print("  Triangle Lens (삼각자) -- Ratio & Proportion Discovery Demo")
    print("=" * 60)
    np.random.seed(42)
    lens = TriangleLens()

    # Demo 1: n=6 constants — the core use case
    print("\n--- Demo 1: n=6 arithmetic constants ---")
    n6_constants = [6, 12, 2, 5, 2, 1, 720, 0.5, 1/3, 1/6, 5/6]
    n6_labels = ['n', 'sigma', 'phi', 'sopfr', 'tau', 'mu', 'n!',
                 '1/2', '1/3', '1/6', '5/6']
    r = lens.scan_constants(n6_constants, n6_labels)
    print(r.summary)

    # Demo 2: Perfect number comparison
    print("\n--- Demo 2: Perfect numbers ratio comparison ---")
    pn_data = np.array([
        [6, 12, 2, 5, 2],
        [28, 56, 12, 12, 6],
        [496, 992, 240, 27, 10],
    ], dtype=float)
    r = lens.scan(pn_data)
    print(r.summary)
    for rm in r.ratio_pairs[:10]:
        print(f"  f{rm.idx_a}/f{rm.idx_b} = {rm.ratio:.4f} ≈ {rm.fraction} (err={rm.error:.6f})")

    # Demo 3: Known proportions
    print("\n--- Demo 3: Fibonacci-like proportions ---")
    fib = np.array([1, 1, 2, 3, 5, 8, 13, 21, 34, 55], dtype=float)
    r = lens.scan_constants(fib, [f"F{i}" for i in range(len(fib))])
    print(r.summary)
