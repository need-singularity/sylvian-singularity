# H-CX-62: 위상 예지 — 장력 바코드가 학습 궤적을 예측한다

> 위상렌즈(H-TOP-7)의 Persistent Homology 바코드를
> 장력 분포에 적용하면, 학습 궤적(미래 정확도 변화)을 예측할 수 있다.
> birth-death 쌍 = 장력 클러스터의 생성-소멸 = 개념 형성-소멸.

## 배경

- H-TOP-7: R 스펙트럼 간극 → PH 바코드의 위상 렌즈, 초점거리 = delta+ x delta-
- H-GEO-7: 위상 망원경, 필트레이션 epsilon = 줌 레벨
- H339/H341: direction = concept, tension = confidence

**핵심 연결**: 각 에폭의 장력 분포를 점 구름(point cloud)으로 보고
PH를 계산하면, 바코드의 긴 막대(persistent feature) = 안정적 개념,
짧은 막대(noisy feature) = 불안정 개념. 긴 막대가 많을수록 미래 정확도 높음.

## 대응 매핑

| 위상렌즈 (H-TOP-7) | 장력 위상 (H-CX-62) |
|---|---|
| Vietoris-Rips filtration | 장력 공간의 epsilon-ball |
| birth = 연결 생성 | 장력 클러스터 형성 |
| death = 연결 소멸 | 장력 클러스터 병합/소멸 |
| persistence = death - birth | 개념 안정성 |
| beta_0 (연결성분 수) | 장력 클러스터 수 |
| 긴 바코드 | 안정적 클래스 분리 |
| 짧은 바코드 | 불안정/혼동 클래스 |

## 예측

1. 에폭 N의 mean_persistence와 에폭 N+K의 accuracy 상관 r > 0.7
2. 클래스 i의 persistence와 해당 클래스 accuracy 상관
3. 학습 초기 바코드 패턴으로 최종 수렴 정확도 예측 가능
4. 짧은 바코드의 클래스 = 혼동 쌍 (H-CX-59와 교차 검증)

## ASCII 바코드 예측

```
  Epoch 5 바코드:
  class 0 ████████████████████ (long = stable → high acc)
  class 1 ███████████████      (medium)
  class 3 ██████               (short = unstable → confusion with 8)
  class 8 ████████             (short)

  → 예측: epoch 15에서 class 0 > class 1 > class 8 > class 3 정확도
```

## 검증 방법 (근사적)

PH 라이브러리 없이도 근사 가능:
```
1. 에폭별 (direction, tension) 쌍 수집
2. 클래스별 direction 코사인 유사도 행렬 계산
3. 유사도 > threshold 인 쌍의 수 = 근사 beta_0
4. threshold를 sweep하면 beta_0(epsilon) 곡선 = 근사 PH
5. 이 곡선의 안정성이 미래 정확도와 상관하는지 확인
```

## 관련 가설

- H-TOP-7 (위상렌즈), H-GEO-7 (위상망원경)
- H-CX-59 (방향예지), H325 (Fisher 정보 장력)
- H281 (장력 시간 인과)

## 한계

- 근사 PH는 실제 PH와 다를 수 있음
- 10D 방향 공간의 거리 메트릭 선택이 결과에 영향
- 소규모(10 클래스)에서 바코드가 의미있을지 불확실

## 검증 상태

- [x] 근사 PH 계산 (버그 발견)
- [ ] persistence vs accuracy 상관
- [ ] 예측 정확도 측정

## 검증 결과

**INCONCLUSIVE** — 근사 PH 구현에 버그 존재 (persistence_from_beta0가 모든 경우 0 반환)

Beta_0 곡선 자체는 의미있는 구조를 보임:

| 데이터셋 | beta_0 (th=0.63) 변화 | 해석 |
|---|---|---|
| MNIST | 8 → 5 (에폭 진행) | 클래스 분리 개선 (연결성분 감소) |
| Fashion | ~3 안정 | 위상 구조 초기에 고정 |

```
  MNIST beta_0 at threshold=0.63:
  beta_0
  8 |  ●
  7 |     ●
  6 |        ●  ●
  5 |              ●  ●  ●  ●  ●
    +--+--+--+--+--+--+--+--+--→ Epoch
     1  2  3  4  5  6  7  8  9

  Fashion beta_0 at threshold=0.63:
  beta_0
  4 |
  3 |  ●  ●  ●  ●  ●  ●  ●  ●  ●
  2 |
    +--+--+--+--+--+--+--+--+--→ Epoch
     1  2  3  4  5  6  7  8  9
```

- persistence_from_beta0 함수가 항상 0을 반환하는 버그로 정량적 검증 불가
- 정성적으로 beta_0 감소는 클래스 분리 개선과 일치
- 적절한 PH 라이브러리 (Ripser/GUDHI) 사용 시 재검증 필요
