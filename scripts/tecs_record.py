#!/usr/bin/env python3
"""TECS-L Discovery Recorder — writes confirmed discoveries to atlas and hypothesis files."""

import json
import os
import sys
from datetime import datetime

TECS_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LOOP_STATE_PATH = os.path.join(TECS_ROOT, 'config', 'loop_state.json')
DISCOVERY_LOG = os.path.join(TECS_ROOT, 'config', 'discovery_log.jsonl')
HYPOTHESES_DIR = os.path.join(TECS_ROOT, 'docs', 'hypotheses')


def load_json(path):
    with open(path, 'r') as f:
        return json.load(f)


def save_json(path, data):
    with open(path, 'w') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def record_discoveries():
    """Move CONFIRMED discoveries from buffer to permanent storage."""
    state = load_json(LOOP_STATE_PATH)
    recorded = []
    remaining = []

    for disc in state['discovery_buffer']:
        if disc.get('grade') == 'CONFIRMED' and disc.get('validated'):
            # Append to discovery log (JSONL)
            with open(DISCOVERY_LOG, 'a') as f:
                f.write(json.dumps(disc, ensure_ascii=False) + '\n')

            recorded.append(disc)
        else:
            remaining.append(disc)

    state['discovery_buffer'] = remaining
    state['_meta']['updated'] = datetime.now().isoformat()
    save_json(LOOP_STATE_PATH, state)

    # Run atlas sync if discoveries were recorded
    if recorded:
        atlas_script = os.path.join(TECS_ROOT, '.shared', 'scan_math_atlas.py')
        if os.path.isfile(atlas_script):
            os.system(f'{sys.executable} {atlas_script} --save --summary 2>/dev/null')

    return {
        'recorded': len(recorded),
        'remaining_buffer': len(remaining),
        'total_in_log': sum(1 for _ in open(DISCOVERY_LOG)) if os.path.isfile(DISCOVERY_LOG) else 0,
    }


if __name__ == '__main__':
    result = record_discoveries()
    print(json.dumps(result, indent=2))
