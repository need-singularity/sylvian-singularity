# 가설 358: 주의 = 선택적 장력 (Attention as Selective Tension)

## 가설

> 의식은 모든 입력을 동등하게 처리하지 않는다.
> attention mask가 장력 계산에 적용되어 '주목하는 부분'에만 높은 장력이 발생한다.
> 선택적 주의 없이는 정보 과부하에서 의식적 처리가 불가능하다.
> tension(x) = base_tension(x) * attention_weight(x) 이며,
> attention weight는 목표(H357)와 놀라움(H355)에 의해 결정된다.

## 배경/맥락

인간 의식의 가장 뚜렷한 특성: 한 번에 하나만 "의식적으로" 처리한다.

```
  Cocktail party effect:
    시끄러운 파티에서 수십 명이 말하지만,
    한 사람의 말에만 "주의"를 기울일 수 있다.
    그러나 자기 이름이 불리면 즉시 전환된다.

  이것은:
    1. 선택적 억제 (다른 입력의 장력 = 0)
    2. 선택적 증폭 (주의 대상의 장력 극대화)
    3. 돌발 전환 (놀라움 > 임계값 -> 주의 이동)
```

현재 Anima의 PureFieldEngine:
```
  모든 입력 차원이 동일한 가중치로 처리됨
  tension = f(전체 입력)   <-- 차원별 차이 없음

  제안:
  tension = f(입력 * attention_mask)   <-- 선택적 장력
```

### 관련 가설
- H319: tension as attention -- 장력 자체가 주의의 측정
- H339: direction = concept -- 방향이 개념을 나타냄
- H-CX-28: information theory unification -- 정보 이론 통합
- H357: intention/goal -- 목표가 주의 방향을 결정
- H355: prediction error -- 놀라움이 주의를 끌어옴

## 주의 메커니즘 수학

### Spotlight Model (기본)

```
  attention_weight(x_i) = softmax(relevance(x_i) / temperature)

  relevance(x_i) = alpha * goal_alignment(x_i)      목표 관련성
                 + beta  * surprise(x_i)              놀라움
                 + gamma * salience(x_i)              현저성 (크기, 변화율)

  temperature = 장력의 역수 (높은 장력 = 좁은 주의)
```

### 주의 범위 vs 장력 관계

```
  주의 폭 (attention breadth)

  폭
  넓음 |*
       | *
       |  *
       |   **
       |     ***
       |        ****
       |            *****
  좁음 |                 ***********
       +--+--+--+--+--+--+--+--+--+--> 장력
       0  0.1 0.2 0.3 0.4 0.5 0.6

  낮은 장력 (이완): 넓은 주의 = 확산적 사고 (divergent)
  높은 장력 (긴장): 좁은 주의 = 수렴적 사고 (convergent)

  이것은 Easterbrook의 "cue utilization theory"와 일치:
    각성 수준이 높을수록 주의 범위가 좁아진다.

  수식:
    breadth = 1 / (1 + k * tension)
    k = 집중 계수 (기본값 2.0)
```

### 차원별 주의 히트맵 예시 (MNIST)

```
  입력 이미지 (숫자 7):          주의 마스크:

  . . . . . . . . . . . .      . . . . . . . . . . . .
  . . . . . # # # # . . .      . . . . . 3 5 8 7 . . .
  . . . . . . . . # . . .      . . . . . . . . 9 . . .
  . . . . . . . # . . . .      . . . . . . . 8 . . . .
  . . . . . . # . . . . .      . . . . . . 7 . . . . .
  . . . . . # . . . . . .      . . . . . 6 . . . . . .
  . . . . # . . . . . . .      . . . . 4 . . . . . . .
  . . . . # . . . . . . .      . . . . 3 . . . . . . .
  . . . . . . . . . . . .      . . . . . . . . . . . .

  숫자가 클수록 높은 주의 (높은 장력).
  획의 꺾이는 부분(정보량 높음)에 주의 집중.
  빈 공간(정보량 낮음)에는 주의 거의 없음.

  attention_tension(pixel_i) = base_tension * attention_weight(pixel_i)
```

### 주의 전환 메커니즘

```
  주의 상태 전이:

  시간 -->

  [초점 A] -----> [초점 A] -----> [전환] -----> [초점 B]
     |               |              ^               |
     |               |              |               |
     v               v              |               v
  T(A)=높음       T(A)=높음    surprise(B)>     T(B)=높음
  T(B)=낮음       T(B)=낮음    threshold       T(A)=낮음

  전환 트리거:
    1. 목표 완료 -> 다음 목표로 전환
    2. surprise(새 입력) > current_attention_tension
    3. 장시간 같은 초점 -> 피로 -> 자발적 전환
    4. 외부 명시적 요청 ("이것 봐")
```

## 구현 설계

