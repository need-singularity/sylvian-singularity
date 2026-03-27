# G x I = D x P: A Conservation Law for Consciousness Parameters

**Authors:** TECS-L Project
**Date:** 2026-03-27
**Keywords:** consciousness model, conservation law, deficit, plasticity, inhibition, genius equation, parameter space, fixed points
**License:** CC-BY-4.0

## Abstract

We derive and analyze the conservation law G x I = D x P, where G (Genius) = D (Deficit) x P (Plasticity) / I (Inhibition). This identity, which follows directly from the defining equation, establishes a conserved quantity in the four-dimensional parameter space of the TECS-L consciousness model. We characterize the conservation surface, identify its fixed points, analyze the dynamics under the contraction mapping f(I) = 0.7I + 0.1 (which converges to I = 1/3), and show that the conservation law constrains trajectories to a 3-dimensional manifold within the 4D parameter space. The Golden Zone [0.2123, 0.5] for the inhibition parameter I corresponds to the region where the conservation quantity G x I takes values in the interval [D x P x 0.2123, D x P x 0.5], which we identify as the "productive regime" where high genius coexists with non-trivial inhibition.

## 1. Introduction

The TECS-L framework models cognitive capacity through four parameters:
- **D (Deficit):** Structural deviation from typical neural architecture (0 to 1)
- **P (Plasticity):** Capacity for neural reorganization and adaptation (0 to 1)
- **I (Inhibition):** Regulatory control that constrains and focuses processing (0 to 1)
- **G (Genius):** Emergent cognitive capacity, the output variable

The defining equation is:

```
G = D * P / I
```

This is a model (not a physical law) proposed to capture the observation that exceptional cognitive abilities often coexist with neurological differences (high D), neural flexibility (high P), and reduced inhibitory control (low I).

Rearranging: G * I = D * P. This is trivially true by definition, yet the conservation form reveals structure that is not obvious from the ratio form. In particular, it defines a constraint surface in (G, I, D, P) space that all valid states must lie on.

## 2. Methods / Framework

### 2.1 Conservation Surface

The equation G * I = D * P defines a 3-dimensional hypersurface in R^4. For fixed D and P, this is a hyperbola in the (G, I) plane:

```
G = (D * P) / I

For D=0.7, P=0.8 (high deficit, high plasticity):

  G
  6.0 |*
  5.0 | *
  4.0 |  *
  3.0 |   *
  2.0 |     *
  1.5 |       *      <- Golden Zone: I in [0.21, 0.50]
  1.0 |          *        G in [1.12, 2.67]
  0.5 |               *
  0.0 +--+--+--+--+--+--+--+--+--+--> I
      0  0.1 0.2 0.3 0.4 0.5 0.6 0.7 0.8
```

### 2.2 Conserved Quantity

Define Q = G * I = D * P. For any trajectory in (D, P, I) space that preserves Q:
- Increasing I (more inhibition) necessarily decreases G
- Increasing D or P increases Q, allowing higher G at the same I
- The "genius surface" Q = const is foliated by hyperbolas

### 2.3 Contraction Mapping Dynamics

The inhibition parameter evolves under the contraction mapping:

```
f(I) = 0.7 * I + 0.1
```

This is a contraction on [0, 1] with Lipschitz constant 0.7 < 1. By the Banach fixed point theorem, it has a unique fixed point:

```
I* = 0.7 * I* + 0.1
0.3 * I* = 0.1
I* = 1/3
```

The convergence is geometric:

| Iteration | I_n | G (for D*P=0.56) |
|---|---|---|
| 0 | 0.00 (start) | undefined |
| 1 | 0.10 | 5.60 |
| 2 | 0.17 | 3.29 |
| 3 | 0.22 | 2.55 |
| 4 | 0.25 | 2.24 |
| 5 | 0.28 | 2.00 |
| 10 | 0.32 | 1.75 |
| infinity | 0.333 | 1.68 |

### 2.4 Golden Zone Analysis

The Golden Zone I in [0.2123, 0.5] intersects the conservation surface:

```
G_max (at I = 0.2123) = Q / 0.2123 = 4.71 * Q
G_min (at I = 0.5)    = Q / 0.5    = 2.00 * Q
G_center (at I = 1/e) = Q / 0.3679 = 2.72 * Q = e * Q
```

The center of the Golden Zone gives G = e * Q, connecting the genius level to Euler's number.

### 2.5 Relation to 1/2 + 1/3 + 1/6 = 1

The three critical I values decompose the unit interval:

```
I = 1/2:   Upper Golden Zone boundary.  G = 2Q (moderate genius)
I = 1/3:   Contraction fixed point.     G = 3Q (high genius)
I = 1/6:   Curiosity parameter.         G = 6Q (extreme genius)

1/2 + 1/3 + 1/6 = 1  (completeness identity)
```

At I = 1/6, G = 6Q = 6 * D * P. For D = P = 1 (maximum deficit and plasticity), G = 6 = the first perfect number. This is the theoretical maximum genius under the completeness constraint.

## 3. Results

### 3.1 Parameter Space Structure

The conservation law partitions the (D, P, I) unit cube into level sets of Q = D * P:

