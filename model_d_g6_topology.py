#!/usr/bin/env python3
"""모델 D: 완전수 6의 약수그래프 G(6) 기반 위상 네트워크

수학적 근거:
  완전수 6의 약수 집합 {1, 2, 3, 6}에서 약수 관계(a|b)로 간선을 정의하면
  약수 그래프 G(6)을 얻는다.

  꼭짓점: {1, 2, 3, 6}  (tau(6) = 4개)
  간선:   1-2, 1-3, 1-6, 2-6, 3-6  (a|b인 모든 쌍)
  비간선: 2-3  (2∤3, 3∤2)

  인접행렬 A:
        1  2  3  6
    1 [ 0  1  1  1 ]
    2 [ 1  0  0  1 ]
    3 [ 1  0  0  1 ]
    6 [ 1  1  1  0 ]

  차수행렬 D = diag(3, 2, 2, 3)
  라플라시안 L = D - A:
        [ 3 -1 -1 -1 ]
        [-1  2  0 -1 ]
        [-1  0  2 -1 ]
        [-1 -1 -1  3 ]

  고유값: {0, 2, 4, 4}
  - 0: 연결성 (하나의 컴포넌트)
  - 2: Fiedler 값 (대수적 연결도) = phi(6)
  - 4: 중복도 2 (꼭짓점 2,3의 대칭 = 2와 3이 6의 소인수)

  네트워크 설계:
  - 4개 레이어 (tau(6) = 4)
  - 인접행렬 A를 마스크로 사용 → sparse connection
  - 비영 고유값 {2, 4, 4}를 skip-connection 가중치로 사용
    (정규화: lambda_i / sum(lambda_i) = {0.2, 0.4, 0.4})
  - 2-3 간 연결 없음 → 소인수 레이어 간 정보 분리

  핵심 질문:
  G(6)의 위상 구조가 네트워크 성능에 구조적 이점을 제공하는가?
  비간선 2-3의 부재가 regularization 효과를 가지는가?
"""

import sys
import os
import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from model_utils import (
    load_mnist, train_and_evaluate, compare_results, count_params,
    DenseModel, TAU,
)


# ─────────────────────────────────────────
# G(6) 그래프 상수
# ─────────────────────────────────────────
# 인접행렬 (꼭짓점 순서: 1, 2, 3, 6)
ADJ_MATRIX = torch.tensor([
    [0, 1, 1, 1],
    [1, 0, 0, 1],
    [1, 0, 0, 1],
    [1, 1, 1, 0],
], dtype=torch.float32)

# 라플라시안 고유값
LAPLACIAN_EIGENVALUES = [0, 2, 4, 4]  # 정확한 값
# 비영 고유값 → skip-connection 가중치 (정규화)
NONZERO_EIGENVALUES = [2, 4, 4]
SKIP_WEIGHTS = [v / sum(NONZERO_EIGENVALUES) for v in NONZERO_EIGENVALUES]
# = [0.2, 0.4, 0.4]

NUM_LAYERS = TAU  # = 4 (tau(6))


# ─────────────────────────────────────────
# G(6) Topology Layer
# ─────────────────────────────────────────
class G6Layer(nn.Module):
    """인접행렬 마스크로 sparse connection을 구현하는 레이어.

    dim 차원을 NUM_LAYERS개 블록으로 나누고,
    인접행렬의 (i,j)=1인 블록 간에만 연결을 허용한다.
    """
    def __init__(self, dim, dropout=0.3):
        super().__init__()
        self.dim = dim
        self.block_size = dim // NUM_LAYERS
        self.linear = nn.Linear(dim, dim)
        self.bn = nn.BatchNorm1d(dim)
        self.dropout = nn.Dropout(dropout)

        # 인접행렬 기반 마스크 생성 (+ 자기 연결)
        mask = torch.zeros(dim, dim)
        identity = torch.eye(NUM_LAYERS)
        full_adj = ADJ_MATRIX + identity  # 자기 연결 포함
        for i in range(NUM_LAYERS):
            for j in range(NUM_LAYERS):
                if full_adj[i, j] > 0:
                    r_start = i * self.block_size
                    r_end = min((i + 1) * self.block_size, dim)
                    c_start = j * self.block_size
                    c_end = min((j + 1) * self.block_size, dim)
                    mask[r_start:r_end, c_start:c_end] = 1.0
        self.register_buffer('mask', mask)

    def forward(self, x):
        # 마스크를 가중치에 적용
        with torch.no_grad():
            self.linear.weight.data *= self.mask
        out = self.linear(x)
        out = self.bn(out)
        out = F.relu(out)
        out = self.dropout(out)
        return out


