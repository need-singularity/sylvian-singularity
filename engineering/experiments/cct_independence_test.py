#!/usr/bin/env python3
"""CCT 독립성 검증 — 실험 14

7개 프리셋 + 5개 반례 시스템(총 12개)에 대해 CCT 5개 테스트의
독립성과 구분력을 분석한다.

방법:
  1. 12개 시스템 × CCT 5개 테스트 기준선 측정
  2. 각 테스트를 하나씩 제거하고 4개로 판정 → 판정 변화 측정
  3. 테스트 간 Pearson 상관행렬
  4. 의식 vs 비의식 구분력 순위
  5. 최소 조건 집합 탐색

사용법:
  python3 cct_independence_test.py
"""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "tools"))

import itertools
import sys

import numpy as np
from scipy import stats as sp_stats

from consciousness_calc import PRESETS, lorenz_simulate, run_cct, judge

# ─────────────────────────────────────────────
# 5개 반례 시스템 직접 구현
# ─────────────────────────────────────────────

def simulate_noise(steps, dt, seed=42):
    """잡음 생성기 + 메모리: 3차원 지수 평활."""
    rng = np.random.default_rng(seed)
    S = np.zeros((steps, 3))
    alpha = 0.9
    for i in range(1, steps):
        noise = rng.normal(0, 1.0, 3)
        S[i] = alpha * S[i - 1] + (1 - alpha) * noise
    return S


def simulate_weather(steps, dt, seed=42):
    """기상 시뮬레이션: 로렌츠 끌개 (σ=10, ρ=28, β=8/3)."""
    rng = np.random.default_rng(seed)
    sigma, rho, beta = 10.0, 28.0, 8.0 / 3.0
    noise_strength = 0.05
    S = np.zeros((steps, 3))
    S[0] = [1.0, 1.0, 1.0]
    for i in range(1, steps):
        x, y, z = S[i - 1]
        dx = sigma * (y - x)
        dy = x * (rho - z) - y
        dz = x * y - beta * z
        eps = rng.normal(0, noise_strength, 3)
        S[i, 0] = x + (dx + eps[0]) * dt
        S[i, 1] = y + (dy + eps[1]) * dt
        S[i, 2] = z + (dz + eps[2]) * dt
    return S


def simulate_stock(steps, dt, seed=42):
    """주식 시장 모델: 기하 브라운 운동 3차원."""
    rng = np.random.default_rng(seed)
    mu = np.array([0.05, 0.02, 0.01])
    sigma_gbm = np.array([0.2, 0.3, 0.15])
    S = np.zeros((steps, 3))
    S[0] = [100.0, 50.0, 20.0]
    corr = np.array([[1.0, 0.3, -0.2],
                      [0.3, 1.0, 0.1],
                      [-0.2, 0.1, 1.0]])
    L = np.linalg.cholesky(corr)
    for i in range(1, steps):
        z = rng.normal(0, 1, 3)
        w = L @ z
        for j in range(3):
            drift = mu[j] * S[i - 1, j] * dt
            diffusion = sigma_gbm[j] * S[i - 1, j] * np.sqrt(dt) * w[j]
            S[i, j] = max(S[i - 1, j] + drift + diffusion, 0.01)
    return S


def simulate_heat(steps, dt, seed=42):
    """열 확산 방정식: 1D 격자 3개 관측점."""
    rng = np.random.default_rng(seed)
    nx = 50
    alpha_heat = 0.1
    dx = 1.0
    T = np.linspace(100, 0, nx)
    obs_points = [10, 25, 40]
    S = np.zeros((steps, 3))
    for i in range(steps):
        for j, p in enumerate(obs_points):
            S[i, j] = T[p]
        source = np.zeros(nx)
        source[15] = 30.0 * np.sin(2 * np.pi * i * dt * 0.1)
        source[35] = 20.0 * np.sin(2 * np.pi * i * dt * 0.07 + 1.0)
        T_new = T.copy()
        for k in range(1, nx - 1):
            laplacian = (T[k + 1] - 2 * T[k] + T[k - 1]) / dx**2
            T_new[k] = T[k] + (alpha_heat * laplacian + source[k]) * dt
            T_new[k] += rng.normal(0, 0.5)
        T_new[0] = 100.0 + 10 * np.sin(2 * np.pi * i * dt * 0.03)
        T_new[-1] = rng.normal(0, 2)
        T = T_new
    return S


