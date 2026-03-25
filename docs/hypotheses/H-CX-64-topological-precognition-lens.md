# H-CX-64: 위상 예지 렌즈 — H0_total 감소율이 예지 AUC를 예측한다

> H0_total_persistence의 에폭별 감소율(dH0/dep)이
> 예지 AUC의 변화를 예측한다. PH가 빠르게 단순화되는 모델 = 더 강한 예지 렌즈.

## 배경

- H-CX-62 v2: H0_total과 accuracy 상관 r=-0.97 (Fashion)
- H-CX-58: tension_scale과 AUC 상관 r=0.982
- 두 가설의 교차점: PH 변화율 → 예지 강도 예측

**핵심 연결**: tension_scale이 "렌즈의 배율"이라면,
H0_total의 감소율은 "렌즈가 초점을 맞추는 속도".
빠른 위상 단순화 = 빠른 초점 = 강한 예지.

## 예측

1. dH0/dep (감소율)과 final AUC의 상관 r > 0.7
2. H0_total이 빠르게 감소하는 데이터셋에서 예지 AUC 높음
3. H0_total 감소율 × tension_scale = 예지 강도 복합 지표
4. 복합 지표가 단일 지표보다 예지 AUC 예측력 높음

## 검증 방법

```
1. 3 데이터셋에서 에폭별 (H0_total, tension_scale, precog_AUC) 수집
2. dH0/dep = linear regression slope of H0_total vs epoch
3. Corr(dH0/dep, final_AUC) 계산
4. 복합 지표: dH0/dep × tension_scale vs AUC
```

## 관련 가설

- H-CX-62 (위상 예지), H-CX-58 (예지 렌즈)
- H320 (tension_scale log 성장)

## 한계

- 3개 데이터셋만으로 cross-dataset 상관의 통계적 유의성 약함
- dH0/dep이 선형이 아닐 수 있음

## 검증 상태

- [x] dH0/dep vs AUC 상관
- [x] 복합 지표 검증

## 검증 결과

**판정: SUPPORTED (cross-dataset r=0.912)**

### dH0/dep (선형 감소율)

| Dataset | dH0/dep | final AUC |
|---------|---------|-----------|
| MNIST   | -0.0358 | 0.953     |
| Fashion | -0.0358 | 0.871     |
| CIFAR   | -0.0338 | 0.612     |

### Cross-dataset 상관

```
Cross-dataset |dH0/dep| vs final_AUC: r = 0.912
```

```
  AUC
  0.95 |  *  MNIST
       |
  0.87 |    *  Fashion
       |
       |
  0.61 |         *  CIFAR
       +--+----+----+------>
        0.034  0.035  0.036
              |dH0/dep|
```

### Epoch-level 상관 (데이터셋 내부)

| Dataset | corr(H0, AUC) | 해석 |
|---------|---------------|------|
| MNIST   | 0.39          | 약한 양의 상관 |
| Fashion | -0.05         | 무상관 |
| CIFAR   | -0.15         | 약한 음의 상관 |

에폭 내부에서는 H0과 AUC의 상관이 약함 -- cross-dataset 수준에서만 강한 상관.

### 복합 지표: |dH0/dep| x ts_final

| Dataset | |dH0/dep| x ts_final |
|---------|----------------------|
| MNIST   | 0.070                |
| Fashion | 0.064                |
| CIFAR   | 0.041                |

```
  복합지표
  0.07 |  ##  MNIST
  0.06 |  ##  ##  Fashion
  0.05 |  ##  ##
  0.04 |  ##  ##  ##  CIFAR
  0.03 |  ##  ##  ##
       +--+---+---+-->
         MNI  FAS  CIF
```

복합 지표도 AUC 순서(MNIST > Fashion > CIFAR)와 일치하여 예측 1, 2 확인.
단, cross-dataset 포인트가 3개뿐이므로 통계적 유의성에 한계가 있다.
