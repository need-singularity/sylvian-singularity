#!/usr/bin/env python3
"""생성 엔진 — 반발력장 잠재 공간의 VAE

반발력장 아키텍처를 생성 모델로 확장.
핵심 통찰: "엔진 사이의 장(field)"이 바로 생성적 잠재 공간이다.

두 축:
  내용 축 (A vs G) = 의미 (무엇을 생성할 것인가)
  구조 축 (E vs F) = 맥락 (어떻게 생성할 것인가)

장력(tension)이 생성의 창의성을 제어:
  낮은 장력 (0.1)     → 안전, 평균적, 지루한 생성
  중간 장력 (~1/e)     → 균형, 의미 있는 생성 (골든존)
  높은 장력 (>1.0)     → 야생적, 새로운, 비일관적 가능성

수학적 근거:
  - 잠재 공간 = 반발력장의 평형점
  - VAE의 KL divergence = 장력의 정보론적 비용
  - 재구성 loss = 장이 현실을 얼마나 잘 반영하는가
  - 장력 조절 = 탐색(exploration) vs 활용(exploitation) 트레이드오프
"""

import torch
import torch.nn as nn
import torch.nn.functional as F
import numpy as np
import math

from model_utils import (
    Expert, SIGMA, TAU, DIVISOR_RECIPROCALS, H_TARGET,
    load_mnist, count_params,
)


# ─────────────────────────────────────────
# ASCII 아트 렌더링
# ─────────────────────────────────────────

def tensor_to_ascii(tensor_28x28, width=14, height=14):
    """28x28 텐서를 ASCII 아트로 변환.

    2x2 블록을 평균 풀링하여 다운샘플링.
    밝기를 문자로 매핑.
    """
    chars = ' .:-=+*#%@'
    img = tensor_28x28.detach().cpu().squeeze()
    if img.dim() == 1:
        img = img.view(28, 28)

    # 0-1 범위로 정규화
    vmin, vmax = img.min(), img.max()
    if vmax - vmin > 1e-6:
        img = (img - vmin) / (vmax - vmin)
    else:
        img = torch.zeros_like(img)

    # 2x2 평균 풀링으로 다운샘플
    img_4d = img.unsqueeze(0).unsqueeze(0)
    pooled = F.avg_pool2d(img_4d, kernel_size=2).squeeze()  # (14, 14)

    lines = []
    for row in range(pooled.size(0)):
        line = ''
        for col in range(pooled.size(1)):
            val = pooled[row, col].item()
            idx = int(val * (len(chars) - 1))
            idx = max(0, min(len(chars) - 1, idx))
            line += chars[idx]
        lines.append(line)
    return '\n'.join(lines)


def show_ascii_grid(tensors, labels=None, width=14, height=14, cols=5):
    """여러 이미지를 ASCII 그리드로 표시."""
    if labels is None:
        labels = [f'[{i}]' for i in range(len(tensors))]

    ascii_images = [tensor_to_ascii(t, width, height).split('\n') for t in tensors]

    # 열 단위로 출력
    for row_start in range(0, len(ascii_images), cols):
        row_end = min(row_start + cols, len(ascii_images))
        batch = ascii_images[row_start:row_end]
        batch_labels = labels[row_start:row_end]

        # 라벨 행
        label_line = '  '.join(f'{l:^{width}}' for l in batch_labels)
        print(f'  {label_line}')

        # 이미지 행
        for line_idx in range(height):
            parts = []
            for img_lines in batch:
                if line_idx < len(img_lines):
                    parts.append(img_lines[line_idx])
                else:
                    parts.append(' ' * width)
            print(f'  {"  ".join(parts)}')
        print()


# ─────────────────────────────────────────
# 엔진 인코더 (경량 버전)
# ─────────────────────────────────────────

class EngineEncoder(nn.Module):
    """단일 엔진의 인코더.

    엔진 특성을 반영한 잠재 공간 매핑.
    mu와 logvar를 출력하여 VAE 재매개변수화에 사용.
    """
    def __init__(self, input_dim, latent_dim, engine_type='A'):
        super().__init__()
        self.encoder = nn.Sequential(
            nn.Linear(input_dim, 128),
            nn.ReLU(),
            nn.Linear(128, 64),
            nn.ReLU(),
        )
        self.mu = nn.Linear(64, latent_dim)
        self.logvar = nn.Linear(64, latent_dim)
        self.engine_type = engine_type

    def forward(self, x):
        h = self.encoder(x)
        return self.mu(h), self.logvar(h), h


