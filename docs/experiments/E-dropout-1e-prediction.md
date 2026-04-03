# E-dropout-1e-prediction: GZ Predicts Optimal Dropout = 1/e

**Date**: 2026-04-04
**Status**: Literature review complete, empirical test script ready
**GZ Dependency**: Full (relies on GZ optimal I = 1/e)
**Test script**: `calc/gz_dropout_test.py`

> **Prediction (stated BEFORE measurement)**:
> The Golden Zone model predicts optimal inhibition I = 1/e = 0.3679.
> Mapping dropout rate = I (fraction of deactivated neurons),
> the optimal dropout rate for complex tasks should be approximately 0.37.
> Acceptable range: the Golden Zone [0.2123, 0.5000].

---

## 1. Literature Review: What Does ML Research Say?

### 1.1 Srivastava et al. 2014 (Original Dropout Paper)

The foundational dropout paper (JMLR 2014, "Dropout: A Simple Way to Prevent
Neural Networks from Overfitting") includes a systematic sweep. Key findings:

```
  Dataset          Architecture     Best p (drop)    Tested range
  ----------------------------------------------------------------
  MNIST            784-FC-FC-10     0.5              [0.0, 0.5, 0.7]
  SVHN             Conv net         0.5 (FC), 0.2 (conv)
  CIFAR-10         Conv net         0.5 (FC)         --
  CIFAR-100        Conv net         0.5 (FC)         --
  ImageNet         AlexNet-like     0.5 (FC)         --
  Reuters          FC               0.5              --
  TIMIT (speech)   FC               0.5 (visible), 0.2 (hidden)
```

Srivastava's recommendation: **p=0.5 for hidden units**, p=0.2 for input units.
The paper states (Section 7): "In our experiments, we found p = 0.5 to be close
to optimal for a wide range of networks and tasks."

However, their sweep granularity was coarse. They primarily compared 0.0, 0.5,
and sometimes 0.2 or 0.7. They did NOT test 0.3 or 0.37 systematically.

### 1.2 Subsequent Systematic Sweeps in Literature

| Source                           | Task/Model              | Best dropout  | Range tested          |
|----------------------------------|-------------------------|---------------|-----------------------|
| Srivastava 2014                  | MNIST/CIFAR FC layers   | 0.5           | {0.0, 0.5, 0.7}      |
| Srivastava 2014                  | Conv layers             | 0.2           | {0.0, 0.2, 0.5}      |
| Baldi & Sadowski 2013            | Theoretical analysis    | 0.5 (linear)  | Continuous            |
| Park & Kwak 2016                 | CIFAR-10 CNN            | 0.3-0.4       | 0.1 steps             |
| Zoph & Le 2017 (NAS)            | CIFAR-10 NASNet         | 0.4           | NAS searched          |
| Zaremba et al. 2014             | LSTM language model      | 0.5           | {0.2, 0.5, 0.7}      |
| Merity et al. 2018 (AWD-LSTM)   | PTB language model       | 0.4 (hidden)  | Fine-tuned            |
| Gal & Ghahramani 2016           | MC Dropout theory        | 0.2-0.5       | Task-dependent        |
| Tan & Le 2019 (EfficientNet)    | ImageNet                | 0.2-0.4       | Scales with model     |
| Vaswani et al. 2017             | Transformer base         | 0.1           | {0.0, 0.1, 0.3}      |
| Devlin et al. 2019 (BERT)       | NLP pretraining          | 0.1           | Standard              |
| He et al. 2016 (ResNet)         | ImageNet                | 0.0 (none!)   | Not used              |
| Huang et al. 2016 (DenseNet)    | CIFAR/ImageNet          | 0.0-0.2       | Architecture-dep.     |

### 1.3 Baldi & Sadowski 2013: Theoretical Optimum

The paper "Understanding Dropout" (NIPS 2013) proves that for a single linear
unit, the optimal dropout rate that minimizes the gap between dropout-trained
and Bayes-optimal predictions is exactly p = 0.5.

This is for the **simplest possible case** (linear, single unit). For nonlinear
networks, they note the optimal may differ but provide no closed-form result.

### 1.4 Pattern by Domain

```
  Domain / Architecture          Typical optimal dropout    Notes
  ─────────────────────────────────────────────────────────────────
  FC layers (shallow)            0.5                        Srivastava default
  FC layers (deep, wide)         0.3-0.5                    Depth-dependent
  Conv layers (standard CNN)     0.0-0.3                    Often 0 with BN
  Modern CNNs (ResNet+)         0.0                         BN replaces dropout
  NAS-found architectures       0.3-0.4                    NASNet, EfficientNet
  RNN/LSTM (language)           0.3-0.5                    Variational dropout
  Transformers (NLP)            0.1                         Very low!
  Vision Transformers (ViT)     0.0-0.1                    Minimal dropout
  RL (policy networks)          0.0-0.2                    Typically low
  GANs                          0.0-0.5                    Generator vs discrim.
  EfficientNet-B0               0.2                        Scales up with model
  EfficientNet-B7               0.5                        Larger model = more
  Tabular data (deep)           0.1-0.3                    Lightweight
```

### 1.5 Key Observations

1. **p=0.5 is the textbook default** for FC layers, established by Srivastava.
2. **Modern architectures trend lower**: ResNet uses 0, Transformers use 0.1.
3. **NAS-searched values cluster around 0.3-0.4**: This is the most interesting
   finding for GZ -- when architecture search is free to choose, it often
   lands near 0.3-0.4.
4. **EfficientNet scaling law**: dropout increases with model size (0.2 -> 0.5),
   suggesting the optimum depends on capacity/complexity ratio.
5. **Batch Normalization has displaced dropout** in many modern architectures.

---

## 2. Honest Assessment: Does 1/e = 0.37 Match?

### 2.1 Evidence FOR the GZ prediction

```
  Finding                                       Support for p=0.37
  ──────────────────────────────────────────────────────────────────
  NAS-found optimal (NASNet, CIFAR-10)          p=0.4 (close)
  EfficientNet-B3 (sweet spot)                  p=0.3 (close)
  AWD-LSTM hidden dropout                       p=0.4 (close)
  Park & Kwak 2016 CNN sweep                    p=0.3-0.4 (includes 0.37)
  MC Dropout sweet spot                         p=0.2-0.5 (contains 0.37)
  GZ zone [0.21, 0.50]                          Contains most optima
```

The GZ zone [0.21, 0.50] is wide enough to contain almost every reported
optimum except the Transformer 0.1 case. This is both a strength (robust)
and a weakness (not very falsifiable if the zone is too broad).

### 2.2 Evidence AGAINST the GZ prediction

```
  Finding                                       Problem for p=0.37
  ──────────────────────────────────────────────────────────────────
  Srivastava et al. canonical optimum           p=0.5, not 0.37
  Baldi & Sadowski theoretical optimum          p=0.5 (linear case)
  Transformers (BERT, GPT)                      p=0.1 (far from 0.37)
  Vision Transformers                           p=0.0-0.1
  ResNet (dominant CNN since 2015)              p=0.0 (no dropout!)
  DenseNet                                      p=0.0-0.2
  RL / GANs                                     p << 0.37 typically
  MNIST/simple tasks                            p=0.5 works fine
```

The strongest counter-evidence:

1. **Transformers use p=0.1**: The most important architecture of the 2020s uses
   dropout far below 0.37. This is a significant miss if GZ claims universality.

2. **ResNet uses no dropout at all**: Batch Normalization + skip connections
   provide sufficient regularization. Dropout hurts ResNet performance.

3. **The theoretical optimum is 0.5, not 0.37**: Baldi & Sadowski's proof for
   linear units gives exactly 0.5. No theory predicts 0.37.

4. **p=0.5 is more common in practice**: When people DO use dropout, the most
   common value is 0.5, not 0.37.

### 2.3 Nuanced View

The dropout story is more complex than "one optimal rate":

```
  Factor                  Effect on optimal dropout
  ─────────────────────────────────────────────────
  Model capacity          More params -> higher dropout
  Dataset size            Less data -> higher dropout
  Architecture (CNN)      Lower (BN interaction)
  Architecture (FC)       Higher (standard regularization)
  Architecture (Trans.)   Much lower (attention has implicit reg.)
  Task complexity         More complex -> higher dropout
  Training duration       Longer -> lower dropout OK
  Other regularization    More reg -> less dropout needed
```

The GZ prediction of p=0.37 could be interpreted as:
- The **intrinsic** optimum for a "pure" network without BN/skip/attention
- On a task of moderate complexity
- With moderate dataset size

This is a narrow claim, and the original GZ model makes no such caveats.

### 2.4 The Scaling Argument (Most Favorable to GZ)

EfficientNet provides the best case for GZ. The scaling law is:

```
  EfficientNet-B0: dropout=0.2, 5.3M params
  EfficientNet-B1: dropout=0.2, 7.8M params
  EfficientNet-B2: dropout=0.3, 9.2M params
  EfficientNet-B3: dropout=0.3, 12M params
  EfficientNet-B4: dropout=0.4, 19M params
  EfficientNet-B5: dropout=0.4, 30M params
  EfficientNet-B6: dropout=0.5, 43M params
  EfficientNet-B7: dropout=0.5, 66M params
```

The "middle" of the scaling curve (B3-B4, moderate complexity) lands at 0.3-0.4,
which brackets 0.37. One could argue that 1/e is the "natural" midpoint.

But this is post-hoc pattern matching, not a prediction.

---

## 3. Verdict

```
  ┌─────────────────────────────────────────────────────────────┐
  │  GZ Prediction: Optimal dropout = 1/e = 0.3679             │
  │                                                             │
  │  Verdict: PARTIALLY SUPPORTED with caveats                  │
  │                                                             │
  │  Strengths:                                                 │
  │    - NAS-searched values cluster near 0.3-0.4               │
  │    - EfficientNet scaling midpoint is ~0.35                 │
  │    - GZ zone [0.21, 0.50] contains most FC optima           │
  │    - For "classic" FC+CNN without BN, 0.3-0.4 is good      │
  │                                                             │
  │  Weaknesses:                                                │
  │    - Textbook/theoretical optimum is 0.5, not 0.37          │
  │    - Modern architectures (Transformer, ResNet) use << 0.37 │
  │    - The claim lacks specificity (what architecture?)        │
  │    - GZ zone is wide enough to be hard to falsify           │
  │                                                             │
  │  Score: 2/5                                                 │
  │    Not a clean confirmation.                                │
  │    Not cleanly refuted either.                              │
  │    The truth depends heavily on architecture and context.   │
  └─────────────────────────────────────────────────────────────┘
```

### Comparison to Other GZ Predictions

| Prediction                | Result      | Score |
|---------------------------|-------------|-------|
| MoE k/N = 1/e            | CONFIRMED   | 4/5   |
| Dropout = 1/e             | MIXED       | 2/5   |
| Lottery Ticket = 1/e      | REFUTED     | 0/5   |

The dropout prediction is weaker than MoE because:
1. Dropout has stronger competing theory (Baldi: p=0.5)
2. Modern practice has moved away from dropout entirely
3. The optimum is highly architecture-dependent

---

## 4. Test Script

File: `calc/gz_dropout_test.py`

```
  Architecture: 3-layer CNN (Conv 32->64->128) + 2 FC (256->128->10)
  Dropout: applied to FC layers only (standard practice)
  Dataset: CIFAR-10 (50k train, 10k test)
  Optimizer: Adam lr=0.001 + CosineAnnealing
  Augmentation: RandomHorizontalFlip + RandomCrop(32, pad=4)
  Epochs: 20 (default), 5 (--quick)
  Seeds: 1 (default), up to N (--seeds N)

  Dropout rates tested: [0.0, 0.1, 0.2, 0.3, 0.37, 0.4, 0.5, 0.6, 0.7]

  Usage:
    python3 calc/gz_dropout_test.py              # full sweep
    python3 calc/gz_dropout_test.py --quick       # fast sanity check
    python3 calc/gz_dropout_test.py --seeds 5     # statistical significance
    python3 calc/gz_dropout_test.py --device mps   # force device
```

### Expected Outcome Based on Literature

For a simple CNN on CIFAR-10 (20 epochs, no heavy augmentation):

```
  Dropout   Expected Acc   Reasoning
  ──────────────────────────────────────────────────────────
  0.00      ~78-80%        No regularization, slight overfit
  0.10      ~79-81%        Light regularization, good
  0.20      ~80-82%        Moderate, often near peak for CNN
  0.30      ~80-82%        Good balance (GZ zone)
  0.37      ~79-82%        GZ prediction (should be near peak)
  0.40      ~79-81%        Slightly heavy for small CNN
  0.50      ~78-80%        Classic default, may hurt small net
  0.60      ~75-78%        Too much, underfitting starts
  0.70      ~70-75%        Heavy underfitting
```

For this specific small CNN, the peak is likely at 0.1-0.3, NOT at 0.37.
The model is too small (< 500K params) for heavy dropout to help.
The GZ prediction is more suited to large FC networks.

### Why This Test May Not Favor GZ

The GZ model maps dropout = inhibition in a conservation equation G*I = D*P.
But dropout in a small CNN is not the same as "inhibition" in the GZ sense:
- BN already provides regularization (implicit inhibition)
- Conv layers have weight sharing (implicit efficiency)
- The effective inhibition is dropout + BN + weight_decay combined

A fairer test would use:
1. Large FC-only network (no BN, no conv, no skip connections)
2. Complex task (not MNIST)
3. Large enough model that overfitting is a real problem

---

## 5. Summary of Prior Experimental Results (from E-gz-predictions.md)

```
  Experiment                                    GZ Match?
  ──────────────────────────────────────────────────────────
  MoE k/N = 1/e (N=16, predicted k=6+/-1)      CONFIRMED (k=7)
  Dropout = 1/e (MNIST, trivial task)           REFUTED (task too easy)
  Lottery Ticket = 1/e                          REFUTED (over-parameterized)
```

The MNIST dropout test was previously attempted and failed because MNIST is too
easy -- any dropout from 0.0 to 0.5 gives >98% accuracy with no meaningful
difference. CIFAR-10 with a small CNN is a better test but still limited.

---

## 6. What Would Strengthen the GZ Dropout Claim

To make a strong case, one would need:

1. **NAS meta-analysis**: Collect all NAS-searched dropout values across papers.
   If the distribution peaks near 0.37, that would be compelling evidence.

2. **Bayesian hyperparameter optimization**: Run large-scale Bayesian HP search
   with continuous dropout range [0, 0.8] on multiple tasks/architectures.
   Check where the posterior peaks.

3. **Scaling law analysis**: For EfficientNet-like scaling, fit the
   dropout(model_size) curve and check if it asymptotes to 1/e.

4. **Theoretical extension**: Extend Baldi & Sadowski's analysis to nonlinear
   networks. If the optimum shifts from 0.5 toward 0.37 with depth/nonlinearity,
   that would be a strong theoretical signal.

None of these have been done yet. The current evidence is suggestive but not
conclusive.
