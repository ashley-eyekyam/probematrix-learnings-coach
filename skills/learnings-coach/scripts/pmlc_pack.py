"""Learning packs: the JSON an audience or analysis skill writes, checked against the workspace and rendered
to a self-contained HTML page and Markdown. `pmlc.py check-pack` and `pmlc.py pack` call into this module.
Schema reference: references/pack-schema.md."""
from __future__ import annotations

import collections
import copy
import datetime as dt
import html
import json
import re
import sys
from pathlib import Path

import pmlc as core

SCHEMA_VERSION = 1
STATUS_PHRASE = "Learning purposes: not a statutory document"
PACK_NAME_RX = re.compile(r"^(?:[a-z0-9]+(?:-[a-z0-9]+)*|dossier-F\d+[a-z]?)$")
SLUG_RX = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
ID_RX = re.compile(r"\b(FND-[0-9A-Za-z]{4,}|EVD-\d{3,})\b")
DATE_RX = re.compile(r"^\d{4}(?:-\d{2}(?:-\d{2})?)?$")
MAX_BOTTOM_LINE = 7

# Item kinds: required fields, optional fields, and whether at least one citation is required.
KINDS = {
    "para": {"req": ["text"], "opt": []},
    "check": {"req": ["text"], "opt": ["hold_point", "when"]},
    "question": {"req": ["question", "why"], "opt": ["answer", "good_evidence", "to"]},
    "recommendation": {"req": ["change", "indicator", "hoc_tier"], "opt": ["barrier", "owner", "by_when"], "cite": True},
    "decision": {"req": ["decision"], "opt": ["options", "trade_offs", "owner", "by_when"]},
    "indicator": {"req": ["name", "measure"], "opt": ["deterioration", "owner"]},
    "card": {"req": ["title", "what_happened", "warning_signs", "good_looks_like"], "opt": ["why_made_sense", "discussion"],
             "cite": True},
    "scenario": {"req": ["situation", "prompts"], "opt": []},
    "table": {"req": ["columns", "rows"], "opt": ["row_cites", "row_supporting_cites", "finding_notes"]},
    "test_point": {"req": ["requirement", "sample", "conformity_evidence"], "opt": ["red_flags"], "cite": True},
    "module": {"req": ["title", "objective", "content"], "opt": ["audience", "duration", "assessment"]},
    "barrier": {"req": ["barrier", "failure_mode", "hoc_tier"], "opt": ["type", "fix", "owner", "state", "indicator"],
                "cite": True},
    "timeline": {"req": ["events"], "opt": []},
    "graph": {"req": ["nodes", "edges"], "opt": []},
    "learning": {"req": ["lesson"], "opt": ["explanation", "owner"], "cite": True},
}
STR_LIST_FIELDS = {"options", "warning_signs", "discussion", "prompts", "columns", "content", "assessment", "red_flags"}
OBJ_LIST_FIELDS = {"rows", "row_cites", "row_supporting_cites", "events", "nodes", "edges"}
MAP_FIELDS = {"finding_notes"}
BOOL_FIELDS = {"hold_point"}
FOLLOW_UP_COLUMNS = ["Finding", "Evidence to collect", "Key questions", "Suggested interviews", "Causal hypothesis"]
FOLLOW_UP_KEYS = ["evidence_to_collect", "key_questions", "suggested_interviews", "causal_hypothesis"]

Result = collections.namedtuple("Result", "problems warnings stats")


def _text(v) -> bool:
    return isinstance(v, str) and v.strip() != ""


def _id_list(v) -> bool:
    return isinstance(v, list) and all(isinstance(x, str) and ID_RX.fullmatch(x) for x in v)


def _iso_partial(v) -> bool:
    """YYYY-MM-DD, YYYY-MM or YYYY, and a real calendar date."""
    if not isinstance(v, str) or not DATE_RX.match(v):
        return False
    full = v + "-01-01"[len(v) - 4:] if len(v) < 10 else v      # 2022 -> 2022-01-01, 2022-03 -> 2022-03-01
    try:
        dt.date.fromisoformat(full)
    except ValueError:
        return False
    return True


def _walk_ids(v, path):
    """Yield (json-path, ID) for every Finding or Evidence ID in any string under v."""
    if isinstance(v, str):
        for m in ID_RX.finditer(v):
            yield path, m.group(1)
    elif isinstance(v, list):
        for i, x in enumerate(v):
            yield from _walk_ids(x, f"{path}[{i}]")
    elif isinstance(v, dict):
        for k, x in v.items():
            yield from _walk_ids(x, f"{path}.{k}" if path else str(k))


# Fields rendered with citation buttons. An ID anywhere else (headings, titles, badges, column headers, graph
# labels) is shown as plain text, so it is not a citation and does not count towards coverage.
INLINE_FIELDS = {
    "para": ["text"], "check": ["text"], "question": ["question", "why", "answer", "good_evidence"],
    "recommendation": ["change", "indicator"], "decision": ["decision", "options", "trade_offs"],
    "indicator": ["name", "measure", "deterioration", "owner"],
    "card": ["what_happened", "why_made_sense", "warning_signs", "good_looks_like", "discussion"],
    "scenario": ["situation", "prompts"], "table": ["rows"],
    "test_point": ["requirement", "sample", "conformity_evidence", "red_flags"],
    "module": ["objective", "content", "assessment"], "barrier": ["barrier", "failure_mode", "fix", "indicator"],
    "timeline": [], "graph": [], "learning": ["lesson", "explanation"],
}
CITE_FIELDS = ["cites", "row_cites", "row_supporting_cites", "supporting_cites"]
STRENGTHS = ("direct", "corroborated", "inferred")
BARRIER_STATES = ("absent", "degraded", "defeated", "worked partly", "worked")
TIME_RX = re.compile(r"(?:[01]\d|2[0-3]):[0-5]\d")          # used with fullmatch: "14:05", never "14:05\n"
GENERIC_FIELDS = ("kind", "id", "cites", "supporting_cites", "evidence_strength", "group")


def _pick(d, keys) -> dict:
    return {k: d[k] for k in keys if k in d} if isinstance(d, dict) else {}


def _citable_item(it) -> dict:
    """The parts of one item that render as citation buttons (same keys, so JSON paths are unchanged)."""
    if not isinstance(it, dict):
        return {}
    kind = it.get("kind")
    out = _pick(it, INLINE_FIELDS.get(kind if isinstance(kind, str) else "", []) + CITE_FIELDS)
    if kind == "timeline" and isinstance(it.get("events"), list):
        out["events"] = [_pick(e, ["text", "cites"]) for e in it["events"]]
    return out


def _citable(pack) -> dict:
    bl, secs, dq = pack.get("bottom_line"), pack.get("sections"), pack.get("data_quality")
    return {"data_quality": [_pick(n, ["text", "cites"]) for n in dq] if isinstance(dq, list) else [],
            "bottom_line": [_pick(e, ["text", "cites", "supporting_cites"]) for e in bl] if isinstance(bl, list) else [],
            "sections": [dict(_pick(s, ["intro"]),
                              items=[_citable_item(it) for it in s["items"]] if isinstance(s.get("items"), list) else [])
                         if isinstance(s, dict) else {} for s in secs] if isinstance(secs, list) else []}


def cited_ids(pack) -> tuple:
    """Ordered unique (finding IDs, evidence IDs) cited in the bottom line or sections: in cites lists, or inline in
    text that renders citation buttons."""
    fids, eids = [], []
    for _, x in _walk_ids(_citable(pack), ""):
        bucket = fids if x.startswith("FND-") else eids
        if x not in bucket:
            bucket.append(x)
    return fids, eids


def with_item_ids(pack) -> dict:
    """Deep copy in which every item has an id: its own, or <section-id>-<position>."""
    p = copy.deepcopy(pack)
    for s in p["sections"]:
        for n, it in enumerate(s["items"], 1):
            it.setdefault("id", f"{s['id']}-{n}")
    return p


