#!/usr/bin/env python3
"""골든 MoE v2 — PyTorch 역전파 + MNIST 벤치마크

비교:
  1. Top-K MoE (K=2, 25% 활성)
  2. 골든 MoE (볼츠만 T=e, ~70% 활성)
  3. Dense (전체 활성, 비교군)
"""

import torch
import torch.nn as nn
import torch.nn.functional as F
from torch.utils.data import DataLoader
from torchvision import datasets, transforms
import numpy as np
import time
import os


# ─────────────────────────────────────────
# 라우터
# ─────────────────────────────────────────
class TopKGate(nn.Module):
    def __init__(self, input_dim, n_experts, k=2):
        super().__init__()
        self.gate = nn.Linear(input_dim, n_experts)
        self.k = k

    def forward(self, x):
        scores = self.gate(x)  # (batch, n_experts)
        topk_vals, topk_idx = scores.topk(self.k, dim=-1)
        mask = torch.zeros_like(scores)
        mask.scatter_(-1, topk_idx, 1.0)
        weights = F.softmax(scores, dim=-1) * mask
        weights = weights / (weights.sum(dim=-1, keepdim=True) + 1e-8)
        return weights


class BoltzmannGate(nn.Module):
    def __init__(self, input_dim, n_experts, temperature=np.e, active_ratio=0.7):
        super().__init__()
        self.gate = nn.Linear(input_dim, n_experts)
        self.temperature = temperature
        self.n_active = max(1, int(n_experts * active_ratio))

    def forward(self, x):
        scores = self.gate(x) / self.temperature  # 볼츠만 온도
        probs = F.softmax(scores, dim=-1)
        # 상위 n_active개 활성
        topk_vals, topk_idx = probs.topk(self.n_active, dim=-1)
        mask = torch.zeros_like(probs)
        mask.scatter_(-1, topk_idx, 1.0)
        weights = probs * mask
        weights = weights / (weights.sum(dim=-1, keepdim=True) + 1e-8)
        return weights


# ─────────────────────────────────────────
# Expert
# ─────────────────────────────────────────
class Expert(nn.Module):
    def __init__(self, input_dim, hidden_dim, output_dim, dropout=0.5):
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
# MoE 모델
# ─────────────────────────────────────────
class MoEModel(nn.Module):
    def __init__(self, input_dim, hidden_dim, output_dim, n_experts=8,
                 gate_type='boltzmann', k=2, temperature=np.e,
                 active_ratio=0.7, dropout=0.5):
        super().__init__()
        self.experts = nn.ModuleList([
            Expert(input_dim, hidden_dim, output_dim, dropout)
            for _ in range(n_experts)
        ])
        self.n_experts = n_experts
        self.gate_type = gate_type

        if gate_type == 'topk':
            self.gate = TopKGate(input_dim, n_experts, k)
        elif gate_type == 'boltzmann':
            self.gate = BoltzmannGate(input_dim, n_experts, temperature, active_ratio)
        else:  # dense
            self.gate = None

        self.expert_usage = torch.zeros(n_experts)
        self.active_counts = []

    def forward(self, x):
        expert_outputs = torch.stack([e(x) for e in self.experts], dim=1)  # (batch, n_experts, output)

        if self.gate is None:  # Dense
            output = expert_outputs.mean(dim=1)
            self.active_counts.append(self.n_experts)
        else:
            weights = self.gate(x)  # (batch, n_experts)
            output = (weights.unsqueeze(-1) * expert_outputs).sum(dim=1)

            with torch.no_grad():
                active = (weights > 0).float().sum(dim=-1).mean().item()
                self.active_counts.append(active)
                self.expert_usage += (weights > 0).float().sum(dim=0).mean(dim=0).cpu()

        return output

    def get_metrics(self):
        usage = self.expert_usage / max(self.expert_usage.sum().item(), 1)
        avg_active = np.mean(self.active_counts) if self.active_counts else 0
        return {
            'avg_active': avg_active,
            'active_ratio': avg_active / self.n_experts,
            'usage_std': usage.std().item(),
            'usage_dist': usage.numpy(),
            'I_effective': 1 - avg_active / self.n_experts,
        }


# ─────────────────────────────────────────
# 학습 + 평가
# ─────────────────────────────────────────
def train_model(model, train_loader, test_loader, epochs=10, lr=0.001):
    optimizer = torch.optim.Adam(model.parameters(), lr=lr)
    criterion = nn.CrossEntropyLoss()

    train_losses = []
    test_accs = []

    for epoch in range(epochs):
        model.train()
        total_loss = 0
        for X, y in train_loader:
            X = X.view(X.size(0), -1)  # Flatten
            optimizer.zero_grad()
            out = model(X)
            loss = criterion(out, y)
            loss.backward()
            optimizer.step()
            total_loss += loss.item()

        avg_loss = total_loss / len(train_loader)
        train_losses.append(avg_loss)

        # 테스트
        model.eval()
        correct = 0
        total = 0
        with torch.no_grad():
            for X, y in test_loader:
                X = X.view(X.size(0), -1)
                out = model(X)
                pred = out.argmax(dim=1)
                correct += (pred == y).sum().item()
                total += y.size(0)

        acc = correct / total
        test_accs.append(acc)

        if (epoch + 1) % 2 == 0 or epoch == 0:
            print(f"    Epoch {epoch+1:>2}/{epochs}: Loss={avg_loss:.4f}, Acc={acc*100:.1f}%")

    return train_losses, test_accs


