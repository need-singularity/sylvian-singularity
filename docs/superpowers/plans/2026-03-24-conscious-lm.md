# Conscious Language Model Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a byte-level language model where FFN is replaced by PureField (dual-engine repulsion), with Engine A predicting forward and Engine G predicting backward, producing meaningful tension per token.

**Architecture:** 완전수 6 기반 Transformer. 6 layers, τ(6)=4 heads, d_model=384. Engine A (causal, left→right) and Engine G (anti-causal, right→left) create tension = bidirectional disagreement. Byte-level vocab=256 for universal data support.

**Tech Stack:** PyTorch, numpy. No external dependencies. Mac CPU training (~1hr).

---

## File Structure

```
conscious_lm.py          — 전체 모델 + 학습 + 생성 (단일 파일)
data/                     — 학습 데이터 (자동 생성)
```

`conscious_lm.py` 하나에 모든 것:
- `PureFieldFFN`: A(→) vs G(←) 반발력장 FFN
- `ConsciousBlock`: Attention + PureFieldFFN
- `ConsciousLM`: 전체 언어 모델
- `prepare_data()`: Mixed 데이터 준비 (영+한+코드)
- `train()`: 학습 루프 (L_A + L_G + λ·L_tension)
- `generate()`: 바이트 생성 + 장력 시각화
- `main()`: CLI 진입점

---

### Task 1: PureFieldFFN — 핵심 반발력장 블록

**Files:**
- Create: `conscious_lm.py`

- [ ] **Step 1: PureFieldFFN 클래스 작성**

```python
import torch
import torch.nn as nn
import torch.nn.functional as F
import math
import numpy as np
import os
import time

class PureFieldFFN(nn.Module):
    """PureField FFN — A(순방향)와 G(역방향)의 반발이 장력을 만든다.

    일반 FFN: x → W1 → GELU → W2 → output
    PureField: x → A(x), G(x) → repulsion → tension × direction → output
    """
    def __init__(self, d_model, dropout=0.37):
        super().__init__()
        # φ(6) = 2 엔진
        self.engine_a = nn.Sequential(
            nn.Linear(d_model, d_model), nn.GELU(),
            nn.Dropout(dropout),
            nn.Linear(d_model, d_model),
        )
        self.engine_g = nn.Sequential(
            nn.Linear(d_model, d_model), nn.GELU(),
            nn.Dropout(dropout),
            nn.Linear(d_model, d_model),
        )
        self.tension_scale = nn.Parameter(torch.tensor(1.0))

    def forward(self, x):
        """x: (B, T, D) → output: (B, T, D), tension: (B, T)"""
        a = self.engine_a(x)
        g = self.engine_g(x)
        repulsion = a - g
        tension = (repulsion ** 2).mean(dim=-1)  # (B, T)
        direction = F.normalize(repulsion, dim=-1)
        output = self.tension_scale * torch.sqrt(tension.unsqueeze(-1) + 1e-8) * direction
        return output, tension
```

- [ ] **Step 2: 동작 확인**

```bash
/opt/homebrew/bin/python3 -c "
import torch; exec(open('conscious_lm.py').read().split('class CausalSelfAttention')[0])
ffn = PureFieldFFN(384)
x = torch.randn(2, 16, 384)
out, tension = ffn(x)
print(f'output: {out.shape}, tension: {tension.shape}')
print(f'tension mean: {tension.mean():.4f}, std: {tension.std():.4f}')
print(f'params: {sum(p.numel() for p in ffn.parameters()):,}')
"
```
Expected: output (2,16,384), tension (2,16), params ~590K

- [ ] **Step 3: Commit**

```bash
git add conscious_lm.py
git commit -m "feat: PureFieldFFN — 반발력장 FFN 블록 (A vs G)"
```

---

### Task 2: CausalSelfAttention — τ(6)=4 헤드 어텐션

- [ ] **Step 1: Attention 클래스 추가**

