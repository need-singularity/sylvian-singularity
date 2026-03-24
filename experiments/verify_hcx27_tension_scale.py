#!/usr/bin/env python3
"""H-CX-27 검증: tension_scale = ln(4) 수렴 — 다중 데이터셋 + 초기값 + 장기학습

기존 결과:
  - MNIST: 1.3887 (ln(4) 오차 0.2%)
  - Fashion: 1.4415 (4.0%)
  - CIFAR: 1.3393 (3.4%)
  - init=0.3에서만 ln(4) 수렴, 작은/큰 init에서는 다른 곳 수렴

추가 검증:
  1. MNIST에서 다양한 init (0.01~5.0), 50 epochs (장기 학습)
  2. Fashion/CIFAR에서도 장기 학습
  3. init에 무관한 수렴점 존재 확인
"""

import torch
import torch.nn as nn
import torch.nn.functional as F
import numpy as np
import math
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

np.random.seed(42)
torch.manual_seed(42)

LN4 = math.log(4)  # 1.38629...

print("=" * 70)
print(f"H-CX-27 검증: tension_scale → ln(4) = {LN4:.5f}")
print("=" * 70)

# ─────────────────────────────────────────
# PureFieldEngine (인라인)
# ─────────────────────────────────────────

class PureFieldEngine(nn.Module):
    def __init__(self, input_dim=784, hidden_dim=128, output_dim=10, init_ts=1.0):
        super().__init__()
        self.engine_a = nn.Sequential(
            nn.Linear(input_dim, hidden_dim), nn.ReLU(), nn.Dropout(0.3),
            nn.Linear(hidden_dim, output_dim),
        )
        self.engine_g = nn.Sequential(
            nn.Linear(input_dim, hidden_dim), nn.ReLU(), nn.Dropout(0.3),
            nn.Linear(hidden_dim, output_dim),
        )
        self.tension_scale = nn.Parameter(torch.tensor(float(init_ts)))

    def forward(self, x):
        out_a = self.engine_a(x)
        out_g = self.engine_g(x)
        repulsion = out_a - out_g
        tension = (repulsion ** 2).mean(dim=-1, keepdim=True)
        direction = F.normalize(repulsion, dim=-1)
        output = self.tension_scale * torch.sqrt(tension + 1e-8) * direction
        return output, tension.squeeze(-1)


# ─────────────────────────────────────────
# 데이터 로딩
# ─────────────────────────────────────────

from torchvision import datasets, transforms

def load_dataset(name):
    transform = transforms.Compose([transforms.ToTensor(), transforms.Lambda(lambda x: x.view(-1))])
    if name == "MNIST":
        train = datasets.MNIST(root='/tmp/data', train=True, download=True, transform=transform)
        test = datasets.MNIST(root='/tmp/data', train=False, download=True, transform=transform)
    elif name == "FashionMNIST":
        train = datasets.FashionMNIST(root='/tmp/data', train=True, download=True, transform=transform)
        test = datasets.FashionMNIST(root='/tmp/data', train=False, download=True, transform=transform)
    return train, test


def train_and_track(dataset_name, init_ts, n_epochs, seed=42):
    """Train and track tension_scale over epochs."""
    torch.manual_seed(seed)
    np.random.seed(seed)

    train_ds, test_ds = load_dataset(dataset_name)
    train_loader = torch.utils.data.DataLoader(train_ds, batch_size=256, shuffle=True)

    model = PureFieldEngine(784, 128, 10, init_ts=init_ts)
    optimizer = torch.optim.Adam(model.parameters(), lr=1e-3)

    ts_history = [init_ts]

    for epoch in range(n_epochs):
        model.train()
        for x_batch, y_batch in train_loader:
            output, tension = model(x_batch)
            loss = F.cross_entropy(output, y_batch)
            optimizer.zero_grad()
            loss.backward()
            optimizer.step()

        ts_history.append(model.tension_scale.item())

    final_ts = model.tension_scale.item()
    return final_ts, ts_history


# ─────────────────────────────────────────
# 실험 1: 다양한 init, 장기 학습 (MNIST, 50 epochs)
# ─────────────────────────────────────────

print("\n" + "─" * 70)
print("실험 1: MNIST — 다양한 init, 50 epochs")
print("─" * 70)

inits = [0.01, 0.05, 0.10, 0.30, 0.50, 1.00, 1.39, 2.00, 3.00, 5.00]
n_epochs_long = 50

