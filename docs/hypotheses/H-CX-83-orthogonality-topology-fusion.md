# H-CX-83: 직교성-위상 통합 — 결합 시 예지 AUC > 0.95

> 3채널 직교성(H-CX-80, r=0.90)과 H0_total(H-CX-62, r=-0.97)을
> 결합하면 단일 feature보다 강한 예지 시스템 구축 가능.
> 목표: MNIST AUC > 0.95.

## 배경

- H-CX-80: orthogonality와 synergy r=0.90
- H-CX-62: H0_total과 accuracy r=-0.97
- 통합 예지: LR(mag,conf,gap) AUC=0.917

## 예측

1. LR(mag,conf,gap,H0_total) AUC > LR(mag,conf,gap) AUC
2. MNIST에서 AUC > 0.95 달성
3. H0_total이 4번째 독립 feature로 시너지 추가

## 검증 상태

- [ ] 4-feature LR AUC
- [ ] H0_total 추가 gain
