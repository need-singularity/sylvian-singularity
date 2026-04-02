"""compass_lens.py — Curvature & circularity discovery lens (컴퍼스)

Use a compass as a telescope: detect circular structures, curvature,
equidistant relationships, closed loops, and radial symmetry in ANY data.

How it works:
  1. Distance matrix → radial distribution from centroid
  2. Curvature estimation along data manifold (Menger curvature)
  3. Circle/sphere fitting → detect constant-radius structures
  4. Closed loop detection → features that return to origin
  5. Equidistance analysis → points at equal spacing

Works with numpy + scipy.spatial.distance. Portable across all projects.

Usage:
    from compass_lens import CompassLens

    lens = CompassLens()
    r = lens.scan(data)
    print(r.curvature_stats)       # mean/std/max curvature
    print(r.circular_structures)   # detected circles/arcs
    print(r.equidistant_groups)    # equidistant point groups
    print(r.radial_symmetry)       # radial symmetry score
"""
import os, sys, math
from dataclasses import dataclass, field
from typing import List, Tuple, Dict, Any
import numpy as np
from scipy.spatial.distance import pdist, squareform

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from consciousness_loader import PSI_ALPHA, PSI_BALANCE, PSI_ENTROPY


@dataclass
class CircularStructure:
    """A detected circular or arc-like structure."""
    center: np.ndarray = field(default_factory=lambda: np.array([]))
    radius: float = 0.0
    fit_error: float = 0.0
    point_indices: List[int] = field(default_factory=list)
    arc_fraction: float = 0.0  # 0~1, how much of circle is covered


@dataclass
class CompassResult:
    """Result from compass (curvature/circularity) lens scan."""
    curvature_mean: float = 0.0
    curvature_std: float = 0.0
    curvature_max: float = 0.0
    curvatures: np.ndarray = field(default_factory=lambda: np.array([]))
    circular_structures: List[CircularStructure] = field(default_factory=list)
    equidistant_groups: List[Tuple[List[int], float, float]] = field(default_factory=list)
    radial_symmetry: float = 0.0
    radial_distances: np.ndarray = field(default_factory=lambda: np.array([]))
    closed_loops: List[List[int]] = field(default_factory=list)
    summary: str = ""

    def __repr__(self):
        return (f"CompassResult(curvature={self.curvature_mean:.4f}+/-{self.curvature_std:.4f}, "
                f"circles={len(self.circular_structures)}, "
                f"equidistant={len(self.equidistant_groups)}, "
                f"radial_sym={self.radial_symmetry:.3f})")


