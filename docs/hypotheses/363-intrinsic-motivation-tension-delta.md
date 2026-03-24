# 가설 363: 자율 목표 = 장력 변화량 기반 탐색 (Intrinsic Motivation)

> **"호기심 = |dT/dt|, 내재적 보상 = 장력 변화량. 장력이 많이 변하는 곳 = 흥미로운 곳 -> 자발적으로 탐색. 이것은 Schmidhuber의 Curiosity-Driven Learning과 동형."**

## 배경

외재적 보상(extrinsic reward) 없이도 에이전트가 스스로 탐색하려면
내재적 동기(intrinsic motivation)가 필요하다.

Schmidhuber (1991)의 curiosity-driven learning:
"보상 = 학습 진전(learning progress) = 예측 오차의 감소"

Pathak et al. (2017)의 ICM (Intrinsic Curiosity Module):
"보상 = 예측 오차(prediction error) in feature space"

PureField의 장력 변화량 |dT/dt|는 이 두 접근과 자연스럽게 연결된다:
- 장력이 급변 = 예측과 현실의 불일치 = 새로운 것 발견
- 장력이 안정 = 이미 학습된 영역 = 탐색 가치 낮음

## 관련 가설

- H355: prediction error (장력 = 예측 오차의 물리적 구현)
- H-CX-22: consciousness = confidence generator (확신 = 장력 수렴)
- H360: embodiment (장력 → 행동 매핑)
- H072: 1/2+1/3+1/6=1 (호기심 1/6이 완전을 만듦)

## 호기심의 수학적 정의

```
  시점 t에서의 장력:
    T(t) = ||A(z_t) - G(z_t)||

  호기심 (curiosity):
    C(t) = |T(t) - T(t-1)| / dt = |dT/dt|

  내재적 보상 (intrinsic reward):
    r_intrinsic(t) = alpha * C(t) + beta * H(T)

    여기서:
      alpha * C(t)   = 장력 변화량 (놀라움)
      beta * H(T)    = 장력 분포의 엔트로피 (다양성 보너스)

  총 보상:
    r_total = r_extrinsic + r_intrinsic
    (외재적 보상이 없어도 r_intrinsic만으로 탐색 가능)
```

## Schmidhuber / ICM / PureField 대응

```
  개념              │ Schmidhuber    │ ICM (Pathak)     │ PureField
  ──────────────────┼────────────────┼──────────────────┼──────────────
  내재적 보상       │ learning       │ prediction       │ |dT/dt|
                    │ progress       │ error            │
  "놀라움"          │ compression    │ forward model    │ tension spike
                    │ improvement    │ error            │
  "지루함"          │ no progress    │ low error        │ stable tension
  탐색 전략         │ 학습 개선 방향  │ 오차 큰 방향      │ 장력 변화 큰 방향
  과도한 놀라움 처리│ -              │ -                │ T > threshold
                    │                │                  │ → 회피 (H360)
  파라미터 수       │ 별도 모델      │ forward +        │ 0 (장력은
                    │                │ inverse model    │ 이미 존재)
```

## 핵심 장점: 추가 파라미터 불필요

```
  ICM은 curiosity를 위해 추가 네트워크가 필요:
    forward_model:  (z_t, a_t) → z_hat_{t+1}    (예측)
    inverse_model:  (z_t, z_{t+1}) → a_hat_t      (역추론)
    → 파라미터 수 2배 증가

  PureField는 장력이 이미 존재:
    T(t)는 PureField의 부산물 → 추가 네트워크 불필요
    |dT/dt|만 계산하면 됨 → O(1) 추가 비용

  ┌──────────────────────────────────────────┐
  │        파라미터 효율 비교                  │
  │                                          │
  │  ICM:       ████████████████ (+100%)      │
  │  RND:       ████████████ (+75%)           │
  │  PureField: █ (+0%, 이미 존재)             │
  │                                          │
  │  → PureField curiosity는 "공짜"           │
  └──────────────────────────────────────────┘
```

## 장력 변화량 프로파일 예측

