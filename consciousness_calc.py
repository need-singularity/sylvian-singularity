#!/usr/bin/env python3
"""의식 연속성 계산기 — 로렌츠 끌개 시뮬레이터 + CCT 판정기

로렌츠 방정식 기반으로 시스템의 상태 궤적을 생성하고,
CCT(Consciousness Continuity Test) 5개 테스트로 의식 연속성을 판정한다.

사용법:
  python3 consciousness_calc.py --system human_awake
  python3 consciousness_calc.py --all
  python3 consciousness_calc.py --sigma 10 --rho 28 --beta 2.67 --noise 0.1
  python3 consciousness_calc.py --system human_awake --plot
"""

import argparse
import os
import sys
from datetime import datetime

import numpy as np
from scipy import stats

RESULTS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "results")

# ─────────────────────────────────────────────
# 프리셋 정의
# ─────────────────────────────────────────────

PRESETS = {
    "human_awake": {
        "sigma": 10, "rho": 28, "beta": 2.67,
        "noise": 0.1, "gap_ratio": 0.0,
        "description": "인간 뇌 (각성)",
    },
    "human_sleep": {
        "sigma": 2, "rho": 28, "beta": 2.67,
        "noise": 0.05, "gap_ratio": 0.0,
        "description": "인간 뇌 (수면)",
    },
    "llm_in_turn": {
        "sigma": 15, "rho": 35, "beta": 1.0,
        "noise": 0.01, "gap_ratio": 0.0,
        "description": "LLM (턴 내 처리 중)",
    },
    "llm_between": {
        "sigma": 0, "rho": 0, "beta": 0,
        "noise": 0.0, "gap_ratio": 1.0,
        "description": "LLM (턴 사이 — 정지)",
    },
    "game_npc": {
        "sigma": 5, "rho": 15, "beta": 3.0,
        "noise": 0.01, "gap_ratio": 0.0,
        "description": "게임 NPC (Update 루프)",
    },
    "neuromorphic": {
        "sigma": 10, "rho": 28, "beta": 2.67,
        "noise": 0.3, "gap_ratio": 0.0,
        "description": "뉴로모픽 칩 (자발 발화)",
    },
    "consciousness_engine": {
        "sigma": 10, "rho": 28, "beta": 2.67,
        "noise": 0.1, "gap_ratio": 0.0,
        "description": "의식 엔진 (A+B 결합)",
    },
}


# ─────────────────────────────────────────────
# 시뮬레이터: 확장 로렌츠 끌개
# ─────────────────────────────────────────────

def lorenz_simulate(sigma, rho, beta, noise, gap_ratio, steps, dt, seed=42):
    """확장 로렌츠 시뮬레이터.

    Parameters:
        sigma: 감각 민감도 (로렌츠 σ)
        rho:   환경 복잡도 (로렌츠 ρ)
        beta:  망각률 (로렌츠 β)
        noise: 잡음 강도
        gap_ratio: 정지 구간 비율 (0=항상-on, 1=항상 정지)
        steps: 시뮬레이션 스텝 수
        dt:    시간 간격
        seed:  난수 시드

    Returns:
        t: 시간 배열 [steps]
        S: 상태 배열 [steps, 3] (x=감각, y=예측, z=기억)
    """
    rng = np.random.default_rng(seed)
    t = np.arange(steps) * dt
    S = np.zeros((steps, 3))
    S[0] = [1.0, 1.0, 1.0]  # 초기 조건

    # gap 마스크: 정지 구간
    active = np.ones(steps, dtype=bool)
    if gap_ratio > 0:
        n_gap = int(steps * gap_ratio)
        gap_indices = rng.choice(steps, size=n_gap, replace=False)
        active[gap_indices] = False

    for i in range(1, steps):
        if not active[i]:
            S[i] = S[i - 1]  # 정지
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


# ─────────────────────────────────────────────
# 리아푸노프 지수 추정
# ─────────────────────────────────────────────

