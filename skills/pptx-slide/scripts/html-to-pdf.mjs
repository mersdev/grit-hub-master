// scripts/html-to-pdf.mjs
// Render any HTML file (including the slides deck) to PDF via headless Chromium.
//
// Usage:
//   node scripts/html-to-pdf.mjs <url> [outPath]
//   node scripts/html-to-pdf.mjs http://localhost:3000/slides/index.html out/deck.pdf
//
// Notes:
// - For the slide deck specifically, this captures the page as-is. The deck-stage
//   component has its own print-to-PDF that emits one page per slide. To use it,
//   open the deck in a real browser and Cmd-/Ctrl-P, or trigger window.print()
//   programmatically (see below).

import { chromium } from "playwright";
import { mkdirSync } from "node:fs";
import { dirname } from "node:path";

const [, , urlArg, outArg] = process.argv;
const url = urlArg || "http://localhost:3000/slides/index.html";
const out = outArg || "out/deck.pdf";

mkdirSync(dirname(out), { recursive: true });

const isDeck = url.includes("/slides/");
const browser = await chromium.launch();
const page = await browser.newPage({ viewport: { width: 1920, height: 1080 } });

console.log(`→ Loading ${url}`);
await page.goto(url, { waitUntil: "networkidle", timeout: 30_000 });
// Give custom fonts & lucide icons one more beat to render.
await page.waitForTimeout(800);

if (isDeck) {
  // deck-stage emits one PDF page per <section> when window.print() is called.
  // We use page.pdf with @page rules instead for headless reliability.
  await page.addStyleTag({
    content: `
      @page { size: 1920px 1080px; margin: 0; }
      html, body { background: #fff; }
      deck-stage { display: block !important; }
      deck-stage > section {
        page-break-after: always;
        break-after: page;
        width: 1920px;
        height: 1080px;
        transform: none !important;
      }
    `
  });
  // Tell deck-stage to drop its scale transform.
  await page.evaluate(() => {
    const s = document.querySelector("deck-stage");
    if (s) s.setAttribute("noscale", "");
  });
  await page.waitForTimeout(400);
}

await page.pdf({
  path: out,
  width: "1920px",
  height: "1080px",
  printBackground: true,
  margin: { top: 0, right: 0, bottom: 0, left: 0 }
});

await browser.close();
console.log(`✓ Wrote ${out}`);
