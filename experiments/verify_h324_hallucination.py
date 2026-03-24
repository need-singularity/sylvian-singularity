#!/usr/bin/env python3
"""가설 324 검증: LLM 환각 탐지 — toy transformer에서 head group tension

방법:
1. 작은 transformer (2-layer, 4-head)를 간단한 사실 데이터로 학습
2. Attention head를 A/G 그룹으로 분할
3. 사실(true) vs 거짓(false) 문장에서 head group tension 차이 측정
4. AUROC 계산
"""

import torch
import torch.nn as nn
import torch.nn.functional as F
import numpy as np
import math

np.random.seed(42)
torch.manual_seed(42)

print("=" * 70)
print("가설 324 검증: LLM 환각 탐지 — Toy Transformer Head Tension")
print("=" * 70)

# ─────────────────────────────────────────
# 1. Toy Transformer 구현
# ─────────────────────────────────────────

class ToyMultiHeadAttention(nn.Module):
    """4-head attention with per-head output extraction."""
    def __init__(self, d_model=64, n_heads=4):
        super().__init__()
        self.d_model = d_model
        self.n_heads = n_heads
        self.d_k = d_model // n_heads

        self.W_q = nn.Linear(d_model, d_model)
        self.W_k = nn.Linear(d_model, d_model)
        self.W_v = nn.Linear(d_model, d_model)
        self.W_o = nn.Linear(d_model, d_model)

    def forward(self, x, return_per_head=False):
        B, T, D = x.shape
        Q = self.W_q(x).view(B, T, self.n_heads, self.d_k).transpose(1, 2)
        K = self.W_k(x).view(B, T, self.n_heads, self.d_k).transpose(1, 2)
        V = self.W_v(x).view(B, T, self.n_heads, self.d_k).transpose(1, 2)

        scores = torch.matmul(Q, K.transpose(-2, -1)) / math.sqrt(self.d_k)
        attn = F.softmax(scores, dim=-1)
        context = torch.matmul(attn, V)  # (B, n_heads, T, d_k)

        if return_per_head:
            # Return per-head outputs before combining
            per_head = context  # (B, n_heads, T, d_k)
            combined = context.transpose(1, 2).contiguous().view(B, T, D)
            return self.W_o(combined), per_head

        combined = context.transpose(1, 2).contiguous().view(B, T, D)
        return self.W_o(combined), None