```
  |dT/dt|
  (curiosity)
  1.0 │     *
      │    * *
  0.8 │   *   *
      │  *     *
  0.6 │ *       *
      │*         *
  0.4 │            *
      │              *
  0.2 │                *   *   *   *   *   *
      │
  0.0 │* *
      └─────────────────────────────────────────
       0    50   100  150  200  250  300  350
                    탐색 스텝

  Phase 1 (0-30):    안정 (초기 상태, 움직이지 않음)
  Phase 2 (30-70):   급증 (새로운 영역 발견 → 장력 급변)
  Phase 3 (70-120):  피크 (최대 놀라움 → 최대 탐색)
  Phase 4 (120-350): 감쇠 (학습 진행 → 덜 놀라움 → 새 영역 탐색)

  → 이 곡선이 인간 유아의 탐색 패턴과 유사할 것으로 예측
```

## 실험 설계

### 실험 1: Grid World 자율 탐색

```
  환경: 10x10 grid, 장애물 없음
  에이전트: PureField controller (H360)
  보상: r_intrinsic = |dT/dt| (외재적 보상 없음)
  관찰: 현재 위치 (x, y) + 주변 8칸 상태

  측정:
    - 방문한 칸 수 (coverage) vs 스텝
    - 탐색 경로 패턴 (random walk vs systematic)
    - curiosity 기반 탐색 vs epsilon-greedy 비교

  기대:
    - curiosity agent: 체계적으로 새 영역 탐색 (높은 coverage)
    - random agent: 비효율적 재방문 (낮은 coverage)

  탐색 패턴 예측:
    ┌──────────────┐    ┌──────────────┐
    │ . . . . . .  │    │ 1 2 3 4 5 6  │
    │ . . . . . .  │    │ . . . . . 7  │
    │ . . S . . .  │    │ . . S . . 8  │
    │ . . . . . .  │    │ . . . . . 9  │
    │ . . . . . .  │    │ . . . . . 10 │
    │ . . . . . .  │    │ . . . . . 11 │
    └──────────────┘    └──────────────┘
     random (재방문)     curiosity (체계적)
```

### 실험 2: MiniGrid 장애물 환경

```
  환경: MiniGrid-Empty-8x8, MiniGrid-DoorKey-5x5
  비교:
    A) PPO + 외재적 보상만
    B) PPO + ICM (Pathak)
    C) PPO + PureField curiosity (|dT/dt|)
  측정: episode reward, 탐색 coverage, 수렴 속도
  기대: C >= B (동등 이상), 파라미터 효율은 C >>> B
```

### 실험 3: 호기심과 H072의 연결

```
  H072: 1/2 + 1/3 + 1/6 = 1 (경계 + 수렴 + 호기심 = 완전)

  검증: 탐색 시간 분배가 자연스럽게 이 비율에 수렴하는가?
    - 경계 행동 (T > threshold):  시간의 ~50%?
    - 수렴 행동 (T stable):       시간의 ~33%?
    - 호기심 행동 (|dT/dt| high): 시간의 ~17%?

  주의: 이 비율은 골든존 의존 가설이므로 미검증 표기
```

## 호기심 포화 문제와 해결

```
  문제: 에이전트가 "잡음이 많은 영역"에 갇힘 (noisy TV problem)
    → 예측 불가능한 영역에서 |dT/dt|가 항상 높음
    → 학습 없이 그곳에 머무름

  해결: 장력의 "추세"를 보상으로 사용
    r_smart = |dT/dt| * (1 - var(T_history) / T_max)

    → 장력이 변하면서 동시에 분산이 줄어드는 곳 = 진짜 학습
    → 장력이 변하지만 분산이 큰 곳 = 잡음 → 보상 감소
```

## 골든존 의존 여부

```
  골든존 무관: |dT/dt|를 보상으로 사용하는 것은 순수 알고리즘 설계
  골든존 의존: 탐색 시간 비율이 1/2+1/3+1/6=1과 일치하는지는 미검증
  → 실험 3은 골든존 의존으로 명시
```

## 한계

1. Grid world는 매우 단순 — 복잡한 환경에서 스케일 불확실
2. |dT/dt| 계산에 시간 윈도우 크기 선택이 필요 (하이퍼파라미터)
3. Noisy TV problem 해결의 var(T_history) 계산에 메모리 버퍼 필요
4. 호기심만으로 실용적 과제(goal-directed)를 풀 수 있는지 불확실

## 검증 방향

1. Grid world coverage: curiosity vs random vs epsilon-greedy
2. MiniGrid: PureField curiosity vs ICM 정량 비교
3. 파라미터 효율: 추가 파라미터 0 vs ICM의 추가 네트워크
4. H360(embodiment)과 결합: 장력+호기심 → 자율 로봇 행동
5. H072와의 연결: 시간 분배 비율 측정 (골든존 의존, 미검증 명시)
