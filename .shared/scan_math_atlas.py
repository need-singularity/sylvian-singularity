#!/usr/bin/env python3
"""Math Atlas — Hypothesis Markdown Parser.

Parses hypothesis markdown files from TECS-L, anima, SEDI repos
and extracts structured metadata (id, title, grade, refs, etc.).
"""

import re
from pathlib import Path

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
