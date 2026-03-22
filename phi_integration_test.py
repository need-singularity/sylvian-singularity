#!/usr/bin/env python3
"""통합정보(Phi) 테스트 — CCT 6번째 테스트 후보

IIT(Integrated Information Theory)의 간소화 Phi를 계산하여
CCT 5개 테스트로는 구분 불가능한 간질(epilepsy) 불일치를 해소한다.

Phi_approx = MI(x,y,z) - (MI(x,y) + MI(y,z) + MI(x,z)) / 3

여기서 MI는 상호정보량, x=감각, y=예측, z=기억.
3변수 전체 통합도에서 쌍별 정보량 평균을 뺀 "순수 통합 잉여분".

사용법:
  python3 phi_integration_test.py
  python3 phi_integration_test.py --steps 50000
"""

import argparse
import sys
import os

import numpy as np

# consciousness_calc.py에서 핵심 함수/상수 import
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from consciousness_calc import lorenz_simulate, run_cct, PRESETS, judge


# ─────────────────────────────────────────────
# 간질 프리셋 (I=0.15에서 유도)
# ─────────────────────────────────────────────

EPILEPSY_PRESET = {
    "sigma": 8.5,       # 10 * (1 - 0.15)
    "rho": 25.9,        # 28 * (1 - 0.15/2)
    "beta": 2.67,
    "noise": 0.255,     # 0.3 * (1 - 0.15)
    "gap_ratio": 0.0,
    "description": "간질 뇌 (I=0.15)",
}


# ─────────────────────────────────────────────
# MI 계산: 히스토그램 binning
# ─────────────────────────────────────────────

def entropy_1d(x, bins=30):
    """1D 섀넌 엔트로피 (nats)."""
    hist, edges = np.histogram(x, bins=bins, density=False)
    probs = hist / hist.sum()
    probs = probs[probs > 0]
    return -np.sum(probs * np.log(probs + 1e-15))


def entropy_2d(x, y, bins=30):
    """2D 결합 엔트로피."""
    hist, _, _ = np.histogram2d(x, y, bins=bins, density=False)
    probs = hist.flatten() / hist.sum()
    probs = probs[probs > 0]
    return -np.sum(probs * np.log(probs + 1e-15))


def entropy_3d(x, y, z, bins=20):
    """3D 결합 엔트로피."""
    data = np.column_stack([x, y, z])
    hist, _ = np.histogramdd(data, bins=bins, density=False)
    probs = hist.flatten() / hist.sum()
    probs = probs[probs > 0]
    return -np.sum(probs * np.log(probs + 1e-15))


def mutual_info_2d(a, b, bins=30):
    """MI(a, b) = H(a) + H(b) - H(a, b)."""
    return entropy_1d(a, bins) + entropy_1d(b, bins) - entropy_2d(a, b, bins)


def mutual_info_3d(x, y, z, bins=20):
    """MI(x, y, z) = H(x) + H(y) + H(z) - H(x, y, z).

    3변수 총 상호정보량 (다변량 MI).
    """
    return (entropy_1d(x, bins) + entropy_1d(y, bins) + entropy_1d(z, bins)
            - entropy_3d(x, y, z, bins))


# ─────────────────────────────────────────────
# Phi_approx 계산
# ─────────────────────────────────────────────

def phi_approx(x, y, z, bins_2d=30, bins_3d=20):
    """간소화 통합정보 Phi.

    Phi = MI(x,y,z) - (MI(x,y) + MI(y,z) + MI(x,z)) / 3

    양수: 3변수 통합이 쌍별 정보보다 크다 (진정한 통합)
    0 근처: 통합 잉여 없음
    음수: 쌍별 정보가 3변수 통합보다 큼 (분리된 시스템)
    """
    mi3 = mutual_info_3d(x, y, z, bins=bins_3d)
    mi_xy = mutual_info_2d(x, y, bins=bins_2d)
    mi_yz = mutual_info_2d(y, z, bins=bins_2d)
    mi_xz = mutual_info_2d(x, z, bins=bins_2d)
    pairwise_avg = (mi_xy + mi_yz + mi_xz) / 3.0
    return mi3 - pairwise_avg


