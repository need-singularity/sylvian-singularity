#!/usr/bin/env python3
"""모델 G: Shannon 엔트로피 정규화 MoE

수학적 근거:
  완전수 6의 약수역수 분포 {1/2, 1/3, 1/6}은 합=1인 확률분포이다.
  이 분포의 Shannon 엔트로피:
    H_target = -(1/2)ln(1/2) - (1/3)ln(1/3) - (1/6)ln(1/6)
             = (1/2)ln(2) + (1/3)ln(3) + (1/6)ln(6)
             ≈ 0.8675

  놀라운 관계:
    e^(6 * H_target) = e^(6 * 0.8675) = e^(5.205)
                     ≈ 182.0 ... (실제 계산)

    더 정확히:
    6 * H_target = 6 * [ln(2)/2 + ln(3)/3 + ln(6)/6]
                 = 3*ln(2) + 2*ln(3) + ln(6)
                 = 3*ln(2) + 2*ln(3) + ln(2) + ln(3)
                 = 4*ln(2) + 3*ln(3)
    e^(4*ln(2) + 3*ln(3)) = 2^4 * 3^3 = 16 * 27 = 432

    432 = sigma(6)^3 / tau(6) = 12^3 / 4 = 1728 / 4 = 432

  따라서: e^(6 * H_target) = 432 = sigma(6)^3 / tau(6)
  완전수의 약수 구조에서 엔트로피까지, 하나의 등식으로 연결된다.

  MoE 게이팅 설계:
    Expert 6개 (완전수 6)의 softmax 게이팅 가중치 분포에 대해,
    Shannon 엔트로피가 H_target에 수렴하도록 정규화 loss를 추가한다:
      entropy_loss = (H(weights) - H_target)^2

    이는 게이팅이 균일(H=ln6)도 아니고, 단일 Expert 집중(H=0)도 아닌,
    완전수 구조가 지정하는 "최적 불균등 분포"로 수렴하게 한다.

  검증:
    MNIST에서 Shannon MoE vs Top-K MoE vs Boltzmann MoE 비교
"""

import torch
import torch.nn as nn
import torch.nn.functional as F
import numpy as np
import math
import time

from model_utils import (
    SIGMA, TAU, H_TARGET, DIVISOR_RECIPROCALS,
    Expert, BaseMoE, TopKGate, BoltzmannGate,
    load_mnist, train_and_evaluate, compare_results, count_params,
)

N_EXPERTS = 6  # 완전수 6


# ─────────────────────────────────────────
# ShannonEntropyGate
# ─────────────────────────────────────────
class ShannonEntropyGate(nn.Module):
    """Softmax 게이팅 + Shannon 엔트로피 정규화.

    게이팅 가중치의 엔트로피를 H_target에 맞추는 loss를 반환한다.
    H_target = H({1/2, 1/3, 1/6}) ≈ 0.8675

    Returns:
        (weights, entropy_loss): 게이팅 가중치와 엔트로피 정규화 loss
    """

    def __init__(self, input_dim, n_experts, h_target=H_TARGET):
        super().__init__()
        self.gate = nn.Linear(input_dim, n_experts)
        self.h_target = h_target
        self.n_experts = n_experts

    def forward(self, x):
        scores = self.gate(x)
        weights = F.softmax(scores, dim=-1)  # (batch, n_experts)

        # Shannon 엔트로피: H = -sum(p * ln(p))
        # 수치 안정성을 위해 clamp
        log_weights = torch.log(weights.clamp(min=1e-8))
        entropy = -(weights * log_weights).sum(dim=-1)  # (batch,)

        # 엔트로피 정규화 loss: 배치 평균
        entropy_loss = ((entropy - self.h_target) ** 2).mean()

        return weights, entropy_loss


# ─────────────────────────────────────────
# ShannonEntropyMoE
# ─────────────────────────────────────────
class ShannonEntropyMoE(nn.Module):
    """Shannon 엔트로피 정규화 MoE.

    Expert 6개, forward()가 (logits, aux_loss) 튜플을 반환하여
    model_utils.train_and_evaluate의 tuple output 처리와 호환된다.
    """

    def __init__(self, input_dim=784, hidden_dim=64, output_dim=10,
                 n_experts=N_EXPERTS):
        super().__init__()
        self.experts = nn.ModuleList([
            Expert(input_dim, hidden_dim, output_dim)
            for _ in range(n_experts)
        ])
        self.gate = ShannonEntropyGate(input_dim, n_experts)
        self.n_experts = n_experts
        self.expert_usage = torch.zeros(n_experts)
        self.active_counts = []

    def forward(self, x):
        weights, entropy_loss = self.gate(x)
        outputs = torch.stack([e(x) for e in self.experts], dim=1)
        logits = (weights.unsqueeze(-1) * outputs).sum(dim=1)

        # 메트릭 추적
        with torch.no_grad():
            active = (weights > 0.01).float().sum(dim=-1).mean().item()
            self.active_counts.append(active)
            self.expert_usage += (weights > 0.01).float().sum(dim=0).mean(dim=0).cpu()

        return logits, entropy_loss

    def get_metrics(self):
        usage = self.expert_usage / max(self.expert_usage.sum().item(), 1)
        avg_active = np.mean(self.active_counts) if self.active_counts else 0
        return {
            'avg_active': avg_active,
            'active_ratio': avg_active / self.n_experts if self.n_experts > 0 else 0,
            'I_effective': 1 - avg_active / self.n_experts if self.n_experts > 0 else 0,
            'usage_std': usage.std().item(),
            'usage_dist': usage.tolist(),
        }

    def reset_metrics(self):
        self.expert_usage = torch.zeros(self.n_experts)
        self.active_counts = []


