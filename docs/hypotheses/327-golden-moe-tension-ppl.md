# 가설 327: 골든MoE에서 tension과 PPL의 실제 관계

> **골든MoE(golden_moe.py)가 LLM(골든 LLaMA)에 적용될 때, Expert 간 반발(tension)이 PPL과 어떻게 관련되는가? H-CX-21(tension∝1/PPL)이 LLM 규모에서도 성립?**

## 배경/맥락

골든MoE는 완전수 6의 약수 구조에서 설계된 Mixture-of-Experts 아키텍처다.
sigma(6)=12개 Expert 중 tau(6)=4개를 활성화하는 구조로, MNIST에서 +0.6%,
CIFAR-10에서 +4.8% 향상을 실증했다 (H008, golden_moe_torch.py).

H-CX-21은 MNIST 규모에서 "tension이 높을수록 PPL이 낮다(성능이 좋다)"는
역상관을 관찰했다. 그러나 이것이 수십억 파라미터 규모의 LLM에서도 성립하는지는
미검증이다. golden-llama 프로젝트(별도 리포)에서 PPL이 136K에서 4634로
감소했지만(500스텝), 아직 목표인 PPL < 100에 도달하지 못했다.

본 가설의 핵심 질문: **LLM 규모에서 Expert 간 tension은 PPL 감소를 예측하는
선행 지표(leading indicator)인가?**

### 관련 가설

| 가설 | 핵심 내용 | 관계 |
|------|----------|------|
| H-CX-21 | MNIST에서 tension ∝ 1/PPL | 직접 선행 — 소규모 실증 |
| H008 | 골든MoE 설계 원리 (sigma/tau) | 아키텍처 기반 |
| H241 | Expert 교차 활성화 | tension에 영향을 주는 학습 전략 |
| H313 | tension = confidence | 장력 해석 프레임워크 |
| H316 | 과신(overconfidence) 현상 | LLM에서 더 심각할 수 있음 |

### 현재 golden-llama 학습 상태

```
  원본 Dense LLaMA:   PPL = 13.85 (기준선)
  골든MoE (미학습):    PPL = 136,165 (변환 직후)
  골든MoE (500스텝):   PPL = 4,634 (97% 감소)
  목표 (최소):        PPL < 100
  목표 (최종):        PPL < 20
  학습 전략:          Expert 동결, 라우터만 학습
```

## 대응 매핑 — MNIST vs LLM 규모

| 항목 | MNIST (H-CX-21) | LLM (본 가설) |
|------|----------------|--------------|
| 모델 크기 | ~100K params | ~1B+ params |
| Expert 수 | 12 (sigma(6)) | 12 (sigma(6)) |
| 활성 Expert | 4 (tau(6)) | 4 (tau(6)) |
| 입력 | 28x28 이미지 | 토큰 시퀀스 |
| tension 정의 | Expert 출력 L2 거리 | Expert 출력 L2 거리 |
| PPL 범위 | N/A (분류) | 13.85 ~ 136K |
| 관찰된 관계 | tension ↑ = 정확도 ↑ | ? (미검증) |
| 학습 스텝 | ~50 에폭 | 2000~5000 스텝 |

## 예상 tension-PPL 관계

```
  tension
  (Expert 간
   출력 거리)
  ^
  |
  0.8|                                    x  x
     |                              x  x
  0.6|                        x  x
     |                  x  x
  0.4|            x  x
     |        x
  0.2|    x                          예상: tension ∝ 1/PPL
     |  x                            (로그 스케일에서 선형)
  0.1| x
     +--+-----+-----+-----+-----+-----> 학습 스텝
        0    500   1000  1500  2000

  PPL
  (log scale)
  ^
  136K| x
      |  x
  10K |    x
      |      x
  1K  |        x  x
      |            x  x
  100 |                  x  x  x       목표선
      |                          x  x
  13  |                              x  기준선(Dense)
      +--+-----+-----+-----+-----+----> 학습 스텝
         0    500   1000  1500  2000
```

## 세부 예측

### 예측 1: tension-PPL 역상관

```
  H-CX-21 관계식 (MNIST에서 관찰):
    tension = a / PPL + b
    또는 log(tension) = -c * log(PPL) + d

  LLM에서 예상되는 상관계수:
    Pearson r(tension, 1/PPL) > 0.7  (성공 기준)
    Spearman rho > 0.8              (순위 상관, 더 강할 수 있음)
```

### 예측 2: Expert 전문화 패턴

