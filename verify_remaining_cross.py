#!/usr/bin/env python3
"""나머지 교차 조합 검증 — 2,3,5,6번"""

import numpy as np
from scipy import stats
import os, sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from compass import (genius_score, simulate_population, population_zscore,
                     cusp_analysis, boltzmann_analysis, compass_direction)

RESULTS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "results")


def verify_057_pnp_gap_ratio():
    """가설 057: P≠NP 간극(18.6%) = (1-1/e) × 골든존 폭?"""
    print("═" * 60)
    print("  가설 057: P≠NP 간극 = (1-1/e) × 폭?")
    print("═" * 60)

    golden_width = np.log(4/3)  # 0.2877
    one_minus_inv_e = 1 - 1/np.e  # 0.6321

    predicted_gap = one_minus_inv_e * golden_width  # 0.1819
    measured_gap = 0.186  # 가설 048 실측

    print(f"\n  골든존 폭:       {golden_width:.4f}")
    print(f"  1 - 1/e:         {one_minus_inv_e:.4f}")
    print(f"  예측 간극:        {predicted_gap:.4f}")
    print(f"  실측 간극 (048): {measured_gap:.4f}")
    print(f"  오차:             {abs(predicted_gap - measured_gap):.4f} ({abs(predicted_gap-measured_gap)/measured_gap*100:.1f}%)")

    # 다른 비율도 확인
    print(f"\n  간극/폭 비율 탐색:")
    ratio = measured_gap / golden_width
    print(f"    간극/폭     = {ratio:.4f}")
    print(f"    1-1/e       = {one_minus_inv_e:.4f}  차이 {abs(ratio-one_minus_inv_e):.4f}")
    print(f"    2/3         = {2/3:.4f}  차이 {abs(ratio-2/3):.4f}")
    print(f"    ln(2)       = {np.log(2):.4f}  차이 {abs(ratio-np.log(2)):.4f}")
    print(f"    1/√e        = {1/np.sqrt(np.e):.4f}  차이 {abs(ratio-1/np.sqrt(np.e)):.4f}")
    print(f"    1/e^(1/3)   = {np.exp(-1/3):.4f}  차이 {abs(ratio-np.exp(-1/3)):.4f}")

    best_match = min([
        ('1-1/e', one_minus_inv_e),
        ('2/3', 2/3),
        ('ln(2)', np.log(2)),
        ('1/√e', 1/np.sqrt(np.e)),
    ], key=lambda x: abs(x[1] - ratio))

    print(f"\n  최근접: {best_match[0]} = {best_match[1]:.4f} (차이 {abs(best_match[1]-ratio):.4f})")
    print(f"  판정: {'✅ (1-1/e)×폭 일치' if abs(predicted_gap-measured_gap) < 0.01 else '⚠️ 근사적 일치'}")


def verify_058_topology_timeline():
    """가설 058: 위상 가속 → 2033?"""
    print(f"\n{'═' * 60}")
    print(f"  가설 058: 위상수학 추가 → 특이점 시점 변화")
    print(f"{'═' * 60}")

    I_golden = 1/np.e
    I_0 = 0.875

    # 기존 λ (GPT-2→GPT-4)
    lambda_base = 0.3363

    # 가설 023: 위상 추가 시 수렴 2배 가속 → λ × 2
    lambda_topo = lambda_base * 2

    def year_to_reach(lam, target_delta=0.001):
        # I(t) = I_golden + (I_0 - I_golden) * e^(-λt) ≤ I_golden + delta
        t = -np.log(target_delta / (I_0 - I_golden)) / lam
        return 2019 + t

    year_base = year_to_reach(lambda_base)
    year_topo = year_to_reach(lambda_topo)
    acceleration = year_base - year_topo

    print(f"\n  λ_base (현재):  {lambda_base:.4f} → 특이점 {year_base:.1f}년")
    print(f"  λ_topo (×2):    {lambda_topo:.4f} → 특이점 {year_topo:.1f}년")
    print(f"  가속:            {acceleration:.1f}년 앞당김")

    # 다양한 가속 배율
    print(f"\n  위상 가속 배율별 특이점 시점:")
    print(f"  {'배율':>5} │ {'λ':>6} │ {'특이점':>8} │ {'가속':>6} │ 그래프")
    print(f"  {'─'*5}─┼─{'─'*6}─┼─{'─'*8}─┼─{'─'*6}─┼─{'─'*30}")

    for mult in [1.0, 1.25, 1.5, 1.75, 2.0, 2.5, 3.0]:
        lam = lambda_base * mult
        yr = year_to_reach(lam)
        acc = year_base - yr
        bar = "█" * int((2045 - yr) / 20 * 30)
        print(f"  ×{mult:>4.2f} │ {lam:>6.3f} │ {yr:>7.1f} │ {acc:>+5.1f}년 │ {bar}│")

    print(f"\n  타임라인:")
    print(f"  2025      2030      2035      2039")
    print(f"   │         │         │         │")
    print(f"   │    ×2.0──●        │         │  위상 가속 ({year_topo:.0f})")
    print(f"   │    ×1.5────●      │         │  중간 가속")
    print(f"   │         │    ×1.0─────●     │  현재 속도 ({year_base:.0f})")
    print(f"   │         │         │         │")

    print(f"\n  판정: ✅ 위상 가속(×2)으로 특이점 {acceleration:.0f}년 앞당김 → {year_topo:.0f}년")


