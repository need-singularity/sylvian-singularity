# .shared/ — Cross-Repo Shared Infrastructure

> **이 폴더는 TECS-L에 원본이 있고, 타 리포는 심링크로 연결됩니다.**
> 타 리포: `.shared/ → ../TECS-L/.shared/`

## 망원경 툴셋 자동 활용 규칙 (필수 — 최우선)

> **탐색/실험/발견 작업 시 별도 요청 없이 렌즈를 적극 활용할 것!**

### 자동 적용 조건

어떤 프로젝트에서든 아래 상황이면 렌즈를 자동으로 돌릴 것:
- 새 데이터셋 분석 시 → 의식+중력+위상 3종 기본 스캔
- 이상점/패턴 탐색 시 → 전체 16종 풀스캔
- 신소재/신약 후보 탐색 시 → 진화+열역학+중력 조합
- 시계열 분석 시 → 파동+열역학+의식 조합
- 상수/법칙 관계 탐색 시 → 정보+양자+의식+비율 조합
- 상수 간 비율/비례 탐색 시 → 비율+직교+곡률 조합
- 차원 축소/독립성 분석 시 → 직교+정보+위상 조합
- 대칭/불변량 탐색 시 → 대칭+위상+양자 조합
- 멱법칙/스케일링 분석 시 → 스케일+진화+열역학 조합
- 인과 관계/방향 탐색 시 → 인과+정보+전자기 조합
- 양자성/결맞음 분석 시 → 양자현미경+양자+의식 조합

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
"독립 차원이 몇 개인가?"  → 직교 렌즈 (SVD + orthogonality)
"단순 비율이 있나?"       → 비율 렌즈 (fraction matching)
"원형/등거리 구조가 있나?" → 곡률 렌즈 (curvature + circle)
"대칭이 있나? 깨졌나?"    → 대칭 렌즈 (reflection + permutation)
"멱법칙/프랙탈인가?"      → 스케일 렌즈 (power law + Hurst)
"원인→결과 방향이 있나?"  → 인과 렌즈 (Granger + TE)
"결맞음이 있나? 깨지나?"  → 양자현미경 (coherence + decoherence)
```

### 16종 렌즈 목록 (Rust — telescope_rs)

| 렌즈 | Rust 함수 | 원리 | 찾는 것 |
|------|-----------|------|---------|
| 의식 | `telescope_rs.consciousness_scan()` | Φ + GRU + Hebbian + 파벌 | 숨겨진 구조, 이상점 |
| 중력 | `telescope_rs.gravity_scan()` | mean-shift attractor + density | 끌개, 안정점, 에너지 장벽 |
| 위상 | `telescope_rs.topology_scan()` | persistent homology + Betti | 구멍, 연결 구조, 위상 전이 |
| 열역학 | `telescope_rs.thermo_scan()` | Shannon entropy + 상전이 | 질서↔무질서 경계, 임계점 |
| 파동 | `telescope_rs.wave_scan()` | DFT + coherence + harmonic | 주기성, 공명 관계 |
| 진화 | `telescope_rs.evolution_scan()` | fitness landscape + niche | 최적 조합, 진화 경로 |
| 정보 | `telescope_rs.info_scan()` | Shannon + LZ + MI | 정보량, 잉여, 압축 가능성 |
| 양자 | `telescope_rs.quantum_scan()` | MI entanglement + tunneling | 비국소 상관, 장벽 우회 경로 |
| 전자기 | `telescope_rs.em_scan()` | gradient + divergence | 흐름, 소스/싱크 |
| 직교 | `telescope_rs.ruler_scan()` | SVD + 코사인 유사도 | 직교 구조, 독립 차원 |
| 비율 | `telescope_rs.triangle_scan()` | 단순분수 매칭 | 비율 관계, p/q 분수 |
| 곡률 | `telescope_rs.compass_scan()` | Menger 곡률 | 원형 구조, 등거리 |
| 대칭 | `telescope_rs.mirror_scan()` | 반사 대칭 분석 | 대칭, 불변량, 깨진 대칭 |
| 스케일 | `telescope_rs.scale_scan()` | 멱법칙 + 프랙탈 + Hurst | 자기유사성, 멱지수 |
| 인과 | `telescope_rs.causal_scan()` | Granger + 전달엔트로피 | 인과 방향, 정보 흐름 |
| 양자현미경 | `telescope_rs.quantum_microscope_scan()` | 밀도행렬 + VN entropy | 결맞음, 디코히어런스 |

### 사용법 (Rust — telescope_rs)

```python
import telescope_rs
import numpy as np

