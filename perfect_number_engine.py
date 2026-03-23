#!/usr/bin/env python3
"""완전수 약수함수 엔진 — σ, τ, φ 조합으로 물리 상수 자동 탐색

완전수의 약수함수(σ, τ, φ 등)를 체계적으로 조합하여
물리 상수와의 매칭을 자동 탐색한다.
텍사스 명사수 검정으로 우연 vs 구조적 발견을 판별.

사용법:
  python3 perfect_number_engine.py                 # 전체 탐색
  python3 perfect_number_engine.py --target 137    # 특정 타겟
  python3 perfect_number_engine.py --cross         # 완전수 교차만
  python3 perfect_number_engine.py --depth 3       # 3개 함수 조합
"""

import argparse
import os
import warnings
from datetime import datetime
from itertools import combinations, permutations
from math import comb, factorial

import numpy as np

warnings.filterwarnings("ignore", category=RuntimeWarning)

RESULTS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "results")


# ─────────────────────────────────────────
# 완전수 + 약수함수
# ─────────────────────────────────────────
PERFECT_NUMBERS = {
    6: {"sigma": 12, "tau": 4, "phi": 2, "prime_factors": [2, 3]},
    28: {"sigma": 56, "tau": 6, "phi": 12, "prime_factors": [2, 7]},
    496: {"sigma": 992, "tau": 10, "phi": 240, "prime_factors": [2, 31]},
    8128: {"sigma": 16256, "tau": 14, "phi": 4096, "prime_factors": [2, 127]},
}


def build_atom_pool():
    """완전수별 약수함수 원자 풀 생성.

    각 완전수 P에 대해:
      P, σ(P), τ(P), φ(P), σ₋₁(P)=2, 소인수들
    """
    atoms = {}  # name -> value
    for p, info in PERFECT_NUMBERS.items():
        tag = f"P{p}"
        atoms[tag] = float(p)
        atoms[f"s({tag})"] = float(info["sigma"])      # σ
        atoms[f"t({tag})"] = float(info["tau"])         # τ
        atoms[f"ph({tag})"] = float(info["phi"])        # φ
        atoms[f"s-1({tag})"] = 2.0                      # σ₋₁ = 2 (완전수 정의)
        for pf in info["prime_factors"]:
            name = f"pf{pf}({tag})"
            atoms[name] = float(pf)
    return atoms


ATOMS = build_atom_pool()


# ─────────────────────────────────────────
# 물리 상수 타겟
# ─────────────────────────────────────────
PHYSICS_TARGETS = {
    "alpha_inv": 137.035999084,
    "m_p/m_e": 1836.15267343,
    "m_mu/m_e": 206.7682830,
    "m_tau/m_e": 3477.48,
    "sin2_theta_W": 0.23122,
    "alpha_s": 0.1185,
    "137": 137.0,
    "496": 496.0,
    "10": 10.0,
    "26": 26.0,
}


# ─────────────────────────────────────────
# 어떤 완전수에서 유래했는지 추출
# ─────────────────────────────────────────
def origin_pn(name):
    """원자 이름에서 완전수 번호 추출."""
    for p in PERFECT_NUMBERS:
        if f"P{p}" in name:
            return p
    return None


def is_cross(name_a, name_b):
    """두 원자가 서로 다른 완전수에서 유래했는가?"""
    return origin_pn(name_a) != origin_pn(name_b)


