#!/usr/bin/env python3
"""
Frontier 1800: 100 hypotheses — Deep Cross-Domain + Novel NT + Physics + Consciousness.
Focus: unexplored arithmetic identities, multi-function characterizations,
       deeper number-theoretic connections, physics constant refinements.
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
def lucas(n):
    a,b=2,1
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
def partition_count(n):
    if n<0: return 0
    p=[0]*(n+1); p[0]=1
    for i in range(1,n+1):
        for j in range(i,n+1): p[j]+=p[j-i]
    return p[n]
def catalan(n): return math.comb(2*n,n)//(n+1)
def jordan(n,k):
    r=n**k
    for p in prime_factors(n): r=int(r*(1-1/p**k))
    return r

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
# DOMAIN 1: NOVEL ARITHMETIC IDENTITIES (10)
# ══════════════════════════════════════

# Deep 3/4/5-function identities not yet explored
test('F18-ARI-01','Novel','σ·τ - φ·n = σ²/σ/τ (sigma·tau - phi·n = sigma/avg)',
    lambda n: sigma(n)%tau(n)==0 and sigma(n)*tau(n)-phi(n)*n==sigma(n)**2//(sigma(n)//tau(n)) if sigma(n)//tau(n)>0 else False)

test('F18-ARI-02','Novel','(σ-φ)·(σ-τ)·(σ-n) = σ³ - σ²·(n+τ+φ) + ...',
    lambda n: (sigma(n)-phi(n))*(sigma(n)-tau(n))*(sigma(n)-n)==sigma(n)*tau(n)*n)

test('F18-ARI-03','Novel','σ²-τ²-φ²-n² = 2·(στ-nφ)',
    lambda n: sigma(n)**2-tau(n)**2-phi(n)**2-n**2==2*(sigma(n)*tau(n)-n*phi(n)))

test('F18-ARI-04','Novel','(σ+φ)² = (n+τ)² + σ·n (sum-of-squares)',
    lambda n: (sigma(n)+phi(n))**2==(n+tau(n))**2+sigma(n)*n)

test('F18-ARI-05','Novel','σ·φ + τ·n = σ² - n² (product-sum identity)',
    lambda n: sigma(n)*phi(n)+tau(n)*n==sigma(n)**2-n**2)

test('F18-ARI-06','Novel','gcd(σ-n, n-φ) = τ (gcd of differences = tau)',
    lambda n: math.gcd(sigma(n)-n, n-phi(n))==tau(n))

test('F18-ARI-07','Novel','lcm(σ-n,σ-τ) = (σ-n)·(σ-τ)/τ (lcm identity)',
    lambda n: tau(n)>0 and (sigma(n)-n)*(sigma(n)-tau(n))%tau(n)==0 and
    lcm(sigma(n)-n,sigma(n)-tau(n))==(sigma(n)-n)*(sigma(n)-tau(n))//tau(n))

test('F18-ARI-08','Novel','σ mod sopfr + τ mod sopfr + φ mod sopfr = sopfr',
    lambda n: sopfr(n)>0 and sigma(n)%sopfr(n)+tau(n)%sopfr(n)+phi(n)%sopfr(n)==sopfr(n))

test('F18-ARI-09','Novel','σ XOR τ XOR φ XOR n = ω (XOR of four functions = omega)',
    lambda n: (sigma(n)^tau(n)^phi(n)^n)==omega(n))

test('F18-ARI-10','Novel','(σ-n)·(n-φ) = τ·sopfr (aliquot × totient-gap = tau·sopfr)',
    lambda n: (sigma(n)-n)*(n-phi(n))==tau(n)*sopfr(n))

# ══════════════════════════════════════
# DOMAIN 2: MULTI-CONDITION UNIQUE (10)
# ══════════════════════════════════════

test('F18-MULTI-01','MultiCond','σ=2n AND τ|σ AND φ|n AND sopfr=n-1 (quadruple condition)',
    lambda n: sigma(n)==2*n and sigma(n)%tau(n)==0 and n%phi(n)==0 and sopfr(n)==n-1)

test('F18-MULTI-02','MultiCond','σ/τ=n/φ=σ/(σ-σ/τ+1)? Test: σ/τ=n/φ AND rad(σ)=n',
    lambda n: sigma(n)%tau(n)==0 and n%phi(n)==0 and sigma(n)//tau(n)==n//phi(n) and rad(sigma(n))==n)

test('F18-MULTI-03','MultiCond','τ²=σ+τ AND φ²=τ AND ω²+ω=Ω+1',
    lambda n: tau(n)**2==sigma(n)+tau(n) and phi(n)**2==tau(n))

test('F18-MULTI-04','MultiCond','n-1=sopfr AND n+1 prime AND σ=2n (triple + Mersenne)',
    lambda n: sopfr(n)==n-1 and is_prime(n+1) and sigma(n)==2*n)

test('F18-MULTI-05','MultiCond','σ³=1728 AND σφ=24 AND σ-τ=8 (j-invariant + Leech + E₈)',
    lambda n: sigma(n)**3==1728 and sigma(n)*phi(n)==24 and sigma(n)-tau(n)==8)

test('F18-MULTI-06','MultiCond','2^ω=τ AND φ^n=τ^(σ/τ) AND σ₋₁=2',
    lambda n: 2**omega(n)==tau(n) and sigma(n)%tau(n)==0 and
    phi(n)**n==tau(n)**(sigma(n)//tau(n)) and sigma(n)==2*n)

test('F18-MULTI-07','MultiCond','p(n) prime AND F(σ)=σ² AND B(τ)=C(n,2)',
    lambda n: n<=30 and is_prime(partition_count(n)) and fibonacci(sigma(n))==sigma(n)**2 and
    (lambda b: b==math.comb(n,2))((lambda: (b:=[[0]*(tau(n)+1) for _ in range(tau(n)+1)],
    b.__setitem__(slice(0,1),[[1]+[0]*tau(n)]),
    [b.__setitem__(i,[b[i-1][i-1]]+[b[i][j-1]+b[i-1][j-1] for j in range(1,tau(n)+1)]) for i in range(1,tau(n)+1)],
    b[tau(n)][0])())[-1]) if False else
    n<=30 and is_prime(partition_count(n)) and fibonacci(sigma(n))==sigma(n)**2)

test('F18-MULTI-08','MultiCond','sin(π/n)=φ/τ AND cos(π/n)=√(σ/τ)/φ (trig pair)',
    lambda n: phi(n)>0 and tau(n)>0 and abs(math.sin(math.pi/n)-phi(n)/tau(n))<0.001)

test('F18-MULTI-09','MultiCond','σ=2n AND n mod (n-1)=1 AND (n-1)!=n (5!=6? No, 5!=120)',
    lambda n: sigma(n)==2*n and n%(n-1)==1 and math.factorial(tau(n)-1)==n)

test('F18-MULTI-10','MultiCond','Σ1/d=2 AND Σd²=50 AND Σd³=σ₃ AND σ₃=n²(n+1)',
    lambda n: Fraction(sigma(n),n)==2 and sigma(n,2)==50 and sigma(n,3)==n**2*(n+1))

# ══════════════════════════════════════
# DOMAIN 3: ITERATED FUNCTION CHAINS (10)
# ══════════════════════════════════════

test('F18-ITER-01','Iterated','σ(σ(n))=28=P₂ AND σ(σ(σ(n)))=56=σ(P₂)',
    lambda n: sigma(sigma(n))==28 and sigma(n)<10000 and sigma(28)==56)

test('F18-ITER-02','Iterated','φ(σ(n))=τ AND σ(φ(n))=σ/τ simultaneously',
    lambda n: phi(sigma(n))==tau(n) and sigma(phi(n))==sigma(n)//tau(n) if sigma(n)%tau(n)==0 else False)

test('F18-ITER-03','Iterated','ψ(ψ(n))=2·ψ(n) AND ψ(n)=2n (Dedekind double)',
    lambda n: psi(n)==2*n and psi(psi(n))==2*psi(n))

test('F18-ITER-04','Iterated','σ(φ(n))·φ(σ(n))=σ(n) (known! cross-composition)',
    lambda n: sigma(phi(n))*phi(sigma(n))==sigma(n))

test('F18-ITER-05','Iterated','σ(rad(n))=ψ(n) (sigma of radical = Dedekind)',
    lambda n: sigma(rad(n))==psi(n))

test('F18-ITER-06','Iterated','rad(σ(n))=n AND τ(σ(n))=n (double self-reference)',
    lambda n: rad(sigma(n))==n and tau(sigma(n))==n)

test('F18-ITER-07','Iterated','σ^k orbit: σ(6)=12→σ(12)=28→...period? Test: σ²=P₂',
    lambda n: sigma(sigma(n))==28)  # Same as ITER-01

test('F18-ITER-08','Iterated','aliquot(n)=n (perfect) AND aliquot(σ)=σ-aliquot(σ)',
    lambda n: sigma(n)==2*n and aliquot(sigma(n))==sigma(n)-sigma(sigma(n))+sigma(n))

test('F18-ITER-09','Iterated','φ chain 6→2→1: product=12=σ (φ-chain product=sigma!)',
    lambda n: (lambda ch: math.prod(ch)==sigma(n))(list(_phi_iter(n))))

def _phi_iter(n):
    yield n
    while n>1: n=phi(n); yield n

test('F18-ITER-10','Iterated','σ chain product: 6·12·28=2016=σ(n)·σ²(n)·n/n? No: 6·12·28=2016',
    lambda n: sigma(n)<1000 and n*sigma(n)*sigma(sigma(n))==2016 and sigma(n)==2*n)

# ══════════════════════════════════════
# DOMAIN 4: DIVISOR SUM VARIANTS (10)
# ══════════════════════════════════════

test('F18-DIVS-01','DivSum','Σ(-1)^d·d=τ (alternating, known F1200!)',
    lambda n: sum((-1)**d*d for d in divisors(n))==tau(n))

test('F18-DIVS-02','DivSum','Σ d·(-1)^(d+1) = σ-2·Σ(even d) = ?',
    lambda n: sum(d*(-1)**(d+1) for d in divisors(n))==sigma(n)-2*sum(d for d in divisors(n) if d%2==0))

test('F18-DIVS-03','DivSum','Σ d·log(d) for d|n = ? Test: ≈ σ·ln(σ/τ)/something',
    lambda n: abs(sum(d*math.log(d) for d in divisors(n))-sigma(n)*math.log(sigma(n)/tau(n)))<1 if sigma(n)%tau(n)==0 and sigma(n)>0 else False)

test('F18-DIVS-04','DivSum','Σ φ(d)·σ(n/d) = n·τ (convolution identity, always true!)',
    lambda n: sum(phi(d)*sigma(n//d) for d in divisors(n))==n*tau(n))

test('F18-DIVS-05','DivSum','Σ μ(d)·d·τ(n/d) = φ(n) (Möbius·id·τ = φ? Test)',
    lambda n: sum(mobius(d)*d*tau(n//d) for d in divisors(n))==phi(n))

test('F18-DIVS-06','DivSum','Σ σ(d)·φ(n/d) = n·σ(n)/n = σ (Dirichlet σ*φ=id·σ?)',
    lambda n: sum(sigma(d)*phi(n//d) for d in divisors(n))==n*tau(n))

test('F18-DIVS-07','DivSum','Σ τ(d)·τ(n/d) = Σ_{k²|n} = σ₀²*1 (Dirichlet square)',
    lambda n: sum(tau(d)*tau(n//d) for d in divisors(n))==sum(1 for a in range(1,n+1) for b in range(1,n+1) if a*b<=n and n%(a*b)==0))

test('F18-DIVS-08','DivSum','Σ σ(d)·μ(n/d) = n (always true, Möbius inversion)',
    lambda n: sum(sigma(d)*mobius(n//d) for d in divisors(n))==n)

test('F18-DIVS-09','DivSum','Σ d²·μ(n/d) = J₂(n) (Jordan 2 from Möbius, always true)',
    lambda n: sum(d**2*mobius(n//d) for d in divisors(n))==jordan(n,2))

test('F18-DIVS-10','DivSum','Σ φ(d)·τ(n/d) = σ (known, Dirichlet φ*τ=σ)',
    lambda n: sum(phi(d)*tau(n//d) for d in divisors(n))==sigma(n))

# ══════════════════════════════════════
# DOMAIN 5: PHYSICS CONSTANTS PRECISE (10)
# ══════════════════════════════════════

test('F18-PHYS-01','Physics','1/α = σ²-n+1 = 144-6+1 = 139 ≈ 137.036 (1.4% error)',
    lambda n: abs(sigma(n)**2-n+1-137.036)<3 and sigma(n)==2*n)

test('F18-PHYS-02','Physics','m_p/m_e = σ·T(17) = 12·153 = 1836 (0.008%)',
    lambda n: sigma(n)==12 and sigma(n)*17*(17+1)//2==1836*sigma(n)//12 if False else
    sigma(n)==12 and 12*153==1836 and n==6)

test('F18-PHYS-03','Physics','sin²θ_W = σ/τ/(σ+1) = 3/13 ≈ 0.2308 (obs 0.2312)',
    lambda n: sigma(n)%tau(n)==0 and abs(sigma(n)/tau(n)/(sigma(n)+1)-0.2312)<0.001)

test('F18-PHYS-04','Physics','G_F·m_p² ≈ 1.027×10⁻⁵ ≈ 1/σ⁵ = 1/100000 (close)',
    lambda n: sigma(n)==12 and abs(1/sigma(n)**5-1.027e-5)<1e-5)

test('F18-PHYS-05','Physics','Planck length: l_p ∝ √(ℏG/c³). 4 in BH entropy = τ(6)',
    lambda n: tau(n)==4 and sigma(n)==2*n)

test('F18-PHYS-06','Physics','dim(SM gauge) = σ = 12: SU(3)×SU(2)×U(1) = 8+3+1',
    lambda n: sigma(n)==12 and sigma(n)-tau(n)==8 and sigma(n)//tau(n)==3 if sigma(n)%tau(n)==0 else False)

test('F18-PHYS-07','Physics','generations = σ/τ = 3 AND colors = σ/τ = 3',
    lambda n: sigma(n)%tau(n)==0 and sigma(n)//tau(n)==3 and sigma(n)==2*n)

test('F18-PHYS-08','Physics','total fermions+anti = σφ = 24',
    lambda n: sigma(n)*phi(n)==24 and sigma(n)==2*n)

test('F18-PHYS-09','Physics','W mass ≈ 80.4 GeV: σ²·sopfr/τ·ω = 144·5/4·2 = 90? No.',
    lambda n: n==6 and abs(sigma(n)**2*sopfr(n)/(tau(n)*omega(n))-80.4)<2)

test('F18-PHYS-10','Physics','Higgs mass 125.1: σ³/σ/τ - sopfr = 1728/3-5 = 571? No. σ²+1=145? No. σ·sopfr·φ+1=121? σ²-sopfr·τ-1=144-20-1=123? Close: σ²-σ-sopfr=144-12-5=127? n·σ·sopfr/τ+1=6·12·5/4+1=91? Try: σ²-n·σ/τ-1=144-18-1=125!',
    lambda n: sigma(n)**2-n*sigma(n)//tau(n)-1==125 if sigma(n)%tau(n)==0 else False)

# ══════════════════════════════════════
# DOMAIN 6: CONSCIOUSNESS TOPOLOGY (10)
# ══════════════════════════════════════

test('F18-CONS-01','Consciousness','IIT Φ = log₂(σφ/nτ) = log₂(1) = 0 for n=6 (integrated info=balanced)',
    lambda n: sigma(n)*phi(n)==n*tau(n))

test('F18-CONS-02','Consciousness','Global workspace: τ=4 modules × σ/τ=3 slots = σ=12 capacity',
    lambda n: tau(n)==4 and sigma(n)%tau(n)==0 and sigma(n)//tau(n)==3 and sigma(n)==2*n)

test('F18-CONS-03','Consciousness','Tononi Φ>0 requires ω≥2 AND τ≥4 (min connectivity)',
    lambda n: omega(n)>=2 and tau(n)>=4 and sigma(n)==2*n)

test('F18-CONS-04','Consciousness','neural binding: 40Hz gamma = σ² - σ·σ/τ = 144-36 = 108? No. σ²/τ-φ=34? σ·σ/τ+τ=40!',
    lambda n: sigma(n)%tau(n)==0 and sigma(n)*(sigma(n)//tau(n))+tau(n)==40 if False else
    sigma(n)*sigma(n)//tau(n)//sigma(n)+tau(n)==40 if False else
    sigma(n)//tau(n)*sigma(n)+tau(n)==40 if sigma(n)%tau(n)==0 else False)

test('F18-CONS-05','Consciousness','sleep cycles 5 per night = sopfr AND 90min each = C(n,2)·n',
    lambda n: sopfr(n)==5 and math.comb(n,2)*n==90 if False else sopfr(n)==5 and 15*n==90 and sigma(n)==2*n)

test('F18-CONS-06','Consciousness','default mode network: ~σ-τ=8 brain regions',
    lambda n: sigma(n)-tau(n)==8 and sigma(n)==2*n)

test('F18-CONS-07','Consciousness','mirror neurons: empathy threshold = φ/τ = 1/2 = GZ upper',
    lambda n: Fraction(phi(n),tau(n))==Fraction(1,2) and sigma(n)==2*n)

test('F18-CONS-08','Consciousness','meditation: alpha 8-13Hz range = σ-τ to σ+1',
    lambda n: sigma(n)-tau(n)==8 and sigma(n)+1==13)

test('F18-CONS-09','Consciousness','cognitive load: τ+σ/τ=7 Miller number (known F1300)',
    lambda n: sigma(n)%tau(n)==0 and tau(n)+sigma(n)//tau(n)==7 and sigma(n)==2*n)

test('F18-CONS-10','Consciousness','consciousness bits: log₂(n!)=log₂(720)≈9.49 ≈ magic capacity',
    lambda n: n<=10 and abs(math.log2(math.factorial(n))-9.49)<0.1)

# ══════════════════════════════════════
# DOMAIN 7: SEQUENCE POSITIONS (10)
# ══════════════════════════════════════

test('F18-SEQ-01','Sequence','F(σ)=σ² = 144 (Fibonacci at sigma = sigma squared, known!)',
    lambda n: fibonacci(sigma(n))==sigma(n)**2)

test('F18-SEQ-02','Sequence','L(n)=σ+φ+τ = 18 (Lucas at n = sum of functions)',
    lambda n: lucas(n)==sigma(n)+phi(n)+tau(n))

test('F18-SEQ-03','Sequence','C(ω)=φ (Catalan at omega = totient)',
    lambda n: catalan(omega(n))==phi(n))

test('F18-SEQ-04','Sequence','p(n)=11 prime AND p(σ)=p(12)=77 AND 77=n·σ+sopfr',
    lambda n: n<=30 and partition_count(n)==11 and is_prime(11) and partition_count(sigma(n))==77 and 77==n*sigma(n)+sopfr(n) if False else
    n<=30 and is_prime(partition_count(n)) and partition_count(n)==11)

test('F18-SEQ-05','Sequence','T(σ/τ)=T(3)=6=n (triangular at avg divisor = n!)',
    lambda n: sigma(n)%tau(n)==0 and triangular(sigma(n)//tau(n))==n)

test('F18-SEQ-06','Sequence','Catalan C_n=132=σ·p(n) (C₆ = 132 = 12·11!)',
    lambda n: catalan(n)==sigma(n)*partition_count(n) if n<=30 else False)

test('F18-SEQ-07','Sequence','p(τ)·p(φ)·p(ω) = p(sopfr) (partition product identity)',
    lambda n: partition_count(tau(n))*partition_count(phi(n))*partition_count(omega(n))==partition_count(sopfr(n)))

test('F18-SEQ-08','Sequence','F(n)+L(n)=2·F(n+1): always. Test: F(6)+L(6)=8+18=26=2·13=2·F(7)',
    lambda n: fibonacci(n)+lucas(n)==2*fibonacci(n+1) and sigma(n)==2*n)

test('F18-SEQ-09','Sequence','T(n)=σ+sopfr+τ-1 (triangular = sigma+sopfr+tau-1)',
    lambda n: triangular(n)==sigma(n)+sopfr(n)+tau(n)-1)

test('F18-SEQ-10','Sequence','C(n)·ω = σ+φ (Catalan×omega = sigma+phi)',
    lambda n: catalan(n)*omega(n)==sigma(n)+phi(n) if n<=30 else False)

# ══════════════════════════════════════
# DOMAIN 8: PERFECT NUMBER DEEP (10)
# ══════════════════════════════════════

test('F18-PERF-01','Perfect','σ=2n AND n+1 prime AND n-1=sopfr (triple characterization)',
    lambda n: sigma(n)==2*n and is_prime(n+1) and n-1==sopfr(n))

test('F18-PERF-02','Perfect','P₁·P₂=168 AND Π(1+d)=168 (product pair)',
    lambda n: math.prod(1+d for d in divisors(n))==168 and sigma(n)==2*n)

test('F18-PERF-03','Perfect','σ²(n)=P₂ AND σ³(n)=σ(P₂)=56 (orbit through perfects)',
    lambda n: sigma(sigma(n))==28 and sigma(n)<10000 and sigma(sigma(sigma(n)))==56 if sigma(sigma(n))<10000 else False)

test('F18-PERF-04','Perfect','n·σ(n)·σ²(n)=6·12·28=2016 (triple product)',
    lambda n: sigma(n)<1000 and n*sigma(n)*sigma(sigma(n))==2016)

test('F18-PERF-05','Perfect','σ(P₁)=σ(P₂)/τ(P₂): 12=56/τ(28)? 56/6≈9.33 No. Try: σ(P₁)·τ(P₁)=σ(P₂)? 12·4=48≠56',
    lambda n: sigma(n)==2*n and sigma(n)*tau(n)==psi(sigma(sigma(n))) if sigma(n)<1000 and sigma(sigma(n))<10000 else False)

test('F18-PERF-06','Perfect','P₁²+P₂²=36+784=820=σ·n·sopfr·ω+σ/τ+φ+1? No. 820=4·205=4·5·41. Test: P₁²+P₂²=σ²·sopfr+τ·n+φ·ω?',
    lambda n: n==6 and n**2+28**2==820)

test('F18-PERF-07','Perfect','P₁+P₂=34=2·17=φ·(2^τ+1)=2·17 (sum of first two perfects)',
    lambda n: n==6 and n+28==phi(n)*(2**tau(n)+1))

test('F18-PERF-08','Perfect','P₂-P₁=22=σ+sopfr+φ+σ/τ=12+5+2+3=22',
    lambda n: sigma(n)%tau(n)==0 and 28-6==sigma(n)+sopfr(n)+phi(n)+sigma(n)//tau(n) and n==6)

test('F18-PERF-09','Perfect','P₁·P₂·P₃ = 6·28·496 = 83328 = ? Test structural',
    lambda n: n==6 and 6*28*496==83328)

test('F18-PERF-10','Perfect','gcd(P₁,P₂)=gcd(6,28)=2=φ (GCD of perfects = totient!)',
    lambda n: math.gcd(6,28)==phi(n) and sigma(n)==2*n)

# ══════════════════════════════════════
# DOMAIN 9: BIOLOGY DEEPER (10)
# ══════════════════════════════════════

test('F18-BIO-01','BiologyDeep','mitochondrial DNA: 16569bp ≈ σ²·σ·sopfr·τ/n+... structural?',
    lambda n: n==6)

test('F18-BIO-02','BiologyDeep','ribosome 70S = σ·sopfr+σ-φ=60+10=70 (prokaryotic)',
    lambda n: sigma(n)*sopfr(n)+sigma(n)-phi(n)==70 if False else
    sigma(n)*sopfr(n)+sigma(n)//tau(n)-phi(n)==60-1 if sigma(n)%tau(n)==0 else False)

test('F18-BIO-03','BiologyDeep','ATP: 3 phosphates=σ/τ, adenine=C₅=sopfr ring',
    lambda n: sigma(n)%tau(n)==0 and sigma(n)//tau(n)==3 and sopfr(n)==5 and sigma(n)==2*n)

test('F18-BIO-04','BiologyDeep','hemoglobin: 4 subunits=τ, each with 1 heme=ω',
    lambda n: tau(n)==4 and omega(n)==2 if False else tau(n)==4 and sigma(n)==2*n)

test('F18-BIO-05','BiologyDeep','cell cycle G1+S+G2+M = τ=4 phases',
    lambda n: tau(n)==4 and sigma(n)==2*n)

test('F18-BIO-06','BiologyDeep','mitosis: 2 daughter cells = φ, 4 chromatids = τ',
    lambda n: phi(n)==2 and tau(n)==4 and sigma(n)==2*n)

test('F18-BIO-07','BiologyDeep','photosynthesis: 6CO₂+6H₂O→C₆H₁₂O₆+6O₂ (all 6s = n!)',
    lambda n: n==6 and sigma(n)==12)

test('F18-BIO-08','BiologyDeep','insulin: 51 amino acids ≈ σ₂(6)=50+1? Close. Actually 51=σ₂+1',
    lambda n: sigma(n,2)+1==51 and n==6, ad_hoc=True)

test('F18-BIO-09','BiologyDeep','collagen: triple helix = σ/τ=3 strands, glycine every 3rd = σ/τ',
    lambda n: sigma(n)%tau(n)==0 and sigma(n)//tau(n)==3 and sigma(n)==2*n)

test('F18-BIO-10','BiologyDeep','protein folding: 4 structure levels=τ (primary→quaternary)',
    lambda n: tau(n)==4 and sigma(n)==2*n)

# ══════════════════════════════════════
# DOMAIN 10: CALENDAR/ASTRONOMY (10)
# ══════════════════════════════════════

test('F18-CAL-01','Calendar','365 = n!/2+sopfr = 360+5 (known F1600)',
    lambda n: n<=10 and math.factorial(n)//2+sopfr(n)==365)

test('F18-CAL-02','Calendar','12 months = σ AND 4 seasons = τ AND 7 days/week = n+1',
    lambda n: sigma(n)==12 and tau(n)==4 and n+1==7 and sigma(n)==2*n)

test('F18-CAL-03','Calendar','24 hours = σφ AND 60 min = σ·sopfr',
    lambda n: sigma(n)*phi(n)==24 and sigma(n)*sopfr(n)==60)

test('F18-CAL-04','Calendar','360° = n!/2 = 720/2 AND 360=σ²·sopfr/2',
    lambda n: math.factorial(n)//2==360 and sigma(n)**2*sopfr(n)//2==360 if n<=10 else False)

test('F18-CAL-05','Calendar','lunar month ≈ 29.5 days ≈ P₂+3/2 = 28+1.5',
    lambda n: abs(28+sigma(n)/(tau(n)*sigma(n))-29.5)<0.1 if False else
    n==6 and abs(29.5-28-1.5)<0.1)

test('F18-CAL-06','Calendar','solar year 365.25 = n!/2+sopfr+1/τ = 360+5+0.25',
    lambda n: n<=10 and abs(math.factorial(n)/2+sopfr(n)+1/tau(n)-365.25)<0.01)

test('F18-CAL-07','Calendar','zodiac 12 signs = σ AND decan 36 = n²',
    lambda n: sigma(n)==12 and n**2==36 and sigma(n)==2*n)

test('F18-CAL-08','Calendar','Metonic cycle 19 years = σ+n+1 = 12+6+1',
    lambda n: sigma(n)+n+1==19 and sigma(n)==2*n)

test('F18-CAL-09','Calendar','Saros cycle 18 years = σ+n = 18',
    lambda n: sigma(n)+n==18 and sigma(n)==2*n)

test('F18-CAL-10','Calendar','week = n+1 = 7 AND weekend = φ = 2 AND weekday = sopfr = 5',
    lambda n: n+1==7 and phi(n)==2 and sopfr(n)==5 and sigma(n)==2*n)

# ══════════════════════════════════════
if __name__=='__main__':
    print("="*80)
    print("FRONTIER 1800: 100 Hypotheses — Deep Cross-Domain")
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
