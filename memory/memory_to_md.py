#!/usr/bin/env python3
"""
memory_to_md.py — Export SQLite memories to a hierarchical Markdown file
for PageIndex tree indexing.

The output markdown uses # headers to create a structure PageIndex can traverse:

# Agent Memory Bank
## Episodic Memories      (events & interactions)
### 2026-05 — May 2026
#### [id=1] Memory title...
## Semantic Memories      (facts & knowledge)
### identity
#### [id=2] Memory title...
## Procedural Memories    (how-to knowledge)
### workflow
#### [id=3] Memory title...
"""

import sqlite3
from datetime import datetime, timezone
from pathlib import Path


def _get_data_dir() -> Path:
    """Return the memory data directory based on where this script lives.

    .github/memory/...  → .github/memory/   (VS Code Copilot Chat, project-rooted)
    ~/.copilot/memory/... → ~/.copilot/memory/ (Copilot CLI, user-global)
    anything else       → ~/.copilot/memory/ (fallback)
    """
    script_dir = Path(__file__).resolve().parent

    # Running from .github/memory/ → use that directory
    if ".github" in script_dir.parts:
        return script_dir

    # Running from anywhere else → user-global
    return Path.home() / ".copilot" / "memory"


DATA_DIR  = _get_data_dir()
DB_PATH   = DATA_DIR / "memories.db"
MD_PATH   = DATA_DIR / "memories_index.md"


def get_all_memories(conn: sqlite3.Connection) -> list[dict]:
    conn.row_factory = sqlite3.Row
    rows = conn.execute(
        "SELECT * FROM memories ORDER BY type, tags, created_at"
    ).fetchall()
    return [dict(r) for r in rows]


def group_episodic(memories: list[dict]) -> dict:
    """Group episodic memories by YYYY-MM."""
    groups: dict[str, list] = {}
    for m in memories:
        key = m["created_at"][:7] if m.get("created_at") else "unknown"
        groups.setdefault(key, []).append(m)
    return groups


def group_by_tag(memories: list[dict]) -> dict:
    """Group semantic/procedural memories by their first tag."""
    groups: dict[str, list] = {}
    for m in memories:
        tags = [t.strip() for t in (m.get("tags") or "").split(",") if t.strip()]
        key = tags[0] if tags else "general"
        groups.setdefault(key, []).append(m)
    return groups


def memory_section(m: dict) -> str:
    """Render a single memory as a markdown section.

    The H4 heading identifies the memory by ID and type without duplicating
    body content (which would inflate PageIndex keyword scores).
    """
    tags = m.get("tags", "")
    mem_type = m.get("type", "unknown").title()
    date = m["created_at"][:10] if m.get("created_at") else "unknown"
    lines = [
        f"#### [id={m['id']}] {mem_type} Memory",
        "",
        f"**Content:** {m['content']}",
        "",
        f"- **Date:** {date}",
        f"- **Importance:** {m.get('importance', 5)}/10",
        f"- **Tags:** {tags}" if tags else "",
        f"- **Access count:** {m.get('access_count', 0)}",
        "",
    ]
    return "\n".join(l for l in lines if l)


def export_to_markdown(memories: list[dict]) -> str:
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    total = len(memories)

    lines = [
        "# Agent Memory Bank",
        "",
        f"> Auto-generated index of {total} memories. Last updated: {now}",
        "> Use PageIndex tree search to retrieve relevant memories by reasoning over this structure.",
        "",
    ]

    # ── Episodic ──────────────────────────────────────────────────────────────
    episodic = [m for m in memories if m["type"] == "episodic"]
    lines += [
        "## Episodic Memories",
        "",
        "Events, interactions, and notable occurrences recorded over time.",
        "",
    ]
    if episodic:
        for period, mems in sorted(group_episodic(episodic).items()):
            try:
                label = datetime.strptime(period, "%Y-%m").strftime("%B %Y")
            except ValueError:
                label = period
            lines += [f"### {period} — {label}", ""]
            for m in sorted(mems, key=lambda x: x["created_at"]):
                lines.append(memory_section(m))
    else:
        lines += ["*No episodic memories yet.*", ""]

    # ── Semantic ──────────────────────────────────────────────────────────────
    semantic = [m for m in memories if m["type"] == "semantic"]
    lines += [
        "## Semantic Memories",
        "",
        "Facts, knowledge, and information about the user, their projects, and their world.",
        "",
    ]
    if semantic:
        for tag, mems in sorted(group_by_tag(semantic).items()):
            lines += [f"### {tag}", ""]
            for m in sorted(mems, key=lambda x: -x.get("importance", 5)):
                lines.append(memory_section(m))
    else:
        lines += ["*No semantic memories yet.*", ""]

    # ── Procedural ────────────────────────────────────────────────────────────
    procedural = [m for m in memories if m["type"] == "procedural"]
    lines += [
        "## Procedural Memories",
        "",
        "Workflows, how-to knowledge, and learned patterns for getting things done.",
        "",
    ]
    if procedural:
        for tag, mems in sorted(group_by_tag(procedural).items()):
            lines += [f"### {tag}", ""]
            for m in sorted(mems, key=lambda x: -x.get("importance", 5)):
                lines.append(memory_section(m))
    else:
        lines += ["*No procedural memories yet.*", ""]

    return "\n".join(lines)


def export(db_path: Path = DB_PATH, md_path: Path = MD_PATH) -> Path:
    if not db_path.exists():
        raise FileNotFoundError(f"Memory database not found: {db_path}")
    md_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(db_path))
    memories = get_all_memories(conn)
    conn.close()
    md_content = export_to_markdown(memories)
    md_path.write_text(md_content, encoding="utf-8")
    return md_path


if __name__ == "__main__":
    out = export()
    print(f"✓ Exported {out}")
