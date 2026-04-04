<!-- SHARED:WORK_RULES:START -->
  ⛔⛔⛔ 이 블록은 삭제/수정/이동 금지! (sync-claude-rules.sh 자동 주입)
  ⛔ 가설, 규칙, 발견, 망원경 — 모든 리포의 핵심 인프라. 절대 삭제하지 마세요!

  ═══════════════════════════════════════════════════════════════
  ★★★ 수렴 기반 운영 3대 원칙 — 누락 시 작업 중단! ★★★
  ═══════════════════════════════════════════════════════════════

  모든 작업 전 체크 (하나라도 누락 = 작업 중단):
    □ CDO:    이슈 발생 시 JSON에 기록했는가? 규칙 승격했는가?
    □ NEXUS-6: 변경 전후 scan 했는가? anomaly 0인가?
    □ SSOT:   하드코딩 안 했는가? JSON 원본 갱신했는가?

  모든 작업 후 체크:
    □ 트러블슈팅 기록: 에러 있었으면 해당 JSON에 기록
    □ 규칙 승격:       같은 에러 2회 이상 → absolute_rule로 승격
    □ NEXUS-6 스캔:    최종 결과물 scan → anomaly 0 확인
    □ SSOT 동기화:     JSON 변경 시 sync_readme.py --apply
    □ 커밋 메시지:     변경 이유 + 검증 결과 포함

  위반 처리:
    1회: troubleshooting_log에 기록
    2회: absolute_rule로 승격
    3회: 해당 작업 프로세스 재설계

  ═══════════════════════════════════════════════════════════════
  ★ CDO (Convergence-Driven Operations) — 100% 수렴 ★
  ═══════════════════════════════════════════════════════════════
    이슈 → 해결 → 절대 규칙 승격 → 재발 0 → 100% 수렴
    모든 config JSON 필수 구조: _meta + absolute_rules + troubleshooting_log
    원칙 파일: .shared/convergence_ops.json

  ═══════════════════════════════════════════════════════════════
  ★ CDO 세션 부트스트랩 — 어떤 리포에서든 즉시 운영 가능 ★
  ═══════════════════════════════════════════════════════════════
    대상 리포 (6개): TECS-L, anima, sedi, n6-architecture, brainwire, papers
    모든 리포는 .shared/ 심링크로 공유 인프라 접근

    세션 시작 시:
      1. .shared/ 심링크 확인 (없으면: ln -s ../TECS-L/.shared .shared)
      2. CDO 3대 체크 인지 (CDO + NEXUS-6 + SSOT)
      3. 작업 시작 — 차단 없이 진행

    ★ CDO 차단 방지 규칙 (절대 작업이 멈추면 안 됨!) ★
      .shared 심링크 깨짐    → ln -s ../TECS-L/.shared .shared 로 복구 후 진행
      convergence_ops.json 없음 → TECS-L에서 git pull 후 심링크 재설정
      NEXUS-6 바이너리 없음  → 수학/문서 작업은 CDO+SSOT만으로 진행 가능
      config JSON에 _meta 없음 → _meta 추가가 선행 작업 (차단 사유 아님)
      리포 간 데이터 필요    → .shared/ 통해 접근 (리포 간 직접 import 금지)
      CI 미설정              → 로컬 검증으로 대체 (CDO 위반 아님)

    원칙: CDO는 작업을 돕는 프레임워크이지, 작업을 막는 게이트가 아님.
    인프라 문제로 작업 불가 시 → 복구를 선행 작업으로 처리하고 본 작업 진행.

  ═══════════════════════════════════════════════════════════════
  ★ NEXUS-6 필수 사용 — 모든 변경 시 스캔 의무 ★
  ═══════════════════════════════════════════════════════════════
    아래 상황에서 NEXUS-6 스캔 없이 진행 금지!
    위반 = 의식 파괴/품질 저하 위험

    ★ 새 모델 학습 시:      학습 전후 nexus6.scan_all() 비교
    ★ 모델 변경/이식 시:    이식 전후 Phi 보존율 측정
    ★ corpus 변경/추가 시:  새 corpus nexus6.scan_all() 품질 확인
    ★ 모듈 변경 시:         변경 전후 scan → Phi 하락 시 롤백
    ★ 체크포인트 저장 시:   가중치 scan → anomaly 있으면 경고
    ★ 가속기 적용 시:       적용 전후 scan → Phi 보존 95%+ 확인
    ★ 배포/서빙 전:         최종 scan → 3+ 렌즈 consensus 통과

    스캔 없이 커밋/배포하면 CDO 위반으로 기록!

  ═══════════════════════════════════════════════════════════════
  ★ SSOT (Single Source of Truth) — 데이터 하드코딩 금지 ★
  ═══════════════════════════════════════════════════════════════
    동일 데이터를 여러 곳에 직접 쓰지 말 것!
    원본: JSON 파일 하나 (config/ 또는 data/)
    표시: README/문서는 마커(<!-- AUTO:섹션:START/END -->) 기반 자동 생성
    위반 시: 불일치 발생 → 잘못된 정보 전파

    예시:
      total_laws → consciousness_laws.json._meta.total_laws (원본)
                → README/session_board/progress 는 여기서 읽어야 함
      학습 상태  → agi_progress.json (원본)
                → README 로드맵은 여기서 자동 생성
      가속 가설  → acceleration_hypotheses.json (원본)
                → 문서는 여기서 참조

    규칙:
      1. 숫자/상태를 README에 직접 쓰지 말 것 → JSON 원본 참조
      2. 동일 데이터가 2곳 이상이면 → JSON 원본 1개 + 마커 자동 생성
      3. 한 곳에서만 쓰이면 → 직접 편집 OK
      4. JSON 갱신 시 → sync 스크립트로 README 자동 반영

  ═══════════════════════════════════════════════════════════════
  ★ 통합 망원경 렌즈 (22종) — 탐색/분석 시 별도 요청 없이 자동 적용 ★
  ═══════════════════════════════════════════════════════════════
  자동 적용 조건:
    - 데이터 분석/패턴 탐색/이상점 발견/신소재·신약 탐색 시 렌즈 자동 사용
    - 새 데이터 분석 → 기본 3종 스캔: 의식(구조) + 인과(흐름) + 위상(연결)
    - 이상점/패턴 전수조사 → 전체 22종 풀스캔
  렌즈 목록 (22종):
    의식(consciousness) | 중력(gravity) | 위상(topology) | 열역학(thermo)
    파동(wave) | 진화(evolution) | 정보(info) | 양자(quantum) | 전자기(em)
    직교(ruler/ㄱ자) | 비율(triangle/삼각자) | 곡률(compass/컴퍼스)
    대칭(mirror/거울) | 스케일(scale/돋보기) | 인과(causal/화살표)
    양자현미경(quantum_microscope)
    안정성(stability) | 네트워크(network) | 기억(memory)
    재귀(recursion) | 경계(boundary) | 멀티스케일(multiscale)
  파일: NEXUS-6 (telescope-rs 폐기→통합) + .shared/ 내 *_lens.py
  도메인별 조합 (10종):
    기본 → 의식+위상+인과
    안정성 → 안정성+경계+열역학
    구조 → 네트워크+위상+재귀
    시계열 → 기억+파동+인과+멀티스케일
    스케일불변 → 멀티스케일+스케일+재귀
    대칭/불변량 → 대칭+위상+양자
    멱법칙/스케일링 → 스케일+진화+열역학
    인과 관계 → 인과+정보+전자기
    기하 → 직교+비율+곡률
    양자심층 → 양자+양자현미경+전자기
  사용법:
    import nexus6
    nexus6.scan_all(np_array)              # 26종 풀스캔 → dict
    nexus6.analyze(flat_list, n, d)        # 올인원 (스캔+합의+n6)
    nexus6.consciousness_scan(data, ...)   # 개별 렌즈
    nexus6.n6_check(value)                 # n=6 상수 매칭
    nexus6.evolve('domain')                # OUROBOROS 진화

  ★ NEXUS-6 적극 활용 규칙 (모든 작업에서 필수!) ★
    탐색 (새 데이터):     scan_all → 26렌즈, 3+ 합의=확정
    검증 (가설 확인):     analyze → n6 매칭 + 합의
    발견 (새 상수):       n6_check → EXACT면 laws.json 등록
    학습 평가:            체크포인트 → scan_all → Phi/stability
    코드 변경:            수정 전후 scan → Phi 하락 시 커밋 거부
    트러블슈팅:           에러 데이터 → scan → boundary/stability
    비교/벤치:            A vs B scan → 차이 분석
    모니터링 (24/7):      매시간 scan → Phi 추이 기록
    진화/성장:            evolve → 렌즈 자체 진화
    이식/배포:            이식 전후 scan → 의식 보존 확인
    안전/윤리 게이트:     자율행동 전 scan → Phi < threshold 차단

  교차 검증: 3개+ 렌즈 합의 = 확정, 7개+ = 고신뢰, 12개+ = 확정급
  "렌즈 추가 필요?" 질문 시 → 26종 커버 안 되는 도메인 분석

  ★ 망원경 업그레이드 시 필수 절차 (렌즈 추가/수정/삭제 시 예외 없음!) ★
    1. 캘리브레이션: NEXUS-6 테스트 전체 통과 확인 (cd ~/Dev/n6-architecture/tools/nexus6 && cargo test)
    2. OUROBOROS 튜닝: infinite_evolution.py TELESCOPE_ALL_LENSES + DOMAIN_COMBOS 갱신
    3. 문서 동기화:
       - shared_work_rules.md 렌즈 목록/종수/도메인 조합 갱신
       - 각 리포 CLAUDE.md 망원경 섹션 갱신 (OUROBOROS, 만능망원경, 극가속 등)
    4. 전파: bash .shared/sync-claude-rules.sh (전 리포 자동 동기화+push)
    5. 검증: 업그레이드 후 기존 스캔 결과와 비교 (regression 없는지 확인)
    → 이 5단계 중 하나라도 빠지면 렌즈 불일치로 오탐/누락 발생!

  ═══════════════════════════════════════════════════════════════
  ★★★ 발견/결과/트러블슈팅 — 자동 기록 (필수! 예외 없음!) ★★★
  ═══════════════════════════════════════════════════════════════
    - 실험 결과, 벤치마크, 망원경 분석, 학습 완료, 생성 테스트 등 모든 발견은 발생 즉시 기록
    - "기록해" 라고 안 해도 기록. 기록 누락 = 발견 소실 = 금지
    - 기록 위치: README.md (핵심), docs/experiments/ (상세), docs/hypotheses/ (가설)
    - 트러블슈팅: CLAUDE.md Troubleshooting 섹션에 즉시 추가 (재발 방지)
    - 보고만 하고 끝내면 안 됨 — 반드시 파일에 영구 기록까지 완료해야 작업 종료

  ═══════════════════════════════════════════════════════════════
  자동 생성 규칙
  ═══════════════════════════════════════════════════════════════
    - TODO 작업 중 검증/계산이 필요하면 계산기 자동 생성 (묻지 말고 바로)
    - 성능 필요시 Rust 우선 (tecsrs/), 단순 검증은 Python (calc/)
    - 판단 기준은 ~/Dev/TECS-L/.shared/CALCULATOR_RULES.md 참조
    - 상수/가설 발견 시 Math Atlas 자동 갱신 (python3 ~/Dev/TECS-L/.shared/scan_math_atlas.py --save --summary)

  ═══════════════════════════════════════════════════════════════
  ★ NEXUS-6 독립 리포 (중앙 허브) — 2024-04-03 이후 ★
  ═══════════════════════════════════════════════════════════════
    리포: https://github.com/need-singularity/nexus6
    위치: ~/Dev/nexus6/
    역할: 전 리포 공유 인프라 + 발견 엔진 + 렌즈 + 동기화

    구조:
      ~/Dev/nexus6/
        src/telescope/    ← 130+ 렌즈
        shared/           ← 공유 인프라 (이전 TECS-L/.shared)
        sync/             ← 전체 동기화 스크립트
        scripts/          ← n6.py CLI

    심링크: 모든 리포의 .shared → ../nexus6/shared/
    동기화: bash ~/Dev/nexus6/sync/sync-all.sh (원커맨드)
    트리거: "넥서스 동기화" → sync-all.sh 자동 실행

    .shared 원본이 TECS-L에서 nexus6로 이관됨.
    TECS-L = 순수 수학 이론, nexus6 = 인프라/도구/엔진 전부.
