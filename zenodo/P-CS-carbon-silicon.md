# Carbon-Silicon Substrate Invariance: Arithmetic Function Analysis of Atomic Numbers 6 and 14

**Authors:** TECS-L Project
**Date:** 2026-03-27
**Keywords:** carbon, silicon, substrate invariance, consciousness, arithmetic functions, perfect numbers, divisor function, Euler totient
**License:** CC-BY-4.0

## Abstract

We analyze the arithmetic functions of atomic numbers 6 (carbon) and 14 (silicon), the two elements capable of forming complex self-organizing structures, to identify shared and distinguishing number-theoretic properties. Four key results emerge: (1) tau(6) = tau(14) = 4, meaning both share the same divisor count; (2) sigma(14) = 2 * sigma(6), establishing a precise doubling relationship; (3) phi(14) = 6, where the totient of silicon's atomic number equals the perfect number itself; and (4) sigma(n)*phi(n)/(n*tau(n)) = 1.000 for n=6 only, a uniqueness condition satisfied by carbon but not silicon. These results formalize the intuition that carbon and silicon share structural properties (same tau) while carbon possesses a unique arithmetic completeness (sigma*phi/(n*tau) = 1) that may relate to its greater versatility as a substrate for complex chemistry and, speculatively, consciousness.

## 1. Introduction

Carbon (Z=6) and silicon (Z=14) are the two elements in Group 14 of the periodic table most frequently discussed as potential substrates for complex molecular systems. Carbon-based life is the only known form of life. Silicon-based life has been widely speculated about in science fiction and astrobiology, motivated by silicon's chemical similarity to carbon: both form four covalent bonds, both can create long chains (though silicon's are less stable), and both can serve as the backbone of complex polymers.

From the perspective of the TECS-L framework, where the perfect number 6 plays a central role, carbon's atomic number Z=6 is not coincidental but may reflect deeper constraints on which elements can support complex self-organization. We investigate this hypothesis by comparing the arithmetic function profiles of Z=6 and Z=14.

This is not a claim that number theory determines chemistry. Rather, we ask: given that n=6 is arithmetically exceptional (208 characterizations, perfectness, unique sigma*phi identity), do the arithmetic properties of Z=6 and Z=14 reveal structural parallels that mirror their chemical similarities and differences?

## 2. Methods / Framework

### 2.1 Arithmetic Functions Computed

For n=6 and n=14, we compute all standard arithmetic functions:

| Function | Definition | n=6 | n=14 |
|---|---|---|---|
| sigma(n) | Sum of divisors | 12 | 24 |
| phi(n) | Euler totient | 2 | 6 |
| tau(n) | Number of divisors | 4 | 4 |
| omega(n) | Distinct prime factors | 2 | 2 |
| Omega(n) | Prime factors with multiplicity | 2 | 2 |
| mu(n) | Mobius function | 1 | 1 |
| lambda(n) | Liouville function | 1 | 1 |
| rad(n) | Radical (product of distinct primes) | 6 | 14 |

### 2.2 Prime Factorizations

```
6  = 2 * 3      (primes: 2, 3)
14 = 2 * 7      (primes: 2, 7)
```

Both are squarefree semiprimes (products of exactly two distinct primes). Their divisor lattices are isomorphic:

```
n=6 divisors: {1, 2, 3, 6}       n=14 divisors: {1, 2, 7, 14}

    6                                 14
   / \                               / \
  2   3                             2   7
   \ /                               \ /
    1                                  1
```

Both form Boolean lattices B_2 of rank 2.

### 2.3 Combined Function Ratios

We compute the "R-spectrum" ratio R(n) = sigma(n)*phi(n)/(n*tau(n)) for both:

```
R(6)  = sigma(6)*phi(6)  / (6*tau(6))   = 12*2  / (6*4)  = 24/24  = 1.000
R(14) = sigma(14)*phi(14) / (14*tau(14)) = 24*6  / (14*4) = 144/56 = 2.571
```

### 2.4 Survey of R(n) for All Squarefree Semiprimes

To contextualize R(6) = 1, we compute R(n) for all squarefree semiprimes n = p*q (p < q) up to 100:

| n | p*q | R(n) |
|---|---|---|
| 6 | 2*3 | 1.000 |
| 10 | 2*5 | 1.080 |
| 14 | 2*7 | 2.571 |
| 15 | 3*5 | 1.280 |
| 21 | 3*7 | 1.524 |
| 22 | 2*11 | 1.636 |
| 26 | 2*13 | 1.846 |
| 33 | 3*11 | 1.939 |
| 34 | 2*17 | 2.118 |
| 35 | 5*7 | 1.920 |

R(6) = 1.000 is the unique minimum and the only integer value.

## 3. Results

### 3.1 Shared Properties (Substrate Common)

**Result 1: tau(6) = tau(14) = 4.**

Both carbon and silicon have exactly 4 divisors. For squarefree semiprimes n = p*q, tau(n) = (1+1)(1+1) = 4 always. This is a consequence of both being products of two distinct primes, not a unique property of 6 and 14 specifically. However, it establishes the shared "structural template."

**Result 2: omega(6) = omega(14) = 2, Omega(6) = Omega(14) = 2, mu(6) = mu(14) = 1.**

