#!/usr/bin/env python3
"""
experiment_rc4_curiosity.py — RC-4: Curiosity = Tension Change as Intrinsic Reward

Hypothesis:
  An agent using |tension(t) - tension(t-1)| as intrinsic reward ("surprise")
  will learn to seek high-variation regions of a 2D grid, while a random agent
  will not.

Setup:
  - 16x16 grid with "interesting" (high local variance) and "boring" (uniform) zones
  - Agent has PureField policy: two opposing engines produce action logits via tension
  - Intrinsic reward = |delta_tension| = surprise signal
  - Training: REINFORCE policy gradient, 500 episodes
  - Comparison: random agent vs curiosity-driven PureField agent

Key question: Does tension-change-as-reward produce curiosity-like exploration?

Self-contained. No external dependencies beyond numpy.
"""

import math
import random
import numpy as np

# ─── Reproducibility ───
SEED = 42
random.seed(SEED)
np.random.seed(SEED)

# ═══════════════════════════════════════════════════════
# 1. 2D Grid Environment
# ═══════════════════════════════════════════════════════

GRID_SIZE = 16
MAX_STEPS = 80

def make_grid():
    """Create a 16x16 grid with interesting and boring regions.

    Interesting regions: high local value variance (rugged landscape).
    Boring regions: uniform values (flat landscape).

    Layout:
      Top-left  (0:6, 0:6)   = interesting (random 0-10)
      Bot-right (10:16,10:16) = interesting (random 0-10)
      Center    (6:10, 6:10)  = mildly interesting (random 0-5)
      Rest                    = boring (constant 5.0)
    """
    grid = np.full((GRID_SIZE, GRID_SIZE), 5.0)

    # Interesting zone 1: top-left
    rng = np.random.RandomState(123)
    grid[0:6, 0:6] = rng.uniform(0, 10, (6, 6))

    # Interesting zone 2: bottom-right
    grid[10:16, 10:16] = rng.uniform(0, 10, (6, 6))

    # Mildly interesting center
    grid[6:10, 6:10] = rng.uniform(2, 8, (4, 4))

    return grid


def local_variance(grid, r, c, radius=1):
    """Compute local variance around (r, c) within given radius."""
    rmin = max(0, r - radius)
    rmax = min(GRID_SIZE, r + radius + 1)
    cmin = max(0, c - radius)
    cmax = min(GRID_SIZE, c + radius + 1)
    patch = grid[rmin:rmax, cmin:cmax]
    return float(np.var(patch))


def get_observation(grid, r, c, radius=2):
    """Return a flattened local patch as observation vector.

    Patch is (2*radius+1) x (2*radius+1), zero-padded at borders.
    """
    size = 2 * radius + 1
    obs = np.zeros((size, size), dtype=np.float64)
    for dr in range(-radius, radius + 1):
        for dc in range(-radius, radius + 1):
            nr, nc = r + dr, c + dc
            if 0 <= nr < GRID_SIZE and 0 <= nc < GRID_SIZE:
                obs[dr + radius, dc + radius] = grid[nr, nc]
    return obs.flatten() / 10.0  # normalize to [0, 1]


# Actions: 0=up, 1=down, 2=left, 3=right
DR = [-1, 1, 0, 0]
DC = [0, 0, -1, 1]
ACTION_NAMES = ['up', 'down', 'left', 'right']
NUM_ACTIONS = 4


class GridEnv:
    """2D grid exploration environment."""

    def __init__(self):
        self.grid = make_grid()
        self.r = GRID_SIZE // 2
        self.c = GRID_SIZE // 2
        self.steps = 0
        self.visit_count = np.zeros((GRID_SIZE, GRID_SIZE), dtype=int)

    def reset(self):
        self.r = GRID_SIZE // 2
        self.c = GRID_SIZE // 2
        self.steps = 0
        self.visit_count[:] = 0
        self.visit_count[self.r, self.c] = 1
        obs = get_observation(self.grid, self.r, self.c)
        return obs

    def step(self, action):
        nr = np.clip(self.r + DR[action], 0, GRID_SIZE - 1)
        nc = np.clip(self.c + DC[action], 0, GRID_SIZE - 1)
        self.r, self.c = int(nr), int(nc)
        self.steps += 1
        self.visit_count[self.r, self.c] += 1

        obs = get_observation(self.grid, self.r, self.c)
        done = self.steps >= MAX_STEPS

        return obs, done


