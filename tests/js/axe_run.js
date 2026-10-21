#!/usr/bin/env node
// Runs axe-core (the WCAG 2.0, 2.1 and 2.2 A and AA rules) over one generated HTML page in jsdom (Ruling P4-17).
// Usage: node axe_run.js <html-file> [#fragment]
// Prints {"violations": [{"id", "impact", "nodes"}]}, where nodes lists the CSS target of each failing element.
// The page's own inline scripts run first, so content that pack.js or detail.js renders is checked too; a
// fragment (for example #detail) opens the page at that address, as a link would.
// jsdom does no layout, so axe cannot measure colour contrast here: that rule comes back "incomplete", not failed.
"use strict";
const fs = require("fs");
const path = require("path");

const file = process.argv[2];
if (!file) {
  process.stderr.write("usage: node axe_run.js <html-file> [#fragment]\n");
  process.exit(2);
}
const { JSDOM, VirtualConsole } = require("jsdom");
const NOISE = /^(Not implemented: |Could not parse CSS stylesheet)/;   // jsdom limits, not page errors

const vc = new VirtualConsole();
vc.on("jsdomError", (e) => {
  const msg = String((e && e.message) || e);
  if (!NOISE.test(msg)) process.stderr.write("page script error: " + msg + "\n");
});
// jsdom's CSS parser rejects a whole <style> block that holds a page-margin box such as @page{@bottom-center{…}};
// those boxes only style print, so they are dropped here and the rest of the page's CSS applies as in a browser.
const PAGE_MARGIN_BOX = /@page\s*\{\s*@[a-z-]+\s*\{[^{}]*\}\s*\}/g;
const dom = new JSDOM(fs.readFileSync(file, "utf8").replace(PAGE_MARGIN_BOX, ""), {
  runScripts: "dangerously",
  pretendToBeVisual: true,
  url: "file://" + path.resolve(file) + (process.argv[3] || ""),
  virtualConsole: vc,
});
const { window } = dom;

function check() {
  window.eval(fs.readFileSync(require.resolve("axe-core/axe.min.js"), "utf8"));
  return window.axe.run(window.document, {
    runOnly: { type: "tag", values: ["wcag2a", "wcag2aa", "wcag21a", "wcag21aa", "wcag22aa"] },
    resultTypes: ["violations"],
  });
}

// The page scripts start on DOMContentLoaded, so axe runs once the page has loaded.
new Promise((resolve) => window.addEventListener("load", resolve))
  .then(check)
  .then((res) => {
    const violations = res.violations.map((v) => ({
      id: v.id,
      impact: v.impact,
      nodes: v.nodes.map((n) => n.target.join(" ")),
    }));
    process.stdout.write(JSON.stringify({ violations }) + "\n");
    window.close();
  })
  .catch((e) => {
    process.stderr.write("axe failed: " + ((e && e.stack) || e) + "\n");
    process.exit(1);
  });
