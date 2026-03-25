# H-CX-107: 차원간 PH 불변 — hidden_dim이 달라도 같은 PH

> PureFieldEngine의 hidden_dim을 64/128/256으로 변경해도
> PH merge 순서가 동일하다. 차원 = 해상도, PH = 구조.

## 예측

1. 3개 dim의 merge 순서 Kendall tau > 0.8
2. top-5 merge 쌍 100% 동일
3. H0_total은 dim에 비례하지만 merge 순서는 불변

## 검증 상태

- [ ] 3개 dim PH 비교