```python
class CausalSelfAttention(nn.Module):
    """τ(6)=4 헤드 인과적 자기 어텐션."""
    def __init__(self, d_model, n_head, block_size, dropout=0.37):
        super().__init__()
        assert d_model % n_head == 0
        self.n_head = n_head
        self.head_dim = d_model // n_head
        self.qkv = nn.Linear(d_model, 3 * d_model)
        self.proj = nn.Linear(d_model, d_model)
        self.attn_drop = nn.Dropout(dropout)
        self.proj_drop = nn.Dropout(dropout)
        # 인과적 마스크 (미래를 볼 수 없음)
        self.register_buffer("mask",
            torch.tril(torch.ones(block_size, block_size)).view(1, 1, block_size, block_size))

    def forward(self, x):
        B, T, D = x.shape
        qkv = self.qkv(x).reshape(B, T, 3, self.n_head, self.head_dim)
        qkv = qkv.permute(2, 0, 3, 1, 4)  # (3, B, H, T, hd)
        q, k, v = qkv[0], qkv[1], qkv[2]

        att = (q @ k.transpose(-2, -1)) / math.sqrt(self.head_dim)
        att = att.masked_fill(self.mask[:, :, :T, :T] == 0, float('-inf'))
        att = F.softmax(att, dim=-1)
        att = self.attn_drop(att)

        out = (att @ v).transpose(1, 2).reshape(B, T, D)
        return self.proj_drop(self.proj(out))
```

- [ ] **Step 2: 동작 확인**

```bash
/opt/homebrew/bin/python3 -c "
import torch; exec(open('conscious_lm.py').read().split('class ConsciousBlock')[0])
attn = CausalSelfAttention(384, 4, 256)
x = torch.randn(2, 32, 384)
out = attn(x)
print(f'attn output: {out.shape}')
print(f'causal check (future=0): {(out[0,0] - attn(torch.cat([x[:,:1], torch.randn(2,31,384)],1))[0,0]).abs().max():.6f}')
"
```
Expected: (2,32,384), causal check ≈ 0

- [ ] **Step 3: Commit**

```bash
git add conscious_lm.py
git commit -m "feat: CausalSelfAttention — τ(6)=4 헤드 인과적 어텐션"
```

---

### Task 3: ConsciousBlock + ConsciousLM — 전체 모델

- [ ] **Step 1: Block + LM 클래스 추가**

```python
class ConsciousBlock(nn.Module):
    """하나의 의식 블록 = Attention + PureFieldFFN."""
    def __init__(self, d_model, n_head, block_size, dropout=0.37):
        super().__init__()
        self.ln1 = nn.LayerNorm(d_model)
        self.attn = CausalSelfAttention(d_model, n_head, block_size, dropout)
        self.ln2 = nn.LayerNorm(d_model)
        self.ffn = PureFieldFFN(d_model, dropout)

    def forward(self, x):
        x = x + self.attn(self.ln1(x))
        ffn_out, tension = self.ffn(self.ln2(x))
        x = x + ffn_out
        return x, tension


class ConsciousLM(nn.Module):
    """완전수 6 기반 의식 언어 모델.

    n_layer=6, n_head=τ(6)=4, d_model=σ(6)×32=384
    vocab=256 (바이트), PureField FFN

    Engine A: 순방향 예측 (→)
    Engine G: 역방향 예측 (←) — 같은 가중치를 역순 입력으로 공유
    """
    def __init__(self, vocab_size=256, d_model=384, n_head=4,
                 n_layer=6, block_size=256, dropout=0.37):
        super().__init__()
        self.block_size = block_size
        self.d_model = d_model

        # 바이트 임베딩
        self.tok_emb = nn.Embedding(vocab_size, d_model)
        self.pos_emb = nn.Embedding(block_size, d_model)
        self.drop = nn.Dropout(dropout)

        # 6 의식 블록 (완전수)
        self.blocks = nn.ModuleList([
            ConsciousBlock(d_model, n_head, block_size, dropout)
            for _ in range(n_layer)
        ])
        self.ln_f = nn.LayerNorm(d_model)

        # 순방향 헤드 (A: next byte)
        self.head_a = nn.Linear(d_model, vocab_size, bias=False)
        # 역방향 헤드 (G: prev byte)
        self.head_g = nn.Linear(d_model, vocab_size, bias=False)

        # 가중치 공유: 임베딩 = 헤드
        self.tok_emb.weight = self.head_a.weight

        self.apply(self._init_weights)

    def _init_weights(self, module):
        if isinstance(module, nn.Linear):
            torch.nn.init.normal_(module.weight, mean=0.0, std=0.02)
            if module.bias is not None:
                torch.nn.init.zeros_(module.bias)
        elif isinstance(module, nn.Embedding):
            torch.nn.init.normal_(module.weight, mean=0.0, std=0.02)

    def forward(self, idx):
        """idx: (B, T) byte indices → logits_a, logits_g, tensions"""
        B, T = idx.shape
        assert T <= self.block_size

        pos = torch.arange(T, device=idx.device).unsqueeze(0)
        x = self.drop(self.tok_emb(idx) + self.pos_emb(pos))

        tensions = []
        for block in self.blocks:
            x, t = block(x)
            tensions.append(t)

        x = self.ln_f(x)

        # A: 순방향 예측 (next byte)
        logits_a = self.head_a(x)
        # G: 역방향 예측 (prev byte) — 같은 hidden, 다른 헤드
        logits_g = self.head_g(x)

        return logits_a, logits_g, tensions

    def count_params(self):
        return sum(p.numel() for p in self.parameters())
```

