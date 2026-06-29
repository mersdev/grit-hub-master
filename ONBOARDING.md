# Onboarding Guide

Get up and running with GRIT Hub framework. Choose your platform below.

---

## Choose Your Platform

- **[GitHub Copilot CLI](#github-copilot-cli-setup)** — Command-line interface (4 minutes)
- **[IDE Copilot (VS Code/JetBrains)](#ide-copilot-setup)** — Integrated development environment (2 minutes)

---

# GitHub Copilot CLI Setup

Get your personalized GitHub Copilot agent running in 4 minutes with Learning Path, Memory System, Skills, MCP servers, and custom Personality & Soul.

## Prerequisites

Before starting, ensure you have:
- ✅ **Windows 10/11** — For winget package manager
- ✅ **GitHub account with Copilot access** — Required for Copilot CLI

---

## Step-by-Step Setup

### Step 1: Install GitHub Copilot CLI (30 seconds)

```powershell
# Install GitHub Copilot CLI using Windows Package Manager
winget install GitHub.Copilot
```

**What this installs:**
- ✅ `copilot` command-line tool
- ✅ Integration with Windows Terminal

**Verify installation:**
```powershell
copilot --version
```

---

### Step 2: Run Copilot CLI (30 seconds)

```powershell
# Launch Copilot CLI in interactive mode
copilot
```

This opens the interactive Copilot CLI session.

---

### Step 3: Login Copilot CLI

Within the Copilot CLI interactive session:

```
/login
```

Follow the prompts:
- ✅ Select Github Enterprise (https://dhl.ghe.com/)
- ✅ Browser will open for authentication
- ✅ Sign in with your GitHub account that has Copilot access
- ✅ Authorize the device

**Verify login:** You should see confirmation in the CLI that you're logged in successfully.

---

### Step 4: Setup Your Personal Agent

Now tell Copilot to initialize and wire your personal agent with all the agent systems from the repository.

**In the Copilot CLI interactive session, type:**

```
Init & wire my new Agent <Personal-Agent-Name> and Implement Learning Path, Memory System, Skills System, MCP Integration, Personality & Soul.md into copilot from https://dhl.ghe.com/SMP-Mobile-Customer-Data-Domai/grit-hub
```

**Example:**
```
Init & wire my new Agent Alex and Implement Learning Path, Memory System, Skills System, MCP Integration, Personality & Soul.md into copilot from https://dhl.ghe.com/SMP-Mobile-Customer-Data-Domai/grit-hub
```

**What Copilot will do:**
1. ✅ Clone the agent repository
2. ✅ Install core systems (Learning Path, Memory, Skills, MCP)
3. ✅ Configure your personal agent with your chosen name
4. ✅ Set up Personality & Soul from the repository
5. ✅ Wire all systems together
6. ✅ Make your agent ready to use

**The process takes about 2 minutes.** Copilot will guide you through any additional configuration needed.

**What gets installed:**

**Core Systems (~/.copilot/):**
- ✅ **Learning Path** — 5-level skill progression tracker
- ✅ **Memory System** — SQLite + PageIndex + FTS5 full-text search
- ✅ **Skills Library** — 52 reusable capabilities
- ✅ **MCP Servers** — 5 Model Context Protocol integrations
- ✅ **PPTX Agent** — DHL-branded presentation generation

**Agents & Persona:**
- ✅ **57 Specialized Agents** — Developer, Team Manager, Quality Assurance, Architect, AI Engineer, Everyone
- ✅ **Personality & Soul** — Customizable agent behaviors and tone
- ✅ **Security Guardrails** — PII protection, secret scanning, compliance

---

## ✅ Verify CLI Setup

After completing the 4 steps above, verify everything is working:

### Check Your Agent is Ready

Within the Copilot CLI interactive session, ask:

```
What is my agent name and what systems do I have access to?
```

Your agent should respond with:
- ✅ Your personal agent name (e.g., "Alex")
- ✅ List of systems: Learning Path, Memory System, Skills, MCP, Personality & Soul
- ✅ Available agents (e.g., Developer, Team Manager, Quality Assurance, Architect, AI Engineer, etc.)
- ✅ Available skills (e.g., memory-recall, code-review, pptx-agent, drawio, portal-generation, etc.)

### Test Agent Systems

Within the Copilot CLI interactive session:

```
# Test Memory System
Remember that our API base URL is https://api.internal.dhl.com

# Test Learning Tracker
What's my current skill level in Python?

# Test Skills
List all available skills

# Test Agents
Show me all available agents organized by role
```

---

## 🚀 Using Your CLI Agent

### Daily Workflow

**Start Copilot CLI and initialize with your agent:**
```powershell
# Launch Copilot CLI
copilot

# Initialize with your personal agent
init agent Alex
```

You're now in the interactive Copilot session with your personal agent loaded!

### Example Interactions

Within the Copilot CLI interactive session:

```
# Ask your agent about itself
What agents and skills are available?

# Use memory system
Remember that our API base URL is https://api.internal.dhl.com
What do you remember about our API?

# Track learning progress
I just learned how to implement OAuth2. Update my learning tracker.
What should I learn next based on my progress?

# Use your agent for different roles
Review my authentication code
Design test cases for the login flow
Generate a sprint status deck

# Generate presentations
Create a 10-slide presentation about our Q2 roadmap

# Create diagrams
Draw a system architecture diagram for our microservices
```

### Daily Workflow Pattern

**Morning:**
```
copilot
init agent Alex
What did I work on yesterday? What's on my plate today?
```

**During Work:**
```
# Your agent has context across all sessions via memory system
Using my past decisions about authentication, recommend an approach for this new service
```

**End of Day:**
```
Save today's key decisions and learnings to memory
```

---

## 📚 What Your CLI Agent Can Do

✅ **Specialized Sub-Agents**
- Developer, Team Manager, Quality Assurance, Architect, Project Manager, Consultant, Support, AI Engineer, Agent Builder, Everyone, and more

✅ **Skills**
- Memory recall & save, Learning tracker, Code review, Deep research, PPTX presentations, draw.io diagrams, portal generation, and more

✅ **Persistent Memory System**
- Save facts, events, workflows across sessions
- Hierarchical search with PageIndex
- Full-text search with FTS5

✅ **Learning Tracker**
- Track your skill progression (5 levels: Novice → Master)
- Get personalized recommendations based on your role
- Curriculum-driven learning paths

✅ **MCP Servers**
- Filesystem access, Web fetch, Memory system, Sequential thinking, draw.io integration, and more

✅ **Your Custom Personality & Soul**
- Unique agent name and persona
- Role-specific behaviors and tone
- Adaptive responses based on your preferences

---

## ❓ CLI Troubleshooting

| Issue | Fix |
|-------|-----|
| **"winget not found"** | Update Windows: Settings → Windows Update. Or install from [Microsoft Store](https://aka.ms/getwinget) |
| **"GitHub.Copilot not found"** | Try: `winget install --id GitHub.Copilot` or install from [GitHub Copilot CLI releases](https://github.com/github/gh-copilot/releases) |
| **"/login command not working"** | Ensure you have GitHub Copilot subscription on your account. Try typing `/help` in Copilot CLI |
| **"Agent initialization fails"** | Check internet connection. Copilot needs to clone the repository from https://dhl.ghe.com/ |
| **"Cannot access repository"** | Ensure you have access to DHL Git Enterprise. Check with your team admin |
| **"Copilot doesn't remember my name"** | Re-run Step 4 with the initialization command |
| **"Skills not working"** | Ask copilot: "What skills do I have?" and verify the response lists 52+ skills |

---

# IDE Copilot Setup

Get GRIT Hub framework running in VS Code, JetBrains, or other IDEs in 2 minutes.

## Prerequisites

Before starting, ensure you have:
- ✅ **Git** — To clone the repository
- ✅ **Node.js 16+** — For setup scripts
- ✅ **npm** — Node package manager (comes with Node.js)
- ✅ **Python 3.10+** — For memory and learning systems
- ✅ **GitHub Copilot extension** — Installed and signed in in your IDE
- ✅ **Git Personal Access Token (PAT)** — For authentication to DHL Git

---

## Step-by-Step Setup

### Step 0: Setup Git Credentials (1 minute — First Time Only)

If this is your first time using DHL Git on this machine:

**Double-click `setup-login.bat`** in the repository root (or run `bash setup-login.sh` on Linux/Mac).

**You only need to do this once per machine.** Skip to Step 1 if you already have Git PAT configured.

---

### Step 1: Clone Repository (30 seconds)

```powershell
git clone https://dhl.ghe.com/SMP-Mobile-Customer-Data-Domai/grit-hub.git
cd grit-hub
```

---

### Step 2: Run npm install (1 minute)

```powershell
npm install
```

**This automatically runs `node setup.js --all` as a postinstall hook and installs everything:**

**Global Installation (~/.copilot/):**
- ✅ Memory system (SQLite + PageIndex)
- ✅ Learning tracker (skill progression)
- ✅ Skills library (code-review, deep-research, etc.)
- ✅ MCP servers config
- ✅ PPTX agent
- ✅ Boot script (for CLI compatibility)

**Project Installation (.github/):**
- ✅ Specialized agents (Developer, Team Manager, Quality Assurance, Architect, Consultant, Support, AI Engineer, Project Manager, Agent Builder, Everyone, and more)
- ✅ Skills (memory-recall, code-review, pptx-agent, drawio, portal-generation, and more)
- ✅ Security guardrails
- ✅ Instructions and AGENTS.md

**Note:** If you prefer manual setup instead of npm install, you can run `node setup.js --all` directly at any time.

---

### Step 3: Reload IDE and Use Agents (30 seconds)

**VS Code:**
- Press `Ctrl+Shift+P` (Windows/Linux) or `Cmd+Shift+P` (Mac)
- Search for "Developer: Reload Window" and press Enter
- Wait for IDE to reload (5-10 seconds)
- Open Copilot Chat (Ctrl+I or Cmd+I)
- Ask: "What agents are available?"

**JetBrains IDEs:**
- File → Invalidate Caches / Restart → Invalidate and Restart
- Wait for IDE to restart
- Open Copilot tool window
- Ask: "What agents are available?"

---

## ✅ Verify IDE Setup

After completing the 3 steps above, verify everything is working:

### Check Global Installation
```powershell
ls "$env:USERPROFILE\.copilot" | Select-Object Name
```

Should show: `agent_boot.py`, `copilot-instructions.md`, `learning`, `memory`, `mcp.json`, `pptx`, `skills`

### Check Project Installation
```powershell
ls ".github" | Select-Object Name
```

Should show: `agents`, `instructions`, `security`, `skills`

✅ If both above commands show files/folders → **IDE Setup is complete!**

---

## 🚀 Using IDE Agents

### In VS Code / IDE Copilot Chat

Simply ask in Copilot Chat:
```
What agents are available?
```

Or use specific agent capabilities:
```
Review my authentication code
Design a microservices architecture
Create a status report
```

### Example Interactions

```
# General questions
Which agent capabilities can help me review code?

# Use your agent for different tasks
Explain this function
Design a microservices architecture
Create a status report

# Memory system (shared with CLI)
Remember that our API uses JWT authentication
What do you remember about our API?

# Learning tracking
I just learned React Hooks. Update my progress.
What should I learn next?
```

---

## 📚 What You Get (Both Platforms)

✅ **57 Specialized Role-Based Agents**
- Developer, Team Manager, Quality Assurance, Architect, Project Manager, Consultant, Support, AI Engineer, Agent Builder, Everyone

✅ **52 Shared Skills**
- Memory recall & save, Learning tracker, Code review, Deep research, PPTX presentations, draw.io diagrams

✅ **Persistent Memory System**
- Save facts, events, workflows across sessions
- Hierarchical search with PageIndex
- Works across both CLI and IDE

✅ **Learning Tracker**
- Track your skill progression
- Get personalized recommendations
- Synced between CLI and IDE

✅ **MCP Servers**
- Filesystem access, Web fetch, Memory system, Sequential thinking, draw.io integration, and more

---

## ❓ IDE Troubleshooting

| Issue | Fix |
|-------|-----|
| **"Node.js not found"** | Install from [nodejs.org](https://nodejs.org) |
| **"Python not found"** | Install from [python.org](https://python.org) — ensure version 3.10+ |
| **"Agents not visible in IDE"** | Reload IDE: `Ctrl+Shift+P` → "Developer: Reload Window" |
| **"Memory commands fail"** | Verify Python installed: `python --version` |
| **"setup.js fails"** | Run with: `node setup.js --all --skip-python` to skip Python deps |
| **"Copilot Chat not responding"** | Ensure Copilot extension is signed in (check status in IDE) |
| **".github/ folder not created?"** | This is NORMAL! `.github/` is created by setup.js --all for IDE discovery |

---

## 📖 Next Steps

1. **Customize your agent:** Edit `~/.copilot/copilot-instructions.md` to refine your agent's personality
2. **Explore skills:** Ask in Copilot CLI: `List all available skills and what they do`
3. **Learn the systems:**
   - Memory: See `memory/README.md` for advanced memory operations
   - Learning: See `learning/README.md` for skill progression tracking
   - MCP: See `mcp/README.md` for Model Context Protocol integration
4. **Browse agents:** Ask: `Show me all available agents organized by role` or check `instructions/AGENTS.md`
5. **Generate portal:** Try the portal generator: `@portal-generator create a portal for my agents`
6. **Contribute:** See [CONTRIBUTING.md](./CONTRIBUTING.md) to add your own skills or agents

---

## 🎯 Quick Verification Checklist

### CLI Setup Checklist

- [ ] `winget install GitHub.Copilot` completed successfully
- [ ] Launched Copilot CLI with `copilot` command
- [ ] Logged in using `/login` within Copilot CLI
- [ ] Initialized agent with Step 4 command
- [ ] Copilot responds with your personal agent name when asked
- [ ] Memory system works: Ask "Remember that my favorite color is blue"
- [ ] Learning tracker works: Ask "What's my current skill level in Python?"
- [ ] Skills work: Ask "List all available skills"

### IDE Setup Checklist

- [ ] `npm install` completed without errors
- [ ] `~/.copilot/` directory exists with: `memory/`, `learning/`, `skills/`, `pptx/`, `copilot-instructions.md`
- [ ] `.github/` directory exists with: `agents/`, `skills/`, `security/`, `instructions/`
- [ ] IDE reloaded successfully
- [ ] Copilot Chat responds to agent questions
- [ ] Memory system works: Ask "Remember that X" in Copilot Chat

---

**Ready?** Choose your platform above and you'll be up and running in minutes! 🚀
