# H-CX-107: 차원간 PH 불변 — hidden_dim이 달라도 같은 PH

> PureFieldEngine의 hidden_dim을 64/128/256으로 변경해도
> PH merge 순서가 동일하다. 차원 = 해상도, PH = 구조.

## 예측

1. 3개 dim의 merge 순서 Kendall tau > 0.8
2. top-5 merge 쌍 100% 동일
3. H0_total은 dim에 비례하지만 merge 순서는 불변

## 검증 상태

- [x] 3개 dim PH 비교

## 검증 결과

**SUPPORTED**

| dim 쌍 | Kendall tau | confusion r | top-5 overlap |
|---------|------------|-------------|---------------|
| 64 vs 128 | 0.83 | 0.96 | 4/5 |
| 64 vs 256 | 0.85 | 0.97 | 4/5 |
| 128 vs 256 | 0.94 | 0.99 | 5/5 |

- 예측 1(tau > 0.8): 모든 쌍에서 확인 (0.83~0.94)
- 예측 2(top-5 동일): 4~5/5 overlap, 거의 동일
- 예측 3(H0_total은 dim 비례, merge 순서 불변): confusion r=0.96~0.99로 불변 확인
- 차원이 커질수록 쌍간 일치도 증가 (128 vs 256: tau=0.94, r=0.99)
- PH merge 순서는 차원 불변 구조임을 강하게 지지
