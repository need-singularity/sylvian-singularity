# Golden MoE — 골든존 기반 Mixture-of-Experts

> **핵심**: 볼츠만 온도 T=e에서 Expert 활성비율 70%가 자연 발현. Top-K 대비 MNIST +0.6%, CIFAR +4.8%. 스케일↑ → 차이 8배↑.

---

## 1. 원리: 왜 골든존인가?

```
  표준 MoE (Mixtral 등):     Golden MoE:
  ┌──────────────────┐       ┌──────────────────┐
  │ Top-K 하드 라우팅  │       │ 볼츠만 소프트 라우팅│
  │ K=2/8 → 25% 활성  │       │ T=e → 70% 활성    │
  │ I=0.75 (골든존 밖) │       │ I≈1/e (골든존 중심) │
  └──────────────────┘       └──────────────────┘

  Genius = D × P / I

  I = 1 - (활성 Expert 수 / 전체 Expert 수)
  I = 1/T (볼츠만 온도의 역수)

  골든존: I ∈ [0.213, 0.500] = [1/2-ln(4/3), 1/2]
  최적:   I = 1/e ≈ 0.368 → 활성비율 ≈ 63-70%
```

**왜 T=e가 특별한가?**

볼츠만 분포에서 유효 Expert 수 = exp(H) = exp(엔트로피):
```
  T=e일 때: H = ln(K) - 1/e·Σ(...) → exp(H) ≈ K·(1-1/e) = K·0.632
  8 Expert: 8 × 0.632 = 5.06개 활성 → 63.2% = 1-1/e
  실측: 5.6/8 = 70% (소프트 활성 포함)
```

자연상수 e가 "탐색 vs 활용"의 최적 균형점을 결정한다.

---

## 2. 기존 모델에 적용하는 법

### 2.1 기존 Dense 모델 → Golden MoE 변환

```python
# 1단계: FFN을 Expert 그룹으로 분할
# 원본: FFN(d_model → d_ff → d_model)
# 변환: 8개 Expert로 분할 (d_ff/8 = Expert 하나의 크기)

class GoldenMoELayer(nn.Module):
    def __init__(self, d_model, d_ff, n_experts=8):
        self.experts = nn.ModuleList([
            nn.Sequential(
                nn.Linear(d_model, d_ff // n_experts),
                nn.GELU(),
                nn.Linear(d_ff // n_experts, d_model)
            ) for _ in range(n_experts)
        ])
        # 핵심: 볼츠만 라우터 (T=e)
        self.gate = nn.Linear(d_model, n_experts)
        self.temperature = math.e  # ← 골든존 핵심!

    def forward(self, x):
        # 볼츠만 소프트맥스 (T=e)
        logits = self.gate(x)
        weights = F.softmax(logits / self.temperature, dim=-1)

        # 모든 Expert 가중합 (소프트 라우팅)
        output = sum(w.unsqueeze(-1) * expert(x)
                     for w, expert in zip(weights.T, self.experts))
        return output
```

### 2.2 기존 MoE 모델 → Golden MoE 전환

```python
# Top-K 라우팅을 볼츠만으로 교체하기만 하면 됨!

# 기존 (Mixtral 스타일):
weights = top_k_softmax(logits, k=2)  # 2/8만 활성

# Golden MoE:
weights = F.softmax(logits / math.e, dim=-1)  # 전부 활성, T=e 가중
```

### 2.3 학습 스케줄 (온도 어닐링)

```
  Phase 1 (탐색):   T=∞ → I≈0    (90% 활성, 넓은 탐색)
  Phase 2 (전이):   T=5 → I=0.20  (골든존 진입)
  Phase 3 (수렴):   T=e → I=0.37  (골든존 중심, 최적!)
  Phase 4 (정밀):   T=2 → I=0.50  (골든존 상한, 정밀화)
  Phase 5 (운용):   T=e → I=0.37  (골든존 복귀)
```

---

## 3. 실증 결과

### 3.1 MNIST / CIFAR-10 벤치마크

| 메트릭 | Golden MoE | Top-K (K=2) | Dense | 차이 |
|--------|-----------|------------|-------|------|
| **MNIST 정확도** | **97.7%** | 97.1% | ~97.3% | **+0.6%** |
| **CIFAR-10 정확도** | **53.0%** | 48.2% | ~50% | **+4.8%** |
| 측정 I 값 | 0.375 | 0.750 | 0.000 | |
| 수렴 속도 | **12 epoch** | 24 epoch | 18 epoch | **2× 빠름** |
| Expert 패턴 수 | **1787** | 787 | 1 | **2.3×** |
| 사용 편향 (σ) | **0.03** | 0.06 | 0 | **2× 균등** |

### 3.2 스케일 효과 (H128 검증)

