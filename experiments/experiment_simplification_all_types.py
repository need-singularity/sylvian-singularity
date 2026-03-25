#!/usr/bin/env python3
"""ALL 14 Data Types: Simplification Verification

Tests 4 variants across all data types:
  1. Original:     scale * sqrt(tension) * direction  (with tension_scale param)
  2. Pure Tension:  scale * sqrt(tension) * direction  (same, explicit)
  3. Raw (A-G):    just A - G
  4. Dense:        single MLP baseline

Key question: Does scale*sqrt*dir help on ALL types, or only some?
"""
import sys, os, time, math
import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F
from torch.utils.data import DataLoader, TensorDataset

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
_print = print
print = lambda *a, **k: (_print(*a, **k, flush=True))


# ═══════════════════════════════════════════
# Models
# ═══════════════════════════════════════════

class Dense(nn.Module):
    def __init__(self, d_in, d_hid, d_out):
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(d_in, d_hid), nn.ReLU(), nn.Dropout(0.3),
            nn.Linear(d_hid, d_out))
    def forward(self, x):
        return self.net(x)


class Original(nn.Module):
    """scale * sqrt(mean(|A-G|^2)) * normalize(A-G) — with learnable scale"""
    def __init__(self, d_in, d_hid, d_out):
        super().__init__()
        self.a = nn.Sequential(nn.Linear(d_in, d_hid), nn.ReLU(), nn.Dropout(0.3), nn.Linear(d_hid, d_out))
        self.g = nn.Sequential(nn.Linear(d_in, d_hid), nn.ReLU(), nn.Dropout(0.3), nn.Linear(d_hid, d_out))
        self.scale = nn.Parameter(torch.ones(1))
    def forward(self, x):
        rep = self.a(x) - self.g(x)
        t = rep.pow(2).mean(dim=-1, keepdim=True)
        d = rep / (rep.norm(dim=-1, keepdim=True) + 1e-8)
        return self.scale * torch.sqrt(t + 1e-8) * d


class RawAG(nn.Module):
    """output = A - G. Maximum simplicity."""
    def __init__(self, d_in, d_hid, d_out):
        super().__init__()
        self.a = nn.Sequential(nn.Linear(d_in, d_hid), nn.ReLU(), nn.Dropout(0.3), nn.Linear(d_hid, d_out))
        self.g = nn.Sequential(nn.Linear(d_in, d_hid), nn.ReLU(), nn.Dropout(0.3), nn.Linear(d_hid, d_out))
    def forward(self, x):
        return self.a(x) - self.g(x)


class ScaledAG(nn.Module):
    """output = scale * (A - G). One learnable param."""
    def __init__(self, d_in, d_hid, d_out):
        super().__init__()
        self.a = nn.Sequential(nn.Linear(d_in, d_hid), nn.ReLU(), nn.Dropout(0.3), nn.Linear(d_hid, d_out))
        self.g = nn.Sequential(nn.Linear(d_in, d_hid), nn.ReLU(), nn.Dropout(0.3), nn.Linear(d_hid, d_out))
        self.scale = nn.Parameter(torch.ones(1))
    def forward(self, x):
        return self.scale * (self.a(x) - self.g(x))


# ═══════════════════════════════════════════
# Data Loaders (all 14 types)
# ═══════════════════════════════════════════

def load_mnist():
    from torchvision import datasets, transforms
    t = transforms.Compose([transforms.ToTensor(), transforms.Normalize((0.1307,), (0.3081,))])
    tr = datasets.MNIST('./data', train=True, download=True, transform=t)
    te = datasets.MNIST('./data', train=False, transform=t)
    X_tr = tr.data.float().view(-1, 784) / 255.0
    y_tr = tr.targets
    X_te = te.data.float().view(-1, 784) / 255.0
    y_te = te.targets
    return X_tr, y_tr, X_te, y_te, 784, 10, 'Image MNIST'


