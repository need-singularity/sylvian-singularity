#!/usr/bin/env python3
"""Math Atlas — Hypothesis Markdown Parser.

Parses hypothesis markdown files from TECS-L, anima, SEDI repos
and extracts structured metadata (id, title, grade, refs, etc.).
"""

import re
import json
import sys
import sqlite3
import argparse
from pathlib import Path
from datetime import datetime

# ── Grade emojis (detection order matters) ──────────────────────────
GRADE_EMOJIS = ["\u2b50", "\U0001f7e9", "\U0001f7e7", "\U0001f7e6", "\U0001f7e8", "\U0001f7e5", "\U0001f7ea", "\u26aa", "\u2b1b", "\u2605", "\u26a1", "\u2705"]


def _parse_yaml_frontmatter(text):
    """Extract YAML frontmatter as a dict (simple key: value parsing)."""
    m = re.match(r'^---\n(.*?)\n---', text, re.DOTALL)
    if not m:
        return {}
    result = {}
    for line in m.group(1).splitlines():
        km = re.match(r'^(\w[\w-]*):\s*"?([^"]*)"?\s*$', line.strip())
        if km:
            result[km.group(1)] = km.group(2).strip()
    return result


def _extract_grade(text, yaml, title_line):
    """Extract grade with priority: YAML > ## Grade > **Grade:**/**Status:** > title emoji > title checkmark."""
    # Priority 1: YAML frontmatter
    if yaml.get("grade"):
        return yaml["grade"]

    # Priority 2: ## Grade: line
    m = re.search(r'^##\s*Grade:\s*(.+)', text, re.MULTILINE)
    if m:
        grade_text = m.group(1).strip()
        emojis = _extract_emoji_run(grade_text)
        if emojis:
            return emojis
        return grade_text

    # Priority 3: **Grade:** or **Status:** line
    m = re.search(r'\*\*(?:Grade|Status):\s*(.+?)(?:\*\*|$)', text, re.MULTILINE)
    if m:
        grade_text = m.group(1).strip()
        emojis = _extract_emoji_run(grade_text)
        if emojis:
            return emojis
        return grade_text

    # Priority 4: Emoji in title
    if title_line:
        emojis = _extract_emoji_run(title_line)
        if emojis:
            return emojis

    # Priority 5: Checkmark in title
    if title_line and "\u2705" in title_line:
        return "\u2705"

    return None


def _extract_emoji_run(text):
    """Extract a contiguous run of grade emojis from text."""
    result = []
    i = 0
    started = False
    while i < len(text):
        matched = False
        for emoji in GRADE_EMOJIS:
            if text[i:].startswith(emoji):
                result.append(emoji)
                i += len(emoji)
                matched = True
                started = True
                break
        if not matched:
            if started:
                break
            i += 1
    return "".join(result) if result else None


def _extract_refs(text):
    """Extract cross-references: related hypothesis numbers and H-XX-NNN patterns."""
    refs = []

    # Pattern: "Related hypotheses: 041(Name), 055(Name)"
    m = re.search(r'[Rr]elated\s+hypothes[ei]s?:\s*(.+)', text)
    if m:
        for num_match in re.finditer(r'(\d{2,4})\s*\(', m.group(1)):
            refs.append(num_match.group(1))

    # Pattern: inline "(H-XX-NNN)" references
    for m in re.finditer(r'\(H-([A-Z]+)-(\d+)\)', text):
        refs.append(f"H-{m.group(1)}-{m.group(2)}")

    return refs


def _extract_gz_dependency(text):
    """Extract Golden Zone dependency flag."""
    m = re.search(r'\*\*Golden Zone dependency:\*\*\s*(.+)', text)
    if not m:
        return None
    value = m.group(1).strip().upper()
    if value.startswith("NONE") or value.startswith("NO"):
        return False
    if value.startswith("YES"):
        return True
    return None


def _extract_domain(hid):
    """Extract domain from H-XX-NNN style ID."""
    m = re.match(r'H-([A-Z]+)-', hid)
    if m:
        return m.group(1)
    return None


