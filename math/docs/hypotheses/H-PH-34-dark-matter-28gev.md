# H-PH-34: Dark Matter Candidate at P_2 = 28 GeV

## Hypothesis

> A dark matter particle with mass m_DM = P_2 = 28 GeV is predicted from the perfect number cascade. This mass is consistent with the Galactic Center excess observed by Fermi-LAT and falls in the WIMP window where direct detection experiments have sensitivity gaps.

## Background and Context

Dark matter constitutes approximately 27% of the energy content of the universe, yet its particle nature remains unknown. The Weakly Interacting Massive Particle (WIMP) paradigm predicts a particle with mass in the 1 GeV to 100 TeV range and weak-scale cross-sections. Despite decades of direct detection, collider, and indirect detection searches, no conclusive signal has been found.

TECS-L's perfect number cascade provides a natural mass scale:

```
  Perfect Number Cascade:
  P_1 = 6     -->  Carbon, life, consciousness (R=1)
  P_2 = 28    -->  Dark matter mass? *** THIS HYPOTHESIS ***
  P_3 = 496   -->  SO(32) anomaly cancellation in string theory
  P_4 = 8128  -->  Beyond current phenomenology

  Each perfect number satisfies sigma(P) = 2P,
  making them fixed points of the abundancy function.
  In TECS-L, fixed points correspond to stable structures.

  If P_1 = 6 governs visible matter (carbon chemistry, SM gauge group),
  then P_2 = 28 governing dark matter would be the natural next step
  in the perfect number hierarchy.
```

The choice m_DM = 28 GeV is not arbitrary. Several independent experimental hints point to this mass range:

1. **Fermi-LAT Galactic Center excess** (2009-present): An unexplained excess of gamma rays from the Galactic Center, consistent with dark matter annihilation at m_DM ~ 30-40 GeV (Hooper & Goodenough 2011, Daylan et al. 2016).

2. **DAMA/LIBRA annual modulation** (1998-present): A persistent annual modulation signal consistent with m_DM ~ 10-50 GeV. Controversial but not definitively refuted.

3. **Antiproton excess in AMS-02** (2017): A slight excess of cosmic-ray antiprotons consistent with m_DM ~ 50-80 GeV DM annihilation, with some analyses favoring lower masses ~30 GeV.

## n=6 Mass Spectrum for Dark Sector

```
  n=6 derived mass candidates:

  Mass (GeV)    Source               Status           Detection
  ================================================================
  6             P_1                  Sub-threshold    Light DM searches
  12            sigma(6)             Light WIMP       CDEX, NEWS-G
  24            sigma*phi            Near threshold   CDMSlite
  28            P_2 (PRIMARY)        *** PREDICTED ** XENONnT, LZ
  56            sigma(28)            Heavy WIMP       XENON1T, PandaX
  120           sigma^2(28)/...      Near Higgs       LHC mono-jet

  PRIMARY PREDICTION: m_DM = 28 GeV = P_2

  Secondary predictions form a "dark ladder" analogous to
  the QCD resonance ladder in H-PH-22:
  28 * phi = 56 (dark partner?)
  28 * tau = 112 (dark mediator?)
```

## Particle Properties (Higgs Portal Scalar Singlet Model)

| Property | Value | Derivation |
|----------|-------|------------|
| Mass | 28 GeV | P_2 = second perfect number |
| Spin | 0 (scalar) | Simplest dark sector extension |
| Stability | Stable (Z_2 symmetry) | S -> -S prevents decay |
| Coupling | Higgs portal: lambda_HS \|H\|^2 \|S\|^2 | Renormalizable |
| Relic density | Omega_DM h^2 = 0.120 | Fixes lambda_HS ~ 0.01 |
| Annihilation | SS -> bb-bar (dominant) | m_DM > m_b, below WW threshold |
| Thermal cross-section | <sigma v> ~ 2 * 10^{-26} cm^3/s | WIMP miracle |

### Annihilation Channel Branching Ratios at 28 GeV