def relevant_findings(w, scope=None) -> list:
    """Finding IDs a pack is expected to draw on: those matching its scope (the same filter as select), or,
    without a scope, the top-rated findings (rating equal to the workspace maximum, as classify counts them)."""
    if scope:
        a = core.select_args(entity=scope.get("entities") or None, tag=scope.get("tags") or None,
                             tier=scope.get("tiers") or None, relation=scope.get("relations") or None,
                             level=scope.get("levels") or None, entity_mode=scope.get("entity_mode") or "any",
                             top_rated=scope.get("min_rating") == "top",
                             min_rating=None if scope.get("min_rating") == "top" else scope.get("min_rating"))
        rel = {f["id"] for f, _ in core._filter(w, a)}
        return [f["id"] for f in w["findings"] if f["id"] in rel]
    top = max(((f.get("rating") or 0) for f in w["findings"]), default=0)
    return [f["id"] for f in w["findings"] if top and (f.get("rating") or 0) == top]


def _check_field(v, f, path, bad):
    if f in BOOL_FIELDS:
        if not isinstance(v, bool):
            bad(path, "must be true or false")
    elif f in STR_LIST_FIELDS:
        if not isinstance(v, list) or not v or not all(_text(x) for x in v):
            bad(path, "must be a non-empty list of text")
    elif f in OBJ_LIST_FIELDS:
        if not isinstance(v, list) or not v:
            bad(path, "must be a non-empty list")
    elif f in MAP_FIELDS:
        return                                   # shape checked by the kind's own check (_check_table)
    elif not _text(v):
        bad(path, "must be non-empty text")


def _check_table(it, ip, bad):
    cols, rows = it.get("columns"), it.get("rows")
    if not isinstance(cols, list) or not isinstance(rows, list):
        return
    for r, row in enumerate(rows):
        if not isinstance(row, list) or len(row) != len(cols):
            bad(f"{ip}.rows[{r}]", f"must have {len(cols)} cells like columns")
            continue
        for c, cell in enumerate(row):
            if isinstance(cell, bool) or not isinstance(cell, (str, int, float)):
                bad(f"{ip}.rows[{r}][{c}]", "must be text or a number")
    for f in ("row_cites", "row_supporting_cites"):
        rc = it.get(f)
        if rc is None:
            continue
        if not isinstance(rc, list) or len(rc) != len(rows):
            bad(f"{ip}.{f}", "must hold one list of IDs per row")
            continue
        for r, c in enumerate(rc):
            if not _id_list(c):
                bad(f"{ip}.{f}[{r}]", "must be a list of Finding or Evidence IDs")
    _check_finding_notes(it, rows, ip, bad)


def _check_finding_notes(it, rows, ip, bad):
    """investigator-coach: an optional note per finding on the follow-up table, for findings that share a row."""
    notes = it.get("finding_notes")
    if notes is None:
        return
    if it.get("id") != "follow-up":
        bad(f"{ip}.finding_notes", "only on the investigator-coach follow-up table")
        return
    if not isinstance(notes, dict) or not notes:
        bad(f"{ip}.finding_notes", "must be an object of Finding ID to note")
        return
    firsts = {x for row in rows if isinstance(row, list) and row and isinstance(row[0], str)
              for x in re.split(r"[\s,;]+", row[0]) if x}
    for x, v in notes.items():
        if x not in firsts:
            bad(f"{ip}.finding_notes.{x}", "not a Finding ID in this table's first column")
        elif not _text(v):
            bad(f"{ip}.finding_notes.{x}", "must be non-empty text")


def _check_timeline(it, ip, bad):
    events = it.get("events")
    if not isinstance(events, list):
        return
    for k, ev in enumerate(events):
        ep = f"{ip}.events[{k}]"
        if not isinstance(ev, dict):
            bad(ep, "must be an object")
            continue
        if not _iso_partial(ev.get("date")):
            bad(f"{ep}.date", "must be YYYY-MM-DD, YYYY-MM or YYYY")
        if not _text(ev.get("text")):
            bad(f"{ep}.text", "required")
        if "signal" in ev and not isinstance(ev["signal"], bool):
            bad(f"{ep}.signal", "must be true or false")
        if "time" in ev and not (isinstance(ev["time"], str) and TIME_RX.fullmatch(ev["time"])):
            bad(f"{ep}.time", "must be HH:MM (24-hour)")
        for f in ("received_by", "response"):
            if f in ev and not _text(ev[f]):
                bad(f"{ep}.{f}", "must be non-empty text")
        if "cites" in ev and not _id_list(ev["cites"]):
            bad(f"{ep}.cites", "must be a list of Finding or Evidence IDs")


def _check_barrier(it, ip, bad):
    if "state" in it and it["state"] not in BARRIER_STATES:
        bad(f"{ip}.state", f"must be one of {', '.join(BARRIER_STATES)}")


def _check_graph(it, ip, bad):
    nodes, edges = it.get("nodes"), it.get("edges")
    if not isinstance(nodes, list) or not isinstance(edges, list):
        return
    ids = set()
    for k, n in enumerate(nodes):
        np_ = f"{ip}.nodes[{k}]"
        if not isinstance(n, dict) or not _text(n.get("id")) or not _text(n.get("label")):
            bad(np_, "needs id and label")
            continue
        if n["id"] in ids:
            bad(f"{np_}.id", f"duplicate node id {n['id']!r}")
        ids.add(n["id"])
    for k, e in enumerate(edges):
        ep = f"{ip}.edges[{k}]"
        if not isinstance(e, dict):
            bad(ep, "must be an object")
            continue
        for end in ("from", "to"):
            if not isinstance(e.get(end), str) or e.get(end) not in ids:
                bad(f"{ep}.{end}", f"{e.get(end)!r} is not a node id")
        if "label" in e and not _text(e["label"]):
            bad(f"{ep}.label", "must be text")


def _check_extras(d, p, bad):
    """Optional on every item and bottom-line entry: supporting_cites, evidence_strength and (items) group."""
    if "supporting_cites" in d and not _id_list(d["supporting_cites"]):
        bad(f"{p}.supporting_cites", "must be a list of Finding or Evidence IDs")
    if "evidence_strength" in d and d["evidence_strength"] not in STRENGTHS:
        bad(f"{p}.evidence_strength", f"must be one of {', '.join(STRENGTHS)}")
    if "group" in d and not _text(d["group"]):
        bad(f"{p}.group", "must be non-empty text")


def _check_item(it, ip, bad, warn):
    if not isinstance(it, dict):
        bad(ip, "must be an object")
        return
    kind = it.get("kind")
    spec = KINDS.get(kind) if isinstance(kind, str) else None
    if spec is None:
        bad(f"{ip}.kind", f"unknown kind {kind!r}; one of: {', '.join(KINDS)}")
        return
    known = spec["req"] + spec["opt"]
    for f in spec["req"]:
        if f not in it:
            bad(f"{ip}.{f}", f"required for {kind}")
    for f in known:
        if f in it:
            _check_field(it[f], f, f"{ip}.{f}", bad)
    if "cites" in it and not _id_list(it["cites"]):
        bad(f"{ip}.cites", "must be a list of Finding or Evidence IDs")
    if spec.get("cite") and not (_id_list(it.get("cites")) and it.get("cites")):
        bad(f"{ip}.cites", f"a {kind} needs at least one Finding or Evidence ID")
    _check_extras(it, ip, bad)
    for f in it:
        if f not in known and f not in GENERIC_FIELDS:
            warn(f"{ip}.{f}", f"unknown field for {kind} (ignored)")
    if _text(it.get("hoc_tier")) and core.norm_hoc(it["hoc_tier"]) == "unclassified":
        bad(f"{ip}.hoc_tier", f"must name a hierarchy-of-controls tier: {', '.join(core.HOC_TIERS)}")
    {"table": _check_table, "timeline": _check_timeline, "graph": _check_graph,
     "barrier": _check_barrier}.get(kind, lambda *x: None)(it, ip, bad)
    if not spec.get("cite") and not any(True for _ in _walk_ids(_citable_item(it), "")):
        warn(ip, "no Finding or Evidence ID cited")


