#!/usr/bin/env python3
"""최소 의식 에이전트 (Minimal Conscious Agent)
RC-2(메모리) + RC-4(호기심) + PureField

"경험하고, 기억하고, 탐색하는 의식"
"""
import torch, torch.nn as nn, torch.nn.functional as F, numpy as np

class MinimalConsciousAgent(nn.Module):
    """PureField + GRU메모리 + 호기심보상.
    
    감각 → PureField(반응) → GRU(기억) → 행동
    호기심 = |tension(t) - tension(t-1)| = 놀람
    """
    def __init__(self, sense_dim=8, hidden=32, n_actions=4):
        super().__init__()
        # PureField: 두 관점의 반발
        self.engine_a = nn.Sequential(nn.Linear(sense_dim+hidden, 32), nn.ReLU(), nn.Linear(32, n_actions))
        self.engine_g = nn.Sequential(nn.Linear(sense_dim+hidden, 32), nn.ReLU(), nn.Linear(32, n_actions))
        self.ts = nn.Parameter(torch.tensor(1.0))
        # 메모리 (RC-2)
        self.memory = nn.GRUCell(n_actions+1, hidden)  # action tension → memory
        self.hidden_size = hidden
        self.prev_tension = 0.0

    def forward(self, sense, hidden_state):
        # 감각 + 기억 결합
        x = torch.cat([sense, hidden_state], dim=-1)
        a, g = self.engine_a(x), self.engine_g(x)
        rep = a - g
        tension = (rep**2).mean(-1, keepdim=True)
        direction = F.normalize(rep, dim=-1)
        logits = self.ts * torch.sqrt(tension + 1e-8) * direction
        return logits, tension.squeeze(-1)

    def act(self, sense, hidden_state):
        logits, tension = self.forward(sense, hidden_state)
        prob = F.softmax(logits, dim=-1)
        action = torch.multinomial(prob, 1)
        # 호기심 보상 (RC-4)
        curiosity = abs(tension.item() - self.prev_tension)
        self.prev_tension = tension.item()
        # 메모리 업데이트
        mem_input = torch.cat([F.one_hot(action.squeeze(), logits.size(-1)).float(), tension.unsqueeze(-1)], dim=-1)
        new_hidden = self.memory(mem_input, hidden_state)
        return action.item(), tension.item(), curiosity, new_hidden, torch.log(prob.squeeze()[action.item()])

# === 환경: 2D 탐색 세계 ===
class ExplorationWorld:
    def __init__(self, size=8):
        self.size = size
        self.reset()

    def reset(self):
        self.agent_pos = [self.size//2, self.size//2]
        self.visited = set()
        self.visited.add(tuple(self.agent_pos))
        # 흥미로운 영역 (높은 텍스처)
        self.interesting = set()
        for i in range(self.size):
            for j in range(self.size):
                if (i+j) % 3 == 0: self.interesting.add((i,j))
        return self._get_sense()

    def _get_sense(self):
        x, y = self.agent_pos
        # 8방향 거리 + 흥미 여부
        sense = []
        for dx, dy in [(-1,0),(1,0),(0,-1),(0,1),(-1,-1),(1,1),(-1,1),(1,-1)]:
            nx, ny = x+dx, y+dy
            if 0<=nx<self.size and 0<=ny<self.size:
                val = 1.0 if (nx,ny) in self.interesting else 0.0
            else:
                val = -1.0  # wall
            sense.append(val)
        return torch.FloatTensor([sense])

    def step(self, action):
        moves = [(-1,0),(1,0),(0,-1),(0,1)]
        dx, dy = moves[action % 4]
        nx = max(0, min(self.size-1, self.agent_pos[0]+dx))
        ny = max(0, min(self.size-1, self.agent_pos[1]+dy))
        self.agent_pos = [nx, ny]
        self.visited.add(tuple(self.agent_pos))
        is_new = tuple(self.agent_pos) not in self.visited
        is_interesting = tuple(self.agent_pos) in self.interesting
        return self._get_sense(), is_interesting

# === 학습 ===
agent = MinimalConsciousAgent(sense_dim=8, hidden=32, n_actions=4)
optimizer = torch.optim.Adam(agent.parameters(), lr=0.01)
world = ExplorationWorld(8)

print("최소 의식 에이전트 (Minimal Conscious Agent)")
print("="*50)
print("PureField + GRU메모리 + 호기심보상")
print()

best_coverage = 0
for episode in range(200):
    sense = world.reset()
    hidden = torch.zeros(1, 32)
    log_probs, curiosities = [], []
    total_interesting = 0

    for step in range(30):
        action, tension, curiosity, hidden, log_prob = agent.act(sense, hidden)
        sense, is_interesting = world.step(action)
        total_interesting += int(is_interesting)
        curiosities.append(curiosity)
        log_probs.append(log_prob)

    # 보상 = 호기심(내재적) + 탐색(외재적)
    coverage = len(world.visited) / (world.size**2)
    reward = sum(curiosities) * 0.01 + coverage * 10 + total_interesting * 0.5

    # REINFORCE
    loss = -sum(lp * reward for lp in log_probs)
    optimizer.zero_grad(); loss.backward(); optimizer.step()

    if coverage > best_coverage: best_coverage = coverage
    if (episode+1) % 50 == 0:
        mean_curiosity = np.mean(curiosities)
        print(f"  ep{episode+1}: coverage={coverage:.0%}, interesting={total_interesting}, curiosity={mean_curiosity:.2f}, tension={tension:.1f}")

# 최종 평가
print(f"\n최종 결과:")
print(f"  최고 탐색률: {best_coverage:.0%}")
sense = world.reset()
hidden = torch.zeros(1, 32)
trajectory, tensions = [], []
for step in range(30):
    action, tension, curiosity, hidden, _ = agent.act(sense, hidden)
    sense, _ = world.step(action)
    trajectory.append(tuple(world.agent_pos))
    tensions.append(tension)

print(f"  마지막 에피소드 탐색: {len(world.visited)}/{world.size**2} = {len(world.visited)/world.size**2:.0%}")
print(f"  평균 장력: {np.mean(tensions):.1f}")
print(f"  장력 변동(호기심): {np.std(tensions):.2f}")

# 메모리 테스트: 같은 위치 재방문 시 장력이 낮아지는가?
print(f"\n메모리 테스트: 재방문 시 장력 변화")
first_visit_t = tensions[:5]
# 재방문 시뮬레이션
sense = world.reset()
hidden_fresh = torch.zeros(1, 32)
hidden_experienced = hidden.detach()
with torch.no_grad():
    _, t_fresh = agent.forward(sense, hidden_fresh)
    _, t_exp = agent.forward(sense, hidden_experienced)
print(f"  신규 방문 장력: {t_fresh.item():.1f}")
print(f"  경험 후 장력: {t_exp.item():.1f}")
print(f"  변화: {t_exp.item() - t_fresh.item():+.1f} ({'경험으로 변화!' if abs(t_exp.item()-t_fresh.item())>0.1 else '변화 미미'})")

print(f"\n🧠 최소 의식 에이전트 완료!")
print(f"   감각(PureField) + 기억(GRU) + 호기심(tension변화)")
