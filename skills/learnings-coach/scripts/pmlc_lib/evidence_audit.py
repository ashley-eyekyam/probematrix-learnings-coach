"""The evidence-audit command: how well the evidence behind the findings holds up, computed by the engine (L3-15).

The strength of a finding or a learning is counted here, never judged by the model: `check-register` holds a
learning's `evidence_strength` to this module's answer once `evidence_audit.json` exists."""
from __future__ import annotations

import collections
import json
import re

from .util import _abs
from .workspace import file_sha256, load_ws, record_derived

EVAUDIT_FILE = "evidence_audit.json"
EVAUDIT_CODE_RX = re.compile(r"\b[A-Z]{2,4} \d\.\d{1,2}\b")
EVAUDIT_CONCENTRATION_MIN = 10          # an item that supports this many findings is a concentration
EVAUDIT_TABLE_KINDS = ("scorecard", "concentration", "levels")
EVAUDIT_ROW_CITES = 5
EVAUDIT_DOCUMENT = "document"
EVAUDIT_WITNESS = "witness_statement"
EVAUDIT_STRENGTHS = ("direct", "corroborated", "inferred")


def _evaudit_ids(f: dict) -> list:
    """The evidence ids a finding names in its Linked Evidence column, distinct, in order."""
    seen = []
    for e in f.get("evidence") or []:
        if e not in seen:
            seen.append(e)
    return seen


def _evaudit_types(ids, ev_by_id: dict) -> list:
    return sorted({(ev_by_id.get(i) or {}).get("type") or "" for i in ids} - {""})


def _evaudit_strength(ids, ev_by_id: dict) -> str:
    """corroborated: 2+ distinct items of 2+ types; direct: at least one item; inferred: none."""
    if not ids:
        return "inferred"
    if len(ids) >= 2 and len(_evaudit_types(ids, ev_by_id)) >= 2:
        return "corroborated"
    return "direct"


def finding_strength(f: dict, ev_by_id: dict) -> str:
    return _evaudit_strength(_evaudit_ids(f), ev_by_id)


def learning_strength(cites: list, w: dict) -> str:
    """The strength of a learning that cites these finding ids: the evidence of all of them, pooled."""
    by_id = {f["id"]: f for f in w.get("findings", [])}
    pooled = []
    for c in cites or []:
        for e in _evaudit_ids(by_id.get(c, {})):
            if e not in pooled:
                pooled.append(e)
    return _evaudit_strength(pooled, w.get("evidence", {}))


def audit(w: dict) -> dict:
    F, ev = w.get("findings", []), w.get("evidence", {})
    out_f, single, doc_only, just_only = {}, [], [], []
    levels = {str(n): {"findings": 0, "single_source": 0, "document_only": 0, "witness": 0} for n in (1, 2, 3, 4)}
    supports = collections.Counter()
    carried = {f.get("code") for f in F}
    named = set()
    for f in sorted(F, key=lambda x: x["id"]):
        ids = _evaudit_ids(f)
        types = _evaudit_types(ids, ev)
        out_f[f["id"]] = {"strength": _evaudit_strength(ids, ev), "sources": len(ids), "types": types}
        lv = levels.get(str(f.get("level")))
        if lv is not None:
            lv["findings"] += 1
        if len(f.get("evidence") or []) == 1:  # raw column rule: the plan and spec calibration value (203)
            single.append(f["id"])
            if lv is not None:
                lv["single_source"] += 1
        if ids and all((ev.get(i) or {}).get("type") == EVAUDIT_DOCUMENT for i in ids):
            doc_only.append(f["id"])
            if lv is not None:
                lv["document_only"] += 1
        if any((ev.get(i) or {}).get("type") == EVAUDIT_WITNESS for i in ids) and lv is not None:
            lv["witness"] += 1
        if not ids:
            just_only.append(f["id"])
        supports.update(ids)
        named.update(EVAUDIT_CODE_RX.findall(f.get("causal") or ""))
    n = len(F)
    conc = [{"evidence": e, "findings": c, "share": round(c / n, 3) if n else 0.0}
            for e, c in sorted(supports.items(), key=lambda kv: (-kv[1], kv[0])) if c >= EVAUDIT_CONCENTRATION_MIN]
    notes = []
    if not ev:
        notes.append("This workspace has no evidence items (no Evidence Links rows): every finding rests on its "
                     "justification alone, so every strength is 'inferred'.")
    elif F and not any(_evaudit_ids(f) for f in F):
        notes.append("No finding names an evidence item: every strength is 'inferred'.")
    return {"version": 1, "findings": out_f, "levels": levels, "single_source": single, "document_only": doc_only,
            "concentration": conc, "justification_only": just_only,
            "unknown_codes": sorted(named - carried), "notes": notes}