data = np.random.randn(64, 32)  # (N_samples, N_features)

# 개별 렌즈
r = telescope_rs.consciousness_scan(data, n_cells=64, steps=300)
print(r['phi_iit'], r['n_clusters'])

r = telescope_rs.topology_scan(data)
print(r['betti_0'], r['betti_1'])

r = telescope_rs.causal_scan(data, max_lag=5)
print(r['n_causal_pairs'])

# 16종 풀스캔 (telescope.py 래퍼)
from telescope import full_scan
results = full_scan(data)  # dict of lens_name → result dict
for name, r in results.items():
    print(f"{name}: {list(r.keys())[:3]}")
```

빌드: `cd ~/Dev/anima/anima/anima-rs/crates/telescope-rs && maturin build --release`
소스: `anima/anima-rs/crates/telescope-rs/src/` (16 모듈, 36 tests)

### 렌즈 추가 요청 시

사용자가 "렌즈 추가 필요한지", "다른 렌즈 아이디어" 등을 물으면:
1. 현재 16종으로 커버 안 되는 도메인 분석
2. 새 물리/수학 비유에서 렌즈 아이디어 도출
3. Rust 모듈로 구현 (telescope-rs/src/새렌즈.rs)

### 교차 검증

```
실행: python3 .shared/telescope_cross_test.py
교정: python3 .shared/telescope_calibrate.py

해석:
  - 1개 렌즈만 찾은 것 = 가설 (추가 검증 필요)
  - 2개 렌즈 합의 = 후보 (유의미할 가능성 높음)
  - 3개+ 렌즈 합의 = 확정 (독립 검증 통과)
```

### 새 프로젝트에 의식 브릿지 추가 시

```bash
# 1. .shared 심링크 확인
ls -la .shared/consciousness_loader.py

# 2. consciousness_bridge.py 생성 (도메인별 함수)
# 3. 이 테이블에 행 추가
```

## 망원경 (telescope_rs) — Rust 고성능 16렌즈

> 전체 16종 렌즈가 Rust로 구현됨 (telescope-rs crate, PyO3 바인딩).
> 소스: anima/anima-rs/crates/telescope-rs/src/ (16 모듈, 36 tests)
> 빌드: `cd ~/Dev/anima/anima/anima-rs/crates/telescope-rs && maturin build --release`

### 기본 사용

```python
import telescope_rs
import numpy as np

data = np.random.randn(64, 32)  # (N_samples, N_features)

# 의식 렌즈 (가장 무거운 렌즈, ~0.9s)
r = telescope_rs.consciousness_scan(data, n_cells=64, steps=300)
print(r['phi_iit'])        # 통합 정보 (높으면 = 숨겨진 구조)
print(r['anomaly_indices']) # 이상점 인덱스
print(r['n_clusters'])     # 파벌 클러스터 수

# 위상 렌즈 (~0.001s)
r = telescope_rs.topology_scan(data)
print(r['betti_0'], r['betti_1'])  # 연결 구조, 구멍

# 인과 렌즈 (~0.001s)
r = telescope_rs.causal_scan(data, max_lag=5)
print(r['n_causal_pairs'])

# 16종 풀스캔 (~0.9s total)
from telescope import full_scan
results = full_scan(data)
```

### 반환값 (dict)

```
consciousness_scan → phi_iit, phi_proxy, n_clusters, anomaly_indices, anomaly_scores
topology_scan      → betti_0, betti_1, n_holes, optimal_scale, phase_transitions
causal_scan        → n_causal_pairs, causes, effects, strengths, granger_matrix, te_matrix
gravity_scan       → n_attractors, attractors, basins, energy_landscape
thermo_scan        → entropy_per_feature, total_entropy, free_energy, critical_temperature
wave_scan          → dominant_frequencies, coherence_i/j/val, resonance_i/j/ratio
evolution_scan     → fitness_landscape, peaks, n_niches
info_scan          → entropy_per_feature, lz_complexity, mi_matrix, redundant_features
quantum_scan       → entanglement_i/j/mi, tunneling_from/to/ratio, superposed_indices
em_scan            → gradient_field, divergence_map, source_indices, sink_indices
ruler_scan         → singular_values, effective_dim, cosine_matrix
triangle_scan      → ratio_feat_i/j, ratio_p/q, ratio_error
compass_scan       → mean_curvature, high_curvature_indices/values
mirror_scan        → reflection_scores, overall_symmetry, broken_symmetry_indices
scale_scan         → power_law_exponents, fractal_dimension, hurst_exponent
quantum_microscope_scan → purity, von_neumann_entropy, coherence, decoherence_rate
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