def load_cifar():
    from torchvision import datasets, transforms
    t = transforms.Compose([transforms.ToTensor(), transforms.Normalize((0.5,0.5,0.5),(0.5,0.5,0.5))])
    tr = datasets.CIFAR10('./data', train=True, download=True, transform=t)
    te = datasets.CIFAR10('./data', train=False, transform=t)
    X_tr = torch.stack([x for x,_ in tr]).view(-1, 3072)
    y_tr = torch.tensor(tr.targets)
    X_te = torch.stack([x for x,_ in te]).view(-1, 3072)
    y_te = torch.tensor(te.targets)
    return X_tr, y_tr, X_te, y_te, 3072, 10, 'Image CIFAR'


def load_text_tfidf():
    from sklearn.datasets import fetch_20newsgroups
    from sklearn.feature_extraction.text import TfidfVectorizer
    cats = ['sci.space', 'rec.sport.baseball', 'comp.graphics', 'talk.politics.guns']
    tr = fetch_20newsgroups(subset='train', categories=cats, remove=('headers','footers','quotes'))
    te = fetch_20newsgroups(subset='test', categories=cats, remove=('headers','footers','quotes'))
    vec = TfidfVectorizer(max_features=500)
    X_tr = torch.tensor(vec.fit_transform(tr.data).toarray(), dtype=torch.float32)
    y_tr = torch.tensor(tr.target, dtype=torch.long)
    X_te = torch.tensor(vec.transform(te.data).toarray(), dtype=torch.float32)
    y_te = torch.tensor(te.target, dtype=torch.long)
    return X_tr, y_tr, X_te, y_te, 500, 4, 'Text TF-IDF'


def load_text_embedding():
    from sklearn.datasets import fetch_20newsgroups
    cats = ['sci.space', 'rec.sport.baseball', 'comp.graphics', 'talk.politics.guns']
    tr = fetch_20newsgroups(subset='train', categories=cats, remove=('headers','footers','quotes'))
    te = fetch_20newsgroups(subset='test', categories=cats, remove=('headers','footers','quotes'))
    vocab_size = 5000
    embed_dim = 64
    # Simple word-index averaging
    from collections import Counter
    all_words = ' '.join(tr.data).lower().split()
    top_words = [w for w, _ in Counter(all_words).most_common(vocab_size)]
    w2i = {w: i+1 for i, w in enumerate(top_words)}
    def text_to_vec(texts):
        vecs = []
        for text in texts:
            words = text.lower().split()
            idxs = [w2i.get(w, 0) for w in words[:200]]
            if not idxs: idxs = [0]
            vecs.append(np.mean([[hash(str(i*j)) % 1000 / 1000.0 for j in range(embed_dim)] for i in idxs], axis=0))
        return torch.tensor(np.array(vecs), dtype=torch.float32)
    X_tr = text_to_vec(tr.data)
    y_tr = torch.tensor(tr.target, dtype=torch.long)
    X_te = text_to_vec(te.data)
    y_te = torch.tensor(te.target, dtype=torch.long)
    return X_tr, y_tr, X_te, y_te, embed_dim, 4, 'Text Embedding'


def load_timeseries():
    np.random.seed(42)
    n = 200
    length = 50
    # 3 classes: sine, square, sawtooth
    X, y = [], []
    for _ in range(n):
        t = np.linspace(0, 2*np.pi, length)
        X.append(np.sin(t) + np.random.randn(length)*0.1); y.append(0)
        X.append(np.sign(np.sin(t)) + np.random.randn(length)*0.1); y.append(1)
        X.append((t % (2*np.pi))/(2*np.pi)*2-1 + np.random.randn(length)*0.1); y.append(2)
    X = torch.tensor(np.array(X), dtype=torch.float32)
    y = torch.tensor(y, dtype=torch.long)
    split = int(0.8 * len(X))
    idx = torch.randperm(len(X))
    return X[idx[:split]], y[idx[:split]], X[idx[split:]], y[idx[split:]], length, 3, 'Time Series'


