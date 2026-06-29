# Scripts

Repo tooling to export the HTML artifacts in this skill to PDF and PPTX.

## Setup (once)

```bash
cd dhl-design
npm install
npx playwright install chromium
```

## Run

```bash
npm run serve        # http://localhost:3000  (terminal 1)
```

```bash
# terminal 2:
npm run pdf  -- http://localhost:3000/slides/index.html out/deck.pdf
npm run pptx -- http://localhost:3000/slides/index.html out/deck.pptx
```

Output lands in `out/` (gitignored).

## `npm run pptx` — interactive two-stage export

1. Screenshots every slide and writes `out/deck.pptx` (pixel-perfect, not text-editable).
2. Prompts:
   ```
   Convert to editable text PPTX as well? (y/N)
   ```
   - **No / just enter** → done. You have one stable, screenshot-based PPTX.
   - **Yes** → walks the DOM, overlays native PowerPoint text boxes on top of each screenshot, writes `out/deck-editable.pptx`. You now have two files: the stable one and an editable variant.

### Non-interactive flags

```bash
npm run pptx -- <url> <out>  --no-prompt    # only the screenshot PPTX
npm run pptx -- <url> <out>  --editable     # both files, no prompt
```

### How the editable overlay works

The editable file uses the screenshot as a background image, then places a native PowerPoint text box at the exact coordinates of every visible text leaf in the DOM, with matching font / size / weight / color. The overlay text covers the screenshot text perfectly when untouched — visually identical to the screenshot-only file.

When edited:
- New text replaces the visible text in that text box.
- The original screenshot text is *underneath* — if the edit is shorter, the leftover screenshot text peeks out.
- Fix: select the text box → Shape Format → Shape Fill → match slide background.

For decks that will be heavily re-edited in PowerPoint, prefer editing the source HTML and re-exporting. The editable PPTX is meant for last-mile copy tweaks, not deep authoring.

## How the scripts work

- **`html-to-pdf.mjs`** — Playwright opens the URL, drops `deck-stage`'s scale, applies `@page { size: 1920px 1080px }`, then `page.pdf()` writes one PDF page per slide.
- **`html-to-pptx.mjs`** — Stage 1: iterates slides via `deck-stage.goTo(n)`, screenshots each `<section>` at 1920×1080@2x, embeds as full-bleed PNGs. Speaker notes from `<script id="speaker-notes">` attach to the notes pane. Stage 2 (on confirmation): re-uses the same screenshots, walks the DOM for text leaves, and emits native PowerPoint text boxes at matching coordinates.

## Caveats

- **Deck-stage required.** The scripts assume the HTML uses the `<deck-stage>` web component. For non-deck HTML, modify the section selector.
- **Custom fonts.** The editable layer names the original font (e.g. "Delivery"). PowerPoint substitutes if it's not installed locally. Distribute the font files alongside the PPTX, or install Delivery in PowerPoint.
- **File size.** Screenshot decks at 1920×1080@2x are ~700KB per slide. A 30-slide deck is ~20MB. The editable variant adds ~5% on top for the text-box XML.
- **Network.** `waitUntil: "networkidle"` + 800ms buffer covers Lucide icons and remote fonts. If a slide shows missing glyphs, bump the timeout in the script.
