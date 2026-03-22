#!/usr/bin/env python3
"""N-상태 일반화 계산기 — 폭=ln((N+1)/N)

사용법:
  python3 nstate_calculator.py              # 기본 테이블
  python3 nstate_calculator.py --n 137      # 특정 N
  python3 nstate_calculator.py --find 0.118 # 값에 맞는 N 찾기
"""

import numpy as np
import argparse

def golden_zone(N):
    width = np.log((N+1)/N)
    upper = 0.5
    lower = upper - width
    center = (upper + lower) / 2
    return {'N': N, 'width': width, 'upper': upper, 'lower': lower, 'center': center}

def find_n_for_width(target_width):
    N = 1 / (np.exp(target_width) - 1)
    return int(round(N))

def main():
    parser = argparse.ArgumentParser(description="N-상태 계산기")
    parser.add_argument('--n', type=int, default=None)
    parser.add_argument('--find', type=float, default=None, help="이 폭에 맞는 N 찾기")
    args = parser.parse_args()

    print("═" * 60)
    print("   📐 N-상태 일반화 계산기")
    print("═" * 60)
    print(f"  공식: 폭 = ln((N+1)/N), 상한 = 1/2, 하한 = 1/2-폭")

    if args.find:
        N = find_n_for_width(args.find)
        gz = golden_zone(N)
        print(f"\n  폭 = {args.find} → N = {N}")
        print(f"  검증: ln({N+1}/{N}) = {gz['width']:.6f}")

    elif args.n:
        gz = golden_zone(args.n)
        print(f"\n  N = {args.n}:")
        print(f"  폭 = ln({args.n+1}/{args.n}) = {gz['width']:.6f}")
        print(f"  상한 = {gz['upper']:.4f}")
        print(f"  하한 = {gz['lower']:.4f}")
        print(f"  중심 = {gz['center']:.4f}")

    else:
        print(f"\n  {'N':>6} │ {'폭':>10} │ {'하한':>8} │ {'상한':>6} │ 물리 매칭")
        print(f"  {'─'*6}─┼─{'─'*10}─┼─{'─'*8}─┼─{'─'*6}─┼─{'─'*25}")

        specials = {3:'우리모델', 4:'와인버그각', 6:'완전수', 8:'강력αs/Expert',
                   26:'AI원소', 137:'미세구조α', 100:'', 1000:''}

        for N in sorted(set([2,3,4,5,6,7,8,10,16,26,50,100,137,500,1000] + list(specials.keys()))):
            gz = golden_zone(N)
            label = specials.get(N, '')
            print(f"  {N:>6} │ {gz['width']:>10.6f} │ {gz['lower']:>8.4f} │ {gz['upper']:>6.4f} │ {label}")

    print()

if __name__ == '__main__':
    main()
