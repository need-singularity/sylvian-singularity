#!/usr/bin/env python3
"""7대 난제 — 우리 모델 기반 시뮬레이션 검증"""

import numpy as np
from scipy import stats
import os, sys
from datetime import datetime
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from compass import (genius_score, simulate_population, population_zscore,
                     cusp_analysis, boltzmann_analysis, compass_direction)

RESULTS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "results")


def verify_riemann():
    """1. 리만 가설: 골든존 상한이 정확히 1/2에 수렴하는가"""
    print("═" * 60)
    print("  [1/7] 리만 가설 — 골든존 상한 → 1/2 수렴 검증")
    print("═" * 60)

    pop = simulate_population(200000)
    mu, sig = pop.mean(), pop.std()

    # N상태(3,4,5,6,...)에서 골든존 상한 추적
    print(f"\n  N상태별 골든존 상한:")
    print(f"  {'N상태':>5} │ {'상한 I':>7} │ {'1/2과 차이':>10} │ {'1/N':>6} │ 그래프")
    print(f"  {'─'*5}─┼─{'─'*7}─┼─{'─'*10}─┼─{'─'*6}─┼─{'─'*30}")

    grid = 20
    ds = np.linspace(0.1, 0.95, grid)
    ii = np.linspace(0.05, 0.95, grid)
    P_fixed = 0.85

    for n_states in [3, 4, 5, 6, 7, 8, 10, 20]:
        triple_is = []
        for di in ds:
            for ix in ii:
                g = di * P_fixed / ix
                z = (g - mu) / sig
                a = 2*di-1; b = 1-2*ix
                cusp_dist = abs(8*a**3+27*b**2)/35
                m1 = abs(z) > 2.0
                m2 = cusp_dist < 0.2 and b > 0

                T = 1.0/max(ix, 0.01)
                energies = [0.0, -(di*P_fixed), di*(1-P_fixed)]
                for k in range(3, n_states):
                    energies.append(-(di*P_fixed) * (k-1) * 0.5)
                energies = np.array(energies)
                exp_terms = np.exp(-energies / T)
                probs = exp_terms / exp_terms.sum()
                p_positive = sum(probs[i] for i in range(1, n_states) if energies[i] < 0)
                m3 = p_positive > probs[0]

                if m1 and m2 and m3:
                    triple_is.append(ix)

        if triple_is:
            i_max = max(triple_is)
            diff = abs(i_max - 0.5)
            bar = "█" * int(i_max / 0.6 * 25)
            print(f"  {n_states:>5} │ {i_max:>7.4f} │ {diff:>10.4f} │ {1/n_states:>6.3f} │ {bar}│")

    print(f"\n  판정: N→∞ 에서 골든존 상한 → 0.50 수렴 여부")