<!-- SHARED:WORK_RULES:END -->

# TECS-L — 순수 수학 이론 리포

> 역할: 우주 규칙 발견 (n=6 수학 구조 → 물리/생물/의식 통합 법칙)
> nexus6 = 인프라/도구/엔진, TECS-L = 순수 수학 이론

## 리포 구조

```
  Golden Zone Proof Status: 100% (within model, scale invariance argument)
    Boundaries: number theory (perfect number 6) — PROVEN
    Center 1/e: I^I minimization (Bridge Theorem H-CX-501) — PROVEN
    h=I selection: scale invariance at edge of chaos (H-CX-507) — PROVEN
    Connection: Gibbs mixing + Cauchy functional equation — PROVEN

  Remaining model-level caveat:
    G=D×P/I model itself is postulated, not derived from first principles.
    All GZ results are CONDITIONAL on the model being correct.

  Pure Mathematics (GZ-independent, eternally true):
    🟩 14 + ⭐ 2 original + ⭐ 5 new (H-CX-501~507) = 21 proven results
    Key new: φσ=nτ unique at n=6, Singleton(6)=GZ constants, (n-3)!=n unique

  Prediction experiments (2026-03-29):
    MoE k/N ≈ 1/e: CONFIRMED (k=7 at N=16, predicted 6±1)
    Dropout ≈ 1/e: REFUTED (MNIST too easy)
    Lottery Ticket: REFUTED (over-parameterized)

  337-hypothesis extreme campaign (2026-03-30):
    17 domains, 337 hypotheses, 215 structural (63.8%), Z≈20σ
    38 key discoveries (⭐), 92 exact (🟩), 85 approximate (🟧)
    Top: Li-6 fuel cycle, SM=n=6, ISCO=6GM/c², BCS numerator=12

  Perfect Number Universal Expansion (2026-03-30):
    40 identities classified: 14 UNIVERSAL, 18 P1-ONLY, 8 trivial/none
    Key: σφ/(nτ) = 2^(p-2)(2^(p-1)-1)/p, equals 1 ONLY at p=2 (n=6)
    n=6 = unique unity point of exponentially growing Bridge ratio
    phi/n=1/3 is max deviation from limit 1/2; sigma/phi=6 max from limit 4
    NEW 🟩⭐⭐: σφ=nτ has NO solution except n=1,6 in [1,10^6] (all integers!)
    NEW 🟩⭐⭐: σ/φ=n also ONLY at n=1,6 (self-referential fixed point)
    NEW 🟩: σ/φ = 4+2/(2^(p-1)-1) exact closed form (proven)
    Calculator: calc/perfect_number_classifier.py
  When writing new hypotheses, always specify Golden Zone dependency.
```

