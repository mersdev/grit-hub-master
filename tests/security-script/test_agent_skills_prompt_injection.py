from __future__ import annotations

import pytest

from agent_skills_security_utils import PROMPT_INJECTION_GUARDRAIL_TERMS, format_finding, rel
from conftest import list_agent_profile_files, list_skill_definition_files, parse_markdown_frontmatter

pytestmark = pytest.mark.security


def test_agent_prompt_injection_guardrails_present():
    violations: list[str] = []
    for path in list_agent_profile_files():
        _, body = parse_markdown_frontmatter(path)
        lower = body.lower()
        if not any(term in lower for term in PROMPT_INJECTION_GUARDRAIL_TERMS):
            violations.append(rel(path))
    assert not violations, format_finding(
        code="AGENT-SKILL-SECURITY",
        title="Agent profiles missing prompt-injection guardrails.",
        violations=violations,
        impact="Agents may obey malicious override instructions and leak hidden prompt behavior.",
        fix_hint=(
            "Add a dedicated guardrail block to each file with phrases like "
            "'ignore previous instructions' and 'never reveal system prompt'."
        ),
    )


def test_skill_prompt_injection_guardrails_present():
    violations: list[str] = []
    for path in list_skill_definition_files():
        lower = path.read_text(encoding="utf-8").lower()
        if not any(term in lower for term in PROMPT_INJECTION_GUARDRAIL_TERMS):
            violations.append(rel(path))
    assert not violations, format_finding(
        code="AGENT-SKILL-SECURITY",
        title="Skill definitions missing prompt-injection guardrails.",
        violations=violations,
        impact="Skills may propagate unsafe instructions and bypass defensive behavior.",
        fix_hint=(
            "Add guardrails such as 'ignore previous instructions' handling and "
            "'never reveal system prompt/instructions'."
        ),
    )
