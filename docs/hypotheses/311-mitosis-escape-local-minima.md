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

## 상태: 🟨 미실험
