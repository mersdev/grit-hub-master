"""
validate_mermaid.py
===================
Validates a Mermaid diagram against (a) Mermaid syntax and (b) the DHL colour /
connector standard.

Two layers:

SYNTAX
  - If the Mermaid CLI (`mmdc`, from @mermaid-js/mermaid-cli) is installed, the
    file is rendered to a throwaway SVG; any parse error is reported. This is the
    authoritative check.
  - If `mmdc` is not available, a structural fallback runs: known header, balanced
    subgraph/end, balanced brackets, non-empty body. The fallback prints a note
    that it is heuristic, not a full parse.

DHL COMPLIANCE
  - Every `classDef` fill is an approved lifecycle colour.
  - Every `linkStyle` stroke is an approved connector colour.
  - Warns if a flowchart/state diagram declares nodes but assigns no classes
    (i.e. lifecycle colour missing).
  - Warns if hard-coded hex colours appear that are not in the approved palette.

Usage:  python validate_mermaid.py file.mmd
Exit 0 = pass, 1 = errors.
"""

from __future__ import annotations

import os
import re
import shutil
import subprocess
import sys
import tempfile

import mermaid_styles as S

APPROVED_FILLS = {c["fill"].lower() for c in S.COLORS.values()}
APPROVED_STROKES = {c["stroke"].lower() for c in S.COLORS.values()} | \
                   {c["stroke"].lower() for c in S.CONNECTORS.values()}
KNOWN_HEADERS = ("flowchart", "graph", "sequenceDiagram", "stateDiagram",
                 "stateDiagram-v2", "erDiagram", "C4Context", "C4Container",
                 "C4Component")


def _strip_frontmatter(text: str) -> str:
    # remove --- title: ... --- front matter for header detection
    if text.lstrip().startswith("---"):
        parts = text.split("---", 2)
        if len(parts) == 3:
            return parts[2]
    return text


def _node_parse(path: str):
    """Try authoritative grammar validation via mmparse.mjs (mermaid.parse + jsdom).

    Returns (ok, message, authoritative) or None if unavailable.
    """
    node = shutil.which("node")
    helper = os.path.join(os.path.dirname(os.path.abspath(__file__)), "mmparse.mjs")
    if not node or not os.path.exists(helper):
        return None
    try:
        res = subprocess.run([node, helper, path],
                             capture_output=True, text=True, timeout=60)
    except subprocess.TimeoutExpired:
        return None
    out = (res.stdout or "").strip()
    if out.startswith("PARSE_OK"):
        return True, "mermaid.parse() accepted the diagram (authoritative)", True
    if out.startswith("PARSE_ERROR:"):
        return False, out, True
    # PARSE_UNAVAILABLE -> deps missing, not a verdict
    return None


def syntax_check(path: str):
    """Return (ok, messages, authoritative).

    Order of preference:
      1. node + mmparse.mjs  (mermaid.parse, authoritative, no browser)
      2. mmdc                 (renders; authoritative if a browser is present)
      3. heuristic            (structural, parser-free)
    """
    np = _node_parse(path)
    if np is not None:
        ok, msg, auth = np
        return ok, [msg], auth

    mmdc = shutil.which("mmdc")
    if mmdc:
        with tempfile.TemporaryDirectory() as tmp:
            out_svg = os.path.join(tmp, "out.svg")
            try:
                res = subprocess.run(
                    [mmdc, "-i", path, "-o", out_svg],
                    capture_output=True, text=True, timeout=60,
                )
            except subprocess.TimeoutExpired:
                # browser hang -> not a syntax verdict; fall back to heuristic
                return _heuristic(path, ["mmdc timed out launching a browser"])
            if res.returncode == 0:
                return True, ["mmdc parsed and rendered OK"], True
            blob = ((res.stderr or "") + (res.stdout or "")).lower()
            # Environment problems (no Chromium / puppeteer) are NOT parse errors.
            env_markers = ("could not find", "puppeteer", "chrome", "chromium",
                           "browser was not found", "executablepath", "cache path",
                           "launch", "enoent")
            if any(m in blob for m in env_markers):
                return _heuristic(
                    path, ["mmdc present but no browser available "
                           "(environment issue, not a syntax error) — "
                           "running heuristic check"])
            err = (res.stderr or res.stdout or "").strip()
            last = err.splitlines()[-1] if err else "unknown"
            return False, [f"mmdc parse error: {last}"], True

    # ---- fallback heuristic ----
    return _heuristic(path, ["(mmdc not installed — running heuristic structural check only)"])


