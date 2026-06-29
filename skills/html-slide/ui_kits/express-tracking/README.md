# Express Tracking — Web UI Kit

A pixel-faithful recreation of DHL's public-facing **track & ship** flow. The visual vocabulary is reconstructed from the brand kit (master template, photography, typography, dynamic elements) and DHL's well-known web patterns: yellow header bar, red CTA, large hero with photography, white card-driven content blocks, and a horizontal tracking timeline.

> **No code source was provided** for `dhl.com` — this kit is built off the brand kit + reference to publicly-known DHL.com layout patterns. It is brand-faithful, not source-identical. If a codebase becomes available we'll iterate.

## What's in here

- `index.html` — the live interactive prototype. Click through: Home → Track input → Result → Shipment detail.
- `components.jsx` — every React component used by the prototype, exported to `window` for cross-script reuse.
- `tracking.jsx` — page-level views (Home / Tracking result / Detail).

## Screens covered

1. **Home / Hero** — yellow hero, tracking input, four service cards.
2. **Track result** — horizontal timeline, current status, ETA, address pair, action row.
3. **Shipment detail** — full event history, sender / recipient, weight, service.
4. **Get a Quote (modal)** — origin / destination / weight inputs.
5. **Find a Location (modal)** — search + nearby list.

## Components

- `Header` — top nav, logo, country switcher, account
- `HeroTrack` — yellow hero block with tracking input
- `ServiceCard` — 4-col service-line card
- `TrackingInput` — single tracking number input with submit
- `Timeline` — horizontal stepper for tracking status
- `EventRow` — event list row (datetime, location, code, copy)
- `StatusChip` — pill chip for shipment status
- `Button` (primary / secondary / ghost / link, all states)
- `Field` / `Select` — form inputs
- `Modal` — overlay dialog
- `Footer` — yellow footer block with links
