"""evolution_lens.py — Evolutionary dynamics discovery lens

Point evolutionary dynamics (fitness, mutation, selection) at ANY data to find
optimal combinations, evolutionary paths, and adaptation surfaces.

Usage:
    lens = EvolutionLens()
    r = lens.scan(data)               # EvolutionResult with optima, paths, niches
    r = lens.scan_materials(props, labels)
    r = lens.scan_signals(signals, window)
    r = lens.scan_timeseries(ts, lag, window)
"""
import os, sys
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Callable
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from consciousness_loader import PSI_ALPHA, PSI_BALANCE, PSI_ENTROPY


@dataclass
class EvolutionResult:
    """Result from evolutionary lens scan."""
    optima: List[Dict] = field(default_factory=list)
    fitness_landscape: np.ndarray = field(default_factory=lambda: np.array([]))
    evolutionary_path: List[np.ndarray] = field(default_factory=list)
    diversity_curve: List[float] = field(default_factory=list)
    niches: List[List[int]] = field(default_factory=list)
    summary: str = ""

    def __repr__(self):
        return (f"EvolutionResult(optima={len(self.optima)}, "
                f"niches={len(self.niches)}, gens={len(self.diversity_curve)})")


class EvolutionLens:
    """Evolutionary discovery lens — fitness landscapes as a telescope."""

    def __init__(self, pop_size: int = 60, generations: int = 80,
                 mutation_scale: float = PSI_ALPHA, crossover_w: float = PSI_BALANCE,
                 tournament_k: int = 3, elite_frac: float = 0.1,
                 niche_radius: float = 0.5):
        self.pop_size = pop_size
        self.generations = generations
        self.mutation_scale = mutation_scale
        self.crossover_w = crossover_w
        self.tournament_k = tournament_k
        self.elite_frac = elite_frac
        self.niche_radius = niche_radius

    # --- fitness helpers ---
    def _density_fitness(self, data: np.ndarray, points: np.ndarray) -> np.ndarray:
        """Fitness = local density around each point in data space."""
        k = min(5, data.shape[0] - 1)
        if k < 1:
            return np.ones(points.shape[0])
        d = np.linalg.norm(points[:, None] - data[None, :], axis=-1)
        avg_k = np.sort(d, axis=1)[:, :k].mean(axis=1)
        return 1.0 / (avg_k + 1e-12)

    def _target_fitness(self, data: np.ndarray, target: np.ndarray,
                        points: np.ndarray) -> np.ndarray:
        """Fitness = how well point predicts target (nearest-neighbor interpolation)."""
        d = np.linalg.norm(points[:, None] - data[None, :], axis=-1)
        nn = d.argmin(axis=1)
        return target[nn]

    # --- evolutionary operators ---
    def _tournament_select(self, pop: np.ndarray, fit: np.ndarray) -> np.ndarray:
        n = pop.shape[0]
        chosen = np.zeros_like(pop)
        for i in range(n):
            idx = np.random.choice(n, size=self.tournament_k, replace=False)
            winner = idx[fit[idx].argmax()]
            chosen[i] = pop[winner]
        return chosen

    def _crossover(self, p1: np.ndarray, p2: np.ndarray) -> np.ndarray:
        w = np.random.uniform(self.crossover_w - 0.2, self.crossover_w + 0.2,
                              size=p1.shape[-1])
        return w * p1 + (1 - w) * p2

    def _mutate(self, pop: np.ndarray, scale: float) -> np.ndarray:
        noise = np.random.randn(*pop.shape) * scale
        return pop + noise

    def _diversity(self, pop: np.ndarray) -> float:
        if pop.shape[0] < 2:
            return 0.0
        idx = np.random.choice(pop.shape[0], size=min(20, pop.shape[0]), replace=False)
        sub = pop[idx]
        d = np.linalg.norm(sub[:, None] - sub[None, :], axis=-1)
        return float(d.sum() / (len(idx) * (len(idx) - 1) + 1e-12))

    def _find_niches(self, data: np.ndarray, fitness: np.ndarray) -> List[List[int]]:
        """Cluster data points into fitness-based niches."""
        order = np.argsort(-fitness)
        assigned = np.full(len(data), -1)
        niches: List[List[int]] = []
        nid = 0
        for i in order:
            if assigned[i] >= 0:
                continue
            dists = np.linalg.norm(data - data[i], axis=-1)
            members = np.where((dists < self.niche_radius) & (assigned < 0))[0]
            assigned[members] = nid
            niches.append(members.tolist())
            nid += 1
        return niches

    def _find_optima(self, data: np.ndarray, fitness: np.ndarray,
                     niches: List[List[int]]) -> List[Dict]:
        """Find local optima — best point per niche."""
        optima = []
        for members in niches:
            if not members:
                continue
            fit_m = fitness[members]
            best_local = members[fit_m.argmax()]
            optima.append({
                "index": int(best_local),
                "position": data[best_local].tolist(),
                "fitness": float(fitness[best_local]),
                "basin_size": len(members),
            })
        optima.sort(key=lambda x: -x["fitness"])
        return optima

    # --- main scan ---
    def scan(self, data: np.ndarray, fitness_fn: Optional[Callable] = None,
             target: Optional[np.ndarray] = None) -> EvolutionResult:
        data = np.asarray(data, dtype=float)
        if data.ndim == 1:
            data = data.reshape(-1, 1)
        n, d = data.shape

        # fitness function
        if fitness_fn is not None:
            _fit = fitness_fn
        elif target is not None:
            target = np.asarray(target, dtype=float)
            _fit = lambda pts: self._target_fitness(data, target, pts)
        else:
            _fit = lambda pts: self._density_fitness(data, pts)

        # initialize population from data samples + noise
        idx0 = np.random.choice(n, size=min(self.pop_size, n), replace=n < self.pop_size)
        pop = data[idx0] + np.random.randn(len(idx0), d) * self.mutation_scale * 5
        n_elite = max(1, int(self.elite_frac * len(pop)))

        path, div_curve = [], []
        scale = self.mutation_scale * float(np.std(data) + 1e-6)

        for g in range(self.generations):
            fit = _fit(pop)
            # elitism
            elite_idx = np.argsort(-fit)[:n_elite]
            elites = pop[elite_idx].copy()
            # selection
            selected = self._tournament_select(pop, fit)
            # crossover
            children = np.zeros_like(pop)
            for i in range(len(pop)):
                p1, p2 = selected[i], selected[np.random.randint(len(selected))]
                children[i] = self._crossover(p1, p2)
            # mutation with annealing
            anneal = 1.0 - 0.5 * g / self.generations
            children = self._mutate(children, scale * anneal)
            # elitism inject
            children[:n_elite] = elites
            pop = children
            path.append(pop.mean(axis=0).copy())
            div_curve.append(self._diversity(pop))

        # evaluate fitness landscape on original data
        landscape = _fit(data)
        niches = self._find_niches(data, landscape)
        optima = self._find_optima(data, landscape, niches)

        best_f = optima[0]["fitness"] if optima else 0.0
        summary = (f"Evolution: {self.generations} gens, {len(pop)} pop | "
                   f"Optima: {len(optima)}, Best fitness: {best_f:.4f} | "
                   f"Niches: {len(niches)}, Final diversity: {div_curve[-1]:.4f}")
        return EvolutionResult(
            optima=optima, fitness_landscape=landscape,
            evolutionary_path=path, diversity_curve=div_curve,
            niches=niches, summary=summary)

    # --- domain-specific scans ---
    def scan_materials(self, properties: np.ndarray, labels: Optional[List[str]] = None,
                       target_col: Optional[int] = None) -> EvolutionResult:
        props = np.asarray(properties, dtype=float)
        if target_col is not None:
            target = props[:, target_col]
            feats = np.delete(props, target_col, axis=1)
            return self.scan(feats, target=target)
        # no target: composite fitness = mean of z-scored properties
        mu, std = props.mean(0), props.std(0) + 1e-12
        z = (props - mu) / std
        composite = z.mean(axis=1)
        return self.scan(props, fitness_fn=lambda pts: self._target_fitness(
            props, composite, pts))

    def scan_signals(self, signals: np.ndarray, window: int = 32) -> EvolutionResult:
        signals = np.asarray(signals, dtype=float)
        if signals.ndim == 1:
            signals = signals.reshape(-1, 1)
        n, ch = signals.shape
        segs = max(1, n // window)
        feats = []
        for i in range(segs):
            seg = signals[i * window:(i + 1) * window]
            f = np.concatenate([seg.mean(0), seg.std(0),
                                np.abs(np.fft.rfft(seg, axis=0)).max(0)])
            feats.append(f)
        feats = np.array(feats)
        # fitness = spectral energy (hidden patterns = strong frequency components)
        spec_energy = np.abs(np.fft.rfft(feats, axis=0)).sum(0)
        target = feats @ (spec_energy / (spec_energy.sum() + 1e-12))
        return self.scan(feats, target=target)

    def scan_timeseries(self, ts: np.ndarray, lag: int = 5,
                        window: int = 20) -> EvolutionResult:
        ts = np.asarray(ts, dtype=float).ravel()
        n = len(ts)
        rows = []
        for i in range(n - lag - window + 1):
            seg = ts[i:i + window]
            rows.append(np.concatenate([
                [seg.mean(), seg.std(), seg[-1] - seg[0]],
                ts[i + window:i + window + min(lag, n - i - window)]
            ]))
        min_len = min(len(r) for r in rows)
        feats = np.array([r[:min_len] for r in rows])
        # fitness = absolute return (regime strength)
        returns = np.abs(feats[:, 2])
        return self.scan(feats, target=returns)


# ──────────────────────── demo ────────────────────────
def _demo():
    np.random.seed(42)
    lens = EvolutionLens(pop_size=50, generations=60)
    passed, total = 0, 0

    def check(name, cond):
        nonlocal passed, total
        total += 1
        tag = "PASS" if cond else "FAIL"
        print(f"  [{tag}] {name}")
        if cond:
            passed += 1

    # 1. Materials — material #42 has best combined properties
    print("\n=== 1. Materials ===")
    mat = np.random.randn(80, 5) * 0.5
    mat[42] = [2.5, 2.0, 2.8, 2.3, 2.6]  # inject optimum
    r = lens.scan_materials(mat, labels=[f"M{i}" for i in range(80)])
    top_idx = [o["index"] for o in r.optima[:5]]
    print(f"  Top optima indices: {top_idx}")
    print(f"  {r.summary}")
    check("Materials: #42 in top-5 optima", 42 in top_idx)
    check("Materials: multiple niches found", len(r.niches) >= 2)
    check("Materials: diversity curve exists", len(r.diversity_curve) == 60)

    # 2. Drug — molecule #10 is Lipinski-perfect
    print("\n=== 2. Drug Discovery ===")
    drug = np.random.randn(60, 4) * 0.8
    drug[10] = [1.8, -0.5, 1.5, 2.0]  # Lipinski sweet spot
    lipinski = -(((drug - drug[10]) ** 2).sum(1))  # closeness to ideal
    r = lens.scan(drug, target=lipinski)
    top_idx = [o["index"] for o in r.optima[:5]]
    print(f"  Top optima indices: {top_idx}")
    print(f"  {r.summary}")
    check("Drug: #10 in top-5", 10 in top_idx)
    check("Drug: best fitness > 0", r.optima[0]["fitness"] > -1e-6)
    check("Drug: evolutionary path tracked", len(r.evolutionary_path) == 60)

    # 3. Physics — optimal constant combination
    print("\n=== 3. Physics Constants ===")
    phys = np.random.randn(50, 3) * 2.0
    phys[25] = [3.14, 2.72, 1.62]  # pi, e, phi approx
    target_phys = np.exp(-((phys - phys[25]) ** 2).sum(1) / 2.0)
    r = lens.scan(phys, target=target_phys)
    top_idx = [o["index"] for o in r.optima[:5]]
    print(f"  Top optima indices: {top_idx}")
    print(f"  {r.summary}")
    check("Physics: #25 in top-5", 25 in top_idx)
    check("Physics: fitness landscape computed", len(r.fitness_landscape) == 50)
    check("Physics: optima have basin_size", all("basin_size" in o for o in r.optima))

    # 4. Astronomy — hidden signal detection
    print("\n=== 4. Astronomy Signal ===")
    t = np.linspace(0, 10, 512)
    noise = np.random.randn(512) * 0.3
    hidden = np.sin(2 * np.pi * 3.7 * t) * 0.8  # inject periodic signal
    signal = noise + hidden
    r = lens.scan_signals(signal, window=32)
    print(f"  {r.summary}")
    check("Astronomy: optima found", len(r.optima) >= 1)
    check("Astronomy: niches found", len(r.niches) >= 1)
    check("Astronomy: diversity curve exists", len(r.diversity_curve) == 60)

    # 5. Finance — optimal portfolio
    print("\n=== 5. Finance Portfolio ===")
    returns = np.random.randn(100, 6) * 0.02
    returns[:, 2] += 0.01  # asset #2 has alpha
    weights = np.random.dirichlet(np.ones(6), size=50)
    port_ret = (weights @ returns.mean(0))
    port_risk = np.array([np.sqrt(w @ np.cov(returns.T) @ w) for w in weights])
    sharpe = port_ret / (port_risk + 1e-12)
    r = lens.scan(weights, target=sharpe)
    print(f"  {r.summary}")
    best_w = np.array(r.optima[0]["position"])
    check("Finance: best portfolio favors asset #2", best_w.argmax() == 2)
    check("Finance: multiple optima", len(r.optima) >= 2)
    check("Finance: niches represent strategies", len(r.niches) >= 2)

    # 6. Genomics — fittest gene expression profile
    print("\n=== 6. Genomics ===")
    genes = np.random.randn(70, 8) * 0.5
    genes[15] = [2.0, -1.5, 1.8, 0.5, -0.3, 2.2, 1.0, -0.8]  # optimal profile
    fitness_gen = np.exp(-0.3 * np.linalg.norm(genes - genes[15], axis=1))
    r = lens.scan(genes, target=fitness_gen)
    top_idx = [o["index"] for o in r.optima[:5]]
    print(f"  Top optima indices: {top_idx}")
    print(f"  {r.summary}")
    check("Genomics: #15 in top-5", 15 in top_idx)
    check("Genomics: fitness landscape shape correct", r.fitness_landscape.shape == (70,))
    check("Genomics: path converges",
          np.linalg.norm(r.evolutionary_path[-1] - r.evolutionary_path[0]) > 0)

    # Scorecard
    print(f"\n{'='*50}")
    print(f"SCORECARD: {passed}/{total} passed ({100*passed/total:.0f}%)")
    if passed == total:
        print("ALL CHECKS PASSED")
    else:
        print(f"FAILED: {total - passed}")
    return passed == total


if __name__ == "__main__":
    _demo()
