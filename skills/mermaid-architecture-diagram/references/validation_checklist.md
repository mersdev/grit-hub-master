# Mermaid DHL Validation Checklist

Run `python scripts/validate_mermaid.py <file>.mmd` for the automated pass, then
confirm the judgement items.

## Automated (validator enforces)

- [ ] Syntax: passes the best available engine — `mermaid.parse()` via
      `node scripts/mmparse.mjs` (authoritative, headless) preferred; else `mmdc`
      (authoritative if a browser is present); else the heuristic structural check.
      The output states which engine ran.
- [ ] Every `classDef` fill is an approved DHL lifecycle colour.
- [ ] Every `linkStyle` stroke is an approved connector colour.
- [ ] No inline `style … fill:` uses a non-palette colour.
- [ ] (Flowchart) nodes are assigned lifecycle classes — colour scheme present.
- [ ] For a **plain** (non-DHL) type, validate with `--plain` so DHL colour
      compliance is skipped; syntax must still pass.

## Type & structure (judgement)

- [ ] Diagram type matches intent (flowchart / sequence / state / er / c4).
- [ ] Correct header line; optional title front matter well-formed.
- [ ] Node labels with special characters are quoted.
- [ ] Each `classDef` defined once; `class` assignments reference real ids.
- [ ] `linkStyle` indices match edge declaration order.
- [ ] subgraph/end balanced.

## DHL semantics (judgement)

- [ ] Shapes echo DHL: database = cylinder, service = rounded, orchestration =
      hexagon, actor = stadium (or actor/Person in sequence/C4).
- [ ] Lifecycle colour of each node matches the real change story.
- [ ] Connector line style + colour match the real interaction.
- [ ] Bidirectional used for request/response rather than two separate edges.
- [ ] Uncertain lifecycle defaulted to Existing – To Change.

## Readability (judgement)

- [ ] Sensible direction (LR for architecture, TB for hierarchy/decisions).
- [ ] Zones via subgraphs where helpful; labels short.
- [ ] Legend present on stakeholder-facing flowcharts.
- [ ] Edge count kept manageable (Mermaid auto-routes; fewer cross-zone edges read
      better).

## Honest-limits note

- [ ] Where relevant, told the user that Mermaid conveys DHL lifecycle by colour and
      connectors by line style and cannot reproduce the custom DHL stencils; offered
      the draw.io skill when richer styling/editing is needed.
