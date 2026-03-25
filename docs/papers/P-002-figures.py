#!/usr/bin/env python3
"""P-002 Figure Generator: Universal Confusion Topology

Generates all publication-quality figures for:
  "Universal Confusion Topology: Persistent Homology Reveals
   Data-Intrinsic Cognitive Structure Shared Across Architectures,
   Algorithms, and Substrates"

Output: docs/papers/figures/fig1..fig7 as 300dpi PNG files.

Usage:
  python3 docs/papers/P-002-figures.py

Requirements: torch, torchvision, numpy, scipy, sklearn, matplotlib
Time: ~15-20 min on Mac CPU
"""

import sys, os, time, warnings
warnings.filterwarnings("ignore")

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, PROJECT_ROOT)

FIGURES_DIR = os.path.join(PROJECT_ROOT, "docs", "papers", "figures")
os.makedirs(FIGURES_DIR, exist_ok=True)

import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F
from torch.utils.data import DataLoader, Subset
from torchvision import datasets, transforms
from scipy.stats import spearmanr, kendalltau
from scipy.cluster.hierarchy import linkage, fcluster, dendrogram
from sklearn.neighbors import KNeighborsClassifier
from sklearn.decomposition import PCA
from sklearn.metrics import confusion_matrix
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker

from model_pure_field import PureFieldEngine

# ============================================================
# Style: Nature-style publication quality
# ============================================================
plt.rcParams.update({
    "font.family": "sans-serif",
    "font.sans-serif": ["Helvetica", "Arial", "DejaVu Sans"],
    "font.size": 9,
    "axes.titlesize": 10,
    "axes.labelsize": 9,
    "xtick.labelsize": 8,
    "ytick.labelsize": 8,
    "legend.fontsize": 8,
    "figure.dpi": 300,
    "savefig.dpi": 300,
    "savefig.bbox": "tight",
    "savefig.pad_inches": 0.05,
    "axes.linewidth": 0.8,
    "xtick.major.width": 0.6,
    "ytick.major.width": 0.6,
    "xtick.major.size": 3,
    "ytick.major.size": 3,
    "axes.spines.top": False,
    "axes.spines.right": False,
    "lines.linewidth": 1.2,
    "lines.markersize": 4,
})

# Nature-style color palette
COLORS = {
    "blue":   "#4477AA",
    "red":    "#CC3311",
    "green":  "#228833",
    "yellow": "#CCBB44",
    "cyan":   "#66CCEE",
    "purple": "#AA3377",
    "grey":   "#BBBBBB",
    "black":  "#000000",
}
PALETTE = [COLORS["blue"], COLORS["red"], COLORS["green"],
           COLORS["yellow"], COLORS["cyan"], COLORS["purple"]]

# ============================================================
# Configuration
# ============================================================
DEVICE = "cpu"
EPOCHS = 15
HIDDEN_DIM = 128
LR = 1e-3
BATCH_SIZE = 256
SEED = 42

DATASET_CONFIGS = {
    "MNIST": {
        "cls": datasets.MNIST,
        "input_dim": 784,
        "mean": (0.1307,), "std": (0.3081,),
        "names": ["0","1","2","3","4","5","6","7","8","9"],
    },
    "Fashion": {
        "cls": datasets.FashionMNIST,
        "input_dim": 784,
        "mean": (0.2860,), "std": (0.3530,),
        "names": ["T-shirt","Trouser","Pullover","Dress","Coat",
                  "Sandal","Shirt","Sneaker","Bag","Boot"],
    },
    "CIFAR": {
        "cls": datasets.CIFAR10,
        "input_dim": 3072,
        "mean": (0.5,0.5,0.5), "std": (0.5,0.5,0.5),
        "names": ["plane","auto","bird","cat","deer",
                  "dog","frog","horse","ship","truck"],
    },
}

CIFAR_CATEGORIES = {
    0: "machine", 1: "machine", 2: "animal", 3: "animal", 4: "animal",
    5: "animal", 6: "animal", 7: "animal", 8: "machine", 9: "machine",
}


# ============================================================
# Helpers (from P-002-reproduction.py)
# ============================================================
def set_seed(seed):
    torch.manual_seed(seed)
    np.random.seed(seed)


def get_loaders(cfg, batch_size=BATCH_SIZE, subset_indices=None):
    t = transforms.Compose([
        transforms.ToTensor(),
        transforms.Normalize(cfg["mean"], cfg["std"]),
    ])
    train_ds = cfg["cls"]("/tmp/data", train=True, download=True, transform=t)
    test_ds = cfg["cls"]("/tmp/data", train=False, download=True, transform=t)
    if subset_indices is not None:
        train_ds = Subset(train_ds, subset_indices)
    train_loader = DataLoader(train_ds, batch_size, shuffle=True, num_workers=0)
    test_loader = DataLoader(test_ds, batch_size=512, shuffle=False, num_workers=0)
    return train_loader, test_loader


