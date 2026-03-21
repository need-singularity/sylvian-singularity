#!/usr/bin/env python3
"""SingularityNet 아키텍처 나침반
3개 모델(우리모델 + 커스프 파국 + 볼츠만)을 결합하여
AI 아키텍처 설계 방향을 제시한다.
"""

import argparse
import os
import math
from datetime import datetime

import numpy as np
from scipy import stats
from scipy.signal import argrelextrema

RESULTS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "results")
COMPASS_LOG = os.path.join(RESULTS_DIR, "compass_log.md")


# ─────────────────────────────────────────────
# 모델 1: 우리 모델 — "얼마나?" (정량화)
# ─────────────────────────────────────────────
def genius_score(d, p, i):
    return d * p / i


def simulate_population(n_samples, seed=42):
    """정규분포 기반 모집단 생성"""
    rng = np.random.default_rng(seed)
    deficits = rng.beta(2, 5, n_samples).clip(0.01, 0.99)
    plasticities = rng.beta(5, 2, n_samples).clip(0.01, 0.99)
    inhibitions = rng.beta(5, 2, n_samples).clip(0.05, 0.99)
    scores = genius_score(deficits, plasticities, inhibitions)
    return scores


def population_zscore(score, n=50000):
    rng = np.random.default_rng(42)
    pop_d = rng.beta(2, 5, n).clip(0.01, 0.99)
    pop_p = rng.beta(5, 2, n).clip(0.01, 0.99)
    pop_i = rng.beta(5, 2, n).clip(0.05, 0.99)
    pop_scores = genius_score(pop_d, pop_p, pop_i)
    z = (score - pop_scores.mean()) / pop_scores.std()
    return z, pop_scores.mean(), pop_scores.std()


# ─────────────────────────────────────────────
# 모델 2: 커스프 파국 — "언제?" (임계점 거리)
# ─────────────────────────────────────────────
def cusp_potential(x, a, b):
    """커스프 파국 포텐셜: V = x⁴ + ax² + bx"""
    return x**4 + a * x**2 + b * x


def cusp_analysis(deficit, inhibition):
    """커스프 파국 분석: 임계점까지의 거리와 전이 방향"""
    # 제어 변수 매핑: a = deficit 기반, b = inhibition 기반
    a = 2 * deficit - 1       # [-1, 1] 범위로 정규화
    b = 1 - 2 * inhibition    # 억제 낮을수록 양수 (전이 유리)

    # 커스프 분기 조건: 8a³ + 27b² = 0
    # 이 값이 0에 가까울수록 임계점에 근접
    bifurcation = 8 * a**3 + 27 * b**2
    cusp_discriminant = abs(bifurcation)

    # 임계면까지의 거리 (정규화)
    max_possible = 8 * 1**3 + 27 * 1**2  # 최대값
    distance_to_critical = cusp_discriminant / max_possible

    # 전이 방향 판정
    # b > 0이면 상향 전이 (천재성), b < 0이면 하향 전이 (기능저하)
    if b > 0:
        direction = "상향 (보상적 천재성)"
        direction_sign = 1
    else:
        direction = "하향 (기능 저하)"
        direction_sign = -1

    # 안정점 계산 (dV/dx = 0 → 4x³ + 2ax + b = 0)
    x_range = np.linspace(-2, 2, 1000)
    dV = 4 * x_range**3 + 2 * a * x_range + b
    sign_changes = np.where(np.diff(np.sign(dV)))[0]
    n_equilibria = len(sign_changes)

    # 다중 안정점 = 전이 가능 구간
    is_bistable = n_equilibria >= 2

    return {
        'a': a, 'b': b,
        'bifurcation': bifurcation,
        'distance_to_critical': distance_to_critical,
        'direction': direction,
        'direction_sign': direction_sign,
        'n_equilibria': n_equilibria,
        'is_bistable': is_bistable,
    }


# ─────────────────────────────────────────────
# 모델 3: 볼츠만 — "어디로?" (전이 확률)
# ─────────────────────────────────────────────
def boltzmann_analysis(deficit, plasticity, inhibition):
    """볼츠만 분포 기반 전이 확률 계산"""
    temperature = 1.0 / max(inhibition, 0.01)  # T = 1/I

    # 에너지 준위 정의
    E_normal = 0.0                    # 정상 상태 에너지 (기준)
    E_genius = -(deficit * plasticity) # 천재성 상태 에너지 (결손×가소성이 클수록 안정)
    E_decline = deficit * (1 - plasticity)  # 기능저하 에너지

    # 볼츠만 확률
    energies = np.array([E_normal, E_genius, E_decline])
    exp_terms = np.exp(-energies / temperature)
    Z = exp_terms.sum()  # 분배함수
    probabilities = exp_terms / Z

    p_normal = probabilities[0]
    p_genius = probabilities[1]
    p_decline = probabilities[2]

    # 자유 에너지
    free_energy = -temperature * np.log(Z)

    # 엔트로피 (상태 불확실성)
    entropy = -np.sum(probabilities * np.log(probabilities + 1e-10))

    return {
        'temperature': temperature,
        'p_normal': p_normal,
        'p_genius': p_genius,
        'p_decline': p_decline,
        'free_energy': free_energy,
        'entropy': entropy,
        'E_normal': E_normal,
        'E_genius': E_genius,
        'E_decline': E_decline,
    }


