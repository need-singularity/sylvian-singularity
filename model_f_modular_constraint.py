#!/usr/bin/env python3
"""모델 F: SL(2,Z) 모듈러 대칭 제약 네트워크

수학적 근거:
  SL(2,Z)는 모듈러 군 — 정수 행렬 중 행렬식=1인 2x2 행렬의 군.
  모듈러 형식(modular form)은 이 군의 작용 하에 변환 법칙을 따르며,
  수론의 핵심 대상(타원곡선, 리만 제타 등)과 깊이 연결된다.

  완전수 6에서 유도되는 블록 크기:
    sigma(6) = 12  (약수합)
    tau(6)   = 4   (약수 개수)
    lcm(tau(6), 6) = lcm(4, 6) = 12 = sigma(6)

  블록 대칭 제약:
    가중치 행렬을 12x12 블록으로 분할하고, 각 블록을 대칭화:
      W_block = (W + W^T) / 2
    이는 SL(2,Z)의 대칭 표현을 이산화한 것으로,
    가중치 공간의 차원을 절반으로 줄여 정규화 효과를 낸다.

  기대 효과:
    - 대칭 제약이 과적합을 방지 (암묵적 정규화)
    - 블록 크기 12가 sigma(6)과 일치하여 완전수 구조 반영
    - L2 정규화와 비교하여 구조적 제약의 우위를 검증

  검증:
    MNIST에서 모듈러 제약 vs 표준 Linear vs L2 정규화 비교
"""

import torch
import torch.nn as nn
import torch.nn.functional as F
import math
import time

from model_utils import (
    SIGMA, TAU, H_TARGET,
    load_mnist, train_and_evaluate, compare_results, count_params,
    DenseModel,
)

# 블록 크기 = lcm(tau(6), 6) = lcm(4, 6) = 12 = sigma(6)
BLOCK_SIZE = SIGMA  # 12


# ─────────────────────────────────────────
# ModularConstraintLinear
# ─────────────────────────────────────────
class ModularConstraintLinear(nn.Module):
    """nn.Linear 대체: 가중치를 12x12 블록 단위로 대칭화.

    가중치 행렬 (out_features x in_features)를 12x12 블록으로 나누고,
    각 블록에 W_block = (W + W^T) / 2 대칭 제약을 적용한다.
    비정방 블록(가장자리)은 제약 없이 그대로 사용한다.
    """

    def __init__(self, in_features, out_features, bias=True):
        super().__init__()
        self.in_features = in_features
        self.out_features = out_features
        self.weight = nn.Parameter(torch.empty(out_features, in_features))
        if bias:
            self.bias = nn.Parameter(torch.zeros(out_features))
        else:
            self.bias = None
        # Kaiming 초기화
        nn.init.kaiming_uniform_(self.weight, a=math.sqrt(5))

    def _symmetrize_blocks(self, W):
        """가중치를 12x12 블록 단위로 대칭화한다."""
        H, W_dim = W.shape
        result = W.clone()
        # 정방 블록만 대칭화 (12x12 단위)
        n_row_blocks = H // BLOCK_SIZE
        n_col_blocks = W_dim // BLOCK_SIZE
        for i in range(n_row_blocks):
            for j in range(n_col_blocks):
                r_start = i * BLOCK_SIZE
                c_start = j * BLOCK_SIZE
                block = W[r_start:r_start + BLOCK_SIZE, c_start:c_start + BLOCK_SIZE]
                # 대칭화: (W + W^T) / 2
                sym_block = (block + block.T) / 2
                result[r_start:r_start + BLOCK_SIZE, c_start:c_start + BLOCK_SIZE] = sym_block
        return result

    def forward(self, x):
        W_sym = self._symmetrize_blocks(self.weight)
        return F.linear(x, W_sym, self.bias)


# ─────────────────────────────────────────
# ModularConstraintNet
# ─────────────────────────────────────────
class ModularConstraintNet(nn.Module):
    """ModularConstraintLinear로 구성된 네트워크.

    hidden_dim은 12의 배수여야 한다 (블록 대칭 적용을 위해).
    """

    def __init__(self, input_dim=784, hidden_dim=48, output_dim=10, dropout=0.5):
        super().__init__()
        assert hidden_dim % BLOCK_SIZE == 0, \
            f"hidden_dim={hidden_dim}은 {BLOCK_SIZE}의 배수여야 합니다."
        self.net = nn.Sequential(
            ModularConstraintLinear(input_dim, hidden_dim),
            nn.ReLU(),
            nn.Dropout(dropout),
            ModularConstraintLinear(hidden_dim, output_dim),
        )

    def forward(self, x):
        return self.net(x)


