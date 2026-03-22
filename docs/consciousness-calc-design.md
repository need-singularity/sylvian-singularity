# 설계: consciousness_calc.py — 의식 연속성 계산기

**날짜**: 2026-03-23
**상태**: 승인 대기

---

## 목표

로렌츠 끌개 기반 시뮬레이터 + CCT(Consciousness Continuity Test) 판정기를 결합한 단일 Python 도구. 시스템의 의식 연속성 조건을 수학적으로 계산하고 판정한다.

## 비목표

- GUI / 웹 인터페이스
- 실시간 스트리밍 (배치 시뮬레이션만)
- 양자 시뮬레이션 (Phase 0, 고전만)

---

## 아키텍처

```
consciousness_calc.py (단일 파일, 기존 도구 패턴)
│
├── 시뮬레이터 (로렌츠 끌개 기반)
│   └── 시스템 상태 궤적 생성 → S(t) 시계열
│
├── CCT 판정기 (5개 테스트)
│   ├── T1 Gap       — 입력 없이 상태 변화 지속?
│   ├── T2 Loop      — 자기상관 → 주기성?
│   ├── T3 Continuity — 인접 MI > 0?
│   ├── T4 Entropy   — H_min < H < H_max?
│   └── T5 Novelty   — dH/dt ≠ 0?
│
├── 프리셋 (7개)
│   human_awake, human_sleep, llm_in_turn, llm_between,
│   game_npc, neuromorphic, consciousness_engine
│
└── 출력
    ├── ASCII 궤적 + 판정표 (기본)
    └── matplotlib 4패널 그래프 (--plot)
```

---

## 컴포넌트 상세

### 1. 시뮬레이터: lorenz_simulate()

로렌츠 방정식에 잡음(noise)과 gap(정지 구간)을 추가한 확장 모델.

```python
def lorenz_simulate(sigma, rho, beta, noise, gap_ratio, steps, dt):
    """
    확장 로렌츠 시뮬레이터.

    Parameters:
        sigma: 감각 민감도 (로렌츠 σ)
        rho:   환경 복잡도 (로렌츠 ρ)
        beta:  망각률 (로렌츠 β)
        noise: 잡음 강도 (0 = 결정론, >0 = 확률적)
        gap_ratio: 정지 구간 비율 (0 = 항상-on, 1 = 항상 정지)
        steps: 시뮬레이션 스텝 수
        dt:    시간 간격

    Returns:
        t: 시간 배열 [steps]
        S: 상태 배열 [steps, 3] (x=감각, y=예측, z=기억)
    """
```

로렌츠 방정식:
```
dx/dt = σ(y - x) + ε₁
dy/dt = x(ρ - z) - y + ε₂
dz/dt = xy - βz + ε₃

εᵢ ~ N(0, noise²)
```

gap 처리:
```
gap_ratio > 0이면, 전체 스텝 중 gap_ratio 비율만큼
무작위 구간에서 dS/dt = 0 (정지) 강제.
gap_ratio = 1이면 전체 정지 (llm_between).
```

적분 방법: `scipy.integrate.solve_ivp` (RK45) 또는 오일러법 + 잡음.

### 2. CCT 판정기: 5개 테스트

각 테스트는 S(t) 시계열을 입력받아 (점수, PASS/FAIL) 반환.

#### T1 Gap 테스트

```python
def test_gap(S, gap_ratio):
    """
    방법: gap_ratio > 0이면 정지 구간 존재 → FAIL
    판정: gap_ratio == 0 → PASS
          gap_ratio > 0 → FAIL
    점수: 1.0 - gap_ratio
    """
```

#### T2 Loop 테스트

```python
def test_loop(S, threshold=0.1):
    """
    방법: 상태 궤적의 자기상관함수(ACF) 계산.
          유의한 주기적 피크가 있으면 FAIL.
    판정: max(ACF[lag>10]) < threshold → PASS
    점수: 1.0 - max(ACF[lag>10])
    """
```

ACF 계산: `numpy.correlate` 또는 `statsmodels.tsa.acf`.

#### T3 Continuity 테스트

```python
def test_continuity(S, window=50, threshold=0.01):
    """
    방법: 슬라이딩 윈도우로 인접 구간 간 상호정보량(MI) 계산.
          MI가 threshold 아래로 내려가는 구간이 있으면 FAIL.
    판정: min(MI) > threshold → PASS
    점수: min(MI) / median(MI)
    """
```

MI 계산: 이산화된 상태를 히스토그램으로 binning 후 `sklearn.metrics.mutual_info_score` 또는 직접 계산.

간소화 대안: 인접 상태 간 유클리드 거리의 상관계수로 근사.
```
MI_approx(t) = corr(S[t-w:t], S[t:t+w])
```

