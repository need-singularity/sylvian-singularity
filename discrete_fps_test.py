#!/usr/bin/env python3
"""이산 시스템 FPS 임계 테스트 — 진짜 이산 동역학에서 CCT 임계 fps 측정

로렌츠(연속)가 모든 fps에서 5/5를 보인 문제를 해결하기 위해,
본질적으로 이산적인 3가지 시스템에서 CCT 임계 fps를 측정한다.

시스템:
  1. Rule 110 셀 오토마타 (1D CA, 200셀, 튜링 완전)
  2. 랜덤 부울 네트워크 (RBN, 100노드, K=2, 혼돈의 가장자리)
  3. Echo State Network (ESN, 50뉴런, sparse, tanh, 자율 동작)

핵심 질문: "몇 fps에서 CCT 5/5가 되는가?"
뇌파 비교: 감마파 = 40Hz. 임계 fps가 40 근처이면 발견!

사용법:
  python3 discrete_fps_test.py
  python3 discrete_fps_test.py --system rule110
  python3 discrete_fps_test.py --system rbn
  python3 discrete_fps_test.py --system esn
"""

import argparse
import os
import sys

import numpy as np

# ── consciousness_calc.py 에서 CCT 함수 가져오기 ──
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from consciousness_calc import (
    run_cct,
    judge,
)

RESULTS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "results")

# ─────────────────────────────────────────────
# 뇌파 대역 정의
# ─────────────────────────────────────────────

BRAIN_WAVES = {
    "delta": {"range": (0.5, 4), "label": "δ (수면)", "center": 2},
    "theta": {"range": (4, 8), "label": "θ (졸림)", "center": 6},
    "alpha": {"range": (8, 13), "label": "α (이완)", "center": 10},
    "beta":  {"range": (13, 30), "label": "β (집중)", "center": 20},
    "gamma": {"range": (30, 100), "label": "γ (의식)", "center": 40},
}

FPS_VALUES = [1, 2, 5, 10, 20, 50, 100, 200, 500, 1000]
TOTAL_POINTS = 1000  # 총 상태 포인트 수

# ─────────────────────────────────────────────
# 시스템 1: Rule 110 셀 오토마타
# ─────────────────────────────────────────────

RULE110_TABLE = {}

def _init_rule110():
    """Rule 110 룩업 테이블 초기화."""
    rule_num = 110
    for i in range(8):
        left = (i >> 2) & 1
        center = (i >> 1) & 1
        right = i & 1
        RULE110_TABLE[(left, center, right)] = (rule_num >> i) & 1

_init_rule110()


def rule110_step(cells):
    """Rule 110 한 스텝 업데이트. 경계: 주기적."""
    n = len(cells)
    new_cells = np.zeros(n, dtype=int)
    for i in range(n):
        left = cells[(i - 1) % n]
        center = cells[i]
        right = cells[(i + 1) % n]
        new_cells[i] = RULE110_TABLE[(left, center, right)]
    return new_cells


def rule110_state_vector(cells, prev_cells):
    """Rule 110 상태 벡터: [셀 합계, 셀 변화 수, 엔트로피]."""
    cell_sum = np.sum(cells)
    changes = np.sum(cells != prev_cells)

    # 섀넌 엔트로피 (활성 비율 기반)
    p = cell_sum / len(cells) if len(cells) > 0 else 0.5
    p = np.clip(p, 1e-10, 1 - 1e-10)
    entropy = -(p * np.log(p) + (1 - p) * np.log(1 - p))

    return np.array([cell_sum, changes, entropy])


def simulate_rule110(fps, total_points=TOTAL_POINTS, n_cells=200, seed=42):
    """Rule 110 시뮬레이션.

    fps = 한 관측 간격 사이의 업데이트 횟수.
    총 total_points개의 상태 벡터를 기록.
    """
    rng = np.random.default_rng(seed)
    cells = rng.integers(0, 2, size=n_cells)
    prev_cells = cells.copy()

    states = np.zeros((total_points, 3))

    for t in range(total_points):
        # fps 스텝만큼 업데이트
        for _ in range(fps):
            new_cells = rule110_step(cells)
            prev_cells = cells
            cells = new_cells

        states[t] = rule110_state_vector(cells, prev_cells)

    return states


