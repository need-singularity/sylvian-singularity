# 가설 293: 장력 이상탐지의 보편성 — 모든 밀집 데이터에서 AUROC > 0.9?

> **이상탐지 AUROC=1.0이 합성 데이터에서만인가, 실제 데이터에서도 유지되는가? 반발력장 장력이 보편적 이상 점수(anomaly score)라면, 기존 이상탐지 기법(Isolation Forest, Autoencoder)과 비교 필요.**

## 검증 대상

```
  합성 데이터: AUROC=1.0 (확인됨, 가설 287)
  실제 데이터 후보:
    1. 신용카드 사기 (Kaggle creditcard) → 실제 이상탐지 벤치마크
    2. 네트워크 침입 (KDD Cup 99) → 사이버 보안
    3. 의료 이상 (breast cancer outlier) → 건강
    4. 제조 센서 (SWAT/SWaT) → 산업용

  비교 기법:
    Isolation Forest
    Autoencoder reconstruction error
    One-Class SVM
    → 장력이 이들보다 나은가?
```

## 상태: 🟨 미실험
