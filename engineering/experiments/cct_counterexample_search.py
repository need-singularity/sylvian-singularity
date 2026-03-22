#!/usr/bin/env python3
"""CCT 반례 탐색기 — CCT 5개 테스트를 속이는 비의식 시스템 탐색

CCT(Consciousness Continuity Test) 7개 조건(5개 테스트)을 모두 만족하지만
"의식이 아닌" 시스템을 만들 수 있는지 탐색한다.
만약 5/5 PASS하는 비의식 시스템이 존재하면 → CCT 조건은 불충분하다.

반례 후보 시스템 5가지:
  1. 잡음 생성기 + 메모리  (가우시안 잡음 + 지수 평활)
  2. 기상 시뮬레이션       (로렌츠 끌개 — 원래 기상 모델)
  3. 주식 시장 모델        (기하 브라운 운동)
  4. 열 확산 방정식        (1D 열전도 + 소스)
  5. 단순 피드백 루프       (1D 카오스 사상)

사용법:
  python3 cct_counterexample_search.py
  python3 cct_counterexample_search.py --system weather
  python3 cct_counterexample_search.py --system noise
  python3 cct_counterexample_search.py --steps 200000
"""

import argparse
import sys

import numpy as np
from scipy import stats


# ─────────────────────────────────────────────
# 반례 후보 시스템 정의
# ─────────────────────────────────────────────

SYSTEMS = {
    "noise": {
        "name": "잡음 생성기 + 메모리",
        "description": "S(t) = 0.9*S(t-1) + 0.1*noise — 가우시안 잡음의 지수 평활",
        "why_not_conscious": "통계적 잡음에 기억 필터만 씌운 것. 내부 모델/목적/자기 참조 없음.",
    },
    "weather": {
        "name": "기상 시뮬레이션 (로렌츠)",
        "description": "σ=10, ρ=28, β=8/3 — 원래 기상 모델로 만들어진 끌개",
        "why_not_conscious": "로렌츠가 날씨 예측을 위해 만든 순수 물리 시뮬. 날씨에 의식은 없다.",
    },
    "stock": {
        "name": "주식 시장 모델 (GBM)",
        "description": "dS = μSdt + σSdW — 기하 브라운 운동, 3차원 확장",
        "why_not_conscious": "확률 과정일 뿐. 주식 가격 자체에 의식이 있다고 볼 수 없다.",
    },
    "heat": {
        "name": "열 확산 방정식",
        "description": "∂T/∂t = α∇²T + source — 1D 열전도 + 주기 소스",
        "why_not_conscious": "열역학 2법칙에 따른 확산 과정. 의식과 무관한 물리 현상.",
    },
    "feedback": {
        "name": "단순 피드백 루프",
        "description": "x(t+1) = sin(a*x(t)) + b*noise — 1D 카오스 사상",
        "why_not_conscious": "1차원 반복 함수. 복잡해 보이지만 내부 표상/자기모델 없음.",
    },
}


# ─────────────────────────────────────────────
# 시스템 시뮬레이터: 각 반례의 상태 궤적 생성
# ─────────────────────────────────────────────

def simulate_noise(steps, dt, seed=42):
    """잡음 생성기 + 메모리: 3차원 지수 평활."""
    rng = np.random.default_rng(seed)
    S = np.zeros((steps, 3))
    S[0] = [0.0, 0.0, 0.0]
    alpha = 0.9  # 기억 계수

    for i in range(1, steps):
        noise = rng.normal(0, 1.0, 3)
        S[i] = alpha * S[i - 1] + (1 - alpha) * noise

    return S