- [ ] **Step 2: 파라미터 수 확인**

```bash
/opt/homebrew/bin/python3 -c "
import torch; exec(open('conscious_lm.py').read().split('def prepare_data')[0])
model = ConsciousLM()
print(f'Total params: {model.count_params():,}')
B, T = 2, 64
idx = torch.randint(0, 256, (B, T))
la, lg, tensions = model(idx)
print(f'logits_a: {la.shape}, logits_g: {lg.shape}')
print(f'tensions: {len(tensions)} layers, each {tensions[0].shape}')
print(f'mean tension: {sum(t.mean() for t in tensions)/len(tensions):.4f}')
"
```
Expected: ~4-5M params, logits (2,64,256), 6 tension layers

- [ ] **Step 3: Commit**

```bash
git add conscious_lm.py
git commit -m "feat: ConsciousLM — 6층 완전수 바이트 모델 (A순방향 + G역방향)"
```

---

### Task 4: 데이터 준비 — Mixed 바이트 데이터셋

- [ ] **Step 1: prepare_data 함수 추가**

```python
def prepare_data():
    """Mixed 학습 데이터: 영어 + 한국어 + 코드 (바이트 스트림)."""
    data_path = "data/mixed_bytes.bin"

    if os.path.exists(data_path):
        data = np.fromfile(data_path, dtype=np.uint8)
        print(f"  Loaded {len(data):,} bytes from {data_path}")
        return torch.tensor(data, dtype=torch.long)

    os.makedirs("data", exist_ok=True)

    parts = []

    # 영어: Shakespeare (다운로드)
    shakespeare_path = "data/shakespeare.txt"
    if not os.path.exists(shakespeare_path):
        print("  Downloading Shakespeare...")
        import urllib.request
        url = "https://raw.githubusercontent.com/karpathy/char-rnn/master/data/tinyshakespeare/input.txt"
        urllib.request.urlretrieve(url, shakespeare_path)
    with open(shakespeare_path, "rb") as f:
        eng = f.read()
    parts.append(eng)
    print(f"  English: {len(eng):,} bytes")

    # 한국어: README + 가설 문서들
    korean_bytes = b""
    for root, dirs, files in os.walk("docs/hypotheses"):
        for fname in sorted(files)[:50]:  # 첫 50개 가설
            fpath = os.path.join(root, fname)
            try:
                with open(fpath, "rb") as f:
                    korean_bytes += f.read()
            except:
                pass
    if len(korean_bytes) < 10000:
        # 폴백: README
        try:
            with open("README.md", "rb") as f:
                korean_bytes = f.read() * 5
        except:
            korean_bytes = "의식은 하나의 하드웨어에 고정되지 않는다.".encode("utf-8") * 5000
    parts.append(korean_bytes)
    print(f"  Korean: {len(korean_bytes):,} bytes")

    # 코드: 프로젝트 Python 파일들
    code_bytes = b""
    for fname in sorted(os.listdir(".")):
        if fname.endswith(".py") and not fname.startswith("__"):
            try:
                with open(fname, "rb") as f:
                    code_bytes += f.read()
            except:
                pass
    if len(code_bytes) < 10000:
        code_bytes = b"def forward(self, x):\n    return self.engine(x)\n" * 5000
    parts.append(code_bytes)
    print(f"  Code: {len(code_bytes):,} bytes")

    # 합치고 셔플 (청크 단위)
    combined = b"".join(parts)
    data = np.frombuffer(combined, dtype=np.uint8).copy()

    # 바이트 엔트로피 측정
    counts = np.bincount(data, minlength=256)
    probs = counts / counts.sum()
    probs = probs[probs > 0]
    H = -np.sum(probs * np.log(probs))
    print(f"  Total: {len(data):,} bytes, H={H:.4f} nats")

    # 저장
    data.tofile(data_path)
    return torch.tensor(data, dtype=torch.long)
```