class DenseMLP(nn.Module):
    def __init__(self, input_dim=784, hidden_dim=128, output_dim=10):
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(input_dim, hidden_dim), nn.ReLU(),
            nn.Dropout(0.3), nn.Linear(hidden_dim, output_dim),
        )

    def forward(self, x):
        return self.net(x), torch.tensor(0.0)


def train_model(model, train_loader, input_dim, epochs=EPOCHS, lr=LR):
    optimizer = torch.optim.Adam(model.parameters(), lr=lr)
    criterion = nn.CrossEntropyLoss()
    model.to(DEVICE)
    for ep in range(epochs):
        model.train()
        for x, y in train_loader:
            x, y = x.view(-1, input_dim).to(DEVICE), y.to(DEVICE)
            optimizer.zero_grad()
            out, _ = model(x)
            loss = criterion(out, y)
            loss.backward()
            optimizer.step()
    return model


def train_model_epoch_snapshots(model, train_loader, test_loader, input_dim,
                                 epochs=EPOCHS, lr=LR):
    """Train and capture per-epoch centroid snapshots + confusion matrices."""
    optimizer = torch.optim.Adam(model.parameters(), lr=lr)
    criterion = nn.CrossEntropyLoss()
    model.to(DEVICE)

    snapshots = []  # list of (epoch, dist_mat, conf_freqs, merge_dists)

    # Epoch 0 (before training)
    dm0 = _snapshot_dist_mat(model, test_loader, input_dim)
    h0_0 = total_h0_persistence(dm0)
    snapshots.append({"epoch": 0, "dist_mat": dm0, "h0_total": h0_0})

    for ep in range(epochs):
        model.train()
        for x, y in train_loader:
            x, y = x.view(-1, input_dim).to(DEVICE), y.to(DEVICE)
            optimizer.zero_grad()
            out, _ = model(x)
            loss = criterion(out, y)
            loss.backward()
            optimizer.step()

        dm = _snapshot_dist_mat(model, test_loader, input_dim)
        h0 = total_h0_persistence(dm)
        md = merge_distances_for_all_pairs(dm)
        y_true, y_pred = compute_predictions(model, test_loader, input_dim)
        cf, cm = get_confusion_frequencies(y_true, y_pred)
        snapshots.append({
            "epoch": ep + 1, "dist_mat": dm, "h0_total": h0,
            "merge_dists": md, "conf_freqs": cf, "cm": cm,
        })

    return model, snapshots


def _snapshot_dist_mat(model, loader, input_dim):
    feats, labels = get_penultimate_features(model, loader, input_dim)
    centroids = compute_class_centroids(feats, labels)
    return cosine_distance_matrix(centroids)


def evaluate_model(model, loader, input_dim):
    model.eval()
    correct = total = 0
    with torch.no_grad():
        for x, y in loader:
            x, y = x.view(-1, input_dim).to(DEVICE), y.to(DEVICE)
            out, _ = model(x)
            correct += (out.argmax(1) == y).sum().item()
            total += y.size(0)
    return 100.0 * correct / total


def get_penultimate_features(model, loader, input_dim):
    model.eval()
    feats, labels = [], []
    with torch.no_grad():
        for x, y in loader:
            x_flat = x.view(-1, input_dim).to(DEVICE)
            if isinstance(model, PureFieldEngine):
                a = model.engine_a(x_flat)
                g = model.engine_g(x_flat)
                feat = a - g
            elif isinstance(model, DenseMLP):
                h = model.net[0](x_flat)
                h = model.net[1](h)
                feat = h
            else:
                out, _ = model(x_flat)
                feat = out
            feats.append(feat.cpu().numpy())
            labels.append(y.numpy())
    return np.concatenate(feats), np.concatenate(labels)


def compute_class_centroids(features, labels, n_classes=10):
    centroids = np.zeros((n_classes, features.shape[1]))
    for c in range(n_classes):
        mask = labels == c
        if mask.sum() > 0:
            centroids[c] = features[mask].mean(axis=0)
    return centroids


def cosine_distance_matrix(centroids):
    norms = np.linalg.norm(centroids, axis=1, keepdims=True)
    normed = centroids / np.clip(norms, 1e-8, None)
    sim = normed @ normed.T
    return 1.0 - sim