def _check_scope(scope, w, bad):
    if scope is None:
        return
    if not isinstance(scope, dict):
        bad("scope", "must be an object")
        return
    for k in scope:
        if k not in ("tiers", "levels", "entities", "tags", "min_rating", "relations", "entity_mode"):
            bad(f"scope.{k}", "unknown key; use tiers, levels, entities, tags, min_rating, relations, entity_mode")
    t, lv, en, mr = scope.get("tiers") or [], scope.get("levels") or [], scope.get("entities") or [], scope.get("min_rating")
    tg = scope.get("tags") or []
    if not isinstance(t, list) or any(not isinstance(x, str) or x not in core.TIER_LABELS for x in t):
        bad("scope.tiers", "a list of T1 to T5")
    if not isinstance(lv, list) or any(isinstance(x, bool) or x not in (1, 2, 3, 4) for x in lv):
        bad("scope.levels", "a list of 1 to 4")
    if not isinstance(en, list) or any(not isinstance(x, str) for x in en):
        bad("scope.entities", "a list of entity IDs like F02")
    if not isinstance(tg, list) or any(not isinstance(x, str) for x in tg):
        bad("scope.tags", "a list of tags like emergency")
        tg = []
    if mr is not None and mr != "top" and (isinstance(mr, bool) or not isinstance(mr, int)):
        bad("scope.min_rating", 'a whole number, "top" or null')
    rl = scope.get("relations") or []
    if not isinstance(rl, list) or any(not isinstance(x, str) for x in rl):
        bad("scope.relations", "a list of relation IDs like owner")
        rl = []
    elif "clusters" in w:
        known_rel = w["clusters"].get("taxonomy", {}).get("relations", {})
        for x in rl:
            if x not in known_rel:
                bad("scope.relations", f"{x} is not a relation in clusters.json ({', '.join(sorted(known_rel))})")
    if scope.get("entity_mode") not in (None, "any", "all"):
        bad("scope.entity_mode", 'must be "any" or "all"')
    if "clusters" in w and isinstance(en, list):
        known = w["clusters"].get("taxonomy", {}).get("entities", {})
        for x in en:
            if isinstance(x, str) and x not in known:
                bad("scope.entities", f"{x} is not an entity in clusters.json")
    if "clusters" in w and tg:
        tagmap = w["clusters"].get("taxonomy", {}).get("tags")
        if tagmap is None:
            bad("scope.tags", "clusters.json has no tags (it predates v2.0). Re-run classify")
        else:
            known = {x for ts in tagmap.values() for x in ts}
            for x in tg:
                if x not in known:
                    bad("scope.tags", f"{x} is not a tag in clusters.json")
    if (t or en or tg or rl) and "clusters" not in w:
        bad("scope", "tiers, entities and tags need clusters.json. Run: pmlc.py classify <ws>")


def _check_notes(pack, w, bad):
    dq = pack.get("data_quality")
    if dq is not None:
        if not isinstance(dq, list) or not dq:
            bad("data_quality", "must be a non-empty list of {text, cites}")
        else:
            for i, n in enumerate(dq):
                if not isinstance(n, dict) or not _text(n.get("text")):
                    bad(f"data_quality[{i}].text", "required")
                elif "cites" in n and not _id_list(n["cites"]):
                    bad(f"data_quality[{i}].cites", "must be a list of Finding or Evidence IDs")
    ex = pack.get("exclusions")
    if ex is None:
        return
    if not isinstance(ex, list) or not ex:
        bad("exclusions", "must be a non-empty list of {id, reason}")
        return
    F = {f["id"] for f in w["findings"]}
    seen = set()
    for i, e in enumerate(ex):
        if not isinstance(e, dict):
            bad(f"exclusions[{i}]", "must be an object with id and reason")
            continue
        x = e.get("id")
        if not (isinstance(x, str) and ID_RX.fullmatch(x) and x.startswith("FND-")):
            bad(f"exclusions[{i}].id", "must be a Finding ID")
        elif x not in F:
            bad(f"exclusions[{i}].id", f"{x} is not in this workspace")
        elif x in seen:
            bad(f"exclusions[{i}].id", f"{x} is listed twice")
        else:
            seen.add(x)
        if not _text(e.get("reason")):
            bad(f"exclusions[{i}].reason", "required")


def excluded_ids(pack) -> list:
    ex = pack.get("exclusions")
    return [e["id"] for e in ex if isinstance(e, dict) and isinstance(e.get("id"), str)] if isinstance(ex, list) else []


def _check_follow_up(secs, bad):
    tables = [it for s in secs if isinstance(s, dict) and isinstance(s.get("items"), list)
              for it in s["items"] if isinstance(it, dict) and it.get("id") == "follow-up"]
    if not tables or tables[0].get("kind") != "table" or tables[0].get("columns") != FOLLOW_UP_COLUMNS:
        bad("investigator-coach", f"needs a table item with id follow-up and columns {FOLLOW_UP_COLUMNS}")
        return
    seen = set()
    for r, row in enumerate(tables[0].get("rows") if isinstance(tables[0].get("rows"), list) else []):
        if not isinstance(row, list) or not row:
            continue
        cell = [x for x in re.split(r"[\s,;]+", row[0]) if x] if isinstance(row[0], str) else []
        if not cell or not all(ID_RX.fullmatch(x) and x.startswith("FND-") for x in cell):
            bad(f"follow-up.rows[{r}][0]", "must be one or more Finding IDs")
            continue
        for x in cell:
            if x in seen:
                bad(f"follow-up.rows[{r}][0]", f"{x} already has a row")
            seen.add(x)