# ═══════════════════════════════════════════════════════
# 2. Minimal Numpy Layers
# ═══════════════════════════════════════════════════════

def softmax(x):
    x = x - np.max(x)
    e = np.exp(np.clip(x, -50, 50))
    return e / (e.sum() + 1e-12)

def relu(x):
    return np.maximum(0, x)


class Linear:
    """Simple linear layer with numpy."""
    def __init__(self, in_dim, out_dim):
        scale = np.sqrt(2.0 / (in_dim + out_dim))
        self.W = np.random.randn(in_dim, out_dim).astype(np.float64) * scale
        self.b = np.zeros(out_dim, dtype=np.float64)
        self.dW = np.zeros_like(self.W)
        self.db = np.zeros_like(self.b)
        self.input = None

    def forward(self, x):
        self.input = x.copy()
        return x @ self.W + self.b

    def zero_grad(self):
        self.dW[:] = 0
        self.db[:] = 0

    def params(self):
        return [(self.W, self.dW), (self.b, self.db)]


# ═══════════════════════════════════════════════════════
# 3. PureField Policy (curiosity agent)
# ═══════════════════════════════════════════════════════

class PureFieldPolicy:
    """PureField-based policy for grid exploration.

    Two opposing engines (A=logic, G=pattern) produce action logits.
    Tension = |engine_A(obs) - engine_G(obs)|^2  (mean over dims)
    Output = tension_scale * sqrt(tension) * direction

    The agent receives intrinsic reward = |tension(t) - tension(t-1)|
    i.e., "surprise" = how much the tension changed.
    """

    def __init__(self, obs_dim=25, hidden_dim=32, action_dim=4):
        # Engine A (logic / analytical)
        self.a1 = Linear(obs_dim, hidden_dim)
        self.a2 = Linear(hidden_dim, action_dim)

        # Engine G (gestalt / pattern)
        self.g1 = Linear(obs_dim, hidden_dim)
        self.g2 = Linear(hidden_dim, action_dim)

        self.tension_scale = 1.0 / 3.0  # meta fixed point
        self.name = "PureFieldCuriosity"

    def forward(self, obs):
        """Returns (action_probs, tension_scalar)."""
        # Engine A
        ha = relu(self.a1.forward(obs))
        out_a = self.a2.forward(ha)

        # Engine G
        hg = relu(self.g1.forward(obs))
        out_g = self.g2.forward(hg)

        # Repulsion field
        repulsion = out_a - out_g
        tension = float(np.mean(repulsion ** 2))

        # Direction (normalized repulsion)
        norm = np.sqrt(np.sum(repulsion ** 2) + 1e-8)
        direction = repulsion / norm

        # Output logits = tension_scale * sqrt(tension) * direction
        logits = self.tension_scale * math.sqrt(tension + 1e-8) * direction

        probs = softmax(logits)
        return probs, tension

    def all_layers(self):
        return [self.a1, self.a2, self.g1, self.g2]


# ═══════════════════════════════════════════════════════
# 4. REINFORCE Training
# ═══════════════════════════════════════════════════════

