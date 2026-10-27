"""The accimap command: place every finding on Rasmussen's six AcciMap levels (1 government to 6 work and equipment).

Placement is by rule (references/accimap.json): the finding's entity first, then its HFACS level. Placements at
levels 1 to 3 are inferred from codes and departments, so a person confirms them before a map is shared."""
from __future__ import annotations

import collections
import json
import re
import sys
from pathlib import Path

from .util import REFS, _abs, write_json
from .workspace import file_sha256, load_ws, record_derived

ACCIMAP_VERSION = 1
ACCIMAP_FILE = "accimap.json"
ACCIMAP_TABLE_KINDS = ["levels"]
ACCIMAP_ROW_CITES = 5
ACCIMAP_TOP_CODES = 4        # code nodes drawn under each level in the graph item
ACCIMAP_LEVELS = (1, 2, 3, 4, 5, 6)


def _am_bad(path, why):
    print(f"Cannot use the AcciMap map {path}: {why}.", file=sys.stderr)
    sys.exit(2)


def _am_level(v) -> bool:
    return isinstance(v, int) and not isinstance(v, bool) and v in ACCIMAP_LEVELS


def accimap_load_map(path=None) -> dict:
    """The AcciMap rules: references/accimap.json, with a --map file merged over it. A bad map stops with one
    plain sentence and exit 2."""
    base = json.loads((REFS / "accimap.json").read_text(encoding="utf-8"))
    if not path:
        return base
    p = Path(path)
    try:
        extra = json.loads(p.read_text(encoding="utf-8"))
    except (OSError, ValueError) as e:
        print(f"Cannot read the AcciMap map {p}: {e}", file=sys.stderr)
        sys.exit(2)
    if not isinstance(extra, dict):
        _am_bad(p, "the top level is not an object")
    for key in ("entities", "subcategories", "hfacs_levels", "keywords"):
        if not isinstance(extra.get(key, {}), dict):
            _am_bad(p, f"'{key}' is not an object")
    for k, v in extra.get("entities", {}).items():
        if not isinstance(v, dict) or not _am_level(v.get("level")):
            _am_bad(p, f"entities {k}: 'level' must be a whole number from 1 to 6")
        for opt in ("rule", "tag"):
            if opt in v and not isinstance(v[opt], str):
                _am_bad(p, f"entities {k}: '{opt}' must be text")
    for key in ("subcategories", "hfacs_levels"):
        for k, v in extra.get(key, {}).items():
            if not _am_level(v):
                _am_bad(p, f"{key} {k}: the level must be a whole number from 1 to 6")
    for lvl, rxs in extra.get("keywords", {}).items():
        if lvl not in {str(i) for i in ACCIMAP_LEVELS}:
            _am_bad(p, f"keywords {lvl}: the key must be a level from 1 to 6")
        if not isinstance(rxs, list) or not all(isinstance(r, str) for r in rxs):
            _am_bad(p, f"keywords {lvl}: the value must be a list of text patterns")
        for rx in rxs:
            try:
                re.compile(rx)
            except re.error as e:
                _am_bad(p, f"keywords {lvl}: {rx!r} does not compile ({e})")
    merged = dict(base)
    for key in ("entities", "subcategories", "hfacs_levels"):
        merged[key] = {**base.get(key, {}), **extra.get(key, {})}
    merged["keywords"] = {**base.get("keywords", {}), **extra.get("keywords", {})}
    return merged


def _am_place_one(f, ents, amap) -> tuple:
    """(level, rule, tag) for one finding."""
    text = " ".join([str(r) for r in (f.get("roles") or [])] + [str(f.get("label") or "")])
    for lvl in sorted(amap.get("keywords", {}), key=int):
        for rx in amap["keywords"][lvl]:
            if re.search(rx, text, re.I):
                return int(lvl), f"map keyword for level {lvl}", None
    found = [e for e in ents.get(f["id"], []) if e in amap["entities"]]
    if found:
        best = min(found, key=lambda e: (amap["entities"][e]["level"], e))
        ent = amap["entities"][best]
        return ent["level"], ent.get("rule") or f"entity {best}", ent.get("tag")
    sub = f.get("subcategory") or ""
    lvl = f.get("level")
    if lvl == 2 and sub in amap["subcategories"]:
        return amap["subcategories"][sub], f"HFACS level 2, {sub}", None
    if str(lvl) in amap["hfacs_levels"]:
        return amap["hfacs_levels"][str(lvl)], f"HFACS level {lvl}", None
    return 0, "", None


def place(w: dict, amap=None) -> dict:
    """The accimap.json document for a loaded workspace."""
    amap = amap or accimap_load_map()
    names = amap["levels"]
    cl = w.get("clusters")
    ents = {fid: c.get("F", []) for fid, c in (cl or {}).get("findings", {}).items()}
    notes = []
    if cl is None:
        notes.append("No clusters.json: run classify. Placement uses the HFACS level only, with no entity rules.")
    elif not any(e in ("F14", "F15") for es in ents.values() for e in es):
        notes.append("No finding is tagged to the corporate or regulator entities (F14, F15): levels 2 and 3 come "
                     "from the codes only.")
    limit = int(amap.get("inferred_up_to", 3))
    placements, by_level, unplaced = {}, collections.defaultdict(list), []
    for f in w["findings"]:
        lvl, rule, tag = _am_place_one(f, ents, amap)
        if not lvl:
            unplaced.append(f["id"])
            continue
        p = {"level": lvl, "rule": rule, "inferred": lvl <= limit}
        if tag:
            p["tag"] = tag
        placements[f["id"]] = p
        by_level[lvl].append(f["id"])
    if unplaced:
        notes.append(f"{len(unplaced)} finding(s) have no HFACS level and are not placed: " + ", ".join(unplaced) + ".")
    levels = {str(i): {"name": names[str(i)], "findings": sorted(by_level.get(i, [])),
                       "inferred": bool(by_level.get(i)) and i <= limit} for i in ACCIMAP_LEVELS}
    gaps = [i for i in ACCIMAP_LEVELS if not by_level.get(i)]
    for g in gaps:
        notes.append(f"Level {g} ({names[str(g)]}) has no placement: it is drawn as an empty band.")
    return {"version": ACCIMAP_VERSION, "levels": levels, "placements": placements, "gaps": gaps, "notes": notes}


