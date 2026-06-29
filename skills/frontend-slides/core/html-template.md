# HTML Presentation Template

Reference architecture for generating slide presentations. Every presentation follows this structure.

## Base HTML Structure

```html
<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>Presentation Title</title>

    <style>
      @font-face {
        font-family: "Delivery";
        src: url("../skills/frontend-slides/assets/fonts/DELIVERY_RG.TTF") format("truetype");
        font-weight: 400;
        font-style: normal;
      }
      @font-face {
        font-family: "Delivery";
        src: url("../skills/frontend-slides/assets/fonts/DELIVERY_BD.TTF") format("truetype");
        font-weight: 700;
        font-style: normal;
      }
      @font-face {
        font-family: "Delivery Condensed";
        src: url("../skills/frontend-slides/assets/fonts/DELIVERY_CDLT.TTF") format("truetype");
        font-weight: 300;
        font-style: normal;
      }
      @font-face {
        font-family: "Delivery Condensed";
        src: url("../skills/frontend-slides/assets/fonts/DELIVERY_CDBLK.TTF") format("truetype");
        font-weight: 900;
        font-style: normal;
      }

      /* ===========================================
           CSS CUSTOM PROPERTIES (THEME)
           Change these to change the whole look
           =========================================== */
      :root {
        /* Colors — DHL reference-locked palette */
        --bg-primary: #f9f9f9;
        --bg-secondary: #eeeeee;
        --text-primary: #1a1c1c;
        --text-secondary: #5e5e5e;
        --accent: #bb001e;
        --accent-glow: rgba(187, 0, 30, 0.22);

        /* Typography — MUST use clamp() */
        --font-display: "Delivery Condensed", "Delivery", sans-serif;
        --font-body: "Delivery", sans-serif;
        --title-color-light: #bb001e;
        --title-color-dark: #ffffff;
        --title-color-current: var(--title-color-light);
        --title-size: clamp(2.4rem, 7vw, 6rem);
        --subtitle-size: clamp(1.1rem, 2.4vw, 1.7rem);
        --body-size: clamp(1rem, 1.8vw, 1.35rem);

        /* Spacing — MUST use clamp() */
        --slide-padding: clamp(1.5rem, 4vw, 4rem);
        --content-gap: clamp(1rem, 2vw, 2rem);

        /* Animation */
        --ease-out-expo: cubic-bezier(0.16, 1, 0.3, 1);
        --duration-normal: 0.6s;
      }

      /* ===========================================
           BASE STYLES
           =========================================== */
      * {
        margin: 0;
        padding: 0;
        box-sizing: border-box;
      }
      body {
        font-family: var(--font-body);
      }
      h1,
      h2,
      h3,
      h4,
      h5,
      h6 {
        font-family: var(--font-display);
      }
      body.theme-light {
        --title-color-current: var(--title-color-light);
      }
      body.theme-dark {
        --title-color-current: var(--title-color-dark);
      }
      @media (prefers-color-scheme: dark) {
        body:not(.theme-light) {
          --title-color-current: var(--title-color-dark);
        }
      }

      /* --- PASTE viewport-base.css CONTENTS HERE --- */

      /* ===========================================
           ANIMATIONS
           Trigger via .visible class (added by JS on scroll)
           =========================================== */
      .reveal {
        opacity: 0;
        transform: translateY(30px);
        transition:
          opacity var(--duration-normal) var(--ease-out-expo),
          transform var(--duration-normal) var(--ease-out-expo);
      }

      .slide.visible .reveal {
        opacity: 1;
        transform: translateY(0);
      }

      /* Stagger children for sequential reveal */
      .reveal:nth-child(1) {
        transition-delay: 0.1s;
      }
      .reveal:nth-child(2) {
        transition-delay: 0.2s;
      }
      .reveal:nth-child(3) {
        transition-delay: 0.3s;
      }
      .reveal:nth-child(4) {
        transition-delay: 0.4s;
      }

      /* ... preset-specific styles ... */

      /* ===========================================
           HERO SLIDE PATTERN (DHL)
           - Background image from skills/frontend-slides/assets/images/
           - Vertically centered title
           - Optional yellow gradient title style OR red title style
           - Banner locked to bottom when hero image is used
           =========================================== */
      .hero-slide {
        justify-content: center;
        align-items: flex-start;
        text-align: left;
        padding: 0;
        background-size: cover;
        background-position: center center;
        background-repeat: no-repeat;
      }
      .hero-slide::before {
        content: "";
        position: absolute;
        inset: 0;
        background: linear-gradient(
          180deg,
          rgba(0, 0, 0, 0.52) 0%,
          rgba(0, 0, 0, 0.62) 100%
        );
      }
      .hero-content {
        position: relative;
        z-index: 2;
        width: min(92vw, 1280px);
        margin-inline: auto;
        padding: clamp(1rem, 3vw, 3rem);
        padding-bottom: clamp(6rem, 14vh, 12rem);
      }
      .hero-title {
        font-size: clamp(2rem, 8vw, 6rem);
        line-height: 0.98;
        letter-spacing: -0.02em;
      }
      .hero-slide.dark-hero .hero-title,
      .hero-slide.dark-hero .hero-kicker,
      .hero-slide.dark-hero .hero-subtitle,
      .hero-slide.dark-hero .internal-use,
      .hero-slide.dark-hero .slide-meta {
        color: #ffffff;
      }
      .hero-kicker {
        font-size: clamp(0.65rem, 1vw, 0.9rem);
        letter-spacing: 0.08em;
        text-transform: uppercase;
        color: #6b5d00;
        margin-bottom: clamp(0.75rem, 1.5vw, 1.2rem);
      }
      .hero-subtitle {
        margin-top: clamp(0.8rem, 1.8vw, 1.4rem);
        font-size: clamp(1.2rem, 3vw, 2.4rem);
        color: #6b5d00;
      }
      .hero-caption {
        margin-top: clamp(0.45rem, 1vw, 0.85rem);
        font-size: clamp(1rem, 2vw, 1.8rem);
        color: #4f5a66;
      }
      .hero-title.yellow-gradient {
        color: transparent;
        background: linear-gradient(90deg, #ffcc00 0%, #fff0a3 100%);
        -webkit-background-clip: text;
        background-clip: text;
        text-shadow: 0 4px 22px rgba(0, 0, 0, 0.28);
      }
      .hero-title.ink-solid {
        color: var(--title-color-current);
        font-weight: 800;
      }
      .hero-title.red-solid {
        color: var(--title-color-current);
        text-shadow: 0 4px 0 rgba(120, 0, 0, 0.25);
      }
      /* Enforce: yellow hero backgrounds always use DHL red title in light theme */
      .hero-slide.no-overlay .hero-title,
      .hero-slide[style*="#ffcc00"] .hero-title,
      .hero-slide[style*="--primary-container"] .hero-title {
        color: var(--title-color-light);
      }
      body.theme-dark .hero-title.red-solid {
        text-shadow: none;
      }
      @media (prefers-color-scheme: dark) {
        body:not(.theme-light) .hero-title.red-solid {
          text-shadow: none;
        }
      }
      .hero-banner {
        position: absolute;
        left: 2%;
        right: 2%;
        bottom: 2.5%;
        width: 96%;
        height: auto;
        z-index: 3;
      }

      /* PDF-style presentation chrome */
      .internal-use {
        position: absolute;
        top: clamp(0.5rem, 1.4vw, 1rem);
        left: clamp(0.75rem, 2vw, 1.5rem);
        z-index: 5;
        font-size: clamp(0.6rem, 1vw, 0.85rem);
        font-weight: 700;
        letter-spacing: 0.08em;
        color: #ffffff;
        text-transform: uppercase;
      }
      .slide-meta {
        position: absolute;
        right: clamp(0.75rem, 2vw, 1.5rem);
        bottom: clamp(0.6rem, 1.6vw, 1rem);
        z-index: 5;
        font-size: clamp(0.58rem, 0.95vw, 0.82rem);
        font-weight: 500;
        color: #f4f4f4;
      }
      .slide-meta.dark {
        color: #4f5a66;
      }

      /* Layout: reference-like split text + image */
      .content-split {
        display: grid;
        grid-template-columns: 58% 42%;
        height: 100%;
      }
      .content-panel {
        background: #e6e6e6;
        padding: clamp(1.6rem, 3vw, 2.8rem);
      }
      .photo-panel {
        position: relative;
        background-size: cover;
        background-position: center;
      }

      /* Layout: full-bleed image with floating info boxes */
      .image-info-slide {
        padding: 0;
        color: #fff;
      }
      .image-info-slide::before {
        content: "";
        position: absolute;
        inset: 0;
        background: linear-gradient(
          180deg,
          rgba(0, 0, 0, 0.52) 0%,
          rgba(0, 0, 0, 0.3) 44%,
          rgba(0, 0, 0, 0.45) 100%
        );
        z-index: 1;
      }
      .image-info-content {
        position: relative;
        z-index: 2;
        width: min(92vw, 1220px);
        margin: 0 auto;
        padding: clamp(2rem, 4vw, 3rem);
        padding-top: clamp(4.4rem, 9vh, 6rem);
      }
      .info-grid {
        display: grid;
        grid-template-columns: repeat(3, minmax(0, 1fr));
        gap: clamp(0.8rem, 1.6vw, 1.2rem);
        margin-top: clamp(1.4rem, 3vh, 2.6rem);
      }
      .info-box {
        background: rgba(236, 236, 236, 0.96);
        color: #111;
        padding: clamp(0.9rem, 1.6vw, 1.2rem);
      }
      .info-box h4 {
        font-size: clamp(1rem, 1.6vw, 1.45rem);
        margin-bottom: 0.3rem;
      }

      /* Diagram slide baseline */
      .diagram-stage {
        width: min(94vw, 1180px);
        margin-inline: auto;
        display: grid;
        grid-template-columns: repeat(3, minmax(0, 1fr));
        gap: clamp(0.5rem, 1.4vw, 1rem);
        align-items: center;
      }
      .diagram-node {
        border: 2px solid #1a1c1c;
        background: #ffcc00;
        color: #1a1c1c;
        font-weight: 700;
        text-align: center;
        padding: clamp(0.6rem, 1.6vw, 1rem);
      }
      .diagram-arrow {
        text-align: center;
        font-size: clamp(1.1rem, 2vw, 1.8rem);
        color: #bb001e;
        font-weight: 800;
      }
    </style>
  </head>
  <body>
    <!-- Optional: Progress bar -->
    <div class="progress-bar"></div>

    <!-- Optional: Navigation dots -->
    <nav class="nav-dots"><!-- Generated by JS --></nav>

    <!-- Slides -->
    <section
      class="slide title-slide hero-slide"
      style="background: #ffcc00;"
    >
      <div class="internal-use">FOR INTERNAL USE</div>
      <div class="hero-content">
        <p class="reveal hero-kicker">FOR INTERNAL USE</p>
        <h1 class="reveal hero-title ink-solid">Welcome to<br />Confluence</h1>
        <p class="reveal hero-subtitle">Your Team Knowledge Hub</p>
        <p class="reveal hero-caption">New Hire Onboarding Guide</p>
      </div>
      <div class="slide-meta dark">DHL | Confluence Onboarding | May 2026</div>
      <img
        src="../skills/frontend-slides/assets/images/banner.png"
        alt=""
        class="hero-banner"
        aria-hidden="true"
      />
    </section>

    <section class="slide content-split">
      <div class="content-panel">
        <div class="internal-use" style="color: #8c8c8c">FOR INTERNAL USE</div>
        <div class="slide-content" style="padding: 0; justify-content: flex-start">
          <h2 class="reveal" style="color: #c40016">Double headline with one or two lines, Delivery Bold, 18 pt</h2>
          <p class="reveal">Action title, multiple lines, Delivery Regular, 15 pt, format via indent list level</p>
        </div>
      </div>
      <div
        class="photo-panel"
        style="background-image: url('../skills/frontend-slides/assets/images/hero-port-logistics.jpg')"
      ></div>
    </section>

    <section
      class="slide image-info-slide"
      style="background-image: url('../skills/frontend-slides/assets/images/hero-air-cargo-network.jpg'); background-size: cover; background-position: center;"
    >
      <div class="image-info-content">
        <h2 class="reveal">Double headline with one or two lines, Delivery Bold, 18 pt</h2>
        <div class="info-grid reveal">
          <div class="info-box">
            <h4>Info box Headline</h4>
            <p>Use optional flexibly placeable info boxes to display additional information.</p>
          </div>
          <div class="info-box">
            <h4>Info box Headline</h4>
            <p>Use optional flexibly placeable info boxes to display additional information.</p>
          </div>
          <div class="info-box">
            <h4>Info box Headline</h4>
            <p>Use optional flexibly placeable info boxes to display additional information.</p>
          </div>
        </div>
      </div>
      <div class="internal-use">FOR INTERNAL USE</div>
      <div class="slide-meta">DHL | Presentation title | Location | xx Month 20xx</div>
    </section>

    <!-- More slides... -->

    <script>
      /* ===========================================
           SLIDE PRESENTATION CONTROLLER
           =========================================== */
      class SlidePresentation {
        constructor() {
          this.slides = document.querySelectorAll(".slide");
          this.currentSlide = 0;
          this.isWheelLocked = false;
          this.setupIntersectionObserver();
          this.setupKeyboardNav();
          this.setupTouchNav();
          this.setupWheelNav();
          this.setupProgressBar();
          this.setupNavDots();
        }

        setupIntersectionObserver() {
          // Add .visible class when slides enter viewport
          // Triggers CSS animations efficiently
        }

        setupKeyboardNav() {
          // Arrow keys, Space, Page Up/Down
        }

        setupTouchNav() {
          // Touch/swipe support for mobile
        }

        setupWheelNav() {
          // One wheel gesture = one slide jump (down -> next, up -> previous).
          // This makes first scroll from hero reliably move to slide 2.
          window.addEventListener(
            "wheel",
            (e) => {
              if (this.isWheelLocked) return;
              if (Math.abs(e.deltaY) < 12) return;
              e.preventDefault();

              this.isWheelLocked = true;
              if (e.deltaY > 0) this.goToSlide(this.currentSlide + 1);
              else this.goToSlide(this.currentSlide - 1);

              setTimeout(() => {
                this.isWheelLocked = false;
              }, 550);
            },
            { passive: false },
          );
        }

        setupProgressBar() {
          // Update progress bar on scroll
        }

        setupNavDots() {
          // IMPORTANT: Always clear before building — if outerHTML was
          // captured while dots were rendered, re-opening the file would
          // append a duplicate set on top of the existing ones.
          this.navDotsContainer.innerHTML = "";
          // Generate and manage navigation dots
        }
      }

      new SlidePresentation();
    </script>
  </body>
</html>
```

