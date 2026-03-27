#!/usr/bin/env python3
"""
H-CX-74: Partition p(6)=11 to Expert Count Bridge
Math identity: p(6)=11 and p(6)=sigma(6)-1=12-1 (unique among perfect numbers).
Hypothesis: The 11 partitions of 6 define the optimal expert count for a
consciousness-aware MoE system, where each expert specializes in one
decomposition mode of 6-dimensional input.

Experiment:
1. Enumerate all 11 partitions of 6 and their structure
2. Measure partition coverage by k experts (k=2..20)
3. Compare routing entropy for different k values
4. Check if k=11 is optimal by information-theoretic measure
5. Texas Sharpshooter + generalization to n=28
"""

import math
import numpy as np
from itertools import combinations_with_replacement
from collections import Counter

print("=" * 60)
print("EXPERIMENT: Partition p(6)=11 Expert Count Bridge")
print("=" * 60)

# Part 1: Enumerate partitions of 6
def partitions(n, max_val=None):
    """Generate all partitions of n."""
    if max_val is None:
        max_val = n
    if n == 0:
        yield []
        return
    for i in range(min(n, max_val), 0, -1):
        for p in partitions(n - i, i):
            yield [i] + p

print("\n--- Part 1: All 11 Partitions of 6 ---")
parts6 = list(partitions(6))
print(f"p(6) = {len(parts6)}")
for i, p in enumerate(parts6):
    print(f"  P{i+1:2d}: {p} (parts={len(p)}, max={p[0]}, distinct={len(set(p))})")

# Structural analysis
print("\n  Structure summary:")
by_length = Counter(len(p) for p in parts6)
for k, v in sorted(by_length.items()):
    print(f"    {k} parts: {v} partitions")

# Part 2: Partition-expert distance matrix
print("\n--- Part 2: Partition Distance Matrix ---")

def partition_to_freq(p, n=6):
    """Convert partition to frequency vector [count of 1s, count of 2s, ..., count of ns]."""
    freq = [0] * n
    for x in p:
        freq[x-1] += 1
    return np.array(freq, dtype=float)

freq_vectors = np.array([partition_to_freq(p) for p in parts6])

# Compute pairwise L2 distances
n_parts = len(parts6)
dist_matrix = np.zeros((n_parts, n_parts))
for i in range(n_parts):
    for j in range(n_parts):
        dist_matrix[i,j] = np.linalg.norm(freq_vectors[i] - freq_vectors[j])

print("Distance matrix (L2 between frequency vectors):")
print("     " + " ".join(f"P{i+1:2d}" for i in range(n_parts)))
for i in range(n_parts):
    row = " ".join(f"{dist_matrix[i,j]:4.1f}" for j in range(n_parts))
    print(f"P{i+1:2d}: {row}")

# Part 3: Optimal expert count via k-medoids-like coverage
print("\n--- Part 3: Expert Coverage vs k ---")

def coverage_score(k, freq_vectors, n_trials=500, seed=42):
    """Measure how well k random 'experts' cover the partition space.
    Each expert = centroid of assigned partitions.
    Coverage = 1 - mean(min distance to nearest expert) / max_possible.
    """
    rng = np.random.RandomState(seed)
    n = len(freq_vectors)
    best_score = -1

    for _ in range(n_trials):
        # Random k centers from partition vectors
        idx = rng.choice(n, size=min(k, n), replace=False)
        centers = freq_vectors[idx]

        # Assign each partition to nearest center
        total_dist = 0
        for v in freq_vectors:
            dists = [np.linalg.norm(v - c) for c in centers]
            total_dist += min(dists)

        score = 1.0 - total_dist / (n * np.max(dist_matrix))
        if score > best_score:
            best_score = score

    return best_score

# Also compute information-theoretic measure
def routing_entropy(k, freq_vectors, n_trials=200, seed=42):
    """Shannon entropy of expert assignment distribution.
    Higher entropy = more uniform use of experts = better.
    """
    rng = np.random.RandomState(seed)
    n = len(freq_vectors)
    best_entropy = -1

    for _ in range(n_trials):
        idx = rng.choice(n, size=min(k, n), replace=False)
        centers = freq_vectors[idx]

        assignments = []
        for v in freq_vectors:
            dists = [np.linalg.norm(v - c) for c in centers]
            assignments.append(np.argmin(dists))

        counts = Counter(assignments)
        probs = np.array([counts.get(i, 0) for i in range(min(k, n))], dtype=float)
        probs = probs / probs.sum()
        probs = probs[probs > 0]
        entropy = -np.sum(probs * np.log2(probs))
        if entropy > best_entropy:
            best_entropy = entropy

    return best_entropy

print(f"\n{'k':>3} {'Coverage':>10} {'Entropy':>10} {'Eff=Cov*Ent':>12} {'Note':>15}")
print("-" * 55)