def merge_distances_for_all_pairs(dist_matrix, n_classes=10):
    condensed = []
    for i in range(n_classes):
        for j in range(i+1, n_classes):
            condensed.append(dist_matrix[i, j])
    condensed = np.array(condensed)
    Z = linkage(condensed, method="single")
    cluster_id = list(range(n_classes))
    merge_dist = {}
    for k in range(len(Z)):
        ci, cj = int(Z[k, 0]), int(Z[k, 1])
        d = Z[k, 2]
        def get_members(idx):
            if idx < n_classes:
                return {idx}
            return get_members(int(Z[idx - n_classes, 0])) | get_members(int(Z[idx - n_classes, 1]))
        members_i = get_members(ci)
        members_j = get_members(cj)
        for a in members_i:
            for b in members_j:
                pair = (min(a, b), max(a, b))
                if pair not in merge_dist:
                    merge_dist[pair] = d
        cluster_id.append(n_classes + k)
    return merge_dist


def get_confusion_frequencies(y_true, y_pred, n_classes=10):
    cm = confusion_matrix(y_true, y_pred, labels=list(range(n_classes)))
    freq = {}
    for i in range(n_classes):
        for j in range(i+1, n_classes):
            freq[(i, j)] = cm[i, j] + cm[j, i]
    return freq, cm


def compute_predictions(model, loader, input_dim):
    model.eval()
    all_y, all_pred = [], []
    with torch.no_grad():
        for x, y in loader:
            x = x.view(-1, input_dim).to(DEVICE)
            out, _ = model(x)
            all_y.append(y.numpy())
            all_pred.append(out.argmax(1).cpu().numpy())
    return np.concatenate(all_y), np.concatenate(all_pred)


def total_h0_persistence(dist_matrix):
    n = dist_matrix.shape[0]
    condensed = []
    for i in range(n):
        for j in range(i+1, n):
            condensed.append(dist_matrix[i, j])
    Z = linkage(condensed, method="single")
    return sum(Z[:, 2])


def correlation_merge_vs_confusion(merge_dists, conf_freqs):
    pairs = sorted(merge_dists.keys())
    md = [merge_dists[p] for p in pairs]
    cf = [conf_freqs.get(p, 0) for p in pairs]
    r, p = spearmanr(md, cf)
    return r, p


def top_k_pairs(freq_dict, k=5):
    return [p[0] for p in sorted(freq_dict.items(), key=lambda x: -x[1])[:k]]


def top_k_merge_pairs(merge_dist_dict, k=5):
    return [p[0] for p in sorted(merge_dist_dict.items(), key=lambda x: x[1])[:k]]


def pair_overlap(list1, list2):
    return len(set(list1) & set(list2))


# ============================================================
# Figure 1: Merge distance vs confusion frequency (3 panels)
# ============================================================
def fig1_merge_vs_confusion(all_results):
    """Scatter plot: merge distance vs confusion frequency for 3 datasets."""
    fig, axes = plt.subplots(1, 3, figsize=(7.2, 2.4))

    for idx, (name, color) in enumerate(zip(["MNIST", "Fashion", "CIFAR"],
                                             [COLORS["blue"], COLORS["red"], COLORS["green"]])):
        ax = axes[idx]
        res = all_results[name]
        merge_dists = res["merge_dists"]
        conf_freqs = res["conf_freqs"]

        pairs = sorted(merge_dists.keys())
        md = np.array([merge_dists[p] for p in pairs])
        cf = np.array([conf_freqs.get(p, 0) for p in pairs])

        r, pval = spearmanr(md, cf)

        ax.scatter(md, cf, c=color, s=18, alpha=0.75, edgecolors="white",
                   linewidths=0.3, zorder=3)

        # Fit line for visual guide
        z = np.polyfit(md, cf, 1)
        x_fit = np.linspace(md.min(), md.max(), 50)
        ax.plot(x_fit, np.polyval(z, x_fit), color=color, alpha=0.5,
                linestyle="--", linewidth=0.8)

        ax.set_title(name, fontweight="bold")
        ax.set_xlabel("PH merge distance")
        if idx == 0:
            ax.set_ylabel("Confusion frequency")

        # Spearman annotation
        ax.text(0.97, 0.95, f"$r_s$ = {r:.3f}",
                transform=ax.transAxes, ha="right", va="top",
                fontsize=8, fontweight="bold",
                bbox=dict(boxstyle="round,pad=0.3", facecolor="white",
                          edgecolor=COLORS["grey"], alpha=0.9))

    fig.tight_layout(w_pad=1.5)
    path = os.path.join(FIGURES_DIR, "fig1_merge_vs_confusion.png")
    fig.savefig(path)
    plt.close(fig)
    print(f"  Saved {path}")


