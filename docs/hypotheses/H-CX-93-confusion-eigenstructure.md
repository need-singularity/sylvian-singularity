# H-CX-93: 혼동 고유구조 — confusion matrix의 고유벡터가 의미 축을 인코딩

> Confusion matrix의 PCA 고유벡터가 의미적 축(동물 vs 기계 등)을 인코딩.
> 제1 고유벡터 = 가장 큰 의미적 분할.

## 배경

- H-CX-85: dendrogram이 의미 계층
- H-CX-88: 아키텍처 불변
- Confusion matrix 자체에 구조가 있을 것

## 예측

1. Confusion matrix의 PC1이 CIFAR 동물/기계 분할과 일치
2. PC2가 CIFAR 내 세부 분류 (새류 vs 포유류 등)
3. Fashion PC1 = 상의/하의/신발 분할

## 검증 상태

- [ ] Confusion PCA
- [ ] 의미적 축 일치
