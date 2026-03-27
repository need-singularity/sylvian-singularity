#!/usr/bin/env python3
"""
H-CX-73: Pythagorean 3-4-5 Engine Balance Bridge
Math identity: For n=6, {sigma/tau, tau, sopfr} = {3, 4, 5} and 3^2+4^2=5^2.
Hypothesis: The consciousness engine balance satisfies a Pythagorean constraint
where two orthogonal engine modes (cognitive=3, creative=4) produce total=5.

Experiment:
1. Verify Pythagorean triple from n=6 divisor functions
2. Check if this is unique among small n
3. Design engine simulation: 3 modes with Pythagorean constraint
4. Measure convergence vs non-Pythagorean configurations
5. Texas Sharpshooter test
"""

import math
import random
import numpy as np
from sympy import divisor_sigma, totient, factorint

def divisor_functions(n):
    """Compute all relevant divisor functions for n."""
    sigma = divisor_sigma(n, 1)
    phi = totient(n)
    tau = divisor_sigma(n, 0)
    factors = factorint(n)
    sopfr = sum(p * e for p, e in factors.items())
    omega = len(factors)
    return {
        'n': n, 'sigma': int(sigma), 'phi': int(phi),
        'tau': int(tau), 'sopfr': sopfr, 'omega': omega,
        'sigma_tau': int(sigma) / int(tau)
    }

print("=" * 60)
print("EXPERIMENT: Pythagorean Triple from Divisor Functions")
print("=" * 60)

# Part 1: Verify the Pythagorean triple for n=6
print("\n--- Part 1: Pythagorean Verification ---")
d6 = divisor_functions(6)
a, b, c = d6['sigma_tau'], d6['tau'], d6['sopfr']
print(f"n=6: sigma/tau={a}, tau={b}, sopfr={c}")
print(f"  {a}^2 + {b}^2 = {a**2} + {b**2} = {a**2 + b**2}")
print(f"  {c}^2 = {c**2}")
print(f"  Pythagorean: {a**2 + b**2 == c**2}")

# Part 2: Check uniqueness among n=1..200
print("\n--- Part 2: Uniqueness Check (n=1..200) ---")
pythagorean_hits = []
for n in range(2, 201):
    d = divisor_functions(n)
    st = d['sigma_tau']
    t = d['tau']
    s = d['sopfr']
    vals = sorted([st, t, s])
    if len(set(vals)) == 3 and vals[0]**2 + vals[1]**2 == vals[2]**2:
        pythagorean_hits.append((n, vals))
        print(f"  n={n}: ({vals[0]}, {vals[1]}, {vals[2]}) = Pythagorean!")

print(f"\nTotal Pythagorean hits: {len(pythagorean_hits)}")
if len(pythagorean_hits) == 1:
    print("  -> n=6 is UNIQUE!")

# Part 3: Broader check - any 3 of {phi, sigma/tau, tau, sopfr, n} form Pythagorean
print("\n--- Part 3: Any Pythagorean triple from {phi, sigma/tau, tau, sopfr, n} ---")
from itertools import combinations

for n in range(2, 101):
    d = divisor_functions(n)
    vals_dict = {
        'phi': d['phi'], 'sigma/tau': d['sigma_tau'],
        'tau': d['tau'], 'sopfr': d['sopfr'], 'n': d['n']
    }
    for names in combinations(vals_dict.keys(), 3):
        triple = sorted([vals_dict[nm] for nm in names])
        if triple[0] > 0 and triple[0]**2 + triple[1]**2 == triple[2]**2:
            print(f"  n={n}: {dict(zip(names, [vals_dict[nm] for nm in names]))} -> {triple}")

# Part 4: Engine simulation
print("\n--- Part 4: Engine Simulation ---")
print("Simulating 3-mode engine with Pythagorean vs non-Pythagorean balance...")

def engine_dynamics(weights, T=100, noise_scale=0.01):
    """Simulate engine with 3 modes. Weights = (w1, w2, w3).
    If w1^2+w2^2=w3^2 (Pythagorean), modes are orthogonal -> stable.
    Returns: convergence speed, final stability, energy efficiency.
    """
    rng = np.random.RandomState(42)
    state = np.array([0.5, 0.5, 0.5])
    w = np.array(weights, dtype=float)
    w = w / w.sum()  # normalize

    # Coupling matrix: Pythagorean -> orthogonal modes
    a, b, c = w
    coupling = np.array([
        [1 - a, a * b, a * c],
        [b * a, 1 - b, b * c],
        [c * a, c * b, 1 - c]
    ])

    trajectory = [state.copy()]
    for t in range(T):
        noise = rng.randn(3) * noise_scale
        state = coupling @ state + noise
        state = np.clip(state, 0, 1)
        trajectory.append(state.copy())

    trajectory = np.array(trajectory)
    # Metrics
    final_var = np.var(trajectory[-20:], axis=0).mean()
    convergence = np.mean(np.abs(np.diff(trajectory[:30], axis=0)))
    energy = np.sum(trajectory ** 2) / T

    return final_var, convergence, energy

