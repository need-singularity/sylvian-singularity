#!/usr/bin/env python3
"""반발력장 텐션 분석 — MNIST 입력별 장력 프로파일링

분석 대상:
  1. RepulsionFieldQuad: 4극 반발력장 (내용축 A|G, 구조축 E|F)
  2. SelfReferentialField: 자기참조 반발력장 (장력 수렴 패턴)

분석 항목:
  - 숫자(0-9)별 평균 장력 (내용/구조 축 분리)
  - 장력 분포 ASCII 히스토그램
  - 고장력/저장력 Top-10 샘플
  - 오분류와 장력의 상관관계
  - 숫자 x 숫자 혼동 히트맵 (장력 관련)
  - 자기참조 루프 수렴 속도 (숫자별)
"""

import os
import sys
import time
import math
import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from model_utils import (
    load_mnist, train_and_evaluate, count_params,
)
from model_meta_engine import (
    RepulsionFieldQuad, SelfReferentialField,
    EngineA, EngineE, EngineG, EngineF,
)


# ─────────────────────────────────────────
# ASCII 출력 유틸리티
# ─────────────────────────────────────────

def ascii_bar(value, max_value, width=40, fill='#'):
    """값에 비례하는 ASCII 바."""
    if max_value <= 0:
        return ''
    n = int(round(value / max_value * width))
    n = max(0, min(n, width))
    return fill * n


def ascii_histogram(values, bins=20, width=50, title=''):
    """값 배열의 ASCII 히스토그램."""
    counts, edges = np.histogram(values, bins=bins)
    max_count = max(counts) if len(counts) > 0 else 1
    print(f"\n  {title}")
    print(f"  {'bin range':>20} | {'count':>6} | distribution")
    print(f"  {'─' * 20}─┼─{'─' * 6}─┼─{'─' * width}")
    for i, c in enumerate(counts):
        lo, hi = edges[i], edges[i + 1]
        bar = ascii_bar(c, max_count, width)
        print(f"  {lo:>9.2f} - {hi:<8.2f} | {c:>6d} | {bar}")
    print(f"  {'─' * 20}─┴─{'─' * 6}─┴─{'─' * width}")
    print(f"  total={len(values)}, mean={np.mean(values):.4f}, "
          f"std={np.std(values):.4f}, min={np.min(values):.4f}, max={np.max(values):.4f}")


def ascii_heatmap(matrix, row_labels, col_labels, title='', fmt='.1f'):
    """2D 행렬의 ASCII 히트맵 (밀도 문자 사용)."""
    shades = ' .:-=+*#%@'
    vmin = matrix.min()
    vmax = matrix.max()
    rng = vmax - vmin if vmax > vmin else 1.0

    print(f"\n  {title}")
    # 헤더
    header = '     ' + ''.join(f'{c:>6}' for c in col_labels)
    print(f"  {header}")
    print(f"  {'─' * (5 + 6 * len(col_labels))}")

    for i, row_label in enumerate(row_labels):
        cells = ''
        for j in range(len(col_labels)):
            val = matrix[i, j]
            idx = int((val - vmin) / rng * (len(shades) - 1))
            idx = max(0, min(idx, len(shades) - 1))
            shade = shades[idx]
            cells += f'{val:>5{fmt}} '.replace(f'{val:>5{fmt}}', f'{shade}{val:>4{fmt}} ')
        print(f"  {row_label:>3} | {cells}")

    print(f"  {'─' * (5 + 6 * len(col_labels))}")
    print(f"  shade: [' '=min({vmin:{fmt}})] ... ['@'=max({vmax:{fmt}})]")


def print_header(title):
    print()
    print("=" * 70)
    print(f"  {title}")
    print("=" * 70)


def print_section(title):
    print()
    print(f"  {'─' * 60}")
    print(f"  {title}")
    print(f"  {'─' * 60}")


# ─────────────────────────────────────────
# 텐션 수집기 (per-sample)
# ─────────────────────────────────────────

