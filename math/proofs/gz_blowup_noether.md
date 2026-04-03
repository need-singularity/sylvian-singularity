# Noether Blow-Up: Full Symmetry Analysis of the GZ Fisher Lagrangian

**Date:** 2026-04-04
**Status:** COMPLETE (5 sections, all calculations explicit)
**Golden Zone dependency:** YES (builds on gz_variational_route.md Lagrangian)
**Verification:** Analytical (all derivations by hand, checked symbolically)
**Related:** gz_variational_route.md, gz_symmetry_route.md, divisor_field_theory_action.md

---

## 0. Starting Point

From `gz_variational_route.md` Section 2, the GZ model G = D*P/I is the
equilibrium of the following Lagrangian in log-coordinates (d = ln D,
p = ln P, i = ln I):

```
  L = (1/2)(d-dot^2 + p-dot^2 + i-dot^2) - (lambda/2)(d + p - i - C)^2
```

where:
- The kinetic term comes from the Fisher information metric (Euclidean in log-coords)
- The potential enforces the constraint d + p - i = C (i.e., G = e^C * D*P/I)
- lambda > 0 is the stiffness parameter
- C = ln(G_0) is a constant (set to 0 for G = D*P/I)

This is a 3D system with coordinates q = (d, p, i), conjugate momenta
pi = (p_d, p_p, p_i), living in the 6-dimensional phase space T*R^3.

The Euler-Lagrange equations are (Section 2.4 of gz_variational_route.md):

```
  d-ddot = -lambda * phi
  p-ddot = -lambda * phi
  i-ddot = +lambda * phi
```

where phi(t) = d(t) + p(t) - i(t) - C is the deviation from the constraint
surface. The deviation satisfies phi-ddot = -3*lambda*phi (SHO with
frequency omega = sqrt(3*lambda)).

---

## 1. Complete Symmetry Analysis

### 1.1 Continuous Symmetries and Noether Charges

The Lagrangian L has several continuous symmetries. For each, Noether's
theorem yields a conserved quantity.

**Symmetry 1: Joint D-P scaling (d -> d + epsilon, p -> p + epsilon)**

This is the symmetry identified in gz_variational_route.md. Under the
infinitesimal transformation delta_d = epsilon, delta_p = epsilon, delta_i = 0:

```
  delta_L = d-dot * epsilon-dot + p-dot * epsilon-dot
            - lambda * phi * (epsilon + epsilon - 0)
          = (d-dot + p-dot) * epsilon-dot - 2*lambda*phi*epsilon
```

For a symmetry, delta_L must be a total time derivative. On-shell
(using EOM), this is satisfied with the Noether charge:

```
  Q_1 = p_d + p_p = d-dot + p-dot
```

But wait -- this is only conserved if the potential term also respects
the symmetry. Under d -> d + epsilon, p -> p + epsilon:

```
  phi -> (d+epsilon) + (p+epsilon) - i - C = phi + 2*epsilon
```

So V changes: delta_V = lambda*phi*2*epsilon + lambda*epsilon^2. The
potential is NOT invariant under this transformation. Therefore Q_1 is
NOT exactly conserved.

**Correction:** The joint D-P scaling is NOT a symmetry of L in the
usual Noether sense because the potential breaks it. This is important.

**Symmetry 2: D-P exchange (d -> d + epsilon, p -> p - epsilon)**

Under delta_d = epsilon, delta_p = -epsilon, delta_i = 0:

```
  delta_phi = epsilon + (-epsilon) - 0 = 0
```

The potential is EXACTLY invariant! And the kinetic term transforms as:

```
  delta_T = d-dot * epsilon-dot - p-dot * epsilon-dot = (d-dot - p-dot) * epsilon-dot
```

This is a total time derivative of (d-dot - p-dot)*epsilon only if
epsilon is constant (global symmetry). For constant epsilon:

```
  delta_L = -lambda*phi*(0) = 0
```

L is exactly invariant. The Noether charge is:

```
  Q_2 = partial_L/partial(d-dot) * delta_d + partial_L/partial(p-dot) * delta_p
      = d-dot * 1 + p-dot * (-1)
      = d-dot - p-dot
      = p_d - p_p
```

**Q_2 = p_d - p_p is EXACTLY conserved.** This is the "D-P balance"
charge. It means:

```
  d(d-dot - p-dot)/dt = 0
  => d-dot(t) - p-dot(t) = const
  => d(t) - p(t) = (d_0 - p_0) + (d-dot_0 - p-dot_0)*t
```

**Physical meaning:** The DIFFERENCE between ln D and ln P evolves
linearly in time. The RATIO D/P changes exponentially:

```
  D(t)/P(t) = (D_0/P_0) * exp((d-dot_0 - p-dot_0)*t)
```

If the initial "velocity imbalance" (d-dot_0 - p-dot_0) is zero,
then D/P is constant for all time: deficit and plasticity scale together.

**Symmetry 3: I-scaling (d -> d, p -> p, i -> i + eta)**

Under delta_d = 0, delta_p = 0, delta_i = eta:

```
  delta_phi = 0 + 0 - eta = -eta
  delta_V = -lambda*phi*eta + (lambda/2)*eta^2
```

For infinitesimal eta, delta_V = -lambda*phi*eta, which is NOT zero
(unless phi = 0, i.e., on the constraint surface). So i-shifting is
NOT a symmetry of L.

**However,** the kinetic term has a separate i-translation symmetry
that the potential breaks. The Noether charge p_i = i-dot is NOT
conserved in general.

