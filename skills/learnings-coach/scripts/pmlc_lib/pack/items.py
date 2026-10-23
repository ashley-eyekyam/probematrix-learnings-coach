"""Learning packs: ready-made items (causal-item)."""
from __future__ import annotations

import collections
import datetime as _dt
import json
import re
import sys
from pathlib import Path

from ..analysis.causal import hub_rows
from ..analysis.timeline import PRECISION_RANK
from ..register.check import HOC_TIERS, norm_hoc
from ..templates import load_adoption, load_register_entries, OrgFileError
from ..util import _abs
from ..workspace import incident_date, load_ws, outputs_dir


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
    ws = _abs(a.ws)
    src = ws / "causal_graph.json"
    if not src.exists():
        sys.exit(f"Needs {src.name}. Run: pmlc.py causal {a.ws}")
    it = causal_graph_item(json.loads(src.read_text(encoding="utf-8")), a.top)
    if not it["edges"]:
        sys.exit("causal_graph.json has no links; tell the causal story in para items instead")
    print(json.dumps(it, indent=1, ensure_ascii=False))


# ----------------------------------------------------------------------------- table items

TABLE_KINDS = ["clusters", "tiers", "relations", "hubs", "interfaces", "evidence-types", "entity-tier", "hoc",
               "adoption", "nine-m"]
ROW_CITES = 5            # Finding IDs cited per table row: the highest rated, ties by ID
NO_ADOPTION = "No adoption record yet: run PMLC templates <ws> adoption and fill it in"


def _table(item_id, columns, rows, row_cites) -> dict:
    return {"kind": "table", "id": item_id, "columns": columns, "rows": rows, "row_cites": row_cites,
            "cites": sorted({x for c in row_cites for x in c})}


def _best(fs, n=ROW_CITES) -> list:
    """IDs of the n highest-rated findings (ties by ID)."""
    return [f["id"] for f in sorted(fs, key=lambda f: (-(f.get("rating") or 0), f["id"]))[:n]]


def _need_clusters(w):
    if "clusters" not in w:
        sys.exit("Needs clusters.json. Run: pmlc.py classify <ws>")
    return w["clusters"]


def _group_table(w, levels, key, names, label, item_id, only=None, top=15) -> dict:
    """Findings (optionally of levels, and of one entity) counted per entity, tier or relation."""
    cl = _need_clusters(w)
    top_r = max(((f.get("rating") or 0) for f in w["findings"]), default=0)
    groups = collections.defaultdict(list)
    for f in w["findings"]:
        c = cl["findings"].get(f["id"], {})
        if (levels and f["level"] not in levels) or (only and only not in c.get("F", [])):
            continue
        for g in c.get(key, []):
            groups[g].append(f)
    order = sorted(groups, key=lambda g: (-len(groups[g]), g))[:max(top, 1)]
    cols = [label, "Name", "Findings", "L1", "L2", "L3", "L4", "Top-rated"]
    rows, cites = [], []
    for g in order:
        fs = groups[g]
        lv = collections.Counter(f["level"] for f in fs)
        rows.append([g, names.get(g, g), len(fs), lv.get(1, 0), lv.get(2, 0), lv.get(3, 0), lv.get(4, 0),
                     sum(1 for f in fs if top_r and (f.get("rating") or 0) == top_r)])
        cites.append(_best(fs))
    return _table(item_id, cols, rows, cites)


def _hoc_counts(entries) -> tuple:
    """(count per control tier, cites per tier) from (hoc text, cites) pairs."""
    n, cites = collections.Counter(), collections.defaultdict(list)
    for text, c in entries:
        t = norm_hoc(text)
        n[t] += 1
        cites[t] += [x for x in c if x not in cites[t]]
    return n, cites


def _hoc_table(a, ws) -> dict:
    pairs = []
    if a.register:
        for e in load_register_entries(a.register):
            for r in e.get("recommendations") or []:
                pairs.append((r.get("hoc_tier"), list(e.get("finding_ids") or [])))
    elif a.pack:
        doc = json.loads(Path(a.pack).read_text(encoding="utf-8"))
        for s in doc.get("sections", []):
            for it in s.get("items", []):
                if it.get("kind") in ("recommendation", "barrier") and it.get("hoc_tier"):
                    pairs.append((it["hoc_tier"], list(it.get("cites") or [])))
    else:
        sys.exit("table-item hoc needs --register or --pack")
    if not pairs:
        sys.exit("No recommendations with a control tier found")
    n, cites = _hoc_counts(pairs)
    order = [t for t in HOC_TIERS + ["unclassified"] if n[t]]
    total = sum(n.values())
    rows = [[t.capitalize(), n[t], f"{round(100 * n[t] / total)}%"] for t in order]
    return _table("hoc-table", ["Control tier", "Recommendations", "Share"], rows,
                  [sorted(cites[t], key=str)[:ROW_CITES] for t in order])