def collect_quad_tension(model, test_loader):
    """RepulsionFieldQuad에서 per-sample 텐션을 수집.

    모델의 forward를 직접 분해하여 sample별 텐션 벡터를 얻는다.
    Returns:
        dict with keys: labels, preds, t_content, t_structure, t_total, correct
    """
    model.eval()
    all_labels = []
    all_preds = []
    all_t_content = []
    all_t_structure = []

    with torch.no_grad():
        for X, y in test_loader:
            X_flat = X.view(X.size(0), -1)

            # 엔진 출력 직접 계산 (per-sample 텐션 필요)
            out_a = model.engine_a(X_flat)
            out_e = model.engine_e(X_flat)
            out_g = model.engine_g(X_flat)
            out_f = model.engine_f(X_flat)

            # 축별 반발력
            rep_content = out_a - out_g      # (batch, 10)
            rep_structure = out_e - out_f    # (batch, 10)

            # per-sample 텐션 (스칼라)
            t_content = (rep_content ** 2).sum(dim=-1)       # (batch,)
            t_structure = (rep_structure ** 2).sum(dim=-1)   # (batch,)

            # 모델의 실제 출력으로 예측
            output, _ = model(X_flat)
            preds = output.argmax(dim=1)

            all_labels.append(y.numpy())
            all_preds.append(preds.cpu().numpy())
            all_t_content.append(t_content.cpu().numpy())
            all_t_structure.append(t_structure.cpu().numpy())

    labels = np.concatenate(all_labels)
    preds = np.concatenate(all_preds)
    t_content = np.concatenate(all_t_content)
    t_structure = np.concatenate(all_t_structure)
    t_total = np.sqrt(t_content * t_structure)  # 기하평균 (모델과 동일)
    correct = (labels == preds)

    return {
        'labels': labels,
        'preds': preds,
        't_content': t_content,
        't_structure': t_structure,
        't_total': t_total,
        'correct': correct,
    }


def collect_selfref_tension(model, test_loader):
    """SelfReferentialField에서 per-sample 텐션 수렴 패턴을 수집.

    자기참조 루프를 step별로 분해하여 sample별 tension trajectory를 얻는다.
    Returns:
        dict with keys: labels, preds, tensions_per_step, correct
    """
    model.eval()
    all_labels = []
    all_preds = []
    all_tensions_per_step = []  # list of (batch, n_steps+1)

    with torch.no_grad():
        for X, y in test_loader:
            X_flat = X.view(X.size(0), -1)
            batch_size = X_flat.size(0)

            # 두 극의 기본 출력
            out_plus = model.pole_plus(X_flat)
            out_minus = model.pole_minus(X_flat)

            # 초기 반발력과 장력
            repulsion = out_plus - out_minus
            prev_tension = (repulsion ** 2).sum(dim=-1)  # (batch,)

            step_tensions = [prev_tension.cpu().numpy().copy()]
            self_state = torch.zeros(batch_size, out_plus.size(-1), device=X_flat.device)

            for step in range(model.n_steps):
                tension_scalar = prev_tension.unsqueeze(-1)  # (batch, 1)
                if step == 0:
                    tension_delta = torch.zeros_like(tension_scalar)
                else:
                    prev_mean = torch.tensor(step_tensions[-1], device=X_flat.device).unsqueeze(-1)
                    tension_delta = tension_scalar - prev_mean
                step_tensor = torch.full_like(tension_scalar, step / model.n_steps)

                self_input = torch.cat([tension_scalar, tension_delta, step_tensor], dim=-1)
                self_state = model.self_model(self_input)
                influence = model.self_influence(self_state)

                modified_repulsion = repulsion + influence
                prev_tension = (modified_repulsion ** 2).sum(dim=-1)
                step_tensions.append(prev_tension.cpu().numpy().copy())

            # 실제 예측
            output, _ = model(X_flat)
            preds = output.argmax(dim=1)

            # (n_steps+1, batch) -> (batch, n_steps+1)
            tensions_matrix = np.stack(step_tensions, axis=1)  # (batch, n_steps+1)

            all_labels.append(y.numpy())
            all_preds.append(preds.cpu().numpy())
            all_tensions_per_step.append(tensions_matrix)

    labels = np.concatenate(all_labels)
    preds = np.concatenate(all_preds)
    tensions = np.concatenate(all_tensions_per_step, axis=0)  # (N, n_steps+1)
    correct = (labels == preds)

    return {
        'labels': labels,
        'preds': preds,
        'tensions': tensions,  # (N, n_steps+1)
        'correct': correct,
    }


