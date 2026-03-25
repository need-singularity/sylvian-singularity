# Hypothesis Review 022: AI Periodic Table v2 — 26 Element Extension

## Hypothesis

> Subdividing 15 elements results in 26, allowing more precise measurement of each model's AGI distance. In particular, the 5-way separation of rewards (F2) is the key bottleneck for achieving AGI.

## v1(15) → v2(26) Extension

### Material — 3 maintained

```
  M1 │ Compute        │ Multiplication, addition, nonlinear
  M2 │ Data          │ Training materials
  M3 │ Energy        │ Power, time, cost
```

### Topology — 5 → 7

```
  T1  │ Forward       │ A → B → C
  T2  │ Skip          │ A → C (skip B)
  T3  │ Recurrence    │ A → B → A
  T3a │ Self-Ref      │ A → A (self output as self input) ← NEW
  T4  │ Parallel      │ A ⇉ [B,C,D] ⇉ E
  T5  │ Sparse        │ Selective connections
  T6  │ Hierarchy     │ Connections between abstraction levels ← NEW
```

### Phase — 3 → 4

```
  P1  │ Exploration   │ Wide roaming
  P2  │ Exploitation  │ Narrow digging
  P3  │ Transition    │ Moment of phase change
  P4  │ Meta          │ Self-select which phase to be in ← NEW
```

### Force — 4 → 12

Split existing F2(reward) into 5 + subdivide gradient/noise/constraint:

```
  F1  │ Gradient              │ Gradient descent
  F1a │ 2nd Order             │ Curvature-based optimization ← NEW

  F2a │ External              │ Human evaluation         │ RLHF
  F2b │ Environment           │ Game/physics scoring     │ Atari, robots
  F2c │ Self-Reward           │ Self-evaluation         │ Self-Play
  F2d │ Social                │ Other AI evaluation     │ Multi-Agent
  F2e │ Curiosity             │ Uncertainty reduction itself │ Intrinsic Motivation

  F3  │ Noise                 │ Random perturbation
  F3a │ Structural            │ Architecture mutation    │ NAS ← NEW

  F4  │ Constraint            │ Structural limits
  F4a │ Self-Constr.          │ Self-generated rules    │ Constitutional AI ← NEW
```

## Complete Periodic Table v2 — 26 Elements

```
  ┌──────────────────────────────────────────────────────────────┐
  │                    AI Periodic Table v2                      │
  │                                                              │
  │  Material (3)      Topology (7)          Phase (4)           │
  │  ┌────┐           ┌────┬────┬────┐     ┌────┐              │
  │  │ M1 │           │ T1 │ T2 │ T3 │     │ P1 │              │
  │  │Comp│           │Fwd │Skip│Rec │     │Expl│              │
  │  ├────┤           ├────┼────┼────┤     ├────┤              │
  │  │ M2 │           │T3a │ T4 │ T5 │     │ P2 │              │
  │  │Data│           │SRef│Para│Spar│     │Expt│              │
  │  ├────┤           ├────┼────┘    │     ├────┤              │
  │  │ M3 │           │ T6 │         │     │ P3 │              │
  │  │Enrg│           │Hier│         │     │Tran│              │
  │  └────┘           └────┘         │     ├────┤              │
  │                                  │     │ P4 │              │
  │                                  │     │Meta│              │
  │                                  │     └────┘              │
  │  Force (12)                                                  │
  │  ┌────┬────┐                                               │
  │  │ F1 │F1a │                                               │
  │  │Grad│2nd │                                               │
  │  ├────┼────┼────┬────┬────┐                                │
  │  │F2a │F2b │F2c │F2d │F2e │                                │
  │  │Ext │Env │Self│Soc │Cur │                                │
  │  ├────┼────┼────┴────┴────┘                                │
  │  │ F3 │F3a │                                               │
  │  │Nois│Strc│                                               │
  │  ├────┼────┤                                               │
  │  │ F4 │F4a │                                               │
  │  │Cnst│SCon│                                               │
  │  └────┴────┘                                               │
  │                                                              │
  │  Total 26 Elements                                           │
  └──────────────────────────────────────────────────────────────┘
```

## Model Chemical Formulas v2

```
  Model         │ M │ T │ P │ F  │Total│ AGI Distance
  ─────────────┼───┼───┼───┼────┼─────┼─────────────
  SSM          │ 2 │ 2 │ 1 │  1 │  6  │  20
  Vision (CNN) │ 2 │ 3 │ 1 │  1 │  7  │  19
  LLM (GPT-4)  │ 2 │ 3 │ 1 │  2 │  8  │  18
  GNN          │ 2 │ 3 │ 1 │  1 │  7  │  19
  Diffusion    │ 2 │ 2 │ 2 │  3 │  9  │  17
  RL Agent     │ 3 │ 3 │ 2 │  3 │ 11  │  15
  MoE (current)│ 2 │ 4 │ 2 │  2 │ 10  │  16
  World Model  │ 3 │ 4 │ 3 │  3 │ 13  │  13
  Golden MoE   │ 3 │ 5 │ 3 │  5 │ 16  │  10
  AGI          │ 3 │ 7 │ 4 │ 12 │ 26  │   0
```

