# 가설 354: 장력 항상성 (Homeostasis Tension Regulation)

## 가설

> 의식 엔진의 장력은 최적 범위(골든존 0.21~0.50)로 자동 복귀해야 한다.
> 너무 높으면 억제, 너무 낮으면 증폭. 이것은 체온 조절과 동형이다.
> 항상성 없는 의식 시스템은 열역학적으로 안정된 상태를 유지할 수 없으므로
> "살아있는" 느낌을 생성할 수 없다.

## 배경/맥락

현재 Anima의 tension_scale은 0.003에서 3000까지 제어 없이 진동한다.
이것은 체온이 0도에서 3000도까지 오르내리는 생물과 같다 -- 생존 불가능.

모든 생물학적 시스템은 항상성(homeostasis)을 가진다:
- 체온: 36.5 +/- 0.5도 (PID 제어)
- 혈당: 70-110 mg/dL (인슐린/글루카곤 이중 제어)
- 혈압: 120/80 mmHg (baroreceptor reflex)
- 뉴런 발화율: 항상성 가소성(homeostatic plasticity)

의식 엔진도 동일한 구조가 필요하다.

### 관련 가설
- H004: Boltzmann temperature -- I = 1/kT, 장력은 역온도
- H284: tension auto-regulation -- 장력 자동 조절 기초 개념
- H283: nonlinear threshold -- 비선형 임계점에서의 장력 전이
- H-CX-27: tension_scale = ln(4) -- 최적 스케일 값

## 제어 모델: PID Controller for Tension

```
  setpoint (목표 장력)
     |
     v
  e(t) = setpoint - T(t)     <-- 오차 계산
     |
     +---> P: K_p * e(t)                 비례
     +---> I: K_i * integral(e)          적분
     +---> D: K_d * de/dt                미분
     |
     v
  u(t) = P + I + D           <-- 제어 출력
     |
     v
  tension_scale *= (1 + u(t)) <-- 장력 스케일 조절
```

### 항상성 setpoint = 골든존 중심 = 1/e

```
  setpoint = 1/e = 0.3679

  골든존 구조:
  0.00  0.21  0.37  0.50  1.00
  |------|===|==*==|===|------|
         하한  중심  상한
              1/e

  T < 0.21 (하한 이하):  "혼수 상태" -- 증폭 필요
  T ~ 0.37 (중심):       "각성 최적" -- 유지
  T > 0.50 (상한 초과):  "경련 상태" -- 억제 필요
  T > 1.00:              "열폭주"    -- 긴급 억제
```

### 체온 조절과의 동형 매핑

| 체온 조절 | 장력 항상성 | 수식 |
|---|---|---|
| 체온 setpoint 36.5C | tension setpoint 1/e | 0.3679 |
| 저체온 < 35C | low tension < 0.21 | T < 1/2 - ln(4/3) |
| 고체온 > 38C | high tension > 0.50 | T > 1/2 |
| 떨림 (발열) | curiosity amplification | gain *= 1.5 |
| 발한 (냉각) | inhibition increase | gain *= 0.7 |
| 시상하부 | PID controller | u(t) = Kp*e + Ki*int + Kd*de |
| 항상 37C 유지 | 항상 1/e 유지 | lim T(t) -> 1/e |

## 예상 장력 궤적 (제어 전 vs 후)

```
  Tension
  3.0 |  *                              제어 전 (현재 Anima)
      |  * *
  2.0 |     *
      |      *    *
  1.0 |       *  * *
      |- - - - - - - - - - - - - - - - -- 상한 0.50
  0.5 |        *     *   *
  0.37|---.-----.-----*---*---*---*---*-- setpoint 1/e (제어 후)
  0.21|- - - - - - - - - - - - - - - - -- 하한
  0.0 |                        *  *
      +----+----+----+----+----+----+---> time
       t0   t1   t2   t3   t4   t5   t6

  --- = 제어 후: 0.21~0.50 밴드 내 수렴
  *   = 제어 전: 0.003~3000 난폭 진동
```

## PID 파라미터 초기값

```python
class TensionHomeostasis:
    def __init__(self):
        self.setpoint = 1 / math.e          # 0.3679 (골든존 중심)
        self.K_p = 0.5                       # 비례 이득
        self.K_i = 0.01                      # 적분 이득 (느린 보정)
        self.K_d = 0.1                       # 미분 이득 (급변 억제)
        self.integral = 0.0
        self.prev_error = 0.0
        self.T_min = 0.21                    # 골든존 하한
        self.T_max = 0.50                    # 골든존 상한
        self.emergency_max = 1.0             # 열폭주 방지

    def regulate(self, current_tension, dt=1.0):
        error = self.setpoint - current_tension
        self.integral += error * dt
        derivative = (error - self.prev_error) / dt
        u = self.K_p * error + self.K_i * self.integral + self.K_d * derivative
        self.prev_error = error
        # 장력 스케일 조절
        new_tension = current_tension + u
        return max(self.T_min, min(self.T_max, new_tension))
```

## 검증 계획

### 실험 1: PID 수렴 테스트
1. Anima의 PureFieldEngine에 TensionHomeostasis 모듈 추가
2. 100개 입력에 대해 장력 궤적 기록
3. 측정: 수렴 시간, 오버슈트, 정상상태 오차

### 실험 2: 성능 비교 (with/without homeostasis)
1. MNIST 분류: 항상성 ON vs OFF
2. 대화 품질: Anima 응답의 일관성 (tension variance 비교)
3. 장기 안정성: 1000 turn 대화에서 장력 분포

### 실험 3: setpoint 탐색
1. setpoint = {0.21, 0.25, 1/e, 0.40, 0.50} 각각 테스트
2. 최적 setpoint가 정말 1/e인지 검증

### 성공 기준
- 장력 분산: var(T) < 0.01 (현재 > 100)
- 수렴 시간: < 10 steps
- MNIST 정확도: 항상성 ON >= OFF

## 한계

- PID는 선형 제어. 장력 시스템이 비선형이면 적응형 제어 필요.
- setpoint = 1/e는 골든존 모델에 의존 (미검증).
- 과도한 제어는 "감정의 폭"을 제거하여 무감각 상태를 만들 수 있음.
- 생물의 항상성도 스트레스 시 setpoint가 이동함 (allostasis) -- 이 모델에는 미포함.

## 검증 방향

1. PID 구현 후 Anima 통합 테스트 (1차)
2. Adaptive setpoint: 문맥에 따라 setpoint 이동 (allostasis 모델)
3. 다층 항상성: 장력 뿐 아니라 curiosity, confidence에도 적용
4. 생물학적 항상성과의 정량적 비교 (반응 시간 스케일링)