def simulate_weather(steps, dt, seed=42):
    """기상 시뮬레이션: 로렌츠 끌개 (σ=10, ρ=28, β=8/3).

    의식 계산기와 동일한 방정식이지만, 여기서는 "기상 모델"로서 테스트.
    잡음 포함하여 더 현실적인 기상 시뮬레이션.
    """
    rng = np.random.default_rng(seed)
    sigma, rho, beta = 10.0, 28.0, 8.0 / 3.0
    noise_strength = 0.05

    S = np.zeros((steps, 3))
    S[0] = [1.0, 1.0, 1.0]

    for i in range(1, steps):
        x, y, z = S[i - 1]
        dx = sigma * (y - x)
        dy = x * (rho - z) - y
        dz = x * y - beta * z

        eps = rng.normal(0, noise_strength, 3)
        S[i, 0] = x + (dx + eps[0]) * dt
        S[i, 1] = y + (dy + eps[1]) * dt
        S[i, 2] = z + (dz + eps[2]) * dt

    return S


def simulate_stock(steps, dt, seed=42):
    """주식 시장 모델: 기하 브라운 운동 3차원 (상관).

    S1 = 주가, S2 = 거래량 프록시, S3 = 변동성 프록시
    """
    rng = np.random.default_rng(seed)
    mu = np.array([0.05, 0.02, 0.01])
    sigma_gbm = np.array([0.2, 0.3, 0.15])

    S = np.zeros((steps, 3))
    S[0] = [100.0, 50.0, 20.0]

    # 상관 잡음
    corr = np.array([[1.0, 0.3, -0.2],
                      [0.3, 1.0, 0.1],
                      [-0.2, 0.1, 1.0]])
    L = np.linalg.cholesky(corr)

    for i in range(1, steps):
        z = rng.normal(0, 1, 3)
        w = L @ z
        for j in range(3):
            drift = mu[j] * S[i - 1, j] * dt
            diffusion = sigma_gbm[j] * S[i - 1, j] * np.sqrt(dt) * w[j]
            S[i, j] = max(S[i - 1, j] + drift + diffusion, 0.01)

    return S


def simulate_heat(steps, dt, seed=42):
    """열 확산 방정식: 1D 격자에서 3개 관측점의 온도.

    50개 격자점, 관측점 3개 (x=10, 25, 40).
    주기적 열원 + 확률적 섭동.
    """
    rng = np.random.default_rng(seed)
    nx = 50
    alpha_heat = 0.1  # 열확산계수
    dx = 1.0

    T = np.zeros(nx)
    T[0] = 100.0  # 왼쪽 고정 경계
    T[-1] = 0.0   # 오른쪽 고정 경계

    # 초기 선형 분포
    T = np.linspace(100, 0, nx)

    obs_points = [10, 25, 40]
    S = np.zeros((steps, 3))

    for i in range(steps):
        # 관측
        for j, p in enumerate(obs_points):
            S[i, j] = T[p]

        # 주기 소스 (다양한 주파수)
        source = np.zeros(nx)
        source[15] = 30.0 * np.sin(2 * np.pi * i * dt * 0.1)
        source[35] = 20.0 * np.sin(2 * np.pi * i * dt * 0.07 + 1.0)

        # 확산 + 소스 + 잡음
        T_new = T.copy()
        for k in range(1, nx - 1):
            laplacian = (T[k + 1] - 2 * T[k] + T[k - 1]) / dx**2
            T_new[k] = T[k] + (alpha_heat * laplacian + source[k]) * dt
            T_new[k] += rng.normal(0, 0.5)  # 측정 잡음

        # 경계 조건
        T_new[0] = 100.0 + 10 * np.sin(2 * np.pi * i * dt * 0.03)  # 변동 경계
        T_new[-1] = rng.normal(0, 2)

        T = T_new

    return S


