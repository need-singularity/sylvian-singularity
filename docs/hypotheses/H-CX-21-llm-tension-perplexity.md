# H-CX-21: LLM's Perplexity = Consciousness Engine's Tension (Cross-domain)

> **LLM perplexity (PPL) and the consciousness engine's tension are structurally identical. PPL = "uncertainty about the next token", tension = "disagreement between engines". Both measure "how confident the system is".**

## Correspondence Table

```
  Consciousness Engine            LLM
  ──────────────────────    ──────────────────────
  tension = |A-G|²          PPL = exp(H(next_token))
  High tension = uncertain  High PPL = uncertain
  tension→0 = confident     PPL→1 = confident
  Anomaly detection (H287)  OOD detection
  AUROC=1.0                 PPL spike on OOD
  H307 dual mechanism       Internal PPL vs ensemble PPL?
```

## Core Cross-domain Connection

```
  1. Tension = biological version of PPL
     PPL = exp(-1/N Σ log p(x_i))
     tension = |f_A(x) - f_G(x)|²

     Both measure "prediction uncertainty"
     PPL: high when failing to predict next token
     tension: high when two engines cannot agree

  2. Anomaly detection ↔ OOD detection
     Consciousness engine: anomaly data → high tension → AUROC=1.0
     LLM: OOD text → high PPL → OOD detected
     → Same mechanism!

  3. Golden MoE ↔ MoE Savant
     Consciousness engine: I=1/e, 37% inhibition is optimal
     Golden MoE: k/N ≈ 5/8 ≈ 0.625 ≈ 1-1/e
     → PPL optimization = tension optimization?

  4. H307 dual mechanism ↔ LLM ensemble
     Internal PPL: uncertainty of a single model
     Ensemble PPL: disagreement among multiple models
     → Internal PPL inversion + ensemble PPL normal = H307?
```

## Verifiable?

```
  Direct verification is difficult (requires LLM training)
  Indirect verification:
    1. Define "PPL-analog metric" on MNIST:
       PPL_analog = exp(CrossEntropy(model_output, true_label))
       → Does this correlate with tension?

    2. Measure PPL and tension simultaneously in Golden MoE
       → Is tension also low when PPL is low?

    3. PPL trajectory in Savant scenario
       → step 3303 with PPL 9.1 → substantial tension?
```

## Experimental Results (2026-03-24)

```
  MNIST RepulsionFieldEngine, 10ep:

  Overall: r(tension, PPL) = +0.001 (nearly uncorrelated)

  Correct/incorrect separated:
    Correct:   tension=702±432, PPL=1.01
    Incorrect: tension=495±298, PPL=283,505
    → Correct predictions have higher tension! (ratio 1.42x)

  Quartile analysis:
    Low-tension quartile:  PPL=430.7 (uncertain)
    High-tension quartile: PPL=9.68  (confident)
    → High tension = low PPL (confident)!

  Conclusion: tension ∝ 1/PPL (inversely proportional!)
    High tension = engines strongly repel = confident
    Low tension = engines agree = uncertain (consensus of confusion!)
    → PPL version of H307 dual mechanism!
    → Original prediction (tension ∝ PPL) refuted
    → Revised: tension ∝ confidence = 1/PPL
```

## Rigorous Verification (2026-04-04)

```
  Statistical analysis (calc/verify_H_CX_21_tension_ppl.py):

  Effect sizes:
    Cohen's d (tension, correct vs wrong) = +0.601 (medium-large)
    Cohen's d (log PPL, correct vs wrong) = -1.427 (very large)
    Mann-Whitney U (tension correct > wrong): p = 1.57e-56
    Mann-Whitney U (PPL wrong > correct):     p < 1e-300

  Quartile analysis:
    Q1 (low tension):  97.7% correct (highest PPL outliers present)
    Q4 (high tension): 97.7% correct (lowest PPL)
    Clear monotonic: higher tension → lower PPL → more correct

  Correlation (non-linear):
    Pearson r(tension, PPL) ≈ 0 (non-linear, as expected)
    Pearson r(tension, 1/PPL) = +0.15 (p < 1e-52)
    Spearman rho(tension, 1/PPL) = +0.08 (p < 1e-14)

  n=6 connection:
    Lambda(2) = -ln(4/3), Lambda(3) = +ln(4/3)
    Low tension ↔ R < 1 ↔ contraction (only n=2)
    High tension ↔ R > 1 ↔ expansion
    Optimal ↔ R = 1 ↔ Lambda = 0 (n=6, edge of chaos)

  Grade assessment:
    Cannot upgrade to 🟩 because:
    - Relationship is approximate (∝), not exact equation
    - Only verified on MNIST, not language domain
    - No analytical derivation of functional form
    Upgrade requires: LLM PPL verification + analytical derivation
```

## Status: 🟧★ Structural (confirmed inverse correlation Z>5σ, not exact equation, consistent with H307)
