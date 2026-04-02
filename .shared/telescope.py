"""telescope.py — 9-Lens Telescope Toolset: unified runner for all lens combinations

511 possible combinations from 9 lenses. Run any subset or all at once.

Usage:
    from telescope import Telescope

    t = Telescope()
    # Full scan (all 9 lenses)
    results = t.full_scan(data)

    # Preset combos
    results = t.material_scan(data, labels=["A","B","C"])
    results = t.signal_scan(signal_array)
    results = t.timeseries_scan(ts_data)

    # Custom combo
    results = t.scan(data, lenses=["consciousness", "gravity", "topology"])

    # All 511 combos (exhaustive)
    all_results = t.exhaustive_scan(data)
"""

import sys
import os
from itertools import combinations
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field

import numpy as np

_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, _DIR)

# Lazy imports — each lens loaded only when needed
_LENS_REGISTRY = {
    "consciousness": ("consciousness_lens", "ConsciousnessLens"),
    "gravity":       ("gravity_lens", "GravityLens"),
    "topology":      ("topology_lens", "TopologyLens"),
    "thermo":        ("thermo_lens", "ThermoLens"),
    "wave":          ("wave_lens", "WaveLens"),
    "evolution":     ("evolution_lens", "EvolutionLens"),
    "info":          ("info_lens", "InfoLens"),
    "quantum":       ("quantum_lens", "QuantumLens"),
    "em":            ("em_lens", "EMLens"),
}

ALL_LENS_NAMES = list(_LENS_REGISTRY.keys())

# Preset combinations for common tasks
PRESETS = {
    "basic":      ["consciousness", "gravity", "topology"],
    "material":   ["consciousness", "gravity", "thermo", "evolution"],
    "signal":     ["consciousness", "wave", "quantum", "info"],
    "timeseries": ["consciousness", "wave", "thermo", "gravity"],
    "discovery":  ["consciousness", "info", "quantum", "topology"],
    "optimize":   ["evolution", "gravity", "thermo"],
    "full":       ALL_LENS_NAMES,
}


@dataclass
class TelescopeResult:
    """Combined result from multiple lenses."""
    lens_results: Dict[str, Any] = field(default_factory=dict)
    combo: List[str] = field(default_factory=list)
    cross_findings: List[Dict] = field(default_factory=list)
    summary: str = ""

    def __repr__(self):
        lenses = ", ".join(self.combo)
        n_cross = len(self.cross_findings)
        return f"TelescopeResult(lenses=[{lenses}], cross_findings={n_cross})"


def _load_lens(name: str):
    """Lazy-load a lens class."""
    if name not in _LENS_REGISTRY:
        raise ValueError(f"Unknown lens: {name}. Available: {ALL_LENS_NAMES}")
    module_name, class_name = _LENS_REGISTRY[name]
    try:
        mod = __import__(module_name)
        return getattr(mod, class_name)
    except (ImportError, AttributeError) as e:
        return None