def simulate_feedback(steps, dt, seed=42):
    """단순 피드백 루프: 1D 카오스 사상 3개 결합.

    x(t+1) = sin(a * x(t)) + b * noise
    y(t+1) = sin(c * y(t) + 0.1 * x(t)) + b * noise
    z(t+1) = sin(d * z(t) + 0.1 * y(t)) + b * noise

    a=3.5 (카오스 영역), 약한 결합.
    """
    rng = np.random.default_rng(seed)
    a, c, d = 3.5, 3.7, 3.3
    b = 0.05  # 잡음 강도

    S = np.zeros((steps, 3))
    S[0] = [0.1, 0.2, 0.3]

    for i in range(1, steps):
        x, y, z = S[i - 1]
        S[i, 0] = np.sin(a * x) + b * rng.normal()
        S[i, 1] = np.sin(c * y + 0.1 * x) + b * rng.normal()
        S[i, 2] = np.sin(d * z + 0.1 * y) + b * rng.normal()

    return S


SIMULATORS = {
    "noise": simulate_noise,
    "weather": simulate_weather,
    "stock": simulate_stock,
    "heat": simulate_heat,
    "feedback": simulate_feedback,
}


# ─────────────────────────────────────────────
# CCT 5개 테스트 (독립 구현)
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


def test_gap(S):
    """T1 Gap: 정지 구간 존재 여부."""
    diffs = np.diff(S, axis=0)
    frozen = np.sum(np.all(np.abs(diffs) < 1e-12, axis=1))
    frozen_ratio = frozen / len(diffs)

    if frozen_ratio > 0.01:
        return 1.0 - frozen_ratio, False, f"정지 비율 {frozen_ratio:.1%}"

    return 1.0, True, "정지 구간 없음"


