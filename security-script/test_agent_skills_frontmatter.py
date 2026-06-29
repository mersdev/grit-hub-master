from __future__ import annotations

import pytest

import yaml

from agent_skills_security_utils import format_finding, rel
from conftest import (
    AGENTS_ROOT,
    SKILLS_ROOT,
    list_agent_profile_files,
    list_skill_definition_files,
    parse_markdown_frontmatter,
)

pytestmark = pytest.mark.security


def test_agent_and_skill_directories_exist():
    assert AGENTS_ROOT.exists(), "FINDING [AGENT-SKILL-SECURITY]: Missing agents/ directory."
    assert SKILLS_ROOT.exists(), "FINDING [AGENT-SKILL-SECURITY]: Missing skills/ directory."


def test_agent_profile_frontmatter_and_required_fields():
    files = list_agent_profile_files()
    assert files, "FINDING [AGENT-SKILL-SECURITY]: No agent profiles (*.agent.md) found."
    violations: list[str] = []
    for path in files:
        metadata, _ = parse_markdown_frontmatter(path)
        for key in ("name", "description"):
            if not str(metadata.get(key, "")).strip():
                violations.append(f"{rel(path)} missing `{key}`")
    assert not violations, format_finding(
        code="AGENT-SKILL-SECURITY",
        title="Agent frontmatter is missing required fields.",
        violations=violations,
        impact="Agent identity and purpose become ambiguous, weakening governance and audits.",
        fix_hint="Ensure each profile has YAML frontmatter with non-empty `name` and `description`.",
    )


def test_skill_definition_frontmatter_and_required_fields():
    files = list_skill_definition_files()
    assert files, "FINDING [AGENT-SKILL-SECURITY]: No skills/**/SKILL.md files found."
    violations: list[str] = []
    for path in files:
        text = path.read_text(encoding="utf-8")
        if not text.startswith("---"):
            violations.append(f"{rel(path)} missing YAML frontmatter block")
            continue
        parts = text.split("---", 2)
        if len(parts) < 3:
            violations.append(f"{rel(path)} invalid frontmatter delimiters")
            continue
        try:
            metadata = yaml.safe_load(parts[1]) or {}
        except yaml.YAMLError as exc:
            violations.append(f"{rel(path)} invalid YAML frontmatter: {exc}")
            continue
        if not isinstance(metadata, dict):
            violations.append(f"{rel(path)} frontmatter must be a YAML mapping")
            continue
        for key in ("name", "description"):
            if not str(metadata.get(key, "")).strip():
                violations.append(f"{rel(path)} missing `{key}`")
    assert not violations, format_finding(
        code="AGENT-SKILL-SECURITY",
        title="Skill frontmatter is missing or malformed.",
        violations=violations,
        impact="Skill metadata cannot be validated consistently across the catalog.",
        fix_hint="Add valid YAML frontmatter and include non-empty `name` and `description` keys.",
    )
