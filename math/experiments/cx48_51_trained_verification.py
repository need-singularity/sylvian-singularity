#!/usr/bin/env python3
"""Ralph 306: 학습된 ConsciousLM에서 H-CX-48/49/50 재검증 + H-CX-51 실험

핵심 질문: "학습이 산술적 구조를 드러내는가?"

Ralph 305에서 미학습 기준선 완료:
  - H-CX-48: 모든 블록 수에서 비율≈1.0 (6블록 특별하지 않음)
  - H-CX-49: 연속 가우시안, Cantor 구조 없음
  - H-CX-50: 약한 감소 추세, 6블록 특별하지 않음

이번 실험: 바이트 수준 언어모델링으로 학습 후 재측정
  + H-CX-51: ld(6)=5/6 ↔ 최적 학습률 비율

설계:
  - 블록 수: 3, 4, 5, 6, 7, 8
  - d_model=128, n_head=2, vocab=256, block_size=64
  - 500 steps 학습 (빠른 수렴 확인)
  - 학습 데이터: 랜덤 바이트 시퀀스 (구조 없는 기준선)
    + 패턴 바이트 (반복 구조가 있는 데이터)
  - 측정: engine A/G 비율, 장력분포, conv collapse, loss 곡선
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), '..'))
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import torch
import torch.nn as nn
import torch.nn.functional as F
import numpy as np
import math
import time
import json

from conscious_lm import PureFieldFFN, CausalSelfAttention, ConsciousBlock, ConsciousLM


def generate_patterned_data(batch_size, seq_len, vocab_size=256):
    """패턴이 있는 바이트 시퀀스 생성.

    유형 혼합:
    - 반복 패턴 (ABC ABC ...)
    - 증가 수열 (0,1,2,3,...)
    - 거울 패턴 (ABC CBA)
    - 피보나치 mod 256
    """
    data = torch.zeros(batch_size, seq_len, dtype=torch.long)

    for i in range(batch_size):
        pattern_type = i % 4
        if pattern_type == 0:  # 반복
            period = np.random.randint(2, 8)
            base = torch.randint(0, vocab_size, (period,))
            for j in range(seq_len):
                data[i, j] = base[j % period]
        elif pattern_type == 1:  # 증가
            start = np.random.randint(0, vocab_size)
            step = np.random.randint(1, 4)
            for j in range(seq_len):
                data[i, j] = (start + j * step) % vocab_size
        elif pattern_type == 2:  # 거울
            half = seq_len // 2
            base = torch.randint(0, vocab_size, (half,))
            data[i, :half] = base
            data[i, half:2*half] = base.flip(0)
            if seq_len % 2:
                data[i, -1] = base[0]
        else:  # 피보나치
            a, b = np.random.randint(1, 10), np.random.randint(1, 10)
            data[i, 0] = a % vocab_size
            data[i, 1] = b % vocab_size
            for j in range(2, seq_len):
                a, b = b, (a + b) % vocab_size
                data[i, j] = b

    return data


def train_model(model, device, n_steps=500, lr=1e-3, batch_size=16, seq_len=32):
    """ConsciousLM을 패턴 데이터로 학습."""
    model.train()
    optimizer = torch.optim.AdamW(model.parameters(), lr=lr, weight_decay=0.01)
    scheduler = torch.optim.lr_scheduler.CosineAnnealingLR(optimizer, T_max=n_steps)

    losses = []
    tension_history = []

    for step in range(n_steps):
        x = generate_patterned_data(batch_size, seq_len + 1).to(device)
        input_ids = x[:, :-1]
        target_next = x[:, 1:]  # next byte
        target_prev = x[:, :-1].clone()
        target_prev[:, 1:] = x[:, :-2]
        target_prev[:, 0] = 0  # padding

        logits_a, logits_g, tensions = model(input_ids)

        # Loss: next byte + prev byte
        loss_a = F.cross_entropy(logits_a.view(-1, model.vocab_size), target_next.reshape(-1))
        loss_g = F.cross_entropy(logits_g.view(-1, model.vocab_size), target_prev.reshape(-1))
        loss = loss_a + loss_g

        optimizer.zero_grad()
        loss.backward()
        torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
        optimizer.step()
        scheduler.step()

        losses.append(loss.item())

        # 매 100스텝마다 장력 기록
        if step % 100 == 0:
            mean_tension = np.mean([t.mean().item() for t in tensions])
            tension_history.append((step, mean_tension))

    return losses, tension_history


def measure_engine_balance(model, device, n_trials=20, batch_size=8, seq_len=32):
    """H-CX-48: engine A/G 비율 측정."""
    model.eval()
    all_ratios = []
    all_log_ratios = []
    per_block_ratios = {i: [] for i in range(model.n_layer)}

    for trial in range(n_trials):
        x = generate_patterned_data(batch_size, seq_len).to(device)

        with torch.no_grad():
            pos = torch.arange(seq_len, device=device)
            h = model.drop(model.tok_emb(x) + model.pos_emb(pos))

            block_ratios = []
            for i, block in enumerate(model.blocks):
                h_pre = block.ln2(h + block.attn(block.ln1(h)))
                a_out = block.ffn.engine_a(h_pre)
                g_out = block.ffn.engine_g(h_pre)

                a_norm = a_out.norm(dim=-1).mean().item()
                g_norm = g_out.norm(dim=-1).mean().item()

                ratio = a_norm / (g_norm + 1e-10)
                block_ratios.append(ratio)
                per_block_ratios[i].append(ratio)

                ffn_out, tension = block.ffn(h_pre)
                h = h_pre + ffn_out

            avg_ratio = np.mean(block_ratios)
            all_ratios.append(avg_ratio)
            all_log_ratios.append(math.log(avg_ratio) if avg_ratio > 0 else 0)

    return {
        'mean_ratio': np.mean(all_ratios),
        'std_ratio': np.std(all_ratios),
        'mean_log': np.mean(all_log_ratios),
        'std_log': np.std(all_log_ratios),
        'per_block': {i: (np.mean(v), np.std(v)) for i, v in per_block_ratios.items()}
    }


def measure_tension_distribution(model, device, n_trials=30):
    """H-CX-49: 장력 분포 측정."""
    model.eval()
    all_tensions = []

    for trial in range(n_trials):
        x = generate_patterned_data(8, 32).to(device)
        with torch.no_grad():
            _, _, tensions = model(x)
            for t in tensions:
                all_tensions.extend(t.cpu().numpy().flatten().tolist())

    arr = np.array(all_tensions)

    # 히스토그램
    hist, bin_edges = np.histogram(arr, bins=20)

    # 간극 분석
    sorted_unique = np.sort(np.unique(np.round(arr, 5)))
    if len(sorted_unique) > 1:
        gaps = np.diff(sorted_unique)
        median_gap = np.median(gaps)
        large_gaps = np.sum(gaps > 3 * median_gap)
        gap_fraction = large_gaps / len(gaps) if len(gaps) > 0 else 0
    else:
        median_gap = 0
        large_gaps = 0
        gap_fraction = 0

    return {
        'mean': arr.mean(), 'std': arr.std(),
        'min': arr.min(), 'max': arr.max(),
        'n_unique': len(sorted_unique),
        'median_gap': median_gap,
        'large_gaps': large_gaps,
        'gap_fraction': gap_fraction,
        'hist': hist.tolist(),
        'bin_edges': bin_edges.tolist(),
        'raw_tensions': arr
    }


def measure_conv_collapse(model, device, n_trials=20):
    """H-CX-50: convolution collapse score."""
    model.eval()
    scores = []

    for trial in range(n_trials):
        x = generate_patterned_data(4, 32).to(device)

        with torch.no_grad():
            pos = torch.arange(32, device=device)
            h = model.drop(model.tok_emb(x) + model.pos_emb(pos))

            block_outputs = []
            for block in model.blocks:
                h, tension = block(h)
                block_outputs.append(h.mean(dim=(0, 1)).cpu().numpy())

            # 인접 블록 쌍의 collapse score
            pair_scores = []
            for i in range(len(block_outputs) - 1):
                a = block_outputs[i]
                b = block_outputs[i + 1]

                # pointwise product
                pw = a * b

                # cross-correlation via FFT
                fa = np.fft.fft(a)
                fb = np.fft.fft(b)
                xcorr = np.real(np.fft.ifft(fa * np.conj(fb)))

                # collapse score
                diff = np.linalg.norm(pw - xcorr)
                pw_norm = np.linalg.norm(pw) + 1e-10
                score = diff / pw_norm
                pair_scores.append(score)

            scores.append(np.mean(pair_scores))

    return {
        'mean_score': np.mean(scores),
        'std_score': np.std(scores),
        'all_scores': scores
    }


def experiment_cx51_learning_rate(device):
    """H-CX-51: ld(6)=5/6 ↔ 최적 학습률 비율.

    산술 미분: ld(6) = 6'(소인수 기여의 합) = 6(1/2 + 1/3) = 5
    로그 미분: ld(6) = 5/6 = Compass 상한!

    예측: lr = base_lr * (5/6) 스케일이 최적이거나,
          6블록 모델에서 최적 lr이 5/6 비율에 위치
    """
    print("\n" + "=" * 70)
    print("H-CX-51: ld(6)=5/6 ↔ 최적 학습률 비율")
    print("=" * 70)

    print("\n--- 산술 미분 배경 ---")
    print("  n'(산술 미분) = n * sum(1/p for p in prime_factors(n))")
    print("  6' = 6*(1/2 + 1/3) = 6*(5/6) = 5")
    print("  ld(6) = 6'/6 = 5/6 = 0.8333... = Compass 상한!")
    print("  ld(28) = 28'/28 = 28*(1/2+1/7)/28 = 9/14 = 0.6429")
    print("  ld(6)만 기존 상수(Compass=5/6)와 정확히 일치!")

    print("\n--- 실험: 학습률 스캔 (6블록 ConsciousLM) ---")
    base_lr = 1e-3
    lr_scales = [0.5, 0.6, 2/3, 0.7, 0.75, 5/6, 0.9, 1.0, 1.1, 1.2, 1.5]

    results = {}

    for scale in lr_scales:
        lr = base_lr * scale
        torch.manual_seed(42)

        model = ConsciousLM(
            vocab_size=256, d_model=128, n_head=2,
            n_layer=6, block_size=64, dropout=0.0
        ).to(device)

        losses, _ = train_model(model, device, n_steps=300, lr=lr, batch_size=16, seq_len=32)

        final_loss = np.mean(losses[-50:])
        min_loss = min(losses)

        results[scale] = {
            'lr': lr,
            'final_loss': final_loss,
            'min_loss': min_loss,
            'losses': losses
        }

        del model
        if torch.backends.mps.is_available():
            torch.mps.empty_cache()

    # 결과 테이블
    print(f"\n{'scale':>8} | {'lr':>10} | {'final_loss':>10} | {'min_loss':>10} | {'note':>20}")
    print("-" * 70)

    best_scale = min(results, key=lambda s: results[s]['final_loss'])

    for scale in lr_scales:
        r = results[scale]
        note = ""
        if abs(scale - 5/6) < 0.001:
            note = "<<< ld(6)=5/6"
        elif scale == best_scale:
            note = "<<< BEST"
        print(f"{scale:>8.4f} | {r['lr']:>10.6f} | {r['final_loss']:>10.4f} | {r['min_loss']:>10.4f} | {note:>20}")

    # ASCII 그래프
    print("\n--- ASCII: final loss vs lr scale ---")
    all_losses = [results[s]['final_loss'] for s in lr_scales]
    vmin, vmax = min(all_losses), max(all_losses)
    width = 50
    for scale in lr_scales:
        v = results[scale]['final_loss']
        if vmax > vmin:
            pos = int((v - vmin) / (vmax - vmin) * width)
        else:
            pos = 0
        bar = "#" * (width - pos) + "." * pos  # 낮은 loss = 긴 막대
        marker = " ***ld(6)" if abs(scale - 5/6) < 0.001 else ""
        print(f"  {scale:.4f}: [{bar}] {v:.4f}{marker}")

    print(f"\n  최적 스케일: {best_scale:.4f}")
    print(f"  ld(6)=5/6=0.8333 순위: {sorted(results, key=lambda s: results[s]['final_loss']).index(5/6) + 1}/{len(lr_scales)}")

    # 5/6과 최적의 거리
    dist = abs(best_scale - 5/6)
    print(f"  최적-ld(6) 거리: {dist:.4f}")

    return results


def main():
    print("=" * 70)
    print("Ralph 306: 학습된 ConsciousLM 교차 검증")
    print("H-CX-48/49/50 재검증 + H-CX-51 신규 실험")
    print("=" * 70)

    device = torch.device("mps" if torch.backends.mps.is_available() else "cpu")
    print(f"\nDevice: {device}")

    # ═══ Part 1: 블록 수별 학습 후 H-CX-48/49/50 측정 ═══
    print("\n" + "=" * 70)
    print("Part 1: 블록 수별 학습 → H-CX-48/49/50 측정")
    print("=" * 70)

    block_counts = [3, 4, 5, 6, 7, 8]
    all_results = {}

    for n_blocks in block_counts:
        print(f"\n--- {n_blocks} blocks: 학습 시작 ---")
        t0 = time.time()

        torch.manual_seed(42)
        model = ConsciousLM(
            vocab_size=256, d_model=128, n_head=2,
            n_layer=n_blocks, block_size=64, dropout=0.0
        ).to(device)

        n_params = model.count_params()
        print(f"  파라미터: {n_params:,}")

        # 학습
        losses, tension_hist = train_model(model, device, n_steps=500, lr=1e-3)
        train_time = time.time() - t0
        print(f"  학습 완료: {train_time:.1f}s, final loss={np.mean(losses[-50:]):.4f}")

        # H-CX-48: engine balance
        cx48 = measure_engine_balance(model, device)
        print(f"  CX-48 ratio: {cx48['mean_ratio']:.6f} (log: {cx48['mean_log']:+.6f})")

        # H-CX-49: tension distribution
        cx49 = measure_tension_distribution(model, device)
        print(f"  CX-49 tension: mean={cx49['mean']:.6f}, unique={cx49['n_unique']}, gaps={cx49['gap_fraction']:.3f}")

        # H-CX-50: conv collapse
        cx50 = measure_conv_collapse(model, device)
        print(f"  CX-50 collapse: {cx50['mean_score']:.6f}")

        all_results[n_blocks] = {
            'n_params': n_params,
            'final_loss': np.mean(losses[-50:]),
            'cx48': cx48,
            'cx49': cx49,
            'cx50': cx50,
            'losses': losses,
            'tension_hist': tension_hist
        }

        del model
        if torch.backends.mps.is_available():
            torch.mps.empty_cache()

    # ═══ 종합 결과 테이블 ═══
    print("\n" + "=" * 70)
    print("종합 결과: 학습 후 H-CX-48/49/50")
    print("=" * 70)

    # CX-48 테이블
    print("\n--- H-CX-48: engine A/G 비율 (학습 후) ---")
    print(f"{'blocks':>6} | {'|A|/|G|':>10} {'std':>8} | {'ln(A/G)':>10} {'std':>8} | {'|ratio-1|':>10} | {'I(n)_arith':>10}")
    print("-" * 80)

    for nb in block_counts:
        r = all_results[nb]['cx48']
        # 산술 I(n)
        divs = [d for d in range(1, nb+1) if nb % d == 0]
        sigma = sum(divs)
        tau = len(divs)
        phi_n = nb
        for p in set(_prime_factors(nb)):
            phi_n = phi_n * (p - 1) // p
        if nb == 1: phi_n = 1
        R = (sigma * phi_n) / (nb * tau)
        I_n = math.log(R)

        marker = " <<<" if nb == 6 else ""
        print(f"{nb:>6} | {r['mean_ratio']:>10.6f} {r['std_ratio']:>8.6f} | "
              f"{r['mean_log']:>+10.6f} {r['std_log']:>8.6f} | "
              f"{abs(r['mean_ratio']-1):>10.6f} | {I_n:>+10.6f}{marker}")

    # CX-48 ASCII
    print("\n--- ASCII: |ratio-1| (학습 후, 낮을수록 균형) ---")
    dists = {nb: abs(all_results[nb]['cx48']['mean_ratio'] - 1.0) for nb in block_counts}
    dmax = max(dists.values())
    for nb in block_counts:
        d = dists[nb]
        bar_len = int(d / (dmax + 1e-10) * 40)
        bar = "#" * bar_len + "." * (40 - bar_len)
        marker = " *** I(6)=0" if nb == 6 else ""
        print(f"  {nb:>2} blocks: [{bar}] {d:.6f}{marker}")

    closest = min(dists, key=dists.get)
    print(f"\n  비율 1.0에 가장 가까운 블록 수: {closest}")
    print(f"  6블록 순위: {sorted(dists.values()).index(dists[6]) + 1}/{len(block_counts)}")

    # CX-49 테이블
    print("\n--- H-CX-49: 장력 분포 (학습 후) ---")
    print(f"{'blocks':>6} | {'mean':>10} {'std':>10} | {'unique':>8} {'large_gaps':>10} {'gap_frac':>8}")
    print("-" * 70)
    for nb in block_counts:
        r = all_results[nb]['cx49']
        print(f"{nb:>6} | {r['mean']:>10.6f} {r['std']:>10.6f} | "
              f"{r['n_unique']:>8} {r['large_gaps']:>10} {r['gap_fraction']:>8.3f}")

    # CX-49 히스토그램 (6블록만)
    r6 = all_results[6]['cx49']
    print(f"\n--- 장력 히스토그램 (6 blocks, 학습 후) ---")
    max_h = max(r6['hist'])
    for i in range(len(r6['hist'])):
        bar_len = int(r6['hist'][i] / (max_h + 1) * 40)
        bar = "#" * bar_len
        lo = r6['bin_edges'][i]
        hi = r6['bin_edges'][i+1]
        print(f"  [{lo:8.5f},{hi:8.5f}) | {bar:<40} {r6['hist'][i]}")

    # CX-50 테이블
    print("\n--- H-CX-50: Convolution Collapse (학습 후) ---")
    print(f"{'blocks':>6} | {'score_mean':>12} {'score_std':>12}")
    print("-" * 40)
    for nb in block_counts:
        r = all_results[nb]['cx50']
        marker = " <<<" if nb == 6 else ""
        print(f"{nb:>6} | {r['mean_score']:>12.6f} {r['std_score']:>12.6f}{marker}")

    # CX-50 ASCII
    print("\n--- ASCII: Collapse Score (낮을수록 합성곱 붕괴) ---")
    scores = {nb: all_results[nb]['cx50']['mean_score'] for nb in block_counts}
    smax = max(scores.values())
    for nb in block_counts:
        s = scores[nb]
        bar_len = int(s / (smax + 1e-10) * 40)
        bar = "#" * bar_len + "." * (40 - bar_len)
        marker = " *** n=6" if nb == 6 else ""
        print(f"  {nb:>2} blocks: [{bar}] {s:.6f}{marker}")

    best_collapse = min(scores, key=scores.get)
    print(f"\n  최소 collapse 블록 수: {best_collapse}")
    print(f"  6블록 순위: {sorted(scores.values()).index(scores[6]) + 1}/{len(block_counts)}")

    # 학습 곡선 비교
    print("\n--- 학습 곡선 (final 50 steps avg) ---")
    print(f"{'blocks':>6} | {'params':>10} | {'final_loss':>10}")
    print("-" * 35)
    for nb in block_counts:
        r = all_results[nb]
        print(f"{nb:>6} | {r['n_params']:>10,} | {r['final_loss']:>10.4f}")

    # ═══ Part 2: H-CX-51 학습률 실험 ═══
    cx51_results = experiment_cx51_learning_rate(device)

    # ═══ 종합 판정 ═══
    print("\n" + "=" * 70)
    print("종합 판정")
    print("=" * 70)

    # CX-48 판정
    cx48_rank = sorted(dists.values()).index(dists[6]) + 1
    cx48_verdict = "CONFIRMED" if cx48_rank <= 2 else "WEAK" if cx48_rank <= 3 else "NOT CONFIRMED"
    print(f"\n  H-CX-48 (학습 후): 6블록 순위={cx48_rank}/{len(block_counts)} → {cx48_verdict}")

    # CX-49 판정
    cx49_6 = all_results[6]['cx49']
    cx49_verdict = "CONFIRMED" if cx49_6['gap_fraction'] > 0.1 else "NOT CONFIRMED"
    print(f"  H-CX-49 (학습 후): gap_fraction={cx49_6['gap_fraction']:.3f} → {cx49_verdict}")

    # CX-50 판정
    cx50_rank = sorted(scores.values()).index(scores[6]) + 1
    cx50_verdict = "CONFIRMED" if cx50_rank <= 2 else "WEAK" if cx50_rank <= 3 else "NOT CONFIRMED"
    print(f"  H-CX-50 (학습 후): 6블록 순위={cx50_rank}/{len(block_counts)} → {cx50_verdict}")

    # CX-51 판정
    lr_ranks = sorted(cx51_results, key=lambda s: cx51_results[s]['final_loss'])
    cx51_rank = lr_ranks.index(5/6) + 1
    cx51_verdict = "CONFIRMED" if cx51_rank <= 3 else "WEAK" if cx51_rank <= 5 else "NOT CONFIRMED"
    print(f"  H-CX-51 (lr scan): 5/6 순위={cx51_rank}/{len(lr_ranks)} → {cx51_verdict}")

    print("\n--- 미학습 vs 학습 비교 ---")
    print("  미학습 기준선 (R305):")
    print("    CX-48: 모든 블록 비율≈1.0, 6블록 특별하지 않음")
    print("    CX-49: 연속 가우시안, gap=2.4%")
    print("    CX-50: 약한 감소 추세")
    print("  학습 후 (R306):")
    print(f"    CX-48: 6블록 순위={cx48_rank}, |ratio-1|={dists[6]:.6f}")
    print(f"    CX-49: gap_fraction={cx49_6['gap_fraction']:.3f}, unique={cx49_6['n_unique']}")
    print(f"    CX-50: 6블록 score={scores[6]:.6f}, 순위={cx50_rank}")

    print("\n실험 완료.")


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


if __name__ == "__main__":
    main()
