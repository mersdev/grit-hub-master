"""
creative_styles.py
==================
Curated 'creative' design system for the Architecture Diagram Designer's
NON-DHL mode. This is the deliberate counterpart to dhl_styles.py:

  dhl_styles.py     -> compliance mode (lifecycle colour law, 5 stencils)
  creative_styles.py -> creative mode  (modern palette, frontend-design polish)

Like the DHL standard, this is a *fixed, approved token set* so the agent
produces tidy, consistent output every time -- it is NOT a free-for-all.
The discipline is what keeps creative diagrams clean instead of random.

Borrowed sensibility from the frontend-design skill:
  - dominant colour + sharp accents (not timid even palettes)
  - a real spacing grid (8px base) so placement is never ad-hoc
  - soft shadows + rounded geometry for depth
  - one accent role-colour per band for instant segregation
"""

# ---------------------------------------------------------------------------
# SPACING GRID  (8px base -- every coordinate is a multiple of GRID)
# ---------------------------------------------------------------------------
GRID = 8
BAND_PAD = 24          # inner padding inside a band
NODE_GAP = 24          # gap between sibling nodes
BAND_GAP = 32          # vertical gap between bands

# ---------------------------------------------------------------------------
# PALETTE  (functional, not lifecycle. colour = which band / role)
#   Each role: fill (soft tint), stroke (saturated), text (ink).
#   Dominant neutral canvas + one accent per band = clean segregation.
# ---------------------------------------------------------------------------
INK   = "#1d2433"      # primary text
MUTED = "#5b6577"      # secondary text
CANVAS = "#f7f8fb"     # page background
BAND_FILL = "#ffffff"  # band container fill
BAND_STROKE = "#e3e7ef"

ROLES = {
    "people":   {"fill": "#eef2ff", "stroke": "#6366f1", "text": "#312e81", "accent": "#6366f1"},
    "access":   {"fill": "#ecfeff", "stroke": "#0891b2", "text": "#155e75", "accent": "#0891b2"},
    "brain":    {"fill": "#faf5ff", "stroke": "#9333ea", "text": "#6b21a8", "accent": "#9333ea"},
    "memory":   {"fill": "#ecfdf5", "stroke": "#059669", "text": "#065f46", "accent": "#059669"},
    "connect":  {"fill": "#fff7ed", "stroke": "#ea580c", "text": "#9a3412", "accent": "#ea580c"},
    "guard":    {"fill": "#fef2f2", "stroke": "#dc2626", "text": "#991b1b", "accent": "#dc2626"},
}

# ---------------------------------------------------------------------------
# NODE SHAPES  (rounded 'card' + 'pill'; semantic but modern)
# ---------------------------------------------------------------------------
def card(role, shadow=True):
    r = ROLES[role]
    sh = "shadow=1;" if shadow else ""
    return (
        f"rounded=1;arcSize=12;whiteSpace=wrap;html=1;{sh}"
        f"fillColor={r['fill']};strokeColor={r['stroke']};strokeWidth=1.5;"
        f"fontColor={r['text']};fontSize=13;fontStyle=1;"
        f"verticalAlign=middle;align=center;spacing=8;"
    )

def hub(role):
    r = ROLES[role]
    return (
        f"ellipse;whiteSpace=wrap;html=1;shadow=1;"
        f"fillColor={r['stroke']};strokeColor={r['accent']};strokeWidth=2;"
        f"fontColor=#ffffff;fontSize=14;fontStyle=1;verticalAlign=middle;align=center;"
    )

def band(role):
    r = ROLES[role]
    return (
        f"rounded=1;arcSize=4;whiteSpace=wrap;html=1;"
        f"fillColor={BAND_FILL};strokeColor={BAND_STROKE};strokeWidth=1;"
        f"verticalAlign=top;align=left;spacingLeft=14;spacingTop=10;"
        f"fontColor={r['text']};fontSize=12;fontStyle=1;"
    )

# ---------------------------------------------------------------------------
# CONNECTORS  (clean orthogonal; colour echoes source band's accent)
# ---------------------------------------------------------------------------
def flow(role, dashed=False):
    r = ROLES[role]
    d = "dashed=1;dashPattern=6 4;" if dashed else ""
    return (
        f"edgeStyle=orthogonalEdgeStyle;rounded=1;html=1;{d}"
        f"strokeColor={r['stroke']};strokeWidth=2;endArrow=block;endFill=1;endSize=8;"
        f"jumpStyle=arc;jumpSize=10;fontColor={MUTED};fontSize=11;"
    )
