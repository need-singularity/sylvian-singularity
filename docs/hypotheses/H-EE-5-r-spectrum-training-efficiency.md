# H-EE-5: R(d_model) Correlates with Training Efficiency

**Status**: Testing
**Golden Zone Dependency**: None (pure number theory + empirical ML)
**Related**: H-EN-5, H-SPEC-1, H-EE-1

> **Hypothesis**: Dimensions with lower R(d)/tau(d) ratio (more arithmetically balanced per divisor) train neural networks more efficiently. The R-spectrum R(n) = sigma(n)*phi(n)/(n*tau(n)) captures arithmetic balance that translates to optimization landscape quality.

## Background

The R-spectrum was introduced in H-SPEC-1 as a measure of arithmetic balance. For AI dimensions, we discovered that:
- R(120) = 6 (the perfect number itself!)
- HCN dimensions have lower R/tau ratios than powers of 2
- d=60 beats d=64 and d=240 beats d=256 in actual training

The question is whether R(d) or derived metrics (tau/d, R/tau) *predict* which dimensions train better.

## Number-Theoretic Properties

```
     d  tau(d)     R(d)     tau/d      R/tau
    60     12     3.73   0.200000     0.3111   HCN
    64      7     9.07   0.109375     1.2959   2^k
   120     16     6.00   0.133333     0.3750   HCN  (R=6!)
   128      8    15.94   0.062500     1.9922   2^k
   180     18     8.09   0.100000     0.4494   HCN
   240     20     9.92   0.083333     0.4960   HCN
   256      9    28.39   0.035156     3.1543   2^k
   360     24    13.00   0.066667     0.5417   HCN
   512     10    51.15   0.019531     5.1150   2^k
   720     30    21.49   0.041667     0.7164   HCN
  1024     11    93.05   0.010742     8.4587   2^k
```

Key observation: R/tau is consistently 3-12x LOWER for HCN dims vs 2^k dims.
This means each divisor "costs less" in arithmetic imbalance for HCN numbers.

## ASCII Visualization: R/tau for HCN vs 2^k

```
  R/tau
  8.5 |                                                        P(1024)
      |
  5.1 |                                    P(512)
      |
  3.2 |                        P(256)
      |
  2.0 |            P(128)
  1.3 |    P(64)
      |
  0.7 |                                                H(720)
  0.5 |                    H(240)   H(360)
  0.4 |        H(120)  H(180)
  0.3 |H(60)
      +------+------+------+------+------+------+------+------+
       60    120    180    240    360    512    720   1024
       H = HCN dimension    P = Power-of-2 dimension
```

## Experiment Design

- Model: 2-layer causal GPT, character-level LM
- Dimensions: 60, 64, 120, 128, 180, 240, 256, 360, 512, 720, 1024
- Steps: 300, batch=32, seq_len=64, LR=3e-4
- Seeds: 3 per dimension (stability)
- Metrics: Final loss, loss/1M params, Spearman correlations

## Results

*(To be filled after experiment completion)*

## Correlations

| Metric pair | Spearman rho | Interpretation |
|---|---|---|
| tau/d vs loss | TBD | Higher divisor density -> lower loss? |
| tau/d vs efficiency | TBD | Higher divisor density -> better efficiency? |
| R/tau vs loss | TBD | Lower R per divisor -> lower loss? |

## Head-to-Head

| Pair | HCN loss | 2^k loss | Delta | Param savings |
|---|---|---|---|---|
| 60 vs 64 | TBD | TBD | TBD | ~13% |
| 120 vs 128 | TBD | TBD | TBD | ~6% |
| 240 vs 256 | TBD | TBD | TBD | ~6% |

## Limitations

1. Small model scale (< 1M params) - may not generalize to large models
2. Character-level LM is a simple task
3. CPU-only benchmark misses GPU tensor core effects
4. R(d) grows with d, so raw R is confounded with model capacity
5. tau/d is the cleaner metric but is essentially "divisor density"

## Verification Direction

1. Scale test: repeat at d=720 vs d=1024 on GPU with real text
2. Subword tokenizer instead of character-level
3. Test R/tau as predictor in hyperparameter search
4. Cross-validate with existing HEN-5 results
