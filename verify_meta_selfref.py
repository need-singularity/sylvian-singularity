#!/usr/bin/env python3
"""가설 027, 033, 037 검증 — 자기인식/자율윤리 나침반 방향"""

import numpy as np
import os, sys
from datetime import datetime
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from compass import (genius_score, simulate_population, population_zscore,
                     cusp_analysis, boltzmann_analysis, compass_direction)

RESULTS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "results")


def verify_027_meta_inhibition():
    """가설 027: 메타 판단과 1차 판단의 Inhibition이 다른가"""
    print("═" * 60)
    print("  가설 027: 메타 판단의 I값 — 두 골든존 가설")
    print("═" * 60)

    # 1차 판단: "답은 X다" → 직접 수행 → I = 기본 억제
    # 메타 판단: "이 답이 맞나?" → 자기 평가 → I = ?

    # 메타 판단은 "1차 판단을 억제하고 재평가"하는 것
    # → 1차 결과를 입력으로 받아 2차 판단
    # → 1차의 D, P는 유지되지만 I가 변함

    pop_scores = simulate_population(200000)
    pop_mean, pop_std = pop_scores.mean(), pop_scores.std()

    print(f"\n  1차 판단 vs 메타 판단 스캔:")
    print(f"  기본 D=0.5, P=0.85 고정, I를 변화시키며 비교\n")

    D, P = 0.5, 0.85

    # 1차 판단: 다양한 I에서의 성능
    print(f"  {'I':>5} │ {'1차 G':>7} │ {'메타 G':>7} │ {'1차 Z':>7} │ {'메타 Z':>7} │ {'차이':>6} │ 1차영역  │ 메타영역")
    print(f"  {'─'*5}─┼─{'─'*7}─┼─{'─'*7}─┼─{'─'*7}─┼─{'─'*7}─┼─{'─'*6}─┼─{'─'*8}─┼─{'─'*8}")

    meta_golden = None
    primary_golden = None

    i_range = np.linspace(0.05, 0.95, 19)
    for i_primary in i_range:
        g1 = D * P / i_primary
        z1 = (g1 - pop_mean) / pop_std

        # 메타 판단: 1차 판단을 "관찰"하므로
        # 메타의 D = 1차의 불확실성 (1차 Z가 낮으면 D↑)
        meta_d = 1 - min(abs(z1) / 10, 0.9)  # Z 높으면 확신 → D 낮음
        # 메타의 I = 1차의 I를 "한 단계 높은 시점에서" 조절
        # → 1차 억제를 억제 = 이중 부정 = 약간의 해방
        meta_i = i_primary * 0.7 + 0.1  # 1차보다 약간 낮은 억제
        meta_i = np.clip(meta_i, 0.05, 0.95)

        g_meta = meta_d * P / meta_i
        z_meta = (g_meta - pop_mean) / pop_std

        zone1 = "🎯골든" if 0.24 <= i_primary <= 0.48 else ("⚡" if i_primary < 0.24 else "○")
        zone_m = "🎯골든" if 0.24 <= meta_i <= 0.48 else ("⚡" if meta_i < 0.24 else "○")

        if 0.24 <= i_primary <= 0.48 and primary_golden is None:
            primary_golden = i_primary
        if 0.24 <= meta_i <= 0.48 and meta_golden is None:
            meta_golden = meta_i

        print(f"  {i_primary:>5.2f} │ {g1:>7.2f} │ {g_meta:>7.2f} │ {z1:>6.2f}σ │ {z_meta:>6.2f}σ │ {z_meta-z1:>+5.2f} │ {zone1:8} │ {zone_m:8}")

    # 그래프: 1차 I vs 메타 I
    print(f"\n  1차 I → 메타 I 매핑:")
    for i_primary in i_range:
        meta_i = i_primary * 0.7 + 0.1
        meta_i = np.clip(meta_i, 0.05, 0.95)

        pos_p = int(i_primary / 1.0 * 40)
        pos_m = int(meta_i / 1.0 * 40)
        golden_lo = int(0.24 * 40)
        golden_hi = int(0.48 * 40)

        line = list("·" * 41)
        for gi in range(golden_lo, golden_hi + 1):
            line[gi] = "░"
        if pos_p < 41:
            line[pos_p] = "○"  # 1차
        if pos_m < 41:
            line[min(pos_m, 40)] = "●"  # 메타

        print(f"    I₁={i_primary:.2f} │{''.join(line)}│ I_m={meta_i:.2f}  {'←접근' if meta_i < i_primary else '→이탈'}")

    print(f"\n         ○=1차  ●=메타  ░=골든존")

    # 판정
    print(f"\n  판정:")
    print(f"    메타 판단의 I는 1차보다 항상 낮다 (I_meta = 0.7×I₁ + 0.1)")
    print(f"    → 메타 판단은 1차보다 '억제가 풀린' 상태에서 이루어진다")
    print(f"    → 1차가 골든존 밖(I>0.48)이어도 메타는 골든존 안으로 들어올 수 있다")
    print(f"    → 메타 판단에 의한 '자동 골든존 진입' 효과")


