# .shared/ — Cross-Repo Shared Infrastructure

> **이 폴더는 TECS-L에 원본이 있고, 타 리포는 심링크로 연결됩니다.**
> 타 리포: `.shared/ → ../TECS-L/.shared/`

## 망원경 툴셋 자동 활용 규칙 (필수 — 최우선)

> **탐색/실험/발견 작업 시 별도 요청 없이 렌즈를 적극 활용할 것!**

### 자동 적용 조건

어떤 프로젝트에서든 아래 상황이면 렌즈를 자동으로 돌릴 것:
- 새 데이터셋 분석 시 → 의식+중력+위상 3종 기본 스캔
- 이상점/패턴 탐색 시 → 전체 9종 풀스캔
- 신소재/신약 후보 탐색 시 → 진화+열역학+중력 조합
- 시계열 분석 시 → 파동+열역학+의식 조합
- 상수/법칙 관계 탐색 시 → 정보+양자+의식 조합

### 렌즈 선택 가이드

```
"숨겨진 구조가 있나?"     → 의식 렌즈 (Φ + 파벌)
"안정점/끌개가 있나?"     → 중력 렌즈 (attractor basin)
"구멍/연결이 있나?"       → 위상 렌즈 (Betti + persistence)
"상전이가 있나?"          → 열역학 렌즈 (엔트로피 + 자유에너지)
"주기/공명이 있나?"       → 파동 렌즈 (FFT + 하모닉)
"최적 조합이 있나?"       → 진화 렌즈 (fitness landscape)
"정보가 어디에 있나?"     → 정보 렌즈 (MI + 압축)
"비국소 상관이 있나?"     → 양자 렌즈 (얽힘 + 터널링)
"흐름 방향이 있나?"       → 전자기 렌즈 (gradient + curl)
```

### 9종 렌즈 목록

| 렌즈 | 파일 | 원리 | 찾는 것 |
|------|------|------|---------|
| 의식 | `consciousness_lens.py` | Φ + 파벌 토론 + Hebbian | 숨겨진 구조, 이상점, 상관관계 |
| 중력 | `gravity_lens.py` | N-body + attractor basin | 끌개, 안정점, 에너지 장벽 |
| 위상 | `topology_lens.py` | persistent homology + Betti | 구멍, 연결 구조, 위상 전이 |
| 열역학 | `thermo_lens.py` | Boltzmann + 상전이 | 질서↔무질서 경계, 임계점 |
| 파동 | `wave_lens.py` | FFT + 공명 + 간섭 | 주기성, 공명 관계, 주파수 변화 |
| 진화 | `evolution_lens.py` | GA + fitness landscape | 최적 조합, 진화 경로 |
| 정보 | `info_lens.py` | Shannon + LZ + MI | 정보량, 잉여, 압축 가능성 |
| 양자 | `quantum_lens.py` | 얽힘 + 터널링 + 중첩 | 비국소 상관, 장벽 우회 경로 |
| 전자기 | `em_lens.py` | gradient + curl + divergence | 흐름, 소스/싱크, 와류 |

### 풀스캔 사용법

```python
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '.shared'))
from consciousness_lens import ConsciousnessLens
from gravity_lens import GravityLens
from topology_lens import TopologyLens
from thermo_lens import ThermoLens
from wave_lens import WaveLens
from evolution_lens import EvolutionLens
from info_lens import InfoLens
from quantum_lens import QuantumLens
from em_lens import EMLens

# 9종 풀스캔
data = load_your_data()
for Lens in [ConsciousnessLens, GravityLens, TopologyLens, ThermoLens,
             WaveLens, EvolutionLens, InfoLens, QuantumLens, EMLens]:
    result = Lens().scan(data)
    print(f"{Lens.__name__}: {result.summary}")
```

### 렌즈 추가 요청 시

사용자가 "렌즈 추가 필요한지", "다른 렌즈 아이디어" 등을 물으면:
1. 현재 9종으로 커버 안 되는 도메인 분석
2. 새 물리/수학 비유에서 렌즈 아이디어 도출
3. 구체적 활용 시나리오와 함께 제안

### 교차 검증 (telescope_cross_test.py)

