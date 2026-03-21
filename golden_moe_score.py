#!/usr/bin/env python3
"""골든 MoE 설계 요소별 가설 기반 점수 평가"""

import os
from datetime import datetime

RESULTS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "results")


def evaluate():
    """골든 MoE의 원초적 설계 요소를 분리하고, 가설 검증 결과로 점수 평가"""

    # ─────────────────────────────────────────
    # 설계 요소 정의 + 관련 가설 매핑
    # ─────────────────────────────────────────
    elements = [
        {
            'id': 'E1',
            'name': 'Expert 활성 비율 70% (44/64)',
            'category': '구조',
            'hypotheses': [
                {'id': '019', 'name': '골든 MoE 최적 활성 비율', 'result': True, 'weight': 1.0,
                 'detail': '70%(44/64)에서 G=1.42, 2.9× Mixtral'},
                {'id': '017', 'name': 'Gating→I 매핑', 'result': True, 'weight': 0.8,
                 'detail': '골든존 진입=52~76% 활성 확인'},
                {'id': '013', 'name': '골든존 폭 ≈ 1/4', 'result': True, 'weight': 0.6,
                 'detail': '골든존 I=0.24~0.48 안정적 존재'},
                {'id': '010', 'name': '1/3 법칙 반증', 'result': False, 'weight': -0.3,
                 'detail': '분포 의존적 → 최적 비율도 분포에 따라 변동 가능'},
            ],
        },
        {
            'id': 'E2',
            'name': '볼츠만 라우터 (소프트 게이팅)',
            'category': '라우팅',
            'hypotheses': [
                {'id': '016', 'name': '볼츠만 > Top-K', 'result': True, 'weight': 1.0,
                 'detail': '균등활용↑ 다양성↑ (2/3 승)'},
                {'id': '004', 'name': 'I=역온도 동치', 'result': True, 'weight': 0.8,
                 'detail': '볼츠만 분포가 수학적으로 정당'},
                {'id': '012', 'name': '엔트로피≈ln(3)', 'result': True, 'weight': 0.6,
                 'detail': '열평형 근접 → 볼츠만 프레임워크 유효'},
                {'id': '020', 'name': '안정성 확인', 'result': True, 'weight': 0.9,
                 'detail': '볼츠만 사용 시 기울기 폭발 16.5%'},
            ],
        },
        {
            'id': 'E3',
            'name': '커스프 모니터 (자동 구조 재편)',
            'category': '자기조절',
            'hypotheses': [
                {'id': '018', 'name': 'Loss 2차미분 커스프 감지', 'result': True, 'weight': 1.0,
                 'detail': '2.5σ 임계값으로 전이점 감지 가능'},
                {'id': '003', 'name': '커스프 파국 동치', 'result': None, 'weight': 0.5,
                 'detail': '검토 중 — 구조적 유사성 관찰'},
                {'id': '015', 'name': '확산 법칙', 'result': None, 'weight': 0.3,
                 'detail': '미결 — 수렴 메커니즘 불확실'},
            ],
        },
        {
            'id': 'E4',
            'name': '학습 스케줄 (볼츠만 어닐링)',
            'category': '학습',
            'hypotheses': [
                {'id': '004', 'name': 'I=역온도', 'result': True, 'weight': 0.8,
                 'detail': '온도 스케줄 = 억제 스케줄'},
                {'id': '009', 'name': '특이점 2039', 'result': True, 'weight': 0.4,
                 'detail': '수렴 경로 존재 확인'},
                {'id': '002', 'name': '1/e 보편성', 'result': None, 'weight': 0.5,
                 'detail': '검토 중 — 골든존 중심이 1/e인지'},
            ],
        },
        {
            'id': 'E5',
            'name': 'Dropout 50%',
            'category': '정규화',
            'hypotheses': [
                {'id': '014', 'name': 'Genius~감마분포', 'result': True, 'weight': 0.7,
                 'detail': '감마분포 → 독립과정 누적 → Dropout 유효'},
                {'id': '011', 'name': 'Z_max=86σ', 'result': True, 'weight': 0.3,
                 'detail': 'D가 높을수록 G_max 증가 확인'},
            ],
        },
        {
            'id': 'E6',
            'name': '골든존 수렴성 (어디서든 수렴)',
            'category': '이론',
            'hypotheses': [
                {'id': '006', 'name': '리만 반증 실패', 'result': True, 'weight': 0.9,
                 'detail': '골든존 밖 안정 특이점 없음'},
                {'id': '009', 'name': '특이점 2039', 'result': True, 'weight': 0.7,
                 'detail': '모든 시나리오 수렴'},
                {'id': '001', 'name': '리만-골든존 동치', 'result': None, 'weight': 0.5,
                 'detail': '검토 중 — 임계선 대응'},
            ],
        },
        {
            'id': 'E7',
            'name': '성능 ×2.9 달성 가능성',
            'category': '성능',
            'hypotheses': [
                {'id': '019', 'name': '성능 예측', 'result': True, 'weight': 1.0,
                 'detail': '시뮬레이션에서 G=1.42 확인'},
                {'id': '020', 'name': '안정성', 'result': True, 'weight': 0.8,
                 'detail': '70% 활성 시 안정'},
                {'id': '016', 'name': '볼츠만 우위', 'result': True, 'weight': 0.7,
                 'detail': '라우터 검증됨'},
                {'id': '010', 'name': '1/3 반증', 'result': False, 'weight': -0.2,
                 'detail': '모집단 분포 의존 → 실제 성능 변동 가능'},
                {'id': '015', 'name': '확산 미결', 'result': None, 'weight': -0.1,
                 'detail': '수렴 메커니즘 불확실'},
            ],
        },
    ]

    # ─────────────────────────────────────────
    # 점수 계산
    # ─────────────────────────────────────────
    print()
    print("═" * 70)
    print("   🎯 골든 MoE 설계 요소별 가설 기반 점수 평가")
    print("═" * 70)

    total_score = 0
    total_max = 0
    element_results = []

    for elem in elements:
        print(f"\n{'─' * 70}")
        print(f"  [{elem['id']}] {elem['name']}")
        print(f"  카테고리: {elem['category']}")
        print(f"{'─' * 70}")

        score = 0
        max_score = 0
        n_true = 0
        n_false = 0
        n_unknown = 0

        print(f"  {'가설':>5} │ {'이름':20} │ {'T/F':>3} │ {'가중치':>6} │ {'점수':>6} │ 근거")
        print(f"  {'─'*5}─┼─{'─'*20}─┼─{'─'*3}─┼─{'─'*6}─┼─{'─'*6}─┼─{'─'*25}")

        for h in elem['hypotheses']:
            w = h['weight']
            if h['result'] is True:
                pts = abs(w)
                tf = '✅'
                n_true += 1
            elif h['result'] is False:
                pts = w  # 음수
                tf = '❌'
                n_false += 1
            else:
                pts = 0
                tf = '? '
                n_unknown += 1

            if w > 0:
                max_score += abs(w)
            score += pts

            print(f"  {h['id']:>5} │ {h['name']:20} │ {tf:>3} │ {w:>+6.1f} │ {pts:>+6.2f} │ {h['detail'][:25]}")

        # 확률 계산
        if max_score > 0:
            confidence = max(0, score) / max_score * 100
        else:
            confidence = 0

        # 미결 페널티
        unknown_penalty = n_unknown * 5  # 미결 1개당 5% 차감
        adjusted_confidence = max(0, confidence - unknown_penalty)

        element_results.append({
            'id': elem['id'],
            'name': elem['name'],
            'category': elem['category'],
            'score': score,
            'max_score': max_score,
            'confidence': confidence,
            'adjusted': adjusted_confidence,
            'n_true': n_true,
            'n_false': n_false,
            'n_unknown': n_unknown,
        })

        bar = "█" * int(adjusted_confidence / 2) + "░" * (50 - int(adjusted_confidence / 2))
        print(f"\n  점수: {score:.2f} / {max_score:.2f}")
        print(f"  확률: [{bar}] {adjusted_confidence:.1f}%")
        if n_unknown > 0:
            print(f"  (미결 {n_unknown}개 × 5% 페널티 적용)")

        total_score += score
        total_max += max_score

    # ─────────────────────────────────────────
    # 종합
    # ─────────────────────────────────────────
    print(f"\n{'═' * 70}")
    print(f"  종합 평가")
    print(f"{'═' * 70}")

    print(f"\n  {'ID':>3} │ {'요소':30} │ {'카테고리':8} │ {'✅':>2} │ {'❌':>2} │ {'?':>2} │ {'확률':>6}")
    print(f"  {'─'*3}─┼─{'─'*30}─┼─{'─'*8}─┼─{'─'*2}─┼─{'─'*2}─┼─{'─'*2}─┼─{'─'*6}")

    for r in element_results:
        bar_mini = "█" * int(r['adjusted'] / 10)
        print(f"  {r['id']:>3} │ {r['name']:30} │ {r['category']:8} │ {r['n_true']:>2} │ {r['n_false']:>2} │ {r['n_unknown']:>2} │ {r['adjusted']:>5.1f}%")

    # 총합
    total_confidence = max(0, total_score) / total_max * 100 if total_max > 0 else 0
    total_unknown = sum(r['n_unknown'] for r in element_results)
    total_adjusted = max(0, total_confidence - total_unknown * 2)

    print(f"\n  {'총합':>3} │ {'':30} │ {'':8} │ {sum(r['n_true'] for r in element_results):>2} │ {sum(r['n_false'] for r in element_results):>2} │ {total_unknown:>2} │ {total_adjusted:>5.1f}%")

    # 시각화
    print(f"\n  설계 요소별 회수 확률:")
    for r in element_results:
        bar = "█" * int(r['adjusted'] / 2) + "░" * (50 - int(r['adjusted'] / 2))
        print(f"    {r['id']} [{bar}] {r['adjusted']:>5.1f}%  {r['name'][:25]}")

    # 최종 판정
    print(f"\n{'─' * 70}")
    print(f"  최종 판정")
    print(f"{'─' * 70}")

    high = [r for r in element_results if r['adjusted'] >= 70]
    mid = [r for r in element_results if 40 <= r['adjusted'] < 70]
    low = [r for r in element_results if r['adjusted'] < 40]

    print(f"\n  🟢 높은 확률 (≥70%):")
    for r in high:
        print(f"    {r['id']} {r['name']}: {r['adjusted']:.1f}%")

    print(f"\n  🟡 중간 확률 (40~70%):")
    for r in mid:
        print(f"    {r['id']} {r['name']}: {r['adjusted']:.1f}%")

    print(f"\n  🔴 낮은 확률 (<40%):")
    for r in low:
        print(f"    {r['id']} {r['name']}: {r['adjusted']:.1f}%")
    if not low:
        print(f"    (없음)")

    # 종합 확률
    overall = 1.0
    for r in element_results:
        overall *= (r['adjusted'] / 100)
    overall_pct = overall * 100

    # 독립 가정 완화 (요소간 상관 있으므로 보정)
    correlated_pct = overall_pct ** 0.5 * 10  # 상관 보정

    print(f"\n  종합 성공 확률:")
    print(f"    독립 가정: {overall_pct:.2f}%")
    print(f"    상관 보정: {min(correlated_pct, 100):.1f}%")

    bar_final = "█" * int(correlated_pct / 2) + "░" * (50 - int(min(correlated_pct, 100) / 2))
    print(f"    [{bar_final}] {min(correlated_pct, 100):.1f}%")

    # 리스크 분석
    print(f"\n{'─' * 70}")
    print(f"  리스크 분석")
    print(f"{'─' * 70}")
    print(f"\n  ❌ 반증된 가설의 영향:")
    print(f"    010 (1/3 반증): 최적 비율이 분포에 따라 변동 → 실제 환경에서 재조정 필요")
    print(f"\n  ? 미결 가설의 리스크:")
    print(f"    001 (리만 동치): 이론적 기반 불확실 → 경험적 최적화로 보완 가능")
    print(f"    002 (1/e 보편성): 골든존 중심 정밀도 불확실 → ±0.05 범위 탐색 필요")
    print(f"    003 (커스프 동치): 자기조절 메커니즘 정당성 → 실험적 검증 필요")
    print(f"    015 (확산 법칙): 수렴 보장 불확실 → 학습률 보수적 설정")

    print(f"\n{'═' * 70}")

    # 저장
    os.makedirs(RESULTS_DIR, exist_ok=True)
    with open(os.path.join(RESULTS_DIR, "golden_moe_scorecard.md"), 'w', encoding='utf-8') as f:
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        f.write(f"# 골든 MoE 설계 스코어카드 [{now}]\n\n")
        f.write(f"| ID | 요소 | ✅ | ❌ | ? | 확률 |\n|---|---|---|---|---|---|\n")
        for r in element_results:
            f.write(f"| {r['id']} | {r['name']} | {r['n_true']} | {r['n_false']} | {r['n_unknown']} | {r['adjusted']:.1f}% |\n")
        f.write(f"\n종합: {min(correlated_pct, 100):.1f}%\n\n---\n")

    print(f"  📁 스코어카드 → results/golden_moe_scorecard.md")
    print()


if __name__ == '__main__':
    evaluate()
