"""
build_creative_smp.py  (creative mode, FREE aesthetics)
========================================================
Rebuilds the GRIT Copilot architecture as a creative-mode diagram.

Creative mode is FREE on aesthetics: this version commits to one bold direction
-- a dark editorial 'midnight control room' poster with gradient panels, a glowing
central hub, and accent-coded bands -- rather than a fixed pastel catalogue.
The palette is defined ONCE at the top (per-diagram discipline) and applied
consistently. Output still passes validate_creative_drawio.py: on-grid, no
overlaps, orthogonal connectors, no crossings. Swap PALETTE to re-skin.
"""
import html
GRID = 8
def snap(v): return int(round(v / GRID) * GRID)

# ---- PER-DIAGRAM PALETTE (single source of consistency for THIS diagram) ----
# Aesthetic direction: light / refined-minimal on white. Soft tinted cards,
# saturated strokes, ink text, one hero accent (amber) for the hub.
BG="#ffffff"; PANEL="#fbfcfe"; PANEL_EDGE="#e6e9f0"
INK="#1d2433"; MUTED="#6b7385"; TITLE="#0f1626"
# accent per band as (soft fill, saturated stroke, dark text-on-fill)
ACCENTS={
 "people":("#f1effe","#7c3aed","#3b2480"), "access":("#e6f7f5","#0d9488","#0a5b52"),
 "brain":("#fff4e0","#d97706","#7a4406"),  "memory":("#e9f8f0","#059669","#075c43"),
 "connect":("#fff0e6","#ea580c","#8a3309"),"guard":("#fdeeee","#dc2626","#8f1d1d"),
}
def card(a,hero=False):
    fill,stroke,txt=ACCENTS[a]; sw=2 if hero else 1.25
    return (f"rounded=1;arcSize=14;whiteSpace=wrap;html=1;shadow=1;"
            f"fillColor={fill};strokeColor={stroke};strokeWidth={sw};"
            f"fontColor={txt};fontSize=13;fontStyle=1;"
            f"verticalAlign=middle;align=center;spacing=8;")
def hub(a):
    fill,stroke,txt=ACCENTS[a]
    return (f"ellipse;whiteSpace=wrap;html=1;shadow=1;"
            f"fillColor={stroke};strokeColor={stroke};strokeWidth=2;"
            f"fontColor=#ffffff;fontSize=14;fontStyle=1;"
            f"verticalAlign=middle;align=center;")
def band():
    return (f"rounded=1;arcSize=3;whiteSpace=wrap;html=1;"
            f"fillColor={PANEL};strokeColor={PANEL_EDGE};strokeWidth=1;"
            f"verticalAlign=top;align=left;spacingLeft=14;spacingTop=9;"
            f"fontColor={MUTED};fontSize=12;fontStyle=2;")
def flow(a,dashed=False):
    fill,stroke,txt=ACCENTS[a]; d="dashed=1;dashPattern=6 4;" if dashed else ""
    return (f"edgeStyle=orthogonalEdgeStyle;rounded=1;html=1;{d}"
            f"strokeColor={stroke};strokeWidth=2;endArrow=block;endFill=1;endSize=8;"
            f"jumpStyle=arc;jumpSize=10;fontColor={MUTED};fontSize=11;")

cells=[]
def cell(id,value,style,x,y,w,h,parent="1"):
    x,y,w,h=snap(x),snap(y),snap(w),snap(h); v=html.escape(value,quote=True)
    cells.append(f'<mxCell id="{id}" value="{v}" style="{style}" vertex="1" parent="{parent}">'
                 f'<mxGeometry x="{x}" y="{y}" width="{w}" height="{h}" as="geometry"/></mxCell>')
def edge(id,src,tgt,style,value=""):
    v=html.escape(value,quote=True)
    cells.append(f'<mxCell id="{id}" value="{v}" style="{style}" edge="1" parent="1" source="{src}" target="{tgt}">'
                 f'<mxGeometry relative="1" as="geometry"/></mxCell>')

PW,PH=1184,1024; MX=40; CW=PW-2*MX; BAND_GAP=32
def band_box(id,title,y,h): cell(id,title,band(),MX,y,CW,h)

