#!/usr/bin/env python3
"""뇌 데이터 분석기 — GABA/구조/가소성 → D,P,I 매핑 → 골든존 판정

사용법:
  python3 brain_analyzer.py --gaba 0.8 --deficit 0.4 --plasticity 0.85
  python3 brain_analyzer.py --profile einstein
  python3 brain_analyzer.py --profile savant
"""

import numpy as np
import argparse
import sys
sys.path.append('.')

def gaba_to_inhibition(gaba_mmol):
    """GABA 농도(mmol/L) → Inhibition 매핑 (가설 155)"""
    # 정상 GABA ≈ 1.0 mmol/L → I ≈ 0.6
    # 선형 매핑: I = 0.6 × gaba
    I = np.clip(0.6 * gaba_mmol, 0.05, 0.95)
    return I

def analyze_brain(D, P, I, name=""):
    """뇌 파라미터 → Genius Score + 골든존 판정"""
    G = D * P / I

    # 모집단 통계
    rng = np.random.default_rng(42)
    pop_d = rng.beta(2, 5, 50000).clip(0.01, 0.99)
    pop_p = rng.beta(5, 2, 50000).clip(0.01, 0.99)
    pop_i = rng.beta(5, 2, 50000).clip(0.05, 0.99)
    pop_g = pop_d * pop_p / pop_i

    z = (G - pop_g.mean()) / pop_g.std()

    # 골든존 판정
    if 0.213 <= I <= 0.500:
        zone = "🎯 골든존!"
    elif I < 0.213:
        zone = "⚡ 골든존 아래 (혼돈 위험)"
    else:
        zone = "○ 골든존 밖 (과억제)"

    # 특이점 등급
    if abs(z) > 5:
        grade = "🔴 극단적 특이점"
    elif abs(z) > 3:
        grade = "🟠 강한 특이점"
    elif abs(z) > 2:
        grade = "🟡 특이점"
    else:
        grade = "○ 정상 범위"

    # 보존법칙
    conservation = D * P  # G×I = D×P

    print(f"\n  {'═' * 50}")
    if name:
        print(f"  프로필: {name}")
    print(f"  {'═' * 50}")
    print(f"  입력:")
    print(f"    Deficit(결손)     = {D:.2f}")
    print(f"    Plasticity(가소성) = {P:.2f}")
    print(f"    Inhibition(억제)  = {I:.2f}")
    print(f"  {'─' * 50}")
    print(f"  결과:")
    print(f"    Genius Score = {G:.2f}")
    print(f"    Z-Score      = {z:.2f}σ  {grade}")
    print(f"    골든존        = {zone}")
    print(f"    G×I = D×P    = {conservation:.4f} (보존)")

    # 그래프
    pos = int(np.clip(I, 0, 1) * 40)
    line = list("·" * 41)
    golden_lo = int(0.213 * 40)
    golden_hi = int(0.500 * 40)
    for gi in range(golden_lo, golden_hi + 1):
        if gi < 41: line[gi] = "░"
    third = int(1/3 * 40)
    if third < 41: line[third] = "│"
    if pos < 41: line[pos] = "●"
    print(f"    {''.join(line)}")
    print(f"    0{'─'*8}0.21{'░'*5}1/3{'░'*5}0.50{'─'*8}1.0")
    print(f"  {'═' * 50}")

PROFILES = {
    'normal': {'D': 0.1, 'P': 0.6, 'I': 0.6, 'name': '정상인'},
    'einstein': {'D': 0.5, 'P': 0.9, 'I': 0.4, 'name': '아인슈타인 (추정)'},
    'savant': {'D': 0.7, 'P': 0.85, 'I': 0.35, 'name': '서번트 (추정)'},
    'epilepsy': {'D': 0.6, 'P': 0.7, 'I': 0.15, 'name': '간질 환자 (추정)'},
    'meditation': {'D': 0.3, 'P': 0.8, 'I': 0.36, 'name': '명상 수행자 (추정)'},
    'child': {'D': 0.2, 'P': 0.95, 'I': 0.5, 'name': '어린이'},
    'elderly': {'D': 0.15, 'P': 0.3, 'I': 0.7, 'name': '노인'},
    'acquired': {'D': 0.6, 'P': 0.7, 'I': 0.3, 'name': '후천적 서번트 (추정)'},
    'sylvian': {'D': 0.4, 'P': 0.85, 'I': 0.4, 'name': '실비우스열 부분 결여'},
}

def main():
    parser = argparse.ArgumentParser(description="뇌 데이터 분석기")
    parser.add_argument('--deficit', type=float, default=None)
    parser.add_argument('--plasticity', type=float, default=None)
    parser.add_argument('--inhibition', type=float, default=None)
    parser.add_argument('--gaba', type=float, default=None, help="GABA 농도 (mmol/L)")
    parser.add_argument('--profile', type=str, default=None, choices=list(PROFILES.keys()))
    parser.add_argument('--all', action='store_true', help="모든 프로필 비교")
    args = parser.parse_args()

    print("═" * 60)
    print("   🧠 뇌 데이터 분석기")
    print("═" * 60)

    if args.all:
        for key, prof in PROFILES.items():
            analyze_brain(prof['D'], prof['P'], prof['I'], prof['name'])
    elif args.profile:
        prof = PROFILES[args.profile]
        analyze_brain(prof['D'], prof['P'], prof['I'], prof['name'])
    elif args.deficit is not None:
        I = args.inhibition or (gaba_to_inhibition(args.gaba) if args.gaba else 0.5)
        P = args.plasticity or 0.8
        analyze_brain(args.deficit, P, I)
    else:
        print("  --profile, --all, 또는 --deficit/--plasticity/--inhibition 지정")
        print(f"  프로필: {', '.join(PROFILES.keys())}")

if __name__ == '__main__':
    main()
