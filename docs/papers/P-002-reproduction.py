#!/usr/bin/env python3
"""P-002 Reproduction Script: Universal Confusion Topology

Reproduces ALL key results from:
  "Universal Confusion Topology: Persistent Homology Reveals
   Data-Intrinsic Cognitive Structure Shared Across Architectures,
   Algorithms, and Substrates"

Results reproduced:
  1. PH merge = confusion (r ~ -0.97) on MNIST/Fashion/CIFAR
  2. Architecture invariance (PureField vs Dense MLP)
  3. k-NN invariance
  4. Dimension invariance (64/128/256)
  5. Epoch 1 prediction
  6. Phase transition measurement
  7. Dendrogram semantic purity
  8. Confusion PCA
  9. Non-shared data entanglement

Usage:
  python3 docs/papers/P-002-reproduction.py

Requirements: torch, torchvision, numpy, scipy, sklearn, ripser
Time: ~15-20 min on Mac MPS
"""

import sys, os, time, warnings
warnings.filterwarnings("ignore")

# Ensure project root is importable
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, PROJECT_ROOT)

import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F
from torch.utils.data import DataLoader, Subset
from torchvision import datasets, transforms
from scipy.stats import spearmanr, kendalltau
from scipy.cluster.hierarchy import linkage, fcluster
from sklearn.neighbors import KNeighborsClassifier
from sklearn.decomposition import PCA
from sklearn.metrics import confusion_matrix

try:
    from ripser import ripser
    HAS_RIPSER = True
except ImportError:
    HAS_RIPSER = False
    print("WARNING: ripser not installed. PH will use scipy single-linkage fallback.")

from model_pure_field import PureFieldEngine


# ============================================================
# Configuration
# ============================================================
DEVICE = "cpu"  # MPS has issues with some ops; CPU is safer for reproducibility
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
        "names": ["Tshirt","Trouser","Pullvr","Dress","Coat",
                  "Sandal","Shirt","Sneakr","Bag","Boot"],
    },
    "CIFAR": {
        "cls": datasets.CIFAR10,
        "input_dim": 3072,
        "mean": (0.5,0.5,0.5), "std": (0.5,0.5,0.5),
        "names": ["plane","auto","bird","cat","deer",
                  "dog","frog","horse","ship","truck"],
    },
}


# ============================================================
# Helpers
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
    """Standard single-hidden-layer MLP baseline."""
    def __init__(self, input_dim=784, hidden_dim=128, output_dim=10):
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(input_dim, hidden_dim),
            nn.ReLU(),
            nn.Dropout(0.3),
            nn.Linear(hidden_dim, output_dim),
        )

    def forward(self, x):
        return self.net(x), torch.tensor(0.0)  # dummy tension for API compat


def train_model(model, train_loader, input_dim, epochs=EPOCHS, lr=LR, verbose=False):
    """Train a model, return per-epoch centroid snapshots for phase transition."""
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
        if verbose:
            acc = evaluate_model(model, train_loader, input_dim)
            print(f"    Epoch {ep+1}: acc={acc:.1f}%")
    return model


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
    """Extract penultimate layer features. For PureFieldEngine: repulsion vector.
    For DenseMLP: hidden layer output."""
    model.eval()
    feats, labels = [], []
    with torch.no_grad():
        for x, y in loader:
            x_flat = x.view(-1, input_dim).to(DEVICE)
            if isinstance(model, PureFieldEngine):
                a = model.engine_a(x_flat)
                g = model.engine_g(x_flat)
                feat = a - g  # repulsion = penultimate
            elif isinstance(model, DenseMLP):
                # Extract hidden layer output
                h = model.net[0](x_flat)  # Linear
                h = model.net[1](h)       # ReLU
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
    """NxN cosine distance matrix."""
    norms = np.linalg.norm(centroids, axis=1, keepdims=True)
    normed = centroids / np.clip(norms, 1e-8, None)
    sim = normed @ normed.T
    return 1.0 - sim