# ─────────────────────────────────────────
# L2 정규화 모델 (비교군)
# ─────────────────────────────────────────
class L2RegularizedModel(nn.Module):
    """표준 Linear + L2 정규화 (weight_decay로 구현)."""

    def __init__(self, input_dim=784, hidden_dim=48, output_dim=10, dropout=0.5):
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(input_dim, hidden_dim),
            nn.ReLU(),
            nn.Dropout(dropout),
            nn.Linear(hidden_dim, output_dim),
        )

    def forward(self, x):
        return self.net(x)


# ─────────────────────────────────────────
# 벤치마크
# ─────────────────────────────────────────
def main():
    print("=" * 70)
    print("  모델 F: SL(2,Z) 모듈러 대칭 제약 네트워크")
    print("=" * 70)
    print(f"\n  블록 크기 = sigma(6) = {SIGMA}")
    print(f"  lcm(tau(6), 6) = lcm({TAU}, 6) = {BLOCK_SIZE}")
    print(f"  H_target = {H_TARGET:.6f}")
    print()

    # 데이터
    train_loader, test_loader = load_mnist()

    hidden_dim = 48  # 12의 배수
    epochs = 10
    lr = 0.001
    results = {}

    # 1. 모듈러 제약
    print("[1/3] ModularConstraintNet (hidden=48, block=12)")
    model_mc = ModularConstraintNet(784, hidden_dim, 10)
    t0 = time.time()
    losses_mc, accs_mc = train_and_evaluate(model_mc, train_loader, test_loader,
                                            epochs=epochs, lr=lr)
    elapsed_mc = time.time() - t0
    results['F: Modular Constraint'] = {
        'acc': accs_mc[-1], 'loss': losses_mc[-1],
        'params': count_params(model_mc), 'time': elapsed_mc,
    }

    # 2. 표준 Dense (같은 크기)
    print(f"\n[2/3] Standard Dense (hidden={hidden_dim})")
    model_std = DenseModel(784, hidden_dim, 10)
    t0 = time.time()
    losses_std, accs_std = train_and_evaluate(model_std, train_loader, test_loader,
                                              epochs=epochs, lr=lr)
    elapsed_std = time.time() - t0
    results['Baseline: Standard Dense'] = {
        'acc': accs_std[-1], 'loss': losses_std[-1],
        'params': count_params(model_std), 'time': elapsed_std,
    }

    # 3. L2 정규화 (weight_decay=0.01)
    print(f"\n[3/3] L2 Regularized (hidden={hidden_dim}, wd=0.01)")
    model_l2 = L2RegularizedModel(784, hidden_dim, 10)
    opt_l2 = torch.optim.Adam(model_l2.parameters(), lr=lr, weight_decay=0.01)
    t0 = time.time()
    losses_l2, accs_l2 = train_and_evaluate(model_l2, train_loader, test_loader,
                                            epochs=epochs, lr=lr, optimizer=opt_l2)
    elapsed_l2 = time.time() - t0
    results['Baseline: L2 Regularized'] = {
        'acc': accs_l2[-1], 'loss': losses_l2[-1],
        'params': count_params(model_l2), 'time': elapsed_l2,
    }

    # 결과 비교
    compare_results(results)

    # 대칭 블록 분석
    print("\n--- 모듈러 대칭 블록 분석 ---")
    W = list(model_mc.net[0].parameters())[0].detach()
    H, W_dim = W.shape
    n_row = H // BLOCK_SIZE
    n_col = W_dim // BLOCK_SIZE
    print(f"  가중치 크기: {H} x {W_dim}")
    print(f"  블록 수: {n_row} x {n_col} = {n_row * n_col} 정방블록")

    # 대칭성 측정 (원본 가중치의 비대칭 정도)
    asym_norms = []
    for i in range(n_row):
        for j in range(n_col):
            block = W[i*BLOCK_SIZE:(i+1)*BLOCK_SIZE, j*BLOCK_SIZE:(j+1)*BLOCK_SIZE]
            asym = (block - block.T).norm().item()
            asym_norms.append(asym)
    avg_asym = sum(asym_norms) / len(asym_norms) if asym_norms else 0
    print(f"  평균 비대칭 노름 (학습 후): {avg_asym:.6f}")
    print(f"  → forward에서 대칭화 적용되므로 실제 출력은 완전 대칭")


if __name__ == '__main__':
    main()