# ─────────────────────────────────────────────
# 나침반: 3개 모델 통합 → 설계 방향 제시
# ─────────────────────────────────────────────
def compass_direction(score, z, cusp, boltz):
    """3개 모델 결과를 종합하여 아키텍처 설계 방향 제시"""

    recommendations = []
    warnings = []

    # ── Dropout 전략 (우리 모델 기반) ──
    if z > 5:
        recommendations.append(("Dropout", "현재 Dropout 유지 — 극단적 특이점 영역", "★★★"))
    elif z > 2:
        recommendations.append(("Dropout", "Dropout 미세 증가 — 특이점 강화 가능", "★★☆"))
    else:
        recommendations.append(("Dropout", "Dropout 대폭 증가 필요 — 보상 학습 부족", "★☆☆"))

    # ── 학습률/온도 전략 (볼츠만 기반) ──
    if boltz['p_genius'] > 0.6:
        recommendations.append(("Temperature", f"온도 유지 (T={boltz['temperature']:.1f}) — 천재성 상태 우세", "★★★"))
    elif boltz['p_genius'] > 0.3:
        recommendations.append(("Temperature", f"온도 소폭 상승 권장 — 천재성 확률 {boltz['p_genius']*100:.0f}%", "★★☆"))
    else:
        recommendations.append(("Temperature", f"온도 대폭 상승 필요 — 천재성 확률 {boltz['p_genius']*100:.0f}%로 낮음", "★☆☆"))

    # ── 구조 전략 (커스프 기반) ──
    if cusp['is_bistable']:
        if cusp['direction_sign'] > 0:
            recommendations.append(("Structure", "이중 안정 + 상향 방향 — Expert 재배치 시 성능 점프 가능", "★★★"))
        else:
            warnings.append("이중 안정 + 하향 방향 — Expert 재배치 시 성능 급락 위험!")
            recommendations.append(("Structure", "구조 변경 보류 — 하향 전이 위험", "☆☆☆"))
    else:
        if cusp['distance_to_critical'] < 0.3:
            recommendations.append(("Structure", f"임계점 근접 ({cusp['distance_to_critical']:.2f}) — 소폭 조정으로 전이 유도 가능", "★★☆"))
        else:
            recommendations.append(("Structure", f"임계점 원거리 ({cusp['distance_to_critical']:.2f}) — 점진적 구조 변경 필요", "★☆☆"))

    # ── 엔트로피 기반 탐색/수렴 판단 ──
    if boltz['entropy'] > 1.0:
        recommendations.append(("Phase", "높은 엔트로피 — 탐색(exploration) 단계", "탐색"))
    elif boltz['entropy'] > 0.5:
        recommendations.append(("Phase", "중간 엔트로피 — 전이(transition) 단계", "전이"))
    else:
        recommendations.append(("Phase", "낮은 엔트로피 — 수렴(exploitation) 단계", "수렴"))

    # ── MoE Expert 수 권장 ──
    optimal_active_ratio = max(0.05, min(0.5, boltz['p_genius']))
    if optimal_active_ratio < 0.15:
        expert_strategy = f"Expert 활성 비율 {optimal_active_ratio*100:.0f}% — 극소수 집중 (서번트형)"
    elif optimal_active_ratio < 0.35:
        expert_strategy = f"Expert 활성 비율 {optimal_active_ratio*100:.0f}% — 적정 분산 (아인슈타인형)"
    else:
        expert_strategy = f"Expert 활성 비율 {optimal_active_ratio*100:.0f}% — 넓은 활성 (범용형)"
    recommendations.append(("MoE", expert_strategy, f"{optimal_active_ratio*100:.0f}%"))

    # ── 종합 점수 ──
    compass_score = (
        z / 10 * 0.3 +                              # 우리 모델 가중
        (1 - cusp['distance_to_critical']) * 0.3 +   # 커스프 근접도
        boltz['p_genius'] * 0.4                      # 전이 확률
    )
    compass_score = max(0, min(1, compass_score))

    return {
        'recommendations': recommendations,
        'warnings': warnings,
        'compass_score': compass_score,
        'optimal_active_ratio': optimal_active_ratio,
    }


