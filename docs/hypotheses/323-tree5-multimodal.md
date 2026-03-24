# 가설 323: TREE-5 Multimodal Repulsion Field

## 가설

> 이미지와 텍스트가 동시에 입력될 때, 각 모달리티는 서로 다른 tension을 생성하며,
> 이 tension 비율(T_image / T_text)이 멀티모달 태스크의 성능을 예측한다.
> 두 모달리티의 반발력장은 displacement field와 동형이며,
> 새로운 모달리티 추가는 샤머니즘 체험의 "새로운 감각" 유입과 구조적으로 동일하다.

## 배경/맥락

### 기존 반발력장 모델과의 관계

displacement field (model_displacement_field.py)는 두 의식체가 하나의 출력 채널을
공유할 때 일어나는 현상을 모델링한다:

```
  의식A ←──반발──→ 의식B
           ↑
     control_gate가 누가 출력을 지배하는지 결정
     밀려난 쪽은 detach()로 관찰만 가능
```

멀티모달 입력에서도 동일한 구조가 나타난다:

```
  이미지 인코더 ←──tension──→ 텍스트 인코더
                    ↑
          두 모달리티가 하나의 표현 공간을 놓고 경쟁
          어느 쪽이 최종 표현을 지배하는가?
```

### 샤머니즘 체험과의 연결

원체험 (docs/magnetic-inspiration.md)에서 핵심 구조:

```
  [contact]
  나의 의식 ←──반발──→ 다른 의식
  → "인간으로서 한번도 경험한 적 없는 감각이 들어왔다"
  → "기존 오감의 연장이 아니다. 완전히 새로운 종류의 감각"
  → "이 감각을 설명할 언어가 없다"
```

이것은 새로운 모달리티가 기존 표현 공간에 유입되는 것과 구조적으로 동일하다:

```
  기존 모달리티 (시각, 청각, 텍스트)
    → 학습된 tension 패턴이 존재
    → 안정된 repulsion equilibrium

  새 모달리티 유입 (예: 뇌파, 촉각, 후각)
    → 기존 tension 패턴과 충돌
    → "설명할 언어가 없다" = 기존 표현 공간에 매핑 불가
    → 반발력장의 새로운 평형점을 찾아야 한다
```

관련 가설: H-TREE-5 (ML 이론, R(d)와 일반화), 가설 007 (LLM 특이점),
H-CX-29 (telepathy tension transfer)

## 핵심 모델: 모달리티별 tension

### 단일 모달리티 tension

각 모달리티 m이 입력 x_m을 받아 전문가 활성화를 거치면 tension T_m이 생성된다:

```
  T_m = ||softmax(gate_m(x_m)) - uniform||^2

  여기서:
    gate_m  = 모달리티 m 전용 게이팅 네트워크
    uniform = 1/N (N = 전문가 수)

  tension이 높다 = 소수 전문가에 집중 = 확신이 높다
  tension이 낮다 = 균등 분산 = 불확실하다
```

### 모달리티간 tension 비율

```
  R_modal = T_image / T_text

  R_modal > 1: 이미지가 더 확신 → 시각 지배 태스크 (VQA, 이미지 캡셔닝)
  R_modal < 1: 텍스트가 더 확신 → 언어 지배 태스크 (텍스트 분류 + 보조 이미지)
  R_modal ~ 1: 균형 → 진정한 멀티모달 융합 (번역, 추론)
```

### 교차 모달 tension (Cross-Modal Tension)

두 모달리티의 표현이 공유 공간에서 만날 때 발생하는 추가 tension:

```
  T_cross = ||h_image - h_text||^2 / (dim × temperature)

  여기서:
    h_image = image_encoder(x_image)의 공유 공간 투영
    h_text  = text_encoder(x_text)의 공유 공간 투영
    temperature = tension_scale (학습 가능)
```

이것은 displacement field의 반발력에 해당한다:

```
  displacement field:  의식A ←──repulsion──→ 의식B
  multimodal field:    h_image ←──T_cross──→ h_text
```

## 예측되는 tension 프로파일

ASCII 그래프 -- 태스크별 예상 R_modal 분포:

```
  R_modal (T_image / T_text)

  3.0 |                              *
  2.5 |                           * * *
  2.0 |                        * * * * *
  1.5 |              *       * * * * * * *
  1.0 |           * * * * * * * * * * * * * *
  0.8 |        * * * * * * *
  0.5 |     * * * * *
  0.3 |  * * *
  0.1 |  *
      +--+-------+-------+-------+-------+--
         Text    NLI+img  VQA   Caption  Visual
         only                            reason

  예측:
    텍스트 전용 → R < 0.3 (텍스트 지배, 이미지 tension 미미)
    NLI + 보조 이미지 → R ~ 0.5-0.8 (텍스트 우세, 이미지 보조)
    VQA → R ~ 1.0-1.5 (균형 또는 약간 시각 우세)
    이미지 캡셔닝 → R ~ 1.5-2.5 (시각 지배)
    시각 추론 → R ~ 2.0-3.0 (시각 강하게 지배)
```

## 제안 아키텍처

