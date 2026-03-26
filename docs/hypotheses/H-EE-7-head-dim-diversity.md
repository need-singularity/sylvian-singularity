# H-EE-7: Head-Dim Diversity Improves Attention

**Status**: Testing
**Golden Zone Dependency**: None (pure number theory + empirical ML)
**Related**: H-EN-5, H-EE-5, H-EE-6

> **Hypothesis**: Non-power-of-2 head dimensions (like 10, 12, 15, 20) capture different attention scales than standard power-of-2 head dims (8, 16, 32, 64), improving loss. HCN dimensions enable this diversity because they have more divisors.

## Background

Standard transformers use d_model=128 with heads in {4, 8, 16, 32}, giving head_dims in {32, 16, 8, 4} -- all powers of 2. But d_model=120 allows head_dims in {5, 6, 8, 10, 12, 15, 20, 24, 30, 40, 60} -- a much richer set including non-power-of-2 values.

The hypothesis is that non-standard head dims create attention patterns at different scales, acting like a multi-scale feature extractor.

## Head-Dim Options Comparison

```
  d=120 head_dims: 4, 5, 6, 8, 10, 12, 15, 20, 24, 30, 40, 60
  d=128 head_dims: 4, 8, 16, 32, 64

  d=120 non-pow2 head_dims: 5, 6, 10, 12, 15, 20, 24, 30, 40, 60  (10 options)
  d=128 non-pow2 head_dims: (none)

  d=120 prime factor diversity in head_dims:
    h_dim=5  : {5}        (1 prime factor)
    h_dim=6  : {2,3}      (2 prime factors)
    h_dim=10 : {2,5}      (2 prime factors)
    h_dim=12 : {2,3}      (2 prime factors)
    h_dim=15 : {3,5}      (2 prime factors)
    h_dim=20 : {2,5}      (2 prime factors)

  d=128 all head_dims share 1 prime factor: {2}
```

## Experiment Design

- d=120: Train with heads in {4, 5, 6, 8, 10, 12, 15, 20, 24, 30}
- d=128: Train with heads in {4, 8, 16, 32}
- 2-layer GPT, character-level LM, 400 steps, 2 seeds each
- Compare: average loss for pow2 vs non-pow2 head_dims within d=120
- Compare: best d=120 config vs best d=128 config

## Results

*(To be filled after experiment completion)*

## ASCII Chart: Loss by head_dim (d=120)

*(To be filled after experiment completion)*

## Analysis

Expected outcomes:
1. If SUPPORTED: Non-pow2 head_dims in d=120 achieve lower average loss than pow2 head_dims
2. If PARTIALLY SUPPORTED: Non-pow2 head_dims are competitive, and the diversity provides more optimal configurations
3. If NOT SUPPORTED: Head_dim value matters less than model capacity

## Limitations

1. Small scale may not reveal multi-scale effects
2. Character-level LM may not benefit from scale diversity
3. Optimal head_dim may depend on task, not just arithmetic properties
4. Head_dim affects parameter count slightly (through projection matrices)

## Verification Direction

1. Test with NLP tasks (sentiment, NER) where multi-scale matters
2. Visualize attention patterns for different head_dims
3. Measure attention entropy as function of head_dim
4. Test "mixed head_dim" architectures (different head sizes per layer)
