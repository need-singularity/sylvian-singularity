# H-CX-94: 혼동 행렬 자체가 거리 행렬 — meta-PH로 2차 위상 구조 추출

> Confusion matrix를 거리 행렬로 해석하고 PH를 계산하면
> "혼동의 혼동" = 2차 위상 구조가 나타난다.
> 이 meta-PH가 데이터셋 난이도와 학습 가능성을 예측.

## 예측

1. confusion→distance 변환 (d=max-conf) 후 PH 계산 가능
2. meta-H0_total이 데이터셋 난이도와 상관 (CIFAR > Fashion > MNIST)
3. meta-dendrogram이 H-CX-85 dendrogram과 일치 (자기 일관성)

## 검증 상태

- [ ] meta-PH 계산
- [ ] 난이도 상관
