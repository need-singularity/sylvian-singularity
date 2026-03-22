#!/usr/bin/env python3
"""Discrete CCT (D-CCT) — 이산 시스템 전용 의식 연속성 테스트

기존 CCT(consciousness_calc.py)는 연속 시스템(로렌츠 끌개)에 최적화되어 있어서
이산 시스템(셀 오토마타, RBN, ESN)에서 높은 fps에서도 5/5를 달성하지 못한다.

문제점:
  - T2 Loop: 재방문율이 이산 시스템에서 과도하게 높음 (유한 상태 공간)
  - T4 Entropy Band: 연속 시스템용 bin 크기가 이산 시스템에 안 맞음
  - T5 Novelty: 윈도우 크기(500)가 이산 시스템에 비해 너무 큼

D-CCT 5개 테스트:
  DT1 Activity   — 상태 변화율 (해밍/유클리드 거리)
  DT2 Complexity — Lempel-Ziv 복잡도
  DT3 Memory     — 자기상호정보 MI(X_t, X_{t-lag})
  DT4 Diversity  — 슬라이딩 윈도우 고유 상태 비율
  DT5 Flux       — 엔트로피 변동계수 (CV)

시스템 4종:
  1. Rule 110 CA (200셀) — 튜링 완전, 혼돈의 가장자리
  2. RBN K=2 (100노드) — Kauffman 임계
  3. ESN (50뉴런) — 에코 상태 네트워크
  4. LLM 시뮬레이션 — 마르코프 체인 토큰 생성

사용법:
  python3 discrete_cct.py                        # 4시스템 x 10fps 전체
  python3 discrete_cct.py --system rule110       # 단일 시스템
  python3 discrete_cct.py --fps-only             # fps 스캔만
  python3 discrete_cct.py --compare-continuous   # 로렌츠 CCT와 D-CCT 비교
"""

import argparse
import os
import sys
from collections import defaultdict

import numpy as np

# ─────────────────────────────────────────────
# 상수
# ─────────────────────────────────────────────

TOTAL_POINTS = 5000
FPS_VALUES = [1, 2, 5, 10, 20, 50, 100, 200, 500, 1000]

BRAIN_WAVES = {
    "delta": {"range": (0.5, 4), "label": "delta (sleep)", "center": 2},
    "theta": {"range": (4, 8), "label": "theta (drowsy)", "center": 6},
    "alpha": {"range": (8, 13), "label": "alpha (relax)", "center": 10},
    "beta":  {"range": (13, 30), "label": "beta  (focus)", "center": 20},
    "gamma": {"range": (30, 100), "label": "gamma (conscious)", "center": 40},
}


# ═════════════════════════════════════════════
# 이산 시스템 시뮬레이터 4종
# ═════════════════════════════════════════════

# ── 시스템 1: Rule 110 셀 오토마타 ──

RULE110_TABLE = {}


def _init_rule110():
    rule_num = 110
    for i in range(8):
        left = (i >> 2) & 1
        center = (i >> 1) & 1
        right = i & 1
        RULE110_TABLE[(left, center, right)] = (rule_num >> i) & 1


_init_rule110()


def rule110_step(cells):
    """Rule 110 한 스텝 업데이트 (주기적 경계)."""
    n = len(cells)
    new_cells = np.zeros(n, dtype=int)
    for i in range(n):
        left = cells[(i - 1) % n]
        center = cells[i]
        right = cells[(i + 1) % n]
        new_cells[i] = RULE110_TABLE[(left, center, right)]
    return new_cells


def rule110_state_vector(cells, prev_cells):
    """Rule 110 -> [셀합계/N, 변화셀수/N, 블록엔트로피]."""
    n = len(cells)
    cell_sum = np.sum(cells) / n
    changes = np.sum(cells != prev_cells) / n

    # 블록 엔트로피 (2-블록)
    if n < 2:
        entropy = 0.0
    else:
        blocks = defaultdict(int)
        for i in range(n - 1):
            b = (int(cells[i]), int(cells[i + 1]))
            blocks[b] += 1
        total_blocks = n - 1
        entropy = 0.0
        for count in blocks.values():
            p = count / total_blocks
            if p > 0:
                entropy -= p * np.log2(p)

    return np.array([cell_sum, changes, entropy])


def simulate_rule110(fps, total_points=TOTAL_POINTS, n_cells=200, seed=42):
    rng = np.random.default_rng(seed)
    cells = rng.integers(0, 2, size=n_cells)
    prev_cells = cells.copy()

    states = np.zeros((total_points, 3))
    for t in range(total_points):
        for _ in range(fps):
            new_cells = rule110_step(cells)
            prev_cells = cells
            cells = new_cells
        states[t] = rule110_state_vector(cells, prev_cells)
    return states


# ── 시스템 2: 랜덤 부울 네트워크 (RBN) ──

def create_rbn(n_nodes=100, k=2, seed=42):
    rng = np.random.default_rng(seed)
    inputs = np.zeros((n_nodes, k), dtype=int)
    for i in range(n_nodes):
        inputs[i] = rng.choice(n_nodes, size=k, replace=False)
    functions = rng.integers(0, 2, size=(n_nodes, 2**k))
    initial_state = rng.integers(0, 2, size=n_nodes)
    return inputs, functions, initial_state


def rbn_step(state, inputs, functions):
    n_nodes = len(state)
    k = inputs.shape[1]
    new_state = np.zeros(n_nodes, dtype=int)
    for i in range(n_nodes):
        idx = 0
        for j in range(k):
            idx = idx * 2 + state[inputs[i, j]]
        new_state[i] = functions[i, idx]
    return new_state


