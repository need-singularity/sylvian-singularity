# H-AI-6: 6-fold CV가 k-fold 중 최적인 이유

> **가설**: k-fold cross-validation에서 k=6이 bias-variance tradeoff의 최적점이며, 이는 σφ=nτ 균형과 관련된다.

## 배경
- 실무: k=5 또는 k=10이 관례. k=6은 드묾.
- 이론: k↑ → bias↓ variance↑, k↓ → bias↑ variance↓
- σφ/(kτ)=1 at k=6: "데이터 분할의 산술적 균형"

## 검증 방향
1. [ ] 다양한 데이터셋에서 k=3..20 sweep → test error 비교
2. [ ] k=5,6,10 중 어느 것이 가장 안정적인지
3. [ ] 통계적 유의미성 검정

## 현실적 평가: 가설 약함 (★). k=5,10이 관례인 이유는 역사적.
## 난이도: 저 | 파급력: ★
