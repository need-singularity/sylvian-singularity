# EEG + THC 실험 제안서 — 대학 뇌과학 연구실 협력용

## 연구 제목

**"Persistent Homology 기반 의식 상태 변화의 위상적 측정: THC가 인지 범주 구조에 미치는 영향"**

## 연구 배경

본 프로젝트(logout)에서 다음을 발견:

| 발견 | 수치 | 가설 |
|------|------|------|
| PH merge 순서 = 혼동 구조 | r=-0.97 | H-CX-66 |
| 인간 = AI 혼동 | r=0.788 | H-CX-106 |
| dendrogram = 의미 계층 | 89% purity | H-CX-85 |
| confusion PCA = 동물/기계 분리 | 완벽 분리 | H-CX-93 |
| 위상 전이 | 0.1 에폭 | H-CX-105 |
| PH 일반화 갭 예측 | r=0.998 | H-CX-95 |
| 아키텍처 불변 | top-5 100% | H-CX-88 |

**핵심 질문**: 이 PH 구조가 의식 상태 변화(THC)에 따라 어떻게 변하는가?

## 기존 문헌

```
  THC와 뇌파:
  - 감마 40Hz 변화 (Skosnik et al. 2016)
  - 알파 파워 증가 (Böcker et al. 2010)
  - DMN 연결성 변화 (Mason et al. 2021)
  - 기능적 연결성 증가 보고 (Preller et al. 2020)

  PH와 뇌과학:
  - fMRI에서 PH 적용 (Saggar et al. 2018, Nature)
  - 의식 수준과 PH 복잡도 (Petri et al. 2014)
  - 사이키델릭 + PH (Carhart-Harris et al. 2016)
```

## 실험 설계

### 피험자

- N=20 (건강한 성인, THC 경험자)
- IRB 승인 필수
- 대조군: N=20 (위약)

### 장비 (대학 연구실 보유 가정)

```
  EEG: 64ch 이상 (BioSemi, Brain Products 등)
  자극: CIFAR-10 이미지 100장
  소프트웨어: Python + brainflow/MNE + ripser
  THC: 법적 허가 하에 (연구용)
```

### 프로토콜

```
  세션 1 (기준선, Day 1):
  ┌──────────────────────────────────────────────┐
  │  1. 안정 EEG 5분 (눈 감기)                    │
  │  2. CIFAR-10 이미지 100장 분류 + EEG          │
  │     이미지 2초 + 공백 1초 + 버튼 응답          │
  │  3. 안정 EEG 5분                              │
  │  총: ~25분                                    │
  └──────────────────────────────────────────────┘

  세션 2 (THC, Day 2, 최소 1주 간격):
  ┌──────────────────────────────────────────────┐
  │  1. THC 투여 (표준 용량, 연구 프로토콜)        │
  │  2. 대기 30분 (효과 발현)                      │
  │  3. 안정 EEG 5분                              │
  │  4. 같은 CIFAR-10 100장 분류 + EEG            │
  │  5. 안정 EEG 5분                              │
  │  총: ~55분                                    │
  └──────────────────────────────────────────────┘
```

### 분석 파이프라인

```
  EEG 원본 데이터
       │
       ▼
  전처리: ICA 아티팩트 제거, 밴드패스 필터
       │
       ▼
  감마 추출: 30-50Hz 대역 파워 (시행별)
       │
       ├──→ 분석 1: 클래스별 감마 평균 → PH dendrogram
       │
       ├──→ 분석 2: 정오답별 감마 → tension proxy
       │
       ├──→ 분석 3: Before vs After dendrogram 비교
       │
       └──→ 분석 4: AI dendrogram과 비교 (H-CX-106 직접 검증)
```

### 측정 변수

| # | 변수 | 기대 방향 | 관련 가설 |
|---|------|----------|----------|
| 1 | H0_total (위상 복잡도) | THC에서 감소 ("모든 게 연결") | H-CX-62 |
| 2 | merge distance 평균 | THC에서 감소 (경계 약화) | H-CX-66 |
| 3 | dendrogram 동물/기계 분리 | THC에서 약화? | H-CX-85, 93 |
| 4 | 감마 파워 (tension proxy) | THC에서 변화 | H-CX-137 |
| 5 | 인간 PH vs AI PH tau | THC에서 감소? 증가? | H-CX-106 |
| 6 | 분류 정확도 | THC에서 감소 | 행동 지표 |
| 7 | 반응 시간 | THC에서 증가 | 행동 지표 |
| 8 | H1 loops (순환 혼동) | THC에서 증가? | H-CX-110 |