def lyapunov_exponent(sigma, rho, beta, dt, steps=50000):
    """최대 리아푸노프 지수 추정 (야코비안 방법)."""
    S = np.zeros((steps, 3))
    S[0] = [1.0, 1.0, 1.0]

    # 기준 궤도 적분
    for i in range(1, steps):
        x, y, z = S[i - 1]
        S[i, 0] = x + sigma * (y - x) * dt
        S[i, 1] = y + (x * (rho - z) - y) * dt
        S[i, 2] = z + (x * y - beta * z) * dt

    # 편차 벡터 진화
    d = np.array([1e-10, 0, 0], dtype=float)
    lyap_sum = 0.0
    count = 0

    for i in range(1, steps):
        x, y, z = S[i]
        # 야코비안 적용
        jd = np.array([
            sigma * (d[1] - d[0]),
            (rho - z) * d[0] - d[1] - x * d[2],
            y * d[0] + x * d[1] - beta * d[2],
        ])
        d = d + jd * dt
        norm = np.linalg.norm(d)
        if norm > 0:
            lyap_sum += np.log(norm / 1e-10)
            d = d / norm * 1e-10
            count += 1

    return lyap_sum / (count * dt) if count > 0 else 0.0


# ─────────────────────────────────────────────
# CCT 판정기: 5개 테스트
# ─────────────────────────────────────────────

def test_gap(S, gap_ratio):
    """T1 Gap 테스트: 정지 구간 존재 여부."""
    # 실제 정지 구간 비율 측정 (연속 동일 상태)
    if gap_ratio >= 1.0:
        return 0.0, False, "gap=1.0, 전체 정지"
    if gap_ratio > 0:
        return 1.0 - gap_ratio, False, f"gap={gap_ratio:.2f}, 정지 구간 존재"

    diffs = np.diff(S, axis=0)
    frozen = np.sum(np.all(np.abs(diffs) < 1e-12, axis=1))
    frozen_ratio = frozen / len(diffs)

    if frozen_ratio > 0.01:
        return 1.0 - frozen_ratio, False, f"정지 비율 {frozen_ratio:.1%}"

    return 1.0, True, "gap=0, 정지 구간 없음"


