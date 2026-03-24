# 가설 335: PureField LLM — 반발력장만으로 언어 모델 구축

> **H334(field만으로 충분)를 LLM에 적용. 기존 MoE의 Expert를 PureField 쌍으로 교체하면, eq(FFN residual) 없이도 동등 이상의 PPL을 달성할 수 있다.**

## 설계

```
  기존 Transformer MoE:
    x → Attention → FFN(eq) + MoE(field) → output

  PureField LLM:
    x → Attention → PureFieldMoE → output
    PureFieldMoE: N pairs of (Expert_A, Expert_G)
    각 pair의 output = scale × √|A-G|² × norm(A-G)
    Router가 pair 선택 (Top-K)

  핵심 차이:
    기존: output = FFN(x) + Σ w_i × Expert_i(x)
    제안: output = Σ w_i × scale_i × √|A_i-G_i|² × norm(A_i-G_i)
    → FFN(eq) 제거 → 파라미터 절약
    → 모든 Expert가 "반발 쌍"으로 구성
```

## 예상 이점

```
  1. 파라미터 효율: FFN 제거 (전체의 ~30%)
  2. Hallucination 감지 내장: 낮은 tension = "모르겠다"
  3. 과신 감지 내장: per-token tension 모니터링
  4. 학습 역학: tension∝ln(step) 로그성장 (H320)

  골든MoE 연결:
    현재: σ(6)=12 Expert, τ(6)=4 활성
    제안: 6쌍(12 Expert) 중 2쌍(4 Expert) 활성
    → 완전수 6의 구조가 자연스럽게 보존
```

## 실험 계획

```
  1단계: 골든-llama에 PureField layer 추가
  2단계: PPL 비교 (FFN+MoE vs PureFieldMoE)
  3단계: Hallucination benchmark에서 tension 활용
  4단계: Continual learning (H312) + PureField
```

## 상태: 🟨 (설계 완료, golden-llama에서 구현 필요)
