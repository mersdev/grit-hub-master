#!/usr/bin/env python3
"""
Hermes Memory Manager
Persistent memory system for GitHub Copilot CLI sessions.
Stores episodic, semantic, and procedural memories in SQLite.

Usage:
  memory_manager.py save   --type <episodic|semantic|procedural> --content "text" [--tags "t1,t2"]
  memory_manager.py recall --query "search text" [--type <type>] [--limit 5]
  memory_manager.py list   [--type <type>] [--limit 20]
  memory_manager.py delete --id <memory_id>
  memory_manager.py stats
"""

import argparse
import sqlite3
import sys
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


DB_PATH = _get_data_dir() / "memories.db"


def get_connection() -> sqlite3.Connection:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    # WAL mode for multi-agent concurrency: readers never block writers
    conn.execute("PRAGMA journal_mode=WAL")
    # Wait up to 5s on lock contention instead of immediate SQLITE_BUSY
    conn.execute("PRAGMA busy_timeout = 5000")
    # Auto-checkpoint every 1000 pages (~4 MB) to prevent unbounded WAL growth
    conn.execute("PRAGMA wal_autocheckpoint = 1000")
    conn.execute("""
        CREATE TABLE IF NOT EXISTS memories (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            type        TEXT NOT NULL CHECK(type IN ('episodic','semantic','procedural')),
            content     TEXT NOT NULL,
            tags        TEXT DEFAULT '',
            importance  INTEGER DEFAULT 5 CHECK(importance BETWEEN 1 AND 10),
            created_at  TEXT NOT NULL,
            updated_at  TEXT NOT NULL,
            last_accessed TEXT,
            access_count INTEGER DEFAULT 0
        )
    """)
    _ensure_column(conn, "memories", "last_accessed", "TEXT")
    conn.execute("""
        CREATE VIRTUAL TABLE IF NOT EXISTS memories_fts USING fts5(
            content, tags,
            content='memories',
            content_rowid='id'
        )
    """)
    conn.execute("""
        CREATE TRIGGER IF NOT EXISTS memories_ai AFTER INSERT ON memories BEGIN
            INSERT INTO memories_fts(rowid, content, tags)
            VALUES (new.id, new.content, new.tags);
        END
    """)
    conn.execute("""
        CREATE TRIGGER IF NOT EXISTS memories_ad AFTER DELETE ON memories BEGIN
            INSERT INTO memories_fts(memories_fts, rowid, content, tags)
            VALUES ('delete', old.id, old.content, old.tags);
        END
    """)
    conn.execute("""
        CREATE TRIGGER IF NOT EXISTS memories_au AFTER UPDATE ON memories BEGIN
            INSERT INTO memories_fts(memories_fts, rowid, content, tags)
            VALUES ('delete', old.id, old.content, old.tags);
            INSERT INTO memories_fts(rowid, content, tags)
            VALUES (new.id, new.content, new.tags);
        END
    """)
    conn.commit()
    return conn


def _ensure_column(conn: sqlite3.Connection, table: str, column: str, definition: str) -> None:
    columns = {
        row["name"]
        for row in conn.execute(f"PRAGMA table_info({table})").fetchall()
    }
    if column not in columns:
        conn.execute(f"ALTER TABLE {table} ADD COLUMN {column} {definition}")


def _touch_memory_accesses(conn: sqlite3.Connection, memory_ids: list[int]) -> None:
    if not memory_ids:
        return
    now = datetime.now(timezone.utc).isoformat()
    placeholders = ",".join("?" * len(memory_ids))
    conn.execute(
        f"""
        UPDATE memories
        SET access_count = access_count + 1,
            last_accessed = ?
        WHERE id IN ({placeholders})
        """,
        [now, *memory_ids],
    )
    conn.commit()


def save_memory(conn: sqlite3.Connection, memory_type: str, content: str,
                tags: str = "", importance: int = 5) -> int:
    now = datetime.now(timezone.utc).isoformat()
    cur = conn.execute(
        "INSERT INTO memories (type, content, tags, importance, created_at, updated_at, last_accessed) "
        "VALUES (?, ?, ?, ?, ?, ?, ?)",
        (memory_type, content, tags, importance, now, now, now)
    )
    conn.commit()
    return cur.lastrowid


def recall_memories(conn: sqlite3.Connection, query: str,
                    memory_type: str = None, limit: int = 5) -> list:
    if memory_type:
        rows = conn.execute("""
            SELECT m.*, rank FROM memories m
            JOIN memories_fts f ON m.id = f.rowid
            WHERE memories_fts MATCH ? AND m.type = ?
            ORDER BY rank, m.importance DESC, m.access_count DESC
            LIMIT ?
        """, (query, memory_type, limit)).fetchall()
    else:
        rows = conn.execute("""
            SELECT m.*, rank FROM memories m
            JOIN memories_fts f ON m.id = f.rowid
            WHERE memories_fts MATCH ?
            ORDER BY rank, m.importance DESC, m.access_count DESC
            LIMIT ?
        """, (query, limit)).fetchall()

    ids = [r["id"] for r in rows]
    _touch_memory_accesses(conn, ids)

    return [dict(r) for r in rows]


def list_memories(conn: sqlite3.Connection, memory_type: str = None, limit: int = 20) -> list:
    if memory_type:
        rows = conn.execute(
            "SELECT * FROM memories WHERE type = ? ORDER BY updated_at DESC LIMIT ?",
            (memory_type, limit)
        ).fetchall()
    else:
        rows = conn.execute(
            "SELECT * FROM memories ORDER BY updated_at DESC LIMIT ?",
            (limit,)
        ).fetchall()
    return [dict(r) for r in rows]


