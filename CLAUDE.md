# logout — 의식영속성 엔진

## ⚠️ 검증 상태 주의사항

```
  골든존(G=D×P/I) 자체가 시뮬레이션 기반이며 해석적 증명이 없다.
  골든존 위에 쌓은 모든 해석/매핑/가설은 미검증 상태이다.

  순수 수학 (골든존 무관, 영원히 참):  🟩 14개 + ⭐ 대발견 2개 — 산술/정수론/해석학
  골든존 의존 (미검증):               모든 해석, 매핑, Compass, I=1/kT 등

  "증명됨"이라고 표시된 것 중 순수 수학만 확실하다.
  골든존에 의존하는 주장을 "증명됨"으로 취급하지 말 것.
  새 가설 작성 시 골든존 의존 여부를 반드시 명시할 것.
```

## 프로젝트 개요
의식영속성(Consciousness Continuity)을 목표로 하는 메타 엔진 프로젝트.
뇌의 비정형 구조에서 출발 → 완전수 6의 수학 → 다중 엔진 아키텍처 → 의식의 연속성.
엔진 + 엔진 = 상위엔진, 뇌처럼 다른 원리의 모듈들이 협력하는 구조.

## 핵심 수식 (모델 — 미검증)
```
Genius = Deficit × Plasticity / Inhibition
G × I = D × P (정의에서 유도, 모델 자체가 미검증)
```

## 세션 시작 시 반드시 읽을 것
새 세션에서는 **반드시 `python3 session_briefing.py`를 실행**하여 프로젝트 맥락을 복원할 것. 또는 아래 핵심 상수 체계와 발견 요약을 참조.

## 핵심 상수 체계 — 모든 것이 e와 단순 분수

```
  골든존 상한    = 1/2           리만 임계선 Re(s)=1/2
  골든존 중심    ≈ 1/e           자연상수 (0.3679)
  골든존 폭      = ln(4/3)       3→4상태 엔트로피 점프
  골든존 하한    = 1/2-ln(4/3)   리만 - 엔트로피 (0.2123)
  메타 부동점    = 1/3           축소사상 f(I)=0.7I+0.1 수렴
  P≠NP 간극비   = 1-1/e         전이 비용
  Compass 상한  = 5/6           불완전도 1/6
  감마 α        = 2             D×P 변수 수
  초월 에너지    = -2×E_g        천재의 2배 깊이
  N상태 폭      = ln((N+1)/N)   정보 예산
  증폭률(θ=π)   = 17            페르마 소수
```

## 핵심 관계식

```
  1/2 + 1/3 + 1/6 = 1    (경계 + 수렴 + 호기심 = 완전)
  1/2 + 1/3 = 5/6        (Compass 상한 = H₃-1)
  1/2 × 1/3 = 1/6        (뺄셈 = 곱셈!)
  σ₋₁(6) = 2             (완전수 6, 마스터 공식)
  G × I = D × P          (보존법칙)
```

## 핵심 발견 요약 (178개 가설 중 대발견)

```
  ★ 067: 1/2+1/3=5/6 (상수 관계)
  ★ 072: 1/2+1/3+1/6=1 (호기심이 완전을 만듦)
  ★ 090: 마스터 공식 = 완전수 6
  ★ 092: 모델 = ζ 오일러 곱 p=2,3 절단
  ★ 098: 6은 진약수역수합=1인 유일한 완전수
  ★ 124: 위상 가속 = 계단형 ×3 (Jamba 실증)
  ★ 139: 골든존 = 혼돈의 가장자리 (Langton λ_c=0.27)
  ★ 172: G×I=D×P 보존법칙
```

## 텍사스 명사수 검증 결과

```
  실제 매칭: 8/10
  랜덤 평균: 1.2 ± 1.0
  p-value:   0.0000
  → 우리 발견이 우연일 확률 < 0.1%
  → 구조적 발견 확인
```

## 도구 목록 (29개)