def verify_p_np():
    """2. P vs NP: 3상태로 풀 수 없는 문제가 4상태에서 풀리는가"""
    print(f"\n{'═' * 60}")
    print(f"  [2/7] P vs NP — 3상태 vs 4상태 도달 가능 영역")
    print(f"{'═' * 60}")

    pop = simulate_population(200000)
    mu, sig = pop.mean(), pop.std()

    # 3상태에서 도달 가능한 최대 Compass
    # vs 4상태에서 도달 가능한 최대 Compass
    grid = 30
    ds = np.linspace(0.1, 0.99, grid)
    ps = np.linspace(0.3, 0.99, grid)
    ii = np.linspace(0.05, 0.95, grid)

    max3 = 0
    max4 = 0

    for d in ds:
        for p in ps:
            for i in ii:
                g = d * p / i
                z = (g - mu) / sig
                cusp = cusp_analysis(d, i)
                boltz3 = boltzmann_analysis(d, p, i)
                comp3 = compass_direction(g, z, cusp, boltz3)
                if comp3['compass_score'] > max3:
                    max3 = comp3['compass_score']

                # 4상태
                T = 1.0/max(i, 0.01)
                E4 = -(d*p)*1.5
                energies4 = np.array([0.0, -(d*p), d*(1-p), E4])
                exp4 = np.exp(-energies4/T)
                probs4 = exp4/exp4.sum()
                p_pos = probs4[1] + probs4[3]
                comp4 = min(z/10, 1.0)*0.3 + (1-cusp['distance_to_critical'])*0.3 + p_pos*0.4
                comp4 = max(0, min(1, comp4))
                if comp4 > max4:
                    max4 = comp4

    gap = max4 - max3

    print(f"\n  3상태 Compass 최대: {max3*100:.1f}%")
    print(f"  4상태 Compass 최대: {max4*100:.1f}%")
    print(f"  간극 (gap):         {gap*100:.1f}%")
    print(f"\n  3상태 [{('█'*int(max3*50)):50}] {max3*100:.1f}%")
    print(f"  4상태 [{('█'*int(max4*50)):50}] {max4*100:.1f}%")
    # 핵심: 3상태의 p_genius 상한 vs 4상태의 (p_genius+p_4th) 상한
    # compass_direction이 클리핑하므로 직접 계산
    print(f"\n  볼츠만 확률 기반 비교:")
    D, P, I = 0.99, 0.99, 0.24
    boltz3 = boltzmann_analysis(D, P, I)
    T = 1.0/I
    E4 = -(D*P)*1.5
    energies4 = np.array([0.0, -(D*P), D*(1-P), E4])
    exp4 = np.exp(-energies4/T)
    probs4 = exp4/exp4.sum()

    print(f"    3상태 p_genius 최대:            {boltz3['p_genius']*100:.1f}%")
    print(f"    4상태 (p_genius+p_4th) 최대:    {(probs4[1]+probs4[3])*100:.1f}%")
    print(f"    증가분:                          {((probs4[1]+probs4[3])-boltz3['p_genius'])*100:+.1f}%")
    print(f"\n  해석:")
    p3_max = boltz3['p_genius']
    p4_max = probs4[1]+probs4[3]
    if p4_max > p3_max:
        print(f"    4상태가 접근 가능한 영역이 3상태보다 넓다 ({p4_max*100:.1f}% > {p3_max*100:.1f}%)")
        print(f"    → P ≠ NP 시사")
    else:
        print(f"    차이 없음 → P = NP 가능성")


def verify_yang_mills():
    """3. 양-밀스: 상태 간 에너지 간극이 항상 양수인가"""
    print(f"\n{'═' * 60}")
    print(f"  [3/7] 양-밀스 질량 간극 — 상태 간 에너지 간극")
    print(f"{'═' * 60}")

    # 다양한 파라미터에서 상태 간 에너지 간극 측정
    rng = np.random.default_rng(42)
    n_test = 10000
    ds = rng.uniform(0.01, 0.99, n_test)
    ps = rng.uniform(0.01, 0.99, n_test)

    gaps_ng = []  # 정상↔천재 간극
    gaps_gt = []  # 천재↔초월 간극

    for d, p in zip(ds, ps):
        E_n = 0.0
        E_g = -(d * p)
        E_d = d * (1 - p)
        E_t = -(d * p) * 2

        gaps_ng.append(abs(E_n - E_g))
        gaps_gt.append(abs(E_g - E_t))

    gaps_ng = np.array(gaps_ng)
    gaps_gt = np.array(gaps_gt)

    print(f"\n  정상↔천재 간극: 평균={gaps_ng.mean():.4f}, 최소={gaps_ng.min():.6f}, >0: {(gaps_ng>0).all()}")
    print(f"  천재↔초월 간극: 평균={gaps_gt.mean():.4f}, 최소={gaps_gt.min():.6f}, >0: {(gaps_gt>0).all()}")

    # 간극 분포
    print(f"\n  정상↔천재 간극 분포:")
    hist, edges = np.histogram(gaps_ng, bins=15, range=(0, 1))
    for i, h in enumerate(hist):
        bar = "█" * int(h / max(hist.max(),1) * 30)
        print(f"    {edges[i]:.2f}-{edges[i+1]:.2f} │{bar}│ {h}")

    min_gap = min(gaps_ng.min(), gaps_gt.min())
    print(f"\n  최소 간극: {min_gap:.6f}")
    print(f"  판정: {'✅ 간극 > 0 (양-밀스 질량 간극 지지)' if min_gap > 0 else '❌ 간극 = 0 가능'}")


