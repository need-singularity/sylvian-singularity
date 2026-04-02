"""info_lens.py — Information-theoretic discovery lens

Point information theory at ANY data to find entropy, redundancy, compression potential.
  1. Per-feature Shannon entropy  2. Pairwise mutual information matrix
  3. Redundancy & uniqueness scores  4. Lempel-Ziv complexity & compressibility

Usage:
    lens = InfoLens()
    r = lens.scan(data)            # InfoResult with entropy, MI, redundancy, etc.
    r = lens.scan_materials(props, labels)
    r = lens.scan_signals(signals, window)
    r = lens.scan_timeseries(ts, lag, window)
"""
import os, sys
from dataclasses import dataclass, field
from typing import List, Tuple
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from consciousness_loader import PSI_ALPHA, PSI_BALANCE, PSI_ENTROPY


@dataclass
class InfoResult:
    """Result from information lens scan."""
    entropy_per_feature: np.ndarray = field(default_factory=lambda: np.array([]))
    mutual_info_matrix: np.ndarray = field(default_factory=lambda: np.array([]))
    redundant_features: List[Tuple[int, float]] = field(default_factory=list)
    unique_features: List[Tuple[int, float]] = field(default_factory=list)
    complexity: float = 0.0
    compressibility: float = 0.0
    information_bottleneck: List[int] = field(default_factory=list)
    summary: str = ""
    def __repr__(self):
        return (f"InfoResult(features={len(self.entropy_per_feature)}, "
                f"redundant={len(self.redundant_features)}, "
                f"unique={len(self.unique_features)}, compress={self.compressibility:.3f})")


