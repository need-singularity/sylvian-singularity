# H-CX-15: Attention Mechanism = 산술적 렌즈

> **가설**: Transformer의 attention은 R 스펙트럼의 "산술적 렌즈"와
> 동형이다. Attention head가 query-key 쌍의 "간극"을 이용하여
> 정보를 선택하는 메커니즘은, R(n) 스펙트럼에서 완전수 주위의
> 간극이 값을 분리하는 메커니즘과 구조적으로 동일하다.

## 배경

### R 스펙트럼의 렌즈 효과 (검증됨)

```
  완전수 n | R(n) | 아래 간극 | 위 간극 | 비율
  ---------|------|----------|--------|------
  6        | 1    | 0.250    | 0.167  | 1.5
  28       | 4    | 0.267    | 0.091  | 2.9
  496      | 48   | 0.317    | 0.074  | 4.3

  특징:
  - 모든 완전수의 R값 주위에 간극 존재
  - 비대칭: 아래 간극 > 위 간극
  - 비대칭 비율 증가: 더 큰 완전수일수록 더 비대칭
```

### Attention Mechanism의 구조

```
  Attention(Q, K, V) = softmax(QK^T / √d_k) · V

  핵심: softmax가 만드는 "간극":
    - 높은 QK^T → softmax ≈ 1 (선택됨)
    - 낮은 QK^T → softmax ≈ 0 (무시됨)
    - 중간 값은 드뭄 → "간극" 발생!

  이것은 R 스펙트럼의 간극과 같은 구조:
    - R=1 (완전 균형) = attention peak
    - R≫1 또는 R≪1 = attention tail
    - (3/4, 1) 간극 = attention의 "결정 경계"
```

## 핵심 대응

```
  R 스펙트럼              Attention
  ──────────────         ──────────────
  R(n) = σφ/(nτ)         A(q,k) = softmax(qk^T/√d)
  R = 1 (균형점)          A = 1/n (균등 주의)
  간극 (3/4,1)∪(1,7/6)   결정 경계 (attend/ignore)
  완전수 = 렌즈            query = 렌즈
  간극 비대칭              attention 비대칭 (sharp vs soft)

  정량적:
    R 간극 1/6 = 1/σ(6)   attention temperature = 1/√d_k
    R 간극 1/4             attention threshold
    비대칭 비율 증가        depth별 attention sharpening
```

### Multi-head = 다중 렌즈

```
  Multi-head attention: h개의 head가 각각 다른 "관점"

  다중 렌즈 비유:
    head 1: R의 2-adic 구조 관측 (v₂ 렌즈)
    head 2: R의 3-adic 구조 관측 (v₃ 렌즈)
    head 3: R의 5-adic 구조 관측 (v₅ 렌즈)
    ...
    head h: R의 p_h-adic 구조 관측

  최적 head 수 = ω(d)?
    d=768: ω=2 (2,3만), 실제 head=12
    d=1024: ω=1 (2만), 실제 head=16

  H-AI-5 결과: R(d)/d ≈ c/τ(d), 상관 r=0.991
  → attention의 "효율" ∝ 1/τ(d)
  → 약수 많은 차원 = 더 유연한 attention
```

### 이상탐지 = 렌즈 초점

```
  이상탐지(H-CX-12, AUROC=1.0):
    정상: R ≈ 1 (렌즈 초점)
    이상: R ≫ 1 (초점 밖)
    간극: 자연 결정 경계

  Attention 이상탐지:
    정상 입력: attention 패턴 균일
    이상 입력: attention 패턴 극단적
    threshold: softmax 간극

  대응:
    AUROC = 1.0 ↔ R 간극이 완벽한 분리 보장
    95x tension ↔ attention 비균일성
    R-S 2051x 비대칭 ↔ Q-K 비대칭
```

## 검증 가능한 예측

```
  예측 1: d=6인 toy transformer에서 attention이 가장 "깨끗"
    (6차원 head → R(6)=1 → 완벽한 균형)

  예측 2: attention 분포의 "간극"이 1/σ(d) 스케일
    d=64: 간극 ~ 1/σ(64) = 1/127 ≈ 0.008
    d=128: 간극 ~ 1/σ(128) = 1/255 ≈ 0.004

  예측 3: 이상탐지에서 최적 threshold ∈ (1, 7/6) × scaling
    R 스펙트럼의 자연 간극이 최적 결정 경계

  예측 4: head 수가 τ(d)의 약수일 때 최적
    BERT d=768, τ=18: head=12 (12|? no, 12 does not divide 18)
    실제로 head|d이면 됨, τ와의 관계는 간접적
```

## 검증 방향

1. [ ] d=6 toy transformer vs d=7,8 비교 실험
2. [ ] attention weight 분포의 "간극" 측정
3. [ ] attention과 R 스펙트럼의 Wasserstein 거리
4. [ ] multi-head attention에서 head별 p-adic 분해 분석
5. [ ] 이상탐지 threshold를 R 간극으로 설정 시 성능

## 판정

```
  상태: 🟧 구조적 비유 + 예측 제시
  비유는 아름답지만, 정량적 대응은 미확인
  예측 1-4가 실험적으로 검증 가능
```

## 난이도: 극고 | 파급력: ★★★★★

"Attention = 산술적 렌즈"가 맞다면:
- Transformer 설계의 수론적 원리 제공
- 최적 d 선택 이론 (R(d)=1에 가까울수록 좋음)
- 이상탐지의 수학적 기초