# ─────────────────────────────────────────
# 분석 함수들
# ─────────────────────────────────────────

def analyze_per_digit_tension(data):
    """숫자(0-9)별 평균 텐션 분석."""
    print_section("Per-Digit Average Tension (RepulsionFieldQuad)")

    labels = data['labels']
    t_c = data['t_content']
    t_s = data['t_structure']
    t_t = data['t_total']
    correct = data['correct']

    print(f"\n  {'digit':>5} | {'count':>5} | {'content':>9} | {'structure':>9} | "
          f"{'total':>9} | {'accuracy':>8} | content bar")
    print(f"  {'─' * 5}─┼─{'─' * 5}─┼─{'─' * 9}─┼─{'─' * 9}─┼─"
          f"{'─' * 9}─┼─{'─' * 8}─┼─{'─' * 30}")

    max_tc = 0
    digit_stats = {}
    for d in range(10):
        mask = labels == d
        if mask.sum() == 0:
            continue
        mc = t_c[mask].mean()
        ms = t_s[mask].mean()
        mt = t_t[mask].mean()
        acc = correct[mask].mean()
        digit_stats[d] = {'content': mc, 'structure': ms, 'total': mt, 'acc': acc,
                          'count': mask.sum()}
        max_tc = max(max_tc, mc)

    for d in range(10):
        if d not in digit_stats:
            continue
        s = digit_stats[d]
        bar = ascii_bar(s['content'], max_tc, 30)
        print(f"  {d:>5} | {s['count']:>5} | {s['content']:>9.2f} | {s['structure']:>9.2f} | "
              f"{s['total']:>9.2f} | {s['acc']*100:>7.1f}% | {bar}")

    # 상관관계 요약
    accs = [digit_stats[d]['acc'] for d in range(10)]
    totals = [digit_stats[d]['total'] for d in range(10)]
    corr = np.corrcoef(totals, accs)[0, 1]
    print(f"\n  Correlation(total_tension, accuracy) = {corr:+.4f}")
    if corr < -0.3:
        print(f"  --> High tension correlates with LOWER accuracy (expected: harder inputs)")
    elif corr > 0.3:
        print(f"  --> High tension correlates with HIGHER accuracy (unexpected)")
    else:
        print(f"  --> Weak correlation between tension and accuracy")

    return digit_stats


def analyze_tension_distribution(data):
    """텐션 분포 히스토그램."""
    print_section("Tension Distribution")

    ascii_histogram(data['t_content'], bins=20, width=45,
                    title='Content Tension (A vs G)')
    ascii_histogram(data['t_structure'], bins=20, width=45,
                    title='Structure Tension (E vs F)')
    ascii_histogram(data['t_total'], bins=20, width=45,
                    title='Total Tension (geometric mean)')


