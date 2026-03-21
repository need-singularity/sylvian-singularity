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


def main():
    parser = argparse.ArgumentParser(description="SingularityNet 아키텍처 나침반")
    parser.add_argument('--deficit', type=float, default=0.7, help="구조적 결손 (Dropout Rate)")
    parser.add_argument('--plasticity', type=float, default=0.8, help="신경가소성 (Learning Rate 계수)")
    parser.add_argument('--inhibition', type=float, default=0.15, help="억제 수준 (Gating 강도)")
    args = parser.parse_args()

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