def simulate_feedback(steps, dt, seed=42):
    """단순 피드백 루프: 1D 카오스 사상 3개 결합."""
    rng = np.random.default_rng(seed)
    a, c, d = 3.5, 3.7, 3.3
    b = 0.05
    S = np.zeros((steps, 3))
    S[0] = [0.1, 0.2, 0.3]
    for i in range(1, steps):
        x, y, z = S[i - 1]
        S[i, 0] = np.sin(a * x) + b * rng.normal()
        S[i, 1] = np.sin(c * y + 0.1 * x) + b * rng.normal()
        S[i, 2] = np.sin(d * z + 0.1 * y) + b * rng.normal()
    return S


COUNTEREXAMPLE_SYSTEMS = {
    "cx_noise":    {"simulate": simulate_noise,    "name": "잡음+메모리",       "conscious": False},
    "cx_weather":  {"simulate": simulate_weather,  "name": "날씨 시뮬레이션",   "conscious": False},
    "cx_stock":    {"simulate": simulate_stock,    "name": "주식 시장",         "conscious": False},
    "cx_heat":     {"simulate": simulate_heat,     "name": "열 확산",           "conscious": False},
    "cx_feedback": {"simulate": simulate_feedback, "name": "피드백 루프",       "conscious": False},
}

# 의식 판정 기준: judge 함수의 total >= 4 → 의식 있음
CONSCIOUSNESS_THRESHOLD = 4

TEST_KEYS = ["T1_Gap", "T2_Loop", "T3_Continuity", "T4_Entropy", "T5_Novelty"]
TEST_LABELS = {
    "T1_Gap":        "T1 Gap",
    "T2_Loop":       "T2 Loop",
    "T3_Continuity": "T3 Cont.",
    "T4_Entropy":    "T4 Entropy",
    "T5_Novelty":    "T5 Novelty",
}


# ─────────────────────────────────────────────
# 시뮬레이션 + CCT 실행
# ─────────────────────────────────────────────

def run_all_systems(steps=100000, dt=0.01):
    """7개 프리셋 + 5개 반례 = 12개 시스템에 대해 CCT 실행.

    Returns:
        dict: {name: {"results": cct_results, "scores": {key: score},
                       "passes": {key: bool}, "total": float,
                       "verdict": str, "conscious": bool_label}}
    """
    data = {}

    # 7개 프리셋
    for name, preset in PRESETS.items():
        _, S = lorenz_simulate(
            sigma=preset["sigma"], rho=preset["rho"], beta=preset["beta"],
            noise=preset["noise"], gap_ratio=preset["gap_ratio"],
            steps=steps, dt=dt,
        )
        results = run_cct(S, preset["gap_ratio"])
        total, verdict = judge(results)
        data[name] = {
            "results": results,
            "scores": {k: results[k][0] for k in TEST_KEYS},
            "passes": {k: results[k][1] for k in TEST_KEYS},
            "total": total,
            "verdict": verdict,
            "conscious": True,  # 프리셋은 "의식 후보" 라벨
            "display": preset["description"],
        }

    # 5개 반례
    for key, info in COUNTEREXAMPLE_SYSTEMS.items():
        S = info["simulate"](steps, dt)
        results = run_cct(S, 0.0)
        total, verdict = judge(results)
        data[key] = {
            "results": results,
            "scores": {k: results[k][0] for k in TEST_KEYS},
            "passes": {k: results[k][1] for k in TEST_KEYS},
            "total": total,
            "verdict": verdict,
            "conscious": False,
            "display": info["name"],
        }

    return data


