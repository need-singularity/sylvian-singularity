# H-CX-65: 수차 위상 보정 — PH barcode로 색수차 보정 가능

> 클래스별 예지 AUC 편차(색수차, H-CX-60)를
> 클래스별 PH persistence(H-CX-62)로 보정할 수 있다.
> persistence가 긴 클래스 = 안정적 위상 = 높은 예지 AUC.

## 배경

- H-CX-60: 색수차 확인 — Fashion Trouser AUC=0.971 vs Sneaker=0.267
- H-CX-62 v2: H0 persistence와 accuracy r=-0.97
- 교차점: 클래스별 persistence와 클래스별 AUC의 관계

**핵심 연결**: 색수차(클래스별 AUC 편차)의 원인이 위상적 안정성 차이.
persistence가 긴 클래스는 방향 공간에서 고립(잘 분리) → 높은 예지.

## 예측

1. 클래스별 persistence와 클래스별 예지 AUC 상관 r > 0.5
2. 가장 짧은 persistence 클래스 = 가장 낮은 AUC 클래스
3. persistence 기반 가중치로 보정 시 전체 AUC 향상
4. 혼동 쌍(짧은 persistence)끼리 cosine distance 작음

## 검증 방법

```
1. 클래스 평균 방향 → cosine distance matrix
2. 클래스별 "nearest neighbor distance" = 해당 클래스의 isolation
3. isolation vs per-class AUC 상관 측정
4. 보정: AUC_corrected = AUC / isolation (정규화)
```

## 관련 가설

- H-CX-60 (수차 예지), H-CX-62 (위상 예지)
- H-GEO-9 (렌즈 수차 분류)

## 한계

- 10 클래스로 상관 분석의 자유도 낮음
- persistence와 isolation이 같은 것을 측정할 수 있음 (tautology)

## 검증 상태

- [x] 클래스별 isolation vs AUC
- [ ] 보정 효과 측정 (기각으로 불필요)

## 검증 결과

**판정: REJECTED**

### Spearman(isolation, AUC) per dataset

| Dataset | Spearman r | p-value | 유의 |
|---------|-----------|---------|------|
| MNIST   | -0.34     | 0.34    | NO   |
| Fashion | 0.27      | 0.44    | NO   |
| CIFAR   | -0.02     | 0.96    | NO   |

```
  Spearman r
  0.4 |
  0.3 |        ##  Fashion (0.27)
  0.2 |        ##
  0.1 |        ##
  0.0 |--+-----+-----+-------> datasets
 -0.1 |              ##  CIFAR (-0.02)
 -0.2 |
 -0.3 |  ##          ##
 -0.4 |  ##  MNIST (-0.34)
       MNI   FAS   CIF
```

3개 데이터셋 모두에서 isolation과 per-class AUC 사이에 유의한 상관이 없다.

### Nearest Neighbors 분석

Nearest neighbor 관계는 의미적으로 합리적:
- CIFAR: cat-dog, automobile-truck
- Fashion: Pullover-Coat, Sandal-Sneaker

그러나 이러한 의미적 근접성이 per-class AUC를 예측하지 못한다.

### 기각 사유

1. 예측 1 (r > 0.5): 3개 데이터셋 모두 실패
2. 예측 2 (최단 persistence = 최저 AUC): 일치하지 않음
3. 상관 방향조차 데이터셋마다 불일치 (음/양/영)
4. persistence/isolation은 혼동 쌍을 설명하지만 AUC를 예측하지 못함