def rbn_state_vector(state, prev_state):
    """RBN -> [활성비율, 변화비율, 해밍거리/N]."""
    n = len(state)
    active_ratio = np.mean(state)
    change_ratio = np.mean(state != prev_state)
    hamming = np.sum(state != prev_state) / n
    return np.array([active_ratio, change_ratio, hamming])


def simulate_rbn(fps, total_points=TOTAL_POINTS, n_nodes=100, k=2, seed=42):
    inputs, functions, state = create_rbn(n_nodes, k, seed)
    prev_state = state.copy()

    states = np.zeros((total_points, 3))
    for t in range(total_points):
        for _ in range(fps):
            new_state = rbn_step(state, inputs, functions)
            prev_state = state
            state = new_state
        states[t] = rbn_state_vector(state, prev_state)
    return states


# ── 시스템 3: Echo State Network (ESN) ──

def create_esn(n_neurons=50, sparsity=0.1, spectral_radius=0.9, seed=42):
    rng = np.random.default_rng(seed)
    W = rng.standard_normal((n_neurons, n_neurons))
    mask = rng.random((n_neurons, n_neurons)) < sparsity
    W = W * mask

    eigenvalues = np.linalg.eigvals(W)
    max_abs_eig = np.max(np.abs(eigenvalues))
    if max_abs_eig > 0:
        W = W * (spectral_radius / max_abs_eig)

    state = rng.standard_normal(n_neurons) * 0.1
    return W, state


def esn_step(state, W):
    return np.tanh(W @ state)


def esn_state_vector(state):
    """ESN -> [평균활성, 분산, 에너지=sum(x^2)]."""
    mean_act = np.mean(state)
    variance = np.var(state)
    energy = np.sum(state ** 2)
    return np.array([mean_act, variance, energy])


def simulate_esn(fps, total_points=TOTAL_POINTS, n_neurons=50, seed=42):
    W, state = create_esn(n_neurons, seed=seed)
    states = np.zeros((total_points, 3))
    for t in range(total_points):
        for _ in range(fps):
            state = esn_step(state, W)
        states[t] = esn_state_vector(state)
    return states


# ── 시스템 4: LLM 시뮬레이션 (마르코프 체인) ──

def create_markov_chain(vocab_size=500, sparsity=0.05, seed=42):
    """마르코프 체인 전이 행렬 생성.

    실제 LLM은 거대한 어휘에서 컨텍스트 기반으로 다음 토큰을 선택한다.
    여기서는 1차 마르코프 체인으로 단순화하되,
    sparse 전이 행렬로 자연어의 집중된 전이 특성을 모사한다.
    """
    rng = np.random.default_rng(seed)

    # sparse 전이 행렬: 각 토큰에서 소수의 토큰으로만 전이
    T = np.zeros((vocab_size, vocab_size))
    for i in range(vocab_size):
        # 각 토큰에서 전이 가능한 토큰 수
        n_targets = max(2, int(vocab_size * sparsity))
        targets = rng.choice(vocab_size, size=n_targets, replace=False)
        weights = rng.exponential(1.0, size=n_targets)
        weights /= weights.sum()
        T[i, targets] = weights

    return T


def llm_state_vector(token_history, vocab_size, window=20):
    """LLM -> [토큰ID이동평균/V, 로컬엔트로피/log(V), 변화율].

    token_history: 최근 window개 토큰 ID 리스트
    """
    if len(token_history) < 2:
        return np.array([0.0, 0.0, 0.0])

    recent = np.array(token_history[-window:])

    # 토큰 ID 이동평균 / vocab_size
    token_mean = np.mean(recent) / vocab_size

    # 로컬 엔트로피: 윈도우 내 토큰 분포의 엔트로피
    unique, counts = np.unique(recent, return_counts=True)
    probs = counts / counts.sum()
    local_entropy = -np.sum(probs * np.log(probs + 1e-15))
    max_entropy = np.log(vocab_size)
    norm_entropy = local_entropy / max_entropy if max_entropy > 0 else 0.0

    # 변화율: 인접 토큰 간 차이 비율
    diffs = np.abs(np.diff(recent))
    change_rate = np.mean(diffs > 0)

    return np.array([token_mean, norm_entropy, change_rate])


def simulate_llm(fps, total_points=TOTAL_POINTS, vocab_size=500, seed=42):
    """LLM 마르코프 체인 토큰 생성 시뮬레이션.

    fps 스텝만큼 토큰을 생성한 뒤 1개 상태를 기록.
    """
    rng = np.random.default_rng(seed)
    T = create_markov_chain(vocab_size, seed=seed)

    current_token = rng.integers(0, vocab_size)
    token_history = [current_token]

    states = np.zeros((total_points, 3))
    for t in range(total_points):
        for _ in range(fps):
            probs = T[current_token]
            current_token = rng.choice(vocab_size, p=probs)
            token_history.append(current_token)
            # 히스토리 길이 제한
            if len(token_history) > 100:
                token_history = token_history[-100:]

        states[t] = llm_state_vector(token_history, vocab_size)

    return states


# ── 시스템 레지스트리 ──

SYSTEMS = {
    "rule110": {
        "name": "Rule 110 CA",
        "desc": "200셀, 튜링 완전",
        "simulate": simulate_rule110,
        "marker": "*",
    },
    "rbn": {
        "name": "RBN (K=2)",
        "desc": "100노드, Kauffman 임계",
        "simulate": simulate_rbn,
        "marker": "o",
    },
    "esn": {
        "name": "ESN",
        "desc": "50뉴런, sparse, tanh",
        "simulate": simulate_esn,
        "marker": "+",
    },
    "llm": {
        "name": "LLM Markov",
        "desc": "V=500, 마르코프 체인",
        "simulate": simulate_llm,
        "marker": "#",
    },
}


