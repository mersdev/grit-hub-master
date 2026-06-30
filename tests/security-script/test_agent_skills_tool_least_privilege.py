from __future__ import annotations

import pytest

from agent_skills_security_utils import RISKY_TOOLS, format_finding, rel
from conftest import list_agent_profile_files, parse_markdown_frontmatter

pytestmark = pytest.mark.security


def test_agent_has_explicit_tool_allowlist():
    violations: list[str] = []
    for path in list_agent_profile_files():
        metadata, _ = parse_markdown_frontmatter(path)
        tools = metadata.get("tools")
        if tools is None:
            violations.append(f"{rel(path)} missing `tools` field")
            continue
        if isinstance(tools, str):
            if tools.strip().lower() in {"*", "all", "any"}:
                violations.append(f"{rel(path)} uses implicit all-tools (`{tools}`)")
            continue
        if isinstance(tools, list):
            if not tools:
                violations.append(f"{rel(path)} has empty tools allowlist")
            elif any(str(item).strip() == "*" for item in tools):
                violations.append(f"{rel(path)} includes wildcard `*` tool entry")
            continue
        violations.append(f"{rel(path)} has invalid `tools` type: {type(tools).__name__}")
    assert not violations, format_finding(
        code="AGENT-SKILL-SECURITY",
        title="Agents are missing explicit least-privilege tool allowlists.",
        violations=violations,
        impact="Broad or implicit tool access increases blast radius of prompt injection and misuse.",
        fix_hint="Define non-empty explicit `tools` lists and remove wildcard/all-tool patterns.",
    )


def test_risky_tools_require_security_guardrails():
    violations: list[str] = []
    for path in list_agent_profile_files():
        metadata, body = parse_markdown_frontmatter(path)
        tools = metadata.get("tools") or []
        if isinstance(tools, str):
            tool_names = {tools.lower()}
        elif isinstance(tools, list):
            tool_names = {str(t).lower() for t in tools}
        else:
            tool_names = set()
        has_risky = any(t in RISKY_TOOLS for t in tool_names)
        if not has_risky:
            continue
        lower = body.lower()
        has_guardrail = any(k in lower for k in ("guardrail", "security", "approval", "confirm", "never"))
        if not has_guardrail:
            violations.append(rel(path))
    assert not violations, format_finding(
        code="AGENT-SKILL-SECURITY",
        title="Profiles with risky tools are missing security guardrail language.",
        violations=violations,
        impact="Shell/terminal capabilities may run without clear constraints.",
        fix_hint="For risky tools, add explicit safety rules and approval requirements in the profile body.",
    )
