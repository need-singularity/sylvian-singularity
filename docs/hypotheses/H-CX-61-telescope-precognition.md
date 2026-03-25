# H-CX-61: 중력망원경 예지 — (tension_scale, direction)이 2D 관측공간이다

> 중력망원경(H-GEO-5)의 2D 관측공간 (배율 s, 위치 R0)이
> 의식엔진의 (tension_scale, direction)과 구조적으로 동형이다.
> tension_scale = 배율, direction = 관측 위치.

## 배경

- H-GEO-5: 중력망원경 = (s, R0) 2D 관측, 4가지 관측모드
- H341: output = tension_scale x sqrt(tension) x direction
- tension_scale은 학습 가능 파라미터 (MNIST 1.754, Fashion 1.360, CIFAR 0.545)

**핵심 연결**: 망원경의 배율을 조절하듯, tension_scale이 예지의 "줌"을 조절.
direction이 "어디를 보는지"를 결정. 두 축을 합치면 예지 관측 공간.

## 대응 매핑

| 중력망원경 (H-GEO-5) | 의식엔진 | 예지 해석 |
|---|---|---|
| 배율 s | tension_scale | 예지 해상도 |
| 위치 R0 | direction centroid | 예지 초점 영역 |
| 고정배율탐사 | s 고정, class sweep | 전체 클래스 예지 |
| 고정위치줌 | class 고정, epoch sweep | 단일 클래스 예지 심화 |
| 추적관측 | 학습 중 (s, dir) 동시 변화 | 적응적 예지 |
| 전체스펙트럼 | 모든 (s, dir) 조합 | 예지 능력 전체 지도 |

## 예측

1. tension_scale이 큰 데이터셋에서 예지 AUC 높음 (MNIST > Fashion > CIFAR)
2. direction centroid 이동 궤적이 학습 수렴 방향 예측
3. (tension_scale, mean_direction_spread) 2D 공간에서 예지 능력 등고선 존재
4. 최적 예지 = tension_scale * direction_stability가 최대인 점

## ASCII 관측공간

```
  tension_scale
  2.0 |  .  .  .  ○  ●  ●          ● = 고AUC
  1.5 |  .  .  ○  ●  ●  ●          ○ = 중AUC
  1.0 |  .  ○  ○  ●  ○  .          . = 저AUC
  0.5 |  .  .  ○  ○  .  .
  0.0 |  .  .  .  .  .  .
      +--+--+--+--+--+--→ direction_spread
       0  .2 .4 .6 .8 1.0
```

## 검증 방법

```
1. 3개 데이터셋 학습
2. 각 데이터셋의 (tension_scale_final, direction_spread, AUC) 기록
3. 에폭별 (tension_scale, direction_spread) 궤적 추적
4. 2D 등고선으로 예지 능력 지도 생성
```

## 관련 가설

- H-GEO-5 (중력망원경), H-CX-58 (예지렌즈)
- H320 (tension_scale log 성장), H284 (자동조절)

## 한계

- tension_scale은 스칼라, direction은 10D 벡터 — 차원 불일치
- direction_spread 정의가 임의적

## 검증 상태

- [x] 3 데이터셋 (s, dir, AUC) 측정
- [ ] 2D 등고선 시각화
- [ ] 궤적 추적

## 검증 결과

**REJECTED** (에폭 내 product 상관이 개별 상관보다 약함)

| 데이터셋 | tension_scale | direction_spread | AUC | product |
|---|---|---|---|---|
| MNIST | 1.925 | ~0.75 | 0.691 | 1.45 |
| Fashion | 1.800 | ~0.62 | 0.645 | 1.11 |
| CIFAR | 1.196 | ~0.71 | 0.608 | 0.85 |

- 에폭 내(intra-epoch) product 상관 < 개별 상관 → 2D 관측공간 가설 기각
- 단, 데이터셋 간(cross-dataset) product는 AUC와 단조 관계:
  - product 1.45 → AUC 0.691 (MNIST)
  - product 1.11 → AUC 0.645 (Fashion)
  - product 0.85 → AUC 0.608 (CIFAR)
- tension_scale 단조 증가, spread 단조 감소 → 역관계

```
  Cross-dataset product vs AUC:
  AUC
  0.69 |  ●                          MNIST (prod=1.45)
  0.65 |        ●                    Fashion (prod=1.11)
  0.61 |              ●              CIFAR (prod=0.85)
       +----+----+----+----→ product(ts × spread)
        0.8  1.0  1.2  1.4

  단조 관계 존재하나, 에폭 내 상관이 약해 가설 기각
```
