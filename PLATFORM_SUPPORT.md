---
name: "Platform Support Matrix"
description: "Explicit support documentation for GitHub Copilot CLI and VS Code IDE with setup differences"
version: "1.0.0"
---

# Platform Support Matrix

This document clarifies exactly how grit-hub works in different Copilot environments.

---

## 📊 Feature Support Matrix

| Feature | GitHub CLI | VS Code | JetBrains IDE |
|---------|-----------|--------|---------------|
| **Memory system** | ✅ Full | ✅ Full | ✅ Full |
| **Learning tracker** | ✅ Full | ✅ Full | ✅ Full |
| **Skills** | ✅ Auto-triggered | ✅ Auto-triggered | ✅ Auto-triggered |
| **MCP servers** | ✅ Yes | ✅ Yes | ⏳ Partial |
| **Boot script** | ✅ Auto-run | ⏳ Manual | ⏳ Manual |
| **Agent personas** | ✅ Yes | ✅ Yes | ✅ Yes |
| **PPTX Agent** | ✅ Yes | ✅ Yes | ✅ Yes |
| **draw.io** | ✅ Yes | ✅ Yes | ✅ Yes |

---

## 🖥️ GitHub Copilot CLI

**Best for:** Command-line workflows, scripting, automation

### Setup
Follow the GitHub CLI setup flow in [ONBOARDING.md](./ONBOARDING.md#github-copilot-cli-setup).

### How It Works
1. **Global setup** installs to `~/.copilot/` (one-time)
2. **Session startup** runs boot script:
   ```powershell
   python "$env:USERPROFILE\.copilot\agent_boot.py"
   ```
3. **Boot script outputs:**
   - Memory summary (5 high-importance memories)
   - Learning status (active skills)
   - Loaded skills
   - MCP servers available

### Usage
For daily CLI commands and examples, see [ONBOARDING.md](./ONBOARDING.md#-using-your-cli-agent).

### Key Differences from IDE
- ✅ Boot script runs automatically at session start
- ✅ Full terminal access for Python scripts
- ✅ All MCP servers available
- ⏳ Manual memory/learning commands (not IDE integration)

---

## 💻 VS Code Copilot

**Best for:** IDE-based development, visual workflows, code editing

### Setup
Follow the IDE setup flow in [ONBOARDING.md](./ONBOARDING.md#ide-copilot-setup).

### How It Works
1. **Global setup** installs to `~/.copilot/` (one-time)
2. **Copilot detects** global `copilot-instructions.md` and `AGENTS.md`
3. **Skills are available** but boot script doesn't auto-run
4. **Memory/Learning** available via command calls (not auto-loaded)

### Usage
For day-to-day IDE usage examples, see [ONBOARDING.md](./ONBOARDING.md#-using-ide-agents).

### Key Differences from CLI
- ⏳ Boot script must run manually (not automatic)
- ✅ Visual editor integration
- ✅ Skills auto-triggered by Copilot
- ✅ Full MCP server access
- ⏳ Memory/Learning accessed via terminal commands

---

## 🧠 Memory Access by Platform

### GitHub CLI
```powershell
# Recall memories
python ~/.copilot/memory/pageindex_recall.py --query "topic"
python ~/.copilot/memory/memory_manager.py recall --query "topic" --engine fts

# Save memories
python ~/.copilot/memory/memory_manager.py save --type semantic --content "..." --tags "..."

# View stats
python ~/.copilot/memory/memory_manager.py stats
```

### VS Code Copilot
```powershell
# Same commands as CLI, but run from VS Code terminal or external terminal

# In Copilot Chat, you can ask:
"What do I know about [topic]?" → Copilot suggests memory recall command
"Remember that [fact]" → Copilot can guide you to memory save command
```

---

## 🛠️ MCP Server Differences

| MCP Server | CLI | VS Code | Status |
|-----------|-----|---------|--------|
| filesystem | ✅ | ✅ | Full read/write access |
| memory | ✅ | ✅ | Access to memory system |
| fetch | ✅ | ✅ | Web content retrieval |
| sequential-thinking | ✅ | ✅ | Multi-step reasoning |
| drawio-mcp | ✅ | ⏳ | Live editor (IDE-dependent) |

---

## 📂 Agent Structure & Discovery

### Agent Organization

Agents are organized by role in the repository:

```
agents/
├── architect/system-designer/
│   └── system-designer.agent.md
├── developer/fullstack-engineer/
│   └── fullstack-engineer.agent.md
├── team-manager/team-coordinator/
│   └── team-coordinator.agent.md
├── quality-assurance/qa-strategist/
│   └── qa-strategist.agent.md
├── project-manager/planning-agent/
│   └── planning-agent.agent.md
├── consultant/advisory-agent/
│   └── advisory-agent.agent.md
├── support/troubleshooter/
│   └── troubleshooter.agent.md
├── ai-engineer/model-evaluator-specialist/
│   └── model-evaluator-specialist.agent.md
├── ai-engineer/development-coach/
│   └── development-coach.agent.md
└── everyone/
    ├── daily-assistant/
    │   └── daily-assistant.agent.md
    └── wfh-leave-submission/
        └── wfh-leave-submission.agent.md
```

### How Agents Are Discovered

**GitHub CLI:**
1. ✅ Agents documented in `instructions/AGENTS.md`
2. ✅ Boot script loads AGENTS.md context
3. ✅ Copilot CLI references agents by path
4. ✅ User specifies which agent to use

**VS Code / JetBrains IDE:**
1. ✅ Agents documented in `instructions/AGENTS.md`
2. ✅ Global instructions loaded from `~/.copilot/copilot-instructions.md`
3. ✅ Copilot references agents from AGENTS.md
4. ✅ User can ask Copilot "Which agent should I use?"

### Using Agents

#### GitHub CLI
```powershell
# Launch Copilot CLI
copilot

# Initialize with your agent
init agent Alex

# Ask for help
What can you help me with for React components?

# Use agent capabilities directly
Write a React component for a login form
```

#### VS Code / IDE
```
In Copilot Chat:
1. Ask: "Which agent is best for [task]?"
2. Copilot references AGENTS.md and suggests an agent
3. The agent's README.md provides examples
4. Use the agent: "[Agent name], help me with [task]"
```

### Customizing Agents

To customize an agent for your team:

1. **Navigate to agent folder:** `agents/<role>/<agent-name>/`
2. **Edit the agent definition:** `agents/<role>/<agent-name>/<agent-name>.agent.md`
   - Customize persona for your team
   - Adjust skills to what you use most
   - Add team-specific guardrails
3. **Reload your IDE** or restart Copilot CLI session
4. **Test the agent** with example prompts

Changes take effect immediately — no setup script re-run needed.

---



## 🔧 Troubleshooting by Platform

### "Skills aren't showing up"

**GitHub CLI:**
1. Verify boot script ran: `python "$env:USERPROFILE\.copilot\agent_boot.py"`
2. Check skills are installed: `ls ~/.copilot/skills/`
3. Verify AGENTS.md exists: `cat ~/AGENTS.md | head -20`

**VS Code:**
1. Reload VS Code: `Ctrl+Shift+P` → "Developer: Reload Window"
2. Check Copilot is signed in (bottom right corner)
3. Verify global config: `cat ~/.copilot/copilot-instructions.md | head -20`

### "Memory commands don't work"

**Both platforms:**
1. Verify Python 3.10+: `python --version`
2. Verify scripts exist: `ls ~/.copilot/memory/`
3. Test directly: `python ~/.copilot/memory/memory_manager.py stats`
4. Check database: `ls ~/.copilot/memory/memory.db`

### "Boot script errors"

**GitHub CLI only:**
1. Verify script exists: `cat ~/.copilot/agent_boot.py | head -10`
2. Check Python dependencies: `pip list | grep -i pptx`
3. Try running manually: `python ~/.copilot/agent_boot.py`

---

## ✅ First-Time Setup Checklist

### For GitHub CLI Users
- [ ] Completed the GitHub CLI setup and verification checklist in [ONBOARDING.md](./ONBOARDING.md#-quick-verification-checklist)

### For VS Code Users
- [ ] Completed the IDE setup and verification checklist in [ONBOARDING.md](./ONBOARDING.md#-quick-verification-checklist)

---

## 📞 Getting Help

**If something isn't working:**

1. **Check this matrix first** — verify your platform supports the feature
2. **Run troubleshooting steps** above for your platform
3. **Check logs:**
   - CLI: Output from boot script
   - VS Code: Output panel in IDE
4. **Open an issue** with:
   - Platform (CLI / VS Code / other IDE)
   - Error message or unexpected behavior
   - Steps to reproduce
   - Your setup output (`node setup.js --dry-run`)

---

## 🔄 Platform Migration

### Moving from GitHub CLI to VS Code
1. Both use the same `~/.copilot/` directory
2. Your memories and learning are shared
3. Just reload VS Code and you're ready
4. Boot script is optional (but you can still run it manually)

### Moving from VS Code to GitHub CLI
1. Same setup.js on target machine
2. Your memories and learning transfer (if you copy `~/.copilot/memory/`)
3. Boot script will now auto-run at session start
4. No other changes needed

---

## 🎯 Recommendations

**Use GitHub CLI if you:**
- Work primarily in the terminal
- Want automatic context loading at session start
- Prefer command-line workflows

**Use VS Code if you:**
- Work primarily in the IDE
- Want visual integration with Copilot Chat
- Prefer graphical environments

**Use both if you:**
- Have different workflows for different tasks
- Work across CLI and IDE-based projects
- Want maximum flexibility

Both setups share the same memory and learning systems, so switching is seamless.
