# Memory System

A persistent, three-tier memory architecture for GitHub Copilot CLI sessions using SQLite with full-text search and hierarchical PageIndex-powered recall.

## Overview

The memory system stores knowledge across three dimensions:

### 1. **Episodic Memories**
Events, interactions, and notable occurrences recorded over time. Organized chronologically by month/year for temporal context.

- **Use case:** "What did we work on in May 2024?"
- **Retention:** Time-indexed, naturally expires through organization
- **Example:** Session summaries, completed project milestones, debugging breakthroughs

### 2. **Semantic Memories**
Facts, knowledge, and information about the user, their projects, and their world. Organized by category (tags).

- **Use case:** "What are my preferred coding patterns?"
- **Retention:** Importance-weighted, survives indefinitely
- **Example:** Developer preferences, project architectures, domain knowledge

### 3. **Procedural Memories**
Workflows, how-to knowledge, and learned patterns for getting things done. Organized by workflow type.

- **Use case:** "How do I set up a new Rust project?"
- **Retention:** Importance-weighted, refined over sessions
- **Example:** Deployment scripts, testing workflows, best practices

## Storage Architecture

```
memory/
├── memories.db                 # SQLite database (3 tables + FTS5 index)
├── memories_index.md           # Auto-exported hierarchical markdown
├── memories_tree.json          # PageIndex tree structure (cached)
├── memory_manager.py           # Main CLI tool
├── pageindex_recall.py         # Hierarchical retrieval engine
└── memory_to_md.py             # Export utility
```

### Database Schema

**`memories` table:**
```sql
CREATE TABLE memories (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    type        TEXT NOT NULL CHECK(type IN ('episodic','semantic','procedural')),
    content     TEXT NOT NULL,
    tags        TEXT DEFAULT '',
    importance  INTEGER DEFAULT 5 CHECK(importance BETWEEN 1 AND 10),
    created_at  TEXT NOT NULL,
    updated_at  TEXT NOT NULL,
    access_count INTEGER DEFAULT 0
);

CREATE VIRTUAL TABLE memories_fts USING fts5(content, tags);
```

**`memories_fts` (FTS5 index):**
Full-text search on content and tags. Automatically synced via triggers.

## PageIndex Integration

The system uses **PageIndex** (VectifyAI/PageIndex) for vectorless, reasoning-based retrieval:

1. **Export phase:** `memory_to_md.py` converts SQLite → hierarchical Markdown
2. **Index phase:** `pageindex_recall.py` builds a tree structure from headers
3. **Recall phase:** Hierarchical keyword scoring without embeddings

### Why PageIndex?

- ✓ **No LLM cost** — structural scoring only
- ✓ **Offline-capable** — works without API calls
- ✓ **Context-preserving** — includes full text excerpts
- ✓ **Reasoning-transparent** — see relevance scores

### PageIndex Scoring

Each node is scored on:
- **TF-style keyword frequency** in title + text
- **Title bonus** (title matches = 1.5x weight)
- **Depth bonus** (deeper nodes = more specific)
- **Importance signal** (extracted from memory metadata)
- **Access patterns** (frequently retrieved = ranked higher)

## Usage

### Save a Memory

```bash
python memory_manager.py save \
  --type semantic \
  --content "My preferred testing pattern: pytest with fixtures" \
  --tags "testing,patterns" \
  --importance 8
```

**Types:** `episodic`, `semantic`, `procedural`  
**Importance:** 1–10 (default: 5)

### Recall (Search) Memories

**Using PageIndex (hierarchical, recommended):**
```bash
python memory_manager.py recall \
  --query "testing patterns" \
  --type semantic \
  --limit 5
```

**Using FTS5 (fast, flat search):**
```bash
python memory_manager.py recall \
  --query "testing patterns" \
  --engine fts \
  --limit 5
```

Output shows:
- Memory ID and relevance score (0–10)
- Importance level (1–10)
- Full text excerpt
- Tags

### List Memories

```bash
# All memories
python memory_manager.py list --limit 20

# Filter by type
python memory_manager.py list --type semantic --limit 20

# Show episodic memories from a specific month
python memory_manager.py list --type episodic
```

### Delete a Memory

```bash
python memory_manager.py delete --id 42
```

### Statistics

```bash
python memory_manager.py stats
```