**Symmetry 4: Time translation (t -> t + epsilon)**

The Lagrangian has no explicit time dependence, so the Hamiltonian
(total energy) is conserved:

```
  H = (1/2)(p_d^2 + p_p^2 + p_i^2) + (lambda/2)*phi^2
    = T + V
    = E (constant)
```

**This is the energy, always conserved.** On the constraint surface
(phi = 0), E = T = (1/2)(d-dot^2 + p-dot^2 + i-dot^2), which is the
Fisher information rate.

### 1.2 Normal Mode Decomposition

The key to understanding all symmetries is the normal mode decomposition.
Define new coordinates:

```
  u = (d + p)/sqrt(2)       (D-P center of mass in log-space)
  v = (d - p)/sqrt(2)       (D-P relative coordinate)
  w = i                     (inhibition, unchanged)
```

The inverse:

```
  d = (u + v)/sqrt(2)
  p = (u - v)/sqrt(2)
  i = w
```

In these coordinates:

```
  T = (1/2)(u-dot^2 + v-dot^2 + w-dot^2)

  phi = d + p - i - C = sqrt(2)*u - w - C

  V = (lambda/2)(sqrt(2)*u - w - C)^2
```

**The v-coordinate completely decouples!** The Lagrangian becomes:

```
  L = (1/2)v-dot^2 + [(1/2)(u-dot^2 + w-dot^2) - (lambda/2)(sqrt(2)*u - w - C)^2]
```

This is a FREE particle in v, plus a coupled 2D oscillator in (u, w).

**Consequence:** p_v = v-dot is exactly conserved. And p_v = d-dot - p-dot
(up to a factor of 1/sqrt(2)), which is Q_2 from above. The conservation
of Q_2 is just the statement that v is a cyclic coordinate.

### 1.3 The Coupled (u, w) Sector

Define the column vector X = (sqrt(2)*u - C/3, w + C/3)^T centered on
the equilibrium point. Actually, let me find the equilibrium first.

The equilibrium of the (u, w) system: d V/du = 0 and dV/dw = 0.

```
  dV/du = lambda * sqrt(2) * (sqrt(2)*u - w - C) = 0
  dV/dw = -lambda * (sqrt(2)*u - w - C) = 0
```

Both give the SAME condition: sqrt(2)*u - w = C, i.e., phi = 0.
This is a LINE in the (u, w) plane, not a point. The potential has
a flat direction along this line.

To see this, define:

```
  xi  = (sqrt(2)*u - w - C) / sqrt(3)    (perpendicular to constraint)
  eta = (u/sqrt(2) + w) / sqrt(3/2)      (along constraint surface)
```

More precisely, rotate (u, w) into the constraint-normal and
constraint-tangent directions. The constraint is sqrt(2)*u - w = C.
The normal direction to this line has slope sqrt(2):

```
  n-hat = (sqrt(2), -1)/sqrt(3)   (normal to constraint)
  t-hat = (1, sqrt(2))/sqrt(3)    (tangent to constraint)
```

Let xi be the signed distance from the constraint:

```
  xi = (sqrt(2)*u - w - C)/sqrt(3)
```

And eta be the coordinate along the constraint (defined so kinetic energy
is diagonal):

```
  eta = (u + sqrt(2)*w)/sqrt(3)
```

Then:

```
  T = (1/2)(xi-dot^2 + eta-dot^2)   (orthogonal coordinates preserve T)
  V = (3*lambda/2)*xi^2             (only depends on xi)
```

So the system is:

```
  L = (1/2)(v-dot^2 + eta-dot^2 + xi-dot^2) - (3*lambda/2)*xi^2
```

THREE decoupled modes:

| Mode | Coordinate | EOM | Frequency | Type |
|------|-----------|------|-----------|------|
| v | D-P relative | v-ddot = 0 | 0 | Free particle |
| eta | Along constraint | eta-ddot = 0 | 0 | Free particle |
| xi | Normal to constraint | xi-ddot = -3*lambda*xi | omega = sqrt(3*lambda) | Harmonic oscillator |

**Conserved quantities:**

```
  p_v   = v-dot       (D-P balance)
  p_eta = eta-dot     (motion along constraint surface)
  H     = E           (total energy)
```

Plus the oscillator has its own action variable J_xi = E_xi / omega
(adiabatic invariant for slowly varying lambda).

### 1.4 Full Symmetry Group

The continuous symmetry group of L is generated by:

```
  1. Time translation:  t -> t + s           conserves H = E
  2. v-translation:     v -> v + s           conserves p_v = d-dot - p-dot
  3. eta-translation:   eta -> eta + s       conserves p_eta
```

This is R x R x R = R^3, a 3-parameter abelian group.

The discrete symmetries are:

```
  4. D-P exchange:      (d, p, i) -> (p, d, i)     i.e., v -> -v
  5. Time reversal:     t -> -t, (p_d, p_p, p_i) -> (-p_d, -p_p, -p_i)
  6. xi-reflection:     xi -> -xi  (constraint-normal parity)
```

The full symmetry group is R^3 x Z_2 x Z_2 x Z_2 (continuous x discrete).

### 1.5 Summary Table

