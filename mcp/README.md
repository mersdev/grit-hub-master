# MCP Servers Configuration

Model Context Protocol (MCP) servers extend GitHub Copilot CLI with specialized tools and capabilities. This configuration defines 5 default servers and shows how to add more.

## What is MCP?

MCP is a standard for connecting Claude (and other AI models) to external data sources, tools, and services. Each MCP server provides a set of **resources** (read-only data) and **tools** (actions the model can take).

**Reference:** [Model Context Protocol](https://modelcontextprotocol.io/)

## Configuration File

**Location:** `mcp.json`

Structure:
```json
{
  "mcpServers": {
    "server-name": {
      "command": "...",           // How to invoke the server
      "args": [...],              // Arguments to pass
      "description": "...",       // What this server provides
      "type": "stdio"             // (optional) stdio or other
    }
  }
}
```

## Default MCP Servers

### 1. Filesystem Server

**Purpose:** Read and write files and directories

**Configuration:**
```json
{
  "command": "npx",
  "args": ["-y", "@modelcontextprotocol/server-filesystem", "%USERPROFILE%"],
  "description": "Read and write files in the user's home directory. Used for memory system, learning path, and project file access."
}
```

**Available Tools:**
- `read_file` — Read file contents
- `write_file` — Write/append to files
- `list_directory` — List directory contents
- `create_directory` — Create new directory

**Use cases:**
- Accessing memory database and exported markdown
- Reading/writing learning progress
- File-based project management

**Example Copilot usage:**
```
@copilot Read my memory recall results and suggest next learning steps
```

---

### 2. Memory Server

**Purpose:** In-session knowledge graph memory for short-term working memory

**Configuration:**
```json
{
  "command": "npx",
  "args": ["-y", "@modelcontextprotocol/server-memory"],
  "description": "In-session knowledge graph memory. Complements the persistent SQLite memory system for short-term working memory within a session."
}
```

**Available Tools:**
- `create_memory` — Save a fact or relationship
- `read_memory` — Query stored facts
- `delete_memory` — Remove a fact
- `list_memory` — List all facts in session

**Key difference from persistent memory:**
- **Session memory** (MCP): Ephemeral, session-scoped working memory
- **Persistent memory** (SQLite): Long-lived, cross-session knowledge base

**Use cases:**
- Tracking context within a long session
- Building up session-specific facts
- Temporary notes and observations

**Example Copilot usage:**
```
@copilot Remember that the user prefers async/await patterns over callbacks
```

---

### 3. Fetch Server

**Purpose:** Retrieve content from the web (HTTP/HTTPS)

**Configuration:**
```json
{
  "command": "npx",
  "args": ["-y", "@modelcontextprotocol/server-fetch"],
  "description": "Fetch web content for research, documentation lookup, and real-time information retrieval."
}
```

**Available Tools:**
- `fetch` — GET request with HTML/JSON response parsing
- `scrape` — Extract structured data from web pages

**Use cases:**
- Look up documentation
- Fetch API specifications
- Real-time information retrieval
- Research current best practices

**Example Copilot usage:**
```
@copilot Fetch the latest Python documentation on asyncio
@copilot Research how to set up GitHub Actions for CI/CD
```

---

### 4. Sequential Thinking Server

**Purpose:** Structured step-by-step reasoning for complex problems

**Configuration:**
```json
{
  "command": "npx",
  "args": ["-y", "@modelcontextprotocol/server-sequential-thinking"],
  "description": "Structured step-by-step reasoning for complex problems. Use for architecture decisions, debugging difficult issues, and multi-step planning."
}
```

**Available Tools:**
- `think` — Break down a problem into sequential steps
- `evaluate` — Assess solution quality
- `refine` — Improve based on feedback

**Use cases:**
- Complex debugging workflows
- Architecture design decisions
- Multi-step problem solving
- Learning new concepts step-by-step

**Example Copilot usage:**
```
@copilot Use structured thinking to debug this race condition
@copilot Plan the architecture for a distributed system
```

---

### 5. Draw.io Server (Optional)

**Purpose:** Real-time interactive diagram editing in a browser

**Configuration:**
```json
{
  "type": "stdio",
  "command": "cmd",
  "args": ["/c", "npx", "--yes", "@next-ai-drawio/mcp-server@latest"],
  "description": "Optional live draw.io browser editing session. Use only when you need real-time interactive diagram refinement in a browser. For offline .drawio generation, use the drawio skill directly."
}
```

**Available Tools:**
- `create_diagram` — Start a new diagram
- `edit_diagram` — Open diagram in browser for interactive editing
- `export_diagram` — Export to PNG/SVG/PDF

**Use cases:**
- Architecture diagrams
- System flow charts
- Database schemas
- Real-time collaborative design

**Example Copilot usage:**
```
@copilot Create an architecture diagram for a microservices system
@copilot Edit this diagram in draw.io
```

**Note:** This is optional because it requires a browser. For automated/offline diagram generation, use the `drawio` skill instead.

---

## Adding Custom MCP Servers

### Example 1: Slack Integration

Connect Copilot to your Slack workspace:

```json
{
  "slack": {
    "command": "node",
    "args": ["/path/to/slack-mcp-server.js"],
    "description": "Send messages to Slack, read channel history. Use for async communication and team notifications.",
    "env": {
      "SLACK_BOT_TOKEN": "${SLACK_BOT_TOKEN}",
      "SLACK_SIGNING_SECRET": "${SLACK_SIGNING_SECRET}"
    }
  }
}
```

**Usage:**
```
@copilot Send a summary of today's work to #updates channel
```

---

### Example 2: GitHub Integration

Interact with GitHub directly:

```json
{
  "github": {
    "command": "npx",
    "args": ["-y", "@modelcontextprotocol/server-github"],
    "description": "Create issues, pull requests, manage repositories. Use for GitHub workflow automation.",
    "env": {
      "GITHUB_TOKEN": "${GITHUB_TOKEN}"
    }
  }
}
```

**Usage:**
```
@copilot Create a GitHub issue for this bug
@copilot Comment on PR #42 with a code review
```

---

### Example 3: Database Integration

Query your databases:

```json
{
  "sqlite": {
    "command": "npx",
    "args": ["-y", "@modelcontextprotocol/server-sqlite"],
    "description": "Query SQLite databases. Use for memory system queries and project data analysis.",
    "args": ["--db-path", "/path/to/database.db"]
  }
}
```

**Usage:**
```
@copilot Query my memories for pattern recognition advice
```

---

### Example 4: Custom Python Server

Create your own MCP server in Python:

```json
{
  "custom-tools": {
    "command": "python",
    "args": ["/path/to/my_mcp_server.py"],
    "description": "Custom Python tools for project-specific tasks."
  }
}
```

**Minimal Python MCP Server:**
```python
#!/usr/bin/env python3
import json
import sys

def handle_request(request):
    if request["method"] == "tools/list":
        return {
            "tools": [
                {
                    "name": "analyze_code",
                    "description": "Analyze code for issues",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "code": {"type": "string"},
                            "language": {"type": "string"}
                        }
                    }
                }
            ]
        }
    elif request["method"] == "tool":
        if request["name"] == "analyze_code":
            code = request["input"]["code"]
            # Your custom logic here
            return {"result": f"Analysis of {len(code)} chars"}
    return {"error": "Unknown request"}

while True:
    try:
        line = sys.stdin.readline()
        if not line:
            break
        request = json.loads(line)
        response = handle_request(request)
        print(json.dumps(response))
        sys.stdout.flush()
    except Exception as e:
        print(json.dumps({"error": str(e)}), file=sys.stderr)
```

---

### Example 5: API Server Integration

Call your own APIs:

```json
{
  "api": {
    "command": "npx",
    "args": ["-y", "@modelcontextprotocol/server-http"],
    "description": "Make HTTP requests to your APIs. Use for custom backend integration.",
    "env": {
      "API_BASE_URL": "https://api.example.com",
      "API_KEY": "${API_KEY}"
    }
  }
}
```

---

## Best Practices

### 1. Environment Variables

Store sensitive data in environment variables, not in mcp.json:

```json
{
  "github": {
    "command": "npx",
    "args": ["-y", "@modelcontextprotocol/server-github"],
    "env": {
      "GITHUB_TOKEN": "${GITHUB_TOKEN}"
    }
  }
}
```

Set in your shell:
```bash
export GITHUB_TOKEN="gh_xxxxxxxxxxxx"
```

### 2. Server Initialization Order

List critical servers first (filesystem, memory) for faster startup:

```json
{
  "mcpServers": {
    "filesystem": { ... },
    "memory": { ... },
    "fetch": { ... }
  }
}
```

### 3. Lazy Loading

For heavy/optional servers, use conditional flags:

```json
{
  "drawio": {
    "command": "cmd",
    "args": ["/c", "..."],
    "disabled": false  // Set to true to skip on startup
  }
}
```

### 4. Testing New Servers

Before adding to production config:

```bash
# Test if server starts
npx -y @modelcontextprotocol/server-name --help

# Run in debug mode
npx -y @modelcontextprotocol/server-name --debug
```

### 5. Error Handling

Servers should gracefully handle:
- Missing environment variables
- Network timeouts
- Invalid input

Example error response:
```json
{
  "error": "GITHUB_TOKEN not set",
  "suggestion": "export GITHUB_TOKEN='gh_xxxxxxxxxxxx'"
}
```

---

## Testing Servers

### Verify a server is connected:

```
@copilot List all available tools from my MCP servers
```

### Test individual servers:

```
# Filesystem
@copilot List files in my memory directory

# Fetch
@copilot Fetch the GitHub API documentation

# Sequential Thinking
@copilot Use structured thinking to solve this problem
```

---

## Server Discovery

Find more MCP servers:

- **Official:** https://modelcontextprotocol.io/
- **Community:** GitHub search: `mcp-server` topic
- **Create your own:** See the SDK docs at modelcontextprotocol.io

---

## Troubleshooting

### Server fails to start
Check if the npm package exists:
```bash
npm search @modelcontextprotocol/server-{name}
```

### Environment variables not loaded
Verify they're exported in your shell:
```bash
echo $GITHUB_TOKEN
```

### Commands not available
Reload Copilot:
```bash
copilot --restart
```

### Port conflicts (for network servers)
Verify no other process is using the port:
```bash
netstat -an | grep LISTEN
```

---

## Server Manifest Reference

| Field | Required | Type | Purpose |
|-------|----------|------|---------|
| `command` | ✓ | string | Executable or npm package |
| `args` | | array | Arguments to pass to command |
| `type` | | string | stdio (default) or other |
| `description` | | string | What this server provides |
| `env` | | object | Environment variables |
| `disabled` | | boolean | Skip on startup if true |

---

**Next:** See `memory/README.md` for the persistent memory system, or `learning/README.md` for the learning tracker.