Output:
```
── Memory Stats ──────────────────────
  Total:       156
  Episodic:    48
  Semantic:    65
  Procedural:  43
  Database:    /path/to/memories.db
```

## PageIndex Recall Deep Dive

### Direct PageIndex Query

```bash
python pageindex_recall.py --query "python best practices"
```

Output shows:
```
── PageIndex Recall: 'python best practices' ──────
   Found 3 relevant memory section(s)

  [0001] Semantic Memories > coding > [id=12] Python best practices
  Score: 5.234 ██████  Depth: 3
  Memory IDs: [12]

    My preferred Python patterns:
    - Use type hints consistently
    - Leverage dataclasses for immutable data
    - Test-driven development with pytest...
```

### Show Memory Tree

```bash
python pageindex_recall.py --show-tree
```

Displays the full hierarchical structure:
```
── Memory Tree: Agent Memory Bank ──────────────────────
   Nodes: 156  |  Built: 2026-05-15 10:30

Episodic Memories
└─ 2026-05 — May 2026  [0015]
  └─ [id=48] Completed Rust project migration  [0016]
  └─ [id=49] Learned about async/await patterns  [0017]
Semantic Memories
└─ coding  [0042]
  └─ [id=12] Python best practices  [0043]
  └─ [id=13] Rust performance tips  [0044]
```

### Rebuild Cache

Tree is automatically rebuilt when markdown changes. Force rebuild:

```bash
python pageindex_recall.py --rebuild
```

## Integration with Copilot CLI

Link memory recall into your Copilot workflows:

```python
# In a copilot skill or task
import subprocess
import sys
from pathlib import Path

memory_dir = Path(__file__).parent / "memory"
result = subprocess.run(
    [sys.executable, memory_dir / "memory_manager.py", "recall",
     "--query", "your search query",
     "--limit", "5"],
    capture_output=True,
    text=True
)
print(result.stdout)
```

Or directly in Python:

```python
from memory.memory_manager import get_connection, recall_memories

conn = get_connection()
memories = recall_memories(conn, "python patterns", limit=5)
for m in memories:
    print(f"[{m['id']}] {m['content'][:100]}")
    print(f"  Importance: {m['importance']}/10, Tags: {m['tags']}")
```

## File Reference

| File | Purpose |
|------|---------|
| `memory_manager.py` | CLI for save/recall/list/delete/stats operations |
| `pageindex_recall.py` | Hierarchical search using PageIndex tree structure |
| `memory_to_md.py` | Export SQLite memories to hierarchical Markdown for indexing |
| `memories.db` | SQLite database (created on first run) |
| `memories_index.md` | Auto-generated Markdown snapshot (for PageIndex) |
| `memories_tree.json` | Cached PageIndex tree (auto-rebuilt when stale) |

## Best Practices

### Memory Selection
- **Episodic:** Session summaries, major milestones, debugging breakthroughs
- **Semantic:** Preferences, architectures, reusable facts, domain knowledge
- **Procedural:** Workflows, setup steps, deployment patterns, testing approach

### Tagging
- Use lowercase, comma-separated tags
- First tag = primary category (used in grouping)
- Examples: `testing,pytest`, `python,best-practices`, `workflow,deployment`

### Importance Scoring
- **1–3:** Nice-to-know facts
- **4–6:** Regular patterns (default: 5)
- **7–8:** Core knowledge, frequently referenced
- **9–10:** Critical patterns, must-remember

### Maintenance
- Periodically review episodic memories (6+ months old) to convert to semantic
- Update importance as your understanding deepens
- Delete outdated procedural memories

## Troubleshooting

### PageIndex not found
Ensure PageIndex is cloned to `~/.copilot/pageindex/`:
```bash
cd ~/.copilot
git clone https://github.com/VectifyAI/PageIndex.git pageindex
```

### Tree cache out of sync
Manually rebuild:
```bash
python pageindex_recall.py --rebuild
```

### FTS5 search not working
Verify SQLite version (3.9.0+):
```bash
python -c "import sqlite3; print(sqlite3.sqlite_version)"
```

### Memory database locked
Wait 10 seconds (WAL mode should auto-recover). If persistent, delete `memories.db-wal`:
```bash
rm ~/.copilot/memory/memories.db-wal
```

---

**Next:** See `learning/README.md` for the learning tracker system.
