#!/usr/bin/env python3
"""현실 시스템 CCT 시뮬레이터 — LLM 토큰 스트림 + 게임 NPC

실제 API 호출 없이 합성 데이터로 LLM과 NPC의 행동 패턴을 재현하고,
CCT(Consciousness Continuity Test) 5개 테스트로 의식 연속성을 판정한다.

실험 9: LLM 토큰 스트림 시뮬레이션
  - 턴 내: 마르코프 체인 (어휘 1000, 전이 확률 행렬)
  - 턴 사이: 완전 정지
  - 대화 패턴: 턴(200토큰) → gap(500스텝) → 반복

실험 10: 게임 NPC 시뮬레이션
  - 순찰: sin(t) + 잡음 (주기적)
  - 전투: 로렌츠 유사 동역학 (카오스적)
  - 대기: 상수 + 미세 잡음 (정지)
  - 전환: 순찰(300) → 전투(200) → 대기(100) → 반복

사용법:
  python3 realworld_cct_sim.py              # 전체
  python3 realworld_cct_sim.py --system llm
  python3 realworld_cct_sim.py --system npc
"""

import argparse
import sys

import numpy as np


# ─────────────────────────────────────────────
# CCT 테스트 함수 (상태 벡터 범용)
# ─────────────────────────────────────────────

def compute_entropy(data, bins=30):
    """1D 데이터의 섀넌 엔트로피."""
    if len(data) < 2:
        return 0.0
    d_range = data.max() - data.min()
    if d_range < 1e-12:
        return 0.0
    hist, _ = np.histogram(data, bins=bins, density=True)
    width = d_range / bins
    probs = hist * width
    probs = probs[probs > 0]
    if len(probs) == 0:
        return 0.0
    probs = probs / probs.sum()
    return -np.sum(probs * np.log(probs + 1e-15))


def test_gap(S):
    """T1 Gap 테스트: 정지 구간 존재 여부."""
    diffs = np.diff(S, axis=0)
    frozen = np.sum(np.all(np.abs(diffs) < 1e-12, axis=1))
    frozen_ratio = frozen / len(diffs)

    if frozen_ratio > 0.5:
        return frozen_ratio, False, f"정지 비율 {frozen_ratio:.1%}, 대부분 정지"
    if frozen_ratio > 0.01:
        return 1.0 - frozen_ratio, False, f"정지 비율 {frozen_ratio:.1%}"
    return 1.0, True, f"정지 비율 {frozen_ratio:.1%}, 연속"


