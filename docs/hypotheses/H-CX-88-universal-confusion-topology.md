# H-CX-88: 보편 혼동 위상 — PH merge 순서가 아키텍처 불변이다

> PureFieldEngine, Dense MLP, 또는 다른 아키텍처에서도
> 동일한 PH merge 순서가 나타난다. 혼동 위상은 데이터 고유 속성.

## 배경

- H-CX-82: 에폭 1에서 완벽 예측 → 학습 의존도 낮음
- H-CX-85: dendrogram이 의미적 → 데이터 분포 반영
- 의문: PureFieldEngine 특화인가, 보편적인가?

## 예측

1. Dense MLP의 confusion matrix에서 동일한 top-5 혼동 쌍
2. PureField vs Dense의 혼동 쌍 overlap > 80%
3. merge 순서의 Kendall tau > 0.7 (아키텍처 간)

## 검증 상태

- [ ] Dense MLP 혼동 행렬
- [ ] 아키텍처 간 overlap