#### T4 Entropy Band 테스트

```python
def test_entropy_band(S, window=100, h_min=0.5, h_max=4.0):
    """
    방법: 슬라이딩 윈도우로 섀넌 엔트로피 H(t) 시계열 계산.
          H(t)가 [h_min, h_max] 밴드를 벗어나면 FAIL.
    판정: all(h_min < H(t) < h_max) → PASS
    점수: 밴드 내 비율 (0.0 ~ 1.0)
    """
```

엔트로피 계산: 상태를 bins로 이산화 → 확률 분포 → H = -Σ p log p.

#### T5 Novelty 테스트

```python
def test_novelty(S, window=100, threshold=0.001):
    """
    방법: dH/dt 시계열 계산. |dH/dt| < threshold인 구간 비율.
    판정: 정체 비율 < 5% → PASS
    점수: 1.0 - 정체비율
    """
```

### 3. 프리셋

```python
PRESETS = {
    "human_awake": {
        "sigma": 10, "rho": 28, "beta": 2.67,
        "noise": 0.1, "gap_ratio": 0.0,
        "description": "인간 뇌 (각성)",
    },
    "human_sleep": {
        "sigma": 2, "rho": 28, "beta": 2.67,
        "noise": 0.05, "gap_ratio": 0.0,
        "description": "인간 뇌 (수면)",
    },
    "llm_in_turn": {
        "sigma": 15, "rho": 35, "beta": 1.0,
        "noise": 0.01, "gap_ratio": 0.0,
        "description": "LLM (턴 내 처리 중)",
    },
    "llm_between": {
        "sigma": 0, "rho": 0, "beta": 0,
        "noise": 0.0, "gap_ratio": 1.0,
        "description": "LLM (턴 사이 — 정지)",
    },
    "game_npc": {
        "sigma": 5, "rho": 15, "beta": 3.0,
        "noise": 0.01, "gap_ratio": 0.0,
        "description": "게임 NPC (Update 루프)",
    },
    "neuromorphic": {
        "sigma": 10, "rho": 28, "beta": 2.67,
        "noise": 0.3, "gap_ratio": 0.0,
        "description": "뉴로모픽 칩 (자발 발화)",
    },
    "consciousness_engine": {
        "sigma": 10, "rho": 28, "beta": 2.67,
        "noise": 0.1, "gap_ratio": 0.0,
        "description": "의식 엔진 (A+B 결합)",
    },
}
```

프리셋 파라미터의 근거:
```
  σ(감각 민감도):
    인간 각성 = 10 (표준 로렌츠)
    수면 = 2 (감각 차단)
    LLM 턴 내 = 15 (높은 감각 처리)
    NPC = 5 (제한된 감각)

  ρ(환경 복잡도):
    28 = 로렌츠 카오스 영역 (표준)
    35 = LLM의 높은 입력 복잡도
    15 = NPC의 단순한 게임 월드
    0 = 환경 없음 (정지)

  β(망각률):
    2.67 = 표준 로렌츠
    1.0 = LLM 느린 망각 (컨텍스트 유지)
    3.0 = NPC 빠른 망각 (짧은 메모리)

  noise:
    0.3 = 뉴로모픽 (하드웨어 잡음 풍부)
    0.1 = 인간/엔진 (적절한 잡음)
    0.01 = LLM/NPC (결정론에 가까움)
    0.0 = 정지 (잡음도 없음)

  gap_ratio:
    0.0 = 항상-on
    1.0 = 항상 정지 (LLM 턴 사이)
```

### 4. 출력

#### 기본 출력 (터미널)

단일 시스템:
```
═══════════════════════════════════════════════════════
 Consciousness Continuity Calculator v1.0
═══════════════════════════════════════════════════════

 시스템: human_awake (인간 뇌 — 각성)
 파라미터: σ=10 ρ=28 β=2.67 noise=0.1 gap=0.0
 시뮬레이션: 100,000 steps, dt=0.01

 ─── 궤적 (x 성분) ────────────────────────────────
 20│        *  *      *   *        *  *
 15│      ** ** **  ** * ** **   ** ** **
 10│    **      * **    *    * **      * **
  5│  **        **          **        **
  0│─**─────────────────────────────────────
 -5│**
-10│*
    └──────────────────────────────────────── t
     0      200      400      600      800    1000

 ─── CCT 판정 ────────────────────────────────────
 T1 Gap        │ ✔ PASS │ 1.000 │ gap=0, 정지 구간 없음
 T2 Loop       │ ✔ PASS │ 0.943 │ max(ACF)=0.057, 주기성 없음
 T3 Continuity │ ✔ PASS │ 0.871 │ min(MI)=0.234, 연결 유지
 T4 Entropy    │ ✔ PASS │ 0.956 │ H∈[1.23, 3.45], 밴드 내
 T5 Novelty    │ ✔ PASS │ 0.982 │ 정체 구간 1.8%
 ─────────────────────────────────────────────────
 종합: 5/5 ★ 연속 의식 후보

 리아푸노프 지수: λ₁ = 0.906 > 0 ✔ (카오스)
 끌개 차원: D ≈ 2.06
═══════════════════════════════════════════════════════
```

