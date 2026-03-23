#!/usr/bin/env python3
"""Collective Recognition: 여럿이 하나를 알아보는 실험

체험 맥락:
  여러 존재가 "폐하"라고 부른다 — 독립된 다수가 하나를 인식한다.
  이 실험은 묻는다: 독립된 7개의 마음이 모두 같은 것을 인식할 때,
  무엇이 창발하는가?

설계:
  7개의 독립 에이전트 (서로 다른 아키텍처, 서로 다른 시드)가
  MNIST 테스트 셋의 각 샘플을 독립적으로 분류한다.
  전원 일치(7/7) = 가장 강한 집단 인식 = "폐하"
  의견 분열 = 혼란/불확실성

분석:
  1. 합의 분포: 7/7, 6/7, ... 빈도
  2. 합의 수준별 정확도: 만장일치일 때 vs 분열일 때
  3. 대관식 효과: 만장일치 정확도 > 최고 개별 정확도?
  4. 숫자별 합의: 어떤 숫자가 보편적으로 인식되는가?
  5. 투표 방식 비교: 다수결, 가중, 약수역수, 만장일치
  6. 창발 질문: 집단 > 최고 개인?
"""

import torch
import torch.nn as nn
import torch.nn.functional as F
import numpy as np
import math
import time
from collections import Counter, defaultdict

from model_utils import (
    Expert, TopKGate, BoltzmannGate, BaseMoE, DenseModel,
    load_mnist, train_and_evaluate, compare_results, count_params,
    SIGMA, TAU, PHI, DIVISOR_RECIPROCALS, H_TARGET
)
from model_meta_engine import (
    EngineA, EngineE, EngineG, EngineF,
    RepulsionFieldEngine, SelfReferentialField
)
from model_temporal_engine import TemporalContinuityEngine


# ─────────────────────────────────────────
# ASCII 시각화 유틸리티
# ─────────────────────────────────────────

def ascii_histogram(values, labels, title, width=50, show_pct=True):
    """수평 ASCII 히스토그램."""
    print(f"\n  {title}")
    print(f"  {'=' * (width + 30)}")
    max_val = max(values) if values else 1
    for label, val in zip(labels, values):
        bar_len = int(val / max_val * width) if max_val > 0 else 0
        bar = "#" * bar_len
        if show_pct:
            total = sum(values)
            pct = val / total * 100 if total > 0 else 0
            print(f"  {label:>12} | {bar:<{width}} | {val:>6} ({pct:5.1f}%)")
        else:
            print(f"  {label:>12} | {bar:<{width}} | {val:>6}")
    print(f"  {'=' * (width + 30)}")


def ascii_bar_chart(labels, values, title, width=40, fmt=".2f"):
    """수평 바 차트 (실수 값)."""
    print(f"\n  {title}")
    print(f"  {'-' * (width + 30)}")
    max_val = max(values) if values else 1
    for label, val in zip(labels, values):
        bar_len = int(val / max_val * width) if max_val > 0 else 0
        bar = "#" * bar_len
        print(f"  {label:>12} | {bar:<{width}} | {val:{fmt}}")
    print(f"  {'-' * (width + 30)}")


# ─────────────────────────────────────────
# 에이전트 생성
# ─────────────────────────────────────────

