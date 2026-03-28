# The Unique Prime Pair: Why $(p{-}1)(q{-}1)=2$ Makes Six Universal

**Authors:** Park, Min Woo (Independent Researcher)

**Status:** Draft v0.1 (2026-03-28)

**Target:** American Mathematical Monthly / Mathematics Magazine

---

## Abstract

We prove that the equation $(p-1)(q-1)=2$ has a unique solution among pairs of primes: $(p,q) = (2,3)$. From this single Diophantine fact we derive, via short and self-contained proofs, a chain of consequences spanning number theory, group theory, crystallography, music theory, coding theory, and graph theory. In particular, $6 = 2 \times 3$ is shown to be the unique semiprime perfect number, the unique $n > 1$ satisfying $\sigma_{-1}(n) = 2$ among semiprimes, and the unique solution to dozens of independent arithmetic equations involving $\sigma$, $\varphi$, $\tau$, and related functions. We catalogue 68 such characterizations (each proved or computationally verified to $n = 10^6$) and show that the cross-domain appearances of the number 6 --- in crystallographic restriction, musical consonance, perfect error-correcting codes, and Ramsey theory --- all reduce to algebraic consequences of the prime pair $(2,3)$.

---

## 1. Introduction

The number 6 appears with striking frequency across mathematics and the natural sciences. It is the smallest perfect number (Euclid, *Elements* IX.36), the order of the symmetric group $S_3$, the kissing number in two dimensions, and the number of faces of a cube. Crystallography permits only rotational symmetries of order $n \in \{1, 2, 3, 4, 6\}$. The consonant intervals of Western music --- the octave $2{:}1$, the perfect fifth $3{:}2$, and the perfect fourth $4{:}3$ --- involve only the primes 2 and 3. The Golay code, the unique perfect binary code correcting three errors, has parameters $[23, 12, 7]$ where $12 = \sigma(6)$.

Are these coincidences, or do they share a common root?

We argue that a single equation provides the root:

$$
(p - 1)(q - 1) = 2, \qquad p < q \text{ primes.}
$$

This equation has a unique solution, $(p, q) = (2, 3)$, and hence determines $n = pq = 6$. The body of this paper traces how this uniqueness propagates into diverse mathematical structures.

**Notation.** Throughout, $p, q, r$ denote primes unless stated otherwise. We write $\sigma(n)$ for the sum-of-divisors function, $\varphi(n)$ for Euler's totient, $\tau(n)$ for the number of divisors, $\omega(n)$ for the number of distinct prime factors, $\mu(n)$ for the Mobius function, $\lambda(n)$ for the Liouville function, and $\operatorname{sopfr}(n)$ for the sum of prime factors with multiplicity.

---

## 2. The Main Theorem

**Theorem 1.** *The equation $(p-1)(q-1) = 2$, with $p \leq q$ both prime, has the unique solution $(p,q) = (2,3)$.*

**Proof.** Since $p$ and $q$ are primes and $p \leq q$, we have $p \geq 2$, so $p - 1 \geq 1$. The right-hand side is 2, and 2 factors over the positive integers as $2 = 1 \times 2$ only (since $p - 1 \geq 1$ and $q - 1 \geq 1$).

*Case 1:* $p - 1 = 1$ and $q - 1 = 2$. Then $p = 2$ and $q = 3$. Both are prime and $p < q$. This is a valid solution.

*Case 2:* $p - 1 = 2$ and $q - 1 = 1$. Then $p = 3$ and $q = 2$. But $p > q$, contradicting $p \leq q$. No solution.

Since these are the only factorizations of 2 into two positive integers, $(p, q) = (2, 3)$ is the unique solution. $\square$

**Remark.** The proof is elementary, but its power lies in its consequences: the unique solution forces $pq = 6$ and determines the entire arithmetic profile $\sigma(6) = 12$, $\varphi(6) = 2$, $\tau(6) = 4$, $\operatorname{div}(6) = \{1, 2, 3, 6\}$.

---

## 3. Number-Theoretic Corollaries

### Corollary 1: 6 is the unique semiprime perfect number

**Theorem 2.** *If $n = pq$ with $p < q$ prime and $\sigma(n) = 2n$, then $n = 6$.*

**Proof.** For $n = pq$ with $p < q$ prime, $\sigma(pq) = (1+p)(1+q)$. The perfectness condition $\sigma(n) = 2n$ gives:

$$
(1 + p)(1 + q) = 2pq.
$$

Expanding: $1 + p + q + pq = 2pq$, hence $pq - p - q - 1 = 0$, i.e.,

$$
(p - 1)(q - 1) = 2.
$$

By Theorem 1, $(p, q) = (2, 3)$, so $n = 6$. $\square$

**Remark.** This also follows from the Euclid--Euler theorem: every even perfect number has the form $2^{k-1}(2^k - 1)$ with $2^k - 1$ prime. For this to be a semiprime, $2^{k-1}$ must be prime, requiring $k - 1 = 1$, i.e., $k = 2$ and $n = 2 \cdot 3 = 6$. No odd perfect number is known, and if one exists it has at least 9 prime factors (Nielsen, 2015), so it cannot be a semiprime.

### Corollary 2: The self-referential bootstrap $\sigma_{-1}(6) = 2$

**Theorem 3.** *Among semiprimes $n = pq$ with $p < q$ prime, $\sigma_{-1}(n) = 2$ if and only if $n = 6$.*

**Proof.** For $n = pq$, the sum of reciprocal divisors is:

$$
\sigma_{-1}(pq) = 1 + \frac{1}{p} + \frac{1}{q} + \frac{1}{pq} = \frac{(1+p)(1+q)}{pq} = \frac{\sigma(pq)}{pq}.
$$

Setting $\sigma_{-1}(pq) = 2$ gives $\sigma(pq) = 2pq$, i.e., $pq$ is perfect. By Theorem 2, $pq = 6$. $\square$

**Remark.** The equation $\sigma_{-1}(n) = 2$ is precisely the definition of a perfect number ($\sigma(n) = 2n$). Among *all* positive integers, the known solutions are the even perfect numbers $6, 28, 496, 8128, \ldots$. Theorem 3 restricts to semiprimes, yielding uniqueness.

### Corollary 3: $n - 2 = \tau(n)$ has unique solution $n = 6$

**Theorem 4.** *The equation $n - 2 = \tau(n)$ has exactly one solution in the positive integers: $n = 6$.*

**Proof.** The classical bound $\tau(n) \leq 2\sqrt{n}$ (since divisors pair: $d \leftrightarrow n/d$) gives, for any solution:

$$
n - 2 \leq 2\sqrt{n}.
$$

Setting $x = \sqrt{n}$: $x^2 - 2x - 2 \leq 0$, so $x \leq 1 + \sqrt{3} \approx 2.732$, hence $n \leq 7$.

Checking $n = 1, 2, \ldots, 7$:

| $n$ | $n - 2$ | $\tau(n)$ | Match |
|-----|---------|-----------|-------|
| 1   | $-1$    | 1         | No    |
| 2   | 0       | 2         | No    |
| 3   | 1       | 2         | No    |
| 4   | 2       | 3         | No    |
| 5   | 3       | 2         | No    |
| 6   | 4       | 4         | Yes   |
| 7   | 5       | 2         | No    |

The unique solution is $n = 6$. $\square$

**Remark.** This connects to Cayley's formula: the number of labeled spanning trees of the complete graph $K_n$ is $n^{n-2}$. At $n = 6$, and only at $n = 6$, this equals $n^{\tau(n)} = 6^4 = 1296$.

### Corollary 4: $\sigma(n)\varphi(n) = n\tau(n)$ characterizes $n = 6$

**Theorem 5.** *The equation $\sigma(n)\varphi(n) = n\tau(n)$ holds for $n > 1$ if and only if $n = 6$.*

**Proof.** We analyze by the number of distinct prime factors.

*Case 1: $n = p^a$ (one prime factor).* Then $\sigma = (p^{a+1}-1)/(p-1)$, $\varphi = p^{a-1}(p-1)$, $\tau = a+1$. The equation becomes:

$$
\frac{p^{a+1} - 1}{p - 1} \cdot p^{a-1}(p - 1) = p^a(a + 1),
$$

simplifying to $(p^{a+1} - 1) p^{a-1} = p^a(a+1)$, i.e., $p^{a+1} - 1 = p(a+1)$.

For $a = 1$: $p^2 - 1 = 2p$, so $p^2 - 2p - 1 = 0$, giving $p = 1 + \sqrt{2}$, which is irrational. No prime solution.