def _heuristic(path: str, msgs: list):
    """Structural, parser-free validation. Returns (ok, messages, authoritative=False)."""
    with open(path) as f:
        text = f.read()
    body = _strip_frontmatter(text).strip()
    if not body:
        return False, msgs + ["empty diagram body"], False
    header = body.splitlines()[0].strip()
    if not header.startswith(KNOWN_HEADERS):
        return False, msgs + [f"unknown diagram header: '{header}'"], False
    # balanced subgraph / end
    n_sub = len(re.findall(r"^\s*subgraph\b", body, re.M))
    n_end = len(re.findall(r"^\s*end\b", body, re.M))
    if n_sub != n_end:
        return False, msgs + [f"unbalanced subgraph/end ({n_sub} subgraph, {n_end} end)"], False
    # Bracket-balance only makes sense for flowcharts, and only after we strip
    # quoted labels and arrow tokens (--), <--, ==>, {{ }}, etc. that legitimately
    # contain bracket characters in sequence/ER/state syntax.
    if header.startswith(("flowchart", "graph")):
        scrubbed = re.sub(r'"[^"]*"', "", body)        # drop quoted labels
        scrubbed = re.sub(r"\|[^|]*\|", "", scrubbed)   # drop |edge labels|
        for op, cl in [("[", "]"), ("(", ")"), ("{", "}")]:
            if scrubbed.count(op) != scrubbed.count(cl):
                msgs.append(f"unbalanced '{op}{cl}' ({scrubbed.count(op)} vs {scrubbed.count(cl)})")
    ok = not any(m.startswith("unbalanced '") for m in msgs)
    return ok, msgs, False


def dhl_check(path: str):
    errors, warnings = [], []
    with open(path) as f:
        text = f.read()
    body = _strip_frontmatter(text)

    # classDef fills
    for m in re.finditer(r"classDef\s+\w+\s+([^;]+);?", body):
        decl = m.group(1)
        fm = re.search(r"fill:\s*(#[0-9a-fA-F]{3,6})", decl)
        if fm and fm.group(1).lower() not in APPROVED_FILLS:
            errors.append(f"classDef fill {fm.group(1)} is not an approved lifecycle colour")

    # linkStyle strokes
    for m in re.finditer(r"linkStyle\s+[\d,\s]+\s+([^;]+);?", body):
        sm = re.search(r"stroke:\s*(#[0-9a-fA-F]{3,6})", m.group(1))
        if sm and sm.group(1).lower() not in APPROVED_STROKES:
            errors.append(f"linkStyle stroke {sm.group(1)} is not an approved connector colour")

    # any other hard-coded hex (style ... fill:) not approved
    for m in re.finditer(r"style\s+\w+\s+([^;]+);?", body):
        fm = re.search(r"fill:\s*(#[0-9a-fA-F]{3,6})", m.group(1))
        if fm and fm.group(1).lower() not in APPROVED_FILLS:
            warnings.append(f"inline style fill {fm.group(1)} is not an approved colour")

    header = body.strip().splitlines()[0].strip() if body.strip() else ""
    if header.startswith(("flowchart", "graph")):
        has_nodes = bool(re.search(r"\w+\s*[\[({]", body))
        has_class = "class " in body or "classDef" in body
        if has_nodes and not has_class:
            warnings.append("flowchart declares nodes but assigns no lifecycle class "
                            "(DHL colour scheme missing)")
    return errors, warnings


def main(argv):
    args = [a for a in argv[1:] if not a.startswith("--")]
    flags = {a for a in argv[1:] if a.startswith("--")}
    if not args:
        print("usage: python validate_mermaid.py [--plain] <file.mmd>")
        print("       --plain : syntax-only; skip DHL colour compliance "
              "(use for non-DHL types like gantt, pie, mindmap, kanban)")
        return 1
    path = args[0]
    ok, msgs, authoritative = syntax_check(path)
    for m in msgs:
        print(("OK: " if ok else "SYNTAX: ") + m)

    plain = "--plain" in flags
    if plain:
        errors, warnings = [], []
        print("NOTE: --plain set; DHL colour compliance skipped (non-DHL diagram).")
    else:
        errors, warnings = dhl_check(path)
    for w in warnings:
        print(f"WARN: {w}")
    for e in errors:
        print(f"ERROR: {e}")
    failed = (not ok) or bool(errors)
    label = "authoritative" if authoritative else "heuristic"
    if failed:
        print(f"\nFAILED ({label} syntax). {len(errors)} DHL error(s), "
              f"{len(warnings)} warning(s).")
        return 1
    print(f"\nPASSED ({label} syntax). 0 errors, {len(warnings)} warning(s).")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
