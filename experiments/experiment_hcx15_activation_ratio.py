#!/usr/bin/env python3
"""H-CX-15: 최적 MoE 활성 비율 = 1-1/e?"""
import torch, torch.nn as nn, torch.nn.functional as F, numpy as np, math
from torchvision import datasets, transforms
from torch.utils.data import DataLoader

class SimpleMoE(nn.Module):
    def __init__(self, input_dim=784, hidden=64, output_dim=10, n_experts=8, k=5):
        super().__init__()
        self.experts = nn.ModuleList([nn.Sequential(nn.Linear(input_dim, hidden), nn.ReLU(), nn.Linear(hidden, output_dim)) for _ in range(n_experts)])
        self.gate = nn.Linear(input_dim, n_experts)
        self.k = k
    def forward(self, x):
        scores = self.gate(x)
        topk_v, topk_i = scores.topk(self.k, dim=-1)
        mask = torch.zeros_like(scores).scatter(-1, topk_i, 1.0)
        weights = F.softmax(scores, dim=-1) * mask
        weights = weights / (weights.sum(-1, keepdim=True) + 1e-8)
        outs = torch.stack([e(x) for e in self.experts], dim=1)
        return (weights.unsqueeze(-1) * outs).sum(1)

transform = transforms.Compose([transforms.ToTensor(), transforms.Normalize((0.1307,), (0.3081,))])
train_ds = datasets.MNIST('/tmp/data', train=True, download=True, transform=transform)
test_ds = datasets.MNIST('/tmp/data', train=False, transform=transform)
tl = DataLoader(train_ds, batch_size=128, shuffle=True)
te = DataLoader(test_ds, batch_size=256)

print("="*60)
print("H-CX-15: MoE 활성 비율 스위프 (N=8)")
print("="*60)

results = []
for k in range(1, 9):
    accs = []
    for trial in range(3):
        model = SimpleMoE(784, 64, 10, 8, k)
        opt = torch.optim.Adam(model.parameters(), lr=0.001)
        for ep in range(10):
            model.train()
            for x, y in tl:
                opt.zero_grad()
                nn.CrossEntropyLoss()(model(x.view(-1,784)), y).backward()
                opt.step()
        model.eval()
        c = t = 0
        with torch.no_grad():
            for x, y in te:
                c += (model(x.view(-1,784)).argmax(1)==y).sum().item()
                t += len(y)
        accs.append(c/t*100)
    ratio = k/8
    mean_acc = np.mean(accs)
    results.append({'k': k, 'ratio': ratio, 'acc': mean_acc, 'std': np.std(accs)})
    marker = " ← 1-1/e" if abs(ratio - (1-1/math.e)) < 0.07 else ""
    print(f"  k={k}/8  ratio={ratio:.3f}  acc={mean_acc:.2f}±{np.std(accs):.2f}%{marker}")

# Find optimal
best = max(results, key=lambda r: r['acc'])
print(f"\n최적: k={best['k']}/8 ratio={best['ratio']:.3f} acc={best['acc']:.2f}%")
print(f"1-1/e = {1-1/math.e:.4f}")
print(f"최적 ratio와 1-1/e 오차: {abs(best['ratio']-(1-1/math.e)):.4f}")

# ASCII graph
print(f"\n활성 비율 vs 정확도")
for r in results:
    bar = '#' * int((r['acc'] - 90) * 5)
    marker = " <<<" if r['k'] == best['k'] else ""
    e_mark = " [1-1/e]" if abs(r['ratio'] - (1-1/math.e)) < 0.07 else ""
    print(f"  k={r['k']}({r['ratio']:.2f}) |{bar}| {r['acc']:.2f}%{marker}{e_mark}")

# Dropout sweep
print(f"\n{'='*60}")
print("Dropout 스위프 (Dense MLP)")
print("="*60)

class DenseMLP(nn.Module):
    def __init__(self, drop=0.5):
        super().__init__()
        self.net = nn.Sequential(nn.Linear(784,128), nn.ReLU(), nn.Dropout(drop), nn.Linear(128,10))
    def forward(self, x): return self.net(x)

drop_results = []
for drop in [0, 0.1, 0.2, 0.3, 0.37, 0.5, 0.7]:
    accs = []
    for trial in range(3):
        m = DenseMLP(drop)
        opt = torch.optim.Adam(m.parameters(), lr=0.001)
        for ep in range(10):
            m.train()
            for x, y in tl:
                opt.zero_grad()
                nn.CrossEntropyLoss()(m(x.view(-1,784)), y).backward()
                opt.step()
        m.eval()
        c = t = 0
        with torch.no_grad():
            for x, y in te:
                c += (m(x.view(-1,784)).argmax(1)==y).sum().item()
                t += len(y)
        accs.append(c/t*100)
    mean_acc = np.mean(accs)
    drop_results.append({'drop': drop, 'acc': mean_acc, 'std': np.std(accs)})
    marker = " ← 1/e" if abs(drop - 1/math.e) < 0.04 else ""
    print(f"  drop={drop:.2f}  acc={mean_acc:.2f}±{np.std(accs):.2f}%{marker}")

best_d = max(drop_results, key=lambda r: r['acc'])
print(f"\n최적 dropout: {best_d['drop']:.2f} acc={best_d['acc']:.2f}%")
print(f"1/e = {1/math.e:.4f}")
print(f"완료")
