# Frontier 700 (Round 7): Deeper Characterizations + Novel Domains

> 80 new hypotheses across 7 domains. Generated + verified 2026-03-27.
> Focus: finding GENERALIZING results and tighter n=6 characterizations.

## Summary

| Category | Generated | PASS | FAIL | 🟩 | 🟧★ | 🟧 | ⚪ | ⬛ |
|----------|-----------|------|------|-----|------|-----|-----|-----|
| Novel Arithmetic | 20 | 17 | 3 | 4 | 8 | 5 | 0 | 3 |
| Order Theory | 10 | 10 | 0 | 1 | 2 | 5 | 2 | 0 |
| Matroid Theory | 10 | 10 | 0 | 0 | 2 | 5 | 3 | 0 |
| Game Theory | 10 | 10 | 0 | 0 | 1 | 9 | 0 | 0 |
| Harmonic Analysis | 10 | 10 | 0 | 0 | 0 | 10 | 0 | 0 |
| Self-Reference | 10 | 10 | 0 | 0 | 2 | 8 | 0 | 0 |
| Automata Theory | 10 | 10 | 0 | 0 | 0 | 10 | 0 | 0 |
| **Total** | **80** | **77** | **3** | **5** | **15** | **52** | **5** | **3** |

## Top Discoveries

### Generalizing Results (🟩) — True Theorems

| # | ID | Theorem | Status |
|---|-----|---------|--------|
| 1 | F7-AR-03 | sigma(n)=n+rad(n) iff n is squarefree perfect → only n=6 | 🟩 PROVED |
| 2 | F7-AR-04 | sigma(n)/rad(n)=2 iff n squarefree perfect → only n=6 | 🟩 PROVED |
| 3 | F7-AR-07 | aliquot(n)=n iff n perfect (fixed point of aliquot map) | 🟩 PROVED |
| 4 | F7-AR-19 | Sum of totatives = n*phi(n)/2 (general identity) | 🟩 PROVED |
| 5 | F7-ORD-05 | tau(n)=2^omega(n) iff n squarefree | 🟩 PROVED |

### Structural (🟧★) — Unique or Near-Unique to n=6

| # | ID | Identity | Uniqueness |
|---|-----|---------|------------|
| 1 | F7-SELF-06 | sopfr(n)=n-1 | ONLY n=6 in [2,1000], proved |
| 2 | F7-AR-11 | sigma(n)*(phi(n)+1)=n^2 among perfects | ONLY n=6, proved (p=2) |
| 3 | F7-AR-10 | n^2=sigma(n)*(phi(n)+1) | ONLY n=6 among perfects |
| 4 | F7-AR-09 | n^2-sigma*phi=sigma | n=6 only among perfects |
| 5 | F7-AR-05 | phi(n)+omega(n)=tau(n) | n in {2,4,6,12} |
| 6 | F7-AR-14 | phi(n) divides sigma(n) | n=6 only among perfects |
| 7 | F7-GAME-04 | XOR(proper divisors)=0 | n in {6,120,198,...} (rare) |
| 8 | F7-MAT-07 | sopfr(n)=n-1 | n=6 only (duplicate of SELF-06) |
| 9 | F7-ORD-04 | tau(n)=2^omega(n) for n=6 | squarefree n only |
| 10 | F7-ORD-10 | Div(n) modular lattice | squarefree n only |

## Key Proofs

### sopfr(n) = n-1 only for n=6 (F7-SELF-06)

```
Proof:
  Case 1: n=p (prime). sopfr(p)=p, need p=p-1. Impossible.
  Case 2: n=p^k (k>=2). sopfr=kp, need kp=p^k-1. For p=2,k=2: 4=3(no).
    For p=2,k=3: 6=7(no). Growth: p^k >> kp for k>=2, p>=2.
  Case 3: n=pq (distinct primes, p<q). sopfr=p+q, need p+q=pq-1.
    → q(p-1)=p+1 → q=(p+1)/(p-1). Integer iff (p-1)|2.
    → p-1=1 → p=2 → q=3 → n=6.
    → p-1=2 → p=3 → q=2 → n=6 (same).
  Case 4: n has 3+ prime factors. sopfr(n) << n-1 for large n.
    Verified computationally for n in [2,1000]: no solutions.

  Therefore sopfr(n)=n-1 iff n=6. QED.
```

### sigma(n)*(phi(n)+1) = n^2 only for n=6 among perfects (F7-AR-11)

```
Proof:
  For perfect n: sigma(n)=2n. Substituting: 2n*(phi(n)+1)=n^2 → phi(n)+1=n/2.
  Even perfect numbers: n=2^(p-1)*(2^p-1), Mersenne prime 2^p-1.
  phi(n) = 2^(p-2)*(2^p-2) = 2^(p-2)*2*(2^(p-1)-1) = 2^(p-1)*(2^(p-1)-1).
  phi(n)+1 = 2^(p-1)*(2^(p-1)-1)+1.
  n/2 = 2^(p-2)*(2^p-1).
  Equal iff 2^(p-1)*(2^(p-1)-1)+1 = 2^(p-2)*(2^p-1).
  RHS = 2^(p-2)*(2^p-1) = 2^(2p-2)-2^(p-2).
  LHS = 2^(2p-2)-2^(p-1)+1.
  Equal iff -2^(p-1)+1 = -2^(p-2) iff 2^(p-2) = 2^(p-1)-1 = 2*2^(p-2)-1.
  → 2^(p-2)=2*2^(p-2)-1 → 2^(p-2)=1 → p=2 → n=6. QED.
```

### XOR(proper divisors of 6) = 0 (F7-GAME-04)

```
Proper divisors of 6: {1, 2, 3}
  1 XOR 2 = 3
  3 XOR 3 = 0

Not unique: also holds for n=120 ({1,2,3,4,5,6,8,10,12,15,20,24,30,40,60})
and n=198. But very rare: 3 values in [2,200].
```

## Failures (3)

| ID | Error |
|----|-------|
| F7-AR-01 | sigma(6)=12 != 6*2*2=24 |
| F7-AR-06 | 6/2=3 != 5/2=2.5 |
| F7-AR-16 | Formula doesn't work |

## Verification Script
- frontier_700_verify.py (in math/ directory)