results = []
for k in range(2, 21):
    cov = coverage_score(k, freq_vectors)
    ent = routing_entropy(k, freq_vectors)
    eff = cov * ent
    note = ""
    if k == 11:
        note = "<- p(6)=11"
    elif k == 6:
        note = "<- n"
    elif k == 12:
        note = "<- sigma"
    elif k == 4:
        note = "<- tau"
    results.append((k, cov, ent, eff))
    print(f"{k:3d} {cov:10.4f} {ent:10.4f} {eff:12.4f} {note:>15}")

# Find optimal k
best_k = max(results, key=lambda x: x[3])
print(f"\nOptimal k by efficiency: k={best_k[0]} (eff={best_k[3]:.4f})")

# Part 4: Deeper analysis - partition lattice properties
print("\n--- Part 4: Partition Lattice Structure ---")

# Conjugate partitions
print("Partition conjugates (Young diagram transpose):")
def conjugate(p, n=6):
    """Conjugate partition."""
    if not p:
        return []
    result = []
    for i in range(1, p[0]+1):
        result.append(sum(1 for x in p if x >= i))
    return result

self_conjugate = 0
for i, p in enumerate(parts6):
    conj = conjugate(p)
    is_self = (p == conj)
    if is_self:
        self_conjugate += 1
    print(f"  P{i+1:2d}: {p} <-> {conj} {'(SELF-CONJUGATE)' if is_self else ''}")

print(f"\nSelf-conjugate partitions: {self_conjugate}")
print(f"  (= number of partitions into distinct odd parts)")

# Part 5: Sigma-partition connection
print("\n--- Part 5: p(n)=sigma(n)-1 Check ---")
from sympy import divisor_sigma

for n in range(1, 51):
    pn = len(list(partitions(n)))
    sn = int(divisor_sigma(n, 1))
    if pn == sn - 1:
        print(f"  n={n}: p({n})={pn}, sigma({n})={sn}, p=sigma-1: YES")

# Part 6: Generalization to n=28
print("\n--- Part 6: Perfect Number 28 Generalization ---")
parts28 = list(partitions(28))
p28 = len(parts28)
sigma28 = int(divisor_sigma(28, 1))
print(f"n=28: p(28)={p28}, sigma(28)={sigma28}")
print(f"  p(28)=sigma(28)-1? {p28} = {sigma28-1}? {p28 == sigma28-1}")
print(f"  p(28)-sigma(28) = {p28 - sigma28}")
print(f"  Ratio p(28)/sigma(28) = {p28/sigma28:.4f}")

# Part 7: Texas Sharpshooter
print("\n--- Part 7: Texas Sharpshooter ---")
# How often does p(n) = sigma(n) +/- 1 for random n?
hits_exact = 0
hits_pm1 = 0
total = 50
for n in range(1, total+1):
    pn = len(list(partitions(n)))
    sn = int(divisor_sigma(n, 1))
    if pn == sn - 1:
        hits_exact += 1
    if abs(pn - sn) <= 1:
        hits_pm1 += 1

print(f"p(n)=sigma(n)-1 for n=1..{total}: {hits_exact}/{total} = {hits_exact/total:.4f}")
print(f"p(n)=sigma(n)+/-1 for n=1..{total}: {hits_pm1}/{total} = {hits_pm1/total:.4f}")

# Monte Carlo: random functions matching divisor function distribution
import random
rng = random.Random(42)
N_MC = 10000
mc_hits = 0
for _ in range(N_MC):
    # Pick random n in 1..50
    n = rng.randint(1, 50)
    pn = len(list(partitions(n)))
    # Random "sigma-like" value
    fake_sigma = rng.randint(n, 3*n)
    if pn == fake_sigma - 1:
        mc_hits += 1

p_mc = mc_hits / N_MC
print(f"Monte Carlo p-value (random sigma): {p_mc:.6f}")

# Part 8: Ad-hoc check
print("\n--- Part 8: Ad-hoc Check ---")
print("Identity: p(6) = sigma(6) - 1 = 11")
print("  The '-1' IS an ad-hoc correction")
print("  But: p(2)=sigma(2)-1=2, p(3)=sigma(3)-1=3 also hold")
print("  So it's a pattern for n in {2,3,6} = divisors of 6!")
print("  The '-1' may encode: 'identity partition excluded'")
print("  since {6} itself maps to sigma rather than a proper partition")

print("\n" + "=" * 60)
print("SUMMARY")
print("=" * 60)
print(f"1. p(6)=11 (verified), p(6)=sigma(6)-1 (verified)")
print(f"2. Holds for n in {{2,3,6}} = proper divisors of 6 plus 6 itself")
print(f"3. Does NOT hold for n=28 (second perfect number)")
print(f"4. Optimal expert k by efficiency: {best_k[0]}")
print(f"5. Self-conjugate partitions of 6: {self_conjugate}")
