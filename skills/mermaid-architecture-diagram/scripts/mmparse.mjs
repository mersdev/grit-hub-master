#!/usr/bin/env node
/*
 * mmparse.mjs — headless Mermaid syntax validation without a browser.
 *
 * Uses mermaid.parse() (grammar-level validation, no rendering) with a jsdom
 * DOM shim so it runs in plain Node. This is authoritative for SYNTAX — it is
 * the same parser the renderer uses — but does not require Chromium.
 *
 * Usage:  node mmparse.mjs <file.mmd>
 * Exit 0 + "PARSE_OK" on success; exit 2 + "PARSE_ERROR: <msg>" on failure;
 * exit 3 + "PARSE_UNAVAILABLE: <msg>" if deps (mermaid/jsdom) are missing.
 *
 * Install deps once:  npm install mermaid jsdom
 */

import { readFileSync } from "node:fs";

const file = process.argv[2];
if (!file) {
  console.log("PARSE_UNAVAILABLE: no input file");
  process.exit(3);
}

let JSDOM, mermaid;
try {
  ({ JSDOM } = await import("jsdom"));
} catch {
  console.log("PARSE_UNAVAILABLE: jsdom not installed");
  process.exit(3);
}
try {
  const dom = new JSDOM("<!DOCTYPE html><body></body>", { pretendToBeVisual: true });
  globalThis.window = dom.window;
  globalThis.document = dom.window.document;
  mermaid = (await import("mermaid")).default;
  mermaid.initialize({ startOnLoad: false });
} catch (e) {
  console.log("PARSE_UNAVAILABLE: " + (e.message || String(e)).split("\n")[0]);
  process.exit(3);
}

const text = readFileSync(file, "utf8");
try {
  await mermaid.parse(text);
  console.log("PARSE_OK");
  process.exit(0);
} catch (e) {
  const msg = (e && (e.str || e.message)) ? (e.str || e.message) : String(e);
  console.log("PARSE_ERROR: " + msg.split("\n")[0].slice(0, 200));
  process.exit(2);
}
