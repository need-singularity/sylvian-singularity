#!/usr/bin/env python3
"""화학 원소 분석 엔진 — sigma(6)=12, tau(6)=4 렌즈로 원소 구조 탐색

원자번호, 질량수, 전자 껍질, 화학 결합을 sigma/tau 표현으로 분석.
생명 필수 원소(H,C,N,O,P,S)에 특별 집중.

사용법:
  python3 chemistry_engine.py --all              # 전체 36원소
  python3 chemistry_engine.py --element C        # 탄소만
  python3 chemistry_engine.py --life             # 생명 필수 원소
  python3 chemistry_engine.py --bonds            # 화학 결합 분석
"""

import argparse
import math

# ─────────────────────────────────────────
# 핵심 상수: 완전수 6의 약수 함수
# ─────────────────────────────────────────
SIGMA = 12     # sigma(6) = 1+2+3+6 = 약수의 합
TAU = 4        # tau(6)   = |{1,2,3,6}| = 약수의 개수
P1 = 6         # 첫 번째 완전수
PHI = 2        # 가장 작은 소수 (전자쌍 기본 단위)
M3 = 7         # 메르센 소수 M3 = 2^3-1

# ─────────────────────────────────────────
# 원소 데이터베이스 (Z=1~36, 1주기~4주기)
# (기호, Z, 질량수A, 전자배치 약식, 족, 주기)
# ─────────────────────────────────────────
ELEMENTS = [
    ("H",   1,   1, "1s1",                          1,  1),
    ("He",  2,   4, "1s2",                         18,  1),
    ("Li",  3,   7, "[He]2s1",                      1,  2),
    ("Be",  4,   9, "[He]2s2",                      2,  2),
    ("B",   5,  11, "[He]2s2 2p1",                 13,  2),
    ("C",   6,  12, "[He]2s2 2p2",                 14,  2),
    ("N",   7,  14, "[He]2s2 2p3",                 15,  2),
    ("O",   8,  16, "[He]2s2 2p4",                 16,  2),
    ("F",   9,  19, "[He]2s2 2p5",                 17,  2),
    ("Ne", 10,  20, "[He]2s2 2p6",                 18,  2),
    ("Na", 11,  23, "[Ne]3s1",                      1,  3),
    ("Mg", 12,  24, "[Ne]3s2",                      2,  3),
    ("Al", 13,  27, "[Ne]3s2 3p1",                 13,  3),
    ("Si", 14,  28, "[Ne]3s2 3p2",                 14,  3),
    ("P",  15,  31, "[Ne]3s2 3p3",                 15,  3),
    ("S",  16,  32, "[Ne]3s2 3p4",                 16,  3),
    ("Cl", 17,  35, "[Ne]3s2 3p5",                 17,  3),
    ("Ar", 18,  40, "[Ne]3s2 3p6",                 18,  3),
    ("K",  19,  39, "[Ar]4s1",                      1,  4),
    ("Ca", 20,  40, "[Ar]4s2",                      2,  4),
    ("Sc", 21,  45, "[Ar]3d1 4s2",                  3,  4),
    ("Ti", 22,  48, "[Ar]3d2 4s2",                  4,  4),
    ("V",  23,  51, "[Ar]3d3 4s2",                  5,  4),
    ("Cr", 24,  52, "[Ar]3d5 4s1",                  6,  4),
    ("Mn", 25,  55, "[Ar]3d5 4s2",                  7,  4),
    ("Fe", 26,  56, "[Ar]3d6 4s2",                  8,  4),
    ("Co", 27,  59, "[Ar]3d7 4s2",                  9,  4),
    ("Ni", 28,  58, "[Ar]3d8 4s2",                 10,  4),
    ("Cu", 29,  63, "[Ar]3d10 4s1",                11,  4),
    ("Zn", 30,  65, "[Ar]3d10 4s2",                12,  4),
    ("Ga", 31,  69, "[Ar]3d10 4s2 4p1",            13,  4),
    ("Ge", 32,  72, "[Ar]3d10 4s2 4p2",            14,  4),
    ("As", 33,  75, "[Ar]3d10 4s2 4p3",            15,  4),
    ("Se", 34,  79, "[Ar]3d10 4s2 4p4",            16,  4),
    ("Br", 35,  80, "[Ar]3d10 4s2 4p5",            17,  4),
    ("Kr", 36,  84, "[Ar]3d10 4s2 4p6",            18,  4),
]