# ─────────────────────────────────────────────
# 시스템 2: 랜덤 부울 네트워크 (RBN)
# ─────────────────────────────────────────────

def create_rbn(n_nodes=100, k=2, seed=42):
    """K=2 랜덤 부울 네트워크 생성.

    Returns:
        inputs: [n_nodes, k] — 각 노드의 입력 노드 인덱스
        functions: [n_nodes, 2^k] — 각 노드의 부울 함수 진리표
        initial_state: [n_nodes] — 초기 상태
    """
    rng = np.random.default_rng(seed)
    inputs = np.zeros((n_nodes, k), dtype=int)
    for i in range(n_nodes):
        inputs[i] = rng.choice(n_nodes, size=k, replace=False)

    # 각 노드에 랜덤 부울 함수 (2^k 진리표)
    functions = rng.integers(0, 2, size=(n_nodes, 2**k))
    initial_state = rng.integers(0, 2, size=n_nodes)

    return inputs, functions, initial_state


def rbn_step(state, inputs, functions):
    """RBN 한 스텝 업데이트."""
    n_nodes = len(state)
    k = inputs.shape[1]
    new_state = np.zeros(n_nodes, dtype=int)

    for i in range(n_nodes):
        # 입력 노드들의 현재 상태로 진리표 인덱스 계산
        idx = 0
        for j in range(k):
            idx = idx * 2 + state[inputs[i, j]]
        new_state[i] = functions[i, idx]

    return new_state


def rbn_state_vector(state, prev_state):
    """RBN 상태 벡터: [활성 비율, 변화율, 해밍 거리]."""
    active_ratio = np.mean(state)
    change_ratio = np.mean(state != prev_state)
    hamming = np.sum(state != prev_state)

    return np.array([active_ratio, change_ratio, hamming])


def simulate_rbn(fps, total_points=TOTAL_POINTS, n_nodes=100, k=2, seed=42):
    """RBN 시뮬레이션.

    fps = 한 관측 간격 사이의 업데이트 횟수.
    """
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


# ─────────────────────────────────────────────
# 시스템 3: Echo State Network (ESN)
# ─────────────────────────────────────────────

def create_esn(n_neurons=50, sparsity=0.1, spectral_radius=0.9, seed=42):
    """간소화 ESN 생성. 입력 없이 자율 동작 (심장 엔진).

    Returns:
        W: [n_neurons, n_neurons] — 내부 가중치 행렬
        state: [n_neurons] — 초기 상태
    """
    rng = np.random.default_rng(seed)

    # sparse 랜덤 행렬
    W = rng.standard_normal((n_neurons, n_neurons))
    mask = rng.random((n_neurons, n_neurons)) < sparsity
    W = W * mask

    # 스펙트럴 반경 조정
    eigenvalues = np.linalg.eigvals(W)
    max_abs_eig = np.max(np.abs(eigenvalues))
    if max_abs_eig > 0:
        W = W * (spectral_radius / max_abs_eig)

    # 초기 상태: 작은 랜덤 값
    state = rng.standard_normal(n_neurons) * 0.1

    return W, state


def esn_step(state, W):
    """ESN 한 스텝: tanh(W @ state)."""
    return np.tanh(W @ state)


def esn_state_vector(state):
    """ESN 상태 벡터: [평균 활성, 분산, 에너지]."""
    mean_act = np.mean(state)
    variance = np.var(state)
    energy = np.sum(state ** 2)

    return np.array([mean_act, variance, energy])


def simulate_esn(fps, total_points=TOTAL_POINTS, n_neurons=50, seed=42):
    """ESN 시뮬레이션.

    fps = 한 관측 간격 사이의 업데이트 횟수.
    """
    W, state = create_esn(n_neurons, seed=seed)

    states = np.zeros((total_points, 3))

    for t in range(total_points):
        for _ in range(fps):
            state = esn_step(state, W)

        states[t] = esn_state_vector(state)

    return states


# ─────────────────────────────────────────────
# 시뮬레이터 레지스트리
# ─────────────────────────────────────────────