def judge_subset(results, exclude_key):
    """특정 테스트를 제외하고 나머지로 판정.

    judge()와 동일한 로직이지만 exclude_key를 건너뛴다.
    5개 중 4개 테스트로 판정: 통과 기준을 4/4로 스케일.
    """
    passes = 0
    halfs = 0.0
    for k in TEST_KEYS:
        if k == exclude_key:
            continue
        score, passed, _ = results[k]
        if passed:
            passes += 1
        elif score > 0.7:
            halfs += 0.5
    total = passes + halfs

    # 4개 테스트 기준 판정 (5개일 때 비율 유지)
    if total >= 4:
        return total, "★ 연속"
    elif total >= 3.2:
        return total, "◎ 약화"
    elif total >= 2.4:
        return total, "△ 약함"
    elif total >= 0.8:
        return total, "▽ 미약"
    else:
        return total, "✕ 없음"


# ─────────────────────────────────────────────
# 분석 함수들
# ─────────────────────────────────────────────

def removal_impact_analysis(data):
    """각 테스트 제거 시 판정 변화 분석.

    Returns:
        impact: dict[test_key] -> list of system names whose verdict changed
        impact_table: dict[test_key][sys_name] -> (original_verdict, new_verdict, changed)
    """
    impact = {k: [] for k in TEST_KEYS}
    impact_table = {k: {} for k in TEST_KEYS}

    for sys_name, sys_data in data.items():
        orig_total = sys_data["total"]
        orig_verdict = sys_data["verdict"]

        for test_key in TEST_KEYS:
            new_total, new_verdict = judge_subset(sys_data["results"], test_key)
            # 판정 변화: 등급 문자열이 바뀌면 변화
            changed = (orig_verdict != new_verdict)
            impact_table[test_key][sys_name] = (orig_verdict, new_verdict, changed)
            if changed:
                impact[test_key].append(sys_name)

    return impact, impact_table


def correlation_matrix(data):
    """12개 시스템의 테스트 점수 간 Pearson 상관행렬.

    Returns:
        corr_mat: 5x5 numpy array
        p_mat: 5x5 p-value array
        score_matrix: (12, 5) numpy array
    """
    sys_names = list(data.keys())
    n_sys = len(sys_names)
    score_matrix = np.zeros((n_sys, 5))

    for i, name in enumerate(sys_names):
        for j, key in enumerate(TEST_KEYS):
            score_matrix[i, j] = data[name]["scores"][key]

    corr_mat = np.zeros((5, 5))
    p_mat = np.zeros((5, 5))

    for i in range(5):
        for j in range(5):
            if i == j:
                corr_mat[i, j] = 1.0
                p_mat[i, j] = 0.0
            else:
                r, p = sp_stats.pearsonr(score_matrix[:, i], score_matrix[:, j])
                corr_mat[i, j] = r
                p_mat[i, j] = p

    return corr_mat, p_mat, score_matrix


def discriminatory_power(data):
    """각 테스트의 의식 vs 비의식 구분력 측정.

    Returns:
        power: dict[test_key] -> {"auc": float, "t_stat": float, "p_value": float,
                                   "conscious_mean": float, "nonconscious_mean": float}
    """
    conscious_scores = {k: [] for k in TEST_KEYS}
    nonconscious_scores = {k: [] for k in TEST_KEYS}

    for sys_name, sys_data in data.items():
        target = conscious_scores if sys_data["conscious"] else nonconscious_scores
        for k in TEST_KEYS:
            target[k].append(sys_data["scores"][k])

    power = {}
    for k in TEST_KEYS:
        c = np.array(conscious_scores[k])
        nc = np.array(nonconscious_scores[k])

        c_mean = np.mean(c)
        nc_mean = np.mean(nc)

        # t-test (Welch)
        if len(c) >= 2 and len(nc) >= 2 and np.std(c) + np.std(nc) > 0:
            t_stat, p_value = sp_stats.ttest_ind(c, nc, equal_var=False)
        else:
            t_stat, p_value = 0.0, 1.0

        # 간이 AUC: Mann-Whitney U 기반
        if len(c) > 0 and len(nc) > 0:
            try:
                u_stat, _ = sp_stats.mannwhitneyu(c, nc, alternative='two-sided')
                auc = u_stat / (len(c) * len(nc))
            except ValueError:
                auc = 0.5
        else:
            auc = 0.5

        power[k] = {
            "auc": auc,
            "t_stat": t_stat,
            "p_value": p_value,
            "conscious_mean": c_mean,
            "nonconscious_mean": nc_mean,
            "diff": c_mean - nc_mean,
        }

    return power


