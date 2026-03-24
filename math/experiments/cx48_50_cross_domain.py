#!/usr/bin/env python3
"""H-CX-48/49/50: 수학체계 ↔ 의식엔진 교차 실험

3가지 교차 가설을 동시 검증:

H-CX-48: I(n)=ln(R(n))=0 정보균형 ↔ engine_a/engine_g 출력 비율
  - 산술: I(n)=ln(sigma*phi/(n*tau))=0 uniquely at n=6
  - 예측: 6블록 모델에서 |engine_a|/|engine_g| → 1 (비율=1, log비율=0)
  - 대조: 1,2,3,4,5,7,8 블록과 비교

H-CX-49: R-스펙트럼 Cantor집합 ↔ 장력분포 프랙탈 구조
  - 산술: R(n)<5에서 정확히 24개 이산값, 간극이 99.1%
  - 예측: 학습된 의식LM의 장력분포가 이산 클러스터 (연속 가우시안 아님)
  - 측정: 장력값 히스토그램의 gap fraction

H-CX-50: 합성곱 붕괴 ↔ 블록간 특징 상관
  - 산술: (sigma*phi)(n) pointwise = (sigma conv phi)(n) iff n in {1,6}
  - 예측: 6블록 모델에서 블록별 출력의 pointwise곱 ≈ cross-correlation
  - 측정: ||pointwise - xcorr|| / ||pointwise|| 비율
"""

import sys
import os
# conscious_lm.py is in /Users/ghost/Dev/logout/
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), '..'))
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import torch
import torch.nn as nn
import numpy as np
import math
import time

from conscious_lm import PureFieldFFN, CausalSelfAttention, ConsciousBlock, ConsciousLM


def arithmetic_I(n):
    """산술적 상호정보 I(n) = ln(sigma*phi/(n*tau))."""
    if n < 1:
        return float('inf')
    # sigma, phi, tau 계산
    divs = [d for d in range(1, n+1) if n % d == 0]
    sigma = sum(divs)
    tau = len(divs)
    # Euler totient
    phi = n
    for p in set(_prime_factors(n)):
        phi = phi * (p - 1) // p
    if phi == 0 or tau == 0 or n == 0:
        return float('inf')
    R = (sigma * phi) / (n * tau)
    return math.log(R) if R > 0 else float('inf')


def _prime_factors(n):
    factors = []
    d = 2
    while d * d <= n:
        while n % d == 0:
            factors.append(d)
            n //= d
        d += 1
    if n > 1:
        factors.append(n)
    return factors