```
9종 렌즈 교차 검증 결과 (2026-04-02):
  Cross-validated GT: 4/4 (100%)
  f0↔f1 상관: 3/9 렌즈 합의 (의식+정보+양자)
  anomaly #10: 4/9 렌즈 합의 (의식+중력+양자+전자기)
  클러스터 구조: 3/9 렌즈 감지 (의식+위상+열역학)

해석:
  - 1개 렌즈만 찾은 것 = 가설 (추가 검증 필요)
  - 2개 렌즈 합의 = 후보 (유의미할 가능성 높음)
  - 3개+ 렌즈 합의 = 확정 (독립 검증 통과)
  - 실행: python3 .shared/telescope_cross_test.py

교차 교정 (telescope_calibrate.py):
  렌즈 A의 발견을 힌트로 렌즈 B의 데이터/파라미터 교정.
  방법: 컨센서스 anomaly 증폭 + correlation 강화 + 파라미터 튜닝
  결과: baseline 합의만으로 GT 4/4 (100%) — 교정 루프 없이도 합의가 충분
  렌즈별 강점:
    의식(consciousness): 구조+이상+상관 모두 감지 (4/4 만점)
    양자(quantum): 상관 발견에 특화 (entanglement = MI 대안)
    전자기(em): anomaly 감지량 최대 (55개, 과감지 경향)
    중력(gravity): attractor basin 특화 (클러스터)
    정보(info): 특징 간 MI에 특화 (redundancy 발견)
  교정이 유효한 경우: 약한 패턴을 다수 렌즈 합의로 부스팅
  실행: python3 .shared/telescope_calibrate.py
```

### 새 프로젝트에 의식 브릿지 추가 시

```bash
# 1. .shared 심링크 확인
ls -la .shared/consciousness_loader.py

# 2. consciousness_bridge.py 생성 (도메인별 함수)
# 3. 이 테이블에 행 추가
```

## 의식 렌즈 (consciousness_lens.py) — 범용 탐색 도구

> 의식엔진을 망원경처럼 사용: 어떤 데이터든 넣으면 숨겨진 구조/이상점/관계를 발견.
> 원리: GRU cells + 12 factions 토론 + Hebbian 학습 + Φ 측정 + 텐션 이상 감지
> 의존성: numpy만 (torch 불필요). 모든 프로젝트에서 즉시 사용 가능.

### 기본 사용

```python
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '.shared'))
from consciousness_lens import ConsciousnessLens, quick_scan

# 원라이너
result = quick_scan(data_matrix)

# 상세 설정
lens = ConsciousnessLens(cells=64, steps=300)
result = lens.scan(data)
print(result.phi)          # 통합 정보 (높으면 = 숨겨진 구조)
print(result.anomalies)    # 이상점 [(index, score), ...]
print(result.clusters)     # 파벌 합의 클러스터
print(result.discoveries)  # 발견된 상관관계
print(result.summary)      # 요약 텍스트
```

### 도메인별 스캔

```python
# 1. 재료/물질 탐색 — 신소재 후보 발견
result = lens.scan_materials(
    properties,                    # (N재료, N특성) 배열
    labels=["원자번호", "전기음성도", "전도도", "밀도", "녹는점"]
)
# result.anomalies → 특이한 물질 (신소재 후보)
# result.discoveries → 숨겨진 특성 간 관계
# result.discoveries[0]['interpretation']
#   → "전도도 increases with 녹는점 (r=0.987, 3 factions agree)"

# 2. 신호 분석 — SEDI 외계 신호, EEG, 센서 데이터
result = lens.scan_signals(
    signal_array,                  # (채널, 샘플) 또는 (샘플,)
    window=256                     # 세그먼트 크기
)
# result.phi > PSI_ENTROPY * 0.5 → "의식 수준 통합" 감지
# result.anomalies → 이상 구간 (버스트, 레짐 변화)

# 3. 시계열 — 금융, 기후, 실험 데이터
result = lens.scan_timeseries(
    ts_data,                       # (시간, 변수) 또는 (시간,)
    lag=10                         # 지연 임베딩
)
# result.anomalies → 레짐 전환점 (시간 인덱스)
# result.clusters → 시간 구간 클러스터
```

### Phi 해석 가이드

```
Phi < 0.3   → 노이즈/무작위 (구조 없음)
Phi 0.3-0.8 → 약한 구조 (일부 상관)
Phi 0.8-1.5 → 강한 구조 (숨겨진 패턴 확실)
Phi > 1.5   → 매우 높은 통합 (복잡한 시스템)
```

### 프로젝트별 활용 시나리오