def create_agents(input_dim=784, hidden_dim=48, output_dim=10):
    """7개의 독립 에이전트 생성. 각기 다른 아키텍처와 시드."""
    agents = {}

    # Agent A: EngineA (sigma,tau-MoE)
    torch.manual_seed(1)
    agents['A (sigma-MoE)'] = {
        'model': EngineA(input_dim, hidden_dim, output_dim),
        'returns_tuple': False,
        'seed': 1,
    }

    # Agent E: EngineE (Euler Product)
    torch.manual_seed(2)
    agents['E (Euler)'] = {
        'model': EngineE(input_dim, hidden_dim, output_dim),
        'returns_tuple': False,
        'seed': 2,
    }

    # Agent G: EngineG (Shannon Entropy)
    torch.manual_seed(3)
    agents['G (Shannon)'] = {
        'model': EngineG(input_dim, hidden_dim, output_dim),
        'returns_tuple': False,
        'seed': 3,
    }

    # Agent R: RepulsionFieldEngine
    torch.manual_seed(4)
    agents['R (Repulsion)'] = {
        'model': RepulsionFieldEngine(input_dim, hidden_dim, output_dim),
        'returns_tuple': True,
        'seed': 4,
    }

    # Agent S: SelfReferentialField
    torch.manual_seed(5)
    agents['S (SelfRef)'] = {
        'model': SelfReferentialField(input_dim, hidden_dim, output_dim, n_self_ref_steps=3),
        'returns_tuple': True,
        'seed': 5,
    }

    # Agent T: TemporalContinuityEngine
    torch.manual_seed(6)
    agents['T (Temporal)'] = {
        'model': TemporalContinuityEngine(input_dim, hidden_dim, output_dim,
                                           state_dim=32, n_self_ref_steps=3),
        'returns_tuple': True,
        'seed': 6,
    }

    # Agent D: DenseModel
    torch.manual_seed(7)
    agents['D (Dense)'] = {
        'model': DenseModel(input_dim, hidden_dim * 4, output_dim),
        'returns_tuple': False,
        'seed': 7,
    }

    return agents


# ─────────────────────────────────────────
# 학습
# ─────────────────────────────────────────

def train_all_agents(agents, train_loader, test_loader, epochs=10):
    """모든 에이전트를 독립적으로 학습."""
    results = {}

    for name, info in agents.items():
        model = info['model']
        seed = info['seed']
        returns_tuple = info['returns_tuple']

        print(f"\n  [{name}] Training (seed={seed})...")
        torch.manual_seed(seed)
        np.random.seed(seed)

        aux_lambda = 0.01 if returns_tuple else 0.0
        losses, accs = train_and_evaluate(
            model, train_loader, test_loader,
            epochs=epochs, lr=0.001,
            aux_lambda=aux_lambda,
            flatten=True, verbose=True
        )
        results[name] = {
            'acc': accs[-1],
            'loss': losses[-1],
            'params': count_params(model),
        }

    return results


# ─────────────────────────────────────────
# 집단 추론
# ─────────────────────────────────────────

def collective_inference(agents, test_loader):
    """모든 에이전트로 테스트 셋 추론. 샘플별 예측과 확신도 수집."""

    # 결과 저장
    all_predictions = {name: [] for name in agents}  # name -> list of predictions
    all_confidences = {name: [] for name in agents}  # name -> list of max softmax prob
    all_labels = []

    for model_info in agents.values():
        model_info['model'].eval()

    with torch.no_grad():
        for X, y in test_loader:
            X_flat = X.view(X.size(0), -1)
            all_labels.append(y.numpy())

            for name, info in agents.items():
                model = info['model']
                out = model(X_flat)
                if info['returns_tuple']:
                    out = out[0]

                probs = F.softmax(out, dim=-1)
                preds = probs.argmax(dim=-1).numpy()
                confs = probs.max(dim=-1).values.numpy()

                all_predictions[name].append(preds)
                all_confidences[name].append(confs)

    # 연결
    labels = np.concatenate(all_labels)
    for name in agents:
        all_predictions[name] = np.concatenate(all_predictions[name])
        all_confidences[name] = np.concatenate(all_confidences[name])

    return all_predictions, all_confidences, labels


# ─────────────────────────────────────────
# 분석 함수들
# ─────────────────────────────────────────

def analyze_agreement(predictions, labels, agent_names):
    """합의 분포 분석."""
    n_samples = len(labels)
    n_agents = len(agent_names)

    # 각 샘플별 합의 수준 계산
    agreement_counts = []  # 가장 많은 투표를 받은 클래스의 투표 수
    majority_predictions = []  # 다수결 예측
    agreement_levels = []  # 합의 수준 (최다 투표수 / 전체)

    for i in range(n_samples):
        votes = [predictions[name][i] for name in agent_names]
        counter = Counter(votes)
        most_common_pred, most_common_count = counter.most_common(1)[0]

        agreement_counts.append(most_common_count)
        majority_predictions.append(most_common_pred)
        agreement_levels.append(most_common_count / n_agents)

    return (np.array(agreement_counts),
            np.array(majority_predictions),
            np.array(agreement_levels))