## Required JavaScript Features

Every presentation must include:

1. **SlidePresentation Class** — Main controller with:
   - Keyboard navigation (arrows, space, page up/down)
   - Touch/swipe support
   - Mouse wheel navigation
   - Progress bar updates
   - Navigation dots

2. **Intersection Observer** — For scroll-triggered animations:
   - Add `.visible` class when slides enter viewport
   - Trigger CSS transitions efficiently

**Wheel behavior requirement:** Scrolling down once from the hero must move to the next slide (slide 2), with a short lock/debounce to avoid skipping multiple slides per gesture.

3. **Optional Enhancements** (match to chosen style):
   - Custom cursor with trail
   - Particle system background (canvas)
   - Parallax effects
   - 3D tilt on hover
   - Magnetic buttons
   - Counter animations

4. **Inline Editing** (only if user opted in during Phase 1 — skip entirely if they said No):
   - Edit toggle button (hidden by default, revealed via hover hotzone or `E` key)
   - Auto-save to localStorage
   - Export/save file functionality
   - See "Inline Editing Implementation" section below

## Inline Editing Implementation (Opt-In Only)

**If the user chose "No" for inline editing in Phase 1, do NOT generate any edit-related HTML, CSS, or JS.**

**Do NOT use CSS `~` sibling selector for hover-based show/hide.** The CSS-only approach (`edit-hotzone:hover ~ .edit-toggle`) fails because `pointer-events: none` on the toggle button breaks the hover chain: user hovers hotzone -> button becomes visible -> mouse moves toward button -> leaves hotzone -> button disappears before click.

