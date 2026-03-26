I'll translate all Korean text to English in this Python file:

```python
#!/usr/bin/env python3
"""DFS Automatic Search Engine — Automates ralph-loop manual iteration

Instead of manually trying constant combinations, systematically explore all combinations with DFS.
Automatically detects cross-island bridges.

Usage:
  python3 dfs_engine.py                          # default depth=2, threshold=0.001
  python3 dfs_engine.py --depth 3                # 3-level recursive combination
  python3 dfs_engine.py --threshold 0.0001       # Within 0.01% error only
  python3 dfs_engine.py --depth 2 --threshold 0.001
"""

import numpy as np
from itertools import combinations
import argparse
import os
import json
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

# ─────────────────────────────────────────
# Configuration: Constants (color classification + island designation)
# ─────────────────────────────────────────

# Island classification:
#   A = Rational numbers (Golden Zone fractions)    greens
#   B = Integers/Fine structure          stars
#   C = Log/Entropy          blues
#   D = Transcendental (e, pi)          transcendental

ISLANDS = {
    'A': {  # greens — Rational/fractions
        '1/2':   0.5,
        '1/3':   1/3,
        '1/6':   1/6,
        '5/6':   5/6,
        '2/3':   2/3,
    },
    'B': {  # stars — Integer/structural constants
        'I*':    0.212073,          # Golden Zone lower bound
        'sigma': 12.0,             # sigma(6)
        'tau':   4.0,              # tau(6)
        'eH':    2**(2/3) * 3**(1/2),  # Hardy-Ramanujan constant
        '17':    17.0,             # Fermat prime
        '137':   137.0,            # Fine structure constant
        '8':     8.0,              # SU(3)
        '6':     6.0,              # Perfect number
    },
    'C': {  # blues — Log/Entropy
        'ln(4/3)':  np.log(4/3),   # Entropy jump
        'ln2':      np.log(2),
        'ln3':      np.log(3),
        'ln17':     np.log(17),
        'ln137':    np.log(137),
    },
    'D': {  # transcendental — Transcendental numbers
        'e':     np.e,
        '1/e':   1/np.e,
        'pi':    np.pi,
        'phi':   (1 + np.sqrt(5)) / 2,
    },
}

# Target constants: considered discoveries when matched
TARGETS = {}

# Mathematical constants
_math = {
    'pi':         np.pi,
    'pi/2':       np.pi / 2,
    'pi/4':       np.pi / 4,
    'pi/6':       np.pi / 6,
    'pi^2/6':     np.pi**2 / 6,
    'e':          np.e,
    '1/e':        1 / np.e,
    'e^2':        np.e**2,
    'phi':        (1 + np.sqrt(5)) / 2,
    'sqrt(2)':    np.sqrt(2),
    'sqrt(3)':    np.sqrt(3),
    'sqrt(5)':    np.sqrt(5),
    'ln2':        np.log(2),
    'ln3':        np.log(3),
    'ln10':       np.log(10),
    'gamma_EM':   0.5772156649,     # Euler-Mascheroni
    'zeta(3)':    1.2020569031,     # Apery
    'Catalan_G':  0.9159655941,     # Catalan
    'Khinchin':   2.6854520011,     # Khinchin
}

# Integers (1~20)
for i in range(1, 21):
    _math[str(i)] = float(i)

# Simple fractions
for a in range(1, 13):
    for b in range(a + 1, 13):
        key = f'{a}/{b}'
        if key not in _math:
            _math[key] = a / b

# Physical constants
_phys = {
    '1/alpha':    137.036,
    'alpha':      1/137.036,
    'alpha_s':    0.118,
    'sin2_thetaW': 0.231,
    'T_CMB':      2.72548,
    'Omega_DE':   0.683,
    'Omega_DM':   0.268,
    'Omega_b':    0.049,
}

TARGETS.update(_math)
TARGETS.update(_phys)


# ─────────────────────────────────────────
# Operators
# ─────────────────────────────────────────

def binary_ops(a_val, a_name, b_val, b_name):
    """Returns list of binary operation results for two values: (value, expression, set_of_islands)"""
    results = []

    def _add(v, expr):
        if isinstance(v, (int, float)) and np.isfinite(v) and abs(v) < 1e12:
            results.append((v, expr))

    _add(a_val + b_val, f'({a_name}+{b_name})')
    _add(a_val - b_val, f'({a_name}-{b_name})')
    _add(b_val - a_val, f'({b_name}-{a_name})')
    _add(a_val * b_val, f'({a_name}*{b_name})')

    if b_val != 0:
        _add(a_val / b_val, f'({a_name}/{b_name})')
    if a_val != 0:
        _add(b_val / a_val, f'({b_name}/{a_name})')

    # Powers
    if a_val > 0 and abs(b_val) < 20:
        try:
            v = a_val ** b_val
            _add(v, f'({a_name}^{b_name})')
        except (OverflowError, ValueError):
            pass
    if b_val > 0 and abs(a_val) < 20:
        try:
            v = b_val ** a_val
            _add(v, f'({b_name}^{a_name})')
        except (OverflowError, ValueError):
            pass

    # log_a(b)
    if a_val > 0 and a_val != 1 and b_val > 0:
        _add(np.log(b_val) / np.log(a_val), f'log_{a_name}({b_name})')
    if b_val > 0 and b_val != 1 and a_val > 0:
        _add(np.log(a_val) / np.log(b_val), f'log_{b_name}({a_name})')

    return results


def unary_ops(val, name):
    """Unary operation expansion"""
    results = [(val, name)]
    if val > 0:
        results.append((np.log(val), f'ln({name})'))
        results.append((np.sqrt(val), f'sqrt({name})'))
    results.append((np.exp(val) if val < 500 else None, f'exp({name})'))
    if val != 0:
        results.append((1.0 / val, f'1/{name}'))
    results.append((abs(val), f'|{name}|'))
    # filter
    return [(v, n) for v, n in results
            if v is not None and isinstance(v, (int, float))
            and np.isfinite(v) and abs(v) < 1e12]


# ─────────────────────────────────────────
# Island tracking (which island's constants were used)
# ─────────────────────────────────────────

def get_island(const_name):
    """Returns the island that a constant belongs to by its name"""
    for island_id, consts in ISLANDS.items():
        if const_name in consts:
            return island_id
    return '?'


def extract_base_constants(expr):
    """Extract base constant names used in the expression string"""
    all_names = set()
    for island_consts in ISLANDS.values():
        for name in island_consts:
            if name in expr:
                all_names.add(name)
    return all_names


def get_islands_from_expr(expr):
    """Returns set of islands used in the expression"""
    islands = set()
    for name in extract_base_constants(expr):
        islands.add(get_island(name))
    return islands


# ─────────────────────────────────────────
# DFS Engine Core
# ─────────────────────────────────────────

def build_level(depth_limit):
    """Recursively generate constant combinations up to depth limit

    Returns: list of (value, expression_string, set_of_islands)
    """
    # Level 0: All base constants + unary operations
    base = []
    for island_id, consts in ISLANDS.items():
        for name, val in consts.items():
            for uv, un in unary_ops(val, name):
                base.append((uv, un, {island_id}))

    if depth_limit < 1:
        return base

    current = list(base)

    for depth in range(1, depth_limit + 1):
        next_level = []
        n = len(current)

        # All pair combinations from previous level
        # depth 1: base x base
        # depth 2: (base+level1) x base  (new only)
        if depth == 1:
            pool_a = base
            pool_b = base
        else:
            pool_a = current  # entire previous
            pool_b = base     # base only (explosion prevention)

        seen_vals = set()
        for i, (av, an, ai) in enumerate(pool_a):
            for j, (bv, bn, bi) in enumerate(pool_b):
                if depth == 1 and j > i:
                    continue  # avoid duplicates
                combined_islands = ai | bi

                for rv, rn in binary_ops(av, an, bv, bn):
                    # Value duplicate filter (6 decimal places)
                    key = round(rv, 8)
                    if key in seen_vals:
                        continue
                    seen_vals.add(key)
                    next_level.append((rv, rn, combined_islands))

        current = current + next_level
        print(f"  [depth {depth}] {len(next_level):,} new expressions "
              f"(total: {len(current):,})")

    return current


def is_trivial(expr, target_name, val, target_val):
    """Determine if matching is trivial (already known identities etc.)"""
    # If expression is the target name itself
    clean_expr = expr.replace('(', '').replace(')', '')
    if clean_expr == target_name:
        return True

    # Simple constant identical to target
    for consts in ISLANDS.values():
        if target_name in consts and clean_expr in consts:
            if abs(val - target_val) < 1e-12:
                return True

    # Expression too simple (single constant)
    base = extract_base_constants(expr)
    if len(base) <= 1 and abs(val - target_val) < 1e-12:
        return True

    return False


def check_targets(expressions, threshold=0.001):
    """Compare all expressions with targets, return matches"""
    matches = []

    for val, expr, islands in expressions:
        if val == 0:
            continue
        for t_name, t_val in TARGETS.items():
            if t_val == 0:
                continue
            rel_err = abs(val - t_val) / abs(t_val)
            if rel_err < threshold:
                if is_trivial(expr, t_name, val, t_val):
                    continue
                n_islands = len(islands)
                # Significance score: more island connections + smaller error = higher score
                significance = n_islands * 10 + max(0, -np.log10(rel_err + 1e-15))
                if rel_err < 1e-12:
                    significance += 50  # exact match bonus

                island_str = '+'.join(sorted(islands))
                matches.append({
                    'target': t_name,
                    'target_val': t_val,
                    'formula': expr,
                    'formula_val': val,
                    'error': rel_err,
                    'error_pct': rel_err * 100,
                    'islands': island_str,
                    'n_islands': n_islands,
                    'significance': significance,
                    'is_exact': rel_err < 1e-12,
                })

    return matches


def filter_best(matches, top_per_target=5):
    """Keep only best matches per target"""
    by_target = {}
    for m in matches:
        key = m['target']
        if key not in by_target:
            by_target[key] = []
        by_target[key].append(m)

    filtered = []
    for key, group in by_target.items():
        group.sort(key=lambda x: (-x['n_islands'], x['error']))
        filtered.extend(group[:top_per_target])

    return filtered


def find_cross_island(matches):
    """Extract only cross-island connections"""
    return [m for m in matches if m['n_islands'] >= 2]


# ─────────────────────────────────────────
# Verification Pipeline (automatically executed upon discovery)
# ─────────────────────────────────────────

def verify_discovery(match):
    """Automatically verify non-triviality of discovery.

    Returns:
        match with added fields: verified_grade, warnings[], verification_detail
    """
    warnings_list = []
    grade = match.get('is_exact', False)

    expr = match['formula']
    target = match['target']
    error_pct = match['error_pct']
    val = match['formula_val']
    target_val = match['target_val']

    # 1. Double-check arithmetic accuracy
    # (already checked in check_targets, double check)

    # 2. Ad hoc correction check: +1, -1 in expression?
    if '+1)' in expr or '-1)' in expr or expr.endswith('+1') or expr.endswith('-1'):
        warnings_list.append('AD_HOC: Contains +1/-1 correction')

    # 3. Strong Law of Small Numbers: all involved constants <100?
    base_consts = extract_base_constants(expr)
    all_small = True
    for name in base_consts:
        for consts in ISLANDS.values():
            if name in consts and abs(consts[name]) >= 100:
                all_small = False
    if all_small and len(base_consts) >= 2:
        # Combinations of small numbers have high chance of coincidence
        warnings_list.append('SMALL_NUMS: All constants <100 (possible coincidence)')

    # 4. Generalization test (if perfect number related)
    if any(name in ['sigma', 'tau', '6'] for name in base_consts):
        # Does it hold for perfect number 28 too?
        warnings_list.append('GENERALIZE: Needs verification for perfect number 28 (not performed)')

    # 5. Simple p-value estimation
    # Estimate "degrees of freedom" of expression: number of constants used × number of operations
    n_consts = len(base_consts)
    # Approximate number of combinations
    total_consts = sum(len(v) for v in ISLANDS.values())
    n_ops = 12  # Types of binary operations
    if n_consts <= 1:
        est_trials = total_consts * 5  # unary only
    elif n_consts == 2:
        est_trials = total_consts * (total_consts - 1) * n_ops
    else:
        est_trials = total_consts ** n_consts * n_ops

    # Number of targets within error range / total space
    # Range: target ± threshold → 2 * threshold * target
    # Space: approximately [0.01, 1000] → 1000
    if target_val != 0:
        p_single = (2 * match['error'] * abs(target_val)) / 1000
    else:
        p_single = 0.001
    p_bonferroni = min(1.0, p_single * est_trials)

    match['p_single'] = p_single
    match['p_bonferroni'] = p_bonferroni
    match['est_trials'] = est_trials

    if p_bonferroni > 0.05:
        warnings_list.append(f'P_VALUE: Bonferroni p={p_bonferroni:.4f} > 0.05 (possible coincidence)')

    # 6. Approximate vs exact grade determination
    if match['is_exact']:
        if not warnings_list:
            verified_grade = '🟩 Exact (verification passed)'
        else:
            verified_grade = '🟩 Exact (caution: ' + '; '.join(warnings_list) + ')'
    elif error_pct < 0.01:
        if p_bonferroni < 0.01:
            verified_grade = '🟧★ Approximate (very precise, p<0.01)'
        elif p_bonferroni < 0.05:
            verified_grade = '🟧 Approximate (precise, p<0.05)'
        else:
            verified_grade = '🟧? Approximate (precise but p>0.05)'
    elif error_pct < 0.1:
        verified_grade = '🟧 Approximate (medium precision)'
    elif error_pct < 1.0:
        verified_grade = '🟧△ Approximate (weak)'
    else:
        verified_grade = '⬜ Meaningless'

    match['verified_grade'] = verified_grade
    match['warnings'] = warnings_list
    match['verification_detail'] = (
        f"grade={verified_grade}, p_bonf={p_bonferroni:.4f}, "
        f"trials≈{est_trials}, warnings={len(warnings_list)}"
    )

    return match


def verify_all(matches):
    """Apply verification pipeline to all discoveries."""
    return [verify_discovery(m) for m in matches]


# ─────────────────────────────────────────
# Output
# ─────────────────────────────────────────

def format_results(matches, cross_only=False):
    """Return sorted results as string"""
    if cross_only:
        matches = find_cross_island(matches)

    matches.sort(key=lambda x: -x['significance'])

    lines = []
    lines.append("=" * 80)
    lines.append("DFS Automatic Search Results")
    lines.append(f"Total {len(matches)} discoveries")
    lines.append("=" * 80)
    lines.append("")

    # Exact matches
    exact = [m for m in matches if m['is_exact']]
    if exact:
        lines.append(f"## Exact Matches ({len(exact)} items)")
        lines.append("")
        for m in exact:
            lines.append(f"  {m['formula']} = {m['target']}  "
                         f"[Islands: {m['islands']}]")
        lines.append("")

    # Approximate matches (cross-connections)
    cross = [m for m in matches if not m['is_exact'] and m['n_islands'] >= 2]
    if cross:
        lines.append(f"## Cross-connection Approximations ({len(cross)} items)")
        lines.append("")
        lines.append(f"  {'Formula':<45} {'Target':<15} {'Error%':>8}  {'Islands':>8}")
        lines.append(f"  {'-'*45} {'-'*15} {'-'*8}  {'-'*8}")
        for m in cross[:50]:
            lines.append(f"  {m['formula']:<45} {m['target']:<15} "
                         f"{m['error_pct']:>7.4f}%  {m['islands']:>8}")
        lines.append("")

    # Single-island approximations
    single = [m for m in matches if not m['is_exact'] and m['n_islands'] < 2]
    if single:
        lines.append(f"## Single-island Approximations ({len(single)} items, top 20)")
        lines.append("")
        for m in single[:20]:
            lines.append(f"  {m['formula']:<45} ~ {m['target']:<15} "
                         f"({m['error_pct']:.4f}%)")
        lines.append("")

    # Cross-connection statistics
    bridge_counts = {}
    for m in matches:
        if m['n_islands'] >= 2:
            key = m['islands']
            bridge_counts[key] = bridge_counts.get(key, 0) + 1
    if bridge_counts:
        lines.append("## Inter-island Bridge Statistics")
        lines.append("")
        for bridge, count in sorted(bridge_counts.items(),
                                     key=lambda x: -x[1]):
            lines.append(f"  {bridge}: {count} connections")
        lines.append("")

    return '\n'.join(lines)


def save_markdown(matches, depth, threshold, output_path):
    """Save results as markdown"""
    now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    lines = []
    lines.append(f"# DFS Automatic Search Results")
    lines.append(f"")
    lines.append(f"- Generated: {now}")
    lines.append(f"- depth: {depth}")
    lines.append(f"- threshold: {threshold} ({threshold*100}%)")
    lines.append(f"- Total discoveries: {len(matches)} items")
    lines.append(f"")

    # Exact matches
    exact = [m for m in matches if m['is_exact']]
    exact.sort(key=lambda x: -x['significance'])
    if exact:
        lines.append(f"## Exact Matches ({len(exact)} items)")
        lines.append(f"")
        lines.append("```")
        for m in exact:
            lines.append(f"  {m['formula']} = {m['target']}  "
                         f"[Islands: {m['islands']}]")
        lines.append("```")
        lines.append("")

    # Cross-connections (core)
    cross = sorted(find_cross_island(matches),
                   key=lambda x: -x['significance'])
    if cross:
        lines.append(f"## Cross-connection Discoveries ({len(cross)} items)")
        lines.append(f"")
        lines.append("| Formula | Target | Error% | Island Connection | Significance |")
        lines.append("|---------|--------|---------|-------------------|--------------|")
        for m in cross[:80]:
            exact_tag = " **exact**" if m['is_exact'] else ""
            lines.append(
                f"| `{m['formula']}` | {m['target']} | "
                f"{m['error_pct']:.5f}%{exact_tag} | "
                f"{m['islands']} | {m['significance']:.1f} |"
            )
        lines.append("")

    # Single-island top
    single = [m for m in matches if m['n_islands'] < 2 and not m['is_exact']]
    single.sort(key=lambda x: x['error'])
    if single:
        lines.append(f"## Single-island Approximations (top 30)")
        lines.append(f"")
        lines.append("| Formula | Target | Error% |")
        lines.append("|---------|--------|--------|")
        for m in single[:30]:
            lines.append(f"| `{m['formula']}` | {m['target']} | "
                         f"{m['error_pct']:.5f}% |")
        lines.append("")

    # Bridge statistics
    bridge_counts = {}
    for m in matches:
        if m['n_islands'] >= 2:
            key = m['islands']
            bridge_counts[key] = bridge_counts.get(key, 0) + 1
    if bridge_counts:
        lines.append("## Inter-island Bridge Summary")
        lines.append("")
        lines.append("```")
        for bridge, count in sorted(bridge_counts.items(),
                                     key=lambda x: -x[1]):
            bar = '#' * min(count, 50)
            lines.append(f"  {bridge:>8}: {count:>4} items  {bar}")
        lines.append("```")
        lines.append("")

    # Key discoveries (top 10 by significance)
    top10 = sorted(matches, key=lambda x: -x['significance'])[:10]
    if top10:
        lines.append("## Top 10 Key Discoveries")
        lines.append("")
        lines.append("```")
        for i, m in enumerate(top10, 1):
            tag = "EXACT" if m['is_exact'] else f"{m['error_pct']:.5f}%"
            lines.append(f"  {i:>2}. {m['formula']}")
            lines.append(f"      = {m['target']} ({tag})  "
                         f"[Islands: {m['islands']}, sig: {m['significance']:.1f}]")
        lines.append("```")
        lines.append("")

    content = '\n'.join(lines)

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(content)

    return output_path


