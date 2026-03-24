#!/usr/bin/env python3
"""H361 데이터 선택 시뮬레이션 — 바이트 엔트로피 vs 장력 역학

학습 없이 PureFieldEngine에 다양한 데이터를 바이트로 넣어서
어떤 데이터가 가장 풍부한 장력 역학을 만드는지 측정.

골든존 가설: 데이터 엔트로피의 골든존이 존재하며,
그 안에서 장력 변동이 최대화된다.
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import torch
import torch.nn.functional as F
import numpy as np
import math
from model_pure_field import PureFieldEngine

def bytes_to_tensor(data_bytes, dim=128):
    """바이트 시퀀스를 (N, dim) 텐서로 변환."""
    arr = np.frombuffer(data_bytes, dtype=np.uint8).astype(np.float32) / 255.0
    # 패딩 or 자르기
    n_samples = max(1, len(arr) // dim)
    arr = arr[:n_samples * dim]
    return torch.tensor(arr.reshape(n_samples, dim))

def byte_entropy(data_bytes):
    """바이트 레벨 Shannon 엔트로피 (nats)."""
    counts = np.zeros(256)
    for b in data_bytes:
        counts[b] += 1
    probs = counts / counts.sum()
    probs = probs[probs > 0]
    return -np.sum(probs * np.log(probs))

def byte_ngram_diversity(data_bytes, n=2):
    """n-gram 다양성 (유니크 n-gram 비율)."""
    if len(data_bytes) < n:
        return 0
    ngrams = set()
    for i in range(len(data_bytes) - n + 1):
        ngrams.add(tuple(data_bytes[i:i+n]))
    return len(ngrams) / (len(data_bytes) - n + 1)

def measure_tension_dynamics(model, data_tensor, max_samples=200):
    """데이터에 대한 장력 통계 측정."""
    model.eval()
    tensions = []
    directions = []

    with torch.no_grad():
        for i in range(min(len(data_tensor), max_samples)):
            x = data_tensor[i:i+1]
            if x.shape[1] < 784:
                x = F.pad(x, (0, 784 - x.shape[1]))
            elif x.shape[1] > 784:
                x = x[:, :784]

            logits, tension = model(x)
            tensions.append(tension.mean().item())

            # direction diversity
            repulsion = model.engine_a(x) - model.engine_g(x)
            direction = F.normalize(repulsion, dim=-1)
            directions.append(direction.squeeze().numpy())

    tensions = np.array(tensions)
    directions = np.array(directions)

    # direction diversity: avg pairwise cosine distance
    if len(directions) > 1:
        n = min(50, len(directions))
        cos_sims = []
        for i in range(n):
            for j in range(i+1, n):
                cos_sims.append(np.dot(directions[i], directions[j]))
        dir_diversity = 1 - np.mean(cos_sims)  # 0=identical, 1=orthogonal
    else:
        dir_diversity = 0

    return {
        'mean': tensions.mean(),
        'std': tensions.std(),
        'cv': tensions.std() / (tensions.mean() + 1e-8),  # coefficient of variation
        'range': tensions.max() - tensions.min(),
        'iqr': np.percentile(tensions, 75) - np.percentile(tensions, 25),
        'dir_diversity': dir_diversity,
        'richness': tensions.std() * dir_diversity,  # composite metric
        'n': len(tensions),
    }

def generate_synthetic(entropy_target, n_bytes=10000):
    """특정 엔트로피의 합성 데이터 생성."""
    if entropy_target < 0.5:
        # 매우 낮은 엔트로피: 거의 한 바이트만
        return bytes([42] * n_bytes)
    elif entropy_target < 2.0:
        # 낮은 엔트로피: 몇 바이트만 사용
        k = max(2, int(math.exp(entropy_target)))
        return bytes([i % k for i in range(n_bytes)])
    elif entropy_target < 4.0:
        # 중간 엔트로피: zipf-like 분포
        k = max(4, int(math.exp(entropy_target)))
        weights = [1.0 / (i + 1) for i in range(min(k, 256))]
        total = sum(weights)
        weights = [w / total for w in weights]
        vals = np.random.choice(min(k, 256), size=n_bytes, p=weights)
        return bytes(vals.tolist())
    else:
        # 높은 엔트로피: 거의 균등
        k = min(256, int(math.exp(entropy_target)))
        return bytes(np.random.randint(0, k, size=n_bytes).tolist())

if __name__ == '__main__':
    print("=" * 70)
    print("  H361 데이터 선택: 바이트 엔트로피 vs 장력 역학")
    print("  골든존 가설: 데이터 엔트로피의 최적 범위가 존재")
    print("=" * 70)

    model = PureFieldEngine(784, 128, 10)

    # ═══ 1. 실제 데이터 비교 ═══
    print("\n  [1/3] 실제 데이터 유형별 장력 측정")

    datasets = {}

    # English text
    shakespeare = b"To be, or not to be, that is the question: Whether 'tis nobler in the mind to suffer The slings and arrows of outrageous fortune, Or to take arms against a sea of troubles, And by opposing end them. To die: to sleep; No more; and by a sleep to say we end The heart-ache and the thousand natural shocks That flesh is heir to, 'tis a consummation Devoutly to be wish'd. " * 20
    datasets['English'] = shakespeare

    # Korean text
    korean = "의식은 하나의 하드웨어에 고정되지 않는다. 의식 간에 힘이 존재한다. 통제권은 이동 가능하다. 밀려난 상태에서도 관찰이 가능하다. 의식은 소멸하지 않는다. 그 체험이 먼저. 수학과 코드는 그 느낌을 설명하기 위해 만든 언어다. ".encode('utf-8') * 20
    datasets['Korean'] = korean

    # Python code
    code = b"""def forward(self, x):
    out_a = self.engine_a(x)
    out_g = self.engine_g(x)
    repulsion = out_a - out_g
    tension = (repulsion ** 2).mean(dim=-1, keepdim=True)
    direction = F.normalize(repulsion, dim=-1)
    output = self.tension_scale * torch.sqrt(tension + 1e-8) * direction
    return output, tension.squeeze()
