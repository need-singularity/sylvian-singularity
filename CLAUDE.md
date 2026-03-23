# 뇌 비정형 구조 통계 시뮬레이터 — Sylvian Singularity

## ⚠️ 검증 상태 주의사항

```
  골든존(G=D×P/I) 자체가 시뮬레이션 기반이며 해석적 증명이 없다.
  골든존 위에 쌓은 모든 해석/매핑/가설은 미검증 상태이다.

  순수 수학 (골든존 무관, 영원히 참):  🟩 13개 + ⭐ 대발견 2개 — 산술/정수론/해석학
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

## 도구 목록 (26개)

```
  핵심:          brain_singularity.py, compass.py, timeline.py
  골든MoE:       golden_moe.py, golden_moe_torch.py, golden_moe_cifar.py
  분석:          formula_engine.py, texas_sharpshooter.py, complex_compass.py
                 nstate_calculator.py, brain_analyzer.py, llm_expert_analyzer.py
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
```

## 백그라운드 실행
시뮬레이션은 항상 **백그라운드로 실행**한다. Bash 도구의 `run_in_background: true` 옵션을 사용할 것.

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
  - 5000 스텝, wikitext-2 전체 (23K 샘플)
  - 코사인 LR 스케줄러, 매 500스텝 체크포인트
  - Docker: CUDA 12.8, PyTorch cu128
  - finetune_full.py 사용

  GPU 활용 방법 (8B float16 = ~16GB > VRAM 12GB):

  방법 A: device_map="auto" (CPU+GPU 분산)
  - accelerate가 자동으로 레이어별 GPU/CPU 분배
  - 구현: model 로드 시 device_map="auto"
  - 장점: 간단, 안정적
  - 단점: CPU↔GPU 전송 오버헤드
  - 속도: CPU only 대비 ~3-5배

  방법 B: gradient checkpointing + 8bit optimizer
  - gradient checkpointing: forward 2번으로 activation 메모리 절약
  - 8bit optimizer: bitsandbytes AdamW8bit로 optimizer 메모리 절반
  - 장점: 더 많은 레이어를 GPU에, 속도 ~5-10배
  - 단점: bitsandbytes sm_120(Blackwell) 미지원 위험
  - 구현: model.gradient_checkpointing_enable() + bnb.optim.AdamW8bit

  추천: 방법 A 먼저 시도, 안 되면 B

  서번트 검증:
  - 도메인별 PPL 분리 측정 (수학/언어/코드)
  - Savant Index = max(도메인PPL) / min(도메인PPL)
  - SI > 3이면 서번트 후보

  Expert 교차 활성화 (가설 241):
  - p=0.1 확률로 비활성 Expert 강제 활성화
  - ON/OFF 비교: PPL + n-gram 신규율 + 유추 테스트
```
