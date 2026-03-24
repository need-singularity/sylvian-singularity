#!/usr/bin/env python3
"""H307: MNIST에서 이중 메커니즘 재현"""
import torch, torch.nn as nn, torch.nn.functional as F, numpy as np, copy
from torchvision import datasets, transforms
from torch.utils.data import DataLoader, Subset
from sklearn.metrics import roc_auc_score

class SimpleAE(nn.Module):
    def __init__(self, dim=784, h=128):
        super().__init__()
        self.ea = nn.Sequential(nn.Linear(dim,h), nn.ReLU(), nn.Linear(h,dim))
        self.eg = nn.Sequential(nn.Linear(dim,h), nn.ReLU(), nn.Linear(h,dim))
        self.eq = nn.Linear(dim, dim)
    def forward(self, x):
        a, g = self.ea(x), self.eg(x)
        return self.eq(x) + 0.3*(a-g), a, g

transform = transforms.Compose([transforms.ToTensor(), transforms.Normalize((0.1307,),(0.3081,))])
train_full = datasets.MNIST('/tmp/data', train=True, download=True, transform=transform)
test_full = datasets.MNIST('/tmp/data', train=False, transform=transform)

# Normal=digit 0, Anomaly=digit 1
train_idx = [i for i, (_, y) in enumerate(train_full) if y == 0]
test_norm = [i for i, (_, y) in enumerate(test_full) if y == 0]
test_anom = [i for i, (_, y) in enumerate(test_full) if y == 1]

train_loader = DataLoader(Subset(train_full, train_idx), batch_size=128, shuffle=True)
test_n_loader = DataLoader(Subset(test_full, test_norm), batch_size=256)
test_a_loader = DataLoader(Subset(test_full, test_anom), batch_size=256)

print("="*60)
print("H307: MNIST 이중 메커니즘 (digit0=정상, digit1=이상)")
print("="*60)

for trial in range(3):
    parent = SimpleAE(784, 128)
    opt = torch.optim.Adam(parent.parameters(), lr=0.001)
    for ep in range(10):
        parent.train()
        for x, _ in train_loader:
            x = x.view(-1,784)
            opt.zero_grad()
            out, _, _ = parent(x)
            F.mse_loss(out, x).backward()
            opt.step()

    ca = copy.deepcopy(parent); cb = copy.deepcopy(parent)
    with torch.no_grad():
        for p in ca.parameters(): p.add_(torch.randn_like(p)*0.01)
        for p in cb.parameters(): p.add_(torch.randn_like(p)*0.01)

    oa = torch.optim.Adam(ca.parameters(), lr=0.001)
    ob = torch.optim.Adam(cb.parameters(), lr=0.001)
    for ep in range(10):
        ca.train(); cb.train()
        for x, _ in train_loader:
            x = x.view(-1,784)
            perm = torch.randperm(len(x)); half = len(perm)//2
            oa.zero_grad(); out_a, _, _ = ca(x[perm[:half]]); F.mse_loss(out_a, x[perm[:half]]).backward(); oa.step()
            ob.zero_grad(); out_b, _, _ = cb(x[perm[half:]]); F.mse_loss(out_b, x[perm[half:]]).backward(); ob.step()

    ca.eval(); cb.eval()
    stats = {}
    with torch.no_grad():
        for name, loader in [("normal", test_n_loader), ("anomaly", test_a_loader)]:
            int_ts, inter_ts, recons = [], [], []
            for x, _ in loader:
                x = x.view(-1,784)
                out_a, ea_a, eg_a = ca(x)
                out_b, ea_b, eg_b = cb(x)
                int_ts.append(((ea_a-eg_a)**2).mean(-1))
                inter_ts.append(((out_a-out_b)**2).mean(-1))
                recons.append(((out_a-x)**2).mean(-1))
            stats[name] = {
                'internal': torch.cat(int_ts),
                'inter': torch.cat(inter_ts),
                'recon': torch.cat(recons)
            }

    print(f"\n  Trial {trial+1}:")
    for metric in ['internal', 'inter', 'recon']:
        n_val = stats['normal'][metric].mean().item()
        a_val = stats['anomaly'][metric].mean().item()
        ratio = a_val / (n_val + 1e-10)
        direction = "HIGHER" if a_val > n_val else "LOWER (inverted)"
        y_true = np.concatenate([np.zeros(len(stats['normal'][metric])), np.ones(len(stats['anomaly'][metric]))])
        scores = torch.cat([stats['normal'][metric], stats['anomaly'][metric]]).numpy()
        auroc = roc_auc_score(y_true, scores)
        print(f"    {metric:>10}: normal={n_val:.4f} anomaly={a_val:.4f} ratio={ratio:.2f}x {direction} AUROC={auroc:.4f}")

print(f"\n완료")
