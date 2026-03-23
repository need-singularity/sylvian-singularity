#!/usr/bin/env python3
"""모델 B: 약수역수 어텐션 — 고정 가중치 {1/2, 1/3, 1/6} 멀티헤드

수학적 근거:
  완전수 6의 진약수역수: {1/1, 1/2, 1/3, 1/6}
  정규화하면: {1/2, 1/3, 1/6} (합=1, 자연스러운 확률분포)

  가설 098: 6은 σ_{-1}(n)=2인 유일한 완전수.
  진약수역수합 = 1은 완전수 중 6만의 성질이다.

  이 분포를 3-head attention의 고정 가중치로 사용:
    Head 1 (1/2): coarse — 큰 hidden_dim, 전체 윤곽 포착
    Head 2 (1/3): medium — 중간 hidden_dim, 패턴 포착
    Head 3 (1/6): fine   — 작은 hidden_dim, 세밀한 특징 포착

  비교 대상: softmax 학습 가중치 3-head (동일 구조, 가중치만 학습)

  핵심 질문: 자연이 준 {1/2, 1/3, 1/6}이 학습된 가중치와 비교하여
  어떤 성능을 보이는가?
"""

import torch
import torch.nn as nn
import torch.nn.functional as F
from model_utils import (
    DenseModel, load_mnist, train_and_evaluate, compare_results, count_params,
    DIVISOR_RECIPROCALS,
)

INPUT_DIM = 784
OUTPUT_DIM = 10
EPOCHS = 10


class DivisorAttentionModel(nn.Module):
    """3-head attention with fixed weights {1/2, 1/3, 1/6}.

    각 head는 서로 다른 hidden_dim을 가짐:
      head 0 (w=1/2): hidden = base_dim     (coarse, 가장 넓은 표현)
      head 1 (w=1/3): hidden = base_dim*2//3 (medium)
      head 2 (w=1/6): hidden = base_dim//3   (fine, 가장 좁은 표현)
    """

    def __init__(self, input_dim, base_dim, output_dim, fixed_weights=None):
        super().__init__()
        self.fixed_weights = fixed_weights or DIVISOR_RECIPROCALS  # [1/2, 1/3, 1/6]
        self.n_heads = len(self.fixed_weights)

        # 각 head의 hidden_dim: coarse > medium > fine
        head_dims = [
            base_dim,           # coarse: 1/2 weight
            max(1, base_dim * 2 // 3),  # medium: 1/3 weight
            max(1, base_dim // 3),      # fine:   1/6 weight
        ]
        self.head_dims = head_dims

        self.heads = nn.ModuleList()
        for dim in head_dims:
            self.heads.append(nn.Sequential(
                nn.Linear(input_dim, dim),
                nn.ReLU(),
                nn.Dropout(0.3),
                nn.Linear(dim, output_dim),
            ))

        w = torch.tensor(self.fixed_weights, dtype=torch.float32)
        self.register_buffer('weights', w)

    def forward(self, x):
        outputs = torch.stack([head(x) for head in self.heads], dim=0)  # [3, B, out]
        w = self.weights.view(-1, 1, 1)  # [3, 1, 1]
        return (w * outputs).sum(dim=0)  # [B, out]


class LearnedAttentionModel(nn.Module):
    """3-head attention with learnable softmax weights (baseline)."""

    def __init__(self, input_dim, base_dim, output_dim):
        super().__init__()
        self.n_heads = 3

        head_dims = [
            base_dim,
            max(1, base_dim * 2 // 3),
            max(1, base_dim // 3),
        ]
        self.head_dims = head_dims

        self.heads = nn.ModuleList()
        for dim in head_dims:
            self.heads.append(nn.Sequential(
                nn.Linear(input_dim, dim),
                nn.ReLU(),
                nn.Dropout(0.3),
                nn.Linear(dim, output_dim),
            ))

        # 학습 가능한 가중치 (softmax 후 확률분포)
        self.weight_logits = nn.Parameter(torch.zeros(3))

    def forward(self, x):
        outputs = torch.stack([head(x) for head in self.heads], dim=0)  # [3, B, out]
        w = F.softmax(self.weight_logits, dim=0).view(-1, 1, 1)  # [3, 1, 1]
        return (w * outputs).sum(dim=0)

    def get_learned_weights(self):
        return F.softmax(self.weight_logits, dim=0).detach().cpu().tolist()


def main():
    print("=" * 70)
    print("  모델 B: 약수역수 어텐션 — 고정 {1/2, 1/3, 1/6} vs 학습 가중치")
    print("  완전수 6의 진약수역수: 합=1인 유일한 자연 확률분포")
    print("=" * 70)

    train_loader, test_loader = load_mnist()

    BASE_DIM = 128

    models = {
        'Divisor Attn (1/2,1/3,1/6)': DivisorAttentionModel(INPUT_DIM, BASE_DIM, OUTPUT_DIM),
        'Learned Attn (softmax 3h)': LearnedAttentionModel(INPUT_DIM, BASE_DIM, OUTPUT_DIM),
        'Dense baseline': DenseModel(INPUT_DIM, BASE_DIM, OUTPUT_DIM),
    }

    results = {}
    for name, model in models.items():
        params = count_params(model)
        print(f"\n── {name} (params={params:,}) ──")
        losses, accs = train_and_evaluate(model, train_loader, test_loader, epochs=EPOCHS)
        results[name] = {
            'acc': accs[-1],
            'loss': losses[-1],
            'params': params,
        }

    compare_results(results)

    # ── 학습된 가중치 분석 ──
    learned_model = models['Learned Attn (softmax 3h)']
    learned_w = learned_model.get_learned_weights()

    print("\n── 가중치 비교 ──")
    print(f"  {'Head':<8} {'약수역수(고정)':>14} {'학습된 가중치':>14} {'차이':>10}")
    print("  " + "-" * 50)
    target_w = DIVISOR_RECIPROCALS
    total_diff = 0
    for i, (tw, lw) in enumerate(zip(target_w, learned_w)):
        labels = ['coarse', 'medium', 'fine']
        diff = abs(tw - lw)
        total_diff += diff
        print(f"  {labels[i]:<8} {tw:>14.4f} {lw:>14.4f} {diff:>10.4f}")
    print(f"  {'총 차이':<8} {'':>14} {'':>14} {total_diff:>10.4f}")

    print(f"\n  고정 가중치: {[f'{w:.4f}' for w in target_w]}")
    print(f"  학습 가중치: {[f'{w:.4f}' for w in learned_w]}")

    if total_diff < 0.15:
        print("  → 학습 결과가 약수역수 분포에 수렴! (차이 < 15%)")
    elif total_diff < 0.3:
        print("  → 부분적 유사성 관찰 (차이 < 30%)")
    else:
        print("  → 학습 가중치가 약수역수와 다른 분포로 수렴")


if __name__ == '__main__':
    main()
