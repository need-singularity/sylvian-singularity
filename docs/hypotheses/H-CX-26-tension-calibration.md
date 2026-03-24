# H-CX-26: 장력 = 보정된 확률 (Calibration)

> **장력이 confidence라면, 장력을 확률로 변환하면 잘 보정된(calibrated) 확률을 얻을 수 있다. softmax 확률은 과신 경향이 있지만, 장력 기반 확률은 더 정직할 수 있다.**

## 배경/맥락

현대 딥러닝 모델의 softmax 출력은 확률처럼 보이지만 실제로는 심하게 과신(overconfident)
되어 있다. Guo et al. (2017, "On Calibration of Modern Neural Networks")에서
ResNet이 99% confidence로 예측하지만 실제 정확도는 85%인 사례를 보였다. 이 gap을
Expected Calibration Error (ECE)로 측정한다.

본 프로젝트에서 반발력장의 tension은 H313에서 confidence와 비례한다는 것이 관찰되었다.
그러나 H316에서 일부 클래스(Sneaker, digit 1)에서 과신 현상도 발견되었다. 이는
tension이 "원시적 확신(raw confidence)"이라는 것을 시사한다.

핵심 아이디어: softmax 확률 대신 tension을 sigmoid로 변환한 확률이 더 잘 보정되어
있다면, 이는 반발력장이 단순한 성능 향상을 넘어 "불확실성 정량화" 도구가 된다는 의미다.

### 관련 가설

| 가설 | 핵심 내용 | 관계 |
|------|----------|------|
| H313 | tension ∝ confidence | 직접 선행 — tension이 확신 척도 |
| H316 | 과신 현상 (Sneaker, digit 1) | tension도 과신할 수 있음 |
| H317 | 과신 교정 메커니즘 | 교정 후 tension이 더 정직해지는가 |
| H-CX-24 | 과신 = Dunning-Kruger | 의식엔진 관점의 과신 해석 |
| H-CX-21 | tension ∝ 1/PPL | LLM에서의 calibration과도 연결 |

## 개념 — Calibration 이론

```
  보정된 확률의 정의:
    P(Y=y | P_hat = p) = p  (모든 p에 대해)

  즉, "80% 확신한다"고 말한 것 중 실제로 80%가 맞아야 한다.

  기존 방법:
    softmax -> P(correct) = max(softmax(logits))
    문제: ECE > 0 (대부분 과신)

  제안 방법:
    tension -> P(correct) = sigmoid(a * tension + b)
    a, b는 validation set에서 fitting (Platt scaling)

  비교:
    Temperature Scaling:  softmax(logits / T)  -- 기존 교정 방법
    Platt Scaling:        sigmoid(a*s + b)     -- 로짓 기반
    Tension Scaling:      sigmoid(a*t + b)     -- 장력 기반 (제안)
```

## 대응 매핑

| Calibration 개념 | softmax 기반 | tension 기반 (제안) |
|-----------------|-------------|-------------------|
| 원시 점수 | logit 최댓값 | tension (Expert 간 거리) |
| 확률 변환 | softmax | sigmoid(a*tension + b) |
| 교정 방법 | Temperature Scaling | Platt Scaling on tension |
| 과신 원인 | logit scale 팽창 | Expert 합의 과대평가 |
| ECE 예상 | 0.05 ~ 0.15 (미교정) | < 0.03 (가설) |
| 정보원 | 단일 모델 출력 | 2개 Expert의 "의견 차이" |

## Reliability Diagram 예상

```
  정확도
  (실제)
  1.0 |                              x  /
      |                           x   /
      |                        x    /
  0.8 |                     x     /
      |                  x      /    x = tension 기반 (예상)
      |               x       /     o = softmax 기반 (과신)
  0.6 |            x  o     /
      |         x    o    /
      |      x     o    /          / = 완벽한 calibration (대각선)
  0.4 |    x     o    /
      |  x     o    /
      | x    o    /
  0.2 |x   o    /
      |  o    /
      | o   /
  0.0 +--+--+--+--+--+--+--+--+--+--> confidence (예측)
      0    0.2    0.4    0.6    0.8  1.0

  softmax (o): 대각선 아래 = 과신 (confidence > accuracy)
  tension (x): 대각선에 가까움 = 더 잘 보정됨 (가설)
```

