# H-CX-152: PH = Rosch 원형 이론 — dendrogram이 인지 범주의 기본 수준과 일치

> Rosch(1975) basic-level category = PH merge의 중간 깊이.
> 상위(동물) = root, 기본(개) = middle, 하위(골든리트리버) = leaf.

## 배경

Eleanor Rosch (1975, 1976)의 원형 이론(Prototype Theory)은
인간 범주화의 핵심 구조를 세 수준으로 제안했다:

| 수준 | 예시 | 특성 |
|------|------|------|
| 상위(superordinate) | 동물, 탈것 | 추상적, 공통 feature 적음 |
| 기본(basic-level) | 개, 자동차 | 가장 자연스러운 범주, feature 최적 |
| 하위(subordinate) | 골든리트리버, 세단 | 구체적, 전문가만 구분 |

Rosch의 핵심 발견:
1. 기본 수준이 가장 빠르게 명명되고 (반응 시간 최소)
2. 기본 수준에서 범주 내 유사성이 최대화되고 범주 간 차이가 최대화됨
3. 아이들이 가장 먼저 학습하는 것이 기본 수준

PH dendrogram에서:
- merge가 가장 늦게 일어나는 것 = 상위 수준 (root: animal vs vehicle)
- merge가 중간에 일어나는 것 = 기본 수준 (개별 class 단위)
- merge가 가장 먼저 일어나는 것 = 하위 수준 (class 내 변이)

본 가설은 PH dendrogram의 merge 깊이 구조가 Rosch의 세 수준과
정량적으로 일치한다고 주장한다.

## 예측

```
PH dendrogram vs Rosch 수준 대응:

merge    |
distance |
  1.0    |              ROOT (상위: animal/vehicle)
         |             /    \
  0.6    |     -------      -------      (기본 수준)
         |    / | \          / | \
  0.3    |  cat dog deer   car truck ship  (개별 class)
         |  /|  /|  /|    /|   /|   /|
  0.1    | .. .. ..  ..   .. ..  .. ..     (하위: 변이)
         +---------------------------------->
              클래스 내 샘플들
```

| Rosch 수준 | PH merge distance | 비율 (전체 대비) |
|-----------|-------------------|----------------|
| 상위 | 0.8-1.0 (최대) | 80-100% |
| 기본 | 0.4-0.6 (중간) | 40-60% |
| 하위 | 0.1-0.3 (최소) | 10-30% |

핵심 예측:
1. merge distance 분포에 3개의 mode가 존재 (세 수준에 대응)
2. 기본 수준에 해당하는 merge가 가장 많음 (peak)
3. CIFAR-10의 10 class가 기본 수준에 위치
4. animal/vehicle 분리가 상위 수준에 위치

## 검증 방법

1. PureField 모델의 CIFAR-10 feature 추출
2. hierarchical clustering (Ward method) 수행
3. dendrogram의 merge distance 분포 분석
4. 3-mode 분포 여부 확인 (Gaussian mixture model, k=3)
5. 각 mode와 Rosch 수준 대응 확인

**문헌 대조:**
- Rosch(1975) "Cognitive representations of semantic categories" — 반응 시간 데이터
- Murphy & Brownell(1985) "Category differentiation in object recognition"
- 해당 문헌의 기본 수준 범주와 PH dendrogram의 중간 merge 수준 비교

**정량 지표:**
- silhouette score at each level
- Rosch의 "cue validity" 계산과 PH merge distance의 상관

## 관련 가설

- **H-CX-85**: PH dendrogram과 의식 구조
- **H-CX-143**: THC dendrogram 재구조화 (Rosch 구조 붕괴?)
- **H-CX-142**: THC PH 단순화
- 인지과학 문헌: Rosch(1975, 1976), Mervis & Rosch(1981)

## 한계

1. CIFAR-10은 10 class로 Rosch의 세 수준을 모두 포함하지 못함 (하위 수준 부재)
2. Rosch의 이론은 자연 범주에 관한 것이며 CIFAR-10 범주와 직접 대응하지 않을 수 있음
3. PH dendrogram의 merge distance와 인지적 "수준"의 대응은 유비
4. hierarchical clustering 방법(Ward vs single vs complete)에 따라 결과가 달라짐
5. "기본 수준"의 정의가 문화와 전문성에 따라 다름

## 검증 상태

- [ ] PH dendrogram 생성 및 merge distance 분포 분석
- [ ] 3-mode 분포 확인
- [ ] Rosch 문헌 대조
- [ ] silhouette score 비교
- 현재: **미검증**