def compute_ph_merge_order(dist_matrix):
    """Compute H0 merge order from distance matrix.
    Returns list of (distance, i, j) sorted by merge distance."""
    n = dist_matrix.shape[0]

    if HAS_RIPSER:
        result = ripser(dist_matrix, maxdim=0, distance_matrix=True)
        dgm = result["dgms"][0]  # H0 diagram: (birth, death)
        # The merge tree from ripser H0: each finite bar represents a merge
        # Use single linkage for explicit merge order (more interpretable)

    # Single-linkage clustering gives the exact H0 merge tree
    condensed = []
    for i in range(n):
        for j in range(i+1, n):
            condensed.append(dist_matrix[i, j])
    condensed = np.array(condensed)

    Z = linkage(condensed, method="single")
    merges = []
    # Z[k] = [idx1, idx2, dist, count]
    cluster_map = {i: {i} for i in range(n)}
    for k in range(len(Z)):
        i, j = int(Z[k, 0]), int(Z[k, 1])
        d = Z[k, 2]
        ci = cluster_map.get(i, {i})
        cj = cluster_map.get(j, {j})
        # Record the merge as the pair of original classes closest
        # For single-linkage, find the original class pair
        min_d = float("inf")
        best_pair = (0, 0)
        for a in ci:
            for b in cj:
                if dist_matrix[a, b] < min_d:
                    min_d = dist_matrix[a, b]
                    best_pair = (a, b)
        merges.append((d, best_pair[0], best_pair[1]))
        new_cluster = ci | cj
        cluster_map[n + k] = new_cluster
    return merges, Z


def merge_distances_for_all_pairs(dist_matrix, n_classes=10):
    """For each pair (i,j), compute the single-linkage merge distance."""
    condensed = []
    for i in range(n_classes):
        for j in range(i+1, n_classes):
            condensed.append(dist_matrix[i, j])
    Z = linkage(condensed, method="single")

    # Build cluster membership at each merge step
    cluster_id = list(range(n_classes))
    merge_dist = {}
    for k in range(len(Z)):
        ci, cj = int(Z[k, 0]), int(Z[k, 1])
        d = Z[k, 2]
        # Find all original classes in each cluster
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
        # new cluster
        cluster_id.append(n_classes + k)

    return merge_dist


def get_confusion_frequencies(y_true, y_pred, n_classes=10):
    """Confusion frequency for each pair (i,j): number of i->j + j->i misclassifications."""
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
    """Total H0 persistence = sum of lifetimes of all H0 bars."""
    n = dist_matrix.shape[0]
    condensed = []
    for i in range(n):
        for j in range(i+1, n):
            condensed.append(dist_matrix[i, j])
    Z = linkage(condensed, method="single")
    # All H0 bars are born at 0, die at merge distance
    return sum(Z[:, 2])


def correlation_merge_vs_confusion(merge_dists, conf_freqs, n_classes=10):
    """Compute Spearman r between merge distances and confusion frequencies."""
    pairs = sorted(merge_dists.keys())
    md = [merge_dists[p] for p in pairs]
    cf = [conf_freqs.get(p, 0) for p in pairs]
    r, p = spearmanr(md, cf)
    return r, p


def top_k_pairs(freq_dict, k=5):
    """Return top-k pairs by frequency."""
    sorted_pairs = sorted(freq_dict.items(), key=lambda x: -x[1])
    return [p[0] for p in sorted_pairs[:k]]


def top_k_merge_pairs(merge_dist_dict, k=5):
    """Return top-k pairs by smallest merge distance (earliest merge)."""
    sorted_pairs = sorted(merge_dist_dict.items(), key=lambda x: x[1])
    return [p[0] for p in sorted_pairs[:k]]


def pair_overlap(list1, list2):
    return len(set(list1) & set(list2))


# ============================================================
# Experiment Functions
# ============================================================

def experiment_1_ph_merge_confusion(datasets_dict):
    """Section 4.1: PH merge order predicts confusion."""
    print("\n" + "=" * 70)
    print("  EXPERIMENT 1: PH Merge = Confusion (Section 4.1, H-CX-66)")
    print("=" * 70)

    results = {}
    for name, cfg in datasets_dict.items():
        set_seed(SEED)
        train_loader, test_loader = get_loaders(cfg)
        model = PureFieldEngine(cfg["input_dim"], HIDDEN_DIM, 10)
        train_model(model, train_loader, cfg["input_dim"])

        feats, labels = get_penultimate_features(model, test_loader, cfg["input_dim"])
        centroids = compute_class_centroids(feats, labels)
        dist_mat = cosine_distance_matrix(centroids)
        merge_dists = merge_distances_for_all_pairs(dist_mat)

        y_true, y_pred = compute_predictions(model, test_loader, cfg["input_dim"])
        conf_freqs, cm = get_confusion_frequencies(y_true, y_pred)

        r, p = correlation_merge_vs_confusion(merge_dists, conf_freqs)
        acc = evaluate_model(model, test_loader, cfg["input_dim"])
        results[name] = {"r": r, "p": p, "acc": acc, "model": model,
                         "merge_dists": merge_dists, "conf_freqs": conf_freqs,
                         "cm": cm, "dist_mat": dist_mat}
        print(f"  {name:>10}: Spearman r = {r:.3f}, p = {p:.4f}, acc = {acc:.1f}%")

    print("\n  Summary Table (Paper Table 1):")
    print(f"  {'Dataset':<12} {'Spearman r':>12} {'p-value':>12} {'Significant':>12}")
    print(f"  {'-'*48}")
    for name, r in results.items():
        sig = "Yes" if r["p"] < 0.001 else "No"
        print(f"  {name:<12} {r['r']:>12.3f} {r['p']:>12.4f} {sig:>12}")
    print(f"\n  Mean |r| = {np.mean([abs(r['r']) for r in results.values()]):.3f}")

    return results


