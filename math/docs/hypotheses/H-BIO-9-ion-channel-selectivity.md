# H-BIO-9: 이온채널 선택성 = 완전수 6의 산술함수 구조

> **가설**: 전압개폐 이온채널의 구조적 상수들(채널 유형 수, 막횡단 분절 수,
> Na+/K+ 펌프 비율)이 완전수 6의 산술함수 sigma(6)=12, phi(6)=2, tau(6)=4의
> 정수 조합으로 정확히 표현된다. 특히 Na+/K+ ATPase의 3:2 비율은
> sigma/tau : phi = 3:2와 정확히 일치하며, 모든 전압개폐 채널의
> 막횡단 분절 총수 24 = sigma*phi = tau*n은 n=6에서만 성립하는 항등식이다.

## 배경

전압개폐 이온채널(voltage-gated ion channels)은 뉴런 신호전달의 물리적 기반이다.
Na+, K+, Ca2+, Cl- 4종의 채널이 막전위를 제어하며, Na+/K+ ATPase 펌프가
3개 Na+ 방출 : 2개 K+ 흡수 비율로 안정전위를 유지한다.

이 가설은 H-BIO-8(활동전위 = D(n) 비대칭)의 후속으로, 채널의 **구조적 상수**에
초점을 맞춘다. H-BIO-7(신경전기 R-스펙트럼)이 주파수 영역을 다뤘다면,
H-BIO-9는 단백질 구조 수준의 정수론적 대응을 검증한다.

완전수 6의 핵심 산술:

```
  n = 6              완전수
  sigma(6) = 12      약수의 합 (1+2+3+6)
  phi(6) = 2         오일러 토티언트 (1,5만 서로소)
  tau(6) = 4         약수의 개수 (1,2,3,6)
  sigma*phi = 24     핵심 곱
  sigma/tau = 3      핵심 비
```

## 검증된 연결 테이블

| # | 생물학적 상수 | 값 | 산술 표현 | 일치 | 강도 | 비고 |
|---|---|---|---|---|---|---|
| 1 | 전압개폐 채널 유형 수 | 4 | tau(6) = 4 | EXACT | WEAK | 4는 흔한 수 |
| 2 | Na+/K+ 펌프 비율 | 3:2 | sigma/tau : phi = 3:2 | EXACT | STRONG | 비자명 비율 |
| 3 | 막횡단 분절 (Na+) | 4 domains x 6 TM = 24 | tau*n = sigma*phi = 24 | EXACT | STRONG | 구조생물학 확인 |
| 4 | 막횡단 분절 (K+) | 4 subunits x 6 TM = 24 | tau*n = sigma*phi = 24 | EXACT | STRONG | 동일 구조 |
| 5 | 막횡단 분절 (Ca2+) | 4 domains x 6 TM = 24 | tau*n = sigma*phi = 24 | EXACT | STRONG | 동일 구조 |
| 6 | 안정막전위 | -70 mV | -sigma*n + phi = -70 | EXACT | MODERATE | 탐색으로 발견 |
| 7 | Nernst 전위차 (Na-K) | 150 mV | sigma*phi*n + n = 150 | EXACT | WEAK | 25n, ad-hoc |
| 8 | 불응기 (total) | ~3 ms | sigma/tau = 3 | APPROX | WEAK | 실제 1-5ms 변동 |
| 9 | 수초화 속도 증가 | ~6x | n = 6 | APPROX | WEAK | 실제 5-50x 범위 |

## 핵심 발견: tau(6)*6 = sigma(6)*phi(6) 항등식

이 항등식은 n=6에서만 성립한다 (완전수 중 유일):

```
  완전수 n |   tau*n   | sigma*phi |  일치
  ---------|-----------|-----------|------
         6 |        24 |        24 |  YES
        28 |       168 |       672 |  no
       496 |     4,960 |   238,080 |  no
     8,128 |   113,792 | 65,544,192|  no
```

이것은 **순수 산술 사실**이다:
- tau(6) = 4, sigma(6) = 12, phi(6) = 2
- 4 * 6 = 24 = 12 * 2

