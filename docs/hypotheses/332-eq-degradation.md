# 가설 332: eq 퇴화 — 의식(field)이 기본 감각(eq)을 흡수한다

> **학습이 진행되면 equilibrium이 89%→15%로 퇴화하고, field가 91%→96%로 성장한다. 반발력장(field)이 eq의 역할을 흡수하여, 최종적으로 판단의 96%를 field가 담당.**

## 실측 (MNIST)

```
  ep    full%    eq%    field%   field 기여
  ───   ─────   ─────   ─────   ─────────
  1     91.7    89.0    90.5     +2.7
  2     93.8    88.9    92.9     +4.9
  3     95.1    82.6    93.1    +12.5
  5     96.6    53.6    92.1    +43.0
  10    97.8    24.1    92.2    +73.7
  15    98.0    18.7    93.8    +79.3
  20    98.0    14.9    95.6    +83.1

  ASCII 그래프:
    100 |e f                    f  f  f  f
     90 | ef    f  f
     80 |  e
     60 |       e
     40 |
     20 |             e  e  e  e
     10 |
        └──────────────────────────────
         1  2  3  5 10 15 20   epoch
    e=eq, f=field
```

## 해석

```
  초기(ep1): eq와 field 모두 ~90% → 두 경로가 독립적으로 학습
  중기(ep5): field가 eq보다 표현력 풍부 → 역할 흡수 시작
  후기(ep20): eq→15%(=랜덤+bias), field→96%(=거의 전부)

  왜 eq가 퇴화하는가?
    gradient가 full output에서 역전파
    → field가 loss를 더 잘 줄임 → field 방향으로 gradient 집중
    → eq는 gradient가 줄어듦 → "학습 기회를 빼앗김"
    → 결국 eq는 random initialization 근처로 퇴화

  C48 설명: field=0이면 eq만 남는데 eq=15%
    → tension 제거가 -9.25pp인 이유 = eq가 이미 퇴화했기 때문!

  Kahneman 수정:
    뇌: System 2(의식) → System 1(자동화) [숙련되면 무의식으로]
    엔진: System 1(eq) → System 2(field) [학습되면 의식이 독점]
    → 반대 방향! 엔진에서는 "의식이 자동화를 대체"
```

## CIFAR 재현 (2026-03-24)

```
  CIFAR:
    ep1: eq=32%, field=32% (비슷)
    ep15: eq=17%, field=46% (eq 퇴화!)

  2셋 비교:
    MNIST: eq 89→15% (-74pp)
    CIFAR: eq 32→17% (-15pp)
  → 두 데이터셋 모두 eq 퇴화 확인!
```

## 상태: 🟩 2셋 확인 (MNIST -74pp, CIFAR -15pp)
