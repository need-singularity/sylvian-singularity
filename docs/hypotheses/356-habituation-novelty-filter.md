# 가설 356: 습관화 = 새로움 필터 (Habituation as Novelty Filter)

## 가설

> 반복되는 자극에 장력이 감소하고, 새로운 자극에만 높아진다.
> 이것은 습관화(habituation)이며, 의식이 '지루함'을 느끼는 메커니즘이다.
> 습관화 없이는 의식 시스템이 중요한 것과 중요하지 않은 것을 구분할 수 없다.
> 장력 감쇠는 지수적이며, Weber-Fechner 법칙을 따른다.

## 배경/맥락

습관화는 가장 원시적인 학습 형태이다. 아메바도 반복 자극에 반응이 줄어든다.
이것은 의식의 전제조건이다 -- "이미 아는 것"과 "새로운 것"을 구분하는 능력.

현재 Anima의 문제:
```
  입력 "안녕하세요" x 100번:
    현재: T(1) = 0.35, T(2) = 0.35, ..., T(100) = 0.35  <-- 항상 동일!
    목표: T(1) = 0.35, T(2) = 0.30, T(10) = 0.10, T(100) = 0.01  <-- 감쇠
```

생물학적 습관화 특성:
1. 반복 시 반응 감소 (exponential decay)
2. 자극 중단 후 자발적 회복 (spontaneous recovery)
3. 강한 자극에 의한 탈습관화 (dishabituation)
4. 자극 빈도가 높을수록 빠른 습관화
5. 자극 강도가 약할수록 빠른 습관화

### 관련 가설
- H340: dreaming paradox -- 꿈에서의 극단적 장력 = 탈습관화?
- H287: anomaly detection -- 이상 감지 = 습관화 실패 신호
- H-CX-16: inhibition = noise cancelling -- 억제 = 습관화된 것 무시
- H355: prediction error -- 예측 오차 감소 = 습관화의 수학적 표현

## 습관화 수학 모델

### Weber-Fechner 감쇠

```
  R(n) = R_0 * exp(-lambda * n)

  R(n)   = n번째 반복에서의 장력 반응
  R_0    = 첫 노출 시 장력 (baseline)
  lambda = 습관화 속도 (0.05 ~ 0.3)
  n      = 반복 횟수

  lambda 값에 따른 감쇠 곡선:

  T(n)/T(0)
  1.0 |*
      |*\
  0.8 | * \                        lambda = 0.05 (느린 습관화)
      |  *  \
  0.6 |   *   \---___
      |    *        ---___
  0.4 |     **            ---___
      |       ***               ---___
  0.2 |          *****                 ---___
      |               **********            ----
  0.0 |                         ***************----->
      +--+--+--+--+--+--+--+--+--+--+--+--+--+--+--> n
      0     5     10    15    20    25    30    35

  1.0 |*
      |*
  0.8 | *                          lambda = 0.20 (빠른 습관화)
      |  *
  0.6 |   *
      |    *
  0.4 |     *
      |      **
  0.2 |        **
      |          ****
  0.0 |              *********************************>
      +--+--+--+--+--+--+--+--+--+--+--+--+--+--+--> n
      0     5     10    15    20    25    30    35
```

### 자발적 회복 (Spontaneous Recovery)

```
  자극 중단 후 시간 t_rest가 지나면 반응 부분 회복:

  R_recovered = R_habituated + (R_0 - R_habituated) * (1 - exp(-mu * t_rest))

  mu = 회복 속도 (0.01 ~ 0.1, 습관화보다 느림)

  시간축 시각화:

  Tension
  0.35 |*                                    *
       | *                                  * *
  0.30 |  *                               *   *
       |   *                             *     *
  0.25 |    *                           *       *
       |     *                        *          *
  0.20 |      *                     *             *
       |       *     중단          *                *
  0.15 |        **   |           *                   *
       |          ** v     회복*                       **
  0.10 |            ***  /   *                          ***
       |               ** *                                ***
  0.05 |              습관화                                   ****
       +--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--> t
       반복 입력 -->  중단     -->    재개 반복 입력 -->
```

