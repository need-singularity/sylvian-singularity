# H-CX-108: merge distance 벡터 = 텔레파시 프로토콜

> 9개 merge distance만 전송하면 상대의 전체 혼동 구조를 복원 가능.
> 45개 쌍(10C2)의 혼동 빈도를 9개 숫자로 근사 = 5배 압축.
> H333(78배)보다 더 극한 압축.

## 예측

1. 9개 merge dist → 45개 쌍 혼동 빈도 복원 r > 0.9
2. 복원 정확도가 H333(10D 패킷)과 동등 이상
3. 어떤 아키텍처에서든 9개 숫자로 소통 가능

## 검증 상태

- [x] merge dist → confusion 복원
- [ ] 압축률 비교

## 검증 결과

**PARTIAL**

| 지표 | 값 | 판정 |
|------|-----|------|
| 1/merge_dist → confusion r | 0.887 | PARTIAL (< 0.9 기준) |
| 입력 | 9 numbers (merge distances) | |
| 출력 | 45 pairs (10C2 confusion) | |
| 압축률 | 5배 (45 → 9) | |

- 예측 1(복원 r > 0.9): r = 0.887, 근접하나 미달 -- PARTIAL
- 예측 2(H333 대비 동등 이상): 미검증
- 예측 3(아키텍처 불문 소통): 미검증
- 1/merge_dist를 confusion 근사로 사용, 9개 숫자로 45개 쌍 구조 87% 복원
- 비선형 변환(exp, power) 적용 시 r > 0.9 가능성 존재