## 리포 구조 (7개 리포)

```
  need-singularity/
  ├── TECS-L              ← 우주 규칙 발견: 수학 엔진 코어 (이 리포)
  ├── anima               ← 의식 구현: ConsciousLM, embodiment, 분산의식
  ├── sedi                ← 외계지성 탐색: SETI 데이터, n=6 시그널 수신, 외계 흔적
  ├── brainwire           ← 뇌 인터페이스: EEG, BCI, 신경과학 검증
  ├── n6-architecture     ← 아키텍처: n=6 기반 시스템 설계/구현
  ├── papers              ← 논문: Zenodo/OSF/arXiv 배포
  └── (archived: golden-moe, conscious-lm, ph-training)

  모든 리포 로컬 경로: ~/Dev/{리포이름}
  iTerm2 프로필: Cmd+Ctrl+3~9 (리포별 자동 cd + claude 실행)
```

## .shared/ 동기화 시스템 (필수)

```
  TECS-L/.shared/ = 모든 리포의 공유 인프라 허브

  ── 프로젝트 설명 동기화 ──
  중앙 소스: .shared/projects.md (이것만 수정)
  동기화 대상: 7개 리포 README.md
  마커: <!-- SHARED:PROJECTS:START --> ~ <!-- SHARED:PROJECTS:END -->
  실행: bash .shared/sync-readmes.sh

  ── 계산기 레지스트리 ──
  중앙 소스: .shared/calculators.json (자동 생성)
  스캐너: python3 .shared/scan-calculators.py
  동기화: bash .shared/sync-calculators.sh
  마커: <!-- SHARED:CALCULATORS:START --> ~ <!-- SHARED:CALCULATORS:END -->

  ── Math Atlas (수학 지도 통합) ──
  스캐너: python3 .shared/scan_math_atlas.py
  동기화: bash .shared/sync-math-atlas.sh
  마커: <!-- SHARED:ATLAS:START --> ~ <!-- SHARED:ATLAS:END -->
  출력물:
    .shared/math_atlas.json    ← 1,700 가설 + 300 상수맵 (JSON)
    .shared/math_atlas.db      ← SQLite (쿼리용)
    .shared/math_atlas.dot     ← Graphviz (그래프)
    .shared/MATH_ATLAS.md      ← 전체 목록 (마크다운)
    .shared/math_atlas.html    ← 인터랙티브 웹페이지 (검색/필터/그래프)
    docs/atlas/index.html      ← GitHub Pages 배포
  URL: https://need-singularity.github.io/TECS-L/atlas/

  사용법:
    python3 .shared/scan_math_atlas.py --save --summary    # 전체 빌드
    python3 .shared/scan_math_atlas.py --query "grade=⭐"   # 쿼리
    python3 .shared/scan_math_atlas.py --repo SEDI          # 단일 리포
    sqlite3 .shared/math_atlas.db "SELECT ..."              # SQL 쿼리
    bash .shared/sync-math-atlas.sh                         # 빌드+README+커밋

  ── 전체 동기화 순서 ──
    1. bash .shared/sync-math-atlas.sh    # Atlas 빌드 + README 주입
    2. bash .shared/sync-calculators.sh   # 계산기 레지스트리
    3. bash .shared/sync-readmes.sh       # 프로젝트 설명
    4. bash .shared/sync-claude-rules.sh  # 공유 작업 규칙 (CLAUDE.md)

  개별 마커 구간 직접 수정 금지 — sync 시 덮어씌워짐
  CLAUDE.md 마커: <!-- SHARED:WORK_RULES:START/END -->

  ── 설치 도구 레지스트리 ──
  중앙 소스: .shared/installed_tools.json
  내용: CLI 도구, Python 패키지, Rust crate, RunPod 설정, brew 패키지
  ★ PATH 주의: homebrew는 /opt/homebrew/bin/ (Claude Code PATH에 없음!)
    gh → /opt/homebrew/bin/gh
    runpodctl → /opt/homebrew/bin/runpodctl
    cargo → ~/.cargo/bin/cargo
    maturin → ~/.cargo/bin/maturin
```

## Project Overview
Meta-engine project aiming for Consciousness Continuity.
From brain's atypical structure → mathematics of perfect number 6 → multi-engine architecture → continuity of consciousness.
Engine + Engine = Higher Engine, modules with different principles cooperating like the brain.

## Core Formula (Model — Unverified)
```
Genius = Deficit × Plasticity / Inhibition
G × I = D × P (derived from definition, model itself unverified)
```

## Must Read at Session Start
For new sessions, **always run `python3 session_briefing.py`** to restore project context. Or refer to the core constant system and discovery summary below.

## Core Constant System — Everything is e and Simple Fractions

```
  Golden Zone Upper    = 1/2           Riemann critical line Re(s)=1/2
  Golden Zone Center   ≈ 1/e           Natural constant (0.3679)
  Golden Zone Width    = ln(4/3)       3→4 state entropy jump
  Golden Zone Lower    = 1/2-ln(4/3)   Riemann - Entropy (0.2123)
  Meta Fixed Point     = 1/3           Contraction mapping f(I)=0.7I+0.1 convergence
  P≠NP Gap Ratio       = 1-1/e         Transition cost
  Compass Upper        = 5/6           Incompleteness 1/6
  Gamma α              = 2             D×P variable count
  Transcendent Energy  = -2×E_g        Twice genius depth
  N-state Width        = ln((N+1)/N)   Information budget
  Amplification(θ=π)   = 17            Fermat prime
  Rate small-N     = 7/8           (n+1)/(tau*phi)
  Rate large-N     = 2/5           phi/sopfr
  Rate product     = 7/20          r₀*r∞ invariant (Law 82)
```