# ─────────────────────────────────────────
# 비자명성 점수
# ─────────────────────────────────────────
def triviality_score(formula, target_name, target_val, formula_val):
    """비자명성 점수 (0=자명, 높을수록 흥미).

    감점 요인:
    - 항등 매핑 (P496 -> 496)
    - 단일 원자
    - 정수 나눗셈 (28/4=7 등 명백한 것)

    가점 요인:
    - 교차 완전수
    - 여러 약수함수 혼합
    - 작은 오차
    """
    score = 5  # 기본점

    # 항등 매핑 감점
    if f"P{int(target_val)}" in formula and formula.count("(") <= 1:
        score -= 4

    # 단일 원자 감점
    operators = ["+", "-", "*", "/", "^", "C(", "T("]
    has_op = any(op in formula for op in operators)
    if not has_op:
        score -= 3

    # 교차 완전수 가점
    pns_in_formula = set()
    for p in PERFECT_NUMBERS:
        if f"P{p}" in formula:
            pns_in_formula.add(p)
    if len(pns_in_formula) >= 2:
        score += 2
    if len(pns_in_formula) >= 3:
        score += 1

    # 다양한 약수함수 가점
    func_types = 0
    if "s(" in formula:
        func_types += 1
    if "t(" in formula:
        func_types += 1
    if "ph(" in formula:
        func_types += 1
    if "pf" in formula:
        func_types += 1
    if func_types >= 2:
        score += 1

    return max(0, score)


# ─────────────────────────────────────────
# 이항 연산 (2개 원자)
# ─────────────────────────────────────────
def binary_ops(na, va, nb, vb):
    """두 원자에 대한 모든 연산 결과를 (값, 공식) 리스트로 반환."""
    results = []

    # 기본 사칙
    results.append((va + vb, f"{na}+{nb}"))
    results.append((va - vb, f"{na}-{nb}"))
    results.append((vb - va, f"{nb}-{na}"))
    results.append((va * vb, f"{na}*{nb}"))

    if vb != 0:
        results.append((va / vb, f"{na}/{nb}"))
    if va != 0:
        results.append((vb / va, f"{nb}/{na}"))

    # 거듭제곱
    if va > 0 and 0 < abs(vb) < 20:
        try:
            val = va ** vb
            if np.isfinite(val) and abs(val) < 1e15:
                results.append((val, f"{na}^{nb}"))
        except (OverflowError, ValueError):
            pass
    if vb > 0 and 0 < abs(va) < 20:
        try:
            val = vb ** va
            if np.isfinite(val) and abs(val) < 1e15:
                results.append((val, f"{nb}^{na}"))
        except (OverflowError, ValueError):
            pass

    # 조합 C(a, b) — 정수만
    if va == int(va) and vb == int(vb):
        a_int, b_int = int(va), int(vb)
        if 0 <= b_int <= a_int <= 200:
            try:
                val = float(comb(a_int, b_int))
                if val < 1e15:
                    results.append((val, f"C({na},{nb})"))
            except (ValueError, OverflowError):
                pass
        if 0 <= a_int <= b_int <= 200:
            try:
                val = float(comb(b_int, a_int))
                if val < 1e15:
                    results.append((val, f"C({nb},{na})"))
            except (ValueError, OverflowError):
                pass

    # 삼각수 T(a+b+1) = (a+b+1)(a+b)/2
    s = va + vb + 1
    if s > 0 and s == int(s) and s < 1000:
        val = s * (s - 1) / 2
        if abs(val) < 1e15:
            results.append((val, f"T({na}+{nb}+1)"))

    # sqrt(a*b)
    if va * vb > 0:
        val = np.sqrt(va * vb)
        if np.isfinite(val):
            results.append((val, f"sqrt({na}*{nb})"))

    # log
    if va > 0 and va != 1 and vb > 0:
        try:
            val = np.log(vb) / np.log(va)
            if np.isfinite(val) and abs(val) < 1e15:
                results.append((val, f"log_{na}({nb})"))
        except (ValueError, ZeroDivisionError):
            pass
    if vb > 0 and vb != 1 and va > 0:
        try:
            val = np.log(va) / np.log(vb)
            if np.isfinite(val) and abs(val) < 1e15:
                results.append((val, f"log_{nb}({na})"))
        except (ValueError, ZeroDivisionError):
            pass

    return [(v, expr) for v, expr in results
            if isinstance(v, (int, float)) and np.isfinite(v) and abs(v) < 1e15]