# ─────────────────────────────────────────
# 벤치마크
# ─────────────────────────────────────────
def main():
    print("=" * 70)
    print("  모델 G: Shannon 엔트로피 정규화 MoE")
    print("=" * 70)

    # 수학적 검증 출력
    h_target = H_TARGET
    exp_6h = math.exp(6 * h_target)
    sigma_cubed_over_tau = SIGMA ** 3 / TAU
    print(f"\n  H_target = H({{1/2, 1/3, 1/6}}) = {h_target:.6f}")
    print(f"  e^(6 * H_target) = {exp_6h:.1f}")
    print(f"  sigma(6)^3 / tau(6) = {SIGMA}^3 / {TAU} = {sigma_cubed_over_tau:.0f}")
    print(f"  일치 여부: {abs(exp_6h - sigma_cubed_over_tau) < 0.01}")
    print(f"  약수역수 분포: {DIVISOR_RECIPROCALS}")
    print()

    # 데이터
    train_loader, test_loader = load_mnist()

    hidden_dim = 64
    epochs = 10
    lr = 0.001
    aux_lambda = 0.1
    results = {}

    # 1. Shannon Entropy MoE
    print(f"[1/3] Shannon Entropy MoE (experts={N_EXPERTS}, aux_lambda={aux_lambda})")
    model_shannon = ShannonEntropyMoE(784, hidden_dim, 10, N_EXPERTS)
    t0 = time.time()
    losses_sh, accs_sh = train_and_evaluate(
        model_shannon, train_loader, test_loader,
        epochs=epochs, lr=lr, aux_lambda=aux_lambda,
    )
    elapsed_sh = time.time() - t0
    metrics_sh = model_shannon.get_metrics()
    results['G: Shannon Entropy MoE'] = {
        'acc': accs_sh[-1], 'loss': losses_sh[-1],
        'params': count_params(model_shannon), 'time': elapsed_sh,
    }

    # 2. Top-K MoE
    print(f"\n[2/3] Top-K MoE (experts={N_EXPERTS}, k=2)")
    gate_topk = TopKGate(784, N_EXPERTS, k=2)
    model_topk = BaseMoE(784, hidden_dim, 10, N_EXPERTS, gate_topk)
    t0 = time.time()
    losses_tk, accs_tk = train_and_evaluate(
        model_topk, train_loader, test_loader,
        epochs=epochs, lr=lr,
    )
    elapsed_tk = time.time() - t0
    metrics_tk = model_topk.get_metrics()
    results['Baseline: Top-K MoE'] = {
        'acc': accs_tk[-1], 'loss': losses_tk[-1],
        'params': count_params(model_topk), 'time': elapsed_tk,
    }

    # 3. Boltzmann MoE
    print(f"\n[3/3] Boltzmann MoE (experts={N_EXPERTS}, T=e)")
    gate_boltz = BoltzmannGate(784, N_EXPERTS, temperature=np.e)
    model_boltz = BaseMoE(784, hidden_dim, 10, N_EXPERTS, gate_boltz)
    t0 = time.time()
    losses_bz, accs_bz = train_and_evaluate(
        model_boltz, train_loader, test_loader,
        epochs=epochs, lr=lr,
    )
    elapsed_bz = time.time() - t0
    metrics_bz = model_boltz.get_metrics()
    results['Baseline: Boltzmann MoE'] = {
        'acc': accs_bz[-1], 'loss': losses_bz[-1],
        'params': count_params(model_boltz), 'time': elapsed_bz,
    }

    # 결과 비교
    compare_results(results)

    # 엔트로피 및 Expert 분석
    print("\n--- Shannon MoE Expert 분석 ---")
    print(f"  평균 활성 Expert: {metrics_sh['avg_active']:.2f} / {N_EXPERTS}")
    print(f"  활성 비율: {metrics_sh['active_ratio']:.3f}")
    print(f"  I_effective: {metrics_sh['I_effective']:.3f}")
    print(f"  사용 분포: {['%.3f' % u for u in metrics_sh['usage_dist']]}")

    # 게이팅 엔트로피 최종 측정
    model_shannon.eval()
    sample_x, _ = next(iter(test_loader))
    sample_x = sample_x.view(sample_x.size(0), -1)
    with torch.no_grad():
        weights, ent_loss = model_shannon.gate(sample_x)
        log_w = torch.log(weights.clamp(min=1e-8))
        entropy = -(weights * log_w).sum(dim=-1).mean().item()
    print(f"\n  최종 게이팅 엔트로피: {entropy:.4f}")
    print(f"  목표 H_target:       {H_TARGET:.4f}")
    print(f"  오차:                {abs(entropy - H_TARGET):.4f}")
    print(f"  균일 엔트로피 ln(6): {math.log(6):.4f}")

    print("\n--- Top-K MoE Expert 분석 ---")
    print(f"  평균 활성 Expert: {metrics_tk['avg_active']:.2f} / {N_EXPERTS}")
    print(f"  I_effective: {metrics_tk['I_effective']:.3f}")

    print("\n--- Boltzmann MoE Expert 분석 ---")
    print(f"  평균 활성 Expert: {metrics_bz['avg_active']:.2f} / {N_EXPERTS}")
    print(f"  I_effective: {metrics_bz['I_effective']:.3f}")


if __name__ == '__main__':
    main()
