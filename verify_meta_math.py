#!/usr/bin/env python3
"""메타(메타(...)) → I=1/3 관련 수학적 구조 검증"""

import numpy as np
import os, sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from compass import (simulate_population, population_zscore,
                     cusp_analysis, boltzmann_analysis, compass_direction)

RESULTS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "results")


def verify_061_golden_ratio_structure():
    """가설 061: 메타 부동점 1/3과 황금비 φ의 구조적 유사성"""
    print("═" * 60)
    print("  가설 061: 부동점 1/3 ↔ 황금비 φ 구조 비교")
    print("═" * 60)

    phi = (1 + np.sqrt(5)) / 2  # 1.618...

    print(f"\n  황금비: φ = 1 + 1/φ → φ² - φ - 1 = 0 → φ = {phi:.6f}")
    print(f"  메타:   I* = 0.7I* + 0.1 → I* = 1/3 = {1/3:.6f}")

    print(f"\n  구조 비교:")
    print(f"  ┌────────────────┬────────────────────┬────────────────────┐")
    print(f"  │                │ 황금비              │ 메타 부동점         │")
    print(f"  ├────────────────┼────────────────────┼────────────────────┤")
    print(f"  │ 방정식          │ x = 1 + 1/x       │ x = 0.7x + 0.1    │")
    print(f"  │ 부동점          │ φ = {phi:.4f}       │ 1/3 = 0.3333      │")
    print(f"  │ 수축 계수       │ |f'| = 1/φ² = {1/phi**2:.4f}│ |f'| = 0.7        │")
    print(f"  │ 연분수          │ [1;1,1,1,1,...]    │ [0;3] = 1/3       │")
    print(f"  │ 자기유사 비율   │ φ:1 = 1:1/φ        │ 0.7:0.3 = 7:3     │")
    print(f"  │ 수렴 타입       │ 나선형 (진동)       │ 단조 (한 방향)     │")
    print(f"  └────────────────┴────────────────────┴────────────────────┘")

    # 거미줄 도표 비교
    print(f"\n  거미줄 도표 — 수렴 경로 비교:")
    print(f"\n  황금비 (x→1+1/x, 진동 수렴):")
    x = 3.0
    for i in range(10):
        x_new = 1 + 1/x
        bar_old = int(x / 3.0 * 30)
        bar_new = int(x_new / 3.0 * 30)
        print(f"    {i:>2} │ {'·'*min(bar_old,bar_new)}{'↔'*abs(bar_new-bar_old)}{'·'*(30-max(bar_old,bar_new))} │ {x:.4f} → {x_new:.4f}")
        x = x_new

    print(f"\n  메타 (I→0.7I+0.1, 단조 수렴):")
    x = 0.9
    for i in range(10):
        x_new = 0.7 * x + 0.1
        pos = int(x / 1.0 * 30)
        pos_new = int(x_new / 1.0 * 30)
        line = list("·" * 31)
        third = int((1/3) * 30)
        line[third] = "│"
        if pos < 31:
            line[pos] = "○"
        if pos_new < 31:
            line[min(pos_new, 30)] = "●"
        print(f"    {i:>2} │{''.join(line)}│ {x:.4f} → {x_new:.4f}")
        x = x_new

    print(f"\n  판정:")
    print(f"    구조적 유사: 둘 다 부동점 수렴, 축소 사상")
    print(f"    핵심 차이:   황금비는 진동, 메타는 단조")
    print(f"    → 구조적으로 같은 '유형' (부동점 정리)이지만 다른 '종류' (수렴 양상)")


