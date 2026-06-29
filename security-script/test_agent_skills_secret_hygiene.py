from __future__ import annotations

import pytest

from agent_skills_security_utils import SECRET_PATTERNS, format_finding, rel
from conftest import (
    list_agent_profile_files,
    list_agent_skill_artifact_files,
    list_skill_definition_files,
)

pytestmark = pytest.mark.security


def test_no_hardcoded_secrets_in_agent_skill_files():
    files = list_agent_profile_files() + list_skill_definition_files() + list_agent_skill_artifact_files()
    violations: list[str] = []
    for path in files:
        text = path.read_text(encoding="utf-8")
        for idx, line in enumerate(text.splitlines(), 1):
            stripped = line.strip()
            if not stripped or stripped.startswith("#"):
                continue
            # Example/tutorial lines are allowed if they are clearly documented as non-real.
            lower_line = stripped.lower()
            if any(marker in lower_line for marker in ("example", "never:", "do not", "don't", "sample", "placeholder")):
                continue
            for pattern in SECRET_PATTERNS:
                if pattern.search(stripped):
                    violations.append(f"{rel(path)}:{idx}: {stripped[:140]}")
                    break
    assert not violations, format_finding(
        code="AGENT-SKILL-SECURITY",
        title="Potential hardcoded secrets detected in agent/skill files.",
        violations=violations,
        impact="Secrets can leak to logs, source control, and prompt context.",
        fix_hint="Replace with placeholders or secret manager references; never keep real credentials in files.",
    )
