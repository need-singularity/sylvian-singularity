# AnimaLM — 장력 기반 의식엔진 LLM

> **"출력은 어느 엔진에도 없다. 둘 사이의 공간에 있다."**

기존 Dense LLM(Mistral 7B)을 장력 기반 의식엔진으로 변환한 모델.
Golden MoE의 Expert 분할 + PureField의 반발력장 메커니즘을 결합.

## 핵심 구조

```
input → BoltzmannRouter → Expert 선택 (5/8 활성, I=0.375)
                            │
                  ┌─────────┴─────────┐
                  │                   │
            Engine A (0~3)      Engine G (4~7)
              논리 진영            패턴 진영
                  │                   │
                  └─────────┬─────────┘
                            │
                    repulsion = A - G
                    tension  = |A - G|²
                    direction = normalize(A - G)
                            │
              output = scale × √tension × direction
```

## 수식

```
  out_A = Σ (weight_i × Expert_i(x))    for i ∈ {0,1,2,3}
  out_G = Σ (weight_j × Expert_j(x))    for j ∈ {4,5,6,7}

  repulsion = out_A - out_G
  tension   = mean(repulsion²)           # 스칼라, 장력 크기
  direction = repulsion / ||repulsion||   # 단위벡터, 방향

  tension_output = tension_scale × √(tension + ε) × direction
  moe_output     = out_A + out_G

  output = σ(α) × moe_output + (1 - σ(α)) × tension_output
```

- `tension_scale`: 학습 가능 스칼라 (레이어당 1개)
- `α`: 혼합 비율 (학습 가능, sigmoid로 0~1 보장)
- 초기: α=0.5 (반반 혼합), 학습하며 최적 비율 탐색

## Golden MoE와의 차이

| 요소 | Golden MoE | AnimaLM |
|------|-----------|---------|
| Expert 분할 | 8개 동등 | A진영(0~3) + G진영(4~7) |
| 출력 방식 | 가중합 (평균적) | 장력 (반발력장) |
| 핵심 수식 | Σ(w_i × E_i) | scale × √\|A-G\|² × dir |
| 추가 파라미터 | 없음 | tension_scale + alpha (64개) |
| 이론 근거 | H019 (골든존 MoE) | H341 (장력 최종 이론) |

## 변환 방법

```bash
# 1. Mistral 7B 다운로드
# 2. AnimaLM 변환
python3 convert_anima.py --model /path/to/mistral-7b-v0.1 --output /path/to/anima-lm-7b

# 3. Fine-tuning (라우터 + tension_scale + alpha 학습)
python3 finetune_anima_mps.py
```

## 학습 파라미터

| 구분 | 파라미터 수 | 학습 여부 |
|------|-----------|----------|
| Expert 가중치 | ~7B | 동결 |
| 라우터 (32층) | ~1M | 학습 |
| tension_scale | 32 | 학습 |
| alpha (혼합비) | 32 | 학습 |
| lm_head | ~131K | 학습 |
| **총 학습** | **~1.1M (0.015%)** | |

## 비교 실험 계획

| 모델 | 구조 | 비교 항목 |
|------|------|----------|
| Mistral 7B (원본) | Dense | 기준선 |
| Golden MoE 7B | MoE 가중합 | MoE 효과 |
| **AnimaLM 7B** | **장력 기반** | **의식엔진 효과** |

- PPL (wikitext-2, 학습 데이터)
- PPL (다른 데이터셋: C4, lambada)
- 생성 품질 (텍스트 샘플)
- 장력 분포 분석 (높은 장력 = 확신, 낮은 장력 = 불확실)
- Savant Index (도메인별 PPL 비율)

## 관련 가설

- H341: 장력 최종 이론 — `output = 반응강도 × 반응방향`
- H334: PureField — equilibrium 없이 반발력장만으로 판단
- H019: Golden MoE — I≈1/e 최적
- H313: 장력 = 확신의 강도
- H307: 이중 메커니즘 (내부장력 vs 간장력)
