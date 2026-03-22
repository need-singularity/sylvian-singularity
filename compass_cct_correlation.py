#!/usr/bin/env python3
"""실험 16: Compass 점수와 CCT 점수의 상관관계 분석

같은 D, P, I 파라미터 격자에서 Compass 점수와 CCT 점수를 동시에 계산하여
두 측정 체계의 관계를 밝힌다.

사용법:
  python3 compass_cct_correlation.py
  python3 compass_cct_correlation.py --grid 5   # 빠른 버전
"""

import argparse
import math
import sys
import time

import numpy as np
from scipy import stats


# ─────────────────────────────────────────────
# 파라미터 격자 정의
# ─────────────────────────────────────────────

D_VALUES = [0.1, 0.3, 0.5, 0.7]
P_VALUES = [0.3, 0.5, 0.7, 0.9]
I_VALUES = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7]

GOLDEN_LOWER = 0.5 - math.log(4 / 3)   # ≈ 0.2123
GOLDEN_UPPER = 0.5


# ─────────────────────────────────────────────
# 모델 1: Genius Score (brain_singularity.py)
# ─────────────────────────────────────────────

def genius_score(d, p, i):
    """G = D * P / I"""
    return d * p / max(i, 1e-6)


# ─────────────────────────────────────────────
# Compass 점수 계산 (compass.py 간소화)
# ─────────────────────────────────────────────

def population_zscore(score, n=50000, seed=42):
    """모집단 대비 Z-score 계산."""
    rng = np.random.default_rng(seed)
    pop_d = rng.beta(2, 5, n).clip(0.01, 0.99)
    pop_p = rng.beta(5, 2, n).clip(0.01, 0.99)
    pop_i = rng.beta(5, 2, n).clip(0.05, 0.99)
    pop_scores = pop_d * pop_p / pop_i
    z = (score - pop_scores.mean()) / pop_scores.std()
    return z, pop_scores.mean(), pop_scores.std()


# 모집단 통계를 한 번만 계산 (캐시)
_POP_CACHE = {}


def _get_pop_stats(seed=42, n=50000):
    if seed not in _POP_CACHE:
        rng = np.random.default_rng(seed)
        pop_d = rng.beta(2, 5, n).clip(0.01, 0.99)
        pop_p = rng.beta(5, 2, n).clip(0.01, 0.99)
        pop_i = rng.beta(5, 2, n).clip(0.05, 0.99)
        pop_scores = pop_d * pop_p / pop_i
        _POP_CACHE[seed] = (pop_scores.mean(), pop_scores.std())
    return _POP_CACHE[seed]


def cusp_analysis(deficit, inhibition):
    """커스프 파국 분석: 임계점 거리와 방향."""
    a = 2 * deficit - 1
    b = 1 - 2 * inhibition

    bifurcation = 8 * a**3 + 27 * b**2
    max_possible = 8 * 1**3 + 27 * 1**2
    distance_to_critical = abs(bifurcation) / max_possible

    direction_sign = 1 if b > 0 else -1

    # 다중 안정점 검사
    x_range = np.linspace(-2, 2, 200)
    dV = 4 * x_range**3 + 2 * a * x_range + b
    sign_changes = np.where(np.diff(np.sign(dV)))[0]
    is_bistable = len(sign_changes) >= 2

    return {
        'distance_to_critical': distance_to_critical,
        'direction_sign': direction_sign,
        'is_bistable': is_bistable,
    }


def boltzmann_analysis(deficit, plasticity, inhibition):
    """볼츠만 분포 기반 전이 확률."""
    temperature = 1.0 / max(inhibition, 0.01)

    E_normal = 0.0
    E_genius = -(deficit * plasticity)
    E_decline = deficit * (1 - plasticity)

    energies = np.array([E_normal, E_genius, E_decline])
    exp_terms = np.exp(-energies / temperature)
    Z = exp_terms.sum()
    probs = exp_terms / Z

    return {
        'p_normal': probs[0],
        'p_genius': probs[1],
        'p_decline': probs[2],
    }