**Required approach: JS-based hover with 400ms delay timeout.**

HTML:

```html
<div class="edit-hotzone"></div>
<button class="edit-toggle" id="editToggle" title="Edit mode (E)">✏️</button>
```

CSS (visibility controlled by JS classes only):

```css
/* Do NOT use CSS ~ sibling selector for this!
   pointer-events: none breaks the hover chain.
   Must use JS with delay timeout. */
.edit-hotzone {
  position: fixed;
  top: 0;
  left: 0;
  width: 80px;
  height: 80px;
  z-index: 10000;
  cursor: pointer;
}
.edit-toggle {
  opacity: 0;
  pointer-events: none;
  transition: opacity 0.3s ease;
  z-index: 10001;
}
.edit-toggle.show,
.edit-toggle.active {
  opacity: 1;
  pointer-events: auto;
}
```

JS (three interaction methods):

```javascript
// 1. Click handler on the toggle button
document.getElementById("editToggle").addEventListener("click", () => {
  editor.toggleEditMode();
});

// 2. Hotzone hover with 400ms grace period
const hotzone = document.querySelector(".edit-hotzone");
const editToggle = document.getElementById("editToggle");
let hideTimeout = null;

hotzone.addEventListener("mouseenter", () => {
  clearTimeout(hideTimeout);
  editToggle.classList.add("show");
});
hotzone.addEventListener("mouseleave", () => {
  hideTimeout = setTimeout(() => {
    if (!editor.isActive) editToggle.classList.remove("show");
  }, 400);
});
editToggle.addEventListener("mouseenter", () => {
  clearTimeout(hideTimeout);
});
editToggle.addEventListener("mouseleave", () => {
  hideTimeout = setTimeout(() => {
    if (!editor.isActive) editToggle.classList.remove("show");
  }, 400);
});

// 3. Hotzone direct click
hotzone.addEventListener("click", () => {
  editor.toggleEditMode();
});

// 4. Keyboard shortcut (E key, skip when editing text)
document.addEventListener("keydown", (e) => {
  if (
    (e.key === "e" || e.key === "E") &&
    !e.target.getAttribute("contenteditable")
  ) {
    editor.toggleEditMode();
  }
});
```

