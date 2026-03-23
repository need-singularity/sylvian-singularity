# H-AI-5: σφ/(nτ) 비율을 Loss Regularizer로 사용

> **가설**: 뉴럴 네트워크의 가중치 행렬 차원을 n으로 볼 때, σφ/(nτ)→1에 가까운 차원이 일반화에 유리하다.

## 배경
- σφ/(nτ)=1인 유일한 n=6
- n=6 근처가 "산술적 균형점"
- 가설: 이 비율을 regularization에 활용

## 아이디어
```python
# 의사코드
def arithmetic_reg(weight_matrix):
    n = weight_matrix.shape[0]  # 차원
    ratio = sigma(n)*phi(n)/(n*tau(n))
    return (ratio - 1)**2  # 1에 가까울수록 페널티 작음
```

## 검증 방향
1. [ ] 소형 네트워크에서 hidden_dim sweep + arithmetic_reg 추가
2. [ ] 일반화 성능 비교 (with/without reg)
3. [ ] dim=6이 실제로 유리한지 확인

## 난이도: 중 | 파급력: ★★ (투기적)
