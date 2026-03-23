#!/usr/bin/env python3
"""텍사스 명사수 검정 — 양자/물리 발견 전용

각 발견의 파라미터 공간을 스캔하여 우연 히트 확률(p-value)을 산출하고,
Bonferroni 보정으로 다중 비교 문제를 교정한다.

사용법:
  python3 texas_quantum.py                        # 전체 검정
  python3 texas_quantum.py --discovery "1/alpha"   # 특정 발견만
  python3 texas_quantum.py --monte-carlo 100000    # 몬테카를로 반복 수
"""

import argparse
import itertools
import math
import sys

import numpy as np

# ─── 수론 함수 ───────────────────────────────────────────────

def divisor_sigma(n, k=1):
    """σ_k(n) = sum of k-th powers of divisors of n."""
    s = 0
    for d in range(1, n + 1):
        if n % d == 0:
            s += d ** k
    return s


def triangular(n):
    """T(n) = n(n+1)/2."""
    return n * (n + 1) // 2


# ─── 발견 목록 ───────────────────────────────────────────────

DISCOVERIES = [
    {
        "name": "1/alpha ≈ 137 + 1/28",
        "formula": "137 + 1/n",
        "param_range": (1, 1000),
        "target": 137.035999084,
        "threshold": 0.001,
    },
    {
        "name": "m_p/m_e ≈ sigma(6) × T(17)",
        "formula": "sigma(n) × T(k)",
        "param_range": [(1, 100), (1, 100)],
        "target": 1836.15267343,
        "threshold": 0.001,
    },
    {
        "name": "m_mu/m_e ≈ 28 × e²",
        "formula": "n × e²",
        "param_range": (1, 100),
        "target": 206.7682830,
        "threshold": 0.001,
    },
    {
        "name": "m_tau/m_e ≈ 3×19×61",
        "formula": "a × b × c",
        "param_range": [(1, 30), (1, 100), (1, 100)],
        "target": 3477.48,
        "threshold": 0.001,
    },
    {
        "name": "sin²θ_W ≈ 3/13",
        "formula": "a/b",
        "param_range": [(1, 20), (1, 200)],
        "target": 0.23122,
        "threshold": 0.005,
    },
    {
        "name": "e^(ln2·ln3) + 1 ≈ π",
        "formula": "a^ln(b) + 1",
        "param_range": None,
        "target": 3.14159265,
        "threshold": 0.0001,
    },
    {
        "name": "exp(1/(2e)) ≈ ζ(3)",
        "formula": "exp(1/(a×b))",
        "param_range": None,
        "target": 1.2020569031,
        "threshold": 0.0001,
    },
    {
        "name": "CMB ≈ e + 1/137",
        "formula": "e + 1/n",
        "param_range": (1, 1000),
        "target": 2.7255,
        "threshold": 0.001,
    },
]


# ─── 스캔 엔진 ───────────────────────────────────────────────

def _relative_error(val, target):
    return abs(val - target) / max(abs(target), 1e-15)


def scan_1d(disc):
    """1차원 파라미터 스캔. 반환: (hits, total)."""
    lo, hi = disc["param_range"]
    formula = disc["formula"]
    target = disc["target"]
    threshold = disc["threshold"]

    hits = 0
    total = hi - lo + 1

    for n in range(lo, hi + 1):
        if "137 + 1/n" in formula:
            val = 137.0 + 1.0 / n
        elif "n × e²" in formula:
            val = n * math.e ** 2
        elif "e + 1/n" in formula:
            val = math.e + 1.0 / n
        else:
            continue

        if _relative_error(val, target) < threshold:
            hits += 1

    return hits, total


def scan_2d(disc):
    """2차원 파라미터 스캔. 반환: (hits, total)."""
    ranges = disc["param_range"]
    formula = disc["formula"]
    target = disc["target"]
    threshold = disc["threshold"]

    r0 = range(ranges[0][0], ranges[0][1] + 1)
    r1 = range(ranges[1][0], ranges[1][1] + 1)
    total = len(r0) * len(r1)
    hits = 0

    for a, b in itertools.product(r0, r1):
        if "sigma(n) × T(k)" in formula:
            val = divisor_sigma(a) * triangular(b)
        elif "a/b" in formula:
            if b == 0:
                continue
            val = a / b
        else:
            continue

        if _relative_error(val, target) < threshold:
            hits += 1

    return hits, total


def scan_3d(disc):
    """3차원 파라미터 스캔. 반환: (hits, total)."""
    ranges = disc["param_range"]
    target = disc["target"]
    threshold = disc["threshold"]

    r0 = range(ranges[0][0], ranges[0][1] + 1)
    r1 = range(ranges[1][0], ranges[1][1] + 1)
    r2 = range(ranges[2][0], ranges[2][1] + 1)
    total = len(r0) * len(r1) * len(r2)
    hits = 0

    for a, b, c in itertools.product(r0, r1, r2):
        val = a * b * c
        if _relative_error(val, target) < threshold:
            hits += 1

    return hits, total