**CRITICAL: `exportFile()` must strip edit state before capturing outerHTML.**

When the user presses Ctrl+S in edit mode, `document.documentElement.outerHTML` captures the live DOM —
including `body.edit-active`, `contenteditable="true"` on every text element, and `.active`/`.show` classes on
the toggle button and banner. Anyone opening the saved file sees dashed outlines, a checkmark button, and an
edit banner, as if permanently stuck in edit mode.

Always implement `exportFile()` like this:

```javascript
exportFile() {
    // Temporarily strip edit state so the saved file opens cleanly
    const editableEls = Array.from(document.querySelectorAll('[contenteditable]'));
    editableEls.forEach(el => el.removeAttribute('contenteditable'));
    document.body.classList.remove('edit-active');

    // Also strip UI classes from toggle button and banner
    const editToggle = document.getElementById('editToggle');
    const editBanner = document.querySelector('.edit-banner');
    editToggle?.classList.remove('active', 'show');
    editBanner?.classList.remove('active', 'show');

    const html = '<!DOCTYPE html>\n' + document.documentElement.outerHTML;

    // Restore edit state so the user can keep editing
    document.body.classList.add('edit-active');
    editableEls.forEach(el => el.setAttribute('contenteditable', 'true'));
    editToggle?.classList.add('active');
    editBanner?.classList.add('active');

    const blob = new Blob([html], { type: 'text/html' });
    const a = document.createElement('a');
    a.href = URL.createObjectURL(blob);
    a.download = 'presentation.html';
    a.click();
    URL.revokeObjectURL(a.href);
}
```

