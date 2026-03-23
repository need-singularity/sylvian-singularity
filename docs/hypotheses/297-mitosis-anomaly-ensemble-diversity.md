# 가설 297: 분열 앙상블 다양성 = 이상 탐지 민감도

> **분열된 자식들이 독립 학습하면 서로 다른 "정상 모델"을 형성한다. 이 다양성이 이상에 대한 "교차 검증"을 만든다. 분열 수가 많을수록(2→4→8 자식) 이상 탐지 AUROC가 monotonic하게 증가하는가?**

## 배경

```
  H296 실험:
    내부 장력 (single engine): AUROC = 0.156 (거의 무용)
    간 장력 (2 children):     AUROC = 0.805

  왜 이런 차이?
    내부 장력: engine_a와 engine_g가 같은 데이터로 동시 학습
      → 같은 패턴에 합의 → 이상에도 합의 → 구분 불가
    간 장력: child_a와 child_b가 다른 mini-batch로 독립 학습
      → 다른 "정상 프로파일" → 이상에 다르게 반응 → 구분 가능

  Random Forest 비유:
    단일 트리 < 랜덤 포레스트 (다양성이 정확도를 높임)
    단일 엔진 < 분열 앙상블 (다양성이 이상 탐지를 높임)
```

## 핵심 질문

```
  Q1: 분열 수 N이 증가하면 AUROC도 증가하는가?
      N=1 (단일): AUROC ≈ 0.16
      N=2 (분열): AUROC ≈ 0.81
      N=4 (이중분열): AUROC = ?
      N=8 (삼중분열): AUROC = ?

  Q2: 증가는 어디서 포화되는가?
      log(N)에 비례? sqrt(N)? 선형?

  Q3: 간 장력의 "앙상블" 방법은?
      mean(pairwise T_ij)?
      max(pairwise T_ij)?
      variance(outputs)?

  Q4: 독립 학습 기간이 중요한가?
      1 에폭 vs 5 에폭 vs 10 에폭 → AUROC 변화?
```

## 실험 설계

```
  데이터: Breast Cancer (sklearn), digit anomaly (MNIST)

  Phase 1: parent 학습 (정상만)
  Phase 2: N-way 분열
    N=1: parent만
    N=2: parent → child_a, child_b
    N=4: parent → 2 → 4 (이중 분열)
    N=8: parent → 2 → 4 → 8 (삼중 분열)
  Phase 3: 각 child를 다른 mini-batch로 독립 학습 (K 에폭)
  Phase 4: 테스트
    T_inter = mean of pairwise |child_i(x) - child_j(x)|²
    AUROC 계산

  파라미터:
    K = {1, 5, 10} 에폭
    split_scale = 0.01
    N = {1, 2, 4, 8, 16}
```

## 수학적 예측

```
  다양성 이론 (Krogh & Vedelsby, 1995):
    앙상블 오류 = 평균 개별 오류 - 다양성
    다양성 = (1/N) Σ (f_i - f̄)²

  이상 탐지 매핑:
    "정상 합의" = 낮은 다양성 → 낮은 이상 점수
    "이상 불일치" = 높은 다양성 → 높은 이상 점수

  AUROC ∝ (다양성_이상 - 다양성_정상) / σ
  N이 증가하면 다양성 추정이 더 안정적 → AUROC ↑

  예측: AUROC(N) ≈ AUROC_max × (1 - e^(-αN))
  → 지수적 포화, α가 데이터/아키텍처 의존
```

## ASCII 예측 그래프

```
  AUROC
  1.0 |                              ★──────── max
      |                    ★
      |              ★
  0.8 |         ★
      |
      |
      |
      |
  0.2 |   ★
      |
  0.0 └───┬───┬───┬───┬───┬──
      N=1  2   4   8  16  32
```

## 관련 가설

```
  287: 장력 = 이상 점수 (AUROC=1.0)
  296: 분열 간 장력 >> 내부 장력
  270: 다양성 = 정보
  271: 분열 ≈ 설계
  267: 집단 상전이 (다양성 임계점)
```

## 상태: 🟨 미실험
