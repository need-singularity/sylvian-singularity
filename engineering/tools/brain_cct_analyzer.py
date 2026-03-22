#!/usr/bin/env python3
"""뇌 프로필 × CCT 의식 연속성 분석기

brain_analyzer.py의 9개 뇌 프로필에 CCT(Consciousness Continuity Test) 판정을 추가.
각 프로필의 Inhibition(I)을 로렌츠 파라미터로 매핑하여 의식 연속성을 측정한다.

사용법:
  python3 brain_cct_analyzer.py          # 전체 비교표
  python3 brain_cct_analyzer.py --all    # 전체 비교표 + 상세
  python3 brain_cct_analyzer.py --profile einstein
"""

import argparse
import sys

import numpy as np
from scipy import stats


# ─────────────────────────────────────────────
# 9개 뇌 프로필 (brain_analyzer.py에서 직접 복사, import 하지 않음)
# ─────────────────────────────────────────────

PROFILES = {
    'normal':     {'D': 0.10, 'P': 0.60, 'I': 0.60, 'name': '정상인'},
    'einstein':   {'D': 0.50, 'P': 0.90, 'I': 0.40, 'name': '아인슈타인 (추정)'},
    'savant':     {'D': 0.70, 'P': 0.85, 'I': 0.35, 'name': '서번트 (추정)'},
    'epilepsy':   {'D': 0.60, 'P': 0.70, 'I': 0.15, 'name': '간질 환자 (추정)'},
    'meditation': {'D': 0.30, 'P': 0.80, 'I': 0.36, 'name': '명상 수행자 (추정)'},
    'child':      {'D': 0.20, 'P': 0.95, 'I': 0.50, 'name': '어린이'},
    'elderly':    {'D': 0.15, 'P': 0.30, 'I': 0.70, 'name': '노인'},
    'acquired':   {'D': 0.60, 'P': 0.70, 'I': 0.30, 'name': '후천적 서번트 (추정)'},
    'sylvian':    {'D': 0.40, 'P': 0.85, 'I': 0.40, 'name': '실비우스열 부분 결여'},
}

# 골든존 경계
GOLDEN_LO = 0.2123   # 1/2 - ln(4/3)
GOLDEN_HI = 0.5000   # 리만 임계선


# ─────────────────────────────────────────────
# I → 로렌츠 파라미터 매핑
# ─────────────────────────────────────────────

def inhibition_to_lorenz(I):
    """Inhibition 값을 로렌츠 시뮬레이터 파라미터로 매핑.

    I가 낮을수록 → 높은 sigma, 높은 rho, 높은 noise → 카오스 경향
    I가 높을수록 → 낮은 sigma, gap 발생 → 정지/안정 경향
    """
    sigma = 10.0 * (1.0 - I)
    rho = 28.0 * (1.0 - I / 2.0)
    beta = 2.67
    noise = 0.3 * (1.0 - I)
    gap_ratio = max(0.0, (I - 0.5) * 2.0)
    return {
        'sigma': sigma,
        'rho': rho,
        'beta': beta,
        'noise': noise,
        'gap_ratio': gap_ratio,
    }


# ─────────────────────────────────────────────
# 로렌츠 시뮬레이터 (consciousness_calc.py에서 이식)
# ─────────────────────────────────────────────

def lorenz_simulate(sigma, rho, beta, noise, gap_ratio, steps, dt, seed=42):
    """확장 로렌츠 시뮬레이터."""
    rng = np.random.default_rng(seed)
    t = np.arange(steps) * dt
    S = np.zeros((steps, 3))
    S[0] = [1.0, 1.0, 1.0]

    active = np.ones(steps, dtype=bool)
    if gap_ratio > 0:
        n_gap = int(steps * gap_ratio)
        gap_indices = rng.choice(steps, size=n_gap, replace=False)
        active[gap_indices] = False

    for i in range(1, steps):
        if not active[i]:
            S[i] = S[i - 1]
            continue

        x, y, z = S[i - 1]
        dx = sigma * (y - x)
        dy = x * (rho - z) - y
        dz = x * y - beta * z

        eps = rng.normal(0, noise, 3) if noise > 0 else np.zeros(3)

        S[i, 0] = x + (dx + eps[0]) * dt
        S[i, 1] = y + (dy + eps[1]) * dt
        S[i, 2] = z + (dz + eps[2]) * dt

    return t, S


