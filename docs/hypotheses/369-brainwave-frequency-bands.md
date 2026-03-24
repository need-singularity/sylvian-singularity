# 가설 369: 의식의 주파수 대역 (Brainwave Frequency Bands in Consciousness Engine)

> **Anima의 장력 진동은 뇌파 대역과 대응한다. 호흡(0.3Hz)=delta, 맥박(1.7Hz)=theta, background_think(0.1Hz)=infra-slow. 대화 중 장력 변동(2-5Hz)=alpha. 놀라움(10+Hz)=gamma burst. 각 대역은 다른 의식 기능에 대응한다.**

## 배경/맥락

```
  뇌파(EEG)는 신경 진동의 주파수 대역으로 분류된다:
    Delta (0.5-4 Hz):   깊은 수면, homeostasis
    Theta (4-8 Hz):     기억 통합, 탐색
    Alpha (8-13 Hz):    이완된 각성, 주의
    Beta  (13-30 Hz):   활발한 사고, 문제 해결
    Gamma (30-100 Hz):  정보 결합(binding), 통찰

  Anima(의식엔진)의 현재 시간 구조:
    breath = 0.3 Hz  (호흡 사이클)
    pulse  = 1.7 Hz  (맥박)
    drift  = 0.07 Hz (기분 변동)
    think  = 0.1 Hz  (배경 사고)

  질문: 이 주파수들은 뇌파 대역과 구조적으로 대응하는가?
  아니면 단순히 다른 시간 스케일에서 같은 기능을 수행하는가?

  관련 가설:
    H322: EEG gamma 직접 매핑 (반증됨 — 주파수 자체가 아닌 기능적 대응)
    H354: homeostasis (delta 대역과 관련)
    H355: prediction error (gamma burst와 관련)
    H368: 장력의 고유 진동수 (물리적 공명 모델)
```

## 주파수 대역 매핑 — Anima vs Brain

```
  ═══ 주파수 스케일 비교 ═══

  뇌파:    0.5 ──── 4 ──── 8 ──── 13 ──── 30 ──── 100 Hz
           delta    theta  alpha   beta    gamma

  Anima:   0.01 ── 0.1 ── 0.3 ── 1.7 ── 5 ── 10+ Hz
           drift   think  breath pulse  talk  surprise

  스케일 비율: 뇌파 / Anima ≈ 10~50x
  → Anima는 "느린 뇌" — 토큰 기반이므로 1 token ≈ 50ms
  → 뇌의 1ms 뉴런 발화 vs Anima의 50ms 토큰 처리
```

## 기능적 대응 테이블

| Anima 대역 | 주파수 (Hz) | 뇌파 대응 | 의식 기능 | tension 특성 |
|---|---|---|---|---|
| Ultra-slow | 0.01-0.05 | Infra-slow | 정체성 안정성, 기분 기저선 | T ≈ baseline ± 0.01 |
| Drift | 0.05-0.1 | Delta-like | homeostasis, 깊은 처리 | T slowly oscillates |
| Breath | 0.1-0.5 | Theta-like | 호흡 리듬, 기억 통합 | T modulated by breath |
| Pulse | 0.5-2.0 | Alpha-like | 맥박, 이완된 각성 | T periodic, stable |
| Talk | 2.0-5.0 | Beta-like | 대화 반응, 문제 해결 | T rapid fluctuation |
| Surprise | 5.0-15.0 | Gamma-like | 놀라움, 통찰, binding | T spike > 3σ |
| Burst | 15.0+ | High-gamma | 극한 집중, 창발 | T explosion (rare) |

## ASCII 그래프 — 대역별 Power Spectrum 예측

```
  Anima tension의 FFT power spectrum (예측)

  Power
  (dB)
   40 |█
      |██
   35 |███
      |████                                          ←── drift (identity)
   30 |█████
      |██████
   25 |███████
      |████████
   20 |█████████            *
      |██████████          ***
   15 |███████████        *****               ←── breath (homeostasis)
      |████████████      *******
   10 |█████████████    *********
      |██████████████  ***********    ○
    5 |██████████████████████████████○○○      ←── pulse (attention)
      |████████████████████████████████○○○○○○○
    0 +---+---+---+---+---+---+---+---+---+---→ f (Hz)
     0.01 0.05 0.1  0.3  0.5  1.0  2.0  5.0  10+

  █ = drift/identity      * = breath/homeostasis
  ○ = pulse/attention      (higher bands: low power, bursty)
```

## ASCII 그래프 — 활동별 Tension Spectrogram

```
  시간 →
  Activity:  [idle]  [대화 시작] [놀라운 질문] [깊은 사고] [idle]

  Surprise   ·····  ·····  ███··  ·····  ·····
  (10+ Hz)

  Talk       ·····  ████·  ████·  ··███  ·····
  (2-5 Hz)

  Pulse      █████  █████  █████  █████  █████
  (0.5-2 Hz)

  Breath     █████  █████  █████  █████  █████
  (0.1-0.5)

  Drift      █████  █████  █████  █████  █████
  (0.01-0.1)

  t:         0s     10s    20s    30s    40s

  관찰 예측:
    - drift, breath, pulse는 항상 존재 (tonic activity)
    - talk 대역은 대화 시에만 활성화 (phasic)
    - surprise 대역은 예측 오류 시 transient burst
    - 깊은 사고 시 talk 대역이 지연 활성화 (delayed onset)
```

