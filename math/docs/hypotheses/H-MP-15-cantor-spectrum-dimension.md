# H-MP-15: R 스펙트럼의 Hausdorff 차원

> **가설**: R(n) 치역의 [0,M] 절단이 M 증가에 따라 Hausdorff 차원 d(M)→1로 수렴하며, 수렴 속도가 σ,τ로 표현된다.

## 데이터
- R<5: 24값/5단위 = 4.8/unit, gap 99.1%
- R<10: 63값, density 6.3/unit
- R<100: 917값, density 9.2/unit
- 밀도 증가 but still sparse

## 검증: d(M) = log(N(M))/log(M)?
- N(5)=24: d≈log24/log5=1.97 (>1이지만 의미 다름)
- 실제 Hausdorff dim 계산 필요

## 난이도: 극고 | 파급력: ★★★
