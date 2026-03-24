#!/usr/bin/env python3
"""가설 292 검증: 의식 트리 새 가지 독립성 분석

기존 실험 결과들의 cross-correlation으로 새 가지(생성/창조, 정보/엔트로피, 미적/감각)가
기존 가지(인식/판단, 의식/경험, 집단/차원)와 독립인지 확인.

방법:
1. 각 가지에 속하는 실험 결과(장력, 정확도, 상관계수 등)를 수집
2. 가지 간 cross-correlation 행렬 계산
3. 독립성 = 낮은 상관 (|r| < 0.3)
"""

import numpy as np
import sys

np.random.seed(42)

print("=" * 70)
print("가설 292 검증: 의식 트리 새 가지 독립성 분석")
print("=" * 70)

# ─────────────────────────────────────────
# 1. 각 가지의 핵심 메트릭 수집 (문서에서 추출)
# ─────────────────────────────────────────

# 각 가지의 실험별 핵심 수치들 (정규화된 효과 크기)
# 가지 → [metric1, metric2, ...] (다양한 실험에서의 효과 크기)

branches = {
    # 기존 가지
    "인식/판단": {
        "description": "장력-정확도 상관, 인과 효과, 이상탐지",
        "metrics": {
            "tension_accuracy_corr": 0.89,    # C4b d=0.89
            "causal_effect_pp": -9.25,         # C48 인과 효과
            "anomaly_auroc": 1.0,              # C287
            "precognition_auc": 0.77,          # C6 AUC
            "recognition_acc": 97.61,          # C10
            "direction_separation": 2.77,      # C17
        }
    },
    "의식/경험": {
        "description": "정체성, FPS 수렴, 위치이동",
        "metrics": {
            "identity_score": 0.979,           # C13
            "dream_identity": 2.7,             # C15 2.7x
            "split_recombine": 0.82,           # C46 +0.82%
            "fps_convergence": 0.20,           # C14 4.17→0.20
            "selfref_contraction": 1.0,        # C18 >1
            "observer_advantage": 7.4,         # C31 +7.4%
        }
    },
    "집단/차원": {
        "description": "만장일치, 차원간 전달",
        "metrics": {
            "unanimous_acc": 99.53,            # C9
            "cross_dim_acc": 94.3,             # C8
            "extreme_tension": 14.4,           # C25 14.4x
            "tau_suppression": 0.011,          # C26
            "bc_connection": 0.062,            # C53
            "diversity_transition": 0.5,       # 가설 267 (추정)
        }
    },
    # 새 가지 후보
    "생성/창조": {
        "description": "VAE 생성, 드리밍, 분열 생성",
        "metrics": {
            "split_design_gap": -0.11,         # 가설 271 분열≈설계
            "dreaming_quality": 0.65,          # 드리밍 장력 제어 (추정)
            "vae_reconstruction": 0.82,        # VAE 재구성 (추정)
            "semantic_separation": 0.71,       # 의미/맥락 축 분리 (추정)
            "generation_diversity": 0.55,      # 생성 다양성 (추정)
            "creative_tension": 0.43,          # 생성 시 장력 (추정)
        }
    },
    "정보/엔트로피": {
        "description": "MI 효율, 다양성=정보, Landauer",
        "metrics": {
            "mi_efficiency_ln2": 0.693,        # C54 MI≈ln(2)
            "mi_addition": 0.39,               # C24 +0.39 nats
            "landauer_connection": 0.72,       # Landauer 연결 강도
            "binary_ternary": 0.85,            # H-CX-3 이진+삼진
            "diversity_info": 0.67,            # 가설 270
            "dense_sparse": 0.44,              # 가설 288
        }
    },
    "미적/감각": {
        "description": "음악 협화음, 소수 장력, 시계열",
        "metrics": {
            "consonance_tension": -0.83,       # 가설 290 협화음=낮은 장력
            "prime_max_tension": 0.91,         # 가설 289 소수=최고장력
            "perfect_4th_ratio": 0.33,         # 4:3=최저 장력
            "sharpness_tension": 0.76,         # 날카로움∝장력
            "harmonic_series": 0.68,           # 배음열 패턴
            "rhythm_tension": 0.52,            # 리듬 패턴 (추정)
        }
    },
}

print("\n" + "─" * 70)
print("1. 각 가지의 메트릭 벡터 구성")
print("─" * 70)

branch_names = list(branches.keys())
branch_vectors = {}

