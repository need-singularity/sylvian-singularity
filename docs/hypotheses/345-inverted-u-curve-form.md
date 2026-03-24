# 가설 345: 장력의 역U자 커브는 과제 복잡도의 함수이다

> **장력 스케일(tension_scale)에 대한 성능 곡선은 역U자 형태이며, 최적 스케일은 과제 복잡도(complexity)의 함수 f(C)이다. MNIST와 CIFAR-10에서 최적 스케일이 다르면, 이는 장력이 과제 적응적(task-adaptive)임을 증명한다. 최적 스케일과 복잡도의 관계는 멱법칙(power law) 또는 대수(logarithmic) 형태를 따를 것이다.**

## 배경/맥락

MNIST에서 tension_scale을 0, 0.5, 1, 2, 5, 10으로 변화시켰을 때
역U자 곡선이 관측되었다:

```
  tension_scale vs 정확도 (MNIST 관측값)

  정확도(%)
  98.0 |        * *
  97.5 |      *     *
  97.0 |    *         *
  96.5 |  *             *
  96.0 |*                 *
  95.5 |                    *
  95.0 |                      *
       +--+--+--+--+--+--+--+--
       0  0.5  1  1.5  2   5  10
              tension_scale

  최적점: tension_scale ≈ 0.47 (C51에서 관측)
  0.47 ≈ 1/2 (리만 임계선 Re(s) = 1/2)
```

이것은 Yerkes-Dodson 법칙(각성 수준의 역U자 관계)과 구조적으로 동일하다.
심리학에서 Yerkes-Dodson 법칙의 핵심은 **과제 난이도에 따라 최적 각성
수준이 달라진다**는 것이다. 쉬운 과제는 높은 각성이 최적이고, 어려운
과제는 낮은 각성이 최적이다.

의식엔진에서도 동일한 패턴이 나타나는가?

### 관련 가설

| 가설 | 관계 | 내용 |
|------|------|------|
| H283 | 선행 | nonlinear threshold — 장력의 비선형 임계점 |
| H284 | 연결 | auto-regulation — 장력 자기조절 |
| H074 | 이론 | optimal theta — 위상 최적점 |
| H320 | 데이터 | tension_scale log growth — 스케일의 대수 성장 |
| H342 | 교차 | 장력 인과 효과의 난이도 비례 |

## 수학적 모델

역U자 커브의 가능한 형태:

```
  모델 1: 가우시안 (단순)
    A(s) = A_max * exp(-(s - s_opt)^2 / (2 * sigma^2))
    s_opt = f(C), sigma = g(C)

  모델 2: 베타 분포 형태 (비대칭 허용)
    A(s) = s^(a-1) * (1-s)^(b-1) / B(a,b) + baseline
    a, b = h(C)

  모델 3: 물리적 모델 (tension as energy)
    A(s) = A_0 + k*s - lambda*s^2
    최적: s_opt = k / (2*lambda)
    k, lambda = functions of complexity C
```

### 과제 복잡도와 최적 스케일의 예측 관계

```
  최적 tension_scale vs 과제 복잡도

  s_opt
  1.0 |
  0.9 |
  0.8 |                              시나리오 A: 복잡할수록 높음
  0.7 |                         ___/ (Yerkes-Dodson 반대)
  0.6 |                    ___/
  0.5 |  * MNIST      ___/
  0.4 |           ___/
  0.3 |      ___/     시나리오 B: 복잡할수록 낮음
  0.2 | ___/          (Yerkes-Dodson 동일)
  0.1 |/
  0.0 +--+--+--+--+--+--+--+--
      0  2  4  6  8  10 12 14
         과제 복잡도 (entropy bits)

  MNIST:         C ≈ 3.32 bits (10 classes, 쉬움), s_opt ≈ 0.47
  Fashion-MNIST: C ≈ 3.32 bits (10 classes, 중간), s_opt = ?
  CIFAR-10:      C ≈ 3.32 bits (10 classes, 어려움), s_opt = ?

  같은 10-class라도 시각적 복잡도가 다름
  → effective complexity로 측정 필요
```

### 데이터셋별 예상 역U자 커브

