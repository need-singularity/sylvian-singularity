# H-CX-69: 위상 가속 — H0_total 감소 속도가 tension_scale 성장률과 일치

> H0_total_persistence의 감소 속도 ∝ (1/3)·ln(epoch) (H320의 tension_scale 성장률).
> 위상 단순화와 장력 성장이 동일한 동역학을 따른다.

## 배경

- H-CX-62 v2: H0_total이 에폭 진행시 단조 감소
- H320: tension_scale ≈ (1/3)·ln(epoch), R²=0.964
- 교차점: H0_total의 감소 곡선도 로그 형태?

**핵심 연결**: tension_scale이 로그로 성장 → 클래스 방향이 분리
→ cosine distance 증가 → H0_total 감소. 같은 동역학.
H0_total(ep) ≈ H0_total(0) - k·ln(ep) ?

## 예측

1. H0_total(ep) = a - b·ln(ep) 피팅의 R² > 0.9
2. b ≈ (1/3)·H0_total(0) (1/3 재등장)
3. tension_scale(ep) × H0_total(ep) ≈ const (역관계 보존)
4. dH0/dep ∝ -1/ep (로그 미분)

## 검증 방법

```
1. H-CX-62 v2 데이터에서 (epoch, H0_total, tension_scale) 추출
2. H0_total = a - b*ln(ep) 피팅 → R² 계산
3. b/(H0_total(0)) 비교 → 1/3 근처?
4. tension_scale * H0_total 의 에폭별 변동 측정
```

## 관련 가설

- H-CX-62 (위상 예지), H320 (tension_scale log 성장)
- H005 (메타 부동점 1/3)

## 한계

- 15 에폭으로 로그 피팅의 자유도 충분하지만 주의 필요
- tension_scale과 H0_total이 독립적으로 측정되지 않음 (같은 모델)

## 검증 상태

- [ ] 로그 피팅 R²
- [ ] 1/3 계수 확인
- [ ] 곱 보존 확인
