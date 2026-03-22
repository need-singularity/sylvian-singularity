#!/usr/bin/env python3
"""이중 뇌 뇌량 시뮬레이터 — Dual Brain Corpus Callosum Model

인간 뇌의 좌반구(분석적)와 우반구(직관적)를 각각 로렌츠 끌개로 모델링하고,
뇌량(corpus callosum) 커플링 κ로 연결하여 의식 연속성을 분석한다.

수학 모델:
  좌반구: dx_L/dt = σ_L(y_L - x_L) + κ(x_R - x_L)  [σ=10, ρ=28, β=2.67, noise=0.05]
  우반구: dx_R/dt = σ_R(y_R - x_R) + κ(x_L - x_R)  [σ=12, ρ=32, β=2.2,  noise=0.2]
  κ: 뇌량 대역폭 (0=분리뇌, 0.5=정상, 5.0=과동기화)

사용법:
  python3 dual_brain_callosum.py                    # κ 스캔 (기본)
  python3 dual_brain_callosum.py --split-brain       # 분리뇌 실험
  python3 dual_brain_callosum.py --agenesis          # 뇌량 무형성
  python3 dual_brain_callosum.py --lateralize left   # 좌반구 우세
  python3 dual_brain_callosum.py --lateralize right  # 우반구 우세
  python3 dual_brain_callosum.py --kappa 0.5         # 특정 κ값
  python3 dual_brain_callosum.py --delay 10          # 전달 지연
  python3 dual_brain_callosum.py --all               # 전체 실험
  python3 dual_brain_callosum.py --plot              # matplotlib 저장
"""

import sys, os

import argparse
import os
import sys
from datetime import datetime

import numpy as np
from scipy import stats

# consciousness_calc.py에서 import
from consciousness_calc import run_cct, judge, compute_entropy

RESULTS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "results")

# ─────────────────────────────────────────────
# 반구 파라미터 정의
# ─────────────────────────────────────────────

LEFT_HEMISPHERE = {
    "sigma": 10, "rho": 28, "beta": 2.67, "noise": 0.05,
    "description": "좌반구 (분석적, 순차적)",
}

RIGHT_HEMISPHERE = {
    "sigma": 12, "rho": 32, "beta": 2.2, "noise": 0.2,
    "description": "우반구 (직관적, 전체적)",
}

# κ 스캔 기본값
KAPPA_SCAN_VALUES = [0.0, 0.01, 0.05, 0.1, 0.2, 0.5, 1.0, 2.0, 5.0]


# ─────────────────────────────────────────────
# 이중 뇌 시뮬레이터
# ─────────────────────────────────────────────

def dual_brain_simulate(left=None, right=None, kappa=0.5,
                        kappa_lr=None, kappa_rl=None,
                        delay=0, steps=50000, dt=0.01, seed=42,
                        kappa_schedule=None):
    """이중 뇌 결합 로렌츠 시뮬레이터.

    Parameters:
        left:   좌반구 파라미터 dict (sigma, rho, beta, noise)
        right:  우반구 파라미터 dict
        kappa:  대칭 커플링 강도 (기본 0.5)
        kappa_lr: 좌→우 전달 강도 (None이면 kappa 사용)
        kappa_rl: 우→좌 전달 강도 (None이면 kappa 사용)
        delay:  전달 지연 스텝 수 (0=즉시)
        steps:  시뮬레이션 스텝 수
        dt:     시간 간격
        seed:   난수 시드
        kappa_schedule: callable(t_index) -> kappa 값 (시간 변화 κ, 분리뇌용)

    Returns:
        t:  시간 배열 [steps]
        S:  상태 배열 [steps, 6] (x_L, y_L, z_L, x_R, y_R, z_R)
        kappas: κ 시계열 [steps] (스케줄 사용 시)
    """
    if left is None:
        left = LEFT_HEMISPHERE
    if right is None:
        right = RIGHT_HEMISPHERE

    # 비대칭 커플링
    k_lr = kappa_lr if kappa_lr is not None else kappa
    k_rl = kappa_rl if kappa_rl is not None else kappa

    rng = np.random.default_rng(seed)
    t = np.arange(steps) * dt
    S = np.zeros((steps, 6))
    # 좌우 다른 초기조건
    S[0] = [1.0, 1.0, 1.0, -1.0, 0.5, 1.5]

    kappas = np.full(steps, kappa, dtype=float)

    σ_L, ρ_L, β_L = left["sigma"], left["rho"], left["beta"]
    σ_R, ρ_R, β_R = right["sigma"], right["rho"], right["beta"]
    n_L, n_R = left["noise"], right["noise"]

    for i in range(1, steps):
        # 시간 변화 κ (분리뇌 실험용)
        if kappa_schedule is not None:
            cur_k = kappa_schedule(i)
            kappas[i] = cur_k
            k_lr_cur = cur_k
            k_rl_cur = cur_k
        else:
            k_lr_cur = k_lr
            k_rl_cur = k_rl

        xL, yL, zL, xR, yR, zR = S[i - 1]

        # 전달 지연: delay 스텝 전의 상대 반구 값 사용
        if delay > 0 and i > delay:
            xR_d, yR_d, zR_d = S[i - 1 - delay, 3], S[i - 1 - delay, 4], S[i - 1 - delay, 5]
            xL_d, yL_d, zL_d = S[i - 1 - delay, 0], S[i - 1 - delay, 1], S[i - 1 - delay, 2]
        else:
            xR_d, yR_d, zR_d = xR, yR, zR
            xL_d, yL_d, zL_d = xL, yL, zL

        # 좌반구 (분석적)
        dxL = σ_L * (yL - xL) + k_rl_cur * (xR_d - xL)
        dyL = xL * (ρ_L - zL) - yL + k_rl_cur * (yR_d - yL)
        dzL = xL * yL - β_L * zL + k_rl_cur * (zR_d - zL)

        # 우반구 (직관적)
        dxR = σ_R * (yR - xR) + k_lr_cur * (xL_d - xR)
        dyR = xR * (ρ_R - zR) - yR + k_lr_cur * (yL_d - yR)
        dzR = xR * yR - β_R * zR + k_lr_cur * (zL_d - zR)

        # 잡음 (좌: 낮은 잡음, 우: 높은 잡음)
        epsL = rng.normal(0, n_L, 3) if n_L > 0 else np.zeros(3)
        epsR = rng.normal(0, n_R, 3) if n_R > 0 else np.zeros(3)

        S[i, 0] = xL + (dxL + epsL[0]) * dt
        S[i, 1] = yL + (dyL + epsL[1]) * dt
        S[i, 2] = zL + (dzL + epsL[2]) * dt
        S[i, 3] = xR + (dxR + epsR[0]) * dt
        S[i, 4] = yR + (dyR + epsR[1]) * dt
        S[i, 5] = zR + (dzR + epsR[2]) * dt

    return t, S, kappas


