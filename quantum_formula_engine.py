#!/usr/bin/env python3
"""양자 공식 탐색 엔진 — 양자역학 무차원 상수 × 프로젝트 상수 DFS 탐색

프로젝트 상수(18개)와 양자 무차원 상수(9개)를 조합하여
수학적 타겟 상수와의 일치를 자동 탐색한다.
텍사스 명사수 검정으로 우연 vs 구조적 발견을 판별.

사용법:
  python3 quantum_formula_engine.py                    # 2개 조합, 0.1% 이내
  python3 quantum_formula_engine.py --threshold 0.01   # 0.01% 이내만
  python3 quantum_formula_engine.py --depth 3          # 3개 조합 (느림)
  python3 quantum_formula_engine.py --cross-only        # A그룹×B그룹 교차만
  python3 quantum_formula_engine.py --texas             # 텍사스 명사수 검정 포함
  python3 quantum_formula_engine.py --top 20            # 상위 20개만 출력
"""

import argparse
import os
import warnings
from datetime import datetime
from itertools import combinations

import numpy as np

warnings.filterwarnings("ignore", category=RuntimeWarning)

RESULTS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "results")


# ─────────────────────────────────────────
# 그룹 A: 프로젝트 상수 (기존)
# ─────────────────────────────────────────
PROJECT_CONSTS = {
    "1/2": 0.5,
    "1/3": 1 / 3,
    "1/6": 1 / 6,
    "5/6": 5 / 6,
    "2": 2.0,
    "6": 6.0,
    "8": 8.0,
    "17": 17.0,
    "137": 137.0,
    "ln3": np.log(3),
    "ln4/3": np.log(4 / 3),
    "e": np.e,
    "1/e": 1 / np.e,
    "sqrt3": np.sqrt(3),
    "4/3": 4 / 3,
    "sigma6": 12.0,
    "tau6": 4.0,
    "28": 28.0,
    "496": 496.0,
}

# ─────────────────────────────────────────
# 그룹 B: 양자 상수 (무차원)
# ─────────────────────────────────────────
QUANTUM_CONSTS = {
    "alpha": 1 / 137.035999084,
    "1/alpha": 137.035999084,
    "g_e-2": 0.00231930436256,
    "alpha_s": 0.1185,
    "sin2_thetaW": 0.23122,
    "m_e/m_p": 1 / 1836.15267343,
    "m_e/m_mu": 1 / 206.7682830,
    "N_gen": 3.0,
    "CMB": 2.7255,
}

# ─────────────────────────────────────────
# 타겟 상수 (매칭 대상)
# ─────────────────────────────────────────
TARGETS = {
    "pi": np.pi,
    "pi/2": np.pi / 2,
    "pi/3": np.pi / 3,
    "pi/4": np.pi / 4,
    "pi/6": np.pi / 6,
    "sqrt2": np.sqrt(2),
    "sqrt3": np.sqrt(3),
    "sqrt5": np.sqrt(5),
    "ln2": np.log(2),
    "phi": (1 + np.sqrt(5)) / 2,
    "Catalan": 0.9159655941,
    "zeta3": 1.2020569031,
    "gamma_EM": 0.5772156649,
    "e^gamma": np.exp(0.5772156649),
    "1/alpha_exact": 137.035999084,
    # 프로젝트 상수도 타겟에 포함 (교차 발견용)
    "1/2": 0.5,
    "1/3": 1 / 3,
    "1/6": 1 / 6,
    "5/6": 5 / 6,
    "1/e": 1 / np.e,
}


# ─────────────────────────────────────────
# 분류: 조합이 어느 그룹인지
# ─────────────────────────────────────────
def classify_pair(name_a, name_b):
    """두 상수의 그룹 조합 분류."""
    a_proj = name_a in PROJECT_CONSTS
    b_proj = name_b in PROJECT_CONSTS
    if a_proj and b_proj:
        return "A*A"
    elif not a_proj and not b_proj:
        return "B*B"
    else:
        return "A*B"


def classify_triple(name_a, name_b, name_c):
    """세 상수의 그룹 조합 분류."""
    names = [name_a, name_b, name_c]
    n_proj = sum(1 for n in names if n in PROJECT_CONSTS)
    if n_proj == 3:
        return "A*A*A"
    elif n_proj == 0:
        return "B*B*B"
    elif n_proj == 2:
        return "A*A*B"
    else:
        return "A*B*B"


