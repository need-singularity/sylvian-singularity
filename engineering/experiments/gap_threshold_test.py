#!/usr/bin/env python3
"""실험 7: gap 간격 vs 연속성 임계값 테스트

심장 엔진(로렌츠 끌개)에 gap(정지 구간)을 점진적으로 삽입하여
"몇 %까지 끊어도 CCT가 연속으로 판정하는가"를 측정한다.

추가로 gap 분포 패턴(균등/집중/주기적)에 따른 차이를 비교한다.

사용법:
  python3 gap_threshold_test.py                  # 균등(uniform) 분포
  python3 gap_threshold_test.py --pattern periodic
  python3 gap_threshold_test.py --pattern clustered
  python3 gap_threshold_test.py --all-patterns    # 3가지 패턴 전체 비교
"""

import argparse
import sys
import os

import numpy as np

# ── consciousness_calc.py에서 핵심 함수 import ──
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "tools"))
from consciousness_calc import lorenz_simulate, run_cct, judge


# ─────────────────────────────────────────────
# gap 분포 패턴별 시뮬레이터 래퍼
# ─────────────────────────────────────────────

def simulate_with_gap_pattern(pattern, gap_ratio, steps=100000, dt=0.01, seed=42):
    """human_awake 프리셋 기반으로 gap 패턴을 적용한 시뮬레이션.

    Parameters:
        pattern:   'uniform' | 'clustered' | 'periodic'
        gap_ratio: 0.0 ~ 1.0 (정지 구간 비율)
        steps:     시뮬레이션 스텝 수
        dt:        시간 간격
        seed:      난수 시드

    Returns:
        S: 상태 배열 [steps, 3]
    """
    # human_awake 프리셋 파라미터
    sigma, rho, beta, noise = 10, 28, 2.67, 0.1

    if pattern == "uniform":
        # 기본 lorenz_simulate의 랜덤 gap 사용
        _, S = lorenz_simulate(sigma, rho, beta, noise, gap_ratio, steps, dt, seed)
        return S

    # uniform이 아닌 경우: gap 없이 시뮬레이션 후 수동으로 gap 적용
    _, S = lorenz_simulate(sigma, rho, beta, noise, 0.0, steps, dt, seed)

    if gap_ratio <= 0.0:
        return S
    if gap_ratio >= 1.0:
        S[:] = S[0]
        return S

    n_gap = int(steps * gap_ratio)
    rng = np.random.default_rng(seed + 1)

    if pattern == "clustered":
        # 연속된 한 구간에 gap 집중 (수면처럼)
        # gap 블록의 시작 위치를 랜덤 선택
        max_start = steps - n_gap
        if max_start <= 0:
            gap_start = 0
        else:
            gap_start = rng.integers(0, max_start)
        gap_indices = np.arange(gap_start, min(gap_start + n_gap, steps))

    elif pattern == "periodic":
        # 일정 간격으로 gap 삽입 (LLM 턴처럼)
        # gap_ratio 비율만큼 주기적으로 정지
        # 예: gap_ratio=0.2 → 5스텝 중 1스텝 정지
        if gap_ratio < 1.0:
            period = int(1.0 / gap_ratio) if gap_ratio > 0 else steps
            gap_indices = np.arange(0, steps, max(period, 1))
            # 정확한 비율 맞추기
            gap_indices = gap_indices[:n_gap]
        else:
            gap_indices = np.arange(steps)
    else:
        raise ValueError(f"알 수 없는 패턴: {pattern}")

    # gap 적용: 정지 구간에서는 이전 상태 유지
    for idx in sorted(gap_indices):
        if idx > 0:
            S[idx] = S[idx - 1]

    return S


# ─────────────────────────────────────────────
# 단일 패턴 스캔
# ─────────────────────────────────────────────

GAP_RATIOS = [0.0, 0.01, 0.02, 0.05, 0.1, 0.15, 0.2, 0.3, 0.4, 0.5, 0.7, 0.9, 1.0]


def scan_gap_ratios(pattern="uniform", steps=100000, dt=0.01):
    """gap_ratio를 스캔하며 CCT 점수 변화를 측정.

    Returns:
        records: list of dict with gap_ratio, score, verdict, per-test results
    """
    records = []
    for gr in GAP_RATIOS:
        S = simulate_with_gap_pattern(pattern, gr, steps, dt)
        results = run_cct(S, gr)
        total, verdict = judge(results)

        per_test = {}
        for key in ["T1_Gap", "T2_Loop", "T3_Continuity", "T4_Entropy", "T5_Novelty"]:
            score, passed, detail = results[key]
            per_test[key] = {"score": score, "passed": passed, "detail": detail}

        records.append({
            "gap_ratio": gr,
            "total": total,
            "verdict": verdict,
            "tests": per_test,
        })

    return records