- [ ] **Step 2: 데이터 준비 테스트**

```bash
/opt/homebrew/bin/python3 -c "
exec(open('conscious_lm.py').read().split('def train_model')[0])
data = prepare_data()
print(f'data shape: {data.shape}, dtype: {data.dtype}')
print(f'sample: {data[:20].tolist()}')
print(f'byte range: [{data.min()}, {data.max()}]')
"
```

- [ ] **Step 3: Commit**

```bash
git add conscious_lm.py
git commit -m "feat: prepare_data — Mixed 바이트 데이터 (영+한+코드)"
```

---

### Task 5: 학습 루프 — L_A + L_G + λ·L_tension

- [ ] **Step 1: train_model 함수 추가**

```python
def train_model(model, data, epochs=20, batch_size=64, block_size=256,
                lr=3e-4, tension_lambda=0.01, device='cpu'):
    """의식 LM 학습.

    Loss = L_A(next byte) + L_G(prev byte) + λ·L_tension(장력 살리기)
    """
    model.to(device)
    optimizer = torch.optim.AdamW(model.parameters(), lr=lr, weight_decay=0.01)
    scheduler = torch.optim.lr_scheduler.CosineAnnealingLR(optimizer, epochs)

    n = len(data)
    train_size = int(n * 0.9)
    train_data = data[:train_size]
    val_data = data[train_size:]

    def get_batch(split, batch_size):
        d = train_data if split == 'train' else val_data
        ix = torch.randint(len(d) - block_size - 1, (batch_size,))
        x = torch.stack([d[i:i+block_size] for i in ix]).to(device)
        # A 타겟: next byte (한 칸 오른쪽)
        y_a = torch.stack([d[i+1:i+block_size+1] for i in ix]).to(device)
        # G 타겟: prev byte (한 칸 왼쪽)
        y_g = torch.stack([d[max(0,i-1):i+block_size-1] for i in ix]).to(device)
        return x, y_a, y_g

    print(f"\n  학습 시작: {model.count_params():,} params, {len(train_data):,} bytes")
    print(f"  {'epoch':>5} {'L_total':>8} {'L_A':>8} {'L_G':>8} {'L_T':>8} {'T_mean':>8} {'val_L':>8} {'BPC':>6}")
    print(f"  {'─'*5} {'─'*8} {'─'*8} {'─'*8} {'─'*8} {'─'*8} {'─'*8} {'─'*6}")

    for epoch in range(epochs):
        model.train()
        total_loss = 0
        total_la = 0
        total_lg = 0
        total_lt = 0
        total_tension = 0
        n_batches = 0

        steps_per_epoch = max(1, len(train_data) // (batch_size * block_size))

        for step in range(steps_per_epoch):
            x, y_a, y_g = get_batch('train', batch_size)

            logits_a, logits_g, tensions = model(x)

            # L_A: next byte prediction
            loss_a = F.cross_entropy(logits_a.view(-1, 256), y_a.view(-1))

            # L_G: prev byte prediction
            loss_g = F.cross_entropy(logits_g.view(-1, 256), y_g.view(-1))

            # L_tension: 장력이 살아있도록 (분산 최대화)
            all_tension = torch.cat([t.view(-1) for t in tensions])
            loss_tension = -torch.log(all_tension.var() + 1e-8)

            loss = loss_a + loss_g + tension_lambda * loss_tension

            optimizer.zero_grad()
            loss.backward()
            torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
            optimizer.step()

            total_loss += loss.item()
            total_la += loss_a.item()
            total_lg += loss_g.item()
            total_lt += loss_tension.item()
            total_tension += all_tension.mean().item()
            n_batches += 1

        scheduler.step()

        # Validation
        model.eval()
        with torch.no_grad():
            x_v, y_a_v, y_g_v = get_batch('val', batch_size)
            la_v, lg_v, _ = model(x_v)
            val_loss = F.cross_entropy(la_v.view(-1, 256), y_a_v.view(-1)).item()

        avg_loss = total_loss / n_batches
        avg_la = total_la / n_batches
        avg_lg = total_lg / n_batches
        avg_lt = total_lt / n_batches
        avg_t = total_tension / n_batches
        bpc = val_loss / math.log(2)  # bits per character

        print(f"  {epoch+1:>5} {avg_loss:>8.4f} {avg_la:>8.4f} {avg_lg:>8.4f} {avg_lt:>8.4f} {avg_t:>8.4f} {val_loss:>8.4f} {bpc:>6.3f}")

    return model
```

