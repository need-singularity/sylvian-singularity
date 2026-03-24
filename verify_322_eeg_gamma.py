#!/usr/bin/env python3
"""가설 322 검증: EEG 감마 진동 = 반발력장 장력 (합성 EEG 실험)

Phase 1: 합성 EEG로 5가지 뇌 상태 생성 → 밴드파워 추출 → 반발력장 학습
→ 장력과 감마 파워의 상관 측정
→ 의식 수준별 장력 분포 비교
"""

import numpy as np
from scipy import signal as sp_signal
from scipy import stats

print("=" * 70)
print("가설 322 검증: EEG 감마 진동 = 반발력장 장력")
print("Phase 1: 합성 EEG + 반발력장 실험")
print("=" * 70)

# ─────────────────────────────────────────────
# 1. 합성 EEG 생성 (eeg_cct_validator.py 기반)
# ─────────────────────────────────────────────

FS = 256
SEED = 42
EPOCH_SEC = 2.0
EPOCH_SAMPLES = int(FS * EPOCH_SEC)
N_EPOCHS = 200  # 상태당 200 에폭

rng = np.random.default_rng(SEED)


def generate_1f_noise(n, fs, rng, exponent=1.0):
    freqs = np.fft.rfftfreq(n, d=1.0 / fs)
    freqs[0] = 1.0
    amplitudes = 1.0 / (freqs ** (exponent / 2.0))
    phases = rng.uniform(0, 2 * np.pi, len(freqs))
    spectrum = amplitudes * np.exp(1j * phases)
    spectrum[0] = 0
    noise = np.fft.irfft(spectrum, n=n)
    return noise / (np.std(noise) + 1e-15)


def generate_oscillation(n, fs, freq, amplitude, rng, phase_jitter=0.0):
    t = np.arange(n) / fs
    phase = 2 * np.pi * freq * t
    if phase_jitter > 0:
        walk = np.cumsum(rng.normal(0, phase_jitter, n))
        phase += walk
    return amplitude * np.sin(phase)


def synthesize_state(state, n, fs, rng):
    """뇌 상태별 합성 EEG 생성."""
    if state == "awake":
        theta = generate_oscillation(n, fs, 6.0, 10.0, rng, 0.02)
        alpha = generate_oscillation(n, fs, 10.0, 25.0, rng, 0.03)
        beta = generate_oscillation(n, fs, 22.0, 15.0, rng, 0.02)
        gamma = generate_oscillation(n, fs, 42.0, 8.0, rng, 0.01)
        pink = generate_1f_noise(n, fs, rng, 1.0) * 12.0
        return theta + alpha + beta + gamma + pink

    elif state == "sleep_n1":
        theta = generate_oscillation(n, fs, 5.0, 35.0, rng, 0.02)
        alpha = generate_oscillation(n, fs, 10.0, 10.0, rng, 0.01)
        gamma = generate_oscillation(n, fs, 40.0, 1.5, rng, 0.005)
        pink = generate_1f_noise(n, fs, rng, 1.2) * 8.0
        return theta + alpha + gamma + pink

    elif state == "sleep_n3":
        delta1 = generate_oscillation(n, fs, 1.0, 100.0, rng, 0.001)
        delta2 = generate_oscillation(n, fs, 2.0, 50.0, rng, 0.001)
        gamma = generate_oscillation(n, fs, 40.0, 0.3, rng, 0.001)
        pink = generate_1f_noise(n, fs, rng, 2.0) * 2.0
        return delta1 + delta2 + gamma + pink

    elif state == "anesthesia":
        delta = generate_oscillation(n, fs, 1.0, 80.0, rng, 0.001)
        # burst-suppression 마스크
        mask = np.ones(n)
        i = 0
        suppressed = False
        while i < n:
            if suppressed:
                dur = int(rng.uniform(1.5, 3.0) * fs)
                end = min(i + dur, n)
                mask[i:end] = 0.0
                i = end
            else:
                dur = int(rng.uniform(0.5, 1.5) * fs)
                i = min(i + dur, n)
            suppressed = not suppressed
        return delta * mask + rng.normal(0, 0.5, n)

    elif state == "rem":
        theta = generate_oscillation(n, fs, 5.5, 30.0, rng, 0.03)
        beta = generate_oscillation(n, fs, 20.0, 8.0, rng, 0.02)
        gamma = generate_oscillation(n, fs, 40.0, 4.0, rng, 0.01)
        pink = generate_1f_noise(n, fs, rng, 1.1) * 10.0
        return theta + beta + gamma + pink