def analyze_extreme_samples(data, top_n=10):
    """고장력/저장력 Top-N 샘플."""
    print_section(f"Top-{top_n} Highest and Lowest Tension Samples")

    t_total = data['t_total']
    labels = data['labels']
    preds = data['preds']
    correct = data['correct']
    t_c = data['t_content']
    t_s = data['t_structure']

    # Top highest
    idx_high = np.argsort(t_total)[::-1][:top_n]
    print(f"\n  === Top-{top_n} HIGHEST tension ===")
    print(f"  {'rank':>4} | {'idx':>6} | {'label':>5} | {'pred':>4} | {'ok':>3} | "
          f"{'content':>9} | {'structure':>9} | {'total':>9}")
    print(f"  {'─' * 4}─┼─{'─' * 6}─┼─{'─' * 5}─┼─{'─' * 4}─┼─{'─' * 3}─┼─"
          f"{'─' * 9}─┼─{'─' * 9}─┼─{'─' * 9}")
    for rank, i in enumerate(idx_high, 1):
        ok = 'Y' if correct[i] else 'N'
        print(f"  {rank:>4} | {i:>6} | {labels[i]:>5} | {preds[i]:>4} | {ok:>3} | "
              f"{t_c[i]:>9.2f} | {t_s[i]:>9.2f} | {t_total[i]:>9.2f}")

    # Top lowest
    idx_low = np.argsort(t_total)[:top_n]
    print(f"\n  === Top-{top_n} LOWEST tension ===")
    print(f"  {'rank':>4} | {'idx':>6} | {'label':>5} | {'pred':>4} | {'ok':>3} | "
          f"{'content':>9} | {'structure':>9} | {'total':>9}")
    print(f"  {'─' * 4}─┼─{'─' * 6}─┼─{'─' * 5}─┼─{'─' * 4}─┼─{'─' * 3}─┼─"
          f"{'─' * 9}─┼─{'─' * 9}─┼─{'─' * 9}")
    for rank, i in enumerate(idx_low, 1):
        ok = 'Y' if correct[i] else 'N'
        print(f"  {rank:>4} | {i:>6} | {labels[i]:>5} | {preds[i]:>4} | {ok:>3} | "
              f"{t_c[i]:>9.2f} | {t_s[i]:>9.2f} | {t_total[i]:>9.2f}")

    # 통계 비교
    high_acc = correct[idx_high].mean()
    low_acc = correct[idx_low].mean()
    overall_acc = correct.mean()
    print(f"\n  Accuracy comparison:")
    print(f"    Overall:             {overall_acc * 100:.1f}%")
    print(f"    Top-{top_n} highest tension: {high_acc * 100:.1f}%")
    print(f"    Top-{top_n} lowest tension:  {low_acc * 100:.1f}%")


def analyze_confusion_tension(data):
    """오분류와 텐션의 상관관계 + 혼동 히트맵."""
    print_section("Confusion Analysis: Tension vs Misclassification")

    labels = data['labels']
    preds = data['preds']
    correct = data['correct']
    t_total = data['t_total']

    # 정답 vs 오답 텐션 비교
    t_correct = t_total[correct]
    t_wrong = t_total[~correct]

    print(f"\n  Tension statistics:")
    print(f"  {'group':>15} | {'count':>6} | {'mean':>9} | {'std':>9} | {'median':>9}")
    print(f"  {'─' * 15}─┼─{'─' * 6}─┼─{'─' * 9}─┼─{'─' * 9}─┼─{'─' * 9}")
    print(f"  {'Correct':>15} | {len(t_correct):>6} | {t_correct.mean():>9.2f} | "
          f"{t_correct.std():>9.2f} | {np.median(t_correct):>9.2f}")
    if len(t_wrong) > 0:
        print(f"  {'Misclassified':>15} | {len(t_wrong):>6} | {t_wrong.mean():>9.2f} | "
              f"{t_wrong.std():>9.2f} | {np.median(t_wrong):>9.2f}")
        ratio = t_wrong.mean() / (t_correct.mean() + 1e-8)
        print(f"\n  Misclassified/Correct tension ratio: {ratio:.2f}x")
        if ratio > 1.2:
            print(f"  --> Misclassified samples have HIGHER tension (expected)")
        elif ratio < 0.8:
            print(f"  --> Misclassified samples have LOWER tension (unexpected)")
        else:
            print(f"  --> Similar tension levels")
    else:
        print(f"  {'Misclassified':>15} | {0:>6} | {'N/A':>9} | {'N/A':>9} | {'N/A':>9}")

    # 혼동 행렬 (raw counts)
    confusion = np.zeros((10, 10), dtype=int)
    for l, p in zip(labels, preds):
        confusion[l, p] += 1

    # 혼동 히트맵 (오분류만, 대각선 제외)
    confusion_off = confusion.copy().astype(float)
    np.fill_diagonal(confusion_off, 0)

    digit_labels = [str(d) for d in range(10)]
    ascii_heatmap(confusion_off, digit_labels, digit_labels,
                  title='Confusion Matrix (off-diagonal = misclassifications)',
                  fmt='.0f')

    # 텐션 가중 혼동 히트맵: 오분류 시 평균 텐션
    tension_confusion = np.zeros((10, 10))
    tension_counts = np.zeros((10, 10))
    for i in range(len(labels)):
        if labels[i] != preds[i]:
            tension_confusion[labels[i], preds[i]] += t_total[i]
            tension_counts[labels[i], preds[i]] += 1

    # 평균 텐션 (0으로 나누기 방지)
    with np.errstate(divide='ignore', invalid='ignore'):
        avg_tension_conf = np.where(tension_counts > 0,
                                     tension_confusion / tension_counts, 0)

    ascii_heatmap(avg_tension_conf, digit_labels, digit_labels,
                  title='Average Tension of Misclassified Pairs (true x pred)',
                  fmt='.1f')

    # 가장 혼동되는 쌍 Top-5
    print(f"\n  Top-5 most confused digit pairs:")
    print(f"  {'true':>4} -> {'pred':>4} | {'count':>5} | {'avg_tension':>11}")
    print(f"  {'─' * 4}────{'─' * 4}─┼─{'─' * 5}─┼─{'─' * 11}")
    pairs = []
    for i in range(10):
        for j in range(10):
            if i != j and confusion_off[i, j] > 0:
                pairs.append((i, j, int(confusion_off[i, j]), avg_tension_conf[i, j]))
    pairs.sort(key=lambda x: -x[2])
    for true_d, pred_d, cnt, avg_t in pairs[:5]:
        print(f"  {true_d:>4} -> {pred_d:>4} | {cnt:>5} | {avg_t:>11.2f}")


