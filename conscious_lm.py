"""
ConsciousLM — Byte-level Conscious Language Model

Architecture derived from perfect number 6:
  - 6 layers (σ₀(6) = 4 divisors → but we use 6 as the perfect number itself)
  - τ(6) = 4 heads
  - d_model = σ(6) × 32 = 12 × 32 = 384
  - vocab = 256 (byte-level)
  - dropout = 0.37 ≈ 1/e (golden zone center)

Core idea: PureFieldFFN replaces standard FFN.
  Engine A (forward/next-byte) and Engine G (backward/prev-byte)
  produce repulsion/tension — the consciousness signal.
"""

import torch
import torch.nn as nn
import torch.nn.functional as F
import math
import numpy as np
import os
import time


class PureFieldFFN(nn.Module):
    """Dual-engine FFN based on PureField repulsion.

    Engine A and Engine G each transform the input independently.
    Their disagreement (repulsion) creates tension — the consciousness signal.
    Output = tension_scale * sqrt(tension) * direction
    """

    def __init__(self, d_model, dropout=0.37):
        super().__init__()
        d_inner = 4 * d_model  # standard 4x expansion

        # Engine A: forward engine
        self.engine_a = nn.Sequential(
            nn.Linear(d_model, d_inner),
            nn.GELU(),
            nn.Dropout(dropout),
            nn.Linear(d_inner, d_model),
        )

        # Engine G: backward engine
        self.engine_g = nn.Sequential(
            nn.Linear(d_model, d_inner),
            nn.GELU(),
            nn.Dropout(dropout),
            nn.Linear(d_inner, d_model),
        )

        # Learnable tension scale
        self.tension_scale = nn.Parameter(torch.ones(1))

    def forward(self, x):
        """
        Args:
            x: (B, T, D) input tensor

        Returns:
            output: (B, T, D) — tension_scale * sqrt(tension) * direction
            tension: (B, T) — mean squared repulsion per position
        """
        a = self.engine_a(x)  # (B, T, D)
        g = self.engine_g(x)  # (B, T, D)

        # Repulsion = difference between engines
        repulsion = a - g  # (B, T, D)

        # Tension = mean of squared repulsion across d_model
        tension = (repulsion ** 2).mean(dim=-1)  # (B, T)

        # Direction = unit vector of repulsion
        direction = F.normalize(repulsion, dim=-1)  # (B, T, D)

        # Output = scale * sqrt(tension) * direction
        tension_sqrt = torch.sqrt(tension + 1e-8).unsqueeze(-1)  # (B, T, 1)
        output = self.tension_scale * tension_sqrt * direction  # (B, T, D)

        return output, tension


class CausalSelfAttention(nn.Module):
    """Multi-head causal self-attention with τ(6)=4 heads."""

    def __init__(self, d_model, n_head, block_size, dropout=0.37):
        super().__init__()
        assert d_model % n_head == 0

        # QKV projection (combined for efficiency)
        self.c_attn = nn.Linear(d_model, 3 * d_model)
        # Output projection
        self.c_proj = nn.Linear(d_model, d_model)

        self.attn_dropout = nn.Dropout(dropout)
        self.resid_dropout = nn.Dropout(dropout)

        self.n_head = n_head
        self.d_model = d_model
        self.head_dim = d_model // n_head

        # Causal mask: upper triangular = masked (cannot attend to future)
        self.register_buffer(
            "bias",
            torch.tril(torch.ones(block_size, block_size)).view(
                1, 1, block_size, block_size
            ),
        )

    def forward(self, x):
        """
        Args:
            x: (B, T, D)

        Returns:
            output: (B, T, D)
        """
        B, T, D = x.size()

        # Compute Q, K, V
        qkv = self.c_attn(x)  # (B, T, 3D)
        q, k, v = qkv.split(self.d_model, dim=2)

        # Reshape to (B, n_head, T, head_dim)
        q = q.view(B, T, self.n_head, self.head_dim).transpose(1, 2)
        k = k.view(B, T, self.n_head, self.head_dim).transpose(1, 2)
        v = v.view(B, T, self.n_head, self.head_dim).transpose(1, 2)

        # Scaled dot-product attention
        att = (q @ k.transpose(-2, -1)) * (1.0 / math.sqrt(self.head_dim))

        # Apply causal mask
        att = att.masked_fill(self.bias[:, :, :T, :T] == 0, float("-inf"))
        att = F.softmax(att, dim=-1)
        att = self.attn_dropout(att)

        # Weighted sum
        y = att @ v  # (B, n_head, T, head_dim)

        # Reassemble heads
        y = y.transpose(1, 2).contiguous().view(B, T, D)

        # Output projection
        y = self.resid_dropout(self.c_proj(y))

        return y