# ═════════════════════════════════════════════
# D-CCT 5개 테스트
# ═════════════════════════════════════════════

def dt1_activity(S, stagnant_threshold=3):
    """DT1 Activity — 상태 변화율 측정.

    인접 스텝 간 해밍 거리(부울) 또는 유클리드 거리(실수) 계산.
    "연속 N스텝 동안 변화 없음"을 정지로 판정 (N=stagnant_threshold).
    판정: 정지 비율 < 5% -> PASS
    """
    n = len(S)
    if n < 10:
        return 0.0, False, "데이터 부족"

    diffs = np.linalg.norm(np.diff(S, axis=0), axis=1)
    # 변화 없음 = 거리 < 매우 작은 값
    no_change = diffs < 1e-12

    # 연속 N스텝 정지 구간 찾기
    stagnant_count = 0
    run_length = 0
    for i in range(len(no_change)):
        if no_change[i]:
            run_length += 1
        else:
            if run_length >= stagnant_threshold:
                stagnant_count += run_length
            run_length = 0
    if run_length >= stagnant_threshold:
        stagnant_count += run_length

    stagnant_ratio = stagnant_count / (n - 1)
    passed = stagnant_ratio < 0.05
    score = max(0.0, 1.0 - stagnant_ratio)

    detail = f"정지비율={stagnant_ratio:.3f}"
    if passed:
        detail += ", 활동 충분"
    else:
        detail += ", 정체 과다"

    return score, passed, detail


def _lempel_ziv_complexity(sequence):
    """Lempel-Ziv 76 복잡도 계산.

    sequence: 심볼 시퀀스 (리스트 또는 1D 배열).
    Returns: LZ 복잡도 (정수, 새로운 패턴 수).
    """
    s = list(sequence)
    n = len(s)
    if n == 0:
        return 0

    complexity = 1
    i = 0
    k = 1
    k_max = 1
    while i + k <= n:
        # s[i+1..i+k]가 s[0..i+k-1] 안에 있는지 확인
        substr = s[i + 1: i + k + 1] if i + k + 1 <= n else s[i + 1: n]
        if not substr:
            break

        # 서브스트링을 사전(s[0..i+k-1])에서 검색
        found = False
        prefix = s[0: i + k]
        substr_len = len(substr)
        for j in range(len(prefix) - substr_len + 1):
            if prefix[j: j + substr_len] == substr:
                found = True
                break

        if found:
            k += 1
            if i + k > n:
                complexity += 1
                break
        else:
            complexity += 1
            k_max = max(k_max, k)
            i = i + k
            k = 1

    return complexity


