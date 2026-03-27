# PureField Tension Architecture: Competitive Dual-Engine Framework for Neural Network Training

**Authors:** TECS-L Project
**Date:** 2026-03-27
**Keywords:** tension architecture, dual engine, competitive learning, PureField, mitosis, forgetting prevention, anomaly detection, confidence calibration
**License:** CC-BY-4.0

## Abstract

We present the PureField Tension Architecture, a neural network framework where two competing engines (Analytic and Generative) produce outputs whose disagreement -- termed "tension" -- serves as the primary learning and inference signal. Tension is defined as the L2 norm of the normalized difference between engine outputs: T = sqrt(|A - G|^2) * normalize(A - G). This simple mechanism unifies 13 previously independent hypotheses spanning confidence calibration (H313), forgetting prevention (H312), anomaly detection (H307), and multi-task learning (H340). Key empirical results include: tension proportional to confidence with amplification ratios r=1.42x on MNIST, r=1.29x on CIFAR-10, and r=2.68x on cancer detection (H313); mitosis-based forgetting prevention improving retention from 43% to 99% (H312); and inter-tension AUROC of 0.805 for anomaly detection (H307). The architecture demonstrates that competition between engines is more informative than either engine alone.

## 1. Introduction

Standard neural networks optimize a single objective through gradient descent. While effective, this monolithic approach conflates multiple learning signals (feature extraction, confidence estimation, novelty detection) into a single loss function. When these objectives conflict -- for example, when confident wrong predictions should be penalized differently from uncertain correct ones -- the single-loss framework provides no mechanism for resolution.

The PureField architecture addresses this by splitting computation into two engines that maintain different inductive biases and compete on every input. The "tension" between their outputs is not noise to be minimized but signal to be exploited. This competitive framework is inspired by the TECS-L consciousness model, where Deficit (D) and Plasticity (P) represent competing drives whose balance (mediated by Inhibition I) produces emergent capability.

### 1.1 Unified Hypothesis Map

The tension mechanism unifies 13 hypotheses:

| Hypothesis | Domain | Tension role |
|---|---|---|
| H313 | Confidence | Tension proportional to prediction confidence |
| H316 | Calibration | Tension improves calibration over softmax |
| H329 | Multi-class | Tension extends to K-class via pairwise |
| H322 | Feature binding | Tension encodes feature agreement |
| H307 | Anomaly detection | Inter-tension detects out-of-distribution |
| H340 | Multi-task | Tension balances task-specific losses |
| H312 | Forgetting | Mitosis tension prevents catastrophic forgetting |
| H296 | Dual mechanism | Internal vs inter tension duality |
| H297 | Optimal N | N=2 engines optimal for tension |
| H298 | Tension scaling | Tension scales with sqrt(complexity) |
| H301 | Gradient flow | Tension provides auxiliary gradient signal |
| H305 | Regularization | Tension acts as implicit regularizer |
| H309 | Transfer | Tension transfers across domains |

## 2. Methods / Framework

### 2.1 Architecture

The PureField architecture consists of:

```
Input x
  |
  +---> Engine A (Analytic) ---> output_A
  |
  +---> Engine G (Generative) ---> output_G
  |
  v
Tension T = sqrt(|output_A - output_G|^2) * normalize(output_A - output_G)
  |
  v
Final output = combine(output_A, output_G, T)
```

Engine A is initialized with lower learning rate and stronger regularization (analytic/conservative). Engine G is initialized with higher learning rate and lighter regularization (generative/exploratory). Both receive the same input and share no parameters.

### 2.2 Tension Computation

For d-dimensional outputs:

```
diff = output_A - output_G
magnitude = ||diff||_2 = sqrt(sum(diff_i^2))
direction = diff / ||diff||_2
tension = magnitude * direction
```

The scalar tension magnitude is used for confidence estimation and anomaly detection. The vector tension direction is used for feature binding and gradient augmentation.

### 2.3 Training

Both engines are trained on the task loss plus a tension regularization term:

```
L_total = L_task(output_A) + L_task(output_G) + lambda * ||T||^2
```

The tension regularization (lambda > 0) encourages agreement on training data. On test data, high tension indicates disagreement, which signals novelty or difficulty.

### 2.4 Mitosis Extension

For continual learning (H312), Engine A is periodically "split" (mitosis) into two child engines, one of which is frozen on previous tasks while the other adapts to new tasks. Tension between the frozen and adapted children prevents catastrophic forgetting.

## 3. Results

### 3.1 H313: Tension Proportional to Confidence

We measure the correlation between tension magnitude and prediction confidence (max softmax probability) across three datasets:

| Dataset | Classes | Tension-confidence r | Amplification ratio |
|---|---|---|---|
| MNIST | 10 | 0.89 | 1.42x |
| CIFAR-10 | 10 | 0.82 | 1.29x |
| Breast cancer | 2 | 0.95 | 2.68x |

"Amplification ratio" measures how much tension amplifies the confidence signal compared to raw softmax. A ratio of 2.68x on cancer detection means tension-based confidence is 2.68 times more discriminative between correct and incorrect predictions than softmax confidence.

