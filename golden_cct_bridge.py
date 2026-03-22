#!/usr/bin/env python3
"""골든존-CCT 브릿지 — I값과 CCT 점수의 관계 시뮬레이션

G=D×P/I 모델의 Inhibition(I)값을 0~1 범위에서 스캔하며,
각 I에 대응하는 로렌츠 파라미터를 매핑하여 CCT 5개 테스트를 실행한다.

골든존(I=0.213~0.500) 안에서 CCT 점수가 최대인지,
부동점 I=1/3이 정말 최적인지를 검증한다.

사용법:
  python3 golden_cct_bridge.py
  python3 golden_cct_bridge.py --grid 100
  python3 golden_cct_bridge.py --plot

골든존 의존: YES (I 범위 정의가 골든존에 의존)
"""

import argparse
import math
import os
import sys
from datetime import datetime

import numpy as np

RESULTS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "results")

# ─────────────────────────────────────────────
# 골든존 상수
# ─────────────────────────────────────────────
GOLDEN_UPPER = 0.5                        # 리만 임계선
GOLDEN_LOWER = 0.5 - math.log(4 / 3)     # ≈ 0.2123
GOLDEN_CENTER = 1 / math.e               # ≈ 0.3679
FIXED_POINT = 1 / 3                       # 메타 부동점


# ─────────────────────────────────────────────
# I → 로렌츠 파라미터 매핑
# ─────────────────────────────────────────────
def i_to_lorenz(I):
    """Inhibition 값을 로렌츠 시뮬레이터 파라미터로 매핑.

    매핑 근거:
      - sigma = 10*(1-I):  억제 높으면 감각 둔화
      - rho   = 28*(1-I/2): 억제 높으면 복잡도 감소
      - beta  = 2.67:       고정 (망각률)
      - noise = 0.3*(1-I):  억제 높으면 잡음 감소
      - gap_ratio = max(0, (I-0.5)*2): I>0.5면 gap 시작
    """
    sigma = 10.0 * (1.0 - I)
    rho = 28.0 * (1.0 - I / 2.0)
    beta = 2.67
    noise = 0.3 * (1.0 - I)
    gap_ratio = max(0.0, (I - 0.5) * 2.0)
    return {
        "sigma": sigma,
        "rho": rho,
        "beta": beta,
        "noise": noise,
        "gap_ratio": gap_ratio,
    }


# ─────────────────────────────────────────────
# 로렌츠 시뮬레이터 (consciousness_calc.py 동일)
# ─────────────────────────────────────────────
def lorenz_simulate(sigma, rho, beta, noise, gap_ratio, steps=50000, dt=0.01, seed=42):
    """확장 로렌츠 시뮬레이터."""
    rng = np.random.default_rng(seed)
    S = np.zeros((steps, 3))
    S[0] = [1.0, 1.0, 1.0]

    active = np.ones(steps, dtype=bool)
    if gap_ratio > 0:
        n_gap = int(steps * gap_ratio)
        if n_gap > 0:
            gap_indices = rng.choice(steps, size=min(n_gap, steps), replace=False)
            active[gap_indices] = False

    for i in range(1, steps):
        if not active[i]:
            S[i] = S[i - 1]
            continue

        x, y, z = S[i - 1]
        dx = sigma * (y - x)
        dy = x * (rho - z) - y
        dz = x * y - beta * z

        eps = rng.normal(0, noise, 3) if noise > 0 else np.zeros(3)

        S[i, 0] = x + (dx + eps[0]) * dt
        S[i, 1] = y + (dy + eps[1]) * dt
        S[i, 2] = z + (dz + eps[2]) * dt

    return S