```
  핵심:          brain_singularity.py, compass.py, timeline.py
  골든MoE:       golden_moe.py, golden_moe_torch.py, golden_moe_cifar.py
  분석:          formula_engine.py, texas_sharpshooter.py, complex_compass.py
                 nstate_calculator.py, brain_analyzer.py, llm_expert_analyzer.py
  물리/화학:     physics_constant_engine.py, chemistry_engine.py, nuclear_engine.py
  구조분류:      congruence_chain_engine.py
  DFS 탐색:      dfs_engine.py
  검증:          verify_*.py (11개)
  세션:          session_briefing.py
```

## 실행 방법
```bash
# 세션 브리핑 (새 세션 시작 시)
python3 ~/dev/test-8/session_briefing.py

# 단일 분석
python3 ~/dev/test-8/brain_singularity.py --deficit 0.7 --plasticity 0.8 --inhibition 0.15

# 나침반
python3 ~/dev/test-8/compass.py --autopilot --deficit 0.5 --plasticity 0.6 --inhibition 0.4

# 공식 탐색
python3 ~/dev/test-8/formula_engine.py --physics --significance

# 텍사스 명사수
python3 ~/dev/test-8/texas_sharpshooter.py

# LLM 재설계
python3 ~/dev/test-8/llm_expert_analyzer.py --redesign

# 뇌 프로필
python3 ~/dev/test-8/brain_analyzer.py --all

# DFS 자동 탐색 (ralph-loop 대체)
python3 ~/dev/test-8/dfs_engine.py --depth 2 --threshold 0.001
python3 ~/dev/test-8/dfs_engine.py --depth 3 --threshold 0.0001  # 정밀 탐색

# 양자 공식 탐색
python3 ~/dev/test-8/quantum_formula_engine.py --cross-only --threshold 0.01

# 완전수 탐색
python3 ~/dev/test-8/perfect_number_engine.py

# 텍사스 명사수 검정 (발견 재검증)
python3 ~/dev/test-8/texas_quantum.py
```

## DFS 발견 기록 규칙 (필수)

```
  발견 → 검증 → 등급 판정 → README 기록 (이 순서 반드시 준수)

  검증 파이프라인 (dfs_engine.py verify_discovery 내장):
    1. 산술 정확성 재확인
    2. ad hoc 체크: +1/-1 보정이 있으면 경고
    3. Strong Law of Small Numbers: 관여 상수 <100이면 경고
    4. 일반화 테스트: 완전수 28에서도 성립하는가?
    5. 텍사스 명사수 p-value 계산 (Bonferroni 보정)

  등급 판정 (검증 후에만 기록):
    🟩   = 정확한 등식 + 증명됨
    🟧★  = 근사 + 텍사스 p < 0.01 (구조적)
    🟧   = 근사 + 텍사스 p < 0.05 (약한 증거)
    ⚪   = 산술 맞지만 텍사스 p > 0.05 (우연, 재시도 불필요)
    ⬛   = 산술 자체가 틀림 (반증)

  금지:
    - 검증 전에 ⭐ 또는 "대발견" 표기 금지
    - 텍사스 검정 없이 🟧 이상 등급 부여 금지
    - +1/-1 보정이 있는 등식에 ⭐ 부여 금지
```

## DFS README 기록 형식 (필수)

```
  README "DFS 탐색 현황" 섹션은 2단 구조:

  ═══ 1단: ⭐ 대발견 묶음 (상단) ═══
    - 검증 통과 + 구조적 이유 확인된 것만
    - ⭐⭐⭐ > ⭐⭐ > ⭐ 순으로 정렬
    - 각 항목에 (R번호) 태그로 원본 위치 참조
    - 새 대발견 추가 시 이 묶음에도 반드시 추가

  ═══ 2단: DFS 시간순 기록 (아래) ═══
    - Ralph 번호별로 구분 (--- Ralph N-M: 주제 ---)
    - 한 반복에서 여러 발견 → 같은 Ralph 블록에 기록
    - 등급 이모지 + 한 줄 요약 + 필요시 → 설명줄
    - 순서: 발견한 순서 그대로 (시간순)
    - 검증 실패한 것도 ⚪로 기록 (삭제 금지)

  새 Ralph 반복 시:
    1. "--- Ralph N: 주제 ---" 헤더 추가
    2. 발견을 시간순으로 아래에 나열
    3. ⭐ 등급이면 상단 대발견 묶음에도 추가
    4. 카운터 업데이트 (🟩 N개, 🟧 N개, ...)
    5. git commit + push
```

