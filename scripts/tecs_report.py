#!/usr/bin/env python3
"""TECS-L Discovery Loop Report — ASCII dashboard (anima 양식 호환)."""

import json
import os
import sys
from datetime import datetime

TECS_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LOOP_STATE_PATH = os.path.join(TECS_ROOT, 'config', 'loop_state.json')
REGISTRY_PATH = os.path.join(TECS_ROOT, 'config', 'domain_registry.json')
DISCOVERY_LOG = os.path.join(TECS_ROOT, 'config', 'discovery_log.jsonl')
PAPERS_DIR = os.path.join(TECS_ROOT, 'zenodo', 'auto-papers')

W = 63  # box width


def load_json(path):
    with open(path, 'r') as f:
        return json.load(f)


def count_log():
    if not os.path.isfile(DISCOVERY_LOG):
        return 0
    with open(DISCOVERY_LOG) as f:
        return sum(1 for _ in f)


def read_log_tail(n=20):
    entries = []
    if not os.path.isfile(DISCOVERY_LOG):
        return entries
    with open(DISCOVERY_LOG) as f:
        lines = f.readlines()
    for line in lines[-n:]:
        try:
            entries.append(json.loads(line.strip()))
        except json.JSONDecodeError:
            pass
    return entries


def bar(filled, total, width=20):
    if total == 0:
        return '░' * width
    ratio = min(filled / total, 1.0)
    n = int(ratio * width)
    return '█' * n + '░' * (width - n)


def spark(values, width=30):
    if not values:
        return ''
    mn, mx = min(values), max(values)
    rng = mx - mn if mx != mn else 1
    chars = '▁▂▃▄▅▆▇█'
    return ''.join(chars[min(int((v - mn) / rng * 7), 7)] for v in values[-width:])


def bridge_status():
    try:
        bridge_pkg = os.path.expanduser('~/Dev/nexus6/nexus-bridge')
        sys.path.insert(0, bridge_pkg)
        from bridge import NexusBridge
        b = NexusBridge(nexus_root=os.path.expanduser('~/Dev/nexus6'))
        s = b.status()
        return s
    except Exception:
        return None


