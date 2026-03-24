# H-CS-6: 해시 충돌 확률과 σφ/(nτ) 비율

> **가설**: n개 버킷 해시에서 충돌 확률의 "최적 부하율"이 σφ/(nτ) 비율과 관련된다.

## 등급: ⚪ (우연 — 구조적 연결 없음)

## 배경
- Birthday problem: n개 버킷에 k개 삽입 시 충돌 확률
- 최적 부하율 (load factor): 보통 0.7-0.8
- σφ/(nτ)가 해시 테이블 크기 n의 "산술적 적합도"?

## 검증 결과 (2026-03-24)

### Test 1: Birthday Paradox

Birthday paradox 공식에 6은 전혀 등장하지 않는다.

```
P(collision) = 1 - prod(1 - i/N) for i=0..k-1
50% threshold: k ≈ sqrt(2*ln(2)) * sqrt(N) ≈ 1.1774 * sqrt(N)

N=2^128 (MD5):    k ≈ 2^64.2
N=2^256 (SHA-256): k ≈ 2^128.2
N=2^512 (SHA-512): k ≈ 2^256.2
```

상수 sqrt(2*ln(2)) = 1.1774는 2와 ln(2)로만 구성. 6 무관.

### Test 2: Hash Function Round Count Survey

| Algorithm  | Bits | Rounds | Rounds%6==0? |
|------------|------|--------|--------------|
| MD5        | 128  |     64 | NO           |
| SHA-1      | 160  |     80 | NO           |
| SHA-256    | 256  |     64 | NO           |
| SHA-512    | 512  |     80 | NO           |
| SHA-3/256  | 256  |     24 | YES (4x6)    |
| SHA-3/512  | 512  |     24 | YES (4x6)    |
| BLAKE2b    | 512  |     12 | YES (2x6)    |
| BLAKE3     | 256  |      7 | NO           |
| Whirlpool  | 512  |     10 | NO           |

```
Multiples of 6: 5/11 = 45%
Control — multiples of 4: 9/11 = 82%
Control — multiples of 8: 8/11 = 73%
```

4와 8이 6보다 훨씬 더 보편적. 이진 컴퓨터에서 당연한 결과.

### Test 3: Keccak l=6 분석

Keccak의 라운드 수 공식: `nr = 12 + 2*l` where `l = log2(w)`.

```
w= 1: l=0, nr=12
w= 2: l=1, nr=14
w= 4: l=2, nr=16
w= 8: l=3, nr=18
w=16: l=4, nr=20
w=32: l=5, nr=22
w=64: l=6, nr=24   ← standard SHA-3
```

l=6이 나오는 이유: 64-bit CPU 레지스터에 맞추어 lane width=64를 선택했기 때문.
128-bit CPU라면 l=7, nr=26이 됨. **6은 CPU 아키텍처의 부산물이지 수론적 필연이 아님.**

### Test 4: σφ/(nτ) = 1

```
n=6:   σ=12, φ=2, τ=4  → σφ/(nτ) = 24/24 = 1.000
n=28:  σ=56, φ=12, τ=6 → σφ/(nτ) = 672/168 = 4.000
n=496: σ=992, φ=240, τ=10 → σφ/(nτ) = 238080/4960 = 48.000
```

σφ/(nτ)=1은 n=6에서만 성립 (n=28, 496에서는 성립하지 않음).
n=6 고유 성질이긴 하나, hash 성능과의 인과적 연결이 없다.
Chaining hash table의 최적 load factor=1과의 일치는 우연.

### Test 5: 기타

```
sqrt(2*ln(2)) = 1.1774  (birthday constant)
sqrt(6)       = 2.4495
ln(6)         = 1.7918
```

어떤 조합도 표준 hash 상수와 일치하지 않음.

## 결론

| 항목 | 결과 |
|------|------|
| Birthday paradox에 6 등장? | NO |
| Hash round counts에 6 패턴? | 일부만 (SHA-3, BLAKE2). 4, 8이 더 보편적 |
| Keccak l=6? | 64-bit CPU 아키텍처 부산물 |
| σφ/(nτ)=1 → hash 성능? | 인과적 연결 없음 |

**GRADE: ⚪** — 해시 충돌 확률과 6 사이에 구조적 수학적 연결이 없다.
Keccak의 l=6은 공학적 선택(64-bit CPU)의 결과이며, σφ/(nτ)=1은 n=6 고유 성질이지만
해시 성능과 무관하다.

## 난이도: 저 | 파급력: ★