def parse_hypothesis_md(text, repo, filepath):
    """Parse a hypothesis markdown file and return structured metadata.

    Args:
        text: Full markdown text content.
        repo: Repository name (TECS-L, anima, SEDI).
        filepath: Relative file path within repo.

    Returns:
        dict with keys: id, title, repo, domain, grade, refs, gz_dependent, filepath
    """
    yaml = _parse_yaml_frontmatter(text)
    stem = Path(filepath).stem  # filename without extension

    # Try to find the first H1 heading
    title_match = re.search(r'^#\s+(.+)', text, re.MULTILINE)
    title_line = title_match.group(1).strip() if title_match else ""

    hid = None
    title = None
    domain = None

    # Pattern A: "Hypothesis Review NNN: Title"
    m = re.match(r'Hypothesis\s+Review\s+(\d+):\s*(.+)', title_line)
    if m:
        hid = m.group(1)
        title = m.group(2).strip()

    # Pattern B: "Hypothesis NNN: Title"
    if not hid:
        m = re.match(r'Hypothesis\s+(\d+):\s*(.+)', title_line)
        if m:
            hid = m.group(1)
            title = m.group(2).strip()

    # Pattern C: "H-XX-NNN: Title"
    if not hid:
        m = re.match(r'(H-[A-Z]+-\d+):\s*(.+)', title_line)
        if m:
            hid = m.group(1)
            title = m.group(2).strip()
            domain = _extract_domain(hid)

    # Pattern E: "Frontier NNN: Title"
    if not hid:
        m = re.match(r'Frontier\s+(\d+):\s*(.+)', title_line)
        if m:
            hid = f"F-{m.group(1)}"
            title = m.group(2).strip()

    # Pattern D: YAML frontmatter id field
    if yaml.get("id"):
        yaml_id = yaml["id"]
        if not hid or hid == yaml_id:
            hid = yaml_id
            domain = _extract_domain(yaml_id)
        if not title and yaml.get("title"):
            title = yaml["title"]

    # Fallback: no pattern matched
    if not hid:
        hid = stem
        title = title_line if title_line else stem

    if not title:
        title = title_line

    # Build full qualified ID
    full_id = f"{repo}:{hid}"

    grade = _extract_grade(text, yaml, title_line)
    refs = _extract_refs(text)
    gz_dependent = _extract_gz_dependency(text)

    return {
        "id": full_id,
        "title": title,
        "repo": repo,
        "domain": domain,
        "grade": grade,
        "refs": refs,
        "gz_dependent": gz_dependent,
        "filepath": filepath,
    }


def parse_anima_recommender(source):
    """Parse anima's HYPOTHESIS_DB Python source and extract hypothesis entries.

    Args:
        source: Python source code containing HYPOTHESIS_DB list.

    Returns:
        list of dicts with keys: id, title, code, category, description, grade
    """
    results = []
    for m in re.finditer(r'Hypothesis\(\s*(.*?)\s*\)', source, re.DOTALL):
        block = m.group(1)
        entry = {}

        for field in ("code", "name", "category", "description"):
            fm = re.search(rf'{field}\s*=\s*"([^"]*)"', block)
            if fm:
                entry[field] = fm.group(1)

        fm = re.search(r'expected_phi\s*=\s*([\d.]+)', block)
        if fm:
            entry["expected_phi"] = float(fm.group(1))

        code = entry.get("code", "???")
        results.append({
            "id": f"anima:{code}",
            "title": entry.get("name", ""),
            "code": code,
            "category": entry.get("category"),
            "description": entry.get("description"),
            "grade": None,
        })

    return results


# ── Repo scan configuration ──────────────────────────────────────

BASE = Path(__file__).resolve().parent.parent  # TECS-L root
DEV = BASE.parent  # ~/Dev

REPO_SCANS = [
    {
        "name": "TECS-L",
        "root": BASE,
        "hypothesis_dirs": ["docs/hypotheses", "math/docs/hypotheses"],
    },
    {
        "name": "SEDI",
        "root": DEV / "SEDI",
        "hypothesis_dirs": ["docs/hypotheses"],
    },
    {
        "name": "anima",
        "root": DEV / "anima",
        "hypothesis_dirs": [],
        "python_sources": ["hypothesis_recommender.py"],
    },
]


