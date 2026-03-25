# H-CX-76: PH 예지 분류기 — merge distance로 혼동 쌍 예측

> PH merge distance를 feature로 사용하면 혼동 쌍 예측 정확도 > 90%.
> H-CX-66의 실용화: 학습 중간에 PH를 계산하면 최종 혼동 쌍을 조기 예측 가능.

## 배경

- H-CX-66: merge_dist vs confusion Spearman r=-0.97 (p<0.001)
- 그러나 상관 ≠ 예측. 실제 분류기(threshold 기반)의 정확도를 측정해야 함.

## 예측

1. merge distance < median인 쌍 = 혼동 쌍 (precision > 80%)
2. 에폭 5에서 계산한 merge distance로 에폭 15 혼동 쌍 예측 가능
3. merge distance rank와 confusion rank의 Kendall tau > 0.8

## 검증 방법

```
1. 에폭 5, 10, 15에서 PH merge distance 계산
2. 에폭 15의 실제 confusion matrix 추출
3. 각 에폭의 merge distance로 "top-K 혼동 쌍" 예측
4. Precision@K, Recall@K 계산
5. 에폭 5 예측 → 에폭 15 실제 비교 (조기 예측)
```

## 관련 가설

- H-CX-66 (방향 위상 혼동)
- H-CX-62 (위상 예지)

## 한계

- 45개 쌍(10C2) 중 실제 혼동 쌍은 소수 → 불균형 분류
- merge distance의 절대값이 데이터셋마다 다름

## 검증 상태

- [ ] Precision@K 측정
- [ ] 조기 예측 정확도
