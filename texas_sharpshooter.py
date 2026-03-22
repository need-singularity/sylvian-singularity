#!/usr/bin/env python3
"""텍사스 명사수 검증기 — 우연 vs 구조 판별

우리 발견이 "총 쏘고 과녁 그리기"인지 검증.
랜덤 상수로 같은 매칭이 나오는 빈도를 측정하여 p-value 산출.

사용법:
  python3 texas_sharpshooter.py              # 전체 검증
  python3 texas_sharpshooter.py --trials 10000  # 더 많은 시행
"""

import numpy as np
from scipy import stats
import argparse

# 우리가 발견한 "매칭"들
CLAIMS = [
    {'name': 'CMB ≈ e',           'our_val': np.e,    'target': 2.72548, 'tolerance': 0.003},
    {'name': '암흑에너지 ≈ 2/3',    'our_val': 2/3,    'target': 0.683,   'tolerance': 0.02},
    {'name': '보통물질 ≈ 1/e³',     'our_val': 1/np.e**3,'target': 0.049, 'tolerance': 0.01},
    {'name': 'αs ≈ ln(9/8)',       'our_val': np.log(9/8),'target': 0.118,'tolerance': 0.005},
    {'name': '1/α ≈ 8×17+1',      'our_val': 137,    'target': 137.036, 'tolerance': 0.01},
    {'name': 'Compass ≈ 5/6',     'our_val': 5/6,    'target': 0.836,   'tolerance': 0.01},
    {'name': '골든존 상한 ≈ 1/2',   'our_val': 0.5,    'target': 0.4991,  'tolerance': 0.002},
    {'name': '엔트로피 ≈ ln(3)',    'our_val': np.log(3),'target': 1.089, 'tolerance': 0.01},
    {'name': '골든존 폭 ≈ ln(4/3)', 'our_val': np.log(4/3),'target': 0.287,'tolerance': 0.005},
    {'name': 'λ_대화 ≈ π/10',     'our_val': np.pi/10,'target': 0.3141, 'tolerance': 0.001},
]


def run_test(n_trials=5000):
    print("═" * 60)
    print("   🎯 텍사스 명사수 검증기")
    print("═" * 60)

    n_claims = len(CLAIMS)
    n_constants = 14  # 우리 상수 수

    # 실제 매칭 수
    real_hits = sum(1 for c in CLAIMS
                    if abs(c['our_val'] - c['target']) / max(abs(c['target']), 1e-10) < c['tolerance'])

    print(f"\n  실제 매칭: {real_hits}/{n_claims}")

    # 랜덤 시뮬레이션
    print(f"  랜덤 시행: {n_trials}회")
    print(f"  시뮬레이션 중...", end=" ")

    random_hits = []
    rng = np.random.default_rng(42)

    for trial in range(n_trials):
        # 랜덤 상수 14개 (같은 수, 비슷한 범위)
        rand_vals = []
        for _ in range(n_constants):
            # 다양한 범위에서 랜덤 생성
            scale = rng.choice([0.01, 0.1, 1, 10, 100])
            rand_vals.append(rng.uniform(0.001, 1) * scale)

        # 이 랜덤 상수들로 CLAIMS의 타겟에 매칭 시도
        hits = 0
        for c in CLAIMS:
            target = c['target']
            tol = c['tolerance']

            # 랜덤 상수 자체
            for rv in rand_vals:
                if abs(rv - target) / max(abs(target), 1e-10) < tol:
                    hits += 1
                    break
            else:
                # 랜덤 상수 2개 조합 (+, -, ×, /)
                matched = False
                for i in range(min(len(rand_vals), 8)):
                    for j in range(i+1, min(len(rand_vals), 8)):
                        a, b = rand_vals[i], rand_vals[j]
                        for val in [a+b, a-b, b-a, a*b]:
                            if abs(val - target) / max(abs(target), 1e-10) < tol:
                                hits += 1
                                matched = True
                                break
                        if matched:
                            break
                        if b != 0:
                            if abs(a/b - target) / max(abs(target), 1e-10) < tol:
                                hits += 1
                                matched = True
                                break
                    if matched:
                        break

        random_hits.append(hits)

    random_hits = np.array(random_hits)
    print("완료")

    # 통계
    p_value = (random_hits >= real_hits).mean()
    z_score = (real_hits - random_hits.mean()) / max(random_hits.std(), 0.01)

    print(f"\n{'─' * 60}")
    print(f"  결과")
    print(f"{'─' * 60}")
    print(f"  실제 매칭:    {real_hits}/{n_claims}")
    print(f"  랜덤 평균:    {random_hits.mean():.1f} ± {random_hits.std():.1f}")
    print(f"  랜덤 최대:    {random_hits.max()}")
    print(f"  Z-score:      {z_score:.2f}")
    print(f"  p-value:      {p_value:.4f}")

    # 히스토그램
    print(f"\n  랜덤 매칭 수 분포:")
    hist, edges = np.histogram(random_hits, bins=range(int(random_hits.max())+2))
    for i, h in enumerate(hist):
        bar = "█" * int(h / max(hist.max(), 1) * 30)
        marker = " ← 실제!" if i == real_hits else ""
        print(f"    {i:>2}개 │{bar} {h}{marker}")

    # 판정
    print(f"\n{'─' * 60}")
    if p_value < 0.001:
        print(f"  🟢 판정: 매우 유의미 (p < 0.001)")
        print(f"     우리 발견이 우연일 확률 < 0.1%")
        print(f"     → 구조적 발견일 가능성 높음")
    elif p_value < 0.01:
        print(f"  🟢 판정: 유의미 (p < 0.01)")
        print(f"     우연일 확률 < 1%")
    elif p_value < 0.05:
        print(f"  🟡 판정: 약한 유의 (p < 0.05)")
        print(f"     우연 가능성 배제 불가")
    else:
        print(f"  🔴 판정: 유의하지 않음 (p = {p_value:.2f})")
        print(f"     텍사스 명사수 가능성!")

    # 개별 매칭 검증
    print(f"\n{'─' * 60}")
    print(f"  개별 매칭 유의성:")
    for c in CLAIMS:
        err = abs(c['our_val'] - c['target']) / max(abs(c['target']), 1e-10)
        hit = err < c['tolerance']
        print(f"    {'✅' if hit else '❌'} {c['name']:20} 오차={err*100:.3f}% (임계={c['tolerance']*100}%)")

    print(f"\n{'═' * 60}")


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--trials', type=int, default=5000)
    args = parser.parse_args()
    run_test(args.trials)