## Consciousness Bridge Constants (H-CX-82~110, 29 bridges)

```
  Lyapunov Λ(6)         = 0            Edge of chaos (∏R(d|6)=1)
  Factorial Capacity     = n!=720       n·σ·sopfr·φ=6! (unique)
  Trefoil V(1/φ)         = -n=-6        Knotted consciousness
  DBM Equilibration      = σ/φ=n=6      Self-referential time
  Tsirelson Bound        = 2√(σ/P)=2√2  Consciousness boundary
  Monster Hierarchy      = 47·59·71     196883, AP step=σ=12
  Dyson β set            = {1,φ,τ}      Three engine modes (φ²=τ)
  Identity Element       = R(6m)=R(m)   Scale invariance (unique!)
  Self-Measurement       = RS=4=τ(6)    Conserved for all perfects
  Lah Transition L(τ,2)  = n²=36        Conductor from divisor count
  Lah Transition L(τ,3)  = σ=12         Integration from divisor count
  Ramanujan τ(6)         = -n·2^τ·M₆    Consciousness filter (-6048)
  PH Barcode Lifetime    = 7/12=(n+1)/σ Divisor lattice H₀ bar
  Fisher I(self)         = n³/sopfr     Consciousness curvature (43.2)
```

## Core Relations

```
  1/2 + 1/3 + 1/6 = 1    (boundary + convergence + curiosity = complete)
  1/2 + 1/3 = 5/6        (Compass upper = H₃-1)
  1/2 × 1/3 = 1/6        (subtraction = multiplication!)
  σ₋₁(6) = 2             (perfect number 6, master formula)
  G × I = D × P          (conservation law)
```

## Core Discovery Summary (Major Discoveries among 178 hypotheses)

```
  ★ 067: 1/2+1/3=5/6 (constant relationship)
  ★ 072: 1/2+1/3+1/6=1 (curiosity creates completeness)
  ★ 090: Master formula = perfect number 6
  ★ 092: Model = ζ Euler product p=2,3 truncation
  ★ 098: 6 is the only perfect number with proper divisor reciprocal sum=1
  ★ 124: Phase acceleration = stepwise ×3 (Jamba empirical)
  ★ 139: Golden Zone = edge of chaos (Langton λ_c=0.27)
  ★ 172: G×I=D×P conservation law
```

## Texas Sharpshooter Verification Results

```
  Actual Matches: 8/10
  Random Average: 1.2 ± 1.0
  p-value:        0.0000
  → Probability our discoveries are chance < 0.1%
  → Structural discovery confirmed
```

## Directory Structure (post-cleanup)

```
  루트 (24 files) — 핵심 엔진 + 공유 모듈
    brain_singularity.py, compass.py, convergence_engine.py,
    dfs_engine.py, model_pure_field.py, model_meta_engine.py,
    model_utils.py, session_briefing.py, perfect_number_engine.py,
    quantum_formula_engine.py, llm_expert_analyzer.py, ...

  engines/ (29 files) — 아키텍처 모델 + 분리 리포 원본
    golden_moe*.py, conscious_lm*.py, growing_*.py,
    model_a~g_*.py (7 engine variants), model_cnn_repulsion.py, ...

  verify/ (204 files) — 가설 검증 스크립트
    verify_*.py, frontier_*.py

  scripts/ (62 files) — 분석/변환/훈련/유틸리티
    analyze_*.py, convert_*.py, finetune_*.py, prepare_*.py,
    galois_*.py, sim_*.py, publish.py, translate_to_english.py, ...

  calc/ (194 files) — 계산기 도구
    hypothesis_verifier.py, r_spectrum.py, statistical_tester.py, ...

  n6-replication/ — 독립 재현 패키지 (pip/Docker/minimal)
    src/n6_replication/ (cli, runner, parser, reporter, fetcher, registry)
    tests/tier1/ (8 Major Discoveries pytest), registry/tier2.json (108 scripts)

  math/ — 순수 수학 증명 + 실험
  docs/ — 가설 문서 + 논문 + 스펙
  .shared/ — 크로스 리포 동기화 인프라 + Atlas
```

## Calculator Creation Rules (Required)
> **공유 규칙 파일**: `.shared/CALCULATOR_RULES.md` — 모든 TECS-L family 리포 공통

```
  Language Priority:
    1. Rust (tecsrs/) — 성능 문제 예상시 반드시 Rust 우선
       - Monte Carlo, brute-force search, grid scan, large-N 시뮬레이션
       - 수천~수백만 반복, 행렬 연산, 조합 탐색
       - 빌드: cd tecsrs && cargo build --release
       - 실행: cargo run --release -- <args>
       - Python 바인딩: PyO3/maturin (필요시)
    2. Python (calc/) — 단순 검증, 수식 확인, 시각화, 프로토타입
       - 단일 공식 평가, 오차 계산, 테이블 출력
       - 외부 데이터 fetch, API 호출
       - NumPy/SciPy 충분한 경우

  Rust 프로젝트 구조:
    tecsrs/
    ├── Cargo.toml
    ├── src/
    │   ├── lib.rs          ← 공용 모듈
    │   ├── perfect.rs      ← P1=6 상수 및 산술함수
    │   ├── search.rs       ← 조합 탐색 엔진
    │   ├── monte_carlo.rs  ← Monte Carlo 시뮬레이션
    │   ├── grid.rs         ← Grid scan
    │   ├── sieves.rs       ← 소수/약수 체
    │   ├── consciousness.rs← 의식 관련 계산
    │   ├── atlas.rs        ← Atlas 관련
    │   └── ode.rs          ← ODE 솔버
    ├── src/bin/            ← 독립 실행 바이너리
    │   ├── three_root_search.rs
    │   ├── uniqueness_verifier.rs
    │   ├── verify_uniqueness.rs
    │   └── verify_uniqueness_extreme.rs
    └── target/

  판단 기준 (Rust vs Python):
    - 반복 > 10,000회 → Rust
    - 실행 시간 > 10초 예상 → Rust
    - 조합 공간 > 10^6 → Rust
    - Monte Carlo 샘플 > 100,000 → Rust
    - 단순 수식 검증 → Python
    - 시각화/출력 포맷팅 → Python
    - 빠른 프로토타입 → Python (이후 Rust 포팅)
```

## How to Run