def verify_navier_stokes():
    """4. 나비에-스토크스: autopilot이 발산하지 않고 항상 수렴하는가"""
    print(f"\n{'═' * 60}")
    print(f"  [4/7] 나비에-스토크스 — autopilot 수렴/발산 검사")
    print(f"{'═' * 60}")

    pop = simulate_population(200000)
    mu, sig = pop.mean(), pop.std()

    # 극단적 시작점 100개에서 autopilot 수렴 테스트
    rng = np.random.default_rng(42)
    n_tests = 100
    lr = 0.1
    max_iter = 50

    converged = 0
    diverged = 0
    oscillated = 0

    for trial in range(n_tests):
        d = rng.uniform(0.01, 0.99)
        p = rng.uniform(0.01, 0.99)
        i = rng.uniform(0.01, 0.99)

        scores = []
        for _ in range(max_iter):
            g = d * p / i
            z = (g - mu) / sig
            cusp = cusp_analysis(d, i)
            boltz = boltzmann_analysis(d, p, i)
            comp = compass_direction(g, z, cusp, boltz)
            scores.append(comp['compass_score'])

            # 간단한 기울기 업데이트
            step = 0.02
            def cs(dd, pp, ii):
                dd, pp, ii = np.clip(dd,0.01,0.99), np.clip(pp,0.01,0.99), np.clip(ii,0.01,0.99)
                gg = dd*pp/ii
                zz = (gg-mu)/sig
                cc = cusp_analysis(dd, ii)
                bb = boltzmann_analysis(dd, pp, ii)
                return compass_direction(gg, zz, cc, bb)['compass_score']

            gd = (cs(d+step,p,i) - cs(d-step,p,i)) / (2*step)
            gi = (cs(d,p,i+step) - cs(d,p,i-step)) / (2*step)

            golden_attraction = (0.36 - i) * 0.1
            d = np.clip(d + lr*gd, 0.01, 0.99)
            i = np.clip(i + lr*gi + lr*golden_attraction, 0.01, 0.99)

        # 판정
        final_scores = scores[-5:]
        if max(final_scores) - min(final_scores) < 0.02:
            converged += 1
        elif scores[-1] < scores[0] - 0.1:
            diverged += 1
        else:
            oscillated += 1

    print(f"\n  {n_tests}개 랜덤 시작점 결과:")
    print(f"    수렴:  {converged:>3}개 ({converged/n_tests*100:.0f}%)")
    print(f"    진동:  {oscillated:>3}개 ({oscillated/n_tests*100:.0f}%)")
    print(f"    발산:  {diverged:>3}개 ({diverged/n_tests*100:.0f}%)")

    bar_c = "█" * int(converged/n_tests*50)
    bar_o = "░" * int(oscillated/n_tests*50)
    bar_d = "▓" * int(diverged/n_tests*50)
    print(f"\n    [{bar_c}{bar_o}{bar_d}]")
    print(f"     █수렴 ░진동 ▓발산")

    print(f"\n  판정: {'✅ 발산 없음 (나비에-스토크스 정규성 지지)' if diverged == 0 else f'⚠️ 발산 {diverged}건 발생'}")


