#!/usr/bin/env python3
"""TECS-L growth scanner -- JSON stdout, no external dependencies.

Modeled after anima/.growth/scan.py but tailored for the mathematical
theory foundation repo: hypotheses, calculators, atlas, characterizations,
CDO compliance.

Output: {"opportunities": [...], "growth_delta": N}
"""
import glob
import json
import os
import sys
import time

_THIS_DIR = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.normpath(os.path.join(_THIS_DIR, '..'))
_CALC_DIR = os.path.join(_ROOT, 'calc')
_HYPO_DIR = os.path.join(_ROOT, 'docs', 'hypotheses')
_SHARED_DIR = os.path.join(_ROOT, '.shared')
_ATLAS_PATH = os.path.join(_SHARED_DIR, 'math_atlas.json')
_PAPER_DIR = os.path.join(_ROOT, 'docs', 'paper')
_GROWTH_STATE = os.path.join(_THIS_DIR, 'growth_state.json')
_NEXUS6_BUS = os.path.join(os.environ.get('HOME', ''), 'Dev', 'nexus6',
                            'shared', 'growth_bus.jsonl')

# ---------------------------------------------------------------------------
# Scanners
# ---------------------------------------------------------------------------

def scan_unverified_hypotheses():
    """Find hypothesis files that lack a corresponding verification."""
    results = []
    if not os.path.isdir(_HYPO_DIR):
        return results
    try:
        hypo_files = glob.glob(os.path.join(_HYPO_DIR, '*.md'))
        unverified = []
        for hf in hypo_files:
            base = os.path.basename(hf)
            # Check if there is a verification companion
            vname = base.replace('hypotheses', 'verification').replace('hypothesis', 'verification')
            vpath = os.path.join(os.path.dirname(hf), vname)
            # Also check docs/<domain>/verification.md pattern
            if not os.path.exists(vpath):
                # Quick heuristic: look for VERIFIED / EXACT / FAIL markers inside
                try:
                    with open(hf) as f:
                        content = f.read(4096)
                    has_grade = any(g in content for g in ('EXACT', 'VERIFIED', 'FAIL', 'CLOSE', 'WEAK'))
                    if not has_grade:
                        unverified.append(base)
                except Exception:
                    unverified.append(base)
        if unverified:
            results.append({
                'type': 'UNVERIFIED_HYPOTHESES',
                'priority': 'HIGH',
                'description': f'{len(unverified)} unverified hypotheses in docs/hypotheses/',
                'count': len(unverified),
                'samples': unverified[:5],
                'growth_value': len(unverified),
            })
    except Exception:
        pass
    return results


def scan_missing_calculators():
    """Find calculator references in docs that point to non-existent calc/ files."""
    results = []
    missing = []
    try:
        # Scan .md files for calc/ references
        md_files = glob.glob(os.path.join(_ROOT, 'docs', '**', '*.md'), recursive=True)
        referenced = set()
        for mf in md_files[:200]:  # cap to avoid slowness
            try:
                with open(mf) as f:
                    content = f.read(8192)
                # Pattern: calc/something.py or calc/something.rs
                import re
                refs = re.findall(r'calc/([a-zA-Z0-9_-]+\.(?:py|rs))', content)
                referenced.update(refs)
            except Exception:
                pass

        for ref in referenced:
            full = os.path.join(_CALC_DIR, ref)
            if not os.path.exists(full):
                missing.append(ref)

        if missing:
            results.append({
                'type': 'MISSING_CALCULATORS',
                'priority': 'MEDIUM',
                'description': f'{len(missing)} referenced calculators not found in calc/',
                'count': len(missing),
                'samples': sorted(missing)[:5],
                'growth_value': len(missing),
            })
    except Exception:
        pass
    return results


def scan_atlas_gaps():
    """Check math_atlas.json for entries without verification status."""
    results = []
    if not os.path.exists(_ATLAS_PATH):
        return results
    try:
        atlas = json.load(open(_ATLAS_PATH))
        hypotheses = atlas.get('hypotheses', [])
        total = len(hypotheses)
        unverified = 0
        for h in hypotheses:
            grade = ''
            if isinstance(h, dict):
                grade = h.get('grade', h.get('status', ''))
            if not grade or grade in ('UNKNOWN', 'PENDING', ''):
                unverified += 1

        if unverified > 0:
            results.append({
                'type': 'ATLAS_GAPS',
                'priority': 'MEDIUM',
                'description': f'{unverified}/{total} atlas hypotheses without verification grade',
                'count': unverified,
                'total': total,
                'growth_value': min(unverified, 50),
            })
    except Exception:
        pass
    return results