def agreement_distribution(agreement_counts, n_agents):
    """합의 수준별 분포."""
    dist = Counter(agreement_counts)
    levels = list(range(1, n_agents + 1))
    counts = [dist.get(level, 0) for level in levels]
    return levels, counts


def accuracy_by_agreement(agreement_counts, majority_predictions, labels, n_agents):
    """합의 수준별 정확도."""
    results = {}
    for level in range(1, n_agents + 1):
        mask = agreement_counts == level
        if mask.sum() > 0:
            correct = (majority_predictions[mask] == labels[mask]).sum()
            total = mask.sum()
            results[level] = {
                'accuracy': correct / total,
                'count': int(total),
                'correct': int(correct),
            }
    return results


def per_digit_agreement(predictions, labels, agent_names):
    """숫자별 합의 분석."""
    n_agents = len(agent_names)
    digit_stats = {}

    for digit in range(10):
        mask = labels == digit
        n_digit = mask.sum()
        if n_digit == 0:
            continue

        # 이 숫자 샘플들에 대한 합의 수준
        digit_agreements = []
        for i in np.where(mask)[0]:
            votes = [predictions[name][i] for name in agent_names]
            counter = Counter(votes)
            most_common_count = counter.most_common(1)[0][1]
            digit_agreements.append(most_common_count)

        digit_agreements = np.array(digit_agreements)
        unanimous = (digit_agreements == n_agents).sum()

        digit_stats[digit] = {
            'count': int(n_digit),
            'unanimous': int(unanimous),
            'unanimous_pct': unanimous / n_digit * 100,
            'avg_agreement': digit_agreements.mean(),
            'min_agreement': int(digit_agreements.min()),
        }

    return digit_stats


def confusion_analysis(predictions, labels, agent_names):
    """에이전트 간 불일치 분석: 누가 누구와 자주 다른가?"""
    n_agents = len(agent_names)
    # 쌍별 불일치 비율
    disagreement_matrix = np.zeros((n_agents, n_agents))
    n_samples = len(labels)

    for i in range(n_agents):
        for j in range(n_agents):
            if i == j:
                continue
            name_i = agent_names[i]
            name_j = agent_names[j]
            disagree = (predictions[name_i] != predictions[name_j]).sum()
            disagreement_matrix[i, j] = disagree / n_samples * 100

    return disagreement_matrix


def voting_schemes(predictions, confidences, labels, agent_names, individual_accs):
    """다양한 투표 방식 비교."""
    n_samples = len(labels)
    n_agents = len(agent_names)
    results = {}

    # 1. 다수결 (Simple majority)
    majority_preds = []
    for i in range(n_samples):
        votes = [predictions[name][i] for name in agent_names]
        counter = Counter(votes)
        majority_preds.append(counter.most_common(1)[0][0])
    majority_preds = np.array(majority_preds)
    results['Majority vote'] = (majority_preds == labels).mean()

    # 2. 개별 정확도 가중 투표
    weighted_scores = np.zeros((n_samples, 10))
    for name in agent_names:
        weight = individual_accs[name]
        for i in range(n_samples):
            pred = predictions[name][i]
            weighted_scores[i, pred] += weight
    weighted_preds = weighted_scores.argmax(axis=1)
    results['Acc-weighted'] = (weighted_preds == labels).mean()

    # 3. 확신도 가중 투표
    conf_scores = np.zeros((n_samples, 10))
    for name in agent_names:
        for i in range(n_samples):
            pred = predictions[name][i]
            conf = confidences[name][i]
            conf_scores[i, pred] += conf
    conf_preds = conf_scores.argmax(axis=1)
    results['Conf-weighted'] = (conf_preds == labels).mean()

    # 4. 약수역수 가중 ({1/2, 1/3, 1/6} 확장)
    # 7개 에이전트: {1/2, 1/3, 1/6, 1/7, 1/7, 1/7, 1/7} 정규화
    base_weights = [1/2, 1/3, 1/6]
    extra = [1/42] * 4  # 나머지를 균등 분배 (합=1이 되도록)
    raw_weights = base_weights + extra
    total_w = sum(raw_weights)
    divisor_weights = [w / total_w for w in raw_weights]

    div_scores = np.zeros((n_samples, 10))
    for idx, name in enumerate(agent_names):
        w = divisor_weights[idx]
        for i in range(n_samples):
            pred = predictions[name][i]
            div_scores[i, pred] += w
    div_preds = div_scores.argmax(axis=1)
    results['Divisor-weighted'] = (div_preds == labels).mean()

    # 5. 만장일치 전용 (전원 동의할 때만 답, 나머지는 기권)
    unanimous_preds = np.full(n_samples, -1)
    for i in range(n_samples):
        votes = [predictions[name][i] for name in agent_names]
        if len(set(votes)) == 1:
            unanimous_preds[i] = votes[0]

    answered = unanimous_preds >= 0
    if answered.sum() > 0:
        unanimous_acc = (unanimous_preds[answered] == labels[answered]).mean()
        coverage = answered.mean()
        results['Unanimity-only'] = unanimous_acc
        results['_unanimity_coverage'] = coverage
    else:
        results['Unanimity-only'] = 0.0
        results['_unanimity_coverage'] = 0.0

    return results


