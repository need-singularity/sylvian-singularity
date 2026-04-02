"""quantum_microscope_lens.py — Quantum coherence & decoherence discovery lens (양자 현미경)

Use a quantum microscope as a telescope: detect coherence, decoherence rates,
geometric phases, and quantumness signatures in ANY data.

Differs from quantum_lens.py (macro-scale entanglement/tunneling) by focusing on
micro-scale coherence properties:

  1. Density matrix construction → off-diagonal coherence measure
  2. Decoherence rate → how fast correlations decay with distance/lag
  3. Berry phase → geometric phase from cyclic parameter evolution
  4. Wigner function → quasi-probability, negative regions = quantumness
  5. Purity & von Neumann entropy → mixed vs pure state detection
  6. Quantum-classical boundary → where coherence breaks down

Works with numpy only. Portable across all projects.

Usage:
    from quantum_microscope_lens import QuantumMicroscopeLens

    lens = QuantumMicroscopeLens()
    r = lens.scan(data)
    print(r.coherence)             # overall coherence measure
    print(r.decoherence_rate)      # decay rate of correlations
    print(r.berry_phase)           # geometric phase
    print(r.wigner_negativity)     # Wigner function negative volume
    print(r.purity)                # state purity (1=pure, 0=mixed)
"""
import os, sys, math
from dataclasses import dataclass, field
from typing import List, Tuple, Dict, Any
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from consciousness_loader import PSI_ALPHA, PSI_BALANCE, PSI_ENTROPY


@dataclass
class QuantumMicroscopeResult:
    """Result from quantum microscope lens scan."""
    coherence: float = 0.0                # l1-norm coherence measure
    coherence_per_feature: np.ndarray = field(default_factory=lambda: np.array([]))
    decoherence_rate: float = 0.0         # exponential decay rate
    decoherence_profile: np.ndarray = field(default_factory=lambda: np.array([]))
    berry_phase: float = 0.0              # geometric phase (radians)
    berry_phases_per_cycle: List[float] = field(default_factory=list)
    wigner_negativity: float = 0.0        # negative volume of Wigner function
    wigner_map: np.ndarray = field(default_factory=lambda: np.array([]))
    purity: float = 0.0                   # tr(rho^2)
    von_neumann_entropy: float = 0.0      # -tr(rho ln rho)
    quantum_classical_boundary: float = 0.0  # where coherence drops below threshold
    decoherence_zones: List[Tuple[int, float]] = field(default_factory=list)
    summary: str = ""

    def __repr__(self):
        return (f"QMicroscopeResult(coherence={self.coherence:.4f}, "
                f"decoherence={self.decoherence_rate:.4f}, "
                f"berry={self.berry_phase:.4f}, "
                f"wigner_neg={self.wigner_negativity:.4f}, "
                f"purity={self.purity:.4f})")