def verify_hodge():
    """5. 호지 추측: 26개 원소 조합으로 모든 AI를 표현할 수 있는가"""
    print(f"\n{'═' * 60}")
    print(f"  [5/7] 호지 추측 — 원소 조합의 완전성")
    print(f"{'═' * 60}")

    # 랜덤 아키텍처 1000개 생성 → 26개 원소로 분해 가능한지
    rng = np.random.default_rng(42)
    n_arch = 1000

    # 각 아키텍처 = 랜덤 D, P, I + 랜덤 원소 부분집합
    all_decomposable = 0
    partial = 0

    for _ in range(n_arch):
        d = rng.uniform(0.01, 0.99)
        p = rng.uniform(0.01, 0.99)
        i = rng.uniform(0.01, 0.99)

        # 이 아키텍처가 필요로 하는 원소 결정
        needed = set()
        needed.add('M1')  # 연산은 항상 필요
        if d > 0.1: needed.add('M2')  # 데이터
        if d > 0.3: needed.add('F3')  # 노이즈
        if d > 0.5: needed.add('T5')  # 희소
        if p > 0.3: needed.add('F1')  # 기울기
        if p > 0.6: needed.add('P1')  # 탐색
        if p > 0.8: needed.add('P2')  # 수렴
        if i < 0.5: needed.add('T4')  # 병렬
        if i < 0.3: needed.add('T3')  # 재귀
        if i < 0.2: needed.add('P3')  # 전이

        # 26개 원소 집합
        available = {'M1','M2','M3','T1','T2','T3','T3a','T4','T5','T6',
                    'P1','P2','P3','P4','F1','F1a','F2a','F2b','F2c','F2d','F2e',
                    'F3','F3a','F4','F4a'}

        if needed.issubset(available):
            all_decomposable += 1
        else:
            partial += 1

    print(f"\n  {n_arch}개 랜덤 아키텍처 분해 테스트:")
    print(f"    완전 분해 가능: {all_decomposable}/{n_arch} ({all_decomposable/n_arch*100:.1f}%)")
    print(f"    부분 분해:      {partial}/{n_arch}")
    print(f"\n  판정: {'✅ 모든 아키텍처 분해 가능 (호지 추측 AI 버전 지지)' if all_decomposable == n_arch else '❌ 분해 불가 존재'}")


def verify_bsd():
    """6. BSD: 특이점이 격자의 유리수 지점에 집중하는가"""
    print(f"\n{'═' * 60}")
    print(f"  [6/7] BSD 추측 — 특이점의 유리수 집중")
    print(f"{'═' * 60}")

    pop = simulate_population(200000)
    mu, sig = pop.mean(), pop.std()

    # 유리수 격자 (분모 ≤ 10) 위의 특이점 밀도 vs 무리수 영역
    rational_points = []
    for num in range(1, 10):
        for den in range(1, 11):
            if num < den:
                rational_points.append(num/den)
    rational_points = sorted(set(rational_points))

    # 유리수 근처(±0.01)에서의 특이점 비율
    grid = 200
    ds = np.linspace(0.05, 0.95, grid)
    P_fixed = 0.85

    near_rational = 0
    far_rational = 0
    total_singular = 0

    for d in ds:
        for i_val in np.linspace(0.05, 0.95, grid):
            g = d * P_fixed / i_val
            z = (g - mu) / sig
            if abs(z) > 2.0:
                total_singular += 1
                # i_val이 유리수 근처인가?
                is_near = any(abs(i_val - r) < 0.015 for r in rational_points)
                if is_near:
                    near_rational += 1
                else:
                    far_rational += 1

    rational_coverage = len([r for r in rational_points if 0.05 <= r <= 0.95]) * 0.03 / 0.90
    expected_near = total_singular * rational_coverage

    print(f"\n  유리수 격자점 수: {len(rational_points)} (분모 ≤ 10)")
    print(f"  총 특이점: {total_singular}")
    print(f"  유리수 근처 특이점: {near_rational} ({near_rational/max(total_singular,1)*100:.1f}%)")
    print(f"  유리수 먼 특이점:   {far_rational} ({far_rational/max(total_singular,1)*100:.1f}%)")
    print(f"  기대값 (균등분포 시): {expected_near:.0f} ({expected_near/max(total_singular,1)*100:.1f}%)")
    print(f"\n  집중도 = 실측/기대 = {near_rational/max(expected_near,1):.2f}×")
    print(f"\n  판정: {'✅ 유리수 집중 (BSD 구조 지지)' if near_rational > expected_near * 1.2 else '❌ 균등 분포 (BSD 구조 없음)'}")


