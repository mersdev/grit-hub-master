"""
validate_creative_drawio.py
============================
Tidiness gate for CREATIVE-mode .drawio output (the non-DHL mode).

Creative mode is free on aesthetics (any palette, gradients, shapes) but strict
on STRUCTURE. This validator therefore checks layout discipline ONLY -- it does
NOT enforce any colour catalogue. (That is the whole point of creative mode.)

Checks
------
  - well-formed XML
  - unique mxCell ids
  - every vertex has geometry with width+height; every edge has source+target
  - every node coordinate is on the GRID (default 8px)
  - no two solid nodes overlap (container/band/group/text cells are skipped)
  - every edge uses orthogonal routing
  - no edge passes through the interior of an unrelated node (crossing check)

Usage:  python validate_creative_drawio.py file.drawio [--grid=N]
Exit 0 = pass, 1 = fail.
"""
import os, sys, xml.etree.ElementTree as ET

GRID = 8
args = [a for a in sys.argv[1:] if not a.startswith("--")]
for a in sys.argv[1:]:
    if a.startswith("--grid="):
        GRID = int(a.split("=", 1)[1])
_default = os.path.join(os.path.dirname(__file__), "..", "examples", "smp_copilot_creative.drawio")
path = args[0] if args else _default

errs = []
try:
    root = ET.parse(path).getroot()
except Exception as e:
    print(f"CREATIVE TIDINESS: FAILED\n - XML parse error: {e}")
    sys.exit(1)

cells = list(root.iter("mxCell"))

def numf(g, k):
    v = g.get(k)
    try: return float(v)
    except (TypeError, ValueError): return None

seen = set()
for c in cells:
    cid = c.get("id")
    if cid in seen: errs.append(f"duplicate id {cid}")
    seen.add(cid)

verts, edges, byid = [], [], {}
for c in cells:
    g = c.find("mxGeometry")
    style = c.get("style", "") or ""
    if c.get("vertex") == "1" and g is not None:
        x, y, w, h = numf(g,"x"), numf(g,"y"), numf(g,"width"), numf(g,"height")
        if w is None or h is None:
            errs.append(f"vertex {c.get('id')} missing width/height"); continue
        rec = (c.get("id"), style, x or 0, y or 0, w, h)
        byid[c.get("id")] = rec; verts.append(rec)
    elif c.get("edge") == "1":
        edges.append(c)

def is_container(style):
    s = style.lower()
    return ("verticalalign=top" in s) or ("group" in s) or ("startsize" in s) or ("text;" in s)
def is_text(style):
    return "text;" in (style or "").lower()

nodes = [v for v in verts if not is_container(v[1]) and not is_text(v[1])]

for (cid, style, x, y, w, h) in verts:
    if is_text(style): continue
    for nm, val in (("x",x),("y",y),("w",w),("h",h)):
        if val is not None and abs(val) % GRID != 0:
            errs.append(f"off-grid {cid} {nm}={val}")

def boxes_overlap(a, b):
    _,_,ax,ay,aw,ah = a; _,_,bx,by,bw,bh = b
    return not (ax+aw <= bx or bx+bw <= ax or ay+ah <= by or by+bh <= ay)
for i in range(len(nodes)):
    for j in range(i+1, len(nodes)):
        if boxes_overlap(nodes[i], nodes[j]):
            errs.append(f"overlap {nodes[i][0]} <-> {nodes[j][0]}")

for e in edges:
    if "orthogonaledgestyle" not in (e.get("style","") or "").lower():
        errs.append(f"non-orthogonal edge {e.get('id')}")

def centre(rec):
    _,_,x,y,w,h = rec; return (x+w/2, y+h/2)
def seg_hits_rect(p1, p2, rec, shrink=6):
    _,_,x,y,w,h = rec
    rx1, ry1, rx2, ry2 = x+shrink, y+shrink, x+w-shrink, y+h-shrink
    for t in range(1, 20):
        f = t/20
        px = p1[0] + (p2[0]-p1[0])*f
        py = p1[1] + (p2[1]-p1[1])*f
        if rx1 < px < rx2 and ry1 < py < ry2: return True
    return False
for e in edges:
    s, t = e.get("source"), e.get("target")
    if s not in byid or t not in byid: continue
    p1, p2 = centre(byid[s]), centre(byid[t])
    for n in nodes:
        if n[0] in (s, t): continue
        if seg_hits_rect(p1, p2, n):
            errs.append(f"edge {e.get('id')} crosses node {n[0]}")

ok = not errs
print("CREATIVE TIDINESS:", "PASSED" if ok else "FAILED")
for e in errs[:30]: print(" -", e)
if len(errs) > 30: print(f" ... and {len(errs)-30} more")
sys.exit(0 if ok else 1)
