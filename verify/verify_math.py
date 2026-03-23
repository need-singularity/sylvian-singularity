#!/usr/bin/env python3
"""미검증 수학 가설 검증"""

import numpy as np
from scipy import stats, integrate
from scipy.special import beta as beta_func
import os
from datetime import datetime

RESULTS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "results")


def verify_one_third_law():
    """가설 A: 1/3 법칙의 해석적 검증"""
    print("═" * 60)
    print("  가설 A: 1/3 법칙 해석적 검증")
    print("═" * 60)

    # 모집단 통계 (Beta 분포 기반)
    samples = [10000, 50000, 200000, 1000000]
    results = []

    for n in samples:
        rng = np.random.default_rng(42)
        d = rng.beta(2, 5, n).clip(0.01, 0.99)
        p = rng.beta(5, 2, n).clip(0.01, 0.99)
        i = rng.beta(5, 2, n).clip(0.05, 0.99)
        g = d * p / i
        mu, sigma = g.mean(), g.std()
        threshold = mu + 2 * sigma

        # 균등 격자에서 비율 계산
        grid = 100
        ds = np.linspace(0.01, 0.99, grid)
        ps = np.linspace(0.01, 0.99, grid)
        ii = np.linspace(0.05, 0.99, grid)
        D, P, I = np.meshgrid(ds, ps, ii, indexing='ij')
        G = D * P / I
        ratio = (G > threshold).sum() / G.size

        results.append({'n': n, 'mu': mu, 'sigma': sigma, 'threshold': threshold, 'ratio': ratio})
        print(f"  n={n:>10,}: μ={mu:.4f}, σ={sigma:.4f}, 임계={threshold:.4f}, 비율={ratio:.4f} ({ratio*100:.2f}%)")

    # 수렴 분석
    ratios = [r['ratio'] for r in results]
    print(f"\n  수렴값: {ratios[-1]:.6f}")
    print(f"  1/3   : {1/3:.6f}")
    print(f"  오차  : {abs(ratios[-1] - 1/3):.6f} ({abs(ratios[-1] - 1/3)/( 1/3)*100:.2f}%)")

    is_one_third = abs(ratios[-1] - 1/3) < 0.01
    print(f"\n  판정: {'✅ 1/3에 근사' if is_one_third else '❌ 1/3 아님'} (오차 {abs(ratios[-1]-1/3)*100:.2f}%)")
    return ratios[-1]


def verify_z_max():
    """가설 B: Z-Score 상한 수렴값"""
    print("\n" + "═" * 60)
    print("  가설 B: Z-Score 상한 수렴값")
    print("═" * 60)

    samples_list = [10000, 50000, 200000, 1000000]
    z_maxes = []

    for n in samples_list:
        rng = np.random.default_rng(42)
        d = rng.beta(2, 5, n).clip(0.01, 0.99)
        p = rng.beta(5, 2, n).clip(0.01, 0.99)
        i = rng.beta(5, 2, n).clip(0.05, 0.99)
        g = d * p / i
        mu, sigma = g.mean(), g.std()

        # 이론적 최대: D=0.99, P=0.99, I=0.05
        g_max = 0.99 * 0.99 / 0.05
        z_max = (g_max - mu) / sigma
        z_maxes.append(z_max)
        print(f"  n={n:>10,}: G_max={g_max:.2f}, Z_max={z_max:.2f}σ")

    print(f"\n  이론적 G_max = 0.99×0.99/0.05 = {0.99*0.99/0.05:.2f}")
    print(f"  Z_max 수렴값 ≈ {z_maxes[-1]:.2f}σ")
    print(f"  80σ와의 차이: {abs(z_maxes[-1] - 80):.2f}")
    print(f"  = G_max/σ ≈ {0.99*0.99/0.05:.2f}/σ")
    return z_maxes[-1]