results_mnist = []

print(f"\n  {'init':>6} | {'final_ts':>10} | {'ln(4)오차':>10} | {'수렴?':>6} | 히스토리")
print(f"  {'─'*6}─┼─{'─'*10}─┼─{'─'*10}─┼─{'─'*6}─┼─{'─'*30}")

for init_val in inits:
    final_ts, history = train_and_track("MNIST", init_val, n_epochs_long)
    error_pct = abs(final_ts - LN4) / LN4 * 100
    converged = error_pct < 5.0

    # Compact history (every 10 epochs)
    brief = [f"{history[i]:.2f}" for i in range(0, len(history), 10)]

    results_mnist.append({
        "init": init_val,
        "final": final_ts,
        "error": error_pct,
        "converged": converged,
        "history": history,
    })

    conv_mark = "YES" if converged else "no"
    print(f"  {init_val:>6.2f} | {final_ts:>10.4f} | {error_pct:>9.1f}% | {conv_mark:>6} | {' -> '.join(brief)}")

# ─────────────────────────────────────────
# 실험 2: Fashion-MNIST, 50 epochs
# ─────────────────────────────────────────

print("\n" + "─" * 70)
print("실험 2: FashionMNIST — 다양한 init, 50 epochs")
print("─" * 70)

inits_fashion = [0.10, 0.30, 0.50, 1.00, 1.39, 2.00]
results_fashion = []

print(f"\n  {'init':>6} | {'final_ts':>10} | {'ln(4)오차':>10} | {'수렴?':>6}")
print(f"  {'─'*6}─┼─{'─'*10}─┼─{'─'*10}─┼─{'─'*6}")

for init_val in inits_fashion:
    final_ts, history = train_and_track("FashionMNIST", init_val, n_epochs_long)
    error_pct = abs(final_ts - LN4) / LN4 * 100
    converged = error_pct < 5.0
    conv_mark = "YES" if converged else "no"

    results_fashion.append({
        "init": init_val,
        "final": final_ts,
        "error": error_pct,
        "converged": converged,
    })
    print(f"  {init_val:>6.2f} | {final_ts:>10.4f} | {error_pct:>9.1f}% | {conv_mark:>6}")

# ─────────────────────────────────────────
# 실험 3: 수렴 경로 분석 (MNIST, 다중 시드)
# ─────────────────────────────────────────

print("\n" + "─" * 70)
print("실험 3: MNIST init=1.0, 5개 시드 (50 epochs)")
print("─" * 70)

seeds = [42, 123, 456, 789, 1024]
multi_seed_finals = []

for seed in seeds:
    final_ts, history = train_and_track("MNIST", 1.0, n_epochs_long, seed=seed)
    multi_seed_finals.append(final_ts)
    error_pct = abs(final_ts - LN4) / LN4 * 100
    print(f"  seed={seed}: final={final_ts:.4f}, ln(4) error={error_pct:.1f}%")

mean_final = np.mean(multi_seed_finals)
std_final = np.std(multi_seed_finals)
mean_error = abs(mean_final - LN4) / LN4 * 100
print(f"\n  평균: {mean_final:.4f} +/- {std_final:.4f}")
print(f"  ln(4) 오차: {mean_error:.1f}%")

# ─────────────────────────────────────────
# ASCII 그래프: tension_scale 수렴 경로
# ─────────────────────────────────────────

print("\n" + "─" * 70)
print("4. ASCII 수렴 경로 (MNIST, 50ep)")
print("─" * 70)

# 3개 대표 init의 수렴 경로
representative = [r for r in results_mnist if r["init"] in [0.01, 0.30, 1.39, 5.00]]

print(f"\n  tension_scale vs epoch:")
print(f"  ln(4) = {LN4:.4f} (점선 위치)")

height = 18
width = 50
y_min = 0.0
y_max = max(max(r["history"]) for r in representative) * 1.1

grid = [['.' for _ in range(width)] for _ in range(height)]

# ln(4) 기준선
ln4_y = int((1 - (LN4 - y_min) / (y_max - y_min)) * (height - 1))
ln4_y = max(0, min(height - 1, ln4_y))
for x in range(width):
    grid[ln4_y][x] = '-'