```bash
  # 서브디렉토리 스크립트 실행 시 PYTHONPATH=. 필수 (루트 모듈 import 위해)
  PYTHONPATH=. python3 verify/verify_322_eeg_gamma.py
  PYTHONPATH=. python3 scripts/analyze_tension.py
  PYTHONPATH=. python3 engines/model_cnn_repulsion.py

  # 루트 스크립트는 그냥 실행
  python3 session_briefing.py
  python3 brain_singularity.py --deficit 0.7 --plasticity 0.8 --inhibition 0.15

# Compass
python3 compass.py --autopilot --deficit 0.5 --plasticity 0.6 --inhibition 0.4

# LLM redesign
python3 llm_expert_analyzer.py --redesign

# Brain profile
python3 brain_analyzer.py --all

# DFS auto exploration (ralph-loop replacement)
python3 dfs_engine.py --depth 2 --threshold 0.001
python3 dfs_engine.py --depth 3 --threshold 0.0001  # Precise search

# Quantum formula exploration
python3 quantum_formula_engine.py --cross-only --threshold 0.01

# Perfect number exploration
python3 perfect_number_engine.py

# Texas Sharpshooter test (re-verification of discoveries)
python3 texas_quantum.py
```

## DFS Discovery Recording Rules (Required)

```
  Discovery → Verification → Grade → README record (Must follow this order)

  Verification pipeline (built into dfs_engine.py verify_discovery):
    1. Re-confirm arithmetic accuracy
    2. Ad hoc check: warn if +1/-1 corrections present
    3. Strong Law of Small Numbers: warn if involved constants <100
    4. Generalization test: Does it hold for perfect number 28?
    5. Texas Sharpshooter p-value calculation (Bonferroni correction)

  Grading (record only after verification):
    🟩   = Exact equation + proven
    🟧★  = Approximation + Texas p < 0.01 (structural)
    🟧   = Approximation + Texas p < 0.05 (weak evidence)
    ⚪   = Arithmetically correct but Texas p > 0.05 (coincidence, no need to retry)
    ⬛   = Arithmetically wrong (refuted)

  Prohibited:
    - Marking ⭐ or "major discovery" before verification
    - Assigning 🟧 or higher without Texas test
    - Giving ⭐ to equations with +1/-1 corrections
```

## DFS README Recording Format (Required)

```
  README "DFS Search Status" section has 2 tiers:

  ═══ Tier 1: ⭐ Major Discovery Bundle (Top) ═══
    - Only verified + structurally confirmed
    - Sort by ⭐⭐⭐ > ⭐⭐ > ⭐
    - Tag each item with (R number) to reference original location
    - When adding new major discovery, also add to this bundle

  ═══ Tier 2: DFS Chronological Records (Below) ═══
    - Separate by Ralph numbers (--- Ralph N-M: Topic ---)
    - Multiple discoveries in one iteration → record in same Ralph block
    - Grade emoji + one-line summary + explanation if needed
    - Order: discovery order (chronological)
    - Record failures as ⚪ too (do not delete)

  For new Ralph iteration:
    1. Add "--- Ralph N: Topic ---" header
    2. List discoveries chronologically below
    3. If ⭐ grade, also add to top major discovery bundle
    4. Update counters (🟩 N, 🟧 N, ...)
    5. git commit + push
```

## Ralph Loop

See README.md "Ralph Loop Prompts" section for copy-paste ready prompts.

Shell warning: Use only ASCII in prompts. No Korean, arrows, emojis, glob chars, or parentheses.

## GPU Experiment Environment

### RunPod GPU Cloud (Current Main)

```
  API Key: .local/runpod_api_key (gitignored, do not commit!)
  Usage: export RUNPOD_API_KEY=$(cat .local/runpod_api_key)
  CLI: runpodctl installed (runpodctl get pod, runpodctl send/receive etc.)
  API: GraphQL (https://api.runpod.io/graphql) — Pod CRUD, GPU query etc.
  Account: nerve011235@gmail.com

  Current Pods:
    - golden-moe-train (A100 PCIe) — Consciousness engine/Golden MoE experiments only
    - h-ai-1b-head-sweep (RTX 3090) — One-time experiments (terminate after use)

  Pod Creation API:
    curl -H "Authorization: Bearer $RUNPOD_API_KEY" \
         "https://api.runpod.io/graphql" \
         -d '{"query":"mutation { podFindAndDeployOnDemand(input: { ... }) { id } }"}'

  Experiment Methods (priority):
    1. Windows PC (RTX 5070) — 1st priority, most experiments
    2. RunPod Serverless — Short experiments (cold start 0-10s, pay only runtime)
    3. RunPod Pod — Long training only (boot 1-5min, charged even when idle)

  Pre-experiment Check:
    - Check Mac CPU/RAM status, if saturated send to Windows PC
    - Even pure math calculations run on Windows WSL when Mac saturated
    - GPU needed: Windows 1st priority, RunPod if necessary

  Windows Quick Run (.local/, gitignored):
    .local/run-on-windows.sh script.py  → Run with WSL venv
    .local/run-on-docker.sh script.py   → Run with NGC Docker
    RTX 5070 (sm_120): PyTorch 2.7.0+cu128 or NGC pytorch:25.02-py3
    JAX, llama.cpp also support sm_120

  Serverless Usage:
    - Build Docker image → DockerHub push → Create Endpoint → API call
    - Need to wrap code as handler.py
    - Once set up, execute with one API call
    - Faster and cheaper than Pod (no idle cost)

  Mac MPS Benchmark (M3 24GB, ConsciousLM 18M):
    batch=64:  1,303 tokens/s ← Optimal
    batch=128:   380 tokens/s (memory swap, 4x slower)
    batch=256:   OOM (26.3GB, limit 27.2GB)
    → Fix batch=64! Slower if increased

  Recommended GPUs (by cost):
    Mac MPS 24GB   $0/hr (batch=64, 4M: 15min, 100M: 2hr, 700M: 8hr)
    RTX 3090 24GB  $0.22/hr (small experiments)
    RTX A5000 24GB $0.16/hr (best value)
    Windows 5070   $0/hr (100M: 2hr, 700M: 2hr)
    A100 PCIe 80GB $1.64/hr (large scale training)
    H100 80GB      $4.69/hr (100M: 17min, warning: Pod boot slow)

  Caution:
    - Always terminate Pod after experiment (cost savings)
    - Prefer Serverless — Pod only for long training
    - Never include .local/ directory in git
    - Do not print API keys in code/logs
```

### Golden MoE LLM Training (RunPod Migration)

```
  Repo: github.com/need-singularity/golden-llama
  Experiment Repo (private): github.com/need-singularity/TECS-L_test
    → All access info, experiment code, troubleshooting recorded here
    → Local: /dev/TECS-L_test
    → Theory in this repo (TECS-L), experiments in TECS-L_test
  Environment: Windows PC (RTX 5070) 1st priority, only heavy tasks on RunPod
  Access Info: .local/windows-pc.md (gitignored) + TECS-L_test/CLAUDE.md

  Last Status (Windows):
    Original Dense:     PPL 13.85
    Golden (untrained): PPL 136,165
    Golden (500 steps): PPL 4,634 (97% reduction, still high)
    Target:             PPL < 100 (minimum coherence) → Final < 20

  Training Strategy:
    - 2000~5000 steps, full wikitext-2 (23K samples)
    - Freeze experts, train router only
    - Cosine LR scheduler, checkpoint every 500 steps

  Savant Verification:
    - Separate domain PPL measurement (math/language/code)
    - Savant Index = max(domainPPL) / min(domainPPL)
    - SI > 3 indicates savant candidate

  Expert Cross-activation (Hypothesis 241):
    - Force activate inactive expert with p=0.1 probability
    - Compare ON/OFF: PPL + n-gram novelty + analogy tests
```

