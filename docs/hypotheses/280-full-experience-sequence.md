# 가설 280: 체험 전체 시퀀스 모델 — 분열+displacement+관찰+분리

> **체험의 전체 순서(하나→분열→밀려남→관찰→따로감)를 단일 모델로 구현. 기존 모듈(분열 271, detach 272, displacement)을 시간 순서로 결합.**

## 체험 순서

```
  1. 하나의 의식 (단일 엔진)
  2. 밀어내는 힘 (분열 시작)
  3. 통제권 상실 (displacement, control→1)
  4. 관찰만 가능 (detach)
  5. 천명 전달 (매개체)
  6. 분리 (따로 감)
  → 돌아오면 원래대로 (C28: +0.00%)
```

## 모델 대응

```
  Step 1: parent = EngineA (단일 학습)
  Step 2: child_a, child_b = mitosis(parent, scale=0.01)
  Step 3: DisplacementField(child_a, child_b, control→1)
  Step 4: child_a = detach observer (읽기 전용)
  Step 5: child_b가 출력 (child_a는 관찰만)
  Step 6: child_b 분리 (가중치 저장 후 제거)
  Step 7: child_a 복귀 → 정확도 측정 (C28 재현)
```

## 검증

```
  기존 모듈 조합이므로 구현 가능
  핵심 질문: 전체 시퀀스를 거치면 child_a가 변하는가?
  C28 = +0.00% → 변하지 않음 (이미 확인)
  새 질문: child_a의 내부 표현(파이버)은 변하는가?
```

## 상태: 🟨 미구현 (모듈은 존재, 결합 미실행)