class ToyTransformer(nn.Module):
    """2-layer transformer for sequence classification."""
    def __init__(self, vocab_size=100, d_model=64, n_heads=4, n_classes=2):
        super().__init__()
        self.embedding = nn.Embedding(vocab_size, d_model)
        self.pos_enc = nn.Parameter(torch.randn(1, 32, d_model) * 0.02)
        self.attn1 = ToyMultiHeadAttention(d_model, n_heads)
        self.ff1 = nn.Sequential(nn.Linear(d_model, 128), nn.ReLU(), nn.Linear(128, d_model))
        self.attn2 = ToyMultiHeadAttention(d_model, n_heads)
        self.ff2 = nn.Sequential(nn.Linear(d_model, 128), nn.ReLU(), nn.Linear(128, d_model))
        self.classifier = nn.Linear(d_model, n_classes)
        self.n_heads = n_heads

    def forward(self, x, return_tension=False):
        B, T = x.shape
        h = self.embedding(x) + self.pos_enc[:, :T, :]

        h1, _ = self.attn1(h)
        h = h + h1
        h = h + self.ff1(h)

        h2, per_head = self.attn2(h, return_per_head=True)
        h = h + h2
        h = h + self.ff2(h)

        # Pool: mean over sequence
        pooled = h.mean(dim=1)  # (B, d_model)
        logits = self.classifier(pooled)

        if return_tension and per_head is not None:
            # Split heads into A group (0,1) and G group (2,3)
            head_A = per_head[:, :self.n_heads//2, :, :]  # (B, 2, T, d_k)
            head_G = per_head[:, self.n_heads//2:, :, :]  # (B, 2, T, d_k)

            # Mean over heads in each group, then over sequence
            mean_A = head_A.mean(dim=1).mean(dim=1)  # (B, d_k)
            mean_G = head_G.mean(dim=1).mean(dim=1)  # (B, d_k)

            # Tension = ||A - G||^2 / d_k
            tension = ((mean_A - mean_G) ** 2).mean(dim=-1)  # (B,)
            return logits, tension

        return logits, None


# ─────────────────────────────────────────
# 2. 사실/거짓 데이터셋 생성
# ─────────────────────────────────────────

print("\n" + "─" * 70)
print("1. Toy 사실/거짓 데이터셋 생성")
print("─" * 70)

vocab_size = 100
seq_len = 16
n_train = 2000
n_test = 500

# 패턴 기반 사실/거짓 생성
# "사실": 특정 토큰 패턴이 일관됨 (A→B, C→D 등)
# "거짓": 패턴이 위반됨 (A→D, C→B 등)

# 규칙: 토큰 i*10 뒤에 토큰 i*10+1 나오면 사실, i*10+5 나오면 거짓
def generate_data(n_samples):
    data = []
    labels = []
    for _ in range(n_samples):
        seq = np.random.randint(0, vocab_size, size=seq_len)
        is_true = np.random.random() > 0.5

        # 3~5개 위치에 규칙 삽입
        n_rules = np.random.randint(3, 6)
        positions = np.random.choice(seq_len - 1, size=min(n_rules, seq_len - 1), replace=False)

        for pos in positions:
            base = np.random.randint(0, 9) * 10  # 0, 10, 20, ..., 80
            seq[pos] = base
            if is_true:
                seq[pos + 1] = base + 1  # 규칙 준수
            else:
                seq[pos + 1] = base + 5  # 규칙 위반

        data.append(seq)
        labels.append(1 if is_true else 0)

    return torch.tensor(np.array(data), dtype=torch.long), torch.tensor(labels, dtype=torch.long)

train_x, train_y = generate_data(n_train)
test_x, test_y = generate_data(n_test)

print(f"  학습: {n_train} (사실: {(train_y==1).sum().item()}, 거짓: {(train_y==0).sum().item()})")
print(f"  테스트: {n_test} (사실: {(test_y==1).sum().item()}, 거짓: {(test_y==0).sum().item()})")

# ─────────────────────────────────────────
# 3. 모델 학습
# ─────────────────────────────────────────

print("\n" + "─" * 70)
print("2. Toy Transformer 학습")
print("─" * 70)

model = ToyTransformer(vocab_size=vocab_size, d_model=64, n_heads=4, n_classes=2)
optimizer = torch.optim.Adam(model.parameters(), lr=1e-3)
criterion = nn.CrossEntropyLoss()

batch_size = 64
n_epochs = 30

for epoch in range(n_epochs):
    model.train()
    total_loss = 0
    correct = 0
    total = 0

    indices = torch.randperm(n_train)
    for i in range(0, n_train, batch_size):
        idx = indices[i:i+batch_size]
        x_batch = train_x[idx]
        y_batch = train_y[idx]

        logits, _ = model(x_batch)
        loss = criterion(logits, y_batch)

        optimizer.zero_grad()
        loss.backward()
        optimizer.step()

        total_loss += loss.item() * len(idx)
        correct += (logits.argmax(dim=-1) == y_batch).sum().item()
        total += len(idx)

    if (epoch + 1) % 10 == 0:
        acc = correct / total * 100
        print(f"  Epoch {epoch+1:3d}: loss={total_loss/total:.4f}, acc={acc:.1f}%")

# Test accuracy
model.eval()
with torch.no_grad():
    logits, _ = model(test_x)
    test_acc = (logits.argmax(dim=-1) == test_y).float().mean().item() * 100
    print(f"\n  테스트 정확도: {test_acc:.1f}%")

# ─────────────────────────────────────────
# 4. Head Group Tension 측정
# ─────────────────────────────────────────

print("\n" + "─" * 70)
print("3. Head Group Tension 측정")
print("─" * 70)

model.eval()
with torch.no_grad():
    _, tensions = model(test_x, return_tension=True)

tensions_np = tensions.numpy()
labels_np = test_y.numpy()

true_tensions = tensions_np[labels_np == 1]
false_tensions = tensions_np[labels_np == 0]

print(f"\n  사실 문장 tension: mean={np.mean(true_tensions):.6f} +/- {np.std(true_tensions):.6f}")
print(f"  거짓 문장 tension: mean={np.mean(false_tensions):.6f} +/- {np.std(false_tensions):.6f}")
print(f"  비율 (사실/거짓):  {np.mean(true_tensions)/(np.mean(false_tensions)+1e-10):.3f}")

# Cohen's d
pooled_std = np.sqrt((np.var(true_tensions) + np.var(false_tensions)) / 2)
cohen_d = (np.mean(true_tensions) - np.mean(false_tensions)) / (pooled_std + 1e-10)
print(f"  Cohen's d:         {cohen_d:+.3f}")

# ─────────────────────────────────────────
# 5. AUROC 계산 (tension으로 사실/거짓 구분)
# ─────────────────────────────────────────

print("\n" + "─" * 70)
print("4. AUROC — tension으로 환각(거짓) 탐지")
print("─" * 70)

# Simple AUROC calculation
def compute_auroc(scores, labels):
    """AUROC: scores가 높을수록 positive(1)."""
    sorted_idx = np.argsort(-scores)
    sorted_labels = labels[sorted_idx]

    tp = 0
    fp = 0
    n_pos = np.sum(labels == 1)
    n_neg = np.sum(labels == 0)

    tpr_list = [0]
    fpr_list = [0]

    for label in sorted_labels:
        if label == 1:
            tp += 1
        else:
            fp += 1
        tpr_list.append(tp / max(n_pos, 1))
        fpr_list.append(fp / max(n_neg, 1))

    # Trapezoidal rule
    auroc = 0
    for i in range(1, len(fpr_list)):
        auroc += (fpr_list[i] - fpr_list[i-1]) * (tpr_list[i] + tpr_list[i-1]) / 2

    return auroc, tpr_list, fpr_list

# 가설: 높은 tension = 사실 (진짜 지식), 낮은 tension = 거짓 (환각)
auroc_high, tpr1, fpr1 = compute_auroc(tensions_np, labels_np)
# 반대 방향도 테스트
auroc_low, tpr2, fpr2 = compute_auroc(-tensions_np, labels_np)

best_auroc = max(auroc_high, auroc_low)
direction = "높은 tension = 사실" if auroc_high >= auroc_low else "낮은 tension = 사실"

print(f"\n  AUROC (높은 tension → 사실): {auroc_high:.4f}")
print(f"  AUROC (낮은 tension → 사실): {auroc_low:.4f}")
print(f"  최선 방향: {direction}")
print(f"  최선 AUROC: {best_auroc:.4f}")

# ─────────────────────────────────────────
# 6. 정답/오답별 tension 분석
# ─────────────────────────────────────────

print("\n" + "─" * 70)
print("5. 정답/오답별 tension (H313 재현)")
print("─" * 70)

with torch.no_grad():
    logits, tensions_all = model(test_x, return_tension=True)
    preds = logits.argmax(dim=-1).numpy()

correct_mask = preds == labels_np
wrong_mask = ~correct_mask

correct_tensions = tensions_np[correct_mask]
wrong_tensions = tensions_np[wrong_mask]

print(f"\n  정답 tension: mean={np.mean(correct_tensions):.6f} +/- {np.std(correct_tensions):.6f} (n={len(correct_tensions)})")
if len(wrong_tensions) > 0:
    print(f"  오답 tension: mean={np.mean(wrong_tensions):.6f} +/- {np.std(wrong_tensions):.6f} (n={len(wrong_tensions)})")
    ratio_cw = np.mean(correct_tensions) / (np.mean(wrong_tensions) + 1e-10)
    print(f"  비율 (정답/오답): {ratio_cw:.3f}")
else:
    print(f"  오답: 없음 (모두 정답)")
    ratio_cw = float('inf')

# ─────────────────────────────────────────
# 7. 거부 메커니즘 테스트 (H314)
# ─────────────────────────────────────────

print("\n" + "─" * 70)
print("6. 거부 메커니즘 (H314) — 낮은 tension 거부 시 정확도")
print("─" * 70)

reject_ratios = [0.05, 0.10, 0.20, 0.30, 0.50, 0.70, 0.90]

print(f"\n  {'거부율':>8} | {'남은수':>6} | {'정확도':>8} | {'향상':>8} | 바")
print(f"  {'─'*8}─┼─{'─'*6}─┼─{'─'*8}─┼─{'─'*8}─┼─{'─'*30}")

base_acc = np.mean(correct_mask) * 100

for ratio in reject_ratios:
    threshold = np.percentile(tensions_np, ratio * 100)
    keep_mask = tensions_np >= threshold
    if np.sum(keep_mask) == 0:
        continue
    kept_correct = np.sum(correct_mask[keep_mask])
    kept_total = np.sum(keep_mask)
    kept_acc = kept_correct / kept_total * 100
    improvement = kept_acc - base_acc

    bar_len = int(max(0, improvement) * 5)
    bar = "#" * min(bar_len, 30)
    print(f"  {ratio:>7.0%} | {kept_total:>6d} | {kept_acc:>7.1f}% | {improvement:>+7.2f}% | {bar}")

# ─────────────────────────────────────────
# 8. ASCII 그래프: tension 분포
# ─────────────────────────────────────────

print("\n" + "─" * 70)
print("7. Tension 분포 (사실 vs 거짓)")
print("─" * 70)

all_min = min(tensions_np.min(), 0)
all_max = tensions_np.max()
n_bins = 20
bin_edges = np.linspace(all_min, all_max, n_bins + 1)

true_hist, _ = np.histogram(true_tensions, bins=bin_edges)
false_hist, _ = np.histogram(false_tensions, bins=bin_edges)

max_count = max(true_hist.max(), false_hist.max())

print(f"\n  사실(T) vs 거짓(F) tension 분포:")
print(f"  {'bin':>12} | T  F")
for i in range(n_bins):
    lo, hi = bin_edges[i], bin_edges[i+1]
    t_bar = "#" * int(true_hist[i] / max(max_count, 1) * 25)
    f_bar = "." * int(false_hist[i] / max(max_count, 1) * 25)
    print(f"  {lo:>5.4f}-{hi:<5.4f} | {t_bar}")
    if f_bar:
        print(f"  {'':>12} | {f_bar}")

# ─────────────────────────────────────────
# 9. 결론
# ─────────────────────────────────────────

print("\n" + "=" * 70)
print("결론")
print("=" * 70)

print(f"\n  모델 정확도:     {test_acc:.1f}%")
print(f"  사실/거짓 tension 차이: Cohen's d = {cohen_d:+.3f}")
print(f"  환각 탐지 AUROC: {best_auroc:.4f}")
print(f"  방향:            {direction}")

if best_auroc > 0.80:
    verdict = "강한 지지 — head tension으로 환각 탐지 실용적"
elif best_auroc > 0.65:
    verdict = "약한 지지 — 신호 있으나 단독 탐지 부족"
elif best_auroc > 0.55:
    verdict = "매우 약한 신호 — 구조는 있으나 거의 랜덤 수준"
else:
    verdict = "지지 안 됨 — 랜덤 수준"

print(f"  판정: {verdict}")
print(f"\n  H313 재현 (정답 vs 오답):")
print(f"    정답 tension > 오답 tension? {'예' if ratio_cw > 1 else '아니오'} (ratio={ratio_cw:.3f})")
print(f"\n  H314 재현 (거부 → 정확도):")
print(f"    10% 거부 시 정확도 향상? 위 표 참조")

print(f"\n  ⚠️ 한계:")
print(f"    - Toy 모델 (64-dim, 4-head) → 실제 LLM과 규모 차이")
print(f"    - 패턴 기반 합성 데이터 → 실제 사실/환각과 다름")
print(f"    - Head 분할이 임의적 (head 0,1 vs 2,3)")
print(f"    - 실제 검증은 실제 LLM + TruthfulQA 필요")
print("=" * 70)
