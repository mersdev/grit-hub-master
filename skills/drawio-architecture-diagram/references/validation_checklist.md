# DHL Draw.io Validation Checklist

Run `python scripts/validate_drawio.py <file>.drawio` for the automated pass, then
confirm the judgement items below.

## Automated (validator enforces)

- [ ] File is well-formed XML and opens in diagrams.net.
- [ ] All `mxCell` ids are unique.
- [ ] Every vertex has `<mxGeometry>` with width and height.
- [ ] Every edge has source+target (or explicit source/target points).
- [ ] Every node fill is an approved lifecycle colour (or actor image / none).
- [ ] Every edge stroke is an approved connector colour.
- [ ] No node uses a non-catalogued `shape=stencil(...)`.
- [ ] No nodes overlap in their bounding boxes.
- [ ] In dense diagrams (>4 edges), edges use orthogonal routing or waypoints.

## Style compliance (judgement)

- [ ] Each node = one approved shape + one approved lifecycle colour.
- [ ] Shape stencils and `points` were preserved; only colour tokens changed.
- [ ] Databases are cylinders, services are service shapes, orchestration is the
      orchestration shape — none collapsed to rectangles.
- [ ] Connector dash/colour come only from the approved table.
- [ ] `bidirectional` used for request/response instead of two parallel lines.
- [ ] Model carries `jumpStyle="arc" jumpSize="8"` for crossing-line arcs.

## Readability (judgement)

- [ ] Primary flow reads left-to-right (or top-to-bottom for stacks).
- [ ] Labels are short; detail is in notes, not crammed into boxes.
- [ ] Zones/grouping make the story obvious for the intended audience.
- [ ] A legend is present for stakeholder-facing or multi-state diagrams.
- [ ] No avoidable crossing or overlapping connectors.

## Semantics (judgement)

- [ ] Lifecycle colour of every node matches the real change story.
- [ ] Connector type of every edge matches the real interaction.
- [ ] Uncertain lifecycle defaulted to Existing – To Change (yellow), not green.
- [ ] Assumptions were stated to the user.
