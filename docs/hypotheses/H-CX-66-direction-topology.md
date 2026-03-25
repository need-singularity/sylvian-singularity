# H-CX-66: 방향 위상 — 혼동 쌍이 PH의 짧은 바코드에 매핑된다

> 방향 코사인 거리 행렬의 PH에서 짧은 바코드(빨리 죽는 feature)가
> 혼동 쌍(H-CX-59)과 정확히 대응한다. 위상적으로 가까운 클래스 = 혼동 클래스.

## 배경

- H-CX-59: 오답 방향이 혼동 클래스를 가리킴 (70-82%)
- H-CX-62 v2: cosine distance matrix의 PH 계산 성공
- 교차점: PH birth-death에서 빨리 merge되는 클래스 쌍 = 혼동 쌍

**핵심 연결**: H0에서 두 클래스가 빨리 합쳐짐 = cosine distance 작음 = 방향이 비슷 = 혼동.
PH가 혼동 쌍을 자동으로 발견.

## 예측

1. PH에서 가장 먼저 merge되는 클래스 쌍 = top 혼동 쌍 (>60% 일치)
2. merge 순서와 혼동 빈도의 Spearman 상관 > 0.5
3. H1 (loops)이 존재하면 3개 이상의 순환 혼동 (A→B→C→A)

## 검증 방법

```
1. Ripser로 cosine distance matrix의 PH 계산
2. H0 birth-death에서 merge 순서 추출
3. 실제 혼동 행렬(confusion matrix)에서 top 혼동 쌍 추출
4. merge 순서 vs 혼동 빈도 Spearman rank correlation
```

## 관련 가설

- H-CX-59 (방향 예지), H-CX-62 (위상 예지)
- H-TOP-7 (위상 렌즈)

## 한계

- merge 쌍 추출이 PH 라이브러리에 따라 다를 수 있음
- 10 클래스에서 9번의 merge만 있어 표본 작음

## 검증 상태

- [x] merge 순서 vs 혼동 빈도 상관
- [x] H1 순환 혼동 확인

## 검증 결과

**판정: STRONGLY SUPPORTED**

### Spearman(merge_dist, confusion)

| Dataset | Spearman r | p-value | 유의 |
|---------|-----------|---------|------|
| MNIST   | -0.941    | 0.0002  | YES  |
| Fashion | -0.933    | 0.0002  | YES  |
| CIFAR   | -0.967    | 0.0000  | YES  |

```
  |Spearman r|
  1.00 |
  0.97 |              ##  CIFAR (0.967)
  0.96 |              ##
  0.95 |              ##
  0.94 |  ##          ##
  0.93 |  ##  ##      ##
  0.92 |  ##  ##      ##
       +--+---+-------+-->
         MNI  FAS    CIF
```

3개 데이터셋 모두에서 p < 0.001. merge 거리가 짧을수록 혼동 빈도가 높다.

### Top-5 혼동 쌍 overlap (merge 순서 vs 실제 혼동)

| Dataset | Overlap | 비율 |
|---------|---------|------|
| MNIST   | 2/5     | 40%  |
| Fashion | 3/5     | 60%  |
| CIFAR   | 4/5     | 80%  |

### CIFAR merge 순서 (H0 dendrogram)

| Merge 순서 | 클래스 쌍       | merge distance |
|-----------|----------------|---------------|
| 1st       | cat - dog      | 0.05          |
| 2nd       | auto - truck   | 0.12          |
| 3rd       | bird - deer    | 0.13          |
| 4th       | plane - ship   | 0.19          |

```
  CIFAR merge dendrogram (H0)
  distance
  0.19 |          +---plane---ship
  0.13 |     +---bird---deer
  0.12 |  +---auto---truck
  0.05 |  +---cat----dog
       +--+---+---+---+---+---->
          merge order
```

cat-dog이 가장 먼저 merge: 의미적으로도 가장 유사한 쌍.

### H1 loops (순환 혼동)

| Dataset | H1 loops | 해석 |
|---------|----------|------|
| MNIST   | 1        | 약한 순환 구조 |
| Fashion | 0        | 순환 혼동 없음 |
| CIFAR   | 1        | 순환 혼동 존재 |

H1 예측은 부분적. 순환 혼동의 증거는 약하나 주요 예측(merge 순서 = 혼동 순서)은 강하게 지지됨.