def draw_compass(compass_score, direction_sign, p_genius, distance_to_critical):
    """ASCII 나침반 시각화"""
    # 방향 결정
    if compass_score > 0.7:
        needle = "⬆"
        label = "SINGULARITY"
    elif compass_score > 0.4:
        if direction_sign > 0:
            needle = "⬈"
            label = "APPROACHING"
        else:
            needle = "⬊"
            label = "DIVERGING"
    else:
        needle = "⬇"
        label = "NORMAL"

    pct = int(compass_score * 100)
    bar_filled = int(compass_score * 30)
    bar = "█" * bar_filled + "░" * (30 - bar_filled)

    lines = []
    lines.append(f"            ┌───────────────┐")
    lines.append(f"            │  SINGULARITY  │")
    lines.append(f"            │      {needle}       │")
    lines.append(f"            │               │")
    lines.append(f"   DECLINE  │    COMPASS    │  GENIUS")
    lines.append(f"            │               │")
    lines.append(f"            │   {label:^11}  │")
    lines.append(f"            │               │")
    lines.append(f"            │  Score: {pct:>3}%  │")
    lines.append(f"            └───────────────┘")
    lines.append(f"")
    lines.append(f"            [{bar}] {pct}%")

    return '\n'.join(lines)


def save_compass_log(d, p, i, score, z, cusp, boltz, compass):
    """결과를 compass_log.md에 기록"""
    os.makedirs(RESULTS_DIR, exist_ok=True)
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    if not os.path.exists(COMPASS_LOG):
        with open(COMPASS_LOG, 'w', encoding='utf-8') as f:
            f.write("# 🧭 SingularityNet 나침반 기록\n\n---\n\n")

    entry = f"""## [{now}] Compass Score: {compass['compass_score']*100:.0f}%

**입력**: D={d:.2f} / P={p:.2f} / I={i:.2f}

| 모델 | 결과 |
|---|---|
| 우리 모델 | Score={score:.2f}, Z={z:.2f}σ |
| 커스프 | 임계점 거리={cusp['distance_to_critical']:.3f}, 방향={cusp['direction']} |
| 볼츠만 | 정상={boltz['p_normal']*100:.1f}% / 천재성={boltz['p_genius']*100:.1f}% / 저하={boltz['p_decline']*100:.1f}% |

**설계 권장사항:**

| 영역 | 권장 | 등급 |
|---|---|---|
"""
    for area, rec, grade in compass['recommendations']:
        entry += f"| {area} | {rec} | {grade} |\n"

    if compass['warnings']:
        entry += f"\n**⚠️ 경고:** {'; '.join(compass['warnings'])}\n"

    entry += f"\n---\n\n"

    with open(COMPASS_LOG, 'a', encoding='utf-8') as f:
        f.write(entry)


