#!/usr/bin/env python3
"""Self-Referential Anomaly Detection

Concept: Feed the model's own tension back as additional input features.
- Round 1: model sees x (padded to 32) -> produces tension T1
- Round 2: model sees [x, T1_normalized] (padded to 32) -> produces tension T2
- Round 3: model sees [x, T1_norm, T2_norm] -> produces tension T3

Does self-referential iteration improve AUROC?

Dataset: Breast Cancer (sklearn), 30 features
Model: Dual-engine autoencoder with inter-engine tension
  - Always takes 32-dim input (30 features + 2 tension slots, zero-padded initially)
  - Train parent on normal data only (MSE reconstruction, 50 epochs)
  - Mitosis N=2, train children independently 30 epochs
  - Anomaly score = reconstruction_error + inter_tension (combined signal)
  - Tension is z-score normalized before feeding back (so it's on same scale as inputs)

5 trials, AUROC per round, ASCII graph.
"""

import sys
import os
import copy
import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F
from sklearn.datasets import load_breast_cancer
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import roc_auc_score


# ── Model ──────────────────────────────────────────────

class DualEngineAutoencoder(nn.Module):
    """Two-engine autoencoder. Tension = disagreement + recon error."""

    def __init__(self, input_dim=32, hidden_dim=64, latent_dim=16, output_dim=32):
        super().__init__()
        # Engine A
        self.enc_a = nn.Sequential(
            nn.Linear(input_dim, hidden_dim), nn.ReLU(),
            nn.Linear(hidden_dim, latent_dim), nn.ReLU(),
        )
        self.dec_a = nn.Sequential(
            nn.Linear(latent_dim, hidden_dim), nn.ReLU(),
            nn.Linear(hidden_dim, output_dim),
        )
        # Engine G
        self.enc_g = nn.Sequential(
            nn.Linear(input_dim, hidden_dim), nn.ReLU(),
            nn.Linear(hidden_dim, latent_dim), nn.ReLU(),
        )
        self.dec_g = nn.Sequential(
            nn.Linear(latent_dim, hidden_dim), nn.ReLU(),
            nn.Linear(hidden_dim, output_dim),
        )

    def forward(self, x):
        out_a = self.dec_a(self.enc_a(x))
        out_g = self.dec_g(self.enc_g(x))
        recon = (out_a + out_g) / 2.0
        # Per-sample reconstruction error (on first 30 features only)
        recon_err = ((recon[:, :30] - x[:, :30]) ** 2).mean(dim=-1)
        # Inter-engine disagreement
        disagree = ((out_a - out_g) ** 2).mean(dim=-1)
        # Combined tension
        tension = recon_err + disagree
        return recon, tension, recon_err, disagree


def mitosis(parent, noise_scale=0.02):
    """Split parent into two children with perturbations."""
    child_a = copy.deepcopy(parent)
    child_b = copy.deepcopy(parent)
    with torch.no_grad():
        for p in child_a.parameters():
            p.add_(torch.randn_like(p) * noise_scale)
        for p in child_b.parameters():
            p.add_(torch.randn_like(p) * noise_scale)
    return child_a, child_b


def compute_scores(model_a, model_b, x):
    """Compute anomaly scores from two models.
    Returns combined tension per sample."""
    with torch.no_grad():
        recon_a, tension_a, recon_err_a, _ = model_a(x)
        recon_b, tension_b, recon_err_b, _ = model_b(x)
    # Inter-model disagreement (on reconstructions)
    inter_disagree = ((recon_a - recon_b) ** 2).mean(dim=-1)
    # Average reconstruction error
    avg_recon = (recon_err_a + recon_err_b) / 2.0
    # Combined score
    score = avg_recon + inter_disagree
    return score


# ── Training ───────────────────────────────────────────