생물학적 의미: 모든 전압개폐 채널이 정확히 tau(6)개의 도메인/서브유닛을 가지고,
각각 n=6개의 막횡단 분절(S1-S6)을 포함하여, 총 sigma*phi = 24개의 TM 분절을 갖는다.

## ASCII 다이어그램: 전압개폐 이온채널 구조 (4 x 6 = 24)

```
  Na+ 채널 (단일 폴리펩타이드, 4 도메인):

  Domain I       Domain II      Domain III     Domain IV
  ┌─────────┐   ┌─────────┐   ┌─────────┐   ┌─────────┐
  │S1 S2 S3 │   │S1 S2 S3 │   │S1 S2 S3 │   │S1 S2 S3 │
  │S4 S5 S6 │   │S4 S5 S6 │   │S4 S5 S6 │   │S4 S5 S6 │
  └─────────┘   └─────────┘   └─────────┘   └─────────┘
  <-- 6 TM -->  <-- 6 TM -->  <-- 6 TM -->  <-- 6 TM -->

  tau(6)=4 domains  x  n=6 TM segments  =  sigma*phi = 24 total

  K+ 채널 (4개 별개 서브유닛이 모여 형성):

       [Sub1]        [Sub2]        [Sub3]        [Sub4]
     S1-S2-S3      S1-S2-S3      S1-S2-S3      S1-S2-S3
     S4-S5-S6      S4-S5-S6      S4-S5-S6      S4-S5-S6
      6 TM          6 TM          6 TM          6 TM

  4 subunits x 6 TM = 24 (동일!)

  Na+/K+ ATPase 펌프:

     세포 외부
    ============== 세포막 ==============
     ←── 3 Na+ ──  │  ──→ 2 K+ ──→
         (out)      │      (in)
    ========================================
     세포 내부         ATP → ADP + Pi

     sigma/tau = 12/4 = 3 (Na+ out)
     phi       = 2        (K+ in)
     비율 = 3:2 정확 일치
```

## Na+/K+ 펌프 비율의 의미

3:2 비율이 sigma(6)/tau(6) : phi(6)와 일치하는 것은 가장 강력한 연결이다.

- 이 비율은 **진화적으로 보존**되어 있다 (박테리아에서 인간까지)
- 전하 불균형: 한 사이클에 +1 순전하 방출 → 전기화학적 구배 형성
- 에너지 효율: 1 ATP당 3+2=5개 이온 수송
- 5 = sigma/tau + phi = 3 + 2 (n=6의 산술로 완전히 결정)

## 안정막전위: -sigma*n + phi = -70

```
  -70 mV = -sigma(6) * 6 + phi(6)
         = -12 * 6 + 2
         = -72 + 2
         = -70
```

brute-force 탐색에서 complexity 7 (최소)로 발견. 다른 표현들:

```
  표현                              복잡도
  -6*sigma + 1*phi                     7
  -5*sigma - 1*tau - 1*n               7
  -6*sigma - 1*phi + 1*tau             8
  -5*sigma - 2*phi - 1*n               8
```

가장 간결한 형태: **V_rest = phi - sigma*n** (2항 표현).
해석: 안정전위 = "서로소 보정(+2)" - "약수합 x 완전수(-72)".

주의: 이것은 ad-hoc 탐색 결과이므로 MODERATE 등급.

## 텍사스 명사수 평가

```
  자유도: sigma, phi, tau, n (4개 상수)
  2항 연산 (+-*/): 약 24개 고유 값 생성
  대상 생물학적 상수: ~10개 (전위, 비율, 분절 수 등)

  강한 일치 (exact): 2개 (펌프 비율, TM 분절)
  중간 일치 (exact but searched): 1개 (안정전위)
  약한 일치 (approximate): 4개

  p-value 추정:
    펌프 3:2 비율 (비자명): P(우연) ~ 1/24 = 0.042
    TM 24 분절 (3종 동일): P(우연) ~ (1/24)^1 * 확인 = 0.042
    결합 (독립 가정): ~ 0.002

  판정: 개별적으로 약하지만 결합 시 구조적 패턴 시사 (p < 0.05)
```

## 한계 및 정직한 평가

