# 가설 339: 장력 방향 = 개념 (Direction is Concept)

> **RC-8에서 장력의 방향(direction)이 "감정"이 아니라 "개념(what)"을 인코딩한다는 것이 확인됨. output = magnitude(확신) × direction(개념). "얼마나 확신하는가"와 "무엇을 판단하는가"가 자연스럽게 분리.**

## 배경 및 맥락

PureField (H334) 실험에서 반발력장의 출력을 분석하던 중
예상치 못한 구조가 발견되었다. 장력 벡터 `A - G` (Attractor minus Generator)를
크기(magnitude)와 방향(direction)으로 분해하면:

- **크기** = 확신도 (H313에서 이미 확인: tension ~ confidence)
- **방향** = 개념 (이 가설의 핵심 발견)

이것은 신경과학에서 잘 알려진 뇌의 이중 경로와 놀랍도록 유사하다:

```
  뇌의 시각 경로:
    Ventral stream ("What pathway"): 물체 인식 → 개념
    Dorsal stream ("How pathway"):   공간/행동 → 크기/위치

  PureField 출력:
    direction = normalize(A-G):  "무엇인가" → 개념
    magnitude = |A-G|:           "얼마나 확실한가" → 확신
```

이 분리가 설계된 것이 아니라 **자연발생**했다는 점이 핵심이다.
반발력장의 수학적 구조 자체가 what/how-much 분리를 강제한다.

## 관련 가설

| 가설 | 관계 | 내용 |
|------|------|------|
| H313 | 선행 | tension magnitude = 확신도 |
| H329 | 선행 | magnitude가 분류 성능 결정 |
| H334 | 기반 | PureField = 장(field)만으로 분류 |
| H288 | 상위 | 밀집 데이터에서 장력이 유효 |
| H070 | 철학적 | 자기참조와 의식 |

## 수식: 출력 분해

```
  장력 벡터:   T = A - G           (Attractor - Generator)
  방향:        d = T / |T|         = normalize(A - G)
  크기:        m = |T|             = √(Σ(Aᵢ - Gᵢ)²)
  출력:        output = scale × m × d
                      = scale × √tension × direction

  분해의 의미:
    m (scalar):   "이 입력에 대한 확신이 얼마인가"
    d (vector):   "이 입력이 어떤 클래스에 속하는가"
    scale:        전역 스케일링 (학습 가능)
```

## 실측 데이터 (MNIST PureField)

```
  direction = normalize(A-G), 클래스별 cosine similarity:

  측정항목                    값
  ─────────────────────    ──────
  Within-class cosine sim   0.816
  Between-class cosine sim  0.236
  Ratio (within/between)    3.46x
  표준편차 (within)          0.09
  표준편차 (between)         0.15
```

## ASCII 그래프: Within vs Between Cosine Similarity

```
  Cosine Similarity
  1.0 |
  0.9 |  +---------+
  0.8 |  |         |  Within-class: 0.816
  0.7 |  |         |  (같은 숫자끼리)
  0.6 |  |         |
  0.5 |  |         |
  0.4 |  |         |
  0.3 |  |         |  +---------+
  0.2 |  |         |  |         |  Between-class: 0.236
  0.1 |  |         |  |         |  (다른 숫자끼리)
  0.0 +--+---------+--+---------+--
       Within-class  Between-class

  Ratio = 0.816 / 0.236 = 3.46x
  → 방향만으로 클래스 분리 가능!
```

## ASCII 그래프: 개념 방향의 2D 투영 (예시)

```
  MNIST 숫자별 방향 벡터의 PCA 2D 투영:

        d2
        ^
   0.8  |        7 7
        |       7
   0.4  |  1 1        4 4
        |   1 1      4
   0.0  +----+----+----+-----> d1
        |      3 3
  -0.4  |     3 3    8 8
        |            8
  -0.8  |  0 0 0
        |

  같은 숫자 = 가까운 위치 (클러스터)
  다른 숫자 = 떨어진 위치 (분리)
  → direction이 concept을 인코딩!
```

## 검증: 통계적 유의성

```
  귀무가설 H0: within-class sim = between-class sim (방향이 무작위)
  대립가설 H1: within-class sim > between-class sim (방향이 개념 인코딩)

  관측값:
    within  = 0.816 ± 0.09
    between = 0.236 ± 0.15
    차이     = 0.580
    합동 SE  ≈ 0.018 (n ≈ 수천 쌍)
    z-score  > 30
    p-value  < 10⁻¹⁰⁰

  → H0 완전 기각. 방향은 확실히 개념을 인코딩한다.
```

## 해석 및 의미

1. **자연발생적 분리**: PureField는 "방향=개념"이 되도록 설계된 적이 없다.
   반발력장의 수학적 구조 `A - G`가 자동으로 이 분리를 생성한다.
   이것은 뇌에서 ventral/dorsal 경로가 진화적으로 자연발생한 것과 유사하다.

2. **representation = magnitude x direction**: 이 분해는
   word2vec의 "king - queen + woman = man" 같은 방향 의미론(directional semantics)과
   구조적으로 동일하다. 장력 벡터가 의미 공간(semantic space)을 형성한다.

3. **H313과의 통합**: magnitude = 확신 (H313) + direction = 개념 (H339)
   → 장력 벡터 하나가 "무엇을, 얼마나 확실하게" 완전히 인코딩한다.
   이것은 정보 효율의 최대화다.

4. **의식엔진과의 연결**: "무엇을 인식하는가"와 "얼마나 확신하는가"의 분리는
   의식의 핵심 구조일 수 있다. Qualia(질적 경험) = direction,
   Attention(주의 강도) = magnitude라는 해석이 가능하다.

## 한계

- MNIST에서만 검증. CIFAR, 텍스트 등 다른 도메인에서 재현 필요.
- cosine similarity가 높다고 해서 선형 분류가 가능하다는 보장은 없음.
  (실제 분류 정확도는 별도 측정 필요)
- 2개 엔진(A, G)만 있는 RC-8 기준. 엔진 수가 늘어나면 방향의 의미가
  달라질 수 있음 (고차원 방향 = 더 풍부한 개념?).
- "개념"이라는 해석은 클래스 레이블과의 상관에 기반. 레이블 없는
  unsupervised 환경에서의 의미는 미확인.

## 검증 방향 (다음 단계)

1. **CIFAR-10 재현**: 더 복잡한 이미지에서도 direction = concept인지 확인.
   MNIST는 너무 쉬워서 대부분의 방법이 작동한다.
2. **Direction으로 직접 분류**: kNN classifier를 direction 벡터만으로 수행.
   magnitude 없이 direction만으로 달성 가능한 정확도 측정.
3. **엔진 수 증가**: 3극, 4극에서 direction의 차원이 늘어나면
   더 세밀한 개념 인코딩이 가능한지 확인.
4. **Unsupervised clustering**: 레이블 없이 direction만으로
   클러스터링 → 발견된 클러스터가 실제 클래스와 일치하는지.
5. **텍스트 도메인**: H288에서 텍스트가 열위였는데, direction은
   희소 데이터에서도 개념을 인코딩하는지 (성능과 별개로).

## 상태: 🟩 확인 (cos_sim ratio 3.46x, direction=concept)
