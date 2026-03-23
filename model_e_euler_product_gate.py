#!/usr/bin/env python3
"""모델 E: 오일러곱 p=2,3 절단 게이트 (EulerProductGate)

수학적 근거:
  리만 제타 함수의 오일러 곱 표현:
    zeta(s) = prod_{p prime} 1/(1 - p^{-s})

  p=2,3에서 절단하면:
    zeta_{2,3}(s) = 1/(1-2^{-s}) * 1/(1-3^{-s})

  가설 092에서 발견: 골든존 모델 = zeta 오일러곱 p=2,3 절단
    G = D * P / I  <-->  zeta_{2,3} 구조

  이 절단은 두 소인수의 곱으로 6개 상태를 생성:
    p=2: {0, 1}      (이진 분류, 2개 상태)
    p=3: {0, 1, 2}   (삼진 분류, 3개 상태)
    합계: 2 x 3 = 6  (= 완전수 6개 Expert)

  게이팅 설계 — EulerProductGate:
    1단계 (p=2): sigmoid(W_2 @ x + b_2)
      -> 이진 게이트 [alpha, 1-alpha]
      -> "기본 on/off 결정"

    2단계 (p=3): softmax(W_3 @ x + b_3)
      -> 삼진 분포 [beta_0, beta_1, beta_2]
      -> "세부 라우팅"

    최종 가중치 (6개 Expert):
      w_{i,j} = gate_2[i] * gate_3[j]
      where i in {0,1}, j in {0,1,2}

    이는 오일러곱의 곱셈적 구조를 정확히 반영:
      zeta_{2,3} = (1단계) * (2단계)

  Expert 배치:
    Expert 0: (0,0) = (1-alpha) * beta_0
    Expert 1: (0,1) = (1-alpha) * beta_1
    Expert 2: (0,2) = (1-alpha) * beta_2
    Expert 3: (1,0) = alpha * beta_0
    Expert 4: (1,1) = alpha * beta_1
    Expert 5: (1,2) = alpha * beta_2

  핵심 질문:
  2단계 계층적 게이팅이 flat Top-K나 Boltzmann보다 효율적인가?
  오일러곱의 곱셈적 독립 구조가 Expert 분화를 촉진하는가?
"""

import sys
import os
import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from model_utils import (
    load_mnist, train_and_evaluate, compare_results, count_params,
    Expert, BaseMoE, TopKGate, BoltzmannGate,
)


# ─────────────────────────────────────────
# 오일러곱 상수
# ─────────────────────────────────────────
P_BINARY = 2   # 첫째 소수
P_TERNARY = 3  # 둘째 소수
N_EXPERTS = P_BINARY * P_TERNARY  # = 6 (완전수!)


# ─────────────────────────────────────────
# EulerProductGate
# ─────────────────────────────────────────
class EulerProductGate(nn.Module):
    """오일러곱 p=2,3 절단 기반 2단계 계층 게이트.

    1단계: sigmoid (이진, p=2) -> alpha in [0,1]
    2단계: softmax (삼진, p=3) -> beta in simplex(3)
    최종:  w[i,j] = gate_2[i] * gate_3[j], i=0..1, j=0..2
    """
    def __init__(self, input_dim, temperature=1.0):
        super().__init__()
        # p=2 이진 게이트
        self.linear_2 = nn.Linear(input_dim, 1)
        # p=3 삼진 게이트
        self.linear_3 = nn.Linear(input_dim, P_TERNARY)
        self.temperature = temperature

    def forward(self, x):
        # 1단계: p=2 이진 분류
        alpha = torch.sigmoid(self.linear_2(x))  # (batch, 1), [0,1]
        gate_2 = torch.cat([1 - alpha, alpha], dim=-1)  # (batch, 2)

        # 2단계: p=3 삼진 분류
        gate_3 = F.softmax(self.linear_3(x) / self.temperature, dim=-1)  # (batch, 3)

        # 오일러곱: 외적으로 6개 Expert 가중치 생성
        # w[i,j] = gate_2[i] * gate_3[j]
        # gate_2: (batch, 2, 1), gate_3: (batch, 1, 3)
        weights = gate_2.unsqueeze(-1) * gate_3.unsqueeze(-2)  # (batch, 2, 3)
        weights = weights.reshape(x.size(0), N_EXPERTS)  # (batch, 6)

        return weights


