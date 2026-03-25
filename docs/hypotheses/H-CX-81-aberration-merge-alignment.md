# H-CX-81: 수차-위상 일치 — 색수차가 큰 클래스 = 빨리 merge되는 클래스

> 색수차(H-CX-60)가 큰 클래스(AUC 편차가 큰 클래스)가
> PH에서 빨리 merge되는 클래스(H-CX-66)와 일치한다.
> 수차의 원인 = 위상적 근접성.

## 배경

- H-CX-60: 색수차 = 클래스별 AUC 편차 (Fashion variance=0.035)
- H-CX-66: PH merge 순서 = 혼동 순서 (r=-0.97)
- 교차: 낮은 AUC 클래스가 빨리 merge되는 클래스?

## 예측

1. 클래스별 AUC와 해당 클래스의 min_merge_distance 양의 상관
2. 가장 빨리 merge되는 클래스 쌍의 두 클래스 = 가장 낮은 AUC 클래스
3. Spearman(min_merge_dist, class_AUC) > 0.5

## 검증 방법

```
1. H-CX-65/66 데이터 재활용
2. 각 클래스의 min_merge_distance (가장 가까운 이웃까지 거리)
3. 각 클래스의 precog AUC
4. Spearman(min_merge_dist, AUC)
```

## 관련 가설

- H-CX-60 (수차 예지), H-CX-66 (방향 위상), H-CX-65 (수차 보정)

## 한계

- H-CX-65에서 isolation vs AUC가 기각됨 — 비슷한 가설
- min_merge_dist ≈ isolation이면 동일 가설 반복

## 검증 상태

- [ ] min_merge_dist vs AUC
- [ ] H-CX-65와의 차이 분석
