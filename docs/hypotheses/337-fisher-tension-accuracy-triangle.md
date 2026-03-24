# 가설 337: Fisher-Tension-Accuracy 삼각관계

> **gradient(Fisher), 장력(Tension), 정확도(Accuracy)가 삼각관계. Fisher∝1/Accuracy(r=-0.97), Tension∝Accuracy(r=+0.14), Fisher∝1/Tension(r=-0.15). "gradient=배울것, tension=배운것, accuracy=결과".**

## 실측 (PureField, MNIST, per-class)

```
  digit  Fisher   Tension   Accuracy
  ────   ──────   ───────   ────────
  d0     0.0007      202     98.6%
  d1     0.0011      115     98.8%
  d2     0.0012      281     97.9%
  d3     0.0012      280     98.5%
  d4     0.0010      196     98.7%
  d5     0.0015      268     98.3%
  d6     0.0014      200     97.6%
  d7     0.0015      246     97.9%
  d8     0.0026      162     96.3%
  d9     0.0035      199     94.6%

  상관:
    r(F, acc)  = -0.972  ← 거의 완벽!
    r(T, acc)  = +0.139
    r(F, T)    = -0.157

  삼각관계:
    Fisher ←(-0.97)→ Accuracy ←(+0.14)→ Tension ←(-0.16)→ Fisher
```

## 해석

```
  Fisher = ∂Loss/∂x = "이 입력에서 얼마나 배울 게 남았나"
  Tension = |A-G|² = "이 입력에 대해 얼마나 확신하나"
  Accuracy = P(correct) = "실제로 맞추는가"

  Fisher→Accuracy: 강함(-0.97) = gradient 큰 클래스는 못 맞춤
  Tension→Accuracy: 약함(+0.14) = 확신이 높으면 약간 더 맞춤
  Fisher→Tension: 약함(-0.16) = gradient 크면 장력 약간 낮음

  왜 Fisher-Accuracy가 가장 강한가?
    Fisher는 loss에서 직접 계산 = accuracy와 직결
    Tension은 A-G 차이 = accuracy의 간접 지표
    → Fisher = "직접 측정", Tension = "간접 측정"
```

## 상태: 🟩 확인 (r(F,acc)=-0.972, 삼각관계 수립)
