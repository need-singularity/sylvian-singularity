# H-CX-92: dendrogram 깊이 = 학습 난이도

> PH dendrogram에서 늦게 merge되는(깊은) 클래스 = 높은 정확도.
> 빨리 merge되는(얕은) 클래스 = 낮은 정확도.
> merge 깊이가 per-class accuracy를 예측.

## 배경

- H-CX-85: dendrogram = 의미 계층 (89% purity)
- H-CX-66: 빨리 merge = 혼동 큼

## 예측

1. 클래스별 "first merge distance"와 class accuracy 양의 상관 r > 0.5
2. 가장 늦게 merge되는 클래스 = 가장 높은 accuracy
3. dendrogram 클러스터 크기와 클러스터 내 평균 accuracy 음의 상관

## 검증 상태

- [ ] first_merge_dist vs class_accuracy