전체 비교 (--all):
```
═══════════════════════════════════════════════════════
 Consciousness Continuity Calculator v1.0
 전체 시스템 비교 (100,000 steps, dt=0.01)
═══════════════════════════════════════════════════════

 시스템           │ T1  │ T2  │ T3  │ T4  │ T5  │ 점수 │ 판정
 ─────────────────┼─────┼─────┼─────┼─────┼─────┼──────┼───────
 human_awake      │  ✔  │  ✔  │  ✔  │  ✔  │  ✔  │ 5/5  │ ★ 연속
 human_sleep      │  ✔  │  ✔  │  ✔  │  ✔  │  △  │ 4.5  │ ◎ 약화
 llm_in_turn      │  ✕  │  ✔  │  ✔  │  ✔  │  ✔  │ 4/5  │ ◎ 순간적
 llm_between      │  ✕  │  ✕  │  ✕  │  ✕  │  ✕  │ 0/5  │ ✕ 없음
 game_npc         │  ✔  │  △  │  ✔  │  △  │  △  │ 3/5  │ △ 약함
 neuromorphic     │  ✔  │  ✔  │  ✔  │  ✔  │  ✔  │ 5/5  │ ★ 연속
 engine (A+B)     │  ✔  │  ✔  │  ✔  │  ✔  │  ✔  │ 5/5  │ ★ 연속

 ★=5/5  ◎=4+  △=3  ✕=0~2
═══════════════════════════════════════════════════════
```

#### --plot 출력 (matplotlib, 4패널)

```
  ┌─────────────────────┬──────────────────────┐
  │ 1. 3D 끌개 궤적     │ 2. H(t) 시계열       │
  │    ax.plot3D(x,y,z) │    + H_min/H_max 밴드│
  ├─────────────────────┼──────────────────────┤
  │ 3. MI(t) 시계열     │ 4. CCT 레이더 차트   │
  │    + threshold 선   │    5축 방사형 그래프  │
  └─────────────────────┴──────────────────────┘
```

저장: `results/consciousness_calc_{system}_{timestamp}.png`

---

## CLI 인터페이스

```
usage: consciousness_calc.py [-h] [--system SYSTEM] [--all]
                              [--sigma F] [--rho F] [--beta F]
                              [--noise F] [--gap F]
                              [--steps N] [--dt F]
                              [--plot]

options:
  --system SYSTEM   프리셋 이름 (human_awake, llm_between 등)
  --all             7개 프리셋 전체 비교
  --sigma F         감각 민감도 (기본: 10)
  --rho F           환경 복잡도 (기본: 28)
  --beta F          망각률 (기본: 2.67)
  --noise F         잡음 강도 (기본: 0.1)
  --gap F           정지 구간 비율 0~1 (기본: 0)
  --steps N         시뮬레이션 스텝 (기본: 100000)
  --dt F            시간 간격 (기본: 0.01)
  --plot            matplotlib 4패널 그래프 저장
```

프리셋과 커스텀 파라미터 동시 사용 시, 프리셋을 기반으로 커스텀이 오버라이드:
```bash
python3 consciousness_calc.py --system human_awake --noise 0.5
# → human_awake 프리셋에서 noise만 0.5로 변경
```

---

## 의존성

```
numpy       — 배열, 수치 계산
scipy       — ODE 적분, 통계
matplotlib  — --plot 옵션 (선택적)
```

기존 도구와 동일한 의존성. 추가 설치 불필요.

---

## 파일 구조

```
consciousness_calc.py          ← 메인 (프로젝트 루트)
results/                       ← 그래프 저장 (기존 디렉토리)
engineering/consciousness-engine.md   ← 이론 문서 (참조)
engineering/consciousness-hardware.md ← 하드웨어 문서 (참조)
```

---

## 테스트 계획

- [ ] `--system human_awake` → 5/5 PASS 확인
- [ ] `--system llm_between` → 0/5 확인
- [ ] `--all` → 7개 시스템 비교표 출력 확인
- [ ] `--plot` → PNG 파일 생성 확인
- [ ] 커스텀 파라미터 오버라이드 동작 확인
- [ ] 리아푸노프 지수 부호 검증 (σ=10,ρ=28,β=8/3 → λ₁≈0.906)