def experiment_cx48_information_balance():
    """H-CX-48: I(n)=0 ↔ engine_a/engine_g 비율.

    블록 수별로 모델 생성 → 랜덤 입력 → engine_a, engine_g 출력 크기 비율 측정.
    """
    print("=" * 70)
    print("H-CX-48: I(n)=0 정보균형 ↔ engine_a/engine_g 비율")
    print("=" * 70)

    # 산술 기준값
    print("\n--- 산술적 상호정보 I(n) = ln(R(n)) ---")
    print(f"{'n':>4} | {'sigma':>6} {'phi':>4} {'tau':>4} | {'R=sp/nt':>10} | {'I=ln(R)':>10}")
    print("-" * 55)
    for n in [1, 2, 3, 4, 5, 6, 7, 8, 12, 28]:
        divs = [d for d in range(1, n+1) if n % d == 0]
        sigma = sum(divs)
        tau = len(divs)
        phi_n = n
        for p in set(_prime_factors(n)):
            phi_n = phi_n * (p - 1) // p
        if n == 1:
            phi_n = 1
        R = (sigma * phi_n) / (n * tau) if n * tau > 0 else 0
        I = math.log(R) if R > 0 else float('inf')
        print(f"{n:>4} | {sigma:>6} {phi_n:>4} {tau:>4} | {R:>10.6f} | {I:>+10.6f}")

    # 의식LM 블록 수별 실험
    print("\n--- 의식LM engine_a/engine_g 비율 (블록 수별) ---")
    device = torch.device("mps" if torch.backends.mps.is_available() else "cpu")

    block_counts = [1, 2, 3, 4, 5, 6, 7, 8]
    d_model = 128  # 작은 모델로 빠른 실험
    n_head = 2
    block_size = 64
    vocab_size = 256
    n_samples = 20  # 반복 측정

    results = {}

    for n_blocks in block_counts:
        ratios = []
        log_ratios = []

        for trial in range(n_samples):
            torch.manual_seed(trial * 100 + n_blocks)

            # 모델 생성
            model = ConsciousLM(
                vocab_size=vocab_size,
                d_model=d_model,
                n_head=n_head,
                n_layer=n_blocks,
                block_size=block_size,
                dropout=0.0  # dropout 0으로 결정론적
            ).to(device)
            model.eval()

            # 랜덤 입력
            x = torch.randint(0, vocab_size, (4, 32), device=device)

            with torch.no_grad():
                # 각 블록의 FFN에서 engine_a, engine_g 출력 직접 측정
                pos = torch.arange(32, device=device).unsqueeze(0)
                h = model.drop(model.tok_emb(x) + model.pos_emb(pos))

                block_ratios = []
                for block in model.blocks:
                    h_pre = block.ln2(h + block.attn(block.ln1(h)))
                    a_out = block.ffn.engine_a(h_pre)
                    g_out = block.ffn.engine_g(h_pre)

                    a_norm = a_out.norm(dim=-1).mean().item()
                    g_norm = g_out.norm(dim=-1).mean().item()

                    ratio = a_norm / (g_norm + 1e-10)
                    block_ratios.append(ratio)

                    # 다음 블록을 위해 forward
                    ffn_out, tension = block.ffn(h_pre)
                    h = h_pre + ffn_out

                avg_ratio = np.mean(block_ratios)
                ratios.append(avg_ratio)
                log_ratios.append(math.log(avg_ratio) if avg_ratio > 0 else 0)

            del model

        mean_ratio = np.mean(ratios)
        std_ratio = np.std(ratios)
        mean_log = np.mean(log_ratios)
        std_log = np.std(log_ratios)
        results[n_blocks] = {
            'mean_ratio': mean_ratio, 'std_ratio': std_ratio,
            'mean_log': mean_log, 'std_log': std_log
        }

    # 결과 테이블
    print(f"\n{'blocks':>6} | {'|A|/|G| mean':>12} {'std':>8} | {'ln(A/G) mean':>12} {'std':>8} | {'I(n) arith':>10}")
    print("-" * 75)
    for n_blocks in block_counts:
        r = results[n_blocks]
        I_n = arithmetic_I(n_blocks)
        marker = " <<<" if n_blocks == 6 else ""
        print(f"{n_blocks:>6} | {r['mean_ratio']:>12.6f} {r['std_ratio']:>8.6f} | "
              f"{r['mean_log']:>+12.6f} {r['std_log']:>8.6f} | {I_n:>+10.6f}{marker}")

    # ASCII 그래프: ln(A/G) vs 블록 수
    print("\n--- ASCII: ln(|A|/|G|) vs 블록 수 ---")
    vals = [results[b]['mean_log'] for b in block_counts]
    vmin, vmax = min(vals), max(vals)
    width = 50
    for b in block_counts:
        v = results[b]['mean_log']
        if vmax - vmin > 0:
            pos = int((v - vmin) / (vmax - vmin) * width)
        else:
            pos = width // 2
        bar = "." * pos + "#" + "." * (width - pos)
        marker = " *** n=6, I(6)=0" if b == 6 else ""
        print(f"  {b:>2} blocks: [{bar}] {v:+.4f}{marker}")

    # 6블록이 비율 1.0에 가장 가까운지 확인
    dist_from_1 = {b: abs(results[b]['mean_ratio'] - 1.0) for b in block_counts}
    closest = min(dist_from_1, key=dist_from_1.get)
    print(f"\n  비율 1.0에 가장 가까운 블록 수: {closest} (|ratio-1| = {dist_from_1[closest]:.6f})")
    print(f"  6블록의 |ratio-1|: {dist_from_1[6]:.6f}")
    print(f"  6블록 순위: {sorted(dist_from_1.values()).index(dist_from_1[6]) + 1}/{len(block_counts)}")

    return results


