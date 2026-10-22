/* ProbeMatrix Learnings Coach: the SCORM 1.2 runtime of <pack>.scorm.zip (pmlc_lib/render/scorm.py, Ruling P4-11).
   It finds the LMS's API object, grades the quiz in the browser against the key in #sm-key, and reports
   cmi.core.score.raw (0 to 100) and cmi.core.lesson_status: "passed" or "failed" against a pass mark of 80% of the
   scored questions, or "completed" when the pack has none. Vanilla JavaScript, no dependencies, works offline.
   Under Node it loads as CommonJS (findAPI, score, finish) for the tests. */
(function () {
  "use strict";

  var PASS = 80;
  var MAX_DEPTH = 7;          // the ADL search: at most 7 parent frames, then the opener's

  function safe(f) {
    try { return f(); } catch (err) { return undefined; }       // a cross-origin frame throws: skip it
  }

  function climb(w) {
    for (var n = 0; w && n <= MAX_DEPTH; n++) {
      var api = safe(function () { return w.API; });
      if (api) return api;
      var p = safe(function () { return w.parent; });
      if (!p || p === w) return null;
      w = p;
    }
    return null;
  }

  /* The SCORM 1.2 API object (window.API) in win, its parents or its opener's frames; null when there is none. */
  function findAPI(win) {
    if (!win) return null;
    return climb(win) || climb(safe(function () { return win.opener; })) || null;
  }

  function norm(s) { return String(s === undefined || s === null ? "" : s).replace(/\s+/g, " ").trim().toLowerCase(); }

  function indexSet(v) {
    var list = Array.isArray(v) ? v : (v === undefined || v === null || v === "" ? [] : [v]);
    var out = [];
    list.forEach(function (x) {
      var n = typeof x === "number" ? x : (/^\d+$/.test(String(x)) ? Number(x) : NaN);
      if (isFinite(n) && out.indexOf(n) === -1) out.push(n);
    });
    return out.sort(function (a, b) { return a - b; });
  }

  function sameSet(a, b) {
    var x = indexSet(a), y = indexSet(b);
    return x.length > 0 && x.length === y.length && x.every(function (v, i) { return v === y[i]; });
  }

  /* answers: {question id: option index | [indices] | text}; key: [{id, type, correct: [indices]} or
     {id, type: "short", accept: [texts]}]. Returns {raw, scored}: raw is the percentage right, rounded down, so a
     score shown as 80 has really reached the pass mark. A question without a type is not scored. */
  function score(answers, key) {
    var qs = Array.isArray(key) ? key : (key && key.questions) || [];
    var a = answers || {};
    var right = 0, scored = 0;
    qs.forEach(function (q) {
      if (!q || !q.type) return;
      scored++;
      var given = a[q.id];
      if (q.type === "short") {
        var t = norm(given);
        if (t && (q.accept || []).some(function (x) { return norm(x) === t; })) right++;
      } else if (sameSet(given, q.correct)) {
        right++;
      }
    });
    return {raw: scored ? Math.floor((100 * right) / scored) : 0, scored: scored};
  }

  function statusFor(raw, scored) {
    return scored ? (raw >= PASS ? "passed" : "failed") : "completed";
  }

  /* Report the result to the LMS and close the session: the score (only when there are scored questions), the
     lesson status, one LMSCommit and one LMSFinish. Returns the status; with no api it reports nothing. */
  function finish(api, raw, scored) {
    var st = statusFor(raw, scored);
    if (api) {
      if (scored) {
        api.LMSSetValue("cmi.core.score.raw", String(raw));
        api.LMSSetValue("cmi.core.score.min", "0");
        api.LMSSetValue("cmi.core.score.max", "100");
      }
      api.LMSSetValue("cmi.core.lesson_status", st);
      api.LMSCommit("");
      api.LMSFinish("");
    }
    return st;
  }

  // ------------------------------------------------------------------------------------------------ the page

  function collect(form) {
    var out = {};
    var boxes = form.querySelectorAll("[data-q]");
    for (var i = 0; i < boxes.length; i++) {
      var box = boxes[i], id = box.getAttribute("data-q"), type = box.getAttribute("data-type");
      var inputs = box.querySelectorAll("input");
      if (type === "short") { out[id] = inputs.length ? inputs[0].value : ""; continue; }
      var picked = [];
      for (var j = 0; j < inputs.length; j++) if (inputs[j].checked) picked.push(Number(inputs[j].value));
      out[id] = type === "multi" ? picked : picked[0];
    }
    return out;
  }

  function fill(text, vals) {
    return String(text || "").replace(/\{(\w+)\}/g, function (m, k) { return k in vals ? vals[k] : m; });
  }

  function init() {
    var d = document, data = {};
    try { data = JSON.parse(d.getElementById("sm-key").textContent); } catch (err) { data = {}; }
    var L = data.labels || {}, key = data.questions || [];
    var api = findAPI(window), done = false;
    if (api) {
      safe(function () {
        api.LMSInitialize("");
        var st = api.LMSGetValue("cmi.core.lesson_status");
        if (!st || st === "not attempted") api.LMSSetValue("cmi.core.lesson_status", "incomplete");
      });
    }
    var form = d.getElementById("sm-form"), out = d.getElementById("sm-result");
    var button = d.getElementById("sm-submit") || d.getElementById("sm-finish");
    if (!form || !button) return;
    button.addEventListener("click", function () {
      if (done) return;
      done = true;
      var r = button.id === "sm-submit" ? score(collect(form), key) : {raw: 0, scored: 0};
      var st = safe(function () { return finish(api, r.raw, r.scored); }) || statusFor(r.raw, r.scored);
      var msg = r.scored ? fill(L["ui.scorm.result"], {raw: r.raw, pass: data.pass || PASS, status: L["ui.scorm." + st] || st})
        : (L["ui.scorm.completed"] || st);
      if (out) out.textContent = msg + (api ? "" : " " + (L["ui.scorm.no_lms"] || ""));
      button.disabled = true;
    });
    window.addEventListener("pagehide", function () {        // left without submitting: close the session, status kept
      if (done || !api) return;
      done = true;
      safe(function () { api.LMSCommit(""); api.LMSFinish(""); });
    });
  }

  var API = {findAPI: findAPI, score: score, finish: finish};
  if (typeof module !== "undefined" && module.exports) { module.exports = API; return; }
  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", init); else init();
})();
