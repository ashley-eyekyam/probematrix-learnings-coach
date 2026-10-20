"""Learning packs: ready-made items (causal-item)."""
from __future__ import annotations

import collections
import json
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
               "adoption"]
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


def cmd_table_item(a):
    print(json.dumps(table_item(_abs(a.ws), a.kind, a), indent=1, ensure_ascii=False))


# ----------------------------------------------------------------------------- register -> learning items

def register_items(entries, tier) -> list:
    """Learning items for one tier: priority 1 first, then by LR-ID. The lesson is the tier's own message when the
    entry has one."""
    mine = [e for e in entries if tier in (e.get("tiers") or [])]
    mine.sort(key=lambda e: (e.get("priority") if isinstance(e.get("priority"), int) else 9, str(e.get("lr_id"))))
    out = []
    for e in mine:
        msg = (e.get("tier_messages") or {}).get(tier)
        it = {"kind": "learning", "id": str(e["lr_id"]).lower(), "learning": e["lr_id"],
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
        ev["text"] = " ".join(c["snippet"].split())[:240]
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


def cmd_timeline_item(a):
    it = timeline_item(_abs(a.ws), a.before, a.top)
    if not it["events"]:
        sys.exit("No dated candidates before that date; tell the story in para items instead")
    print(json.dumps(it, indent=1, ensure_ascii=False))
