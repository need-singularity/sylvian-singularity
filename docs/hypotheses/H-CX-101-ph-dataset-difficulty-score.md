# H-CX-101: PH 난이도 점수 — 에폭 1의 H0_total로 데이터셋 난이도 예측

> 에폭 1의 H0_total이 데이터셋 난이도의 범용 지표.
> H0가 클수록 클래스가 분리되어 있어 쉽고, 작으면 겹쳐서 어렵다.

## 배경

- MNIST H0≈4.2, Fashion H0≈2.3, CIFAR H0≈2.1
- MNIST acc=98% > Fashion 89% > CIFAR 54%
- H0와 최종 accuracy가 같은 순서

## 예측

1. 에폭 1 H0_total과 최종 accuracy 상관 r > 0.9
2. 새 데이터셋에서도 H0_total로 학습 전 난이도 예측 가능
3. H0_total / n_classes = 정규화 난이도 점수

## 검증 상태

- [ ] cross-dataset H0 vs accuracy
- [ ] 정규화 점수