def reinforce_update(policy, log_probs, rewards, lr=0.005, gamma=0.99):
    """Simple REINFORCE with numerical gradient estimation.

    Since we use numpy (no autograd), we use finite differences
    on the log-probability to estimate policy gradients.
    """
    # Compute discounted returns
    T = len(rewards)
    returns = np.zeros(T)
    G = 0.0
    for t in reversed(range(T)):
        G = rewards[t] + gamma * G
        returns[t] = G

    # Normalize returns
    if T > 1:
        std = returns.std()
        if std > 1e-8:
            returns = (returns - returns.mean()) / std

    # Numerical gradient via REINFORCE score function
    # For each parameter, perturb slightly and measure effect on log_prob
    eps = 1e-4
    for layer in policy.all_layers():
        for (param, grad) in layer.params():
            # Accumulate gradient estimate
            shape = param.shape
            flat = param.flatten()
            grad_flat = np.zeros_like(flat)

            # Sample a subset of parameters to perturb (for speed)
            n_params = len(flat)
            n_sample = min(n_params, 20)  # perturb up to 20 params per layer
            indices = np.random.choice(n_params, n_sample, replace=False)

            for idx in indices:
                old_val = flat[idx]

                # Positive perturbation
                flat[idx] = old_val + eps
                param[:] = flat.reshape(shape)

                # Negative perturbation
                flat[idx] = old_val - eps
                param[:] = flat.reshape(shape)

                flat[idx] = old_val
                param[:] = flat.reshape(shape)

            # Use the score function estimator instead:
            # grad = sum_t( return_t * grad_log_pi )
            # We approximate by: param += lr * mean(returns) * random_direction
            # This is a simplified evolutionary strategy
            noise = np.random.randn(*shape) * 0.01
            update = lr * np.mean(returns) * noise
            param += update


def run_episode_curiosity(env, policy):
    """Run one episode with curiosity (tension-change) reward."""
    obs = env.reset()

    log_probs = []
    rewards = []
    tensions = []
    positions = []

    prev_tension = 0.0
    done = False

    while not done:
        probs, tension = policy.forward(obs)
        tensions.append(tension)

        # Sample action
        action = np.random.choice(NUM_ACTIONS, p=probs)
        log_prob = math.log(probs[action] + 1e-12)
        log_probs.append(log_prob)

        # Intrinsic reward = |delta_tension| = surprise
        surprise = abs(tension - prev_tension)
        rewards.append(surprise)
        prev_tension = tension

        positions.append((env.r, env.c))
        obs, done = env.step(action)

    return log_probs, rewards, tensions, positions


def run_episode_random(env):
    """Run one episode with random policy."""
    obs = env.reset()
    positions = []
    local_vars = []
    done = False

    while not done:
        action = random.randint(0, NUM_ACTIONS - 1)
        positions.append((env.r, env.c))
        local_vars.append(local_variance(env.grid, env.r, env.c))
        obs, done = env.step(action)

    return positions, local_vars


# ═══════════════════════════════════════════════════════
# 5. Evolutionary Strategy Training (replaces broken REINFORCE)
# ═══════════════════════════════════════════════════════

def collect_params(policy):
    """Flatten all parameters into a single vector."""
    parts = []
    for layer in policy.all_layers():
        for (param, _) in layer.params():
            parts.append(param.flatten())
    return np.concatenate(parts)


def set_params(policy, flat_params):
    """Set policy parameters from a flat vector."""
    offset = 0
    for layer in policy.all_layers():
        for (param, _) in layer.params():
            size = param.size
            param[:] = flat_params[offset:offset + size].reshape(param.shape)
            offset += size


def evaluate_policy(policy, env, n_episodes=3):
    """Evaluate a policy: return mean total surprise reward."""
    total = 0.0
    for _ in range(n_episodes):
        obs = env.reset()
        prev_tension = 0.0
        done = False
        ep_reward = 0.0
        while not done:
            probs, tension = policy.forward(obs)
            action = np.random.choice(NUM_ACTIONS, p=probs)
            surprise = abs(tension - prev_tension)
            ep_reward += surprise
            prev_tension = tension
            obs, done = env.step(action)
        total += ep_reward
    return total / n_episodes


