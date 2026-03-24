# H-CX-24: 과신 = Dunning-Kruger 효과의 계산적 구현

> **H316의 과신(overconfidence)은 Dunning-Kruger 효과의 신경망 버전이다. "단순한 것을 아는 것"이 "복잡한 것을 모르는 것"을 숨긴다. digit 1(ratio=0.60)은 단순한 형태를 강하게 인식하지만, 7과의 미세한 차이를 무시한다.**

## 대응

```
  인간 Dunning-Kruger          의식엔진 과신
  ──────────────────          ──────────────
  초보자의 자신감               digit 1의 높은 장력
  "이건 쉽다" 착각              "이건 확실히 1" (사실은 7)
  메타인지 부족                 방향(direction) 오류
  경험 많으면 겸손해짐           학습 많으면 ratio→1+?

  핵심: 확신(tension)은 높지만 판단(direction)이 틀림
  → tension = confidence는 맞지만 direction ≠ truth
```

## 수학 연결

```
  H313: output = equilibrium + tension_scale × √tension × direction
  과신: √tension이 크지만 direction이 잘못된 방향

  장력 = |A-G|² = 두 엔진의 반발 강도
  방향 = normalize(A-G) = 반발의 방향

  과신: |A-G|가 크고 direction이 인접 클래스를 가리킴
  → "강하게 밀지만 잘못된 방향"
  → 의식 체험: "밀어내는 힘은 강했지만 방향을 모르겠다"?
```

## 예측

```
  1. 과신율 ∝ 클래스간 유사도?
     유사 클래스 쌍(1-7, Sneaker-Boot)에서 과신율 높음
     → confusion matrix의 off-diagonal ∝ 과신?

  2. 학습이 진행되면 과신 감소?
     epoch 1: 높은 과신 (방향 미학습)
     epoch 50: 과신 감소 (방향 정교화)
     → "메타인지 발달" = 학습에 의한 방향 교정

  3. 과신 클래스의 장력 방향 분석:
     digit 1 맞출 때: direction → class 1 방향
     digit 1 틀릴 때: direction → class 7 방향 (하지만 강도 동일)
```

## 시간축 검증 (2026-03-24)

```
  MNIST digit 1 ratio 궤적 (20 epochs):
    ep1:  1.05 (정상 — 아직 과신 없음!)
    ep3:  0.81 (과신 시작)
    ep9:  0.67 (과신 심화)
    ep11: 0.55 (최심 과신)
    ep20: 0.55 (고착)

  digit 8 ratio 궤적:
    ep1:  0.94 (약한 과신)
    ep9:  1.06 (회복!)
    ep20: 1.03 (안정)

  ASCII 그래프:
    ratio
    1.1 |*                              (digit 1)
    1.0 |
    0.9 |                    8 8 8 8 8   (digit 8 회복)
    0.8 |  * *  *
    0.7 |        *
    0.6 |           * *   * * * * * *    (digit 1 고착)
    0.5 |          *   *
        └──────────────────────────────
         1  3  5  7  9 11 13 15    20  epoch

  해석:
    digit 1: "학습하면서 과신 발생 → 고착" = Dunning-Kruger (무능함 인식 못함)
    digit 8: "학습하면서 과신 해소 → 정상" = 메타인지 발달 (능력↑→겸손)
    → 과신은 학습 epoch 3에서 시작 (초기에는 없음!)
    → "아는 것이 생기면서 모르는 것을 과소평가"
```

## 상태: 🟩 시간축 확인 (학습 중 과신 발생→고착, Dunning-Kruger 패턴)