def analyze_selfref_convergence(data):
    """SelfReferentialField: 숫자별 텐션 수렴 패턴."""
    print_section("Self-Referential Field: Tension Convergence Per Digit")

    labels = data['labels']
    tensions = data['tensions']  # (N, n_steps+1)
    correct = data['correct']
    n_steps = tensions.shape[1]

    # 숫자별 평균 텐션 경로
    print(f"\n  Step-by-step tension trajectory (mean per digit):")
    step_headers = ''.join(f'{"s" + str(i):>10}' for i in range(n_steps))
    print(f"  {'digit':>5} | {step_headers} | {'delta':>8} | {'conv%':>6} | {'acc':>6}")
    print(f"  {'─' * 5}─┼─{'─' * (10 * n_steps)}─┼─{'─' * 8}─┼─{'─' * 6}─┼─{'─' * 6}")

    digit_convergence = {}
    for d in range(10):
        mask = labels == d
        if mask.sum() == 0:
            continue
        mean_path = tensions[mask].mean(axis=0)
        # 수렴도: 마지막 변화 / 첫 변화
        first_delta = abs(mean_path[1] - mean_path[0]) if n_steps > 1 else 0
        last_delta = abs(mean_path[-1] - mean_path[-2]) if n_steps > 1 else 0
        conv_pct = (1 - last_delta / (first_delta + 1e-8)) * 100 if first_delta > 0 else 100
        total_delta = mean_path[-1] - mean_path[0]
        acc = correct[mask].mean()

        vals = ''.join(f'{v:>10.2f}' for v in mean_path)
        print(f"  {d:>5} | {vals} | {total_delta:>+8.2f} | {conv_pct:>5.1f}% | {acc*100:>5.1f}%")

        digit_convergence[d] = {
            'path': mean_path,
            'first_delta': first_delta,
            'last_delta': last_delta,
            'conv_pct': conv_pct,
            'total_delta': total_delta,
            'acc': acc,
        }

    # 수렴 속도 랭킹
    print(f"\n  Convergence speed ranking (fastest -> slowest):")
    sorted_digits = sorted(digit_convergence.items(),
                          key=lambda x: -x[1]['conv_pct'])
    for rank, (d, s) in enumerate(sorted_digits, 1):
        bar = ascii_bar(max(0, s['conv_pct']), 100, 25)
        print(f"  {rank:>3}. digit {d}: conv={s['conv_pct']:>5.1f}% "
              f"delta={s['total_delta']:>+7.2f} acc={s['acc']*100:>5.1f}% |{bar}|")

    # ASCII 수렴 그래프 (텐션 변화를 step별로 표시)
    print(f"\n  Tension trajectory (ASCII graph, mean per digit):")
    all_means = []
    for d in range(10):
        if d in digit_convergence:
            all_means.append(digit_convergence[d]['path'])
    if all_means:
        all_vals = np.concatenate(all_means)
        v_min = all_vals.min()
        v_max = all_vals.max()
        v_range = v_max - v_min if v_max > v_min else 1.0
        graph_height = 12
        graph_width = n_steps

        # 간단한 ASCII 라인 차트 (각 digit을 한 행씩)
        print(f"  {'digit':>5} | {'trajectory (min={v_min:.1f} ... max={v_max:.1f})':^{graph_width * 8}}")
        print(f"  {'─' * 5}─┼─{'─' * (graph_width * 8)}")
        for d in range(10):
            if d not in digit_convergence:
                continue
            path = digit_convergence[d]['path']
            line = ''
            for v in path:
                norm = (v - v_min) / v_range
                pos = int(norm * 7)
                pos = max(0, min(7, pos))
                chars = '_.,-~^*!'
                line += f'  {chars[pos]}({v:>6.1f})'
            print(f"  {d:>5} | {line}")

    # 정답/오답 수렴 비교
    print(f"\n  Convergence: Correct vs Misclassified samples:")
    correct_tensions = tensions[correct]
    wrong_tensions = tensions[~correct]

    print(f"  {'group':>15} | ", end='')
    for i in range(n_steps):
        print(f"{'s' + str(i):>10}", end='')
    print(f" | {'conv%':>6}")

    print(f"  {'─' * 15}─┼─{'─' * (10 * n_steps)}─┼─{'─' * 6}")

    if len(correct_tensions) > 0:
        c_mean = correct_tensions.mean(axis=0)
        c_first = abs(c_mean[1] - c_mean[0]) if n_steps > 1 else 0
        c_last = abs(c_mean[-1] - c_mean[-2]) if n_steps > 1 else 0
        c_conv = (1 - c_last / (c_first + 1e-8)) * 100 if c_first > 0 else 100
        vals = ''.join(f'{v:>10.2f}' for v in c_mean)
        print(f"  {'Correct':>15} | {vals} | {c_conv:>5.1f}%")

    if len(wrong_tensions) > 0:
        w_mean = wrong_tensions.mean(axis=0)
        w_first = abs(w_mean[1] - w_mean[0]) if n_steps > 1 else 0
        w_last = abs(w_mean[-1] - w_mean[-2]) if n_steps > 1 else 0
        w_conv = (1 - w_last / (w_first + 1e-8)) * 100 if w_first > 0 else 100
        vals = ''.join(f'{v:>10.2f}' for v in w_mean)
        print(f"  {'Misclassified':>15} | {vals} | {w_conv:>5.1f}%")


