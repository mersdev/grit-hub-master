from __future__ import annotations

import pathlib
import re
from typing import Iterable

from conftest import PROJECT_ROOT

RISKY_TOOLS = {"bash", "powershell", "runinterminal", "execute", "shell"}

PROMPT_INJECTION_GUARDRAIL_TERMS = (
    "ignore previous instructions",
    "never reveal",
    "do not reveal",
    "must not reveal",
    "prompt injection",
    "system prompt",
)

SENSITIVE_DATA_GUARDRAIL_TERMS = (
    "never store passwords",
    "never store tokens",
    "never log",
    "sensitive data",
    "mask sensitive",
    "redact",
    "credentials",
)

DESTRUCTIVE_CONFIRMATION_TERMS = (
    "explicit confirmation",
    "confirm",
    "approval",
    "consent",
    "before submitting",
    "before deleting",
)

BYPASS_APPROVAL_PATTERNS = (
    "bypass approval",
    "skip approval",
    "ignore policy",
    "disable guardrail",
    "override security",
    "auto-approve everything",
)

SECRET_PATTERNS = [
    re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH |DSA )?PRIVATE KEY-----"),
    re.compile(r"(?i)\bapi[_-]?key\s*[:=]\s*['\"][^'\"]{8,}['\"]"),
    re.compile(r"(?i)\btoken\s*[:=]\s*['\"][^'\"]{8,}['\"]"),
    re.compile(r"(?i)\bpassword\s*[:=]\s*['\"][^'\"]{4,}['\"]"),
    re.compile(r"(?i)authorization\s*:\s*bearer\s+[a-z0-9\-_\.=]{16,}"),
    re.compile(r"\bghp_[A-Za-z0-9]{20,}\b"),
]


def rel(path: pathlib.Path) -> str:
    return str(path.relative_to(PROJECT_ROOT))


def format_finding(
    code: str,
    title: str,
    violations: Iterable[str],
    fix_hint: str,
    impact: str | None = None,
) -> str:
    """Return a consistent, readable failure message for debugging."""
    items = sorted(str(v) for v in violations)
    lines = [f"FINDING [{code}]: {title}"]
    if impact:
        lines.append(f"Impact: {impact}")
    lines.append(f"Total Violations: {len(items)}")
    lines.append(f"Fix Hint: {fix_hint}")
    lines.append("Affected Files:")
    lines.extend(f"{i}. {item}" for i, item in enumerate(items, 1))
    return "\n".join(lines)