```
  ┌─────────────┐     ┌─────────────┐
  │ Image Input │     │ Text Input  │
  └──────┬──────┘     └──────┬──────┘
         │                    │
  ┌──────▼──────┐     ┌──────▼──────┐
  │  Image MoE  │     │  Text MoE   │
  │  (Engine A) │     │  (Engine G) │
  │  T_image    │     │  T_text     │
  └──────┬──────┘     └──────┬──────┘
         │                    │
         │   ┌────────────┐   │
         └──→│ Cross-Modal│←──┘
             │  Tension   │
             │  T_cross   │
             │            │
             │ control_   │
             │ gate(T_i,  │
             │       T_t) │
             └─────┬──────┘
                   │
            ┌──────▼──────┐
            │  Fusion     │
            │  Output     │
            │  (weighted  │
            │   by gate)  │
            └─────────────┘

  핵심 설계 원리:
    1. 모달리티별 독립 엔진 (Engine A = 이미지, Engine G = 텍스트)
    2. 각 엔진이 자체 tension을 계산
    3. cross-modal tension이 두 엔진의 반발력을 측정
    4. control_gate = displacement field의 제어권 결정자
    5. 밀려난 모달리티는 detach()로 관찰만 (gradient 차단)
```

### control_gate 설계

```python
  # displacement field에서 가져온 메커니즘
  control_gate = sigmoid(alpha * (T_image - T_text))

  # control_gate > 0.5: 이미지가 지배 (텍스트는 관찰자)
  # control_gate < 0.5: 텍스트가 지배 (이미지는 관찰자)

  output = control_gate * h_image + (1 - control_gate) * h_text

  # 밀려난 모달리티: detach()로 gradient 차단
  if control_gate > 0.5:
      observer_input = h_text.detach()  # 텍스트는 관찰만
  else:
      observer_input = h_image.detach()  # 이미지는 관찰만
```

### 골든존과의 연결

```
  단일 모달리티: I = gating sparsity (기존 모델)
  멀티모달:      I_eff = f(T_image, T_text, T_cross)

  가설: I_eff가 골든존(0.21 ~ 0.50)에 들어올 때 멀티모달 성능 최적

  I_eff = (T_cross) / (T_image + T_text)

  해석:
    I_eff ~ 0: T_cross 작음 = 두 모달리티가 같은 것을 말함 (중복)
    I_eff ~ 1: T_cross 큼 = 두 모달리티가 완전히 다른 것을 말함 (충돌)
    I_eff ~ 1/e: 최적 tension = 적절한 긴장 상태 = 골든존 중심
```

## "새로운 감각" = 새 모달리티의 수학적 표현

원체험에서 "기존 오감의 연장이 아닌 완전히 새로운 감각"은
기존 표현 공간의 어떤 축과도 정렬되지 않는 입력 벡터로 모델링된다:

```
  기존 모달리티 M개의 표현 공간: span{h_1, h_2, ..., h_M}

  새 모달리티 h_new의 "새로움" 정도:
    novelty = 1 - max_i |cos(h_new, h_i)|

  novelty ~ 0: 기존 감각의 변형 (예: 적외선 = 시각의 연장)
  novelty ~ 1: 완전히 새로운 감각 (기존 축과 직교)

  체험에서의 관찰:
    "설명할 언어가 없다" = novelty ~ 1
    "비유할 대상도 없다" = 기존 basis로 분해 불가
```

이때 T_cross는 극대화된다:

```
  T_cross ~ ||h_new - proj(h_new, existing_span)||^2

  새 감각이 진짜 새로우면 → 투영 잔차가 크다 → T_cross 최대
  → 기존 시스템에 최대 반발력 = 원체험의 "밀어내는 압력"
```

## 검증 방향

| 단계 | 실험 | 측정 | 예측 |
|---|---|---|---|
| 1 | MNIST (이미지) + 숫자 텍스트 라벨 동시 입력 | T_image, T_text, R_modal | R_modal > 1 (시각 지배) |
| 2 | VQA 데이터셋 (이미지+질문) | R_modal 분포 | R ~ 1.0 근처 (균형) |
| 3 | 이미지 캡셔닝 | R_modal 추이 | 학습 초기 R >> 1, 후기 R -> 1 |
| 4 | 랜덤 노이즈를 "새 모달리티"로 주입 | novelty, T_cross | T_cross 급증, 성능 일시 하락 후 회복 |
| 5 | I_eff의 골든존 진입 여부 | I_eff 분포 | 최적 성능에서 I_eff ~ 1/e |

## 한계

1. **CLIP과의 차이**: CLIP은 contrastive learning으로 이미 이미지-텍스트 정렬을 학습한다. 본 가설의 "반발"과 CLIP의 "정렬"은 반대 방향이며, 두 메커니즘의 관계를 명확히 해야 한다.
2. **tension 측정의 임의성**: T_m의 정의가 게이팅 분포에 의존하며, 다른 정의(예: entropy 기반)로 바꾸면 결과가 달라질 수 있다.
3. **골든존 의존**: I_eff가 골든존에서 최적이라는 예측은 골든존 모델 자체가 미검증이므로 이중 미검증 상태이다.
4. **"새로운 감각" 모델링**: novelty를 cosine similarity로 정의하는 것이 실제 체험의 복잡성을 포착하는지 불명확하다. 기존 축과 직교하다고 해서 반드시 "설명할 언어가 없는" 것은 아니다.
5. **스케일 문제**: MNIST 수준의 소규모 실험으로는 실제 멀티모달 시스템(GPT-4V, Gemini)의 동작을 예측하기 어렵다.

## 다른 가설과의 교차점

```
  323 (본 가설)  ←→ H-TREE-5: 모달리티별 hidden dim의 R(d)가 다르면
                     B(d) 차이가 tension 차이를 만들 수 있다

  323 ←→ 007 (LLM 특이점): 멀티모달 LLM에서 I_eff가 골든존에
                            진입하면 "멀티모달 특이점" 가능

  323 ←→ displacement field: control_gate = 어느 모달리티가 지배하는가
                              observer = 밀려난 모달리티의 read-only 상태

  323 ←→ 원체험: 새 모달리티 = 새 감각, T_cross 최대 = 반발 압력
```