symbols = ['o', 'x', '+', '*']
for idx, r in enumerate(representative):
    hist = r["history"]
    sym = symbols[idx % len(symbols)]
    for ep in range(0, len(hist), max(1, len(hist) // width)):
        x = int(ep / len(hist) * (width - 1))
        y = int((1 - (hist[ep] - y_min) / (y_max - y_min + 1e-10)) * (height - 1))
        x = max(0, min(width - 1, x))
        y = max(0, min(height - 1, y))
        grid[y][x] = sym

print(f"    {y_max:.1f} ^")
for row in grid:
    print(f"         |{''.join(row)}")
print(f"    {y_min:.1f} +{'─' * width}> epoch")
print(f"         0         10        20        30        40        50")

# 범례
for idx, r in enumerate(representative):
    sym = symbols[idx % len(symbols)]
    print(f"    {sym} = init={r['init']}")
print(f"    - = ln(4) = {LN4:.4f}")

# ─────────────────────────────────────────
# 5. 수렴 basin 분석
# ─────────────────────────────────────────

print("\n" + "─" * 70)
print("5. 수렴 basin 분석")
print("─" * 70)

# 모든 MNIST 결과의 final_ts 분포
all_finals = [r["final"] for r in results_mnist]

print(f"\n  MNIST 전체 final tension_scale 분포:")
print(f"    min  = {min(all_finals):.4f}")
print(f"    max  = {max(all_finals):.4f}")
print(f"    mean = {np.mean(all_finals):.4f}")
print(f"    std  = {np.std(all_finals):.4f}")
print(f"    ln(4) = {LN4:.4f}")

# 수렴 여부 판정
converged_count = sum(1 for r in results_mnist if r["converged"])
print(f"\n  ln(4) 수렴 (오차 <5%): {converged_count}/{len(results_mnist)}")

# init 범위별 수렴
print(f"\n  init 범위별 수렴:")
ranges = [(0, 0.1), (0.1, 0.5), (0.5, 1.5), (1.5, 3.0), (3.0, 10.0)]
for lo, hi in ranges:
    subset = [r for r in results_mnist if lo <= r["init"] < hi]
    if subset:
        conv = sum(1 for r in subset if r["converged"])
        avg = np.mean([r["final"] for r in subset])
        print(f"    init [{lo:.1f}, {hi:.1f}): {conv}/{len(subset)} 수렴, 평균 final={avg:.4f}")

# ─────────────────────────────────────────
# 6. 결론
# ─────────────────────────────────────────

print("\n" + "=" * 70)
print("결론")
print("=" * 70)

# 종합
mnist_conv = sum(1 for r in results_mnist if r["converged"])
fashion_conv = sum(1 for r in results_fashion if r["converged"])

print(f"\n  MNIST ln(4) 수렴:   {mnist_conv}/{len(results_mnist)} (50ep)")
print(f"  Fashion ln(4) 수렴: {fashion_conv}/{len(results_fashion)} (50ep)")
print(f"  다중 시드 평균:     {mean_final:.4f} +/- {std_final:.4f} (init=1.0)")
print(f"  ln(4) = {LN4:.4f}")

# 초기값 의존성 판정
all_close = all(r["converged"] for r in results_mnist)
some_close = any(r["converged"] for r in results_mnist)

if all_close:
    init_verdict = "초기값 무관 수렴 — 보편적 끌개(universal attractor)"
elif some_close:
    converged_inits = [r["init"] for r in results_mnist if r["converged"]]
    init_verdict = f"초기값 편향 — init={converged_inits} 근방에서만 수렴"
else:
    init_verdict = "ln(4) 수렴 기각 — 어떤 init에서도 수렴 안 함 (50ep)"

print(f"\n  초기값 판정: {init_verdict}")

# 전체 판정
if all_close and fashion_conv == len(results_fashion):
    verdict = "강한 지지 — ln(4)가 보편적 끌개"
elif some_close:
    verdict = "약화된 지지 — 특정 init에서만 수렴, 보편성 부족"
else:
    verdict = "기각 — ln(4) 수렴은 우연"

print(f"  전체 판정: {verdict}")

print(f"\n  ⚠️ 한계:")
print(f"    - 50 epochs도 충분하지 않을 수 있음 (100ep+ 필요?)")
print(f"    - optimizer (Adam) 의존성 미확인")
print(f"    - 학습률 의존성 미확인")
print(f"    - loss landscape에 multiple minima 가능성")
print("=" * 70)