def delete_memory(conn: sqlite3.Connection, memory_id: int) -> bool:
    cur = conn.execute("DELETE FROM memories WHERE id = ?", (memory_id,))
    conn.commit()
    return cur.rowcount > 0


def get_stats(conn: sqlite3.Connection) -> dict:
    stats = {}
    for mtype in ("episodic", "semantic", "procedural"):
        row = conn.execute(
            "SELECT COUNT(*) as cnt FROM memories WHERE type = ?", (mtype,)
        ).fetchone()
        stats[mtype] = row["cnt"]
    row = conn.execute("SELECT COUNT(*) as cnt FROM memories").fetchone()
    stats["total"] = row["cnt"]
    return stats


def format_memory(m: dict) -> str:
    mem_id = m.get("id", "?")
    mem_type = m.get("type", "unknown").upper()
    importance = m.get("importance", "?")
    created = (m.get("created_at") or "")[:10] or "?"
    content = m.get("content", "")
    tags = f"  tags: {m['tags']}" if m.get("tags") else ""
    return (
        f"[{mem_id}] [{mem_type}] (importance: {importance}) "
        f"{created}\n"
        f"  {content}{tags}"
    )


def recall_pageindex(query: str, memory_type: str = None, limit: int = 5) -> None:
    """PageIndex-powered hierarchical recall (in-process, fast)."""
    from pageindex_recall import get_tree, hierarchical_recall, print_results

    tree = get_tree()
    results = hierarchical_recall(
        tree,
        query=query,
        memory_type=memory_type,
        limit=limit,
    )
    mem_ids = sorted({mid for result in results for mid in result.get("mem_ids", [])})
    if mem_ids:
        conn = get_connection()
        try:
            _touch_memory_accesses(conn, mem_ids)
        finally:
            conn.close()
    print_results(results, query)


# ── argparse validators ─────────────────────────────────────────────────────

def _importance_arg(value: str) -> int:
    """Validate importance is 1-10."""
    val = int(value)
    if not 1 <= val <= 10:
        raise argparse.ArgumentTypeError(f"Importance must be 1-10, got {val}")
    return val


def _limit_arg(value: str) -> int:
    """Validate limit is positive, cap at 1000."""
    val = int(value)
    if val < 1:
        raise argparse.ArgumentTypeError(f"Limit must be >= 1, got {val}")
    return min(val, 1000)


def main():
    parser = argparse.ArgumentParser(description="Hermes Memory Manager")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # save
    p_save = subparsers.add_parser("save", help="Save a new memory")
    p_save.add_argument("--type", required=True, choices=["episodic", "semantic", "procedural"])
    p_save.add_argument("--content", required=True)
    p_save.add_argument("--tags", default="")
    p_save.add_argument("--importance", type=_importance_arg, default=5,
                        help="1-10 (default: 5)")

    # recall
    p_recall = subparsers.add_parser("recall", help="Search memories")
    p_recall.add_argument("--query", required=True)
    p_recall.add_argument("--type", choices=["episodic", "semantic", "procedural"])
    p_recall.add_argument("--limit", type=_limit_arg, default=5,
                          help="Max results, 1-1000 (default: 5)")
    p_recall.add_argument(
        "--engine",
        choices=["fts", "pageindex"],
        default="fts",
        help="Retrieval engine: 'fts' (fast SQLite FTS5, default) or "
             "'pageindex' (hierarchical tree search)"
    )

    # list
    p_list = subparsers.add_parser("list", help="List memories")
    p_list.add_argument("--type", choices=["episodic", "semantic", "procedural"])
    p_list.add_argument("--limit", type=_limit_arg, default=20,
                        help="Max results, 1-1000 (default: 20)")

    # delete
    p_del = subparsers.add_parser("delete", help="Delete a memory by ID")
    p_del.add_argument("--id", type=int, required=True)

    # stats
    subparsers.add_parser("stats", help="Show memory statistics")

    args = parser.parse_args()

    try:
        conn = get_connection()
        try:
            if args.command == "save":
                mid = save_memory(conn, args.type, args.content,
                                  args.tags, args.importance)
                print(f"Memory saved [id={mid}]")

            elif args.command == "recall":
                if args.engine == "pageindex":
                    # Close the DB connection so PageIndex can open its own
                    conn.close()
                    recall_pageindex(args.query, args.type, args.limit)
                    return
                # FTS default
                memories = recall_memories(conn, args.query, args.type, args.limit)
                if not memories:
                    print("No matching memories found.")
                else:
                    print(f"Found {len(memories)} memories:\n")
                    for m in memories:
                        print(format_memory(m))
                        print()

            elif args.command == "list":
                memories = list_memories(conn, args.type, args.limit)
                if not memories:
                    print("No memories stored yet.")
                else:
                    print(f"Showing {len(memories)} memories:\n")
                    for m in memories:
                        print(format_memory(m))
                        print()

            elif args.command == "delete":
                if delete_memory(conn, args.id):
                    print(f"Memory [id={args.id}] deleted.")
                else:
                    print(f"No memory found with id={args.id}")

            elif args.command == "stats":
                stats = get_stats(conn)
                print("── Memory Stats ──────────────────")
                print(f"  Total:       {stats['total']}")
                print(f"  Episodic:    {stats['episodic']}")
                print(f"  Semantic:    {stats['semantic']}")
                print(f"  Procedural:  {stats['procedural']}")
                print(f"  Database:    {DB_PATH}")
        finally:
            conn.close()
    except sqlite3.OperationalError as e:
        print(f"Error: Database operation failed — {e}", file=sys.stderr)
        sys.exit(1)
    except sqlite3.IntegrityError as e:
        print(f"Error: Data constraint violation — {e}", file=sys.stderr)
        sys.exit(1)
    except FileNotFoundError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error: {type(e).__name__}: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
