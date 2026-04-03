# Golden Zone Experimental Protocols: Testing G = D*P/I

**Date**: 2026-04-04
**Status**: Protocol Design (pre-registration ready)
**Model dependency**: G = D*P/I derived under axioms (~95%); empirically untested. All protocols test model predictions.
**Calculator**: `calc/gz_experiment_power_analysis.py`
**Related**: H-096, H-099, H-167, `math/proofs/gz_fi_coefficient_analysis.md`, `math/proofs/gz_fi_nexus6_derivation.md`

---

## Overview

Three experimental protocols of increasing causal strength to test the model G = D*P/I, where:
- G = Genius (creative output, measured via standardized tasks)
- D = Deficit (structural brain asymmetry)
- P = Plasticity (white matter reorganization capacity)
- I = Inhibition (GABAergic tone, prefrontal inhibition)

Key quantitative predictions:
- G*I = D*P (conservation law)
- Optimal I ~ 1/e = 0.3679 (Golden Zone center)
- Golden Zone: I in [0.2123, 0.5000]
- Contraction: f(I) = 0.7I + 0.1 converges to 1/3

```
  Protocol Strength Ladder:

  Causal
  Strength
    ^
    |  P3: Pharmacological ──── CAUSAL (manipulate I, measure G)
    |        |
    |  P2: fMRI/MRS ─────────── STRUCTURAL (multi-modal correlation)
    |        |
    |  P1: EEG Entropy ──────── CORRELATIONAL (high N, fast)
    |
    +───────────────────────────> Feasibility / Cost
       Easy ($40K)         Hard ($250K)
```

---

## Protocol 1: EEG Entropy and Creative Output in the Golden Zone

### 1.1 Hypothesis (Formal, Falsifiable)

> H1: Individuals whose resting-state EEG inhibition index (I_EEG) falls
> within the Golden Zone [0.2123, 0.5000] produce significantly higher
> scores on standardized creativity tests than individuals outside this range.
>
> H1a: The relationship between I_EEG and creativity follows an inverted-U
> shape, with the peak near I = 1/e = 0.3679.
>
> H1b: Spectral entropy during creative tasks is maximized at I ~ 1/e.

### 1.2 Variables

**Independent Variable (quasi-experimental):**
- I_EEG: Resting-state inhibition index, computed from alpha/theta ratio
  and spectral entropy. Subjects grouped post-hoc into:
  - Low-I group: I < 0.21 (below Golden Zone)
  - GZ group: 0.21 <= I <= 0.50 (within Golden Zone)
  - High-I group: I > 0.50 (above Golden Zone)

**Dependent Variables:**
- G_composite: Composite creativity score (primary outcome)
  - AUT (Alternative Uses Task): fluency + originality + flexibility
  - RAT (Remote Associates Test): accuracy + response time
  - Figure Completion Task: Torrance-style, expert-rated originality
- H_task: Spectral entropy during creative tasks (secondary outcome)

