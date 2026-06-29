"""
drawio_builder.py
=================
Programmatic builder for DHL-standard draw.io diagrams.

It composes nodes from (approved shape stencil) + (approved lifecycle colour)
and edges from (approved connector style) + (routing / jump / bidirectional
options). The output is valid diagrams.net XML.

NEW visual features over the original DHL pack
----------------------------------------------
1. Orthogonal routing        -> edgeStyle=orthogonalEdgeStyle (90-degree elbows,
                                 far fewer overlaps than straight lines).
2. Line jumps / gap arcs     -> jettySize + at the model level jumpStyle="arc"
                                 so a line that crosses another shows a small arc
                                 hop instead of an ambiguous intersection.
3. Bidirectional connectors  -> startArrow=block so one edge expresses a full
                                 request & response without two separate lines.
4. Waypoints                 -> optional explicit Array of points to hand-route
                                 a wire around a node.

Public API
----------
    d = Diagram(title="My Architecture")
    a = d.add_node("Order API", shape="service", color="new_target_solution")
    b = d.add_node("GCDB", shape="database", color="new_target_solution")
    d.connect(a, b, connector="query_response_new", label="getOrder",
              bidirectional=True)
    d.add_legend(["new_target_solution", "existing_decomm"],
                 ["query_response_new", "update_feed_target"])
    xml = d.to_xml()

CLI
---
    python drawio_builder.py spec.json out.drawio
where spec.json follows the schema documented in SKILL.md.
"""

from __future__ import annotations

import html
import json
import sys
from dataclasses import dataclass, field
from typing import Optional

import dhl_styles as S


# ---------------------------------------------------------------------------
# Node / Edge dataclasses
# ---------------------------------------------------------------------------

@dataclass
class Node:
    id: str
    label: str
    shape_key: str
    color_key: str
    x: int
    y: int
    w: int
    h: int
    parent: str = "1"


@dataclass
class Edge:
    id: str
    source: str
    target: str
    connector_key: str
    label: str = ""
    bidirectional: bool = False
    orthogonal: bool = True
    waypoints: list = field(default_factory=list)  # list of (x, y)
    exit_x: Optional[float] = None
    exit_y: Optional[float] = None
    entry_x: Optional[float] = None
    entry_y: Optional[float] = None


# ---------------------------------------------------------------------------
# Diagram
# ---------------------------------------------------------------------------

