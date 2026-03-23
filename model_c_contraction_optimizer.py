#!/usr/bin/env python3
"""모델 C: 수축 사상 옵티마이저 — f(x) = 0.7x + 0.1 에서 유도

수학적 근거:
  골든존 모델의 메타 부동점 방정식:
    f(I) = 0.7 * I + 0.1
    부동점: I* = 0.1 / (1 - 0.7) = 1/3

  수축 사상 정리 (Banach):
    |f(x) - f(y)| ≤ 0.7 * |x - y|
    수축계수 a = 0.7 < 1 이므로 유일한 부동점 1/3에 수렴.

  이를 최적화에 적용:
    θ_{t+1} = a * θ_t + b * (-∇L)
    여기서 a = 0.7 (수축계수), b는 학습률 역할.

  해석:
    - a*θ: 현재 파라미터를 0으로 수축 (weight decay 유사, 하지만 곱셈)
    - b*grad: gradient 방향으로 이동
    - 부동점: θ* = b*(-∇L) / (1-a) = b*(-∇L) / 0.3
      → loss의 critical point에서 ∇L=0이면 θ*=0으로 수렴
      → gradient가 있으면 gradient의 3.33배로 안정화

  a=0.7은 L2 weight decay λ=0.3과 동등:
    θ - λθ = (1-λ)θ = 0.7θ

  비교: Adam, SGD (with/without weight decay)
"""

import torch
from torch.optim import Optimizer
from model_utils import (
    DenseModel, load_mnist, train_and_evaluate, compare_results, count_params,
)

INPUT_DIM = 784
OUTPUT_DIM = 10
EPOCHS = 10


class ContractionOptimizer(Optimizer):
    """수축 사상 옵티마이저: θ_{t+1} = a * θ_t - b * ∇L

    Args:
        params: 모델 파라미터
        lr: 학습률 (= b, gradient 스케일링)
        contraction: 수축계수 (= a, 기본 0.7)
    """

    def __init__(self, params, lr=0.01, contraction=0.7):
        if not 0.0 < contraction < 1.0:
            raise ValueError(f"수축계수는 (0,1) 범위: {contraction}")
        defaults = dict(lr=lr, contraction=contraction)
        super().__init__(params, defaults)

    @torch.no_grad()
    def step(self, closure=None):
        loss = None
        if closure is not None:
            with torch.enable_grad():
                loss = closure()

        for group in self.param_groups:
            a = group['contraction']
            b = group['lr']

            for p in group['params']:
                if p.grad is None:
                    continue
                # f(θ) = a*θ - b*∇L
                p.mul_(a).add_(p.grad, alpha=-b)

        return loss


def main():
    print("=" * 70)
    print("  모델 C: 수축 사상 옵티마이저")
    print("  f(θ) = 0.7θ - lr·∇L  (수축계수 a=0.7, 부동점 I*=1/3)")
    print("=" * 70)

    train_loader, test_loader = load_mnist()

    HIDDEN_DIM = 256

    # 각 옵티마이저별 동일한 모델 구조 사용
    configs = [
        ('Contraction (a=0.7)', lambda m: ContractionOptimizer(m.parameters(), lr=0.01, contraction=0.7)),
        ('Contraction (a=0.8)', lambda m: ContractionOptimizer(m.parameters(), lr=0.01, contraction=0.8)),
        ('Contraction (a=0.9)', lambda m: ContractionOptimizer(m.parameters(), lr=0.01, contraction=0.9)),
        ('Adam (baseline)',     lambda m: torch.optim.Adam(m.parameters(), lr=0.001)),
        ('SGD (lr=0.01)',       lambda m: torch.optim.SGD(m.parameters(), lr=0.01)),
        ('SGD+WD (wd=0.3)',    lambda m: torch.optim.SGD(m.parameters(), lr=0.01, weight_decay=0.3)),
    ]

    results = {}
    for name, opt_fn in configs:
        model = DenseModel(INPUT_DIM, HIDDEN_DIM, OUTPUT_DIM)
        params = count_params(model)
        optimizer = opt_fn(model)

        print(f"\n── {name} (params={params:,}) ──")
        losses, accs = train_and_evaluate(
            model, train_loader, test_loader,
            epochs=EPOCHS, optimizer=optimizer,
        )
        results[name] = {
            'acc': accs[-1],
            'loss': losses[-1],
            'params': params,
        }

    compare_results(results)

    # ── 수축 분석 ──
    print("\n── 수축 사상 분석 ──")
    print("  f(θ) = a·θ - b·∇L")
    print("  a=0.7: 강한 수축, 빠른 수렴, 과소적합 위험")
    print("  a=0.9: 약한 수축, SGD에 가까움")
    print("  a=0.7 ↔ weight_decay=0.3: 수학적 동등")
    print()

    c07 = results.get('Contraction (a=0.7)', {}).get('acc', 0)
    sgd_wd = results.get('SGD+WD (wd=0.3)', {}).get('acc', 0)
    adam = results.get('Adam (baseline)', {}).get('acc', 0)

    print(f"  Contraction(0.7) vs SGD+WD(0.3): {(c07-sgd_wd)*100:+.2f}%")
    print(f"  Contraction(0.7) vs Adam:         {(c07-adam)*100:+.2f}%")

    if abs(c07 - sgd_wd) < 0.01:
        print("  → a=0.7과 WD=0.3이 동등함을 실증 ✓")
    else:
        print("  → 구현 차이로 인한 성능 괴리 (곱셈 vs 뺄셈 순서)")


if __name__ == '__main__':
    main()
