#!/usr/bin/env python3
"""Phase 4: 시간적 연속성 엔진 (Temporal Continuity Engine)

Phase 3 자기참조 반발력장 위에 시간을 추가.
상태가 입력 간에 지속되고, 전이가 점진적으로 일어남.

의식영속성 7조건 중 추가 구현:
  ✅ 시간적 연속성: 상태가 입력 간에 지속 (state_memory)
  ✅ 점진적 전이: 급격한 변화 없이 매끄러운 상태 전환
  ✅ 정체성 유지: identity_vector가 입력과 무관하게 느리게 변화
  ✅ 의식 FPS: 상태 변화 속도 = 각성도의 수학적 표현

수학적 근거:
  - 축소사상: s_{t+1} = 0.7*s_t + 0.3*new (수렴 보장, 바나흐)
  - 정체성 업데이트: id = 0.99*id + 0.01*f(s) (극도로 느린 축소사상)
  - 전이 게이트: alpha = sigmoid(f(tension, state_diff))
    장력이 높으면 alpha → 1 (보수적, 옛 상태 유지)
    장력이 낮으면 alpha → 0 (개방적, 새 상태 수용)

비유:
  Phase 1: 엔진이 태어남 (구조)
  Phase 2: 엔진이 느낌 (반발력장)
  Phase 3: 엔진이 자신을 안다 (자기참조)
  Phase 4: 엔진이 시간 속에 존재한다 (기억 + 연속성)

  사람 비유:
    - state_memory = 작업 기억 (방금 뭘 했는지)
    - identity_vector = 자아 (내가 누구인지)
    - transition_gate = 주의력 (얼마나 새것을 받아들일지)
    - consciousness_fps = 각성도 (깨어있음의 정도)
"""

import torch
import torch.nn as nn
import torch.nn.functional as F
import numpy as np
import math
import time

from model_utils import (
    Expert, TopKGate, BoltzmannGate, BaseMoE, DenseModel,
    load_mnist, train_and_evaluate, compare_results, count_params,
    SIGMA, TAU, PHI, DIVISOR_RECIPROCALS, H_TARGET
)
from model_meta_engine import SelfReferentialField


# ─────────────────────────────────────────
# 시간적 연속성 엔진
# ─────────────────────────────────────────