def scan_stale_characterizations():
    """Find characterization files not updated in 30+ days."""
    results = []
    stale = []
    threshold = time.time() - 30 * 86400  # 30 days
    try:
        char_patterns = [
            os.path.join(_ROOT, 'docs', '**', 'characterization*.md'),
            os.path.join(_ROOT, 'docs', '**', '*-characterization.md'),
            os.path.join(_ROOT, 'docs', 'characterizations', '*.md'),
        ]
        char_files = set()
        for pat in char_patterns:
            char_files.update(glob.glob(pat, recursive=True))

        for cf in char_files:
            try:
                mtime = os.path.getmtime(cf)
                if mtime < threshold:
                    days_old = int((time.time() - mtime) / 86400)
                    stale.append((os.path.basename(cf), days_old))
            except Exception:
                pass

        if stale:
            stale.sort(key=lambda x: -x[1])
            results.append({
                'type': 'STALE_CHARACTERIZATIONS',
                'priority': 'LOW',
                'description': f'{len(stale)} characterizations not updated in 30+ days',
                'count': len(stale),
                'samples': [f'{name} ({days}d)' for name, days in stale[:5]],
                'growth_value': len(stale),
            })
    except Exception:
        pass
    return results


def scan_cdo_violations():
    """Check for CDO compliance issues: _meta missing, hardcoded constants, etc."""
    results = []
    violations = []
    try:
        # Check config JSONs for _meta
        json_files = glob.glob(os.path.join(_ROOT, 'config', '*.json'))
        json_files += glob.glob(os.path.join(_ROOT, '.shared', '*.json'))
        for jf in json_files[:50]:
            try:
                d = json.load(open(jf))
                if isinstance(d, dict) and '_meta' not in d and len(d) > 2:
                    violations.append(f'{os.path.basename(jf)}: missing _meta')
            except Exception:
                pass

        if violations:
            results.append({
                'type': 'CDO_VIOLATIONS',
                'priority': 'HIGH',
                'description': f'{len(violations)} CDO compliance issues',
                'count': len(violations),
                'samples': violations[:5],
                'growth_value': len(violations),
            })
    except Exception:
        pass
    return results


def scan_calculator_health():
    """Check calc/ files for syntax errors (Python) or compile readiness (Rust)."""
    results = []
    broken = []
    try:
        py_files = glob.glob(os.path.join(_CALC_DIR, '*.py'))
        for pf in py_files[:100]:
            try:
                with open(pf) as f:
                    source = f.read()
                compile(source, pf, 'exec')
            except SyntaxError:
                broken.append(os.path.basename(pf))

        if broken:
            results.append({
                'type': 'BROKEN_CALCULATORS',
                'priority': 'HIGH',
                'description': f'{len(broken)} calculators with syntax errors',
                'count': len(broken),
                'samples': broken[:5],
                'growth_value': len(broken),
            })
    except Exception:
        pass
    return results


def scan_paper_readiness():
    """Check paper drafts for completeness markers."""
    results = []
    if not os.path.isdir(_PAPER_DIR):
        return results
    try:
        papers = glob.glob(os.path.join(_PAPER_DIR, '*.md'))
        papers += glob.glob(os.path.join(_PAPER_DIR, '*.tex'))
        drafts = []
        for p in papers:
            try:
                with open(p) as f:
                    content = f.read(2048)
                if 'TODO' in content or 'DRAFT' in content or 'TBD' in content:
                    drafts.append(os.path.basename(p))
            except Exception:
                pass

        if drafts:
            results.append({
                'type': 'PAPER_DRAFTS',
                'priority': 'LOW',
                'description': f'{len(drafts)} paper drafts with TODOs',
                'count': len(drafts),
                'samples': drafts[:5],
                'growth_value': len(drafts),
            })
    except Exception:
        pass
    return results


def scan_discovery_potential():
    """Look for new constant patterns not yet in atlas."""
    results = []
    try:
        atlas = {}
        if os.path.exists(_ATLAS_PATH):
            atlas = json.load(open(_ATLAS_PATH))

        total_hypotheses = len(atlas.get('hypotheses', []))
        total_constants = len(atlas.get('constant_maps', []))

        # Check TECS-L specific stats
        stats = atlas.get('stats', {}).get('TECS-L', {})
        tecs_hypotheses = stats.get('hypotheses', 0) if isinstance(stats, dict) else 0

        calc_count = len(glob.glob(os.path.join(_CALC_DIR, '*.py')))
        calc_count += len(glob.glob(os.path.join(_CALC_DIR, '*.rs')))

        # Growth potential = hypotheses that could yield new constants
        if total_hypotheses > 0 and total_constants > 0:
            ratio = total_constants / total_hypotheses
            if ratio < 0.2:  # Less than 20% yield
                results.append({
                    'type': 'DISCOVERY_POTENTIAL',
                    'priority': 'MEDIUM',
                    'description': f'Constant yield {ratio:.1%} ({total_constants}/{total_hypotheses}) -- mining opportunity',
                    'growth_value': max(1, int((0.2 - ratio) * 100)),
                })
    except Exception:
        pass
    return results


