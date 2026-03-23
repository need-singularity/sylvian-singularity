#!/usr/bin/env python3
"""CIFAR-10 벤치마크 — 모든 메타 엔진 모델 테스트

MNIST(784차원, 흑백)보다 어려운 CIFAR-10(3072차원, 컬러)에서
메타 엔진 아키텍처들의 성능을 비교한다.

입력: 32x32x3 = 3072 (flatten)
hidden_dim: 64 (MNIST 48보다 크게, 더 어려운 태스크)
epochs: 15 (MNIST 10보다 길게)
"""

import torch
import time

from model_utils import (
    DenseModel, BaseMoE, TopKGate,
    load_cifar10, train_and_evaluate, compare_results, count_params,
)
from model_meta_engine import (
    EngineA, EngineE,
    DualBrainEngine, MetaEngine, HierarchicalMetaEngine,
    RepulsionFieldEngine, RepulsionFieldQuad, SelfReferentialField,
)


# ─────────────────────────────────────────
# MNIST 기준 결과 (model_meta_engine.py 벤치마크)
# ─────────────────────────────────────────
MNIST_RESULTS = {
    'Dense':             96.56,
    'Top-K MoE':         96.79,
    'Engine A':          97.17,
    'Engine E':          96.55,
    'DualBrain (A+G)':   97.27,
    'Meta (AEGF)':       97.63,
    'Meta fixed':        97.75,
    'Hierarchical':      97.49,
    'Repulsion (A|G)':   97.41,
    'Repulsion Quad':    97.19,
    'SelfRef Field':     97.52,
}