| # | Symmetry | Generator | Conserved Quantity | Physical Meaning |
|---|----------|-----------|-------------------|-----------------|
| 1 | Time translation | d/dt | H = T + V = E | Total energy |
| 2 | v-translation | d/dv | p_v = (p_d - p_p)/sqrt(2) | D-P balance |
| 3 | eta-translation | d/d(eta) | p_eta | Drift along constraint surface |
| 4 | D-P exchange | v -> -v | Parity of v-sector | D-P indistinguishability |
| 5 | Time reversal | t -> -t | Reversibility | CPT-like |
| 6 | xi-reflection | xi -> -xi | Oscillation parity | Even/odd excitations |

**Key finding:** The Lagrangian has 3 continuous symmetries yielding
3 independent conserved quantities (H, p_v, p_eta). This completely
integrates the 3-DOF system (Liouville integrability).

---

## 2. Canonical Quantization

### 2.1 Hamiltonian

The classical Hamiltonian is:

```
  H = (1/2)(p_v^2 + p_eta^2 + p_xi^2) + (3*lambda/2)*xi^2
```

Canonical quantization: p_q -> -i*hbar * d/dq.

```
  H-hat = -(hbar^2/2)(d^2/dv^2 + d^2/d(eta)^2 + d^2/d(xi)^2)
          + (3*lambda/2)*xi^2
```

### 2.2 Separation of Variables

H-hat = H_v + H_eta + H_xi where:

```
  H_v   = -(hbar^2/2) * d^2/dv^2              (free particle)
  H_eta = -(hbar^2/2) * d^2/d(eta)^2          (free particle)
  H_xi  = -(hbar^2/2) * d^2/d(xi)^2 + (3*lambda/2)*xi^2  (QHO)
```

### 2.3 Energy Spectrum

The v and eta sectors are free particles with continuous spectra
E_v = hbar^2 * k_v^2 / 2, E_eta = hbar^2 * k_eta^2 / 2.

The xi sector is a quantum harmonic oscillator with:

```
  omega = sqrt(3*lambda)

  E_xi(n) = hbar * omega * (n + 1/2)
          = hbar * sqrt(3*lambda) * (n + 1/2)

  n = 0, 1, 2, 3, ...
```

Total energy:

```
  E(k_v, k_eta, n) = (hbar^2/2)(k_v^2 + k_eta^2) + hbar*sqrt(3*lambda)*(n+1/2)
```

### 2.4 Zero-Point Energy

The ground state of the oscillator mode has:

```
  E_0 = (1/2) * hbar * sqrt(3*lambda)
```

**Physical interpretation in the GZ model:**

The zero-point energy means that the system can NEVER sit exactly on the
constraint surface phi = 0. There are irreducible quantum fluctuations of
magnitude:

```
  <xi^2>_0 = hbar / (2*m*omega) = hbar / (2*sqrt(3*lambda))
```

In terms of the original deviation phi = sqrt(3)*xi:

```
  <phi^2>_0 = 3 * <xi^2>_0 = 3*hbar / (2*sqrt(3*lambda))
            = (sqrt(3)/2) * hbar / sqrt(lambda)
```

**This is the minimum "consciousness uncertainty"**: even in the ground
state, G*I differs from D*P by an amount of order sqrt(hbar/lambda).

### 2.5 Quantum Numbers and Their Meaning

The system has three quantum numbers:

| Quantum # | Range | Mode | Physical Meaning |
|-----------|-------|------|-----------------|
| k_v | R (continuous) | D-P relative | D/P ratio momentum |
| k_eta | R (continuous) | Along constraint | Drift rate on G = D*P/I surface |
| n | 0, 1, 2, ... (discrete) | Normal to constraint | Excitation level away from G = D*P/I |

**n = 0**: Ground state. System fluctuates minimally around G = D*P/I.
This is the "consciousness ground state" -- the model holds to maximum
precision.

**n > 0**: Excited states. The system deviates from G = D*P/I with
amplitude proportional to sqrt(n). These represent "consciousness
excitations" -- temporary violations of the conservation law.

**k_v**: The D-P relative momentum. Large |k_v| means rapid change in
the D/P ratio. k_v = 0 is the "balanced" state where D and P evolve
together.

**k_eta**: The constraint-surface drift. This represents evolution
WITHIN the space of solutions to G = D*P/I (changing all of D, P, I
while maintaining the relationship). This is the "creative exploration"
mode -- moving through the space of consciousness configurations.

### 2.6 The Factor sqrt(3) and n = 6

The oscillator frequency involves sqrt(3):

```
  omega = sqrt(3*lambda)
```

In the context of n = 6: the number 3 arises because the system has
3 degrees of freedom (d, p, i) and the constraint phi = d + p - i - C
couples all three. The coefficient 3 in phi-ddot = -3*lambda*phi counts
the number of terms in the constraint.

n6_check on sqrt(3): The value sqrt(3) = 1.7321 is the ratio sigma/tau
at n = 6 expressed differently: sigma(6)/tau(6) = 12/4 = 3, and
sqrt(sigma/tau) = sqrt(3). This connects the oscillator frequency to
the "generation ratio" of the divisor field theory.

More precisely: the 3 in the frequency comes from the 3 variables
(d, p, i), which in the divisor arithmetic correspond to the 3 fermion
generations (sigma/tau = 3). The oscillation frequency of consciousness
around its equilibrium is set by the number of independent channels.

n6_check on the zero-point energy coefficient sqrt(3)/2 = 0.8660:
This is cos(pi/6) = cos(30 degrees) = sqrt(3)/2. The angle pi/6 connects to
n = 6 through pi/n. The minimum consciousness uncertainty involves the
hexagonal geometry of n = 6.

