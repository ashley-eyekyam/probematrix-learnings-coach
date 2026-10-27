"""The wai-wad command: work as imagined set against work as done (Phase 6, Task 4).

For each HFACS code it separates the findings backed by documents (how the work was imagined) from those backed by
witness statements, log records or recordings (how the work was done), and lists the codes that have both, so a
learning team can ask what made sense at the time. It also marks findings whose justification uses counterfactual
wording (Ruling P6-6) and turns them into questions. The type sets and the word list are data in
references/learning-team.json. The engine counts; it never judges."""
from __future__ import annotations

import json
import re

from .lint import load_terms, personal_name
from .util import _abs, REFS
from .workspace import file_sha256, load_ws, record_derived

WAIWAD_FILE = "wai_wad.json"
WAIWAD_REF = REFS / "learning-team.json"
WAIWAD_TABLE_KINDS = ("gaps", "codes")
WAIWAD_PROMPT_MAX = 30
WAIWAD_ROW_CITES = 5
WAIWAD_PROMPT_RULES = ("JC2", "JC3", "JC4", "JC5", "JC12")
_WAIWAD_CACHE = {}


def waiwad_lexicon() -> dict:
    """references/learning-team.json, read once."""
    if "d" not in _WAIWAD_CACHE:
        _WAIWAD_CACHE["d"] = json.loads(WAIWAD_REF.read_text(encoding="utf-8"))
    return _WAIWAD_CACHE["d"]


def waiwad_patterns(lex=None) -> list:
    """The compiled counterfactual patterns: whole words, case-insensitive."""
    lex = lex or waiwad_lexicon()
    return [re.compile(p, re.I) for p in lex["counterfactual"]]


def counterfactual_hits(text, patterns=None) -> list:
    """The distinct matched words of a text, lower-cased, in order of first appearance."""
    out = []
    for rx in patterns or waiwad_patterns():
        for m in rx.finditer(text or ""):
            s = m.group(0).lower().replace("’", "'")
            if s not in out:
                out.append(s)
    return out


def _waiwad_ids(f: dict) -> list:
    seen = []
    for e in f.get("evidence") or []:
        if e not in seen:
            seen.append(e)
    return seen


def waiwad_compare(w: dict) -> dict:
    lex = waiwad_lexicon()
    doc_t, wad_t = set(lex["doc_types"]), set(lex["wad_types"])
    ev = w.get("evidence", {})
    pats = waiwad_patterns(lex)
    codes, counterfactual = {}, []
    n_both = n_wad = 0
    for f in sorted(w.get("findings", []), key=lambda x: x["id"]):
        ids = _waiwad_ids(f)
        types = {(ev.get(i) or {}).get("type") for i in ids}
        has_doc, has_wad = bool(types & doc_t), bool(types & wad_t)
        n_wad += has_wad
        n_both += has_doc and has_wad
        c = codes.setdefault(f.get("code") or "", {"name": f.get("name") or "", "findings": [], "doc": [], "wad": [],
                                                   "both": [], "_doc_ev": set(), "_wad_ev": set()})
        c["findings"].append(f["id"])
        if has_doc:
            c["doc"].append(f["id"])
            c["_doc_ev"].update(i for i in ids if (ev.get(i) or {}).get("type") in doc_t)
        if has_wad:
            c["wad"].append(f["id"])
            c["_wad_ev"].update(i for i in ids if (ev.get(i) or {}).get("type") in wad_t)
        if has_doc and has_wad:
            c["both"].append(f["id"])
        if counterfactual_hits(f.get("justification"), pats):
            counterfactual.append(f["id"])
    gaps = []
    for code in sorted(codes):
        c = codes[code]
        if c["_doc_ev"] and c["_wad_ev"]:       # per code: any linked document, and any linked work-as-done item
            gaps.append({"code": code, "name": c["name"], "doc_evidence": sorted(c["_doc_ev"]),
                         "wad_evidence": sorted(c["_wad_ev"]), "findings": c["findings"]})
    for c in codes.values():
        del c["_doc_ev"], c["_wad_ev"]
    notes = []
    nt = lex["notes"]
    if not ev:
        notes.append(nt["no_evidence"])
    if not n_wad:
        notes.append(nt["no_wad"])
    elif not gaps:
        notes.append(nt["no_pairs"])
    if w.get("findings") and not counterfactual:
        notes.append(nt["no_counterfactual"])
    return {"version": 1, "doc_types": list(lex["doc_types"]), "wad_types": list(lex["wad_types"]),
            "codes": codes, "gaps": gaps, "counterfactual": counterfactual,
            "counts": {"codes": len(codes), "codes_both": len(gaps), "findings_both": n_both,
                       "findings_wad": n_wad, "counterfactual": len(counterfactual)},
            "notes": notes}


# ----------------------------------------------------------------------------- items

