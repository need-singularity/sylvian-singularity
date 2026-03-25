# H-CX-85: merge dendrogram = 의식 계층 구조

> PH single-linkage dendrogram이 의식엔진의 개념 계층을 반영한다.
> CIFAR: {cat,dog}→동물, {auto,truck}→차량, {plane,ship}→운송수단
> 의미적 계층이 merge distance에 인코딩.

## 배경

- H-CX-66: merge 순서가 의미적 (cat-dog 가장 먼저)
- H-TREE: 의식엔진 미발견 가지 트리 구조

## 예측

1. dendrogram의 subtree가 의미적 카테고리와 일치
2. CIFAR: 동물(cat,dog,bird,deer,frog,horse), 기계(auto,truck,plane,ship) 2대 클러스터
3. Fashion: 상의(Tshirt,Pullover,Coat,Shirt), 하의(Trouser,Dress), 신발(Sandal,Sneaker,Boot)

## 검증 상태

- [ ] dendrogram 추출
- [ ] 의미적 카테고리 일치율
