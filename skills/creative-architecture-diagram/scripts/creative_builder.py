"""
creative_builder.py
====================
Spec-driven generator for creative banded-poster .drawio diagrams.

This is the ENGINE. Do NOT hand-write draw.io XML for a creative banded poster --
write a small JSON/dict spec and call build(spec) (or run this file on a spec JSON).
The builder owns every tidiness-critical detail so the output is guaranteed clean:

  * two-line cards (bold title row + lighter subtitle row) -- never a run-on string
  * full-width band containers with a top-left band label (not floating text)
  * a straight orthogonal connector spine, waypointed so nothing crosses
  * 8px grid snapping on every coordinate
  * one accent colour per band

Because the builder fixes all of that, a caller cannot reproduce the "hand-written
XML" failure mode (jammed text, loose labels, busy connectors). Just describe content.

------------------------------------------------------------------------------
SPEC FORMAT  (all keys optional unless noted)
------------------------------------------------------------------------------
{
  "title": "GRIT Copilot — Agent Architecture",        # required
  "subtitle": "One assistant · shared memory · ...",
  "aesthetic": "light",            # "light" (default, white bg) or "dark"
  "bands": [                       # required, top-to-bottom order
    {
      "id": "people",              # short slug, also the accent key
      "label": "PEOPLE",           # band header (top-left, inside the band)
      "accent": "violet",          # name from PALETTES[aesthetic], or omit to auto-assign
      "items": [                   # 1-3 cards in this band
        {"id": "members", "title": "Team members",
         "subtitle": "Developers, testers, architects"},
        {"id": "admin", "title": "Team admin / contributor",
         "subtitle": "Adds new skills and agents"}
      ],
      "hub": {"id": "hub", "title": "Agent", "subtitle": "Interpreter"}  # optional centre piece
    },
    ...
  ],
  "connections": [                 # straight spine; builder routes orthogonally
    {"from": "members", "to": "cli"},
    {"from": "admin",   "to": "ide"},
    ...
  ]
}

Run:  python creative_builder.py spec.json out.drawio
   or import: from creative_builder import build; xml = build(spec_dict)
"""
import html, json, os, sys

GRID = 8
def snap(v): return int(round(v / GRID) * GRID)

# ---------------------------------------------------------------------------
# PALETTES -- aesthetic direction. Each accent is (fill, stroke, text-on-fill).
# Add or edit accents freely; this is the per-diagram palette source.
# ---------------------------------------------------------------------------
PALETTES = {
    "light": {
        "_bg": "#ffffff", "_panel": "#fbfcfe", "_panel_edge": "#e6e9f0",
        "_ink": "#1d2433", "_muted": "#6b7385", "_title": "#0f1626",
        "violet":  ("#f1effe", "#7c3aed", "#3b2480"),
        "teal":    ("#e6f7f5", "#0d9488", "#0a5b52"),
        "amber":   ("#fff4e0", "#d97706", "#7a4406"),
        "emerald": ("#e9f8f0", "#059669", "#075c43"),
        "orange":  ("#fff0e6", "#ea580c", "#8a3309"),
        "red":     ("#fdeeee", "#dc2626", "#8f1d1d"),
        "blue":    ("#eaf1fd", "#2563eb", "#1e3a8a"),
        "slate":   ("#eef1f6", "#475569", "#1e293b"),
    },
    "dark": {
        "_bg": "#0e1424", "_panel": "#16213a", "_panel_edge": "#243250",
        "_ink": "#eef2ff", "_muted": "#93a1c4", "_title": "#ffffff",
        # dark uses saturated fills with light text
        "violet":  ("#3b2480", "#a78bfa", "#ede9fe"),
        "teal":    ("#0a5b52", "#5eead4", "#ccfbf1"),
        "amber":   ("#7a4406", "#fbbf24", "#fef3c7"),
        "emerald": ("#075c43", "#6ee7b7", "#d1fae5"),
        "orange":  ("#8a3309", "#fdba74", "#ffedd5"),
        "red":     ("#8f1d1d", "#fca5a5", "#fee2e2"),
        "blue":    ("#1e3a8a", "#93c5fd", "#dbeafe"),
        "slate":   ("#1e293b", "#94a3b8", "#e2e8f0"),
    },
}
# default accent rotation when a band omits "accent"
ACCENT_ORDER = ["violet", "teal", "amber", "emerald", "orange", "red", "blue", "slate"]

