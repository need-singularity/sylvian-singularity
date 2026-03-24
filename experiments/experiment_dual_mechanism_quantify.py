#!/usr/bin/env python3
"""이중 메커니즘 정량화: 내부반전비 × 간정상비 = 상수?"""
import torch, torch.nn as nn, torch.nn.functional as F, numpy as np, copy
from sklearn.datasets import load_breast_cancer, load_iris, load_wine
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import roc_auc_score

class SimpleAE(nn.Module):
    def __init__(self, dim, h=64):
        super().__init__()
        self.ea = nn.Sequential(nn.Linear(dim,h), nn.ReLU(), nn.Linear(h,dim))
        self.eg = nn.Sequential(nn.Linear(dim,h), nn.ReLU(), nn.Linear(h,dim))
        self.eq = nn.Linear(dim, dim)
    def forward(self, x):
        a, g = self.ea(x), self.eg(x)
        return self.eq(x) + 0.3*(a-g), a, g

def run_dataset(name, X, y, normal_label):
    scaler = StandardScaler(); X = scaler.fit_transform(X)
    X_n = X[y==normal_label]; X_a = X[y!=normal_label]
    if len(X_a) > 200: X_a = X_a[:200]
    np.random.seed(42); idx = np.random.permutation(len(X_n))
    n_train = max(int(0.7*len(X_n)), 20)
    X_train = torch.FloatTensor(X_n[idx[:n_train]])
    X_test_n = torch.FloatTensor(X_n[idx[n_train:]])
    X_test_a = torch.FloatTensor(X_a)
    dim = X.shape[1]
    
    ratios = []
    for trial in range(3):
        parent = SimpleAE(dim); opt = torch.optim.Adam(parent.parameters(), lr=0.001)
        for ep in range(50):
            opt.zero_grad(); out, _, _ = parent(X_train); F.mse_loss(out, X_train).backward(); opt.step()
        ca, cb = copy.deepcopy(parent), copy.deepcopy(parent)
        with torch.no_grad():
            for p in ca.parameters(): p.add_(torch.randn_like(p)*0.01)
            for p in cb.parameters(): p.add_(torch.randn_like(p)*0.01)
        oa, ob = torch.optim.Adam(ca.parameters(), lr=0.001), torch.optim.Adam(cb.parameters(), lr=0.001)
        for ep in range(30):
            perm = torch.randperm(len(X_train)); h = len(perm)//2
            ca.train(); oa.zero_grad(); out_a, _, _ = ca(X_train[perm[:h]]); F.mse_loss(out_a, X_train[perm[:h]]).backward(); oa.step()
            cb.train(); ob.zero_grad(); out_b, _, _ = cb(X_train[perm[h:]]); F.mse_loss(out_b, X_train[perm[h:]]).backward(); ob.step()
        ca.eval(); cb.eval()
        with torch.no_grad():
            for Xt, lbl in [(X_test_n, "norm"), (X_test_a, "anom")]:
                if len(Xt) == 0: continue
                out_a, ea_a, eg_a = ca(Xt); out_b, _, _ = cb(Xt)
                internal = ((ea_a-eg_a)**2).mean(-1).mean().item()
                inter = ((out_a-out_b)**2).mean(-1).mean().item()
                if lbl == "norm": int_n, inter_n = internal, inter
                else: int_a, inter_a = internal, inter
        
        int_ratio = int_a / (int_n + 1e-10)  # 내부: <1이면 반전
        inter_ratio = inter_a / (inter_n + 1e-10)  # 간: >1이면 정상
        product = int_ratio * inter_ratio
        ratios.append({'int_ratio': int_ratio, 'inter_ratio': inter_ratio, 'product': product})
    
    avg_int = np.mean([r['int_ratio'] for r in ratios])
    avg_inter = np.mean([r['inter_ratio'] for r in ratios])
    avg_prod = np.mean([r['product'] for r in ratios])
    print(f"  {name:>15}: int_ratio={avg_int:.4f} inter_ratio={avg_inter:.4f} product={avg_prod:.4f}")
    return avg_int, avg_inter, avg_prod

print("="*60)
print("이중 메커니즘 정량화: 내부반전비 × 간정상비 = 상수?")
print("="*60)

datasets_info = [
    ("Cancer", *load_breast_cancer(return_X_y=True), 1),
    ("Iris", *load_iris(return_X_y=True), 0),
    ("Wine", *load_wine(return_X_y=True), 0),
]

all_results = []
for name, X, y, nl in datasets_info:
    ir, jr, pr = run_dataset(name, X, y, nl)
    all_results.append({'name': name, 'int_ratio': ir, 'inter_ratio': jr, 'product': pr})

print(f"\n  {'Dataset':>15} {'int_r':>8} {'inter_r':>8} {'product':>8}")
print(f"  {'-'*40}")
for r in all_results:
    print(f"  {r['name']:>15} {r['int_ratio']:>8.4f} {r['inter_ratio']:>8.4f} {r['product']:>8.4f}")

products = [r['product'] for r in all_results]
print(f"\n  product 평균: {np.mean(products):.4f}")
print(f"  product std:  {np.std(products):.4f}")
print(f"  product CV:   {np.std(products)/np.mean(products):.4f}")

if np.std(products)/np.mean(products) < 0.3:
    print(f"  → product ≈ 상수! ({np.mean(products):.3f})")
else:
    print(f"  → product 비상수 (CV > 0.3)")
print(f"\n완료")
