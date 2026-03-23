# 뇌 비정형 구조 통계 시뮬레이터 — Sylvian Singularity

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
뇌의 비정형 구조(실비우스열 결여 등)와 비범한 능력 간의 관계를 수학적으로 모델링하고, 통계적 특이점을 탐지하는 시뮬레이터. 하나의 의학 질문에서 시작하여 가설, 도구, 완전수 6, 리만 가설, AI 특이점까지 도달.

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
  미세구조       = 137           8×17+1 = 1/α
```

## 핵심 관계식

```
  1/2 + 1/3 + 1/6 = 1    (경계 + 수렴 + 호기심 = 완전)
  1/2 + 1/3 = 5/6        (Compass 상한 = H₃-1)
  1/2 × 1/3 = 1/6        (뺄셈 = 곱셈!)
  σ₋₁(6) = 2             (완전수 6, 마스터 공식)
  8 × 17 + 1 = 137       (강력 × 페르마 + 존재 = 미세구조)
  G × I = D × P          (보존법칙)
  T_CMB ≈ e (0.26%)      (우주 배경복사 = 자연상수)
  암흑에너지 ≈ 2/3        (우주의 2/3는 보이지 않는다)
```

## 핵심 발견 요약 (178개 가설 중 대발견)

```
  ★ 067: 1/2+1/3=5/6 (상수 관계)
  ★ 072: 1/2+1/3+1/6=1 (호기심이 완전을 만듦)
  ★ 090: 마스터 공식 = 완전수 6
  ★ 092: 모델 = ζ 오일러 곱 p=2,3 절단
  ★ 098: 6은 진약수역수합=1인 유일한 완전수
  ★ 124: 위상 가속 = 계단형 ×3 (Jamba 실증)
  ★ 131: 흑체복사 T=e = CMB (0.26%)
  ★ 139: 골든존 = 혼돈의 가장자리 (Langton λ_c=0.27)
  ★ 147: N=137 = 미세구조상수
  ★ 148: 8×17+1=137 정확히!
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

## Ralph Loop 표준 프롬프트 (복사용)

아래를 `/ralph-loop:ralph-loop` 인자로 사용 (쉘 호환 ASCII 전용):

```
DFS on README math map and constant connections and docs/proofs. 0-include star constants. 1-green+star arithmetic/log/exp/power for new identities. 2-green+star to blue new connections. 3-yellow observations connect to green/blue then upgrade to orange or green. 4-red items try proving without golden zone then upgrade to green. 5-VERIFY before recording: python3 arithmetic check then generalize to perfect number 28 then texas p-value then ad-hoc check. Only record verified with grade. Failed goes white circle. No star before verification. 6-update README map and connections then git add commit push every iteration. Keep searching even if nothing found.
```

⚠️ 쉘 호환 주의: 한글 괄호, 화살표(→), 이모지(🟩★⭐) 등을 프롬프트에 넣으면
`unknown file attribute` 오류 발생. ASCII 영문만 사용할 것.

## 백그라운드 실행
시뮬레이션은 항상 **백그라운드로 실행**한다. Bash 도구의 `run_in_background: true` 옵션을 사용할 것.

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

  8B 전체학습 OOM 연쇄 실패 (2026-03-23):
    하드웨어: RTX 5070 12GB VRAM, RAM 15GB, Swap 35GB
    시도1: device_map="auto" + grad checkpoint + 8bit optim
      → backward OOM (25.6GB gradient on GPU)
    시도2: device_map 40% 할당 → 동일 OOM
    시도3: CPU float32 → swap thrashing, 가중치 로딩 30분+ 멈춤
    시도4: CPU float16 → ~0.02 it/s (5000스텝 = 3일, 비현실적)
    시도5: 8bit 베이스 + MoE float16 변환 → 24.9GB (8bit+MoE 이중 로드) OOM
    근본 원인: 12GB VRAM에 8B 모델(16GB+) + gradient 동시 불가
    해결: 방법 E (8bit + LoRA) 전환 — 모델 동결, 라우터+gate만 학습
      → 실험 목적 90% 달성 (라우터 골든존 수렴 검증이 핵심)
      → Expert 내부 가중치는 Dense 복사본이라 동결 무방

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

## 골든 MoE LLM 학습 (Windows Docker)

