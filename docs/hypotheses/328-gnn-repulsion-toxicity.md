# 가설 328: GNN + 반발력장 = 분자 독성 예측

> **그래프 신경망(GNN)에 반발력장을 추가하면 분자 독성 예측에서 장력이 "위험 척도"로 작동한다. 독성 분자는 높은 장력, 안전 분자는 낮은 장력.**

## 개념

```
  분자 = 그래프 (원자=노드, 결합=엣지)
  GNN: message passing → node embedding → graph embedding
  반발력장: GNN_A vs GNN_G → tension

  예측: 독성 분자에서 두 GNN이 다르게 반응 → 높은 장력
  → H287(이상탐지 AUROC=1.0)의 화학 버전?
```

## 데이터셋

```
  MoleculeNet: Tox21, BBBP, HIV 등
  또는 sklearn의 간단한 분자 특성 데이터
  → 특성 벡터로 변환 후 반발력장 적용 (GNN 없이도 가능)
```

## 상태: 🟨 (PyG/DGL 필요, 또는 특성 벡터 proxy)