def load_audio():
    np.random.seed(42)
    sr, dur, n_per = 8000, 0.5, 100
    n_fft = 100
    X, y = [], []
    for _ in range(n_per):
        for cls, freq in enumerate([200, 500, 1000]):
            t = np.linspace(0, dur, int(sr*dur))
            sig = np.sin(2*np.pi*freq*t) + np.random.randn(len(t))*0.05
            fft = np.abs(np.fft.rfft(sig))[:n_fft]
            X.append(fft / (fft.max()+1e-8)); y.append(cls)
        # chord
        t = np.linspace(0, dur, int(sr*dur))
        sig = np.sin(2*np.pi*200*t) + np.sin(2*np.pi*500*t) + np.random.randn(len(t))*0.05
        fft = np.abs(np.fft.rfft(sig))[:n_fft]
        X.append(fft / (fft.max()+1e-8)); y.append(3)
        # noise
        sig = np.random.randn(int(sr*dur))
        fft = np.abs(np.fft.rfft(sig))[:n_fft]
        X.append(fft / (fft.max()+1e-8)); y.append(4)
    X = torch.tensor(np.array(X), dtype=torch.float32)
    y = torch.tensor(y, dtype=torch.long)
    split = int(0.8 * len(X))
    idx = torch.randperm(len(X))
    return X[idx[:split]], y[idx[:split]], X[idx[split:]], y[idx[split:]], n_fft, 5, 'Audio'


def _load_sklearn(loader_fn, name):
    from sklearn.preprocessing import StandardScaler
    data = loader_fn()
    X = StandardScaler().fit_transform(data.data)
    y = data.target
    X = torch.tensor(X, dtype=torch.float32)
    y = torch.tensor(y, dtype=torch.long)
    split = int(0.8 * len(X))
    idx = torch.randperm(len(X), generator=torch.Generator().manual_seed(42))
    return X[idx[:split]], y[idx[:split]], X[idx[split:]], y[idx[split:]], X.shape[1], len(set(y.numpy())), name

def load_iris():
    from sklearn.datasets import load_iris
    return _load_sklearn(load_iris, 'Tabular Iris')

def load_wine():
    from sklearn.datasets import load_wine
    return _load_sklearn(load_wine, 'Tabular Wine')

def load_cancer():
    from sklearn.datasets import load_breast_cancer
    return _load_sklearn(load_breast_cancer, 'Tabular Cancer')


def load_anomaly():
    """Returns accuracy-style metric: we'll use tension-based AUROC."""
    from sklearn.datasets import make_blobs
    np.random.seed(42)
    X_normal, _ = make_blobs(n_samples=500, n_features=20, centers=2, cluster_std=1.0)
    X_anomaly = np.random.uniform(-6, 6, size=(100, 20))
    X_all = np.vstack([X_normal, X_anomaly])
    y_all = np.array([0]*500 + [1]*100)
    X = torch.tensor(X_all, dtype=torch.float32)
    y = torch.tensor(y_all, dtype=torch.long)
    # Train on normal only, test on all
    X_tr = torch.tensor(X_normal[:400], dtype=torch.float32)
    y_tr = torch.zeros(400, dtype=torch.long)
    X_te = X
    y_te = y
    return X_tr, y_tr, X_te, y_te, 20, 2, 'Anomaly'


def load_numbers():
    np.random.seed(42)
    def is_prime(n):
        if n < 2: return False
        for i in range(2, int(n**0.5)+1):
            if n % i == 0: return False
        return True
    def count_div(n):
        return sum(1 for i in range(1, n+1) if n % i == 0) if n > 0 else 0

    fibs = set(); a,b = 1,1
    while a <= 1000: fibs.add(a); a,b = b,a+b
    pows2 = {2**i for i in range(11) if 2**i <= 1000}
    squares = {i*i for i in range(1, 32) if i*i <= 1000}

    X, y = [], []
    for n in range(1, 1001):
        feats = [n/1000, n%2, n%3, n%6, sum(int(d) for d in str(n))/27,
                 count_div(n)/30, int(n%2==0), (n%10)/9, math.log(max(n,1))/math.log(1000),
                 sum(d for d in range(1,n) if n%d==0)/max(n,1)]
        X.append(feats)
        if is_prime(n): y.append(0)
        elif n in squares: y.append(1)
        elif n in fibs: y.append(2)
        elif n in pows2: y.append(3)
        else: y.append(4)
    X = torch.tensor(X, dtype=torch.float32)
    y = torch.tensor(y, dtype=torch.long)
    split = 800
    return X[:split], y[:split], X[split:], y[split:], 10, 5, 'Number System'