# ─────────────────────────────────────────
# Euler Product MoE
# ─────────────────────────────────────────
class EulerProductMoE(nn.Module):
    """오일러곱 게이트 기반 MoE 모델.

    6개 Expert를 2x3 계층적으로 라우팅한다.
    """
    def __init__(self, input_dim=784, hidden_dim=128, output_dim=10, temperature=1.0):
        super().__init__()
        self.experts = nn.ModuleList([
            Expert(input_dim, hidden_dim, output_dim)
            for _ in range(N_EXPERTS)
        ])
        self.gate = EulerProductGate(input_dim, temperature=temperature)
        self.n_experts = N_EXPERTS

        # 메트릭 추적
        self.expert_usage = torch.zeros(N_EXPERTS)
        self.active_counts = []
        self.binary_entropy_history = []
        self.ternary_entropy_history = []

    def forward(self, x):
        weights = self.gate(x)  # (batch, 6)
        outputs = torch.stack([e(x) for e in self.experts], dim=1)  # (batch, 6, output_dim)
        result = (weights.unsqueeze(-1) * outputs).sum(dim=1)  # (batch, output_dim)

        with torch.no_grad():
            active = (weights > 0.01).float().sum(dim=-1).mean().item()
            self.active_counts.append(active)
            self.expert_usage += (weights > 0.01).float().sum(dim=0).mean(dim=0).cpu()

            # 2x3 구조 분석
            w_2d = weights.reshape(-1, P_BINARY, P_TERNARY)
            binary_probs = w_2d.sum(dim=-1)  # (batch, 2)
            ternary_probs = w_2d.sum(dim=-2)  # (batch, 3)

            # Shannon entropy
            def entropy(p):
                p = p.clamp(min=1e-8)
                return -(p * p.log()).sum(dim=-1).mean().item()

            self.binary_entropy_history.append(entropy(binary_probs))
            self.ternary_entropy_history.append(entropy(ternary_probs))

        return result

    def get_metrics(self):
        usage = self.expert_usage / max(self.expert_usage.sum().item(), 1)
        avg_active = np.mean(self.active_counts) if self.active_counts else 0
        avg_h2 = np.mean(self.binary_entropy_history) if self.binary_entropy_history else 0
        avg_h3 = np.mean(self.ternary_entropy_history) if self.ternary_entropy_history else 0
        return {
            'avg_active': avg_active,
            'active_ratio': avg_active / self.n_experts,
            'I_effective': 1 - avg_active / self.n_experts,
            'usage_std': usage.std().item(),
            'binary_entropy': avg_h2,
            'ternary_entropy': avg_h3,
            'usage_per_expert': usage.tolist(),
        }

    def reset_metrics(self):
        self.expert_usage = torch.zeros(self.n_experts)
        self.active_counts = []
        self.binary_entropy_history = []
        self.ternary_entropy_history = []