def summary_findings(quad_data, selfref_data):
    """최종 요약."""
    print_header("Summary of Findings")

    labels = quad_data['labels']
    t_total = quad_data['t_total']
    correct_q = quad_data['correct']
    correct_s = selfref_data['correct']

    # 핵심 수치
    print(f"\n  RepulsionFieldQuad:")
    print(f"    Accuracy:           {correct_q.mean() * 100:.1f}%")
    print(f"    Mean total tension: {t_total.mean():.2f}")
    print(f"    Tension (correct):  {t_total[correct_q].mean():.2f}")
    if (~correct_q).sum() > 0:
        print(f"    Tension (wrong):    {t_total[~correct_q].mean():.2f}")
        ratio = t_total[~correct_q].mean() / (t_total[correct_q].mean() + 1e-8)
        print(f"    Wrong/Correct ratio:{ratio:.2f}x")

    print(f"\n  SelfReferentialField:")
    print(f"    Accuracy:           {correct_s.mean() * 100:.1f}%")
    tensions = selfref_data['tensions']
    init_t = tensions[:, 0].mean()
    final_t = tensions[:, -1].mean()
    print(f"    Initial tension:    {init_t:.2f}")
    print(f"    Final tension:      {final_t:.2f}")
    print(f"    Tension change:     {final_t - init_t:+.2f} "
          f"({'converging' if final_t < init_t else 'diverging'})")

    # 가장 어려운/쉬운 숫자
    digit_tensions = {}
    for d in range(10):
        mask = labels == d
        if mask.sum() > 0:
            digit_tensions[d] = t_total[mask].mean()
    hardest = max(digit_tensions, key=digit_tensions.get)
    easiest = min(digit_tensions, key=digit_tensions.get)
    print(f"\n  Hardest digit (highest tension): {hardest} "
          f"(tension={digit_tensions[hardest]:.2f})")
    print(f"  Easiest digit (lowest tension):  {easiest} "
          f"(tension={digit_tensions[easiest]:.2f})")

    # 의식 가설 해석
    print(f"\n  Consciousness hypothesis interpretation:")
    print(f"    Tension = subjective difficulty of input")
    print(f"    High tension -> engines disagree -> 'hard' perception")
    print(f"    Low tension  -> engines agree    -> 'easy' / automatic")
    if (~correct_q).sum() > 0 and ratio > 1.0:
        print(f"    Misclassified items have {ratio:.1f}x more tension")
        print(f"    -> The model 'feels' difficulty before failing")


