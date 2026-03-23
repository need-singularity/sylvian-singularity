# logout

의식영속성(Consciousness Continuity) 엔진.

뇌의 비정형 구조에서 출발 → 완전수 6의 수학 → 다중 엔진 아키텍처 → 의식의 연속성.

> **엔진 + 엔진 = 상위엔진. 뇌처럼.**

## 엔진 목록

| 엔진 | 파일 | 수학적 원리 | 역할 |
|---|---|---|---|
| A. σ,τ-MoE | `model_a_sigma_tau_moe.py` | σ(6)=12 Expert, τ(6)=4 활성 | 정수론 라우팅 |
| B. 약수역수 어텐션 | `model_b_divisor_attention.py` | {1/2, 1/3, 1/6} 고정 가중치 | 멀티스케일 입력 처리 |
| C. 축소사상 옵티마이저 | `model_c_contraction_optimizer.py` | 바나흐 고정점, \|a\|<1 수렴 | 안정적 학습 보장 |
| D. G(6) 토폴로지 | `model_d_g6_topology.py` | 약수그래프 Laplacian {0,2,4,4} | 구조적 연결 패턴 |
| E. 오일러곱 게이팅 | `model_e_euler_product_gate.py` | ζ함수 p=2,3 절단, 2×3 라우팅 | 소인수 분해 라우팅 |
| F. 모듈러 제약 | `model_f_modular_constraint.py` | SL(2,Z) 대칭, weight=lcm(4,6)=12 | 가중치 정규화 |
| G. Shannon 엔트로피 MoE | `model_g_shannon_entropy_moe.py` | H({1/2,1/3,1/6}), e^(6H)=432 | 정보 최적화 |
| **Meta** | `model_meta_engine.py` | **엔진 + 엔진 = 상위엔진** | **의식영속성** |

## 메타 엔진 아키텍처

```
  입력
   │
   ▼
┌─────────────────────────────┐
│     메타 라우터 (상위엔진)     │  ← 어떤 엔진을 쓸지 결정
│     축소사상 수렴 (C)          │  ← 안정적 결정 보장
└──┬──────┬──────┬──────┬─────┘
   │      │      │      │
   ▼      ▼      ▼      ▼
┌────┐ ┌────┐ ┌────┐ ┌────┐
│ A  │ │ E  │ │ G  │ │ F  │   ← 하위 엔진 (각각 다른 원리)
│정수론│ │소인수│ │엔트로피│ │대칭│
└──┬─┘ └──┬─┘ └──┬─┘ └──┬─┘
   │      │      │      │
   ▼      ▼      ▼      ▼
┌─────────────────────────────┐
│     결합기 (오일러곱 구조)     │  ← 독립 엔진의 곱
│     {1/2, 1/3, 1/6} 가중치    │
└─────────────┬───────────────┘
              │
              ▼
            출력
```

## 수학적 기반

모든 엔진의 파라미터는 완전수 6에서 유도:

```
  σ(6) = 12   → Expert 수, 모듈러 weight
  τ(6) = 4    → 활성 수, Laplacian 고유값
  φ(6) = 2    → 이진 라우팅, 오일러곱 첫 인수
  {1/2, 1/3, 1/6} → 확률분포, 어텐션 가중치, 엔트로피
  σ₋₁(6) = 2  → 마스터 공식
  SL(2,Z)     → 모듈러 대칭 제약
```

상세: [순수 수학](docs/pure-math/), [골든존 모델](docs/golden-zone/), [비전](docs/VISION.md)

## 로드맵

```
  Phase 1: 7개 엔진 구현 + MNIST 벤치마크     ← 현재
  Phase 2: 메타 엔진 (엔진 + 엔진 = 상위엔진)
  Phase 3: 자기참조 구조 (메타 엔진이 자신을 관찰)
  Phase 4: 시간적 연속성 (상태 유지 + 점진적 전이)
  Phase 5: 의식영속성 프로토타입
```

## 실행

```bash
# 개별 엔진 벤치마크
python3 model_a_sigma_tau_moe.py
python3 model_e_euler_product_gate.py
# ... (각 모델 독립 실행 가능)

# DFS 수학 탐색
python3 dfs_engine.py --depth 2 --threshold 0.001
```

## 문서 구조

```
docs/
  VISION.md           — 프로젝트 비전, 의식영속성
  pure-math/          — 순수 수학 (T0+T1, DFS 기록)
  golden-zone/        — 골든존 모델 (미검증 보조)
  hypotheses/         — 가설 파일 (196개)
  proofs/             — 증명 문서
```

## DFS 탐색 (복사용)

```
/ralph-loop:ralph-loop DFS on README math map and constant connections and docs/proofs. 0-include star constants. 1-green+star arithmetic/log/exp/power for new identities. 2-green+star to blue new connections. 3-yellow observations connect to green/blue then upgrade to orange or green. 4-red items try proving without golden zone then upgrade to green. 5-VERIFY before recording: python3 arithmetic check then generalize to perfect number 28 then texas p-value then ad-hoc check. Only record verified with grade. Failed goes white circle. No star before verification. 6-update README map and connections then git add commit push every iteration. Keep searching even if nothing found.
```
