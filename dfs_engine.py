#!/usr/bin/env python3
"""DFS 자동 탐색 엔진 — ralph-loop 수동 반복을 자동화

수동으로 상수 조합을 시도하는 대신, 체계적으로 모든 조합을 DFS로 탐색.
섬 간 교차연결(cross-island bridges)을 자동으로 감지.

사용법:
  python3 dfs_engine.py                          # 기본 depth=2, threshold=0.001
  python3 dfs_engine.py --depth 3                # 3단계 재귀 조합
  python3 dfs_engine.py --threshold 0.0001       # 0.01% 오차 이내만
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
# 설정: 상수 (색상 분류 + 섬 지정)
# ─────────────────────────────────────────

# 섬(Island) 분류:
#   A = 유리수(골든존 분수)    greens
#   B = 정수/미세구조          stars
#   C = 로그/엔트로피          blues
#   D = 초월수(e, pi)          transcendental

ISLANDS = {
    'A': {  # greens — 유리수/분수
        '1/2':   0.5,
        '1/3':   1/3,
        '1/6':   1/6,
        '5/6':   5/6,
        '2/3':   2/3,
    },
    'B': {  # stars — 정수/구조상수
        'I*':    0.212073,          # 골든존 하한
        'sigma': 12.0,             # sigma(6)
        'tau':   4.0,              # tau(6)
        'eH':    2**(2/3) * 3**(1/2),  # 하디-라마누잔 상수
        '17':    17.0,             # 페르마 소수
        '137':   137.0,            # 미세구조상수
        '8':     8.0,              # SU(3)
        '6':     6.0,              # 완전수
    },
    'C': {  # blues — 로그/엔트로피
        'ln(4/3)':  np.log(4/3),   # 엔트로피 점프
        'ln2':      np.log(2),
        'ln3':      np.log(3),
        'ln17':     np.log(17),
        'ln137':    np.log(137),
    },
    'D': {  # transcendental — 초월수
        'e':     np.e,
        '1/e':   1/np.e,
        'pi':    np.pi,
        'phi':   (1 + np.sqrt(5)) / 2,
    },
}

# 타겟 상수: 매칭하면 발견으로 간주
TARGETS = {}

# 수학 상수
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

# 정수 (1~20)
for i in range(1, 21):
    _math[str(i)] = float(i)

# 단순 분수
for a in range(1, 13):
    for b in range(a + 1, 13):
        key = f'{a}/{b}'
        if key not in _math:
            _math[key] = a / b

# 물리 상수
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
# 연산자
# ─────────────────────────────────────────

def binary_ops(a_val, a_name, b_val, b_name):
    """두 값의 이항 연산 결과 리스트 반환: (value, expression, set_of_islands)"""
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

    # 거듭제곱
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
    """단항 연산 확장"""
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
# 섬 추적 (어떤 섬의 상수가 사용되었는지)
# ─────────────────────────────────────────

def get_island(const_name):
    """상수 이름으로 소속 섬을 반환"""
    for island_id, consts in ISLANDS.items():
        if const_name in consts:
            return island_id
    return '?'


def extract_base_constants(expr):
    """수식 문자열에서 사용된 기본 상수 이름들 추출"""
    all_names = set()
    for island_consts in ISLANDS.values():
        for name in island_consts:
            if name in expr:
                all_names.add(name)
    return all_names


def get_islands_from_expr(expr):
    """수식에서 사용된 섬들의 집합 반환"""
    islands = set()
    for name in extract_base_constants(expr):
        islands.add(get_island(name))
    return islands


# ─────────────────────────────────────────
# DFS 엔진 핵심
# ─────────────────────────────────────────

def build_level(depth_limit):
    """깊이 제한까지 상수 조합을 재귀적으로 생성

    Returns: list of (value, expression_string, set_of_islands)
    """
    # Level 0: 모든 기본 상수 + 단항연산
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

        # 이전 레벨의 모든 쌍 조합
        # depth 1: base x base
        # depth 2: (base+level1) x base  (새 것만)
        if depth == 1:
            pool_a = base
            pool_b = base
        else:
            pool_a = current  # 이전 전체
            pool_b = base     # 기본만 (폭발 방지)

        seen_vals = set()
        for i, (av, an, ai) in enumerate(pool_a):
            for j, (bv, bn, bi) in enumerate(pool_b):
                if depth == 1 and j > i:
                    continue  # 중복 방지
                combined_islands = ai | bi

                for rv, rn in binary_ops(av, an, bv, bn):
                    # 값 중복 필터 (소수점 6자리)
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
    """자명한 매칭인지 판별 (이미 알려진 항등식 등)"""
    # 수식이 타겟 이름 자체인 경우
    clean_expr = expr.replace('(', '').replace(')', '')
    if clean_expr == target_name:
        return True

    # 단순 상수가 타겟과 동일
    for consts in ISLANDS.values():
        if target_name in consts and clean_expr in consts:
            if abs(val - target_val) < 1e-12:
                return True

    # 식이 너무 단순 (단일 상수)
    base = extract_base_constants(expr)
    if len(base) <= 1 and abs(val - target_val) < 1e-12:
        return True

    return False


def check_targets(expressions, threshold=0.001):
    """모든 수식을 타겟과 비교, 매칭 반환"""
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
                # 유의성 점수: 더 많은 섬 연결 + 더 작은 오차 = 더 높은 점수
                significance = n_islands * 10 + max(0, -np.log10(rel_err + 1e-15))
                if rel_err < 1e-12:
                    significance += 50  # 정확 일치 보너스

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
    """타겟당 최고 매칭만 유지"""
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
    """섬 간 교차연결만 추출"""
    return [m for m in matches if m['n_islands'] >= 2]


# ─────────────────────────────────────────
# 검증 파이프라인 (발견 즉시 자동 실행)
# ─────────────────────────────────────────

def verify_discovery(match):
    """발견의 비자명성을 자동 검증.

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

    # 1. 산술 정확성 재확인
    # (이미 check_targets에서 확인됨, 이중 체크)

    # 2. ad hoc 보정 체크: +1, -1이 수식에 포함?
    if '+1)' in expr or '-1)' in expr or expr.endswith('+1') or expr.endswith('-1'):
        warnings_list.append('AD_HOC: +1/-1 보정 포함')

    # 3. Strong Law of Small Numbers: 관여 상수가 모두 <100?
    base_consts = extract_base_constants(expr)
    all_small = True
    for name in base_consts:
        for consts in ISLANDS.values():
            if name in consts and abs(consts[name]) >= 100:
                all_small = False
    if all_small and len(base_consts) >= 2:
        # 작은 수끼리의 조합은 우연 일치 가능성 높음
        warnings_list.append('SMALL_NUMS: 모든 상수 <100 (우연 가능성)')

    # 4. 일반화 테스트 (완전수 관련이면)
    if any(name in ['sigma', 'tau', '6'] for name in base_consts):
        # 완전수 28에서도 성립하는지?
        warnings_list.append('GENERALIZE: 완전수 28에서 검증 필요 (미수행)')

    # 5. p-value 간이 추정
    # 수식의 "자유도" 추정: 사용된 상수 수 × 연산 수
    n_consts = len(base_consts)
    # 대략적 조합 수
    total_consts = sum(len(v) for v in ISLANDS.values())
    n_ops = 12  # 이항연산 종류
    if n_consts <= 1:
        est_trials = total_consts * 5  # 단항만
    elif n_consts == 2:
        est_trials = total_consts * (total_consts - 1) * n_ops
    else:
        est_trials = total_consts ** n_consts * n_ops

    # 오차 범위 내 타겟 수 / 전체 공간
    # 범위: target ± threshold → 2 * threshold * target
    # 공간: 대략 [0.01, 1000] → 1000
    if target_val != 0:
        p_single = (2 * match['error'] * abs(target_val)) / 1000
    else:
        p_single = 0.001
    p_bonferroni = min(1.0, p_single * est_trials)

    match['p_single'] = p_single
    match['p_bonferroni'] = p_bonferroni
    match['est_trials'] = est_trials

    if p_bonferroni > 0.05:
        warnings_list.append(f'P_VALUE: Bonferroni p={p_bonferroni:.4f} > 0.05 (우연 가능)')

    # 6. 근사 vs 정확 등급 판정
    if match['is_exact']:
        if not warnings_list:
            verified_grade = '🟩 정확 (검증 통과)'
        else:
            verified_grade = '🟩 정확 (주의: ' + '; '.join(warnings_list) + ')'
    elif error_pct < 0.01:
        if p_bonferroni < 0.01:
            verified_grade = '🟧★ 근사 (매우 정밀, p<0.01)'
        elif p_bonferroni < 0.05:
            verified_grade = '🟧 근사 (정밀, p<0.05)'
        else:
            verified_grade = '🟧? 근사 (정밀하지만 p>0.05)'
    elif error_pct < 0.1:
        verified_grade = '🟧 근사 (중간 정밀)'
    elif error_pct < 1.0:
        verified_grade = '🟧△ 근사 (약한)'
    else:
        verified_grade = '⬜ 무의미'

    match['verified_grade'] = verified_grade
    match['warnings'] = warnings_list
    match['verification_detail'] = (
        f"grade={verified_grade}, p_bonf={p_bonferroni:.4f}, "
        f"trials≈{est_trials}, warnings={len(warnings_list)}"
    )

    return match


