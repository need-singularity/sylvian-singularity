#!/usr/bin/env python3
"""공식 생성 엔진 — 상수 관계 자동 탐색 + 유의성 검정

사용법:
  python3 formula_engine.py                    # 전체 탐색
  python3 formula_engine.py --target 137       # 137을 만드는 공식 탐색
  python3 formula_engine.py --depth 3          # 3단계 깊이 탐색
  python3 formula_engine.py --significance     # 유의성 검정 포함
"""

import numpy as np
from itertools import combinations, product as iterproduct
import argparse
from scipy import stats
import os
from datetime import datetime

RESULTS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "results")


# ─────────────────────────────────────────
# 우리 모델의 핵심 상수
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

# 물리 상수 (타겟)
PHYSICS = {
    'α(미세구조)': 1/137.036,
    '1/α': 137.036,
    'αs(강력)': 0.118,
    'sin²θ_W': 0.231,
    'T_CMB': 2.72548,
    'Ω_Λ(암흑에너지)': 0.683,
    'Ω_b(보통물질)': 0.049,
    'Ω_DM(암흑물질)': 0.268,
}

# 수학 상수 (타겟)
MATH_TARGETS = {
    'π': np.pi,
    'π/2': np.pi/2,
    'π/4': np.pi/4,
    'π/6': np.pi/6,
    'φ(황금비)': (1+np.sqrt(5))/2,
    'ln(2)': np.log(2),
    'ln(3)': np.log(3),
    'sqrt(2)': np.sqrt(2),
    'sqrt(3)': np.sqrt(3),
    'γ(오일러-마스케로니)': 0.5772156649,
}


# ─────────────────────────────────────────
# 연산자
# ─────────────────────────────────────────
def safe_ops(a, b):
    """두 값에 대한 안전한 연산 목록 반환"""
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
    """단항 연산"""
    results = [(a[0], a[1])]
    if a[0] > 0:
        results.append((np.log(a[0]), f'ln({a[1]})'))
        results.append((np.sqrt(a[0]), f'√({a[1]})'))
    results.append((np.exp(a[0]), f'e^({a[1]})'))
    if a[0] != 0:
        results.append((1/a[0], f'1/({a[1]})'))
    return [(v, expr) for v, expr in results if np.isfinite(v) and abs(v) < 1e10]


# ─────────────────────────────────────────
# 공식 탐색 엔진
# ─────────────────────────────────────────
def search_formulas(targets, max_depth=2, threshold=0.01):
    """상수 조합으로 타겟 값을 만드는 공식 탐색"""

    # 1단계: 기본 상수
    level_1 = [(v, k) for k, v in CONSTANTS.items()]

    # 단항 연산 확장
    level_1_ext = []
    for val, name in level_1:
        level_1_ext.extend(unary_ops((val, name)))

    # 2단계: 이항 연산
    level_2 = []
    if max_depth >= 2:
        for i, a in enumerate(level_1_ext):
            for j, b in enumerate(level_1_ext):
                if i <= j:
                    level_2.extend(safe_ops(a, b))

    all_formulas = level_1_ext + level_2

    # 타겟 매칭
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

    # 정렬: 오차 순
    matches.sort(key=lambda x: (x['target'], x['error']))

    return matches


def significance_test(matches, n_random=10000):
    """텍사스 명사수 검정: 랜덤 상수로도 같은 매칭이 나오는가?"""

    n_real_matches = len(matches)
    n_targets = len(set(m['target'] for m in matches))

    # 랜덤 상수로 같은 탐색 반복
    random_match_counts = []

    for trial in range(n_random):
        # 랜덤 상수 (같은 수, 같은 범위)
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

        # 같은 타겟에 대해 매칭 수 계산
        targets = {m['target']: m['target_val'] for m in matches}
        rand_matches = 0
        for t_name, t_val in targets.items():
            for val, expr in all_rand:
                if t_val != 0 and abs(val - t_val) / abs(t_val) < 0.01:
                    rand_matches += 1
                    break  # 타겟당 1개만

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
# 메인
# ─────────────────────────────────────────
def main():
    parser = argparse.ArgumentParser(description="공식 생성 엔진")
    parser.add_argument('--target', type=float, default=None, help="특정 값을 만드는 공식 탐색")
    parser.add_argument('--depth', type=int, default=2, help="탐색 깊이 (기본 2)")
    parser.add_argument('--threshold', type=float, default=0.01, help="오차 임계값 (기본 0.01)")
    parser.add_argument('--significance', action='store_true', help="텍사스 명사수 검정")
    parser.add_argument('--physics', action='store_true', help="물리 상수 타겟")
    parser.add_argument('--math', action='store_true', help="수학 상수 타겟")
    parser.add_argument('--all', action='store_true', help="전체 탐색")
    args = parser.parse_args()

    print()
    print("═" * 60)
    print("   🔬 공식 생성 엔진 v1.0")
    print("═" * 60)

    # 타겟 결정
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

    print(f"  상수: {len(CONSTANTS)}개")
    print(f"  타겟: {len(targets)}개")
    print(f"  깊이: {args.depth}")
    print(f"  임계: {args.threshold*100}%")
    print("─" * 60)

    # 탐색
    matches = search_formulas(targets, max_depth=args.depth, threshold=args.threshold)

    # 결과 출력
    print(f"\n  발견된 공식: {len(matches)}개")
    print()

    current_target = None
    for m in matches:
        if m['target'] != current_target:
            current_target = m['target']
            print(f"  ═══ {m['target']} = {m['target_val']:.6f} ═══")

        star = "★" if m['error_pct'] < 0.1 else ("●" if m['error_pct'] < 0.5 else "·")
        print(f"    {star} {m['formula']:30} = {m['formula_val']:.6f} (오차 {m['error_pct']:.3f}%)")

    # 유의성 검정
    if args.significance and matches:
        print(f"\n{'═' * 60}")
        print(f"  텍사스 명사수 검정")
        print(f"{'═' * 60}")

        sig = significance_test(matches, n_random=1000)

        print(f"  실제 매칭 타겟: {sig['real_targets_hit']}개")
        print(f"  랜덤 평균:      {sig['random_mean']:.1f} ± {sig['random_std']:.1f}")
        print(f"  Z-score:        {sig['z_score']:.2f}")
        print(f"  p-value:        {sig['p_value']:.4f}")
        print()

        if sig['p_value'] < 0.01:
            print(f"  판정: ✅ 유의미 (p < 0.01) — 우연이 아닐 확률 {(1-sig['p_value'])*100:.1f}%")
        elif sig['p_value'] < 0.05:
            print(f"  판정: ⚠️ 약한 유의 (p < 0.05)")
        else:
            print(f"  판정: ❌ 유의하지 않음 (p = {sig['p_value']:.2f}) — 텍사스 명사수 가능성")

    # 저장
    os.makedirs(RESULTS_DIR, exist_ok=True)
    with open(os.path.join(RESULTS_DIR, "formula_discovery.md"), 'a', encoding='utf-8') as f:
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        f.write(f"\n# 공식 탐색 [{now}]\n\n")
        f.write(f"상수 {len(CONSTANTS)}개, 타겟 {len(targets)}개, 발견 {len(matches)}개\n\n")
        for m in matches[:20]:
            f.write(f"- {m['target']}: {m['formula']} = {m['formula_val']:.6f} (오차 {m['error_pct']:.3f}%)\n")
        f.write("\n---\n")

    print(f"\n  📁 결과 → results/formula_discovery.md")
    print()


if __name__ == '__main__':
    main()