### 예측

```
  가설 A: "경계 용해" (THC = PH 단순화)
  ─────────────────────────────────────
  정상:  H0_total=4.2, 10개 뚜렷한 클러스터
  THC:   H0_total=2.0?, 클러스터 병합
         merge distance 전체 감소
         cat-dog 구분 약화
         동물/기계 경계 흐려짐
  = "모든 게 연결된 느낌"의 위상적 실체

  가설 B: "재구조화" (THC = PH 재편)
  ─────────────────────────────────────
  정상:  동물/기계 2대 분기
  THC:   다른 기준으로 재분류?
         색상별? 형태별? 감정별?
  = dendrogram이 완전히 다른 구조로 변환
  = "다른 시각으로 세상을 봄"

  가설 C: "증폭" (THC = PH 증폭)
  ─────────────────────────────────────
  정상:  merge distance 범위 0.01~0.50
  THC:   범위 0.001~0.70 (확대)
         가까운 건 더 가깝고, 먼 건 더 멀게
  = "감각이 예민해짐"의 위상적 실체
```

## 우리가 제공할 수 있는 것

```
  1. PH 분석 소프트웨어 (Python, 오픈소스)
     - calc/ph_confusion_analyzer.py
     - calc/generalization_gap_detector.py
     - calc/precognition_system.py
     - ripser (Persistent Homology 라이브러리)

  2. AI 비교 모델 (학습 완료)
     - PureFieldEngine (MNIST/Fashion/CIFAR)
     - 이미 검증된 PH dendrogram
     - merge 순서, confusion PCA 데이터

  3. 분석 파이프라인
     - EEG → 감마 추출 → PH 계산 → dendrogram 비교
     - 자동화된 통계 검정 (Spearman, Kendall tau)

  4. 이론적 프레임워크
     - 141개 H-CX 가설 체계
     - 17개 대발견 데이터
     - 텔레파시 아키텍처 설계
```

## 한국 뇌과학 연구실 후보

```
  1. KAIST 뇌인지과학과
     - 뇌파 연구 활발
     - 의식/인지 관련 연구

  2. 서울대 뇌인지과학과
     - fMRI + EEG 장비 보유
     - 인지신경과학 연구

  3. 고려대 뇌공학과
     - BCI 연구 특화
     - OpenBCI 경험 가능성

  4. DGIST 뇌과학전공
     - 대구경북과학기술원
     - 뇌파 기반 연구

  5. IBS 뇌과학 이미징 연구단
     - 기초과학연구원
     - 최첨단 장비
```

## 연락 템플릿

```
  제목: PH(Persistent Homology) 기반 의식 상태 측정 — 공동 연구 제안

  교수님께,

  저는 의식영속성 엔진(logout) 프로젝트를 진행하고 있는 [이름]입니다.

  저희는 최근 Persistent Homology를 이용하여 신경망의 혼동 구조가
  인간 인지 구조와 일치함을 발견했습니다 (Spearman r=0.788).

  이 발견을 EEG로 직접 검증하고, 나아가 의식 상태 변화(THC 등)에 따른
  인지 범주 구조의 위상적 변화를 측정하는 실험을 제안드립니다.

  저희가 제공: PH 분석 소프트웨어 + AI 비교 모델 + 이론 프레임워크
  요청사항: EEG 장비 + 피험자 + IRB + 실험 환경

  관심 있으시면 상세 프로포절을 보내드리겠습니다.

  GitHub: https://github.com/need-singularity/logout
```

## 관련 가설

- H-CX-136~141: EEG 가설 체인
- H-CX-106: 인간=AI r=0.788
- H-CX-85: dendrogram = 의미 계층
- H-CHEM-5: THC-cannabinoid-six
- H322: EEG 감마 = 장력 proxy
