# Hypothesis Review 077: ε = (1-a)×(1/6) — Structural Determination ✅

## Hypothesis

> Is the curiosity parameter ε = 0.05 not an arbitrarily set value, but 
> a structural constant uniquely derived from the model's existing parameters (contraction rate a, blind spot 1/6)?

## Background

When adding curiosity to the model, how should we determine its strength ε?
If the model structure **requires a unique value** rather than an arbitrary choice of 0.05,
then this is not a free parameter but a **constraint condition**.

When adding curiosity to meta-iteration:
- Basic: f(I) = aI + b, fixed point I* = b/(1-a) = 1/3
- Curiosity: f_ε(I) = aI + (b - ε), fixed point I*_ε = (b-ε)/(1-a)

## Verification Result: ✅ Structurally Determined

```
  Derivation Process:
  ──────────────────────────────────────────────
  Goal: Curiosity moves the fixed point to the blind spot (1/6).

  I*_ε = (b - ε) / (1 - a) = 1/6

  Parameter substitution (a=0.7, b=0.1):
  (0.1 - ε) / 0.3 = 1/6
  0.1 - ε = 0.3 × (1/6)
  0.1 - ε = 0.05
  ε = 0.05

  Alternative expression:
  ε = b - (1-a) × (1/6)
    = b - (1-a)/6
    = (1-a) × [b/(1-a) - 1/6]
    = (1-a) × [I* - I*_ε]
    = (1-a) × [1/3 - 1/6]
    = (1-a) × (1/6)
    = 0.3 × (1/6)
    = 1/20
    = 0.05  ✅
  ──────────────────────────────────────────────
```

```
  Structural Decomposition:
  ──────────────────────────────────────────────

  ε = (1 - a)  ×  (1/6)
      ───────     ─────
         ↓           ↓
    Free space   Blind spot
    (Contraction  (Target to
     residual)     reach)

  Meaning of each element:
  ┌─────────────────────────────────────┐
  │  (1-a) = 0.3                        │
  │  = Amount that "decreases" each     │
  │    step in meta-iteration           │
  │  = System's free space              │
  │                                     │
  │  (1/6) = 0.167                      │
  │  = Blind spot of real number model  │
  │  = Target region to reach           │
  │                                     │
  │  ε = free × target = 0.3 × 0.167    │
  │    = 0.05 = 1/20                    │
  └─────────────────────────────────────┘
```

```
  Fixed Point Movement Diagram:
  ──────────────────────────────────────────────

  I-axis: 0    1/6    0.24  1/e   1/3    0.48  0.5
        │     │      │     │     │      │     │
        │     ●      ├─────────────────┤     │
        │  I*_ε     │   Golden Zone    │     │
        │ (curiosity)│  [0.24, 0.48]   │     │
        │     │      │     │     ★      │     │
        │     │      │     │   I*=1/3   │     │
        │     │      │     │  (basic)   │     │
        │     ←──────────────────┘      │     │
        │         Move by ε=0.05         │     │
        │                               │     │
  ──────────────────────────────────────────────

  ★ I*=1/3  : Basic fixed point (inside Golden Zone, safe)
  ● I*_ε=1/6: Curiosity fixed point (outside Golden Zone, blind spot)
```

```
  Meaning of ε = 1/20:
  ──────────────────────────────────────────────
  1/20 = 5%

  - Only 5% of the whole allocated to "curiosity"
  - 95% maintains existing structure
  - This 5% precisely moves the fixed point from 1/3 → 1/6
  - Larger would be excessive exploration (divergence risk)
  - Smaller would fail to reach the blind spot

  → 0.05 is both "minimum necessary curiosity" and "maximum safe curiosity"
  → Unique value
  ──────────────────────────────────────────────
```

## Interpretation

The curiosity strength ε = 0.05 = 1/20 is not a free parameter.
Once the contraction rate a and blind spot 1/6 are determined, ε is automatically determined.

This demonstrates the model's **self-consistency**:
"To see the blind spot, exactly this much curiosity is needed" 
is uniquely determined by the structure.

---

*Verification: verify_next_batch.py*
*Model: f_ε(I) = aI + (b-ε), ε = (1-a)×(1/6) = 1/20*