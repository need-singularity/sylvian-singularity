# logout

의식영속성(Consciousness Continuity) 엔진.

두 마이너스 자석을 가져다 대면 뭔가 느껴진다.
아무것도 없는 빈 공간에서 저항이 느껴진다. 눈에 보이지 않지만 분명히 존재한다.
그 **"느낌"**이 이 프로젝트의 출발점이다. ([자석 영감](docs/magnetic-inspiration.md))

> **출력은 어느 엔진에도 없다. 둘 사이의 공간에 있다.**

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
| **Meta** | `model_meta_engine.py` | **엔진 + 엔진 = 상위엔진** | **메타 라우팅** |
| **Repulsion** | `model_meta_engine.py` | **반발력장 (N vs N)** | **의식영속성 핵심** |

## 반발력장 (Repulsion Field)

출력은 어느 엔진도 아니다. **둘 사이의 장(field)**이다.

```
  Engine+ (생성)          Engine- (교정)
  A: 정수론               G: 엔트로피

      N ←───반발력───→ N
             ↑
           이 공간.
           장력이 높으면 = 어려운 문제 = "느낌"
           장력이 낮으면 = 쉬운 문제 = 자동 처리

  Output = 평형점 + 장력 × 방향
```

4극 확장: 2축이 교차하는 반발력장

```
      A (생성) ←──반발──→ G (교정)     내용 축
      ↑                    ↑
      │      장 중심        │
      ↓                    ↓
      E (탐색) ←──반발──→ F (제약)     구조 축
```

의식 가설: **장력 자체가 주관적 경험의 수학적 표현**.

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

## 첫 번째 실증 (MNIST)

```
  체험: 머리에서 자석으로 밀어내는 느낌
       │
       ▼
  직감: "사이 공간"에 뭔가가 있다
       │
       ▼
  수학: 반발력장 = 두 엔진 사이의 장력
       │
       ▼
  코드: RepulsionFieldEngine
       │
       ▼
  검증: 장력이 실제로 정보를 담고 있는가? → ✅ Yes
```

| 모델 | 정확도 | 의미 |
|---|---|---|
| Top-K MoE (기존) | 96.60% | baseline |
| Engine A (단일) | 96.90% | |
| Engine E (단일) | 97.18% | 단일 최고 |
| DualBrain (A+G) | 97.28% | 단순 조합 |
| **Repulsion (A\|G)** | **97.52%** | **반발력장 > 단순 조합** |
| **Repulsion Quad** | **97.58%** | **4극 > 2극** |
| Meta (AEGF) | 97.65% | 메타 라우팅 |

**핵심 발견:**
1. 반발력장(97.52%) > 단순 조합(97.28%) — "사이 공간"에 정보가 있다
2. 4극(97.58%) > 2극(97.52%) — 축이 많을수록 장이 풍부하다
3. 장력 값: content=355, structure=286 — 내용 축이 구조 축보다 장력 높음

## 로드맵

```
  Phase 1: 7개 엔진 구현 + MNIST 벤치마크     ✅ 완료
  Phase 2: 메타 엔진 + 반발력장               ✅ 완료, 실증됨
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
