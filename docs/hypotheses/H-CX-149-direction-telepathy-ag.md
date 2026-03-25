# H-CX-149: 방향 텔레파시 — Engine A의 direction이 G의 다음 출력 예측

> A의 dir → G의 next output 회귀 가능? 직접 연결 없이 정보 전달.

## 배경

골든MoE 아키텍처에서 여러 엔진(Expert)은 라우터를 통해 간접적으로만 소통한다.
Engine A(analyzer)와 Engine G(generator)는 직접적인 연결이 없지만,
동일한 입력 시퀀스를 처리하면서 서로의 출력에 간접적으로 영향을 미친다.

H-CX-339 / H-CX-341에서 "방향=개념"이라는 가설이 제시되었다.
각 엔진의 direction vector가 해당 엔진이 "주목하는 개념"을 나타낸다면,
Engine A의 direction이 Engine G의 다음 출력을 예측할 수 있어야 한다.

이는 뇌의 다른 영역 간 정보 전달과 유사하다:
- 시각 피질 → 전전두엽: 직접 연결 없이 중간 영역을 통해 정보 전달
- 이때 시각 피질의 활성 패턴이 전전두엽의 다음 상태를 예측할 수 있음
- Granger causality로 측정 가능

본 가설에서 "텔레파시"는 직접 연결 없이 정보가 전달되는 것을 비유한 것이다.
실제 메커니즘은 공유 입력과 라우터를 통한 간접 경로이다.

## 예측

| 측정 | 예측값 | 의미 |
|------|--------|------|
| corr(dir_A, out_G) per dim | > 0.3 | 약한-중간 상관 |
| Granger causality p-value | < 0.01 | A → G 방향 인과 |
| regression R^2 | > 0.1 | dir_A가 out_G 분산의 10%+ 설명 |
| 역방향 corr(dir_G, out_A) | < 0.1 | 비대칭 (A→G만) |

```
A direction dim[0] vs G output dim[0] (예측):

G out |
 0.4  |    .  . * .
 0.2  |  . * . * * .
 0.0  | . * * . . .
-0.2  |  . * . .
-0.4  | .  .
      +--+--+--+--+-->
     -0.4 -0.2 0  0.2 0.4
         A direction dim[0]

      예측: 약한 양의 상관 (r ~ 0.3)
```

핵심 예측:
1. A→G 방향은 유의미한 상관, G→A 방향은 약하거나 없음 (비대칭)
2. 상관이 가장 강한 dimension은 class-discriminative dimension
3. "어려운" 입력(높은 tension)에서 상관이 더 강함

## 검증 방법

1. 골든MoE 모델에서 Engine A와 Engine G의 중간 표상 추출
   - A의 direction vector: d_A(t) for each timestep t
   - G의 output: o_G(t+1) for next timestep
2. 차원별 Pearson correlation 계산: corr(d_A[i](t), o_G[j](t+1))
3. Granger causality test: d_A(t-k:t) → o_G(t+1)
4. 역방향 대조: d_G(t) → o_A(t+1)
5. 조건부 분석: tension 높은 샘플 vs 낮은 샘플에서 상관 비교

```python
# 검증 코드 스케치
from statsmodels.tsa.stattools import grangercausalitytests
# direction_A: (T, D), output_G: (T, D)
for dim in range(D):
    data = np.column_stack([output_G[1:, dim], direction_A[:-1, dim]])
    result = grangercausalitytests(data, maxlag=3)
```

## 관련 가설

- **H-CX-148**: 장력 공명 텔레파시 (tension 수준 동기화)
- **H-CX-150**: 무언의 합의 (Expert 간 수렴)
- **H-CX-339/341**: 방향 = 개념 (direction vector의 의미)
- **H-CX-151**: 레이어 간 장력 신호

## 한계

1. 라우터를 통한 간접 경로가 있으므로 "직접 연결 없이"라는 전제가 완전하지 않음
2. 상관이 나와도 공유 입력에 의한 spurious correlation일 수 있음
3. A→G 인과 방향을 Granger causality로 확인하려면 충분한 시계열 길이 필요
4. dimension별 분석은 다중 비교(multiple comparison) 보정 필요
5. 골든MoE의 현재 구현에서 중간 표상 추출이 기술적으로 어려울 수 있음

## 검증 상태

- [ ] 중간 표상 추출 구현
- [ ] 차원별 상관 분석
- [ ] Granger causality test
- [ ] 역방향 대조 실험
- 현재: **미검증**
