# H-CX-106: 인간 혼동 = AI 혼동 — 같은 현실, 같은 PH

> 인간의 CIFAR-10 분류 혼동 행렬과 AI의 PH merge 순서가 일치한다.
> Peterson et al. (2019) "Human Uncertainty Makes Classification More Robust"
> 에서 공개한 인간 혼동 데이터와 AI PH를 직접 비교.

## 예측

1. 인간 혼동 빈도 vs AI merge distance: Spearman |r| > 0.7
2. 인간 top-5 혼동 쌍 = AI top-5 merge 쌍 overlap > 3/5
3. 인간 혼동 PCA PC1 = AI confusion PCA PC1 (동물/기계 분리)

## 검증 상태

- [ ] 인간 혼동 데이터 수집
- [ ] Spearman 상관
- [ ] PCA 비교