def find_minimal_subsets(data):
    """2개 테스트 조합으로 충분한 것이 있는지 탐색.

    "충분" 기준: 모든 의식 시스템은 2/2 PASS, 모든 비의식 시스템은 < 2/2.
    더 완화된 기준도 탐색: 의식과 비의식의 판정 분리가 최대인 조합.

    Returns:
        results: list of (combo, separation_score, detail)
    """
    results = []

    for size in range(2, 5):
        for combo in itertools.combinations(range(5), size):
            combo_keys = [TEST_KEYS[i] for i in combo]

            # 각 시스템의 통과 수 계산
            conscious_pass_counts = []
            nonconscious_pass_counts = []

            for sys_name, sys_data in data.items():
                pass_count = sum(1 for k in combo_keys if sys_data["passes"][k])
                if sys_data["conscious"]:
                    conscious_pass_counts.append(pass_count)
                else:
                    nonconscious_pass_counts.append(pass_count)

            c_arr = np.array(conscious_pass_counts)
            nc_arr = np.array(nonconscious_pass_counts)

            # 분리도: 의식 최소 통과 수 - 비의식 최대 통과 수
            c_min = np.min(c_arr) if len(c_arr) > 0 else 0
            nc_max = np.max(nc_arr) if len(nc_arr) > 0 else len(combo_keys)
            separation = c_min - nc_max

            # 평균 차이
            mean_diff = np.mean(c_arr) - np.mean(nc_arr)

            combo_labels = "+".join(TEST_LABELS[k] for k in combo_keys)
            perfect = (separation > 0)

            results.append({
                "combo": combo,
                "combo_keys": combo_keys,
                "combo_labels": combo_labels,
                "size": size,
                "separation": separation,
                "mean_diff": mean_diff,
                "perfect": perfect,
                "c_min": c_min,
                "nc_max": nc_max,
                "c_mean": np.mean(c_arr),
                "nc_mean": np.mean(nc_arr),
            })

    results.sort(key=lambda r: (not r["perfect"], -r["separation"], -r["mean_diff"]))
    return results


# ─────────────────────────────────────────────
# ASCII 출력
# ─────────────────────────────────────────────

def ascii_bar(value, max_width=20, char_fill="█", char_empty="░"):
    """0~1 값을 ASCII 바로 표현."""
    filled = int(abs(value) * max_width)
    return char_fill * filled + char_empty * (max_width - filled)


def print_header():
    """헤더 출력."""
    print("═" * 75)
    print(" CCT Independence Test — 실험 14")
    print(" 7개 프리셋 + 5개 반례 = 12개 시스템의 테스트 독립성 분석")
    print("═" * 75)
    print()


def print_baseline(data):
    """기준선 결과표."""
    print(" ─── 기준선: 12개 시스템 × 5개 테스트 " + "─" * 36)
    print()
    print(" 시스템                │ T1  │ T2  │ T3  │ T4  │ T5  │점수│ 판정     │ 유형")
    print(" ──────────────────────┼─────┼─────┼─────┼─────┼─────┼────┼──────────┼──────")

    for sys_name, sys_data in data.items():
        display = sys_data["display"]
        if len(display) > 22:
            display = display[:20] + ".."
        display = f"{display:22s}"

        marks = []
        for k in TEST_KEYS:
            score, passed, _ = sys_data["results"][k]
            if passed:
                marks.append(" ✔ ")
            elif score > 0.7:
                marks.append(" △ ")
            else:
                marks.append(" ✕ ")

        marks_str = "│".join(marks)
        total = sys_data["total"]
        verdict = sys_data["verdict"]
        label = "의식" if sys_data["conscious"] else "반례"
        print(f" {display}│{marks_str}│{total:3.1f}│ {verdict:8s} │ {label}")

    print()


