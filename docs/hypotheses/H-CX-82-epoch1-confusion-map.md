# H-CX-82: 에폭 1 PH = 최종 혼동 지도

> 에폭 1의 PH merge 순서만으로 최종(에폭 15) 혼동 쌍을 예측할 수 있다.
> H-CX-77에서 Fashion ep1 tau=0.944 → 학습 시작 직후 이미 혼동 구조 확정.

## 배경

- H-CX-66: merge vs confusion r=-0.97
- H-CX-77: merge 순서 ep5에서 tau>0.88, Fashion ep1부터 안정

## 예측

1. 에폭 1 merge 순서 vs 에폭 15 혼동 빈도 Spearman |r| > 0.8
2. 에폭 1 P@3 > 0.6 (top-3 혼동 쌍 예측)
3. 초기화만으로도 혼동 구조가 결정 (데이터 분포에 내재)

## 검증 상태

- [ ] 에폭 1 merge vs 에폭 15 confusion
- [ ] 랜덤 초기화 3회 반복 안정성