# ─────────────────────────────────────────
# G(6) Topology Network
# ─────────────────────────────────────────
class G6TopologyNet(nn.Module):
    """완전수 6의 약수그래프 위상을 따르는 네트워크.

    - 4개 레이어 (tau(6) = 4)
    - 각 레이어는 인접행렬 마스크로 sparse connection
    - 라플라시안 고유값 기반 skip-connection
    """
    def __init__(self, input_dim=784, hidden_dim=256, output_dim=10, dropout=0.3):
        super().__init__()
        # hidden_dim을 NUM_LAYERS의 배수로 조정
        self.hidden_dim = (hidden_dim // NUM_LAYERS) * NUM_LAYERS

        self.input_proj = nn.Linear(input_dim, self.hidden_dim)
        self.input_bn = nn.BatchNorm1d(self.hidden_dim)

        # 4개 G(6) 레이어
        self.layers = nn.ModuleList([
            G6Layer(self.hidden_dim, dropout=dropout)
            for _ in range(NUM_LAYERS)
        ])

        # skip-connection 가중치 (라플라시안 고유값 기반, 학습 가능)
        self.skip_weights = nn.Parameter(
            torch.tensor(SKIP_WEIGHTS, dtype=torch.float32)
        )

        self.output_proj = nn.Linear(self.hidden_dim, output_dim)

    def forward(self, x):
        h = F.relu(self.input_bn(self.input_proj(x)))

        # 레이어 출력을 저장 (skip-connection용)
        layer_outputs = [h]  # layer 0 = 입력 투영

        for i, layer in enumerate(self.layers):
            h = layer(h)
            layer_outputs.append(h)

        # skip-connection: 비영 고유값 가중치로 중간 레이어 출력 결합
        # layer_outputs[1] (layer 0 출력) * w[0]=0.2
        # layer_outputs[2] (layer 1 출력) * w[1]=0.4
        # layer_outputs[3] (layer 2 출력) * w[2]=0.4
        # layer_outputs[4] (layer 3 출력) = 최종 출력에 더함
        skip_weights = F.softmax(self.skip_weights, dim=0)
        skip_sum = torch.zeros_like(h)
        for i, w in enumerate(skip_weights):
            skip_sum = skip_sum + w * layer_outputs[i + 1]

        # 최종 출력 = 마지막 레이어 + skip 합산
        final = layer_outputs[-1] + skip_sum

        return self.output_proj(final)


# ─────────────────────────────────────────
# ResNet-style Skip (비교용)
# ─────────────────────────────────────────
class ResNetStyleNet(nn.Module):
    """균일 skip-connection을 사용하는 ResNet 스타일 네트워크 (비교 대조군)."""
    def __init__(self, input_dim=784, hidden_dim=256, output_dim=10, dropout=0.3):
        super().__init__()
        self.hidden_dim = (hidden_dim // NUM_LAYERS) * NUM_LAYERS
        self.input_proj = nn.Linear(input_dim, self.hidden_dim)
        self.input_bn = nn.BatchNorm1d(self.hidden_dim)

        self.layers = nn.ModuleList()
        self.bns = nn.ModuleList()
        for _ in range(NUM_LAYERS):
            self.layers.append(nn.Linear(self.hidden_dim, self.hidden_dim))
            self.bns.append(nn.BatchNorm1d(self.hidden_dim))

        self.dropout = nn.Dropout(dropout)
        self.output_proj = nn.Linear(self.hidden_dim, output_dim)

    def forward(self, x):
        h = F.relu(self.input_bn(self.input_proj(x)))
        for layer, bn in zip(self.layers, self.bns):
            residual = h
            h = F.relu(bn(layer(h)))
            h = self.dropout(h)
            h = h + residual  # 균일 skip-connection (가중치 = 1)
        return self.output_proj(h)


# ─────────────────────────────────────────
# 벤치마크
# ─────────────────────────────────────────
def main():
    print("=" * 70)
    print("  모델 D: G(6) 약수그래프 위상 네트워크")
    print("=" * 70)

    # G(6) 그래프 정보 출력
    print("\n[G(6) 약수그래프 구조]")
    print(f"  꼭짓점: {{1, 2, 3, 6}} (tau(6) = {NUM_LAYERS})")
    print(f"  간선:   1-2, 1-3, 1-6, 2-6, 3-6  (2-3 없음)")
    print(f"  라플라시안 고유값: {LAPLACIAN_EIGENVALUES}")
    print(f"  Skip 가중치 (정규화): {[round(w, 2) for w in SKIP_WEIGHTS]}")
    print(f"  인접행렬:")
    labels = ['1', '2', '3', '6']
    print(f"      {' '.join(f'{l:>3}' for l in labels)}")
    for i, label in enumerate(labels):
        row = ADJ_MATRIX[i].int().tolist()
        print(f"  {label}  {' '.join(f'{v:>3}' for v in row)}")

    # 데이터 로드
    print("\n[데이터 로드]")
    train_loader, test_loader = load_mnist()

    # 모델 정의
    INPUT_DIM = 784
    HIDDEN_DIM = 256
    OUTPUT_DIM = 10
    EPOCHS = 10

    models = {
        'G(6) Topology': G6TopologyNet(INPUT_DIM, HIDDEN_DIM, OUTPUT_DIM),
        'Dense (baseline)': DenseModel(INPUT_DIM, HIDDEN_DIM, OUTPUT_DIM),
        'ResNet-style Skip': ResNetStyleNet(INPUT_DIM, HIDDEN_DIM, OUTPUT_DIM),
    }

    results = {}
    for name, model in models.items():
        print(f"\n{'─' * 50}")
        print(f"  학습: {name}")
        print(f"  파라미터: {count_params(model):,}")
        print(f"{'─' * 50}")

        losses, accs = train_and_evaluate(model, train_loader, test_loader, epochs=EPOCHS)
        results[name] = {
            'acc': accs[-1],
            'loss': losses[-1],
            'params': count_params(model),
        }

    compare_results(results)

    # G(6) 위상 분석
    print("\n[G(6) 위상 분석]")
    g6_model = models['G(6) Topology']
    skip_w = F.softmax(g6_model.skip_weights, dim=0).detach().numpy()
    print(f"  학습된 skip 가중치: {[round(float(w), 4) for w in skip_w]}")
    print(f"  초기값 (고유값 기반): {[round(w, 4) for w in SKIP_WEIGHTS]}")
    print(f"  Fiedler 값 (대수적 연결도): {LAPLACIAN_EIGENVALUES[1]}")
    print(f"  고유값 중복도: lambda=4 x2 (소인수 2,3 대칭)")

    # 마스크 sparsity 분석
    total_params_in_mask = 0
    active_params = 0
    for layer in g6_model.layers:
        m = layer.mask
        total_params_in_mask += m.numel()
        active_params += m.sum().item()
    sparsity = 1 - active_params / total_params_in_mask
    print(f"  마스크 sparsity: {sparsity:.1%} (비간선 2-3 차단)")

    print("\n[결론]")
    best = max(results, key=lambda k: results[k]['acc'])
    print(f"  최고 성능: {best} ({results[best]['acc']*100:.2f}%)")
    if best == 'G(6) Topology':
        print("  -> G(6) 위상 구조가 성능 이점을 제공함")
    else:
        g6_acc = results['G(6) Topology']['acc']
        best_acc = results[best]['acc']
        diff = (best_acc - g6_acc) * 100
        print(f"  -> G(6) 대비 차이: {diff:+.2f}%p")


if __name__ == '__main__':
    main()