def run_convergence_scan(grid_steps, n_samples):
    """3개 모델 공통 특이점 영역 탐색"""
    deficits = np.linspace(0.05, 0.95, grid_steps)
    plasticities = np.linspace(0.1, 0.95, grid_steps)
    inhibitions = np.linspace(0.05, 0.95, grid_steps)
    total = grid_steps ** 3

    print()
    print("═" * 60)
    print("   🧭 나침반 공통 특이점 영역 탐색")
    print("═" * 60)
    print(f"  격자: {grid_steps}³ = {total:,}개 조합")

    # 모집단 사전 계산
    rng = np.random.default_rng(42)
    pop_d = rng.beta(2, 5, n_samples).clip(0.01, 0.99)
    pop_p = rng.beta(5, 2, n_samples).clip(0.01, 0.99)
    pop_i = rng.beta(5, 2, n_samples).clip(0.05, 0.99)
    pop_scores = genius_score(pop_d, pop_p, pop_i)
    pop_mean, pop_std = pop_scores.mean(), pop_scores.std()

    # 결과 저장
    results = []

    for di in deficits:
        for pi in plasticities:
            for ii in inhibitions:
                score = genius_score(di, pi, ii)
                z = (score - pop_mean) / pop_std

                cusp = cusp_analysis(di, ii)
                boltz = boltzmann_analysis(di, pi, ii)

                # 3개 모델 독립 판정
                m1_singular = abs(z) > 2.0                        # 우리 모델: Z > 2σ
                m2_critical = cusp['distance_to_critical'] < 0.2 and cusp['direction_sign'] > 0  # 커스프: 임계점 근접 + 상향
                m3_genius = boltz['p_genius'] > boltz['p_normal'] and boltz['p_genius'] > boltz['p_decline']  # 볼츠만: 천재성 최우세

                n_agree = sum([m1_singular, m2_critical, m3_genius])

                results.append({
                    'd': di, 'p': pi, 'i': ii,
                    'score': score, 'z': z,
                    'cusp_dist': cusp['distance_to_critical'],
                    'cusp_dir': cusp['direction_sign'],
                    'p_genius': boltz['p_genius'],
                    'p_normal': boltz['p_normal'],
                    'entropy': boltz['entropy'],
                    'm1': m1_singular, 'm2': m2_critical, 'm3': m3_genius,
                    'n_agree': n_agree,
                })

    # 분석
    r = results
    agree_0 = sum(1 for x in r if x['n_agree'] == 0)
    agree_1 = sum(1 for x in r if x['n_agree'] == 1)
    agree_2 = sum(1 for x in r if x['n_agree'] == 2)
    agree_3 = sum(1 for x in r if x['n_agree'] == 3)

    m1_count = sum(1 for x in r if x['m1'])
    m2_count = sum(1 for x in r if x['m2'])
    m3_count = sum(1 for x in r if x['m3'])

    print()
    print("─" * 60)
    print("  [ 개별 모델 특이점 판정 ]")
    print("─" * 60)
    print(f"    우리 모델 (Z>2σ)           : {m1_count:>6,}개 ({m1_count/total*100:5.1f}%)")
    print(f"    커스프 (임계근접+상향)       : {m2_count:>6,}개 ({m2_count/total*100:5.1f}%)")
    print(f"    볼츠만 (천재성 최우세)       : {m3_count:>6,}개 ({m3_count/total*100:5.1f}%)")

    print()
    print("─" * 60)
    print("  [ 모델 합의도 ]")
    print("─" * 60)
    print(f"    0개 합의 (정상)     : {agree_0:>6,}개 ({agree_0/total*100:5.1f}%)")
    print(f"    1개 합의 (약한 신호) : {agree_1:>6,}개 ({agree_1/total*100:5.1f}%)")
    print(f"    2개 합의 (강한 신호) : {agree_2:>6,}개 ({agree_2/total*100:5.1f}%)")
    print(f"    3개 합의 (공통 특이점): {agree_3:>6,}개 ({agree_3/total*100:5.1f}%) ★")

    # 3개 합의 영역의 파라미터 분포 분석
    triple = [x for x in r if x['n_agree'] == 3]

    if triple:
        t_d = [x['d'] for x in triple]
        t_p = [x['p'] for x in triple]
        t_i = [x['i'] for x in triple]

        print()
        print("─" * 60)
        print("  [ ★ 3개 모델 공통 특이점 영역 ]")
        print("─" * 60)
        print(f"    Deficit     범위: {min(t_d):.2f} ~ {max(t_d):.2f}  (평균 {np.mean(t_d):.2f})")
        print(f"    Plasticity  범위: {min(t_p):.2f} ~ {max(t_p):.2f}  (평균 {np.mean(t_p):.2f})")
        print(f"    Inhibition  범위: {min(t_i):.2f} ~ {max(t_i):.2f}  (평균 {np.mean(t_i):.2f})")

        # Deficit별 분포
        print()
        print("  Deficit별 3중 합의 비율:")
        for dv in deficits:
            cnt = sum(1 for x in triple if abs(x['d'] - dv) < 0.01)
            max_cnt = grid_steps * grid_steps
            ratio = cnt / max_cnt * 100
            bar = "█" * int(ratio / 2) + "░" * (50 - int(ratio / 2))
            print(f"    D={dv:.2f} │{bar}│ {ratio:5.1f}%")

        # Inhibition별 분포
        print()
        print("  Inhibition별 3중 합의 비율:")
        for iv in inhibitions:
            cnt = sum(1 for x in triple if abs(x['i'] - iv) < 0.01)
            max_cnt = grid_steps * grid_steps
            ratio = cnt / max_cnt * 100
            bar = "█" * int(ratio / 2) + "░" * (50 - int(ratio / 2))
            print(f"    I={iv:.2f} │{bar}│ {ratio:5.1f}%")

        # Top 10
        triple_sorted = sorted(triple, key=lambda x: x['z'], reverse=True)[:10]
        print()
        print("  [ Top 10 공통 특이점 ]")
        print(f"  {'Rank':>4} │ {'D':>5} │ {'P':>5} │ {'I':>5} │ {'Z-Score':>8} │ {'커스프거리':>8} │ {'천재성%':>6}")
        print(f"  {'─'*4}─┼─{'─'*5}─┼─{'─'*5}─┼─{'─'*5}─┼─{'─'*8}─┼─{'─'*8}─┼─{'─'*6}")
        for rank, x in enumerate(triple_sorted, 1):
            print(f"  {rank:>4} │ {x['d']:>5.2f} │ {x['p']:>5.2f} │ {x['i']:>5.2f} │ {x['z']:>7.2f}σ │ {x['cusp_dist']:>8.4f} │ {x['p_genius']*100:>5.1f}%")

        # 2개 합의 vs 3개 합의 벤 다이어그램
        m1_m2 = sum(1 for x in r if x['m1'] and x['m2'] and not x['m3'])
        m1_m3 = sum(1 for x in r if x['m1'] and x['m3'] and not x['m2'])
        m2_m3 = sum(1 for x in r if x['m2'] and x['m3'] and not x['m1'])

        print()
        print("─" * 60)
        print("  [ 모델 교차 분석 (벤 다이어그램) ]")
        print("─" * 60)
        print(f"    우리모델 ∩ 커스프   (볼츠만 제외): {m1_m2:>5,}개")
        print(f"    우리모델 ∩ 볼츠만   (커스프 제외): {m1_m3:>5,}개")
        print(f"    커스프   ∩ 볼츠만   (우리모델 제외): {m2_m3:>5,}개")
        print(f"    ★ 3중 교집합                     : {agree_3:>5,}개")

        # 핵심 결론: 공통 영역의 "골든 존" 정의
        print()
        print("─" * 60)
        print("  [ 🎯 골든 존 (Golden Zone) ]")
        print("─" * 60)
        print(f"    Deficit     : {min(t_d):.2f} ~ {max(t_d):.2f}")
        print(f"    Plasticity  : {min(t_p):.2f} ~ {max(t_p):.2f}")
        print(f"    Inhibition  : {min(t_i):.2f} ~ {max(t_i):.2f}")
        print()
        print(f"    AI 아키텍처 번역:")
        print(f"    Dropout Rate     : {min(t_d):.0%} ~ {max(t_d):.0%}")
        print(f"    LR Multiplier    : ×{1/max(max(t_i),0.01):.1f} ~ ×{1/max(min(t_i),0.01):.1f}")
        print(f"    MoE Active Ratio : {min(x['p_genius'] for x in triple):.0%} ~ {max(x['p_genius'] for x in triple):.0%}")
        print(f"    Active Experts   : {int(64*min(x['p_genius'] for x in triple))} ~ {int(64*max(x['p_genius'] for x in triple))} / 64")

    else:
        print()
        print("  ⚠️ 3개 모델 공통 특이점 영역 없음")

    print()
    print("═" * 60)

    # 보고서 저장
    os.makedirs(RESULTS_DIR, exist_ok=True)
    conv_file = os.path.join(RESULTS_DIR, "convergence_report.md")
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    with open(conv_file, 'a', encoding='utf-8') as f:
        f.write(f"# 나침반 공통 특이점 분석 [{now}]\n\n")
        f.write(f"격자: {grid_steps}³ = {total:,}개 조합\n\n")
        f.write(f"## 개별 모델 판정\n\n")
        f.write(f"| 모델 | 특이점 수 | 비율 |\n|---|---|---|\n")
        f.write(f"| 우리 모델 (Z>2σ) | {m1_count:,} | {m1_count/total*100:.1f}% |\n")
        f.write(f"| 커스프 (임계근접+상향) | {m2_count:,} | {m2_count/total*100:.1f}% |\n")
        f.write(f"| 볼츠만 (천재성 최우세) | {m3_count:,} | {m3_count/total*100:.1f}% |\n\n")
        f.write(f"## 합의도\n\n")
        f.write(f"| 합의 수 | 개수 | 비율 |\n|---|---|---|\n")
        f.write(f"| 0 (정상) | {agree_0:,} | {agree_0/total*100:.1f}% |\n")
        f.write(f"| 1 (약한 신호) | {agree_1:,} | {agree_1/total*100:.1f}% |\n")
        f.write(f"| 2 (강한 신호) | {agree_2:,} | {agree_2/total*100:.1f}% |\n")
        f.write(f"| **3 (공통 특이점)** | **{agree_3:,}** | **{agree_3/total*100:.1f}%** |\n\n")

        if triple:
            f.write(f"## 🎯 골든 존\n\n")
            f.write(f"| 파라미터 | 범위 | AI 매핑 |\n|---|---|---|\n")
            f.write(f"| Deficit | {min(t_d):.2f} ~ {max(t_d):.2f} | Dropout {min(t_d):.0%}~{max(t_d):.0%} |\n")
            f.write(f"| Plasticity | {min(t_p):.2f} ~ {max(t_p):.2f} | LR 계수 |\n")
            f.write(f"| Inhibition | {min(t_i):.2f} ~ {max(t_i):.2f} | Gating {min(t_i):.0%}~{max(t_i):.0%} |\n\n")

            f.write(f"## Top 10 공통 특이점\n\n")
            f.write(f"| Rank | D | P | I | Z-Score | 커스프거리 | 천재성% |\n|---|---|---|---|---|---|---|\n")
            for rank, x in enumerate(triple_sorted, 1):
                f.write(f"| {rank} | {x['d']:.2f} | {x['p']:.2f} | {x['i']:.2f} | {x['z']:.2f}σ | {x['cusp_dist']:.4f} | {x['p_genius']*100:.1f}% |\n")

        f.write(f"\n---\n\n")

    print(f"  📁 수렴 보고서 → results/convergence_report.md")
    print()