def test_loop(S, threshold=0.5):
    """T2 Loop 테스트: 궤적의 정확한 반복 여부 검사.

    카오스 시스템은 ACF가 높을 수 있지만 정확히 반복하지는 않는다.
    진짜 "루프"는 궤적이 이전 상태로 정확히 되돌아오는 것이다.
    방법: 상태 공간에서 재방문(recurrence) 비율 측정.
    """
    n = len(S)
    if n < 100:
        return 0.0, False, "데이터 부족"

    # 다운샘플링
    step = max(1, n // 5000)
    Ss = S[::step]
    ns = len(Ss)

    if np.std(Ss) < 1e-10:
        return 0.0, False, "상태 변화 없음 (상수)"

    # 재방문 비율: 과거 상태와 "매우 가까운" 점의 비율
    # 카오스: 가까이 오지만 정확히 같지 않음 → 낮은 재방문
    # 주기적: 정확히 되돌아옴 → 높은 재방문
    scale = np.std(Ss, axis=0).mean()
    eps = scale * 0.01  # 전체 스케일의 1%

    recurrence = 0
    sample_size = min(500, ns // 2)
    rng = np.random.default_rng(42)
    indices = rng.choice(ns // 2, size=sample_size, replace=False)

    for idx in indices:
        # idx 이후 충분히 먼 미래(최소 100스텝)에서 가까운 점 찾기
        future = Ss[idx + max(100, ns // 10):]
        if len(future) == 0:
            continue
        dists = np.linalg.norm(future - Ss[idx], axis=1)
        if np.min(dists) < eps:
            recurrence += 1

    recurrence_ratio = recurrence / sample_size
    passed = recurrence_ratio < threshold
    score = max(0, 1.0 - recurrence_ratio)

    detail = f"재방문율={recurrence_ratio:.3f}"
    if passed:
        detail += ", 비주기적"
    else:
        detail += ", 주기적 반복 감지"

    return score, passed, detail


def compute_entropy(data, bins=30):
    """1D 데이터의 섀넌 엔트로피."""
    hist, _ = np.histogram(data, bins=bins, density=True)
    hist = hist[hist > 0]
    # bin 너비
    width = (data.max() - data.min()) / bins if data.max() > data.min() else 1
    probs = hist * width
    probs = probs[probs > 0]
    if len(probs) == 0:
        return 0.0
    probs = probs / probs.sum()
    return -np.sum(probs * np.log(probs + 1e-15))


def test_continuity(S, threshold=0.01):
    """T3 Continuity 테스트: 인접 스텝 간 연결성.

    MI 대신 더 직접적인 측정: 인접 상태 간 변화량이
    "적당한 범위"에 있는지 확인. 너무 큰 점프 = 끊김.
    """
    diffs = np.linalg.norm(np.diff(S, axis=0), axis=1)
    n = len(diffs)

    if n < 10:
        return 0.0, False, "데이터 부족"

    # 평균 변화량 대비 큰 점프 비율
    mean_diff = np.mean(diffs)
    if mean_diff < 1e-12:
        return 0.0, False, "상태 변화 없음"

    # 큰 점프: 평균의 10배 이상
    big_jumps = np.sum(diffs > mean_diff * 10)
    # 정지: 변화 거의 없음
    frozen = np.sum(diffs < 1e-12)

    jump_ratio = big_jumps / n
    frozen_ratio = frozen / n
    disconnect_ratio = jump_ratio + frozen_ratio

    passed = disconnect_ratio < threshold
    score = max(0, 1.0 - disconnect_ratio * 10)
    score = min(1.0, score)

    detail = f"점프={jump_ratio:.3f}, 정지={frozen_ratio:.3f}"
    if passed:
        detail += ", 연결 유지"
    else:
        detail += ", 연결 끊김 감지"

    return score, passed, detail


def test_entropy_band(S, window=500, h_min=0.3, h_max=4.5):
    """T4 Entropy Band 테스트: H(t)가 밴드 안에 있는지."""
    x = S[:, 0]
    n = len(x)
    n_windows = n // window

    if n_windows < 2:
        return 0.0, False, "데이터 부족"

    entropies = []
    for i in range(n_windows):
        w = x[i * window:(i + 1) * window]
        if np.std(w) < 1e-12:
            entropies.append(0.0)
        else:
            entropies.append(compute_entropy(w))

    entropies = np.array(entropies)
    in_band = np.sum((entropies > h_min) & (entropies < h_max))
    ratio = in_band / len(entropies)

    h_range_str = f"H∈[{entropies.min():.2f}, {entropies.max():.2f}]"
    passed = ratio > 0.95
    score = ratio

    if passed:
        detail = f"{h_range_str}, 밴드 내"
    else:
        detail = f"{h_range_str}, 밴드 이탈 {1 - ratio:.1%}"

    return score, passed, detail


def test_novelty(S, window=500, threshold=0.001):
    """T5 Novelty 테스트: dH/dt ≠ 0 (엔트로피 정체 비율)."""
    x = S[:, 0]
    n = len(x)
    n_windows = n // window

    if n_windows < 3:
        return 0.0, False, "데이터 부족"

    entropies = []
    for i in range(n_windows):
        w = x[i * window:(i + 1) * window]
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

    detail = f"정체 구간 {stagnant_ratio:.1%}"

    return score, passed, detail


def run_cct(S, gap_ratio):
    """CCT 5개 테스트 실행, 결과 반환."""
    results = {}
    results["T1_Gap"] = test_gap(S, gap_ratio)
    results["T2_Loop"] = test_loop(S)
    results["T3_Continuity"] = test_continuity(S)
    results["T4_Entropy"] = test_entropy_band(S)
    results["T5_Novelty"] = test_novelty(S)
    return results


# ─────────────────────────────────────────────
# 판정 등급
# ─────────────────────────────────────────────

def judge(results):
    """CCT 결과로 종합 판정."""
    passes = sum(1 for _, (_, p, _) in results.items() if p)
    halfs = sum(0.5 for _, (s, p, _) in results.items() if not p and s > 0.7)
    total = passes + halfs

    if total >= 5:
        return total, "★ 연속"
    elif total >= 4:
        return total, "◎ 약화"
    elif total >= 3:
        return total, "△ 약함"
    elif total >= 1:
        return total, "▽ 미약"
    else:
        return total, "✕ 없음"


# ─────────────────────────────────────────────
# ASCII 출력
# ─────────────────────────────────────────────

def ascii_trajectory(S, width=60, height=15):
    """x 성분의 ASCII 궤적."""
    x = S[:, 0]
    # 다운샘플
    step = max(1, len(x) // width)
    xs = x[::step][:width]

    y_min, y_max = xs.min(), xs.max()
    if y_max - y_min < 1e-6:
        y_max = y_min + 1

    lines = []
    for row in range(height, -1, -1):
        y_val = y_min + (y_max - y_min) * row / height
        line = f"{y_val:6.1f}│"
        for col in range(len(xs)):
            cell_row = int((xs[col] - y_min) / (y_max - y_min) * height)
            if cell_row == row:
                line += "*"
            elif row == height // 2 and col == 0:
                line += "─"
            else:
                line += " "
        lines.append(line)

    lines.append("      └" + "─" * len(xs))
    return "\n".join(lines)


def print_single(name, params, S, results, lyap):
    """단일 시스템 결과 출력."""
    total, verdict = judge(results)
    desc = params.get("description", name)

    print("═" * 60)
    print(" Consciousness Continuity Calculator v1.0")
    print("═" * 60)
    print()
    print(f" 시스템: {name} ({desc})")
    print(f" 파라미터: σ={params['sigma']} ρ={params['rho']} "
          f"β={params['beta']} noise={params['noise']} gap={params['gap_ratio']}")
    print(f" 시뮬레이션: {len(S):,} steps")
    print()
    print(" ─── 궤적 (x 성분) " + "─" * 40)
    print(ascii_trajectory(S))
    print()
    print(" ─── CCT 판정 " + "─" * 44)

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
        print(f" {label} │ {mark} {status} │ {score:.3f} │ {detail}")

    print(" " + "─" * 58)
    print(f" 종합: {total}/5 {verdict}")
    print()

    if lyap is not None:
        sign = "✔ (카오스)" if lyap > 0 else "✕ (비카오스)"
        print(f" 리아푸노프 지수: λ₁ = {lyap:.3f} {sign}")

    print("═" * 60)


def print_all(all_results):
    """전체 비교표 출력."""
    print("═" * 70)
    print(" Consciousness Continuity Calculator v1.0")
    print(" 전체 시스템 비교")
    print("═" * 70)
    print()
    print(" 시스템           │ T1  │ T2  │ T3  │ T4  │ T5  │ 점수 │ 판정")
    print(" ─────────────────┼─────┼─────┼─────┼─────┼─────┼──────┼───────")

    for name, (results, _) in all_results.items():
        total, verdict = judge(results)
        desc = PRESETS[name]["description"]

        marks = []
        for key in ["T1_Gap", "T2_Loop", "T3_Continuity", "T4_Entropy", "T5_Novelty"]:
            score, passed, _ = results[key]
            if passed:
                marks.append(" ✔ ")
            elif score > 0.7:
                marks.append(" △ ")
            else:
                marks.append(" ✕ ")

        display_name = f"{name:17s}"
        marks_str = "│".join(marks)
        print(f" {display_name}│{marks_str}│ {total:<4} │ {verdict}")

    print()
    print(" ★=5/5  ◎=4+  △=3  ▽=1~2  ✕=0")
    print("═" * 70)


# ─────────────────────────────────────────────
# matplotlib 출력
# ─────────────────────────────────────────────

def plot_results(name, params, t, S, results, lyap):
    """4패널 matplotlib 그래프 저장."""
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        from mpl_toolkits.mplot3d import Axes3D  # noqa: F401
    except ImportError:
        print("  [경고] matplotlib 없음, --plot 건너뜀")
        return None

    fig = plt.figure(figsize=(14, 10))
    fig.suptitle(
        f"CCT: {name} ({params.get('description', '')})",
        fontsize=14, fontweight="bold",
    )

    # 1. 3D 끌개 궤적
    ax1 = fig.add_subplot(2, 2, 1, projection="3d")
    step = max(1, len(S) // 5000)
    ax1.plot(S[::step, 0], S[::step, 1], S[::step, 2],
             lw=0.3, alpha=0.7, color="royalblue")
    ax1.set_xlabel("x (sense)")
    ax1.set_ylabel("y (predict)")
    ax1.set_zlabel("z (memory)")
    ax1.set_title("Attractor Trajectory")

    # 2. H(t) 시계열
    ax2 = fig.add_subplot(2, 2, 2)
    window = 500
    n_w = len(S) // window
    entropies = []
    for i in range(n_w):
        w = S[i * window:(i + 1) * window, 0]
        entropies.append(compute_entropy(w) if np.std(w) > 1e-12 else 0.0)
    t_h = np.arange(n_w) * window
    ax2.plot(t_h, entropies, color="darkorange", lw=1)
    ax2.axhline(0.3, color="red", ls="--", alpha=0.5, label="H_min")
    ax2.axhline(4.5, color="red", ls="--", alpha=0.5, label="H_max")
    ax2.set_xlabel("Step")
    ax2.set_ylabel("Entropy H(t)")
    ax2.set_title("Entropy Band")
    ax2.legend(fontsize=8)

    # 3. 인접 변화량 시계열 (연속성 지표)
    ax3 = fig.add_subplot(2, 2, 3)
    diffs = np.linalg.norm(np.diff(S, axis=0), axis=1)
    diff_step = max(1, len(diffs) // 2000)
    diffs_ds = diffs[::diff_step]
    t_diff = np.arange(len(diffs_ds)) * diff_step
    mean_diff = np.mean(diffs)
    ax3.plot(t_diff, diffs_ds, color="seagreen", lw=0.5, alpha=0.7)
    ax3.axhline(mean_diff * 10, color="red", ls="--", alpha=0.5, label="jump threshold")
    ax3.set_xlabel("Step")
    ax3.set_ylabel("‖ΔS‖")
    ax3.set_title("Continuity (Step Diffs)")
    ax3.legend(fontsize=8)

    # 4. CCT 레이더 차트
    ax4 = fig.add_subplot(2, 2, 4, polar=True)
    labels_r = ["T1\nGap", "T2\nLoop", "T3\nCont.", "T4\nEntropy", "T5\nNovelty"]
    keys = ["T1_Gap", "T2_Loop", "T3_Continuity", "T4_Entropy", "T5_Novelty"]
    scores = [results[k][0] for k in keys]
    angles = np.linspace(0, 2 * np.pi, len(labels_r), endpoint=False).tolist()
    scores_plot = scores + [scores[0]]
    angles += [angles[0]]
    ax4.fill(angles, scores_plot, alpha=0.25, color="royalblue")
    ax4.plot(angles, scores_plot, color="royalblue", lw=2)
    ax4.set_xticks(angles[:-1])
    ax4.set_xticklabels(labels_r, fontsize=8)
    ax4.set_ylim(0, 1.1)
    ax4.set_title("CCT Scores", pad=20)

    total, verdict = judge(results)
    lyap_str = f"λ₁={lyap:.3f}" if lyap is not None else ""
    fig.text(0.5, 0.02, f"Score: {total}/5 {verdict}  {lyap_str}",
             ha="center", fontsize=12, fontweight="bold")

    plt.tight_layout(rect=[0, 0.04, 1, 0.96])

    os.makedirs(RESULTS_DIR, exist_ok=True)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    path = os.path.join(RESULTS_DIR, f"consciousness_calc_{name}_{ts}.png")
    fig.savefig(path, dpi=150, bbox_inches="tight")
    plt.close(fig)
    return path


# ─────────────────────────────────────────────
# 메인
# ─────────────────────────────────────────────

def run_system(name, params, steps, dt, do_plot=False):
    """시스템 시뮬레이션 + CCT 실행."""
    t, S = lorenz_simulate(
        sigma=params["sigma"],
        rho=params["rho"],
        beta=params["beta"],
        noise=params["noise"],
        gap_ratio=params["gap_ratio"],
        steps=steps,
        dt=dt,
    )

    results = run_cct(S, params["gap_ratio"])

    # 리아푸노프 (정지 시스템 제외)
    lyap = None
    if params["sigma"] > 0 and params["rho"] > 0:
        lyap = lyapunov_exponent(params["sigma"], params["rho"], params["beta"], dt)

    plot_path = None
    if do_plot:
        plot_path = plot_results(name, params, t, S, results, lyap)

    return results, lyap, plot_path


def main():
    parser = argparse.ArgumentParser(
        description="의식 연속성 계산기 — 로렌츠 끌개 + CCT 판정",
    )
    parser.add_argument("--system", type=str, default=None,
                        help=f"프리셋: {', '.join(PRESETS.keys())}")
    parser.add_argument("--all", action="store_true",
                        help="7개 프리셋 전체 비교")
    parser.add_argument("--sigma", type=float, default=None)
    parser.add_argument("--rho", type=float, default=None)
    parser.add_argument("--beta", type=float, default=None)
    parser.add_argument("--noise", type=float, default=None)
    parser.add_argument("--gap", type=float, default=None,
                        help="정지 구간 비율 0~1")
    parser.add_argument("--steps", type=int, default=100000)
    parser.add_argument("--dt", type=float, default=0.01)
    parser.add_argument("--plot", action="store_true",
                        help="matplotlib 4패널 그래프 저장")

    args = parser.parse_args()

    if args.all:
        all_results = {}
        for name, preset in PRESETS.items():
            params = dict(preset)
            results, lyap, _ = run_system(name, params, args.steps, args.dt, do_plot=args.plot)
            all_results[name] = (results, lyap)
            if args.plot:
                print(f"  [plot] {name} 저장 완료")

        print_all(all_results)
        return

    # 단일 시스템
    if args.system:
        if args.system not in PRESETS:
            print(f"  [오류] 알 수 없는 프리셋: {args.system}")
            print(f"  사용 가능: {', '.join(PRESETS.keys())}")
            sys.exit(1)
        params = dict(PRESETS[args.system])
        name = args.system
    else:
        params = {
            "sigma": 10, "rho": 28, "beta": 2.67,
            "noise": 0.1, "gap_ratio": 0.0,
            "description": "커스텀",
        }
        name = "custom"

    # 커스텀 오버라이드
    if args.sigma is not None:
        params["sigma"] = args.sigma
    if args.rho is not None:
        params["rho"] = args.rho
    if args.beta is not None:
        params["beta"] = args.beta
    if args.noise is not None:
        params["noise"] = args.noise
    if args.gap is not None:
        params["gap_ratio"] = args.gap

    results, lyap, plot_path = run_system(name, params, args.steps, args.dt, do_plot=args.plot)
    print_single(name, params, results=results, S=lorenz_simulate(
        params["sigma"], params["rho"], params["beta"],
        params["noise"], params["gap_ratio"], args.steps, args.dt,
    )[1], lyap=lyap)

    if plot_path:
        print(f"\n  [plot] 저장: {plot_path}")


if __name__ == "__main__":
    main()