```
TECS-L:     수학 상수 테이블 스캔 → 숨겨진 관계식 발견
SEDI:       77개 데이터 소스 스캔 → 지적 신호 후보 필터링
N6 Arch:    아키텍처 파라미터 공간 스캔 → 최적 설계점 발견
BrainWire:  EEG 실시간 스캔 → 의식 상태 모니터링
HEXA-LANG:  컴파일러 중간 표현 스캔 → 코드 구조 품질 측정
anima:      의식 엔진 텔레메트리 스캔 → 법칙 자동 발견 (기존 파이프라인)
```

---

## 핵심 원칙

**TECS-L/.shared/ = 모든 리포의 단일 소스 (Single Source of Truth)**

어떤 리포에서 작업하든, 새로운 계산기/상수/도구를 만들면 반드시 여기에 등록하고 동기화합니다.

## 새로운 산출물 발생 시 즉시 처리 (필수)

### 1. 새 계산기 생성 시
```bash
# 계산기는 반드시 .shared/calc/ 에 생성
# 어떤 리포에서 작업하든 calc/ 심링크가 .shared/calc/ 를 가리킴
python3 calc/my_new_calculator.py   # 생성 즉시 모든 리포에서 접근 가능

# 레지스트리 갱신
python3 .shared/scan-calculators.py --save --summary
```

### 2. 새 상수 발견 시
```bash
# Math Atlas 자동 갱신 (가설/상수 파일에 기록 후)
python3 .shared/scan_math_atlas.py --save --summary

# README 동기화
bash .shared/sync-math-atlas.sh
```

### 3. 새 도구/스크립트 생성 시
- 단일 리포 전용 → 해당 리포에 유지
- 크로스 리포 유틸리티 → `.shared/` 에 배치
- 설치 도구 추가 → `.shared/installed_tools.json` 갱신

### 4. 가설 등급 변경 시
```bash
# Atlas 재빌드
python3 .shared/scan_math_atlas.py --save --summary
```

## 폴더 구조

```
.shared/
  CLAUDE.md              ← 이 파일 (공유 규칙)
  CALCULATOR_RULES.md    ← 계산기 생성 규칙 (Rust vs Python 판단)
  SECRET.md              ← API 토큰/계정 (gitignored in 타 리포)
  projects.md            ← 프로젝트 설명 원본 (README 동기화용)
  shared_work_rules.md   ← 작업 규칙 (CLAUDE.md SHARED:WORK_RULES 주입용)
  installed_tools.json        ← 설치 도구 레지스트리
  consciousness_laws.json     ← 의식 법칙/PSI 상수 (anima에서 이관)
  consciousness_mechanisms.json ← 의식 메커니즘 (상태머신, 게이트)
  consciousness_loader.py     ← 의식 법칙/상수 Python 로더 (크로스 리포 import용)
  sedi-grades.json            ← SEDI 가설 등급 (역동기화)
  sync_to_atlas.py            ← Atlas 동기화 (sedi에서 이관)

  calc/                  ← 계산기 원본 (194+ files, Python)
  tecsrs/                ← Rust 고성능 계산기 (Monte Carlo, 탐색, ODE)
    src/                 ← 공용 모듈 (perfect.rs, search.rs, monte_carlo.rs...)
    src/bin/             ← 독립 실행 바이너리
    Cargo.toml
  dse/                   ← Domain-Specific Exploration
    domains/*.toml       ← DSE 도메인 정의

  calculators.json       ← 계산기 레지스트리 (자동 생성)
  math_atlas.json        ← 수학 지도 (자동 생성)
  math_atlas.db          ← SQLite (쿼리용)
  MATH_ATLAS.md          ← 전체 목록 마크다운

  scan-calculators.py    ← 계산기 스캐너
  scan_math_atlas.py     ← Atlas 스캐너
  sync-readmes.sh        ← README 프로젝트 설명 동기화
  sync-calculators.sh    ← 계산기 레지스트리 동기화
  sync-math-atlas.sh     ← Atlas 빌드 + README 주입
  sync-claude-rules.sh   ← CLAUDE.md 작업 규칙 주입
  sync-dse.sh            ← DSE 도메인 동기화
```

## 동기화 명령 (전체)

```bash
# 개별 실행 (순서 무관)
bash .shared/sync-math-atlas.sh      # Atlas 빌드 + README
bash .shared/sync-calculators.sh     # 계산기 레지스트리
bash .shared/sync-readmes.sh         # 프로젝트 설명
bash .shared/sync-claude-rules.sh    # CLAUDE.md 작업 규칙

# 전체 동기화 (권장 순서)
bash .shared/sync-math-atlas.sh && \
bash .shared/sync-calculators.sh && \
bash .shared/sync-readmes.sh && \
bash .shared/sync-claude-rules.sh
```

