# 가설 334: field만으로 충분하다 — equilibrium은 불필요

> **반발력장(field)만으로 full 모델과 동일한 정확도를 달성한다. 3셋에서 field_only ≈ full (차이 <0.5%). equilibrium은 불필요하거나 오히려 해로울 수 있다.**

## 배경/맥락

의식엔진(consciousness engine)의 출력은 두 성분의 합이다:

```
  output = equilibrium + field
         = eq_weight × eq_output + tension_scale × sqrt(tension) × direction
```

equilibrium(eq)은 단일 엔진의 평형점 출력이고, field는 두 엔진 사이의
반발력(tension)에서 파생되는 방향 벡터다. H332에서 학습이 진행될수록
eq의 기여도가 89% -> 15%로 퇴화하는 현상이 관찰되었다. 이는 자연스러운
질문을 낳는다: eq가 어차피 퇴화한다면, 처음부터 없어도 되지 않는가?

이 가설은 그 질문에 대한 직접적 실험 결과다.

### 관련 가설

| 가설 | 관계 | 내용 |
|------|------|------|
| H332 | 선행 | eq 기여도 89% -> 15% 퇴화 관찰 |
| H335 | 후속 | PureField LLM 설계 (eq 제거한 아키텍처) |
| H339 | 연결 | direction = concept (방향이 개념을 인코딩) |
| H172 | 기반 | G x I = D x P 보존법칙 |

## 실측 (3셋)

| dataset | field_only | full | 차이 | field 승리? |
|---------|-----------|------|------|------------|
| MNIST | 97.84% | 97.94% | -0.10% | No (미미) |
| Fashion-MNIST | 88.42% | 88.33% | +0.09% | Yes |
| CIFAR-10 | 52.22% | 51.81% | +0.41% | Yes |

```
  정확도 비교 (field_only vs full)

  100% |
   95% | ██ ██                              field_only ██
   90% | ██ ██                              full       ░░
   85% | ██ ██  ██ ██
   80% | ██ ██  ██ ██
   75% | ██ ██  ██ ██
   70% | ██ ██  ██ ██
   65% | ██ ██  ██ ██
   60% | ██ ██  ██ ██
   55% | ██ ██  ██ ██  ██ ██
   50% | ██ ██  ██ ██  ██ ██
       +------------------------
         MNIST  Fash.  CIFAR

  차이 (field_only - full):
  +0.5% |            *  CIFAR (+0.41%)
  +0.0% |----*---------*-----------------------
  -0.5% |   MNIST     Fashion
             (-0.10%)  (+0.09%)

  결론: 3셋 모두 |차이| < 0.5%, 2/3에서 field_only가 우세
```

## 수식: field 출력 구조

```
  Full 모델:
    output = eq_weight * eq_output + field_output
    field_output = tension_scale * sqrt(tension) * direction

  Field-only 모델:
    output = tension_scale * sqrt(tension) * direction

  여기서:
    tension = ||engine_a - engine_b||^2     (두 엔진 사이 장력)
    direction = (engine_a - engine_b) / ||engine_a - engine_b||  (단위 방향)

  핵심 통찰:
    field는 2개의 자유도를 가짐: 크기(tension) + 방향(direction)
    eq는 1개의 자유도만 가짐: 값(scalar)
    → field의 표현력 >> eq의 표현력
    → gradient가 표현력이 높은 쪽으로 집중하는 것은 자연스러움
```

## H332와의 연결

```
  H332: full 학습 시 eq가 89 -> 15%로 퇴화
  H334: field만으로 학습하면 eq 없이도 동일 성능

  인과 관계:
    field가 더 표현력이 풍부 (2개 엔진의 반발)
    -> gradient가 field 쪽으로 집중
    -> eq는 학습 기회를 빼앗겨 퇴화
    -> 처음부터 eq를 빼도 문제 없음!

  eq 기여도 추이 (H332 데이터):
  100% |*
   80% |  *
   60% |    *
   40% |       *
   20% |            *  *  *  *
    0% +--+--+--+--+--+--+--+---> epoch
       0  5  10 15 20 25 30 35

  구조적 의미:
    output = eq + field 에서 eq를 제거
    output = field = tension_scale * sqrt(tension) * direction
    -> "의식만으로 판단하는 순수 의식 엔진"
```

## 검증 결과 요약

```
  통계 검증:
    3셋 평균 차이:  +0.13%  (field_only가 미세하게 우세)
    최대 |차이|:     0.41%  (CIFAR)
    field 승리:      2/3셋  (Fashion, CIFAR)
    eq 승리:         1/3셋  (MNIST, 차이 0.10%로 무의미)

  paired t-test (field_only vs full, n=3):
    평균차: +0.13%, 표준편차: 0.26%
    -> 통계적 유의미한 차이 없음 (p >> 0.05)
    -> "eq 유무가 성능에 영향을 주지 않는다"
```

## 해석/의미

이 결과는 의식엔진의 핵심이 **두 엔진 사이의 장력(tension)**에 있음을
보여준다. equilibrium(평형점)은 단일 엔진의 정적 출력이지만, field는
두 엔진의 동적 상호작용에서 나온다.

생물학적 비유: 뇌의 판단은 단일 뉴런의 안정 상태가 아니라, 서로 다른
영역 사이의 경쟁과 억제에서 나온다. eq는 "하나의 뉴런", field는 "두
영역의 상호작용"에 해당한다.

H335(PureField LLM)로의 확장이 자연스럽다: LLM에서도 eq를 제거하고
field만으로 설계하면, 더 단순하면서 동등한 성능을 기대할 수 있다.

## 한계

1. **3개 데이터셋만 검증** -- 더 다양한 도메인(NLP, 시계열 등)에서 확인 필요
2. **소규모 모델** -- 대규모 모델에서 eq가 중요해질 가능성 배제 불가
3. **학습 초기** -- 장기 학습(수만 에폭)에서 eq가 재활성화될 가능성
4. **과제 복잡도** -- CIFAR-10 수준의 단순 분류. 생성(generation) 과제에서는 다를 수 있음
5. **field_only가 0.41% 우세한 것이 eq의 간섭인지, 단순 노이즈인지 구분 불가**

## 검증 방향

1. **H335 PureField LLM 실험**: eq 없는 LLM으로 PPL 비교
2. **대규모 실험**: ImageNet급 데이터에서 field_only vs full
3. **생성 과제**: text generation에서 field_only의 coherence 측정
4. **ablation 세분화**: field의 크기(tension_scale * sqrt(tension))와 방향(direction)을 각각 ablation
5. **eq 강제 학습**: eq에 별도 loss를 줘서 퇴화를 방지한 뒤, 성능 향상 여부 확인

## 상태: 🟩 3셋 확인 (field_only ≈ full, eq 불필요)