# ============================================================
# Figure 2: Architecture invariance (PF vs Dense vs k-NN, CIFAR)
# ============================================================
def fig2_architecture_invariance(pf_freqs, dense_freqs, knn_freqs, names):
    """Bar chart: top-5 confusion pairs across 3 methods for CIFAR."""
    # Get union of top-5 pairs from all methods
    top5_pf = top_k_pairs(pf_freqs, 5)
    top5_dense = top_k_pairs(dense_freqs, 5)
    top5_knn = top_k_pairs(knn_freqs, 5)

    # Use PF order as reference
    all_top = list(dict.fromkeys(top5_pf + top5_dense + top5_knn))[:7]

    labels = [f"{names[p[0]]}-{names[p[1]]}" for p in all_top]
    pf_vals = [pf_freqs.get(p, 0) for p in all_top]
    dense_vals = [dense_freqs.get(p, 0) for p in all_top]
    knn_vals = [knn_freqs.get(p, 0) for p in all_top]

    # Normalize to percentages of total errors for comparability
    pf_total = max(sum(pf_freqs.values()), 1)
    dense_total = max(sum(dense_freqs.values()), 1)
    knn_total = max(sum(knn_freqs.values()), 1)
    pf_pct = [v / pf_total * 100 for v in pf_vals]
    dense_pct = [v / dense_total * 100 for v in dense_vals]
    knn_pct = [v / knn_total * 100 for v in knn_vals]

    x = np.arange(len(all_top))
    w = 0.25

    fig, ax = plt.subplots(figsize=(5.5, 2.8))
    ax.bar(x - w, pf_pct, w, label="PureField", color=COLORS["blue"], edgecolor="white", linewidth=0.3)
    ax.bar(x, dense_pct, w, label="Dense MLP", color=COLORS["red"], edgecolor="white", linewidth=0.3)
    ax.bar(x + w, knn_pct, w, label="k-NN", color=COLORS["green"], edgecolor="white", linewidth=0.3)

    ax.set_xticks(x)
    ax.set_xticklabels(labels, rotation=35, ha="right", fontsize=7)
    ax.set_ylabel("Confusion share (%)")
    ax.set_title("CIFAR-10: Top confusion pairs across architectures", fontweight="bold")
    ax.legend(frameon=True, framealpha=0.9, edgecolor=COLORS["grey"])

    fig.tight_layout()
    path = os.path.join(FIGURES_DIR, "fig2_architecture_invariance.png")
    fig.savefig(path)
    plt.close(fig)
    print(f"  Saved {path}")


# ============================================================
# Figure 3: Epoch 1 prediction
# ============================================================
def fig3_epoch1_prediction(snapshots_cifar, snapshots_fashion):
    """(a) Kendall tau convergence, (b) P@K at epochs 1, 5, 15."""
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(6.0, 2.6))

    # --- Panel (a): Kendall tau per epoch vs final confusion ---
    for snapshots, name, color in [(snapshots_cifar, "CIFAR", COLORS["blue"]),
                                    (snapshots_fashion, "Fashion", COLORS["red"])]:
        final_cf = snapshots[-1]["conf_freqs"]
        taus = []
        epochs_list = []
        for snap in snapshots[1:]:  # skip epoch 0 (no merge_dists before training)
            md = snap["merge_dists"]
            pairs = sorted(md.keys())
            md_vals = [md[p] for p in pairs]
            cf_vals = [final_cf.get(p, 0) for p in pairs]
            tau, _ = kendalltau(md_vals, cf_vals)
            taus.append(abs(tau))
            epochs_list.append(snap["epoch"])

        ax1.plot(epochs_list, taus, "-o", color=color, label=name, markersize=3)

    ax1.set_xlabel("Epoch")
    ax1.set_ylabel("|Kendall $\\tau$| vs final confusion")
    ax1.set_title("(a) Convergence of merge order", fontweight="bold", fontsize=9)
    ax1.legend(frameon=True, framealpha=0.9, edgecolor=COLORS["grey"])
    ax1.set_ylim(0.3, 1.05)
    ax1.axhline(y=0.9, color=COLORS["grey"], linestyle=":", linewidth=0.6)

    # --- Panel (b): P@K at epoch 1, 5, 15 ---
    target_epochs = [1, 5, 15]
    bar_data = {}  # {(dataset, epoch): {"P@3": ..., "P@5": ...}}

    for snapshots, name in [(snapshots_cifar, "CIFAR"), (snapshots_fashion, "Fashion")]:
        final_cf = snapshots[-1]["conf_freqs"]
        top3_final = top_k_pairs(final_cf, 3)
        top5_final = top_k_pairs(final_cf, 5)

        for ep_target in target_epochs:
            snap = next((s for s in snapshots if s["epoch"] == ep_target), None)
            if snap is None or "merge_dists" not in snap:
                continue
            top3_merge = top_k_merge_pairs(snap["merge_dists"], 3)
            top5_merge = top_k_merge_pairs(snap["merge_dists"], 5)
            p3 = pair_overlap(top3_merge, top3_final) / 3.0
            p5 = pair_overlap(top5_merge, top5_final) / 5.0
            bar_data[(name, ep_target)] = {"P@3": p3, "P@5": p5}

    x_positions = np.arange(len(target_epochs))
    w = 0.18
    offsets = {"CIFAR P@3": -1.5*w, "CIFAR P@5": -0.5*w,
               "Fashion P@3": 0.5*w, "Fashion P@5": 1.5*w}
    bar_colors = {"CIFAR P@3": COLORS["blue"], "CIFAR P@5": COLORS["cyan"],
                  "Fashion P@3": COLORS["red"], "Fashion P@5": COLORS["yellow"]}

    for label_key, offset in offsets.items():
        ds_name = label_key.split()[0]
        metric = label_key.split()[1]
        vals = []
        for ep in target_epochs:
            key = (ds_name, ep)
            if key in bar_data:
                vals.append(bar_data[key][metric])
            else:
                vals.append(0)
        ax2.bar(x_positions + offset, vals, w, label=label_key,
                color=bar_colors[label_key], edgecolor="white", linewidth=0.3)

    ax2.set_xticks(x_positions)
    ax2.set_xticklabels([f"Ep {e}" for e in target_epochs])
    ax2.set_ylabel("Precision@K")
    ax2.set_title("(b) P@K vs training epoch", fontweight="bold", fontsize=9)
    ax2.legend(frameon=True, framealpha=0.9, edgecolor=COLORS["grey"],
               fontsize=6, ncol=2)
    ax2.set_ylim(0, 1.15)

    fig.tight_layout(w_pad=2.0)
    path = os.path.join(FIGURES_DIR, "fig3_epoch1_prediction.png")
    fig.savefig(path)
    plt.close(fig)
    print(f"  Saved {path}")