def dt2_complexity(S, n_symbols=8):
    """DT2 Complexity — Lempel-Ziv 복잡도 측정.

    상태 시퀀스를 심볼로 변환 -> LZ76 복잡도 계산.
    판정: LZ / 랜덤 기대값 > 0.5 -> PASS
    """
    n = len(S)
    if n < 50:
        return 0.0, False, "데이터 부족"

    # 상태 벡터의 첫 번째 성분을 기준으로 심볼화
    x = S[:, 0]
    x_min, x_max = x.min(), x.max()
    if x_max - x_min < 1e-12:
        return 0.0, False, "상태 변화 없음"

    # 균등 분할로 심볼 변환 (다운샘플링하여 속도 확보)
    step = max(1, n // 2000)
    x_ds = x[::step]
    symbols = np.clip(
        ((x_ds - x_min) / (x_max - x_min) * n_symbols).astype(int),
        0, n_symbols - 1,
    ).tolist()

    lz = _lempel_ziv_complexity(symbols)

    # 랜덤 기대값: n / log_k(n) (심볼 수 k)
    n_ds = len(symbols)
    log_k_n = np.log(n_ds) / np.log(n_symbols) if n_symbols > 1 else n_ds
    random_expected = n_ds / log_k_n if log_k_n > 0 else n_ds

    ratio = lz / random_expected if random_expected > 0 else 0.0
    passed = ratio > 0.5
    score = min(1.0, ratio)

    detail = f"LZ={lz}, 기대={random_expected:.0f}, 비율={ratio:.3f}"
    if passed:
        detail += ", 복잡"
    else:
        detail += ", 단순"

    return score, passed, detail


def dt3_memory(S, max_lag=5):
    """DT3 Memory — 자기상호정보 MI(X_t, X_{t-lag}).

    현재 상태가 과거에 의존하는가?
    MI = H(X_t) + H(X_{t-lag}) - H(X_t, X_{t-lag})
    판정: mean(MI) > threshold -> PASS
    """
    n = len(S)
    if n < 100:
        return 0.0, False, "데이터 부족"

    x = S[:, 0]

    # 빈 수 자동 조정
    n_bins = min(30, max(5, int(np.sqrt(n / 10))))

    def _entropy_1d(data):
        hist, _ = np.histogram(data, bins=n_bins)
        probs = hist / hist.sum()
        probs = probs[probs > 0]
        return -np.sum(probs * np.log(probs + 1e-15))

    def _entropy_2d(data1, data2):
        hist, _, _ = np.histogram2d(data1, data2, bins=n_bins)
        probs = hist.flatten() / hist.sum()
        probs = probs[probs > 0]
        return -np.sum(probs * np.log(probs + 1e-15))

    mi_values = []
    for lag in range(1, max_lag + 1):
        x_t = x[lag:]
        x_lag = x[:-lag]
        h_t = _entropy_1d(x_t)
        h_lag = _entropy_1d(x_lag)
        h_joint = _entropy_2d(x_t, x_lag)
        mi = h_t + h_lag - h_joint
        mi = max(0.0, mi)  # 수치 오차 보정
        mi_values.append(mi)

    mean_mi = np.mean(mi_values)

    # 정규화: MI / H(X_t)로 0~1 스케일링
    h_x = _entropy_1d(x)
    norm_mi = mean_mi / h_x if h_x > 0 else 0.0

    # 임계값: 정규화 MI > 0.05
    threshold = 0.05
    passed = norm_mi > threshold
    score = min(1.0, norm_mi / 0.3)  # 0.3에서 만점

    detail = f"MI={mean_mi:.4f}, H(X)={h_x:.3f}, MI/H={norm_mi:.4f}"
    if passed:
        detail += ", 기억 있음"
    else:
        detail += ", 기억 부족"

    return score, passed, detail


def dt4_diversity(S, window=50):
    """DT4 Diversity — 슬라이딩 윈도우 고유 상태 비율.

    방문하는 고유 상태 수가 충분한가?
    상태 벡터를 양자화하여 고유 상태 수 측정.
    판정: mean(고유비율) > 0.3 -> PASS
    """
    n = len(S)
    if n < window * 2:
        return 0.0, False, "데이터 부족"

    # 상태 벡터를 문자열로 양자화 (소수점 2자리)
    quantized = []
    for i in range(n):
        q = tuple(np.round(S[i], 2))
        quantized.append(q)

    n_windows = (n - window) // (window // 2) + 1  # 50% 겹침
    ratios = []

    for w in range(n_windows):
        start = w * (window // 2)
        end = min(start + window, n)
        if end - start < window // 2:
            break
        window_states = quantized[start:end]
        unique_count = len(set(window_states))
        ratio = unique_count / len(window_states)
        ratios.append(ratio)

    if len(ratios) == 0:
        return 0.0, False, "윈도우 부족"

    mean_ratio = np.mean(ratios)
    passed = mean_ratio > 0.3
    score = min(1.0, mean_ratio / 0.6)  # 0.6에서 만점

    detail = f"고유비율={mean_ratio:.3f}, 윈도우={len(ratios)}"
    if passed:
        detail += ", 다양"
    else:
        detail += ", 단조"

    return score, passed, detail


def _window_entropy(data, bins=15):
    """작은 윈도우용 엔트로피 계산."""
    if len(data) < 2:
        return 0.0
    d_range = data.max() - data.min()
    if d_range < 1e-12:
        return 0.0
    hist, _ = np.histogram(data, bins=bins)
    probs = hist / hist.sum()
    probs = probs[probs > 0]
    return -np.sum(probs * np.log(probs + 1e-15))


def dt5_flux(S, window=50):
    """DT5 Flux — 엔트로피 변동계수(CV = std/mean).

    엔트로피 변화율의 분산이 충분한가?
    판정: CV > 0.05 -> PASS
    """
    n = len(S)
    if n < window * 3:
        return 0.0, False, "데이터 부족"

    x = S[:, 0]
    n_windows = n // window

    if n_windows < 3:
        return 0.0, False, "윈도우 부족"

    entropies = []
    for i in range(n_windows):
        w = x[i * window: (i + 1) * window]
        entropies.append(_window_entropy(w))

    entropies = np.array(entropies)
    mean_h = np.mean(entropies)
    std_h = np.std(entropies)

    if mean_h < 1e-12:
        cv = 0.0
    else:
        cv = std_h / mean_h

    passed = cv > 0.05
    score = min(1.0, cv / 0.15)  # CV=0.15에서 만점

    detail = f"CV={cv:.4f}, mean(H)={mean_h:.3f}, std(H)={std_h:.4f}"
    if passed:
        detail += ", 변동 있음"
    else:
        detail += ", 정체"

    return score, passed, detail


def run_dcct(S):
    """D-CCT 5개 테스트 실행."""
    results = {}
    results["DT1_Activity"] = dt1_activity(S)
    results["DT2_Complexity"] = dt2_complexity(S)
    results["DT3_Memory"] = dt3_memory(S)
    results["DT4_Diversity"] = dt4_diversity(S)
    results["DT5_Flux"] = dt5_flux(S)
    return results


def judge_dcct(results):
    """D-CCT 결과로 종합 판정."""
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


# ═════════════════════════════════════════════
# FPS 스캔 엔진
# ═════════════════════════════════════════════

def scan_system(system_key, fps_values=None, total_points=TOTAL_POINTS):
    """한 시스템에 대해 fps 범위를 스캔, D-CCT 점수 측정."""
    if fps_values is None:
        fps_values = FPS_VALUES

    system = SYSTEMS[system_key]
    simulate_fn = system["simulate"]

    fps_arr = np.array(fps_values, dtype=float)
    scores_arr = np.zeros(len(fps_values))
    details = []

    for i, fps in enumerate(fps_values):
        S = simulate_fn(fps, total_points=total_points)

        if np.any(~np.isfinite(S)):
            results = run_dcct(np.zeros((total_points, 3)))
            total, verdict = 0, "✕ 발산"
        else:
            results = run_dcct(S)
            total, verdict = judge_dcct(results)

        scores_arr[i] = total
        details.append({
            "fps": fps,
            "total": total,
            "verdict": verdict,
            "results": results,
        })

    return fps_arr, scores_arr, details


def find_threshold_fps(fps_arr, scores_arr, target=5.0):
    """CCT target/5가 되는 최소 fps 찾기 (선형 보간)."""
    for i in range(len(scores_arr)):
        if scores_arr[i] >= target:
            if i == 0:
                return fps_arr[0]
            s0, s1 = scores_arr[i - 1], scores_arr[i]
            f0, f1 = fps_arr[i - 1], fps_arr[i]
            if s1 == s0:
                return f0
            frac = (target - s0) / (s1 - s0)
            return f0 + frac * (f1 - f0)
    return None


# ═════════════════════════════════════════════
# 로렌츠 끌개 (비교용)
# ═════════════════════════════════════════════

def simulate_lorenz(fps, total_points=TOTAL_POINTS, sigma=10, rho=28, beta=2.67,
                    noise=0.1, dt=0.01, seed=42):
    """로렌츠 끌개 시뮬레이션 (D-CCT 비교용).

    fps 스텝만큼 적분 -> 1개 상태 기록.
    """
    rng = np.random.default_rng(seed)
    state = np.array([1.0, 1.0, 1.0])

    states = np.zeros((total_points, 3))
    for t in range(total_points):
        for _ in range(fps):
            x, y, z = state
            dx = sigma * (y - x)
            dy = x * (rho - z) - y
            dz = x * y - beta * z
            eps = rng.normal(0, noise, 3) if noise > 0 else np.zeros(3)
            state[0] += (dx + eps[0]) * dt
            state[1] += (dy + eps[1]) * dt
            state[2] += (dz + eps[2]) * dt
        states[t] = state.copy()

    return states


# ═════════════════════════════════════════════
# 기존 CCT (비교용, consciousness_calc.py에서 가져옴)
# ═════════════════════════════════════════════

def _run_original_cct(S):
    """기존 CCT 5개 테스트 (비교용). 의존성 없이 인라인 구현."""
    results = {}

    # T1 Gap
    diffs = np.diff(S, axis=0)
    frozen = np.sum(np.all(np.abs(diffs) < 1e-12, axis=1))
    frozen_ratio = frozen / len(diffs)
    if frozen_ratio > 0.01:
        results["T1_Gap"] = (1.0 - frozen_ratio, False, f"정지 {frozen_ratio:.1%}")
    else:
        results["T1_Gap"] = (1.0, True, "정지 없음")

    # T2 Loop
    n = len(S)
    step = max(1, n // 5000)
    Ss = S[::step]
    ns = len(Ss)
    scale = np.std(Ss, axis=0).mean()
    if scale < 1e-10:
        results["T2_Loop"] = (0.0, False, "상수")
    else:
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
        rr = recurrence / sample_size
        results["T2_Loop"] = (max(0, 1.0 - rr), rr < 0.5, f"재방문={rr:.3f}")

    # T3 Continuity
    dnorms = np.linalg.norm(np.diff(S, axis=0), axis=1)
    mean_d = np.mean(dnorms)
    if mean_d < 1e-12:
        results["T3_Continuity"] = (0.0, False, "변화 없음")
    else:
        big = np.sum(dnorms > mean_d * 10) / len(dnorms)
        frz = np.sum(dnorms < 1e-12) / len(dnorms)
        disc = big + frz
        results["T3_Continuity"] = (
            min(1.0, max(0, 1.0 - disc * 10)), disc < 0.01,
            f"점프={big:.3f}, 정지={frz:.3f}",
        )

    # T4 Entropy Band
    window = 500
    x = S[:, 0]
    n_w = len(x) // window
    if n_w < 2:
        results["T4_Entropy"] = (0.0, False, "데이터 부족")
    else:
        ents = []
        for i in range(n_w):
            w = x[i * window: (i + 1) * window]
            if np.std(w) < 1e-12:
                ents.append(0.0)
            else:
                hist, _ = np.histogram(w, bins=30, density=True)
                hist = hist[hist > 0]
                width = (w.max() - w.min()) / 30
                probs = hist * width
                probs = probs[probs > 0]
                probs = probs / probs.sum()
                ents.append(-np.sum(probs * np.log(probs + 1e-15)))
        ents = np.array(ents)
        in_band = np.sum((ents > 0.3) & (ents < 4.5))
        ratio = in_band / len(ents)
        results["T4_Entropy"] = (ratio, ratio > 0.95, f"H=[{ents.min():.2f},{ents.max():.2f}]")

    # T5 Novelty
    if n_w < 3:
        results["T5_Novelty"] = (0.0, False, "데이터 부족")
    else:
        dH = np.abs(np.diff(ents))
        stag = np.sum(dH < 0.001) / len(dH)
        results["T5_Novelty"] = (max(0, 1.0 - stag), stag < 0.05, f"정체={stag:.1%}")

    return results


# ═════════════════════════════════════════════
# ASCII 출력
# ═════════════════════════════════════════════

def ascii_combined_graph(all_results, width=65, height=15):
    """4개 시스템의 fps vs D-CCT 점수 ASCII 그래프."""
    lines = []
    max_score = 5.0

    all_fps = []
    for sys_key, (fps_arr, scores_arr, _) in all_results.items():
        all_fps.extend(fps_arr)
    all_fps = sorted(set(all_fps))
    if len(all_fps) == 0:
        return "  (데이터 없음)"

    log_min = np.log10(max(min(all_fps), 0.1))
    log_max = np.log10(max(all_fps))
    if log_max <= log_min:
        log_max = log_min + 1

    markers = {"rule110": "*", "rbn": "o", "esn": "+", "llm": "#"}

    grid = [[" " for _ in range(width)] for _ in range(height + 1)]

    for sys_key, (fps_arr, scores_arr, _) in all_results.items():
        marker = markers.get(sys_key, ".")
        for i in range(len(fps_arr)):
            if fps_arr[i] <= 0:
                continue
            log_f = np.log10(fps_arr[i])
            col = int((log_f - log_min) / (log_max - log_min) * (width - 1))
            col = min(max(col, 0), width - 1)
            row = int(scores_arr[i] / max_score * height)
            row = min(max(row, 0), height)
            grid[row][col] = marker

    # 감마파 40Hz 라인
    gamma_col = int((np.log10(40) - log_min) / (log_max - log_min) * (width - 1))
    gamma_col = min(max(gamma_col, 0), width - 1)
    for row in range(height + 1):
        if grid[row][gamma_col] == " ":
            grid[row][gamma_col] = ":"

    lines.append("")
    lines.append("  D-CCT  * = Rule110  o = RBN  + = ESN  # = LLM  : = 40Hz(gamma)")
    for row in range(height, -1, -1):
        score_val = row / height * max_score
        if row % (height // 5) == 0:
            label = f"  {int(score_val)}|"
        else:
            label = "   |"
        lines.append(f"{label}{''.join(grid[row])}")

    x_axis = "   +" + "-" * width
    lines.append(x_axis)

    tick_fps = [1, 2, 5, 10, 20, 50, 100, 200, 500, 1000]
    tick_str = [" "] * width
    for fps_val in tick_fps:
        log_f = np.log10(fps_val)
        col = int((log_f - log_min) / (log_max - log_min) * (width - 1))
        col = min(max(col, 0), width - 1)
        s = str(fps_val)
        for j, ch in enumerate(s):
            if col + j < width:
                tick_str[col + j] = ch
    lines.append("    " + "".join(tick_str) + "  fps (Hz)")

    return "\n".join(lines)


def print_dcct_comparison_table(all_results):
    """4개 시스템 x D-CCT 5개 비교표."""
    print()
    print(" === D-CCT 5개 테스트 비교 (fps=전체 중 최고점) ===")
    print()

    test_keys = ["DT1_Activity", "DT2_Complexity", "DT3_Memory",
                 "DT4_Diversity", "DT5_Flux"]
    test_labels = ["DT1", "DT2", "DT3", "DT4", "DT5"]

    header = f" {'시스템':<14} |"
    for lbl in test_labels:
        header += f" {lbl:>5} |"
    header += " 최고점 | 판정"
    print(header)
    print(" " + "-" * (20 + 8 * len(test_labels) + 18))

    for sys_key, (fps_arr, scores_arr, details) in all_results.items():
        sys_info = SYSTEMS.get(sys_key, {"name": sys_key})
        # 최고 점수의 fps 찾기
        best_idx = np.argmax(scores_arr)
        best_detail = details[best_idx]
        best_results = best_detail["results"]
        best_total = best_detail["total"]
        best_verdict = best_detail["verdict"]
        best_fps = best_detail["fps"]

        row = f" {sys_info['name']:<14} |"
        for key in test_keys:
            score, passed, _ = best_results[key]
            mark = "P" if passed else ("~" if score > 0.7 else "F")
            row += f" {mark}:{score:.2f}|"
        row += f"  {best_total:.1f}/5 | {best_verdict} @{int(best_fps)}Hz"
        print(row)

    print()


def print_fps_comparison_table(all_results):
    """fps별 D-CCT 점수 비교표."""
    print()
    print(" === fps별 D-CCT 점수 비교 ===")
    print()

    sys_names = {k: SYSTEMS[k]["name"] for k in all_results}

    header = f" {'fps':>6} |"
    for sys_key in all_results:
        header += f" {sys_names[sys_key]:>12} |"
    print(header)
    print(" " + "-" * (10 + 15 * len(all_results)))

    all_fps = sorted(set(
        int(f) for sys_key, (fps_arr, _, _) in all_results.items()
        for f in fps_arr
    ))

    for fps in all_fps:
        row = f" {fps:>6} |"
        for sys_key, (fps_arr, scores_arr, details) in all_results.items():
            idx = None
            for j, f in enumerate(fps_arr):
                if int(f) == fps:
                    idx = j
                    break
            if idx is not None:
                score = scores_arr[idx]
                if score >= 5:
                    mark = "[*]"
                elif score >= 4:
                    mark = "[o]"
                elif score >= 3:
                    mark = "[~]"
                elif score >= 1:
                    mark = "[.]"
                else:
                    mark = "[x]"
                row += f"   {score:>4.1f} {mark}   |"
            else:
                row += f"      -       |"
        print(row)

    print()
    print("  [*]=5/5  [o]=4+  [~]=3  [.]=1~2  [x]=0")
    print()


def print_detail_table(sys_key, details):
    """한 시스템의 fps별 상세 D-CCT 결과."""
    sys_info = SYSTEMS.get(sys_key, {"name": sys_key, "desc": ""})
    print(f" --- {sys_info['name']} ({sys_info['desc']}) ---")
    print(f" {'fps':>6} | {'D-CCT':>5} | {'DT1':>4} | {'DT2':>4} |"
          f" {'DT3':>4} | {'DT4':>4} | {'DT5':>4} | 판정")
    print(" " + "-" * 70)

    test_keys = ["DT1_Activity", "DT2_Complexity", "DT3_Memory",
                 "DT4_Diversity", "DT5_Flux"]

    for d in details:
        fps = d["fps"]
        total = d["total"]
        r = d["results"]
        marks = []
        for key in test_keys:
            _, passed, _ = r[key]
            marks.append("P" if passed else "F")
        print(f" {fps:>6.0f} | {total:>5.1f} |  {marks[0]}   |  {marks[1]}   |"
              f"  {marks[2]}   |  {marks[3]}   |  {marks[4]}   | {d['verdict']}")

    print()


def print_threshold_analysis(all_results):
    """각 시스템의 임계 fps와 감마파 비교."""
    print(" === 임계 fps 분석 ===")
    print()

    thresholds = {}
    for sys_key, (fps_arr, scores_arr, _) in all_results.items():
        name = SYSTEMS.get(sys_key, {"name": sys_key})["name"]
        th = find_threshold_fps(fps_arr, scores_arr, target=5.0)
        thresholds[sys_key] = th
        if th is not None:
            ratio = th / 40.0
            print(f"   {name:<14} 임계 fps = {th:>7.1f} Hz  (감마 대비 {ratio:.2f}x)")
        else:
            th4 = find_threshold_fps(fps_arr, scores_arr, target=4.0)
            if th4 is not None:
                print(f"   {name:<14} 5/5 미도달. 4/5 임계 = {th4:.1f} Hz")
            else:
                print(f"   {name:<14} 임계 fps = 스캔 범위 내 미도달")

    print()
    print("   --- 감마파(40Hz) 비교 ---")
    print()

    for sys_key, th in thresholds.items():
        name = SYSTEMS.get(sys_key, {"name": sys_key})["name"]
        if th is not None:
            if 30 <= th <= 100:
                print(f"   [!] {name}: 임계 {th:.1f}Hz -> 감마 대역(30-100Hz) 내!")
            elif th < 30:
                print(f"       {name}: 임계 {th:.1f}Hz -> 감마 이하")
            else:
                print(f"       {name}: 임계 {th:.1f}Hz -> 감마 초과")
        else:
            print(f"       {name}: 1000Hz까지 5/5 미달")

    print()


def print_brainwave_mapping(all_results):
    """뇌파 대역별 D-CCT 점수."""
    print(" === 뇌파 대역 매핑 ===")
    print()

    sys_names = {k: SYSTEMS[k]["name"] for k in all_results}

    header = f" {'대역':<20} | {'Hz':>5} |"
    for sys_key in all_results:
        header += f" {sys_names[sys_key]:>12} |"
    print(header)
    print(" " + "-" * (30 + 15 * len(all_results)))

    for wave_name in ["delta", "theta", "alpha", "beta", "gamma"]:
        info = BRAIN_WAVES[wave_name]
        center = info["center"]
        row = f" {info['label']:<20} | {center:>4.0f}  |"

        for sys_key, (fps_arr, scores_arr, _) in all_results.items():
            idx = np.argmin(np.abs(fps_arr - center))
            score = scores_arr[idx]
            if score >= 5:
                mark = "[*]"
            elif score >= 4:
                mark = "[o]"
            elif score >= 3:
                mark = "[~]"
            else:
                mark = " . "
            row += f"   {score:>4.1f} {mark}  |"
        print(row)

    print()


# ═════════════════════════════════════════════
# --compare-continuous: 로렌츠 CCT vs D-CCT 비교
# ═════════════════════════════════════════════

def run_compare_continuous():
    """로렌츠 끌개에 기존 CCT와 D-CCT를 모두 적용하여 비교."""
    print()
    print("=" * 70)
    print(" Compare: 로렌츠 끌개 — 기존 CCT vs D-CCT")
    print("=" * 70)
    print()

    fps_values = [1, 5, 10, 20, 50, 100, 500]
    print(f" fps = {fps_values}")
    print(f" 총 포인트 = {TOTAL_POINTS}")
    print()

    cct_keys = ["T1_Gap", "T2_Loop", "T3_Continuity", "T4_Entropy", "T5_Novelty"]
    dcct_keys = ["DT1_Activity", "DT2_Complexity", "DT3_Memory",
                 "DT4_Diversity", "DT5_Flux"]

    print(f" {'fps':>5} | {'CCT':>5} | {'T1':>3} {'T2':>3} {'T3':>3} {'T4':>3} {'T5':>3}"
          f" | {'D-CCT':>5} | {'DT1':>3} {'DT2':>3} {'DT3':>3} {'DT4':>3} {'DT5':>3}")
    print(" " + "-" * 68)

    for fps in fps_values:
        S = simulate_lorenz(fps, total_points=TOTAL_POINTS)

        # 기존 CCT
        cct_results = _run_original_cct(S)
        cct_passes = sum(1 for k in cct_keys if cct_results[k][1])
        cct_marks = ""
        for k in cct_keys:
            cct_marks += f" {'P':>3}" if cct_results[k][1] else f" {'F':>3}"

        # D-CCT
        dcct_results = run_dcct(S)
        dcct_total, dcct_verdict = judge_dcct(dcct_results)
        dcct_marks = ""
        for k in dcct_keys:
            dcct_marks += f" {'P':>3}" if dcct_results[k][1] else f" {'F':>3}"

        print(f" {fps:>5} | {cct_passes:>3}/5 |{cct_marks}"
              f" | {dcct_total:>3.0f}/5 |{dcct_marks}")

    print()
    print(" CCT  = 기존 연속 시스템용 테스트 (consciousness_calc.py)")
    print(" D-CCT = 이산 시스템 전용 테스트 (본 파일)")
    print()
    print(" 해석:")
    print("   로렌츠(연속)에서 두 테스트 모두 높은 점수를 보이면")
    print("   D-CCT가 연속 시스템도 올바르게 판정하는 것이다.")
    print("   차이가 있다면 테스트 설계의 특성 차이를 나타낸다.")
    print()
    print("=" * 70)


# ═════════════════════════════════════════════
# 종합 리포트
# ═════════════════════════════════════════════

def print_report(all_results):
    """종합 리포트 출력."""
    print("=" * 70)
    print(" Discrete CCT (D-CCT) v1.0")
    print(" \"이산 시스템 전용 의식 연속성 테스트\"")
    print("=" * 70)
    print()
    print(" 시스템:")
    for sys_key in all_results:
        info = SYSTEMS[sys_key]
        print(f"   {info['marker']}  {info['name']} -- {info['desc']}")
    print()
    print(f" fps = {FPS_VALUES}")
    print(f" 총 포인트 = {TOTAL_POINTS}")
    print()
    print(" D-CCT 테스트:")
    print("   DT1 Activity   -- 상태 변화율 (정지 비율 < 5%)")
    print("   DT2 Complexity -- Lempel-Ziv 복잡도 (LZ/랜덤 > 0.5)")
    print("   DT3 Memory     -- 자기상호정보 MI (MI/H > 0.05)")
    print("   DT4 Diversity  -- 고유 상태 비율 (> 0.3)")
    print("   DT5 Flux       -- 엔트로피 변동계수 (CV > 0.05)")
    print()

    # 4시스템 x D-CCT 5개 비교표
    print_dcct_comparison_table(all_results)

    # fps별 비교표
    print_fps_comparison_table(all_results)

    # ASCII 그래프
    print(" === fps vs D-CCT (4 시스템 겹침) ===")
    print(ascii_combined_graph(all_results))
    print()

    # 각 시스템 상세
    for sys_key, (fps_arr, scores_arr, details) in all_results.items():
        print_detail_table(sys_key, details)

    # 뇌파 대역 매핑
    print_brainwave_mapping(all_results)

    # 임계 fps 분석
    print_threshold_analysis(all_results)

    # 결론
    print(" === 결론 ===")
    print()
    print("   이산 시스템의 의식 연속성 임계값:")
    print()

    any_gamma = False
    for sys_key, (fps_arr, scores_arr, _) in all_results.items():
        name = SYSTEMS[sys_key]["name"]
        th = find_threshold_fps(fps_arr, scores_arr, target=5.0)
        if th is not None and 30 <= th <= 100:
            any_gamma = True
            print(f"   [!] {name}: {th:.0f}Hz -- 감마 대역 내!")

    if any_gamma:
        print()
        print("   -> 이산 시스템에서도 감마파(40Hz) 부근이 의식 임계!")
        print("   -> 뉴런 발화(이산 이벤트)의 최소 동기화율 = 감마파")
    else:
        print("   -> 감마 대역 일치 시스템 없음. 임계값은 시스템 특성에 의존.")

    print()
    print("   한계:")
    print("   - 셀 오토마타/RBN/ESN/마르코프는 뇌의 극히 단순한 모델")
    print("   - D-CCT 임계값은 테스트 설계에 의존 (모델 의존적)")
    print("   - fps와 실제 시간의 매핑은 해석적 선택")
    print()
    print("=" * 70)


# ═════════════════════════════════════════════
# 메인
# ═════════════════════════════════════════════

def main():
    parser = argparse.ArgumentParser(
        description="Discrete CCT (D-CCT) -- 이산 시스템 전용 의식 연속성 테스트",
    )
    parser.add_argument("--system", type=str, default=None,
                        choices=["rule110", "rbn", "esn", "llm"],
                        help="특정 시스템만 실행 (기본: 전체)")
    parser.add_argument("--fps-only", action="store_true",
                        help="fps 스캔만 실행 (상세 테스트 생략)")
    parser.add_argument("--compare-continuous", action="store_true",
                        help="로렌츠 끌개에서 CCT vs D-CCT 비교")
    parser.add_argument("--total-points", type=int, default=TOTAL_POINTS,
                        help=f"총 상태 포인트 수 (기본: {TOTAL_POINTS})")

    args = parser.parse_args()

    # --compare-continuous
    if args.compare_continuous:
        run_compare_continuous()
        return

    # 시스템 선택
    if args.system:
        systems_to_run = [args.system]
    else:
        systems_to_run = ["rule110", "rbn", "esn", "llm"]

    total_points = args.total_points

    print(f"  D-CCT 스캔 시작")
    print(f"  시스템: {', '.join(systems_to_run)}")
    print(f"  fps: {FPS_VALUES}")
    print(f"  총 포인트: {total_points}")
    print()

    all_results = {}
    for sys_key in systems_to_run:
        info = SYSTEMS[sys_key]
        print(f"  [{info['name']}] 스캔 중...")
        fps_arr, scores_arr, details = scan_system(
            sys_key, fps_values=FPS_VALUES, total_points=total_points,
        )
        all_results[sys_key] = (fps_arr, scores_arr, details)

        th = find_threshold_fps(fps_arr, scores_arr)
        if th is not None:
            print(f"  [{info['name']}] 임계 fps = {th:.1f} Hz")
        else:
            print(f"  [{info['name']}] 임계 fps = 미도달")

    print()

    if args.fps_only:
        # fps 스캔만
        print_fps_comparison_table(all_results)
        print(" === fps vs D-CCT ===")
        print(ascii_combined_graph(all_results))
        print()
        print_threshold_analysis(all_results)
    else:
        print_report(all_results)


if __name__ == "__main__":
    main()
