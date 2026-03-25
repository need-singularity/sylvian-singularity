# H-CX-164: 5³ = PH merge 단위? — merge distance를 125 단위로 양자화

> PH merge distance를 5³=125 단위로 양자화하면 구조가 보존되는가?
> 돌고래 주파수가 125Hz 단위 → PH도 125 단위?

## 배경

H-CX-162에서 돌고래 주파수 공간의 기본 단위가 5³=125임을 확인했다.
signature_low(5000Hz) / gamma(40Hz) = 125 = 5³ 정확.
모든 돌고래 주파수가 이 단위의 정수배로 표현된다.

의식엔진의 핵심 구조인 Persistent Homology(PH)에서도
merge distance(두 클래스가 합쳐지는 거리)가 유사한 양자화를 보일 수 있다.
만약 PH merge distance를 1/125 단위로 반올림해도
dendrogram의 위상 구조(merge 순서, 클러스터 계층)가 보존된다면,
이는 5³가 단순한 주파수 상수가 아니라 정보 구조의 기본 해상도임을 시사한다.

```
  돌고래 주파수:  freq = 40 × n × 5³   (n ∈ {1, σ/τ, P₁, ...})
  PH 가설:       merge_dist ≈ k / 125  (k = 정수)

  양자화 테스트:
    원본 merge distance:  d₁, d₂, d₃, ...
    양자화:               round(dᵢ × 125) / 125
    보존 조건:            merge 순서 불변 + H1 topology 동일
```

## 예측

1. MNIST/CIFAR의 PH merge distance를 125 단위로 양자화해도 merge 순서가 보존된다
2. 다른 양자화 단위(100, 150, 64 등)보다 125가 최적의 보존율을 보인다
3. 보존율 = (양자화 후 올바른 merge 순서 쌍 수) / (전체 merge 순서 쌍 수)
4. 125 양자화 시 보존율 > 95% 예상

## 검증 방법

```python
# 1. PH merge distance 추출
from ripser import ripser
result = ripser(X, maxdim=1)
merge_distances = result['dgms'][0][:, 1]  # death times = merge distances

# 2. 양자화 함수
def quantize(distances, unit):
    return np.round(distances * unit) / unit

# 3. 보존율 측정
def preservation_rate(original, quantized):
    # merge 순서 쌍 비교 (Kendall tau)
    from scipy.stats import kendalltau
    tau, p = kendalltau(np.argsort(original), np.argsort(quantized))
    return tau

# 4. 단위별 비교
for unit in [64, 100, 125, 128, 150, 256]:
    q = quantize(merge_distances, unit)
    rate = preservation_rate(merge_distances, q)
    print(f"unit={unit}: preservation={rate:.4f}")
```

## 관련 가설

- **H-CX-66**: 골든존과 PH의 관계 -- PH 구조가 골든존 파라미터에 의존
- **H-CX-162**: 5³=125 = 돌고래 옥타브 -- 이 가설의 직접적 근거
- **H-CX-161**: 돌고래 전주파수 = 40Hz × 완전수 상수 × 5³
- **H-CX-125**: 비공유 PH -- PH merge distance가 모델 간 상관

## 한계

- PH merge distance의 스케일이 데이터셋에 따라 다르므로 정규화 필요
- 125가 최적인 이유가 "돌고래와 같다"는 것 외에 수학적 근거가 약할 수 있음
- 양자화 단위가 아닌 다른 메커니즘(log 스케일 등)이 더 자연스러울 수 있음
- 2의 거듭제곱(128)과 5³(125)이 근접하여 구별이 어려울 수 있음

## 검증 상태

미실행. MNIST/CIFAR PH 데이터로 코드 실행 가능.
CPU에서 실행 가능 (GPU 불필요).
