# Portal Generator — Usage Guide

> Generate branded agent portals with AI assistance. The agent guides you through setup, customization, and Docker/OpenShift deployment.

## 🤖 Using the Agent (Recommended)

### Prerequisites

Before using the portal generator agent, ensure you have:
- ✅ **GitHub Copilot CLI** installed (`winget install GitHub.Copilot`)
- ✅ **Authenticated** to Copilot (`gh auth login`)
- ✅ **Agent framework** installed (see [ONBOARDING.md](../../../ONBOARDING.md))
- ✅ **Python 3.10+** for portal generation script
- ✅ **Your personal agent** initialized with agent systems

### Quick Start - Launch Existing Portal

**If portal is already generated:**

```powershell
# Navigate to scripts directory
cd grit-hub/skills/portal-generation/scripts

# Start the portal server (Python)
python start_portal.py

# OR use PowerShell
.\start_portal.ps1
```

The portal will automatically:
- ✅ Open in your browser at http://localhost:8080
- ✅ Serve from the correct dist/ directory
- ✅ Display the GRIT Hub Agents portal directly

### Generate or Regenerate Portal

**In GitHub Copilot CLI:**

```powershell
# 1. Ensure you're in the grit-hub directory
cd grit-hub

# 2. Boot agent system (loads your personal agent + portal generator skill)
python "$env:USERPROFILE\.copilot\agent_boot.py"

# 3. Invoke the portal generator agent
copilot chat "@portal-generator I want to create a portal for my agents"
```

### What the Agent Does

The agent will **interactively guide you** through:

1. ✅ **Prerequisites check** — Verify Python, folder structure, agent systems
2. ✅ **Configuration gathering** — Ask for project name, repo URL, banner, agent name
3. ✅ **Color customization** — Help choose brand colors (or use DHL defaults)
4. ✅ **Portal generation** — Run the generator script for you
5. ✅ **Local testing** — Start server and open preview at localhost:8080
6. ✅ **Docker setup** — Create Dockerfile and build configuration
7. ✅ **OpenShift deployment** — Configure GitHub Actions workflow
8. ✅ **Troubleshooting** — Help fix any issues

**Example conversation:**

```
You: @portal-generator I want to create a portal

Agent: I'll help you create a branded agent portal! 

Let me check your project structure...
✓ Found 75 agents
✓ Found 35 skills
✓ Your agent name: Alex

What's your project name? (or press Enter to use "GRIT Hub")

You: [Press Enter]

Agent: Great! Using "GRIT Hub"
What's your GitHub repository URL?

You: https://dhl.ghe.com/SMP-Mobile-Customer-Data-Domai/grit-hub

Agent: Perfect! Do you have a banner image ready?

You: Yes, I have assets/banner.png

Agent: Excellent! [Creates configuration and generates portal...]

✓ Portal generated! 
✓ Server started at http://localhost:8080
✓ Browser opened automatically

Your portal features:
  • 75 agents organized by role
  • 35 skills with technical details
  • Search and filter capabilities
  • DHL branded design
  • Last updated: 2026-05-20 15:45 GMT+8

Want to set up automatic deployment to OpenShift?

You: Yes

Agent: [Configures GitHub Actions workflow...]

✓ Deployment workflow created at .github/workflows/deploy-portal.yml
✓ Portal will auto-deploy on every merge to master

Add these secrets in your GitHub repo settings:
  • OPENSHIFT_SERVER
  • OPENSHIFT_USER
  • OPENSHIFT_PASSWORD
  • OPENSHIFT_NAMESPACE (optional)

All set! Your portal is ready locally and will deploy automatically.
```

---

## 🛠️ Manual Setup (Without Agent)

If you prefer to run the portal generator manually without agent assistance:

### 1. Install Prerequisites

```powershell
# Ensure GitHub Copilot CLI is installed
winget install GitHub.Copilot

# Ensure Python 3.10+ is installed
python --version

# Ensure agent framework is installed
ls "$env:USERPROFILE\.copilot"  # Should show: memory/, learning/, skills/, etc.
```

### 2. Generate Portal

```bash
cd skills/portal-generation/scripts
python generate_portal.py
```

### 3. Test Locally

```bash
python dist/serve.py  # Serves at http://localhost:8080
```

### 4. Customize (Optional)

Edit `scripts/portal-config.json`:

```json
{
  "project_name": "Your Project Name",
  "github_repo": "https://github.com/yourorg/yourrepo",
  "banner_image": "assets/your-banner.png",
  "primary_color": "#d40511",
  "secondary_color": "#ffcc00",
  "show_stats": true,
  "show_contributors": true,
  "agent_name": "Your-Personal-Agent-Name"
}
```

**But remember:** The agent provides interactive guidance, validation, and error handling that makes this much easier!

---

## 🎯 What You Get

After portal generation, you'll have:

✅ **Responsive Web Portal**
- DHL-branded design (or your custom branding)
- Search functionality across all agents and skills
- Filter by role (Developer, Manager, Tester, etc.)
- Detailed agent/skill cards with usage examples
- Statistics overview (total agents, skills, roles)
- "Getting Started" modal with setup guide
- Last updated timestamp (GMT+8)

✅ **Data Export**
- `data.json` with all agent/skill metadata (for API use)
- Structured format for integration with other tools

✅ **Deployment Ready**
- Docker configuration for containerization
- OpenShift manifests for Kubernetes deployment
- GitHub Actions workflow for CI/CD
- Automatic rebuild on every merge to master

✅ **Personalization**
- Your agent name embedded in portal metadata
- Custom banner and branding
- Configurable colors and styles
- Role-specific agent groupings

---

---

## 🐳 Docker Build (Local Testing)

```bash
cd skills/portal-generation/scripts
docker build -t grit-hub-portal .
docker run -p 8080:8080 grit-hub-portal
```

Access at: http://localhost:8080

---

## ☸️ OpenShift Deployment

### Auto-Deployment (via GitHub Actions)

**On every merge to master:**

1. Portal regenerates with latest agents/skills
2. Docker image builds
3. Pushes to OpenShift registry
4. Deploys to cluster

**Setup:** Configure GitHub Secrets:
- `OPENSHIFT_SERVER` — API URL
- `OPENSHIFT_TOKEN` — Service account token
- `OPENSHIFT_NAMESPACE` — Project name (optional)

**That's it!** Push to master and portal deploys automatically.

### Manual Deployment

```bash
# Login
oc login --server=https://api.cluster.com:6443 --token=your-token

# Deploy
cd skills/portal-generation/scripts
oc apply -f k8s/ -n your-namespace

# Get URL
oc get route grit-hub-portal -n your-namespace
```

---

## 🌐 For Other Projects

### Using the Agent (Recommended)

**Note:** If your project has onboarded to GRIT Copilot Agent framework, the portal generator is already available. No file copying needed!

**Just invoke:**

```powershell
cd your-project
copilot chat "@portal-generator create a portal for this project"
```

The agent will:
- ✅ Scan your agents/ and skills/
- ✅ Ask for your project details
- ✅ Generate customized portal
- ✅ Setup OpenShift deployment

**That's it!** The agent handles everything.

---

## 📁 File Structure

```
skills/portal-generation/
├── SKILL.md                # Skill documentation
├── README.md               # This file - usage guide
├── QUICK_START.md          # Quick reference
├── .gitignore              # Excludes generated files
└── scripts/                # Technical implementation
    ├── generate_portal.py  # Generator script
    ├── portal-config.json  # Configuration
    ├── requirements.txt    # Python deps
    ├── Dockerfile          # Docker build
    ├── nginx.conf          # Server config
    ├── assets/             # Banner images
    ├── k8s/                # OpenShift manifests
    └── (dist/)             # Generated (not in Git)
```

**Note:** `dist/` is excluded from Git. Generated during Docker build.

---

## 🔧 Configuration

Edit `portal-config.json`:

```json
{
  "project_name": "My Project",
  "github_repo": "https://github.com/org/repo",
  "banner_image": "assets/banner.png",
  "colors": {
    "primary": "#0066CC",
    "secondary": "#FF9900"
  }
}
```

---

## 🆘 Troubleshooting

| Issue | Solution |
|-------|----------|
| Portal not updating | Rebuild: `python generate_portal.py` |
| Docker build fails | Check assets exist, verify requirements.txt |
| OpenShift deploy fails | Check secrets, verify namespace exists |
| Route not accessible | `oc get route`, check pod logs |

---

## 📚 Documentation

- **Agent:** `agents/everyone/portal-generator/portal-generator.agent.md`
- **Skill:** `skills/portal-generation/SKILL.md`
- **Quick Start:** `skills/portal-generation/QUICK_START.md`
- **Workflow:** `.github/workflows/deploy-portal.yml`

---

**Start now:**

```powershell
copilot chat "@portal-generator I want to create a portal"
```

The agent will guide you from there! 🚀