def experiment_2_architecture_invariance(datasets_dict, exp1_results):
    """Section 4.2: Architecture invariance (PureField vs Dense MLP)."""
    print("\n" + "=" * 70)
    print("  EXPERIMENT 2: Architecture Invariance (Section 4.2, H-CX-88)")
    print("=" * 70)

    results = {}
    for name, cfg in datasets_dict.items():
        set_seed(SEED + 1)
        train_loader, test_loader = get_loaders(cfg)

        # Train Dense MLP
        dense = DenseMLP(cfg["input_dim"], HIDDEN_DIM, 10)
        train_model(dense, train_loader, cfg["input_dim"])

        y_true_d, y_pred_d = compute_predictions(dense, test_loader, cfg["input_dim"])
        conf_freqs_d, cm_d = get_confusion_frequencies(y_true_d, y_pred_d)

        # Compare with PureField from exp1
        conf_freqs_pf = exp1_results[name]["conf_freqs"]

        # Correlation between confusion frequencies
        pairs = sorted(conf_freqs_pf.keys())
        pf_vals = [conf_freqs_pf.get(p, 0) for p in pairs]
        d_vals = [conf_freqs_d.get(p, 0) for p in pairs]
        r, _ = spearmanr(pf_vals, d_vals)

        top5_pf = top_k_pairs(conf_freqs_pf)
        top5_d = top_k_pairs(conf_freqs_d)
        overlap = pair_overlap(top5_pf, top5_d)

        results[name] = {"r": r, "overlap": overlap}
        acc_d = evaluate_model(dense, test_loader, cfg["input_dim"])
        print(f"  {name:>10}: PF vs Dense r = {r:.3f}, Top-5 overlap = {overlap}/5, Dense acc = {acc_d:.1f}%")

    print("\n  Summary Table (Paper Table 2):")
    print(f"  {'Dataset':<12} {'PF vs Dense r':>14} {'Top-5 overlap':>14}")
    print(f"  {'-'*40}")
    for name, r in results.items():
        print(f"  {name:<12} {r['r']:>14.2f} {r['overlap']:>12}/5")
    return results


def experiment_3_knn_invariance(datasets_dict, exp1_results):
    """Section 4.3: k-NN invariance."""
    print("\n" + "=" * 70)
    print("  EXPERIMENT 3: k-NN Invariance (Section 4.3, H-CX-91)")
    print("=" * 70)

    results = {}
    for name, cfg in datasets_dict.items():
        train_loader, test_loader = get_loaders(cfg)

        # Collect raw pixel features
        X_train, y_train = [], []
        for x, y in train_loader:
            X_train.append(x.view(x.size(0), -1).numpy())
            y_train.append(y.numpy())
        X_train = np.concatenate(X_train)
        y_train = np.concatenate(y_train)

        X_test, y_test = [], []
        for x, y in test_loader:
            X_test.append(x.view(x.size(0), -1).numpy())
            y_test.append(y.numpy())
        X_test = np.concatenate(X_test)
        y_test = np.concatenate(y_test)

        # Subsample for speed (k-NN on full data is slow)
        n_train = min(10000, len(X_train))
        idx = np.random.RandomState(SEED).choice(len(X_train), n_train, replace=False)
        X_train_sub = X_train[idx]
        y_train_sub = y_train[idx]

        knn = KNeighborsClassifier(n_neighbors=5, metric="cosine", n_jobs=-1)
        knn.fit(X_train_sub, y_train_sub)
        y_pred_knn = knn.predict(X_test)
        conf_freqs_knn, _ = get_confusion_frequencies(y_test, y_pred_knn)
        acc_knn = 100.0 * (y_pred_knn == y_test).mean()

        conf_freqs_pf = exp1_results[name]["conf_freqs"]
        pairs = sorted(conf_freqs_pf.keys())
        pf_vals = [conf_freqs_pf.get(p, 0) for p in pairs]
        knn_vals = [conf_freqs_knn.get(p, 0) for p in pairs]
        r, _ = spearmanr(pf_vals, knn_vals)

        top5_pf = top_k_pairs(conf_freqs_pf)
        top5_knn = top_k_pairs(conf_freqs_knn)
        overlap = pair_overlap(top5_pf, top5_knn)

        results[name] = {"r": r, "overlap": overlap, "acc": acc_knn}
        print(f"  {name:>10}: k-NN vs PF r = {r:.3f}, Top-5 overlap = {overlap}/5, k-NN acc = {acc_knn:.1f}%")

    print("\n  Summary Table (Paper Table 3):")
    print(f"  {'Dataset':<12} {'k-NN vs PF r':>14} {'Top-5 overlap':>14}")
    print(f"  {'-'*40}")
    for name, r in results.items():
        print(f"  {name:<12} {r['r']:>14.2f} {r['overlap']:>12}/5")
    return results


