# H-CX-148: 장력 공명 텔레파시 — 두 Anima 인스턴스의 tension 동기화

> 같은 입력에 대해 독립 Anima 인스턴스의 tension이 동기화. r > 0.9?

## 배경

골든존 모델에서 tension은 입력의 "어려움"이나 "모호성"을 반영한다.
만약 tension이 입력의 본질적 속성(intrinsic property)을 측정한다면,
독립적으로 학습된 두 모델이 같은 입력에 대해 유사한 tension을 보여야 한다.

이것은 물리학의 공명(resonance) 현상과 유사하다:
두 독립된 진동자가 같은 외력을 받으면 동일한 주파수로 진동한다.
마찬가지로, 두 독립 PureField 모델이 같은 입력을 받으면
유사한 tension 패턴을 보일 수 있다.

이 현상이 확인되면 tension은 모델의 학습 과정에 의존하지 않는
입력의 "고유 어려움(intrinsic difficulty)"을 측정하는 지표가 된다.
이는 의식엔진에서 tension이 주관적 경험이 아니라 객관적 측정량이라는
근거가 된다.

"텔레파시"는 비유이다. 두 모델이 정보를 교환하는 것이 아니라,
같은 입력의 같은 속성에 반응하는 것이다. 마치 두 사람이
같은 퍼즐을 보고 비슷한 난이도를 느끼는 것과 같다.

## 예측

| 측정 | 예측값 | 의미 |
|------|--------|------|
| tension 상관 (r) | > 0.9 | 강한 동기화 |
| class별 tension 순위 | Kendall tau > 0.8 | 순위도 일치 |
| tension 분산 비율 | > 80% 공유 | 대부분 입력 기인 |
| 모델 간 tension 차이 | < 0.05 (scale 조정 후) | 절대값도 유사 |

```
모델 A tension vs 모델 B tension (예측):

B tension |
  0.5     |          *  *
  0.4     |       * * *
  0.3     |     * **
  0.2     |   **
  0.1     | **
  0.0     +--+--+--+--+--+-->
          0  0.1 0.2 0.3 0.4 0.5
              A tension

          예측: r > 0.9, 거의 대각선
```

핵심 예측:
1. 같은 시드의 다른 초기화 → r > 0.95
2. 다른 시드의 다른 초기화 → r > 0.85
3. 다른 아키텍처(같은 원리) → r > 0.7
4. "어려운" 이미지(경계 근처)에서 tension이 가장 높고, 두 모델이 일치

## 검증 방법

1. PureField 모델 2개를 다른 random seed로 독립 학습
   - seed A: 42, seed B: 137
   - 동일 CIFAR-10 데이터셋, 동일 하이퍼파라미터
2. 테스트 셋 전체에 대해 두 모델의 tension 측정
3. Pearson correlation, Spearman rank correlation 계산
4. class별 평균 tension 비교 (10 classes)
5. per-sample tension scatter plot 생성

```python
# 검증 코드 스케치
model_a = PureField(seed=42)
model_b = PureField(seed=137)
# 학습 후
tensions_a = [model_a.get_tension(x) for x in test_set]
tensions_b = [model_b.get_tension(x) for x in test_set]
r, p = pearsonr(tensions_a, tensions_b)
```

## 관련 가설

- **H-CX-149**: 방향 텔레파시 (direction 수준의 동기화)
- **H-CX-150**: 무언의 합의 (class centroid 수렴)
- **H-CX-151**: 레이어 간 장력 신호 (tension의 정보 전달 역할)
- **H-CX-95**: tension-accuracy 상관

## 한계

1. r > 0.9가 나와도 "입력의 고유 어려움"이 아니라 학습 데이터의 통계적 규칙성일 수 있음
2. 같은 아키텍처와 같은 데이터로 학습하면 수렴은 자명할 수 있음
3. 진정한 검증은 다른 아키텍처(CNN vs Transformer 등)에서도 일치하는지 확인 필요
4. tension의 정의가 모델마다 다르면 직접 비교가 불가
5. "텔레파시"라는 용어가 오해를 줄 수 있음 — 실제로는 공통 입력 반응

## 검증 상태

- [ ] 2-seed 모델 학습
- [ ] tension 상관 분석
- [ ] 다른 아키텍처 간 비교
- 현재: **미검증**