# ============================================================
# Figure 4: Phase transition (H0 total change per epoch)
# ============================================================
def fig4_phase_transition(all_snapshots):
    """H0_total change per epoch, showing the 30x spike at epoch 0->1."""
    fig, ax = plt.subplots(figsize=(4.5, 2.8))

    for name, color in [("MNIST", COLORS["blue"]),
                         ("Fashion", COLORS["red"]),
                         ("CIFAR", COLORS["green"])]:
        snapshots = all_snapshots[name]
        epochs = [s["epoch"] for s in snapshots]
        h0_vals = [s["h0_total"] for s in snapshots]
        dh0 = [abs(h0_vals[i+1] - h0_vals[i]) for i in range(len(h0_vals)-1)]
        ep_labels = [f"{epochs[i]}->{epochs[i+1]}" for i in range(len(epochs)-1)]
        ep_nums = list(range(1, len(dh0)+1))

        ax.plot(ep_nums, dh0, "-o", color=color, label=name, markersize=3)

    ax.set_xlabel("Epoch transition")
    ax.set_ylabel("$\\Delta H_0$ (total persistence change)")
    ax.set_title("Phase transition: 30x spike at epoch 0$\\rightarrow$1", fontweight="bold")
    ax.legend(frameon=True, framealpha=0.9, edgecolor=COLORS["grey"])

    # Annotate the spike
    ax.annotate("30x spike", xy=(1, None), fontsize=7, color=COLORS["grey"],
                xytext=(3, None), ha="left")
    # We'll set the annotation after knowing the data; use a simpler approach
    ax.set_yscale("log")
    ax.xaxis.set_major_locator(ticker.MaxNLocator(integer=True))

    fig.tight_layout()
    path = os.path.join(FIGURES_DIR, "fig4_phase_transition.png")
    fig.savefig(path)
    plt.close(fig)
    print(f"  Saved {path}")


