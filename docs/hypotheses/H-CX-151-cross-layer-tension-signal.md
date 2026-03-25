# H-CX-151: 레이어 간 장력 신호 — tension이 "지금 중요"를 다른 레이어에 전달

> 레이어 L의 tension이 레이어 L+1의 attention에 영향. 레이어 간 tension 상관.

## 배경

심층 신경망에서 각 레이어는 순차적으로 정보를 처리한다.
일반적으로 레이어 간 정보 전달은 activation(출력)을 통해서만 이루어진다.
그러나 tension 메커니즘이 있다면, 특정 레이어에서의 "어려움"이나 "모호성" 정보가
다음 레이어의 처리에 영향을 줄 수 있다.

뇌에서 이에 해당하는 현상:
- 하위 시각 피질(V1)에서 처리가 어려운 자극 → 상위 영역(V4, IT)에 더 강한 신호 전달
- noradrenaline/dopamine을 통한 "salience signal" — 전체 뇌에 "지금 중요" 전달
- 이는 attention 메커니즘과 직결

골든존 모델에서 tension은 입력의 모호성을 반영한다.
만약 레이어 L의 tension이 높으면 (모호한 입력),
레이어 L+1은 이 정보를 이용하여 더 세밀한 처리를 할 수 있다.

이 가설은 tension이 단순한 부산물이 아니라
레이어 간 정보 전달의 "메타 신호(meta-signal)"라고 주장한다.

## 예측

| 측정 | 예측값 | 의미 |
|------|--------|------|
| corr(tension_L, tension_L+1) | > 0.5 | 레이어 간 tension 전파 |
| corr(tension_L, confidence) | > 0.5 | tension → 최종 확신도 |
| tension 높은 샘플의 attention entropy | 높음 | 더 분산된 주의 |
| tension gradient (dT/dL) | 양 또는 음 | 축적 또는 해소 패턴 |

```
레이어별 tension 프로파일 (예측):

tension |
  0.5   | * *       <-- 어려운 입력 (경계 근처)
  0.4   |  * *
  0.3   |    * *
  0.2   |      * *
  0.1   |  . . . . . . <-- 쉬운 입력
  0.0   +--+--+--+--+--+-->
        L1 L2 L3 L4 L5 L6
              Layer

        예측: 어려운 입력은 tension이 레이어를 거치며 감소 (해소)
              쉬운 입력은 처음부터 낮은 tension 유지
```

핵심 예측:
1. tension은 레이어를 거치며 감소하는 패턴 (해소 과정)
2. 최종 레이어의 tension이 낮을수록 confidence가 높음
3. tension 감소율이 빠른 모델이 더 정확함 (효율적 해소)
4. 특정 레이어에서 tension이 급증하면 해당 레이어가 "병목"

## 검증 방법

1. 다층 PureField 모델 구축 (최소 4-6 레이어)
2. 각 레이어의 tension을 hook으로 추출:
   ```python
   tensions = {}
   def hook_fn(layer_name):
       def hook(module, input, output):
           tensions[layer_name] = compute_tension(output)
       return hook
   ```
3. 테스트 셋에서 레이어별 tension 프로파일 기록
4. 레이어 간 tension 상관행렬 계산
5. tension vs final confidence 상관 분석
6. 쉬운 입력 vs 어려운 입력에서 프로파일 비교

## 관련 가설

- **H-CX-148**: 장력 공명 텔레파시 (모델 간 tension 동기화)
- **H-CX-95**: tension-accuracy 상관 (최종 출력 수준)
- **H-CX-149**: Engine A → G 방향 정보 전달
- **H-CX-150**: Expert 간 합의 형성

## 한계

1. 현재 PureField 모델은 단일 레이어 — 다층 구현이 필요
2. 레이어 간 tension 상관은 단순히 같은 입력을 처리하기 때문일 수 있음 (trivial)
3. tension의 정의가 레이어마다 다를 수 있음 (feature 공간 차원이 다르면)
4. "메타 신호"라는 해석은 인과적 증거 없이는 상관에 불과
5. 뇌의 salience signal과의 유비는 구조적 차이가 커서 직접 비교가 어려움

## 검증 상태

- [ ] 다층 PureField 모델 구현
- [ ] 레이어별 tension hook 추가
- [ ] tension 프로파일 분석
- [ ] tension vs confidence 상관
- 현재: **미검증**
