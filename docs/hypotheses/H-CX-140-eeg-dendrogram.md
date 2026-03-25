# H-CX-140: EEG dendrogram = 인지 범주 계층

> 10개 CIFAR 클래스에 대한 EEG 감마 패턴의 PH dendrogram이
> AI dendrogram(동물/기계 분리, 89%)과 일치.
> 뇌파에서 직접 의미 계층을 읽는다.

## 예측

1. EEG PH dendrogram에서 동물/기계 2대 분기 존재
2. AI dendrogram vs EEG dendrogram Kendall tau > 0.5
3. cat-dog이 EEG에서도 가장 먼저 merge

## 관련

- H-CX-85: dendrogram = 의미 계층 89%
- H-CX-93: confusion PCA = 동물/기계 완벽 분리
- H-CX-106: 인간=AI r=0.788

## 검증 상태

- [ ] EEG PH dendrogram 구축