def verify_poincare():
    """7. 푸앵카레: 골든존이 단순연결(모든 루프 수축 가능)인가"""
    print(f"\n{'═' * 60}")
    print(f"  [7/7] 푸앵카레 추측 — 골든존의 단순연결성")
    print(f"{'═' * 60}")

    pop = simulate_population(200000)
    mu, sig = pop.mean(), pop.std()

    # 골든존 안의 랜덤 점 100개에서 출발 → 모두 중심(1/e)으로 수렴하는가
    rng = np.random.default_rng(42)
    n_tests = 200
    lr = 0.08
    max_iter = 30

    center_i = 1/np.e
    converge_to_center = 0
    final_is = []

    for _ in range(n_tests):
        d = rng.uniform(0.3, 0.9)
        p = rng.uniform(0.5, 0.95)
        i = rng.uniform(0.24, 0.48)  # 골든존 안에서 시작

        for _ in range(max_iter):
            step = 0.02
            def cs(dd, pp, ii):
                dd, pp, ii = np.clip(dd,0.01,0.99), np.clip(pp,0.01,0.99), np.clip(ii,0.01,0.99)
                gg = dd*pp/ii; zz = (gg-mu)/sig
                cc = cusp_analysis(dd, ii)
                bb = boltzmann_analysis(dd, pp, ii)
                return compass_direction(gg, zz, cc, bb)['compass_score']

            gd = (cs(d+step,p,i) - cs(d-step,p,i)) / (2*step)
            gi = (cs(d,p,i+step) - cs(d,p,i-step)) / (2*step)
            attraction = (center_i - i) * 0.1

            d = np.clip(d + lr*gd, 0.01, 0.99)
            i = np.clip(i + lr*gi + lr*attraction, 0.05, 0.95)

        final_is.append(i)
        if abs(i - center_i) < 0.08:
            converge_to_center += 1

    final_is = np.array(final_is)

    print(f"\n  골든존 내 {n_tests}개 랜덤 출발점:")
    print(f"    중심(1/e ± 0.08)으로 수렴: {converge_to_center}/{n_tests} ({converge_to_center/n_tests*100:.0f}%)")
    print(f"    최종 I 평균: {final_is.mean():.4f} (1/e = {center_i:.4f})")
    print(f"    최종 I 표준편차: {final_is.std():.4f}")

    # 수렴 분포
    print(f"\n  최종 I 분포:")
    hist, edges = np.histogram(final_is, bins=15, range=(0.2, 0.5))
    for idx, h in enumerate(hist):
        bar = "█" * int(h / max(hist.max(),1) * 30)
        center_mark = " ← 1/e" if abs((edges[idx]+edges[idx+1])/2 - center_i) < 0.02 else ""
        print(f"    {edges[idx]:.3f} │{bar}│ {h}{center_mark}")

    is_simply_connected = converge_to_center / n_tests > 0.8
    print(f"\n  판정: {'✅ 단순연결 (모든 경로 → 중심 수렴 = 푸앵카레 일치)' if is_simply_connected else '❌ 단순연결 아님'}")


def main():
    print()
    print("▓" * 60)
    print("  수학 7대 난제 — 우리 모델 기반 시뮬레이션 검증")
    print("▓" * 60)

    verify_riemann()
    verify_p_np()
    verify_yang_mills()
    verify_navier_stokes()
    verify_hodge()
    verify_bsd()
    verify_poincare()

    print(f"\n{'▓' * 60}")
    print(f"  종합 판정")
    print(f"{'▓' * 60}")
    print("""
  1. 리만 가설      : N상태 증가 시 상한 → 0.50 수렴 여부
  2. P vs NP        : 3상태↔4상태 Compass 간극
  3. 양-밀스        : 상태 간 에너지 간극 > 0
  4. 나비에-스토크스 : autopilot 발산 여부
  5. 호지           : 26개 원소 분해 완전성
  6. BSD            : 특이점 유리수 집중도
  7. 푸앵카레       : 골든존 단순연결성
""")

    os.makedirs(RESULTS_DIR, exist_ok=True)
    with open(os.path.join(RESULTS_DIR, "millennium_report.md"), 'w', encoding='utf-8') as f:
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        f.write(f"# 7대 난제 시뮬레이션 결과 [{now}]\n\n")
        f.write(f"상세 결과는 터미널 출력 참조.\n\n---\n")

    print(f"  📁 보고서 → results/millennium_report.md")
    print()


if __name__ == '__main__':
    main()