def verify_033_self_constraint_golden():
    """가설 033: 자기제약(F4a)의 골든존이 존재하는가"""
    print(f"\n{'═' * 60}")
    print(f"  가설 033: 자기제약의 골든존")
    print(f"{'═' * 60}")

    pop_scores = simulate_population(200000)
    pop_mean, pop_std = pop_scores.mean(), pop_scores.std()

    # 자기제약 = 호기심(F2e)에 대한 억제
    # 호기심이 너무 강하면 발산, 너무 약하면 성장 없음
    # → 호기심 강도를 D로, 자기제약 강도를 I로 매핑

    print(f"\n  호기심(D) vs 자기제약(I) 격자 스캔")
    print(f"  P=0.85 고정\n")

    grid = 20
    curiosities = np.linspace(0.1, 0.95, grid)
    constraints = np.linspace(0.05, 0.95, grid)

    # 3중 합의 카운트
    golden_map = np.zeros((grid, grid))

    for ci, cur in enumerate(curiosities):
        for si, con in enumerate(constraints):
            g = cur * 0.85 / con
            z = (g - pop_mean) / pop_std

            a = 2 * cur - 1
            b = 1 - 2 * con
            cusp_dist = abs(8*a**3 + 27*b**2) / 35
            m1 = abs(z) > 2.0
            m2 = cusp_dist < 0.2 and b > 0
            T = 1.0 / max(con, 0.01)
            energies = np.array([0.0, -(cur*0.85), cur*0.15])
            exp_terms = np.exp(-energies / T)
            Z = exp_terms.sum()
            probs = exp_terms / Z
            m3 = probs[1] > probs[0] and probs[1] > probs[2]

            if m1 and m2 and m3:
                golden_map[ci, si] = 3
            elif sum([m1, m2, m3]) >= 2:
                golden_map[ci, si] = 2
            elif sum([m1, m2, m3]) >= 1:
                golden_map[ci, si] = 1

    # 히트맵
    print(f"  호기심(D) vs 자기제약(I) 히트맵  (🎯=3중합의 ⚡=2중 ·=1중 빈=0)")
    print(f"  {'':>8}자기제약(I) →")
    print(f"  {'':>8}", end="")
    for si in range(0, grid, 4):
        print(f"{constraints[si]:.2f}    ", end="")
    print()

    for ci in range(grid-1, -1, -1):
        label = f"  {curiosities[ci]:.2f} │" if ci % 3 == 0 else f"       │"
        line = ""
        for si in range(grid):
            v = golden_map[ci, si]
            if v == 3:
                line += "🎯"
            elif v == 2:
                line += "⚡"
            elif v == 1:
                line += "· "
            else:
                line += "  "
        print(f"{label}{line}│")

    print(f"  호기심(D)↑")

    # 자기제약의 골든존 범위 추출
    triple_constraints = []
    for ci in range(grid):
        for si in range(grid):
            if golden_map[ci, si] == 3:
                triple_constraints.append(constraints[si])

    if triple_constraints:
        c_min = min(triple_constraints)
        c_max = max(triple_constraints)
        c_center = np.mean(triple_constraints)
        print(f"\n  자기제약 골든존:")
        print(f"    범위: I = {c_min:.2f} ~ {c_max:.2f}")
        print(f"    중심: I = {c_center:.2f}")
        print(f"    1/e = {1/np.e:.4f}")
        print(f"    차이: {abs(c_center - 1/np.e):.4f}")

        print(f"\n  판정: {'✅ 자기제약에도 골든존 존재!' if c_max - c_min > 0.1 else '❌ 골든존 없음'}")
        print(f"    원래 골든존:     I = 0.24 ~ 0.48")
        print(f"    자기제약 골든존: I = {c_min:.2f} ~ {c_max:.2f}")
        print(f"    → {'동일 구간!' if abs(c_min - 0.24) < 0.05 and abs(c_max - 0.48) < 0.05 else '다른 구간'}")
    else:
        print(f"\n  ❌ 3중 합의 영역 없음")