def _scan_md_dir(repo_name, repo_root, rel_dir):
    """Scan a directory for *.md files and parse each as a hypothesis.

    Args:
        repo_name: Repository name (TECS-L, SEDI, anima).
        repo_root: Path to the repository root.
        rel_dir: Relative directory path within the repo.

    Returns:
        list of parsed hypothesis dicts.
    """
    results = []
    dirpath = repo_root / rel_dir
    if not dirpath.is_dir():
        return results
    for mdfile in sorted(dirpath.glob("*.md")):
        try:
            text = mdfile.read_text(encoding="utf-8", errors="replace")
        except (OSError, IOError):
            continue
        filepath = str(mdfile.relative_to(repo_root))
        h = parse_hypothesis_md(text, repo_name, filepath)
        results.append(h)
    return results


def _scan_anima_python(repo_root, source_file):
    """Read and parse an anima Python source file.

    Args:
        repo_root: Path to the anima repository root.
        source_file: Relative path to the Python source.

    Returns:
        list of parsed hypothesis dicts (anima format).
    """
    fpath = repo_root / source_file
    if not fpath.is_file():
        return []
    try:
        text = fpath.read_text(encoding="utf-8", errors="replace")
    except (OSError, IOError):
        return []
    entries = parse_anima_recommender(text)
    # Normalize anima entries to match MD hypothesis shape
    results = []
    for e in entries:
        results.append({
            "id": e["id"],
            "title": e["title"],
            "repo": "anima",
            "domain": e.get("category"),
            "grade": e.get("grade"),
            "refs": [],
            "gz_dependent": None,
            "filepath": source_file,
        })
    return results


def build_atlas():
    """Scan all repos and build a unified atlas of hypotheses.

    Returns:
        dict with keys: version, generated, stats, total, hypotheses
    """
    all_hypotheses = []
    stats = {}

    for repo_cfg in REPO_SCANS:
        name = repo_cfg["name"]
        root = repo_cfg["root"]
        repo_count = 0

        # Scan markdown hypothesis directories
        for rel_dir in repo_cfg.get("hypothesis_dirs", []):
            entries = _scan_md_dir(name, root, rel_dir)
            all_hypotheses.extend(entries)
            repo_count += len(entries)

        # Scan Python sources (anima)
        for src in repo_cfg.get("python_sources", []):
            entries = _scan_anima_python(root, src)
            all_hypotheses.extend(entries)
            repo_count += len(entries)

        stats[name] = repo_count

    # Deduplicate by ID (keep first occurrence)
    seen = set()
    unique = []
    for h in all_hypotheses:
        if h["id"] not in seen:
            seen.add(h["id"])
            unique.append(h)

    return {
        "version": "1.0",
        "generated": datetime.now().isoformat(timespec="seconds"),
        "stats": stats,
        "total": len(unique),
        "hypotheses": unique,
    }


# ── SQLite output ────────────────────────────────────────────────

