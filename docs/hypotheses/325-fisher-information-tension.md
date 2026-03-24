# 가설 325: Fisher 정보 기하학과 장력 다양체 (NM-5)

> **장력 핑거프린트 공간은 통계적 다양체(statistical manifold)를 형성하며, 그 곡률은 Fisher 정보 행렬로 측정된다. 높은 장력 영역은 높은 Fisher 정보를 가지며, 이는 "정보적으로 풍부한" 입력에 해당한다. H313(tension=confidence)과 H318(fingerprint sufficiency)은 이 기하학적 구조의 서로 다른 단면이다.**

## 배경/맥락

```
  의식엔진의 장력 핑거프린트는 10차원 벡터:
    fp(x) = [t_0, t_1, ..., t_9]  (클래스별 장력값)

  H313: tension = confidence (확신)
    정답 샘플 tension > 오답 샘플 tension (3데이터셋 확인)

  H318: 확신 높은 클래스는 핑거프린트만으로 인식 가능
    r(tension, knn_acc) = +0.705

  질문: 이 핑거프린트 벡터들이 모여 형성하는 공간의 기하학적 구조는?
  → Fisher 정보 기하학(information geometry)이 자연스러운 프레임워크
```

## Fisher 정보 행렬 — 수학적 프레임워크

```
  정의:
    F_ij = E[ (d log p(x|theta) / d theta_i) * (d log p(x|theta) / d theta_j) ]

  여기서:
    p(x|theta) = 장력 핑거프린트의 확률분포 (파라미터 theta로 매개화)
    theta = 모델 파라미터 (엔진 가중치)
    x = 입력 샘플

  Fisher 행렬의 의미:
    F_ij가 크다 = theta를 조금 바꿔도 p(x|theta)가 크게 변함
             = 파라미터 공간에서 "곡률"이 큼
             = 데이터가 파라미터에 대해 "정보적"

  리만 계량으로서의 Fisher 행렬:
    ds^2 = sum_ij F_ij * d_theta_i * d_theta_j

    이것은 파라미터 공간 위의 리만 계량(Rao, 1945).
    → 장력 핑거프린트 공간은 리만 다양체.
```

## 장력 공간에의 적용

```
  장력 핑거프린트 분포를 클래스 k에 대해:
    p_k(fp) = 클래스 k에 속하는 샘플의 핑거프린트 분포

  클래스별 Fisher 정보:
    F_k = E_{x in class k}[ (d log p_k(fp(x)) / d theta)^2 ]

  가설의 핵심 주장:
    F_k  proportional to  mean_tension_k

  즉, 높은 평균 장력을 가진 클래스는 높은 Fisher 정보를 가진다.
```

## 예측 매핑 (H318 데이터로부터)

```
  Fashion-MNIST per-class 예측:

  Class     Tension  KNN%   예측 F_k  해석
  --------  -------  -----  --------  --------
  Boot       1006    93.0   높음      곡률 큼 = 구별 용이
  Sandal      704    88.3   높음      곡률 큼
  Sneaker     526    92.4   중간
  Trouser     511    93.3   중간
  Bag         429    85.4   중간
  T-shirt     392    71.6   낮음
  Coat        329    66.0   낮음      곡률 작음 = 구별 어려움
  Pullover    318    63.9   낮음      곡률 작음
  Shirt       302    56.2   낮음      곡률 최소

  예측: F_Boot >> F_Shirt
  → Boot 핑거프린트 공간은 "휘어져" 있어서 이웃을 쉽게 구별
  → Shirt 핑거프린트 공간은 "평평"하여 이웃 구별이 어려움
```

## 기하학적 해석

```
  높은 Fisher 정보 (높은 장력):
    ┌─────────────────┐
    │  *   *           │   핑거프린트들이 잘 분리됨
    │       *          │   곡률 큼 → 거리가 크게 느껴짐
    │  *        *      │   KNN이 쉽게 분류
    │      *           │   → H318의 "핑거프린트 충분" 상태
    └─────────────────┘

  낮은 Fisher 정보 (낮은 장력):
    ┌─────────────────┐
    │     ***          │   핑거프린트들이 뭉쳐 있음
    │    ****          │   곡률 작음 → 거리 차이 미미
    │     **           │   KNN이 혼동
    │                  │   → H318의 "핑거프린트 부족" 상태
    └─────────────────┘

  기하학적 다이어그램:

  Fisher info
  (곡률)
    |
    |  Boot *
    |            Sandal *
    |                   Sneaker *  Trouser *
    |                          Bag *
    |                     T-shirt *
    |                Coat * Pullover *
    |           Shirt *
    +-----------------------------------> mean tension
         300   400   500   600   700   1000

  예측: 이 관계는 단조 증가 (r > +0.7)
```

