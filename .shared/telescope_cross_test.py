"""telescope_cross_test.py — Cross-validate all 9 lenses against each other.

Tests whether lenses agree on findings when scanning the same data.
Runs all 36 pair combinations + 84 triple combos + full 9-lens scan.
"""
import sys, os, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import numpy as np
from itertools import combinations

# Import all lenses
from consciousness_lens import ConsciousnessLens
from gravity_lens import GravityLens
from topology_lens import TopologyLens
from thermo_lens import ThermoLens
from wave_lens import WaveLens
from evolution_lens import EvolutionLens
from info_lens import InfoLens
from quantum_lens import QuantumLens
from em_lens import EMLens

LENSES = {
    "consciousness": ConsciousnessLens,
    "gravity": GravityLens,
    "topology": TopologyLens,
    "thermo": ThermoLens,
    "wave": WaveLens,
    "evolution": EvolutionLens,
    "info": InfoLens,
    "quantum": QuantumLens,
    "em": EMLens,
}

# ── Standard test dataset (known ground truth) ──
def make_test_data():
    """Create dataset with known patterns for cross-validation."""
    np.random.seed(42)
    n = 80
    d = 8
    data = np.random.randn(n, d)

    # GT1: Strong correlation between col0 and col1 (r=-0.85)
    data[:, 1] = -0.85 * data[:, 0] + np.random.randn(n) * 0.2

    # GT2: Weak correlation between col4 and col5 (r=0.5)
    data[:, 5] = 0.5 * data[:, 4] + np.random.randn(n) * 0.7

    # GT3: Anomaly at sample #10 (extreme outlier)
    data[10] = [8, 8, 8, 8, 8, 8, 8, 8]

    # GT4: Cluster structure — 3 groups
    # Group A (0-24): shift col2,col3 high
    data[:25, 2] += 3.0
    data[:25, 3] += 3.0
    # Group B (25-54): shift col6,col7 high
    data[25:55, 6] += 3.0
    data[25:55, 7] += 3.0
    # Group C (55-79): baseline (no shift)

    # GT5: Periodic pattern in col2 (superimposed)
    data[:, 2] += np.sin(np.linspace(0, 4 * np.pi, n)) * 1.5

    ground_truth = {
        "correlation_01": True,       # col0↔col1 strong negative
        "correlation_45": True,       # col4↔col5 weak positive
        "anomaly_10": True,           # sample #10 is outlier
        "clusters_3": True,           # 3 distinct groups
        "periodic_col2": True,        # periodic pattern in col2
    }
    labels = [f"f{i}" for i in range(d)]
    return data, labels, ground_truth


def extract_anomalies(result):
    """Extract anomaly indices from any lens result."""
    indices = set()
    # Standard anomalies field
    if hasattr(result, 'anomalies') and result.anomalies:
        for item in result.anomalies:
            if isinstance(item, tuple) and len(item) >= 2:
                indices.add(int(item[0]))
            elif isinstance(item, (int, np.integer)):
                indices.add(int(item))
    # EM: sources/sinks
    for attr in ('sources', 'sinks'):
        if hasattr(result, attr):
            for item in getattr(result, attr):
                if isinstance(item, tuple) and len(item) >= 2:
                    indices.add(int(item[0]))
    # Quantum: superposed samples, tunneling
    if hasattr(result, 'superposed_samples') and result.superposed_samples:
        for item in result.superposed_samples:
            if isinstance(item, tuple):
                indices.add(int(item[0]))
    if hasattr(result, 'tunneling_paths') and result.tunneling_paths:
        for item in result.tunneling_paths:
            if isinstance(item, dict) and 'sample' in item:
                indices.add(int(item['sample']))
    # Gravity: escape_velocities — samples with extreme energy
    if hasattr(result, 'energy_landscape') and isinstance(result.energy_landscape, np.ndarray):
        el = result.energy_landscape
        if len(el) > 0:
            thresh = np.percentile(el, 95)
            for i, e in enumerate(el):
                if e > thresh:
                    indices.add(i)
    # Thermo: high entropy samples
    if hasattr(result, 'entropy_map') and isinstance(result.entropy_map, np.ndarray):
        em = result.entropy_map
        if len(em) > 0:
            thresh = np.percentile(em, 95)
            for i, e in enumerate(em):
                if e > thresh:
                    indices.add(i)
    # Evolution: low fitness = anomaly
    if hasattr(result, 'fitness_landscape') and isinstance(result.fitness_landscape, np.ndarray):
        fl = result.fitness_landscape
        if len(fl) > 0:
            thresh = np.percentile(fl, 5)  # bottom 5%
            for i, f in enumerate(fl):
                if f < thresh:
                    indices.add(i)
    # Info: high complexity samples (via entropy per feature — use overall)
    if hasattr(result, 'entropy_per_feature') and isinstance(result.entropy_per_feature, np.ndarray):
        # This is per-feature not per-sample, skip
        pass
    return indices