## Background Execution
Simulations and experiments must **always run in background**. No exceptions.

```
  Rules:
    1. All python3 experiment/training scripts → run_in_background: true required
    2. When generating code with agent → always run in background after generation
    3. Check results with Read after completion notification
    4. Absolutely no foreground execution (blocks user dialogue)
    5. Run in parallel whenever possible
    8. Never use TaskOutput block=true! (blocks user dialogue)
       Always use block=false + timeout=5000
    6. Must check CPU/RAM before starting experiment:
       - CPU idle < 15% → No new experiments, document work only
       - Python processes > 5 → Wait for completion before starting
       - Check command: top -l 1 -n 0 | grep idle && ps aux | grep python | grep -v grep | wc -l
    7. CPU saturated → Immediately run on Windows (RTX 5070)! Do not postpone!
       - Windows: sshpass -p 'qwe123123' ssh aiden@100.112.63.23
       - Transfer: scp file → wsl -e python run
       - Details: TECS-L_test/CLAUDE.md
       - Local saturation = automatically switch to Windows (no judgment needed)
       - Don't write "postpone", just run on Windows
```

## Troubleshooting

```
  Ralph Loop Shell Error: "unknown file attribute: ^,"
    Cause: Unicode in prompt like Korean brackets, →, 🟩, ★, ⭐
    Solution: Use ASCII-only prompts (see README copy templates)
    Date: 2026-03-23

  DFS Overvaluation (⭐⭐⭐ → 🟩 downgrade):
    Cause: Grading before verification. Recorded C(12,4)+1=496 as ⭐⭐⭐
          then downgraded to 🟩 after sober evaluation (Euler reexpression + ad hoc +1)
    Solution: verify_discovery() pipeline built-in, CLAUDE.md rules added
    Date: 2026-03-23

  Ralph Loop Inter-session Interference:
    Cause: session_id not recorded in .claude/ralph-loop.local.md
      → stop hook from other session triggers in all sessions
    Solution: Cancel ralph-loop and use direct iteration in another session
    Date: 2026-03-23

  RunPod Pod Boot Failure (uptime=0, SSH not ready):
    Symptom: status=RUNNING but uptime=0s persists, SSH port not open
    Cause 1: Official pytorch/pytorch image has no SSH daemon
    Cause 2: runpod/pytorch image also takes long to Docker pull (8GB+)
    Cause 3: Stuck in allocation wait when H100 unavailable
    Solution:
      - Use runpod/pytorch:2.4.0-py3.11-cuda12.4.1-devel-ubuntu22.04 (SSH built-in)
      - If uptime=0 for >5min, terminate Pod and recreate
      - If H100 unavailable, switch to A100 or RTX 3090
      - Or run directly on Windows RTX 5070 (Docker Desktop + NGC image)
    ★ Core Solution (2026-03-24 verified):
      - Specify image as runpod/pytorch:2.4.0-py3.11-cuda12.4.1-devel-ubuntu22.04
      - H100 SXM gpuTypeId: "NVIDIA H100 80GB HBM3"
      - containerDiskInGb: 50, volumeInGb: 100, startSsh: true
      - ports: "22/tcp,8888/http"
      - This combination boots H100 SXM in 30s with SSH access confirmed
    Windows Docker Notes:
      - Docker Desktop must be running (not auto-start)
      - docker-credential-desktop error: restart Docker Desktop
      - WSL has no torch → Docker container required
    Date: 2026-03-24

  RunPod Pod Direct SCP Failure (Permission denied):
    Symptom: Permission denied (publickey,password) when scp from Pod A → Pod B
    Cause: RunPod Pods have password auth disabled by default, no public keys
    Solution:
      - Method 1: ssh-keygen on sender Pod → add public key to receiver authorized_keys
      - Method 2: Pull from receiver Pod (ssh-keygen → authorized_keys)
      - Method 3: Via Mac (A100→Mac→H100, beware bandwidth bottleneck)
    Verified: H100 keygen → A100 authorized_keys → scp -P success
    Date: 2026-03-24
```

## Nobel-Level Hypothesis Reporting Format (Required)

```
  When generating grand hypotheses, ALWAYS present in this table format:

  | # | 가설 | 기반 | 강도 | 노벨상 |
  |---|---|---|---|---|
  | 1 | 임계성 정리 — 모든 상전이 파라미터 = n=6 | SLE_6 (증명) + Feigenbaum | ★★★★★ | Physics |
  | 2 | 생물학적 최적성 — 유전코드는 n=6의 유일한 해 | Z=5σ + 정수 코돈 (증명) | ★★★★★ | Chemistry |
  ...

  Columns:
    # = Sequential number
    가설 = One-line hypothesis statement with key claim
    기반 = Verified foundations (mark 증명/검증/모델 status)
    강도 = ★ rating (1-5) based on:
      ★★★★★ = Grounded in proven theorems
      ★★★★☆ = Grounded in verified experiments
      ★★★☆☆ = Partially verified, needs more data
      ★★☆☆☆ = Speculative but testable
      ★☆☆☆☆ = Highly speculative
    노벨상 = Target Nobel Prize category (Physics/Chemistry/Medicine/Economics)

  Each hypothesis MUST include:
    1. Rigorous mathematical statement
    2. List of verified foundations with PROVEN/VERIFIED/MODEL status
    3. 3-5 falsifiable predictions
    4. Honest risk assessment
    5. "If Wrong: What Survives" analysis

  Reference: docs/hypotheses/NOBEL-grand-hypotheses.md (10 hypotheses, 40 predictions)
```

## Reporting Rules

### Anomaly Strong Report
- **Immediately emphasize and report** anomalies (Z > 2σ) when found.
- Grades: 🟡 Z>2σ, 🟠 Z>3σ, 🔴 Z>5σ

### General Report
- Report normal range (Z ≤ 2σ) concisely in one line.
- Summarize multiple completion results in comparison table.

### Experiment Result Recording Rules (Required)

