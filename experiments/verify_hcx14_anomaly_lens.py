#!/usr/bin/env python3
"""H-CX-14 검증: 이상탐지 = 중력렌즈 구조적 동형성 정량화

방법:
1. R(n) = sigma*phi/(n*tau) 스펙트럼과 T(x) 장력 구조의 대응 행렬 작성
2. 6개 구조적 대응을 정량화 (이름, 함수형, 스케일링, 경계)
3. AUROC(K) 데이터를 피팅: 1-a/K^b vs 1-a*exp(-bK) vs sigmoid
4. 수학적 F(s)~1/(s-1) 발산과의 구조 비교
5. 대응 일관성 점수 계산
"""

import numpy as np
from scipy.optimize import curve_fit
import warnings
warnings.filterwarnings('ignore')

np.random.seed(42)

print("=" * 70)
print("H-CX-14 검증: 이상탐지 = 중력렌즈 구조적 동형성")
print("=" * 70)

# ─────────────────────────────────────────
# 1. R 스펙트럼 계산
# ─────────────────────────────────────────

print("\n" + "─" * 70)
print("1. R 스펙트럼: R(n) = sigma(n)*phi(n) / (n*tau(n))")
print("─" * 70)

def sigma(n):
    """약수의 합."""
    return sum(d for d in range(1, n+1) if n % d == 0)

def tau(n):
    """약수의 개수."""
    return sum(1 for d in range(1, n+1) if n % d == 0)

def euler_phi(n):
    """오일러 토션트."""
    count = 0
    for i in range(1, n+1):
        if gcd(i, n) == 1:
            count += 1
    return count

def gcd(a, b):
    while b:
        a, b = b, a % b
    return a

def R(n):
    """R 스펙트럼."""
    return sigma(n) * euler_phi(n) / (n * tau(n))

# R(n) for n=1..100
ns = list(range(1, 101))
Rs = [R(n) for n in ns]

print(f"\n  완전수 R값:")
for n in [6, 28]:
    print(f"    R({n}) = {R(n):.6f}")

print(f"\n  R=1 근방의 수 (간극 분석):")
for n in ns[:30]:
    if abs(R(n) - 1.0) < 0.3:
        print(f"    R({n:3d}) = {R(n):.4f}  {'*** 완전!' if R(n) == 1.0 else ''}")

# 간극: R=1 양쪽
rs_array = np.array(Rs)
below_1 = rs_array[rs_array < 1.0]
above_1 = rs_array[rs_array > 1.0]

if len(below_1) > 0 and len(above_1) > 0:
    gap_below = 1.0 - np.max(below_1)
    gap_above = np.min(above_1) - 1.0
    print(f"\n  간극 (R=1 주위):")
    print(f"    아래 최대: R = {np.max(below_1):.4f} (간극 = {gap_below:.4f})")
    print(f"    위 최소:   R = {np.min(above_1):.4f} (간극 = {gap_above:.4f})")
    total_gap = gap_below + gap_above
    print(f"    총 간극:   {total_gap:.4f}")

# ─────────────────────────────────────────
# 2. AUROC(K) 피팅
# ─────────────────────────────────────────

print("\n" + "─" * 70)
print("2. AUROC(K) 데이터 피팅 (H298)")
print("─" * 70)

# 실측 데이터 (H298)
K_data = np.array([0, 1, 2, 5, 10, 20, 50])
AUROC_data = np.array([0.58, 0.58, 0.69, 0.67, 0.74, 0.84, 0.95])

# 모델 1: Power law: AUROC = 1 - a * K^(-b) (K>0)
def power_model(K, a, b):
    return 1.0 - a * np.power(K + 0.1, -b)

# 모델 2: Exponential: AUROC = 1 - a * exp(-b*K)
def exp_model(K, a, b):
    return 1.0 - a * np.exp(-b * K)

# 모델 3: Sigmoid: AUROC = L / (1 + a * exp(-b*K))
def sigmoid_model(K, L, a, b):
    return L / (1.0 + a * np.exp(-b * K))

models = {
    "Power law: 1 - a*K^(-b)": (power_model, [0.4, 0.5], 2),
    "Exponential: 1 - a*exp(-bK)": (exp_model, [0.4, 0.05], 2),
    "Sigmoid: L/(1+a*exp(-bK))": (sigmoid_model, [1.0, 2.0, 0.1], 3),
}

fit_results = {}
print(f"\n  {'모델':>30} | {'SSE':>10} | {'R^2':>8} | 파라미터")
print(f"  {'─'*30}─┼─{'─'*10}─┼─{'─'*8}─┼─{'─'*30}")

ss_tot = np.sum((AUROC_data - np.mean(AUROC_data))**2)

for name, (func, p0, n_params) in models.items():
    try:
        popt, pcov = curve_fit(func, K_data, AUROC_data, p0=p0, maxfev=10000)
        y_pred = func(K_data, *popt)
        sse = np.sum((AUROC_data - y_pred)**2)
        r2 = 1 - sse / ss_tot
        params_str = ", ".join([f"{p:.4f}" for p in popt])
        print(f"  {name:>30} | {sse:>10.6f} | {r2:>7.4f} | {params_str}")
        fit_results[name] = {"func": func, "params": popt, "sse": sse, "r2": r2}
    except Exception as e:
        print(f"  {name:>30} | {'FAIL':>10} | {'---':>8} | {str(e)[:30]}")

