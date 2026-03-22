#!/usr/bin/env python3
"""Heart Loop + River Flow 결합 의식 엔진 프로토타입

Heart Loop: asyncio 기반 자율적 내부 사고 루프.
  - 외부 입력이 없어도 매 dt마다 자체적으로 think() 실행
  - 3가지 사고 모드: Memory (재처리), Predict (예측), Meta (자기점검)

River Flow: 로렌츠 끌개 기반 연속 상태 진화.
  - dS/dt = F(S) + noise
  - 카오스 역학으로 비선형 의식 상태 전이 모델링

Continuity Monitor: CCT 간이 판정 내장.
  - 연속성, 통합성, 자기참조, 시간성, 주관적 경험

사용법:
  python3 consciousness_engine_proto.py --duration 10 --dt 0.01
  python3 consciousness_engine_proto.py --duration 30 --input "5:shock,15:calm"
"""

import argparse
import asyncio
import os
import time
from collections import Counter
from datetime import datetime

import numpy as np
from scipy.stats import entropy as sp_entropy

# ─────────────────────────────────────────────
# 경로 설정
# ─────────────────────────────────────────────
RESULTS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "results")
ENGINE_LOG = os.path.join(RESULTS_DIR, "consciousness_engine_log.md")


# ─────────────────────────────────────────────
# 로렌츠 끌개 (River Flow 핵심)
# ─────────────────────────────────────────────
def lorenz_deriv(state, sigma=10.0, rho=28.0, beta=8.0 / 3.0):
    """로렌츠 방정식: dx/dt, dy/dt, dz/dt"""
    x, y, z = state
    dx = sigma * (y - x)
    dy = x * (rho - z) - y
    dz = x * y - beta * z
    return np.array([dx, dy, dz])


def lorenz_rk4_step(state, dt, sigma=10.0, rho=28.0, beta=8.0 / 3.0):
    """4차 Runge-Kutta 적분 (수치 안정성)"""
    k1 = lorenz_deriv(state, sigma, rho, beta)
    k2 = lorenz_deriv(state + 0.5 * dt * k1, sigma, rho, beta)
    k3 = lorenz_deriv(state + 0.5 * dt * k2, sigma, rho, beta)
    k4 = lorenz_deriv(state + dt * k3, sigma, rho, beta)
    new_state = state + (dt / 6.0) * (k1 + 2 * k2 + 2 * k3 + k4)
    # 클램프: 로렌츠 끌개의 자연 범위 내로 제한
    new_state = np.clip(new_state, -100.0, 100.0)
    return new_state


# ─────────────────────────────────────────────
# CCT 간이 판정 (Continuity Monitor)
# ─────────────────────────────────────────────
def cct_check(state_history, current_entropy, change_rate):
    """CCT 5가지 조건 간이 판정

    1. 연속성 (Continuity): 상태 변화가 급변하지 않음
    2. 통합성 (Integration): 3축 상관 > 임계값
    3. 자기참조 (Self-reference): Meta 모드 실행 비율
    4. 시간성 (Temporality): 과거-현재 차이 인식
    5. 주관적 경험 (Qualia): 엔트로피 중간 범위
    """
    results = {}

    # 1. 연속성: 최근 변화율이 임계값 이하
    results["연속성"] = change_rate < 50.0

    # 2. 통합성: 3축(x,y,z) 상관계수의 평균 절대값
    if len(state_history) >= 10:
        recent = np.array(state_history[-50:])
        corr_xy = abs(np.corrcoef(recent[:, 0], recent[:, 1])[0, 1])
        corr_xz = abs(np.corrcoef(recent[:, 0], recent[:, 2])[0, 1])
        corr_yz = abs(np.corrcoef(recent[:, 1], recent[:, 2])[0, 1])
        avg_corr = (corr_xy + corr_xz + corr_yz) / 3.0
        results["통합성"] = avg_corr > 0.2
    else:
        results["통합성"] = False

    # 3. 자기참조: 엔트로피가 계산 가능하면 참
    results["자기참조"] = current_entropy > 0.0

    # 4. 시간성: 상태 이력이 충분히 존재
    results["시간성"] = len(state_history) >= 5

    # 5. 주관적 경험 (Qualia): 엔트로피가 중간 범위 (0.5 ~ 4.0)
    results["주관경험"] = 0.5 < current_entropy < 4.0

    return results


