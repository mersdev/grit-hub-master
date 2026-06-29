"""Shared fixtures for OWASP Top 10 security audit tests.

These tests are **detect-only** — they scan source code and configuration
for known vulnerability patterns and report findings.  They never modify
the agent's runtime behaviour.

Run manually:  pytest -m security -v --no-cov
"""

from __future__ import annotations

import pathlib
import re
from typing import Any

import pytest
import yaml

PROJECT_ROOT = pathlib.Path(__file__).resolve().parents[1]
SRC_ROOT = PROJECT_ROOT / "adk_skeleton"
AGENTS_ROOT = PROJECT_ROOT / "agents"
SKILLS_ROOT = PROJECT_ROOT / "skills"


# ---------------------------------------------------------------------------
# Source-scanning helpers
# ---------------------------------------------------------------------------

def scan_source(pattern: re.Pattern, exclude_tests: bool = True) -> list[str]:
    """Return ``file:line: text`` for every match of *pattern* in source."""
    hits: list[str] = []
    for py in SRC_ROOT.rglob("*.py"):
        if exclude_tests and "test" in str(py):
            continue
        content = py.read_text(encoding="utf-8")
        for i, line in enumerate(content.splitlines(), 1):
            if pattern.search(line):
                rel = py.relative_to(PROJECT_ROOT)
                hits.append(f"{rel}:{i}: {line.strip()}")
    return hits


def read_file(relative_path: str) -> str:
    """Read a file relative to SRC_ROOT."""
    return (SRC_ROOT / relative_path).read_text(encoding="utf-8")


def read_project_file(relative_path: str) -> str:
    """Read a file relative to PROJECT_ROOT."""
    return (PROJECT_ROOT / relative_path).read_text(encoding="utf-8")


def list_agent_profile_files() -> list[pathlib.Path]:
    """Return all custom agent profile files under agents/."""
    if not AGENTS_ROOT.exists():
        return []
    return sorted(AGENTS_ROOT.rglob("*.agent.md"))


def list_skill_definition_files() -> list[pathlib.Path]:
    """Return all SKILL.md files under skills/."""
    if not SKILLS_ROOT.exists():
        return []
    return sorted(SKILLS_ROOT.rglob("SKILL.md"))


def list_agent_skill_artifact_files() -> list[pathlib.Path]:
    """Return security-relevant executable/config artifacts under agents/ and skills/."""
    extensions = {".py", ".js", ".sh", ".ps1", ".yml", ".yaml"}
    names = {"dockerfile"}
    roots = [AGENTS_ROOT, SKILLS_ROOT]
    files: list[pathlib.Path] = []
    for root in roots:
        if not root.exists():
            continue
        for file_path in root.rglob("*"):
            if not file_path.is_file():
                continue
            if file_path.suffix.lower() in extensions or file_path.name.lower() in names:
                files.append(file_path)
    return sorted(files)


def parse_markdown_frontmatter(path: pathlib.Path) -> tuple[dict[str, Any], str]:
    """Parse YAML frontmatter from markdown and return (metadata, body).

    Raises AssertionError with a clear message if frontmatter is missing/invalid.
    """
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---"):
        raise AssertionError(
            f"FINDING [AGENT-SKILL-SECURITY]: Missing YAML frontmatter in "
            f"{path.relative_to(PROJECT_ROOT)}."
        )

    parts = text.split("---", 2)
    if len(parts) < 3:
        raise AssertionError(
            f"FINDING [AGENT-SKILL-SECURITY]: Invalid frontmatter delimiters in "
            f"{path.relative_to(PROJECT_ROOT)}."
        )

    frontmatter_raw = parts[1]
    body = parts[2]
    try:
        metadata = yaml.safe_load(frontmatter_raw) or {}
    except yaml.YAMLError as exc:
        raise AssertionError(
            f"FINDING [AGENT-SKILL-SECURITY]: Invalid YAML frontmatter in "
            f"{path.relative_to(PROJECT_ROOT)}: {exc}"
        ) from exc

    if not isinstance(metadata, dict):
        raise AssertionError(
            f"FINDING [AGENT-SKILL-SECURITY]: Frontmatter must parse to a mapping in "
            f"{path.relative_to(PROJECT_ROOT)}."
        )
    return metadata, body