def _waiwad_best(w: dict, ids) -> list:
    rating = {f["id"]: f.get("rating") or 0 for f in w.get("findings", [])}
    return sorted(ids, key=lambda i: (-rating.get(i, 0), i))[:WAIWAD_ROW_CITES]


def _waiwad_table(item_id, columns, rows, row_cites) -> dict:
    return {"kind": "table", "id": item_id, "columns": columns, "rows": rows, "row_cites": row_cites,
            "cites": sorted({x for c in row_cites for x in c})}


def waiwad_table_item(d: dict, which: str, w: dict = None) -> dict:
    """A ready table item: `gaps` (the codes with both kinds of evidence) or `codes` (every code, the counts)."""
    w = w or {"findings": []}
    if which == "gaps":
        rows = [[g["code"], g["name"], ", ".join(g["doc_evidence"]), ", ".join(g["wad_evidence"])] for g in d["gaps"]]
        return _waiwad_table("wai-wad-gaps-table", ["Code", "Name", "Document evidence", "Work-as-done evidence"],
                             rows, [_waiwad_best(w, g["findings"]) for g in d["gaps"]])
    rows, cites = [], []
    for code in sorted(d["codes"]):
        c = d["codes"][code]
        rows.append([code, c["name"], len(c["findings"]), len(c["doc"]), len(c["wad"]), len(c["both"])])
        cites.append(_waiwad_best(w, c["findings"]))
    return _waiwad_table("wai-wad-codes-table",
                         ["Code", "Name", "Findings", "With documents", "With work-as-done evidence", "With both"],
                         rows, cites)


def _waiwad_clean(c, text) -> bool:
    """True when the text trips none of the just-culture word rules (JC2 to JC5, JC12) or the counterfactual list."""
    terms = load_terms()["rules"]
    for rule in WAIWAD_PROMPT_RULES:
        if any(re.search(p, text, re.I) for p in terms[rule]["patterns"]):
            return False
    return not counterfactual_hits(text, c)


def _waiwad_phrase(f: dict, pats, w: dict) -> str:
    """The topic of a question: the finding's short description, else its label or name, else its code. The first
    that holds no flagged wording, so the question never repeats the export's counterfactual words."""
    for key in ("short", "label", "name"):
        t = (f.get(key) or "").strip().rstrip(".")
        if t and _waiwad_clean(pats, t) and not personal_name(t, w):
            return f"this condition: {t}"
    return f"this condition, coded {f.get('code') or f['id']}"


def waiwad_prompt_items(d: dict, top=None, w: dict = None) -> list:
    """`question` items for the findings with counterfactual wording, highest rating first, at most `top`."""
    w = w or {"findings": []}
    by_id = {f["id"]: f for f in w.get("findings", [])}
    pats = waiwad_patterns()
    ids = sorted(d["counterfactual"], key=lambda i: (-(by_id.get(i, {}).get("rating") or 0), i))
    n = WAIWAD_PROMPT_MAX if top is None else max(0, int(top))
    out = []
    for fid in ids[:n]:
        f = by_id.get(fid)
        if not f:
            continue
        hits = counterfactual_hits(f.get("justification"), pats)
        out.append({"kind": "question", "id": f"wai-wad-prompt-{len(out) + 1:02d}",
                    "question": f"What made sense at the time about {_waiwad_phrase(f, pats, w)}?",
                    "why": "The export's wording is counterfactual: " + ", ".join(f'"{h}"' for h in hits),
                    "cites": [fid]})
    return out


# ----------------------------------------------------------------------------- command

def cmd_wai_wad(a):
    ws = _abs(a.ws)
    w = load_ws(ws)
    res = waiwad_compare(w)
    (ws / WAIWAD_FILE).write_text(json.dumps(res, indent=1, ensure_ascii=False, sort_keys=True), encoding="utf-8")
    record_derived(ws, WAIWAD_FILE, {n: file_sha256(ws / n) for n in ("findings.json", "evidence.json")
                                     if (ws / n).exists()})
    if a.table_item:
        print(json.dumps(waiwad_table_item(res, a.table_item, w), indent=1, ensure_ascii=False))
        return
    if a.items:
        print(json.dumps(waiwad_prompt_items(res, a.top, w), indent=1, ensure_ascii=False))
        return
    if a.json:
        print(json.dumps({"command": "wai-wad", "ok": True, "exit_code": 0, "wai_wad": res},
                         indent=1, ensure_ascii=False, sort_keys=True))
        return
    c = res["counts"]
    print(f"Work as imagined and work as done: {c['codes']} codes, written to {ws / WAIWAD_FILE}.\n")
    print(f"- codes with both document and work-as-done evidence: {c['codes_both']} of {c['codes']}")
    print(f"- findings with both: {c['findings_both']}")
    print(f"- findings with any work-as-done evidence: {c['findings_wad']}")
    print(f"- findings with counterfactual wording: {c['counterfactual']}")
    for x in res["notes"]:
        print(f"\nNote: {x}")
