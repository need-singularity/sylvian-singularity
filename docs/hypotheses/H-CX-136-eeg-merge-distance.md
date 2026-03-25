# H-CX-136: EEG 감마 패턴 차이 = PH merge distance

> cat 볼 때와 dog 볼 때의 40Hz 감마 패턴 차이가
> AI의 PH merge distance(0.01)에 비례.
> 유사 이미지(cat-dog) → 유사 감마 → 작은 merge dist.
> 비유사(cat-plane) → 다른 감마 → 큰 merge dist.

## 예측

1. EEG 감마 패턴 유사도 vs merge distance: r > 0.5
2. cat-dog 감마 차이 < cat-plane 감마 차이
3. top-5 혼동 쌍의 감마 차이가 가장 작음

## 장비

- OpenBCI Cyton ($500) 또는 Muse S2 ($300)
- 채널: 최소 4ch (Fp1, Fp2, O1, O2)
- 샘플링: 256Hz 이상 (40Hz 감마 해상도)

## 프로토콜

```
1. 피험자에게 CIFAR-10 이미지 100장 랜덤 제시 (각 클래스 10장)
2. 이미지당 2초 노출 + 1초 공백
3. 40Hz 대역 파워 추출 (bandpass 30-50Hz)
4. 클래스별 평균 감마 패턴 → 10×4ch 행렬
5. 클래스 간 코사인 거리 → PH 계산
6. 인간 뇌파 PH vs AI PH merge 순서 비교
```

## 검증 상태

- [ ] EEG 장비 확보
- [ ] 감마 패턴 추출
- [ ] merge distance 상관