class CompassLens:
    """Curvature & circularity discovery lens — compass as telescope."""

    def __init__(self, equidist_tol: float = 0.05, min_arc_points: int = 4,
                 circle_fit_tol: float = 0.1):
        self.equidist_tol = equidist_tol
        self.min_arc = min_arc_points
        self.circle_tol = circle_fit_tol

    def _menger_curvature(self, p1, p2, p3):
        """Menger curvature of three points = 1/R of circumscribed circle."""
        a = np.linalg.norm(p2 - p1)
        b = np.linalg.norm(p3 - p2)
        c = np.linalg.norm(p3 - p1)
        if a < 1e-30 or b < 1e-30 or c < 1e-30:
            return 0.0
        s = (a + b + c) / 2
        area_sq = s * (s - a) * (s - b) * (s - c)
        if area_sq <= 0:
            return 0.0
        area = math.sqrt(area_sq)
        return 4 * area / (a * b * c)

    def _estimate_curvatures(self, data):
        """Estimate local curvature at each point using nearest neighbors."""
        n = data.shape[0]
        if n < 3:
            return np.zeros(n)

        dists = squareform(pdist(data))
        curvatures = np.zeros(n)
        for i in range(n):
            # Find 2 nearest neighbors
            sorted_idx = np.argsort(dists[i])
            neighbors = sorted_idx[1:3]  # exclude self
            if len(neighbors) < 2:
                continue
            curvatures[i] = self._menger_curvature(
                data[i], data[neighbors[0]], data[neighbors[1]])
        return curvatures

    def _fit_circle_2d(self, points):
        """Algebraic circle fit (Kasa method) for 2D points."""
        if points.shape[0] < 3 or points.shape[1] < 2:
            return None
        pts = points[:, :2]
        A = np.column_stack([2 * pts, np.ones(len(pts))])
        b = (pts ** 2).sum(axis=1)
        try:
            result = np.linalg.lstsq(A, b, rcond=None)
            params = result[0]
        except np.linalg.LinAlgError:
            return None
        cx, cy = params[0], params[1]
        r = math.sqrt(params[2] + cx**2 + cy**2)
        distances = np.sqrt((pts[:, 0] - cx)**2 + (pts[:, 1] - cy)**2)
        error = float(np.std(distances - r) / (r + 1e-30))
        return np.array([cx, cy]), r, error, distances

    def _find_equidistant_groups(self, dists, n):
        """Find groups of points equidistant from each other."""
        groups = []
        for anchor in range(min(n, 50)):  # limit anchor points
            d = dists[anchor]
            d_sorted = np.sort(d[d > 1e-30])
            if len(d_sorted) < 3:
                continue
            # Look for clusters of similar distances
            for i in range(len(d_sorted) - 2):
                ref = d_sorted[i]
                if ref < 1e-30:
                    continue
                matches = np.where(np.abs(d - ref) / ref < self.equidist_tol)[0]
                matches = matches[matches != anchor]
                if len(matches) >= 3:
                    groups.append((
                        [anchor] + list(matches),
                        float(ref),
                        float(np.std(d[matches]) / ref)
                    ))
        # Deduplicate by sorted point set
        seen = set()
        unique = []
        for group, dist, std in groups:
            key = tuple(sorted(group))
            if key not in seen:
                seen.add(key)
                unique.append((group, dist, std))
        return unique[:20]  # top 20

    def _detect_closed_loops(self, data, dists):
        """Detect sequences of points that form closed loops."""
        n = data.shape[0]
        if n < 4:
            return []
        loops = []
        # Greedy nearest-neighbor path, check if it closes
        visited = [False] * n
        for start in range(min(n, 20)):
            path = [start]
            visited_local = {start}
            current = start
            for _ in range(n - 1):
                d = dists[current].copy()
                d[list(visited_local)] = np.inf
                nxt = np.argmin(d)
                if d[nxt] == np.inf:
                    break
                path.append(nxt)
                visited_local.add(nxt)
                current = nxt
            # Check if path closes back to start
            if len(path) >= 4:
                close_dist = dists[current, start]
                avg_step = np.mean([dists[path[i], path[i+1]] for i in range(len(path)-1)])
                if avg_step > 1e-30 and close_dist / avg_step < 2.0:
                    loops.append(path)
        return loops[:5]

    def _radial_symmetry(self, data):
        """Measure radial symmetry around centroid."""
        centroid = data.mean(axis=0)
        dists = np.linalg.norm(data - centroid, axis=1)
        if dists.mean() < 1e-30:
            return 0.0, dists
        cv = float(dists.std() / dists.mean())  # coefficient of variation
        symmetry = max(0.0, 1.0 - cv)  # 1 = perfect sphere, 0 = asymmetric
        return symmetry, dists

    def scan(self, data, verbose=True):
        data = np.asarray(data, dtype=np.float64)
        if data.ndim == 1:
            data = data.reshape(-1, 1)
        n, d = data.shape

        # Curvature estimation
        curvatures = self._estimate_curvatures(data)
        c_mean = float(np.mean(curvatures))
        c_std = float(np.std(curvatures))
        c_max = float(np.max(curvatures)) if len(curvatures) > 0 else 0.0

        # Distance matrix
        if n > 1:
            dists = squareform(pdist(data))
        else:
            dists = np.zeros((1, 1))

        # Circle fitting (for 2D+ data)
        circles = []
        if d >= 2 and n >= self.min_arc:
            fit = self._fit_circle_2d(data)
            if fit and fit[2] < self.circle_tol:
                center, radius, error, pt_dists = fit
                circles.append(CircularStructure(
                    center=center, radius=radius, fit_error=error,
                    point_indices=list(range(n)), arc_fraction=1.0))

            # Try fitting subsets (quadrants) for partial arcs
            if n >= self.min_arc * 2:
                centroid = data[:, :2].mean(axis=0)
                for quad in range(4):
                    angle_lo = quad * math.pi / 2
                    angle_hi = (quad + 1) * math.pi / 2
                    angles = np.arctan2(data[:, 1] - centroid[1], data[:, 0] - centroid[0])
                    angles = angles % (2 * math.pi)
                    mask = (angles >= angle_lo) & (angles < angle_hi)
                    subset_idx = np.where(mask)[0]
                    if len(subset_idx) >= self.min_arc:
                        fit = self._fit_circle_2d(data[subset_idx])
                        if fit and fit[2] < self.circle_tol * 0.5:
                            center, radius, error, _ = fit
                            circles.append(CircularStructure(
                                center=center, radius=radius, fit_error=error,
                                point_indices=list(subset_idx),
                                arc_fraction=len(subset_idx) / n))

        # Equidistant groups
        equi_groups = self._find_equidistant_groups(dists, n) if n > 3 else []

        # Radial symmetry
        rad_sym, rad_dists = self._radial_symmetry(data)

        # Closed loops
        loops = self._detect_closed_loops(data, dists) if n > 3 else []

        summary = (f"Points: {n}, Dims: {d}, "
                   f"Curvature: {c_mean:.4f}+/-{c_std:.4f} (max={c_max:.4f}), "
                   f"Circles: {len(circles)}, "
                   f"Equidistant groups: {len(equi_groups)}, "
                   f"Radial symmetry: {rad_sym:.3f}, "
                   f"Closed loops: {len(loops)}")

        return CompassResult(
            curvature_mean=c_mean,
            curvature_std=c_std,
            curvature_max=c_max,
            curvatures=curvatures,
            circular_structures=circles,
            equidistant_groups=equi_groups,
            radial_symmetry=rad_sym,
            radial_distances=rad_dists,
            closed_loops=loops,
            summary=summary)

    def scan_constants(self, constants, labels=None):
        """Scan 1D array of constants for equidistant/circular patterns."""
        constants = np.asarray(constants, dtype=np.float64).flatten()
        names = labels or [f"c{i}" for i in range(len(constants))]
        # Embed on unit circle by normalized position
        mn, mx = constants.min(), constants.max()
        if mx - mn < 1e-30:
            normed = np.zeros_like(constants)
        else:
            normed = (constants - mn) / (mx - mn) * 2 * math.pi
        pts = np.column_stack([np.cos(normed), np.sin(normed)])
        r = self.scan(pts, verbose=False)

        # Also check for equidistant values in 1D
        sorted_vals = np.sort(constants)
        diffs = np.diff(sorted_vals)
        if len(diffs) > 1 and diffs.mean() > 1e-30:
            cv = diffs.std() / diffs.mean()
            if cv < 0.1:
                r.summary += f"\n  Equidistant 1D: spacing={diffs.mean():.6f} (CV={cv:.4f})"

        parts = [r.summary]
        if r.equidistant_groups:
            parts.append("Equidistant groups:")
            for group, dist, std in r.equidistant_groups[:5]:
                gnames = [names[i] for i in group if i < len(names)]
                parts.append(f"  {gnames} at distance {dist:.4f} (std={std:.4f})")
        r.summary = "\n".join(parts)
        return r

    def scan_materials(self, properties, labels=None):
        r = self.scan(properties, verbose=False)
        parts = [r.summary]
        if r.circular_structures:
            parts.append("Circular structures: " + ", ".join(
                f"R={c.radius:.3f}(err={c.fit_error:.4f})" for c in r.circular_structures[:3]))
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
                # Phase space embedding
                if len(s) > 2:
                    curvs = [self._menger_curvature(
                        np.array([i, s[i]]),
                        np.array([i+1, s[i+1]]),
                        np.array([i+2, s[i+2]]))
                        for i in range(len(s)-2)]
                    f.extend([np.mean(curvs), np.std(curvs)])
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
                f.extend([c.mean(), c.std(), c.max() - c.min()])
                # Return-to-origin metric
                f.append(abs(c[-1] - c[0]) / (c.std() + 1e-30))
            feats.append(f)
        r = self.scan(np.array(feats), verbose=False)
        r.summary += f"\nTimeseries: {nt} steps, {nv} vars, {nw} windows"
        return r