def train_model(model, X_train, epochs, lr=1e-3):
    """Train autoencoder with MSE reconstruction loss."""
    opt = torch.optim.Adam(model.parameters(), lr=lr)
    for ep in range(epochs):
        model.train()
        opt.zero_grad()
        recon, tension, recon_err, disagree = model(X_train)
        loss = F.mse_loss(recon[:, :30], X_train[:, :30])
        loss.backward()
        opt.step()
    return model


# ── Self-Referential Forward ───────────────────────────

def selfref_forward(model_a, model_b, X_base, n_rounds=3):
    """
    Self-referential anomaly scoring.

    X_base: (N, 30) raw features
    Returns: list of score arrays [S1, S2, S3] each shape (N,)

    Round 1: input = [X_base, 0, 0] -> score S1
    Round 2: input = [X_base, normalize(S1), 0] -> score S2
    Round 3: input = [X_base, normalize(S1), normalize(S2)] -> score S3

    Key: normalize scores to z-scores before feeding back,
    so they're on the same scale as the standardized features.
    """
    N = X_base.shape[0]
    scores = []

    x_aug = torch.zeros(N, 32)
    x_aug[:, :30] = X_base

    for r in range(n_rounds):
        s = compute_scores(model_a, model_b, x_aug)
        scores.append(s.numpy())

        # Z-score normalize and feed back
        s_np = s.numpy()
        s_mean = s_np.mean()
        s_std = s_np.std() + 1e-8
        s_normalized = (s_np - s_mean) / s_std  # Now mean=0, std=1 like features

        if r == 0:
            x_aug[:, 30] = torch.FloatTensor(s_normalized)
        elif r == 1:
            x_aug[:, 31] = torch.FloatTensor(s_normalized)

    return scores


# ── Main Experiment ────────────────────────────────────