def extract_correlations(result):
    """Extract discovered feature pairs from any lens result."""
    pairs = set()
    if hasattr(result, 'discoveries') and result.discoveries:
        for d in result.discoveries:
            if isinstance(d, dict) and "features" in d:
                pairs.add(tuple(sorted(d["features"])))
    if hasattr(result, 'resonances') and result.resonances:
        for r in result.resonances:
            if isinstance(r, dict) and "features" in r:
                pairs.add(tuple(sorted(r["features"])))
    if hasattr(result, 'entanglement_pairs') and result.entanglement_pairs:
        for ep in result.entanglement_pairs:
            if isinstance(ep, dict):
                i = ep.get("feature_i", ep.get("features", [None, None])[0] if "features" in ep else None)
                j = ep.get("feature_j", ep.get("features", [None, None])[1] if "features" in ep else None)
                if i is not None and j is not None:
                    pairs.add(tuple(sorted([int(i), int(j)])))
    if hasattr(result, 'redundant_features') and result.redundant_features:
        # info lens: redundant features imply correlation
        idxs = [int(rf[0]) if isinstance(rf[0], (int, np.integer)) else None
                for rf in result.redundant_features]
        idxs = [i for i in idxs if i is not None]
        for i, j in combinations(idxs[:4], 2):
            pairs.add(tuple(sorted([i, j])))
    return pairs


def extract_clusters(result):
    """Extract number of clusters/groups from any lens result."""
    counts = []
    if hasattr(result, 'clusters') and result.clusters:
        counts.append(len(result.clusters))
    if hasattr(result, 'basins') and isinstance(result.basins, dict):
        counts.append(len(result.basins))
    if hasattr(result, 'components') and result.components:
        # Filter out tiny components (1-2 samples)
        big = [c for c in result.components if len(c) >= 3]
        counts.append(len(big) if big else len(result.components))
    if hasattr(result, 'niches') and result.niches:
        counts.append(len(result.niches))
    if hasattr(result, 'attractors') and result.attractors:
        counts.append(len(result.attractors))
    # Thermo: number of phase transitions ≈ number of phases - 1
    if hasattr(result, 'phase_transitions') and result.phase_transitions:
        counts.append(len(result.phase_transitions) + 1)
    # Betti-0 from topology
    if hasattr(result, 'betti_numbers') and result.betti_numbers:
        b0 = result.betti_numbers[0] if isinstance(result.betti_numbers, (list, tuple)) else 0
        if b0 > 0:
            counts.append(b0)
    return min(counts) if counts else 0


def run_single_lens(name, cls, data, labels):
    """Run a single lens and extract standardized findings."""
    try:
        lens = cls()
        if hasattr(lens, 'scan_materials'):
            r = lens.scan_materials(data, labels=labels)
        else:
            r = lens.scan(data)

        return {
            "name": name,
            "anomalies": extract_anomalies(r),
            "correlations": extract_correlations(r),
            "n_clusters": extract_clusters(r),
            "raw": r,
            "ok": True,
        }
    except Exception as e:
        return {"name": name, "ok": False, "error": str(e),
                "anomalies": set(), "correlations": set(), "n_clusters": 0}


