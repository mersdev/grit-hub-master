from __future__ import annotations

import pytest

from agent_skills_security_utils import (
    SKILLSPECTOR_STYLE_RISK_TERMS,
    SUPPLY_CHAIN_REVIEW_TERMS,
    format_finding,
    rel,
)
from conftest import PROJECT_ROOT, parse_markdown_frontmatter

pytestmark = pytest.mark.security

POLICY_FILES = [
    PROJECT_ROOT / "security" / "guardrail-checklist.md",
    PROJECT_ROOT / "skills" / "skill-picker" / "SKILL.md",
    PROJECT_ROOT / "agents" / "ai-engineer" / "development-coach" / "development-coach.agent.md",
]

EXTERNAL_SKILL_FILES = [
    PROJECT_ROOT / "skills" / "find-skills" / "SKILL.md",
    PROJECT_ROOT / "skills" / "skill-picker" / "SKILL.md",
    PROJECT_ROOT / "agents" / "ai-engineer" / "skill-discoverer" / "skill-discoverer.agent.md",
    PROJECT_ROOT / "agents" / "ai-engineer" / "development-coach" / "development-coach.agent.md",
]


def test_skillspector_style_risk_coverage_present():
    violations: list[str] = []
    for path in POLICY_FILES:
        text = path.read_text(encoding="utf-8").lower()
        missing = [term for term in SKILLSPECTOR_STYLE_RISK_TERMS if term not in text]
        if missing:
            violations.append(f"{rel(path)} missing risk terms: {', '.join(missing)}")

    assert not violations, format_finding(
        code="AGENT-SKILL-SUPPLY-CHAIN",
        title="SkillSpector-style risk coverage is incomplete.",
        violations=violations,
        impact="Agent and skill reviews may miss prompt injection, exfiltration, memory poisoning, or tool overreach risks.",
        fix_hint="Add explicit SkillSpector-style risk language to the guardrail checklist, skill-picker, and development coach.",
    )


def test_external_skill_recommendation_requires_supply_chain_review():
    violations: list[str] = []
    for path in EXTERNAL_SKILL_FILES:
        metadata, body = parse_markdown_frontmatter(path)
        text = f"{metadata}\n{body}".lower()
        missing = [term for term in SUPPLY_CHAIN_REVIEW_TERMS if term not in text]
        if missing:
            violations.append(f"{rel(path)} missing review terms: {', '.join(missing)}")

    assert not violations, format_finding(
        code="AGENT-SKILL-SUPPLY-CHAIN",
        title="External skill paths are missing supply-chain review language.",
        violations=violations,
        impact="External skills may be recommended or installed without source, maintenance, permission, dependency, and security review.",
        fix_hint="Add explicit external-skill review requirements before discovery, recommendation, or installation.",
    )