def verify_entropy_ln3():
    """가설 C: 엔트로피 = ln(3) 불변"""
    print("\n" + "═" * 60)
    print("  가설 C: 엔트로피 = ln(3) 불변")
    print("═" * 60)

    ln3 = np.log(3)
    print(f"  ln(3) = {ln3:.6f}\n")

    test_params = [
        (0.3, 0.5, 0.7),
        (0.7, 0.8, 0.15),
        (0.5, 0.6, 0.36),
        (0.9, 0.95, 0.05),
        (0.1, 0.1, 0.9),
        (0.5, 0.5, 0.5),
        (0.8, 0.9, 0.30),
        (0.2, 0.3, 0.8),
    ]

    entropies = []
    print(f"  {'D':>5} {'P':>5} {'I':>5} │ {'엔트로피':>8} │ {'ln(3)과 차이':>12} │ {'일치?':>5}")
    print(f"  {'─'*5} {'─'*5} {'─'*5}─┼─{'─'*8}─┼─{'─'*12}─┼─{'─'*5}")

    for d, p, i in test_params:
        T = 1.0 / max(i, 0.01)
        E_normal = 0.0
        E_genius = -(d * p)
        E_decline = d * (1 - p)
        energies = np.array([E_normal, E_genius, E_decline])
        exp_terms = np.exp(-energies / T)
        Z = exp_terms.sum()
        probs = exp_terms / Z
        entropy = -np.sum(probs * np.log(probs + 1e-10))
        entropies.append(entropy)
        diff = abs(entropy - ln3)
        match = "✅" if diff < 0.01 else "❌"
        print(f"  {d:>5.2f} {p:>5.2f} {i:>5.2f} │ {entropy:>8.6f} │ {diff:>12.6f} │ {match:>5}")

    mean_s = np.mean(entropies)
    std_s = np.std(entropies)
    print(f"\n  평균 엔트로피: {mean_s:.6f} ± {std_s:.6f}")
    print(f"  ln(3)       : {ln3:.6f}")
    print(f"  평균 오차    : {abs(mean_s - ln3):.6f}")

    # 대규모 검증: 랜덤 파라미터 1000개
    rng = np.random.default_rng(42)
    ds = rng.uniform(0.01, 0.99, 10000)
    ps = rng.uniform(0.01, 0.99, 10000)
    ii = rng.uniform(0.01, 0.99, 10000)

    all_entropies = []
    for d, p, i in zip(ds, ps, ii):
        T = 1.0 / max(i, 0.01)
        energies = np.array([0.0, -(d*p), d*(1-p)])
        exp_terms = np.exp(-energies / T)
        Z = exp_terms.sum()
        probs = exp_terms / Z
        s = -np.sum(probs * np.log(probs + 1e-10))
        all_entropies.append(s)

    all_entropies = np.array(all_entropies)
    print(f"\n  대규모 검증 (10,000 랜덤 파라미터):")
    print(f"    평균: {all_entropies.mean():.6f}")
    print(f"    표준편차: {all_entropies.std():.6f}")
    print(f"    최소/최대: {all_entropies.min():.6f} / {all_entropies.max():.6f}")
    print(f"    ln(3)과 오차: {abs(all_entropies.mean() - ln3):.6f}")

    is_ln3 = abs(all_entropies.mean() - ln3) < 0.01
    is_invariant = all_entropies.std() < 0.05
    print(f"\n  판정:")
    print(f"    ln(3) 근사: {'✅' if is_ln3 else '❌'}")
    print(f"    불변량:     {'✅ (σ < 0.05)' if is_invariant else '❌ 변동 있음 (σ=' + f'{all_entropies.std():.4f})'}")
    return all_entropies.mean(), all_entropies.std()


def verify_diffusion():
    """가설 D: 수렴 속도 ∝ (ΔI)² — 확산 방정식"""
    print("\n" + "═" * 60)
    print("  가설 D: 수렴 속도 ∝ (ΔI)² 확산 법칙")
    print("═" * 60)

    # 실측 데이터
    data = [
        ('골든 MoE', 0.008, 3),
        ('GPT-4', 0.132, 8),
        ('Mixtral', 0.507, 21),
        ('GPT-2', 0.507, 39),
    ]

    print(f"\n  {'모델':12} │ {'ΔI':>6} │ {'ΔI²':>8} │ {'τ(실측)':>7} │ {'τ∝ΔI²':>7} │ {'τ∝ΔI':>6}")
    print(f"  {'─'*12}─┼─{'─'*6}─┼─{'─'*8}─┼─{'─'*7}─┼─{'─'*7}─┼─{'─'*6}")

    # ΔI² 모델 피팅 (골든 MoE 기준)
    base_di2 = data[0][1]**2
    base_tau = data[0][2]
    k_di2 = base_tau / max(base_di2, 1e-6)

    base_di = data[0][1]
    k_di = base_tau / max(base_di, 1e-6)

    errors_sq = []
    errors_lin = []

    for name, di, tau in data:
        tau_sq = k_di2 * di**2
        tau_lin = k_di * di
        err_sq = abs(tau - tau_sq) / tau * 100
        err_lin = abs(tau - tau_lin) / tau * 100
        errors_sq.append(err_sq)
        errors_lin.append(err_lin)
        print(f"  {name:12} │ {di:>6.3f} │ {di**2:>8.5f} │ {tau:>7} │ {tau_sq:>7.1f} │ {tau_lin:>6.1f}")

    print(f"\n  평균 오차:")
    print(f"    τ ∝ ΔI² (확산): {np.mean(errors_sq):.1f}%")
    print(f"    τ ∝ ΔI  (선형): {np.mean(errors_lin):.1f}%")

    # R² 계산
    dis = np.array([d[1] for d in data])
    taus = np.array([d[2] for d in data])

    # ΔI² 모델
    slope_sq, intercept_sq, r_sq, _, _ = stats.linregress(dis**2, taus)
    # ΔI 모델
    slope_lin, intercept_lin, r_lin, _, _ = stats.linregress(dis, taus)

    print(f"\n  R² (결정계수):")
    print(f"    τ vs ΔI² : R² = {r_sq**2:.4f}")
    print(f"    τ vs ΔI  : R² = {r_lin**2:.4f}")

    better = "확산 (ΔI²)" if r_sq**2 > r_lin**2 else "선형 (ΔI)"
    print(f"\n  판정: {better} 모델이 더 적합 (R²={max(r_sq**2, r_lin**2):.4f})")
    return r_sq**2, r_lin**2