## Image Pipeline (Skip If No Images)

If user chose "No images" in Phase 1, skip this entirely. If images were provided, process them before generating HTML.

**Dependency:** `pip install Pillow`

### Image Processing

```python
from PIL import Image, ImageDraw

# Circular crop (for logos on modern/clean styles)
def crop_circle(input_path, output_path):
    img = Image.open(input_path).convert('RGBA')
    w, h = img.size
    size = min(w, h)
    left, top = (w - size) // 2, (h - size) // 2
    img = img.crop((left, top, left + size, top + size))
    mask = Image.new('L', (size, size), 0)
    ImageDraw.Draw(mask).ellipse([0, 0, size, size], fill=255)
    img.putalpha(mask)
    img.save(output_path, 'PNG')

# Resize (for oversized images that inflate HTML)
def resize_max(input_path, output_path, max_dim=1200):
    img = Image.open(input_path)
    img.thumbnail((max_dim, max_dim), Image.LANCZOS)
    img.save(output_path, quality=85)
```

| Situation                        | Operation                     |
| -------------------------------- | ----------------------------- |
| Square logo on rounded aesthetic | `crop_circle()`               |
| Image > 1MB                      | `resize_max(max_dim=1200)`    |
| Wrong aspect ratio               | Manual crop with `img.crop()` |