# ─────────────────────────────────────────
# 이항 연산 (2개 상수)
# ─────────────────────────────────────────
def binary_ops(na, va, nb, vb):
    """두 상수에 대한 모든 연산 결과를 (값, 공식문자열) 리스트로 반환."""
    results = []

    # a + b
    results.append((va + vb, f"{na}+{nb}"))
    # a - b
    results.append((va - vb, f"{na}-{nb}"))
    # b - a
    results.append((vb - va, f"{nb}-{na}"))
    # a * b
    results.append((va * vb, f"{na}*{nb}"))
    # a / b
    if vb != 0:
        results.append((va / vb, f"{na}/{nb}"))
    # b / a
    if va != 0:
        results.append((vb / va, f"{nb}/{na}"))

    # a^b (|b| < 20)
    if va > 0 and abs(vb) < 20:
        try:
            val = va ** vb
            if np.isfinite(val) and abs(val) < 1e15:
                results.append((val, f"{na}^{nb}"))
        except (OverflowError, ValueError):
            pass

    # b^a (|a| < 20)
    if vb > 0 and abs(va) < 20:
        try:
            val = vb ** va
            if np.isfinite(val) and abs(val) < 1e15:
                results.append((val, f"{nb}^{na}"))
        except (OverflowError, ValueError):
            pass

    # log_a(b) : a>0, a!=1, b>0
    if va > 0 and va != 1 and vb > 0:
        try:
            val = np.log(vb) / np.log(va)
            if np.isfinite(val) and abs(val) < 1e15:
                results.append((val, f"log_{na}({nb})"))
        except (ValueError, ZeroDivisionError):
            pass

    # log_b(a) : b>0, b!=1, a>0
    if vb > 0 and vb != 1 and va > 0:
        try:
            val = np.log(va) / np.log(vb)
            if np.isfinite(val) and abs(val) < 1e15:
                results.append((val, f"log_{nb}({na})"))
        except (ValueError, ZeroDivisionError):
            pass

    # exp(a*b) : |a*b| < 20
    if abs(va * vb) < 20:
        try:
            val = np.exp(va * vb)
            if np.isfinite(val) and abs(val) < 1e15:
                results.append((val, f"exp({na}*{nb})"))
        except OverflowError:
            pass

    # sqrt(a*b) : a*b > 0
    if va * vb > 0:
        val = np.sqrt(va * vb)
        if np.isfinite(val):
            results.append((val, f"sqrt({na}*{nb})"))

    # a^(1/b) : a>0, b!=0
    if va > 0 and vb != 0 and abs(1 / vb) < 20:
        try:
            val = va ** (1 / vb)
            if np.isfinite(val) and abs(val) < 1e15:
                results.append((val, f"{na}^(1/{nb})"))
        except (OverflowError, ValueError):
            pass

    # b^(1/a) : b>0, a!=0
    if vb > 0 and va != 0 and abs(1 / va) < 20:
        try:
            val = vb ** (1 / va)
            if np.isfinite(val) and abs(val) < 1e15:
                results.append((val, f"{nb}^(1/{na})"))
        except (OverflowError, ValueError):
            pass

    # 유효한 결과만
    return [(v, expr) for v, expr in results
            if isinstance(v, (int, float)) and np.isfinite(v) and abs(v) < 1e15]


# ─────────────────────────────────────────
# 삼항 연산 (3개 상수)
# ─────────────────────────────────────────
def ternary_ops(na, va, nb, vb, nc, vc):
    """세 상수에 대한 연산 결과 리스트."""
    results = []

    # a*b + c
    results.append((va * vb + vc, f"{na}*{nb}+{nc}"))
    # a*b - c
    results.append((va * vb - vc, f"{na}*{nb}-{nc}"))
    # a*b*c
    val = va * vb * vc
    if np.isfinite(val) and abs(val) < 1e15:
        results.append((val, f"{na}*{nb}*{nc}"))

    # a^b + c (|b| < 20)
    if va > 0 and abs(vb) < 20:
        try:
            val = va ** vb + vc
            if np.isfinite(val) and abs(val) < 1e15:
                results.append((val, f"{na}^{nb}+{nc}"))
        except (OverflowError, ValueError):
            pass

    # (a+b)*c
    results.append(((va + vb) * vc, f"({na}+{nb})*{nc}"))

    # a^b * c (|b| < 20)
    if va > 0 and abs(vb) < 20:
        try:
            val = va ** vb * vc
            if np.isfinite(val) and abs(val) < 1e15:
                results.append((val, f"{na}^{nb}*{nc}"))
        except (OverflowError, ValueError):
            pass

    # a / (b+c)
    if vb + vc != 0:
        results.append((va / (vb + vc), f"{na}/({nb}+{nc})"))

    # (a*b)^c (|c| < 20)
    if va * vb > 0 and abs(vc) < 20:
        try:
            val = (va * vb) ** vc
            if np.isfinite(val) and abs(val) < 1e15:
                results.append((val, f"({na}*{nb})^{nc}"))
        except (OverflowError, ValueError):
            pass

    return [(v, expr) for v, expr in results
            if isinstance(v, (int, float)) and np.isfinite(v) and abs(v) < 1e15]


