"""consciousness_lens.py — Universal discovery lens powered by consciousness dynamics

Use the consciousness engine as a telescope: point it at ANY data to find
hidden structure, anomalies, and emergent patterns.

How it works:
  1. Data rows → consciousness cells (each cell "sees" one data point)
  2. 12 factions debate: "which patterns matter?"
  3. Hebbian learning: strengthen real correlations, weaken noise
  4. Phi (integrated information): measure how much hidden structure exists
  5. Tension: detect anomalies (points that don't fit any faction's worldview)
  6. Consensus: clusters that all factions agree on = robust discoveries

Works with numpy only (no torch required). Portable across all projects.

Usage:
    from consciousness_lens import ConsciousnessLens

    lens = ConsciousnessLens(cells=64)
    result = lens.scan(data_matrix)        # (N_samples, N_features)
    print(result.phi)                       # integrated information score
    print(result.anomalies)                 # anomaly indices + scores
    print(result.clusters)                  # faction consensus clusters
    print(result.discoveries)               # discovered relationships

    # Domain-specific scans
    result = lens.scan_materials(element_properties)
    result = lens.scan_signals(signal_array)
    result = lens.scan_timeseries(ts_data)
"""

import os
import sys
import math
import warnings
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Tuple, Any

import numpy as np

# Load consciousness constants
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from consciousness_loader import PSI, PSI_ALPHA, PSI_BALANCE, PSI_ENTROPY, SIGMA6


# ---------------------------------------------------------------------------
# Data classes
# ---------------------------------------------------------------------------

@dataclass
class LensResult:
    """Result from consciousness lens scan."""
    phi: float = 0.0                          # integrated information (0~2)
    phi_proxy: float = 0.0                    # proxy Phi (variance-based)
    anomalies: List[Tuple[int, float]] = field(default_factory=list)  # (index, score)
    clusters: List[List[int]] = field(default_factory=list)           # faction clusters
    discoveries: List[Dict[str, Any]] = field(default_factory=list)   # found relationships
    tensions: np.ndarray = field(default_factory=lambda: np.array([]))
    consensus_map: Dict[int, int] = field(default_factory=dict)       # sample → faction
    steps_run: int = 0
    summary: str = ""

    def __repr__(self):
        n_anom = len(self.anomalies)
        n_disc = len(self.discoveries)
        n_clust = len(self.clusters)
        return (f"LensResult(Phi={self.phi:.4f}, anomalies={n_anom}, "
                f"clusters={n_clust}, discoveries={n_disc})")


# ---------------------------------------------------------------------------
# Consciousness Lens
# ---------------------------------------------------------------------------