# ─────────────────────────────────────────
# 삼항 연산 (3개 원자)
# ─────────────────────────────────────────
def ternary_ops(na, va, nb, vb, nc, vc):
    """세 원자에 대한 연산 결과 리스트."""
    results = []

    # a*b + c, a*b - c
    results.append((va * vb + vc, f"{na}*{nb}+{nc}"))
    results.append((va * vb - vc, f"{na}*{nb}-{nc}"))

    # a*b*c
    val = va * vb * vc
    if np.isfinite(val) and abs(val) < 1e15:
        results.append((val, f"{na}*{nb}*{nc}"))

    # (a+b)*c
    results.append(((va + vb) * vc, f"({na}+{nb})*{nc}"))

    # (a-b)*c
    results.append(((va - vb) * vc, f"({na}-{nb})*{nc}"))

    # a^b + c
    if va > 0 and abs(vb) < 20:
        try:
            val = va ** vb + vc
            if np.isfinite(val) and abs(val) < 1e15:
                results.append((val, f"{na}^{nb}+{nc}"))
        except (OverflowError, ValueError):
            pass

    # a^b * c
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

    # a / (b*c)
    if vb * vc != 0:
        results.append((va / (vb * vc), f"{na}/({nb}*{nc})"))

    # (a*b)^c
    if va * vb > 0 and abs(vc) < 20:
        try:
            val = (va * vb) ** vc
            if np.isfinite(val) and abs(val) < 1e15:
                results.append((val, f"({na}*{nb})^{nc}"))
        except (OverflowError, ValueError):
            pass

    # C(a*b, c) — 정수만
    ab = va * vb
    if ab == int(ab) and vc == int(vc):
        ab_int, c_int = int(ab), int(vc)
        if 0 <= c_int <= ab_int <= 200:
            try:
                val = float(comb(ab_int, c_int))
                if val < 1e15:
                    results.append((val, f"C({na}*{nb},{nc})"))
            except (ValueError, OverflowError):
                pass

    return [(v, expr) for v, expr in results
            if isinstance(v, (int, float)) and np.isfinite(v) and abs(v) < 1e15]