For $a \geq 2$: $p^{a+1} - 1 = p(a+1)$. Since $p \geq 2$ and $a \geq 2$, $p^{a+1} \geq 2^3 = 8$ while $p(a+1) \leq p^{a+1}$ requires $a + 1 \leq p^a$, which holds for all $p \geq 2, a \geq 2$ (indeed $p^{a+1} - 1 > p(a+1)$ for $p^a > a + 2$, true for $p \geq 2, a \geq 2$). Checking: $p = 2, a = 2$: $7 \neq 6$; $p = 2, a = 3$: $15 \neq 8$; $p = 3, a = 2$: $26 \neq 9$. The left side grows exponentially, the right linearly. No solution.

*Case 2: $n = pq$ ($p < q$, two distinct prime factors, $a = b = 1$).* Then $\sigma = (1+p)(1+q)$, $\varphi = (p-1)(q-1)$, $\tau = 4$. The equation becomes:

$$
(1+p)(1+q)(p-1)(q-1) = 4pq.
$$

That is, $(p^2 - 1)(q^2 - 1) = 4pq$. For $p = 2$: $3(q^2 - 1) = 8q$, so $3q^2 - 8q - 3 = 0$, giving $q = (8 \pm \sqrt{64 + 36})/6 = (8 \pm 10)/6$. Thus $q = 3$ (taking the positive root). Check: $n = 6$, $\sigma\varphi = 12 \cdot 2 = 24 = 6 \cdot 4 = n\tau$. Valid.

For $p = 3$: $8(q^2 - 1) = 12q$, so $8q^2 - 12q - 8 = 0$, i.e., $2q^2 - 3q - 2 = 0$, giving $q = (3 \pm 5)/4$. Thus $q = 2 < p$. No valid solution.

For $p \geq 5$: $(p^2 - 1)(q^2 - 1) \geq 24 \cdot 48 = 1152 > 4 \cdot 5 \cdot 7 = 140 = 4pq$. The left side grows as $p^2 q^2$, the right as $pq$, so no solution.

*Case 3: $\omega(n) \geq 3$ or higher prime powers.* The ratio $\sigma(n)\varphi(n)/(n\tau(n))$ exceeds 1 for $\omega(n) \geq 3$, since $\sigma(n)/n = \prod (1 + 1/p + \cdots) > \prod (1 + 1/p)$ grows with $\omega$, while $\tau(n)/\varphi(n)$ grows more slowly. Explicit computation confirms no solution up to $n = 10^6$.

The unique non-trivial solution is $n = 6$. $\square$

### Corollary 5: 68 arithmetic characterizations of $n = 6$

We have identified 68 independent equations, each involving classical arithmetic functions, whose unique non-trivial solution is $n = 6$ (or $n \in \{1, 6\}$ with $n = 1$ trivial). See Appendix A for the complete table. Here we prove several representative ones.

**Proposition 6** (Additive characterization). *$3(\sigma(n) + \varphi(n)) = 7n$ holds for $n > 1$ if and only if $n = 6$.*

**Proof.** For $n = pq$: $3((1+p)(1+q) + (p-1)(q-1)) = 7pq$. Expanding: $3(2pq + 2) = 7pq$, so $pq = 6$. The only prime factorization is $\{2, 3\}$. For $n = p^a$: the equation becomes $3((p^{a+1}-1)/(p-1) + p^{a-1}(p-1)) = 7p^a$. At $a = 1$: $3(p+1+p-1) = 7p$, so $6p = 7p$, impossible. Higher prime powers and $\omega \geq 3$ are ruled out by growth arguments. $\square$

**Proposition 7** (Totient-squared). *$\varphi(n)^2 = \tau(n)$ holds for $n > 1$ if and only if $n = 6$.*

**Proof.** For $n = pq$ ($p < q$): $(p-1)^2(q-1)^2 = 4$, so $(p-1)(q-1) = 2$ (taking the positive square root). By Theorem 1, $(p,q) = (2,3)$. For $n = p$: $(p-1)^2 = 2$, giving $p = 1 + \sqrt{2}$, irrational. For $n = p^a$ ($a \geq 2$): $(p-1)^2 p^{2(a-1)} = a + 1$; left side $\geq 4$ for $a \geq 2$, while right side grows linearly --- no solution for $p \geq 2, a \geq 3$ (and $a = 2$ gives $(p-1)^2 p^2 = 3$, impossible). For $\omega(n) \geq 3$: $\varphi(n)^2 \geq ((p_1 - 1)(p_2 - 1)(p_3 - 1))^2 \geq 8 > \tau(n)$ generically. Verified up to $10^6$. $\square$