def main():
    print()
    print("=" * 65)
    print("   logout — CIFAR-10 메타 엔진 벤치마크")
    print("   엔진 + 엔진 = 상위엔진 (harder task)")
    print("=" * 65)

    train_loader, test_loader = load_cifar10()
    input_dim, hidden_dim, output_dim = 3072, 64, 10
    epochs = 15
    results = {}

    start_time = time.time()

    # ── Baseline: Dense ──
    print("\n[Dense baseline]")
    model = DenseModel(input_dim, hidden_dim * 4, output_dim)
    losses, accs = train_and_evaluate(model, train_loader, test_loader, epochs)
    results['Dense'] = {'acc': accs[-1], 'loss': losses[-1], 'params': count_params(model)}

    # ── Baseline: Top-K MoE (8, k=2) ──
    print("\n[Top-K MoE (8 experts, k=2)]")
    model = BaseMoE(input_dim, hidden_dim, output_dim, 8,
                     TopKGate(input_dim, 8, 2))
    losses, accs = train_and_evaluate(model, train_loader, test_loader, epochs)
    results['Top-K MoE'] = {'acc': accs[-1], 'loss': losses[-1], 'params': count_params(model)}

    # ── 단일 엔진 A ──
    print("\n[Engine A: sigma,tau-MoE (12e, k=4)]")
    model = EngineA(input_dim, hidden_dim, output_dim)
    losses, accs = train_and_evaluate(model, train_loader, test_loader, epochs)
    results['Engine A'] = {'acc': accs[-1], 'loss': losses[-1], 'params': count_params(model)}

    # ── 단일 엔진 E ──
    print("\n[Engine E: Euler Product (2x3)]")
    model = EngineE(input_dim, hidden_dim, output_dim)
    losses, accs = train_and_evaluate(model, train_loader, test_loader, epochs)
    results['Engine E'] = {'acc': accs[-1], 'loss': losses[-1], 'params': count_params(model)}

    # ── DualBrain (A+G) ──
    print("\n[DualBrain: Left(A) + Right(G) + Corpus Callosum]")
    model = DualBrainEngine(input_dim, hidden_dim, output_dim)
    losses, accs = train_and_evaluate(model, train_loader, test_loader, epochs,
                                       aux_lambda=0.01)
    results['DualBrain (A+G)'] = {'acc': accs[-1], 'loss': losses[-1], 'params': count_params(model)}

    # ── MetaEngine (AEGF, 축소사상 라우팅) ──
    print("\n[MetaEngine: A+E+G+F (contraction routing)]")
    model = MetaEngine(input_dim, hidden_dim, output_dim,
                        engines='AEGF', routing='meta')
    losses, accs = train_and_evaluate(model, train_loader, test_loader, epochs,
                                       aux_lambda=0.01)
    results['Meta (AEGF)'] = {'acc': accs[-1], 'loss': losses[-1], 'params': count_params(model)}

    # ── MetaEngine (고정 가중치) ──
    print("\n[MetaEngine: A+E+G+F (fixed {1/2,1/3,1/6} weights)]")
    model = MetaEngine(input_dim, hidden_dim, output_dim,
                        engines='AEGF', routing='fixed')
    losses, accs = train_and_evaluate(model, train_loader, test_loader, epochs,
                                       aux_lambda=0.01)
    results['Meta fixed'] = {'acc': accs[-1], 'loss': losses[-1], 'params': count_params(model)}

    # ── Hierarchical (메타의 메타) ──
    print("\n[Hierarchical: (A+E) + (G+F) meta-combined]")
    model = HierarchicalMetaEngine(input_dim, hidden_dim, output_dim)
    losses, accs = train_and_evaluate(model, train_loader, test_loader, epochs,
                                       aux_lambda=0.01)
    results['Hierarchical'] = {'acc': accs[-1], 'loss': losses[-1], 'params': count_params(model)}

    # ── RepulsionField (2극: A vs G) ──
    print("\n[RepulsionField: Pole+(A) vs Pole-(G)]")
    model = RepulsionFieldEngine(input_dim, hidden_dim, output_dim)
    losses, accs = train_and_evaluate(model, train_loader, test_loader, epochs,
                                       aux_lambda=0.01)
    results['Repulsion (A|G)'] = {'acc': accs[-1], 'loss': losses[-1], 'params': count_params(model)}
    print(f"    Tension: {model.tension_magnitude:.4f}")

    # ── RepulsionFieldQuad (4극: A|G × E|F) ──
    print("\n[RepulsionFieldQuad: (A|G) x (E|F)]")
    model = RepulsionFieldQuad(input_dim, hidden_dim, output_dim)
    losses, accs = train_and_evaluate(model, train_loader, test_loader, epochs,
                                       aux_lambda=0.01)
    results['Repulsion Quad'] = {'acc': accs[-1], 'loss': losses[-1], 'params': count_params(model)}
    print(f"    Tension content: {model.tension_content:.4f}, structure: {model.tension_structure:.4f}")

    # ── SelfReferentialField (자기참조 반발력장) ──
    print("\n[SelfReferentialField: 장력을 관찰하는 엔진 (Phase 3)]")
    model = SelfReferentialField(input_dim, hidden_dim, output_dim, n_self_ref_steps=3)
    losses, accs = train_and_evaluate(model, train_loader, test_loader, epochs,
                                       aux_lambda=0.01)
    results['SelfRef Field'] = {'acc': accs[-1], 'loss': losses[-1], 'params': count_params(model)}
    print(f"    Tension history: {['%.1f' % t for t in model.tension_history]}")
    print(f"    Self-state norm: {model.self_state_norm:.4f}")
    converged = (len(model.tension_history) >= 2 and
                 abs(model.tension_history[-1] - model.tension_history[-2]) <
                 abs(model.tension_history[1] - model.tension_history[0]))
    print(f"    Tension converging: {'YES' if converged else 'NO'}")

    elapsed = time.time() - start_time

    # ── 결과 비교 ──
    compare_results(results)

    print(f"\n  Total time: {elapsed:.0f}s ({elapsed/60:.1f}min)")

    # ── 핵심 분석 ──
    print("\n" + "-" * 65)
    print("  핵심 질문: 엔진 조합이 단일 엔진보다 나은가? (CIFAR-10)")
    print("-" * 65)

    single_best = max(results['Engine A']['acc'], results['Engine E']['acc'])
    meta_acc = results['Meta (AEGF)']['acc']
    dual_acc = results['DualBrain (A+G)']['acc']

    print(f"  단일 엔진 최고:     {single_best*100:.2f}%")
    print(f"  DualBrain (A+G):    {dual_acc*100:.2f}%  ({'+' if dual_acc > single_best else ''}{(dual_acc-single_best)*100:.2f}%)")
    print(f"  Meta (AEGF):        {meta_acc*100:.2f}%  ({'+' if meta_acc > single_best else ''}{(meta_acc-single_best)*100:.2f}%)")

    # ── MNIST vs CIFAR-10 비교 ──
    print("\n" + "=" * 70)
    print("   MNIST vs CIFAR-10 비교")
    print("=" * 70)
    print(f"  {'모델':<30} {'MNIST':>8} {'CIFAR':>8} {'차이':>8}")
    print("-" * 70)

    for name in ['Dense', 'Top-K MoE', 'Engine A', 'Engine E',
                  'DualBrain (A+G)', 'Meta (AEGF)', 'Meta fixed',
                  'Hierarchical', 'Repulsion (A|G)', 'Repulsion Quad',
                  'SelfRef Field']:
        mnist = MNIST_RESULTS.get(name, 0)
        cifar = results.get(name, {}).get('acc', 0) * 100
        diff = cifar - mnist
        print(f"  {name:<30} {mnist:>7.2f}% {cifar:>7.2f}% {diff:>+7.2f}%")

    print("=" * 70)
    print("  CIFAR-10은 MNIST보다 훨씬 어려운 태스크 (컬러, 실물 객체)")
    print("  절대 정확도 하락보다 모델 간 상대 순위가 중요")
    print()


if __name__ == '__main__':
    main()