def compute_compass_score(d, p, i):
    """compass.py의 compass_direction 핵심 로직.

    compass_score = z/10 * 0.3 + (1 - cusp_dist) * 0.3 + p_genius * 0.4
    """
    score = genius_score(d, p, i)
    pop_mean, pop_std = _get_pop_stats()
    z = (score - pop_mean) / pop_std

    cusp = cusp_analysis(d, i)
    boltz = boltzmann_analysis(d, p, i)

    compass_score = (
        z / 10 * 0.3
        + (1 - cusp['distance_to_critical']) * 0.3
        + boltz['p_genius'] * 0.4
    )
    compass_score = max(0.0, min(1.0, compass_score))

    return compass_score, z, cusp, boltz


# ─────────────────────────────────────────────
# CCT 점수 계산 (consciousness_calc.py 간소화)
# ─────────────────────────────────────────────

def lorenz_simulate(sigma, rho, beta, noise, gap_ratio, steps, dt=0.01, seed=42):
    """확장 로렌츠 시뮬레이터."""
    rng = np.random.default_rng(seed)
    t = np.arange(steps) * dt
    S = np.zeros((steps, 3))
    S[0] = [1.0, 1.0, 1.0]

    active = np.ones(steps, dtype=bool)
    if gap_ratio > 0:
        n_gap = int(steps * gap_ratio)
        gap_indices = rng.choice(steps, size=n_gap, replace=False)
        active[gap_indices] = False

    for idx in range(1, steps):
        if not active[idx]:
            S[idx] = S[idx - 1]
            continue
        x, y, z_val = S[idx - 1]
        dx = sigma * (y - x)
        dy = x * (rho - z_val) - y
        dz = x * y - beta * z_val
        eps = rng.normal(0, noise, 3) if noise > 0 else np.zeros(3)
        S[idx, 0] = x + (dx + eps[0]) * dt
        S[idx, 1] = y + (dy + eps[1]) * dt
        S[idx, 2] = z_val + (dz + eps[2]) * dt

    return t, S


def compute_entropy(data, bins=30):
    """1D 섀넌 엔트로피."""
    if len(data) < 2:
        return 0.0
    hist, _ = np.histogram(data, bins=bins, density=True)
    hist = hist[hist > 0]
    d_range = data.max() - data.min()
    width = d_range / bins if d_range > 0 else 1
    probs = hist * width
    probs = probs[probs > 0]
    if len(probs) == 0:
        return 0.0
    probs = probs / probs.sum()
    return -np.sum(probs * np.log(probs + 1e-15))


def test_gap(S, gap_ratio):
    if gap_ratio >= 1.0:
        return 0.0, False
    if gap_ratio > 0:
        return 1.0 - gap_ratio, False
    diffs = np.diff(S, axis=0)
    frozen = np.sum(np.all(np.abs(diffs) < 1e-12, axis=1))
    frozen_ratio = frozen / len(diffs)
    if frozen_ratio > 0.01:
        return 1.0 - frozen_ratio, False
    return 1.0, True


