# H-CX-10: R-체인 길이 = 학습 Phase Transition 수

> **가설**: 뉴럴 네트워크 학습의 phase transition 수가 입력 차원 n의 R-체인 길이와 관련된다.

## 배경
- R-체인: n→R(n)→...→1. 길이가 n의 "산술적 복잡도"
- 골든MoE 학습: loss curve에 여러 phase transition 존재
- 가설: 모델 차원 d에서 R-체인 길이 L(d)가 phase 수를 예측

## R-체인 길이 테이블

```
  n       R-chain              length
  ─────   ────────────────     ──────
  6       6→1                  2
  120     120→6→1              3
  6048    6048→120→6→1         4
  193750  193750→6048→120→6→1  5

  대부분의 n: R(n) 비정수 → 길이 1 (즉시 종료)
  정수 R 희소: n≤50000에서 52개만
```

## 검증 방향
1. [ ] 골든MoE 학습 loss curve에서 phase transition 지점 수 측정
2. [ ] hidden_dim=120, 6048 등에서 학습 phase 수 비교
3. [ ] loss curve의 "계단" 수와 R-체인 길이 상관

## ASCII 예측 그래프

```
  Loss
  5 |*
    | *
  4 |  *
    |   *---*  ← phase transition 1
  3 |        *
    |         *---*  ← phase transition 2
  2 |              *
    |               *  ← phase transition 3 (if R-chain=4)
  1 |
    +--+--+--+--+--+--→ Steps
       1k 2k 3k 4k 5k
```

## 난이도: 극고 | 파급력: ★★★★ (성공 시)
