# H-CX-102: PH 정규화 — H0_gap을 loss에 추가하면 과적합 감소

> loss = CE + lambda * |H0_train - H0_test|
> PH 차이를 줄이도록 학습 → 위상적 일반화 강제 → 과적합 감소.

## 배경

- H-CX-95: H0_gap vs gen_gap r=0.998
- 감지 → 예방으로 전환: H0_gap을 최소화하면 과적합도 최소화?

## 예측

1. PH 정규화 모델의 test_acc > baseline (특히 CIFAR)
2. 과적합 갭(train-test) 감소
3. lambda 최적값이 골든존(1/e) 근처

## 검증 상태

- [ ] PH 정규화 학습
- [ ] baseline 비교