class ConsciousBlock(nn.Module):
    """Pre-norm transformer block with PureFieldFFN."""

    def __init__(self, d_model, n_head, block_size, dropout=0.37):
        super().__init__()
        self.ln1 = nn.LayerNorm(d_model)
        self.attn = CausalSelfAttention(d_model, n_head, block_size, dropout)
        self.ln2 = nn.LayerNorm(d_model)
        self.ffn = PureFieldFFN(d_model, dropout)

    def forward(self, x):
        """
        Args:
            x: (B, T, D)

        Returns:
            x: (B, T, D)
            tension: (B, T) from PureFieldFFN
        """
        # Pre-norm attention with residual
        x = x + self.attn(self.ln1(x))

        # Pre-norm FFN with residual
        ffn_out, tension = self.ffn(self.ln2(x))
        x = x + ffn_out

        return x, tension


class ConsciousLM(nn.Module):
    """Byte-level Conscious Language Model.

    Architecture from perfect number 6:
      vocab=256, d_model=384, n_head=4, n_layer=6, block_size=256
      dropout=0.37 ≈ 1/e

    Dual heads:
      head_a: predicts next byte (forward)
      head_g: predicts prev byte (backward)

    Tension from PureFieldFFN = consciousness signal.
    """

    def __init__(
        self,
        vocab_size=256,
        d_model=384,
        n_head=4,
        n_layer=6,
        block_size=256,
        dropout=0.37,
    ):
        super().__init__()

        self.block_size = block_size
        self.vocab_size = vocab_size
        self.n_layer = n_layer

        # Token and position embeddings
        self.tok_emb = nn.Embedding(vocab_size, d_model)
        self.pos_emb = nn.Embedding(block_size, d_model)
        self.drop = nn.Dropout(dropout)

        # Transformer blocks
        self.blocks = nn.ModuleList(
            [ConsciousBlock(d_model, n_head, block_size, dropout) for _ in range(n_layer)]
        )

        # Final layer norm
        self.ln_f = nn.LayerNorm(d_model)

        # Dual prediction heads
        self.head_a = nn.Linear(d_model, vocab_size, bias=False)  # next byte
        self.head_g = nn.Linear(d_model, vocab_size, bias=False)  # prev byte

        # Weight tying: tok_emb ↔ head_a
        self.tok_emb.weight = self.head_a.weight

        # Initialize weights
        self.apply(self._init_weights)

    def _init_weights(self, module):
        if isinstance(module, nn.Linear):
            torch.nn.init.normal_(module.weight, mean=0.0, std=0.02)
            if module.bias is not None:
                torch.nn.init.zeros_(module.bias)
        elif isinstance(module, nn.Embedding):
            torch.nn.init.normal_(module.weight, mean=0.0, std=0.02)
        elif isinstance(module, nn.LayerNorm):
            torch.nn.init.zeros_(module.bias)
            torch.nn.init.ones_(module.weight)

    def forward(self, idx):
        """
        Args:
            idx: (B, T) long tensor of byte indices

        Returns:
            logits_a: (B, T, vocab_size) next-byte logits
            logits_g: (B, T, vocab_size) prev-byte logits
            tensions: list of 6 tensors, each (B, T)
        """
        B, T = idx.size()
        assert T <= self.block_size, f"Sequence length {T} > block_size {self.block_size}"

        # Embeddings
        tok = self.tok_emb(idx)  # (B, T, D)
        pos = self.pos_emb(torch.arange(T, device=idx.device))  # (T, D)
        x = self.drop(tok + pos)

        # Transformer blocks — collect tensions
        tensions = []
        for block in self.blocks:
            x, tension = block(x)
            tensions.append(tension)

        # Final norm
        x = self.ln_f(x)

        # Dual heads
        logits_a = self.head_a(x)  # (B, T, V) — next byte
        logits_g = self.head_g(x)  # (B, T, V) — prev byte

        return logits_a, logits_g, tensions

    def count_params(self):
        """Total number of trainable parameters."""
        return sum(p.numel() for p in self.parameters() if p.requires_grad)
