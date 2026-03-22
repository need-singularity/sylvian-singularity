#!/usr/bin/env python3
"""LLM Expert 활성 측정기 + 재설계 방향 분석

사용법:
  python3 llm_expert_analyzer.py                    # 전체 LLM 비교
  python3 llm_expert_analyzer.py --model llama-8b   # 특정 모델
  python3 llm_expert_analyzer.py --redesign         # 골든존 재설계 제안
"""

import numpy as np
import argparse

# 알려진/추정된 LLM 아키텍처
LLM_SPECS = {
    'gpt2': {
        'name': 'GPT-2 (Dense)',
        'params': '1.5B', 'experts': 1, 'active': 1,
        'dropout': 0.1, 'lr_scale': 0.9, 'year': 2019,
        'type': 'dense',
    },
    'llama-8b': {
        'name': 'Llama 3 8B (Dense)',
        'params': '8B', 'experts': 1, 'active': 1,
        'dropout': 0.0, 'lr_scale': 0.95, 'year': 2024,
        'type': 'dense',
    },
    'llama-70b': {
        'name': 'Llama 3 70B (Dense)',
        'params': '70B', 'experts': 1, 'active': 1,
        'dropout': 0.0, 'lr_scale': 0.95, 'year': 2024,
        'type': 'dense',
    },
    'mixtral': {
        'name': 'Mixtral 8×7B (MoE)',
        'params': '46.7B', 'experts': 8, 'active': 2,
        'dropout': 0.1, 'lr_scale': 0.85, 'year': 2023,
        'type': 'moe',
    },
    'mixtral-large': {
        'name': 'Mixtral 8×22B',
        'params': '141B', 'experts': 8, 'active': 2,
        'dropout': 0.1, 'lr_scale': 0.85, 'year': 2024,
        'type': 'moe',
    },
    'deepseek-v2': {
        'name': 'DeepSeek-V2 MoE',
        'params': '236B', 'experts': 160, 'active': 6,
        'dropout': 0.1, 'lr_scale': 0.90, 'year': 2024,
        'type': 'moe',
    },
    'jamba': {
        'name': 'Jamba (Mamba+MoE)',
        'params': '52B', 'experts': 16, 'active': 2,
        'dropout': 0.1, 'lr_scale': 0.90, 'year': 2024,
        'type': 'hybrid',
    },
    'gpt4': {
        'name': 'GPT-4 (추정 MoE)',
        'params': '~1.8T', 'experts': 16, 'active': 2,
        'dropout': 0.1, 'lr_scale': 0.95, 'year': 2023,
        'type': 'moe',
    },
}


def analyze_llm(spec):
    """LLM 스펙 → D, P, I 매핑 → 골든존 판정"""
    if spec['type'] == 'dense':
        active_ratio = 1.0
    else:
        active_ratio = spec['active'] / spec['experts']

    D = max(spec['dropout'], 0.05)  # Dense는 dropout≈0 → D≈0.05
    P = spec['lr_scale']
    I = 1 - active_ratio

    G = D * P / max(I, 0.01)

    if 0.213 <= I <= 0.500:
        zone = "🎯 골든존"
    elif I < 0.213:
        zone = "⚡ 아래"
    else:
        zone = "○ 밖"

    return {
        **spec,
        'active_ratio': active_ratio,
        'D': D, 'P': P, 'I': I, 'G': G, 'zone': zone,
    }


def redesign_for_golden(spec):
    """골든존 진입을 위한 재설계 제안"""
    current = analyze_llm(spec)

    # 목표: I ∈ [0.24, 0.48]
    # I = 1 - active/experts
    # active = experts × (1 - I)
    target_I = 1/np.e  # 골든존 중심
    target_active = int(spec['experts'] * (1 - target_I))
    target_active = max(1, target_active)

    # Dropout 조정
    target_D = 0.5  # 골든존 최적

    return {
        'current': current,
        'target_I': target_I,
        'target_active': target_active,
        'target_D': target_D,
        'target_G': target_D * spec['lr_scale'] / target_I,
        'improvement': target_D * spec['lr_scale'] / target_I / max(current['G'], 0.01),
    }


def main():
    parser = argparse.ArgumentParser(description="LLM Expert 분석기")
    parser.add_argument('--model', type=str, default=None, choices=list(LLM_SPECS.keys()))
    parser.add_argument('--redesign', action='store_true', help="골든존 재설계 제안")
    args = parser.parse_args()

    print("═" * 70)
    print("   🤖 LLM Expert 활성 분석기 + 재설계 방향")
    print("═" * 70)

    if args.model:
        models = {args.model: LLM_SPECS[args.model]}
    else:
        models = LLM_SPECS

    # 분석
    print(f"\n  {'모델':25} │ {'Expert':>7} │ {'활성':>5} │ {'I':>5} │ {'D':>5} │ {'G':>6} │ 영역")
    print(f"  {'─'*25}─┼─{'─'*7}─┼─{'─'*5}─┼─{'─'*5}─┼─{'─'*5}─┼─{'─'*6}─┼─{'─'*10}")

    for key, spec in models.items():
        r = analyze_llm(spec)
        active_str = f"{r['active']}/{r['experts']}" if r['experts'] > 1 else "Dense"
        print(f"  {r['name']:25} │ {active_str:>7} │ {r['active_ratio']*100:>4.0f}% │ {r['I']:>5.3f} │ {r['D']:>5.2f} │ {r['G']:>6.2f} │ {r['zone']}")

    # I 축 시각화
    print(f"\n  I 축 위치:")
    for key, spec in models.items():
        r = analyze_llm(spec)
        pos = int(np.clip(r['I'], 0, 1) * 50)
        line = list("·" * 51)
        for gi in range(int(0.213*50), int(0.500*50)+1):
            if gi < 51: line[gi] = "░"
        if pos < 51: line[pos] = "●"
        short_name = r['name'][:15]
        print(f"    {short_name:15} │{''.join(line)}│ I={r['I']:.3f}")
    print(f"    {'':15} {'0.0':.<10}{'0.21':.<7}{'0.50':.<7}{'1.0'}")
    print(f"    {'':15} {'':>10}└─골든존─┘")

    # 재설계
    if args.redesign:
        print(f"\n{'═' * 70}")
        print(f"  골든존 재설계 제안")
        print(f"{'═' * 70}")

        for key, spec in models.items():
            rd = redesign_for_golden(spec)
            c = rd['current']

            print(f"\n  [{c['name']}]")
            print(f"    현재: Expert {c['active']}/{c['experts']} ({c['active_ratio']*100:.0f}%), I={c['I']:.3f}, G={c['G']:.2f} {c['zone']}")
            print(f"    제안: Expert {rd['target_active']}/{spec['experts']} ({(1-rd['target_I'])*100:.0f}%), I={rd['target_I']:.3f}, G={rd['target_G']:.2f} 🎯")
            print(f"    변경: Expert {c['active']}→{rd['target_active']} (+{rd['target_active']-c['active']}), Dropout {c['D']:.1f}→{rd['target_D']:.1f}")
            print(f"    예상 개선: ×{rd['improvement']:.1f}")

            if spec['type'] == 'dense':
                print(f"    ⚠️ Dense 모델 → MoE 전환 필요")
                print(f"       제안: {spec['experts']}→8 Expert MoE 전환, Top-K→볼츠만 라우터")

    print(f"\n{'═' * 70}")


if __name__ == '__main__':
    main()
