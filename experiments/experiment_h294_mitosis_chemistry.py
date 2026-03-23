#!/usr/bin/env python3
"""가설 294: 분열 + 뇌화학 — 분열 시 장력(도파민) 시스템 추적"""

import sys
sys.path.insert(0, '/Users/ghost/Dev/logout')

import torch
import torch.nn as nn
import torch.nn.functional as F
import numpy as np
import copy

class RepulsionEngine(nn.Module):
    def __init__(self, input_dim=784, hidden_dim=128, output_dim=10):
        super().__init__()
        self.engine_a = nn.Sequential(nn.Linear(input_dim, hidden_dim), nn.ReLU(), nn.Dropout(0.3), nn.Linear(hidden_dim, output_dim))
        self.engine_g = nn.Sequential(nn.Linear(input_dim, hidden_dim), nn.ReLU(), nn.Dropout(0.3), nn.Linear(hidden_dim, output_dim))
        self.tension_scale = nn.Parameter(torch.tensor(0.3))
        self.equilibrium = nn.Linear(input_dim, output_dim)

    def forward(self, x):
        out_a = self.engine_a(x)
        out_g = self.engine_g(x)
        repulsion = out_a - out_g
        tension = (repulsion ** 2).mean(dim=-1, keepdim=True)
        direction = F.normalize(repulsion, dim=-1)
        eq = self.equilibrium(x)
        return eq + self.tension_scale * torch.sqrt(tension + 1e-8) * direction, tension.mean(), out_a, out_g

def measure_tension(model, loader):
    model.eval()
    tensions = []
    correct = total = 0
    with torch.no_grad():
        for x, y in loader:
            x = x.view(x.size(0), -1)
            out, t, _, _ = model(x)
            tensions.append(t.item())
            correct += (out.argmax(1) == y).sum().item()
            total += y.size(0)
    return np.mean(tensions), correct / total * 100

def measure_inter_tension(model_a, model_b, loader):
    model_a.eval(); model_b.eval()
    tensions = []
    with torch.no_grad():
        for x, y in loader:
            x = x.view(x.size(0), -1)
            out_a, _, _, _ = model_a(x)
            out_b, _, _, _ = model_b(x)
            t_ab = ((out_a - out_b) ** 2).mean()
            tensions.append(t_ab.item())
    return np.mean(tensions)

def train_epoch(model, loader, opt, criterion):
    model.train()
    tensions = []
    for x, y in loader:
        x = x.view(x.size(0), -1)
        opt.zero_grad()
        out, t, _, _ = model(x)
        loss = criterion(out, y)
        loss.backward()
        opt.step()
        tensions.append(t.item())
    return np.mean(tensions)

def mitosis(parent, scale=0.01):
    child_a = copy.deepcopy(parent)
    child_b = copy.deepcopy(parent)
    with torch.no_grad():
        for p in child_a.parameters():
            p.add_(torch.randn_like(p) * scale)
        for p in child_b.parameters():
            p.add_(torch.randn_like(p) * scale)
    return child_a, child_b

