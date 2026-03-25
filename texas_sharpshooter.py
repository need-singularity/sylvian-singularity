#!/usr/bin/env python3
"""Texas Sharpshooter Validator — Distinguishing Chance vs Structure

Verify if our discoveries are "shoot first, draw target later".
Calculate p-value by measuring frequency of same matching with random constants.

Usage:
  python3 texas_sharpshooter.py              # Full verification
  python3 texas_sharpshooter.py --trials 10000  # More trials
"""

import numpy as np
from scipy import stats
import argparse

# Our discovered "matchings"
CLAIMS = [
    {'name': 'CMB ≈ e',           'our_val': np.e,    'target': 2.72548, 'tolerance': 0.003},
    {'name': 'Dark energy ≈ 2/3',    'our_val': 2/3,    'target': 0.683,   'tolerance': 0.02},
    {'name': 'Ordinary matter ≈ 1/e³',     'our_val': 1/np.e**3,'target': 0.049, 'tolerance': 0.01},
    {'name': 'αs ≈ ln(9/8)',       'our_val': np.log(9/8),'target': 0.118,'tolerance': 0.005},
    {'name': '1/α ≈ 8×17+1',      'our_val': 137,    'target': 137.036, 'tolerance': 0.01},
    {'name': 'Compass ≈ 5/6',     'our_val': 5/6,    'target': 0.836,   'tolerance': 0.01},
    {'name': 'Golden zone upper limit ≈ 1/2',   'our_val': 0.5,    'target': 0.4991,  'tolerance': 0.002},
    {'name': 'Entropy ≈ ln(3)',    'our_val': np.log(3),'target': 1.089, 'tolerance': 0.01},
    {'name': 'Golden zone width ≈ ln(4/3)', 'our_val': np.log(4/3),'target': 0.287,'tolerance': 0.005},
    {'name': 'λ_conversation ≈ π/10',     'our_val': np.pi/10,'target': 0.3141, 'tolerance': 0.001},
]


def run_test(n_trials=5000):
    print("═" * 60)
    print("   🎯 Texas Sharpshooter Validator")
    print("═" * 60)

    n_claims = len(CLAIMS)
    n_constants = 14  # Number of our constants

    # Actual matching count
    real_hits = sum(1 for c in CLAIMS
                    if abs(c['our_val'] - c['target']) / max(abs(c['target']), 1e-10) < c['tolerance'])

    print(f"\n  Actual matches: {real_hits}/{n_claims}")

    # Random simulation
    print(f"  Random trials: {n_trials} times")
    print(f"  Simulating...", end=" ")

    random_hits = []
    rng = np.random.default_rng(42)

    for trial in range(n_trials):
        # 14 random constants (same count, similar range)
        rand_vals = []
        for _ in range(n_constants):
            # Generate from various ranges
            scale = rng.choice([0.01, 0.1, 1, 10, 100])
            rand_vals.append(rng.uniform(0.001, 1) * scale)

        # Try to match CLAIMS targets with these random constants
        hits = 0
        for c in CLAIMS:
            target = c['target']
            tol = c['tolerance']

            # Random constant itself
            for rv in rand_vals:
                if abs(rv - target) / max(abs(target), 1e-10) < tol:
                    hits += 1
                    break
            else:
                # Combination of 2 random constants (+, -, ×, /)
                matched = False
                for i in range(min(len(rand_vals), 8)):
                    for j in range(i+1, min(len(rand_vals), 8)):
                        a, b = rand_vals[i], rand_vals[j]
                        for val in [a+b, a-b, b-a, a*b]:
                            if abs(val - target) / max(abs(target), 1e-10) < tol:
                                hits += 1
                                matched = True
                                break
                        if matched:
                            break
                        if b != 0:
                            if abs(a/b - target) / max(abs(target), 1e-10) < tol:
                                hits += 1
                                matched = True
                                break
                    if matched:
                        break

        random_hits.append(hits)

    random_hits = np.array(random_hits)
    print("Complete")

    # Statistics
    p_value = (random_hits >= real_hits).mean()
    z_score = (real_hits - random_hits.mean()) / max(random_hits.std(), 0.01)

    print(f"\n{'─' * 60}")
    print(f"  Results")
    print(f"{'─' * 60}")
    print(f"  Actual matches:    {real_hits}/{n_claims}")
    print(f"  Random average:    {random_hits.mean():.1f} ± {random_hits.std():.1f}")
    print(f"  Random maximum:    {random_hits.max()}")
    print(f"  Z-score:      {z_score:.2f}")
    print(f"  p-value:      {p_value:.4f}")

    # Histogram
    print(f"\n  Random match count distribution:")
    hist, edges = np.histogram(random_hits, bins=range(int(random_hits.max())+2))
    for i, h in enumerate(hist):
        bar = "█" * int(h / max(hist.max(), 1) * 30)
        marker = " ← Actual!" if i == real_hits else ""
        print(f"    {i:>2} │{bar} {h}{marker}")

    # Judgment
    print(f"\n{'─' * 60}")
    if p_value < 0.001:
        print(f"  🟢 Judgment: Highly significant (p < 0.001)")
        print(f"     Probability our discovery is chance < 0.1%")
        print(f"     → High possibility of structural discovery")
    elif p_value < 0.01:
        print(f"  🟢 Judgment: Significant (p < 0.01)")
        print(f"     Probability of chance < 1%")
    elif p_value < 0.05:
        print(f"  🟡 Judgment: Weakly significant (p < 0.05)")
        print(f"     Cannot exclude chance possibility")
    else:
        print(f"  🔴 Judgment: Not significant (p = {p_value:.2f})")
        print(f"     Possible Texas sharpshooter!")

    # Individual match verification
    print(f"\n{'─' * 60}")
    print(f"  Individual match significance:")
    for c in CLAIMS:
        err = abs(c['our_val'] - c['target']) / max(abs(c['target']), 1e-10)
        hit = err < c['tolerance']
        print(f"    {'✅' if hit else '❌'} {c['name']:20} error={err*100:.3f}% (threshold={c['tolerance']*100}%)")

    print(f"\n{'═' * 60}")


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--trials', type=int, default=5000)
    args = parser.parse_args()
    run_test(args.trials)