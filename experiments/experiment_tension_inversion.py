#!/usr/bin/env python3
"""장력 방향 반전 조사: 왜 이상=낮은 간장력인가?"""
import torch, torch.nn as nn, torch.nn.functional as F, numpy as np, copy
from sklearn.datasets import load_breast_cancer
from sklearn.preprocessing import StandardScaler

class SimpleAE(nn.Module):
    def __init__(self, dim, h=64):
        super().__init__()
        self.ea = nn.Sequential(nn.Linear(dim,h), nn.ReLU(), nn.Linear(h,dim))
        self.eg = nn.Sequential(nn.Linear(dim,h), nn.ReLU(), nn.Linear(h,dim))
        self.eq = nn.Linear(dim, dim)
    def forward(self, x):
        a, g = self.ea(x), self.eg(x)
        out = self.eq(x) + 0.3*(a-g)
        return out, a, g

data = load_breast_cancer()
X, y = data.data, data.target
scaler = StandardScaler()
X = scaler.fit_transform(X)
X_n = X[y==1]; X_a = X[y==0]
np.random.seed(42)
idx = np.random.permutation(len(X_n))
X_train = torch.FloatTensor(X_n[idx[:250]])
X_test_n = torch.FloatTensor(X_n[idx[250:]])
X_test_a = torch.FloatTensor(X_a)

# Train parent
parent = SimpleAE(30)
opt = torch.optim.Adam(parent.parameters(), lr=0.001)
for ep in range(50):
    opt.zero_grad()
    out, _, _ = parent(X_train)
    F.mse_loss(out, X_train).backward()
    opt.step()

# Mitosis
ca = copy.deepcopy(parent); cb = copy.deepcopy(parent)
with torch.no_grad():
    for p in ca.parameters(): p.add_(torch.randn_like(p)*0.01)
    for p in cb.parameters(): p.add_(torch.randn_like(p)*0.01)

# Train children independently
oa = torch.optim.Adam(ca.parameters(), lr=0.001)
ob = torch.optim.Adam(cb.parameters(), lr=0.001)
for ep in range(30):
    perm = torch.randperm(len(X_train)); half = len(perm)//2
    ca.train(); oa.zero_grad()
    out_a, _, _ = ca(X_train[perm[:half]])
    F.mse_loss(out_a, X_train[perm[:half]]).backward(); oa.step()
    cb.train(); ob.zero_grad()
    out_b, _, _ = cb(X_train[perm[half:]])
    F.mse_loss(out_b, X_train[perm[half:]]).backward(); ob.step()

# Analyze
ca.eval(); cb.eval()
with torch.no_grad():
    for label, Xt, name in [(0, X_test_n, "NORMAL"), (1, X_test_a, "ANOMALY")]:
        out_a, ea_a, eg_a = ca(Xt)
        out_b, ea_b, eg_b = cb(Xt)
        
        int_a = ((ea_a - eg_a)**2).mean(-1)
        int_b = ((ea_b - eg_b)**2).mean(-1)
        inter = ((out_a - out_b)**2).mean(-1)
        recon_a = ((out_a - Xt)**2).mean(-1)
        recon_b = ((out_b - Xt)**2).mean(-1)
        
        print(f"\n{'='*50}")
        print(f"  {name} (N={len(Xt)})")
        print(f"{'='*50}")
        print(f"  Internal tension (child_a):  {int_a.mean():.6f} ± {int_a.std():.6f}")
        print(f"  Internal tension (child_b):  {int_b.mean():.6f} ± {int_b.std():.6f}")
        print(f"  Inter tension (a vs b):      {inter.mean():.6f} ± {inter.std():.6f}")
        print(f"  Recon error (child_a):       {recon_a.mean():.6f} ± {recon_a.std():.6f}")
        print(f"  Recon error (child_b):       {recon_b.mean():.6f} ± {recon_b.std():.6f}")
        print(f"  Output norm (child_a):       {out_a.norm(dim=-1).mean():.6f}")
        print(f"  Output norm (child_b):       {out_b.norm(dim=-1).mean():.6f}")

# Direct comparison
with torch.no_grad():
    out_an, _, _ = ca(X_test_n); out_bn, _, _ = cb(X_test_n)
    out_aa, _, _ = ca(X_test_a); out_ba, _, _ = cb(X_test_a)
    inter_n = ((out_an - out_bn)**2).mean(-1)
    inter_a = ((out_aa - out_ba)**2).mean(-1)
    recon_n = ((out_an - X_test_n)**2).mean(-1)
    recon_a = ((out_aa - X_test_a)**2).mean(-1)

print(f"\n{'='*50}")
print(f"  COMPARISON")
print(f"{'='*50}")
print(f"  Inter tension normal:  {inter_n.mean():.6f}")
print(f"  Inter tension anomaly: {inter_a.mean():.6f}")
print(f"  Ratio (anom/norm):     {inter_a.mean()/inter_n.mean():.4f}")
print(f"  Direction:             {'HIGHER for anomaly' if inter_a.mean() > inter_n.mean() else 'LOWER for anomaly (INVERTED!)'}")
print(f"\n  Recon error normal:    {recon_n.mean():.6f}")
print(f"  Recon error anomaly:   {recon_a.mean():.6f}")
print(f"  Ratio (anom/norm):     {recon_a.mean()/recon_n.mean():.4f}")
print(f"  Direction:             {'HIGHER for anomaly' if recon_a.mean() > recon_n.mean() else 'LOWER for anomaly'}")

print(f"\n  INTERPRETATION:")
if inter_a.mean() < inter_n.mean():
    print(f"  → 이상=낮은 간장력 확인")
    print(f"  → 'Agreement in confusion': 둘 다 이상을 못 복원 → 비슷한 실패 → 낮은 차이")
    print(f"  → 정상: 각자 다르게 잘 복원 → 높은 차이")
else:
    print(f"  → 이상=높은 간장력 (예상대로)")
print(f"\n완료")