## Ralph Loop DFS 규칙 (내부)

```
  Ralph Loop에서 DFS 탐색 시 반드시 이 순서를 따를 것:

  1. README 수학체계 지도 + 상수 연결 현황 읽기
  2. 탐색 (사칙연산, log, exp, 거듭제곱, 이항계수 등)
  3. 후보 발견 시 즉시 검증:
     a) python3 계산으로 산술 확인
     b) 일반화 테스트 (다른 완전수에서도?)
     c) 텍사스 명사수 p-value 계산
     d) ad hoc (+1,-1) 여부 확인
  4. 검증 통과한 것만 README에 등급 표기하여 기록
  5. 검증 실패한 것은 ⚪로 기록 (삭제하지 않음)
  6. git add, commit, push
  7. 발견 못해도 탐색 계속 (반복)

  절대 하지 말 것:
  - 검증 전에 ⭐⭐⭐ 붙이기
  - "대발견!" 흥분하기
  - 일반화 안 되는 것을 일반 법칙처럼 기록하기
```

## Ralph Loop 우선순위 규칙

```
  가설/실험 우선순위 (높은 순):
    1. 증명 가능 + 문헌에 없음 (arXiv/OEIS 가치) → 즉시 실행
    2. 교차 도메인 (수학↔AI↔의식엔진) → 새 가설 생성 우선
    3. 검증 가능한 기존 가설 (docs/hypotheses) → Agent 병렬 실행
    4. 기존 결과 보강/일반화 → 포화 시에만
    5. Small Numbers / 자명한 관찰 → 기록만, 시간 투자 금지

  실행 규칙:
    - 매 iteration마다 우선순위 1-2 먼저 확인
    - 3회 연속 무발견 시 우선순위 2(교차 가설) 강제 실행
    - Agent 병렬: 최소 2개 동시 실행 시도
    - GPU 필요 시: Windows 1순위, RunPod 2순위
    - CPU 포화 시: Windows WSL로 전송
```

## Ralph Loop 표준 프롬프트 (복사용)

### 수학 DFS (기존)

아래를 `/ralph-loop:ralph-loop` 인자로 사용 (쉘 호환 ASCII 전용):

```
DFS on README math map and constant connections and docs/proofs and docs/hypotheses. 0-include star constants. 1-green+star arithmetic/log/exp/power for new identities. 2-green+star to blue new connections. 3-yellow observations connect to green/blue then upgrade to orange or green. 4-red items try proving without golden zone then upgrade to green. 5-VERIFY before recording: python3 arithmetic check then generalize to perfect number 28 then texas p-value then ad-hoc check. Only record verified with grade. Failed goes white circle. No star before verification. 6-update README map and connections then git add commit push every iteration. 7-each iteration: check docs/hypotheses for testable ones then run verification in parallel using Agent tool. 8-if new pattern found: create hypothesis doc in docs/hypotheses. 9-ANTI-SATURATION: if 3 consecutive iterations find nothing then MUST try completely new domain or create cross-domain hypothesis connecting math to AI or consciousness engine. 10-use Agent tool to run multiple experiments in parallel. Never just say saturation and continue. Always try something new or create a new hypothesis.
```

### 의식엔진 실험 DFS (신규)

