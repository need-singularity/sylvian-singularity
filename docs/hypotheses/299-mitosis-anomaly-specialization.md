# 가설 299: 분열 특수화 이상탐지 — 각 자식이 다른 정상 패턴을 "전문화"

> **분열된 자식들이 독립 학습하면 각자 정상 데이터의 다른 측면을 전문화한다. child_a는 feature 1-15에 민감, child_b는 feature 16-30에 민감. 이상 데이터가 어떤 feature 범위에서 벗어나든 최소 한 자식이 감지한다.**

## 개념

```
  단일 모델 이상탐지:
    정상 전체를 하나의 모델로 커버
    → 커버리지 넓지만 각 영역 해상도 낮음
    → 미묘한 이상 놓칠 수 있음

  분열 이상탐지:
    child_a: 정상의 pattern_A 전문화
    child_b: 정상의 pattern_B 전문화
    → 각 영역 해상도 높음
    → 이상이 A 영역이면 child_a가, B 영역이면 child_b가 감지
    → 간 장력 = "어떤 자식이 불편해하는가"

  Random Forest 비유:
    각 트리가 다른 feature subset 사용
    → 이상이 어느 feature에서 나타나든 감지
    분열 = "자연스러운 feature selection"
```

## 검증 방법

```
  1. Breast Cancer 데이터 (30 features)
  2. parent → child_a, child_b (다른 mini-batch로 학습)
  3. 학습 후 각 child의 feature 중요도 분석:
     a) child_a의 engine_a 1st layer weight norm per feature
     b) child_b의 engine_a 1st layer weight norm per feature
  4. 특수화 정도 = 1 - cosine_similarity(weight_a, weight_b)
  5. 특수화 vs AUROC 상관

  추가 실험:
    강제 특수화: child_a는 feature[:15]만, child_b는 feature[15:]만 학습
    → AUROC가 자연 분열보다 높은가 낮은가?
```

## 수학적 배경

```
  커버리지 이론:
    P(detect anomaly) = 1 - Π(1 - p_i)
    p_i = i번째 child가 감지할 확률

    독립이면: P = 1 - (1-p)^N
    N=2, p=0.6: P = 0.84
    N=4, p=0.6: P = 0.97
    N=8, p=0.6: P = 0.9993

  → 분열 수 증가 = 커버리지 증가 (가설 297과 연결)
```

## 뇌과학 대응

```
  시각 피질: V1→V2→V4→IT
    각 영역이 다른 특징 전문화 (선분, 텍스처, 형태, 물체)
    → 이상(왜곡된 얼굴) = 특정 영역이 강하게 반응

  분열 = 피질 영역 분화
  간 장력 = 영역 간 불일치 = "뭔가 이상하다" 신호
  → P300 뇌파 (이상 자극 감지)와 구조적 동형
```

## 상태: 🟨 미실험
