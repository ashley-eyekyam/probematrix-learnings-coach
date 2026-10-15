/* ProbeMatrix Learnings Coach: the "Detailed register" tab of organisation-learning-map.html.
   Vanilla JavaScript, no dependencies, works offline. pmlc.py inlines this file inside a script
   element, so it must never contain a closing script tag. Data comes from the #pmlc-data block. */
(function () {
  "use strict";

  var ID_RX = /\b(LR-\d+|FND-[0-9A-Za-z]{4,}|EVD-\d{3,})\b/g;
  var SAFE_ID = /^(LR|FND|EVD)-[0-9A-Za-z]+$/;
  var STRONG = ["elimination", "substitution", "engineering"];

  function flat(v) {
    if (v === null || v === undefined) return "";
    if (Array.isArray(v)) return v.map(flat).join(" ");
    if (typeof v === "object") return Object.keys(v).map(function (k) { return flat(v[k]); }).join(" ");  /* values only */
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

  /* ------------------------------------------------------------------ browser rendering */

  var D, els = {}, pendingCtx = null;
  var state = {lens: "all", priority: "", owner: "", level: "", hoc: "", q: ""};
  var GROUPS = [
    ["Causation", ["hfacs_level", "causal_role", "barrier", "hazard", "activity", "performance_mode"]],
    ["Organisation", ["owner_entity", "tiers", "org_system", "audiences", "learning_level", "formats", "ml_id"]],
    ["Risk", ["priority", "worst_case", "transferability", "pattern", "precursors"]],
    ["Evidence quality", ["evidence_strength", "confidence", "comparison", "reason_class"]]
  ];
  var DEDICATED = ["lr_id", "title", "lesson", "context", "finding_ids", "evidence_ids", "tier_messages", "recommendations"];
  var REC_KNOWN = ["what", "level_barrier", "evidence_basis", "hoc_tier", "leading_indicator"];
  var FND_SHOWN = ["id", "code", "name", "level", "rating", "classification", "label", "short", "justification",
                   "causal", "roles", "evidence", "clusters", "votes"];
  var EVD_SHOWN = ["id", "type", "description", "links"];
  var DOWN_RX = /^(downgrade|reject|remove)$/i;

  function h(tag, attrs, kids) {
    var el = document.createElement(tag);
    Object.keys(attrs || {}).forEach(function (k) {
      var v = attrs[k];
      if (v === null || v === undefined || v === false) return;
      if (k === "class") el.className = v;
      else if (k === "text") el.textContent = v;
      else if (k.slice(0, 2) === "on") el.addEventListener(k.slice(2), v);
      else el.setAttribute(k, v === true ? "" : v);
    });
    (kids || []).forEach(function (c) {
      if (c === null || c === undefined || c === false) return;
      el.appendChild(typeof c === "string" ? document.createTextNode(c) : c);
    });
    return el;
  }
  function rich(text) {
    var span = h("span");
    tokenize(text).forEach(function (t) {
      span.appendChild(t.id ? h("a", {href: "#detail/" + t.id, class: "ref", text: t.id}) : document.createTextNode(t.text));
    });
    return span;
  }
  function chip(text, cls) { return h("span", {class: "chip" + (cls ? " " + cls : ""), text: String(text)}); }
  function humanKey(k) { return String(k).replace(/_/g, " "); }
  function label(k) { return (D.labels && D.labels[k]) || humanKey(k); }
  function isBlank(v) {
    return v === null || v === undefined || v === "" || (Array.isArray(v) && !v.length) ||
      (typeof v === "object" && !Array.isArray(v) && !Object.keys(v).length);
  }
  function valueNode(v) {
    if (Array.isArray(v)) {
      if (v.every(function (x) { return x === null || typeof x !== "object"; })) return rich(v.join(", "));
      return h("ul", {class: "plain"}, v.map(function (x) { return h("li", null, [valueNode(x)]); }));
    }
    if (v !== null && typeof v === "object") return fieldList(v, Object.keys(v), humanKey);
    return rich(v);
  }
  function fieldList(obj, keys, labeller) {
    var lab = labeller || label, kids = [];
    keys.forEach(function (k) {
      if (!isBlank(obj[k])) { kids.push(h("dt", {text: lab(k)})); kids.push(h("dd", null, [valueNode(obj[k])])); }
    });
    return kids.length ? h("dl", {class: "fields"}, kids) : null;
  }
  function kv(name, value) { return h("p", {class: "kv"}, [h("b", {text: name + ": "}), valueNode(value)]); }
  function trunc(s, n) { s = String(s || ""); return s.length > n ? s.slice(0, n - 1) + "…" : s; }
  function entityName(code) {
    var n = D.taxonomy && D.taxonomy.entities && D.taxonomy.entities[code];
    return n ? code + " " + n : String(code);
  }
  function tierName(t) {
    var n = (D.tier_labels && D.tier_labels[t]) || (D.taxonomy && D.taxonomy.tiers && D.taxonomy.tiers[t]) || "";
    return (t + " " + n).trim();
  }
  function tiersOf(e) {
    var list = Array.isArray(e.tiers) ? e.tiers.map(String)
      : String(e.tiers || "").split(/[^A-Za-z0-9]+/).filter(function (x) { return /^T\d$/.test(x); });
    return list.length ? list : Object.keys(e.tier_messages || {}).sort();
  }

  function findingNode(fid, lr) {
    var f = D.findings[fid];
    if (!f) return h("p", {class: "missing", "data-ref": fid}, [h("span", {class: "id", text: fid}), " not in workspace"]);
    var cl = f.clusters || {}, votes = f.votes || [];
    var down = votes.some(function (v) { return DOWN_RX.test(String(v.vote || "")); });
    var also = (D.byFinding[fid] || []).filter(function (x) { return x !== lr; });
    var extra = Object.keys(f).filter(function (k) { return FND_SHOWN.indexOf(k) < 0; });
    return h("details", {class: "fnd", "data-ref": fid}, [
      h("summary", null, [
        h("span", {class: "id", text: fid}),
        h("span", {class: "code", text: [f.code, f.name].filter(Boolean).join(" · ")}),
        f.level !== null && f.level !== undefined ? chip("L" + f.level) : null,
        f.rating !== null && f.rating !== undefined ? chip("rating " + f.rating) : null,
        f.classification ? chip(f.classification) : null,
        down ? chip("reviewer downgrade vote", "warn") : null,
        h("span", {class: "lab", text: f.label || ""})]),
      h("div", {class: "fbody"}, [
        f.short ? kv("Summary", f.short) : null,
        f.justification ? kv("Justification", f.justification) : null,
        f.causal ? kv("Causal reasoning", f.causal) : null,
        (f.roles || []).length ? kv("Roles", f.roles.join("; ")) : null,
        (cl.F || []).length ? kv("Entities", cl.F.map(entityName).join("; ")) : null,
        (cl.T || []).length ? kv("Tiers", cl.T.map(tierName).join("; ")) : null,
        (cl.R || []).length ? kv("Relations", cl.R.join(", ")) : null,
        (f.evidence || []).length ? kv("Evidence", f.evidence.join(", ")) : null,
        also.length ? kv("Also in", also.join(", ")) : null,
        votes.length ? kv("Reviewer votes", votes.map(function (v) {
          return v.vote + (v.reason ? " (" + v.reason + ")" : ""); }).join("; ")) : null,
        fieldList(f, extra, humanKey)])
    ]);
  }

  function evidenceNode(eid, e) {
    var v = D.evidence[eid];
    if (!v) return h("p", {class: "missing", "data-ref": eid}, [h("span", {class: "id", text: eid}), " not in workspace"]);
    var citedBy = (e.finding_ids || []).filter(function (fid) {
      return D.findings[fid] && (D.findings[fid].evidence || []).indexOf(eid) >= 0; });
    var extra = Object.keys(v).filter(function (k) { return EVD_SHOWN.indexOf(k) < 0; });
    return h("details", {class: "evd", "data-ref": eid}, [
      h("summary", null, [
        h("span", {class: "id", text: eid}),
        v.type ? chip(v.type) : null,
        (e.evidence_ids || []).indexOf(eid) >= 0 ? chip("cited by the learning", "acc") : null,
        h("span", {class: "lab", text: trunc(v.description, 160)})]),
      h("div", {class: "fbody"}, [
        v.description ? kv("Description", v.description) : null,
        (v.links || []).length ? h("ul", {class: "links"}, v.links.map(function (l) {
          return h("li", null, [h("b", {text: (l.code || "") + ": "}), rich(l.relevance || ""),
            l.reference ? h("blockquote", null, [rich(l.reference)]) : null]); })) : null,
        citedBy.length ? kv("Cited by", citedBy.join(", ")) : null,
        fieldList(v, extra, humanKey)])
    ]);
  }

  var SECTIONS = {
    lesson: function (e) { return e.lesson ? {title: "Lesson", node: h("p", null, [valueNode(e.lesson)])} : null; },
    context: function (e) {
      return e.context ? {title: "What happened and why it made sense", node: h("p", null, [valueNode(e.context)])} : null;
    },
    warn: function (e) { return isBlank(e.precursors) ? null : {title: "Warning signs", node: h("div", null, [valueNode(e.precursors)])}; },
    classification: function (e) {
      var node = h("div"), grouped = [];
      GROUPS.forEach(function (g) {
        grouped = grouped.concat(g[1]);
        var dl = fieldList(e, g[1]);
        if (dl) { node.appendChild(h("h4", {class: "grp", text: g[0]})); node.appendChild(dl); }
      });
      var other = Object.keys(e).filter(function (k) { return DEDICATED.indexOf(k) < 0 && grouped.indexOf(k) < 0; });
      var odl = fieldList(e, other);
      if (odl) { node.appendChild(h("h4", {class: "grp", text: "Other fields"})); node.appendChild(odl); }
      return node.childNodes.length ? {title: "Classification", node: node} : null;
    },
    risk: function (e, d) {
      var counts = {};
      (d.hoc || []).forEach(function (t) { counts[t] = (counts[t] || 0) + 1; });
      var tiers = (D.hoc_order || []).concat(["unclassified"]).filter(function (t) { return counts[t]; });
      return {title: "Risk and control strength", node: h("div", null, [
        fieldList(e, ["priority", "worst_case", "transferability"]),
        h("p", {class: "strip"}, [h("b", {text: "Control strength: "})].concat(
          tiers.map(function (t) { return chip(t + " × " + counts[t], "hoc " + t); })))])};
    },
    quality: function (e) {
      var dl = fieldList(e, ["evidence_strength", "confidence", "comparison", "reason_class"]);
      return dl ? {title: "Evidence quality", node: dl} : null;
    },
    recs: function (e, d) {
      var recs = e.recommendations || [];
      if (!recs.length) return null;
      return {title: "Recommendations (" + recs.length + ")", node: h("ol", {class: "recs"}, recs.map(function (r, i) {
        var t = (d.hoc || [])[i] || "unclassified";
        var extra = Object.keys(r).filter(function (k) { return REC_KNOWN.indexOf(k) < 0; });
        return h("li", {class: "rec"}, [
          h("p", {class: "what"}, [chip(t, "hoc " + t), " ", rich(r.what || "")]),
          r.hoc_tier && String(r.hoc_tier).toLowerCase() !== t ? kv("Control tier as written", r.hoc_tier) : null,
          r.level_barrier ? kv("HFACS level and barrier", r.level_barrier) : null,
          r.evidence_basis ? kv("Evidence basis", r.evidence_basis) : null,
          r.leading_indicator ? h("p", {class: "kpi"}, [h("b", {text: "Leading indicator: "}), rich(r.leading_indicator)]) : null,
          fieldList(r, extra, humanKey)]);
      }))};
    },
    tiers: function (e) {
      var tm = e.tier_messages || {}, keys = Object.keys(tm).sort();
      if (!keys.length) return null;
      return {title: "Tier messages (" + keys.length + ")", node: h("table", {class: "tm"}, [h("tbody", null,
        keys.map(function (t) { return h("tr", null, [h("th", {scope: "row", text: tierName(t)}), h("td", null, [valueNode(tm[t])])]); }))])};
    },
    findings: function (e) {
      var ids = e.finding_ids || [];
      if (!ids.length) return null;
      if (!Object.keys(D.findings).length) return {title: "Findings (" + ids.length + ")", node: kv("Finding IDs", ids.join(", "))};
      return {title: "Findings (" + ids.length + ")", node: h("div", null,
        sortFindings(ids, D.findings).map(function (fid) { return findingNode(fid, e.lr_id); }))};
    },
    evidence: function (e) {
      var ids = evidenceIdsFor(e, D);
      if (!ids.length) return null;
      if (!Object.keys(D.evidence).length) return {title: "Evidence (" + ids.length + ")", node: kv("Evidence IDs", ids.join(", "))};
      return {title: "Evidence (" + ids.length + ")", node: h("div", null, ids.map(function (eid) { return evidenceNode(eid, e); }))};
    }
  };

  function cardNode(e, spec) {
    var d = (D.derived || {})[e.lr_id] || {};
    var msg = spec.tier && e.tier_messages && e.tier_messages[spec.tier];
    var p = e.priority === null || e.priority === undefined ? "?" : String(e.priority);
    var meta = [chip(entityName(d.entity || e.owner_entity || "unset"))]
      .concat(tiersOf(e).map(function (t) { return chip(t, "tier"); }))
      .concat([d.level ? chip(d.level) : null,
               chip("strongest: " + (d.strongest || "unclassified"), "hoc " + (d.strongest || "")),
               chip((e.finding_ids || []).length + " findings"), chip(evidenceIdsFor(e, D).length + " evidence"),
               e.confidence ? chip("confidence " + e.confidence) : null]);
    var body = h("div", {class: "lr-body"});
    if (msg) body.appendChild(h("div", {class: "callout"}, [h("b", {text: tierName(spec.tier) + ": "}), valueNode(msg)]));
    spec.order.forEach(function (sid) {
      var s = SECTIONS[sid](e, d);
      if (s) body.appendChild(h("details", {class: "sec sec-" + sid, open: spec.open.indexOf(sid) >= 0},
        [h("summary", {text: s.title}), s.node]));
    });
    return h("article", {class: "lr", id: "lr-" + e.lr_id}, [h("details", {class: "card"}, [
      h("summary", {class: "lr-head"}, [
        h("span", {class: "id", text: e.lr_id || "?"}), chip("P" + p, "p" + p), h("span", {class: "t", text: e.title || ""}),
        h("span", {class: "pv", text: trunc(msg || e.lesson || "", 240)}),
        h("span", {class: "meta"}, meta)]),
      body])]);
  }

  function banner() {
    var reg = D.register || {};
    var extra = Object.keys(reg).filter(function (k) { return k !== "title" && k !== "source"; });
    return h("div", {class: "banner"}, [
      h("p", null, [h("b", {text: "Learning purposes: not a statutory document. "}), reg.title || "Learnings Register"]),
      reg.source ? h("p", {class: "src"}, ["Source: ", rich(reg.source)]) : null,
      extra.length ? h("details", null, [h("summary", {text: "Register details"}), fieldList(reg, extra, humanKey)]) : null]);
  }

  function coverage() {
    var u = D.uncovered || [];
    if (!u.length) return h("p", {class: "m", text: "Every finding in the workspace is covered by a learning."});
    return h("details", {class: "coverage", id: "coverage"}, [
      h("summary", {text: "Findings not covered by any learning (" + u.length + ")"}),
      h("div", null, u.map(function (x) {
        return h("div", {class: "unc"}, [h("p", {class: "m"}, [h("span", {class: "id", text: x.id}), " " + (x.reason || "")]),
          findingNode(x.id, null)]); }))]);
  }

  function selectBox(name, text, opts) {
    var sel = h("select", {name: name}, opts.map(function (o) { return h("option", {value: o.value, text: o.label}); }));
    sel.addEventListener("change", function () {
      state[name] = sel.value;
      if (name === "lens") renderCards(); else applyFilters();
    });
    return h("label", null, [text, sel]);
  }

  function toolbar() {
    var dv = D.derived || {};
    function opts(values, fmt) {
      return [{value: "", label: "All"}].concat(uniq(values.filter(Boolean)).sort().map(function (v) {
        return {value: v, label: fmt ? fmt(v) : v}; }));
    }
    var q = h("input", {type: "search", placeholder: "Search learnings, findings, evidence"});
    var timer = null;
    q.addEventListener("input", function () {
      clearTimeout(timer);
      timer = setTimeout(function () { state.q = q.value; applyFilters(); }, 150);
    });
    return h("div", {class: "toolbar", role: "search"}, [
      selectBox("lens", "View as", lensesFor(D)),
      selectBox("priority", "Priority", opts(D.entries.map(function (e) {
        return e.priority === null || e.priority === undefined ? "" : String(e.priority); }), function (v) { return "P" + v; })),
      selectBox("owner", "Owner", opts(D.entries.map(function (e) { return (dv[e.lr_id] || {}).entity; }), entityName)),
      selectBox("level", "HFACS level", opts(D.entries.map(function (e) { return (dv[e.lr_id] || {}).level; }))),
      selectBox("hoc", "Control tier", opts([].concat.apply([], D.entries.map(function (e) { return (dv[e.lr_id] || {}).hoc || []; })))),
      h("label", null, ["Search", q]),
      h("span", {class: "btns"}, [
        h("button", {type: "button", text: "Expand all", onclick: function () { setOpen(true); }}),
        h("button", {type: "button", text: "Collapse all", onclick: function () { setOpen(false); }}),
        h("button", {type: "button", text: "Print", onclick: function () { window.print(); }})])]);
  }

  function setOpen(on) {
    els.panel.querySelectorAll("details").forEach(function (d) { if (!d.closest("[hidden]")) d.open = on; });
  }

  function renderSummary(visible) {
    var s = summarise(visible, D), total = D.entries.length;
    var kpis = [["Learnings", s.learnings], ["Priority-1", s.p1], ["Recommendations", s.recs],
                ["Findings covered", s.findings + " of " + ((D.totals || {}).findings || s.findings)],
                ["Evidence items", s.evidence], ["Fixes above administrative tier", s.strongPct + "%"]];
    els.summary.textContent = "";
    kpis.forEach(function (k) { els.summary.appendChild(h("div", null, [h("b", {text: String(k[1])}), h("span", {text: k[0]})])); });
    els.showing.textContent = visible.length < total ? "Showing " + visible.length + " of " + total + " learnings"
      : "All " + total + " learnings";
  }

  function renderCards() {
    var spec = lensSpec(state.lens);
    els.list.textContent = "";
    sortEntries(D.entries).forEach(function (e) { els.list.appendChild(cardNode(e, spec)); });
    applyFilters();
  }

  function applyFilters() {
    var spec = lensSpec(state.lens), visible = [];
    var f = {tier: spec.tier, priority: state.priority, owner: state.owner, level: state.level, hoc: state.hoc, q: state.q};
    sortEntries(D.entries).forEach(function (e) {
      var ok = matches(e, D, f), card = document.getElementById("lr-" + e.lr_id);
      if (card) card.hidden = !ok;
      if (ok) visible.push(e);
    });
    renderSummary(visible);
  }

  function resetFilters() {
    state = {lens: "all", priority: "", owner: "", level: "", hoc: "", q: ""};
    els.panel.querySelectorAll(".toolbar select").forEach(function (s) { s.value = s.name === "lens" ? "all" : ""; });
    var q = els.panel.querySelector(".toolbar input");
    if (q) q.value = "";
    renderCards();
  }

  function findTarget(id, ctx) {
    if (!SAFE_ID.test(id)) return null;
    if (id.indexOf("LR-") === 0) {
      var c = document.getElementById("lr-" + id);
      return c && !c.hidden ? c : null;
    }
    var sel = '[data-ref="' + id + '"]';
    var card = ctx ? document.getElementById(ctx) : null;
    var t = card && !card.hidden ? card.querySelector(sel) : null;
    if (t) return t;
    var all = els.panel.querySelectorAll(sel);
    for (var i = 0; i < all.length; i++) if (!all[i].closest("[hidden]")) return all[i];
    return null;
  }

  function go(id, ctx) {
    var t = findTarget(id, ctx);
    var known = id.indexOf("LR-") === 0 ? D.entries.some(function (e) { return e.lr_id === id; })
      : Boolean(D.findings[id] || D.evidence[id]);
    if (!t && known) { resetFilters(); t = findTarget(id, ctx); }
    if (!t) return;
    if (t.tagName === "ARTICLE") { var card = t.querySelector("details.card"); if (card) card.open = true; }
    for (var n = t; n && n !== els.panel; n = n.parentElement) if (n.tagName === "DETAILS") n.open = true;
    t.scrollIntoView({block: "start"});
    t.classList.add("flash");
    setTimeout(function () { t.classList.remove("flash"); }, 1600);
  }

  function showTab(name) {
    ["overview", "detail"].forEach(function (n) {
      var p = document.getElementById("tab-" + n), t = document.getElementById("t-" + n), on = n === name;
      if (p) p.hidden = !on;
      if (t) { t.setAttribute("aria-selected", on ? "true" : "false"); t.tabIndex = on ? 0 : -1; }
    });
  }

  function route() {
    var p = parseHash(location.hash);
    showTab(p.tab);
    if (p.id) go(p.id, pendingCtx);
    pendingCtx = null;
  }

  function wire() {
    ["overview", "detail"].forEach(function (n) {
      var t = document.getElementById("t-" + n);
      if (t) t.addEventListener("click", function () {
        var want = "#" + n;
        if (location.hash === want) route(); else location.hash = want;
      });
    });
    var bar = document.querySelector("[role=tablist]");
    if (bar) bar.addEventListener("keydown", function (ev) {
      if (ev.key !== "ArrowLeft" && ev.key !== "ArrowRight") return;
      var cur = document.getElementById("t-overview").getAttribute("aria-selected") === "true";
      var next = document.getElementById(cur ? "t-detail" : "t-overview");
      next.focus();
      next.click();
      ev.preventDefault();
    });
    window.addEventListener("hashchange", route);
    document.addEventListener("click", function (ev) {
      var a = ev.target.closest ? ev.target.closest("a[href^='#detail']") : null;
      if (!a) return;
      var card = a.closest("article.lr");
      pendingCtx = card ? card.id : null;
      if (location.hash === a.getAttribute("href")) { ev.preventDefault(); route(); }
    });
    window.addEventListener("beforeprint", function () {
      document.querySelectorAll("[role=tabpanel]:not([hidden]) details").forEach(function (d) {
        if (!d.closest("[hidden]")) d.open = true; });
    });
  }

  function init() {
    var node = document.getElementById("pmlc-data");
    els.panel = document.getElementById("tab-detail");
    if (!node || !els.panel) return;
    D = JSON.parse(node.textContent);
    D.entries = D.entries || [];
    D.findings = D.findings || {};
    D.evidence = D.evidence || {};
    D.byFinding = {};
    D.entries.forEach(function (e) {
      (e.finding_ids || []).forEach(function (f) { (D.byFinding[f] = D.byFinding[f] || []).push(e.lr_id); });
    });
    els.summary = h("div", {class: "k sum"});
    els.showing = h("p", {class: "showing"});
    els.list = h("div", {class: "cards"});
    [banner(), els.summary, toolbar(), els.showing, els.list, coverage()].forEach(function (n) { els.panel.appendChild(n); });
    renderCards();
    wire();
    route();
  }

  var API = {tokenize: tokenize, parseHash: parseHash, lensSpec: lensSpec, lensesFor: lensesFor, matches: matches,
             sortEntries: sortEntries, sortFindings: sortFindings, summarise: summarise, evidenceIdsFor: evidenceIdsFor};
  if (typeof module !== "undefined" && module.exports) { module.exports = API; return; }
  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", init); else init();
})();
