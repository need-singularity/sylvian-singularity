# H-CX-95: PH로 일반화 갭 예측 — train PH vs test PH 차이 = 과적합

> Train set의 PH와 test set의 PH 차이가 일반화 갭(train_acc - test_acc)을 예측.
> PH 차이가 크면 과적합, 작으면 좋은 일반화.

## 예측

1. |H0_train - H0_test|와 generalization gap 양의 상관
2. merge 순서의 train-test tau가 높을수록 좋은 일반화
3. 에폭별 PH gap 추적 → 과적합 조기 감지

## 검증 상태

- [ ] train/test PH 비교
- [ ] gap 상관
