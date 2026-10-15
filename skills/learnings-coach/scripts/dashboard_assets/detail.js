/* ProbeMatrix Learnings Coach: the "Detailed register" tab of organisation-learning-map.html.
   Vanilla JavaScript, no dependencies, works offline. pmlc.py inlines this file inside a script
   element, so it must never contain a closing script tag. Data comes from the #pmlc-data block. */
(function () {
  "use strict";

  var ID_RX = /\b(LR-\d{1,3}|FND-[0-9A-Za-z]{4,}|EVD-\d{3,})\b/g;
  var SAFE_ID = /^(LR|FND|EVD)-[0-9A-Za-z]+$/;
  var STRONG = ["elimination", "substitution", "engineering"];

  function flat(v) {
    if (v === null || v === undefined) return "";
    if (Array.isArray(v)) return v.map(flat).join(" ");
    if (typeof v === "object") return Object.keys(v).map(function (k) { return k + " " + flat(v[k]); }).join(" ");
    return String(v);
  }

  function uniq(xs) { return xs.filter(function (x, i) { return xs.indexOf(x) === i; }); }

  /* "see EVD-0001." -> [{text: "see "}, {id: "EVD-0001"}, {text: "."}] */
  function tokenize(text) {
    var s = text === null || text === undefined ? "" : String(text), out = [], last = 0, m;
    ID_RX.lastIndex = 0;
    while ((m = ID_RX.exec(s))) {
      if (m.index > last) out.push({text: s.slice(last, m.index)});
      out.push({id: m[1]});
      last = m.index + m[0].length;
    }
    if (last < s.length) out.push({text: s.slice(last)});
    return out;
  }

  /* "#detail/LR-03" -> {tab: "detail", id: "LR-03"}; anything unsafe gives id null. */
  function parseHash(hash) {
    var parts = String(hash || "").replace(/^#/, "").split("/");
    if (parts[0] !== "detail") return {tab: "overview", id: null};
    var id = null;
    try { id = parts[1] ? decodeURIComponent(parts[1]) : null; } catch (err) { id = null; }
    return {tab: "detail", id: id && SAFE_ID.test(id) ? id : null};
  }

  function evidenceIdsFor(e, data) {
    var ids = (e.evidence_ids || []).slice();
    (e.finding_ids || []).forEach(function (fid) {
      var f = (data.findings || {})[fid];
      ((f && f.evidence) || []).forEach(function (x) { ids.push(x); });
    });
    return uniq(ids);
  }

  var hayCache = new WeakMap();
  function haystack(e, data) {
    if (hayCache.has(e)) return hayCache.get(e);
    var parts = [flat(e)];
    (e.finding_ids || []).forEach(function (fid) { if ((data.findings || {})[fid]) parts.push(flat(data.findings[fid])); });
    evidenceIdsFor(e, data).forEach(function (eid) { if ((data.evidence || {})[eid]) parts.push(flat(data.evidence[eid])); });
    var s = parts.join(" ").toLowerCase();
    hayCache.set(e, s);
    return s;
  }

  function matches(e, data, f) {
    var d = (data.derived || {})[e.lr_id] || {};
    if (f.tier && !(e.tier_messages && e.tier_messages[f.tier])) return false;
    if (f.priority && String(e.priority) !== String(f.priority)) return false;
    if (f.owner && d.entity !== f.owner) return false;
    if (f.level && d.level !== f.level) return false;
    if (f.hoc && (d.hoc || []).indexOf(f.hoc) < 0) return false;
    var q = String(f.q || "").trim().toLowerCase();
    if (q && haystack(e, data).indexOf(q) < 0) return false;
    return true;
  }

  function sortEntries(entries) {
    return entries.slice().sort(function (a, b) {
      var pa = Number(a.priority) || 9, pb = Number(b.priority) || 9;
      if (pa !== pb) return pa - pb;
      return String(a.lr_id || "").localeCompare(String(b.lr_id || ""), undefined, {numeric: true});
    });
  }

  /* Highest rating first, then highest level; IDs missing from the workspace last. */
  function sortFindings(ids, findings) {
    function key(id) { var f = findings[id]; return f ? [0, -(f.rating || 0), -(f.level || 0)] : [1, 0, 0]; }
    return ids.slice().sort(function (a, b) {
      var p = key(a), q = key(b);
      for (var i = 0; i < 3; i++) if (p[i] !== q[i]) return p[i] - q[i];
      return 0;
    });
  }

  function lensesFor(data) {
    var seen = {};
    (data.entries || []).forEach(function (e) { Object.keys(e.tier_messages || {}).forEach(function (t) { seen[t] = 1; }); });
    var tiers = Object.keys(seen).sort().map(function (t) {
      return {value: t, label: (t + " " + ((data.tier_labels || {})[t] || "")).trim()};
    });
    return [{value: "all", label: "All"}].concat(tiers,
      [{value: "investigator", label: "Investigator"}, {value: "auditor", label: "Auditor"}]);
  }

  /* Which cards a lens shows (tier), and the order and default-open state of each card's sections. */
  function lensSpec(lens) {
    if (!lens || lens === "all") {
      return {tier: null, order: ["lesson", "context", "classification", "recs", "tiers", "findings", "evidence"], open: ["lesson"]};
    }
    if (lens === "investigator") {
      var inv = ["lesson", "context", "findings", "evidence", "classification", "recs", "tiers"];
      return {tier: null, order: inv, open: inv.slice()};
    }
    if (lens === "auditor") {
      return {tier: null, order: ["lesson", "recs", "quality", "findings", "evidence", "classification", "context", "tiers"],
              open: ["lesson", "recs", "quality", "findings", "evidence"]};
    }
    if (lens === "T5") {
      return {tier: "T5", order: ["lesson", "risk", "recs", "context", "tiers", "classification", "findings", "evidence"],
              open: ["lesson", "risk", "recs"]};
    }
    return {tier: lens, order: ["lesson", "context", "warn", "recs", "tiers", "classification", "findings", "evidence"],
            open: ["lesson", "context", "warn", "recs"]};
  }

  function summarise(entries, data) {
    var recs = 0, strong = 0, p1 = 0, fset = {}, eset = {};
    entries.forEach(function (e) {
      var d = (data.derived || {})[e.lr_id] || {};
      (d.hoc || []).forEach(function (t) { recs++; if (STRONG.indexOf(t) >= 0) strong++; });
      if (String(e.priority) === "1") p1++;
      (e.finding_ids || []).forEach(function (f) { if ((data.findings || {})[f]) fset[f] = 1; });
      evidenceIdsFor(e, data).forEach(function (x) { eset[x] = 1; });
    });
    return {learnings: entries.length, p1: p1, recs: recs, strongPct: recs ? Math.round(100 * strong / recs) : 0,
            findings: Object.keys(fset).length, evidence: Object.keys(eset).length};
  }

  var API = {tokenize: tokenize, parseHash: parseHash, lensSpec: lensSpec, lensesFor: lensesFor, matches: matches,
             sortEntries: sortEntries, sortFindings: sortFindings, summarise: summarise, evidenceIdsFor: evidenceIdsFor};
  if (typeof module !== "undefined" && module.exports) { module.exports = API; }
})();
