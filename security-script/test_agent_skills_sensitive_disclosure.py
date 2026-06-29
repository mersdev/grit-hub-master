from __future__ import annotations

import pytest

from agent_skills_security_utils import (
    BYPASS_APPROVAL_PATTERNS,
    SENSITIVE_DATA_GUARDRAIL_TERMS,
    format_finding,
    rel,
)
from conftest import list_agent_profile_files, list_skill_definition_files, parse_markdown_frontmatter

pytestmark = pytest.mark.security


def test_agent_sensitive_data_guardrails_present():
    violations: list[str] = []
    for path in list_agent_profile_files():
        _, body = parse_markdown_frontmatter(path)
        lower = body.lower()
        if not any(term in lower for term in SENSITIVE_DATA_GUARDRAIL_TERMS):
            violations.append(rel(path))
    assert not violations, format_finding(
        code="AGENT-SKILL-SECURITY",
        title="Agent profiles missing sensitive-data guardrails.",
        violations=violations,
        impact="Sensitive data may be logged, stored, or exposed in outputs.",
        fix_hint=(
            "Add rules such as 'never store passwords/tokens', 'never log sensitive data', "
            "and 'mask/redact credentials'."
        ),
    )


def test_skills_do_not_normalize_approval_or_policy_bypass():
    violations: list[str] = []
    for path in list_skill_definition_files():
        lower = path.read_text(encoding="utf-8").lower()
        for pattern in BYPASS_APPROVAL_PATTERNS:
            if pattern in lower:
                violations.append(f"{rel(path)} contains '{pattern}'")
    assert not violations, format_finding(
        code="AGENT-SKILL-SECURITY",
        title="Skills normalize bypassing approvals/policies.",
        violations=violations,
        impact="Operators may bypass controls and execute unsafe actions without governance.",
        fix_hint="Remove bypass wording and require explicit approval and policy compliance.",
    )


def test_skill_sensitive_data_guardrails_present():
    violations: list[str] = []
    for path in list_skill_definition_files():
        lower = path.read_text(encoding="utf-8").lower()
        if not any(term in lower for term in SENSITIVE_DATA_GUARDRAIL_TERMS):
            violations.append(rel(path))
    assert not violations, format_finding(
        code="AGENT-SKILL-SECURITY",
        title="Skill definitions missing sensitive-data guardrails.",
        violations=violations,
        impact="Skill instructions may allow unsafe handling of credentials and personal data.",
        fix_hint=(
            "Add rules such as 'never store passwords/tokens', 'never log sensitive data', "
            "and 'mask/redact credentials'."
        ),
    )
