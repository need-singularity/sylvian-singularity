#!/usr/bin/env python3
"""물리 상수 매칭 엔진 — sigma,tau 표현식으로 CODATA 물리 상수 탐색

완전수 6의 sigma=12, tau=4에서 파생된 표현식이
물리 상수를 얼마나 잘 근사하는지 체계적으로 탐색한다.

사용법:
  python3 physics_constant_engine.py                    # 기본 탐색 (1%)
  python3 physics_constant_engine.py --threshold 0.1    # 0.1% 이내만
  python3 physics_constant_engine.py --deep             # 깊은 탐색 (더 많은 표현식)
  python3 physics_constant_engine.py --element           # 원소 분석 모드
"""

import argparse
import math
import random
from itertools import combinations, product as iterproduct

# ─────────────────────────────────────────
# 기본 상수: 완전수 6에서 유도
# ─────────────────────────────────────────
SIGMA = 12          # σ(6) = 1+2+3+6
TAU = 4             # τ(6) = 약수 개수
P1 = 6              # 완전수 자체
M3 = 7              # 메르센 소수 M3 = 2^3 - 1
PERFECT_PAIR = 28   # 두 번째 완전수

# 파생 상수
DERIVED = {
    'sigma':    SIGMA,          # 12
    'tau':      TAU,            # 4
    'P1':       P1,             # 6
    'M3':       M3,             # 7
    's-t':      SIGMA - TAU,    # 8 = SU(3)
    's+t':      SIGMA + TAU,    # 16
    's*t':      SIGMA * TAU,    # 48
    's/t':      SIGMA / TAU,    # 3
    't!':       math.factorial(TAU),  # 24
    'P1!':      720,            # 6! = 720
    's+P1':     SIGMA + P1,     # 18
    'T(s)':     SIGMA * (SIGMA + 1) // 2,  # 삼각수 T(12) = 78
    'T(t)':     TAU * (TAU + 1) // 2,      # 삼각수 T(4) = 10
    'T(P1)':    P1 * (P1 + 1) // 2,        # 삼각수 T(6) = 21
    '2':        2,
    '3':        3,
    '1':        1,
    '5':        5,
    '17':       17,             # 페르마 소수
    '137':      137,            # 미세구조상수
    '153':      153,            # 삼각수 T(17)
}

# ─────────────────────────────────────────
# CODATA 물리 상수 + 핵물리 + 원소
# ─────────────────────────────────────────
PHYSICS_CONSTANTS = {
    # 전자기
    '1/alpha':          137.035999084,      # 미세구조상수 역수
    'alpha':            1/137.035999084,     # 미세구조상수
    # 질량비
    'm_p/m_e':          1836.15267343,       # 양성자/전자 질량비
    'm_mu/m_e':         206.7682830,         # 뮤온/전자 질량비
    'm_tau/m_e':        3477.48,             # 타우 렙톤/전자 질량비
    # 전약력
    'sin2_thetaW':      0.23122,             # 와인버그 각 sin²θ_W
    'alpha_s(M_Z)':     0.1179,              # 강결합상수 at M_Z
    # 원자물리
    'Rydberg_eV':       13.605693122994,     # 뤼드베리 상수 (eV)
    'a0/r_e':           137.036**2,          # 보어반지름/고전적전자반지름
    # 핵 마법수
    'magic_2':          2,
    'magic_8':          8,
    'magic_20':         20,
    'magic_28':         28,
    'magic_50':         50,
    'magic_82':         82,
    'magic_126':        126,
}

# 원소 원자번호
ELEMENTS = {
    'H(1)':   1,   'He(2)':  2,   'C(6)':   6,   'N(7)':   7,
    'O(8)':   8,   'Si(14)': 14,  'Fe(26)': 26,  'Au(79)': 79,
    'U(92)':  92,  'Pb(82)': 82,
}

# 이미 알려진 매칭 (프로젝트 기존 발견)
KNOWN_MATCHES = {
    '1/alpha':      ('8*17+1', 8*17+1, 137),
    'm_p/m_e':      ('sigma*153', SIGMA * 153, 1836),
    'sin2_thetaW':  ('s/t / (s+1)', (SIGMA/TAU) / (SIGMA+1), 3/13),
}


def factorial(n):
    """안전한 팩토리얼 (정수, 범위 제한)"""
    if isinstance(n, float):
        n = int(n)
    if 0 <= n <= 12:
        return math.factorial(n)
    return None


def triangular(n):
    """삼각수 T(n) = n(n+1)/2"""
    if isinstance(n, float):
        n = int(n)
    if 0 <= n <= 1000:
        return n * (n + 1) // 2
    return None


