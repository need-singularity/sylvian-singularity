# Hypothesis Review 155: GABA Concentration and Inhibition Mapping

## Status: 🔬 Under experimentation

## Hypothesis

> GABA (gamma-aminobutyric acid) concentration directly corresponds to Inhibition (I) in our model. GABA↑ → I↑. Normal people have I≈0.5-0.7, savants have I≈0.3-0.4 (Golden Zone), and epilepsy patients have I<0.2 (chaotic region).

## Background

GABA is the primary inhibitory neurotransmitter in the central nervous system. Approximately 30-40% of all brain synapses are GABAergic, and GABA suppresses excessive excitation in neural circuits. Abnormalities in the GABA system are associated with various neurological conditions including epilepsy, anxiety disorders, and savant syndrome.

In our model, Inhibition (I) represents the level of inhibition in neural circuits, and it sits in the denominator of the formula G = D × P / I. If GABA concentration can be directly mapped to this I value, a pathway opens to verify Golden Zone theory at the neurochemical level.

Related hypotheses: Hypothesis 004 (Boltzmann-inhibition temperature), Hypothesis 158 (brainwave-temperature), Hypothesis 162 (acquired savant)

## GABA Concentration → Inhibition Mapping

```
  GABA concentration (relative)    Inhibition (I)         State
  ──────────────────────────       ──────────────         ──────
  Very high (>1.5x)         →      I ≈ 0.7-0.9           Over-inhibited (lethargy, sedation)
  Normal (1.0x)             →      I ≈ 0.5-0.7           Normal range
  Slightly low (0.7x)       →      I ≈ 0.3-0.4           Golden Zone! (savant)
  Low (0.4x)                →      I ≈ 0.15-0.25         Epilepsy risk
  Very low (<0.2x)          →      I < 0.15              Chaos (seizure)
```

## GABA-I Mapping Diagram

```
  I (Inhibition)
  1.0│
     │  ■ Over-inhibited (benzodiazepine overdose)
  0.9│  ■
     │  ■
  0.7│──■──────────────────────── Normal upper bound
     │    ■
  0.6│      ■ ← Normal range
     │        ■
  0.5│─ ─ ─ ─ ─●─ ─ ─ ─ ─ ─ ─ ─ Critical line (Riemann)
     │          ■
  0.4│ ┌─────────■──────────┐
     │ │ Golden Zone  ■ Savant │
  0.35│ │    1/e ──★────────│── Golden Zone center
     │ │          ■        │
  0.3│ │           ■       │
     │ └───────────■───────┘
  0.21│─ ─ ─ ─ ─ ─ ─■─ ─ ─ ─ ─ ─ Golden Zone lower bound
     │               ■
  0.15│                ■ ← Epilepsy risk
     │                  ■
  0.05│                    ■ Chaos/seizure
     │
  0.0└──┬──┬──┬──┬──┬──┬──┬──→ GABA concentration
       0.2 0.4 0.6 0.8 1.0 1.2 1.4 (relative)
```

## Clinical Data Correspondence

| State | GABA level | Estimated I | G (D=0.5, P=0.7 basis) | Region |
|---|---|---|---|---|
| Normal (average) | 1.0x | 0.60 | 0.58 | Normal |
| Normal (high) | 0.85x | 0.50 | 0.70 | Critical line |
| Savant syndrome | 0.65x | 0.35 | 1.00 | Golden Zone center |
| Epilepsy (mild) | 0.45x | 0.22 | 1.59 | Golden Zone lower bound |
| Epilepsy (moderate) | 0.30x | 0.15 | 2.33 | Chaotic region |
| Benzodiazepine dose | 1.4x | 0.80 | 0.44 | Over-inhibited |

## Key Observations

### 1. Nonlinear Mapping
The relationship between GABA concentration and I is likely not simply linear. Since the dose-response curve of GABA receptors (GABA-A, GABA-B) is sigmoid in shape:

```
  I = I_max / (1 + exp(-k × (GABA - GABA_50)))
```

where GABA_50 is the GABA concentration that induces half-maximum inhibition.

### 2. Savant's GABA Golden Zone
In savant syndrome, when GABA is slightly lower than normal (≈0.6-0.7x), I enters the Golden Zone (0.24-0.48). This is consistent with Treffert's clinical observation that "appropriate disinhibition is the key to savant abilities."

### 3. Boundary with Epilepsy
When GABA drops too low, I falls below the Golden Zone lower bound (0.21), and the G value runs away. This becomes a mathematical model of epileptic seizures — insufficient inhibition causes neural activity to become uncontrollable.

## Pharmacological Implications

If I can be positioned in the Golden Zone by modulating GABA:
- Antiepileptics (increase GABA) → pull I from chaos up to Golden Zone
- Stimulants (decrease GABA) → bring I down from normal to Golden Zone
- Precision GABA modulation → target I = 1/e ≈ 0.368

## Limitations

- GABA concentration varies by brain region; difficult to reduce to a single I value for the whole brain
- Besides GABA, other neurotransmitters such as glutamate and dopamine also contribute to inhibition
- Low precision of in vivo GABA measurement (MRS) makes it difficult to distinguish Golden Zone-level differences
- Nonlinear parameters (k, GABA_50) of the GABA-I mapping are still undetermined

## Verification Directions

- [ ] Compare GABA concentrations in savant/normal/epilepsy groups by MRS (magnetic resonance spectroscopy)
- [ ] Separate modeling of inhibitory contributions by GABA-A/GABA-B receptor type
- [ ] Track GABA-I changes before and after antiepileptic drug administration
- [ ] Correlation analysis of GABA changes due to meditation (Hypothesis 159) and I changes
- [ ] Construct region-by-region I map from GABA distribution by brain area

---

*Written: 2026-03-22*
*Status: 🔬 Under experimentation — GABA-I nonlinear mapping parameters need determination*
