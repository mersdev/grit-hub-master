# Style Presets Reference

This deployment is intentionally restricted to a single style: **DHL Logistics Intelligence**.

**Viewport CSS:** For mandatory base styles, see [viewport-base.css](viewport-base.css). Include in every presentation.

---

## DHL Logistics Intelligence (Only Preset)

**Vibe:** Corporate, urgent, analytical, industrial-strength

**Layout Direction:**
- Structured 12-column desktop grid, 4-column mobile grid
- Sharp rectangular cards and sections (`border-radius: 0`)
- Yellow hero/surface areas with white/neutral data containers
- Strong red accents for actions, highlights, and critical states

**Typography:**
- Display: `Delivery Condensed` from `skills/frontend-slides/assets/fonts/` (Black/Light)
- Body: `Delivery` from `skills/frontend-slides/assets/fonts/` (Regular/Bold)
- PDF-template mapping:
  - Cover title visual weight equivalent to Delivery Condensed Black
  - Cover subline visual weight equivalent to Delivery Condensed Light
  - Body hierarchy equivalent to Delivery 12 pt / 18 pt pattern (scaled responsively with `clamp()`)
  - If in doubt, choose larger text and split content across slides rather than shrinking type below readable size

**Colors:**
```css
:root {
    --surface: #f9f9f9;
    --surface-container-lowest: #ffffff;
    --surface-container: #eeeeee;
    --surface-container-highest: #e2e2e2;
    --on-surface: #1a1c1c;
    --outline: #80765f;

    --primary: #745b00;
    --primary-container: #ffcc00;
    --on-primary: #ffffff;
    --on-primary-container: #6f5700;

    --secondary: #bb001e;
    --secondary-container: #e5192e;
    --on-secondary: #ffffff;

    --tertiary: #5e5e5e;
    --background: #f9f9f9;
}
```

**Component Rules:**
- Buttons: solid red primary, bordered secondary, no rounded corners
- Cards: white or light-neutral with 2px black/red borders
- Inputs: underlined or boxed with 2px border; yellow/red focus
- Chips/status: rectangular grade labels (excellent/good/fair/incomplete)
- Progress: thick linear red bars (no circular loaders)

**Depth Rules:**
- Prefer flat surfaces and 2px strong outlines
- Avoid soft shadows
- If depth is needed, use hard 4px offset shadow with no blur

**Icon & Visual Sourcing Rule (Strict):**
When visuals are required:
1. Use only local images from `skills/frontend-slides/assets/images/` unless the user explicitly supplies additional files.
2. Keep one consistent visual family across the deck.
3. Prefer simple, geometric, high-contrast visuals compatible with DHL corporate templates.
4. Do not use Thiings API or HAR-derived sources.

**Hero Rule (DHL Required):**
- Hero/title slide must be vertically centered.
- Hero/title slide must be the first slide in the deck.
- Any slide that contains only a centered title must use the hero slide pattern.
- If hero uses image background, source it from `skills/frontend-slides/assets/images/`.
- Hero title color treatment must match the reference family:
  - dark ink on yellow hero OR solid red on light neutral backgrounds.
  - In light theme: title color must be DHL red (`#bb001e`).
  - In dark theme: title color must be white (`#ffffff`).
- If hero background is DHL yellow (`#ffcc00`), title color must be DHL red (`#bb001e`) regardless of variant naming.
- Add `skills/frontend-slides/assets/images/banner.png` pinned at the bottom of the hero slide.
- Prefer a left-aligned text block over image + dark overlay, similar to executive keynote cover style.

**Alignment Rule (Strict):**
- Hero text block: left-aligned, anchored to the same horizontal inset across hero slides.
- Vertical rhythm: internal-use label at top-left, content block centered vertically, metadata at bottom-right, banner pinned bottom.
- Do not alternate hero alignment between slides unless the user explicitly asks.

**Reference Design Lock (Strict):**
- Follow the provided reference images for layout language and component style.
- Match color palette and composition patterns exactly; do not introduce alternate themes.
- Font sizes may be adjusted responsively for fit/readability, but color roles and layout style must remain consistent with the references.

**Diagram Rule (DHL Required):**
- Include at least one diagram slide in every deck (process flow, architecture, timeline, or system map).
- Prefer structured rectangles + connector arrows in DHL yellow/red/neutral palette.
- Do not replace diagrams with bullet-only explanation.

**Template Chrome Rule (PDF-aligned):**
- Include `FOR INTERNAL USE` label in header area.
- Include footer metadata line in the style: `DHL | Presentation title | Location | xx Month 20xx`.
- Keep this chrome subtle but present across slides unless the user explicitly asks to remove it.

**PDF Layout Family Rule (Strict):**
- Generated decks should mirror the DHL PDF slide families:
  - Cover hero
  - Agenda
  - Divider (gradient)
  - Divider (image)
  - Standard content
  - Diagram/process
  - Charts/tables
  - Quote-on-image
- Do not output only repeated generic bullet slides.

**Minimum Readability Rule (Strict):**
- Cover title must read large at first glance (no undersized hero headings).
- Standard content text must remain comfortably readable from presentation distance.
- Use additional slides to control density; do not compress typography to force content fit.

**GSAP Rule:**
- If smoother transitions are requested, use GSAP (`https://gsap.com/`) patterns.
- Recommended include: `https://cdn.jsdelivr.net/npm/gsap@3/dist/gsap.min.js`
- Prefer `gsap.timeline()` and `fromTo()` with staggered reveals and `power3.out`/`expo.out` easing.
- Always keep `prefers-reduced-motion` fallback.

---

## Do Not Use

- Any alternate preset from the upstream repository
- Rounded "friendly" UI motifs
- Purple-gradient-on-white aesthetics
- Soft glassmorphism or decorative illustrations that conflict with logistics-corporate tone

