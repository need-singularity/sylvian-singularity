"""causal_lens.py — Causal discovery lens (화살표)

Use an arrow as a telescope: detect causal directions, information flow,
Granger causality, and temporal precedence in ANY data.

How it works:
  1. Granger causality: does past of X improve prediction of Y?
  2. Transfer entropy: directed information flow X→Y vs Y→X
  3. Lag correlation: time-shifted cross-correlations
  4. Conditional independence: X⊥Y|Z tests via partial correlation
  5. Causal graph reconstruction via PC-like algorithm

Works with numpy + scipy. Portable across all projects.

Usage:
    from causal_lens import CausalLens

    lens = CausalLens()
    r = lens.scan(data)
    print(r.causal_pairs)          # directed X→Y pairs
    print(r.transfer_entropy)      # TE matrix
    print(r.lag_correlations)      # optimal lag per pair
"""
import os, sys, math
from dataclasses import dataclass, field
from typing import List, Tuple, Dict, Any
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from consciousness_loader import PSI_ALPHA, PSI_BALANCE, PSI_ENTROPY


@dataclass
class CausalPair:
    """A detected causal relationship."""
    cause: int
    effect: int
    strength: float      # 0~1
    lag: int             # optimal lag
    method: str          # "granger", "transfer_entropy", "lag_corr"
    description: str = ""


@dataclass
class CausalResult:
    """Result from causal (arrow) lens scan."""
    causal_pairs: List[CausalPair] = field(default_factory=list)
    granger_matrix: np.ndarray = field(default_factory=lambda: np.array([]))
    transfer_entropy_matrix: np.ndarray = field(default_factory=lambda: np.array([]))
    lag_matrix: np.ndarray = field(default_factory=lambda: np.array([]))
    partial_correlations: np.ndarray = field(default_factory=lambda: np.array([]))
    causal_graph: Dict[int, List[int]] = field(default_factory=dict)
    summary: str = ""

    def __repr__(self):
        return (f"CausalResult(pairs={len(self.causal_pairs)}, "
                f"graph_edges={sum(len(v) for v in self.causal_graph.values())})")


