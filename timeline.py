#!/usr/bin/env python3
"""LLM 특이점 도달 시점 예측"""

import numpy as np
import os
from datetime import datetime

RESULTS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "results")


def predict_timeline():
    """실측 데이터로 λ를 피팅하고 특이점 도달 시점 예측"""

    # 실측 데이터 포인트
    data = {
        'GPT-2':    {'year': 2019, 'I': 0.875},
        'GPT-3':    {'year': 2020, 'I': 0.75},   # 추정
        'Mixtral':  {'year': 2023, 'I': 0.875},   # MoE지만 Gating 동일
        'GPT-4':    {'year': 2023, 'I': 0.50},
        'Claude-3': {'year': 2024, 'I': 0.45},    # 추정
        'GPT-4o':   {'year': 2024, 'I': 0.42},    # 추정
    }

    I_golden = 1 / np.e  # 0.3679

    # 기준점: GPT-2 (2019) → GPT-4 (2023)
    t0_year = 2019
    I_0 = 0.875

    # I(t) = I_golden + (I_0 - I_golden) * e^(-λt)
    # GPT-4: t=4, I=0.50
    # 0.50 = 0.368 + 0.507 * e^(-4λ)
    # e^(-4λ) = (0.50 - 0.368) / 0.507 = 0.260
    # λ = -ln(0.260) / 4
    lambda_fit = -np.log((0.50 - I_golden) / (I_0 - I_golden)) / 4

    def I_predict(year):
        t = year - t0_year
        return I_golden + (I_0 - I_golden) * np.exp(-lambda_fit * t)

    # 특이점 도달 시점: I(t) ≤ I_golden + ε
    thresholds = [0.40, 0.39, 0.38, 0.375, 0.370, 0.3685, 0.3680]

    print()
    print("═" * 70)
    print("   📅 LLM 특이점 도달 시점 예측")
    print("═" * 70)

    print()
    print(f"  진화 경로 함수:")
    print(f"    I(t) = 1/e + (I₀ - 1/e) × e^(-λt)")
    print(f"    I₀ = {I_0} (GPT-2, 2019)")
    print(f"    I_golden = 1/e = {I_golden:.4f}")
    print(f"    λ = {lambda_fit:.4f} (GPT-2→GPT-4 피팅)")
    print()

    # 실측 vs 예측
    print("─" * 70)
    print("  [ 실측 데이터 vs 모델 예측 ]")
    print("─" * 70)
    print(f"  {'모델':12} │ {'연도':>4} │ {'실측 I':>7} │ {'예측 I':>7} │ {'오차':>7} │ 상태")
    print(f"  {'─'*12}─┼─{'─'*4}─┼─{'─'*7}─┼─{'─'*7}─┼─{'─'*7}─┼─{'─'*15}")
    for name, d in data.items():
        pred_I = I_predict(d['year'])
        err = d['I'] - pred_I
        status = "골든존" if d['I'] <= 0.48 else "밖"
        print(f"  {name:12} │ {d['year']:>4} │ {d['I']:>7.3f} │ {pred_I:>7.3f} │ {err:>+7.3f} │ {status}")

    # 미래 예측
    print()
    print("─" * 70)
    print("  [ 미래 예측 — 특이점까지 ]")
    print("─" * 70)
    print()

    future_years = list(range(2025, 2045))
    for year in future_years:
        I_pred = I_predict(year)
        delta = I_pred - I_golden
        bar_pos = int((I_pred - 0.30) / 0.60 * 50)
        bar_pos = max(0, min(49, bar_pos))
        golden_lo = int((0.24 - 0.30) / 0.60 * 50)
        golden_hi = int((0.48 - 0.30) / 0.60 * 50)
        golden_lo = max(0, golden_lo)

        line = list("·" * 50)
        for gi in range(golden_lo, golden_hi + 1):
            if 0 <= gi < 50:
                line[gi] = "░"
        if 0 <= bar_pos < 50:
            line[bar_pos] = "●"

        if I_pred <= I_golden + 0.001:
            marker = "🎯 특이점!"
        elif I_pred <= 0.40:
            marker = "⚡ 골든존 중심부"
        elif I_pred <= 0.48:
            marker = "★ 골든존"
        elif I_pred <= 0.50:
            marker = "· 임계선"
        else:
            marker = ""

        print(f"    {year} │{''.join(line)}│ I={I_pred:.4f} ΔI={delta:+.4f} {marker}")

    print(f"         {'':>1}{'0.30':.<15}{'0.48':.<15}{'0.90'}")
    print(f"         {'':>1}{'':>5}└─ 골든존 ─┘")

    # 특이점 도달 시점 계산
    print()
    print("─" * 70)
    print("  [ 특이점 도달 시점 ]")
    print("─" * 70)
    print(f"  {'임계값':>10} │ {'도달 연도':>10} │ {'Δ(현재)':>10} │ 의미")
    print(f"  {'─'*10}─┼─{'─'*10}─┼─{'─'*10}─┼─{'─'*20}")
    for thr in thresholds:
        # I_golden + (I_0 - I_golden) * e^(-λt) = thr
        # e^(-λt) = (thr - I_golden) / (I_0 - I_golden)
        ratio = (thr - I_golden) / (I_0 - I_golden)
        if ratio > 0:
            t_reach = -np.log(ratio) / lambda_fit
            year_reach = t0_year + t_reach
            delta_now = year_reach - 2026
            if thr <= I_golden + 0.001:
                meaning = "수학적 특이점 (≈1/e)"
            elif thr <= 0.375:
                meaning = "실질적 특이점"
            elif thr <= 0.38:
                meaning = "골든존 깊숙이"
            elif thr <= 0.39:
                meaning = "골든존 중심부"
            else:
                meaning = "골든존 진입"
            print(f"  I≤{thr:.4f} │ {year_reach:>10.1f} │ {delta_now:>+9.1f}년 │ {meaning}")

    # 시나리오 분석
    print()
    print("─" * 70)
    print("  [ 시나리오 분석 ]")
    print("─" * 70)

    # 시나리오 1: 현재 속도 유지 (λ=0.337)
    t_sing_base = -np.log(0.002 / 0.507) / lambda_fit
    year_base = t0_year + t_sing_base

    # 시나리오 2: 가속 (λ×1.5) — AI 투자 급증, 골든 MoE 인식
    lambda_fast = lambda_fit * 1.5
    t_sing_fast = -np.log(0.002 / 0.507) / lambda_fast
    year_fast = t0_year + t_sing_fast

    # 시나리오 3: 감속 (λ×0.7) — 규제, 기술 한계
    lambda_slow = lambda_fit * 0.7
    t_sing_slow = -np.log(0.002 / 0.507) / lambda_slow
    year_slow = t0_year + t_sing_slow

    # 시나리오 4: 정체 후 돌파 (S-커브)
    # 2026-2030 정체 후 2030-2035 급가속
    year_scurve = 2037  # 추정

    print()
    print(f"  {'시나리오':20} │ {'λ':>6} │ {'도달 연도':>8} │ 근거")
    print(f"  {'─'*20}─┼─{'─'*6}─┼─{'─'*8}─┼─{'─'*30}")
    print(f"  {'현재 속도 유지':20} │ {lambda_fit:>6.3f} │ {year_base:>8.1f} │ GPT-2→GPT-4 추세 연장")
    print(f"  {'가속 (×1.5)':20} │ {lambda_fast:>6.3f} │ {year_fast:>8.1f} │ 골든 MoE 인식, 투자 급증")
    print(f"  {'감속 (×0.7)':20} │ {lambda_slow:>6.3f} │ {year_slow:>8.1f} │ 규제, 에너지 한계")
    print(f"  {'S-커브 (정체→돌파)':20} │ {'가변':>6} │ {'~2037':>8} │ 2026-30 정체 후 급가속")

    # 2039년 검증
    I_2039 = I_predict(2039)
    print()
    print("─" * 70)
    print("  [ 가설 검증: 특이점 시점 = 2039년 ]")
    print("─" * 70)
    print(f"    2039년 예측 I = {I_2039:.4f}")
    print(f"    골든존 중심 I = {I_golden:.4f}")
    print(f"    차이 ΔI       = {I_2039 - I_golden:+.4f}")
    print()

    if abs(I_2039 - I_golden) < 0.005:
        verdict = "🎯 2039년에 특이점 도달 — 가설 지지"
    elif I_2039 < 0.40:
        verdict = "⚡ 2039년에 골든존 중심부 — 특이점에 매우 근접"
    elif I_2039 < 0.48:
        verdict = "★ 2039년에 골든존 내부 — 특이점 이전 단계"
    else:
        verdict = "○ 2039년에 골든존 미도달"

    print(f"    판정: {verdict}")

    # 모든 시나리오에서 2039년 검증
    print()
    for name, lam in [("현재속도", lambda_fit), ("가속", lambda_fast), ("감속", lambda_slow)]:
        I_val = I_golden + (I_0 - I_golden) * np.exp(-lam * (2039 - t0_year))
        status = "🎯 특이점" if abs(I_val - I_golden) < 0.005 else ("⚡ 근접" if I_val < 0.40 else "★ 골든존" if I_val < 0.48 else "○ 미도달")
        print(f"    {name:8} 시나리오: 2039년 I = {I_val:.4f}  {status}")

    print()
    print("═" * 70)

    # 보고서 저장
    os.makedirs(RESULTS_DIR, exist_ok=True)
    timeline_file = os.path.join(RESULTS_DIR, "timeline_report.md")
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    with open(timeline_file, 'a', encoding='utf-8') as f:
        f.write(f"# 특이점 타임라인 예측 [{now}]\n\n")
        f.write(f"λ = {lambda_fit:.4f} (GPT-2→GPT-4 피팅)\n\n")
        f.write(f"| 시나리오 | 도달 연도 |\n|---|---|\n")
        f.write(f"| 현재 속도 | {year_base:.1f} |\n")
        f.write(f"| 가속 ×1.5 | {year_fast:.1f} |\n")
        f.write(f"| 감속 ×0.7 | {year_slow:.1f} |\n")
        f.write(f"| S-커브 | ~2037 |\n\n")
        f.write(f"2039년 예측 I = {I_2039:.4f} (ΔI = {I_2039-I_golden:+.4f})\n\n---\n\n")

    print(f"  📁 타임라인 보고서 → results/timeline_report.md")
    print()


if __name__ == '__main__':
    predict_timeline()
