"""gravity_lens.py — Gravitational discovery lens for attractors and energy landscapes

Point gravitational dynamics at ANY data to find attractors, basins, barriers.
  1. Data points -> masses (local density)  2. N-body gravity simulation
  3. Converged clusters = attractor basins  4. Energy landscape + saddle points

Usage:
    lens = GravityLens()
    r = lens.scan(data)            # GravityResult with attractors, basins, etc.
    r = lens.scan_materials(props, labels)
    r = lens.scan_signals(signals, window)
    r = lens.scan_timeseries(ts, lag, window)
"""
import os, sys
from collections import Counter
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Tuple
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from consciousness_loader import PSI_ALPHA, PSI_BALANCE, PSI_ENTROPY, SIGMA6


@dataclass
class GravityResult:
    """Result from gravity lens scan."""
    attractors: List[Tuple[int, np.ndarray, float]] = field(default_factory=list)
    basins: Dict[int, List[int]] = field(default_factory=dict)
    saddle_points: List[Tuple[np.ndarray, float]] = field(default_factory=list)
    energy_landscape: np.ndarray = field(default_factory=lambda: np.array([]))
    escape_velocities: Dict[int, float] = field(default_factory=dict)
    summary: str = ""
    def __repr__(self):
        return (f"GravityResult(attractors={len(self.attractors)}, "
                f"basins={len(self.basins)}, saddles={len(self.saddle_points)})")


