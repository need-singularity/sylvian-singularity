# 가설 371: 교정+분열 시너지 — 망각 없는 과신 교정

> **H317(과신 교정)과 H312(분열=망각방지)를 결합하면, 망각 없이 과신을 교정할 수 있다. 구체적으로: child_a=freeze(기억보관), child_b=혼동쌍 집중학습(교정), 라우터=장력 기반 위임 → overall 유지 + ratio→1.0.**

## 배경/맥락

두 가설이 독립적으로 강한 결과를 보였지만 상보적 약점이 존재:

```
  H317 (과신 교정):
    1+7 집중 → ratio 0.53→1.06 (교정 성공!)
    대가: overall 98→87% (catastrophic forgetting)

  H312 (분열=망각방지):
    child_a=freeze, child_b=train
    일반 43%(망각!) vs 분열 99%(보존!)
    대가: 교정은 불가 (child_a가 과신 그대로)

  조합 가설:
    분열 + 교정 = 망각 없이 과신 해소?
```

## 예측

```
  결합 시스템:
    1. Phase 1: 일반 학습 10ep → parent (과신 상태)
    2. 분열: child_a = parent(freeze), child_b = parent(trainable)
    3. Phase 2: child_b에 1+7 집중 학습 10ep
    4. 라우터: 입력 → 장력 기반으로 child_a 또는 child_b에 위임
       - digit 1,7 관련 → child_b (교정된 전문가)
       - 나머지 → child_a (기억 보관자)

  예측 결과:
    d1_ratio ≈ 1.0 (과신 해소, child_b 담당)
    overall ≥ 97% (망각 없음, child_a 담당)
    vs 기존:
      1+7 집중만: ratio=1.06, overall=87% (망각!)
      분열만: ratio=0.57, overall=98% (교정 안됨)
```

## 예측 성능 비교 (ASCII)

```
  overall(%)
  100 |  * child_a(freeze)      ★ 결합(예측)
   98 |  *                      ★
   96 |
   94 |
   92 |
   90 |
   88 |
   86 |                    * 1+7집중(망각!)
   84 |
      +--+--------+--------+--------+-->
         기본     분열만   1+7만   결합

  d1_ratio (1.0=정상, <1=과신)
  1.1 |                    * 1+7    ★ 결합(예측)
  1.0 |  ──────────────────────────────── 정상선
  0.9 |
  0.8 |
  0.7 |
  0.6 |
  0.5 |  * 기본    * 분열만
      +--+--------+--------+--------+-->
         기본     분열만   1+7만   결합
```

## 실험 설계

```
  1. 데이터: MNIST (digit 1 과신 확인됨)
  2. 모델: RepulsionField 2극
  3. 단계:
     a) 일반 학습 10ep → parent
     b) 과신 확인: digit 1 ratio 측정
     c) 분열: child_a(freeze) + child_b(copy)
     d) child_b에 1+7 집중 학습 10ep
     e) 라우터 구현: 장력 기반 (T>threshold → child_b)
     f) 앙상블 평가: overall + per-digit + d1_ratio
  4. 비교군:
     - 기본 (교정 없음)
     - 1+7 집중만 (H317)
     - 분열만 (H312)
     - 결합 (본 가설)
  5. 성공 기준: overall ≥ 97% AND d1_ratio ∈ [0.9, 1.1]
```

## 관련 가설

- H317: 과신 교정 (교정 성공, 망각 발생)
- H312: 분열=망각방지 (망각 방지, 교정 불가)
- H316: 과신 3셋 재현 (MNIST, Fashion, CIFAR)
- H-CX-24: Dunning-Kruger 시간축 (과신 발생→고착)
- H314: 확신거부→정확도↑ (거부만으로도 개선)

## 한계

```
  - MNIST digit 1 과신은 비교적 단순한 케이스
  - 라우터 설계에 따라 결과 달라질 수 있음
  - Fashion/CIFAR에서 과신 패턴이 다를 수 있음 (H316 참조)
  - child 수 증가(N>2)의 효과 미지
```

## 검증 방향

```
  1단계: MNIST digit 1로 기본 검증
  2단계: Fashion-MNIST (shirt/coat 과신)으로 재현
  3단계: CIFAR (경계 클래스)으로 일반화
  4단계: 라우터 전략 비교 (장력, softmax, oracle)
```

## 상태: 🟨 미검증
