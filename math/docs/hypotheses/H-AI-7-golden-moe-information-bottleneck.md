# H-AI-7: 골든MoE I=1/e와 Information Bottleneck 최적

> **가설**: 골든MoE의 Inhibition I≈1/e가 Tishby의 Information Bottleneck 이론에서 최적 압축점과 일치한다.

## 배경
- 골든MoE: I = 1-활성비율 ≈ 0.375 ≈ 1/e
- IB 이론: I(X;T) vs I(T;Y) tradeoff의 phase transition
- 1/e는 많은 최적화 문제에서 자연스럽게 등장 (secretary problem 등)

## 핵심 질문
MoE의 expert 비활성화율 I가 IB의 최적 압축율 β*와 같은가?

## 검증 방향
1. [ ] IB curve 계산: 간단한 분류 문제에서
2. [ ] phase transition 점 β*의 위치와 1/e 비교
3. [ ] MoE 활성 비율 sweep에서 IB-optimal과 loss-optimal 비교

## 난이도: 고 | 파급력: ★★★