# ─────────────────────────────────────────
# 탐색 엔진
# ─────────────────────────────────────────
def search(depth=2, threshold=0.001, cross_only=False):
    """상수 조합으로 타겟을 만드는 공식 탐색.

    Args:
        depth: 조합 깊이 (2 또는 3)
        threshold: 상대 오차 임계값 (0.001 = 0.1%)
        cross_only: True이면 A*B 교차 조합만

    Returns:
        matches: list of dict
        total_trials: 총 시도 수
    """
    all_consts = {}
    all_consts.update(PROJECT_CONSTS)
    all_consts.update(QUANTUM_CONSTS)

    names = list(all_consts.keys())
    vals = [all_consts[n] for n in names]

    matches = []
    total_trials = 0

    # ── 2개 조합 ──
    for i in range(len(names)):
        for j in range(i, len(names)):
            na, va = names[i], vals[i]
            nb, vb = names[j], vals[j]

            cat = classify_pair(na, nb)
            if cross_only and cat != "A*B":
                continue

            ops = binary_ops(na, va, nb, vb)
            total_trials += len(ops)

            for val, expr in ops:
                for t_name, t_val in TARGETS.items():
                    if t_val == 0:
                        continue
                    rel_err = abs(val - t_val) / abs(t_val)
                    if rel_err < threshold:
                        # 자명한 매칭 스킵 (자기 자신)
                        if expr == t_name or ('+' not in expr and '-' not in expr
                                              and '*' not in expr and '/' not in expr
                                              and '^' not in expr and 'log' not in expr
                                              and 'exp' not in expr and 'sqrt' not in expr):
                            continue
                        matches.append({
                            "target": t_name,
                            "target_val": t_val,
                            "formula": expr,
                            "formula_val": val,
                            "error": rel_err,
                            "error_pct": rel_err * 100,
                            "category": cat,
                            "depth": 2,
                        })

    # ── 3개 조합 (선택적) ──
    if depth >= 3:
        for i in range(len(names)):
            for j in range(i, len(names)):
                for k in range(j, len(names)):
                    na, va = names[i], vals[i]
                    nb, vb = names[j], vals[j]
                    nc, vc = names[k], vals[k]

                    cat = classify_triple(na, nb, nc)
                    if cross_only and "A" not in cat and "B" not in cat:
                        continue
                    if cross_only and (cat == "A*A*A" or cat == "B*B*B"):
                        continue

                    # 모든 순열 조합
                    perms = [
                        (na, va, nb, vb, nc, vc),
                        (na, va, nc, vc, nb, vb),
                        (nb, vb, nc, vc, na, va),
                    ]
                    for pa, pva, pb, pvb, pc, pvc in perms:
                        ops = ternary_ops(pa, pva, pb, pvb, pc, pvc)
                        total_trials += len(ops)

                        for val, expr in ops:
                            for t_name, t_val in TARGETS.items():
                                if t_val == 0:
                                    continue
                                rel_err = abs(val - t_val) / abs(t_val)
                                if rel_err < threshold:
                                    matches.append({
                                        "target": t_name,
                                        "target_val": t_val,
                                        "formula": expr,
                                        "formula_val": val,
                                        "error": rel_err,
                                        "error_pct": rel_err * 100,
                                        "category": cat,
                                        "depth": 3,
                                    })

    # 중복 제거 (같은 타겟+공식)
    seen = set()
    unique = []
    for m in matches:
        key = (m["target"], m["formula"])
        if key not in seen:
            seen.add(key)
            unique.append(m)

    # 오차 순 정렬
    unique.sort(key=lambda x: x["error_pct"])

    return unique, total_trials