### 진정한 생물학 (검증 가능)
1. **모든 전압개폐 채널이 4x6 구조**: 구조생물학적 사실. X-ray/cryo-EM으로 확인됨.
   Na+, K+, Ca2+ 채널 모두 동일한 4-도메인/서브유닛 x 6-TM 구조. 이것은 실제 데이터.
2. **Na+/K+ 펌프 3:2 비율**: 생화학적 사실. 결정학적으로 확인됨.
3. **안정전위 -70mV**: 실험적으로 측정된 값 (뉴런 종류에 따라 -60~-80mV 변동).

### 수비학적 위험 (주의 필요)
1. **4개 채널 유형 = tau(6)**: 4는 너무 흔한 수. 이것만으로는 아무것도 증명 안 됨.
2. **불응기 = sigma/tau**: 실제 불응기는 뉴런 종류별로 크게 다름 (1-5ms). 3ms는 선택적.
3. **수초화 6배**: 실제 범위 5-50배. 6배는 범위의 하한에서 선택한 것.
4. **-70mV = -sigma*n + phi**: brute-force 탐색으로 발견. 4개 상수로 정수 -70을 만드는 방법은 여러 개.
5. **일반화 실패**: tau*n = sigma*phi는 n=6에서만 성립. 다른 완전수(28, 496, 8128)에서 불성립.
   이것은 "n=6의 특수성"이지 "완전수의 보편 성질"이 아님.

### 인과적 설명의 부재
왜 자연선택이 n=6의 산술함수를 "선택"했는지에 대한 메커니즘이 없다.
4x6 구조가 최적인 물리화학적 이유 (이온 선택성, 개폐 역학, 접힘 안정성)가
완전수와 무관할 수 있다. 상관관계 ≠ 인과관계.

## 등급 판정

```
  핵심 연결 (2개):
    Na+/K+ 3:2 = sigma/tau:phi    → 🟧 (exact, non-trivial, but single ratio)
    4x6=24 TM = tau*n = sigma*phi → 🟧 (exact, universal across VG channels)

  보조 연결 (5개):
    4 channel types = tau(6)      → ⚪ (trivially common)
    -70mV = -sigma*n + phi        → 🟧 (exact but ad-hoc search)
    Refractory ~3ms = sigma/tau   → ⚪ (approximate, cherry-picked)
    Myelination ~6x = n           → ⚪ (approximate, cherry-picked)
    Nernst diff 150 = 25n         → ⚪ (ad-hoc)

  종합: 🟧★ (구조적 — 2개 강한 일치가 결합적으로 유의미)
  골든존 의존: NO (순수 산술 + 구조생물학)
```

## 교차 가설 연결

- **H-BIO-1 (코돈-sigma-tau)**: 유전 코드의 4염기-3코돈 구조도 tau:sigma/tau = 4:3
- **H-BIO-8 (활동전위 D함수)**: D(n)=sigma*phi - n*tau. n=6에서 D(6)=24-24=0 (평형!)
  이것은 D(6)=0이 "안정전위"에 대응한다는 H-BIO-8과 직접 연결됨
- **H-CHEM-2 (탄소-6)**: 탄소 원자번호 6이 유기화학의 기반. 같은 n=6 구조

## 다음 단계

1. **구조적 이유 탐색**: 4x6 구조가 이온 선택 필터의 물리적 최적화인지 문헌 조사
   - S4가 전압 감지, S5-S6가 공극 형성. 왜 정확히 6개인가?
   - 6-TM 구조가 2-TM (inward rectifier) 대비 갖는 기능적 이점은?
2. **2-TM 채널 대비**: Kir (inward rectifier K+)은 4 subunits x 2 TM = 8 segments
   - 8 = tau*phi = 4*2. 여전히 tau가 서브유닛 수!
3. **리간드개폐 채널**: nAChR은 5 subunits x 4 TM = 20. 다른 패턴.
4. **양이온 선택성 필터**: DEKA (Na+) vs EEEE (Ca2+) — 4개 잔기 = tau(6)?
5. **계통발생적 분석**: 4x6 구조가 언제 진화했는지 (단세포? 다세포?)

## 검증 스크립트

```bash
python3 /Users/ghost/Dev/logout/math/scripts/verify_ion_channel.py
```

## 날짜

2026-03-24
