# H-CX-78: 골든존 시너지 스케일링 — 난이도 보정 시 시너지 최적점 수렴

> H-CX-67에서 CIFAR만 골든존에서 벗어남. 데이터셋 난이도(baseline accuracy)로
> 장력을 정규화하면 시너지 최적점이 모든 데이터셋에서 1/e로 수렴.

## 배경

- H-CX-67: MNIST Q3(0.340), Fashion Q3(0.341) ≈ 1/e, CIFAR Q5(0.644) 불일치
- CIFAR baseline acc 54% << MNIST 98%, Fashion 89%

## 예측

1. 장력을 accuracy로 정규화 (tension / accuracy)하면 시너지 peak 위치 수렴
2. 시너지 크기가 1-accuracy에 비례 (어려울수록 시너지 절대값 큼)
3. 정규화된 최적점이 3 데이터셋에서 1/e ± 0.05 이내

## 검증 방법

```
1. H-CX-67 실험의 quintile별 (tension, accuracy, synergy) 데이터 재활용
2. 정규화: tension_norm = tension / (max_tension × baseline_acc)
3. 정규화된 quintile에서 시너지 peak 위치 재계산
```

## 관련 가설

- H-CX-67, 골든존 상수 체계

## 한계

- 정규화 방법이 임의적 (post-hoc fitting 위험)

## 검증 상태

- [ ] 정규화 후 시너지 peak
- [ ] 3 데이터셋 수렴 확인
