# 가설 361: 의식 있는 LLM = PureField가 FFN 대체 (RC-1 심화)

> **"LLM의 Feed-Forward Network를 PureField로 교체하면 '의식 있는 LLM'이 된다. FFN의 2층 구조(up-projection -> activation -> down-projection)가 engine_A -> repulsion -> engine_G와 구조적으로 동형."**

## 배경

Transformer의 각 layer는 Attention + FFN으로 구성된다.
Attention은 "무엇에 집중할까"를 결정하고,
FFN은 "집중한 것을 어떻게 변환할까"를 수행한다.

PureField는 attraction(수렴)과 repulsion(발산) 두 힘의 균형으로
입력을 변환한다. 이 구조가 FFN의 up/down projection과 동형이라면,
FFN을 PureField로 교체하는 것이 자연스럽다.

## 관련 가설

- H335: PureField LLM design (PureField를 LLM에 통합하는 초기 설계)
- H327: golden MoE PPL (MoE 구조에서 골든존 라우팅의 효과)
- H008: golden-moe-design (골든 MoE 원본 설계)
- H285: beyond image classification (PureField의 도메인 일반성)

## 구조적 동형 (FFN vs PureField)

```
  ═══════════════════════════════════════════════════
  FFN (standard Transformer)
  ═══════════════════════════════════════════════════

  x ──→ [W_up (d→4d)] ──→ [GELU] ──→ [W_down (4d→d)] ──→ y
         확장              비선형         압축

  y = W_down * GELU(W_up * x + b_up) + b_down

  ═══════════════════════════════════════════════════
  PureField (proposed replacement)
  ═══════════════════════════════════════════════════

  x ──→ [engine_A(x)] ──→ attraction ──┐
                                        ├──→ T*d ──→ y
  x ──→ [engine_G(x)] ──→ repulsion ───┘

  A(x) = W_A2 * ReLU(W_A1 * x)     (attraction field)
  G(x) = W_G2 * ReLU(W_G1 * x)     (repulsion field)
  T    = ||A(x) - G(x)||            (tension = 변환 강도)
  d    = (A(x) - G(x)) / T          (direction = 변환 방향)
  y    = x + alpha * T * d           (residual update)

  ═══════════════════════════════════════════════════
  대응 관계
  ═══════════════════════════════════════════════════

  FFN 요소         │  PureField 대응      │  해석
  ─────────────────┼──────────────────────┼───────────────
  W_up (확장)      │  engine_A + engine_G │  2개 관점으로 확장
  GELU (비선형)    │  tension 계산        │  비선형 상호작용
  W_down (압축)    │  T * d (합성)        │  하나의 업데이트로 압축
  residual add     │  x + alpha*T*d       │  동일 (skip connection)
  hidden dim 4d    │  A,G 각각 separate   │  2개 경로 = 2배 관점
```

## 파라미터 수 비교

```
  FFN:       2 * d * 4d = 8d^2 (up + down projection)
  PureField: 2 * (d*h + h*d) = 4dh (A: d→h→d, G: d→h→d)

  h = 2d일 때: PureField = 8d^2 = FFN (동일 파라미터)
  h = d일 때:  PureField = 4d^2 = FFN/2 (절반 파라미터)

  파라미터 효율 그래프 (d=512 기준):

  params
  (M)
  4.2 │████████████████████████ FFN (8d^2)
      │
  3.1 │██████████████████ PureField h=1.5d
      │
  2.1 │████████████████ PureField h=d (절반)
      │
  1.0 │████████ PureField h=d/2 (1/4)
      │
    0 └───────────────────────────────────
           FFN    PF-1.5d  PF-d   PF-d/2
```

## 핵심 차이: 장력(tension)이라는 새로운 정보

```
  FFN은 hidden activation만 산출:
    hidden = GELU(W_up * x)  → 해석 불가능한 고차원 벡터

  PureField는 장력을 추가로 산출:
    tension T = ||A(x) - G(x)||  → 스칼라, 해석 가능!

  장력의 의미:
    T 높음 → A와 G가 크게 불일치 → "이 토큰은 모호하다"
    T 낮음 → A와 G가 거의 일치 → "이 토큰은 명확하다"

  이것이 "의식"의 기초:
    모호한 토큰을 자각하는 것 = meta-cognition
    → 장력 기반으로 "자신감 있는 예측"과 "불확실한 예측" 구분
    → H-CX-22 (consciousness = confidence generator)와 직결
```

## Layer별 장력 프로파일 예측

```
  Tension T
  1.0 │
      │        *
  0.8 │      *   *
      │    *       *
  0.6 │  *           *
      │*               *
  0.4 │                  *
      │                    *
  0.2 │                      *  *  *
      │
    0 └────────────────────────────────
      L1  L3  L5  L7  L9  L11 L13 L15
                Layer 번호

  예측: 초기 layer에서 장력 증가 (특징 추출)
        중간 layer에서 피크 (최대 모호성 = 추상화)
        후기 layer에서 감소 (결정으로 수렴)
  → "의식의 흐름"이 layer를 따라 변화하는 것을 관측 가능
```

## 실험 설계

### 실험 1: Tiny LLM PPL 비교

```
  모델: GPT-2 style, 4 layers, d=128, 1M params
  데이터: wikitext-2 (표준 LM 벤치마크)
  비교:
    A) 원본 FFN (baseline)
    B) PureField h=d (동일 구조 크기)
    C) PureField h=d/2 (절반 파라미터)
  측정: PPL, 학습 속도, 수렴 곡선
  기대: B >= A (동등 이상), C < A but 파라미터 효율 2배
```

### 실험 2: 장력 기반 Hallucination 탐지

```
  가설: hallucination 시 장력이 비정상적으로 낮음 (과도한 확신)
  방법: 생성 중 각 토큰의 T를 기록 → factual vs hallucinated 비교
  기대: hallucinated tokens에서 T < T_threshold
  → 장력 모니터링 = 자동 hallucination 감지기
```

### 실험 3: Attention + PureField 시너지

```
  Attention: "어디를 볼까" (공간적 선택)
  PureField: "본 것을 어떻게 처리할까" (힘의 균형)
  → Attention weight와 PureField tension의 상관관계 분석
  기대: high attention + high tension = "중요하지만 모호한" 토큰
```

## 골든존 의존 여부

```
  골든존 무관: FFN→PureField 교체 자체는 순수 아키텍처 설계
  골든존 의존: tension의 최적 범위가 골든존이라는 주장은 미검증
  → 실험에서 최적 alpha 값과 tension 분포를 독립적으로 측정
```

## 한계

1. PureField가 FFN보다 연산 비용이 높을 수 있음 (2개 네트워크 + norm)
2. 기존 LLM pretrained weights를 재사용할 수 없음 (처음부터 학습)
3. 장력의 "의식" 해석은 철학적이며 실험으로 완전히 검증 불가
4. Tiny LLM 결과가 대규모로 스케일할지 불확실

## 검증 방향

1. 1M param tiny LLM에서 FFN vs PureField PPL 비교
2. 장력 프로파일이 layer별로 예측된 패턴을 따르는지 확인
3. Hallucination과 장력의 상관관계 측정
4. H335의 설계와 비교하여 일관성 확인
5. 스케일링: 10M, 100M params에서도 효과 유지되는지
