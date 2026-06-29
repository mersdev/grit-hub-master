"""
mermaid_styles.py
=================
Single source of truth for the DHL Mermaid diagram standard.

Mermaid cannot reproduce draw.io custom stencils (no actor PNG, no database
cylinder applied to arbitrary nodes, no gradient fills). So the DHL identity in
Mermaid is carried by:

  1. LIFECYCLE COLOUR  -> classDef blocks (fill + stroke), matching the draw.io
                          colour scheme exactly.
  2. NODE SHAPE        -> Mermaid's built-in node-shape syntax, chosen to echo the
                          semantic shape as closely as Mermaid allows.
  3. CONNECTOR MEANING -> link style (solid/dotted/thick) + a labelled convention,
                          matching the draw.io connector catalogue.

These are the approved tokens. Do not invent new fill colours at the diagram level.

Imported by mermaid_builder.py and validate_mermaid.py.
"""

from __future__ import annotations

# ---------------------------------------------------------------------------
# 1. LIFECYCLE COLOURS  ->  classDef blocks
#    fill / stroke values are identical to the draw.io DHL pack.
# ---------------------------------------------------------------------------

COLORS = {
    "existing_no_change": {
        "label": "Existing – No Change", "human": "green",
        "fill": "#85ca39", "stroke": "#5a8a26", "color": "#1b2a0a",
    },
    "existing_to_change": {
        "label": "Existing – To Change", "human": "yellow",
        "fill": "#ffd21e", "stroke": "#b8960f", "color": "#3a2f00",
    },
    "existing_decomm": {
        "label": "Existing – Decomm", "human": "grey",
        "fill": "#969696", "stroke": "#6b6b6b", "color": "#1a1a1a",
    },
    "new_target_solution": {
        "label": "New Target Solution", "human": "blue",
        "fill": "#158aff", "stroke": "#0a5cb8", "color": "#ffffff",
    },
    "new_sub_component": {
        "label": "New Sub Component", "human": "red",
        "fill": "#bd2f2f", "stroke": "#7d1f1f", "color": "#ffffff",
    },
    "logical_name": {
        "label": "Logical Name", "human": "yellow label",
        "fill": "#ffd21e", "stroke": "#b8960f", "color": "#3a2f00",
    },
    "link_to_different_function_view": {
        "label": "Link To Different Function View", "human": "yellow, dark border",
        "fill": "#ffd21e", "stroke": "#404040", "color": "#3a2f00",
    },
}

# CSS class name used in Mermaid for each colour key (classDef <name>).
CLASS_NAMES = {k: k for k in COLORS}

COLOR_ALIASES = {
    "no_change": "existing_no_change", "unchanged": "existing_no_change",
    "keep": "existing_no_change", "green": "existing_no_change",
    "to_change": "existing_to_change", "change": "existing_to_change",
    "modify": "existing_to_change", "rewire": "existing_to_change",
    "enhance": "existing_to_change", "yellow": "existing_to_change",
    "decomm": "existing_decomm", "retire": "existing_decomm",
    "remove": "existing_decomm", "bypass": "existing_decomm", "grey": "existing_decomm",
    "new": "new_target_solution", "target": "new_target_solution",
    "new_solution": "new_target_solution", "blue": "new_target_solution",
    "subcomponent": "new_sub_component", "sub": "new_sub_component", "red": "new_sub_component",
}

# ---------------------------------------------------------------------------
# 2. SEMANTIC SHAPES  ->  Mermaid flowchart node-shape syntax
#    Each entry is (open_token, close_token) that wraps the label.
#    These echo the draw.io shapes as closely as Mermaid permits.
# ---------------------------------------------------------------------------

SHAPES = {
    "actor": {
        "label": "Actor / Role / Business Function",
        # Mermaid has no person icon in flowcharts; a stadium reads as a role.
        "open": "([", "close": "])",
        "note": "Stadium shape stands in for an actor/role (Mermaid has no person icon in flowcharts).",
    },
    "application": {
        "label": "Application",
        "open": "[", "close": "]",
        "note": "Rectangle = application/system.",
    },
    "business_orchestration": {
        "label": "Business Orchestration",
        "open": "{{", "close": "}}",
        "note": "Hexagon = orchestration/workflow/middleware.",
    },
    "service": {
        "label": "Service",
        "open": "(", "close": ")",
        "note": "Rounded rectangle = API/service.",
    },
    "database": {
        "label": "Database",
        "open": "[(", "close": ")]",
        "note": "Cylinder = database/datastore.",
    },
}

SHAPE_ALIASES = {
    "actor": "actor", "role": "actor", "user": "actor", "person": "actor",
    "team": "actor", "department": "actor", "business_function": "actor",
    "app": "application", "application": "application", "system": "application",
    "frontend": "application", "backend": "application", "portal": "application",
    "webapp": "application", "mobile": "application", "dashboard": "application",
    "platform": "application",
    "orchestration": "business_orchestration", "workflow": "business_orchestration",
    "middleware": "business_orchestration", "process_engine": "business_orchestration",
    "integration_flow": "business_orchestration", "esb": "business_orchestration",
    "service": "service", "api": "service", "microservice": "service",
    "endpoint": "service", "soa": "service",
    "database": "database", "db": "database", "datastore": "database",
    "warehouse": "database", "schema": "database", "table": "database",
    "datalake": "database",
}