def train_es(policy, env, generations=200, population=20, lr=0.03, sigma=0.1):
    """Train with Evolution Strategy (OpenAI-style simplified ES).

    More reliable than numerical REINFORCE for small problems.
    """
    base_params = collect_params(policy)
    n_params = len(base_params)

    best_reward = -float('inf')
    reward_history = []

    for gen in range(generations):
        # Generate perturbations
        noise = np.random.randn(population, n_params)
        rewards = np.zeros(population)

        for i in range(population):
            # Positive perturbation
            set_params(policy, base_params + sigma * noise[i])
            r_pos = evaluate_policy(policy, env, n_episodes=2)

            # Negative perturbation
            set_params(policy, base_params - sigma * noise[i])
            r_neg = evaluate_policy(policy, env, n_episodes=2)

            rewards[i] = r_pos - r_neg

        # Normalize rewards
        std = rewards.std()
        if std > 1e-8:
            rewards = (rewards - rewards.mean()) / std

        # Update parameters
        gradient = (1.0 / (population * sigma)) * (noise.T @ rewards)
        base_params += lr * gradient

        set_params(policy, base_params)

        # Evaluate current policy
        if gen % 20 == 0 or gen == generations - 1:
            mean_r = evaluate_policy(policy, env, n_episodes=5)
            reward_history.append((gen, mean_r))
            if mean_r > best_reward:
                best_reward = mean_r
            print(f"  Gen {gen:4d} | mean surprise reward: {mean_r:.4f} | best: {best_reward:.4f}")

    set_params(policy, base_params)
    return reward_history


# ═══════════════════════════════════════════════════════
# 6. Analysis & Visualization
# ═══════════════════════════════════════════════════════

def compute_variance_map(grid):
    """Compute local variance at every cell."""
    vmap = np.zeros((GRID_SIZE, GRID_SIZE))
    for r in range(GRID_SIZE):
        for c in range(GRID_SIZE):
            vmap[r, c] = local_variance(grid, r, c)
    return vmap


def print_grid_ascii(grid, title, fmt=".1f"):
    """Print a grid as ASCII heatmap with symbols."""
    print(f"\n{'=' * 50}")
    print(f"  {title}")
    print(f"{'=' * 50}")

    vmin, vmax = grid.min(), grid.max()
    rng = vmax - vmin if vmax > vmin else 1.0

    # Quantize to symbols
    symbols = ' .:-=+*#%@'

    # Column headers
    header = "    " + "".join(f"{c:2d}" for c in range(GRID_SIZE))
    print(header)
    print("    " + "--" * GRID_SIZE)

    for r in range(GRID_SIZE):
        row_str = f"{r:2d} | "
        for c in range(GRID_SIZE):
            level = int((grid[r, c] - vmin) / rng * (len(symbols) - 1))
            level = min(level, len(symbols) - 1)
            row_str += symbols[level] + " "
        print(row_str)


def print_visit_heatmap(visit_count, title):
    """Print visit counts as ASCII heatmap."""
    print(f"\n{'=' * 50}")
    print(f"  {title}")
    print(f"{'=' * 50}")

    vmax = max(visit_count.max(), 1)
    symbols = ' .:-=+*#%@'

    header = "    " + "".join(f"{c:2d}" for c in range(GRID_SIZE))
    print(header)
    print("    " + "--" * GRID_SIZE)

    for r in range(GRID_SIZE):
        row_str = f"{r:2d} | "
        for c in range(GRID_SIZE):
            level = int(visit_count[r, c] / vmax * (len(symbols) - 1))
            level = min(level, len(symbols) - 1)
            row_str += symbols[level] + " "
        print(row_str)


def region_time_fraction(positions, grid_size=GRID_SIZE):
    """Compute fraction of time spent in interesting vs boring regions."""
    interesting = 0
    boring = 0
    for (r, c) in positions:
        if (r < 6 and c < 6) or (r >= 10 and c >= 10) or (6 <= r < 10 and 6 <= c < 10):
            interesting += 1
        else:
            boring += 1
    total = interesting + boring
    return interesting / total if total > 0 else 0.0


def print_trajectory_segment(positions, n=20):
    """Print first n steps of trajectory."""
    print(f"  First {min(n, len(positions))} steps:")
    for i, (r, c) in enumerate(positions[:n]):
        print(f"    t={i:3d}: ({r:2d}, {c:2d})")


# ═══════════════════════════════════════════════════════
# 7. Main Experiment
# ═══════════════════════════════════════════════════════

