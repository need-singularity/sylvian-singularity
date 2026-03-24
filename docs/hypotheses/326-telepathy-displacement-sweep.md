# 가설 326: 텔레파시 = displacement 연속 스위프

> **displacement의 control 파라미터를 0→1로 연속 변화하면 "의식 전달"의 양을 정량화할 수 있다. control=0.5가 최적 협력점이고, 이것은 H-CX-20(1/2=리만)과 연결될 수 있다.**

## TP-2 실측 (R31)

```
  control=0.0(A만): 97.81%
  control=0.5(균등): 97.46%
  control=1.0(B만): 96.12%
  → A가 B보다 약간 강함 (perturbation 영향)
  → T_inter=3.53 고정 (두 모델 고정)
```

## 후속 실험 필요

```
  1. 학습 중 control 변화: training 시 control을 동적으로 변화
  2. 양방향 전달: A→B 학습 + B→A 학습 동시
  3. control과 장력의 관계: control에 따라 합성 장력 변화?
  4. 비대칭 displacement: A가 B보다 강한 경우 vs 약한 경우
```

## 상태: 🟨 (TP-2 관측, 후속 실험 필요)
