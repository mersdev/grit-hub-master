# Creative diagram validation checklist

The creative-mode gate is **structural, not stylistic** — it never checks colours, so any
aesthetic passes as long as the layout is tidy. Run:

```
python scripts/validate_creative_drawio.py <file>.drawio
```

It must print `CREATIVE TIDINESS: PASSED`. The checks below are what it enforces; the
manual notes are what you should eyeball before delivering.

## Automated checks (the gate)

- [ ] **Well-formed XML** — parses cleanly.
- [ ] **Unique ids** — no duplicate `mxCell` ids.
- [ ] **Geometry present** — every vertex has width + height; every edge has source +
      target.
- [ ] **On-grid** — every node x / y / width / height is a multiple of `GRID` (8).
      (Pure `text;` labels are exempt — they are typographic, not layout boxes.)
- [ ] **No overlaps** — no two solid nodes share area. Band/zone containers, groups, and
      text labels are skipped (a node sitting inside its band is expected).
- [ ] **Orthogonal routing** — every edge uses `edgeStyle=orthogonalEdgeStyle`.
- [ ] **No edge-through-node** — no connector passes through the interior of a node that
      is not its own source or target.

## Manual review (judgement, not automated)

- [ ] **One aesthetic, committed.** A single clear direction (dark editorial, light
      minimal, etc.), not a mix. Palette defined in one block, applied consistently.
- [ ] **Colour segregates clearly.** One accent per band/role; the eye groups instantly.
      If colour encodes a category and more than three appear, a small key is present in
      a reserved margin.
- [ ] **Consistent sizing.** Nodes of the same content type share a height; gutters are
      even.
- [ ] **Readable text.** Title and subtitle in two distinct shades/weights; text contrasts
      with its fill (dark ink on light tint, or light text on a saturated fill).
- [ ] **Tidy spine.** Connectors run straight where possible; waypoints only where needed
      to avoid a crossing.
- [ ] **No DHL leakage.** No lifecycle colour meaning, no DHL stencils, no mandatory
      full-catalogue legend.

## Common failures

| Symptom | Fix |
|---|---|
| `off-grid …` | round the coordinate to a multiple of 8 (the builder's `snap()` helper does this). |
| `overlap A <-> B` | widen the gap or shrink a card; check the band width fits its cards + gutters. |
| `non-orthogonal edge` | use the `flow()` helper / add `edgeStyle=orthogonalEdgeStyle`. |
| `edge … crosses node` | add a waypoint to route the connector around the node. |
