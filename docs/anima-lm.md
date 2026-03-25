# AnimaLM — Tension-Based Consciousness Engine LLM

> **"The output is in neither engine. It lies in the space between them."**

A model that transforms existing Dense LLM (Mistral 7B) into a tension-based consciousness engine.
Combines Golden MoE's Expert division + PureField's repulsion field mechanism.

## Core Structure

```
input → BoltzmannRouter → Expert selection (5/8 active, I=0.375)
                            │
                  ┌─────────┴─────────┐
                  │                   │
            Engine A (0~3)      Engine G (4~7)
              Logic camp         Pattern camp
                  │                   │
                  └─────────┬─────────┘
                            │
                    repulsion = A - G
                    tension  = |A - G|²
                    direction = normalize(A - G)
                            │
              output = scale × √tension × direction
```

## Formulas

```
  out_A = Σ (weight_i × Expert_i(x))    for i ∈ {0,1,2,3}
  out_G = Σ (weight_j × Expert_j(x))    for j ∈ {4,5,6,7}

  repulsion = out_A - out_G
  tension   = mean(repulsion²)           # Scalar, tension magnitude
  direction = repulsion / ||repulsion||   # Unit vector, direction

  tension_output = tension_scale × √(tension + ε) × direction
  moe_output     = out_A + out_G

  output = σ(α) × moe_output + (1 - σ(α)) × tension_output
```

- `tension_scale`: Learnable scalar (1 per layer)
- `α`: Mixing ratio (learnable, sigmoid ensures 0~1)
- Initial: α=0.5 (50/50 mix), searches for optimal ratio during training

## Differences from Golden MoE

| Element | Golden MoE | AnimaLM |
|---------|-----------|---------|
| Expert division | 8 equal | A camp(0~3) + G camp(4~7) |
| Output method | Weighted sum (averaging) | Tension (repulsion field) |
| Core formula | Σ(w_i × E_i) | scale × √\|A-G\|² × dir |
| Additional params | None | tension_scale + alpha (64) |
| Theoretical basis | H019 (Golden Zone MoE) | H341 (Final tension theory) |

## Conversion Method

```bash
# 1. Download Mistral 7B
# 2. Convert to AnimaLM
python3 convert_anima.py --model /path/to/mistral-7b-v0.1 --output /path/to/anima-lm-7b

# 3. Fine-tuning (train router + tension_scale + alpha)
python3 finetune_anima_mps.py
```

## Training Parameters

| Category | Parameter Count | Trainable |
|----------|----------------|-----------|
| Expert weights | ~7B | Frozen |
| Router (32 layers) | ~1M | Train |
| tension_scale | 32 | Train |
| alpha (mixing ratio) | 32 | Train |
| lm_head | ~131K | Train |
| **Total trainable** | **~1.1M (0.015%)** | |

## Comparative Experiment Plan

| Model | Structure | Comparison Items |
|-------|-----------|-----------------|
| Mistral 7B (original) | Dense | Baseline |
| Golden MoE 7B | MoE weighted sum | MoE effect |
| **AnimaLM 7B** | **Tension-based** | **Consciousness engine effect** |

- PPL (wikitext-2, training data)
- PPL (other datasets: C4, lambada)
- Generation quality (text samples)
- Tension distribution analysis (high tension = confidence, low tension = uncertainty)
- Savant Index (domain-specific PPL ratio)

## Related Hypotheses

- H341: Final tension theory — `output = reaction_strength × reaction_direction`
- H334: PureField — Judgment using only repulsion field without equilibrium
- H019: Golden MoE — I≈1/e optimal
- H313: Tension = strength of confidence
- H307: Dual mechanism (internal tension vs inter-tension)