class Telescope:
    """9-lens telescope: run any combination of lenses on data."""

    def __init__(self, verbose: bool = False):
        self.verbose = verbose
        self._cache = {}

    def _get_lens(self, name: str):
        if name not in self._cache:
            cls = _load_lens(name)
            if cls is not None:
                self._cache[name] = cls()
            else:
                self._cache[name] = None
        return self._cache[name]

    def scan(self, data: np.ndarray, lenses: Optional[List[str]] = None,
             labels: Optional[List[str]] = None) -> TelescopeResult:
        """Run selected lenses on data.

        Args:
            data: (N_samples, N_features) array
            lenses: list of lens names, or preset name ("basic", "full", etc.)
            labels: optional feature labels
        """
        if lenses is None:
            lenses = PRESETS["basic"]
        elif isinstance(lenses, str):
            lenses = PRESETS.get(lenses, [lenses])

        results = {}
        for name in lenses:
            lens = self._get_lens(name)
            if lens is None:
                if self.verbose:
                    print(f"  [{name}] not available, skipping")
                continue
            try:
                if hasattr(lens, 'scan_materials') and labels:
                    r = lens.scan_materials(data, labels=labels)
                else:
                    r = lens.scan(data)
                results[name] = r
                if self.verbose:
                    print(f"  [{name}] done: {getattr(r, 'summary', '')[:80]}")
            except Exception as e:
                if self.verbose:
                    print(f"  [{name}] error: {e}")

        # Cross-lens analysis
        cross = self._cross_analyze(results)

        summary_lines = [f"Telescope: {len(results)}/{len(lenses)} lenses completed"]
        for name, r in results.items():
            s = getattr(r, 'summary', str(r))
            first_line = s.split('\n')[0] if s else ''
            summary_lines.append(f"  {name}: {first_line[:60]}")
        if cross:
            summary_lines.append(f"Cross-findings: {len(cross)}")

        return TelescopeResult(
            lens_results=results,
            combo=list(results.keys()),
            cross_findings=cross,
            summary="\n".join(summary_lines)
        )

    def full_scan(self, data, **kwargs) -> TelescopeResult:
        """Run all 9 lenses."""
        return self.scan(data, lenses="full", **kwargs)

    def material_scan(self, data, **kwargs) -> TelescopeResult:
        """Preset for material discovery."""
        return self.scan(data, lenses="material", **kwargs)

    def signal_scan(self, data, **kwargs) -> TelescopeResult:
        """Preset for signal analysis."""
        return self.scan(data, lenses="signal", **kwargs)

    def timeseries_scan(self, data, **kwargs) -> TelescopeResult:
        """Preset for time series."""
        return self.scan(data, lenses="timeseries", **kwargs)

    def exhaustive_scan(self, data, min_combo: int = 1, max_combo: int = 3,
                        **kwargs) -> List[TelescopeResult]:
        """Run all combinations up to max_combo size."""
        all_results = []
        for r in range(min_combo, min(max_combo + 1, len(ALL_LENS_NAMES) + 1)):
            for combo in combinations(ALL_LENS_NAMES, r):
                result = self.scan(data, lenses=list(combo), **kwargs)
                all_results.append(result)
        return all_results

    def _cross_analyze(self, results: Dict) -> List[Dict]:
        """Find agreements/conflicts between lenses."""
        cross = []

        # Extract anomalies from each lens
        anomaly_sets = {}
        for name, r in results.items():
            if hasattr(r, 'anomalies') and r.anomalies:
                indices = set()
                for item in r.anomalies:
                    if isinstance(item, tuple) and len(item) >= 2:
                        indices.add(item[0])
                    elif isinstance(item, (int, np.integer)):
                        indices.add(int(item))
                anomaly_sets[name] = indices

        # Find anomalies confirmed by multiple lenses
        if len(anomaly_sets) >= 2:
            all_anomalies = set()
            for s in anomaly_sets.values():
                all_anomalies |= s
            for idx in all_anomalies:
                confirming = [n for n, s in anomaly_sets.items() if idx in s]
                if len(confirming) >= 2:
                    cross.append({
                        "type": "multi_lens_anomaly",
                        "sample": int(idx),
                        "confirmed_by": confirming,
                        "confidence": len(confirming) / len(anomaly_sets),
                    })

        # Extract discoveries/correlations
        discovery_sets = {}
        for name, r in results.items():
            if hasattr(r, 'discoveries') and r.discoveries:
                for d in r.discoveries:
                    if isinstance(d, dict) and "features" in d:
                        key = tuple(sorted(d["features"]))
                        if key not in discovery_sets:
                            discovery_sets[key] = []
                        discovery_sets[key].append(name)

        for features, lenses in discovery_sets.items():
            if len(lenses) >= 2:
                cross.append({
                    "type": "multi_lens_discovery",
                    "features": features,
                    "confirmed_by": lenses,
                    "confidence": len(lenses) / len(results),
                })

        cross.sort(key=lambda x: -x.get("confidence", 0))
        return cross

    @staticmethod
    def available_lenses() -> List[str]:
        """List available lenses."""
        available = []
        for name in ALL_LENS_NAMES:
            cls = _load_lens(name)
            available.append(f"{'OK' if cls else '--'} {name}")
        return available

    @staticmethod
    def list_presets() -> Dict[str, List[str]]:
        return PRESETS

    @staticmethod
    def total_combinations() -> int:
        """Total possible combinations: 2^9 - 1 = 511."""
        return 2 ** len(ALL_LENS_NAMES) - 1


if __name__ == '__main__':
    print("=" * 60)
    print("  Telescope — 9-Lens Discovery Toolset")
    print("=" * 60)

    print("\nAvailable lenses:")
    for s in Telescope.available_lenses():
        print(f"  {s}")

    print(f"\nTotal combinations: {Telescope.total_combinations()}")
    print(f"\nPresets:")
    for name, lenses in Telescope.list_presets().items():
        print(f"  {name}: {', '.join(lenses)}")

    # Quick demo with available lenses
    np.random.seed(42)
    data = np.random.randn(50, 5)
    data[:, 2] = -0.8 * data[:, 1] + np.random.randn(50) * 0.2
    data[7] = [10, 10, 10, 10, 10]

    t = Telescope(verbose=True)
    print("\n--- Basic scan (3 lenses) ---")
    result = t.scan(data, lenses="basic",
                    labels=["A", "B", "C", "D", "E"])
    print(f"\n{result}")
    print(result.summary)
    if result.cross_findings:
        print(f"\nCross-lens findings:")
        for cf in result.cross_findings[:5]:
            print(f"  {cf}")