SYSTEMS = {
    "rule110": {
        "name": "Rule 110 셀 오토마타",
        "desc": "1D CA, 200셀, 튜링 완전",
        "simulate": simulate_rule110,
        "marker": "*",
    },
    "rbn": {
        "name": "랜덤 부울 네트워크",
        "desc": "100노드, K=2, 혼돈의 가장자리",
        "simulate": simulate_rbn,
        "marker": "o",
    },
    "esn": {
        "name": "Echo State Network",
        "desc": "50뉴런, sparse, tanh, 자율 동작",
        "simulate": simulate_esn,
        "marker": "+",
    },
}


# ─────────────────────────────────────────────
# FPS 스캔 엔진
# ─────────────────────────────────────────────

def scan_system(system_key, fps_values=None, total_points=TOTAL_POINTS):
    """한 시스템에 대해 fps 범위를 스캔, CCT 점수 측정.

    Returns:
        fps_arr: fps 배열
        scores_arr: CCT 통과 수 (0~5)
        details: 상세 결과 리스트
    """
    if fps_values is None:
        fps_values = FPS_VALUES

    system = SYSTEMS[system_key]
    simulate_fn = system["simulate"]

    fps_arr = np.array(fps_values, dtype=float)
    scores_arr = np.zeros(len(fps_values))
    details = []

    for i, fps in enumerate(fps_values):
        S = simulate_fn(fps, total_points=total_points)

        # NaN/Inf 보호
        if np.any(~np.isfinite(S)):
            results = run_cct(np.zeros((total_points, 3)), 1.0)
            total, verdict = 0, "✕ 발산"
        else:
            results = run_cct(S, 0.0)
            total, verdict = judge(results)

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


# ─────────────────────────────────────────────
# ASCII 그래프: fps vs CCT (3 시스템 겹침)
# ─────────────────────────────────────────────