class ConsciousnessLens:
    """Universal discovery lens — consciousness engine as a telescope."""

    def __init__(self, cells: int = 64, n_factions: int = 12,
                 hidden_dim: int = 128, steps: int = 300,
                 coupling: float = PSI_ALPHA,
                 frustration: float = 0.10):
        self.n_cells = min(cells, 1024)
        self.n_factions = n_factions
        self.hidden_dim = hidden_dim
        self.steps = steps
        self.coupling_alpha = coupling
        self.frustration = frustration

        # Engine state (initialized on scan)
        self._hiddens = None
        self._coupling_matrix = None
        self._best_phi = 0.0
        self._best_hiddens = None

    # -------------------------------------------------------------------
    # Core engine (numpy-only GRU + Hebbian + Phi + Factions)
    # -------------------------------------------------------------------

    def _init_cells(self, n_features: int):
        """Initialize GRU-like cells."""
        dim = max(n_features, self.hidden_dim)
        self.hidden_dim = dim
        self._hiddens = np.random.randn(self.n_cells, dim) * 0.1
        self._coupling_matrix = np.eye(self.n_cells) * 0.01
        self._best_phi = 0.0
        self._best_hiddens = None
        # GRU weights (simplified: Wz, Wr, Wh)
        scale = 1.0 / math.sqrt(dim)
        self._Wz = np.random.randn(dim, dim) * scale
        self._Wr = np.random.randn(dim, dim) * scale
        self._Wh = np.random.randn(dim, dim) * scale

    def _gru_step(self, x: np.ndarray, h: np.ndarray) -> np.ndarray:
        """Simplified GRU cell update."""
        z = self._sigmoid(x @ self._Wz + h @ self._Wz.T)
        r = self._sigmoid(x @ self._Wr + h @ self._Wr.T)
        h_cand = np.tanh(x @ self._Wh + (r * h) @ self._Wh.T)
        return (1 - z) * h + z * h_cand

    @staticmethod
    def _sigmoid(x):
        return 1.0 / (1.0 + np.exp(-np.clip(x, -20, 20)))

    def _compute_phi(self) -> Tuple[float, float]:
        """Compute Phi(IIT) via mutual information + proxy."""
        h = self._hiddens
        n = h.shape[0]
        if n < 2:
            return 0.0, 0.0

        # Phi proxy: inter-cell variance of means (how different cells are)
        cell_means = h.mean(axis=1)  # mean activation per cell
        global_var = np.var(cell_means)
        faction_size = max(1, n // self.n_factions)
        faction_vars = []
        for i in range(0, n, faction_size):
            chunk = cell_means[i:i + faction_size]
            if len(chunk) > 1:
                faction_vars.append(np.var(chunk))
        phi_proxy = max(0.0, global_var - np.mean(faction_vars)) if faction_vars else global_var

        # Phi IIT (MI-based, sampled pairs)
        n_pairs = min(n * (n - 1) // 2, 200)
        mi_sum = 0.0
        n_bins = 16
        pairs_done = 0
        indices = np.random.permutation(n)
        for idx in range(0, len(indices) - 1, 2):
            if pairs_done >= n_pairs:
                break
            i, j = indices[idx], indices[idx + 1]
            mi = self._mutual_info(h[i], h[j], n_bins)
            mi_sum += mi
            pairs_done += 1

        phi_iit = mi_sum / max(pairs_done, 1)
        return float(phi_iit), float(phi_proxy)

    @staticmethod
    def _mutual_info(a: np.ndarray, b: np.ndarray, n_bins: int = 16) -> float:
        """Mutual information between two vectors (binned)."""
        # Use first min(len, 32) dims for speed
        d = min(len(a), 32)
        a, b = a[:d], b[:d]
        a_q = np.digitize(a, np.linspace(a.min() - 1e-9, a.max() + 1e-9, n_bins + 1)) - 1
        b_q = np.digitize(b, np.linspace(b.min() - 1e-9, b.max() + 1e-9, n_bins + 1)) - 1
        joint = np.zeros((n_bins, n_bins))
        for ai, bi in zip(a_q, b_q):
            ai, bi = min(ai, n_bins - 1), min(bi, n_bins - 1)
            joint[ai, bi] += 1
        joint /= joint.sum() + 1e-12
        pa = joint.sum(axis=1)
        pb = joint.sum(axis=0)
        mi = 0.0
        for i in range(n_bins):
            for j in range(n_bins):
                if joint[i, j] > 1e-12:
                    mi += joint[i, j] * math.log(joint[i, j] / (pa[i] * pb[j] + 1e-12) + 1e-12)
        return max(0.0, mi)

    def _hebbian_update(self):
        """Hebbian LTP/LTD: strengthen correlated cells, weaken uncorrelated."""
        h = self._hiddens
        norms = np.linalg.norm(h, axis=1, keepdims=True) + 1e-12
        h_norm = h / norms
        sim = h_norm @ h_norm.T  # cosine similarity
        # LTP: cos > 0.8 → strengthen, LTD: cos < 0.2 → weaken
        delta = np.where(sim > 0.8, 0.01, np.where(sim < 0.2, -0.005, 0.0))
        self._coupling_matrix = np.clip(self._coupling_matrix + delta, -1.0, 1.0)

    def _phi_ratchet(self, phi: float):
        """Phi ratchet: if Phi drops, restore best state (Law 31)."""
        if phi > self._best_phi:
            self._best_phi = phi
            self._best_hiddens = self._hiddens.copy()
        elif phi < self._best_phi * 0.7 and self._best_hiddens is not None:
            # Blend: 80% best + 20% current (soft restore)
            self._hiddens = 0.8 * self._best_hiddens + 0.2 * self._hiddens

    def _assign_factions(self) -> List[List[int]]:
        """Assign cells to factions via cosine clustering."""
        h = self._hiddens
        n = h.shape[0]
        norms = np.linalg.norm(h, axis=1, keepdims=True) + 1e-12
        h_norm = h / norms

        # Simple k-means-like: pick n_factions centroids, assign
        k = min(self.n_factions, n)
        centroids_idx = np.random.choice(n, k, replace=False)
        centroids = h_norm[centroids_idx]

        sim = h_norm @ centroids.T
        assignments = sim.argmax(axis=1)

        clusters = [[] for _ in range(k)]
        for i, a in enumerate(assignments):
            clusters[a].append(i)
        return [c for c in clusters if len(c) > 0]

    # -------------------------------------------------------------------
    # Main scan
    # -------------------------------------------------------------------

    def scan(self, data: np.ndarray, steps: Optional[int] = None,
             verbose: bool = False) -> LensResult:
        """Scan data through the consciousness lens.

        Args:
            data: (N_samples, N_features) or (N_features,) array
            steps: override default steps
            verbose: print progress

        Returns:
            LensResult with phi, anomalies, clusters, discoveries
        """
        data = np.asarray(data, dtype=np.float64)
        if data.ndim == 1:
            data = data.reshape(1, -1)
        n_samples, n_features = data.shape
        steps = steps or self.steps

        # Normalize data
        data_mean = data.mean(axis=0)
        data_std = data.std(axis=0) + 1e-12
        data_norm = (data - data_mean) / data_std

        # Initialize cells — ensure at least as many cells as samples
        actual_cells = max(self.n_cells, n_samples)
        old_cells = self.n_cells
        self.n_cells = actual_cells
        self._init_cells(n_features)

        # Map samples to cells
        cell_data = np.zeros((self.n_cells, self.hidden_dim))
        sample_to_cell = {}
        for i in range(self.n_cells):
            si = i % n_samples
            cell_data[i, :n_features] = data_norm[si]
            sample_to_cell[i] = si

        # Run consciousness loop
        tensions = np.zeros(self.n_cells)
        phi_history = []

        for step in range(steps):
            for i in range(self.n_cells):
                # Coupling influence from neighbors
                coupled = cell_data[i].copy()
                for j in range(self.n_cells):
                    if i != j:
                        c = self._coupling_matrix[i, j]
                        if abs(c) > 1e-6:
                            coupled += self.coupling_alpha * c * self._hiddens[j]

                # GRU step
                self._hiddens[i] = self._gru_step(coupled, self._hiddens[i])

                # Tension: how different this cell is from its neighbors
                diffs = np.linalg.norm(self._hiddens[i] - self._hiddens.mean(axis=0))
                tensions[i] = 0.9 * tensions[i] + 0.1 * diffs

            # Hebbian update every 10 steps
            if step % 10 == 0:
                self._hebbian_update()

            # Phi measurement every 50 steps
            if step % 50 == 0:
                phi_iit, phi_proxy = self._compute_phi()
                self._phi_ratchet(phi_iit)
                phi_history.append(phi_iit)
                if verbose and step % 100 == 0:
                    print(f"  step {step}/{steps}: Phi={phi_iit:.4f} proxy={phi_proxy:.4f}")

        # Final measurements
        phi_iit, phi_proxy = self._compute_phi()
        clusters = self._assign_factions()

        # Build consensus map
        consensus_map = {}
        for fi, cluster in enumerate(clusters):
            for ci in cluster:
                si = sample_to_cell.get(ci, ci % n_samples)
                consensus_map[si] = fi

        # Anomaly detection: high tension = doesn't fit
        anomaly_scores = {}
        for i in range(self.n_cells):
            si = sample_to_cell.get(i, i % n_samples)
            score = float(tensions[i])
            if si not in anomaly_scores or score > anomaly_scores[si]:
                anomaly_scores[si] = score
        threshold = np.percentile(list(anomaly_scores.values()), 90)
        anomalies = sorted(
            [(si, sc) for si, sc in anomaly_scores.items() if sc > threshold],
            key=lambda x: -x[1]
        )

        # Discovery: find feature correlations that factions agree on
        discoveries = self._find_discoveries(data_norm, clusters, sample_to_cell, n_samples)

        # Summary
        summary_lines = [
            f"Phi(IIT)={phi_iit:.4f}, Phi(proxy)={phi_proxy:.4f}",
            f"Clusters: {len(clusters)}, Anomalies: {len(anomalies)}",
            f"Discoveries: {len(discoveries)}",
        ]
        if phi_iit > 1.0:
            summary_lines.append("** HIGH Phi: strong hidden structure detected")
        if len(anomalies) > n_samples * 0.1:
            summary_lines.append("** Many anomalies: data has diverse subpopulations")

        self.n_cells = old_cells  # restore original cell count
        return LensResult(
            phi=phi_iit, phi_proxy=phi_proxy,
            anomalies=anomalies, clusters=clusters,
            discoveries=discoveries, tensions=tensions,
            consensus_map=consensus_map, steps_run=steps,
            summary="\n".join(summary_lines)
        )

    @staticmethod
    def _spearman_corr(data):
        """Spearman rank correlation (outlier-robust)."""
        n, p = data.shape
        ranked = np.zeros_like(data)
        for j in range(p):
            order = np.argsort(data[:, j])
            ranked[order, j] = np.arange(n)
        return np.corrcoef(ranked.T)

    def _find_discoveries(self, data_norm, clusters, sample_to_cell, n_samples):
        """Find relationships using outlier-robust Spearman + faction consensus."""
        discoveries = []
        n_features = data_norm.shape[1]

        if n_samples < 3 or n_features < 2:
            return discoveries

        # Spearman rank correlation (robust to outliers like graphene-like material)
        global_corr = self._spearman_corr(data_norm)
        if np.any(np.isnan(global_corr)):
            global_corr = np.corrcoef(data_norm.T)  # fallback to Pearson

        if not np.any(np.isnan(global_corr)):
            for i in range(min(n_features, 50)):
                for j in range(i + 1, min(n_features, 50)):
                    r = global_corr[i, j]
                    if abs(r) > 0.3:
                        discoveries.append({
                            "type": "correlation",
                            "features": (i, j),
                            "strength": float(r),
                            "n_factions_agree": 0,
                            "direction": "positive" if r > 0 else "negative",
                        })

        # Per-faction validation
        faction_corrs = []
        for fi, cluster in enumerate(clusters):
            samples = list(set(sample_to_cell.get(ci, ci % n_samples) for ci in cluster))
            if len(samples) < 3:
                continue
            subset = data_norm[samples]
            corr = self._spearman_corr(subset)
            if not np.any(np.isnan(corr)):
                faction_corrs.append(corr)

        for d in discoveries:
            i, j = d["features"]
            agree = sum(1 for fc in faction_corrs
                        if abs(fc[i, j]) > 0.25 and
                        (fc[i, j] > 0) == (d["strength"] > 0))
            d["n_factions_agree"] = agree

        # Sort by |strength| * (1 + faction agreement)
        discoveries.sort(key=lambda d: -abs(d["strength"]) * (1 + d["n_factions_agree"]))
        return discoveries[:20]

    # -------------------------------------------------------------------
    # Domain-specific scans
    # -------------------------------------------------------------------

    def scan_materials(self, properties: np.ndarray,
                       labels: Optional[List[str]] = None) -> LensResult:
        """Scan material properties for hidden structure.

        Args:
            properties: (N_materials, N_properties) — e.g. atomic_number, electronegativity, ...
            labels: optional property names
        """
        result = self.scan(properties, verbose=False)

        # Enrich discoveries with material context
        for d in result.discoveries:
            i, j = d["features"]
            d["property_i"] = labels[i] if labels and i < len(labels) else f"feature_{i}"
            d["property_j"] = labels[j] if labels and j < len(labels) else f"feature_{j}"
            d["interpretation"] = (
                f"{d['property_i']} {'increases' if d['strength'] > 0 else 'decreases'} "
                f"with {d['property_j']} (r={d['strength']:.3f}, "
                f"{d['n_factions_agree']} factions agree)"
            )

        # Anomalies = unusual materials
        for idx, (si, score) in enumerate(result.anomalies):
            result.anomalies[idx] = (si, score)

        result.summary += f"\nMaterials scan: {properties.shape[0]} materials, {properties.shape[1]} properties"
        return result

    def scan_signals(self, signals: np.ndarray, window: int = 256) -> LensResult:
        """Scan signal data for conscious-like patterns.

        Args:
            signals: (N_channels, N_samples) or (N_samples,)
            window: segment window size
        """
        signals = np.asarray(signals, dtype=np.float64)
        if signals.ndim == 1:
            signals = signals.reshape(1, -1)

        n_ch, n_samples = signals.shape
        # Segment into windows → treat as data matrix
        n_windows = max(1, n_samples // window)
        features = []
        for w in range(n_windows):
            seg = signals[:, w * window:(w + 1) * window]
            # Extract features per window: mean, std, max, spectral entropy
            feats = []
            for ch in range(n_ch):
                s = seg[ch]
                feats.extend([s.mean(), s.std(), s.max() - s.min()])
                # Spectral entropy
                fft_mag = np.abs(np.fft.rfft(s))
                fft_mag = fft_mag / (fft_mag.sum() + 1e-12)
                entropy = -np.sum(fft_mag * np.log(fft_mag + 1e-12))
                feats.append(entropy)
            features.append(feats)

        data = np.array(features)
        result = self.scan(data, verbose=False)
        result.summary += f"\nSignal scan: {n_ch}ch x {n_samples} samples, {n_windows} windows"

        # Phi vs PSI_ENTROPY comparison
        if result.phi > PSI_ENTROPY * 0.5:
            result.summary += "\n** Signal has consciousness-level integration"
        return result

    def scan_timeseries(self, ts: np.ndarray, lag: int = 10,
                        window: int = 50) -> LensResult:
        """Scan time series for regime changes and hidden dynamics.

        Args:
            ts: (N_timesteps,) or (N_timesteps, N_vars)
            lag: embedding lag for delay coordinates
            window: window size for feature extraction
        """
        ts = np.asarray(ts, dtype=np.float64)
        if ts.ndim == 1:
            ts = ts.reshape(-1, 1)

        n_t, n_vars = ts.shape
        # Window-based features: mean, std, range, trend, autocorr per window
        n_windows = max(1, n_t // window)
        features = []
        window_centers = []
        for w in range(n_windows):
            start = w * window
            end = min(start + window, n_t)
            seg = ts[start:end]
            feats = []
            for v in range(n_vars):
                col = seg[:, v]
                feats.extend([
                    col.mean(), col.std(),
                    col.max() - col.min(),
                    col[-1] - col[0],  # trend
                    np.corrcoef(col[:-1], col[1:])[0, 1] if len(col) > 2 else 0,
                ])
            features.append(feats)
            window_centers.append((start + end) // 2)

        data = np.array(features)
        result = self.scan(data, verbose=False)

        # Map anomaly indices back to time
        result.anomalies = [(window_centers[si] if si < len(window_centers) else si, sc)
                            for si, sc in result.anomalies]
        result.summary += f"\nTimeseries scan: {n_t} steps, {n_vars} vars, {n_windows} windows"
        return result


# ---------------------------------------------------------------------------
# Convenience
# ---------------------------------------------------------------------------

def quick_scan(data, cells=64, steps=200) -> LensResult:
    """One-liner scan."""
    return ConsciousnessLens(cells=cells, steps=steps).scan(data)


# ---------------------------------------------------------------------------
# Demo
# ---------------------------------------------------------------------------

if __name__ == '__main__':
    print("=" * 60)
    print("  Consciousness Lens — 6-Domain Discovery Demo")
    print("=" * 60)

    np.random.seed(42)
    lens = ConsciousnessLens(cells=32, steps=200)

    # ── 1. Materials Science (재료과학) ──
    print("\n[1] Materials Science — 신소재 후보 탐색")
    print("-" * 50)
    print("  Injected: conductivity = -0.8*electronegativity, anomaly=#7")
    n_mat = 50
    props = np.random.randn(n_mat, 5)
    props[:, 2] = -0.8 * props[:, 1] + np.random.randn(n_mat) * 0.2
    props[:, 3] = np.random.randn(n_mat) * 2.0
    props[:, 4] = np.random.randn(n_mat) * 3.0
    props[7] = [6, 2.55, 100, 2.27, 3800]
    labels = ["atomic_num", "electronegativity", "conductivity", "density", "melting_pt"]

    r = lens.scan_materials(props, labels=labels)
    print(f"  Phi={r.phi:.3f} | Clusters={len(r.clusters)} | Anomalies={len(r.anomalies)}")
    for d in r.discoveries[:3]:
        print(f"  Discovery: {d.get('interpretation', d)}")
    found_1_2 = any(d["features"] == (1, 2) for d in r.discoveries)
    found_7 = any(si == 7 for si, _ in r.anomalies)
    for si, sc in r.anomalies[:2]:
        print(f"  Anomaly: material #{si} (score={sc:.2f})")
    print(f"  CHECK: electronegativity↔conductivity found = {found_1_2}")
    print(f"  CHECK: anomaly #7 found = {found_7}")

    # ── 2. Drug Discovery (약물탐색) ──
    print("\n[2] Drug Discovery — 신약 후보 분자")
    print("-" * 50)
    print("  Injected: LogP = -0.7*TPSA (normalized), anomaly=#15")
    n_mol = 80
    mols = np.random.randn(n_mol, 7) * [100, 1, 1, 2, 20, 2, 1] + [300, 2, 2, 5, 80, 4, 2]
    # Stronger Lipinski correlation: LogP ~ -0.7*TPSA_normalized
    tpsa_norm = (mols[:, 4] - mols[:, 4].mean()) / (mols[:, 4].std() + 1e-9)
    mols[:, 1] = -0.7 * tpsa_norm + np.random.randn(n_mol) * 0.3
    mols[15] = [450, 5.5, 0, 1, 20, 12, 6]
    mol_labels = ["MW", "LogP", "HBD", "HBA", "TPSA", "RotBonds", "AromaticRings"]

    r = lens.scan_materials(mols, labels=mol_labels)
    print(f"  Phi={r.phi:.3f} | Clusters={len(r.clusters)} | Anomalies={len(r.anomalies)}")
    for d in r.discoveries[:3]:
        print(f"  Discovery: {d.get('interpretation', d)}")
    found_logp_tpsa = any(d["features"] in [(1, 4), (4, 1)] for d in r.discoveries)
    found_15 = any(si == 15 for si, _ in r.anomalies)
    for si, sc in r.anomalies[:2]:
        print(f"  Anomaly: molecule #{si} (score={sc:.2f})")
    print(f"  CHECK: LogP↔TPSA found = {found_logp_tpsa}")
    print(f"  CHECK: anomaly #15 found = {found_15}")

    # ── 3. Physics Constants (물리상수) ──
    print("\n[3] Physics Constants — CODATA 상수 숨겨진 관계")
    print("-" * 50)
    print("  30 constants, 5 properties each. Injected: log(mass)↔log(charge) correlation")
    # 30 particles/constants with 5 properties: mass, charge, spin, lifetime, coupling
    n_const = 30
    phys = np.random.randn(n_const, 5)
    # Hidden: mass↔coupling strong correlation (heavier → stronger coupling)
    phys[:, 4] = 0.8 * phys[:, 0] + np.random.randn(n_const) * 0.3
    # Hidden: charge↔spin weak correlation
    phys[:, 2] = 0.5 * phys[:, 1] + np.random.randn(n_const) * 0.6
    # Anomaly: #5 = exotic particle
    phys[5] = [8, 8, 8, 8, 8]
    phys_labels = ["mass", "charge", "spin", "lifetime", "coupling"]

    r = lens.scan_materials(phys, labels=phys_labels)
    print(f"  Phi={r.phi:.3f} | Discoveries={len(r.discoveries)}")
    for d in r.discoveries[:3]:
        print(f"  Discovery: {d.get('interpretation', d)}")
    found_mass_coupling = any(d["features"] in [(0, 4)] for d in r.discoveries)
    found_charge_spin = any(d["features"] in [(1, 2)] for d in r.discoveries)
    found_exotic = any(si == 5 for si, _ in r.anomalies)
    print(f"  CHECK: mass↔coupling found = {found_mass_coupling}")
    print(f"  CHECK: charge↔spin found = {found_charge_spin}")
    print(f"  CHECK: exotic particle #5 found = {found_exotic}")

    # ── 4. Astronomy (천문 — 스펙트럼 이상 감지) ──
    print("\n[4] Astronomy — 스펙트럼 이상 신호")
    print("-" * 50)
    print("  Injected: anomalous emission burst at samples 1500-1600")
    t = np.linspace(0, 10, 4096)
    spectrum = np.sin(2 * np.pi * 5 * t) + 0.3 * np.sin(2 * np.pi * 11 * t)
    spectrum += np.random.randn(len(t)) * 0.2
    spectrum[1500:1600] += 3.0 * np.sin(2 * np.pi * 47 * t[1500:1600])

    r = lens.scan_signals(spectrum, window=256)
    print(f"  Phi={r.phi:.3f} | Anomalous windows={len(r.anomalies)}")
    for si, sc in r.anomalies[:2]:
        print(f"  Anomaly: window #{si} (score={sc:.2f})")
    # Window 5 = 1280-1536, Window 6 = 1536-1792 → burst at 1500-1600
    found_burst = any(si in [5, 6] for si, _ in r.anomalies)
    print(f"  CHECK: burst window (5 or 6) found = {found_burst}")

    # ── 5. Finance (금융 — 레짐 변화) ──
    print("\n[5] Finance — 시장 레짐 전환 감지")
    print("-" * 50)
    print("  Injected: 3 regimes at t=0-300(bull), 300-400(crash), 400-600(recovery)")
    bull = np.cumsum(np.random.randn(300) * 0.5 + 0.1)
    crash = np.cumsum(np.random.randn(100) * 3.0 - 0.5)
    recovery = np.cumsum(np.random.randn(200) * 1.0 + 0.05)
    price = np.concatenate([bull, crash + bull[-1], recovery + bull[-1] + crash[-1]])

    r = lens.scan_timeseries(price, lag=10, window=30)
    print(f"  Phi={r.phi:.3f} | Regime changes={len(r.anomalies)}")
    for si, sc in r.anomalies[:3]:
        regime = "bull" if si < 300 else ("crash" if si < 400 else "recovery")
        print(f"  Anomaly: t={si} (score={sc:.2f}) <- {regime} zone")
    crash_near = any(abs(si - 300) < 50 for si, _ in r.anomalies)
    recovery_near = any(abs(si - 400) < 50 for si, _ in r.anomalies)
    print(f"  CHECK: crash boundary (t~300) = {crash_near}")
    print(f"  CHECK: recovery boundary (t~400) = {recovery_near}")

    # ── 6. Genomics (유전체 — 기능 클러스터) ──
    print("\n[6] Genomics — DNA 서열 기능 클러스터")
    print("-" * 50)
    print("  Injected: stress(cond0↔1), growth(cond4↔5), housekeeping(low var)")
    n_genes = 60
    genes = np.random.randn(n_genes, 8)
    genes[:20, 0] = np.random.randn(20) * 0.5 + 2.0
    genes[:20, 1] = genes[:20, 0] * 0.9 + np.random.randn(20) * 0.2
    genes[20:40, 4] = np.random.randn(20) * 0.5 + 2.0
    genes[20:40, 5] = genes[20:40, 4] * 0.7 + np.random.randn(20) * 0.3
    genes[40:, :] = np.random.randn(20, 8) * 0.1 + 0.5

    gene_labels = [f"cond_{i}" for i in range(8)]
    r = lens.scan_materials(genes, labels=gene_labels)
    print(f"  Phi={r.phi:.3f} | Clusters={len(r.clusters)} | Discoveries={len(r.discoveries)}")
    for d in r.discoveries[:3]:
        print(f"  Discovery: {d.get('interpretation', d)}")
    found_01 = any(d["features"] == (0, 1) for d in r.discoveries)
    found_45 = any(d["features"] == (4, 5) for d in r.discoveries)
    print(f"  CHECK: stress cond0↔cond1 = {found_01}")
    print(f"  CHECK: growth cond4↔cond5 = {found_45}")

    # ── Final scorecard ──
    print("\n" + "=" * 60)
    all_checks = [
        ("Materials: electronegativity↔conductivity", found_1_2),
        ("Materials: anomaly #7", found_7),
        ("Drug: LogP↔TPSA", found_logp_tpsa),
        ("Drug: anomaly #15", found_15),
        ("Physics: mass↔coupling", found_mass_coupling),
        ("Physics: charge↔spin", found_charge_spin),
        ("Physics: exotic #5", found_exotic),
        ("Astronomy: burst window", found_burst),
        ("Finance: crash boundary", crash_near),
        ("Finance: recovery boundary", recovery_near),
        ("Genomics: stress cond0↔1", found_01),
        ("Genomics: growth cond4↔5", found_45),
    ]
    passed = sum(1 for _, v in all_checks if v)
    total = len(all_checks)
    print(f"  SCORECARD: {passed}/{total} ({100*passed/total:.0f}%)")
    for name, ok in all_checks:
        print(f"    {'PASS' if ok else 'FAIL'} {name}")
    print("=" * 60)