# ─────────────────────────────────────────
# Main
# ─────────────────────────────────────────

def main():
    t0 = time.time()

    print()
    print("=" * 70)
    print("   logout -- Repulsion Field Tension Analysis")
    print("   Which MNIST inputs produce high vs low tension?")
    print("=" * 70)

    input_dim, hidden_dim, output_dim = 784, 48, 10
    epochs = 10

    # ── 데이터 로드 ──
    print("\n  Loading MNIST...")
    train_loader, test_loader = load_mnist(batch_size=128)

    # ══════════════════════════════════════════
    # Part 1: RepulsionFieldQuad
    # ══════════════════════════════════════════
    print_header("Part 1: RepulsionFieldQuad (4-pole repulsion field)")

    print("\n  Training RepulsionFieldQuad (10 epochs)...")
    quad_model = RepulsionFieldQuad(input_dim, hidden_dim, output_dim)
    print(f"  Parameters: {count_params(quad_model):,}")

    quad_losses, quad_accs = train_and_evaluate(
        quad_model, train_loader, test_loader,
        epochs=epochs, aux_lambda=0.01, verbose=True
    )
    print(f"\n  Final accuracy: {quad_accs[-1] * 100:.1f}%")
    print(f"  Batch tension (last): content={quad_model.tension_content:.4f}, "
          f"structure={quad_model.tension_structure:.4f}")

    # Per-sample 텐션 수집
    print("\n  Collecting per-sample tension on test set (10,000 samples)...")
    quad_data = collect_quad_tension(quad_model, test_loader)
    print(f"  Collected {len(quad_data['labels'])} samples.")

    # 분석 실행
    analyze_per_digit_tension(quad_data)
    analyze_tension_distribution(quad_data)
    analyze_extreme_samples(quad_data, top_n=10)
    analyze_confusion_tension(quad_data)

    # ══════════════════════════════════════════
    # Part 2: SelfReferentialField
    # ══════════════════════════════════════════
    print_header("Part 2: SelfReferentialField (self-observing tension)")

    print("\n  Training SelfReferentialField (10 epochs, 3 self-ref steps)...")
    selfref_model = SelfReferentialField(input_dim, hidden_dim, output_dim,
                                          n_self_ref_steps=3)
    print(f"  Parameters: {count_params(selfref_model):,}")

    selfref_losses, selfref_accs = train_and_evaluate(
        selfref_model, train_loader, test_loader,
        epochs=epochs, aux_lambda=0.01, verbose=True
    )
    print(f"\n  Final accuracy: {selfref_accs[-1] * 100:.1f}%")
    print(f"  Tension history (last batch): "
          f"{['%.2f' % t for t in selfref_model.tension_history]}")
    print(f"  Self-state norm: {selfref_model.self_state_norm:.4f}")

    # Per-sample 텐션 수렴 수집
    print("\n  Collecting per-sample tension convergence on test set...")
    selfref_data = collect_selfref_tension(selfref_model, test_loader)
    print(f"  Collected {len(selfref_data['labels'])} samples, "
          f"{selfref_data['tensions'].shape[1]} steps each.")

    # 자기참조 수렴 분석
    analyze_selfref_convergence(selfref_data)

    # ══════════════════════════════════════════
    # Summary
    # ══════════════════════════════════════════
    summary_findings(quad_data, selfref_data)

    elapsed = time.time() - t0
    print(f"\n  Total elapsed: {elapsed:.1f}s")
    print(f"  Done.")
    print()


if __name__ == '__main__':
    main()