class Diagram:
    def __init__(self, title: str = "Solution Architecture",
                 page_w: int = 1654, page_h: int = 1169):
        self.title = title
        self.page_w = page_w
        self.page_h = page_h
        self.nodes: list[Node] = []
        self.edges: list[Edge] = []
        self._auto = 0
        self._extra_cells: list[str] = []  # raw cells (legend chips etc.)

    # -- id helper -----------------------------------------------------------
    def _next_id(self, prefix="n") -> str:
        self._auto += 1
        return f"{prefix}{self._auto}"

    # -- node ----------------------------------------------------------------
    def add_node(self, label: str, shape: str, color: str,
                 x: int = 0, y: int = 0,
                 w: Optional[int] = None, h: Optional[int] = None,
                 parent: str = "1", node_id: Optional[str] = None) -> str:
        shape_key = S.resolve_shape(shape)
        color_key = S.resolve_color(color)
        dw, dh = S.SHAPES[shape_key]["default_geometry"]
        node = Node(
            id=node_id or self._next_id("node_"),
            label=label, shape_key=shape_key, color_key=color_key,
            x=x, y=y, w=w or dw, h=h or dh, parent=parent,
        )
        self.nodes.append(node)
        return node.id

    # -- edge ----------------------------------------------------------------
    def connect(self, source: str, target: str, connector: str,
                label: str = "", bidirectional: bool = False,
                orthogonal: bool = True, waypoints: Optional[list] = None,
                exit_point: Optional[tuple] = None,
                entry_point: Optional[tuple] = None) -> str:
        connector_key = S.resolve_connector(connector)
        edge = Edge(
            id=self._next_id("edge_"),
            source=source, target=target, connector_key=connector_key,
            label=label, bidirectional=bidirectional, orthogonal=orthogonal,
            waypoints=waypoints or [],
            exit_x=exit_point[0] if exit_point else None,
            exit_y=exit_point[1] if exit_point else None,
            entry_x=entry_point[0] if entry_point else None,
            entry_y=entry_point[1] if entry_point else None,
        )
        self.edges.append(edge)
        return edge.id

    # -- style composition ---------------------------------------------------
    @staticmethod
    def _node_style(node: Node) -> str:
        shape = S.SHAPES[node.shape_key]
        color = S.COLORS[node.color_key]
        if shape["is_image"]:
            # Actor is a PNG; colour can't be injected. Returned as-is.
            return shape["style"]
        return shape["style"].format(
            fill=color["fill"], grad=color["grad"], stroke=color["stroke"]
        )

    @staticmethod
    def _edge_style(edge: Edge) -> str:
        c = S.CONNECTORS[edge.connector_key]
        parts = []
        # Routing: orthogonal elbows reduce overlaps.
        if edge.orthogonal:
            parts.append("edgeStyle=orthogonalEdgeStyle")
            parts.append("rounded=1")        # rounded elbows read cleaner
            parts.append("jettySize=auto")
        else:
            parts.append("edgeStyle=none")
            parts.append("rounded=0")
        parts.append("orthogonalLoop=1")
        # Arrowheads: bidirectional = request & response on one wire.
        if edge.bidirectional:
            parts.append("startArrow=block")
        else:
            parts.append("startArrow=none")
        parts.append("endArrow=block")
        parts.append("startSize=5")
        parts.append("endSize=5")
        parts.append("strokeWidth=2")
        parts.append(f"strokeColor={c['stroke']}")
        if c["dashed"]:
            parts.append("dashed=1")
            parts.append("dashPattern=2.00 2.00")
        parts.append("html=1")
        parts.append("labelBackgroundColor=#ffffff")
        parts.append("spacingTop=0;spacingBottom=0;spacingLeft=0;spacingRight=0")
        parts.append("verticalAlign=middle")
        # Fixed exit / entry connection ports if provided.
        if edge.exit_x is not None:
            parts.append(f"exitX={edge.exit_x};exitY={edge.exit_y};exitDx=0;exitDy=0")
        if edge.entry_x is not None:
            parts.append(f"entryX={edge.entry_x};entryY={edge.entry_y};entryDx=0;entryDy=0")
        return ";".join(parts) + ";"

    # -- legend --------------------------------------------------------------
    def add_legend(self, color_keys: Optional[list] = None,
                   connector_keys: Optional[list] = None,
                   x: Optional[int] = None, y: int = 40):
        """Render the legend.

        The legend is a reference key, so it ALWAYS shows the full DHL catalogue —
        every lifecycle colour and every connector — regardless of what this
        particular diagram uses. The color_keys / connector_keys arguments are
        accepted for backwards compatibility but ignored; the legend is complete by
        design.
        """
        color_keys = list(S.COLORS.keys())          # full catalogue, always
        connector_keys = list(S.CONNECTORS.keys())   # full catalogue, always
        rows = len(color_keys) + len(connector_keys) + 2  # +2 section headers
        box_w, row_h = 300, 22
        box_h = rows * row_h + 20
        if x is None:
            x = self.page_w - box_w - 40
        cid = self._next_id("legend_")
        self._extra_cells.append(
            f'<mxCell id="{cid}" value="DHL LEGEND — full reference" '
            f'style="{S.LEGEND_OUTER}" vertex="1" parent="1">'
            f'<mxGeometry x="{x}" y="{y}" width="{box_w}" height="{box_h}" as="geometry"/></mxCell>'
        )
        cursor = y + 26
        # Colour swatches
        self._legend_header(cid, "Lifecycle", x + 8, cursor); cursor += row_h
        for k in color_keys:
            c = S.COLORS[k]
            sw = self._next_id("lc_")
            self._extra_cells.append(
                f'<mxCell id="{sw}" value="" style="rounded=0;whiteSpace=wrap;html=1;'
                f'fillColor={c["fill"]};gradientColor={c["grad"]};strokeColor={c["stroke"]};shadow=1;" '
                f'vertex="1" parent="1"><mxGeometry x="{x+12}" y="{cursor+3}" '
                f'width="26" height="14" as="geometry"/></mxCell>'
            )
            tx = self._next_id("lt_")
            self._extra_cells.append(
                f'<mxCell id="{tx}" value="{html.escape(c["label"])}" '
                f'style="text;html=1;align=left;verticalAlign=middle;fontSize=10;" '
                f'vertex="1" parent="1"><mxGeometry x="{x+46}" y="{cursor}" '
                f'width="{box_w-54}" height="{row_h}" as="geometry"/></mxCell>'
            )
            cursor += row_h
        # Connector lines
        self._legend_header(cid, "Messages", x + 8, cursor); cursor += row_h
        for k in connector_keys:
            c = S.CONNECTORS[k]
            ln = self._next_id("ll_")
            dash = "dashed=1;dashPattern=2.00 2.00;" if c["dashed"] else ""
            self._extra_cells.append(
                f'<mxCell id="{ln}" value="" style="endArrow=block;html=1;strokeWidth=2;'
                f'strokeColor={c["stroke"]};{dash}" edge="1" parent="1">'
                f'<mxGeometry relative="1" as="geometry">'
                f'<mxPoint x="{x+12}" y="{cursor+10}" as="sourcePoint"/>'
                f'<mxPoint x="{x+40}" y="{cursor+10}" as="targetPoint"/></mxGeometry></mxCell>'
            )
            tx = self._next_id("lt_")
            self._extra_cells.append(
                f'<mxCell id="{tx}" value="{html.escape(c["label"])}" '
                f'style="text;html=1;align=left;verticalAlign=middle;fontSize=10;" '
                f'vertex="1" parent="1"><mxGeometry x="{x+46}" y="{cursor}" '
                f'width="{box_w-54}" height="{row_h}" as="geometry"/></mxCell>'
            )
            cursor += row_h

    def _legend_header(self, parent, text, x, y):
        hid = self._next_id("lh_")
        self._extra_cells.append(
            f'<mxCell id="{hid}" value="{html.escape(text)}" '
            f'style="text;html=1;align=left;verticalAlign=middle;fontSize=10;fontStyle=1;fontColor=#666666;" '
            f'vertex="1" parent="1"><mxGeometry x="{x}" y="{y}" width="200" height="20" as="geometry"/></mxCell>'
        )

    # -- XML emit ------------------------------------------------------------
    def _node_xml(self, node: Node) -> str:
        style = html.escape(self._node_style(node), quote=True)
        label = html.escape(node.label, quote=True)
        return (
            f'<mxCell id="{node.id}" value="{label}" style="{style}" '
            f'vertex="1" parent="{node.parent}">'
            f'<mxGeometry x="{node.x}" y="{node.y}" width="{node.w}" '
            f'height="{node.h}" as="geometry"/></mxCell>'
        )

    def _edge_xml(self, edge: Edge) -> str:
        style = html.escape(self._edge_style(edge), quote=True)
        label = html.escape(edge.label, quote=True)
        geo = '<mxGeometry relative="1" as="geometry">'
        if edge.waypoints:
            pts = "".join(
                f'<mxPoint x="{px}" y="{py}"/>' for px, py in edge.waypoints
            )
            geo += f'<Array as="points">{pts}</Array>'
        geo += "</mxGeometry>"
        return (
            f'<mxCell id="{edge.id}" value="{label}" style="{style}" '
            f'edge="1" parent="1" source="{edge.source}" target="{edge.target}">'
            f'{geo}</mxCell>'
        )

    def to_xml(self) -> str:
        cells = [self._node_xml(n) for n in self.nodes]
        cells += [self._edge_xml(e) for e in self.edges]
        cells += self._extra_cells
        body = "\n        ".join(cells)
        # jumpStyle="arc" + jumpSize render the line-gap arcs at crossings.
        return (
            '<?xml version="1.0" encoding="UTF-8"?>\n'
            '<mxfile host="app.diagrams.net">\n'
            f'  <diagram name="{html.escape(self.title)}" id="dhl-arch">\n'
            f'    <mxGraphModel dx="900" dy="600" grid="1" gridSize="10" guides="1" '
            f'tooltips="1" connect="1" arrows="1" fold="1" page="1" pageScale="1" '
            f'pageWidth="{self.page_w}" pageHeight="{self.page_h}" math="0" shadow="0" '
            f'jumpStyle="arc" jumpSize="8">\n'
            '      <root>\n'
            '        <mxCell id="0"/>\n'
            '        <mxCell id="1" parent="0"/>\n'
            f'        {body}\n'
            '      </root>\n'
            '    </mxGraphModel>\n'
            '  </diagram>\n'
            '</mxfile>\n'
        )