class CausalLens:
    """Causal discovery lens — arrow as telescope."""

    def __init__(self, max_lag: int = 5, significance: float = 0.05,
                 te_bins: int = 16, min_strength: float = 0.1):
        self.max_lag = max_lag
        self.sig = significance
        self.te_bins = te_bins
        self.min_strength = min_strength

    def _granger_causality(self, x, y, max_lag):
        """Simple Granger causality test: does past x help predict y?"""
        n = len(y)
        if n < max_lag + 5:
            return 0.0, 0

        best_score = 0.0
        best_lag = 1

        for lag in range(1, max_lag + 1):
            # Restricted model: y[t] ~ y[t-1], ..., y[t-lag]
            Y = y[lag:]
            n_eff = len(Y)
            X_r = np.column_stack([y[lag-k:n-k] for k in range(1, lag + 1)])

            # Unrestricted model: y[t] ~ y[t-1],...,y[t-lag], x[t-1],...,x[t-lag]
            X_u = np.column_stack([X_r] + [x[lag-k:n-k] for k in range(1, lag + 1)])

            # Fit both models
            try:
                # Restricted RSS
                beta_r = np.linalg.lstsq(X_r, Y, rcond=None)[0]
                rss_r = float(np.sum((Y - X_r @ beta_r) ** 2))

                # Unrestricted RSS
                beta_u = np.linalg.lstsq(X_u, Y, rcond=None)[0]
                rss_u = float(np.sum((Y - X_u @ beta_u) ** 2))
            except np.linalg.LinAlgError:
                continue

            if rss_r < 1e-30:
                continue

            # F-statistic-inspired score (normalized)
            improvement = (rss_r - rss_u) / rss_r
            if improvement > best_score:
                best_score = improvement
                best_lag = lag

        return best_score, best_lag

    def _transfer_entropy(self, x, y, lag=1):
        """Estimate transfer entropy from x to y."""
        n = len(x)
        if n < lag + 10:
            return 0.0

        # Discretize
        def digitize(v):
            lo, hi = v.min(), v.max()
            if hi - lo < 1e-30:
                return np.zeros(len(v), dtype=int)
            edges = np.linspace(lo, hi, self.te_bins + 1)
            return np.clip(np.digitize(v, edges[1:-1]), 0, self.te_bins - 1)

        dx = digitize(x)
        dy = digitize(y)

        # TE = H(Y_t | Y_{t-lag}) - H(Y_t | Y_{t-lag}, X_{t-lag})
        yt = dy[lag:]
        yt_past = dy[:-lag]
        xt_past = dx[:-lag]
        m = len(yt)

        # Joint counts
        def entropy_cond(a, b):
            """H(a|b) = H(a,b) - H(b)"""
            joint = a * (self.te_bins + 1) + b
            # H(joint)
            counts_j = np.bincount(joint)
            p_j = counts_j[counts_j > 0] / m
            h_joint = -np.sum(p_j * np.log2(p_j + 1e-30))
            # H(b)
            counts_b = np.bincount(b)
            p_b = counts_b[counts_b > 0] / m
            h_b = -np.sum(p_b * np.log2(p_b + 1e-30))
            return h_joint - h_b

        h_yt_given_past = entropy_cond(yt, yt_past)

        # H(Y_t | Y_{t-lag}, X_{t-lag})
        combined_past = yt_past * (self.te_bins + 1) + xt_past
        h_yt_given_both = entropy_cond(yt, combined_past)

        te = max(0.0, h_yt_given_past - h_yt_given_both)
        return te

    def _lag_correlation(self, x, y, max_lag):
        """Find optimal lag and correlation between x and y."""
        n = min(len(x), len(y))
        if n < max_lag + 5:
            return 0.0, 0

        best_corr = 0.0
        best_lag = 0

        for lag in range(-max_lag, max_lag + 1):
            if lag > 0:
                a, b = x[:n-lag], y[lag:n]
            elif lag < 0:
                a, b = x[-lag:n], y[:n+lag]
            else:
                a, b = x[:n], y[:n]

            if len(a) < 5:
                continue
            c = np.corrcoef(a, b)[0, 1]
            if np.isfinite(c) and abs(c) > abs(best_corr):
                best_corr = float(c)
                best_lag = lag

        return best_corr, best_lag

    def _partial_correlation(self, data):
        """Compute partial correlation matrix."""
        d = data.shape[1]
        corr = np.corrcoef(data.T)
        # Fix any NaN
        corr = np.nan_to_num(corr, nan=0.0)

        try:
            # Partial correlation via precision matrix
            prec = np.linalg.inv(corr + np.eye(d) * 1e-6)
            diag = np.sqrt(np.abs(np.diag(prec)))
            diag[diag < 1e-30] = 1e-30
            pcorr = -prec / np.outer(diag, diag)
            np.fill_diagonal(pcorr, 1.0)
        except np.linalg.LinAlgError:
            pcorr = corr

        return pcorr

    def _build_causal_graph(self, granger, te, d):
        """Build causal graph from Granger + TE evidence."""
        graph = {i: [] for i in range(d)}
        for i in range(d):
            for j in range(d):
                if i == j:
                    continue
                # Both Granger and TE agree on direction
                g_ij = granger[i, j]
                g_ji = granger[j, i]
                te_ij = te[i, j]
                te_ji = te[j, i]

                if (g_ij > self.min_strength and g_ij > g_ji and
                        te_ij > te_ji):
                    graph[i].append(j)
        return graph

    def scan(self, data, verbose=True):
        data = np.asarray(data, dtype=np.float64)
        if data.ndim == 1:
            data = data.reshape(-1, 1)
        n, d = data.shape

        # Granger causality matrix
        granger = np.zeros((d, d))
        lag_mat = np.zeros((d, d), dtype=int)
        for i in range(d):
            for j in range(d):
                if i != j:
                    score, lag = self._granger_causality(data[:, i], data[:, j], self.max_lag)
                    granger[i, j] = score
                    lag_mat[i, j] = lag

        # Transfer entropy matrix
        te = np.zeros((d, d))
        for i in range(d):
            for j in range(d):
                if i != j:
                    te[i, j] = self._transfer_entropy(data[:, i], data[:, j])

        # Lag correlation matrix
        lag_corr = np.zeros((d, d))
        lag_optimal = np.zeros((d, d), dtype=int)
        for i in range(d):
            for j in range(i + 1, d):
                corr, lag = self._lag_correlation(data[:, i], data[:, j], self.max_lag)
                lag_corr[i, j] = lag_corr[j, i] = corr
                lag_optimal[i, j] = lag
                lag_optimal[j, i] = -lag

        # Partial correlations
        pcorr = self._partial_correlation(data) if d > 2 else np.corrcoef(data.T)

        # Build causal graph
        graph = self._build_causal_graph(granger, te, d)

        # Collect significant causal pairs
        pairs = []
        for i in range(d):
            for j in graph[i]:
                strength = (granger[i, j] + te[i, j]) / 2
                pairs.append(CausalPair(
                    cause=i, effect=j, strength=strength,
                    lag=int(lag_mat[i, j]), method="granger+te",
                    description=f"f{i}→f{j} (strength={strength:.3f}, lag={lag_mat[i,j]})"))

        # Also add strong lag-correlation pairs not in graph
        for i in range(d):
            for j in range(i + 1, d):
                if abs(lag_corr[i, j]) > 0.5 and lag_optimal[i, j] != 0:
                    cause = i if lag_optimal[i, j] > 0 else j
                    effect = j if lag_optimal[i, j] > 0 else i
                    if not any(p.cause == cause and p.effect == effect for p in pairs):
                        pairs.append(CausalPair(
                            cause=cause, effect=effect,
                            strength=abs(float(lag_corr[i, j])),
                            lag=abs(int(lag_optimal[i, j])),
                            method="lag_corr",
                            description=f"f{cause}→f{effect} (corr={lag_corr[i,j]:.3f}, lag={abs(lag_optimal[i,j])})"))

        pairs.sort(key=lambda x: -x.strength)

        n_edges = sum(len(v) for v in graph.values())
        summary = (f"Features: {d}, Samples: {n}, "
                   f"Causal pairs: {len(pairs)}, "
                   f"Graph edges: {n_edges}, "
                   f"Avg Granger: {granger[granger > 0].mean():.3f}" if granger[granger > 0].size > 0 else
                   f"Features: {d}, Samples: {n}, "
                   f"Causal pairs: {len(pairs)}, "
                   f"Graph edges: {n_edges}")

        return CausalResult(
            causal_pairs=pairs,
            granger_matrix=granger,
            transfer_entropy_matrix=te,
            lag_matrix=lag_optimal,
            partial_correlations=pcorr,
            causal_graph=graph,
            summary=summary)

    def scan_materials(self, properties, labels=None):
        r = self.scan(properties, verbose=False)
        parts = [r.summary]
        if r.causal_pairs:
            parts.append("Causal: " + ", ".join(p.description for p in r.causal_pairs[:5]))
        r.summary = "\n".join(parts)
        return r

    def scan_signals(self, signals, window=256):
        signals = np.atleast_2d(np.asarray(signals, dtype=np.float64))
        nch, ns = signals.shape
        # Treat channels as features, time as samples
        if nch <= ns:
            data = signals.T  # (time, channels)
        else:
            data = signals
        r = self.scan(data, verbose=False)
        r.summary += f"\nSignal: {nch}ch x {ns} samples"
        return r

    def scan_timeseries(self, ts, lag=None, window=None):
        ts = np.asarray(ts, dtype=np.float64)
        if ts.ndim == 1:
            ts = ts.reshape(-1, 1)
        if lag is not None:
            self.max_lag = lag
        r = self.scan(ts, verbose=False)
        r.summary += f"\nTimeseries: {ts.shape[0]} steps, {ts.shape[1]} vars"
        return r


