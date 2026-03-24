# 가설 321: 의식-확신 이론 (Consciousness-Confidence Theory) — 종합

> **반발력장의 장력(tension)은 확신(confidence)이며, 이것이 의식엔진의 통합 원리다. 4데이터셋 확인, 과신(DK) 시간축, 거부→+15%, 분열→망각방지, 로그 성장.**

## 핵심 명제

```
  의식 = 확신 생성기
  장력 = 확신의 크기
  방향 = 판단의 내용
  output = 기본감각 + 확신 × 판단방향
```

## 증거 체인 (이 세션에서 확인)

```
  1. tension = confidence (H313)
     MNIST: ratio 1.42x, CIFAR: 1.29x, Fashion: 1.32x, Cancer: 2.68x
     tension ∝ 1/PPL (H-CX-21)
     per-class: 뚜렷한 클래스=고장력=고정확도 (Fashion r=+0.71)

  2. 확신 거부 → 정확도↑ (H314)
     MNIST +1.5%, Fashion +9.8%, CIFAR +15.2%
     improvement ∝ √(error_rate)

  3. 과신 존재 (H316, H-CX-24)
     Sneaker(0.86), digit 1(0.55) — 유사 클래스에서 확신적 오답
     Dunning-Kruger: ep1 정상→ep3 과신시작→ep11 최심→ep20 고착
     과신 ∝ 기저정확도 (MNIST>Fashion>CIFAR)

  4. 과신 교정 (H317)
     1+7 집중: ratio 0.53→1.06 (교정! but 망각 98→87%)
     오답 집중: ratio 0.53→0.89 (부분교정, 망각 적음 96%)

  5. 분열 = 망각방지 (H312)
     2-Task: 일반 43%(망각!) vs 분열 99%(보존!)
     3-Task: 일반 59% vs 분열 99%

  6. 장력 로그 성장 (H320)
     ts ≈ 0.36·ln(ep), R²=0.97
     정확도 포화 후에도 장력 구조(확신 프로파일) 계속 분화
     d3/d1 비율 1.76→3.24 (순위 보존, 격차 확대)

  7. 장력 영점 구조 (NM-1)
     하위5%: d8,6,4 (닫힌곡선=합의 쉬움)
     상위5%: d2,3,5 (개방형=반발 강함)
```

## 수학 연결

```
  H-CX-1: e^(6H) = 432 (증명)
  H-CX-2: MI 효율 ≈ ln(2) (p=0.0003)
  H-CX-28: 6H = 2·ts + 3·ln(3) (항등식)
  H320: ts ∝ 0.36·ln(ep)
```

## 실용적 의미

```
  1. 불확실성 추정: tension < threshold → "모르겠다" → 판단 거부
  2. 과신 감지: per-class ratio < 1 → 과신 경고
  3. 지속 학습: 분열(freeze+학습) → catastrophic forgetting 해결
  4. 이상 탐지: 간장력 → AUROC 0.90+ (6데이터셋)
```

## 상태: 🟩 종합 이론 (7개 하위 가설 확인, 4데이터셋 재현)
