"""
mermaid_builder.py
==================
Builds DHL-standard Mermaid diagrams from a JSON spec or a Python API.

Supported types: flowchart, sequence, state, er, c4.

Lifecycle colour is applied via classDef (flowchart, state). Connector meaning is
applied via Mermaid link syntax (solid/dotted/thick, bidirectional) plus a
linkStyle colour that matches the draw.io connector catalogue.

Public API
----------
    b = FlowchartBuilder("Integration – Target State", direction="LR")
    b.node("web", "Web Portal", shape="application", color="existing_to_change")
    b.node("gcdb", "GCDB", shape="database", color="new_target_solution")
    b.edge("web", "gcdb", connector="query_response_new", label="read/write",
           bidirectional=True)
    b.subgraph("Target", ["gcdb"])
    b.legend()                       # appends a colour/connector legend subgraph
    print(b.render())

CLI
---
    python mermaid_builder.py spec.json out.mmd
"""

from __future__ import annotations

import json
import sys

import mermaid_styles as S


# ===========================================================================
# FLOWCHART
# ===========================================================================

class FlowchartBuilder:
    def __init__(self, title: str = "", direction: str = "LR"):
        self.title = title
        self.direction = direction
        self._nodes = []          # (id, label, shape_key, color_key)
        self._edges = []          # dict
        self._subgraphs = []      # (name, [node_ids])
        self._want_legend = False

    def node(self, node_id, label, shape, color):
        self._nodes.append((node_id, label,
                            S.resolve_shape(shape), S.resolve_color(color)))
        return node_id

    def edge(self, source, target, connector, label="", bidirectional=False):
        ck = S.resolve_connector(connector)
        if bidirectional and not S.CONNECTORS[ck]["bidir_ok"]:
            bidirectional = False  # only query/response connectors are bidir
        self._edges.append(dict(source=source, target=target, ck=ck,
                                label=label, bidir=bidirectional))

    def subgraph(self, name, node_ids):
        self._subgraphs.append((name, list(node_ids)))

    def legend(self):
        self._want_legend = True

    # -- rendering -----------------------------------------------------------
    @staticmethod
    def _wrap(shape_key, label):
        o = S.SHAPES[shape_key]["open"]
        c = S.SHAPES[shape_key]["close"]
        safe = label.replace('"', "'")
        return f'{o}"{safe}"{c}'

    def _edge_arrow(self, e):
        """Return the arrow token between source and target.

        Uses the canonical Mermaid forms verified against the official syntax docs
        and the mermaid parser:
          solid    one-way:  -->        labelled: -->|text|
          dotted   one-way:  -.->       labelled: -.->|text|
          thick    one-way:  ==>        labelled: ==>|text|
          solid    bidir:    <-->       labelled: <-->|text|
          dotted   bidir:    <-.->      labelled: <-.->|text|
          thick    bidir:    <==>       labelled: <==>|text|
        The |text| form is preferred over `-- text -->` because it is unambiguous
        and never breaks on labels containing spaces or reserved words.
        """
        line = S.CONNECTORS[e["ck"]]["line"]
        bidir = e["bidir"]
        lbl = (e["label"] or "").replace("|", "/")  # pipe is the label delimiter

        if line == "dotted":
            arrow = "<-.->" if bidir else "-.->"
        elif line == "thick":
            arrow = "<==>" if bidir else "==>"
        else:  # solid
            arrow = "<-->" if bidir else "-->"

        if lbl:
            return f"{arrow}|{lbl}| "
        return arrow + " "


    def render(self):
        lines = []
        if self.title:
            lines.append("---")
            lines.append(f"title: {self.title}")
            lines.append("---")
        lines.append(f"flowchart {self.direction}")

        sub_members = {nid for _, ids in self._subgraphs for nid in ids}

        # nodes not in any subgraph
        for nid, label, sk, ck in self._nodes:
            if nid not in sub_members:
                lines.append(f"    {nid}{self._wrap(sk, label)}")

        # subgraphs
        node_by_id = {n[0]: n for n in self._nodes}
        for name, ids in self._subgraphs:
            lines.append(f'    subgraph {name.replace(" ", "_")}["{name}"]')
            for nid in ids:
                if nid in node_by_id:
                    _, label, sk, ck = node_by_id[nid]
                    lines.append(f"        {nid}{self._wrap(sk, label)}")
            lines.append("    end")

        # edges (record order so linkStyle indices line up)
        for e in self._edges:
            lines.append(f"    {e['source']} {self._edge_arrow(e)}{e['target']}")

        # classDef blocks. Normally only for colours actually used; but when a
        # full legend is requested every lifecycle class must be defined so the
        # legend swatches can reference them.
        used_colors = {ck for _, _, _, ck in self._nodes}
        emit_colors = set(S.COLORS) if self._want_legend else used_colors
        for ck in S.COLORS:
            if ck in emit_colors:
                lines.append(f"    {S.classdef_line(ck)}")

        # class assignments
        for nid, _, _, ck in self._nodes:
            lines.append(f"    class {nid} {S.CLASS_NAMES[ck]};")

        # linkStyle colours per edge (index = edge order)
        for i, e in enumerate(self._edges):
            stroke = S.CONNECTORS[e["ck"]]["stroke"]
            lines.append(f"    linkStyle {i} stroke:{stroke},stroke-width:2px;")

        if self._want_legend:
            legend_lines, legend_link_styles = self._legend_lines(base_index=len(self._edges))
            lines.extend(legend_lines)
            lines.extend(legend_link_styles)

        return "\n".join(lines)

    def _legend_lines(self, base_index):
        """Render the FULL DHL catalogue legend — every lifecycle colour and every
        connector — regardless of what this diagram uses. The legend is a reference
        key, so it must always be complete.

        Returns (body_lines, link_style_lines). The connector swatch edges are
        declared after the diagram's own edges, so their linkStyle indices start at
        base_index (= number of real edges) to avoid recolouring real edges.
        """
        out = ['    subgraph LEGEND["DHL Legend — full reference"]',
               "        direction TB"]
        # Lifecycle colours: one swatch node per colour, all of them.
        out.append('        subgraph LEG_LIFECYCLE["Lifecycle"]')
        out.append("            direction TB")
        for ck in S.COLORS:
            out.append(f'            leg_{ck}["{S.COLORS[ck]["label"]}"]')
        out.append("        end")
        # Connectors: a tiny edge per connector, all nine, styled to match.
        out.append('        subgraph LEG_CONNECTORS["Messages"]')
        out.append("            direction LR")
        link_styles = []
        idx = base_index
        for ck in S.CONNECTORS:
            a, b = f"lc_{ck}_a", f"lc_{ck}_b"
            cc = S.CONNECTORS[ck]
            line = cc["line"]
            arrow = "-.->" if line == "dotted" else ("==>" if line == "thick" else "-->")
            # Declare both endpoints inline on the edge line: a small dot source
            # and a labelled target. Mermaid creates the nodes from this one line.
            out.append(f'            {a}(("&nbsp;")) {arrow} {b}["{cc["label"]}"]')
            link_styles.append(f"    linkStyle {idx} stroke:{cc['stroke']},stroke-width:2px;")
            idx += 1
        out.append("        end")
        out.append("    end")
        # colour the legend swatch nodes
        for ck in S.COLORS:
            out.append(f"    class leg_{ck} {S.CLASS_NAMES[ck]};")
        return out, link_styles


