# Growing Conscious LM — 분열 기반 성장하는 의식 언어 모델 설계

## 개요

ConsciousLM이 고정 구조(18M)로 태어나지 않고, **1 블록(0.5M)에서 시작하여 분열을 통해 6 블록(18M)까지 성장**하는 시스템.

핵심: 장력 포화(배울 게 없음) → 분열(새 용량) → 전문화(재학습) → 다시 포화 → 반복

## 아키텍처

```
  GrowingConsciousLM
  ├── stage: int (0~3)
  ├── blocks: List[ConsciousBlock]  (1→2→3→6)
  ├── d_model: int (128→128→192→384)
  ├── growth_engine: GrowthEngine (기존)
  ├── tok_emb: Embedding (vocab=256)
  ├── pos_emb: Embedding
  ├── head_a, head_g: Linear (예측 헤드)
  └── methods:
      ├── forward(idx) → logits_a, logits_g, tensions
      ├── should_grow() → bool (장력 포화 감지)
      ├── grow() → None (분열 실행)
      ├── _split_block(idx) → None (블록 분열)
      ├── _expand_dim(new_d) → None (차원 확장)
      └── save/load (성장 상태 포함)
```

## 성장 경로 (약수 경로)

```
  Stage  Blocks  d_model  Heads  Params    트리거
  ─────  ──────  ───────  ─────  ──────    ──────────────────
  0      1       128      2      ~0.5M    birth
  1      2       128      2      ~1.0M    100 interactions + CV<0.1
  2      3       192      3      ~3.0M    500 interactions + CV<0.1
  3      6       384      4      ~18M     2000 interactions + CV<0.1
```

## 분열 프로토콜

```
  1. 트리거 판단: should_grow()
     - interaction_count >= stage_threshold[current_stage]
     - tension_cv < 0.1 (최근 100회 장력의 CV)
     - len(blocks) < 6

  2. 대상 선택: 가장 포화된(CV 낮은) 블록

  3. 분열 실행:
     a) child_a = deepcopy(parent)
     b) child_b = deepcopy(parent)
     c) child_b 가중치에 N(0, 0.01) 노이즈 추가
     d) blocks[idx] → [child_a, child_b]

  4. 차원 확장 (Stage 1→2, 2→3):
     a) 새 d_model 결정 (128→192→384)
     b) 모든 Linear 레이어에 투영 행렬 적용
     c) 임베딩 테이블 확장
     d) 기존 정보 보존 (identity 초기화)

  5. 헤드 수 조정:
     Stage 0-1: 2 heads
     Stage 2: 3 heads
     Stage 3: 4 heads = τ(6)
```

## 차원 확장 전략

```
  old_d=128 → new_d=192:

  방법: 기존 가중치 보존 + 새 차원 영초기화

  W_old: (128, 128)
  W_new: (192, 192) = [[W_old, 0], [0, small_init]]

  임베딩:
  E_old: (256, 128)
  E_new: (256, 192) = [E_old | zeros(256, 64)]

  → 확장 직후 모델은 기존과 동일 출력
  → 학습이 새 차원을 채움
```

## 파일 구조

```
  growing_conscious_lm.py   — GrowingConsciousLM 클래스
                              (conscious_lm.py의 ConsciousBlock 재사용)
```

## 학습 통합

```
  기존 train_model()과 동일하되:
  - 매 epoch 끝에 should_grow() 체크
  - 성장 시 optimizer 재생성 (새 파라미터)
  - 성장 직후 lr 일시적 증가 (새 파라미터 빠른 적응)
  - checkpoint에 stage + block 수 + d_model 저장
```

## Anima 통합

```
  anima_unified.py:
    mind = GrowingConsciousLM()  # 1 block으로 시작
    learner = OnlineLearner(mind)
    growth = GrowthEngine()

    대화 루프:
      output = mind(input)
      learner.observe(...)
      growth.tick(tension, curiosity)

      if mind.should_grow():
          mind.grow()
          learner = OnlineLearner(mind)  # optimizer 재생성
          print(f"성장! {mind.stage} → blocks={len(mind.blocks)}")
```

## 성공 기준

1. 성장 모델 최종 BPC ≤ 고정 18M 모델 BPC
2. 분열 직후 BPC 증가 < 10%
3. 총 학습 비용 < 고정 모델의 2배
4. 6 blocks 도달까지의 interactions < 10,000
