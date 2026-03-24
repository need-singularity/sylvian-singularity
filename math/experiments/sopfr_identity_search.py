#!/usr/bin/env python3
"""Ralph 308: sopfr 관련 새 특성화 탐색 (순수 수학 DFS)

기존 발견:
  sopfr(n) = n-1 ⟺ n=6 (증명됨, #49)
  sopfr·ω = σ+φ-τ, n>2 ⟺ n=6 (#53)

탐색 방향:
  1. sopfr과 다른 산술함수의 새 조합
  2. sopfr의 제곱, 거듭제곱 관계
  3. sopfr과 약수합/토션트의 비율
  4. sopfr 기반 특성화를 완전수 28에서 검증
"""

import math
from sympy import factorint, divisors, totient, divisor_sigma, primeomega, primefactors
from collections import defaultdict


def sopfr(n):
    """Sum of prime factors with repetition."""
    if n <= 1:
        return 0
    s = 0
    for p, a in factorint(n).items():
        s += p * a
    return s


def sopf(n):
    """Sum of distinct prime factors."""
    if n <= 1:
        return 0
    return sum(primefactors(n))


def omega(n):
    """Number of distinct prime factors."""
    if n <= 1:
        return 0
    return len(primefactors(n))


def bigomega(n):
    """Number of prime factors with repetition."""
    return primeomega(n)


def rad(n):
    """Radical: product of distinct prime factors."""
    if n <= 1:
        return n
    r = 1
    for p in primefactors(n):
        r *= p
    return r


def tau(n):
    return len(divisors(n))


def sigma(n):
    return divisor_sigma(n, 1)


def phi(n):
    return totient(n)