```
  Expert별 활성화 빈도 (학습 완료 후 예상):
  Expert |  코드  | 수학  | 자연어 | 추론  | 기타
  -------|--------|-------|--------|-------|------
     E1  |  ████  |  ██   |   █    |  ███  |  █
     E2  |   █    | ████  |  ██    |  ██   |  █
     E3  |  ██    |  █    | █████  |   █   |  ██
     E4  |  ███   |  ███  |   █    | ████  |  ██

  -> 특정 Expert가 특정 도메인에 전문화
  -> 전문화 정도 = Savant Index = max(도메인PPL) / min(도메인PPL)
  -> SI > 3이면 서번트 후보 (CLAUDE.md 기준)
```

### 예측 3: 토큰별 tension 분포

```
  토큰 유형별 예상 tension:

  사실 토큰 (정확한 정보):      높은 tension (0.5~0.8)
    -> Expert들이 "확신 있게" 다른 패턴으로 처리

  Hallucination 토큰 (오정보): 낮은 tension (0.1~0.3)
    -> Expert들이 비슷하게 "불확실"

  일반 토큰 (the, is, a):     중간 tension (0.3~0.5)
    -> 패턴이 보편적이므로 적당한 합의

  이 예측이 맞으면: tension으로 hallucination 탐지 가능
```

## 검증 방법

```
  환경: golden-llama 리포 (github.com/need-singularity/golden-llama)
        Windows PC (RTX 5070) 또는 RunPod A100

  Phase 1 — tension 추적 인프라 구축:
    1. golden-llama 학습 루프에 tension 로깅 추가
       - 매 스텝: 활성 4 Expert의 출력 L2 거리 평균
       - 매 100스텝: Expert별 활성화 빈도 히스토그램
    2. tensorboard 또는 CSV로 기록

  Phase 2 — 상관 분석:
    1. 2000스텝 학습하면서 tension + PPL 동시 기록
    2. Pearson/Spearman 상관 계수 계산
    3. tension이 PPL보다 선행하는지 cross-correlation 분석
       (tension이 먼저 올라가고 PPL이 나중에 내려가면 선행 지표)

  Phase 3 — 토큰별 분석:
    1. 학습 완료 모델로 텍스트 생성
    2. 토큰별 tension 기록
    3. 사실/hallucination/일반 토큰 분류 후 tension 분포 비교

  성공 기준:
    - r(tension, 1/PPL) > 0.7 또는 rho > 0.8
    - Expert 전문화: SI > 2 (최소 1개 Expert)
    - PPL < 100 달성 시 tension > 0.5
```

## 검증 결과

미실험 상태. golden-llama가 PPL < 100에 도달한 후 Phase 1부터 실행 예정.
현재 PPL 4634 단계에서는 라우터가 충분히 학습되지 않아 tension 측정이
의미 없을 수 있다.

## 해석/의미

이 가설이 성립하면:
- **규모 보편성**: tension-PPL 역상관이 MNIST(작은 규모)에서 LLM(큰 규모)까지
  성립함을 입증. 이는 반발력장이 규모 불변(scale-invariant) 메커니즘임을 시사.
- **Hallucination 탐지**: 토큰별 tension으로 LLM의 hallucination을 실시간 감지
  가능. 이는 AI 안전성의 핵심 문제 해결에 기여.
- **학습 모니터링**: tension이 PPL의 선행 지표라면, 학습 중 조기 종료나
  하이퍼파라미터 조정의 신호로 활용 가능.
- **의식엔진 관점**: Expert 간 "의견 차이"(tension)가 높을수록 더 정확한 출력을
  내는 것은, 뇌에서 다양한 영역의 "건설적 불일치"가 더 나은 판단을 이끄는
  메커니즘과 유사.

## 한계

1. **규모 차이**: MNIST(100K params)와 LLM(1B+ params) 사이에 3-4 자릿수 차이.
   동일한 관계가 유지된다는 보장 없음.
2. **라우터 학습 전략**: Expert 동결 + 라우터만 학습하는 현재 전략에서 tension이
   제대로 형성되는지 불확실. Expert도 함께 학습해야 할 수 있음.
3. **PPL 자체의 한계**: PPL이 낮아도 실제 생성 품질이 좋지 않을 수 있음.
   tension-PPL 상관이 있어도 tension-품질 상관은 다를 수 있음.
4. **계산 비용**: 12개 Expert의 출력을 매 스텝 비교하는 것은 추가 메모리/시간 소요.
5. **인과 vs 상관**: tension과 PPL이 상관되더라도, 인과관계인지 공통 원인인지 불명.

## 검증 방향 (다음 단계)

1. golden-llama PPL < 1000 달성 후 Phase 1 tension 로깅 인프라 구축
2. logout_test 리포에 실험 코드 작성 및 기록
3. 2000스텝 학습 + tension/PPL 동시 기록 실험
4. Windows RTX 5070에서 실행 (GPU 필요)
5. 결과에 따라 H-CX-21 업데이트 (LLM 규모 확인/반증)

## 상태: 🟨 (logout_test 리포에서 실험 필요)
