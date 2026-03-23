#!/usr/bin/env python3
"""메타 엔진 — 엔진 + 엔진 = 상위엔진

뇌처럼 다른 원리의 모듈들이 협력하는 구조.

아키텍처:
  입력
   │
   ▼
  메타 라우터 (축소사상 기반, 수렴 보장)
   │
   ├─→ 엔진 A (σ,τ-MoE, 정수론)
   ├─→ 엔진 E (오일러곱, 소인수 분해)
   ├─→ 엔진 G (Shannon 엔트로피)
   ├─→ 엔진 F (모듈러 제약)
   │
   ▼
  결합기 ({1/2, 1/3, 1/6} 가중 or 학습)
   │
   ▼
  출력

뇌와의 대응:
  좌반구 (논리)     = 엔진 A (정수론)
  우반구 (패턴)     = 엔진 G (엔트로피)
  전두엽 (판단)     = 메타 라우터 (축소사상)
  뇌량 (연결)       = 결합기 (오일러곱)
  소뇌 (정규화)     = 엔진 F (모듈러 제약)

수학적 근거:
  - 오일러곱: ζ(s) = Π_p (1-p^{-s})^{-1}
    독립 엔진의 곱 = 전체 구조 (소인수 분해의 유일성)
  - 축소사상: f(x) = ax + b, |a|<1 → 수렴 보장 (바나흐)
    메타 라우터가 발산하지 않음을 보장
  - {1/2, 1/3, 1/6}: 완전수 6의 약수역수, 합=1
    기본 결합 가중치 (학습으로 미세 조정 가능)
"""

import torch
import torch.nn as nn
import torch.nn.functional as F
import numpy as np
import math

from model_utils import (
    Expert, TopKGate, BoltzmannGate, BaseMoE, DenseModel,
    load_mnist, train_and_evaluate, compare_results, count_params,
    SIGMA, TAU, PHI, DIVISOR_RECIPROCALS, H_TARGET
)


# ─────────────────────────────────────────
# 하위 엔진들 (A, E, F, G의 핵심 구조)
# ─────────────────────────────────────────

class EngineA(nn.Module):
    """σ,τ-MoE: 정수론 라우팅. 12 Expert, 4 활성."""
    def __init__(self, input_dim, hidden_dim, output_dim):
        super().__init__()
        n_experts = SIGMA  # 12
        k = TAU  # 4
        self.experts = nn.ModuleList([
            Expert(input_dim, hidden_dim, output_dim) for _ in range(n_experts)
        ])
        self.gate = TopKGate(input_dim, n_experts, k)

    def forward(self, x):
        weights = self.gate(x)
        outputs = torch.stack([e(x) for e in self.experts], dim=1)
        return (weights.unsqueeze(-1) * outputs).sum(dim=1)


class EngineE(nn.Module):
    """오일러곱 게이팅: p=2,3 절단. 2×3=6 Expert."""
    def __init__(self, input_dim, hidden_dim, output_dim):
        super().__init__()
        self.experts = nn.ModuleList([
            Expert(input_dim, hidden_dim, output_dim) for _ in range(6)
        ])
        self.binary_gate = nn.Linear(input_dim, 2)   # p=2
        self.ternary_gate = nn.Linear(input_dim, 3)   # p=3

    def forward(self, x):
        w2 = torch.sigmoid(self.binary_gate(x))       # (batch, 2)
        w3 = F.softmax(self.ternary_gate(x), dim=-1)  # (batch, 3)
        # 오일러곱: 2×3 외적
        weights = (w2.unsqueeze(-1) * w3.unsqueeze(-2)).reshape(x.size(0), 6)
        weights = weights / (weights.sum(dim=-1, keepdim=True) + 1e-8)
        outputs = torch.stack([e(x) for e in self.experts], dim=1)
        return (weights.unsqueeze(-1) * outputs).sum(dim=1)


