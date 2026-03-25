# H-CX-98: PH 조기 종료 — H0_gap 기반 early stopping이 val_loss 기반보다 빠르다

> H0_gap이 임계값을 넘는 시점이 val_loss가 증가하기 시작하는 시점보다 앞선다.
> PH가 과적합을 val_loss보다 먼저 감지 → 더 나은 early stopping 기준.

## 배경

- H-CX-95: H0_gap vs gen_gap r=0.998 (CIFAR)
- gap_detector: 에폭 2에서 이미 ALERT
- val_loss는 보통 에폭 5~10에서야 증가 시작

## 예측

1. H0_gap alert 시점 < val_loss 증가 시점
2. H0_gap 기반 early stop의 최종 test_acc >= val_loss 기반
3. H0_gap 기반이 평균 2-5 에폭 더 빠른 종료

## 검증 상태

- [ ] alert 시점 비교
- [ ] 최종 정확도 비교
