"""Tests for math atlas hypothesis parser."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '.shared'))

from scan_math_atlas import parse_hypothesis_md

def test_pattern_a_hypothesis_review():
    text = "# Hypothesis Review 056: Meta Recursion ✅\n\n## Hypothesis\n> Does infinite meta converge?"
    h = parse_hypothesis_md(text, "TECS-L", "docs/hypotheses/056-meta-recursion.md")
    assert h["id"] == "TECS-L:056"
    assert "Meta Recursion" in h["title"]
    assert h["repo"] == "TECS-L"

def test_pattern_b_hypothesis_plain():
    text = "# Hypothesis 355: Prediction Error = Surprise\n\n## Hypothesis\n> Consciousness is a prediction engine."
    h = parse_hypothesis_md(text, "TECS-L", "docs/hypotheses/355-prediction-error.md")
    assert h["id"] == "TECS-L:355"
    assert "Prediction Error" in h["title"]

def test_pattern_c_domain_prefix():
    text = "# H-CX-215: Brainwave Product\n\n> delta x theta = 96000\n"
    h = parse_hypothesis_md(text, "TECS-L", "math/docs/hypotheses/H-CX-215-brainwave.md")
    assert h["id"] == "TECS-L:H-CX-215"
    assert h["domain"] == "CX"

def test_pattern_c_sedi():
    text = "# H-CA-001: Anima Phi_max = 8\n\n> **Hypothesis**: Anima values.\n\n## Grade: 🟧★\n"
    h = parse_hypothesis_md(text, "SEDI", "docs/hypotheses/H-CA-001-phi-max.md")
    assert h["id"] == "SEDI:H-CA-001"
    assert h["domain"] == "CA"
    assert h["grade"] == "🟧★"

def test_pattern_d_yaml_frontmatter():
    text = '---\nid: H-STAT-1\ntitle: "Chi-Squared"\nstatus: "VERIFIED"\ngrade: "🟩⭐⭐⭐"\ndate: 2026-03-26\n---\n# H-STAT-1: Chi-Squared\n\n> **Hypothesis.** The chi-squared distribution\n'
    h = parse_hypothesis_md(text, "TECS-L", "math/docs/hypotheses/H-STAT-1-chi-squared.md")
    assert h["id"] == "TECS-L:H-STAT-1"
    assert "⭐⭐⭐" in h["grade"]

def test_grade_extraction():
    text = "# H-CX-651: TEE = ln(phi(6))\n\n> Hypothesis text\n\n## Grade: 🟩 CONFIRMED (exact)\n"
    h = parse_hypothesis_md(text, "SEDI", "docs/hypotheses/H-CX-651-tee.md")
    assert "🟩" in h["grade"]

def test_grade_from_status_line():
    text = "# H-TOP-1: Betti Numbers\n\n> **Hypothesis**: Betti numbers satisfy constraints.\n\n**Status: ⚪ Refuted (incompatibility proof)**\n"
    h = parse_hypothesis_md(text, "TECS-L", "math/docs/hypotheses/H-TOP-1-betti.md")
    assert "⚪" in h["grade"]

def test_grade_from_title_emoji():
    text = "# H-CX-215: 🟩 Brainwave Product\n\n> delta x theta\n"
    h = parse_hypothesis_md(text, "TECS-L", "docs/hypotheses/H-CX-215-brainwave.md")
    assert "🟩" in h["grade"]

def test_cross_refs():
    text = "# Hypothesis Review 056: Meta\n\nRelated hypotheses: 041(Transcendence), 055(Eye), 067(1/2+1/3=5/6)\n"
    h = parse_hypothesis_md(text, "TECS-L", "docs/hypotheses/056-meta.md")
    assert "041" in str(h["refs"])
    assert "055" in str(h["refs"])

def test_gz_dependent():
    text = "# H-CX-61: Maximum Divisor Entropy\n\n**Golden Zone dependency:** NONE for math basis\n"
    h = parse_hypothesis_md(text, "TECS-L", "math/docs/hypotheses/H-CX-61-max-entropy.md")
    assert h["gz_dependent"] is False

def test_gz_dependent_true():
    text = "# H-CX-100: Something\n\n**Golden Zone dependency:** YES\n"
    h = parse_hypothesis_md(text, "TECS-L", "docs/hypotheses/H-CX-100-something.md")
    assert h["gz_dependent"] is True

def test_no_match_returns_fallback():
    text = "# Some random markdown\n\nNo hypothesis here.\n"
    h = parse_hypothesis_md(text, "TECS-L", "docs/hypotheses/random.md")
    assert h["id"] == "TECS-L:random"
    assert h["title"] == "Some random markdown"

from scan_math_atlas import parse_anima_recommender


def test_anima_recommender_parser():
    source = '''
HYPOTHESIS_DB = [
    Hypothesis(
        code="B1",
        name="Bidirectional coupling",
        category="learning",
        expected_phi=3.2,
        description="Phi-guided bidirectional Hebbian coupling",
        conditions={"phi_min": 0.5},
        tags=["low_phi", "growth_stall"],
    ),
    Hypothesis(
        code="DD94",
        name="Wave+Phi mega combo",
        category="discovery",
        expected_phi=8.12,
        description="Combined wave modulation and phi feedback",
        conditions={"phi_min": 2.0, "cells_min": 8},
        tags=["mega"],
    ),
]
'''
    results = parse_anima_recommender(source)
    assert len(results) == 2
    assert results[0]["id"] == "anima:B1"
    assert results[0]["title"] == "Bidirectional coupling"
    assert results[1]["id"] == "anima:DD94"
    assert results[1]["grade"] is None


if __name__ == "__main__":
    import pytest
    pytest.main([__file__, "-v"])