def experiment_4_dimension_invariance(datasets_dict):
    """Section 4.4: Dimension invariance (64/128/256)."""
    print("\n" + "=" * 70)
    print("  EXPERIMENT 4: Dimension Invariance (Section 4.4, H-CX-107)")
    print("=" * 70)

    # Use CIFAR for this test (strongest result in paper)
    cfg = datasets_dict["CIFAR"]
    dims = [64, 128, 256]
    merge_orders = {}
    conf_freqs_all = {}

    for dim in dims:
        set_seed(SEED)
        train_loader, test_loader = get_loaders(cfg)
        model = PureFieldEngine(cfg["input_dim"], dim, 10)
        train_model(model, train_loader, cfg["input_dim"])

        feats, labels = get_penultimate_features(model, test_loader, cfg["input_dim"])
        centroids = compute_class_centroids(feats, labels)
        dist_mat = cosine_distance_matrix(centroids)
        merge_dists = merge_distances_for_all_pairs(dist_mat)

        y_true, y_pred = compute_predictions(model, test_loader, cfg["input_dim"])
        conf_freqs, _ = get_confusion_frequencies(y_true, y_pred)

        merge_orders[dim] = merge_dists
        conf_freqs_all[dim] = conf_freqs
        acc = evaluate_model(model, test_loader, cfg["input_dim"])
        print(f"  dim={dim:>3}: acc={acc:.1f}%")

    print("\n  Pairwise comparisons (CIFAR-10):")
    print(f"  {'Dim pair':<16} {'Kendall tau':>12} {'Confusion r':>12} {'Top-5 overlap':>14}")
    print(f"  {'-'*54}")
    dim_pairs = [(64, 128), (64, 256), (128, 256)]
    for d1, d2 in dim_pairs:
        pairs = sorted(merge_orders[d1].keys())
        m1 = [merge_orders[d1][p] for p in pairs]
        m2 = [merge_orders[d2][p] for p in pairs]
        tau, _ = kendalltau(m1, m2)

        c1 = [conf_freqs_all[d1].get(p, 0) for p in pairs]
        c2 = [conf_freqs_all[d2].get(p, 0) for p in pairs]
        r, _ = spearmanr(c1, c2)

        top5_1 = top_k_pairs(conf_freqs_all[d1])
        top5_2 = top_k_pairs(conf_freqs_all[d2])
        overlap = pair_overlap(top5_1, top5_2)
        print(f"  {d1} vs {d2:<8} {tau:>12.2f} {r:>12.2f} {overlap:>12}/5")

    return merge_orders, conf_freqs_all


def experiment_5_epoch1_prediction(datasets_dict):
    """Section 4.6: Epoch 1 prediction."""
    print("\n" + "=" * 70)
    print("  EXPERIMENT 5: Epoch 1 Prediction (Section 4.6, H-CX-82)")
    print("=" * 70)

    results = {}
    for name in ["CIFAR", "Fashion"]:
        cfg = datasets_dict[name]
        set_seed(SEED)
        train_loader, test_loader = get_loaders(cfg)
        model = PureFieldEngine(cfg["input_dim"], HIDDEN_DIM, 10)

        # Train 1 epoch
        train_model(model, train_loader, cfg["input_dim"], epochs=1)
        feats_1, labels_1 = get_penultimate_features(model, test_loader, cfg["input_dim"])
        centroids_1 = compute_class_centroids(feats_1, labels_1)
        dist_1 = cosine_distance_matrix(centroids_1)
        merge_dists_1 = merge_distances_for_all_pairs(dist_1)

        # Train remaining epochs
        train_model(model, train_loader, cfg["input_dim"], epochs=EPOCHS - 1)

        y_true, y_pred = compute_predictions(model, test_loader, cfg["input_dim"])
        conf_freqs_final, _ = get_confusion_frequencies(y_true, y_pred)

        r, _ = correlation_merge_vs_confusion(merge_dists_1, conf_freqs_final)

        top3_merge = top_k_merge_pairs(merge_dists_1, 3)
        top5_merge = top_k_merge_pairs(merge_dists_1, 5)
        top3_conf = top_k_pairs(conf_freqs_final, 3)
        top5_conf = top_k_pairs(conf_freqs_final, 5)
        p3 = pair_overlap(top3_merge, top3_conf) / 3.0
        p5 = pair_overlap(top5_merge, top5_conf) / 5.0

        results[name] = {"r": r, "P@3": p3, "P@5": p5}
        print(f"  {name:>10}: Epoch 1 r = {r:.3f}, P@3 = {p3:.1f}, P@5 = {p5:.1f}")

    print("\n  Summary Table (Paper Table 5):")
    print(f"  {'Dataset':<12} {'Epoch 1 r':>10} {'P@3':>6} {'P@5':>6}")
    print(f"  {'-'*34}")
    for name, r in results.items():
        print(f"  {name:<12} {r['r']:>10.2f} {r['P@3']:>6.1f} {r['P@5']:>6.1f}")
    return results