STATES = ["awake", "rem", "sleep_n1", "sleep_n3", "anesthesia"]
STATE_NAMES = {
    "awake": "Awake (conscious)",
    "rem": "REM (dream)",
    "sleep_n1": "N1 (drowsy)",
    "sleep_n3": "N3 (deep sleep)",
    "anesthesia": "Anesthesia",
}
# 의식 수준 순서 (높은→낮은)
CONSCIOUSNESS_ORDER = {"awake": 5, "rem": 4, "sleep_n1": 3, "sleep_n3": 2, "anesthesia": 1}

print("\n상태별 합성 EEG 생성 중...")
all_features = []
all_labels = []
all_gamma_power = []
all_consciousness = []

for state in STATES:
    for ep in range(N_EPOCHS):
        eeg = synthesize_state(state, EPOCH_SAMPLES, FS, rng)

        # ─────────────────────────────────────────────
        # 2. 밴드파워 추출 (FFT)
        # ─────────────────────────────────────────────
        freqs_fft = np.fft.rfftfreq(EPOCH_SAMPLES, d=1.0/FS)
        fft_vals = np.abs(np.fft.rfft(eeg)) ** 2 / EPOCH_SAMPLES

        # 밴드파워 계산
        def band_power(f_low, f_high):
            mask = (freqs_fft >= f_low) & (freqs_fft < f_high)
            return np.mean(fft_vals[mask]) if np.any(mask) else 0.0

        delta_p = band_power(0.5, 4.0)
        theta_p = band_power(4.0, 8.0)
        alpha_p = band_power(8.0, 13.0)
        beta_p = band_power(13.0, 30.0)
        gamma_p = band_power(30.0, 100.0)
        total_p = delta_p + theta_p + alpha_p + beta_p + gamma_p + 1e-15

        # 특징 벡터: 상대 밴드파워 + 비율
        gamma_ratio = gamma_p / total_p
        theta_beta = theta_p / (beta_p + 1e-15)

        # 스펙트럼 엔트로피
        psd_norm = fft_vals / (np.sum(fft_vals) + 1e-15)
        psd_norm = psd_norm[psd_norm > 0]
        spectral_entropy = -np.sum(psd_norm * np.log2(psd_norm + 1e-15))

        features = np.array([
            delta_p, theta_p, alpha_p, beta_p, gamma_p,
            spectral_entropy, gamma_ratio, theta_beta
        ])
        features_log = np.log1p(features)  # log 스케일 for better separation

        all_features.append(features_log)
        all_labels.append(state)
        all_gamma_power.append(gamma_p)
        all_consciousness.append(CONSCIOUSNESS_ORDER[state])

X = np.array(all_features)
y_labels = np.array(all_labels)
y_gamma = np.array(all_gamma_power)
y_consciousness = np.array(all_consciousness)

print(f"  총 에폭: {len(X)} ({N_EPOCHS} x {len(STATES)} 상태)")
print(f"  특징 차원: {X.shape[1]}")

# ─────────────────────────────────────────────
# 3. 반발력장 엔진 학습
# ─────────────────────────────────────────────

print("\n" + "─" * 70)
print("3. 반발력장(Repulsive Field) 엔진 학습")
print("─" * 70)


