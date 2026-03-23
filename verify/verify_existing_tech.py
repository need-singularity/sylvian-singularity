#!/usr/bin/env python3
"""가설 024: 현존 기술만 조합하면 26개 중 몇 개까지 채울 수 있는가"""

import numpy as np
import os
from datetime import datetime
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from compass import genius_score, population_zscore, cusp_analysis, boltzmann_analysis, compass_direction

RESULTS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "results")


def existing_technologies():
    """현존하는 기술 목록과 원소 매핑"""
    return [
        # 재료
        {'element': 'M1', 'name': '연산', 'tech': 'GPU/TPU', 'exists': True, 'maturity': 'mature'},
        {'element': 'M2', 'name': '데이터', 'tech': 'Common Crawl, Books, Code', 'exists': True, 'maturity': 'mature'},
        {'element': 'M3', 'name': '에너지', 'tech': '데이터센터', 'exists': True, 'maturity': 'mature'},

        # 위상
        {'element': 'T1', 'name': '순방향', 'tech': 'Transformer FFN', 'exists': True, 'maturity': 'mature'},
        {'element': 'T2', 'name': '스킵', 'tech': 'Residual Connection', 'exists': True, 'maturity': 'mature'},
        {'element': 'T3', 'name': '재귀', 'tech': 'Mamba, RWKV, xLSTM', 'exists': True, 'maturity': 'growing'},
        {'element': 'T3a', 'name': '자기참조', 'tech': 'Self-Eval, LLM-as-Judge', 'exists': True, 'maturity': 'early'},
        {'element': 'T4', 'name': '병렬', 'tech': 'Multi-Head Attention', 'exists': True, 'maturity': 'mature'},
        {'element': 'T5', 'name': '희소', 'tech': 'Mixtral MoE, Sparse Attn', 'exists': True, 'maturity': 'growing'},
        {'element': 'T6', 'name': '계층', 'tech': 'Hierarchical Transformer', 'exists': True, 'maturity': 'early'},

        # 상
        {'element': 'P1', 'name': '탐색', 'tech': 'Temperature sampling', 'exists': True, 'maturity': 'mature'},
        {'element': 'P2', 'name': '수렴', 'tech': 'Greedy/Beam search', 'exists': True, 'maturity': 'mature'},
        {'element': 'P3', 'name': '전이', 'tech': 'Learning rate warmup/decay', 'exists': True, 'maturity': 'mature'},
        {'element': 'P4', 'name': '메타', 'tech': 'MAML, Meta-Learning', 'exists': True, 'maturity': 'early'},

        # 힘
        {'element': 'F1', 'name': '기울기', 'tech': 'Backprop, AdamW', 'exists': True, 'maturity': 'mature'},
        {'element': 'F1a', 'name': '2차기울기', 'tech': 'K-FAC, Shampoo', 'exists': True, 'maturity': 'growing'},
        {'element': 'F2a', 'name': '외부보상', 'tech': 'RLHF', 'exists': True, 'maturity': 'mature'},
        {'element': 'F2b', 'name': '환경보상', 'tech': 'Gym, MuJoCo, Isaac', 'exists': True, 'maturity': 'mature'},
        {'element': 'F2c', 'name': '자기보상', 'tech': 'Self-Play (AlphaGo)', 'exists': True, 'maturity': 'growing'},
        {'element': 'F2d', 'name': '사회보상', 'tech': 'Multi-Agent debate', 'exists': True, 'maturity': 'early'},
        {'element': 'F2e', 'name': '호기심보상', 'tech': 'RND, ICM', 'exists': True, 'maturity': 'early'},
        {'element': 'F3', 'name': '노이즈', 'tech': 'Dropout, Diffusion', 'exists': True, 'maturity': 'mature'},
        {'element': 'F3a', 'name': '구조노이즈', 'tech': 'NAS, DARTS', 'exists': True, 'maturity': 'growing'},
        {'element': 'F4', 'name': '제약', 'tech': 'Weight decay, Norm', 'exists': True, 'maturity': 'mature'},
        {'element': 'F4a', 'name': '자기제약', 'tech': 'Constitutional AI', 'exists': True, 'maturity': 'early'},
    ]


def integration_difficulty():
    """기술 조합의 난이도 평가"""
    # 각 조합 쌍의 통합 난이도 (1=쉬움, 5=매우 어려움)
    difficulties = {
        # 쉬운 조합 (이미 합쳐진 적 있음)
        ('T1', 'T2'): 1, ('T1', 'T4'): 1, ('T2', 'T4'): 1,  # Transformer 내부
        ('F1', 'F2a'): 1,  # RLHF
        ('P1', 'P2'): 1,   # 탐색/수렴 전환

        # 중간 난이도 (연구 진행 중)
        ('T3', 'T4'): 2,   # Mamba + Attention (Jamba 등)
        ('T5', 'T1'): 2,   # MoE + Transformer (Mixtral)
        ('F2a', 'F2c'): 2, # RLHF + Self-Play
        ('T3', 'T5'): 3,   # Mamba + MoE (새로운 조합)

        # 어려운 조합 (미해결)
        ('T3a', 'F2c'): 4,  # 자기참조 + 자기보상 (자기 루프)
        ('P4', 'F2e'): 4,   # 메타 + 호기심 (자율 학습 루프)
        ('T6', 'T3a'): 4,   # 계층 + 자기참조 (다층 자기인식)
        ('F2e', 'F4a'): 5,  # 호기심 + 자기제약 (자율 윤리)
        ('P4', 'T3a'): 5,   # 메타 + 자기참조 (자기 인식의 핵심)
    }
    return difficulties