Save processed images with `_processed` suffix. Never overwrite originals.

### Image Placement

**Use direct file paths** (not base64) — presentations are viewed locally:

```html
<img src="assets/logo_round.png" alt="Logo" class="slide-image logo" />
<img
  src="assets/screenshot.png"
  alt="Screenshot"
  class="slide-image screenshot"
/>
```

```css
.slide-image {
  max-width: 100%;
  max-height: min(50vh, 400px);
  object-fit: contain;
  border-radius: 8px;
}
.slide-image.screenshot {
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 12px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
}
.slide-image.logo {
  max-height: min(30vh, 200px);
}
```

**Adapt border/shadow colors to match the chosen style's accent.** Never repeat the same image on multiple slides (except logos on title + closing).

**Placement patterns:** Logo centered on title slide. Screenshots in two-column layouts with text. Full-bleed images as slide backgrounds with text overlay (use sparingly).

## Hero Slide Rules (Required)

If a hero/title slide uses an image background, it must follow these rules:

1. First and last slides must always be hero slides with image backgrounds from `skills/frontend-slides/assets/images/`.
2. Any title-only divider slide (no body content) must also be implemented as an image-backed hero slide.
3. Keep hero content vertically centered (`justify-content: center`).
3. Theme title color rule:
   - Light theme title color must be DHL red (`#bb001e`).
   - Dark theme title color must be white (`#ffffff`).
   - If the hero photo is dark, apply a `dark-hero` variant and force white title/subtitle/metadata text.
   - If hero background is DHL yellow (`#ffcc00`), title must be DHL red (`#bb001e`).
4. Add `../skills/frontend-slides/assets/images/banner.png` at the bottom of the hero slide.
5. Apply a readable overlay so title contrast is preserved. For photo backgrounds, use a dark overlay baseline at or above `rgba(0,0,0,0.45)` and increase if text is still low-contrast.
6. Prefer left-aligned hero text with reserved bottom space for the banner, similar to a keynote cover layout.
7. Hero should contain `FOR INTERNAL USE` and footer metadata line in PDF-template style.

## Capability Grid Rules (Required)

1. For 6 capability cards, use a centered `3 + 3` layout.
2. For 7 capability cards, use a centered `4 + 3` layout (top row has more than bottom row).
3. For odd capability counts, keep the top row heavier than the bottom row where possible.

## Diagram Slide Rules (Required)

1. Every generated deck must include at least one dedicated diagram slide.
2. Diagram may be SVG or HTML/CSS blocks with connectors, but must visually show flow/architecture.
3. Do not rely on bullets alone when introducing architecture/process content.

## GSAP Motion Pattern (Optional, Recommended)

For smoother transitions in presentation mode, GSAP can be included in single-file HTML:

```html
<script src="https://cdn.jsdelivr.net/npm/gsap@3/dist/gsap.min.js"></script>
```

Then animate reveal elements when a slide becomes visible:

```js
const reduceMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
if (!reduceMotion && window.gsap) {
  gsap.fromTo(
    ".slide.visible .reveal",
    { y: 26, opacity: 0 },
    {
      y: 0,
      opacity: 1,
      duration: 0.7,
      ease: "power3.out",
      stagger: 0.08,
      overwrite: "auto",
    },
  );
}
```

Use `gsap.timeline()` and `fromTo()` for sequence control, and keep reduced-motion fallback enabled.

---

## Code Quality

**Comments:** Every section needs clear comments explaining what it does and how to modify it.

**Accessibility:**

- Semantic HTML (`<section>`, `<nav>`, `<main>`)
- Keyboard navigation works fully
- ARIA labels where needed
- `prefers-reduced-motion` support (included in viewport-base.css)

## File Structure

Single presentations:

```
presentation.html    # Self-contained, all CSS/JS inline
assets/              # Images only, if any
```

Multiple presentations in one project:

```
[name].html
[name]-assets/
```