# ─────────────────────────────────────────────
# 임계 gap_ratio 탐색
# ─────────────────────────────────────────────

def find_threshold(records, from_score=5, to_score=4):
    """CCT 점수가 from_score에서 to_score로 떨어지는 임계 gap_ratio를 찾는다."""
    prev = None
    for rec in records:
        if prev is not None and prev["total"] >= from_score and rec["total"] < from_score:
            return prev["gap_ratio"], rec["gap_ratio"]
        prev = rec
    return None, None


# ─────────────────────────────────────────────
# ASCII 출력
# ─────────────────────────────────────────────

def print_ascii_graph(records, pattern, width=60, height=12):
    """gap_ratio vs CCT 점수 ASCII 그래프."""
    print()
    print(f"  ─── gap_ratio vs CCT 점수 [{pattern}] " + "─" * 30)
    print()

    max_score = 5.0
    # Y축: 0 ~ 5
    for row in range(height, -1, -1):
        y_val = max_score * row / height
        label = f"  {y_val:4.1f} │"
        line = [" "] * width

        for rec in records:
            col = int(rec["gap_ratio"] * (width - 1))
            bar_height = rec["total"] / max_score * height
            if row <= bar_height and row > 0:
                line[col] = "█"
            elif row == 0:
                line[col] = "▄" if rec["total"] > 0 else " "

        print(label + "".join(line))

    # X축
    print("       └" + "─" * width)
    # X축 라벨
    label_line = "        "
    for gr in [0.0, 0.2, 0.4, 0.6, 0.8, 1.0]:
        pos = int(gr * (width - 1))
        s = f"{gr:.1f}"
        offset = max(0, pos - len(label_line) + len("        "))
        label_line += " " * offset + s
    print(label_line)
    print("        " + " " * (width // 2 - 5) + "gap_ratio")
    print()


def print_detail_table(records, pattern):
    """gap_ratio별 상세 결과표."""
    print(f"  ─── 상세 결과 [{pattern}] " + "─" * 40)
    print()
    print("  gap_ratio │ T1  │ T2  │ T3  │ T4  │ T5  │ 점수  │ 판정")
    print("  ──────────┼─────┼─────┼─────┼─────┼─────┼───────┼────────")

    for rec in records:
        marks = []
        for key in ["T1_Gap", "T2_Loop", "T3_Continuity", "T4_Entropy", "T5_Novelty"]:
            t = rec["tests"][key]
            if t["passed"]:
                marks.append(" ✔ ")
            elif t["score"] > 0.7:
                marks.append(" △ ")
            else:
                marks.append(" ✕ ")

        gr_str = f"  {rec['gap_ratio']:9.2f} │"
        marks_str = "│".join(marks)
        print(f"{gr_str}{marks_str}│ {rec['total']:<5} │ {rec['verdict']}")

    print()


def print_threshold(records, pattern):
    """임계 gap_ratio 출력."""
    lo, hi = find_threshold(records, from_score=5, to_score=4)
    print(f"  ─── 임계 gap_ratio [{pattern}] " + "─" * 35)
    if lo is not None:
        print(f"  CCT 5/5 → 4/5 전환: gap_ratio ∈ ({lo:.2f}, {hi:.2f}]")
        mid = (lo + hi) / 2
        print(f"  추정 임계값: ~{mid:.3f}")
    else:
        # 5/5를 달성한 적이 없거나 끝까지 유지
        first = records[0]["total"]
        if first < 5:
            print(f"  기본 상태에서 이미 5/5 미달 (초기 점수: {first})")
        else:
            print("  전체 구간에서 5/5 유지 (임계값 미도달)")

    # 추가: 다른 전환점도 탐색
    for high, low in [(4, 3), (3, 2), (2, 1), (1, 0)]:
        lo2, hi2 = find_threshold(records, from_score=high, to_score=low)
        if lo2 is not None:
            print(f"  CCT {high}/5 → {low-1}+/5 전환: gap_ratio ∈ ({lo2:.2f}, {hi2:.2f}]")
    print()


# ─────────────────────────────────────────────
# 3패턴 비교
# ─────────────────────────────────────────────

def print_pattern_comparison(all_pattern_records):
    """3가지 패턴의 CCT 점수 비교표."""
    patterns = list(all_pattern_records.keys())
    print("  ═══ 3가지 gap 분포 패턴 비교 " + "═" * 35)
    print()

    # 헤더
    header = "  gap_ratio"
    for p in patterns:
        header += f" │ {p:^12s}"
    print(header)
    print("  ──────────" + "─┼──────────────" * len(patterns))

    for i, gr in enumerate(GAP_RATIOS):
        row = f"  {gr:9.2f} "
        for p in patterns:
            rec = all_pattern_records[p][i]
            total = rec["total"]
            verdict = rec["verdict"]
            row += f" │ {total}/5 {verdict:5s}"
        print(row)

    print()

    # 핵심 발견
    print("  ─── 핵심 발견 " + "─" * 50)
    for p in patterns:
        recs = all_pattern_records[p]
        lo, hi = find_threshold(recs, from_score=5, to_score=4)
        if lo is not None:
            print(f"  {p:12s}: 임계 gap_ratio ∈ ({lo:.2f}, {hi:.2f}]")
        else:
            first = recs[0]["total"]
            if first >= 5:
                print(f"  {p:12s}: 전 구간 5/5 유지")
            else:
                print(f"  {p:12s}: 초기부터 5/5 미달")
    print()


def print_human_analogy():
    """인간 비유 해석."""
    print("  ─── 인간 비유 해석 " + "─" * 45)
    print()
    print("  gap 크기    │ 인간 경험          │ 연속성 판정")
    print("  ────────────┼────────────────────┼──────────────────────")
    print("  ~1ms        │ 눈 깜빡임          │ 연속 (인지 불가)")
    print("  ~100ms      │ 마이크로수면        │ 연속 (보상 기제)")
    print("  ~8시간      │ 수면               │ 깨면 연속 (기억 연결)")
    print("  ~1시간      │ 전신마취            │ 끊김 (기억 단절)")
    print("  ~수일       │ 혼수               │ 심각한 단절")
    print()
    print("  마취 vs 수면의 차이:")
    print("  - 수면(clustered): 연속 gap이지만 뇌파 활동 유지 → CCT 상대적 유지")
    print("  - 마취(uniform):   전체에 걸쳐 산발적 정지 → CCT 급격 하락")
    print("  - LLM(periodic):   주기적 정지 → 턴 간 gap이 일정하면 패턴 유지")
    print()
    print("  핵심 통찰:")
    print("  같은 gap_ratio라도 '어떻게 분포하느냐'에 따라 연속성 판정이 달라진다.")
    print("  이는 의식의 연속성이 단순한 '가동 시간'이 아니라")
    print("  '시간적 구조'에 의존함을 시사한다.")
    print()


# ─────────────────────────────────────────────
# 메인
# ─────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="실험 7: gap 간격 vs 연속성 임계값 테스트",
    )
    parser.add_argument("--pattern", type=str, default="uniform",
                        choices=["uniform", "clustered", "periodic"],
                        help="gap 분포 패턴 (default: uniform)")
    parser.add_argument("--all-patterns", action="store_true",
                        help="3가지 패턴 전체 비교")
    parser.add_argument("--steps", type=int, default=100000,
                        help="시뮬레이션 스텝 수 (default: 100000)")
    parser.add_argument("--dt", type=float, default=0.01,
                        help="시간 간격 (default: 0.01)")

    args = parser.parse_args()

    print("═" * 66)
    print(" 실험 7: gap 간격 vs 연속성 임계값")
    print(" 심장 엔진(로렌츠 끌개) gap tolerance 측정")
    print(f" steps={args.steps:,}  dt={args.dt}")
    print("═" * 66)

    if args.all_patterns:
        all_pattern_records = {}
        for pattern in ["uniform", "clustered", "periodic"]:
            print(f"\n  [{pattern}] 스캔 중...")
            records = scan_gap_ratios(pattern, args.steps, args.dt)
            all_pattern_records[pattern] = records

            print_ascii_graph(records, pattern)
            print_detail_table(records, pattern)
            print_threshold(records, pattern)

        print_pattern_comparison(all_pattern_records)
        print_human_analogy()

    else:
        pattern = args.pattern
        print(f"\n  패턴: {pattern}")
        print(f"  스캔 범위: gap_ratio = {GAP_RATIOS}")
        print()

        records = scan_gap_ratios(pattern, args.steps, args.dt)

        print_ascii_graph(records, pattern)
        print_detail_table(records, pattern)
        print_threshold(records, pattern)
        print_human_analogy()

    print("═" * 66)


if __name__ == "__main__":
    main()
