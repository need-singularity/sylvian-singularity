#!/usr/bin/env python3
"""의식엔진 확신(confidence) 분석기

사용법:
  python3 calc/confidence_analyzer.py --dataset mnist
  python3 calc/confidence_analyzer.py --dataset fashion --reject 50

기능:
  1. per-class 장력(=확신) 프로파일
  2. 과신(overconfidence) 클래스 감지 (ratio < 1)
  3. 확신 기반 판단 거부 시 정확도 곡선
  4. Dunning-Kruger 시간축 (에폭별 ratio 변화)
"""

import sys, argparse
sys.path.insert(0, '/Users/ghost/Dev/logout')

import torch, torch.nn as nn, torch.nn.functional as F, numpy as np

class RepulsionEngine(nn.Module):
    def __init__(self, d=784, h=128, o=10):
        super().__init__()
        self.ea = nn.Sequential(nn.Linear(d,h), nn.ReLU(), nn.Linear(h,o))
        self.eg = nn.Sequential(nn.Linear(d,h), nn.ReLU(), nn.Linear(h,o))
        self.eq = nn.Linear(d, o)
        self.ts = nn.Parameter(torch.tensor(0.3))
    def forward(self, x):
        a, g = self.ea(x), self.eg(x)
        t = ((a-g)**2).mean(-1, keepdim=True)
        return self.eq(x) + self.ts*torch.sqrt(t+1e-8)*F.normalize(a-g,dim=-1), t.squeeze()

def load_data(name):
    from torchvision import datasets, transforms
    from torch.utils.data import DataLoader
    if name == 'mnist':
        t = transforms.Compose([transforms.ToTensor(), transforms.Normalize((0.1307,),(0.3081,))])
        tr = datasets.MNIST('/tmp/data', train=True, download=True, transform=t)
        te = datasets.MNIST('/tmp/data', train=False, transform=t)
        return 784, 10, DataLoader(tr,256,True), DataLoader(te,512), [str(i) for i in range(10)]
    elif name == 'fashion':
        t = transforms.Compose([transforms.ToTensor(), transforms.Normalize((0.2860,),(0.3530,))])
        tr = datasets.FashionMNIST('/tmp/data', train=True, download=True, transform=t)
        te = datasets.FashionMNIST('/tmp/data', train=False, transform=t)
        return 784, 10, DataLoader(tr,256,True), DataLoader(te,512), \
            ['T-shirt','Trouser','Pullover','Dress','Coat','Sandal','Shirt','Sneaker','Bag','Boot']
    elif name == 'cifar':
        t = transforms.Compose([transforms.ToTensor(), transforms.Normalize((0.5,0.5,0.5),(0.5,0.5,0.5))])
        tr = datasets.CIFAR10('/tmp/data', train=True, download=True, transform=t)
        te = datasets.CIFAR10('/tmp/data', train=False, transform=t)
        return 3072, 10, DataLoader(tr,256,True), DataLoader(te,512), \
            ['airplane','auto','bird','cat','deer','dog','frog','horse','ship','truck']

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--dataset', default='mnist', choices=['mnist','fashion','cifar'])
    parser.add_argument('--epochs', type=int, default=10)
    parser.add_argument('--reject', type=int, default=0, help='rejection percentage (0-99)')
    args = parser.parse_args()

    dim, n_cls, tl, te, names = load_data(args.dataset)
    m = RepulsionEngine(dim, 128, n_cls)
    o = torch.optim.Adam(m.parameters(), lr=0.001)

    print(f"\n  의식엔진 확신 분석기 — {args.dataset.upper()}")
    print(f"  {'='*50}")

    # Train
    for ep in range(args.epochs):
        m.train()
        for x,y in tl:
            o.zero_grad(); out,_ = m(x.view(-1,dim))
            nn.CrossEntropyLoss()(out,y).backward(); o.step()

    # Evaluate
    m.eval(); T,Y,P = [],[],[]
    with torch.no_grad():
        for x,y in te:
            out,t = m(x.view(-1,dim)); T.append(t); Y.append(y); P.append(out.argmax(1))
    T=torch.cat(T).numpy(); Y=torch.cat(Y).numpy(); P=torch.cat(P).numpy()

    overall = (P==Y).mean()*100
    print(f"\n  전체 정확도: {overall:.2f}%")
    print(f"  tension_scale: {m.ts.item():.4f}")

    # Per-class profile
    print(f"\n  {'Class':>12} {'N':>5} {'Acc%':>6} {'T_mean':>8} {'ratio':>6} {'과신?':>6}")
    print(f"  {'-'*50}")
    overconf_classes = []
    for c in range(n_cls):
        mask = Y==c; correct = P[mask]==c
        acc = correct.mean()*100
        t_c = T[mask][correct].mean() if correct.sum()>0 else 0
        t_w = T[mask][~correct].mean() if (~correct).sum()>0 else 0
        ratio = t_c/(t_w+1e-10) if (~correct).sum()>0 else float('inf')
        oc = "⚠️" if ratio < 1.0 else ""
        if ratio < 1.0: overconf_classes.append(names[c])
        print(f"  {names[c]:>12} {mask.sum():>5} {acc:>6.1f} {T[mask].mean():>8.1f} {ratio:>6.2f} {oc:>6}")

    if overconf_classes:
        print(f"\n  ⚠️ 과신 클래스: {', '.join(overconf_classes)}")

    # Rejection curve
    if args.reject > 0:
        th = np.percentile(T, args.reject)
        mask = T >= th
        rej_acc = (P[mask]==Y[mask]).mean()*100
        print(f"\n  확신 거부 ({args.reject}%): {overall:.2f}% → {rej_acc:.2f}% (+{rej_acc-overall:.2f}%)")
    else:
        print(f"\n  확신 거부 곡선:")
        for r in [0, 10, 30, 50, 70, 90]:
            th = np.percentile(T, r); mask = T >= th
            acc_r = (P[mask]==Y[mask]).mean()*100
            print(f"    거부 {r:>2}%: {acc_r:.2f}% ({mask.sum():>5}샘플)")

if __name__ == '__main__':
    main()