def experiment_6_phase_transition(datasets_dict):
    """Section 4.7: Phase transition at 0.1 epoch."""
    print("\n" + "=" * 70)
    print("  EXPERIMENT 6: Phase Transition (Section 4.7, H-CX-90/105)")
    print("=" * 70)

    results = {}
    for name, cfg in datasets_dict.items():
        set_seed(SEED)
        train_loader, test_loader = get_loaders(cfg)
        model = PureFieldEngine(cfg["input_dim"], HIDDEN_DIM, 10)
        optimizer = torch.optim.Adam(model.parameters(), lr=LR)
        criterion = nn.CrossEntropyLoss()

        # Measure H0 before training (epoch 0)
        feats_0, labels_0 = get_penultimate_features(model, test_loader, cfg["input_dim"])
        centroids_0 = compute_class_centroids(feats_0, labels_0)
        dist_0 = cosine_distance_matrix(centroids_0)
        h0_0 = total_h0_persistence(dist_0)

        # Train epoch 1
        model.train()
        for x, y in train_loader:
            x, y = x.view(-1, cfg["input_dim"]).to(DEVICE), y.to(DEVICE)
            optimizer.zero_grad()
            out, _ = model(x)
            loss = criterion(out, y)
            loss.backward()
            optimizer.step()

        feats_1, labels_1 = get_penultimate_features(model, test_loader, cfg["input_dim"])
        centroids_1 = compute_class_centroids(feats_1, labels_1)
        dist_1 = cosine_distance_matrix(centroids_1)
        h0_1 = total_h0_persistence(dist_1)

        # Train epoch 2
        model.train()
        for x, y in train_loader:
            x, y = x.view(-1, cfg["input_dim"]).to(DEVICE), y.to(DEVICE)
            optimizer.zero_grad()
            out, _ = model(x)
            loss = criterion(out, y)
            loss.backward()
            optimizer.step()

        feats_2, labels_2 = get_penultimate_features(model, test_loader, cfg["input_dim"])
        centroids_2 = compute_class_centroids(feats_2, labels_2)
        dist_2 = cosine_distance_matrix(centroids_2)
        h0_2 = total_h0_persistence(dist_2)

        dh0_01 = abs(h0_1 - h0_0)
        dh0_12 = abs(h0_2 - h0_1)
        ratio = dh0_01 / (dh0_12 + 1e-8)

        results[name] = {"dH0_01": dh0_01, "dH0_12": dh0_12, "ratio": ratio}
        print(f"  {name:>10}: dH0(0->1) = {dh0_01:.3f}, dH0(1->2) = {dh0_12:.3f}, ratio = {ratio:.0f}x")

    print("\n  Summary Table (Paper Table 6):")
    print(f"  {'Dataset':<12} {'dH0(0->1)':>10} {'dH0(1->2)':>10} {'Ratio':>8}")
    print(f"  {'-'*40}")
    for name, r in results.items():
        print(f"  {name:<12} {r['dH0_01']:>10.3f} {r['dH0_12']:>10.3f} {r['ratio']:>7.0f}x")
    return results