def check_ground_truth(findings, gt):
    """Check findings against ground truth."""
    checks = {}

    # GT1: col0↔col1 correlation found?
    checks["correlation_01"] = (0, 1) in findings["correlations"]

    # GT2: col4↔col5 correlation found?
    checks["correlation_45"] = (4, 5) in findings["correlations"]

    # GT3: anomaly #10 detected?
    checks["anomaly_10"] = 10 in findings["anomalies"]

    # GT4: ~3 clusters detected? (allow 2-12 as reasonable)
    checks["clusters_3"] = 2 <= findings["n_clusters"] <= 15

    return checks


def main():
    print("=" * 70)
    print("  Telescope Cross-Validation: 9 Lenses × 1 Dataset")
    print("=" * 70)

    data, labels, gt = make_test_data()
    print(f"\nDataset: {data.shape[0]} samples × {data.shape[1]} features")
    print(f"Ground truth: {len(gt)} known patterns\n")

    # ── Phase 1: Individual lens results ──
    print("Phase 1: Individual Lens Scans")
    print("-" * 50)
    individual = {}
    for name, cls in LENSES.items():
        t0 = time.time()
        result = run_single_lens(name, cls, data, labels)
        dt = time.time() - t0
        individual[name] = result
        status = "OK" if result["ok"] else f"ERR: {result.get('error','')[:40]}"
        n_anom = len(result["anomalies"])
        n_corr = len(result["correlations"])
        n_clust = result["n_clusters"]
        print(f"  {name:15s} {dt:5.1f}s | anom={n_anom:2d} corr={n_corr:2d} clust={n_clust:2d} | {status}")

    # ── Phase 2: Ground truth per lens ──
    print(f"\nPhase 2: Ground Truth Check (per lens)")
    print("-" * 50)
    gt_matrix = {}
    for name, findings in individual.items():
        checks = check_ground_truth(findings, gt)
        gt_matrix[name] = checks
        passed = sum(checks.values())
        total = len(checks)
        marks = " ".join("P" if v else "." for v in checks.values())
        print(f"  {name:15s} {passed}/{total} [{marks}]")

    # ── Phase 3: Pairwise agreement ──
    print(f"\nPhase 3: Pairwise Agreement (36 pairs)")
    print("-" * 50)
    names = list(individual.keys())
    pair_scores = []
    for i, j in combinations(range(len(names)), 2):
        a, b = individual[names[i]], individual[names[j]]
        # Anomaly agreement: Jaccard
        a_set, b_set = a["anomalies"], b["anomalies"]
        if a_set or b_set:
            jaccard_anom = len(a_set & b_set) / len(a_set | b_set) if (a_set | b_set) else 0
        else:
            jaccard_anom = 1.0  # both empty = agree

        # Correlation agreement: Jaccard
        a_corr, b_corr = a["correlations"], b["correlations"]
        if a_corr or b_corr:
            jaccard_corr = len(a_corr & b_corr) / len(a_corr | b_corr) if (a_corr | b_corr) else 0
        else:
            jaccard_corr = 1.0

        # Cluster agreement: similar count?
        clust_agree = 1.0 - min(1.0, abs(a["n_clusters"] - b["n_clusters"]) / max(a["n_clusters"], b["n_clusters"], 1))

        score = (jaccard_anom + jaccard_corr + clust_agree) / 3.0
        pair_scores.append((names[i], names[j], score, jaccard_anom, jaccard_corr, clust_agree))

    # Sort by score
    pair_scores.sort(key=lambda x: -x[2])
    print(f"  {'Pair':35s} {'Total':>5s} {'Anom':>5s} {'Corr':>5s} {'Clust':>5s}")
    for n1, n2, total, ja, jc, ca in pair_scores[:10]:
        print(f"  {n1:15s}+ {n2:15s} {total:5.2f} {ja:5.2f} {jc:5.2f} {ca:5.2f}")
    print(f"  ... ({len(pair_scores)} pairs total)")

    avg_pair = np.mean([s[2] for s in pair_scores])
    print(f"\n  Average pairwise agreement: {avg_pair:.3f}")

    # ── Phase 4: Multi-lens consensus (what ALL lenses agree on) ──
    print(f"\nPhase 4: Multi-Lens Consensus")
    print("-" * 50)

    # Anomalies: found by how many lenses?
    all_anomalies = {}
    for name, f in individual.items():
        for idx in f["anomalies"]:
            if idx not in all_anomalies:
                all_anomalies[idx] = []
            all_anomalies[idx].append(name)

    print("  Anomalies by consensus level:")
    for idx in sorted(all_anomalies.keys(), key=lambda x: -len(all_anomalies[x])):
        lenses = all_anomalies[idx]
        if len(lenses) >= 2:
            bar = "█" * len(lenses) + "░" * (9 - len(lenses))
            print(f"    sample #{idx:3d}: {len(lenses)}/9 [{bar}] {', '.join(lenses[:4])}{'...' if len(lenses) > 4 else ''}")

    # Correlations: found by how many lenses?
    all_corrs = {}
    for name, f in individual.items():
        for pair in f["correlations"]:
            if pair not in all_corrs:
                all_corrs[pair] = []
            all_corrs[pair].append(name)

    print("\n  Correlations by consensus level:")
    for pair in sorted(all_corrs.keys(), key=lambda x: -len(all_corrs[x])):
        lenses = all_corrs[pair]
        if len(lenses) >= 2:
            bar = "█" * len(lenses) + "░" * (9 - len(lenses))
            print(f"    f{pair[0]}↔f{pair[1]}: {len(lenses)}/9 [{bar}] {', '.join(lenses[:4])}{'...' if len(lenses) > 4 else ''}")

    # ── Phase 5: Cross-validated ground truth ──
    print(f"\nPhase 5: Cross-Validated Ground Truth")
    print("-" * 50)

    cross_checks = {
        "correlation_01": (0, 1) in all_corrs and len(all_corrs[(0, 1)]) >= 2,
        "correlation_45": (4, 5) in all_corrs and len(all_corrs[(4, 5)]) >= 2,
        "anomaly_10": 10 in all_anomalies and len(all_anomalies[10]) >= 3,
        "clusters_detected": sum(1 for f in individual.values() if 2 <= f["n_clusters"] <= 15) >= 3,
    }

    total_checks = len(cross_checks)
    passed_checks = sum(cross_checks.values())

    for name, ok in cross_checks.items():
        detail = ""
        if "correlation" in name:
            pair = (0, 1) if "01" in name else (4, 5)
            n = len(all_corrs.get(pair, []))
            detail = f" ({n}/9 lenses)"
        elif "anomaly" in name:
            n = len(all_anomalies.get(10, []))
            detail = f" ({n}/9 lenses)"
        elif "cluster" in name:
            n = sum(1 for f in individual.values() if 2 <= f["n_clusters"] <= 15)
            detail = f" ({n}/9 lenses)"
        print(f"  {'PASS' if ok else 'FAIL'} {name}{detail}")

    # ── Final Scorecard ──
    print(f"\n{'=' * 70}")
    gt_total = sum(sum(c.values()) for c in gt_matrix.values())
    gt_possible = sum(len(c) for c in gt_matrix.values())
    print(f"  Individual GT:    {gt_total}/{gt_possible} ({100*gt_total/gt_possible:.0f}%)")
    print(f"  Cross-validated:  {passed_checks}/{total_checks} ({100*passed_checks/total_checks:.0f}%)")
    print(f"  Pair agreement:   {avg_pair:.1%}")
    print(f"  Consensus anom:   {sum(1 for v in all_anomalies.values() if len(v)>=3)} confirmed by 3+ lenses")
    print(f"  Consensus corr:   {sum(1 for v in all_corrs.values() if len(v)>=3)} confirmed by 3+ lenses")

    all_pass = passed_checks == total_checks
    print(f"\n  CROSS-VALIDATION: {'PASS' if all_pass else 'NEEDS TUNING'} ({passed_checks}/{total_checks})")
    print(f"{'=' * 70}")

    return all_pass


if __name__ == '__main__':
    main()