# ─────────────────────────────────────────
# 텍사스 명사수 검정
# ─────────────────────────────────────────
def texas_sharpshooter(matches, total_trials, n_random=5000):
    """각 발견의 Bonferroni p-value 계산.

    방법:
    1. 같은 연산 형태에 랜덤 상수 2개를 넣어 같은 정밀도로 타겟 맞출 확률 추정
    2. 총 시도 수 x 단일 확률 = Bonferroni p-value
    3. 분류: p<0.01 구조적, 0.01~0.05 약한 증거, >0.05 우연 가능

    Returns:
        list of dict with p_value and verdict added
    """
    rng = np.random.default_rng(42)

    # 각 타겟에 대해 랜덤 히트 확률 추정
    target_hit_probs = {}
    for t_name, t_val in TARGETS.items():
        if t_val == 0:
            continue
        hits = 0
        for _ in range(n_random):
            a = rng.uniform(0.01, 200)
            b = rng.uniform(0.01, 200)
            # 기본 연산 8종 시도
            test_vals = [a + b, a - b, a * b]
            if b != 0:
                test_vals.append(a / b)
            if a > 0 and abs(b) < 20:
                try:
                    test_vals.append(a ** b)
                except (OverflowError, ValueError):
                    pass
            if a > 0 and a != 1 and b > 0:
                try:
                    test_vals.append(np.log(b) / np.log(a))
                except (ValueError, ZeroDivisionError):
                    pass
            if abs(a * b) < 20:
                try:
                    test_vals.append(np.exp(a * b))
                except OverflowError:
                    pass
            if a * b > 0:
                test_vals.append(np.sqrt(a * b))

            for v in test_vals:
                if isinstance(v, (int, float)) and np.isfinite(v) and t_val != 0:
                    if abs(v - t_val) / abs(t_val) < 0.001:
                        hits += 1
                        break

        target_hit_probs[t_name] = max(hits / n_random, 1e-6)

    # Bonferroni 보정
    results = []
    n_significant = 0
    for m in matches:
        p_single = target_hit_probs.get(m["target"], 0.01)
        # 정밀도 보정: 오차가 더 작을수록 확률 더 낮음
        precision_factor = m["error_pct"] / 0.1 if m["error_pct"] > 0 else 0.01
        p_adjusted = min(1.0, p_single * precision_factor * total_trials)

        if p_adjusted < 0.01:
            verdict = "구조적"
            n_significant += 1
        elif p_adjusted < 0.05:
            verdict = "약한 증거"
            n_significant += 1
        else:
            verdict = "우연 가능"

        m_copy = dict(m)
        m_copy["p_value"] = p_adjusted
        m_copy["verdict"] = verdict
        results.append(m_copy)

    return results, n_significant