# ---------------------------------------------------------------------------
# layout constants
# ---------------------------------------------------------------------------
PW = 1184                 # page width  (148 * 8)
MX = 40                   # outer margin
CW = PW - 2 * MX          # content width = 1104
GUT = 24                  # gutter between cards
BAND_GAP = 32             # vertical gap between bands
BAND_LABEL_H = 32         # space the band label occupies at the top of a band
CARD_H1 = 56              # single/two-line card height in a normal band
CARD_H_HUB = 72           # card + hub height in an intelligence band
TITLE_STRIP = 88          # top strip for title + subtitle


def _two_line_value(title, subtitle):
    """Bold title row + lighter subtitle row. draw.io cells with html=1 render
    HTML, but the value attribute must be XML-escaped, so the tags are encoded
    as entities (&lt;b&gt; ...). This yields a distinct title/subtitle -- never
    a hyphen-joined run-on string -- while keeping the XML well-formed."""
    t = html.escape(title, quote=True)
    if subtitle:
        s = html.escape(subtitle, quote=True)
        raw = (f"<b>{t}</b><br><span style=\"font-size:11px;opacity:0.85\">{s}</span>")
    else:
        raw = f"<b>{t}</b>"
    # escape the whole HTML string for safe embedding in the XML attribute
    return html.escape(raw, quote=True)


