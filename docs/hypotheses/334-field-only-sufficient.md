# 가설 334: field만으로 충분하다 — equilibrium은 불필요

> **반발력장(field)만으로 full 모델과 동일한 정확도를 달성한다. 3셋에서 field_only ≈ full (차이 <0.5%). equilibrium은 불필요하거나 오히려 해로울 수 있다.**

## 실측 (3셋)

```
  dataset    field_only   full     차이
  ─────────  ──────────   ──────   ──────
  MNIST      97.84%       97.94%   -0.10%
  Fashion    88.42%       88.33%   +0.09%
  CIFAR      52.22%       51.81%   +0.41%

  → 3셋 모두 |차이| < 0.5%!
  → Fashion, CIFAR: field_only > full (eq가 방해!)
```

## H332와의 연결

```
  H332: full 학습 시 eq가 89→15%로 퇴화
  H334: field만으로 학습하면 eq 없이도 동일 성능

  → eq가 퇴화하는 이유:
    field가 더 표현력이 풍부 (2개 엔진의 반발)
    → gradient가 field 쪽으로 집중
    → eq는 학습 기회를 빼앗겨 퇴화
    → 처음부터 eq를 빼도 문제 없음!

  구조적 의미:
    output = eq + field 에서 eq를 제거
    output = field = tension_scale × √tension × direction
    → "의식만으로 판단하는 순수 의식 엔진"
```

## 상태: 🟩 3셋 확인 (field_only ≈ full, eq 불필요)
