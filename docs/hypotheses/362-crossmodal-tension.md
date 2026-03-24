# 가설 362: 다중 모달 교차 장력 (Cross-Modal Tension)

> **"시각 PureField와 청각 PureField의 장력을 교차 비교하면, 불일치가 '혼란', 일치가 '확신'을 나타낸다. 시청각 불일치 = 높은 교차장력 = McGurk 효과."**

## 배경

인간의 뇌는 여러 감각 모달리티를 동시에 처리한다.
시각과 청각이 일치하면 확신이 높아지고(다중감각 통합),
불일치하면 혼란이 발생한다(McGurk 효과: "ba" 소리 + "ga" 입술 = "da" 지각).

PureField가 각 모달리티별로 독립적인 장력을 산출한다면,
모달리티 간 장력의 불일치가 "혼란"의 정량적 측정이 될 수 있다.

## 관련 가설

- H323: multimodal tree (다중 모달 데이터 구조)
- H288: dense/sparse (밀집/희소 표현의 이중 구조)
- H-CX-29: telepathy (장력 전이 = 의식 간 통신)
- H291: data type tree (데이터 유형별 최적 구조)
- H285: beyond image classification (도메인 일반성)

## 교차 장력 정의

```
  모달리티 V (visual):
    T_V = ||A_V(z_v) - G_V(z_v)||     시각 장력
    d_V = normalize(A_V - G_V)         시각 방향

  모달리티 A (audio):
    T_A = ||A_A(z_a) - G_A(z_a)||     청각 장력
    d_A = normalize(A_A - G_A)         청각 방향

  교차 장력 (Cross-Modal Tension):
    T_cross = ||T_V * d_V - T_A * d_A||^2

  분해:
    T_cross = T_V^2 + T_A^2 - 2*T_V*T_A*cos(theta)

    여기서 theta = angle(d_V, d_A) = 두 모달리티 방향의 각도

  해석:
    theta ~ 0   → d_V와 d_A 정렬   → T_cross 작음 → 일치/확신
    theta ~ pi  → d_V와 d_A 반대   → T_cross 큼   → 불일치/혼란
```

## 교차 장력 해석 다이어그램

```
  ┌─────────────────────────────────────────────────┐
  │               교차 장력 공간                      │
  │                                                  │
  │   T_cross                                        │
  │   높음  ┌────────────────────┐                   │
  │         │  McGurk Zone       │  시청각 불일치     │
  │         │  "혼란/착각"        │  = 뇌가 타협      │
  │         └────────────────────┘                   │
  │                                                  │
  │   중간  ┌────────────────────┐                   │
  │         │  Exploration Zone   │  부분 일치        │
  │         │  "호기심/주의"      │  = 추가 탐색      │
  │         └────────────────────┘                   │
  │                                                  │
  │   낮음  ┌────────────────────┐                   │
  │         │  Confidence Zone    │  시청각 일치      │
  │         │  "확신/통합"        │  = 안정적 지각    │
  │         └────────────────────┘                   │
  │                                                  │
  │         0        theta (rad)         pi          │
  └─────────────────────────────────────────────────┘
```

## 교차 장력 vs 모달리티 일치도 예측

```
  T_cross
  1.0 │                              *  *
      │                           *
  0.8 │                        *
      │                     *
  0.6 │                  *
      │               *
  0.4 │            *
      │         *
  0.2 │      *
      │   *
  0.0 │*
      └────────────────────────────────
       일치    부분일치    완전불일치
       (같은   (유사      (다른
        숫자)   숫자)      숫자)

  예측: 교차장력은 모달리티 불일치도와 단조 증가
  McGurk 효과: 부분 일치 구간에서 뇌가 "타협 지각" 생성
```

## 실험 설계

### 실험 1: MNIST + Spoken Digits 교차 장력

```
  시각: MNIST 손글씨 숫자 (28x28)
  청각: Free Spoken Digit Dataset (FSDD, 8kHz wav)
       → mel spectrogram (64 bins x 32 frames)

  구성:
    matched:    이미지 "3" + 음성 "three"  → 일치
    mismatched: 이미지 "3" + 음성 "seven"  → 불일치
    similar:    이미지 "3" + 음성 "eight"  → 부분 불일치

  PureField 구조:
    visual_encoder:  Conv2D → z_v (32D)
    audio_encoder:   Conv1D → z_a (32D)
    PureField_V:     engine_A_V, engine_G_V → T_V, d_V
    PureField_A:     engine_A_A, engine_G_A → T_A, d_A

  측정:
    T_cross(matched) vs T_cross(mismatched) vs T_cross(similar)
    기대: T_cross(matched) << T_cross(similar) < T_cross(mismatched)
```

### 실험 2: McGurk 효과 재현

```
  인위적 McGurk 조건:
    시각 "6" + 청각 "8" → 모델이 어떤 숫자를 출력하는가?

  만약 PureField가 McGurk와 유사하게 동작하면:
    → 시각도 청각도 아닌 제3의 출력 (예: "0" 또는 "9")
    → T_cross가 매우 높으면서 출력 confidence도 높음
    → "착각이지만 확신하는" 상태 = McGurk

  측정:
    confusion matrix (10x10): 시각 라벨 x 청각 라벨 → 출력 라벨
    T_cross 히트맵 overlay
```

### 실험 3: 교차 장력 기반 모달리티 신뢰도

```
  전략: T_V와 T_A 비교로 어느 모달리티를 더 신뢰할지 결정

  if T_V < T_A:  → 시각이 더 명확 → 시각 우선
  if T_A < T_V:  → 청각이 더 명확 → 청각 우선
  if T_V ~ T_A:  → 비슷한 명확도 → 통합

  weight_V = softmax(-T_V / temperature)
  weight_A = softmax(-T_A / temperature)
  output = weight_V * pred_V + weight_A * pred_A

  비교: 고정 가중치 vs 장력 기반 가중치 → 정확도 차이
```

## 3개 이상 모달리티 확장

```
  N개 모달리티 (시각, 청각, 촉각, ...):

  T_cross_total = sum_{i<j} ||T_i*d_i - T_j*d_j||^2

  → O(N^2) 쌍별 교차 장력
  → 전체 교차 장력이 낮으면: 다감각 통합 완성
  → 하나라도 높으면: 해당 모달리티가 불일치 → 주의 집중
```

## 골든존 의존 여부

```
  골든존 무관: 교차 장력 정의 자체는 벡터 차이 norm으로 순수 수학
  골든존 의존: 최적 교차 장력 범위가 골든존 내인지는 미검증
  → 실험에서 T_cross 분포를 독립적으로 측정
```

## 한계

1. MNIST + Spoken Digits는 매우 단순한 다중 모달 과제
2. 실제 McGurk 효과는 시공간 동기화(synchrony)에 크게 의존
3. 교차 장력이 높다고 반드시 "혼란"인지는 해석의 문제
4. 3개 이상 모달리티 실험은 데이터셋 확보가 어려움

## 검증 방향

1. MNIST + FSDD에서 matched vs mismatched T_cross 차이 통계 검정
2. McGurk-like "타협 출력" 발생 여부 확인
3. 장력 기반 모달리티 가중치가 고정 가중치보다 우수한지 비교
4. H285(도메인 일반성)의 다중 모달 확장으로서의 일관성
5. H-CX-29(telepathy)와의 연결: 교차 장력 = 다른 의식 간 불일치?