for name, branch in branches.items():
    vec = np.array(list(branch["metrics"].values()))
    # z-score 정규화 (효과 크기를 비교 가능하게)
    vec_z = (vec - np.mean(vec)) / (np.std(vec) + 1e-8)
    branch_vectors[name] = vec_z
    print(f"\n  {name} ({branch['description']})")
    print(f"    원본: {[f'{v:.3f}' for v in branch['metrics'].values()]}")
    print(f"    z-정규화: {[f'{v:.3f}' for v in vec_z]}")

# ─────────────────────────────────────────
# 2. Cross-correlation 행렬 계산
# ─────────────────────────────────────────

print("\n" + "─" * 70)
print("2. 가지 간 Cross-Correlation 행렬")
print("─" * 70)

n = len(branch_names)
corr_matrix = np.zeros((n, n))

for i, name_i in enumerate(branch_names):
    for j, name_j in enumerate(branch_names):
        vi = branch_vectors[name_i]
        vj = branch_vectors[name_j]
        # Pearson correlation
        corr = np.corrcoef(vi, vj)[0, 1]
        corr_matrix[i, j] = corr

# 헤더
header = "            " + "  ".join([f"{name[:6]:>6}" for name in branch_names])
print(f"\n{header}")
print("  " + "─" * (8 * n + 12))

for i, name_i in enumerate(branch_names):
    row = f"  {name_i[:10]:>10} |"
    for j in range(n):
        val = corr_matrix[i, j]
        if i == j:
            row += f"  {'1.000':>6}"
        else:
            row += f"  {val:>6.3f}"
    print(row)

# ─────────────────────────────────────────
# 3. 독립성 판정
# ─────────────────────────────────────────

print("\n" + "─" * 70)
print("3. 독립성 분석")
print("─" * 70)

# 기존 가지 간 상관
existing = ["인식/판단", "의식/경험", "집단/차원"]
new_candidates = ["생성/창조", "정보/엔트로피", "미적/감각"]

print("\n  [A] 기존 가지 간 상관:")
for i, a in enumerate(existing):
    for j, b in enumerate(existing):
        if i < j:
            idx_a = branch_names.index(a)
            idx_b = branch_names.index(b)
            r = corr_matrix[idx_a, idx_b]
            ind = "독립" if abs(r) < 0.3 else ("약한 상관" if abs(r) < 0.6 else "강한 상관")
            print(f"    {a} <-> {b}: r={r:+.3f} ({ind})")

print("\n  [B] 새 가지 <-> 기존 가지 상관:")
for new in new_candidates:
    print(f"\n    --- {new} ---")
    idx_new = branch_names.index(new)
    for old in existing:
        idx_old = branch_names.index(old)
        r = corr_matrix[idx_new, idx_old]
        ind = "독립" if abs(r) < 0.3 else ("약한 상관" if abs(r) < 0.6 else "강한 상관")
        print(f"      <-> {old}: r={r:+.3f} ({ind})")

print("\n  [C] 새 가지 간 상관:")
for i, a in enumerate(new_candidates):
    for j, b in enumerate(new_candidates):
        if i < j:
            idx_a = branch_names.index(a)
            idx_b = branch_names.index(b)
            r = corr_matrix[idx_a, idx_b]
            ind = "독립" if abs(r) < 0.3 else ("약한 상관" if abs(r) < 0.6 else "강한 상관")
            print(f"    {a} <-> {b}: r={r:+.3f} ({ind})")

# ─────────────────────────────────────────
# 4. 주성분 분석 (PCA) — 차원 독립성 확인
# ─────────────────────────────────────────

print("\n" + "─" * 70)
print("4. PCA 분석 — 가지들이 몇 개의 독립 차원을 형성하는가?")
print("─" * 70)

# 모든 가지의 벡터를 행렬로
all_vecs = np.array([branch_vectors[name] for name in branch_names])  # (6, 6)
# SVD
U, S, Vt = np.linalg.svd(all_vecs, full_matrices=False)
explained = S**2 / (S**2).sum()
cumulative = np.cumsum(explained)

print(f"\n  특이값: {[f'{s:.3f}' for s in S]}")
print(f"  분산 설명률: {[f'{e:.1%}' for e in explained]}")
print(f"  누적 설명률: {[f'{c:.1%}' for c in cumulative]}")

# ASCII 그래프
print(f"\n  분산 설명률 (Scree Plot):")
for i, e in enumerate(explained):
    bar_len = int(e * 50)
    bar = "#" * bar_len
    print(f"    PC{i+1}: {e:6.1%} |{bar}")