NINE_M_NO_VALUES = ("The register has no nine_m values: copy each learning's M from the nine-m-analysis outputs "
                    "into the register first (learnings-register)")
NINE_M_UNSET = ["none", "No 9M value recorded"]


def _nine_m_table(a, ws) -> dict:
    """P5-18: the register's learnings counted per M (nine_m), M1 to M9 in order with empty Ms kept, plus a last row
    for the learnings with no nine_m when the register has both. Row cites: each M's learnings' findings."""
    from ..ninem import load_nine_m, NINE_M_CODES        # late: keeps the pack modules free of the 9M references
    reg = Path(a.register) if a.register else _default_register(ws)
    if not reg.is_file():
        sys.exit(f"No Learnings Register at {reg}: write it first, or pass --register FILE")
    entries = load_register_entries(reg)
    by = collections.defaultdict(list)
    for e in entries:
        by[e.get("nine_m") if e.get("nine_m") in NINE_M_CODES else None].append(e)
    if not any(by[m] for m in NINE_M_CODES):
        sys.exit(NINE_M_NO_VALUES)
    names = {c["code"]: c["title"] for c in load_nine_m()["chapters"]}
    keys = list(NINE_M_CODES) + ([None] if by[None] else [])
    rows, cites = [], []
    for m in keys:
        es = sorted(by[m], key=lambda e: str(e.get("lr_id")))
        head = [m, names.get(m, m)] if m else list(NINE_M_UNSET)
        rows.append(head + [len(es), sum(1 for e in es if e.get("priority") == 1),
                            ", ".join(str(e.get("lr_id")) for e in es) or "none"])
        cites.append(list(dict.fromkeys(x for e in es for x in e.get("finding_ids") or []))[:ROW_CITES])
    return _table("nine-m-table", ["M", "Name", "Learnings", "Priority 1", "LR-IDs"], rows, cites)


def _default_register(ws) -> Path:
    return outputs_dir(ws) / "learnings-register.json"