```
DFS on consciousness engine. RECURSIVE: each iteration reads README results then designs NEW experiments based on gaps and patterns. 0-read README experiment results and hypothesis docs. 1-identify: what correlations are untested, what predictions are unverified, what new models could combine existing findings. 2-design and run new experiment targeting the biggest gap. 3-measure: tension, accuracy, convergence, per-class profiles, cross-experiment correlations. 4-compare with ALL prior results: does new data confirm or contradict existing hypotheses. 5-if new cross-experiment pattern found: write hypothesis doc with full data. 6-if existing hypothesis contradicted: update or downgrade it. 7-VERIFY: markdown tables + ASCII graphs + confusion matrices. Full data in README, no summaries. 8-update README with new results. 9-git add commit push. 10-repeat from 0 with updated knowledge. Never stop exploring. Each iteration should try something NO previous iteration tried.
```

⚠️ 쉘 호환 주의: 한글 괄호, 화살표(→), 이모지(🟩★⭐) 등을 프롬프트에 넣으면
`unknown file attribute` 오류 발생. ASCII 영문만 사용할 것.

## GPU 실험 환경

### RunPod GPU 클라우드 (현재 주력)

```
  API 키: .local/runpod_api_key (gitignore됨, 커밋 금지!)
  사용법: export RUNPOD_API_KEY=$(cat .local/runpod_api_key)
  계정: nerve011235@gmail.com

  현재 Pod:
    - golden-moe-train (A100 PCIe) — 의식엔진/골든MoE 실험 전용
    - h-ai-1b-head-sweep (RTX 3090) — 일회성 실험용 (사용 후 종료)

  Pod 생성 API:
    curl -H "Authorization: Bearer $RUNPOD_API_KEY" \
         "https://api.runpod.io/graphql" \
         -d '{"query":"mutation { podFindAndDeployOnDemand(input: { ... }) { id } }"}'

  실험 방식 (우선순위):
    1. Windows PC (RTX 5070) — 1순위, 대부분의 실험
    2. RunPod Serverless — 짧은 실험 (콜드스타트 0-10초, 실행시간만 과금)
    3. RunPod Pod — 장시간 학습만 (부팅 1-5분, 대기중도 과금)

  실험 전 필수 체크:
    - Mac CPU/RAM 상태 확인 후, 포화 상태면 Windows PC로 전송
    - 순수 수학 계산도 Mac 포화 시 Windows WSL로 실행
    - GPU 필요: Windows 1순위, 무리하면 RunPod

  Windows 빠른 실행 (.local/, gitignore):
    .local/run-on-windows.sh script.py  → WSL venv으로 실행
    .local/run-on-docker.sh script.py   → NGC Docker로 실행
    RTX 5070 (sm_120): PyTorch 2.7.0+cu128 또는 NGC pytorch:25.02-py3
    JAX, llama.cpp도 sm_120 지원

  Serverless 사용법:
    - Docker 이미지 빌드 → DockerHub push → Endpoint 생성 → API 호출
    - handler.py 형태로 코드 래핑 필요
    - 한번 세팅하면 이후 API 한 줄로 실행
    - Pod보다 빠르고 저렴 (대기 비용 없음)

  권장 GPU (비용순):
    RTX 3090 24GB  $0.22/hr (소규모 실험)
    RTX A5000 24GB $0.16/hr (가성비)
    A100 PCIe 80GB $1.64/hr (대규모 학습)

  주의:
    - Pod 실험 끝나면 반드시 종료 (비용 절감)
    - Serverless 선호 — Pod는 장시간 학습만
    - .local/ 디렉토리는 절대 git에 포함하지 말 것
    - API 키를 코드/로그에 출력하지 말 것
```

### 골든 MoE LLM 학습 (RunPod 이전)