def check_pack(pack, w) -> Result:
    """Every problem that would make the pack wrong or unrenderable (problems), plus advice (warnings)."""
    P, W = [], []

    def bad(path, msg):
        P.append(f"{path}: {msg}")

    def warn(path, msg):
        W.append(f"{path}: {msg}")

    if not isinstance(pack, dict):
        return Result(["(root): a pack must be a JSON object"], [], {})
    for k, typ in (("pack", str), ("title", str), ("audience", str), ("status", str),
                   ("bottom_line", list), ("sections", list)):
        v = pack.get(k)
        if k not in pack:
            bad(k, "required")
        elif not isinstance(v, typ) or not v or (typ is str and not v.strip()):
            bad(k, f"must be a non-empty {'list' if typ is list else 'string'}")
    if pack.get("schema") != SCHEMA_VERSION or isinstance(pack.get("schema"), bool):
        bad("schema", f"must be {SCHEMA_VERSION}")
    if _text(pack.get("pack")) and not PACK_NAME_RX.fullmatch(pack["pack"]):
        bad("pack", "must be lowercase words joined by hyphens (or dossier-F<nn>)")
    if _text(pack.get("status")) and STATUS_PHRASE not in pack["status"]:
        bad("status", f'must contain "{STATUS_PHRASE}"')
    inc = pack.get("incident")
    if inc is not None:
        if not isinstance(inc, dict):
            bad("incident", "must be an object with title and/or date")
        else:
            for k in inc:
                if k not in ("title", "date"):
                    bad(f"incident.{k}", "unknown key; use title, date")
            if "title" in inc and not _text(inc["title"]):
                bad("incident.title", "must be non-empty text")
            if "date" in inc and not (isinstance(inc["date"], str) and len(inc["date"]) == 10 and _iso_partial(inc["date"])):
                bad("incident.date", "must be YYYY-MM-DD")
    bl = pack.get("bottom_line") if isinstance(pack.get("bottom_line"), list) else []
    if len(bl) > MAX_BOTTOM_LINE:
        bad("bottom_line", f"at most {MAX_BOTTOM_LINE} entries (got {len(bl)})")
    for i, e in enumerate(bl):
        if not isinstance(e, dict) or not _text(e.get("text")):
            bad(f"bottom_line[{i}].text", "required")
            continue
        if not (_id_list(e.get("cites")) and e.get("cites")):
            bad(f"bottom_line[{i}].cites", "every bottom-line entry needs at least one Finding or Evidence ID")
        _check_extras(e, f"bottom_line[{i}]", bad)
    _check_scope(pack.get("scope"), w, bad)
    _check_notes(pack, w, bad)

    secs = pack.get("sections") if isinstance(pack.get("sections"), list) else []
    seen, n_items = set(), 0
    for si, s in enumerate(secs):
        sp = f"sections[{si}]"
        if not isinstance(s, dict):
            bad(sp, "must be an object")
            continue
        sid = s.get("id")
        if not isinstance(sid, str) or not SLUG_RX.fullmatch(sid):
            bad(f"{sp}.id", "required: lowercase words joined by hyphens")
            sid = None
        elif sid in seen:
            bad(f"{sp}.id", f"duplicate id {sid!r}")
        else:
            seen.add(sid)
        if not _text(s.get("heading")):
            bad(f"{sp}.heading", "required")
        if "intro" in s and not _text(s.get("intro")):
            bad(f"{sp}.intro", "must be non-empty text when present")
        items = s.get("items")
        if not isinstance(items, list) or not items:
            bad(f"{sp}.items", "required: a non-empty list")
            continue
        for ii, it in enumerate(items):
            n_items += 1
            ip = f"{sp}.items[{ii}]"
            iid = it.get("id") if isinstance(it, dict) else None
            if iid is not None and not (isinstance(iid, str) and SLUG_RX.fullmatch(iid)):
                bad(f"{ip}.id", "must be lowercase words joined by hyphens")
                iid = None
            elif iid is None and sid:
                iid = f"{sid}-{ii + 1}"
            if iid is not None:
                if iid in seen:
                    bad(f"{ip}.id", f"duplicate id {iid!r}")
                seen.add(iid)
            _check_item(it, ip, bad, warn)
    if pack.get("pack") == "investigator-coach":
        _check_follow_up(secs, bad)

    F = {f["id"] for f in w["findings"]}
    E = set(w.get("evidence", {}))
    ids, cit = set(), set()
    for path, x in _walk_ids(_citable(pack), ""):
        ids.add(x)
        cit.add((path, x))
        if x not in (F if x.startswith("FND-") else E):
            bad(path, f"{x} is not in this workspace")
    for path, x in _walk_ids({"data_quality": pack.get("data_quality"), "bottom_line": pack.get("bottom_line"),
                              "sections": pack.get("sections")}, ""):
        if (path, x) not in cit:
            warn(path, f"{x} is shown as plain text, not a citation; put it in cites")
    for i, x in enumerate(excluded_ids(pack)):
        if x in ids:
            bad(f"exclusions[{i}].id", f"{x} is also cited; a finding is either cited or left out on purpose")
    if not P:
        rel = [x for x in relevant_findings(w, pack.get("scope")) if x not in excluded_ids(pack)]
        got = len(set(rel) & ids)
        if rel and got * 4 < len(rel):
            W.append(f"coverage: cites {got} of {len(rel)} relevant findings (under a quarter)")
    return Result(P, W, {"sections": len(secs), "items": n_items, "cited": len(ids)})


def load_pack(path) -> tuple:
    """(parsed JSON, None) or (None, a problem line)."""
    try:
        return json.loads(Path(path).read_text(encoding="utf-8")), None
    except FileNotFoundError:
        return None, f"(file): {path} not found"
    except json.JSONDecodeError as e:
        return None, f"(json): invalid JSON at line {e.lineno} column {e.colno}: {e.msg}"
    except (OSError, UnicodeDecodeError, RecursionError) as e:
        return None, f"(file): cannot read {path} as UTF-8 JSON ({e.__class__.__name__})"


def _checked(a):
    """Load the workspace and pack, print warnings, exit listing every problem; else return (w, pack, result)."""
    w = core.load_ws(a.ws)
    pack, err = load_pack(a.pack)
    res = Result([err], [], {}) if err else check_pack(pack, w)
    if not err and isinstance(pack, dict) and isinstance(pack.get("pack"), str):
        try:
            core.record_pack_check(a.ws, pack["pack"], a.pack, not res.problems, len(res.problems))
        except OSError:
            pass
    for x in res.warnings:
        print(f"warning: {x}")
    if res.problems:
        for x in res.problems:
            print(x, file=sys.stderr)
        sys.exit(f"{len(res.problems)} problem(s) in {a.pack}.{' Nothing written.' if a.cmd == 'pack' else ''}")
    return w, pack, res


def cmd_check_pack(a):
    _, _, res = _checked(a)
    s = res.stats
    print(f"OK: {s['sections']} sections, {s['items']} items, {s['cited']} cited IDs")


# ----------------------------------------------------------------------------- graph layout

NODE_W, NODE_H, GAP_X, GAP_Y, PAD, CURVE = 190, 46, 70, 18, 12, 44
LABEL_MAX = 28


def _clip(s, n=LABEL_MAX):
    s = " ".join(str(s).split())
    return s if len(s) <= n else s[: n - 1] + "…"


def layout_graph(nodes, edges, uid, max_nodes=60) -> dict:
    """Deterministic left-to-right layered drawing of a small graph as inline SVG (no library).
    Layers follow the longest path from the sources; back edges (found by depth-first search in input order)
    are ignored for layering and drawn as dashed curves below the nodes; a link that skips a layer arcs above them,
    so it never lies on a chain through the layers between; four barycentre passes order each layer.
    Over max_nodes, the nodes with the most links are kept and the rest counted in 'omitted'."""
    order = [n["id"] for n in nodes]
    label = {n["id"]: n.get("label") or n["id"] for n in nodes}
    deg = collections.Counter()
    for e in edges:
        deg[e["from"]] += 1
        deg[e["to"]] += 1
    omitted = max(0, len(order) - max_nodes)
    if omitted:
        first = {i: k for k, i in enumerate(order)}
        keep = set(sorted(order, key=lambda i: (-deg[i], first[i]))[:max_nodes])
        order = [i for i in order if i in keep]
    rank = {i: k for k, i in enumerate(order)}
    E, seen = [], set()
    for e in edges:
        u, v = e["from"], e["to"]
        if u in rank and v in rank and u != v and (u, v) not in seen:
            seen.add((u, v))
            E.append((u, v, e.get("label") or ""))

    succ = {i: [] for i in order}
    for u, v, _ in E:
        succ[u].append(v)
    state, back = {}, set()

    def dfs(u):
        state[u] = 1
        for v in succ[u]:
            if state.get(v) == 1:
                back.add((u, v))
            elif v not in state:
                dfs(v)
        state[u] = 2

    for i in order:
        if i not in state:
            dfs(i)
    fwd = [(u, v) for u, v, _ in E if (u, v) not in back]
    layer = {i: 0 for i in order}
    for _ in range(len(order)):                       # longest path by relaxation; n <= max_nodes
        changed = False
        for u, v in fwd:
            if layer[v] < layer[u] + 1:
                layer[v], changed = layer[u] + 1, True
        if not changed:
            break
    cols = collections.defaultdict(list)
    for i in order:
        cols[layer[i]].append(i)
    pos = {i: k for c in cols.values() for k, i in enumerate(c)}
    preds = collections.defaultdict(list)
    for u, v in fwd:
        preds[v].append(u)
    for _ in range(4):
        for c in sorted(cols)[1:]:
            cols[c].sort(key=lambda i: (sum(pos[p] for p in preds[i]) / len(preds[i]) if preds[i] else pos[i], rank[i]))
            for k, i in enumerate(cols[c]):
                pos[i] = k

    ncols = (max(cols) + 1) if cols else 0
    nrows = max((len(c) for c in cols.values()), default=0)
    curved = any((u, v) in back or layer[v] <= layer[u] for u, v, _ in E)
    skips = {(u, v) for u, v, _ in E if (u, v) not in back and layer[v] > layer[u] + 1}
    top = CURVE if skips else 0
    width = PAD * 2 + ncols * NODE_W + max(0, ncols - 1) * GAP_X
    height = PAD * 2 + nrows * NODE_H + max(0, nrows - 1) * GAP_Y + (CURVE if curved else 0) + top
    xy = {i: (PAD + layer[i] * (NODE_W + GAP_X), PAD + top + pos[i] * (NODE_H + GAP_Y)) for i in order}
    esc = html.escape
    out = [f'<svg class="graph" viewBox="0 0 {width} {height}" width="{width}" height="{height}" role="group" '
           f'aria-label="Graph of {len(order)} nodes and {len(E)} links">',
           f'<defs><marker id="arr-{esc(uid)}" viewBox="0 0 10 10" refX="10" refY="5" markerWidth="7" markerHeight="7" '
           f'orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" fill="currentColor"/></marker></defs>']
    for u, v, lab in E:
        (x1, y1), (x2, y2) = xy[u], xy[v]
        if (u, v) in back or layer[v] <= layer[u]:
            sx, sy, ex, ey = x1 + NODE_W // 2, y1 + NODE_H, x2 + NODE_W // 2, y2 + NODE_H
            d, cls = f"M{sx},{sy} C{sx},{sy + CURVE} {ex},{ey + CURVE} {ex},{ey}", "edge back"
        elif (u, v) in skips:                         # top centre to top centre, through the room above row one
            sx, ex = x1 + NODE_W // 2, x2 + NODE_W // 2
            d, cls = f"M{sx},{y1} C{sx},0 {ex},0 {ex},{y2}", "edge skip"
        else:
            d, cls = f"M{x1 + NODE_W},{y1 + NODE_H // 2} L{x2},{y2 + NODE_H // 2}", "edge"
        tip = esc(label[u]) + " → " + esc(label[v]) + (": " + esc(str(lab)) if lab else "")
        out.append(f'<path class="{cls}" d="{d}" marker-end="url(#arr-{esc(uid)})"><title>{tip}</title></path>')
    for i in order:
        x, y = xy[i]
        out.append(f'<g class="node" tabindex="0" role="img" aria-label="{esc(label[i])}" transform="translate({x},{y})">'
                   f'<rect width="{NODE_W}" height="{NODE_H}" rx="8"/>'
                   f'<text x="10" y="{NODE_H // 2 + 5}">{esc(_clip(label[i]))}</text><title>{esc(label[i])}</title></g>')
    out.append("</svg>")
    return {"svg": "".join(out), "omitted": omitted, "shown": len(order)}