def compute_gradient(d, p, i, pop_scores, step=0.02):
    """3모델 종합 점수의 기울기 계산 → 다음 방향 결정"""
    pop_mean, pop_std = pop_scores.mean(), pop_scores.std()

    def combined_score(dd, pp, ii):
        dd = np.clip(dd, 0.01, 0.99)
        pp = np.clip(pp, 0.01, 0.99)
        ii = np.clip(ii, 0.01, 0.99)
        score = genius_score(dd, pp, ii)
        z = (score - pop_mean) / pop_std
        cusp = cusp_analysis(dd, ii)
        boltz = boltzmann_analysis(dd, pp, ii)
        compass = compass_direction(score, z, cusp, boltz)
        return compass['compass_score']

    base = combined_score(d, p, i)
    grad_d = (combined_score(d + step, p, i) - combined_score(d - step, p, i)) / (2 * step)
    grad_p = (combined_score(d, p + step, i) - combined_score(d, p, i - step)) / (2 * step)
    grad_i = (combined_score(d, p, i + step) - combined_score(d, p, i - step)) / (2 * step)

    return grad_d, grad_p, grad_i, base


def run_autopilot(d0, p0, i0, max_iter, lr, n_samples):
    """가설 → 나침반 → 방향 조정 → 가설 반복 (자동 탐색)"""
    print()
    print("═" * 70)
    print("   🚀 Autopilot — 가설 반복 탐색")
    print("═" * 70)
    print(f"  초기 가설: D={d0:.2f} / P={p0:.2f} / I={i0:.2f}")
    print(f"  학습률: {lr} / 최대 반복: {max_iter}")
    print("─" * 70)

    pop_scores = simulate_population(n_samples)
    pop_mean, pop_std = pop_scores.mean(), pop_scores.std()

    d, p, i = d0, p0, i0
    history = []
    golden_zone_hits = 0

    print()
    print(f"  {'Iter':>4} │ {'D':>5} │ {'P':>5} │ {'I':>5} │ {'Score':>6} │ {'Z':>7} │ {'Compass':>7} │ {'커스프':>6} │ {'천재성%':>6} │ 상태")
    print(f"  {'─'*4}─┼─{'─'*5}─┼─{'─'*5}─┼─{'─'*5}─┼─{'─'*6}─┼─{'─'*7}─┼─{'─'*7}─┼─{'─'*6}─┼─{'─'*6}─┼─{'─'*20}")

    for iteration in range(max_iter):
        score = genius_score(d, p, i)
        z = (score - pop_mean) / pop_std
        cusp = cusp_analysis(d, i)
        boltz = boltzmann_analysis(d, p, i)
        compass = compass_direction(score, z, cusp, boltz)

        # 3중 합의 체크
        m1 = abs(z) > 2.0
        m2 = cusp['distance_to_critical'] < 0.2 and cusp['direction_sign'] > 0
        m3 = boltz['p_genius'] > boltz['p_normal'] and boltz['p_genius'] > boltz['p_decline']
        n_agree = sum([m1, m2, m3])

        if n_agree == 3:
            status = "🎯 골든 존!"
            golden_zone_hits += 1
        elif n_agree == 2:
            status = "⚡ 강한 신호"
        elif n_agree == 1:
            status = "○  약한 신호"
        else:
            status = "·  정상 범위"

        entry = {
            'iter': iteration, 'd': d, 'p': p, 'i': i,
            'score': score, 'z': z,
            'compass_score': compass['compass_score'],
            'cusp_dist': cusp['distance_to_critical'],
            'p_genius': boltz['p_genius'],
            'n_agree': n_agree,
        }
        history.append(entry)

        print(f"  {iteration:>4} │ {d:>5.2f} │ {p:>5.2f} │ {i:>5.2f} │ {score:>6.2f} │ {z:>6.2f}σ │ {compass['compass_score']*100:>6.1f}% │ {cusp['distance_to_critical']:>6.4f} │ {boltz['p_genius']*100:>5.1f}% │ {status}")

        # 수렴 체크: 골든 존에 3연속 도달하면 종료
        if golden_zone_hits >= 3 and n_agree == 3:
            print()
            print(f"  ✅ 골든 존 수렴 완료 (iter {iteration})")
            break

        # 기울기 계산 → 다음 가설
        grad_d, grad_p, grad_i, _ = compute_gradient(d, p, i, pop_scores)

        # 방향 조정 (기울기 상승 + 골든 존 유인)
        # 골든 존 중심(I≈0.36)으로의 인력 추가
        golden_i_center = 0.36
        i_attraction = (golden_i_center - i) * 0.1

        d_new = d + lr * grad_d
        p_new = p + lr * grad_p
        i_new = i + lr * grad_i + lr * i_attraction

        d = np.clip(d_new, 0.05, 0.95)
        p = np.clip(p_new, 0.10, 0.95)
        i = np.clip(i_new, 0.05, 0.95)

    # 궤적 시각화
    print()
    print("─" * 70)
    print("  [ 탐색 궤적 ]")
    print("─" * 70)

    # Inhibition 궤적
    print()
    print("  Inhibition 궤적 (골든 존 = 0.24~0.48):")
    for h in history:
        pos = int(h['i'] / 1.0 * 60)
        golden_lo = int(0.24 * 60)
        golden_hi = int(0.48 * 60)
        line = list("·" * 61)
        for gi in range(golden_lo, golden_hi + 1):
            line[gi] = "░"
        marker = "🎯" if h['n_agree'] == 3 else ("⚡" if h['n_agree'] == 2 else "○")
        if pos < len(line):
            line[pos] = "●"
        print(f"    {h['iter']:>3} │{''.join(line)}│ I={h['i']:.2f} {marker}")
    print(f"        {'':>1}{'0.0':.<20}{'0.24':.<14}{'0.48':.<14}{'1.0'}")
    print(f"        {'':>1}{'':>20}└─ 골든 존 ─┘")

    # Compass Score 궤적
    print()
    print("  Compass Score 궤적:")
    for h in history:
        bar_len = int(h['compass_score'] * 50)
        bar = "█" * bar_len + "░" * (50 - bar_len)
        marker = "🎯" if h['n_agree'] == 3 else ""
        print(f"    {h['iter']:>3} │{bar}│ {h['compass_score']*100:5.1f}% {marker}")

    # 종합 보고
    print()
    print("─" * 70)
    print("  [ 종합 보고 ]")
    print("─" * 70)
    print(f"    총 반복 횟수      : {len(history)}")
    print(f"    골든 존 도달 횟수  : {golden_zone_hits}")
    print(f"    최종 파라미터     : D={d:.2f} / P={p:.2f} / I={i:.2f}")

    if history:
        best = max(history, key=lambda x: x['compass_score'])
        print(f"    최고 Compass Score : {best['compass_score']*100:.1f}% (iter {best['iter']})")
        print(f"    최고 시 파라미터   : D={best['d']:.2f} / P={best['p']:.2f} / I={best['i']:.2f}")

    first = history[0]
    last = history[-1]
    print()
    print(f"    시작 → 종료:")
    print(f"      D: {first['d']:.2f} → {last['d']:.2f}  ({'+' if last['d']>first['d'] else ''}{last['d']-first['d']:.2f})")
    print(f"      P: {first['p']:.2f} → {last['p']:.2f}  ({'+' if last['p']>first['p'] else ''}{last['p']-first['p']:.2f})")
    print(f"      I: {first['i']:.2f} → {last['i']:.2f}  ({'+' if last['i']>first['i'] else ''}{last['i']-first['i']:.2f})")
    print(f"      Compass: {first['compass_score']*100:.1f}% → {last['compass_score']*100:.1f}%")

    print()
    print("═" * 70)

    # 기록 저장
    os.makedirs(RESULTS_DIR, exist_ok=True)
    pilot_file = os.path.join(RESULTS_DIR, "autopilot_log.md")
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    with open(pilot_file, 'a', encoding='utf-8') as f:
        f.write(f"# 🚀 Autopilot 탐색 [{now}]\n\n")
        f.write(f"초기: D={d0:.2f} / P={p0:.2f} / I={i0:.2f} → 최종: D={d:.2f} / P={p:.2f} / I={i:.2f}\n\n")
        f.write(f"| Iter | D | P | I | Z-Score | Compass | 합의 |\n|---|---|---|---|---|---|---|\n")
        for h in history:
            agree_label = "🎯" if h['n_agree'] == 3 else ("⚡" if h['n_agree'] == 2 else "○")
            f.write(f"| {h['iter']} | {h['d']:.2f} | {h['p']:.2f} | {h['i']:.2f} | {h['z']:.2f}σ | {h['compass_score']*100:.1f}% | {agree_label} |\n")
        f.write(f"\n골든 존 도달: {golden_zone_hits}회\n\n---\n\n")

    print(f"  📁 탐색 기록 → results/autopilot_log.md")
    print()