# ---------------------------------------------------------------------------
# Auto-layout: simple layered left-to-right placement when x/y omitted.
# ---------------------------------------------------------------------------

def auto_layout(diagram: Diagram, layer_of: dict, col_gap=240, row_gap=140,
                origin=(60, 80)):
    """Assign x/y to nodes based on an integer layer per node id.

    layer_of: {node_id: layer_index}. Nodes in the same layer stack vertically.
    """
    from collections import defaultdict
    cols = defaultdict(list)
    for n in diagram.nodes:
        cols[layer_of.get(n.id, 0)].append(n)
    ox, oy = origin
    for layer, nodes in sorted(cols.items()):
        for row, n in enumerate(nodes):
            n.x = ox + layer * col_gap
            n.y = oy + row * row_gap


# ---------------------------------------------------------------------------
# JSON spec -> Diagram  (CLI entry)
# ---------------------------------------------------------------------------

def build_from_spec(spec: dict) -> Diagram:
    d = Diagram(title=spec.get("title", "Solution Architecture"),
                page_w=spec.get("page_w", 1654),
                page_h=spec.get("page_h", 1169))
    id_map = {}
    for nd in spec["nodes"]:
        nid = d.add_node(
            label=nd["label"], shape=nd["shape"], color=nd["color"],
            x=nd.get("x", 0), y=nd.get("y", 0),
            w=nd.get("w"), h=nd.get("h"),
            node_id=nd.get("id"),
        )
        id_map[nd.get("id", nid)] = nid
    # auto layout if any node lacks coordinates
    if any("x" not in nd for nd in spec["nodes"]) and "layers" in spec:
        layer_of = {id_map[k]: v for k, v in spec["layers"].items()}
        auto_layout(d, layer_of)
    for ed in spec.get("edges", []):
        d.connect(
            source=id_map.get(ed["source"], ed["source"]),
            target=id_map.get(ed["target"], ed["target"]),
            connector=ed["connector"],
            label=ed.get("label", ""),
            bidirectional=ed.get("bidirectional", False),
            orthogonal=ed.get("orthogonal", True),
            waypoints=[tuple(p) for p in ed.get("waypoints", [])],
            exit_point=tuple(ed["exit_point"]) if "exit_point" in ed else None,
            entry_point=tuple(ed["entry_point"]) if "entry_point" in ed else None,
        )
    legend = spec.get("legend")
    if legend:
        # Legend always renders the full DHL catalogue; any colours/connectors in
        # the spec are ignored. Accept legend as either `true` or an object.
        d.add_legend()
    return d


def main(argv):
    if len(argv) < 3:
        print("usage: python drawio_builder.py <spec.json> <out.drawio>")
        return 1
    with open(argv[1]) as f:
        spec = json.load(f)
    d = build_from_spec(spec)
    with open(argv[2], "w") as f:
        f.write(d.to_xml())
    print(f"Wrote {argv[2]} ({len(d.nodes)} nodes, {len(d.edges)} edges)")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