# ===========================================================================
# SEQUENCE
# ===========================================================================

class SequenceBuilder:
    """Maps DHL connectors to sequence arrows:
        solid request   ->  ->>
        dotted/target    ->  --) (async/future)
        response         ->  -->>
        bidirectional    ->  request ->> then response -->>
    """
    def __init__(self, title=""):
        self.title = title
        self._participants = []   # (id, label, kind)
        self._messages = []       # dict

    def participant(self, pid, label=None, actor=False):
        self._participants.append((pid, label or pid, actor))
        return pid

    def message(self, source, target, connector, label="", bidirectional=False):
        ck = S.resolve_connector(connector)
        self._messages.append(dict(source=source, target=target, ck=ck,
                                   label=label, bidir=bidirectional))

    def note(self, text, over):
        self._messages.append(dict(note=text, over=over))

    def render(self):
        lines = []
        if self.title:
            lines += ["---", f"title: {self.title}", "---"]
        lines.append("sequenceDiagram")
        lines.append("    autonumber")
        for pid, label, actor in self._participants:
            kw = "actor" if actor else "participant"
            lines.append(f'    {kw} {pid} as {label}')
        for m in self._messages:
            if "note" in m:
                lines.append(f'    Note over {m["over"]}: {m["note"]}')
                continue
            ck = m["ck"]
            line = S.CONNECTORS[ck]["line"]
            lbl = m["label"] or S.CONNECTORS[ck]["label"]
            if m["bidir"]:
                # Native bidirectional arrowheads (mermaid v11+):
                #   solid  <<->>   dotted  <<-->>
                arrow = "<<-->>" if line == "dotted" else "<<->>"
                lines.append(f'    {m["source"]}{arrow}{m["target"]}: {lbl}')
            else:
                if ck == "response":
                    arrow = "-->>"
                elif line == "dotted":
                    arrow = "--)"        # async / future (open arrowhead)
                else:
                    arrow = "->>"
                lines.append(f'    {m["source"]}{arrow}{m["target"]}: {lbl}')
        return "\n".join(lines)


