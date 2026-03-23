#!/usr/bin/env python3
"""상수 검증기 — 새 상수 발견 시 텍사스 명사수 자동 검정

사용법:
  python3 constant_verifier.py --value 0.577 --target "1/sqrt(3)"
  python3 constant_verifier.py --value 1.676 --target "5/3"
  python3 constant_verifier.py --value 1.0114 --target "1"
"""

import argparse
import math
import random


def parse_target(target_str):
    """문자열을 수학 값으로 변환."""
    replacements = {
        'sqrt': 'math.sqrt',
        'log': 'math.log',
        'ln': 'math.log',
        'pi': 'math.pi',
        'e': 'math.e',
        'phi': '((1+math.sqrt(5))/2)',
    }
    expr = target_str
    for k, v in replacements.items():
        expr = expr.replace(k, v)
    try:
        return eval(expr)
    except:
        raise ValueError(f"Cannot parse: {target_str}")


def texas_sharpshooter(value, target, search_type='simple', n_sim=100000):
    """텍사스 명사수 검정.

    search_type:
      'simple': a/sqrt(b), a=1..3, b=1..20
      'ratio': a/b, a,b=1..20
      'product': a*b, a,b from known constants
    """
    error = abs(value / target - 1) if target != 0 else abs(value)

    if search_type == 'simple':
        count = 0
        total = 0
        for a in range(1, 4):
            for b in range(1, 21):
                try:
                    val = a / math.sqrt(b)
                    total += 1
                    if abs(val / target - 1) <= error:
                        count += 1
                except:
                    pass
        # Also check a^(b/c) * d^(1/e)
        for a in [2, 3, 5, 6, 7]:
            for b in range(1, 7):
                for c in range(1, 7):
                    if b == c:
                        continue
                    for d in [2, 3, 5, 6, 7]:
                        for f in [2, 3, 4, 5, 6]:
                            try:
                                val = a**(b/c) * d**(1/f)
                                total += 1
                                if abs(val / target - 1) <= error:
                                    count += 1
                            except:
                                pass
        p = count / total if total > 0 else 1.0
        return p, count, total

    elif search_type == 'ratio':
        count = 0
        total = 0
        for a in range(1, 21):
            for b in range(1, 21):
                if a == b:
                    continue
                val = a / b
                total += 1
                if abs(val / target - 1) <= error:
                    count += 1
        p = count / total if total > 0 else 1.0
        return p, count, total

    elif search_type == 'uniform':
        random.seed(42)
        lo = target * 0.5
        hi = target * 2.0
        count = sum(1 for _ in range(n_sim) if abs(random.uniform(lo, hi) / target - 1) <= error)
        p = count / n_sim
        return p, count, n_sim


def grade(p_value, error_pct):
    """등급 판정."""
    if p_value > 0.05:
        return '⚪', '우연 (p > 0.05)'
    elif p_value > 0.01:
        return '🟧', f'구조적 근사 (p={p_value:.4f}, {error_pct:.3f}%)'
    else:
        return '🟧★', f'강한 구조적 근사 (p={p_value:.4f}, {error_pct:.3f}%)'


def main():
    parser = argparse.ArgumentParser(description='상수 텍사스 명사수 검정기')
    parser.add_argument('--value', type=float, required=True, help='실측값')
    parser.add_argument('--target', type=str, required=True, help='비교 대상 (예: "1/sqrt(3)", "5/3")')
    parser.add_argument('--search', type=str, default='simple', help='탐색 유형: simple, ratio, uniform')
    args = parser.parse_args()

    target_val = parse_target(args.target)
    error_pct = abs(args.value / target_val - 1) * 100

    print('=' * 50)
    print('  상수 검증기 — 텍사스 명사수 검정')
    print('=' * 50)
    print(f'  실측값:   {args.value}')
    print(f'  타겟:     {args.target} = {target_val:.6f}')
    print(f'  오차:     {error_pct:.4f}%')
    print(f'  탐색 유형: {args.search}')
    print()

    p, count, total = texas_sharpshooter(args.value, target_val, args.search)

    print(f'  탐색 공간: {total} 조합')
    print(f'  동등 이하: {count}')
    print(f'  p-value:   {p:.4f}')
    print()

    emoji, desc = grade(p, error_pct)
    print(f'  등급: {emoji} {desc}')
    print()

    if p <= 0.05:
        print(f'  README 기록용:')
        print(f'  | C?? | {emoji} | {args.target} | {args.value} vs {target_val:.4f} | 검증기 | 텍사스 p={p:.4f}, 오차 {error_pct:.3f}% |')
    else:
        print(f'  기록 불필요 (우연)')

    print('=' * 50)


if __name__ == '__main__':
    main()
