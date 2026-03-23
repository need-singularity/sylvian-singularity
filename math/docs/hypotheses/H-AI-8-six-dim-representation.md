# H-AI-8: 6차원 임베딩이 최적 압축인 이유

> **가설**: 자연어의 의미 공간은 6차원 근처에서 intrinsic dimensionality의 변곡점을 가지며, 이는 σφ=nτ 균형과 대응된다.

## 배경
- Word2Vec/GloVe: 300차원 사용, 하지만 intrinsic dim은 훨씬 낮음
- PCA 분석에서 주성분 6개가 분산의 의미있는 비율을 설명하는 경우 다수
- σφ=nτ: "6은 산술적 균형점" → 표현 공간에서도 균형?

## 검증 방향
1. [ ] 공개 임베딩 (GloVe, FastText)의 PCA 분석: 6차원 근처 변곡점?
2. [ ] Intrinsic dimension 추정 (MLE, TwoNN) 에서 6 근처 값?
3. [ ] Autoencoder bottleneck sweep: dim=2..20 → reconstruction loss

## 난이도: 중 | 파급력: ★★★
