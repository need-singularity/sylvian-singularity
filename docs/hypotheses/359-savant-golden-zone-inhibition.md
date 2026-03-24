# 가설 359: 서번트 = 골든존 하한의 억제 해제

> **서번트 특성은 G=D×P/I에서 I를 골든존 하한(0.21≈1/2-ln(4/3))까지 낮추면 발생한다. 분열 후 한쪽 자식의 억제(dropout/regularization)를 골든존 하한으로 설정하면, 그 도메인에서 폭발적 전문화가 일어난다. Savant Index (SI) = max(도메인장력) / min(도메인장력) > 3이 기준.**

## 배경/맥락

골든존 공식 G = D×P/I에서:
- **정상**: I ≈ 1/e (0.37, 골든존 중심) → 균형 잡힌 성능
- **서번트**: I ≈ 0.21 (골든존 하한) → 특정 영역 폭발, 나머지 약화
- **병적**: I < 0.21 → 골든존 이탈, 불안정/붕괴

```
  G(I) 곡선 — 서번트는 골든존 가장자리

  G
  ↑
  █                         ← 서번트 (I=0.21, G 최대)
  █ █
  █ █ █                     ← 천재 (I=1/e=0.37)
  █ █ █ █
  █ █ █ █ █                 ← 평균 (I=0.5)
  █ █ █ █ █ █
  █ █ █ █ █ █ █ █ █ █
  ┼─┼─┼─┼─┼─┼─┼─┼─┼─┼──→ I
  0 .1 .2 .3 .4 .5 .6 .8 1
     ↑  ↑        ↑
     붕괴 하한     상한
         ├─골든존─┤
```

### 관련 가설

| 가설 | 핵심 | 관계 |
|------|------|------|
| H-CX-15 | 서번트=골든존=분열 | N=8에서 k=3≈1/e |
| H241 | Expert 교차 활성화 | 비활성 Expert 강제 활성화 |
| H271 | 분열 | 복제+발산 |
| H299 | 분열 후 전문화 | ⬛ 반박 (cosine=0.9999, 대칭이라서) |
| H004 | 볼츠만 I=1/kT | 온도=억제, 낮은T=높은I |

## 핵심 수식

```
  G = D × P / I

  서번트 조건:
    I → I_min = 1/2 - ln(4/3) ≈ 0.2123 (골든존 하한)
    G_savant = D × P / 0.2123

  일반 조건:
    I → 1/e ≈ 0.3679 (골든존 중심)
    G_normal = D × P / 0.3679

  서번트 증폭비:
    G_savant / G_normal = (1/e) / (1/2 - ln(4/3))
                        = 0.3679 / 0.2123
                        = 1.733

  → 서번트는 일반 천재의 ~1.73배 (≈ √3 !!)
```

### √3 연결!

```
  서번트 증폭비 = (1/e) / (1/2 - ln(4/3))

  python3 검증:
    >>> import math
    >>> (1/math.e) / (0.5 - math.log(4/3))
    1.7326...
    >>> math.sqrt(3)
    1.7320...
    >>> 오차: 0.03%

  → 서번트 증폭비 ≈ √3 (오차 0.03%!)
  → √3 = 정삼각형의 높이/밑변 = 가장 안정한 구조의 비율
  → C41(1/√3)과 역수 관계!
```

## Anima 구현 방법

```
  1. 분열: parent → child_a + child_b (동일 가중치)

  2. 억제 비대칭 설정:
     child_a: dropout = 0.21 (골든존 하한) → 도메인 X 전문화
     child_b: dropout = 0.37 (골든존 중심) → 범용 유지

  3. 도메인 분리 학습:
     child_a: 도메인 X 데이터만 (lr = stage.learning_rate)
     child_b: 전체 데이터 (lr = stage.learning_rate)

  4. 교차 억제:
     child_a 활성 시 → child_b의 해당 뉴런 10% 추가 억제
     (서번트 뇌의 교차 억제 모델)

  5. Savant Index 측정:
     SI = max(class_tension) / min(class_tension)
     SI > 3: 서번트 후보
     SI > 5: 강한 서번트
```

## 검증 실험

