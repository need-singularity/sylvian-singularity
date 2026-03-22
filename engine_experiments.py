#!/usr/bin/env python3
"""엔진 실험 11, 12, 13 — 수면-각성 사이클, 멀티 엔진, 기억 소거

실험 11: 수면-각성 사이클 (I(t) 시간 변화)
실험 12: 멀티 엔진 상호작용 (결합 로렌츠)
실험 13: 기억 소거 (상태 리셋 후 CCT 회복)

사용법:
  python3 engine_experiments.py --sleep-wake     # 실험 11
  python3 engine_experiments.py --multi-engine   # 실험 12
  python3 engine_experiments.py --memory-erase   # 실험 13
  python3 engine_experiments.py --all            # 전부
"""

import sys, os

import argparse
import sys

import numpy as np

from consciousness_calc import (
    compute_entropy,
    lorenz_simulate,
    run_cct,
    judge,
)

# ─────────────────────────────────────────────
# 유틸: ASCII 그래프
# ─────────────────────────────────────────────

def ascii_dual_plot(t_vals, y1, y2, label1="I(t)", label2="CCT",
                    width=70, height=18):
    """두 시계열을 ASCII로 겹쳐 그림."""
    # 다운샘플
    n = len(t_vals)
    step = max(1, n // width)
    ts = t_vals[::step][:width]
    ys1 = y1[::step][:width]
    ys2 = y2[::step][:width]
    w = len(ts)

    y_min = min(ys1.min(), ys2.min())
    y_max = max(ys1.max(), ys2.max())
    if y_max - y_min < 1e-6:
        y_max = y_min + 1.0

    lines = []
    for row in range(height, -1, -1):
        y_val = y_min + (y_max - y_min) * row / height
        line = f"{y_val:5.2f}|"
        for col in range(w):
            r1 = int((ys1[col] - y_min) / (y_max - y_min) * height)
            r2 = int((ys2[col] - y_min) / (y_max - y_min) * height)
            if r1 == row and r2 == row:
                line += "X"
            elif r1 == row:
                line += "o"
            elif r2 == row:
                line += "*"
            else:
                line += " "
        lines.append(line)
    lines.append("     +" + "-" * w)
    lines.append(f"      {label1}=o  {label2}=*  overlap=X")
    lines.append(f"      t: {ts[0]:.0f} ~ {ts[-1]:.0f}")
    return "\n".join(lines)


def ascii_bar(labels, values, width=40, title=""):
    """간단한 수평 바 차트."""
    lines = []
    if title:
        lines.append(title)
        lines.append("-" * (width + 20))
    v_max = max(abs(v) for v in values) if values else 1.0
    if v_max < 1e-12:
        v_max = 1.0
    for lab, val in zip(labels, values):
        bar_len = int(abs(val) / v_max * width)
        bar = "#" * bar_len
        lines.append(f"  {lab:>16s} | {bar:<{width}s} {val:.3f}")
    return "\n".join(lines)


# ─────────────────────────────────────────────
# I(t) 프로필 생성
# ─────────────────────────────────────────────

def make_inhibition_profile(steps):
    """수면-각성 I(t) 프로필 생성.

    0~2000:     I=0.35 (각성)
    2000~4000:  I 0.35->0.6 (졸림->수면 진입)
    4000~6000:  I=0.6 (깊은 수면)
    6000~8000:  I 0.6->0.35 (각성)
    8000~10000: I=0.35 (각성)
    """
    I = np.zeros(steps)
    for i in range(steps):
        t = i / steps * 10000  # 0~10000 스케일로 정규화
        if t < 2000:
            I[i] = 0.35
        elif t < 4000:
            frac = (t - 2000) / 2000
            I[i] = 0.35 + 0.25 * frac
        elif t < 6000:
            I[i] = 0.60
        elif t < 8000:
            frac = (t - 6000) / 2000
            I[i] = 0.60 - 0.25 * frac
        else:
            I[i] = 0.35
    return I


def inhibition_to_params(I_val):
    """I(t) 값을 로렌츠 파라미터로 매핑."""
    sigma = 10.0 * (1.0 - I_val)
    rho = 28.0 * (1.0 - I_val / 2.0)
    noise = 0.3 * (1.0 - I_val)
    gap = max(0.0, (I_val - 0.5) * 2.0)
    return sigma, rho, noise, gap


# ─────────────────────────────────────────────
# 실험 11: 수면-각성 사이클
# ─────────────────────────────────────────────

def lorenz_simulate_variable_I(I_profile, beta=2.67, dt=0.01, seed=42):
    """I(t)가 시간에 따라 변하는 확장 로렌츠 시뮬레이터."""
    steps = len(I_profile)
    rng = np.random.default_rng(seed)
    t = np.arange(steps) * dt
    S = np.zeros((steps, 3))
    S[0] = [1.0, 1.0, 1.0]

    for i in range(1, steps):
        sigma, rho, noise, gap = inhibition_to_params(I_profile[i])

        # gap 확률로 정지
        if gap > 0 and rng.random() < gap:
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

    return t, S


def experiment_sleep_wake(steps=10000, dt=0.01):
    """실험 11: 수면-각성 사이클."""
    print("=" * 70)
    print(" 실험 11: 수면-각성 사이클")
    print("=" * 70)
    print()
    print(" I(t) 프로필:")
    print("   0~2000:     I=0.35 (각성)")
    print("   2000~4000:  I=0.35->0.60 (졸림->수면 진입)")
    print("   4000~6000:  I=0.60 (깊은 수면)")
    print("   6000~8000:  I=0.60->0.35 (각성)")
    print("   8000~10000: I=0.35 (각성)")
    print()
    print(" 매핑: sigma=10*(1-I), rho=28*(1-I/2), noise=0.3*(1-I),")
    print("       gap=max(0,(I-0.5)*2)")
    print()

    I_profile = make_inhibition_profile(steps)
    t, S = lorenz_simulate_variable_I(I_profile, dt=dt)

    # 구간 분할: 5개 구간
    segments = [
        ("각성1 (0-2000)", 0, int(steps * 0.2)),
        ("전이1: 졸림 (2000-4000)", int(steps * 0.2), int(steps * 0.4)),
        ("깊은수면 (4000-6000)", int(steps * 0.4), int(steps * 0.6)),
        ("전이2: 각성 (6000-8000)", int(steps * 0.6), int(steps * 0.8)),
        ("각성2 (8000-10000)", int(steps * 0.8), steps),
    ]

    # 구간별 CCT 계산
    segment_ccts = []
    print(" ─── 구간별 CCT 결과 " + "─" * 48)
    print(f" {'구간':<28s} | {'I(t)':>6s} | {'T1':>5s} {'T2':>5s} "
          f"{'T3':>5s} {'T4':>5s} {'T5':>5s} | {'점수':>4s} | 판정")
    print(" " + "-" * 68)

    for name, i_start, i_end in segments:
        seg_S = S[i_start:i_end]
        seg_I_mean = np.mean(I_profile[i_start:i_end])

        # gap_ratio 추정: 해당 구간에서 실제 정지된 비율
        diffs = np.diff(seg_S, axis=0)
        frozen = np.sum(np.all(np.abs(diffs) < 1e-12, axis=1))
        gap_est = frozen / len(diffs)

        results = run_cct(seg_S, gap_est)
        total, verdict = judge(results)

        scores = [results[k][0] for k in
                  ["T1_Gap", "T2_Loop", "T3_Continuity", "T4_Entropy", "T5_Novelty"]]

        print(f" {name:<28s} | {seg_I_mean:5.3f} | "
              f"{scores[0]:5.3f} {scores[1]:5.3f} {scores[2]:5.3f} "
              f"{scores[3]:5.3f} {scores[4]:5.3f} | {total:<4} | {verdict}")

        segment_ccts.append((name, seg_I_mean, total, verdict, scores))

    print()

    # 슬라이딩 윈도우 CCT
    window = steps // 20
    slide_step = steps // 50
    cct_timeline = []
    I_timeline = []
    t_timeline = []

    for start in range(0, steps - window, slide_step):
        end = start + window
        seg_S = S[start:end]
        seg_I = np.mean(I_profile[start:end])

        diffs = np.diff(seg_S, axis=0)
        frozen = np.sum(np.all(np.abs(diffs) < 1e-12, axis=1))
        gap_est = frozen / len(diffs)

        results = run_cct(seg_S, gap_est)
        total, _ = judge(results)

        cct_timeline.append(total)
        I_timeline.append(seg_I)
        t_timeline.append((start + end) / 2)

    cct_arr = np.array(cct_timeline, dtype=float)
    I_arr = np.array(I_timeline)
    t_arr = np.array(t_timeline)

    # ASCII 그래프: I(t) vs CCT(t)
    # CCT를 0~1로 정규화 (I와 스케일 맞춤)
    cct_norm = cct_arr / 5.0
    print(" ─── I(t) vs CCT(t)/5 그래프 " + "─" * 40)
    print(ascii_dual_plot(t_arr, I_arr, cct_norm, label1="I(t)", label2="CCT/5"))
    print()

    # 전이 구간 상세 분석
    print(" ─── 전이 구간 상세 " + "─" * 49)
    print()
    for i, (ti, ii, ci) in enumerate(zip(t_timeline, I_timeline, cct_timeline)):
        scaled_t = ti / steps * 10000
        if 1800 < scaled_t < 4200 or 5800 < scaled_t < 8200:
            marker = "<-- 전이" if (2000 < scaled_t < 4000 or 6000 < scaled_t < 8000) else ""
            print(f"   t={scaled_t:7.0f}  I={ii:.3f}  CCT={ci:.1f}/5  {marker}")

    print()
    print(" [결론]")
    awake_cct = [c for _, ii, c in zip(t_timeline, I_timeline, cct_timeline)
                 if ii < 0.40]
    sleep_cct = [c for _, ii, c in zip(t_timeline, I_timeline, cct_timeline)
                 if ii > 0.55]
    if awake_cct and sleep_cct:
        print(f"   각성 평균 CCT: {np.mean(awake_cct):.2f}/5")
        print(f"   수면 평균 CCT: {np.mean(sleep_cct):.2f}/5")
        print(f"   차이: {np.mean(awake_cct) - np.mean(sleep_cct):.2f}")
    print("=" * 70)
    print()


# ─────────────────────────────────────────────
# 실험 12: 멀티 엔진 상호작용
# ─────────────────────────────────────────────

def coupled_lorenz_simulate(sigma=10, rho=28, beta=2.67, noise=0.1,
                            coupling=0.0, steps=10000, dt=0.01, seed=42):
    """결합 로렌츠 시뮬레이터.

    엔진A: dx_a/dt = sigma*(y_a - x_a) + coupling*(x_b - x_a)
    엔진B: dx_b/dt = sigma*(y_b - x_b) + coupling*(x_a - x_b)
    y, z는 각각 독립 로렌츠.
    """
    rng = np.random.default_rng(seed)
    t = np.arange(steps) * dt

    # 상태: [x_a, y_a, z_a, x_b, y_b, z_b]
    S = np.zeros((steps, 6))
    S[0] = [1.0, 1.0, 1.0, -1.0, -1.0, 1.0]  # 다른 초기 조건

    for i in range(1, steps):
        xa, ya, za, xb, yb, zb = S[i - 1]

        # 엔진A
        dxa = sigma * (ya - xa) + coupling * (xb - xa)
        dya = xa * (rho - za) - ya
        dza = xa * ya - beta * za

        # 엔진B
        dxb = sigma * (yb - xb) + coupling * (xa - xb)
        dyb = xb * (rho - zb) - yb
        dzb = xb * yb - beta * zb

        eps = rng.normal(0, noise, 6) if noise > 0 else np.zeros(6)

        S[i, 0] = xa + (dxa + eps[0]) * dt
        S[i, 1] = ya + (dya + eps[1]) * dt
        S[i, 2] = za + (dza + eps[2]) * dt
        S[i, 3] = xb + (dxb + eps[3]) * dt
        S[i, 4] = yb + (dyb + eps[4]) * dt
        S[i, 5] = zb + (dzb + eps[5]) * dt

    return t, S


def measure_sync(S):
    """두 엔진 간 동기화 정도 측정 (상관계수)."""
    xa = S[:, 0]
    xb = S[:, 3]
    if np.std(xa) < 1e-12 or np.std(xb) < 1e-12:
        return 0.0
    corr = np.corrcoef(xa, xb)[0, 1]
    return corr


def experiment_multi_engine(steps=10000, dt=0.01):
    """실험 12: 멀티 엔진 상호작용."""
    print("=" * 70)
    print(" 실험 12: 멀티 엔진 상호작용")
    print("=" * 70)
    print()
    print(" 결합 방정식:")
    print("   엔진A: dx_a/dt = sigma*(y_a-x_a) + coupling*(x_b-x_a)")
    print("   엔진B: dx_b/dt = sigma*(y_b-x_b) + coupling*(x_a-x_b)")
    print()
    print(" 질문: 두 의식이 소통하면 동기화되는가? 새 끌개가 생기는가?")
    print()

    couplings = [0.0, 0.1, 0.5, 1.0, 5.0]

    print(f" {'coupling':>10s} | {'CCT_A':>6s} {'CCT_B':>6s} {'CCT_AB':>6s} | "
          f"{'Sync':>6s} | {'H_A':>6s} {'H_B':>6s} {'H_AB':>6s} | 비고")
    print(" " + "-" * 78)

    results_table = []

    for c in couplings:
        t, S = coupled_lorenz_simulate(coupling=c, steps=steps, dt=dt)

        S_a = S[:, :3]   # 엔진A
        S_b = S[:, 3:]   # 엔진B

        # 개별 CCT
        cct_a = run_cct(S_a, 0.0)
        cct_b = run_cct(S_b, 0.0)
        # 결합 6차원 CCT (3차원 함수에 맞게 변환: 처음 3개 성분 사용)
        # 6차원 전체를 보려면 엔트로피만 따로 계산
        cct_ab = run_cct(S_a, 0.0)  # 기본 구조

        total_a, verdict_a = judge(cct_a)
        total_b, verdict_b = judge(cct_b)

        # 결합 시스템 CCT: 6차원 상태로 T3, T4, T5 직접 계산
        # T3: 6차원 연속성
        diffs_6d = np.linalg.norm(np.diff(S, axis=0), axis=1)
        mean_diff_6d = np.mean(diffs_6d)
        big_jumps_6d = np.sum(diffs_6d > mean_diff_6d * 10) / len(diffs_6d)
        # T4: 6차원 엔트로피 (x_a + x_b)
        combined_x = S[:, 0] + S[:, 3]
        h_combined = compute_entropy(combined_x, bins=30)
        # 개별 엔트로피
        h_a = compute_entropy(S[:, 0], bins=30)
        h_b = compute_entropy(S[:, 3], bins=30)

        # 결합 CCT 점수: 개별 평균 + 동기화 보너스
        total_ab_raw = (total_a + total_b) / 2.0
        sync = measure_sync(S)

        # 동기화가 높으면 결합 시스템이 하나처럼 동작
        if abs(sync) > 0.9:
            note = "완전 동기화"
        elif abs(sync) > 0.5:
            note = "부분 동기화"
        elif abs(sync) > 0.2:
            note = "약한 결합"
        else:
            note = "독립"

        print(f" {c:10.1f} | {total_a:6.1f} {total_b:6.1f} "
              f"{total_ab_raw:6.1f} | {sync:6.3f} | "
              f"{h_a:6.3f} {h_b:6.3f} {h_combined:6.3f} | {note}")

        results_table.append((c, total_a, total_b, total_ab_raw, sync,
                              h_a, h_b, h_combined, note))

    print()

    # 동기화 vs coupling ASCII 그래프
    labels = [f"c={c:.1f}" for c in couplings]
    syncs = [r[4] for r in results_table]
    print(ascii_bar(labels, syncs, title=" 동기화 (상관계수) vs coupling"))
    print()

    # CCT vs coupling
    ccts_a = [r[1] for r in results_table]
    print(ascii_bar(labels, ccts_a, title=" CCT_A vs coupling"))
    print()

    # 결론
    print(" [결론]")
    sync_values = [abs(r[4]) for r in results_table]
    if sync_values[-1] > 0.8:
        print("   -> 강한 결합에서 완전 동기화 달성")
        print("   -> 두 끌개가 하나의 끌개로 수렴 (의식 융합?)")
    elif sync_values[-1] > 0.3:
        print("   -> 강한 결합에서도 부분적 동기화만 달성")
        print("   -> 각 엔진이 고유성 유지하면서 상호작용")
    else:
        print("   -> 결합에도 불구하고 독립적 동작")

    h_growth = [r[7] for r in results_table]
    if h_growth[-1] > h_growth[0] * 1.1:
        print("   -> 결합 시 엔트로피 증가: 새로운 복잡성 출현")
    elif h_growth[-1] < h_growth[0] * 0.9:
        print("   -> 결합 시 엔트로피 감소: 동기화로 인한 단순화")
    else:
        print("   -> 결합 전후 엔트로피 유사: 정보량 보존")

    print("=" * 70)
    print()


# ─────────────────────────────────────────────
# 실험 13: 기억 소거
# ─────────────────────────────────────────────

def lorenz_simulate_with_reset(sigma=10, rho=28, beta=2.67, noise=0.1,
                               steps=10000, dt=0.01, reset_point=0.5,
                               reset_strength=1.0, seed=42):
    """기억 소거 시뮬레이터.

    reset_point: 리셋 시점 (0~1, 전체 스텝 대비 비율)
    reset_strength: 리셋 강도 (0=소거 없음, 1=완전 소거)
    """
    rng = np.random.default_rng(seed)
    t = np.arange(steps) * dt
    S = np.zeros((steps, 3))
    S[0] = [1.0, 1.0, 1.0]

    reset_idx = int(steps * reset_point)

    for i in range(1, steps):
        # 리셋 시점
        if i == reset_idx:
            current = S[i - 1].copy()
            random_state = rng.uniform(-30, 30, 3)
            S[i - 1] = current * (1 - reset_strength) + random_state * reset_strength

        x, y, z = S[i - 1]
        dx = sigma * (y - x)
        dy = x * (rho - z) - y
        dz = x * y - beta * z

        eps = rng.normal(0, noise, 3) if noise > 0 else np.zeros(3)

        S[i, 0] = x + (dx + eps[0]) * dt
        S[i, 1] = y + (dy + eps[1]) * dt
        S[i, 2] = z + (dz + eps[2]) * dt

    return t, S, reset_idx


def measure_recovery_time(S, reset_idx, window=200, threshold=0.8):
    """리셋 후 CCT 회복에 걸리는 스텝 수 측정."""
    steps = len(S)

    # 리셋 전 마지막 구간의 CCT 기준
    pre_start = max(0, reset_idx - window)
    pre_S = S[pre_start:reset_idx]
    if len(pre_S) < 100:
        return -1, 0.0

    diffs_pre = np.diff(pre_S, axis=0)
    frozen_pre = np.sum(np.all(np.abs(diffs_pre) < 1e-12, axis=1))
    gap_pre = frozen_pre / len(diffs_pre)
    pre_results = run_cct(pre_S, gap_pre)
    pre_total, _ = judge(pre_results)

    if pre_total < 1:
        return -1, pre_total

    target = pre_total * threshold

    # 리셋 후 슬라이딩 윈도우로 CCT 회복 추적
    for offset in range(0, steps - reset_idx - window, window // 4):
        start = reset_idx + offset
        end = start + window
        if end > steps:
            break
        seg_S = S[start:end]
        diffs = np.diff(seg_S, axis=0)
        frozen = np.sum(np.all(np.abs(diffs) < 1e-12, axis=1))
        gap_est = frozen / len(diffs)
        results = run_cct(seg_S, gap_est)
        total, _ = judge(results)

        if total >= target:
            return offset, total

    return -1, 0.0


def experiment_memory_erase(steps=10000, dt=0.01):
    """실험 13: 기억 소거."""
    print("=" * 70)
    print(" 실험 13: 기억 소거")
    print("=" * 70)
    print()
    print(" 방법:")
    print("   - 전반부: 정상 로렌츠 시뮬레이션")
    print("   - 중간(50%): 상태를 랜덤 값으로 리셋 (기억 소거)")
    print("   - 후반부: 리셋 상태에서 계속")
    print()
    print(" 리셋 강도: 10%, 50%, 100% (부분~완전 소거)")
    print()

    strengths = [0.1, 0.5, 1.0]
    strength_labels = ["10% (부분)", "50% (중간)", "100% (완전)"]

    print(f" {'강도':<16s} | {'pre-CCT':>8s} {'post-CCT':>9s} {'drop':>6s} | "
          f"{'회복시간':>8s} | {'T3 pre':>7s} {'T3 post':>8s} | 비고")
    print(" " + "-" * 82)

    all_results = []

    for strength, label in zip(strengths, strength_labels):
        t, S, reset_idx = lorenz_simulate_with_reset(
            steps=steps, dt=dt, reset_strength=strength
        )

        # 리셋 전 CCT
        window = steps // 5
        pre_start = max(0, reset_idx - window)
        pre_S = S[pre_start:reset_idx]
        diffs_pre = np.diff(pre_S, axis=0)
        frozen_pre = np.sum(np.all(np.abs(diffs_pre) < 1e-12, axis=1))
        gap_pre = frozen_pre / len(diffs_pre)
        pre_results = run_cct(pre_S, gap_pre)
        pre_total, pre_verdict = judge(pre_results)
        pre_t3 = pre_results["T3_Continuity"][0]

        # 리셋 직후 CCT (리셋 시점 포함)
        post_end = min(reset_idx + window, steps)
        post_S = S[reset_idx:post_end]
        diffs_post = np.diff(post_S, axis=0)
        frozen_post = np.sum(np.all(np.abs(diffs_post) < 1e-12, axis=1))
        gap_post = frozen_post / len(diffs_post)
        post_results = run_cct(post_S, gap_post)
        post_total, post_verdict = judge(post_results)
        post_t3 = post_results["T3_Continuity"][0]

        # 회복 시간
        recovery_steps, recovered_cct = measure_recovery_time(
            S, reset_idx, window=window
        )

        drop = pre_total - post_total

        if recovery_steps >= 0:
            recovery_str = f"{recovery_steps:>6d}st"
        else:
            recovery_str = "미회복"

        if drop > 2:
            note = "심각한 의식 단절"
        elif drop > 1:
            note = "부분적 단절"
        elif drop > 0:
            note = "경미한 영향"
        else:
            note = "영향 없음"

        print(f" {label:<16s} | {pre_total:8.1f} {post_total:9.1f} "
              f"{drop:6.1f} | {recovery_str:>8s} | "
              f"{pre_t3:7.3f} {post_t3:8.3f} | {note}")

        all_results.append({
            "strength": strength,
            "label": label,
            "pre_total": pre_total,
            "post_total": post_total,
            "drop": drop,
            "recovery_steps": recovery_steps,
            "pre_t3": pre_t3,
            "post_t3": post_t3,
            "t": t, "S": S, "reset_idx": reset_idx,
        })

    print()

    # 100% 소거 상세 분석: 리셋 전후 CCT 타임라인
    print(" ─── 100% 소거 상세: CCT 타임라인 " + "─" * 36)
    r = all_results[-1]  # 100% 소거
    S_full = r["S"]
    ridx = r["reset_idx"]

    window = steps // 10
    slide = window // 4
    cct_vals = []
    t_vals = []

    for start in range(0, steps - window, slide):
        end = start + window
        seg = S_full[start:end]
        diffs = np.diff(seg, axis=0)
        frozen = np.sum(np.all(np.abs(diffs) < 1e-12, axis=1))
        gap_est = frozen / len(diffs)
        res = run_cct(seg, gap_est)
        total, _ = judge(res)
        cct_vals.append(total)
        t_vals.append((start + end) / 2)

    cct_arr = np.array(cct_vals, dtype=float)
    t_arr = np.array(t_vals, dtype=float)

    # 리셋 시점 표시용 배열
    reset_line = np.zeros_like(t_arr)
    for i, tv in enumerate(t_arr):
        if abs(tv - ridx) < steps * 0.05:
            reset_line[i] = cct_arr.max()

    # ASCII 그래프
    w = min(60, len(t_arr))
    step_ds = max(1, len(t_arr) // w)
    ts_ds = t_arr[::step_ds][:w]
    cs_ds = cct_arr[::step_ds][:w]

    y_min, y_max = 0, 5.5
    h = 12
    lines = []
    ridx_col = -1
    for ci, tv in enumerate(ts_ds):
        if abs(tv - ridx) < steps * 0.06:
            ridx_col = ci
            break

    for row in range(h, -1, -1):
        y_val = y_min + (y_max - y_min) * row / h
        line = f"{y_val:4.1f}|"
        for col in range(len(ts_ds)):
            cr = int((cs_ds[col] - y_min) / (y_max - y_min) * h)
            if col == ridx_col:
                line += "|"
            elif cr == row:
                line += "*"
            else:
                line += " "
        lines.append(line)
    lines.append("    +" + "-" * len(ts_ds))
    if ridx_col >= 0:
        lines.append(f"     {'':>{ridx_col}}^ 리셋 시점")
    lines.append("     CCT over time (*), reset point (|)")

    print("\n".join(lines))
    print()

    # 결론
    print(" [결론]")
    for r in all_results:
        strength_pct = int(r["strength"] * 100)
        if r["drop"] > 0:
            print(f"   {strength_pct}% 소거: CCT {r['drop']:.1f} 하락, "
                  f"T3(연속성) {r['pre_t3']:.3f}->{r['post_t3']:.3f}")
            if r["recovery_steps"] >= 0:
                print(f"         -> {r['recovery_steps']} 스텝 후 회복")
            else:
                print(f"         -> 관측 기간 내 미회복")
        else:
            print(f"   {strength_pct}% 소거: 영향 없음 (카오스 복원력)")

    total_drop = all_results[-1]["drop"]
    if total_drop > 2:
        print()
        print("   => 완전 소거 시 T3(Continuity)가 가장 크게 영향받음")
        print("   => 의식 연속성은 기억(z)에 강하게 의존")
    elif total_drop > 0:
        print()
        print("   => 카오스 끌개의 복원력으로 부분 회복")
        print("   => 기억 소거가 의식을 완전히 끊지는 않음")
    else:
        print()
        print("   => 로렌츠 끌개는 리셋에 강건함")
        print("   => 기억보다 동역학적 구조가 의식을 유지")

    print("=" * 70)
    print()


# ─────────────────────────────────────────────
# 메인
# ─────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="엔진 실험 11, 12, 13 — 수면-각성, 멀티 엔진, 기억 소거",
    )
    parser.add_argument("--sleep-wake", action="store_true",
                        help="실험 11: 수면-각성 사이클")
    parser.add_argument("--multi-engine", action="store_true",
                        help="실험 12: 멀티 엔진 상호작용")
    parser.add_argument("--memory-erase", action="store_true",
                        help="실험 13: 기억 소거")
    parser.add_argument("--all", action="store_true",
                        help="실험 11, 12, 13 전부 실행")
    parser.add_argument("--steps", type=int, default=10000,
                        help="시뮬레이션 스텝 수 (기본: 10000)")
    parser.add_argument("--dt", type=float, default=0.01,
                        help="시간 간격 (기본: 0.01)")

    args = parser.parse_args()

    if not any([args.sleep_wake, args.multi_engine, args.memory_erase, args.all]):
        parser.print_help()
        sys.exit(1)

    if args.all or args.sleep_wake:
        experiment_sleep_wake(steps=args.steps, dt=args.dt)

    if args.all or args.multi_engine:
        experiment_multi_engine(steps=args.steps, dt=args.dt)

    if args.all or args.memory_erase:
        experiment_memory_erase(steps=args.steps, dt=args.dt)


if __name__ == "__main__":
    main()