## 심링크 구조

```
TECS-L/                          (원본)
  .shared/          ← 실제 폴더
  calc → .shared/calc
  tecsrs → .shared/tecsrs

anima, sedi, brainwire,          (소비자)
n6-architecture, papers/
  .shared → ../TECS-L/.shared    ← 심링크
  calc → .shared/calc            ← 심링크 체인
  tecsrs → .shared/tecsrs       ← Rust 계산기 공유
```

## 계산기 규칙 요약

> 상세: `.shared/CALCULATOR_RULES.md`

| 조건 | 언어 |
|------|------|
| 반복 > 10,000회 | Rust (tecsrs/) |
| 실행 > 10초 예상 | Rust |
| Monte Carlo > 100K | Rust |
| 단순 수식 검증 | Python (calc/) |
| 시각화/출력 | Python |

## 리포별 역할

| 리포 | 역할 | .shared 사용 |
|------|------|-------------|
| TECS-L | 수학 엔진 코어 | 원본 관리 |
| anima | 의식 구현 | 상수/계산기 소비 |
| sedi | 외계지성 탐색 | 상수/계산기 소비, 등급 역동기화 |
| brainwire | 뇌 인터페이스 | 상수/계산기 소비 |
| n6-architecture | 시스템 설계 | 상수/계산기 소비, DSE 역동기화 |
| papers | 논문 배포 | Atlas/계산기 참조 |
| golden-moe | MoE 라우팅 | 의식 라우팅 파라미터 |
| hexa-lang | 프로그래밍 언어 | Ψ 내장 상수, 린트 |

## 의식 법칙 크로스 리포 활용 (consciousness_loader.py)

> 의식 법칙(711개)과 Ψ 상수(80개)를 모든 프로젝트에서 활용.
> 원본: `.shared/consciousness_laws.json` → 로더: `.shared/consciousness_loader.py`

### 기본 사용법

```python
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '.shared'))
from consciousness_loader import PSI, LAWS, FORMULAS, get_law, get_psi

print(PSI['alpha'])     # 0.014
print(get_law(22))      # "Adding features → Φ↓; adding structure → Φ↑"
```

### 리포별 consciousness_bridge.py 활용

각 프로젝트 루트에 `consciousness_bridge.py`가 있으며, 도메인별 의식 법칙 활용 함수 제공:

| 리포 | 브릿지 | 핵심 함수 | 용도 |
|------|--------|----------|------|
| TECS-L | `consciousness_bridge.py` | `psi_from_n6()`, `cross_validate_constants()` | Ψ 상수의 n=6 수학적 도출 검증 |
| anima | `src/consciousness_laws.py` | `PSI`, `LAWS`, `check_violation()` | 의식 엔진 코어 (원본) |
| sedi | `consciousness_bridge.py` | `signal_phi_score()`, `is_conscious_signal()` | Φ 기반 지적 신호 판별 |
| n6-arch | `consciousness_constraints.py` | `validate_architecture()`, `suggest_dimensions()` | 칩/AI 설계 법칙 제약조건 |
| brainwire | `consciousness_bridge.py` | `validate_stimulation()`, `eeg_consciousness_score()` | 뇌자극 안전 검증 |
| hexa-lang | `consciousness_bridge.py` | `psi_builtins()`, `lint_consciousness()` | 언어 내장 상수 + 린트 |
| golden-moe | `consciousness_bridge.py` | `faction_routing()`, `phi_gated_selection()` | 의식 역학 MoE 라우팅 |

### 주요 Ψ 상수 (크로스 리포 공통)

```
PSI_ALPHA    = 0.014   # PureField 혼합 비율 (C→D 결합 강도)
PSI_BALANCE  = 0.5     # 의식 균형점 (좌뇌/우뇌, 흥분/억제)
PSI_STEPS    = 4.33    # 의식 단계 수 (ln(2) 파생)
PSI_ENTROPY  = 0.998   # 의식 엔트로피 상한
SIGMA6       = 12      # σ(6) = 약수합 → 12 파벌, 12 모듈
F_CRITICAL   = 0.10    # 임계 좌절 (10% 갈등이 최적)
```