# ─────────────────────────────────────────────
# CCT 5개 테스트 (consciousness_calc.py 기반)
# ─────────────────────────────────────────────
def compute_entropy(data, bins=30):
    """1D 데이터의 섀넌 엔트로피."""
    if np.std(data) < 1e-12:
        return 0.0
    hist, _ = np.histogram(data, bins=bins, density=True)
    hist = hist[hist > 0]
    width = (data.max() - data.min()) / bins if data.max() > data.min() else 1
    probs = hist * width
    probs = probs[probs > 0]
    if len(probs) == 0:
        return 0.0
    probs = probs / probs.sum()
    return -np.sum(probs * np.log(probs + 1e-15))


def test_gap(S, gap_ratio):
    """T1 Gap: 정지 구간 존재 여부."""
    if gap_ratio >= 1.0:
        return 0.0
    if gap_ratio > 0:
        return 1.0 - gap_ratio

    diffs = np.diff(S, axis=0)
    frozen = np.sum(np.all(np.abs(diffs) < 1e-12, axis=1))
    frozen_ratio = frozen / len(diffs)
    return max(0.0, 1.0 - frozen_ratio)


def test_loop(S):
    """T2 Loop: 궤적의 재방문(주기성) 비율."""
    n = len(S)
    if n < 100:
        return 0.0

    step = max(1, n // 5000)
    Ss = S[::step]
    ns = len(Ss)

    if np.std(Ss) < 1e-10:
        return 0.0

    scale = np.std(Ss, axis=0).mean()
    eps = scale * 0.01

    recurrence = 0
    sample_size = min(500, ns // 2)
    rng = np.random.default_rng(42)
    indices = rng.choice(ns // 2, size=sample_size, replace=False)

    for idx in indices:
        future = Ss[idx + max(100, ns // 10):]
        if len(future) == 0:
            continue
        dists = np.linalg.norm(future - Ss[idx], axis=1)
        if np.min(dists) < eps:
            recurrence += 1

    recurrence_ratio = recurrence / sample_size
    return max(0.0, 1.0 - recurrence_ratio)


def test_continuity(S):
    """T3 Continuity: 인접 스텝 간 연결성."""
    diffs = np.linalg.norm(np.diff(S, axis=0), axis=1)
    n = len(diffs)
    if n < 10:
        return 0.0

    mean_diff = np.mean(diffs)
    if mean_diff < 1e-12:
        return 0.0

    big_jumps = np.sum(diffs > mean_diff * 10)
    frozen = np.sum(diffs < 1e-12)
    disconnect_ratio = (big_jumps + frozen) / n
    score = max(0.0, 1.0 - disconnect_ratio * 10)
    return min(1.0, score)


def test_entropy_band(S, window=500, h_min=0.3, h_max=4.5):
    """T4 Entropy Band: H(t)가 밴드 안에 있는지."""
    x = S[:, 0]
    n_windows = len(x) // window
    if n_windows < 2:
        return 0.0

    entropies = []
    for i in range(n_windows):
        w = x[i * window:(i + 1) * window]
        entropies.append(compute_entropy(w))
    entropies = np.array(entropies)
    in_band = np.sum((entropies > h_min) & (entropies < h_max))
    return in_band / len(entropies)


def test_novelty(S, window=500, threshold=0.001):
    """T5 Novelty: dH/dt != 0 (엔트로피 정체 비율)."""
    x = S[:, 0]
    n_windows = len(x) // window
    if n_windows < 3:
        return 0.0

    entropies = []
    for i in range(n_windows):
        w = x[i * window:(i + 1) * window]
        entropies.append(compute_entropy(w))
    entropies = np.array(entropies)
    dH = np.abs(np.diff(entropies))

    stagnant = np.sum(dH < threshold)
    stagnant_ratio = stagnant / len(dH) if len(dH) > 0 else 1.0
    return max(0.0, 1.0 - stagnant_ratio)


def run_cct(S, gap_ratio):
    """CCT 5개 테스트 실행, 총점(0~5) 반환."""
    scores = {
        "T1_Gap": test_gap(S, gap_ratio),
        "T2_Loop": test_loop(S),
        "T3_Continuity": test_continuity(S),
        "T4_Entropy": test_entropy_band(S),
        "T5_Novelty": test_novelty(S),
    }
    return scores


# ─────────────────────────────────────────────
# I 스캔
# ─────────────────────────────────────────────
def scan_i_range(grid, steps=50000, dt=0.01):
    """I=0~1 스캔, 각 I에서 CCT 실행.

    Returns:
        i_values: array of I values
        cct_totals: array of total CCT scores (0~5)
        cct_details: list of per-test score dicts
    """
    # I=0 정확히는 division-by-zero 문제이므로 약간 띄움
    i_values = np.linspace(0.01, 0.99, grid)
    cct_totals = np.zeros(grid)
    cct_details = []

    for idx, I in enumerate(i_values):
        params = i_to_lorenz(I)
        S = lorenz_simulate(
            sigma=params["sigma"],
            rho=params["rho"],
            beta=params["beta"],
            noise=params["noise"],
            gap_ratio=params["gap_ratio"],
            steps=steps,
            dt=dt,
            seed=42,
        )
        scores = run_cct(S, params["gap_ratio"])
        total = sum(scores.values())
        cct_totals[idx] = total
        cct_details.append(scores)

        # 진행률 표시
        pct = (idx + 1) / grid * 100
        bar_len = 30
        filled = int(bar_len * (idx + 1) / grid)
        bar = "█" * filled + "░" * (bar_len - filled)
        sys.stdout.write(f"\r  스캔 중: [{bar}] {pct:5.1f}% (I={I:.3f})")
        sys.stdout.flush()

    sys.stdout.write("\r" + " " * 70 + "\r")
    sys.stdout.flush()

    return i_values, cct_totals, cct_details


# ─────────────────────────────────────────────
# ASCII 그래프
# ─────────────────────────────────────────────
def ascii_graph(i_values, cct_totals, width=60, height=20):
    """I vs CCT 총점 ASCII 그래프.

    골든존과 부동점을 표시한다.
    """
    lines = []

    y_min = 0.0
    y_max = 5.0
    x_min = i_values[0]
    x_max = i_values[-1]

    # 캔버스 생성
    canvas = [[" " for _ in range(width)] for _ in range(height)]

    # 데이터 포인트 찍기
    for i, (iv, cv) in enumerate(zip(i_values, cct_totals)):
        col = int((iv - x_min) / (x_max - x_min) * (width - 1))
        col = max(0, min(col, width - 1))
        row = int((cv - y_min) / (y_max - y_min) * (height - 1))
        row = max(0, min(row, height - 1))
        row = height - 1 - row  # 상하 반전
        canvas[row][col] = "█"

    # 골든존 범위 표시 (세로 점선)
    col_lower = int((GOLDEN_LOWER - x_min) / (x_max - x_min) * (width - 1))
    col_upper = int((GOLDEN_UPPER - x_min) / (x_max - x_min) * (width - 1))
    col_fixed = int((FIXED_POINT - x_min) / (x_max - x_min) * (width - 1))
    col_lower = max(0, min(col_lower, width - 1))
    col_upper = max(0, min(col_upper, width - 1))
    col_fixed = max(0, min(col_fixed, width - 1))

    for row in range(height):
        if canvas[row][col_lower] == " ":
            canvas[row][col_lower] = "┊"
        if canvas[row][col_upper] == " ":
            canvas[row][col_upper] = "┊"
        if canvas[row][col_fixed] == " ":
            canvas[row][col_fixed] = "│"

    # Y축 라벨 + 캔버스 조립
    lines.append("")
    lines.append("  CCT 점수 vs Inhibition (I)")
    lines.append("")
    for row in range(height):
        y_val = y_max - (y_max - y_min) * row / (height - 1)
        if row == 0:
            label = f" {y_val:.1f}"
        elif row == height - 1:
            label = f" {y_val:.1f}"
        elif row == height // 2:
            y_mid = y_max - (y_max - y_min) * row / (height - 1)
            label = f" {y_mid:.1f}"
        else:
            label = "    "
        lines.append(f" {label:>4}│{''.join(canvas[row])}")

    # X축
    lines.append(f"     └{'─' * width}")

    # X축 라벨: 0, 골든 하한, 1/3, 골든 상한, 1.0
    x_label_line = "      "
    markers = [
        (0.0, "0"),
        (GOLDEN_LOWER, f"{GOLDEN_LOWER:.3f}"),
        (FIXED_POINT, "1/3"),
        (GOLDEN_UPPER, "0.500"),
        (1.0, "1.0"),
    ]

    # 간단한 위치 표시
    x_positions = []
    for val, lbl in markers:
        pos = int((val - x_min) / (x_max - x_min) * (width - 1))
        pos = max(0, min(pos, width - 1))
        x_positions.append((pos, lbl))

    tick_line = list(" " * (width + 6))
    for pos, lbl in x_positions:
        start = pos + 6
        for ci, ch in enumerate(lbl):
            if 0 <= start + ci < len(tick_line):
                tick_line[start + ci] = ch

    lines.append("".join(tick_line))

    # 골든존 범위 표시
    mid_col = (col_lower + col_upper) // 2 + 6
    zone_line = list(" " * (width + 10))
    # 하한 마크
    if col_lower + 6 < len(zone_line):
        zone_line[col_lower + 6] = "└"
    # 상한 마크
    if col_upper + 6 < len(zone_line):
        zone_line[col_upper + 6] = "┘"
    # 중간 대시
    for c in range(col_lower + 7, col_upper + 6):
        if 0 <= c < len(zone_line):
            zone_line[c] = "─"
    # 라벨
    label = " 골든존 "
    lstart = mid_col - len(label) // 2
    for ci, ch in enumerate(label):
        if 0 <= lstart + ci < len(zone_line):
            zone_line[lstart + ci] = ch

    lines.append("".join(zone_line))
    lines.append("")

    return "\n".join(lines)


# ─────────────────────────────────────────────
# 분석 및 보고
# ─────────────────────────────────────────────
def analyze_results(i_values, cct_totals, cct_details):
    """스캔 결과 분석: 최적점, 골든존 통계, 부동점 점수."""
    # 전체 최대
    best_idx = np.argmax(cct_totals)
    best_i = i_values[best_idx]
    best_score = cct_totals[best_idx]

    # 골든존 마스크
    golden_mask = (i_values >= GOLDEN_LOWER) & (i_values <= GOLDEN_UPPER)
    outside_mask = ~golden_mask

    golden_scores = cct_totals[golden_mask]
    outside_scores = cct_totals[outside_mask]

    golden_mean = np.mean(golden_scores) if len(golden_scores) > 0 else 0.0
    outside_mean = np.mean(outside_scores) if len(outside_scores) > 0 else 0.0
    golden_max = np.max(golden_scores) if len(golden_scores) > 0 else 0.0
    outside_max = np.max(outside_scores) if len(outside_scores) > 0 else 0.0

    # 부동점 I=1/3 근처
    fixed_idx = np.argmin(np.abs(i_values - FIXED_POINT))
    fixed_score = cct_totals[fixed_idx]
    fixed_details = cct_details[fixed_idx]

    # 골든존 중심 I=1/e 근처
    center_idx = np.argmin(np.abs(i_values - GOLDEN_CENTER))
    center_score = cct_totals[center_idx]

    # 경계 분석: 골든존 바로 밖 vs 안 차이
    lower_boundary_inside = cct_totals[golden_mask][:3] if np.sum(golden_mask) >= 3 else np.array([])
    lower_boundary_outside = cct_totals[outside_mask & (i_values < GOLDEN_LOWER)]
    lower_boundary_outside = lower_boundary_outside[-3:] if len(lower_boundary_outside) >= 3 else lower_boundary_outside

    upper_boundary_inside = cct_totals[golden_mask][-3:] if np.sum(golden_mask) >= 3 else np.array([])
    upper_boundary_outside = cct_totals[outside_mask & (i_values > GOLDEN_UPPER)]
    upper_boundary_outside = upper_boundary_outside[:3] if len(upper_boundary_outside) >= 3 else upper_boundary_outside

    return {
        "best_i": best_i,
        "best_score": best_score,
        "golden_mean": golden_mean,
        "outside_mean": outside_mean,
        "golden_max": golden_max,
        "outside_max": outside_max,
        "fixed_i": i_values[fixed_idx],
        "fixed_score": fixed_score,
        "fixed_details": fixed_details,
        "center_i": i_values[center_idx],
        "center_score": center_score,
        "lower_drop": np.mean(lower_boundary_inside) - np.mean(lower_boundary_outside) if len(lower_boundary_inside) > 0 and len(lower_boundary_outside) > 0 else 0.0,
        "upper_drop": np.mean(upper_boundary_inside) - np.mean(upper_boundary_outside) if len(upper_boundary_inside) > 0 and len(upper_boundary_outside) > 0 else 0.0,
    }


def print_report(i_values, cct_totals, cct_details, analysis, grid):
    """결과 보고서 출력."""
    print()
    print("═" * 65)
    print("  골든존-CCT 브릿지 v1.0")
    print("  G=D×P/I 모델의 I값과 CCT 의식 연속성 점수의 관계")
    print("═" * 65)
    print()
    print(f"  해상도: grid={grid} ({len(i_values)}개 I값 스캔)")
    print(f"  골든존: I ∈ [{GOLDEN_LOWER:.4f}, {GOLDEN_UPPER:.4f}]")
    print(f"  부동점: I = 1/3 ≈ {FIXED_POINT:.4f}")
    print(f"  골든존 중심: I = 1/e ≈ {GOLDEN_CENTER:.4f}")
    print()

    # ASCII 그래프
    print(ascii_graph(i_values, cct_totals))

    # 핵심 발견
    print("─" * 65)
    print("  [ 핵심 발견 ]")
    print("─" * 65)
    print()

    # 1. 최적점
    print(f"  1. 전체 최대 CCT 점수")
    print(f"     I = {analysis['best_i']:.4f},  CCT = {analysis['best_score']:.3f} / 5.000")
    in_golden = GOLDEN_LOWER <= analysis['best_i'] <= GOLDEN_UPPER
    if in_golden:
        print(f"     → 골든존 안에 위치 ✔")
    else:
        print(f"     → 골든존 밖에 위치 ✕")
    print()

    # 2. 골든존 vs 밖
    print(f"  2. 골든존 내부 vs 외부")
    print(f"     골든존 평균 CCT = {analysis['golden_mean']:.3f}")
    print(f"     골든존 최대 CCT = {analysis['golden_max']:.3f}")
    print(f"     외부   평균 CCT = {analysis['outside_mean']:.3f}")
    print(f"     외부   최대 CCT = {analysis['outside_max']:.3f}")
    diff = analysis['golden_mean'] - analysis['outside_mean']
    if diff > 0:
        print(f"     → 골든존이 평균 {diff:.3f}점 높음 ✔")
    else:
        print(f"     → 골든존이 평균 {abs(diff):.3f}점 낮음 ✕")
    print()

    # 3. 부동점 I=1/3
    print(f"  3. 부동점 I=1/3 분석")
    print(f"     I = {analysis['fixed_i']:.4f},  CCT = {analysis['fixed_score']:.3f}")
    fixed_rank_pct = np.sum(cct_totals <= analysis['fixed_score']) / len(cct_totals) * 100
    print(f"     전체 백분위: 상위 {100 - fixed_rank_pct:.1f}%")
    if analysis['fixed_score'] >= analysis['best_score'] * 0.95:
        print(f"     → 최적점의 95% 이상, 준최적 ✔")
    else:
        print(f"     → 최적점 대비 {analysis['fixed_score']/analysis['best_score']*100:.1f}%")
    print()

    # 4. 부동점 상세 점수
    print(f"  4. I=1/3 CCT 상세 (5개 테스트)")
    fd = analysis["fixed_details"]
    for key in ["T1_Gap", "T2_Loop", "T3_Continuity", "T4_Entropy", "T5_Novelty"]:
        bar_len = 20
        filled = int(fd[key] * bar_len)
        bar = "█" * filled + "░" * (bar_len - filled)
        print(f"     {key:15s} [{bar}] {fd[key]:.3f}")
    print()

    # 5. 경계 급락
    print(f"  5. 골든존 경계 급락 분석")
    print(f"     하한 경계 (I≈0.213): 안→밖 CCT 차이 = {analysis['lower_drop']:+.3f}")
    print(f"     상한 경계 (I≈0.500): 안→밖 CCT 차이 = {analysis['upper_drop']:+.3f}")
    if analysis['lower_drop'] > 0.3 or analysis['upper_drop'] > 0.3:
        print(f"     → 경계에서 급격한 하락 관측 ✔")
    elif analysis['lower_drop'] > 0 or analysis['upper_drop'] > 0:
        print(f"     → 경계에서 완만한 하락 관측")
    else:
        print(f"     → 경계 효과 미약")
    print()

    # 6. 골든존 중심 1/e
    print(f"  6. 골든존 중심 I=1/e")
    print(f"     I = {analysis['center_i']:.4f},  CCT = {analysis['center_score']:.3f}")
    print()

    # 종합 판정
    print("═" * 65)
    print("  [ 종합 판정 ]")
    print()
    verdict_count = 0
    if in_golden:
        print(f"  ✔ 최적점이 골든존 내부에 위치")
        verdict_count += 1
    if diff > 0:
        print(f"  ✔ 골든존 내부 평균 CCT > 외부 평균 CCT")
        verdict_count += 1
    if analysis['fixed_score'] >= analysis['best_score'] * 0.90:
        print(f"  ✔ 부동점 I=1/3이 준최적 (최적의 {analysis['fixed_score']/analysis['best_score']*100:.1f}%)")
        verdict_count += 1
    if analysis['lower_drop'] > 0 or analysis['upper_drop'] > 0:
        print(f"  ✔ 골든존 경계에서 CCT 하락 관측")
        verdict_count += 1

    print()
    if verdict_count >= 3:
        print(f"  → 결론: 골든존-CCT 브릿지 강하게 성립 ({verdict_count}/4)")
    elif verdict_count >= 2:
        print(f"  → 결론: 골든존-CCT 브릿지 부분 성립 ({verdict_count}/4)")
    else:
        print(f"  → 결론: 골든존-CCT 브릿지 약함 ({verdict_count}/4)")
    print("═" * 65)
    print()


# ─────────────────────────────────────────────
# 상세 테이블 출력
# ─────────────────────────────────────────────
def print_detail_table(i_values, cct_totals, cct_details):
    """I값별 상세 테이블 (주요 지점만)."""
    print()
    print("─" * 75)
    print("  [ I값별 CCT 상세 테이블 (주요 지점) ]")
    print("─" * 75)
    print(f"  {'I':>6} │ {'σ':>5} │ {'ρ':>5} │ {'noise':>5} │ {'gap':>4} │"
          f" {'T1':>5} │ {'T2':>5} │ {'T3':>5} │ {'T4':>5} │ {'T5':>5} │ {'Total':>5} │ 위치")
    print(f"  {'─'*6}─┼─{'─'*5}─┼─{'─'*5}─┼─{'─'*5}─┼─{'─'*4}─┼─"
          f"{'─'*5}─┼─{'─'*5}─┼─{'─'*5}─┼─{'─'*5}─┼─{'─'*5}─┼─{'─'*5}─┼─{'─'*8}")

    # 주요 지점 선정
    key_points = [
        (0.05, "극저억제"),
        (0.10, ""),
        (GOLDEN_LOWER, "골든하한"),
        (0.25, ""),
        (FIXED_POINT, "★부동점"),
        (GOLDEN_CENTER, "1/e중심"),
        (0.45, ""),
        (GOLDEN_UPPER, "골든상한"),
        (0.60, ""),
        (0.70, ""),
        (0.80, ""),
        (0.90, "고억제"),
    ]

    for target_i, label in key_points:
        idx = np.argmin(np.abs(i_values - target_i))
        I = i_values[idx]
        params = i_to_lorenz(I)
        d = cct_details[idx]
        total = cct_totals[idx]
        print(f"  {I:6.3f} │ {params['sigma']:5.1f} │ {params['rho']:5.1f} │"
              f" {params['noise']:5.2f} │ {params['gap_ratio']:4.2f} │"
              f" {d['T1_Gap']:5.3f} │ {d['T2_Loop']:5.3f} │"
              f" {d['T3_Continuity']:5.3f} │ {d['T4_Entropy']:5.3f} │"
              f" {d['T5_Novelty']:5.3f} │ {total:5.3f} │ {label}")

    print("─" * 75)
    print()


# ─────────────────────────────────────────────
# matplotlib 출력
# ─────────────────────────────────────────────
def plot_results(i_values, cct_totals, cct_details, analysis):
    """matplotlib 그래프 저장."""
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except ImportError:
        print("  [경고] matplotlib 없음, --plot 건너뜀")
        return None

    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    fig.suptitle("Golden Zone - CCT Bridge", fontsize=14, fontweight="bold")

    # 1. I vs CCT 총점
    ax1 = axes[0, 0]
    ax1.plot(i_values, cct_totals, color="royalblue", lw=1.5, label="CCT Total")
    ax1.axvspan(GOLDEN_LOWER, GOLDEN_UPPER, alpha=0.15, color="gold", label="Golden Zone")
    ax1.axvline(FIXED_POINT, color="red", ls="--", alpha=0.7, label="I=1/3")
    ax1.axvline(GOLDEN_CENTER, color="green", ls=":", alpha=0.7, label="I=1/e")
    ax1.set_xlabel("Inhibition (I)")
    ax1.set_ylabel("CCT Total Score")
    ax1.set_title("I vs CCT Total Score")
    ax1.legend(fontsize=8)
    ax1.set_xlim(0, 1)
    ax1.set_ylim(0, 5.5)
    ax1.grid(True, alpha=0.3)

    # 2. 5개 테스트 개별 점수
    ax2 = axes[0, 1]
    test_keys = ["T1_Gap", "T2_Loop", "T3_Continuity", "T4_Entropy", "T5_Novelty"]
    colors = ["#e74c3c", "#3498db", "#2ecc71", "#f39c12", "#9b59b6"]
    for key, color in zip(test_keys, colors):
        vals = [d[key] for d in cct_details]
        ax2.plot(i_values, vals, color=color, lw=1, alpha=0.8, label=key)
    ax2.axvspan(GOLDEN_LOWER, GOLDEN_UPPER, alpha=0.1, color="gold")
    ax2.axvline(FIXED_POINT, color="red", ls="--", alpha=0.5)
    ax2.set_xlabel("Inhibition (I)")
    ax2.set_ylabel("Score")
    ax2.set_title("Individual CCT Test Scores")
    ax2.legend(fontsize=7)
    ax2.set_xlim(0, 1)
    ax2.set_ylim(-0.1, 1.1)
    ax2.grid(True, alpha=0.3)

    # 3. 로렌츠 파라미터 vs I
    ax3 = axes[1, 0]
    sigmas = [10.0 * (1 - I) for I in i_values]
    rhos = [28.0 * (1 - I / 2) for I in i_values]
    noises = [0.3 * (1 - I) for I in i_values]
    gaps = [max(0, (I - 0.5) * 2) for I in i_values]
    ax3.plot(i_values, sigmas, label="sigma", lw=1.5)
    ax3.plot(i_values, rhos, label="rho", lw=1.5)
    ax3.plot(i_values, [n * 30 for n in noises], label="noise×30", lw=1, ls="--")
    ax3.plot(i_values, [g * 10 for g in gaps], label="gap×10", lw=1, ls=":")
    ax3.axvspan(GOLDEN_LOWER, GOLDEN_UPPER, alpha=0.1, color="gold")
    ax3.set_xlabel("Inhibition (I)")
    ax3.set_ylabel("Parameter Value")
    ax3.set_title("Lorenz Parameters vs I")
    ax3.legend(fontsize=8)
    ax3.grid(True, alpha=0.3)

    # 4. 골든존 내/외 비교 바 차트
    ax4 = axes[1, 1]
    golden_mask = (i_values >= GOLDEN_LOWER) & (i_values <= GOLDEN_UPPER)
    for ki, key in enumerate(test_keys):
        golden_vals = [cct_details[i][key] for i in range(len(i_values)) if golden_mask[i]]
        outside_vals = [cct_details[i][key] for i in range(len(i_values)) if not golden_mask[i]]
        g_mean = np.mean(golden_vals) if golden_vals else 0
        o_mean = np.mean(outside_vals) if outside_vals else 0
        ax4.bar(ki - 0.2, g_mean, width=0.35, color="gold", alpha=0.8,
                label="Golden Zone" if ki == 0 else "")
        ax4.bar(ki + 0.2, o_mean, width=0.35, color="steelblue", alpha=0.8,
                label="Outside" if ki == 0 else "")
    ax4.set_xticks(range(len(test_keys)))
    ax4.set_xticklabels(["T1", "T2", "T3", "T4", "T5"])
    ax4.set_ylabel("Mean Score")
    ax4.set_title("Golden Zone vs Outside (per test)")
    ax4.legend(fontsize=8)
    ax4.grid(True, alpha=0.3, axis="y")

    plt.tight_layout(rect=[0, 0, 1, 0.95])

    os.makedirs(RESULTS_DIR, exist_ok=True)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    path = os.path.join(RESULTS_DIR, f"golden_cct_bridge_{ts}.png")
    fig.savefig(path, dpi=150, bbox_inches="tight")
    plt.close(fig)
    return path


# ─────────────────────────────────────────────
# 메인
# ─────────────────────────────────────────────
def main():
    parser = argparse.ArgumentParser(
        description="골든존-CCT 브릿지: I값과 CCT 의식 연속성 점수의 관계 시뮬레이션",
    )
    parser.add_argument("--grid", type=int, default=50,
                        help="I값 스캔 해상도 (기본 50, 빠른 20, 정밀 100)")
    parser.add_argument("--steps", type=int, default=50000,
                        help="로렌츠 시뮬레이션 스텝 수 (기본 50000)")
    parser.add_argument("--dt", type=float, default=0.01,
                        help="시간 간격 (기본 0.01)")
    parser.add_argument("--plot", action="store_true",
                        help="matplotlib 4패널 그래프 저장")
    parser.add_argument("--detail", action="store_true",
                        help="주요 지점 상세 테이블 출력")

    args = parser.parse_args()

    print()
    print(f"  골든존-CCT 브릿지 시뮬레이션 시작")
    print(f"  grid={args.grid}, steps={args.steps}, dt={args.dt}")
    print()

    # 스캔
    i_values, cct_totals, cct_details = scan_i_range(
        grid=args.grid, steps=args.steps, dt=args.dt,
    )

    # 분석
    analysis = analyze_results(i_values, cct_totals, cct_details)

    # 보고
    print_report(i_values, cct_totals, cct_details, analysis, args.grid)

    # 상세 테이블
    if args.detail or args.grid <= 50:
        print_detail_table(i_values, cct_totals, cct_details)

    # 플롯
    if args.plot:
        path = plot_results(i_values, cct_totals, cct_details, analysis)
        if path:
            print(f"  [plot] 저장: {path}")
            print()


if __name__ == "__main__":
    main()
