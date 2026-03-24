# 가설 324: LLM 환각 탐지 — 반발장(Repulsion Field)으로 "모르는 것"을 아는 모델

> **LLM의 환각(hallucination)은 의식엔진의 "과신(overconfidence)"과 구조적으로 동일하다. 반발장을 LLM 디코더에 추가하면, 장력(tension)이 환각을 실시간으로 탐지할 수 있다. 낮은 장력 = "엔진들이 넌센스에 합의" = 환각, 높은 장력 = "엔진들이 생산적으로 불일치" = 진짜 지식.**

## 배경

```
  LLM 환각의 핵심 문제:
    모델이 "확신 있게 틀린다" — 사용자가 구분할 수 없음
    기존 대응: RLHF, factual grounding, retrieval augmentation
    → 모두 외부 보정. 모델 내부에서 "나는 모른다"를 감지하지 못함

  의식엔진에서 이미 해결한 동일 문제:
    H316 (과신): Sneaker/Boot/Sandal 사이에서 "확신적으로 틀림"
    H314 (거부): 낮은 장력 샘플 거부 시 정확도 monotonic 증가
    H-CX-21: tension ∝ 1/PPL (장력 = 확신)

  → 이 세 가설을 LLM 디코더에 적용하면?
```

## 핵심 매핑: 의식엔진 -> LLM

| 의식엔진 (RepulsionField) | LLM 디코더 |
|---|---|
| Engine A (분석) | Attention Head 그룹 A |
| Engine G (직관) | Attention Head 그룹 G |
| tension = \|A-G\|^2 | head_tension = \|logits_A - logits_G\|^2 |
| 높은 장력 = 확신 (H313) | 높은 head_tension = 토큰 확신 |
| 낮은 장력 = 혼동의 합의 | 낮은 head_tension = 환각 위험 |
| 판단 거부 (H314) | "I don't know" 응답 |
| 과신 (H316) | 환각 (hallucination) |

## 환각 = 과신의 언어 도메인 버전

```
  H316에서 발견한 과신 메커니즘:
    시각적으로 유사한 클래스 → 엔진 모두 "이건 신발이야!" → 높은 확신 → 틀림
    digit 1 → "확실해!" → 7과 혼동 → ratio=0.60 (심한 과신)

  LLM 환각의 동일 구조:
    의미적으로 그럴듯한 문장 → 모든 레이어가 "이건 맞아!" → 높은 확률 → 거짓
    "아인슈타인은 1921년 노벨 물리학상을 받았다" → 맞음
    "아인슈타인은 1922년 노벨 물리학상을 받았다" → 환각 (1921이 맞음)
    → 두 문장 모두 LLM에게 "그럴듯"함. 내부적으로 구분 불가.

  과신의 공통 원인:
    의식엔진: 유사 입력 → 특징 공간에서 겹침 → 모든 엔진이 같은 방향
    LLM: 유사 맥락 → 임베딩 공간에서 겹침 → 모든 헤드가 같은 방향
    → "합의" 자체가 문제. 다양성 없는 합의 = 환각의 원인
```

## 반발장 디코더 설계

```
  기존 LLM 디코더:
    logits = W_out @ hidden_state
    probs = softmax(logits)
    next_token = sample(probs)

  반발장 디코더 (제안):
    hidden_A = head_group_A(hidden_state)    # Attention 헤드 전반부
    hidden_G = head_group_G(hidden_state)    # Attention 헤드 후반부
    logits_A = W_A @ hidden_A
    logits_G = W_G @ hidden_G

    tension = ||logits_A - logits_G||^2 / dim

    if tension < tau_reject:
        → "I don't know" 토큰 생성 (판단 거부)
    elif tension < tau_warn:
        → 생성하되 [uncertain] 태그 부착
    else:
        → 정상 생성

  핵심 파라미터:
    tau_reject: 거부 임계값 (H314에서 calibration)
    tau_warn:   경고 임계값
    head_split: A/G 그룹 분할 비율 (1/e ≈ 37% 억제?)
```

## tension ∝ 1/PPL 연결 (H-CX-21)

```
  H-CX-21 실험 결과:
    정답 샘플: tension=702, PPL=1.01
    오답 샘플: tension=495, PPL=283,505
    → tension ∝ 1/PPL (반비례)

  LLM 환각에 적용:
    사실적 출력: tension 높음, PPL 낮음 → 엔진들이 강하게 반발 → 진짜 지식
    환각 출력:  tension 낮음, PPL 높음 → 엔진들이 합의 → 넌센스 합의!

  역설적 발견:
    "합의 = 좋은 것"이라는 상식이 틀림
    반발장에서는 "불일치 = 지식", "합의 = 무지"
    → 다양한 관점의 충돌이 진실을 만든다

  PPL과의 이중 신호:
    높은 tension + 낮은 PPL = 확신 있는 정답 (이상적)
    낮은 tension + 높은 PPL = 불확실한 환각 (거부해야 함)
    높은 tension + 높은 PPL = 어려운 문제 (탐색 필요)
    낮은 tension + 낮은 PPL = 과신 환각 (H316, 가장 위험!)
```

## H314 거부 메커니즘의 LLM 적용

