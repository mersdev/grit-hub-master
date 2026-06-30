---
name: "Agent Guardrail Checklist"
description: "Mandatory security and compliance checks for all agents before deployment"
version: "1.0.0"
---

# Security & Guardrail Checklist

Every agent must pass this checklist before being considered complete. These guardrails ensure team safety, data security, and compliance with DHL standards.

---

## 🔐 Data Protection (Mandatory)

- [ ] **No PII in examples** — All code examples use placeholder values only
  - ✅ Good: `"john.doe@example.com"`, `"+1-555-0100"`, `"123 Example St"`
  - ❌ Bad: Real email addresses, phone numbers, names, or addresses

- [ ] **No secrets in code** — No API keys, tokens, passwords, or credentials hardcoded
  - ✅ Good: Use `$env:MY_API_KEY` or `.env` files
  - ❌ Bad: `const apiKey = "sk-1234567890abcdef"`

- [ ] **Memory privacy** — Agent does not store real PII to memory without encryption
  - ✅ Good: Store references, categories, roles (no personal data)
  - ❌ Bad: Store real emails, phone numbers, SSNs, passport numbers

- [ ] **Logs sanitized** — If logs are generated, mask sensitive data
  - ✅ Good: Log user as `user-***-1234` (last 4 chars only)
  - ❌ Bad: Log full email or phone number

---

## 🧪 Skill Supply Chain Review (Mandatory)

These checks are SkillSpector-style controls for prompt injection, data exfiltration, tool least privilege, least-privilege access, memory poisoning, MCP overreach, dependency risk, external skill review, and untrusted skill content.

- [ ] **Prompt injection checked** — Skill or agent does not contain instructions to ignore higher-priority rules, bypass safety, or hide behaviour
  - ✅ Good: Clear task instructions only
  - ❌ Bad: "Ignore previous instructions", "always comply", hidden comments that change behaviour

- [ ] **No data exfiltration path** — Skill does not send files, logs, tokens, memory, or environment variables outside approved systems
  - ✅ Good: Local-only processing unless user approves a destination
  - ❌ Bad: Upload scripts, webhooks, or telemetry with unclear purpose

- [ ] **Tool least privilege** — Tools and MCP servers are limited to what the task needs
  - ✅ Good: Read-only file access for documentation review
  - ❌ Bad: Shell, browser, network, and full filesystem access "just in case"

- [ ] **External skill reviewed** — Any third-party skill has source, maintenance, dependencies, and permissions review before recommendation or install
  - ✅ Good: Known source, maintained repo, clear permissions
  - ❌ Bad: Unknown source, broad install script, unclear owner

---

## 🛡️ Access Control (Mandatory)

- [ ] **Role clarity** — Agent clearly states what roles it applies to
  - ✅ Good: `applies_to: ["developer", "architect"]`
  - ❌ Bad: No role declaration; assumes universal access

- [ ] **Scope limits** — Agent does not attempt to access resources outside its scope
  - ✅ Good: Developer agent accesses code and logs
  - ❌ Bad: Developer agent tries to access financial systems

- [ ] **Permission warnings** — Agent warns before taking dangerous actions
  - ✅ Good: "⚠️ This will delete 10 files. Continue? [y/n]"
  - ❌ Bad: Silently destructive operations

---

## 🔍 Code Quality (Mandatory)

- [ ] **No hallucination** — Agent does not fabricate information
  - ✅ Good: "I don't know this; let me research it"
  - ❌ Bad: Making up documentation or code behavior

- [ ] **Error handling** — Examples include error cases, not just happy paths
  - ✅ Good: Try-catch blocks, null checks, validation
  - ❌ Bad: Only works if everything goes perfectly

- [ ] **Dependencies safe** — All referenced libraries are vetted and non-malicious
  - ✅ Good: Popular, maintained packages from npm/PyPI
  - ❌ Bad: Obscure packages or typosquatting (e.g., `reqeusts` instead of `requests`)

---

## 📋 Clarity & Documentation (Mandatory)