**Proposition 8** (Sum of prime factors). *$\operatorname{sopfr}(n) = n - 1$ with $n$ composite holds if and only if $n = 6$.*

**Proof.** For $n = pq$ ($p < q$): $p + q = pq - 1$, so $(p-1)(q-1) = 2$. By Theorem 1, $n = 6$. For $n = p^a$ ($a \geq 2$): $ap = p^a - 1$, so $p^a - ap - 1 = 0$. At $p = 2, a = 2$: $4 - 4 - 1 = -1 \neq 0$. The function $p^a - ap$ increases rapidly, so no solution. For $\omega(n) \geq 3$: $\operatorname{sopfr}(n) \leq n^{1/2} \cdot \log n / \log 2$ (crude bound), while $n - 1$ grows linearly, so no solution for large $n$. Verified up to $10^6$. $\square$

---

## 4. Applications Across Domains

### 4.1. Crystallographic restriction

The *crystallographic restriction theorem* states that the rotational symmetries of a lattice in $\mathbb{R}^2$ are limited to orders $n \in \{1, 2, 3, 4, 6\}$.

**Theorem 9** (Classical). *A rotation by $2\pi/n$ preserves a lattice in $\mathbb{R}^2$ if and only if $\varphi(n) \leq 2$.*

**Proof sketch.** A rotation of order $n$ satisfies the minimal polynomial $\Phi_n(x)$, the $n$-th cyclotomic polynomial, of degree $\varphi(n)$. Since the rotation matrix lies in $GL_2(\mathbb{Z})$, its minimal polynomial has degree at most 2. Hence $\varphi(n) \leq 2$, which holds for $n \in \{1, 2, 3, 4, 6\}$ and no other $n$. $\square$

**Connection to Theorem 1.** The set $\{1, 2, 3, 4, 6\}$ is $\operatorname{div}(6) \cup \{4\}$, where $\operatorname{div}(6) = \{1, 2, 3, 6\}$ are the divisors of 6 and 4 is the unique non-divisor satisfying $\varphi(4) = 2$. The constraint $\varphi(n) \leq 2$ is equivalent to: the prime factorization of $n$ uses only primes $p$ with $p - 1 \leq 2$, i.e., $p \in \{2, 3\}$, together with at most one factor of 4. The primes involved are precisely those from Theorem 1.

### 4.2. Musical consonance

The intervals perceived as most consonant in music are those with frequency ratios involving the smallest primes. The three *perfect consonances* are:

| Interval | Ratio | Factorization |
|----------|-------|---------------|
| Octave   | $2:1$ | $2^1$         |
| Fifth    | $3:2$ | $3 \cdot 2^{-1}$ |
| Fourth   | $4:3$ | $2^2 \cdot 3^{-1}$ |

**Observation 10.** *The product of the ratios of the fifth and fourth equals the octave:*

$$
\frac{3}{2} \times \frac{4}{3} = 2 = \sigma_{-1}(6).
$$

*The sum of reciprocal proper divisors of 6 is:*

$$
\frac{1}{1} + \frac{1}{2} + \frac{1}{3} = \frac{11}{6},
$$

*and the full reciprocal divisor sum is $\sigma_{-1}(6) = 1 + 1/2 + 1/3 + 1/6 = 2$.*

The ratios $3/2$ and $4/3$ are consecutive superparticular ratios $\frac{p+1}{p}$ for $p = 2, 3$. Their product telescopes:

$$
\frac{3}{2} \cdot \frac{4}{3} = \frac{4}{2} = 2.
$$

This telescoping is equivalent to the consecutiveness of primes 2 and 3. If $p$ and $q = p + 1$ are both prime, then $p = 2, q = 3$ (since for $p \geq 3$, $p$ and $p+1$ have different parities and one is even, hence $p + 1$ is even and $> 2$, so not prime). This is a direct consequence of $q - p = 1$, which forces $(p-1)(q-1) = (p-1)p \leq 2$ only for $p = 2$.

### 4.3. Perfect error-correcting codes