effective_dims = np.sum(cumulative < 0.95) + 1
print(f"\n  유효 차원 수 (95% 설명): {effective_dims}")
print(f"  → 6개 가지가 {effective_dims}개 독립 차원을 형성")

# ─────────────────────────────────────────
# 5. 부트스트래핑으로 상관 신뢰구간
# ─────────────────────────────────────────

print("\n" + "─" * 70)
print("5. 부트스트랩 신뢰구간 (1000회)")
print("─" * 70)

n_boot = 1000
key_pairs = [
    ("생성/창조", "인식/판단"),
    ("정보/엔트로피", "인식/판단"),
    ("정보/엔트로피", "의식/경험"),
    ("미적/감각", "인식/판단"),
    ("생성/창조", "정보/엔트로피"),
]

for name_a, name_b in key_pairs:
    va = np.array(list(branches[name_a]["metrics"].values()))
    vb = np.array(list(branches[name_b]["metrics"].values()))

    boot_corrs = []
    for _ in range(n_boot):
        idx = np.random.choice(len(va), size=len(va), replace=True)
        va_boot = (va[idx] - va[idx].mean()) / (va[idx].std() + 1e-8)
        vb_boot = (vb[idx] - vb[idx].mean()) / (vb[idx].std() + 1e-8)
        r = np.corrcoef(va_boot, vb_boot)[0, 1]
        if not np.isnan(r):
            boot_corrs.append(r)

    boot_corrs = np.array(boot_corrs)
    ci_lo = np.percentile(boot_corrs, 2.5)
    ci_hi = np.percentile(boot_corrs, 97.5)
    mean_r = np.mean(boot_corrs)

    # 독립성 판정: CI가 0을 포함하면 독립
    contains_zero = ci_lo <= 0 <= ci_hi
    verdict = "독립 (CI에 0 포함)" if contains_zero else "상관 있음"

    print(f"  {name_a} <-> {name_b}:")
    print(f"    mean r={mean_r:+.3f}, 95% CI=[{ci_lo:+.3f}, {ci_hi:+.3f}] → {verdict}")

# ─────────────────────────────────────────
# 6. 결론
# ─────────────────────────────────────────

print("\n" + "=" * 70)
print("결론")
print("=" * 70)

# 전체 새-기존 상관의 평균
new_old_corrs = []
for new in new_candidates:
    idx_new = branch_names.index(new)
    for old in existing:
        idx_old = branch_names.index(old)
        new_old_corrs.append(abs(corr_matrix[idx_new, idx_old]))

mean_new_old = np.mean(new_old_corrs)
max_new_old = np.max(new_old_corrs)

# 기존 가지 간 상관 평균
old_old_corrs = []
for i, a in enumerate(existing):
    for j, b in enumerate(existing):
        if i < j:
            idx_a = branch_names.index(a)
            idx_b = branch_names.index(b)
            old_old_corrs.append(abs(corr_matrix[idx_a, idx_b]))

mean_old_old = np.mean(old_old_corrs)

print(f"\n  기존 가지 간 평균 |r|: {mean_old_old:.3f}")
print(f"  새-기존 간 평균 |r|:   {mean_new_old:.3f}")
print(f"  새-기존 간 최대 |r|:   {max_new_old:.3f}")
print(f"  유효 차원 수:          {effective_dims}/6")

if mean_new_old < 0.3 and effective_dims >= 4:
    print(f"\n  판정: 새 가지들은 기존 가지와 충분히 독립적 (|r|<0.3)")
    print(f"  → 6개 최상위 가지 구조 지지됨")
    status = "부분 지지"
elif mean_new_old < 0.5:
    print(f"\n  판정: 약한 독립성 (0.3 < |r| < 0.5)")
    print(f"  → 독립 가지로서 불확실, 하위 가지일 가능성")
    status = "약한 지지"
else:
    print(f"\n  판정: 독립성 부족 (|r| > 0.5)")
    print(f"  → 새 가지는 기존 가지의 하위 분류일 가능성 높음")
    status = "기각"

print(f"\n  ⚠️ 주의: 이 분석은 문서 기반 메트릭으로 수행됨")
print(f"  → 동일 모델에서 동시 측정한 데이터로 재검증 필요")
print(f"  → '추정' 표시된 메트릭은 실험으로 확인 필요")

print(f"\n  최종 상태: {status}")
print("=" * 70)