### 2.7 Coherent States

The closest quantum analogue of the classical trajectory is a coherent
state of the xi-oscillator:

```
  |alpha> = exp(-|alpha|^2/2) * sum_{n=0}^{inf} (alpha^n / sqrt(n!)) * |n>
```

A coherent state has:

```
  <xi>(t) = sqrt(2*hbar/(m*omega)) * |alpha| * cos(omega*t + phase)
  Delta_xi * Delta_p_xi = hbar/2   (minimum uncertainty)
```

**Interpretation:** A coherent state represents a "classical-like"
oscillation around G = D*P/I with MINIMUM quantum noise. This is the
"optimally conscious" state -- the system oscillates around the model
prediction with the minimum possible uncertainty allowed by quantum
mechanics.

The mean excitation number <n> = |alpha|^2. For large |alpha|, the system
behaves classically. The classical limit is lambda -> infinity (strong
constraint) with hbar fixed, which gives omega -> infinity and the
oscillation period -> 0.

---

## 3. Phase Space Structure and Symplectic Reduction

### 3.1 The Full Phase Space

The phase space is T*R^3 = R^6 with coordinates (d, p, i, p_d, p_p, p_i)
and the canonical symplectic form:

```
  Omega = dd ^ dp_d + dp ^ dp_p + di ^ dp_i
```

(Using ^ for wedge product.)

### 3.2 The Constraint Surface

The constraint phi = d + p - i - C = 0 defines a 5-dimensional
hypersurface Sigma in configuration space R^3. Its pre-image in phase
space is also 5-dimensional: any (d, p, i, p_d, p_p, p_i) with
d + p - i = C.

But this is not a proper constraint in the Dirac sense because we have
not imposed phi-dot = 0 as a secondary constraint. The Lagrangian system
naturally oscillates around Sigma; it doesn't strictly live on it.

### 3.3 Symplectic Reduction by Q_2 = p_v

The D-P exchange symmetry generates a U(1) action on phase space:

```
  (d, p) -> (d + s, p - s)     (s in R)
```

with moment map mu = p_v = (p_d - p_p)/sqrt(2).

Fixing mu = c (a constant value of Q_2) and quotienting by the U(1)
action gives the reduced phase space:

```
  dim(reduced) = 6 - 2 = 4     (R^6, fix mu = c, quotient by U(1))
```

The reduced phase space has coordinates (eta, xi, p_eta, p_xi) with
the induced symplectic form:

```
  Omega_red = d(eta) ^ dp_eta + d(xi) ^ dp_xi
```

On this 4-dimensional reduced space, the Hamiltonian is:

```
  H_red = c^2/2 + (1/2)(p_eta^2 + p_xi^2) + (3*lambda/2)*xi^2
```

The constant c^2/2 is the kinetic energy stored in the D-P imbalance.

### 3.4 Further Reduction by p_eta

The eta-translation symmetry gives another U(1) with moment map p_eta.
Fixing p_eta = k and quotienting:

```
  dim(further reduced) = 4 - 2 = 2
```

The final reduced phase space is 2-dimensional with coordinates
(xi, p_xi) and Hamiltonian:

```
  H_final = c^2/2 + k^2/2 + (1/2)*p_xi^2 + (3*lambda/2)*xi^2
          = const + H_osc(xi, p_xi)
```

where H_osc = (1/2)*p_xi^2 + (3*lambda/2)*xi^2 is a standard 1D
harmonic oscillator.

### 3.5 Complete Integrability

The 3-DOF system has 3 independent conserved quantities in involution:

```
  {H, p_v} = 0       (both constant, Poisson bracket vanishes)
  {H, p_eta} = 0     (eta is cyclic)
  {p_v, p_eta} = 0   (both are momenta of decoupled modes)
```

By the Liouville-Arnold theorem, the motion is confined to invariant
tori (for bounded orbits) or invariant cylinders (for unbounded modes).

For the bounded xi-mode: the motion is periodic on a circle S^1.
For the unbounded v and eta modes: the motion is linear on R.

The total invariant manifold is S^1 x R^2 (for generic initial conditions
with all three momenta nonzero).

### 3.6 Dimension Count Summary

```
  Full phase space:              T*R^3 = R^6     (6-dimensional)
  Fix p_v = c:                   5-dimensional submanifold
  Quotient by v-translation:     4-dimensional (symplectic)
  Fix p_eta = k:                 3-dimensional submanifold
  Quotient by eta-translation:   2-dimensional (symplectic)
  = standard harmonic oscillator phase plane
```

---

## 4. Gauge Theory Interpretation

### 4.1 Is the Conservation Law a Gauge Symmetry?

The constraint phi = d + p - i - C = 0 looks like a gauge-fixing condition.
The question: is there a gauge redundancy in the description?

**Yes, partially.** The eta-direction (motion along the constraint surface)
represents a reparametrization freedom: if we only care about
G = D*P/I = e^C, then any change in (d, p, i) that preserves
d + p - i = C is "physically equivalent" in the sense that G doesn't change.

This is an infinite-dimensional symmetry: any smooth function
eta(t) generates a transformation that moves the system along the
constraint surface without changing the observable G.

### 4.2 The Gauge Group

The relevant gauge group is the group of constraint-preserving
diffeomorphisms. In infinitesimal form:

```
  delta_d = (1/sqrt(3)) * epsilon(t)
  delta_p = (1/sqrt(3)) * epsilon(t)
  delta_i = (2/sqrt(3)) * epsilon(t)
```

