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

- [ ] dH0/dep vs AUC 상관
- [ ] 복합 지표 검증