def scan_monte_carlo(disc, n_trials):
    """특수 검정: 몬테카를로 시뮬레이션. 반환: (hits, total)."""
    rng = np.random.default_rng(42)
    target = disc["target"]
    threshold = disc["threshold"]
    formula = disc["formula"]

    # 상수 범위: 정수 2~10 사이의 랜덤 실수 (e≈2.718 같은 소규모 상수)
    hits = 0
    total = n_trials

    for _ in range(n_trials):
        a = rng.uniform(1.5, 10.0)
        b = rng.uniform(1.5, 10.0)

        if "a^ln(b) + 1" in formula:
            try:
                val = a ** math.log(b) + 1.0
            except (ValueError, OverflowError):
                continue
        elif "exp(1/(a×b))" in formula:
            try:
                val = math.exp(1.0 / (a * b))
            except (ValueError, OverflowError):
                continue
        else:
            continue

        if _relative_error(val, target) < threshold:
            hits += 1

    return hits, total


def run_single(disc, n_monte_carlo):
    """단일 발견 검정. 반환: (hits, total)."""
    pr = disc["param_range"]

    if pr is None:
        return scan_monte_carlo(disc, n_monte_carlo)
    elif isinstance(pr, list):
        if len(pr) == 2:
            return scan_2d(disc)
        elif len(pr) == 3:
            return scan_3d(disc)
    else:
        return scan_1d(disc)

    return 0, 1  # fallback


# ─── 판정 ─────────────────────────────────────────────────────

def verdict(bonf_p):
    if bonf_p < 0.01:
        return "★ 구조적"
    elif bonf_p < 0.05:
        return "△ 약한"
    else:
        return "✕ 우연"


# ─── 메인 ─────────────────────────────────────────────────────

def run(discoveries, n_monte_carlo, filter_name=None):
    if filter_name:
        discoveries = [d for d in discoveries if filter_name.lower() in d["name"].lower()]
        if not discoveries:
            print(f"  '{filter_name}'에 해당하는 발견 없음")
            sys.exit(1)

    n_total_disc = len(DISCOVERIES)  # Bonferroni는 항상 전체 수 기준

    print("═" * 55)
    print(" Texas Sharpshooter — Quantum Discoveries")
    print("═" * 55)
    print()

    # 헤더
    hdr = f" {'발견':<26}│ {'단일 p':>10} │ {'Bonf. p':>10} │ {'판정'}"
    print(hdr)
    print(f" {'─' * 26}┼{'─' * 12}┼{'─' * 12}┼{'─' * 12}")

    results = []
    total_combinations = 0
    significant = 0

    for disc in discoveries:
        hits, total = run_single(disc, n_monte_carlo)
        total_combinations += total

        if total == 0:
            p_single = 1.0
        else:
            p_single = hits / total

        p_bonf = min(p_single * n_total_disc, 1.0)
        verd = verdict(p_bonf)

        if "구조적" in verd:
            significant += 1

        results.append({
            "name": disc["name"],
            "hits": hits,
            "total": total,
            "p_single": p_single,
            "p_bonf": p_bonf,
            "verdict": verd,
        })

        # 이름 자르기 (최대 26자)
        short = disc["name"][:26]
        print(f" {short:<26}│ {p_single:>10.6f} │ {p_bonf:>10.6f} │ {verd}")

    print()
    print(f" 총 조합 수: ~{total_combinations:.2e}")
    print(f" 유의한 발견: {significant}/{len(discoveries)}")
    print("═" * 55)

    # 개별 상세
    print()
    print("─" * 55)
    print(" 상세 결과")
    print("─" * 55)
    for r in results:
        print(f"  {r['name']}")
        print(f"    hits={r['hits']}, total={r['total']}, "
              f"p={r['p_single']:.8f}, bonf={r['p_bonf']:.8f}")
    print("─" * 55)


def main():
    parser = argparse.ArgumentParser(
        description="텍사스 명사수 검정 — 양자/물리 발견 전용"
    )
    parser.add_argument(
        "--discovery", type=str, default=None,
        help="특정 발견만 검정 (이름 부분 매칭)"
    )
    parser.add_argument(
        "--monte-carlo", type=int, default=100000,
        help="몬테카를로 반복 수 (기본 100000)"
    )
    args = parser.parse_args()

    run(DISCOVERIES, args.monte_carlo, args.discovery)


if __name__ == "__main__":
    main()
