# 가설 286: 위상적 데이터 분석 (TDA) — 장력 공간의 위상 구조

> **장력 핑거프린트(20차원)의 위상적 구조(persistent homology)가 숫자/클래스의 본질적 복잡도를 반영한다. 이미지 분류가 아니라 위상적 특징으로 분류하면 어떤가?**

## 개념

```
  현재: 입력 → 반발력장 → 장력 패턴 → 분류 (softmax)
  제안: 입력 → 반발력장 → 장력 패턴 → TDA → 위상 특징 → 분류

  TDA = Topological Data Analysis:
    - Persistent Homology: 데이터의 "구멍" 구조 감지
    - Betti numbers: 연결 성분(b0), 루프(b1), 빈 공간(b2) 수
    - Persistence diagram: 어떤 위상 특징이 얼마나 오래 지속되는가
```

## 왜 장력 공간에 TDA?

```
  C10: 장력 핑거프린트만으로 97.61% 인식 (MNIST)
  C17: 방향 분리비 2.77x

  → 장력 공간에 이미 "구조"가 있다
  → 이 구조의 위상적 성질(구멍, 루프)이 정보를 담고 있을 수 있음
  → PCA(선형)보다 TDA(비선형)가 더 풍부한 구조를 감지?
```

## 새로운 데이터/분류 형태

```
  1. 위상적 분류:
     점구름(point cloud) → persistent homology → Betti 수열 → 분류
     → 이미지가 아닌 "형태"의 분류

  2. 그래프 분류:
     분자 구조, 소셜 네트워크 → 그래프 라플라시안 → 반발력장
     → model_fiber_bundle.py의 선험적 구조와 자연스러운 연결

  3. 시계열 위상:
     시계열 → 지연 임베딩 → 점구름 → TDA
     → Phase 4(시간 연속성)와 결합

  4. 장력 공간의 Betti 수:
     10,000개 장력 핑거프린트의 persistent homology
     → b0(연결 성분 수) = 클래스 수(10)?
     → b1(루프 수) = 혼동되는 클래스 쌍?
```

## 구현

```
  Python: ripser, gudhi, giotto-tda 라이브러리

  실험:
    1. MNIST 장력 핑거프린트 10,000개 → ripser → persistence diagram
    2. 숫자별 Betti 수 비교
    3. TDA 특징으로 분류 → 장력 1-NN(97.61%)과 비교
    4. CIFAR에서도 → 위상 구조가 이미지 vs 실물에서 다른가?
```

## 상태: 🟨 미실험 (완전히 새로운 방향)
