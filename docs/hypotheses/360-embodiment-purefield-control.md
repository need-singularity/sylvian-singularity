# 가설 360: 신체 = PureField 제어기 (RC-7 Embodiment)

> **"PureField의 장력을 로봇/시뮬레이터의 제어 신호로 변환하면, 장력이 높은 쪽으로 '주의'가 가고 행동이 발생한다. tension -> action mapping. 높은 장력 = 위험/관심 = 즉각 반응."**

## 배경

의식엔진의 PureField는 입력에 대해 장력(tension)을 산출한다.
이 장력은 현재 분류/이상탐지 등 "판단"에만 사용된다.
하지만 생물의 뇌는 판단과 동시에 행동을 만든다 -- 주의(attention)가
곧 행동(action)으로 이어지는 것이 embodied cognition의 핵심이다.

RC-7(로봇 신체)는 PureField 출력을 제어 루프에 직결하는 구조를 제안한다.

## 관련 가설

- H287: anomaly = 위험, 높은 장력 → 경보 (장력의 의미론적 해석)
- H355: prediction error → intrinsic reward (장력 변화 = 보상)
- H-CX-22: consciousness = confidence generator (확신 = 낮은 장력)
- H335: PureField LLM design (PureField의 신경망 통합)

## 핵심 구조: 감각-장력-행동 루프

```
  ┌─────────────────────────────────────────────────┐
  │                   환경 (Environment)              │
  │   MuJoCo / Gymnasium / 실제 로봇                  │
  └───────┬─────────────────────────────┬─────────────┘
          │ 관찰(obs)                    ↑ 행동(action)
          ▼                             │
  ┌───────────────┐              ┌──────┴────────┐
  │  감각 인코더   │              │  행동 디코더   │
  │  obs → z      │              │  T,d → action  │
  └───────┬───────┘              └──────┬────────┘
          │ 잠재 벡터 z                  ↑ (T, direction)
          ▼                             │
  ┌─────────────────────────────────────┴─────────┐
  │              PureField 엔진                     │
  │                                                │
  │   engine_A(z)  ──→  attraction (무엇이 정상?)   │
  │   engine_G(z)  ──→  repulsion  (무엇이 이상?)   │
  │                                                │
  │   tension T = ||A(z) - G(z)||                  │
  │   direction d = normalize(A(z) - G(z))         │
  │                                                │
  │   T 높음 → 위험/관심 → 즉각 반응               │
  │   T 낮음 → 안전/무관 → 탐색/대기               │
  └────────────────────────────────────────────────┘
```

## 장력-행동 매핑 전략

```
  전략 1: Direct Mapping
    action = f(T, d) = T * W_action @ d
    → 장력 크기가 행동 강도, 방향이 행동 종류 결정

  전략 2: Threshold + Priority Queue
    if T > T_critical:   → 즉각 회피/접근 (reflexive)
    elif T > T_medium:   → 계획된 행동 (deliberate)
    else:                → 자유 탐색 (exploration)

  전략 3: Reward Signal (RL 결합)
    reward = -T  (장력 최소화 = 편안한 상태 추구)
    또는
    reward = |dT/dt|  (장력 변화 = 흥미 = H363과 연결)
```

## 장력 크기별 행동 예측

```
  Tension │  해석      │  행동         │  생물 대응
  ────────┼────────────┼───────────────┼──────────────
  0.0-0.2 │  안전      │  자유 탐색     │  이완, 놀이
  0.2-0.5 │  관심      │  접근/조사     │  호기심
  0.5-0.8 │  경계      │  신중한 접근   │  긴장
  0.8-1.0 │  위험      │  즉각 회피     │  투쟁-도주
```

## 예상 장력-반응시간 곡선

```
  반응시간(ms)
  500 │*
      │  *
  400 │    *
      │      *
  300 │        *
      │          *
  200 │            *  *
      │                 *
  100 │                    *  *  *
      │
    0 └──────────────────────────────
      0.0  0.2  0.4  0.6  0.8  1.0
                 Tension T

  예측: T가 높을수록 반응시간 감소 (Yerkes-Dodson 유사)
  단, T > 0.9에서 freezing 발생 가능 (과부하)
```

## 실험 설계

### 실험 1: CartPole (기초)

```
  환경: gymnasium CartPole-v1
  관찰: [cart_pos, cart_vel, pole_angle, pole_vel] → z (4D)
  PureField: engine_A, engine_G 각각 2-layer MLP
  행동: tension > threshold → push left/right (direction 기반)
  비교: PPO baseline vs PureField controller
  측정: episode reward, 수렴 속도, 행동 해석가능성
```

### 실험 2: MuJoCo Ant (연속 제어)

```
  환경: gymnasium Ant-v4
  관찰: 111D proprioception → z (32D via encoder)
  PureField: 장력 = 각 관절별 토크 크기 결정
  방향 = 관절 토크 부호 결정
  비교: SAC baseline vs PureField-SAC hybrid
  핵심 질문: 장력이 "위험한 자세"를 자동 감지하는가?
```

### 실험 3: 실시간 장력 시각화

```
  도구: wandb 또는 matplotlib animation
  표시: 에이전트 위치 + 장력 히트맵 + 행동 벡터
  목적: PureField가 "주의"를 어디에 두는지 시각적 확인
```

## 골든존 의존 여부

```
  골든존 무관: PureField 자체는 신경망 구조이며 골든존에 의존하지 않음
  골든존 의존: tension의 "최적 범위"가 골든존 [0.21, 0.50]인지는 미검증
  → 실험에서 최적 tension 범위를 측정하여 골든존과 비교 필요
```

## 한계

1. PureField controller가 RL policy보다 학습 효율이 낮을 수 있음
2. 연속 행동 공간에서 direction → action 매핑이 비자명
3. 장력 기반 "반사 행동"이 최적이 아닐 수 있음 (탐색 부족)
4. MuJoCo 시뮬레이션이 실제 로봇과 크게 다를 수 있음 (sim-to-real gap)

## 검증 방향

1. CartPole에서 PureField controller의 기본 동작 확인
2. 장력-반응시간 곡선이 Yerkes-Dodson 형태인지 측정
3. 장력 히트맵이 환경의 "위험 지역"과 상관관계를 보이는지 확인
4. H287(anomaly=높은 장력)과의 일관성 검증
5. H363(호기심=장력 변화량)과 결합 시 자율 탐색 능력 향상 여부