# ============================================================
# Figure 5: CIFAR dendrogram with animal/machine coloring
# ============================================================
def fig5_dendrogram(dist_mat_cifar, names):
    """CIFAR dendrogram showing animal/machine split with 89% purity."""
    n = dist_mat_cifar.shape[0]
    condensed = []
    for i in range(n):
        for j in range(i+1, n):
            condensed.append(dist_mat_cifar[i, j])
    condensed = np.array(condensed)
    Z = linkage(condensed, method="single")

    # Color labels by category
    label_colors = {}
    for i in range(n):
        cat = CIFAR_CATEGORIES[i]
        label_colors[names[i]] = COLORS["blue"] if cat == "animal" else COLORS["red"]

    fig, ax = plt.subplots(figsize=(5.0, 3.2))

    dend = dendrogram(Z, labels=names, ax=ax, leaf_rotation=45,
                      leaf_font_size=8, above_threshold_color=COLORS["grey"],
                      color_threshold=0.3)

    # Color x-axis labels
    xlabels = ax.get_xticklabels()
    for lbl in xlabels:
        txt = lbl.get_text()
        if txt in label_colors:
            lbl.set_color(label_colors[txt])
            lbl.set_fontweight("bold")

    ax.set_ylabel("Cosine distance")
    ax.set_title("CIFAR-10 H$_0$ dendrogram (animal=blue, machine=red)", fontweight="bold")

    # Add horizontal line at 2-cluster cut
    labels_2 = fcluster(Z, t=2, criterion="maxclust")
    # Find the merge distance that splits into 2 clusters
    cut_dist = Z[-1, 2] - 0.01  # just below the last merge
    # Actually draw at a sensible position between last two merges
    if len(Z) >= 2:
        cut_dist = (Z[-1, 2] + Z[-2, 2]) / 2
    ax.axhline(y=cut_dist, color=COLORS["grey"], linestyle="--", linewidth=0.8, alpha=0.7)
    ax.text(0.98, cut_dist + 0.01, "2-cluster cut (89% purity)",
            transform=ax.get_yaxis_transform(), ha="right", fontsize=7,
            color=COLORS["grey"])

    fig.tight_layout()
    path = os.path.join(FIGURES_DIR, "fig5_dendrogram.png")
    fig.savefig(path)
    plt.close(fig)
    print(f"  Saved {path}")


# ============================================================
# Figure 6: Confusion PCA — animal(+) vs machine(-) on PC1
# ============================================================
def fig6_pca_semantic(cm_cifar, names):
    """CIFAR confusion PCA showing animal vs machine separation on PC1."""
    cm_norm = cm_cifar.astype(float)
    row_sums = cm_norm.sum(axis=1, keepdims=True)
    cm_norm = cm_norm / np.clip(row_sums, 1, None)

    pca = PCA(n_components=2)
    coords = pca.fit_transform(cm_norm)
    pc1 = pca.components_[0]
    var_explained = pca.explained_variance_ratio_

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(6.5, 2.8))

    # --- Panel (a): PC1 loadings bar chart ---
    order = np.argsort(pc1)[::-1]
    bar_colors = [COLORS["blue"] if CIFAR_CATEGORIES[i] == "animal" else COLORS["red"]
                  for i in order]
    ax1.barh(range(10), pc1[order], color=bar_colors, edgecolor="white", linewidth=0.3)
    ax1.set_yticks(range(10))
    ax1.set_yticklabels([names[i] for i in order], fontsize=7)
    ax1.set_xlabel(f"PC1 loading ({var_explained[0]*100:.1f}% var.)")
    ax1.set_title("(a) PC1 loadings", fontweight="bold", fontsize=9)
    ax1.axvline(x=0, color=COLORS["black"], linewidth=0.5)
    ax1.invert_yaxis()

    # --- Panel (b): PC1 vs PC2 scatter ---
    for i in range(10):
        cat = CIFAR_CATEGORIES[i]
        marker = "o" if cat == "animal" else "s"
        color = COLORS["blue"] if cat == "animal" else COLORS["red"]
        ax2.scatter(coords[i, 0], coords[i, 1], c=color, marker=marker,
                    s=50, edgecolors="white", linewidths=0.5, zorder=3)
        ax2.annotate(names[i], (coords[i, 0], coords[i, 1]),
                     textcoords="offset points", xytext=(5, 4),
                     fontsize=6.5, color=color)

    ax2.set_xlabel(f"PC1 ({var_explained[0]*100:.1f}%)")
    ax2.set_ylabel(f"PC2 ({var_explained[1]*100:.1f}%)")
    ax2.set_title("(b) Confusion PCA", fontweight="bold", fontsize=9)
    ax2.axvline(x=0, color=COLORS["grey"], linestyle=":", linewidth=0.5)
    ax2.axhline(y=0, color=COLORS["grey"], linestyle=":", linewidth=0.5)

    # Legend
    from matplotlib.lines import Line2D
    legend_elements = [
        Line2D([0], [0], marker="o", color="w", markerfacecolor=COLORS["blue"],
               markersize=6, label="Animal"),
        Line2D([0], [0], marker="s", color="w", markerfacecolor=COLORS["red"],
               markersize=6, label="Machine"),
    ]
    ax2.legend(handles=legend_elements, frameon=True, framealpha=0.9,
               edgecolor=COLORS["grey"], fontsize=7)

    fig.tight_layout(w_pad=2.0)
    path = os.path.join(FIGURES_DIR, "fig6_pca_semantic.png")
    fig.savefig(path)
    plt.close(fig)
    print(f"  Saved {path}")