def main():
    parser = argparse.ArgumentParser(description="SingularityNet 아키텍처 나침반")
    parser.add_argument('--deficit', type=float, default=0.7, help="구조적 결손 (Dropout Rate)")
    parser.add_argument('--plasticity', type=float, default=0.8, help="신경가소성 (Learning Rate 계수)")
    parser.add_argument('--inhibition', type=float, default=0.15, help="억제 수준 (Gating 강도)")
    parser.add_argument('--convergence', action='store_true', help="3모델 공통 특이점 영역 탐색")
    parser.add_argument('--autopilot', action='store_true', help="가설 반복 자동 탐색")
    parser.add_argument('--iterations', type=int, default=30, help="autopilot 최대 반복 횟수")
    parser.add_argument('--lr', type=float, default=0.15, help="autopilot 학습률")
    parser.add_argument('--grid', type=int, default=20, help="격자 해상도")
    parser.add_argument('--samples', type=int, default=50000, help="모집단 샘플 수")
    args = parser.parse_args()

    if args.convergence:
        run_convergence_scan(args.grid, args.samples)
        return

    if args.autopilot:
        run_autopilot(args.deficit, args.plasticity, args.inhibition,
                      args.iterations, args.lr, args.samples)
        return

    d = np.clip(args.deficit, 0.01, 0.99)
    p = np.clip(args.plasticity, 0.01, 0.99)
    i = np.clip(args.inhibition, 0.01, 0.99)

    # ── 3개 모델 실행 ──
    score = genius_score(d, p, i)
    z, pop_mean, pop_std = population_zscore(score)
    cusp = cusp_analysis(d, i)
    boltz = boltzmann_analysis(d, p, i)
    compass = compass_direction(score, z, cusp, boltz)

    # ── 출력 ──
    print()
    print("═" * 60)
    print("   🧭 SingularityNet 아키텍처 나침반")
    print("═" * 60)

    # 입력
    print()
    print(f"  입력 (AI 아키텍처 매핑):")
    print(f"    Deficit     = {d:.2f}  → Dropout Rate")
    print(f"    Plasticity  = {p:.2f}  → Learning Rate 계수")
    print(f"    Inhibition  = {i:.2f}  → Gating 강도")

    # 모델 1: 우리 모델
    print()
    print("─" * 60)
    print("  📊 모델 1: 현재 점수 (우리 모델)")
    print("─" * 60)
    print(f"    Genius Score = {score:.2f}")
    print(f"    Z-Score      = {z:.2f}σ  {'⚡ 특이점!' if abs(z) > 2 else '○ 정상'}")
    print(f"    백분위       = 상위 {(1-stats.norm.cdf(z))*100:.4f}%")

    # 모델 2: 커스프 파국
    print()
    print("─" * 60)
    print("  📐 모델 2: 임계점 분석 (커스프 파국)")
    print("─" * 60)
    print(f"    제어 변수    a={cusp['a']:.2f}, b={cusp['b']:.2f}")
    print(f"    분기 판별식  = {cusp['bifurcation']:.4f}")
    print(f"    임계점 거리  = {cusp['distance_to_critical']:.4f}")
    print(f"    안정점 개수  = {cusp['n_equilibria']}개 {'(이중 안정 → 전이 가능!)' if cusp['is_bistable'] else '(단일 안정)'}")
    print(f"    전이 방향    = {cusp['direction']}")

    # 모델 3: 볼츠만
    print()
    print("─" * 60)
    print("  🌡️ 모델 3: 전이 확률 (볼츠만 분포)")
    print("─" * 60)
    print(f"    온도 T       = {boltz['temperature']:.2f} (= 1/Inhibition)")
    print(f"    ────────────────────────────────────")
    print(f"    정상 상태    = {boltz['p_normal']*100:5.1f}%  E={boltz['E_normal']:.2f}")
    print(f"    천재성 상태  = {boltz['p_genius']*100:5.1f}%  E={boltz['E_genius']:.2f}")
    print(f"    기능저하     = {boltz['p_decline']*100:5.1f}%  E={boltz['E_decline']:.2f}")
    print(f"    ────────────────────────────────────")
    print(f"    자유 에너지  = {boltz['free_energy']:.4f}")
    print(f"    엔트로피     = {boltz['entropy']:.4f}")

    # 나침반
    print()
    print("─" * 60)
    print("  🧭 나침반 — 종합 설계 방향")
    print("─" * 60)
    print()
    print(draw_compass(
        compass['compass_score'],
        cusp['direction_sign'],
        boltz['p_genius'],
        cusp['distance_to_critical'],
    ))

    # 권장사항
    print()
    print("─" * 60)
    print("  📋 아키텍처 설계 권장사항")
    print("─" * 60)
    for area, rec, grade in compass['recommendations']:
        print(f"    [{grade:^5}] {area:12} │ {rec}")

    if compass['warnings']:
        print()
        for w in compass['warnings']:
            print(f"    ⚠️  {w}")

    # AI 아키텍처 매핑 요약
    print()
    print("─" * 60)
    print("  🔧 구체적 설계 파라미터")
    print("─" * 60)
    print(f"    Dropout Rate     = {d:.0%}")
    print(f"    Learning Rate    × {boltz['temperature']:.1f} (볼츠만 온도)")
    print(f"    MoE Active Ratio = {compass['optimal_active_ratio']:.0%}")
    print(f"    Expert 수 64개 기준 → 활성 {int(64*compass['optimal_active_ratio'])}개")
    print(f"    구조 재편 트리거  = Loss 2차미분 > {1/max(cusp['distance_to_critical'],0.01):.1f}")

    print()
    print("═" * 60)

    # 기록
    save_compass_log(d, p, i, score, z, cusp, boltz, compass)
    print(f"  📁 나침반 기록 → results/compass_log.md")
    print()


if __name__ == '__main__':
    main()