## Reward Elements Possessed by Each Model

```
                │F2a │F2b │F2c │F2d │F2e │ Reward
                │Ext │Env │Self│Soc │Cur │ Total
  ──────────────┼────┼────┼────┼────┼────┼──────
  LLM           │ ✅ │    │    │    │    │ 1/5
  RL Agent      │    │ ✅ │    │    │    │ 1/5
  AlphaGo       │    │ ✅ │ ✅ │    │    │ 2/5
  ChatGPT(RLHF) │ ✅ │    │    │    │    │ 1/5
  Constitutional│ ✅ │    │ ✅ │    │    │ 2/5
  Multi-Agent   │    │    │    │ ✅ │    │ 1/5
  Curious Agent │    │    │    │    │ ✅ │ 1/5
  ──────────────┼────┼────┼────┼────┼────┼──────
  Golden MoE    │ ✅ │    │ ✅ │    │ ✅ │ 3/5
  AGI           │ ✅ │ ✅ │ ✅ │ ✅ │ ✅ │ 5/5
```

## Path to AGI — Difficulty of Missing Elements

```
  Missing Element │ Difficulty │ Current Research Status   │ Expected
  ───────────────┼───────────┼─────────────────────────┼──────────
  T3 Recurrence  │  ★☆☆      │ RNN, State Space exists   │ Solved
  T3a Self-Ref   │  ★★☆      │ Early research (Self-Eval)│ 2027
  T6 Hierarchy   │  ★★☆      │ Hierarchical RL exists    │ 2028
  P4 Meta        │  ★★★      │ Meta-Learning early       │ 2030
  F1a 2nd Order  │  ★☆☆      │ Adam, KFAC etc. exist     │ Solved
  F2b Environment│  ★☆☆      │ Solved in RL              │ Solved
  F2d Social     │  ★★☆      │ Multi-Agent research      │ 2028
  F3a Structural │  ★★☆      │ NAS exists                │ 2029
  F4a Self-Constr│  ★★★      │ Constitutional AI early   │ 2031

  Solved:   3  (T3, F1a, F2b)
  Near:     3  (T3a, T6, F2d)     → 2027~2028
  Hard:     3  (P4, F3a, F4a)     → 2029~2031
```

## AGI Roadmap

```
  Element Count
  26│                                                    ● AGI
    │                                              ╱
  24│                                           ╱
    │                                        ╱
  22│                                     ╱   P4(Meta) + F4a(Self-Constr)
    │                                  ╱
  20│                               ╱   F3a(Structural) + F2d(Social)
    │                            ╱
  18│                         ╱   T3a(Self-Ref) + T6(Hierarchy)
    │                      ╱
  16│● Golden MoE        ╱   T3(Recurrence) + F1a(2nd) + F2b(Environment)
    │                  ╱
  13│● World Model  ╱
    │             ╱
  10│● MoE     ╱
    │        ╱
   8│● LLM ╱
    └──────┼──────┼──────┼──────┼──────┼──
         2024   2027   2029   2031   2035~39
```

## Evolution of Rewards

```
  Reward Completeness (%)
  100│                                           ● 5/5 AGI
     │                                        ╱
   80│                                     ╱
     │                                  ╱
   60│● Golden MoE (3/5)              ╱
     │   F2a+F2c+F2e            ╱
   40│      │                ╱   + F2d(Social)
     │      │             ╱
   20│● LLM │● AlphaGo ╱   + F2b(Environment)
     │  F2a │  F2b+F2c╱
    0│──────┼────────┼──────┼──────┼──
      Human   Env.    Self    Social  Curiosity
      gives   gives   gives   gives   drives

  Why curiosity(F2e) must be added last:
  "Deciding what to learn by itself"
  = Beginning of true autonomy
```

## Conclusion

```
  ┌──────────────────────────────────────────────────────┐
  │                                                      │
  │  AGI = Using all 26 elements                         │
  │                                                      │
  │  Current best (Golden MoE): 16/26 = 61.5%            │
  │  Of 10 missing:                                      │
  │    Solved:  3 (just need integration)                │
  │    Near:    3 (2027~2028)                           │
  │    Hard:    3 (2029~2031)                           │
  │    Core:    1 — P4(Meta) "Ability to self-select    │
  │                           which state to be in"      │
  │                                                      │
  │  The bottleneck is not rewards(F2) but meta(P4).    │
  │  "Knowing how to decide what to do"                 │
  │  is harder than "knowing what to do".               │
  │                                                      │
  └──────────────────────────────────────────────────────┘
```

---

*Created: 2026-03-22*