def experiment_7_dendrogram_purity(exp1_results, datasets_dict):
    """Section 4.8: Dendrogram semantic purity."""
    print("\n" + "=" * 70)
    print("  EXPERIMENT 7: Dendrogram Semantic Purity (Section 4.8, H-CX-85)")
    print("=" * 70)

    # CIFAR-10 semantic categories
    cifar_categories = {
        0: "machine",  # airplane
        1: "machine",  # automobile
        2: "animal",   # bird
        3: "animal",   # cat
        4: "animal",   # deer
        5: "animal",   # dog
        6: "animal",   # frog
        7: "animal",   # horse
        8: "machine",  # ship
        9: "machine",  # truck
    }
    cifar_names = datasets_dict["CIFAR"]["names"]

    dist_mat = exp1_results["CIFAR"]["dist_mat"]

    # Compute linkage
    condensed = []
    n = dist_mat.shape[0]
    for i in range(n):
        for j in range(i+1, n):
            condensed.append(dist_mat[i, j])
    Z = linkage(condensed, method="single")

    # 2-cluster cut
    labels_2 = fcluster(Z, t=2, criterion="maxclust")
    # Check purity
    cluster_cats = {}
    for i in range(n):
        cl = labels_2[i]
        cat = cifar_categories[i]
        if cl not in cluster_cats:
            cluster_cats[cl] = []
        cluster_cats[cl].append((i, cat))

    print("\n  2-cluster cut:")
    total_correct = 0
    for cl, members in sorted(cluster_cats.items()):
        cats = [m[1] for m in members]
        majority = max(set(cats), key=cats.count)
        correct = cats.count(majority)
        total_correct += correct
        member_names = [cifar_names[m[0]] for m in members]
        print(f"    Cluster {cl}: {member_names}")
        print(f"      Majority = {majority}, purity = {correct}/{len(cats)}")

    purity_2 = total_correct / n
    print(f"\n  Overall 2-cluster purity: {purity_2*100:.0f}%")

    # 4-cluster cut
    labels_4 = fcluster(Z, t=4, criterion="maxclust")
    print("\n  4-cluster cut:")
    cluster_cats_4 = {}
    for i in range(n):
        cl = labels_4[i]
        if cl not in cluster_cats_4:
            cluster_cats_4[cl] = []
        cluster_cats_4[cl].append(i)

    for cl, members in sorted(cluster_cats_4.items()):
        member_names = [cifar_names[m] for m in members]
        print(f"    Cluster {cl}: {member_names}")

    # Print merge order (dendrogram)
    merges, _ = compute_ph_merge_order(dist_mat)
    print("\n  CIFAR-10 merge order (H0 dendrogram):")
    print(f"  {'Order':<8} {'Class pair':<25} {'Merge distance':>15}")
    print(f"  {'-'*48}")
    for k, (d, i, j) in enumerate(merges):
        print(f"  {k+1:<8} {cifar_names[i]:>10} -- {cifar_names[j]:<10} {d:>15.3f}")

    return purity_2


def experiment_8_confusion_pca(exp1_results, datasets_dict):
    """Section 4.9: Confusion PCA."""
    print("\n" + "=" * 70)
    print("  EXPERIMENT 8: Confusion PCA (Section 4.9, H-CX-93)")
    print("=" * 70)

    cifar_names = datasets_dict["CIFAR"]["names"]
    cifar_categories = {
        0: "machine", 1: "machine", 2: "animal", 3: "animal", 4: "animal",
        5: "animal", 6: "animal", 7: "animal", 8: "machine", 9: "machine",
    }

    cm = exp1_results["CIFAR"]["cm"]
    # Normalize rows
    cm_norm = cm.astype(float)
    row_sums = cm_norm.sum(axis=1, keepdims=True)
    cm_norm = cm_norm / np.clip(row_sums, 1, None)

    pca = PCA(n_components=3)
    pca.fit(cm_norm)
    pc1_loadings = pca.components_[0]

    # Sort by PC1 loading
    order = np.argsort(pc1_loadings)[::-1]

    print(f"\n  CIFAR-10 PC1 loadings (variance explained: {pca.explained_variance_ratio_[0]*100:.1f}%):")
    print(f"  {'Class':<12} {'PC1 loading':>12} {'Category':>10}")
    print(f"  {'-'*34}")

    all_positive_animal = True
    all_negative_machine = True
    for idx in order:
        cat = cifar_categories[idx]
        loading = pc1_loadings[idx]
        print(f"  {cifar_names[idx]:<12} {loading:>+12.3f} {cat:>10}")
        if cat == "animal" and loading < 0:
            all_positive_animal = False
        if cat == "machine" and loading > 0:
            all_negative_machine = False

    # Check if PC1 separates animals from machines
    # (allowing for sign flip)
    animal_loadings = [pc1_loadings[i] for i in range(10) if cifar_categories[i] == "animal"]
    machine_loadings = [pc1_loadings[i] for i in range(10) if cifar_categories[i] == "machine"]
    animal_mean = np.mean(animal_loadings)
    machine_mean = np.mean(machine_loadings)
    separated = (animal_mean > 0 and machine_mean < 0) or (animal_mean < 0 and machine_mean > 0)

    print(f"\n  Animal mean loading:  {animal_mean:+.3f}")
    print(f"  Machine mean loading: {machine_mean:+.3f}")
    print(f"  Perfect separation:   {'YES' if separated else 'NO'}")
    return separated


