# H-CX-91: k-NN 혼동 예측 — 신경망 없이 원본 데이터만으로 혼동 구조 재현

> k-NN 분류기의 confusion matrix가 신경망(PureField, Dense)과
> 동일한 혼동 구조를 가진다. 혼동 = 순수 데이터 기하학.

## 배경

- H-CX-88: PF vs Dense 혼동 r=0.96 (아키텍처 불변)
- H-CX-89: MNIST raw→confusion r=-0.90
- 극한 검증: 학습 없는 k-NN에서도?

## 예측

1. k-NN confusion vs PureField confusion Spearman r > 0.8
2. k-NN top-5 혼동 쌍 = PureField top-5 overlap > 3/5
3. k=1,3,5,10 모두에서 일관

## 검증 상태

- [ ] k-NN confusion matrix
- [ ] 아키텍처 간 비교
