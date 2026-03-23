#!/usr/bin/env python3
"""가설 261 심층 분석: 합동 부분군 분류와 강제 연쇄

종수-0 N에 대해 sigma(N), tau(N), phi(N) 계산 및
강제 연쇄 품질 등급(A/B/C/D) 판정.
"""

import math
from congruence_chain_engine import (
    factorize, divisors, euler_phi, sigma_k, mobius,
    gamma0_index, gamma0_cusps, gamma0_elliptic2, gamma0_elliptic3,
    gamma0_genus, isotropy_orders, forcing_chain_analysis, first_cusp_form_weight,
    gcd, lcm
)


def ramanujan_tau(n):
    """라마누잔 tau 함수 (n <= 30 정도까지 정확)
    Delta(q) = q * prod_{n>=1} (1-q^n)^24 의 계수"""
    if n <= 0:
        return 0
    # 급수 전개로 계산
    max_terms = n + 10
    # (1 - q^k)^24 의 전개
    coeffs = [0] * (n + 1)
    coeffs[0] = 1
    for k in range(1, n + 1):
        # (1 - q^k)^24 을 곱함
        new_coeffs = coeffs[:]
        for power in range(1, 25):  # -q^k 의 거듭제곱
            sign = (-1) ** power
            coeff_mult = math.comb(24, power) * sign
            shift = k * power
            if shift > n:
                break
            temp = [0] * (n + 1)
            for j in range(n + 1):
                if coeffs[j] != 0 and j + shift <= n:
                    temp[j + shift] += coeffs[j] * coeff_mult
            for j in range(n + 1):
                new_coeffs[j] += temp[j]
        coeffs = new_coeffs
    # Delta(q) = q * prod(1-q^n)^24, so tau(n) = coeffs[n-1]
    if n - 1 < len(coeffs):
        return coeffs[n - 1]
    return 0


def number_of_divisors(n):
    """약수의 수 d(N) = sigma_0(N)"""
    return sigma_k(n, 0)


def analyze_genus0():
    """종수-0인 모든 N에 대한 심층 분석"""
    genus0 = []
    for n in range(1, 101):
        if gamma0_genus(n) == 0:
            genus0.append(n)

    print("=" * 90)
    print("  [1] 종수-0 N의 산술 함수 종합 테이블")
    print("=" * 90)
    print(f"  {'N':>4} | {'mu':>5} | {'sigma':>5} | {'tau':>8} | {'phi':>5} | "
          f"{'d(N)':>4} | {'mu/sig':>7} | {'mu%12':>5} | {'mu/12':>5}")
    print(f"  {'-'*4}-+-{'-'*5}-+-{'-'*5}-+-{'-'*8}-+-{'-'*5}-+-"
          f"{'-'*4}-+-{'-'*7}-+-{'-'*5}-+-{'-'*5}")

    for n in genus0:
        mu = gamma0_index(n)
        sig = sigma_k(n, 1)
        tau = ramanujan_tau(n)
        phi = euler_phi(n)
        d_n = number_of_divisors(n)
        mu_sig_ratio = f"{mu/sig:.3f}" if sig > 0 else "-"
        mu_mod12 = mu % 12
        mu_div12 = f"{mu/12:.2f}"

        print(f"  {n:>4} | {mu:>5} | {sig:>5} | {tau:>8} | {phi:>5} | "
              f"{d_n:>4} | {mu_sig_ratio:>7} | {mu_mod12:>5} | {mu_div12:>5}")

    return genus0