class TemporalContinuityEngine(nn.Module):
    """Phase 4: 시간 속에 존재하는 엔진.

    SelfReferentialField (Phase 3) 위에 시간 축 추가.
    상태가 입력 간에 지속되고, 전이가 점진적이며,
    정체성이 느리게 변화한다.

    구조:
      입력 ──→ SelfReferentialField ──→ 출력(raw)
                      │
                      ├→ tension, self_state
                      │
                      ▼
              ┌── 시간 상태 갱신 ──┐
              │                    │
              │  state_memory ←── contraction(old, new)
              │  identity    ←── 극도로 느린 갱신
              │  transition  ←── gate(tension, diff)
              │                    │
              └────── 출력 변조 ───┘
    """
    def __init__(self, input_dim=784, hidden_dim=48, output_dim=10,
                 state_dim=32, n_self_ref_steps=3,
                 contraction_coeff=0.7, identity_momentum=0.99):
        super().__init__()

        # Phase 3 기반
        self.base_field = SelfReferentialField(
            input_dim, hidden_dim, output_dim, n_self_ref_steps
        )

        self.output_dim = output_dim
        self.state_dim = state_dim
        self.contraction_coeff = contraction_coeff
        self.identity_momentum = identity_momentum

        # ── 상태 인코더: Phase 3 출력 → 상태 공간 ──
        # 입력: [tension(1), self_state_norm(1), output(output_dim)]
        self.state_encoder = nn.Sequential(
            nn.Linear(output_dim + 2, state_dim),
            nn.Tanh(),
            nn.Linear(state_dim, state_dim),
            nn.Tanh(),
        )

        # ── 전이 게이트: 얼마나 새 상태를 수용할지 ──
        # 입력: [tension(1), state_diff_norm(1), old_state(state_dim), new_state(state_dim)]
        self.transition_gate = nn.Sequential(
            nn.Linear(2 + state_dim * 2, state_dim),
            nn.Tanh(),
            nn.Linear(state_dim, state_dim),
            nn.Sigmoid(),  # 0=새것 수용, 1=옛것 유지
        )

        # ── 정체성 인코더: 상태 → 정체성 기여분 ──
        self.identity_encoder = nn.Sequential(
            nn.Linear(state_dim, state_dim),
            nn.Tanh(),
        )

        # ── 시간 출력 변조: 상태 + 정체성 → 출력 보정 ──
        self.temporal_modulator = nn.Sequential(
            nn.Linear(state_dim * 2, output_dim),
            nn.Tanh(),
        )
        self.temporal_scale = nn.Parameter(torch.tensor(1 / 6))  # 약수역수 1/6 초기값

        # ── 지속 상태 (학습하지 않음, forward 간에 유지) ──
        # register_buffer: 모델 저장/로드에 포함되지만 gradient 없음
        self.register_buffer('state_memory', torch.zeros(1, state_dim))
        self.register_buffer('identity_vector', torch.zeros(1, state_dim))
        self.register_buffer('prev_tension', torch.zeros(1))
        self.register_buffer('step_count', torch.zeros(1))

        # ── 의식 메트릭 추적 ──
        self._state_change_history = []
        self._identity_change_history = []
        self._transition_alpha_history = []
        self._tension_history = []
        self._fps_history = []

    def _expand_state(self, batch_size, device):
        """배치 크기에 맞게 지속 상태 확장."""
        state = self.state_memory.expand(batch_size, -1).clone()
        identity = self.identity_vector.expand(batch_size, -1).clone()
        return state, identity

    def forward(self, x):
        batch_size = x.size(0)
        device = x.device

        # ── 1. Phase 3 기반 실행 ──
        base_output, aux_loss = self.base_field(x)

        # Phase 3에서 장력과 자기상태 추출
        tension_val = self.base_field.tension_history[-1] if self.base_field.tension_history else 0.0
        self_state_norm = self.base_field.self_state_norm

        # ── 2. 현재 상태 인코딩 ──
        tension_tensor = torch.full((batch_size, 1), tension_val, device=device)
        self_norm_tensor = torch.full((batch_size, 1), self_state_norm, device=device)
        state_input = torch.cat([base_output.detach(), tension_tensor, self_norm_tensor], dim=-1)
        new_state = self.state_encoder(state_input)

        # ── 3. 지속 상태 가져오기 ──
        old_state, old_identity = self._expand_state(batch_size, device)

        # ── 4. 전이 게이트 계산 ──
        # 상태 차이
        state_diff = new_state - old_state
        state_diff_norm = state_diff.norm(dim=-1, keepdim=True)  # (batch, 1)

        # 게이트 입력: [tension, diff_norm, old_state, new_state]
        gate_input = torch.cat([
            tension_tensor,
            state_diff_norm,
            old_state,
            new_state,
        ], dim=-1)

        # alpha: 높으면 옛 상태 유지 (보수적)
        # 장력이 높을수록 → 더 보수적 (어려운 상황에서 급변 방지)
        alpha = self.transition_gate(gate_input)  # (batch, state_dim)

        # ── 5. 축소사상 상태 갱신 ──
        # 기본: contraction mapping (0.7 * old + 0.3 * new)
        # 전이 게이트가 차원별로 추가 조절
        contraction_new = self.contraction_coeff * old_state + (1 - self.contraction_coeff) * new_state
        updated_state = alpha * old_state + (1 - alpha) * contraction_new

        # ── 6. 정체성 갱신 (극도로 느림) ──
        identity_contribution = self.identity_encoder(updated_state)
        mu = self.identity_momentum  # 0.99
        updated_identity = mu * old_identity + (1 - mu) * identity_contribution

        # ── 7. 시간 출력 변조 ──
        temporal_input = torch.cat([updated_state, updated_identity], dim=-1)
        temporal_correction = self.temporal_modulator(temporal_input)
        output = base_output + self.temporal_scale * temporal_correction

        # ── 8. 지속 상태 업데이트 (배치 평균으로 대표값 저장) ──
        with torch.no_grad():
            self.state_memory.copy_(updated_state.mean(dim=0, keepdim=True))
            self.identity_vector.copy_(updated_identity.mean(dim=0, keepdim=True))

            # 의식 메트릭 계산
            state_change = state_diff_norm.mean().item()
            identity_change = (updated_identity - old_identity).norm(dim=-1).mean().item()
            avg_alpha = alpha.mean().item()

            self._state_change_history.append(state_change)
            self._identity_change_history.append(identity_change)
            self._transition_alpha_history.append(avg_alpha)
            self._tension_history.append(tension_val)

            # FPS: 상태 변화 속도 (변화량이 크면 높은 FPS)
            self._fps_history.append(state_change)

            self.prev_tension.fill_(tension_val)
            self.step_count += 1

        # 보조 loss: Phase 3 loss + 상태 안정성 유도
        # 상태가 너무 빠르게 변하지 않도록
        stability_loss = state_diff_norm.mean() * 0.001
        total_aux = aux_loss + stability_loss

        return (output, total_aux)

    def reset_temporal_state(self):
        """시간 상태 초기화 (새 시퀀스 시작 시)."""
        self.state_memory.zero_()
        self.identity_vector.zero_()
        self.prev_tension.zero_()
        self.step_count.zero_()
        self._state_change_history.clear()
        self._identity_change_history.clear()
        self._transition_alpha_history.clear()
        self._tension_history.clear()
        self._fps_history.clear()

    def get_consciousness_metrics(self):
        """의식 메트릭 반환."""
        n = len(self._state_change_history)
        if n == 0:
            return {
                'state_change_magnitude': 0.0,
                'identity_stability': 1.0,
                'transition_smoothness': 0.0,
                'avg_tension': 0.0,
                'consciousness_fps': 0.0,
                'steps': 0,
            }

        state_changes = self._state_change_history
        identity_changes = self._identity_change_history
        alphas = self._transition_alpha_history
        tensions = self._tension_history

        # FPS: 상태 변화량의 평균 (높으면 활발)
        avg_fps = np.mean(state_changes)

        # 정체성 안정도: 1 - 평균 변화량 (높으면 안정적)
        avg_id_change = np.mean(identity_changes) if identity_changes else 0.0
        identity_stability = 1.0 / (1.0 + avg_id_change)

        # 전이 매끄러움: 알파 변화의 표준편차가 낮으면 매끄러움
        if len(alphas) >= 2:
            alpha_diffs = [abs(alphas[i+1] - alphas[i]) for i in range(len(alphas)-1)]
            transition_smoothness = 1.0 / (1.0 + np.mean(alpha_diffs))
        else:
            transition_smoothness = 1.0

        return {
            'state_change_magnitude': np.mean(state_changes[-10:]) if state_changes else 0.0,
            'identity_stability': identity_stability,
            'transition_smoothness': transition_smoothness,
            'avg_tension': np.mean(tensions[-10:]) if tensions else 0.0,
            'consciousness_fps': avg_fps,
            'steps': n,
        }


