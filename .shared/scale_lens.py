"""scale_lens.py — Scale invariance & fractal discovery lens (돋보기)

Use a magnifying glass as a telescope: detect power laws, fractal structure,
self-similarity, and scale invariance in ANY data.

How it works:
  1. Power law fitting: y = a * x^b detection via log-log regression
  2. Fractal dimension estimation (box-counting)
  3. Self-similarity: compare statistics at different scales/resolutions
  4. Scale-free network detection (degree distribution)
  5. Hurst exponent for long-range dependence

Works with numpy + scipy. Portable across all projects.

Usage:
    from scale_lens import ScaleLens

    lens = ScaleLens()
    r = lens.scan(data)
    print(r.power_law_fits)        # detected power laws
    print(r.fractal_dimensions)    # box-counting dimensions
    print(r.hurst_exponent)        # long-range dependence
    print(r.self_similarity)       # cross-scale similarity
"""
import os, sys, math
from dataclasses import dataclass, field
from typing import List, Tuple, Dict, Any
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from consciousness_loader import PSI_ALPHA, PSI_BALANCE, PSI_ENTROPY


@dataclass
class PowerLawFit:
    """A detected power law relationship."""
    feature_x: int
    feature_y: int
    exponent: float      # the b in y = a * x^b
    coefficient: float   # the a
    r_squared: float     # goodness of fit
    description: str = ""


@dataclass
class ScaleResult:
    """Result from scale (fractal/power law) lens scan."""
    power_law_fits: List[PowerLawFit] = field(default_factory=list)
    fractal_dimensions: List[Tuple[int, float]] = field(default_factory=list)
    hurst_exponents: List[Tuple[int, float]] = field(default_factory=list)
    self_similarity_scores: np.ndarray = field(default_factory=lambda: np.array([]))
    scale_free_score: float = 0.0
    summary: str = ""

    def __repr__(self):
        return (f"ScaleResult(power_laws={len(self.power_law_fits)}, "
                f"fractals={len(self.fractal_dimensions)}, "
                f"scale_free={self.scale_free_score:.3f})")