def main():
    from torchvision import datasets, transforms
    from torch.utils.data import DataLoader

    print("=" * 70)
    print("가설 294: 분열 + 뇌화학 — 장력(도파민) 시스템 추적")
    print("=" * 70)

    transform = transforms.Compose([transforms.ToTensor(), transforms.Normalize((0.1307,), (0.3081,))])
    train_ds = datasets.MNIST('/tmp/data', train=True, download=True, transform=transform)
    test_ds = datasets.MNIST('/tmp/data', train=False, transform=transform)
    train_loader = DataLoader(train_ds, batch_size=128, shuffle=True)
    test_loader = DataLoader(test_ds, batch_size=256)

    # Phase 1: 부모 학습
    print("\n[Phase 1] 부모 학습 (10 에폭)")
    parent = RepulsionEngine()
    opt = torch.optim.Adam(parent.parameters(), lr=0.001)
    criterion = nn.CrossEntropyLoss()

    parent_history = []
    for ep in range(10):
        train_t = train_epoch(parent, train_loader, opt, criterion)
        test_t, test_acc = measure_tension(parent, test_loader)
        parent_history.append({'ep': ep+1, 'train_t': train_t, 'test_t': test_t, 'acc': test_acc})
        print(f"  ep{ep+1:2d}: tension={test_t:.4f}, acc={test_acc:.2f}%")

    # Phase 2: 분열
    print(f"\n[Phase 2] 분열 (scale=0.01)")
    child_a, child_b = mitosis(parent, scale=0.01)

    t_a_pre, acc_a_pre = measure_tension(child_a, test_loader)
    t_b_pre, acc_b_pre = measure_tension(child_b, test_loader)
    t_ab_pre = measure_inter_tension(child_a, child_b, test_loader)

    print(f"  분열 직후:")
    print(f"    T_a (child_a 내부): {t_a_pre:.4f}, acc={acc_a_pre:.2f}%")
    print(f"    T_b (child_b 내부): {t_b_pre:.4f}, acc={acc_b_pre:.2f}%")
    print(f"    T_ab (자식간):      {t_ab_pre:.4f}")
    print(f"    T_parent:           {parent_history[-1]['test_t']:.4f}")

    # Phase 3: 독립 학습
    print(f"\n[Phase 3] 독립 학습 (10 에폭 each)")
    opt_a = torch.optim.Adam(child_a.parameters(), lr=0.001)
    opt_b = torch.optim.Adam(child_b.parameters(), lr=0.001)

    child_history = []
    for ep in range(10):
        train_epoch(child_a, train_loader, opt_a, criterion)
        train_epoch(child_b, train_loader, opt_b, criterion)

        t_a, acc_a = measure_tension(child_a, test_loader)
        t_b, acc_b = measure_tension(child_b, test_loader)
        t_ab = measure_inter_tension(child_a, child_b, test_loader)

        child_history.append({
            'ep': ep+1, 't_a': t_a, 't_b': t_b, 't_ab': t_ab,
            'acc_a': acc_a, 'acc_b': acc_b
        })
        print(f"  ep{ep+1:2d}: T_a={t_a:.4f} T_b={t_b:.4f} T_ab={t_ab:.4f} acc_a={acc_a:.2f}% acc_b={acc_b:.2f}%")

    # Phase 4: 재결합 (앙상블)
    print(f"\n[Phase 4] 재결합 (앙상블)")
    child_a.eval(); child_b.eval()
    correct = total = 0
    with torch.no_grad():
        for x, y in test_loader:
            x = x.view(x.size(0), -1)
            out_a, _, _, _ = child_a(x)
            out_b, _, _, _ = child_b(x)
            out_ensemble = (out_a + out_b) / 2
            correct += (out_ensemble.argmax(1) == y).sum().item()
            total += y.size(0)
    ensemble_acc = correct / total * 100
    print(f"  앙상블 정확도: {ensemble_acc:.2f}%")
    print(f"  child_a 단독:  {child_history[-1]['acc_a']:.2f}%")
    print(f"  child_b 단독:  {child_history[-1]['acc_b']:.2f}%")
    print(f"  부모 최종:     {parent_history[-1]['acc']:.2f}%")

    # ── 종합 분석 ──
    print(f"\n{'='*70}")
    print("종합: 장력(도파민) 시스템 추적")
    print(f"{'='*70}")

    t_parent_final = parent_history[-1]['test_t']
    t_ab_final = child_history[-1]['t_ab']

    print(f"\n  Phase 1 (부모 학습):")
    print(f"    ep1  tension={parent_history[0]['test_t']:.4f}")
    print(f"    ep10 tension={t_parent_final:.4f}")

    print(f"\n  Phase 2 (분열 직후):")
    print(f"    T_ab = {t_ab_pre:.4f} (자식간) vs T_parent = {t_parent_final:.4f}")
    print(f"    비율: T_ab/T_parent = {t_ab_pre/(t_parent_final+1e-8):.4f}")

    print(f"\n  Phase 3 (독립 학습 후):")
    print(f"    T_ab = {t_ab_final:.4f}")
    print(f"    증가율: {t_ab_final/(t_ab_pre+1e-8):.1f}x")

    if t_ab_final > t_parent_final:
        print(f"\n  결론: T_ab(자식간) > T_parent(부모내부)")
        print(f"    → 분열 후 '도파민 시스템 분화' 확인")
        print(f"    → 독립 학습이 새로운 장력(도파민) 경로를 생성")
    else:
        print(f"\n  결론: T_ab(자식간) ≤ T_parent(부모내부)")
        print(f"    → 분열이 추가 장력을 만들지 않음")

    # ASCII 그래프
    print(f"\n장력 궤적 (분열 전후)")
    all_t = [h['test_t'] for h in parent_history]
    all_t += [t_ab_pre] + [h['t_ab'] for h in child_history]
    all_ta = [h['test_t'] for h in parent_history]
    all_ta += [t_a_pre] + [h['t_a'] for h in child_history]

    lo = min(min(all_t), min(all_ta))
    hi = max(max(all_t), max(all_ta))

    grid = [[' ']*42 for _ in range(12)]
    for i, v in enumerate(all_t):
        x = i * 2
        y = int((v - lo)/(hi - lo + 1e-8) * 11)
        y = min(11, max(0, y))
        if x < 42: grid[11-y][x] = 'X'  # T_ab or T_parent

    for i, v in enumerate(all_ta):
        x = i * 2
        y = int((v - lo)/(hi - lo + 1e-8) * 11)
        y = min(11, max(0, y))
        if x < 42: grid[11-y][x] = 'A'  # T_a internal

    for i, row in enumerate(grid):
        label = f"{hi:.3f}" if i == 0 else (f"{lo:.3f}" if i == 11 else "")
        print(f"  {label:>7}|{''.join(row)}|")
    print(f"         {'─'*42}")
    print(f"         parent(10ep)  |split|  children(10ep)")
    print(f"  X=T_ab(or T_parent)  A=T_a(child_a internal)")

    print(f"\n{'='*70}")
    print("완료")

if __name__ == '__main__':
    main()
