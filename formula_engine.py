```python
#!/usr/bin/env python3
"""Formula Generation Engine — Automatic Constant Relationship Discovery + Significance Testing

Usage:
  python3 formula_engine.py                    # Full search
  python3 formula_engine.py --target 137       # Search for formulas that create 137
  python3 formula_engine.py --depth 3          # Search with depth 3
  python3 formula_engine.py --significance     # Include significance testing
"""

import numpy as np
from itertools import combinations, product as iterproduct
import argparse
from scipy import stats
import os
from datetime import datetime

RESULTS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "results")


# ─────────────────────────────────────────
# Core constants of our model
# ─────────────────────────────────────────
CONSTANTS = {
    '1': 1.0,
    '2': 2.0,
    '3': 3.0,
    '6': 6.0,
    '8': 8.0,
    '17': 17.0,
    '1/2': 0.5,
    '1/3': 1/3,
    '1/6': 1/6,
    '5/6': 5/6,
    'e': np.e,
    '1/e': 1/np.e,
    'ln(4/3)': np.log(4/3),
    'π': np.pi,
}

# Physics constants (targets)
PHYSICS = {
    'α(fine structure)': 1/137.036,
    '1/α': 137.036,
    'αs(strong)': 0.118,
    'sin²θ_W': 0.231,
    'T_CMB': 2.72548,
    'Ω_Λ(dark energy)': 0.683,
    'Ω_b(ordinary matter)': 0.049,
    'Ω_DM(dark matter)': 0.268,
}

# Mathematical constants (targets)
MATH_TARGETS = {
    'π': np.pi,
    'π/2': np.pi/2,
    'π/4': np.pi/4,
    'π/6': np.pi/6,
    'φ(golden ratio)': (1+np.sqrt(5))/2,
    'ln(2)': np.log(2),
    'ln(3)': np.log(3),
    'sqrt(2)': np.sqrt(2),
    'sqrt(3)': np.sqrt(3),
    'γ(Euler-Mascheroni)': 0.5772156649,
}


# ─────────────────────────────────────────
# Operators
# ─────────────────────────────────────────
def safe_ops(a, b):
    """Return list of safe operations on two values"""
    results = []
    av, an = a
    bv, bn = b
    results.append((av + bv, f'({an}+{bn})'))
    results.append((av - bv, f'({an}-{bn})'))
    results.append((bv - av, f'({bn}-{an})'))
    results.append((av * bv, f'({an}×{bn})'))

    if bv != 0:
        results.append((av / bv, f'({an}/{bn})'))
    if av != 0:
        results.append((bv / av, f'({bn}/{an})'))

    if av > 0 and abs(bv) < 10:
        try:
            val = av ** bv
            if np.isfinite(val) and abs(val) < 1e10:
                results.append((val, f'({an}^{bn})'))
        except:
            pass

    return [(v, expr) for v, expr in results if isinstance(v, (int, float)) and np.isfinite(v) and abs(v) < 1e10]


def unary_ops(a):
    """Unary operations"""
    results = [(a[0], a[1])]
    if a[0] > 0:
        results.append((np.log(a[0]), f'ln({a[1]})'))
        results.append((np.sqrt(a[0]), f'√({a[1]})'))
    results.append((np.exp(a[0]), f'e^({a[1]})'))
    if a[0] != 0:
        results.append((1/a[0], f'1/({a[1]})'))
    return [(v, expr) for v, expr in results if np.isfinite(v) and abs(v) < 1e10]


# ─────────────────────────────────────────
# Formula Search Engine
# ─────────────────────────────────────────
def search_formulas(targets, max_depth=2, threshold=0.01):
    """Search for formulas that create target values using constant combinations"""

    # Level 1: Basic constants
    level_1 = [(v, k) for k, v in CONSTANTS.items()]

    # Expand with unary operations
    level_1_ext = []
    for val, name in level_1:
        level_1_ext.extend(unary_ops((val, name)))

    # Level 2: Binary operations
    level_2 = []
    if max_depth >= 2:
        for i, a in enumerate(level_1_ext):
            for j, b in enumerate(level_1_ext):
                if i <= j:
                    level_2.extend(safe_ops(a, b))

    all_formulas = level_1_ext + level_2

    # Target matching
    matches = []
    for t_name, t_val in targets.items():
        for val, expr in all_formulas:
            if t_val != 0:
                rel_err = abs(val - t_val) / abs(t_val)
            else:
                rel_err = abs(val - t_val)

            if rel_err < threshold:
                matches.append({
                    'target': t_name,
                    'target_val': t_val,
                    'formula': expr,
                    'formula_val': val,
                    'error': rel_err,
                    'error_pct': rel_err * 100,
                })

    # Sort by error
    matches.sort(key=lambda x: (x['target'], x['error']))

    return matches


def significance_test(matches, n_random=10000):
    """Texas Sharpshooter Test: Do we get the same matches with random constants?"""

    n_real_matches = len(matches)
    n_targets = len(set(m['target'] for m in matches))

    # Repeat same search with random constants
    random_match_counts = []

    for trial in range(n_random):
        # Random constants (same count, same range)
        rng = np.random.default_rng(trial)
        rand_constants = {}
        for k in CONSTANTS:
            rand_constants[k] = rng.uniform(0.01, 20)

        rand_level_1 = [(v, k) for k, v in rand_constants.items()]
        rand_level_2 = []
        for i, a in enumerate(rand_level_1):
            for j, b in enumerate(rand_level_1):
                if i <= j:
                    rand_level_2.extend(safe_ops(a, b))

        all_rand = rand_level_1 + rand_level_2

        # Count matches for same targets
        targets = {m['target']: m['target_val'] for m in matches}
        rand_matches = 0
        for t_name, t_val in targets.items():
            for val, expr in all_rand:
                if t_val != 0 and abs(val - t_val) / abs(t_val) < 0.01:
                    rand_matches += 1
                    break  # Only 1 per target

        random_match_counts.append(rand_matches)

    random_match_counts = np.array(random_match_counts)
    p_value = (random_match_counts >= n_targets).mean()

    return {
        'real_matches': n_real_matches,
        'real_targets_hit': n_targets,
        'random_mean': random_match_counts.mean(),
        'random_std': random_match_counts.std(),
        'p_value': p_value,
        'z_score': (n_targets - random_match_counts.mean()) / max(random_match_counts.std(), 0.01),
    }


# ─────────────────────────────────────────
# Main
# ─────────────────────────────────────────
def main():
    parser = argparse.ArgumentParser(description="Formula Generation Engine")
    parser.add_argument('--target', type=float, default=None, help="Search for formulas creating specific value")
    parser.add_argument('--depth', type=int, default=2, help="Search depth (default 2)")
    parser.add_argument('--threshold', type=float, default=0.01, help="Error threshold (default 0.01)")
    parser.add_argument('--significance', action='store_true', help="Texas Sharpshooter test")
    parser.add_argument('--physics', action='store_true', help="Physics constant targets")
    parser.add_argument('--math', action='store_true', help="Mathematical constant targets")
    parser.add_argument('--all', action='store_true', help="Full search")
    args = parser.parse_args()

    print()
    print("═" * 60)
    print("   🔬 Formula Generation Engine v1.0")
    print("═" * 60)

    # Determine targets
    if args.target:
        targets = {f'target={args.target}': args.target}
    elif args.physics:
        targets = PHYSICS
    elif args.math:
        targets = MATH_TARGETS
    elif args.all:
        targets = {**PHYSICS, **MATH_TARGETS}
    else:
        targets = {**PHYSICS, **MATH_TARGETS}

    print(f"  Constants: {len(CONSTANTS)}")
    print(f"  Targets: {len(targets)}")
    print(f"  Depth: {args.depth}")
    print(f"  Threshold: {args.threshold*100}%")
    print("─" * 60)

    # Search
    matches = search_formulas(targets, max_depth=args.depth, threshold=args.threshold)

    # Output results
    print(f"\n  Formulas found: {len(matches)}")
    print()

    current_target = None
    for m in matches:
        if m['target'] != current_target:
            current_target = m['target']
            print(f"  ═══ {m['target']} = {m['target_val']:.6f} ═══")

        star = "★" if m['error_pct'] < 0.1 else ("●" if m['error_pct'] < 0.5 else "·")
        print(f"    {star} {m['formula']:30} = {m['formula_val']:.6f} (error {m['error_pct']:.3f}%)")

    # Significance test
    if args.significance and matches:
        print(f"\n{'═' * 60}")
        print(f"  Texas Sharpshooter Test")
        print(f"{'═' * 60}")

        sig = significance_test(matches, n_random=1000)

        print(f"  Real matched targets: {sig['real_targets_hit']}")
        print(f"  Random average:       {sig['random_mean']:.1f} ± {sig['random_std']:.1f}")
        print(f"  Z-score:              {sig['z_score']:.2f}")
        print(f"  p-value:              {sig['p_value']:.4f}")
        print()

        if sig['p_value'] < 0.01:
            print(f"  Result: ✅ Significant (p < 0.01) — {(1-sig['p_value'])*100:.1f}% chance not by coincidence")
        elif sig['p_value'] < 0.05:
            print(f"  Result: ⚠️ Weakly significant (p < 0.05)")
        else:
            print(f"  Result: ❌ Not significant (p = {sig['p_value']:.2f}) — Possible Texas Sharpshooter")

    # Save
    os.makedirs(RESULTS_DIR, exist_ok=True)
    with open(os.path.join(RESULTS_DIR, "formula_discovery.md"), 'a', encoding='utf-8') as f:
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        f.write(f"\n# Formula Search [{now}]\n\n")
        f.write(f"Constants {len(CONSTANTS)}, Targets {len(targets)}, Discoveries {len(matches)}\n\n")
        for m in matches[:20]:
            f.write(f"- {m['target']}: {m['formula']} = {m['formula_val']:.6f} (error {m['error_pct']:.3f}%)\n")
        f.write("\n---\n")

    print(f"\n  📁 Results → results/formula_discovery.md")
    print()


if __name__ == '__main__':
    main()
```