def main():
    print()
    print("═" * 60)
    print("   🧠 골든 MoE v2 — PyTorch + MNIST")
    print("═" * 60)

    # MNIST 데이터
    transform = transforms.Compose([
        transforms.ToTensor(),
        transforms.Normalize((0.1307,), (0.3081,))
    ])

    print("\n  데이터 로딩...", end=" ")
    train_data = datasets.MNIST('./data', train=True, download=True, transform=transform)
    test_data = datasets.MNIST('./data', train=False, transform=transform)

    train_loader = DataLoader(train_data, batch_size=128, shuffle=True)
    test_loader = DataLoader(test_data, batch_size=256, shuffle=False)
    print(f"완료 (train: {len(train_data)}, test: {len(test_data)})")

    input_dim = 784  # 28×28
    hidden_dim = 64
    output_dim = 10
    n_experts = 8
    epochs = 10

    configs = [
        ('Top-K (K=2, 25%)', 'topk', {'k': 2}),
        ('골든 MoE (T=e, 70%)', 'boltzmann', {'temperature': np.e, 'active_ratio': 0.7}),
        ('Dense (100%)', 'dense', {}),
    ]

    results = {}

    for name, gate_type, kwargs in configs:
        print(f"\n{'─' * 60}")
        print(f"  [{name}]")
        print(f"{'─' * 60}")

        model = MoEModel(
            input_dim, hidden_dim, output_dim,
            n_experts=n_experts, gate_type=gate_type,
            dropout=0.5, **kwargs
        )

        param_count = sum(p.numel() for p in model.parameters())
        print(f"  파라미터: {param_count:,}")

        start = time.time()
        losses, accs = train_model(model, train_loader, test_loader, epochs=epochs)
        elapsed = time.time() - start

        metrics = model.get_metrics()
        results[name] = {
            'accuracy': accs[-1],
            'best_accuracy': max(accs),
            'final_loss': losses[-1],
            'time': elapsed,
            'params': param_count,
            'losses': losses,
            'accs': accs,
            **metrics,
        }

    # ─── 비교 ───
    print(f"\n{'═' * 60}")
    print(f"  종합 비교")
    print(f"{'═' * 60}")

    print(f"\n  {'메트릭':20} │", end="")
    for name in results:
        print(f" {name[:12]:>12} │", end="")
    print()
    print(f"  {'─'*20}─┼" + "─" * 14 + "┼" + "─" * 14 + "┼" + "─" * 14 + "┤")

    metrics_list = [
        ('최종 정확도', 'accuracy', lambda x: f"{x*100:.1f}%", 'high'),
        ('최고 정확도', 'best_accuracy', lambda x: f"{x*100:.1f}%", 'high'),
        ('최종 Loss', 'final_loss', lambda x: f"{x:.4f}", 'low'),
        ('학습 시간(초)', 'time', lambda x: f"{x:.1f}s", 'low'),
        ('활성 비율', 'active_ratio', lambda x: f"{x*100:.0f}%", 'info'),
        ('유효 I', 'I_effective', lambda x: f"{x:.3f}", 'info'),
        ('Expert 균등σ', 'usage_std', lambda x: f"{x:.4f}", 'low'),
    ]

    for label, key, fmt, direction in metrics_list:
        print(f"  {label:20} │", end="")
        vals = []
        for name, r in results.items():
            val = r.get(key, 0)
            vals.append((name, val))
            print(f" {fmt(val):>12} │", end="")
        print()

    # 골든존 판정
    print(f"\n  골든존 판정:")
    for name, r in results.items():
        I = r['I_effective']
        if 0.213 <= I <= 0.500:
            zone = "🎯 골든존!"
        elif I < 0.213:
            zone = "⚡ 아래"
        else:
            zone = "○ 밖"
        G = 0.5 * 0.85 / max(I, 0.01)
        print(f"    {name:25}: I={I:.3f} G={G:.2f} {zone}")

    # Expert 활용 비교
    print(f"\n  Expert 활용 분포:")
    for name, r in results.items():
        if 'usage_dist' in r and r['usage_dist'] is not None:
            print(f"    [{name[:15]}]")
            for i, u in enumerate(r['usage_dist']):
                bar = "█" * int(u * 60)
                print(f"      E{i}: {bar} {u*100:.1f}%")

    # 정확도 궤적
    print(f"\n  정확도 궤적:")
    for epoch in range(epochs):
        line = f"    {epoch+1:>2} │"
        for name, r in results.items():
            acc = r['accs'][epoch]
            bar_char = "█" if 'Top' in name else ("▓" if '골든' in name else "░")
            bar = bar_char * int(acc * 20)
            line += f" {bar:20} │"
        print(line)
    print(f"       █=Top-K  ▓=골든MoE  ░=Dense")

    # 최종 판정
    print(f"\n{'═' * 60}")
    best = max(results.items(), key=lambda x: x[1]['best_accuracy'])
    print(f"  🏆 최고 정확도: {best[0]} ({best[1]['best_accuracy']*100:.1f}%)")

    golden = results.get('골든 MoE (T=e, 70%)', {})
    topk = results.get('Top-K (K=2, 25%)', {})
    if golden and topk:
        diff = golden['best_accuracy'] - topk['best_accuracy']
        print(f"  골든 MoE vs Top-K: {diff*100:+.1f}%")
        print(f"  골든 MoE I = {golden['I_effective']:.3f} {'🎯 골든존' if 0.213<=golden['I_effective']<=0.5 else ''}")

    print(f"\n{'═' * 60}")


if __name__ == '__main__':
    main()