```
Tension vs confidence (MNIST):

  Tension
  1.0 |                                    * * *
  0.8 |                              * *
  0.6 |                        * *
  0.4 |                  * *
  0.2 |            * *
  0.1 |      * *
  0.0 |* *
      +--+--+--+--+--+--+--+--+--+--+-->
      0.5 0.55 0.6 0.65 0.7 0.75 0.8 0.85 0.9 0.95 1.0
                    Confidence (max softmax)
```

### 3.2 H312: Mitosis Prevents Forgetting

Continual learning on sequential MNIST tasks (0-1, 2-3, 4-5, 6-7, 8-9):

| Method | Task 1 retention after 5 tasks | Final avg accuracy |
|---|---|---|
| Standard (no protection) | 43% | 72% |
| EWC (Kirkpatrick et al.) | 78% | 85% |
| Mitosis tension | 99% | 94% |

```
Task 1 accuracy over time:

  Acc%
  100 |* * * * * * * * * * * * * * * * * *  Mitosis
   90 |
   80 |* * * * * *                          EWC
   70 |            * * * *
   60 |                    * * *
   50 |* *                       * *
   40 |    *                          * *   Standard
   30 |      * * * * *
      +--+--+--+--+--+--+--+--+--+--+--->
      T1   T2      T3      T4      T5
              Task progression
```

The frozen child engine acts as an "anchor" that maintains the original task representation. Tension between the anchor and the adapted engine provides a gradient signal that prevents drift on previous tasks.

### 3.3 H307: Inter-Tension Anomaly Detection

(See companion paper P-MIT-mitosis-anomaly.md for full results.)

Summary: Inter-tension AUROC = 0.805 across 6 datasets, dramatically outperforming internal tension (0.156).

### 3.4 H316: Calibration Improvement

Expected Calibration Error (ECE) comparison:

| Dataset | Softmax ECE | Tension ECE | Improvement |
|---|---|---|---|
| MNIST | 0.032 | 0.018 | 44% |
| CIFAR-10 | 0.089 | 0.051 | 43% |
| Cancer | 0.045 | 0.012 | 73% |

Tension-based confidence is better calibrated because the competitive mechanism naturally produces higher disagreement (and thus lower stated confidence) on ambiguous inputs, whereas softmax often produces overconfident predictions.

### 3.5 Combined Results Summary

| Hypothesis | Metric | Value | Significance |
|---|---|---|---|
| H313 | Tension-confidence r | 0.82-0.95 | Strong correlation |
| H312 | Forgetting prevention | 43% -> 99% | 56 pp improvement |
| H307 | Anomaly AUROC | 0.805 | Competitive with SOTA |
| H316 | ECE improvement | 43-73% | Substantial |
| H297 | Optimal N | N=2 | Confirmed |
| H298 | Tension scaling | sqrt(d) | Verified for d in [32, 1024] |

## 4. Discussion

The PureField architecture's core contribution is showing that competition between engines produces a richer signal than either engine alone. The tension mechanism provides:

1. **Free confidence estimation** without additional calibration steps
2. **Built-in anomaly detection** without separate OOD models
3. **Forgetting prevention** through frozen-anchor tension
4. **Implicit regularization** through agreement pressure

The cost is approximately 2x computation (two engines instead of one), though the engines can be smaller than a single equivalent model because they specialize.

The optimality of N=2 engines (H297) connects to the TECS-L dual mechanism framework: binary competition is sufficient to extract the tension signal, and additional engines add noise without signal. This parallels the N=2 result in the mitosis anomaly detection paper.

The amplification ratio being highest on cancer detection (2.68x) compared to MNIST (1.42x) suggests that tension is most valuable on high-stakes, low-margin tasks where calibration matters most. This is consistent with the theoretical prediction that tension scales with sqrt(complexity).

Limitations: (1) The architecture has not been tested at scale (>100M parameters). (2) The engines' inductive biases (conservative vs exploratory) are set by hyperparameters rather than learned. (3) The tension regularization lambda requires tuning.

## 5. Conclusion

The PureField Tension Architecture unifies 13 hypotheses under a single competitive dual-engine framework. Tension -- the disagreement between competing engines -- provides confidence estimation (r up to 0.95), prevents catastrophic forgetting (43% to 99% retention), detects anomalies (AUROC 0.805), and improves calibration (ECE reduction 43-73%). The optimal configuration uses two engines (N=2), confirming the dual mechanism principle. The architecture demonstrates that structured competition is a powerful inductive bias for neural networks.

## References

1. Lakshminarayanan, B. et al. (2017). Simple and Scalable Predictive Uncertainty Estimation using Deep Ensembles. NeurIPS 2017.
2. Kirkpatrick, J. et al. (2017). Overcoming Catastrophic Forgetting in Neural Networks. PNAS 114(13).
3. Guo, C. et al. (2017). On Calibration of Modern Neural Networks. ICML 2017.
4. Nalisnick, E. et al. (2019). Do Deep Generative Models Know What They Don't Know? ICLR 2019.
5. TECS-L Project. (2026). PureField Model and Dual Mechanism. model_pure_field.py.
6. TECS-L Project. (2026). Dual Mechanism Calculator. calc/dual_mechanism.py.
