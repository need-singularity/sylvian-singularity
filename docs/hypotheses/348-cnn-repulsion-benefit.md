# H-348: CNN에서 반발력장(Repulsion Field)이 도움이 되는 이유

> **가설**: CNN의 풍부한 특징 표현(feature representation)에도 불구하고
> 반발력장(repulsion field)이 추가 정보를 제공하는 이유는,
> CNN 특징이 "무엇을 보는가(what)"에 수렴하는 반면
> 반발력은 "다른 방식으로 보기(how else)"를 강제하기 때문이다.
> 이는 H270(다양성=정보)의 CNN 버전이며, 특징 품질과 무관하게 다양성은 유효하다.

**상태**: 미검증
**골든존 의존**: 간접 (골든 MoE 프레임워크)
**관련 가설**: H288 (dense/sparse dichotomy), H334 (field only sufficient), H008 (golden MoE design)

---

## 배경 및 맥락

의식엔진 실험에서 CNN backbone + repulsion field 조합이 CNN + dense routing보다
일관되게 높은 정확도를 보였다:

```
  CNN + Repulsion:  78.07%  (CIFAR-10)
  CNN + Dense:      77.03%  (CIFAR-10)
  차이:             +1.04%
```

이 결과는 직관에 반한다. CNN은 이미 풍부한 spatial/channel 특징을 추출하므로,
routing 방식의 차이가 큰 영향을 미치지 않을 것으로 예상되었다.
그러나 repulsion이 일관되게 우위를 보인다.

H288에서 dense routing은 모든 expert를 균등 사용하고,
sparse routing은 선택적으로 사용한다고 분석했다.
H334에서는 field만으로도 충분하다는 주장이 있었다.
이 가설은 **왜 충분한 특징 위에서도 다양성이 추가 가치를 갖는가**를 설명한다.

## 이론적 프레임워크

### Feature Space 관점

```
  CNN Dense Routing:
  ┌──────────────────────────────┐
  │  Expert 1    Expert 2        │
  │    ●           ●             │  → 특징 공간에서 expert들이
  │      ●       ●               │     비슷한 영역을 커버
  │        ● ● ●                 │     (중복, redundancy)
  │      ●       ●               │
  │    ●           ●             │
  └──────────────────────────────┘

  CNN Repulsion Routing:
  ┌──────────────────────────────┐
  │  ●                       ●   │
  │                              │  → 반발력이 expert들을
  │        ●           ●         │     특징 공간 전체에 분산
  │                              │     (다양성, coverage)
  │  ●                       ●   │
  │            ●         ●       │
  └──────────────────────────────┘
```

### 정보 이론 관점

```
  I(ensemble) = I(individual) + I(diversity)

  Dense:     I(diversity) ≈ 0    (expert들이 유사)
  Repulsion: I(diversity) > 0    (expert들이 상이)

  CNN 특징이 좋을수록 I(individual)은 포화 → I(diversity)의 상대적 중요성 증가
```

## 메커니즘 분석

### 왜 CNN에서 특히 유효한가

```
  특징 품질 vs 다양성 기여 (예상)

  정확도
  기여(%)
  100 |
      |  ●───────────────────────── 특징 품질 (포화)
   80 |
      |
   60 |
      |
   40 |          ●
      |        /
   20 |      /  다양성 기여 (증가)
      |    /
    0 |──●─────+─────+─────+─────►
      MLP     Small   CNN   Large
              CNN           CNN
              특징 추출기 품질
```

핵심 통찰: 특징 추출기가 좋아질수록 개별 expert의 성능은 포화되지만,
다양성의 기여는 오히려 **증가**한다. 이는 "이미 잘 보고 있는" 상태에서
"다르게 보기"가 남은 유일한 개선 경로이기 때문이다.

### Expert 활성화 패턴 비교