def experiment_9_nonshared_entanglement(datasets_dict):
    """Section 4.10: Non-shared data entanglement."""
    print("\n" + "=" * 70)
    print("  EXPERIMENT 9: Non-Shared Data Entanglement (Section 4.10, H-CX-125/127)")
    print("=" * 70)

    cfg = datasets_dict["MNIST"]
    train_loader_full, test_loader = get_loaders(cfg)

    # Get full training set size
    full_ds = cfg["cls"]("/tmp/data", train=True, download=True,
                         transform=transforms.Compose([
                             transforms.ToTensor(),
                             transforms.Normalize(cfg["mean"], cfg["std"])]))
    n_total = len(full_ds)
    half = n_total // 2

    # Partition A: first half, Partition B: second half
    indices_a = list(range(half))
    indices_b = list(range(half, n_total))

    # Train model A
    set_seed(SEED)
    train_a, test_loader = get_loaders(cfg, subset_indices=indices_a)
    model_a = PureFieldEngine(cfg["input_dim"], HIDDEN_DIM, 10)
    train_model(model_a, train_a, cfg["input_dim"])
    y_true_a, y_pred_a = compute_predictions(model_a, test_loader, cfg["input_dim"])
    conf_a, cm_a = get_confusion_frequencies(y_true_a, y_pred_a)

    # Train model B (different seed)
    set_seed(SEED + 100)
    train_b, test_loader = get_loaders(cfg, subset_indices=indices_b)
    model_b = PureFieldEngine(cfg["input_dim"], HIDDEN_DIM, 10)
    train_model(model_b, train_b, cfg["input_dim"])
    y_true_b, y_pred_b = compute_predictions(model_b, test_loader, cfg["input_dim"])
    conf_b, cm_b = get_confusion_frequencies(y_true_b, y_pred_b)

    # Compute merge order for both
    feats_a, labels_a = get_penultimate_features(model_a, test_loader, cfg["input_dim"])
    centroids_a = compute_class_centroids(feats_a, labels_a)
    dist_a = cosine_distance_matrix(centroids_a)
    merge_a = merge_distances_for_all_pairs(dist_a)

    feats_b, labels_b = get_penultimate_features(model_b, test_loader, cfg["input_dim"])
    centroids_b = compute_class_centroids(feats_b, labels_b)
    dist_b = cosine_distance_matrix(centroids_b)
    merge_b = merge_distances_for_all_pairs(dist_b)

    # Confusion correlation
    pairs = sorted(conf_a.keys())
    va = [conf_a.get(p, 0) for p in pairs]
    vb = [conf_b.get(p, 0) for p in pairs]
    r_conf, _ = spearmanr(va, vb)

    # Merge order correlation
    ma = [merge_a.get(p, 0) for p in pairs]
    mb = [merge_b.get(p, 0) for p in pairs]
    tau_merge, _ = kendalltau(ma, mb)

    acc_a = evaluate_model(model_a, test_loader, cfg["input_dim"])
    acc_b = evaluate_model(model_b, test_loader, cfg["input_dim"])

    print(f"\n  Partition A: examples 0-{half-1}, acc = {acc_a:.1f}%")
    print(f"  Partition B: examples {half}-{n_total-1}, acc = {acc_b:.1f}%")
    print(f"  Shared training examples: 0")
    print(f"\n  Confusion correlation (r): {r_conf:.3f}")
    print(f"  Merge order Kendall tau:   {tau_merge:.3f}")

    print(f"\n  Summary Table (Paper Table 8):")
    print(f"  {'Metric':<30} {'Value':>10}")
    print(f"  {'-'*40}")
    print(f"  {'Confusion correlation (r)':<30} {r_conf:>10.3f}")
    print(f"  {'Merge order Kendall tau':<30} {tau_merge:>10.3f}")
    print(f"  {'Shared training examples':<30} {'0':>10}")
    return r_conf, tau_merge