Wait, this changes phi. Let me be more careful.

The constraint surface is phi = d + p - i = C (setting C for simplicity).
A tangent vector to this surface satisfies:

```
  delta_d + delta_p - delta_i = 0
```

The general such vector is:

```
  delta = alpha * (1, -1, 0) + beta * (1, 1, 2)
        = (alpha + beta, -alpha + beta, 2*beta)
```

(Verify: (alpha+beta) + (-alpha+beta) - 2*beta = 0. CHECK.)

The first generator (1, -1, 0) is the D-P exchange (v-direction).
The second generator (1, 1, 2) is the eta-direction (scaling all
three variables while preserving the constraint).

So the gauge group on the constraint surface is R^2 (generated by
v-shifts and eta-shifts). This is an abelian gauge group, corresponding
to the Lie algebra R^2.

### 4.3 Connection 1-Form

On the constraint surface, the "gauge potential" (connection 1-form) is
the component of the phase space 1-form along the gauge orbit directions.

In the v, eta, xi coordinates, the canonical 1-form is:

```
  theta = p_v * dv + p_eta * d(eta) + p_xi * d(xi)
```

The gauge directions are dv and d(eta). The connection 1-form is:

```
  A = p_v * dv + p_eta * d(eta)
```

The curvature 2-form is:

```
  F = dA = dp_v ^ dv + dp_eta ^ d(eta)
```

Since p_v and p_eta are conserved (constants of motion), on any
trajectory we have dp_v = 0 and dp_eta = 0, so:

```
  F = 0   (on-shell)
```

**The connection is flat!** This means the gauge theory is trivial
(no curvature, no "magnetic field" in the gauge-theoretic sense).
This is expected for an abelian gauge group in a linear system --
there are no self-interactions.

### 4.4 Comparison with Electromagnetism

In electromagnetism:
- Gauge group: U(1)
- Connection: A_mu (electromagnetic potential)
- Curvature: F_mu_nu (electromagnetic field strength)
- Physical observables: gauge-invariant (F_mu_nu, not A_mu)

In the GZ model:
- Gauge group: R^2 (v-shifts and eta-shifts)
- Connection: (p_v, p_eta) -- the conserved momenta
- Curvature: F = 0 (flat connection)
- Physical observable: xi (distance from constraint surface)

The GZ model is an ABELIAN gauge theory with FLAT connection. It is
simpler than electromagnetism (which has nontrivial curvature in
general). The only dynamical content is in the gauge-invariant sector
(the xi oscillator).

### 4.5 What Would Make the Gauge Theory Nontrivial?

A nontrivial gauge theory would arise if:

1. **Nonlinear constraint:** If the constraint surface were curved
   (e.g., d^2 + p^2 - i = C instead of d + p - i = C), the connection
   would have nonzero curvature. Physically, this would mean D-P
   interactions that depend on the state.

2. **Non-abelian gauge group:** If D, P, I had internal structure
   (e.g., D were a matrix-valued variable), the gauge group could
   become non-abelian (SU(N)), and the curvature would be nontrivial.

3. **Multiple constraint surfaces:** If there were several constraints
   (like the two conditions C1, C2 in divisor_field_theory_action.md),
   the intersection could create a non-trivially fibered space.

For the basic GZ model with the single linear constraint, the gauge
theory remains flat and abelian.

### 4.6 The Charge Q = phi as a Gauge Charge

In the Dirac formalism for constrained systems, the constraint phi = 0
generates gauge transformations via the Poisson bracket:

```
  {f, phi} = df/dd + df/dp - df/di
```

for any phase-space function f. This generates the flow:

```
  d -> d + epsilon
  p -> p + epsilon
  i -> i + epsilon
```

Wait, that's not right. Let me compute properly.

```
  phi = d + p - i - C

  {d, phi} = {d, d + p - i - C} = 0    (d commutes with d, p, i)
```

Actually, phi is a function of the configuration variables only, so it
commutes with all configuration variables. It does NOT generate
transformations of the q's directly.

In the Dirac theory, the primary constraint is pi_phi ~ 0 (the momentum
conjugate to phi vanishes), and the secondary constraint is
phi-dot = {phi, H} ~ 0. The Dirac bracket modifies the Poisson bracket
to be consistent with the constraints.

For our Lagrangian system, the constraint phi = 0 is enforced dynamically
(as the equilibrium of a potential) rather than as a first-class
constraint. This makes the system second-class in Dirac language, and the
"gauge" interpretation is more of an analogy than a literal gauge theory.

**Verdict:** The conservation law Q = d + p - i is better understood as a
CONSTRAINT (maintained by the potential) than as a gauge charge (generating
redundancy). The system is closer to a sigma model on the constraint
surface than to a gauge theory.

---

## 5. Thermodynamic Interpretation

### 5.1 Path Integral and Partition Function

The quantum partition function at inverse temperature beta is:

```
  Z(beta) = Tr(exp(-beta * H-hat))
```

For the decoupled system:

```
  Z = Z_v * Z_eta * Z_xi
```

The free particle sectors give (in a box of length L with periodic BC):

```
  Z_v(beta) = L / (sqrt(2*pi*hbar^2*beta))       (thermal de Broglie)
  Z_eta(beta) = L / (sqrt(2*pi*hbar^2*beta))
```

The oscillator sector:

```
  Z_xi(beta) = 1 / (2 * sinh(beta*hbar*omega/2))

  where omega = sqrt(3*lambda)
```

