# H-CX-106: 인간 혼동 = AI 혼동 — 같은 현실, 같은 PH

> 인간의 CIFAR-10 분류 혼동 행렬과 AI의 PH merge 순서가 일치한다.
> Peterson et al. (2019) "Human Uncertainty Makes Classification More Robust"
> 에서 공개한 인간 혼동 데이터와 AI PH를 직접 비교.

## 예측

1. 인간 혼동 빈도 vs AI merge distance: Spearman |r| > 0.7
2. 인간 top-5 혼동 쌍 = AI top-5 merge 쌍 overlap > 3/5
3. 인간 혼동 PCA PC1 = AI confusion PCA PC1 (동물/기계 분리)

## 검증 상태

- [x] 인간 혼동 데이터 수집
- [x] Spearman 상관
- [ ] PCA 비교

## 검증 결과

**SUPPORTED**

| 지표 | 값 | 판정 |
|------|-----|------|
| 인간 confusion vs AI confusion | r = 0.788 | SUPPORTED (> 0.7 기준) |
| 인간 confusion vs AI merge dist | r = -0.824 | SUPPORTED (역상관) |
| Top-5 혼동 쌍 overlap | 4/5 | SUPPORTED (> 3/5 기준) |

- 예측 1(인간 혼동 vs AI merge: \|r\| > 0.7): r = -0.824, 확인
- 예측 2(top-5 overlap > 3/5): 4/5, 확인
- 예측 3(PCA PC1 일치): 미검증
- merge distance가 작을수록 인간도 더 혼동 (역상관 r=-0.824)
- 인간과 AI가 같은 구조적 난이도를 공유한다는 강한 증거