def verify_all(matches):
    """모든 발견에 검증 파이프라인 적용."""
    return [verify_discovery(m) for m in matches]


# ─────────────────────────────────────────
# 출력
# ─────────────────────────────────────────

def format_results(matches, cross_only=False):
    """결과를 정렬하여 문자열로 반환"""
    if cross_only:
        matches = find_cross_island(matches)

    matches.sort(key=lambda x: -x['significance'])

    lines = []
    lines.append("=" * 80)
    lines.append("DFS 자동 탐색 결과")
    lines.append(f"발견 총 {len(matches)}개")
    lines.append("=" * 80)
    lines.append("")

    # 정확 일치
    exact = [m for m in matches if m['is_exact']]
    if exact:
        lines.append(f"## 정확 일치 ({len(exact)}개)")
        lines.append("")
        for m in exact:
            lines.append(f"  {m['formula']} = {m['target']}  "
                         f"[섬: {m['islands']}]")
        lines.append("")

    # 근사 일치 (교차연결)
    cross = [m for m in matches if not m['is_exact'] and m['n_islands'] >= 2]
    if cross:
        lines.append(f"## 교차연결 근사 ({len(cross)}개)")
        lines.append("")
        lines.append(f"  {'공식':<45} {'타겟':<15} {'오차%':>8}  {'섬':>8}")
        lines.append(f"  {'-'*45} {'-'*15} {'-'*8}  {'-'*8}")
        for m in cross[:50]:
            lines.append(f"  {m['formula']:<45} {m['target']:<15} "
                         f"{m['error_pct']:>7.4f}%  {m['islands']:>8}")
        lines.append("")

    # 단일섬 근사
    single = [m for m in matches if not m['is_exact'] and m['n_islands'] < 2]
    if single:
        lines.append(f"## 단일섬 근사 ({len(single)}개, 상위 20개)")
        lines.append("")
        for m in single[:20]:
            lines.append(f"  {m['formula']:<45} ~ {m['target']:<15} "
                         f"({m['error_pct']:.4f}%)")
        lines.append("")

    # 교차연결 통계
    bridge_counts = {}
    for m in matches:
        if m['n_islands'] >= 2:
            key = m['islands']
            bridge_counts[key] = bridge_counts.get(key, 0) + 1
    if bridge_counts:
        lines.append("## 섬 간 다리 통계")
        lines.append("")
        for bridge, count in sorted(bridge_counts.items(),
                                     key=lambda x: -x[1]):
            lines.append(f"  {bridge}: {count}개 연결")
        lines.append("")

    return '\n'.join(lines)


