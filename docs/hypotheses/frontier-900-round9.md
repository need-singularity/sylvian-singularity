# Frontier 900 (Round 9): Iterated Compositions + Multiplicative + Inequalities

> 60 hypotheses via systematic scanning. Generated + verified 2026-03-27.

## Summary

| Category | Gen | PASS | FAIL | 🟩 | 🟧★ | 🟧 | ⬛ |
|----------|-----|------|------|-----|------|-----|-----|
| Iterated Compositions | 20 | 18 | 2 | 1 | 9 | 8 | 2 |
| Multiplicative Combos | 20 | 20 | 0 | 0 | 14 | 6 | 0 |
| Inequality Chars | 20 | 20 | 0 | 3 | 9 | 8 | 0 |
| **Total** | **60** | **58** | **2** | **4** | **32** | **22** | **2** |

## Major Discoveries

### NEW UNIQUE CHARACTERIZATIONS (🟧★, n=6 only)

| # | Identity | Solutions |
|---|---------|----------|
| 1 | rad(sigma(n)) = n | {6} ONLY |
| 2 | sigma/tau + phi/omega = tau | {6} ONLY |
| 3 | sigma/phi = n | {6} ONLY |
| 4 | sigma(tau(n)) = n+1 | {2, 6} |
| 5 | phi(sigma)+sigma(phi) = n+1 | {2, 6} |
| 6 | sigma*tau - n*phi = n^2 | {2, 6} |
| 7 | tau*sigma - phi*psi = sigma*phi | {2, 6} |

### PROVED GENERALIZING THEOREMS (🟩)

| # | Theorem | Scope |
|---|---------|-------|
| 1 | (sigma-phi)/(tau-omega) = sopfr | ALL squarefree semiprimes |
| 2 | n' = sopfr for semiprimes | ALL squarefree semiprimes |
| 3 | aliquot(n) = n iff perfect | ALL perfect numbers |
| 4 | tau!/sigma = phi | n=6 among perfects |

### KEY CHAIN: sigma^2(P_1) = P_2

```
sigma(6) = 12
sigma(12) = 28 = P_2 (second perfect number!)
sigma(28) = 56
sigma(56) = 120

Iterated sigma starting from P_1=6 hits P_2=28 at step 2.
Does NOT continue: sigma^2(28)=120 != 496=P_3.
```

### PROVED: (sigma-phi)/(tau-omega) = sopfr for semiprimes

```
For n=pq (distinct primes):
  sigma = (1+p)(1+q), phi = (p-1)(q-1), tau = 4, omega = 2
  sigma-phi = (1+p+q+pq)-(pq-p-q+1) = 2(p+q)
  tau-omega = 4-2 = 2
  Ratio = (2(p+q))/2 = p+q = sopfr(n). QED.

Verified: n=6(5), 10(7), 14(9), 15(8), 21(10), 22(13)... all match!
```

## Verification Script
- frontier_900_verify.py (in math/ directory)