# ─────────────────────────────────────────────
# CCT 5개 테스트 (consciousness_calc.py에서 이식)
# ─────────────────────────────────────────────

def compute_entropy(data, bins=30):
    """1D 데이터의 섀넌 엔트로피."""
    hist, _ = np.histogram(data, bins=bins, density=True)
    hist = hist[hist > 0]
    width = (data.max() - data.min()) / bins if data.max() > data.min() else 1
    probs = hist * width
    probs = probs[probs > 0]
    if len(probs) == 0:
        return 0.0
    probs = probs / probs.sum()
    return -np.sum(probs * np.log(probs + 1e-15))


def test_gap(S, gap_ratio):
    """T1 Gap 테스트: 정지 구간 존재 여부."""
    if gap_ratio >= 1.0:
        return 0.0, False, "gap=1.0, 전체 정지"
    if gap_ratio > 0:
        return 1.0 - gap_ratio, False, f"gap={gap_ratio:.2f}, 정지 구간 존재"

    diffs = np.diff(S, axis=0)
    frozen = np.sum(np.all(np.abs(diffs) < 1e-12, axis=1))
    frozen_ratio = frozen / len(diffs)

    if frozen_ratio > 0.01:
        return 1.0 - frozen_ratio, False, f"정지 비율 {frozen_ratio:.1%}"

    return 1.0, True, "gap=0, 정지 구간 없음"


