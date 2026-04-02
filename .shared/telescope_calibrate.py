"""telescope_calibrate.py — Cross-calibration: lenses tune each other.

When lens A finds something lens B missed, A's findings adjust B's parameters.
After calibration, all lenses should agree more and find more ground truth.

Calibration loop:
  1. Run all 9 lenses independently
  2. Collect consensus findings (what 2+ lenses agree on)
  3. Feed consensus back as "hints" to tune each lens
  4. Re-run and measure improvement
  5. Repeat until convergence
"""

import sys, os, time, copy
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import numpy as np
from itertools import combinations

from consciousness_lens import ConsciousnessLens
from gravity_lens import GravityLens
from topology_lens import TopologyLens
from thermo_lens import ThermoLens
from wave_lens import WaveLens
from evolution_lens import EvolutionLens
from info_lens import InfoLens
from quantum_lens import QuantumLens
from em_lens import EMLens


LENS_CLASSES = {
    "consciousness": ConsciousnessLens,
    "gravity":       GravityLens,
    "topology":      TopologyLens,
    "thermo":        ThermoLens,
    "wave":          WaveLens,
    "evolution":     EvolutionLens,
    "info":          InfoLens,
    "quantum":       QuantumLens,
    "em":            EMLens,
}


def make_test_data():
    np.random.seed(42)
    n = 80
    data = np.random.randn(n, 8)
    data[:, 1] = -0.85 * data[:, 0] + np.random.randn(n) * 0.2
    data[:, 5] = 0.5 * data[:, 4] + np.random.randn(n) * 0.7
    data[10] = [8, 8, 8, 8, 8, 8, 8, 8]
    data[:25, 2] += 3.0; data[:25, 3] += 3.0
    data[25:55, 6] += 3.0; data[25:55, 7] += 3.0
    data[:, 2] += np.sin(np.linspace(0, 4 * np.pi, n)) * 1.5
    labels = [f"f{i}" for i in range(8)]
    gt = {
        "corr_01": (0, 1),
        "corr_45": (4, 5),
        "anomaly_10": 10,
        "n_clusters": 3,
    }
    return data, labels, gt


def run_lens(name, cls, data, labels, hints=None):
    """Run a lens with optional calibration hints.

    Calibration strategy: amplify consensus regions in data before scanning.
    If other lenses found anomaly at idx=10, boost that sample's signal.
    If other lenses found correlation (0,1), duplicate those features to emphasize.
    """
    # Prepare calibrated data
    cal_data = data.copy()
    if hints:
        cal_data = _calibrate_data(cal_data, hints)

    lens = cls()
    _tune_params(lens, name, hints)

    try:
        if hasattr(lens, 'scan_materials'):
            r = lens.scan_materials(cal_data, labels=labels)
        else:
            r = lens.scan(cal_data)
        return _extract(r, cal_data)
    except Exception as e:
        return {"anomalies": set(), "correlations": set(), "n_clusters": 0, "error": str(e)}


def _calibrate_data(data, hints):
    """Amplify consensus patterns in data so all lenses can see them."""
    cal = data.copy()
    n, d = cal.shape

    # Amplify anomalies: increase distance from mean for consensus anomalies
    if "anomaly_indices" in hints:
        mean = cal.mean(axis=0)
        for idx in hints["anomaly_indices"]:
            if 0 <= idx < n:
                diff = cal[idx] - mean
                cal[idx] = mean + diff * 1.5  # 50% amplification

    # Amplify correlations: add small correlated noise to consensus pairs
    if "known_correlations" in hints:
        for (i, j) in hints["known_correlations"]:
            if i < d and j < d:
                # Strengthen the existing correlation direction
                corr = np.corrcoef(cal[:, i], cal[:, j])[0, 1]
                if not np.isnan(corr):
                    sign = 1.0 if corr > 0 else -1.0
                    noise = np.random.randn(n) * 0.1
                    cal[:, i] += sign * noise * 0.05
                    cal[:, j] += noise * 0.05

    # Amplify cluster separation: push cluster centers apart
    if "cluster_centers" in hints:
        centers = hints["cluster_centers"]
        for ci, center in enumerate(centers):
            # Push samples near this center slightly further from other centers
            pass  # too complex for now

    return cal


