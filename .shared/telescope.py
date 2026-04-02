"""telescope.py — Rust-backed telescope (telescope_rs)

All 3 core lenses run in Rust via PyO3. ×2~×82 faster than Python.
Install: cd ~/Dev/anima/anima/anima-rs/crates/telescope-rs && maturin build --release && pip install <wheel>

Usage:
    from telescope import Telescope
    t = Telescope()
    r = t.full_scan(data)           # all 3 lenses
    r = t.consciousness_scan(data)  # consciousness only
    r = t.topology_scan(data)       # topology only
    r = t.causal_scan(data)         # causal only
"""

import numpy as np
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional, Tuple

import telescope_rs

# ── Result types ──────────────────────────────────────────

@dataclass
class LensResult:
    phi: float = 0.0
    phi_proxy: float = 0.0
    anomalies: List[Tuple[int, float]] = field(default_factory=list)
    clusters: List[List[int]] = field(default_factory=list)
    discoveries: List[Dict[str, Any]] = field(default_factory=list)
    summary: str = ""
    betti_numbers: Tuple[int, int] = (0, 0)
    components: List[List[int]] = field(default_factory=list)
    holes: List[Dict[str, Any]] = field(default_factory=list)
    phase_transitions: List[Tuple[float, str]] = field(default_factory=list)
    causal_pairs: list = field(default_factory=list)
    causal_graph: Dict[int, List[int]] = field(default_factory=dict)
    overall_symmetry: float = 0.0
    reflection_scores: list = field(default_factory=list)


@dataclass
class ScanResult:
    lens_results: Dict[str, LensResult] = field(default_factory=dict)
    cross_findings: List[Dict[str, Any]] = field(default_factory=list)


# ── Telescope ─────────────────────────────────────────────

class Telescope:
    """Rust-backed 3-lens telescope."""

    def __init__(self, n_cells: int = 64, steps: int = 300,
                 n_factions: int = 12, coupling_alpha: float = 0.014,
                 verbose: bool = False):
        self.n_cells = n_cells
        self.steps = steps
        self.n_factions = n_factions
        self.coupling_alpha = coupling_alpha
        self.verbose = verbose

    def full_scan(self, data: np.ndarray) -> ScanResult:
        """Run all 3 lenses on data (N_samples, N_features)."""
        data = np.asarray(data, dtype=np.float64)
        if data.ndim == 1:
            data = data.reshape(-1, 1)

        result = ScanResult()
        result.lens_results['consciousness'] = self._consciousness(data)
        result.lens_results['topology'] = self._topology(data)
        result.lens_results['causal'] = self._causal(data)

        # Cross-findings: patterns found by 2+ lenses
        result.cross_findings = self._cross_validate(result.lens_results)
        return result

    def scan(self, data: np.ndarray, preset: str = "discovery") -> ScanResult:
        """Alias for full_scan (all presets use same 3 Rust lenses)."""
        return self.full_scan(data)

    def consciousness_scan(self, data: np.ndarray) -> LensResult:
        data = np.asarray(data, dtype=np.float64)
        if data.ndim == 1:
            data = data.reshape(-1, 1)
        return self._consciousness(data)

    def topology_scan(self, data: np.ndarray) -> LensResult:
        data = np.asarray(data, dtype=np.float64)
        if data.ndim == 1:
            data = data.reshape(-1, 1)
        return self._topology(data)

    def causal_scan(self, data: np.ndarray) -> LensResult:
        data = np.asarray(data, dtype=np.float64)
        if data.ndim == 1:
            data = data.reshape(-1, 1)
        return self._causal(data)

    # ── Internal ──────────────────────────────────────────

    def _consciousness(self, data: np.ndarray) -> LensResult:
        r = telescope_rs.consciousness_scan(
            data, n_cells=self.n_cells, n_factions=self.n_factions,
            steps=self.steps, coupling_alpha=self.coupling_alpha)

        anomalies = []
        if 'anomaly_indices' in r and 'anomaly_scores' in r:
            idx = np.asarray(r['anomaly_indices'], dtype=int)
            scores = np.asarray(r['anomaly_scores'])
            anomalies = [(int(idx[i]), float(scores[i])) for i in range(len(idx))]

        return LensResult(
            phi=r['phi_iit'], phi_proxy=r.get('phi_proxy', 0.0),
            anomalies=anomalies,
            summary=f"Phi(IIT)={r['phi_iit']:.4f}, clusters={r['n_clusters']}, steps={r['steps_run']}")

    def _topology(self, data: np.ndarray) -> LensResult:
        r = telescope_rs.topology_scan(data, n_filtration_steps=100,
                                        persistence_threshold=self.coupling_alpha)

        phase_transitions = []
        for pt in r.get('phase_transitions', []):
            if isinstance(pt, str):
                phase_transitions.append((0.0, pt))
            else:
                phase_transitions.append((0.0, str(pt)))

        return LensResult(
            betti_numbers=(r['betti_0'], r['betti_1']),
            holes=[{'persistence': 0}] * r['n_holes'],
            phase_transitions=phase_transitions,
            summary=f"B0={r['betti_0']}, B1={r['betti_1']}, holes={r['n_holes']}, scale={r['optimal_scale']:.4f}")

    def _causal(self, data: np.ndarray) -> LensResult:
        r = telescope_rs.causal_scan(data, max_lag=5, te_bins=16, min_strength=0.1)

        causal_pairs = []
        causes = r.get('causes', [])
        effects = r.get('effects', [])
        strengths = r.get('strengths', [])
        for i in range(len(causes)):
            causal_pairs.append({
                'cause': causes[i], 'effect': effects[i],
                'strength': strengths[i] if i < len(strengths) else 0.0,
            })

        graph = {}
        for p in causal_pairs:
            c = p['cause']
            graph.setdefault(c, []).append(p['effect'])

        return LensResult(
            causal_pairs=causal_pairs,
            causal_graph=graph,
            summary=f"pairs={len(causal_pairs)}, features={r['n_features']}")

    def _cross_validate(self, results: Dict[str, LensResult]) -> List[Dict[str, Any]]:
        """Find patterns confirmed by multiple lenses."""
        findings = []

        c = results.get('consciousness')
        t = results.get('topology')

        if c and t:
            # High Phi + non-trivial topology = real structure
            if c.phi > 0.5 and t.betti_numbers[1] > 0:
                findings.append({
                    'type': 'cross_structure',
                    'lenses': ['consciousness', 'topology'],
                    'description': f'High Phi ({c.phi:.3f}) + {t.betti_numbers[1]} holes → real hidden structure',
                    'confidence': min(1.0, c.phi),
                })

        return findings


# ── Convenience aliases (backward compat) ─────────────────

class ConsciousnessLens:
    """Backward-compatible alias → Rust telescope_rs."""
    def __init__(self, cells=64, **kw):
        self._t = Telescope(n_cells=cells, **kw)
    def scan(self, data, **kw):
        return self._t.consciousness_scan(data)

class TopologyLens:
    def __init__(self, **kw):
        self._t = Telescope(**kw)
    def scan(self, data, **kw):
        return self._t.topology_scan(data)

class CausalLens:
    def __init__(self, **kw):
        self._t = Telescope(**kw)
    def scan(self, data, **kw):
        return self._t.causal_scan(data)