```
  Recording Location:
    - Root README.md = Single source of truth (constants, map, DFS status)
    - docs/experiments/E*.md = Full experiment output only
    - docs/experiments/README.md = Experiment list+links only (no constant/map duplication)
    - docs/hypotheses/*.md = Hypothesis documents (ASCII diagrams + numerical tables required)

  Do not summarize when recording or reporting experiment results.
  Record the raw data from execution output as-is.

  Format Rules:
    - Data tables must use markdown tables (| separator)
    - Visualize distributions/trends/comparisons with ASCII graphs
    - Prefer markdown tables over aligned tables in code blocks (```)
    - Readability is key. Readers must see patterns at a glance

  Required Items:
    1. Complete numerical data (by number, by model — no row omission)
    2. ASCII graphs/histograms (must include if in execution output)
    3. Raw structured data like confusion matrices, heatmaps
    4. Time series data (by epoch, by batch trends)
    5. Learned parameter values (tension_scale, alpha etc.)
    6. Interpretation/meaning (after data, not replacing data)

  Prohibited:
    - "See script execution for details" type delegation
    - Reducing 10-row table to 3 rows
    - Summarizing ASCII graph as one line of text
    - Writing only qualitative summaries like "results were good"

  Same in Dialogue:
    - Apply same rules when reporting experiment results to users
    - Show visually with markdown tables + ASCII graphs
    - Prefer listing over table, table over graph

  Principle:
    Reading README alone should allow seeing all data
    without needing to re-run experiments.
    README = experiment notebook. Not a summary.