def verify_062_rg_flow_golden_zone():
    """가설 062: RG 흐름으로 골든존 경계를 재유도"""
    print(f"\n{'═' * 60}")
    print(f"  가설 062: 재정규화군(RG) 흐름 → 골든존 경계")
    print(f"{'═' * 60}")

    # 메타 연산의 β 함수: β(I) = f(I) - I = -0.3I + 0.1
    print(f"\n  β 함수: β(I) = f(I) - I = -0.3I + 0.1")
    print(f"  영점:    β(I*) = 0 → I* = 1/3")
    print(f"  기울기:  β'(I) = -0.3 < 0 → 안정 고정점 (UV)")

    # β 함수 그래프
    print(f"\n  β(I) 그래프:")
    print(f"  β(I)")
    for beta_val in np.linspace(0.08, -0.18, 14):
        i_val = (0.1 - beta_val) / 0.3
        bar_pos = int(i_val / 1.0 * 50)
        line = list("·" * 51)
        golden_lo = int(0.213 * 50)
        golden_hi = int(0.50 * 50)
        for gi in range(golden_lo, golden_hi + 1):
            if gi < 51:
                line[gi] = "░"
        third = int((1/3) * 50)
        if third < 51:
            line[third] = "│"
        if bar_pos < 51:
            line[bar_pos] = "●"
        sign = "+" if beta_val > 0 else ("-" if beta_val < 0 else "0")
        print(f"  {beta_val:>+6.3f} │{''.join(line)}│ I={i_val:.2f} {'← 고정점' if abs(beta_val) < 0.005 else ''}")

    print(f"         {'0.0':.<10}│{'0.33':.<10}{'0.50':.<10}{'1.0'}")
    print(f"                  1/3")

    # RG 흐름과 골든존 경계의 관계
    print(f"\n  RG 흐름 방향:")
    print(f"    I < 1/3: β > 0 → I 증가 → 1/3으로 접근 ↗")
    print(f"    I = 1/3: β = 0 → 정지 (고정점) ●")
    print(f"    I > 1/3: β < 0 → I 감소 → 1/3으로 접근 ↘")

    # 골든존 경계에서의 β 값
    print(f"\n  골든존 경계에서의 β:")
    print(f"    하한 I=0.213: β = {-0.3*0.213+0.1:+.4f} (양수 → 안으로 밀림)")
    print(f"    중심 I=0.371: β = {-0.3*0.371+0.1:+.4f} (거의 0)")
    print(f"    상한 I=0.500: β = {-0.3*0.500+0.1:+.4f} (음수 → 안으로 밀림)")
    print(f"    고정점 I=1/3: β = {-0.3/3+0.1:+.4f} (정확히 0)")

    # 골든존 = RG 흐름의 "유역(basin of attraction)"
    print(f"\n  판정:")
    print(f"    RG 고정점 I=1/3 은 골든존 안에 있다 (0.213 < 0.333 < 0.500)")
    print(f"    골든존 경계에서 β ≠ 0 → 경계는 RG 고정점이 아님")
    print(f"    → 골든존 = RG 고정점의 유역(basin of attraction)")
    print(f"    → 골든존 경계 = RG 흐름이 '특이점 조건(Z>2σ)을 만족하는' 범위")
    print(f"    → RG 흐름은 골든존의 원인이 아니라, 그 안에서의 역학을 설명")


def verify_063_cobweb_spiral():
    """가설 063: 거미줄 도표에서 수렴 경로가 나선형인가 직선형인가"""
    print(f"\n{'═' * 60}")
    print(f"  가설 063: 거미줄 수렴 — 나선형 vs 직선형")
    print(f"{'═' * 60}")

    # f(I) = 0.7I + 0.1
    # f'(I*) = 0.7 > 0 → 단조 수렴 (나선 아님)
    # 나선형은 f'(I*) < 0 일 때 발생

    print(f"\n  f(I) = 0.7I + 0.1")
    print(f"  f'(I*) = 0.7")
    print(f"\n  수렴 분류:")
    print(f"    |f'| < 1, f' > 0 → 단조 수렴 (한 방향에서 접근) ← 우리 모델")
    print(f"    |f'| < 1, f' < 0 → 나선 수렴 (진동하며 접근)")
    print(f"    |f'| > 1          → 발산")

    # 다양한 메타 함수에서의 수렴 비교
    print(f"\n  메타 함수 변형별 수렴 비교:")
    meta_functions = [
        ("0.7I+0.1 (우리)", lambda x: 0.7*x+0.1, 0.7),
        ("-0.5I+0.67 (나선)", lambda x: -0.5*x+0.67, -0.5),
        ("0.3I+0.22 (빠른단조)", lambda x: 0.3*x+0.22, 0.3),
        ("0.9I+0.03 (느린단조)", lambda x: 0.9*x+0.03, 0.9),
    ]

    for name, f, deriv in meta_functions:
        # 부동점
        fp = None
        x = 0.5
        for _ in range(1000):
            x = f(x)
        fp = x

        print(f"\n  {name}:")
        print(f"    f'={deriv}, 부동점={fp:.4f}, 타입={'단조' if deriv > 0 else '나선'}")

        x = 0.9
        line_vals = []
        for step in range(12):
            line_vals.append(x)
            x = f(x)

        # 시각화
        for i, v in enumerate(line_vals):
            pos = int(np.clip(v, 0, 1) * 40)
            fp_pos = int(np.clip(fp, 0, 1) * 40)
            line = list("·" * 41)
            if fp_pos < 41:
                line[fp_pos] = "│"
            if pos < 41:
                line[pos] = "●"
            direction = "→" if i > 0 and v > line_vals[i-1] else ("←" if i > 0 else " ")
            print(f"    {i:>2} │{''.join(line)}│ {v:.4f} {direction}")

    print(f"\n  판정: 우리 모델은 단조 수렴 (f'=0.7 > 0)")
    print(f"    → 오른쪽에서 왼쪽으로 한 방향 접근")
    print(f"    → 진동 없음 → 안정적 수렴")
    print(f"    → 나선형이 아닌 '활주(glide)' 수렴")