# ─────────────────────────────────────────
# RepulsionFieldVAE
# ─────────────────────────────────────────

class RepulsionFieldVAE(nn.Module):
    """반발력장 잠재 공간의 변분 오토인코더.

    4개 엔진이 잠재 공간에서 반발력장을 형성:
      내용 축: A(생성) ←반발→ G(교정) = 의미 벡터
      구조 축: E(탐색) ←반발→ F(제약) = 맥락 벡터

    장력이 생성의 날카로움을 결정:
      높은 장력 = 선명하고 확신 있는 생성
      낮은 장력 = 흐리고 평균적인 생성
    """

    def __init__(self, input_dim=784, latent_dim=16):
        super().__init__()
        self.input_dim = input_dim
        self.latent_dim = latent_dim

        # 공유 인코더
        self.shared_encoder = nn.Sequential(
            nn.Linear(input_dim, 256),
            nn.ReLU(),
            nn.Linear(256, 128),
            nn.ReLU(),
        )

        # 4개 엔진 인코더 (공유 인코더 출력에서 분기)
        self.engine_a_enc = EngineEncoder(128, latent_dim, 'A')  # 생성
        self.engine_g_enc = EngineEncoder(128, latent_dim, 'G')  # 교정
        self.engine_e_enc = EngineEncoder(128, latent_dim, 'E')  # 탐색
        self.engine_f_enc = EngineEncoder(128, latent_dim, 'F')  # 제약

        # 반발력 → 잠재 분포 매핑
        self.content_mu = nn.Linear(latent_dim, latent_dim)
        self.content_logvar = nn.Linear(latent_dim, latent_dim)
        self.structure_mu = nn.Linear(latent_dim, latent_dim)
        self.structure_logvar = nn.Linear(latent_dim, latent_dim)

        # 디코더: latent_dim*2 (content + structure) → 이미지
        self.decoder = nn.Sequential(
            nn.Linear(latent_dim * 2, 128),
            nn.ReLU(),
            nn.Linear(128, 256),
            nn.ReLU(),
            nn.Linear(256, input_dim),
            nn.Sigmoid(),
        )

        # 장력 스케일 (학습 가능, 초기값 1/3 = 메타 부동점)
        self.tension_scale = nn.Parameter(torch.tensor(1 / 3))

        # 모니터링
        self.tension_content = 0.0
        self.tension_structure = 0.0

    def encode(self, x):
        """입력을 잠재 공간으로 인코딩.

        Returns:
            mu_content, logvar_content: 내용 축 분포
            mu_structure, logvar_structure: 구조 축 분포
            tension_content, tension_structure: 각 축의 장력
        """
        h = self.shared_encoder(x)

        # 4개 엔진의 잠재 표현
        mu_a, logvar_a, _ = self.engine_a_enc(h)
        mu_g, logvar_g, _ = self.engine_g_enc(h)
        mu_e, logvar_e, _ = self.engine_e_enc(h)
        mu_f, logvar_f, _ = self.engine_f_enc(h)

        # 반발력 = 두 엔진 mu의 차이 (의미 벡터)
        repulsion_content = mu_a - mu_g      # 내용 축 반발
        repulsion_structure = mu_e - mu_f    # 구조 축 반발

        # 장력 = 반발의 크기
        t_content = (repulsion_content ** 2).sum(dim=-1, keepdim=True)
        t_structure = (repulsion_structure ** 2).sum(dim=-1, keepdim=True)

        # 반발력의 평형점 → 잠재 분포의 mu
        # 평형 = 두 극의 평균, 반발력이 방향을 제공
        content_eq = (mu_a + mu_g) / 2
        structure_eq = (mu_e + mu_f) / 2

        mu_content = self.content_mu(content_eq + self.tension_scale * repulsion_content)
        logvar_content = self.content_logvar(content_eq)
        mu_structure = self.structure_mu(structure_eq + self.tension_scale * repulsion_structure)
        logvar_structure = self.structure_logvar(structure_eq)

        return (mu_content, logvar_content,
                mu_structure, logvar_structure,
                t_content, t_structure)

    def reparameterize(self, mu, logvar):
        """재매개변수화 트릭."""
        std = torch.exp(0.5 * logvar)
        eps = torch.randn_like(std)
        return mu + eps * std

    def decode(self, z, tension=None):
        """잠재 벡터를 이미지로 디코딩.

        Args:
            z: (batch, latent_dim*2) 잠재 벡터
            tension: 장력 스케일. None이면 기본값 사용.
        """
        out = self.decoder(z)

        if tension is not None:
            # 장력이 높으면 출력을 더 날카롭게 (대비 증가)
            # sigmoid를 다시 적용하여 0-1 범위 유지
            sharpness = 1.0 + tension * 2.0
            out = torch.sigmoid((out - 0.5) * sharpness)

        return out

    def forward(self, x):
        """순전파: 인코딩 → 재매개변수화 → 디코딩."""
        (mu_c, logvar_c, mu_s, logvar_s,
         t_content, t_structure) = self.encode(x)

        z_content = self.reparameterize(mu_c, logvar_c)
        z_structure = self.reparameterize(mu_s, logvar_s)
        z = torch.cat([z_content, z_structure], dim=-1)

        recon = self.decode(z)

        # 모니터링
        with torch.no_grad():
            self.tension_content = t_content.mean().item()
            self.tension_structure = t_structure.mean().item()

        return recon, mu_c, logvar_c, mu_s, logvar_s

    def generate(self, n_samples=1, tension_level=None, device='cpu'):
        """새로운 이미지 생성.

        Args:
            n_samples: 생성할 이미지 수
            tension_level: 장력 수준 (None=기본, float=지정)
            device: 디바이스
        """
        z = torch.randn(n_samples, self.latent_dim * 2, device=device)

        if tension_level is not None:
            # 장력에 비례하여 잠재 벡터 스케일 조정
            z = z * tension_level

        return self.decode(z, tension=tension_level)

    def interpolate(self, x1, x2, steps=7, axis='content'):
        """두 입력 사이를 보간.

        Args:
            x1, x2: 입력 이미지 (batch=1)
            steps: 보간 단계 수
            axis: 'content' (내용 축) 또는 'structure' (구조 축)
        """
        (mu_c1, _, mu_s1, _, _, _) = self.encode(x1)
        (mu_c2, _, mu_s2, _, _, _) = self.encode(x2)

        results = []
        for i in range(steps):
            alpha = i / (steps - 1)

            if axis == 'content':
                # 내용만 보간, 구조는 x1 고정
                mu_c = (1 - alpha) * mu_c1 + alpha * mu_c2
                mu_s = mu_s1
            elif axis == 'structure':
                # 구조만 보간, 내용은 x1 고정
                mu_c = mu_c1
                mu_s = (1 - alpha) * mu_s1 + alpha * mu_s2
            else:
                # 양축 동시 보간
                mu_c = (1 - alpha) * mu_c1 + alpha * mu_c2
                mu_s = (1 - alpha) * mu_s1 + alpha * mu_s2

            z = torch.cat([mu_c, mu_s], dim=-1)
            recon = self.decode(z)
            results.append(recon)

        return results