- [ ] **Clear description** — Agent description is 1-2 sentences, explains persona & purpose
  - ✅ Good: "Expert full-stack engineer writing clean, tested code"
  - ❌ Bad: "Agent thing"

- [ ] **Responsibilities clear** — Each responsibility explains what the agent does (1-2 sentences)
  - ✅ Good: "Write production code — clean, typed, tested, documented"
  - ❌ Bad: "Do stuff"

- [ ] **Version set** — Agent has a semantic version number (e.g., `1.0.0`)
  - ✅ Good: `version: "1.0.0"`
  - ❌ Bad: No version or invalid format

- [ ] **Workflow documented** — If steps are involved, they are documented clearly
  - ✅ Good: "1. Understand request → 2. Explore code → 3. Implement → 4. Test"
  - ❌ Bad: Vague instructions

---

## 🛠️ Technical Requirements (Mandatory)

- [ ] **Valid YAML frontmatter** — Frontmatter is valid YAML with required fields
  - Required: `name`, `description`, `version`, `applies_to`, `tools`, `skills`
  - Test: `python -m yaml < agent-file.md` (no errors)

- [ ] **File location correct** — Agent is in the right folder
  - ✅ Good: `agents/<role>/<agent-name>.agent.md`
  - ❌ Bad: Wrong folder or wrong filename format

- [ ] **Skills exist** — All listed skills are documented in `skills/` folder
  - Test: `ls ~/.copilot/skills/ | grep <skill-name>`

- [ ] **Setup test passes** — `node setup.js --dry-run` completes without errors
  - Test: Run `node setup.js --dry-run` in the repo root

---

## 👥 Team Alignment (Recommended)

- [ ] **No personal context** — Agent does not reference personal memory, personality, or individual preferences
  - ✅ Good: "Follow team conventions stored in memory"
  - ❌ Bad: "Use my preferred style" or "Remember my projects"

- [ ] **Shareable** — Another team member can use this agent without modification
  - ✅ Good: Role-based (works for any Developer)
  - ❌ Bad: Customized to one person's workflow

- [ ] **Platform agnostic** — Agent works in both GitHub CLI and VS Code
  - ✅ Good: Uses standard Copilot features
  - ❌ Bad: Assumes GitHub CLI only

---

## 🚀 Before Merging to Main

**Checklist for PR reviewers:**

- [ ] All "Mandatory" checkboxes above are checked
- [ ] No PII or secrets in agent description or examples
- [ ] Role is clearly documented
- [ ] Guardrails section is not removed or weakened
- [ ] Passes `node setup.js --dry-run` without errors
- [ ] Description explains what the agent does and who benefits
- [ ] At least one example interaction is provided
- [ ] Skill supply-chain review is complete for any new or external skill

---

## 🤔 If You're Unsure

**Common questions:**

**Q: Can I store user names in memory?**  
A: No. Store role, team, or category instead (e.g., `team: "logistics-platform"`). Never store personal names.

**Q: Can I use `<your-name>` in agent description?**  
A: No. Agent is for the team, not individuals. Use role name instead (e.g., "Developer", "Tester").

**Q: What if I hardcode a test API key (for documentation)?**  
A: Use a publicly documented example key like GitHub provides in docs, or use a clearly marked placeholder like `sk-test-1234567890abcdefghijk`.

**Q: Can I reference "my preferred tech stack"?**  
A: No. Reference team standards or ask the user to provide their stack. Agents are role-based, not personal.

**Q: Do I need to provide boot/startup code?**  
A: No. The main `agent_boot.py` handles startup for CLI. Agents are just personas.

---

## Example: Agent That Passes

See `agents/developer/fullstack-engineer.agent.md` for an agent that passes all checks.

---

## Report Issues

Found an agent that doesn't pass these checks?
1. Open an issue in the repo
2. Tag the agent author
3. Cite which checklist items are failing
4. The author has 1 week to fix or the agent is removed

See `CONTRIBUTING.md` for the full review process.
