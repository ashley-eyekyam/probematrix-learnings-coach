/* ProbeMatrix Learnings Coach: behaviour for a learning-pack page (<skill>.html). pmlc.py pack renders
   the whole page; this script only adds citation expansion, search, expand/collapse, ticks, deep links
   and print. Vanilla JavaScript, no dependencies, works offline. pmlc.py inlines this file inside a
   script element, so it must never contain a closing script tag. Data comes from #pmlc-pack-data. */
(function () {
  "use strict";

  var SAFE = /^[a-z0-9]+(?:-[a-z0-9]+)*$/;
  var D = null;

  /* "#s/before-work" -> {kind: "s", id: "before-work"}; "#i/x-2" -> {kind: "i", ...}; anything else null. */
  function parseHash(hash) {
    var m = /^#([si])\/(.+)$/.exec(String(hash || ""));
    if (!m) return null;
    var id;
    try { id = decodeURIComponent(m[2]); } catch (err) { return null; }
    return SAFE.test(id) ? {kind: m[1], id: id} : null;
  }

  /* Every whitespace-separated word of q appears in text, ignoring case. An empty query matches. */
  function matches(text, q) {
    var t = String(text || "").toLowerCase();
    return String(q || "").toLowerCase().split(/\s+/).filter(Boolean)
      .every(function (w) { return t.indexOf(w) !== -1; });
  }

  function tickKey(pack, run) { return "pmlc-pack:" + pack + ":" + run; }

  function readTicks(store, key) {
    try {
      var v = JSON.parse(store.getItem(key) || "{}");
      return v && typeof v === "object" && !Array.isArray(v) ? v : {};
    } catch (err) { return {}; }
  }

  function isTicked(ticks, k) { return Object.prototype.hasOwnProperty.call(ticks, k) && !!ticks[k]; }

  function writeTicks(store, key, ticks) {
    try { store.setItem(key, JSON.stringify(ticks)); return true; } catch (err) { return false; }
  }

  /* A finding's text is the investigation's AI-drafted wording: true unless the export marks it edited by a person. */
  function unedited(f) { return ["yes", "y", "true", "1"].indexOf(String(f.user_edited || "").trim().toLowerCase()) === -1; }

  /* --embed cited and summary: an uncovered or excluded finding travels as {id, label, rating} only. */
  var STUB_KEYS = ["id", "label", "rating"];
  var STUB_NOTE = "Only the label and rating are embedded in this page.";
  function isStub(f) {
    var keys = f && typeof f === "object" ? Object.keys(f) : [];
    return keys.length === STUB_KEYS.length && keys.every(function (k) { return STUB_KEYS.indexOf(k) !== -1; });
  }

  function nonEmpty(rows) { return rows.filter(function (r) { return r[1] && String(r[1]).trim() !== ""; }); }

  /* [label, value] rows describing one finding or evidence record, or null if it is not in the data. */
  function recordRows(id, data) {
    var f = data && data.findings && data.findings[id];
    if (f && isStub(f)) {
      return nonEmpty([["Finding", f.label || ""],
        ["Rating", f.rating === null || f.rating === undefined ? "" : String(f.rating)], ["Detail", STUB_NOTE]]);
    }
    if (f) {
      var c = f.clusters || {};
      return nonEmpty([
        ["Finding", f.label || f.name || ""],
        ["Level", f.level ? "L" + f.level + " " + (f.level_name || "") + (f.subcategory ? " · " + f.subcategory : "") : ""],
        ["Factor", ((f.code || "") + " " + (f.name || "")).trim()],
        ["Rating", f.rating === null || f.rating === undefined ? "" : String(f.rating)],
        ["Roles involved", (f.roles || []).join("; ")],
        ["Learning clusters", [(c.F || []).join(", "), (c.T || []).join(", "), (c.R || []).join(", ")]
          .filter(Boolean).join(" · ")],
        ["Description", f.short || ""],
        [(data.brand && data.brand.ai_justification_label) || "Justification", f.justification || ""],
        ["Causal explanation", f.causal || ""],
        ["Reviewer votes", (f.votes || []).map(function (v) { return v.vote + (v.reason ? ": " + v.reason : ""); }).join("; ")],
        ["Evidence", (f.evidence || []).join(", ")]]);
    }
    var e = data && data.evidence && data.evidence[id];
    if (!e) return null;
    var rows = [["Evidence", e.description || ""], ["Type", e.type || ""]];
    (e.links || []).forEach(function (l) {
      rows.push(["Linked to " + l.code, [l.relevance, l.reference].filter(Boolean).join(": ")]);
    });
    return nonEmpty(rows);
  }

  /* What an expanded record shows: {banner, chip, rows}, or null if the ID is not in the data. A finding starts with
     the export-language banner, and carries the AI chip when no person edited it; an evidence record has neither. */
  function recordView(id, data) {
    var rows = recordRows(id, data);
    if (!rows) return null;
    var f = data.findings && data.findings[id], b = data.brand || {};
    return {banner: f ? b.export_banner || null : null, chip: f && !isStub(f) && unedited(f) ? b.ai_chip || null : null,
            rows: rows};
  }

  function el(tag, cls, text) {
    var n = document.createElement(tag);
    if (cls) n.className = cls;
    if (text !== null && text !== undefined) n.textContent = text;
    return n;
  }

  function toggleCite(btn) {
    var next = btn.nextElementSibling;
    if (btn.getAttribute("aria-expanded") === "true") {
      if (next && next.classList.contains("rec")) next.remove();
      btn.setAttribute("aria-expanded", "false");
      return;
    }
    var v = recordView(btn.getAttribute("data-id"), D), box = el("div", "rec");
    if (!v) box.appendChild(el("p", "m", "Not in this export."));
    else {
      if (v.banner) box.appendChild(el("p", "export-banner", v.banner));
      if (v.chip) box.appendChild(el("span", "chip-ai", v.chip));
      var dl = el("dl");
      v.rows.forEach(function (r) { dl.appendChild(el("dt", null, r[0])); dl.appendChild(el("dd", null, r[1])); });
      box.appendChild(dl);
    }
    btn.insertAdjacentElement("afterend", box);
    btn.setAttribute("aria-expanded", "true");
  }

  function search(q) {
    var shown = 0, active = String(q || "").trim() !== "";
    document.querySelectorAll(".item").forEach(function (it) {
      var ok = matches(it.textContent, q);
      it.hidden = !ok;
      if (ok) shown++;
    });
    document.querySelectorAll("details.sec").forEach(function (s) {
      var any = s.querySelector(".item:not([hidden])");
      s.hidden = !any;
      if (any && active) s.open = true;
    });
    var n = document.getElementById("showing");
    if (n) n.textContent = active ? shown + " matching items" : "";
  }

  function setAll(open) {
    document.querySelectorAll("main details:not(.rail)").forEach(function (d) { d.open = open; });
  }

  /* Print opens what prints; the uncovered list (.noprint) prints as one line instead (L4-01). */
  function openForPrint() {
    document.querySelectorAll("main details:not(.rail):not(.noprint)").forEach(function (d) { d.open = true; });
  }

  function route() {
    var h = parseHash(location.hash);
    if (!h) return;                                   /* unknown or unsafe: leave the reader's view alone */
    var target = document.getElementById((h.kind === "s" ? "s-" : "i-") + h.id);
    if (!target) return;
    if (target.closest("[hidden]")) {
      var q = document.getElementById("q");
      if (q) q.value = "";
      search("");
    }
    var sec = target.closest("details.sec");
    if (sec) sec.open = true;
    if (h.kind === "s") target.open = true;
    document.querySelectorAll(".item.hit").forEach(function (n) { n.classList.remove("hit"); });
    if (h.kind === "i") target.classList.add("hit");
    target.scrollIntoView({block: "start"});
  }

  function wireTicks() {
    var key = tickKey(D.pack, D.run), store = null;
    try { store = window.localStorage; } catch (err) { store = null; }
    var ticks = store ? readTicks(store, key) : {};
    var boxes = document.querySelectorAll("input.tick");
    boxes.forEach(function (cb) {
      var k = cb.getAttribute("data-key");
      cb.checked = isTicked(ticks, k);
      cb.addEventListener("change", function () {
        if (cb.checked) ticks[k] = 1; else delete ticks[k];
        if (store) writeTicks(store, key, ticks);
      });
    });
    var clear = document.getElementById("clear-ticks");
    if (clear) clear.addEventListener("click", function () {
      ticks = {};
      if (store) writeTicks(store, key, ticks);
      boxes.forEach(function (cb) { cb.checked = false; });
    });
  }

  function wire() {
    document.addEventListener("click", function (ev) {
      var b = ev.target && ev.target.closest ? ev.target.closest("button.cite") : null;
      if (b) toggleCite(b);
      var a = ev.target && ev.target.closest ? ev.target.closest('a[href^="#s/"],a[href^="#i/"]') : null;
      if (a && location.hash === a.getAttribute("href")) { ev.preventDefault(); route(); }
    });
    var q = document.getElementById("q");
    if (q) q.addEventListener("input", function () { search(q.value); });
    var on = function (id, fn) { var n = document.getElementById(id); if (n) n.addEventListener("click", fn); };
    on("expand-all", function () { setAll(true); });
    on("collapse-all", function () { setAll(false); });
    on("print", function () { window.print(); });
    window.addEventListener("beforeprint", openForPrint);
    window.addEventListener("hashchange", route);
  }

  function init() {
    var node = document.getElementById("pmlc-pack-data");
    if (!node) return;
    D = JSON.parse(node.textContent);
    D.findings = D.findings || {};
    D.evidence = D.evidence || {};
    document.body.classList.add("js");
    var rail = document.querySelector("details.rail");
    if (rail && window.matchMedia && !window.matchMedia("(min-width:1000px)").matches) rail.open = false;
    wireTicks();
    wire();
    route();
  }

  var API = {parseHash: parseHash, matches: matches, tickKey: tickKey, readTicks: readTicks, writeTicks: writeTicks,
             isTicked: isTicked, recordRows: recordRows, recordView: recordView};
  if (typeof module !== "undefined" && module.exports) { module.exports = API; return; }
  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", init); else init();
})();