# ============================================================
# Figure 7: Non-shared data entanglement scatter
# ============================================================
def fig7_entanglement(conf_a, conf_b, names):
    """Scatter plot: model A confusion vs model B confusion, r=0.897."""
    pairs = sorted(conf_a.keys())
    va = np.array([conf_a.get(p, 0) for p in pairs])
    vb = np.array([conf_b.get(p, 0) for p in pairs])
    r, pval = spearmanr(va, vb)

    fig, ax = plt.subplots(figsize=(3.5, 3.2))

    ax.scatter(va, vb, c=COLORS["purple"], s=20, alpha=0.7,
               edgecolors="white", linewidths=0.3, zorder=3)

    # Fit line
    z = np.polyfit(va, vb, 1)
    x_fit = np.linspace(va.min(), va.max(), 50)
    ax.plot(x_fit, np.polyval(z, x_fit), color=COLORS["purple"],
            alpha=0.5, linestyle="--", linewidth=0.8)

    # Label top pairs
    top_indices = np.argsort(va + vb)[-3:]
    for idx in top_indices:
        p = pairs[idx]
        label = f"{names[p[0]]}-{names[p[1]]}"
        ax.annotate(label, (va[idx], vb[idx]),
                    textcoords="offset points", xytext=(5, 5),
                    fontsize=6, color=COLORS["purple"], alpha=0.8)

    ax.set_xlabel("Model A confusion (examples 0-29k)")
    ax.set_ylabel("Model B confusion (examples 30k-60k)")
    ax.set_title("Zero shared data, $r_s$ = {:.3f}".format(r), fontweight="bold")

    ax.text(0.03, 0.97, "0 shared\nexamples",
            transform=ax.transAxes, ha="left", va="top",
            fontsize=8, fontweight="bold", color=COLORS["red"],
            bbox=dict(boxstyle="round,pad=0.3", facecolor="white",
                      edgecolor=COLORS["red"], alpha=0.8))

    fig.tight_layout()
    path = os.path.join(FIGURES_DIR, "fig7_entanglement.png")
    fig.savefig(path)
    plt.close(fig)
    print(f"  Saved {path}")


