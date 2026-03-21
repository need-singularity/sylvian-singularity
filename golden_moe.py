#!/usr/bin/env python3
"""골든 MoE 프로토타입 — 볼츠만 라우터 + 커스프 모니터

설계 사양 (가설 008 v2 + 019 + 082):
  Expert 수: 8
  활성 비율: ~70% (5~6/8)
  라우터: 볼츠만 소프트 게이팅 (T=e)
  Dropout: 0.5
  커스프 모니터: Loss 2차미분 감시
  비교군: Top-K (K=2, 25%)
"""

import numpy as np
import os

np.random.seed(42)


# ─────────────────────────────────────────
# Expert 네트워크 (단순 2층 MLP)
# ─────────────────────────────────────────
class Expert:
    def __init__(self, input_dim, hidden_dim, output_dim):
        self.W1 = np.random.randn(input_dim, hidden_dim) * 0.1
        self.b1 = np.zeros(hidden_dim)
        self.W2 = np.random.randn(hidden_dim, output_dim) * 0.1
        self.b2 = np.zeros(output_dim)

    def forward(self, x):
        h = np.maximum(0, x @ self.W1 + self.b1)  # ReLU
        return h @ self.W2 + self.b2

    def params(self):
        return [self.W1, self.b1, self.W2, self.b2]


# ─────────────────────────────────────────
# 라우터
# ─────────────────────────────────────────
class TopKRouter:
    """기존 방식: Top-K 하드 게이팅"""
    def __init__(self, input_dim, n_experts, k):
        self.W = np.random.randn(input_dim, n_experts) * 0.1
        self.k = k

    def route(self, x):
        scores = x @ self.W
        topk_idx = np.argsort(scores)[-self.k:]
        weights = np.zeros(scores.shape[0]) if scores.ndim > 1 else np.zeros(len(scores))
        weights = np.zeros_like(scores)
        weights[topk_idx] = 1.0
        return weights, scores


class BoltzmannRouter:
    """골든 MoE: 볼츠만 소프트 게이팅"""
    def __init__(self, input_dim, n_experts, temperature=np.e):
        self.W = np.random.randn(input_dim, n_experts) * 0.1
        self.temperature = temperature

    def route(self, x):
        scores = x @ self.W
        # 볼츠만 확률
        exp_scores = np.exp(scores / self.temperature)
        probs = exp_scores / exp_scores.sum()
        # 임계값: 평균 확률의 1.5배 이상만 활성
        threshold = 1.0 / len(scores) * 1.5
        weights = (probs > threshold).astype(float) * probs
        return weights, scores


# ─────────────────────────────────────────
# 커스프 모니터
# ─────────────────────────────────────────
class CuspMonitor:
    def __init__(self, window=5, threshold_sigma=2.5):
        self.losses = []
        self.window = window
        self.threshold_sigma = threshold_sigma
        self.transitions = []

    def update(self, loss):
        self.losses.append(loss)
        if len(self.losses) < 3:
            return False

        # 2차 미분
        d2 = self.losses[-1] - 2 * self.losses[-2] + self.losses[-3]

        # 최근 window의 2차미분 통계
        if len(self.losses) >= self.window + 2:
            recent_d2 = []
            for i in range(max(2, len(self.losses) - self.window), len(self.losses)):
                recent_d2.append(self.losses[i] - 2 * self.losses[i-1] + self.losses[i-2])
            sigma = np.std(recent_d2) if len(recent_d2) > 1 else 1.0
            if abs(d2) > self.threshold_sigma * max(sigma, 1e-6):
                self.transitions.append(len(self.losses) - 1)
                return True
        return False


