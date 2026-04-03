# GZ Blowup Directions: Status and Priorities

**Date**: 2026-04-04
**Scope**: All results from GZ closure + blowup rounds 1-2

---

## EXHAUSTED (no more to extract)

| Direction | What was found | Why exhausted |
|-----------|---------------|---------------|
| Axiomatic closure | 4 routes, minimum 3 axioms, irreducibility proven | gz_final_tuning.md: cannot reduce below 3, all routes are Noether faces of one fact |
| GZ identities scan | width=ln(4/3), center=1/e, upper=1/2 | Exhaustive scan: width^2~1/12 is 0.69% off, no new exact identities exist |
| f(I) coefficient a=0.7 | No physics constant matches, no derivation possible | Confirmed empirical (like alpha~1/137). Lagrangian cannot fix it. Dead end. |
| SIR epidemic mapping | Form matches exactly, GZ constants do NOT | 1/15 accuracy. gamma is a rate not a fraction. Axiom violation kills predictions. |
| Noether/Lagrangian structure | 3 conserved quantities, 3 modes, Liouville integrable | Fully solved. Normal modes decomposed. Nothing left to decompose. |
| Thermodynamics mapping | W=Q*(1-I) not D*P/I | Linear penalty, not multiplicative. Structural mismatch, unfixable. |
| Shannon capacity | C=B*log(1/I) not D*P/I | Logarithmic vs hyperbolic. Entropy origin prevents exact match. |

## FERTILE (more discoveries possible)

| Direction | Current state | What remains |
|-----------|--------------|-------------|
| A2/SU(3) lattice | 10/10 invariants match, Theorems 13-21 | E8 embedding, theta functions, modular forms at level 3, physical SU(3) prediction |
| Quantum GZ | Ground state = single state in strip, hbar_lattice derived | Partition function, spectral zeta at Re(s)=1/2, non-flat Fisher metric curvature |
| Higher perfect numbers (n=28) | det=28/3 not integer, no lattice | Fractional lattice theory, compare all 10 theorems at n=28, find what BREAKS |
| Universality domain testing | 7 domains, 2 structural matches (SIR form, ML partial) | Digital economy Cobb-Douglas (alpha->1), cascade turbines, erasure channels |
| ML experimental verification | MoE k/N confirmed, dropout MNIST refuted | Dropout on CIFAR-100/ImageNet, Hessian trace measurement, scaling law test |
| Neuroscience predictions | 5 predictions, 0 tested | GABA fraction MRS study, anesthesia LOC threshold, cheapest: meta-analysis of existing dropout studies |

## UNTOUCHED (new directions never explored)

| Direction | Description | Entry point |
|-----------|------------|-------------|
| Spectral zeta of GZ strip | zeta_H(s) = sum lambda_m^{-s}. Special values at Re(s)=1/2? | Theorem 4 eigenvalues are explicit. Compute zeta, check Riemann line. |
| A2 theta function in GZ | Theta_A2(q) = 1+6q+6q^3+... Coefficients are n,sigma multiples. | Does this appear as the GZ partition function Z = Tr(e^{-beta H})? |
| Modular forms connection | A2 theta is weight-1 for Gamma_0(3). Level 3 = det(g_H). | Direct bridge to Riemann zeta via GZ upper boundary = 1/2. |
| Non-Gaussian Fisher metric | What if observation noise is non-Gaussian? H acquires curvature. | Does Ricci scalar encode n=6? This could be a new theorem. |
| Leech lattice bridge | sigma*phi = n*tau = 24 = dim(Leech). A2 is sublattice of E8. | Trace the A2 -> E8 -> Leech chain through n=6 arithmetic. |
| Renormalization group flow | GZ as a fixed point of RG flow on the space of models. | Does the spectral gap lambda_1=8.97 control the RG beta function? |
| Category theory deeper | G=D*P/I is initial object in C. What is the terminal object? | Adjoint functors, limits/colimits in the category of admissible functionals. |
| Stochastic GZ | Add noise to the Lagrangian: Langevin equation on H. | Fokker-Planck on the GZ strip. Stationary distribution peaked at 1/e? |
| Consciousness state counting | Theorem 17: N_GZ < 1 (single state). What if GZ widens? | Phase transition at L=1 (lattice spacing). What critical width triggers 2 states? |
| Information geometry (full) | Fisher rank=1 (Thm 6). Amari alpha-connections on H? | Dual connections, exponential/mixture families on the GZ manifold. |

---

## Prioritized TODO

| # | Priority | Direction | Impact | Effort | Status |
|---|----------|-----------|--------|--------|--------|
| 1 | *** | Spectral zeta at Re(s)=1/2 | Nobel-level if connects GZ to Riemann | Medium | Untouched |
| 2 | *** | A2 theta = GZ partition function | Unifies lattice geometry with quantum GZ | Medium | Untouched |
| 3 | *** | Modular forms Gamma_0(3) bridge | Direct number theory to GZ geometry | Hard | Untouched |
| 4 | ** | Non-Gaussian Fisher curvature | New theorem: Ricci scalar from n=6? | Medium | Untouched |
| 5 | ** | Leech lattice 24D chain | A2->E8->Leech through n=6 | Hard | Untouched |
| 6 | ** | ML dropout on hard tasks | Cheapest empirical test of entire model | Low | Partially done |
| 7 | ** | n=28 systematic comparison | What breaks = what's special about 6 | Medium | Noted in open questions |
| 8 | ** | Stochastic GZ / Fokker-Planck | Makes model testable in noisy systems | Medium | Untouched |
| 9 | * | RG flow interpretation | Connects GZ to statistical mechanics | Hard | Untouched |
| 10 | * | Consciousness state counting (L=1 transition) | Concrete prediction: critical width | Low | Untouched |
| 11 | * | Category theory terminal object | Mathematical completeness | Low | Untouched |
| 12 | * | Digital economy Cobb-Douglas test | Empirical universality evidence | Low | Noted |

Impact: *** = Nobel-level, ** = paper-level, * = nice-to-have

**Verdict**: The closure and internal geometry are done. The lattice/quantum/Noether
mechanics are done. What remains is the OUTWARD connections: to number theory (items 1-3),
to physics (4-5, 8-9), and to experiment (6, 12). The modular forms direction (1-3) is
the highest-value unexplored territory by far.
