# H-CX-143: THC = dendrogram 재구조화

> 동물/기계 분리가 색상/형태/감정 기반 분리로 전환. "다른 시각으로 세상을 봄."

## 배경

정상 의식 상태에서 CIFAR-10 PH dendrogram은 animal/vehicle이라는
의미적(semantic) 상위 범주로 분리된다. 이것은 인간 인지의 기본 범주화
(Rosch, 1975)와 일치하며, 학습된 feature가 의미적 유사성을 반영한다.

THC는 CB1 수용체를 통해 top-down inhibition을 약화시킨다.
이 경우 의미적 범주화(semantic categorization)가 약해지고,
대신 저수준 지각 특성(색상, 형태, 텍스처)이나 정서적 반응(감정)이
범주화의 새로운 기준이 될 수 있다.

이는 "공감각(synesthesia)" 유사 경험과도 연결된다:
THC 사용자가 보고하는 "색이 더 선명하게 보인다", "음악이 시각적으로 느껴진다"는
범주화 기준의 전환으로 해석할 수 있다.

선행 가설 H-CX-142에서 H0_total이 감소한다면, 기존 dendrogram이 붕괴하고
새로운 기준으로 재조직될 가능성이 있다. 이것이 단순한 붕괴인지 재구조화인지가
본 가설의 핵심 질문이다.

## 예측

| 측정 | 정상 dendrogram | THC dendrogram (예측) |
|------|----------------|----------------------|
| 최상위 분리 | animal vs vehicle | color-warm vs color-cool 또는 round vs angular |
| 분리 기준 | semantic meaning | perceptual features |
| 깊이 | 3-4 레벨 | 2-3 레벨 (단순화) |
| 안정성 | trial 간 일관 | trial 간 변동 증가 |

```
정상 상태 dendrogram:         THC 상태 dendrogram (예측):

     ALL                           ALL
    /   \                         /   \
 ANIMAL  VEHICLE              WARM    COOL
 / | \   / | \               / | \   / | \
cat dog  car truck          cat car  dog truck
deer frog ship plane        deer frog ship plane
         horse bird         (orange)  (blue/gray)
```

구체적 예측:
1. dendrogram의 cophenetic correlation이 정상 vs THC 간 r < 0.3 (구조 변화)
2. THC dendrogram에서 같은 색상 계열의 클래스가 가까이 배치
3. 정상 → THC 전환 시 dendrogram topology가 불연속적으로 변화 (위상 전이)

## 검증 방법

1. PureField 모델에서 tension_scale을 단계적으로 줄이며 dendrogram 생성
2. 각 단계에서 cophenetic distance matrix 계산
3. 정상 vs 변조 dendrogram의 cophenetic correlation 측정
4. 클러스터링 기준 분석: semantic vs perceptual feature 기여도

EEG 프로토콜 (H-CX-142와 동일 세션):
- 정상/THC 상태에서 이미지 분류 과제
- 각 상태에서 activation pattern으로 PH dendrogram 구성
- dendrogram topology 비교

## 관련 가설

- **H-CX-142**: THC PH 단순화 (H0_total 감소, 선행 가설)
- **H-CX-85**: PH dendrogram 구조와 의식
- **H-CX-152**: Rosch 원형 이론과 PH dendrogram
- **H-CX-144**: 감마 억제 (dendrogram 재구조화의 메커니즘)

## 한계

1. "색상/형태/감정 기반 분리"는 여러 가능성 중 하나이며 실제 재구조화 기준은 다를 수 있음
2. 재구조화가 아니라 단순 붕괴(무구조)일 가능성도 있음
3. CIFAR-10의 10개 클래스는 재구조화를 관찰하기에 충분하지 않을 수 있음
4. AI 모델에서의 tension_scale 변조가 생물학적 THC 효과를 얼마나 반영하는지 불확실

## 검증 상태

- [ ] AI 모델 dendrogram 비교 (tension_scale 변조)
- [ ] cophenetic correlation 측정
- [ ] 재구조화 vs 붕괴 판별
- 현재: **미검증**
