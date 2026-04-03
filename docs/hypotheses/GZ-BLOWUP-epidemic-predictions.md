# GZ-BLOWUP: Epidemic Predictions from G=D*P/I Mapping to SIR

**Grade**: STRUCTURAL (form match) / REFUTED (GZ constant predictions)
**Status**: Quantitative test complete -- 15 diseases, 2 mappings
**Date**: 2026-04-04
**Script**: `calc/gz_epidemic_analyzer.py`
**Related**: GZ-BLOWUP-universality.md (domain #4), GZ-BLOWUP-predictions.md
**Golden Zone dependency**: YES -- GZ constants (1/e, 0.2123, 0.5) are model-dependent

---

## Core Mapping

> R_0 = beta * S_0 / gamma is algebraically identical to G = D * P / I.

| G=D*P/I | SIR model | Units | Axiom satisfied? |
|---------|-----------|-------|------------------|
| G (output) | R_0 (basic reproduction number) | dimensionless | YES |
| D (deficit) | beta (transmission rate) | 1/(time*contacts) | YES (extensive) |
| P (plasticity) | S_0 (susceptible fraction) | dimensionless | YES (extensive) |
| I (inhibition) | gamma (recovery rate) | 1/time | PARTIAL (not dimensionless!) |

**Dimensional problem**: The G=D*P/I axioms require I to be a dimensionless fraction
in (0,1). But gamma is a rate with units 1/time. Two rescue attempts:

1. I = gamma/beta: dimensionless but often > 1 (violates axiom)
2. I = 1/R_0: always in (0,1) for R_0 > 1, but circular (defines G in terms of itself)

Neither mapping fully satisfies the axioms.

---

## Prediction 1: Golden Zone of Epidemics

**Claim**: Epidemics with I = gamma/beta in GZ [0.2123, 0.5000] are "endemic"
(sustainable); below GZ are explosive; above GZ are self-limiting.

### Test Results (Mapping 1: I = gamma/beta)

```
  Disease                           I=g/b    GZ Zone              Actual       Match
  ---------------------------------------------------------------------------------
  Malaria                           0.1000   EXPLOSIVE            endemic       NO
  Smallpox                          0.1961   EXPLOSIVE            explosive     NO*
  COVID-19 Delta                    0.2500   GOLDEN ZONE          explosive     NO
  COVID-19 Omicron                  0.2667   GOLDEN ZONE          explosive     NO
  HIV (untreated)                   0.2740   GOLDEN ZONE          endemic       YES
  Measles                           0.2778   GOLDEN ZONE          explosive     NO
  COVID-19 (Wuhan)                  0.3333   GOLDEN ZONE          explosive     NO
  1918 Influenza                    0.5000   GOLDEN ZONE          explosive     NO
  SARS (2003)                       0.5556   SELF-LIMITING        explosive     NO
  COVID-19 (endemic 2024+)          0.5714   SELF-LIMITING        endemic       NO
  Ebola                             0.6250   SELF-LIMITING        explosive     NO
  Seasonal Influenza                1.0000   SELF-LIMITING        endemic       NO
  MERS                              1.1905   SELF-LIMITING        self-limiting NO*
  Common Cold                       2.2222   SELF-LIMITING        self-limiting NO*
  Tuberculosis                      2.7397   SELF-LIMITING        endemic       NO
  ---------------------------------------------------------------------------------
  Accuracy: 1/15 = 6.7%
```

*Smallpox, MERS, and Common Cold are borderline/arguable classifications.

### Test Results (Mapping 2: I = 1/R_0)

```
  Disease                           I=1/R_0  GZ Zone              Actual       Match
  ---------------------------------------------------------------------------------
  Malaria                           0.0100   EXPLOSIVE            endemic       NO
  Measles                           0.0667   EXPLOSIVE            explosive     YES*
  Omicron                           0.1053   EXPLOSIVE            explosive     YES*
  Smallpox                          0.1818   EXPLOSIVE            explosive     YES*
  Delta                             0.1961   EXPLOSIVE            explosive     YES*
  HIV                               0.2500   GOLDEN ZONE          endemic       YES
  Tuberculosis                      0.3333   GOLDEN ZONE          endemic       YES
  COVID-19 (Wuhan)                  0.3484   GOLDEN ZONE          explosive     NO
  SARS                              0.3704   GOLDEN ZONE          explosive     NO
  1918 Influenza                    0.5000   GOLDEN ZONE          explosive     NO
  Ebola                             0.5556   SELF-LIMITING        explosive     NO
  Seasonal Flu                      0.7692   SELF-LIMITING        endemic       NO
  Common Cold                       0.8333   SELF-LIMITING        self-limiting YES
  COVID-19 (endemic 2024+)          0.9091   SELF-LIMITING        endemic       NO
  MERS                              1.1111   SELF-LIMITING        self-limiting YES
  ---------------------------------------------------------------------------------
  Accuracy: 2/15 = 13.3% (strict)
  *If we count "explosive" correctly classified: ~5/15 for explosive alone
```

### ASCII Zone Map (I = gamma/beta)

```
  I = gamma / beta

  EXPLOSIVE       GOLDEN ZONE              SELF-LIMITING
  I < 0.2123      0.2123 <= I <= 0.5       I > 0.5
  |               |<-- ln(4/3) -->|        |
  0         0.2123    0.3679    0.5        1.0        2.0+
            lower     1/e      upper

  Malaria   #.....|.............|.........|..........................
  Smallpox  .....#|.............|.........|..........................
  Delta     ......|..#..........|.........|..........................
  Omicron   ......|...#.........|.........|..........................
  HIV       ......|....#........|.........|..........................
  Measles   ......|....#........|.........|..........................
  COVID-Wu  ......|........#....|.........|..........................
  1918 Flu  ......|.............|#........|..........................
  SARS      ......|.............|..#......|..........................
  COVID-end ......|.............|...#.....|..........................
  Ebola     ......|.............|.....#...|..........................
  Flu(seas) ......|.............|.........|..........#...............
  MERS      ......|.............|.........|...............#..........
  Cold      ......|.............|.........|........................# → 2.22
  TB        ......|.............|.........|........................# → 2.74

  Legend: # = disease position, | = GZ boundary
```

**VERDICT on Prediction 1**: REFUTED. The GZ boundaries do not separate
epidemic types. Measles (explosive) and HIV (endemic) both land in the Golden
Zone. Seasonal flu (endemic) and Ebola (explosive) both land in the
self-limiting zone. The classification accuracy (7-13%) is WORSE than random
guessing with a 3-class prior.

---

## Prediction 2: Conservation Law G*I = D*P

**Claim**: R_0 * (gamma/beta) = beta * S_0 * (gamma/beta) should be conserved.

### Test

```
  R_0 * (gamma/beta) = (beta*S_0/gamma) * (gamma/beta)
                      = S_0
                      = constant (by definition, at t=0)

  Every disease: G*I = S_0 exactly. Zero error.
```

**VERDICT**: The conservation law is a TAUTOLOGY. It is algebraically
guaranteed by the definitions, not a dynamical constraint. During an actual
epidemic, S(t) decreases over time, but gamma and beta remain constant, so
I = gamma/beta does not change to compensate. The G=D*P/I "conservation"
does not produce the SIR trajectory equations:

```
  SIR dynamics:
    dS/dt = -beta * S * I_infected
    dI_infected/dt = beta * S * I_infected - gamma * I_infected
    dR/dt = gamma * I_infected

  The conserved quantity in SIR is: S + I_infected + R = 1 (trivial)
  and the Lyapunov function: V = S - S* ln(S) + I - I* ln(I)

  Neither matches G*I = S_0.
```

**VERDICT on Prediction 2**: NOT TESTABLE. The conservation is definitional,
not dynamical. It adds no information beyond the SIR definition.

---

## Prediction 3: Meta Fixed Point I* = 1/3

**Claim**: Endemic diseases converge to gamma/beta ~ 1/3.

### Test

```
  Endemic diseases:
    Malaria            I = 0.100   (delta from 1/3: -0.233)
    HIV                I = 0.274   (delta from 1/3: -0.059)
    COVID-19 (endemic) I = 0.571   (delta from 1/3: +0.238)
    Seasonal Flu       I = 1.000   (delta from 1/3: +0.667)
    Tuberculosis       I = 2.740   (delta from 1/3: +2.406)

  Mean I (all endemic):      0.937
  Mean I (acute endemic):    0.786
  Target:                    0.333

  Range of endemic I values: 0.100 to 2.740 (27x spread)
```

**VERDICT on Prediction 3**: REFUTED. Endemic diseases span a 27-fold range
of I = gamma/beta values. The mean (0.94) is nowhere near 1/3. Even restricting
to acute respiratory endemic diseases, the mean (0.79) is 2.4x the prediction.

The claim that "COVID settled at gamma/beta ~ 0.33" is parameter-dependent.
With different (equally valid) estimates of endemic-phase beta and gamma,
you can get any value. This is not a robust finding.

---

## Prediction 4: Optimal Vaccination at I = 1/e

**Claim**: The GZ center I = 1/e corresponds to an "optimal" epidemic state,
implying vaccination should target R_0 = e = 2.718.

### Analysis

```
  Herd immunity coverage needed:
    Measles (R_0=15):    v_c = 93.3%
    Smallpox (R_0=5.5):  v_c = 81.8%
    COVID original:      v_c = 65.2%
    GZ "optimal" (R_0=e): v_c = 63.2%   <-- the GZ prediction
    Seasonal Flu:        v_c = 23.1%
```

**Critical semantic inversion**: In consciousness, G = genius is GOOD.
In epidemics, G = R_0 is BAD. The GZ "peak" at I = 1/e corresponds to
R_0 = e = 2.718, which is a moderately dangerous epidemic (like COVID).
This is not "optimal" in any public health sense -- it is the regime of
maximum sustained damage.

If anything, the GZ mapping suggests that R_0 ~ e diseases are the most
"efficient" pathogens from the virus's perspective. This is interesting
but requires the normative inversion to be explicitly acknowledged.

**VERDICT on Prediction 4**: SEMANTICALLY INVERTED. The mapping works
structurally but "optimal" means opposite things in the two domains.
The prediction is unfalsifiable as stated because it does not specify
optimal for whom.

---

## Prediction 5: Phase Transition at GZ Boundaries

**Claim**: Epidemiological behavior changes sharply at I = 0.2123 (GZ lower)
and I = 0.5 (GZ upper).

### Test

The SIR model has exactly ONE phase transition: R_0 = 1 (I_eff = 1).
- R_0 > 1: epidemic grows
- R_0 < 1: epidemic dies out

There is no known phase transition at:
- R_0 = 4.71 (corresponding to I = 0.2123)
- R_0 = 2.00 (corresponding to I = 0.5)
- R_0 = e (corresponding to I = 1/e)

The SIR dynamics are smooth functions of R_0. The only non-analyticity
is at R_0 = 1 (transcritical bifurcation).

Extended models (SIS, SEIR, network SIR) also have their primary
bifurcation at R_0 = 1. Some network models have a secondary transition
at R_0 ~ 2 (percolation on random graphs), but this depends on network
topology, not on the GZ constants.

**VERDICT on Prediction 5**: REFUTED by SIR theory. No phase transitions
exist at the GZ boundary values.

---

## Where the Mapping DOES Work

### 1. Structural Form (CONFIRMED)

R_0 = beta * S_0 / gamma has exactly the form D * P / I.
This is the simplest multiplicative function of three positive variables
where the output increases with two (beta, S_0) and decreases with one
(gamma). The G=D*P/I universality theorem (Cencov/Cauchy derivation)
guarantees this form under the five axioms.

This is a genuine structural result: the SIR R_0 formula did not have
to take this form. It does because the SIR assumptions (homogeneous
mixing, constant rates, exponential waiting times) happen to satisfy
the independence and scale-invariance axioms.

### 2. Monotonicity Structure (CONFIRMED)

- More transmissible pathogen (higher beta) => higher R_0 (higher G)
- More susceptibles (higher S_0) => higher R_0 (higher G)
- Faster recovery (higher gamma) => lower R_0 (lower G)

This is trivially true but confirms the axiom mapping is correct.

### 3. Dimensional Analysis (CONFIRMED)

R_0 is dimensionless, as required for G. The product beta*S_0 has units
of rate, and gamma has units of rate, so R_0 = beta*S_0/gamma is
indeed dimensionless. The axiom that G is a "performance measure" maps
to R_0 being a "transmission efficiency measure."

---

## Where the Mapping FAILS

### 1. GZ Constants Are Meaningless in Epidemiology

The values 1/e, 0.2123, 0.5 derive from:
- 1/e: minimizer of I^I (information-theoretic, from n=6 divisor entropy)
- 0.2123 = 1/2 - ln(4/3): Shannon entropy of 3-to-4 state transition
- 0.5: Riemann critical line Re(s) = 1/2

None of these have any epidemiological derivation. The SIR model has no
entropy function related to n=6 divisors, no connection to the Riemann
zeta function, and no information-theoretic optimality at I = 1/e.

### 2. Classification Accuracy Is Worse Than Random

```
  Mapping 1 (I = gamma/beta):   1/15 = 6.7% accuracy
  Mapping 2 (I = 1/R_0):        2/15 = 13.3% accuracy
  Random baseline (3 classes):   33.3% accuracy

  GZ predictions are 3-5x WORSE than random guessing.
```

### 3. The Mapping Is Not Predictive

Given beta, gamma, S_0, we compute R_0 = beta*S_0/gamma directly.
The G=D*P/I framing adds zero computational power. No new prediction
emerges that R_0 alone cannot provide.

### 4. Semantic Inversion Breaks Interpretation

In consciousness: high G = good (genius, creativity, peak performance)
In epidemics: high G = bad (more infections, more deaths)

The entire GZ "optimization" framework inverts when applied to epidemics.
The "frozen zone" (I > 0.5) is actually the PUBLIC HEALTH IDEAL. The
"seizure zone" (I < 0.21) is the worst-case pandemic scenario.

---

## Comparison: GZ vs. Standard Epidemiology

| Question | GZ answer | Standard epi answer | Agreement? |
|----------|-----------|-------------------|------------|
| What is R_0? | G = D*P/I | beta*S/gamma | SAME (tautology) |
| When does epidemic grow? | I < some threshold | R_0 > 1 | SAME (restatement) |
| Critical transition point | I = 0.2123 or 0.5 | R_0 = 1 | DISAGREE |
| Optimal endemic state | I = 1/e (R_0=e) | R_0 = 1 (elimination) | DISAGREE |
| Conservation law | G*I = S_0 | S+I+R = 1 | DIFFERENT (both true) |
| Herd immunity threshold | Not derived | 1 - 1/R_0 | GZ ADDS NOTHING |
| Dynamic trajectory | Not derived | SIR ODEs | GZ CANNOT PREDICT |

---

## Final Grade

```
  Structural form match:        CONFIRMED (exact algebraic identity)
  GZ zone predictions:          REFUTED   (7-13% accuracy, worse than random)
  Conservation law:             TAUTOLOGICAL (not testable)
  Meta fixed point I* = 1/3:    REFUTED   (endemic I ranges 0.1 to 2.7)
  Optimal vaccination:          SEMANTICALLY INVERTED (good for virus, bad for humans)
  Phase transitions at GZ:      REFUTED   (SIR has transition only at R_0 = 1)

  Overall: STRUCTURAL MATCH + GZ OVERLAY REFUTED

  The R_0 formula is an instance of the D*P/I functional form, confirming
  that this form arises across domains. But the Golden Zone constants
  (1/e, 0.2123, 0.5) have NO predictive power in epidemiology.

  This is an important negative result: it delineates the boundary of
  G=D*P/I universality. The FORM is universal; the CONSTANTS are not.
```

---

## What Survives

1. The structural form G=D*P/I appears in epidemiology (R_0 = beta*S/gamma).
   This confirms the Cencov uniqueness theorem applies broadly.

2. The form match tells us something about WHY R_0 has this particular
   structure: it is the unique function satisfying positivity, monotonicity,
   separability, and scale invariance for three independent variables.

3. The FAILURE of GZ constants is equally informative: it tells us that
   the 1/e, 0.2123, 0.5 values are specific to information-theoretic
   systems (consciousness, neural networks, channel capacity) and do NOT
   transfer to population dynamics where the relevant entropy is different.

4. The semantic inversion (high G = bad in epidemics) suggests that G=D*P/I
   describes "amplification efficiency" generically, and whether amplification
   is good or bad depends on the domain.

---

## References

- Anderson & May, "Infectious Diseases of Humans" (1991) -- R_0 theory
- Kermack & McKendrick, Proc. R. Soc. A (1927) -- original SIR model
- Diekmann, Heesterbeek & Metz, J. Math. Biol. (1990) -- R_0 definition
- Guerra et al., Lancet Infect. Dis. (2017) -- measles R_0
- Li et al., NEJM (2020) -- COVID-19 early R_0
- Liu & Rocklov, J. Travel Med. (2022) -- Omicron R_0
- Smith et al., PLoS Med. (2007) -- malaria R_0
- Breban et al., Lancet (2013) -- MERS R_0
- Biggerstaff et al., BMC Infect. Dis. (2014) -- influenza R_0