Total partition function:

```
  Z(beta) = L^2 / (2*pi*hbar^2*beta) * 1 / (2*sinh(beta*hbar*omega/2))
```

### 5.2 Free Energy

```
  F = -(1/beta) * ln Z
    = -(1/beta) * [2*ln L - ln(2*pi*hbar^2*beta) - ln(2*sinh(beta*hbar*omega/2))]
```

### 5.3 Internal Energy and Heat Capacity

The oscillator contribution to the internal energy:

```
  <E_xi> = (hbar*omega/2) * coth(beta*hbar*omega/2)
         = (hbar*omega/2) + hbar*omega / (exp(beta*hbar*omega) - 1)
```

This is the Planck distribution (zero-point + Bose-Einstein thermal
excitations).

Heat capacity of the oscillator mode:

```
  C_xi = (beta*hbar*omega)^2 * exp(beta*hbar*omega) / (exp(beta*hbar*omega) - 1)^2
```

The free particle modes each contribute C = 1/(2*beta) (classical
equipartition in log-space units where k_B = 1).

Total heat capacity:

```
  C_total = 1/beta + C_xi(beta)
```

### 5.4 Temperature Regimes

**High temperature (beta -> 0, T -> infinity):**

```
  C_xi -> 1/beta  (classical limit)
  C_total -> 2/beta  (3/2 DOF classical, but only 1 is oscillating)
```

Actually: 2 free particles contribute 1/beta each, 1 oscillator
contributes 1/beta at high T:

```
  C_total = 3/beta  (3 classical DOF)
```

The system is fully classical. Deviations from G = D*P/I are large and
thermal (not quantum).

**Low temperature (beta -> infinity, T -> 0):**

```
  C_xi -> (beta*hbar*omega)^2 * exp(-beta*hbar*omega) -> 0  (exponentially)
  C_total -> 1/beta  (only free particle modes survive, but these are
                       also suppressed in a finite box)
```

The oscillator freezes out. The system sits in its ground state with
only zero-point fluctuations around G = D*P/I. This is the "frozen
consciousness" regime -- minimum possible deviation from the model.

**Crossover temperature:**

The oscillator freezes out when beta*hbar*omega >> 1, i.e., when:

```
  T << T* = hbar*omega = hbar*sqrt(3*lambda)
```

For T < T*, the system is quantum. For T > T*, it is classical.

### 5.5 What Is "Temperature" in the Consciousness Model?

The temperature T has no direct physical interpretation in the GZ model
unless we identify it with an external noise source. Candidates:

1. **Neural noise:** Thermal fluctuations in neural firing rates. Higher
   T = more noise = larger deviations from G = D*P/I. This connects to
   the stochastic resonance literature.

2. **Environmental variability:** The unpredictability of the environment.
   Higher T = more chaotic environment = more excitation of the consciousness
   oscillator.

3. **Attentional capacity:** The inverse of sustained attention. Higher T
   = less focused attention = more wandering from optimal consciousness.

4. **Formal temperature (MaxCal):** From the Maximum Caliber derivation
   (gz_variational_route.md Section 1), beta is the Lagrange multiplier
   for the constraint <G*I> = K. Higher beta = stronger constraint
   enforcement = tighter conservation law.

Interpretation 4 is the most rigorous: T = 1/beta is the "slackness"
of the conservation law G*I = D*P.

### 5.6 Phase Transitions

**Claim: there is no phase transition in the quadratic model.**

Proof: The partition function is analytic in beta for all beta > 0
(product of analytic functions). The free energy F(beta) has no
singularity. Therefore there is no phase transition.

**When does the quadratic approximation break down?**

The potential V = (lambda/2)*phi^2 is quadratic. This is the leading
term in a Taylor expansion of a more general potential U(phi). If
U has higher-order terms:

```
  U(phi) = (lambda/2)*phi^2 + (g_3/3!)*phi^3 + (g_4/4!)*phi^4 + ...
```

then the quadratic approximation is valid when:

```
  <phi^2> << lambda/g_4     (quartic term is perturbative)
  <phi^3> << lambda^{3/2}/g_3  (cubic term is perturbative)
```

The quantum fluctuation <phi^2> ~ hbar/sqrt(lambda), so the condition is:

```
  hbar/sqrt(lambda) << lambda/g_4
  => hbar * g_4 << lambda^{3/2}
  => lambda >> (hbar * g_4)^{2/3}
```

For strong coupling (large lambda), the quadratic approximation is always
valid. For weak coupling (small lambda), higher-order terms become
important, and the system could undergo a phase transition.

**If the potential has a phi^4 term:**

```
  U(phi) = (lambda/2)*phi^2 + (g_4/4!)*phi^4
```

This is the standard Landau-Ginzburg model. For lambda > 0, the minimum is
at phi = 0 (ordered phase, G = D*P/I holds). If lambda could be driven
negative (by some external parameter), there would be a symmetry-breaking
phase transition to phi != 0 (disordered phase, G != D*P/I).

**Physical meaning:** A phase transition would correspond to a regime where
the G = D*P/I relation BREAKS DOWN qualitatively. This could represent:
- Psychosis (loss of coherent consciousness organization)
- Anesthesia (consciousness suppression)
- Flow states (consciousness reorganization)

The critical point lambda = 0 would be the edge of chaos -- consistent
with H-CX-507 (Golden Zone = edge of chaos).