# ─────────────────────────────────────────
# 출력
# ─────────────────────────────────────────
def print_results(matches, total_trials, threshold, depth, cross_only, top_n, texas=False):
    """결과 ASCII 출력."""

    n_proj = len(PROJECT_CONSTS)
    n_quant = len(QUANTUM_CONSTS)
    n_total = n_proj + n_quant

    print()
    print("=" * 55)
    print(" Quantum Formula Engine v1.0")
    print(f" 상수: {n_proj}(프로젝트) + {n_quant}(양자) = {n_total}개")
    print(f" 연산: {'8종(2개)' if depth < 3 else '8종(2개)+8종(3개)'}, "
          f"조합: ~{total_trials:,}개")
    mode = "교차(A*B)만" if cross_only else "전체"
    print(f" 모드: {mode}, 깊이: {depth}, 임계: {threshold * 100}%")
    print("=" * 55)

    if not matches:
        print()
        print(" 발견 없음.")
        print("=" * 55)
        return

    display = matches[:top_n] if top_n else matches

    print()
    print(f" 발견 (오차 <= {threshold * 100}%): {len(matches)}개"
          + (f", 상위 {top_n}개 표시" if top_n and top_n < len(matches) else ""))
    print(" " + "-" * 53)
    print(f" {'오차%':>7} | {'공식':<28} | {'값':>10} | {'타겟':<10} | 분류")
    print(" " + "-" * 53)

    for m in display:
        err_str = f"{m['error_pct']:.4f}"
        val_str = f"{m['formula_val']:.5f}"
        formula = m["formula"]
        if len(formula) > 28:
            formula = formula[:25] + "..."

        # 등급 표시
        if m["error_pct"] < 0.001:
            star = "**"
        elif m["error_pct"] < 0.01:
            star = "* "
        elif m["error_pct"] < 0.05:
            star = ". "
        else:
            star = "  "

        cat = m.get("category", "?")
        print(f" {star}{err_str:>6} | {formula:<28} | {val_str:>10} | "
              f"{m['target']:<10} | {cat}")

    print(" " + "-" * 53)

    # 텍사스 명사수 검정
    if texas:
        print()
        print(" 텍사스 명사수 검정:")
        texas_results, n_sig = texas_sharpshooter(matches, total_trials)
        n_structural = sum(1 for r in texas_results if r["verdict"] == "구조적")
        n_weak = sum(1 for r in texas_results if r["verdict"] == "약한 증거")
        n_chance = sum(1 for r in texas_results if r["verdict"] == "우연 가능")

        print(f"  총 시도: {total_trials:,}, "
              f"{threshold * 100}% 이내 발견: {len(matches)}개")
        print(f"  Bonferroni 유의: {n_sig}/{len(matches)} (p < 0.05)")
        print(f"   - 구조적 (p<0.01): {n_structural}개")
        print(f"   - 약한 증거 (p<0.05): {n_weak}개")
        print(f"   - 우연 가능 (p>=0.05): {n_chance}개")

        # 상위 구조적 발견 표시
        structural = [r for r in texas_results if r["verdict"] == "구조적"]
        if structural:
            structural.sort(key=lambda x: x["p_value"])
            print()
            print(" 구조적 발견 (p < 0.01):")
            for r in structural[:10]:
                print(f"   p={r['p_value']:.4f} | {r['formula']:<28} -> "
                      f"{r['target']} (err {r['error_pct']:.4f}%)")

    print()
    print("=" * 55)


def save_results(matches, total_trials, threshold, depth):
    """결과를 results/ 폴더에 저장."""
    os.makedirs(RESULTS_DIR, exist_ok=True)
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    path = os.path.join(RESULTS_DIR, "quantum_formula_discovery.md")

    with open(path, "a", encoding="utf-8") as f:
        f.write(f"\n# 양자 공식 탐색 [{now}]\n\n")
        f.write(f"상수 {len(PROJECT_CONSTS) + len(QUANTUM_CONSTS)}개, "
                f"시도 {total_trials:,}, "
                f"발견 {len(matches)}개, "
                f"임계 {threshold * 100}%\n\n")
        f.write(f"| 오차% | 공식 | 값 | 타겟 | 분류 |\n")
        f.write(f"|-------|------|-----|------|------|\n")
        for m in matches[:30]:
            f.write(f"| {m['error_pct']:.4f} | {m['formula']} | "
                    f"{m['formula_val']:.6f} | {m['target']} | "
                    f"{m.get('category', '?')} |\n")
        f.write("\n---\n")

    return path


# ─────────────────────────────────────────
# 메인
# ─────────────────────────────────────────
def main():
    parser = argparse.ArgumentParser(
        description="양자 공식 탐색 엔진 — 양자 무차원 상수 x 프로젝트 상수 DFS",
    )
    parser.add_argument("--threshold", type=float, default=0.001,
                        help="상대 오차 임계값 (기본 0.001 = 0.1%%)")
    parser.add_argument("--depth", type=int, default=2, choices=[2, 3],
                        help="조합 깊이 (기본 2, 3은 느림)")
    parser.add_argument("--cross-only", action="store_true",
                        help="A그룹 x B그룹 교차 조합만 탐색")
    parser.add_argument("--texas", action="store_true",
                        help="텍사스 명사수 검정 포함")
    parser.add_argument("--top", type=int, default=None,
                        help="상위 N개만 출력")

    args = parser.parse_args()

    # 탐색
    matches, total_trials = search(
        depth=args.depth,
        threshold=args.threshold,
        cross_only=args.cross_only,
    )

    # 출력
    print_results(
        matches,
        total_trials,
        threshold=args.threshold,
        depth=args.depth,
        cross_only=args.cross_only,
        top_n=args.top,
        texas=args.texas,
    )

    # 저장
    path = save_results(matches, total_trials, args.threshold, args.depth)
    print(f" -> results/ 저장: {path}")
    print()


if __name__ == "__main__":
    main()