def table_item(ws, kind, a) -> dict:
    w = load_ws(ws)
    levels = set(a.level or ())
    top = a.top
    if kind == "clusters":
        cl = _need_clusters(w)
        return _group_table(w, levels, "F", cl["taxonomy"]["entities"], "Cluster", "clusters-table", top=top)
    if kind == "tiers":
        cl = _need_clusters(w)
        return _group_table(w, levels, "T", cl["taxonomy"]["tiers"], "Tier", "tiers-table", top=top)
    if kind == "relations":
        cl = _need_clusters(w)
        return _group_table(w, levels, "R", cl["taxonomy"]["relations"], "Relation", "relations-table", top=top)
    if kind == "entity-tier":
        cl = _need_clusters(w)
        if not a.entity:
            sys.exit("table-item entity-tier needs --entity F (for example F02)")
        if a.entity not in cl["taxonomy"]["entities"]:
            sys.exit(f"{a.entity} is not an entity in clusters.json")
        it = _group_table(w, levels, "T", cl["taxonomy"]["tiers"], "Tier", f"entity-tier-{a.entity.lower()}",
                          only=a.entity, top=top)
        if not it["rows"]:
            sys.exit(f"No findings for {a.entity}")
        return it
    if kind == "hubs":
        src = Path(ws) / "causal_graph.json"
        if not src.exists():
            sys.exit(f"Needs {src.name}. Run: pmlc.py causal {a.ws}")
        hubs = [h for h in hub_rows(json.loads(src.read_text(encoding="utf-8")))
                if not levels or h["level"] in levels][:max(top, 1)]
        if not hubs:
            sys.exit("causal_graph.json has no links")
        return _table("hubs-table", ["Factor", "Level", "Links out", "Mentions", "Name"],
                      [[h["code"], f"L{h['level']}", h["links"], h["mentions"], h["name"]] for h in hubs],
                      [h["findings"][:ROW_CITES] for h in hubs])
    if kind == "interfaces":
        cl = _need_clusters(w)
        src = Path(ws) / "interfaces.json"
        if not src.exists():
            sys.exit(f"Needs {src.name}. Run: pmlc.py interfaces {a.ws}")
        names = cl["taxonomy"]["entities"]
        pairs = json.loads(src.read_text(encoding="utf-8"))["pairs"][:max(top, 1)]
        if not pairs:
            sys.exit("interfaces.json has no pairs")
        return _table("interfaces-table", ["Interface", "Shared findings", "Cross-entity causal mentions"],
                      [[f"{p['a']} {names.get(p['a'], '')} - {p['b']} {names.get(p['b'], '')}",
                        p["shared_findings"], p["cross_causal_mentions"]] for p in pairs],
                      [sorted(p["examples"])[:ROW_CITES] for p in pairs])
    if kind == "evidence-types":
        ev = w.get("evidence", {})
        if not ev:
            sys.exit("This workspace has no evidence items")
        by = collections.defaultdict(list)
        for e in ev.values():
            by[e.get("type") or "unspecified"].append(e["id"])
        order = sorted(by, key=lambda t: (-len(by[t]), t))[:max(top, 1)]
        return _table("evidence-types-table", ["Evidence type", "Items"], [[t, len(by[t])] for t in order],
                      [sorted(by[t])[:ROW_CITES] for t in order])
    if kind == "hoc":
        return _hoc_table(a, ws)
    if kind == "nine-m":
        return _nine_m_table(a, ws)
    if kind == "adoption":
        try:
            rows = load_adoption(ws)
        except OrgFileError as e:
            sys.exit(str(e))
        if not rows:
            return _table("adoption-table", ["Adoption"], [[NO_ADOPTION]], [[]])
        reg = Path(a.register) if a.register else _default_register(ws)
        ids = {e.get("lr_id"): list(e.get("finding_ids") or [])[:ROW_CITES]
               for e in (load_register_entries(reg) if reg.is_file() else [])}
        return _table("adoption-table", ["LR-ID", "Title", "Response", "Reason", "Owning role", "Target window"],
                      [[r["lr_id"], r["title"], r["response"], r["reason"], r["owning_role"], r["target_window"]]
                       for r in rows], [ids.get(r["lr_id"], []) for r in rows])
    sys.exit(f"Unknown table kind {kind}")


def drop_excluded(item: dict, pack_path) -> dict:
    """INT-B: with --pack, remove every id the pack lists in `exclusions` from row_cites and cites, so a generated
    table never cites what the pack leaves out on purpose. A row left with no cites keeps an empty list."""
    from .schema import excluded_ids
    try:
        gone = set(excluded_ids(json.loads(Path(pack_path).read_text(encoding="utf-8"))))
    except (OSError, ValueError):
        sys.exit(f"Cannot read the pack {pack_path}")
    if gone and isinstance(item.get("row_cites"), list):
        item["row_cites"] = [[x for x in c if x not in gone] for c in item["row_cites"]]
        item["cites"] = sorted({x for c in item["row_cites"] for x in c})
    return item


def cmd_table_item(a):
    item = table_item(_abs(a.ws), a.kind, a)
    if a.pack:
        item = drop_excluded(item, a.pack)
    print(json.dumps(item, indent=1, ensure_ascii=False))


# ----------------------------------------------------------------------------- register -> learning items

def register_items(entries, tier) -> list:
    """Learning items for one tier: priority 1 first, then by LR-ID. The lesson is the tier's own message when the
    entry has one."""
    mine = [e for e in entries if tier in (e.get("tiers") or [])]
    mine.sort(key=lambda e: (e.get("priority") if isinstance(e.get("priority"), int) else 9, str(e.get("lr_id"))))
    out = []
    for e in mine:
        msg = (e.get("tier_messages") or {}).get(tier)
        it = {"kind": "learning", "id": f"{tier.lower()}-{str(e['lr_id']).lower()}", "learning": e["lr_id"],
              "lesson": msg or e.get("lesson") or e.get("title", "")}
        expl = e.get("lesson") if msg else e.get("context")
        if expl:
            it["explanation"] = expl
        it["cites"] = list(dict.fromkeys(list(e.get("finding_ids") or []) + list(e.get("evidence_ids") or [])))
        out.append(it)
    return out


def cmd_register_items(a):
    ws = _abs(a.ws)
    reg = Path(a.register) if a.register else _default_register(ws)
    if not reg.is_file():
        sys.exit(f"No Learnings Register at {reg}: write it first, or pass --register FILE")
    print(json.dumps(register_items(load_register_entries(reg), a.tier), indent=1, ensure_ascii=False))


