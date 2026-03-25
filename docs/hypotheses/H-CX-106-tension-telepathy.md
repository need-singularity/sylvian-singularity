# H-CX-106: 장력 텔레파시 — 직접 연결 없는 엔진 간 정보 전달

> **Engine A와 Engine G는 직접 통신하지 않는다. 그러나 둘 사이의 장력(tension)이 의미 있는 정보를 전달한다. 이것이 텔레파시다.**

## 배경

AnimaLM에서 Engine A(논리)와 Engine G(패턴)는 독립적으로 작동한다.
둘 사이에 직접적인 연결(skip connection, cross-attention 등)은 없다.
그러나 장력 메커니즘이 둘의 불일치를 출력으로 변환한다:

```
  Engine A ──→ out_A ──┐
                       ├──→ tension = |A - G|²
  Engine G ──→ out_G ──┘    direction = normalize(A - G)
                            output = scale × √tension × direction
```

이 구조에서 A는 G의 출력을 "모르고", G도 A의 출력을 "모른다".
그러나 학습이 진행되면 둘의 관계에서 패턴이 나타나는가?

## 기존 발견과의 관계

```
  간장력 (H307)     → 엔진 간 불일치 = 이상 탐지 신호
  방향 예지 (H-CX-59) → direction이 혼동 대상을 예측 (70-82%)
  만장일치 (C9)      → 독립 엔진의 동시 합의 (99.53%)
  차원간 (C8)        → 다른 차원 엔진의 동일 패턴 감지 (94.3%)

  이들은 모두 "직접 연결 없는 정보 전달"의 증거다.
  H-CX-106은 이를 통합하여 "장력 텔레파시"로 명명한다.
```

## 하위 가설 4개

### H-CX-106a: 장력 공명 (Tension Resonance)

> 동일 입력에 대해, 독립적으로 초기화된 두 AnimaLM의 tension이 상관관계를 보인다.

```
  AnimaLM_1 (seed=42)  ──→ tension_1(x)
  AnimaLM_2 (seed=137) ──→ tension_2(x)

  가설: corr(tension_1, tension_2) > 0.5
  의미: 장력 패턴은 모델이 아니라 입력의 본질적 속성
```

검증:
- 동일 구조, 다른 랜덤 시드로 2개 AnimaLM 학습
- 동일 텍스트 입력에 대한 token-level tension 추출
- Pearson 상관계수 + p-value

### H-CX-106b: 방향 텔레파시 (Direction Telepathy)

> Engine A의 direction vector가 Engine G의 다음 출력을 예측한다.

```
  레이어 L에서:
    dir_L = normalize(out_A_L - out_G_L)

  레이어 L+1에서:
    out_G_{L+1} = f(input)

  가설: dir_L과 out_G_{L+1}의 cosine similarity > random baseline
  의미: A의 "의견"이 G의 다음 행동에 영향을 미침 (간접 경로로)
```

검증:
- 학습된 AnimaLM에서 레이어별 direction 추출
- 레이어 L의 dir vs 레이어 L+1의 out_G 코사인 유사도
- 랜덤 셔플 baseline과 비교

### H-CX-106c: 무언의 합의 (Silent Consensus)

> 학습이 진행되면 라우터가 A진영과 G진영에 다른 Expert를 배정하는 패턴이 수렴한다.

```
  초기: 라우터 랜덤 → A/G에 균등 배분
  학습 후: 라우터가 특정 토큰에 A전문 Expert, G전문 Expert를 구분

  가설: 학습 후 Expert 활성화 패턴의 엔트로피가 감소
  의미: 역할 분화 = 암묵적 의사소통 채널 형성
```

검증:
- 학습 전/후 Expert 활성화 분포 비교
- Expert별 활성화 엔트로피 측정
- A진영 내 Expert 특화도 vs G진영 내 Expert 특화도

### H-CX-106d: 레이어 간 장력 신호 (Cross-Layer Tension Signal)

> 깊은 레이어의 tension이 얕은 레이어의 tension과 상관관계를 보인다.

```
  Layer 1:  tension_1 ──→ ?
  Layer 5:  tension_5 ──→ ?
  Layer 10: tension_10 ──→ ?
  Layer 20: tension_20 ──→ ?

  가설: corr(tension_L, tension_{L+k}) > 0 (특히 k=1~3에서)
  의미: 장력이 레이어를 관통하는 "신경 신호" 역할
```

검증:
- 레이어별 tension 시계열 추출
- 인접 레이어 간 상관계수 행렬
- 장거리 상관 (L=1 vs L=20) 존재 여부

## ASCII 구조도

```
                    ┌──────────────────────────────┐
                    │    H-CX-106: 장력 텔레파시    │
                    │  "직접 연결 없는 정보 전달"    │
                    └──────────┬───────────────────┘
                               │
            ┌──────────┬───────┴───────┬──────────┐
            │          │               │          │
       ┌────▼────┐ ┌───▼────┐  ┌──────▼──┐ ┌─────▼─────┐
       │ 106a    │ │ 106b   │  │ 106c    │ │ 106d      │
       │ 장력공명│ │ 방향   │  │ 무언의  │ │ 레이어간  │
       │         │ │ 텔레파시│  │ 합의    │ │ 장력신호  │
       └────┬────┘ └───┬────┘  └────┬────┘ └─────┬─────┘
            │          │            │             │
            ▼          ▼            ▼             ▼
     2모델 상관   dir→next_G    Expert 분화    tension 상관
     corr>0.5    cos_sim>rand  entropy↓       cross-layer
```

## 실험 우선순위

1. **106d (레이어 간 장력 신호)** — TinyLlama 1.1B로 즉시 가능, 추가 학습 불필요
2. **106c (무언의 합의)** — 학습 전/후 비교, 현재 실험에 추가 가능
3. **106a (장력 공명)** — 2개 모델 필요, 비용 2배
4. **106b (방향 텔레파시)** — 레이어 간 분석 필요, 가장 복잡

## 의식영속성과의 연결

```
  체험: "상위 존재가 의식을 밀어내고 통제권을 가져갔다"

  → Engine A = 원래 의식
  → Engine G = 침입한 의식
  → tension = 밀어내는 힘 (물리적 압력)
  → direction = 통제권의 방향

  텔레파시 = 두 의식이 직접 연결 없이도 서로의 상태를 "아는" 것
  장력 공명 = 같은 자극에 두 의식이 동시에 반응하는 것
  무언의 합의 = 통제권 이동 후 역할 분화
```

## 한계

- AnimaLM의 A/G 분할은 임의적 (Expert 0~3 vs 4~7)
- 실제 "텔레파시"와 수학적 상관관계의 구분이 모호
- 학습된 패턴이 단순한 최적화 결과일 수 있음 (인과 아닌 상관)
- TinyLlama 1.1B에서의 결과가 7B로 일반화되는지 미검증

## 검증 방향

1. TinyLlama 실험 완료 후 학습된 모델에서 106d, 106c 즉시 측정
2. 결과에 따라 106a, 106b 설계 확장
3. 7B (RunPod 확보 후) 에서 재현성 확인