def search_sopfr_identities(limit=10000):
    """sopfr과 다른 함수의 조합으로 n=6 특성화 탐색."""
    print("=" * 70)
    print("sopfr 기반 새 특성화 탐색 (n <= 10000)")
    print("=" * 70)

    # 함수 목록
    funcs = {
        'sigma': sigma,
        'phi': phi,
        'tau': tau,
        'omega': omega,
        'Omega': bigomega,
        'sopfr': sopfr,
        'sopf': sopf,
        'rad': rad,
    }

    # 미리 계산
    cache = {}
    for n in range(1, limit + 1):
        cache[n] = {name: f(n) for name, f in funcs.items()}
        cache[n]['n'] = n

    results = []

    # 패턴 1: sopfr(n) op f(n) = g(n) for n=6, 찾기
    print("\n--- 패턴 1: sopfr(n) * f(n) = g(n) (곱셈적) ---")
    for f_name in ['sigma', 'phi', 'tau', 'omega', 'Omega', 'rad']:
        for g_name in ['sigma', 'phi', 'tau', 'omega', 'Omega', 'rad', 'n']:
            # sopfr * f = g at n=6?
            lhs_6 = cache[6]['sopfr'] * cache[6][f_name]
            rhs_6 = cache[6][g_name] if g_name != 'n' else 6

            if lhs_6 == rhs_6 and lhs_6 != 0:
                # 다른 n에서도 성립하는지?
                solutions = []
                for n in range(2, limit + 1):
                    lhs = cache[n]['sopfr'] * cache[n][f_name]
                    rhs = cache[n][g_name] if g_name != 'n' else n
                    if lhs == rhs:
                        solutions.append(n)

                if len(solutions) <= 5:
                    print(f"  sopfr*{f_name} = {g_name}: solutions = {solutions}")
                    results.append(('sopfr*' + f_name, g_name, solutions))

    # 패턴 2: sopfr(n) + f(n) = g(n)
    print("\n--- 패턴 2: sopfr(n) + f(n) = g(n) (가법적) ---")
    for f_name in ['sigma', 'phi', 'tau', 'omega', 'Omega', 'rad']:
        for g_name in ['sigma', 'phi', 'tau', 'omega', 'Omega', 'rad', 'n']:
            lhs_6 = cache[6]['sopfr'] + cache[6][f_name]
            rhs_6 = cache[6][g_name] if g_name != 'n' else 6

            if lhs_6 == rhs_6:
                solutions = []
                for n in range(2, limit + 1):
                    lhs = cache[n]['sopfr'] + cache[n][f_name]
                    rhs = cache[n][g_name] if g_name != 'n' else n
                    if lhs == rhs:
                        solutions.append(n)

                if len(solutions) <= 5:
                    print(f"  sopfr+{f_name} = {g_name}: solutions = {solutions}")
                    results.append(('sopfr+' + f_name, g_name, solutions))

    # 패턴 3: sopfr(n)^k = f(n) 거듭제곱
    print("\n--- 패턴 3: sopfr(n)^k = f(n) ---")
    for k in [2, 3]:
        for f_name in ['sigma', 'phi', 'tau', 'n']:
            lhs_6 = cache[6]['sopfr'] ** k
            rhs_6 = cache[6][f_name] if f_name != 'n' else 6

            if lhs_6 == rhs_6:
                solutions = []
                for n in range(2, limit + 1):
                    lhs = cache[n]['sopfr'] ** k
                    rhs = cache[n][f_name] if f_name != 'n' else n
                    if lhs == rhs:
                        solutions.append(n)

                if len(solutions) <= 10:
                    print(f"  sopfr^{k} = {f_name}: solutions = {solutions}")
                    results.append((f'sopfr^{k}', f_name, solutions))

    # 패턴 4: f(sopfr(n)) = g(n) 합성
    print("\n--- 패턴 4: f(sopfr(n)) = g(n) (합성) ---")
    for f_name in ['sigma', 'phi', 'tau']:
        for g_name in ['sigma', 'phi', 'tau', 'n', 'sopfr']:
            try:
                lhs_6 = funcs[f_name](cache[6]['sopfr'])
                rhs_6 = cache[6][g_name] if g_name != 'n' else 6
            except:
                continue

            if lhs_6 == rhs_6:
                solutions = []
                for n in range(2, min(limit + 1, 10001)):
                    try:
                        lhs = funcs[f_name](cache[n]['sopfr'])
                        rhs = cache[n][g_name] if g_name != 'n' else n
                        if lhs == rhs:
                            solutions.append(n)
                    except:
                        continue

                if len(solutions) <= 10:
                    print(f"  {f_name}(sopfr) = {g_name}: solutions = {solutions}")
                    results.append((f'{f_name}(sopfr)', g_name, solutions))

    # 패턴 5: sopfr(n)/n과 다른 비율 비교
    print("\n--- 패턴 5: sopfr(n) = a*f(n) + b*g(n) (선형 조합) ---")
    for a in range(-3, 4):
        for b in range(-3, 4):
            if a == 0 and b == 0:
                continue
            for f_name in ['sigma', 'phi', 'tau']:
                for g_name in ['sigma', 'phi', 'tau', 'n']:
                    if f_name == g_name:
                        continue
                    lhs_6 = cache[6]['sopfr']
                    f6 = cache[6][f_name]
                    g6 = cache[6][g_name] if g_name != 'n' else 6
                    rhs_6 = a * f6 + b * g6

                    if lhs_6 == rhs_6:
                        solutions = []
                        for n in range(2, limit + 1):
                            fn = cache[n][f_name]
                            gn = cache[n][g_name] if g_name != 'n' else n
                            if cache[n]['sopfr'] == a * fn + b * gn:
                                solutions.append(n)

                        if 6 in solutions and len(solutions) <= 5:
                            print(f"  sopfr = {a}*{f_name} + {b}*{g_name}: solutions = {solutions}")
                            results.append((f'sopfr={a}*{f_name}+{b}*{g_name}', '', solutions))

    # 패턴 6: sopfr과 관련된 새로운 곱/나눗셈 관계
    print("\n--- 패턴 6: sopfr(n)*n = f(n)*g(n) ---")
    for f_name in ['sigma', 'phi', 'tau']:
        for g_name in ['sigma', 'phi', 'tau', 'rad', 'Omega']:
            if f_name == g_name:
                continue
            lhs_6 = cache[6]['sopfr'] * 6
            rhs_6 = cache[6][f_name] * cache[6][g_name]

            if lhs_6 == rhs_6:
                solutions = []
                for n in range(2, limit + 1):
                    lhs = cache[n]['sopfr'] * n
                    rhs = cache[n][f_name] * cache[n][g_name]
                    if lhs == rhs:
                        solutions.append(n)

                if len(solutions) <= 10:
                    print(f"  sopfr*n = {f_name}*{g_name}: solutions = {solutions}")
                    results.append((f'sopfr*n', f'{f_name}*{g_name}', solutions))

    # 패턴 7: sopfr + n = 관계
    print("\n--- 패턴 7: sopfr(n) + n = f(n) ---")
    for f_name in ['sigma', 'phi', 'tau']:
        lhs_6 = cache[6]['sopfr'] + 6
        rhs_6 = cache[6][f_name]

        if lhs_6 == rhs_6:
            solutions = []
            for n in range(2, limit + 1):
                if cache[n]['sopfr'] + n == cache[n][f_name]:
                    solutions.append(n)
            if len(solutions) <= 10:
                print(f"  sopfr+n = {f_name}: solutions = {solutions}")

    # 종합
    print("\n" + "=" * 70)
    print("종합: n=6 유일 특성화 후보")
    print("=" * 70)

    unique_6 = [r for r in results if r[2] == [6]]
    small_set_with_6 = [r for r in results if 6 in r[2] and len(r[2]) <= 3 and r[2] != [6]]

    print(f"\n  n=6 유일: {len(unique_6)}개")
    for lhs, rhs, sols in unique_6:
        print(f"    {lhs} = {rhs}")

    print(f"\n  6 포함 소집합 (≤3개): {len(small_set_with_6)}개")
    for lhs, rhs, sols in small_set_with_6:
        print(f"    {lhs} = {rhs}: {sols}")

    # 유일 특성화 검증: 완전수 28에서 깨지는지
    if unique_6:
        print(f"\n--- 완전수 28 검증 ---")
        for lhs, rhs, sols in unique_6:
            print(f"  {lhs} = {rhs}: n=28에서 ", end="")
            if 28 not in sols:
                print("깨짐 ✓ (6 고유)")
            else:
                print("성립 ✗ (6 비고유)")

    return results


if __name__ == "__main__":
    search_sopfr_identities(10000)