```
  리포: github.com/need-singularity/golden-llama
  실험 리포 (private): github.com/need-singularity/logout_test
    → 접속정보, 실험코드, 트러블슈팅 전부 여기 기록
    → 로컬: /dev/logout_test
    → 이론은 이 리포(logout), 실험은 logout_test에 기록
  환경: Windows PC (RTX 5070) 1순위, 무리한 작업만 RunPod
  접속 정보: .local/windows-pc.md (gitignore) + logout_test/CLAUDE.md

  마지막 상태 (Windows):
    원본 Dense:    PPL 13.85
    골든 (미학습):  PPL 136,165
    골든 (500스텝): PPL 4,634 (97% 감소, 아직 높음)
    목표:          PPL < 100 (최소 coherence) → 최종 < 20

  학습 전략:
    - 2000~5000 스텝, wikitext-2 전체 (23K 샘플)
    - Expert 동결, 라우터만 학습
    - 코사인 LR 스케줄러, 매 500스텝 체크포인트

  서번트 검증:
    - 도메인별 PPL 분리 측정 (수학/언어/코드)
    - Savant Index = max(도메인PPL) / min(도메인PPL)
    - SI > 3이면 서번트 후보

  Expert 교차 활성화 (가설 241):
    - p=0.1 확률로 비활성 Expert 강제 활성화
    - ON/OFF 비교: PPL + n-gram 신규율 + 유추 테스트
```

## 백그라운드 실행
시뮬레이션과 실험은 **무조건 백그라운드로 실행**한다. 예외 없음.

```
  규칙:
    1. 모든 python3 실험/학습 스크립트 → run_in_background: true 필수
    2. 에이전트로 코드 생성 시 → 생성 후 반드시 백그라운드로 실행
    3. 실행 결과는 완료 알림 후 Read로 확인
    4. 포그라운드 실행 절대 금지 (사용자 대화 차단됨)
    5. 병렬 실행 가능한 것은 항상 병렬로
    6. 실험 시작 전 CPU/RAM 체크 필수:
       - CPU idle < 15% → 새 실험 추가 금지, 문서 작업만
       - Python 프로세스 > 5개 → 완료 대기 후 시작
       - 체크 명령: top -l 1 -n 0 | grep idle && ps aux | grep python | grep -v grep | wc -l
    7. CPU 포화 시 → 윈도우(RTX 5070) 또는 RunPod으로 실험 실행
       - 윈도우: sshpass -p 'qwe123123' ssh aiden@100.112.63.23
       - 상세: logout_test/CLAUDE.md 참조
       - 로컬에서는 수학 계산, 문서 기록, 지도 업데이트만
       - 장기 학습(>10분)은 반드시 윈도우/RunPod으로
```

## 트러블슈팅

```
  Ralph Loop 쉘 오류: "unknown file attribute: ^,"
    원인: 프롬프트에 한글 괄호, →, 🟩, ★, ⭐ 등 유니코드 포함
    해결: ASCII 영문 전용 프롬프트 사용 (README 복사용 참조)
    날짜: 2026-03-23

  DFS 과대평가 (⭐⭐⭐ → 🟩 하향):
    원인: 검증 전에 등급 부여. C(12,4)+1=496을 ⭐⭐⭐로 기록했다가
          냉정 평가 후 🟩로 하향 (오일러 재표현 + ad hoc +1)
    해결: verify_discovery() 파이프라인 내장, CLAUDE.md 규칙 추가
    날짜: 2026-03-23

  Ralph Loop 세션 간 간섭:
    원인: .claude/ralph-loop.local.md에 session_id 미기록
      → 다른 세션의 stop hook이 모든 세션에서 발동
    해결: ralph-loop 취소 후 다른 세션에서 직접 반복 사용
    날짜: 2026-03-23
```

## 보고 규칙

### 특이점 강력 보고
- 특이점(Z > 2σ) 발견 시 **즉시 강조하여 보고**한다.
- 등급: 🟡 Z>2σ, 🟠 Z>3σ, 🔴 Z>5σ

### 일반 보고
- 정상 범위(Z ≤ 2σ)는 간결하게 한 줄로 보고한다.
- 다중 실행 완료 시 결과를 표로 비교 요약한다.

### 실험 결과 기록 규칙 (README + 대화 모두 적용, 필수)