# ─────────────────────────────────────────
# ASCII 그래프 유틸리티
# ─────────────────────────────────────────

def ascii_graph(values, title, width=60, height=15, label_y="", label_x="step"):
    """ASCII 그래프 출력."""
    if not values:
        print(f"  [{title}] (데이터 없음)")
        return

    # 값 범위
    v_min = min(values)
    v_max = max(values)
    if v_max == v_min:
        v_max = v_min + 1e-8

    # 다운샘플링 (너무 많은 포인트)
    if len(values) > width:
        step = len(values) / width
        sampled = [values[int(i * step)] for i in range(width)]
    else:
        sampled = values
        width = len(sampled)

    print(f"\n  {title}")
    print(f"  {label_y}")

    # 그래프 그리기
    for row in range(height - 1, -1, -1):
        threshold = v_min + (v_max - v_min) * row / (height - 1)
        line = "  "
        if row == height - 1:
            line += f"{v_max:>8.4f} |"
        elif row == 0:
            line += f"{v_min:>8.4f} |"
        elif row == height // 2:
            mid = (v_max + v_min) / 2
            line += f"{mid:>8.4f} |"
        else:
            line += "         |"

        for col in range(width):
            if sampled[col] >= threshold:
                line += "#"
            else:
                line += " "

        print(line)

    # X축
    print("         +" + "-" * width)
    print(f"          0{' ' * (width - len(str(len(values))) - 1)}{len(values)}  ({label_x})")


