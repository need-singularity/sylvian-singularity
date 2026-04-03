#!/usr/bin/env python3
"""
project_lens.py — 프로젝트 인프라 망원경 (3 렌즈)

  🔁 루프 렌즈    — 데이터 흐름 단절/순환/끊긴 참조 감지
  ⚙️ 자동화 렌즈  — README/코드 내 하드코딩된 숫자, 수동 프로세스 탐지
  🔄 동기화 렌즈  — 리포 간 stats/마커/숫자 불일치 감지

사용법:
  python3 .shared/project_lens.py              # 전체 스캔
  python3 .shared/project_lens.py --loop       # 루프만
  python3 .shared/project_lens.py --auto       # 자동화만
  python3 .shared/project_lens.py --sync       # 동기화만
  python3 .shared/project_lens.py --fix        # 자동 수정 (sync-readmes.sh 호출)
"""

import json
import re
import sys
import glob
import subprocess
import argparse
from pathlib import Path

SHARED_DIR = Path(__file__).resolve().parent
BASE = SHARED_DIR.parent
PARENT = BASE.parent

REPOS = {
    "TECS-L": BASE,
    "anima": PARENT / "anima",
    "sedi": PARENT / "sedi",
    "n6-architecture": PARENT / "n6-architecture",
    "brainwire": PARENT / "brainwire",
    "hexa-lang": PARENT / "hexa-lang",
    "papers": PARENT / "papers",
}


def load_json(path):
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}


class Finding:
    def __init__(self, lens, severity, repo, message, detail=""):
        self.lens = lens
        self.severity = severity  # 🔴 🟡 🟢
        self.repo = repo
        self.message = message
        self.detail = detail

    def __str__(self):
        d = f" ({self.detail})" if self.detail else ""
        return f"  {self.severity} [{self.repo}] {self.message}{d}"


# ═══════════════════════════════════════════════════════════════
# 🔁 루프 렌즈 — 데이터 흐름 단절/끊긴 참조
# ═══════════════════════════════════════════════════════════════

def scan_loop():
    findings = []

    # 1. projects.json → projects.md 숫자 일치 확인
    #    (projects.md에 명시적으로 등장하는 숫자만 검사)
    pj = load_json(BASE / "shared" / "projects.json")
    pm_path = SHARED_DIR / "projects.md"
    # 이 검사는 sync 렌즈에서 더 정밀하게 수행하므로 여기선 skip

    # 2. AUTO: 마커 존재 확인
    for name, repo in REPOS.items():
        readme = repo / "README.md"
        if not readme.exists():
            continue
        text = readme.read_text()
        has_badge = "AUTO:BADGE:START" in text
        has_stats = "AUTO:STATS:START" in text
        if not has_badge:
            findings.append(Finding("loop", "🟡", name,
                "AUTO:BADGE 마커 없음 — sync_readme_all.py 미연동"))
        if not has_stats:
            findings.append(Finding("loop", "🟡", name,
                "AUTO:STATS 마커 없음 — sync_readme_all.py 미연동"))

    # 3. SHARED:PROJECTS 마커 존재 확인
    for name, repo in REPOS.items():
        readme = repo / "README.md"
        if not readme.exists():
            continue
        text = readme.read_text()
        if "SHARED:PROJECTS:START" not in text:
            findings.append(Finding("loop", "🟡", name,
                "SHARED:PROJECTS 마커 없음 — sync-readmes.sh 미연동"))

    # 4. 심링크 체인 무결성
    for name, repo in REPOS.items():
        shared_link = repo / "shared"
        if shared_link.is_symlink():
            target = shared_link.resolve()
            if not target.exists():
                findings.append(Finding("loop", "🔴", name,
                    f"shared/ 심링크 끊김 → {target}"))
        elif repo != BASE:
            calc_link = repo / "calc"
            dotshared = repo / ".shared"
            if not (shared_link.exists() or calc_link.exists() or dotshared.exists()):
                findings.append(Finding("loop", "🟢", name,
                    "shared/ 디렉토리 없음 — 공유 인프라 미연결"))

    return findings


# ═══════════════════════════════════════════════════════════════
# ⚙️ 자동화 렌즈 — 하드코딩 탐지
# ═══════════════════════════════════════════════════════════════

