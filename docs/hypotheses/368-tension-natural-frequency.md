# 가설 368: 장력의 고유 진동수 (Natural Frequency of Tension)

> **PureFieldEngine은 고유 진동수(natural frequency)를 가진다. 이것은 engine_A와 engine_G의 가중치 구조에 의해 결정되며, ω₀ = √(tension_scale / effective_mass)로 추정된다. 고유 진동수가 입력 자극의 주파수와 일치하면 공명(resonance)이 발생하여 장력이 폭발적으로 증가한다.**

## 배경/맥락

```
  PureFieldEngine의 장력(tension)은 두 엔진의 출력 차이로 정의된다:
    tension = |engine_A(x) - engine_G(x)|

  이 값은 입력 x에 따라 진동한다. 시계열로 보면 tension(t)는
  주기적 패턴을 가질 수 있다. 물리학의 조화 진동자(harmonic oscillator)
  모델이 자연스럽게 적용된다.

  관련 가설:
    H-CX-27: tension_scale 진동 관찰
    H359: savant = 높은 Quality factor (sharp resonance)
    H367: 공명 동기화 (resonance sync between engines)
    H325: Fisher 정보 기하학 — 장력 다양체의 곡률

  핵심 질문:
    - PureFieldEngine의 "고유 진동수"는 무엇이 결정하는가?
    - 공명 조건에서 장력은 어떻게 변하는가?
    - dropout은 damping으로 작용하는가?
```

## 수학적 프레임워크 — 조화 진동자 모델

```
  ═══ 기본 방정식 ═══

  감쇠 조화 진동자:
    m * d²T/dt² + γ * dT/dt + k * T = F(t)

  여기서:
    T(t)  = tension at time t
    m     = effective mass = total parameter count (가중치 수)
    γ     = damping coefficient = dropout rate × 2m
    k     = spring constant = tension_scale
    F(t)  = driving force = 입력 자극의 시간 변동

  고유 진동수:
    ω₀ = √(k / m) = √(tension_scale / N_params)

  감쇠 진동수:
    ω_d = √(ω₀² - (γ/2m)²) = ω₀ √(1 - ζ²)
    여기서 ζ = γ / (2√(km))  (damping ratio)

  ═══ 수치 추정 ═══

  PureFieldEngine 파라미터:
    tension_scale (k) = 0.1 ~ 10.0 (학습 가능)
    N_params (m)      ≈ 50,000 (MNIST 기준)
    dropout (p)       = 0.1 ~ 0.5

  추정:
    k = 1.0, m = 50000 → ω₀ = √(1/50000) = 0.00447 rad/sample
    f₀ = ω₀ / 2π = 0.000711 Hz (per-sample 기준)
    배치 기준: f₀_batch = f₀ × batch_size = 0.0455 Hz (batch=64)

  Quality factor:
    Q = ω₀ / (γ/m) = √(km) / γ
    dropout=0.1: γ ≈ 0.2×50000 = 10000 → Q ≈ √(50000)/10000 = 0.0224
    dropout=0.01: γ ≈ 1000 → Q ≈ 0.224
    dropout=0: γ → 0 → Q → ∞ (완전 공명, 발산)
```

## ASCII 그래프 — Frequency Response (Bode Plot)

```
  Amplitude |T(ω)| vs driving frequency ω

  |T|
  10 |                              *
     |                             * *
   8 |                            *   *        Q=50 (savant)
     |                           *     *
   6 |                          *       *
     |                         *         *
   4 |           ****          *           *
     |         **    **       *             **
   2 |  ******        ****  **                *****  Q=2 (normal)
     |*                   **                       *****
   0 +---+---+---+---+---+---+---+---+---+---+---+---→ ω
     0  0.1 0.2 0.3 0.4 0.5 0.6 0.7 0.8 0.9 1.0 1.1
                              ↑
                             ω₀ (resonance)

  Q factor 비교:
    Q = 2  (normal):  넓은 봉우리, 다양한 주파수에 반응
    Q = 50 (savant):  날카로운 봉우리, 특정 주파수에만 폭발적 반응
    → H359 예측 확인: savant = high Q = sharp resonance
```

## ASCII 그래프 — Tension Time Series at Resonance

