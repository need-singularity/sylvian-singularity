# H-CX-97: 교차 데이터셋 계층 전이 — MNIST의 형태 계층이 Fashion에 전이

> MNIST에서 학습한 PH 계층(둥근 숫자 vs 직선 숫자)이
> Fashion에서도 유사한 형태 기반 계층(둥근 옷 vs 직선 옷)으로 전이.
> 의미는 다르지만 형태 기하학이 보존.

## 예측

1. MNIST 학습 모델로 Fashion 입력 시 PH 구조가 의미적 (상의/신발 분리 아님)
2. 대신 형태 기반 클러스터링 발생 (둥근 형태끼리 모임)
3. confusion PCA의 설명 분산 비율이 MNIST→Fashion 전이 시 감소

## 검증 상태

- [ ] cross-dataset PH
- [ ] 형태 vs 의미 분석
