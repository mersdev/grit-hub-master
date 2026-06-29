// scripts/html-to-pptx.mjs
//
// Two-stage interactive export:
//   1. Screenshot each slide and write a stable, pixel-perfect PPTX.
//   2. Prompt: "Convert to editable text PPTX?" (y/N)
//      If yes -> walk the DOM and rebuild each slide as native PPTX
//      objects (rectangles for colored blocks, images for <img>/<svg>,
//      text boxes for text) on top of a stripped background plate.
//
// Stage 1 always runs. Stage 2 only on confirmation.
//
// Usage:
//   node scripts/html-to-pptx.mjs <url> [outPath]
//
// Flags:
//   --no-prompt          -> just the screenshot PPTX
//   --editable           -> both files, no prompt

import { chromium } from "playwright";
import PptxGenJS from "pptxgenjs";
import { mkdirSync } from "node:fs";
import { dirname, extname, basename, join } from "node:path";
import { createInterface } from "node:readline/promises";
import { stdin as input, stdout as output } from "node:process";

// ----- CLI args -----
const args = process.argv.slice(2);
const flags = new Set(args.filter(a => a.startsWith("--")));
const positional = args.filter(a => !a.startsWith("--"));
const url = positional[0] || "http://localhost:3000/slides/index.html";
const outScreens = positional[1] || "out/deck.pptx";
const outEditable = join(
  dirname(outScreens),
  basename(outScreens, extname(outScreens)) + "-editable" + extname(outScreens)
);

mkdirSync(dirname(outScreens), { recursive: true });

// ----- Geometry -----
const SLIDE_W_PX = 1920, SLIDE_H_PX = 1080;
const SLIDE_W_IN = 13.333, SLIDE_H_IN = 7.5;
const pxToInX = (px) => (px / SLIDE_W_PX) * SLIDE_W_IN;
const pxToInY = (px) => (px / SLIDE_H_PX) * SLIDE_H_IN;
// Slide is 1920px mapped to 13.333in (= 960pt), so 1px = 0.5pt at this DPI.
// Using the generic 96-DPI conversion (px*0.75) inflates every font size by 50%.
const PT_PER_PX = (SLIDE_W_IN * 72) / SLIDE_W_PX;
const pxToPt  = (px) => Math.max(6, Math.round(px * PT_PER_PX * 10) / 10);