# ----------------------------------------------------------------------------- timeline candidates -> timeline item

def trim_words(text, limit=240) -> str:
    """text with whitespace collapsed, cut at the last whitespace before `limit` characters with an ellipsis when it
    is longer (P5-11): the result is at most `limit` characters and never ends inside a word."""
    s = " ".join(str(text).split())
    if len(s) <= limit:
        return s
    head = s[:limit]
    i = head.rfind(" ")
    head = head[:i] if i > 0 else head[:limit - 1]
    return head.rstrip().rstrip("…") + "…"


def timeline_item(ws, before, top=12) -> dict:
    w = load_ws(ws)
    src = Path(ws) / "timeline_candidates.json"
    if not src.exists():
        sys.exit(f"Needs {src.name}. Run: pmlc.py timeline {ws} --before incident")
    if before == "incident":
        before = incident_date(w)
        if not before:
            sys.exit("No incident date in this workspace; pass --date to ingest.")
    else:
        from ..util import iso_date
        if not iso_date(before):
            sys.exit('--before: use YYYY-MM-DD or "incident"')
    cands = [c for c in json.loads(src.read_text(encoding="utf-8")) if c["date"] <= before]
    cands.sort(key=lambda c: (-len(c["sources"]), PRECISION_RANK[c["precision"]], c["date"], c["snippet"]))
    cands = cands[:max(top, 1)]
    cl = w.get("clusters")
    names = cl["taxonomy"]["entities"] if cl else {}
    events = []
    for c in cands:
        d = c["date"]
        ev = {"date": d if c["precision"] == "day" else d[:7] if c["precision"] == "month" else d[:4]}
        if c.get("time"):
            ev["time"] = c["time"]
        ev["text"] = trim_words(c["snippet"])
        if cl:
            for sid in sorted(c["sources"]):
                m = cl["findings"].get(sid)
                if m:
                    f = next((x for x in m["F"] if x != "F99"), None)
                    if f:
                        ev["received_by"] = f"{names.get(f, f)} ({f}, {(m['T'] or ['T9'])[0]})"
                        break
        ev["cites"] = sorted(c["sources"])
        events.append(ev)
    events.sort(key=lambda e: (e["date"], e.get("time") or ""))
    return {"kind": "timeline", "id": "timeline-candidates", "events": events,
            "cites": sorted({x for e in events for x in e["cites"]})}


# ----------------------------------------------------------------------------- narrative -> event-day timeline item

# hh:mm or hh.mm (P5-10, the calibration rule), but not the start of a dotted date such as 4.09.2020
EVENT_DAY_RX = re.compile(r"\b([01]?\d|2[0-3])[:.]([0-5]\d)\b(?![./-]\d)")
_SENTENCE_END_RX = re.compile(r"[.!?][\"'”’)\]]*(?=\s|$)")
_TIME_CELL_RX = re.compile(r"~?\s*\d{1,2}[:.]\d\d(?::\d\d)?\s*(?:hours?|hrs?|h)?\.?")


def _event_day_units(narrative):
    """(text the times are read from, text the event shows) for each sentence of the narrative. Markdown emphasis,
    list and heading marks are dropped. A table row is one unit: its cells joined with ' | ', without the cells that
    hold only a time (the event's own time shows it); table separator rows are skipped."""
    for line in str(narrative or "").splitlines():
        line = line.replace("**", "").replace("__", "").strip()
        if line.startswith("|"):
            cells = [c.strip() for c in line.strip("|").split("|")]
            cells = [c for c in cells if c]
            if not cells or all(re.fullmatch(r":?-+:?", c) for c in cells):
                continue
            words = [c for c in cells if not _TIME_CELL_RX.fullmatch(c)] or cells
            yield " ".join(cells), " | ".join(words)
            continue
        line = re.sub(r"^(?:#+|[-*+]|>)\s+", "", line)
        start = 0
        for m in _SENTENCE_END_RX.finditer(line):
            unit = line[start:m.end()].strip()
            if unit:
                yield unit, unit
            start = m.end()
        if line[start:].strip():
            yield line[start:].strip(), line[start:].strip()


def event_day_times(text) -> set:
    return {f"{int(m.group(1)):02d}:{m.group(2)}" for m in EVENT_DAY_RX.finditer(str(text or ""))}