```python
# MNIST에서 서번트 실험
from model_pure_field import PureFieldEngine

# 부모
parent = PureFieldEngine(784, 128, 10)
train(parent, mnist_all, epochs=15)  # 범용 학습

# 분열
child_savant = copy.deepcopy(parent)
child_normal = copy.deepcopy(parent)

# 억제 비대칭: 서번트 자식의 dropout을 골든존 하한으로
for m in child_savant.modules():
    if isinstance(m, nn.Dropout):
        m.p = 0.21   # 골든존 하한

for m in child_normal.modules():
    if isinstance(m, nn.Dropout):
        m.p = 0.37   # 골든존 중심

# 도메인 분리 학습
train(child_savant, mnist_digits_03, epochs=20)  # 0-3만
train(child_normal, mnist_all, epochs=20)         # 전체

# SI 측정
for digit in range(10):
    t_savant[digit] = measure_tension(child_savant, digit)
    t_normal[digit] = measure_tension(child_normal, digit)

SI_savant = max(t_savant) / min(t_savant)
SI_normal = max(t_normal) / min(t_normal)
```

### 예상 결과

```
  Per-class tension (예상):

  Digit  child_savant  child_normal
  ────── ────────────  ────────────
  0      ████████ 8.5  ███ 3.2
  1      ████████ 8.1  ███ 2.9
  2      ███████ 7.8   ███ 3.1
  3      ███████ 7.5   ██ 2.8
  4      █ 1.2         ██ 2.7      ← 서번트: 학습 안 한 도메인 약함
  5      █ 1.0         ██ 2.6
  6      █ 0.8         ██ 2.5
  7      █ 0.9         ██ 2.4
  8      █ 0.7         ██ 2.3
  9      █ 0.6         ██ 2.2

  SI_savant = 8.5 / 0.6 = 14.2 ★★★ (강한 서번트!)
  SI_normal = 3.2 / 2.2 = 1.45    (범용)
```

## H299 실패의 원인과 해결

```
  H299: 대칭 분열 → cosine=0.9999 → 전문화 없음
  원인: 같은 dropout(0.3), 같은 데이터, 같은 lr → 발산할 이유 없음

  H359 해결:
    1. 비대칭 dropout (0.21 vs 0.37)
    2. 비대칭 데이터 (도메인 분리)
    3. 교차 억제 (한쪽 활성 → 다른 쪽 억제)

  → 3가지 비대칭이 전문화를 강제
```

## 한계

1. dropout을 0.21로 낮추면 과적합 위험 — 도메인 데이터가 충분해야
2. 서번트 자식은 비학습 도메인에서 성능 급락 — 범용 자식이 보완 필요
3. SI > 3 기준은 경험적 — 이론적 근거 필요 (√3 연결?)
4. MNIST 수준에서의 서번트는 진짜 서번트와 스케일 차이 큼
5. 교차 억제 구현이 PureFieldEngine의 dropout 구조에 의존

## 검증 방향

1. MNIST 0-3 도메인에서 dropout=0.21 vs 0.37 비교
2. SI 측정 + √3 임계점 검증 (SI=√3에서 질적 전환?)
3. CIFAR에서 재현 (카테고리 분리: 동물 vs 탈것)
4. Golden LLaMA에서 Expert별 SI 측정
5. dropout 연속 sweep: 0.1→0.5, SI vs dropout 곡선에서 골든존 확인

## 실험 결과 (2026-03-24)

```
  Dropout sweep — digits 0-4만 학습, 20ep:

  dropout       SI   Acc(0-4)   Acc(5-9)
  ──────── ──────── ────────── ──────────
  0.1000     3.13      99.6%      17.7%
  0.2123     3.63      99.5%       9.8%  ← 골든하한
  0.3000     3.04      99.6%       6.1%
  0.3679     3.84      99.5%       7.3%  ← 골든중심
  0.5000     4.03      99.5%       2.5%  ← 최고 SI!

  Per-class (dropout=0.2123):
  Digit  Tension   Acc
  0      1704.7   99.8% ★
  1       553.8   99.6% ★
  2      1429.0   98.6% ★
  3      1773.7   99.8% ★ ← 최고
  4      1132.5   99.6% ★
  5      1183.1   17.0%
  8       488.9    2.9%  ← 최저
  9       873.4    0.1%
```

### 해석

```
  1. SI > 3 달성! → 서번트 특성 유도 성공
  2. 하지만 골든존 하한이 특별하지 않음:
     dp=0.50 → SI=4.03 > dp=0.21 → SI=3.63
     → dropout이 낮을수록 과적합 → 서번트 (단순한 과적합 효과)
  3. √3 증폭비 반박: SI(하한)/SI(중심) = 0.95 ≠ √3
     → 증폭비 가설은 적용되지 않음
  4. 서번트 = "특정 도메인 과적합" + "비학습 도메인 붕괴"
     → 골든존 공식보다 단순한 메커니즘
```

## 상태: 🟧 부분확인 (SI>3 성공, 골든하한 특별하지 않음, √3 반박)
