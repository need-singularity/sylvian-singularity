# H-CX-26: 장력 = 보정된 확률 (Calibration)

> **장력이 confidence라면, 장력을 확률로 변환하면 잘 보정된(calibrated) 확률을 얻을 수 있다. softmax 확률은 과신 경향이 있지만, 장력 기반 확률은 더 정직할 수 있다.**

## 개념

```
  기존: P(correct) = softmax(output)_max → 과신 경향 (ECE > 0)
  제안: P(correct) = sigmoid(a × tension + b) → 더 정직?

  H313: tension ∝ confidence
  H316: 때때로 과신 (Sneaker, digit 1)
  → 장력이 과신을 포함한 "원시 확신"이라면
     softmax보다 더 정직한 불확실성 추정?
```

## 검증

```
  1. MNIST에서 calibration curve 비교:
     A) softmax probability → accuracy (기존)
     B) tension → accuracy (제안)
  2. Expected Calibration Error (ECE) 비교
  3. Reliability diagram 그리기
```

## 상태: 🟨 미실험