# ----------------------------------------------------------------------------- table items

def _evaudit_table(item_id, columns, rows, row_cites) -> dict:
    return {"kind": "table", "id": item_id, "columns": columns, "rows": rows, "row_cites": row_cites,
            "cites": sorted({x for c in row_cites for x in c})}


def _evaudit_best(w: dict, ids) -> list:
    rating = {f["id"]: f.get("rating") or 0 for f in w.get("findings", [])}
    return sorted(ids, key=lambda i: (-rating.get(i, 0), i))[:EVAUDIT_ROW_CITES]


def audit_table_item(w: dict, a: dict, which: str) -> dict:
    F = w.get("findings", [])
    if which == "scorecard":
        by = collections.defaultdict(list)
        for fid, v in a["findings"].items():
            by[v["strength"]].append(fid)
        rows = [[s, len(by[s])] for s in EVAUDIT_STRENGTHS]
        return _evaudit_table("evidence-scorecard-table", ["Evidence strength", "Findings"], rows,
                      [_evaudit_best(w, by[s]) for s in EVAUDIT_STRENGTHS])
    if which == "concentration":
        by_ev = collections.defaultdict(list)
        for f in F:
            for e in _evaudit_ids(f):
                by_ev[e].append(f["id"])
        rows = [[c["evidence"], c["findings"], f"{round(c['share'] * 100)}%"] for c in a["concentration"]]
        return _evaudit_table("evidence-concentration-table", ["Evidence item", "Findings supported", "Share of findings"],
                      rows, [_evaudit_best(w, by_ev[c["evidence"]]) for c in a["concentration"]])
    by_level = collections.defaultdict(lambda: collections.defaultdict(list))
    for f in F:
        by_level[str(f.get("level"))]["all"].append(f["id"])
    sets = {"single_source": set(a["single_source"]), "document_only": set(a["document_only"])}
    rows, cites = [], []
    for lv in ("1", "2", "3", "4"):
        v = a["levels"][lv]
        rows.append([f"Level {lv}", v["findings"], v["single_source"], v["document_only"], v["witness"]])
        mine = by_level[lv]["all"]
        cites.append(_evaudit_best(w, [i for i in mine if i in sets["single_source"]] or mine))
    return _evaudit_table("evidence-levels-table",
                  ["HFACS level", "Findings", "Single-source", "Document-only", "With a witness statement"],
                  rows, cites)


# ----------------------------------------------------------------------------- command

def cmd_evidence_audit(a):
    ws = _abs(a.ws)
    w = load_ws(ws)
    res = audit(w)
    (ws / EVAUDIT_FILE).write_text(json.dumps(res, indent=1, ensure_ascii=False, sort_keys=True), encoding="utf-8")
    record_derived(ws, EVAUDIT_FILE, {n: file_sha256(ws / n) for n in ("findings.json", "evidence.json")
                                  if (ws / n).exists()})
    if a.table_item:
        print(json.dumps(audit_table_item(w, res, a.table_item), indent=1, ensure_ascii=False))
        return
    if a.json:
        print(json.dumps({"command": "evidence-audit", "ok": True, "exit_code": 0, "audit": res},
                         indent=1, ensure_ascii=False, sort_keys=True))
        return
    n = len(res["findings"])
    c = collections.Counter(v["strength"] for v in res["findings"].values())
    print(f"Evidence audit of {n} findings written to {ws / EVAUDIT_FILE}.\n")
    print("| Measure | Findings |\n|---|---:|")
    for s in EVAUDIT_STRENGTHS:
        print(f"| {s} | {c.get(s, 0)} |")
    print(f"| single-source | {len(res['single_source'])} |\n| document-only | {len(res['document_only'])} |\n"
          f"| justification only | {len(res['justification_only'])} |")
    for x in res["concentration"][:5]:
        print(f"\nConcentration: {x['evidence']} supports {x['findings']} findings ({round(x['share'] * 100)}%).")
    for x in res["notes"]:
        print(f"\nNote: {x}")