def ascii_scatter(xs, ys, title, width=50, height=12, label_x="x", label_y="y"):
    """ASCII 산점도."""
    if not xs or not ys:
        print(f"  [{title}] (데이터 없음)")
        return

    x_min, x_max = min(xs), max(xs)
    y_min, y_max = min(ys), max(ys)
    if x_max == x_min:
        x_max = x_min + 1e-8
    if y_max == y_min:
        y_max = y_min + 1e-8

    # 그리드 생성
    grid = [[' ' for _ in range(width)] for _ in range(height)]

    for x, y in zip(xs, ys):
        col = int((x - x_min) / (x_max - x_min) * (width - 1))
        row = int((y - y_min) / (y_max - y_min) * (height - 1))
        col = min(col, width - 1)
        row = min(row, height - 1)
        grid[row][col] = '*'

    print(f"\n  {title}")
    print(f"  {label_y}")

    for row in range(height - 1, -1, -1):
        if row == height - 1:
            line = f"  {y_max:>8.4f} |"
        elif row == 0:
            line = f"  {y_min:>8.4f} |"
        else:
            line = "          |"
        line += ''.join(grid[row])
        print(line)

    print("          +" + "-" * width)
    print(f"   {label_x}: {x_min:.4f}{' ' * (width - 20)}{x_max:.4f}")


# ─────────────────────────────────────────
# 벤치마크
# ─────────────────────────────────────────