def test_loop(S, threshold=0.5):
    n = len(S)
    if n < 100:
        return 0.0, False
    step = max(1, n // 5000)
    Ss = S[::step]
    ns = len(Ss)
    if np.std(Ss) < 1e-10:
        return 0.0, False
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
    passed = recurrence_ratio < threshold
    score = max(0, 1.0 - recurrence_ratio)
    return score, passed


def test_continuity(S, threshold=0.01):
    diffs = np.linalg.norm(np.diff(S, axis=0), axis=1)
    n = len(diffs)
    if n < 10:
        return 0.0, False
    mean_diff = np.mean(diffs)
    if mean_diff < 1e-12:
        return 0.0, False
    big_jumps = np.sum(diffs > mean_diff * 10)
    frozen = np.sum(diffs < 1e-12)
    disconnect_ratio = (big_jumps + frozen) / n
    passed = disconnect_ratio < threshold
    score = max(0, min(1.0, 1.0 - disconnect_ratio * 10))
    return score, passed


def test_entropy_band(S, window=500, h_min=0.3, h_max=4.5):
    x = S[:, 0]
    n_windows = len(x) // window
    if n_windows < 2:
        return 0.0, False
    entropies = []
    for w_i in range(n_windows):
        w = x[w_i * window:(w_i + 1) * window]
        if np.std(w) < 1e-12:
            entropies.append(0.0)
        else:
            entropies.append(compute_entropy(w))
    entropies = np.array(entropies)
    in_band = np.sum((entropies > h_min) & (entropies < h_max))
    ratio = in_band / len(entropies)
    return ratio, ratio > 0.95


def test_novelty(S, window=500, threshold=0.001):
    x = S[:, 0]
    n_windows = len(x) // window
    if n_windows < 3:
        return 0.0, False
    entropies = []
    for w_i in range(n_windows):
        w = x[w_i * window:(w_i + 1) * window]
        if np.std(w) < 1e-12:
            entropies.append(0.0)
        else:
            entropies.append(compute_entropy(w))
    entropies = np.array(entropies)
    dH = np.abs(np.diff(entropies))
    stagnant = np.sum(dH < threshold)
    stagnant_ratio = stagnant / len(dH) if len(dH) > 0 else 1.0
    passed = stagnant_ratio < 0.05
    score = max(0, 1.0 - stagnant_ratio)
    return score, passed


def run_cct(S, gap_ratio):
    """CCT 5개 테스트 → (총점 /5, pass 수)"""
    t1_score, t1_pass = test_gap(S, gap_ratio)
    t2_score, t2_pass = test_loop(S)
    t3_score, t3_pass = test_continuity(S)
    t4_score, t4_pass = test_entropy_band(S)
    t5_score, t5_pass = test_novelty(S)

    tests = [
        (t1_score, t1_pass),
        (t2_score, t2_pass),
        (t3_score, t3_pass),
        (t4_score, t4_pass),
        (t5_score, t5_pass),
    ]
    passes = sum(1 for _, p in tests if p)
    halfs = sum(0.5 for s, p in tests if not p and s > 0.7)
    total = passes + halfs
    avg_score = np.mean([s for s, _ in tests])
    return total, passes, avg_score


def dpi_to_lorenz(d, p, i):
    """D, P, I → 로렌츠 파라미터 매핑.

    매핑 전략:
      sigma (감각 민감도) = 5 + 15 * d        (결손 클수록 감각 민감)
      rho   (환경 복잡도) = 10 + 30 * p       (가소성 클수록 복잡한 환경 처리)
      beta  (망각률)      = 0.5 + 4.0 * i     (억제 클수록 망각 빠름)
      noise               = 0.05 + 0.2 * (1 - i)  (억제 낮을수록 잡음 큼)
      gap_ratio            = 0.0               (정지 구간 없음)
    """
    sigma = 5 + 15 * d
    rho = 10 + 30 * p
    beta = 0.5 + 4.0 * i
    noise = 0.05 + 0.2 * (1 - i)
    gap_ratio = 0.0
    return sigma, rho, beta, noise, gap_ratio


# ─────────────────────────────────────────────
# 가설 166 판정: 골든존 + Compass > 0
# ─────────────────────────────────────────────

def hypothesis_166(i_val, compass_score):
    """가설 166: I가 골든존 내 + Compass > 0 → 의식 있음."""
    in_golden = GOLDEN_LOWER <= i_val <= GOLDEN_UPPER
    compass_positive = compass_score > 0
    return in_golden and compass_positive


# ─────────────────────────────────────────────
# ASCII 산점도
# ─────────────────────────────────────────────

def ascii_scatter(xs, ys, xlabel, ylabel, width=60, height=20):
    """ASCII 산점도."""
    x_min, x_max = min(xs), max(xs)
    y_min, y_max = min(ys), max(ys)
    if x_max - x_min < 1e-12:
        x_max = x_min + 1
    if y_max - y_min < 1e-12:
        y_max = y_min + 1

    grid = [[' ' for _ in range(width)] for _ in range(height)]

    # 점 밀도 카운트
    density = {}
    for x, y in zip(xs, ys):
        col = int((x - x_min) / (x_max - x_min) * (width - 1))
        row = height - 1 - int((y - y_min) / (y_max - y_min) * (height - 1))
        col = max(0, min(width - 1, col))
        row = max(0, min(height - 1, row))
        key = (row, col)
        density[key] = density.get(key, 0) + 1

    for (row, col), cnt in density.items():
        if cnt >= 5:
            grid[row][col] = '#'
        elif cnt >= 3:
            grid[row][col] = '*'
        elif cnt >= 2:
            grid[row][col] = 'o'
        else:
            grid[row][col] = '.'

    lines = []
    for r in range(height):
        if r == 0:
            label = f"{y_max:6.2f}"
        elif r == height - 1:
            label = f"{y_min:6.2f}"
        elif r == height // 2:
            label = f"{(y_max + y_min) / 2:6.2f}"
        else:
            label = "      "
        lines.append(f"  {label} |{''.join(grid[r])}|")

    lines.append(f"         +{'-' * width}+")
    lines.append(f"         {x_min:<6.2f}{' ' * (width - 12)}{x_max:>6.2f}")
    lines.append(f"         {' ' * ((width - len(xlabel)) // 2)}{xlabel}")

    header = f"  {ylabel}"
    lines.insert(0, header)

    return '\n'.join(lines)


# ─────────────────────────────────────────────
# 메인 분석
# ─────────────────────────────────────────────

def run_analysis(steps=10000):
    """격자 스캔 → Compass/CCT 동시 계산 → 상관 분석."""

    combos = []
    for d in D_VALUES:
        for p in P_VALUES:
            for i_val in I_VALUES:
                combos.append((d, p, i_val))

    total = len(combos)
    print()
    print("=" * 65)
    print("  실험 16: Compass 점수와 CCT 점수의 상관관계 분석")
    print("=" * 65)
    print()
    print(f"  격자: D={len(D_VALUES)} x P={len(P_VALUES)} x I={len(I_VALUES)}"
          f" = {total}개 조합")
    print(f"  로렌츠 시뮬레이션: {steps:,} steps/조합")
    print(f"  골든존: I in [{GOLDEN_LOWER:.4f}, {GOLDEN_UPPER:.4f}]")
    print()

    # 모집단 통계 사전 캐시
    _get_pop_stats()

    # 결과 저장
    records = []
    t_start = time.time()

    for idx, (d, p, i_val) in enumerate(combos):
        # Compass 계산
        compass_score, z, cusp, boltz = compute_compass_score(d, p, i_val)

        # G 계산
        g = genius_score(d, p, i_val)

        # 로렌츠 파라미터 매핑 → CCT
        sigma, rho, beta, noise, gap_ratio = dpi_to_lorenz(d, p, i_val)
        _, S = lorenz_simulate(sigma, rho, beta, noise, gap_ratio,
                               steps=steps, dt=0.01, seed=42)
        cct_total, cct_passes, cct_avg = run_cct(S, gap_ratio)

        # 가설 166
        h166 = hypothesis_166(i_val, compass_score)

        records.append({
            'd': d, 'p': p, 'i': i_val,
            'g': g, 'z': z,
            'compass': compass_score,
            'cct_total': cct_total,
            'cct_passes': cct_passes,
            'cct_avg': cct_avg,
            'h166': h166,
            'p_genius': boltz['p_genius'],
        })

        # 진행 표시
        if (idx + 1) % 20 == 0 or idx + 1 == total:
            elapsed = time.time() - t_start
            eta = elapsed / (idx + 1) * (total - idx - 1)
            print(f"\r  진행: {idx + 1}/{total}"
                  f"  ({elapsed:.1f}s / ETA {eta:.1f}s)", end="", flush=True)

    elapsed_total = time.time() - t_start
    print(f"\n  완료! ({elapsed_total:.1f}초)")
    print()

    # ── 데이터 추출 ──
    compass_arr = np.array([r['compass'] for r in records])
    cct_total_arr = np.array([r['cct_total'] for r in records])
    cct_avg_arr = np.array([r['cct_avg'] for r in records])
    g_arr = np.array([r['g'] for r in records])
    i_arr = np.array([r['i'] for r in records])
    z_arr = np.array([r['z'] for r in records])

    # ── 1. 상관계수 ──
    print("-" * 65)
    print("  [1] Pearson 상관계수")
    print("-" * 65)

    pairs = [
        ("Compass vs CCT(total)", compass_arr, cct_total_arr),
        ("Compass vs CCT(avg)",   compass_arr, cct_avg_arr),
        ("G vs CCT(total)",       g_arr,       cct_total_arr),
        ("G vs CCT(avg)",         g_arr,       cct_avg_arr),
        ("I vs CCT(total)",       i_arr,       cct_total_arr),
        ("I vs CCT(avg)",         i_arr,       cct_avg_arr),
        ("Z vs CCT(total)",       z_arr,       cct_total_arr),
        ("Compass vs G",          compass_arr, g_arr),
    ]

    print()
    print(f"  {'측정 쌍':<28} {'r':>8} {'p-value':>12} {'판정':>10}")
    print(f"  {'─' * 28} {'─' * 8} {'─' * 12} {'─' * 10}")

    for label, x, y in pairs:
        if np.std(x) < 1e-12 or np.std(y) < 1e-12:
            print(f"  {label:<28} {'N/A':>8} {'N/A':>12} {'분산=0':>10}")
            continue
        r, pval = stats.pearsonr(x, y)
        if pval < 0.001:
            sig = "***"
        elif pval < 0.01:
            sig = "**"
        elif pval < 0.05:
            sig = "*"
        else:
            sig = "n.s."
        print(f"  {label:<28} {r:>8.4f} {pval:>12.2e} {sig:>10}")

    # ── 2. Compass > 0 vs <= 0 비교 ──
    print()
    print("-" * 65)
    print("  [2] Compass > 0 vs Compass = 0 : CCT 비교")
    print("-" * 65)

    mask_pos = compass_arr > 0
    mask_zero = compass_arr <= 0

    n_pos = mask_pos.sum()
    n_zero = mask_zero.sum()

    if n_pos > 0 and n_zero > 0:
        cct_pos_mean = cct_total_arr[mask_pos].mean()
        cct_pos_std = cct_total_arr[mask_pos].std()
        cct_zero_mean = cct_total_arr[mask_zero].mean()
        cct_zero_std = cct_total_arr[mask_zero].std()

        # t-검정
        t_stat, t_pval = stats.ttest_ind(
            cct_total_arr[mask_pos], cct_total_arr[mask_zero]
        )

        print()
        print(f"  {'그룹':<20} {'N':>5} {'CCT 평균':>10} {'CCT 표준편차':>12}")
        print(f"  {'─' * 20} {'─' * 5} {'─' * 10} {'─' * 12}")
        print(f"  {'Compass > 0':<20} {n_pos:>5} {cct_pos_mean:>10.3f} {cct_pos_std:>12.3f}")
        print(f"  {'Compass = 0':<20} {n_zero:>5} {cct_zero_mean:>10.3f} {cct_zero_std:>12.3f}")
        print()
        print(f"  t-검정: t = {t_stat:.3f}, p = {t_pval:.2e}")
        if t_pval < 0.05:
            print(f"  --> 유의미한 차이 (p < 0.05)")
        else:
            print(f"  --> 유의미한 차이 없음 (p >= 0.05)")
    else:
        print(f"  Compass > 0: {n_pos}개, Compass = 0: {n_zero}개")
        print(f"  한쪽 그룹이 비어 비교 불가")

    # ── 3. 가설 166 vs CCT 5/5 일치도 ──
    print()
    print("-" * 65)
    print("  [3] 가설 166 판정 vs CCT 5/5 일치도")
    print("-" * 65)

    h166_arr = np.array([r['h166'] for r in records])
    cct55_arr = cct_total_arr >= 5.0

    # 혼동 행렬
    tp = np.sum(h166_arr & cct55_arr)
    fp = np.sum(h166_arr & ~cct55_arr)
    fn = np.sum(~h166_arr & cct55_arr)
    tn = np.sum(~h166_arr & ~cct55_arr)

    accuracy = (tp + tn) / total
    precision = tp / (tp + fp) if (tp + fp) > 0 else 0
    recall = tp / (tp + fn) if (tp + fn) > 0 else 0
    f1 = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0

    print()
    print(f"                    CCT 5/5     CCT < 5")
    print(f"  H166 = True    {tp:>8}     {fp:>8}     (예측: 의식)")
    print(f"  H166 = False   {fn:>8}     {tn:>8}     (예측: 비의식)")
    print()
    print(f"  정확도(Accuracy)  = {accuracy:.4f}")
    print(f"  정밀도(Precision) = {precision:.4f}")
    print(f"  재현율(Recall)    = {recall:.4f}")
    print(f"  F1 Score          = {f1:.4f}")

    # CCT >= 4 기준도 추가 비교
    cct4_arr = cct_total_arr >= 4.0
    tp4 = np.sum(h166_arr & cct4_arr)
    fp4 = np.sum(h166_arr & ~cct4_arr)
    fn4 = np.sum(~h166_arr & cct4_arr)
    tn4 = np.sum(~h166_arr & ~cct4_arr)
    acc4 = (tp4 + tn4) / total

    print()
    print(f"  (참고: CCT >= 4 기준 시 정확도 = {acc4:.4f})")

    # ── 4. ASCII 산점도 ──
    print()
    print("-" * 65)
    print("  [4] ASCII 산점도: Compass vs CCT(total)")
    print("-" * 65)
    print()
    print(ascii_scatter(
        compass_arr.tolist(), cct_total_arr.tolist(),
        xlabel="Compass Score",
        ylabel="  CCT Total (/5)",
    ))

    print()
    print("-" * 65)
    print("  [5] ASCII 산점도: I vs CCT(total)")
    print("-" * 65)
    print()
    print(ascii_scatter(
        i_arr.tolist(), cct_total_arr.tolist(),
        xlabel="Inhibition (I)",
        ylabel="  CCT Total (/5)",
    ))

    # ── 5. I 구간별 CCT 분포 ──
    print()
    print("-" * 65)
    print("  [6] I 구간별 CCT 평균")
    print("-" * 65)
    print()
    print(f"  {'I값':>6} {'N':>4} {'CCT평균':>8} {'CCT범위':>14}"
          f" {'골든존':>8} {'Compass평균':>12}")
    print(f"  {'─' * 6} {'─' * 4} {'─' * 8} {'─' * 14}"
          f" {'─' * 8} {'─' * 12}")

    for iv in I_VALUES:
        mask = np.isclose(i_arr, iv)
        n_iv = mask.sum()
        if n_iv == 0:
            continue
        cct_mean = cct_total_arr[mask].mean()
        cct_min = cct_total_arr[mask].min()
        cct_max = cct_total_arr[mask].max()
        comp_mean = compass_arr[mask].mean()
        in_golden = "Yes" if GOLDEN_LOWER <= iv <= GOLDEN_UPPER else "No"
        print(f"  {iv:>6.2f} {n_iv:>4} {cct_mean:>8.2f}"
              f" {cct_min:>5.1f} ~ {cct_max:>5.1f}"
              f" {in_golden:>8} {comp_mean:>12.4f}")

    # ── 6. 결론 ──
    print()
    print("=" * 65)
    print("  [결론]")
    print("=" * 65)
    print()

    # Compass-CCT 상관 판정
    r_compass_cct, p_compass_cct = stats.pearsonr(compass_arr, cct_total_arr)
    r_i_cct, p_i_cct = stats.pearsonr(i_arr, cct_total_arr)

    if abs(r_compass_cct) > 0.7:
        rel = "강한 상관 (종속)"
    elif abs(r_compass_cct) > 0.4:
        rel = "중간 상관 (부분 종속)"
    elif abs(r_compass_cct) > 0.2:
        rel = "약한 상관 (약한 종속)"
    else:
        rel = "거의 무상관 (독립에 가까움)"

    print(f"  Compass vs CCT: r = {r_compass_cct:.4f} (p = {p_compass_cct:.2e})")
    print(f"  --> {rel}")
    print()
    print(f"  I vs CCT:       r = {r_i_cct:.4f} (p = {p_i_cct:.2e})")
    if abs(r_i_cct) > abs(r_compass_cct):
        print(f"  --> I가 Compass보다 CCT와 더 직접적으로 관련")
    else:
        print(f"  --> Compass가 I보다 CCT와 더 직접적으로 관련")
    print()

    print(f"  가설 166 판정 vs CCT 일치도: {accuracy:.1%}")
    if accuracy > 0.7:
        print(f"  --> 가설 166의 의식 판정이 CCT와 높은 일치")
    else:
        print(f"  --> 가설 166과 CCT는 다른 측면을 측정")
    print()
    print("=" * 65)

    return records


def main():
    parser = argparse.ArgumentParser(
        description="실험 16: Compass 점수와 CCT 점수의 상관관계 분석",
    )
    parser.add_argument("--grid", type=int, default=None,
                        help="간소화 격자 (각 축 N단계, 기본: 사전 정의 격자)")
    parser.add_argument("--steps", type=int, default=10000,
                        help="로렌츠 시뮬레이션 스텝 수 (기본: 10000)")
    args = parser.parse_args()

    if args.grid is not None:
        global D_VALUES, P_VALUES, I_VALUES
        D_VALUES = np.linspace(0.1, 0.7, args.grid).tolist()
        P_VALUES = np.linspace(0.3, 0.9, args.grid).tolist()
        I_VALUES = np.linspace(0.1, 0.7, args.grid).tolist()

    run_analysis(steps=args.steps)


if __name__ == "__main__":
    main()