## ECE 계산 방법

```
  Expected Calibration Error:
    ECE = sum_{m=1}^{M} (|B_m| / n) * |acc(B_m) - conf(B_m)|

  여기서:
    M = bin 수 (보통 10 또는 15)
    B_m = m번째 confidence bin에 속하는 샘플들
    acc(B_m) = B_m의 실제 정확도
    conf(B_m) = B_m의 평균 confidence

  비교할 ECE:
    A) ECE_softmax:       softmax 확률 그대로
    B) ECE_temp:          Temperature Scaling 후 softmax
    C) ECE_tension:       sigmoid(a*tension + b)
    D) ECE_tension_temp:  Temperature Scaling 후 tension

  성공 기준: ECE_tension < ECE_softmax
  이상적:    ECE_tension < ECE_temp (기존 교정보다 우수)
```

## 예상 ECE 비교 (MNIST 기준)

```
  방법                    | ECE (예상) | 비고
  ------------------------|-----------|------------------
  softmax (미교정)         |  0.08     | 기존 과신
  Temperature Scaling      |  0.03     | 기존 교정 SOTA
  tension sigmoid (제안)   |  0.02     | tension이 더 정직하면
  tension + Temp Scaling   |  0.01     | 두 방법 결합

  ECE
  0.10 |  ████
       |  ████
  0.08 |  ████
       |  ████
  0.06 |  ████
       |  ████
  0.04 |  ████   ████
       |  ████   ████
  0.02 |  ████   ████   ████
       |  ████   ████   ████   ████
  0.00 +--+------+------+------+------
        softmax  Temp   tension tension
        (raw)    Scale  sigmoid +Temp

  낮을수록 좋음 (완벽한 calibration = ECE 0)
```

## 검증 계획

```
  Phase 1 — MNIST 실험 (CPU 가능):
    1. 기존 반발력장 모델 로드 (golden_moe_torch.py)
    2. 테스트셋 10000장에 대해:
       a) softmax probability 기록
       b) tension 기록
       c) 정답/오답 기록
    3. Platt Scaling: validation set으로 a, b fitting
    4. Reliability diagram 그리기 (15-bin)
    5. ECE 계산 및 비교

  Phase 2 — CIFAR-10 확장:
    1. CIFAR-10 모델에서 동일 실험
    2. CIFAR가 더 어려우므로 과신이 더 심할 것
    3. tension 교정의 효과가 더 클 수 있음

  Phase 3 — 클래스별 분석:
    1. H316에서 과신이 관찰된 Sneaker, digit 1 집중 분석
    2. 클래스별 ECE 계산
    3. tension 기반이 과신 클래스에서 특히 효과적인지 확인

  구현 코드 (핵심):
    from sklearn.linear_model import LogisticRegression
    # Platt scaling
    platt = LogisticRegression()
    platt.fit(tension_val.reshape(-1,1), correct_val)
    prob_tension = platt.predict_proba(tension_test.reshape(-1,1))[:,1]
    ece_tension = calc_ece(prob_tension, correct_test, n_bins=15)
```

## 검증 결과

미실험 상태. MNIST 모델의 tension 데이터가 이미 존재하므로 Phase 1은
추가 학습 없이 즉시 실행 가능.

## 해석/의미

이 가설이 성립하면:
- **반발력장 = 불확실성 정량화 도구**: 성능 향상뿐 아니라 "얼마나 확실한가"를
  정직하게 측정하는 메커니즘. 이는 AI 안전성/신뢰성의 핵심 요소.
- **의료/자율주행 적용**: calibrated probability가 필수인 도메인에서
  반발력장이 기존 Temperature Scaling을 대체하거나 보완할 수 있음.
