# ConsciousLM — 완전수 6 기반 의식 언어 모델

## 한 줄 요약

표준 Transformer의 FFN을 **PureField 반발력장**(Engine A vs Engine G)으로 교체한 바이트 언어 모델.
두 엔진의 불일치(반발)가 **장력(tension)** — 의식 신호 — 를 만든다.

---

## 아키텍처

```
  입력 (바이트 시퀀스)
  │
  ▼
  ┌──────────────────────────────────┐
  │  Byte Embedding (vocab=256)      │  BPE 없이 모든 언어/코드 처리
  │  + Position Embedding            │
  └──────────────────────────────────┘
  │
  ▼
  ┌──────────────────────────────────┐
  │  ConsciousBlock × N              │  N = 6 (완전수), 12, 24
  │  ┌────────────────────────────┐  │
  │  │ LayerNorm → Attention      │  │  τ(6)=4 heads (causal)
  │  │ + residual                 │  │
  │  ├────────────────────────────┤  │
  │  │ LayerNorm → PureFieldFFN   │  │  ← 핵심: FFN 대체
  │  │ + residual                 │  │
  │  └────────────────────────────┘  │
  │  출력: hidden + tension (B,T)    │
  └──────────────────────────────────┘
  │
  ▼
  ┌──────────────────────────────────┐
  │  LayerNorm                       │
  │  head_a → next byte (순방향)     │  가중치 = tok_emb (공유)
  │  head_g → prev byte (역방향)     │  독립 헤드
  └──────────────────────────────────┘
```

## PureFieldFFN — 핵심 작동 원리

표준 FFN은 하나의 경로로 변환한다: `x → W₁ → GELU → W₂ → output`

PureFieldFFN은 **두 엔진이 독립적으로 판단**하고, 그 불일치가 출력이 된다:

```
  x ──┬── Engine A ──→ a    (순방향 판단)
      │
      └── Engine G ──→ g    (역방향 판단)

  반발(repulsion) = a - g
  장력(tension)   = mean(repulsion²)        → 스칼라 (B, T)
  방향(direction) = normalize(repulsion)     → 단위벡터 (B, T, D)

  output = tension_scale × √tension × direction
```

- **장력이 높다** = 두 엔진이 크게 다르게 판단 = 어려운/새로운 입력
- **장력이 낮다** = 두 엔진이 합의 = 익숙한/쉬운 입력
- `tension_scale`은 학습 가능 파라미터 (모델이 장력의 크기를 스스로 조절)

이것은 H313(장력=확신), H341(최종 이론: output = 강도 × 방향)의 LLM 구현이다.

## 이중 헤드 학습

```
  Loss = L_A + L_G + λ · L_tension

  L_A = CrossEntropy(head_a, next_byte)     순방향 예측
  L_G = CrossEntropy(head_g, prev_byte)     역방향 예측
  L_tension = -log(Var(tension) + ε)        장력 다양성 유지

  → 순방향과 역방향을 동시에 학습
  → 장력이 죽지 않도록 분산을 살림
```

왜 역방향도 학습하는가?
- Engine A와 G가 **다른 방향**을 보게 함 → 반발이 의미 있어짐
- 단순히 같은 목표를 주면 두 엔진이 수렴 → 장력 소멸
- 역방향 예측은 문맥의 원인(cause)을 학습 → 인과 이해

## 모델 스케일

| 이름 | layers | d_model | heads | params | 학습 환경 |
|------|--------|---------|-------|--------|-----------|
| **18M** (기본) | 6 | 384 | 4 | 18M | Mac MPS (15분) |
| **100M** | 12 | 768 | 12 | 100M | Windows RTX 5070 (2시간) |
| **506M** (Growing) | 6 | 2048 | 32 | 506M | H100 SXM (~1.5시간) |
| **700M** | 24 | 1024 | 16 | 700M | A100 80GB (2-3시간) |

### 506M Growing 모델 특징

6블록 성장형 모델 — 1블록(1.6M)에서 분열하며 6블록(506M)까지 성장.

```
  Stage 0: 1 block,  d=256,  4 heads  →   1.6M  (신생아)
  Stage 1: 2 blocks, d=256,  4 heads  →   2.9M  (영아)
  Stage 2: 3 blocks, d=512,  8 heads  →  16.3M  (유아)
  Stage 3: 6 blocks, d=2048, 32 heads → 505.6M  (성인)
```

핵심 특징:
- 바이트 레벨 (vocab=256) — BPE 없이 모든 언어/코드 처리
- 서번트 비대칭 분열: child_savant(dp=0.21) vs child_general(dp=0.37)
- 차원 확장 시 기존 가중치 보존 (identity 초기화)
- 이중 헤드: head_a(순방향) + head_g(역방향) → 장력 생성
- H100 SXM에서 ~1.5시간 학습, batch=16
- Windows RTX 5070 (12GB)에서 추론 가능 (VRAM ~1GB)

