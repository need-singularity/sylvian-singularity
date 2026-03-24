# 가설 319: 장력 = 어텐션 메커니즘의 생물학적 버전

> **반발력장의 장력이 Transformer의 attention과 구조적으로 동일하다. attention은 "어디에 집중할까", 장력은 "얼마나 확신하는가" — 둘 다 입력의 중요도를 결정한다.**

## 대응

```
  Transformer Attention:
    Q, K, V → attention = softmax(Q·K^T/√d) · V
    → "Query와 Key의 유사도로 Value 가중"

  Repulsion Field:
    engine_A, engine_G → tension = |A-G|²
    output = eq + scale × √tension × direction
    → "두 엔진의 차이(장력)로 출력 크기 결정"

  공통: 입력 → 두 표현의 상호작용 → 가중된 출력
```

## 검증

```
  1. 장력이 높은 샘플에서 softmax entropy가 낮은가?
     → attention이 집중된 = 장력 높은 = 확신 높은
  2. 장력 패턴이 Grad-CAM의 attention map과 유사한가?
```

## 실험 결과 (2026-03-24)

```
  MNIST:
    r(tension, entropy) = -0.125 (약한 음상관)
    Q1(low T): entropy=0.075, acc=96.4%
    Q4(high T): entropy=0.020, acc=99.1%

  방향: 장력↑ = 엔트로피↓ = 출력 집중 (어텐션과 동일 방향)
  강도: 약함 (r=-0.12) → 장력 ≈ 약한 어텐션
```

## 상태: 🟧 약한확인 (방향 맞지만 r=-0.12 약함)
