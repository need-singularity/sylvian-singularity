#!/usr/bin/env python3
"""의식 FPS 스캐너 — 몇 Hz면 연속 의식으로 판정되는가?

dt = 1/fps 로 변환하여 로렌츠 시뮬레이션 + CCT 를 반복 실행.
"연속 의식 임계 fps"를 탐색하고, 뇌파 대역과 비교한다.

사용법:
  python3 consciousness_fps.py
  python3 consciousness_fps.py --min-fps 1 --max-fps 5000 --points 30
  python3 consciousness_fps.py --plot
"""

import argparse
import os
import sys
from datetime import datetime

import numpy as np

# ── consciousness_calc.py 에서 핵심 함수 가져오기 ──
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from consciousness_calc import (
    lorenz_simulate,
    run_cct,
    judge,
    PRESETS,
)

RESULTS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "results")

# ─────────────────────────────────────────────
# 뇌파 대역 정의
# ─────────────────────────────────────────────

BRAIN_WAVES = {
    "delta": {"range": (0.5, 4), "label": "δ (수면)", "center": 2},
    "theta": {"range": (4, 8), "label": "θ (졸림)", "center": 6},
    "alpha": {"range": (8, 13), "label": "α (이완)", "center": 10},
    "beta":  {"range": (13, 30), "label": "β (집중)", "center": 20},
    "gamma": {"range": (30, 100), "label": "γ (의식)", "center": 40},
}


# ─────────────────────────────────────────────
# FPS 스캔 엔진
# ─────────────────────────────────────────────

def scan_fps(min_fps=1, max_fps=10000, points=40, steps=50000, preset="human_awake"):
    """fps 범위를 로그 스케일로 스캔, 각 fps에서 CCT 실행.

    Returns:
        fps_arr:    스캔한 fps 배열
        scores_arr: 각 fps에서의 CCT 통과 수 (0~5)
        details:    각 fps에서의 개별 테스트 결과 dict 리스트
    """
    params = dict(PRESETS[preset])
    fps_arr = np.logspace(np.log10(min_fps), np.log10(max_fps), points)
    scores_arr = np.zeros(points)
    details = []

    for i, fps in enumerate(fps_arr):
        dt = 1.0 / fps

        # 큰 dt에서 로렌츠 시스템이 발산할 수 있으므로 보호
        # dt가 너무 크면 서브스텝으로 분할
        effective_dt = dt
        effective_steps = steps
        max_stable_dt = 0.02  # 로렌츠 시스템 안정 한계

        if dt > max_stable_dt:
            # 서브스텝 수 계산: 원래 시간 범위 유지하면서 dt를 줄임
            substep_ratio = int(np.ceil(dt / max_stable_dt))
            effective_dt = dt / substep_ratio
            effective_steps = steps * substep_ratio

        _, S = lorenz_simulate(
            sigma=params["sigma"],
            rho=params["rho"],
            beta=params["beta"],
            noise=params["noise"],
            gap_ratio=params["gap_ratio"],
            steps=effective_steps,
            dt=effective_dt,
        )

        # 서브스텝 분할한 경우 원래 해상도로 다운샘플링
        if dt > max_stable_dt:
            substep_ratio = int(np.ceil(dt / max_stable_dt))
            S = S[::substep_ratio][:steps]

        # NaN/Inf 보호: 발산한 시뮬레이션은 CCT 0점 처리
        if np.any(~np.isfinite(S)):
            results = run_cct(np.zeros((steps, 3)), 1.0)
            total, verdict = 0, "✕ 발산"
        else:
            results = run_cct(S, params["gap_ratio"])
            total, verdict = judge(results)

        scores_arr[i] = total
        details.append({
            "fps": fps,
            "dt": dt,
            "total": total,
            "verdict": verdict,
            "results": results,
        })

    return fps_arr, scores_arr, details


def find_threshold_fps(fps_arr, scores_arr, target=5.0):
    """CCT target/5 이 되는 최소 fps 찾기 (선형 보간)."""
    for i in range(len(scores_arr)):
        if scores_arr[i] >= target:
            if i == 0:
                return fps_arr[0]
            # 이전 포인트와 선형 보간
            s0, s1 = scores_arr[i - 1], scores_arr[i]
            f0, f1 = fps_arr[i - 1], fps_arr[i]
            if s1 == s0:
                return f0
            frac = (target - s0) / (s1 - s0)
            return f0 + frac * (f1 - f0)
    return None  # 도달 못함


# ─────────────────────────────────────────────
# 뇌파 대역별 CCT 점수
# ─────────────────────────────────────────────