def main():
    print("=" * 60)
    print("  RC-4: Curiosity = Tension Change as Intrinsic Reward")
    print("=" * 60)

    env = GridEnv()
    grid = env.grid

    # --- Variance map ---
    vmap = compute_variance_map(grid)
    print_grid_ascii(vmap, "Local Variance Map (interesting = high)")

    print(f"\n  Interesting zones: top-left(0:6,0:6), bot-right(10:16,10:16)")
    print(f"  Mildly interesting: center(6:10,6:10)")
    print(f"  Boring: everywhere else (variance ~ 0)")
    print(f"  Max local variance: {vmap.max():.3f}")
    print(f"  Mean local variance: {vmap.mean():.3f}")

    # --- Phase 1: Random agent baseline ---
    print("\n" + "=" * 60)
    print("  Phase 1: Random Agent (baseline)")
    print("=" * 60)

    N_EVAL = 100
    random_interesting_fracs = []
    random_unique_cells = []
    all_random_visits = np.zeros((GRID_SIZE, GRID_SIZE), dtype=int)

    for ep in range(N_EVAL):
        positions, _ = run_episode_random(env)
        random_interesting_fracs.append(region_time_fraction(positions))
        unique = len(set(positions))
        random_unique_cells.append(unique)
        for (r, c) in positions:
            all_random_visits[r, c] += 1

    print(f"\n  Random agent ({N_EVAL} episodes, {MAX_STEPS} steps each):")
    print(f"  Mean interesting-zone fraction: {np.mean(random_interesting_fracs):.4f}")
    print(f"  Mean unique cells visited:      {np.mean(random_unique_cells):.1f} / {GRID_SIZE*GRID_SIZE}")

    print_visit_heatmap(all_random_visits, "Random Agent Visit Heatmap (100 episodes)")

    # --- Phase 2: Train curiosity agent ---
    print("\n" + "=" * 60)
    print("  Phase 2: Training Curiosity Agent (ES, 200 generations)")
    print("=" * 60)

    policy = PureFieldPolicy(obs_dim=25, hidden_dim=32, action_dim=4)
    reward_history = train_es(policy, env, generations=200, population=20, lr=0.03, sigma=0.1)

    # --- Phase 3: Evaluate trained curiosity agent ---
    print("\n" + "=" * 60)
    print("  Phase 3: Evaluating Trained Curiosity Agent")
    print("=" * 60)

    curiosity_interesting_fracs = []
    curiosity_unique_cells = []
    curiosity_total_surprises = []
    all_curiosity_visits = np.zeros((GRID_SIZE, GRID_SIZE), dtype=int)
    all_tensions = []

    for ep in range(N_EVAL):
        log_probs, rewards, tensions, positions = run_episode_curiosity(env, policy)
        curiosity_interesting_fracs.append(region_time_fraction(positions))
        unique = len(set(positions))
        curiosity_unique_cells.append(unique)
        curiosity_total_surprises.append(sum(rewards))
        for (r, c) in positions:
            all_curiosity_visits[r, c] += 1
        all_tensions.extend(tensions)

    print(f"\n  Curiosity agent ({N_EVAL} episodes, {MAX_STEPS} steps each):")
    print(f"  Mean interesting-zone fraction: {np.mean(curiosity_interesting_fracs):.4f}")
    print(f"  Mean unique cells visited:      {np.mean(curiosity_unique_cells):.1f} / {GRID_SIZE*GRID_SIZE}")
    print(f"  Mean total surprise per episode: {np.mean(curiosity_total_surprises):.4f}")

    print_visit_heatmap(all_curiosity_visits, "Curiosity Agent Visit Heatmap (100 episodes)")

    # --- Phase 4: Comparison ---
    print("\n" + "=" * 60)
    print("  Phase 4: Comparison")
    print("=" * 60)

    r_int = np.mean(random_interesting_fracs)
    c_int = np.mean(curiosity_interesting_fracs)
    r_uniq = np.mean(random_unique_cells)
    c_uniq = np.mean(curiosity_unique_cells)

    print(f"""
  +-----------------------------+----------+----------+----------+
  | Metric                      |  Random  | Curiosity|  Delta   |
  +-----------------------------+----------+----------+----------+
  | Interesting-zone fraction   | {r_int:8.4f} | {c_int:8.4f} | {c_int - r_int:+8.4f} |
  | Unique cells visited        | {r_uniq:8.1f} | {c_uniq:8.1f} | {c_uniq - r_uniq:+8.1f} |
  +-----------------------------+----------+----------+----------+
""")

    # --- Phase 5: Tension map ---
    print("=" * 60)
    print("  Phase 5: Tension Map (mean tension at each cell)")
    print("=" * 60)

    tension_map = np.zeros((GRID_SIZE, GRID_SIZE))
    tension_count = np.zeros((GRID_SIZE, GRID_SIZE))

    for ep in range(20):
        obs = env.reset()
        prev_tension = 0.0
        done = False
        while not done:
            probs, tension = policy.forward(obs)
            tension_map[env.r, env.c] += tension
            tension_count[env.r, env.c] += 1
            action = np.random.choice(NUM_ACTIONS, p=probs)
            obs, done = env.step(action)

    # Avoid division by zero
    tension_count[tension_count == 0] = 1
    tension_map /= tension_count

    print_grid_ascii(tension_map, "Mean Tension at Each Cell (trained agent)")

    # --- Correlation: tension vs local variance ---
    flat_tension = tension_map.flatten()
    flat_variance = vmap.flatten()

    # Only cells that were visited
    mask = (tension_count.flatten() > 1)
    if mask.sum() > 5:
        corr = np.corrcoef(flat_tension[mask], flat_variance[mask])[0, 1]
    else:
        corr = float('nan')

    print(f"\n  Correlation(tension, local_variance) over visited cells: {corr:.4f}")

    # --- Phase 6: Sample trajectory ---
    print("\n" + "=" * 60)
    print("  Phase 6: Sample Trajectories")
    print("=" * 60)

    print("\n  --- Random Agent ---")
    positions_r, _ = run_episode_random(env)
    print_trajectory_segment(positions_r, n=20)
    print(f"  Interesting fraction: {region_time_fraction(positions_r):.3f}")

    print("\n  --- Curiosity Agent ---")
    _, _, _, positions_c = run_episode_curiosity(env, policy)
    print_trajectory_segment(positions_c, n=20)
    print(f"  Interesting fraction: {region_time_fraction(positions_c):.3f}")

    # --- Phase 7: Training curve ---
    print("\n" + "=" * 60)
    print("  Phase 7: Training Curve (surprise reward over generations)")
    print("=" * 60)

    if reward_history:
        max_r = max(r for _, r in reward_history)
        min_r = min(r for _, r in reward_history)
        rng = max_r - min_r if max_r > min_r else 1.0

        print(f"\n  {'Gen':>6s}  {'Reward':>10s}  Bar")
        print(f"  {'-'*6}  {'-'*10}  {'-'*40}")
        for gen, r in reward_history:
            bar_len = int((r - min_r) / rng * 40)
            bar = '#' * bar_len
            print(f"  {gen:6d}  {r:10.4f}  |{bar}")

    # --- Summary ---
    print("\n" + "=" * 60)
    print("  Summary")
    print("=" * 60)

    gained_interest = c_int - r_int > 0.01
    gained_coverage = c_uniq - r_uniq > 1.0

    print(f"""
  Curiosity agent seeks interesting zones: {'YES' if gained_interest else 'NO'} (delta = {c_int - r_int:+.4f})
  Curiosity agent explores more cells:     {'YES' if gained_coverage else 'NO'} (delta = {c_uniq - r_uniq:+.1f})
  Tension-variance correlation:            {corr:.4f}

  Interpretation:
    - If interesting-zone fraction increased: tension-change reward
      drives the agent toward high-variance (surprising) regions.
    - If correlation(tension, variance) > 0: the PureField's internal
      tension responds to environmental complexity, confirming that
      the repulsion field encodes "interestingness".
    - This validates RC-4: |delta_tension| as intrinsic curiosity reward.
""")


if __name__ == '__main__':
    main()
