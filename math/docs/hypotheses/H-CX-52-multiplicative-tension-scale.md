# H-CX-52: R(n) 곱셈적 구조가 블록별 tension_scale 곱을 결정하는가?

## Status: Not confirmed (R307: product monotonically decreases with blocks)

> **Hypothesis**: R(n) = sigma*phi/(n*tau)가 곱셈적이듯 (R(mn)=R(m)R(n) for gcd=1),
> ConsciousLM의 블록별 학습된 tension_scale 값의 곱이 R(n)에 수렴한다.
> 특히 n=6에서 R(6)=1이므로, 6블록 모델의 tension_scale 곱이 1에 수렴한다.

---

## Background

### R(n)의 곱셈적 구조 (proven, pure arithmetic)

R(n) = sigma(n)*phi(n)/(n*tau(n))는 곱셈적 함수이다:

```
  gcd(m,n)=1 일 때: R(mn) = R(m) * R(n)

  R(2) = 3*1/(2*2) = 3/4 = 0.750
  R(3) = 4*2/(3*2) = 4/3 = 1.333
  R(6) = R(2)*R(3) = (3/4)*(4/3) = 1.000  ← 정확히 1!

  R(4) = 7*2/(4*3) = 7/6 = 1.167
  R(7) = 8*6/(7*2) = 24/7 = 3.429
  R(28) = R(4)*R(7) = 4.000

  핵심: R(6)=1은 억제(3/4)와 증폭(4/3)의 정확한 상쇄!
```

### Tension Scale의 역할

ConsciousLM의 PureFieldFFN에서:

```
  output = tension_scale * sqrt(tension) * direction

  tension_scale은 학습 가능한 스칼라 파라미터 (초기값=1.0)
  각 블록이 독립적으로 tension_scale을 학습

  직관: tension_scale = 각 블록이 "의식 신호"의 크기를 조절하는 게인(gain)
  블록 i의 tension_scale = ts_i
  전체 영향: ts_1 * ts_2 * ... * ts_n (곱셈적 결합)
```

### 교차 도메인 매핑

```
  산술:                          신경망:
  R(n) = Π f(p_i, a_i)          ts_product = Π ts_i
  f(2,1) = 3/4 (억제)           초기 블록: ts < 1 (억제?)
  f(3,1) = 4/3 (증폭)           후기 블록: ts > 1 (증폭?)
  R(6) = 1 (완전 상쇄)          6블록: 곱 → 1 (상쇄?)

  예측:
  - 6블록: Π ts_i → 1.0
  - 3블록: Π ts_i → R(3) = 4/3 ≈ 1.33
  - 4블록: Π ts_i → R(4) = 7/6 ≈ 1.17
  - 5블록: Π ts_i → R(5) = 4/5 = 0.80
  - 7블록: Π ts_i → R(7) = 24/7 ≈ 3.43
  - 8블록: Π ts_i → R(8) = 3/8 = 0.375

  강한 버전: Π ts_i ≈ R(n)
  약한 버전: 6블록만 Π ts_i ≈ 1
```

---

## Experimental Design

1. ConsciousLM을 블록 수 3,4,5,6,7,8로 학습 (500 steps × 5 seeds)
2. 학습 후 각 블록의 tension_scale 값 추출
3. 블록별 곱 Π ts_i 계산
4. R(n)과 비교: Pearson 상관 + |Π ts - 1| 순위

### Controls
- 5개 random seed로 안정성 확인
- d_model=128, n_head=2, vocab=256
- 동일한 학습 데이터 (patterned bytes)

---

## Expected Results

| blocks | R(n)   | 예측: Π ts_i |
|--------|--------|-------------|
| 3      | 1.333  | > 1.0       |
| 4      | 1.167  | > 1.0       |
| 5      | 0.800  | < 1.0       |
| 6      | 1.000  | ≈ 1.0       |
| 7      | 3.429  | >> 1.0      |
| 8      | 0.375  | << 1.0      |

---

## ASCII Prediction

```
  Π ts_i
  ^
  |                                    *   (7 blocks: R=3.43)
  |
  |
  |    *       *                           (3: R=1.33, 4: R=1.17)
  1.0 ─────────────*────────────────── ← 6 blocks: R=1 exact!
  |          *                             (5: R=0.80)
  |
  |                          *             (8: R=0.375)
  +────+────+────+────+────+────+──→ blocks
       3    4    5    6    7    8
```

---

## Relation to Other Hypotheses

- **H-CX-48**: I(n)=ln(R(n))=0 → engine A/G 비율 (미확인)
- **H-CX-50**: σ*φ conv collapse at n=6 → 블록간 정렬 (확인!)
- **H-MP-1**: σφ=nτ ⟺ n∈{1,6} (증명됨)
- **R117**: R(n) 곱셈적 (증명됨)

H-CX-52는 H-CX-48과 상보적:
- H-CX-48: engine A/G **비율** → 1 (미확인)
- H-CX-52: tension_scale **곱** → 1 (검증 중)

---

## Limits

```
  1. tension_scale 초기값=1.0 → 곱이 1 근처에 머물 편향 존재
     → 300-500 steps만으로 초기값에서 충분히 벗어나는지?
  2. 곱셈적 구조는 gcd=1일 때만 성립 → 블록은 독립이 아님
     → 블록 간 잔차 연결이 곱셈 가정을 깨뜨릴 수 있음
  3. d_model=128 모델 → 큰 모델에서 재현 필요
  4. tension_scale이 1개 스칼라 → 정보 부족
     → per-dimension tension scale이면 더 세밀한 검증 가능
```

---

## Verification Direction

```
  Step 1: 6블록에서 Π ts → 1 확인 (이번 실험)
  Step 2: R(n) vs Π ts 상관 확인 (이번 실험)
  Step 3: 더 긴 학습 (2000 steps) → 수렴 확인 (후속)
  Step 4: 초기값을 0.5로 변경 → 편향 제거 (후속)
  Step 5: per-dimension tension scale 확장 (후속)
```