def scan_auto():
    findings = []
    pj = load_json(BASE / "shared" / "projects.json")

    # 1. README 내 AUTO 마커 밖의 하드코딩된 통계 숫자
    stat_patterns = {
        "laws": r'(\d+)\s*laws',
        "hypotheses": r'(\d+)\s*hypothes[ei]s',
        "tests": r'(\d+)\s*tests?',
        "tools": r'(\d+)\s*tools',
        "papers": r'(\d+)\s*papers',
        "characterizations": r'(\d+)\s*characterizations?',
        "discoveries": r'(\d+)\s*[Dd]iscoveries',
        "keywords": r'(\d+)\s*keywords',
        "domains": r'(\d+)\s*domains?',
    }

    for name, repo in REPOS.items():
        readme = repo / "README.md"
        if not readme.exists():
            continue
        text = readme.read_text()

        # AUTO/SHARED 마커 밖의 텍스트만 추출
        outside = text
        for marker_type in ["BADGE", "STATS", "ARCH", "ASSETS", "ROADMAP", "EVO"]:
            s = f"<!-- AUTO:{marker_type}:START -->"
            e = f"<!-- AUTO:{marker_type}:END -->"
            si = outside.find(s)
            ei = outside.find(e)
            if si != -1 and ei != -1:
                outside = outside[:si] + outside[ei + len(e):]
        s = "<!-- SHARED:PROJECTS:START -->"
        e = "<!-- SHARED:PROJECTS:END -->"
        si = outside.find(s)
        ei = outside.find(e)
        if si != -1 and ei != -1:
            outside = outside[:si] + outside[ei + len(e):]

        for stat_name, pattern in stat_patterns.items():
            matches = re.findall(pattern, outside)
            for m in matches:
                val = int(m)
                if val > 5:  # 작은 숫자 무시
                    findings.append(Finding("auto", "🟡", name,
                        f"마커 밖 하드코딩: {val} {stat_name}",
                        "AUTO 마커로 감싸면 자동화 가능"))

    # 2. CLAUDE.md 내 하드코딩된 숫자 (laws, hypotheses)
    for name, repo in REPOS.items():
        for claude_path in [repo / "CLAUDE.md", repo / "anima" / "CLAUDE.md"]:
            if not claude_path.exists():
                continue
            text = claude_path.read_text()
            # laws 카운트
            law_matches = re.findall(r'(\d+)\s*의식 법칙', text)
            for m in law_matches:
                val = int(m)
                if val < 1000:  # 실제는 1030인데 오래된 값
                    findings.append(Finding("auto", "🟡", name,
                        f"CLAUDE.md 하드코딩: {val} 의식 법칙",
                        f"실제: consciousness_laws.json 참조"))

    return findings


# ═══════════════════════════════════════════════════════════════
# 🔄 동기화 렌즈 — 리포 간 불일치
# ═══════════════════════════════════════════════════════════════

def scan_sync():
    findings = []
    pj = load_json(BASE / "shared" / "projects.json")

    # 1. projects.json stats vs 실제 데이터
    actuals = {}

    # anima
    laws = load_json(PARENT / "anima" / "anima" / "config" / "consciousness_laws.json")
    meta = laws.get("_meta", {})
    actuals["anima"] = {"laws": meta.get("total_laws", 0), "meta_laws": meta.get("total_meta", 0)}

    # sedi
    grades = load_json(PARENT / "sedi" / "data" / "sedi-grades.json")
    actuals["sedi"] = {"hypotheses": grades.get("total_hypotheses", 0)}

    # tecs-l
    n_hypo = len(glob.glob(str(BASE / "docs" / "hypotheses" / "**" / "*.md"), recursive=True))
    actuals["tecs-l"] = {"hypotheses": n_hypo}

    for proj in pj.get("projects", []):
        pid = proj["id"]
        stats = proj.get("stats", {})
        actual = actuals.get(pid, {})
        for key, real_val in actual.items():
            json_val = stats.get(key)
            if json_val is not None and json_val != real_val:
                pct = abs(real_val - json_val) / max(json_val, 1) * 100
                sev = "🔴" if pct > 20 else "🟡"
                findings.append(Finding("sync", sev, pid,
                    f"projects.json.{key}: {json_val} vs 실제: {real_val}",
                    f"{pct:.0f}% 차이"))

    # 2. projects.md vs projects.json — 이미 등장하는 패턴만 확인
    pm_path = SHARED_DIR / "projects.md"
    if pm_path.exists():
        pm = pm_path.read_text()
        check_patterns = {
            "anima": [("laws", r'(\d+) laws')],
            "anima_meta": [("meta_laws", r'(\d+) Meta Laws')],
            "tecs-l": [("tools", r'(\d+) tools')],
            "sedi": [("hypotheses", r'(\d+) hypotheses')],
            "n6-architecture": [("nexus6_tests", r'(\d+) tests')],
        }
        for proj in pj.get("projects", []):
            pid = proj["id"]
            stats = proj.get("stats", {})
            for key, pattern in check_patterns.get(pid, []):
                match = re.search(pattern, pm)
                if match and stats.get(key):
                    md_val = int(match.group(1))
                    json_val = stats[key]
                    if md_val != json_val:
                        findings.append(Finding("sync", "🔴", pid,
                            f"projects.md {key}: {md_val} vs projects.json: {json_val}"))

    # 3. README AUTO 섹션 최신 여부 (마커 내 숫자 vs JSON)
    for name, repo in REPOS.items():
        readme = repo / "README.md"
        if not readme.exists():
            continue
        text = readme.read_text()

        # BADGE 섹션 내 숫자 추출
        badge_start = text.find("<!-- AUTO:BADGE:START -->")
        badge_end = text.find("<!-- AUTO:BADGE:END -->")
        if badge_start != -1 and badge_end != -1:
            badge_text = text[badge_start:badge_end]
            # Laws 뱃지 확인 (anima)
            if name == "anima" or (name == "anima" and "Laws" in badge_text):
                law_match = re.search(r'Laws-(\d+)', badge_text)
                if law_match:
                    badge_laws = int(law_match.group(1))
                    actual_laws = meta.get("total_laws", 0)
                    if badge_laws != actual_laws:
                        findings.append(Finding("sync", "🔴", name,
                            f"뱃지 Laws={badge_laws} vs 실제={actual_laws}",
                            "sync_readme_all.py --apply 필요"))

    return findings