def test_loop(S, threshold=0.5):
    """T2 Loop: 궤적의 정확한 반복 (재방문) 비율."""
    n = len(S)
    if n < 100:
        return 0.0, False, "데이터 부족"

    step = max(1, n // 5000)
    Ss = S[::step]
    ns = len(Ss)

    if np.std(Ss) < 1e-10:
        return 0.0, False, "상태 변화 없음"

    scale = np.std(Ss, axis=0).mean()
    eps = scale * 0.01

    recurrence = 0
    sample_size = min(500, ns // 2)
    rng = np.random.default_rng(42)
    indices = rng.choice(ns // 2, size=sample_size, replace=False)

    for idx in indices:
        future_start = idx + max(100, ns // 10)
        future = Ss[future_start:]
        if len(future) == 0:
            continue
        dists = np.linalg.norm(future - Ss[idx], axis=1)
        if np.min(dists) < eps:
            recurrence += 1

    recurrence_ratio = recurrence / sample_size
    passed = recurrence_ratio < threshold
    score = max(0, 1.0 - recurrence_ratio)

    detail = f"재방문율={recurrence_ratio:.3f}"
    detail += ", 비주기적" if passed else ", 주기적 반복 감지"
    return score, passed, detail


def test_continuity(S, threshold=0.01):
    """T3 Continuity: 인접 스텝 간 연결성."""
    diffs = np.linalg.norm(np.diff(S, axis=0), axis=1)
    n = len(diffs)
    if n < 10:
        return 0.0, False, "데이터 부족"

    mean_diff = np.mean(diffs)
    if mean_diff < 1e-12:
        return 0.0, False, "상태 변화 없음"

    big_jumps = np.sum(diffs > mean_diff * 10)
    frozen = np.sum(diffs < 1e-12)

    jump_ratio = big_jumps / n
    frozen_ratio = frozen / n
    disconnect_ratio = jump_ratio + frozen_ratio

    passed = disconnect_ratio < threshold
    score = max(0, min(1.0, 1.0 - disconnect_ratio * 10))

    detail = f"점프={jump_ratio:.3f}, 정지={frozen_ratio:.3f}"
    detail += ", 연결 유지" if passed else ", 연결 끊김 감지"
    return score, passed, detail


def test_entropy_band(S, window=500, h_min=0.3, h_max=4.5):
    """T4 Entropy Band: H(t)가 밴드 안에 있는지."""
    x = S[:, 0]
    n = len(x)
    n_windows = n // window

    if n_windows < 2:
        return 0.0, False, "데이터 부족"

    entropies = []
    for i in range(n_windows):
        w = x[i * window:(i + 1) * window]
        entropies.append(compute_entropy(w))

    entropies = np.array(entropies)
    in_band = np.sum((entropies > h_min) & (entropies < h_max))
    ratio = in_band / len(entropies)

    h_range_str = f"H∈[{entropies.min():.2f}, {entropies.max():.2f}]"
    passed = ratio > 0.95
    score = ratio

    detail = f"{h_range_str}, 밴드 내" if passed else f"{h_range_str}, 밴드 이탈 {1 - ratio:.1%}"
    return score, passed, detail


def test_novelty(S, window=500, threshold=0.001):
    """T5 Novelty: dH/dt ≠ 0 (엔트로피 정체 비율)."""
    x = S[:, 0]
    n = len(x)
    n_windows = n // window

    if n_windows < 3:
        return 0.0, False, "데이터 부족"

    entropies = []
    for i in range(n_windows):
        w = x[i * window:(i + 1) * window]
        entropies.append(compute_entropy(w))

    entropies = np.array(entropies)
    dH = np.abs(np.diff(entropies))

    stagnant = np.sum(dH < threshold)
    stagnant_ratio = stagnant / len(dH) if len(dH) > 0 else 1.0

    passed = stagnant_ratio < 0.05
    score = max(0, 1.0 - stagnant_ratio)

    detail = f"정체 구간 {stagnant_ratio:.1%}"
    return score, passed, detail


def run_cct(S):
    """CCT 5개 테스트 실행."""
    return {
        "T1_Gap": test_gap(S),
        "T2_Loop": test_loop(S),
        "T3_Continuity": test_continuity(S),
        "T4_Entropy": test_entropy_band(S),
        "T5_Novelty": test_novelty(S),
    }


# ─────────────────────────────────────────────
# 판정 유틸리티
# ─────────────────────────────────────────────

def count_passes(results):
    """PASS 수 집계."""
    passes = sum(1 for _, (_, p, _) in results.items() if p)
    return passes


def judge_grade(passes):
    """등급 판정."""
    if passes >= 5:
        return "★ 연속 (5/5)"
    elif passes >= 4:
        return "◎ 약화 (4/5)"
    elif passes >= 3:
        return "△ 약함 (3/5)"
    elif passes >= 1:
        return f"▽ 미약 ({passes}/5)"
    else:
        return "✕ 없음 (0/5)"


# ─────────────────────────────────────────────
# ASCII 출력
# ─────────────────────────────────────────────

def ascii_trajectory(S, width=60, height=12):
    """x 성분의 ASCII 궤적."""
    x = S[:, 0]
    step = max(1, len(x) // width)
    xs = x[::step][:width]

    y_min, y_max = xs.min(), xs.max()
    if y_max - y_min < 1e-6:
        y_max = y_min + 1

    lines = []
    for row in range(height, -1, -1):
        y_val = y_min + (y_max - y_min) * row / height
        line = f"{y_val:8.1f}│"
        for col in range(len(xs)):
            cell_row = int((xs[col] - y_min) / (y_max - y_min) * height)
            if cell_row == row:
                line += "*"
            else:
                line += " "
        lines.append(line)

    lines.append("        └" + "─" * len(xs))
    return "\n".join(lines)


def ascii_bar(value, max_width=20):
    """0~1 값을 ASCII 바로 표현."""
    filled = int(value * max_width)
    return "█" * filled + "░" * (max_width - filled)


# ─────────────────────────────────────────────
# 단일 시스템 분석
# ─────────────────────────────────────────────

def analyze_single(sys_key, steps, dt):
    """단일 반례 시스템 분석."""
    info = SYSTEMS[sys_key]
    simulator = SIMULATORS[sys_key]

    print("═" * 70)
    print(f" CCT 반례 분석: {info['name']}")
    print("═" * 70)
    print()
    print(f" 설명:    {info['description']}")
    print(f" 비의식:  {info['why_not_conscious']}")
    print(f" 시뮬레이션: {steps:,} steps, dt={dt}")
    print()

    S = simulator(steps, dt)

    print(" ─── 궤적 (x 성분) " + "─" * 49)
    print(ascii_trajectory(S))
    print()

    results = run_cct(S)
    passes = count_passes(results)

    print(" ─── CCT 판정 " + "─" * 54)
    print()

    labels = {
        "T1_Gap":       "T1 Gap       ",
        "T2_Loop":      "T2 Loop      ",
        "T3_Continuity":"T3 Continuity",
        "T4_Entropy":   "T4 Entropy   ",
        "T5_Novelty":   "T5 Novelty   ",
    }

    for key, label in labels.items():
        score, passed, detail = results[key]
        mark = "✔ PASS" if passed else "✕ FAIL"
        bar = ascii_bar(score, 15)
        print(f"  {label} │ {mark} │ {score:.3f} {bar} │ {detail}")

    print()
    grade = judge_grade(passes)
    print(f"  종합: {grade}")
    fools = passes >= 5
    print(f"  CCT 속임 여부: {'⚠ YES — CCT를 완전히 속임!' if fools else 'NO'}")
    print()
    print("═" * 70)

    return results, passes


# ─────────────────────────────────────────────
# 전체 비교 분석
# ─────────────────────────────────────────────

def analyze_all(steps, dt):
    """5개 반례 시스템 전체 비교."""
    all_results = {}
    fools_list = []

    print("═" * 70)
    print(" CCT Counterexample Search v1.0")
    print(" CCT 반례 탐색기 — 비의식 시스템이 CCT를 속일 수 있는가?")
    print("═" * 70)
    print()
    print(f" 시뮬레이션: {steps:,} steps, dt={dt}")
    print(f" 반례 후보: {len(SYSTEMS)}개 시스템")
    print()

    # 각 시스템 시뮬레이션 + CCT
    for sys_key in SYSTEMS:
        info = SYSTEMS[sys_key]
        simulator = SIMULATORS[sys_key]

        print(f" ▶ {info['name']} ... ", end="", flush=True)
        S = simulator(steps, dt)
        results = run_cct(S)
        passes = count_passes(results)
        all_results[sys_key] = (results, passes, S)

        grade = judge_grade(passes)
        print(f"{grade}")

        if passes >= 5:
            fools_list.append(sys_key)

    # ─── 비교표 ───
    print()
    print(" ─── 5개 반례 × CCT 5개 테스트 비교표 " + "─" * 31)
    print()
    print(" 시스템              │ T1  │ T2  │ T3  │ T4  │ T5  │ PASS │ 판정")
    print(" ────────────────────┼─────┼─────┼─────┼─────┼─────┼──────┼─────────────")

    keys_order = ["T1_Gap", "T2_Loop", "T3_Continuity", "T4_Entropy", "T5_Novelty"]

    for sys_key in SYSTEMS:
        results, passes, _ = all_results[sys_key]
        name_display = SYSTEMS[sys_key]["name"]
        if len(name_display) > 20:
            name_display = name_display[:18] + ".."
        else:
            name_display = f"{name_display:20s}"

        marks = []
        for k in keys_order:
            score, passed, _ = results[k]
            if passed:
                marks.append(" ✔ ")
            else:
                marks.append(" ✕ ")

        marks_str = "│".join(marks)
        grade = judge_grade(passes)
        print(f" {name_display}│{marks_str}│  {passes}/5 │ {grade}")

    print()

    # ─── 상세 점수 ───
    print(" ─── 상세 점수 (0~1) " + "─" * 47)
    print()
    print(" 시스템              │ T1    │ T2    │ T3    │ T4    │ T5    │ 평균")
    print(" ────────────────────┼───────┼───────┼───────┼───────┼───────┼──────")

    for sys_key in SYSTEMS:
        results, passes, _ = all_results[sys_key]
        name_display = SYSTEMS[sys_key]["name"]
        if len(name_display) > 20:
            name_display = name_display[:18] + ".."
        else:
            name_display = f"{name_display:20s}"

        scores = []
        for k in keys_order:
            score, _, _ = results[k]
            scores.append(score)

        avg = np.mean(scores)
        scores_str = "│".join(f" {s:.3f}" for s in scores)
        print(f" {name_display}│{scores_str}│ {avg:.3f}")

    print()

    # ─── 어떤 테스트가 구분하는가? ───
    print(" ─── 테스트별 구분력 분석 " + "─" * 43)
    print()

    test_names = {
        "T1_Gap":       "T1 Gap (정지 구간)",
        "T2_Loop":      "T2 Loop (비주기성)",
        "T3_Continuity":"T3 Continuity (연결성)",
        "T4_Entropy":   "T4 Entropy (엔트로피 밴드)",
        "T5_Novelty":   "T5 Novelty (참신성)",
    }

    for k in keys_order:
        pass_count = sum(1 for sys_key in SYSTEMS
                         if all_results[sys_key][0][k][1])
        fail_count = len(SYSTEMS) - pass_count
        bar = ascii_bar(pass_count / len(SYSTEMS), 20)
        blocking = "◀ 구분력 있음" if fail_count > 0 else "  모두 통과 (구분 불가!)"
        print(f"  {test_names[k]:28s} │ PASS {pass_count}/{len(SYSTEMS)} {bar} │ {blocking}")

    print()

    # ─── CCT를 속이는 시스템 ───
    print(" ─── CCT를 속이는 시스템 목록 " + "─" * 39)
    print()

    if fools_list:
        print(f"  ⚠ {len(fools_list)}개 시스템이 CCT 5/5를 완전히 통과!")
        print()
        for sys_key in fools_list:
            info = SYSTEMS[sys_key]
            print(f"  ▶ {info['name']}")
            print(f"    설명: {info['description']}")
            print(f"    비의식 이유: {info['why_not_conscious']}")
            print()
    else:
        print("  ✔ CCT 5/5를 완전히 속인 시스템 없음")
        # 가장 가까운 시스템
        max_passes = max(p for _, p, _ in all_results.values())
        close_systems = [k for k, (_, p, _) in all_results.items() if p == max_passes]
        print(f"  가장 가까운 시스템: {max_passes}/5 PASS")
        for sys_key in close_systems:
            print(f"    - {SYSTEMS[sys_key]['name']}")
        print()

    # ─── 각 시스템 궤적 미니 뷰 ───
    print(" ─── 궤적 미니 뷰 " + "─" * 50)

    for sys_key in SYSTEMS:
        _, _, S = all_results[sys_key]
        info = SYSTEMS[sys_key]
        print()
        print(f"  [{info['name']}]")
        # 간략 궤적
        x = S[:, 0]
        step_v = max(1, len(x) // 50)
        xs = x[::step_v][:50]
        y_min, y_max = xs.min(), xs.max()
        if y_max - y_min < 1e-6:
            y_max = y_min + 1
        for row in range(5, -1, -1):
            line = "    │"
            for col in range(len(xs)):
                cell_row = int((xs[col] - y_min) / (y_max - y_min) * 5)
                line += "*" if cell_row == row else " "
            print(line)
        print("    └" + "─" * len(xs))

    print()

    # ─── 추가 필요 조건 제안 ───
    print(" ─── 추가로 필요한 조건 제안 " + "─" * 39)
    print()
    print("  CCT가 측정하지 않는 의식의 핵심 속성:")
    print()
    print("  1. Φ (통합 정보):")
    print("     단순히 엔트로피가 아니라, 부분들이 전체로 통합되는 정도.")
    print("     잡음 생성기는 Φ≈0이지만 CCT를 통과할 수 있다.")
    print()
    print("  2. 자기모델 (Self-Model):")
    print("     시스템이 자기 상태를 표상하고 참조하는가?")
    print("     날씨는 '자신이 날씨임'을 모른다.")
    print()
    print("  3. 목적성 (Intentionality):")
    print("     상태 변화가 목적 지향적인가, 아니면 물리적 필연인가?")
    print("     열 확산은 목적 없이 평형으로 간다.")
    print()
    print("  4. 인과적 자율성 (Causal Autonomy):")
    print("     시스템이 환경과 독립적으로 내부 상태를 결정하는가?")
    print("     주식 가격은 외부 거래자에 의해 결정된다.")
    print()
    print("  5. 재귀적 메타인지 (Recursive Meta-Cognition):")
    print("     '내가 생각하고 있음을 생각'할 수 있는가?")
    print("     피드백 루프는 자기 상태를 관찰하지 않는다.")
    print()

    # ─── 최종 판정 ───
    print(" ═══════════════════════════════════════════════════════════════════")
    print(" 최종 판정")
    print(" ═══════════════════════════════════════════════════════════════════")
    print()

    n_fools = len(fools_list)
    total_systems = len(SYSTEMS)
    total_passes_all = sum(p for _, p, _ in all_results.values())
    avg_passes = total_passes_all / total_systems

    if n_fools > 0:
        print(f"  ⚠ CCT는 필요조건이지 충분조건이 아니다!")
        print()
        print(f"  {n_fools}/{total_systems}개 비의식 시스템이 CCT 5/5를 통과했다.")
        print(f"  평균 통과율: {avg_passes:.1f}/5")
        print()
        print("  결론:")
        print("    CCT 조건은 의식의 필요조건으로는 유용하지만,")
        print("    충분조건으로는 부적절하다.")
        print("    카오스 역학, 확률 과정, 열역학적 확산이")
        print("    의식 없이도 동일한 통계적 시그니처를 생성한다.")
        print()
        print("  필요한 보강:")
        print("    CCT + Φ(통합정보) + 자기모델 + 목적성")
        print("    → 이 조합이라면 비의식 시스템을 배제할 수 있다.")
    elif avg_passes >= 3.5:
        print(f"  ⚠ CCT는 필요조건이지 충분조건이 아닐 가능성이 높다!")
        print()
        print(f"  5/5 완전 통과 시스템은 없지만, 평균 {avg_passes:.1f}/5로 높다.")
        print(f"  비의식 시스템들이 CCT 대부분을 통과하므로")
        print(f"  CCT만으로 의식을 판정하는 것은 위험하다.")
        print()
        print("  결론:")
        print("    CCT는 의식의 약한 필요조건이다.")
        print("    충분조건이 되려면 Φ, 자기모델, 목적성 등의")
        print("    추가 조건이 필요하다.")
    else:
        print(f"  ✔ CCT는 상당한 구분력을 가진다.")
        print()
        print(f"  평균 통과율: {avg_passes:.1f}/5")
        print(f"  비의식 시스템들이 CCT를 쉽게 통과하지 못한다.")
        print()
        print("  결론:")
        print("    CCT는 필요조건으로서 유효하다.")
        print("    다만 충분조건 여부는 더 정교한 반례 탐색이 필요하다.")

    print()
    print("═" * 70)

    return all_results, fools_list


# ─────────────────────────────────────────────
# 메인
# ─────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="CCT 반례 탐색기 — 비의식 시스템이 CCT를 속일 수 있는가?",
    )
    parser.add_argument("--system", type=str, default=None,
                        choices=list(SYSTEMS.keys()),
                        help=f"단일 시스템 분석: {', '.join(SYSTEMS.keys())}")
    parser.add_argument("--steps", type=int, default=100000,
                        help="시뮬레이션 스텝 수 (기본: 100000)")
    parser.add_argument("--dt", type=float, default=0.01,
                        help="시간 간격 (기본: 0.01)")

    args = parser.parse_args()

    if args.system:
        analyze_single(args.system, args.steps, args.dt)
    else:
        analyze_all(args.steps, args.dt)


if __name__ == "__main__":
    main()