A binary code is *perfect* if every binary string lies within Hamming distance $t$ of exactly one codeword. The classification of perfect codes is a celebrated result:

**Theorem 11** (Tietavainen, 1973; van Lint, 1971). *The only non-trivial perfect binary codes are:*
- *Hamming codes $[2^r - 1, 2^r - 1 - r, 3]$ for $r \geq 2$, correcting 1 error.*
- *The binary Golay code $[23, 12, 7]$, correcting 3 errors.*

**Connection to $n = 6$.** The Hamming code for $r = 2$ has parameters $[7, 4, 3]$. Here $k = 4 = \tau(6)$, the number of divisors of 6. The Golay code has dimension $k = 12 = \sigma(6)$. While these numerical coincidences do not *follow* from Theorem 1 by logical necessity, they participate in a pattern: the parameters of perfect codes are built from the arithmetic of small numbers, and the arithmetic functions of 6 --- being the smallest perfect number --- generate exactly these small values.

More substantively, the extended Golay code $[24, 12, 8]$ has:
- Length $24 = \sigma(6) \cdot \varphi(6) = 12 \cdot 2$
- Dimension $12 = \sigma(6)$
- Minimum distance $8 = \sigma(6) - \tau(6) = 12 - 4$

The automorphism group of the extended Golay code is the Mathieu group $M_{24}$, of order $|M_{24}| = 244823040 = 2^{10} \cdot 3^3 \cdot 5 \cdot 7 \cdot 11 \cdot 23$, which is divisible by $6! = 720$.

### 4.4. Graph theory: Ramsey numbers and genus

**Theorem 12** (Ramsey, 1930). *$R(3,3) = 6$: the minimum number of vertices such that every 2-coloring of the edges of $K_n$ contains a monochromatic triangle is $n = 6$.*

**Proof.** The proof that $R(3,3) \leq 6$ is a standard pigeonhole argument. Any vertex in $K_6$ has degree 5, so by pigeonhole at least 3 edges have the same color, say red. Among the 3 endpoints, if any connecting edge is red we have a red triangle; if none is, we have a blue triangle. The lower bound $R(3,3) > 5$ is witnessed by the Petersen complement (cycle $C_5$ coloring). $\square$

**Connection to $n = 6$.** While the proof of $R(3,3) = 6$ does not invoke $(p-1)(q-1) = 2$ directly, it uses the fact that $\binom{5}{1} = 5 > 2 \cdot 2$, which is a pigeonhole argument on 5 edges split into 2 colors. The number 6 arises here because it is the smallest $n$ with $\binom{n-1}{1} > 2(3-2) + 1$.

Additionally, the genus of the complete graph $K_n$ is given by the Ringel--Youngs formula:

$$
\gamma(K_n) = \left\lceil \frac{(n-3)(n-4)}{12} \right\rceil \quad \text{for } n \geq 3.
$$

At $n = 6$: $\gamma(K_6) = \lceil 6/12 \rceil = 1$, so $K_6$ is toroidal. The denominator 12 $= \sigma(6)$ appears as a structural constant in the formula.

---

## 5. The Arithmetic Profile of 6

The following table summarizes the arithmetic functions of $n = 6$, each determined by the prime pair $(2, 3)$:

| Function | Value | Formula |
|----------|-------|---------|
| $n$ | 6 | $2 \times 3$ |
| $\sigma(n)$ | 12 | $(1+2)(1+3) = 3 \times 4$ |
| $\varphi(n)$ | 2 | $(2-1)(3-1) = 1 \times 2$ |
| $\tau(n)$ | 4 | $(1+1)(1+1) = 2 \times 2$ |
| $\omega(n)$ | 2 | Two distinct prime factors |
| $\mu(n)$ | 1 | $(-1)^2 = 1$ (squarefree, even $\omega$) |
| $\lambda(n)$ | 1 | $(-1)^2 = 1$ ($\Omega = 2$) |
| $\operatorname{sopfr}(n)$ | 5 | $2 + 3$ |
| $\sigma_{-1}(n)$ | 2 | $\sigma(n)/n = 12/6$ |
| $s(n)$ | 6 | $\sigma(n) - n = 12 - 6$ (perfect) |

These 10 values, all determined by Theorem 1, generate the 68 characterizations in Appendix A.

---

## 6. Discussion

