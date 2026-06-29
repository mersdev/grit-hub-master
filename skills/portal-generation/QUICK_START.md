# Portal Generator — Quick Reference

## 🚀 **For New Users: Use the Agent!**

### Prerequisites

```powershell
# 1. Install GitHub Copilot CLI
winget install GitHub.Copilot

# 2. Login to Copilot
gh auth login

# 3. Install agent framework
git clone https://dhl.ghe.com/SMP-Mobile-Customer-Data-Domai/grit-hub.git
cd grit-hub
npm install

# 4. Initialize your personal agent
copilot chat "Initialize my agent as <Your-Personal-Agent-Name>"
```

### Quick Launch (Portal Already Generated)

**Start the portal server:**
```powershell
# Navigate to scripts directory
cd grit-hub/skills/portal-generation/scripts

# Start portal (Python)
python start_portal.py

# OR use PowerShell
.\start_portal.ps1
```

Portal opens automatically at **http://localhost:8080** ✅

### Generate New Portal

**GitHub Copilot CLI:**
```powershell
# Load agent systems
python "$env:USERPROFILE\.copilot\agent_boot.py"

# Invoke portal generator
copilot chat "@portal-generator I want to create a portal"
```

---

## 🤖 What the Agent Does For You

The agent provides **interactive guidance**:

✅ **Checks prerequisites** — Python, folder structure, agent systems  
✅ **Gathers configuration** — Asks for project details, your agent name  
✅ **Customizes branding** — Colors, banner, fonts  
✅ **Generates portal** — Runs script for you (75 agents, 35 skills)  
✅ **Tests locally** — Starts server, opens browser at localhost:8080  
✅ **Sets up deployment** — Creates OpenShift workflow  
✅ **Troubleshoots issues** — Helps fix problems  
✅ **Personalizes portal** — Embeds your personal agent name

---

## 💬 Example Conversations

### First-Time Setup

```
You: @portal-generator create a portal

Agent: I'll help! Let me check your project and agent configuration...
✓ Found 75 agents, 35 skills
✓ Your agent name: Alex

What's your project name? (or press Enter for "GRIT Hub")

You: [Press Enter]

Agent: Great! Using "GRIT Hub"
What's your GitHub repo?

You: https://dhl.ghe.com/SMP-Mobile-Customer-Data-Domai/grit-hub

Agent: Perfect! Got a banner image?

You: Yes, assets/GRIT Hub.png

Agent: Want custom colors or use DHL defaults?

You: Use DHL defaults

Agent: [Generates portal with your agent name...]

✓ Portal created! 
✓ 75 agents organized by role
✓ 35 skills with details
✓ Personalized with agent: Alex
✓ Test at http://localhost:8080

Want to set up auto-deployment to OpenShift?
```

### Update Banner

```
You: @portal-generator update banner with new-banner.png

Agent: ✓ Banner updated
✓ Portal regenerated with your agent: Alex
Test at http://localhost:8080
```

### Change Colors

```
You: @portal-generator change colors to green and purple

Agent: What hex codes?

You: #00C853 and #9C27B0

Agent: ✓ Colors updated
✓ Portal regenerated
```

### Setup Deployment

```
You: @portal-generator set up auto-deployment

Agent: Creating OpenShift deployment workflow...
✓ GitHub Actions workflow created

Next steps:
1. Add secrets in GitHub repo settings:
   • OPENSHIFT_SERVER
   • OPENSHIFT_USER
   • OPENSHIFT_PASSWORD
   • OPENSHIFT_NAMESPACE
2. Merge to master
3. Portal auto-deploys!
```

---

## 🎯 **Purpose of Agent & Skill Files**

### Why Use the Agent?

**Without Agent** (manual):
- ❌ Edit JSON config manually
- ❌ Remember file paths and formats
- ❌ Run commands yourself
- ❌ Debug errors alone
- ❌ Figure out deployment yourself
- ❌ No personalization with your agent name