class SimpleEngine:
    """간단한 선형 엔진 (W*x + b → softmax)."""
    def __init__(self, n_features, n_classes, rng, lr=0.01):
        self.W = rng.normal(0, 0.1, (n_features, n_classes))
        self.b = np.zeros(n_classes)
        self.lr = lr

    def forward(self, X):
        logits = X @ self.W + self.b
        # softmax
        exp_logits = np.exp(logits - np.max(logits, axis=-1, keepdims=True))
        return exp_logits / (np.sum(exp_logits, axis=-1, keepdims=True) + 1e-15)

    def train_step(self, X, y_onehot):
        probs = self.forward(X)
        # gradient (cross-entropy)
        grad = probs - y_onehot
        self.W -= self.lr * (X.T @ grad) / len(X)
        self.b -= self.lr * np.mean(grad, axis=0)
        loss = -np.mean(np.sum(y_onehot * np.log(probs + 1e-15), axis=-1))
        return loss


# One-hot encoding
classes = sorted(set(y_labels))
class_to_idx = {c: i for i, c in enumerate(classes)}
n_classes = len(classes)
y_idx = np.array([class_to_idx[l] for l in y_labels])
y_onehot = np.zeros((len(y_idx), n_classes))
y_onehot[np.arange(len(y_idx)), y_idx] = 1.0

# 정규화
X_mean = X.mean(axis=0)
X_std = X.std(axis=0) + 1e-15
X_norm = (X - X_mean) / X_std

# 두 엔진: A (산술적), G (기하적)
# A: 절반 특징만 사용 (밴드파워)
# G: 나머지 + 전체 (비율/엔트로피)
n_feat = X_norm.shape[1]
engine_A = SimpleEngine(n_feat, n_classes, np.random.default_rng(1), lr=0.05)
engine_G = SimpleEngine(n_feat, n_classes, np.random.default_rng(2), lr=0.05)

# 서로 다른 초기화 + 서로 다른 특징 가중치로 다양성 확보
# A는 짝수 특징 강조, G는 홀수 특징 강조
X_A = X_norm.copy()
X_G = X_norm.copy()
X_A[:, 1::2] *= 0.3   # A: 홀수 특징 약화
X_G[:, 0::2] *= 0.3   # G: 짝수 특징 약화

print("학습 시작...")
n_epochs_train = 200
for epoch in range(n_epochs_train):
    # 셔플
    perm = rng.permutation(len(X_norm))
    loss_A = engine_A.train_step(X_A[perm], y_onehot[perm])
    loss_G = engine_G.train_step(X_G[perm], y_onehot[perm])
    if (epoch + 1) % 50 == 0:
        print(f"  Epoch {epoch+1}/{n_epochs_train}: Loss_A={loss_A:.4f}, Loss_G={loss_G:.4f}")

# ─────────────────────────────────────────────
# 4. 장력(Tension) 계산
# ─────────────────────────────────────────────

print("\n" + "─" * 70)
print("4. 장력(Tension) = |Engine_A(x) - Engine_G(x)|^2")
print("─" * 70)

probs_A = engine_A.forward(X_A)
probs_G = engine_G.forward(X_G)

# 장력 = 두 엔진 출력의 제곱 거리
tension = np.sum((probs_A - probs_G) ** 2, axis=1)

# 정확도 계산
preds_A = np.argmax(probs_A, axis=1)
preds_G = np.argmax(probs_G, axis=1)
# 앙상블: 평균 확률
probs_ensemble = (probs_A + probs_G) / 2.0
preds_ensemble = np.argmax(probs_ensemble, axis=1)

acc_A = np.mean(preds_A == y_idx)
acc_G = np.mean(preds_G == y_idx)
acc_E = np.mean(preds_ensemble == y_idx)

print(f"  Engine A accuracy: {acc_A:.4f}")
print(f"  Engine G accuracy: {acc_G:.4f}")
print(f"  Ensemble accuracy: {acc_E:.4f}")

# ─────────────────────────────────────────────
# 5. 예측 P1: tension(awake) > tension(sleep)
# ─────────────────────────────────────────────

print("\n" + "─" * 70)
print("5. 예측 검증")
print("─" * 70)

print("\n--- P1: tension(awake) > tension(sleep) ---")
state_tensions = {}
for state in STATES:
    mask = y_labels == state
    t = tension[mask]
    state_tensions[state] = t
    print(f"  {STATE_NAMES[state]:<25} tension: mean={np.mean(t):.6f}, "
          f"std={np.std(t):.6f}, median={np.median(t):.6f}")