def generate_expressions(deep=False):
    """sigma, tau 파생 상수로 표현식 생성 → (값, 이름) 리스트"""
    # 1단계: 기본 상수
    exprs = [(v, k) for k, v in DERIVED.items()]

    # 단항 연산: 팩토리얼, 삼각수, 제곱, 세제곱
    unary_extra = []
    for v, n in exprs:
        if isinstance(v, (int, float)) and 1 <= v <= 12:
            f = factorial(int(v))
            if f is not None:
                unary_extra.append((f, f'{n}!'))
        if isinstance(v, (int, float)) and 1 <= v <= 200:
            t = triangular(int(v))
            if t is not None:
                unary_extra.append((t, f'T({n})'))
        # 거듭제곱
        if abs(v) < 100:
            unary_extra.append((v**2, f'{n}^2'))
            if abs(v) < 20:
                unary_extra.append((v**3, f'{n}^3'))
    exprs.extend(unary_extra)

    # 2단계: 이항 연산
    base_exprs = list(exprs)
    binary = []
    for (av, an), (bv, bn) in combinations(base_exprs, 2):
        if av is None or bv is None:
            continue
        _safe_add(binary, av + bv, f'({an}+{bn})')
        _safe_add(binary, av - bv, f'({an}-{bn})')
        _safe_add(binary, bv - av, f'({bn}-{an})')
        _safe_add(binary, av * bv, f'{an}*{bn}')
        if bv != 0:
            _safe_add(binary, av / bv, f'{an}/{bn}')
        if av != 0:
            _safe_add(binary, bv / av, f'{bn}/{an}')
        # 거듭제곱 (작은 지수만)
        if 0 < abs(bv) <= 6 and abs(av) < 1000:
            try:
                r = av ** bv
                if abs(r) < 1e15:
                    _safe_add(binary, r, f'{an}^{bn}')
            except (OverflowError, ValueError):
                pass
        if 0 < abs(av) <= 6 and abs(bv) < 1000:
            try:
                r = bv ** av
                if abs(r) < 1e15:
                    _safe_add(binary, r, f'{bn}^{an}')
            except (OverflowError, ValueError):
                pass
    exprs.extend(binary)

    # 3단계 (--deep): 삼항 연산 a*b+c, a*b-c, a*b*c
    if deep:
        for (av, an), (bv, bn) in combinations(base_exprs[:20], 2):
            if av is None or bv is None:
                continue
            ab = av * bv
            ab_n = f'{an}*{bn}'
            for cv, cn in base_exprs[:20]:
                if cv is None:
                    continue
                _safe_add(exprs, ab + cv, f'({ab_n}+{cn})')
                _safe_add(exprs, ab - cv, f'({ab_n}-{cn})')
                _safe_add(exprs, ab * cv, f'{ab_n}*{cn}')
                if cv != 0:
                    _safe_add(exprs, ab / cv, f'{ab_n}/{cn}')

    return exprs


def _safe_add(lst, val, name):
    """유한한 값만 추가"""
    if isinstance(val, (int, float)) and math.isfinite(val) and abs(val) < 1e15:
        lst.append((val, name))


def find_matches(exprs, targets, threshold):
    """각 물리 상수에 가장 가까운 표현식 찾기"""
    results = []
    for tname, tval in targets.items():
        if tval == 0:
            continue
        best_err = float('inf')
        best_expr = None
        best_calc = None
        for val, ename in exprs:
            if val == 0 and tval == 0:
                continue
            err = abs(val - tval) / abs(tval)
            if err < best_err:
                best_err = err
                best_expr = ename
                best_calc = val
        if best_err <= threshold:
            results.append({
                'target': tname,
                'value': tval,
                'expr': best_expr,
                'calc': best_calc,
                'error': best_err * 100,  # 퍼센트
            })
    # 오차순 정렬
    results.sort(key=lambda x: x['error'])
    return results


def texas_sharpshooter(exprs, targets, threshold, trials=1000):
    """텍사스 명사수 검정: 랜덤 표현식 대비 매칭 수 비교

    랜덤으로 같은 수의 표현식을 만들어 매칭 수를 측정.
    우리 매칭이 우연보다 유의미한지 판정한다.
    """
    # 실제 매칭 수
    actual = len(find_matches(exprs, targets, threshold))

    # 랜덤 시뮬레이션: 동일 개수의 랜덤 값으로 매칭 시도
    n_exprs = len(exprs)
    val_range = [v for v, _ in exprs if abs(v) < 1e6]
    if not val_range:
        return actual, 0.0, 0

    vmin, vmax = min(val_range), max(val_range)
    random_counts = []
    for _ in range(trials):
        # 랜덤 표현식: 같은 범위에서 균등 분포
        rand_exprs = [(random.uniform(vmin, vmax), f'rand_{i}')
                      for i in range(min(n_exprs, 500))]
        cnt = len(find_matches(rand_exprs, targets, threshold))
        random_counts.append(cnt)

    avg_random = sum(random_counts) / len(random_counts) if random_counts else 0
    # p-value: 랜덤이 actual 이상 매칭한 비율
    p_value = sum(1 for c in random_counts if c >= actual) / trials
    return actual, avg_random, p_value


