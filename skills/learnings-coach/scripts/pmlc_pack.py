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
import types
from pathlib import Path

import pmlc as core

SCHEMA_VERSION = 1
STATUS_PHRASE = "Learning purposes: not a statutory document"
PACK_NAME_RX = re.compile(r"^(?:[a-z0-9]+(?:-[a-z0-9]+)*|dossier-F\d+)$")
SLUG_RX = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
ID_RX = re.compile(r"\b(FND-[0-9A-Za-z]{4,}|EVD-\d{3,})\b")
DATE_RX = re.compile(r"^\d{4}(?:-\d{2}(?:-\d{2})?)?$")
MAX_BOTTOM_LINE = 7

# Item kinds: required fields, optional fields, and whether at least one citation is required.
KINDS = {
    "para": {"req": ["text"], "opt": []},
    "check": {"req": ["text"], "opt": ["hold_point", "when"]},
    "question": {"req": ["question", "why"], "opt": ["good_evidence", "to"]},
    "recommendation": {"req": ["change", "indicator", "hoc_tier"], "opt": ["barrier", "owner", "by_when"], "cite": True},
    "decision": {"req": ["decision"], "opt": ["options", "trade_offs", "owner", "by_when"]},
    "indicator": {"req": ["name", "measure"], "opt": ["deterioration", "owner"]},
    "card": {"req": ["title", "what_happened", "warning_signs", "good_looks_like"], "opt": ["why_made_sense", "discussion"],
             "cite": True},
    "scenario": {"req": ["situation", "prompts"], "opt": []},
    "table": {"req": ["columns", "rows"], "opt": ["row_cites"]},
    "test_point": {"req": ["requirement", "sample", "conformity_evidence"], "opt": ["red_flags"], "cite": True},
    "module": {"req": ["title", "objective", "content"], "opt": ["audience", "duration", "assessment"]},
    "barrier": {"req": ["barrier", "failure_mode", "hoc_tier"], "opt": ["type", "fix"], "cite": True},
    "timeline": {"req": ["events"], "opt": []},
    "graph": {"req": ["nodes", "edges"], "opt": []},
}
STR_LIST_FIELDS = {"options", "warning_signs", "discussion", "prompts", "columns", "content", "assessment", "red_flags"}
OBJ_LIST_FIELDS = {"rows", "row_cites", "events", "nodes", "edges"}
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


def cited_ids(pack) -> tuple:
    """Ordered unique (finding IDs, evidence IDs) cited anywhere in the bottom line or sections."""
    fids, eids = [], []
    for _, x in _walk_ids({"bottom_line": pack.get("bottom_line"), "sections": pack.get("sections")}, ""):
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
        a = types.SimpleNamespace(entity=scope.get("entities") or None, tier=scope.get("tiers") or None,
                                  relation=None, level=scope.get("levels") or None,
                                  min_rating=scope.get("min_rating"), code=None, text=None, max=None)
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
    rc = it.get("row_cites")
    if rc is None:
        return
    if not isinstance(rc, list) or len(rc) != len(rows):
        bad(f"{ip}.row_cites", "must hold one list of IDs per row")
        return
    for r, c in enumerate(rc):
        if not _id_list(c):
            bad(f"{ip}.row_cites[{r}]", "must be a list of Finding or Evidence IDs")


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
        if "cites" in ev and not _id_list(ev["cites"]):
            bad(f"{ep}.cites", "must be a list of Finding or Evidence IDs")


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
    for f in it:
        if f not in known and f not in ("kind", "id", "cites"):
            warn(f"{ip}.{f}", f"unknown field for {kind} (ignored)")
    if _text(it.get("hoc_tier")) and core.norm_hoc(it["hoc_tier"]) == "unclassified":
        bad(f"{ip}.hoc_tier", f"must name a hierarchy-of-controls tier: {', '.join(core.HOC_TIERS)}")
    {"table": _check_table, "timeline": _check_timeline, "graph": _check_graph}.get(kind, lambda *x: None)(it, ip, bad)
    if not spec.get("cite") and not any(True for _ in _walk_ids(it, "")):
        warn(ip, "no Finding or Evidence ID cited")


def _check_scope(scope, w, bad):
    if scope is None:
        return
    if not isinstance(scope, dict):
        bad("scope", "must be an object")
        return
    for k in scope:
        if k not in ("tiers", "levels", "entities", "min_rating"):
            bad(f"scope.{k}", "unknown key; use tiers, levels, entities, min_rating")
    t, lv, en, mr = scope.get("tiers") or [], scope.get("levels") or [], scope.get("entities") or [], scope.get("min_rating")
    if not isinstance(t, list) or any(x not in core.TIER_LABELS for x in t):
        bad("scope.tiers", "a list of T1 to T5")
    if not isinstance(lv, list) or any(isinstance(x, bool) or x not in (1, 2, 3, 4) for x in lv):
        bad("scope.levels", "a list of 1 to 4")
    if not isinstance(en, list) or any(not isinstance(x, str) for x in en):
        bad("scope.entities", "a list of entity IDs like F02")
    if mr is not None and (isinstance(mr, bool) or not isinstance(mr, int)):
        bad("scope.min_rating", "a whole number or null")
    if (t or en) and "clusters" not in w:
        bad("scope", "tiers and entities need clusters.json. Run: pmlc.py classify <ws>")