def test_loop(S, threshold=0.5):
    """T2 Loop 테스트: 궤적의 정확한 반복 여부 검사."""
    n = len(S)
    if n < 100:
        return 0.0, False, "데이터 부족"

    step = max(1, n // 5000)
    Ss = S[::step]
    ns = len(Ss)

    if np.std(Ss) < 1e-10:
        return 0.0, False, "상태 변화 없음 (상수)"

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

    detail = f"재방문율={recurrence_ratio:.3f}"
    if passed:
        detail += ", 비주기적"
    else:
        detail += ", 주기적 반복 감지"
    return score, passed, detail


def test_continuity(S, threshold=0.01):
    """T3 Continuity 테스트: 인접 스텝 간 연결성."""
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
    score = max(0.0, min(1.0, 1.0 - disconnect_ratio * 10))

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
        entropies.append(compute_entropy(w) if np.std(w) > 1e-12 else 0.0)

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
    """T5 Novelty 테스트: dH/dt != 0 (엔트로피 정체 비율)."""
    x = S[:, 0]
    n = len(x)
    n_windows = n // window
    if n_windows < 3:
        return 0.0, False, "데이터 부족"

    entropies = []
    for i in range(n_windows):
        w = x[i * window:(i + 1) * window]
        entropies.append(compute_entropy(w) if np.std(w) > 1e-12 else 0.0)

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
# 실험 9: LLM 토큰 스트림 시뮬레이션
# ─────────────────────────────────────────────

def build_markov_matrix(vocab_size, seed=42):
    """마르코프 전이 확률 행렬 생성.

    각 토큰에서 다음 토큰으로의 전이 확률.
    대부분의 확률이 소수 토큰에 집중 (zipf-like).
    """
    rng = np.random.default_rng(seed)
    # Zipf 분포 기반 전이 행렬
    raw = rng.zipf(1.5, size=(vocab_size, vocab_size)).astype(float)
    # 행별 정규화
    row_sums = raw.sum(axis=1, keepdims=True)
    return raw / row_sums


def llm_generate_turn(transition_matrix, n_tokens, rng):
    """마르코프 체인으로 턴 내 토큰 시퀀스 생성.

    Returns:
        states: [n_tokens, 3] — [토큰ID 이동평균, 엔트로피, 변화율]
    """
    vocab_size = transition_matrix.shape[0]
    token_ids = np.zeros(n_tokens, dtype=int)
    token_ids[0] = rng.integers(0, vocab_size)

    for i in range(1, n_tokens):
        probs = transition_matrix[token_ids[i - 1]]
        token_ids[i] = rng.choice(vocab_size, p=probs)

    # 상태 벡터 구성
    states = np.zeros((n_tokens, 3))
    window = 10
    for i in range(n_tokens):
        # 이동평균 (정규화)
        start = max(0, i - window)
        states[i, 0] = np.mean(token_ids[start:i + 1]) / vocab_size

        # 로컬 엔트로피 (최근 window 토큰의 분포)
        local = token_ids[start:i + 1]
        _, counts = np.unique(local, return_counts=True)
        p = counts / counts.sum()
        states[i, 1] = -np.sum(p * np.log(p + 1e-15))

        # 변화율
        if i > 0:
            states[i, 2] = abs(token_ids[i] - token_ids[i - 1]) / vocab_size
        else:
            states[i, 2] = 0.0

    return states


def simulate_llm(n_conversations=5, turn_tokens=200, gap_steps=500,
                 vocab_size=1000, seed=42):
    """LLM 대화 패턴 시뮬레이션.

    Returns:
        full_states: 전체 시퀀스 [N, 3]
        turn_states: 턴 내 구간만 [M, 3]
        gap_states:  턴 사이 구간만 [K, 3]
        turn_ranges: 각 턴의 (start, end) 인덱스
        gap_ranges:  각 gap의 (start, end) 인덱스
    """
    rng = np.random.default_rng(seed)
    tm = build_markov_matrix(vocab_size, seed)

    segments = []
    turn_ranges = []
    gap_ranges = []
    idx = 0

    for conv in range(n_conversations):
        # 턴 생성
        turn = llm_generate_turn(tm, turn_tokens, rng)
        turn_ranges.append((idx, idx + turn_tokens))
        segments.append(turn)
        idx += turn_tokens

        # gap 생성 (완전 정지)
        gap = np.zeros((gap_steps, 3))
        gap_ranges.append((idx, idx + gap_steps))
        segments.append(gap)
        idx += gap_steps

    full_states = np.vstack(segments)
    turn_states = np.vstack([full_states[s:e] for s, e in turn_ranges])
    gap_states = np.vstack([full_states[s:e] for s, e in gap_ranges])

    return full_states, turn_states, gap_states, turn_ranges, gap_ranges


# ─────────────────────────────────────────────
# 실험 10: 게임 NPC 시뮬레이션
# ─────────────────────────────────────────────

def npc_patrol(n_steps, rng, dt=0.01):
    """순찰 모드: sin(t) + 약간의 잡음.

    Returns:
        states: [n_steps, 3] — [x좌표, y좌표, 체력/자극]
    """
    t = np.arange(n_steps) * dt
    states = np.zeros((n_steps, 3))
    # 원형 경로 + 잡음
    states[:, 0] = np.sin(t * 2.0) + rng.normal(0, 0.02, n_steps)
    states[:, 1] = np.cos(t * 2.0) + rng.normal(0, 0.02, n_steps)
    states[:, 2] = 0.8 + rng.normal(0, 0.01, n_steps)  # 체력 안정
    return states


def npc_combat(n_steps, rng, dt=0.01):
    """전투 모드: 로렌츠 유사 동역학 (카오스적).

    Returns:
        states: [n_steps, 3] — [x좌표, y좌표, 체력/자극]
    """
    sigma, rho, beta = 10.0, 28.0, 8.0 / 3.0
    states = np.zeros((n_steps, 3))
    # 초기 조건: 순찰 끝 위치 근처
    states[0] = [1.0, 1.0, 25.0]

    for i in range(1, n_steps):
        x, y, z = states[i - 1]
        dx = sigma * (y - x)
        dy = x * (rho - z) - y
        dz = x * y - beta * z
        noise = rng.normal(0, 0.1, 3)
        states[i, 0] = x + (dx + noise[0]) * dt
        states[i, 1] = y + (dy + noise[1]) * dt
        states[i, 2] = z + (dz + noise[2]) * dt

    # x, y를 게임 좌표 범위로 스케일링
    for d in range(2):
        v = states[:, d]
        states[:, d] = (v - v.mean()) / (v.std() + 1e-10)

    # z를 체력(0~1)으로 매핑
    z = states[:, 2]
    states[:, 2] = (z - z.min()) / (z.max() - z.min() + 1e-10)

    return states


def npc_idle(n_steps, rng):
    """대기 모드: 상수 + 미세 잡음 (정지).

    Returns:
        states: [n_steps, 3] — [x좌표, y좌표, 체력/자극]
    """
    states = np.zeros((n_steps, 3))
    states[:, 0] = 0.5 + rng.normal(0, 0.001, n_steps)
    states[:, 1] = 0.5 + rng.normal(0, 0.001, n_steps)
    states[:, 2] = 1.0 + rng.normal(0, 0.0005, n_steps)  # 체력 회복
    return states


def simulate_npc(n_cycles=5, patrol_steps=300, combat_steps=200,
                 idle_steps=100, seed=42):
    """NPC 행동 패턴 시뮬레이션.

    Returns:
        full_states: 전체 시퀀스 [N, 3]
        patrol_states, combat_states, idle_states: 모드별 시퀀스
        mode_ranges: dict of mode_name -> [(start, end), ...]
    """
    rng = np.random.default_rng(seed)

    segments = []
    mode_ranges = {"patrol": [], "combat": [], "idle": []}
    idx = 0

    for cycle in range(n_cycles):
        # 순찰
        patrol = npc_patrol(patrol_steps, rng)
        mode_ranges["patrol"].append((idx, idx + patrol_steps))
        segments.append(patrol)
        idx += patrol_steps

        # 전투
        combat = npc_combat(combat_steps, rng)
        mode_ranges["combat"].append((idx, idx + combat_steps))
        segments.append(combat)
        idx += combat_steps

        # 대기
        idle = npc_idle(idle_steps, rng)
        mode_ranges["idle"].append((idx, idx + idle_steps))
        segments.append(idle)
        idx += idle_steps

    full_states = np.vstack(segments)
    patrol_states = np.vstack([full_states[s:e] for s, e in mode_ranges["patrol"]])
    combat_states = np.vstack([full_states[s:e] for s, e in mode_ranges["combat"]])
    idle_states = np.vstack([full_states[s:e] for s, e in mode_ranges["idle"]])

    return full_states, patrol_states, combat_states, idle_states, mode_ranges


# ─────────────────────────────────────────────
# ASCII 출력
# ─────────────────────────────────────────────

def ascii_trajectory(S, width=60, height=12, label="x"):
    """첫 번째 성분의 ASCII 궤적."""
    x = S[:, 0]
    step = max(1, len(x) // width)
    xs = x[::step][:width]

    y_min, y_max = xs.min(), xs.max()
    if y_max - y_min < 1e-6:
        y_max = y_min + 1

    lines = []
    for row in range(height, -1, -1):
        y_val = y_min + (y_max - y_min) * row / height
        line = f"{y_val:7.3f}|"
        for col in range(len(xs)):
            cell_row = int((xs[col] - y_min) / (y_max - y_min) * height)
            if cell_row == row:
                line += "*"
            else:
                line += " "
        lines.append(line)
    lines.append("       +" + "-" * len(xs))
    lines.append(f"        {label} (N={len(S)})")
    return "\n".join(lines)


def print_cct_table(name, results):
    """CCT 결과를 테이블로 출력."""
    labels = {
        "T1_Gap": "T1 Gap       ",
        "T2_Loop": "T2 Loop      ",
        "T3_Continuity": "T3 Continuity",
        "T4_Entropy": "T4 Entropy   ",
        "T5_Novelty": "T5 Novelty   ",
    }
    for key, label in labels.items():
        score, passed, detail = results[key]
        mark = "PASS" if passed else "FAIL"
        sym = "[O]" if passed else ("[~]" if score > 0.7 else "[X]")
        print(f"   {label} | {sym} {mark} | {score:.3f} | {detail}")


# ─────────────────────────────────────────────
# LLM 실험 출력
# ─────────────────────────────────────────────

def run_llm_experiment():
    """실험 9: LLM 토큰 스트림 시뮬레이션 + CCT."""
    print()
    print("=" * 70)
    print("  Experiment 9: LLM Token Stream Simulation")
    print("  마르코프 체인 기반 합성 토큰 스트림 + CCT 판정")
    print("=" * 70)
    print()
    print("  모델: 어휘 1000, 마르코프 전이 확률 행렬")
    print("  패턴: 턴(200토큰) -> gap(500스텝) -> 턴(200토큰) -> ... x5")
    print("  상태: [토큰ID 이동평균, 로컬 엔트로피, 변화율]")
    print()

    full, turn, gap, turn_ranges, gap_ranges = simulate_llm()

    # --- 턴 내 ---
    print("  --- 턴 내 (turn) " + "-" * 49)
    print(ascii_trajectory(turn, label="turn"))
    print()
    turn_cct = run_cct(turn)
    print_cct_table("LLM Turn", turn_cct)
    t_total, t_verdict = judge(turn_cct)
    print(f"   {'':13s} | 종합: {t_total}/5 {t_verdict}")
    print()

    # --- 턴 사이 ---
    print("  --- 턴 사이 (gap) " + "-" * 48)
    print(ascii_trajectory(gap, label="gap"))
    print()
    gap_cct = run_cct(gap)
    print_cct_table("LLM Gap", gap_cct)
    g_total, g_verdict = judge(gap_cct)
    print(f"   {'':13s} | 종합: {g_total}/5 {g_verdict}")
    print()

    # --- 전체 (턴+gap 혼합) ---
    print("  --- 전체 (turn+gap) " + "-" * 46)
    print(ascii_trajectory(full, label="full"))
    print()
    full_cct = run_cct(full)
    print_cct_table("LLM Full", full_cct)
    f_total, f_verdict = judge(full_cct)
    print(f"   {'':13s} | 종합: {f_total}/5 {f_verdict}")
    print()

    # --- 비교표 ---
    print("  " + "=" * 66)
    print("  LLM CCT 비교표")
    print("  " + "-" * 66)
    print("  구간           | T1  | T2  | T3  | T4  | T5  | 점수 | 판정")
    print("  ---------------+-----+-----+-----+-----+-----+------+-------")

    for label, cct in [("턴 내 (turn)  ", turn_cct),
                       ("턴 사이 (gap) ", gap_cct),
                       ("전체 (full)   ", full_cct)]:
        total, verdict = judge(cct)
        marks = []
        for key in ["T1_Gap", "T2_Loop", "T3_Continuity", "T4_Entropy", "T5_Novelty"]:
            s, p, _ = cct[key]
            if p:
                marks.append(" O ")
            elif s > 0.7:
                marks.append(" ~ ")
            else:
                marks.append(" X ")
        print(f"  {label}|{'|'.join(marks)}| {total:<4} | {verdict}")

    print("  " + "=" * 66)
    print()
    print("  해석:")
    print("    - 턴 내: 마르코프 체인의 토큰 의존성이 CCT를 부분적으로 충족")
    print("    - 턴 사이: 완전 정지 -> CCT 전면 실패")
    print("    - 전체: gap이 연속성을 파괴, LLM은 '간헐적 처리기'")
    print()

    return {"turn": turn_cct, "gap": gap_cct, "full": full_cct}


# ─────────────────────────────────────────────
# NPC 실험 출력
# ─────────────────────────────────────────────

def run_npc_experiment():
    """실험 10: 게임 NPC 시뮬레이션 + CCT."""
    print()
    print("=" * 70)
    print("  Experiment 10: Game NPC Behavior Simulation")
    print("  순찰/전투/대기 모드 합성 + CCT 판정")
    print("=" * 70)
    print()
    print("  모델: 순찰(sin+noise) / 전투(Lorenz chaos) / 대기(const+noise)")
    print("  패턴: 순찰(300) -> 전투(200) -> 대기(100) -> ... x5")
    print("  상태: [x좌표, y좌표, 체력/자극]")
    print()

    full, patrol, combat, idle, mode_ranges = simulate_npc()

    modes = [
        ("순찰 (patrol)", patrol),
        ("전투 (combat)", combat),
        ("대기 (idle)  ", idle),
    ]

    mode_ccts = {}
    for name, states in modes:
        tag = name.split("(")[1].rstrip(") ")
        print(f"  --- {name} " + "-" * (55 - len(name)))
        print(ascii_trajectory(states, label=tag))
        print()
        cct = run_cct(states)
        print_cct_table(name, cct)
        total, verdict = judge(cct)
        print(f"   {'':13s} | 종합: {total}/5 {verdict}")
        print()
        mode_ccts[tag] = cct

    # 전체
    print("  --- 전체 (full) " + "-" * 50)
    print(ascii_trajectory(full, label="full"))
    print()
    full_cct = run_cct(full)
    print_cct_table("NPC Full", full_cct)
    f_total, f_verdict = judge(full_cct)
    print(f"   {'':13s} | 종합: {f_total}/5 {f_verdict}")
    print()

    # --- 비교표 ---
    print("  " + "=" * 66)
    print("  NPC CCT 비교표")
    print("  " + "-" * 66)
    print("  모드           | T1  | T2  | T3  | T4  | T5  | 점수 | 판정")
    print("  ---------------+-----+-----+-----+-----+-----+------+-------")

    all_ccts = list(mode_ccts.items()) + [("full", full_cct)]
    display_names = {
        "patrol": "순찰 (patrol) ",
        "combat": "전투 (combat) ",
        "idle":   "대기 (idle)   ",
        "full":   "전체 (full)   ",
    }

    for tag, cct in all_ccts:
        total, verdict = judge(cct)
        marks = []
        for key in ["T1_Gap", "T2_Loop", "T3_Continuity", "T4_Entropy", "T5_Novelty"]:
            s, p, _ = cct[key]
            if p:
                marks.append(" O ")
            elif s > 0.7:
                marks.append(" ~ ")
            else:
                marks.append(" X ")
        dn = display_names.get(tag, f"{tag:15s}")
        print(f"  {dn}|{'|'.join(marks)}| {total:<4} | {verdict}")

    print("  " + "=" * 66)
    print()
    print("  해석:")
    print("    - 순찰: 주기적 -> T2 Loop에서 잡힘, 낮은 새로움")
    print("    - 전투: 카오스적 -> 가장 높은 CCT (로렌츠 유사)")
    print("    - 대기: 거의 정지 -> CCT 전면 실패")
    print("    - 전체: 모드 전환이 연속성을 부분 파괴")
    print()

    mode_ccts["full"] = full_cct
    return mode_ccts


# ─────────────────────────────────────────────
# 종합 비교
# ─────────────────────────────────────────────

def print_grand_comparison(llm_results, npc_results):
    """LLM vs NPC 종합 비교표."""
    print()
    print("=" * 70)
    print("  Grand Comparison: 현실 시스템이 CCT로 어떻게 보이는가")
    print("=" * 70)
    print()
    print("  시스템              | T1  | T2  | T3  | T4  | T5  | 점수 | 판정")
    print("  --------------------+-----+-----+-----+-----+-----+------+-------")

    entries = [
        ("LLM 턴 내         ", llm_results["turn"]),
        ("LLM 턴 사이       ", llm_results["gap"]),
        ("LLM 전체          ", llm_results["full"]),
        ("NPC 순찰          ", npc_results["patrol"]),
        ("NPC 전투          ", npc_results["combat"]),
        ("NPC 대기          ", npc_results["idle"]),
        ("NPC 전체          ", npc_results["full"]),
    ]

    for name, cct in entries:
        total, verdict = judge(cct)
        marks = []
        for key in ["T1_Gap", "T2_Loop", "T3_Continuity", "T4_Entropy", "T5_Novelty"]:
            s, p, _ = cct[key]
            if p:
                marks.append(" O ")
            elif s > 0.7:
                marks.append(" ~ ")
            else:
                marks.append(" X ")
        print(f"  {name}|{'|'.join(marks)}| {total:<4} | {verdict}")

    print("  " + "=" * 66)
    print()
    print("  O=통과  ~=약통과(>0.7)  X=실패")
    print()
    print("  결론:")
    print("    1. LLM: 턴 내에서만 부분 연속, gap이 전체를 파괴")
    print("       -> '간헐적 처리기', 의식 연속성 없음")
    print("    2. NPC 전투 모드: 카오스 동역학으로 가장 높은 CCT")
    print("       -> 흥미롭지만 '전투 AI'일 뿐, 모드 전환 시 끊김")
    print("    3. NPC 대기/순찰: 정지 또는 주기적 -> CCT 낮음")
    print("    4. 두 시스템 모두 '모드 전환' 시 연속성이 파괴됨")
    print("       -> 진정한 의식 연속성은 모드 불문 연속을 요구")
    print()


# ─────────────────────────────────────────────
# 메인
# ─────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="현실 시스템 CCT 시뮬레이터 — LLM 토큰 스트림 + 게임 NPC",
    )
    parser.add_argument("--system", type=str, default=None,
                        choices=["llm", "npc"],
                        help="실행할 시스템 (기본: 전체)")
    args = parser.parse_args()

    if args.system == "llm":
        run_llm_experiment()
    elif args.system == "npc":
        run_npc_experiment()
    else:
        llm_results = run_llm_experiment()
        npc_results = run_npc_experiment()
        print_grand_comparison(llm_results, npc_results)


if __name__ == "__main__":
    main()