**Control Variables:**
- Age (18-45, stratified sampling)
- Education level (minimum bachelor's or equivalent)
- IQ (Raven's Progressive Matrices, used as covariate)
- Handedness (right-handed only, to reduce structural variability)
- Caffeine/alcohol (24h abstinence)
- Sleep quality (Pittsburgh Sleep Quality Index, exclude PSQI > 10)
- Time of day (all sessions 09:00-12:00)
- Task order (counterbalanced Latin square)

### 1.3 Proxy Mappings

```
  Neural Measure           Model Variable    Justification
  ──────────────────────────────────────────────────────────────
  Alpha/theta power ratio  I (Inhibition)    Alpha power reflects cortical
  (resting, eyes closed)                     inhibition via thalamic gating.
                                             Alpha-theta ratio indexes
                                             inhibitory tone (Klimesch 1999,
                                             Bazanova & Vernon 2014).
                                             Normalization: z-score across
                                             sample, rescale to [0,1].

  Spectral entropy         1/I (proxy)       Low entropy = high inhibition
  (resting, broadband)                       (dominant alpha rhythm).
                                             High entropy = low inhibition
                                             (flat spectrum, seizure-like).

  AUT + RAT + Torrance     G (Genius)        Standard creativity battery.
  composite z-score                          AUT: divergent thinking.
                                             RAT: convergent insight.
                                             Torrance: figural creativity.
                                             All validated, test-retest > 0.70.

  Note: D and P are NOT directly measured in this protocol.
  This tests only the I-G relationship.
```

### 1.4 Sample Size (Power Analysis)

```
  Design: One-way ANOVA, 3 groups, alpha=0.05, power=0.80
  Expected effect: d = 0.65 (based on alpha-power/creativity literature)

  | Scenario       | d    | N/group | Total N | Power |
  |----------------|------|---------|---------|-------|
  | Conservative   | 0.50 |      64 |     192 | 0.80  |
  | Moderate *     | 0.65 |      38 |     114 | 0.80  |
  | Optimistic     | 0.80 |      26 |      78 | 0.80  |

  * Selected scenario: d=0.65 is realistic based on:
    - Jauk et al. 2012: alpha power vs. AUT, r=0.30-0.45 (d~0.65)
    - Benedek et al. 2011: alpha synchronization during AUT, d=0.6
    - Fink & Benedek 2014: meta-analysis alpha-creativity, d~0.5-0.8

  RECOMMENDED: N = 38/group x 3 groups = 114
  With 20% attrition buffer: RECRUIT 137 subjects
  Screening pool needed: ~200 (to fill Low-I and High-I tails)
```

### 1.5 Expected Results

```
  Creativity
  (G composite z)
   1.5 |
       |              *
   1.0 |           *     *
       |        *           *
   0.5 |     *                 *
       |  *                       *
   0.0 |*─────────────────────────────*
       |
  -0.5 |
       +──────────────────────────────────> I_EEG
       0.0  0.1  0.2  0.3  0.4  0.5  0.6  0.7  0.8
                  ^GZ_L  ^1/e  ^GZ_U

  Expected group means (G composite z-score):
    Low-I group  (I < 0.21):  G = -0.1 to +0.2 (disorganized, variable)
    GZ group (0.21-0.50):     G = +0.5 to +0.9 (peak creativity)
    High-I group (I > 0.50):  G = -0.2 to +0.1 (over-inhibited, conventional)

  Expected F-test: F(2, 111) > 5.0, p < 0.01
  Expected pairwise: GZ > High-I (p < 0.01), GZ > Low-I (p < 0.05)
  Expected quadratic regression: G ~ beta_1*I + beta_2*I^2, beta_2 < 0 (p < 0.05)
  Expected peak: I_peak = -beta_1/(2*beta_2), predict 0.30 < I_peak < 0.45
```

### 1.6 Falsification Criteria

The model is **REFUTED** if ANY of the following:

1. **No group difference**: F-test p > 0.10. No relationship between I and G at all.
2. **Monotonic relationship**: G increases or decreases linearly with I, no inverted-U.
   Specifically: quadratic term beta_2 is not significantly negative (p > 0.10).
3. **Peak outside GZ**: The fitted peak I_peak < 0.15 or I_peak > 0.60.
   This means the optimal inhibition is far from 1/e.
4. **Low-I group performs best**: If I < 0.21 group has highest G, the model's
   lower boundary prediction fails.

The model is **SUPPORTED** (not proven) if:
- Significant inverted-U (beta_2 < 0, p < 0.05)
- Peak within GZ [0.21, 0.50]
- GZ group significantly higher than both tails

### 1.7 Practical Requirements

```
  Equipment:
    - 64-channel EEG system (e.g., BrainVision actiCHamp, ~$80K if not available)
    - Shielded recording room
    - Stimulus presentation PC (PsychoPy/E-Prime)

  Personnel:
    - PI (cognitive neuroscientist)
    - EEG technician (0.5 FTE, 6 months)
    - Research assistant (1 FTE, 6 months)
    - Statistician (0.2 FTE)

  Timeline:
    Months 1-2:   IRB approval, task programming, pilot (N=10)
    Months 3-5:   Data collection (4 subjects/week x 12 weeks = 48/month)
    Month 6:      Analysis, manuscript preparation

  Budget estimate:
    Subject compensation: 137 x $50 = $6,850
    EEG supplies (gel, caps): $2,000
    Personnel (if externally funded): $25,000-40,000
    Cognitive tests (RAT license): $500
    Total: $35,000-50,000 (excluding existing equipment)

  Ethics:
    - Minimal risk (EEG is non-invasive)
    - Standard IRB for behavioral + EEG research
    - Informed consent, right to withdraw
    - Data anonymization, GDPR compliance
```

---

## Protocol 2: fMRI/MRS Multi-Modal Conservation Law Test

### 2.1 Hypothesis (Formal, Falsifiable)

> H2: The product G*I, measured via creativity tests (G) and MEGA-PRESS
> GABA/Creatine ratio (I), correlates positively with D*P, measured via
> structural MRI cortical asymmetry (D) and DTI fractional anisotropy (P),
> with r > 0.35 (pre-registered threshold).
>
> H2a: The conservation quantity C = G*I - D*P does not differ significantly
> from zero across subjects (equivalence test, delta = 0.15 SD units).
>
> H2b: A regression model G = beta * D * P / I explains more variance than
> G = beta_1*D + beta_2*P + beta_3*I (multiplicative vs. additive).

### 2.2 Variables

**Measured Variables (all continuous):**

| Variable | Instrument | Acquisition | ROI |
|----------|-----------|-------------|-----|
| I (Inhibition) | MEGA-PRESS MRS | 20 min | Prefrontal cortex (dlPFC) + Sensorimotor cortex |
| D (Deficit) | T1-weighted sMRI | 8 min | Sylvian fissure asymmetry index + cortical thickness asymmetry |
| P (Plasticity) | DTI (60 directions) | 12 min | Mean FA of association tracts (SLF, IFOF, UF) |
| G (Genius) | AUT + RAT + Expert rating | 45 min (outside scanner) | Composite z-score |

**Additional measures:**
| Measure | Purpose |
|---------|---------|
| Glx/Creatine (MRS) | E/I ratio computation (Glx/GABA) |
| Resting-state fMRI (10 min) | Functional connectivity as secondary G proxy |
| IQ (Raven's) | Covariate |
| BDI-II, BAI | Exclude clinical depression/anxiety (confound GABA) |

**Derived variables:**
- C_conservation = G_norm * I_norm - D_norm * P_norm
- I_normalized: GABA/Cr rescaled to [0, 1] using population min/max
- D_normalized: Asymmetry index rescaled (0 = symmetric, 1 = max asymmetry)
- P_normalized: FA relative to age-matched norms, rescaled [0, 1]
- G_normalized: Creativity composite z-score rescaled [0, max]

### 2.3 Proxy Mappings

```
  Neural Measure              Model Var   Justification
  ──────────────────────────────────────────────────────────────
  GABA/Cr (MEGA-PRESS,        I           GABA is the primary inhibitory
  dlPFC voxel 3x3x3 cm)                   neurotransmitter. dlPFC GABA
                                           correlates with executive control,
                                           working memory gating (Yoon 2016).
                                           GABA/Cr ratio is standard MRS
                                           metric with ICC = 0.72-0.82
                                           (Near 2014, Bogner 2010).

  Sylvian fissure asymmetry   D           Sylvian fissure is the most
  index (SFI) from T1w MRI                prominent sulcus affected in
                                           savant-linked conditions.
                                           SFI = (L_vol - R_vol)/(L+R).
                                           Atypical: |SFI| > 2 SD.
                                           FreeSurfer automated extraction.

  Cortical thickness           D (add)     Complementary D measure.
  asymmetry (CTA)                          CTA in temporal/parietal regions
                                           captures structural variants
                                           beyond Sylvian fissure.

  Mean FA of SLF + IFOF       P           FA (Fractional Anisotropy) in
  from DTI tractography                    association tracts indexes white
                                           matter plasticity. Higher FA in
                                           non-standard tracts suggests
                                           compensatory rewiring.
                                           SLF: language/creativity pathway.
                                           IFOF: semantic integration.
                                           (Takeuchi 2010: FA correlates
                                           with creativity, r=0.25-0.40)

  AUT + RAT + Expert          G           Same battery as Protocol 1.
  composite z-score                        Expert rating adds ecological
                                           validity (3 raters, ICC > 0.80).

  E/I ratio (Glx/GABA)        1/I or     Alternative I operationalization.
                               I_alt       If primary I (GABA/Cr) fails,
                                           E/I ratio may better capture
                                           the model's inhibition concept.
```

### 2.4 Sample Size

```
  Primary analysis: Correlation of G*I vs D*P
  Expected r = 0.50 (based on within-individual structure)

  | Scenario       | r    | N needed | Power |
  |----------------|------|----------|-------|
  | Conservative   | 0.35 |       62 | 0.80  |
  | Moderate *     | 0.50 |       34 | 0.80  |
  | Optimistic     | 0.65 |       19 | 0.80  |

  Secondary: Regression G ~ D*P/I (f^2 = 0.15, 4 predictors)
  N needed = 77 (for medium effect, power 0.80)

  RECOMMENDED: N = 62 (conservative, covers both analyses)
  With 15% scan failure: RECRUIT 72 subjects
  Estimated screening: 100 (to get range of D values)

  NOTE: Enriched sampling strategy — recruit 20% from populations with
  known structural variants (musicians, bilingual, left-handed) to ensure
  adequate D variance. Without D variance, the test has no power.
```

### 2.5 Expected Results

```
  ── Primary: G*I vs D*P Scatterplot ──

  G*I
  (normalized)
  1.0 |                               *
      |                          *  *
  0.8 |                     *  *  *
      |                  * * *
  0.6 |              * * *        r = 0.50
      |           * * *           p < 0.001
  0.4 |        * * *
      |     * * *
  0.2 |   * *
      | *
  0.0 +──────────────────────────────> D*P
      0.0  0.2  0.4  0.6  0.8  1.0

  Expected: Pearson r = 0.50 (95% CI: 0.28, 0.67) at N=62
  If r > 0.35 and p < 0.05: conservation law SUPPORTED
  If r < 0.20 or p > 0.10: conservation law REFUTED

  ── Secondary: Model Comparison ──

  Multiplicative model: G = beta * D * P / I
    Expected R^2 = 0.30 (95% CI: 0.15, 0.45)

  Additive model: G = b1*D + b2*P + b3*I
    Expected R^2 = 0.18 (95% CI: 0.05, 0.30)

  Test: Vuong test or AIC comparison
    Expected delta-AIC > 4 favoring multiplicative model

  ── Conservation quantity ──

  C = G*I - D*P (standardized)
  Expected: mean(C) = 0.00, SD(C) = 0.25
  TOST equivalence test: |mean(C)| < 0.15 (p < 0.05)
  If |mean(C)| > 0.30: conservation REFUTED
```

### 2.6 Falsification Criteria

The model is **REFUTED** if ANY of the following:

1. **No G*I vs D*P correlation**: r < 0.20 at N >= 62 (two-tailed p > 0.10).
   This means the conservation law does not hold even weakly.

2. **Additive model wins**: Additive R^2 > Multiplicative R^2.
   The multiplicative structure G = D*P/I is wrong; variables combine additively.

3. **Conservation violation**: Mean |G*I - D*P| > 0.30 SD units.
   The products are systematically unequal.

4. **I-G relationship is positive**: Higher GABA correlates with HIGHER creativity.
   This contradicts G = D*P/I (where higher I should decrease G, holding D,P fixed).

5. **D or P have no effect**: Controlling for I, neither D nor P predicts G (both p > 0.20).
   Then G is not a function of D*P at all.

### 2.7 Practical Requirements

```
  Equipment:
    - 3T MRI scanner (Siemens Prisma or equivalent)
    - MEGA-PRESS sequence for GABA (requires spectroscopy license)
    - DTI with 60+ gradient directions
    - Gannet or LCModel for MRS quantification
    - FreeSurfer for structural analysis
    - FSL for DTI tractography

  Personnel:
    - PI (cognitive/clinical neuroscientist with MRI experience)
    - MRI physicist (0.2 FTE, sequence optimization)
    - MRS analysis expert (0.3 FTE)
    - Research coordinator (0.5 FTE)
    - Statistician (0.3 FTE)

  Timeline:
    Months 1-3:   IRB, MRS sequence optimization, pilot (N=5)
    Months 4-7:   Data collection (3 subjects/week x 16 weeks = ~48/month)
    Months 8-9:   Imaging analysis pipeline
    Month 10:     Statistical analysis, manuscript

  Budget:
    MRI time: 72 subjects x 50 min x $600/hr = $36,000
    Subject compensation: 72 x $100 = $7,200
    Personnel: $50,000-70,000
    Software licenses: $3,000
    Cognitive tests: $1,000
    Total: $95,000-115,000

  Ethics:
    - Standard MRI safety (no metal, claustrophobia screening)
    - IRB for neuroimaging + cognitive testing
    - MRS is non-invasive, no contrast agent
    - Incidental findings protocol (radiologist review of T1w)
    - Data: BIDS format, anonymized, shared on OpenNeuro
```

---

## Protocol 3: Pharmacological Manipulation of Inhibition (Causal Test)

### 3.1 Hypothesis (Formal, Falsifiable)

> H3: Pharmacological manipulation of GABAergic inhibition (I) while holding
> D and P constant (same subjects, short interval) produces changes in
> creative output (G) consistent with G = D*P/I.
>
> H3a: Increasing I (benzodiazepine) decreases G, with dose-response
> following a 1/I curve.
>
> H3b: Decreasing I (flumazenil) increases G, IF baseline I > 1/e.
>
> H3c: The crossover point (where flumazenil stops helping) occurs near
> I_baseline = 1/e = 0.3679.

### 3.2 Variables

**Independent Variable (manipulated):**
- Drug condition (within-subjects, 4 levels):

| Condition | Drug | Dose | Expected I shift | Mechanism |
|-----------|------|------|-----------------|-----------|
| A: Placebo | Lactose capsule + saline IV | - | 0 (baseline) | None |
| B: Low Enhance | Diazepam (oral) | 2 mg | +0.05 to +0.10 | GABA-A positive allosteric modulator |
| C: High Enhance | Diazepam (oral) | 5 mg | +0.10 to +0.20 | Stronger GABA enhancement |
| D: Reduce | Flumazenil (IV) | 0.2 mg/kg | -0.05 to -0.10 | GABA-A competitive antagonist |

**Dependent Variables:**
- G_AUT: Alternative Uses Task score (primary)
- G_RAT: Remote Associates Test score (primary)
- G_composite: Combined creativity z-score (primary)
- EEG alpha/theta ratio during task (secondary, confirms I manipulation)
- Reaction time and error rate (safety monitoring)

**Controlled Variables (held constant by within-subjects design):**
- D: Same brain structure (same person, 1-week intervals)
- P: Same plasticity (short interval, no training between sessions)
- Time of day: All sessions at same time (within 1 hour)
- Caffeine, alcohol, other drugs: 48h washout
- Practice effects: Parallel forms of AUT/RAT (validated equivalence)
- Order effects: Counterbalanced using 4x4 Williams square design
- Blinding: Double-blind (participant + experimenter)

### 3.3 Proxy Mappings

```
  Manipulation/Measure        Model Var   Justification
  ──────────────────────────────────────────────────────────────
  Drug condition               I           Diazepam increases GABA-A
  (diazepam/flumazenil)                    receptor activity (I increases).
                                           Flumazenil blocks GABA-A
                                           (I decreases). Well-characterized
                                           pharmacology. Dose-response
                                           curves known.

  EEG alpha power change       I (verify)  Confirms drug-induced I change.
  (pre-dose vs post-dose)                  Diazepam increases beta power
                                           (paradoxical) but increases
                                           alpha coherence. Alpha/theta
                                           ratio serves as I biomarker.

  AUT + RAT composite          G           Same validated battery.
                                           Parallel forms: AUT uses
                                           different objects per session.
                                           RAT uses different word triads.

  Brain structure (MRI at      D           Measured once, assumed constant.
  screening, not repeated)                 Sylvian fissure + cortical
                                           thickness asymmetry.

  DTI (screening)              P           Measured once, assumed constant
                                           over 4-week study period.
```

### 3.4 Sample Size

```
  Design: Within-subjects, 4 conditions, rho=0.60 (creativity test-retest)
  Expected effect: d = 0.65 (drug-induced creativity change)

  | Scenario       | d    | N subjects | Total sessions | Power |
  |----------------|------|------------|----------------|-------|
  | Conservative   | 0.50 |         20 |             80 | 0.80  |
  | Moderate *     | 0.65 |         12 |             48 | 0.80  |
  | Optimistic     | 0.80 |         10 |             40 | 0.80  |

  * Within-subjects design dramatically reduces N through rho=0.60.

  RECOMMENDED: N = 20 subjects x 4 sessions = 80 total sessions
  Choosing N=20 (conservative) because:
    (a) Drug studies require extra safety margin
    (b) Some subjects may withdraw due to side effects
    (c) Allows subgroup analysis (high-I vs low-I baseline)
  With 20% dropout: RECRUIT 25 subjects

  NOTE: Each subject also gets baseline MRI + DTI (1 screening session).
  Total contact: 5 sessions per subject (1 screening + 4 drug sessions).
  Minimum washout between drug sessions: 7 days (diazepam t_half ~ 48h).
```

### 3.5 Expected Results

```
  ── Primary: G(I) Dose-Response Curve ──

  G (creativity
  composite z)
   1.0 |
       |  *                               Flumazenil: I decreases
   0.8 |     *                            G increases (if baseline I > 1/e)
       |
   0.6 |        * ← Placebo baseline
       |
   0.4 |              *                   Diaz 2mg: I increases slightly
       |                                  G decreases moderately
   0.2 |                    *             Diaz 5mg: I increases more
       |                                  G decreases more
   0.0 +──────────────────────────────> I (estimated)
       0.25   0.30   0.35   0.40   0.50   0.60

  Expected numerical results (population with baseline I ~ 0.38):

  | Condition   | I est. | G/G_base | AUT fluency | RAT accuracy |
  |-------------|--------|----------|-------------|--------------|
  | Flumazenil  | 0.30   | 1.27     | 25.3        | 19.0         |
  | Placebo     | 0.38   | 1.00     | 20.0        | 15.0         |
  | Diaz 2mg    | 0.45   | 0.84     | 16.9        | 12.7         |
  | Diaz 5mg    | 0.53   | 0.72     | 14.3        | 10.7         |

  Expected within-subjects ANOVA:
    F(3, 57) > 4.0, p < 0.01
    Linear trend (G decreasing with I): p < 0.01
    Quadratic component: p = borderline (0.05-0.15)

  ── Key Prediction: Asymmetric Response ──

  For subjects with HIGH baseline I (> 0.40):
    Flumazenil → large G increase (toward GZ center)
    Diazepam → moderate G decrease

  For subjects with LOW baseline I (< 0.35):
    Flumazenil → small G increase OR DECREASE (past GZ center)
    Diazepam → G decrease

  This baseline-dependent asymmetry is the STRONGEST test.
  A simple "less inhibition = more creativity" model predicts
  symmetric effects. G = D*P/I predicts the asymmetry.

  ── Fitted Curve ──

  Fit: G = k/I (where k = D*P for each subject)
  Expected: R^2 > 0.70 for within-subject G vs 1/I
  Compare: G = a + b*I (linear model)
  Expected: R^2 = 0.50-0.60 (worse fit)
  AIC difference: delta_AIC > 4 favoring 1/I model
```

### 3.6 Falsification Criteria

The model is **REFUTED** if ANY of the following:

1. **No drug effect on creativity**: F-test p > 0.10.
   Neither diazepam nor flumazenil changes creativity.
   (This would also challenge the general GABA-creativity link.)

2. **Diazepam INCREASES creativity**: If enhancing GABA increases G,
   the model G = D*P/I is wrong (higher I should decrease G).

3. **Flumazenil DECREASES creativity in high-I subjects**: If reducing
   inhibition in over-inhibited subjects makes them LESS creative,
   the 1/I relationship is wrong.

4. **No baseline-dependent asymmetry**: If flumazenil has the same
   effect regardless of baseline I, the Golden Zone concept is wrong.
   Specifically: interaction of drug x baseline-I-group is not
   significant (p > 0.10).

5. **Linear model fits better than 1/I**: If G = a + b*I (linear)
   has lower AIC than G = k/I, the multiplicative model is wrong.

6. **Within-subject G*I is not constant**: If G*I varies by more than
   0.30 SD across drug conditions within the same subject (where D*P
   is constant), the conservation law fails.

### 3.7 Practical Requirements

```
  Equipment:
    - EEG system (32-channel minimum, for I verification)
    - IV infusion pump (for flumazenil)
    - Pulse oximeter + blood pressure monitor (safety)
    - Emergency resuscitation equipment (flumazenil can precipitate seizures
      in benzodiazepine-dependent individuals — exclude these)
    - 3T MRI (screening session only)

  Drugs:
    - Diazepam 2mg and 5mg tablets (oral, commercially available)
    - Flumazenil 0.1 mg/mL solution (IV, commercially available)
    - Placebo capsules + saline (matched appearance)
    - All drugs from hospital pharmacy with proper labeling

  Personnel:
    - PI (cognitive neuroscientist + pharmacology training)
    - Study physician (MD, present during all drug sessions)
    - Research nurse (IV administration, vital signs)
    - EEG technician (0.5 FTE)
    - Research coordinator (0.5 FTE, 12 months)
    - Clinical pharmacist (drug preparation, blinding)
    - Statistician (0.3 FTE)

  Timeline:
    Months 1-4:   IND application, IRB, DSMB setup, drug procurement
    Month 5:      Pilot (N=3, open-label safety + dose confirmation)
    Months 6-10:  Data collection (25 subjects x 5 sessions)
                  Rate: 2 subjects/week starting, 4-week rolling
    Month 11:     Analysis
    Month 12:     Manuscript

  Budget:
    Screening MRI: 25 x $600 = $15,000
    Drug costs: 25 x 4 x $50 = $5,000
    EEG sessions: 25 x 4 x $200 = $20,000
    Study physician: $40,000 (0.3 FTE x 12 months)
    Research nurse: $30,000 (0.4 FTE)
    Subject compensation: 25 x 5 sessions x $150 = $18,750
    Insurance/liability: $10,000
    Personnel (PI, coordinator, tech): $60,000
    Miscellaneous (supplies, IRB fees): $5,000
    Total: $200,000-250,000

  Ethics and Safety:
    CRITICAL — this protocol involves drug administration.

    Inclusion criteria:
      - Age 18-40
      - No psychiatric diagnosis (SCID screening)
      - No benzodiazepine use in past 6 months
      - No seizure history (flumazenil contraindication)
      - No pregnancy (urine test at each session)
      - No substance use disorder
      - Normal liver function (diazepam metabolism)

    Exclusion criteria:
      - Benzodiazepine dependence or recent use (seizure risk with flumazenil)
      - Epilepsy or seizure history
      - Pregnancy or breastfeeding
      - Chronic liver disease
      - Current psychotropic medication
      - Known allergy to benzodiazepines

    Safety monitoring:
      - Vital signs every 15 min during drug sessions
      - Continuous pulse oximetry
      - DSMB (Data Safety Monitoring Board) review after every 5 subjects
      - Stop rules: any SAE (serious adverse event) triggers review
      - Post-session monitoring: 2 hours after flumazenil, 4 hours after diazepam
      - No driving for 24h after drug sessions

    Regulatory:
      - IND (Investigational New Drug) application to FDA
        (Off-label use of approved drugs may qualify for IND exemption)
      - IRB approval (full board review, not expedited)
      - Clinical trial registration (ClinicalTrials.gov)
      - GCP (Good Clinical Practice) compliance
      - DSMB charter
```

---

## Cross-Protocol Integration

### Staged Execution Plan

```
  Year 1:  Protocol 1 (EEG Entropy)
           - Fastest to execute, lowest risk
           - Results inform P2 and P3 design
           - Provides I_EEG distribution for population

  Year 2:  Protocol 2 (fMRI/MRS)
           - Uses P1 creativity battery (validated)
           - Adds direct GABA measurement
           - Tests conservation law

  Year 3:  Protocol 3 (Pharmacological)
           - Uses P1+P2 norms for expected values
           - Only proceed if P1 and P2 show GZ signal
           - Strongest causal test
```

### Convergence Criteria

```
  All 3 protocols support G = D*P/I if:
    P1: Inverted-U with peak in GZ           (correlational)
    P2: G*I ~ D*P correlation r > 0.35       (structural)
    P3: 1/I dose-response curve fits         (causal)

  Model REFUTED if 2 of 3 protocols show falsification.
  Model WEAKENED if 1 of 3 shows falsification.
  Model SUPPORTED (not proven) if all 3 pass.
```

### Limitations Common to All Protocols

```
  1. PROXY PROBLEM: D, P, I are model variables mapped to neural measures.
     The mapping itself is a hypothesis. If mapping is wrong, all tests
     are testing the wrong thing. Mitigation: use multiple proxies per
     variable and test robustness.

  2. NORMALIZATION: Converting neural measures (GABA in mM, FA in [0,1],
     SFI in mm) to unitless model variables [0,1] requires arbitrary
     normalization. Different normalization choices may change results.
     Mitigation: report results for 3+ normalization schemes.

  3. INDIVIDUAL DIFFERENCES: D*P is assumed relatively stable for each
     person. In reality, P may fluctuate (sleep, learning, stress).
     Mitigation: P3 uses short intervals; P1/P2 are single-session.

  4. MODEL INCOMPLETENESS: G = D*P/I may be a first approximation.
     The true relationship could be G = f(D,P,I) where f is more complex.
     Mitigation: test alternative models (additive, power-law) alongside.

  5. ECOLOGICAL VALIDITY: Lab creativity tests (AUT, RAT) may not capture
     real-world creative achievement. Mitigation: include Creative
     Achievement Questionnaire (Carson et al. 2005) as secondary outcome.
```

---

## Pre-Registration Checklist

For each protocol, the following must be pre-registered (e.g., on OSF or AsPredicted):

- [ ] Exact hypothesis statements (H1/H2/H3 and sub-hypotheses)
- [ ] Sample size justification with power analysis
- [ ] Primary and secondary outcomes
- [ ] Exact analysis plan (statistical tests, model comparisons)
- [ ] Falsification criteria (specific numerical thresholds)
- [ ] Normalization procedure for model variables
- [ ] Exclusion criteria for subjects and data points
- [ ] Multiple comparison correction method (Bonferroni for planned comparisons)
- [ ] Exploratory analyses clearly labeled as such

---

*Generated 2026-04-04. Calculator: calc/gz_experiment_power_analysis.py*
*Related: H-096, H-099, H-167, calc/experimental_protocol.py*
