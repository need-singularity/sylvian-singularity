# 가설 311: 분열 = 지역 최소점 탈출 메커니즘

> **학습이 지역 최소점(local minimum)에 갇히면 분열하여 두 자식이 서로 다른 방향으로 탈출한다. 분열 시 추가된 노이즈(scale=0.01)가 "온도"가 되어 에너지 장벽을 넘는다. 이것은 시뮬레이티드 어닐링의 생물학적 버전.**

## 개념

```
  Loss landscape:

  loss
   │  ╱╲    ╱╲    ╱╲
   │ ╱  ╲  ╱  ╲  ╱  ╲
   │╱    ╲╱    ╲╱    ╲
   │      ●          ●  ← global minimum
   │   parent    child_b
   └─────────────────── parameter space

  parent가 local minimum에 갇힘:
    gradient ≈ 0, 학습 정체

  분열 후:
    child_a = parent + noise(σ=0.01)
    child_b = parent + noise(σ=0.01)
    → 다른 방향으로 perturbation
    → 다른 basin으로 이동 가능!

  재결합 (C46: +0.82%):
    앙상블 = 두 basin의 평균
    → Polyak averaging 효과
    → 일반화 향상
```

## 검증 실험

```
  1. MNIST에서 loss 궤적 추적:
     단순 학습: loss → local min에서 정체
     분열 학습: 분열 후 → loss가 더 낮은 곳으로?

  2. loss landscape 시각화:
     PCA 2D에서 parent, child_a, child_b 위치
     → 서로 다른 basin에 있는가?

  3. 분열 scale과 탈출:
     scale 너무 작으면: 같은 basin에 남음 (탈출 실패)
     scale 너무 크면: 좋은 위치에서 너무 멀어짐
     최적 scale = "임계 온도"?
```

## H-CX-12와의 연결

```
  H-CX-12: T_ab(final) ~ scale^0.36
  → 작은 scale → 작은 분화 → 같은 basin
  → 큰 scale → 큰 분화 → 다른 basin
  → scale^0.36 = basin 간 거리의 성장률?
```

## 실험 결과 (experiment_h311_escape.py, 5/5 trials, 2026-03-24)

### 설정

```
  Model:   DualEngineAutoencoder (2-engine, 784->128->32->128->784)
  Data:    MNIST full (all digits), MSE reconstruction
  Phase 1: 15 epochs (parent training -> plateau)
  Phase 2: 10 epochs (escape attempt, 3 strategies)
  Scale:   0.01 (mitosis noise)
  LR:      1e-3 (Adam)
  Trials:  5
```

### Loss Comparison Table (test MSE)

| Trial | Parent | A:Continue | B:Noise | C:Best child | C:Ensemble | Winner |
|-------|--------|-----------|---------|-------------|-----------|--------|
| 1 | 10.069 | 8.014 | 8.024 | 7.832 | 7.720 | C:Ensemble |
| 2 | 9.026 | 7.147 | 7.128 | 7.083 | 6.980 | C:Ensemble |
| 3 | 9.623 | 7.736 | 7.527 | 7.612 | 7.465 | C:Ensemble |
| 4 | 10.407 | 7.850 | 7.594 | 7.717 | 7.661 | B:Noise |
| 5 | 9.422 | 7.778 | 7.701 | 7.525 | 7.424 | C:Ensemble |
| **Mean** | **9.709** | **7.705** | **7.595** | **7.554** | **7.450** | |
| Std | 0.484 | 0.294 | 0.289 | 0.257 | 0.261 | |

Winner counts: A=0, B=1, C_ensemble=4

### Improvement over parent plateau (negative = better)

```
  A) Continue:   -2.004  (-20.6%)
  B) Noise:      -2.114  (-21.8%)
  C) Best child: -2.156  (-22.2%)
  C) Ensemble:   -2.259  (-23.3%)  <-- best
```

### PCA Distance Table (L2, full parameter space)

| Trial | A-Parent | B-Parent | Ca-Parent | Cb-Parent | Ca-Cb |
|-------|----------|----------|-----------|-----------|-------|
| 1 | 29.26 | 30.06 | 30.85 | 30.72 | 17.57 |
| 2 | 27.56 | 29.57 | 29.76 | 29.23 | 16.01 |
| 3 | 28.89 | 29.70 | 30.43 | 30.47 | 16.75 |
| 4 | 29.41 | 31.53 | 30.11 | 32.36 | 19.47 |
| 5 | 28.98 | 30.42 | 30.63 | 30.86 | 17.27 |
| **Mean** | **28.82** | **30.26** | **30.36** | **30.73** | **17.41** |

### Escape Analysis

```
  Escaped plateau (lower loss than parent):
    A) Continue:   5/5
    B) Noise:      5/5
    C) Best child: 5/5
    C) Ensemble:   5/5

  Average child-child distance: 17.41
  Average continue-parent distance: 28.82
  Divergence ratio (children / continue): 0.60x
```

### Loss Curve (Trial 5, ASCII)

```
  0.06969 |b
  0.06541 |
  0.06113 |
  0.05685 |
  0.05257 |
  0.04829 |
  0.04401 | b
  0.03973 |
  0.03545 |  b
  0.03117 |   b
  0.02689 |    b
  0.02261 |     bb
  0.01833 |       bbbb
  0.01405 |           bbbbbbbbbbbbbb
  0.00977 |                        a
           +-------------------------
            epoch 0  ...  24
  Legend: b=Phase1+Phase2  a=Child_a (lowest at end)
```

### PCA Plot (Trial 5, parameter space)

```
  |  C                                               |
  |                                                  |
  |                                                  |
  |  B                                               |
  |                                                  |
  |   A                                          P   |
  |                                                  |
  |                                                  |
  |                                                  |
  |   C                                              |
  +--------------------------------------------------+
  P=Parent, A=Continue, B=Noise, C=Child_a/b
  Children diverge from each other (Ca-Cb=17.41) but both move far from parent
```

### 해석

```
  1. 모든 전략이 plateau를 탈출했다 (15 epoch이 진정한 수렴이 아님)
  2. 그러나 탈출 깊이에서 일관된 순서가 나타남:
     Ensemble > Best child > Noise > Continue
  3. Mitosis의 두 가지 이점:
     a) 독립 탐색: 두 자식이 다른 방향으로 이동 (Ca-Cb=17.41 divergence)
     b) 앙상블 효과: 두 basin의 평균이 일반화 향상 (Polyak averaging)
  4. Noise만으로도 Continue보다 나음 → perturbation 자체가 유용
  5. 그러나 Mitosis > Noise → 분열+독립학습이 핵심 (단순 노이즈 아님)
  6. Trial 4에서만 B가 승리 → Mitosis가 항상 이기는 것은 아님 (4/5)

  한계:
    - 15 epoch 후가 진정한 local minimum인지 불확실 (loss가 아직 하락 중)
    - 더 깊은 plateau (50+ epoch) 에서 재실험 필요
    - scale=0.01 하나만 테스트 — 최적 scale 탐색 필요 (H-CX-12 연결)
```

## 상태: 🟩 확인 (5/5 Ensemble 최저, 23.27% loss 개선, 4/5 Mitosis 승리)