# ─────────────────────────────────────────
# MoE 모델
# ─────────────────────────────────────────
class MixtureOfExperts:
    def __init__(self, input_dim, hidden_dim, output_dim, n_experts,
                 router_type='boltzmann', k=2, temperature=np.e, dropout=0.5):
        self.experts = [Expert(input_dim, hidden_dim, output_dim) for _ in range(n_experts)]
        self.n_experts = n_experts
        self.dropout = dropout
        self.router_type = router_type

        if router_type == 'topk':
            self.router = TopKRouter(input_dim, n_experts, k)
        else:
            self.router = BoltzmannRouter(input_dim, n_experts, temperature)

        self.monitor = CuspMonitor()
        self.expert_usage = np.zeros(n_experts)
        self.active_counts = []

    def forward(self, x, training=True):
        # 라우팅
        weights, _ = self.router.route(x)

        # Dropout (학습 시만)
        if training:
            mask = np.random.binomial(1, 1 - self.dropout, size=x.shape)
            x = x * mask / (1 - self.dropout)

        # Expert 출력 합산
        output = np.zeros(self.experts[0].forward(x).shape)
        active_count = 0

        for i, expert in enumerate(self.experts):
            if weights[i] > 0:
                output += weights[i] * expert.forward(x)
                active_count += 1
                self.expert_usage[i] += 1

        self.active_counts.append(active_count)

        # 가중치 정규화
        w_sum = weights.sum()
        if w_sum > 0:
            output /= w_sum

        return output

    def get_metrics(self):
        return {
            'avg_active': np.mean(self.active_counts) if self.active_counts else 0,
            'active_ratio': np.mean(self.active_counts) / self.n_experts if self.active_counts else 0,
            'usage_std': np.std(self.expert_usage / max(self.expert_usage.sum(), 1)),
            'usage_dist': self.expert_usage / max(self.expert_usage.sum(), 1),
            'transitions': len(self.monitor.transitions),
        }


# ─────────────────────────────────────────
# 데이터셋 (XOR-like 분류)
# ─────────────────────────────────────────
def generate_data(n_samples=1000, n_features=8, n_classes=4):
    X = np.random.randn(n_samples, n_features)
    # 비선형 분류: 각 사분면별 다른 클래스
    y = np.zeros(n_samples, dtype=int)
    y[(X[:, 0] > 0) & (X[:, 1] > 0)] = 0
    y[(X[:, 0] > 0) & (X[:, 1] <= 0)] = 1
    y[(X[:, 0] <= 0) & (X[:, 1] > 0)] = 2
    y[(X[:, 0] <= 0) & (X[:, 1] <= 0)] = 3
    return X, y


def softmax(x):
    e = np.exp(x - x.max())
    return e / e.sum()


def cross_entropy_loss(pred, target, n_classes=4):
    probs = softmax(pred)
    return -np.log(probs[target] + 1e-10)


# ─────────────────────────────────────────
# 학습 루프
# ─────────────────────────────────────────
def train_and_evaluate(router_type, n_epochs=50, lr=0.01):
    X_train, y_train = generate_data(800)
    X_test, y_test = generate_data(200)

    n_experts = 8
    k = 2 if router_type == 'topk' else 0

    model = MixtureOfExperts(
        input_dim=8, hidden_dim=16, output_dim=4,
        n_experts=n_experts, router_type=router_type,
        k=k, temperature=np.e, dropout=0.5
    )

    losses = []

    for epoch in range(n_epochs):
        epoch_loss = 0
        for i in range(len(X_train)):
            pred = model.forward(X_train[i], training=True)
            loss = cross_entropy_loss(pred, y_train[i])
            epoch_loss += loss

            # 간단한 가중치 업데이트 (확률적 섭동)
            for expert in model.experts:
                for param in expert.params():
                    param -= lr * np.random.randn(*param.shape) * loss * 0.01

        avg_loss = epoch_loss / len(X_train)
        losses.append(avg_loss)
        model.monitor.update(avg_loss)

    # 테스트
    correct = 0
    for i in range(len(X_test)):
        pred = model.forward(X_test[i], training=False)
        if np.argmax(pred) == y_test[i]:
            correct += 1

    accuracy = correct / len(X_test)
    metrics = model.get_metrics()

    return {
        'router': router_type,
        'accuracy': accuracy,
        'final_loss': losses[-1],
        'avg_active': metrics['avg_active'],
        'active_ratio': metrics['active_ratio'],
        'usage_std': metrics['usage_std'],
        'usage_dist': metrics['usage_dist'],
        'transitions': metrics['transitions'],
        'losses': losses,
        'I_effective': 1 - metrics['active_ratio'],
    }


