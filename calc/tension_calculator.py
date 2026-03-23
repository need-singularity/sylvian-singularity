#!/usr/bin/env python3
"""장력 계산기 — 장력값으로 정확도/예지/정체성 예측

사용법:
  python3 tension_calculator.py --tension 200
  python3 tension_calculator.py --tension 100 --compare 300
  python3 tension_calculator.py --scan
"""

import argparse
import math


# 실측 상수 (README에서)
C4B_D = 0.89       # Cohen's d (장력-정확도)
C6_AUC = 0.77      # 장력 단독 AUC (평균)
C7_RATIO = 0.577   # 오답/정답 장력 비
C15_AMPLIFY = 2.7  # 장력-정체성 증폭
C17_SEP = 2.77     # 방향 분리비

# 실측 통계 (analyze_tension.py, c4_verify에서)
CORRECT_MEAN = 201.3   # 정답 평균 장력
CORRECT_STD = 92.1
WRONG_MEAN = 120.3     # 오답 평균 장력
WRONG_STD = 57.9


def predict_accuracy(tension):
    """장력으로 정확도 추정 (로지스틱 모델)."""
    # P(correct) = sigmoid(a + b*z), z = (tension - mean) / std
    overall_mean = (CORRECT_MEAN * 0.975 + WRONG_MEAN * 0.025)
    overall_std = 90.0
    z = (tension - overall_mean) / overall_std
    # 로지스틱: a=3.5 (base), b=0.5 (slope from d=0.89)
    logit = 3.5 + 0.5 * z
    prob = 1 / (1 + math.exp(-logit))
    return prob


def predict_precognition(tension):
    """장력으로 예지 신뢰도 추정."""
    # AUC=0.77에서 유도: 장력이 높을수록 예측 신뢰
    if tension > CORRECT_MEAN:
        return 0.95  # 높은 장력 = 거의 확실히 맞음
    elif tension > (CORRECT_MEAN + WRONG_MEAN) / 2:
        return 0.85
    elif tension > WRONG_MEAN:
        return 0.70
    else:
        return 0.50  # 낮은 장력 = 동전 던지기


def predict_identity_effect(tension_low, tension_high):
    """두 장력 수준에서의 정체성 차이 증폭."""
    if tension_low <= 0:
        return float('inf')
    ratio = tension_high / tension_low
    # C15: T=1.5/T=0.1 → 2.7x 증폭, 선형 보간
    return ratio * (C15_AMPLIFY / 15.0)  # 스케일 조정


def main():
    parser = argparse.ArgumentParser(description='장력 계산기')
    parser.add_argument('--tension', type=float, help='장력값')
    parser.add_argument('--compare', type=float, help='비교할 두 번째 장력값')
    parser.add_argument('--scan', action='store_true', help='전 구간 스캔')
    args = parser.parse_args()

    if args.scan:
        print('=' * 60)
        print('  장력 전 구간 스캔')
        print('=' * 60)
        print(f'  {"Tension":>8} │ {"P(correct)":>10} │ {"Precog":>8} │ {"Zone":>10}')
        print(f'  {"─"*8}─┼─{"─"*10}─┼─{"─"*8}─┼─{"─"*10}')
        for t in [50, 75, 100, 120, 150, 175, 200, 250, 300, 400, 500]:
            p = predict_accuracy(t)
            prec = predict_precognition(t)
            if t < WRONG_MEAN:
                zone = '⚠️ 위험'
            elif t < (CORRECT_MEAN + WRONG_MEAN) / 2:
                zone = '🟨 불확실'
            elif t < CORRECT_MEAN:
                zone = '🟩 양호'
            else:
                zone = '🟩🟩 최적'
            print(f'  {t:>8.0f} │ {p*100:>9.1f}% │ {prec:>7.0f}% │ {zone:>10}')

        print()
        print(f'  기준값:')
        print(f'    오답 평균: {WRONG_MEAN:.1f}')
        print(f'    정답 평균: {CORRECT_MEAN:.1f}')
        print(f'    비율 C7:   {C7_RATIO:.3f} ≈ 1/√3')
        return

    if args.tension is None:
        parser.print_help()
        return

    t = args.tension
    p = predict_accuracy(t)
    prec = predict_precognition(t)

    print('=' * 50)
    print(f'  장력 = {t:.1f}')
    print('=' * 50)
    print(f'  예상 정확도:    {p*100:.1f}%')
    print(f'  예지 신뢰도:    {prec*100:.0f}%')
    print(f'  정답 평균 대비: {t/CORRECT_MEAN*100:.0f}%')
    print(f'  오답 평균 대비: {t/WRONG_MEAN*100:.0f}%')

    if t < WRONG_MEAN:
        print(f'  ⚠️ 위험 구간 — 오답 평균({WRONG_MEAN:.0f}) 이하')
    elif t > CORRECT_MEAN:
        print(f'  🟩 최적 구간 — 정답 평균({CORRECT_MEAN:.0f}) 이상')
    else:
        print(f'  🟨 중간 구간')

    if args.compare:
        t2 = args.compare
        p2 = predict_accuracy(t2)
        id_effect = predict_identity_effect(min(t, t2), max(t, t2))
        print(f'\n  비교: {t:.0f} vs {t2:.0f}')
        print(f'  정확도 차이: {(p2-p)*100:+.1f}%')
        print(f'  정체성 증폭: {id_effect:.2f}x')

    print('=' * 50)


if __name__ == '__main__':
    main()