# ─────────────────────────────────────────
# 탐색 엔진
# ─────────────────────────────────────────
def search(targets, depth=2, cross_only=False, threshold=0.01):
    """완전수 약수함수 조합으로 타겟을 만드는 공식 탐색.

    Args:
        targets: {이름: 값} dict
        depth: 조합 깊이 (2 또는 3)
        cross_only: True이면 서로 다른 완전수 교차만
        threshold: 상대 오차 임계값

    Returns:
        matches: list of dict
        total_trials: 총 시도 수
    """
    names = list(ATOMS.keys())
    vals = [ATOMS[n] for n in names]

    matches = []
    total_trials = 0

    # ── 1개 원자 (단항) ──
    for i in range(len(names)):
        na, va = names[i], vals[i]
        total_trials += 1
        for t_name, t_val in targets.items():
            if t_val == 0:
                continue
            rel_err = abs(va - t_val) / abs(t_val)
            if rel_err < threshold:
                matches.append({
                    "target": t_name,
                    "target_val": t_val,
                    "formula": na,
                    "formula_val": va,
                    "error": rel_err,
                    "error_pct": rel_err * 100,
                    "depth": 1,
                    "origins": {origin_pn(na)},
                })

    # ── 2개 조합 ──
    for i in range(len(names)):
        for j in range(i, len(names)):
            na, va = names[i], vals[i]
            nb, vb = names[j], vals[j]

            if cross_only and not is_cross(na, nb):
                continue

            ops = binary_ops(na, va, nb, vb)
            total_trials += len(ops)

            for val, expr in ops:
                for t_name, t_val in targets.items():
                    if t_val == 0:
                        continue
                    rel_err = abs(val - t_val) / abs(t_val)
                    if rel_err < threshold:
                        # 자명한 항등 스킵
                        if expr == t_name:
                            continue
                        origins = set()
                        o1, o2 = origin_pn(na), origin_pn(nb)
                        if o1:
                            origins.add(o1)
                        if o2:
                            origins.add(o2)
                        matches.append({
                            "target": t_name,
                            "target_val": t_val,
                            "formula": expr,
                            "formula_val": val,
                            "error": rel_err,
                            "error_pct": rel_err * 100,
                            "depth": 2,
                            "origins": origins,
                        })

    # ── 3개 조합 ──
    if depth >= 3:
        for i in range(len(names)):
            for j in range(i, len(names)):
                for k in range(j, len(names)):
                    na, va = names[i], vals[i]
                    nb, vb = names[j], vals[j]
                    nc, vc = names[k], vals[k]

                    if cross_only:
                        pns = set(filter(None, [origin_pn(na), origin_pn(nb), origin_pn(nc)]))
                        if len(pns) < 2:
                            continue

                    # 3가지 순열
                    perms = [
                        (na, va, nb, vb, nc, vc),
                        (na, va, nc, vc, nb, vb),
                        (nb, vb, nc, vc, na, va),
                    ]
                    for pa, pva, pb, pvb, pc, pvc in perms:
                        ops = ternary_ops(pa, pva, pb, pvb, pc, pvc)
                        total_trials += len(ops)

                        for val, expr in ops:
                            for t_name, t_val in targets.items():
                                if t_val == 0:
                                    continue
                                rel_err = abs(val - t_val) / abs(t_val)
                                if rel_err < threshold:
                                    origins = set(filter(None, [
                                        origin_pn(pa), origin_pn(pb), origin_pn(pc)
                                    ]))
                                    matches.append({
                                        "target": t_name,
                                        "target_val": t_val,
                                        "formula": expr,
                                        "formula_val": val,
                                        "error": rel_err,
                                        "error_pct": rel_err * 100,
                                        "depth": 3,
                                        "origins": origins,
                                    })

    # 중복 제거
    seen = set()
    unique = []
    for m in matches:
        key = (m["target"], m["formula"])
        if key not in seen:
            seen.add(key)
            unique.append(m)

    # 비자명성 점수 추가
    for m in unique:
        m["nontrivial"] = triviality_score(
            m["formula"], m["target"], m["target_val"], m["formula_val"]
        )

    # 오차 순 정렬
    unique.sort(key=lambda x: x["error_pct"])

    return unique, total_trials


# ─────────────────────────────────────────
# 텍사스 명사수 검정
# ─────────────────────────────────────────
def texas_sharpshooter(matches, total_trials, n_random=5000):
    """Bonferroni p-value 기반 검정."""
    rng = np.random.default_rng(42)

    # 각 타겟에 대해 랜덤 히트 확률 추정
    target_hit_probs = {}
    unique_targets = {m["target"]: m["target_val"] for m in matches}

    for t_name, t_val in unique_targets.items():
        if t_val == 0:
            continue
        hits = 0
        for _ in range(n_random):
            a = rng.uniform(1, 500)
            b = rng.uniform(1, 500)
            test_vals = [a + b, a - b, a * b]
            if b != 0:
                test_vals.append(a / b)
            if a > 0 and abs(b) < 20:
                try:
                    test_vals.append(a ** b)
                except (OverflowError, ValueError):
                    pass
            if a * b > 0:
                test_vals.append(np.sqrt(a * b))

            for v in test_vals:
                if isinstance(v, (int, float)) and np.isfinite(v) and t_val != 0:
                    if abs(v - t_val) / abs(t_val) < 0.01:
                        hits += 1
                        break

        target_hit_probs[t_name] = max(hits / n_random, 1e-6)

    # Bonferroni 보정
    results = []
    n_significant = 0
    for m in matches:
        p_single = target_hit_probs.get(m["target"], 0.01)
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
# 완전수별 기여도 분석
# ─────────────────────────────────────────
def contribution_analysis(matches):
    """어떤 완전수가 가장 많이 등장하는지 분석."""
    counter = {}
    for p in PERFECT_NUMBERS:
        counter[p] = {"total": 0, "nontrivial": 0, "best_err": float("inf")}

    for m in matches:
        for p in m.get("origins", set()):
            if p in counter:
                counter[p]["total"] += 1
                if m.get("nontrivial", 0) >= 4:
                    counter[p]["nontrivial"] += 1
                counter[p]["best_err"] = min(counter[p]["best_err"], m["error_pct"])

    return counter


