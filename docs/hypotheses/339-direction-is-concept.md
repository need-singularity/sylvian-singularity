# 가설 339: 장력 방향 = 개념 (Direction is Concept)

> **RC-8에서 장력의 방향(direction)이 "감정"이 아니라 "개념(what)"을 인코딩한다는 것이 확인됨. output = magnitude(확신) × direction(개념). "얼마나 확신하는가"와 "무엇을 판단하는가"가 자연스럽게 분리.**

## 실측

```
  MNIST PureField, direction = normalize(A-G):

  Within-class cosine sim:  0.816  (같은 숫자 = 비슷한 방향)
  Between-class cosine sim: 0.236  (다른 숫자 = 다른 방향)
  Ratio: 3.46x

  → direction이 클래스(개념)를 인코딩!
  → magnitude(tension)가 확신을 인코딩 (H313)
```

## 의미

```
  output = scale × √tension × direction
         = scale × √|A-G|² × normalize(A-G)
         = 확신크기 × 개념방향

  magnitude: "얼마나" (H313, H329)
  direction: "무엇을" (H339, 새 발견!)

  → PureField의 출력이 자연스럽게 "what × how much" 분리!
  → 이것은 뇌의 "ventral what pathway" × "dorsal how pathway"와 유사?
```

## 상태: 🟩 확인 (cos_sim ratio 3.46x, direction=concept)