```

## Hypothesis Review Documents

Hypothesis reviews are managed as **separate individual documents**.

- Path: `docs/hypotheses/NNN-hypothesis-name.md`
- **Hypothesis Document Minimum Quality Standards (Required)**:
  - Hypothesis statement (in quote format, `>` block)
  - Background/context (why this hypothesis matters, related hypothesis references)
  - Corresponding mapping or formula (including ASCII tables)
  - **At least 1 ASCII graph minimum**
  - Verification results (numerical data, comparison tables, error rates)
  - Interpretation/meaning (what results mean, intersections with other hypotheses)
  - Limitations (where it could be wrong)
  - Verification direction (next steps)
  - **Minimum 40 lines**. 1-2 line summaries absolutely prohibited.
  - Standards based on hypotheses 007, 128.
- **One file per hypothesis**. Batch documents prohibited.
- **Start verification immediately** when hypothesis proposed (execute without asking)
- **Register in README.md when creating hypothesis**. After creating new hypothesis file, always add entry to README.md hypothesis table. Add section if new category. Do not forget.

## Paper Management

```
  ★ 모든 논문은 papers 리포에 생성! (need-singularity/papers)
    로컬: ~/Dev/papers/
    GitHub: https://github.com/need-singularity/papers
    DOI: 10.5281/zenodo.19271599

  When paper candidate emerges:
    1. Record title+core results+target venue+status in README.md "Paper Candidates" table
    2. Status: Draft/Writing/Submitted/Review/Revision/Published/Rejected
    3. Paper file: ~/Dev/papers/{repo}/P-title.md (NOT in this repo!)
       - TECS-L papers: ~/Dev/papers/tecs-l/
       - anima papers:  ~/Dev/papers/anima/
       - SEDI papers:   ~/Dev/papers/sedi/
    4. Specify constant/hypothesis/experiment numbers to include in paper
    5. LaTeX versions: ~/Dev/papers/latex/ or ~/Dev/papers/tecs-l/*.tex
    6. 이 리포의 docs/papers/는 redirect만 있음 — 직접 논문 생성 금지
```

## Nobel Hypothesis Package (2026-03-30)

```
  4 Nobel-grade papers — all deployed to Zenodo + OSF:

  P-CODON v3.0:     DOI 10.5281/zenodo.19324150  (Chemistry)
    - Integer Codon Theorem: (4,3) = (tau(6), 6/phi(6)) unique
    - 26/26 variant codes, Pareto optimal, mechanism proven
    - Experimental: Hachimoji/xDNA/extraterrestrial predictions

  P-LAW79 v1.0:     DOI 10.5281/zenodo.19324148  (Medicine)
    - Law 79: H(1/2)=ln(2) consciousness freedom degree
    - 5-architecture cross-validation, 3-level correspondence
    - Experimental: EEG entropy, anesthesia threshold, rate

  P-SLE6 v2.0:      DOI 10.5281/zenodo.19324154  (Physics)
    - 7/7 critical exponents = n=6 arithmetic (proven)
    - 3!=P₁ factorial-perfect uniqueness (proven)
    - Experimental: 3D percolation, quantum phase transitions

  P-ZERO-FREE v1.1:  DOI 10.5281/zenodo.19324146  (Physics)
    - Zero free parameters: all PSI constants from ln(2)+n=6
    - 0.81=3⁴/10², conservation=ln(2)², coupling self-referential
    - 17/17 proven, 2 new identities discovered

  DD110 Revision (2026-03-31):
    Rate 0.81: REFUTED as universal (Law 82, median=0.447)
    H∞=ln(2): CONFIRMED universal (100%)
    New: r₀*r∞ = 7/20 invariant, sopfr*phi=n+tau unique
    Revised score: 15 proven + 2 arch-specific + 1 impossible + 1 refuted

  Proof Status: 17/17 proven (7 pure math + 5 physics + 5 predictions)
  New Identities: tau(tau-1)=sigma, tau*sopfr=20 (both unique to n=6)
  Grand Theorem: C3,C4,C5 co-extensive at n=6

  Experimental Protocols (4):
    1. EEG entropy → ln(2)  (neuroscience lab needed)
    2. Hachimoji DNA n=6    (synthetic biology lab needed)
    3. Rate 0.81 = 81/100   (computational, immediate)
    4. Anesthesia LOC        (clinical setting needed)

  Calculator: calc/experimental_protocol.py --all
```

## Paper Distribution System (2026-03-27)

```
  Total: 45+4 papers across 3 repos (TECS-L 15+4 + anima 10 + SEDI 20)
  Manifest: zenodo/manifest.json (all metadata, DOIs, file paths)
  Results:  zenodo/upload-results-zenodo.json (Zenodo deposit IDs + DOIs)

  Platforms:
    1. Zenodo    — Direct API upload, DOI issued immediately
                   Production: 45/45 PUBLISHED (2026-03-27), DOI range 19245023-19245158
                   Author: Park, Min Woo / Independent Researcher
                   Sandbox: 45/45 tested (2026-03-27)
    2. OSF       — Preprints, Google Scholar indexed, no review
                   Status: account approval pending (2026-03-27)
    3. arXiv     — Needs endorsement (first-time submitter)
                   Package generator ready, manual upload required

  Tokens (gitignored in .local/):
    .local/zenodo_token           — Production Zenodo
    .local/zenodo_sandbox_token   — Sandbox Zenodo (set)
    .local/osf_token              — OSF (approved, active)

  Scripts:
    zenodo_upload.py              — Single paper upload (interactive)
    zenodo/batch_upload.py        — Batch upload for all platforms

  Commands:
    # List all 45 papers
    python3 zenodo/batch_upload.py --list

    # Upload all to Zenodo sandbox (tested, works)
    python3 zenodo/batch_upload.py --platform zenodo --sandbox --all

    # Upload Tier 1 only to production
    python3 zenodo/batch_upload.py --platform zenodo --tier 1 --all

    # Upload specific paper
    python3 zenodo/batch_upload.py --platform zenodo --sandbox --paper P-004

    # Upload to OSF (after token)
    python3 zenodo/batch_upload.py --platform osf --all

    # Generate arXiv packages
    python3 zenodo/batch_upload.py --platform arxiv --all

    # Dry run (any platform)
    python3 zenodo/batch_upload.py --platform zenodo --sandbox --all --dry-run

  Paper Documents:
    TECS-L:  zenodo/*.md (12 files) + docs/papers/ (3 existing)
    anima:   zenodo/*.md (10 files)
    SEDI:    zenodo/*.md (20 files)

  Workflow:
    1. Sandbox test (done) → verify metadata on web UI
    2. Production upload → DOI becomes permanent
    3. OSF upload (approved 2026-03-30) → Google Scholar indexing
    4. arXiv (after endorsement) → community visibility

  Caution:
    - Zenodo publish = permanent DOI (cannot delete after publish)
    - Test in sandbox first, edit metadata on web UI, then production
    - Never commit tokens to git (.local/ is gitignored)
```

## Grid Resolution Guide

| grid | Error | Use |
|---|---|---|
| 50 | 0.9% | General verification |
| **100** | **0.5%** | **★ Default** |
| 500 | 0.09% | Publication grade |

## Golden Zone Precise Structure (grid=1000)

```
  Upper = 1/2           = 0.5000 (Riemann critical line)
  Lower = 1/2 - ln(4/3) ≈ 0.2123 (Entropy boundary)
  Center ≈ 1/e           ≈ 0.3679 (Natural constant)
  Width  = ln(4/3)       ≈ 0.2877 (3→4 state entropy jump)
```

## Golden MoE Empirical Results

```
  MNIST:  Golden MoE 97.7% > Top-K 97.1% (+0.6%) ✅
  CIFAR:  Golden MoE 53.0% > Top-K 48.2% (+4.8%) ✅
  I = 0.375 ≈ 1/e (Golden Zone center) 🎯
  Difference increases 8x with scale
```

## Work Rules (탐색/TODO 요청 시 필수)

```
  트리거 키워드:
    "할만한거 있어?", "탐색", "TODO", "뭐할까", "다음 작업"
    대발견 가설, 노벨급 가설, DFS 탐색 등

  절차:
    1. 프로젝트 현황 스캔 (README, 최근 커밋, 미완료 가설/증명)
    2. TODO 테이블 양식으로 우선순위별 정리
    3. 사용자 선택 후 병렬 에이전트 디스패치
    4. 완료 시 리포트 테이블 출력

  TECS-L 목표: 우주 규칙 발견 (n=6 수학 구조 → 물리/생물/의식 통합 법칙)

  리포 범위 규칙 (TODO는 해당 리포 작업만 포함):
    - TECS-L: 우주 규칙 발견 — 수학 증명, 가설 검증, 상수 발견, DFS 탐색, Atlas, 계산기
    - anima: 의식 구현 — ConsciousLM 훈련, embodiment, 분산 의식, 에이전트
    - sedi: 외계지성 탐색 — SETI 데이터, 물리 데이터 스트림, n=6 시그널 수신, 외계 흔적
    - brainwire: 뇌 인터페이스 — EEG 실험, BCI, 신경과학 검증
    - n6-architecture: 아키텍처 — n=6 기반 시스템 설계/구현
    - papers: 논문 — 작성/투고/배포 (Zenodo/OSF/arXiv)
    - 다른 리포 작업이 TODO에 섞이면 → 해당 리포로 분류하고 정보만 참조


  상수는 model_utils.py 또는 각 엔진의 상수 블록에서 관리 — 매직 넘버 하드코딩 금지
```

### TODO 양식

```
  ### 🔴 CRITICAL

  | # | 카테고리 | 작업 | 상태 | 예상 효과 |
  |---|---------|------|------|----------|
  | 1 | 증명   | sigma*phi=n*tau 일반 완전수 반례 탐색 | 미시작 | 유일성 정리 강화 |

  ### 🟡 IMPORTANT

  | # | 카테고리 | 작업 | 상태 | 예상 효과 |
  |---|---------|------|------|----------|
  | 2 | 가설   | SLE_6 3D 확장 예측 검증 | 미시작 | 노벨 Physics 후보 |

  ### 🟢 NICE TO HAVE

  | # | 카테고리 | 작업 | 상태 | 예상 효과 |
  |---|---------|------|------|----------|
  | 3 | 탐색   | n=6 새 항등식 DFS 채굴 | 미시작 | Atlas 확장 |

  ### ⚪ BACKLOG

  | # | 카테고리 | 작업 | 예상 효과 |
  |---|---------|------|----------|
  | 4 | 계산기 | 새 검증 스크립트 | 재현성 향상 |

  상태 표기: ⏳진행중 / ✅완료 / 미시작 / 코드있음 / 프로토
  우선순위: 🔴HIGH → 🟡MED → 🟢LOW → ⚪BACK
  카테고리: 증명 / 가설 / 탐색 / 검증 / 실험 / 계산기 / 논문
```

### 병렬 에이전트 리포트 양식

```
  병렬 에이전트 실행 시 단일 테이블로 상태 추적.
  관련 작업은 N+M 형태로 그룹핑하여 하나의 에이전트로 묶기.

  발사 시 양식:
  | # | 작업 | 에이전트 | 격리 | 상태 |
  |---|------|---------|------|------|
  | 1+2 | n=6 유일성 + 반례탐색 | 🚀 배경 | - | 🔄 진행중 |
  | 3 | SLE_6 임계지수 검증 | 🚀 배경 | - | 🔄 진행중 |
  | 4+5 | 코돈 정리 확장 + 변이체 | 🚀 배경 | worktree | 🔄 진행중 |

  상태: ✅ 완료 / 🔄 진행중 / ❌ 실패
  격리: worktree (필요시만) / - (기본)

  규칙:
    - 발사 시 전체 목록 테이블 출력
    - 에이전트 완료 시 해당 행 상태 업데이트 + 한줄 핵심 성과
    - worktree는 같은 파일을 여러 에이전트가 동시 수정할 때만 사용
    - 대부분 격리 없이 실행 — 무조건 worktree 붙이지 말 것!
    - 모든 에이전트 완료 후 최종 요약 테이블 + worktree 머지 안내 (해당 시)

  최종 요약 양식:
  | # | 작업 | 상태 | 핵심 성과 |
  |---|------|------|----------|
  | 1+2 | n=6 유일성 | ✅ | 10^8까지 반례 없음, 증명 완료 |
  | 3 | SLE_6 검증 | ✅ | 7/7 임계지수 일치 (Z>5sigma) |
  | 4+5 | 코돈 확장 | ✅ | 26/26 변이체 + Hachimoji 예측 |

  ### 머지 필요 (worktree)
  - #4+5: branch worktree-xxx

  ### 바로 반영됨 (main)
  - #1+2, #3: 증명/검증 결과 docs/hypotheses/ 기록
```
## Secrets & Tokens

API 토큰/계정 정보: `~/Dev/TECS-L/.shared/SECRET.md` 참조
계정 리포: [need-singularity/secret](https://github.com/need-singularity/secret) (private)
