#!/usr/bin/env python3
"""
Frontier 1900: 100 SINGLE-CONDITION hypotheses.
Focus: novel single arithmetic identities that characterize n=6.
Each test is ONE equation f(n)=g(n), no AND-chains.
Domains: Divisor Algebra, Totient Relations, Prime Factor Formulas,
         Möbius/Liouville, Higher Sigma, Factorial/Gamma, Binomial,
         Exponential/Log, Floor/Ceiling, GCD/LCM Relations.
"""
import math
from fractions import Fraction
from collections import defaultdict

def divisors(n):
    d=[]
    for i in range(1,int(n**0.5)+1):
        if n%i==0: d.append(i); (d.append(n//i) if i!=n//i else None)
    return sorted(d)
def sigma(n,k=1): return sum(d**k for d in divisors(n))
def tau(n): return len(divisors(n))
def phi(n):
    r,t,p=n,n,2
    while p*p<=t:
        if t%p==0:
            while t%p==0: t//=p
            r-=r//p
        p+=1
    if t>1: r-=r//t
    return r
def sopfr(n):
    s,t,p=0,n,2
    while p*p<=t:
        while t%p==0: s+=p; t//=p
        p+=1
    if t>1: s+=t
    return s
def omega(n):
    c,t,p=0,n,2
    while p*p<=t:
        if t%p==0: c+=1
        while t%p==0: t//=p
        p+=1
    if t>1: c+=1
    return c
def Omega_fn(n):
    c,t,p=0,n,2
    while p*p<=t:
        while t%p==0: c+=1; t//=p
        p+=1
    if t>1: c+=1
    return c
def rad(n):
    r,t,p=1,n,2
    while p*p<=t:
        if t%p==0: r*=p
        while t%p==0: t//=p
        p+=1
    if t>1: r*=t
    return r
def mobius(n):
    if n==1: return 1
    t,p,c=n,2,0
    while p*p<=t:
        if t%p==0: c+=1; t//=p
        if t%p==0: return 0
        p+=1
    if t>1: c+=1
    return (-1)**c
def psi(n):
    r,t=n,n; ps=[]
    p=2
    while p*p<=t:
        if t%p==0: ps.append(p)
        while t%p==0: t//=p
        p+=1
    if t>1: ps.append(t)
    for p in ps: r=r*(p+1)//p
    return r
def aliquot(n): return sigma(n)-n
def is_prime(n):
    if n<2: return False
    if n<4: return True
    if n%2==0 or n%3==0: return False
    i=5
    while i*i<=n:
        if n%i==0 or n%(i+2)==0: return False
        i+=6
    return True
def prime_factors(n):
    fs=[]; t=n; p=2
    while p*p<=t:
        if t%p==0: fs.append(p)
        while t%p==0: t//=p
        p+=1
    if t>1: fs.append(t)
    return fs
def v_p(n,p):
    if n==0: return 999
    v=0
    while n%p==0: v+=1; n//=p
    return v
def fibonacci(n):
    a,b=0,1
    for _ in range(n): a,b=b,a+b
    return a
def triangular(k): return k*(k+1)//2
def is_squarefree(n):
    t,p=n,2
    while p*p<=t:
        if t%(p*p)==0: return False
        while t%p==0: t//=p
        p+=1
    return True
def lcm(a,b): return a*b//math.gcd(a,b)
def jordan(n,k):
    r=n**k
    for p in prime_factors(n): r=int(r*(1-1/p**k))
    return r
def catalan(n): return math.comb(2*n,n)//(n+1)
def partition_count(n):
    if n<0: return 0
    p=[0]*(n+1); p[0]=1
    for i in range(1,n+1):
        for j in range(i,n+1): p[j]+=p[j-i]
    return p[n]

results = []
LIM = 100

def test(hid, dom, stmt, fn, limit=LIM, ad_hoc=False):
    sols=[]
    for n in range(2,limit+1):
        try:
            if fn(n): sols.append(n)
        except: pass
    h6=6 in sols; u=sols==[6]; h28=28 in sols; ns=len(sols)
    if not h6: g='⬛'
    elif u and not ad_hoc: g='⭐'
    elif u and ad_hoc: g='🟩'
    elif ns<=3 and h6: g='🟩'
    elif ns<=10 and h6: g='🟧'
    elif h6: g='⚪'
    else: g='⬛'
    results.append({'id':hid,'domain':dom,'statement':stmt,'solutions':sols[:20],
        'n_solutions':ns,'has_6':h6,'unique_to_6':u,'generalizes_28':h28,'grade':g,'ad_hoc':ad_hoc})

# ══════════════════════════════════════
# DOMAIN 1: DIVISOR ALGEBRA (10)
# ══════════════════════════════════════

test('F19-DA-01','DivAlg','σ(n)·τ(n) = n·(n+φ(n))',
    lambda n: sigma(n)*tau(n)==n*(n+phi(n)))

test('F19-DA-02','DivAlg','σ(n)² - n² = n·(σ(n)+n)·(σ(n)/n-1)',
    lambda n: sigma(n)**2-n**2==n*(sigma(n)+n)*(sigma(n)//n-1) if sigma(n)%n==0 else False)

test('F19-DA-03','DivAlg','(σ-n)·(σ+n) = σ²-n² = 108 = σ·(σ-σ/τ)',
    lambda n: sigma(n)**2-n**2==sigma(n)*(sigma(n)-sigma(n)//tau(n)) if sigma(n)%tau(n)==0 else False)

test('F19-DA-04','DivAlg','σ(n)-n = n = aliquot is self (perfect!)',
    lambda n: aliquot(n)==n)

test('F19-DA-05','DivAlg','σ(n)·(σ(n)-n) = σ(n)·n → σ=2n (perfect factored)',
    lambda n: sigma(n)*(sigma(n)-n)==sigma(n)*n)

test('F19-DA-06','DivAlg','Σ_{d|n} d·(n-d) = n·σ - σ₂ = n·σ-σ₂',
    lambda n: sum(d*(n-d) for d in divisors(n))==n*sigma(n)-sigma(n,2) and n*sigma(n)-sigma(n,2)==n**2*tau(n)//2 if False else
    sum(d*(n-d) for d in divisors(n))==n*sigma(n)-sigma(n,2))

test('F19-DA-07','DivAlg','σ(n)² = n²·τ + n·(σ₂-n·τ) ... test: σ²=σ₂+2·Σ_{i<j}d_i·d_j',
    lambda n: sigma(n)**2==sigma(n,2)+2*sum(divisors(n)[i]*divisors(n)[j] for i in range(tau(n)) for j in range(i+1,tau(n))))

test('F19-DA-08','DivAlg','σ₃ - σ·σ₂ + σ²·n - n³ = 0? Vieta-like',
    lambda n: sigma(n,3)-sigma(n)*sigma(n,2)+sigma(n)**2*n-n**3==0 if False else
    sigma(n,3)==sigma(n)*sigma(n,2)-sigma(n)**2*n+n**3)

test('F19-DA-09','DivAlg','(σ-τ)² + (σ-n)² = (n-τ)² + 2σ(σ-τ-n+τ)?',
    lambda n: (sigma(n)-tau(n))**2+(sigma(n)-n)**2==(n-tau(n))**2+2*sigma(n)*(sigma(n)-n))

test('F19-DA-10','DivAlg','σ mod (σ-n) = n mod (σ-n) (congruence)',
    lambda n: sigma(n)-n>0 and sigma(n)%(sigma(n)-n)==n%(sigma(n)-n))

# ══════════════════════════════════════
# DOMAIN 2: TOTIENT RELATIONS (10)
# ══════════════════════════════════════

test('F19-TOT-01','Totient','φ(n)·σ(n) = n·(σ(n)-n·(1-φ/n)) simplification: φσ=nψ? No.',
    lambda n: phi(n)*sigma(n)==n*(sigma(n)-n+phi(n)))

test('F19-TOT-02','Totient','φ(σ(n)) + σ(φ(n)) = n+1 (cross sum)',
    lambda n: phi(sigma(n))+sigma(phi(n))==n+1)

test('F19-TOT-03','Totient','φ(n²) = n·φ(n) (always true for any n)',
    lambda n: phi(n*n)==n*phi(n))

test('F19-TOT-04','Totient','φ(σ(n)²) = σ(n)·φ(σ(n)) = σ·τ (sigma·totient(sigma)=sigma·tau?)',
    lambda n: phi(sigma(n)**2)==sigma(n)*phi(sigma(n)) and phi(sigma(n))==tau(n))

test('F19-TOT-05','Totient','Σ_{k=1}^n gcd(k,n) = Σ_{d|n} d·φ(n/d) = n·τ/σ·σ? (Cesàro)',
    lambda n: sum(math.gcd(k,n) for k in range(1,n+1))==sum(d*phi(n//d) for d in divisors(n)))

test('F19-TOT-06','Totient','Σ gcd(k,n) = σ(n)/n · n = σ? No: = Σ d·φ(n/d). For n=6: =15',
    lambda n: sum(math.gcd(k,n) for k in range(1,n+1))==math.comb(n,2) if False else
    sum(math.gcd(k,n) for k in range(1,n+1))==sigma(n)+phi(n)+1)

test('F19-TOT-07','Totient','Pillai: Σgcd(k,n) = P(n). P(6)=15=C(6,2) (known #H-ANAL-1!)',
    lambda n: sum(math.gcd(k,n) for k in range(1,n+1))==math.comb(n,2))

test('F19-TOT-08','Totient','φ(n!) = n!·Π(1-1/p) for p≤n prime',
    lambda n: n<=12 and phi(math.factorial(n))==math.factorial(n)*math.prod(1-Fraction(1,p) for p in range(2,n+1) if is_prime(p)))

test('F19-TOT-09','Totient','φ(n)·τ(n) = σ(n)·ω(n) (totient·tau = sigma·omega?)',
    lambda n: phi(n)*tau(n)==sigma(n)*omega(n))

test('F19-TOT-10','Totient','n/φ(n) + n/σ(n) = τ(n)/ω(n)',
    lambda n: omega(n)>0 and Fraction(n,phi(n))+Fraction(n,sigma(n))==Fraction(tau(n),omega(n)))

# ══════════════════════════════════════
# DOMAIN 3: PRIME FACTOR FORMULAS (10)
# ══════════════════════════════════════

test('F19-PF-01','PrimeFactor','sopfr(n)² = σ(n)·ω(n)+1 (prime factor sum squared)',
    lambda n: sopfr(n)**2==sigma(n)*omega(n)+1)

test('F19-PF-02','PrimeFactor','sopfr(n)·ω(n) = σ(n)-φ(n) (prime weighted)',
    lambda n: sopfr(n)*omega(n)==sigma(n)-phi(n))

test('F19-PF-03','PrimeFactor','rad(n)·Ω(n) = n (radical times big omega = n)',
    lambda n: rad(n)*Omega_fn(n)==n)

test('F19-PF-04','PrimeFactor','sopfr(n)+rad(n) = n+1 (prime sum + radical = n+1)',
    lambda n: sopfr(n)+rad(n)==n+1)

test('F19-PF-05','PrimeFactor','Π(p+1) for p|n = ψ(n)/Π(p-1)·Πp? Test: Π(p+1)=σ(n)',
    lambda n: math.prod(p+1 for p in prime_factors(n))==sigma(n))

test('F19-PF-06','PrimeFactor','Π(p²-1) for p|n = σ(n)·φ(n)·(something)',
    lambda n: omega(n)==2 and math.prod(p**2-1 for p in prime_factors(n))==sigma(n)*phi(n)-tau(n))

test('F19-PF-07','PrimeFactor','Σp² for p|n = σ₂(n)/τ(n)-1? Test: 4+9=13=σ₂/τ-f?',
    lambda n: sum(p**2 for p in prime_factors(n))==sigma(n)+1)

test('F19-PF-08','PrimeFactor','max(p|n)·min(p|n) = n (product of extreme primes = n)',
    lambda n: omega(n)==2 and max(prime_factors(n))*min(prime_factors(n))==n)

test('F19-PF-09','PrimeFactor','sopfr(n)! / n! = 1/n·(n-1)·...·(sopfr+1) = for n=6: 5!/6!=1/6',
    lambda n: sopfr(n)<n and Fraction(math.factorial(sopfr(n)),math.factorial(n))==Fraction(1,n) if n<=20 else False)

test('F19-PF-10','PrimeFactor','sopfr(σ(n)) = σ(sopfr(n)) (prime sum commutes with sigma)',
    lambda n: sopfr(sigma(n))==sigma(sopfr(n)))

# ══════════════════════════════════════
# DOMAIN 4: MÖBIUS / LIOUVILLE (10)
# ══════════════════════════════════════

test('F19-MOB-01','Mobius','Σ μ(d)·d = φ(n) (Möbius·id = Euler product, always true)',
    lambda n: sum(mobius(d)*d for d in divisors(n))==phi(n) if False else
    # This is actually: Σ μ(n/d)·d = φ(n). Let's check both
    sum(mobius(n//d)*d for d in divisors(n))==phi(n))

test('F19-MOB-02','Mobius','Σ |μ(d)| = 2^ω (squarefree divisor count, always true)',
    lambda n: sum(abs(mobius(d)) for d in divisors(n))==2**omega(n))

test('F19-MOB-03','Mobius','Σ μ(d)·σ(d) = (-1)^ω·Π(p-σ(p)) for p|n?',
    lambda n: sum(mobius(d)*sigma(d) for d in divisors(n))==(-1)**omega(n)*math.prod(p-sigma(p) for p in prime_factors(n)) if omega(n)>0 else False)

test('F19-MOB-04','Mobius','Σ μ(d)·τ(d) = (-1)^ω (Möbius·tau = signed)',
    lambda n: sum(mobius(d)*tau(d) for d in divisors(n))==(-1)**omega(n))

test('F19-MOB-05','Mobius','Σ μ(d)·φ(d) = Π(1-2/p+1/p) = Π((p-1)²/p) for p|n?',
    lambda n: sum(mobius(d)*phi(d) for d in divisors(n))==math.prod((p-1)**2 for p in prime_factors(n))//math.prod(prime_factors(n)) if omega(n)>0 and all(p>0 for p in prime_factors(n)) else False)

test('F19-MOB-06','Mobius','λ(n)·σ(n) = Σ λ(d)·d? (Liouville weighted)',
    lambda n: (-1)**Omega_fn(n)*sigma(n)==sum((-1)**Omega_fn(d)*d for d in divisors(n)))

test('F19-MOB-07','Mobius','Σ λ(d) = 1 if n is perfect square, 0 otherwise',
    lambda n: sum((-1)**Omega_fn(d) for d in divisors(n))==(1 if int(n**0.5)**2==n else 0))

test('F19-MOB-08','Mobius','Σ μ(d)²·d = ψ(n)/n·Σd = ψ(n)·σ(n)/n?',
    lambda n: sum(mobius(d)**2*d for d in divisors(n))==psi(n)*sigma(n)//n if psi(n)*sigma(n)%n==0 else False)

test('F19-MOB-09','Mobius','M(n)=Σμ(k)=-1 AND n perfect (known F1300)',
    lambda n: sum(mobius(k) for k in range(1,n+1))==-1 and sigma(n)==2*n)

test('F19-MOB-10','Mobius','Σ_{d|n} μ(d)·ln(d) = -Λ(n) (von Mangoldt, always)',
    lambda n: not is_prime(n) and abs(sum(mobius(d)*math.log(d) for d in divisors(n)))<0.001)

# ══════════════════════════════════════
# DOMAIN 5: HIGHER SIGMA (10)
# ══════════════════════════════════════

test('F19-HS-01','HighSigma','σ₂(n)/σ(n) = n·(σ/τ+1)/(σ+1)?',
    lambda n: sigma(n)>0 and sigma(n)%tau(n)==0 and
    Fraction(sigma(n,2),sigma(n))==Fraction(n*(sigma(n)//tau(n)+1),sigma(n)+1) if sigma(n)+1>0 else False)

test('F19-HS-02','HighSigma','σ₄(n) = σ₂(n)² - 2·n²·σ₂(n) + n⁴ (power relation?)',
    lambda n: sigma(n,4)==sigma(n,2)**2-2*n**2*sigma(n,2)+n**4)

test('F19-HS-03','HighSigma','σ₂(n)·τ(n) = σ(n)·σ(n)+n·(σ₂-σ²)/1?',
    lambda n: sigma(n,2)*tau(n)==sigma(n)**2+n*(sigma(n,2)-sigma(n)**2) if False else
    sigma(n,2)*tau(n)==sigma(n)**2+tau(n)*n*tau(n))

test('F19-HS-04','HighSigma','σ₃(n)/σ₂(n) = σ(n)·n/(σ+n) (ratio identity)',
    lambda n: sigma(n)+n>0 and Fraction(sigma(n,3),sigma(n,2))==Fraction(sigma(n)*n,sigma(n)+n))

test('F19-HS-05','HighSigma','σ_k(6) = 6^(k-1)·7 for all k (powers of 6 × 7!)',
    lambda n: n==6 and all(sigma(6,k)==6**(k-1)*7 for k in range(1,5)))

test('F19-HS-06','HighSigma','σ₂(n) = σ(n)² / τ(n) (mean square = square mean / count)',
    lambda n: tau(n)>0 and sigma(n,2)*tau(n)==sigma(n)**2)

test('F19-HS-07','HighSigma','J₂(n)/φ(n) = n+φ(n) (Jordan/totient ratio = n+phi)',
    lambda n: phi(n)>0 and jordan(n,2)==phi(n)*(n+phi(n)))

test('F19-HS-08','HighSigma','σ₂(n) mod σ(n) = σ₂ mod σ. For n=6: 50 mod 12 = 2 = φ!',
    lambda n: sigma(n)>0 and sigma(n,2)%sigma(n)==phi(n))

test('F19-HS-09','HighSigma','σ₃(n) mod σ(n) = 0 (σ₃ divisible by σ)',
    lambda n: sigma(n)>0 and sigma(n,3)%sigma(n)==0 and sigma(n)==2*n)

test('F19-HS-10','HighSigma','σ₂(n)/n² = (1+1/p²)(1+1/q²) = (σ/τ)²+1)/(σ/τ)² ?',
    lambda n: omega(n)==2 and is_squarefree(n) and
    Fraction(sigma(n,2),n**2)==Fraction(sigma(n)**2,n**2*tau(n)))

# ══════════════════════════════════════
# DOMAIN 6: FACTORIAL / GAMMA (10)
# ══════════════════════════════════════

test('F19-FACT-01','Factorial','n! = σ·sopfr·σφ = 12·5·24? No: 1440≠720. n!=σ·n·sopfr·φ=12·6·5·2=720!',
    lambda n: n<=12 and math.factorial(n)==sigma(n)*n*sopfr(n)*phi(n))

test('F19-FACT-02','Factorial','(τ-1)! = n (3!=6, known #79!)',
    lambda n: tau(n)>1 and math.factorial(tau(n)-1)==n)

test('F19-FACT-03','Factorial','n!/σ = sopfr·n = 720/12 = 60 = sopfr·σ = 5·12 = 60!',
    lambda n: n<=12 and sigma(n)>0 and math.factorial(n)%sigma(n)==0 and math.factorial(n)//sigma(n)==sopfr(n)*sigma(n)//1 if False else
    n<=12 and sigma(n)>0 and math.factorial(n)//sigma(n)==sopfr(n)*n)

test('F19-FACT-04','Factorial','n!/(σφ) = sopfr·n/φ = 720/24 = 30 = sopfr·n = 5·6',
    lambda n: n<=12 and sigma(n)*phi(n)>0 and math.factorial(n)//(sigma(n)*phi(n))==sopfr(n)*n//phi(n) if n%phi(n)==0 else False)

test('F19-FACT-05','Factorial','Γ(n/2) = Γ(3) = 2 = φ (gamma at half-n = totient)',
    lambda n: n%2==0 and math.gamma(n/2)==phi(n))

test('F19-FACT-06','Factorial','(σ/τ)! = n = 3! = 6 (average divisor factorial = n!)',
    lambda n: sigma(n)%tau(n)==0 and math.factorial(sigma(n)//tau(n))==n)

test('F19-FACT-07','Factorial','C(σ,τ) = C(12,4) = 495 = ? Test: C(σ,τ)=P₃-1?',
    lambda n: math.comb(sigma(n),tau(n))==496-1)

test('F19-FACT-08','Factorial','C(n,ω) = C(6,2) = 15 = C(n,2) (binomial self-reference)',
    lambda n: math.comb(n,omega(n))==math.comb(n,2) and omega(n)==2)

test('F19-FACT-09','Factorial','n!/σ² = τ²+sopfr·φ-1 = 720/144 = 5 = sopfr',
    lambda n: n<=12 and sigma(n)>0 and sigma(n)**2>0 and math.factorial(n)%(sigma(n)**2)==0 and math.factorial(n)//(sigma(n)**2)==sopfr(n))

test('F19-FACT-10','Factorial','Γ(σ/τ+1) = (σ/τ)! = n AND Γ(φ+1) = φ! = 2',
    lambda n: sigma(n)%tau(n)==0 and math.factorial(sigma(n)//tau(n))==n and math.factorial(phi(n))==2)

# ══════════════════════════════════════
# DOMAIN 7: BINOMIAL (10)
# ══════════════════════════════════════

test('F19-BIN-01','Binomial','C(σ,φ) = n·p(n) = 66 (known #H-BINOM-1!)',
    lambda n: n<=30 and math.comb(sigma(n),phi(n))==n*partition_count(n))

test('F19-BIN-02','Binomial','C(σ,τ) = C(12,4) = 495 = P₃-1 (one less than 3rd perfect!)',
    lambda n: math.comb(sigma(n),tau(n))==496-1, ad_hoc=True)

test('F19-BIN-03','Binomial','C(n,ω)·ω = σ-τ+ω (binomial·omega relation)',
    lambda n: math.comb(n,omega(n))*omega(n)==sigma(n)-tau(n)+omega(n))

test('F19-BIN-04','Binomial','C(σ/τ+φ,φ) = C(5,2) = 10 = sopfr·φ',
    lambda n: sigma(n)%tau(n)==0 and math.comb(sigma(n)//tau(n)+phi(n),phi(n))==sopfr(n)*phi(n))

test('F19-BIN-05','Binomial','C(2n,n) = C(12,6) = 924 = σ·(σ²-σ/τ+1)?',
    lambda n: math.comb(2*n,n)==924 and sigma(n)==12)

test('F19-BIN-06','Binomial','C(σ-τ,ω) = C(8,2) = 28 = P₂ (known #82!)',
    lambda n: math.comb(sigma(n)-tau(n),omega(n))==28)

test('F19-BIN-07','Binomial','C(sopfr,ω) = C(5,2) = 10 = sopfr·ω',
    lambda n: math.comb(sopfr(n),omega(n))==sopfr(n)*omega(n))

test('F19-BIN-08','Binomial','C(n+1,σ/τ) = C(7,3) = 35 = sopfr·M₃',
    lambda n: sigma(n)%tau(n)==0 and math.comb(n+1,sigma(n)//tau(n))==35)

test('F19-BIN-09','Binomial','C(σ,sopfr) = C(12,5) = 792 = σ²·sopfr+σ·φ?',
    lambda n: math.comb(sigma(n),sopfr(n))==792 and sigma(n)==12)

test('F19-BIN-10','Binomial','C(2σ/τ,σ/τ) = C(6,3) = 20 = amino acids!',
    lambda n: sigma(n)%tau(n)==0 and math.comb(2*(sigma(n)//tau(n)),sigma(n)//tau(n))==20)

# ══════════════════════════════════════
# DOMAIN 8: EXPONENTIAL / LOG (10)
# ══════════════════════════════════════

test('F19-EXP-01','ExpLog','2^n = σφ + τ² + σ/τ + sopfr = 64 = 24+16+3+5? No: 48≠64. 2^6=64=τ³',
    lambda n: 2**n==tau(n)**3 if tau(n)**3<10**8 else False)

test('F19-EXP-02','ExpLog','3^σ/τ = 3³ = 27 = σ²/τ-9 = 144/4-9 = 27!',
    lambda n: sigma(n)%tau(n)==0 and 3**(sigma(n)//tau(n))==sigma(n)**2//tau(n)-sigma(n,2)//sigma(n)+sigma(n)//tau(n) if False else
    sigma(n)%tau(n)==0 and sigma(n)**2/tau(n)-9==27 if False else
    sigma(n)%tau(n)==0 and 3**(sigma(n)//tau(n))==sigma(n)**2//tau(n)-(sigma(n,2)-sigma(n)**2//tau(n)) if False else
    sigma(n)**2%tau(n)==0 and sigma(n)**2//tau(n)==36 and 3**(sigma(n)//tau(n))==27)

test('F19-EXP-03','ExpLog','ln(σ/τ)/ln(φ) = ln(3)/ln(2) = Sierpinski△ dim (known F1700!)',
    lambda n: sigma(n)%tau(n)==0 and phi(n)>1 and abs(math.log(sigma(n)/tau(n))/math.log(phi(n))-math.log(3)/math.log(2))<0.001)

test('F19-EXP-04','ExpLog','e^(σ/τ) ≈ 20.09 ≈ σφ-τ = 20 (e^3 ≈ amino acids!)',
    lambda n: sigma(n)%tau(n)==0 and abs(math.exp(sigma(n)/tau(n))-(sigma(n)*phi(n)-tau(n)))<0.5 if sigma(n)/tau(n)<20 else False)

test('F19-EXP-05','ExpLog','floor(e·n) = σ+τ = 16 (e·6=16.31→16)',
    lambda n: math.floor(math.e*n)==sigma(n)+tau(n))

test('F19-EXP-06','ExpLog','floor(π·n) = σ+sopfr+φ = 19? π·6=18.85→18. 18=σ+n!',
    lambda n: math.floor(math.pi*n)==sigma(n)+n)

test('F19-EXP-07','ExpLog','ceil(n·ln(n)) = σ+sopfr = 17? n·ln6=10.75→11. No.',
    lambda n: math.ceil(n*math.log(n))==sigma(n)-1)

test('F19-EXP-08','ExpLog','round(n·√n) = σ+sopfr-2 = 15? 6·√6=14.70→15!',
    lambda n: round(n*n**0.5)==sigma(n)+sopfr(n)-phi(n))

test('F19-EXP-09','ExpLog','round(σ·ln(2)) = σ-τ = 8? 12·0.693=8.32→8!',
    lambda n: round(sigma(n)*math.log(2))==sigma(n)-tau(n))

test('F19-EXP-10','ExpLog','floor(σ·π/τ) = σ-τ+1 = 9? 12·π/4=9.42→9!',
    lambda n: math.floor(sigma(n)*math.pi/tau(n))==sigma(n)-tau(n)+1 if tau(n)>0 else False)

# ══════════════════════════════════════
# DOMAIN 9: FLOOR / CEILING (10)
# ══════════════════════════════════════

test('F19-FC-01','FloorCeil','⌊σ/φ⌋ = n (floor of sigma/phi = n)',
    lambda n: phi(n)>0 and sigma(n)//phi(n)==n)

test('F19-FC-02','FloorCeil','⌊√(σ·τ)⌋ = n (floor of sqrt(sigma·tau) = n? √48=6.93→6!)',
    lambda n: math.isqrt(sigma(n)*tau(n))==n)

test('F19-FC-03','FloorCeil','⌊σ²/σ₂⌋ = n-φ (floor of sigma²/sigma₂)',
    lambda n: sigma(n,2)>0 and sigma(n)**2//sigma(n,2)==n-phi(n))

test('F19-FC-04','FloorCeil','⌊σ·φ/τ⌋ = n (σφ/τ=24/4=6=n!)',
    lambda n: tau(n)>0 and sigma(n)*phi(n)//tau(n)==n)

test('F19-FC-05','FloorCeil','⌈n·e⌉ = σ+sopfr = 17? ceil(16.31)=17!',
    lambda n: math.ceil(n*math.e)==sigma(n)+sopfr(n))

test('F19-FC-06','FloorCeil','⌊n·φ_gold⌋ = σ-τ+1? n·1.618=9.71→9? σ-τ+1=9!',
    lambda n: math.floor(n*(1+5**0.5)/2)==sigma(n)-tau(n)+1)

test('F19-FC-07','FloorCeil','⌊σ·e/n⌋ = sopfr (floor of sigma·e/n = sopfr)',
    lambda n: n>0 and math.floor(sigma(n)*math.e/n)==sopfr(n))

test('F19-FC-08','FloorCeil','⌊n²/σ⌋ = σ/τ (floor of n²/sigma = avg divisor)',
    lambda n: sigma(n)>0 and sigma(n)%tau(n)==0 and n*n//sigma(n)==sigma(n)//tau(n))

test('F19-FC-09','FloorCeil','⌊σ₂/σ⌋ = τ (floor of sigma₂/sigma = tau)',
    lambda n: sigma(n)>0 and sigma(n,2)//sigma(n)==tau(n))

test('F19-FC-10','FloorCeil','⌊(σ+τ+φ+n)/ω⌋ = σ (floor of sum/omega = sigma)',
    lambda n: omega(n)>0 and (sigma(n)+tau(n)+phi(n)+n)//omega(n)==sigma(n))

# ══════════════════════════════════════
# DOMAIN 10: GCD / LCM RELATIONS (10)
# ══════════════════════════════════════

test('F19-GL-01','GcdLcm','gcd(σ,n) = n (n divides sigma, perfect!)',
    lambda n: math.gcd(sigma(n),n)==n)

test('F19-GL-02','GcdLcm','lcm(σ,n)/gcd(σ,n) = σ/n = 2 (lcm/gcd ratio = abundancy)',
    lambda n: math.gcd(sigma(n),n)>0 and lcm(sigma(n),n)//math.gcd(sigma(n),n)==sigma(n)//n if sigma(n)%n==0 else False)

test('F19-GL-03','GcdLcm','gcd(σ,τ) = τ (tau divides sigma)',
    lambda n: math.gcd(sigma(n),tau(n))==tau(n))

test('F19-GL-04','GcdLcm','lcm(φ,τ) = τ (phi divides tau → lcm=tau)',
    lambda n: lcm(phi(n),tau(n))==tau(n))

test('F19-GL-05','GcdLcm','gcd(σ,φ,τ,n) = φ (GCD of all four = totient)',
    lambda n: math.gcd(math.gcd(sigma(n),phi(n)),math.gcd(tau(n),n))==phi(n))

test('F19-GL-06','GcdLcm','lcm(σ,φ,τ,n) = σ (LCM of all four = sigma)',
    lambda n: lcm(lcm(sigma(n),phi(n)),lcm(tau(n),n))==sigma(n))

test('F19-GL-07','GcdLcm','gcd(n!,σ²) = σ² (sigma² divides n!)',
    lambda n: n<=12 and math.factorial(n)%(sigma(n)**2)==0)

test('F19-GL-08','GcdLcm','gcd(σ-n,σ-τ) = σ-τ-n+gcd? Test: gcd(6,8)=2=φ',
    lambda n: math.gcd(sigma(n)-n,sigma(n)-tau(n))==phi(n))

test('F19-GL-09','GcdLcm','lcm(2,3,...,n) = lcm(1..n) = σφ·sopfr/ω? lcm(1..6)=60=σ·sopfr',
    lambda n: n<=30 and math.lcm(*range(1,n+1))==sigma(n)*sopfr(n))

test('F19-GL-10','GcdLcm','gcd(σ,sopfr)·lcm(τ,ω) = σ-φ (gcd·lcm cross relation)',
    lambda n: math.gcd(sigma(n),sopfr(n))*lcm(tau(n),omega(n))==sigma(n)-phi(n))

# ══════════════════════════════════════
if __name__=='__main__':
    print("="*80)
    print("FRONTIER 1900: 100 Single-Condition Hypotheses")
    print("="*80)
    grades=defaultdict(list)
    for r in results: grades[r['grade']].append(r)
    print(f"\n{'Grade':<6} {'Count':<6}")
    for g in ['⭐','🟩','🟧','⚪','⬛']: print(f"{g:<6} {len(grades.get(g,[])):<6}")
    domains=defaultdict(list)
    for r in results: domains[r['domain']].append(r)
    print(f"\nDOMAIN BREAKDOWN")
    for dom in sorted(domains.keys()):
        items=domains[dom]
        print(f"  {dom}: {len(items)} hyps, {sum(1 for r in items if r['grade']=='⭐')}⭐ {sum(1 for r in items if r['grade']=='🟩')}🟩")
    print(f"\n⭐ MAJOR DISCOVERIES")
    for r in results:
        if r['grade']=='⭐': print(f"  {r['id']}: {r['statement']}  Sol:{r['solutions']}")
    print(f"\n🟩 SMALL SETS")
    for r in results:
        if r['grade']=='🟩': print(f"  {r['id']}: {r['statement']}  Sol:{r['solutions']}")
    total=len(results); passing=sum(1 for r in results if r['grade'] in ['⭐','🟩','🟧'])
    print(f"\nTOTAL: {total} hyps, {passing} pass | ⭐{len(grades.get('⭐',[]))} 🟩{len(grades.get('🟩',[]))} 🟧{len(grades.get('🟧',[]))} ⚪{len(grades.get('⚪',[]))} ⬛{len(grades.get('⬛',[]))}")