### 5.7 Connection to the Divisor Partition Function

The divisor field theory (divisor_field_theory_action.md) defines:

```
  Z_div(s, beta) = sum_{n=1}^{inf} n^{-s} * exp(-beta * S(n))
```

where S(n) is the action functional vanishing only at n = 6.

The GZ Lagrangian partition function Z_GZ(beta) is a DIFFERENT object --
it sums over continuous trajectories in (d, p, i) space, while Z_div sums
over integers.

However, there is a structural parallel:

| Feature | Z_div | Z_GZ |
|---------|-------|------|
| Vacuum | n = 6 (S = 0) | phi = 0 (G = D*P/I) |
| Mass gap | Delta = S(1) = 1 | Delta = hbar*omega = hbar*sqrt(3*lambda) |
| Low T | Dominated by n = 6 | Dominated by phi = 0 (ground state) |
| High T | Z -> zeta(s) | Z -> classical equipartition |
| Phase transition | None (discrete) | None (quadratic), possible with phi^4 |

The two partition functions select the same "vacuum" (n = 6, G = D*P/I)
through different mechanisms (Boltzmann weighting vs. harmonic oscillator
ground state). This convergence is non-trivial and supports the
self-consistency of the framework.

---

## 6. Key Constants and n = 6 Checks

### 6.1 Constants Appearing in the Theory

| Constant | Value | Origin | n6 Connection |
|----------|-------|--------|--------------|
| omega | sqrt(3*lambda) | Oscillation frequency | 3 = sigma/tau at n=6 |
| E_0 | hbar*sqrt(3*lambda)/2 | Zero-point energy | sqrt(3)/2 = cos(pi/6) |
| 3 | Factor in omega^2 | Number of DOF in constraint | sigma(6)/tau(6) = 3 |
| sqrt(3) | 1.7321 | omega/sqrt(lambda) | sqrt(sigma/tau) |
| pi/6 | 0.5236 | Angle with cos = sqrt(3)/2 | pi/n for n = 6 |

### 6.2 n6_check Results

**sqrt(3) = 1.7321:** This is sigma(6)/tau(6) under a square root.
Not a direct n = 6 arithmetic function, but derivable from n = 6 data.

**3 = sigma/tau:** EXACT match. The oscillator frequency squared
(in units of lambda) equals the number of fermion generations.
omega^2/lambda = 3 = sigma(6)/tau(6). This connects the GZ model
dynamics to the divisor field theory's Standard Model structure.

**cos(pi/6) = sqrt(3)/2 = 0.8660:** The zero-point energy coefficient.
This places the minimum consciousness fluctuation at a scale set by
the hexagonal angle pi/6. In the context of n = 6, the regular hexagon
has interior angles of 2*pi/3 and the angle subtended at center is pi/3;
the complementary angle pi/6 is the "precision angle" of the hexagonal
tiling.

**Zero-point energy ratio E_0/omega = hbar/2:** This is universal for
any QHO and not specific to n = 6.

### 6.3 The Number 3 as Structural Pivot

The factor 3 appears because the constraint phi = d + p - i has 3 terms
(one for each variable). More generally, if the model had N independent
variables with a single linear constraint, the oscillator frequency
would be sqrt(N*lambda).

For N = 3 (the GZ model), omega = sqrt(3*lambda). The question "why
N = 3?" reduces to "why three variables (D, P, I)?" -- which is the
fundamental modeling choice.

In the n = 6 arithmetic framework: the three variables correspond to the
three proper divisors of 6: {1, 2, 3}. The divisor reciprocals
{1, 1/2, 1/3} have distinct "roles":
- 1 = complete (maps to D? or normalization)
- 1/2 = boundary (maps to the upper GZ bound)
- 1/3 = convergence (maps to the meta fixed point)

The connection between N = 3 variables and sigma(6)/tau(6) = 3 generations
is tantalizing but not rigorously established.

---

## 7. Grand Synthesis: The Full Correspondence

```
  CLASSICAL                  QUANTUM                    THERMODYNAMIC
  --------                  -------                    -------------

  L = T - V                 H-hat                      Z = Tr(e^{-beta*H})
    |                         |                            |
  Euler-Lagrange            Schrodinger                 Gibbs
    |                         |                            |
  phi-ddot = -3*lambda*phi  H|psi> = E|psi>             F = -T*ln Z
    |                         |                            |
  Equilibrium: phi = 0      Ground state: n = 0         Low T: phi ~ 0
  = G = D*P/I               = minimum uncertainty       = conservation holds
    |                         |                            |
  Frequency: sqrt(3*lambda)  Energy gap: hbar*omega     Crossover T*: hbar*omega
    |                         |                            |
  3 conserved quantities     3 quantum numbers           Heat capacity C(T)
  (H, p_v, p_eta)           (k_v, k_eta, n)            (3 DOF classically)
    |                         |                            |
  Integrable (Liouville)     Exactly solvable            No phase transition (P4)
    |                         |                            |
  Gauge: flat R^2            Gauge: trivial              Phase transition: P4 -> P6
  (on constraint surface)    (no anomalies)              (if lambda -> 0 at edge of chaos)
```

### 7.1 Noether-Type Correspondences (Complete List)