# ===========================================================================
# STATE
# ===========================================================================

class StateBuilder:
    def __init__(self, title=""):
        self.title = title
        self._states = []     # (id, label, color_key|None)
        self._transitions = []  # (src, tgt, label)

    def state(self, sid, label=None, color=None):
        self._states.append((sid, label, S.resolve_color(color) if color else None))
        return sid

    def transition(self, src, tgt, label=""):
        self._transitions.append((src, tgt, label))

    def render(self):
        lines = []
        if self.title:
            lines += ["---", f"title: {self.title}", "---"]
        lines.append("stateDiagram-v2")
        for sid, label, ck in self._states:
            if label:
                lines.append(f'    {sid} : {label}')
        for src, tgt, label in self._transitions:
            if label:
                lines.append(f'    {src} --> {tgt} : {label}')
            else:
                lines.append(f'    {src} --> {tgt}')
        used = {ck for _, _, ck in self._states if ck}
        for ck in S.COLORS:
            if ck in used:
                lines.append(f"    {S.classdef_line(ck)}")
        for sid, _, ck in self._states:
            if ck:
                lines.append(f"    class {sid} {S.CLASS_NAMES[ck]}")
        return "\n".join(lines)


# ===========================================================================
# ER
# ===========================================================================

class ERBuilder:
    def __init__(self, title=""):
        self.title = title
        self._entities = {}     # name -> [(type, attr, key)]
        self._rels = []         # (a, b, card, label)

    def entity(self, name, attributes=None):
        self._entities[name] = attributes or []
        return name

    def attr(self, entity, type_, name, key=""):
        self._entities.setdefault(entity, []).append((type_, name, key))

    def relationship(self, a, b, cardinality, label=""):
        # cardinality e.g. "||--o{"
        self._rels.append((a, b, cardinality, label))

    def render(self):
        lines = []
        if self.title:
            lines += ["---", f"title: {self.title}", "---"]
        lines.append("erDiagram")
        for a, b, card, label in self._rels:
            lbl = label or "relates"
            lines.append(f'    {a} {card} {b} : "{lbl}"')
        for name, attrs in self._entities.items():
            if attrs:
                lines.append(f"    {name} {{")
                for type_, attr_name, key in attrs:
                    suffix = f" {key}" if key else ""
                    lines.append(f"        {type_} {attr_name}{suffix}")
                lines.append("    }")
        return "\n".join(lines)


# ===========================================================================
# C4
# ===========================================================================

