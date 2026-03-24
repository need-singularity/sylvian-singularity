#!/usr/bin/env python3
"""
가설 검증 계산기 (Hypothesis Verification Calculator)
=====================================================
CLAUDE.md 5단계 검증 파이프라인 구현:
  1. 산술 정확성 재확인
  2. Ad-hoc 체크 (+1/-1 보정 경고)
  3. Strong Law of Small Numbers (상수 <100 경고)
  4. 일반화 테스트 (완전수 28에서도 성립?)
  5. 텍사스 명사수 p-value (Bonferroni 보정)

사용법:
  python3 hypothesis_verifier.py --value 2.0 --target "sigma_inv(6)"
  python3 hypothesis_verifier.py --value 0.6931 --target "ln(2)" --tolerance 0.001
  python3 hypothesis_verifier.py --value 12 --target "sigma(6)" --generalize-28
  python3 hypothesis_verifier.py --value 1.0 --target "1/2+1/3+1/6"
  python3 hypothesis_verifier.py --value 17 --target "sigma(6)+tau(6)+1" --search-space-size 100
"""

import argparse
import math
import random
import sys
from fractions import Fraction

# ═══════════════════════════════════════════════════════════════
# 수학 상수 사전
# ═══════════════════════════════════════════════════════════════

MATH_CONSTANTS = {
    # 기본 상수
    'pi': math.pi,
    'e': math.e,
    'phi_golden': (1 + math.sqrt(5)) / 2,  # 황금비
    '1/e': 1 / math.e,
    'ln(2)': math.log(2),
    'ln(3)': math.log(3),
    'ln(4)': math.log(4),
    'ln(4/3)': math.log(4 / 3),

    # 단순 분수 (골든존 핵심)
    '1/2': 0.5,
    '1/3': 1.0 / 3,
    '1/6': 1.0 / 6,
    '5/6': 5.0 / 6,
    '2/3': 2.0 / 3,

    # 무리수
    'sqrt(2)': math.sqrt(2),
    'sqrt(3)': math.sqrt(3),
    'sqrt(6)': math.sqrt(6),

    # 오일러-마스케로니 상수
    'gamma': 0.5772156649015329,

    # 아페리 상수
    'zeta(3)': 1.2020569031595942,

    # 카탈란 상수
    'catalan': 0.9159655941772190,
}

# ═══════════════════════════════════════════════════════════════
# 완전수 속성
# ═══════════════════════════════════════════════════════════════

PERFECT_NUMBERS = {
    6: {
        'n': 6,
        'sigma': 12,      # 약수합
        'tau': 4,          # 약수 개수
        'phi': 2,          # 오일러 토션트
        'sigma_inv': 2,    # 진약수 역수합 = sigma_{-1}(6) = 1+1/2+1/3+1/6 = 2
        'divisors': [1, 2, 3, 6],
        'proper_divisors': [1, 2, 3],
        'prime_factors': [2, 3],
        'sopfr': 5,        # 소인수 합 2+3
        'omega': 2,        # 서로 다른 소인수 개수
        'mersenne_prime': 3,  # 2^p-1 = 3, p=2
    },
    28: {
        'n': 28,
        'sigma': 56,       # 약수합
        'tau': 6,           # 약수 개수
        'phi': 12,          # 오일러 토션트
        'sigma_inv': 2,     # 진약수 역수합 = 완전수이므로 항상 2
        'divisors': [1, 2, 4, 7, 14, 28],
        'proper_divisors': [1, 2, 4, 7, 14],
        'prime_factors': [2, 7],
        'sopfr': 9,         # 2+7
        'omega': 2,         # 서로 다른 소인수 개수
        'mersenne_prime': 7,  # 2^p-1 = 7, p=3
    },
}

# ═══════════════════════════════════════════════════════════════
# 수식 파서
# ═══════════════════════════════════════════════════════════════