def graph_item(d: dict, w: dict) -> dict:
    """A ready graph item: one node per level, the most-cited codes under each level, and the causal links
    between the codes shown."""
    F = {f["id"]: f for f in w["findings"]}
    nodes, edges, cites = [], [], set()
    shown = {}                                   # code -> (count, node id) at its busiest level
    for i in ACCIMAP_LEVELS:
        lv = d["levels"][str(i)]
        n = len(lv["findings"])
        node = {"id": f"L{i}", "label": f"L{i} {lv['name']} ({n} finding{'' if n == 1 else 's'})"}
        if lv["inferred"]:
            node["inferred"] = True
        nodes.append(node)
        codes = collections.defaultdict(list)
        for fid in lv["findings"]:
            codes[F[fid]["code"]].append(fid)
        for code in sorted(codes, key=lambda c: (-len(codes[c]), c))[:ACCIMAP_TOP_CODES]:
            fs = codes[code]
            cid = f"L{i}-{code}"
            cn = {"id": cid, "label": f"{code} {F[fs[0]].get('name', '')} ({len(fs)})".replace("  ", " ")}
            if lv["inferred"]:
                cn["inferred"] = True
            nodes.append(cn)
            edges.append({"from": f"L{i}", "to": cid, "label": "holds"})
            if code not in shown or len(fs) > shown[code][0]:
                shown[code] = (len(fs), cid)
            cites.update(sorted(fs, key=lambda x: (-(F[x].get("rating") or 0), x))[:1])
    g = w.get("causal_graph") or {}
    for e in sorted(g.get("edges", []), key=lambda e: (-e.get("mentions", 0), e["from"], e["to"])):
        if e["from"] in shown and e["to"] in shown and e["from"] != e["to"]:
            m = e.get("mentions", 1)
            edges.append({"from": shown[e["from"]][1], "to": shown[e["to"]][1],
                          "label": f"{m} mention" + ("" if m == 1 else "s")})
            cites.update(x for x in e.get("findings", []) if x in F)
    it = {"kind": "graph", "id": "accimap", "nodes": nodes, "edges": edges}
    if cites:
        it["cites"] = sorted(cites)
    return it


def accimap_table_item(d: dict, w: dict, which: str = "levels") -> dict:
    if which != "levels":
        raise ValueError(f"unknown table: {which}")
    F = {f["id"]: f for f in w["findings"]}
    cols = ["Level", "Name", "Findings", "Placement"]
    rows, row_cites = [], []
    for i in ACCIMAP_LEVELS:
        lv = d["levels"][str(i)]
        if not lv["findings"]:
            continue
        rows.append([f"L{i}", lv["name"], len(lv["findings"]), "inferred" if lv["inferred"] else "from the HFACS level"])
        row_cites.append(sorted(lv["findings"], key=lambda x: (-(F[x].get("rating") or 0), x))[:ACCIMAP_ROW_CITES])
    return {"kind": "table", "id": "accimap-levels", "columns": cols, "rows": rows, "row_cites": row_cites,
            "cites": sorted({x for c in row_cites for x in c})}


def cmd_accimap(a):
    ws = _abs(a.ws)
    w = load_ws(ws)
    amap = accimap_load_map(a.map)
    gp = ws / "causal_graph.json"
    if gp.is_file():
        w["causal_graph"] = json.loads(gp.read_text(encoding="utf-8"))
    d = place(w, amap)
    write_json(ws / ACCIMAP_FILE, d)
    record_derived(ws, ACCIMAP_FILE,
                   {n: file_sha256(ws / n) for n in ("findings.json", "clusters.json", "causal_graph.json")
                    if (ws / n).exists()})
    if a.graph_item:
        print(json.dumps(graph_item(d, w), indent=1, ensure_ascii=False))
        return
    if a.table_item:
        t = accimap_table_item(d, w, a.table_item)
        if not t["rows"]:
            sys.exit("The levels table has no rows for this workspace")
        print(json.dumps(t, indent=1, ensure_ascii=False))
        return
    if a.json:
        print(json.dumps(d, indent=1, ensure_ascii=False))
        return
    print(f"Wrote {ACCIMAP_FILE}: {len(d['placements'])} findings placed, "
          f"{len(d['gaps'])} empty level(s)" + (f" ({', '.join(map(str, d['gaps']))})." if d["gaps"] else "."))
    for n in d["notes"]:
        print(f"Note: {n}")
    print("\n| Level | Name | Findings | Placement |\n|---|---|---:|---|")
    for i in ACCIMAP_LEVELS:
        lv = d["levels"][str(i)]
        print(f"| L{i} | {lv['name']} | {len(lv['findings'])} | "
              f"{'inferred' if lv['inferred'] else ('gap' if not lv['findings'] else 'from the HFACS level')} |")
