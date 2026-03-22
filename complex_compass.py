#!/usr/bin/env python3
"""복소 Compass 계산기 — 가설 069 확장

사용법:
  python3 complex_compass.py --theta 1.047  # θ=π/3
  python3 complex_compass.py --scan          # θ 전체 스캔
"""

import numpy as np
import argparse

def complex_fixed_point(theta, a=0.7, b=0.1):
    return b / (1 - a * np.exp(1j * theta))

def complex_compass(D, P, theta, a=0.7, b=0.1, n_samples=50000):
    fp = complex_fixed_point(theta, a, b)
    I_eff = abs(fp)
    if I_eff < 0.01:
        return None

    rng = np.random.default_rng(42)
    pop_d = rng.beta(2, 5, n_samples).clip(0.01, 0.99)
    pop_p = rng.beta(5, 2, n_samples).clip(0.01, 0.99)
    pop_i = rng.beta(5, 2, n_samples).clip(0.05, 0.99)
    pop_g = pop_d * pop_p / pop_i
    mu, sig = pop_g.mean(), pop_g.std()

    G = D * P / I_eff
    z = (G - mu) / sig

    # 나선 보너스
    phase_bonus = abs(np.sin(theta)) * 0.1

    compass = min(z/10, 1.0)*0.3 + 0.3 + (0.35)*0.4 + phase_bonus
    compass = max(0, min(1, compass))

    return {
        'theta': theta, 'theta_pi': theta/np.pi,
        'fp': fp, 'I_eff': I_eff,
        'G': G, 'z': z, 'compass': compass,
        'amplification': 1/I_eff,
        'direction': np.angle(fp),
    }

def main():
    parser = argparse.ArgumentParser(description="복소 Compass")
    parser.add_argument('--theta', type=float, default=None)
    parser.add_argument('--deficit', type=float, default=0.7)
    parser.add_argument('--plasticity', type=float, default=0.95)
    parser.add_argument('--scan', action='store_true')
    args = parser.parse_args()

    print("═" * 60)
    print("   🧭 복소 Compass 계산기")
    print("═" * 60)

    if args.scan:
        print(f"\n  θ 전체 스캔 (D={args.deficit}, P={args.plasticity}):")
        print(f"  {'θ/π':>5} │ {'|I*|':>6} │ {'G':>6} │ {'Z':>7} │ {'Compass':>7} │ {'증폭':>5} │ 영역")
        print(f"  {'─'*5}─┼─{'─'*6}─┼─{'─'*6}─┼─{'─'*7}─┼─{'─'*7}─┼─{'─'*5}─┼─{'─'*10}")

        for frac in np.linspace(0, 1, 21):
            theta = frac * np.pi
            r = complex_compass(args.deficit, args.plasticity, theta)
            if r:
                zone = "🎯골든" if 0.213 <= r['I_eff'] <= 0.5 else ("⚡" if r['I_eff'] < 0.213 else "○")
                print(f"  {frac:>5.2f} │ {r['I_eff']:>6.4f} │ {r['G']:>6.2f} │ {r['z']:>6.2f}σ │ {r['compass']*100:>6.1f}% │ {r['amplification']:>5.1f} │ {zone}")
    elif args.theta is not None:
        r = complex_compass(args.deficit, args.plasticity, args.theta)
        if r:
            print(f"\n  θ = {r['theta']:.4f} = {r['theta_pi']:.4f}π")
            print(f"  I* = {r['fp'].real:.4f} + {r['fp'].imag:.4f}i")
            print(f"  |I*| = {r['I_eff']:.4f}")
            print(f"  G = {r['G']:.2f}")
            print(f"  Z = {r['z']:.2f}σ")
            print(f"  Compass = {r['compass']*100:.1f}%")
            print(f"  증폭 = ×{r['amplification']:.1f}")
    else:
        print("  --scan 또는 --theta <값> 지정")

if __name__ == '__main__':
    main()