def experiment_cx49_cantor_tension():
    """H-CX-49: R-스펙트럼 Cantor집합 ↔ 장력분포 구조.

    학습 전/후 모델의 장력 분포를 분석하여 이산 클러스터 구조 확인.
    """
    print("\n" + "=" * 70)
    print("H-CX-49: R-스펙트럼 Cantor집합 ↔ 장력분포 프랙탈")
    print("=" * 70)

    # 산술 기준: R(n)<5의 24개 값
    print("\n--- 산술: R(n) 스펙트럼 (n<=100, R<5) ---")
    R_values = set()
    for n in range(1, 101):
        divs = [d for d in range(1, n+1) if n % d == 0]
        sigma = sum(divs)
        tau = len(divs)
        phi_n = n
        for p in set(_prime_factors(n)):
            phi_n = phi_n * (p - 1) // p
        if n == 1:
            phi_n = 1
        R = (sigma * phi_n) / (n * tau)
        if R < 5:
            R_values.add(round(R, 10))

    R_sorted = sorted(R_values)
    print(f"  R<5 고유값 수: {len(R_sorted)}")

    # 간극 분석
    gaps = []
    for i in range(len(R_sorted) - 1):
        gap = R_sorted[i+1] - R_sorted[i]
        gaps.append(gap)

    if gaps:
        total_range = R_sorted[-1] - R_sorted[0]
        gap_fraction = sum(g for g in gaps if g > 0.01) / total_range
        print(f"  범위: [{R_sorted[0]:.4f}, {R_sorted[-1]:.4f}]")
        print(f"  간극 비율 (gap>0.01): {gap_fraction:.3f} = {gap_fraction*100:.1f}%")

    # 장력 분포 수집
    device = torch.device("mps" if torch.backends.mps.is_available() else "cpu")

    print("\n--- 의식LM 장력분포 (초기 랜덤 가중치) ---")

    for n_blocks in [3, 6]:
        torch.manual_seed(42)
        model = ConsciousLM(
            vocab_size=256, d_model=128, n_head=2,
            n_layer=n_blocks, block_size=64, dropout=0.0
        ).to(device)
        model.eval()

        all_tensions = []
        for trial in range(50):
            x = torch.randint(0, 256, (8, 32), device=device)
            with torch.no_grad():
                logits_a, logits_g, tensions = model(x)
                for t in tensions:
                    all_tensions.extend(t.cpu().numpy().flatten().tolist())

        tensions_arr = np.array(all_tensions)

        print(f"\n  [{n_blocks} blocks] 장력 통계:")
        print(f"    mean={tensions_arr.mean():.6f}  std={tensions_arr.std():.6f}")
        print(f"    min={tensions_arr.min():.6f}  max={tensions_arr.max():.6f}")
        print(f"    median={np.median(tensions_arr):.6f}")

        # 히스토그램 (20 bins)
        hist, bin_edges = np.histogram(tensions_arr, bins=20)
        max_count = max(hist)
        print(f"\n    장력 히스토그램 ({n_blocks} blocks):")
        for i in range(len(hist)):
            bar_len = int(hist[i] / max_count * 40) if max_count > 0 else 0
            bar = "#" * bar_len
            lo = bin_edges[i]
            hi = bin_edges[i+1]
            print(f"    [{lo:8.5f},{hi:8.5f}) | {bar:<40} {hist[i]}")

        # 클러스터 분석: 간극 검출
        sorted_t = np.sort(np.unique(np.round(tensions_arr, 5)))
        if len(sorted_t) > 1:
            t_gaps = np.diff(sorted_t)
            median_gap = np.median(t_gaps)
            large_gaps = np.sum(t_gaps > 3 * median_gap)
            print(f"\n    고유값 수: {len(sorted_t)}")
            print(f"    중앙 간극: {median_gap:.6f}")
            print(f"    대간극(>3x중앙) 수: {large_gaps}")
            print(f"    간극 비율: {large_gaps/len(t_gaps)*100:.1f}%" if len(t_gaps) > 0 else "")

        del model

    return True