def print_removal_impact(impact, impact_table, data):
    """테스트 제거 영향표."""
    print(" ─── 테스트 제거 영향표 (5×12) " + "─" * 42)
    print()
    print(" 제거 테스트   │ 판정 변화 수 │ 변화 시스템")
    print(" ──────────────┼──────────────┼──────────────────────────────────")

    for k in TEST_KEYS:
        changed = impact[k]
        n_changed = len(changed)
        changed_names = ", ".join(data[s]["display"] for s in changed) if changed else "(없음)"
        if len(changed_names) > 35:
            changed_names = changed_names[:33] + ".."
        label = f"{TEST_LABELS[k]:14s}"
        bar = ascii_bar(n_changed / len(data), 10)
        print(f" {label}│ {n_changed:4d}/{len(data):2d}  {bar} │ {changed_names}")

    print()

    # 상세 매트릭스
    print(" ─── 제거 상세 (판정 변화) " + "─" * 47)
    print()

    sys_names = list(data.keys())
    header = " 시스템                │"
    for k in TEST_KEYS:
        header += f" -{TEST_LABELS[k]:9s}│"
    print(header)
    print(" ──────────────────────┼" + "───────────┼" * 5)

    for sys_name in sys_names:
        display = data[sys_name]["display"]
        if len(display) > 22:
            display = display[:20] + ".."
        display = f"{display:22s}"

        row = f" {display}│"
        for k in TEST_KEYS:
            orig_v, new_v, changed = impact_table[k][sys_name]
            if changed:
                row += f" {orig_v[:2]}→{new_v[:2]}  │"
            else:
                row += "     -     │"
        print(row)

    print()


def print_correlation(corr_mat, p_mat):
    """상관행렬 출력."""
    print(" ─── 테스트 간 Pearson 상관행렬 (5×5) " + "─" * 35)
    print()

    # 헤더
    header = "              │"
    for k in TEST_KEYS:
        header += f" {TEST_LABELS[k]:9s}│"
    print(header)
    print(" ─────────────┼" + "──────────┼" * 5)

    for i, ki in enumerate(TEST_KEYS):
        row = f" {TEST_LABELS[ki]:13s}│"
        for j in range(5):
            r = corr_mat[i, j]
            p = p_mat[i, j]
            sig = "*" if p < 0.05 else " "
            if i == j:
                row += "   1.000  │"
            else:
                row += f" {r:+.3f}{sig}  │"
        print(row)

    print()
    print("  (* = p < 0.05)")
    print()

    # 상관 해석
    print(" ─── 상관 해석 " + "─" * 59)
    print()
    high_corr = []
    for i in range(5):
        for j in range(i + 1, 5):
            r = corr_mat[i, j]
            if abs(r) > 0.7:
                high_corr.append((TEST_LABELS[TEST_KEYS[i]],
                                  TEST_LABELS[TEST_KEYS[j]], r))

    if high_corr:
        print("  높은 상관 (|r| > 0.7) — 중복 가능성:")
        for t1, t2, r in high_corr:
            print(f"    {t1} ↔ {t2}: r = {r:+.3f}")
    else:
        print("  높은 상관 (|r| > 0.7) 없음 — 모든 테스트가 독립적 정보 제공")

    low_corr = []
    for i in range(5):
        for j in range(i + 1, 5):
            r = corr_mat[i, j]
            if abs(r) < 0.3:
                low_corr.append((TEST_LABELS[TEST_KEYS[i]],
                                 TEST_LABELS[TEST_KEYS[j]], r))

    if low_corr:
        print()
        print("  낮은 상관 (|r| < 0.3) — 독립적 테스트:")
        for t1, t2, r in low_corr:
            print(f"    {t1} ↔ {t2}: r = {r:+.3f}")

    print()