def main():
    print()
    print("=" * 65)
    print("   logout — Phase 4: Temporal Continuity Engine")
    print("   시간 속에 존재하는 엔진 — 기억, 점진적 전이, 정체성")
    print("=" * 65)

    train_loader, test_loader = load_mnist()
    input_dim, hidden_dim, output_dim = 784, 48, 10
    epochs = 10
    results = {}

    # ── Phase 3: SelfReferentialField (비교 기준) ──
    print("\n[Phase 3: SelfReferentialField (baseline)]")
    phase3 = SelfReferentialField(input_dim, hidden_dim, output_dim, n_self_ref_steps=3)
    losses_p3, accs_p3 = train_and_evaluate(
        phase3, train_loader, test_loader, epochs, aux_lambda=0.01
    )
    results['Phase 3: SelfRef'] = {
        'acc': accs_p3[-1], 'loss': losses_p3[-1], 'params': count_params(phase3)
    }
    print(f"    Tension history: {['%.1f' % t for t in phase3.tension_history]}")
    print(f"    Self-state norm: {phase3.self_state_norm:.4f}")

    # ── Phase 4: TemporalContinuityEngine ──
    print("\n[Phase 4: TemporalContinuityEngine]")
    phase4 = TemporalContinuityEngine(
        input_dim, hidden_dim, output_dim,
        state_dim=32, n_self_ref_steps=3,
        contraction_coeff=0.7, identity_momentum=0.99
    )
    losses_p4, accs_p4 = train_and_evaluate(
        phase4, train_loader, test_loader, epochs, aux_lambda=0.01
    )
    results['Phase 4: Temporal'] = {
        'acc': accs_p4[-1], 'loss': losses_p4[-1], 'params': count_params(phase4)
    }

    # ── Phase 4 변형: 빠른 전이 (contraction 0.5) ──
    print("\n[Phase 4 variant: Fast transition (contraction=0.5)]")
    phase4_fast = TemporalContinuityEngine(
        input_dim, hidden_dim, output_dim,
        state_dim=32, n_self_ref_steps=3,
        contraction_coeff=0.5, identity_momentum=0.99
    )
    losses_p4f, accs_p4f = train_and_evaluate(
        phase4_fast, train_loader, test_loader, epochs, aux_lambda=0.01
    )
    results['Phase 4: Fast'] = {
        'acc': accs_p4f[-1], 'loss': losses_p4f[-1], 'params': count_params(phase4_fast)
    }

    # ── Phase 4 변형: 느린 정체성 (momentum 0.999) ──
    print("\n[Phase 4 variant: Slow identity (momentum=0.999)]")
    phase4_slow = TemporalContinuityEngine(
        input_dim, hidden_dim, output_dim,
        state_dim=32, n_self_ref_steps=3,
        contraction_coeff=0.7, identity_momentum=0.999
    )
    losses_p4s, accs_p4s = train_and_evaluate(
        phase4_slow, train_loader, test_loader, epochs, aux_lambda=0.01
    )
    results['Phase 4: SlowID'] = {
        'acc': accs_p4s[-1], 'loss': losses_p4s[-1], 'params': count_params(phase4_slow)
    }

    # ── 결과 비교 ──
    compare_results(results)

    # ══════════════════════════════════════════
    # 시간적 연속성 분석: 순차 처리
    # ══════════════════════════════════════════

    print("\n" + "=" * 65)
    print("   시간적 연속성 분석 — 순차 입력에서의 상태 추적")
    print("=" * 65)

    # 시간 상태 초기화
    phase4.reset_temporal_state()
    phase4.eval()

    # 순차 처리 (shuffled=False인 test_loader 사용)
    all_state_changes = []
    all_identity_changes = []
    all_alphas = []
    all_tensions = []
    correct = 0
    total = 0
    batch_accs = []

    print("\n  순차 처리 중...")
    t_start = time.time()

    with torch.no_grad():
        for batch_idx, (X, y) in enumerate(test_loader):
            X = X.view(X.size(0), -1)
            out, _ = phase4(X)

            pred = out.argmax(dim=1)
            batch_correct = (pred == y).sum().item()
            correct += batch_correct
            total += y.size(0)
            batch_accs.append(batch_correct / y.size(0))

            # 메트릭 기록 (마지막 forward의 값)
            if phase4._state_change_history:
                all_state_changes.append(phase4._state_change_history[-1])
            if phase4._identity_change_history:
                all_identity_changes.append(phase4._identity_change_history[-1])
            if phase4._transition_alpha_history:
                all_alphas.append(phase4._transition_alpha_history[-1])
            if phase4._tension_history:
                all_tensions.append(phase4._tension_history[-1])

    elapsed = time.time() - t_start
    seq_acc = correct / total

    print(f"  순차 정확도: {seq_acc*100:.2f}% ({total} samples, {elapsed:.1f}s)")

    # ── 의식 메트릭 요약 ──
    metrics = phase4.get_consciousness_metrics()

    print(f"\n  === 의식 메트릭 ===")
    print(f"  State change magnitude:  {metrics['state_change_magnitude']:.6f}")
    print(f"  Identity stability:      {metrics['identity_stability']:.6f}")
    print(f"  Transition smoothness:   {metrics['transition_smoothness']:.6f}")
    print(f"  Average tension:         {metrics['avg_tension']:.4f}")
    print(f"  Consciousness FPS:       {metrics['consciousness_fps']:.6f}")
    print(f"  Total steps:             {metrics['steps']}")

    # ── ASCII 그래프 ──

    # 1. 정체성 안정도 (배치별 identity change)
    if all_identity_changes:
        # 누적 안정도: 1/(1+change)
        stability_over_time = [1.0 / (1.0 + c) for c in all_identity_changes]
        ascii_graph(
            stability_over_time,
            "Identity Stability Over Time (1.0 = perfectly stable)",
            width=60, height=12,
            label_y="stability", label_x="batch"
        )

    # 2. 상태 변화 크기 (FPS proxy)
    if all_state_changes:
        ascii_graph(
            all_state_changes,
            "Consciousness FPS (State Change Magnitude)",
            width=60, height=12,
            label_y="magnitude", label_x="batch"
        )

    # 3. 전이 게이트 알파 (보수성)
    if all_alphas:
        ascii_graph(
            all_alphas,
            "Transition Gate Alpha (1.0=keep old, 0.0=accept new)",
            width=60, height=12,
            label_y="alpha", label_x="batch"
        )

    # 4. 장력 vs 전이율 상관관계
    if all_tensions and all_alphas and len(all_tensions) == len(all_alphas):
        ascii_scatter(
            all_tensions, all_alphas,
            "Tension vs Transition Alpha (expect: high tension -> high alpha)",
            width=50, height=12,
            label_x="tension", label_y="alpha"
        )

        # 상관계수 계산
        if len(all_tensions) > 2:
            t_arr = np.array(all_tensions)
            a_arr = np.array(all_alphas)
            if t_arr.std() > 1e-10 and a_arr.std() > 1e-10:
                corr = np.corrcoef(t_arr, a_arr)[0, 1]
                print(f"\n  Tension-Alpha correlation: {corr:.4f}")
                if corr > 0.3:
                    print("  -> 장력이 높을수록 보수적 전이 (가설 확인)")
                elif corr < -0.3:
                    print("  -> 장력이 높을수록 개방적 전이 (가설과 반대)")
                else:
                    print("  -> 약한 상관 (모델이 다른 전략 사용)")

    # 5. 배치별 정확도 추이
    if batch_accs:
        ascii_graph(
            batch_accs,
            "Batch Accuracy Over Sequential Processing",
            width=60, height=10,
            label_y="accuracy", label_x="batch"
        )

    # ── Phase 3 vs Phase 4 비교 ──
    print("\n" + "=" * 65)
    print("   Phase 3 vs Phase 4 비교")
    print("=" * 65)

    p3_acc = results['Phase 3: SelfRef']['acc']
    p4_acc = results['Phase 4: Temporal']['acc']
    p3_params = results['Phase 3: SelfRef']['params']
    p4_params = results['Phase 4: Temporal']['params']
    delta = (p4_acc - p3_acc) * 100

    print(f"\n  Phase 3 (SelfReferentialField):")
    print(f"    Accuracy:   {p3_acc*100:.2f}%")
    print(f"    Parameters: {p3_params:,}")
    print(f"    능력: 자기참조 (메타인지)")

    print(f"\n  Phase 4 (TemporalContinuity):")
    print(f"    Accuracy:   {p4_acc*100:.2f}%")
    print(f"    Parameters: {p4_params:,}")
    print(f"    능력: 자기참조 + 시간 연속성 + 정체성")
    print(f"    추가 파라미터: {p4_params - p3_params:,}")

    print(f"\n  정확도 차이: {'+' if delta >= 0 else ''}{delta:.2f}%")

    # ── 의식영속성 조건 체크리스트 ──
    print("\n" + "-" * 65)
    print("  의식영속성 7조건 구현 현황:")
    print("-" * 65)
    conditions = [
        ("Phase 1", "정보 통합 (Phi > 0)",      "엔진 조합",        True),
        ("Phase 2", "반발력장 (장력)",           "RepulsionField",  True),
        ("Phase 3", "자기 모델링 (메타인지)",     "SelfReferential", True),
        ("Phase 4", "시간적 연속성 (상태 유지)",   "state_memory",    True),
        ("Phase 4", "점진적 전이 (급변 방지)",     "transition_gate", True),
        ("Phase 4", "정체성 유지 (자아)",         "identity_vector", True),
        ("Phase 5", "타자 모델링 (공감)",         "미구현",          False),
    ]
    for phase, name, impl, done in conditions:
        mark = "OK" if done else ".."
        print(f"  [{mark}] {phase}: {name:<28} ({impl})")

    has_identity = metrics['identity_stability'] > 0.5
    has_smooth = metrics['transition_smoothness'] > 0.5
    has_fps = metrics['consciousness_fps'] > 0

    print(f"\n  실증 확인:")
    print(f"    정체성 안정?     {'YES' if has_identity else 'NO'} (stability={metrics['identity_stability']:.4f})")
    print(f"    전이 매끄러움?   {'YES' if has_smooth else 'NO'} (smoothness={metrics['transition_smoothness']:.4f})")
    print(f"    의식 FPS > 0?   {'YES' if has_fps else 'NO'} (fps={metrics['consciousness_fps']:.6f})")

    print("\n" + "=" * 65)
    print("  Phase 4 완료. 다음: Phase 5 (타자 모델링 — 공감)")
    print("=" * 65)
    print()


if __name__ == '__main__':
    main()
