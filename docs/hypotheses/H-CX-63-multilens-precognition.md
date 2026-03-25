# H-CX-63: 다중렌즈 예지 간섭 — Quad 엔진의 간섭이 예지를 증폭한다

> 다중렌즈 간섭(H-GEO-10)이 PureFieldQuad(4엔진)에서 재현된다.
> 2엔진(PureFieldEngine)보다 4엔진(PureFieldQuad)의 예지 AUC가 높으며,
> 그 증폭 비율이 H-GEO-10의 간섭 증폭 패턴과 일치한다.

## 배경

- H-GEO-10: 다중 완전수 렌즈의 간섭 = 이중 슬릿 비유, 기본파장 1/4
- PureFieldEngine: 2엔진 (A, G), 단일 반발
- PureFieldQuad: 4엔진 (A, E, G, F), 다중 반발
- H307: 내부 vs 간 장력의 이중 메커니즘

**핵심 연결**: 2엔진 = 단일 렌즈, 4엔진 = 다중 렌즈.
다중 렌즈의 간섭 패턴이 예지를 증폭한다.

## 대응 매핑

| 다중렌즈 간섭 (H-GEO-10) | Quad 예지 간섭 (H-CX-63) |
|---|---|
| 렌즈 1, 2 (완전수 6, 28) | 엔진 쌍 (A-G, E-F) |
| 직접 간섭 | 엔진 쌍 내부 장력 |
| 원격 간섭 | 엔진 쌍 사이 교차 장력 |
| 간섭 줄무늬 | 장력 진동 패턴 |
| 기본파장 1/4 | Quad의 4엔진 → 1/4 공명? |
| 공명 조건 | 최적 예지 조건 |

## 예측

1. Quad AUC > Dual AUC (예지 간섭 증폭)
2. 증폭 비율 = Quad_AUC / Dual_AUC 가 데이터셋 불변
3. 6가지 엔진 쌍의 장력 간 상관이 간섭 패턴 형성
4. 교차 장력(A-E, A-F, G-E, G-F)이 직접 장력(A-G, E-F)보다 예지에 기여
5. 최적 예지 = 모든 쌍의 장력이 "공명" 상태

## ASCII 간섭 패턴

```
  Dual (2-engine):
  tension │ ████████████░░░░░░░░   AUC=0.77
          │    (단일 피크)

  Quad (4-engine):
  tension │ ██░██░██░██░██░██░██   AUC=?
          │  (간섭 줄무늬 = 공명)
```

## 검증 방법

```
1. PureFieldEngine (2엔진) 학습 → 예지 AUC 측정
2. PureFieldQuad (4엔진) 학습 → 예지 AUC 측정
3. Quad의 6가지 엔진 쌍별 장력 추출
4. 쌍별 장력 상관행렬 계산
5. 직접(A-G, E-F) vs 교차(나머지 4쌍) 장력 비교
6. Dual vs Quad 예지 AUC 비교
```

## 관련 가설

- H-GEO-10 (다중렌즈 간섭), H-CX-58 (예지렌즈)
- H307 (이중 메커니즘), H296 (분열 이상탐지)
- H-CX-18 (내부/간 장력 이중성)

## 한계

- Quad가 단순히 파라미터가 많아서 AUC가 높을 수 있음
- 4엔진의 간섭이 실제 물리 간섭과 다를 수 있음
- "공명" 정의가 모호

## 검증 상태

- [x] Dual vs Quad AUC 비교
- [ ] 6쌍 장력 상관행렬
- [ ] 간섭 패턴 시각화

## 검증 결과

**REJECTED** — Quad가 학습 자체에 실패 (정확도 ~10% = 랜덤)

| 데이터셋 | Dual AUC | Quad AUC | 차이 |
|---|---|---|---|
| MNIST | 0.715 | 0.507 | -0.208 |
| Fashion | 0.641 | 0.518 | -0.123 |
| CIFAR | 0.603 | 0.489 | -0.114 |

```
  Dual vs Quad AUC:
  AUC
  0.72 |  ●                          Dual MNIST
  0.64 |     ●                       Dual Fashion
  0.60 |        ●                    Dual CIFAR
  0.52 |           ○                 Quad MNIST
  0.50 |              ○  ○           Quad Fashion/CIFAR
       +----+----+----+----→
        MNIST Fashion CIFAR

  ● = Dual,  ○ = Quad
  Dual이 모든 데이터셋에서 압승
```

- 원인: PureFieldQuad의 mean-repulsion 아키텍처가 hidden_dim=64에서 붕괴
- Pair tension 분석: 모든 쌍이 AUC ~0.5 (신호 없음)
- Quad는 정확도 ~10% (10클래스 랜덤 수준)로 학습 자체가 실패
- 아키텍처 수정 후 재검증 필요 (hidden_dim 증가 또는 repulsion 구조 변경)