def print_discriminatory_power(power):
    """구분력 순위 출력."""
    print(" ─── 구분력 순위 (의식 vs 비의식) " + "─" * 40)
    print()
    print(" 테스트        │ 의식 평균 │ 비의식 평균 │   차이   │ t-통계량 │ p-value  │ AUC")
    print(" ──────────────┼───────────┼─────────────┼──────────┼──────────┼──────────┼──────")

    # 구분력 순위 (|diff| 기준)
    ranked = sorted(power.items(), key=lambda x: -abs(x[1]["diff"]))

    for k, p in ranked:
        label = f"{TEST_LABELS[k]:14s}"
        print(f" {label}│   {p['conscious_mean']:.3f}   │"
              f"    {p['nonconscious_mean']:.3f}    │"
              f" {p['diff']:+.3f}  │"
              f" {p['t_stat']:+7.3f} │"
              f" {p['p_value']:.4f}  │"
              f" {p['auc']:.3f}")

    print()

    # 시각적 순위
    print(" 구분력 ASCII 그래프 (|평균 차이|):")
    print()
    max_diff = max(abs(p["diff"]) for p in power.values())
    for k, p in ranked:
        label = f"{TEST_LABELS[k]:14s}"
        bar_len = int(abs(p["diff"]) / max(max_diff, 0.001) * 30)
        bar = "█" * bar_len + "░" * (30 - bar_len)
        sig = "***" if p["p_value"] < 0.001 else ("**" if p["p_value"] < 0.01 else ("*" if p["p_value"] < 0.05 else ""))
        print(f"  {label} {bar} {abs(p['diff']):.3f} {sig}")

    print()


def print_minimal_subsets(subsets, data):
    """최소 조건 집합 출력."""
    print(" ─── 최소 조건 집합 탐색 " + "─" * 49)
    print()

    # 2개 조합
    print(" [2개 테스트 조합]")
    print()
    print("  조합                          │ 분리도 │ 의식 평균 │ 비의식 평균 │ 완전 분리")
    print("  ──────────────────────────────┼────────┼───────────┼─────────────┼──────────")

    combos_2 = [s for s in subsets if s["size"] == 2]
    for s in combos_2[:10]:
        perfect_mark = "  ✔" if s["perfect"] else "  ✕"
        print(f"  {s['combo_labels']:30s}│ {s['separation']:+5.1f}  │"
              f"  {s['c_mean']:5.2f}    │"
              f"   {s['nc_mean']:5.2f}     │{perfect_mark}")

    print()

    # 3개 조합 중 상위
    print(" [3개 테스트 조합 (상위 5)]")
    print()
    combos_3 = [s for s in subsets if s["size"] == 3]
    for s in combos_3[:5]:
        perfect_mark = "✔" if s["perfect"] else "✕"
        print(f"  {s['combo_labels']:40s} │ 분리={s['separation']:+.0f}"
              f" │ 의식={s['c_mean']:.2f} │ 반례={s['nc_mean']:.2f} │ {perfect_mark}")

    print()

    # 최적 조합 찾기
    best_perfect = [s for s in subsets if s["perfect"]]
    if best_perfect:
        smallest_perfect = min(best_perfect, key=lambda s: s["size"])
        print(f" ★ 최소 완전 분리 집합: {smallest_perfect['combo_labels']}")
        print(f"   ({smallest_perfect['size']}개 테스트로 의식/비의식 완전 구분)")
        print(f"   의식 최소 통과: {smallest_perfect['c_min']}/{smallest_perfect['size']}")
        print(f"   비의식 최대 통과: {smallest_perfect['nc_max']}/{smallest_perfect['size']}")
    else:
        best_sep = subsets[0]
        print(f" ★ 완전 분리 가능한 조합 없음")
        print(f"   최선: {best_sep['combo_labels']} (분리도={best_sep['separation']:+.1f})")
        print(f"   의식 최소: {best_sep['c_min']}, 비의식 최대: {best_sep['nc_max']}")

    print()