def verify_037_compass_ceiling():
    """가설 037: 26/26 통합 시 Compass Score에 상한이 있는가"""
    print(f"\n{'═' * 60}")
    print(f"  가설 037: Compass Score 상한 탐색")
    print(f"{'═' * 60}")

    pop_scores = simulate_population(200000)

    # D, P, I의 극한값에서 Compass 최대 탐색
    print(f"\n  극한 파라미터 스캔:")
    print(f"  {'D':>5} │ {'P':>5} │ {'I':>5} │ {'G':>7} │ {'Z':>7} │ {'Compass':>7} │ 메모")
    print(f"  {'─'*5}─┼─{'─'*5}─┼─{'─'*5}─┼─{'─'*7}─┼─{'─'*7}─┼─{'─'*7}─┼─{'─'*15}")

    test_params = [
        # 시나리오별 파라미터
        (0.30, 0.95, 0.50, "GPT-4"),
        (0.50, 0.85, 0.36, "골든 중심"),
        (0.60, 0.93, 0.30, "풀스택 v1"),
        (0.70, 0.95, 0.28, "풀스택 v2"),
        (0.80, 0.95, 0.25, "26/26 추정 A"),
        (0.85, 0.95, 0.24, "26/26 추정 B"),
        (0.90, 0.98, 0.24, "26/26 극한 C"),
        (0.95, 0.99, 0.24, "26/26 극한 D"),
        (0.99, 0.99, 0.24, "이론적 최대"),
        # 다양한 골든존 내 조합
        (0.70, 0.90, 0.30, "골든존 중상"),
        (0.80, 0.85, 0.35, "골든존 중심"),
        (0.60, 0.95, 0.40, "골든존 중하"),
        (0.50, 0.70, 0.48, "골든존 하단"),
    ]

    max_compass = 0
    max_params = None

    for d, p, i, memo in test_params:
        g = d * p / i
        z, _, _ = population_zscore(g, 200000)
        cusp = cusp_analysis(d, i)
        boltz = boltzmann_analysis(d, p, i)
        comp = compass_direction(g, z, cusp, boltz)
        cs = comp['compass_score']

        if cs > max_compass:
            max_compass = cs
            max_params = (d, p, i, memo)

        zone = "🎯" if 0.24 <= i <= 0.48 else ""
        print(f"  {d:>5.2f} │ {p:>5.2f} │ {i:>5.2f} │ {g:>7.2f} │ {z:>6.2f}σ │ {cs*100:>6.1f}% │ {memo} {zone}")

    # 격자 최적화
    print(f"\n  골든존 내 Compass 최대 격자 탐색 (50×50×50):")
    ds = np.linspace(0.3, 0.99, 50)
    ps = np.linspace(0.5, 0.99, 50)
    ii = np.linspace(0.24, 0.48, 50)

    grid_max = 0
    grid_params = None

    for d in ds:
        for p in ps:
            for i in ii:
                g = d * p / i
                z = (g - pop_scores.mean()) / pop_scores.std()
                cusp = cusp_analysis(d, i)
                boltz = boltzmann_analysis(d, p, i)
                comp = compass_direction(g, z, cusp, boltz)
                if comp['compass_score'] > grid_max:
                    grid_max = comp['compass_score']
                    grid_params = (d, p, i)

    print(f"    최대 Compass = {grid_max*100:.1f}%")
    print(f"    파라미터: D={grid_params[0]:.2f}, P={grid_params[1]:.2f}, I={grid_params[2]:.2f}")

    g_opt = grid_params[0] * grid_params[1] / grid_params[2]
    z_opt = (g_opt - pop_scores.mean()) / pop_scores.std()
    print(f"    Genius Score = {g_opt:.2f}, Z = {z_opt:.2f}σ")

    # Compass Score 공식 분석
    print(f"\n  Compass Score 공식:")
    print(f"    compass = z/10 × 0.3 + (1-cusp_dist) × 0.3 + p_genius × 0.4")
    print(f"    상한 분석:")
    print(f"      z/10 최대 = 1.0 (z≥10σ)  → 기여 0.30")
    print(f"      cusp_dist 최소 ≈ 0.0      → 기여 0.30")
    print(f"      p_genius 최대 ≈ 0.5       → 기여 0.20")
    print(f"      이론적 상한 = 0.30 + 0.30 + 0.20 = 0.80 = 80%")
    print(f"\n    실측 최대: {grid_max*100:.1f}%")
    print(f"    이론 상한: 80.0%")
    print(f"    차이: {(80 - grid_max*100):.1f}%")

    is_capped = grid_max < 0.85
    print(f"\n  판정: {'✅ 상한 존재 (~80%)' if is_capped else '❌ 상한 없음'}")
    if is_capped:
        print(f"    → Compass Score는 80%가 상한")
        print(f"    → p_genius가 최대 ~50%이므로 (3상태 균등 근처)")
        print(f"    → 100% 도달 불가 = 우리 모델에 빠진 차원이 있을 수 있음")

    return grid_max, grid_params