class C4Builder:
    """Minimal C4Context/Container builder."""
    def __init__(self, title="", level="C4Context"):
        self.title = title
        self.level = level  # C4Context | C4Container | C4Component
        self._elems = []    # raw element lines
        self._rels = []     # (a, b, label, tech)

    def person(self, pid, label, descr=""):
        self._elems.append(f'    Person({pid}, "{label}", "{descr}")')
        return pid

    def system(self, sid, label, descr="", external=False):
        kw = "System_Ext" if external else "System"
        self._elems.append(f'    {kw}({sid}, "{label}", "{descr}")')
        return sid

    def container(self, cid, label, tech="", descr=""):
        self._elems.append(f'    Container({cid}, "{label}", "{tech}", "{descr}")')
        return cid

    def db(self, cid, label, tech="", descr=""):
        self._elems.append(f'    ContainerDb({cid}, "{label}", "{tech}", "{descr}")')
        return cid

    def rel(self, a, b, label="", tech=""):
        self._rels.append((a, b, label, tech))

    def render(self):
        lines = []
        if self.title:
            lines += ["---", f"title: {self.title}", "---"]
        lines.append(self.level)
        lines.extend(self._elems)
        for a, b, label, tech in self._rels:
            if tech:
                lines.append(f'    Rel({a}, {b}, "{label}", "{tech}")')
            else:
                lines.append(f'    Rel({a}, {b}, "{label}")')
        return "\n".join(lines)


# ===========================================================================
# SPEC DISPATCH
# ===========================================================================

def build_from_spec(spec: dict) -> str:
    t = spec.get("type", "flowchart")
    title = spec.get("title", "")

    if t == "flowchart":
        b = FlowchartBuilder(title, direction=spec.get("direction", "LR"))
        for n in spec["nodes"]:
            b.node(n["id"], n["label"], n["shape"], n["color"])
        for sg in spec.get("subgraphs", []):
            b.subgraph(sg["name"], sg["nodes"])
        for e in spec.get("edges", []):
            b.edge(e["source"], e["target"], e["connector"],
                   e.get("label", ""), e.get("bidirectional", False))
        if spec.get("legend"):
            b.legend()
        return b.render()

    if t == "sequence":
        b = SequenceBuilder(title)
        for p in spec["participants"]:
            b.participant(p["id"], p.get("label"), p.get("actor", False))
        for m in spec["messages"]:
            if m.get("note"):
                b.note(m["note"], m["over"])
            else:
                b.message(m["source"], m["target"], m["connector"],
                          m.get("label", ""), m.get("bidirectional", False))
        return b.render()

    if t == "state":
        b = StateBuilder(title)
        for s in spec["states"]:
            b.state(s["id"], s.get("label"), s.get("color"))
        for tr in spec["transitions"]:
            b.transition(tr["source"], tr["target"], tr.get("label", ""))
        return b.render()

    if t == "er":
        b = ERBuilder(title)
        for ent in spec["entities"]:
            b.entity(ent["name"], [(a["type"], a["name"], a.get("key", ""))
                                   for a in ent.get("attributes", [])])
        for r in spec.get("relationships", []):
            b.relationship(r["a"], r["b"], r["cardinality"], r.get("label", ""))
        return b.render()

    if t == "c4":
        b = C4Builder(title, level=spec.get("level", "C4Context"))
        for el in spec["elements"]:
            kind = el["kind"]
            if kind == "person":
                b.person(el["id"], el["label"], el.get("descr", ""))
            elif kind == "system":
                b.system(el["id"], el["label"], el.get("descr", ""),
                         el.get("external", False))
            elif kind == "container":
                b.container(el["id"], el["label"], el.get("tech", ""), el.get("descr", ""))
            elif kind == "db":
                b.db(el["id"], el["label"], el.get("tech", ""), el.get("descr", ""))
        for r in spec.get("relationships", []):
            b.rel(r["a"], r["b"], r.get("label", ""), r.get("tech", ""))
        return b.render()

    raise ValueError(f"Unknown diagram type: {t}")


def main(argv):
    if len(argv) < 3:
        print("usage: python mermaid_builder.py <spec.json> <out.mmd>")
        return 1
    with open(argv[1]) as f:
        spec = json.load(f)
    out = build_from_spec(spec)
    with open(argv[2], "w") as f:
        f.write(out + "\n")
    print(f"Wrote {argv[2]} ({spec.get('type','flowchart')} diagram)")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
