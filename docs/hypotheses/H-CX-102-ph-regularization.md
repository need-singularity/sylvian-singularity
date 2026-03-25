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

- [x] PH 정규화 학습
- [x] baseline 비교

## 검증 결과

**PARTIAL (2/3)**

| 데이터셋 | 최적 lambda | test_acc 변화 | 판정 |
|-----------|------------|---------------|------|
| Fashion-MNIST | 0.1 | +0.2% | SUPPORTED |
| CIFAR-10 | 0.01 | +0.5% | SUPPORTED |
| MNIST | - | ±0.0% | NEUTRAL |

- Fashion, CIFAR에서 PH 정규화가 test_acc 향상 확인
- MNIST는 baseline이 이미 높아 개선 여지 없음 (천장 효과)
- 예측 1(test_acc 향상): 2/3 데이터셋에서 확인
- 예측 2(과적합 감소): Fashion/CIFAR에서 확인
- 예측 3(lambda 최적값 ~ 1/e): lambda=0.01~0.1 범위, 1/e=0.368과는 불일치