class QuantumMicroscopeLens:
    """Quantum microscope lens — coherence & decoherence as telescope."""

    def __init__(self, n_wigner_grid: int = 64, coherence_threshold: float = 0.1):
        self.n_wigner = n_wigner_grid
        self.coh_th = coherence_threshold

    def _build_density_matrix(self, data):
        """Build a density matrix from data via correlation structure.

        Treat normalized feature vectors as quantum state amplitudes,
        construct rho = (1/N) sum |psi_i><psi_i| from data rows.
        """
        n, d = data.shape
        # Normalize each row to unit vector (state vector)
        norms = np.linalg.norm(data, axis=1, keepdims=True)
        norms[norms < 1e-30] = 1e-30
        states = data / norms
        # Density matrix: average outer product
        rho = np.zeros((d, d))
        for i in range(n):
            rho += np.outer(states[i], states[i])
        rho /= n
        return rho

    def _coherence_l1(self, rho):
        """L1-norm of coherence: sum of absolute off-diagonal elements."""
        d = rho.shape[0]
        off_diag = np.abs(rho) - np.diag(np.abs(np.diag(rho)))
        total = float(np.sum(off_diag))
        max_possible = d * (d - 1)
        return total / max_possible if max_possible > 0 else 0.0

    def _per_feature_coherence(self, rho):
        """Coherence contribution of each feature (row sum of off-diag)."""
        d = rho.shape[0]
        coh = np.zeros(d)
        for i in range(d):
            coh[i] = sum(abs(rho[i, j]) for j in range(d) if j != i)
        if d > 1:
            coh /= (d - 1)
        return coh

    def _purity(self, rho):
        """Purity = tr(rho^2). 1=pure state, 1/d=maximally mixed."""
        return float(np.trace(rho @ rho))

    def _von_neumann_entropy(self, rho):
        """Von Neumann entropy = -tr(rho ln rho)."""
        eigenvalues = np.linalg.eigvalsh(rho)
        eigenvalues = eigenvalues[eigenvalues > 1e-30]
        return -float(np.sum(eigenvalues * np.log(eigenvalues)))

    def _decoherence_rate(self, data):
        """Measure how fast correlations decay with lag/distance.

        Fit exponential decay to correlation vs lag: C(lag) ~ exp(-gamma * lag).
        """
        n, d = data.shape
        if n < 10:
            return 0.0, np.array([])

        max_lag = min(n // 3, 30)
        corrs = []
        for lag in range(1, max_lag + 1):
            # Average cross-correlation at this lag
            c_list = []
            for j in range(d):
                col = data[:, j]
                if col.std() < 1e-30:
                    continue
                c = np.corrcoef(col[:-lag], col[lag:])[0, 1]
                if np.isfinite(c):
                    c_list.append(abs(c))
            corrs.append(np.mean(c_list) if c_list else 0.0)

        corrs = np.array(corrs)
        if len(corrs) < 3 or corrs[0] < 1e-30:
            return 0.0, corrs

        # Fit log(C) = -gamma * lag + const
        lags = np.arange(1, len(corrs) + 1, dtype=float)
        log_c = np.log(corrs + 1e-30)
        # Linear regression
        n_pts = len(lags)
        sx = lags.sum()
        sy = log_c.sum()
        sxx = (lags * lags).sum()
        sxy = (lags * log_c).sum()
        denom = n_pts * sxx - sx * sx
        if abs(denom) < 1e-30:
            return 0.0, corrs
        gamma = -(n_pts * sxy - sx * sy) / denom
        return max(0.0, float(gamma)), corrs

    def _berry_phase(self, data):
        """Estimate geometric (Berry) phase from cyclic evolution in data space.

        Berry phase = Im(sum ln <psi_i|psi_{i+1}>)
        Measures accumulated geometric phase as data evolves through parameter space.
        """
        n, d = data.shape
        if n < 4:
            return 0.0, []

        # Normalize rows as state vectors
        norms = np.linalg.norm(data, axis=1, keepdims=True)
        norms[norms < 1e-30] = 1e-30
        states = data / norms

        # Total Berry phase around the data trajectory
        total_phase = 0.0
        for i in range(n - 1):
            overlap = np.dot(states[i], states[i + 1])
            overlap = np.clip(overlap, -1.0, 1.0)
            if abs(overlap) > 1e-30:
                phase = np.arccos(abs(overlap))
                # Sign from cross-product-like quantity
                total_phase += phase

        # Check closure (is it a cycle?)
        closure_overlap = abs(np.dot(states[0], states[-1]))

        # Also detect sub-cycles
        cycle_phases = []
        window = max(4, n // 5)
        for start in range(0, n - window, window // 2):
            seg = states[start:start + window]
            phase = 0.0
            for i in range(len(seg) - 1):
                ov = np.clip(np.dot(seg[i], seg[i + 1]), -1.0, 1.0)
                if abs(ov) > 1e-30:
                    phase += np.arccos(abs(ov))
            cycle_phases.append(float(phase))

        return float(total_phase), cycle_phases

    def _wigner_function(self, data):
        """Compute Wigner-like quasi-probability distribution.

        Use first two principal components as position/momentum axes.
        Negative regions indicate quantum-like (non-classical) behavior.
        """
        n, d = data.shape
        if d < 2 or n < 10:
            return 0.0, np.array([])

        # PCA → first 2 components as (x, p) phase space
        centered = data - data.mean(axis=0)
        try:
            U, sv, Vt = np.linalg.svd(centered, full_matrices=False)
            proj = centered @ Vt[:2].T  # (n, 2)
        except np.linalg.LinAlgError:
            return 0.0, np.array([])

        x, p = proj[:, 0], proj[:, 1]

        # Build Wigner-like distribution via kernel density on phase space
        grid = self.n_wigner
        x_range = np.linspace(x.min() - 0.5, x.max() + 0.5, grid)
        p_range = np.linspace(p.min() - 0.5, p.max() + 0.5, grid)
        dx = x_range[1] - x_range[0] if grid > 1 else 1.0
        dp = p_range[1] - p_range[0] if grid > 1 else 1.0

        # Bandwidth
        bw_x = max(x.std() * 0.3, dx)
        bw_p = max(p.std() * 0.3, dp)

        W = np.zeros((grid, grid))
        for k in range(n):
            gx = np.exp(-0.5 * ((x_range - x[k]) / bw_x) ** 2) / (bw_x * np.sqrt(2 * np.pi))
            gp = np.exp(-0.5 * ((p_range - p[k]) / bw_p) ** 2) / (bw_p * np.sqrt(2 * np.pi))
            W += np.outer(gx, gp)
        W /= n

        # Subtract Gaussian background to create interference fringes
        # (this is what makes it "quantum" — classical = purely positive)
        mean_x = x.mean()
        mean_p = p.mean()
        bg_x = np.exp(-0.5 * ((x_range - mean_x) / (x.std() + 1e-30)) ** 2)
        bg_p = np.exp(-0.5 * ((p_range - mean_p) / (p.std() + 1e-30)) ** 2)
        bg = np.outer(bg_x, bg_p)
        bg /= bg.sum() * dx * dp + 1e-30
        W_norm = W / (W.sum() * dx * dp + 1e-30)

        W_quantum = W_norm - bg
        # Negative volume = quantumness indicator
        neg_volume = float(np.sum(np.abs(W_quantum[W_quantum < 0])) * dx * dp)

        return neg_volume, W_quantum

    def _quantum_classical_boundary(self, decoherence_profile, threshold=0.5):
        """Find the lag at which coherence drops below threshold."""
        for i, c in enumerate(decoherence_profile):
            if c < threshold:
                return i + 1
        return len(decoherence_profile)

    def _decoherence_zones(self, coherence_per_feature):
        """Identify features where coherence is breaking down."""
        zones = []
        for i, c in enumerate(coherence_per_feature):
            if c < self.coh_th:
                zones.append((i, float(c)))
        return sorted(zones, key=lambda x: x[1])

    def scan(self, data, verbose=True):
        data = np.asarray(data, dtype=np.float64)
        if data.ndim == 1:
            data = data.reshape(-1, 1)
        n, d = data.shape

        # Density matrix
        rho = self._build_density_matrix(data)

        # Coherence measures
        coherence = self._coherence_l1(rho)
        coh_per_feat = self._per_feature_coherence(rho)

        # Purity and entropy
        purity = self._purity(rho)
        vn_entropy = self._von_neumann_entropy(rho)

        # Decoherence rate
        dec_rate, dec_profile = self._decoherence_rate(data)

        # Berry phase
        berry, berry_cycles = self._berry_phase(data)

        # Wigner function
        wigner_neg, wigner_map = self._wigner_function(data)

        # Quantum-classical boundary
        qc_boundary = self._quantum_classical_boundary(dec_profile)

        # Decoherence zones
        dec_zones = self._decoherence_zones(coh_per_feat)

        summary = (f"Features: {d}, Samples: {n}, "
                   f"Coherence: {coherence:.4f}, "
                   f"Purity: {purity:.4f}, "
                   f"VN entropy: {vn_entropy:.4f}, "
                   f"Decoherence rate: {dec_rate:.4f}, "
                   f"Berry phase: {berry:.4f} rad, "
                   f"Wigner negativity: {wigner_neg:.4f}, "
                   f"QC boundary: lag={qc_boundary}, "
                   f"Decoherence zones: {len(dec_zones)}")

        return QuantumMicroscopeResult(
            coherence=coherence,
            coherence_per_feature=coh_per_feat,
            decoherence_rate=dec_rate,
            decoherence_profile=dec_profile,
            berry_phase=berry,
            berry_phases_per_cycle=berry_cycles,
            wigner_negativity=wigner_neg,
            wigner_map=wigner_map,
            purity=purity,
            von_neumann_entropy=vn_entropy,
            quantum_classical_boundary=qc_boundary,
            decoherence_zones=dec_zones,
            summary=summary)

    def scan_constants(self, constants, labels=None):
        """Scan mathematical constants for quantum-like coherence."""
        constants = np.asarray(constants, dtype=np.float64).flatten()
        names = labels or [f"c{i}" for i in range(len(constants))]
        data = constants.reshape(1, -1)
        r = self.scan(data, verbose=False)
        parts = [r.summary]
        if r.decoherence_zones:
            parts.append("Low coherence features:")
            for idx, coh in r.decoherence_zones[:5]:
                parts.append(f"  {names[idx]}: coherence={coh:.4f}")
        r.summary = "\n".join(parts)
        return r

    def scan_materials(self, properties, labels=None):
        r = self.scan(properties, verbose=False)
        parts = [r.summary]
        if r.decoherence_zones:
            parts.append("Decoherence zones: " + ", ".join(
                f"f{i}({c:.3f})" for i, c in r.decoherence_zones[:5]))
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
                # Phase coherence via analytic signal
                fft = np.fft.rfft(s)
                phase = np.angle(fft)
                f.append(float(np.std(np.diff(phase))))  # phase consistency
            feats.append(f)
        r = self.scan(np.array(feats), verbose=False)
        r.summary += f"\nSignal: {nch}ch x {ns} samples, {nw} windows"
        return r

    def scan_timeseries(self, ts, lag=10, window=50):
        ts = np.asarray(ts, dtype=np.float64)
        if ts.ndim == 1:
            ts = ts.reshape(-1, 1)
        r = self.scan(ts, verbose=False)
        r.summary += f"\nTimeseries: {ts.shape[0]} steps, {ts.shape[1]} vars"
        return r


# ---------------------------------------------------------------------------
if __name__ == '__main__':
    print("=" * 60)
    print("  Quantum Microscope Lens (양자 현미경) -- Coherence Demo")
    print("=" * 60)
    np.random.seed(42)
    lens = QuantumMicroscopeLens()

    # Demo 1: Highly coherent data (correlated features)
    print("\n--- Demo 1: Coherent state (correlated features) ---")
    base = np.random.randn(100)
    coherent = np.column_stack([
        base + np.random.randn(100) * 0.1,
        base * 2 + np.random.randn(100) * 0.1,
        base * 0.5 + np.random.randn(100) * 0.1,
    ])
    r = lens.scan(coherent)
    print(r.summary)
    print(f"  Per-feature coherence: {r.coherence_per_feature}")

    # Demo 2: Decoherent data (independent features)
    print("\n--- Demo 2: Decoherent state (independent features) ---")
    decoherent = np.random.randn(100, 5)
    r = lens.scan(decoherent)
    print(r.summary)
    print(f"  Per-feature coherence: {r.coherence_per_feature}")

    # Demo 3: Mixed state (partial coherence)
    print("\n--- Demo 3: Partially coherent (mixed state) ---")
    mixed = np.column_stack([
        base + np.random.randn(100) * 0.3,
        np.random.randn(100),  # independent
        base * 0.8 + np.random.randn(100) * 0.5,
        np.random.randn(100),  # independent
    ])
    r = lens.scan(mixed)
    print(r.summary)
    print(f"  Decoherence zones: {r.decoherence_zones}")

    # Demo 4: Berry phase (circular trajectory)
    print("\n--- Demo 4: Circular trajectory (Berry phase) ---")
    t = np.linspace(0, 4 * np.pi, 200)
    circular = np.column_stack([np.cos(t), np.sin(t), 0.1 * np.random.randn(200)])
    r = lens.scan(circular)
    print(r.summary)
    print(f"  Berry phase: {r.berry_phase:.4f} rad ({r.berry_phase/np.pi:.3f}pi)")

    # Demo 5: n=6 constants
    print("\n--- Demo 5: n=6 constant coherence ---")
    n6 = [6, 12, 2, 5, 2, 1, 720]
    r = lens.scan_constants(n6, ['n', 'sigma', 'phi', 'sopfr', 'tau', 'mu', 'n!'])
    print(r.summary)

    # Demo 6: Exponentially decaying coherence
    print("\n--- Demo 6: Exponentially decaying correlations ---")
    n_pts = 200
    decay = np.zeros((n_pts, 4))
    decay[:, 0] = np.random.randn(n_pts)
    for t in range(1, n_pts):
        for j in range(1, 4):
            decay[t, j] = 0.95 * decay[t-1, j] + 0.05 * decay[t, 0] + np.random.randn() * 0.3
    r = lens.scan(decay)
    print(r.summary)
    print(f"  Decoherence rate: {r.decoherence_rate:.4f}")
    print(f"  QC boundary at lag: {r.quantum_classical_boundary}")