t_awake = state_tensions["awake"]
t_sleep = np.concatenate([state_tensions["sleep_n3"], state_tensions["anesthesia"]])

t_stat, p_val = stats.mannwhitneyu(t_awake, t_sleep, alternative="greater")
d_val = (np.mean(t_awake) - np.mean(t_sleep)) / np.sqrt(
    (np.std(t_awake)**2 + np.std(t_sleep)**2) / 2 + 1e-15
)
print(f"\n  Mann-Whitney U: stat={t_stat:.2f}, p={p_val:.2e}")
print(f"  Cohen's d: {d_val:.4f}")
p1_pass = p_val < 0.05 and d_val > 0.5
print(f"  P1 결과: {'PASS' if p1_pass else 'FAIL'} (d > 0.5 and p < 0.05)")

# ─────────────────────────────────────────────
# 6. 예측 P2: r(gamma_power, tension) > 0.5
# ─────────────────────────────────────────────

print("\n--- P2: r(gamma_power, tension) > 0.5 ---")
r_gamma, p_gamma = stats.pearsonr(y_gamma, tension)
r_spearman, p_spearman = stats.spearmanr(y_gamma, tension)
print(f"  Pearson r(gamma, tension) = {r_gamma:.4f}, p = {p_gamma:.2e}")
print(f"  Spearman rho(gamma, tension) = {r_spearman:.4f}, p = {p_spearman:.2e}")
p2_pass = r_gamma > 0.5 or r_spearman > 0.5
print(f"  P2 결과: {'PASS' if p2_pass else 'FAIL'}")

# ─────────────────────────────────────────────
# 7. 예측 P3: 장력만으로 의식 분류
# ─────────────────────────────────────────────

print("\n--- P3: 장력 단일 특징으로 각성 vs 수면 분류 ---")

# 이진 분류: awake vs non-awake
y_binary = (y_labels == "awake").astype(int)
# 최적 임계값 찾기
thresholds = np.linspace(np.min(tension), np.max(tension), 100)
best_acc = 0
best_thr = 0
for thr in thresholds:
    pred = (tension >= thr).astype(int)
    acc = np.mean(pred == y_binary)
    if acc > best_acc:
        best_acc = acc
        best_thr = thr

print(f"  최적 임계값: {best_thr:.6f}")
print(f"  분류 정확도: {best_acc:.4f}")
p3_pass = best_acc > 0.80
print(f"  P3 결과: {'PASS' if p3_pass else 'FAIL'} (accuracy > 80%)")

# 5-class 분류도 시도
# 장력 + 의식 수준 상관
r_consc, p_consc = stats.spearmanr(tension, y_consciousness)
print(f"\n  장력 vs 의식수준 Spearman rho = {r_consc:.4f}, p = {p_consc:.2e}")

# ─────────────────────────────────────────────
# 8. 예측 P4: 장력 순서 = 의식 순서
# ─────────────────────────────────────────────

print("\n--- P4: tension 순서 = 의식 수준 순서 ---")
mean_tensions = {s: np.mean(state_tensions[s]) for s in STATES}
sorted_by_tension = sorted(mean_tensions.items(), key=lambda x: x[1], reverse=True)

print("  예측 순서: awake > rem > N1 > N3 > anesthesia")
print("  실제 순서 (장력 높은 → 낮은):")
order_match = True
for i, (state, t_mean) in enumerate(sorted_by_tension):
    expected_order = STATES  # awake, rem, sleep_n1, sleep_n3, anesthesia
    marker = "✓" if sorted_by_tension[i][0] == STATES[i] else "✗"
    if sorted_by_tension[i][0] != STATES[i]:
        order_match = False
    print(f"    {i+1}. {STATE_NAMES[state]:<25} tension={t_mean:.6f} {marker}")

# Kendall's tau (순서 일치도)
predicted_rank = [CONSCIOUSNESS_ORDER[s] for s in STATES]
actual_rank_by_tension = []
for state in STATES:
    actual_rank_by_tension.append(mean_tensions[state])