# ─────────────────────────────────────────
# VAE 손실 함수
# ─────────────────────────────────────────

def vae_loss(recon, target, mu_c, logvar_c, mu_s, logvar_s, beta=1.0):
    """VAE 손실 = 재구성 손실 + beta * KL divergence.

    Args:
        recon: 재구성 이미지
        target: 원본 이미지
        mu_c, logvar_c: 내용 축 분포 파라미터
        mu_s, logvar_s: 구조 축 분포 파라미터
        beta: KL 가중치 (beta-VAE)
    """
    # 재구성 손실: Binary Cross Entropy
    recon_loss = F.binary_cross_entropy(recon, target, reduction='sum')

    # KL divergence: 내용 + 구조
    kl_content = -0.5 * torch.sum(1 + logvar_c - mu_c.pow(2) - logvar_c.exp())
    kl_structure = -0.5 * torch.sum(1 + logvar_s - mu_s.pow(2) - logvar_s.exp())

    kl = kl_content + kl_structure

    return recon_loss + beta * kl, recon_loss, kl


# ─────────────────────────────────────────
# 학습 루프
# ─────────────────────────────────────────

def train_vae(model, train_loader, epochs=20, lr=1e-3, beta=1.0, verbose=True):
    """VAE 학습.

    beta 스케줄: 처음 5 에폭은 beta를 0에서 목표값까지 선형 증가.
    (KL annealing — 초기에 재구성에 집중)
    """
    optimizer = torch.optim.Adam(model.parameters(), lr=lr)

    history = {
        'total_loss': [], 'recon_loss': [], 'kl_loss': [],
        'tension_content': [], 'tension_structure': [],
    }

    for epoch in range(epochs):
        model.train()
        total_loss = 0
        total_recon = 0
        total_kl = 0
        n_samples = 0

        # KL annealing: 5 에폭에 걸쳐 선형 증가
        beta_current = min(beta, beta * (epoch + 1) / 5)

        for X, _ in train_loader:
            X = X.view(X.size(0), -1)
            # MNIST 정규화 역변환: (x - 0.1307) / 0.3081 → x
            # sigmoid 출력과 비교하려면 0-1 범위 필요
            X_target = X * 0.3081 + 0.1307
            X_target = X_target.clamp(0, 1)

            optimizer.zero_grad()
            recon, mu_c, logvar_c, mu_s, logvar_s = model(X)

            loss, recon_l, kl_l = vae_loss(
                recon, X_target, mu_c, logvar_c, mu_s, logvar_s, beta_current
            )

            loss.backward()
            optimizer.step()

            batch_size = X.size(0)
            total_loss += loss.item()
            total_recon += recon_l.item()
            total_kl += kl_l.item()
            n_samples += batch_size

        avg_loss = total_loss / n_samples
        avg_recon = total_recon / n_samples
        avg_kl = total_kl / n_samples

        history['total_loss'].append(avg_loss)
        history['recon_loss'].append(avg_recon)
        history['kl_loss'].append(avg_kl)
        history['tension_content'].append(model.tension_content)
        history['tension_structure'].append(model.tension_structure)

        if verbose and ((epoch + 1) % 2 == 0 or epoch == 0):
            print(f'    Epoch {epoch+1:>2}/{epochs}: '
                  f'Loss={avg_loss:.2f}  Recon={avg_recon:.2f}  KL={avg_kl:.2f}  '
                  f'beta={beta_current:.3f}  '
                  f'T_c={model.tension_content:.2f}  T_s={model.tension_structure:.2f}')

    return history