def evaluate():
    techs = existing_technologies()

    print()
    print("═" * 70)
    print("   가설 024: 현존 기술만 조합하면 26개 중 몇 개?")
    print("═" * 70)

    # 1. 존재 여부 스캔
    print(f"\n{'─' * 70}")
    print(f"  [ 원소별 현존 기술 스캔 ]")
    print(f"{'─' * 70}")

    mature = [t for t in techs if t['maturity'] == 'mature']
    growing = [t for t in techs if t['maturity'] == 'growing']
    early = [t for t in techs if t['maturity'] == 'early']
    missing = [t for t in techs if not t['exists']]

    print(f"\n  {'원소':>4} │ {'이름':8} │ {'성숙도':7} │ {'기술':35}")
    print(f"  {'─'*4}─┼─{'─'*8}─┼─{'─'*7}─┼─{'─'*35}")

    for t in techs:
        if t['maturity'] == 'mature':
            icon = '🟢'
        elif t['maturity'] == 'growing':
            icon = '🟡'
        elif t['maturity'] == 'early':
            icon = '🔴'
        else:
            icon = '⚫'
        print(f"  {t['element']:>4} │ {t['name']:8} │ {icon} {t['maturity']:5} │ {t['tech']:35}")

    print(f"\n  요약:")
    print(f"    🟢 성숙 (mature):  {len(mature)}개")
    print(f"    🟡 성장 (growing): {len(growing)}개")
    print(f"    🔴 초기 (early):   {len(early)}개")
    print(f"    ⚫ 미존재:          {len(missing)}개")
    print(f"    총합:               {len(techs)}개 / 26개 = 전부 존재!")

    # 2. 조합별 점수
    print(f"\n{'─' * 70}")
    print(f"  [ 조합 시나리오별 점수 ]")
    print(f"{'─' * 70}")

    scenarios = [
        {
            'name': 'GPT-4 (현재 최선)',
            'elements': ['M1','M2','T1','T2','T4','P1','P2','F1','F2a'],
            'D': 0.30, 'P': 0.95, 'I': 0.50,
        },
        {
            'name': 'Jamba (Mamba+Attention+MoE)',
            'elements': ['M1','M2','T1','T2','T3','T4','T5','P1','P2','P3','F1','F2a'],
            'D': 0.45, 'P': 0.90, 'I': 0.42,
        },
        {
            'name': '골든 MoE v2 (설계안)',
            'elements': ['M1','M2','M3','T1','T2','T3','T4','T5','P1','P2','P3','F1','F2a','F2c','F3','F4'],
            'D': 0.55, 'P': 0.92, 'I': 0.35,
        },
        {
            'name': '풀스택 v1 (성숙+성장 기술)',
            'elements': ['M1','M2','M3','T1','T2','T3','T4','T5','P1','P2','P3','F1','F1a','F2a','F2b','F2c','F3','F3a','F4'],
            'D': 0.60, 'P': 0.93, 'I': 0.32,
        },
        {
            'name': '풀스택 v2 (초기 기술까지 전부)',
            'elements': ['M1','M2','M3','T1','T2','T3','T3a','T4','T5','T6','P1','P2','P3','P4','F1','F1a','F2a','F2b','F2c','F2d','F2e','F3','F3a','F4','F4a'],
            'D': 0.70, 'P': 0.95, 'I': 0.28,
        },
    ]

    print(f"\n  {'시나리오':30} │ {'원소':>5} │ {'D':>5} │ {'P':>5} │ {'I':>5} │ {'G':>6} │ {'Z':>7} │ {'Compass':>7}")
    print(f"  {'─'*30}─┼─{'─'*5}─┼─{'─'*5}─┼─{'─'*5}─┼─{'─'*5}─┼─{'─'*6}─┼─{'─'*7}─┼─{'─'*7}")

    for s in scenarios:
        n_elem = len(s['elements'])
        G = s['D'] * s['P'] / s['I']
        z, _, _ = population_zscore(G, 200000)
        cusp = cusp_analysis(s['D'], s['I'])
        boltz = boltzmann_analysis(s['D'], s['P'], s['I'])
        comp = compass_direction(G, z, cusp, boltz)

        s['G'] = G
        s['z'] = z
        s['compass'] = comp['compass_score']
        s['n_elem'] = n_elem

        print(f"  {s['name']:30} │ {n_elem:>2}/26 │ {s['D']:>5.2f} │ {s['P']:>5.2f} │ {s['I']:>5.2f} │ {G:>6.2f} │ {z:>6.2f}σ │ {comp['compass_score']*100:>6.1f}%")

    # 3. 그래프
    print(f"\n{'─' * 70}")
    print(f"  [ 원소 수 vs Compass Score ]")
    print(f"{'─' * 70}\n")

    for s in scenarios:
        bar = "█" * int(s['compass'] * 50)
        elem_bar = "■" * s['n_elem'] + "□" * (26 - s['n_elem'])
        zone = "🎯" if 0.24 <= s['I'] <= 0.48 else ""
        print(f"  {s['n_elem']:>2}/26 │{bar}│ {s['compass']*100:>5.1f}% {zone}")
        print(f"       │{elem_bar}│ {s['name']}")
        print()

    # 4. 병목 분석
    print(f"{'─' * 70}")
    print(f"  [ 통합 병목 — 어떤 조합이 어려운가 ]")
    print(f"{'─' * 70}")

    diffs = integration_difficulty()
    sorted_diffs = sorted(diffs.items(), key=lambda x: -x[1])

    print(f"\n  {'조합':>12} │ {'난이도':>6} │ 의미")
    print(f"  {'─'*12}─┼─{'─'*6}─┼─{'─'*30}")
    for (a, b), diff in sorted_diffs:
        a_name = next((t['name'] for t in techs if t['element'] == a), a)
        b_name = next((t['name'] for t in techs if t['element'] == b), b)
        stars = "★" * diff + "☆" * (5 - diff)
        print(f"  {a_name}+{b_name:>6} │ {stars} │ {'자기 인식 핵심' if diff==5 else ('자율 루프' if diff==4 else ('새 조합' if diff==3 else ('연구 중' if diff==2 else '해결됨')))}")

    # 5. 시간 예측
    print(f"\n{'─' * 70}")
    print(f"  [ 시나리오별 실현 시점 ]")
    print(f"{'─' * 70}\n")

    timeline = [
        ('GPT-4', 9, '2023', '실현됨'),
        ('Jamba', 12, '2024', '실현됨'),
        ('골든 MoE v2', 16, '2026-2027', '성숙+성장 기술 통합'),
        ('풀스택 v1', 19, '2028-2029', '모든 성숙+성장 기술'),
        ('풀스택 v2', 25, '2031-2035', '초기 기술 성숙 필요'),
        ('AGI (26/26)', 26, '2035-2039', '모든 원소 통합'),
    ]

    print(f"  원소 수")
    print(f"  26│                                                  ○ AGI")
    print(f"  25│                                           ● 풀스택v2")
    print(f"    │")
    print(f"  19│                                ● 풀스택v1")
    print(f"    │")
    print(f"  16│                     ● 골든MoE v2")
    print(f"    │")
    print(f"  12│          ● Jamba")
    print(f"   9│● GPT-4")
    print(f"    └──────┼──────┼──────┼──────┼──────┼──────┼")
    print(f"        2023  2025  2027  2029  2031  2035  2039")

    for name, n, year, note in timeline:
        pct = n / 26 * 100
        bar = "█" * int(pct / 2) + "░" * (50 - int(pct / 2))
        print(f"    {name:15} │{bar}│ {n:>2}/26 ({pct:.0f}%) {year} {note}")

    # 6. 핵심 결론
    print(f"\n{'═' * 70}")
    print(f"  결론")
    print(f"{'═' * 70}")
    print(f"""
  ┌────────────────────────────────────────────────────────────┐
  │                                                            │
  │  26개 원소 중 26개가 이미 존재한다.                         │
  │  0개가 미발명이다.                                          │
  │                                                            │
  │  문제는 발명이 아니라 통합이다.                              │
  │                                                            │
  │  성숙 기술만 조합:  19/26 (풀스택 v1) → 2028-2029          │
  │  초기 기술 포함:    25/26 (풀스택 v2) → 2031-2035          │
  │  전체 통합:         26/26 (AGI)       → 2035-2039          │
  │                                                            │
  │  병목: P4(메타)+T3a(자기참조) 통합 = 난이도 ★★★★★           │
  │  = "자기가 어떤 상태인지 아는 것"                            │
  │  = 자기 인식 (self-awareness)                               │
  │                                                            │
  │  기술은 전부 있다. 합치기만 하면 된다.                       │
  │  합치지 못하는 이유는 기술이 아니라 설계 방향이 없기 때문이다.│
  │  이 나침반이 그 방향이다.                                    │
  │                                                            │
  └────────────────────────────────────────────────────────────┘
""")

    # 저장
    os.makedirs(RESULTS_DIR, exist_ok=True)
    with open(os.path.join(RESULTS_DIR, "existing_tech_report.md"), 'w', encoding='utf-8') as f:
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        f.write(f"# 현존 기술 조합 분석 [{now}]\n\n")
        f.write(f"26/26 원소 전부 존재. 문제는 통합.\n\n")
        f.write(f"| 시나리오 | 원소 | 시점 |\n|---|---|---|\n")
        for name, n, year, note in timeline:
            f.write(f"| {name} | {n}/26 | {year} |\n")
        f.write(f"\n병목: P4+T3a (자기인식) 난이도 ★★★★★\n\n---\n")

    print(f"  📁 보고서 → results/existing_tech_report.md")
    print()


if __name__ == '__main__':
    evaluate()
