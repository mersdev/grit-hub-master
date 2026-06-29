"""
dhl_styles.py
=============
Single source of truth for all approved DHL draw.io styles.

These strings are cloned verbatim from the DHL Chart Legend (.drawio XML).
DO NOT invent new fillColor / gradientColor / shape=stencil(...) values here.
The composition helpers below only ever swap the approved lifecycle colour
tokens onto an approved shape stencil — they never alter the stencil itself.

Imported by drawio_builder.py.
"""

# ---------------------------------------------------------------------------
# 1. SHAPE STENCILS  (answer: "what is this thing?")
#    Each entry stores the raw style with its native fillColor placeholders.
#    `default_geometry` is (width, height).
# ---------------------------------------------------------------------------

SHAPES = {
    "actor": {
        "label": "Actor / Role / Business Function",
        "default_geometry": (62, 72),
        # Image-based actor. Has no fillColor to recolour (it's a PNG stencil),
        # so lifecycle colour is conveyed by a small status chip beside it.
        "is_image": True,
        "style": (
            "vsdxID=9;fillColor=none;gradientColor=none;image;aspect=fixed;"
            "image=data:image/png,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;"
            "strokeColor=none;points=[];labelBackgroundColor=none;rounded=0;html=1;whiteSpace=wrap;"
        ),
    },
    "application": {
        "label": "Application",
        "default_geometry": (160, 60),
        "is_image": False,
        "style": (
            "verticalAlign=middle;align=center;overflow=width;vsdxID=10;"
            "fillColor={fill};gradientColor={grad};gradientDirection=north;"
            "shape=stencil(nZBLDoAgDERP0z3SIyjew0SURgSD+Lu9kMZoXLhwN9O+tukAlrNpJg1SzDH4QW/URgNYgZTkjA4UkwJUgGXng+6DX1zLfmoymdXo17xh5zmRJ6Q42BWCfc2oJfdAr+Yv+AP9Cb7OJ3H/2JG1HNGz/84klThPVCc=);"
            "strokeColor={stroke};shadow=1;spacingTop=-1;spacingBottom=-1;spacingLeft=-1;spacingRight=-1;"
            "points=[[1,0.5,0],[0.5,0.5,0],[0.5,0,0]];labelBackgroundColor=none;rounded=0;html=1;whiteSpace=wrap;"
        ),
    },
    "business_orchestration": {
        "label": "Business Orchestration",
        "default_geometry": (170, 70),
        "is_image": False,
        "style": (
            "verticalAlign=middle;align=center;overflow=width;vsdxID=11;"
            "fillColor={fill};gradientColor={grad};gradientDirection=north;"
            "shape=stencil(UzV2Ls5ILEhVNTIoLinKz04tz0wpyVA1dlE1MsrMy0gtyiwBslSNXVWNndPyi1LTi/JL81Ig/IJEkEoQKze/DGRCBUSfkSlIi5FBJYRraGAA5rtB1OZk5iGpNSdBLUwSptiUeHPxqDQiWiXxtuMPASADEXRpmTk5kJBHlkcPaqAQJJqMXQE=);"
            "strokeColor={stroke};shadow=1;spacingTop=-1;spacingBottom=-1;spacingLeft=-1;spacingRight=-1;"
            "points=[[1,0.5,0],[0.5,0.5,0],[0.5,0,0]];labelBackgroundColor=none;rounded=0;html=1;whiteSpace=wrap;"
        ),
    },
    "service": {
        "label": "Service",
        "default_geometry": (160, 60),
        "is_image": False,
        "style": (
            "verticalAlign=middle;align=center;overflow=width;vsdxID=12;"
            "fillColor={fill};gradientColor={grad};gradientDirection=north;"
            "shape=stencil(tVLRDsIgDPwaHkkQsvgBc/5Ho2xrRFgKuvn3gmjc5uaDiW93vWubcjBV+hY6zaTwgdxJ93gMLVM7JiXaVhOGiJiqmCprR7ohd7HHzDtIzoTO7pomDLlPFqlFilumGyEefJ+9Bu3Iu/3qBTpEjWZz6Wkusndl1EvkMKDn5AIEdHaiGaBG87iE1waaieR7rbuP8uIJcmnvLwesvNtfTojgHV+NxuT0x/o87ljKX0VVdw==);"
            "strokeColor={stroke};shadow=1;spacingTop=-1;spacingBottom=-1;spacingLeft=-1;spacingRight=-1;"
            "points=[[0.5,1,0],[0.5,0,0],[0.5,0.5,0],[1,0.5,0]];labelBackgroundColor=none;rounded=0;html=1;whiteSpace=wrap;"
        ),
    },
    "database": {
        "label": "Database",
        "default_geometry": (90, 90),
        "is_image": False,
        "style": (
            "verticalAlign=middle;align=center;overflow=width;vsdxID=13;rotation=270;"
            "fillColor={fill};gradientColor={grad};gradientDirection=north;"
            "shape=stencil(1VPLEoIwDPyaHumkLTDjGfE/OlKgY6VMqIJ/b7E+kLHePHjbbDbJbJMSUQyt7BXhMDi0BzXqyrVEbAnnumsVaucRESURRW1RNWhPXRXiXs7KGR3tee4whTrGaTYXcbgEAm7RLmiN7pZagLhU4t5n8C7lbEMhDWq8y1kGlOWBi3R8xlMiJz0kaJ102nbLeWAkNirx85LayOYtNYxK9QuafTGzNv6YHfHDqMhXftKUbt7tfH7Mn7jx4LXTWhsTTuKZjy7875YIUdsryx6sz95T4cuI8go=);"
            "strokeColor={stroke};shadow=1;spacingTop=-1;spacingBottom=-1;spacingLeft=-1;spacingRight=-1;"
            "points=[[0.5,0,0],[0.5,0,0],[1.13,0.5,0],[1,0.5,0]];labelBackgroundColor=none;rounded=0;html=1;whiteSpace=wrap;"
        ),
    },
}

