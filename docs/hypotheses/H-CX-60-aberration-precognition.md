# H-CX-60: 수차 예지 — 예지 실패 유형이 자이델 수차에 매핑된다

> 예지의 클래스별 AUC 편차는 렌즈 수차(H-GEO-9)와 구조적으로 동형이다.
> 5대 자이델 수차 = 5가지 예지 실패 모드.

## 배경

- H-GEO-9: R 스펙트럼의 5대 자이델 수차 (색/구면/비점/코마/왜곡)
- 예지: AUC=0.925이지만 클래스별로 편차 존재
- H339/H341: 방향+크기 분해

**핵심 연결**: 예지가 완벽하지 않은 이유 = 렌즈 수차.
각 수차 유형이 특정 예지 실패 패턴에 대응.

## 수차-예지 매핑

| 자이델 수차 | R 스펙트럼 (H-GEO-9) | 예지 실패 모드 |
|---|---|---|
| 색수차 (Chromatic) | f(p,1) 소수별 차이 | 클래스별 AUC 편차 |
| 구면수차 (Spherical) | R=1 주변 밀도 프로필 | 중간 장력 구간 불확실성 |
| 비점수차 (Astigmatic) | R-S 비대칭 | 방향 vs 크기 비대칭 |
| 코마 (Coma) | 비대칭 간극 delta-/delta+ | 과확신 vs 과소확신 비대칭 |
| 왜곡 (Distortion) | R-chain 분포 | 에폭별 예지 정확도 왜곡 |

## 예측

1. 클래스별 AUC 편차의 패턴이 "색수차" 구조 (유사 클래스끼리 AUC 낮음)
2. 중간 장력 구간의 예지 실패율이 "구면수차" 패턴 (U자형)
3. 방향 안정성 vs 크기 안정성의 비대칭 = "비점수차"
4. 과확신 오답(high tension + wrong) vs 과소확신 정답(low tension + correct) 비대칭 = "코마"
5. 학습 초기 vs 후기의 예지 패턴 변화 = "왜곡"

## ASCII 수차 스펙트럼

```
  AUC
  1.0 |  0   1       2           6   7
  0.9 |          3       5
  0.8 |              4       8
  0.7 |                          9
      +--+--+--+--+--+--+--+--+--+--→ Class
       0  1  2  3  4  5  6  7  8  9

  색수차: 유사 클래스(3/8, 4/9) 수렴
  비점수차: 방향 안정성 ≠ 크기 안정성
```

## 검증 방법

```
1. PureFieldEngine 학습 (3 datasets)
2. 클래스별 예지 AUC 계산 (색수차)
3. 장력 5-quantile별 예지 정확도 (구면수차)
4. 방향 std vs 크기 std 비교 (비점수차)
5. 과확신/과소확신 비율 비교 (코마)
6. 에폭별 예지 AUC 추이 (왜곡)
```

## 관련 가설

- H-GEO-9 (렌즈수차 분류), H-CX-58 (예지렌즈)
- H316 (유사 클래스 과확신), H339 (방향=개념)

## 한계

- 5대 수차 매핑이 강제적일 수 있음 (over-fitting to metaphor)
- 수차 보정 방법이 불명확

## 검증 상태

- [x] 5가지 수차 측정
- [ ] 수차 간 상관관계
- [ ] 보정 가능성 탐색

## 검증 결과

**PARTIAL (3/5 수차 확인)**

| 수차 유형 | 결과 | 세부 |
|---|---|---|
| 색수차 (Chromatic) | SUPPORTED | Fashion Trouser AUC=0.971 vs Sneaker=0.267 — 극단적 클래스별 편차 |
| 구면수차 (Spherical) | REJECTED | 단조 증가 패턴, U자형 아님 |
| 비점수차 (Astigmatic) | SUPPORTED | dir_std << mag_std 일관 (비율 0.01-0.09) |
| 코마 (Coma) | SUPPORTED (MNIST/Fashion) | 극단적 비대칭 — MNIST over/under=0.010 |
| 왜곡 (Distortion) | SUPPORTED | 모든 데이터셋에서 HIGH (14 에폭 중 5-9회 반전) |

```
  수차 스코어카드:
  Chromatic   ████████████████████  SUPPORTED
  Spherical   ░░░░░░░░░░░░░░░░░░░░  REJECTED (monotonic, not U-shape)
  Astigmatic  ████████████████████  SUPPORTED
  Coma        ██████████████░░░░░░  SUPPORTED (MNIST/Fashion)
  Distortion  ████████████████████  SUPPORTED

  3/5 confirmed → PARTIAL support
```

- 구면수차만 기각: 중간 장력 구간 불확실성이 U자형이 아닌 단조 증가
- 비점수차가 가장 명확: 방향 안정성이 크기 안정성보다 1-2 자릿수 낮음
- 코마 비대칭 극단적: 과확신 오답이 과소확신 정답보다 압도적으로 적음