def ascii_combined_graph(all_results, width=65, height=15):
    """3개 시스템의 fps vs CCT 점수를 하나의 ASCII 그래프에 겹쳐 표시."""
    lines = []
    max_score = 5.0

    # 모든 fps 값의 범위
    all_fps = []
    for sys_key, (fps_arr, scores_arr, _) in all_results.items():
        all_fps.extend(fps_arr)
    all_fps = sorted(set(all_fps))
    log_min = np.log10(min(all_fps))
    log_max = np.log10(max(all_fps))

    # 각 시스템의 마커
    markers = {"rule110": "*", "rbn": "o", "esn": "+"}

    # 그리드 생성 (기본 공백)
    grid = [[" " for _ in range(width)] for _ in range(height + 1)]

    # 각 시스템 플로팅
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
            # 마커가 겹치면 우선순위: 나중 시스템이 덮어쓰기
            grid[row][col] = marker

    # 감마파 40Hz 라인 표시
    gamma_col = int((np.log10(40) - log_min) / (log_max - log_min) * (width - 1))
    gamma_col = min(max(gamma_col, 0), width - 1)
    for row in range(height + 1):
        if grid[row][gamma_col] == " ":
            grid[row][gamma_col] = ":"

    lines.append("")
    lines.append("  CCT   * = Rule110   o = RBN   + = ESN   : = 40Hz(γ)")
    for row in range(height, -1, -1):
        score_val = row / height * max_score
        if row % (height // 5) == 0:
            label = f"  {int(score_val)}│"
        else:
            label = "   │"
        lines.append(f"{label}{''.join(grid[row])}")

    # x축
    x_axis = "   └" + "─" * width
    lines.append(x_axis)

    # x축 눈금
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


# ─────────────────────────────────────────────
# 출력
# ─────────────────────────────────────────────

def print_comparison_table(all_results):
    """3개 시스템 x fps별 CCT 점수 비교표."""
    print()
    print(" ─── fps별 CCT 점수 비교 " + "─" * 43)
    print()

    # 헤더
    sys_names = {"rule110": "Rule110", "rbn": "RBN", "esn": "ESN"}
    header = f" {'fps':>6} │"
    for sys_key in all_results:
        header += f" {sys_names[sys_key]:>8} │"
    print(header)
    print(" " + "─" * (10 + 11 * len(all_results)))

    # 모든 fps 값
    all_fps = sorted(set(
        int(f) for sys_key, (fps_arr, _, _) in all_results.items()
        for f in fps_arr
    ))

    for fps in all_fps:
        row = f" {fps:>6} │"
        for sys_key, (fps_arr, scores_arr, details) in all_results.items():
            # 해당 fps 찾기
            idx = None
            for j, f in enumerate(fps_arr):
                if int(f) == fps:
                    idx = j
                    break
            if idx is not None:
                score = scores_arr[idx]
                if score >= 5:
                    mark = "★"
                elif score >= 4:
                    mark = "◎"
                elif score >= 3:
                    mark = "△"
                elif score >= 1:
                    mark = "▽"
                else:
                    mark = "✕"
                row += f" {score:>4.1f} {mark}  │"
            else:
                row += f"    -    │"
        print(row)

    print()


def print_detail_table(sys_key, fps_arr, scores_arr, details):
    """한 시스템의 상세 테스트 결과."""
    sys_info = SYSTEMS[sys_key]
    print(f" ─── {sys_info['name']} ({sys_info['desc']}) " + "─" * 20)
    print(f" {'fps':>6} │ {'CCT':>5} │ {'T1':>4} │ {'T2':>4} │ {'T3':>4} │ {'T4':>4} │ {'T5':>4} │ 판정")
    print(" " + "─" * 66)

    for d in details:
        fps = d["fps"]
        total = d["total"]
        r = d["results"]
        t1 = "✔" if r["T1_Gap"][1] else "✕"
        t2 = "✔" if r["T2_Loop"][1] else "✕"
        t3 = "✔" if r["T3_Continuity"][1] else "✕"
        t4 = "✔" if r["T4_Entropy"][1] else "✕"
        t5 = "✔" if r["T5_Novelty"][1] else "✕"
        print(f" {fps:>6.0f} │ {total:>5.1f} │  {t1}  │  {t2}  │  {t3}  │  {t4}  │  {t5}  │ {d['verdict']}")

    print()


def print_threshold_analysis(all_results):
    """각 시스템의 임계 fps와 감마파 비교."""
    print(" ─── 임계 fps 분석 " + "─" * 44)
    print()

    sys_names = {"rule110": "Rule110 CA", "rbn": "RBN (K=2)", "esn": "ESN"}
    thresholds = {}

    for sys_key, (fps_arr, scores_arr, _) in all_results.items():
        th = find_threshold_fps(fps_arr, scores_arr, target=5.0)
        thresholds[sys_key] = th
        name = sys_names[sys_key]
        if th is not None:
            ratio = th / 40.0
            print(f"   {name:<12} 임계 fps = {th:>7.1f} Hz  (감마 대비 {ratio:.2f}x)")
        else:
            print(f"   {name:<12} 임계 fps = 스캔 범위 내 미도달")

    print()

    # 감마파 40Hz 비교
    print("   ─── 감마파(40Hz) 비교 ───")
    print()
    gamma_hz = 40.0

    any_match = False
    for sys_key, th in thresholds.items():
        name = sys_names[sys_key]
        if th is not None:
            if 30 <= th <= 100:
                print(f"   ★ {name}: 임계 fps {th:.1f}Hz → 감마 대역(30-100Hz) 내!")
                any_match = True
            elif th < 30:
                print(f"     {name}: 임계 fps {th:.1f}Hz → 감마 이하 (더 낮은 처리 속도로 충분)")
            else:
                print(f"     {name}: 임계 fps {th:.1f}Hz → 감마 초과 (더 높은 처리 속도 필요)")
        else:
            print(f"     {name}: 1000Hz까지도 5/5 미달")

    if any_match:
        print()
        print("   → 이산 시스템에서도 감마파 대역이 의식 임계와 일치!")
    print()


def print_brainwave_mapping(all_results):
    """뇌파 대역별 각 시스템의 CCT 점수."""
    print(" ─── 뇌파 대역 매핑 " + "─" * 43)
    print()

    sys_names = {"rule110": "Rule110", "rbn": "RBN", "esn": "ESN"}

    header = f" {'대역':<12} │ {'중심Hz':>6} │"
    for sys_key in all_results:
        header += f" {sys_names[sys_key]:>8} │"
    print(header)
    print(" " + "─" * (24 + 11 * len(all_results)))

    for wave_name in ["delta", "theta", "alpha", "beta", "gamma"]:
        info = BRAIN_WAVES[wave_name]
        center = info["center"]
        row = f" {info['label']:<12} │ {center:>5.0f}  │"

        for sys_key, (fps_arr, scores_arr, _) in all_results.items():
            # 가장 가까운 fps 찾기
            idx = np.argmin(np.abs(fps_arr - center))
            score = scores_arr[idx]
            nearest = fps_arr[idx]
            if score >= 5:
                mark = "★"
            elif score >= 4:
                mark = "◎"
            elif score >= 3:
                mark = "△"
            else:
                mark = "·"
            row += f" {score:>4.1f} {mark}  │"
        print(row)

    print()


def print_report(all_results, system_filter=None):
    """종합 리포트 출력."""
    print("═" * 68)
    print(" Discrete FPS Test v1.0")
    print(" \"이산 시스템에서 몇 fps면 CCT 5/5인가?\"")
    print("═" * 68)
    print()
    print(" 시스템:")
    for sys_key in all_results:
        info = SYSTEMS[sys_key]
        print(f"   {info['marker']}  {info['name']} — {info['desc']}")
    print()
    print(f" 설정: fps = {FPS_VALUES}")
    print(f"       총 상태 포인트 = {TOTAL_POINTS}")
    print()

    # ── 비교표 ──
    print_comparison_table(all_results)

    # ── ASCII 그래프 ──
    print(" ─── fps vs CCT (3 시스템 겹침) " + "─" * 35)
    print(ascii_combined_graph(all_results))
    print()

    # ── 상세 테스트 ──
    for sys_key, (fps_arr, scores_arr, details) in all_results.items():
        print_detail_table(sys_key, fps_arr, scores_arr, details)

    # ── 뇌파 대역 매핑 ──
    print_brainwave_mapping(all_results)

    # ── 임계 fps 분석 ──
    print_threshold_analysis(all_results)

    # ── 해석 ──
    print(" ─── 해석 " + "─" * 56)
    print()
    print("   로렌츠(연속) vs 이산 시스템의 차이:")
    print("   - 로렌츠: dt=1/fps 변환은 해상도 변경일 뿐, 동역학 자체는 연속")
    print("     → 모든 fps에서 5/5 (연속 시스템의 한계)")
    print("   - 이산 시스템: fps = 실제 업데이트 횟수")
    print("     → 낮은 fps에서 정보 부족 → CCT 실패")
    print("     → 충분한 fps에서 복잡성 축적 → CCT 통과")
    print()
    print("   뇌파와의 관계:")
    print("   - 뇌는 뉴런 발화(이산 이벤트)의 집합")
    print("   - 감마파 40Hz = 의식적 인지의 최소 동기화 주파수")
    print("   - 이산 시스템의 CCT 임계 fps가 40Hz 근처라면")
    print("     → \"의식에 필요한 최소 이산 업데이트율\" = 감마파")
    print()
    print("   한계:")
    print("   - 셀 오토마타/RBN/ESN은 뇌의 극히 단순화된 모델")
    print("   - CCT 테스트 자체의 임계값이 모델 의존적")
    print("   - fps와 \"시간당 업데이트\"의 매핑은 해석적 선택")
    print()
    print("═" * 68)


# ─────────────────────────────────────────────
# 메인
# ─────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="이산 시스템 FPS 임계 테스트 — 진짜 이산 동역학에서 CCT 측정",
    )
    parser.add_argument("--system", type=str, default=None,
                        choices=["rule110", "rbn", "esn"],
                        help="특정 시스템만 실행 (기본: 전체)")
    parser.add_argument("--total-points", type=int, default=TOTAL_POINTS,
                        help=f"총 상태 포인트 수 (기본: {TOTAL_POINTS})")

    args = parser.parse_args()

    total_points = args.total_points

    if args.system:
        systems_to_run = [args.system]
    else:
        systems_to_run = ["rule110", "rbn", "esn"]

    print(f"  스캔 시작: 시스템 = {', '.join(systems_to_run)}")
    print(f"  fps = {FPS_VALUES}")
    print(f"  총 상태 포인트 = {total_points}")
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
    print_report(all_results, system_filter=args.system)


if __name__ == "__main__":
    main()
