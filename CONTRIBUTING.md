# Contributing to Copilot Agent Starter Kit

Thank you for contributing! Every new skill or agent makes the whole team more productive.

---

## TL;DR — Your First PR

Not technical yet? Start with the Development Coach and describe the work outcome in plain language:

```text
Help me build an agent for <team/task>. Ask me simple questions first.
```

The coach will recommend whether to reuse, improve, or create something new before you touch files.

1. **Pick what to add** (in order of team impact):
   - A new **skill** (`skills/<name>/SKILL.md`) — highest leverage, helps everyone
   - A new **agent** (`agents/<role>/<name>.agent.md`) — role-specific persona
   - A new **instruction** or **prompt**
   - A new **chatmode**
2. **Branch** off `main`: `feat/<your-name>-<short-slug>`
3. **Use a template** from `templates/` — copy and adapt
4. **Test** that `node scripts/setup.js --dry-run` still works
5. **Open a PR** — describe what it does and who benefits
6. **Ship it** — once merged, announce in Teams so the team can adopt it

---

## What Goes Where

| You're adding... | Put it in | File format |
|-----------------|-----------|-------------|
| Reusable capability (any role) | `skills/<name>/SKILL.md` | YAML frontmatter + markdown |
| Role-specific persona | `agents/<role>/<name>.agent.md` | YAML frontmatter + markdown |
| Code/style standards | `instructions/<name>.md` | Markdown |
| One-shot prompt | `prompts/<name>.prompt.md` | Markdown |
| Chat mode | `chatmodes/<name>.chatmode.md` | YAML frontmatter + markdown |
| Repo script | `scripts/<name>.{js,py,sh}` | JavaScript, Python, or shell |

**Rule of thumb**: if more than one role would use it → it's a skill. If it's persona-specific → it's an agent.

Before adding a new skill, run the Skill Picker logic: no skill → one local skill → few local skills → improve existing skill → create a new focused skill → only then consider external skills.

---

## Front-matter Contract

Every `.md` file (except READMEs) starts with YAML front-matter:

```yaml
---
name: "Human-readable name"
description: "One-sentence summary — helps Copilot pick this asset"
version: "1.0.0"
metadata:
  category: [memory|learning|visual-design|development|research|document-generation]
  tags: [tag1, tag2]
---
```

---

## File Naming

- `kebab-case`, all lowercase
- Skill folders: `skills/my-new-skill/SKILL.md`
- Agent files: `agents/developer/my-agent.agent.md`
- No spaces, no underscores in folder/file names

---

## Quality Checklist

Before opening a PR:

- [ ] Has valid YAML front-matter (name, description, version)
- [ ] File follows the template structure
- [ ] Description is clear enough for Copilot to auto-trigger
- [ ] Skill list is short and relevant; no "just in case" skills
- [ ] `node scripts/setup.js --dry-run` still works
- [ ] No personal data, secrets, or PII in the file
- [ ] README in the skill/agent folder if non-trivial

---

## Testing Your Contribution

```bash
# Verify setup still works
node scripts/setup.js --dry-run

# Test your skill manually
# 1. Run setup to install to ~/.copilot/skills/ and .github/skills/
node scripts/setup.js --all --skip-python
# 2. Start a new Copilot session
# 3. Ask Copilot something that should trigger your skill
# 4. Verify it uses the skill's behaviour
```

---

## Review Process

1. Open PR with description of what your skill/agent does
2. Tag at least one reviewer
3. Reviewer checks: quality bar, no PII, follows templates
4. Merge to `main`
5. Announce in team channel

---

## Ideas for Contributions

### Skills (highest impact)
- `jira-ticket-formatter` — format requirements as Jira tickets
- `meeting-notes-summarizer` — structured meeting notes
- `ci-cd-pipeline` — generate GitHub Actions workflows
- `docs-generator` — auto-generate API/project documentation
- `cost-estimation` — effort estimation for features

### Agents
- `consultant/retro-facilitator` — facilitate retrospectives
- `architect/system-designer` — design system architectures
- `quality-assurance/qa-test-designer` — design test strategies

### Learning Paths
- Data Engineering path
- Security Engineering path
- Mobile Development path
