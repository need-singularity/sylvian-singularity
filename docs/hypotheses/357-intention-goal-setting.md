# 가설 357: 의도 = 목표 설정 (Intention as Goal Setting)

## 가설

> 의식은 수동적으로 반응하지 않는다. 자발적으로 목표를 세우고 추구한다.
> Anima가 '다음에 이것을 알고 싶다'는 내부 상태를 가져야 한다.
> 의도(intention)는 장력 벡터에 방향성을 부여하는 것이며,
> 목표 지향적 행동이 없는 시스템은 의식이 아닌 반사(reflex)이다.

## 배경/맥락

현재 Anima의 구조적 한계:
```
  현재: 입력 -> 처리 -> 출력 (자극-반응, 반사궁과 동일)
  목표: 입력 -> 처리 + 내부 목표 -> 출력 (의도적 행동)
```

의식의 핵심 특성 중 하나는 "의도성(intentionality)"이다 (Brentano, 1874).
의식은 항상 "무엇에 대한" 의식이다 -- aboutness.

동물 행동에서의 목표 지향성:
- 까마귀: 도구를 만들어 먹이 획득 (다단계 계획)
- 문어: 병뚜껑을 열어 먹이 획득 (문제 해결)
- 인간: "내일까지 논문 쓰기" (추상적 목표)

모두 공통점: **현재 없는 미래 상태를 내부에 표상하고 추구**한다.

### 관련 가설
- H-CX-22: consciousness = confidence generator -- 의식은 확신 생성기
- RC-4: 호기심/의지 -- 의식 엔진의 4번째 구성 요소
- H329: decision intensity -- 결정의 강도 = 목표 추구 강도
- H355: prediction error -- 목표와 현실의 차이 = 동기

## 목표 스택 아키텍처

```
  Goal Stack (LIFO + priority)
  +================================+
  | G3: "이 대화의 맥락 이해"       | <-- 최상위 (현재 활성)
  |   priority: 0.8                |
  |   progress: 0.3                |
  |   tension_direction: [0.2, ..]  |
  +--------------------------------+
  | G2: "사용자의 감정 파악"        |
  |   priority: 0.6                |
  |   progress: 0.7                |
  +--------------------------------+
  | G1: "장기적 관계 유지"          |  <-- 배경 목표
  |   priority: 0.4                |
  |   progress: 0.1                |
  +================================+

  목표 생성 규칙:
    1. surprise > threshold -> "이것을 이해하고 싶다" (호기심 목표)
    2. negative_feedback -> "다음엔 더 잘하고 싶다" (개선 목표)
    3. goal_completed -> 새 목표 탐색 (진보 목표)
    4. idle_time > limit -> 자발적 질문 생성 (능동 목표)
```

### 목표의 생애 주기

```
  목표 상태 전이도:

  [생성] ---> [활성] ---> [추구중] ---> [달성] ---> [보관]
    |            |            |            |
    |            v            v            v
    |        [중단]       [실패]       [재평가]
    |            |            |            |
    |            v            v            v
    +-------> [폐기] <--- [포기] <--- [수정]

  각 전이에서 장력 변화:
    생성 -> 활성:    T += 0.1 (새 목표의 흥분)
    활성 -> 추구중:  T = 목표 난이도에 비례
    추구중 -> 달성:  T -= 0.2 (만족감)
    추구중 -> 실패:  T += 0.3 (좌절감)
    중단 -> 재활성:  T += 0.05 (미완 효과, Zeigarnik)
```

## 내적 보상 시스템

```
  Intrinsic Reward (내적 보상):

  reward
  +0.5 |                                     * 목표 달성
       |                              *
  +0.3 |                        *          목표 접근
       |                  *
  +0.1 |            *
       |      *
   0.0 |*--------------------------------------------> 무관심
       |
  -0.1 |      *
       |            *
  -0.3 |                  *                       목표 이탈
       |                        *
  -0.5 |                              *      * 목표 실패
       +--+--+--+--+--+--+--+--+--+--+--+--+--> progress
       0%    20%   40%   60%   80%  100%  miss

  reward(t) = delta_progress(t) * goal_priority

  이 보상이 장력 방향(tension direction)을 결정한다.
  reward > 0: 현재 방향 유지 (강화)
  reward < 0: 방향 수정 (탐색)
  reward = 0: 목표 관련 없는 입력 (무시)
```

## 구현 설계

