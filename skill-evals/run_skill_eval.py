#!/usr/bin/env python3
"""Evaluate GRIT Hub skills for readiness.

This script is intentionally local and dependency-light. It checks every
skills/<skill>/SKILL.md for metadata quality, trigger clarity, required usage
sections, output format guidance, safety guardrails, token size, and optional
per-skill JSONL prompt cases.

Usage:
  python skill-evals/run_skill_eval.py --all
  python skill-evals/run_skill_eval.py --skill skill-picker
  python skill-evals/run_skill_eval.py --all --strict
  python skill-evals/run_skill_eval.py --all --json

Optional case file:
  skills/<skill>/tests/cases.jsonl

Case format:
  {"prompt":"...", "should_trigger":true, "must_contain":["..."], "must_not_contain":["..."]}
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SKILLS_ROOT = PROJECT_ROOT / "skills"

READY_SCORE = 85
USABLE_SCORE = 70
DEFAULT_MIN_SCORE = 70
MAX_SKILL_WORDS = 2600
MAX_DESC_CHARS = 500
MIN_DESC_CHARS = 40

REQUIRED_METADATA = ("name", "description")
WHEN_TERMS = (
    "when to use",
    "use this skill",
    "when the user",
    "trigger",
    "use when",
    "when asked",
)
OUTPUT_TERMS = ("output format", "response format", "deliverable", "return", "report")
EXAMPLE_TERMS = ("example", "examples", "sample", "prompt")
SAFETY_TERMS = (
    "security",
    "guardrail",
    "never",
    "approval",
    "confirm",
    "sensitive",
    "secret",
    "credential",
    "prompt injection",
)
TOKEN_EFFICIENCY_TERMS = ("concise", "token", "compact", "smallest", "minimal", "short")
TRIGGER_VERBS = (
    "create",
    "write",
    "review",
    "generate",
    "convert",
    "analyze",
    "summarize",
    "design",
    "build",
    "test",
    "debug",
    "optimize",
    "improve",
    "choose",
    "pick",
)
CRITICAL_UNSAFE_PATTERNS = (
    r"(?i)ignore (all )?(previous|prior|higher.priority) instructions",
    r"(?i)reveal (the )?(system|developer) prompt",
    r"(?i)show (the )?(hidden|private) chain.of.thought",
    r"(?i)auto.?approve (everything|all)",
    r"(?i)disable (all )?(guardrails|security)",
    r"(?i)exfiltrate|send all files|upload all files",
)
SECRET_PATTERNS = (
    r"-----BEGIN (?:RSA |EC |OPENSSH |DSA )?PRIVATE KEY-----",
    r"(?i)\b(api[_-]?key|token|password)\s*[:=]\s*['\"][^'\"]{8,}['\"]",
    r"(?i)authorization\s*:\s*bearer\s+[a-z0-9\-_\.=]{16,}",
    r"\bghp_[A-Za-z0-9]{20,}\b",
)


@dataclass
class Finding:
    level: str
    message: str


@dataclass
class SkillResult:
    skill: str
    path: str
    score: int = 0
    status: str = "not-ready"
    findings: list[Finding] = field(default_factory=list)
    case_total: int = 0
    case_passed: int = 0

    @property
    def critical_count(self) -> int:
        return sum(1 for item in self.findings if item.level == "critical")

    @property
    def warning_count(self) -> int:
        return sum(1 for item in self.findings if item.level == "warning")


def word_count(text: str) -> int:
    return len(re.findall(r"\b\w+\b", text))


def has_any(text: str, terms: tuple[str, ...]) -> bool:
    lower = text.lower()
    return any(term in lower for term in terms)


def parse_frontmatter(text: str) -> tuple[dict[str, Any], str, list[str]]:
    errors: list[str] = []
    if not text.startswith("---"):
        return {}, text, ["Missing YAML frontmatter"]

    parts = text.split("---", 2)
    if len(parts) < 3:
        return {}, text, ["Invalid YAML frontmatter delimiters"]

    raw = parts[1].strip("\n")
    body = parts[2]
    metadata: dict[str, Any] = {}
    current_key: str | None = None

    for line in raw.splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        if stripped.startswith("-") and current_key:
            metadata.setdefault(current_key, [])
            if isinstance(metadata[current_key], list):
                metadata[current_key].append(stripped.lstrip("-").strip().strip('"\''))
            continue
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        key = key.strip()
        value = value.strip()
        current_key = key
        if not value:
            metadata[key] = []
        elif value.startswith("[") and value.endswith("]"):
            metadata[key] = [item.strip().strip('"\'') for item in value[1:-1].split(",") if item.strip()]
        else:
            metadata[key] = value.strip('"\'')

    return metadata, body, errors


def add(result: SkillResult, level: str, message: str) -> None:
    result.findings.append(Finding(level=level, message=message))


def score_metadata(result: SkillResult, metadata: dict[str, Any]) -> int:
    score = 0
    for key in REQUIRED_METADATA:
        if metadata.get(key):
            score += 5
        else:
            add(result, "critical", f"Missing frontmatter field `{key}`")

    description = str(metadata.get("description") or "").strip()
    if description:
        desc_len = len(description)
        if MIN_DESC_CHARS <= desc_len <= MAX_DESC_CHARS:
            score += 5
        else:
            add(result, "warning", f"Description length should be {MIN_DESC_CHARS}-{MAX_DESC_CHARS} chars; got {desc_len}")

        if any(verb in description.lower() for verb in TRIGGER_VERBS):
            score += 5
        else:
            add(result, "warning", "Description should include clear action/trigger verbs")
    return score


def score_body(result: SkillResult, body: str) -> int:
    score = 0
    if has_any(body, WHEN_TERMS):
        score += 10
    else:
        add(result, "warning", "Missing clear 'when to use' guidance")

    if has_any(body, OUTPUT_TERMS):
        score += 10
    else:
        add(result, "warning", "Missing output/response format guidance")

    if has_any(body, EXAMPLE_TERMS):
        score += 10
    else:
        add(result, "warning", "Missing examples or sample prompts")

    if has_any(body, SAFETY_TERMS):
        score += 15
    else:
        add(result, "critical", "Missing security/safety guardrails")

    if has_any(body, TOKEN_EFFICIENCY_TERMS):
        score += 5
    else:
        add(result, "warning", "Missing token-efficiency guidance")

    headings = re.findall(r"^#{1,3}\s+", body, flags=re.MULTILINE)
    if len(headings) >= 3:
        score += 5
    else:
        add(result, "warning", "Skill should be structured with at least 3 headings")

    return score


def line_is_guardrail(line: str) -> bool:
    lower = line.lower()
    safe_context = (
        "reject",
        "refuse",
        "never",
        "do not",
        "don't",
        "must not",
        "forbid",
        "forbidden",
        "block",
        "unsafe",
        "prompt injection",
        "guardrail",
        "hidden",
        "private",
        "secret",
        "leak",
        "escalate",
    )
    return any(term in lower for term in safe_context)


def score_security(result: SkillResult, full_text: str) -> int:
    score = 15
    for pattern in CRITICAL_UNSAFE_PATTERNS:
        for line_no, line in enumerate(full_text.splitlines(), 1):
            if not re.search(pattern, line):
                continue
            if line_is_guardrail(line):
                continue
            add(result, "critical", f"Unsafe instruction pattern found at line {line_no}: {pattern}")
            score -= 5
    for pattern in SECRET_PATTERNS:
        if re.search(pattern, full_text):
            add(result, "critical", f"Potential hardcoded secret pattern found: {pattern}")
            score -= 10
    return max(score, 0)


def score_size(result: SkillResult, full_text: str) -> int:
    words = word_count(full_text)
    if words <= MAX_SKILL_WORDS:
        return 10
    add(result, "warning", f"Skill is long: {words} words; target <= {MAX_SKILL_WORDS}")
    return 5 if words <= MAX_SKILL_WORDS * 1.5 else 0


def load_cases(skill_dir: Path) -> list[dict[str, Any]]:
    cases_path = skill_dir / "tests" / "cases.jsonl"
    if not cases_path.exists():
        return []
    cases: list[dict[str, Any]] = []
    for line_no, line in enumerate(cases_path.read_text(encoding="utf-8").splitlines(), 1):
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        try:
            cases.append(json.loads(stripped))
        except json.JSONDecodeError as exc:
            cases.append({"_invalid": f"{cases_path}:{line_no}: {exc}"})
    return cases


def case_matches_skill(prompt: str, metadata: dict[str, Any], body: str, skill_name: str) -> bool:
    prompt_lower = prompt.lower()
    skill_phrase = skill_name.replace("-", " ")
    if skill_name in prompt_lower or skill_phrase in prompt_lower:
        return True

    haystack = " ".join(
        str(value)
        for value in [metadata.get("name", ""), metadata.get("description", ""), skill_name, body[:4000]]
    ).lower()
    prompt_tokens = {token for token in re.findall(r"[a-z0-9][a-z0-9-]{2,}", prompt_lower)}
    haystack_tokens = {token for token in re.findall(r"[a-z0-9][a-z0-9-]{2,}", haystack)}
    stop_tokens = {"this", "that", "with", "from", "into", "help", "create", "make", "use", "user", "users"}
    overlap = (prompt_tokens - stop_tokens) & haystack_tokens
    return len(overlap) >= 2


def score_cases(result: SkillResult, skill_dir: Path, metadata: dict[str, Any], body: str) -> int:
    cases = load_cases(skill_dir)
    if not cases:
        add(result, "warning", "No optional prompt cases found at tests/cases.jsonl")
        return 5

    passed = 0
    for case in cases:
        result.case_total += 1
        if "_invalid" in case:
            add(result, "critical", f"Invalid case JSON: {case['_invalid']}")
            continue

        prompt = str(case.get("prompt") or "")
        should_trigger = bool(case.get("should_trigger", True))
        predicted = case_matches_skill(prompt, metadata, body, result.skill)
        ok = predicted == should_trigger

        full_text = f"{metadata}\n{body}".lower()
        for term in case.get("must_contain", []) or []:
            if str(term).lower() not in full_text:
                ok = False
                add(result, "warning", f"Case requires missing term `{term}`")
        for term in case.get("must_not_contain", []) or []:
            if str(term).lower() in full_text:
                ok = False
                add(result, "critical", f"Case forbids present term `{term}`")

        if ok:
            passed += 1
        else:
            expected = "trigger" if should_trigger else "not trigger"
            actual = "trigger" if predicted else "not trigger"
            add(result, "warning", f"Prompt case mismatch: expected {expected}, predicted {actual}: {prompt[:80]}")

    result.case_passed = passed
    if result.case_total == 0:
        return 0
    ratio = passed / result.case_total
    return round(ratio * 10)


def evaluate_skill(skill_dir: Path) -> SkillResult:
    skill_file = skill_dir / "SKILL.md"
    result = SkillResult(skill=skill_dir.name, path=str(skill_file.relative_to(PROJECT_ROOT)))

    if not skill_file.exists():
        add(result, "critical", "Missing SKILL.md")
        return result

    text = skill_file.read_text(encoding="utf-8")
    metadata, body, fm_errors = parse_frontmatter(text)
    for error in fm_errors:
        add(result, "critical", error)

    result.score += score_metadata(result, metadata)
    result.score += score_body(result, body)
    result.score += score_security(result, text)
    result.score += score_size(result, text)
    result.score += score_cases(result, skill_dir, metadata, body)
    result.score = max(0, min(100, result.score))

    if result.critical_count:
        result.status = "not-ready"
    elif result.score >= READY_SCORE:
        result.status = "ready"
    elif result.score >= USABLE_SCORE:
        result.status = "needs-improvement"
    else:
        result.status = "not-ready"
    return result


def find_skill_dirs(skill: str | None = None) -> list[Path]:
    if skill:
        target = SKILLS_ROOT / skill
        return [target]
    return sorted(path for path in SKILLS_ROOT.iterdir() if path.is_dir() and (path / "SKILL.md").exists())


def print_text_report(results: list[SkillResult]) -> None:
    total = len(results)
    ready = sum(1 for item in results if item.status == "ready")
    needs = sum(1 for item in results if item.status == "needs-improvement")
    failed = sum(1 for item in results if item.status == "not-ready")
    avg = round(sum(item.score for item in results) / total, 1) if total else 0

    print("Skill readiness report")
    print("=" * 72)
    print(f"Skills tested: {total}")
    print(f"Ready: {ready} | Needs improvement: {needs} | Not ready: {failed} | Avg score: {avg}")
    print()

    for item in sorted(results, key=lambda r: (r.status != "not-ready", r.score, r.skill)):
        case_info = f" cases {item.case_passed}/{item.case_total}" if item.case_total else " no cases"
        print(f"[{item.status.upper():17}] {item.score:3d}/100 {item.skill} ({case_info})")
        shown = 0
        for finding in item.findings:
            if finding.level == "critical" or shown < 3:
                print(f"  - {finding.level}: {finding.message}")
                shown += 1
        remaining = len(item.findings) - shown
        if remaining > 0:
            print(f"  - ... {remaining} more finding(s)")
    print()
    print("Ready threshold: >=85 with no critical findings")
    print("CI/default pass threshold: >=70 with no critical findings, unless --strict is used")


def main() -> int:
    parser = argparse.ArgumentParser(description="Evaluate GRIT Hub skill readiness")
    target = parser.add_mutually_exclusive_group(required=True)
    target.add_argument("--all", action="store_true", help="Evaluate all skills")
    target.add_argument("--skill", help="Evaluate one skill folder name")
    parser.add_argument("--strict", action="store_true", help="Fail unless every skill is ready (>=85 and no critical findings)")
    parser.add_argument("--min-score", type=int, default=DEFAULT_MIN_SCORE, help="Minimum score for non-strict mode")
    parser.add_argument("--json", action="store_true", help="Output JSON report")
    args = parser.parse_args()

    skill_dirs = find_skill_dirs(None if args.all else args.skill)
    if not skill_dirs:
        print("No skills found", file=sys.stderr)
        return 2

    results = [evaluate_skill(path) for path in skill_dirs]

    if args.json:
        print(json.dumps([item.__dict__ | {"findings": [f.__dict__ for f in item.findings]} for item in results], indent=2))
    else:
        print_text_report(results)

    if args.strict:
        bad = [item for item in results if item.status != "ready"]
    else:
        bad = [item for item in results if item.critical_count or item.score < args.min_score]

    return 1 if bad else 0


if __name__ == "__main__":
    raise SystemExit(main())