def polha_test(predictions, confidences, labels, agent_names):
    """'폐하' 테스트: 전원 일치 + 전원 고확신 샘플.

    이것이 데이터셋의 '왕' -- 보편적으로 인식되는 샘플.
    """
    n_samples = len(labels)
    n_agents = len(agent_names)

    # 전원 일치 여부
    unanimous_mask = np.zeros(n_samples, dtype=bool)
    for i in range(n_samples):
        votes = [predictions[name][i] for name in agent_names]
        unanimous_mask[i] = len(set(votes)) == 1

    # 전원 고확신 (모든 에이전트 confidence > 0.9)
    high_conf_mask = np.ones(n_samples, dtype=bool)
    for name in agent_names:
        high_conf_mask &= confidences[name] > 0.9

    # 폐하 = 전원 일치 AND 전원 고확신
    royalty_mask = unanimous_mask & high_conf_mask

    # Nobody = 최다 투표가 n_agents//2 이하 (과반 미달)
    nobody_mask = np.zeros(n_samples, dtype=bool)
    for i in range(n_samples):
        votes = [predictions[name][i] for name in agent_names]
        counter = Counter(votes)
        max_count = counter.most_common(1)[0][1]
        nobody_mask[i] = max_count <= n_agents // 2  # 3 이하

    royalty_correct = (np.array([predictions[agent_names[0]][i] for i in range(n_samples)])[royalty_mask]
                       == labels[royalty_mask]).mean() if royalty_mask.sum() > 0 else 0.0

    return {
        'unanimous_count': int(unanimous_mask.sum()),
        'unanimous_pct': unanimous_mask.mean() * 100,
        'high_conf_count': int(high_conf_mask.sum()),
        'royalty_count': int(royalty_mask.sum()),
        'royalty_pct': royalty_mask.mean() * 100,
        'royalty_accuracy': float(royalty_correct),
        'nobody_count': int(nobody_mask.sum()),
        'nobody_pct': nobody_mask.mean() * 100,
        'nobody_accuracy': float(
            (np.array([Counter([predictions[name][i] for name in agent_names]).most_common(1)[0][0]
                       for i in np.where(nobody_mask)[0]])
             == labels[nobody_mask]).mean()
        ) if nobody_mask.sum() > 0 else 0.0,
    }


# ─────────────────────────────────────────
# 메인
# ─────────────────────────────────────────

