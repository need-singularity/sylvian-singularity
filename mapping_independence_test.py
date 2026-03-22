#!/usr/bin/env python3
"""매핑 독립성 검증 — "골든존에서 CCT 최대"는 구조적 발견인가?

1000가지 랜덤 매핑 공식을 생성하여, "CCT가 골든존에서 최대"라는
결과가 우리 매핑(i_to_lorenz)의 특수성 때문인지, 아니면 로렌츠
시스템 자체의 구조적 성질인지를 검증한다.

실험:
  - 1000개 랜덤 매핑: sigma, rho, noise, gap = f(I) (랜덤 계수)
  - 각 매핑에서 I=0~1 스캔 → CCT 최적 I값 기록
  - 최적 I값이 골든존(0.213~0.500)에 떨어지는 비율 측정
  - 랜덤 기대값(28.7%)과 비교 → 이항검정

골든존 의존: YES (검증 대상 자체가 골든존)

사용법:
  python3 mapping_independence_test.py
  python3 mapping_independence_test.py --n-mappings 500 --grid 15
  python3 mapping_independence_test.py --quick
"""

import argparse
import math
import sys
import time

import numpy as np
from scipy import stats as sp_stats

from consciousness_calc import lorenz_simulate, run_cct

# ─────────────────────────────────────────────
# 골든존 상수
# ─────────────────────────────────────────────
GOLDEN_UPPER = 0.5
GOLDEN_LOWER = 0.5 - math.log(4 / 3)   # ≈ 0.2123
GOLDEN_WIDTH = GOLDEN_UPPER - GOLDEN_LOWER  # ≈ 0.2877
GOLDEN_EXPECTED = GOLDEN_WIDTH / (0.99 - 0.01)  # 스캔 범위 0.01~0.99 기준


# ─────────────────────────────────────────────
# 랜덤 매핑 생성
# ─────────────────────────────────────────────
def generate_random_mapping(rng):
    """랜덤 매핑 계수를 생성한다.

    각 파라미터 = a + b * I^c 형태.
    범위 제약: sigma ∈ [0.1, 20], rho ∈ [1, 50], noise ∈ [0, 1], gap ∈ [0, 1]

    Returns:
        dict with keys 'sigma_abc', 'rho_abc', 'noise_abc', 'gap_abc'
        각 값은 (a, b, c) 튜플
    """
    def rand_abc(a_range, b_range, c_range):
        a = rng.uniform(*a_range)
        b = rng.uniform(*b_range)
        c = rng.uniform(*c_range)
        return (a, b, c)

    return {
        # sigma: 0.1~20 범위. a ∈ [0.1, 15], b ∈ [-15, 15], c ∈ [0.2, 3]
        "sigma_abc": rand_abc((0.1, 15.0), (-15.0, 15.0), (0.2, 3.0)),
        # rho: 1~50 범위. a ∈ [1, 40], b ∈ [-30, 30], c ∈ [0.2, 3]
        "rho_abc": rand_abc((1.0, 40.0), (-30.0, 30.0), (0.2, 3.0)),
        # noise: 0~1 범위. a ∈ [0, 0.5], b ∈ [-0.5, 0.5], c ∈ [0.2, 3]
        "noise_abc": rand_abc((0.0, 0.5), (-0.5, 0.5), (0.2, 3.0)),
        # gap: 0~1 범위. a ∈ [-0.5, 0.3], b ∈ [-0.5, 0.5], c ∈ [0.2, 3]
        "gap_abc": rand_abc((-0.5, 0.3), (-0.5, 0.5), (0.2, 3.0)),
    }


def apply_mapping(mapping, I):
    """매핑 계수로 I를 로렌츠 파라미터로 변환한다."""
    def calc(abc, I_val):
        a, b, c = abc
        return a + b * (I_val ** c)

    sigma = np.clip(calc(mapping["sigma_abc"], I), 0.1, 20.0)
    rho = np.clip(calc(mapping["rho_abc"], I), 1.0, 50.0)
    noise = np.clip(calc(mapping["noise_abc"], I), 0.0, 1.0)
    gap = np.clip(calc(mapping["gap_abc"], I), 0.0, 1.0)
    beta = 2.67

    return {
        "sigma": float(sigma),
        "rho": float(rho),
        "beta": beta,
        "noise": float(noise),
        "gap_ratio": float(gap),
    }