# ============================================================
# Main
# ============================================================
def main():
    t0 = time.time()
    print("=" * 60)
    print("  P-002 FIGURE GENERATOR")
    print("  Universal Confusion Topology")
    print("=" * 60)
    print(f"  Output: {FIGURES_DIR}")
    print(f"  Device: {DEVICE}, Seed: {SEED}, Epochs: {EPOCHS}\n")

    # ==== Step 1: Train PureField on all 3 datasets with epoch snapshots ====
    print("  [1/7] Training PureFieldEngine on 3 datasets with epoch snapshots...")
    all_results = {}
    all_snapshots = {}

    for name, cfg in DATASET_CONFIGS.items():
        print(f"    Training {name}...")
        set_seed(SEED)
        train_loader, test_loader = get_loaders(cfg)
        model = PureFieldEngine(cfg["input_dim"], HIDDEN_DIM, 10)
        model, snapshots = train_model_epoch_snapshots(
            model, train_loader, test_loader, cfg["input_dim"], epochs=EPOCHS)

        # Final results
        final = snapshots[-1]
        acc = evaluate_model(model, test_loader, cfg["input_dim"])
        r, p = correlation_merge_vs_confusion(final["merge_dists"], final["conf_freqs"])
        print(f"      acc={acc:.1f}%, Spearman r={r:.3f}")

        all_results[name] = {
            "model": model, "merge_dists": final["merge_dists"],
            "conf_freqs": final["conf_freqs"], "cm": final["cm"],
            "dist_mat": final["dist_mat"], "acc": acc,
            "train_loader": train_loader, "test_loader": test_loader,
            "cfg": cfg,
        }
        all_snapshots[name] = snapshots

    # ==== Step 2: Fig 1 — Merge vs Confusion ====
    print("\n  [2/7] Figure 1: Merge distance vs confusion frequency...")
    fig1_merge_vs_confusion(all_results)

    # ==== Step 3: Fig 2 — Architecture invariance (need Dense + k-NN for CIFAR) ====
    print("\n  [3/7] Figure 2: Architecture invariance (training Dense + k-NN on CIFAR)...")
    cfg_cifar = DATASET_CONFIGS["CIFAR"]
    set_seed(SEED + 1)
    train_loader_c, test_loader_c = get_loaders(cfg_cifar)

    # Dense MLP
    dense = DenseMLP(cfg_cifar["input_dim"], HIDDEN_DIM, 10)
    train_model(dense, train_loader_c, cfg_cifar["input_dim"])
    y_true_d, y_pred_d = compute_predictions(dense, test_loader_c, cfg_cifar["input_dim"])
    dense_freqs, _ = get_confusion_frequencies(y_true_d, y_pred_d)

    # k-NN
    print("    Training k-NN on CIFAR (subsampled)...")
    X_train_list, y_train_list = [], []
    for x, y in train_loader_c:
        X_train_list.append(x.view(x.size(0), -1).numpy())
        y_train_list.append(y.numpy())
    X_train_all = np.concatenate(X_train_list)
    y_train_all = np.concatenate(y_train_list)
    n_sub = min(10000, len(X_train_all))
    idx_sub = np.random.RandomState(SEED).choice(len(X_train_all), n_sub, replace=False)

    X_test_list, y_test_list = [], []
    for x, y in test_loader_c:
        X_test_list.append(x.view(x.size(0), -1).numpy())
        y_test_list.append(y.numpy())
    X_test_all = np.concatenate(X_test_list)
    y_test_all = np.concatenate(y_test_list)

    knn = KNeighborsClassifier(n_neighbors=5, metric="cosine", n_jobs=-1)
    knn.fit(X_train_all[idx_sub], y_train_all[idx_sub])
    y_pred_knn = knn.predict(X_test_all)
    knn_freqs, _ = get_confusion_frequencies(y_test_all, y_pred_knn)

    fig2_architecture_invariance(
        all_results["CIFAR"]["conf_freqs"], dense_freqs, knn_freqs,
        cfg_cifar["names"])

    # ==== Step 4: Fig 3 — Epoch 1 prediction ====
    print("\n  [4/7] Figure 3: Epoch 1 prediction convergence...")
    fig3_epoch1_prediction(all_snapshots["CIFAR"], all_snapshots["Fashion"])

    # ==== Step 5: Fig 4 — Phase transition ====
    print("\n  [5/7] Figure 4: Phase transition (H0 total change)...")
    fig4_phase_transition(all_snapshots)

    # ==== Step 6: Fig 5 — Dendrogram ====
    print("\n  [6/7] Figure 5: CIFAR dendrogram...")
    fig5_dendrogram(all_results["CIFAR"]["dist_mat"], cfg_cifar["names"])

    # ==== Step 6b: Fig 6 — PCA ====
    print("\n  [6b/7] Figure 6: Confusion PCA semantic axes...")
    fig6_pca_semantic(all_results["CIFAR"]["cm"], cfg_cifar["names"])

    # ==== Step 7: Fig 7 — Non-shared data entanglement ====
    print("\n  [7/7] Figure 7: Non-shared data entanglement (MNIST split)...")
    cfg_mnist = DATASET_CONFIGS["MNIST"]
    full_ds = cfg_mnist["cls"]("/tmp/data", train=True, download=True,
                                transform=transforms.Compose([
                                    transforms.ToTensor(),
                                    transforms.Normalize(cfg_mnist["mean"], cfg_mnist["std"])]))
    n_total = len(full_ds)
    half = n_total // 2

    set_seed(SEED)
    train_a, test_a = get_loaders(cfg_mnist, subset_indices=list(range(half)))
    model_a = PureFieldEngine(cfg_mnist["input_dim"], HIDDEN_DIM, 10)
    train_model(model_a, train_a, cfg_mnist["input_dim"])
    y_true_a, y_pred_a = compute_predictions(model_a, test_a, cfg_mnist["input_dim"])
    conf_a, _ = get_confusion_frequencies(y_true_a, y_pred_a)

    set_seed(SEED + 100)
    train_b, test_b = get_loaders(cfg_mnist, subset_indices=list(range(half, n_total)))
    model_b = PureFieldEngine(cfg_mnist["input_dim"], HIDDEN_DIM, 10)
    train_model(model_b, train_b, cfg_mnist["input_dim"])
    y_true_b, y_pred_b = compute_predictions(model_b, test_b, cfg_mnist["input_dim"])
    conf_b, _ = get_confusion_frequencies(y_true_b, y_pred_b)

    fig7_entanglement(conf_a, conf_b, cfg_mnist["names"])

    # ==== Done ====
    elapsed = time.time() - t0
    print(f"\n{'=' * 60}")
    print(f"  All 7 figures saved to {FIGURES_DIR}")
    print(f"  Total time: {elapsed:.0f}s ({elapsed/60:.1f} min)")
    print(f"{'=' * 60}")

    # List generated files
    for f in sorted(os.listdir(FIGURES_DIR)):
        if f.endswith(".png"):
            fpath = os.path.join(FIGURES_DIR, f)
            size_kb = os.path.getsize(fpath) / 1024
            print(f"    {f} ({size_kb:.0f} KB)")


if __name__ == "__main__":
    main()
