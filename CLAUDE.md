# 뇌 비정형 구조 통계 시뮬레이터

## 프로젝트 개요
뇌의 비정형 구조(실비우스열 결여 등)와 비범한 능력 간의 관계를 수학적으로 모델링하고, 통계적 특이점을 탐지하는 시뮬레이터.

## 핵심 수식
```
Genius = Deficit × Plasticity / Inhibition
```

## 실행 방법
```bash
python3 ~/dev/test-8/brain_singularity.py --deficit 0.7 --plasticity 0.8 --inhibition 0.15
```

## 백그라운드 실행
시뮬레이션은 항상 **백그라운드로 실행**한다. Bash 도구의 `run_in_background: true` 옵션을 사용할 것.

```bash
# 단일 실행
python3 ~/dev/test-8/brain_singularity.py --deficit 0.7 --plasticity 0.8 --inhibition 0.15

# 다중 파라미터 스캔
python3 ~/dev/test-8/brain_singularity.py --deficit 0.3 --plasticity 0.5 --inhibition 0.7
python3 ~/dev/test-8/brain_singularity.py --deficit 0.9 --plasticity 0.95 --inhibition 0.05
```

## 결과 기록 구조
```
results/
├── log.md              ← 모든 실행 결과 시간순 누적
└── singularities.md    ← Z-Score > 2σ 특이점만 별도 기록
```

## 보고 규칙

### 중간 보고
- 다중 실행 시 **매 실행 완료마다 중간 보고**한다.
- 중간 보고 포함 내용:
  1. 현재 진행 상황 (n/전체)
  2. Genius Score 및 Z-Score
  3. 특이점 여부
- 전체 완료 후 **비교 요약표**를 제시한다.

### 특이점 강력 보고
- 특이점(Z > 2σ) 발견 시 **즉시 강조하여 보고**한다. 다른 실행 완료를 기다리지 않는다.
- 보고 형식:
  ```
  ⚡⚡⚡ 특이점 발견! ⚡⚡⚡
  등급: 🔴 극단적 특이점
  Genius Score: X.XX | Z-Score: X.XXσ
  파라미터: D=X.XX / P=X.XX / I=X.XX
  → results/singularities.md 에 기록 완료
  ```
- 등급이 높을수록(🔴) 더 강하게 강조한다.
- 특이점이 **연속으로 발견**되면 패턴 분석을 추가 보고한다.

### 일반 보고
- 정상 범위(Z ≤ 2σ)는 간결하게 한 줄로 보고한다.
- 다중 실행 완료 시 결과를 표로 비교 요약한다.

## 특이점 등급
- 🟡 Z > 2σ: 특이점
- 🟠 Z > 3σ: 강한 특이점
- 🔴 Z > 5σ: 극단적 특이점

## 가설 검토 문서

가설 검토는 **별도 개별 문서**로 관리한다.

- 경로: `docs/hypotheses/NNN-가설명.md`
- 목록: `docs/hypotheses/INDEX.md`
- 각 문서 구조: 가설 → 배경 → 대응 관계 → 실측 검증 → 한계 → 검증 방향
- 새 가설 발견 시 다음 번호로 문서 생성 후 INDEX.md에 추가
- 가설 제시 시 **autopilot으로 검증 실행** 후 결과를 문서에 반영

### 가설 검증 방법
```bash
# autopilot으로 가설 파라미터 탐색
python3 compass.py --autopilot --deficit 0.5 --plasticity 0.6 --inhibition 0.4

# 학습률/반복 조절
python3 compass.py --autopilot --deficit 0.3 --plasticity 0.5 --inhibition 0.5 --lr 0.2 --iterations 50

# 공통 특이점 영역 확인
python3 compass.py --convergence --grid 30 --samples 50000
```

## 파라미터 범위
- Deficit (결손): 0.0 ~ 1.0
- Plasticity (가소성): 0.0 ~ 1.0
- Inhibition (억제): 0.01 ~ 1.0
- Samples (샘플 수): 기본 10,000