def _build_eval_namespace(n=6):
    """수식 평가용 네임스페이스 구축."""
    pn = PERFECT_NUMBERS.get(n, PERFECT_NUMBERS[6])
    ns = {
        # math 함수
        'sqrt': math.sqrt,
        'log': math.log,
        'ln': math.log,
        'exp': math.exp,
        'sin': math.sin,
        'cos': math.cos,
        'abs': abs,
        'factorial': math.factorial,

        # 상수
        'pi': math.pi,
        'e': math.e,
        'phi_golden': (1 + math.sqrt(5)) / 2,
        'gamma': 0.5772156649015329,
        'zeta3': 1.2020569031595942,
        'catalan': 0.9159655941772190,

        # 완전수 n의 산술 함수
        'sigma': lambda x=None: pn['sigma'] if x is None else _sigma(x),
        'tau': lambda x=None: pn['tau'] if x is None else _tau(x),
        'phi': lambda x=None: pn['phi'] if x is None else _euler_phi(x),
        'sigma_inv': lambda x=None: pn['sigma_inv'] if x is None else _sigma_inv(x),
        'omega': lambda x=None: pn['omega'] if x is None else _omega(x),
        'sopfr': lambda x=None: pn['sopfr'] if x is None else _sopfr(x),
        'n': pn['n'],
    }
    return ns