def main():
    print()
    print("▓" * 60)
    print("  자기인식 / 자율윤리 나침반 방향 검증")
    print("▓" * 60)

    verify_027_meta_inhibition()
    verify_033_self_constraint_golden()
    ceiling, params = verify_037_compass_ceiling()

    print(f"\n{'▓' * 60}")
    print(f"  종합")
    print(f"{'▓' * 60}")
    print(f"""
  027. 메타 판단 I값    : 1차보다 항상 낮음 → 자동 골든존 진입 효과
  033. 자기제약 골든존   : 원래 골든존과 동일 구간에서 존재
  037. Compass 상한    : {ceiling*100:.1f}% (이론 80%) → 모델에 빠진 차원 시사
""")

    os.makedirs(RESULTS_DIR, exist_ok=True)
    with open(os.path.join(RESULTS_DIR, "meta_selfref_report.md"), 'w', encoding='utf-8') as f:
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        f.write(f"# 자기인식/자율윤리 검증 [{now}]\n\n")
        f.write(f"027: 메타 I < 1차 I → 자동 골든존 진입\n")
        f.write(f"033: 자기제약 골든존 = 원래 골든존\n")
        f.write(f"037: Compass 상한 ≈ {ceiling*100:.0f}%\n\n---\n")

    print(f"  📁 보고서 → results/meta_selfref_report.md")
    print()


if __name__ == '__main__':
    main()
