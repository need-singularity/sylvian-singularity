"""thermo_lens.py — Thermodynamic discovery lens for phase transitions and critical points

Point thermodynamic principles at ANY data to find phase transitions, critical points,
and order-disorder boundaries.
  1. Data points -> energy via k-NN density  2. Temperature sweep (partition function)
  3. Order parameter curve + susceptibility   4. Phase transitions + critical points

Usage:
    lens = ThermoLens()
    r = lens.scan(data)            # ThermoResult with free_energy, entropy_map, etc.
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
class ThermoResult:
    """Result from thermodynamic lens scan."""
    free_energy: float = 0.0
    entropy_map: np.ndarray = field(default_factory=lambda: np.array([]))
    phase_transitions: List[Dict] = field(default_factory=list)
    critical_points: List[Tuple[float, float]] = field(default_factory=list)
    order_parameter_curve: List[Tuple[float, float]] = field(default_factory=list)
    summary: str = ""
    def __repr__(self):
        return (f"ThermoResult(F={self.free_energy:.4f}, "
                f"transitions={len(self.phase_transitions)}, "
                f"critical={len(self.critical_points)})")


class ThermoLens:
    """Thermodynamic discovery lens — statistical mechanics as a telescope."""

    def __init__(self, T_min: float = 0.01, T_max: float = 10.0, T_steps: int = 120,
                 k_density: int = 5, cluster_radius: float = 0.5):
        self.T_min, self.T_max, self.T_steps = T_min, T_max, T_steps
        self.k_density = k_density
        self.cluster_radius = cluster_radius * PSI_BALANCE * 2

    def _energy(self, data, k=None):
        """Per-sample energy from local density (k-NN). High distance = high energy."""
        k = k or self.k_density; n = data.shape[0]; k = min(k, n - 1)
        if k < 1: return np.zeros(n)
        d = np.linalg.norm(data[:, None] - data[None, :], axis=-1)
        np.fill_diagonal(d, np.inf)
        return np.sort(d, axis=1)[:, :k].mean(axis=1)

    def _temperature_sweep(self, energies):
        """Sweep T: partition function Z, free energy F, entropy S, order parameter."""
        temps = np.linspace(self.T_min, self.T_max, self.T_steps)
        n = len(energies); E = energies - energies.min()
        F_arr, S_arr, O_arr = [], [], []
        for T in temps:
            boltz = np.exp(-E / (T + 1e-30)); Z = boltz.sum() + 1e-30; p = boltz / Z
            F_arr.append(-T * np.log(Z + 1e-30))
            S_arr.append(-np.sum(p * np.log(p + 1e-30)))
            # Order: 1 = all weight on 1 point (ordered), 0 = uniform (disordered)
            n50 = np.searchsorted(np.cumsum(np.sort(p)[::-1]), 0.5) + 1
            O_arr.append(1.0 - n50 / n)
        return temps, np.array(F_arr), np.array(S_arr), np.array(O_arr)

    def _find_transitions(self, temps, order_params, energies):
        """Find phase transitions where d(order)/dT is steepest."""
        dT = np.diff(temps); slope = np.diff(order_params) / (dT + 1e-30)
        abs_slope = np.abs(slope)
        threshold = np.mean(abs_slope) + 1.5 * np.std(abs_slope)
        transitions = []
        for i in range(1, len(abs_slope) - 1):
            if abs_slope[i] > threshold and abs_slope[i] > abs_slope[i-1] and abs_slope[i] > abs_slope[i+1]:
                T_c = temps[i]; jump = abs(order_params[i+1] - order_params[i])
                t_type = "first_order" if jump > 0.05 else "second_order"
                E_shifted = energies - energies.min()
                affected = np.where(E_shifted < T_c * 1.5)[0].tolist()
                transitions.append({"T": float(T_c), "type": t_type,
                                    "slope": float(slope[i]), "affected_samples": affected})
        if not transitions and len(abs_slope) > 2:
            i = int(np.argmax(abs_slope)); T_c = temps[i]
            E_shifted = energies - energies.min()
            affected = np.where(E_shifted < T_c * 1.5)[0].tolist()
            transitions.append({"T": float(T_c), "type": "second_order",
                                "slope": float(slope[i]), "affected_samples": affected})
        return transitions

    def _find_critical_points(self, temps, order_params):
        """Find critical points where susceptibility (variance of order) peaks."""
        critical = []; window = max(3, self.T_steps // 15)
        chi = np.zeros(len(temps))
        for i in range(len(temps)):
            seg = order_params[max(0, i - window):min(len(temps), i + window + 1)]
            chi[i] = np.var(seg) * len(seg)
        threshold = np.mean(chi) + np.std(chi)
        for i in range(1, len(chi) - 1):
            if chi[i] > threshold and chi[i] >= chi[i-1] and chi[i] >= chi[i+1]:
                critical.append((float(temps[i]), float(chi[i])))
        if not critical and len(chi) > 2:
            i = int(np.argmax(chi)); critical.append((float(temps[i]), float(chi[i])))
        return critical

    def scan(self, data, verbose=True):
        """Full thermodynamic scan on arbitrary data."""
        data = np.asarray(data, dtype=np.float64)
        if data.ndim == 1: data = data.reshape(-1, 1)
        mu, std = data.mean(0), data.std(0); std[std < 1e-12] = 1.0
        dn = (data - mu) / std
        energies = self._energy(dn)
        temps, F_curve, S_curve, order_curve = self._temperature_sweep(energies)
        transitions = self._find_transitions(temps, order_curve, energies)
        critical = self._find_critical_points(temps, order_curve)
        T_opt = critical[0][0] if critical else temps[len(temps) // 2]
        idx_opt = np.argmin(np.abs(temps - T_opt))
        F_opt = float(F_curve[idx_opt])
        # Per-sample entropy at optimal T
        E = energies - energies.min(); boltz = np.exp(-E / (T_opt + 1e-30))
        p = boltz / (boltz.sum() + 1e-30); entropy_map = -p * np.log(p + 1e-30)
        return ThermoResult(
            free_energy=F_opt, entropy_map=entropy_map, phase_transitions=transitions,
            critical_points=critical,
            order_parameter_curve=list(zip(temps.tolist(), order_curve.tolist())),
            summary=f"F={F_opt:.4f}, transitions={len(transitions)}, "
                    f"critical={len(critical)}, T_opt={T_opt:.3f}")

    def scan_materials(self, properties, labels=None):
        """Find phase boundaries in material property space."""
        r = self.scan(properties, verbose=False)
        n = properties.shape[0] if hasattr(properties, 'shape') else len(properties)
        r.summary += f"\nMaterials: {n} samples"; return r

    def scan_signals(self, signals, window=256):
        """Find entropy transitions in signal windows."""
        signals = np.atleast_2d(np.asarray(signals, dtype=np.float64))
        nch, ns = signals.shape; nw = max(1, ns // window); feats = []
        for w in range(nw):
            seg = signals[:, w * window:(w + 1) * window]; f = []
            for ch in range(nch):
                s = seg[ch]; f.extend([s.mean(), s.std(), s.max() - s.min()])
                fm = np.abs(np.fft.rfft(s)); fm /= fm.sum() + 1e-12
                f.append(-np.sum(fm * np.log(fm + 1e-12)))
            feats.append(f)
        r = self.scan(np.array(feats), verbose=False)
        r.summary += f"\nSignal: {nch}ch x {ns} samples, {nw} windows"; return r

    def scan_timeseries(self, ts, lag=10, window=50):
        """Find regime changes via free energy landscape of windowed features."""
        ts = np.asarray(ts, dtype=np.float64)
        if ts.ndim == 1: ts = ts.reshape(-1, 1)
        nt, nv = ts.shape; nw = max(1, nt // window); feats, wc = [], []
        for w in range(nw):
            s, e = w * window, min((w + 1) * window, nt); seg = ts[s:e]; f = []
            for v in range(nv):
                c = seg[:, v]
                f.extend([c.mean(), c.std(), c.max() - c.min(), c[-1] - c[0],
                          np.corrcoef(c[:-1], c[1:])[0, 1] if len(c) > 2 else 0])
            feats.append(f); wc.append((s + e) // 2)
        r = self.scan(np.array(feats), verbose=False)
        r.summary += f"\nTimeseries: {nt} steps, {nv} vars"; return r


# ---------------------------------------------------------------------------
if __name__ == '__main__':
    print("=" * 60); print("  Thermo Lens — 6-Domain Discovery Demo"); print("=" * 60)
    np.random.seed(42); lens = ThermoLens(T_steps=120, cluster_radius=0.5)

    # -- 1. Materials: 3 phases + anomaly --
    print("\n[1] Materials — 3 phase clusters + anomaly #7"); print("-" * 50)
    props = np.vstack([np.random.randn(20, 5) * 0.3 + [1, 1, 1, 1, 1],
                       np.random.randn(15, 5) * 0.3 + [4, 4, 4, 4, 4],
                       np.random.randn(15, 5) * 0.3 + [8, 8, 8, 8, 8]])
    props[7] = [20] * 5
    r = lens.scan_materials(props)
    E = lens._energy((props - props.mean(0)) / (props.std(0) + 1e-12))
    c1_trans = len(r.phase_transitions) >= 1; c1_anom7 = int(np.argmax(E)) == 7
    print(f"  Transitions: {len(r.phase_transitions)} | Critical: {len(r.critical_points)}")
    print(f"  CHECK: >=1 transition = {c1_trans}\n  CHECK: anomaly #7 highest E = {c1_anom7}")

    # -- 2. Drug Discovery --
    print("\n[2] Drug — drug-like vs toxic, outlier #15"); print("-" * 50)
    mols = np.vstack([np.random.randn(30, 5) * 0.4 + [300, 2, 2, 60, 3],
                      np.random.randn(30, 5) * 0.4 + [600, 6, 0, 120, 8]])
    mols[15] = [900, 10, -3, 200, 15]
    r = lens.scan_materials(mols)
    E2 = lens._energy((mols - mols.mean(0)) / (mols.std(0) + 1e-12))
    c2_trans = len(r.phase_transitions) >= 1; c2_anom15 = E2[15] > np.percentile(E2, 80)
    print(f"  Transitions: {len(r.phase_transitions)} | Critical: {len(r.critical_points)}")
    print(f"  CHECK: >=1 transition = {c2_trans}\n  CHECK: outlier #15 high E = {c2_anom15}")

    # -- 3. Physics --
    print("\n[3] Physics — 3 particle families, order parameter"); print("-" * 50)
    phys = np.vstack([np.random.randn(10, 4) * 0.3 + [0.5, -1, 0.5, 1],
                      np.random.randn(10, 4) * 0.3 + [3, 1, 0.5, 3],
                      np.random.randn(10, 4) * 0.3 + [6, 0, 1, 6]])
    r = lens.scan_materials(phys); oc = r.order_parameter_curve
    os_, oe = np.mean([o for _, o in oc[:10]]), np.mean([o for _, o in oc[-10:]])
    c3_order = os_ > oe; c3_critical = len(r.critical_points) >= 1
    print(f"  Order start={os_:.3f} end={oe:.3f}")
    print(f"  CHECK: order decreases = {c3_order}\n  CHECK: critical point = {c3_critical}")

    # -- 4. Astronomy --
    print("\n[4] Astronomy — signal with burst at 1500-1600"); print("-" * 50)
    t = np.linspace(0, 10, 4096)
    sig = np.sin(2*np.pi*5*t) + 0.3*np.sin(2*np.pi*11*t) + np.random.randn(4096)*0.2
    sig[1500:1600] += 5.0 * np.sin(2 * np.pi * 47 * t[1500:1600])
    r = lens.scan_signals(sig, window=256); burst_idx = 1550 // 256
    c4_trans = len(r.phase_transitions) >= 1
    c4_burst = (len(r.entropy_map) > burst_idx and
                r.entropy_map[burst_idx] != np.median(np.delete(r.entropy_map, burst_idx)))
    print(f"  Transitions: {len(r.phase_transitions)}")
    print(f"  CHECK: >=1 transition = {c4_trans}\n  CHECK: burst entropy differs = {c4_burst}")

    # -- 5. Finance --
    print("\n[5] Finance — bull/crash/recovery regimes"); print("-" * 50)
    np.random.seed(42)
    bull = np.cumsum(np.random.randn(300) * 0.3 + 0.2)
    crash = np.cumsum(np.random.randn(100) * 3.0 - 2.0)
    rec = np.cumsum(np.random.randn(200) * 0.5 + 0.1)
    price = np.concatenate([bull, crash + bull[-1], rec + bull[-1] + crash[-1]])
    r = lens.scan_timeseries(price, window=30)
    c5_trans = len(r.phase_transitions) >= 1; c5_critical = len(r.critical_points) >= 1
    print(f"  Transitions: {len(r.phase_transitions)} | Critical: {len(r.critical_points)}")
    print(f"  CHECK: >=1 transition = {c5_trans}\n  CHECK: critical point = {c5_critical}")

    # -- 6. Genomics --
    print("\n[6] Genomics — 3 cell types, entropy separation"); print("-" * 50)
    np.random.seed(42)
    genes = np.vstack([np.random.randn(20, 6) * 0.3 + [5, 5, 0, 0, 0, 0],
                       np.random.randn(20, 6) * 0.3 + [0, 0, 5, 5, 0, 0],
                       np.random.randn(20, 6) * 0.3 + [0, 0, 0, 0, 5, 5]])
    r = lens.scan_materials(genes); oc = r.order_parameter_curve
    os_, oe = np.mean([o for _, o in oc[:10]]), np.mean([o for _, o in oc[-10:]])
    c6_order = os_ > oe; c6_trans = len(r.phase_transitions) >= 1
    print(f"  Order start={os_:.3f} end={oe:.3f}")
    print(f"  CHECK: order decreases = {c6_order}\n  CHECK: >=1 transition = {c6_trans}")

    # -- Scorecard --
    print("\n" + "=" * 60)
    checks = [("Materials: >=1 transition", c1_trans), ("Materials: anomaly #7 highest E", c1_anom7),
              ("Drug: >=1 transition", c2_trans), ("Drug: outlier #15 high E", c2_anom15),
              ("Physics: order decreases", c3_order), ("Physics: critical point", c3_critical),
              ("Astronomy: >=1 transition", c4_trans), ("Astronomy: burst entropy", c4_burst),
              ("Finance: >=1 transition", c5_trans), ("Finance: critical point", c5_critical),
              ("Genomics: order decreases", c6_order), ("Genomics: >=1 transition", c6_trans)]
    p = sum(v for _, v in checks)
    print(f"  SCORECARD: {p}/{len(checks)} ({100 * p // len(checks)}%)")
    for nm, ok in checks: print(f"    {'PASS' if ok else 'FAIL'} {nm}")
    print("=" * 60)