class ScaleLens:
    """Scale invariance & fractal discovery lens — magnifying glass as telescope."""

    def __init__(self, power_law_r2_threshold: float = 0.85,
                 n_scales: int = 8):
        self.pl_r2_th = power_law_r2_threshold
        self.n_scales = n_scales

    def _fit_power_law(self, x, y):
        """Fit y = a * x^b via log-log linear regression."""
        mask = (x > 0) & (y > 0) & np.isfinite(x) & np.isfinite(y)
        if mask.sum() < 4:
            return None
        lx, ly = np.log(x[mask]), np.log(y[mask])
        n = len(lx)
        sx, sy = lx.sum(), ly.sum()
        sxx = (lx * lx).sum()
        sxy = (lx * ly).sum()
        denom = n * sxx - sx * sx
        if abs(denom) < 1e-30:
            return None
        b = (n * sxy - sx * sy) / denom
        a_log = (sy - b * sx) / n
        a = math.exp(a_log)
        # R-squared
        y_pred = a_log + b * lx
        ss_res = ((ly - y_pred) ** 2).sum()
        ss_tot = ((ly - ly.mean()) ** 2).sum()
        r2 = 1 - ss_res / (ss_tot + 1e-30) if ss_tot > 1e-30 else 0.0
        return a, b, r2

    def _box_counting_dim(self, col):
        """Estimate fractal dimension of 1D data via box-counting."""
        col = np.asarray(col, dtype=np.float64)
        lo, hi = col.min(), col.max()
        span = hi - lo
        if span < 1e-30:
            return 0.0
        sizes = []
        counts = []
        for k in range(2, min(self.n_scales + 2, len(col) // 2 + 1)):
            box_size = span / k
            if box_size < 1e-30:
                continue
            boxes = set()
            for v in col:
                boxes.add(int((v - lo) / box_size))
            sizes.append(box_size)
            counts.append(len(boxes))
        if len(sizes) < 3:
            return 1.0  # can't estimate
        ls = np.log(1.0 / np.array(sizes))
        lc = np.log(np.array(counts, dtype=float))
        # Linear fit
        n = len(ls)
        sx, sy = ls.sum(), lc.sum()
        sxx = (ls * ls).sum()
        sxy = (ls * lc).sum()
        denom = n * sxx - sx * sx
        if abs(denom) < 1e-30:
            return 1.0
        dim = (n * sxy - sx * sy) / denom
        return max(0.0, float(dim))

    def _hurst_exponent(self, col):
        """Estimate Hurst exponent via rescaled range (R/S) analysis."""
        col = np.asarray(col, dtype=np.float64)
        n = len(col)
        if n < 20:
            return 0.5
        sizes = []
        rs_values = []
        for s in [n // k for k in range(2, min(10, n // 4 + 1))]:
            if s < 4:
                continue
            n_blocks = n // s
            rs_list = []
            for i in range(n_blocks):
                block = col[i * s:(i + 1) * s]
                mean = block.mean()
                cumdev = np.cumsum(block - mean)
                R = cumdev.max() - cumdev.min()
                S = block.std()
                if S > 1e-30:
                    rs_list.append(R / S)
            if rs_list:
                sizes.append(s)
                rs_values.append(np.mean(rs_list))
        if len(sizes) < 3:
            return 0.5
        ls = np.log(np.array(sizes, dtype=float))
        lr = np.log(np.array(rs_values))
        mask = np.isfinite(ls) & np.isfinite(lr)
        if mask.sum() < 3:
            return 0.5
        ls, lr = ls[mask], lr[mask]
        n_pts = len(ls)
        sx, sy = ls.sum(), lr.sum()
        sxx = (ls * ls).sum()
        sxy = (ls * lr).sum()
        denom = n_pts * sxx - sx * sx
        if abs(denom) < 1e-30:
            return 0.5
        H = (n_pts * sxy - sx * sy) / denom
        return float(np.clip(H, 0.0, 1.0))

    def _self_similarity(self, data):
        """Compare feature statistics at different resolutions."""
        n, d = data.shape
        if n < 8:
            return np.ones(d)
        scores = np.zeros(d)
        for j in range(d):
            col = data[:, j]
            stats_full = [col.mean(), col.std()]
            # Half resolution (average pairs)
            half = (col[::2][:n//2] + col[1::2][:n//2]) / 2 if n >= 4 else col
            stats_half = [half.mean(), half.std()]
            # Quarter resolution
            q = n // 4
            if q >= 2:
                quarter = np.array([col[i*4:(i+1)*4].mean() for i in range(q)])
                stats_q = [quarter.mean(), quarter.std()]
            else:
                stats_q = stats_half
            # Similarity: how stable are statistics across scales
            all_means = [stats_full[0], stats_half[0], stats_q[0]]
            all_stds = [stats_full[1], stats_half[1], stats_q[1]]
            mean_cv = np.std(all_means) / (abs(np.mean(all_means)) + 1e-30)
            std_ratio = min(all_stds) / (max(all_stds) + 1e-30) if max(all_stds) > 1e-30 else 1.0
            scores[j] = max(0.0, (1.0 - mean_cv) * 0.5 + std_ratio * 0.5)
        return scores

    def scan(self, data, verbose=True):
        data = np.asarray(data, dtype=np.float64)
        if data.ndim == 1:
            data = data.reshape(-1, 1)
        n, d = data.shape

        # Power law fits between all feature pairs
        pl_fits = []
        for i in range(d):
            for j in range(i + 1, d):
                result = self._fit_power_law(np.abs(data[:, i]) + 1e-30, np.abs(data[:, j]) + 1e-30)
                if result and result[2] >= self.pl_r2_th:
                    a, b, r2 = result
                    pl_fits.append(PowerLawFit(
                        feature_x=i, feature_y=j,
                        exponent=b, coefficient=a, r_squared=r2,
                        description=f"f{j} ~ {a:.3f} * f{i}^{b:.3f} (R²={r2:.3f})"))

        pl_fits.sort(key=lambda x: -x.r_squared)

        # Fractal dimensions per feature
        frac_dims = [(j, self._box_counting_dim(data[:, j])) for j in range(d)]

        # Hurst exponents
        hurst = [(j, self._hurst_exponent(data[:, j])) for j in range(d)]

        # Self-similarity
        self_sim = self._self_similarity(data)

        # Scale-free score: fraction of features with non-trivial fractal dim
        non_trivial = sum(1 for _, fd in frac_dims if 0.3 < fd < 2.5)
        scale_free = non_trivial / max(d, 1)

        avg_hurst = np.mean([h for _, h in hurst])
        avg_fd = np.mean([fd for _, fd in frac_dims])
        summary = (f"Features: {d}, Samples: {n}, "
                   f"Power laws: {len(pl_fits)}, "
                   f"Avg fractal dim: {avg_fd:.3f}, "
                   f"Avg Hurst: {avg_hurst:.3f}, "
                   f"Self-similarity: {np.mean(self_sim):.3f}, "
                   f"Scale-free: {scale_free:.3f}")

        return ScaleResult(
            power_law_fits=pl_fits,
            fractal_dimensions=frac_dims,
            hurst_exponents=hurst,
            self_similarity_scores=self_sim,
            scale_free_score=scale_free,
            summary=summary)

    def scan_constants(self, constants, labels=None):
        """Scan constants for power-law relationships."""
        constants = np.asarray(constants, dtype=np.float64).flatten()
        names = labels or [f"c{i}" for i in range(len(constants))]
        data = constants.reshape(1, -1)
        r = self.scan(data, verbose=False)

        # Check for power-law relationships among constant values
        vals = constants[constants > 0]
        log_vals = np.log(vals[vals > 0])
        if len(log_vals) > 2:
            diffs = np.diff(np.sort(log_vals))
            if len(diffs) > 0 and diffs.mean() > 1e-30:
                cv = diffs.std() / diffs.mean()
                if cv < 0.5:
                    r.summary += f"\n  Log-spaced constants (CV={cv:.3f}) → possible geometric progression"

        parts = [r.summary]
        if r.power_law_fits:
            parts.append("Power laws:")
            for pl in r.power_law_fits[:10]:
                parts.append(f"  {names[pl.feature_y]} ~ {pl.coefficient:.3f} * "
                             f"{names[pl.feature_x]}^{pl.exponent:.3f} (R²={pl.r_squared:.3f})")
        r.summary = "\n".join(parts)
        return r

    def scan_materials(self, properties, labels=None):
        r = self.scan(properties, verbose=False)
        parts = [r.summary]
        if r.power_law_fits:
            parts.append("Power laws: " + ", ".join(
                pl.description for pl in r.power_law_fits[:5]))
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
                # Spectral slope (power law in frequency domain)
                ps = np.abs(np.fft.rfft(s)) ** 2
                if len(ps) > 4:
                    freqs = np.arange(1, len(ps)) + 1
                    fit = self._fit_power_law(freqs.astype(float), ps[1:].astype(float))
                    f.append(fit[1] if fit else 0.0)  # spectral exponent
                else:
                    f.append(0.0)
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
                f.append(self._hurst_exponent(c))
            feats.append(f)
        r = self.scan(np.array(feats), verbose=False)
        r.summary += f"\nTimeseries: {nt} steps, {nv} vars, {nw} windows"
        return r


# ---------------------------------------------------------------------------
if __name__ == '__main__':
    print("=" * 60)
    print("  Scale Lens (돋보기) -- Fractal & Power Law Discovery Demo")
    print("=" * 60)
    np.random.seed(42)
    lens = ScaleLens()

    # Demo 1: Power law data
    print("\n--- Demo 1: y = 2 * x^1.5 + noise ---")
    x = np.random.uniform(1, 100, 200)
    y = 2 * x ** 1.5 + np.random.randn(200) * 10
    data = np.column_stack([x, y])
    r = lens.scan(data)
    print(r.summary)
    for pl in r.power_law_fits:
        print(f"  {pl.description}")

    # Demo 2: Fractal/Hurst analysis
    print("\n--- Demo 2: Brownian vs anti-persistent signal ---")
    # Brownian motion (H ≈ 0.5)
    brownian = np.cumsum(np.random.randn(500))
    # Persistent (H > 0.5)
    persistent = np.cumsum(np.sign(np.random.randn(500)) * np.abs(np.random.randn(500)) ** 0.3)
    data2 = np.column_stack([brownian, persistent])
    r = lens.scan(data2)
    print(r.summary)
    for j, h in r.hurst_exponents:
        print(f"  Feature {j}: Hurst={h:.3f}")

    # Demo 3: n=6 constants
    print("\n--- Demo 3: n=6 constant scaling ---")
    n6 = [1, 2, 5, 6, 12, 720]
    r = lens.scan_constants(n6, ['mu', 'phi', 'sopfr', 'n', 'sigma', 'n!'])
    print(r.summary)