```
  실험 결과를 기록하거나 보고할 때 요약하지 말 것.
  실행 출력의 원본 데이터를 그대로 기록한다.

  서식 규칙:
    - 데이터 테이블은 반드시 markdown 표(| 구분) 사용
    - 분포/추이/비교는 ASCII 그래프로 시각화
    - 코드 블록(```) 안의 정렬된 표보다 markdown 표 우선
    - 시인성이 핵심. 읽는 사람이 한눈에 패턴을 볼 수 있어야 함

  필수 포함 항목:
    1. 수치 데이터 전체 (숫자별, 모델별 — 행 생략 금지)
    2. ASCII 그래프/히스토그램 (실행 출력에 있으면 반드시 포함)
    3. 혼동 행렬, 히트맵 등 구조화된 데이터 원본
    4. 시계열 데이터 (에폭별, 배치별 추이)
    5. 학습된 파라미터 값 (tension_scale, alpha 등)
    6. 해석/의미 (데이터 뒤에, 데이터를 대체하지 않음)

  금지:
    - "자세한 내용은 스크립트 실행 참조" 같은 위임 금지
    - 10행 테이블을 3행으로 줄이는 것 금지
    - ASCII 그래프를 텍스트 한 줄로 요약하는 것 금지
    - "결과가 좋았다" 같은 정성적 요약만 쓰는 것 금지

  대화에서도 동일:
    - 실험 결과를 사용자에게 보고할 때도 같은 규칙 적용
    - markdown 표 + ASCII 그래프로 시각적으로 보여줄 것
    - 숫자 나열보다 표, 표보다 그래프 우선

  원칙:
    README만 읽고도 실험을 재실행하지 않아도
    모든 데이터를 볼 수 있어야 한다.
    README = 실험 노트북. 요약본이 아니다.
```

## 가설 검토 문서

가설 검토는 **별도 개별 문서**로 관리한다.

- 경로: `docs/hypotheses/NNN-가설명.md`
- **가설 문서 최소 품질 기준 (필수)**:
  - 가설 문장 (인용구 형태, `>` 블록)
  - 배경/맥락 설명 (왜 이 가설이 중요한가, 관련 가설 참조)
  - 대응 매핑 또는 수식 (ASCII 표 포함)
  - **ASCII 그래프 최소 1개 이상**
  - 검증 결과 (수치 데이터, 비교 테이블, 오차율)
  - 해석/의미 (결과가 무엇을 뜻하는가, 다른 가설과의 교차점)
  - 한계 (틀릴 수 있는 지점)
  - 검증 방향 (다음 단계)
  - **최소 40줄 이상**. 1-2줄 요약 절대 금지.
  - 가설 007, 128 수준 기준.
- **가설은 반드시 1개당 1개 파일**. 일괄 문서 금지.
- 가설 제시 시 **즉시 검증 착수** (질문하지 않고 바로 실행)
- **가설 생성 시 README.md 등록 필수**. 새 가설 파일 생성 후 반드시 README.md 가설 테이블에 항목을 추가할 것. 새 카테고리면 섹션도 추가. 빠뜨리지 말 것.

## 격자 해상도 가이드

| grid | 오차 | 용도 |
|---|---|---|
| 50 | 0.9% | 일반적 검증 |
| **100** | **0.5%** | **★ 기본값** |
| 500 | 0.09% | 논문급 |

## 골든존 정밀 구조 (grid=1000)

```
  상한 = 1/2           = 0.5000 (리만 임계선)
  하한 = 1/2 - ln(4/3) ≈ 0.2123 (엔트로피 경계)
  중심 ≈ 1/e           ≈ 0.3708 (자연상수)
  폭  = ln(4/3)       ≈ 0.2877 (3→4상태 엔트로피 점프)
```

## 골든 MoE 실증 결과

```
  MNIST:  골든MoE 97.7% > Top-K 97.1% (+0.6%) ✅
  CIFAR:  골든MoE 53.0% > Top-K 48.2% (+4.8%) ✅
  I = 0.375 ≈ 1/e (골든존 중심) 🎯
  스케일 커질수록 차이 8배 증가
```