# ----------------------------------------------------------------------------- causal graph -> graph item

def causal_graph_item(g, top=40) -> dict:
    """A ready graph item from <ws>/causal_graph.json: the top links by mentions (ties by code), their end
    nodes in first-seen order, and the findings behind those links as cites."""
    edges = sorted(g.get("edges", []), key=lambda e: (-e["mentions"], e["from"], e["to"]))[:max(top, 1)]
    names = {n["code"]: n for n in g.get("nodes", [])}
    used = []
    for e in edges:
        for c in (e["from"], e["to"]):
            if c not in used:
                used.append(c)
    nodes = [{"id": c, "label": f"L{names[c]['level']} {c} {names[c]['name']}" if c in names else c} for c in used]
    it = {"kind": "graph", "id": "causal-map", "nodes": nodes,
          "edges": [{"from": e["from"], "to": e["to"],
                     "label": f"{e['mentions']} mention" + ("" if e["mentions"] == 1 else "s")} for e in edges]}
    cites = sorted({x for e in edges for x in e.get("findings", [])})
    if cites:
        it["cites"] = cites
    return it


def cmd_causal_item(a):
    ws = core._abs(a.ws)
    src = ws / "causal_graph.json"
    if not src.exists():
        sys.exit(f"Needs {src.name}. Run: pmlc.py causal {a.ws}")
    it = causal_graph_item(json.loads(src.read_text(encoding="utf-8")), a.top)
    if not it["edges"]:
        sys.exit("causal_graph.json has no links; tell the causal story in para items instead")
    print(json.dumps(it, indent=1, ensure_ascii=False))


# ----------------------------------------------------------------------------- coverage and Markdown

def coverage(w, pack) -> dict:
    """How many of the pack's relevant findings it cites, which it leaves out, and which it excludes on purpose."""
    fids = set(cited_ids(pack)[0])
    F = {f["id"]: f for f in w["findings"]}
    reasons = {e["id"]: e.get("reason", "") for e in (pack.get("exclusions") or [])
               if isinstance(e, dict) and e.get("id") in F}
    rel = [x for x in relevant_findings(w, pack.get("scope")) if x not in reasons]
    downs = core.downgraded_findings(w)
    unc = [{"id": x, "label": F[x].get("label", ""), "rating": F[x].get("rating"), "level": F[x].get("level"),
            "reason": "reviewer downgrade vote" if x in downs else "not cited in this pack"} for x in rel if x not in fids]
    excl = [{"id": x, "label": F[x].get("label", ""), "reason": r} for x, r in reasons.items()]
    return {"relevant": len(rel), "cited": len(rel) - len(unc), "uncovered": unc, "excluded": excl}


def sorted_events(events) -> list:
    """By date, then time; events with the same date and no time keep the author's order (sorted is stable)."""
    return sorted(events, key=lambda e: (e["date"], e.get("time") or ""))


_INC_DATE = None      # the incident date of the pack being rendered; set by render_pack_md / render_pack_html


def event_when(ev: dict, incident_date: str | None) -> str:
    """How a timeline event's date reads: 'c. 2015' (year only), '2019-03', '2019-03-04 14:05'. A date before the incident
    adds ' (N months before)', or ' (about N years before)' for a year-only date."""
    d = ev["date"]
    when = f"c. {d}" if len(d) == 4 else d + (f" {ev['time']}" if ev.get("time") else "")
    if incident_date:
        try:
            y, m, day = (list(map(int, d.split("-"))) + [1, 1])[:3]
            if len(d) == 4:
                n, unit = int(incident_date[:4]) - y, "years"
            else:
                n, unit = core.months_between(dt.date(y, m, day), dt.date.fromisoformat(incident_date)), "months"
        except ValueError:
            return when
        if n > 0:
            when += f" (about {n} {'year' if n == 1 else 'years'} before)" if unit == "years" else f" ({n} months before)"
    return when


def _pack_incident_date(pack, w):
    return (pack.get("incident") or {}).get("date") or core.incident_date(w)


def _c(cites):
    return f" [{'; '.join(cites)}]" if cites else ""


def _numbered(xs):
    return "\n".join(f"{i}. {x}" for i, x in enumerate(xs, 1))


def _lines(pairs):
    return "\n".join(f"- {k}: {v}" for k, v in pairs if v)


def _md_cell(v):
    return str(v).replace("|", "\\|").replace("\n", " ")


def _cites_cell(cites, sup) -> str:
    """The Markdown Cites cell of one table row: key IDs, then '+N supporting'."""
    s = "; ".join(cites)
    if not sup:
        return s
    more = f"+{len(sup)} supporting"
    return f"{s} ({more})" if s else more