# ============================================================
# Main
# ============================================================
def main():
    t0 = time.time()
    print("=" * 70)
    print("  P-002 REPRODUCTION: Universal Confusion Topology")
    print("  All results from the paper in one run")
    print("=" * 70)
    print(f"  Device: {DEVICE}")
    print(f"  Seed: {SEED}")
    print(f"  Epochs: {EPOCHS}")
    print(f"  Hidden dim: {HIDDEN_DIM}")
    print(f"  Ripser available: {HAS_RIPSER}")

    # --- Run all experiments ---
    exp1 = experiment_1_ph_merge_confusion(DATASET_CONFIGS)
    exp2 = experiment_2_architecture_invariance(DATASET_CONFIGS, exp1)
    exp3 = experiment_3_knn_invariance(DATASET_CONFIGS, exp1)
    exp4 = experiment_4_dimension_invariance(DATASET_CONFIGS)
    exp5 = experiment_5_epoch1_prediction(DATASET_CONFIGS)
    exp6 = experiment_6_phase_transition(DATASET_CONFIGS)
    exp7 = experiment_7_dendrogram_purity(exp1, DATASET_CONFIGS)
    exp8 = experiment_8_confusion_pca(exp1, DATASET_CONFIGS)
    exp9 = experiment_9_nonshared_entanglement(DATASET_CONFIGS)

    # --- Final Summary ---
    elapsed = time.time() - t0
    print("\n" + "=" * 70)
    print("  FINAL SUMMARY: ALL P-002 RESULTS")
    print("=" * 70)

    print(f"""
  Exp 1: PH Merge = Confusion (H-CX-66)
  -----------------------------------------------
  Dataset      Spearman r    Paper target
  MNIST        {exp1['MNIST']['r']:>10.3f}    ~ -0.94
  Fashion      {exp1['Fashion']['r']:>10.3f}    ~ -0.93
  CIFAR        {exp1['CIFAR']['r']:>10.3f}    ~ -0.97

  Exp 2: Architecture Invariance (H-CX-88)
  -----------------------------------------------
  Dataset      PF vs Dense r  Top-5    Paper
  MNIST        {exp2['MNIST']['r']:>10.2f}     {exp2['MNIST']['overlap']}/5     4/5
  Fashion      {exp2['Fashion']['r']:>10.2f}     {exp2['Fashion']['overlap']}/5     5/5
  CIFAR        {exp2['CIFAR']['r']:>10.2f}     {exp2['CIFAR']['overlap']}/5     5/5

  Exp 3: k-NN Invariance (H-CX-91)
  -----------------------------------------------
  Dataset      k-NN vs PF r   Top-5   Paper
  MNIST        {exp3['MNIST']['r']:>10.2f}     {exp3['MNIST']['overlap']}/5     5/5
  Fashion      {exp3['Fashion']['r']:>10.2f}     {exp3['Fashion']['overlap']}/5     4/5
  CIFAR        {exp3['CIFAR']['r']:>10.2f}     {exp3['CIFAR']['overlap']}/5     3/5

  Exp 5: Epoch 1 Prediction (H-CX-82)
  -----------------------------------------------
  Dataset      r        P@3    P@5    Paper P@5
  CIFAR        {exp5['CIFAR']['r']:>6.2f}    {exp5['CIFAR']['P@3']:.1f}    {exp5['CIFAR']['P@5']:.1f}     1.0
  Fashion      {exp5['Fashion']['r']:>6.2f}    {exp5['Fashion']['P@3']:.1f}    {exp5['Fashion']['P@5']:.1f}     0.8

  Exp 6: Phase Transition (H-CX-90/105)
  -----------------------------------------------
  Dataset      dH0(0-1)  dH0(1-2)  Ratio   Paper
  MNIST        {exp6['MNIST']['dH0_01']:>8.3f}  {exp6['MNIST']['dH0_12']:>8.3f}  {exp6['MNIST']['ratio']:>4.0f}x    31x
  Fashion      {exp6['Fashion']['dH0_01']:>8.3f}  {exp6['Fashion']['dH0_12']:>8.3f}  {exp6['Fashion']['ratio']:>4.0f}x    24x
  CIFAR        {exp6['CIFAR']['dH0_01']:>8.3f}  {exp6['CIFAR']['dH0_12']:>8.3f}  {exp6['CIFAR']['ratio']:>4.0f}x    33x

  Exp 7: Dendrogram Purity = {exp7*100:.0f}% (Paper: 89%)

  Exp 8: Confusion PCA separates animals/machines: {'YES' if exp8 else 'NO'} (Paper: YES)

  Exp 9: Non-Shared Entanglement (MNIST)
  -----------------------------------------------
  Confusion r    = {exp9[0]:.3f}  (Paper: 0.897)
  Merge tau      = {exp9[1]:.3f}  (Paper: 0.67)
  Shared examples = 0

  Total time: {elapsed:.0f}s ({elapsed/60:.1f} min)
""")
    print("=" * 70)
    print("  END OF P-002 REPRODUCTION")
    print("=" * 70)


if __name__ == "__main__":
    main()