# ─────────────────────────────────────────
# 간단한 분류기 (생성 결과 평가용)
# ─────────────────────────────────────────

class SimpleClassifier(nn.Module):
    """생성된 이미지의 숫자를 판별하는 간단한 분류기."""
    def __init__(self, input_dim=784, hidden_dim=128, output_dim=10):
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(input_dim, hidden_dim),
            nn.ReLU(),
            nn.Linear(hidden_dim, output_dim),
        )

    def forward(self, x):
        return self.net(x)


def train_classifier(model, train_loader, epochs=5):
    """분류기 학습."""
    optimizer = torch.optim.Adam(model.parameters(), lr=1e-3)
    criterion = nn.CrossEntropyLoss()

    for epoch in range(epochs):
        model.train()
        for X, y in train_loader:
            X = X.view(X.size(0), -1)
            optimizer.zero_grad()
            loss = criterion(model(X), y)
            loss.backward()
            optimizer.step()

    model.eval()
    return model


# ─────────────────────────────────────────
# 메인
# ─────────────────────────────────────────

def main():
    print()
    print('=' * 65)
    print('   logout -- RepulsionFieldVAE: Generative Engine')
    print('   The field between engines IS the generative space')
    print('=' * 65)

    # ── 데이터 로드 ──
    print('\n[1] Loading MNIST...')
    train_loader, test_loader = load_mnist(batch_size=128)

    # ── 모델 생성 ──
    latent_dim = 16
    model = RepulsionFieldVAE(input_dim=784, latent_dim=latent_dim)
    n_params = count_params(model)
    print(f'    RepulsionFieldVAE: {n_params:,} parameters')
    print(f'    Latent dim: {latent_dim} x 2 axes = {latent_dim * 2} total')
    print(f'    Content axis: A(generate) <-repulsion-> G(correct)')
    print(f'    Structure axis: E(explore) <-repulsion-> F(constrain)')

    # ── 학습 ──
    print(f'\n[2] Training (20 epochs, KL annealing)...')
    history = train_vae(model, train_loader, epochs=20, lr=1e-3, beta=1.0)

    print(f'\n    Final: Recon={history["recon_loss"][-1]:.2f}  '
          f'KL={history["kl_loss"][-1]:.2f}')
    print(f'    Tension scale (learned): {model.tension_scale.item():.4f} '
          f'(init=1/3={1/3:.4f})')

    # ── 재구성 품질 ──
    print(f'\n[3] Reconstruction quality...')
    model.eval()

    test_iter = iter(test_loader)
    X_test, y_test = next(test_iter)
    X_flat = X_test.view(X_test.size(0), -1)
    X_target = X_flat * 0.3081 + 0.1307
    X_target = X_target.clamp(0, 1)

    with torch.no_grad():
        recon, _, _, _, _ = model(X_flat)

    # 5개 샘플 표시
    n_show = 5
    print('\n    Original:')
    show_ascii_grid(
        [X_target[i].view(28, 28) for i in range(n_show)],
        [f'y={y_test[i].item()}' for i in range(n_show)],
        cols=n_show,
    )
    print('    Reconstructed:')
    show_ascii_grid(
        [recon[i].view(28, 28) for i in range(n_show)],
        [f'y={y_test[i].item()}' for i in range(n_show)],
        cols=n_show,
    )

    # ── 장력 제어 생성 ──
    print(f'\n[4] Tension-controlled generation...')
    tension_levels = [0.1, 0.3, 1 / math.e, 0.7, 1.5]
    tension_labels = ['T=0.1', 'T=0.3', f'T=1/e', 'T=0.7', 'T=1.5']

    print('    Low tension  = safe, average, boring')
    print('    1/e tension  = golden zone (balanced, meaningful)')
    print('    High tension = wild, novel, possibly incoherent')
    print()

    for t_val, t_label in zip(tension_levels, tension_labels):
        with torch.no_grad():
            generated = model.generate(n_samples=5, tension_level=t_val)
        print(f'    {t_label} (tension={t_val:.4f}):')
        show_ascii_grid(
            [generated[i].view(28, 28) for i in range(5)],
            [f'#{i+1}' for i in range(5)],
            cols=5,
        )

    # ── 의미 축 탐색 (내용 보간) ──
    print(f'\n[5] Content axis exploration (meaning morphing)...')
    print('    Interpolating CONTENT while keeping STRUCTURE fixed')
    print('    This shows how one concept becomes another\n')

    # 두 다른 숫자 찾기 (3과 8)
    digit_a, digit_b = 3, 8
    idx_a = idx_b = None
    for i in range(len(y_test)):
        if y_test[i].item() == digit_a and idx_a is None:
            idx_a = i
        if y_test[i].item() == digit_b and idx_b is None:
            idx_b = i
        if idx_a is not None and idx_b is not None:
            break

    if idx_a is not None and idx_b is not None:
        x1 = X_flat[idx_a:idx_a + 1]
        x2 = X_flat[idx_b:idx_b + 1]

        with torch.no_grad():
            interp = model.interpolate(x1, x2, steps=7, axis='content')

        print(f'    {digit_a} --> {digit_b} (content axis, 7 steps):')
        labels = [f'{digit_a}'] + [f'{i+1}/5' for i in range(5)] + [f'{digit_b}']
        show_ascii_grid(
            [img.view(28, 28) for img in interp],
            labels,
            cols=7,
        )

    # ── 맥락 축 탐색 (구조 보간) ──
    print(f'\n[6] Structure axis exploration (style morphing)...')
    print('    Interpolating STRUCTURE while keeping CONTENT fixed')
    print('    Same digit, different handwriting style\n')

    # 같은 숫자 다른 스타일 2개 찾기
    target_digit = 7
    indices = [i for i in range(len(y_test)) if y_test[i].item() == target_digit]

    if len(indices) >= 2:
        # 가장 다른 두 샘플 선택 (L2 거리 기반)
        idx1 = indices[0]
        max_dist = 0
        idx2 = indices[1]
        for j in indices[1:min(len(indices), 50)]:
            dist = (X_flat[idx1] - X_flat[j]).pow(2).sum().item()
            if dist > max_dist:
                max_dist = dist
                idx2 = j

        x1 = X_flat[idx1:idx1 + 1]
        x2 = X_flat[idx2:idx2 + 1]

        with torch.no_grad():
            interp = model.interpolate(x1, x2, steps=7, axis='structure')

        print(f'    Digit {target_digit}, style A --> style B (structure axis, 7 steps):')
        labels = ['A'] + [f'{i+1}/5' for i in range(5)] + ['B']
        show_ascii_grid(
            [img.view(28, 28) for img in interp],
            labels,
            cols=7,
        )

    # ── 드리밍 모드 ──
    print(f'\n[7] Dreaming mode (random latent sampling)...')
    print('    No input -- the engine imagines\n')

    # 분류기 학습 (생성 결과 평가용)
    print('    Training classifier for dream analysis...')
    classifier = SimpleClassifier()
    classifier = train_classifier(classifier, train_loader, epochs=5)

    dream_tensions = [0.3, 1 / math.e, 0.8]
    dream_labels_t = ['calm', 'golden', 'vivid']

    for t_val, t_name in zip(dream_tensions, dream_labels_t):
        n_dreams = 100
        with torch.no_grad():
            dreams = model.generate(n_samples=n_dreams, tension_level=t_val)
            logits = classifier(dreams)
            predicted = logits.argmax(dim=-1)

        # 분포 계산
        counts = torch.zeros(10)
        for d in range(10):
            counts[d] = (predicted == d).sum().item()

        # 상위 5개 표시
        show_dreams = model.generate(n_samples=5, tension_level=t_val)
        print(f'    Dream ({t_name}, T={t_val:.3f}):')
        show_ascii_grid(
            [show_dreams[i].view(28, 28) for i in range(5)],
            [f'#{i+1}' for i in range(5)],
            cols=5,
        )

        # 분포 막대 그래프
        max_count = counts.max().item()
        print(f'    Digit distribution (n={n_dreams}):')
        for d in range(10):
            bar_len = int(counts[d].item() / max(max_count, 1) * 20)
            bar = '#' * bar_len
            print(f'      {d}: {bar:<20} ({int(counts[d].item()):>3})')
        print()

    # ── 잠재 공간 분석 ──
    print(f'\n[8] Latent space analysis...')
    print('    Encoding full test set...\n')

    model.eval()
    all_mu_c = []
    all_mu_s = []
    all_tension_c = []
    all_tension_s = []
    all_labels = []

    with torch.no_grad():
        for X_batch, y_batch in test_loader:
            X_batch = X_batch.view(X_batch.size(0), -1)
            mu_c, _, mu_s, _, t_c, t_s = model.encode(X_batch)
            all_mu_c.append(mu_c)
            all_mu_s.append(mu_s)
            all_tension_c.append(t_c)
            all_tension_s.append(t_s)
            all_labels.append(y_batch)

    all_mu_c = torch.cat(all_mu_c, dim=0)
    all_mu_s = torch.cat(all_mu_s, dim=0)
    all_tension_c = torch.cat(all_tension_c, dim=0).squeeze()
    all_tension_s = torch.cat(all_tension_s, dim=0).squeeze()
    all_labels = torch.cat(all_labels, dim=0)

    # 숫자별 평균 장력
    print('    Per-digit average tension:')
    print(f'    {"Digit":>5}  {"T_content":>10}  {"T_structure":>12}  {"Total":>8}')
    print(f'    {"-"*5}  {"-"*10}  {"-"*12}  {"-"*8}')

    digit_tensions = {}
    for d in range(10):
        mask = all_labels == d
        tc = all_tension_c[mask].mean().item()
        ts = all_tension_s[mask].mean().item()
        total = tc + ts
        digit_tensions[d] = (tc, ts, total)
        print(f'    {d:>5}  {tc:>10.2f}  {ts:>12.2f}  {total:>8.2f}')

    # 가장 높은/낮은 장력 숫자
    sorted_by_total = sorted(digit_tensions.items(), key=lambda x: x[1][2])
    print(f'\n    Lowest tension  (easiest): digit {sorted_by_total[0][0]} '
          f'(T={sorted_by_total[0][1][2]:.2f})')
    print(f'    Highest tension (hardest): digit {sorted_by_total[-1][0]} '
          f'(T={sorted_by_total[-1][1][2]:.2f})')

    # 숫자간 잠재 공간 거리 (내용 vs 구조)
    print(f'\n    Inter-digit distances (content axis):')
    centroids_c = torch.zeros(10, latent_dim)
    centroids_s = torch.zeros(10, latent_dim)
    for d in range(10):
        mask = all_labels == d
        centroids_c[d] = all_mu_c[mask].mean(dim=0)
        centroids_s[d] = all_mu_s[mask].mean(dim=0)

    # 가장 가까운/먼 숫자 쌍 (내용 축)
    min_dist_c = float('inf')
    max_dist_c = 0
    closest_c = (0, 0)
    farthest_c = (0, 0)

    for i in range(10):
        for j in range(i + 1, 10):
            dist = (centroids_c[i] - centroids_c[j]).pow(2).sum().sqrt().item()
            if dist < min_dist_c:
                min_dist_c = dist
                closest_c = (i, j)
            if dist > max_dist_c:
                max_dist_c = dist
                farthest_c = (i, j)

    print(f'    Closest  (content): {closest_c[0]} <-> {closest_c[1]}  '
          f'(dist={min_dist_c:.2f})')
    print(f'    Farthest (content): {farthest_c[0]} <-> {farthest_c[1]}  '
          f'(dist={max_dist_c:.2f})')

    # 구조 축
    min_dist_s = float('inf')
    max_dist_s = 0
    closest_s = (0, 0)
    farthest_s = (0, 0)

    for i in range(10):
        for j in range(i + 1, 10):
            dist = (centroids_s[i] - centroids_s[j]).pow(2).sum().sqrt().item()
            if dist < min_dist_s:
                min_dist_s = dist
                closest_s = (i, j)
            if dist > max_dist_s:
                max_dist_s = dist
                farthest_s = (i, j)

    print(f'    Closest  (structure): {closest_s[0]} <-> {closest_s[1]}  '
          f'(dist={min_dist_s:.2f})')
    print(f'    Farthest (structure): {farthest_s[0]} <-> {farthest_s[1]}  '
          f'(dist={max_dist_s:.2f})')

    # ── 학습 곡선 ──
    print(f'\n[9] Training curve (ASCII):')
    recon_losses = history['recon_loss']
    kl_losses = history['kl_loss']

    max_val = max(recon_losses)
    chart_height = 10
    chart_width = len(recon_losses)

    print(f'\n    Reconstruction loss:')
    for row in range(chart_height, 0, -1):
        threshold = max_val * row / chart_height
        line = '    '
        if row == chart_height:
            line += f'{max_val:>6.1f} |'
        elif row == 1:
            line += f'{max_val/chart_height:>6.1f} |'
        else:
            line += '       |'
        for epoch in range(chart_width):
            if recon_losses[epoch] >= threshold:
                line += '#'
            else:
                line += ' '
        print(line)
    print(f'       +{"=" * chart_width}')
    print(f'        {"Epoch 1":<{chart_width//2}}{"Epoch " + str(chart_width):>{chart_width//2}}')

    # ── 요약 ──
    print(f'\n{"=" * 65}')
    print(f'   Summary')
    print(f'{"=" * 65}')
    print(f'   Parameters:          {n_params:,}')
    print(f'   Final recon loss:    {history["recon_loss"][-1]:.2f}')
    print(f'   Final KL loss:       {history["kl_loss"][-1]:.2f}')
    print(f'   Tension scale:       {model.tension_scale.item():.4f} (1/3={1/3:.4f})')
    print(f'   Content tension:     {history["tension_content"][-1]:.2f}')
    print(f'   Structure tension:   {history["tension_structure"][-1]:.2f}')
    print(f'')
    print(f'   Key insight: the repulsion field between engines')
    print(f'   forms a structured latent space where:')
    print(f'     Content axis (A vs G) = WHAT to generate')
    print(f'     Structure axis (E vs F) = HOW to generate it')
    print(f'     Tension = creativity control')
    print(f'{"=" * 65}')
    print()


if __name__ == '__main__':
    main()