def _md_item(it) -> str:
    k, c, g = it["kind"], _c(it.get("cites")), it.get
    if k == "para":
        return it["text"] + c
    if k == "check":
        hold = "**Hold point:** " if g("hold_point") else ""
        when = f" *({it['when']})*" if g("when") else ""
        return f"- [ ] {hold}{it['text']}{when}{c}"
    if k == "question":
        return (f"**Q: {it['question']}**{c}\n"
                + _lines([("Why it matters", it["why"]), ("Answer", g("answer")),
                          ("Good evidence looks like", g("good_evidence")), ("Put to", g("to"))]))
    if k == "recommendation":
        return (f"**Recommendation:** {it['change']}{c}\n"
                + _lines([("Control tier", core.norm_hoc(it["hoc_tier"])), ("Barrier", g("barrier")), ("Owner", g("owner")),
                          ("By when", g("by_when")), ("Leading indicator", it["indicator"])]))
    if k == "decision":
        return (f"**Decision:** {it['decision']}{c}\n"
                + _lines([("Options", "; ".join(g("options") or [])), ("Trade-offs", g("trade_offs")),
                          ("Owner", g("owner")), ("By when", g("by_when"))]))
    if k == "indicator":
        return (f"**Indicator:** {it['name']}{c}\n"
                + _lines([("Measure", it["measure"]), ("Deterioration looks like", g("deterioration")), ("Owner", g("owner"))]))
    if k == "card":
        parts = [f"### {it['title']}{c}", f"**What happened:** {it['what_happened']}"]
        if g("why_made_sense"):
            parts.append(f"**Why it made sense at the time:** {it['why_made_sense']}")
        parts.append("**Warning signs:**\n" + "\n".join(f"- {x}" for x in it["warning_signs"]))
        parts.append(f"**What good looks like:** {it['good_looks_like']}")
        if g("discussion"):
            parts.append("**Questions for discussion:**\n" + _numbered(it["discussion"]))
        return "\n\n".join(parts)
    if k == "scenario":
        return f"**Scenario:** {it['situation']}{c}\n\n" + _numbered(it["prompts"])
    if k == "table":
        cols, rows = list(it["columns"]), [list(r) for r in it["rows"]]
        rc, rs = g("row_cites"), g("row_supporting_cites")
        if rc or rs:
            cols.append("Cites")
            rows = [r + [_cites_cell(rc[i] if rc else [], rs[i] if rs else [])] for i, r in enumerate(rows)]
        out = ["| " + " | ".join(_md_cell(x) for x in cols) + " |", "|" + "---|" * len(cols)]
        out += ["| " + " | ".join(_md_cell(x) for x in r) + " |" for r in rows]
        md = "\n".join(out) + (f"\n\nSources:{c}" if c else "")
        if g("finding_notes"):
            md += "\n\nNotes per finding:\n" + "\n".join(f"- {x}: {v}" for x, v in it["finding_notes"].items())
        return md
    if k == "test_point":
        return (f"**Test point:** {it['requirement']}{c}\n"
                + _lines([("What to sample", it["sample"]), ("Evidence of conformity", it["conformity_evidence"]),
                          ("Red flags", "; ".join(g("red_flags") or []))]))
    if k == "module":
        out = (f"### Module: {it['title']}{c}\n\n"
               + _lines([("Objective", it["objective"]), ("Audience", g("audience")), ("Duration", g("duration"))])
               + "\n\n**Content:**\n" + _numbered(it["content"]))
        return out + ("\n\n**Assessment:**\n" + _numbered(it["assessment"]) if g("assessment") else "")
    if k == "barrier":
        return (f"**Barrier:** {it['barrier']}{c}\n"
                + _lines([("Failure mode", it["failure_mode"]), ("Type", g("type")), ("State on the day", g("state")),
                          ("Owner", g("owner")), ("Control tier", core.norm_hoc(it["hoc_tier"])), ("Fix", g("fix")),
                          ("Leading indicator", g("indicator"))]))
    if k == "timeline":
        lines = []
        for e in sorted_events(it["events"]):
            when = event_when(e, _INC_DATE)
            lines.append(f"- {when}: {e['text']}{' *(weak signal)*' if e.get('signal') else ''}{_c(e.get('cites'))}")
            lines += [f"  - {lab}: {e[f]}" for f, lab in (("received_by", "Received by"), ("response", "Response"))
                      if e.get(f)]
        return (f"Sources:{c}\n\n" if c else "") + "\n".join(lines)
    if k == "graph":
        lab = {n["id"]: n["label"] for n in it["nodes"]}
        lines = [f"- {lab[e['from']]} → {lab[e['to']]}" + (f" ({e['label']})" if e.get("label") else "") for e in it["edges"]]
        return f"Graph: {len(it['nodes'])} nodes, {len(it['edges'])} links{c}\n\n" + "\n".join(lines)
    if k == "learning":
        out = f"**Learning:** {it['lesson']}{c}"
        if g("explanation"):
            out += f"\n\n{it['explanation']}"
        return out + (f"\n\n- Owner: {it['owner']}" if g("owner") else "")
    raise ValueError(f"unknown kind {k!r}")


def _md_extras(d) -> str:
    bits = ([f"evidence: {d['evidence_strength']}"] if d.get("evidence_strength") else []) + \
           ([f"+{len(d['supporting_cites'])} supporting"] if d.get("supporting_cites") else [])
    return f"*({'; '.join(bits)})*" if bits else ""


def _md_block(it) -> str:
    x = _md_extras(it)
    if not x:
        return _md_item(it)
    return _md_item(it) + (" " + x if it["kind"] in ("para", "check") else "\n\n" + x)


def render_pack_md(pack, w) -> str:
    """The pack as Markdown: generated, never hand-written, so it always agrees with the HTML."""
    global _INC_DATE
    _INC_DATE = _pack_incident_date(pack, w)
    cov = coverage(w, pack)
    out = [f"# {pack['title']}", f"*{pack['status']}*", f"**Audience:** {pack['audience']}"]
    fields, inc = w.get("incident", {}).get("fields", {}), pack.get("incident") or {}
    shown = [str(x) for x in (inc.get("title") or fields.get("Incident Title"), inc.get("date") or fields.get("Date")) if x]
    if shown:
        out.append("**Incident:** " + " · ".join(shown))
    if pack.get("data_quality"):
        out += ["## Data quality and limits",
                "\n".join(f"- {n['text']}{_c(n.get('cites'))}" for n in pack["data_quality"])]
    out += ["## Bottom line",
           "\n".join(f"- {b['text']}{_c(b.get('cites'))}" + (" " + _md_extras(b) if _md_extras(b) else "")
                     for b in pack["bottom_line"])]
    for s in pack["sections"]:
        out.append(f"## {s['heading']}")
        if s.get("intro"):
            out.append(s["intro"])
        prev, tick = None, False
        for it in s["items"]:
            g = it.get("group")
            head = bool(g and g != prev)
            if head:
                out.append(f"### {g}")
            prev = g
            if tick and it["kind"] == "check" and not head:       # consecutive checks: one tight list
                out[-1] += "\n" + _md_block(it)
            else:
                out.append(_md_block(it))
            tick = it["kind"] == "check"
    sup = [f"- Bottom line › {i}: {'; '.join(b['supporting_cites'])}"
           for i, b in enumerate(pack["bottom_line"], 1) if b.get("supporting_cites")]
    sup += [f"- {s['heading']} › {n}: {'; '.join(it['supporting_cites'])}"
            for s in pack["sections"] for n, it in enumerate(s["items"], 1) if it.get("supporting_cites")]
    sup += [f"- {s['heading']} › {n}, row {r}: {'; '.join(x)}"
            for s in pack["sections"] for n, it in enumerate(s["items"], 1)
            for r, x in enumerate(it.get("row_supporting_cites") or [], 1) if x]
    if sup:
        out += ["## Supporting citations", "\n".join(sup)]
    tail = ["---", f"This pack cites {cov['cited']} of {cov['relevant']} relevant findings."]
    if cov["excluded"]:
        tail.append("Left out on purpose:\n" + "\n".join(f"- {e['id']}: {e['reason']}" for e in cov["excluded"]))
    out += tail + [f"> {core.BRAND}"]
    return "\n\n".join(out) + "\n"


# ----------------------------------------------------------------------------- HTML

GRID_KINDS = {"card", "indicator", "test_point", "module"}
STRONG_HOC = {"elimination", "substitution", "engineering"}


def _h(s) -> str:
    return html.escape("" if s is None else str(s), quote=True)


def _chip(x) -> str:
    return f'<button type="button" class="cite" data-id="{_h(x)}" aria-expanded="false">{_h(x)}</button>'


def _chips(cites) -> str:
    return '<span class="cites">' + "".join(_chip(x) for x in cites) + "</span>" if cites else ""


def _inline(s) -> str:
    """Escaped text in which Finding and Evidence IDs become citation buttons."""
    s, out, last = str(s), [], 0
    for m in ID_RX.finditer(s):
        out += [_h(s[last:m.start()]), _chip(m.group(1))]
        last = m.end()
    return "".join(out) + _h(s[last:])


def _rich(text) -> str:
    return "".join(f"<p>{_inline(p)}</p>" for p in re.split(r"\n\s*\n", str(text)) if p.strip())