def run_experiment():
    print("=" * 70)
    print("  SELF-REFERENTIAL ANOMALY DETECTION")
    print("  Feed normalized tension back as input -> does AUROC improve?")
    print("=" * 70)

    # Load data
    data = load_breast_cancer()
    X_raw, y = data.data, data.target  # 1=benign(normal), 0=malignant(anomaly)

    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X_raw)

    X_normal = X_scaled[y == 1]
    X_anomaly = X_scaled[y == 0]

    print(f"\nDataset: Breast Cancer (30 features)")
    print(f"  Normal (benign):   {len(X_normal)}")
    print(f"  Anomaly (malign):  {len(X_anomaly)}")
    print(f"\nMethod:")
    print(f"  - Dual-engine autoencoder (32-dim input: 30 feat + 2 tension slots)")
    print(f"  - Train parent 50 epochs on normal only")
    print(f"  - Mitosis -> 2 children, train 30 epochs each")
    print(f"  - Score = recon_error + inter_model_disagreement")
    print(f"  - Self-ref: feed z-normalized score back into tension slots")

    N_TRIALS = 5
    all_aurocs = {1: [], 2: [], 3: []}
    all_tensions_detail = []

    for trial in range(N_TRIALS):
        seed = trial * 7 + 42
        torch.manual_seed(seed)
        np.random.seed(seed)

        # Split normal into train/test
        idx = np.random.permutation(len(X_normal))
        n_train = int(0.7 * len(X_normal))
        X_train_np = X_normal[idx[:n_train]]
        X_test_normal_np = X_normal[idx[n_train:]]

        # Test set: normal + anomaly
        X_test_np = np.vstack([X_test_normal_np, X_anomaly])
        y_test = np.array([0] * len(X_test_normal_np) + [1] * len(X_anomaly))

        # Pad to 32 dims
        X_train_32 = np.zeros((len(X_train_np), 32))
        X_train_32[:, :30] = X_train_np
        X_train_t = torch.FloatTensor(X_train_32)

        X_test_base = torch.FloatTensor(X_test_np)  # 30-dim for selfref

        # ── Phase 1: Train parent (50 epochs) ──
        parent = DualEngineAutoencoder(input_dim=32, hidden_dim=64, latent_dim=16, output_dim=32)
        train_model(parent, X_train_t, epochs=50)

        # ── Phase 2: Mitosis + independent training (30 epochs) ──
        child_a, child_b = mitosis(parent, noise_scale=0.02)
        train_model(child_a, X_train_t, epochs=30)
        train_model(child_b, X_train_t, epochs=30)

        # ── Phase 3: Self-referential forward ──
        child_a.eval()
        child_b.eval()
        scores = selfref_forward(child_a, child_b, X_test_base, n_rounds=3)

        # Compute AUROC for each round
        aurocs = []
        n_normal_test = len(X_test_normal_np)
        for r in range(3):
            auc = roc_auc_score(y_test, scores[r])
            aurocs.append(auc)
            all_aurocs[r + 1].append(auc)

        # Store detail for last trial
        if trial == N_TRIALS - 1:
            all_tensions_detail = (scores, n_normal_test)

        print(f"\n  Trial {trial+1}: T1={aurocs[0]:.4f}  T2={aurocs[1]:.4f}  T3={aurocs[2]:.4f}"
              f"  delta(T3-T1)={aurocs[2]-aurocs[0]:+.4f}")

    # ── Results ────────────────────────────────────────

    print("\n" + "=" * 70)
    print("  RESULTS: AUROC per Self-Referential Round")
    print("=" * 70)

    means = {}
    stds = {}
    for r in [1, 2, 3]:
        means[r] = np.mean(all_aurocs[r])
        stds[r] = np.std(all_aurocs[r])

    # Table
    print(f"\n{'Round':<8} {'Mean AUROC':<14} {'Std':<10} {'Individual Trials'}")
    print("-" * 70)
    for r in [1, 2, 3]:
        trials_str = "  ".join(f"{v:.4f}" for v in all_aurocs[r])
        print(f"  T{r:<5} {means[r]:<14.4f} {stds[r]:<10.4f} {trials_str}")

    delta_21 = means[2] - means[1]
    delta_31 = means[3] - means[1]
    delta_32 = means[3] - means[2]

    print(f"\n  Delta T2-T1: {delta_21:+.4f}")
    print(f"  Delta T3-T1: {delta_31:+.4f}")
    print(f"  Delta T3-T2: {delta_32:+.4f}")

    # ── ASCII Graph ────────────────────────────────────

    print("\n" + "=" * 70)
    print("  ASCII: AUROC by Round (mean +/- std)")
    print("=" * 70)

    # Determine bar range
    all_vals = [means[r] for r in [1, 2, 3]]
    all_errs = [stds[r] for r in [1, 2, 3]]
    lo = max(0, min(all_vals) - max(all_errs) - 0.05)
    hi = max(all_vals) + max(all_errs) + 0.05
    span = hi - lo

    BAR_WIDTH = 50
    for r in [1, 2, 3]:
        bar_len = int((means[r] - lo) / span * BAR_WIDTH) if span > 0 else 25
        bar_len = max(1, min(BAR_WIDTH, bar_len))
        err_lo = int((means[r] - stds[r] - lo) / span * BAR_WIDTH)
        err_hi = int((means[r] + stds[r] - lo) / span * BAR_WIDTH)
        err_lo = max(0, err_lo)
        err_hi = min(BAR_WIDTH, err_hi)

        line = [' '] * BAR_WIDTH
        for i in range(bar_len):
            line[i] = '█'
        for i in range(bar_len, err_hi):
            line[i] = '░'

        bar = ''.join(line)
        print(f"  T{r} |{bar}| {means[r]:.4f} +/- {stds[r]:.4f}")

    print(f"     +{'─' * BAR_WIDTH}+")
    print(f"     {lo:.2f}{' ' * (BAR_WIDTH - 8)}{hi:.2f}")

    # ── Per-Trial Trajectory ───────────────────────────

    print("\n" + "=" * 70)
    print("  TRAJECTORY: Per-Trial AUROC across rounds")
    print("=" * 70)

    for trial in range(N_TRIALS):
        vals = [all_aurocs[r][trial] for r in [1, 2, 3]]
        arrows = []
        for i in range(1, 3):
            d = vals[i] - vals[i - 1]
            if d > 0.005:
                arrows.append("^")
            elif d < -0.005:
                arrows.append("v")
            else:
                arrows.append("=")
        print(f"  Trial {trial + 1}: {vals[0]:.4f} {arrows[0]} {vals[1]:.4f} {arrows[1]} {vals[2]:.4f}"
              f"  net={vals[2] - vals[0]:+.4f}")

    # ── Tension Distribution Analysis ──────────────────

    print("\n" + "=" * 70)
    print("  TENSION STATISTICS (last trial)")
    print("=" * 70)

    scores_detail, n_normal_test = all_tensions_detail
    print(f"\n  {'Round':<8} {'Normal mean':<16} {'Anomaly mean':<16} {'Separation':<12} {'Ratio'}")
    print("  " + "-" * 65)
    for r in range(3):
        t = scores_detail[r]
        t_norm = t[:n_normal_test]
        t_anom = t[n_normal_test:]
        sep = (np.mean(t_anom) - np.mean(t_norm)) / (np.std(t_norm) + 1e-8)
        ratio = np.mean(t_anom) / (np.mean(t_norm) + 1e-8)
        print(f"  T{r + 1:<5} {np.mean(t_norm):<16.6f} {np.mean(t_anom):<16.6f} "
              f"{sep:<12.2f}sigma  {ratio:.2f}x")

    # ── Histogram (ASCII) ──────────────────────────────

    print("\n" + "=" * 70)
    print("  HISTOGRAM: Score distributions (T1 vs T3, last trial)")
    print("=" * 70)

    for rnd, label in [(0, "T1"), (2, "T3")]:
        t = scores_detail[rnd]
        t_norm = t[:n_normal_test]
        t_anom = t[n_normal_test:]

        # 10-bin histogram
        all_t = np.concatenate([t_norm, t_anom])
        bins = np.linspace(np.percentile(all_t, 1), np.percentile(all_t, 99), 11)
        h_norm, _ = np.histogram(t_norm, bins=bins)
        h_anom, _ = np.histogram(t_anom, bins=bins)

        max_h = max(max(h_norm), max(h_anom), 1)
        scale = 30.0 / max_h

        print(f"\n  {label} - Normal (N) vs Anomaly (A):")
        for i in range(len(bins) - 1):
            bn = int(h_norm[i] * scale)
            ba = int(h_anom[i] * scale)
            bar_n = 'N' * bn
            bar_a = 'A' * ba
            print(f"  {bins[i]:8.4f} |{bar_n}{bar_a}")
        print(f"  {bins[-1]:8.4f} |")

    # ── Verdict ────────────────────────────────────────

    print("\n" + "=" * 70)
    if delta_31 > 0.005:
        print("  VERDICT: Self-referential iteration IMPROVES anomaly detection")
        print(f"           T3 > T1 by {delta_31:+.4f} AUROC (mean over {N_TRIALS} trials)")
    elif delta_31 < -0.005:
        print("  VERDICT: Self-referential iteration DEGRADES anomaly detection")
        print(f"           T3 < T1 by {delta_31:+.4f} AUROC (mean over {N_TRIALS} trials)")
    else:
        print("  VERDICT: Self-referential iteration has NEGLIGIBLE effect")
        print(f"           T3 - T1 = {delta_31:+.4f} AUROC (mean over {N_TRIALS} trials)")

    improved = sum(1 for t in range(N_TRIALS) if all_aurocs[3][t] > all_aurocs[1][t] + 0.001)
    degraded = sum(1 for t in range(N_TRIALS) if all_aurocs[3][t] < all_aurocs[1][t] - 0.001)
    print(f"  Improved: {improved}/{N_TRIALS}  Degraded: {degraded}/{N_TRIALS}")

    # Best single round
    best_round = max([1, 2, 3], key=lambda r: means[r])
    print(f"  Best round: T{best_round} (AUROC={means[best_round]:.4f})")
    print("=" * 70)


if __name__ == "__main__":
    run_experiment()
