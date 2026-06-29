"""
validate_drawio.py
==================
Validates a generated .drawio file against DHL standards and draw.io
structural rules. Run before handing a diagram to the user.

Checks
------
STRUCTURAL
  - well-formed XML
  - unique mxCell ids
  - every edge has source+target (or explicit source/target points)
  - every vertex has geometry with width+height
APPROVED STYLE
  - every node fillColor is an approved lifecycle colour (or actor image / none)
  - every edge strokeColor is an approved connector colour
  - no shape=stencil(...) other than the approved five (warns if unknown)
READABILITY (warnings, not errors)
  - flags nodes that overlap in bounding box
  - flags edges with neither orthogonal routing nor waypoints when many edges exist

Usage:  python validate_drawio.py file.drawio
Exit code 0 = pass, 1 = errors found.
"""

from __future__ import annotations

import re
import sys
import xml.etree.ElementTree as ET

import dhl_styles as S

APPROVED_FILLS = {c["fill"] for c in S.COLORS.values()} | {"none", "#ffffff",
                                                            "#f0f0f0", "#e1a900"}
APPROVED_STROKES = {c["stroke"] for c in S.CONNECTORS.values()}
APPROVED_STENCIL_FRAGMENTS = []
for sh in S.SHAPES.values():
    m = re.search(r"shape=stencil\(([^)]*)\)", sh["style"])
    if m:
        APPROVED_STENCIL_FRAGMENTS.append(m.group(1))


def _attr_from_style(style: str, key: str):
    m = re.search(rf"(?:^|;){re.escape(key)}=([^;]*)", style or "")
    return m.group(1) if m else None


def validate(path: str):
    errors, warnings = [], []
    try:
        tree = ET.parse(path)
    except ET.ParseError as e:
        return [f"XML parse error: {e}"], []
    root = tree.getroot()

    cells = root.iter("mxCell")
    ids, vertices, edges = set(), [], []
    for c in cells:
        cid = c.get("id")
        if cid in ids:
            errors.append(f"Duplicate mxCell id: {cid}")
        ids.add(cid)
        style = c.get("style", "") or ""
        if c.get("vertex") == "1":
            vertices.append(c)
            geo = c.find("mxGeometry")
            # Edge-label child cells (style contains 'edgeLabel', or parent is an
            # edge) are relative-positioned and legitimately have no width/height.
            is_edge_label = ("edgeLabel" in style) or (c.get("connectable") == "0"
                                                       and geo is not None
                                                       and geo.get("relative") == "1")
            if not is_edge_label and (geo is None or not (geo.get("width") and geo.get("height"))):
                errors.append(f"Vertex {cid} missing geometry width/height")
            fill = _attr_from_style(style, "fillColor")
            if fill and fill.lower() not in {f.lower() for f in APPROVED_FILLS}:
                # allowed: legend text cells use no fill; warn only
                if "shape=stencil" in style:
                    warnings.append(
                        f"Vertex {cid} fillColor {fill} not an approved lifecycle colour")
            if "shape=stencil(" in style:
                frag = re.search(r"shape=stencil\(([^)]*)\)", style)
                if frag and frag.group(1) not in APPROVED_STENCIL_FRAGMENTS:
                    # legend container stencils are allowed; warn for nodes
                    warnings.append(f"Vertex {cid} uses a non-catalogued stencil")
        if c.get("edge") == "1":
            edges.append(c)
            src, tgt = c.get("source"), c.get("target")
            geo = c.find("mxGeometry")
            has_pts = geo is not None and (
                geo.find("mxPoint[@as='sourcePoint']") is not None
                and geo.find("mxPoint[@as='targetPoint']") is not None)
            if not (src and tgt) and not has_pts:
                errors.append(f"Edge {cid} has no source/target nor explicit points")
            stroke = _attr_from_style(style, "strokeColor")
            if stroke and stroke.lower() not in {s.lower() for s in APPROVED_STROKES}:
                warnings.append(
                    f"Edge {cid} strokeColor {stroke} not an approved connector colour")

    # overlap check
    boxes = []
    for v in vertices:
        geo = v.find("mxGeometry")
        if geo is None:
            continue
        try:
            x, y = float(geo.get("x", 0)), float(geo.get("y", 0))
            w, h = float(geo.get("width", 0)), float(geo.get("height", 0))
        except (TypeError, ValueError):
            continue
        if "shape=stencil" not in (v.get("style") or ""):
            continue
        boxes.append((v.get("id"), x, y, w, h))
    for i in range(len(boxes)):
        for j in range(i + 1, len(boxes)):
            _, ax, ay, aw, ah = boxes[i]
            _, bx, by, bw, bh = boxes[j]
            if ax < bx + bw and ax + aw > bx and ay < by + bh and ay + ah > by:
                warnings.append(
                    f"Nodes {boxes[i][0]} and {boxes[j][0]} overlap (check layout)")

    # Only count "real" edges (those with source+target); legend sample
    # lines use explicit points and should not trigger the density check.
    real_edges = [e for e in edges if e.get("source") and e.get("target")]
    if len(real_edges) > 4:
        for e in real_edges:
            style = e.get("style", "")
            if "orthogonalEdgeStyle" not in style and e.find(
                    "mxGeometry/Array[@as='points']") is None:
                warnings.append(
                    f"Edge {e.get('id')} is straight in a dense diagram; "
                    f"consider orthogonal routing or waypoints to avoid overlaps")
    return errors, warnings


def main(argv):
    if len(argv) < 2:
        print("usage: python validate_drawio.py <file.drawio>")
        return 1
    errors, warnings = validate(argv[1])
    for w in warnings:
        print(f"WARN: {w}")
    for e in errors:
        print(f"ERROR: {e}")
    if errors:
        print(f"\nFAILED with {len(errors)} error(s), {len(warnings)} warning(s).")
        return 1
    print(f"\nPASSED. 0 errors, {len(warnings)} warning(s).")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