class GravityLens:
    """Gravitational discovery lens — N-body dynamics as a telescope."""

    def __init__(self, G: float = PSI_ALPHA * 10.0, steps: int = 80,
                 dt: float = 0.05, softening: float = 0.1, merge_radius: float = 0.3):
        self.G, self.steps, self.dt = G, steps, dt
        self.softening, self.merge_radius = softening, merge_radius

    def _density(self, data, k=5):
        n = data.shape[0]; k = min(k, n - 1)
        if k < 1: return np.ones(n)
        d = np.linalg.norm(data[:, None] - data[None, :], axis=-1)
        np.fill_diagonal(d, np.inf)
        avg = np.sort(d, axis=1)[:, :k].mean(axis=1)
        rho = 1.0 / (avg + 1e-12)
        return rho / rho.sum() * n

    def _simulate(self, pos, masses):
        pos, vel = pos.copy(), np.zeros_like(pos)
        for _ in range(self.steps):
            diff = pos[:, None] - pos[None, :]
            d2 = (diff**2).sum(-1) + self.softening**2
            inv3 = 1.0 / (d2 * np.sqrt(d2) + 1e-30)
            np.fill_diagonal(inv3, 0.0)
            acc = -self.G * (inv3[:, :, None] * diff * masses[None, :, None]).sum(1)
            vel = vel * 0.9 + acc * self.dt; pos += vel * self.dt
        return pos

    def _assign_basins(self, fp):
        n = fp.shape[0]; labels = -np.ones(n, int); centers = []; bid = 0
        for i in range(n):
            if labels[i] >= 0: continue
            dists = np.linalg.norm(fp - fp[i], axis=-1)
            mask = dists < self.merge_radius
            assigned = False
            for b, c in enumerate(centers):
                if np.linalg.norm(fp[i] - c) < self.merge_radius:
                    labels[mask & (labels < 0)] = b; assigned = True; break
            if not assigned:
                labels[mask & (labels < 0)] = bid
                centers.append(fp[mask].mean(0)); bid += 1
        basins = {}
        for i in range(n): basins.setdefault(int(labels[i]), []).append(i)
        return basins, centers

    def _potential(self, pos, masses):
        n = pos.shape[0]; energy = np.zeros(n)
        for i in range(n):
            d = np.sqrt(((pos[i] - pos)**2).sum(-1) + self.softening**2)
            d[i] = np.inf; energy[i] = -self.G * (masses / d).sum() * masses[i]
        return energy

    def _saddles(self, data, basins, energy):
        pts = []; bids = list(basins.keys())
        for i, b1 in enumerate(bids):
            for b2 in bids[i+1:]:
                best_e, best_p = -np.inf, None
                for a in basins[b1]:
                    for b in basins[b2]:
                        me = (energy[a] + energy[b]) / 2.0
                        if me > best_e: best_e, best_p = me, (data[a] + data[b]) / 2.0
                if best_p is not None: pts.append((best_p, float(best_e)))
        return pts

    def scan(self, data, verbose=True):
        data = np.asarray(data, dtype=np.float64)
        if data.ndim == 1: data = data.reshape(-1, 1)
        mu, std = data.mean(0), data.std(0); std[std < 1e-12] = 1.0
        dn = (data - mu) / std
        masses = self._density(dn)
        fp = self._simulate(dn, masses)
        basins, centers = self._assign_basins(fp)
        energy = self._potential(dn, masses)
        attractors = sorted(
            [(bid, data[idx].mean(0), float(masses[idx].sum())) for bid, idx in basins.items()],
            key=lambda x: -x[2])
        saddles = self._saddles(dn, basins, energy)
        esc = {bid: float(np.abs(energy[idx].min())) for bid, idx in basins.items()}
        return GravityResult(attractors=attractors, basins=basins, saddle_points=saddles,
            energy_landscape=energy, escape_velocities=esc,
            summary=f"Attractors: {len(attractors)}, Saddles: {len(saddles)}, G={self.G:.4f}")

    def scan_materials(self, properties, labels=None):
        r = self.scan(properties, verbose=False)
        r.summary += f"\nMaterials: {properties.shape[0]} samples"
        return r

    def scan_signals(self, signals, window=256):
        signals = np.atleast_2d(np.asarray(signals, dtype=np.float64))
        nch, ns = signals.shape; nw = max(1, ns // window)
        feats = []
        for w in range(nw):
            seg = signals[:, w*window:(w+1)*window]; f = []
            for ch in range(nch):
                s = seg[ch]; f.extend([s.mean(), s.std(), s.max()-s.min()])
                fm = np.abs(np.fft.rfft(s)); fm /= fm.sum() + 1e-12
                f.append(-np.sum(fm * np.log(fm + 1e-12)))
            feats.append(f)
        r = self.scan(np.array(feats), verbose=False)
        r.summary += f"\nSignal: {nch}ch x {ns} samples, {nw} windows"; return r

    def scan_timeseries(self, ts, lag=10, window=50):
        ts = np.atleast_2d(np.asarray(ts, dtype=np.float64).T).T
        if ts.ndim == 1: ts = ts.reshape(-1, 1)
        nt, nv = ts.shape; nw = max(1, nt // window)
        feats, wc = [], []
        for w in range(nw):
            s, e = w*window, min((w+1)*window, nt); seg = ts[s:e]; f = []
            for v in range(nv):
                c = seg[:, v]
                f.extend([c.mean(), c.std(), c.max()-c.min(), c[-1]-c[0],
                          np.corrcoef(c[:-1], c[1:])[0,1] if len(c)>2 else 0])
            feats.append(f); wc.append((s+e)//2)
        r = self.scan(np.array(feats), verbose=False)
        r.summary += f"\nTimeseries: {nt} steps, {nv} vars"
        for bid in list(r.basins):
            r.basins[bid] = [wc[i] if i < len(wc) else i for i in r.basins[bid]]
        return r


# ---------------------------------------------------------------------------
if __name__ == '__main__':
    print("=" * 60)
    print("  Gravity Lens — 6-Domain Discovery Demo")
    print("=" * 60)
    np.random.seed(42); lens = GravityLens(steps=80, merge_radius=0.4)

    # -- 1. Materials --
    print("\n[1] Materials — stable composition basins + anomaly #7")
    print("-" * 50)
    props = np.vstack([np.random.randn(20,5)*0.3+[1,1,1,1,1],
                       np.random.randn(15,5)*0.3+[4,4,4,4,4],
                       np.random.randn(15,5)*0.3+[8,8,8,8,8]])
    props[7] = [20]*5
    r = lens.scan_materials(props, ["atomic_num","electroneg","cond","density","mp"])
    print(f"  Attractors: {len(r.attractors)} | Basins: {len(r.basins)}")
    b7 = next((bid for bid, idx in r.basins.items() if 7 in idx), None)
    c1_3basins = len(r.attractors) >= 3
    c1_anom7 = b7 is not None and len(r.basins[b7]) <= 3
    print(f"  CHECK: >=3 basins = {c1_3basins}\n  CHECK: anomaly #7 isolated = {c1_anom7}")

    # -- 2. Drug Discovery --
    print("\n[2] Drug — drug-like basin + toxic outlier #15")
    print("-" * 50)
    mols = np.vstack([np.random.randn(30,5)*0.4+[300,2,2,60,3],
                      np.random.randn(30,5)*0.4+[600,6,0,120,8]])
    mols[15] = [900,10,-3,200,15]
    r = lens.scan_materials(mols, ["MW","LogP","HBD","TPSA","RotBonds"])
    print(f"  Attractors: {len(r.attractors)}")
    b15 = next((bid for bid, idx in r.basins.items() if 15 in idx), None)
    c2_basins = len(r.attractors) >= 2
    c2_anom15 = b15 is not None and len(r.basins[b15]) <= 3
    print(f"  CHECK: >=2 basins = {c2_basins}\n  CHECK: anomaly #15 isolated = {c2_anom15}")

    # -- 3. Physics --
    print("\n[3] Physics — particle family clusters")
    print("-" * 50)
    phys = np.vstack([np.random.randn(10,4)*0.3+[0.5,-1,0.5,1],
                      np.random.randn(10,4)*0.3+[3,1,0.5,3],
                      np.random.randn(10,4)*0.3+[6,0,1,6]])
    r = lens.scan_materials(phys, ["mass","charge","spin","coupling"])
    print(f"  Attractors: {len(r.attractors)}")
    c3_fam = len(r.attractors) >= 3
    pure = 0
    for idx in r.basins.values():
        fam = [0 if i<10 else (1 if i<20 else 2) for i in idx]
        if fam and Counter(fam).most_common(1)[0][1]/len(fam) > 0.7: pure += 1
    c3_pure = pure >= 3
    print(f"  CHECK: >=3 families = {c3_fam}\n  CHECK: >=3 pure basins = {c3_pure}")

    # -- 4. Astronomy --
    print("\n[4] Astronomy — signal attractor states (burst at 1500-1600)")
    print("-" * 50)
    t = np.linspace(0,10,4096)
    sig = np.sin(2*np.pi*5*t) + 0.3*np.sin(2*np.pi*11*t) + np.random.randn(4096)*0.2
    sig[1500:1600] += 5.0*np.sin(2*np.pi*47*t[1500:1600])
    r = lens.scan_signals(sig, window=256)
    print(f"  Attractors: {len(r.attractors)}")
    c4_states = len(r.attractors) >= 2
    nb = next((b for b,i in r.basins.items() if 0 in i), None)
    bb = next((b for b,i in r.basins.items() if 5 in i or 6 in i), None)
    c4_sep = nb is not None and bb is not None and nb != bb
    if not c4_sep and len(r.energy_landscape) > 6:
        en = np.mean([r.energy_landscape[i] for i in range(len(r.energy_landscape)) if i not in [5,6]])
        eb = np.mean([r.energy_landscape[min(i,len(r.energy_landscape)-1)] for i in [5,6]])
        c4_sep = abs(eb - en) > abs(en) * 0.05
    print(f"  CHECK: >=2 states = {c4_states}\n  CHECK: burst separated = {c4_sep}")

    # -- 5. Finance --
    print("\n[5] Finance — regime attractors + barriers")
    print("-" * 50)
    np.random.seed(42)
    bull = np.cumsum(np.random.randn(300)*0.3+0.2)
    crash = np.cumsum(np.random.randn(100)*3.0-2.0)
    rec = np.cumsum(np.random.randn(200)*0.5+0.1)
    price = np.concatenate([bull, crash+bull[-1], rec+bull[-1]+crash[-1]])
    r = lens.scan_timeseries(price, window=30)
    print(f"  Attractors: {len(r.attractors)} | Saddles: {len(r.saddle_points)}")
    c5_reg = len(r.attractors) >= 2; c5_bar = len(r.saddle_points) >= 1
    print(f"  CHECK: >=2 regimes = {c5_reg}\n  CHECK: >=1 barrier = {c5_bar}")

    # -- 6. Genomics --
    print("\n[6] Genomics — gene expression basins")
    print("-" * 50)
    np.random.seed(42)
    genes = np.vstack([np.random.randn(20,6)*0.3+[5,5,0,0,0,0],
                       np.random.randn(20,6)*0.3+[0,0,5,5,0,0],
                       np.random.randn(20,6)*0.3+[0,0,0,0,5,5]])
    r = lens.scan_materials(genes, [f"cond_{i}" for i in range(6)])
    print(f"  Attractors: {len(r.attractors)}")
    c6_bas = len(r.attractors) >= 3
    gp = 0
    for idx in r.basins.values():
        grp = [0 if i<20 else (1 if i<40 else 2) for i in idx]
        if grp and Counter(grp).most_common(1)[0][1]/len(grp) > 0.7: gp += 1
    c6_pure = gp >= 3
    print(f"  CHECK: >=3 basins = {c6_bas}\n  CHECK: >=3 pure groups = {c6_pure}")

    # -- Scorecard --
    print("\n" + "=" * 60)
    checks = [("Materials: >=3 basins", c1_3basins), ("Materials: anomaly #7", c1_anom7),
              ("Drug: >=2 basins", c2_basins), ("Drug: anomaly #15", c2_anom15),
              ("Physics: >=3 families", c3_fam), ("Physics: pure basins", c3_pure),
              ("Astronomy: >=2 states", c4_states), ("Astronomy: burst sep", c4_sep),
              ("Finance: >=2 regimes", c5_reg), ("Finance: barrier", c5_bar),
              ("Genomics: >=3 basins", c6_bas), ("Genomics: pure groups", c6_pure)]
    p = sum(v for _,v in checks)
    print(f"  SCORECARD: {p}/{len(checks)} ({100*p//len(checks)}%)")
    for nm, ok in checks: print(f"    {'PASS' if ok else 'FAIL'} {nm}")
    print("=" * 60)
