#!/usr/bin/env python3
"""
Hermes Learning Path Manager
Tracks learning progress, curricula, and skill levels across sessions.

Usage:
  learning_manager.py status                        — current progress overview
  learning_manager.py progress --topic "X" --level beginner --notes "what I learned"
  learning_manager.py add-path --name "Python Mastery" --description "..." --topics "t1,t2,t3"
  learning_manager.py list-paths
  learning_manager.py suggest                       — suggest next learning steps
  learning_manager.py history [--topic "X"] [--limit 10]
"""

import argparse
import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path

DB_PATH = Path(__file__).parent / "learning.db"
LEVELS = ["novice", "beginner", "intermediate", "advanced", "expert"]


def get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")

    conn.executescript("""
        CREATE TABLE IF NOT EXISTS learning_paths (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            name        TEXT NOT NULL UNIQUE,
            description TEXT DEFAULT '',
            topics      TEXT DEFAULT '[]',
            created_at  TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS topic_progress (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            topic       TEXT NOT NULL,
            level       TEXT NOT NULL,
            notes       TEXT DEFAULT '',
            path_id     INTEGER REFERENCES learning_paths(id),
            recorded_at TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS skill_levels (
            topic       TEXT PRIMARY KEY,
            level       TEXT NOT NULL,
            updated_at  TEXT NOT NULL,
            session_count INTEGER DEFAULT 1
        );
    """)
    conn.commit()

    # Seed default learning paths if none exist
    row = conn.execute("SELECT COUNT(*) as cnt FROM learning_paths").fetchone()
    if row["cnt"] == 0:
        now = datetime.now(timezone.utc).isoformat()
        default_paths = [
            (
                "Software Engineering Fundamentals",
                "Core software engineering concepts every developer should know",
                json.dumps([
                    "Data Structures", "Algorithms", "Design Patterns", "Testing",
                    "Version Control", "CI/CD", "System Design", "Security Basics"
                ]),
                now
            ),
            (
                "AI & Machine Learning",
                "From ML fundamentals to modern LLM applications",
                json.dumps([
                    "Statistics & Probability", "Linear Algebra", "Python for ML",
                    "Classical ML", "Deep Learning", "NLP", "LLMs & Prompt Engineering",
                    "AI Agents", "Fine-tuning", "MLOps"
                ]),
                now
            ),
            (
                "Cloud & DevOps",
                "Modern cloud infrastructure and DevOps practices",
                json.dumps([
                    "Linux Fundamentals", "Networking", "Docker", "Kubernetes",
                    "Terraform", "AWS/Azure/GCP", "Monitoring", "GitOps"
                ]),
                now
            ),
        ]
        conn.executemany(
            "INSERT INTO learning_paths (name, description, topics, created_at) VALUES (?,?,?,?)",
            default_paths
        )
        conn.commit()

    return conn


def record_progress(conn: sqlite3.Connection, topic: str, level: str, notes: str = "",
                    path_id: int = None):
    if level not in LEVELS:
        print(f"✗ Invalid level '{level}'. Choose from: {', '.join(LEVELS)}")
        return

    now = datetime.now(timezone.utc).isoformat()
    conn.execute(
        "INSERT INTO topic_progress (topic, level, notes, path_id, recorded_at) VALUES (?,?,?,?,?)",
        (topic, level, notes, path_id, now)
    )
    conn.execute("""
        INSERT INTO skill_levels (topic, level, updated_at, session_count)
        VALUES (?, ?, ?, 1)
        ON CONFLICT(topic) DO UPDATE SET
            level = excluded.level,
            updated_at = excluded.updated_at,
            session_count = session_count + 1
    """, (topic, level, now))
    conn.commit()
    print(f"✓ Progress recorded: {topic} → {level}")


def get_status(conn: sqlite3.Connection):
    skills = conn.execute(
        "SELECT topic, level, updated_at, session_count FROM skill_levels ORDER BY updated_at DESC"
    ).fetchall()

    if not skills:
        print("No learning progress recorded yet.")
        print("Start with: learning_manager.py progress --topic 'Python' --level beginner")
        return

    print("── Current Skill Levels ─────────────────────────────────")
    level_groups = {lv: [] for lv in LEVELS}
    for s in skills:
        lv = s["level"]
        if lv in level_groups:
            level_groups[lv].append(s["topic"])

    for lv in reversed(LEVELS):
        topics = level_groups[lv]
        if topics:
            bar = "█" * (LEVELS.index(lv) + 1)
            print(f"  {lv.upper():12} {bar}  {', '.join(topics)}")

    print(f"\n  Total topics tracked: {len(skills)}")