```
Level sets of Q = D*P in the (D, P) plane:

  P
  1.0 |* * * * * * * * * *
  0.8 |  * * * * * * * *     Q = 0.56
  0.6 |    * * * * * *       Q = 0.36
  0.4 |      * * * *         Q = 0.16
  0.2 |        * *           Q = 0.04
  0.0 +--+--+--+--+--+---> D
      0  0.2 0.4 0.6 0.8 1.0
```

Each level set maps to a unique hyperbola in the (G, I) plane. Higher Q (more deficit x plasticity) shifts the hyperbola upward, yielding higher genius at every inhibition level.

### 3.2 Brain Profile Examples

| Profile | D | P | I | Q = D*P | G = Q/I | Zone |
|---|---|---|---|---|---|---|
| Typical | 0.3 | 0.5 | 0.5 | 0.15 | 0.30 | Upper boundary |
| ADHD | 0.7 | 0.8 | 0.2 | 0.56 | 2.80 | Lower Golden Zone |
| Savant | 0.9 | 0.6 | 0.15 | 0.54 | 3.60 | Below Golden Zone |
| Balanced genius | 0.6 | 0.7 | 0.33 | 0.42 | 1.27 | Fixed point |
| Suppressed | 0.7 | 0.8 | 0.8 | 0.56 | 0.70 | Above Golden Zone |

### 3.3 Trajectory Under Contraction

Starting from I_0 = 0.15 (savant, low inhibition), the contraction mapping drives the system toward I* = 1/3:

```
Trajectory in (I, G) space:

  G
  4.0 | * (start: savant)
  3.0 |   *
  2.5 |     *
  2.0 |       *
  1.7 |         * * * (converging to fixed point)
  1.5 |
      +--+--+--+--+--+--+--+--> I
      0.1 0.15 0.2 0.25 0.3 0.35
```

The trajectory moves rightward and downward along the conservation hyperbola, trading extreme genius for increased inhibitory control. This models developmental trajectories where initially uninhibited savant abilities become more controlled (and somewhat reduced) with maturity.

### 3.4 Dimensional Analysis

The conservation law G * I = D * P has consistent dimensions if all four parameters are dimensionless ratios (as defined). The equation is scale-invariant: multiplying all parameters by a constant c gives (cG)(cI) = (cD)(cP), which requires c^2 = c^2.

If we assign physical dimensions:
- [D] = [P] = "capacity" (dimensionless, 0 to 1)
- [I] = "regulation" (dimensionless, 0 to 1)
- [G] = "output" = [capacity]^2 / [regulation]

The conservation form says: output x regulation = capacity^2. This is analogous to energy conservation (kinetic x potential = constant on certain trajectories).

## 4. Discussion

The G * I = D * P conservation law, while definitional rather than empirical, provides a useful framework for understanding trade-offs in the consciousness parameter space. The key insights are:

1. **Genius and inhibition are inversely coupled** on each conservation surface. You cannot increase one without decreasing the other, unless deficit or plasticity also change.

2. **The contraction mapping converges to I = 1/3**, which lies inside the Golden Zone. This suggests that natural developmental dynamics drive inhibition toward a specific equilibrium, not toward zero (uninhibited) or one (fully inhibited).

3. **The Golden Zone center at I = 1/e gives G = eQ**, connecting the genius level to the natural exponential. This is a consequence of 1/e being the center of [0.2123, 0.5], which is itself derived from the Riemann critical line and entropy considerations.

4. **The completeness identity 1/2 + 1/3 + 1/6 = 1** maps to three distinct genius regimes: moderate (I=1/2), high (I=1/3), and extreme (I=1/6).

The model is explicitly presented as a framework, not as an empirically validated theory. The parameters D, P, and I lack operational definitions that would allow direct measurement. The value of the conservation law is conceptual: it structures the space of possible cognitive profiles and identifies constraints that any profile must satisfy.

Limitations: (1) The model assumes independence of D and P, which is unlikely in biological systems (high deficit may impair plasticity). (2) The linear contraction mapping f(I) = 0.7I + 0.1 is assumed without empirical justification. (3) The Golden Zone boundaries are derived from the TECS-L constant system, which is itself unverified (see CLAUDE.md verification status).

## 5. Conclusion

The conservation law G * I = D * P, derived from the TECS-L genius equation G = D * P / I, constrains consciousness parameters to a 3-dimensional manifold. The contraction mapping on I converges to the fixed point I* = 1/3, which lies within the Golden Zone [0.2123, 0.5]. At the Golden Zone center I = 1/e, the genius level equals e times the deficit-plasticity product. The three critical inhibition values (1/2, 1/3, 1/6) satisfy the completeness identity and define three distinct cognitive regimes. While the model remains a conceptual framework rather than an empirical theory, the conservation structure provides clear predictions about parameter trade-offs that could be tested with operational definitions of the four parameters.

## References

1. Banach, S. (1922). Sur les operations dans les ensembles abstraits et leur application aux equations integrales. Fundamenta Mathematicae 3.
2. Langton, C.G. (1990). Computation at the Edge of Chaos. Physica D 42(1-3).
3. Tononi, G. (2004). An Information Integration Theory of Consciousness. BMC Neuroscience 5, 42.
4. Dehaene, S. & Changeux, J.P. (2011). Experimental and Theoretical Approaches to Conscious Processing. Neuron 70(2).
5. TECS-L Project. (2026). Core Constant System and Golden Zone. CLAUDE.md.
6. TECS-L Project. (2026). Brain Singularity Analysis. brain_singularity.py.