def verify_golden_width():
    """가설 E: 골든 존 폭 = 정확히 1/4"""
    print("\n" + "═" * 60)
    print("  가설 E: 골든 존 폭 = 1/4, 상한/하한 = 2")
    print("═" * 60)

    # 다양한 격자 해상도에서 골든 존 경계 측정
    grids = [20, 30, 50, 80]
    results = []

    for grid in grids:
        n_samples = 50000
        rng = np.random.default_rng(42)
        pop_d = rng.beta(2, 5, n_samples).clip(0.01, 0.99)
        pop_p = rng.beta(5, 2, n_samples).clip(0.01, 0.99)
        pop_i = rng.beta(5, 2, n_samples).clip(0.05, 0.99)
        pop_g = pop_d * pop_p / pop_i
        pop_mean, pop_std = pop_g.mean(), pop_g.std()

        deficits = np.linspace(0.05, 0.95, grid)
        plasticities = np.linspace(0.1, 0.95, grid)
        inhibitions = np.linspace(0.05, 0.95, grid)

        # 3중 합의 영역의 I 범위 측정
        triple_is = []
        for di in deficits:
            for pi in plasticities:
                for ii in inhibitions:
                    g = di * pi / ii
                    z = (g - pop_mean) / pop_std

                    # 3중 합의 조건 (간소화)
                    a = 2 * di - 1
                    b = 1 - 2 * ii
                    cusp_dist = abs(8*a**3 + 27*b**2) / 35
                    m1 = abs(z) > 2.0
                    m2 = cusp_dist < 0.2 and b > 0
                    T = 1.0 / max(ii, 0.01)
                    energies = np.array([0.0, -(di*pi), di*(1-pi)])
                    exp_terms = np.exp(-energies / T)
                    Z_part = exp_terms.sum()
                    probs = exp_terms / Z_part
                    m3 = probs[1] > probs[0] and probs[1] > probs[2]

                    if m1 and m2 and m3:
                        triple_is.append(ii)

        if triple_is:
            i_min = min(triple_is)
            i_max = max(triple_is)
            width = i_max - i_min
            ratio = i_max / i_min if i_min > 0 else float('inf')
            results.append({'grid': grid, 'i_min': i_min, 'i_max': i_max, 'width': width, 'ratio': ratio})
            print(f"  grid={grid:>3}: I=[{i_min:.4f}, {i_max:.4f}], 폭={width:.4f}, 상한/하한={ratio:.4f}")

    if results:
        avg_width = np.mean([r['width'] for r in results])
        avg_ratio = np.mean([r['ratio'] for r in results])
        print(f"\n  평균 폭: {avg_width:.4f}")
        print(f"  1/4   : {0.25:.4f}")
        print(f"  오차  : {abs(avg_width - 0.25):.4f}")
        print(f"\n  평균 상한/하한 비: {avg_ratio:.4f}")
        print(f"  2.0과 차이       : {abs(avg_ratio - 2.0):.4f}")

        is_quarter = abs(avg_width - 0.25) < 0.03
        is_double = abs(avg_ratio - 2.0) < 0.3
        print(f"\n  판정:")
        print(f"    폭 = 1/4: {'✅' if is_quarter else '❌'} (오차 {abs(avg_width-0.25):.4f})")
        print(f"    비 = 2  : {'✅' if is_double else '❌'} (오차 {abs(avg_ratio-2.0):.4f})")
    return results