def _divisors(n):
    """n의 약수 리스트."""
    divs = []
    for i in range(1, int(math.isqrt(n)) + 1):
        if n % i == 0:
            divs.append(i)
            if i != n // i:
                divs.append(n // i)
    return sorted(divs)


def _sigma(n):
    """약수합."""
    return sum(_divisors(n))


def _tau(n):
    """약수 개수."""
    return len(_divisors(n))


def _euler_phi(n):
    """오일러 토션트."""
    count = 0
    for k in range(1, n + 1):
        if math.gcd(k, n) == 1:
            count += 1
    return count


def _sigma_inv(n):
    """약수 역수합 = sigma_{-1}(n)."""
    return sum(Fraction(1, d) for d in _divisors(n))


def _omega(n):
    """서로 다른 소인수 개수."""
    count = 0
    d = 2
    temp = n
    while d * d <= temp:
        if temp % d == 0:
            count += 1
            while temp % d == 0:
                temp //= d
        d += 1
    if temp > 1:
        count += 1
    return count


def _sopfr(n):
    """소인수 합 (중복 포함)."""
    total = 0
    d = 2
    temp = n
    while d * d <= temp:
        while temp % d == 0:
            total += d
            temp //= d
        d += 1
    if temp > 1:
        total += temp
    return total


def parse_target(target_str, n=6):
    """
    수식 문자열을 수치로 변환.
    예: "ln(2)", "sigma(6)", "1/2+1/3+1/6", "pi/6", "sigma_inv(6)"
    """
    ns = _build_eval_namespace(n)

    # sigma(6), tau(28) 등 명시적 인자 처리
    import re
    expr = target_str

    # 함수(숫자) 패턴을 직접 계산으로 변환
    func_map = {
        'sigma': _sigma,
        'tau': _tau,
        'phi': _euler_phi,
        'sigma_inv': lambda x: float(_sigma_inv(x)),
        'omega': _omega,
        'sopfr': _sopfr,
    }

    for fname, func in func_map.items():
        pattern = rf'{fname}\((\d+)\)'
        for match in re.finditer(pattern, expr):
            arg = int(match.group(1))
            result = func(arg)
            expr = expr.replace(match.group(0), str(float(result)))

    # 인자 없는 함수 호출 → 기본 완전수 n의 값
    for fname in func_map:
        pattern = rf'\b{fname}\b(?!\()'
        if re.search(pattern, expr):
            pn = PERFECT_NUMBERS.get(n, PERFECT_NUMBERS[6])
            if fname == 'sigma_inv':
                val = float(pn['sigma_inv'])
            else:
                val = float(pn.get(fname, 0))
            expr = re.sub(pattern, str(val), expr)

    try:
        result = eval(expr, {"__builtins__": {}}, ns)
        return float(result)
    except Exception as ex:
        raise ValueError(f"수식 파싱 실패: '{target_str}' -> '{expr}': {ex}")


# ═══════════════════════════════════════════════════════════════
# 5단계 검증 파이프라인
# ═══════════════════════════════════════════════════════════════

def step1_arithmetic(value, target_val, tolerance):
    """1단계: 산술 정확성 재확인."""
    if target_val == 0:
        error = abs(value)
        rel_error = None
    else:
        error = abs(value - target_val)
        rel_error = abs(error / target_val)

    exact = (error == 0)
    within_tol = (error <= tolerance) if not exact else True

    return {
        'step': 1,
        'name': '산술 정확성',
        'value': value,
        'target': target_val,
        'error': error,
        'rel_error': rel_error,
        'exact': exact,
        'within_tolerance': within_tol,
        'passed': within_tol,
    }


def step2_adhoc(target_str):
    """2단계: Ad-hoc 보정 체크 (+1, -1 등이 포함되어 있으면 경고)."""
    # +1, -1, +2, -2 등의 보정 패턴 탐지
    # 분수(1/2, 1/3 등)의 분자는 제외: +1 뒤에 /가 오면 분수임
    import re
    adhoc_patterns = [
        (r'[+\-]\s*1(?!\d)(?!\s*/)', '+1/-1 보정'),
        (r'[+\-]\s*2(?!\d)(?!\s*/)', '+2/-2 보정'),
        (r'[+\-]\s*0\.5(?!\d)', '+0.5/-0.5 보정'),
    ]

    warnings = []
    for pattern, desc in adhoc_patterns:
        if re.search(pattern, target_str):
            warnings.append(desc)

    has_adhoc = len(warnings) > 0

    return {
        'step': 2,
        'name': 'Ad-hoc 보정 체크',
        'warnings': warnings,
        'has_adhoc': has_adhoc,
        'passed': not has_adhoc,
        'note': '보정 없음 (양호)' if not has_adhoc else f'경고: {", ".join(warnings)} 감지',
    }


def step3_small_numbers(target_str, target_val):
    """3단계: Strong Law of Small Numbers 체크."""
    # 수식에 관여하는 상수가 모두 100 미만인지
    import re
    numbers = re.findall(r'\d+\.?\d*', target_str)
    numeric_vals = [float(x) for x in numbers]

    all_small = all(v < 100 for v in numeric_vals) if numeric_vals else True
    # target_val 자체도 체크
    target_small = abs(target_val) < 100

    is_small = all_small and target_small

    return {
        'step': 3,
        'name': 'Small Numbers 체크',
        'constants_in_formula': numeric_vals,
        'all_under_100': all_small,
        'target_under_100': target_small,
        'is_small_number_regime': is_small,
        'passed': True,  # 경고만, 실패 아님
        'warning': is_small,
        'note': '경고: 모든 상수 <100 (Small Numbers 영역)' if is_small else '100 이상 상수 포함 (양호)',
    }


def step4_generalize_28(target_str, tolerance):
    """
    4단계: 완전수 28에서도 성립하는지 테스트.
    n=6 수식의 산술 함수를 n=28로 교체하여 평가.
    """
    try:
        val_6 = parse_target(target_str, n=6)
        val_28 = parse_target(target_str, n=28)

        # 비율이 유지되는지 (구조적 관계)
        if val_6 != 0:
            ratio = val_28 / val_6
        else:
            ratio = None

        # 완전수 공통 성질: sigma_inv = 2 (항상)
        # 구조적이면 같은 값이거나 일정한 스케일링
        same_value = abs(val_28 - val_6) < tolerance
        # sigma_inv 관계는 항상 2
        both_give_2 = abs(val_6 - 2.0) < tolerance and abs(val_28 - 2.0) < tolerance

        return {
            'step': 4,
            'name': '일반화 테스트 (n=28)',
            'value_n6': val_6,
            'value_n28': val_28,
            'ratio': ratio,
            'same_value': same_value,
            'both_give_2': both_give_2,
            'passed': same_value or both_give_2,
            'note': (
                '동일 값 (구조적!)' if same_value
                else f'n=6: {val_6:.6f}, n=28: {val_28:.6f}, 비율: {ratio:.4f}' if ratio
                else f'n=6: {val_6:.6f}, n=28: {val_28:.6f}'
            ),
        }
    except Exception as ex:
        return {
            'step': 4,
            'name': '일반화 테스트 (n=28)',
            'passed': None,
            'note': f'평가 불가: {ex}',
            'error': str(ex),
        }


def step5_texas_pvalue(value, target_val, tolerance, search_space_size, n_sim=200000):
    """
    5단계: 텍사스 명사수 p-value (Bonferroni 보정).

    랜덤 상수 조합이 같은 오차 이내로 매칭될 확률 계산.
    """
    if target_val == 0:
        obs_error = abs(value)
    else:
        obs_error = abs(value - target_val) / abs(target_val)

    # 상수 풀: 다양한 수학 상수
    const_pool = list(MATH_CONSTANTS.values())

    # 연산: +, -, *, /
    hit_count = 0

    random.seed(42)  # 재현성
    for _ in range(n_sim):
        # 랜덤으로 2개 상수 선택 + 연산
        a = random.choice(const_pool)
        b = random.choice(const_pool)
        op = random.randint(0, 3)
        try:
            if op == 0:
                r = a + b
            elif op == 1:
                r = a - b
            elif op == 2:
                r = a * b
            else:
                if b != 0:
                    r = a / b
                else:
                    continue

            if target_val != 0:
                trial_error = abs(r - target_val) / abs(target_val)
            else:
                trial_error = abs(r)

            if trial_error <= obs_error:
                hit_count += 1
        except (OverflowError, ZeroDivisionError):
            continue

    # 단일 비교 p-value
    raw_p = hit_count / n_sim

    # Bonferroni 보정: 탐색 공간 크기만큼 곱함
    corrected_p = min(1.0, raw_p * search_space_size)

    return {
        'step': 5,
        'name': '텍사스 명사수 p-value',
        'observed_rel_error': obs_error,
        'n_simulations': n_sim,
        'hits': hit_count,
        'raw_p': raw_p,
        'search_space_size': search_space_size,
        'corrected_p': corrected_p,
        'passed': corrected_p < 0.05,
        'structural': corrected_p < 0.01,
        'note': (
            f'p={corrected_p:.6f} (Bonferroni k={search_space_size})'
            + (' *** 구조적!' if corrected_p < 0.01
               else ' * 유의' if corrected_p < 0.05
               else ' (유의하지 않음)')
        ),
    }


# ═══════════════════════════════════════════════════════════════
# 등급 판정
# ═══════════════════════════════════════════════════════════════

def determine_grade(results):
    """
    검증 결과에서 등급 판정.

    등급:
      green  = 정확한 등식 + 증명됨
      orange_star = 근사 + p < 0.01 (구조적)
      orange = 근사 + p < 0.05 (약한 증거)
      white  = 산술 맞지만 p > 0.05 (우연)
      black  = 산술 자체가 틀림

    Ad-hoc 보정이 있으면 star 부여 금지.
    """
    s1 = results[0]  # 산술
    s2 = results[1]  # ad-hoc
    s5 = results[4]  # 텍사스

    # 산술 실패 → 반증
    if not s1['passed']:
        return 'black', '(반증)'

    has_adhoc = s2['has_adhoc']

    # 정확한 등식
    if s1['exact']:
        return 'green', '(정확한 등식)'

    # 근사 + 텍사스 결과
    p = s5.get('corrected_p', 1.0)

    if p < 0.01 and not has_adhoc:
        return 'orange_star', '(구조적 근사, p<0.01)'
    elif p < 0.05:
        return 'orange', '(약한 증거, p<0.05)'
    else:
        return 'white', '(우연 가능성, p>=0.05)'


GRADE_EMOJI = {
    'green': '\U0001f7e9',        # 녹색 사각형
    'orange_star': '\U0001f7e7\u2b50',  # 주황 + 별
    'orange': '\U0001f7e7',       # 주황 사각형
    'white': '\u26aa',            # 흰 원
    'black': '\u2b1b',            # 검은 사각형
}


# ═══════════════════════════════════════════════════════════════
# ASCII 리포트
# ═══════════════════════════════════════════════════════════════

def print_report(value, target_str, target_val, results, grade, grade_desc, do_generalize):
    """검증 결과 ASCII 리포트 출력."""
    w = 60
    print('=' * w)
    print('  가설 검증 리포트 (Hypothesis Verifier)')
    print('=' * w)
    print(f'  측정값:   {value}')
    print(f'  수식:     {target_str}')
    print(f'  목표값:   {target_val}')
    print('-' * w)

    for r in results:
        step = r['step']
        name = r['name']
        passed = r.get('passed')

        if passed is True:
            mark = 'PASS'
        elif passed is False:
            mark = 'FAIL'
        elif passed is None:
            mark = 'N/A '
        else:
            mark = '??? '

        # 경고가 있으면 WARN 표시
        if r.get('warning', False) and passed:
            mark = 'WARN'

        print(f'  [{mark}] Step {step}: {name}')

        # 상세 정보
        if step == 1:
            err = r['error']
            rel = r.get('rel_error')
            print(f'         오차: {err:.2e}', end='')
            if rel is not None:
                print(f'  (상대: {rel:.2e})', end='')
            if r['exact']:
                print('  [정확 일치]', end='')
            print()
        elif step == 2:
            print(f'         {r["note"]}')
        elif step == 3:
            print(f'         {r["note"]}')
            if r['constants_in_formula']:
                print(f'         수식 내 숫자: {r["constants_in_formula"]}')
        elif step == 4:
            if do_generalize:
                print(f'         {r["note"]}')
            else:
                print('         (--generalize-28 미지정, 건너뜀)')
        elif step == 5:
            print(f'         {r["note"]}')
            raw = r.get('raw_p', 0)
            print(f'         raw p={raw:.6f}, hits={r.get("hits", 0)}/{r.get("n_simulations", 0)}')

    print('-' * w)
    emoji = GRADE_EMOJI.get(grade, '?')
    print(f'  최종 등급: {emoji}  {grade.upper()} {grade_desc}')
    print('=' * w)

    # 요약 바
    s2 = results[1]
    s3 = results[2]
    warnings = []
    if s2['has_adhoc']:
        warnings.append('AD-HOC 보정 감지 (star 금지)')
    if s3.get('warning', False):
        warnings.append('Small Numbers 영역')
    if warnings:
        print()
        for w_msg in warnings:
            print(f'  >>> 경고: {w_msg}')
        print()


# ═══════════════════════════════════════════════════════════════
# 메인
# ═══════════════════════════════════════════════════════════════

def run_verification(value, target_str, tolerance=0.01, do_generalize=False,
                     search_space_size=50):
    """전체 5단계 검증 파이프라인 실행."""
    # 목표값 계산
    target_val = parse_target(target_str)

    results = []

    # Step 1: 산술 정확성
    r1 = step1_arithmetic(value, target_val, tolerance)
    results.append(r1)

    # Step 2: Ad-hoc 체크
    r2 = step2_adhoc(target_str)
    results.append(r2)

    # Step 3: Small Numbers
    r3 = step3_small_numbers(target_str, target_val)
    results.append(r3)

    # Step 4: 일반화 (옵션)
    if do_generalize:
        r4 = step4_generalize_28(target_str, tolerance)
    else:
        r4 = {
            'step': 4,
            'name': '일반화 테스트 (n=28)',
            'passed': None,
            'note': '건너뜀 (--generalize-28 필요)',
        }
    results.append(r4)

    # Step 5: 텍사스 명사수 (산술 통과시에만)
    if r1['passed']:
        r5 = step5_texas_pvalue(value, target_val, tolerance, search_space_size)
    else:
        r5 = {
            'step': 5,
            'name': '텍사스 명사수 p-value',
            'passed': False,
            'corrected_p': 1.0,
            'note': '산술 실패로 건너뜀',
        }
    results.append(r5)

    # 등급 판정
    grade, grade_desc = determine_grade(results)

    # 리포트 출력
    print_report(value, target_str, target_val, results, grade, grade_desc, do_generalize)

    return grade, results


def main():
    parser = argparse.ArgumentParser(
        description='가설 검증 계산기 — CLAUDE.md 5단계 파이프라인',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
사용 예시:
  %(prog)s --value 2.0 --target "sigma_inv(6)"
  %(prog)s --value 0.6931 --target "ln(2)" --tolerance 0.001
  %(prog)s --value 12 --target "sigma(6)" --generalize-28
  %(prog)s --value 1.0 --target "1/2+1/3+1/6"
  %(prog)s --value 17 --target "sigma(6)+tau(6)+1" --search-space-size 100

수식에서 사용 가능한 함수:
  sigma(n), tau(n), phi(n), sigma_inv(n), omega(n), sopfr(n)
  ln(x), log(x), sqrt(x), exp(x), sin(x), cos(x)
  pi, e, phi_golden, gamma, zeta3
        """,
    )
    parser.add_argument('--value', type=float, required=True,
                        help='측정/관찰된 값')
    parser.add_argument('--target', type=str, required=True,
                        help='기대 수식 (예: "ln(2)", "sigma(6)", "1/2+1/3+1/6")')
    parser.add_argument('--tolerance', type=float, default=0.01,
                        help='허용 오차 (기본: 0.01)')
    parser.add_argument('--generalize-28', action='store_true', dest='generalize_28',
                        help='완전수 28에서도 성립하는지 테스트')
    parser.add_argument('--search-space-size', type=int, default=50, dest='search_space_size',
                        help='Bonferroni 보정용 탐색 공간 크기 (기본: 50)')

    args = parser.parse_args()

    grade, results = run_verification(
        value=args.value,
        target_str=args.target,
        tolerance=args.tolerance,
        do_generalize=args.generalize_28,
        search_space_size=args.search_space_size,
    )

    # 종료 코드: green/orange_star=0, orange=1, white/black=2
    if grade in ('green', 'orange_star'):
        sys.exit(0)
    elif grade == 'orange':
        sys.exit(1)
    else:
        sys.exit(2)


if __name__ == '__main__':
    main()