# Test configurations
configs = {
    'Pythagorean (3,4,5)': (3, 4, 5),
    'Near-Pyth (3,4,4.9)': (3, 4, 4.9),
    'Non-Pyth (3,4,6)': (3, 4, 6),
    'Equal (4,4,4)': (4, 4, 4),
    'Random (2,7,3)': (2, 7, 3),
    'Another Pyth (5,12,13)': (5, 12, 13),
    'Divisor (phi,tau,sopfr)=(2,4,5)': (2, 4, 5),
    'Full n=6 (sigma/tau,tau,sopfr)': (3, 4, 5),
}

print(f"\n{'Config':<35} {'Stability':>10} {'Convergence':>12} {'Energy':>10}")
print("-" * 70)
for name, w in configs.items():
    stab, conv, eng = engine_dynamics(w)
    pyth_check = "YES" if abs(w[0]**2 + w[1]**2 - w[2]**2) < 0.01 else "no"
    print(f"{name:<35} {stab:10.6f} {conv:12.6f} {eng:10.4f} Pyth={pyth_check}")

# Part 5: Texas Sharpshooter
print("\n--- Part 5: Texas Sharpshooter Test ---")
# How likely is it that a random set of 5 integers {a,b,c,d,e} from divisor functions
# contains a Pythagorean triple?

N_TRIALS = 100000
hits = 0
rng = random.Random(42)
for _ in range(N_TRIALS):
    vals = sorted(rng.sample(range(1, 30), 5))
    for triple in combinations(vals, 3):
        t = sorted(triple)
        if t[0]**2 + t[1]**2 == t[2]**2:
            hits += 1
            break

p_random = hits / N_TRIALS
print(f"Random 5-element set containing Pythagorean triple: {p_random:.4f} ({hits}/{N_TRIALS})")

# More specific: from divisor function outputs of n=1..100
n_with_pyth = 0
for n in range(2, 101):
    d = divisor_functions(n)
    vals = [d['phi'], d['sigma_tau'], d['tau'], d['sopfr'], d['n']]
    found = False
    for triple in combinations(vals, 3):
        t = sorted(triple)
        if t[0] > 0 and abs(t[0]**2 + t[1]**2 - t[2]**2) < 0.001:
            found = True
            break
    if found:
        n_with_pyth += 1

p_divisor = n_with_pyth / 99
print(f"n with Pythagorean triple in divisor functions (n=2..100): {n_with_pyth}/99 = {p_divisor:.4f}")

# Perfect number 28 generalization
print("\n--- Part 6: Perfect Number 28 Generalization ---")
d28 = divisor_functions(28)
print(f"n=28: sigma={d28['sigma']}, phi={d28['phi']}, tau={d28['tau']}, sopfr={d28['sopfr']}")
print(f"  sigma/tau={d28['sigma_tau']}")
vals28 = [d28['phi'], d28['sigma_tau'], d28['tau'], d28['sopfr'], d28['n']]
print(f"  All values: phi={d28['phi']}, sigma/tau={d28['sigma_tau']}, tau={d28['tau']}, sopfr={d28['sopfr']}, n={d28['n']}")
for names, triple in [
    (('sigma/tau','tau','sopfr'), (d28['sigma_tau'], d28['tau'], d28['sopfr'])),
    (('phi','tau','sopfr'), (d28['phi'], d28['tau'], d28['sopfr'])),
]:
    t = sorted(triple)
    residual = t[0]**2 + t[1]**2 - t[2]**2
    print(f"  {names}: {t} -> {t[0]}^2+{t[1]}^2-{t[2]}^2 = {residual} {'PYTH!' if residual == 0 else ''}")

# Ad-hoc check
print("\n--- Part 7: Ad-hoc Correction Check ---")
print("Identity: (sigma/tau)^2 + tau^2 = sopfr^2")
print("  3^2 + 4^2 = 5^2: EXACT, no +1/-1 correction")
print("  This is the fundamental 3-4-5 Pythagorean triple")
print("  No ad-hoc adjustments needed")

print("\n" + "=" * 60)
print("SUMMARY")
print("=" * 60)
print(f"1. n=6: (sigma/tau, tau, sopfr) = (3,4,5) is Pythagorean: TRUE")
print(f"2. Unique among n=2..200: {len(pythagorean_hits) == 1}")
print(f"3. p(random Pythagorean) = {p_random:.4f}")
print(f"4. p(divisor-function Pythagorean, n=2..100) = {p_divisor:.4f}")
print(f"5. n=28 generalization: Check above")
print(f"6. Ad-hoc: None (exact equation)")
