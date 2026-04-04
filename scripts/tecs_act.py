#!/usr/bin/env python3
"""TECS-L Discovery Action — runs convergence/proof engine on target domain."""

import json
import os
import sys
import subprocess
from datetime import datetime

TECS_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(TECS_ROOT, '.shared'))

LOOP_STATE_PATH = os.path.join(TECS_ROOT, 'config', 'loop_state.json')
REGISTRY_PATH = os.path.join(TECS_ROOT, 'config', 'domain_registry.json')

# Mode → convergence_engine strategy mapping
MODE_STRATEGY = {
    'dfs': '1',        # S1: Open Search DFS
    'pair': '2',       # S2: Pair Scan
    'backtrack': '3',  # S3: Target Backtrack
}


def load_json(path):
    with open(path, 'r') as f:
        return json.load(f)


def save_json(path, data):
    with open(path, 'w') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def run_convergence_engine(domain_code, mode):
    """Run convergence_engine.py with specified strategy and domain filter."""
    engine_path = os.path.join(TECS_ROOT, '.shared', 'convergence_engine.py')
    if not os.path.isfile(engine_path):
        return {'success': False, 'error': 'convergence_engine.py not found'}

    strategy = MODE_STRATEGY.get(mode, '1')
    cmd = [
        sys.executable, engine_path,
        '--strategy', strategy,
        '--domain', domain_code,
        '--max-results', '10',
        '--json-output',
    ]
    try:
        result = subprocess.run(
            cmd, capture_output=True, text=True, timeout=120,
            cwd=TECS_ROOT
        )
        if result.returncode == 0 and result.stdout.strip():
            try:
                findings = json.loads(result.stdout.strip())
                return {'success': True, 'findings': findings}
            except json.JSONDecodeError:
                # Engine may output non-JSON — parse lines as discoveries
                lines = [l.strip() for l in result.stdout.strip().split('\n') if l.strip()]
                return {'success': True, 'findings': lines}
        else:
            return {
                'success': False,
                'error': result.stderr[:500] if result.stderr else 'no output',
            }
    except subprocess.TimeoutExpired:
        return {'success': False, 'error': 'timeout (120s)'}
    except Exception as e:
        return {'success': False, 'error': str(e)}


def run_proof_engine(domain_code):
    """Run proof_engine.py to tier-classify unverified hypotheses."""
    engine_path = os.path.join(TECS_ROOT, '.shared', 'proof_engine.py')
    if not os.path.isfile(engine_path):
        return {'success': False, 'error': 'proof_engine.py not found'}

    cmd = [
        sys.executable, engine_path,
        '--domain', domain_code,
        '--json-output',
    ]
    try:
        result = subprocess.run(
            cmd, capture_output=True, text=True, timeout=120,
            cwd=TECS_ROOT
        )
        if result.returncode == 0 and result.stdout.strip():
            try:
                return {'success': True, 'proofs': json.loads(result.stdout.strip())}
            except json.JSONDecodeError:
                lines = [l.strip() for l in result.stdout.strip().split('\n') if l.strip()]
                return {'success': True, 'proofs': lines}
        return {'success': False, 'error': result.stderr[:500] if result.stderr else 'no output'}
    except subprocess.TimeoutExpired:
        return {'success': False, 'error': 'timeout (120s)'}
    except Exception as e:
        return {'success': False, 'error': str(e)}


def act(domain_code, mode):
    """Execute discovery action on target domain with current mode."""
    state = load_json(LOOP_STATE_PATH)

    # Run both engines
    conv_result = run_convergence_engine(domain_code, mode)
    proof_result = run_proof_engine(domain_code)

    discoveries = []
    now = datetime.now().isoformat()

    if conv_result['success'] and conv_result.get('findings'):
        findings = conv_result['findings']
        if isinstance(findings, list):
            for f in findings[:6]:  # cap at n=6
                discoveries.append({
                    'type': 'convergence',
                    'domain': domain_code,
                    'content': f if isinstance(f, str) else json.dumps(f),
                    'timestamp': now,
                    'mode': mode,
                    'validated': False,
                })

    if proof_result['success'] and proof_result.get('proofs'):
        proofs = proof_result['proofs']
        if isinstance(proofs, list):
            for p in proofs[:6]:
                discoveries.append({
                    'type': 'proof',
                    'domain': domain_code,
                    'content': p if isinstance(p, str) else json.dumps(p),
                    'timestamp': now,
                    'mode': mode,
                    'validated': False,
                })

    # Update state
    if discoveries:
        state['loop']['consecutive_failures'] = 0
        state['discovery_buffer'].extend(discoveries)
    else:
        state['loop']['consecutive_failures'] += 1

    state['loop']['cycle'] += 1
    state['loop']['last_run'] = now
    state['_meta']['updated'] = now

    # Mode rotation on stagnation
    reg = load_json(REGISTRY_PATH)
    domain_data = reg['domains'].get(domain_code, {})
    stagnant = domain_data.get('stagnant_cycles', 0)
    if not discoveries:
        domain_data['stagnant_cycles'] = stagnant + 1
        if domain_data['stagnant_cycles'] >= state['mode_stagnation_trigger']:
            modes = state['mode_rotation']
            current_idx = modes.index(state['loop']['mode']) if state['loop']['mode'] in modes else 0
            state['loop']['mode'] = modes[(current_idx + 1) % len(modes)]
            domain_data['stagnant_cycles'] = 0
    else:
        domain_data['stagnant_cycles'] = 0
    reg['domains'][domain_code] = domain_data
    save_json(REGISTRY_PATH, reg)

    save_json(LOOP_STATE_PATH, state)

    return {
        'discoveries': len(discoveries),
        'cycle': state['loop']['cycle'],
        'mode': state['loop']['mode'],
        'consecutive_failures': state['loop']['consecutive_failures'],
        'buffer_size': len(state['discovery_buffer']),
    }


if __name__ == '__main__':
    domain = sys.argv[1] if len(sys.argv) > 1 else 'N'
    mode = sys.argv[2] if len(sys.argv) > 2 else 'dfs'
    result = act(domain, mode)
    print(json.dumps(result, indent=2))
