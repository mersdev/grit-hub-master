#!/usr/bin/env python3
"""
pageindex_recall.py — PageIndex-style hierarchical keyword memory retrieval.

How it works:
  1. Export SQLite memories → structured Markdown (memory_to_md.py)
  2. Build PageIndex tree from the Markdown (VectifyAI/PageIndex page_index_md.py)
  3. Traverse the tree with hierarchical keyword scoring to find the most relevant nodes
  4. Return ranked memory sections with full context

This is vectorless, structural retrieval:
  - No embeddings or vector DB needed
  - Tree structure preserves the episodic/semantic/procedural hierarchy
  - Scoring combines keyword frequency, node depth, and importance signals

Usage:
  python pageindex_recall.py --query "python preferences" [--limit 5] [--type semantic]
  python pageindex_recall.py --rebuild        # force rebuild tree index
  python pageindex_recall.py --show-tree      # display tree structure
"""

import argparse
import json
import math
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

# ── Paths ─────────────────────────────────────────────────────────────────────

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


DATA_DIR     = _get_data_dir()
DB_PATH      = DATA_DIR / "memories.db"
MD_PATH      = DATA_DIR / "memories_index.md"
TREE_PATH    = DATA_DIR / "memories_tree.json"

# PageIndex lives in ~/.copilot/pageindex (Copilot CLI extension directory)
PAGEINDEX_DIR = Path.home() / ".copilot" / "pageindex"

sys.path.insert(0, str(PAGEINDEX_DIR))


def _import_pageindex():
    """Import PageIndex tree builder, gracefully handling missing litellm."""
    try:
        from pageindex.page_index_md import (
            extract_nodes_from_markdown,
            extract_node_text_content,
            build_tree_from_nodes,
            clean_tree_for_output,
        )
        return extract_nodes_from_markdown, extract_node_text_content, build_tree_from_nodes, clean_tree_for_output
    except ImportError as e:
        print(f"⚠  PageIndex import issue: {e}", file=sys.stderr)
        return None, None, None, None


# ── Tree Building (no LLM required) ──────────────────────────────────────────

def build_tree_from_markdown(md_path: Path) -> dict:
    """
    Build PageIndex tree structure from markdown WITHOUT calling any LLM.
    Uses the structural headers only — fast, free, offline.
    """
    extract_nodes, extract_text, build_tree, clean_tree = _import_pageindex()
    if extract_nodes is None:
        # Fallback: minimal inline parser if PageIndex unavailable
        return _fallback_tree_builder(md_path)

    content = md_path.read_text(encoding="utf-8")
    line_count = content.count("\n") + 1

    node_list, md_lines = extract_nodes(content)
    nodes_with_text = extract_text(node_list, md_lines)
    tree_structure = build_tree(nodes_with_text)
    cleaned = clean_tree_for_output(tree_structure)

    return {
        "doc_name": "Agent Memory Bank",
        "doc_description": "Hierarchical index of episodic, semantic, and procedural memories.",
        "line_count": line_count,
        "built_at": datetime.now(timezone.utc).isoformat(),
        "structure": cleaned,
    }


def _read_text_with_fallback(path: Path) -> str:
    """Read text file with encoding fallback: UTF-8 → cp1252 → latin-1."""
    for enc in ("utf-8", "cp1252", "latin-1"):
        try:
            return path.read_text(encoding=enc)
        except (UnicodeDecodeError, UnicodeError):
            continue
    return path.read_text(encoding="utf-8", errors="replace")


def _fallback_tree_builder(md_path: Path) -> dict:
    """Minimal tree builder used if PageIndex package is unavailable.

    Builds a properly nested tree structure from markdown headers:
    - h1 headers are root nodes
    - h2..h6 are nested under their nearest parent with a lower level
    - Text between a header and the next header becomes that node's content
    """
    content = _read_text_with_fallback(md_path)
    lines = content.split("\n")

    # ── Pass 1: locate all headers ──────────────────────────────────────────
    header_positions = []
    for i, line in enumerate(lines):
        m = re.match(r"^(#{1,6})\s+(.+)$", line)
        if m:
            header_positions.append({
                "line_idx": i,
                "line_num": i + 1,
                "level": len(m.group(1)),
                "title": m.group(2).strip(),
            })

    if not header_positions:
        return {
            "doc_name": "Agent Memory Bank",
            "doc_description": "Fallback tree (PageIndex unavailable — no headers found)",
            "built_at": datetime.now(timezone.utc).isoformat(),
            "structure": [],
        }

    # ── Pass 2: build flat node list with text ──────────────────────────────
    nodes_data = []
    for idx, h in enumerate(header_positions):
        start = h["line_idx"] + 1  # line after the header itself
        if idx + 1 < len(header_positions):
            end = header_positions[idx + 1]["line_idx"]
        else:
            end = len(lines)
        text = "\n".join(lines[start:end]).strip()

        nodes_data.append({
            "title": h["title"],
            "node_id": str(idx + 1).zfill(4),
            "line_num": h["line_num"],
            "level": h["level"],
            "text": text,
            "nodes": [],
        })

    # ── Pass 3: nest nodes using a level stack ──────────────────────────────
    root = []
    # stack holds (level, node) — the chain of ancestors
    stack: list[tuple[int, dict]] = []

    for node in nodes_data:
        level = node["level"]

        # Pop until we find a parent with strictly lower level
        while stack and stack[-1][0] >= level:
            stack.pop()

        if stack:
            stack[-1][1]["nodes"].append(node)
        else:
            root.append(node)

        stack.append((level, node))

    return {
        "doc_name": "Agent Memory Bank",
        "doc_description": "Fallback tree (PageIndex unavailable)",
        "built_at": datetime.now(timezone.utc).isoformat(),
        "structure": root,
    }


