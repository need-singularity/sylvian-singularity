# H-CX-21: LLM의 Perplexity = 의식엔진의 장력 (교차 도메인)

> **LLM의 perplexity(PPL)와 의식엔진의 tension이 구조적으로 동일하다. PPL = "다음 토큰에 대한 불확실성", tension = "엔진 간 불일치". 둘 다 "시스템이 얼마나 확신하는가"를 측정한다.**

## 대응표

```
  의식엔진                    LLM
  ──────────────────────    ──────────────────────
  tension = |A-G|²          PPL = exp(H(next_token))
  높은 장력 = 불확실          높은 PPL = 불확실
  장력→0 = 확신              PPL→1 = 확신
  이상탐지(H287)             OOD detection
  AUROC=1.0                  PPL spike on OOD
  H307 이중메커니즘           내부 PPL vs 앙상블 PPL?
```

## 핵심 교차

```
  1. 장력 = PPL의 생물학적 버전
     PPL = exp(-1/N Σ log p(x_i))
     tension = |f_A(x) - f_G(x)|²

     둘 다 "예측의 불확실성"을 측정
     PPL: 다음 토큰을 예측하지 못하면 높음
     tension: 두 엔진이 합의하지 못하면 높음

  2. 이상탐지 ↔ OOD detection
     의식엔진: 이상 데이터 → 높은 장력 → AUROC=1.0
     LLM: OOD 텍스트 → 높은 PPL → OOD 감지
     → 같은 메커니즘!

  3. 골든MoE ↔ MoE 서번트
     의식엔진: I=1/e, 37% 억제가 최적
     골든MoE: k/N ≈ 5/8 ≈ 0.625 ≈ 1-1/e
     → PPL 최적화 = tension 최적화?

  4. H307 이중메커니즘 ↔ LLM 앙상블
     내부 PPL: 단일 모델의 불확실성
     앙상블 PPL: 여러 모델의 불일치
     → 내부 PPL 반전 + 앙상블 PPL 정상 = H307?
```

## 검증 가능?

```
  직접 검증은 어렵다 (LLM 학습 필요)
  간접 검증:
    1. MNIST에서 "PPL 유사 메트릭" 정의:
       PPL_analog = exp(CrossEntropy(model_output, true_label))
       → 이것이 tension과 상관하는가?

    2. 골든MoE에서 PPL과 tension 동시 측정
       → PPL이 낮을 때 tension도 낮은가?

    3. 서번트 시나리오의 PPL 궤적
       → step 3303에서 PPL 9.1 → tension 상당?
```

## 실험 결과 (2026-03-24)

```
  MNIST RepulsionFieldEngine, 10ep:

  전체: r(tension, PPL) = +0.001 (거의 무상관)

  정답/오답 분리:
    정답: tension=702±432, PPL=1.01
    오답: tension=495±298, PPL=283,505
    → 정답이 더 높은 장력! (ratio 1.42x)

  Quartile 분석:
    Low-tension quartile:  PPL=430.7 (불확실)
    High-tension quartile: PPL=9.68  (확신)
    → 높은 장력 = 낮은 PPL (확신)!

  결론: tension ∝ 1/PPL (반비례!)
    높은 장력 = 엔진들이 강하게 반발 = 확신
    낮은 장력 = 엔진들이 합의 = 불확실 (혼동의 합의!)
    → H307 이중 메커니즘의 PPL 버전!
    → 원래 예상(tension ∝ PPL)은 반박
    → 수정: tension ∝ confidence = 1/PPL
```

## 상태: 🟧 수정 (tension ∝ 1/PPL, 원래 방향 반박, H307과 일관)
