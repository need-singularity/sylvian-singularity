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

- [ ] 클래스별 isolation vs AUC
- [ ] 보정 효과 측정