def save_tree(tree: dict, path: Path = TREE_PATH):
    path.write_text(json.dumps(tree, ensure_ascii=False, indent=2), encoding="utf-8")


def load_tree(path: Path = TREE_PATH) -> dict | None:
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return None


def tree_is_stale(tree: dict, md_path: Path = MD_PATH) -> bool:
    """Return True if the markdown is newer than the cached tree."""
    built_at = tree.get("built_at")
    if not built_at:
        return True
    try:
        tree_time = datetime.fromisoformat(built_at)
        md_time = datetime.fromtimestamp(md_path.stat().st_mtime, tz=timezone.utc)
        return md_time > tree_time
    except Exception:
        return True


def get_tree(force_rebuild: bool = False) -> dict:
    """Get the tree index, rebuilding only if stale or missing.

    The staleness check compares the cached tree's build timestamp against
    the SQLite database's mtime (the true source of truth), not the
    intermediate markdown file.
    """
    from memory_to_md import export

    # Check whether a rebuild is needed BEFORE touching the filesystem
    cached = load_tree()
    needs_rebuild = force_rebuild or not cached
    if not needs_rebuild:
        # Compare against DB mtime, not MD mtime — the DB is the source of truth.
        # The markdown is always regenerated from the DB anyway.
        try:
            db_mtime = datetime.fromtimestamp(DB_PATH.stat().st_mtime, tz=timezone.utc)
            tree_time = _parse_tree_timestamp(cached.get("built_at"))
            needs_rebuild = tree_time is None or db_mtime > tree_time
        except (OSError, ValueError):
            needs_rebuild = True

    if not needs_rebuild:
        return cached

    # Re-export memories to markdown, then build the tree
    export(DB_PATH, MD_PATH)
    print("  Building PageIndex tree from memory markdown...", file=sys.stderr)
    tree = build_tree_from_markdown(MD_PATH)
    save_tree(tree)
    print(f"  Tree built: {len(_flatten_tree(tree['structure']))} nodes", file=sys.stderr)
    return tree


def _parse_tree_timestamp(built_at: str | None) -> datetime | None:
    """Parse a tree's built_at timestamp safely across Python versions.

    datetime.fromisoformat() only supports timezone offsets in 3.11+.
    On 3.10, timestamps like '2026-06-22T12:00:00+00:00' raise ValueError.
    This helper strips the tz offset and re-attaches it explicitly.
    """
    if not built_at:
        return None
    try:
        # Try native fromisoformat first (3.11+)
        return datetime.fromisoformat(built_at)
    except ValueError:
        # Python 3.10 fallback: strip tz offset, parse naive, attach UTC
        import re as _re
        naive = _re.sub(r"\+00:00$", "", built_at)
        try:
            return datetime.fromisoformat(naive).replace(tzinfo=timezone.utc)
        except ValueError:
            return None


# ── Tree Traversal & Scoring ──────────────────────────────────────────────────

def _flatten_tree(nodes: list, depth: int = 0) -> list[dict]:
    """Flatten tree into list of (node, depth) pairs."""
    result = []
    for node in nodes:
        result.append({**node, "_depth": depth})
        if node.get("nodes"):
            result.extend(_flatten_tree(node["nodes"], depth + 1))
    return result


def _tokenize(text: str) -> list[str]:
    """Simple word tokenizer."""
    return re.findall(r"\b[a-zA-Z0-9_\-]+\b", text.lower())


def _score_node(node: dict, query_tokens: set[str], depth: int) -> float:
    """
    Score a tree node for relevance to a query.
    Combines:
      - TF-style keyword frequency in node text + title
      - Depth bonus (leaf nodes = more specific content)
      - Importance signal extracted from text
    """
    title = node.get("title", "")
    text  = node.get("text", "")
    combined = (title + " " + text).lower()
    node_tokens = _tokenize(combined)

    if not node_tokens:
        return 0.0

    # Keyword hit score
    hits = sum(1 for t in node_tokens if t in query_tokens)
    title_hits = sum(1 for t in _tokenize(title.lower()) if t in query_tokens)

    # No keyword match = not relevant (don't score on depth/importance alone)
    if hits == 0 and title_hits == 0:
        return 0.0

    # TF-like: hits / log(total_tokens + 1)
    tf = hits / math.log(len(node_tokens) + 2)

    # Title bonus (title hits are more informative)
    title_bonus = title_hits * 1.5

    # Depth bonus (deeper = more specific) — only when relevant
    depth_bonus = depth * 0.3

    # Importance signal: look for "importance: N" in text
    imp_match = re.search(r"\*\*Importance:\*\*\s*(\d+)", text)
    importance = int(imp_match.group(1)) / 10.0 if imp_match else 0.5

    return tf + title_bonus + depth_bonus + importance