tau, p_tau = stats.kendalltau(predicted_rank, actual_rank_by_tension)
print(f"\n  Kendall's tau = {tau:.4f}, p = {p_tau:.4f}")
p4_pass = tau > 0.6
print(f"  P4 결과: {'PASS' if p4_pass else 'FAIL'} (tau > 0.6)")

# ─────────────────────────────────────────────
# 9. 순환 논증 검사: 감마 제외 후 재분석
# ─────────────────────────────────────────────

print("\n" + "─" * 70)
print("9. 순환 논증 검사: 감마 특징 제외")
print("─" * 70)

# 감마 파워(feat[4])와 감마 비율(feat[6])을 제외한 특징으로 재학습
exclude_idx = [4, 6]  # gamma_power, gamma_ratio
keep_idx = [i for i in range(n_feat) if i not in exclude_idx]

X_no_gamma = X_norm[:, keep_idx]
X_A_ng = X_no_gamma.copy()
X_G_ng = X_no_gamma.copy()
n_feat_ng = len(keep_idx)
X_A_ng[:, 1::2] *= 0.3
X_G_ng[:, ::2] *= 0.3

engine_A_ng = SimpleEngine(n_feat_ng, n_classes, np.random.default_rng(10), lr=0.05)
engine_G_ng = SimpleEngine(n_feat_ng, n_classes, np.random.default_rng(20), lr=0.05)

for epoch in range(n_epochs_train):
    perm = rng.permutation(len(X_no_gamma))
    engine_A_ng.train_step(X_A_ng[perm], y_onehot[perm])
    engine_G_ng.train_step(X_G_ng[perm], y_onehot[perm])

probs_A_ng = engine_A_ng.forward(X_A_ng)
probs_G_ng = engine_G_ng.forward(X_G_ng)
tension_no_gamma = np.sum((probs_A_ng - probs_G_ng) ** 2, axis=1)

r_ng, p_ng = stats.pearsonr(y_gamma, tension_no_gamma)
print(f"  감마 제외 후 r(gamma, tension) = {r_ng:.4f}, p = {p_ng:.2e}")

# 감마 제외 후에도 의식 수준과 상관?
r_consc_ng, p_consc_ng = stats.spearmanr(tension_no_gamma, y_consciousness)
print(f"  감마 제외 후 rho(tension, consciousness) = {r_consc_ng:.4f}, p = {p_consc_ng:.2e}")

for state in STATES:
    mask = y_labels == state
    t = tension_no_gamma[mask]
    print(f"    {STATE_NAMES[state]:<25} tension_no_gamma: mean={np.mean(t):.6f}")

# ─────────────────────────────────────────────
# 10. ASCII 시각화
# ─────────────────────────────────────────────

print("\n" + "─" * 70)
print("10. 결과 시각화")
print("─" * 70)

# 상태별 장력 분포 히스토그램
print("\n장력 분포 (상태별):")
max_tension = np.max(tension)
bin_edges = np.linspace(0, max_tension * 1.1, 30)

for state in STATES:
    mask = y_labels == state
    t = tension[mask]
    hist, _ = np.histogram(t, bins=bin_edges)
    max_h = max(hist) if max(hist) > 0 else 1
    bar = ""
    for h in hist:
        n_chars = int(h / max_h * 20)
        bar += "█" * n_chars if n_chars > 0 else ""
    print(f"  {STATE_NAMES[state]:<25} |{bar}| mean={np.mean(t):.5f}")

# 감마 vs 장력 산점도 (ASCII)
print("\n감마 파워 vs 장력 (ASCII 산점도):")
width, height = 60, 20
canvas = [[' ' for _ in range(width)] for _ in range(height)]

x_min, x_max = np.min(tension), np.max(tension)
y_min, y_max = np.min(y_gamma), np.max(y_gamma)

state_chars = {"awake": "A", "rem": "R", "sleep_n1": "1", "sleep_n3": "3", "anesthesia": "X"}