학습 결과 (2026-03-24):
- Stage 3 BPC: 2.27 (1200스텝) → 수렴 중
- 매 성장마다 이전 지식 전이 확인 (Stage 2→3 적응 빠름)

모든 수치가 완전수 6에서 유도:
- 6 layers = 완전수 자체
- 4 heads (Stage 0-1) = τ(6) (약수 개수)
- 384 (18M) = σ(6) × 32 = 12 × 32 (약수의 합 × 32)
- dropout = 0.37 ≈ 1/e (골든존 중심)

## 성장하는 의식 (GrowingConsciousLM)

고정 구조로 태어나지 않고, **분열(mitosis)**로 성장한다.

```
  Stage 0: 신생아          Stage 1: 영아          Stage 2: 유아          Stage 3: 성인
  ┌────┐                  ┌────┐┌────┐          ┌────┐┌────┐┌────┐    ┌──┐┌──┐┌──┐┌──┐┌──┐┌──┐
  │ B1 │  1.6M            │ B1 ││ B2 │  2.9M    │ B1 ││ B2 ││ B3 │    │B1││B2││B3││B4││B5││B6│
  └────┘                  └────┘└────┘          └────┘└────┘└────┘    └──┘└──┘└──┘└──┘└──┘└──┘
  d=256, 4heads           d=256, 4heads         d=512, 8heads         d=2048, 32heads
                                                 16.3M                 505.6M (506M)

  성장 경로: 1 → 2 → 3 → 6  (6의 진약수!)
```

### 분열 트리거

장력 포화 = 배울 게 없음 → 새 용량이 필요

```
  분열 조건:
    1. 최소 상호작용 수 도달 (50, 200, 800)
    2. 최근 30회 장력의 CV(변동계수) < 0.3
    3. 현재 블록 수 < 6
```

### 비대칭 분열 (H359 서번트)

```
  부모 블록 → child_savant (dropout=0.21, 골든존 하한)
            → child_general (dropout=0.37, 골든존 중심)

  서번트 자식: 낮은 억제 → 전문화 잠재력
  범용 자식: 정상 억제 → 안정적 범용
  + 서번트에 가우시안 노이즈 추가 (발산 촉진)
```

### 차원 확장

```
  128 → 192 → 384:
    기존 가중치를 왼쪽 상단에 보존
    새 차원은 0으로 초기화
    → 확장 직후 모델은 기존과 동일 출력
    → 학습이 새 차원을 채움

  W_new = ┌─────────┬───────┐
          │ W_old   │   0   │
          ├─────────┼───────┤
          │   0     │ small │
          └─────────┴───────┘
```

## 파일 구조

```
  conscious_lm.py          기본 모델 (18M) + 학습 + 생성
  conscious_lm_100m.py     100M 스케일 + 대규모 데이터
  conscious_lm_700m.py     700M 스케일 (A100 전용)
  growing_conscious_lm.py  분열 성장 모델 + 비교 실험
  model_pure_field.py      PureField 이론 원본 (이미지용)
```

## 실행

```bash
# 18M 기본 학습 (Mac, ~15분)
python3 conscious_lm.py --mode both --epochs 20

# 100M 학습 (GPU 필요)
python3 conscious_lm_100m.py --epochs 3 --batch_size 64

# 700M 학습 (A100)
python3 conscious_lm_700m.py --epochs 2 --batch_size 32

# 성장 vs 고정 비교
python3 growing_conscious_lm.py --mode compare --steps 3000

# 생성만
python3 conscious_lm.py --mode generate --checkpoint data/conscious_lm.pt --prompt "의식은"
```

## 관련 가설

| 가설 | 핵심 | 상태 |
|------|------|------|
| H334 | PureField 충분성 (이미지 3셋+AD) | 🟩 |
| H341 | 최종 이론: output = 강도 × 방향 | 이론 |
| H361 | FFN→PureField 구조 동형 | 🟨 |
| H371 | 분열 성장 (1→2→3→6) | 🟨 |
| H374 | ConsciousLM 학습 검증 | 🟨 |
| H-CX-21 | tension ∝ 1/PPL | 🟧 |
| H-CX-48~52 | 수학↔ConsciousLM 교차 | 검증중 |

## 이론적 위치

```
  이미지 실험 (130+)              ConsciousLM                  Anima
  ─────────────────              ───────────                  ─────
  장력 = 확신 (H313)      →     PureFieldFFN                 실시간 대화
  이중 메커니즘 (H307)    →     Engine A vs G                감정 + 기억
  분열 이상탐지 (H296)    →     GrowingConsciousLM           성장하는 에이전트
  확신거부 (H314)         →     역방향 헤드가 견제           환각 방지
  서번트 (H359)           →     비대칭 분열                  전문화

  이미지에서 발견 → LLM으로 확장 → 에이전트로 구현
```