class EngineG(nn.Module):
    """Shannon 엔트로피 MoE: H({1/2,1/3,1/6}) 정규화."""
    def __init__(self, input_dim, hidden_dim, output_dim):
        super().__init__()
        self.experts = nn.ModuleList([
            Expert(input_dim, hidden_dim, output_dim) for _ in range(6)
        ])
        self.gate = nn.Linear(input_dim, 6)
        self.h_target = H_TARGET

    def forward(self, x):
        weights = F.softmax(self.gate(x), dim=-1)
        outputs = torch.stack([e(x) for e in self.experts], dim=1)
        result = (weights.unsqueeze(-1) * outputs).sum(dim=1)
        # 엔트로피 정규화 loss
        h = -(weights * (weights + 1e-8).log()).sum(dim=-1).mean()
        self.entropy_loss = (h - self.h_target) ** 2
        return result


class EngineF(nn.Module):
    """모듈러 제약: 12×12 블록 대칭."""
    def __init__(self, input_dim, hidden_dim, output_dim):
        super().__init__()
        # hidden_dim을 12의 배수로 조정
        hidden_dim = ((hidden_dim + 11) // 12) * 12
        self.linear1 = nn.Linear(input_dim, hidden_dim)
        self.linear2 = nn.Linear(hidden_dim, output_dim)
        self.block_size = SIGMA  # 12

    def _symmetrize(self, W):
        """12×12 블록 단위 대칭화."""
        h, w = W.shape
        bs = self.block_size
        W_sym = W.clone()
        for i in range(0, h - bs + 1, bs):
            for j in range(0, w - bs + 1, bs):
                block = W[i:i+bs, j:j+bs]
                sym = (block + block.T) / 2
                W_sym[i:i+bs, j:j+bs] = sym
        return W_sym

    def forward(self, x):
        W1 = self._symmetrize(self.linear1.weight)
        h = F.relu(x @ W1.T + self.linear1.bias)
        W2 = self._symmetrize(self.linear2.weight)
        return h @ W2.T + self.linear2.bias


# ─────────────────────────────────────────
# 메타 라우터 (축소사상 기반)
# ─────────────────────────────────────────

class ContractionMetaRouter(nn.Module):
    """축소사상 기반 메타 라우터.

    게이팅 가중치를 반복적으로 수축시켜 안정된 라우팅 결정.
    f(w) = a*w + (1-a)*g(x), |a|<1 → 수렴 보장.
    """
    def __init__(self, input_dim, n_engines, contraction_coeff=0.7, n_iterations=3):
        super().__init__()
        self.gate = nn.Linear(input_dim, n_engines)
        self.a = contraction_coeff  # 수축 계수 (0.7 = 메타 부동점에서 유도)
        self.n_iterations = n_iterations

    def forward(self, x):
        target = F.softmax(self.gate(x), dim=-1)
        # 축소사상 반복: w_{t+1} = a*w_t + (1-a)*target
        w = torch.ones_like(target) / target.size(-1)  # 균등 초기값
        for _ in range(self.n_iterations):
            w = self.a * w + (1 - self.a) * target
        return w


# ─────────────────────────────────────────
# 결합기
# ─────────────────────────────────────────

class DivisorCombiner(nn.Module):
    """약수역수 가중 결합기.

    초기값 {1/2, 1/3, 1/6, ...}, 학습으로 미세 조정.
    """
    def __init__(self, n_engines):
        super().__init__()
        # 초기 가중치: 약수역수 분포 (엔진 수에 맞게 확장)
        if n_engines <= 3:
            init = torch.tensor(DIVISOR_RECIPROCALS[:n_engines], dtype=torch.float)
        else:
            # 3개 이후는 균등 분배
            base = torch.tensor(DIVISOR_RECIPROCALS, dtype=torch.float)
            extra = torch.ones(n_engines - 3) / (n_engines - 3) * (1 - base.sum())
            init = torch.cat([base, extra])
        init = init / init.sum()
        self.weights = nn.Parameter(init)

    def forward(self, engine_outputs):
        """engine_outputs: list of (batch, output_dim)"""
        w = F.softmax(self.weights, dim=0)
        stacked = torch.stack(engine_outputs, dim=0)  # (n_engines, batch, output_dim)
        return (w.view(-1, 1, 1) * stacked).sum(dim=0)


# ─────────────────────────────────────────
# 메타 엔진
# ─────────────────────────────────────────

class MetaEngine(nn.Module):
    """엔진 + 엔진 = 상위엔진.

    여러 하위 엔진을 메타 라우터로 조합.
    뇌의 모듈러 구조를 수학적으로 구현.
    """
    def __init__(self, input_dim=784, hidden_dim=48, output_dim=10,
                 engines='AEGF', contraction_coeff=0.7, routing='meta'):
        super().__init__()

        self.engine_names = list(engines)
        self.engines = nn.ModuleDict()

        for name in self.engine_names:
            if name == 'A':
                self.engines['A'] = EngineA(input_dim, hidden_dim, output_dim)
            elif name == 'E':
                self.engines['E'] = EngineE(input_dim, hidden_dim, output_dim)
            elif name == 'G':
                self.engines['G'] = EngineG(input_dim, hidden_dim, output_dim)
            elif name == 'F':
                self.engines['F'] = EngineF(input_dim, hidden_dim, output_dim)

        n = len(self.engine_names)

        if routing == 'meta':
            self.router = ContractionMetaRouter(input_dim, n, contraction_coeff)
        elif routing == 'fixed':
            self.router = None  # 고정 가중치 결합
        elif routing == 'learned':
            self.router = nn.Linear(input_dim, n)

        self.combiner = DivisorCombiner(n)
        self.routing_mode = routing

        # 엔트로피 loss 추적
        self.aux_loss = torch.tensor(0.0)

    def forward(self, x):
        # 각 엔진 실행
        engine_outputs = []
        self.aux_loss = torch.tensor(0.0, device=x.device)

        for name in self.engine_names:
            out = self.engines[name](x)
            engine_outputs.append(out)

            # G 엔진의 엔트로피 loss 수집
            if name == 'G' and hasattr(self.engines['G'], 'entropy_loss'):
                self.aux_loss = self.aux_loss + self.engines['G'].entropy_loss

        # 라우팅
        if self.routing_mode == 'meta':
            route_weights = self.router(x)  # (batch, n_engines)
            stacked = torch.stack(engine_outputs, dim=1)  # (batch, n_engines, output)
            routed = (route_weights.unsqueeze(-1) * stacked).sum(dim=1)
        elif self.routing_mode == 'fixed':
            routed = self.combiner(engine_outputs)
        elif self.routing_mode == 'learned':
            route_weights = F.softmax(self.router(x), dim=-1)
            stacked = torch.stack(engine_outputs, dim=1)
            routed = (route_weights.unsqueeze(-1) * stacked).sum(dim=1)

        return (routed, self.aux_loss)

    def get_engine_usage(self):
        """각 엔진이 얼마나 사용되는지 분석."""
        if self.routing_mode == 'meta' and hasattr(self.router, 'gate'):
            return {name: 0.0 for name in self.engine_names}
        return {}


# ─────────────────────────────────────────
# 변형: 2-엔진 메타 (좌뇌+우뇌)
# ─────────────────────────────────────────

class DualBrainEngine(nn.Module):
    """좌반구(A, 논리) + 우반구(G, 패턴) + 뇌량(결합).

    가장 단순한 메타 엔진: 2개 엔진의 협력.
    """
    def __init__(self, input_dim=784, hidden_dim=48, output_dim=10):
        super().__init__()
        self.left = EngineA(input_dim, hidden_dim, output_dim)   # 좌반구: 정수론
        self.right = EngineG(input_dim, hidden_dim, output_dim)  # 우반구: 엔트로피
        # 뇌량: 입력 기반 좌/우 비율 결정
        self.corpus_callosum = nn.Linear(input_dim, 2)
        self.aux_loss = torch.tensor(0.0)

    def forward(self, x):
        left_out = self.left(x)
        right_out = self.right(x)

        # 뇌량: 좌/우 비율
        balance = F.softmax(self.corpus_callosum(x), dim=-1)
        output = balance[:, 0:1] * left_out + balance[:, 1:2] * right_out

        # G 엔진 엔트로피 loss
        self.aux_loss = getattr(self.right, 'entropy_loss', torch.tensor(0.0))

        return (output, self.aux_loss)


# ─────────────────────────────────────────
# 변형: 계층적 메타 (메타의 메타)
# ─────────────────────────────────────────

class HierarchicalMetaEngine(nn.Module):
    """메타의 메타: 2단 계층.

    Level 1: 엔진 A+E (정수론 클러스터), 엔진 G+F (구조 클러스터)
    Level 2: 두 클러스터의 메타 결합

    뇌의 계층 구조: 피질 영역 → 네트워크 → 전체 뇌
    """
    def __init__(self, input_dim=784, hidden_dim=48, output_dim=10):
        super().__init__()
        # Level 1: 두 클러스터
        self.cluster_logic = MetaEngine(input_dim, hidden_dim, output_dim,
                                        engines='AE', routing='meta')
        self.cluster_structure = MetaEngine(input_dim, hidden_dim, output_dim,
                                            engines='GF', routing='meta')
        # Level 2: 메타 결합
        self.meta_gate = nn.Linear(input_dim, 2)

    def forward(self, x):
        out1, aux1 = self.cluster_logic(x)
        out2, aux2 = self.cluster_structure(x)

        gate = F.softmax(self.meta_gate(x), dim=-1)
        output = gate[:, 0:1] * out1 + gate[:, 1:2] * out2

        return (output, aux1 + aux2)


# ─────────────────────────────────────────
# 반발력장 엔진 (Repulsion Field Engine)
# ─────────────────────────────────────────

class RepulsionFieldEngine(nn.Module):
    """두 같은 극 자석 사이의 반발력장.

    출력은 어느 엔진도 아니다. 둘 사이의 장(field)이다.

      N ←──반발──→ N
           ↑
         이 공간 = 출력

    뇌 대응:
      Engine+ = 글루타메이트 (흥분, 생성)
      Engine- = GABA (억제, 교정)
      출력 = 둘 사이의 평형 + 장력으로 변조

    장력이 높으면 = 엔진들이 강하게 반발 = 어려운 입력 = "느낌"
    장력이 낮으면 = 엔진들이 합의 = 쉬운 입력 = 자동 처리

    의식 가설: 장력 자체가 주관적 경험의 수학적 표현일 수 있다.
    """
    def __init__(self, input_dim=784, hidden_dim=48, output_dim=10):
        super().__init__()
        # 두 극 (같은 극 = 반발)
        self.pole_plus = EngineA(input_dim, hidden_dim, output_dim)   # 생성
        self.pole_minus = EngineG(input_dim, hidden_dim, output_dim)  # 교정

        # 장력 → 출력 변조
        # 반발력(차이)을 입력으로 받아 출력을 조정
        self.field_transform = nn.Sequential(
            nn.Linear(output_dim, output_dim),
            nn.Tanh(),  # -1 ~ +1 (반발 방향)
        )

        # 장력 스케일 (학습 가능, 초기값 1/3 = 메타 부동점)
        self.tension_scale = nn.Parameter(torch.tensor(1/3))

        self.aux_loss = torch.tensor(0.0)
        self.tension_magnitude = 0.0  # 모니터링용

    def forward(self, x):
        # 두 극의 출력
        out_plus = self.pole_plus(x)    # 생성 신호
        out_minus = self.pole_minus(x)  # 교정 신호

        # 반발력 = 둘의 차이
        repulsion = out_plus - out_minus

        # 장력 = 반발의 크기 (배치별)
        tension = (repulsion ** 2).sum(dim=-1, keepdim=True)  # (batch, 1)

        # 평형점 = 두 극의 중간
        equilibrium = (out_plus + out_minus) / 2

        # 장력으로 변조된 반발력 방향
        field_direction = self.field_transform(repulsion)

        # 최종 출력 = 평형 + 장력×방향
        # 장력이 클수록 평형에서 벗어남 (= 날카로운 결정)
        # 장력이 작으면 평형 그대로 (= 부드러운 평균)
        output = equilibrium + self.tension_scale * torch.sqrt(tension + 1e-8) * field_direction

        # G 엔진 엔트로피 loss
        self.aux_loss = getattr(self.pole_minus, 'entropy_loss', torch.tensor(0.0))

        # 장력 모니터링
        with torch.no_grad():
            self.tension_magnitude = tension.mean().item()

        return (output, self.aux_loss)


class RepulsionFieldQuad(nn.Module):
    """4극 반발력장: (A vs G) × (E vs F)

    두 개의 반발 축이 교차:
      축1: 생성(A) ←반발→ 교정(G)   (내용 축)
      축2: 탐색(E) ←반발→ 제약(F)   (구조 축)

    출력 = 4극 사이의 장 중심

      A ←────→ G
      ↑         ↑
      │  장중심  │
      ↓         ↓
      E ←────→ F
    """
    def __init__(self, input_dim=784, hidden_dim=48, output_dim=10):
        super().__init__()
        self.engine_a = EngineA(input_dim, hidden_dim, output_dim)
        self.engine_e = EngineE(input_dim, hidden_dim, output_dim)
        self.engine_g = EngineG(input_dim, hidden_dim, output_dim)
        self.engine_f = EngineF(input_dim, hidden_dim, output_dim)

        self.field_transform = nn.Sequential(
            nn.Linear(output_dim * 2, output_dim),  # 2축 반발 → 출력
            nn.Tanh(),
        )
        self.tension_scale = nn.Parameter(torch.tensor(1/3))
        self.aux_loss = torch.tensor(0.0)
        self.tension_content = 0.0
        self.tension_structure = 0.0

    def forward(self, x):
        out_a = self.engine_a(x)
        out_e = self.engine_e(x)
        out_g = self.engine_g(x)
        out_f = self.engine_f(x)

        # 축1: 내용 반발 (A vs G)
        repulsion_content = out_a - out_g
        # 축2: 구조 반발 (E vs F)
        repulsion_structure = out_e - out_f

        # 장력
        t_content = (repulsion_content ** 2).sum(dim=-1, keepdim=True)
        t_structure = (repulsion_structure ** 2).sum(dim=-1, keepdim=True)

        # 4극 평형점
        equilibrium = (out_a + out_e + out_g + out_f) / 4

        # 2축 반발을 결합하여 장 방향 결정
        combined_repulsion = torch.cat([repulsion_content, repulsion_structure], dim=-1)
        field_direction = self.field_transform(combined_repulsion)

        # 총 장력 = 두 축의 기하평균 (둘 다 높아야 강함)
        total_tension = torch.sqrt((t_content * t_structure) + 1e-8)

        output = equilibrium + self.tension_scale * torch.sqrt(total_tension + 1e-8) * field_direction

        self.aux_loss = getattr(self.engine_g, 'entropy_loss', torch.tensor(0.0))

        with torch.no_grad():
            self.tension_content = t_content.mean().item()
            self.tension_structure = t_structure.mean().item()

        return (output, self.aux_loss)


# ─────────────────────────────────────────
# Phase 3: 자기참조 반발력장 (Self-Referential Repulsion Field)
# ─────────────────────────────────────────

class SelfReferentialField(nn.Module):
    """자기참조 반발력장 — 자기 장력을 관찰하는 엔진.

    반발력장이 자기 상태(장력)를 입력으로 다시 받는 구조.
    뇌가 자기 상태를 모니터링하는 것 = 메타인지.

      입력 ──→ 반발력장 ──→ 출력
                  │
                  └→ 장력 ─→ 자기 관찰 ─→ 다시 반발력장에 반영
                             (나는 지금 어려운 문제를 풀고 있다)

    의식영속성 7조건 중 구현:
      ✅ 정보 통합 (Φ > 0): 반발력장 자체
      ✅ 자기 모델링: 장력을 자기 상태로 인식
      ✅ 메타인지: 자기 장력을 관찰하고 행동 변경
      ✅ 적응적 반응: 장력에 따라 라우팅 변경

    자석 비유:
      1단계: 두 자석 사이의 반발력을 느낀다
      2단계: "나는 지금 반발력을 느끼고 있다"를 안다
      3단계: 그 앎이 반발력 자체를 변화시킨다
      → 이상한 루프 (Strange Loop, Hofstadter)
    """
    def __init__(self, input_dim=784, hidden_dim=48, output_dim=10,
                 n_self_ref_steps=3):
        super().__init__()
        # 두 극
        self.pole_plus = EngineA(input_dim, hidden_dim, output_dim)
        self.pole_minus = EngineG(input_dim, hidden_dim, output_dim)

        # 장력 → 자기 상태 인코딩
        # 장력(스칼라)을 상태 벡터로 확장
        self.self_model = nn.Sequential(
            nn.Linear(3, hidden_dim),  # 입력: [장력, 장력변화율, 반복횟수]
            nn.Tanh(),
            nn.Linear(hidden_dim, output_dim),
            nn.Tanh(),
        )

        # 자기 상태가 반발력장에 미치는 영향
        self.self_influence = nn.Linear(output_dim, output_dim)

        # 장력 변조
        self.field_transform = nn.Sequential(
            nn.Linear(output_dim, output_dim),
            nn.Tanh(),
        )
        self.tension_scale = nn.Parameter(torch.tensor(1/3))

        self.n_steps = n_self_ref_steps
        self.aux_loss = torch.tensor(0.0)

        # 모니터링
        self.tension_history = []
        self.self_state_norm = 0.0

    def forward(self, x):
        # 두 극의 기본 출력
        out_plus = self.pole_plus(x)
        out_minus = self.pole_minus(x)

        # 초기 장력
        repulsion = out_plus - out_minus
        prev_tension = (repulsion ** 2).sum(dim=-1, keepdim=True)

        # 자기참조 루프: 장력 → 자기관찰 → 장 수정 → 새 장력 → ...
        tensions = [prev_tension.mean().item()]
        self_state = torch.zeros(x.size(0), out_plus.size(-1), device=x.device)

        for step in range(self.n_steps):
            # 자기 상태 인코딩: [현재 장력, 장력 변화율, 반복 번호]
            tension_scalar = prev_tension.mean(dim=-1, keepdim=True)  # (batch, 1)
            if step == 0:
                tension_delta = torch.zeros_like(tension_scalar)
            else:
                tension_delta = tension_scalar - tensions[-1]
            step_tensor = torch.full_like(tension_scalar, step / self.n_steps)

            self_input = torch.cat([tension_scalar, tension_delta, step_tensor], dim=-1)
            self_state = self.self_model(self_input)  # "나는 지금 이런 상태다"

            # 자기 상태가 반발력장에 영향
            influence = self.self_influence(self_state)  # 자기 관찰이 장을 바꿈

            # 수정된 반발력
            modified_repulsion = repulsion + influence
            prev_tension = (modified_repulsion ** 2).sum(dim=-1, keepdim=True)
            tensions.append(prev_tension.mean().item())

        # 최종 출력
        equilibrium = (out_plus + out_minus) / 2
        field_direction = self.field_transform(modified_repulsion)
        output = equilibrium + self.tension_scale * torch.sqrt(prev_tension + 1e-8) * field_direction

        # 보조 loss: 자기참조가 장력을 안정시키도록 유도
        # 장력 변화가 감소해야 함 (수렴) = 축소사상
        if len(tensions) >= 2:
            tension_changes = [abs(tensions[i+1] - tensions[i]) for i in range(len(tensions)-1)]
            convergence_loss = torch.tensor(sum(tension_changes) / len(tension_changes))
        else:
            convergence_loss = torch.tensor(0.0)

        entropy_loss = getattr(self.pole_minus, 'entropy_loss', torch.tensor(0.0))
        self.aux_loss = entropy_loss + 0.001 * convergence_loss

        # 모니터링
        with torch.no_grad():
            self.tension_history = tensions
            self.self_state_norm = self_state.norm(dim=-1).mean().item()

        return (output, self.aux_loss)


# ─────────────────────────────────────────
# 벤치마크
# ─────────────────────────────────────────

def main():
    print()
    print("=" * 65)
    print("   logout — 메타 엔진 벤치마크")
    print("   엔진 + 엔진 = 상위엔진")
    print("=" * 65)

    train_loader, test_loader = load_mnist()
    input_dim, hidden_dim, output_dim = 784, 48, 10
    epochs = 10
    results = {}

    # ── Baseline: Dense ──
    print("\n[Dense baseline]")
    model = DenseModel(input_dim, hidden_dim * 4, output_dim)
    losses, accs = train_and_evaluate(model, train_loader, test_loader, epochs)
    results['Dense'] = {'acc': accs[-1], 'loss': losses[-1], 'params': count_params(model)}

    # ── Baseline: Top-K MoE (8, k=2) ──
    print("\n[Top-K MoE (8 experts, k=2)]")
    model = BaseMoE(input_dim, hidden_dim, output_dim, 8,
                     TopKGate(input_dim, 8, 2))
    losses, accs = train_and_evaluate(model, train_loader, test_loader, epochs)
    results['Top-K MoE'] = {'acc': accs[-1], 'loss': losses[-1], 'params': count_params(model)}

    # ── 단일 엔진 A ──
    print("\n[Engine A: sigma,tau-MoE (12e, k=4)]")
    model = EngineA(input_dim, hidden_dim, output_dim)
    losses, accs = train_and_evaluate(model, train_loader, test_loader, epochs)
    results['Engine A'] = {'acc': accs[-1], 'loss': losses[-1], 'params': count_params(model)}

    # ── 단일 엔진 E ──
    print("\n[Engine E: Euler Product (2x3)]")
    model = EngineE(input_dim, hidden_dim, output_dim)
    losses, accs = train_and_evaluate(model, train_loader, test_loader, epochs)
    results['Engine E'] = {'acc': accs[-1], 'loss': losses[-1], 'params': count_params(model)}

    # ── DualBrain (A+G) ──
    print("\n[DualBrain: Left(A) + Right(G) + Corpus Callosum]")
    model = DualBrainEngine(input_dim, hidden_dim, output_dim)
    losses, accs = train_and_evaluate(model, train_loader, test_loader, epochs,
                                       aux_lambda=0.01)
    results['DualBrain (A+G)'] = {'acc': accs[-1], 'loss': losses[-1], 'params': count_params(model)}

    # ── MetaEngine (AEGF, 축소사상 라우팅) ──
    print("\n[MetaEngine: A+E+G+F (contraction routing)]")
    model = MetaEngine(input_dim, hidden_dim, output_dim,
                        engines='AEGF', routing='meta')
    losses, accs = train_and_evaluate(model, train_loader, test_loader, epochs,
                                       aux_lambda=0.01)
    results['Meta (AEGF)'] = {'acc': accs[-1], 'loss': losses[-1], 'params': count_params(model)}

    # ── MetaEngine (고정 가중치) ──
    print("\n[MetaEngine: A+E+G+F (fixed {1/2,1/3,1/6} weights)]")
    model = MetaEngine(input_dim, hidden_dim, output_dim,
                        engines='AEGF', routing='fixed')
    losses, accs = train_and_evaluate(model, train_loader, test_loader, epochs,
                                       aux_lambda=0.01)
    results['Meta fixed'] = {'acc': accs[-1], 'loss': losses[-1], 'params': count_params(model)}

    # ── Hierarchical (메타의 메타) ──
    print("\n[Hierarchical: (A+E) + (G+F) meta-combined]")
    model = HierarchicalMetaEngine(input_dim, hidden_dim, output_dim)
    losses, accs = train_and_evaluate(model, train_loader, test_loader, epochs,
                                       aux_lambda=0.01)
    results['Hierarchical'] = {'acc': accs[-1], 'loss': losses[-1], 'params': count_params(model)}

    # ── RepulsionField (2극: A vs G) ──
    print("\n[RepulsionField: Pole+(A) vs Pole-(G)]")
    model = RepulsionFieldEngine(input_dim, hidden_dim, output_dim)
    losses, accs = train_and_evaluate(model, train_loader, test_loader, epochs,
                                       aux_lambda=0.01)
    results['Repulsion (A|G)'] = {'acc': accs[-1], 'loss': losses[-1], 'params': count_params(model)}
    print(f"    Tension: {model.tension_magnitude:.4f}")

    # ── RepulsionFieldQuad (4극: A|G × E|F) ──
    print("\n[RepulsionFieldQuad: (A|G) x (E|F)]")
    model = RepulsionFieldQuad(input_dim, hidden_dim, output_dim)
    losses, accs = train_and_evaluate(model, train_loader, test_loader, epochs,
                                       aux_lambda=0.01)
    results['Repulsion Quad'] = {'acc': accs[-1], 'loss': losses[-1], 'params': count_params(model)}
    print(f"    Tension content: {model.tension_content:.4f}, structure: {model.tension_structure:.4f}")

    # ── SelfReferentialField (자기참조 반발력장) ──
    print("\n[SelfReferentialField: 장력을 관찰하는 엔진 (Phase 3)]")
    model = SelfReferentialField(input_dim, hidden_dim, output_dim, n_self_ref_steps=3)
    losses, accs = train_and_evaluate(model, train_loader, test_loader, epochs,
                                       aux_lambda=0.01)
    results['SelfRef Field'] = {'acc': accs[-1], 'loss': losses[-1], 'params': count_params(model)}
    print(f"    Tension history: {['%.1f' % t for t in model.tension_history]}")
    print(f"    Self-state norm: {model.self_state_norm:.4f}")
    converged = len(model.tension_history) >= 2 and abs(model.tension_history[-1] - model.tension_history[-2]) < abs(model.tension_history[1] - model.tension_history[0])
    print(f"    Tension converging: {'YES' if converged else 'NO'}")

    # ── 결과 비교 ──
    compare_results(results)

    print("\n" + "-" * 65)
    print("  핵심 질문: 엔진 조합이 단일 엔진보다 나은가?")
    print("  메타 > max(A, E) 이면 → 엔진 협력 효과 실증")
    print("-" * 65)

    single_best = max(results['Engine A']['acc'], results['Engine E']['acc'])
    meta_acc = results['Meta (AEGF)']['acc']
    dual_acc = results['DualBrain (A+G)']['acc']

    print(f"  단일 엔진 최고:     {single_best*100:.2f}%")
    print(f"  DualBrain (A+G):    {dual_acc*100:.2f}%  ({'+' if dual_acc > single_best else ''}{(dual_acc-single_best)*100:.2f}%)")
    print(f"  Meta (AEGF):        {meta_acc*100:.2f}%  ({'+' if meta_acc > single_best else ''}{(meta_acc-single_best)*100:.2f}%)")
    print()


if __name__ == '__main__':
    main()
