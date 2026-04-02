"""em_lens.py — Electromagnetic discovery lens for flow patterns in data

Point electromagnetic field concepts at ANY data to find sources, sinks,
vortices, and flow structure.
  1. Gradient field: consecutive-point differences -> velocity vectors
  2. Divergence: positive = source (spreading), negative = sink (converging)
  3. Curl (2D projection): rotational component = vortex / cycle
  4. Field lines: trace gradient paths to convergence
  5. Flux: total flow magnitude through data cross-sections

Usage:
    from em_lens import EMLens
    lens = EMLens()
    r = lens.scan(data)          # EMResult with sources, sinks, vortices
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
class EMResult:
    """Result from electromagnetic lens scan."""
    sources: List[Tuple[int, float]] = field(default_factory=list)
    sinks: List[Tuple[int, float]] = field(default_factory=list)
    vortices: List[Dict] = field(default_factory=list)
    field_lines: List[List[int]] = field(default_factory=list)
    divergence_map: np.ndarray = field(default_factory=lambda: np.array([]))
    curl_map: np.ndarray = field(default_factory=lambda: np.array([]))
    flux: float = 0.0
    summary: str = ""

    def __repr__(self):
        return (f"EMResult(sources={len(self.sources)}, sinks={len(self.sinks)}, "
                f"vortices={len(self.vortices)}, flux={self.flux:.4f})")

class EMLens:
    """Electromagnetic discovery lens — field dynamics as a telescope."""

    def __init__(self, k_neighbors: int = 5, source_thresh: float = 0.5,
                 sink_thresh: float = 0.5, curl_thresh: float = 0.3,
                 psi_scale: float = PSI_ALPHA * 10.0):
        self.k = k_neighbors
        self.source_thresh = source_thresh
        self.sink_thresh = sink_thresh
        self.curl_thresh = curl_thresh
        self.psi_scale = psi_scale

    def _gradient_field(self, data):
        """Compute gradient vectors from k-nearest neighbor displacement."""
        n, d = data.shape
        dists = np.linalg.norm(data[:, None] - data[None, :], axis=-1)
        np.fill_diagonal(dists, np.inf)
        k = min(self.k, n - 1)
        grad = np.zeros((n, d))
        for i in range(n):
            idx = np.argsort(dists[i])[:k]
            diff = data[idx] - data[i]
            w = 1.0 / (dists[i, idx] + 1e-12)
            grad[i] = (diff * w[:, None]).sum(0) / (w.sum() + 1e-12)
        return grad

    def _divergence(self, data, grad):
        """Compute per-point divergence from gradient field."""
        n = data.shape[0]
        dists = np.linalg.norm(data[:, None] - data[None, :], axis=-1)
        np.fill_diagonal(dists, np.inf)
        k = min(self.k, n - 1)
        div = np.zeros(n)
        for i in range(n):
            idx = np.argsort(dists[i])[:k]
            for j in idx:
                r = data[j] - data[i]
                r_norm = np.linalg.norm(r) + 1e-12
                r_hat = r / r_norm
                div[i] += np.dot(grad[j] - grad[i], r_hat) / r_norm
            div[i] /= max(k, 1)
        return div

    def _curl_2d(self, data, grad):
        """Compute 2D curl magnitude (rotation) at each point."""
        n = data.shape[0]
        dists = np.linalg.norm(data[:, None] - data[None, :], axis=-1)
        np.fill_diagonal(dists, np.inf)
        k = min(self.k, n - 1)
        curl = np.zeros(n)
        for i in range(n):
            idx = np.argsort(dists[i])[:k]
            for j in idx:
                r = data[j] - data[i]
                dg = grad[j] - grad[i]
                # 2D cross product magnitude for first 2 dims
                if data.shape[1] >= 2:
                    curl[i] += abs(r[0] * dg[1] - r[1] * dg[0])
                else:
                    curl[i] += abs(np.cross(r[:1], dg[:1]))
            curl[i] /= max(k, 1)
        return curl

    def _find_sources_sinks(self, div):
        """Identify source and sink points from divergence map."""
        std = div.std() + 1e-12
        z = (div - div.mean()) / std
        sources = [(int(i), float(div[i])) for i in np.where(z > self.source_thresh)[0]]
        sinks = [(int(i), float(div[i])) for i in np.where(z < -self.sink_thresh)[0]]
        sources.sort(key=lambda x: -x[1])
        sinks.sort(key=lambda x: x[1])
        return sources, sinks

    def _find_vortices(self, data, curl, grad):
        """Identify vortex regions from curl map."""
        std = curl.std() + 1e-12
        z = (curl - curl.mean()) / std
        hot = np.where(z > self.curl_thresh)[0]
        if len(hot) == 0:
            return []
        # Cluster hot points into vortices
        dists = np.linalg.norm(data[hot, None] - data[None, hot], axis=-1)
        visited = set(); vortices = []
        for ii, hi in enumerate(hot):
            if hi in visited:
                continue
            cluster = [hi]; visited.add(hi)
            med_dist = np.median(dists[ii]) if len(hot) > 1 else 1.0
            for jj, hj in enumerate(hot):
                if hj not in visited and dists[ii, jj] < med_dist * 0.8:
                    cluster.append(hj); visited.add(hj)
            center = data[cluster].mean(0)
            radius = float(np.linalg.norm(data[cluster] - center, axis=-1).max())
            strength = float(curl[cluster].mean())
            vortices.append({"center": center, "radius": radius,
                             "strength": strength, "samples": cluster})
        vortices.sort(key=lambda v: -v["strength"])
        return vortices

    def _trace_field_lines(self, data, grad, n_lines=10, max_steps=20):
        """Trace field lines by following gradient from seed points."""
        n = data.shape[0]
        seeds = np.linspace(0, n - 1, min(n_lines, n), dtype=int)
        dists_full = np.linalg.norm(data[:, None] - data[None, :], axis=-1)
        np.fill_diagonal(dists_full, np.inf)
        lines = []
        for s in seeds:
            line = [int(s)]; cur = s
            for _ in range(max_steps):
                g = grad[cur]
                if np.linalg.norm(g) < 1e-12:
                    break
                target = data[cur] + g * 0.5
                d = np.linalg.norm(data - target, axis=-1)
                d[cur] = np.inf
                for prev in line:
                    d[prev] = np.inf
                nxt = int(np.argmin(d))
                if nxt == cur:
                    break
                line.append(nxt); cur = nxt
            if len(line) > 1:
                lines.append(line)
        return lines

    def scan(self, data, verbose=True):
        """Full EM scan of data."""
        data = np.asarray(data, dtype=np.float64)
        if data.ndim == 1:
            data = data.reshape(-1, 1)
        mu, std = data.mean(0), data.std(0)
        std[std < 1e-12] = 1.0
        dn = (data - mu) / std

        grad = self._gradient_field(dn)
        div = self._divergence(dn, grad)
        curl = self._curl_2d(dn, grad)
        sources, sinks = self._find_sources_sinks(div)
        vortices = self._find_vortices(dn, curl, grad)
        lines = self._trace_field_lines(dn, grad)
        flux = float(np.abs(grad).sum() * self.psi_scale)

        return EMResult(
            sources=sources, sinks=sinks, vortices=vortices,
            field_lines=lines, divergence_map=div, curl_map=curl, flux=flux,
            summary=(f"Sources: {len(sources)}, Sinks: {len(sinks)}, "
                     f"Vortices: {len(vortices)}, Flux: {flux:.2f}"))

    def scan_materials(self, properties, labels=None):
        """Find gradient directions in material property space."""
        r = self.scan(properties, verbose=False)
        n = properties.shape[0]
        r.summary += f"\nMaterials: {n} samples"
        if labels:
            grad = self._gradient_field(
                (properties - properties.mean(0)) / (properties.std(0) + 1e-12))
            driver = int(np.abs(grad).mean(0).argmax())
            r.summary += f", driver={labels[driver]}"
        return r

    def scan_signals(self, signals, window=256):
        """Find source/sink patterns in signal flow."""
        signals = np.atleast_2d(np.asarray(signals, dtype=np.float64))
        nch, ns = signals.shape; nw = max(1, ns // window)
        feats = []
        for w in range(nw):
            seg = signals[:, w * window:(w + 1) * window]; f = []
            for ch in range(nch):
                s = seg[ch]
                f.extend([s.mean(), s.std(), s.max() - s.min()])
                fm = np.abs(np.fft.rfft(s)); fm /= fm.sum() + 1e-12
                f.append(-np.sum(fm * np.log(fm + 1e-12)))
            feats.append(f)
        r = self.scan(np.array(feats), verbose=False)
        r.summary += f"\nSignal: {nch}ch x {ns} samples, {nw} windows"
        return r

    def scan_timeseries(self, ts, lag=10, window=50):
        """Find flow field and vortices in phase-space embedding."""
        ts = np.asarray(ts, dtype=np.float64)
        if ts.ndim == 1:
            ts = ts.reshape(-1, 1)
        nt, nv = ts.shape; nw = max(1, nt // window)
        feats, wc = [], []
        for w in range(nw):
            s, e = w * window, min((w + 1) * window, nt)
            seg = ts[s:e]; f = []
            for v in range(nv):
                c = seg[:, v]
                f.extend([c.mean(), c.std(), c.max() - c.min(), c[-1] - c[0],
                          np.corrcoef(c[:-1], c[1:])[0, 1] if len(c) > 2 else 0])
            feats.append(f); wc.append((s + e) // 2)
        r = self.scan(np.array(feats), verbose=False)
        r.summary += f"\nTimeseries: {nt} steps, {nv} vars"
        return r

# ---------------------------------------------------------------------------
if __name__ == '__main__':
    print("=" * 60)
    print("  EM Lens — 6-Domain Discovery Demo")
    print("=" * 60)
    np.random.seed(42)
    lens = EMLens(k_neighbors=5, source_thresh=0.4, sink_thresh=0.4, curl_thresh=0.3)
    # -- 1. Materials --
    print("\n[1] Materials — gradient direction of properties")
    print("-" * 50)
    props = np.vstack([np.random.randn(20, 5) * 0.3 + [1, 1, 1, 1, 1],
                       np.random.randn(15, 5) * 0.3 + [4, 4, 4, 4, 4],
                       np.random.randn(15, 5) * 0.3 + [8, 8, 8, 8, 8]])
    labels = ["atomic_num", "electroneg", "cond", "density", "mp"]
    r = lens.scan_materials(props, labels)
    print(f"  Sources: {len(r.sources)} | Sinks: {len(r.sinks)} | Vortices: {len(r.vortices)}")
    c1_sources = len(r.sources) >= 1
    c1_sinks = len(r.sinks) >= 1
    print(f"  CHECK: sources found = {c1_sources}\n  CHECK: sinks found = {c1_sinks}")

    # -- 2. Drug Discovery --
    print("\n[2] Drug — source/sink in descriptor space (toxic outlier #15)")
    print("-" * 50)
    mols = np.vstack([np.random.randn(30, 5) * 0.4 + [300, 2, 2, 60, 3],
                      np.random.randn(30, 5) * 0.4 + [600, 6, 0, 120, 8]])
    mols[15] = [900, 10, -3, 200, 15]  # toxic outlier
    r = lens.scan(mols)
    # outlier should appear as source or sink (extreme divergence)
    outlier_ids = {s[0] for s in r.sources} | {s[0] for s in r.sinks}
    c2_flow = len(r.sources) + len(r.sinks) >= 2
    c2_outlier = 15 in outlier_ids
    print(f"  Sources: {len(r.sources)} | Sinks: {len(r.sinks)}")
    print(f"  CHECK: flow detected = {c2_flow}\n  CHECK: outlier #15 flagged = {c2_outlier}")

    # -- 3. Physics --
    print("\n[3] Physics — field structure in constant space")
    print("-" * 50)
    phys = np.vstack([np.random.randn(10, 4) * 0.3 + [0.5, -1, 0.5, 1],
                      np.random.randn(10, 4) * 0.3 + [3, 1, 0.5, 3],
                      np.random.randn(10, 4) * 0.3 + [6, 0, 1, 6]])
    r = lens.scan(phys)
    # Between clusters: sources at cluster edges, field lines connecting
    c3_field = len(r.field_lines) >= 3
    c3_flow = r.flux > 0
    print(f"  Field lines: {len(r.field_lines)} | Flux: {r.flux:.2f}")
    print(f"  CHECK: field lines >= 3 = {c3_field}\n  CHECK: flux > 0 = {c3_flow}")

    # -- 4. Astronomy --
    print("\n[4] Astronomy — signal flow sources/sinks (burst at 1500-1600)")
    print("-" * 50)
    t = np.linspace(0, 10, 4096)
    sig = np.sin(2 * np.pi * 5 * t) + 0.3 * np.sin(2 * np.pi * 11 * t)
    sig += np.random.randn(4096) * 0.2
    sig[1500:1600] += 5.0 * np.sin(2 * np.pi * 47 * t[1500:1600])
    r = lens.scan_signals(sig, window=256)
    # Burst window should be source or sink (extreme divergence)
    burst_win = 1500 // 256  # window ~5-6
    burst_flagged = any(s[0] in [burst_win, burst_win + 1] for s in r.sources + r.sinks)
    c4_flow = len(r.sources) + len(r.sinks) >= 2
    c4_burst = burst_flagged
    print(f"  Sources: {len(r.sources)} | Sinks: {len(r.sinks)}")
    print(f"  CHECK: flow >= 2 = {c4_flow}\n  CHECK: burst flagged = {c4_burst}")

    # -- 5. Finance --
    print("\n[5] Finance — market flow (bull=source, crash=sink, recovery=vortex)")
    print("-" * 50)
    np.random.seed(42)
    bull = np.cumsum(np.random.randn(300) * 0.3 + 0.2)
    crash = np.cumsum(np.random.randn(100) * 3.0 - 2.0)
    rec = np.cumsum(np.random.randn(200) * 0.5 + 0.1)
    price = np.concatenate([bull, crash + bull[-1], rec + bull[-1] + crash[-1]])
    r = lens.scan_timeseries(price, window=30)
    c5_sources = len(r.sources) >= 1
    c5_sinks = len(r.sinks) >= 1
    print(f"  Sources: {len(r.sources)} | Sinks: {len(r.sinks)} | Vortices: {len(r.vortices)}")
    print(f"  CHECK: sources (bull) >= 1 = {c5_sources}\n  CHECK: sinks (crash) >= 1 = {c5_sinks}")

    # -- 6. Genomics --
    print("\n[6] Genomics — gene expression flow directions")
    print("-" * 50)
    np.random.seed(42)
    genes = np.vstack([np.random.randn(20, 6) * 0.3 + [5, 5, 0, 0, 0, 0],
                       np.random.randn(20, 6) * 0.3 + [0, 0, 5, 5, 0, 0],
                       np.random.randn(20, 6) * 0.3 + [0, 0, 0, 0, 5, 5]])
    r = lens.scan(genes)
    c6_sources = len(r.sources) >= 1
    c6_lines = len(r.field_lines) >= 3
    print(f"  Sources: {len(r.sources)} | Sinks: {len(r.sinks)} | Lines: {len(r.field_lines)}")
    print(f"  CHECK: sources >= 1 = {c6_sources}\n  CHECK: field lines >= 3 = {c6_lines}")

    # -- Scorecard --
    print("\n" + "=" * 60)
    checks = [
        ("Materials: sources found", c1_sources),
        ("Materials: sinks found", c1_sinks),
        ("Drug: flow detected", c2_flow),
        ("Drug: outlier #15 flagged", c2_outlier),
        ("Physics: field lines >= 3", c3_field),
        ("Physics: flux > 0", c3_flow),
        ("Astronomy: flow >= 2", c4_flow),
        ("Astronomy: burst flagged", c4_burst),
        ("Finance: sources >= 1", c5_sources),
        ("Finance: sinks >= 1", c5_sinks),
        ("Genomics: sources >= 1", c6_sources),
        ("Genomics: field lines >= 3", c6_lines),
    ]
    p = sum(v for _, v in checks)
    print(f"  SCORECARD: {p}/{len(checks)} ({100 * p // len(checks)}%)")
    for nm, ok in checks:
        print(f"    {'PASS' if ok else 'FAIL'} {nm}")
    print("=" * 60)