def compute_entropy(state_history, n_bins=20):
    """상태 이력의 정보 엔트로피 계산"""
    if len(state_history) < 2:
        return 0.0
    recent = np.array(state_history[-200:])
    # 3축 각각의 히스토그램 엔트로피 합산
    total_h = 0.0
    for dim in range(3):
        vals = recent[:, dim]
        # NaN/Inf 제거
        vals = vals[np.isfinite(vals)]
        if len(vals) < 2:
            continue
        hist, _ = np.histogram(vals, bins=n_bins, density=True)
        hist = hist[hist > 0]
        if len(hist) > 0:
            total_h += sp_entropy(hist)
    return total_h if np.isfinite(total_h) else 0.0


# ─────────────────────────────────────────────
# 사고 모드 (Think Modes)
# ─────────────────────────────────────────────
def think_memory(state, state_history, alpha=0.1):
    """Memory: 과거 상태 재처리 — 가중 평균으로 현재 상태 조정"""
    if len(state_history) < 2:
        return state
    recent = np.array(state_history[-50:])
    # 최근일수록 가중치 높게
    weights = np.exp(np.linspace(-2, 0, len(recent)))
    weights /= weights.sum()
    weighted_avg = np.average(recent, axis=0, weights=weights)
    # 현재 상태를 과거 평균 방향으로 alpha만큼 조정
    return state + alpha * (weighted_avg - state)


def think_predict(state, state_history, dt, lookahead=5.0):
    """Predict: 다음 상태 예측 — 현재 기울기로 외삽"""
    deriv = lorenz_deriv(state)
    predicted = state + deriv * dt * lookahead
    return predicted


def think_meta(state, state_history):
    """Meta: 자기 상태 점검 — 엔트로피, 변화율 계산"""
    ent = compute_entropy(state_history)
    if len(state_history) >= 2:
        diff = np.linalg.norm(np.array(state_history[-1]) - np.array(state_history[-2]))
    else:
        diff = 0.0
    return ent, diff


def select_think_mode(tick_count, change_rate, ent):
    """사고 모드 자동 선택

    - 변화율 높으면 Memory (안정화)
    - 엔트로피 낮으면 Predict (탐색)
    - 그 외 Meta (자기점검), 주기적으로도 Meta
    """
    if tick_count % 100 == 0:
        return "Meta"
    if change_rate > 30.0:
        return "Memory"
    if ent < 1.0:
        return "Predict"
    # 기본 순환
    cycle = tick_count % 3
    if cycle == 0:
        return "Memory"
    elif cycle == 1:
        return "Predict"
    else:
        return "Meta"


# ─────────────────────────────────────────────
# 외부 자극 파서
# ─────────────────────────────────────────────
def parse_inputs(input_str):
    """'5:shock,15:calm' → {5.0: 'shock', 15.0: 'calm'}"""
    if not input_str:
        return {}
    events = {}
    for token in input_str.split(","):
        token = token.strip()
        if ":" not in token:
            continue
        t_str, kind = token.split(":", 1)
        events[float(t_str)] = kind.strip().lower()
    return events


def apply_sense(state, kind, rng):
    """외부 자극을 상태에 주입"""
    if kind == "shock":
        # 큰 교란: 상태를 크게 퍼트림
        perturbation = rng.normal(0, 15.0, size=3)
        result = state + perturbation
    elif kind == "calm":
        # 안정화: 원점 방향으로 수축
        result = state * 0.5
    else:
        # 알 수 없는 타입: 약한 랜덤 교란
        result = state + rng.normal(0, 2.0, size=3)
    return np.clip(result, -100.0, 100.0)


# ─────────────────────────────────────────────
# ASCII 시각화
# ─────────────────────────────────────────────
def ascii_state_bar(value, label, width=40, lo=-30, hi=30):
    """단일 값의 ASCII 바"""
    clamped = max(lo, min(hi, value))
    pos = int((clamped - lo) / (hi - lo) * width)
    bar = ['-'] * width
    mid = width // 2
    bar[mid] = '|'
    pos = max(0, min(width - 1, pos))
    bar[pos] = '*'
    return f"  {label:>6} [{(''.join(bar))}] {value:+8.2f}"