def load_music():
    np.random.seed(42)
    sr, dur = 8000, 0.5
    n_fft = 100
    intervals = [(1,1), (16,15), (9,8), (6,5), (5,4), (4,3), (45,32), (3,2), (2,1)]
    X, y = [], []
    base = 200
    for _ in range(60):
        for cls, (p, q) in enumerate(intervals):
            t = np.linspace(0, dur, int(sr*dur))
            f2 = base * p / q
            sig = np.sin(2*np.pi*base*t) + np.sin(2*np.pi*f2*t) + np.random.randn(len(t))*0.02
            fft = np.abs(np.fft.rfft(sig))[:n_fft]
            X.append(fft / (fft.max()+1e-8)); y.append(cls)
    X = torch.tensor(np.array(X), dtype=torch.float32)
    y = torch.tensor(y, dtype=torch.long)
    split = int(0.8 * len(X))
    idx = torch.randperm(len(X))
    return X[idx[:split]], y[idx[:split]], X[idx[split:]], y[idx[split:]], n_fft, 9, 'Music Theory'


# ═══════════════════════════════════════════
# Training
# ═══════════════════════════════════════════

def train_eval(ModelCls, X_tr, y_tr, X_te, y_te, d_in, d_hid, d_out, epochs=20, lr=0.001, is_anomaly=False):
    torch.manual_seed(42)
    model = ModelCls(d_in, d_hid, d_out)
    opt = torch.optim.Adam(model.parameters(), lr=lr)
    crit = nn.CrossEntropyLoss()

    for _ in range(epochs):
        model.train()
        idx = torch.randperm(len(X_tr))
        for i in range(0, len(X_tr), 64):
            batch_x = X_tr[idx[i:i+64]]
            batch_y = y_tr[idx[i:i+64]]
            opt.zero_grad()
            out = model(batch_x)
            loss = crit(out, batch_y)
            loss.backward()
            opt.step()

    model.eval()
    with torch.no_grad():
        out = model(X_te)
        if is_anomaly and hasattr(model, 'a'):
            # For anomaly: use tension as score
            rep = model.a(X_te) - model.g(X_te) if hasattr(model, 'g') else out
            tension = rep.pow(2).mean(dim=-1)
            from sklearn.metrics import roc_auc_score
            try:
                auroc = roc_auc_score(y_te.numpy(), tension.numpy())
                return auroc
            except:
                return 0.5
        pred = out.argmax(dim=1)
        acc = (pred == y_te).float().mean().item()
    return acc


# ═══════════════════════════════════════════
# Main
# ═══════════════════════════════════════════