def analyze_mu_multiples_of_12():
    """mu(N)이 12의 배수인 모든 N (1..100)"""
    print()
    print("=" * 90)
    print("  [2] mu(N)이 12의 배수인 N (= sigma 관련)")
    print("=" * 90)
    results = []
    for n in range(1, 101):
        mu = gamma0_index(n)
        if mu % 12 == 0:
            sig = sigma_k(n, 1)
            g = gamma0_genus(n)
            results.append((n, mu, mu // 12, sig, g))

    print(f"  {'N':>4} | {'mu':>6} | {'mu/12':>5} | {'sigma':>6} | {'genus':>5} | {'mu=sig?':>7}")
    print(f"  {'-'*4}-+-{'-'*6}-+-{'-'*5}-+-{'-'*6}-+-{'-'*5}-+-{'-'*7}")
    for n, mu, md, sig, g in results:
        eq = "YES" if mu == sig else ""
        print(f"  {n:>4} | {mu:>6} | {md:>5} | {sig:>6} | {g:>5} | {eq:>7}")

    print(f"\n  총 {len(results)}개 / 100")
    return results


def analyze_both_elliptic():
    """e2 > 0 AND e3 > 0인 N"""
    print()
    print("=" * 90)
    print("  [3] e2 > 0 AND e3 > 0 (양쪽 타원점 모두 존재)")
    print("=" * 90)
    results = []
    for n in range(1, 101):
        e2 = gamma0_elliptic2(n)
        e3 = gamma0_elliptic3(n)
        if e2 > 0 and e3 > 0:
            mu = gamma0_index(n)
            g = gamma0_genus(n)
            sig = sigma_k(n, 1)
            iso = isotropy_orders(n)
            iso_lcm = 1
            for o in iso:
                iso_lcm = lcm(iso_lcm, o)
            results.append((n, mu, g, e2, e3, iso_lcm, sig))

    print(f"  {'N':>4} | {'mu':>5} | {'g':>3} | {'e2':>3} | {'e3':>3} | "
          f"{'lcm':>4} | {'sigma':>5} | 비고")
    print(f"  {'-'*4}-+-{'-'*5}-+-{'-'*3}-+-{'-'*3}-+-{'-'*3}-+-"
          f"{'-'*4}-+-{'-'*5}-+------")
    for n, mu, g, e2, e3, il, sig in results:
        notes = []
        if il == 6:
            notes.append("lcm=6(완전)")
        if g == 0:
            notes.append("g=0")
        if mu == sig:
            notes.append("mu=sig")
        # N이 squarefree인지
        facts = factorize(n)
        if all(e == 1 for e in facts.values()):
            notes.append("sqfree")
        print(f"  {n:>4} | {mu:>5} | {g:>3} | {e2:>3} | {e3:>3} | "
              f"{il:>4} | {sig:>5} | {', '.join(notes)}")

    print(f"\n  총 {len(results)}개 / 100")
    print(f"  이들의 lcm(isotropy)는 모두 6 = 첫 번째 완전수")
    return results


def analyze_cusp_form_weights():
    """첫 커스프 형식 가중치 패턴"""
    print()
    print("=" * 90)
    print("  [4] 첫 커스프 형식 가중치 k 패턴")
    print("=" * 90)

    weight_groups = {}
    for n in range(1, 101):
        fk = first_cusp_form_weight(n)
        if fk not in weight_groups:
            weight_groups[fk] = []
        weight_groups[fk].append(n)

    for k in sorted(weight_groups.keys(), key=lambda x: x if x else 999):
        ns = weight_groups[k]
        k_str = str(k) if k else ">48"
        print(f"  k = {k_str:>3}: {len(ns):>3}개  N = {ns[:20]}{'...' if len(ns) > 20 else ''}")

    return weight_groups


def forcing_chain_quality():
    """강제 연쇄 품질 등급 판정 (A/B/C/D)"""
    print()
    print("=" * 90)
    print("  [5] 강제 연쇄 품질 등급 (종수-0 N)")
    print("=" * 90)
    print()
    print("  등급 기준:")
    print("    A: lcm(iso) * cusps = sigma(N) 정확 일치 + mu%12=0")
    print("    B: lcm(iso) * d(N) = mu 정확 일치 또는 mu = sigma(N)")
    print("    C: mu%12=0 이고 다른 부분 관계 존재")
    print("    D: 특별한 관계 없음")
    print()

    genus0 = [n for n in range(1, 101) if gamma0_genus(n) == 0]

    print(f"  {'N':>4} | {'mu':>5} | {'c':>3} | {'lcm':>4} | {'sig':>5} | "
          f"{'d(N)':>4} | {'lcm*c':>6} | {'lcm*d':>6} | {'등급':>4} | 근거")
    print(f"  {'-'*4}-+-{'-'*5}-+-{'-'*3}-+-{'-'*4}-+-{'-'*5}-+-"
          f"{'-'*4}-+-{'-'*6}-+-{'-'*6}-+-{'-'*4}-+------")

    grades = {}
    for n in genus0:
        mu = gamma0_index(n)
        c = gamma0_cusps(n)
        sig = sigma_k(n, 1)
        d_n = number_of_divisors(n)
        iso = isotropy_orders(n)
        iso_lcm = 1
        for o in iso:
            iso_lcm = lcm(iso_lcm, o)

        lc = iso_lcm * c
        ld = iso_lcm * d_n

        reasons = []
        grade = "D"

        # A 조건
        if lc == sig and mu % 12 == 0:
            grade = "A"
            reasons.append("lcm*c=sig + mu%12=0")
        elif lc == sig:
            grade = "A"
            reasons.append("lcm*c=sig")
        # B 조건
        elif ld == mu:
            grade = "B"
            reasons.append("lcm*d=mu")
        elif mu == sig:
            if mu % 12 == 0:
                grade = "B"
                reasons.append("mu=sig + mu%12=0")
            else:
                grade = "B"
                reasons.append("mu=sig")
        # C 조건
        elif mu % 12 == 0:
            grade = "C"
            reasons.append(f"mu/12={mu//12}")
            if sig % iso_lcm == 0:
                reasons.append(f"sig/{iso_lcm}={sig//iso_lcm}")
        # D
        else:
            reasons.append("관계 미약")

        grades[n] = grade

        print(f"  {n:>4} | {mu:>5} | {c:>3} | {iso_lcm:>4} | {sig:>5} | "
              f"{d_n:>4} | {lc:>6} | {ld:>6} | {grade:>4} | {'; '.join(reasons)}")

    # 등급 통계
    print()
    for g in ['A', 'B', 'C', 'D']:
        ns = [n for n, gr in grades.items() if gr == g]
        print(f"  등급 {g}: {len(ns)}개 — N = {ns}")

    return grades


def sigma_mu_relation_deep():
    """sigma(N)과 mu(N)의 깊은 관계 탐색"""
    print()
    print("=" * 90)
    print("  [6] sigma(N)과 mu(N) 관계의 깊은 분석")
    print("=" * 90)
    print()
    print("  mu(N) = N * prod_{p|N} (1 + 1/p)")
    print("  sigma(N) = prod_{p^e || N} (p^{e+1} - 1)/(p - 1)")
    print("  squarefree N이면: mu(N) = sigma(N) (정확히!)")
    print()

    sqfree_match = 0
    sqfree_total = 0
    non_sqfree_match = 0
    non_sqfree_total = 0

    for n in range(1, 101):
        mu = gamma0_index(n)
        sig = sigma_k(n, 1)
        facts = factorize(n)
        is_sqfree = all(e == 1 for e in facts.values()) if facts else True

        if is_sqfree:
            sqfree_total += 1
            if mu == sig:
                sqfree_match += 1
        else:
            non_sqfree_total += 1
            if mu == sig:
                non_sqfree_match += 1

    print(f"  Squarefree N (1..100):     {sqfree_total}개, mu=sigma 일치: {sqfree_match}개")
    print(f"  Non-squarefree N (1..100): {non_sqfree_total}개, mu=sigma 일치: {non_sqfree_match}개")
    print()

    # 증명
    print("  [증명] N이 squarefree이면 mu(N) = sigma(N)")
    print("    N = p1 * p2 * ... * pk (각 pi 서로 다른 소수)")
    print("    mu(N) = N * prod(1 + 1/pi) = prod(pi) * prod(1 + 1/pi)")
    print("          = prod(pi + 1)")
    print("    sigma(N) = prod(1 + pi) = prod(pi + 1)  [각 소수의 약수합]")
    print("    따라서 mu(N) = sigma(N).  QED")
    print()
    print("  이것은 순수 산술 정리 (골든존 무관, 영원히 참) [Green]")


def main():
    genus0 = analyze_genus0()
    mu12_results = analyze_mu_multiples_of_12()
    both_elliptic = analyze_both_elliptic()
    weight_groups = analyze_cusp_form_weights()
    grades = forcing_chain_quality()
    sigma_mu_relation_deep()

    # 최종 요약
    print()
    print("=" * 90)
    print("  [최종 요약] 가설 261 계산 결과")
    print("=" * 90)
    print()
    print(f"  종수-0 N (1..100): {len(genus0)}개 = {genus0}")
    print(f"  mu%12=0인 N: {len(mu12_results)}개")
    print(f"  e2>0 AND e3>0인 N: {len(both_elliptic)}개 (모두 lcm=6)")
    print()
    print("  핵심 발견:")
    print("    1. squarefree N <=> mu(N) = sigma(N) [순수 산술 정리, 증명됨]")
    print("    2. e2>0 AND e3>0 <=> lcm(isotropy) = 6 = 첫 번째 완전수")
    print("    3. N=1, 13 만이 종수-0이면서 lcm=6 (양쪽 타원점 + g=0)")
    print("    4. 종수-0이고 mu%12=0인 N = {6, 8, 9, 12, 16, 18} — 합성수만")
    print("    5. 강제 연쇄 등급 A (가장 깨끗): lcm*cusps = sigma(N)")


if __name__ == '__main__':
    main()