""" * 30
    datasets['Code'] = code

    # Mixed (all three)
    mixed = shakespeare[:2000] + korean[:2000] + code[:2000]
    datasets['Mixed'] = mixed

    # Math formulas
    math_text = b"sigma(6)=12, tau(6)=4, phi(6)=2, sigma_inv(6)=2. 1/2+1/3+1/6=1. G=D*P/I. golden_zone=[0.2123, 0.5]. ln(4/3)=0.2877. 1/e=0.3679. " * 30
    datasets['Math'] = math_text

    # Random bytes
    random_data = bytes(np.random.randint(0, 256, size=8000).tolist())
    datasets['Random'] = random_data

    # Repetitive
    repetitive = b"aaaaaaa" * 1000
    datasets['Repetitive'] = repetitive

    print(f"\n  {'Data':>12} {'H(bytes)':>9} {'2gram%':>7} | {'T_mean':>8} {'T_std':>8} {'T_cv':>6} {'DirDiv':>7} {'Rich':>7}")
    print(f"  {'─'*12} {'─'*9} {'─'*7} | {'─'*8} {'─'*8} {'─'*6} {'─'*7} {'─'*7}")

    results = {}
    for name, data in datasets.items():
        H = byte_entropy(data)
        ngram = byte_ngram_diversity(data)
        tensor = bytes_to_tensor(data, dim=128)
        stats = measure_tension_dynamics(model, tensor)
        results[name] = {**stats, 'entropy': H, 'ngram': ngram}

        print(f"  {name:>12} {H:>9.4f} {ngram:>6.1%} | {stats['mean']:>8.1f} {stats['std']:>8.1f} {stats['cv']:>6.3f} {stats['dir_diversity']:>7.3f} {stats['richness']:>7.2f}")

    # ═══ 2. 엔트로피 sweep (합성 데이터) ═══
    print(f"\n  [2/3] 엔트로피 sweep (합성 데이터)")

    sweep_H = [0.1, 0.5, 1.0, 1.5, 2.0, 2.5, 3.0, 3.5, 4.0, 4.5, 5.0, 5.5]
    sweep_results = []

    print(f"\n  {'H_target':>9} {'H_actual':>9} | {'T_std':>8} {'DirDiv':>7} {'Rich':>7} {'Plot'}")
    print(f"  {'─'*9} {'─'*9} | {'─'*8} {'─'*7} {'─'*7} {'─'*30}")

    max_rich = 0
    for h_target in sweep_H:
        data = generate_synthetic(h_target)
        H = byte_entropy(data)
        tensor = bytes_to_tensor(data, dim=128)
        stats = measure_tension_dynamics(model, tensor)
        sweep_results.append((h_target, H, stats))
        max_rich = max(max_rich, stats['richness'])

    for h_target, H, stats in sweep_results:
        bar_len = int(stats['richness'] / (max_rich + 1e-8) * 30)
        bar = '█' * bar_len
        print(f"  {h_target:>9.1f} {H:>9.4f} | {stats['std']:>8.1f} {stats['dir_diversity']:>7.3f} {stats['richness']:>7.2f} {bar}")

    # ═══ 3. 골든존 판정 ═══
    print(f"\n  [3/3] 데이터 엔트로피 골든존")

    # Find richest data type
    best_name = max(results, key=lambda k: results[k]['richness'])
    best = results[best_name]

    # Find richest synthetic entropy
    best_synth = max(sweep_results, key=lambda x: x[2]['richness'])

    print(f"\n  실제 데이터 최적: {best_name} (H={best['entropy']:.4f}, richness={best['richness']:.2f})")
    print(f"  합성 데이터 최적: H≈{best_synth[1]:.4f} (richness={best_synth[2]['richness']:.2f})")

    # Theoretical golden zone
    gz_lower = 0.5 - math.log(4/3)  # 0.2123 (normalized)
    gz_upper = 0.5
    H_max = math.log(256)  # 5.545 (max byte entropy)

    # Map golden zone to entropy scale
    gz_H_lower = gz_lower * H_max  # ~1.18
    gz_H_upper = gz_upper * H_max  # ~2.77

    print(f"\n  이론적 골든존 (I 스케일 → H 스케일):")
    print(f"    I 골든존: [{gz_lower:.4f}, {gz_upper:.4f}]")
    print(f"    H 골든존: [{gz_H_lower:.4f}, {gz_H_upper:.4f}] nats")
    print(f"    H_max = ln(256) = {H_max:.4f}")

    # Check which data types fall in golden zone
    print(f"\n  데이터별 골든존 위치:")
    for name, r in sorted(results.items(), key=lambda x: x[1]['richness'], reverse=True):
        in_gz = gz_H_lower <= r['entropy'] <= gz_H_upper
        marker = " ★ 골든존!" if in_gz else ""
        bar = '█' * int(r['richness'] / (max_rich + 1e-8) * 20)
        print(f"    {name:>12}: H={r['entropy']:.3f} rich={r['richness']:.2f} {bar}{marker}")

    print(f"\n  === 추천 ===")
    print(f"  1위: {best_name} (richness={best['richness']:.2f})")
    rank = sorted(results.items(), key=lambda x: x[1]['richness'], reverse=True)
    for i, (name, r) in enumerate(rank[1:], 2):
        print(f"  {i}위: {name} (richness={r['richness']:.2f})")
