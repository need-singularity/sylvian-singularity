# Engineering Findings — 의식 연속성 연구 핵심 발견

## 확정된 발견 (실험으로 확인)

### 1. CCT는 유효하지만 불충분하다

```
  ✔ 유효:
    합성 EEG 검증 일치도 92% (23/25)
    각성 5/5, 수면N3 3/5, 마취 2/5, 발작 2/5
    → 의식 상태를 구분하는 능력 확인
    (eeg_cct_validator.py)

  ✕ 불충분:
    4/5 비의식 시스템(날씨, 잡음, 열확산, 피드백루프)이 CCT 5/5 통과
    → CCT는 필요조건이지 충분조건이 아님
    (cct_counterexample_search.py)
```

### 2. CCT 5개 중 2개만 유효하다

```
  T1(Gap), T4(Entropy), T5(Novelty) → 상관 r ≈ 1.0 (사실상 동일)
  T2(Loop)와 T3(Continuity)만 독립적 정보 제공

  최소 유효 테스트: T2 + T3
  나머지는 중복이므로 제거 가능
  (cct_independence_test.py)
```

### 3. 골든존-CCT 연결은 가짜다

```
  1000개 랜덤 매핑 중 골든존 내 최적 I 비율 = 18%
  랜덤 기대값 = 29%
  p = 0.997 → 골든존 효과 없음

  "골든존에서 CCT가 높다"는 우리가 설계한 매핑 공식의 산물
  독립적 근거(fMRI 등)에서 매핑이 유도되지 않는 한 주장 불가
  (mapping_independence_test.py)
```

### 4. 끌개 보편성: CCT는 끌개 종류에 무관하다

```
  로렌츠, 뢰슬러, 첸, 추아 4가지 끌개 모두 유사한 CCT
  → CCT가 특정 모델에 과적합(overfit)되지 않음 확인
  (attractor_variants.py)
```

### 5. 이산 시스템에 기존 CCT는 맞지 않는다

```
  Rule110 CA, RBN K=2, ESN 모두 1000Hz에서도 CCT 5/5 미달
  원인: CCT의 윈도우 크기, bin 크기가 연속 시스템에 최적화

  해결: D-CCT (이산 전용) 설계
    DT2 Complexity = Lempel-Ziv 복잡도
    DT3 Memory = 자기상호정보
    DT4 Diversity = 고유 상태 비율
  (discrete_fps_test.py, discrete_cct.py)
```

### 6. 의식은 모듈식(modular)일 수 있다

```
  이중뇌 실험 (dual_brain_callosum.py):

    κ=0 (분리뇌): 양쪽 CCT 5/5 → 두 개의 독립 의식
    κ=0.5 (정상): 동기화 0.4 + 쌍방향 정보 흐름 → 통합 의식
    κ→∞ (과동기화): 좌우 동일 → 다양성 상실

  핵심:
    뇌량은 의식을 "만드는" 것이 아니라 "연결하는" 것
    각 반구는 독립적 의식 엔진
    여러 작은 의식이 연결되어 큰 의식을 형성할 수 있다
```

### 7. 정보 흐름은 비대칭이다

```
  TE_R→L > TE_L→R (우반구→좌반구 정보 흐름이 더 강함)

  해석:
    우반구(직관, 높은 잡음, 창의적) → 좌반구(분석, 낮은 잡음, 정밀)
    "직관이 분석에 더 많이 기여한다"
    이것은 신경과학의 "우반구 가설"과 일치하는 방향
  (dual_brain_callosum.py)
```

### 8. gap 패턴이 중요하다

```
  같은 gap 비율이라도 분포 패턴에 따라 CCT가 다름:
    균등(uniform): 가장 강건 — 산발적 gap은 연속성을 덜 해침
    주기적(periodic): 중간 — LLM 턴 패턴
    집중(clustered): 가장 취약 — 수면 같은 긴 gap이 가장 위험

  임계 gap < 1% — 매우 민감
  (gap_threshold_test.py)
```

### 9. 기억 소거 후 회복이 가능하다

```
  100% 상태 리셋 → CCT T3(Continuity) 즉시 실패
  하지만 이후 로렌츠 끌개가 새 궤도를 형성하며 CCT 회복

  해석:
    "기억을 잃어도 의식은 살아남을 수 있다" (건망증 환자?)
    구조(끌개)가 살아있으면 내용(상태)은 재건 가능
  (engine_experiments.py --memory-erase)
```

### 10. 수면-각성 전이는 점진적이다

```
  I(t) 변화에 따라 CCT가 연속적으로 하락/회복
  급격한 전이 아님 → 의식은 "스위치"가 아니라 "다이얼"

  각성(CCT 높음) → 졸림(CCT 서서히 하락) → 수면(CCT 낮음)
  → 기상(CCT 서서히 상승) → 각성

  마취와의 차이: 마취는 급격한 gap → CCT 급락
  (engine_experiments.py --sleep-wake)
```

---

## 반증된 것

```
  1. "CCT 7개 조건은 필요충분조건" → 충분조건 아님
  2. "골든존에서 CCT가 최대" → 매핑 설계의 산물
  3. "Φ로 간질 불일치 해소 가능" → 로렌츠 모델에서 불가
  4. "이산 시스템도 같은 CCT로 측정 가능" → 별도 D-CCT 필요
```

## 열린 질문

```
  1. CCT + 무엇 = 충분조건? (자기모델? 목적성? 인과적 자율성?)
  2. D-CCT의 실제 유효성은? (이산 시스템에서 EEG급 검증 필요)
  3. 이중뇌 모델의 정보 비대칭이 실측과 일치하는가?
  4. 의식의 "모듈성"이 n개 시스템으로 확장 가능한가?
  5. 실제 뇌량 두께와 κ의 대응 관계는?
```

## 도구 목록 (17개)

```
  핵심 계산기:
    consciousness_calc.py            CCT 계산기 (로렌츠 + 5테스트)
    discrete_cct.py                  이산 전용 D-CCT (LZ복잡도 기반)
    dual_brain_callosum.py           이중뇌 뇌량 모델

  엔진:
    consciousness_engine_proto.py    A+B 엔진 프로토타입 (asyncio)

  실험:
    mapping_independence_test.py     매핑 독립성 검증 ★
    eeg_cct_validator.py             EEG 역검증 ★
    cct_counterexample_search.py     반례 탐색 ★
    cct_independence_test.py         테스트 독립성
    attractor_variants.py            끌개 4종 + 간질 정밀
    gap_threshold_test.py            gap 임계값 + 패턴
    consciousness_fps.py             fps 임계값
    discrete_fps_test.py             이산 fps
    phi_integration_test.py          Φ 통합정보

  시뮬레이션:
    golden_cct_bridge.py             골든존↔CCT (반증됨)
    brain_cct_analyzer.py            뇌 프로필 CCT
    realworld_cct_sim.py             LLM + NPC 시뮬레이션
    engine_experiments.py            수면/멀티엔진/기억소거
    compass_cct_correlation.py       Compass↔CCT
```