# ─────────────────────────────────────────────
# 측정 함수
# ─────────────────────────────────────────────

def measure_sync(S):
    """좌우 반구 동기화도: corr(x_L, x_R)."""
    xL = S[:, 0]
    xR = S[:, 3]
    if np.std(xL) < 1e-12 or np.std(xR) < 1e-12:
        return 0.0
    return np.corrcoef(xL, xR)[0, 1]


def transfer_entropy(source, target, bins=10, lag=1):
    """Transfer Entropy: source → target.

    TE(S→T) = H(T_future | T_past) - H(T_future | T_past, S_past)
    이산화 후 조건부 엔트로피로 근사.
    """
    n = len(source) - lag
    if n < 100:
        return 0.0

    s_past = source[:n]
    t_past = target[:n]
    t_future = target[lag:lag + n]

    # 이산화
    s_bins = np.digitize(s_past, np.linspace(s_past.min(), s_past.max(), bins + 1)[:-1])
    t_bins_past = np.digitize(t_past, np.linspace(t_past.min(), t_past.max(), bins + 1)[:-1])
    t_bins_future = np.digitize(t_future, np.linspace(t_future.min(), t_future.max(), bins + 1)[:-1])

    # 결합 확률 계산
    # H(T_f, T_p) - H(T_p)
    def joint_entropy_2(a, b, nbins):
        hist = np.histogram2d(a, b, bins=nbins)[0]
        p = hist / hist.sum()
        p = p[p > 0]
        return -np.sum(p * np.log2(p + 1e-15))

    def joint_entropy_3(a, b, c, nbins):
        # 3D 히스토그램
        sample = np.column_stack([a, b, c])
        hist, _ = np.histogramdd(sample, bins=nbins)
        p = hist / hist.sum()
        p = p[p > 0]
        return -np.sum(p * np.log2(p + 1e-15))

    h_tf_tp = joint_entropy_2(t_bins_future, t_bins_past, bins)
    h_tp = compute_entropy(t_past.astype(float), bins=bins)
    h_tf_tp_sp = joint_entropy_3(t_bins_future, t_bins_past, s_bins, bins)
    h_tp_sp = joint_entropy_2(t_bins_past, s_bins, bins)

    # TE = H(T_f | T_p) - H(T_f | T_p, S_p)
    #    = [H(T_f, T_p) - H(T_p)] - [H(T_f, T_p, S_p) - H(T_p, S_p)]
    te = (h_tf_tp - h_tp) - (h_tf_tp_sp - h_tp_sp)
    return max(0.0, te)  # TE >= 0


def joint_entropy_2d(x, y, bins=30):
    """2D 결합 엔트로피 H(X, Y)."""
    hist = np.histogram2d(x, y, bins=bins)[0]
    p = hist / hist.sum()
    p = p[p > 0]
    return -np.sum(p * np.log(p + 1e-15))