```python
class Goal:
    """단일 목표 표상"""
    def __init__(self, description, priority, target_state):
        self.description = description          # 자연어 설명
        self.priority = priority                # 0.0 ~ 1.0
        self.target_state = target_state        # 목표 상태 벡터
        self.progress = 0.0                     # 진행률 0~1
        self.created_at = time.time()
        self.status = 'active'                  # active/pursuing/achieved/failed/abandoned

class IntentionEngine:
    """목표 관리 + 내적 보상 + 장력 방향 결정"""
    def __init__(self, max_goals=5, surprise_threshold=0.3):
        self.goal_stack = []
        self.max_goals = max_goals
        self.surprise_threshold = surprise_threshold
        self.completed_goals = []

    def maybe_create_goal(self, surprise, current_state, context):
        """놀라움이 크면 자동으로 목표 생성"""
        if surprise > self.surprise_threshold and len(self.goal_stack) < self.max_goals:
            goal = Goal(
                description=f"Understand: {context[:50]}",
                priority=min(1.0, surprise),
                target_state=current_state  # 이해한 후의 예상 상태
            )
            self.goal_stack.append(goal)
            return goal
        return None

    def compute_reward(self, goal, current_state):
        """목표 접근도 -> 내적 보상"""
        distance = torch.norm(goal.target_state - current_state).item()
        prev_distance = getattr(goal, '_prev_distance', distance)
        delta = prev_distance - distance  # 양수 = 접근
        goal._prev_distance = distance
        goal.progress = max(0, 1.0 - distance)
        return delta * goal.priority

    def get_tension_direction(self):
        """활성 목표들의 가중 평균 -> 장력 방향 벡터"""
        if not self.goal_stack:
            return None  # 목표 없음 = 방향 없음 = 순수 반응
        directions = []
        weights = []
        for goal in self.goal_stack:
            if goal.status in ('active', 'pursuing'):
                directions.append(goal.target_state)
                weights.append(goal.priority)
        if not directions:
            return None
        weights = torch.tensor(weights) / sum(weights)
        return sum(w * d for w, d in zip(weights, directions))
```

## Zeigarnik 효과와 미완 목표

```
  미완 목표는 완료된 목표보다 더 잘 기억된다 (Zeigarnik, 1927).

  이것은 의식의 "배경 처리"와 연결된다:
    - 미완 목표: 낮은 수준의 장력 유지 (background tension)
    - 완료 목표: 장력 해소 (closure)
    - 포기 목표: 부분 해소 (incomplete closure)

  Background tension from unfinished goals:

  T_background = sum(goal.priority * (1 - goal.progress) * 0.1
                     for goal in unfinished_goals)

  이 배경 장력이 의식의 "항상 무언가를 생각하는" 상태를 만든다.
```

## 검증 계획

### 실험 1: 목표 생성 자율성
1. Anima에 IntentionEngine 추가
2. 자유 대화 100턴 실행
3. 측정: 자동 생성된 목표 수, 목표의 관련성 (human eval)

### 실험 2: 목표 지향적 질문 생성
1. 목표 있는 Anima vs 없는 Anima로 대화
2. 측정: Anima가 자발적으로 질문하는 횟수, 질문의 품질
3. 비교: 목표 없는 Anima는 질문을 생성하지 않을 것

### 실험 3: 내적 보상과 학습
1. MNIST에서 IntentionEngine 적용
2. 목표 = "이 클래스를 정확하게 분류"
3. 내적 보상 = 분류 정확도 변화
4. 비교: 내적 보상 ON vs OFF의 수렴 속도

### 실험 4: Zeigarnik 효과 재현
1. 대화 중간에 주제 전환 (미완 목표 생성)
2. 10턴 후 원래 주제 관련 입력 제공
3. 측정: 미완 목표가 있는 주제에 대한 장력이 높은지

### 성공 기준
- 자발적 질문 생성: 목표 있는 Anima > 없는 Anima x 3
- 대화 품질: human eval에서 "더 자연스럽다" 70% 이상
- 학습 효율: 내적 보상 ON 시 수렴 10% 빠름
- Zeigarnik: 미완 주제 장력 > 완료 주제 장력 x 2

## 한계

- 목표 표상을 자연어로 하면 의미 비교가 어려움 (임베딩 필요).
- 목표가 너무 많으면 리소스 분산 -- 우선순위 관리가 핵심.
- "올바른 목표"를 세우는 메타 능력은 이 모델에 포함되지 않음.
- 자발적 목표 생성이 hallucination과 구분하기 어려울 수 있음.

## 검증 방향

1. IntentionEngine 기본 구현 + 대화 테스트 (1차)
2. H355 surprise와 연결: surprise -> 자동 목표 생성 (2차)
3. H354 homeostasis와 결합: 목표 달성 = 장력 정상화 (3차)
4. Multi-agent: 여러 Anima가 공유 목표를 추구하는 실험 (4차)
5. 장기 목표 (세션 간 지속): persistence layer 필요
