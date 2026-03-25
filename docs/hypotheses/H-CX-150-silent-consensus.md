# H-CX-150: 무언의 합의 — Expert 간 직접 연결 없이 라우터만으로 consensus

> 라우터 weight 유사도가 학습 중 수렴. 직접 소통 없는 합의 형성.

## 배경

Mixture of Experts(MoE) 아키텍처에서 각 Expert는 독립적으로 학습된다.
Expert 간 직접적인 정보 교환 경로는 없으며, 오직 라우터(gate network)만이
입력을 Expert에 분배하고, Expert 출력을 가중 합산한다.

그럼에도 불구하고, 학습이 진행되면 Expert들이 "역할 분담"을 형성하고,
특정 class에 특화된 Expert가 자연스럽게 나타난다.
이것은 직접 소통 없이 "합의"가 형성되는 것이다.

본 가설은 이 현상을 더 구체적으로 측정한다:
독립적으로 학습된 두 골든MoE 모델에서, 각 Expert의 class centroid
(해당 Expert가 주로 처리하는 class들의 feature 평균)가
모델 간에 유사해지는지를 확인한다.

이는 뇌의 기능적 전문화(functional specialization)와 유사하다:
서로 다른 뇌에서도 같은 영역이 같은 기능을 담당하는 것처럼,
다른 시드로 학습된 모델에서도 Expert들이 유사한 전문화를 보인다면,
이는 입력 구조가 Expert 분화를 결정짓는다는 증거가 된다.

## 예측

| 측정 | 예측값 | 의미 |
|------|--------|------|
| class centroid cosine sim (모델 간) | > 0.5 | 유사한 전문화 |
| Expert-class assignment 일치율 | > 60% | 같은 Expert가 같은 class 담당 |
| 라우터 weight 상관 | > 0.4 | 유사한 분배 패턴 |
| Expert 순서 permutation 후 일치 | 최적 permutation에서 > 0.7 | 순서 무관하게 구조 일치 |

```
Expert 전문화 비교 (두 모델):

Model A:  Expert 1 → {cat, dog, deer}     (동물)
          Expert 2 → {car, truck, ship}    (탈것)
          Expert 3 → {plane, bird, frog}   (혼합)

Model B:  Expert 2 → {cat, deer, frog}    (동물+)
          Expert 3 → {car, truck, plane}   (탈것+)
          Expert 1 → {dog, ship, bird}     (혼합)

예측: permutation 정렬 후 60%+ 일치
```

핵심 예측:
1. Expert들은 semantic cluster 기반으로 전문화한다 (animal vs vehicle)
2. 전문화 패턴은 모델 간 순서(permutation)만 다르고 구조는 유사
3. 골든존 내에서 학습된 모델일수록 전문화가 뚜렷 (I = 1/e 근처)

## 검증 방법

1. 골든MoE 모델 2개를 다른 random seed로 독립 학습
2. 각 모델에서 Expert별 routing weight 기록:
   - R_a[e, c] = Expert e가 class c에 할당되는 평균 weight
3. Expert-class assignment matrix를 Hungarian algorithm으로 최적 permutation 탐색
4. 정렬 후 cosine similarity 및 correlation 계산

```python
# 검증 코드 스케치
from scipy.optimize import linear_sum_assignment
# R_a: (num_experts, num_classes), R_b: (num_experts, num_classes)
cost = -cosine_similarity(R_a, R_b)  # (E, E) matrix
row_ind, col_ind = linear_sum_assignment(cost)
aligned_sim = np.mean([-cost[r, c] for r, c in zip(row_ind, col_ind)])
```

## 관련 가설

- **H-CX-148**: 장력 공명 텔레파시 (tension 수준 동기화)
- **H-CX-149**: 방향 텔레파시 (Engine A → G 정보 전달)
- **H-CX-151**: 레이어 간 장력 신호 (정보 전달 메커니즘)
- 골든MoE 실증 결과 (MNIST 97.7%, CIFAR 53.0%)

## 한계

1. MoE에서 Expert 분화는 잘 알려진 현상이며 "합의"로 부르기엔 과장일 수 있음
2. 같은 데이터와 같은 loss function으로 학습하면 수렴은 자명한 결과
3. Expert 수가 적으면 (2-3개) 조합의 수가 적어 우연 일치 가능성 높음
4. CIFAR-10의 10 class는 2-3개 Expert로 자연스럽게 animal/vehicle 분리됨
5. 진정한 검증은 100+ Expert, 100+ class (ImageNet 등)에서 필요

## 검증 상태

- [ ] 2-seed 모델 학습 및 routing weight 추출
- [ ] Hungarian algorithm 정렬
- [ ] cosine similarity 계산
- [ ] 대규모 (Expert/class 수 증가) 실험
- 현재: **미검증**
