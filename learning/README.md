# Learning System

A structured learning progress tracker that maps skill development across multiple learning paths, using 5 proficiency levels and a curriculum-based approach.

## Overview

The learning system enables deliberate skill development by:

1. **Tracking proficiency levels** across topics (novice → expert)
2. **Organizing learning paths** that group related topics
3. **Suggesting next steps** based on prerequisites and current progress
4. **Maintaining learning history** for reflection and review

## Proficiency Levels

Skills are tracked across a 5-level scale:

```
novice       → beginner       → intermediate → advanced      → expert
[BLANK]        [1 block]         [2 blocks]      [3 blocks]    [4 blocks]
```

| Level | Description | Time | Examples |
|-------|-------------|------|----------|
| **novice** | Aware of the topic but no practical experience | 0h | "I've heard of Docker" |
| **beginner** | Completed basics, simple tasks independently | 10–20h | "I can write basic SQL queries" |
| **intermediate** | Comfortable with common patterns, debug issues | 50–100h | "I build production Python apps" |
| **advanced** | Expert-level for most scenarios, teaching others | 200+ h | "I optimize Python performance" |
| **expert** | Mastery; leading design decisions in your field | 500+ h | "I architect Python systems" |

## Learning Paths

Pre-configured learning paths group related topics in logical progression:

### 1. Software Engineering Fundamentals
Core concepts every developer should master:
- Data Structures
- Algorithms
- Design Patterns
- Testing
- Version Control
- CI/CD
- System Design
- Security Basics

### 2. AI & Machine Learning
From fundamentals to modern LLM applications:
- Statistics & Probability
- Linear Algebra
- Python for ML
- Classical ML
- Deep Learning
- NLP
- LLMs & Prompt Engineering
- AI Agents
- Fine-tuning
- MLOps

### 3. Cloud & DevOps
Modern infrastructure and operations:
- Linux Fundamentals
- Networking
- Docker
- Kubernetes
- Terraform
- AWS/Azure/GCP
- Monitoring
- GitOps

## Storage Architecture

```
learning/
├── learning.db              # SQLite database (3 tables)
├── learning_manager.py      # Main CLI tool
└── README.md               # This file
```

### Database Schema

**`learning_paths` table:**
```sql
CREATE TABLE learning_paths (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    name        TEXT NOT NULL UNIQUE,
    description TEXT DEFAULT '',
    topics      TEXT DEFAULT '[]',  -- JSON array
    created_at  TEXT NOT NULL
);
```

**`topic_progress` table:**
```sql
CREATE TABLE topic_progress (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    topic       TEXT NOT NULL,
    level       TEXT NOT NULL,
    notes       TEXT DEFAULT '',
    path_id     INTEGER REFERENCES learning_paths(id),
    recorded_at TEXT NOT NULL
);
```

**`skill_levels` table (current snapshot):**
```sql
CREATE TABLE skill_levels (
    topic       TEXT PRIMARY KEY,
    level       TEXT NOT NULL,
    updated_at  TEXT NOT NULL,
    session_count INTEGER DEFAULT 1  -- how many sessions contributed
);
```

## Usage

### View Current Status

```bash
python learning_manager.py status
```

Output shows skills organized by level:
```
── Current Skill Levels ────────────────────────────────
  EXPERT       ████████  Machine Learning, Python
  ADVANCED     ███████   Docker, Testing
  INTERMEDIATE ██████    Kubernetes, Design Patterns
  BEGINNER     █████     Terraform
  NOVICE       ████      MLOps

  Total topics tracked: 14
```

### Record Progress

When you've learned or improved a skill:

```bash
python learning_manager.py progress \
  --topic "Python" \
  --level intermediate \
  --notes "Built async web scraper with asyncio and aiohttp"
```

**Arguments:**
- `--topic` (required): Name of the topic
- `--level` (required): One of: `novice`, `beginner`, `intermediate`, `advanced`, `expert`
- `--notes` (optional): What you learned or achieved
- `--path-id` (optional): Associate with a specific learning path (see `list-paths`)

The system automatically creates a skill record if it doesn't exist, or updates the existing one.

### List Learning Paths

```bash
python learning_manager.py list-paths
```

Output:
```
── Learning Paths ─────────────────────────────────────

  [1] Software Engineering Fundamentals
       Core software engineering concepts every developer should know
       Topics (8): Data Structures, Algorithms, Design Patterns, Testing, Version Control, CI/CD, System Design, Security Basics

  [2] AI & Machine Learning
       From ML fundamentals to modern LLM applications
       Topics (10): Statistics & Probability, Linear Algebra, Python for ML, Classical ML, Deep Learning, NLP, LLMs & Prompt Engineering, AI Agents, Fine-tuning, MLOps

  [3] Cloud & DevOps
       Modern cloud infrastructure and DevOps practices
       Topics (8): Linux Fundamentals, Networking, Docker, Kubernetes, Terraform, AWS/Azure/GCP, Monitoring, GitOps
```

### Get Suggestions

```bash
python learning_manager.py suggest
```

Uses prerequisites to suggest next topics:
```
── Suggested Next Steps ────────────────────────────────
  START  [AI & Machine Learning] → Statistics & Probability (novice → beginner)
  LEVEL UP  [Software Engineering Fundamentals] → Algorithms: intermediate → advanced
  LEVEL UP  [Cloud & DevOps] → Docker: beginner → intermediate
  START  [Software Engineering Fundamentals] → System Design (novice → beginner)
```

**Logic:**
- Suggest starting a topic if previous topic reached `advanced` or `expert`
- Suggest leveling up if below `advanced` level
- Respect learning path order (don't start topic 3 if topic 1 isn't complete)

### View Learning History

```bash
python learning_manager.py history --limit 10
```