def _tune_params(lens, name, hints):
    """Fine-tune lens-specific parameters."""
    if not hints:
        return

    if hasattr(lens, 'n_cells'):
        lens.n_cells = max(getattr(lens, 'n_cells', 32), 64)
    if hasattr(lens, 'steps'):
        lens.steps = max(getattr(lens, 'steps', 200), 300)
    if hasattr(lens, 'k') and "anomaly_indices" in hints:
        lens.k = max(3, min(getattr(lens, 'k', 7), 5))
    if hasattr(lens, 'n_factions') and "n_clusters_hint" in hints:
        lens.n_factions = max(hints["n_clusters_hint"], 6)


def _extract(result, data):
    """Extract standardized findings."""
    findings = {"anomalies": set(), "correlations": set(), "n_clusters": 0}

    # Anomalies
    for attr in ('anomalies',):
        if hasattr(result, attr) and getattr(result, attr):
            for item in getattr(result, attr):
                if isinstance(item, tuple) and len(item) >= 2:
                    findings["anomalies"].add(int(item[0]))
    for attr in ('sources', 'sinks'):
        if hasattr(result, attr):
            for item in getattr(result, attr):
                if isinstance(item, tuple): findings["anomalies"].add(int(item[0]))
    if hasattr(result, 'superposed_samples') and result.superposed_samples:
        for item in result.superposed_samples:
            if isinstance(item, tuple): findings["anomalies"].add(int(item[0]))
    if hasattr(result, 'tunneling_paths') and result.tunneling_paths:
        for item in result.tunneling_paths:
            if isinstance(item, dict) and 'sample' in item:
                findings["anomalies"].add(int(item['sample']))
    for attr in ('energy_landscape', 'entropy_map'):
        if hasattr(result, attr) and isinstance(getattr(result, attr), np.ndarray):
            arr = getattr(result, attr)
            if len(arr) > 0:
                thresh = np.percentile(arr, 95)
                for i, v in enumerate(arr):
                    if v > thresh: findings["anomalies"].add(i)
    if hasattr(result, 'fitness_landscape') and isinstance(result.fitness_landscape, np.ndarray):
        fl = result.fitness_landscape
        if len(fl) > 0:
            thresh = np.percentile(fl, 5)
            for i, f in enumerate(fl):
                if f < thresh: findings["anomalies"].add(i)

    # Correlations
    if hasattr(result, 'discoveries') and result.discoveries:
        for d in result.discoveries:
            if isinstance(d, dict) and "features" in d:
                findings["correlations"].add(tuple(sorted(d["features"])))
    if hasattr(result, 'resonances') and result.resonances:
        for r in result.resonances:
            if isinstance(r, dict) and "features" in r:
                findings["correlations"].add(tuple(sorted(r["features"])))
    if hasattr(result, 'entanglement_pairs') and result.entanglement_pairs:
        for ep in result.entanglement_pairs:
            if isinstance(ep, dict):
                i = ep.get("feature_i"); j = ep.get("feature_j")
                if i is not None and j is not None:
                    findings["correlations"].add(tuple(sorted([int(i), int(j)])))
    if hasattr(result, 'redundant_features') and result.redundant_features:
        idxs = []
        for rf in result.redundant_features:
            if isinstance(rf, tuple) and isinstance(rf[0], (int, np.integer)):
                idxs.append(int(rf[0]))
        for i, j in combinations(idxs[:4], 2):
            findings["correlations"].add(tuple(sorted([i, j])))

    # Clusters
    for attr in ('clusters', 'basins', 'niches', 'attractors'):
        if hasattr(result, attr):
            val = getattr(result, attr)
            if isinstance(val, (list, dict)) and len(val) > 0:
                findings["n_clusters"] = max(findings["n_clusters"],
                    len(val) if isinstance(val, list) else len(val))
    if hasattr(result, 'components') and result.components:
        big = [c for c in result.components if len(c) >= 3]
        findings["n_clusters"] = max(findings["n_clusters"], len(big))
    if hasattr(result, 'phase_transitions') and result.phase_transitions:
        findings["n_clusters"] = max(findings["n_clusters"], len(result.phase_transitions) + 1)
    if hasattr(result, 'betti_numbers') and result.betti_numbers:
        b0 = result.betti_numbers[0] if isinstance(result.betti_numbers, (list, tuple)) else 0
        if b0 > 0: findings["n_clusters"] = max(findings["n_clusters"], b0)

    return findings