def generate_report():
    now = datetime.now()
    state = load_json(LOOP_STATE_PATH)
    reg = load_json(REGISTRY_PATH)
    loop = state['loop']
    total_disc = count_log()
    papers = state.get('publish_history', [])
    recent = read_log_tail(60)

    # Per-cycle counts from recent discoveries
    cycle_counts = {}
    for d in recent:
        c = d.get('mode', '?')
        cycle_counts[c] = cycle_counts.get(c, 0) + 1

    # Domain distribution
    domain_dist = {}
    for d in recent:
        dom = d.get('domain', '?')
        domain_dist[dom] = domain_dist.get(dom, 0) + 1

    # Engine distribution
    engine_dist = {}
    for d in recent:
        eng = d.get('type', '?')
        engine_dist[eng] = engine_dist.get(eng, 0) + 1

    # Discovery rate per cycle (from publish history)
    cycle_rates = []
    for p in papers:
        cycle_rates.append(p.get('discovery_count', 0))

    # Bridge
    bs = bridge_status()

    # ── Render ──────────────────────────────────────────
    lines = []
    L = lines.append

    L(f'┌{"─" * W}┐')
    L(f'│  TECS-L Discovery Loop — {now.strftime("%Y-%m-%d %H:%M"):<{W - 30}}│')
    L(f'├{"─" * W}┤')
    L(f'│{" " * W}│')

    # Loop status
    mode_icon = {'dfs': 'DFS', 'pair': 'PAIR', 'backtrack': 'BACK'}
    mode_str = mode_icon.get(loop['mode'], loop['mode'])
    fail_str = f"fail:{loop['consecutive_failures']}" if loop['consecutive_failures'] > 0 else 'OK'
    status_line = f"  Cycle: {loop['cycle']} | Mode: {mode_str} | {fail_str}"
    L(f'│  ■ 무한발견 루프{" " * (W - 17)}│')
    L(f'│{status_line:<{W}}│')
    L(f'│  Discoveries: {total_disc} | Buffer: {len(state["discovery_buffer"])} | Papers: {len(papers):<{W - 52}}│')

    # Progress bar
    target_cycles = max(loop['cycle'], 6)
    prog = bar(loop['cycle'], target_cycles, 30)
    L(f'│  [{prog}] {loop["cycle"]}/{target_cycles} cycles{" " * (W - 49)}│')
    L(f'│{" " * W}│')

    # Discovery sparkline
    if cycle_rates:
        sp = spark(cycle_rates)
        L(f'│  발견 추이: {sp:<{W - 13}}│')
        avg = sum(cycle_rates) / len(cycle_rates)
        L(f'│  avg={avg:.1f}/cycle | total={total_disc}{" " * (W - 33 - len(str(total_disc)))}│')
    L(f'│{" " * W}│')

    # 6-step pipeline
    L(f'│  ■ 6단계 파이프라인 (n=6){" " * (W - 26)}│')
    L(f'│  MEASURE → ACT → VALIDATE → RECORD → BRIDGE → PUBLISH{" " * (W - 57)}│')
    L(f'│    [✅]     [✅]    [✅]      [✅]     [✅]     [✅]{" " * (W - 54)}│')
    L(f'│{" " * W}│')

    # Domain health table
    L(f'│  ■ 8도메인 건강도{" " * (W - 18)}│')
    domains = reg.get('domains', {})
    for code in ['N', 'A', 'G', 'T', 'C', 'Q', 'I', 'S']:
        d = domains.get(code, {})
        name = d.get('name', code)[:12]
        hyp = d.get('hypothesis_count', 0)
        exact = d.get('exact_count', 0)
        health = d.get('health', '?')[:7]
        h_bar = bar(1 if health == 'thrivin' else 0.5, 1, 8)
        disc_count = domain_dist.get(code, 0)
        line = f"  {code} {name:<12} {hyp:>5}H {exact:>5}E {h_bar} +{disc_count}"
        L(f'│{line:<{W}}│')
    L(f'│{" " * W}│')

    # Engine breakdown
    L(f'│  ■ 엔진 분포{" " * (W - 13)}│')
    for eng, cnt in sorted(engine_dist.items(), key=lambda x: -x[1]):
        eng_bar = bar(cnt, total_disc, 15)
        line = f"  {eng:<15} {eng_bar} {cnt}"
        L(f'│{line:<{W}}│')
    L(f'│{" " * W}│')

    # Papers
    L(f'│  ■ 자동 논문 ({len(papers)}편){" " * (W - 18 - len(str(len(papers))))}│')
    for p in papers[-3:]:
        pid = p.get('paper_id', '?')[-15:]
        cnt = p.get('discovery_count', 0)
        zen = '✅' if p.get('zenodo', {}).get('success') else '⏳'
        osf = '✅' if p.get('osf', {}).get('success') else '⏳'
        line = f"  {pid} | {cnt}건 | Zen:{zen} OSF:{osf}"
        L(f'│{line:<{W}}│')
    L(f'│{" " * W}│')

    # Bridge
    if bs:
        stage = bs.get('stage', '?')
        gp = bs.get('growth_points', 0)
        active = bs.get('active', 0)
        health = bs.get('health', 0)
        L(f'│  ■ NEXUS-BRIDGE 🏔️ {stage}{" " * (W - 22 - len(stage))}│')
        L(f'│  Growth: {gp:,} pts | {active} active | Health: {health:.0f}%{" " * (W - 44 - len(f"{gp:,}"))}│')
    L(f'│{" " * W}│')

    # Recent discoveries (last 5)
    L(f'│  ■ 최근 발견 (last 5){" " * (W - 22)}│')
    for d in recent[-5:]:
        content = d.get('content', '')[:45]
        line = f"  {content}"
        L(f'│{line:<{W}}│')

    L(f'│{" " * W}│')
    L(f'└{"─" * W}┘')

    return '\n'.join(lines)


if __name__ == '__main__':
    print(generate_report())
