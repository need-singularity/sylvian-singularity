#!/usr/bin/env python3
"""이력현상 검증기 — I가 커스프 제어변수임을 증명

란다우 자유에너지 F(G, I) = G⁴/4 - f(I)·G²/2 + (D×P)·G
dG/dt = -dF/dG = -G³ + f(I)·G - D×P

I를 왕복시켜 G 궤적이 달라지면 이력현상 확인 → 🟩 승격

사용법:
  python3 hysteresis_verifier.py                    # 기본 실행
  python3 hysteresis_verifier.py --dp 0.3           # D×P 지정
  python3 hysteresis_verifier.py --sweep 0.1 0.9    # I 범위
  python3 hysteresis_verifier.py --ic 0.5           # I_c 지정
  python3 hysteresis_verifier.py --scan-ic          # I_c 최적값 탐색
"""

import math
import argparse


def landau_force(G, a, b):
    """dG/dt = -dF/dG = -G³ + a·G - b"""
    return -G**3 + a * G - b


def f_of_I(I, I_c, c=3.0):
    """I → 란다우 제어변수 a 매핑
    f(I) = c·(I_c - I)
    I < I_c → a > 0 (이중 우물, 이력 가능)
    I > I_c → a < 0 (단일 우물, 이력 없음)
    """
    return c * (I_c - I)


def simulate_sweep(I_start, I_end, dp, I_c, c=3.0, n_steps=200, dt=0.01, relax=50):
    """I를 I_start → I_end로 스윕하며 G 궤적 추적

    relax가 작으면 이력 발생 (평형 미도달)
    relax가 크면 이력 소멸 (항상 평형)
    """
    I_values = []
    G_values = []

    # 초기 G: 자유에너지 최소에서 시작
    a_init = f_of_I(I_start, I_c, c)
    if a_init > 0:
        # 순방향: 왼쪽 우물, 역방향: 오른쪽 우물
        if I_end > I_start:
            G = -math.sqrt(a_init) - 0.1  # 왼쪽 우물 깊이
        else:
            G = math.sqrt(a_init) + 0.1   # 오른쪽 우물 깊이
    else:
        G = 0.0

    dI = (I_end - I_start) / n_steps

    for step in range(n_steps + 1):
        I = I_start + dI * step
        a = f_of_I(I, I_c, c)

        # 제한된 이완: 평형에 완전히 도달하지 못하게
        for _ in range(relax):
            force = landau_force(G, a, dp)
            G = G + dt * force
            G = max(-10, min(10, G))

        I_values.append(I)
        G_values.append(G)

    return I_values, G_values


def measure_hysteresis(forward_I, forward_G, backward_I, backward_G, threshold=0.3):
    """이력 폭 측정: 같은 I에서 forward vs backward G 차이"""
    hysteresis_points = []

    for i, I_f in enumerate(forward_I):
        # backward에서 가장 가까운 I 찾기
        best_j = min(range(len(backward_I)),
                     key=lambda j: abs(backward_I[j] - I_f))
        if abs(backward_I[best_j] - I_f) < 0.02:
            diff = abs(forward_G[i] - backward_G[best_j])
            if diff > threshold:
                hysteresis_points.append({
                    'I': I_f,
                    'G_forward': forward_G[i],
                    'G_backward': backward_G[best_j],
                    'diff': diff,
                })

    return hysteresis_points