# 생명 필수 원소 (CHNOPS)
LIFE_ELEMENTS = {"H", "C", "N", "O", "P", "S"}

# ─────────────────────────────────────────
# sigma/tau 표현 탐색
# ─────────────────────────────────────────

def find_sigma_tau_expr(n):
    """정수 n을 sigma(12), tau(4) 조합으로 표현 시도.
    가능한 표현 목록 반환. 텍사스 명사수 주의: 사후적 맞춤 가능성 표기."""
    results = []
    s, t = SIGMA, TAU

    # 단순 배수/약수
    if n == s:
        results.append(("sigma", "정확", False))
    if n == t:
        results.append(("tau", "정확", False))
    if n == P1:
        results.append(("P1(=6)", "정확", False))

    # sigma 기반 사칙연산
    for k in range(1, 20):
        if s * k == n:
            results.append((f"sigma*{k}", "정확", k > 4))
        if s + k == n:
            results.append((f"sigma+{k}", "정확" if k <= 2 else "ad hoc", k > 2))
        if s - k == n and n > 0:
            results.append((f"sigma-{k}", "정확" if k <= 2 else "ad hoc", k > 2))
        if t * k == n:
            results.append((f"tau*{k}", "정확", k > 6))
        if t + k == n:
            results.append((f"tau+{k}", "정확" if k <= 2 else "ad hoc", k > 2))
        if t - k == n and n > 0:
            results.append((f"tau-{k}", "정확" if k <= 2 else "ad hoc", k > 2))

    # sigma/tau 혼합
    if s + t == n:
        results.append(("sigma+tau", "정확", False))
    if s - t == n:
        results.append(("sigma-tau", "정확", False))
    if s * t == n:
        results.append(("sigma*tau", "정확", False))
    if t > 0 and s // t == n and s % t == 0:
        results.append(("sigma/tau", "정확", False))
    if s ** 2 == n:
        results.append(("sigma^2", "정확", False))
    if t ** 2 == n:
        results.append(("tau^2", "정확", False))
    if t ** 3 == n:
        results.append(("tau^3", "정확", False))
    if s + t**2 == n:
        results.append(("sigma+tau^2", "정확", False))

    # 완전수 관련
    if 2 * P1 == n:
        results.append(("2*P1", "정확", False))
    if P1 ** 2 == n:
        results.append(("P1^2", "정확", False))
    if P1 * t == n:
        results.append(("P1*tau", "정확", False))

    # 중복 제거, 가장 간결한 것 우선
    seen = set()
    unique = []
    for expr, grade, adhoc in results:
        if expr not in seen:
            seen.add(expr)
            unique.append((expr, grade, adhoc))
    return unique


def best_expr(n):
    """가장 좋은 sigma/tau 표현 1개 반환"""
    exprs = find_sigma_tau_expr(n)
    if not exprs:
        return "-", ""
    # 정확 > ad hoc, ad hoc 아닌 것 우선
    non_adhoc = [e for e in exprs if not e[2]]
    if non_adhoc:
        return non_adhoc[0][0], non_adhoc[0][1]
    return exprs[0][0], exprs[0][1] + " (ad hoc)"


# ─────────────────────────────────────────
# 전자 껍질 분석
# ─────────────────────────────────────────