def _labelled(label, value) -> str:
    return f'<span class="label">{_h(label)}</span><p>{_inline(value)}</p>' if value else ""


def _list(xs, tag="ul") -> str:
    return f"<{tag}>" + "".join(f"<li>{_inline(x)}</li>" for x in xs) + f"</{tag}>" if xs else ""


def _badges(pairs) -> str:
    return "".join(f'<span class="badge">{_h(k)}: {_h(v)}</span>' for k, v in pairs if v)


def _hoc(v) -> str:
    t = core.norm_hoc(v)
    cls = "badge strong" if t in STRONG_HOC else "badge"
    return f'<span class="{cls}">Control: {_h(t)}</span>'


def _extras(d) -> str:
    s = d.get("evidence_strength")
    badge = f' <span class="badge strength">Evidence: {_h(s)}</span>' if s else ""
    sup = d.get("supporting_cites") or []
    more = f'<details class="more"><summary>+{len(sup)} supporting</summary>{_chips(sup)}</details>' if sup else ""
    return badge + more


def _html_item(it, graphs) -> str:
    k, g, c = it["kind"], it.get, _chips(it.get("cites"))
    if k == "para":
        body = _rich(it["text"]) + c
    elif k == "check":
        key = _h(it["id"])
        hold = '<span class="badge hold">Hold point</span> ' if g("hold_point") else ""
        when = f' <span class="badge">{_h(g("when"))}</span>' if g("when") else ""
        body = (f'<div class="check"><input type="checkbox" class="tick" id="t-{key}" data-key="{key}" '
                f'aria-labelledby="tl-{key}"><span id="tl-{key}">{hold}{_inline(it["text"])}{when}</span></div>{c}')
    elif k == "question":
        to = f' <span class="badge">Put to: {_h(g("to"))}</span>' if g("to") else ""
        body = (f'<p><b>{_inline(it["question"])}</b>{to}</p>' + _labelled("Why it matters", it["why"])
                + _labelled("Answer", g("answer"))
                + _labelled("Good evidence looks like", g("good_evidence")) + c)
    elif k == "recommendation":
        meta = _hoc(it["hoc_tier"]) + _badges([("Barrier", g("barrier")), ("Owner", g("owner")), ("By", g("by_when"))])
        body = (f'<p><b>{_inline(it["change"])}</b></p><p>{meta}</p><p class="indicator-line">'
                f'<span class="label">Leading indicator</span>{_inline(it["indicator"])}</p>{c}')
    elif k == "decision":
        opts = '<span class="label">Options</span>' + _list(g("options")) if g("options") else ""
        body = (f'<p><b>{_inline(it["decision"])}</b></p>{opts}' + _labelled("Trade-offs", g("trade_offs"))
                + f'<p>{_badges([("Owner", g("owner")), ("By", g("by_when"))])}</p>{c}')
    elif k == "indicator":
        body = (f'<div class="card"><p><b>{_inline(it["name"])}</b></p>' + _labelled("Measure", it["measure"])
                + _labelled("Deterioration looks like", g("deterioration")) + _labelled("Owner", g("owner")) + c + "</div>")
    elif k == "card":
        disc = '<span class="label">Questions for discussion</span>' + _list(g("discussion"), "ol") if g("discussion") else ""
        body = (f'<div class="card"><h3>{_h(it["title"])}</h3>' + _labelled("What happened", it["what_happened"])
                + _labelled("Why it made sense at the time", g("why_made_sense"))
                + '<span class="label">Warning signs</span>' + _list(it["warning_signs"])
                + _labelled("What good looks like", it["good_looks_like"]) + disc + c + "</div>")
    elif k == "scenario":
        body = (f'<p><b>Scenario.</b> {_inline(it["situation"])}</p><details><summary>Discussion prompts</summary>'
                + _list(it["prompts"], "ol") + f"</details>{c}")
    elif k == "table":
        rc, rs = g("row_cites"), g("row_supporting_cites")
        cols = list(it["columns"]) + (["Cites"] if rc or rs else [])
        head = "".join(f'<th scope="col">{_h(x)}</th>' for x in cols)
        rows = []
        for r, row in enumerate(it["rows"]):
            cites = ""
            if rc or rs:
                sup = rs[r] if rs else []
                more = (f'<details class="more"><summary>+{len(sup)} supporting</summary>{_chips(sup)}</details>'
                        if sup else "")
                cites = f'<td class="cites-cell">{_chips(rc[r]) if rc else ""}{more}</td>'
            rows.append("<tr>" + "".join(f"<td>{_inline(x)}</td>" for x in row) + cites + "</tr>")
        notes = g("finding_notes")
        note_html = ('<span class="label">Notes per finding</span><ul class="notes">'
                     + "".join(f"<li>{_chip(x)} {_h(v)}</li>" for x, v in notes.items()) + "</ul>") if notes else ""
        body = (f'<div class="tablewrap" tabindex="0"><table><thead><tr>{head}</tr></thead>'
                f'<tbody>{"".join(rows)}</tbody></table></div>{note_html}{c}')
    elif k == "test_point":
        flags = ('<span class="label">Red flags seen in this investigation</span>' + _list(g("red_flags"))
                 if g("red_flags") else "")
        body = (f'<div class="card"><p><b>{_inline(it["requirement"])}</b></p>' + _labelled("What to sample", it["sample"])
                + _labelled("Evidence of conformity", it["conformity_evidence"]) + flags + c + "</div>")
    elif k == "module":
        meta = "".join(f'<span class="badge">{_h(g(f))}</span>' for f in ("audience", "duration") if g(f))
        assess = ("<details><summary>Assessment</summary>" + _list(g("assessment"), "ol") + "</details>"
                  if g("assessment") else "")
        body = (f'<div class="card"><h3>Module: {_h(it["title"])}</h3><p>{meta}</p>' + _labelled("Objective", it["objective"])
                + '<span class="label">Content</span>' + _list(it["content"], "ol") + assess + c + "</div>")
    elif k == "barrier":
        meta = _hoc(it["hoc_tier"]) + _badges([("Type", g("type")), ("State", g("state")), ("Owner", g("owner"))])
        body = (f'<p><b>{_inline(it["barrier"])}</b></p><p>{meta}</p>' + _labelled("Failure mode", it["failure_mode"])
                + _labelled("Fix", g("fix")) + _labelled("Leading indicator", g("indicator")) + c)
    elif k == "timeline":
        lis = []
        for e in sorted_events(it["events"]):
            sig = '<span class="badge hold">Weak signal</span> ' if e.get("signal") else ""
            when = _h(event_when(e, _INC_DATE))
            more = "".join(f'<p class="m">{lab}: {_h(e[f])}</p>'
                           for f, lab in (("received_by", "Received by"), ("response", "Response")) if e.get(f))
            lis.append(f'<li><time>{when}</time>{sig}{_inline(e["text"])} {_chips(e.get("cites"))}{more}</li>')
        body = f'<ol class="timeline">{"".join(lis)}</ol>{c}'
    elif k == "graph":
        gr = graphs[it["id"]]
        lab = {n["id"]: n["label"] for n in it["nodes"]}
        note = (f'<p class="m">{gr["omitted"]} nodes with the fewest links are not drawn; every link is listed below.</p>'
                if gr["omitted"] else "")
        links = "".join(f'<li>{_h(lab[e["from"]])} → {_h(lab[e["to"]])}'
                        + (f' ({_h(e["label"])})' if e.get("label") else "") + "</li>" for e in it["edges"])
        body = (f'<div class="graphwrap">{gr["svg"]}</div>{note}<details><summary>Links as text ({len(it["edges"])})'
                f'</summary><ul>{links}</ul></details>{c}')
    elif k == "learning":
        body = (f'<p><b>{_inline(it["lesson"])}</b> {_badges([("Owner", g("owner"))])}</p>'
                + (_rich(it["explanation"]) if g("explanation") else "") + c)
    else:
        raise ValueError(f"unknown kind {k!r}")
    return f'<div class="item k-{k}" id="i-{_h(it["id"])}">{body}{_extras(it)}</div>'