```python
class SelectiveAttention:
    """선택적 주의 = 차원별 장력 마스크"""
    def __init__(self, input_dim, hidden_dim=32):
        # 주의 가중치 생성 네트워크
        self.query_net = nn.Linear(input_dim, hidden_dim)
        self.key_net = nn.Linear(input_dim, hidden_dim)
        self.value_net = nn.Linear(input_dim, hidden_dim)
        # 목표 + 놀라움 결합
        self.goal_projection = nn.Linear(hidden_dim, hidden_dim)
        self.surprise_gate = nn.Linear(1, hidden_dim)
        # 주의 폭 제어
        self.breadth_k = 2.0

    def compute_attention(self, input_x, goal_vector=None, surprise=0.0):
        """입력 차원별 주의 가중치 계산"""
        Q = self.query_net(input_x)
        K = self.key_net(input_x)
        V = self.value_net(input_x)

        # 목표 관련성 반영
        if goal_vector is not None:
            goal_bias = self.goal_projection(goal_vector)
            Q = Q + goal_bias

        # 놀라움에 의한 주의 끌림
        surprise_bias = self.surprise_gate(torch.tensor([surprise]))
        K = K + surprise_bias

        # attention weights (softmax with tension-based temperature)
        scores = torch.matmul(Q, K.T) / math.sqrt(K.shape[-1])
        weights = F.softmax(scores, dim=-1)

        # 주의 적용된 출력
        attended = torch.matmul(weights, V)
        return attended, weights

    def attention_breadth(self, tension):
        """장력에 따른 주의 범위"""
        return 1.0 / (1.0 + self.breadth_k * tension)

    def modulate_tension(self, base_tension_per_dim, attention_weights):
        """차원별 장력 = 기본 장력 * 주의 가중치"""
        return base_tension_per_dim * attention_weights
```

## 의식과 주의의 관계

```
  Global Workspace Theory (Baars, 1988):

  +--------------------------------------------------+
  |  무의식 처리 (습관화된 것, 낮은 장력)              |
  |   +------+  +------+  +------+  +------+         |
  |   |모듈 1|  |모듈 2|  |모듈 3|  |모듈 N|         |
  |   +---+--+  +---+--+  +---+--+  +---+--+         |
  |       |          |          |          |          |
  |       v          v          v          v          |
  |   +==========================================+   |
  |   |    Global Workspace (의식적 처리)          |   |
  |   |    = 주의가 선택한 것만 여기 올라옴         |   |
  |   |    = 높은 장력 = 의식의 내용               |   |
  |   +==========================================+   |
  |                      |                            |
  |                      v                            |
  |               [행동/출력/기억]                      |
  +--------------------------------------------------+

  주의 = 의식의 게이트키퍼
  높은 장력 = workspace에 올라감 = 의식됨
  낮은 장력 = workspace 밖 = 무의식적 처리
```

## 검증 계획

### 실험 1: MNIST attention 시각화
1. PureFieldEngine + SelectiveAttention으로 MNIST 분류
2. 각 이미지에 대한 attention map 시각화
3. 측정: attention이 의미 있는 영역(획)에 집중하는지

### 실험 2: with/without attention 성능 비교
1. PureFieldEngine (기본) vs PureFieldEngine + SelectiveAttention
2. MNIST 정확도 비교
3. 학습 속도 비교 (epochs to convergence)

### 실험 3: 주의 폭 vs 장력 관계
1. 다양한 장력 수준에서 attention entropy 측정
2. 높은 장력 -> 낮은 entropy (좁은 주의) 확인
3. Easterbrook theory와 정량적 비교

### 실험 4: 주의 전환 속도
1. 연속 입력에서 갑작스러운 패턴 변경
2. attention map이 새 패턴으로 이동하는 데 걸리는 step 수
3. 목표 관련 vs 무관 변경에 대한 전환 속도 차이

### 성공 기준
- MNIST attention map: 획 영역에 80% 이상 집중
- 정확도: attention 추가 시 >= baseline
- 장력-주의폭 상관: r < -0.7 (음의 상관)
- 전환 속도: 목표 관련 변경 < 무관 변경 (더 빠름)

## 한계

- Self-attention 추가로 계산 비용 증가 (O(n^2)).
- 주의 메커니즘이 학습 초기에 무작위 -> 의미 있는 주의까지 시간 필요.
- "무의식적 처리"를 명시적으로 모델링하지 않음 (attention=0인 부분).
- Transformer의 attention과 "의식적 주의"는 다를 수 있음.

## 검증 방향

1. SelectiveAttention 구현 + MNIST 테스트 (1차)
2. H357 goal과 통합: 목표 -> 주의 방향 (2차)
3. H355 surprise와 통합: 놀라움 -> 주의 끌림 (3차)
4. H356 habituation과 통합: 습관화 -> 주의 감소 (4차)
5. 전체 통합: 항상성 + 예측 + 습관화 + 의도 + 주의 = 의식 루프