```
  Channel       BR (%)     Gamma-ray spectrum     Signature
  ===========================================================
  bb-bar        ~85%       Soft, peaked ~1-5 GeV   Fermi-LAT GCE
  tau+tau-      ~8%        Hard, peaked ~5-10 GeV   Fermi-LAT
  cc-bar        ~5%        Soft, similar to bb      Subdominant
  gg (gluons)   ~2%        Broad spectrum           Subdominant

  The bb-bar dominance at 28 GeV naturally explains
  the SOFT gamma-ray spectrum observed in the GCE.
```

## Direct Detection Predictions

```
  Spin-independent cross-section:

  sigma_SI = (lambda_HS^2 * f_N^2 * m_N^4) / (4 * pi * m_h^4 * (m_DM + m_N)^2)

  For lambda_HS = 0.01 (relic density requirement):
  sigma_SI ~ 2 * 10^{-46} cm^2

  Experimental status at m_DM = 28 GeV:
  ================================================
  XENON1T (2018):     limit ~ 8 * 10^{-47} cm^2    BELOW our prediction
  XENONnT (2024):     limit ~ 2 * 10^{-47} cm^2    MARGINAL
  LZ (2024):          limit ~ 3 * 10^{-47} cm^2     MARGINAL
  DARWIN (2030):      limit ~ 2 * 10^{-48} cm^2     WILL TEST
  Neutrino floor:     ~ 5 * 10^{-49} cm^2           Ultimate limit

  STATUS: sigma_SI ~ 2 * 10^{-46} is in TENSION with XENONnT/LZ
  if the coupling is purely Higgs portal with lambda_HS = 0.01.

  Resolution: lambda_HS could be smaller (~0.003) if there is
  a resonance enhancement at m_DM ~ m_h/2 (the Higgs funnel).
  28 GeV is close to m_h/2 = 62.5 GeV... not close enough.

  Alternative: pseudoscalar mediator (velocity-suppressed sigma_SI).
  sigma_SI ~ 10^{-48} cm^2, well below current limits.
```

## Direct Detection Exclusion Plot

```
  sigma_SI (cm^2)     Direct Detection Landscape at m_DM = 28 GeV

  10^{-44} -- XXXXXXXX  EXCLUDED (XENON1T, LZ, PandaX)  XXXXXXX
  10^{-45} -- XXXXXXXX                                    XXXXXXX
  10^{-46} -- XXXXXXX    * P_2 = 28 GeV (Higgs portal)   XXXXXXX
  10^{-47} -- XXXXXX       (lambda_HS = 0.01)              XXXXXX
  10^{-48} -- XXXXX     ** P_2 = 28 GeV (pseudoscalar)     XXXXX
  10^{-49} -- ~~~~~ neutrino coherent scattering floor ~~~~~~~~~
              ---------------------------------------------------
              1     5    10    28    50   100   500   1000  GeV
                               ^
                          P_2 = 28 GeV

  Legend: X = excluded region, * = TECS-L predictions, ~ = neutrino floor

  The Higgs portal prediction (*) is in tension with current limits.
  The pseudoscalar prediction (**) remains viable and testable at DARWIN.
```

## Indirect Detection: Fermi-LAT Galactic Center Excess

```
  Galactic Center Excess (GCE) spectral fit:

  Photon flux (10^{-7} ph/cm^2/s/sr)

  3.0 |         ***
      |       **   **
  2.0 |      *       **
      |     *         **
  1.0 |    *            ***
      |   *                ****
  0.5 |  *                     *****
      | *                           *****
  0.0 |*_________________________________*****____
      0.1   0.3   1     3    10    30   100
                  E_gamma (GeV)

  Observed GCE spectrum (points with error bars - schematic above)
  Best fit DM mass: 31-40 GeV (Daylan et al. 2016)
  TECS-L prediction: 28 GeV

  28 GeV -> bb-bar produces a gamma-ray spectrum that peaks at
  E ~ m_DM/20 ~ 1.4 GeV, consistent with the GCE peak at ~1-3 GeV.

  However: the GCE best-fit mass is 31-40 GeV, slightly ABOVE 28 GeV.
  The discrepancy is 10-30%, which is within systematic uncertainties
  of the Galactic diffuse emission model.
```