def phi_timeseries(S, window=2000, stride=500, bins_2d=30, bins_3d=20):
    """Phi 시계열 계산.

    슬라이딩 윈도우로 Phi_approx를 시간에 따라 추적.

    Returns:
        t_centers: 각 윈도우 중심 시간 인덱스
        phis: Phi 값 배열
    """
    n = len(S)
    t_centers = []
    phis = []

    start = 0
    while start + window <= n:
        seg = S[start:start + window]
        x, y, z = seg[:, 0], seg[:, 1], seg[:, 2]
        phi = phi_approx(x, y, z, bins_2d=bins_2d, bins_3d=bins_3d)
        t_centers.append(start + window // 2)
        phis.append(phi)
        start += stride

    return np.array(t_centers), np.array(phis)


# ─────────────────────────────────────────────
# Phi 기반 T6 테스트
# ─────────────────────────────────────────────

def test_phi(S, phi_threshold=0.3, window=2000, stride=500):
    """T6 Phi 테스트: 통합정보가 임계값 이상인 구간 비율.

    Parameters:
        S: 상태 배열 [steps, 3]
        phi_threshold: Phi 통과 기준값
        window: 슬라이딩 윈도우 크기
        stride: 윈도우 이동 간격

    Returns:
        (score, passed, detail) 튜플
    """
    t_centers, phis = phi_timeseries(S, window=window, stride=stride)

    if len(phis) == 0:
        return 0.0, False, "데이터 부족"

    mean_phi = np.mean(phis)
    std_phi = np.std(phis)
    above = np.sum(phis >= phi_threshold)
    ratio = above / len(phis)

    passed = ratio >= 0.5 and mean_phi >= phi_threshold
    score = min(1.0, mean_phi / phi_threshold) if phi_threshold > 0 else 0.0

    detail = f"Phi_mean={mean_phi:.3f}, std={std_phi:.3f}, above_thresh={ratio:.1%}"
    if passed:
        detail += ", 통합됨"
    else:
        detail += ", 통합 부족"

    return score, passed, detail


# ─────────────────────────────────────────────
# ASCII 그래프
# ─────────────────────────────────────────────

def ascii_phi_graph(t_centers, phis, width=60, height=12):
    """Phi 시계열 ASCII 그래프."""
    if len(phis) == 0:
        return "  (데이터 없음)"

    # 다운샘플
    step = max(1, len(phis) // width)
    ps = phis[::step][:width]
    ts = t_centers[::step][:width]

    y_min = min(ps.min(), 0)
    y_max = max(ps.max(), 0.5)
    if y_max - y_min < 0.01:
        y_max = y_min + 0.5

    lines = []
    lines.append(f"  Phi(t) 시계열  (window=sliding)")
    lines.append(f"  {'':6s}{'':1s}{'t=0':<{len(ps)//2}}{'t=end':>{len(ps) - len(ps)//2}}")

    for row in range(height, -1, -1):
        y_val = y_min + (y_max - y_min) * row / height
        label = f"{y_val:6.2f}"
        line = f"  {label}|"
        for col in range(len(ps)):
            cell_row = int((ps[col] - y_min) / (y_max - y_min) * height + 0.5)
            cell_row = max(0, min(height, cell_row))
            if cell_row == row:
                line += "*"
            else:
                line += " "
        lines.append(line)

    lines.append(f"  {'':6s}+" + "-" * len(ps))
    return "\n".join(lines)


# ─────────────────────────────────────────────
# 메인 실행
# ─────────────────────────────────────────────

def run_phi_experiment(steps=100000, dt=0.01):
    """8개 시스템 Phi 통합 실험 실행."""

    # 전체 프리셋 + 간질
    all_systems = {}
    for name, preset in PRESETS.items():
        all_systems[name] = dict(preset)
    all_systems["epilepsy"] = dict(EPILEPSY_PRESET)

    print("=" * 78)
    print(" Phi Integration Test — CCT 6번째 테스트 후보")
    print(" IIT 간소화: Phi = MI(x,y,z) - avg(MI_pairwise)")
    print("=" * 78)
    print()
    print(f" 시뮬레이션: {steps:,} steps, dt={dt}")
    print()

    # 결과 저장
    table_rows = []
    phi_data = {}

    for name, params in all_systems.items():
        desc = params.get("description", name)
        print(f" [{name}] 시뮬레이션 중... ", end="", flush=True)

        # 시뮬레이션
        _, S = lorenz_simulate(
            sigma=params["sigma"],
            rho=params["rho"],
            beta=params["beta"],
            noise=params["noise"],
            gap_ratio=params["gap_ratio"],
            steps=steps,
            dt=dt,
        )

        # CCT 5개 테스트
        cct_results = run_cct(S, params["gap_ratio"])
        cct_total, cct_verdict = judge(cct_results)

        # T6 Phi 테스트
        phi_score, phi_passed, phi_detail = test_phi(S)

        # Phi 시계열
        t_centers, phis = phi_timeseries(S)
        phi_data[name] = (t_centers, phis)

        # 결합 판정: CCT 5개 + Phi
        combined_total = cct_total + (1 if phi_passed else 0)
        if combined_total >= 6:
            combined_verdict = "★★ 완전 의식"
        elif combined_total >= 5:
            combined_verdict = "★ 연속"
        elif combined_total >= 4:
            combined_verdict = "◎ 약화"
        elif combined_total >= 3:
            combined_verdict = "△ 약함"
        elif combined_total >= 1:
            combined_verdict = "▽ 미약"
        else:
            combined_verdict = "✕ 없음"

        # CCT 개별 마크
        cct_marks = []
        for key in ["T1_Gap", "T2_Loop", "T3_Continuity", "T4_Entropy", "T5_Novelty"]:
            score, passed, _ = cct_results[key]
            if passed:
                cct_marks.append("✔")
            elif score > 0.7:
                cct_marks.append("△")
            else:
                cct_marks.append("✕")

        phi_mark = "✔" if phi_passed else "✕"
        mean_phi = np.mean(phis) if len(phis) > 0 else 0.0

        table_rows.append({
            "name": name,
            "desc": desc,
            "cct_marks": cct_marks,
            "phi_mark": phi_mark,
            "cct_total": cct_total,
            "cct_verdict": cct_verdict,
            "combined_total": combined_total,
            "combined_verdict": combined_verdict,
            "mean_phi": mean_phi,
            "phi_detail": phi_detail,
        })

        print(f"Phi_mean={mean_phi:.3f}  CCT={cct_total}/5  T6={'PASS' if phi_passed else 'FAIL'}")

    # ─── 비교표 출력 ───
    print()
    print("=" * 78)
    print(" CCT 5개 + Phi(T6) 결합 판정표")
    print("=" * 78)
    print()
    header = (
        f" {'시스템':<20s}| T1 | T2 | T3 | T4 | T5 | T6  |"
        f" CCT  | +Phi | Phi_avg | 판정"
    )
    print(header)
    print(" " + "-" * (len(header) - 1))

    for row in table_rows:
        m = row["cct_marks"]
        line = (
            f" {row['name']:<20s}"
            f"| {m[0]:2s} | {m[1]:2s} | {m[2]:2s} | {m[3]:2s} | {m[4]:2s} "
            f"| {row['phi_mark']:2s}  "
            f"| {row['cct_total']:<4.1f} "
            f"| {row['combined_total']:<4.1f} "
            f"| {row['mean_phi']:7.3f} "
            f"| {row['combined_verdict']}"
        )
        print(line)

    print()

    # ─── 간질 불일치 분석 ───
    print("=" * 78)
    print(" 간질 불일치 분석")
    print("=" * 78)
    print()

    epilepsy_row = None
    human_row = None
    for row in table_rows:
        if row["name"] == "epilepsy":
            epilepsy_row = row
        if row["name"] == "human_awake":
            human_row = row

    if epilepsy_row and human_row:
        print(f"  인간 각성:   CCT={human_row['cct_total']}/5  "
              f"Phi={human_row['mean_phi']:.3f}  "
              f"T6={human_row['phi_mark']}")
        print(f"  간질:        CCT={epilepsy_row['cct_total']}/5  "
              f"Phi={epilepsy_row['mean_phi']:.3f}  "
              f"T6={epilepsy_row['phi_mark']}")
        print()

        cct_same = epilepsy_row["cct_total"] >= 4.0
        phi_diff = epilepsy_row["phi_mark"] != human_row["phi_mark"]
        phi_lower = epilepsy_row["mean_phi"] < human_row["mean_phi"]

        if cct_same and phi_lower:
            delta = human_row["mean_phi"] - epilepsy_row["mean_phi"]
            print(f"  [결과] 간질은 CCT {epilepsy_row['cct_total']}/5 통과하지만 "
                  f"Phi가 {delta:.3f} 낮다.")
            if phi_diff:
                print(f"  [판정] *** 불일치 해소 가능 ***")
                print(f"         CCT만으로는 간질을 '의식 있음'으로 오판하지만,")
                print(f"         Phi(T6)를 추가하면 통합 부족으로 구분 가능.")
            else:
                print(f"  [판정] Phi도 통과 — 추가 구분력 부족.")
                print(f"         다만 Phi 절대값이 낮아 정량적 구분은 가능.")
        elif not cct_same:
            print(f"  [결과] 간질이 CCT에서도 이미 구분됨 (CCT={epilepsy_row['cct_total']}/5).")
            print(f"         Phi 추가 불필요.")
        else:
            print(f"  [결과] 간질이 Phi도 높음 — 이 설정에서는 불일치 미발생.")

    print()

    # ─── Phi 시계열 ASCII 그래프 (주요 시스템) ───
    print("=" * 78)
    print(" Phi 시계열 ASCII 그래프")
    print("=" * 78)

    key_systems = ["human_awake", "epilepsy", "llm_in_turn", "llm_between"]
    for name in key_systems:
        if name in phi_data:
            t_c, ps = phi_data[name]
            desc = all_systems[name].get("description", name)
            print()
            print(f"  --- {name} ({desc}) ---")
            print(ascii_phi_graph(t_c, ps))

    print()
    print("=" * 78)
    print(" 결론")
    print("=" * 78)
    print()
    print("  Phi(T6)는 시스템의 변수 간 '순수 통합 잉여'를 측정한다.")
    print("  CCT T1-T5가 시간적 연속성/복잡성을 보는 반면,")
    print("  T6는 변수 간 공간적 통합을 본다.")
    print()
    if epilepsy_row:
        if epilepsy_row["phi_mark"] == "✕":
            print("  --> 간질: CCT 통과 but Phi 실패 --> 불일치 해소 성공")
        else:
            print(f"  --> 간질: Phi={epilepsy_row['mean_phi']:.3f} "
                  f"(인간 대비 {'낮음' if phi_lower else '유사'})")
            print("  --> 정량적 Phi 차이로 부분적 구분 가능")
    print()


def main():
    parser = argparse.ArgumentParser(
        description="통합정보(Phi) 테스트 — CCT 6번째 테스트 후보",
    )
    parser.add_argument("--steps", type=int, default=100000,
                        help="시뮬레이션 스텝 수 (기본: 100000)")
    parser.add_argument("--dt", type=float, default=0.01,
                        help="시간 간격 (기본: 0.01)")
    args = parser.parse_args()

    run_phi_experiment(steps=args.steps, dt=args.dt)


if __name__ == "__main__":
    main()