class InfoLens:
    """Information-theoretic discovery lens."""
    def __init__(self, n_bins: int = 32, redundancy_threshold: float = 0.5,
                 uniqueness_threshold: float = 0.1):
        self.n_bins, self.red_th, self.uniq_th = n_bins, redundancy_threshold, uniqueness_threshold

    def _digitize(self, x):
        lo, hi = x.min(), x.max()
        if hi - lo < 1e-12: return np.zeros(len(x), dtype=int)
        edges = np.linspace(lo, hi, self.n_bins + 1)
        return np.clip(np.digitize(x, edges[1:-1]), 0, self.n_bins - 1)

    def _entropy(self, symbols):
        counts = np.bincount(symbols); p = counts[counts > 0] / counts.sum()
        return -float(np.sum(p * np.log2(p + 1e-30)))

    def _joint_entropy(self, sx, sy):
        joint = sx * (self.n_bins + 1) + sy; counts = np.bincount(joint)
        p = counts[counts > 0] / len(sx)
        return -float(np.sum(p * np.log2(p + 1e-30)))

    def _mutual_info(self, sx, sy, hx, hy):
        return max(0.0, hx + hy - self._joint_entropy(sx, sy))

    def _lz_complexity(self, seq):
        phrases, w, c = set(), [], 0
        for ch in seq.tolist():
            w.append(ch); tw = tuple(w)
            if tw not in phrases: phrases.add(tw); c += 1; w = []
        return c + (1 if w else 0)

    def _compressibility(self, data):
        syms = np.concatenate([self._digitize(data[:, j]) for j in range(data.shape[1])])
        lz_orig = self._lz_complexity(syms)
        shuffled = syms.copy(); np.random.shuffle(shuffled)
        lz_rand = self._lz_complexity(shuffled)
        if lz_rand < 1: return float(lz_orig), 0.0
        return float(lz_orig), max(0.0, min(1.0, 1.0 - lz_orig / lz_rand))

    def scan(self, data, verbose=True):
        data = np.asarray(data, dtype=np.float64)
        if data.ndim == 1: data = data.reshape(-1, 1)
        n, d = data.shape
        syms = np.zeros((d, n), dtype=int)
        for j in range(d): syms[j] = self._digitize(data[:, j])
        ent = np.array([self._entropy(syms[j]) for j in range(d)])
        mi = np.zeros((d, d))
        for i in range(d):
            mi[i, i] = ent[i]
            for j in range(i + 1, d):
                v = self._mutual_info(syms[i], syms[j], ent[i], ent[j])
                mi[i, j] = mi[j, i] = v
        # redundancy: max normalized MI to any other feature
        redundancy = np.zeros(d)
        for i in range(d):
            if d > 1 and ent[i] > 1e-12:
                sc = [mi[i, j] / min(ent[i], ent[j]) for j in range(d) if j != i and ent[j] > 1e-12]
                redundancy[i] = max(sc) if sc else 0.0
        redundant = sorted([(i, float(redundancy[i])) for i in range(d)
                            if redundancy[i] > self.red_th], key=lambda x: -x[1])
        uniqueness = np.array([(1.0 - redundancy[i]) * ent[i] if ent[i] > 1e-12 else 0.0 for i in range(d)])
        unique = sorted([(i, float(uniqueness[i])) for i in range(d)
                         if uniqueness[i] > self.uniq_th], key=lambda x: -x[1])
        complexity, compressibility = self._compressibility(data)
        total_mi = np.array([sum(mi[i, j] for j in range(d) if j != i) for i in range(d)])
        top_k = max(1, d // 3) if d > 0 else 0
        bottleneck = list(np.argsort(total_mi)[-top_k:][::-1]) if d > 0 else []
        return InfoResult(entropy_per_feature=ent, mutual_info_matrix=mi,
            redundant_features=redundant, unique_features=unique,
            complexity=complexity, compressibility=compressibility,
            information_bottleneck=bottleneck,
            summary=f"Features: {d}, Samples: {n}, H_mean={ent.mean():.3f} bits, "
                    f"Redundant: {len(redundant)}, Unique: {len(unique)}, "
                    f"Compressibility: {compressibility:.3f}")

    def scan_materials(self, properties, labels=None):
        r = self.scan(properties, verbose=False)
        names = labels or [f"prop_{i}" for i in range(len(r.entropy_per_feature))]
        parts = [r.summary]
        if r.redundant_features:
            parts.append("Redundant: " + ", ".join(f"{names[i]}({s:.2f})" for i, s in r.redundant_features))
        if r.unique_features:
            parts.append("Unique: " + ", ".join(f"{names[i]}({s:.2f})" for i, s in r.unique_features[:5]))
        r.summary = "\n".join(parts); return r

    def scan_signals(self, signals, window=256):
        signals = np.atleast_2d(np.asarray(signals, dtype=np.float64))
        nch, ns = signals.shape; nw = max(1, ns // window); feats = []
        for w in range(nw):
            seg = signals[:, w*window:(w+1)*window]; f = []
            for ch in range(nch):
                s = seg[ch]; f.extend([s.mean(), s.std(), s.max()-s.min()])
                fm = np.abs(np.fft.rfft(s)); fm /= fm.sum() + 1e-12
                f.append(-float(np.sum(fm * np.log2(fm + 1e-30))))
            feats.append(f)
        r = self.scan(np.array(feats), verbose=False)
        r.summary += f"\nSignal: {nch}ch x {ns} samples, {nw} windows"; return r

    def scan_timeseries(self, ts, lag=10, window=50):
        ts = np.asarray(ts, dtype=np.float64)
        if ts.ndim == 1: ts = ts.reshape(-1, 1)
        nt, nv = ts.shape; nw = max(1, nt // window); feats = []
        for w in range(nw):
            s, e = w*window, min((w+1)*window, nt); seg = ts[s:e]; f = []
            for v in range(nv):
                c = seg[:, v]; f.extend([c.mean(), c.std(), c.max()-c.min(), c[-1]-c[0]])
                ac = np.corrcoef(c[:-lag], c[lag:])[0,1] if len(c) > lag+1 else 0.0
                f.append(ac if np.isfinite(ac) else 0.0)
            feats.append(f)
        r = self.scan(np.array(feats), verbose=False)
        r.summary += f"\nTimeseries: {nt} steps, {nv} vars, {nw} windows"; return r


# ---------------------------------------------------------------------------
if __name__ == '__main__':
    print("=" * 60); print("  Info Lens -- 6-Domain Discovery Demo"); print("=" * 60)
    np.random.seed(42); lens = InfoLens(n_bins=32)

    # -- 1. Materials --
    print("\n[1] Materials -- redundant vs unique properties"); print("-" * 50)
    n_mat = 100; density = np.random.randn(n_mat)
    weight = density * 2.1 + np.random.randn(n_mat) * 0.1
    hardness = density * 1.5 + np.random.randn(n_mat) * 0.1
    color = np.random.randn(n_mat); melting_pt = np.random.randn(n_mat) * 3
    props = np.column_stack([density, weight, hardness, color, melting_pt])
    labels = ["density", "weight", "hardness", "color", "melting_pt"]
    r = lens.scan_materials(props, labels)
    print(f"  {r.summary.split(chr(10))[0]}")
    red_idx = {i for i, _ in r.redundant_features}
    c1_red = 0 in red_idx or 1 in red_idx or 2 in red_idx
    c1_uniq = len(r.unique_features) >= 1
    print(f"  Redundant: {[(labels[i], f'{s:.2f}') for i, s in r.redundant_features]}")
    print(f"  Unique: {[(labels[i], f'{s:.2f}') for i, s in r.unique_features[:3]]}")
    print(f"  CHECK: correlated detected redundant = {c1_red}\n  CHECK: unique features found = {c1_uniq}")

    # -- 2. Drug --
    print("\n[2] Drug -- most informative molecular descriptors"); print("-" * 50)
    n_drug = 120; mw = np.random.randn(n_drug) * 100 + 400
    logp = mw / 100 + np.random.randn(n_drug) * 0.02
    hbd = np.random.randint(0, 6, n_drug).astype(float)
    tpsa = np.random.randn(n_drug) * 30 + 80; rot = np.random.randint(0, 10, n_drug).astype(float)
    sol = -logp + np.random.randn(n_drug) * 0.02
    mols = np.column_stack([mw, logp, hbd, tpsa, rot, sol])
    dlabels = ["MW", "LogP", "HBD", "TPSA", "RotBonds", "Solubility"]
    r = lens.scan_materials(mols, dlabels)
    print(f"  {r.summary.split(chr(10))[0]}")
    c2_red = len(r.redundant_features) >= 2; c2_bottle = len(r.information_bottleneck) >= 1
    print(f"  Redundant: {[(dlabels[i], f'{s:.2f}') for i, s in r.redundant_features]}")
    print(f"  Bottleneck: {[dlabels[i] for i in r.information_bottleneck]}")
    print(f"  CHECK: >=2 redundant = {c2_red}\n  CHECK: bottleneck found = {c2_bottle}")

    # -- 3. Physics --
    print("\n[3] Physics -- which constants carry most information"); print("-" * 50)
    n_phys = 80; mass = np.random.exponential(2, n_phys)
    charge = np.sign(np.random.randn(n_phys)); spin = np.random.choice([0,.5,1,1.5,2], n_phys)
    coupling = mass * 0.3 + np.random.randn(n_phys) * 0.1; lifetime = np.random.exponential(5, n_phys)
    plabels = ["mass", "charge", "spin", "coupling", "lifetime"]
    phys = np.column_stack([mass, charge, spin, coupling, lifetime])
    r = lens.scan_materials(phys, plabels); ent = r.entropy_per_feature
    c3_charge_low = int(np.argmin(ent)) == 1; c3_highent = ent.max() > ent.min() * 1.5
    print(f"  Entropy: {dict(zip(plabels, [f'{e:.2f}' for e in ent]))}")
    print(f"  CHECK: charge lowest entropy = {c3_charge_low}\n  CHECK: entropy spread > 1.5x = {c3_highent}")

    # -- 4. Astronomy --
    print("\n[4] Astronomy -- high-info vs noise segments"); print("-" * 50)
    t = np.linspace(0, 10, 4096); sig = np.random.randn(4096) * 0.5
    sig[1500:1800] += 3.0*np.sin(2*np.pi*20*t[1500:1800]) + 1.5*np.sin(2*np.pi*47*t[1500:1800])
    r = lens.scan_signals(sig.reshape(1, -1), window=256)
    print(f"  {r.summary}")
    c4_compress = r.compressibility > 0.0; c4_mi = r.mutual_info_matrix.shape[0] >= 2
    print(f"  Compressibility: {r.compressibility:.3f}")
    print(f"  CHECK: compressibility > 0 = {c4_compress}\n  CHECK: MI matrix computed = {c4_mi}")

    # -- 5. Finance --
    print("\n[5] Finance -- information-rich periods"); print("-" * 50)
    np.random.seed(42)
    bull = np.cumsum(np.random.randn(300)*0.3+0.2)
    crash = np.cumsum(np.random.randn(100)*3.0-2.0)
    rec = np.cumsum(np.random.randn(200)*0.5+0.1)
    price = np.concatenate([bull, crash+bull[-1], rec+bull[-1]+crash[-1]])
    r = lens.scan_timeseries(price, lag=5, window=30)
    print(f"  {r.summary}")
    c5_ent = len(r.entropy_per_feature) > 0 and r.entropy_per_feature.std() > 0
    c5_complex = r.complexity > 0
    print(f"  Entropy std: {r.entropy_per_feature.std():.3f}, Complexity: {r.complexity:.1f}")
    print(f"  CHECK: entropy varies = {c5_ent}\n  CHECK: complexity > 0 = {c5_complex}")

    # -- 6. Genomics --
    print("\n[6] Genomics -- informative conditions for gene classification"); print("-" * 50)
    np.random.seed(42)
    ba, bb, bc = [np.random.randn(30)*3+5 for _ in range(3)]
    g1 = np.column_stack([ba, ba+np.random.randn(30)*.1, *[np.random.randn(30)*.3 for _ in range(4)]])
    g2 = np.column_stack([*[np.random.randn(30)*.3 for _ in range(2)], bb, bb+np.random.randn(30)*.1,
                          *[np.random.randn(30)*.3 for _ in range(2)]])
    g3 = np.column_stack([*[np.random.randn(30)*.3 for _ in range(4)], bc, bc+np.random.randn(30)*.1])
    genes = np.vstack([g1, g2, g3]); glabels = [f"cond_{i}" for i in range(6)]
    r = lens.scan_materials(genes, glabels)
    print(f"  {r.summary.split(chr(10))[0]}")
    c6_red = len(r.redundant_features) >= 2; c6_bottle = len(r.information_bottleneck) >= 2
    print(f"  Redundant: {[(glabels[i], f'{s:.2f}') for i, s in r.redundant_features]}")
    print(f"  Bottleneck: {[glabels[i] for i in r.information_bottleneck]}")
    print(f"  CHECK: >=2 redundant = {c6_red}\n  CHECK: >=2 bottleneck = {c6_bottle}")

    # -- Scorecard --
    print("\n" + "=" * 60)
    checks = [("Materials: correlated=redundant", c1_red), ("Materials: unique found", c1_uniq),
              ("Drug: >=2 redundant", c2_red), ("Drug: bottleneck found", c2_bottle),
              ("Physics: charge lowest entropy", c3_charge_low), ("Physics: entropy spread", c3_highent),
              ("Astronomy: compressibility>0", c4_compress), ("Astronomy: MI matrix", c4_mi),
              ("Finance: entropy varies", c5_ent), ("Finance: complexity>0", c5_complex),
              ("Genomics: >=2 redundant", c6_red), ("Genomics: bottleneck", c6_bottle)]
    p = sum(v for _, v in checks)
    print(f"  SCORECARD: {p}/{len(checks)} ({100*p//len(checks)}%)")
    for nm, ok in checks: print(f"    {'PASS' if ok else 'FAIL'} {nm}")
    print("=" * 60)