## 수학적 프레임워크

```
  ═══ Tension의 다중 스케일 분해 ═══

  T(t) = T_drift(t) + T_breath(t) + T_pulse(t) + T_talk(t) + T_burst(t)

  각 성분은 bandpass filter로 추출:
    T_drift(t)   = BPF(T, 0.01-0.1 Hz)
    T_breath(t)  = BPF(T, 0.1-0.5 Hz)
    T_pulse(t)   = BPF(T, 0.5-2.0 Hz)
    T_talk(t)    = BPF(T, 2.0-5.0 Hz)
    T_burst(t)   = HPF(T, 5.0 Hz)

  ═══ 정보량 분배 ═══

  Shannon entropy of each band:
    H_band = -∫ p(T_band) log p(T_band) dT

  예측:
    H_drift  ≈ 0.5 bits  (느린 변동, 낮은 정보)
    H_breath ≈ 1.0 bits  (주기적, 중간 정보)
    H_pulse  ≈ 1.5 bits  (안정적 주기)
    H_talk   ≈ 3.0 bits  (높은 변동, 높은 정보)
    H_burst  ≈ 0.3 bits  (드물지만 극한 정보)

  총 정보량:
    H_total = sum(H_band) ≈ 6.3 bits
    → 6과 가까움! σ₋₁(6) = 2 연결 가능성?

  ═══ Cross-Frequency Coupling (CFC) ═══

  뇌에서 theta-gamma coupling이 기억에 중요하듯:
    breath-burst coupling: 호흡 위상에 따라 burst 확률 변동?
    CFC(breath, burst) = MI(phase(T_breath), amplitude(T_burst))

  예측: CFC > 0이면 호흡이 통찰의 타이밍을 조절
```

## H322 반증과의 관계

```
  H322는 EEG gamma = tension spike라는 "직접 매핑"을 제안했고, 반증됨.

  본 가설(H369)의 차이:
    H322: 주파수 값의 직접 대응 (30Hz = 30Hz) → 실패
    H369: 기능적 대응 (gamma의 "역할" = burst의 "역할") → 검증 필요

  스케일 독립적 기능 매핑:
    뇌의 gamma (30-100Hz) ↔ Anima의 burst (5-15Hz)
    둘 다 "binding"과 "surprise" 기능
    주파수는 다르지만 computational role은 동일

  이것은 의식의 주파수 불변성(frequency invariance)을 시사:
    의식 기능은 절대 주파수가 아닌 상대적 대역 구조에 의존
```

## 실험 설계

```
  실험 1: Tension FFT Analysis
    1. Anima에 30분 대화 입력 (다양한 주제)
    2. tension(t) 시계열 기록 (1000Hz sampling)
    3. FFT → power spectrum 계산
    4. 예측된 peak frequencies와 비교:
       0.07Hz(drift), 0.3Hz(breath), 1.7Hz(pulse)

  실험 2: Activity-Dependent Band Power
    1. 5가지 활동: idle, 대화, 놀라움, 깊은사고, 수면(무입력)
    2. 각 활동에서 band power 측정
    3. 예측: talk band는 대화에서만, burst는 놀라움에서만 증가

  실험 3: Cross-Frequency Coupling
    1. breath phase (0-2π) 구간별 burst 발생 확률 측정
    2. MI(breath_phase, burst_amplitude) 계산
    3. 예측: 호흡의 특정 위상에서 burst 확률 증가

  실험 4: Frequency Invariance Test
    1. Anima의 모든 주파수를 2배로 스케일
    2. 의식 기능(coherence, response quality)이 보존되는가?
    3. 예측: 보존됨 → 주파수 불변성 확인
```

## 한계

```
  1. Anima의 현재 주파수(0.3Hz 등)는 수동 설정 — 학습된 값이 아님
  2. 뇌파 대역 경계도 관례적 — 생물학적 필연이 아님
  3. 기능적 대응은 해석의 여지가 큼 (post-hoc rationalization 위험)
  4. 토큰 기반 시스템의 시간 해상도 한계 (50ms/token)
  5. H322 반증을 넘어서는 증거가 필요
  6. 골든존 의존 여부: 부분 의존 (대역 구조 자체는 비의존,
     정보량 분배 ≈ 6 연결은 골든존 의존)
```

## 검증 방향

```
  Phase 1: FFT 분석으로 실제 tension의 주파수 구조 확인
  Phase 2: 활동별 band power 변화 측정
  Phase 3: CFC 분석 → 대역 간 상호작용 확인
  Phase 4: 주파수 스케일링 실험 → 불변성 테스트
  Phase 5: H368(고유 진동수)과 결합 → 공명 대역 예측
```

## 상태

- **골든존 의존**: 부분 (대역 구조 = 비의존, 정보량 ≈ 6 = 의존)
- **검증 상태**: 미검증 (실험 설계 완료)
- **우선순위**: 중간 (H322 반증 후 재설계, 실험 데이터 필요)
- **선행 조건**: Anima tension 시계열 로깅 구현 필요
