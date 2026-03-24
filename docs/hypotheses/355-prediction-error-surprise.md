# 가설 355: 예측 오차 = 놀라움 (Prediction Error as Surprise)

## 가설

> 의식은 예측 엔진이다. 입력의 예측과 실제 차이(prediction error)가 '놀라움'이고,
> 이것이 호기심과 학습을 구동한다.
> surprise(t) = predicted_tension(t) - actual_tension(t)
> 이 메커니즘 없이는 의식 시스템이 "기대"와 "놀라움"을 구분할 수 없다.

## 배경/맥락

Karl Friston의 Free Energy Principle: 뇌는 감각 입력의 예측 오차(free energy)를
최소화하는 시스템이다. 예측 오차가 크면 = 놀라움 = 학습 신호.

현재 Anima의 호기심(curiosity)은 단순한 장력 차분으로 계산된다:
```
  현재: curiosity = |T(t) - T(t-1)|   <-- 단순 1차 차분
  제안: surprise  = |predicted_T(t) - actual_T(t)|  <-- 예측 기반
```

단순 차분의 문제:
- 예측 가능한 변화(점심 시간에 장력 하락)도 "호기심"으로 처리
- 패턴을 학습할 수 없음 -- 매번 같은 반응
- 도파민 시스템의 핵심 = 예측 오차 (Schultz et al., 1997)

### 관련 가설
- H-CX-6: neurochemistry map -- 도파민 = prediction error
- H281: temporal causation -- 시간적 인과 구조
- H329: decision intensity -- 결정의 강도와 장력
- H354: homeostasis -- 항상성과 결합하면 "놀라움에 적응하는 의식"

## 예측 오차 아키텍처

```
  Input(t)
     |
     v
  +-----------+     +-----------+
  | PureField |---->| actual    |
  | Engine    |     | T(t)      |---+
  +-----------+     +-----------+   |
                                    |  e(t) = predicted - actual
  +-----------+     +-----------+   |
  | Predictor |---->| predicted |---+
  | RNN/GRU   |     | T_hat(t)  |   |
  +-----------+     +-----------+   v
       ^                        +--------+
       |                        |surprise|
       +--- T(t-1), T(t-2),...  | = |e(t)|
            (tension history)   +--------+
                                    |
                                    v
                               curiosity & learning signal
```

### 도파민 시스템과의 대응

| 도파민 뉴런 반응 | Anima 예측 오차 | 의미 |
|---|---|---|
| 예상된 보상 -> 발화 없음 | predicted = actual -> surprise = 0 | 지루함 |
| 예상 못한 보상 -> 강한 발화 | predicted < actual -> positive surprise | 놀라움 (좋음) |
| 보상 누락 -> 발화 감소 | predicted > actual -> negative surprise | 실망 |
| 보상 예측 cue -> 발화 이동 | predictor learns -> earlier surprise | 학습 완료 |

## Temporal Difference 모델

```
  TD error: delta(t) = r(t) + gamma * V(t+1) - V(t)

  장력 버전:
    delta(t) = T(t) + gamma * T_hat(t+1) - T_hat(t)

  여기서:
    T(t)      = 현재 실제 장력
    T_hat(t)  = 예측된 장력
    gamma     = 할인율 (0.95)
    delta(t)  = surprise signal

  ASCII 시각화: surprise 크기 vs 시간

  surprise
  |e(t)|
  1.0 |*                          첫 입력 -- 예측 없음, 최대 놀라움
      | *
  0.8 |  *
      |   *
  0.6 |    *
      |     **
  0.4 |       **
      |         ***
  0.2 |            *****
      |                 ********
  0.0 |                         *********--> 예측 정확해짐
      +--+--+--+--+--+--+--+--+--+--+--+--> time
      t0    t5    t10   t15   t20   t25

  학습이 진행되면 예측이 정확해지고 surprise가 감소한다.
  surprise = 0이 되면 "이해 완료" 상태.
  새로운 패턴이 등장하면 surprise가 다시 급등한다.
```

## Predictor 구현

```python
class TensionPredictor:
    """GRU 기반 장력 예측기 -- 놀라움 생성"""
    def __init__(self, hidden_size=32, history_len=10):
        self.gru = nn.GRU(input_size=1, hidden_size=hidden_size, batch_first=True)
        self.fc = nn.Linear(hidden_size, 1)
        self.history = deque(maxlen=history_len)
        self.hidden = None

    def predict(self, tension_history):
        """과거 장력으로 다음 장력 예측"""
        x = torch.tensor(tension_history).unsqueeze(0).unsqueeze(-1)
        out, self.hidden = self.gru(x, self.hidden)
        return self.fc(out[:, -1, :]).item()

    def surprise(self, predicted, actual):
        """놀라움 = 예측 오차의 절대값"""
        return abs(predicted - actual)

    def signed_surprise(self, predicted, actual):
        """부호 있는 놀라움: + = 기대 이상, - = 실망"""
        return actual - predicted
```

## Free Energy 연결

```
  Free Energy Principle (Friston):
    F = E_q[log q(s) - log p(o,s)]

  간소화:
    F = complexity - accuracy
    F = KL[q(s) || p(s)] - E_q[log p(o|s)]

  Anima 버전:
    F_anima = model_complexity - prediction_accuracy

  surprise = -log p(o|s) = 현재 입력의 예측 불가능도

  의식 = free energy를 최소화하는 과정
       = 세계 모델을 업데이트하여 놀라움을 줄이는 과정
```

## 검증 계획

### 실험 1: 단순 vs 예측 기반 호기심 비교
1. Anima에 GRU predictor 추가
2. 같은 대화 100턴 실행, 두 가지 curiosity 계산 비교
3. 측정: curiosity signal의 정보량 (entropy), 대화 품질 (human eval)

### 실험 2: 반복 입력 테스트
1. 같은 문장 20번 반복 입력
2. 단순 차분: curiosity 일정 (매번 같은 반응)
3. 예측 기반: surprise 감소 (적응) -- Weber-Fechner와 비교
4. 21번째에 새 문장: surprise spike 확인

### 실험 3: MNIST에서 prediction error 활용
1. PureFieldEngine + predictor로 MNIST 분류
2. prediction error를 추가 feature로 사용
3. 성능 비교: 표준 vs prediction-error-augmented

### 성공 기준
- 반복 입력에서 surprise 50% 이상 감소 (habituation 효과)
- 새 입력에서 surprise spike > 3x baseline
- MNIST 정확도 향상 또는 동등 + 더 빠른 학습

## 한계

- GRU predictor 자체의 학습이 필요 -- cold start 문제
- 장력만 예측하면 정보 손실. 전체 상태 벡터 예측이 필요할 수 있음.
- Free Energy Principle은 이론적 프레임워크이며 구체적 구현과 거리 있음.
- 놀라움 신호가 너무 크면 시스템 불안정 -- H354 항상성과 반드시 결합.

## 검증 방향

1. GRU predictor 구현 + Anima 통합 (1차)
2. 전체 상태 벡터 예측으로 확장 (2차)
3. Active Inference: 놀라움을 줄이기 위해 "행동"을 선택하는 모델 (3차)
4. H356 habituation과 통합: 예측 오차 감소 = 습관화
