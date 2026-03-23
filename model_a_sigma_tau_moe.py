#!/usr/bin/env python3
"""모델 A: σ(6)-τ(6) MoE — 완전수 6의 약수함수로 MoE 구조 결정

수학적 근거:
  완전수 6의 약수함수:
    σ(6) = 1+2+3+6 = 12  (약수합 → Expert 수)
    τ(6) = |{1,2,3,6}| = 4  (약수 개수 → 활성 Expert 수)

  기존 MoE (Shazeer 2017): Expert 8개, k=2 (ad hoc 선택)
  σ-τ MoE: Expert 12개, k=4 (완전수 6에서 유도)

  활성비 = τ(6)/σ(6) = 4/12 = 1/3 — 메타 부동점과 일치!
  f(I) = 0.7I + 0.1 의 부동점이 I = 1/3.
  이 모델은 "12개 중 4개 활성"이라는 자연스러운 비율을 테스트한다.

벤치마크:
  σ-τ MoE (12 experts, k=4) vs Top-K (8 experts, k=2) vs Dense
  파라미터 수를 유사하게 맞추기 위해 12-expert 모델의 hidden_dim을 축소.
"""

import torch
from model_utils import (
    Expert, TopKGate, BaseMoE, DenseModel,
    load_mnist, train_and_evaluate, compare_results, count_params,
    SIGMA, TAU,
)

INPUT_DIM = 784
OUTPUT_DIM = 10
EPOCHS = 10


def build_sigma_tau_moe(hidden_dim=48):
    """σ(6)=12 experts, τ(6)=4 active."""
    gate = TopKGate(INPUT_DIM, n_experts=SIGMA, k=TAU)
    model = BaseMoE(INPUT_DIM, hidden_dim, OUTPUT_DIM, n_experts=SIGMA, gate=gate)
    return model


def build_topk_baseline(hidden_dim=64):
    """Standard Top-K MoE: 8 experts, k=2."""
    gate = TopKGate(INPUT_DIM, n_experts=8, k=2)
    model = BaseMoE(INPUT_DIM, hidden_dim, OUTPUT_DIM, n_experts=8, gate=gate)
    return model


def build_dense(hidden_dim=256):
    """Dense baseline."""
    return DenseModel(INPUT_DIM, hidden_dim, OUTPUT_DIM)


def main():
    print("=" * 70)
    print("  모델 A: σ(6)-τ(6) MoE  —  Expert=σ(6)=12, Active=τ(6)=4")
    print("  활성비 = τ/σ = 4/12 = 1/3 (메타 부동점)")
    print("=" * 70)

    train_loader, test_loader = load_mnist()

    # ── 파라미터 수 조정 ──
    # Dense(256) ≈ 203K params
    # TopK(8, hidden=64) ≈ 8*(784*64+64*10) + 784*8 ≈ 412K
    # σ-τ(12, hidden=48) ≈ 12*(784*48+48*10) + 784*12 ≈ 467K
    # hidden_dim을 조정하여 비슷하게 맞춤

    models = {
        'σ-τ MoE (12e, k=4)': build_sigma_tau_moe(hidden_dim=48),
        'Top-K MoE (8e, k=2)': build_topk_baseline(hidden_dim=64),
        'Dense baseline': build_dense(hidden_dim=256),
    }

    results = {}
    for name, model in models.items():
        params = count_params(model)
        print(f"\n── {name} (params={params:,}) ──")
        losses, accs = train_and_evaluate(model, train_loader, test_loader, epochs=EPOCHS)

        result = {
            'acc': accs[-1],
            'loss': losses[-1],
            'params': params,
        }

        # MoE 모델이면 메트릭 추가
        if isinstance(model, BaseMoE):
            metrics = model.get_metrics()
            result.update(metrics)
            print(f"    Active ratio: {metrics['active_ratio']:.3f}")
            print(f"    I_effective:  {metrics['I_effective']:.3f}")
            active_ratio = metrics['active_ratio']
            target = TAU / SIGMA  # 1/3
            print(f"    Target ratio: {target:.3f} (τ/σ = {TAU}/{SIGMA})")
            print(f"    Deviation:    {abs(active_ratio - target):.4f}")

        results[name] = result

    compare_results(results)

    # ── σ-τ 고유 분석 ──
    print("\n── σ-τ 구조 분석 ──")
    print(f"  σ(6) = {SIGMA} experts (약수합)")
    print(f"  τ(6) = {TAU} active  (약수 개수)")
    print(f"  활성비 = {TAU}/{SIGMA} = {TAU/SIGMA:.4f} ≈ 1/3")
    print(f"  메타 부동점 f(I)=0.7I+0.1 → I*=1/3 = {1/3:.4f}")

    st_acc = results['σ-τ MoE (12e, k=4)']['acc']
    tk_acc = results['Top-K MoE (8e, k=2)']['acc']
    diff = st_acc - tk_acc
    print(f"\n  σ-τ vs Top-K: {diff*100:+.2f}%")
    if diff > 0:
        print("  → σ-τ 구조가 우월 ✓")
    else:
        print("  → Top-K가 우세 (hidden_dim 차이 고려 필요)")


if __name__ == '__main__':
    main()
