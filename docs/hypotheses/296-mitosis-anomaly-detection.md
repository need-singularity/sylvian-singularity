---
가설: 296
제목: 분열 + 이상탐지 — 분열이 이상탐지 성능을 높이는가
---

# 가설 296: 분열 + 이상탐지 — 분열된 엔진이 더 나은 이상 탐지기인가

> **단일 엔진보다 분열된 2개 엔진 사이의 "간 장력"(T_ab)이 더 민감한 이상 점수를 제공한다. 부모 내부 장력(AUROC=1.0, 가설 287)보다 자식간 장력이 이상을 더 잘 감지하는가?**

## 근거

```
  가설 287: 부모 내부 장력 → AUROC=1.0 (합성 데이터)
  가설 293: 실제 데이터 → AUROC 0.94~1.0

  분열 추가:
    parent → child_a, child_b
    T_internal: child_a 내 engine_a vs engine_g
    T_inter: child_a 전체 출력 vs child_b 전체 출력

    가설: T_inter가 T_internal보다 민감
    이유: 분열 후 서로 다르게 학습 → 이상에 다르게 반응
    → 앙상블 다양성 = 이상 탐지 민감도
```

## 실험 설계

```
  1. parent 학습 (정상 데이터만)
  2. 분열 → child_a, child_b
  3. 각 child를 독립 학습 (정상 데이터, 다른 mini-batch)
  4. 테스트: 정상 + 이상 데이터
     a) T_internal_a: child_a 내부 장력 → AUROC_a
     b) T_internal_b: child_b 내부 장력 → AUROC_b
     c) T_inter: |child_a(x) - child_b(x)|² → AUROC_inter
     d) T_combined: T_internal + T_inter → AUROC_combined
  5. 비교: AUROC_inter > AUROC_internal?
```

## 예측

```
  AUROC_internal ≈ 1.0 (이미 확인됨)
  AUROC_inter ≥ AUROC_internal (다양성 추가)
  AUROC_combined ≥ max(individual) (정보 보완)

  하지만 AUROC=1.0이면 더 올릴 수 없다
  → 실제 데이터(breast cancer)에서 차이가 드러날 것
  → 0.947 → 0.97+?
```

## 상태: 🟨 미실험
