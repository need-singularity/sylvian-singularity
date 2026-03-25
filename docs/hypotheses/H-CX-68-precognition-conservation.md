# H-CX-68: 예지 보존법칙 — 크기 예지 + 방향 예지 ≈ 상수

> 클래스별로 mag_AUC + dir_AUC ≈ const (보존).
> 크기 예지가 약한 클래스에서 방향 예지가 보상하고, 그 반대도 성립.
> G×I = D×P 보존법칙(H172)의 예지 버전.

## 배경

- 통합 예지에서 per-class 데이터:
  - MNIST class 1: mag_AUC=0.331, dir_AUC=0.969 (합=1.30)
  - MNIST class 7: mag_AUC=0.861, dir_AUC=0.885 (합=1.75)
- H172: G×I = D×P (보존법칙)

**핵심 연결**: 장력의 크기와 방향이 "예지 에너지"를 분배.
한 채널이 약하면 다른 채널이 보상 → 총 예지 에너지 보존?

## 예측

1. 클래스별 mag_AUC + dir_AUC의 분산이 mag_AUC 또는 dir_AUC 단독 분산보다 작음
2. mag_AUC와 dir_AUC의 상관이 음수 (트레이드오프)
3. 합의 변동계수(CV) < 개별 CV
4. 곱(mag_AUC × dir_AUC)도 보존될 가능성

## 검증 방법

```
1. 통합 예지 실험의 per-class (mag_AUC, dir_AUC) 수집
2. 합과 곱의 분산/CV 계산
3. Corr(mag_AUC, dir_AUC) — 음수면 트레이드오프
4. 3 데이터셋에서 반복
```

## 관련 가설

- H172 (G×I=D×P 보존법칙), H-CX-58, H-CX-59
- H341 (output = magnitude × direction)

## 한계

- 10 클래스로 통계적 검정력 약함
- 보존이 아닌 단순 ceiling 효과일 수 있음

## 검증 상태

- [ ] 합/곱 분산 비교
- [ ] 트레이드오프 상관