def suggest_next(conn: sqlite3.Connection):
    skills = {r["topic"]: r["level"] for r in conn.execute(
        "SELECT topic, level FROM skill_levels"
    ).fetchall()}

    paths = conn.execute("SELECT * FROM learning_paths").fetchall()
    print("── Suggested Next Steps ─────────────────────────────────")
    suggestions = []

    for path in paths:
        topics = json.loads(path["topics"])
        for i, topic in enumerate(topics):
            current_level = skills.get(topic)
            if current_level is None:
                # Not started — suggest if previous is done or it's first
                if i == 0 or skills.get(topics[i - 1]) in ("advanced", "expert"):
                    suggestions.append(
                        f"  START  [{path['name']}] → {topic} (novice → beginner)"
                    )
            elif LEVELS.index(current_level) < len(LEVELS) - 2:
                next_level = LEVELS[LEVELS.index(current_level) + 1]
                suggestions.append(
                    f"  LEVEL UP  [{path['name']}] → {topic}: {current_level} → {next_level}"
                )

    if not suggestions:
        print("  You're on track! Keep building depth in your current skills.")
    else:
        for s in suggestions[:8]:
            print(s)


def list_paths(conn: sqlite3.Connection):
    paths = conn.execute("SELECT * FROM learning_paths ORDER BY id").fetchall()
    print("── Learning Paths ───────────────────────────────────────")
    for path in paths:
        topics = json.loads(path["topics"])
        print(f"\n  [{path['id']}] {path['name']}")
        print(f"       {path['description']}")
        print(f"       Topics ({len(topics)}): {', '.join(topics)}")


def add_path(conn: sqlite3.Connection, name: str, description: str, topics: str):
    topic_list = [t.strip() for t in topics.split(",") if t.strip()]
    now = datetime.now(timezone.utc).isoformat()
    try:
        conn.execute(
            "INSERT INTO learning_paths (name, description, topics, created_at) VALUES (?,?,?,?)",
            (name, description, json.dumps(topic_list), now)
        )
        conn.commit()
        print(f"✓ Learning path '{name}' created with {len(topic_list)} topics.")
    except sqlite3.IntegrityError:
        print(f"✗ A path named '{name}' already exists.")


def show_history(conn: sqlite3.Connection, topic: str = None, limit: int = 10):
    if topic:
        rows = conn.execute(
            "SELECT * FROM topic_progress WHERE topic LIKE ? ORDER BY recorded_at DESC LIMIT ?",
            (f"%{topic}%", limit)
        ).fetchall()
    else:
        rows = conn.execute(
            "SELECT * FROM topic_progress ORDER BY recorded_at DESC LIMIT ?", (limit,)
        ).fetchall()

    print(f"── Learning History (last {limit}) ──────────────────────")
    for r in rows:
        print(f"  {r['recorded_at'][:10]}  {r['topic']:25} → {r['level']:12}  {r['notes'][:60]}")


def main():
    parser = argparse.ArgumentParser(description="Hermes Learning Path Manager")
    subparsers = parser.add_subparsers(dest="command", required=True)

    subparsers.add_parser("status", help="Show current skill levels")
    subparsers.add_parser("suggest", help="Suggest next learning steps")
    subparsers.add_parser("list-paths", help="List available learning paths")

    p_prog = subparsers.add_parser("progress", help="Record learning progress")
    p_prog.add_argument("--topic", required=True)
    p_prog.add_argument("--level", required=True, choices=LEVELS)
    p_prog.add_argument("--notes", default="")
    p_prog.add_argument("--path-id", type=int)

    p_add = subparsers.add_parser("add-path", help="Create a new learning path")
    p_add.add_argument("--name", required=True)
    p_add.add_argument("--description", default="")
    p_add.add_argument("--topics", required=True, help="Comma-separated list of topics")

    p_hist = subparsers.add_parser("history", help="Show learning history")
    p_hist.add_argument("--topic")
    p_hist.add_argument("--limit", type=int, default=10)

    args = parser.parse_args()
    conn = get_connection()

    if args.command == "status":
        get_status(conn)
    elif args.command == "suggest":
        suggest_next(conn)
    elif args.command == "list-paths":
        list_paths(conn)
    elif args.command == "progress":
        record_progress(conn, args.topic, args.level, args.notes,
                        getattr(args, "path_id", None))
    elif args.command == "add-path":
        add_path(conn, args.name, args.description, args.topics)
    elif args.command == "history":
        show_history(conn, getattr(args, "topic", None), args.limit)

    conn.close()


if __name__ == "__main__":
    main()