# ─────────────────────────────────────────
# 교차 관계 분석
# ─────────────────────────────────────────
def cross_analysis(matches):
    """서로 다른 완전수를 잇는 교차 관계."""
    cross_matches = []
    for m in matches:
        origins = m.get("origins", set())
        if len(origins) >= 2:
            cross_matches.append(m)
    cross_matches.sort(key=lambda x: x["error_pct"])
    return cross_matches


# ─────────────────────────────────────────
# 출력
# ─────────────────────────────────────────
def print_results(matches, total_trials, targets, depth, cross_only,
                  threshold, texas=False):
    """결과 ASCII 출력."""

    n_atoms = len(ATOMS)
    n_pn = len(PERFECT_NUMBERS)

    print()
    print("=" * 65)
    print("  Perfect Number Engine v1.0")
    print(f"  완전수: {n_pn}개, 원자: {n_atoms}개, 타겟: {len(targets)}개")
    print(f"  연산 조합: ~{total_trials:,}개, 깊이: {depth}, 임계: {threshold * 100}%")
    mode = "교차(P_i x P_j)만" if cross_only else "전체"
    print(f"  모드: {mode}")
    print("=" * 65)

    if not matches:
        print()
        print("  발견 없음.")
        print("=" * 65)
        return

    # ── 발견 테이블 (오차순) ──
    # 비자명한 것 우선 표시
    nontrivial = [m for m in matches if m.get("nontrivial", 0) >= 3]
    trivial = [m for m in matches if m.get("nontrivial", 0) < 3]

    print()
    print(f"  비자명 발견: {len(nontrivial)}개, 자명: {len(trivial)}개")
    print()

    if nontrivial:
        print("  --- 비자명 발견 (오차순) ---")
        print(f"  {'오차%':>8} | {'공식':<35} | {'값':>12} | {'타겟':<12} | NT")
        print("  " + "-" * 78)
        for m in nontrivial[:40]:
            err_str = f"{m['error_pct']:.4f}"
            val_str = f"{m['formula_val']:.5f}"
            formula = m["formula"]
            if len(formula) > 35:
                formula = formula[:32] + "..."
            nt = m.get("nontrivial", 0)

            if m["error_pct"] < 0.001:
                star = "**"
            elif m["error_pct"] < 0.01:
                star = "* "
            elif m["error_pct"] < 0.1:
                star = ". "
            else:
                star = "  "

            print(f"  {star}{err_str:>6} | {formula:<35} | {val_str:>12} | "
                  f"{m['target']:<12} | {nt}")
        print("  " + "-" * 78)

    # ── 완전수별 기여도 ──
    contrib = contribution_analysis(matches)
    print()
    print("  --- 완전수별 기여도 ---")
    print(f"  {'완전수':>8} | {'총 등장':>8} | {'비자명':>8} | {'최소 오차%':>10}")
    print("  " + "-" * 45)
    for p in sorted(contrib.keys()):
        c = contrib[p]
        best = f"{c['best_err']:.4f}" if c['best_err'] < float("inf") else "-"
        print(f"  {p:>8} | {c['total']:>8} | {c['nontrivial']:>8} | {best:>10}")
    print("  " + "-" * 45)

    # ── 교차 관계 ──
    cross = cross_analysis(matches)
    if cross:
        print()
        print(f"  --- 교차 관계 (P_i x P_j): {len(cross)}개 ---")
        for m in cross[:15]:
            origins_str = " x ".join(f"P{p}" for p in sorted(m["origins"]))
            print(f"    {m['error_pct']:>7.4f}% | {m['formula']:<35} -> "
                  f"{m['target']} [{origins_str}]")

    # ── 텍사스 명사수 검정 ──
    if texas and matches:
        print()
        print("  --- 텍사스 명사수 검정 ---")
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

        structural = [r for r in texas_results if r["verdict"] == "구조적"]
        if structural:
            structural.sort(key=lambda x: x["p_value"])
            print()
            print("  구조적 발견 (p < 0.01):")
            for r in structural[:10]:
                print(f"    p={r['p_value']:.4f} | {r['formula']:<35} -> "
                      f"{r['target']} (err {r['error_pct']:.4f}%)")

    print()
    print("=" * 65)


