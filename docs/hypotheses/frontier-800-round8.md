# Frontier 800 (Round 8): Systematic Characterization Search

> 74 hypotheses via systematic scanning. Generated + verified 2026-03-27.
> Strategy: computationally scan f(n)=g(n) for n=2..200.

## Summary

| Category | Generated | PASS | FAIL | 🟩 | 🟧★ | 🟧 | ⚪ | ⬛ |
|----------|-----------|------|------|-----|------|-----|-----|-----|
| Systematic Scans | 14 | 12 | 2 | 2 | 7 | 3 | 0 | 2 |
| Characterizations | 20 | 20 | 0 | 0 | 14 | 6 | 0 | 0 |
| Number Theory | 20 | 20 | 0 | 0 | 1 | 18 | 1 | 0 |
| Synthesis | 20 | 20 | 0 | 0 | 6 | 14 | 0 | 0 |
| **Total** | **74** | **72** | **2** | **2** | **28** | **41** | **1** | **2** |

## Major New Characterizations

### 1. n*tau(n) = sigma(n)*omega(n): ONLY n=6 in [2,200] (H-NT-432)

```
6*4 = 12*2 = 24
Proved for semiprimes: (p-1)(q-1)=2 forces p=2,q=3.
Other factorization types ruled out.
```

### 2. phi(n)+tau(n)=n AND sigma(n)=2n: ONLY n=6 (H-SYNTH-14/15)

```
phi(6)+tau(6) = 2+4 = 6 = n
sigma(6) = 12 = 2*6
Conjunction uniquely characterizes 6 among ALL integers.
phi+tau=n alone: solutions {6, 8, 9}
sigma=2n alone: solutions {6, 28, 496, ...}
Intersection: {6}
```

### 3. sigma(n) = phi(n)*sopfr(n) + omega(n): n in {2, 6} (H-NT-433)

```
12 = 2*5 + 2
Master decomposition: divisor sum = totient*prime_weight + prime_count.
Only n=6 among perfect numbers.
```

### 4. phi*sopfr = sigma - omega: n in {2, 6}

```
2*5 = 10 = 12-2
Equivalent to master identity above.
```

### 5. phi(sigma(n)) = n - omega(n): n in {3, 6}

```
phi(12) = 4 = 6-2
Near-unique: also n=3 (phi(4)=2=3-1).
```

### 6. sigma*phi/n = tau: ONLY n=6 among tested range

```
12*2/6 = 4 = tau(6)
Equivalently: sigma*phi = n*tau = 24.
```

### 7. 6 is the only number that is perfect + factorial + primorial + highly composite

```
Perfect: sigma(6)=12=2*6 ✓
Factorial: 6=3! ✓
Primorial: 6=2*3=2# ✓
Highly composite: tau(6)>tau(m) for all m<6 ✓
Triangular: 6=T_3 ✓
Practical: all 1..12 representable ✓
```

## Failures (2)

| ID | Error |
|----|-------|
| F8-SYS-06 | sigma+phi=psi+tau: solutions include {3,4,10,30}, not {6} |
| F8-SYS-08 | J_2(n)=n^2-n: solutions are prime squares, not n=6 |

## Verification Script
- frontier_800_verify.py (in math/ directory)