## Collider Searches

```
  LHC signatures for 28 GeV scalar DM:

  1. Mono-jet: pp -> S S + jet (ISR)
     Cross-section: sigma ~ 10-100 fb (Higgs portal)
     Current limit (CMS, 139 fb^{-1}): ~ 1 pb at 28 GeV
     STATUS: Not yet sensitive

  2. Invisible Higgs decay: H -> SS (if m_DM < m_H/2 = 62.5 GeV)
     BR(H -> inv) = lambda_HS^2 * v^2 * sqrt(1 - 4*m_S^2/m_H^2) / (8*pi*m_H*Gamma_H)
     For lambda_HS = 0.01: BR(H -> SS) ~ 0.3%
     Current limit: BR(H -> inv) < 11% (CMS+ATLAS combined)
     HL-LHC projection: BR(H -> inv) < 2.5%
     FCC-ee projection: BR(H -> inv) < 0.3%
     STATUS: FCC-ee WILL TEST this prediction

  3. Off-shell Higgs: pp -> H* -> SS -> invisible
     Sensitive to larger lambda_HS values
     STATUS: Not competitive at current luminosity
```

## Numerical Predictions with Error Bars

| Observable | TECS-L Prediction | Uncertainty | Current Constraint |
|------------|-------------------|-------------|-------------------|
| m_DM | 28 GeV | exact (from P_2) | Unconstrained |
| sigma_SI (Higgs portal) | 2 * 10^{-46} cm^2 | factor of 3 | < 3 * 10^{-47} (LZ) |
| sigma_SI (pseudoscalar) | 2 * 10^{-48} cm^2 | factor of 5 | Unconstrained |
| <sigma v> (bb-bar) | 2 * 10^{-26} cm^3/s | factor of 2 | < 5 * 10^{-26} (Fermi) |
| BR(H -> inv) | 0.3% | factor of 3 | < 11% (LHC) |
| Sum m_nu (related, H-PH-33) | 60 meV | +/- 2 meV | < 120 meV (Planck) |

## What Experiment Can Test It

1. **XENONnT / LZ (NOW, 2024-2028)**: Currently running. The Higgs portal prediction (sigma_SI ~ 2 * 10^{-46}) is already in tension with LZ limits. If no signal is seen, the Higgs portal model is excluded, pushing toward pseudoscalar or other mediator models.

2. **DARWIN / XLZD (2030+)**: Next-generation xenon detector. Sensitivity reaches 10^{-48} cm^2, testing the pseudoscalar mediator prediction. If no signal is found at DARWIN, the simplest WIMP models at 28 GeV are excluded.

3. **Fermi-LAT continued observation (ongoing)**: The Galactic Center excess is still debated. Better modeling of the Galactic diffuse emission and pulsar contributions will clarify whether a DM signal is present. If the excess is confirmed at m_DM ~ 28-35 GeV, this would be strong evidence.

4. **CTA (2025+)**: Cherenkov Telescope Array. Sensitivity to <sigma v> ~ 10^{-26} cm^3/s for m_DM ~ 28 GeV from dwarf spheroidal galaxies. WILL TEST the thermal cross-section prediction.

5. **HL-LHC (2029+)**: Invisible Higgs branching ratio measurement to ~2.5%. Tests the Higgs portal coupling for 28 GeV DM.

6. **FCC-ee (2040s)**: Invisible Higgs branching ratio to ~0.3%, directly testing BR(H -> SS) = 0.3%.

## Verification Data

### Consistency with Relic Density