def _extract_memory_ids(node: dict) -> list[int]:
    """Extract memory IDs from a node's title AND text."""
    combined = node.get("title", "") + " " + node.get("text", "")
    return [int(m) for m in re.findall(r"\[id=(\d+)\]", combined)]


def hierarchical_recall(
    tree: dict,
    query: str,
    memory_type: str | None = None,
    limit: int = 5,
) -> list[dict]:
    """
    PageIndex-style hierarchical recall:
    1. Score all nodes in the tree
    2. Prefer leaf nodes (actual memories) over section headers
    3. Filter by type section if requested
    4. Return top-k scored nodes with their ancestry context
    """
    query_tokens = set(_tokenize(query))
    if not query_tokens:
        return []

    flat = _flatten_tree(tree.get("structure", []))

    # Filter to the right type section if specified
    if memory_type:
        type_map = {
            "episodic":   "Episodic Memories",
            "semantic":   "Semantic Memories",
            "procedural": "Procedural Memories",
        }
        section_title = type_map.get(memory_type, "")
        # Find the section root and keep only its descendants
        in_section = False
        section_depth = None
        filtered = []
        for n in flat:
            if n["title"] == section_title and n["_depth"] == 1:
                in_section = True
                section_depth = n["_depth"]
                continue
            if in_section:
                if n["_depth"] <= section_depth:
                    break
                filtered.append(n)
        flat = filtered if filtered else flat

    # Score all nodes
    scored = []
    for node in flat:
        score = _score_node(node, query_tokens, node["_depth"])
        if score > 0:
            scored.append((score, node))

    # Sort by score descending
    scored.sort(key=lambda x: -x[0])

    # Build result records
    results = []
    seen_ids = set()
    for score, node in scored[:limit * 2]:  # over-fetch, deduplicate
        mem_ids = _extract_memory_ids(node)
        has_id_in_title = re.search(r"\[id=\d+\]", node.get("title", ""))
        # Skip pure section headers with no memory content
        if not mem_ids and not has_id_in_title and node["_depth"] < 2:
            continue
        key = node.get("node_id", node["title"])
        if key in seen_ids:
            continue
        seen_ids.add(key)
        results.append({
            "score":    round(score, 3),
            "depth":    node["_depth"],
            "title":    node["title"],
            "node_id":  node.get("node_id", ""),
            "text":     node.get("text", ""),
            "mem_ids":  mem_ids,
        })
        if len(results) >= limit:
            break

    return results


# ── Display ────────────────────────────────────────────────────────────────────

def print_tree(structure: list, indent: int = 0):
    for node in structure:
        prefix = "  " * indent + ("+- " if indent else "")
        print(f"{prefix}{node.get('title', '?')}  [{node.get('node_id','')}]")
        if node.get("nodes"):
            print_tree(node["nodes"], indent + 1)


def print_results(results: list[dict], query: str):
    if not results:
        print(f"No memories found for: {query!r}")
        return
    print(f"\n-- PageIndex Recall: '{query}' " + "-" * 40)
    print(f"   Found {len(results)} relevant memory section(s)\n")
    for r in results:
        bar = "#" * min(int(r["score"] * 2), 10)
        print(f"  [{r['node_id']}] {r['title']}")
        print(f"  Score: {r['score']:.3f} {bar}  Depth: {r['depth']}")
        if r["mem_ids"]:
            print(f"  Memory IDs: {r['mem_ids']}")
        # Print text excerpt (first 400 chars)
        excerpt = r["text"].strip()[:400].replace("\n", "\n    ")
        if excerpt:
            print(f"\n    {excerpt}")
            if len(r["text"]) > 400:
                print("    [...]")
        print()


# ── CLI ────────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="PageIndex-powered memory recall"
    )
    parser.add_argument("--query",      help="Search query")
    parser.add_argument("--type",       choices=["episodic", "semantic", "procedural"])
    parser.add_argument("--limit",      type=int, default=5)
    parser.add_argument("--rebuild",    action="store_true", help="Force rebuild tree index")
    parser.add_argument("--show-tree",  action="store_true", help="Display tree structure")
    args = parser.parse_args()

    tree = get_tree(force_rebuild=args.rebuild)

    if args.show_tree:
        print(f"\n-- Memory Tree: {tree['doc_name']} " + "-" * 40)
        print(f"   Nodes: {len(_flatten_tree(tree['structure']))}  |  Built: {tree.get('built_at','?')[:19]}\n")
        print_tree(tree["structure"])
        return

    if not args.query:
        parser.print_help()
        return

    results = hierarchical_recall(
        tree,
        query=args.query,
        memory_type=args.type,
        limit=args.limit,
    )
    print_results(results, args.query)


if __name__ == "__main__":
    main()