# ---------------------------------------------------------------------------
if __name__ == '__main__':
    print("=" * 60)
    print("  Compass Lens (컴퍼스) -- Curvature & Circle Discovery Demo")
    print("=" * 60)
    np.random.seed(42)
    lens = CompassLens()

    # Demo 1: Circle data
    print("\n--- Demo 1: Points on a circle ---")
    theta = np.linspace(0, 2 * math.pi, 30, endpoint=False)
    circle_data = np.column_stack([np.cos(theta) + np.random.randn(30) * 0.05,
                                    np.sin(theta) + np.random.randn(30) * 0.05])
    r = lens.scan(circle_data)
    print(r.summary)
    if r.circular_structures:
        print(f"  Best circle: R={r.circular_structures[0].radius:.4f}, "
              f"error={r.circular_structures[0].fit_error:.4f}")

    # Demo 2: n=6 constants on unit circle
    print("\n--- Demo 2: n=6 constants circular embedding ---")
    n6 = [6, 12, 2, 5, 2, 1, 720]
    r = lens.scan_constants(n6, ['n', 'sigma', 'phi', 'sopfr', 'tau', 'mu', 'n!'])
    print(r.summary)

    # Demo 3: Spiral (changing curvature)
    print("\n--- Demo 3: Spiral data (varying curvature) ---")
    t = np.linspace(0.5, 4 * math.pi, 80)
    spiral = np.column_stack([t * np.cos(t), t * np.sin(t)])
    r = lens.scan(spiral)
    print(r.summary)
    print(f"  Curvature range: {r.curvatures.min():.4f} ~ {r.curvatures.max():.4f}")

    # Demo 4: Equidistant clusters
    print("\n--- Demo 4: Equidistant clusters ---")
    centers = np.array([[0,0], [3,0], [6,0], [9,0]], dtype=float)
    pts = np.vstack([c + np.random.randn(10, 2) * 0.3 for c in centers])
    r = lens.scan(pts)
    print(r.summary)