def generate_inverted_mapping(rng):
    """반전 매핑: 원래와 반대 방향의 매핑을 생성한다.

    sigma = a + b*I (b > 0, 즉 I가 클수록 sigma 증가 — 원래와 반대)
    rho   = a + b*I (b > 0)
    noise = a + b*I (b > 0)
    gap   = a + b*I (b < 0, 즉 I가 클수록 gap 감소)
    """
    return {
        "sigma_abc": (rng.uniform(0.5, 5.0), rng.uniform(5.0, 15.0), 1.0),
        "rho_abc": (rng.uniform(5.0, 15.0), rng.uniform(10.0, 30.0), 1.0),
        "noise_abc": (rng.uniform(0.0, 0.1), rng.uniform(0.1, 0.5), 1.0),
        "gap_abc": (rng.uniform(0.0, 0.5), rng.uniform(-0.8, -0.2), 1.0),
    }


# ─────────────────────────────────────────────
# CCT 스캔
# ─────────────────────────────────────────────
def scan_mapping(mapping, grid, steps, dt):
    """하나의 매핑에서 I=0.01~0.99를 스캔하여 CCT 총점을 구한다.

    Returns:
        best_i: CCT 최대인 I값
        best_score: 최대 CCT 총점
        has_gap: 이 매핑에서 gap > 0인 I값이 존재하는지
    """
    i_values = np.linspace(0.01, 0.99, grid)
    best_i = 0.0
    best_score = -1.0
    has_gap = False

    for I in i_values:
        params = apply_mapping(mapping, I)
        if params["gap_ratio"] > 0.01:
            has_gap = True

        try:
            _, S = lorenz_simulate(
                sigma=params["sigma"],
                rho=params["rho"],
                beta=params["beta"],
                noise=params["noise"],
                gap_ratio=params["gap_ratio"],
                steps=steps,
                dt=dt,
                seed=42,
            )

            results = run_cct(S, params["gap_ratio"])
            # run_cct returns dict of (score, passed, detail) tuples
            total = sum(score for score, _, _ in results.values())

            if total > best_score:
                best_score = total
                best_i = I
        except Exception:
            continue

    return best_i, best_score, has_gap


# ─────────────────────────────────────────────
# ASCII 히스토그램
# ─────────────────────────────────────────────
def ascii_histogram(values, bins=20, width=50, title=""):
    """값 분포의 ASCII 히스토그램을 반환한다."""
    lines = []
    if title:
        lines.append(f"  {title}")
        lines.append("")

    hist, edges = np.histogram(values, bins=bins, range=(0.0, 1.0))
    max_count = max(hist) if max(hist) > 0 else 1

    for i in range(len(hist)):
        lo = edges[i]
        hi = edges[i + 1]
        bar_len = int(hist[i] / max_count * width)
        bar = "█" * bar_len

        # 골든존 내부인지 표시
        mid = (lo + hi) / 2
        in_golden = GOLDEN_LOWER <= mid <= GOLDEN_UPPER
        marker = " ◀" if in_golden else ""

        lines.append(f"  {lo:.2f}-{hi:.2f} │{bar:<{width}} {hist[i]:>4}{marker}")

    lines.append(f"  {'─' * 10}┘{'─' * width}")
    lines.append(f"  골든존 범위: {GOLDEN_LOWER:.3f} ~ {GOLDEN_UPPER:.3f}")
    lines.append("")
    return "\n".join(lines)


# ─────────────────────────────────────────────
# 이항검정
# ─────────────────────────────────────────────
def binomial_test(n_in_golden, n_total, expected_rate):
    """이항검정으로 p-value를 산출한다."""
    result = sp_stats.binomtest(n_in_golden, n_total, expected_rate, alternative="greater")
    return result.pvalue


