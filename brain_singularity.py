#!/usr/bin/env python3
"""뇌 비정형 구조 통계 시뮬레이터 - 통계적 특이점 탐지"""

import argparse
import os
from datetime import datetime

import numpy as np
from scipy import stats
from scipy.signal import argrelextrema


RESULTS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "results")
LOG_FILE = os.path.join(RESULTS_DIR, "log.md")
SINGULARITY_FILE = os.path.join(RESULTS_DIR, "singularities.md")


def genius_score(deficit, plasticity, inhibition):
    """Genius = Deficit × Plasticity / Inhibition"""
    return deficit * plasticity / inhibition


def simulate_population(n_samples, seed=42):
    """정규분포 기반 모집단 생성"""
    rng = np.random.default_rng(seed)
    deficits = rng.beta(2, 5, n_samples).clip(0.01, 0.99)
    plasticities = rng.beta(5, 2, n_samples).clip(0.01, 0.99)
    inhibitions = rng.beta(5, 2, n_samples).clip(0.05, 0.99)
    scores = genius_score(deficits, plasticities, inhibitions)
    return scores


def find_critical_points(n_points=1000):
    """Deficit 연속 변화 → 임계점(2차 미분 피크) 탐지"""
    deficits = np.linspace(0.01, 0.99, n_points)
    plasticity_mean = 0.7
    inhibition_base = 0.8

    inhibitions = inhibition_base * np.exp(-3 * deficits**2)
    scores = genius_score(deficits, plasticity_mean, inhibitions)

    d1 = np.gradient(scores, deficits)
    d2 = np.gradient(d1, deficits)

    peaks = argrelextrema(np.abs(d2), np.greater, order=20)[0]

    return deficits, scores, d2, peaks


def ascii_chart(deficits, scores, user_deficit, user_score, critical_indices, width=60, height=20):
    """터미널 ASCII 차트"""
    min_s, max_s = scores.min(), scores.max()
    if max_s == min_s:
        max_s = min_s + 1

    chart = [[' ' for _ in range(width)] for _ in range(height)]

    for i in range(width):
        idx = int(i / width * len(scores))
        y = int((scores[idx] - min_s) / (max_s - min_s) * (height - 1))
        y = height - 1 - y
        chart[y][i] = '·'

    for ci in critical_indices:
        x = int(ci / len(deficits) * width)
        x = min(x, width - 1)
        for row in range(height):
            if chart[row][x] == ' ':
                chart[row][x] = '│'

    ux = int(user_deficit / 0.99 * (width - 1))
    ux = min(ux, width - 1)
    uy = int((user_score - min_s) / (max_s - min_s) * (height - 1))
    uy = height - 1 - uy
    uy = max(0, min(uy, height - 1))
    chart[uy][ux] = '★'

    lines = []
    for i, row in enumerate(chart):
        if i == 0:
            label = f"  {max_s:6.2f} ┤"
        elif i == height - 1:
            label = f"  {min_s:6.2f} ┤"
        elif i == height // 2:
            mid = (max_s + min_s) / 2
            label = f"  {mid:6.2f} ┤"
        else:
            label = "         │"
        lines.append(label + ''.join(row))
    lines.append("         └" + "─" * width)
    lines.append(f"         Deficit: 0.0{' ' * (width - 10)}1.0")
    lines.append("")
    lines.append("  · 능력 곡선   │ 임계점   ★ 입력값 위치")

    return '\n'.join(lines)


def ensure_results_dir():
    os.makedirs(RESULTS_DIR, exist_ok=True)
    if not os.path.exists(LOG_FILE):
        with open(LOG_FILE, 'w', encoding='utf-8') as f:
            f.write("# 시뮬레이션 기록\n\n")
            f.write("모든 실행 결과가 시간순으로 누적됩니다.\n\n")
            f.write("---\n\n")
    if not os.path.exists(SINGULARITY_FILE):
        with open(SINGULARITY_FILE, 'w', encoding='utf-8') as f:
            f.write("# ⚡ 통계적 특이점 기록\n\n")
            f.write("Z-Score > 2.0σ 인 특이점만 별도 기록됩니다.\n\n")
            f.write("---\n\n")


def append_to_log(d, p, i, score, z, percentile, phase, phase_icon, crit_low, crit_high, is_singular, chart_text, pop_mean, pop_std, n_samples):
    """매 실행 결과를 log.md에 누적"""
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    singular_tag = " `⚡ 특이점`" if is_singular else ""

    entry = f"""## [{now}]{singular_tag}

| 파라미터 | 값 |
|---|---|
| Deficit(결손) | {d:.2f} |
| Plasticity(가소성) | {p:.2f} |
| Inhibition(억제) | {i:.2f} |

| 결과 | 값 |
|---|---|
| Genius Score | {score:.2f} |
| Z-Score | {z:.2f}σ |
| 백분위 | 상위 {percentile:.2f}% |
| 위상 | {phase_icon} {phase} |
| 임계점 구간 | Deficit {crit_low:.2f} ~ {crit_high:.2f} |

<details>
<summary>능력 곡선</summary>

```
{chart_text}
```

</details>

모집단: n={n_samples:,} / 평균={pop_mean:.2f} / σ={pop_std:.2f}

---

"""
    with open(LOG_FILE, 'a', encoding='utf-8') as f:
        f.write(entry)