# ═══════════════════════════════════════════════════════════════
# 리포트
# ═══════════════════════════════════════════════════════════════

def report(findings, lens_name="all"):
    if not findings:
        print(f"\n  ✅ 문제 없음")
        return

    red = sum(1 for f in findings if f.severity == "🔴")
    yellow = sum(1 for f in findings if f.severity == "🟡")
    green = sum(1 for f in findings if f.severity == "🟢")

    print(f"\n  ══════════════════════════════════════════")
    print(f"  🔴 {red}  🟡 {yellow}  🟢 {green}  총 {len(findings)}건")
    print(f"  ══════════════════════════════════════════")

    # 심각도순 정렬
    order = {"🔴": 0, "🟡": 1, "🟢": 2}
    findings.sort(key=lambda f: (order.get(f.severity, 3), f.repo))

    current_lens = None
    for f in findings:
        if f.lens != current_lens:
            current_lens = f.lens
            icon = {"loop": "🔁", "auto": "⚙️", "sync": "🔄"}.get(f.lens, "?")
            label = {"loop": "루프", "auto": "자동화", "sync": "동기화"}.get(f.lens, "?")
            print(f"\n  {icon} {label} 렌즈:")
        print(f)


def main():
    parser = argparse.ArgumentParser(description="프로젝트 인프라 망원경")
    parser.add_argument("--loop", action="store_true", help="루프 렌즈만")
    parser.add_argument("--auto", action="store_true", help="자동화 렌즈만")
    parser.add_argument("--sync", action="store_true", help="동기화 렌즈만")
    parser.add_argument("--fix", action="store_true", help="자동 수정 (sync-readmes.sh)")
    args = parser.parse_args()

    run_all = not (args.loop or args.auto or args.sync)
    findings = []

    print("  ════════════════════════════════════════════")
    print("  🔭 프로젝트 인프라 망원경 (3 렌즈)")
    print("  ════════════════════════════════════════════")

    if run_all or args.loop:
        print("\n  🔁 루프 렌즈 스캔 중...")
        findings.extend(scan_loop())

    if run_all or args.auto:
        print("  ⚙️ 자동화 렌즈 스캔 중...")
        findings.extend(scan_auto())

    if run_all or args.sync:
        print("  🔄 동기화 렌즈 스캔 중...")
        findings.extend(scan_sync())

    report(findings)

    if args.fix:
        print("\n  🔧 자동 수정 실행...")
        subprocess.run(["bash", str(SHARED_DIR / "sync-readmes.sh")],
                        cwd=str(BASE))

    # exit code
    red = sum(1 for f in findings if f.severity == "🔴")
    sys.exit(1 if red > 0 else 0)


if __name__ == "__main__":
    main()