def test_loop(S, threshold=0.5):
    """T2 Loop 테스트: 궤적의 정확한 반복 여부 검사."""
    n = len(S)
    if n < 100:
        return 0.0, False, "데이터 부족"

    step = max(1, n // 5000)
    Ss = S[::step]
    ns = len(Ss)

    if np.std(Ss) < 1e-10:
        return 0.0, False, "상태 변화 없음 (상수)"

    scale = np.std(Ss, axis=0).mean()
    eps = scale * 0.01

    recurrence = 0
    sample_size = min(500, ns // 2)
    rng = np.random.default_rng(42)
    indices = rng.choice(ns // 2, size=sample_size, replace=False)

    for idx in indices:
        future = Ss[idx + max(100, ns // 10):]
        if len(future) == 0:
            continue
        dists = np.linalg.norm(future - Ss[idx], axis=1)
        if np.min(dists) < eps:
            recurrence += 1

    recurrence_ratio = recurrence / sample_size
    passed = recurrence_ratio < threshold
    score = max(0, 1.0 - recurrence_ratio)

    detail = f"재방문율={recurrence_ratio:.3f}"
    if passed:
        detail += ", 비주기적"
    else:
        detail += ", 주기적 반복 감지"

    return score, passed, detail


def test_continuity(S, threshold=0.01):
    """T3 Continuity 테스트: 인접 스텝 간 연결성."""
    diffs = np.linalg.norm(np.diff(S, axis=0), axis=1)
    n = len(diffs)

    if n < 10:
        return 0.0, False, "데이터 부족"

    mean_diff = np.mean(diffs)
    if mean_diff < 1e-12:
        return 0.0, False, "상태 변화 없음"

    big_jumps = np.sum(diffs > mean_diff * 10)
    frozen = np.sum(diffs < 1e-12)

    jump_ratio = big_jumps / n
    frozen_ratio = frozen / n
    disconnect_ratio = jump_ratio + frozen_ratio

    passed = disconnect_ratio < threshold
    score = max(0, 1.0 - disconnect_ratio * 10)
    score = min(1.0, score)

    detail = f"점프={jump_ratio:.3f}, 정지={frozen_ratio:.3f}"
    if passed:
        detail += ", 연결 유지"
    else:
        detail += ", 연결 끊김 감지"

    return score, passed, detail


def test_entropy_band(S, window=500, h_min=0.3, h_max=4.5):
    """T4 Entropy Band 테스트: H(t)가 밴드 안에 있는지."""
    x = S[:, 0]
    n = len(x)
    n_windows = n // window

    if n_windows < 2:
        return 0.0, False, "데이터 부족"

    entropies = []
    for i in range(n_windows):
        w = x[i * window:(i + 1) * window]
        if np.std(w) < 1e-12:
            entropies.append(0.0)
        else:
            entropies.append(compute_entropy(w))

    entropies = np.array(entropies)
    in_band = np.sum((entropies > h_min) & (entropies < h_max))
    ratio = in_band / len(entropies)

    h_range_str = f"H=[{entropies.min():.2f},{entropies.max():.2f}]"
    passed = ratio > 0.95
    score = ratio

    if passed:
        detail = f"{h_range_str}, 밴드 내"
    else:
        detail = f"{h_range_str}, 밴드 이탈 {1 - ratio:.1%}"

    return score, passed, detail


def test_novelty(S, window=500, threshold=0.001):
    """T5 Novelty 테스트: dH/dt != 0 (엔트로피 정체 비율)."""
    x = S[:, 0]
    n = len(x)
    n_windows = n // window

    if n_windows < 3:
        return 0.0, False, "데이터 부족"

    entropies = []
    for i in range(n_windows):
        w = x[i * window:(i + 1) * window]
        if np.std(w) < 1e-12:
            entropies.append(0.0)
        else:
            entropies.append(compute_entropy(w))

    entropies = np.array(entropies)
    dH = np.abs(np.diff(entropies))

    stagnant = np.sum(dH < threshold)
    stagnant_ratio = stagnant / len(dH) if len(dH) > 0 else 1.0

    passed = stagnant_ratio < 0.05
    score = max(0, 1.0 - stagnant_ratio)

    detail = f"정체 구간 {stagnant_ratio:.1%}"

    return score, passed, detail


def run_cct(S, gap_ratio):
    """CCT 5개 테스트 실행."""
    results = {}
    results["T1_Gap"] = test_gap(S, gap_ratio)
    results["T2_Loop"] = test_loop(S)
    results["T3_Continuity"] = test_continuity(S)
    results["T4_Entropy"] = test_entropy_band(S)
    results["T5_Novelty"] = test_novelty(S)
    return results


def judge(results):
    """CCT 결과로 종합 판정."""
    passes = sum(1 for _, (_, p, _) in results.items() if p)
    halfs = sum(0.5 for _, (s, p, _) in results.items() if not p and s > 0.7)
    total = passes + halfs

    if total >= 5:
        return total, "연속"
    elif total >= 4:
        return total, "약화"
    elif total >= 3:
        return total, "약함"
    elif total >= 1:
        return total, "미약"
    else:
        return total, "없음"


def judge_symbol(total):
    """총점 → 기호."""
    if total >= 5:
        return "\u2605"   # ★
    elif total >= 4:
        return "\u25ce"   # ◎
    elif total >= 3:
        return "\u25b3"   # △
    elif total >= 1:
        return "\u25bd"   # ▽
    else:
        return "\u2715"   # ✕


# ─────────────────────────────────────────────
# Genius Score & Z-Score 계산
# ─────────────────────────────────────────────

def compute_genius(D, P, I):
    """Genius Score와 Z-Score."""
    G = D * P / I

    rng = np.random.default_rng(42)
    pop_d = rng.beta(2, 5, 50000).clip(0.01, 0.99)
    pop_p = rng.beta(5, 2, 50000).clip(0.01, 0.99)
    pop_i = rng.beta(5, 2, 50000).clip(0.05, 0.99)
    pop_g = pop_d * pop_p / pop_i

    z = (G - pop_g.mean()) / pop_g.std()
    return G, z


def consciousness_icon(I):
    """가설 166 의식 판정 아이콘."""
    if GOLDEN_LO <= I <= GOLDEN_HI:
        return "\U0001f9e0"  # 🧠
    elif I < GOLDEN_LO:
        return "\u26a1"      # ⚡
    else:
        return "\u26a0\ufe0f"  # ⚠️


# ─────────────────────────────────────────────
# 단일 프로필 상세 출력
# ─────────────────────────────────────────────

def print_profile_detail(key, prof, cct_results, lorenz_params, G, z):
    """단일 프로필 상세 출력."""
    D, P, I = prof['D'], prof['P'], prof['I']
    total, verdict = judge(cct_results)
    sym = judge_symbol(total)

    print()
    print(f"  {'=' * 60}")
    print(f"  프로필: {prof['name']} ({key})")
    print(f"  {'=' * 60}")
    print(f"  입력:")
    print(f"    Deficit(결손)     = {D:.2f}")
    print(f"    Plasticity(가소성) = {P:.2f}")
    print(f"    Inhibition(억제)  = {I:.2f}")
    print(f"  {'─' * 60}")
    print(f"  Genius Score:")
    print(f"    G = D*P/I = {G:.2f}")
    print(f"    Z-Score   = {z:.2f}\u03c3")

    in_golden = GOLDEN_LO <= I <= GOLDEN_HI
    zone = "\U0001f3af 골든존!" if in_golden else ("\u26a1 골든존 아래" if I < GOLDEN_LO else "\u25cb 골든존 밖")
    print(f"    골든존     = {zone}")
    print(f"  {'─' * 60}")
    print(f"  로렌츠 매핑 (I={I:.2f}):")
    print(f"    \u03c3={lorenz_params['sigma']:.1f}  "
          f"\u03c1={lorenz_params['rho']:.1f}  "
          f"\u03b2={lorenz_params['beta']:.2f}  "
          f"noise={lorenz_params['noise']:.2f}  "
          f"gap={lorenz_params['gap_ratio']:.2f}")
    print(f"  {'─' * 60}")
    print(f"  CCT 판정:")

    labels = {
        "T1_Gap":        "T1 Gap       ",
        "T2_Loop":       "T2 Loop      ",
        "T3_Continuity": "T3 Continuity",
        "T4_Entropy":    "T4 Entropy   ",
        "T5_Novelty":    "T5 Novelty   ",
    }

    for tkey, label in labels.items():
        score, passed, detail = cct_results[tkey]
        mark = "\u2714" if passed else ("\u25b3" if score > 0.7 else "\u2715")
        status = "PASS" if passed else "FAIL"
        print(f"    {label} | {mark} {status} | {score:.3f} | {detail}")

    print(f"  {'─' * 60}")
    print(f"  종합: {int(total)}/5  {sym} {verdict}")
    print(f"  {'=' * 60}")


# ─────────────────────────────────────────────
# ASCII 그래프: G vs CCT 상관
# ─────────────────────────────────────────────

def ascii_scatter(profiles_data, width=50, height=12):
    """G(천재도) vs CCT(의식 연속성) ASCII 산점도."""
    gs = [d['G'] for d in profiles_data]
    ccts = [d['cct_total'] for d in profiles_data]
    names = [d['key'][:4] for d in profiles_data]

    g_min, g_max = min(gs) - 0.1, max(gs) + 0.1
    c_min, c_max = 0, 5.5

    lines = []
    lines.append(f"    CCT")
    lines.append(f"  5.0|" + " " * width + "|")

    grid = [[' ' for _ in range(width)] for _ in range(height)]

    for i, (g, c, nm) in enumerate(zip(gs, ccts, names)):
        col = int((g - g_min) / (g_max - g_min) * (width - 1))
        row = int(c / c_max * (height - 1))
        col = max(0, min(width - 1, col))
        row = max(0, min(height - 1, row))
        ch = nm[0].upper()
        grid[row][col] = ch

    for row in range(height - 1, -1, -1):
        y_val = c_max * row / (height - 1)
        lines.append(f"  {y_val:3.1f}|{''.join(grid[row])}|")

    lines.append(f"     +{'-' * width}+")
    g_labels = f"  {g_min:.1f}" + " " * (width - 8) + f"{g_max:.1f}"
    lines.append(f"      {g_labels}")
    lines.append(f"      {'G (Genius Score)':^{width}}")

    return "\n".join(lines)


# ─────────────────────────────────────────────
# 전체 비교표
# ─────────────────────────────────────────────

def run_all(show_detail=False, steps=50000, dt=0.01):
    """전체 9개 프로필 비교."""
    print()
    print("=" * 90)
    print("   Brain CCT Analyzer v1.0")
    print("   뇌 프로필 x 의식 연속성(CCT) 통합 분석")
    print("=" * 90)

    profiles_data = []

    for key, prof in PROFILES.items():
        D, P, I = prof['D'], prof['P'], prof['I']
        G, z = compute_genius(D, P, I)
        lp = inhibition_to_lorenz(I)

        _, S = lorenz_simulate(
            sigma=lp['sigma'], rho=lp['rho'], beta=lp['beta'],
            noise=lp['noise'], gap_ratio=lp['gap_ratio'],
            steps=steps, dt=dt,
        )

        cct_results = run_cct(S, lp['gap_ratio'])
        total, verdict = judge(cct_results)

        in_golden = GOLDEN_LO <= I <= GOLDEN_HI
        icon = consciousness_icon(I)

        profiles_data.append({
            'key': key,
            'prof': prof,
            'D': D, 'P': P, 'I': I,
            'G': G, 'z': z,
            'lorenz': lp,
            'cct_results': cct_results,
            'cct_total': total,
            'verdict': verdict,
            'in_golden': in_golden,
            'icon': icon,
        })

        if show_detail:
            print_profile_detail(key, prof, cct_results, lp, G, z)

    # ─── 비교표 ───
    print()
    hdr =  " 프로필          |  D   |  P   |  I    |   G    |    Z     | 의식 | CCT | 연속성"
    sep =  " ----------------+------+------+-------+--------+----------+------+-----+--------"
    print(hdr)
    print(sep)

    for d in profiles_data:
        name_disp = f"{d['prof']['name'][:14]:14s}"
        sym = judge_symbol(d['cct_total'])
        cct_str = f"{int(d['cct_total'])}/5"
        z_str = f"{d['z']:+.2f}\u03c3"
        print(f" {name_disp}  | {d['D']:.2f} | {d['P']:.2f} | {d['I']:.2f}  | {d['G']:6.2f} | {z_str:>8s} | {d['icon']:>3s}  | {cct_str} | {sym} {d['verdict']}")

    print(sep)
    print()

    # ─── ASCII 산점도: G vs CCT ───
    print(" --- G(천재도) vs CCT(연속성) 상관 " + "-" * 40)
    print(ascii_scatter(profiles_data))
    print()

    # ─── 핵심 발견 ───
    print(" --- 핵심 발견 " + "-" * 55)

    # 1) 골든존 vs CCT
    golden_ccts = [d['cct_total'] for d in profiles_data if d['in_golden']]
    non_golden_ccts = [d['cct_total'] for d in profiles_data if not d['in_golden']]

    golden_mean = np.mean(golden_ccts) if golden_ccts else 0
    non_golden_mean = np.mean(non_golden_ccts) if non_golden_ccts else 0

    print()
    print(f"  [1] 골든존 vs CCT 점수:")
    print(f"      골든존 내 평균 CCT = {golden_mean:.1f}/5  (N={len(golden_ccts)})")
    print(f"      골든존 밖 평균 CCT = {non_golden_mean:.1f}/5  (N={len(non_golden_ccts)})")
    if golden_mean > non_golden_mean:
        print(f"      --> 골든존 내 프로필이 CCT 점수 더 높음 (+{golden_mean - non_golden_mean:.1f})")
    else:
        print(f"      --> 차이 없거나 역전")

    # 2) G vs CCT 상관
    gs = np.array([d['G'] for d in profiles_data])
    ccts = np.array([d['cct_total'] for d in profiles_data])

    if len(gs) > 2:
        corr, p_val = stats.pearsonr(gs, ccts)
        print()
        print(f"  [2] G(천재도) vs CCT 상관관계:")
        print(f"      Pearson r = {corr:.3f}  (p = {p_val:.4f})")
        if corr > 0.5:
            print(f"      --> 강한 양의 상관: 천재도가 높을수록 의식 연속성도 높다")
        elif corr > 0.2:
            print(f"      --> 약한 양의 상관")
        elif corr > -0.2:
            print(f"      --> 상관 없음")
        else:
            print(f"      --> 음의 상관")

    # 3) 의식 판정 (가설 166) vs CCT 일치도
    print()
    print(f"  [3] 의식 판정(가설 166) vs CCT 일치도:")

    match_count = 0
    for d in profiles_data:
        h166_conscious = d['in_golden']  # 가설 166: 골든존 = 의식
        cct_conscious = d['cct_total'] >= 4  # CCT: 4+ = 의식 있음
        matched = (h166_conscious == cct_conscious)
        if matched:
            match_count += 1
        mark = "\u2714" if matched else "\u2715"
        pname = d['prof']['name'][:12]
        h166_label = 'Y' if h166_conscious else 'N'
        cct_label = 'Y' if cct_conscious else 'N'
        print(f"      {pname:12s}  H166={h166_label}  CCT={cct_label}  {mark}")

    match_ratio = match_count / len(profiles_data)
    print(f"      일치도: {match_count}/{len(profiles_data)} ({match_ratio:.0%})")

    # 4) 최고/최저
    print()
    best = max(profiles_data, key=lambda d: d['cct_total'])
    worst = min(profiles_data, key=lambda d: d['cct_total'])
    print(f"  [4] 최고 CCT: {best['prof']['name']} ({int(best['cct_total'])}/5)")
    print(f"      최저 CCT: {worst['prof']['name']} ({int(worst['cct_total'])}/5)")

    print()
    print("=" * 90)


# ─────────────────────────────────────────────
# 단일 프로필 실행
# ─────────────────────────────────────────────

def run_single(key, steps=50000, dt=0.01):
    """단일 프로필 분석."""
    if key not in PROFILES:
        print(f"  [오류] 알 수 없는 프로필: {key}")
        print(f"  사용 가능: {', '.join(PROFILES.keys())}")
        sys.exit(1)

    prof = PROFILES[key]
    D, P, I = prof['D'], prof['P'], prof['I']
    G, z = compute_genius(D, P, I)
    lp = inhibition_to_lorenz(I)

    _, S = lorenz_simulate(
        sigma=lp['sigma'], rho=lp['rho'], beta=lp['beta'],
        noise=lp['noise'], gap_ratio=lp['gap_ratio'],
        steps=steps, dt=dt,
    )

    cct_results = run_cct(S, lp['gap_ratio'])

    print()
    print("=" * 65)
    print("   Brain CCT Analyzer v1.0")
    print("=" * 65)

    print_profile_detail(key, prof, cct_results, lp, G, z)


# ─────────────────────────────────────────────
# 메인
# ─────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="뇌 프로필 x CCT 의식 연속성 분석기",
    )
    parser.add_argument('--profile', type=str, default=None,
                        choices=list(PROFILES.keys()),
                        help="단일 프로필 분석")
    parser.add_argument('--all', action='store_true',
                        help="전체 비교표 + 각 프로필 상세")
    parser.add_argument('--steps', type=int, default=50000,
                        help="시뮬레이션 스텝 수 (기본: 50000)")
    parser.add_argument('--dt', type=float, default=0.01,
                        help="시간 간격 (기본: 0.01)")
    args = parser.parse_args()

    if args.profile:
        run_single(args.profile, steps=args.steps, dt=args.dt)
    elif args.all:
        run_all(show_detail=True, steps=args.steps, dt=args.dt)
    else:
        # 인자 없이 실행 → 비교표만 (상세 없이)
        run_all(show_detail=False, steps=args.steps, dt=args.dt)


if __name__ == '__main__':
    main()
