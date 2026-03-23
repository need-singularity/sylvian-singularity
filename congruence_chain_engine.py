#!/usr/bin/env python3
"""합동 부분군 Gamma_0(N) 강제 연쇄(forcing chain) 체계 분석 엔진

Gamma_0(N)의 핵심 불변량(지수, 커스프 수, 타원점 수, 종수)을 계산하고
N=1..100 범위에서 "강제 연쇄"가 sigma(N), tau(N)과 어떻게 관계하는지 탐색.

사용법:
  python3 congruence_chain_engine.py                    # N=1..100 전체 테이블
  python3 congruence_chain_engine.py --range 1 50       # N=1..50
  python3 congruence_chain_engine.py --detail 6         # N=6 상세 분석
  python3 congruence_chain_engine.py --moonshine        # 문샤인형 N 탐색
"""

import argparse
import math
from collections import defaultdict

# ─────────────────────────────────────────
# 기초 정수론 함수들
# ─────────────────────────────────────────

def factorize(n):
    """n의 소인수분해를 {소수: 지수} 딕셔너리로 반환"""
    if n <= 1:
        return {}
    factors = {}
    d = 2
    while d * d <= n:
        while n % d == 0:
            factors[d] = factors.get(d, 0) + 1
            n //= d
        d += 1
    if n > 1:
        factors[n] = factors.get(n, 0) + 1
    return factors


