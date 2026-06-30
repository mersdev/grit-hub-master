# Security Audit — Agents and Skills

This directory contains the active security tests for repository-defined custom agents and skills.
These tests are strict and **hard-fail** on policy violations to block insecure definitions.

---

## Quick Start

```powershell
# Option A: use existing virtual env (recommended)
.\.venv\Scripts\python -m pytest tests/security-script -v --no-cov -m security
```

If you don't have a virtual environment yet:

```powershell
python -m venv .venv
.\.venv\Scripts\python -m pip install --upgrade pip pytest pytest-cov pyyaml
```

Then run:

```powershell
.\.venv\Scripts\python -m pytest tests/security-script -v --no-cov -m security
```

Run one scenario only:

```powershell
.\.venv\Scripts\python -m pytest tests/security-script\test_agent_skills_prompt_injection.py -v --no-cov -m security
```

---

## Test Modules

| Module | Security Scenario | What It Checks |
|--------|-------------------|----------------|
| `test_agent_skills_frontmatter.py` | Agent/Skill Metadata Integrity | **Hard-fail** frontmatter + required `name`/`description` checks |
| `test_agent_skills_tool_least_privilege.py` | Agent Tool Least Privilege | **Hard-fail** explicit allowlist, no wildcard/all-tools, risky tool guardrails |
| `test_agent_skills_prompt_injection.py` | Agent Prompt Injection Guardrails | **Hard-fail** prompt-injection resistance language |
| `test_agent_skills_sensitive_disclosure.py` | Sensitive Disclosure & Policy Bypass | **Hard-fail** sensitive-data guardrails + no policy-bypass language |
| `test_agent_skills_excessive_agency.py` | Excessive Agency Controls | **Hard-fail** explicit confirmation/approval language for irreversible actions |
| `test_agent_skills_secret_hygiene.py` | Secret Hygiene | **Hard-fail** hardcoded secret pattern detection in markdown/scripts/configs |
| `test_agent_skills_supply_chain.py` | Skill Supply Chain / SkillSpector-style Review | **Hard-fail** prompt injection, data exfiltration, memory poisoning, MCP/tool overreach, dependency risk, and external skill review coverage |

---

## Reading the Results

| Status | Meaning |
|--------|---------|
| **PASSED** | The agent is already secure in this area |
| **FAILED** | Policy violation — test output includes `FINDING [...]` with affected file paths |

### Strict Module Behavior

`test_agent_skills_*.py` intentionally uses strict assertions (hard-fail mode).
Custom agent/skill profiles should fail fast when core controls are missing.

### Design Principles

1. **Hard-fail** — findings block the run.
2. **Single responsibility** — one scenario per `test_agent_skills_*` file.
3. **Policy focused** — tests cover metadata, least privilege, guardrails, secret hygiene, and SkillSpector-style skill supply-chain risk coverage.

## Troubleshooting

1. If `pytest` is not recognized, run with Python module form:
   `.\.venv\Scripts\python -m pytest ...`
2. If you see `Unknown pytest.mark.security`, ensure root `pytest.ini` contains the `security` marker.
3. If tests fail, read the `FINDING [...]` message; it includes the violating file paths to fix.

---

## Adding New Checks

1. Add tests under `test_agent_skills_<security-scenario>.py`.
2. Use hard assertions with `FINDING [...]` messages and file paths.
3. Mark with `pytestmark = pytest.mark.security`.
4. Reuse helpers in `conftest.py` and `agent_skills_security_utils.py`.