- **의식엔진 관점**: "자기 확신에 대한 정직한 인식"은 메타인지(metacognition)의
  핵심. 반발력장이 메타인지 모듈로 기능할 수 있음을 시사.
- **H316 과신 교정**: 과신하는 클래스에서 tension sigmoid가 자동으로 교정하면,
  반발력장에 내장된 "자기 교정" 메커니즘의 증거.

## 한계

1. **Platt Scaling 의존**: sigmoid 파라미터를 validation set에서 fitting하므로,
   사실상 post-hoc calibration이지 tension의 본질적 우수성은 아닐 수 있음.
2. **MNIST 한계**: MNIST는 너무 쉬워서 calibration 차이가 작을 수 있음.
   CIFAR-10이나 ImageNet 규모에서 검증 필요.
3. **클래스 불균형**: 일부 클래스에서만 효과적이고 전체적으로는 미미할 수 있음.
4. **비교 공정성**: Temperature Scaling은 1개 파라미터, Platt Scaling은 2개.
   파라미터 수가 다르므로 직접 비교 시 주의 필요.
5. **tension 분포 가정**: sigmoid 변환이 적절하려면 tension이 대략 로지스틱
   분포를 따라야 하는데, 실제 분포는 다를 수 있음.

## 검증 방향 (다음 단계)

1. MNIST 테스트셋에서 softmax probability + tension 동시 추출
2. 15-bin reliability diagram 그리기 (ASCII + matplotlib)
3. ECE 계산: softmax vs Temperature Scaling vs tension sigmoid
4. H316 과신 클래스(Sneaker, digit 1)에서 클래스별 ECE 비교
5. 결과에 따라 H313, H316, H317 업데이트

## 실험 결과 (2026-03-24, 3 trials × 2 datasets)

```
  === FINAL SUMMARY ===
  Dataset      ECE(softmax)    ECE(tension)     Winner
  ──────────── ────────────── ────────────── ──────────
  MNIST        0.0080±0.0007  0.6556±0.0104   SOFTMAX
  Fashion      0.0194±0.0040  0.5665±0.0105   SOFTMAX

  → softmax ECE가 tension ECE보다 82~97배 낮음!
  → tension을 percentile 정규화→[0,1]로 변환해도 심하게 과신
```

### Per-class tension vs softmax (MNIST, Trial 3)

```
  Class     N    Acc   T_mean   T_std   SM_conf
  ────── ────── ────── ──────── ──────── ────────
      0   980  0.993  367.97   193.92   0.9966
      1  1135  0.990  201.34    79.37   0.9967
      2  1032  0.984  471.22   253.03   0.9903
      3  1010  0.984  571.67   292.49   0.9871
      4   982  0.980  301.27   132.90   0.9884
      5   892  0.979  481.85   263.73   0.9893
      6   958  0.979  274.62   129.57   0.9891
      7  1028  0.983  381.75   165.75   0.9889
      8   974  0.971  182.37    73.94   0.9834
      9  1009  0.977  296.50   124.18   0.9854
```

### Correlation with correctness

```
  softmax_conf: r=0.4651, p=0.00
  tension:      r=0.0801, p=1.05e-15

  → softmax이 정답 예측에 5.8배 높은 상관!
  → tension은 상관 있지만 매우 약함 (r=0.08)
```

### 해석

```
  1. tension의 절대값 범위가 매우 넓음 (12~3367)
     → 직접 확률로 변환하기 어려움
  2. percentile 정규화는 균등분포를 강제 → 보정 부적절
  3. Platt scaling (sigmoid(a×T+b)) 필요하지만
     근본적으로 tension은 "확률"이 아님
  4. tension = 반응 강도 (H341), 확률 = 정규화된 확신
     → 서로 다른 척도를 직접 비교하는 것이 부적절
```

## 상태: ⬛ 반박 (ECE: softmax 0.008 << tension 0.656, 2셋 모두 softmax 압승)