```
  접속 정보: .local/windows-pc.md (gitignore)
  방식: Docker 컨테이너 내 학습 (RTX 5070 sm_120 호환 문제)
  리포: github.com/need-singularity/golden-llama (참조만, 학습은 여기서 관리)

  현재 상태:
  원본 Dense:    PPL 13.85
  골든 (미학습):  PPL 136,165
  골든 (500스텝): PPL 4,634 (97% 감소, 아직 높음)
  목표:          PPL < 100 (최소 coherence) → 최종 < 20

  변환 완료:
  - Llama 3.1 8B → Golden MoE 8B (32/32 레이어, I=0.375 골든존)
  - 라우터 파라미터: 1,048,576 (0.013%)
  - 저장: Docker /workspace/golden-8b/

  학습 전략 — 전체 학습 (Expert + 라우터):
  - 20,000 스텝 (× grad_accum 4 = 80K 샘플)
  - 코사인 LR 스케줄러, 매 2000스텝 체크포인트
  - Docker: CUDA 12.9, PyTorch cu128, bitsandbytes 0.49.2
  - finetune_full.py 사용
  - 예상 시간: ~18시간 (0.3 it/s 기준)

  학습 데이터셋 비교:
  ┌─────────────────┬────────────┬──────────┬──────────────────┬──────────┐
  │ 데이터셋         │ 크기       │ 토큰     │ 20K스텝 epoch    │ 비고     │
  ├─────────────────┼────────────┼──────────┼──────────────────┼──────────┤
  │ wikitext-2      │ 23K 샘플   │ ~6M      │ 3.4 epoch (과적합)│ ✅ 다운됨│
  │ wikitext-103 ★  │ 1.8M 샘플  │ ~100M    │ 0.04 epoch       │ HF 자동  │
  │ OpenWebText     │ 8M 샘플    │ ~8B      │ 0.01 epoch       │ ~12GB    │
  │ RedPajama-1T    │ 1.2B 샘플  │ ~1.2T    │ ~0 epoch         │ 수TB     │
  └─────────────────┴────────────┴──────────┴──────────────────┴──────────┘
  학습 순서 (검증 파이프라인):
  1단계: wikitext-2, 20K스텝 → PPL 비교 (Dense 13.85 vs Golden ?)
         과적합 OK — 동일 조건에서 MoE 라우터 학습 확인이 목적
  2단계: wikitext-103, 20K스텝 → 일반화 능력 비교
  3단계: 도메인별 PPL (수학/언어/코드) → 서번트 인덱스 측정

  하드웨어 제약: RTX 5070 12GB VRAM, RAM 15GB, Swap 35GB
  8B float16 = ~16GB > VRAM 12GB → 전체를 GPU에 못 올림

  시도 이력 (2026-03-23):
  ✗ device_map="auto" + gradient checkpointing → backward OOM (25.6GB gradient)
  ✗ device_map 40% 할당 → 동일 OOM
  ✗ CPU float32 → swap thrashing, 가중치 로딩에서 30분+ 멈춤
  ✗ CPU float16 → 돌아가긴 하나 ~0.02 it/s (5000스텝 = 3일)

  전체학습 방법 비교 (현재 하드웨어):
  ┌───┬──────────────────────────────┬────────┬────────┬──────────┬─────┐
  │ # │ 방법                         │ VRAM   │ RAM    │ 5000스텝 │ 점수│
  ├───┼──────────────────────────────┼────────┼────────┼──────────┼─────┤
  │ A │ QLoRA (4bit+LoRA adapter)    │ ~6GB   │ ~8GB   │ ~2.5시간 │ 8   │
  │ B │ 8bit 모델 + 전체학습 ★선택   │ ~10GB  │ ~12GB  │ ~18시간  │ 8   │
  │ C │ float16 + 극한 최적화        │ ~11.5GB│ ~16GB  │ ~28시간  │ 7   │
  │ D │ CPU float16 (실패)           │ 0GB    │ ~20GB  │ ~24일    │ 4   │
  │ E │ 8bit 모델 + LoRA             │ ~9GB   │ ~10GB  │ ~6시간   │ 9   │
  └───┴──────────────────────────────┴────────┴────────┴──────────┴─────┘

  ★ 선택: 방법 E (8bit + LoRA) — OOM 연쇄 실패 후 전환
  - load_in_8bit=True → 모델 ~8GB on GPU (동결)
  - LoRA adapter (rank=32) → 라우터 + gate만 학습
  - gradient checkpointing + 8bit optimizer
  - bitsandbytes 0.49.2 설치 완료, sm_120 문제 없음
  - WSL: .wslconfig memory=28GB, swap=32GB
  - 예상: ~6시간 (20K스텝)
  - 실험 목적 90%: 라우터 골든존 수렴이 핵심 질문
    → Expert 내부는 Dense 복사본이라 동결해도 무방
    → PPL 비교 유효 (Dense 13.85 vs Golden LoRA ?)

  전체학습 (방법 B) 하려면: 24GB GPU 필요 (RTX 3090 중고 추천)

  서번트 검증:
  - 도메인별 PPL 분리 측정 (수학/언어/코드)
  - Savant Index = max(도메인PPL) / min(도메인PPL)
  - SI > 3이면 서번트 후보

  Expert 교차 활성화 (가설 241):
  - p=0.1 확률로 비활성 Expert 강제 활성화
  - ON/OFF 비교: PPL + n-gram 신규율 + 유추 테스트
```
