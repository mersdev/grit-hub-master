#!/usr/bin/env python3
"""
boot.py — Session boot script for Copilot Agent Starter Kit
Run at the start of every Copilot session to load context.

Usage:
  python boot.py            # full boot (memory + learning + skills + MCP)
  python boot.py --brief    # one-liner summary
  python boot.py --memory   # memory stats only
"""

import argparse
import json
import sqlite3
import sys
from pathlib import Path

COPILOT_DIR = Path.home() / ".copilot"
MEMORY_DB = COPILOT_DIR / "memory" / "memories.db"
LEARNING_DB = COPILOT_DIR / "learning" / "learning.db"
SKILLS_DIR = COPILOT_DIR / "skills"
MCP_CONFIG = COPILOT_DIR / "mcp.json"


def memory_stats():
    if not MEMORY_DB.exists():
        return {"total": 0, "types": {}, "recent": []}
    conn = sqlite3.connect(str(MEMORY_DB))
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    try:
        cur.execute("SELECT COUNT(*) as c FROM memories")
        total = cur.fetchone()["c"]
        cur.execute("SELECT type, COUNT(*) as c FROM memories GROUP BY type")
        types = {row["type"]: row["c"] for row in cur.fetchall()}
        columns = {
            row["name"]
            for row in cur.execute("PRAGMA table_info(memories)").fetchall()
        }
        if "last_accessed" in columns:
            order_expr = "COALESCE(last_accessed, updated_at, created_at)"
        else:
            order_expr = "COALESCE(updated_at, created_at)"
        cur.execute(
            f"""
            SELECT content, type, importance
            FROM memories
            ORDER BY {order_expr} DESC
            LIMIT 3
            """
        )
        recent = [dict(row) for row in cur.fetchall()]
        return {"total": total, "types": types, "recent": recent}
    except Exception:
        return {"total": 0, "types": {}, "recent": []}
    finally:
        conn.close()


def learning_stats():
    if not LEARNING_DB.exists():
        return {"skills": 0, "paths": 0, "recent": []}
    conn = sqlite3.connect(str(LEARNING_DB))
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    try:
        cur.execute("SELECT COUNT(DISTINCT topic) as c FROM skill_levels")
        skills = cur.fetchone()["c"]
        cur.execute("SELECT COUNT(*) as c FROM learning_paths")
        paths = cur.fetchone()["c"]
        cur.execute("SELECT topic, level FROM skill_levels ORDER BY updated_at DESC LIMIT 3")
        recent = [dict(row) for row in cur.fetchall()]
        return {"skills": skills, "paths": paths, "recent": recent}
    except Exception:
        return {"skills": 0, "paths": 0, "recent": []}
    finally:
        conn.close()


def skills_list():
    if not SKILLS_DIR.exists():
        return []
    return sorted([f.stem for f in SKILLS_DIR.glob("*.md")])


def mcp_servers():
    if not MCP_CONFIG.exists():
        return []
    with open(MCP_CONFIG, encoding="utf-8") as f:
        cfg = json.load(f)
    return list(cfg.get("mcpServers", {}).keys())


def full_boot():
    print("=" * 55)
    print("  Copilot Agent — Session Boot")
    print("=" * 55)

    # Memory
    ms = memory_stats()
    print(f"\n  Memory: {ms['total']} memories stored")
    for mtype, count in ms["types"].items():
        print(f"    {mtype}: {count}")
    if ms["recent"]:
        print("  Recent:")
        for m in ms["recent"]:
            print(f"    [{m['type']}] {m['content'][:60]}...")

    # Learning
    ls = learning_stats()
    print(f"\n  Learning: {ls['skills']} skills tracked, {ls['paths']} paths")
    if ls["recent"]:
        for s in ls["recent"]:
            print(f"    {s['topic']}: {s['level']}")

    # Skills
    sk = skills_list()
    print(f"\n  Skills: {len(sk)} loaded")
    for s in sk[:10]:
        print(f"    {s}")
    if len(sk) > 10:
        print(f"    ... and {len(sk) - 10} more")

    # MCP
    servers = mcp_servers()
    print(f"\n  MCP Servers: {len(servers)}")
    for s in servers:
        print(f"    {s}")

    print("\n" + "=" * 55)
    print("  Ready. Type your request.")
    print("=" * 55)


def brief_boot():
    ms = memory_stats()
    ls = learning_stats()
    sk = skills_list()
    servers = mcp_servers()
    print(f"Agent ready | {ms['total']} memories | {ls['skills']} skills tracked | {len(sk)} skills loaded | {len(servers)} MCP servers")


def main():
    parser = argparse.ArgumentParser(description="Session boot script")
    parser.add_argument("--brief", action="store_true", help="One-liner summary")
    parser.add_argument("--memory", action="store_true", help="Memory stats only")
    args = parser.parse_args()

    if args.brief:
        brief_boot()
    elif args.memory:
        ms = memory_stats()
        print(f"Memory: {ms['total']} total | " +
              " | ".join(f"{k}: {v}" for k, v in ms["types"].items()))
    else:
        full_boot()


if __name__ == "__main__":
    main()