def write_sqlite(atlas, dbpath):
    """Write atlas data to a SQLite database.

    Creates tables:
        hypotheses: id (PK), repo, file, title, grade, domain, gz_dependent, refs (JSON)
        edges: source_id, target_id, relation

    Args:
        atlas: dict returned by build_atlas().
        dbpath: Path to the SQLite database file.
    """
    conn = sqlite3.connect(dbpath)
    cur = conn.cursor()

    cur.execute("DROP TABLE IF EXISTS hypotheses")
    cur.execute("DROP TABLE IF EXISTS edges")

    cur.execute("""
        CREATE TABLE hypotheses (
            id TEXT PRIMARY KEY,
            repo TEXT,
            file TEXT,
            title TEXT,
            grade TEXT,
            domain TEXT,
            gz_dependent INTEGER,
            refs TEXT
        )
    """)
    cur.execute("""
        CREATE TABLE edges (
            source_id TEXT,
            target_id TEXT,
            relation TEXT
        )
    """)

    cur.execute("CREATE INDEX idx_repo ON hypotheses(repo)")
    cur.execute("CREATE INDEX idx_grade ON hypotheses(grade)")
    cur.execute("CREATE INDEX idx_domain ON hypotheses(domain)")

    # Insert hypotheses
    for h in atlas["hypotheses"]:
        gz = None
        if h["gz_dependent"] is True:
            gz = 1
        elif h["gz_dependent"] is False:
            gz = 0
        cur.execute(
            "INSERT INTO hypotheses VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            (h["id"], h["repo"], h["filepath"], h["title"],
             h["grade"], h["domain"], gz, json.dumps(h["refs"])),
        )

    # Build ID lookup: short_id -> full_id (for resolving refs)
    id_lookup = {}
    for h in atlas["hypotheses"]:
        full_id = h["id"]
        # e.g. "TECS-L:056" -> short "056", "TECS-L:H-CX-215" -> short "H-CX-215"
        short = full_id.split(":", 1)[1] if ":" in full_id else full_id
        # Map short -> full (first wins for collisions)
        if short not in id_lookup:
            id_lookup[short] = full_id

    # Build edges from refs
    for h in atlas["hypotheses"]:
        source = h["id"]
        for ref in h.get("refs", []):
            target = id_lookup.get(ref)
            if target and target != source:
                cur.execute(
                    "INSERT INTO edges VALUES (?, ?, ?)",
                    (source, target, "ref"),
                )

    conn.commit()
    conn.close()


# ── Graphviz DOT output ──────────────────────────────────────────

REPO_COLORS = {
    "TECS-L": "#4A90D9",
    "SEDI": "#E67E22",
    "anima": "#2ECC71",
}

GRADE_SHAPES = {
    "\u2b50": "doubleoctagon",   # star
    "\u2605": "doubleoctagon",   # filled star
    "\U0001f7e9": "box",         # green square
    "\U0001f7e7": "diamond",     # orange square
    "\u26aa": "ellipse",         # white circle
    "\u2b1b": "point",           # black square
}


def _sanitize_dot_id(hid):
    """Sanitize a hypothesis ID for use as a DOT node ID."""
    return re.sub(r'[:\-]', '_', hid)


def _grade_to_shape(grade):
    """Map a grade string to a DOT shape."""
    if not grade:
        return "ellipse"
    for emoji, shape in GRADE_SHAPES.items():
        if emoji in grade:
            return shape
    return "ellipse"


def write_dot(atlas, dotpath):
    """Write atlas graph to a Graphviz DOT file.

    Only includes nodes that have at least one edge (ref connection).

    Args:
        atlas: dict returned by build_atlas().
        dotpath: Path to the output .dot file.
    """
    # Build ID lookup for resolving refs
    id_lookup = {}
    hyp_by_id = {}
    for h in atlas["hypotheses"]:
        full_id = h["id"]
        short = full_id.split(":", 1)[1] if ":" in full_id else full_id
        if short not in id_lookup:
            id_lookup[short] = full_id
        hyp_by_id[full_id] = h

    # Collect edges
    edges = []
    connected = set()
    for h in atlas["hypotheses"]:
        source = h["id"]
        for ref in h.get("refs", []):
            target = id_lookup.get(ref)
            if target and target != source:
                edges.append((source, target))
                connected.add(source)
                connected.add(target)

    lines = ['digraph math_atlas {', '  rankdir=LR;', '  node [style=filled];', '']

    # Emit connected nodes
    for nid in sorted(connected):
        h = hyp_by_id.get(nid)
        if not h:
            continue
        safe = _sanitize_dot_id(nid)
        color = REPO_COLORS.get(h["repo"], "#999999")
        shape = _grade_to_shape(h.get("grade"))
        label = h["title"][:40].replace('"', '\\"') if h.get("title") else nid
        lines.append(f'  {safe} [label="{label}" fillcolor="{color}" shape={shape}];')

    lines.append('')

    # Emit edges
    for src, tgt in edges:
        lines.append(f'  {_sanitize_dot_id(src)} -> {_sanitize_dot_id(tgt)};')

    lines.append('}')

    with open(dotpath, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines) + '\n')