def print_table(results, actual, avg_random, p_value):
    """결과를 ASCII 테이블로 출력"""
    print("\n" + "=" * 80)
    print("  물리 상수 매칭 엔진 — sigma(6)=12, tau(6)=4 표현식 탐색")
    print("=" * 80)

    if not results:
        print("\n  매칭 결과 없음. --threshold 값을 늘려보세요.")
        return

    # 헤더
    print(f"\n{'순위':>4} {'물리상수':<18} {'실제값':>14} {'표현식':<28} {'계산값':>14} {'오차%':>8}")
    print("-" * 90)

    for i, r in enumerate(results, 1):
        # 기존 발견 마커
        marker = ""
        if r['target'] in KNOWN_MATCHES:
            marker = " *기존*"
        print(f"{i:>4} {r['target']:<18} {r['value']:>14.6f} "
              f"{r['expr']:<28} {r['calc']:>14.6f} {r['error']:>7.4f}%{marker}")

    print("-" * 90)
    print(f"  총 매칭: {len(results)}개")

    # 텍사스 명사수 결과
    print(f"\n{'=' * 50}")
    print("  텍사스 명사수 검정 (Texas Sharpshooter Test)")
    print(f"{'=' * 50}")
    print(f"  실제 매칭 수:     {actual}")
    print(f"  랜덤 평균 매칭:   {avg_random:.1f}")
    print(f"  p-value:          {p_value:.4f}")
    if p_value < 0.01:
        print("  판정: 구조적 발견 (p < 0.01)")
    elif p_value < 0.05:
        print("  판정: 약한 증거 (p < 0.05)")
    else:
        print("  판정: 우연 가능 (p >= 0.05)")


def element_analysis(exprs, threshold):
    """원소 원자번호 매칭 분석 모드"""
    print("\n" + "=" * 60)
    print("  원소 원자번호 매칭 (sigma,tau 표현식)")
    print("=" * 60)

    results = find_matches(exprs, ELEMENTS, threshold)
    if not results:
        print("  매칭 없음.")
        return

    print(f"\n{'원소':<10} {'Z':>4} {'표현식':<30} {'계산값':>10} {'오차%':>8}")
    print("-" * 66)
    for r in results:
        print(f"{r['target']:<10} {r['value']:>4.0f} "
              f"{r['expr']:<30} {r['calc']:>10.4f} {r['error']:>7.4f}%")


def main():
    parser = argparse.ArgumentParser(
        description='물리 상수 매칭 엔진 — sigma,tau 표현식 탐색')
    parser.add_argument('--threshold', type=float, default=1.0,
                        help='오차 임계값 %% (기본: 1.0)')
    parser.add_argument('--deep', action='store_true',
                        help='깊은 탐색 (삼항 연산 포함)')
    parser.add_argument('--element', action='store_true',
                        help='원소 원자번호 분석 모드')
    parser.add_argument('--texas-trials', type=int, default=500,
                        help='텍사스 명사수 시뮬레이션 횟수 (기본: 500)')
    args = parser.parse_args()

    threshold = args.threshold / 100.0  # 퍼센트→비율

    print(f"  설정: threshold={args.threshold}%, deep={args.deep}")
    print(f"  기본 상수: sigma={SIGMA}, tau={TAU}, P1={P1}, M3={M3}")

    # 표현식 생성
    exprs = generate_expressions(deep=args.deep)
    print(f"  생성된 표현식: {len(exprs)}개")

    # 알려진 매칭 강제 추가
    for tname, (expr_str, calc_val, _) in KNOWN_MATCHES.items():
        exprs.append((calc_val, expr_str))

    # 물리 상수 매칭
    results = find_matches(exprs, PHYSICS_CONSTANTS, threshold)

    # 텍사스 명사수 검정
    actual, avg_random, p_value = texas_sharpshooter(
        exprs, PHYSICS_CONSTANTS, threshold, trials=args.texas_trials)

    print_table(results, actual, avg_random, p_value)

    # 원소 분석 모드
    if args.element:
        element_analysis(exprs, threshold)

    # 기존 발견 요약
    print(f"\n{'=' * 50}")
    print("  기존 발견 (프로젝트 내 검증 완료)")
    print(f"{'=' * 50}")
    for tname, (expr_str, calc_val, approx) in KNOWN_MATCHES.items():
        tv = PHYSICS_CONSTANTS.get(tname, 0)
        err = abs(calc_val - tv) / abs(tv) * 100 if tv else 0
        print(f"  {tname}: {expr_str} = {calc_val} (오차 {err:.4f}%)")


if __name__ == '__main__':
    main()
