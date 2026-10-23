"""The hfacs-profile command: the level x subcategory heat map, code recurrence and causal feed counts.

For one incident these counts describe this investigation only. They are not rates, trends or a benchmark."""
from __future__ import annotations

import collections
import json
import sys
from pathlib import Path

from .util import REFS, _abs, write_json
from .workspace import file_sha256, load_ws, record_derived

HP_VERSION = 1
HP_ROW_CITES = 5            # Finding IDs cited per table row: the highest rated, ties by ID
MIN_RECURRENCE = 2       # a code is "recurring" when two or more findings carry it
HP_TABLE_KINDS = ["heatmap", "feeds", "recurrence"]


def _hp_prefixes() -> dict:
    return json.loads((REFS / "hfacs-codes.json").read_text(encoding="utf-8"))["prefixes"]


def _hp_best(fs, n=HP_ROW_CITES) -> list:
    """IDs of the n highest-rated findings (ties by ID)."""
    return [f["id"] for f in sorted(fs, key=lambda f: (-(f.get("rating") or 0), f["id"]))[:n]]


def _hp_prefix(code) -> str:
    return str(code or "").split()[0] if str(code or "").split() else ""


def profile(w: dict, graph: dict | None = None) -> dict:
    """The hfacs_profile.json document for a loaded workspace. `graph` is the parsed causal_graph.json, or None."""
    F = w["findings"]
    known = _hp_prefixes()
    top = max(((f.get("rating") or 0) for f in F), default=0)
    notes = []
    levels = {str(i): 0 for i in (1, 2, 3, 4)}
    cells = collections.defaultdict(list)
    unresolved = set()
    for f in F:
        pre = _hp_prefix(f.get("code"))
        info = known.get(pre)
        if info is None:
            unresolved.add(pre)
        lvl = f.get("level") or (info or {}).get("level")
        if lvl in (1, 2, 3, 4):
            levels[str(lvl)] += 1
        sub = f.get("subcategory") or (info or {}).get("subcategory") or "Unspecified"
        cells[(lvl or 0, sub)].append(f)
    total = sum(levels.values())
    share = round((levels["3"] + levels["4"]) / total, 3) if total else 0.0
    matrix = []
    for (lvl, sub), fs in sorted(cells.items(), key=lambda kv: (kv[0][0], kv[0][1])):
        is_top = [f for f in fs if top and (f.get("rating") or 0) == top]
        matrix.append({"level": lvl, "subcategory": sub,
                       "prefix": "/".join(sorted({_hp_prefix(f.get("code")) for f in fs})),
                       "top": len(is_top), "other": len(fs) - len(is_top), "findings": _hp_best(fs)})
    by_code = collections.defaultdict(list)
    for f in F:
        by_code[f["code"]].append(f)
    recurrence = [{"code": c, "name": fs[0].get("name", ""), "n": len(fs), "findings": _hp_best(fs)}
                  for c, fs in by_code.items() if len(fs) >= MIN_RECURRENCE]
    recurrence.sort(key=lambda r: (-r["n"], r["code"]))
    feeds = []
    if graph is None:
        notes.append("No causal_graph.json: run causal to count which codes feed which.")
    elif not graph.get("edges"):
        notes.append("causal_graph.json has no links, so no code feeds another.")
    else:
        names = {n["code"]: n.get("name", "") for n in graph.get("nodes", [])}
        out, inn, ids = collections.Counter(), collections.Counter(), collections.defaultdict(set)
        for e in graph["edges"]:
            out[e["from"]] += 1
            inn[e["to"]] += 1
            for x in e.get("findings", []):
                if str(x).startswith("FND-"):
                    ids[e["from"]].add(x)
                    ids[e["to"]].add(x)
        rating = {f["id"]: f.get("rating") or 0 for f in F}
        for c in sorted(set(out) | set(inn)):
            cites = sorted(ids[c], key=lambda x: (-rating.get(x, 0), x))[:HP_ROW_CITES] or _hp_best(by_code.get(c, []))
            feeds.append({"code": c, "name": names.get(c, ""), "out": out[c], "in": inn[c], "findings": cites})
        feeds.sort(key=lambda r: (-r["out"], -r["in"], r["code"]))
    if unresolved:
        notes.append("Prefix not in hfacs-codes.json: " + ", ".join(sorted(unresolved)) + ".")
    return {"version": HP_VERSION, "levels": levels, "share_l34": share, "matrix": matrix, "recurrence": recurrence,
            "feeds": feeds, "unresolved": sorted(unresolved), "notes": notes}


def _hp_table(item_id, columns, rows, row_cites) -> dict:
    return {"kind": "table", "id": item_id, "columns": columns, "rows": rows, "row_cites": row_cites,
            "cites": sorted({x for c in row_cites for x in c})}


def table_item(prof: dict, which: str) -> dict:
    """A ready table item (heatmap, feeds or recurrence) from a profile. Every row carries its cites."""
    if which == "heatmap":
        rows = prof["matrix"]
        return _hp_table("hfacs-heatmap", ["Level", "Subcategory", "Prefix", "Top rated", "Other"],
                      [[f"L{r['level']}", r["subcategory"], r["prefix"], r["top"], r["other"]] for r in rows],
                      [r["findings"] for r in rows])
    if which == "feeds":
        rows = prof["feeds"]
        return _hp_table("hfacs-feeds", ["Code", "Name", "Links out", "Links in"],
                      [[r["code"], r["name"], r["out"], r["in"]] for r in rows], [r["findings"] for r in rows])
    if which == "recurrence":
        rows = prof["recurrence"]
        return _hp_table("hfacs-recurrence", ["Code", "Name", "Findings"],
                      [[r["code"], r["name"], r["n"]] for r in rows], [r["findings"] for r in rows])
    raise ValueError(f"unknown table: {which}")


def cmd_hfacs_profile(a):
    ws = _abs(a.ws)
    w = load_ws(ws)
    gp = ws / "causal_graph.json"
    graph = json.loads(gp.read_text(encoding="utf-8")) if gp.is_file() else None
    prof = profile(w, graph)
    write_json(ws / "hfacs_profile.json", prof)
    record_derived(ws, "hfacs_profile.json",
                   {n: file_sha256(ws / n) for n in ("findings.json", "causal_graph.json") if (ws / n).exists()})
    if a.table_item:
        rows = table_item(prof, a.table_item)
        if not rows["rows"]:
            sys.exit(f"The {a.table_item} table has no rows for this workspace")
        print(json.dumps(rows, indent=1, ensure_ascii=False))
        return
    if a.json:
        print(json.dumps(prof, indent=1, ensure_ascii=False))
        return
    print(f"Wrote {Path(ws, 'hfacs_profile.json').name}: {sum(prof['levels'].values())} findings, "
          f"{prof['share_l34']:.1%} at levels 3 and 4, {len(prof['matrix'])} heat-map rows, "
          f"{len(prof['recurrence'])} recurring codes, {len(prof['feeds'])} codes in the causal graph.")
    for n in prof["notes"]:
        print(f"Note: {n}")
    print("\n| Level | Subcategory | Top rated | Other |\n|---|---|---:|---:|")
    for r in prof["matrix"]:
        print(f"| L{r['level']} | {r['subcategory']} | {r['top']} | {r['other']} |")
