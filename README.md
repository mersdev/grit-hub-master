# GRIT Hub

A team-ready AI agent framework for GitHub Copilot with persistent memory, learning tracking, specialized role-based agents, and reusable skills.

---

## Quick Start

Choose your platform:

### 🖥️ GitHub Copilot CLI (4 Minutes)

```powershell
# Step 1: Install
winget install GitHub.Copilot

# Step 2: Run
copilot

# Step 3: Login
/login

# Step 4: Initialize your agent
Init & wire my new Agent <Your-Name> and Implement Learning Path, Memory System, Skills System, MCP Integration, Personality & Soul.md into copilot from https://dhl.ghe.com/SMP-Mobile-Customer-Data-Domai/grit-hub
```

**Example:** `Init & wire my new Agent Alex and Implement Learning Path, Memory System, Skills System, MCP Integration, Personality & Soul.md into copilot from https://dhl.ghe.com/SMP-Mobile-Customer-Data-Domai/grit-hub`

**Daily Use:**
```powershell
# Launch Copilot CLI
copilot

# Initialize with your agent
init agent Alex
```

---

### 💻 IDE Copilot (VS Code/JetBrains) (2 Minutes)

```powershell
# Step 1: Clone and install
git clone https://dhl.ghe.com/SMP-Mobile-Customer-Data-Domai/grit-hub.git
cd grit-hub
npm install

# Step 2: Reload IDE
# Ctrl+Shift+P → "Developer: Reload Window"

# Step 3: Start using
# Open Copilot Chat → Ask: "What agents are available?"
```

---

**See [ONBOARDING.md](./ONBOARDING.md) for detailed instructions.**

---

## What You Get

| Component | Description |
|-----------|-------------|
| **Agents** | Specialized role-based AI personas (e.g., Developer, Team Manager, Quality Assurance, Architect, AI Engineer, Angular Specialist) |
| **Skills** | Reusable capabilities (e.g., memory-recall, code-review, pptx-agent, drawio, portal-generation) |
| **Memory System** | Persistent knowledge across sessions (SQLite + PageIndex RAG + FTS5) |
| **Learning Tracker** | 5-level skill progression (Novice → Master) with curriculum |
| **MCP Integration** | Model Context Protocol servers (filesystem, web, memory, thinking, drawio) |
| **Security** | PII protection, secret scanning, guardrails |

---

## Agent Roles

| Role | Use Case | Example |
|------|----------|---------|
| **Developer** | Code review, debugging, implementation | "Review this authentication code" |
| **Team Manager** | Team coordination, status tracking, presentations | "Generate sprint status deck" |
| **Quality Assurance** | Test strategy, edge cases, bug reports | "Design test cases for login flow" |
| **Architect** | System design, architecture decisions | "Design microservices architecture" |
| **AI Engineer** | LLM agents, RAG systems, prompt engineering | "Build a RAG retrieval pipeline" |
| **Everyone** | Daily tasks, meeting notes, leave submission, portal generation | "Submit WFH leave for tomorrow" |

**+ More specialized agents** (Angular, React, Azure, AWS, API Designer, Security Auditor, etc.)

---

## Repository Structure

```
grit-hub/
├── agents/           # Specialized agent personas (Developer, Team Manager, Quality Assurance, etc.)
├── skills/           # Reusable capabilities (memory, code-review, pptx, etc.)
├── memory/           # Persistent memory system (SQLite + PageIndex)
├── learning/         # Learning path tracker (5-level progression)
├── mcp/              # MCP server configurations
├── security/         # Security guardrails
├── templates/        # Templates for new agents/skills
├── setup.js          # Unified setup script
└── ONBOARDING.md     # Detailed setup guide
```

---

## Documentation

| File | Purpose |
|------|---------|
| [ONBOARDING.md](./ONBOARDING.md) | Platform-specific setup guides (CLI and IDE) |
| [CONTRIBUTING.md](./CONTRIBUTING.md) | How to add new skills and agents |
| [ROLE_GUIDE.md](./ROLE_GUIDE.md) | Role-based customization guide |
| [PLATFORM_SUPPORT.md](./PLATFORM_SUPPORT.md) | CLI vs IDE comparison and troubleshooting |

---

## Troubleshooting

### CLI Issues

| Issue | Fix |
|-------|-----|
| winget not found | Update Windows or install from [Microsoft Store](https://aka.ms/getwinget) |
| /login not working | Ensure GitHub Copilot subscription is active |
| Agent initialization fails | Check internet connection for repository access |

### IDE Issues

| Issue | Fix |
|-------|-----|
| Agents not visible | Reload IDE: Ctrl+Shift+P → "Developer: Reload Window" |
| Copilot Chat not responding | Ensure Copilot extension is signed in |
| Memory commands fail | Verify Python 3.10+: `python --version` |

**See [ONBOARDING.md](./ONBOARDING.md) for detailed troubleshooting.**

---

## Contributing

We welcome contributions! See [CONTRIBUTING.md](./CONTRIBUTING.md) for details.

**High-impact contributions:**
- ⭐⭐⭐ New reusable **skills** (helps everyone)
- ⭐⭐ New role-specific **agents**
- ⭐⭐ New **learning path** curricula
- 🛡️ New **security guardrails**

---

## Architecture

```
┌──────────────────────────────────────────┐
│  GitHub Copilot (CLI / VS Code / IDE)   │
├──────────────────────────────────────────┤
│  Agents  │  Skills  │  Instructions      │
├──────────────────────────────────────────┤
│  Memory System  │  Learning Tracker      │
│  SQLite+PageIndex│  5-Level Progression  │
├──────────────────────────────────────────┤
│  MCP Servers (filesystem, web, memory,   │
│  thinking, drawio)                       │
└──────────────────────────────────────────┘
```

---

## License

MIT — Use it, fork it, improve it, share it.

---

## Next Steps

1. **Choose your platform:** [CLI](#-github-copilot-cli-4-minutes) or [IDE](#-ide-copilot-vs-codejetbrains-2-minutes)
2. **Follow setup:** See Quick Start above or [ONBOARDING.md](./ONBOARDING.md)
3. **Start using:** Your agents, skills, and memory are ready immediately
4. **Explore:** Ask Copilot "What agents are available?" or "List all skills"

Questions? See [ONBOARDING.md](./ONBOARDING.md) for examples and [CONTRIBUTING.md](./CONTRIBUTING.md) to add skills.
