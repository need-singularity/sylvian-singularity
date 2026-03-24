# 가설 327: 골든MoE에서 tension과 PPL의 실제 관계

> **골든MoE(golden_moe.py)가 LLM(골든 LLaMA)에 적용될 때, Expert 간 반발(tension)이 PPL과 어떻게 관련되는가? H-CX-21(tension∝1/PPL)이 LLM 규모에서도 성립?**

## 배경

```
  골든MoE: σ(6)=12 Expert, τ(6)=4 활성
  golden_moe_torch.py: MNIST +0.6%, CIFAR +4.8%
  golden-llama (별도 리포): PPL 136K→4634→목표 <100

  H-CX-21: MNIST에서 tension ∝ 1/PPL
  → LLM에서도? Expert 간 출력 차이(tension) ∝ 1/PPL?
```

## 검증 방법

```
  1. golden-llama 학습 중 Expert 간 tension 추적
  2. 스텝별 tension vs PPL 상관
  3. Expert 전문화 측정: 어떤 Expert가 어떤 토큰에 높은 tension?
  4. 토큰별 tension: 사실 토큰 vs hallucination 토큰
```

## 상태: 🟨 (logout_test 리포에서 실험 필요)