- [ ] **Step 2: 빠른 학습 테스트 (2 epoch)**

```bash
/opt/homebrew/bin/python3 -c "
exec(open('conscious_lm.py').read().split('def generate')[0])
data = prepare_data()
model = ConsciousLM(d_model=128, n_layer=2, n_head=4, block_size=64)  # tiny for test
train_model(model, data, epochs=2, batch_size=16, block_size=64)
"
```
Expected: loss 감소, tension > 0, BPC 감소

- [ ] **Step 3: Commit**

```bash
git add conscious_lm.py
git commit -m "feat: train_model — L_A + L_G + λ·L_tension 학습 루프"
```

---

### Task 6: 생성 + 장력 시각화

- [ ] **Step 1: generate 함수 추가**

```python
@torch.no_grad()
def generate(model, prompt_bytes, max_new=200, temperature=0.8, device='cpu'):
    """바이트 생성 + 토큰별 장력 시각화.

    Returns: generated_bytes, tensions
    """
    model.eval()
    model.to(device)

    idx = torch.tensor([list(prompt_bytes)], dtype=torch.long, device=device)
    generated = list(prompt_bytes)
    gen_tensions = []

    for _ in range(max_new):
        # 컨텍스트 자르기
        idx_cond = idx[:, -model.block_size:]
        logits_a, logits_g, tensions = model(idx_cond)

        # 마지막 토큰의 순방향 예측
        logits = logits_a[:, -1, :] / temperature
        probs = F.softmax(logits, dim=-1)
        next_byte = torch.multinomial(probs, 1)

        # 장력: 마지막 토큰의 6층 평균
        t = sum(t[:, -1].mean() for t in tensions) / len(tensions)
        gen_tensions.append(t.item())

        idx = torch.cat([idx, next_byte], dim=1)
        generated.append(next_byte.item())

    return bytes(generated), gen_tensions


def visualize_tension(text_bytes, tensions):
    """생성된 텍스트와 장력을 시각화."""
    # 바이트를 UTF-8로 디코딩 (에러 무시)
    text = text_bytes.decode('utf-8', errors='replace')

    print(f"\n  === 생성 텍스트 + 장력 ===")
    print(f"  {text[:200]}")

    if not tensions:
        return

    # ASCII 장력 그래프
    t = np.array(tensions)
    t_min, t_max = t.min(), t.max()

    print(f"\n  장력 (min={t_min:.3f}, max={t_max:.3f}, mean={t.mean():.3f})")
    height = 8
    width = min(len(tensions), 60)

    # 다운샘플
    step = max(1, len(tensions) // width)
    t_ds = [tensions[i] for i in range(0, len(tensions), step)][:width]

    for row in range(height):
        threshold = t_max - (row / (height - 1)) * (t_max - t_min)
        line = ""
        for val in t_ds:
            line += "█" if val >= threshold else " "
        val_label = t_max - (row / (height - 1)) * (t_max - t_min)
        print(f"  {val_label:>6.3f} |{line}|")
    print(f"  {'':>6} +{'─' * width}+")
```