def save_markdown(matches, depth, threshold, output_path):
    """결과를 마크다운으로 저장"""
    now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    lines = []
    lines.append(f"# DFS 자동 탐색 결과")
    lines.append(f"")
    lines.append(f"- 생성: {now}")
    lines.append(f"- depth: {depth}")
    lines.append(f"- threshold: {threshold} ({threshold*100}%)")
    lines.append(f"- 총 발견: {len(matches)}개")
    lines.append(f"")

    # 정확 일치
    exact = [m for m in matches if m['is_exact']]
    exact.sort(key=lambda x: -x['significance'])
    if exact:
        lines.append(f"## 정확 일치 ({len(exact)}개)")
        lines.append(f"")
        lines.append("```")
        for m in exact:
            lines.append(f"  {m['formula']} = {m['target']}  "
                         f"[섬: {m['islands']}]")
        lines.append("```")
        lines.append("")

    # 교차연결 (핵심)
    cross = sorted(find_cross_island(matches),
                   key=lambda x: -x['significance'])
    if cross:
        lines.append(f"## 교차연결 발견 ({len(cross)}개)")
        lines.append(f"")
        lines.append("| 공식 | 타겟 | 오차% | 섬 연결 | 유의성 |")
        lines.append("|------|------|-------|---------|--------|")
        for m in cross[:80]:
            exact_tag = " **exact**" if m['is_exact'] else ""
            lines.append(
                f"| `{m['formula']}` | {m['target']} | "
                f"{m['error_pct']:.5f}%{exact_tag} | "
                f"{m['islands']} | {m['significance']:.1f} |"
            )
        lines.append("")

    # 단일섬 상위
    single = [m for m in matches if m['n_islands'] < 2 and not m['is_exact']]
    single.sort(key=lambda x: x['error'])
    if single:
        lines.append(f"## 단일섬 근사 (상위 30개)")
        lines.append(f"")
        lines.append("| 공식 | 타겟 | 오차% |")
        lines.append("|------|------|-------|")
        for m in single[:30]:
            lines.append(f"| `{m['formula']}` | {m['target']} | "
                         f"{m['error_pct']:.5f}% |")
        lines.append("")

    # 다리 통계
    bridge_counts = {}
    for m in matches:
        if m['n_islands'] >= 2:
            key = m['islands']
            bridge_counts[key] = bridge_counts.get(key, 0) + 1
    if bridge_counts:
        lines.append("## 섬 간 다리 요약")
        lines.append("")
        lines.append("```")
        for bridge, count in sorted(bridge_counts.items(),
                                     key=lambda x: -x[1]):
            bar = '#' * min(count, 50)
            lines.append(f"  {bridge:>8}: {count:>4}개  {bar}")
        lines.append("```")
        lines.append("")

    # 핵심 발견 (significance 상위 10)
    top10 = sorted(matches, key=lambda x: -x['significance'])[:10]
    if top10:
        lines.append("## 핵심 발견 Top 10")
        lines.append("")
        lines.append("```")
        for i, m in enumerate(top10, 1):
            tag = "EXACT" if m['is_exact'] else f"{m['error_pct']:.5f}%"
            lines.append(f"  {i:>2}. {m['formula']}")
            lines.append(f"      = {m['target']} ({tag})  "
                         f"[섬: {m['islands']}, sig: {m['significance']:.1f}]")
        lines.append("```")
        lines.append("")

    content = '\n'.join(lines)

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(content)

    return output_path