def append_to_singularities(d, p, i, score, z, percentile, phase):
    """특이점을 singularities.md에 별도 기록"""
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # 특이점 등급 판정
    if abs(z) > 5:
        grade = "🔴 극단적 특이점"
    elif abs(z) > 3:
        grade = "🟠 강한 특이점"
    else:
        grade = "🟡 특이점"

    entry = f"""## {grade} [{now}]

- **Genius Score: {score:.2f}** | **Z-Score: {z:.2f}σ** | 상위 {percentile:.4f}%
- Deficit={d:.2f} / Plasticity={p:.2f} / Inhibition={i:.2f}
- 위상: {phase}

---

"""
    with open(SINGULARITY_FILE, 'a', encoding='utf-8') as f:
        f.write(entry)


def main():
    parser = argparse.ArgumentParser(description="뇌 비정형 구조 통계 시뮬레이터")
    parser.add_argument('--deficit', type=float, default=0.7, help="구조적 결손 정도 (0.0~1.0)")
    parser.add_argument('--plasticity', type=float, default=0.8, help="신경가소성 계수 (0.0~1.0)")
    parser.add_argument('--inhibition', type=float, default=0.15, help="전두엽 억제 수준 (0.01~1.0)")
    parser.add_argument('--samples', type=int, default=10000, help="시뮬레이션 샘플 수")
    args = parser.parse_args()

    d = np.clip(args.deficit, 0.0, 1.0)
    p = np.clip(args.plasticity, 0.0, 1.0)
    i = np.clip(args.inhibition, 0.01, 1.0)

    # 1. 개인 점수 계산
    score = genius_score(d, p, i)

    # 2. 모집단 시뮬레이션
    pop_scores = simulate_population(args.samples)
    z = (score - pop_scores.mean()) / pop_scores.std()
    percentile = (1 - stats.norm.cdf(z)) * 100

    # 3. 임계점 탐지
    curve_d, curve_s, d2, critical_idx = find_critical_points()

    if len(critical_idx) > 0:
        crit_low = curve_d[critical_idx[0]]
        crit_high = curve_d[critical_idx[-1]] if len(critical_idx) > 1 else crit_low + 0.15
    else:
        crit_low, crit_high = 0.5, 0.7

    # 4. 위상 판정
    if d < crit_low:
        phase = "일반적 범위 (보상 동기 부족)"
        phase_icon = "○"
    elif d > crit_high + 0.1:
        phase = "과도한 결손 (보상 한계 초과)"
        phase_icon = "▼"
    else:
        phase = "임계점 내 (보상적 천재성 구간)"
        phase_icon = "⚡"

    is_singular = abs(z) > 2.0

    # 5. 터미널 출력
    chart_text = ascii_chart(curve_d, curve_s, d, score, critical_idx)

    print()
    print("═" * 50)
    print("   뇌 비정형 구조 특이점 분석")
    print("═" * 50)
    print()
    print(f"  입력 파라미터:")
    print(f"    Deficit(결손)     = {d:.2f}")
    print(f"    Plasticity(가소성) = {p:.2f}")
    print(f"    Inhibition(억제)  = {i:.2f}")
    print()
    print("─" * 50)
    print(f"  Genius Score: {score:.2f}")
    print(f"  Z-Score: {z:.2f}σ  {'⚡ 통계적 특이점!' if is_singular else '○ 정상 범위'}")
    print(f"  백분위: 상위 {percentile:.2f}%")
    print("─" * 50)
    print(f"  임계점 구간: Deficit {crit_low:.2f} ~ {crit_high:.2f}")
    print(f"  위상 판정: {phase_icon} {phase}")
    print("─" * 50)
    print()
    print("  [ 능력 곡선 (Deficit vs Genius Score) ]")
    print()
    print(chart_text)
    print()

    print("─" * 50)
    print(f"  모집단 통계 (n={args.samples:,})")
    print(f"    평균: {pop_scores.mean():.2f}")
    print(f"    표준편차: {pop_scores.std():.2f}")
    print(f"    최소/최대: {pop_scores.min():.2f} / {pop_scores.max():.2f}")
    print("═" * 50)

    # 6. 결과 기록
    ensure_results_dir()
    append_to_log(d, p, i, score, z, percentile, phase, phase_icon,
                  crit_low, crit_high, is_singular, chart_text,
                  pop_scores.mean(), pop_scores.std(), args.samples)

    if is_singular:
        append_to_singularities(d, p, i, score, z, percentile, phase)
        print(f"\n  📁 특이점 기록 → results/singularities.md")

    print(f"  📁 전체 기록 → results/log.md")
    print()


if __name__ == '__main__':
    main()
