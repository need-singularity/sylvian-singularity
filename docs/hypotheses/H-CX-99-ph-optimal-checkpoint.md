# H-CX-99: PH 최적 체크포인트 — H0_gap이 최소인 에폭이 최적 모델

> H0_gap이 최소인(train/test PH가 가장 유사한) 에폭의 모델이
> 최고 test accuracy를 달성한다. "위상적 균형" = 최적 일반화.

## 배경

- H-CX-95: H0_gap과 gen_gap r=0.998
- gap_detector: H0_gap이 단조 증가 → 최소는 에폭 1 근처

## 예측

1. min(H0_gap) 에폭의 test_acc = 최고 또는 최고 근처
2. H0_gap 기반 체크포인트 선택이 val_loss 기반과 동등 이상
3. 여러 seed에서 일관적

## 검증 상태

- [ ] H0_gap 최소 에폭 vs best test_acc 에폭