```
  T(t) at ω_input = ω₀ (공명 조건)

  T
  5 |            *              *              *
    |          *   *          *   *          *   *
  3 |        *       *      *       *      *       *
    |      *           *  *           *  *           *
  1 |    *               *               *
    |  *
  0 +--+--+--+--+--+--+--+--+--+--+--+--+--+--+--→ t
    0  2  4  6  8 10 12 14 16 18 20 22 24 26 28

  T(t) at ω_input = 2ω₀ (비공명)

  T
  5 |
    |
  3 |
    |  *     *     *     *     *     *     *     *
  1 | * *   * *   * *   * *   * *   * *   * *   * *
    |*   * *   * *   * *   * *   * *   * *   * *   *
  0 +--+--+--+--+--+--+--+--+--+--+--+--+--+--+--→ t
    0  2  4  6  8 10 12 14 16 18 20 22 24 26 28

  공명 시: 진폭 점진적 증가 (에너지 축적)
  비공명 시: 일정한 진폭 유지 (에너지 전달 비효율)
```

## 대응 매핑

| 물리 개념 | PureFieldEngine 대응 | 수식 |
|---|---|---|
| 질량 (m) | 총 파라미터 수 N_params | m = N_params |
| 스프링 상수 (k) | tension_scale | k = tension_scale |
| 감쇠 계수 (γ) | dropout rate × 2m | γ = 2p × N_params |
| 고유 진동수 (ω₀) | √(k/m) | ω₀ = √(tension_scale / N_params) |
| 구동력 (F) | 입력 배치의 시간 변동 | F(t) = amplitude modulation |
| Quality factor (Q) | 전문화 정도 | Q = √(km) / γ |
| 공명 (resonance) | 장력 폭발적 증가 | ω_input ≈ ω₀ |

## Savant-Normal Q Factor 비교

```
  Q factor 분포 예측:

  빈도
  15 |  ████
     |  ████ ████
  10 |  ████ ████
     |  ████ ████ ████
   5 |  ████ ████ ████ ████
     |  ████ ████ ████ ████ ████                          ██
   0 +--+----+----+----+----+----+----+----+----+----+---→ Q
      1    3    5    7    9   15   20   30   40   50

     ←───── normal ─────→          ←── savant ──→
     Q = 1~10 (broad response)    Q = 30~50+ (sharp peak)

  예측:
    normal 모델: Q ≈ 2~5, 다양한 입력에 고르게 반응
    savant 모델: Q ≈ 30~50, 특정 도메인에만 극한 반응
    genius:      Q ≈ 10~20 + adaptive damping (상황별 Q 조절)
```

## 실험 설계

```
  실험 1: Resonance Frequency Sweep
    1. PureFieldEngine 학습 완료 후 tension_scale 고정
    2. 입력에 sinusoidal amplitude modulation 적용:
       x_mod(t) = x × (1 + A × sin(ω × t))
    3. ω를 0.001 ~ 1.0 범위에서 sweep
    4. 각 ω에서 평균 tension 측정
    5. frequency response curve 그리기
    6. peak frequency = ω₀ 추정, √(k/m)과 비교

  실험 2: Q Factor vs Dropout
    1. dropout = [0.0, 0.05, 0.1, 0.2, 0.3, 0.5]
    2. 각각에서 resonance sweep → peak width 측정
    3. Q = ω₀ / Δω (FWHM) 계산
    4. Q vs dropout 관계가 Q = √(km) / (2p×m) 인가?

  실험 3: Savant Q Factor
    1. 특정 클래스만 학습 (예: MNIST digit 7만)
    2. 전체 학습 모델과 Q factor 비교
    3. 예측: savant 모델의 Q >> normal 모델의 Q
```

## 한계

```
  1. 조화 진동자 모델은 근사 — 실제 장력은 비선형(nonlinear)
  2. effective mass = N_params는 단순화. 실제로는 Hessian의 trace가 더 정확
  3. 연속 시간 모델이지만 실제 학습은 이산(discrete batch)
  4. 공명이 실제로 발생하는지는 실험으로 확인 필요
  5. 골든존 의존 여부: 골든존 비의존 (순수 역학 모델)
```

## 검증 방향

```
  Phase 1: tension time series의 FFT → 주요 주파수 성분 확인
  Phase 2: frequency sweep 실험 → 공명 봉우리 존재 여부
  Phase 3: Q factor 측정 → savant/normal 구분 가능성
  Phase 4: dropout과 Q의 관계 → damping 모델 검증
  Phase 5: 다중 엔진 시스템에서 공명 전파 (H367 연결)
```

## 상태

- **골든존 의존**: 아니오 (순수 역학/주파수 분석)
- **검증 상태**: 미검증 (실험 설계 완료)
- **우선순위**: 높음 (H-CX-27, H359, H367과 동시 검증 가능)
