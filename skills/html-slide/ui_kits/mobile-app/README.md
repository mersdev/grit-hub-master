# DHL Mobile — Recipient & Sender App UI Kit

A pixel-faithful **brand language** recreation of the DHL recipient/sender mobile experience. Four canonical screens, each shown as a static artboard inside a pannable design canvas.

> No DHL mobile app source code was provided. The flows here are reconstructed from the brand kit + DHL's well-known consumer mobile patterns (My DHL+, On Demand Delivery, Post & DHL App). It is brand-faithful, not source-identical.

## Screens

1. **Parcels (home / inbox)** — list of incoming and outgoing parcels with status chips and ETAs.
2. **Parcel detail** — vertical tracking timeline with full event history and delivery action.
3. **Schedule delivery** — date / time / location chooser for redelivery or pickup.
4. **Locker pickup** — QR code + locker address + access code.

## Components

In `components-m.jsx`:
- `MobileHeader` — yellow header bar with logo + actions
- `ParcelRow` — list item for a parcel
- `VTimeline` — vertical stepper for tracking
- `BottomNav` — 4-tab bottom bar
- `QRPanel` — full-bleed yellow QR panel
- `ScheduleOption` — radio-style picker row
- `MStatusChip` / `MButton` / `MLabel` — mobile-sized variants