# ---------------------------------------------------------------------------
if __name__ == '__main__':
    print("=" * 60)
    print("  Causal Lens (화살표) -- Causal Discovery Demo")
    print("=" * 60)
    np.random.seed(42)
    lens = CausalLens()

    # Demo 1: Clear causal chain A→B→C
    print("\n--- Demo 1: A→B→C causal chain ---")
    n = 200
    A = np.random.randn(n)
    B = np.zeros(n)
    C = np.zeros(n)
    for t in range(2, n):
        B[t] = 0.7 * A[t-1] + 0.3 * np.random.randn()
        C[t] = 0.6 * B[t-1] + 0.4 * np.random.randn()
    data = np.column_stack([A, B, C])
    r = lens.scan(data)
    print(r.summary)
    for p in r.causal_pairs:
        print(f"  {p.description}")
    print(f"  Graph: {r.causal_graph}")

    # Demo 2: Bidirectional (feedback loop)
    print("\n--- Demo 2: Feedback loop X↔Y ---")
    X = np.zeros(n)
    Y = np.zeros(n)
    X[0] = Y[0] = np.random.randn()
    for t in range(1, n):
        X[t] = 0.5 * Y[t-1] + 0.5 * np.random.randn()
        Y[t] = 0.4 * X[t-1] + 0.6 * np.random.randn()
    data2 = np.column_stack([X, Y])
    r = lens.scan(data2)
    print(r.summary)
    for p in r.causal_pairs:
        print(f"  {p.description}")

    # Demo 3: No causality (independent)
    print("\n--- Demo 3: Independent signals ---")
    data3 = np.random.randn(200, 4)
    r = lens.scan(data3)
    print(r.summary)
    print(f"  Causal pairs: {len(r.causal_pairs)} (should be ~0)")

    # Demo 4: Lagged correlation
    print("\n--- Demo 4: Signal with lag-3 copy ---")
    sig = np.random.randn(200)
    lagged = np.zeros(200)
    lagged[3:] = sig[:-3] * 0.9 + np.random.randn(197) * 0.1
    data4 = np.column_stack([sig, lagged])
    r = lens.scan(data4)
    print(r.summary)
    for p in r.causal_pairs:
        print(f"  {p.description}")
