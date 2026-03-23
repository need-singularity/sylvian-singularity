#!/usr/bin/env python3
"""공통 유틸리티 — 7개 모델이 공유하는 컴포넌트

수학적 상수 (완전수 6에서 유도):
  sigma(6) = 12  (약수합)
  tau(6)   = 4   (약수 개수)
  phi(6)   = 2   (오일러 토션트)
  sigma_{-1}(6) = 2  (약수역수합)
  {1/2, 1/3, 1/6} = 약수역수 (합=1, 확률분포)
"""

import torch
import torch.nn as nn
import torch.nn.functional as F
from torch.utils.data import DataLoader
from torchvision import datasets, transforms
import numpy as np
import math
import time

# ─────────────────────────────────────────
# 수학 상수
# ─────────────────────────────────────────
SIGMA = 12       # sigma(6)
TAU = 4          # tau(6)
PHI = 2          # phi(6)
SIGMA_INV = 2    # sigma_{-1}(6)
DIVISOR_RECIPROCALS = [1/2, 1/3, 1/6]  # 합=1, 확률분포
H_TARGET = sum(-p * math.log(p) for p in DIVISOR_RECIPROCALS)  # Shannon entropy


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
# 기본 게이트
# ─────────────────────────────────────────
class TopKGate(nn.Module):
    def __init__(self, input_dim, n_experts, k=2):
        super().__init__()
        self.gate = nn.Linear(input_dim, n_experts)
        self.k = k

    def forward(self, x):
        scores = self.gate(x)
        topk_vals, topk_idx = scores.topk(self.k, dim=-1)
        mask = torch.zeros_like(scores)
        mask.scatter_(-1, topk_idx, 1.0)
        weights = F.softmax(scores, dim=-1) * mask
        return weights / (weights.sum(dim=-1, keepdim=True) + 1e-8)


class BoltzmannGate(nn.Module):
    def __init__(self, input_dim, n_experts, temperature=np.e, active_ratio=0.7):
        super().__init__()
        self.gate = nn.Linear(input_dim, n_experts)
        self.temperature = temperature
        self.n_active = max(1, int(n_experts * active_ratio))

    def forward(self, x):
        scores = self.gate(x) / self.temperature
        probs = F.softmax(scores, dim=-1)
        topk_vals, topk_idx = probs.topk(self.n_active, dim=-1)
        mask = torch.zeros_like(probs)
        mask.scatter_(-1, topk_idx, 1.0)
        weights = probs * mask
        return weights / (weights.sum(dim=-1, keepdim=True) + 1e-8)


# ─────────────────────────────────────────
# 기본 MoE
# ─────────────────────────────────────────
class BaseMoE(nn.Module):
    def __init__(self, input_dim, hidden_dim, output_dim, n_experts, gate):
        super().__init__()
        self.experts = nn.ModuleList([
            Expert(input_dim, hidden_dim, output_dim)
            for _ in range(n_experts)
        ])
        self.gate = gate
        self.n_experts = n_experts
        self.expert_usage = torch.zeros(n_experts)
        self.active_counts = []

    def forward(self, x):
        weights = self.gate(x)
        outputs = torch.stack([e(x) for e in self.experts], dim=1)
        result = (weights.unsqueeze(-1) * outputs).sum(dim=1)

        with torch.no_grad():
            active = (weights > 0.01).float().sum(dim=-1).mean().item()
            self.active_counts.append(active)
            self.expert_usage += (weights > 0.01).float().sum(dim=0).mean(dim=0).cpu()

        return result

    def get_metrics(self):
        usage = self.expert_usage / max(self.expert_usage.sum().item(), 1)
        avg_active = np.mean(self.active_counts) if self.active_counts else 0
        return {
            'avg_active': avg_active,
            'active_ratio': avg_active / self.n_experts if self.n_experts > 0 else 0,
            'I_effective': 1 - avg_active / self.n_experts if self.n_experts > 0 else 0,
            'usage_std': usage.std().item(),
        }

    def reset_metrics(self):
        self.expert_usage = torch.zeros(self.n_experts)
        self.active_counts = []