**With Agent** (interactive):
- ✅ Answer simple questions
- ✅ Agent creates config for you
- ✅ Agent runs commands
- ✅ Agent explains errors
- ✅ Agent sets up deployment
- ✅ Automatically embeds your agent name

### What Each File Does

| File | Purpose |
|------|---------|
| **portal-generator.agent.md** | Agent persona - knows HOW to help users build portals |
| **skills/portal-generation/SKILL.md** | Technical capability - portal generation knowledge |
| **scripts/generate_portal.py** | Script - does the actual work |
| **scripts/portal-config.json** | Config - what gets customized |

**Think of it as:**
- **Agent** = Your assistant who guides you
- **Skill** = The knowledge the agent has
- **Script** = The tool the agent uses for you
- **Config** = Settings the agent helps you create

---

## 📋 For Other Projects

### How Other Projects Can Use This

1. **Install GitHub Copilot CLI:**
   ```powershell
   winget install GitHub.Copilot
   gh auth login
   ```

2. **Clone and integrate agent systems:**
   ```bash
   git clone https://dhl.ghe.com/SMP-Mobile-Customer-Data-Domai/grit-hub.git
   cd grit-hub
   npm install
   ```

3. **Initialize with your project's agent name:**
   ```powershell
   copilot chat "Initialize my agent as <Your-Project-Agent-Name>"
   ```

4. **Copy to your project:**
   ```bash
   cp -r agents/everyone/portal-generator your-project/agents/everyone/
   cp -r skills/portal-generation your-project/skills/
   ```

5. **Generate portal for your project:**
   ```powershell
   cd your-project
   copilot chat "@portal-generator create a portal for this project"
   ```

**The agent will:**
1. Scan YOUR agents/ and skills/
2. Ask for YOUR project details
3. Use YOUR agent name
4. Generate YOUR portal
5. Help deploy YOUR portal

---

## 🔧 Manual Mode (If You Don't Want Agent Help)

```bash
cd skills/portal-generation/scripts
nano portal-config.json  # Edit manually (add your agent name!)
python generate_portal.py
cd dist
python serve.py
```

But why do manual work when the agent can help? 😊

---

## ✨ Key Benefits of Using the Agent

1. **No JSON editing** — Agent creates config for you
2. **Interactive** — Answer questions, not read docs
3. **Error handling** — Agent explains and fixes issues
4. **Deployment help** — Agent sets up automation
5. **Personalization** — Automatically uses your agent name
6. **Faster** — 2 minutes vs 30 minutes manual setup
7. **Friendly** — Natural language, not commands
8. **Memory integration** — Saves portal events to your agent memory

---

## 🆘 Quick Commands

| Task | Command |
|------|---------|
| Create portal | `@portal-generator create a portal` |
| Update banner | `@portal-generator update banner` |
| Change colors | `@portal-generator change colors` |
| Test locally | `@portal-generator test locally` |
| Setup deployment | `@portal-generator setup deployment` |
| Troubleshoot | `@portal-generator portal not working` |
| Check config | `@portal-generator show current configuration` |

---

## 📚 Full Documentation

- **Onboarding**: [ONBOARDING.md](../../../ONBOARDING.md) — Install Copilot CLI + agent framework
- **Agent**: [portal-generator.agent.md](../../../agents/everyone/portal-generator/portal-generator.agent.md)
- **Skill**: [SKILL.md](./SKILL.md)
- **Usage**: [README.md](./README.md)

---

**Start now:**

```powershell
# Step 1: Install Copilot CLI
winget install GitHub.Copilot

# Step 2: Login
gh auth login

# Step 3: Setup agent framework
git clone https://dhl.ghe.com/SMP-Mobile-Customer-Data-Domai/grit-hub.git
cd grit-hub
npm install
copilot chat "Initialize my agent as <Your-Name>"

# Step 4: Generate portal
python "$env:USERPROFILE\.copilot\agent_boot.py"
copilot chat "@portal-generator I want to create a portal"
```

The agent will guide you from there! 🚀
