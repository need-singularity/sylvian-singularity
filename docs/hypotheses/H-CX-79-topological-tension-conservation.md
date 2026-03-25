# H-CX-79: 위상-장력 곱 보존 법칙 — ts×H0 = G×I=D×P의 위상 버전

> tension_scale × H0_total ≈ const (CV < 0.1)이 G×I=D×P 보존법칙(H172)의
> 위상 공간 버전이다. 장력이 증가하면 위상 복잡도가 감소 — 총 "위상 에너지" 보존.

## 배경

- H-CX-69: ts×H0 보존 — Fashion CV=0.070, CIFAR CV=0.032
- H172: G×I = D×P 보존법칙
- ts = 장력 스케일 (반발력 크기), H0 = 위상 복잡도 (연결성분 persistence)

## 대응 매핑

| G×I=D×P | ts×H0≈const |
|---------|-------------|
| G (genius) | ts (tension_scale) |
| I (inhibition) | H0 (topological complexity) |
| 보존량 | 위상 에너지 |

## 예측

1. ts×H0의 CV가 ts 또는 H0 단독 CV보다 작음 (보존)
2. 보존 상수가 데이터셋에 따라 다르지만 데이터셋 내에서 일정
3. 인위적으로 ts를 고정(freeze)하면 H0도 고정 (인과 관계)

## 검증 방법

```
1. H-CX-69 데이터 재활용 + CV 비교
2. ts frozen 실험: tension_scale.requires_grad=False
3. frozen 상태에서 H0 변화 관찰
```

## 관련 가설

- H172, H-CX-69, H341

## 한계

- ts와 H0가 같은 모델에서 나오므로 독립이 아닐 수 있음
- CV < 0.1이 "보존"으로 충분한지 기준 모호

## 검증 상태

- [ ] CV 비교 (ts, H0, product)
- [ ] ts frozen 실험