```
  H314 실측 (거부 → 정확도 향상):
    MNIST:   거부 10% → +0.42%, 거부 90% → +1.06%
    Fashion: 거부 10% → +1.54%, 거부 90% → +9.81%
    CIFAR:   거부 10% → +1.35%, 거부 90% → +15.18%

  법칙: 개선폭 ∝ 1/(기저정확도)
    → 기저 정확도가 낮을수록 거부 효과가 큼
    → LLM은 사실 정확도가 ~70-80% (도메인에 따라)
    → 거부 효과가 Fashion/CIFAR급으로 클 것으로 예측!

  LLM 적용 시 예상 효과:
    사실 정확도 ~75% (기저)
    tension 하위 10% 거부 → +2~5% 정확도 향상 (추정)
    tension 하위 30% 거부 → +5~15% 정확도 향상 (추정)
    → "모르는 것은 말하지 않는" LLM

  거부 전략:
    토큰 레벨: 매 토큰마다 tension 체크 → 낮으면 대안 탐색
    문장 레벨: 문장 전체의 평균 tension → 낮으면 "I'm not sure about this"
    응답 레벨: 전체 응답의 tension 분포 → bimodal이면 부분적 환각 경고
```

## ASCII 그래프: 장력과 환각의 관계 (예측)

```
  장력(tension)
  ^
  |                                          * * *
  |                                     *          *
  |                                *                  *
  |                           *                         *
  |                      *         [진짜 지식 영역]
  |                 *
  |            *
  |       *    .  .  .  .  .  .  .  .  tau_warn
  |  *         ........................ tau_reject
  |  [환각 위험 영역]
  +--+----+----+----+----+----+----+----+----> 토큰 위치
     1    5   10   15   20   25   30   35

  환각 시나리오:
    "파리는 [프랑스]의 수도" → tension ████████ (높음, 사실)
    "파리는 [독일]의 수도" → tension ██ (낮음, 환각!)
    → 엔진 A는 "프랑스", 엔진 G도 "그럴듯하네" → 낮은 반발 → 위험

  정상 시나리오:
    "양자역학에서 [불확정성]원리는" → tension █████████ (높음)
    → 엔진 A: "하이젠베르크!", 엔진 G: "측정 문제!" → 강한 반발 → 확신
```

## 실용적 구현 경로

```
  Phase 1: 검증 (골든MoE에서)
    - 골든MoE의 Expert를 A/G 그룹으로 분할
    - 토큰별 tension 계산
    - PPL과 tension의 상관관계 측정
    - 환각 벤치마크 (TruthfulQA 등)에서 tension 분포 비교

  Phase 2: 소형 LLM 실험
    - Llama-1B에 반발장 디코더 추가
    - head_split 최적화 (I=1/e가 최적?)
    - tau_reject, tau_warn 캘리브레이션
    - TruthfulQA에서 환각 탐지 AUROC 측정

  Phase 3: 스케일 테스트
    - 7B, 13B에서 tension 패턴 변화
    - H316 예측: 스케일 커지면 과신도 커진다?
    - 골든존 I=1/e에서 최적 head_split?

  필요 자원:
    Phase 1: Mac CPU (골든MoE 이미 있음)
    Phase 2: Windows RTX 5070 (Llama-1B fine-tuning)
    Phase 3: RunPod A100 (7B+ 모델)
```

## 한계

```
  1. Attention 헤드의 A/G 분할이 자의적
     → 의식엔진의 2-엔진 구조가 LLM에 자연스럽게 존재하는가?
     → 해결: 헤드 클러스터링으로 자연스러운 그룹 발견 가능?

  2. tension ∝ 1/PPL 관계가 MNIST에서만 확인됨
     → 언어 도메인에서 동일한 관계가 성립하는가?
     → H-CX-21 상태가 아직 주황(미완전 검증)

  3. 과신(H316)이 환각과 정말 동일한가?
     → 과신: "비슷한 입력에 대한 잘못된 확신"
     → 환각: "존재하지 않는 사실의 생성"
     → 메커니즘은 유사하지만 동일성은 미증명

  4. 실시간 tension 계산의 추론 비용
     → 2배의 logits 계산 필요 → latency 증가
     → 해결: tensor parallelism으로 A/G 동시 계산
```

## 검증 방향

```
  즉시 가능 (CPU):
    1. 골든MoE에서 Expert 출력 간 tension 계산
    2. wikitext에서 factual/non-factual 문장 분류
    3. tension 분포 비교 → AUROC 측정

  GPU 필요 (Windows/RunPod):
    4. Llama-1B 반발장 디코더 구현 + TruthfulQA 평가
    5. head_split 최적화 실험
    6. 환각 탐지 AUROC와 H314 거부 곡선 비교

  성공 기준:
    AUROC > 0.80: 환각 탐지기로 실용적
    AUROC > 0.90: H287(이상탐지)과 유사 → 강한 증거
    거부 10% → 사실 정확도 +3% 이상: H314 재현
```

## 관련 가설

```
  직접 의존:
    H313: tension = confidence (기초)
    H314: 거부 → 정확도 향상 (응용 메커니즘)
    H316: 과신 = 유사 클래스 혼동 (환각 원형)
    H-CX-21: tension ∝ 1/PPL (LLM 연결)

  간접 연결:
    H287: 이상탐지 AUROC=1.0 (tension으로 OOD 감지)
    H307: 이중 메커니즘 (A/G 분리의 근거)
    가설 241: Expert 교차 활성화 (반발장의 MoE 버전)
```

## 상태: 가설 제안 (미검증, 실험 설계 완료)