# ─────────────────────────────────────────
# 벤치마크
# ─────────────────────────────────────────
def main():
    print("=" * 70)
    print("  모델 E: 오일러곱 p=2,3 절단 게이트")
    print("=" * 70)

    # 오일러곱 구조 설명
    print("\n[오일러곱 구조]")
    print(f"  zeta_{{2,3}}(s) = 1/(1-2^{{-s}}) * 1/(1-3^{{-s}})")
    print(f"  p=2 이진 게이트: sigmoid -> [alpha, 1-alpha]")
    print(f"  p=3 삼진 게이트: softmax -> [beta_0, beta_1, beta_2]")
    print(f"  Expert 수: {P_BINARY} x {P_TERNARY} = {N_EXPERTS} (완전수 6)")
    print(f"\n  Expert 배치 (2x3):")
    print(f"          j=0       j=1       j=2")
    print(f"  i=0  [(1-a)*b0  (1-a)*b1  (1-a)*b2]")
    print(f"  i=1  [  a*b0      a*b1      a*b2  ]")

    # 데이터 로드
    print("\n[데이터 로드]")
    train_loader, test_loader = load_mnist()

    # 모델 정의
    INPUT_DIM = 784
    HIDDEN_DIM = 128
    OUTPUT_DIM = 10
    EPOCHS = 10

    # 오일러곱 MoE
    euler_model = EulerProductMoE(INPUT_DIM, HIDDEN_DIM, OUTPUT_DIM)

    # Top-K(6, k=2) MoE (비교)
    topk_gate = TopKGate(INPUT_DIM, N_EXPERTS, k=2)
    topk_model = BaseMoE(INPUT_DIM, HIDDEN_DIM, OUTPUT_DIM, N_EXPERTS, topk_gate)

    # Boltzmann(6) MoE (비교)
    boltz_gate = BoltzmannGate(INPUT_DIM, N_EXPERTS)
    boltz_model = BaseMoE(INPUT_DIM, HIDDEN_DIM, OUTPUT_DIM, N_EXPERTS, boltz_gate)

    models = {
        'EulerProduct (2x3)': euler_model,
        'Top-K (6, k=2)': topk_model,
        'Boltzmann (6)': boltz_model,
    }

    results = {}
    for name, model in models.items():
        print(f"\n{'─' * 50}")
        print(f"  학습: {name}")
        print(f"  파라미터: {count_params(model):,}")
        print(f"{'─' * 50}")

        if hasattr(model, 'reset_metrics'):
            model.reset_metrics()

        losses, accs = train_and_evaluate(model, train_loader, test_loader, epochs=EPOCHS)
        results[name] = {
            'acc': accs[-1],
            'loss': losses[-1],
            'params': count_params(model),
        }

        # 메트릭 수집
        if hasattr(model, 'get_metrics'):
            metrics = model.get_metrics()
            results[name].update(metrics)

    compare_results(results)

    # 오일러곱 구조 분석
    print("\n[오일러곱 게이트 분석]")
    euler_metrics = euler_model.get_metrics()
    print(f"  평균 활성 Expert: {euler_metrics['avg_active']:.2f} / {N_EXPERTS}")
    print(f"  활성 비율:        {euler_metrics['active_ratio']:.4f}")
    print(f"  I_effective:      {euler_metrics['I_effective']:.4f}")
    print(f"  이진 엔트로피:    {euler_metrics['binary_entropy']:.4f}  (max={np.log(2):.4f})")
    print(f"  삼진 엔트로피:    {euler_metrics['ternary_entropy']:.4f}  (max={np.log(3):.4f})")

    # Expert 사용량 (2x3 격자)
    usage = euler_metrics['usage_per_expert']
    print(f"\n  Expert 사용량 (2x3 격자):")
    print(f"          j=0      j=1      j=2")
    for i in range(P_BINARY):
        row = [usage[i * P_TERNARY + j] for j in range(P_TERNARY)]
        print(f"  i={i}  [{' '.join(f'{v:7.4f}' for v in row)}]")

    # Top-K 메트릭
    print(f"\n[Top-K 게이트 분석]")
    topk_metrics = topk_model.get_metrics()
    print(f"  평균 활성 Expert: {topk_metrics['avg_active']:.2f} / {N_EXPERTS}")
    print(f"  I_effective:      {topk_metrics['I_effective']:.4f}")

    # Boltzmann 메트릭
    print(f"\n[Boltzmann 게이트 분석]")
    boltz_metrics = boltz_model.get_metrics()
    print(f"  평균 활성 Expert: {boltz_metrics['avg_active']:.2f} / {N_EXPERTS}")
    print(f"  I_effective:      {boltz_metrics['I_effective']:.4f}")

    # 결론
    print("\n[결론]")
    best = max(results, key=lambda k: results[k]['acc'])
    print(f"  최고 성능: {best} ({results[best]['acc']*100:.2f}%)")

    euler_acc = results['EulerProduct (2x3)']['acc']
    topk_acc = results['Top-K (6, k=2)']['acc']
    boltz_acc = results['Boltzmann (6)']['acc']
    print(f"  EulerProduct vs Top-K:     {(euler_acc - topk_acc)*100:+.2f}%p")
    print(f"  EulerProduct vs Boltzmann: {(euler_acc - boltz_acc)*100:+.2f}%p")

    if euler_metrics['I_effective'] > 0.2 and euler_metrics['I_effective'] < 0.5:
        print(f"  I_effective = {euler_metrics['I_effective']:.4f} -> 골든존 근방!")
    else:
        print(f"  I_effective = {euler_metrics['I_effective']:.4f} -> 골든존 밖")


if __name__ == '__main__':
    main()