# ---------------------------------------------------------------------------
# 3. CONNECTORS  ->  Mermaid flowchart link styles
#    Mermaid links can't carry arbitrary colours inline per-link easily across
#    all renderers, so meaning is encoded by line pattern + label convention,
#    and reinforced by `linkStyle` colour where the renderer supports it.
#
#    line:    "solid" | "dotted" | "thick"
#    bidir:   whether to use <--> (request & response on one arrow)
#    stroke:  colour applied via linkStyle (matches draw.io connector colour)
# ---------------------------------------------------------------------------

CONNECTORS = {
    "update_feed_existing": {
        "label": "Update / Feed - Existing", "line": "solid",
        "stroke": "#404040", "bidir_ok": False,
    },
    "update_feed_target": {
        "label": "Update / Feed - Target", "line": "dotted",
        "stroke": "#404040", "bidir_ok": False,
    },
    "query_response_existing": {
        "label": "Query & Response - Existing", "line": "solid",
        "stroke": "#ff9933", "bidir_ok": True,
    },
    "query_response_change": {
        "label": "Query & Response - Change", "line": "solid",
        "stroke": "#ff0000", "bidir_ok": True,
    },
    "query_response_new": {
        "label": "Query & Response - New", "line": "dotted",
        "stroke": "#ff0000", "bidir_ok": True,
    },
    "status_existing": {
        "label": "Status - Existing", "line": "solid",
        "stroke": "#00b050", "bidir_ok": False,
    },
    "status_target": {
        "label": "Status - Target", "line": "dotted",
        "stroke": "#00b050", "bidir_ok": False,
    },
    "persistent_process_call": {
        "label": "Persistent Process Call", "line": "thick",
        "stroke": "#3399ff", "bidir_ok": False,
    },
    "response": {
        "label": "Response", "line": "solid",
        "stroke": "#92d050", "bidir_ok": False,
    },
}

CONNECTOR_ALIASES = {
    "feed": "update_feed_existing", "update": "update_feed_existing",
    "batch": "update_feed_existing", "daily_feed": "update_feed_existing",
    "future_feed": "update_feed_target", "target_feed": "update_feed_target",
    "query": "query_response_existing", "request_reply": "query_response_existing",
    "qr": "query_response_existing", "api_call": "query_response_existing",
    "changed_query": "query_response_change",
    "new_query": "query_response_new",
    "status": "status_existing",
    "future_status": "status_target",
    "persistent": "persistent_process_call", "long_running": "persistent_process_call",
    "response": "response", "reply": "response", "return": "response",
}

# ---------------------------------------------------------------------------
# 4. SUPPORTED DIAGRAM TYPES
# ---------------------------------------------------------------------------

DIAGRAM_TYPES = {
    "flowchart": {
        "header": "flowchart LR",
        "use": "solution / integration / data-flow / migration / infra-zone diagrams",
        "supports_classdef": True,
    },
    "sequence": {
        "header": "sequenceDiagram",
        "use": "request/response flows, API orchestration, multi-agent messaging",
        "supports_classdef": False,
    },
    "state": {
        "header": "stateDiagram-v2",
        "use": "lifecycle/status machines, order processing, registration/role flows",
        "supports_classdef": True,
    },
    "er": {
        "header": "erDiagram",
        "use": "database schemas and data models",
        "supports_classdef": False,
    },
    "c4": {
        "header": "C4Context",
        "use": "C4 system/container/component architecture views",
        "supports_classdef": False,
    },
}


# ---------------------------------------------------------------------------
# Resolvers
# ---------------------------------------------------------------------------

def _norm(s: str) -> str:
    return s.strip().lower().replace(" ", "_").replace("–", "").replace("-", "_") \
        .replace("&", "").replace("/", "_").replace("__", "_").strip("_")


def resolve_color(name: str) -> str:
    key = _norm(name)
    if key in COLORS:
        return key
    if key in COLOR_ALIASES:
        return COLOR_ALIASES[key]
    raise KeyError(f"Unknown colour '{name}'. Valid: {list(COLORS)} or aliases.")


def resolve_shape(name: str) -> str:
    key = name.strip().lower().replace(" ", "_").replace("/", "_")
    if key in SHAPES:
        return key
    if key in SHAPE_ALIASES:
        return SHAPE_ALIASES[key]
    raise KeyError(f"Unknown shape '{name}'. Valid: {list(SHAPES)} or aliases.")


def resolve_connector(name: str) -> str:
    key = _norm(name)
    if key in CONNECTORS:
        return key
    if key in CONNECTOR_ALIASES:
        return CONNECTOR_ALIASES[key]
    raise KeyError(f"Unknown connector '{name}'. Valid: {list(CONNECTORS)} or aliases.")


def classdef_line(color_key: str) -> str:
    """Return a Mermaid `classDef` line for a lifecycle colour."""
    c = COLORS[color_key]
    return (f"classDef {CLASS_NAMES[color_key]} "
            f"fill:{c['fill']},stroke:{c['stroke']},color:{c['color']},stroke-width:2px;")