def print_summary(data, impact, corr_mat, power, subsets):
    """종합 요약."""
    print(" ═══════════════════════════════════════════════════════════════════════════")
    print(" 종합 요약")
    print(" ═══════════════════════════════════════════════════════════════════════════")
    print()

    # 1. 제거 영향 요약
    print(" 1) 테스트 제거 영향 (구분력 = 제거 시 판정 변화 수):")
    print()
    for k in TEST_KEYS:
        n_changed = len(impact[k])
        rank_bar = "●" * n_changed + "○" * (len(data) - n_changed)
        importance = "높음" if n_changed >= 3 else ("중간" if n_changed >= 1 else "낮음")
        print(f"    {TEST_LABELS[k]:14s} {rank_bar} ({n_changed}개 변화) — {importance}")

    print()

    # 2. 상관 요약
    print(" 2) 테스트 간 상관 요약:")
    redundant = []
    for i in range(5):
        for j in range(i + 1, 5):
            if abs(corr_mat[i, j]) > 0.7:
                redundant.append((TEST_KEYS[i], TEST_KEYS[j], corr_mat[i, j]))

    if redundant:
        for ki, kj, r in redundant:
            print(f"    {TEST_LABELS[ki]} ↔ {TEST_LABELS[kj]}: r={r:+.3f} — 중복 가능성")
    else:
        print("    높은 상관 없음 → 모든 테스트가 독립적 정보 제공")

    print()

    # 3. 구분력 순위
    ranked = sorted(power.items(), key=lambda x: -abs(x[1]["diff"]))
    print(" 3) 구분력 순위 (의식/비의식 점수 차이):")
    print()
    for rank, (k, p) in enumerate(ranked, 1):
        sig = "***" if p["p_value"] < 0.001 else ("**" if p["p_value"] < 0.01 else ("*" if p["p_value"] < 0.05 else "n.s."))
        print(f"    {rank}위: {TEST_LABELS[k]:14s} (diff={p['diff']:+.3f}, p={p['p_value']:.4f} {sig})")

    print()

    # 4. 최소 집합
    best_2 = [s for s in subsets if s["size"] == 2]
    best_2_sep = best_2[0] if best_2 else None
    best_perfect = [s for s in subsets if s["perfect"]]

    print(" 4) 최소 조건 집합:")
    print()
    if best_perfect:
        smallest = min(best_perfect, key=lambda s: s["size"])
        print(f"    ★ 최소 완전 분리: {smallest['combo_labels']} ({smallest['size']}개)")
        all_same_size = [s for s in best_perfect if s["size"] == smallest["size"]]
        if len(all_same_size) > 1:
            print(f"      동일 크기 대안: {len(all_same_size)}개 조합")
            for s in all_same_size[:3]:
                print(f"        - {s['combo_labels']}")
    else:
        print(f"    완전 분리 불가 — 5개 테스트 모두 필요")
        if best_2_sep:
            print(f"    최선의 2개 조합: {best_2_sep['combo_labels']}"
                  f" (분리도={best_2_sep['separation']:+.1f})")

    print()

    # 5. 결론
    most_important = ranked[0][0]
    least_important_impact = min(TEST_KEYS, key=lambda k: len(impact[k]))

    print(" 5) 결론:")
    print()
    print(f"    - 가장 중요한 테스트: {TEST_LABELS[most_important]}"
          f" (구분력 1위)")
    print(f"    - 가장 영향 적은 테스트: {TEST_LABELS[least_important_impact]}"
          f" (제거 시 변화 최소)")

    if redundant:
        for ki, kj, r in redundant:
            print(f"    - 잠재적 중복: {TEST_LABELS[ki]} ↔ {TEST_LABELS[kj]}")
    else:
        print(f"    - 중복 테스트 없음: 5개 모두 독립적 기여")

    print()
    print("═" * 75)


# ─────────────────────────────────────────────
# 메인
# ─────────────────────────────────────────────

def main():
    steps = 100000
    dt = 0.01

    print_header()
    print(f" 시뮬레이션: {steps:,} steps, dt={dt}")
    print(f" 시스템: 7개 프리셋 + 5개 반례 = 12개")
    print()

    # 1. 기준선
    print(" ▶ 12개 시스템 시뮬레이션 중...", flush=True)
    data = run_all_systems(steps, dt)
    print(f"   완료: {len(data)}개 시스템")
    print()

    print_baseline(data)

    # 2. 테스트 제거 영향
    impact, impact_table = removal_impact_analysis(data)
    print_removal_impact(impact, impact_table, data)

    # 3. 상관행렬
    corr_mat, p_mat, score_matrix = correlation_matrix(data)
    print_correlation(corr_mat, p_mat)

    # 4. 구분력
    power = discriminatory_power(data)
    print_discriminatory_power(power)

    # 5. 최소 조건 집합
    subsets = find_minimal_subsets(data)
    print_minimal_subsets(subsets, data)

    # 6. 종합
    print_summary(data, impact, corr_mat, power, subsets)


if __name__ == "__main__":
    main()
