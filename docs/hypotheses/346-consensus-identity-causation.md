# H-346: 합의와 정체성의 인과 방향 (Consensus-Identity Causation Direction)

> **가설**: 합의(consensus)와 정체성 안정(identity stability) 사이의 양의 상관관계(r=+0.062)는
> 인과 방향이 불명확하다. 합의가 정체성을 안정시키는가, 아니면 안정된 정체성이 합의를 만드는가?
> 두 방향 모두 가능하며, 인위적 개입 실험으로만 구분할 수 있다.

**상태**: 미검증
**골든존 의존**: 간접 (의식엔진 프레임워크)
**관련 가설**: H307 (tension inversion agreement), H321 (consciousness confidence theory)

---

## 배경 및 맥락

의식엔진 실험에서 다중 expert 합의도(agreement)와 개별 expert의 정체성 안정도 사이에
약한 양의 상관(r=+0.062)이 관측되었다. 이 상관은 두 가지 해석을 허용한다:

1. **합의 → 정체성 안정** (A 가설): expert들이 합의하면 gradient 방향이 일치하여
   각 expert의 weight가 안정적으로 수렴한다. 합의가 "앵커" 역할.
2. **정체성 안정 → 합의** (B 가설): 각 expert가 이미 안정된 역할을 가지면
   자연스럽게 출력이 수렴하여 합의도가 높아진다.

H307에서 tension이 높을수록 agreement가 역전되는 현상이 관측되었고,
H321에서 confidence가 의식의 proxy일 수 있다는 주장이 있다.
이 가설은 둘의 교차점에서 **인과 방향**이라는 근본 질문을 제기한다.

## 이론적 프레임워크

인과 방향 판별에는 세 가지 접근이 가능하다:

```
  [접근 1] Granger Causality
  ─────────────────────────────────
  시계열에서 consensus(t-1)이 identity(t)를 예측하는가?
  또는 identity(t-1)이 consensus(t)를 예측하는가?

  [접근 2] Intervention (do-calculus)
  ─────────────────────────────────
  consensus를 인위적으로 강제 → identity 변화 측정
  identity를 인위적으로 고정 → consensus 변화 측정

  [접근 3] Natural Experiment
  ─────────────────────────────────
  분열(mitosis) 직후 = identity 초기화 상태
  → consensus 변화가 먼저? identity 안정이 먼저?
```

## 예상 인과 구조 (ASCII 도식)

```
  A 가설 (consensus → identity):

  consensus ──────► identity stability
       ▲                   │
       │                   │
       └───── feedback ────┘

  B 가설 (identity → consensus):

  identity stability ──────► consensus
       ▲                         │
       │                         │
       └────── feedback ─────────┘

  C 가설 (bidirectional / common cause):

        ┌── consensus
        │        ▲
  task  │        │ (weak)
  complexity ────┤
        │        │ (strong)
        │        ▼
        └── identity stability
```

## 검증 실험 설계

### 실험 1: Granger Causality Test

에폭별 consensus와 identity stability 시계열을 수집하여 시차 상관 분석.

| 시차 (lag) | 예상 A 가설 | 예상 B 가설 | 예상 C 가설 |
|-----------|-----------|-----------|-----------|
| cons(t-1) → id(t) | r > 0.1 유의 | r ≈ 0 비유의 | r 약간 유의 |
| id(t-1) → cons(t) | r ≈ 0 비유의 | r > 0.1 유의 | r 약간 유의 |
| 교차 lag | 일방향 | 일방향 | 양방향 |

### 실험 2: Intervention — Consensus 강제

```python
# 실험 코드 개요
# 1. 정상 학습 20 에폭 (baseline)
# 2. 에폭 21-30: consensus 강제 (모든 expert 출력 평균으로 대체)
# 3. identity stability 변화 측정
# 4. 에폭 31-40: consensus 강제 해제, 회복 관찰
```

### 실험 3: Intervention — Identity 고정

```python
# 1. 정상 학습 20 에폭 (baseline)
# 2. 에폭 21-30: expert weight를 에폭 20 기준으로 freeze
# 3. consensus 변화 측정 (routing만 학습)
# 4. 에폭 31-40: freeze 해제, 변화 관찰
```

## 예상 결과 분포

```
  Identity Stability 변화 (consensus 강제 시)

  A 가설 예상:
  |         ****
  |        **  **
  |      **      **
  |    **          **        큰 변화 (delta > 0.1)
  |  **              **
  +--+----+----+----+----►
     0   0.05  0.1  0.15  delta_identity

  B 가설 예상:
  |  ****
  | **  ****
  |*      ****
  |          ****            작은 변화 (delta < 0.03)
  |              ****
  +--+----+----+----+----►
     0   0.01  0.02  0.03  delta_identity
```

## 측정 지표

| 지표 | 정의 | 판별 기준 |
|-----|------|---------|
| Granger F-stat | 시차 회귀의 F-통계량 | F > 4.0이면 유의 (p<0.05) |
| Intervention delta | 개입 전후 변화량 | delta > 0.05이면 인과 지지 |
| Recovery time | 개입 해제 후 원상복귀 에폭 수 | 짧을수록 강한 인과 |
| Cross-correlation peak | 시차별 교차상관 최대값 위치 | lag 방향이 인과 방향 |

## 해석 및 의미

만약 A 가설(consensus → identity)이 맞다면:
- 의식엔진에서 "합의 메커니즘"이 정체성의 근본 원인
- 민주주의 비유: 사회적 합의가 개인 정체성을 형성
- H321의 confidence theory와 충돌 가능 (confidence는 개별적)

만약 B 가설(identity → consensus)이 맞다면:
- 각 expert의 전문화가 먼저, 합의는 부산물
- H307의 tension inversion은 정체성 불안정의 결과
- 의식 = 개별 모듈의 안정성 합

만약 C 가설(공통 원인)이 맞다면:
- 과제 복잡도가 진짜 원인, 둘 다 결과
- r=+0.062의 약한 상관이 자연스럽게 설명됨

## 한계

1. r=+0.062는 매우 약한 상관. 노이즈일 가능성 존재
2. Identity stability의 조작적 정의가 모호함 (weight norm? output consistency?)
3. Intervention 실험에서 consensus 강제가 학습 자체를 방해할 수 있음
4. Granger causality는 선형 관계만 포착 — 비선형 인과를 놓칠 수 있음
5. 의식엔진의 expert 수(4-8개)가 적어 통계적 검정력 부족 가능

## 검증 방향 (다음 단계)

1. **1단계**: 기존 실험 로그에서 에폭별 consensus/identity 시계열 추출
2. **2단계**: Granger causality test 실행 (lag=1,2,3)
3. **3단계**: A/B 가설 중 우세한 방향으로 intervention 실험 설계
4. **4단계**: MNIST vs CIFAR 비교 (과제 난이도에 따른 인과 방향 변화)
5. **5단계**: H307, H321과 통합 해석