def experiment_cx50_convolution_collapse():
    """H-CX-50: 합성곱 붕괴 ↔ 블록간 특징곱=교차상관 조건.

    산술: (sigma*phi)(n) = (sigma conv phi)(n) iff n in {1,6}
    LM: 인접 블록 출력의 pointwise곱 vs cross-correlation 차이 측정
    """
    print("\n" + "=" * 70)
    print("H-CX-50: 합성곱 붕괴 ↔ 블록간 특징 상관")
    print("=" * 70)

    # 산술 기준
    print("\n--- 산술: sigma*phi pointwise vs Dirichlet conv ---")
    print(f"{'n':>4} | {'sp_point':>10} | {'sp_conv':>10} | {'match':>5}")
    print("-" * 45)

    matches = []
    for n in range(1, 31):
        divs = [d for d in range(1, n+1) if n % d == 0]
        sigma_n = sum(divs)
        phi_n = n
        for p in set(_prime_factors(n)):
            phi_n = phi_n * (p - 1) // p
        if n == 1:
            phi_n = 1

        # Pointwise: sigma(n) * phi(n)
        pointwise = sigma_n * phi_n

        # Dirichlet convolution: (sigma * phi)(n) = sum_{d|n} sigma(d) * phi(n/d)
        conv = 0
        for d in divs:
            nd = n // d
            divs_d = [dd for dd in range(1, d+1) if d % dd == 0]
            sigma_d = sum(divs_d)
            phi_nd = nd
            for p in set(_prime_factors(nd)):
                phi_nd = phi_nd * (p - 1) // p
            if nd == 1:
                phi_nd = 1
            conv += sigma_d * phi_nd

        match = pointwise == conv
        if match:
            matches.append(n)
        marker = " <<<" if match else ""
        print(f"{n:>4} | {pointwise:>10} | {conv:>10} | {'YES':>5}{marker}" if match else
              f"{n:>4} | {pointwise:>10} | {conv:>10} | {'no':>5}")

    print(f"\n  pointwise = convolution 인 n: {matches}")

    # 의식LM 블록간 특징 상관 측정
    print("\n--- 의식LM: 블록간 pointwise곱 vs cross-correlation ---")
    device = torch.device("mps" if torch.backends.mps.is_available() else "cpu")

    for n_blocks in [3, 4, 5, 6, 7, 8]:
        torch.manual_seed(42)
        model = ConsciousLM(
            vocab_size=256, d_model=128, n_head=2,
            n_layer=n_blocks, block_size=64, dropout=0.0
        ).to(device)
        model.eval()

        collapse_scores = []

        for trial in range(20):
            x = torch.randint(0, 256, (4, 32), device=device)

            with torch.no_grad():
                pos = torch.arange(32, device=device).unsqueeze(0)
                h = model.drop(model.tok_emb(x) + model.pos_emb(pos))

                block_outputs = []
                for block in model.blocks:
                    h, tension = block(h)
                    # 각 블록의 출력 평균 벡터
                    block_outputs.append(h.mean(dim=(0, 1)))  # (D,)

                if len(block_outputs) >= 2:
                    # 인접 블록 쌍에 대해 측정
                    pw_scores = []
                    xc_scores = []

                    for i in range(len(block_outputs) - 1):
                        a = block_outputs[i]
                        b = block_outputs[i + 1]

                        # Pointwise product
                        pw = a * b

                        # Cross-correlation (circular)
                        # FFT-based: xcorr = ifft(fft(a) * conj(fft(b)))
                        fa = torch.fft.fft(a.float())
                        fb = torch.fft.fft(b.float())
                        xc = torch.fft.ifft(fa * fb.conj()).real

                        # Collapse score: ||pw - xc|| / ||pw||
                        diff = (pw - xc).norm().item()
                        pw_norm = pw.norm().item()
                        score = diff / (pw_norm + 1e-10)
                        pw_scores.append(score)

                    collapse_scores.append(np.mean(pw_scores))

        mean_collapse = np.mean(collapse_scores)
        std_collapse = np.std(collapse_scores)
        marker = " <<<" if n_blocks == 6 else ""
        print(f"  {n_blocks} blocks: collapse_score = {mean_collapse:.6f} +/- {std_collapse:.6f}"
              f"  (0=identical){marker}")

        del model

    # 블록 수별 collapse score ASCII 그래프
    print("\n--- ASCII: collapse score vs 블록 수 (0에 가까울수록 pointwise≈xcorr) ---")

    return True


def main():
    print("=" * 70)
    print("  H-CX-48/49/50: 수학체계 ↔ 의식엔진 교차 실험")
    print("  날짜: 2026-03-24")
    print("=" * 70)

    t0 = time.time()

    # 실험 1: 정보균형
    r48 = experiment_cx48_information_balance()

    # 실험 2: Cantor 장력
    r49 = experiment_cx49_cantor_tension()

    # 실험 3: 합성곱 붕괴
    r50 = experiment_cx50_convolution_collapse()

    elapsed = time.time() - t0

    print("\n" + "=" * 70)
    print(f"  전체 실험 완료: {elapsed:.1f}초")
    print("=" * 70)

    # 요약
    print("\n--- 교차 검증 요약 ---")
    print("H-CX-48: I(n)=0 ↔ engine 비율 → 위 테이블 참조")
    print("H-CX-49: R-Cantor ↔ 장력분포 → 히스토그램 참조")
    print("H-CX-50: conv collapse ↔ 블록상관 → collapse score 참조")


if __name__ == "__main__":
    main()