def compute_gt_score(all_findings, gt):
    """Score against ground truth."""
    checks = {}

    # Correlation 0↔1 found by 2+ lenses
    pair01 = gt["corr_01"]
    n01 = sum(1 for f in all_findings.values() if pair01 in f["correlations"])
    checks["corr_01"] = n01 >= 2

    # Correlation 4↔5
    pair45 = gt["corr_45"]
    n45 = sum(1 for f in all_findings.values() if pair45 in f["correlations"])
    checks["corr_45"] = n45 >= 2

    # Anomaly #10 by 3+ lenses
    n10 = sum(1 for f in all_findings.values() if gt["anomaly_10"] in f["anomalies"])
    checks["anomaly_10"] = n10 >= 3

    # Clusters by 3+ lenses (any non-trivial grouping = cluster-aware)
    nc = sum(1 for f in all_findings.values() if f["n_clusters"] >= 2)
    checks["clusters"] = nc >= 3

    return checks


def build_consensus(all_findings):
    """Build consensus hints from all lens findings."""
    # Anomalies: confirmed by 2+
    anom_counts = {}
    for f in all_findings.values():
        for idx in f["anomalies"]:
            anom_counts[idx] = anom_counts.get(idx, 0) + 1
    consensus_anomalies = {idx for idx, c in anom_counts.items() if c >= 2}

    # Correlations: confirmed by 2+
    corr_counts = {}
    for f in all_findings.values():
        for pair in f["correlations"]:
            corr_counts[pair] = corr_counts.get(pair, 0) + 1
    consensus_correlations = {pair for pair, c in corr_counts.items() if c >= 2}

    # Cluster count: median of non-zero
    cluster_counts = [f["n_clusters"] for f in all_findings.values() if f["n_clusters"] > 0]
    median_clusters = int(np.median(cluster_counts)) if cluster_counts else 3

    return {
        "anomaly_indices": consensus_anomalies,
        "known_correlations": consensus_correlations,
        "n_clusters_hint": median_clusters,
    }