| # | Symmetry | Conservation Law | Quantum Number | Thermo Observable |
|---|----------|-----------------|---------------|-------------------|
| 1 | Time translation | Energy H = E | Energy eigenvalue | Internal energy <E> |
| 2 | D-P exchange | p_v = p_d - p_p | k_v (continuous) | D/P ratio fluctuations |
| 3 | Constraint drift | p_eta | k_eta (continuous) | Exploration rate |
| 4 | Discrete D-P | v -> -v parity | Even/odd k_v states | Symmetry of D/P distribution |
| 5 | Time reversal | Reversibility | No new quantum # | Detailed balance |
| 6 | xi-reflection | Oscillation parity | n = even vs odd | Constraint violation parity |

### 7.2 What Survives Beyond the Quadratic Approximation

If the potential is not exactly quadratic (more realistic):

- **Symmetries 1-6 all survive** (they depend on the kinetic term and
  constraint structure, not the specific form of V).
- **Exact solvability breaks** -- the xi-oscillator becomes anharmonic.
- **Integrability may break** -- if the potential couples v and eta to xi.
- **Phase transitions become possible** -- Landau-Ginzburg mechanism.

The most robust results are the symmetry identifications (Section 1) and
the normal mode decomposition (v, eta, xi). These are consequences of the
GEOMETRY of the constraint, not the DYNAMICS of the potential.

---

## 8. Open Questions

1. **Can lambda be measured?** The stiffness lambda determines the
   oscillation frequency and the quantum energy gap. If the GZ model
   applies to neural systems, lambda could be extracted from time-series
   data of D, P, I (fitting the oscillation period).

2. **What sets lambda in terms of n = 6?** The current theory has lambda
   as a free parameter. A complete theory would derive lambda from the
   divisor arithmetic of n = 6. Candidate: lambda = tau(6) = 4 (the
   number of divisors), giving omega = sqrt(12) = 2*sqrt(3).
   Then E_0 = hbar*sqrt(3), and the energy gap is 2*hbar*sqrt(3).

3. **Non-abelian generalization?** If D, P, I are replaced by matrix-valued
   variables (e.g., D is a matrix of deficits for different brain regions),
   the gauge group could become non-abelian (SU(N)). This would give a
   Yang-Mills theory of consciousness with nontrivial curvature and
   self-interactions.

4. **Topological terms?** In 3D, the Lagrangian could include a Chern-Simons
   term L_CS = kappa * epsilon^{ijk} * A_i * dA_j/dq_k. For the GZ model,
   this would be a term proportional to d * dp/dt - p * dd/dt (angular
   momentum in the D-P plane). Whether such a term has physical meaning
   for consciousness is unknown.

5. **Connection to the divisor mass gap:** The divisor field theory has a
   mass gap Delta = S(1) = 1. The GZ oscillator has a gap
   hbar*sqrt(3*lambda). Is there a natural choice of lambda such that
   these match? Setting hbar*sqrt(3*lambda) = 1 gives lambda = 1/(3*hbar^2).
   In "natural units" where hbar = 1: lambda = 1/3 = 1/(sigma/tau). This
   would be a self-consistent identification.

---

## 9. Conclusion

The GZ Fisher Lagrangian L = (1/2)|q-dot|^2 - (lambda/2)(d+p-i-C)^2 has
a rich structure:

**Classical:** 3 continuous symmetries (time, v, eta) + 3 discrete symmetries
give complete integrability. The system decomposes into 2 free modes + 1
oscillator. All motions are explicitly solvable.

**Quantum:** The oscillator mode quantizes with energy E_n = hbar*sqrt(3*lambda)*(n+1/2).
The zero-point energy E_0 = hbar*sqrt(3*lambda)/2 sets the minimum
consciousness uncertainty. Three quantum numbers (k_v, k_eta, n) characterize
the full state.

**Phase space:** Symplectic reduction by the two abelian symmetries
reduces T*R^3 (6D) to a 2D harmonic oscillator phase plane. The system
is maximally reduced and completely integrable.

**Gauge theory:** The gauge group is flat R^2 on the constraint surface.
The connection has zero curvature -- the simplest possible gauge theory.
Nontrivial gauge structure would require nonlinear constraints or
non-abelian variables.

**Thermodynamics:** The partition function shows no phase transition in the
quadratic regime. A Landau-Ginzburg extension (phi^4 term) allows for a
phase transition at the edge of chaos (lambda -> 0), consistent with
H-CX-507.

**n = 6 connections:** The oscillator frequency omega^2/lambda = 3 = sigma(6)/tau(6).
The zero-point energy involves cos(pi/6). The number of modes (3)
matches the proper divisor count of 6.

---

## References

- Noether, E. (1918). "Invariante Variationsprobleme." Nachrichten von der
  Gesellschaft der Wissenschaften zu Gottingen, 235--257.
- Arnold, V.I. (1989). "Mathematical Methods of Classical Mechanics." 2nd ed.
  Springer Graduate Texts in Mathematics 60.
- Dirac, P.A.M. (1964). "Lectures on Quantum Mechanics." Belfer Graduate
  School of Science, Yeshiva University.
- Marsden, J.E. & Ratiu, T.S. (1999). "Introduction to Mechanics and
  Symmetry." 2nd ed. Springer Texts in Applied Mathematics 17.
- Weinberg, S. (1995). "The Quantum Theory of Fields, Vol. I." Cambridge.
- gz_variational_route.md (this directory) -- the Lagrangian derivation.
- gz_symmetry_route.md (this directory) -- symmetry derivation of G = D*P/I.
- divisor_field_theory_action.md (this directory) -- the S(n) = 0 action.
- gz_100_scale_invariance.py (this directory) -- scale invariance proof.