def asymmetry_index(cct_L, cct_R):
    """좌우 비대칭 지수: |CCT_L - CCT_R| / (CCT_L + CCT_R)."""
    total = cct_L + cct_R
    if total < 1e-12:
        return 0.0
    return abs(cct_L - cct_R) / total


def measure_all(S, gap_ratio=0.0):
    """모든 측정 항목을 한 번에 계산.

    Returns:
        dict with keys: cct_L, cct_R, cct_combined, sync, te_lr, te_rl,
                         joint_h, sum_h, asymmetry, verdict_L, verdict_R, verdict_combined
    """
    S_L = S[:, :3]
    S_R = S[:, 3:]

    # CCT 개별
    results_L = run_cct(S_L, gap_ratio)
    results_R = run_cct(S_R, gap_ratio)

    total_L, verdict_L = judge(results_L)
    total_R, verdict_R = judge(results_R)

    # CCT 결합: 6차원 상태를 3차원으로 투영하여 CCT 실행
    # 방법: 좌우 x,y,z를 합산하여 단일 끌개로 간주
    S_combined = np.column_stack([
        S[:, 0] + S[:, 3],  # x_L + x_R
        S[:, 1] + S[:, 4],  # y_L + y_R
        S[:, 2] + S[:, 5],  # z_L + z_R
    ])
    results_combined = run_cct(S_combined, gap_ratio)
    total_combined, verdict_combined = judge(results_combined)

    # 동기화
    sync = measure_sync(S)

    # Transfer Entropy (다운샘플링으로 속도 확보)
    step = max(1, len(S) // 10000)
    xL_ds = S[::step, 0]
    xR_ds = S[::step, 3]
    te_lr = transfer_entropy(xL_ds, xR_ds, bins=8, lag=1)
    te_rl = transfer_entropy(xR_ds, xL_ds, bins=8, lag=1)

    # 결합 엔트로피
    h_L = compute_entropy(S[:, 0], bins=30)
    h_R = compute_entropy(S[:, 3], bins=30)
    h_joint = joint_entropy_2d(S[:, 0], S[:, 3], bins=30)
    h_sum = h_L + h_R

    # 비대칭
    asym = asymmetry_index(total_L, total_R)

    return {
        "cct_L": total_L, "verdict_L": verdict_L,
        "cct_R": total_R, "verdict_R": verdict_R,
        "cct_combined": total_combined, "verdict_combined": verdict_combined,
        "sync": sync,
        "te_lr": te_lr, "te_rl": te_rl,
        "h_joint": h_joint, "h_sum": h_sum,
        "asymmetry": asym,
        "results_L": results_L,
        "results_R": results_R,
        "results_combined": results_combined,
    }


# ─────────────────────────────────────────────
# 판정 로직
# ─────────────────────────────────────────────

def kappa_verdict(sync, te_lr, te_rl):
    """κ 상태 판정."""
    if abs(sync) > 0.9:
        return "과동기화"
    elif abs(sync) > 0.7:
        return "정상"
    elif abs(sync) > 0.3:
        return "약결합"
    elif abs(sync) > 0.1:
        return "미약"
    else:
        return "분리"


# ─────────────────────────────────────────────
# 실험 A: κ 스캔
# ─────────────────────────────────────────────

def experiment_kappa_scan(steps=50000, dt=0.01, kappas=None):
    """실험 A: 뇌량 강도 스캔."""
    if kappas is None:
        kappas = KAPPA_SCAN_VALUES

    print("=" * 90)
    print(" 실험 A: 뇌량 강도(κ) 스캔 — Corpus Callosum Bandwidth")
    print("=" * 90)
    print()
    print(" 좌반구: σ=10, ρ=28, β=2.67, noise=0.05 (분석적, 정밀)")
    print(" 우반구: σ=12, ρ=32, β=2.2,  noise=0.2  (직관적, 창의적)")
    print()

    header = (f"  {'κ':>5s} │ {'CCT_L':>5s} │ {'CCT_R':>5s} │ {'CCT_합':>6s} │ "
              f"{'동기화':>6s} │ {'TE_L→R':>6s} │ {'TE_R→L':>6s} │ "
              f"{'비대칭':>6s} │ 판정")
    sep = "  ─────┼───────┼───────┼────────┼────────┼────────┼────────┼────────┼─────────"
    print(header)
    print(sep)

    all_results = []

    for k in kappas:
        _, S, _ = dual_brain_simulate(kappa=k, steps=steps, dt=dt)
        m = measure_all(S)
        verdict = kappa_verdict(m["sync"], m["te_lr"], m["te_rl"])

        print(f"  {k:5.2f} │ {m['cct_L']:5.1f} │ {m['cct_R']:5.1f} │ "
              f"{m['cct_combined']:6.1f} │ {m['sync']:6.3f} │ "
              f"{m['te_lr']:6.3f} │ {m['te_rl']:6.3f} │ "
              f"{m['asymmetry']:6.3f} │ {verdict}")

        all_results.append((k, m, verdict))

    print()

    # 최적 κ 탐색
    best_k = None
    best_score = -1
    for k, m, v in all_results:
        # 최적: 높은 CCT_합 + 적절한 동기화 (0.3~0.8) + 낮은 비대칭
        if 0.3 < abs(m["sync"]) < 0.85:
            score = m["cct_combined"] - m["asymmetry"] * 2
            if score > best_score:
                best_score = score
                best_k = k

    print(" ─── 핵심 발견 ───")
    if best_k is not None:
        print(f"  최적 κ = {best_k} (동기화-다양성 균형)")
    else:
        print("  최적 κ: 판정 불가 (모든 κ에서 동기화 범위 밖)")

    # 임계값 찾기: sync가 0.5를 넘는 최소 κ
    threshold_k = None
    for k, m, v in all_results:
        if abs(m["sync"]) > 0.5 and threshold_k is None:
            threshold_k = k
    if threshold_k is not None:
        print(f"  통합 임계 κ ≈ {threshold_k} (동기화 > 0.5 — '하나의 의식' 후보)")

    # TE 비대칭 분석
    for k, m, v in all_results:
        if k == 0.5:  # 정상 뇌량
            if m["te_rl"] > m["te_lr"] * 1.2:
                print(f"  κ=0.5 정보 흐름: 우→좌 우세 (TE_R→L={m['te_rl']:.3f} > TE_L→R={m['te_lr']:.3f})")
            elif m["te_lr"] > m["te_rl"] * 1.2:
                print(f"  κ=0.5 정보 흐름: 좌→우 우세 (TE_L→R={m['te_lr']:.3f} > TE_R→L={m['te_rl']:.3f})")
            else:
                print(f"  κ=0.5 정보 흐름: 대칭적 (TE_L→R={m['te_lr']:.3f} ≈ TE_R→L={m['te_rl']:.3f})")

    print("=" * 90)
    return all_results


# ─────────────────────────────────────────────
# 실험 B: 분리뇌 (Split-brain)
# ─────────────────────────────────────────────

def experiment_split_brain(steps=50000, dt=0.01):
    """실험 B: Sperry 분리뇌 실험 재현.

    1. κ=0.5 (정상)에서 시작
    2. t=steps//2에서 κ=0으로 절단
    3. 절단 전후 CCT 비교
    """
    cut_step = steps // 2

    def kappa_schedule(i):
        return 0.5 if i < cut_step else 0.0

    print("=" * 90)
    print(" 실험 B: 분리뇌 (Split-Brain) — Sperry 실험 재현")
    print("=" * 90)
    print()
    print(f" 프로토콜: κ=0.5 (0~{cut_step} steps) → κ=0.0 ({cut_step}~{steps} steps)")
    print(f" 절단 시점: t = {cut_step * dt:.0f} (step {cut_step})")
    print()

    _, S, kappas = dual_brain_simulate(
        kappa=0.5, steps=steps, dt=dt, kappa_schedule=kappa_schedule
    )

    # 절단 전/후 분리 분석
    S_before = S[:cut_step]
    S_after = S[cut_step:]

    m_before = measure_all(S_before)
    m_after = measure_all(S_after)

    print(" ─── 절단 전 (κ=0.5, 정상 뇌량) ───")
    print(f"  CCT_L={m_before['cct_L']:.1f}/5  CCT_R={m_before['cct_R']:.1f}/5  "
          f"CCT_합={m_before['cct_combined']:.1f}/5")
    print(f"  동기화={m_before['sync']:.3f}  TE_L→R={m_before['te_lr']:.3f}  "
          f"TE_R→L={m_before['te_rl']:.3f}")
    print()

    print(" ─── 절단 후 (κ=0.0, 뇌량 절단) ───")
    print(f"  CCT_L={m_after['cct_L']:.1f}/5  CCT_R={m_after['cct_R']:.1f}/5  "
          f"CCT_합={m_after['cct_combined']:.1f}/5")
    print(f"  동기화={m_after['sync']:.3f}  TE_L→R={m_after['te_lr']:.3f}  "
          f"TE_R→L={m_after['te_rl']:.3f}")
    print()

    # ASCII 타임라인
    print(" ─── 동기화 타임라인 ───")
    _print_sync_timeline(S, cut_step, steps, dt)
    print()

    # 핵심 발견
    print(" ─── 핵심 발견 ───")
    sync_drop = abs(m_before["sync"]) - abs(m_after["sync"])
    print(f"  동기화 하락: {m_before['sync']:.3f} → {m_after['sync']:.3f} "
          f"(Δ = {sync_drop:.3f})")

    if m_after["cct_L"] >= 3 and m_after["cct_R"] >= 3:
        print("  → 양 반구 모두 독립적 CCT 유지 = 두 개의 의식?")
    elif m_after["cct_L"] >= 3 or m_after["cct_R"] >= 3:
        print("  → 한 반구만 CCT 유지 — 비대칭 의식 분리")
    else:
        print("  → 양 반구 모두 CCT 저하 — 뇌량 의존적 의식")

    print("=" * 90)
    return m_before, m_after, S, kappas


def _print_sync_timeline(S, cut_step, steps, dt):
    """동기화 변화 ASCII 타임라인."""
    n_windows = 40
    window_size = steps // n_windows

    syncs = []
    for w in range(n_windows):
        start = w * window_size
        end = start + window_size
        chunk = S[start:end]
        s = measure_sync(chunk)
        syncs.append(s)

    syncs = np.array(syncs)
    height = 10

    print(f"  동기화")
    for row in range(height, -1, -1):
        val = row / height
        line = f"  {val:4.1f}│"
        for col in range(n_windows):
            mid = col * window_size + window_size // 2
            mapped = int(max(0, syncs[col]) * height + 0.5)
            if mapped == row:
                line += "█"
            elif col * window_size <= cut_step < (col + 1) * window_size:
                line += "│"
            else:
                line += " "
        lines_out = line
        print(lines_out)

    cut_col = cut_step // window_size
    ruler = "  " + "    └" + "─" * cut_col + "┼" + "─" * (n_windows - cut_col - 1)
    print(ruler)
    print("  " + " " * (5 + cut_col) + "절단")


# ─────────────────────────────────────────────
# 실험 C: 뇌량 무형성 (Callosal Agenesis)
# ─────────────────────────────────────────────

def experiment_agenesis(steps=50000, dt=0.01):
    """실험 C: 선천적 뇌량 부재.

    κ=0 전체, 하지만 보상 메커니즘으로 noise 증가 (대안 경로 시뮬레이션).
    """
    print("=" * 90)
    print(" 실험 C: 뇌량 무형성 (Callosal Agenesis)")
    print("=" * 90)
    print()
    print(" 조건: κ=0 (태생적 뇌량 없음)")
    print(" 대안 경로: anterior commissure → noise 증가로 근사")
    print()

    conditions = [
        ("정상 뇌", 0.5, LEFT_HEMISPHERE, RIGHT_HEMISPHERE),
        ("뇌량 무형성 (보상 없음)", 0.0, LEFT_HEMISPHERE, RIGHT_HEMISPHERE),
        ("뇌량 무형성 (보상: noise↑)", 0.0,
         {**LEFT_HEMISPHERE, "noise": 0.15},
         {**RIGHT_HEMISPHERE, "noise": 0.4}),
        ("뇌량 무형성 (보상: noise↑↑)", 0.0,
         {**LEFT_HEMISPHERE, "noise": 0.3},
         {**RIGHT_HEMISPHERE, "noise": 0.6}),
    ]

    header = (f"  {'조건':>28s} │ {'κ':>4s} │ {'CCT_L':>5s} │ {'CCT_R':>5s} │ "
              f"{'CCT_합':>6s} │ {'동기화':>6s} │ {'비대칭':>6s}")
    sep = "  " + "─" * 28 + "┼──────┼───────┼───────┼────────┼────────┼────────"
    print(header)
    print(sep)

    for name, k, left, right in conditions:
        _, S, _ = dual_brain_simulate(left=left, right=right, kappa=k,
                                       steps=steps, dt=dt)
        m = measure_all(S)
        print(f"  {name:>28s} │ {k:4.1f} │ {m['cct_L']:5.1f} │ {m['cct_R']:5.1f} │ "
              f"{m['cct_combined']:6.1f} │ {m['sync']:6.3f} │ {m['asymmetry']:6.3f}")

    print()
    print(" ─── 해석 ───")
    print("  실제 뇌량 무형성 환자: 정상 IQ, 정상 의식 (보상 경로 존재)")
    print("  시뮬레이션: noise 증가가 대안 경로(전교련 등)를 근사")
    print("  핵심: 뇌량 없이도 의식 연속성 유지 가능한가?")
    print("=" * 90)


# ─────────────────────────────────────────────
# 실험 D: 좌우 우세 (Lateralization)
# ─────────────────────────────────────────────

def experiment_lateralize(direction="left", steps=50000, dt=0.01):
    """실험 D: 비대칭 뇌량 — 좌/우 반구 우세.

    좌반구 우세: κ_LR=0.3 (좌→우 약), κ_RL=0.7 (우→좌 강)
    우반구 우세: κ_LR=0.7 (좌→우 강), κ_RL=0.3 (우→좌 약)
    """
    print("=" * 90)
    print(f" 실험 D: 뇌량 비대칭 — {direction.upper()} 반구 우세")
    print("=" * 90)
    print()

    conditions = []

    if direction == "left":
        # 좌반구 우세: 우→좌 정보 강함 (좌가 더 많이 받음)
        conditions = [
            ("대칭 (대조군)", 0.5, 0.5),
            ("좌 약간 우세", 0.4, 0.6),
            ("좌 우세", 0.3, 0.7),
            ("좌 강한 우세", 0.2, 0.8),
        ]
    else:
        # 우반구 우세: 좌→우 정보 강함
        conditions = [
            ("대칭 (대조군)", 0.5, 0.5),
            ("우 약간 우세", 0.6, 0.4),
            ("우 우세", 0.7, 0.3),
            ("우 강한 우세", 0.8, 0.2),
        ]

    print(f"  {'조건':>16s} │ {'κ_LR':>5s} │ {'κ_RL':>5s} │ {'CCT_L':>5s} │ "
          f"{'CCT_R':>5s} │ {'동기화':>6s} │ {'TE_L→R':>6s} │ {'TE_R→L':>6s} │ {'비대칭':>6s}")
    sep = "  " + "─" * 16 + "┼───────┼───────┼───────┼───────┼────────┼────────┼────────┼────────"
    print(sep)

    for name, k_lr, k_rl in conditions:
        _, S, _ = dual_brain_simulate(
            kappa_lr=k_lr, kappa_rl=k_rl, steps=steps, dt=dt
        )
        m = measure_all(S)
        print(f"  {name:>16s} │ {k_lr:5.2f} │ {k_rl:5.2f} │ {m['cct_L']:5.1f} │ "
              f"{m['cct_R']:5.1f} │ {m['sync']:6.3f} │ "
              f"{m['te_lr']:6.3f} │ {m['te_rl']:6.3f} │ {m['asymmetry']:6.3f}")

    print()
    print(" ─── 해석 ───")
    if direction == "left":
        print("  좌반구 우세: 언어 처리, 논리적 사고 강화")
        print("  우→좌 전달 강화 = 직관을 분석으로 변환하는 능력 증가")
    else:
        print("  우반구 우세: 공간 처리, 예술적 직관 강화")
        print("  좌→우 전달 강화 = 분석을 통합적 직관으로 변환")
    print("=" * 90)


# ─────────────────────────────────────────────
# 단일 κ 실행
# ─────────────────────────────────────────────

def run_single_kappa(kappa=0.5, kappa_lr=None, kappa_rl=None,
                     delay=0, steps=50000, dt=0.01):
    """단일 κ 값으로 전체 분석."""
    print("=" * 90)
    if kappa_lr is not None and kappa_rl is not None:
        print(f" 이중 뇌 분석 — κ_LR={kappa_lr}, κ_RL={kappa_rl}, delay={delay}")
    else:
        print(f" 이중 뇌 분석 — κ={kappa}, delay={delay}")
    print("=" * 90)
    print()

    _, S, _ = dual_brain_simulate(
        kappa=kappa, kappa_lr=kappa_lr, kappa_rl=kappa_rl,
        delay=delay, steps=steps, dt=dt
    )
    m = measure_all(S)

    # 좌반구 상세
    print(" ─── 좌반구 (분석적) ───")
    print(f"  파라미터: σ=10, ρ=28, β=2.67, noise=0.05")
    _print_cct_detail(m["results_L"], m["cct_L"], m["verdict_L"])

    print()
    print(" ─── 우반구 (직관적) ───")
    print(f"  파라미터: σ=12, ρ=32, β=2.2, noise=0.2")
    _print_cct_detail(m["results_R"], m["cct_R"], m["verdict_R"])

    print()
    print(" ─── 결합 시스템 (6차원 → 3차원 투영) ───")
    _print_cct_detail(m["results_combined"], m["cct_combined"], m["verdict_combined"])

    print()
    print(" ─── 뇌량 지표 ───")
    print(f"  동기화 corr(x_L, x_R) = {m['sync']:.4f}")
    print(f"  Transfer Entropy L→R  = {m['te_lr']:.4f}")
    print(f"  Transfer Entropy R→L  = {m['te_rl']:.4f}")
    print(f"  결합 엔트로피 H(L,R)  = {m['h_joint']:.4f}")
    print(f"  독립 합 H(L)+H(R)    = {m['h_sum']:.4f}")
    redundancy = max(0, m['h_sum'] - m['h_joint'])
    print(f"  중복 정보 (redundancy)= {redundancy:.4f}")
    print(f"  좌우 비대칭 지수      = {m['asymmetry']:.4f}")

    verdict = kappa_verdict(m["sync"], m["te_lr"], m["te_rl"])
    print(f"\n  종합 판정: {verdict}")
    print("=" * 90)

    return m, S


def _print_cct_detail(results, total, verdict):
    """CCT 테스트 상세 출력."""
    labels = {
        "T1_Gap": "T1 Gap       ",
        "T2_Loop": "T2 Loop      ",
        "T3_Continuity": "T3 Continuity",
        "T4_Entropy": "T4 Entropy   ",
        "T5_Novelty": "T5 Novelty   ",
    }
    for key, label in labels.items():
        score, passed, detail = results[key]
        mark = "✔" if passed else ("△" if score > 0.7 else "✕")
        status = "PASS" if passed else "FAIL"
        print(f"  {label} │ {mark} {status} │ {score:.3f} │ {detail}")
    print(f"  {'─' * 56}")
    print(f"  종합: {total}/5 {verdict}")


# ─────────────────────────────────────────────
# matplotlib 플롯
# ─────────────────────────────────────────────

def plot_kappa_scan(all_results):
    """κ 스캔 결과 matplotlib 그래프 저장."""
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except ImportError:
        print("  [경고] matplotlib 없음, --plot 건너뜀")
        return None

    kappas = [r[0] for r in all_results]
    cct_L = [r[1]["cct_L"] for r in all_results]
    cct_R = [r[1]["cct_R"] for r in all_results]
    cct_C = [r[1]["cct_combined"] for r in all_results]
    syncs = [r[1]["sync"] for r in all_results]
    te_lr = [r[1]["te_lr"] for r in all_results]
    te_rl = [r[1]["te_rl"] for r in all_results]
    asyms = [r[1]["asymmetry"] for r in all_results]

    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    fig.suptitle("Dual Brain Corpus Callosum — κ Scan", fontsize=14, fontweight="bold")

    # 1. CCT vs κ
    ax = axes[0, 0]
    ax.plot(kappas, cct_L, "b-o", label="CCT Left (analytic)", markersize=4)
    ax.plot(kappas, cct_R, "r-s", label="CCT Right (intuitive)", markersize=4)
    ax.plot(kappas, cct_C, "g-^", label="CCT Combined", markersize=4)
    ax.set_xlabel("κ (corpus callosum bandwidth)")
    ax.set_ylabel("CCT Score (/5)")
    ax.set_title("CCT vs Coupling Strength")
    ax.legend(fontsize=8)
    ax.set_xscale("symlog", linthresh=0.01)
    ax.grid(True, alpha=0.3)

    # 2. 동기화 vs κ
    ax = axes[0, 1]
    ax.plot(kappas, syncs, "purple", marker="o", markersize=4)
    ax.axhline(0.5, color="red", ls="--", alpha=0.5, label="통합 임계")
    ax.set_xlabel("κ")
    ax.set_ylabel("Synchronization corr(x_L, x_R)")
    ax.set_title("Hemisphere Synchronization")
    ax.set_xscale("symlog", linthresh=0.01)
    ax.legend(fontsize=8)
    ax.grid(True, alpha=0.3)

    # 3. Transfer Entropy vs κ
    ax = axes[1, 0]
    ax.plot(kappas, te_lr, "b-o", label="TE L→R", markersize=4)
    ax.plot(kappas, te_rl, "r-s", label="TE R→L", markersize=4)
    ax.set_xlabel("κ")
    ax.set_ylabel("Transfer Entropy (bits)")
    ax.set_title("Information Flow")
    ax.set_xscale("symlog", linthresh=0.01)
    ax.legend(fontsize=8)
    ax.grid(True, alpha=0.3)

    # 4. 비대칭 vs κ
    ax = axes[1, 1]
    ax.plot(kappas, asyms, "darkorange", marker="o", markersize=4)
    ax.set_xlabel("κ")
    ax.set_ylabel("Asymmetry Index")
    ax.set_title("Left-Right Asymmetry")
    ax.set_xscale("symlog", linthresh=0.01)
    ax.grid(True, alpha=0.3)

    plt.tight_layout(rect=[0, 0, 1, 0.95])

    os.makedirs(RESULTS_DIR, exist_ok=True)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    path = os.path.join(RESULTS_DIR, f"dual_brain_kappa_scan_{ts}.png")
    fig.savefig(path, dpi=150, bbox_inches="tight")
    plt.close(fig)
    return path


def plot_split_brain(S, kappas, cut_step, steps, dt):
    """분리뇌 실험 matplotlib 그래프 저장."""
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except ImportError:
        print("  [경고] matplotlib 없음, --plot 건너뜀")
        return None

    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    fig.suptitle("Split-Brain Experiment", fontsize=14, fontweight="bold")

    t = np.arange(steps) * dt
    ds = max(1, steps // 5000)

    # 1. x_L, x_R 궤적
    ax = axes[0, 0]
    ax.plot(t[::ds], S[::ds, 0], "b-", lw=0.5, alpha=0.7, label="x_L")
    ax.plot(t[::ds], S[::ds, 3], "r-", lw=0.5, alpha=0.7, label="x_R")
    ax.axvline(cut_step * dt, color="black", ls="--", lw=2, label="절단")
    ax.set_xlabel("Time")
    ax.set_ylabel("x")
    ax.set_title("Hemisphere Trajectories")
    ax.legend(fontsize=8)

    # 2. κ 시계열
    ax = axes[0, 1]
    ax.plot(t[::ds], kappas[::ds], "green", lw=2)
    ax.set_xlabel("Time")
    ax.set_ylabel("κ")
    ax.set_title("Corpus Callosum Bandwidth")
    ax.set_ylim(-0.1, 1.0)

    # 3. 윈도우별 동기화
    ax = axes[1, 0]
    n_windows = 50
    window_size = steps // n_windows
    sync_t = []
    sync_v = []
    for w in range(n_windows):
        start = w * window_size
        end = start + window_size
        chunk = S[start:end]
        sync_t.append((start + end) / 2 * dt)
        sync_v.append(measure_sync(chunk))
    ax.plot(sync_t, sync_v, "purple", marker=".", markersize=3)
    ax.axvline(cut_step * dt, color="black", ls="--", lw=2, label="절단")
    ax.set_xlabel("Time")
    ax.set_ylabel("Synchronization")
    ax.set_title("Sync Over Time")
    ax.legend(fontsize=8)

    # 4. 윈도우별 엔트로피
    ax = axes[1, 1]
    h_L_t = []
    h_R_t = []
    for w in range(n_windows):
        start = w * window_size
        end = start + window_size
        chunk = S[start:end]
        h_L_t.append(compute_entropy(chunk[:, 0], bins=30))
        h_R_t.append(compute_entropy(chunk[:, 3], bins=30))
    ax.plot(sync_t, h_L_t, "b-", label="H(Left)")
    ax.plot(sync_t, h_R_t, "r-", label="H(Right)")
    ax.axvline(cut_step * dt, color="black", ls="--", lw=2, label="절단")
    ax.set_xlabel("Time")
    ax.set_ylabel("Entropy")
    ax.set_title("Hemisphere Entropy")
    ax.legend(fontsize=8)

    plt.tight_layout(rect=[0, 0, 1, 0.95])

    os.makedirs(RESULTS_DIR, exist_ok=True)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    path = os.path.join(RESULTS_DIR, f"dual_brain_split_{ts}.png")
    fig.savefig(path, dpi=150, bbox_inches="tight")
    plt.close(fig)
    return path


# ─────────────────────────────────────────────
# 메인
# ─────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="이중 뇌 뇌량 시뮬레이터 — Dual Brain Corpus Callosum Model",
    )
    parser.add_argument("--kappa", type=float, default=None,
                        help="특정 κ 값으로 분석 (기본: κ 스캔)")
    parser.add_argument("--split-brain", action="store_true",
                        help="실험 B: 분리뇌 (Sperry 실험)")
    parser.add_argument("--agenesis", action="store_true",
                        help="실험 C: 뇌량 무형성")
    parser.add_argument("--lateralize", type=str, choices=["left", "right"], default=None,
                        help="실험 D: 좌/우 반구 우세")
    parser.add_argument("--delay", type=int, default=0,
                        help="전달 지연 스텝 수 (기본: 0)")
    parser.add_argument("--all", action="store_true",
                        help="전체 실험 (A+B+C+D)")
    parser.add_argument("--steps", type=int, default=50000,
                        help="시뮬레이션 스텝 수 (기본: 50000)")
    parser.add_argument("--dt", type=float, default=0.01,
                        help="시간 간격 (기본: 0.01)")
    parser.add_argument("--plot", action="store_true",
                        help="matplotlib 그래프 저장")

    args = parser.parse_args()

    # 아무 옵션도 없으면 κ 스캔 실행
    run_scan = not any([args.kappa is not None, args.split_brain,
                        args.agenesis, args.lateralize, args.all])

    if args.all or run_scan:
        results = experiment_kappa_scan(steps=args.steps, dt=args.dt)
        if args.plot:
            path = plot_kappa_scan(results)
            if path:
                print(f"\n  [plot] 저장: {path}")
        print()

    if args.all or args.split_brain:
        m_before, m_after, S, kappas = experiment_split_brain(
            steps=args.steps, dt=args.dt
        )
        if args.plot:
            cut_step = args.steps // 2
            path = plot_split_brain(S, kappas, cut_step, args.steps, args.dt)
            if path:
                print(f"\n  [plot] 저장: {path}")
        print()

    if args.all or args.agenesis:
        experiment_agenesis(steps=args.steps, dt=args.dt)
        print()

    if args.all or args.lateralize == "left":
        experiment_lateralize("left", steps=args.steps, dt=args.dt)
        print()

    if args.all or args.lateralize == "right":
        experiment_lateralize("right", steps=args.steps, dt=args.dt)
        print()

    if args.kappa is not None and not args.all:
        m, S = run_single_kappa(
            kappa=args.kappa, delay=args.delay,
            steps=args.steps, dt=args.dt
        )


if __name__ == "__main__":
    main()