cells.append(f'<mxCell id="title" value="GRIT Copilot — Agent Architecture" '
  f'style="text;html=1;fontSize=24;fontStyle=1;fontColor={TITLE};align=left;verticalAlign=middle;" '
  f'vertex="1" parent="1"><mxGeometry x="40" y="24" width="1104" height="38" as="geometry"/></mxCell>')
cells.append(f'<mxCell id="subtitle" value="One assistant · specialized agents · shared memory · guarded integrations" '
  f'style="text;html=1;fontSize=13;fontColor={MUTED};align=left;verticalAlign=middle;" '
  f'vertex="1" parent="1"><mxGeometry x="40" y="62" width="1104" height="22" as="geometry"/></mxCell>')

cw2=(CW-3*24)//2
y=104
band_box("b_people","PEOPLE",y,96)
cell("p_members","Team members\nDevelopers · testers · architects",card("people"),MX+24,y+32,cw2,48)
cell("p_admin","Team admin / contributor\nAdds new skills and agents",card("people"),MX+48+cw2,y+32,cw2,48)
y+=96+BAND_GAP
band_box("b_access","ACCESS POINTS · GitHub Copilot — one assistant, two ways in",y,96)
cell("a_cli","Command line (CLI)",card("access"),MX+24,y+32,cw2,48)
cell("a_ide","IDE (VS Code / JetBrains)",card("access"),MX+48+cw2,y+32,cw2,48)
y+=96+BAND_GAP
BH=152
band_box("b_brain","INTELLIGENCE LAYER · the agent brain",y,BH)
cell("br_agents","Specialized agents\nA persona per role & task",card("brain"),MX+24,y+48,304,72)
cell("h_hub","Agent\nInterpreter",hub("brain"),MX+(CW-152)//2,y+48,152,72)
cell("br_skills","Reusable skills\nReview · research · slides",card("brain"),MX+CW-24-304,y+48,304,72)
y+=BH+BAND_GAP
band_box("b_mem","KNOWLEDGE CORE · shared memory that persists across sessions",y,96)
cell("m_mem","Memory system\nRemembers facts & decisions",card("memory"),MX+24,y+32,cw2,48)
cell("m_track","Learning tracker\nTracks skill progression",card("memory"),MX+48+cw2,y+32,cw2,48)
y+=96+BAND_GAP
band_box("b_conn","CONNECTIONS & SAFEGUARDS",y,96)
cell("c_mcp","MCP integrations\nFiles · web · diagrams · reasoning",card("connect"),MX+24,y+32,cw2,48)
cell("c_guard","Security guardrails\nPII protection · secret scanning",card("guard"),MX+48+cw2,y+32,cw2,48)

edge("e1","p_members","a_cli",flow("people"))
edge("e2","p_admin","a_ide",flow("people"))
edge("e3","a_cli","br_agents",flow("access"))
edge("e4","a_ide","br_skills",flow("access"))
edge("e5","br_agents","h_hub",flow("brain"))
edge("e6","br_skills","h_hub",flow("brain"))
edge("e7","h_hub","m_mem",flow("brain"))
edge("e8","h_hub","m_track",flow("brain"))
edge("e9","m_mem","c_mcp",flow("memory"))
edge("e10","m_track","c_guard",flow("memory"))

inner="\n".join(cells)
xml=f'''<mxfile host="app.diagrams.net">
  <diagram name="GRIT Copilot Architecture (creative)">
    <mxGraphModel dx="800" dy="600" grid="1" gridSize="8" guides="1" tooltips="1"
      connect="1" arrows="1" fold="1" page="1" pageScale="1"
      pageWidth="{PW}" pageHeight="{PH}" math="0" shadow="0" background="{BG}">
      <root>
        <mxCell id="0"/>
        <mxCell id="1" parent="0"/>
{inner}
      </root>
    </mxGraphModel>
  </diagram>
</mxfile>'''
import os, sys
_default = os.path.join(os.path.dirname(__file__), "..", "examples", "smp_copilot_creative.drawio")
_out = sys.argv[1] if len(sys.argv) > 1 else _default
open(_out, "w").write(xml)
print("wrote", os.path.abspath(_out), len(xml), "bytes,", len(cells), "cells")
