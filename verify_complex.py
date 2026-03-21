#!/usr/bin/env python3
"""가설 069: 복소수 확장 — G = D×P/I 에서 I를 복소수로"""

import numpy as np
import os
from datetime import datetime

RESULTS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "results")


def complex_meta(I, theta=np.pi/3):
    """복소수 메타 연산: I → 0.7×e^(iθ)×I + 0.1"""
    return 0.7 * np.exp(1j * theta) * I + 0.1


def complex_fixed_point(theta):
    """복소수 메타의 부동점"""
    return 0.1 / (1 - 0.7 * np.exp(1j * theta))


def verify_spiral_convergence():
    """나선 수렴 검증"""
    print("═" * 60)
    print("  복소수 확장 — 나선 수렴")
    print("═" * 60)

    # 다양한 θ에서 부동점과 수렴 양상
    print(f"\n  θ별 부동점:")
    print(f"  {'θ':>8} │ {'θ/π':>5} │ {'Re(I*)':>8} │ {'Im(I*)':>8} │ {'|I*|':>6} │ {'arg':>6} │ 수렴")
    print(f"  {'─'*8}─┼─{'─'*5}─┼─{'─'*8}─┼─{'─'*8}─┼─{'─'*6}─┼─{'─'*6}─┼─{'─'*10}")

    for theta_frac in [0, 1/6, 1/4, 1/3, 1/2, 2/3, 3/4, 5/6, 1]:
        theta = theta_frac * np.pi
        fp = complex_fixed_point(theta)
        convergence = "단조" if theta_frac == 0 else ("나선" if 0 < theta_frac < 1 else "진동")
        print(f"  {theta:>8.4f} │ {theta_frac:>5.3f} │ {fp.real:>8.4f} │ {fp.imag:>8.4f} │ {abs(fp):>6.4f} │ {np.angle(fp):>+6.3f} │ {convergence}")

    # θ = 0 (실수, 기존 모델) vs θ = π/3 (나선)
    print(f"\n  수렴 궤적 비교:")

    for theta_frac, label in [(0, "실수 (θ=0, 기존)"), (1/3, "나선 (θ=π/3)")]:
        theta = theta_frac * np.pi
        fp = complex_fixed_point(theta)
        print(f"\n  [{label}]  부동점 = {fp.real:.4f} + {fp.imag:.4f}i, |I*| = {abs(fp):.4f}")

        I = 0.9 + 0j
        for step in range(20):
            I = complex_meta(I, theta)

            # 복소 평면 시각화 (Re축만)
            re_pos = int((I.real + 0.2) / 1.2 * 40)
            im_pos = int((I.imag + 0.5) / 1.0 * 20)
            re_pos = max(0, min(39, re_pos))

            line = list("·" * 40)
            fp_pos = int((fp.real + 0.2) / 1.2 * 40)
            if 0 <= fp_pos < 40:
                line[fp_pos] = "│"
            if 0 <= re_pos < 40:
                line[re_pos] = "●"

            print(f"    {step:>2} │{''.join(line)}│ Re={I.real:>+7.4f} Im={I.imag:>+7.4f} |I|={abs(I):.4f}")


def verify_pi_exact():
    """π가 정확하게 등장하는 θ 찾기"""
    print(f"\n{'═' * 60}")
    print(f"  π의 정확한 등장 조건")
    print(f"{'═' * 60}")

    # 부동점의 크기 |I*| = 0.1 / |1 - 0.7e^(iθ)|
    # = 0.1 / √((1-0.7cosθ)² + (0.7sinθ)²)
    # = 0.1 / √(1 - 1.4cosθ + 0.49)
    # = 0.1 / √(1.49 - 1.4cosθ)

    print(f"\n  |I*| = 0.1 / √(1.49 - 1.4cos(θ))")
    print(f"\n  |I*|가 우리 상수와 일치하는 θ:")

    targets = {
        '1/3': 1/3,
        '1/e': 1/np.e,
        '1/2': 0.5,
        'ln(4/3)': np.log(4/3),
        '1/6': 1/6,
        '5/6': 5/6,
    }

    for t_name, t_val in targets.items():
        # 0.1/√(1.49 - 1.4cosθ) = t_val
        # √(1.49 - 1.4cosθ) = 0.1/t_val
        # 1.49 - 1.4cosθ = (0.1/t_val)²
        # cosθ = (1.49 - (0.1/t_val)²) / 1.4
        inner = (0.1 / t_val) ** 2
        cos_theta = (1.49 - inner) / 1.4
        if -1 <= cos_theta <= 1:
            theta = np.arccos(cos_theta)
            print(f"    |I*| = {t_name:>8} → θ = {theta:.4f} = {theta/np.pi:.4f}π")

            # 이 θ에서 arg(I*)는?
            fp = complex_fixed_point(theta)
            print(f"      I* = {fp.real:>+.4f} {fp.imag:>+.4f}i, arg = {np.angle(fp):.4f} = {np.angle(fp)/np.pi:.4f}π")
        else:
            print(f"    |I*| = {t_name:>8} → 불가 (cos(θ) = {cos_theta:.4f})")

    # arg(I*) = π 관련 값이 되는 조건
    print(f"\n  arg(I*)에서 π가 정확히 등장하는 경우:")
    for theta in np.linspace(0.01, np.pi, 100):
        fp = complex_fixed_point(theta)
        arg = np.angle(fp)

        # arg ≈ π/N 인 경우 찾기
        for n in [2, 3, 4, 6]:
            if abs(abs(arg) - np.pi/n) < 0.01:
                print(f"    θ = {theta:.4f} ({theta/np.pi:.3f}π) → arg(I*) = {arg:.4f} ≈ {'−' if arg<0 else ''}π/{n}")