# 최적 모델
best_model = max(fit_results.items(), key=lambda x: x[1]["r2"])
print(f"\n  최적 모델: {best_model[0]} (R^2 = {best_model[1]['r2']:.4f})")

# AUROC 예측
print(f"\n  최적 모델 예측:")
K_pred = [0, 1, 2, 5, 10, 20, 50, 100, 200, 500]
for K in K_pred:
    pred = best_model[1]["func"](np.array([K]), *best_model[1]["params"])[0]
    pred = min(pred, 1.0)
    actual = ""
    for i, kd in enumerate(K_data):
        if kd == K:
            actual = f" (실측: {AUROC_data[i]:.2f})"
            break
    print(f"    K={K:>4}: AUROC = {pred:.4f}{actual}")

# ASCII 그래프
print(f"\n  AUROC vs K (실측 * vs 피팅 -):")
height = 12
width = 50
grid = [['.' for _ in range(width)] for _ in range(height)]

K_fine = np.linspace(0, 55, width)
AUROC_fine = best_model[1]["func"](K_fine, *best_model[1]["params"])
AUROC_fine = np.clip(AUROC_fine, 0.5, 1.0)

for i, K in enumerate(K_fine):
    y = int((AUROC_fine[i] - 0.5) / 0.5 * (height - 1))
    y = height - 1 - max(0, min(height - 1, y))
    grid[y][i] = '-'

for i, K in enumerate(K_data):
    x = int(K / 55 * (width - 1))
    y = int((AUROC_data[i] - 0.5) / 0.5 * (height - 1))
    y = height - 1 - max(0, min(height - 1, y))
    x = max(0, min(width - 1, x))
    grid[y][x] = '*'

print(f"    1.0 ^")
for row in grid:
    print(f"        |{''.join(row)}")
print(f"    0.5 +{'─' * width}> K")
print(f"        0          10         20         30         40         50")

# ─────────────────────────────────────────
# 3. 구조적 대응 행렬
# ─────────────────────────────────────────

print("\n" + "─" * 70)
print("3. 구조적 대응 행렬: R 스펙트럼 <-> 이상탐지")
print("─" * 70)

correspondences = [
    {
        "math": "R(n) = 1 (완전수)",
        "engine": "T(x) = T_expected (정상)",
        "type": "Identity/Fixed point",
        "math_property": "sigma(n)/n = 2",
        "engine_property": "tension = class mean",
        "structural_match": True,
        "reason": "둘 다 '이상적 균형점'을 정의",
    },
    {
        "math": "R(n) != 1 (비완전수)",
        "engine": "T(x) >> T_expected (이상)",
        "type": "Deviation detection",
        "math_property": "|R(n)-1| > gap",
        "engine_property": "|T-T_mean| > threshold",
        "structural_match": True,
        "reason": "둘 다 '이상적에서의 이탈'을 감지",
    },
    {
        "math": "gap width (R=1 주위)",
        "engine": "decision boundary width",
        "type": "Sensitivity/Resolution",
        "math_property": f"total gap = {total_gap:.4f}",
        "engine_property": "threshold = percentile",
        "structural_match": True,
        "reason": "간극이 넓을수록 = 민감도 높음",
    },
    {
        "math": "s parameter (Dirichlet)",
        "engine": "K (학습 에폭)",
        "type": "Scale/Resolution",
        "math_property": "F(s) ~ 1/(s-1) as s->1",
        "engine_property": f"AUROC(K) ~ {best_model[0]}",
        "structural_match": "s->1 발산" in best_model[0] or best_model[1]["r2"] > 0.9,
        "reason": "둘 다 '한계에서 최대 해상도'",
    },
    {
        "math": "lens (n=6: infinite lens)",
        "engine": "split (scale=0: identical copy)",
        "type": "Focusing mechanism",
        "math_property": "M(6)=0 → 1/|M|=∞",
        "engine_property": "scale=0 → perfect copy → max AUROC",
        "structural_match": True,
        "reason": "'완전' = '무한 렌즈' = '완전한 관측'",
    },
    {
        "math": "(s, R_0) 2D space",
        "engine": "(objective, tension_type) 2x2 matrix",
        "type": "Parameter space",
        "math_property": "2 continuous dims",
        "engine_property": "2 categorical dims",
        "structural_match": False,
        "reason": "차원 수는 같으나 연속/범주 차이",
    },
]

n_match = sum(1 for c in correspondences if c["structural_match"])
total_corr = len(correspondences)
consistency_score = n_match / total_corr

print(f"\n  | # | 수학 (R 스펙트럼) | 엔진 (이상탐지) | 유형 | 일치? |")
print(f"  |---|---|---|---|---|")
for i, c in enumerate(correspondences):
    match = "O" if c["structural_match"] else "X"
    print(f"  | {i+1} | {c['math'][:25]:25s} | {c['engine'][:25]:25s} | {c['type'][:20]:20s} | {match} |")

