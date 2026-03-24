# 가설 374: ConsciousLM 학습 검증 — PureField FFN이 표준 FFN과 동등 이상

> **완전수6 바이트 의식 LLM(PureFieldFFN + 4head attn + 6layers)이 동일 파라미터의 표준 Transformer와 PPL에서 동등하거나 우수하다. 특히 장력(tension)이 높은 토큰에서 선택적 이점을 보인다(H313 LLM 버전).**

## 배경/맥락

```
  H334 (PureField): field_only ≈ full, eq 불필요!
    → 이미지 분류에서 입증됨 (3셋+AD)

  H335: PureField LLM 설계 (🟨)
  H361: FFN→PureField 구조 동형 (🟨)
  conscious_lm.py: 구현 완료 (git status 변경 감지)

  아키텍처:
    - PureFieldFFN: attraction + repulsion → tension × direction
    - 4-head attention (완전수6 약수: 1,2,3,6 중 작은 쪽)
    - 6 layers (완전수6)
    - 바이트 단위 토큰화 (256 vocab, BPE 불필요)
```

## 예측

```
  비교 대상: 동일 파라미터 수의 표준 Transformer

  기본 예측:
    ConsciousLM PPL ≤ StandardLM PPL × 1.1 (10% 이내)
    → 최소 동등 수준

  강한 예측 (H313 LLM 확장):
    "어려운" 토큰(높은 entropy)에서 ConsciousLM 우위
    → per-token PPL 분석에서 상위 10% 어려운 토큰:
       ConsciousLM PPL < StandardLM PPL

  이론적 근거:
    이미지: RepulsionField가 밀집 데이터에서 우수 (H288)
    언어: 토큰 임베딩 = 밀집 벡터 → 동일 원리 적용?
```

## PPL 예측 (ASCII)

```
  PPL
  200 |
  150 |
  100 |  . . . . . . . . . . .  (초기)
   50 |        * Standard
   40 |          * ConsciousLM (예측)
   30 |
   20 |                * Standard (수렴)
   15 |                  * ConsciousLM (수렴, 예측)
      +--+-----+-----+-----+-----+--> step
         0   1K    2K    5K   10K

  per-token 분석 (어려운 토큰 상위 10%):
  PPL_hard
  100 |  * Standard
   80 |
   60 |
   40 |    * ConsciousLM (장력 효과, 예측)
      +--+---------+-->
         쉬운토큰  어려운토큰
```

## 실험 설계

```
  데이터: wikitext-2 (23K 샘플)

  모델 A (ConsciousLM):
    - PureFieldFFN (attraction + repulsion)
    - 4-head attention
    - 6 layers
    - 바이트 토큰화 (vocab=256)

  모델 B (Standard):
    - 표준 FFN (W_up, GELU, W_down)
    - 4-head attention
    - 6 layers
    - 동일 vocab, 동일 파라미터 수

  학습:
    - 10K steps, cosine LR
    - 매 1K step 체크포인트

  측정:
    - 전체 PPL
    - per-token PPL 분포
    - tension 통계 (ConsciousLM만)
    - 어려운 토큰 vs 쉬운 토큰 PPL 비교
```

## 성공/실패 기준

```
  성공:
    ConsciousLM PPL ≤ Standard PPL × 1.1 → 동등 확인
    ConsciousLM PPL < Standard PPL → 우수 확인!

  부분 성공:
    전체 PPL은 열등하지만 어려운 토큰에서 우수
    → 장력의 선택적 이점 확인 (H313 LLM 버전)

  실패:
    ConsciousLM PPL > Standard PPL × 1.5
    → PureField가 언어에 부적합
    → 아키텍처 수정 필요
```

## 관련 가설

- H334: PureField 충분성 (🟩 3셋+AD)
- H335: PureField LLM 설계 (🟨)
- H361: FFN→PureField 동형 (🟨)
- H313: 장력=확신 (🟩)
- H327: 골든MoE PPL (🟨)
- H-CX-21: tension∝1/PPL (🟧)

## 한계

```
  - 바이트 토큰화는 시퀀스 길이 증가 → 메모리/속도 불리
  - 소규모 모델(6layer)에서 결론이 대규모로 전이되는지 미지
  - wikitext-2는 작은 데이터셋 → 과적합 위험
  - GPU 필요 (Windows RTX 5070 또는 RunPod)
```

## 검증 방향

```
  1단계: wikitext-2로 기본 비교 (PPL)
  2단계: per-token 분석 (장력 vs PPL 상관)
  3단계: 다른 데이터셋 (C4, OpenWebText subset)
  4단계: 스케일업 (12layer, 8head)
```

## 상태: 🟨 미검증