function parseRGBA(c) {
  if (!c) return null;
  const m = c.match(/rgba?\(\s*(\d+)[,\s]+(\d+)[,\s]+(\d+)(?:[,\s/]+([\d.]+))?/i);
  if (!m) return null;
  return { r: +m[1], g: +m[2], b: +m[3], a: m[4] !== undefined ? parseFloat(m[4]) : 1 };
}
function rgbToHex({ r, g, b }) {
  return [r, g, b].map(n => n.toString(16).padStart(2, "0")).join("").toUpperCase();
}
function cssToHex(c) {
  const p = parseRGBA(c);
  return p ? rgbToHex(p) : "000000";
}

// ----- Boot Playwright -----
const browser = await chromium.launch();
const page = await browser.newPage({
  viewport: { width: SLIDE_W_PX, height: SLIDE_H_PX },
  deviceScaleFactor: 2
});

console.log(`-> Loading ${url}`);
await page.goto(url, { waitUntil: "networkidle", timeout: 30_000 });
await page.waitForTimeout(800);

await page.evaluate(() => {
  const s = document.querySelector("deck-stage");
  if (s) s.setAttribute("noscale", "");
});
await page.waitForTimeout(300);

const slideCount = await page.evaluate(
  () => document.querySelectorAll("deck-stage > section").length
);
console.log(`-> ${slideCount} slide(s)`);

const notes = await page.evaluate(() => {
  try {
    const t = document.querySelector("script#speaker-notes");
    return t ? JSON.parse(t.textContent) : [];
  } catch { return []; }
});

// ----- Stage 1: pixel-perfect screenshots -----
console.log(`\n[Stage 1] Capturing screenshots...`);

const screens = []; // pixel-perfect screenshot dataURL per slide

for (let i = 0; i < slideCount; i++) {
  await page.evaluate((n) => {
    const stage = document.querySelector("deck-stage");
    if (stage && typeof stage.goTo === "function") stage.goTo(n);
  }, i);
  await page.waitForTimeout(450);

  const sect = page.locator(`deck-stage > section:nth-child(${i + 1})`);
  const buf = await sect.screenshot({ type: "png" });
  screens.push({
    dataUrl: `data:image/png;base64,${buf.toString("base64")}`,
    note: notes[i] || ""
  });
  console.log(`  - slide ${i + 1}/${slideCount} captured`);
}

// Write screenshot-only PPTX
{
  const pptx = new PptxGenJS();
  pptx.defineLayout({ name: "DHL_HD", width: SLIDE_W_IN, height: SLIDE_H_IN });
  pptx.layout = "DHL_HD";
  pptx.title = "DHL Deck";

  for (const s of screens) {
    const slide = pptx.addSlide();
    slide.background = { color: "FFFFFF" };
    slide.addImage({ data: s.dataUrl, x: 0, y: 0, w: SLIDE_W_IN, h: SLIDE_H_IN });
    if (s.note) slide.addNotes(s.note);
  }
  await pptx.writeFile({ fileName: outScreens });
  console.log(`\nOK wrote ${outScreens}  (screenshots - pixel-perfect, not editable)`);
}

// ----- Stage 2 prompt -----
async function askYesNo(question) {
  if (flags.has("--no-prompt")) return false;
  if (flags.has("--editable")) return true;
  const rl = createInterface({ input, output });
  const ans = (await rl.question(question)).trim().toLowerCase();
  rl.close();
  return ans === "y" || ans === "yes";
}

const doEditable = await askYesNo(`\nConvert to editable PPTX as well? (y/N) `);

if (!doEditable) {
  await browser.close();
  console.log(`\nDone. Single output: ${outScreens}`);
  process.exit(0);
}

console.log(`\n[Stage 2] Rebuilding slides as native PPTX objects...`);

// Inject the DOM walker. It returns:
//   - objects[]   : ordered list of shapes / images / text to render
//   - bgColor     : section's own background color (paints the slide)
// then we screenshot a "plate" with all reconstructable things hidden,
// so anything we miss (gradients, pseudo-elements, complex backgrounds)
// still shows through underneath.
await page.addScriptTag({ content: `
async function blobToDataURL(blob) {
  return new Promise((res, rej) => {
    const fr = new FileReader();
    fr.onload = () => res(fr.result);
    fr.onerror = rej;
    fr.readAsDataURL(blob);
  });
}

async function fetchAsDataURL(src) {
  try {
    const r = await fetch(src);
    if (!r.ok) return null;
    const b = await r.blob();
    return await blobToDataURL(b);
  } catch { return null; }
}

function isOpaque(cs) {
  return cs.visibility !== "hidden" && cs.display !== "none" && parseFloat(cs.opacity) > 0;
}

function effectiveZ(el) {
  // walk up; first explicit z-index wins, else 0
  let z = 0, depth = 0, n = el;
  while (n && n.nodeType === 1) {
    const cs = getComputedStyle(n);
    if (cs.position !== "static") {
      const v = parseInt(cs.zIndex, 10);
      if (!Number.isNaN(v)) { z = v; break; }
    }
    n = n.parentElement;
    depth++;
  }
  return z;
}

async function collectSlideObjects(section) {
  const sRect = section.getBoundingClientRect();
  const ox = sRect.left, oy = sRect.top;
  const objects = [];
  let order = 0;

  const sectionCS = getComputedStyle(section);
  const bgColor = sectionCS.backgroundColor;

  const all = section.querySelectorAll("*");
  for (const el of all) {
    // Anything inside an <svg> stays part of the embedded SVG image —
    // don't extract its text/shapes as separate native objects.
    if (el.closest && el.closest("svg") && el.tagName.toLowerCase() !== "svg") continue;
    // Skip page-bar / footer entirely: PowerPoint manages its own footer.
    if (el.classList && el.classList.contains("pagebar")) continue;
    if (el.closest && el.closest(".pagebar")) continue;
    // Skip anything inside a list we've already aggregated (handled below).
    if (el.closest && el.closest("ul, ol") && !(el.tagName === "UL" || el.tagName === "OL")) continue;
    const cs = getComputedStyle(el);
    if (!isOpaque(cs)) continue;
    const r = el.getBoundingClientRect();
    if (r.width < 1 || r.height < 1) continue;

    const tag = el.tagName;
    const z = effectiveZ(el);
    const baseGeom = {
      x: r.left - ox, y: r.top - oy, w: r.width, h: r.height,
      z, order: order++
    };

    if (tag === "IMG") {
      const src = el.currentSrc || el.src;
      let data = src;
      if (/^https?:/i.test(src) || src.startsWith("/")) {
        data = (await fetchAsDataURL(src)) || src;
      }
      objects.push({ kind: "image", ...baseGeom, src: data });
      continue;
    }
    if (tag.toLowerCase() === "svg") {
      const clone = el.cloneNode(true);
      if (!clone.getAttribute("xmlns")) clone.setAttribute("xmlns", "http://www.w3.org/2000/svg");
      const w = r.width, h = r.height;
      if (!clone.getAttribute("width"))  clone.setAttribute("width",  w);
      if (!clone.getAttribute("height")) clone.setAttribute("height", h);
      // Inline computed fills so var(--...) survives outside the page
      const paintables = clone.querySelectorAll("*");
      const liveAll = el.querySelectorAll("*");
      for (let i = 0; i < paintables.length && i < liveAll.length; i++) {
        const lcs = getComputedStyle(liveAll[i]);
        if (lcs.fill && lcs.fill !== "none") paintables[i].setAttribute("fill", lcs.fill);
        if (lcs.stroke && lcs.stroke !== "none") paintables[i].setAttribute("stroke", lcs.stroke);
        if (lcs.opacity && lcs.opacity !== "1") paintables[i].setAttribute("opacity", lcs.opacity);
      }
      const xml = new XMLSerializer().serializeToString(clone);
      const dataUrl = "data:image/svg+xml;base64," + btoa(unescape(encodeURIComponent(xml)));
      objects.push({ kind: "image", ...baseGeom, src: dataUrl });
      continue;
    }

    if (tag === "UL" || tag === "OL") {
      const items = Array.from(el.children)
        .filter(li => li.tagName === "LI")
        .map(li => (li.textContent || "").replace(/\\s+/g, " ").trim())
        .filter(Boolean);
      if (items.length) {
        objects.push({
          kind: "list", ...baseGeom,
          items,
          ordered: tag === "OL",
          size: parseFloat(cs.fontSize),
          weight: cs.fontWeight,
          family: cs.fontFamily,
          color: cs.color,
          lineHeightPx: parseFloat(cs.lineHeight) || parseFloat(cs.fontSize) * 1.2
        });
      }
      continue;
    }

    // Solid background rectangle?
    const bg = parseRGBAStr(cs.backgroundColor);
    if (bg && bg.a > 0) {
      const radius = parseFloat(cs.borderTopLeftRadius) || 0;
      objects.push({
        kind: "shape", ...baseGeom,
        fill: bg, radius
      });
    }

    // Direct text content of this node (children with own text handled separately)
    const direct = Array.from(el.childNodes)
      .filter(n => n.nodeType === 3 && n.textContent.trim())
      .map(n => n.textContent.replace(/\\s+/g, " ").trim())
      .join(" ")
      .trim();
    if (direct) {
      const lineH = parseFloat(cs.lineHeight) || parseFloat(cs.fontSize) * 1.2;
      const padY = (parseFloat(cs.paddingTop) || 0) + (parseFloat(cs.paddingBottom) || 0);
      const innerH = Math.max(0, r.height - padY);
      const lines = Math.max(1, Math.round(innerH / lineH));
      const display = cs.textTransform === "uppercase" ? direct.toUpperCase() : direct;
      const measured = measureTextPx(display, cs);
      objects.push({
        kind: "text", ...baseGeom,
        text: direct,
        size: parseFloat(cs.fontSize),
        weight: cs.fontWeight,
        family: cs.fontFamily,
        color: cs.color,
        align: cs.textAlign,
        italic: cs.fontStyle === "italic",
        transform: cs.textTransform,
        letterSpacing: cs.letterSpacing,
        lineHeightPx: lineH,
        lines,
        textPxWidth: measured,
        className: el.className || ""
      });
    }
  }
  return { bgColor, objects };
}

function measureTextPx(text, cs) {
  try {
    const canvas = measureTextPx._c || (measureTextPx._c = document.createElement("canvas"));
    const ctx = canvas.getContext("2d");
    const style = cs.fontStyle && cs.fontStyle !== "normal" ? cs.fontStyle : "";
    const variant = "";
    const weight = cs.fontWeight || "400";
    const size = cs.fontSize || "16px";
    const lineH = "/1";
    const family = cs.fontFamily || "sans-serif";
    ctx.font = [style, variant, weight, size, family].filter(Boolean).join(" ");
    const m = ctx.measureText(text);
    let w = m.width;
    const ls = parseFloat(cs.letterSpacing);
    if (Number.isFinite(ls) && ls !== 0) w += ls * Math.max(0, text.length - 1);
    return w;
  } catch { return null; }
}

function parseRGBAStr(c) {
  if (!c) return null;
  const m = c.match(/rgba?\\(\\s*(\\d+)[,\\s]+(\\d+)[,\\s]+(\\d+)(?:[,\\s/]+([\\d.]+))?/i);
  if (!m) return null;
  return { r: +m[1], g: +m[2], b: +m[3], a: m[4] !== undefined ? parseFloat(m[4]) : 1 };
}

// Hide reconstructable things so the residual "plate" only carries
// gradients / pseudo-element artwork / bg-images we did not extract.
function strip(section) {
  const touched = [];
  for (const el of section.querySelectorAll("img, svg")) {
    touched.push({ el, attr: el.getAttribute("style") });
    el.style.setProperty("visibility", "hidden", "important");
  }
  for (const el of section.querySelectorAll(".pagebar, .pagebar *")) {
    touched.push({ el, attr: el.getAttribute("style") });
    el.style.setProperty("display", "none", "important");
  }
  for (const el of section.querySelectorAll("*")) {
    const cs = getComputedStyle(el);
    const bg = parseRGBAStr(cs.backgroundColor);
    if (bg && bg.a > 0) {
      touched.push({ el, attr: el.getAttribute("style") });
      el.style.setProperty("background-color", "transparent", "important");
    }
  }
  const style = document.createElement("style");
  style.setAttribute("data-plate-style", "");
  style.textContent = \`
    deck-stage > section *, deck-stage > section *::before, deck-stage > section *::after {
      color: transparent !important;
      -webkit-text-fill-color: transparent !important;
      text-shadow: none !important;
    }
  \`;
  document.head.appendChild(style);
  window.__plateRestore = () => {
    for (const t of touched) {
      if (t.attr === null) t.el.removeAttribute("style");
      else t.el.setAttribute("style", t.attr);
    }
    for (const s of document.querySelectorAll("style[data-plate-style]")) s.remove();
    window.__plateRestore = null;
  };
}
` });

// Build editable PPTX
{
  const pptx = new PptxGenJS();
  pptx.defineLayout({ name: "DHL_HD", width: SLIDE_W_IN, height: SLIDE_H_IN });
  pptx.layout = "DHL_HD";
  pptx.title = "DHL Deck (editable)";

  for (let i = 0; i < slideCount; i++) {
    await page.evaluate((n) => {
      const stage = document.querySelector("deck-stage");
      if (stage && typeof stage.goTo === "function") stage.goTo(n);
    }, i);
    await page.waitForTimeout(400);

    // 1. Collect objects from the live DOM.
    const { bgColor, objects } = await page.evaluate(async (n) => {
      const sec = document.querySelectorAll("deck-stage > section")[n];
      // eslint-disable-next-line no-undef
      return await collectSlideObjects(sec);
    }, i);

    // 2. Plate skipped: nothing to strip/screenshot. All artwork is rebuilt natively below.

    // 4. Build the slide.
    const slide = pptx.addSlide();
    const sectionBg = parseRGBA(bgColor);
    slide.background = { color: sectionBg ? rgbToHex(sectionBg) : "FFFFFF" };

    // No background plate: every shape/image/text is reconstructed natively.

    // Sort: shapes/images first, then text on top. Within a kind,
    // honor z-index then DOM order.
    const kindOrder = { shape: 0, image: 1, text: 2 };
    objects.sort((a, b) => {
      if (kindOrder[a.kind] !== kindOrder[b.kind]) return kindOrder[a.kind] - kindOrder[b.kind];
      if (a.z !== b.z) return a.z - b.z;
      return a.order - b.order;
    });

    let shapeN = 0, imgN = 0, textN = 0;
    for (const o of objects) {
      const x = pxToInX(o.x), y = pxToInY(o.y);
      const w = pxToInX(o.w), h = pxToInY(o.h);

      if (o.kind === "shape") {
        const hex = rgbToHex(o.fill);
        const transparency = Math.round((1 - o.fill.a) * 100);
        const rounded = o.radius > 0;
        const opts = {
          x, y, w, h,
          fill: transparency > 0 ? { color: hex, transparency } : { color: hex },
        };
        if (rounded) opts.rectRadius = Math.min(0.5, o.radius / Math.min(o.w, o.h));
        slide.addShape(rounded ? "roundRect" : "rect", opts);
        shapeN++;
      } else if (o.kind === "image") {
        try {
          slide.addImage({ data: o.src.startsWith("data:") ? o.src : undefined,
                           path: o.src.startsWith("data:") ? undefined : o.src,
                           x, y, w, h });
          imgN++;
        } catch { /* skip unreadable images */ }
      } else if (o.kind === "list") {
        const fontFace = (o.family || "").split(",")[0].replace(/["\']/g, "").trim();
        const weight = parseInt(o.weight, 10) || (o.weight === "bold" ? 700 : 400);
        const lineH = o.lineHeightPx || o.size * 1.4;
        // Generous box: width = full original + buffer; height = lines * lineH + pad.
        const buffer = Math.max(80, o.size * 1.2);
        const pxW = Math.min(o.w + buffer, 1920 - o.x - 4);
        const pxH = Math.min(Math.max(o.h, lineH * o.items.length) + 24, 1080 - o.y);
        const paragraphs = o.items.map(t => ({
          text: t,
          options: {
            bullet: o.ordered ? { type: "number" } : { code: "25A0" }
          }
        }));
        slide.addText(paragraphs, {
          x, y,
          w: pxToInX(pxW),
          h: pxToInY(pxH),
          fontFace,
          fontSize: pxToPt(o.size),
          color: cssToHex(o.color),
          bold: weight >= 600,
          valign: "top",
          margin: 0,
          isTextBox: true,
          wrap: true,
          shrinkText: false,
          autoFit: false,
          paraSpaceAfter: 6
        });
        textN++;
      } else if (o.kind === "text") {
        const text = o.transform === "uppercase" ? o.text.toUpperCase() : o.text;
        const fontFace = (o.family || "").split(",")[0].replace(/["']/g, "").trim();
        const weight = parseInt(o.weight, 10) || (o.weight === "bold" ? 700 : 400);
        const charSpacing = (() => {
          const v = parseFloat(o.letterSpacing);
          if (!Number.isFinite(v) || v === 0) return undefined;
          // CSS letter-spacing is in px; pptxgenjs charSpacing is in points.
          // 1px ≈ 0.75pt. Clamp so brand eyebrow tracking (.08em ≈ 1pt) stays subtle.
          const pt = v * 0.75;
          if (Math.abs(pt) < 0.25) return undefined;
          return Math.round(pt * 10) / 10;
        })();

        const singleLine = (o.lines || 1) <= 1;

        // Real text width measured with the browser canvas, plus a generous
        // buffer so PowerPoint font fallbacks (Calibri/Arial when Delivery
        // is missing) cannot push text into a wrap or vertical stripe.
        const measured = Number.isFinite(o.textPxWidth) ? o.textPxWidth : o.w;
        // Big display text needs bigger absolute buffers — fallback fonts can be
        // 25-40% wider than Delivery Condensed Black at large sizes, and a few
        // missing px causes wrap and vertical overlap.
        const big = o.size >= 45;
        const buffer = big ? Math.max(96, o.size * 1.4) : Math.max(48, o.size * 0.9);
        let pxW = Math.max(o.w, measured) + buffer;
        const fallbackPad = singleLine
          ? Math.max(measured * (big ? 0.45 : 0.30), o.size * (big ? 1.0 : 0.6))
          : 0;
        pxW += fallbackPad;

        // Anchor + clamp depending on alignment, so right/center-aligned text
        // (page numbers, centered titles) does not drift off the slide.
        let pxX = o.x;
        const align = ["left", "center", "right"].includes(o.align) ? o.align : "left";
        if (align === "right") {
          const rightEdge = o.x + o.w;
          pxX = Math.max(0, rightEdge - pxW);
        } else if (align === "center") {
          const cx = o.x + o.w / 2;
          pxX = Math.max(0, cx - pxW / 2);
        }
        // Final clamp to slide width.
        if (pxX + pxW > 1920) {
          if (align === "left") pxW = 1920 - pxX - 4;
          else pxX = Math.max(0, 1920 - pxW - 4);
        }

        // Height: keep enough room for descenders and font metric drift.
        const lineH = o.lineHeightPx || o.size * 1.2;
        const lines = Math.max(1, o.lines || 1);
        const heightPad = singleLine ? Math.ceil(o.size * 0.6) : Math.ceil(o.size * 0.5);
        const pxH = Math.min(
          Math.max(o.h, lineH * lines) + heightPad,
          1080 - o.y
        );

        slide.addText(text, {
          x: pxToInX(pxX),
          y,
          w: pxToInX(pxW),
          h: pxToInY(pxH),
          fontFace,
          fontSize: pxToPt(o.size),
          color: cssToHex(o.color),
          bold: weight >= 600,
          italic: o.italic,
          align,
          valign: "top",
          margin: 0,
          isTextBox: true,
          wrap: !singleLine,
          shrinkText: false,
          autoFit: false,
          charSpacing
        });
        textN++;
      }
    }

    if (notes[i]) slide.addNotes(notes[i]);
    console.log(`  - slide ${i + 1}/${slideCount}: ${shapeN} shapes, ${imgN} images, ${textN} text boxes`);
  }

  await pptx.writeFile({ fileName: outEditable });
  console.log(`\nOK wrote ${outEditable}  (native shapes + images + text on a plate)`);
}

await browser.close();
console.log(`\nDone. Two outputs:`);
console.log(`  - ${outScreens}    (pixel-perfect, not editable)`);
console.log(`  - ${outEditable}   (every shape, image and text box is movable)`);