def _section_items(items, graphs) -> str:
    out, run, prev = [], [], None

    def flush():
        if run:
            out.append('<div class="grid">' + "".join(run) + "</div>")
            run.clear()

    for it in items:
        g = it.get("group")
        if g and g != prev:
            flush()
            out.append(f'<h3 class="group">{_h(g)}</h3>')
        prev = g
        h = _html_item(it, graphs)
        if it["kind"] in GRID_KINDS:
            run.append(h)
            continue
        flush()
        out.append(h)
    flush()
    return "".join(out)


def build_pack_data(w, pack, run) -> dict:
    """What the page script needs: full records of every cited finding and evidence item, plus the
    relevant findings the pack leaves uncited (so the coverage list can expand them too)."""
    fids, eids = cited_ids(pack)
    uncited = [x for x in relevant_findings(w, pack.get("scope")) if x not in fids]
    findings, evidence = core.citation_records(w, fids + uncited + excluded_ids(pack), eids)
    return {"pack": pack["pack"], "run": run, "findings": findings, "evidence": evidence}


def _trail(data) -> str:
    rows = [f'<dt>{_h(i)}</dt><dd>{_h(f.get("label") or f.get("name"))} · L{_h(f.get("level"))} · '
            f'rating {_h(f.get("rating"))}. {_h(f.get("short"))}</dd>' for i, f in data["findings"].items()]
    rows += [f'<dt>{_h(i)}</dt><dd>{_h(e.get("type"))}: {_h(e.get("description"))}</dd>' for i, e in data["evidence"].items()]
    return f'<section class="trail"><h2>Evidence trail</h2><dl>{"".join(rows)}</dl></section>'


def render_pack_html(w, pack, run, generated) -> str:
    """One self-contained offline page: server-rendered content, with pack.js adding behaviour."""
    global _INC_DATE
    _INC_DATE = _pack_incident_date(pack, w)
    pack = with_item_ids(pack)
    fields = w.get("incident", {}).get("fields", {})
    data = build_pack_data(w, pack, run)
    cov = coverage(w, pack)
    graphs = {it["id"]: layout_graph(it["nodes"], it["edges"], uid=it["id"])
              for s in pack["sections"] for it in s["items"] if it["kind"] == "graph"}
    has_checks = any(it["kind"] == "check" for s in pack["sections"] for it in s["items"])

    rail = "".join(f'<li><a href="#s/{_h(s["id"])}"><span>{_h(s["heading"])}</span>'
                   f'<span class="n">{len(s["items"])}</span></a></li>' for s in pack["sections"])
    secs = []
    for s in pack["sections"]:
        intro = f'<div class="intro">{_rich(s["intro"])}</div>' if s.get("intro") else ""
        secs.append(f'<details class="sec" id="s-{_h(s["id"])}" open><summary><h2>{_h(s["heading"])}</h2>'
                    f'<span class="n">{len(s["items"])}</span></summary><div class="sec-body">{intro}'
                    f'{_section_items(s["items"], graphs)}</div></details>')
    dq = pack.get("data_quality") or []
    dq_html = ('<section class="dq"><h2>Data quality and limits</h2><ul>'
               + "".join(f'<li>{_inline(n["text"])} {_chips(n.get("cites"))}</li>' for n in dq) + "</ul></section>") if dq else ""
    exc = "".join(f'<li>{_chip(e["id"])} {_h(e["label"])} · {_h(e["reason"])}</li>' for e in cov["excluded"])
    unc = "".join(f'<li>{_chip(u["id"])} {_h(u["label"])} · rating {_h(u["rating"])} · L{_h(u["level"])} · '
                  f'{_h(u["reason"])}</li>' for u in cov["uncovered"])
    cov_html = ('<section class="coverage"><h2>Coverage</h2>'
                f'<p>This pack cites {cov["cited"]} of {cov["relevant"]} relevant findings.</p>'
                + (f'<details><summary>Not covered here ({len(cov["uncovered"])})</summary><ul>{unc}</ul></details>'
                   if unc else "")
                + (f'<details><summary>Left out on purpose ({len(cov["excluded"])})</summary><ul>{exc}</ul></details>'
                   if exc else "") + "</section>")
    bottom = "".join(f'<li>{_inline(b["text"])} {_chips(b.get("cites"))}{_extras(b)}</li>' for b in pack["bottom_line"])
    clear = '<button type="button" id="clear-ticks">Clear ticks</button>' if has_checks else ""
    inc = pack.get("incident") or {}
    meta = " · ".join(_h(x) for x in (pack["audience"], inc.get("title") or fields.get("Incident Title"),
                                      inc.get("date") or fields.get("Date"), f"run {run}", f"generated {generated}") if x)
    title = _h(pack["title"])
    status = _h(pack["status"])
    css = (core.DASHBOARD_ASSETS / "pack.css").read_text(encoding="utf-8")
    js = (core.DASHBOARD_ASSETS / "pack.js").read_text(encoding="utf-8")
    payload = core.embed_json(data)
    brand = _h(core.BRAND)
    tokens, wide = core.PAGE_TOKENS_CSS, core.WIDE_CSS
    body = "".join(secs) + cov_html + _trail(data)
    return f"""<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{title}</title>
<style>
{tokens}
main{{max-width:1180px;margin:0 auto;padding:24px 16px 48px}}
{wide}
h1{{font-size:24px;margin:0 0 4px}} p.m{{color:var(--mut);margin:0 0 8px}}
footer{{margin-top:40px;color:var(--mut);font-size:12px;border-top:1px solid var(--line);padding-top:12px}}
{css}
</style></head><body><main>
<h1>{title}</h1>
<p class="m">{meta}</p>
<p class="status">{status}</p>
{dq_html}
<section class="bottom"><h2>Bottom line</h2><ul>{bottom}</ul></section>
<div class="toolbar" role="search"><input id="q" type="search" placeholder="Search this pack" aria-label="Search this pack">
<button type="button" id="expand-all">Expand all</button><button type="button" id="collapse-all">Collapse all</button>
<button type="button" id="print">Print</button>{clear}<span id="showing" aria-live="polite"></span></div>
<div class="layout"><details class="rail" open><summary>Contents</summary><ol>{rail}</ol></details>
<div class="content">{body}</div></div>
<footer>{brand}</footer>
</main>
<script type="application/json" id="pmlc-pack-data">{payload}</script>
<script>
{js}
</script>
</body></html>"""


def follow_up(pack) -> dict:
    """investigator-coach: finding ID -> the export's four follow-up fields, read from the table with id follow-up.
    A row may name several findings (one row per condition); each gets the row's fields, plus its own note if
    finding_notes gives one."""
    for s in pack["sections"]:
        for it in s["items"]:
            if it.get("id") == "follow-up" and it.get("kind") == "table":
                out, notes = {}, it.get("finding_notes") or {}
                for row in it["rows"]:
                    fields = dict(zip(FOLLOW_UP_KEYS, (str(x) for x in row[1:5])))
                    for x in re.split(r"[\s,;]+", str(row[0])):
                        if x:
                            out[x] = dict(fields, **({"note": notes[x]} if x in notes else {}))
                return out
    return {}


def cmd_pack(a):
    w, pack, _ = _checked(a)
    core.warn_stale(a.ws)
    ws = core._abs(a.ws)
    run = ws.parent.name if core.is_standard_ws(ws) else ws.name
    out = Path(a.out) if a.out else core.outputs_dir(ws)
    out.mkdir(parents=True, exist_ok=True)
    page = out / f"{pack['pack']}.html"
    page.write_text(render_pack_html(w, pack, run, dt.date.today().isoformat()), encoding="utf-8")
    print(f"HTML written to {page}")
    if not a.no_md:
        md = out / f"{pack['pack']}.md"
        md.write_text(render_pack_md(pack, w), encoding="utf-8")
        print(f"Markdown written to {md}")
    if pack["pack"] == "investigator-coach":
        fu = out / "follow-up.json"
        core.write_json(fu, follow_up(pack))
        print(f"Follow-up fields written to {fu}")