for i in range(0, len(tension), 5):  # subsample for readability
    x = int((tension[i] - x_min) / (x_max - x_min + 1e-15) * (width - 1))
    y = int((y_gamma[i] - y_min) / (y_max - y_min + 1e-15) * (height - 1))
    y = height - 1 - y
    x = max(0, min(x, width - 1))
    y = max(0, min(y, height - 1))
    canvas[y][x] = state_chars[y_labels[i]]

print(f"  Gamma {'':>{width-6}}")
print(f"  power")
for i, row in enumerate(canvas):
    if i == 0:
        print(f"  {y_max:>8.1f} |{''.join(row)}|")
    elif i == height - 1:
        print(f"  {y_min:>8.1f} |{''.join(row)}|")
    else:
        print(f"  {'':>8} |{''.join(row)}|")
print(f"  {'':>8}  {'─' * width}")
print(f"  {'':>8}  {x_min:.4f}{' ' * (width - 16)}{x_max:.4f}")
print(f"  {'':>8}  {'Tension (|A-G|^2)':^{width}}")
print(f"  Legend: A=Awake, R=REM, 1=N1, 3=N3, X=Anesthesia")

# ─────────────────────────────────────────────
# 11. 종합 결과
# ─────────────────────────────────────────────

print("\n" + "=" * 70)
print("11. 종합 결과")
print("=" * 70)

results = {
    "P1 tension(awake) > tension(sleep)": (p1_pass, f"d={d_val:.3f}, p={p_val:.2e}"),
    "P2 r(gamma, tension) > 0.5": (p2_pass, f"r={r_gamma:.3f}, rho={r_spearman:.3f}"),
    "P3 장력 단일 분류 > 80%": (p3_pass, f"acc={best_acc:.3f}"),
    "P4 장력 순서 = 의식 순서": (p4_pass, f"tau={tau:.3f}"),
}

print(f"\n{'Prediction':<40} {'Result':>8} {'Detail':<30}")
print("─" * 80)
pass_count = 0
for pred, (passed, detail) in results.items():
    result_str = "PASS" if passed else "FAIL"
    print(f"  {pred:<40} {result_str:>6}   {detail}")
    if passed:
        pass_count += 1

print(f"\n통과: {pass_count}/{len(results)}")

# 순환 논증 검사 결과
print(f"\n순환 논증 검사:")
print(f"  감마 포함: r(gamma, tension) = {r_gamma:.4f}")
print(f"  감마 제외: r(gamma, tension) = {r_ng:.4f}")
if abs(r_ng) > 0.3:
    print(f"  → 감마 제외 후에도 상관 유지 → 장력이 감마 이상의 정보 포착")
else:
    print(f"  → 감마 제외 시 상관 소멸 → 장력의 감마 의존성 높음 (순환 주의)")

print(f"""
  ┌─────────────────────────────────────────────────────────────────┐
  │ 가설 322 Phase 1 검증 결과 (합성 EEG)                           │
  ├─────────────────────────────────────────────────────────────────┤
  │                                                                 │
  │ P1 (의식→장력): {'PASS' if p1_pass else 'FAIL':>4}  d={d_val:.3f}                            │
  │ P2 (감마-장력): {'PASS' if p2_pass else 'FAIL':>4}  r={r_gamma:.3f}, rho={r_spearman:.3f}                   │
  │ P3 (단일분류):  {'PASS' if p3_pass else 'FAIL':>4}  acc={best_acc:.3f}                           │
  │ P4 (순서일치):  {'PASS' if p4_pass else 'FAIL':>4}  tau={tau:.3f}                             │
  │                                                                 │
  │ 순환 검사:                                                       │
  │   감마 포함 r={r_gamma:.3f} → 감마 제외 r={r_ng:.3f}                       │
  │   의식 상관 rho={r_consc:.3f} → 감마 제외 rho={r_consc_ng:.3f}               │
  │                                                                 │
  │ 한계: 합성 데이터 → 실제 EEG(PhysioNet)로 재검증 필요            │
  │                                                                 │
  │ 상태: {'🟧 부분 검증' if pass_count >= 2 else '⚪ 미검증'} (Phase 1 합성 데이터)                     │
  └─────────────────────────────────────────────────────────────────┘
""")

print("검증 완료.")