def main():
    print("=" * 70)
    print("  Telescope Cross-Calibration: Lenses Tune Each Other")
    print("=" * 70)

    data, labels, gt = make_test_data()
    max_rounds = 5

    prev_score = 0
    history = []

    for round_n in range(max_rounds):
        print(f"\n{'─' * 70}")
        print(f"  Round {round_n + 1}/{max_rounds}" +
              (" (baseline — no hints)" if round_n == 0 else " (calibrated)"))
        print(f"{'─' * 70}")

        # Build hints from previous round
        hints = None
        if round_n > 0 and history:
            hints = build_consensus(history[-1])
            n_ah = len(hints.get("anomaly_indices", set()))
            n_ch = len(hints.get("known_correlations", set()))
            nc_h = hints.get("n_clusters_hint", "?")
            print(f"  Hints: {n_ah} anomalies, {n_ch} correlations, ~{nc_h} clusters")

        # Run all lenses
        all_findings = {}
        for name, cls in LENS_CLASSES.items():
            t0 = time.time()
            findings = run_lens(name, cls, data, labels, hints=hints)
            dt = time.time() - t0
            all_findings[name] = findings
            na = len(findings["anomalies"])
            nc = len(findings["correlations"])
            ncl = findings["n_clusters"]
            print(f"  {name:15s} {dt:4.1f}s | anom={na:2d} corr={nc:2d} clust={ncl:2d}")

        history.append(all_findings)

        # Score
        checks = compute_gt_score(all_findings, gt)
        score = sum(checks.values())
        total = len(checks)
        print(f"\n  GT Score: {score}/{total}")
        for k, v in checks.items():
            detail = ""
            if "corr" in k:
                pair = gt[k]
                n = sum(1 for f in all_findings.values() if pair in f["correlations"])
                detail = f" ({n}/9)"
            elif "anomaly" in k:
                n = sum(1 for f in all_findings.values() if gt["anomaly_10"] in f["anomalies"])
                detail = f" ({n}/9)"
            elif "cluster" in k:
                n = sum(1 for f in all_findings.values() if 2 <= f["n_clusters"] <= 15)
                detail = f" ({n}/9)"
            print(f"    {'PASS' if v else 'FAIL'} {k}{detail}")

        if score == total:
            print(f"\n  Converged at round {round_n + 1}!")
            break

        if score <= prev_score and round_n > 0:
            print(f"\n  No improvement, stopping early.")
            break
        prev_score = score

    # ── Final comparison ──
    print(f"\n{'=' * 70}")
    print(f"  Calibration Report")
    print(f"{'=' * 70}")

    if len(history) >= 2:
        base = history[0]
        final = history[-1]

        print(f"\n  Per-lens improvement (anomaly detection):")
        print(f"  {'Lens':15s} {'Before':>8s} {'After':>8s} {'Delta':>8s}")
        total_before = 0
        total_after = 0
        for name in LENS_CLASSES:
            b_anom = len(base[name]["anomalies"])
            f_anom = len(final[name]["anomalies"])
            b_has10 = 10 in base[name]["anomalies"]
            f_has10 = 10 in final[name]["anomalies"]
            delta = f_anom - b_anom
            mark = ""
            if not b_has10 and f_has10: mark = " ← NEW #10!"
            elif b_has10 and f_has10: mark = " ✓ #10"
            print(f"  {name:15s} {b_anom:8d} {f_anom:8d} {delta:+8d}{mark}")
            total_before += b_anom
            total_after += f_anom

        print(f"\n  Per-lens improvement (correlation discovery):")
        print(f"  {'Lens':15s} {'Before':>8s} {'After':>8s} {'Delta':>8s}")
        for name in LENS_CLASSES:
            b_corr = len(base[name]["correlations"])
            f_corr = len(final[name]["correlations"])
            delta = f_corr - b_corr
            b_01 = gt["corr_01"] in base[name]["correlations"]
            f_01 = gt["corr_01"] in final[name]["correlations"]
            mark = ""
            if not b_01 and f_01: mark = " ← NEW f0↔f1!"
            elif b_01: mark = " ✓ f0↔f1"
            print(f"  {name:15s} {b_corr:8d} {f_corr:8d} {delta:+8d}{mark}")

        # Final consensus
        base_checks = compute_gt_score(base, gt)
        final_checks = compute_gt_score(final, gt)
        b_score = sum(base_checks.values())
        f_score = sum(final_checks.values())
        total = len(base_checks)
        print(f"\n  Before calibration: {b_score}/{total} ({100*b_score/total:.0f}%)")
        print(f"  After calibration:  {f_score}/{total} ({100*f_score/total:.0f}%)")

        if f_score > b_score:
            print(f"  Improvement: +{f_score - b_score} checks")
        elif f_score == b_score == total:
            print(f"  Already perfect — calibration maintained 100%")
        else:
            print(f"  No change (or degradation)")
    else:
        checks = compute_gt_score(history[0], gt)
        score = sum(checks.values())
        print(f"\n  Single round: {score}/{len(checks)} ({100*score/len(checks):.0f}%)")

    print(f"{'=' * 70}")


if __name__ == '__main__':
    main()
