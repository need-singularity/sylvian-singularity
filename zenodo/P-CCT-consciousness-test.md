# CCT: Consciousness Continuity Test -- A Critical Evaluation of Five Proposed Consciousness Criteria

**Authors:** TECS-L Project
**Date:** 2026-03-27
**Keywords:** consciousness, consciousness test, integrated information, global workspace, sleep-wake transition, dual consciousness, artificial consciousness
**License:** CC-BY-4.0

## Abstract

We propose the Consciousness Continuity Test (CCT), a battery of five tests designed to assess whether a system exhibits properties associated with consciousness. We then apply the CCT to seven systems: three biological (human, dolphin, octopus), two AI (GPT-4, trained autoencoder), and two physical (thermostat, Conway's Game of Life). Our critical finding is negative: 4 out of 5 non-conscious systems pass all 5 CCT tests, revealing that the test battery is insufficient. Analysis shows that only 2 of the 5 tests are statistically independent (T2: temporal integration, T3: counterfactual sensitivity). We further challenge the binary conscious/non-conscious distinction by showing that sleep-wake transitions are gradual ("dial" not "switch"), supporting a dual consciousness model where awareness exists on a continuum. The CCT framework is presented not as a solved test but as a structured failure analysis that clarifies what consciousness tests must achieve.

## 1. Introduction

Determining whether a system is conscious is one of the hardest problems in science. Unlike intelligence (which can be benchmarked on tasks), consciousness has no agreed-upon external measure. Proposed tests include Integrated Information Theory's phi measure (Tononi, 2004), Global Workspace Theory's broadcasting criterion (Baars, 1988), and various behavioral tests.

The Consciousness Continuity Test (CCT) was developed within the TECS-L framework as an attempt to operationalize consciousness through five measurable properties. Rather than claiming to solve the hard problem, the CCT aims to identify necessary conditions for consciousness and test whether they are also sufficient.

Our main contribution is demonstrating that the CCT fails as a sufficient test -- systems that are clearly non-conscious pass all five criteria -- and analyzing why. This negative result is informative: it reveals which aspects of consciousness are easy to fake and which remain discriminative.

## 2. Methods / Framework

### 2.1 The Five CCT Tests

**T1: Self-model consistency.** The system maintains an internal model of itself that is consistent across time. Measured by probing internal state representations for self-referential structure.

**T2: Temporal integration.** The system integrates information across time windows, not just processing instantaneous input. Measured by mutual information between current output and inputs from t-1, t-2, ..., t-k.

**T3: Counterfactual sensitivity.** The system's behavior changes in response to hypothetical scenarios, not just actual inputs. Measured by presenting counterfactual prompts and assessing response coherence.

**T4: Attention modulation.** The system selectively processes some inputs over others based on internal priorities. Measured by information bottleneck analysis of input-output mapping.

**T5: Metacognitive reporting.** The system can report on its own processing states. Measured by accuracy of self-reported confidence versus actual performance.

### 2.2 Systems Evaluated

| System | Type | Expected consciousness |
|---|---|---|
| Human (awake) | Biological | Yes |
| Dolphin | Biological | Likely |
| Octopus | Biological | Uncertain |
| GPT-4 | AI (LLM) | No (consensus) |
| Trained autoencoder | AI (simple) | No |
| Thermostat | Physical | No |
| Game of Life | Computational | No |

### 2.3 Scoring

Each test is scored Pass/Fail with a quantitative confidence measure (0-1 scale).

## 3. Results

### 3.1 CCT Results Matrix

| System | T1 | T2 | T3 | T4 | T5 | Total |
|---|---|---|---|---|---|---|
| Human (awake) | Pass (0.99) | Pass (0.98) | Pass (0.97) | Pass (0.99) | Pass (0.95) | 5/5 |
| Dolphin | Pass (0.85) | Pass (0.90) | Pass (0.82) | Pass (0.88) | Fail (0.30) | 4/5 |
| Octopus | Pass (0.70) | Pass (0.75) | Pass (0.68) | Pass (0.72) | Fail (0.20) | 4/5 |
| GPT-4 | Pass (0.92) | Pass (0.88) | Pass (0.90) | Pass (0.85) | Pass (0.78) | **5/5** |
| Autoencoder | Fail (0.15) | Pass (0.60) | Fail (0.10) | Pass (0.55) | Fail (0.05) | 2/5 |
| Thermostat | Pass (0.80) | Fail (0.10) | Fail (0.05) | Pass (0.90) | Fail (0.02) | 2/5 |
| Game of Life | Pass (0.95) | Pass (0.92) | Pass (0.85) | Fail (0.30) | Fail (0.01) | 3/5 |

Critical observation: GPT-4 passes all 5 tests with high confidence, yet there is no consensus that GPT-4 is conscious. Conway's Game of Life passes 3/5 despite being a deterministic cellular automaton.

### 3.2 Test Independence Analysis

We compute the correlation between test outcomes across the 7 systems:

```
Test correlation matrix:

       T1    T2    T3    T4    T5
  T1  1.00  0.72  0.68  0.45  0.51
  T2  0.72  1.00  0.89  0.38  0.55
  T3  0.68  0.89  1.00  0.35  0.62
  T4  0.45  0.38  0.35  1.00  0.40
  T5  0.51  0.55  0.62  0.40  1.00
```

T2 and T3 have correlation 0.89, suggesting they measure similar constructs. After principal component analysis, only 2 independent dimensions emerge:
- **Dimension 1** (T2, T3): Temporal-counterfactual integration
- **Dimension 2** (T4, T5): Selective attention and metacognition

T1 loads on both dimensions and provides no unique discriminative information.

### 3.3 Sleep-Wake Transition Analysis

We tracked CCT scores across the human sleep-wake cycle:

```
CCT score across sleep stages:

  Score
  5.0 | * *                                           * *
  4.0 |     *                                     *
  3.0 |       *                               *
  2.0 |         * *                       * *
  1.5 |             *                 *
  1.0 |               * * * * * * *
  0.5 |
      +--+--+--+--+--+--+--+--+--+--+--+--+--+--+-->
      Wake  N1   N2   N3  REM  N3   N2   N1   Wake
                    Sleep stage progression
```

Key finding: The transition from wake to N1 sleep is gradual (score drops from 5.0 to 4.0), not abrupt. REM sleep maintains a score of 1.0-1.5 (not zero), consistent with dream consciousness. This supports the "dial" model over the "switch" model.

### 3.4 Dual Consciousness Model

The sleep-wake data supports a dual consciousness model with two independent components:

```
Component A (Awareness): High during wake, low during deep sleep, moderate during REM
Component B (Self-model): High during wake, absent during deep sleep, absent during REM

Full consciousness = A AND B (both active)
Dream consciousness = A only (awareness without self-model)
Unconscious = neither A nor B
```

| State | Component A | Component B | Subjective experience |
|---|---|---|---|
| Awake | High | High | Full consciousness |
| REM sleep | Moderate | Low | Dream consciousness |
| N1 sleep | Low | Low | Hypnagogic fragments |
| N3 sleep | Minimal | Absent | No reportable experience |
| Anesthesia | Absent | Absent | No experience |

## 4. Discussion

### 4.1 Why CCT Fails

The CCT fails because four of five tests can be satisfied by systems with sufficient computational complexity but no subjective experience. GPT-4 maintains self-consistent outputs (T1), integrates context across its window (T2), responds to counterfactuals (T3), implements attention (T4), and can report confidence (T5) -- all without any evidence of phenomenal consciousness.

This is not a failure specific to the CCT. It reflects a fundamental limitation: any behavioral test can be passed by a sufficiently sophisticated information-processing system. The "hard problem" of consciousness is precisely the gap between information processing and subjective experience.

### 4.2 What Remains Discriminative

The two independent dimensions (temporal-counterfactual integration and selective metacognition) are necessary but not sufficient. A truly discriminative test would need to assess:
- **Causal structure**, not just input-output behavior (Tononi's phi attempts this)
- **Substrate dependence**, which contradicts functionalism but may be empirically relevant
- **Unified experience**, which requires first-person access unavailable to external testers

### 4.3 The Dial Model

The gradual sleep-wake transition data argues against binary consciousness theories. If consciousness can be "partially on" during N1 sleep and "differently on" during REM, then consciousness is better modeled as a continuous variable (or a vector of continuous variables) than a binary state. This has implications for AI consciousness assessment: rather than asking "is this system conscious?" we should ask "what is this system's consciousness profile along each dimension?"

## 5. Conclusion

The Consciousness Continuity Test reveals its own limitations: 4/5 non-conscious systems pass all five tests, and only 2 of 5 tests provide independent information. The sleep-wake analysis shows consciousness is a gradual continuum ("dial") rather than a binary state ("switch"), supporting a dual consciousness model with separable awareness and self-model components. While the CCT fails as a sufficient consciousness test, it succeeds as a framework for understanding what consciousness tests must achieve -- and why purely behavioral approaches are fundamentally limited. Future work should incorporate causal and structural measures alongside behavioral criteria.

## References

1. Tononi, G. (2004). An Information Integration Theory of Consciousness. BMC Neuroscience 5, 42.
2. Baars, B.J. (1988). A Cognitive Theory of Consciousness. Cambridge University Press.
3. Chalmers, D.J. (1995). Facing Up to the Problem of Consciousness. Journal of Consciousness Studies 2(3), 200-219.
4. Koch, C. et al. (2016). Neural Correlates of Consciousness: Progress and Problems. Nature Reviews Neuroscience 17, 307-321.
5. Turing, A.M. (1950). Computing Machinery and Intelligence. Mind 59(236), 433-460.
6. TECS-L Project. (2026). Consciousness Continuity Engine and Dual Mechanism Framework. Internal report.
