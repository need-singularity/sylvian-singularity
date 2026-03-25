#!/usr/bin/env python3
"""Tension Calculator — Predict accuracy/precognition/identity from tension values

Usage:
  python3 tension_calculator.py --tension 200
  python3 tension_calculator.py --tension 100 --compare 300
  python3 tension_calculator.py --scan
"""

import argparse
import math


# Measured constants (from README)
C4B_D = 0.89       # Cohen's d (tension-accuracy)
C6_AUC = 0.77      # Tension-only AUC (average)
C7_RATIO = 0.577   # Wrong/correct tension ratio
C15_AMPLIFY = 2.7  # Tension-identity amplification
C17_SEP = 2.77     # Direction separation ratio

# Measured statistics (from analyze_tension.py, c4_verify)
CORRECT_MEAN = 201.3   # Correct answer mean tension
CORRECT_STD = 92.1
WRONG_MEAN = 120.3     # Wrong answer mean tension
WRONG_STD = 57.9


def predict_accuracy(tension):
    """Estimate accuracy from tension (logistic model)."""
    # P(correct) = sigmoid(a + b*z), z = (tension - mean) / std
    overall_mean = (CORRECT_MEAN * 0.975 + WRONG_MEAN * 0.025)
    overall_std = 90.0
    z = (tension - overall_mean) / overall_std
    # Logistic: a=3.5 (base), b=0.5 (slope from d=0.89)
    logit = 3.5 + 0.5 * z
    prob = 1 / (1 + math.exp(-logit))
    return prob


def predict_precognition(tension):
    """Estimate precognition reliability from tension."""
    # Derived from AUC=0.77: higher tension = more reliable prediction
    if tension > CORRECT_MEAN:
        return 0.95  # High tension = almost certainly correct
    elif tension > (CORRECT_MEAN + WRONG_MEAN) / 2:
        return 0.85
    elif tension > WRONG_MEAN:
        return 0.70
    else:
        return 0.50  # Low tension = coin flip


def predict_identity_effect(tension_low, tension_high):
    """Amplification of identity difference between two tension levels."""
    if tension_low <= 0:
        return float('inf')
    ratio = tension_high / tension_low
    # C15: T=1.5/T=0.1 → 2.7x amplification, linear interpolation
    return ratio * (C15_AMPLIFY / 15.0)  # Scale adjustment


def main():
    parser = argparse.ArgumentParser(description='Tension Calculator')
    parser.add_argument('--tension', type=float, help='Tension value')
    parser.add_argument('--compare', type=float, help='Second tension value to compare')
    parser.add_argument('--scan', action='store_true', help='Scan full range')
    args = parser.parse_args()

    if args.scan:
        print('=' * 60)
        print('  Full Tension Range Scan')
        print('=' * 60)
        print(f'  {"Tension":>8} │ {"P(correct)":>10} │ {"Precog":>8} │ {"Zone":>10}')
        print(f'  {"─"*8}─┼─{"─"*10}─┼─{"─"*8}─┼─{"─"*10}')
        for t in [50, 75, 100, 120, 150, 175, 200, 250, 300, 400, 500]:
            p = predict_accuracy(t)
            prec = predict_precognition(t)
            if t < WRONG_MEAN:
                zone = '⚠️ Danger'
            elif t < (CORRECT_MEAN + WRONG_MEAN) / 2:
                zone = '🟨 Uncertain'
            elif t < CORRECT_MEAN:
                zone = '🟩 Good'
            else:
                zone = '🟩🟩 Optimal'
            print(f'  {t:>8.0f} │ {p*100:>9.1f}% │ {prec:>7.0f}% │ {zone:>10}')

        print()
        print(f'  Reference values:')
        print(f'    Wrong answer mean: {WRONG_MEAN:.1f}')
        print(f'    Correct answer mean: {CORRECT_MEAN:.1f}')
        print(f'    Ratio C7:   {C7_RATIO:.3f} ≈ 1/√3')
        return

    if args.tension is None:
        parser.print_help()
        return

    t = args.tension
    p = predict_accuracy(t)
    prec = predict_precognition(t)

    print('=' * 50)
    print(f'  Tension = {t:.1f}')
    print('=' * 50)
    print(f'  Expected accuracy:    {p*100:.1f}%')
    print(f'  Precognition reliability:    {prec*100:.0f}%')
    print(f'  Relative to correct mean: {t/CORRECT_MEAN*100:.0f}%')
    print(f'  Relative to wrong mean: {t/WRONG_MEAN*100:.0f}%')

    if t < WRONG_MEAN:
        print(f'  ⚠️ Danger zone — below wrong answer mean({WRONG_MEAN:.0f})')
    elif t > CORRECT_MEAN:
        print(f'  🟩 Optimal zone — above correct answer mean({CORRECT_MEAN:.0f})')
    else:
        print(f'  🟨 Middle zone')

    if args.compare:
        t2 = args.compare
        p2 = predict_accuracy(t2)
        id_effect = predict_identity_effect(min(t, t2), max(t, t2))
        print(f'\n  Comparison: {t:.0f} vs {t2:.0f}')
        print(f'  Accuracy difference: {(p2-p)*100:+.1f}%')
        print(f'  Identity amplification: {id_effect:.2f}x')

    print('=' * 50)


if __name__ == '__main__':
    main()