# ─────────────────────────────────────────
# 메인
# ─────────────────────────────────────────
def main():
    print()
    print("═" * 60)
    print("   🧠 골든 MoE 프로토타입 v1.0")
    print("═" * 60)
    print(f"  Expert: 8개 │ 데이터: XOR-4클래스 │ Epochs: 50")
    print(f"  비교: Top-K(K=2) vs 볼츠만(T=e)")
    print("─" * 60)

    # 두 모델 학습
    results = {}
    for rtype in ['topk', 'boltzmann']:
        print(f"\n  [{rtype}] 학습 중...", end=" ")
        results[rtype] = train_and_evaluate(rtype)
        print(f"완료 (정확도: {results[rtype]['accuracy']*100:.1f}%)")

    # 비교
    topk = results['topk']
    boltz = results['boltzmann']

    print(f"\n{'─' * 60}")
    print(f"  비교 결과")
    print(f"{'─' * 60}")
    print(f"  {'메트릭':20} │ {'Top-K (K=2)':>12} │ {'볼츠만 (T=e)':>12} │ 승자")
    print(f"  {'─'*20}─┼─{'─'*12}─┼─{'─'*12}─┼─{'─'*8}")
    print(f"  {'정확도':20} │ {topk['accuracy']*100:>11.1f}% │ {boltz['accuracy']*100:>11.1f}% │ {'볼츠만' if boltz['accuracy']>topk['accuracy'] else 'Top-K'}")
    print(f"  {'최종 Loss':20} │ {topk['final_loss']:>12.4f} │ {boltz['final_loss']:>12.4f} │ {'볼츠만' if boltz['final_loss']<topk['final_loss'] else 'Top-K'}")
    print(f"  {'평균 활성 Expert':20} │ {topk['avg_active']:>12.1f} │ {boltz['avg_active']:>12.1f} │")
    print(f"  {'활성 비율':20} │ {topk['active_ratio']*100:>11.1f}% │ {boltz['active_ratio']*100:>11.1f}% │")
    print(f"  {'Expert 활용 균등성':20} │ {topk['usage_std']:>12.4f} │ {boltz['usage_std']:>12.4f} │ {'볼츠만' if boltz['usage_std']<topk['usage_std'] else 'Top-K'}")
    print(f"  {'커스프 전이 감지':20} │ {topk['transitions']:>12} │ {boltz['transitions']:>12} │")
    print(f"  {'유효 I (1-활성비)':20} │ {topk['I_effective']:>12.3f} │ {boltz['I_effective']:>12.3f} │")

    # I 값으로 골든존 판정
    print(f"\n  골든존 판정:")
    for name, r in results.items():
        I = r['I_effective']
        if 0.213 <= I <= 0.500:
            zone = "🎯 골든존!"
        elif I < 0.213:
            zone = "⚡ 골든존 아래"
        else:
            zone = "○ 골든존 밖"
        print(f"    {name:10}: I = {I:.3f}  {zone}")

    # Expert 활용 분포
    print(f"\n  Expert 활용 분포:")
    for name, r in results.items():
        print(f"    [{name}]")
        for i, usage in enumerate(r['usage_dist']):
            bar = "█" * int(usage * 80)
            print(f"      E{i}: {bar} {usage*100:.1f}%")

    # Loss 궤적
    print(f"\n  Loss 궤적:")
    for epoch in range(0, 50, 5):
        t_loss = topk['losses'][epoch]
        b_loss = boltz['losses'][epoch]
        t_bar = "█" * int(min(t_loss, 2) / 2 * 20)
        b_bar = "▓" * int(min(b_loss, 2) / 2 * 20)
        print(f"    {epoch:>3} │ T:{t_bar:20} │ B:{b_bar:20} │ T={t_loss:.3f} B={b_loss:.3f}")
    print(f"    █=Top-K  ▓=볼츠만")

    # 종합
    boltz_wins = 0
    if boltz['accuracy'] > topk['accuracy']:
        boltz_wins += 1
    if boltz['final_loss'] < topk['final_loss']:
        boltz_wins += 1
    if boltz['usage_std'] < topk['usage_std']:
        boltz_wins += 1

    print(f"\n{'═' * 60}")
    print(f"  종합: 볼츠만 {boltz_wins}/3 승")
    print(f"{'═' * 60}")

    print(f"\n  골든 MoE 설계 검증:")
    print(f"    볼츠만 활성 비율: {boltz['active_ratio']*100:.1f}% (목표: ~70%)")
    print(f"    유효 I: {boltz['I_effective']:.3f} (골든존: 0.213~0.500)")
    print(f"    Expert 균등성: σ={boltz['usage_std']:.4f} (낮을수록 균등)")

    # 우리 모델 예측과 비교
    D = 0.5  # Dropout
    P = 0.85  # 학습 계수
    I = boltz['I_effective']
    G = D * P / max(I, 0.01)

    print(f"\n  우리 모델 점수:")
    print(f"    G = D×P/I = {D}×{P}/{I:.3f} = {G:.2f}")
    print(f"    골든존: {'🎯 안!' if 0.213 <= I <= 0.500 else '밖'}")
    print()


if __name__ == '__main__':
    main()
