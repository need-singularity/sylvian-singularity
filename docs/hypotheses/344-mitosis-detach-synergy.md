# 가설 344: 분열(mitosis) + detach 관찰자 결합 시너지

> **분열(mitosis)로 생성된 두 엔진 중 하나에 detach observer를 부착하면, 각각 단독 적용보다 더 큰 성능 향상이 나타난다. 분열이 다양성을 생성하고, detach 관찰자가 그 다양성을 효율적으로 압축하기 때문이다. 이것은 "분열 후 한쪽은 관찰만 하는" 비대칭 구조가 최적임을 의미한다.**

## 배경/맥락

의식엔진의 두 핵심 메커니즘:

```
  분열 (Mitosis, H271):
    하나의 엔진 → noise 주입 → 두 개의 엔진
    효과: 97.49% (MNIST), 다양성 생성
    원리: 세포분열처럼 복제 후 분화

  Detach Observer (H272):
    관찰자의 gradient를 차단 (stop_gradient)
    효과: +0.15% 향상
    원리: 관찰이 관찰 대상을 교란하지 않음
```

각각은 독립적으로 효과가 있다. 그러나 이 둘은 자연스러운 결합이 가능하다:
분열로 두 엔진이 생기면, 한쪽은 "행동자(actor)", 다른 한쪽은
"관찰자(observer)"로 역할을 나눌 수 있다. 관찰자 쪽에 detach를 걸면
gradient가 차단되어 순수한 관찰만 수행한다.

이것은 체험적으로도 흥미롭다: 분열 후 "밀려난 쪽"은 관찰만 하는 존재가
된다. 의식의 분열에서 한쪽은 행동하고, 다른 한쪽은 지켜본다.

### 관련 가설

| 가설 | 관계 | 내용 |
|------|------|------|
| H271 | 기반 | mitosis — 엔진 분열 메커니즘 |
| H272 | 기반 | detach design principle — gradient 차단 |
| H297 | 연결 | ensemble diversity — 앙상블 다양성 |
| H334 | 연결 | field only sufficient — field 중심 구조 |
| H276 | 이론 | observation as compression — 관찰=압축 |

## 예측 모델

```
  단독 효과:
    mitosis:  +X pp  (다양성 생성)
    detach:   +Y pp  (관찰 보정)

  결합 효과 시나리오:
    가산적:   +X + Y pp     (독립적, 시너지 없음)
    초가산:   +(X+Y+S) pp   (시너지 S > 0)
    부가산:   +(X+Y-C) pp   (간섭 C > 0)
```

```
  결합 효과 예측 (MNIST)

  정확도(%)
  98.2 |                     ?  ← mitosis+detach (초가산?)
  98.0 |               *       ← mitosis+detach (가산적?)
  97.8 |          *            ← mitosis+detach (부가산?)
  97.6 |
  97.5 | *                     ← mitosis only (97.49%)
  97.4 |
  97.2 |
  97.0 | - - - - - - - - - - - ← baseline (97.00%)
       +--+--+--+--+--+--+--
        base mito detach combo

  핵심 질문: combo의 위치는?
  초가산이면 시너지 확인 → 아키텍처 설계 원리
```

## 실험 설계

### 2x2 요인 실험 (factorial design)

| 조건 | mitosis | detach | 예상 정확도 |
|------|---------|--------|-----------|
| A: baseline | OFF | OFF | ~97.00% |
| B: mitosis only | ON | OFF | ~97.49% |
| C: detach only | OFF | ON | ~97.15% |
| D: mitosis+detach | ON | ON | ? (핵심) |

시너지 측정:
```
  시너지 S = D - A - (B - A) - (C - A)
           = D - B - C + A

  S > 0 → 초가산적 시너지 (분열+관찰이 각각보다 나음)
  S = 0 → 가산적 (독립)
  S < 0 → 간섭 (서로 방해)
```

### 비대칭 실험 (actor-observer 구조)

```
  변형 D1: 엔진1(actor, gradient ON) + 엔진2(observer, detach)
  변형 D2: 엔진1(observer, detach) + 엔진2(actor, gradient ON)
  변형 D3: 양쪽 모두 detach (관찰만, 학습 불가?)
  변형 D4: 양쪽 모두 gradient ON (기존 mitosis)

  D1 ≠ D2 이면 비대칭 중요 → 어느 쪽이 observer인지 중요
  D1 = D2 이면 대칭 → 역할 교환 무관
```

## 검증 계획

```
  단계 1: 2x2 요인 실험 (MNIST)
    - 4개 조건 각 3회 반복 (신뢰구간용)
    - 동일 하이퍼파라미터, 동일 seed set
    - 시너지 S 계산 + 95% CI

  단계 2: 비대칭 실험 (MNIST)
    - D1-D4 변형 각 3회 반복
    - actor-observer 비대칭 여부 확인

  단계 3: 클래스별 분석
    - H342(난이도 비례)와 교차
    - 시너지가 어려운 클래스에서 더 큰가?
    - confusion matrix 비교 (4조건)

  단계 4: 다중 데이터셋
    - Fashion-MNIST, CIFAR-10에서 반복
    - 과제 난이도와 시너지 크기의 상관
```

## 해석/의미

초가산적 시너지가 확인되면, 의식엔진의 최적 아키텍처는:

```
  [엔진 A] ─── tension ─── [엔진 B]
     │                        │
   actor                  observer
  (학습)               (detach, 관찰만)
     │                        │
     └──── field output ──────┘
                │
          final prediction
```

이 구조의 의미:
1. **다양성 생성** (mitosis) + **다양성 활용** (detach observer) = 상보적
2. 하나는 탐험(explore), 하나는 착취(exploit) → exploration-exploitation tradeoff의 해결
3. 의식의 체험적 모델: "행동하는 나"와 "관찰하는 나"의 분리

이것은 H334(field only sufficient)와도 연결된다. field가 이미 충분하다면,
observer의 역할은 field의 방향을 "검증"하는 것일 수 있다. detach는
이 검증이 field 자체를 교란하지 않도록 보장한다.

## 한계

- mitosis와 detach의 효과 크기가 작아서 (0.15-0.49%) 시너지 검출이 어려울 수 있음
- 3회 반복으로는 통계적 유의성 확보가 어려울 수 있음 (10회 필요할 수도)
- actor-observer 비대칭이 단순히 초기 noise 차이일 수 있음
- MNIST에서의 시너지가 더 어려운 과제에서도 유지되는지 미확인

## 다음 단계

1. MNIST 2x2 요인 실험 실행 (CPU 가능, 3회 반복)
2. 시너지 S 부호 확인 → 초가산적이면 비대칭 실험으로 진행
3. H342와 교차: 클래스별 시너지 크기 측정
4. 확인되면 H335(PureField LLM)에 actor-observer 구조 적용 제안