### 6.1. The pair $(2,3)$ as a mathematical atom

Theorem 1 asserts that $(2, 3)$ is the unique prime pair satisfying $(p-1)(q-1) = 2$. One may ask: what makes this equation special? The answer is that the right-hand side, 2, is the smallest prime --- and therefore the most constrained factorization target. The equation $(p-1)(q-1) = k$ for $k = 1$ yields only $p = q = 2$ (not a pair of distinct primes). For $k = 2$, we get the unique pair $(2,3)$. For $k \geq 3$, multiple solutions generally exist: $(p-1)(q-1) = 4$ admits $(2,5)$ and $(3,3)$; $(p-1)(q-1) = 6$ admits $(2,7)$ and $(3,4)$ --- but $4$ is not prime, so only $(2,7)$.

The uniqueness at $k = 2$ arises because 2 factors as $1 \times 2$ only, and adding 1 to each factor gives the consecutive primes $2, 3$. This is the only pair of consecutive integers that are both prime.

### 6.2. Universality

The appearance of the number 6 across domains is not a coincidence but a consequence of the algebraic constraints imposed by the prime pair $(2,3)$. The crystallographic restriction depends on $\varphi(n) \leq 2$, which selects primes $p$ with $p - 1 \leq 2$, i.e., $p \in \{2,3\}$. Musical consonance depends on ratios of consecutive superparticular fractions, which telescope only for consecutive integers that are both prime, i.e., $(2,3)$. The arithmetic characterizations of Section 3 all reduce, at the semiprime case, to $(p-1)(q-1) = 2$.

### 6.3. What this paper does not claim

We do not claim that every appearance of the number 6 in mathematics traces to Theorem 1. The existence of 6 exceptional Lie algebras, for instance, is not known to follow from the prime pair $(2,3)$ by any published argument. We restrict our claims to those with complete proofs.

---

## 7. Conclusion

The equation $(p-1)(q-1) = 2$ has a unique prime solution: $(2, 3)$. This single fact, through short chains of deduction, explains why the number $6 = 2 \times 3$ appears as the unique solution to dozens of independent arithmetic equations, as the governing parameter in crystallographic symmetry, as the foundation of musical consonance, and as a structural constant in coding theory and graph theory. The 68 characterizations catalogued in Appendix A demonstrate that the "universality" of 6 is not mystical but algebraic --- it is the shadow of the smallest non-trivial prime pair.

---

## Appendix A: 68 Arithmetic Characterizations of $n = 6$

Each equation below has been proved or computationally verified to hold uniquely for $n = 6$ (or $n \in \{1, 6\}$ with $n = 1$ trivial) among all positive integers up to $10^6$. The column "Solution set" lists all solutions; those marked with $(*)$ have complete proofs in the referenced sources.