# Convenience aliases so natural-language classification maps cleanly.
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
# 2. LIFECYCLE COLOUR SCHEMES  (answer: "what is its status?")
#    Only fillColor / gradientColor / strokeColor are ever swapped.
# ---------------------------------------------------------------------------

COLORS = {
    "existing_no_change": {
        "label": "Existing – No Change", "human": "green",
        "fill": "#85ca39", "grad": "#92d050", "stroke": "#ffffff",
    },
    "existing_to_change": {
        "label": "Existing – To Change", "human": "yellow",
        "fill": "#ffd21e", "grad": "#ffd83c", "stroke": "#ffffff",
    },
    "existing_decomm": {
        "label": "Existing – Decomm", "human": "grey",
        "fill": "#969696", "grad": "#a5a5a5", "stroke": "#ffffff",
    },
    "new_target_solution": {
        "label": "New Target Solution", "human": "blue",
        "fill": "#158aff", "grad": "#3399ff", "stroke": "#ffffff",
    },
    "new_sub_component": {
        "label": "New Sub Component", "human": "red",
        "fill": "#bd2f2f", "grad": "#ce3c3c", "stroke": "#ffffff",
    },
    "logical_name": {
        "label": "Logical Name", "human": "yellow label",
        "fill": "#ffd21e", "grad": "#ffd83c", "stroke": "#ffffff",
    },
    "link_to_different_function_view": {
        "label": "Link To Different Function View", "human": "yellow, black border",
        "fill": "#ffd21e", "grad": "#ffd83c", "stroke": "#404040",
    },
}

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
# 3. CONNECTOR STYLES  (answer: "what kind of message connects them?")
#    Base styles cloned from legend. {edge} and {bidir} placeholders are
#    filled by drawio_builder to add orthogonal routing, line jumps, and
#    bidirectional (request & response) arrowheads — without touching colour.
# ---------------------------------------------------------------------------

CONNECTORS = {
    "update_feed_existing": {
        "label": "Update / Feed - Existing", "stroke": "#404040", "dashed": False,
    },
    "update_feed_target": {
        "label": "Update / Feed - Target", "stroke": "#404040", "dashed": True,
    },
    "query_response_existing": {
        "label": "Query & Response - Existing", "stroke": "#ff9933", "dashed": False,
    },
    "query_response_change": {
        "label": "Query & Response - Change", "stroke": "#ff0000", "dashed": False,
    },
    "query_response_new": {
        "label": "Query & Response - New", "stroke": "#ff0000", "dashed": True,
    },
    "status_existing": {
        "label": "Status - Existing", "stroke": "#00b050", "dashed": False,
    },
    "status_target": {
        "label": "Status - Target", "stroke": "#00b050", "dashed": True,
    },
    "persistent_process_call": {
        "label": "Persistent Process Call", "stroke": "#3399ff", "dashed": False,
    },
    "response": {
        "label": "Response", "stroke": "#92d050", "dashed": False,
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
# 4. LEGEND CONTAINER STYLES (cloned from legend file)
# ---------------------------------------------------------------------------

LEGEND_OUTER = (
    "rounded=0;whiteSpace=wrap;html=1;fillColor=#ffffff;strokeColor=#a5a5a5;"
    "shadow=1;verticalAlign=top;align=left;spacingTop=6;spacingLeft=8;fontStyle=1;fontSize=11;"
)


def resolve_shape(name: str) -> str:
    key = name.strip().lower().replace(" ", "_").replace("/", "_")
    if key in SHAPES:
        return key
    if key in SHAPE_ALIASES:
        return SHAPE_ALIASES[key]
    raise KeyError(f"Unknown shape '{name}'. Valid: {list(SHAPES)} or aliases.")


def resolve_color(name: str) -> str:
    key = name.strip().lower().replace(" ", "_").replace("–", "").replace("-", "_")
    key = key.replace("__", "_").strip("_")
    if key in COLORS:
        return key
    if key in COLOR_ALIASES:
        return COLOR_ALIASES[key]
    raise KeyError(f"Unknown colour '{name}'. Valid: {list(COLORS)} or aliases.")


def resolve_connector(name: str) -> str:
    key = name.strip().lower().replace(" ", "_").replace("&", "").replace("/", "_")
    key = key.replace("__", "_").strip("_")
    if key in CONNECTORS:
        return key
    if key in CONNECTOR_ALIASES:
        return CONNECTOR_ALIASES[key]
    raise KeyError(f"Unknown connector '{name}'. Valid: {list(CONNECTORS)} or aliases.")