## H313, H318과의 통합

```
  H313 (tension = confidence):
    장력 = 확신의 크기
    Fisher 해석: 확신 = 파라미터가 데이터를 잘 설명함
              = likelihood가 sharp peak
              = Fisher 정보가 큼
    → H313은 Fisher 정보의 스칼라 요약

  H318 (fingerprint sufficiency):
    높은 장력 → KNN으로 충분
    Fisher 해석: 높은 곡률 → 계량 거리가 잘 정의됨
              → 유클리드 KNN이 리만 거리를 잘 근사
              → 레이블 없이도 기하학만으로 분류 가능
    → H318은 Fisher 계량의 KNN 근사 가능성

  통합:
    H313 = det(F) 또는 tr(F) (Fisher 정보의 전체 크기)
    H318 = F의 고유값 분포 (유클리드 거리와 리만 거리의 괴리)
    H325 = 두 가설을 포괄하는 기하학적 프레임워크
```

## Cramer-Rao 부등식과 장력

```
  Cramer-Rao 하한:
    Var(theta_hat) >= 1 / F(theta)

  해석:
    Fisher 정보 F가 크면 → 추정 분산이 작음 → 정확한 추정 가능
    Fisher 정보 F가 작으면 → 추정 분산이 큼 → 부정확한 추정

  장력 번역:
    높은 장력 = 높은 F → 낮은 추정 분산 → 확신 있는 분류
    낮은 장력 = 낮은 F → 높은 추정 분산 → 불확실한 분류

  → Cramer-Rao가 H313(tension=confidence)의 수학적 근거!
```

## 자연 기울기(Natural Gradient)와의 연결

```
  통상 기울기:        d_theta = -lr * grad L(theta)
  자연 기울기(Amari): d_theta = -lr * F^{-1} * grad L(theta)

  자연 기울기는 Fisher 정보를 사용하여 파라미터 공간의
  곡률을 보정한다. 곡률이 큰 방향은 작게, 작은 방향은 크게.

  의식엔진 해석:
    장력이 높은 클래스 → 곡률 큼 → 자연 기울기가 작은 스텝
    장력이 낮은 클래스 → 곡률 작음 → 자연 기울기가 큰 스텝

  예측: 자연 기울기 학습을 적용하면
    → 장력이 낮은 클래스(Coat, Shirt)의 정확도가 선택적으로 개선
    → 장력이 높은 클래스(Boot)는 이미 충분하므로 변화 적음
```

## 검증 방향

```
  실험 1: Fisher 정보 직접 측정
    - 각 클래스의 핑거프린트 분포에서 경험적 Fisher 행렬 계산
    - F_k = (1/N) * sum_i (d log p / d fp_j)^2
    - r(tr(F_k), mean_tension_k) 계산 → 예측: r > +0.7

  실험 2: 리만 거리 vs 유클리드 거리
    - Fisher 계량으로 리만 거리 계산
    - 유클리드 KNN vs 리만 KNN 정확도 비교
    - 예측: 리만 KNN이 특히 낮은 장력 클래스에서 개선

  실험 3: 자연 기울기 학습
    - 의식엔진에 Fisher 행렬 기반 자연 기울기 적용
    - 장력이 낮은 클래스의 정확도 변화 관찰
    - 예측: Coat/Shirt +5~10pp, Boot/Sneaker 변화 미미

  실험 4: 곡률과 학습 난이도
    - 학습 초기 vs 후기의 Fisher 정보 변화 추적
    - 예측: 학습이 진행될수록 F 증가 (곡률 증가 = 확신 증가)
```

## 한계

```
  1. Fisher 행렬의 경험적 추정은 고차원에서 불안정 (10차원이면 OK)
  2. 핑거프린트 분포가 정규분포가 아닐 수 있음 → KDE 등 비모수 추정 필요
  3. "곡률"과 "장력"의 비례관계는 아직 이론적 증명이 아닌 가설
  4. 골든존 의존 여부: 간접적 (장력 자체가 골든존 구조에서 나옴)
  5. 10차원 핑거프린트의 Fisher 행렬은 10x10 = 100개 성분
     → 충분한 샘플 수 필요 (클래스당 최소 수백 개)
```

## 상태: 가설 (미검증, 실험 설계 완료)