def _check_follow_up(secs, bad):
    tables = [it for s in secs if isinstance(s, dict) and isinstance(s.get("items"), list)
              for it in s["items"] if isinstance(it, dict) and it.get("id") == "follow-up"]
    if not tables or tables[0].get("kind") != "table" or tables[0].get("columns") != FOLLOW_UP_COLUMNS:
        bad("investigator-coach", f"needs a table item with id follow-up and columns {FOLLOW_UP_COLUMNS}")
        return
    for r, row in enumerate(tables[0].get("rows") if isinstance(tables[0].get("rows"), list) else []):
        if isinstance(row, list) and row and not (isinstance(row[0], str) and ID_RX.fullmatch(row[0].strip())
                                                  and row[0].strip().startswith("FND-")):
            bad(f"follow-up.rows[{r}][0]", "must be a Finding ID")


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
    if _text(pack.get("pack")) and not PACK_NAME_RX.match(pack["pack"]):
        bad("pack", "must be lowercase words joined by hyphens (or dossier-F<nn>)")
    if _text(pack.get("status")) and STATUS_PHRASE not in pack["status"]:
        bad("status", f'must contain "{STATUS_PHRASE}"')
    bl = pack.get("bottom_line") if isinstance(pack.get("bottom_line"), list) else []
    if len(bl) > MAX_BOTTOM_LINE:
        bad("bottom_line", f"at most {MAX_BOTTOM_LINE} entries (got {len(bl)})")
    for i, e in enumerate(bl):
        if not isinstance(e, dict) or not _text(e.get("text")):
            bad(f"bottom_line[{i}].text", "required")
        elif not (_id_list(e.get("cites")) and e.get("cites")):
            bad(f"bottom_line[{i}].cites", "every bottom-line entry needs at least one Finding or Evidence ID")
    _check_scope(pack.get("scope"), w, bad)

    secs = pack.get("sections") if isinstance(pack.get("sections"), list) else []
    seen, n_items = set(), 0
    for si, s in enumerate(secs):
        sp = f"sections[{si}]"
        if not isinstance(s, dict):
            bad(sp, "must be an object")
            continue
        sid = s.get("id")
        if not isinstance(sid, str) or not SLUG_RX.match(sid):
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
            if iid is not None and not (isinstance(iid, str) and SLUG_RX.match(iid)):
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
    ids = set()
    for path, x in _walk_ids({"bottom_line": pack.get("bottom_line"), "sections": pack.get("sections")}, ""):
        ids.add(x)
        if x not in (F if x.startswith("FND-") else E):
            bad(path, f"{x} is not in this workspace")
    if not P:
        rel = relevant_findings(w, pack.get("scope"))
        got = len(set(rel) & ids)
        if rel and got * 2 < len(rel):
            W.append(f"coverage: cites {got} of {len(rel)} relevant findings (under half)")
    return Result(P, W, {"sections": len(secs), "items": n_items, "cited": len(ids)})


def load_pack(path) -> tuple:
    """(parsed JSON, None) or (None, a problem line)."""
    try:
        return json.loads(Path(path).read_text(encoding="utf-8")), None
    except FileNotFoundError:
        return None, f"(file): {path} not found"
    except json.JSONDecodeError as e:
        return None, f"(json): invalid JSON at line {e.lineno} column {e.colno}: {e.msg}"


def _checked(a):
    """Load the workspace and pack, print warnings, exit listing every problem; else return (w, pack, result)."""
    w = core.load_ws(a.ws)
    pack, err = load_pack(a.pack)
    res = Result([err], [], {}) if err else check_pack(pack, w)
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
    are ignored for layering and drawn as dashed curves; four barycentre passes order each layer.
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
    width = PAD * 2 + ncols * NODE_W + max(0, ncols - 1) * GAP_X
    height = PAD * 2 + nrows * NODE_H + max(0, nrows - 1) * GAP_Y + (CURVE if curved else 0)
    xy = {i: (PAD + layer[i] * (NODE_W + GAP_X), PAD + pos[i] * (NODE_H + GAP_Y)) for i in order}
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
        else:
            d, cls = f"M{x1 + NODE_W},{y1 + NODE_H // 2} L{x2},{y2 + NODE_H // 2}", "edge"
        tip = esc(label[u]) + " → " + esc(label[v]) + (": " + esc(lab) if lab else "")
        out.append(f'<path class="{cls}" d="{d}" marker-end="url(#arr-{esc(uid)})"><title>{tip}</title></path>')
    for i in order:
        x, y = xy[i]
        out.append(f'<g class="node" tabindex="0" role="img" aria-label="{esc(label[i])}" transform="translate({x},{y})">'
                   f'<rect width="{NODE_W}" height="{NODE_H}" rx="8"/>'
                   f'<text x="10" y="{NODE_H // 2 + 5}">{esc(_clip(label[i]))}</text><title>{esc(label[i])}</title></g>')
    out.append("</svg>")
    return {"svg": "".join(out), "omitted": omitted, "shown": len(order)}