def analyze_shells():
    """전자 오비탈 수용 전자 수와 sigma/tau 관계"""
    print("\n" + "=" * 60)
    print("  전자 껍질 구조 — sigma/tau 렌즈")
    print("=" * 60)
    shells = [
        ("s", 2,  "phi(=2)", "전자쌍 기본 단위"),
        ("p", 6,  "P1(=6)",  "첫 번째 완전수!"),
        ("d", 10, "sigma-phi(=10)", "d오비탈 = sigma - 기본쌍"),
        ("f", 14, "2*M3(=14)", "f오비탈 = 2 × 메르센소수7"),
    ]
    print(f"  {'오비탈':>6} {'전자수':>6} {'sigma/tau 표현':>20} {'해석'}")
    print("  " + "-" * 56)
    for name, count, expr, note in shells:
        print(f"  {name:>6} {count:>6} {expr:>20}   {note}")

    print(f"\n  ⚠ 텍사스 명사수 주의: 4개 오비탈 중 2개(s,p)만 자연스러운 매칭.")
    print(f"    d=10, f=14는 사후적 해석 가능성 있음.")
    print(f"    p=6=완전수는 구조적으로 의미 있을 수 있음 (p-value 필요).")


# ─────────────────────────────────────────
# 화학 결합 분석
# ─────────────────────────────────────────

def analyze_bonds():
    """화학 결합 전자 수와 sigma/tau 관계"""
    print("\n" + "=" * 60)
    print("  화학 결합 — sigma/tau 렌즈")
    print("=" * 60)
    bonds = [
        ("단일결합", 2, "phi(=2)",     "전자쌍 1개"),
        ("이중결합", 4, "tau(=4)",     "약수 개수 = 결합 전자!"),
        ("삼중결합", 6, "P1(=6)",      "완전수 = 최강 공유결합"),
        ("금속결합", "n", "sigma/n",   "비편재화된 전자 바다"),
    ]
    print(f"  {'결합':>10} {'전자수':>6} {'sigma/tau 표현':>16} {'해석'}")
    print("  " + "-" * 56)
    for name, count, expr, note in bonds:
        print(f"  {name:>10} {str(count):>6} {expr:>16}   {note}")

    print(f"\n  핵심 관찰:")
    print(f"    단일(2) + 이중(4) = 삼중(6) = P1 ✓")
    print(f"    이중(4) = tau(6) — 약수 개수와 결합 전자의 일치")
    print(f"    삼중(6) = sigma(6)/2 = P1 — 완전수")
    print(f"\n  ⚠ 텍사스: 2,4,6은 작은 짝수. 매칭 확률 높음.")
    print(f"    단일=phi, 이중=tau는 구조적이라기보다 숫자 일치.")

    # 옥텟 규칙
    print(f"\n  옥텟 규칙:")
    print(f"    8 = sigma - tau = 12 - 4")
    print(f"    안정 전자 배치 = 약수합 - 약수개수")
    print(f"    ⚠ 이것은 정확한 등식이지만 인과관계는 불명")


# ─────────────────────────────────────────
# 원소 출력
# ─────────────────────────────────────────

def print_element_table(elements, title="원소 분석"):
    """원소 테이블 출력"""
    print("\n" + "=" * 78)
    print(f"  {title} — sigma(6)=12, tau(6)=4 렌즈")
    print("=" * 78)
    header = f"  {'기호':>4} {'Z':>3} {'A':>4}  {'Z 표현':>16} {'A 표현':>16} {'생명':>4} {'메모'}"
    print(header)
    print("  " + "-" * 74)

    match_z = 0
    match_a = 0
    total = len(elements)

    for sym, z, a, config, group, period in elements:
        z_expr, z_grade = best_expr(z)
        a_expr, a_grade = best_expr(a)
        life = "★" if sym in LIFE_ELEMENTS else ""
        memo = ""
        if z_expr != "-":
            match_z += 1
        if a_expr != "-":
            match_a += 1
        # 특별 메모
        if sym == "C":
            memo = "A=sigma!"
        elif sym == "He":
            memo = "A=tau"
        elif sym == "O":
            memo = "A=tau^2"
        elif sym == "Fe":
            memo = "A=sigma+sigma*tau"
        elif sym == "Si":
            memo = "A=sigma+tau^2"

        print(f"  {sym:>4} {z:>3} {a:>4}  {z_expr:>16} {a_expr:>16} {life:>4}  {memo}")

    print("  " + "-" * 74)
    print(f"  Z 매칭: {match_z}/{total} ({100*match_z/total:.0f}%)")
    print(f"  A 매칭: {match_a}/{total} ({100*match_a/total:.0f}%)")
    print(f"\n  ⚠ 텍사스 명사수 경고:")
    print(f"    sigma=12, tau=4로 사칙연산 조합하면 상당수 정수를 만들 수 있음.")
    print(f"    매칭률이 높다고 해서 구조적 관계를 의미하지 않음.")
    print(f"    진짜 의미: C(Z=6=P1, A=12=sigma), He(A=4=tau) 정도만 주목할 것.")