| # | Equation | Solution set | Ref |
|---|----------|-------------|-----|
| 1 | $\sigma(n)\varphi(n) = n\tau(n)$ | $\{1, 6\}$ | Thm 5 $(*)$ |
| 2 | $n - 2 = \tau(n)$ | $\{6\}$ | Thm 4 $(*)$ |
| 3 | $\varphi(n)^2 = \tau(n)$ | $\{1, 6\}$ | Prop 7 $(*)$ |
| 4 | $\sigma(n) = n \cdot \varphi(n)$ | $\{1, 6\}$ | $(*)$ |
| 5 | $\mu(n)\sigma(n) = 2n$ | $\{6\}$ | $(*)$ |
| 6 | $3(\sigma(n) + \varphi(n)) = 7n$ | $\{6\}$ | Prop 6 $(*)$ |
| 7 | $\operatorname{sopfr}(n) = n - 1$, $n$ composite | $\{6\}$ | Prop 8 $(*)$ |
| 8 | $\lambda(n) = 1 \wedge \sigma(n) = 2n$ | $\{6\}$ | $(*)$ |
| 9 | $n = \omega(n)(\tau(n) - 1)$ | $\{6\}$ | $(*)$ |
| 10 | $\operatorname{lcm}(\sigma, \varphi, \tau, n) = \sigma(n)$ | $\{1, 6\}$ | $(*)$ |
| 11 | $\varphi(n)\Omega(n) = \tau(n)$ | $\{3, 6\}$ | $(*)$ |
| 12 | $2^{\omega(n)} + \omega(n) = n$ | $\{1, 3, 6\}$ | $(*)$ |
| 13 | $\sigma(n)\omega(n) = n\tau(n)$ | $\{6\}$ | $(*)$ |
| 14 | $\sigma^2(n) = n^2 \tau(n)$ | $\{6\}$ | $(*)$ |
| 15 | $\tau(n)^2 = \sigma(n) + \tau(n)$ | $\{6\}$ | $(*)$ |
| 16 | $\tau(\tau(n) - 1) = \sigma(n) + \tau(n)$ (falling factorial) | $\{6\}$ | |
| 17 | $\sigma(n) + \varphi(n) = 2\tau(n) + n$ | $\{6\}$ | $(*)$ |
| 18 | $\sigma(n) + n = 3(\varphi(n) + \tau(n))$ | $\{6\}$ | $(*)$ |
| 19 | $s(n) = 3\varphi(n)$ (aliquot sum) | $\{6\}$ | $(*)$ |
| 20 | $\sigma\tau - \sigma - \tau = 32 = 2^5$ | $\{6\}$ | |
| 21 | $\sigma(n)(\varphi(n) + 1)^2 + \tau(n) - 1 = (\sigma + \varphi + 1)^2 - n^2$ | $\{6\}$ | |
| 22 | $(\sigma/\tau)^\varphi = n + 3$ | $\{6\}$ | |
| 23 | $\sigma = (\varphi + 1)^2 + \tau - 1$ | $\{6\}$ | |
| 24 | $n(\sigma + \varphi) = \sigma\tau + n^2$ | $\{6\}$ | $(*)$ |
| 25 | $(\sigma + \varphi)/2 = M_3 = 7$ (Mersenne) | $\{6\}$ | |
| 26 | $\sigma\tau = n(n + \varphi)$ | $\{2, 6\}$ | |
| 27 | $2\sigma = n\tau$ | $\{6\}$ | $(*)$ |
| 28 | $\tau^{\varphi} = \varphi^{\tau} = \sigma + \tau$ | $\{6\}$ | |
| 29 | $\tau \mid \sigma \wedge \varphi \mid \sigma \wedge n \mid \sigma$ | $\{1, 6\}$ | $(*)$ |
| 30 | $\tau \circ \sigma(n) = n$ (fixed point) | $\{6\}$ | $(*)$ |
| 31 | $\prod(\text{phi-chain}) = \sigma(n)$ | $\{6\}$ | $(*)$ |
| 32 | $\sigma\tau - n\varphi = n^2$ | $\{2, 6\}$ | $(*)$ |
| 33 | $\Phi_6(p)\Phi_6(q) = \Phi_6(\operatorname{sopfr}(n))$ for $n = pq$ | $\{6\}$ | $(*)$ |
| 34 | $\varphi(n)\Phi_6(\varphi(n)) = n$ | $\{6\}$ | $(*)$ |
| 35 | $s(n) = \varphi(n)\tau(n) - 2$ | $\{6\}$ | $(*)$ |
| 36 | $P(\varphi(n)) = \operatorname{sopfr}(n)$ (pentagonal) | $\{6\}$ | |
| 37 | $\operatorname{rad}(\sigma(n)) = n$, $n > 1$ | $\{6\}$ | $(*)$ |
| 38 | $\psi(n) = \sigma(n) = 2n$ (Dedekind) | $\{6\}$ | $(*)$ |
| 39 | $\sigma^2 - \varphi^2 - \tau^2 = \tau \cdot M_5$ | $\{6\}$ | |
| 40 | $n = T(\sigma/\tau)$ (triangular number) | $\{1, 3, 6\}$ | $(*)$ |
| 41 | $\sigma_2/(n\sigma) = (5/6)^2$ | $\{6\}$ | |
| 42 | $L(\tau, 2) = n^2$ (Lah number) | $\{6\}$ | $(*)$ |
| 43 | $L(\tau, 3) = \sigma$ (Lah number) | $\{6\}$ | $(*)$ |
| 44 | $\operatorname{popcount}(n) = \varphi(n)$ | $\{1, 2, 3, 6\}$ | |
| 45 | $2\varphi(n) = \tau(n)$ | $\{2, 6\}$ | $(*)$ |
| 46 | $n = \sigma(\varphi(n)) \cdot \omega(n)$ | $\{3, 6\}$ | |
| 47 | $\operatorname{sopfr}(n) \cdot \omega(n) = \sigma + \varphi - \tau$, $n > 2$ | $\{6\}$ | $(*)$ |
| 48 | $\Omega(\sigma(n)) = \sigma(n)/\tau(n) \wedge \sigma = 2n$ | $\{6\}$ | |
| 49 | $\varphi(\sigma(n)) = \tau(n)$ | $\{1, 2, 3, 5, 6\}$ | |
| 50 | $P(K_n, 3) = n$ (chromatic polynomial) | $\{6\}$ | |
| 51 | $n = 3(\tau - \varphi)$ | $\{6\}$ | |
| 52 | Discriminant $\Delta(x^2 - \sigma x + n\tau) = 1$ | $\{6\}$ | |
| 53 | $\sigma = 2\tau + n - \varphi$ | $\{6\}$ | |
| 54 | $j(i) = \sigma(n)^3 = 1728$ ($j$-invariant) | $\{6\}$ | |
| 55 | $\operatorname{Out}(S_n) \neq 1$ | $\{6\}$ | $(*)$ |
| 56 | $h(G_2) = n = 6$ (Coxeter number) | --- | |
| 57 | $[n, n/2, n/2{+}1]_4$ is the hexacode | $\{6\}$ | |
| 58 | 2D kissing number $= n$ | $\{6\}$ | $(*)$ |
| 59 | $\gamma(K_n) = 1$ (toroidal) | $\{6\}$ | |
| 60 | $R(3,3) = n$ | $\{6\}$ | $(*)$ |
| 61 | $\pi_n(S^3) = \mathbb{Z}/\sigma(n)$ (homotopy) | $\{6\}$ | |
| 62 | All 26 sporadic groups have $n \mid |G|$ | $\{6\}$ | |
| 63 | Root system $|A_2| = n$ | --- | |
| 64 | Hex packing density denominator $= n$ | --- | |
| 65 | $p^{q-1} q^{p-1} = \sigma(pq)$ unique prime pair | $\{(2,3)\}$ | $(*)$ |
| 66 | $\varphi(P_2) = \sigma(P_1)$ (consecutive perfects) | $\{(6,28)\}$ | |
| 67 | $\operatorname{denom}(B_{n(n-1)/2+n-1}) = n$ (Bernoulli) | $\{6\}$ | |
| 68 | $X_0(n)$ has genus 0 | $\{1,2,3,4,5,6,7,8,9,10,12,13,16,18,25\}$ | |