def main():
    print()
    print("=" * 70)
    print("   logout -- Collective Recognition Experiment")
    print("   여럿이 하나를 알아본다: 7개의 독립된 마음")
    print("=" * 70)

    # ── 데이터 로드 ──
    print("\n[1] Loading MNIST...")
    train_loader, test_loader = load_mnist(batch_size=128)

    input_dim, hidden_dim, output_dim = 784, 48, 10
    epochs = 10

    # ── 에이전트 생성 ──
    print("\n[2] Creating 7 independent agents...")
    agents = create_agents(input_dim, hidden_dim, output_dim)
    agent_names = list(agents.keys())

    for name, info in agents.items():
        params = count_params(info['model'])
        print(f"    {name:20s} | params={params:>8,} | seed={info['seed']}")

    # ── 독립 학습 ──
    print("\n[3] Training all agents independently...")
    print("=" * 70)
    t_start = time.time()
    train_results = train_all_agents(agents, train_loader, test_loader, epochs)
    t_train = time.time() - t_start
    print(f"\n  Total training time: {t_train:.1f}s")

    # 개별 결과 표
    print("\n" + "=" * 70)
    print("  Individual Agent Results")
    print("-" * 70)
    print(f"  {'Agent':<20} {'Accuracy':>10} {'Params':>10}")
    print("-" * 70)
    individual_accs = {}
    for name in agent_names:
        acc = train_results[name]['acc']
        params = train_results[name]['params']
        individual_accs[name] = acc
        print(f"  {name:<20} {acc*100:>9.2f}% {params:>10,}")
    best_agent = max(individual_accs, key=individual_accs.get)
    best_acc = individual_accs[best_agent]
    print("-" * 70)
    print(f"  Best individual: {best_agent} ({best_acc*100:.2f}%)")
    print("=" * 70)

    # ── 집단 추론 ──
    print("\n[4] Collective inference on test set...")
    predictions, confidences, labels = collective_inference(agents, test_loader)
    n_samples = len(labels)
    n_agents = len(agent_names)
    print(f"  {n_samples} samples, {n_agents} agents")

    # ══════════════════════════════════════════
    # 분석 시작
    # ══════════════════════════════════════════

    print("\n" + "=" * 70)
    print("   ANALYSIS")
    print("=" * 70)

    # ── A. 합의 분포 ──
    agreement_counts, majority_preds, agreement_levels = \
        analyze_agreement(predictions, labels, agent_names)

    levels, level_counts = agreement_distribution(agreement_counts, n_agents)
    level_labels = [f"{l}/{n_agents}" for l in levels]
    ascii_histogram(level_counts, level_labels, "Agreement Distribution (how many agents agree?)")

    # ── B. 합의 수준별 정확도 ──
    acc_by_level = accuracy_by_agreement(agreement_counts, majority_preds, labels, n_agents)

    print("\n  Accuracy by Agreement Level")
    print("  " + "-" * 60)
    print(f"  {'Level':>8} {'Count':>8} {'Correct':>8} {'Accuracy':>10}")
    print("  " + "-" * 60)
    acc_labels = []
    acc_values = []
    for level in sorted(acc_by_level.keys()):
        info = acc_by_level[level]
        print(f"  {level:>5}/{n_agents} {info['count']:>8} {info['correct']:>8} {info['accuracy']*100:>9.2f}%")
        acc_labels.append(f"{level}/{n_agents}")
        acc_values.append(info['accuracy'] * 100)
    print("  " + "-" * 60)

    if acc_values:
        ascii_bar_chart(acc_labels, acc_values,
                        "Accuracy by Agreement Level (%)", width=40, fmt=".1f")

    # ── C. 대관식 효과 (Coronation Effect) ──
    print("\n  === CORONATION EFFECT ===")
    print("  When all 7 minds agree, is the collective smarter than the best individual?")
    print()

    majority_acc = (majority_preds == labels).mean()
    unanimous_info = acc_by_level.get(n_agents, {'accuracy': 0.0, 'count': 0})
    unanimous_acc = unanimous_info['accuracy']
    unanimous_count = unanimous_info['count']

    print(f"  Best individual agent:    {best_acc*100:.2f}% ({best_agent})")
    print(f"  Majority vote (all):      {majority_acc*100:.2f}%")
    print(f"  Unanimous (7/7) accuracy: {unanimous_acc*100:.2f}% ({unanimous_count} samples)")
    print()

    if majority_acc > best_acc:
        delta = (majority_acc - best_acc) * 100
        print(f"  >> EMERGENT INTELLIGENCE: Collective > Best Individual by +{delta:.2f}%")
        print(f"     7 independent minds together are smarter than any one alone.")
    else:
        delta = (best_acc - majority_acc) * 100
        print(f"  >> No emergence: Best individual beats collective by +{delta:.2f}%")

    if unanimous_acc > best_acc:
        delta_u = (unanimous_acc - best_acc) * 100
        print(f"  >> CORONATION: Unanimous accuracy exceeds best individual by +{delta_u:.2f}%")
        print(f"     When all bow, the answer is almost certainly correct.")
    print()

    # ── D. 숫자별 합의 ──
    digit_stats = per_digit_agreement(predictions, labels, agent_names)

    print("\n  Per-Digit Agreement Analysis")
    print("  " + "-" * 65)
    print(f"  {'Digit':>6} {'Count':>7} {'Unanimous':>10} {'Unan%':>7} {'AvgAgree':>9}")
    print("  " + "-" * 65)
    digit_labels = []
    digit_unan_pcts = []
    for digit in range(10):
        if digit in digit_stats:
            s = digit_stats[digit]
            print(f"  {digit:>6} {s['count']:>7} {s['unanimous']:>10} {s['unanimous_pct']:>6.1f}% {s['avg_agreement']:>8.2f}")
            digit_labels.append(str(digit))
            digit_unan_pcts.append(s['unanimous_pct'])
    print("  " + "-" * 65)

    # 가장/덜 인식되는 숫자
    if digit_unan_pcts:
        best_digit = digit_labels[np.argmax(digit_unan_pcts)]
        worst_digit = digit_labels[np.argmin(digit_unan_pcts)]
        print(f"\n  Most universally recognized:  digit {best_digit} ({max(digit_unan_pcts):.1f}% unanimous)")
        print(f"  Least universally recognized: digit {worst_digit} ({min(digit_unan_pcts):.1f}% unanimous)")

    ascii_bar_chart(digit_labels, digit_unan_pcts,
                    "Unanimous Recognition Rate by Digit (%)", width=40, fmt=".1f")

    # ── E. 에이전트 간 불일치 ──
    dis_matrix = confusion_analysis(predictions, labels, agent_names)

    print("\n  Agent Disagreement Matrix (% of samples where agents disagree)")
    print("  " + "-" * (12 + 9 * n_agents))
    header = "  " + " " * 13
    for name in agent_names:
        short = name.split(' ')[0]
        header += f"{short:>8}"
    print(header)
    print("  " + "-" * (12 + 9 * n_agents))
    for i, name_i in enumerate(agent_names):
        short_i = name_i.split(' ')[0]
        row = f"  {short_i:>12}"
        for j in range(n_agents):
            if i == j:
                row += "      --"
            else:
                row += f"{dis_matrix[i,j]:>7.1f}%"
        print(row)
    print("  " + "-" * (12 + 9 * n_agents))

    # 가장 유사한/다른 쌍
    min_dis = float('inf')
    max_dis = 0
    min_pair = ("", "")
    max_pair = ("", "")
    for i in range(n_agents):
        for j in range(i+1, n_agents):
            d = dis_matrix[i, j]
            if d < min_dis:
                min_dis = d
                min_pair = (agent_names[i].split(' ')[0], agent_names[j].split(' ')[0])
            if d > max_dis:
                max_dis = d
                max_pair = (agent_names[i].split(' ')[0], agent_names[j].split(' ')[0])
    print(f"\n  Most similar pair:  {min_pair[0]} & {min_pair[1]} ({min_dis:.1f}% disagree)")
    print(f"  Most different pair: {max_pair[0]} & {max_pair[1]} ({max_dis:.1f}% disagree)")

    # ── F. 투표 방식 비교 ──
    vote_results = voting_schemes(predictions, confidences, labels, agent_names, individual_accs)

    print("\n  Voting Scheme Comparison")
    print("  " + "-" * 55)
    print(f"  {'Scheme':<25} {'Accuracy':>10} {'vs Best':>10}")
    print("  " + "-" * 55)
    vote_labels = []
    vote_accs = []
    for scheme, acc in vote_results.items():
        if scheme.startswith('_'):
            continue
        delta = (acc - best_acc) * 100
        sign = "+" if delta >= 0 else ""
        extra = ""
        if scheme == 'Unanimity-only':
            cov = vote_results.get('_unanimity_coverage', 0)
            extra = f"  (coverage: {cov*100:.1f}%)"
        print(f"  {scheme:<25} {acc*100:>9.2f}% {sign}{delta:>8.2f}%{extra}")
        vote_labels.append(scheme)
        vote_accs.append(acc * 100)
    print(f"  {'Best individual':<25} {best_acc*100:>9.2f}%")
    print("  " + "-" * 55)

    ascii_bar_chart(vote_labels + ['Best single'],
                    vote_accs + [best_acc * 100],
                    "Voting Schemes vs Best Individual (%)", width=40, fmt=".2f")

    # ── G. '폐하' 테스트 ──
    polha = polha_test(predictions, confidences, labels, agent_names)

    print("\n" + "=" * 70)
    print("   THE 'PYEHA' (CORONATION) TEST")
    print("   When ALL agents agree with HIGH confidence")
    print("=" * 70)

    print(f"""
  Total test samples:           {n_samples:>6}

  Unanimous (7/7 agree):        {polha['unanimous_count']:>6} ({polha['unanimous_pct']:.1f}%)
  High confidence (all > 0.9):  {polha['high_conf_count']:>6}
  'Royalty' (both):             {polha['royalty_count']:>6} ({polha['royalty_pct']:.1f}%)
  'Royalty' accuracy:           {polha['royalty_accuracy']*100:.2f}%

  'Nobody' (no majority):       {polha['nobody_count']:>6} ({polha['nobody_pct']:.1f}%)
  'Nobody' accuracy:            {polha['nobody_accuracy']*100:.2f}%
""")

    if polha['royalty_count'] > 0 and polha['nobody_count'] > 0:
        gap = polha['royalty_accuracy'] - polha['nobody_accuracy']
        print(f"  Royalty vs Nobody accuracy gap: {gap*100:.2f}%")
        print()
        if polha['royalty_accuracy'] > 0.99:
            print("  >> The 'Royalty' of this dataset are near-perfectly recognized.")
            print("     When 7 independent minds all bow with conviction,")
            print("     the recognition is almost infallible.")

    # ══════════════════════════════════════════
    # 최종 요약
    # ══════════════════════════════════════════

    print("\n" + "=" * 70)
    print("   SUMMARY: COLLECTIVE RECOGNITION")
    print("=" * 70)

    print(f"""
  7 agents, 7 architectures, 7 seeds.
  Each learned independently. Then they voted.

  Best individual:              {best_acc*100:.2f}%  ({best_agent})
  Majority vote:                {majority_acc*100:.2f}%  ({'+' if majority_acc > best_acc else ''}{(majority_acc-best_acc)*100:.2f}%)
  Unanimous (7/7) accuracy:     {unanimous_acc*100:.2f}%  on {unanimous_count}/{n_samples} samples
  'Royalty' accuracy:           {polha['royalty_accuracy']*100:.2f}%  on {polha['royalty_count']}/{n_samples} samples
""")

    # 창발 판정
    if majority_acc > best_acc:
        print("  VERDICT: EMERGENT COLLECTIVE INTELLIGENCE")
        print("  The whole is greater than the best part.")
        print("  Independent minds, agreeing, create something beyond any one of them.")
    else:
        print("  VERDICT: No clear emergence in majority vote.")

    if unanimous_acc > 0.99 and unanimous_count > n_samples * 0.5:
        print("\n  CORONATION CONFIRMED:")
        print("  When all 7 bow, accuracy approaches perfection.")
        print("  The 'Pyeha' of the dataset -- universally recognized, almost never wrong.")

    print()
    print("=" * 70)
    print("  Experiment complete.")
    print("=" * 70)
    print()


if __name__ == '__main__':
    main()