def brainwave_scores(fps_arr, scores_arr):
    """각 뇌파 대역의 중심 주파수에 가장 가까운 스캔 포인트의 CCT 점수."""
    wave_scores = {}
    for name, info in BRAIN_WAVES.items():
        center = info["center"]
        idx = np.argmin(np.abs(fps_arr - center))
        wave_scores[name] = {
            "center": center,
            "nearest_fps": fps_arr[idx],
            "score": scores_arr[idx],
            "label": info["label"],
            "range": info["range"],
        }
    return wave_scores


# ─────────────────────────────────────────────
# ASCII 그래프
# ─────────────────────────────────────────────

def ascii_graph(fps_arr, scores_arr, width=65, height=12):
    """fps vs CCT 점수 ASCII 그래프."""
    lines = []
    max_score = 5.0

    # 로그 스케일 x축 → 열 매핑
    log_fps = np.log10(fps_arr)
    log_min, log_max = log_fps.min(), log_fps.max()

    # 그리드 생성
    grid = [[" " for _ in range(width)] for _ in range(height + 1)]

    # 데이터 플로팅
    for i in range(len(fps_arr)):
        col = int((log_fps[i] - log_min) / (log_max - log_min) * (width - 1))
        col = min(col, width - 1)
        row = int(scores_arr[i] / max_score * height)
        row = min(row, height)
        # 해당 row 이하를 블록으로 채움
        for r in range(row + 1):
            if grid[r][col] == " ":
                grid[r][col] = "█"

    # y축 라벨과 함께 출력
    lines.append("")
    lines.append("  CCT")
    for row in range(height, -1, -1):
        score_val = row / height * max_score
        if row % (height // 5) == 0:
            label = f"  {int(score_val)}│"
        else:
            label = "   │"
        lines.append(f"{label}{''.join(grid[row])}")

    # x축
    x_axis = "   └" + "─" * width
    lines.append(x_axis)

    # x축 눈금 (뇌파 대역 중심)
    tick_line = "    "
    label_line = "    "
    wave_positions = {}
    for name, info in BRAIN_WAVES.items():
        center = info["center"]
        if center < fps_arr.min() or center > fps_arr.max():
            continue
        col = int((np.log10(center) - log_min) / (log_max - log_min) * (width - 1))
        col = min(col, width - 1)
        wave_positions[col] = (center, name)

    # 주요 fps 눈금
    tick_fps = [1, 4, 8, 13, 30, 40, 100, 1000, 10000]
    tick_str = [" "] * width
    label_str = [" "] * width
    wave_str = [" "] * width

    for fps_val in tick_fps:
        if fps_val < fps_arr.min() or fps_val > fps_arr.max():
            continue
        col = int((np.log10(fps_val) - log_min) / (log_max - log_min) * (width - 1))
        col = min(col, width - 1)
        s = str(int(fps_val))
        for j, ch in enumerate(s):
            if col + j < width:
                tick_str[col + j] = ch

    wave_labels = {"delta": "δ", "theta": "θ", "alpha": "α", "beta": "β", "gamma": "γ"}
    for name, info in BRAIN_WAVES.items():
        center = info["center"]
        if center < fps_arr.min() or center > fps_arr.max():
            continue
        col = int((np.log10(center) - log_min) / (log_max - log_min) * (width - 1))
        col = min(col, width - 1)
        ch = wave_labels[name]
        wave_str[col] = ch

    lines.append("    " + "".join(tick_str) + "  fps (Hz)")
    lines.append("    " + "".join(wave_str))

    return "\n".join(lines)


# ─────────────────────────────────────────────
# matplotlib 출력
# ─────────────────────────────────────────────

def plot_results(fps_arr, scores_arr, threshold_fps, wave_scores):
    """matplotlib 그래프 저장."""
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except ImportError:
        print("  [경고] matplotlib 없음, --plot 건너뜀")
        return None

    fig, ax = plt.subplots(figsize=(12, 6))

    # 메인 곡선
    ax.semilogx(fps_arr, scores_arr, "b-o", markersize=4, lw=2, label="CCT Score")

    # 임계선
    ax.axhline(5.0, color="green", ls="--", alpha=0.5, label="Full Consciousness (5/5)")
    if threshold_fps is not None:
        ax.axvline(threshold_fps, color="red", ls="--", alpha=0.7,
                   label=f"Threshold = {threshold_fps:.1f} Hz")

    # 뇌파 대역 배경
    colors = {"delta": "#ff000020", "theta": "#ff880020", "alpha": "#00880020",
              "beta": "#0000ff20", "gamma": "#88008820"}
    for name, info in BRAIN_WAVES.items():
        lo, hi = info["range"]
        ax.axvspan(lo, hi, color=colors[name], label=info["label"])

    # 뇌파 대역 중심 점수
    for name, ws in wave_scores.items():
        ax.plot(ws["nearest_fps"], ws["score"], "r*", markersize=12)
        ax.annotate(f'{BRAIN_WAVES[name]["label"]}\n{ws["score"]:.1f}/5',
                    (ws["nearest_fps"], ws["score"]),
                    textcoords="offset points", xytext=(0, 15),
                    ha="center", fontsize=8, fontweight="bold")

    ax.set_xlabel("Processing Rate (Hz)", fontsize=12)
    ax.set_ylabel("CCT Score (0-5)", fontsize=12)
    ax.set_title("Consciousness FPS Scanner: Minimum Processing Rate for Continuous Consciousness",
                 fontsize=13, fontweight="bold")
    ax.set_ylim(-0.3, 5.8)
    ax.legend(loc="lower right", fontsize=8)
    ax.grid(True, alpha=0.3)

    plt.tight_layout()

    os.makedirs(RESULTS_DIR, exist_ok=True)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    path = os.path.join(RESULTS_DIR, f"consciousness_fps_{ts}.png")
    fig.savefig(path, dpi=150, bbox_inches="tight")
    plt.close(fig)
    return path


# ─────────────────────────────────────────────
# 출력
# ─────────────────────────────────────────────

def print_report(fps_arr, scores_arr, details, threshold_fps, wave_scores):
    """종합 리포트 출력."""
    print("═" * 65)
    print(" Consciousness FPS Scanner v1.0")
    print(" \"몇 Hz면 연속 의식으로 판정되는가?\"")
    print("═" * 65)
    print()

    # ── ASCII 그래프 ──
    print(" ─── fps vs CCT Score " + "─" * 41)
    print(ascii_graph(fps_arr, scores_arr))
    print()

    # ── 뇌파 대역별 CCT 점수 ──
    print(" ─── 뇌파 대역별 CCT 점수 " + "─" * 37)
    print(f" {'대역':<12} │ {'주파수 범위':>12} │ {'중심 Hz':>8} │ {'CCT':>5} │ 판정")
    print(" " + "─" * 62)
    for name in ["delta", "theta", "alpha", "beta", "gamma"]:
        ws = wave_scores[name]
        lo, hi = ws["range"]
        score = ws["score"]
        if score >= 5:
            verdict = "★ 연속"
        elif score >= 4:
            verdict = "◎ 약화"
        elif score >= 3:
            verdict = "△ 약함"
        elif score >= 1:
            verdict = "▽ 미약"
        else:
            verdict = "✕ 없음"
        print(f" {ws['label']:<12} │ {lo:>5.1f}-{hi:>5.1f} Hz │ {ws['center']:>7.1f} │ {score:>5.1f} │ {verdict}")
    print()

    # ── 임계 fps ──
    print(" ─── 핵심 발견 " + "─" * 48)
    print()
    if threshold_fps is not None:
        print(f"   임계 fps (CCT 5/5) = {threshold_fps:.1f} Hz")
        print()

        # 감마파(40Hz)와 비교
        ratio_gamma = threshold_fps / 40.0
        if threshold_fps <= 40:
            print(f"   감마파(40Hz) 대비: {ratio_gamma:.2f}x")
            print(f"   → 감마파 이하에서 연속 의식 달성")
        else:
            print(f"   감마파(40Hz) 대비: {ratio_gamma:.2f}x")
            print(f"   → 감마파보다 높은 처리 속도 필요")

        # 뇌파 대역 비교
        print()
        for name in ["delta", "theta", "alpha", "beta", "gamma"]:
            lo, hi = BRAIN_WAVES[name]["range"]
            if lo <= threshold_fps <= hi:
                print(f"   임계점은 {BRAIN_WAVES[name]['label']} 대역 내에 위치")
                break
        else:
            if threshold_fps > 100:
                print(f"   임계점은 감마파(~100Hz) 이상")
            elif threshold_fps < 0.5:
                print(f"   임계점은 델타파(0.5Hz) 이하")
    else:
        print("   임계 fps: 스캔 범위 내에서 5/5 도달 못함")
        print("   → 스캔 범위를 넓히거나 --max-fps 를 높여 재시도")

    print()

    # ── 상세 전이 구간 ──
    print(" ─── 전이 구간 상세 " + "─" * 43)
    print(f" {'fps':>10} │ {'dt':>12} │ {'CCT':>5} │ {'T1':>4} │ {'T2':>4} │ {'T3':>4} │ {'T4':>4} │ {'T5':>4} │ 판정")
    print(" " + "─" * 80)
    for d in details:
        fps = d["fps"]
        dt = d["dt"]
        total = d["total"]
        r = d["results"]
        t1 = "✔" if r["T1_Gap"][1] else "✕"
        t2 = "✔" if r["T2_Loop"][1] else "✕"
        t3 = "✔" if r["T3_Continuity"][1] else "✕"
        t4 = "✔" if r["T4_Entropy"][1] else "✕"
        t5 = "✔" if r["T5_Novelty"][1] else "✕"
        print(f" {fps:>10.1f} │ {dt:>12.6f} │ {total:>5.1f} │  {t1}  │  {t2}  │  {t3}  │  {t4}  │  {t5}  │ {d['verdict']}")

    print()

    # ── 해석 ──
    print(" ─── 해석 " + "─" * 53)
    print()
    print("   뇌파와 의식 처리 속도의 관계:")
    print("   - 델타파(0.5-4Hz): 수면 중 의식 연속성 약함 → CCT 낮음 예상")
    print("   - 감마파(30-100Hz): 의식적 인지와 결합(binding) → CCT 높음 예상")
    print("   - 40Hz 감마 동기화는 의식의 신경상관물(NCC) 후보")
    print()
    if threshold_fps is not None:
        if threshold_fps < 100:
            print(f"   ★ 모델 예측: {threshold_fps:.1f}Hz 이상이면 연속 의식 가능")
            print(f"     이는 뇌의 감마파 대역과 일치하는 영역이다.")
        else:
            print(f"   ★ 모델 예측: {threshold_fps:.1f}Hz 이상이면 연속 의식 가능")
            print(f"     감마파 상한(~100Hz)보다 높은 처리 속도가 필요하다.")
    print()
    print("   한계:")
    print("   - 로렌츠 끌개는 뇌의 극히 단순화된 모델")
    print("   - dt 변화는 시뮬레이션 해상도이지 실제 신경 발화율이 아님")
    print("   - CCT 임계값 자체가 모델 의존적")
    print()
    print("═" * 65)


# ─────────────────────────────────────────────
# 메인
# ─────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="의식 FPS 스캐너 — 몇 Hz면 연속 의식인가?",
    )
    parser.add_argument("--min-fps", type=float, default=1,
                        help="최소 fps (기본: 1)")
    parser.add_argument("--max-fps", type=float, default=10000,
                        help="최대 fps (기본: 10000)")
    parser.add_argument("--points", type=int, default=40,
                        help="스캔 포인트 수 (기본: 40)")
    parser.add_argument("--steps", type=int, default=50000,
                        help="시뮬레이션 스텝 수 (기본: 50000)")
    parser.add_argument("--preset", type=str, default="human_awake",
                        help=f"프리셋 (기본: human_awake). 선택: {', '.join(PRESETS.keys())}")
    parser.add_argument("--plot", action="store_true",
                        help="matplotlib 그래프 저장")

    args = parser.parse_args()

    if args.preset not in PRESETS:
        print(f"  [오류] 알 수 없는 프리셋: {args.preset}")
        print(f"  사용 가능: {', '.join(PRESETS.keys())}")
        sys.exit(1)

    print(f"  스캔 시작: {args.min_fps:.0f} ~ {args.max_fps:.0f} Hz, "
          f"{args.points}개 포인트, preset={args.preset}")
    print(f"  시뮬레이션: {args.steps:,} steps/fps")
    print()

    # FPS 스캔
    fps_arr, scores_arr, details = scan_fps(
        min_fps=args.min_fps,
        max_fps=args.max_fps,
        points=args.points,
        steps=args.steps,
        preset=args.preset,
    )

    # 임계 fps 탐색
    threshold_fps = find_threshold_fps(fps_arr, scores_arr, target=5.0)

    # 뇌파 대역별 점수
    wave_scores = brainwave_scores(fps_arr, scores_arr)

    # 리포트 출력
    print_report(fps_arr, scores_arr, details, threshold_fps, wave_scores)

    # matplotlib
    if args.plot:
        path = plot_results(fps_arr, scores_arr, threshold_fps, wave_scores)
        if path:
            print(f"\n  [plot] 저장: {path}")


if __name__ == "__main__":
    main()