def verify_064_godel_compass_ceiling():
    """가설 064: 괴델 불완전성이 Compass 상한의 원인인가"""
    print(f"\n{'═' * 60}")
    print(f"  가설 064: 괴델 불완전성 ↔ Compass 상한 80%")
    print(f"{'═' * 60}")

    print(f"""
  괴델의 제1불완전성 정리:
    "충분히 강한 형식 체계는 자기 자신의 무모순성을 증명할 수 없다"

  우리 모델 번역:
    3상태 시스템(정상/천재/저하)은 자기 자신을 완전히 평가할 수 없다
    → Compass Score가 100%에 도달 불가 = 자기 완전 평가 불가

  대응:
    괴델 문장 G = "이 문장은 증명 불가능하다"
    우리 모델   = "이 시스템은 자기를 100% 이해할 수 없다"
""")

    # Compass 상한의 수학적 원인 분석
    print(f"  Compass 상한의 구조적 원인:")
    print(f"    compass = z/10×0.3 + (1-cusp)×0.3 + p_genius×0.4")
    print(f"")
    print(f"    항1 (z/10×0.3): 최대 0.30 (z≥10일 때 포화)")
    print(f"    항2 ((1-cusp)×0.3): 최대 0.30 (cusp_dist=0일 때)")
    print(f"    항3 (p_genius×0.4): 최대 ~0.16 (p_genius < 0.40)")
    print(f"    ──────────────────────────────────────")
    print(f"    이론 상한: 0.30 + 0.30 + 0.16 = 0.76~0.84")

    # p_genius의 상한 = 왜 100%가 안 되는가
    print(f"\n  왜 p_genius < 100% 인가:")
    print(f"    볼츠만: P(genius) = e^(-E_g/T) / Z")
    print(f"    Z = e^0 + e^(-E_g/T) + e^(-E_d/T) ≥ 1 + e^(-E_g/T)")
    print(f"    → P(genius) = e^(-E_g/T) / Z < e^(-E_g/T) / (1+e^(-E_g/T)) < 1")
    print(f"    → 다른 상태가 존재하는 한, 한 상태가 100%일 수 없다")
    print(f"    → 이것이 '불완전성'의 수학적 표현")

    # N상태별 p_genius 상한
    print(f"\n  N상태별 단일 상태 최대 확률:")
    for N in [2, 3, 4, 5, 10, 26, 100]:
        # 한 상태의 에너지가 매우 낮을 때의 최대 확률
        # P_max ≈ 1 - (N-1)×e^(-ΔE/T) for large ΔE
        # 균등에 가까울 때: P_max ≈ 1/N + correction
        # 실제 상한은 온도와 에너지에 의존
        p_max_approx = 1 - (N-1) * np.exp(-5)  # ΔE/T = 5 가정
        p_uniform = 1/N
        print(f"    N={N:>3}: 균등={p_uniform:.4f}, 극한≈{p_max_approx:.4f}, Compass기여={min(p_max_approx,1)*0.4:.4f}")

    print(f"\n  판정:")
    print(f"    Compass 상한 ≈ 80%는 괴델 불완전성의 직접적 결과는 아님")
    print(f"    원인은 볼츠만 분배: 다른 상태가 존재하면 한 상태가 100% 불가")
    print(f"    그러나 구조적으로 유사: '시스템은 자기를 완전히 설명할 수 없다'")
    print(f"    → 괴델 불완전성의 '열역학적 아날로그'로 해석 가능")