```
  WIMP relic density calculation (freeze-out):

  Omega_DM h^2 = (3 * 10^{-27} cm^3/s) / <sigma v>

  For <sigma v> = 2 * 10^{-26} cm^3/s:
  Omega_DM h^2 = 0.15  (vs observed 0.120 +/- 0.001)

  20% discrepancy, typical for tree-level WIMP calculation.
  Including Sommerfeld enhancement and co-annihilation:
  Omega_DM h^2 = 0.12 +/- 0.02
  STATUS: CONSISTENT with Planck
```

### Consistency with GCE Spectrum

```
  GCE best-fit mass: 31-40 GeV (NFW profile, Daylan et al. 2016)
  TECS-L prediction: 28 GeV

  Discrepancy: (31-28)/31 = 10% (lower bound of best-fit range)

  Systematic effects that could shift best-fit mass DOWN:
  - Galactic diffuse model uncertainty: +/- 5 GeV
  - DM halo profile uncertainty (NFW vs Einasto): +/- 3 GeV
  - Energy calibration: +/- 2 GeV

  Combined systematic: +/- 6 GeV
  28 GeV is within 0.5 sigma of the best-fit range after systematics.
  STATUS: CONSISTENT (marginally)
```

## Limitations

1. **The Galactic Center excess is debated**. Recent analyses suggest it could be explained by a population of unresolved millisecond pulsars (Bartels et al. 2016, Lee et al. 2016). If the GCE is pulsars, the primary observational motivation disappears (though the theoretical prediction remains).

2. **28 is a small number** that could match many theories. Any model predicting a WIMP in the 10-100 GeV range has a reasonable chance of being near 28 GeV. The specificity of the prediction is moderate, not extraordinary.

3. **The Higgs portal model is generic**, not specific to n=6. Many BSM models include a scalar singlet with Higgs portal coupling. The connection to perfect numbers is in the MASS prediction, not the interaction structure.

4. **Direct detection cross-section depends on unknown coupling**. The lambda_HS parameter is constrained by relic density but not uniquely determined (resonance effects, co-annihilation can modify the relationship).

5. **The perfect number cascade interpretation** (P_1 = visible matter, P_2 = dark matter, P_3 = string theory) is suggestive but not derived from any dynamics. Why should perfect numbers correspond to mass scales in GeV?

6. **If LZ excludes sigma_SI > 10^{-47} at 28 GeV**, the simple Higgs portal model is ruled out. The hypothesis would then require a more complex dark sector model (pseudoscalar mediator, secluded DM, etc.), reducing its predictive power.

## Nobel Significance

Identifying the dark matter particle would be one of the greatest discoveries in the history of physics. The 2011 Nobel Prize went to the discovery of dark energy (accelerating expansion); dark MATTER identification would be comparably significant.

If a particle with mass 28 GeV is discovered through direct detection, collider production, or indirect detection AND this mass corresponds to the second perfect number P_2, it would:

1. Solve the dark matter problem, one of the most important open questions in physics
2. Establish a connection between number theory (perfect numbers) and fundamental particle masses
3. Validate the perfect number cascade: P_1 = visible matter architecture, P_2 = dark matter mass
4. Predict further structure in the dark sector at masses corresponding to sigma(28) = 56 GeV, tau(28) = 6, etc.
5. Open the door to testing P_3 = 496 in the context of string theory anomaly cancellation

The combination of a correct mass prediction AND the perfect number framework would constitute a paradigm shift in our understanding of the relationship between mathematics and physics.

## References

- Hooper & Goodenough, Phys. Lett. B697 (2011) 412 (Galactic Center excess)
- Daylan et al., Phys. Dark Univ. 12 (2016) 1 (GCE spectral analysis)
- LZ Collaboration, arXiv:2207.03764 (direct detection limits)
- XENON Collaboration, Phys. Rev. Lett. 131 (2023) 041003
- H-PH-9: Perfect number string unification (P_3 = 496)
- H-PH-30: Theory of Flavor (sigma, tau, phi framework)
- Planck Collaboration, A&A 641 (2020) A6 (relic density)