# ─────────────────────────────────────────
# Main
# ─────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description='DFS Automatic Search Engine — Systematic exploration of constant combinations')
    parser.add_argument('--depth', type=int, default=2,
                        help='Recursive combination depth (default: 2)')
    parser.add_argument('--threshold', type=float, default=0.001,
                        help='Error threshold (default: 0.001 = 0.1%%)')
    parser.add_argument('--cross-only', action='store_true',
                        help='Output cross-connections only')
    parser.add_argument('--top', type=int, default=5,
                        help='Maximum matches per target (default: 5)')
    parser.add_argument('--output', type=str,
                        default=None,
                        help='Result save path')
    args = parser.parse_args()

    script_dir = os.path.dirname(os.path.abspath(__file__))
    output_path = args.output or os.path.join(
        script_dir, 'docs', 'proofs', 'dfs-auto-results.md')

    print(f"DFS Automatic Search Engine")
    print(f"  depth:     {args.depth}")
    print(f"  threshold: {args.threshold} ({args.threshold*100}%)")
    print(f"  Output:    {output_path}")
    print()

    # Constant summary
    total_consts = sum(len(v) for v in ISLANDS.values())
    print(f"Input constants: {total_consts} items")
    for iid, consts in ISLANDS.items():
        names = ', '.join(consts.keys())
        print(f"  Island {iid}: {names}")
    print(f"Targets: {len(TARGETS)} items")
    print()

    # DFS build
    print("Generating expressions...")
    expressions = build_level(args.depth)
    print(f"Total expressions: {len(expressions):,} items")
    print()

    # Target matching
    print("Matching targets...")
    matches = check_targets(expressions, threshold=args.threshold)
    print(f"Raw matches: {len(matches):,} items")

    # Filtering
    filtered = filter_best(matches, top_per_target=args.top)
    print(f"After filter: {len(filtered):,} items")

    # Verification pipeline
    print("Verifying...")
    filtered = verify_all(filtered)
    n_warnings = sum(1 for m in filtered if m.get('warnings'))
    n_passed = sum(1 for m in filtered if 'p>0.05' not in m.get('verified_grade', ''))
    print(f"Verification complete: {n_passed} passed, {n_warnings} warnings")

    cross = find_cross_island(filtered)
    print(f"Cross-connections: {len(cross):,} items")
    print()

    # Output
    print(format_results(filtered, cross_only=args.cross_only))

    # Verification summary output
    print("\n" + "=" * 60)
    print(" Verification Pipeline Results")
    print("=" * 60)
    for m in sorted(filtered, key=lambda x: -x['significance'])[:20]:
        grade = m.get('verified_grade', '?')
        warns = m.get('warnings', [])
        warn_str = f" ⚠ {'; '.join(warns)}" if warns else ""
        print(f"  {grade}")
        print(f"    {m['formula']} ≈ {m['target']} ({m['error_pct']:.5f}%)")
        if warn_str:
            print(f"   {warn_str}")
    print()

    # Save
    saved = save_markdown(filtered, args.depth, args.threshold, output_path)
    print(f"\nResults saved: {saved}")


if __name__ == '__main__':
    main()
```