def verify_genius_distribution():
    """가설 G: Genius Score 분포 판별"""
    print("\n" + "═" * 60)
    print("  가설 G: Genius Score 분포 판별")
    print("═" * 60)

    n = 1000000
    rng = np.random.default_rng(42)
    d = rng.beta(2, 5, n).clip(0.01, 0.99)
    p = rng.beta(5, 2, n).clip(0.01, 0.99)
    i = rng.beta(5, 2, n).clip(0.05, 0.99)
    g = d * p / i

    print(f"\n  G = D×P/I 분포 (n={n:,})")
    print(f"  평균: {g.mean():.4f}")
    print(f"  표준편차: {g.std():.4f}")
    print(f"  왜도(skewness): {stats.skew(g):.4f}")
    print(f"  첨도(kurtosis): {stats.kurtosis(g):.4f}")
    print(f"  최소/최대: {g.min():.4f} / {g.max():.4f}")

    # 분포 피팅 테스트
    distributions = {
        'lognormal': stats.lognorm,
        'gamma': stats.gamma,
        'beta_prime': stats.betaprime,
        'f': stats.f,
        'invgamma': stats.invgamma,
    }

    print(f"\n  분포 피팅 (KS 검정):")
    print(f"  {'분포':15} │ {'KS 통계량':>10} │ {'p-value':>10} │ 판정")
    print(f"  {'─'*15}─┼─{'─'*10}─┼─{'─'*10}─┼─{'─'*10}")

    best_name = ""
    best_pval = 0
    g_sample = rng.choice(g, 5000, replace=False)  # KS 검정용 서브샘플

    for name, dist in distributions.items():
        try:
            params = dist.fit(g_sample)
            ks_stat, p_val = stats.kstest(g_sample, dist.cdf, args=params)
            match = "✅" if p_val > 0.05 else "❌"
            print(f"  {name:15} │ {ks_stat:>10.4f} │ {p_val:>10.6f} │ {match}")
            if p_val > best_pval:
                best_pval = p_val
                best_name = name
        except Exception as e:
            print(f"  {name:15} │ {'실패':>10} │ {'─':>10} │ {str(e)[:20]}")

    print(f"\n  최적 분포: {best_name} (p={best_pval:.6f})")

    # 히스토그램 ASCII
    print(f"\n  분포 형태:")
    hist, edges = np.histogram(g, bins=40, range=(0, 3))
    max_h = hist.max()
    for i in range(len(hist)):
        bar = "█" * int(hist[i] / max_h * 40)
        print(f"  {edges[i]:>5.2f} │{bar}")

    return best_name, best_pval


def main():
    print()
    print("▓" * 60)
    print("  수학적 미검증 가설 일괄 검증")
    print("▓" * 60)

    results = {}

    results['A'] = verify_one_third_law()
    results['B'] = verify_z_max()
    results['C'] = verify_entropy_ln3()
    results['D'] = verify_diffusion()
    results['E'] = verify_golden_width()
    results['G'] = verify_genius_distribution()

    # 종합
    print("\n" + "▓" * 60)
    print("  종합 판정")
    print("▓" * 60)

    print(f"""
  A. 1/3 법칙        : 비율 = {results['A']:.4f} ({'✅ 근사' if abs(results['A']-1/3)<0.01 else '❌'})
  B. Z_max 수렴      : {results['B']:.2f}σ
  C. 엔트로피 = ln(3): 평균 = {results['C'][0]:.4f}, σ = {results['C'][1]:.4f} ({'✅' if results['C'][1]<0.05 else '❌ 변동'})
  D. 확산 법칙       : R²(ΔI²) = {results['D'][0]:.4f}, R²(ΔI) = {results['D'][1]:.4f}
  E. 폭 = 1/4       : 측정 중
  G. Genius 분포     : {results['G'][0]} (p={results['G'][1]:.6f})
""")

    # 보고서 저장
    os.makedirs(RESULTS_DIR, exist_ok=True)
    with open(os.path.join(RESULTS_DIR, "math_verification.md"), 'w', encoding='utf-8') as f:
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        f.write(f"# 수학적 미검증 가설 검증 결과 [{now}]\n\n")
        f.write(f"| 가설 | 결과 |\n|---|---|\n")
        f.write(f"| A. 1/3 법칙 | {results['A']:.4f} |\n")
        f.write(f"| B. Z_max | {results['B']:.2f}σ |\n")
        f.write(f"| C. 엔트로피 | {results['C'][0]:.4f} ± {results['C'][1]:.4f} |\n")
        f.write(f"| D. 확산 R² | ΔI²={results['D'][0]:.4f}, ΔI={results['D'][1]:.4f} |\n")
        f.write(f"| G. 분포 | {results['G'][0]} |\n")

    print(f"  📁 검증 결과 → results/math_verification.md")
    print()


if __name__ == '__main__':
    main()