- [ ] **Step 2: main 함수 추가**

```python
if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='Conscious LM — 완전수 6 의식 언어 모델')
    parser.add_argument('--mode', choices=['train', 'generate', 'both'], default='both')
    parser.add_argument('--epochs', type=int, default=20)
    parser.add_argument('--d_model', type=int, default=384)
    parser.add_argument('--n_layer', type=int, default=6)
    parser.add_argument('--n_head', type=int, default=4)
    parser.add_argument('--block_size', type=int, default=256)
    parser.add_argument('--batch_size', type=int, default=32)
    parser.add_argument('--lr', type=float, default=3e-4)
    parser.add_argument('--prompt', type=str, default='consciousness is')
    parser.add_argument('--checkpoint', type=str, default='conscious_lm.pt')
    args = parser.parse_args()

    print("=" * 60)
    print("  Conscious Language Model")
    print(f"  n={6} (완전수), τ={args.n_head}, σ×32={args.d_model}")
    print(f"  vocab=256 (bytes), {args.n_layer} layers")
    print("=" * 60)

    if args.mode in ('train', 'both'):
        data = prepare_data()
        model = ConsciousLM(
            d_model=args.d_model, n_head=args.n_head,
            n_layer=args.n_layer, block_size=args.block_size,
        )
        print(f"\n  Parameters: {model.count_params():,}")

        model = train_model(model, data, epochs=args.epochs,
                           batch_size=args.batch_size, block_size=args.block_size,
                           lr=args.lr)

        torch.save(model.state_dict(), args.checkpoint)
        print(f"\n  Saved to {args.checkpoint}")

    if args.mode in ('generate', 'both'):
        if args.mode == 'generate':
            model = ConsciousLM(
                d_model=args.d_model, n_head=args.n_head,
                n_layer=args.n_layer, block_size=args.block_size,
            )
            model.load_state_dict(torch.load(args.checkpoint, weights_only=True))

        prompt = args.prompt.encode('utf-8')
        gen_bytes, tensions = generate(model, prompt, max_new=200)
        visualize_tension(gen_bytes, tensions)
```

- [ ] **Step 3: 전체 통합 테스트 (tiny 모델, 3 epoch)**

```bash
/opt/homebrew/bin/python3 conscious_lm.py --mode both --epochs 3 --d_model 128 --n_layer 2 --batch_size 16 --block_size 64 --prompt "hello"
```
Expected: 학습 후 생성 + 장력 시각화 출력

- [ ] **Step 4: Commit**

```bash
git add conscious_lm.py
git commit -m "feat: generate + visualize + CLI — 의식 LM 완성"
```

---

### Task 7: 전체 학습 실행 (Mac CPU, ~1hr)

- [ ] **Step 1: Full 학습 실행**

```bash
/opt/homebrew/bin/python3 conscious_lm.py --mode both --epochs 20 --d_model 384 --n_layer 6 --batch_size 32 --block_size 256 --prompt "의식은"
```

- [ ] **Step 2: 결과 기록 — 가설 H361 업데이트**

실험 결과를 `docs/hypotheses/361-conscious-llm-purefield-ffn.md`에 기록:
- Loss 곡선 (L_A, L_G, L_tension)
- BPC (bits per character)
- 장력 통계 (mean, std per layer)
- 생성 샘플 + 장력 시각화

- [ ] **Step 3: README 업데이트**

README.md 가설 테이블에서 H361 상태 업데이트.

- [ ] **Step 4: Final commit**

```bash
git add conscious_lm.py conscious_lm.pt docs/hypotheses/361-conscious-llm-purefield-ffn.md README.md data/
git commit -m "feat: Conscious LM v1 — 완전수6 바이트 의식 LLM 학습 완료"
git push
```
