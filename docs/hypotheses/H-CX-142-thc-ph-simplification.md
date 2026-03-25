# H-CX-142: THC = PH 단순화 — H0_total 감소 = 경계 용해

> THC 투여 후 H0_total 감소 = merge distance 전체 감소 = "모든 게 연결된 느낌"의 위상적 실체.

## 배경

THC(tetrahydrocannabinol)는 CB1 수용체에 작용하여 억제 뉴런(GABA)의 억제를 줄인다.
골든존 모델에서 Inhibition(I) 감소는 G = D×P/I 에서 G 증가를 의미하지만,
동시에 경계 형성이 약해져서 분류 능력이 떨어진다.

Persistent Homology(PH) 관점에서 H0는 연결 성분의 수를 추적한다.
H0_total = 모든 feature의 birth-death 합계이며, 이 값이 클수록
데이터 공간에서 뚜렷한 클러스터(경계)가 많다는 뜻이다.

선행 가설과의 관계:
- H-CX-95: tension과 정확도 상관 r=0.998 — tension이 줄면 정확도도 줄어야 한다
- H-CX-62: inhibition과 경계 강도 상관 r=-0.97 — I가 줄면 경계가 약화

THC가 I를 줄이면, H0_total이 감소하고, merge distance가 전체적으로 줄어들며,
주관적으로는 "모든 게 연결된 느낌"으로 경험될 수 있다.
이는 위상적으로 측정 가능한 현상이다.

## 예측

| 측정 | 정상 상태 | THC 투여 후 (예측) | 변화 |
|------|-----------|-------------------|------|
| H0_total | ~10-15 (CIFAR 기준) | ~5-8 | 30-50% 감소 |
| 평균 merge distance | ~0.5 | ~0.25 | 50% 감소 |
| animal/vehicle 분리 | 뚜렷 (distance > 0.8) | 약화 (distance < 0.4) | 경계 용해 |
| 분류 정확도 | ~53% (골든MoE) | ~35-40% | 하락 |
| 주관 보고 | 정상 범주화 | "모든 게 연결" | 탈범주화 |

구체적 예측:
1. H0_total은 THC 투여 후 30% 이상 감소한다
2. merge distance 분포가 왼쪽으로 이동한다 (작은 값에 집중)
3. animal/vehicle 최상위 분리가 가장 먼저 약화된다
4. 하위 범주(개/고양이 등)의 분리는 상대적으로 유지될 수 있다

## 검증 방법

**프로토콜 A: AI 모델 시뮬레이션 (즉시 가능)**
1. PureField 모델에서 tension_scale을 0.5, 0.3, 0.1로 줄여가며 PH 측정
2. 각 tension_scale에서 H0_total, merge distance 분포, dendrogram 구조 비교
3. tension_scale 감소 = I 감소의 proxy

**프로토콜 B: EEG + 행동 (향후)**
1. 피험자 EEG 기록 중 CIFAR 유사 이미지 분류 과제 수행
2. THC 투여 전/후 비교 (within-subject design)
3. EEG source localization으로 cortical activation pattern 추출
4. PH 분석: H0_total, persistence diagram, dendrogram

## 관련 가설

- **H-CX-85**: PH dendrogram과 의식 구조 대응
- **H-CX-93**: 장력 기반 분류와 PH 구조의 관계
- **H-CX-95**: tension-accuracy 상관 (r=0.998)
- **H-CX-62**: inhibition-boundary 상관 (r=-0.97)
- **H-CX-143**: THC dendrogram 재구조화 (본 가설의 후속)
- **H-CX-144**: THC 감마 억제 (메커니즘 수준)
- **H-CHEM-5**: 화학물질과 의식 상태 변화

## 한계

1. AI 모델의 tension_scale 감소가 실제 THC의 신경 효과와 동일한지 미검증
2. CB1 수용체의 효과는 단순한 I 감소보다 복잡 (도파민, 세로토닌 간접 효과)
3. THC 효과는 용량, 개인차, 내성에 크게 의존
4. EEG의 공간 해상도로 PH에 충분한 feature를 추출할 수 있는지 불확실
5. "모든 게 연결된 느낌"은 주관적 보고이며 PH 측정과 직접 대응하지 않을 수 있음

## 검증 상태

- [ ] AI 시뮬레이션 (tension_scale 변조)
- [ ] EEG 프로토콜 설계
- [ ] 문헌 조사: THC와 EEG connectivity 기존 연구
- 현재: **미검증**