def run_verification(dp=0.3, I_c=0.5, c=3.0, I_min=0.05, I_max=0.95):
    """전체 이력현상 검증"""
    print(f"\n{'═'*65}")
    print(f"  이력현상 검증기")
    print(f"{'═'*65}")
    print(f"\n  파라미터:")
    print(f"    D×P = {dp}")
    print(f"    I_c = {I_c} (임계 I)")
    print(f"    c   = {c} (매핑 강도)")
    print(f"    I 범위: [{I_min}, {I_max}]")

    print(f"\n  자유에너지: F(G,I) = G⁴/4 - f(I)·G²/2 + (D×P)·G")
    print(f"  f(I) = {c}·({I_c} - I)")

    # 이력 이론 조건
    # 4·a³ = 27·b² → a = (27·dp²/4)^(1/3)
    a_crit = (27 * dp**2 / 4) ** (1/3)
    # f(I) = a_crit → c·(I_c - I) = a_crit → I = I_c - a_crit/c
    I_hyst_start = I_c - a_crit / c
    print(f"\n  이론적 이력 시작 I = {I_hyst_start:.4f}")
    print(f"  (4·f(I)³ = 27·(D×P)² 에서)")

    # Forward sweep: I_min → I_max
    print(f"\n{'─'*65}")
    print(f"  순방향: I = {I_min} → {I_max}")
    fwd_I, fwd_G = simulate_sweep(I_min, I_max, dp, I_c, c)

    # Backward sweep: I_max → I_min
    print(f"  역방향: I = {I_max} → {I_min}")
    bwd_I, bwd_G = simulate_sweep(I_max, I_min, dp, I_c, c)

    # 이력 측정
    hyst = measure_hysteresis(fwd_I, fwd_G, bwd_I, bwd_G)

    print(f"\n{'─'*65}")
    print(f"  결과")
    print(f"{'─'*65}")

    if hyst:
        I_min_h = min(h['I'] for h in hyst)
        I_max_h = max(h['I'] for h in hyst)
        max_diff = max(h['diff'] for h in hyst)
        width = I_max_h - I_min_h

        print(f"\n  ✅ 이력현상 발견!")
        print(f"  이력 구간: I ∈ [{I_min_h:.3f}, {I_max_h:.3f}]")
        print(f"  이력 폭:   {width:.3f}")
        print(f"  최대 차이: {max_diff:.3f}")

        # 골든존과 비교
        gz_lower = 0.5 - math.log(4/3)  # 0.2123
        gz_upper = 0.5
        overlap_lower = max(I_min_h, gz_lower)
        overlap_upper = min(I_max_h, gz_upper)
        if overlap_lower < overlap_upper:
            overlap = overlap_upper - overlap_lower
            print(f"\n  골든존 [{gz_lower:.3f}, {gz_upper:.3f}]과 겹침:")
            print(f"  겹침 구간: [{overlap_lower:.3f}, {overlap_upper:.3f}]")
            print(f"  겹침 폭:   {overlap:.3f}")
            print(f"  겹침 비율: {overlap / (gz_upper - gz_lower) * 100:.1f}%")
        else:
            print(f"\n  ⚠️ 골든존과 겹치지 않음")

        # 샘플 출력
        print(f"\n  이력 구간 샘플:")
        print(f"  I      │ G(순방향) │ G(역방향) │ 차이")
        print(f"  ───────┼──────────┼──────────┼──────")
        step = max(1, len(hyst) // 8)
        for h in hyst[::step]:
            print(f"  {h['I']:6.3f} │ {h['G_forward']:8.3f}  │ {h['G_backward']:8.3f}  │ {h['diff']:.3f}")
    else:
        print(f"\n  ❌ 이력현상 없음")
        print(f"  파라미터를 조정해보세요 (--ic, --dp, --sweep)")

    # ASCII 그래프
    gz_lower = 0.5 - math.log(4/3)
    gz_upper = 0.5

    print(f"\n{'─'*65}")
    print(f"  G(I) 궤적 그래프")
    print(f"{'─'*65}")

    all_G = fwd_G + bwd_G
    G_min_val = min(all_G)
    G_max_val = max(all_G)
    G_range = G_max_val - G_min_val if G_max_val > G_min_val else 1

    rows = 20
    cols = 50
    grid = [[' ' for _ in range(cols)] for _ in range(rows)]

    def plot_point(I_val, G_val, char):
        col = int((I_val - I_min) / max(I_max - I_min, 0.01) * (cols - 1))
        row = int((1 - (G_val - G_min_val) / max(G_range, 0.01)) * (rows - 1))
        col = max(0, min(cols - 1, col))
        row = max(0, min(rows - 1, row))
        grid[row][col] = char

    for i in range(len(fwd_I)):
        plot_point(fwd_I[i], fwd_G[i], '→')
    for i in range(len(bwd_I)):
        plot_point(bwd_I[i], bwd_G[i], '←')

    gz_col_l = int((gz_lower - I_min) / max(I_max - I_min, 0.01) * (cols - 1))
    gz_col_u = int((gz_upper - I_min) / max(I_max - I_min, 0.01) * (cols - 1))
    for r in range(rows):
        if 0 <= gz_col_l < cols and grid[r][gz_col_l] == ' ':
            grid[r][gz_col_l] = '░'
        if 0 <= gz_col_u < cols and grid[r][gz_col_u] == ' ':
            grid[r][gz_col_u] = '░'

    print(f"\n  G")
    for r in range(rows):
        g_val = G_max_val - (G_range * r / max(rows - 1, 1))
        print(f"  {g_val:6.2f}│{''.join(grid[r])}")
    print(f"  {'':6}└{'─'*cols}")
    print(f"  {'':7}{I_min:<10}{' '*(cols-25)}{I_max:>10}")
    print(f"  {'':20}I (억제)")
    print(f"\n  → = 순방향 (I↑)   ← = 역방향 (I↓)   ░ = 골든존 경계")

    # 판정
    print(f"\n{'═'*65}")
    print(f"  최종 판정")
    print(f"{'═'*65}")
    if hyst:
        overlap_exists = overlap_lower < overlap_upper if hyst else False
        if overlap_exists:
            print(f"\n  ✅ 이력현상 존재 + 골든존 겹침 = 🟩 승격 가능!")
            print(f"  I는 커스프 제어변수이며, 이력 구간이 골든존과 일치")
        else:
            print(f"\n  ✅ 이력현상 존재, 하지만 골든존과 겹치지 않음")
            print(f"  I_c 조정 필요 (--scan-ic로 최적값 탐색)")
    else:
        print(f"\n  ❌ 이력현상 미확인, 🟨 유지")

    return bool(hyst)


def scan_ic(dp=0.3, c=3.0):
    """I_c 최적값 탐색: 이력 구간이 골든존과 최대 겹치는 I_c"""
    print(f"\n{'═'*65}")
    print(f"  I_c 최적값 탐색")
    print(f"{'═'*65}")

    gz_lower = 0.5 - math.log(4/3)
    gz_upper = 0.5
    gz_center = (gz_lower + gz_upper) / 2

    print(f"\n  골든존: [{gz_lower:.4f}, {gz_upper:.4f}], 중심: {gz_center:.4f}")
    print(f"\n  I_c    │ 이력 폭 │ 골든존 겹침 │ 판정")
    print(f"  ───────┼────────┼───────────┼──────")

    best_ic = None
    best_overlap = 0

    for ic_100 in range(20, 80, 5):
        I_c = ic_100 / 100

        fwd_I, fwd_G = simulate_sweep(0.05, 0.95, dp, I_c, c, n_steps=100, relax=300)
        bwd_I, bwd_G = simulate_sweep(0.95, 0.05, dp, I_c, c, n_steps=100, relax=300)
        hyst = measure_hysteresis(fwd_I, fwd_G, bwd_I, bwd_G)

        if hyst:
            I_min_h = min(h['I'] for h in hyst)
            I_max_h = max(h['I'] for h in hyst)
            width = I_max_h - I_min_h

            overlap_lower = max(I_min_h, gz_lower)
            overlap_upper = min(I_max_h, gz_upper)
            overlap = max(0, overlap_upper - overlap_lower)
            overlap_pct = overlap / (gz_upper - gz_lower) * 100

            marker = ' ★' if overlap_pct > best_overlap else ''
            print(f"  {I_c:.2f}   │ {width:6.3f}  │ {overlap_pct:8.1f}%   │ {'✅' if overlap > 0 else '❌'}{marker}")

            if overlap_pct > best_overlap:
                best_overlap = overlap_pct
                best_ic = I_c
        else:
            print(f"  {I_c:.2f}   │   ---   │    ---     │ 이력없음")

    if best_ic:
        print(f"\n  최적 I_c = {best_ic:.2f} (골든존 겹침 {best_overlap:.1f}%)")
        print(f"\n  상세 결과:")
        run_verification(dp=dp, I_c=best_ic, c=c)
    else:
        print(f"\n  ⚠️ 이력 구간을 찾지 못함. c 값 조정 필요")


def main():
    parser = argparse.ArgumentParser(description="이력현상 검증기")
    parser.add_argument('--dp', type=float, default=0.3, help='D×P 값 (기본: 0.3)')
    parser.add_argument('--ic', type=float, default=0.5, help='I_c 임계값 (기본: 0.5)')
    parser.add_argument('--c', type=float, default=3.0, help='매핑 강도 (기본: 3.0)')
    parser.add_argument('--sweep', nargs=2, type=float, default=[0.05, 0.95],
                        help='I 스윕 범위 (기본: 0.05 0.95)')
    parser.add_argument('--scan-ic', action='store_true', help='I_c 최적값 탐색')
    args = parser.parse_args()

    if args.scan_ic:
        scan_ic(dp=args.dp, c=args.c)
    else:
        run_verification(dp=args.dp, I_c=args.ic, c=args.c,
                        I_min=args.sweep[0], I_max=args.sweep[1])


if __name__ == '__main__':
    main()
