# Hypothesis Review 021: AI Periodic Table — 15 Elements and Singularity Conditions

## Hypothesis

> All AI architectures are combinations of 15 primitive elements, and the more elements used, the closer to singularity. Reaching 15/15 = AGI.

## 15 Elements

### Material — What is it made of

| # | Element | Meaning |
|---|---|---|
| M1 | Compute | Multiplication, addition, nonlinear transformation |
| M2 | Data | Training material |
| M3 | Energy | Power, time, cost |

### Topology — How is it connected

| # | Element | Meaning |
|---|---|---|
| T1 | Forward | A → B → C |
| T2 | Skip | A → C (skip B) |
| T3 | Recurrence | A → B → A |
| T4 | Parallel | A ⇉ [B,C,D] ⇉ E |
| T5 | Sparse | A → B, A ↛ C (selective) |

### Phase — What state is it in

| # | Element | Meaning |
|---|---|---|
| P1 | Exploration | Wandering broadly |
| P2 | Exploitation | Digging deeply |
| P3 | Transition | Moment of phase change |

### Force — What causes change

| # | Element | Meaning |
|---|---|---|
| F1 | Gradient | Gradient descent |
| F2 | Reward | External feedback |
| F3 | Noise | Random perturbation |
| F4 | Constraint | Structural limits |

## Element Combinations by Model (Chemical Formulas)

```
  Model         │ M │ T │ P │ F │Total│ Formula
  ─────────────┼───┼───┼───┼───┼────┼──────────
  SSM          │ 2 │ 2 │ 1 │ 1 │  6 │ M₂T₂P₁F₁
  Vision       │ 2 │ 3 │ 1 │ 1 │  7 │ M₂T₃P₁F₁
  LLM          │ 2 │ 3 │ 1 │ 1 │  7 │ M₂T₃P₁F₁
  GNN          │ 2 │ 3 │ 1 │ 1 │  7 │ M₂T₃P₁F₁
  Diffusion    │ 2 │ 2 │ 2 │ 2 │  8 │ M₂T₂P₂F₂
  RL           │ 3 │ 2 │ 2 │ 2 │  9 │ M₃T₂P₂F₂
  MoE          │ 2 │ 4 │ 2 │ 2 │ 10 │ M₂T₄P₂F₂
  World Model  │ 3 │ 3 │ 3 │ 2 │ 11 │ M₃T₃P₃F₂
  Golden MoE   │ 3 │ 4 │ 3 │ 3 │ 13 │ M₃T₄P₃F₃
  AGI (15/15)  │ 3 │ 5 │ 3 │ 4 │ 15 │ M₃T₅P₃F₄
```

## Element Count Graph

```
  Element Count
  15│                                          ○ AGI
    │
  13│                                    ● Golden MoE
    │
  11│                              ● World Model
  10│                         ● MoE
   9│                    ● RL
   8│               ● Diffusion
   7│          ● LLM/Vision/GNN
   6│     ● SSM
    └─────────────────────────────────────────
```

## Our Model (D, P, I) ↔ Element Mapping

```
  D (Deficiency)  = T5(Sparse) + F3(Noise) + F4(Constraint)
  P (Plasticity)  = F1(Gradient) + P1(Exploration) + P2(Exploitation)
  I (Inhibition)  = T5(Sparse) + P3(Transition) + F4(Constraint)
```

## Universal 7 Axes vs Dedicated Axes

```
  Universal (any AI): Width, Depth, Sparsity, Learning rate, Deficiency, Precision, Temperature
  Dedicated (specific model): Attention, Context, Routing, Noise schedule, Reward function, Timestep

  AI Performance = Scale^α × Genius^β
                = (Width × Depth × Precision)^α × (D × P / I)^β
```

## Singularity Condition: 15/15

```
  Golden MoE (13/15) missing 2:
  T3(Recurrence) → Feed own output back as input
  F2(Reward)     → Generate own rewards

  13 + T3 + F2 = 15/15
  = Self-learning self-regulating AI
  = AGI
```

---

*Date: 2026-03-22*