#!/usr/bin/env python3
"""핵물리 분석 엔진 — sigma(6)=12, tau(6)=4 렌즈로 핵 구조 탐색

마법수, 핵반응, 결합에너지를 sigma/tau 표현으로 분석.
삼중알파 반응(3*He4=C12 = 3*tau=sigma)이 핵심 연결고리.

사용법:
  python3 nuclear_engine.py --magic              # 마법수 분석
  python3 nuclear_engine.py --reactions          # 핵반응 분석
  python3 nuclear_engine.py --binding            # 결합에너지 곡선
  python3 nuclear_engine.py                      # 전체 실행
"""

import argparse
import math

# ─────────────────────────────────────────
# 핵심 상수: 완전수 6의 약수 함수
# ─────────────────────────────────────────
SIGMA = 12     # sigma(6) = 약수의 합
TAU = 4        # tau(6) = 약수의 개수
P1 = 6         # 첫 번째 완전수
PHI = 2        # 가장 작은 소수

# ─────────────────────────────────────────
# sigma/tau 표현 탐색 (chemistry_engine과 동일 로직)
# ─────────────────────────────────────────

def find_sigma_tau_exprs(n):
    """정수 n을 sigma, tau, P1 조합으로 표현 시도.
    (표현식, 등급, ad_hoc 여부) 리스트 반환."""
    results = []
    s, t, p = SIGMA, TAU, P1

    # 정확히 일치
    if n == s: results.append(("sigma", "정확", False))
    if n == t: results.append(("tau", "정확", False))
    if n == p: results.append(("P1", "정확", False))
    if n == PHI: results.append(("phi", "정확", False))

    # 사칙연산 + 거듭제곱
    combos = [
        (s + t,     "sigma+tau"),
        (s - t,     "sigma-tau"),
        (s * t,     "sigma*tau"),
        (s // t,    "sigma/tau"),
        (t ** 2,    "tau^2"),
        (t ** 3,    "tau^3"),
        (s ** 2,    "sigma^2"),
        (s + t**2,  "sigma+tau^2"),
        (s * t**2,  "sigma*tau^2"),
        (s + p,     "sigma+P1"),
        (s * p,     "sigma*P1"),
        (p * t,     "P1*tau"),
        (p ** 2,    "P1^2"),
        (s + s,     "2*sigma"),
        (s * 3,     "3*sigma"),
        (s + s + t, "2*sigma+tau"),
        (2 * s * t, "2*sigma*tau"),
        (t * t * t, "tau^3"),
        (s * t + t, "sigma*tau+tau"),
        (s * t + s, "sigma*tau+sigma"),
        (s * t - t, "sigma*tau-tau"),
        (s * t - s, "sigma*tau-sigma"),
        (p * p + p, "P1^2+P1"),
        (s + t + p, "sigma+tau+P1"),
        (s * t + p, "sigma*tau+P1"),
        ((s + t) * t, "(sigma+tau)*tau"),
        (s * (s - t), "sigma*(sigma-tau)"),
        (t * (t + 1), "tau*(tau+1)"),
        (p * (p + 1), "P1*(P1+1)"),
        (2 ** (t - 1), "2^(tau-1)"),
        (2 ** t,       "2^tau"),
        (2 ** (t + 1), "2^(tau+1)"),
        (2 ** (p - 1), "2^(P1-1)"),
        (2 ** p,       "2^P1"),
        (2 ** p - PHI, "2^P1-2"),
        (2 ** 7 - PHI, "2^7-2"),
    ]
    for val, expr in combos:
        if val == n:
            # +1/-1 보정이 포함된 것은 ad hoc
            adhoc = "+1" in expr or "-1" in expr
            results.append((expr, "정확", adhoc))

    # 배수 탐색 (작은 계수만)
    for k in range(2, 12):
        if s * k == n and f"{k}*sigma" not in [r[0] for r in results]:
            results.append((f"{k}*sigma", "정확", k > 5))
        if t * k == n and f"{k}*tau" not in [r[0] for r in results]:
            results.append((f"{k}*tau", "정확", k > 8))
        if p * k == n and f"{k}*P1" not in [r[0] for r in results]:
            results.append((f"{k}*P1", "정확", k > 6))

    # 중복 제거
    seen = set()
    unique = []
    for expr, grade, adhoc in results:
        if expr not in seen:
            seen.add(expr)
            unique.append((expr, grade, adhoc))
    return unique


def best_expr(n):
    """가장 간결한 표현 반환"""
    exprs = find_sigma_tau_exprs(n)
    if not exprs:
        return "-"
    non_adhoc = [e for e in exprs if not e[2]]
    if non_adhoc:
        return non_adhoc[0][0]
    return exprs[0][0] + "*"  # * = ad hoc 표시


# ─────────────────────────────────────────
# 마법수 분석
# ─────────────────────────────────────────

MAGIC_NUMBERS = [2, 8, 20, 28, 50, 82, 126]

def analyze_magic():
    """핵 마법수와 sigma/tau 관계 분석"""
    print("\n" + "=" * 70)
    print("  핵 마법수 — sigma(6)=12, tau(6)=4 렌즈")
    print("  마법수: 핵자가 특별히 안정한 양성자/중성자 수")
    print("=" * 70)

    header = f"  {'마법수':>6} {'sigma/tau 표현':>24} {'표현 수':>6} {'등급'}"
    print(header)
    print("  " + "-" * 66)

    matched = 0
    for mn in MAGIC_NUMBERS:
        exprs = find_sigma_tau_exprs(mn)
        non_adhoc = [e for e in exprs if not e[2]]
        be = best_expr(mn)
        n_expr = len(non_adhoc)

        if n_expr > 0:
            grade = "🟩" if n_expr >= 2 else "🟧"
            matched += 1
        else:
            grade = "⚪"

        # 추가 표현 (최대 3개)
        extra = ""
        if len(non_adhoc) > 1:
            extra = " | " + ", ".join(e[0] for e in non_adhoc[1:3])

        print(f"  {mn:>6} {be:>24}{extra:>20} {n_expr:>6} {grade}")

    print("  " + "-" * 66)
    print(f"  매칭: {matched}/{len(MAGIC_NUMBERS)}")

    # 핵심 관찰
    print(f"\n  핵심 관찰:")
    print(f"    2  = phi (가장 작은 소수, 전자쌍)")
    print(f"    8  = sigma - tau = 12 - 4  ★ 옥텟과 동일!")
    print(f"    20 = tau * (tau + 1) = 4 × 5")
    print(f"    28 = sigma + tau^2 = 12 + 16 = sigma(6) + tau(6)^2")
    print(f"         (참고: 28은 두 번째 완전수! sigma(28)=56)")
    print(f"    50 = sigma*tau + tau-2? → ad hoc")
    print(f"    82 = ?  (깔끔한 표현 없음)")
    print(f"    126 = 2^7 - 2 = 2*(2^P1-1) = 2*M6")

    print(f"\n  ⚠ 텍사스 명사수 분석:")
    print(f"    7개 마법수 중 자연스러운 매칭: 2, 8, 28 (3개)")
    print(f"    28=완전수는 sigma/tau 무관하게 독립적으로 주목할 만함")
    print(f"    8=sigma-tau는 구조적일 가능성 (옥텟 규칙과 일치)")
    print(f"    나머지(20,50,82,126)는 억지 매칭 위험")


# ─────────────────────────────────────────
# 핵반응 분석
# ─────────────────────────────────────────

def analyze_reactions():
    """주요 핵반응을 sigma/tau로 해석"""
    print("\n" + "=" * 70)
    print("  핵반응 — sigma/tau 렌즈")
    print("=" * 70)

    # 삼중알파 반응 (핵심!)
    print(f"\n  ━━ 삼중알파 반응 (Triple-Alpha) ━━━━━━━━━━━━━━━━━━━━━━")
    print(f"  3 × He-4 → C-12")
    print(f"  3 × tau  → sigma   ★★★ 핵심 연결!")
    print(f"")
    print(f"    He-4:  Z=2, A=4=tau    (알파 입자 = tau!)")
    print(f"    C-12:  Z=6=P1, A=12=sigma  (탄소 = sigma!)")
    print(f"    반응:  3 × (A=tau) = (A=sigma)")
    print(f"           즉 3*tau = sigma = 12  ✓")
    print(f"")
    print(f"    의미: 알파입자 3개가 모이면 완전수의 약수합이 된다")
    print(f"          tau에서 sigma로의 전환 = 별의 핵합성")
    print(f"")
    print(f"    등급: 🟩 (정확한 등식, 우연 확률 낮음)")
    print(f"    이유: 3*4=12는 자명하지만, He-4=tau와 C-12=sigma의")
    print(f"          동시 대응은 두 독립 매칭의 곱 → p ≈ 1/36")

    # pp-chain (태양)
    print(f"\n  ━━ pp-chain (양성자-양성자 연쇄) ━━━━━━━━━━━━━━━━━━━")
    print(f"  4p → He-4 + 2e⁺ + 2ν + 에너지")
    print(f"  tau 개의 양성자 → tau 질량의 핵 (He-4)")
    print(f"")
    print(f"    입력:  4 = tau 개의 양성자")
    print(f"    출력:  He-4 (A=tau)")
    print(f"    에너지: 26.7 MeV ≈ ? (sigma/tau 매칭 약함)")
    print(f"")
    print(f"    등급: 🟧 (tau 매칭은 자명 — 4p→He4는 정의상)")

    # CNO 순환
    print(f"\n  ━━ CNO 순환 ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print(f"  C-12 촉매 → 4p를 He-4로 변환")
    print(f"  sigma가 촉매 역할! tau개 양성자를 먹고 tau를 출력")
    print(f"")
    print(f"    촉매:    C-12 (A=sigma)")
    print(f"    입력:    4p (tau개)")
    print(f"    출력:    He-4 (A=tau) + C-12 (sigma 복원)")
    print(f"    순환:    sigma + tau*p → sigma + tau-핵")
    print(f"")
    print(f"    sigma는 보존된다 (촉매) ← 흥미로운 관찰")
    print(f"    등급: 🟧★ (sigma 촉매 보존은 구조적)")

    # 핵분열
    print(f"\n  ━━ 우라늄 핵분열 ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print(f"  U-235 + n → Ba-141 + Kr-92 + 3n")
    print(f"  A=235, Z=92 → sigma/tau 매칭 탐색")
    u235_expr = best_expr(235)
    u92_expr = best_expr(92)
    print(f"    235 → {u235_expr}")
    print(f"     92 → {u92_expr}")
    print(f"    분열 중성자: 3개 (= sigma/tau = 3)")
    print(f"    등급: ⚪ (큰 수에서 sigma/tau 매칭은 거의 확실히 우연)")

    # 수소 폭탄 (D-T 반응)
    print(f"\n  ━━ D-T 핵융합 ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print(f"  D(A=2) + T(A=3) → He-4(A=tau) + n")
    print(f"  phi + 3 → tau + 1")
    print(f"  약수(2,3)의 합 → 약수개수(tau)!")
    print(f"  D의 A=2, T의 A=3: 6의 약수 2와 3의 핵이 합쳐짐")
    print(f"  등급: 🟧 (2+3=5≠4이므로 중성자 1개 방출. 흥미롭지만 약함)")

    # 요약 테이블
    print(f"\n  ━━ 핵반응 요약 ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print(f"  {'반응':>14} {'sigma/tau 해석':>30} {'등급':>6}")
    print(f"  " + "-" * 56)
    reactions = [
        ("삼중알파",    "3*tau → sigma (He4→C12)",     "🟩"),
        ("pp-chain",    "tau*p → tau-핵 (자명)",        "🟧"),
        ("CNO 순환",    "sigma 촉매 보존",              "🟧★"),
        ("D-T 융합",    "약수(2,3)→tau+n",             "🟧"),
        ("U 분열",      "큰 수, 우연 매칭",             "⚪"),
    ]
    for name, interp, grade in reactions:
        print(f"  {name:>14} {interp:>30} {grade:>6}")


# ─────────────────────────────────────────
# 결합에너지 곡선 분석
# ─────────────────────────────────────────

# 핵자당 결합에너지 근사값 (MeV, 주요 핵종)
BINDING_ENERGY = [
    # (원소, A, Z, BE/A MeV)
    ("H-2",    2,   1, 1.11),
    ("He-3",   3,   2, 2.57),
    ("He-4",   4,   2, 7.07),
    ("Li-6",   6,   3, 5.33),
    ("Li-7",   7,   3, 5.61),
    ("C-12",  12,   6, 7.68),
    ("N-14",  14,   7, 7.48),
    ("O-16",  16,   8, 7.98),
    ("Ne-20", 20,  10, 8.03),
    ("Si-28", 28,  14, 8.45),
    ("S-32",  32,  16, 8.49),
    ("Ca-40", 40,  20, 8.55),
    ("Ti-48", 48,  22, 8.72),
    ("Cr-52", 52,  24, 8.78),
    ("Fe-56", 56,  26, 8.79),  # ← 최대!
    ("Ni-62", 62,  28, 8.79),
    ("Zn-64", 64,  30, 8.74),
    ("Kr-84", 84,  36, 8.72),
    ("Zr-90", 90,  40, 8.71),
    ("Mo-98", 98,  42, 8.64),
    ("Sn-120",120, 50, 8.51),
    ("Nd-142",142, 60, 8.35),
    ("Pb-208",208, 82, 7.87),
    ("U-238", 238, 92, 7.57),
]

def analyze_binding():
    """결합에너지 곡선과 sigma/tau"""
    print("\n" + "=" * 70)
    print("  핵자당 결합에너지 — sigma/tau 렌즈")
    print("=" * 70)

    # ASCII 그래프
    print(f"\n  BE/A (MeV)")
    print(f"  9.0 ┤")

    max_a = 240
    chart_w = 55
    chart_h = 12
    min_be = 1.0
    max_be = 9.0

    # 그리드 생성
    grid = [[" " for _ in range(chart_w)] for _ in range(chart_h)]

    for name, a, z, be in BINDING_ENERGY:
        x = int(a / max_a * (chart_w - 1))
        y = int((be - min_be) / (max_be - min_be) * (chart_h - 1))
        y = min(max(y, 0), chart_h - 1)
        y_inv = chart_h - 1 - y
        ch = "*"
        if name == "Fe-56":
            ch = "F"  # Fe 표시
        elif name == "He-4":
            ch = "H"  # He 표시
        elif name == "C-12":
            ch = "C"
        grid[y_inv][x] = ch

    # 출력
    be_labels = [9.0, 8.0, 7.0, 6.0, 5.0, 4.0, 3.0, 2.0, 1.0]
    for i, row in enumerate(grid):
        be_val = max_be - i * (max_be - min_be) / (chart_h - 1)
        label = f"{be_val:4.1f}" if i % 3 == 0 else "    "
        line = "".join(row)
        bar = "┤" if i % 3 == 0 else "│"
        print(f"  {label} {bar}{line}")
    print(f"       └" + "─" * chart_w)
    print(f"        0      50     100    150    200    A (질량수)")
    print(f"        H=핵, C=탄소, F=철(Fe-56 정점)")

    # sigma/tau 분석
    print(f"\n  ━━ 정점 분석: Fe-56 ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print(f"    Fe: Z=26, A=56")
    print(f"    A=56 = sigma * tau + sigma - tau = 12*4+12-4 = 56 ✓")
    print(f"         = sigma*(tau+1) - tau = 12*5-4 = 56 ✓")
    print(f"         = 2 * 28 = 2 * (두 번째 완전수)")
    print(f"         = 2 * sigma(28)... 아니, sigma(28)=56! ★")
    print(f"    sigma(28) = 1+2+4+7+14+28 = 56 = Fe의 질량수!")
    print(f"    28은 완전수이므로 sigma(28) = 2*28 = 56")
    print(f"")
    print(f"    Z=26 = 2 * 13  (13은 소수)")
    z26_expr = best_expr(26)
    print(f"    Z=26 → {z26_expr}")
    print(f"")
    print(f"    등급: 🟧★ (Fe-56 = sigma(28) = sigma(P2) 는 구조적)")
    print(f"    주의: BE 정점이 Fe-56인 것은 핵력 + 쿨롱의 결과")
    print(f"          sigma(P2)=56과의 일치는 우연일 가능성 높음")

    # 알파 입자 특이성
    print(f"\n  ━━ He-4 (알파 입자) 특이성 ━━━━━━━━━━━━━━━━━━━━━━")
    print(f"    A=4=tau에서 BE/A=7.07 — A 대비 비정상적으로 높음")
    print(f"    tau-핵의 초안정성 → 마법수 2의 이중 마법핵")
    print(f"    (Z=2=phi, N=2=phi 모두 마법수)")

    # 핵자당 BE 테이블
    print(f"\n  ━━ sigma/tau 매칭 테이블 ━━━━━━━━━━━━━━━━━━━━━━━━")
    print(f"  {'핵종':>8} {'A':>4} {'Z':>3} {'BE/A':>6} {'A 표현':>20} {'비고'}")
    print(f"  " + "-" * 64)
    for name, a, z, be in BINDING_ENERGY:
        expr = best_expr(a)
        note = ""
        if name == "Fe-56":
            note = "★ 정점, sigma(28)"
        elif name == "He-4":
            note = "★ tau, 알파 초안정"
        elif name == "C-12":
            note = "★ sigma, 삼중알파"
        elif name == "Si-28":
            note = "P2(완전수28)"
        elif name == "Ni-62":
            note = "실제 최대 BE/A"
        print(f"  {name:>8} {a:>4} {z:>3} {be:>6.2f} {expr:>20}  {note}")

    print(f"\n  ⚠ 텍사스 명사수 경고:")
    print(f"    질량수는 단순 정수 → sigma*tau 조합으로 많은 수 표현 가능")
    print(f"    진짜 주목: He-4=tau(정점급 BE), C-12=sigma(생명), Fe-56=sigma(P2)")


# ─────────────────────────────────────────
# 메인
# ─────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="핵물리 분석 — sigma(6)=12, tau(6)=4 렌즈"
    )
    parser.add_argument("--magic", action="store_true", help="마법수 분석")
    parser.add_argument("--reactions", action="store_true", help="핵반응 분석")
    parser.add_argument("--binding", action="store_true", help="결합에너지 곡선")
    args = parser.parse_args()

    # 인자 없으면 전체 실행
    if not any([args.magic, args.reactions, args.binding]):
        args.magic = True
        args.reactions = True
        args.binding = True

    print("╔══════════════════════════════════════════════════════════╗")
    print("║  핵물리 분석 엔진 — sigma(6)=12, tau(6)=4 렌즈         ║")
    print("║  마법수, 핵반응, 결합에너지를 약수함수로 해석           ║")
    print("╚══════════════════════════════════════════════════════════╝")

    if args.magic:
        analyze_magic()

    if args.reactions:
        analyze_reactions()

    if args.binding:
        analyze_binding()


if __name__ == "__main__":
    main()
