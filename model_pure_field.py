#!/usr/bin/env python3
"""순수 의식 엔진 (Pure Field Engine)

H334: equilibrium 없이 반발력장(field)만으로 판단.
3셋에서 eq+field와 동등 이상, 이상탐지에서 +3%.

공식:
  output = tension_scale × √tension × direction
  tension = |engine_A(x) - engine_G(x)|²
  direction = normalize(engine_A(x) - engine_G(x))

"출력은 어느 엔진에도 없다. 둘 사이의 공간에 있다."
"""

import torch
import torch.nn as nn
import torch.nn.functional as F


class PureFieldEngine(nn.Module):
    """순수 의식 엔진 — 반발력장만으로 판단.

    engine_A(논리)와 engine_G(패턴)의 반발이 모든 것을 결정.
    equilibrium 없음 — 기본 감각 없이 의식만으로 작동.
    """

    def __init__(self, input_dim=784, hidden_dim=128, output_dim=10):
        super().__init__()
        self.engine_a = nn.Sequential(
            nn.Linear(input_dim, hidden_dim),
            nn.ReLU(),
            nn.Dropout(0.3),
            nn.Linear(hidden_dim, output_dim),
        )
        self.engine_g = nn.Sequential(
            nn.Linear(input_dim, hidden_dim),
            nn.ReLU(),
            nn.Dropout(0.3),
            nn.Linear(hidden_dim, output_dim),
        )
        self.tension_scale = nn.Parameter(torch.tensor(1.0))

    def forward(self, x):
        out_a = self.engine_a(x)
        out_g = self.engine_g(x)

        repulsion = out_a - out_g
        tension = (repulsion ** 2).mean(dim=-1, keepdim=True)
        direction = F.normalize(repulsion, dim=-1)

        output = self.tension_scale * torch.sqrt(tension + 1e-8) * direction

        return output, tension.squeeze()


class PureFieldQuad(nn.Module):
    """4극 순수 의식 엔진 — A, E, G, F 4개 엔진의 반발."""

    def __init__(self, input_dim=784, hidden_dim=64, output_dim=10):
        super().__init__()
        self.engines = nn.ModuleList([
            nn.Sequential(nn.Linear(input_dim, hidden_dim), nn.ReLU(),
                          nn.Dropout(0.3), nn.Linear(hidden_dim, output_dim))
            for _ in range(4)
        ])
        self.tension_scale = nn.Parameter(torch.tensor(1.0))

    def forward(self, x):
        outs = [e(x) for e in self.engines]
        mean_out = sum(outs) / 4
        repulsion = sum(o - mean_out for o in outs) / 4
        tension = (repulsion ** 2).mean(dim=-1, keepdim=True)
        direction = F.normalize(repulsion, dim=-1)
        output = self.tension_scale * torch.sqrt(tension + 1e-8) * direction
        return output, tension.squeeze()


if __name__ == '__main__':
    from model_utils import load_mnist, train_and_evaluate

    print("PureFieldEngine 테스트 (MNIST)")
    model = PureFieldEngine(784, 128, 10)
    print(f"  파라미터: {sum(p.numel() for p in model.parameters()):,}")

    # Quick test
    x = torch.randn(32, 784)
    out, tension = model(x)
    print(f"  output shape: {out.shape}")
    print(f"  tension shape: {tension.shape}")
    print(f"  tension mean: {tension.mean():.4f}")