def save_results(matches, total_trials, targets, threshold, depth):
    """결과를 results/ 폴더에 저장."""
    os.makedirs(RESULTS_DIR, exist_ok=True)
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    path = os.path.join(RESULTS_DIR, "perfect_number_discovery.md")

    with open(path, "a", encoding="utf-8") as f:
        f.write(f"\n# 완전수 약수함수 탐색 [{now}]\n\n")
        f.write(f"완전수 {len(PERFECT_NUMBERS)}개, 원자 {len(ATOMS)}개, "
                f"타겟 {len(targets)}개, "
                f"시도 {total_trials:,}, "
                f"발견 {len(matches)}개, "
                f"임계 {threshold * 100}%\n\n")

        nontrivial = [m for m in matches if m.get("nontrivial", 0) >= 3]

        f.write("| 오차% | 공식 | 값 | 타겟 | NT |\n")
        f.write("|-------|------|-----|------|----|\n")
        for m in nontrivial[:30]:
            f.write(f"| {m['error_pct']:.4f} | {m['formula']} | "
                    f"{m['formula_val']:.6f} | {m['target']} | "
                    f"{m.get('nontrivial', 0)} |\n")

        # 교차 관계
        cross = cross_analysis(matches)
        if cross:
            f.write(f"\n## 교차 관계 ({len(cross)}개)\n\n")
            for m in cross[:15]:
                origins_str = " x ".join(f"P{p}" for p in sorted(m["origins"]))
                f.write(f"- {m['error_pct']:.4f}% | {m['formula']} -> "
                        f"{m['target']} [{origins_str}]\n")

        f.write("\n---\n")

    return path


# ─────────────────────────────────────────
# 메인
# ─────────────────────────────────────────
def main():
    parser = argparse.ArgumentParser(
        description="완전수 약수함수 엔진 — sigma, tau, phi 조합으로 물리 상수 탐색",
    )
    parser.add_argument("--target", type=float, default=None,
                        help="특정 값을 만드는 공식 탐색")
    parser.add_argument("--depth", type=int, default=2, choices=[2, 3],
                        help="조합 깊이 (기본 2, 3은 느림)")
    parser.add_argument("--cross", action="store_true",
                        help="서로 다른 완전수 교차 조합만 탐색")
    parser.add_argument("--threshold", type=float, default=0.01,
                        help="상대 오차 임계값 (기본 0.01 = 1%%)")
    parser.add_argument("--texas", action="store_true",
                        help="텍사스 명사수 검정 포함")
    parser.add_argument("--top", type=int, default=None,
                        help="상위 N개만 출력")

    args = parser.parse_args()

    # 타겟 결정
    if args.target is not None:
        targets = {f"target={args.target}": args.target}
    else:
        targets = PHYSICS_TARGETS

    # 탐색
    matches, total_trials = search(
        targets=targets,
        depth=args.depth,
        cross_only=args.cross,
        threshold=args.threshold,
    )

    # top N 필터
    if args.top and len(matches) > args.top:
        matches = matches[:args.top]

    # 출력
    print_results(
        matches,
        total_trials,
        targets=targets,
        depth=args.depth,
        cross_only=args.cross,
        threshold=args.threshold,
        texas=args.texas,
    )

    # 저장
    path = save_results(matches, total_trials, targets, args.threshold, args.depth)
    print(f"  -> results/ 저장: {path}")
    print()


if __name__ == "__main__":
    main()