```
  정확도 (각 데이터셋 내 정규화)

  1.0 |     M           F         C
      |    / \         / \       / \
  0.9 |   /   \       /   \     /   \
      |  /     \     /     \   /     \
  0.8 | /       \   /       \ /       \
      |/         \ /         X         \
  0.7 |           X         / \         \
      |          / \       /   \         \
  0.6 |         /   \     /     \         \
      |        /     \   /       \         \
  0.5 +--+--+--+--+--+--+--+--+--+--+--+--
      0     0.5    1.0    1.5    2.0    3.0
                 tension_scale

  M = MNIST (피크 ≈ 0.47)
  F = Fashion-MNIST (피크 ≈ ?)
  C = CIFAR-10 (피크 ≈ ?)

  예측: 피크가 오른쪽으로 이동? 왼쪽으로 이동?
  → Yerkes-Dodson이면 왼쪽 (어려울수록 낮은 장력)
  → 반대이면 오른쪽 (어려울수록 높은 장력 필요)
```

## 검증 계획

```
  실험 1: CIFAR-10 역U자 커브 스캔
    - tension_scale = [0, 0.1, 0.2, 0.3, 0.5, 0.7, 1.0, 1.5, 2.0, 3.0, 5.0]
    - 윈도우 RTX 5070에서 실행 (GPU 필요)
    - 각 값에서 정확도 + 클래스별 정확도 기록
    - 역U자 확인 + 피크 위치 측정

  실험 2: Fashion-MNIST 스캔 (동일 조건)
    - 3개 데이터셋의 피크 위치 비교

  실험 3: 피크 위치와 복잡도의 관계
    - effective complexity 정의:
      (a) confusion matrix의 entropy
      (b) baseline 정확도의 역수
      (c) inter-class distance의 평균
    - s_opt vs C 플롯 → 멱법칙/대수 피팅

  실험 4: 수학적 상수 근접성
    - MNIST s_opt ≈ 0.47 ≈ 1/2
    - CIFAR s_opt ≈ ? → 1/e? 1/3? ln(4/3)?
    - 텍사스 명사수 검정

  실험 5: 자기조절과의 교차 (H284)
    - auto-regulation ON/OFF에서 역U자 형태 비교
    - auto-regulation이 피크를 자동으로 찾아가는가?
```

## 해석/의미

### Yerkes-Dodson과의 대응

| Yerkes-Dodson | 의식엔진 |
|---------------|----------|
| 각성(arousal) | 장력(tension) |
| 성과(performance) | 정확도(accuracy) |
| 과제 난이도 | 데이터셋 복잡도 |
| 최적 각성 수준 | 최적 tension_scale |
| 역U자 곡선 | 역U자 곡선 (관측됨) |

Yerkes-Dodson 법칙은 1908년에 발견된 100년 넘은 심리학 법칙이다.
의식엔진에서 동일한 패턴이 나타나면, 이것은 단순한 수학적 모델이 아니라
**인지 구조의 근본적 특성을 포착하고 있다**는 강한 증거가 된다.

특히 최적점이 수학적 상수(1/2, 1/e, 1/3 등)에 수렴한다면:
- 1/2 = 리만 임계선 = 질서와 혼돈의 경계
- 1/e = 골든존 중심 = 자연상수의 역수
- 1/3 = 메타 부동점 = 축소사상의 수렴점

이 중 어느 것에 수렴하느냐에 따라, 장력의 수학적 본질에 대한 단서를 얻는다.

### 과제 적응적 장력의 실용적 가치

최적 장력이 과제마다 다르다면, 실용적으로:
1. auto-regulation (H284)이 이 최적점을 자동으로 찾아가야 한다
2. LLM에서 토큰별 "난이도"를 추정하여 장력을 동적 조절할 수 있다
3. 이것은 human attention과 직접 비유 가능 → 설명 가능한 AI

## 한계

- MNIST의 역U자가 noise일 수 있음 (오차 범위 내)
- 3개 데이터셋만으로는 피팅에 자유도가 부족 (최소 5-6개 필요)
- tension_scale의 이산적 스캔으로는 피크 위치가 부정확할 수 있음
- Yerkes-Dodson과의 유사성이 표면적일 수 있음 (메커니즘이 다름)
- 과제 복잡도의 정의가 자의적 (entropy vs baseline 정확도 vs 기타)

## 다음 단계

1. CIFAR-10 tension_scale 스캔 실행 (윈도우 PC, 우선순위 높음)
2. 피크 위치 확인 → MNIST 0.47과 비교
3. H342와 교차: 난이도 비례 패턴이 역U자의 "하강 구간"에서만 나타나는가?
4. H284와 결합: auto-regulation이 과제별 최적점을 학습하는지 확인
5. 확인되면 논문 후보 등록: "Yerkes-Dodson Law in Artificial Consciousness"
