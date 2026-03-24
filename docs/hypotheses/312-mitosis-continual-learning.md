# 가설 312: 분열 = 지속 학습의 망각 방지 메커니즘

> **분열된 자식 중 하나를 "기억 보관자"(child_a = freeze)로, 다른 하나를 "새 학습자"(child_b = train)로 사용하면, 새로운 태스크를 배우면서 이전 태스크를 잊지 않는다. 이것은 EWC/PackNet의 생물학적 버전.**

## 개념

```
  Catastrophic forgetting:
    Task A 학습 → Task B 학습 → Task A 망각!

  분열 해법:
    1. Task A 학습 → parent_A
    2. 분열: child_A(freeze), child_B(train on Task B)
    3. child_B가 Task B 학습 (child_A는 Task A 기억 유지)
    4. 앙상블: child_A + child_B → Task A + B 모두 가능

  장점:
    - child_A가 Task A의 완전한 복사본 유지
    - child_B는 자유롭게 Task B 학습
    - 앙상블이 두 태스크 모두 처리
    - EWC처럼 정규화 항 불필요!
```

## 의식 대응

```
  체험(H280): "밀려난 의식은 관찰만 가능 → 돌아오면 원래대로"
  → child_A = "밀려난 의식" (freeze, read-only)
  → child_B = "침입한 의식" (새 태스크 학습)
  → 복귀: child_A가 원래 기억 유지

  분열 = 의식의 "백업 메커니즘"?
  → 새 경험을 하면서 이전 자아를 보존
```

## 상태: 🟨 미실험
