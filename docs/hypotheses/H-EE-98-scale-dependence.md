# H-EE-98: Scale Dependence — Large-Scale Validation Unfinished

## Hypothesis

> The n=6 efficiency benefits demonstrated at ~100K parameter scale may
> diminish or disappear at 1B+ parameter scale. Large-scale validation
> (Phase 4) is critical and currently unfinished.

## Background

- All experiments in this repository are at 10K-500K parameter scale
- The largest validated model: ~480K parameters (experiment_h_ee_11)
- GPT-2 scale: ~117M parameters (2 orders of magnitude larger)
- GPT-3 scale: ~175B parameters (6 orders of magnitude larger)

## Known Scale Effects in Deep Learning

1. Grokking: Generalization emerges suddenly at large scale, not smoothly
2. Emergent abilities: Qualitatively new behaviors appear above thresholds
3. Chinchilla scaling: Optimal compute allocation shifts with model size
4. Neural collapse: Terminal-phase geometry changes with scale

Any of these could interact with R=1 balance in unexpected ways.

## Risk Assessment

| Scale       | Parameters | Validation Status      | Risk Level |
|-------------|------------|------------------------|------------|
| Toy         | <10K       | Verified               | Low        |
| Small       | 10K-1M     | Verified               | Low        |
| Medium      | 1M-100M    | Untested               | Medium     |
| Large       | 100M-10B   | Untested               | High       |
| Frontier    | >10B       | Untested               | Unknown    |

## Specific Concerns

1. At large scale, sigma/tau ratios become dominated by architectural choices
   (e.g., attention head count) rather than layer count — R-score meaning shifts

2. MoE architectures at scale (Switch Transformer, Mixtral) have effective
   parameter counts that may decouple from the R-score computation

3. Training instabilities at large scale (loss spikes, attention entropy collapse)
   may override any R=1 benefit

## What Would Falsify This

If a 1B+ parameter model trained with R=1 architecture shows NO improvement
over a matched non-R=1 baseline, H-EE-98 is confirmed as a real boundary.

## Conclusion

**Status: Open risk — Phase 4 validation required**
**Key concern:** All results are sub-1M parameters. Scale extrapolation is unverified.
**Bridge:** Phase 4 large-scale experiments needed before claiming universality.