_MONTHS = ("jan", "feb", "mar", "apr", "may", "jun", "jul", "aug", "sep", "oct", "nov", "dec")
_MONTH_RX = r"(jan(?:uary)?|feb(?:ruary)?|mar(?:ch)?|apr(?:il)?|may|june?|july?|aug(?:ust)?|sep(?:t(?:ember)?)?|oct(?:ober)?|nov(?:ember)?|dec(?:ember)?)"
_DAY_MONTH_RX = re.compile(r"\b(?:(\d{1,2})(?:st|nd|rd|th)?\s+" + _MONTH_RX + r"|" + _MONTH_RX + r"\s+(\d{1,2})(?:st|nd|rd|th)?)\b",
                           re.I)


def _named_day(text, pos, day):
    """The YYYY-MM-DD of the day-and-month named nearest before `pos` in `text` (e.g. '23 Sep 20:00'), with the year
    from the incident `day` (one year earlier when the month is more than six months after the incident's); None when
    the unit names no day before the time or the day is not a real date. The month name must be capitalised
    ('23 Sep', '23 SEP'), so a number before the modal verb 'may' or a lower-case word never re-dates an event."""
    last = None
    for m in _DAY_MONTH_RX.finditer(text):
        if m.start() >= pos:
            break
        if (m.group(2) or m.group(3))[0].isupper():   # 'valve 2 may be open', '3 dec valves': prose, not a date
            last = m
    if not last:
        return None
    d = int(last.group(1) or last.group(4))
    mon = _MONTHS.index((last.group(2) or last.group(3))[:3].lower()) + 1
    year, inc_mon = int(day[:4]), int(day[5:7])
    if mon - inc_mon > 6:
        year -= 1
    try:
        return _dt.date(year, mon, d).isoformat()
    except ValueError:
        return None


def event_day_events(narrative, findings, day) -> list:
    """One event per distinct narrative hh:mm: the first sentence that holds the time, whole (sentence start to
    sentence end), cited to the findings whose text holds the same time (P5-10). The event is dated with the incident
    day, unless its sentence names another day and month before the time ('23 Sep 20:00'): then that day, with the
    incident's year. Events run in (date, time) order."""
    first = {}
    for source, shown in _event_day_units(narrative):
        for m in sorted(EVENT_DAY_RX.finditer(source), key=lambda m: m.start()):
            hhmm = f"{int(m.group(1)):02d}:{m.group(2)}"
            if hhmm not in first:
                first[hhmm] = (_named_day(source, m.start(), day) or day, " ".join(shown.split()))
    held = {f["id"]: event_day_times(" ".join(str(f.get(k) or "") for k in ("label", "short", "justification", "causal")))
            for f in findings}
    return [{"date": first[hhmm][0], "time": hhmm, "text": first[hhmm][1],
             "cites": sorted(fid for fid, times in held.items() if hhmm in times), "knowable_then": True}
            for hhmm in sorted(first, key=lambda t: (first[t][0], t))]


def event_day_item(ws) -> dict:
    """The event-day timeline item from the incident narrative. No times: an empty item and a note on stderr."""
    w = load_ws(ws)
    narrative = w.get("incident", {}).get("narrative", "")
    item = {"kind": "timeline", "id": "event-day", "events": [], "cites": []}
    if not event_day_times(narrative):
        print("No hh:mm times in the incident narrative: the event-day item is empty; tell the sequence in para "
              "items instead.", file=sys.stderr)
        return item
    day = incident_date(w)
    if not day:
        sys.exit("No incident date in this workspace; pass --date to ingest.")
    item["events"] = event_day_events(narrative, w["findings"], day)
    for e in item["events"]:
        if e["date"] != day:
            print(f"Event {e['time']} dated {e['date']}, not the incident day {day}, from the day and month its "
                  "sentence names; check the date before using the item.", file=sys.stderr)
    item["cites"] = sorted({x for e in item["events"] for x in e["cites"]})
    return item


def cmd_timeline_item(a):
    if getattr(a, "event_day", False):
        print(json.dumps(event_day_item(_abs(a.ws)), indent=1, ensure_ascii=False))
        return
    if not a.before:
        sys.exit("timeline-item needs --before YYYY-MM-DD|incident, or --event-day for the incident-day sequence")
    it = timeline_item(_abs(a.ws), a.before, a.top)
    if not it["events"]:
        sys.exit("No dated candidates before that date; tell the story in para items instead")
    print(json.dumps(it, indent=1, ensure_ascii=False))