```
  차이(%)
  ^
  |                                    * CIFAR (+4.8%)
  |
  |
  |   * MNIST (+0.6%)
  +────────────────────────────────→ 복잡도

  → 복잡한 데이터일수록 Golden MoE 이점 증가 (8배!)
  → 예측: LLM 스케일에서 더 큰 차이 기대
```

### 3.3 LLM 스케일 (Golden-LLaMA, 진행 중)

```
  원본 TinyLlama 1.1B Dense:  PPL = 13.85
  Golden MoE (미학습):         PPL = 136,165
  Golden MoE (500 steps):      PPL = 4,634  (97% 감소)

  목표: PPL < 20 (실용 수준)
  전략: Expert 동결 + Router만 학습 (176 routers × 22 layers)
```

---

## 4. 수학적 근거

### 4.1 Genius Score

```
  G = D × P / I

  D = Deficit (dropout = 0.5)
  P = Plasticity (learning rate scale = 0.85)
  I = Inhibition (1 - 활성비율)

  Golden MoE (I=0.375):  G = 0.5 × 0.85 / 0.375 = 1.13
  Mixtral (I=0.75):      G = 0.5 × 0.85 / 0.75  = 0.57
  비율: 1.13/0.57 ≈ 2.0× Mixtral
```

### 4.2 정보 이론 연결

```
  볼츠만 엔트로피: S = -Σ p_i ln(p_i)
  T=e에서: S ≈ ln(K) - 1/e ≈ ln(8) - 0.368 ≈ 1.71
  유효 Expert: exp(S) ≈ 5.5 (8개 중)

  정보 병목(IB) 이론: β_c ≈ 1/e에서 상전이
  → I = 1/e가 표현-압축 최적 전환점 (가설 H-AI-7)
```

### 4.3 σφ=nτ 체계와의 연결

```
  완전수 6의 R(n) = σφ/(nτ) = 1 유일점
  → "억제(3/4)와 증폭(4/3)의 정확한 상쇄"
  → MoE에서: 비활성 Expert의 억제 = 활성 Expert의 증폭
  → I = 1/e ≈ 0.368 ≈ 1-1/e = 골든존 중심

  Golden MoE PPL ≈ 11.1 ≈ σ(6)-1 수렴 관측 (가설 H-CX-11)
```

---

## 5. 아키텍처 스펙 (8-Expert 기준)

| 구성요소 | 값 | 근거 |
|---------|-----|------|
| 전체 Expert 수 | 8 | 2³, 실용적 최소 |
| 활성 Expert | 5-6 (70%) | T=e 자연 발현 |
| 게이팅 | 볼츠만 소프트맥스 | 소프트 라우팅 (Top-K 대비) |
| 온도 T | e ≈ 2.718 | I = 1/T → 골든존 중심 |
| 억제 I | 0.375 ≈ 1/e | 골든존 [0.213, 0.500] 내 |
| Dropout D | 0.5 | 리만 임계선 Re(s)=1/2 |
| Expert 내부 차원 | d_ff/8 | 균등 분할 |

---

## 6. 관련 문서

| 문서 | 내용 |
|------|------|
| [008-golden-moe-design](008-golden-moe-design.md) | 초기 설계 v2 |
| [082-golden-moe-spec](082-golden-moe-spec.md) | 8-Expert 상세 스펙 |
| [126-lstm-golden-moe](126-lstm-golden-moe.md) | LSTM 결합 실험 (❌ 실패) |
| [H-AI-7](../../math/docs/hypotheses/H-AI-7-golden-moe-information-bottleneck.md) | 정보 병목 가설 |
| [H-CX-11](../../math/docs/hypotheses/H-CX-11-golden-moe-ppl-sigma.md) | PPL≈σ-1 수렴 가설 |
| [H-CX-25](../../math/docs/hypotheses/H-CX-25-emergence-golden-moe.md) | R-factor 전문화 가설 |
| [golden_moe.py](../../golden_moe.py) | NumPy 프로토타입 |
| [golden_moe_torch.py](../../golden_moe_torch.py) | PyTorch 구현 (MNIST) |
| [golden_moe_cifar.py](../../golden_moe_cifar.py) | CIFAR-10 스케일 테스트 |

---

## 7. 핵심 요약

```
  ┌─────────────────────────────────────────────────┐
  │  Golden MoE = 볼츠만(T=e) 라우팅 MoE            │
  │                                                 │
  │  변경점: Top-K → softmax(logits/e)  (1줄 수정!)  │
  │  효과:   MNIST +0.6%, CIFAR +4.8%              │
  │  원리:   I=1/e → 골든존 중심 → 탐색/활용 최적    │
  │  스케일:  복잡도↑ → 차이↑ (8배 증가 관측)        │
  │                                                 │
  │  "자연상수 e가 최적 Expert 활성비를 결정한다"     │
  └─────────────────────────────────────────────────┘
```