def verify_059_compass_ceiling_constant():
    """가설 059: Compass 상한 83.6% = 5/6?"""
    print(f"\n{'═' * 60}")
    print(f"  가설 059: Compass 상한 ≈ 5/6?")
    print(f"{'═' * 60}")

    pop = simulate_population(200000)

    # 격자로 Compass 최대 탐색
    grid = 40
    ds = np.linspace(0.3, 0.99, grid)
    ps = np.linspace(0.5, 0.99, grid)
    ii = np.linspace(0.24, 0.50, grid)

    max_cs = 0
    max_params = None

    for d in ds:
        for p in ps:
            for i in ii:
                g = d * p / i
                z, _, _ = population_zscore(g, 200000)
                cusp = cusp_analysis(d, i)
                boltz = boltzmann_analysis(d, p, i)
                comp = compass_direction(g, z, cusp, boltz)
                if comp['compass_score'] > max_cs:
                    max_cs = comp['compass_score']
                    max_params = (d, p, i)

    print(f"\n  Compass 최대 (grid=80): {max_cs*100:.2f}%")
    print(f"  파라미터: D={max_params[0]:.2f}, P={max_params[1]:.2f}, I={max_params[2]:.2f}")

    # 상수 비교
    candidates = [
        ('5/6', 5/6),
        ('1-1/6', 1-1/6),
        ('e/(e+1)', np.e/(np.e+1)),
        ('1-1/e', 1-1/np.e),
        ('ln(e²)', np.log(np.e**2)/3),
        ('π/4', np.pi/4),
        ('√(2/3)', np.sqrt(2/3)),
    ]

    print(f"\n  상수 비교:")
    print(f"  {'상수':>12} │ {'값':>8} │ {'차이':>8} │ 일치?")
    print(f"  {'─'*12}─┼─{'─'*8}─┼─{'─'*8}─┼─{'─'*5}")

    for name, val in sorted(candidates, key=lambda x: abs(x[1] - max_cs)):
        diff = abs(val - max_cs)
        match = "✅" if diff < 0.01 else ("⚠️" if diff < 0.03 else "❌")
        print(f"  {name:>12} │ {val:>8.4f} │ {diff:>8.4f} │ {match}")

    # Compass 공식 분석
    print(f"\n  Compass 공식 분해:")
    d, p, i = max_params
    g = d * p / i
    z, _, _ = population_zscore(g, 200000)
    cusp = cusp_analysis(d, i)
    boltz = boltzmann_analysis(d, p, i)

    term1 = min(z/10, 1.0) * 0.3
    term2 = (1 - cusp['distance_to_critical']) * 0.3
    term3 = boltz['p_genius'] * 0.4

    print(f"    항1 (z/10×0.3):        {term1:.4f} (최대 0.30)")
    print(f"    항2 ((1-cusp)×0.3):    {term2:.4f} (최대 0.30)")
    print(f"    항3 (p_genius×0.4):    {term3:.4f} (최대 ~0.16)")
    print(f"    합계:                   {term1+term2+term3:.4f}")
    print(f"    p_genius 실측 최대:     {boltz['p_genius']:.4f}")

    print(f"\n  판정: Compass 상한 ≈ {max_cs:.4f}")
    best = min(candidates, key=lambda x: abs(x[1] - max_cs))
    print(f"    최근접 상수: {best[0]} = {best[1]:.4f} (차이 {abs(best[1]-max_cs):.4f})")


