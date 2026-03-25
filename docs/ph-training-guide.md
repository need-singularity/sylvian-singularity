# PH 기반 모델 학습 가이드

> PH 발견들을 실제 모델 학습에 적용하는 방법.

## 1. 학습 전: 난이도 예측 (H-CX-101/160)

```python
# 1에폭만 학습 → H0_total로 최종 정확도 예측
model = PureFieldEngine(dim, 128, n_classes)
train_1_epoch(model, train_loader)
h0 = compute_h0(model, test_loader)

# H0 높을수록 쉬움
# MNIST H0≈4.2 → 98%, Fashion H0≈2.3 → 89%, CIFAR H0≈2.1 → 54%
print(f"예상 난이도: H0={h0:.2f}")
if h0 > 3.5: print("쉬움 — 적은 에폭으로 충분")
elif h0 > 2.0: print("보통")
else: print("어려움 — 많은 에폭/큰 모델 필요")
```

## 2. 학습 중: 과적합 실시간 감지 (H-CX-95)

```python
from calc.generalization_gap_detector import compute_h0

for epoch in range(max_epochs):
    train(model, train_loader)

    # 매 에폭: train/test PH 비교
    h0_train = compute_h0(model, train_loader)
    h0_test = compute_h0(model, test_loader)
    h0_gap = abs(h0_train - h0_test)

    if h0_gap > threshold:
        print(f"⚠️ 과적합 감지! (gap={h0_gap:.4f})")
        break  # 조기 종료

    # gap detector: CIFAR r=0.998, Fashion r=0.846
```

## 3. 학습률 자동 탐색 (H-CX-100)

```python
# H0 CV(변동계수)가 최소인 LR = 최적 LR
best_lr, best_cv = None, 999

for lr in [1e-4, 3e-4, 1e-3, 3e-3, 1e-2]:
    model = PureFieldEngine(dim, 128, n_classes)
    h0s = []
    for epoch in range(10):
        train_with_lr(model, train_loader, lr)
        h0s.append(compute_h0(model, test_loader))

    cv = np.std(h0s) / np.mean(h0s)
    if cv < best_cv:
        best_cv = cv
        best_lr = lr

print(f"최적 LR: {best_lr} (H0 CV={best_cv:.4f})")
# CIFAR에서 H0 CV 최소 LR = 최고 accuracy LR 일치!
```

## 4. 혼동 쌍 사전 파악 (H-CX-66/82)

```python
# 에폭 1에서 이미 혼동 쌍 완벽 예측 (P@5=1.0)
model = PureFieldEngine(dim, 128, n_classes)
train_1_epoch(model, train_loader)
merges = compute_merge_order(model, test_loader)

print("혼동 쌍 (학습 시작 직후 확정):")
for dist, i, j in sorted(merges)[:5]:
    print(f"  {class_names[i]} ↔ {class_names[j]}: d={dist:.4f}")

# → 이 쌍에 집중 학습? (H-CX-87: 효과 없음!)
# → 대신: 이 쌍의 데이터 품질 점검, 라벨 오류 확인
```

## 5. 적대적 취약점 예측 (H-CX-104)

```python
# merge distance 짧은 쌍 = FGSM에 취약 (r=-0.71)
vulnerable_pairs = sorted(merges)[:3]
print("FGSM 취약 쌍:")
for dist, i, j in vulnerable_pairs:
    print(f"  {class_names[i]}-{class_names[j]}: 공격 성공률 높음")

# → adversarial training에서 이 쌍 우선 강화
```

## 6. 아키텍처 선택 (H-CX-88/107)

```python
# PH는 아키텍처에 불변 (top-5 100%)
# → 아키텍처 선택은 PH에 영향 없음
# → 대신: 파라미터 효율성으로 선택

# hidden_dim 64/128/256 → PH 동일 (tau=0.83~0.94)
# → 작은 모델로 PH 분석 후, 큰 모델에 적용 가능!
```

## 7. 멀티태스크 학습 (분열/분류)

```python
# PH dendrogram = 의미 계층 (89% purity)
# → dendrogram 기반 태스크 분해

dendrogram = compute_dendrogram(model, test_loader)
# CIFAR: {cat,dog}→동물, {auto,truck}→기계

# 상위 분류(동물 vs 기계) 먼저 학습
# → 하위 분류(cat vs dog) 나중에 학습
# = curriculum learning의 PH 버전
```

## 8. ConsciousLM (LLM) 학습 시

```python
# byte-level LLM에서 PH 적용:
# 바이트 256개 → 그룹 13개 (lower, upper, digit, korean, ...)
# 그룹별 방향벡터 → PH 계산

# 모니터링:
# - H0_gap: 과적합 감지
# - merge 순서: 어떤 바이트 그룹이 혼동되는지
# - dendrogram: 언어 구조의 위상적 계층

# ⚠️ H-CX-95 LLM 미검증 — 경량화 버전으로 재시도 필요
```

## 요약: PH 학습 체크리스트

```
  학습 전:
  □ 1에폭 H0_total → 난이도 예측
  □ merge 순서 → 혼동 쌍 파악
  □ H0 CV sweep → 최적 LR

  학습 중:
  □ 에폭별 H0_gap → 과적합 감지
  □ H0 트렌드 → 학습 진행 모니터링
  □ merge 안정성 → 수렴 판단

  학습 후:
  □ dendrogram → 의미 계층 확인
  □ confusion PCA → 데이터 구조 이해
  □ 취약 쌍 → 적대적 방어 우선순위
```

## 관련 도구

```
  calc/ph_confusion_analyzer.py     — 통합 PH 분석
  calc/generalization_gap_detector.py — 과적합 감지
  calc/precognition_system.py       — 3채널 예지
  ph_module.py (anima)              — 실시간 PH
```

## 관련 가설

| 가설 | 적용 | 효과 |
|------|------|------|
| H-CX-95 | 과적합 감지 | r=0.998 |
| H-CX-100 | LR 탐색 | H0 CV 최소=최적 |
| H-CX-101 | 난이도 예측 | H0_ep1 vs acc r>0.9 |
| H-CX-66 | 혼동 예측 | r=-0.97 |
| H-CX-82 | 에폭1 예측 | P@5=1.0 |
| H-CX-104 | FGSM 취약 | r=-0.71 |
| H-CX-102 | PH 정규화 | +0.5% (CIFAR) |
