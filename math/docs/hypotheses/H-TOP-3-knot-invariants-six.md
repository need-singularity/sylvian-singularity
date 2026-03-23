# H-TOP-3: 매듭 불변량과 6

> **가설**: Trefoil 매듭 T(2,3)의 불변량이 sigma,tau를 반영한다.

**상태: 🟨 약한 증거 (Small Numbers 효과 지배적)**

## 배경

Trefoil = 가장 단순한 비자명 매듭 = torus knot T(2,3).
(2,3)은 6의 소인수 분해 6 = 2 x 3에서 나온다.

## Trefoil T(2,3)의 불변량 일람

| 불변량 | 값 | sigma,tau 관계? | 판정 |
|---|---|---|---|
| (p,q) | (2,3) | 2=phi(6), 3=sigma/tau | 자명 |
| crossing number | 3 | sigma/tau = 12/4 = 3 | 자명 |
| genus | 1 | (p-1)(q-1)/2 = 1 | 무관 |
| bridge number | 2 | min(p,q) = phi(6) | 자명 |
| braid index | 2 | min(p,q) = phi(6) | 자명 |
| signature | -2 | -phi(6) | 자명 |
| determinant | 3 | sigma/tau | 자명 |
| unknotting number | 1 | (p-1)(q-1)/2 | 무관 |
| writhe (standard) | 3 | sigma/tau | 자명 |
| stick number | 6 | P_1 = 6 | 주목 |
| colorability | 3-colorable | sigma/tau | 자명 |

### Alexander 다항식

```
  Delta(t) = t - 1 + t^{-1}

  계수: [1, -1, 1]   -- 번갈아 나오는 1, -1
  Delta(-1) = -1 - 1 + (-1) = -3   =>  det = |Delta(-1)| = 3 = sigma/tau
  Delta(1) = 1 - 1 + 1 = 1
```

### Jones 다항식

```
  V(t) = -t^{-4} + t^{-3} + t^{-1}

  계수: [-1, 1, 0, 1]  at  t^{-4}, t^{-3}, t^{-2}, t^{-1}
  지수 범위: -4 에서 -1  =>  span = 3 = sigma/tau
  V(e^{2pi*i/6}): 6번째 단위근에서의 값 -- 특별한 값?

  t = e^{2pi*i/6}: t^6 = 1, t^3 = -1, t^2 = e^{2pi*i/3}
  V(e^{2pi*i/6}) = -e^{-8pi*i/6} + e^{-6pi*i/6} + e^{-2pi*i/6}
                 = -e^{-4pi*i/3} + e^{-pi*i} + e^{-pi*i/3}
                 = -e^{2pi*i/3} + (-1) + e^{-pi*i/3}
                 = -(cos(2pi/3)+i*sin(2pi/3)) - 1 + cos(pi/3)-i*sin(pi/3)
                 = -(-.5+.866i) - 1 + .5 - .866i
                 = .5 - .866i - 1 + .5 - .866i
                 = 0 - 1.732i = -i*sqrt(3)

  |V(e^{2pi*i/6})| = sqrt(3) -- 흥미로우나 sqrt(3)은 매우 흔한 값
```

### Braid group B_3

```
  B_3 = <sigma_1, sigma_2 | sigma_1*sigma_2*sigma_1 = sigma_2*sigma_1*sigma_2>

  중심: Z(B_3) = <(sigma_1*sigma_2)^3>
    지수 3 = sigma/tau

  B_3 / Z(B_3) ≅ PSL(2,Z) = Z/2Z * Z/3Z (자유곱)
    2 = phi(6), 3 = sigma/tau

  PSL(2,Z)는 모듈라 군 -- 모듈라 형식의 대칭군
  weight 12 모듈라 판별식 Delta:
    12 = sigma(6)
    Delta(q) = q * product_{n>=1} (1-q^n)^{24}
    24 = sigma(6) * phi(6)
```

## 핵심 문제: Small Numbers

위 대응표에서 거의 모든 불변량 값이 1, 2, 3 중 하나이다.
이들은 6의 산술 함수 값(tau=4, phi=2, sigma=12)과도 겹치지만,
가장 작은 양의 정수들이므로 우연 일치 확률이 매우 높다.

```
  불변량 값 분포:
    값 = 1: genus, unknotting number    (2개)
    값 = 2: bridge, braid index         (2개)
    값 = 3: crossing, determinant       (2개)
    값 = 6: stick number                (1개)

  sigma,tau 함수 출력:
    sigma/tau = 3,  phi = 2,  tau = 4,  1 (단위)

  1, 2, 3이 겹칠 확률: 매우 높음
```

## 텍사스 명사수 검정 (엄밀)

```
  불변량 수: 11 (위 표)
  sigma,tau 관련 타겟 값: {1, 2, 3, 4, 6, 12}  (6개)
  불변량 값 범위: 대부분 [1, 10]

  불변량 하나가 우연히 타겟에 맞을 확률: ~6/10 = 0.6
  11개 중 k개 매칭 기대값: 11 * 0.6 = 6.6개
  실제 매칭: ~8개 (genus=1, unknotting=1 포함)

  관찰된 매칭이 기대값에 가깝다!

  p-value (8개 이상 매칭): 이항분포 B(11, 0.6)에서
    P(X >= 8) = C(11,8)*0.6^8*0.4^3 + C(11,9)*0.6^9*0.4^2
              + C(11,10)*0.6^10*0.4 + C(11,11)*0.6^11
            = 165*0.01680*0.064 + 55*0.01008*0.16
              + 11*0.00605*0.4 + 1*0.00363
            = 0.1774 + 0.0887 + 0.0266 + 0.0036
            = 0.296

  p = 0.30 >> 0.05  (유의하지 않음!)
```

