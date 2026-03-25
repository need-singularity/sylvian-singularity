# H-405: AnimaLM Expert Topological Specialization

> **Hypothesis**: In a trained AnimaLM (A-G repulsion field) model, Engine A experts
> and Engine G experts will develop distinct topological signatures measurable via
> Persistent Homology. Specifically: A-camp experts will have lower H0 persistence
> (more concentrated representations) while G-camp experts will have higher H1
> persistence (more loop structures = associative connections). The Wasserstein
> distance between A-camp and G-camp barcodes will correlate with model accuracy
> (r > 0.5), indicating that topological specialization drives performance.

**Golden Zone Dependency**: PH computation is GZ-independent. The A/G camp interpretation
inherits GZ dependency from the tension framework.

---

## Background

AnimaLM splits 8 experts into two camps:
- **Engine A (experts 0-3)**: logic/analytical processing
- **Engine G (experts 4-7)**: pattern/creative processing
- **Output**: `A - G` (pure repulsion)

H-404 showed that soft camp assignment preserves the hard A/G split on MNIST
(camp_a_prob = 0.86-0.90), suggesting the initial split is already reasonable.

But we have never measured the **topological structure** of what each camp learns.

### Key Questions

1. Do A-experts and G-experts develop different topological signatures?
2. Is topological divergence between camps correlated with accuracy?
3. Can we predict model quality from PH analysis of expert representations alone?

### Related Hypotheses

| Hypothesis | Connection |
|------------|-----------|
| H-CX-62 | PH topology predicts accuracy (r=-0.97 H0 vs acc) |
| H-CX-82 | Epoch 1 confusion map — does camp divergence appear at epoch 1? |
| H-CX-88 | Confusion topology consistency across architectures |
| H-CX-93 | Confusion PCA = semantic axes — do A/G camps align with semantic axes? |
| H-401 | PH correction uses barcode distance — specialization determines its magnitude |
| H-402 | PH routing depends on expert signatures — this tests if signatures are meaningful |
| H-404 | Soft camp preserved hard split — but topological divergence untested |

---

## Prediction: Topological Specialization Pattern

```
  Training progression (predicted):

  Epoch 1:  A-camp and G-camp nearly identical PH
            H0 persistence similar, H1 minimal
            Wasserstein distance ≈ 0 (no specialization yet)

  Epoch 3:  Divergence begins
            A-camp H0 decreases (tighter clusters)
            G-camp H1 increases (loop structures forming)
            Wasserstein distance grows

  Epoch 10: Stable specialization
            A: low H0, near-zero H1 (concentrated, simple topology)
            G: moderate H0, significant H1 (distributed, complex topology)
            Wasserstein distance plateaus

  Wasserstein(A,G) vs accuracy:

  Acc     │
  98% ──► │                           ●●●●●
  97% ──► │               ●●●●●●●●●●●
  96% ──► │         ●●●●●●
  95% ──► │    ●●●●
  94% ──► │●●●
          └──────────────────────────────────
          0.0   0.1   0.2   0.3   0.4   0.5
                  Wasserstein(PH_A, PH_G)

  Prediction: r > 0.5, monotonic increase
  Higher camp divergence → better repulsion → better accuracy
```

---

## Measurement Protocol

### Step 1: Train AnimaLM on MNIST + CIFAR-10

Use existing `experiment_anima_simplification.py` Raw Repulsion model.
At each epoch checkpoint, extract:

```python
# For each test batch:
out_a, out_g = get_ag_outputs(experts, gate, x, n_camp_a)

# Compute PH on A-camp output space
ph_a = ripser(out_a.detach().cpu().numpy(), maxdim=1)
barcode_a_h0 = ph_a['dgms'][0]  # connected components
barcode_a_h1 = ph_a['dgms'][1]  # loops

# Compute PH on G-camp output space
ph_g = ripser(out_g.detach().cpu().numpy(), maxdim=1)
barcode_g_h0 = ph_g['dgms'][0]
barcode_g_h1 = ph_g['dgms'][1]

# Metrics:
total_pers_a_h0 = sum(death - birth for birth, death in barcode_a_h0 if finite)
total_pers_g_h0 = ...
total_pers_a_h1 = ...
total_pers_g_h1 = ...
wasserstein_h0 = wasserstein_distance(barcode_a_h0, barcode_g_h0)
wasserstein_h1 = wasserstein_distance(barcode_a_h1, barcode_g_h1)
```

### Step 2: Track Divergence Over Training

| Epoch | A_H0_pers | G_H0_pers | A_H1_pers | G_H1_pers | W_H0 | W_H1 | Acc |
|-------|-----------|-----------|-----------|-----------|------|------|-----|
| 1     | ?         | ?         | ?         | ?         | ?    | ?    | ~95%|
| 3     | ?         | ?         | ?         | ?         | ?    | ?    | ~97%|
| 5     | ?         | ?         | ?         | ?         | ?    | ?    | ~97.5%|
| 10    | ?         | ?         | ?         | ?         | ?    | ?    | ~97.8%|

### Step 3: Statistical Tests

- Spearman correlation: Wasserstein vs accuracy across epochs
- Permutation test: randomize A/G assignment, measure if real split > random
- Cross-dataset: verify pattern holds for both MNIST and CIFAR-10

---

## ASCII Architecture: What We're Measuring

```
  Input tokens
      │
      ▼
  [BoltzmannRouter I≈1/e]
      │
  ┌───┴───────────────────────────┐
  │                               │
  E0  E1  E2  E3          E4  E5  E6  E7
  └──── A-camp ────┘      └──── G-camp ────┘
         │                       │
       out_A                   out_G
         │                       │
    ┌────┴────┐            ┌─────┴────┐
    │  PH(A)  │            │  PH(G)   │
    │ H0: ??? │            │ H0: ???  │
    │ H1: ??? │            │ H1: ???  │
    └────┬────┘            └────┬─────┘
         │                      │
         └──── Wasserstein ─────┘
               distance
                 │
         correlation with accuracy?
```

---

## Falsification Criteria

1. If Wasserstein(A,G) shows no correlation with accuracy (r < 0.3): REFUTED
2. If A-camp and G-camp develop identical PH profiles: REFUTED (no specialization)
3. If random A/G assignment achieves same Wasserstein: REFUTED (split doesn't matter)

---

## Limitations

1. **MNIST ceiling**: limited dynamic range for correlation measurement
2. **Batch size dependence**: PH on different batch sizes may give different barcodes
3. **Expert count**: only 4 experts per camp — small sample for PH computation
4. **Output space PH**: measuring PH on 10-dim output, not hidden representations.
   Hidden dim PH would be richer but more expensive
5. **Confound**: divergence and accuracy both increase with training.
   Must control for epoch (partial correlation or detrending)

---

## Next Steps

1. Implement measurement in `experiment_anima_simplification.py` (add PH tracking)
2. Run on MNIST + CIFAR-10 with per-epoch PH snapshots
3. If divergence correlates: this validates H-401 and H-402 foundations
4. If divergence doesn't correlate: reconsider A/G camp assignment strategy
5. Cross-reference with H-CX-93 (semantic axes) — do A/G camps align with PC1?

---

*H-405 | Status: Proposed | GZ-dependency: Partial (PH independent, A/G interpretation dependent)*
*Related: H-401, H-402, H-404, H-CX-62, H-CX-82, H-CX-88, H-CX-93*
