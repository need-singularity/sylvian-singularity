# 가설 301: 분열 이상탐지 = 적응 면역 시스템 (교차 도메인: 면역학 ↔ 의식)

> **분열+독립학습+간장력 이상탐지는 적응 면역 시스템과 구조적으로 동형이다. parent=줄기세포, 분열=V(D)J 재조합, 독립학습=흉선 선택, 간장력=항원-항체 불일치 감지. 면역학의 클론 선택 이론이 의식엔진에서 재현된다.**

## 대응표

```
  면역 시스템              의식엔진 분열 이상탐지
  ────────────────────    ────────────────────────
  조혈줄기세포 (HSC)       parent engine
  V(D)J 재조합             mitosis (random perturbation)
  미성숙 T세포             children (분열 직후)
  흉선 양성 선택           독립 학습 (정상 데이터)
  흉선 음성 선택           (해당 없음 — 자가면역 방지)
  성숙 T세포               학습 완료된 children
  항원 제시                이상 데이터 입력
  TCR-항원 불일치          간 장력 (T_inter)
  면역 반응                이상 탐지 (AUROC > 0.5)
  클론 확장                (미구현 — 성공한 child 복제?)
  면역 기억                (미구현 — 이상 패턴 저장?)
```

## 핵심 유사성

```
  1. 다양성 생성:
     면역: V(D)J → ~10^15 다른 수용체
     엔진: mitosis + random noise → 다른 가중치
     → 둘 다 "같은 원본에서 다양한 변형 생성"

  2. 자기/비자기 구분:
     면역: 자기 항원에 반응하지 않는 T세포만 생존
     엔진: 정상 데이터로 학습 → 정상에 낮은 장력
     → 둘 다 "정상에 반응하지 않도록 선택"

  3. 불일치 감지:
     면역: TCR이 외래 항원과 불일치 → 활성화
     엔진: children 출력이 이상에서 불일치 → 높은 T_inter
     → 둘 다 "합의 실패 = 경보"

  4. 앙상블 효과:
     면역: 수천 종의 T세포가 서로 다른 항원 감지
     엔진: N개 children이 서로 다른 이상 감지
     → 가설 297(앙상블 다양성)과 일치
```

## 차이점 (중요!)

```
  면역에는 있지만 엔진에 없는 것:
    1. 음성 선택: 자가면역 방지 메커니즘
       → 엔진에서 구현하면? 정상에 너무 반응하는 child 제거
       → "자가면역 = false positive" 감소?

    2. 클론 확장: 성공적 감지 후 해당 클론 복제
       → 엔진에서 구현하면? 이상 잘 감지한 child를 더 분열
       → "적응적 이상탐지"?

    3. 면역 기억: 한 번 감지한 이상 패턴 저장
       → Phase 4(시간 연속성)와 결합?
       → state_memory에 이상 패턴 저장?
```

## 새 아키텍처 제안: AdaptiveImmuneEngine

```python
  class AdaptiveImmuneEngine:
      def __init__(self, parent, n_clones=8):
          self.clones = [mitosis(parent) for _ in range(n_clones)]
          self.fitness = [0] * n_clones  # 감지 성공 횟수

      def detect(self, x):
          outputs = [c(x) for c in self.clones]
          pairwise_tension = mean_pairwise_diff(outputs)
          return pairwise_tension  # 이상 점수

      def adapt(self, x, is_anomaly):
          # 클론 확장: 이상 잘 감지한 클론 복제
          if is_anomaly:
              best_clone = argmax(individual_tension)
              new_clone = mitosis(best_clone, scale=0.001)
              replace_worst(self.clones, new_clone)
          # 음성 선택: 정상에 너무 반응하는 클론 제거
          else:
              worst_clone = argmax(individual_tension)  # false positive
              self.fitness[worst_clone] -= 1
              if self.fitness[worst_clone] < threshold:
                  remove_and_replace(worst_clone)
```

## 검증 방향

```
  Phase 1: 기본 분열 이상탐지 (H296, 이미 확인)
  Phase 2: 음성 선택 추가 → false positive 감소?
  Phase 3: 클론 확장 추가 → 적응적 AUROC 향상?
  Phase 4: 면역 기억 추가 → 반복 이상 즉시 감지?
```

## 상태: 🟨 미실험 (구조적 비유 + 코드 제안)