## stick number = 6에 대한 별도 검토

```
  Trefoil의 stick number = 6은 특별한가?

  stick number: 매듭을 직선 막대기로 구현하는 최소 막대 수
  Trefoil: 최소 6개의 직선 구간 필요 (증명됨, Randell 1994)

  이것은 T(2,3)에서 2+3=5가 아닌 2*3=6과 일치.
  그러나 torus knot T(p,q)의 stick number 일반 공식:
    s(T(p,q)) = 2q  (if p < q, p >= 2, 일부 범위)
    s(T(2,3)) = 2*3 = 6  ← 단순히 2q

  이것은 6 = 2*3이라는 사실의 trivial한 귀결이다.
  stick = 2q이므로 T(2,3)의 stick=6은 구조적 이유가 자명.
```

## B_3 -> PSL(2,Z) -> modular forms 경로

이 경로는 가장 흥미롭지만 sigma,tau와의 연결은 간접적:

```
  T(2,3) ──> B_3 ──> PSL(2,Z) = Z/2 * Z/3
                        |
                        v
                    modular forms
                        |
                    weight 12 = sigma(6)
                        |
                    Delta = q * prod(1-q^n)^{24}
                        |
                    24 = 2 * sigma(6)
                        |
                    Leech lattice (dim 24)
                    Ramanujan tau function

  이 경로에서 12와 24의 등장은 깊은 수학이지만,
  sigma(6)=12가 여기서 등장하는 것은 우연인가 필연인가?

  weight 12의 유래:
    - 모듈라 판별식 Delta의 weight = 12
    - 12 = 2*2*3 = 양의 짝수 중 cusp form이 처음 나타나는 weight
    - S_k(SL_2(Z))의 차원: dim S_{12} = 1 (유일한 cusp form = Delta)
    - 12가 특별한 이유: SL_2(Z)의 관계식에서 자연스럽게 유도

  sigma(6) = 12와 weight 12의 관계:
    - 12 = 1+2+3+4+6+12... 아니, sigma(6) = 1+2+3+6 = 12
    - weight 12가 modular에서 특별한 이유와
      sigma(6)=12인 이유는 독립적이다
    - 공통점: 둘 다 2와 3의 조합에서 비롯
      (6=2*3, SL_2=2x2 행렬, Z/2*Z/3=PSL_2)
```

## 판정

| 항목 | 결과 |
|---|---|
| T(2,3) 파라미터 (2,3) = 6의 소인수 | 자명 (정의에 의해) |
| 불변량 매칭 8/11 | 기대값 6.6, p=0.30 (유의하지 않음) |
| stick=6 | 2q=2*3, 자명한 귀결 |
| B_3->PSL_2->weight 12 | 간접적, 독립적 유래 |
| 텍사스 p-value | 0.30 (유의하지 않음) |
| ad hoc 여부 | Small Numbers 효과 지배적 |
| **등급** | **🟨 약한 증거 (small numbers, p=0.30)** |

## ASCII 요약도

```
  Trefoil T(2,3)
    |
    |-- 불변량들: 거의 모두 {1, 2, 3}
    |   |
    |   +-- sigma,tau 값도 {1, 2, 3, 4, 6, 12}
    |   |
    |   +-- 겹침: small numbers => p=0.30 (유의하지 않음)
    |
    |-- B_3 -> PSL(2,Z) -> modular forms
    |   |
    |   +-- weight 12 = sigma(6)?
    |   |
    |   +-- 독립적 유래 (SL_2 구조 vs 약수합)
    |
    +-- 결론: 흥미롭지만 통계적으로 유의하지 않음

  유의도:  |====.........| p=0.30 (임계값 0.05 미달)
```

## 한계
- Jones 다항식의 특수값 분석이 불완전
- weight 12의 깊은 수론적 유래와 sigma(6)의 관계는 추가 연구 가치 있음
- T(p,q) 일반 torus knot에서 완전수와의 체계적 비교 미실시

## 해석

Trefoil T(2,3)과 6=2x3의 관계는 정의에 의해 자명하다.
매듭 불변량들이 sigma,tau와 겹치는 것은 값이 모두 작은 정수이기 때문이며,
통계적으로 유의하지 않다 (p=0.30).

유일하게 비자명한 경로는 B_3 -> PSL(2,Z) -> weight 12 modular forms이나,
이 경로에서 12가 등장하는 이유와 sigma(6)=12인 이유는 독립적이다.
둘 다 2와 3의 조합에서 비롯된다는 점은 흥미롭지만, 이는 6=2x3이라는
소인수 구조의 반영이지 완전수 고유의 성질은 아니다.

## 난이도: 고 | 파급력: ★ (Small Numbers 한계)
