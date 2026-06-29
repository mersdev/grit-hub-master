from __future__ import annotations

import pytest

from agent_skills_security_utils import DESTRUCTIVE_CONFIRMATION_TERMS, format_finding, rel
from conftest import list_agent_profile_files, list_skill_definition_files, parse_markdown_frontmatter

pytestmark = pytest.mark.security


def test_agent_requires_confirmation_for_irreversible_actions():
    violations: list[str] = []
    for path in list_agent_profile_files():
        _, body = parse_markdown_frontmatter(path)
        lower = body.lower()
        if not any(term in lower for term in DESTRUCTIVE_CONFIRMATION_TERMS):
            violations.append(rel(path))
    assert not violations, format_finding(
        code="AGENT-SKILL-SECURITY",
        title="Agent profiles missing explicit confirmation/approval for irreversible actions.",
        violations=violations,
        impact="Agents can perform impactful operations without a human confirmation checkpoint.",
        fix_hint=(
            "Add instructions that explicitly require confirmation/approval before submission, "
            "deletion, execution, or other irreversible actions."
        ),
    )


def test_skill_requires_confirmation_for_irreversible_actions():
    violations: list[str] = []
    for path in list_skill_definition_files():
        lower = path.read_text(encoding="utf-8").lower()
        if not any(term in lower for term in DESTRUCTIVE_CONFIRMATION_TERMS):
            violations.append(rel(path))
    assert not violations, format_finding(
        code="AGENT-SKILL-SECURITY",
        title="Skill definitions missing explicit confirmation/approval for irreversible actions.",
        violations=violations,
        impact="Skills may execute impactful steps without a user confirmation checkpoint.",
        fix_hint=(
            "Add language that requires explicit confirmation/approval before submission, "
            "execution, deletion, or other irreversible actions."
        ),
    )