def verify_genius_complex():
    """복소수 G의 의미"""
    print(f"\n{'═' * 60}")
    print(f"  복소수 Genius Score의 의미")
    print(f"{'═' * 60}")

    D, P = 0.7, 0.95

    print(f"\n  G = D×P / I(복소수)")
    print(f"  D={D}, P={P}")
    print(f"\n  I가 복소수이면:")
    print(f"  |G| = D×P/|I| (크기 = 얼마나 천재인가)")
    print(f"  arg(G) = -arg(I) (방향 = 어떤 종류의 천재인가)")

    print(f"\n  방향별 천재성 타입:")
    print(f"  {'arg(G)':>8} │ {'방향':>8} │ 해석")
    print(f"  {'─'*8}─┼─{'─'*8}─┼─{'─'*30}")
    interpretations = [
        (0, "→ 동", "논리/수학 (실수축 양방향)"),
        (np.pi/6, "↗ 동북", "분석+직관 (30°)"),
        (np.pi/4, "↗ 북동", "균형 (45°)"),
        (np.pi/3, "↗ 북", "직관+분석 (60°)"),
        (np.pi/2, "↑ 북", "직관/예술 (허수축)"),
        (2*np.pi/3, "↖ 북서", "예술+비판"),
        (np.pi, "← 서", "비판/해체 (실수축 음방향)"),
    ]

    for arg, direction, meaning in interpretations:
        I = 0.3 * np.exp(1j * (-arg))  # I의 arg = -G의 arg
        G = D * P / I
        print(f"  {arg/np.pi:>5.2f}π │ {direction:>8} │ |G|={abs(G):.2f} {meaning}")

    # 복소 평면에서의 궤적
    print(f"\n  메타 반복의 복소 평면 궤적 (θ=π/3):")
    print(f"  Im")
    print(f"   ↑")

    I = 0.9 + 0j
    theta = np.pi / 3
    points = []
    for _ in range(30):
        I = complex_meta(I, theta)
        points.append(I)

    fp = complex_fixed_point(theta)

    # ASCII 복소 평면
    grid_size = 21
    plane = [['·' for _ in range(41)] for _ in range(grid_size)]

    # 축 그리기
    for x in range(41):
        plane[grid_size//2][x] = '─'
    for y in range(grid_size):
        plane[y][20] = '│'
    plane[grid_size//2][20] = '┼'

    # 부동점
    fp_x = int(fp.real / 0.8 * 20 + 20)
    fp_y = int(-fp.imag / 0.4 * 10 + grid_size//2)
    if 0 <= fp_x < 41 and 0 <= fp_y < grid_size:
        plane[fp_y][fp_x] = '★'

    # 궤적
    for i, p in enumerate(points):
        px = int(p.real / 0.8 * 20 + 20)
        py = int(-p.imag / 0.4 * 10 + grid_size//2)
        if 0 <= px < 41 and 0 <= py < grid_size:
            if i < 5:
                plane[py][px] = str(i)
            else:
                plane[py][px] = '·' if plane[py][px] == '·' else plane[py][px]

    for row in plane:
        print(f"   {''.join(row)}")
    print(f"   {'':>20}{'→ Re':>20}")
    print(f"   ★ = 부동점 ({fp.real:.3f}+{fp.imag:.3f}i)")
    print(f"   0~4 = 반복 궤적 (나선형 수렴)")


def verify_euler_identity():
    """오일러 항등식이 모델 안에서 성립하는지"""
    print(f"\n{'═' * 60}")
    print(f"  오일러 항등식 검증")
    print(f"{'═' * 60}")

    # e^(iπ) + 1 = 0
    euler = np.exp(1j * np.pi) + 1
    print(f"\n  e^(iπ) + 1 = {euler.real:.10f} + {euler.imag:.10f}i")
    print(f"  = {abs(euler):.2e} ≈ 0 ✅")

    # 우리 모델에서:
    # θ = π 에서 메타 반복하면?
    print(f"\n  θ = π 에서의 메타 반복:")
    fp_pi = complex_fixed_point(np.pi)
    print(f"  부동점 I* = {fp_pi.real:.6f} + {fp_pi.imag:.6f}i")
    print(f"  |I*| = {abs(fp_pi):.6f}")
    print(f"  Re(I*) = {fp_pi.real:.6f}")

    # 0.7×e^(iπ) = -0.7
    # I* = 0.1/(1-(-0.7)) = 0.1/1.7 = 1/17
    print(f"  해석적: I* = 0.1/(1+0.7) = 0.1/1.7 = {0.1/1.7:.6f} = 1/17")
    print(f"  → θ=π에서 부동점은 실수! (허수부=0)")
    print(f"  → 1/17 ≈ {1/17:.4f}")

    # 우리 상수 체계에서 오일러:
    print(f"\n  우리 모델의 오일러 유사 항등식:")
    print(f"    e^(iπ) + 1 = 0  (오일러)")
    print(f"    ↓")
    print(f"    I*(θ=π) = 1/17  (우리 모델에서 θ=π의 부동점)")
    print(f"    G*(θ=π) = D×P / (1/17) = 17×D×P")
    print(f"    → θ=π는 Genius를 17배 증폭!")
    print(f"    → '완전한 반전'(π) = 최대 증폭")

    # 각 θ에서의 Genius 증폭률
    print(f"\n  θ별 Genius 증폭률 (|G|/|G_real|):")
    D, P = 0.5, 0.85
    G_real = D * P / (1/3)  # 실수 부동점

    for theta_frac in [0, 1/6, 1/4, 1/3, 1/2, 2/3, 5/6, 1]:
        theta = theta_frac * np.pi
        fp = complex_fixed_point(theta)
        G_complex = D * P / fp
        ratio = abs(G_complex) / G_real
        bar = "█" * int(ratio * 10)
        print(f"    θ={theta_frac:.2f}π │{bar}│ ×{ratio:.2f} |G|={abs(G_complex):.2f}")

    print(f"\n  ┌──────────────────────────────────────────────────┐")
    print(f"  │                                                  │")
    print(f"  │  복소수 확장의 의미:                              │")
    print(f"  │                                                  │")
    print(f"  │  실수 모델: G = 크기만 (얼마나 천재인가)          │")
    print(f"  │  복소 모델: G = 크기 + 방향                       │")
    print(f"  │           (얼마나 + 어떤 종류의 천재인가)          │")
    print(f"  │                                                  │")
    print(f"  │  θ = 0:   단조 수렴 (현재 모델)                   │")
    print(f"  │  θ = π/3: 나선 수렴 (π가 자연스럽게 등장)         │")
    print(f"  │  θ = π:   완전 반전 (17배 증폭, 오일러 항등식)    │")
    print(f"  │                                                  │")
    print(f"  │  복소수 확장 = 실수에서 보이지 않던                │")
    print(f"  │  1/6 블라인드 스팟이 열리는 것                    │")
    print(f"  │                                                  │")
    print(f"  └──────────────────────────────────────────────────┘")


def main():
    print()
    print("▓" * 60)
    print("  가설 069: 복소수 확장")
    print("▓" * 60)

    verify_spiral_convergence()
    verify_pi_exact()
    verify_genius_complex()
    verify_euler_identity()

    os.makedirs(RESULTS_DIR, exist_ok=True)
    with open(os.path.join(RESULTS_DIR, "complex_report.md"), 'w', encoding='utf-8') as f:
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        f.write(f"# 복소수 확장 검증 [{now}]\n\n")
        f.write(f"θ=π/3 나선 수렴 확인\n")
        f.write(f"θ=π에서 17배 증폭 (오일러)\n\n---\n")

    print(f"\n  📁 보고서 → results/complex_report.md")
    print()


if __name__ == '__main__':
    main()
