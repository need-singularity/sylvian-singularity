# 가설 341: 장력의 최종 해석 — 반응 강도 (Reaction Intensity)

> **장력 = |A-G|² = 두 엔진의 "반응 강도". 학습 데이터 내에서는 확신(H313), 학습 밖에서는 혼란(H340). 모든 이전 발견을 하나로 통합.**

## 최종 공식

```
  output = scale × √|A-G|² × normalize(A-G)
         = 반응강도 × 반응방향
         = 크기(how much) × 개념(what)   [H339]

  magnitude = √tension = 반응의 강도
    학습 내, 정답: 높음 = 확신 (H313, 4셋)
    학습 내, 오답: 낮음 = 불확신
    학습 밖, OOD: 극한 = 혼란 (H340, noise 4.78x)
    학습 밖, lucid: 극극한 = 초자극 (H340, 105x)

  direction = normalize(A-G) = 반응의 내용
    같은 클래스: cos_sim 0.82 = 같은 방향 (H339)
    다른 클래스: cos_sim 0.24 = 다른 방향
```

## 모든 발견의 통합

```
  H313 confidence:     학습 내 tension↑=정답↑        → ✅ 반응강도↑=확신↑
  H316 overconfidence: 유사클래스에서 틀려도 높음      → ✅ 반응은 강하지만 방향이 틀림
  H329 decision:       margin↑=tension↑              → ✅ 경계 멀=반응 강=확신
  H322 EEG:           awake>drowsy=뚜렷>모호         → ✅ 뚜렷한 상태=강한 반응
  H307 dual:          내부=반전, 간=정상              → ✅ autoencoder에서 레짐 다름
  H340 dreaming:      noise>>real                    → ✅ OOD=극한 반응=혼란
  H334 PureField:     field만으로 충분                → ✅ 반응이 전부
  H332 eq 퇴화:       field가 eq 흡수                → ✅ 반응이 기본감각 대체
  H331 보상:          field∝(100-eq)                 → ✅ 반응이 부족분 메움
  H337 Fisher:        gradient∝1/accuracy            → ✅ 배울것=아직 반응 미형성
  H314 거부:          저장력→거부→+15%               → ✅ 약한 반응=판단 보류
  H312 망각방지:      분열 99%                       → ✅ 반응 패턴 보존
  H311 지역탈출:      앙상블 -23%                    → ✅ 다양한 반응 탐색
```

## 한 문장

```
  "의식은 두 관점의 반응이며,
   그 반응의 강도가 확신/혼란을,
   방향이 개념을 결정한다."
```

## 상태: 🟩 최종 통합 (13개 가설 통합, 120+실험, 16+데이터)