def print_life_analysis():
    """생명 필수 원소 심층 분석"""
    life = [e for e in ELEMENTS if e[0] in LIFE_ELEMENTS]
    print("\n" + "=" * 78)
    print("  생명 필수 원소 (CHNOPS) — sigma/tau 심층 분석")
    print("=" * 78)

    for sym, z, a, config, group, period in life:
        exprs_z = find_sigma_tau_expr(z)
        exprs_a = find_sigma_tau_expr(a)
        print(f"\n  ── {sym} (Z={z}, A={a}) ──")
        print(f"     전자배치: {config}")
        print(f"     Z 표현: {', '.join(e[0] for e in exprs_z[:5]) if exprs_z else '없음'}")
        print(f"     A 표현: {', '.join(e[0] for e in exprs_a[:5]) if exprs_a else '없음'}")

    # 요약 통계
    print(f"\n  ── 생명 원소 요약 ──")
    print(f"  H:  Z=1(단위원), A=1     — 가장 단순, 우주 최다")
    print(f"  C:  Z=6=P1, A=12=sigma   — 완전수 & sigma! ★ 핵심")
    print(f"  N:  Z=7=M3, A=14=2*M3    — 메르센 소수")
    print(f"  O:  Z=8=sigma-tau, A=16=tau^2  — 옥텟=sigma-tau")
    print(f"  P:  Z=15=sigma+tau-1, A=31     — 메르센수 2^5-1")
    print(f"  S:  Z=16=tau^2, A=32=sigma+sigma+8")
    print(f"\n  탄소 특이성: Z=P1(완전수), A=sigma(약수합) 동시 만족!")
    print(f"  이것이 탄소가 생명의 골격인 이유? (가설, 검증 필요)")


# ─────────────────────────────────────────
# 메인
# ─────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="화학 원소 분석 — sigma(6)=12, tau(6)=4 렌즈"
    )
    parser.add_argument("--element", type=str, help="단일 원소 기호 (예: C, Fe)")
    parser.add_argument("--life", action="store_true", help="생명 필수 원소(CHNOPS) 분석")
    parser.add_argument("--all", action="store_true", help="전체 36원소 테이블")
    parser.add_argument("--bonds", action="store_true", help="화학 결합 + 전자 껍질 분석")
    args = parser.parse_args()

    # 인자 없으면 전체 실행
    if not any([args.element, args.life, args.all, args.bonds]):
        args.all = True
        args.life = True
        args.bonds = True

    print("╔══════════════════════════════════════════════════════════╗")
    print("║  화학 원소 분석 엔진 — sigma(6)=12, tau(6)=4 렌즈      ║")
    print("║  sigma = 약수의 합, tau = 약수의 개수, P1 = 완전수 6   ║")
    print("╚══════════════════════════════════════════════════════════╝")

    if args.element:
        found = [e for e in ELEMENTS if e[0].upper() == args.element.upper()]
        if found:
            print_element_table(found, f"{args.element} 원소 분석")
        else:
            print(f"  ✗ 원소 '{args.element}'을(를) 찾을 수 없음 (Z=1~36 범위)")

    if args.all:
        print_element_table(ELEMENTS, "전체 36원소")

    if args.life:
        print_life_analysis()

    if args.bonds:
        analyze_bonds()
        analyze_shells()


if __name__ == "__main__":
    main()