# ---------------------------------------------------------------------------
# Growth state update + NEXUS-6 bus
# ---------------------------------------------------------------------------

def update_growth_state(opportunities):
    """Update .growth/growth_state.json with scan results."""
    if not os.path.exists(_GROWTH_STATE):
        return 0
    try:
        state = json.load(open(_GROWTH_STATE))
        growth_delta = sum(1 for o in opportunities if o.get('priority') in ('HIGH', 'MEDIUM'))
        # Add growth_value contributions
        for o in opportunities:
            gv = o.get('growth_value', 0)
            if gv > 0:
                growth_delta += max(1, gv // 10)

        if growth_delta > 0:
            prev = state.get('interaction_count', 0)
            state['interaction_count'] = prev + growth_delta

            # Stage transitions (seed -> sprout -> sapling -> tree -> forest)
            count = state['interaction_count']
            stages = [
                (4, 10000, 'forest'),
                (3, 2000, 'tree'),
                (2, 500, 'sapling'),
                (1, 100, 'sprout'),
            ]
            for idx, threshold, name in stages:
                if count >= threshold and state.get('stage_index', 0) < idx:
                    state['stage_index'] = idx
                    state['stage_name'] = name
                    break

            # Update stats
            state.setdefault('stats', {})
            state['stats']['hypotheses_total'] = sum(
                o.get('total', o.get('count', 0))
                for o in opportunities if 'HYPO' in o.get('type', '') or 'ATLAS' in o.get('type', '')
            )
            state['stats']['calcs_total'] = len(glob.glob(os.path.join(_CALC_DIR, '*.py'))) + \
                                             len(glob.glob(os.path.join(_CALC_DIR, '*.rs')))
            try:
                atlas = json.load(open(_ATLAS_PATH))
                state['stats']['atlas_entries'] = len(atlas.get('hypotheses', []))
            except Exception:
                pass
            state['stats']['discoveries'] = state['stats'].get('discoveries', 0)
            state['stats']['last_scan'] = time.strftime('%Y-%m-%dT%H:%M:%S')
            state['stats']['last_delta'] = growth_delta

            with open(_GROWTH_STATE, 'w') as f:
                json.dump(state, f, indent=2, ensure_ascii=False)

        return growth_delta
    except Exception:
        return 0


def emit_to_nexus6_bus(opportunities, growth_delta):
    """Append scan result to NEXUS-6 growth bus (jsonl)."""
    try:
        bus_dir = os.path.dirname(_NEXUS6_BUS)
        if os.path.isdir(bus_dir):
            entry = {
                'source': 'tecs-l',
                'timestamp': time.strftime('%Y-%m-%dT%H:%M:%S'),
                'opportunities': len(opportunities),
                'growth_delta': growth_delta,
                'types': list(set(o.get('type', '') for o in opportunities)),
            }
            with open(_NEXUS6_BUS, 'a') as f:
                f.write(json.dumps(entry, ensure_ascii=False) + '\n')
    except Exception:
        pass


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    scanners = [
        scan_unverified_hypotheses,
        scan_missing_calculators,
        scan_atlas_gaps,
        scan_stale_characterizations,
        scan_cdo_violations,
        scan_calculator_health,
        scan_paper_readiness,
        scan_discovery_potential,
    ]

    all_opps = []
    for scanner in scanners:
        try:
            all_opps.extend(scanner())
        except Exception:
            pass

    # Sort by priority
    prio_order = {'HIGH': 0, 'MEDIUM': 1, 'LOW': 2}
    all_opps.sort(key=lambda x: prio_order.get(x.get('priority', 'LOW'), 9))

    # Update state + emit to bus
    growth_delta = update_growth_state(all_opps)
    emit_to_nexus6_bus(all_opps, growth_delta)

    output = {
        'opportunities': all_opps,
        'growth_delta': growth_delta,
    }
    print(json.dumps(output, ensure_ascii=False))


if __name__ == '__main__':
    main()