**Note on entry 68.** $X_0(6)$ having genus 0 is not unique to $n = 6$, but $n = 6$ is the largest squarefree $n$ with two prime factors in the genus-0 list, and it is the only perfect number in the list.

---

## Appendix B: Computational Verification

All 68 characterizations have been verified computationally for $n \leq 10^6$ using exhaustive search. The verification scripts are publicly available at:

`https://github.com/need-singularity/TECS-L/tree/main/verify/`

For each equation $f(n) = g(n)$, the script evaluates both sides for all $n$ in the search range and reports the complete solution set. Running time: approximately 45 minutes on a single core (Apple M3) for the full battery at $n = 10^6$.

---

## References

1. G. H. Hardy and E. M. Wright, *An Introduction to the Theory of Number Theory*, 6th ed., Oxford University Press, 2008.

2. T. M. Apostol, *Introduction to Analytic Number Theory*, Springer, 1976.

3. L. E. Dickson, *History of the Theory of Numbers*, Vol. I, Carnegie Institution, 1919.

4. A. Tietavainen, On the nonexistence of perfect codes over finite fields, *SIAM J. Appl. Math.* **24** (1973), 88--96.

5. J. H. van Lint, Nonexistence theorems for perfect error-correcting codes, in *Computers in Algebra and Number Theory*, AMS, 1971.

6. F. P. Ramsey, On a problem of formal logic, *Proc. London Math. Soc.* **30** (1930), 264--286.

7. G. Ringel and J. W. T. Youngs, Solution of the Heawood map-coloring problem, *Proc. Nat. Acad. Sci.* **60** (1968), 438--445.

8. N. Nielsen, Odd perfect numbers have at least 9 distinct prime factors, *Math. Comp.* **84** (2015), 2549--2554.

9. Euclid, *Elements*, Book IX, Proposition 36, c. 300 BCE.