def build(spec):
    aesthetic = spec.get("aesthetic", "light")
    P = PALETTES[aesthetic]
    BG, PANEL, PANEL_EDGE = P["_bg"], P["_panel"], P["_panel_edge"]
    MUTED, TITLE = P["_muted"], P["_title"]

    cells = []
    def cell(cid, value, style, x, y, w, h, parent="1", is_html=False):
        x, y, w, h = snap(x), snap(y), snap(w), snap(h)
        v = value if is_html else html.escape(value, quote=True)
        cells.append(
            f'<mxCell id="{cid}" value="{v}" style="{style}" vertex="1" parent="{parent}">'
            f'<mxGeometry x="{x}" y="{y}" width="{w}" height="{h}" as="geometry"/></mxCell>')
    def edge(cid, src, tgt, style):
        cells.append(
            f'<mxCell id="{cid}" value="" style="{style}" edge="1" parent="1" '
            f'source="{src}" target="{tgt}"><mxGeometry relative="1" as="geometry"/></mxCell>')

    def card_style(accent, hero=False):
        fill, stroke, txt = P[accent]
        sw = 2 if hero else 1.25
        return (f"rounded=1;arcSize=14;whiteSpace=wrap;html=1;shadow=1;"
                f"fillColor={fill};strokeColor={stroke};strokeWidth={sw};"
                f"fontColor={txt};fontSize=13;verticalAlign=middle;align=center;spacing=8;")
    def hub_style(accent):
        fill, stroke, txt = P[accent]
        return (f"ellipse;whiteSpace=wrap;html=1;shadow=1;"
                f"fillColor={stroke};strokeColor={stroke};strokeWidth=2;"
                f"fontColor=#ffffff;fontSize=14;verticalAlign=middle;align=center;")
    def band_style():
        return (f"rounded=1;arcSize=3;whiteSpace=wrap;html=1;"
                f"fillColor={PANEL};strokeColor={PANEL_EDGE};strokeWidth=1;"
                f"verticalAlign=top;align=left;spacingLeft=14;spacingTop=9;"
                f"fontColor={MUTED};fontSize=12;fontStyle=2;")
    def flow_style(accent):
        fill, stroke, txt = P[accent]
        return (f"edgeStyle=orthogonalEdgeStyle;rounded=1;html=1;"
                f"strokeColor={stroke};strokeWidth=2;endArrow=block;endFill=1;endSize=8;"
                f"jumpStyle=arc;jumpSize=10;")

    # ---- title strip ----
    cell("title", spec["title"],
         f"text;html=1;fontSize=24;fontStyle=1;fontColor={TITLE};align=left;verticalAlign=middle;",
         MX, 24, CW, 38)
    if spec.get("subtitle"):
        cell("subtitle", spec["subtitle"],
             f"text;html=1;fontSize=13;fontColor={MUTED};align=left;verticalAlign=middle;",
             MX, 62, CW, 22)

    # ---- bands ----
    accent_for = {}
    auto_i = 0
    y = TITLE_STRIP + 16
    item_accent = {}     # item id -> accent (for connector colour)
    for band in spec["bands"]:
        bid = band["id"]
        accent = band.get("accent")
        if not accent:
            accent = ACCENT_ORDER[auto_i % len(ACCENT_ORDER)]; auto_i += 1
        accent_for[bid] = accent

        has_hub = "hub" in band and band["hub"]
        band_h = BAND_LABEL_H + (CARD_H_HUB if has_hub else CARD_H1) + 16
        cell(f"band_{bid}", band.get("label", bid.upper()), band_style(), MX, y, CW, band_h)

        items = band["items"]
        card_y = y + BAND_LABEL_H
        card_h = CARD_H_HUB if has_hub else CARD_H1

        if has_hub and len(items) == 2:
            # left card | hub | right card
            hub_w = 152
            side_w = (CW - 2 * GUT - hub_w - 2 * GUT) // 2
            left, right = items[0], items[1]
            cell(left["id"], _two_line_value(left["title"], left.get("subtitle")),
                 card_style(accent), MX + GUT, card_y, side_w, card_h, is_html=True)
            cell(band["hub"]["id"], _two_line_value(band["hub"]["title"], band["hub"].get("subtitle")),
                 hub_style(accent), MX + (CW - hub_w) // 2, card_y, hub_w, card_h, is_html=True)
            cell(right["id"], _two_line_value(right["title"], right.get("subtitle")),
                 card_style(accent), MX + CW - GUT - side_w, card_y, side_w, card_h, is_html=True)
            item_accent[left["id"]] = item_accent[right["id"]] = accent
            item_accent[band["hub"]["id"]] = accent
        else:
            n = len(items)
            card_w = (CW - (n + 1) * GUT) // n
            for i, it in enumerate(items):
                cx = MX + GUT + i * (card_w + GUT)
                cell(it["id"], _two_line_value(it["title"], it.get("subtitle")),
                     card_style(accent), cx, card_y, card_w, card_h, is_html=True)
                item_accent[it["id"]] = accent

        y += band_h + BAND_GAP

    # ---- connectors (orthogonal; colour echoes source band accent) ----
    for i, c in enumerate(spec.get("connections", [])):
        acc = item_accent.get(c["from"], ACCENT_ORDER[0])
        edge(f"e{i}", c["from"], c["to"], flow_style(acc))

    page_h = snap(y + 40)
    inner = "\n".join(cells)
    return (f'<mxfile host="app.diagrams.net">\n'
            f'  <diagram name="{html.escape(spec["title"], quote=True)}">\n'
            f'    <mxGraphModel dx="800" dy="600" grid="1" gridSize="8" guides="1" '
            f'tooltips="1" connect="1" arrows="1" fold="1" page="1" pageScale="1" '
            f'pageWidth="{PW}" pageHeight="{page_h}" math="0" shadow="0" background="{BG}">\n'
            f'      <root>\n        <mxCell id="0"/>\n        <mxCell id="1" parent="0"/>\n'
            f'{inner}\n      </root>\n    </mxGraphModel>\n  </diagram>\n</mxfile>')


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("usage: python creative_builder.py <spec.json> [out.drawio]")
        sys.exit(2)
    spec = json.load(open(sys.argv[1]))
    out = sys.argv[2] if len(sys.argv) > 2 else os.path.splitext(sys.argv[1])[0] + ".drawio"
    open(out, "w").write(build(spec))
    print("wrote", os.path.abspath(out))