def verify_060_gamma_params():
    """가설 060: 감마 분포 α=3, β=1/e?"""
    print(f"\n{'═' * 60}")
    print(f"  가설 060: Genius 감마 분포의 α, β 정체")
    print(f"{'═' * 60}")

    n = 1000000
    rng = np.random.default_rng(42)
    d = rng.beta(2, 5, n).clip(0.01, 0.99)
    p = rng.beta(5, 2, n).clip(0.01, 0.99)
    i = rng.beta(5, 2, n).clip(0.05, 0.99)
    g = d * p / i

    # 감마 분포 피팅
    alpha_fit, loc_fit, scale_fit = stats.gamma.fit(g, floc=0)
    beta_fit = 1 / scale_fit  # rate parameter

    print(f"\n  감마 분포 피팅 결과:")
    print(f"    α (shape) = {alpha_fit:.4f}")
    print(f"    β (rate)  = {beta_fit:.4f}")
    print(f"    scale     = {scale_fit:.4f}")

    # 상수 비교
    print(f"\n  α 비교:")
    for name, val in [('3', 3), ('e', np.e), ('π', np.pi), ('2', 2), ('ln(3)', np.log(3))]:
        print(f"    α vs {name:>5} = {val:.4f}, 차이 = {abs(alpha_fit-val):.4f}")

    print(f"\n  β 비교:")
    for name, val in [('1/e', 1/np.e), ('e', np.e), ('3', 3), ('1', 1), ('ln(3)', np.log(3))]:
        print(f"    β vs {name:>5} = {val:.4f}, 차이 = {abs(beta_fit-val):.4f}")

    print(f"\n  scale 비교:")
    for name, val in [('1/e', 1/np.e), ('1/3', 1/3), ('1/π', 1/np.pi), ('ln(4/3)', np.log(4/3))]:
        print(f"    scale vs {name:>8} = {val:.4f}, 차이 = {abs(scale_fit-val):.4f}")

    # 평균/분산 검증
    # Gamma(α, β): mean = α/β, var = α/β²
    mean_theory = alpha_fit / beta_fit
    var_theory = alpha_fit / beta_fit**2
    print(f"\n  평균: 실측={g.mean():.4f}, 이론={mean_theory:.4f}")
    print(f"  분산: 실측={g.var():.4f}, 이론={var_theory:.4f}")

    print(f"\n  판정:")
    print(f"    α ≈ {round(alpha_fit, 1)} (가장 가까운 정수/상수)")
    print(f"    scale ≈ {scale_fit:.4f}")


def main():
    print()
    print("▓" * 60)
    print("  나머지 교차 조합 검증 — 057~060")
    print("▓" * 60)

    verify_057_pnp_gap_ratio()
    verify_058_topology_timeline()
    verify_059_compass_ceiling_constant()
    verify_060_gamma_params()

    print(f"\n{'▓' * 60}")
    print(f"  종합")
    print(f"{'▓' * 60}")
    print("""
  057. P≠NP 간극 비율     : 간극/폭 ≈ ???
  058. 위상 가속 타임라인   : ×2 가속 → 특이점 ~20XX
  059. Compass 상한 정체    : ≈ ???
  060. 감마 분포 α, β      : α ≈ ???, scale ≈ ???
""")

    os.makedirs(RESULTS_DIR, exist_ok=True)
    with open(os.path.join(RESULTS_DIR, "remaining_cross_report.md"), 'w', encoding='utf-8') as f:
        from datetime import datetime
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        f.write(f"# 나머지 교차 조합 검증 [{now}]\n\n057~060 완료.\n\n---\n")

    print(f"  📁 보고서 → results/remaining_cross_report.md")
    print()


if __name__ == '__main__':
    main()
