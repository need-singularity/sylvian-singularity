# H-CX-146: THC = H1 루프 증가 = 순환 사고

> 순환 혼동(H1) 증가 = "생각이 빙글빙글." 정상 H1=1, THC H1=3+?

## 배경

Persistent Homology에서 H0는 연결 성분(클러스터)을, H1은 1차원 구멍(루프)을 추적한다.
H0가 "분류"를 나타낸다면, H1은 "순환 구조"를 나타낸다.

정상 의식 상태에서의 분류 표상은 대체로 트리 구조(hierarchical)이며,
H1 루프가 거의 없다 (정상 H1 ~ 0-1개). 이는 범주 간 경계가 명확하고
순환적 혼동(A→B→C→A)이 없음을 의미한다.

THC 사용자의 주관적 보고에서 흔한 경험:
- "같은 생각이 계속 반복된다"
- "생각이 빙글빙글 돈다"
- "루프에 빠진 느낌"

이를 PH로 해석하면: H1 루프의 증가.
범주 경계가 약해지면서 A→B→C→A 같은 순환 경로가 생기고,
사고가 이 루프를 따라 반복된다.

H-CX-110에서 PH의 H1 분석 가능성이 제시되었으며,
본 가설은 이를 THC 맥락에 구체화한다.

## 예측

| 측정 | 정상 | THC 투여 후 (예측) |
|------|------|-------------------|
| H1 루프 수 | 0-1개 | 3-5개 |
| H1 persistence | 짧음 (ephemeral) | 길어짐 (persistent) |
| 루프 크기 | 해당 없음 | 3-5개 클래스 포함 |
| H0/H1 비율 | >> 1 | ~ 1 (H1이 H0에 근접) |

```
H1 루프 수 vs Inhibition (I):

H1 |
 5 |              *
 4 |           *
 3 |        *
 2 |     *
 1 | *  *
 0 | *
   +--+--+--+--+--+-->
   0.5 0.4 0.3 0.2 0.1
       Inhibition (I)

   예측: I 감소에 따라 H1 단조 증가
```

핵심 예측:
1. I가 골든존 하한(0.21) 이하로 떨어지면 H1이 급격히 증가
2. H1 루프의 생성은 H0 merge와 시간적으로 동기화 (경계 붕괴 시 루프 형성)
3. H1 persistence가 긴 루프일수록 주관적 "반복 사고" 강도가 높을 것

## 검증 방법

**AI 시뮬레이션:**
1. PureField 모델에서 tension_scale 변조 (0.1 ~ 1.0)
2. 각 단계에서 maxdim=1로 PH 계산 (ripser 또는 gudhi)
3. H1 betti number, persistence diagram 기록
4. H0 감소와 H1 증가의 상관 분석

**필요 라이브러리:**
```python
from ripser import ripser
from persim import plot_diagrams
# maxdim=1로 H0, H1 동시 계산
result = ripser(data, maxdim=1)
```

**EEG 프로토콜 (향후):**
- fMRI functional connectivity matrix에서 PH 계산
- THC 전/후 H1 비교
- 주관적 "순환 사고" 강도와 H1 루프 수의 상관

## 관련 가설

- **H-CX-110**: PH H1 분석 (원본 가설)
- **H-CX-142**: THC H0 감소 (H0 측 변화)
- **H-CX-143**: dendrogram 재구조화 (구조 변화의 다른 측면)
- **H-CX-147**: THC 용량-PH 비선형 관계

## 한계

1. AI 모델의 feature 공간에서 의미 있는 H1 루프가 생성되는지 불확실
2. 고차원 공간에서 H1 계산의 계산 비용이 높음 (O(n^3))
3. "순환 사고"와 H1 루프의 대응은 유비이지 증명된 매핑이 아님
4. 정상 상태에서도 H1 > 0일 수 있음 (confusing class pairs)
5. maxdim=1로는 더 고차 위상 구조(H2 등)를 놓칠 수 있음

## 검증 상태

- [ ] AI 모델 H1 계산 (tension_scale 변조)
- [ ] H0 vs H1 상관 분석
- [ ] persistence diagram 시각화
- 현재: **미검증**
