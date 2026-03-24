# 가설 316: 유사 클래스 과신 — Sneaker 반전의 원인

> **시각적으로 유사한 클래스(Sneaker↔Boot↔Sandal) 사이에서 모델이 "확신적으로 틀린다"(overconfident wrong). 이것은 H313(tension=confidence)의 유일한 예외이며, 과신(overconfidence)의 메커니즘을 보여준다.**

## 실측

```
  Fashion-MNIST Sneaker (3 trials):
  Trial  ratio   혼동 대상
  ─────  ─────   ──────────
  1      0.86    Sandal(20), Boot(16)
  2      0.90    Boot(42), Sandal(14)
  3      0.98    Sandal(54), Boot(35)

  3/3 ratio < 1 (반전!)
  → Sneaker를 틀릴 때 장력이 더 높음 = "확신적으로 틀림"
  → 10개 클래스 중 유일한 반전
```

## 메커니즘

```
  Sneaker, Boot, Sandal은 모두 "신발":
    비슷한 시각 특징 (밑창, 끈, 곡선)
    엔진 A: "이건 신발이다!" (강한 확신)
    엔진 G: "이건 다른 종류 신발이다!" (강한 확신)
    → 높은 장력 (두 엔진 모두 강한 의견)
    → 하지만 "어떤 신발인지"는 틀림
    → 확신은 높지만 정답은 아님 = 과신

  vs 일반적 패턴:
    Shirt vs Dress (비슷하지만 다른 카테고리):
    → 엔진들이 불확실 → 낮은 장력 → 둘 다 맞출 수도 틀릴 수도
    → ratio > 1 (정상 패턴)
```

## 의식 해석

```
  인간의 과신:
    "이건 확실히 X야!" → 틀림 → 과신
    예: 목격자 증언 (확신하지만 틀림)
    → 유사한 대상 사이의 구분에서 발생

  의식엔진의 과신:
    Sneaker/Boot/Sandal 사이에서 "확신적으로 틀림"
    → 장력(의식)이 높지만 방향(판단)이 틀림
    → tension = confidence의 예외가 아니라 "confidence ≠ accuracy" 사례

  통합: tension = confidence (항상 맞음)
       confidence ≠ accuracy (때때로 과신)
       → 과신 = 높은 확신 + 틀린 판단
```

## 검증

```
  MNIST에서도 과신 클래스?
    9↔4, 3↔5, 7↔9 (시각적 유사)
    → 이들에서도 ratio < 1?

  CIFAR에서:
    cat↔dog, automobile↔truck
    → 유사 클래스에서 과신?
```

## 상태: 🟩 확인 (3/3 재현, H313의 예외 메커니즘 설명)