print(f"\n  대응 일관성 점수: {n_match}/{total_corr} = {consistency_score:.2f}")

# ─────────────────────────────────────────
# 4. 수학적 발산 구조 비교
# ─────────────────────────────────────────

print("\n" + "─" * 70)
print("4. 수학의 1/(s-1) 발산 vs AUROC 수렴 비교")
print("─" * 70)

# 수학: F(s) ~ C/(s-1) as s->1
# 엔진: AUROC(K) -> 1 as K -> infinity
# 대응: s = 1 + C/K?  (s->1 <=> K->inf)

# s = 1 + a/K 변환하에:
# F(s) = C/(s-1) = C*K/a
# AUROC가 이 변환으로 선형이면 구조 동형

print(f"\n  변환: s = 1 + a/K (s->1 as K->inf)")
print(f"  이 변환에서 F(s) = C/(s-1) = C*K/a ∝ K")
print(f"  → AUROC가 K에 대해 선형? = 발산 구조 공유?")

# 선형 피팅 (K>0)
K_pos = K_data[K_data > 0]
A_pos = AUROC_data[len(K_data) - len(K_pos):]

# 1-AUROC vs 1/K (power law test)
inv_K = 1.0 / (K_pos + 0.1)
one_minus_auroc = 1.0 - A_pos

# Log-log
log_K = np.log(K_pos + 0.1)
log_1mA = np.log(one_minus_auroc + 1e-10)

# Linear regression
slope, intercept = np.polyfit(log_K, log_1mA, 1)

print(f"\n  log(1-AUROC) vs log(K) 선형 피팅:")
print(f"    기울기 = {slope:.4f} (음수 = 감쇠)")
print(f"    절편   = {intercept:.4f}")
print(f"    → 1-AUROC ~ K^({slope:.2f})")
print(f"    → 수학의 1/(s-1)에 대응하려면 기울기 ≈ -1.0")
print(f"    → 실제 기울기 = {slope:.2f} ({'유사' if abs(slope + 1) < 0.5 else '다름'})")

# ─────────────────────────────────────────
# 5. 렌즈 강도 vs 분열 scale 대응
# ─────────────────────────────────────────

print("\n" + "─" * 70)
print("5. 렌즈 강도 M(n) vs 이상탐지 민감도")
print("─" * 70)

print(f"\n  M(n) = |sigma(n)/n - 2| (완전성 이탈)")
print(f"  렌즈 강도 = 1/M(n)")
print(f"\n  {'n':>4} | {'sigma/n':>8} | {'M(n)':>8} | {'렌즈강도':>10} | {'유형':>8}")
print(f"  {'─'*4}─┼─{'─'*8}─┼─{'─'*8}─┼─{'─'*10}─┼─{'─'*8}")

for n in [1, 2, 3, 4, 5, 6, 7, 8, 10, 12, 28]:
    sn = sigma(n)
    mn = abs(sn/n - 2)
    lens = 1/mn if mn > 0 else float('inf')
    ntype = "완전" if mn == 0 else ("과잉" if sn/n > 2 else "부족")
    lens_str = f"{lens:.2f}" if lens < 1e6 else "INF"
    print(f"  {n:>4} | {sn/n:>8.4f} | {mn:>8.4f} | {lens_str:>10} | {ntype:>8}")

# ─────────────────────────────────────────
# 6. 결론
# ─────────────────────────────────────────

print("\n" + "=" * 70)
print("결론")
print("=" * 70)

print(f"\n  구조적 대응 일관성: {consistency_score:.0%} ({n_match}/{total_corr})")
print(f"  최적 피팅 모델: {best_model[0]} (R^2={best_model[1]['r2']:.4f})")
print(f"  발산 구조 기울기: {slope:.2f} (예측 -1.0)")
print(f"  R=1 간극: {total_gap:.4f}")

# 종합 점수 (0-1)
scores = [
    consistency_score,
    best_model[1]["r2"],
    1.0 if abs(slope + 1) < 0.5 else 0.5 if abs(slope + 1) < 1.0 else 0.0,
]
total_score = np.mean(scores)

print(f"\n  종합 동형성 점수: {total_score:.2f}")

if total_score > 0.7:
    verdict = "강한 구조적 동형성 — 수학과 이상탐지가 같은 구조"
elif total_score > 0.5:
    verdict = "부분적 동형성 — 일부 대응은 확인, 일부는 불일치"
elif total_score > 0.3:
    verdict = "약한 유비 — 구조적 동형보다는 비유 수준"
else:
    verdict = "동형성 기각 — 우연적 유사성"

print(f"  판정: {verdict}")

print(f"\n  ⚠️ 한계:")
print(f"    - AUROC 데이터 7점만으로 피팅 (과적합 위험)")
print(f"    - s↔K 변환이 물리적으로 정당화되지 않음")
print(f"    - 구조적 대응의 주관성 (5/6 일치는 선택 편향 가능)")
print(f"    - 정량적 동형성 증명이 아닌 정성적 평가")
print("=" * 70)
