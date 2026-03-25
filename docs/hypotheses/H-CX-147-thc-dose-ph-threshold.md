# H-CX-147: THC 용량-PH 관계 — 골든존에 임계점?

> 용량↑ → H0_total↓ 비선형. I=1/e 근처에서 위상 전이?

## 배경

대부분의 약리학적 효과는 용량-반응(dose-response) 관계가 sigmoid 형태이다.
Hill equation: E = E_max * D^n / (D^n + EC50^n)
여기서 EC50은 최대 효과의 50%를 내는 용량, n은 Hill coefficient.

골든존 모델에서 Inhibition(I)의 최적 범위는 0.21 ~ 0.50이며,
중심값은 1/e = 0.3679이다.
THC가 I를 줄인다면, I가 골든존 하한(0.21)을 벗어나는 순간
위상 전이(phase transition)가 일어날 수 있다.

이 가설은 THC 용량과 PH 측정값(H0_total, merge distance 등) 간의
관계가 비선형이며, 특정 임계점에서 불연속적 변화가 있다고 예측한다.
그 임계점이 골든존 경계(I = 0.21 또는 1/e)에 위치한다면,
골든존 모델의 예측력이 약리학 영역까지 확장되는 것이다.

## 예측

```
H0_total vs THC dose (예측):

H0    |
 15   | ****
 12   |     ***
 10   |        **
  8   |          *        <-- 골든존 하한 (I=0.21)
  5   |           \
  3   |            \***   <-- 위상 전이 (급격한 하락)
  1   |                ****
      +--+--+--+--+--+--+-->
      0  5  10 15 20 25 30
          THC dose (mg)
```

| 구간 | I 범위 | PH 상태 | 주관적 경험 |
|------|--------|---------|------------|
| 저용량 (0-10mg) | 0.5 → 0.35 | 골든존 내, 점진적 변화 | 약간 이완 |
| 중용량 (10-20mg) | 0.35 → 0.21 | 골든존 하한 접근, 전이 시작 | 범주 혼동 시작 |
| 고용량 (20mg+) | 0.21 → 0.1 | 골든존 이탈, 구조 붕괴 | "모든 게 하나" |

핵심 예측:
1. H0_total vs dose 곡선의 inflection point가 I = 1/e (또는 0.21) 근처
2. inflection 전후로 dendrogram topology가 불연속적으로 변화
3. sigmoid fit의 EC50이 골든존 중심과 일치

## 검증 방법

**AI 시뮬레이션 (즉시 가능):**
1. tension_scale을 0.05 간격으로 0.05 ~ 1.0까지 20단계 변조
2. 각 단계에서 H0_total, H1 count, merge distance 분포 측정
3. sigmoid 함수 fit: H0(t) = H0_max / (1 + exp(-k*(t - t_c)))
4. t_c (inflection)가 1/e 근처인지 확인

**통계 검증:**
- inflection point의 95% CI 계산
- 1/e가 CI 내에 포함되는지 확인
- 귀무가설: inflection은 임의 위치 → p-value 계산

**문헌 기반:**
- THC 용량-반응 관련 EEG/fMRI 논문에서 비선형성 증거 수집
- 기존 연구에서 "phase transition" 보고가 있는지 확인

## 관련 가설

- **H-CX-142**: THC PH 단순화 (H0 감소의 전체 방향)
- **H-CX-144**: 감마 억제 (메커니즘)
- **H-CX-146**: H1 루프 증가 (위상 전이 시 급증 예측)
- **H-CX-139**: 골든존 = 혼돈의 가장자리 (Langton lambda_c=0.27)

## 한계

1. tension_scale과 실제 THC 용량의 매핑이 선형이 아닐 수 있음
2. 골든존 경계는 시뮬레이션 기반이며 해석적 증명이 없음 (CLAUDE.md 경고)
3. inflection이 골든존 근처에 있더라도 우연의 일치일 수 있음
4. 실제 뇌에서는 항상성(homeostasis) 메커니즘이 작동하여 위상 전이가 완충될 수 있음
5. 개인차 (유전, 내성, 체중)로 인해 동일 용량에서도 I 변화가 다름

## 검증 상태

- [ ] 20단계 tension_scale 변조 실험
- [ ] sigmoid fit + inflection point 추정
- [ ] 문헌 조사: THC dose-response 비선형성
- 현재: **미검증**