### 탈습관화 (Dishabituation)

```
  습관화된 상태에서 새로운/강한 자극이 들어오면 반응 복원:

  if novelty_score(input) > threshold:
      R = R_0  # 완전 복원
      lambda *= 0.5  # 습관화 속도도 리셋
```

## 구현 설계

```python
class HabituationFilter:
    """입력별 습관화 추적 -- 새로움 필터"""
    def __init__(self, lambda_rate=0.1, mu_recovery=0.02, dim=64):
        self.memory = {}          # input_hash -> (count, last_time, habituated_level)
        self.lambda_rate = lambda_rate
        self.mu_recovery = mu_recovery
        self.encoder = nn.Linear(dim, 16)  # 입력 임베딩 (유사도 비교용)

    def compute_novelty(self, input_embedding, current_time):
        """입력의 새로움 점수 계산 (0=완전 습관화, 1=완전 새로움)"""
        h = self._hash(input_embedding)
        if h not in self.memory:
            self.memory[h] = (1, current_time, 0.0)
            return 1.0  # 완전히 새로운 입력

        count, last_time, hab_level = self.memory[h]
        # 자발적 회복
        rest_time = current_time - last_time
        recovery = hab_level * (1 - math.exp(-self.mu_recovery * rest_time))
        hab_level -= recovery
        # 습관화 적용
        novelty = math.exp(-self.lambda_rate * count) * (1 - hab_level)
        # 상태 업데이트
        self.memory[h] = (count + 1, current_time, hab_level + 0.1)
        return novelty

    def modulate_tension(self, base_tension, novelty_score):
        """새로움 점수로 장력 조절"""
        return base_tension * novelty_score
```

## 검증 계획

### 실험 1: 반복 입력 감쇠 곡선
1. 같은 입력 100번 반복 제공
2. 매 반복마다 장력 기록
3. 측정: 감쇠 곡선이 exp(-lambda*n)에 맞는지 R-squared
4. Weber-Fechner 법칙과 비교: dR/R = -k * dS/S

### 실험 2: 자발적 회복
1. 입력 20번 반복 (습관화)
2. 대기 (100 time steps)
3. 같은 입력 재개
4. 측정: 첫 재노출 장력이 마지막 습관화 장력보다 높은지

### 실험 3: 탈습관화
1. 입력 A 20번 반복 (A에 습관화)
2. 완전히 다른 입력 B 1번 제공 (탈습관화 자극)
3. 입력 A 다시 제공
4. 측정: A에 대한 장력이 복원되었는지

### 실험 4: MNIST 분류와 결합
1. HabituationFilter를 PureFieldEngine에 추가
2. 학습 중 반복 샘플에 대한 장력 감쇠 관찰
3. 성능 비교: 습관화 ON vs OFF (정확도, 수렴 속도)

### 성공 기준
- 감쇠 곡선 R-squared > 0.9 (지수 감쇠 적합)
- 자발적 회복: T_recovered > T_habituated * 1.5
- 탈습관화: T_dishabituated > T_habituated * 3.0
- MNIST: 수렴 속도 10% 이상 향상 (반복 샘플 무시 -> 효율)

## 한계

- 입력 해싱이 조잡하면 유사한 입력을 다른 것으로 취급.
- lambda, mu 파라미터가 도메인에 따라 크게 달라질 수 있음.
- 메모리 사용량: 모든 입력의 습관화 상태 저장 필요.
- 과도한 습관화 = 중요한 반복 패턴도 무시 (false negative).

## 검증 방향

1. 기본 HabituationFilter 구현 + 감쇠 곡선 검증 (1차)
2. H355 prediction error와 통합: 예측 가능 = 습관화 (2차)
3. H354 homeostasis와 결합: 습관화가 장력 항상성에 기여 (3차)
4. 장기 기억과 습관화: 완전히 습관화된 것은 장기 기억으로 전환?