Filter by topic:
```bash
python learning_manager.py history --topic "Python" --limit 20
```

Output:
```
── Learning History (last 10) ──────────────────────
  2026-05-15  Python                   → intermediate   Built async web scraper with asyncio
  2026-05-10  Machine Learning         → advanced       Completed Stanford CS229 course
  2026-05-08  Docker                   → intermediate   Deployed multi-container app with Compose
  2026-05-05  Kubernetes               → beginner       Deployed first pod to minikube
  2026-05-01  Design Patterns          → intermediate   Refactored app with strategy pattern
```

### Create Custom Learning Path

```bash
python learning_manager.py add-path \
  --name "Full-Stack Web Development" \
  --description "Frontend, backend, database, deployment" \
  --topics "HTML & CSS,JavaScript,React,Node.js,PostgreSQL,DevOps,Testing"
```

## Curriculum System

### Understanding Prerequisites

Topics have implicit prerequisites within each path:
- Path topics are ordered from foundational → advanced
- Can't efficiently progress beyond topic 2 if topic 1 is at `novice`

Example: Before learning `Kubernetes` (Cloud & DevOps path), it's assumed you've reached at least `beginner` in `Docker`.

### Progression Model

Skill progression is **non-linear** and **experience-driven**:

1. **Jump in:** Try building a project → hit wall
2. **Return to fundamentals:** Study basics → practice
3. **Iterate:** Build → learn → build
4. **Deepen:** Teach others, optimize, lead architecture

Use `progress` to record these transitions:

```bash
# Hit a wall trying Kubernetes
python learning_manager.py progress --topic "Kubernetes" --level beginner --notes "Deployed pod but struggling with networking"

# Back to Docker to deepen
python learning_manager.py progress --topic "Docker" --level intermediate --notes "Deep dive into networking and compose"

# Return to Kubernetes, now confident
python learning_manager.py progress --topic "Kubernetes" --level intermediate --notes "Networking model makes sense now, deployed stateful app"
```

### Suggested Session Workflow

1. **Start of session:** Run `status` to remind yourself of current skills
2. **During session:** Try learning something new, deepen a skill
3. **End of session:** Run `progress` to log what you learned
4. **Next session:** Run `suggest` to see what to tackle next

```bash
# Morning
python learning_manager.py status

# Work on Docker Compose project...

# End of day
python learning_manager.py progress \
  --topic "Docker" \
  --level intermediate \
  --notes "Built multi-service app with volumes and networking"

# Next day
python learning_manager.py suggest
```

## Integration with Memory System

Link learning progress with your persistent memory:

```bash
# Learn something and save it to memory
python memory_manager.py save \
  --type procedural \
  --content "Multi-container Docker setup with volumes and networking for production apps" \
  --tags "docker,workflow" \
  --importance 8

# Then record progress
python learning_manager.py progress \
  --topic "Docker" \
  --level intermediate \
  --notes "Built multi-service app; saved workflow to memory"
```

## Statistics & Insights

### Topic Coverage

Find gaps in your learning:

```python
from learning.learning_manager import get_connection

conn = get_connection()
skills = {r["topic"]: r["level"] for r in conn.execute(
    "SELECT topic, level FROM skill_levels"
).fetchall()}

# Find gaps across all paths
all_paths = conn.execute("SELECT * FROM learning_paths").fetchall()
for path in all_paths:
    topics = json.loads(path["topics"])
    missing = [t for t in topics if t not in skills]
    if missing:
        print(f"Gap in {path['name']}: {missing}")
```

### Session Count

See which topics you've studied most:

```bash
python learning_manager.py history | grep "session_count DESC"
```

## File Reference

| File | Purpose |
|------|---------|
| `learning_manager.py` | CLI for progress tracking, path management, suggestions |
| `learning.db` | SQLite database (created on first run) |

## Best Practices

### Proficiency Self-Assessment

- **novice:** "I've heard of this, watched tutorials"
- **beginner:** "I've built something simple, can follow along"
- **intermediate:** "I build projects solo, debug common issues"
- **advanced:** "I optimize, mentor others, lead decisions"
- **expert:** "I architect systems, publish papers/talks"

### Documenting Progress

Be specific in `--notes`:
- ✓ "Built async web scraper with asyncio and aiohttp"
- ✓ "Debugged Docker networking issue with custom bridge"
- ✓ "Completed Stanford ML course, built image classifier"
- ✗ "Learned Docker"
- ✗ "Got better at Python"

### Long-term Tracking

Example 6-month arc:
```
Mar: Python beginner → intermediate (wrote flask app)
Apr: Docker novice → beginner (learned basics)
May: Python intermediate → advanced (optimized web scraper)
May: Docker beginner → intermediate (production multi-container setup)
Jun: Kubernetes novice → beginner (deployed first cluster)
```

### Learning Path Strategy

**Breadth first (exploratory):**
- Sample multiple paths to find interests
- Reach `intermediate` in 3–4 areas first
- Deepen based on project needs

**Depth first (mastery):**
- Complete one path to `advanced`+
- Become an expert in your domain
- Build credibility and specialization

## Troubleshooting

### Database locked
Wait 10 seconds. If persistent:
```bash
rm ~/.copilot/learning/learning.db-wal
```

### Custom paths not appearing
Verify topic names in `--topics` argument:
```bash
python learning_manager.py add-path \
  --name "DevOps Mastery" \
  --topics "Terraform,Ansible,Jenkins,Prometheus"
```

### Progress not updating
Ensure topic name matches exactly (case-sensitive):
```bash
python learning_manager.py list-paths  # Find exact topic name
python learning_manager.py progress --topic "EXACT_TOPIC_NAME" --level intermediate
```

---

**Next:** See `mcp/README.md` for the MCP servers configuration.
