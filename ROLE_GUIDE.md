---
name: "Role-Based Customization Guide"
description: "Step-by-step guide to customize your agent for your specific role"
version: "1.0.0"
---

# Role-Based Customization

After cloning and setup, explore available agents and customize one for your role.

---

## 📋 All Available Agents in This Repo

### Role-Based Agents

| Role | Agent File | Status | Use Case |
|------|-----------|--------|----------|
| **Developer** | `agents/developer/fullstack-engineer/fullstack-engineer.agent.md` | ✅ Ready | Code review, debugging, architecture decisions |
| **Team Manager** | `agents/team-manager/team-coordinator/team-coordinator.agent.md` | ✅ Ready | Team coordination, status reports, presentations |
| **Quality Assurance** | `agents/quality-assurance/qa-strategist/qa-strategist.agent.md` | ✅ Ready | Test strategy, edge cases, bug tracking |
| **Project Manager** | `agents/project-manager/planning-agent/planning-agent.agent.md` | ✅ Ready | Sprint planning, risk tracking, estimation |
| **Architect** | `agents/architect/system-designer/system-designer.agent.md` | ✅ Ready | System design, technical decisions, architecture |
| **Consultant** | `agents/consultant/advisory-agent/advisory-agent.agent.md` | ✅ Ready | Advisory, best practices, mentoring |
| **Support** | `agents/support/troubleshooter/troubleshooter.agent.md` | ✅ Ready | Diagnose issues, document solutions, support |
| **AI Engineer** | `agents/ai-engineer/model-evaluator-specialist/model-evaluator-specialist.agent.md` | ✅ Ready | LLM agents, RAG systems, prompt engineering |

### Everyone Agents (Available to All)

| Agent | Agent File | Purpose |
|-------|-----------|---------|
| **WFH Leave Submission** | `agents/everyone/wfh-leave-submission/wfh-leave-submission.agent.md` | Automate WFH leave submission to MyPortalPlus |
| **Daily Assistant** | `agents/everyone/daily-assistant/daily-assistant.agent.md` | Daily tasks, routine automation, reminders |

### Development/Utility Agents

| Agent | Agent File | Purpose |
|-------|-----------|---------|
| **Development Coach** | `agents/ai-engineer/development-coach/development-coach.agent.md` | Learning path tracking, skill development |

---

## 🎯 Available Skills (Adoptable in Your Agents)

### Core Skills

| Skill | File | Purpose | When to Use |
|-------|------|---------|------------|
| **Memory Recall** | `skills/memory-recall/SKILL.md` | Surface relevant memories with hierarchical search | "I need to remember..." |
| **Memory Save** | `skills/memory-save/SKILL.md` | Persist important information to long-term memory | After learning something important |
| **Learning Tracker** | `skills/learning-tracker/SKILL.md` | Track skill progression and suggest next steps | Check your development path |
| **Deep Research** | `skills/deep-research/SKILL.md` | Systematic multi-source research and synthesis | Investigate complex topics |
| **Code Review** | `skills/code-review/SKILL.md` | Structured code review (security, performance, maintainability) | Review PRs or audit code |
| **Draw.io** | `skills/drawio/SKILL.md` | Create diagrams (flowcharts, architecture, UML, network) | Design architectures, visualize flows |
| **PPTX Agent** | `skills/pptx-agent/SKILL.md` | DHL-branded PowerPoint generation with diagrams | Create presentations |

---

## 🚀 How to Customize Your Agent

### Step 1: Choose Your Role

Find your role's agent from the table above.

### Step 2: Open the Agent File

```powershell
# Example for Developer
code agents/developer/fullstack-engineer/fullstack-engineer.agent.md
```

### Step 3: Customize the Agent

Update these sections:

```yaml
## Persona

You are an expert full-stack engineer with deep knowledge of:
- [Your tech stack]
- [Your platforms]
- [Your databases]
- [Your tools]
```

### Step 4: Choose Your Skills

Edit the `skills:` section to include skills that match your workflow:

```yaml
skills:
  - memory-recall           # Remember team conventions
  - memory-save             # Document decisions
  - code-review             # Review PRs
  - deep-research           # Investigate technologies
  - learning-tracker        # Track progress
  # Add or remove as needed
```

### Step 5: Add Role-Specific Guardrails

```yaml
## Guardrails

### ✓ Always
- [Your team requirement 1]
- [Your team requirement 2]

### ✗ Never
- [Your team restriction 1]
```

### Step 6: Reload & Test

- **VS Code/IDE:** `Ctrl+Shift+P` → "Developer: Reload Window"
- **CLI:** Restart terminal session

Changes take effect immediately.

---

## 📖 Recommended Skills per Role

### 🧑‍💻 Developer
```yaml
skills:
  - code-review
  - memory-recall
  - memory-save
  - learning-tracker
  - deep-research
```

### 👔 Team Manager
```yaml
skills:
  - memory-save
  - memory-recall
  - learning-tracker
  - pptx-agent
  - deep-research
```

### 🧪 Quality Assurance
```yaml
skills:
  - deep-research
  - code-review
  - memory-recall
  - memory-save
  - drawio
```

### 📊 Project Manager
```yaml
skills:
  - memory-recall
  - memory-save
  - pptx-agent
  - learning-tracker
  - deep-research
```

### 🏗️ Architect
```yaml
skills:
  - drawio
  - memory-recall
  - memory-save
  - deep-research
```

### 💼 Consultant
```yaml
skills:
  - memory-recall
  - memory-save
  - deep-research
  - learning-tracker
```

### 🛠️ Support
```yaml
skills:
  - memory-recall
  - memory-save
  - code-review
  - deep-research
```

### 🤖 AI Engineer
```yaml
skills:
  - memory-recall
  - memory-save
  - learning-tracker
  - deep-research
  - drawio
```

---

## 💾 Save Team Knowledge After Customizing

Make your customizations stick by saving to memory:

```powershell
python ~/.copilot/memory/memory_manager.py save \
  --type semantic \
  --content "Our team uses: [your tech stack, conventions, standards]" \
  --tags "team,standards,<your-role>" \
  --importance 8
```

This makes agent decisions consistent across the team.

---

## ❓ Questions?

- **See all agents:** [instructions/AGENTS.md](./instructions/AGENTS.md)
- **Contributing new agents:** [CONTRIBUTING.md](./CONTRIBUTING.md)
- **Platform issues:** [PLATFORM_SUPPORT.md](./PLATFORM_SUPPORT.md)
- **Security standards:** [security/guardrail-checklist.md](./security/guardrail-checklist.md)