def main():
    print("=" * 75)
    print("  ALL 14 Data Types: Simplification Verification")
    print("  Dense vs Original(scale*sqrt*dir) vs Raw(A-G) vs Scaled(s*(A-G))")
    print("=" * 75)

    loaders = [
        (load_mnist, 64, 10),
        (load_cifar, 128, 15),
        (load_text_tfidf, 64, 15),
        (load_text_embedding, 64, 20),
        (load_timeseries, 32, 30),
        (load_audio, 32, 30),
        (load_iris, 16, 50),
        (load_wine, 16, 50),
        (load_cancer, 32, 50),
        (load_anomaly, 32, 30),
        (load_numbers, 32, 30),
        (load_music, 32, 30),
    ]

    models = {
        'Dense':       Dense,
        'Original':    Original,
        'Raw(A-G)':    RawAG,
        'Scaled(sAG)': ScaledAG,
    }

    all_results = []

    for loader_fn, d_hid, epochs in loaders:
        try:
            X_tr, y_tr, X_te, y_te, d_in, d_out, name = loader_fn()
        except Exception as e:
            print(f"  SKIP {loader_fn.__name__}: {e}")
            continue

        is_anom = 'Anomaly' in name
        print(f"\n  [{name}] d_in={d_in} d_out={d_out} train={len(X_tr)} test={len(X_te)}")

        row = {'name': name}
        for mname, MCls in models.items():
            # For anomaly with Dense, use reconstruction-based approach
            if is_anom and mname == 'Dense':
                # Dense can't do tension-based anomaly, use classification acc
                acc = train_eval(MCls, X_tr, y_tr, X_te, y_te, d_in, d_hid, d_out, epochs)
                row[mname] = acc
            elif is_anom:
                acc = train_eval(MCls, X_tr, y_tr, X_te, y_te, d_in, d_hid, d_out, epochs, is_anomaly=True)
                row[mname] = acc
            else:
                acc = train_eval(MCls, X_tr, y_tr, X_te, y_te, d_in, d_hid, d_out, epochs)
                row[mname] = acc
            print(f"    {mname:14s}: {acc*100:.2f}%")

        all_results.append(row)

    # ═══ Summary Table ═══
    print(f"\n{'=' * 75}")
    print(f"  SUMMARY: All Data Types")
    print(f"{'=' * 75}")
    print(f"\n  {'#':>2} {'Data Type':18s} | {'Dense':>8s} | {'Original':>8s} | {'Raw(A-G)':>8s} | {'Scaled':>8s} | {'Winner':12s} | {'A-G vs Orig':>10s}")
    print(f"  {'─'*2} {'─'*18}-+-{'─'*8}-+-{'─'*8}-+-{'─'*8}-+-{'─'*8}-+-{'─'*12}-+-{'─'*10}")

    ag_wins = 0
    orig_wins = 0
    for i, row in enumerate(all_results):
        name = row['name']
        vals = {k: row[k] for k in models}
        winner = max(vals, key=vals.get)
        delta = (row.get('Raw(A-G)', 0) - row.get('Original', 0)) * 100
        marker = '✅' if delta >= 0 else '❌'

        print(f"  {i+1:2d} {name:18s} |"
              f" {row.get('Dense',0)*100:6.2f}% |"
              f" {row.get('Original',0)*100:6.2f}% |"
              f" {row.get('Raw(A-G)',0)*100:6.2f}% |"
              f" {row.get('Scaled(sAG)',0)*100:6.2f}% |"
              f" {winner:12s} | {delta:+6.2f}% {marker}")

        if delta >= 0: ag_wins += 1
        else: orig_wins += 1

    print(f"\n  Raw(A-G) >= Original: {ag_wins}/{len(all_results)} datasets")
    print(f"  Original > Raw(A-G):  {orig_wins}/{len(all_results)} datasets")

    if ag_wins > orig_wins:
        print(f"\n  VERDICT: A-G is sufficient for MOST data types.")
        print(f"  scale*sqrt*dir adds value only on {orig_wins} datasets.")
    else:
        print(f"\n  VERDICT: scale*sqrt*dir helps on MOST data types.")
        print(f"  Keep Original formula, don't over-simplify.")

    # Category analysis
    print(f"\n  By data density:")
    dense_types = [r for r in all_results if any(k in r['name'] for k in ['MNIST','CIFAR','Embedding','series','Audio','Iris','Wine','Cancer','Number','Music'])]
    sparse_types = [r for r in all_results if 'TF-IDF' in r['name']]

    if dense_types:
        dense_ag = np.mean([(r.get('Raw(A-G)',0) - r.get('Original',0))*100 for r in dense_types])
        print(f"    Dense data:  Raw(A-G) vs Original avg delta = {dense_ag:+.2f}%")
    if sparse_types:
        sparse_ag = np.mean([(r.get('Raw(A-G)',0) - r.get('Original',0))*100 for r in sparse_types])
        print(f"    Sparse data: Raw(A-G) vs Original avg delta = {sparse_ag:+.2f}%")

    print(f"\n{'=' * 75}")


if __name__ == '__main__':
    main()