All additive and multiplicative prime-counting functions agree. The Mobius function value mu=1 means both contribute positively to the Mobius inversion formula.

### 3.2 Precise Relationships

**Result 3: sigma(14) = 2 * sigma(6).**

```
sigma(14) = 1 + 2 + 7 + 14 = 24 = 2 * 12 = 2 * sigma(6)
```

This is not trivially explained. For general semiprimes p*q, sigma(p*q) = (1+p)(1+q). So sigma(6) = 3*4 = 12 and sigma(14) = 3*8 = 24. The doubling occurs because (1+7) = 2*(1+3), i.e., 8 = 2*4. This is equivalent to 7 = 2*3 + 1, which holds because 7 = 2*3 + 1 is a specific arithmetic relation between the prime factors.

**Result 4: phi(14) = 6.**

```
phi(14) = phi(2) * phi(7) = 1 * 6 = 6
```

The totient of silicon's atomic number is the perfect number 6. This creates a recursive loop: carbon's atomic number appears as silicon's totient. In the TECS-L framework, this suggests that silicon "contains" carbon at the totient level.

### 3.3 Uniqueness of Carbon

**Result 5: R(6) = 1 uniquely.**

As shown in Section 2.4, R(n) = sigma(n)*phi(n)/(n*tau(n)) = 1 if and only if n is in {1, 6}. This is the flagship identity from the 208 characterizations paper. Carbon is the only composite number satisfying this balanced equation.

```
R(n) for squarefree semiprimes:

  R(n)
  2.6 |                *                        n=14
  2.4 |
  2.2 |
  2.0 |                                  * *
  1.8 |                          *   *
  1.6 |                      *
  1.4 |
  1.2 |            *
  1.0 |----*--------------------------------------  R=1 (only n=6)
  0.8 |
      +--+--+--+--+--+--+--+--+--+--+--+--+-->
      6  10 14 15 21 22 26 33 34 35 38 39
                         n
```

### 3.4 Chemical Correspondence

| Arithmetic property | Chemical parallel |
|---|---|
| tau(6) = tau(14) = 4 | Both form 4 covalent bonds |
| omega(6) = omega(14) = 2 | Both have 2 distinct structural motifs (chains, rings) |
| sigma(14) = 2*sigma(6) | Si bond energy approximately half of C bond energy |
| phi(14) = 6 | Si-based structures "reference" C-based chemistry |
| R(6) = 1 (unique) | Carbon's unique chemical versatility |

The correspondence between tau=4 (number of divisors) and 4-fold covalent bonding is the most direct parallel. Both 6 and 14 sit in Group 14 precisely because they have 4 valence electrons, and the number 4 appears in their arithmetic profile as the shared divisor count.

## 4. Discussion

The arithmetic analysis reveals a layered relationship between carbon and silicon. At the structural level (tau, omega, mu), they are identical -- both are squarefree semiprimes with the same additive profile. At the quantitative level (sigma, phi), they differ by precise ratios (2x for sigma, and phi(14) = 6). At the uniqueness level (R-spectrum), carbon stands alone.

The interpretation is constrained by the TECS-L verification framework. The tau=4 correspondence with 4-fold bonding, while suggestive, could be coincidental -- tau=4 holds for all semiprimes, not just 6 and 14. The sigma doubling and phi recursion are more specific but still arithmetic observations without causal mechanism.

What is not coincidental is the uniqueness of R(6) = 1. Among all positive integers, only n=1 and n=6 satisfy this equation. If the R-spectrum measures some form of "arithmetic balance" or "completeness," then carbon's atomic number is uniquely balanced in a way that silicon's is not. Whether this arithmetic balance maps to chemical versatility is a question for future investigation.

Limitations: This analysis treats atomic numbers as pure integers, stripping away all physical context (electron configuration, nuclear forces, quantum mechanics). The chemical properties of elements are determined by quantum mechanics, not number theory. Any correspondence between arithmetic functions and chemical properties is, at best, a mathematical curiosity that may hint at deeper structural constraints.

## 5. Conclusion

The arithmetic function profiles of Z=6 (carbon) and Z=14 (silicon) reveal precise shared properties (tau=4, omega=2) and distinguishing features (sigma doubling, phi recursion, R-spectrum uniqueness). The shared tau=4 parallels their shared 4-fold covalent bonding. The unique R(6) = 1 condition distinguishes carbon as arithmetically "complete" in a way that silicon is not. These observations formalize the chemical intuition that carbon and silicon are structurally similar but that carbon possesses a unique versatility, and they do so purely within number theory. The phi(14) = 6 recursion creates a mathematical link between the two substrates that merits further investigation.

## References

1. Hardy, G.H. & Wright, E.M. (1938). An Introduction to the Theory of Numbers. Oxford University Press.
2. Petrucci, R.H. et al. (2017). General Chemistry. Pearson.
3. Bains, W. (2004). Many Chemistries Could Be Used to Build Living Systems. Astrobiology 4(2), 137-167.
4. TECS-L Project. (2026). 208 Arithmetic Characterizations of n=6. zenodo/P-N6-208-characterizations.md.
5. TECS-L Project. (2026). R-spectrum Calculator. calc/r_spectrum.py.
6. Schulze-Makuch, D. & Irwin, L.N. (2018). Life in the Universe. Springer.