# ─────────────────────────────────────────────
# 메인 실험
# ─────────────────────────────────────────────
def run_experiment(n_mappings, grid, steps, dt, seed=12345):
    """전체 실험 실행."""
    rng = np.random.default_rng(seed)

    # 일반 랜덤 매핑 (80%) + 반전 매핑 (20%)
    n_inverted = n_mappings // 5
    n_normal = n_mappings - n_inverted

    all_best_i = []
    all_has_gap = []
    all_mapping_type = []  # 'normal' or 'inverted'

    t_start = time.time()

    print(f"  실험 설정:")
    print(f"    총 매핑 수:     {n_mappings}")
    print(f"    일반 매핑:      {n_normal}")
    print(f"    반전 매핑:      {n_inverted}")
    print(f"    I 스캔 해상도:  grid={grid}")
    print(f"    시뮬레이션:     steps={steps}, dt={dt}")
    print(f"    골든존:         [{GOLDEN_LOWER:.4f}, {GOLDEN_UPPER:.4f}]")
    print(f"    골든존 폭:      {GOLDEN_WIDTH:.4f}")
    print(f"    랜덤 기대 비율: {GOLDEN_EXPECTED:.4f} ({GOLDEN_EXPECTED*100:.1f}%)")
    print()

    for i in range(n_mappings):
        if i < n_normal:
            mapping = generate_random_mapping(rng)
            mtype = "normal"
        else:
            mapping = generate_inverted_mapping(rng)
            mtype = "inverted"

        best_i, best_score, has_gap = scan_mapping(mapping, grid, steps, dt)
        all_best_i.append(best_i)
        all_has_gap.append(has_gap)
        all_mapping_type.append(mtype)

        # 진행률 (매 100개 또는 매 10%)
        if (i + 1) % max(1, n_mappings // 10) == 0 or (i + 1) == n_mappings:
            elapsed = time.time() - t_start
            rate = (i + 1) / elapsed if elapsed > 0 else 0
            eta = (n_mappings - i - 1) / rate if rate > 0 else 0
            pct = (i + 1) / n_mappings * 100
            bar_len = 30
            filled = int(bar_len * (i + 1) / n_mappings)
            bar = "█" * filled + "░" * (bar_len - filled)
            sys.stdout.write(
                f"\r  진행: [{bar}] {pct:5.1f}% ({i+1}/{n_mappings}) "
                f"ETA: {eta:.0f}s"
            )
            sys.stdout.flush()

    sys.stdout.write("\r" + " " * 80 + "\r")
    sys.stdout.flush()

    elapsed = time.time() - t_start
    print(f"  완료: {n_mappings}개 매핑, {elapsed:.1f}초 소요")
    print()

    # numpy 변환
    all_best_i = np.array(all_best_i)
    all_has_gap = np.array(all_has_gap)
    all_mapping_type = np.array(all_mapping_type)

    return all_best_i, all_has_gap, all_mapping_type


def analyze_and_report(all_best_i, all_has_gap, all_mapping_type):
    """결과 분석 및 보고."""
    n_total = len(all_best_i)

    # 1. 전체 분석
    in_golden = (all_best_i >= GOLDEN_LOWER) & (all_best_i <= GOLDEN_UPPER)
    n_in_golden = np.sum(in_golden)
    ratio_golden = n_in_golden / n_total

    # 이항검정
    p_value = binomial_test(int(n_in_golden), n_total, GOLDEN_EXPECTED)

    print("═" * 65)
    print("  매핑 독립성 검증 — 골든존 CCT 최적화 테스트")
    print("═" * 65)
    print()

    # 히스토그램
    print(ascii_histogram(all_best_i, bins=20, title="최적 I값 분포 (전체)"))

    # 핵심 결과
    print("─" * 65)
    print("  [ 핵심 결과 ]")
    print("─" * 65)
    print()
    print(f"  전체 매핑 수:          {n_total}")
    print(f"  골든존 내 최적 I:      {n_in_golden} ({ratio_golden*100:.1f}%)")
    print(f"  랜덤 기대값:           {GOLDEN_EXPECTED*100:.1f}%")
    print(f"  초과 비율:             {(ratio_golden - GOLDEN_EXPECTED)*100:+.1f}%p")
    print(f"  이항검정 p-value:      {p_value:.6f}")
    if p_value < 0.001:
        print(f"  유의수준:              p < 0.001 ★★★")
    elif p_value < 0.01:
        print(f"  유의수준:              p < 0.01  ★★")
    elif p_value < 0.05:
        print(f"  유의수준:              p < 0.05  ★")
    else:
        print(f"  유의수준:              유의하지 않음 (p >= 0.05)")
    print()

    # 2. 매핑 유형별 분석
    normal_mask = all_mapping_type == "normal"
    inverted_mask = all_mapping_type == "inverted"

    print("─" * 65)
    print("  [ 매핑 유형별 분석 ]")
    print("─" * 65)
    print()

    for label, mask in [("일반 매핑", normal_mask), ("반전 매핑", inverted_mask)]:
        if np.sum(mask) == 0:
            continue
        subset = all_best_i[mask]
        n_sub = len(subset)
        n_sub_golden = np.sum((subset >= GOLDEN_LOWER) & (subset <= GOLDEN_UPPER))
        r_sub = n_sub_golden / n_sub if n_sub > 0 else 0
        p_sub = binomial_test(int(n_sub_golden), n_sub, GOLDEN_EXPECTED) if n_sub > 0 else 1.0
        print(f"  {label}:")
        print(f"    개수:              {n_sub}")
        print(f"    골든존 내 비율:    {n_sub_golden}/{n_sub} ({r_sub*100:.1f}%)")
        print(f"    p-value:           {p_sub:.6f}")
        print()

    # 3. gap 유무별 분석
    print("─" * 65)
    print("  [ gap 유무별 분석 ]")
    print("─" * 65)
    print()

    for label, mask in [("gap 있는 매핑", all_has_gap), ("gap 없는 매핑", ~all_has_gap)]:
        if np.sum(mask) == 0:
            print(f"  {label}: 없음")
            print()
            continue
        subset = all_best_i[mask]
        n_sub = len(subset)
        n_sub_golden = np.sum((subset >= GOLDEN_LOWER) & (subset <= GOLDEN_UPPER))
        r_sub = n_sub_golden / n_sub if n_sub > 0 else 0
        p_sub = binomial_test(int(n_sub_golden), n_sub, GOLDEN_EXPECTED) if n_sub > 0 else 1.0
        print(f"  {label}:")
        print(f"    개수:              {n_sub}")
        print(f"    골든존 내 비율:    {n_sub_golden}/{n_sub} ({r_sub*100:.1f}%)")
        print(f"    p-value:           {p_sub:.6f}")
        mean_i = np.mean(subset)
        std_i = np.std(subset)
        print(f"    최적I 평균±std:    {mean_i:.3f} ± {std_i:.3f}")
        print()

    # gap 없는 매핑만의 히스토그램
    no_gap_mask = ~all_has_gap
    if np.sum(no_gap_mask) > 10:
        print(ascii_histogram(
            all_best_i[no_gap_mask], bins=20,
            title="최적 I값 분포 (gap 없는 매핑만)",
        ))

    # 4. 텍사스 명사수 검정 요약
    print("─" * 65)
    print("  [ 텍사스 명사수 검정 ]")
    print("─" * 65)
    print()
    print(f"  H0: 최적 I값의 골든존 집중은 우연 (기대={GOLDEN_EXPECTED*100:.1f}%)")
    print(f"  H1: 골든존 집중은 구조적 (기대 초과)")
    print()
    print(f"  관측값:     {n_in_golden}/{n_total} ({ratio_golden*100:.1f}%)")
    print(f"  기대값:     {GOLDEN_EXPECTED*n_total:.1f}/{n_total} ({GOLDEN_EXPECTED*100:.1f}%)")
    print(f"  p-value:    {p_value:.6f}")
    print()

    # 5. 최종 판정
    print("═" * 65)
    print("  [ 최종 판정 ]")
    print("═" * 65)
    print()

    if p_value < 0.05 and ratio_golden > GOLDEN_EXPECTED * 1.5:
        verdict = "구조적 발견"
        detail = (
            f"골든존 내 최적 I 비율({ratio_golden*100:.1f}%)이 "
            f"랜덤 기대({GOLDEN_EXPECTED*100:.1f}%)를 유의하게 초과.\n"
            f"  매핑 공식에 무관하게 로렌츠 시스템 자체가 골든존에서 CCT를 최대화하는 경향이 있다."
        )
    elif p_value < 0.05:
        verdict = "약한 구조적 발견"
        detail = (
            f"통계적으로 유의(p={p_value:.4f})하지만 효과 크기가 작다.\n"
            f"  골든존 효과가 존재하나 매핑에 크게 의존한다."
        )
    elif ratio_golden > GOLDEN_EXPECTED * 1.2:
        verdict = "판단 보류"
        detail = (
            f"골든존 비율({ratio_golden*100:.1f}%)이 기대보다 약간 높으나 "
            f"통계적으로 유의하지 않음(p={p_value:.4f}).\n"
            f"  더 많은 매핑(n > 5000)으로 재검증 필요."
        )
    else:
        verdict = "매핑의 산물"
        detail = (
            f"골든존 내 최적 I 비율({ratio_golden*100:.1f}%)이 "
            f"랜덤 기대({GOLDEN_EXPECTED*100:.1f}%)와 유사.\n"
            f"  '골든존에서 CCT 최대'는 매핑 공식 설계의 산물일 가능성이 높다."
        )

    print(f"  판정: {verdict}")
    print(f"  근거: {detail}")
    print()

    # gap 없는 매핑 추가 판정
    if np.sum(~all_has_gap) > 10:
        no_gap_best = all_best_i[~all_has_gap]
        ng_in_golden = np.sum((no_gap_best >= GOLDEN_LOWER) & (no_gap_best <= GOLDEN_UPPER))
        ng_ratio = ng_in_golden / len(no_gap_best)
        ng_p = binomial_test(int(ng_in_golden), len(no_gap_best), GOLDEN_EXPECTED)
        print(f"  추가: gap 없는 매핑에서도 골든존 효과 {'있음' if ng_p < 0.05 else '없음'}"
              f" (비율={ng_ratio*100:.1f}%, p={ng_p:.4f})")
        if ng_p < 0.05:
            print(f"  → gap 메커니즘 없이도 골든존 효과 존재 = 더 강한 증거")
        print()

    print("═" * 65)
    print()


# ─────────────────────────────────────────────
# CLI
# ─────────────────────────────────────────────
def main():
    parser = argparse.ArgumentParser(
        description="매핑 독립성 검증: 골든존 CCT 최적화가 매핑의 산물인지 구조적 발견인지 검증",
    )
    parser.add_argument("--n-mappings", type=int, default=1000,
                        help="랜덤 매핑 수 (기본 1000)")
    parser.add_argument("--grid", type=int, default=20,
                        help="I 스캔 해상도 (기본 20)")
    parser.add_argument("--steps", type=int, default=10000,
                        help="로렌츠 시뮬레이션 스텝 수 (기본 10000, 속도 우선)")
    parser.add_argument("--dt", type=float, default=0.01,
                        help="시간 간격 (기본 0.01)")
    parser.add_argument("--quick", action="store_true",
                        help="빠른 실행 (100개, grid=10)")
    parser.add_argument("--seed", type=int, default=12345,
                        help="난수 시드 (기본 12345)")

    args = parser.parse_args()

    if args.quick:
        args.n_mappings = 100
        args.grid = 10

    print()
    print("═" * 65)
    print("  매핑 독립성 검증 시작")
    print("═" * 65)
    print()

    all_best_i, all_has_gap, all_mapping_type = run_experiment(
        n_mappings=args.n_mappings,
        grid=args.grid,
        steps=args.steps,
        dt=args.dt,
        seed=args.seed,
    )

    analyze_and_report(all_best_i, all_has_gap, all_mapping_type)


if __name__ == "__main__":
    main()
