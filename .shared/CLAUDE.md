# .shared/ — Cross-Repo Shared Infrastructure

> **이 폴더는 TECS-L에 원본이 있고, 타 리포는 심링크로 연결됩니다.**
> 타 리포: `.shared/ → ../TECS-L/.shared/`

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
  installed_tools.json   ← 설치 도구 레지스트리

  calc/                  ← 계산기 원본 (194+ files)
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

anima, sedi, brainwire,          (소비자)
n6-architecture, papers/
  .shared → ../TECS-L/.shared    ← 심링크
  calc → .shared/calc            ← 심링크 체인
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