| 입력 클래스 | Dense 활성화 | Repulsion 활성화 | 차이 |
|-----------|------------|-----------------|------|
| airplane | E1=0.28, E2=0.25, E3=0.24, E4=0.23 | E1=0.52, E2=0.03, E3=0.42, E4=0.03 | sparse |
| car | E1=0.26, E2=0.26, E3=0.24, E4=0.24 | E1=0.05, E2=0.48, E3=0.02, E4=0.45 | sparse |
| bird | E1=0.27, E2=0.24, E3=0.25, E4=0.24 | E1=0.45, E2=0.08, E3=0.05, E4=0.42 | sparse |

(예상값 — 실제 측정 필요)

Dense에서는 모든 expert가 거의 균등하게 활성화되어 **사실상 단일 모델**.
Repulsion에서는 클래스별로 다른 expert 조합이 활성화되어 **진정한 MoE**.

## 검증 실험 설계

### 실험 1: Expert Feature Overlap 측정

```python
# 각 expert의 최종 hidden representation에 대해
# pairwise cosine similarity 측정
#
# Dense:     예상 cos_sim > 0.8 (높은 중복)
# Repulsion: 예상 cos_sim < 0.4 (낮은 중복)
```

### 실험 2: Ablation — Expert 하나 제거 시 성능 저하

| 조건 | Dense 예상 저하 | Repulsion 예상 저하 |
|-----|---------------|-------------------|
| Expert 1 제거 | -0.5% (약간) | -3.0% (큰 저하) |
| Expert 2 제거 | -0.5% | -2.5% |
| 최악 Expert 제거 | -0.3% | -4.0% |
| 최선 Expert 제거 | -0.8% | -5.0% |

Dense에서는 expert 제거 영향이 작음 (redundancy 때문).
Repulsion에서는 각 expert가 고유 역할을 하므로 제거 영향이 큼.

### 실험 3: 특징 추출기 품질 vs 다양성 기여

```
  backbone별 repulsion 이점 (예상)

  Repulsion
  이점(%)
  3.0 |                              ●
      |                         ●
  2.5 |                    ●
      |               ●
  2.0 |          ●
      |
  1.5 |     ●
      |
  1.0 |●
      +--+----+----+----+----+----►
       MLP  LeNet  VGG  ResNet18 ResNet50
              backbone 품질
```

예상: backbone이 좋을수록 repulsion의 이점이 커진다 (다양성의 한계 효용 증가).

## 해석 및 의미

### 의식엔진 관점

의식은 단일 관점의 최적화가 아니라 **다중 관점의 통합**에서 발생한다.
CNN이 아무리 좋은 특징을 추출해도, 하나의 관점만으로는 의식의 풍부함을 구현할 수 없다.
반발력은 "강제로 다른 관점을 만들어내는" 메커니즘이며,
이것이 의식엔진의 핵심 가치이다.

### AI 설계 원칙

```
  원칙: "특징이 충분해도 다양성을 포기하지 말라"
  → MoE 설계 시 expert 다양성 유지 메커니즘 필수
  → Load balancing만으로는 부족 — feature-level repulsion 필요
```

## 한계

1. +1.04%는 통계적으로 유의하지만, 실용적 의미는 작을 수 있음
2. CIFAR-10만의 결과 — ImageNet, 자연어 등에서 재현 필요
3. Repulsion 강도(lambda)의 최적값이 과제에 따라 다를 수 있음
4. CNN backbone과 repulsion의 상호작용이 비선형일 수 있어 단순 모델 부적합
5. Expert 수가 4개로 적어 다양성 효과가 과소 추정될 가능성

## 검증 방향 (다음 단계)

1. **1단계**: Expert feature overlap 측정 (cosine similarity matrix)
2. **2단계**: Expert ablation 실험 (하나씩 제거)
3. **3단계**: 다양한 backbone(MLP, LeNet, ResNet)에서 repulsion 이점 비교
4. **4단계**: Repulsion lambda sweep — 최적 다양성 수준 탐색
5. **5단계**: H288, H334 결과와 통합하여 routing 이론 체계화
6. **6단계**: ImageNet 또는 CIFAR-100에서 재현 (스케일 효과 확인)