# ─────────────────────────────────────────
# Dense 모델 (baseline)
# ─────────────────────────────────────────
class DenseModel(nn.Module):
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
# 데이터 로더
# ─────────────────────────────────────────
def load_mnist(batch_size=128, data_dir='data'):
    transform = transforms.Compose([
        transforms.ToTensor(),
        transforms.Normalize((0.1307,), (0.3081,))
    ])
    train_ds = datasets.MNIST(data_dir, train=True, download=True, transform=transform)
    test_ds = datasets.MNIST(data_dir, train=False, transform=transform)
    train_loader = DataLoader(train_ds, batch_size=batch_size, shuffle=True, num_workers=0)
    test_loader = DataLoader(test_ds, batch_size=batch_size, shuffle=False, num_workers=0)
    return train_loader, test_loader


# ─────────────────────────────────────────
# 학습 + 평가
# ─────────────────────────────────────────
def train_and_evaluate(model, train_loader, test_loader, epochs=10, lr=0.001,
                       optimizer=None, aux_loss_fn=None, aux_lambda=0.1,
                       flatten=True, verbose=True):
    """공통 학습 루프.

    Args:
        optimizer: None이면 Adam 사용. 커스텀 옵티마이저 주입 가능 (모델 C용).
        aux_loss_fn: 보조 loss 함수 (모델 G용). model output에서 추출.
        aux_lambda: 보조 loss 가중치.
        flatten: True면 입력을 1D로 펼침 (MNIST용).
    """
    if optimizer is None:
        optimizer = torch.optim.Adam(model.parameters(), lr=lr)
    criterion = nn.CrossEntropyLoss()

    train_losses = []
    test_accs = []

    for epoch in range(epochs):
        model.train()
        total_loss = 0
        for X, y in train_loader:
            if flatten:
                X = X.view(X.size(0), -1)
            optimizer.zero_grad()
            out = model(X)

            if isinstance(out, tuple):
                logits, aux = out
                loss = criterion(logits, y) + aux_lambda * aux
            else:
                logits = out
                loss = criterion(logits, y)

            loss.backward()
            optimizer.step()
            total_loss += loss.item()

        avg_loss = total_loss / len(train_loader)
        train_losses.append(avg_loss)

        model.eval()
        correct = total = 0
        with torch.no_grad():
            for X, y in test_loader:
                if flatten:
                    X = X.view(X.size(0), -1)
                out = model(X)
                if isinstance(out, tuple):
                    out = out[0]
                correct += (out.argmax(1) == y).sum().item()
                total += y.size(0)
        acc = correct / total
        test_accs.append(acc)

        if verbose and ((epoch + 1) % 2 == 0 or epoch == 0):
            print(f"    Epoch {epoch+1:>2}/{epochs}: Loss={avg_loss:.4f}, Acc={acc*100:.1f}%")

    return train_losses, test_accs


# ─────────────────────────────────────────
# 결과 비교
# ─────────────────────────────────────────
def compare_results(results):
    """results: dict of {name: {'acc': float, 'loss': float, 'params': int, ...}}"""
    print("\n" + "=" * 70)
    print(f"  {'모델':<30} {'정확도':>8} {'Loss':>8} {'파라미터':>10}")
    print("-" * 70)
    for name, r in sorted(results.items(), key=lambda x: -x[1].get('acc', 0)):
        acc = r.get('acc', 0)
        loss = r.get('loss', 0)
        params = r.get('params', 0)
        marker = ' <-- best' if acc == max(v.get('acc', 0) for v in results.values()) else ''
        print(f"  {name:<30} {acc*100:>7.2f}% {loss:>8.4f} {params:>10,}{marker}")
    print("=" * 70)


def count_params(model):
    return sum(p.numel() for p in model.parameters())