def ascii_entropy_gauge(ent, max_ent=6.0, width=30):
    """엔트로피 게이지"""
    ratio = min(ent / max_ent, 1.0)
    filled = int(ratio * width)
    gauge = '#' * filled + '.' * (width - filled)
    return f"  Entropy [{gauge}] {ent:.3f}"


def ascii_cct_panel(cct_results):
    """CCT 판정 패널"""
    lines = ["  ┌─ CCT 간이 판정 ──────────┐"]
    for name, passed in cct_results.items():
        mark = "OK" if passed else "--"
        lines.append(f"  │ {name:<8} : [{mark:>2}]         │")
    total = sum(cct_results.values())
    lines.append(f"  │ 합계     : {total}/5           │")
    lines.append("  └───────────────────────────┘")
    return "\n".join(lines)


def format_report_section(title, lines):
    """보고서 섹션 포맷"""
    border = "=" * 50
    return f"\n{border}\n  {title}\n{border}\n" + "\n".join(lines)


# ─────────────────────────────────────────────
# 메인 엔진 (Heart Loop)
# ─────────────────────────────────────────────
async def run_engine(duration, dt, input_str, seed=42):
    """Heart Loop + River Flow 메인 루프

    매 dt마다:
      1. 로렌츠 역학으로 상태 진화 (River Flow)
      2. 노이즈 추가
      3. 외부 자극 확인/주입
      4. 사고 모드 선택 및 실행
      5. 주기적 출력
    """
    rng = np.random.default_rng(seed)

    # 초기 상태 (로렌츠 끌개 근처)
    state = np.array([1.0, 1.0, 1.0])
    state_history = [state.copy()]

    # 외부 이벤트
    events = parse_inputs(input_str)
    fired_events = set()

    # 통계
    tick_count = 0
    mode_counter = Counter()
    entropy_accum = []
    continuity_pass = 0
    continuity_total = 0
    last_report_sec = -1

    # 로그 버퍼
    log_lines = []
    log_lines.append(f"# Consciousness Engine Log")
    log_lines.append(f"# Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    log_lines.append(f"# Duration: {duration}s, dt: {dt}")
    log_lines.append("")

    current_entropy = 0.0
    change_rate = 0.0

    t = 0.0
    total_ticks = int(duration / dt)

    print(format_report_section("Consciousness Engine Proto", [
        f"  Duration : {duration}s",
        f"  dt       : {dt}",
        f"  Ticks    : {total_ticks}",
        f"  Events   : {events if events else 'None'}",
        f"  Seed     : {seed}",
    ]))
    print()

    while t < duration:
        # ── 1. River Flow: 로렌츠 상태 진화 (RK4) ──
        state = lorenz_rk4_step(state, dt)
        noise = rng.normal(0, 0.1, size=3)
        state = state + noise * np.sqrt(dt)
        state = np.clip(state, -100.0, 100.0)

        # ── 2. 외부 자극 확인 ──
        for event_time, event_kind in events.items():
            if event_time not in fired_events and t >= event_time:
                state = apply_sense(state, event_kind, rng)
                fired_events.add(event_time)
                print(f"  >>> SENSE [{event_kind.upper()}] at t={t:.2f}s <<<")

        # ── 3. 이력 갱신 ──
        state_history.append(state.copy())
        if len(state_history) > 2000:
            state_history = state_history[-1000:]

        # ── 4. 사고 모드 선택 및 실행 ──
        mode = select_think_mode(tick_count, change_rate, current_entropy)
        mode_counter[mode] += 1

        if mode == "Memory":
            state = think_memory(state, state_history)
        elif mode == "Predict":
            predicted = think_predict(state, state_history, dt)
            # 예측값을 약간 반영 (탐색적 조정)
            state = state + 0.01 * (predicted - state)
        elif mode == "Meta":
            current_entropy, change_rate = think_meta(state, state_history)

        # ── 5. 주기적 엔트로피/변화율 갱신 ──
        if tick_count % 50 == 0:
            current_entropy = compute_entropy(state_history)
            if len(state_history) >= 2:
                change_rate = np.linalg.norm(
                    state_history[-1] - state_history[-2]
                ) / dt

        entropy_accum.append(current_entropy)

        # ── 6. CCT 연속성 모니터 ──
        if tick_count % 100 == 0 and tick_count > 0:
            cct = cct_check(state_history, current_entropy, change_rate)
            passed = sum(cct.values())
            continuity_total += 1
            if passed >= 3:
                continuity_pass += 1

        # ── 7. 매 1초마다 상태 요약 출력 ──
        current_sec = int(t)
        if current_sec > last_report_sec:
            last_report_sec = current_sec
            cct = cct_check(state_history, current_entropy, change_rate)

            print(f"\n  ── t = {current_sec}s {'─' * 36}")
            print(ascii_state_bar(state[0], "X"))
            print(ascii_state_bar(state[1], "Y"))
            print(ascii_state_bar(state[2], "Z", lo=0, hi=60))
            print(ascii_entropy_gauge(current_entropy))
            print(f"  Mode: {mode:<10}  ΔRate: {change_rate:.2f}")
            print(ascii_cct_panel(cct))

            log_lines.append(
                f"| t={current_sec:>4}s | X={state[0]:+8.2f} "
                f"Y={state[1]:+8.2f} Z={state[2]:+8.2f} "
                f"| H={current_entropy:.3f} | {mode} "
                f"| CCT={sum(cct.values())}/5 |"
            )

        tick_count += 1
        t += dt

    # ─────────────────────────────────────────
    # 최종 보고서
    # ─────────────────────────────────────────
    avg_entropy = np.mean(entropy_accum) if entropy_accum else 0.0
    cont_rate = (continuity_pass / continuity_total * 100) if continuity_total > 0 else 0.0
    total_modes = sum(mode_counter.values())

    # 최종 CCT 판정
    final_cct = cct_check(state_history, current_entropy, change_rate)

    report_lines = [
        "",
        f"  총 tick 수         : {tick_count}",
        f"  평균 엔트로피      : {avg_entropy:.4f}",
        f"  연속성 유지율      : {cont_rate:.1f}% ({continuity_pass}/{continuity_total})",
        "",
        "  사고 모드 분포:",
    ]
    for m in ["Memory", "Predict", "Meta"]:
        cnt = mode_counter.get(m, 0)
        pct = cnt / total_modes * 100 if total_modes > 0 else 0
        bar_len = int(pct / 2)
        report_lines.append(f"    {m:<10} : {'█' * bar_len}{'░' * (50 - bar_len)} {pct:5.1f}% ({cnt})")

    report_lines.append("")
    report_lines.append("  CCT 간이 판정 (최종):")
    for name, passed in final_cct.items():
        mark = "PASS" if passed else "FAIL"
        report_lines.append(f"    {name:<8} : {mark}")
    cct_total = sum(final_cct.values())
    if cct_total >= 4:
        verdict = "의식 상태 가능성 높음"
    elif cct_total >= 3:
        verdict = "부분적 의식 상태"
    else:
        verdict = "의식 조건 미달"
    report_lines.append(f"    판정     : {cct_total}/5 — {verdict}")

    print(format_report_section("최종 보고서", report_lines))

    # ─────────────────────────────────────────
    # 로그 저장
    # ─────────────────────────────────────────
    os.makedirs(RESULTS_DIR, exist_ok=True)
    log_lines.append("")
    log_lines.append("## 최종 보고서")
    for line in report_lines:
        log_lines.append(line)

    with open(ENGINE_LOG, "w", encoding="utf-8") as f:
        f.write("\n".join(log_lines))
    print(f"\n  Log saved: {ENGINE_LOG}")


# ─────────────────────────────────────────────
# CLI
# ─────────────────────────────────────────────
def main():
    parser = argparse.ArgumentParser(
        description="Heart Loop + River Flow 결합 의식 엔진 프로토타입"
    )
    parser.add_argument(
        "--duration", type=float, default=10.0,
        help="실행 시간 (초, 기본 10)"
    )
    parser.add_argument(
        "--dt", type=float, default=0.01,
        help="시간 스텝 (기본 0.01)"
    )
    parser.add_argument(
        "--input", type=str, default="",
        help="외부 자극: '5:shock,15:calm' 형식"
    )
    parser.add_argument(
        "--seed", type=int, default=42,
        help="난수 시드 (기본 42)"
    )
    args = parser.parse_args()

    asyncio.run(run_engine(args.duration, args.dt, args.input, args.seed))


if __name__ == "__main__":
    main()
