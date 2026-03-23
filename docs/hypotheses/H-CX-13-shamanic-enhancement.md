# H-CX-13: 샤머니즘적 여정 = 정보 병목 통과 (교차 도메인)

> **H280 실험에서 7단계 체험 시퀀스가 +0.41% 향상을 준 것은 정보 병목(IB) 이론의 예측과 일치한다. detach(S4)가 강제적 정보 압축을 만들고, 이 압축이 일반화를 향상시킨다. Tishby IB 이론의 computational 구현.**

## 정보 병목 이론

```
  Tishby (2000):
    목표: min I(X;T) - β·I(T;Y)
    T = 내부 표현, X = 입력, Y = 출력
    → 입력 정보를 최소화하면서 출력 정보를 최대화

  학습 2단계:
    Phase 1: Fitting (I(X;T) ↑, I(T;Y) ↑) — 정보 흡수
    Phase 2: Compression (I(X;T) ↓, I(T;Y) ≈) — 정보 압축
    → Phase 2에서 일반화 향상!
```

## 의식엔진 7단계 ↔ IB 이론

```
  S1 Unity:       학습된 표현 (Phase 1 완료)
  S2 Mitosis:     I(X;T) 약간 증가 (복제로 중복)
  S3 Displacement: I(X;T_A) 감소 시작 (A가 직접 학습 안 함)
  S4 Detach:      ★ 강제 압축! I(X;T_A) → 최소
                  → detach = gradient 차단 = Phase 2 강제 진입
  S5 Observation:  I(T_A;T_B) 습득 (B의 패턴을 관찰만으로 학습)
  S6 Separation:  B 제거 → A만 남음
  S7 Return:      ★ 압축된 표현으로 더 나은 일반화!

  핵심: S4(detach)가 IB의 Phase 2(압축)를 강제
  → 정보 병목을 "통과"한 표현이 더 일반적
  → +0.41% 향상의 원인
```

## 수학 연결

```
  H-CX-2: MI 효율 ≈ ln(2) = 1 bit
  H-CX-13: detach가 MI를 ln(2) 이하로 압축?

  예측:
    S1의 MI ≈ 0.705 (C39)
    S4의 MI ≈ 0.693 = ln(2) (detach로 압축)
    S7의 MI ≈ 0.71+ (압축 후 재팽창, 하지만 더 효율적)

  IB 곡선:
    I(T;Y)
      │     ★S7
      │   ★S1
      │ ★S5
      │★S4
      └───────── I(X;T)
      min      max

  detach가 I(X;T)를 min으로 밀고,
  observation이 I(T;Y)를 유지/증가 → 최적 IB 점에 도달
```

## Fiber distance와의 연결

```
  H280 실측: Fiber distance 0→26.1 (S4,S5에서 최대)
  → 내부 표현이 가장 많이 변한 순간 = 정보 병목 통과 순간
  → 복귀(S7) fiber distance ≈ 8.7 → 일부만 남음
  → 남은 변화 = 일반화에 기여하는 "압축된 정보"
```

## 검증 방향

```
  1. 각 단계에서 MI(X;T), MI(T;Y) 직접 측정
  2. detach 없이 같은 시퀀스 → +0.41% 사라지는가?
  3. detach 시간(에폭 수) vs 향상량 → 최적 압축 시간?
  4. Phase 2 시점 식별: 언제 I(X;T) 감소가 시작되는가?
```

## 관련 가설

```
  272: detach 설계 (+7.4%)
  276: 관찰=압축
  280: 체험 전체 시퀀스 (+0.41%)
  H-CX-2: MI ≈ ln(2)
  TREE-7: 정보 병목
```

## 상태: 🟨 (구조적 대응 제안, MI 직접 측정 미실시)