# ─────────────────────────────────────────
# 메인
# ─────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description='DFS 자동 탐색 엔진 — 상수 조합 체계적 탐색')
    parser.add_argument('--depth', type=int, default=2,
                        help='재귀 조합 깊이 (기본: 2)')
    parser.add_argument('--threshold', type=float, default=0.001,
                        help='오차 임계값 (기본: 0.001 = 0.1%%)')
    parser.add_argument('--cross-only', action='store_true',
                        help='교차연결만 출력')
    parser.add_argument('--top', type=int, default=5,
                        help='타겟당 최대 매칭 수 (기본: 5)')
    parser.add_argument('--output', type=str,
                        default=None,
                        help='결과 저장 경로')
    args = parser.parse_args()

    script_dir = os.path.dirname(os.path.abspath(__file__))
    output_path = args.output or os.path.join(
        script_dir, 'docs', 'proofs', 'dfs-auto-results.md')

    print(f"DFS 자동 탐색 엔진")
    print(f"  depth:     {args.depth}")
    print(f"  threshold: {args.threshold} ({args.threshold*100}%)")
    print(f"  출력:      {output_path}")
    print()

    # 상수 요약
    total_consts = sum(len(v) for v in ISLANDS.values())
    print(f"입력 상수: {total_consts}개")
    for iid, consts in ISLANDS.items():
        names = ', '.join(consts.keys())
        print(f"  섬 {iid}: {names}")
    print(f"타겟: {len(TARGETS)}개")
    print()

    # DFS 빌드
    print("수식 생성 중...")
    expressions = build_level(args.depth)
    print(f"총 수식: {len(expressions):,}개")
    print()

    # 타겟 매칭
    print("타겟 매칭 중...")
    matches = check_targets(expressions, threshold=args.threshold)
    print(f"원시 매칭: {len(matches):,}개")

    # 필터링
    filtered = filter_best(matches, top_per_target=args.top)
    print(f"필터 후:   {len(filtered):,}개")

    # 검증 파이프라인
    print("검증 중...")
    filtered = verify_all(filtered)
    n_warnings = sum(1 for m in filtered if m.get('warnings'))
    n_passed = sum(1 for m in filtered if 'p>0.05' not in m.get('verified_grade', ''))
    print(f"검증 완료: {n_passed}개 통과, {n_warnings}개 주의")

    cross = find_cross_island(filtered)
    print(f"교차연결:  {len(cross):,}개")
    print()

    # 출력
    print(format_results(filtered, cross_only=args.cross_only))

    # 검증 요약 출력
    print("\n" + "=" * 60)
    print(" 검증 파이프라인 결과")
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

    # 저장
    saved = save_markdown(filtered, args.depth, args.threshold, output_path)
    print(f"\n결과 저장: {saved}")


if __name__ == '__main__':
    main()