def divisors(n):
    """n의 모든 약수를 정렬된 리스트로 반환"""
    if n <= 0:
        return []
    divs = []
    for i in range(1, int(math.isqrt(n)) + 1):
        if n % i == 0:
            divs.append(i)
            if i != n // i:
                divs.append(n // i)
    return sorted(divs)


def euler_phi(n):
    """오일러 파이 함수 phi(n)"""
    if n <= 0:
        return 0
    result = n
    facts = factorize(n)
    for p in facts:
        result = result * (p - 1) // p
    return result


def mobius(n):
    """뫼비우스 함수 mu(n)"""
    if n == 1:
        return 1
    facts = factorize(n)
    for p, e in facts.items():
        if e > 1:
            return 0
    return (-1) ** len(facts)


def sigma_k(n, k=1):
    """약수 함수 sigma_k(n) = sum(d^k for d|n)"""
    if n <= 0:
        return 0
    return sum(d ** k for d in divisors(n))


def gcd(a, b):
    """최대공약수"""
    while b:
        a, b = b, a % b
    return a


def lcm(a, b):
    """최소공배수"""
    if a == 0 or b == 0:
        return 0
    return abs(a * b) // gcd(a, b)


def kronecker_symbol(a, n):
    """크로네커 기호 (a/n) — 르장드르 기호의 일반화

    야코비 기호를 확장하여 짝수 및 음수 모듈러스도 처리"""
    if n == 0:
        return 1 if abs(a) == 1 else 0
    if n == 1:
        return 1
    if n == -1:
        return -1 if a < 0 else 1

    # n=2인 경우: (a/2)
    if n == 2:
        if a % 2 == 0:
            return 0
        r = a % 8
        if r == 1 or r == 7:
            return 1
        else:
            return -1

    # 음수 n 처리
    if n < 0:
        return kronecker_symbol(a, -1) * kronecker_symbol(a, -n)

    # 짝수 n 분리: n = 2^s * m (m 홀수)
    s = 0
    m = n
    while m % 2 == 0:
        s += 1
        m //= 2

    # (a/n) = (a/2)^s * (a/m)
    result = kronecker_symbol(a, 2) ** s if s > 0 else 1
    if m == 1:
        return result

    # 야코비 기호 (a/m) — m은 홀수 양수
    return result * jacobi_symbol(a, m)


def jacobi_symbol(a, n):
    """야코비 기호 (a/n) — n은 홀수 양수"""
    if n <= 0 or n % 2 == 0:
        raise ValueError(f"야코비 기호: n={n}은 홀수 양수여야 합니다")
    if n == 1:
        return 1

    a = a % n
    result = 1

    while a != 0:
        # a에서 2의 인수 제거
        while a % 2 == 0:
            a //= 2
            # (2/n) 처리: n mod 8이 3 또는 5이면 부호 반전
            if n % 8 in (3, 5):
                result = -result

        # 이차 상호법칙 적용
        a, n = n, a
        if a % 4 == 3 and n % 4 == 3:
            result = -result
        a = a % n

    if n == 1:
        return result
    return 0


# ─────────────────────────────────────────
# Gamma_0(N) 불변량 계산
# ─────────────────────────────────────────

def gamma0_index(n):
    """[SL(2,Z) : Gamma_0(N)] = N * prod(1 + 1/p) for p|N

    이것은 PSL(2,Z)에서의 지수 mu"""
    if n <= 0:
        return 0
    if n == 1:
        return 1
    facts = factorize(n)
    # mu = N * prod_{p|N} (1 + 1/p)
    # 정수 연산: N * prod((p+1)/p) = prod(p^(e-1) * (p+1))
    result = 1
    for p, e in facts.items():
        result *= (p ** (e - 1)) * (p + 1)
    return result


def gamma0_cusps(n):
    """Gamma_0(N)의 커스프 수 = sum_{d|N} phi(gcd(d, N/d))"""
    if n <= 0:
        return 0
    return sum(euler_phi(gcd(d, n // d)) for d in divisors(n))


def gamma0_elliptic2(n):
    """Gamma_0(N)의 위수 2 타원점 수 e2

    e2 = 0  if 4|N
    e2 = prod_{p|N} (1 + kronecker(-4, p))  otherwise

    여기서 kronecker(-4, p) = kronecker(-1, p) (p 홀수 소수일 때)
    p=2일 때는 별도 처리"""
    if n <= 0:
        return 0
    if n == 1:
        return 1  # SL(2,Z)는 타원점 1개 (i)

    # 4|N이면 e2=0
    if n % 4 == 0:
        return 0

    facts = factorize(n)
    result = 1
    for p, e in facts.items():
        if e >= 2 and p == 2:
            # 4|N 조건은 위에서 이미 처리됨 (2^2 이상)
            return 0
        if p == 2:
            # 2||N (정확히 한 번): (1 + kronecker(-4,2)) = (1 + 0) = 1
            result *= 1
        else:
            # 홀수 소수 p: p^e | N
            if e >= 2:
                return 0
            # p가 정확히 한 번: (1 + kronecker(-1, p))
            leg = kronecker_symbol(-1, p)
            result *= (1 + leg)

    return result


def gamma0_elliptic3(n):
    """Gamma_0(N)의 위수 3 타원점 수 e3

    e3 = 0  if 9|N
    e3 = prod_{p|N} (1 + kronecker(-3, p))  otherwise

    p=3일 때는 별도 처리"""
    if n <= 0:
        return 0
    if n == 1:
        return 1  # SL(2,Z)는 타원점 1개 (rho)

    # 9|N이면 e3=0
    if n % 9 == 0:
        return 0

    facts = factorize(n)
    result = 1
    for p, e in facts.items():
        if p == 3 and e >= 2:
            return 0
        if p == 3:
            # 3||N: (1 + kronecker(-3,3)) = (1 + 0) = 1
            result *= 1
        else:
            if e >= 2:
                return 0
            # 소수 p != 3: (1 + kronecker(-3, p))
            leg = kronecker_symbol(-3, p)
            result *= (1 + leg)

    return result


def gamma0_genus(n):
    """Gamma_0(N)의 종수 g

    g = 1 + mu/12 - e2/4 - e3/3 - c/2

    여기서 mu = 지수, e2 = 위수2 타원점, e3 = 위수3 타원점, c = 커스프 수"""
    mu = gamma0_index(n)
    e2 = gamma0_elliptic2(n)
    e3 = gamma0_elliptic3(n)
    c = gamma0_cusps(n)

    # 유리수 연산으로 정확도 보장
    # g = 1 + mu/12 - e2/4 - e3/3 - c/2
    # 분모 12로 통일: 12 + mu - 3*e2 - 4*e3 - 6*c, 전부 /12
    numerator = 12 + mu - 3 * e2 - 4 * e3 - 6 * c
    # 종수는 반드시 음이 아닌 정수여야 함
    g = numerator // 12
    return g


def first_cusp_form_weight(n):
    """dim S_k(Gamma_0(N)) > 0인 최소 짝수 정수 k를 찾는다

    리만-로흐 공식으로부터:
    dim S_k(Gamma_0(N)) = (k-1)(g-1) + floor(k/4)*e2 + floor(k/3)*e3 + (k/2 - 1)*c
    (k >= 2, 짝수일 때)

    정밀 공식:
    dim S_k = (k-1)(mu/12) - (e2/4)*{k에 의존하는 항} - ...
    실제로는 리만-로흐 정리의 정확한 형태를 사용"""
    mu = gamma0_index(n)
    e2 = gamma0_elliptic2(n)
    e3 = gamma0_elliptic3(n)
    c = gamma0_cusps(n)
    g = gamma0_genus(n)

    for k in range(2, 50, 2):  # 짝수 가중치만
        dim = dim_cusp_forms(k, mu, e2, e3, c, g)
        if dim > 0:
            return k
    return None  # 50 이하에서 못 찾음


def dim_cusp_forms(k, mu, e2, e3, c, g):
    """가중치 k인 커스프 형식의 차원 dim S_k(Gamma_0(N))

    k=2일 때: dim S_2 = g (종수)
    k >= 4 짝수일 때:
      dim S_k = (k-1)(g-1) + floor((k-2)/4)*e2 + floor((k-2)/3)*e3 + (k/2 - 1)*c

    정확한 공식 (Shimura):
      dim S_k = (k-1)(mu/12) - lambda_2(k)*e2 - lambda_3(k)*e3 - c/2  (k>=2 짝수, + 보정)

    여기서는 k=2일 때 g, k>=4일 때 리만-로흐 공식 사용"""
    if k < 2 or k % 2 != 0:
        return 0

    if k == 2:
        return g

    # k >= 4 짝수: 정확한 차원 공식
    # dim S_k(Gamma_0(N)) = (k-1)(g-1) + floor(k/4)*e2_coeff + floor(k/3)*e3_coeff + ...
    # 표준 공식 (Diamond & Shurman):
    # dim S_k = (k-1)(mu/12) - e2 * lambda_2(k) - e3 * lambda_3(k) - c * (1/2)
    #   여기서 lambda_2(k) = 값은 k mod 4에 의존
    #   lambda_3(k) = 값은 k mod 3에 의존

    # lambda_2(k): k mod 4에 따라
    km4 = k % 4
    if km4 == 0:
        lam2 = 1.0 / 4.0
    elif km4 == 2:
        lam2 = 1.0 / 4.0
    else:
        lam2 = 0  # 홀수는 여기 안 옴

    # lambda_3(k): k mod 3에 따라
    km3 = k % 3
    if km3 == 0:
        lam3 = 1.0 / 3.0
    elif km3 == 1:
        lam3 = 1.0 / 3.0
    elif km3 == 2:
        lam3 = 1.0 / 3.0
    else:
        lam3 = 0

    # 일반 차원 공식 (k >= 4 짝수):
    # dim = (k-1)(g-1) + floor(k*e2/4) + floor(k*e3/3) + (k/2 - 1)*c
    # 이것이 아닌 정확한 공식:
    # dim M_k = (k-1)(g-1) + floor(k/4)*e2 + floor(k/3)*e3 + (k/2)*c
    # dim S_k = dim M_k - c  (아이젠슈타인 급수 c개 제거)
    # => dim S_k = (k-1)(g-1) + floor(k/4)*e2 + floor(k/3)*e3 + (k/2 - 1)*c

    dim = (k - 1) * (g - 1) + (k // 4) * e2 + (k // 3) * e3 + (k // 2 - 1) * c
    return max(0, dim)


# ─────────────────────────────────────────
# 강제 연쇄(forcing chain) 분석
# ─────────────────────────────────────────

def isotropy_orders(n):
    """Gamma_0(N)의 등방성 위수 집합

    위수 1 (항등원), 위수 2 (e2 > 0이면), 위수 3 (e3 > 0이면),
    그리고 파라볼릭 원소 (커스프)의 위수는 무한 → lcm에서는 제외"""
    orders = {1}  # 항등원은 항상 존재
    if gamma0_elliptic2(n) > 0:
        orders.add(2)
    if gamma0_elliptic3(n) > 0:
        orders.add(3)
    return orders


def forcing_chain_analysis(n):
    """N에 대한 강제 연쇄 분석

    등방성 위수들의 lcm이 sigma(N) 또는 다른 산술 함수와
    어떤 관계를 갖는지 탐색"""
    orders = isotropy_orders(n)
    iso_lcm = 1
    for o in orders:
        iso_lcm = lcm(iso_lcm, o)

    sig = sigma_k(n, 1)  # sigma_1(N)
    sig0 = sigma_k(n, 0)  # 약수의 수 d(N)
    mu = gamma0_index(n)
    c = gamma0_cusps(n)

    result = {
        'isotropy_orders': sorted(orders),
        'lcm_isotropy': iso_lcm,
        'sigma_1': sig,
        'sigma_0': sig0,
        'index': mu,
        'cusps': c,
        'relations': []
    }

    # 관계 탐색: lcm과 산술 함수 사이
    if iso_lcm > 0:
        if sig % iso_lcm == 0:
            result['relations'].append(f"sigma({n}) = {sig//iso_lcm} * lcm = {sig}")
        if mu % iso_lcm == 0:
            result['relations'].append(f"index = {mu//iso_lcm} * lcm = {mu}")
        # lcm * cusps vs sigma
        prod_lc = iso_lcm * c
        if prod_lc == sig:
            result['relations'].append(f"lcm * cusps = sigma({n}) = {sig} [정확 일치!]")
        elif prod_lc > 0 and sig % prod_lc == 0:
            result['relations'].append(f"sigma({n}) = {sig//prod_lc} * (lcm*cusps)")
        # lcm * sigma_0 vs index
        prod_ld = iso_lcm * sig0
        if prod_ld == mu:
            result['relations'].append(f"lcm * d({n}) = index = {mu} [정확 일치!]")
        # 12와의 관계 (모듈러 형식의 핵심 상수)
        if iso_lcm > 0 and mu % (12 * iso_lcm) == 0:
            result['relations'].append(f"index = {mu//(12*iso_lcm)} * 12 * lcm")

    return result


# ─────────────────────────────────────────
# 출력 포매팅
# ─────────────────────────────────────────

def print_table(n_start, n_end):
    """N=n_start..n_end의 불변량 테이블 출력"""
    # 헤더
    header = (
        f"{'N':>4} | {'mu':>6} | {'cusps':>5} | {'e2':>3} | {'e3':>3} | "
        f"{'genus':>5} | {'1st k':>5} | {'iso_lcm':>7} | {'sigma':>6} | {'특이'}"
    )
    sep = "-" * len(header)

    print("=" * len(header))
    print("  Gamma_0(N) 합동 부분군 불변량 테이블")
    print("  강제 연쇄(forcing chain) 분석")
    print("=" * len(header))
    print(header)
    print(sep)

    # 종수 통계 수집
    genus_0_list = []
    genus_1_list = []
    special_notes = []

    for n in range(n_start, n_end + 1):
        mu = gamma0_index(n)
        c = gamma0_cusps(n)
        e2 = gamma0_elliptic2(n)
        e3 = gamma0_elliptic3(n)
        g = gamma0_genus(n)
        fk = first_cusp_form_weight(n)
        fk_str = str(fk) if fk else "-"

        orders = isotropy_orders(n)
        iso_lcm = 1
        for o in orders:
            iso_lcm = lcm(iso_lcm, o)

        sig = sigma_k(n, 1)

        # 특이 표시
        notes = []
        if g == 0:
            notes.append("g=0")
            genus_0_list.append(n)
        if g == 1:
            notes.append("g=1")
            genus_1_list.append(n)

        # 강제 연쇄 일치 체크
        fc = forcing_chain_analysis(n)
        for rel in fc['relations']:
            if "정확 일치" in rel:
                notes.append("chain!")

        # sigma와 index의 관계
        if mu == sig:
            notes.append("mu=sig")

        note_str = ", ".join(notes) if notes else ""

        print(
            f"{n:>4} | {mu:>6} | {c:>5} | {e2:>3} | {e3:>3} | "
            f"{g:>5} | {fk_str:>5} | {iso_lcm:>7} | {sig:>6} | {note_str}"
        )

    print(sep)
    print()

    # 요약 통계
    print("=" * 60)
    print("  요약 통계")
    print("=" * 60)
    print(f"  종수 0 (유리 모듈러 곡선): {len(genus_0_list)}개")
    if genus_0_list:
        print(f"    N = {genus_0_list}")
    print(f"  종수 1 (타원 곡선):        {len(genus_1_list)}개")
    if genus_1_list:
        print(f"    N = {genus_1_list}")
    print()

    # N=1이 특별한 이유
    print("=" * 60)
    print("  N=1이 특별한 이유 (강제 연쇄 관점)")
    print("=" * 60)
    print("  N=1: Gamma_0(1) = SL(2,Z) — 전체 모듈러 군")
    print(f"    지수 mu = {gamma0_index(1)}")
    print(f"    커스프  = {gamma0_cusps(1)} (유일한 커스프: infinity)")
    print(f"    e2 = {gamma0_elliptic2(1)} (고정점: i)")
    print(f"    e3 = {gamma0_elliptic3(1)} (고정점: rho = e^(2pi*i/3))")
    print(f"    종수 g = {gamma0_genus(1)} (유리 곡선 → j-불변량)")
    print(f"    등방성 위수: {{1, 2, 3}} → lcm = 6")
    print(f"    sigma(1) = 1, sigma(6) = 12")
    print(f"    12 = SL(2,Z)의 '마법 수' — 종수 공식의 분모!")
    print(f"    lcm(1,2,3) = 6 → 첫 번째 완전수")
    print()


def print_detail(n):
    """N에 대한 상세 분석 출력"""
    print("=" * 60)
    print(f"  Gamma_0({n}) 상세 분석")
    print("=" * 60)

    mu = gamma0_index(n)
    c = gamma0_cusps(n)
    e2 = gamma0_elliptic2(n)
    e3 = gamma0_elliptic3(n)
    g = gamma0_genus(n)
    fk = first_cusp_form_weight(n)
    facts = factorize(n)
    divs = divisors(n)

    print(f"\n  N = {n}")
    print(f"  소인수분해: {n} = ", end="")
    if not facts:
        print("1")
    else:
        parts = []
        for p, e in sorted(facts.items()):
            if e == 1:
                parts.append(str(p))
            else:
                parts.append(f"{p}^{e}")
        print(" * ".join(parts))
    print(f"  약수: {divs}")
    print()

    # 불변량
    print("  [불변량]")
    print(f"    지수 mu = [SL(2,Z) : Gamma_0({n})] = {mu}")
    print(f"      = {n} * prod(1 + 1/p) for p|{n}")
    print(f"    커스프 수 c = sum phi(gcd(d, {n}/d)) = {c}")
    print(f"    위수 2 타원점 e2 = {e2}")
    print(f"    위수 3 타원점 e3 = {e3}")
    print(f"    종수 g = 1 + {mu}/12 - {e2}/4 - {e3}/3 - {c}/2 = {g}")
    if fk:
        print(f"    최소 커스프 형식 가중치 k = {fk}")
        print(f"      dim S_{fk}(Gamma_0({n})) > 0")
    else:
        print(f"    최소 커스프 형식 가중치: k > 48 (범위 초과)")
    print()

    # 산술 함수
    sig1 = sigma_k(n, 1)
    sig0 = sigma_k(n, 0)
    phi_n = euler_phi(n)
    print("  [산술 함수]")
    print(f"    sigma_1({n}) = {sig1}")
    print(f"    sigma_0({n}) = d({n}) = {sig0}")
    print(f"    phi({n}) = {phi_n}")
    print(f"    mu({n}) = {mobius(n)}")
    if sig1 == 2 * n:
        print(f"    *** {n}은 완전수! sigma({n}) = 2*{n} ***")
    print()

    # 강제 연쇄
    fc = forcing_chain_analysis(n)
    print("  [강제 연쇄 분석]")
    print(f"    등방성 위수: {fc['isotropy_orders']}")
    print(f"    lcm(등방성 위수) = {fc['lcm_isotropy']}")
    if fc['relations']:
        print("    발견된 관계:")
        for rel in fc['relations']:
            print(f"      -> {rel}")
    else:
        print("    sigma/index와 직접적 정수 관계 없음")
    print()

    # 커스프 상세
    print("  [커스프 분해]")
    print(f"    sum_{{d|{n}}} phi(gcd(d, {n}/d)):")
    for d in divs:
        nd = n // d
        g_val = gcd(d, nd)
        phi_g = euler_phi(g_val)
        print(f"      d={d:>4}, {n}/d={nd:>4}, gcd={g_val:>4}, phi={phi_g:>4}")
    print(f"    합계 = {c}")
    print()

    # 차원 테이블
    print("  [커스프 형식 차원 dim S_k(Gamma_0({0}))]".format(n))
    print(f"    {'k':>4} | {'dim S_k':>8}")
    print(f"    {'-'*4}-+-{'-'*8}")
    for k in range(2, 26, 2):
        dim = dim_cusp_forms(k, mu, e2, e3, c, g)
        marker = " <-- 최소" if k == fk else ""
        print(f"    {k:>4} | {dim:>8}{marker}")
    print()


def print_moonshine(n_start, n_end):
    """문샤인 유형의 N 탐색 — 종수 0이고 특별한 산술 성질을 갖는 N"""
    print("=" * 60)
    print("  문샤인(Moonshine) 유형 탐색")
    print("  종수 0 + 강제 연쇄가 깔끔한 N")
    print("=" * 60)
    print()

    # 몬스터 군과 관련된 알려진 종수 0 레벨들
    known_moonshine = {1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 12, 13, 16, 18, 25}

    genus0_ns = []
    for n in range(n_start, n_end + 1):
        g = gamma0_genus(n)
        if g == 0:
            genus0_ns.append(n)

    print(f"  종수 0인 N (범위 {n_start}..{n_end}): {len(genus0_ns)}개")
    print(f"  N = {genus0_ns}")
    print()

    # 각 종수 0 레벨에 대한 상세
    print(f"  {'N':>4} | {'mu':>5} | {'c':>3} | {'e2':>3} | {'e3':>3} | "
          f"{'lcm':>4} | {'sig':>5} | {'moon':>4} | 비고")
    print(f"  {'-'*4}-+-{'-'*5}-+-{'-'*3}-+-{'-'*3}-+-{'-'*3}-+-"
          f"{'-'*4}-+-{'-'*5}-+-{'-'*4}-+------")

    for n in genus0_ns:
        mu = gamma0_index(n)
        c = gamma0_cusps(n)
        e2 = gamma0_elliptic2(n)
        e3 = gamma0_elliptic3(n)
        orders = isotropy_orders(n)
        iso_lcm = 1
        for o in orders:
            iso_lcm = lcm(iso_lcm, o)
        sig = sigma_k(n, 1)

        moon = "Y" if n in known_moonshine else ""
        notes = []

        # 특별한 성질 체크
        if iso_lcm == 6:
            notes.append("lcm=6(완전)")
        if mu == 12:
            notes.append("mu=12")
        if sig == 2 * n:
            notes.append("완전수!")
        if mu % 12 == 0:
            notes.append(f"mu/12={mu//12}")

        fc = forcing_chain_analysis(n)
        for rel in fc['relations']:
            if "정확 일치" in rel:
                notes.append("chain")

        note_str = ", ".join(notes) if notes else ""
        print(
            f"  {n:>4} | {mu:>5} | {c:>3} | {e2:>3} | {e3:>3} | "
            f"{iso_lcm:>4} | {sig:>5} | {moon:>4} | {note_str}"
        )

    print()

    # 12의 역할 분석
    print("=" * 60)
    print("  12의 역할 — 종수 공식의 분모")
    print("=" * 60)
    print("  종수 공식: g = 1 + mu/12 - e2/4 - e3/3 - c/2")
    print("  12 = lcm(1,2,3,4,6) — 종수 공식에 나타나는 모든 분모의 lcm")
    print("  12 = 2 * sigma(6) — 완전수 6의 약수합의 2배")
    print("  12 = |SL(2,Z)/+-1| 에서 기본 영역의 면적 (4*pi/12 = pi/3)")
    print()
    print("  N=1에서의 강제 연쇄:")
    print("    {1, 2, 3} -> lcm = 6 (첫 번째 완전수)")
    print("    종수 공식 분모 = 12 = 2 * 6")
    print("    sigma(6) = 1+2+3+6 = 12 -> 종수 공식으로 순환!")
    print("    이것이 N=1이 '자기 참조적'인 이유")
    print()


# ─────────────────────────────────────────
# 메인
# ─────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="합동 부분군 Gamma_0(N) 강제 연쇄 분석 엔진"
    )
    parser.add_argument(
        '--range', nargs=2, type=int, default=[1, 100],
        metavar=('N1', 'N2'),
        help='분석 범위 (기본: 1 100)'
    )
    parser.add_argument(
        '--detail', type=int, default=None,
        metavar='N',
        help='단일 N에 대한 상세 분석'
    )
    parser.add_argument(
        '--moonshine', action='store_true',
        help='문샤인 유형 N 탐색 (종수 0 + 특수 성질)'
    )

    args = parser.parse_args()

    if args.detail is not None:
        print_detail(args.detail)
    elif args.moonshine:
        print_moonshine(args.range[0], args.range[1])
    else:
        print_table(args.range[0], args.range[1])


if __name__ == '__main__':
    main()