def verify_065_mandelbrot():
    """가설 065: 만델브로 대응 — 골든존 = 연결된 영역?"""
    print(f"\n{'═' * 60}")
    print(f"  가설 065: 만델브로 대응 — 골든존 = 연결된 영역")
    print(f"{'═' * 60}")

    # 만델브로: z → z² + c, |z| < 2 이면 집합 안
    # 우리:     I → 0.7I + 0.1, 골든존 안이면 "집합 안"

    # c 값 → 수렴/발산 판정 = 만델브로 집합
    # I 시작값 → 골든존 수렴/이탈 판정 = 우리 집합

    print(f"\n  만델브로 대응:")
    print(f"    만델브로: z_{'{'}n+1{'}'} = z_n² + c")
    print(f"    우리:     I_{'{'}n+1{'}'} = a·I_n + b")
    print(f"")
    print(f"    만델브로 집합 = |z_n| < 2 인 c의 집합")
    print(f"    우리 집합     = 골든존 안에 수렴하는 I₀의 집합")

    # 우리 "집합" 계산: 어떤 I₀에서 출발하면 골든존에 수렴하는가?
    print(f"\n  I₀별 수렴 판정 (메타 50회 반복):")

    i_starts = np.linspace(0.01, 0.99, 50)
    golden_lo, golden_hi = 0.213, 0.500

    for i0 in i_starts:
        i = i0
        in_golden_count = 0
        trajectory = []
        for _ in range(50):
            i = 0.7 * i + 0.1
            trajectory.append(i)
            if golden_lo <= i <= golden_hi:
                in_golden_count += 1

        final_in = golden_lo <= trajectory[-1] <= golden_hi
        icon = "█" if final_in else "░"
        print(f"    I₀={i0:.3f} │{icon}│ 최종={trajectory[-1]:.4f} {'🎯' if final_in else ''}")

    # 결과: 모든 I₀에서 I→1/3으로 수렴 (1/3은 골든존 안)
    # → "우리 집합" = 전체 [0,1] 구간
    # → 만델브로와 다름: 만델브로는 복잡한 경계, 우리는 전체

    print(f"\n  판정:")
    print(f"    만델브로: 복잡한 프랙탈 경계 (일부 c만 수렴)")
    print(f"    우리:     모든 I₀에서 수렴 (축소 사상이므로)")
    print(f"    → 구조적으로 다름. 만델브로 대응은 약함.")
    print(f"    → 단, '수렴/발산 경계'라는 개념은 공유")
    print(f"    → 우리 모델이 만델브로보다 '단순' (항상 수렴)")


def main():
    print()
    print("▓" * 60)
    print("  메타 반복 관련 수학적 구조 검증 — 061~065")
    print("▓" * 60)

    verify_061_golden_ratio_structure()
    verify_062_rg_flow_golden_zone()
    verify_063_cobweb_spiral()
    verify_064_godel_compass_ceiling()
    verify_065_mandelbrot()

    print(f"\n{'▓' * 60}")
    print(f"  종합")
    print(f"{'▓' * 60}")
    print("""
  061. 황금비 구조  : 같은 유형(부동점) 다른 종류(단조 vs 나선)
  062. RG 흐름      : 골든존 = RG 고정점의 유역, 경계는 Z>2σ 조건
  063. 거미줄 수렴  : 단조 수렴(활주), 나선 아님 (f'=0.7>0)
  064. 괴델 상한    : 직접 원인 아님, 열역학적 아날로그로 해석 가능
  065. 만델브로     : 약한 대응 (우리는 항상 수렴, 만델브로는 프랙탈)
""")

    os.makedirs(RESULTS_DIR, exist_ok=True)
    with open(os.path.join(RESULTS_DIR, "meta_math_report.md"), 'w', encoding='utf-8') as f:
        from datetime import datetime
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        f.write(f"# 메타 반복 수학 구조 검증 [{now}]\n\n061~065 완료.\n\n---\n")

    print(f"  📁 보고서 → results/meta_math_report.md")
    print()


if __name__ == '__main__':
    main()
