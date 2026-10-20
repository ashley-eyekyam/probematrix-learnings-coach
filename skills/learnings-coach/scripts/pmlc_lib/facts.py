"""The facts command: the numbers every pack and brief quotes, in one place."""
from __future__ import annotations

import collections
import json
import sys
from pathlib import Path

from .classify import TIER_LABELS
from .templates import load_register_entries
from .util import _abs
from .workspace import incident_date, load_ws, outputs_dir, top_rating


def facts(ws, register=None) -> dict:
    w = load_ws(ws)
    F = w["findings"]
    lv = collections.Counter(f["level"] for f in F)
    levels = {str(k): lv.get(k, 0) for k in (1, 2, 3, 4)}
    top = top_rating(w)
    cl = w.get("clusters")
    entities = {e: d["n"] for e, d in sorted(cl["entities"].items())} if cl else {}
    tc = collections.Counter(t for v in cl["findings"].values() for t in v["T"]) if cl else {}
    p1 = None
    if register:
        p1 = {t: [] for t in TIER_LABELS}
        for e in load_register_entries(register):
            if e.get("priority") == 1:
                for t in e.get("tiers") or []:
                    if t in p1:
                        p1[t].append(e["lr_id"])
    return {"findings": len(F), "evidence_items": len(w.get("evidence", {})), "levels": levels,
            "l34_share": round((levels["3"] + levels["4"]) / len(F), 3) if F else 0,
            "entities": entities, "tiers": dict(sorted(tc.items())), "top_rating": top,
            "top_rated": sum(1 for f in F if top and (f.get("rating") or 0) == top),
            "incident_date": incident_date(w), "p1_by_tier": p1}


def cmd_facts(a):
    ws = _abs(a.ws)
    reg = Path(a.register) if a.register else outputs_dir(ws) / "learnings-register.json"
    if a.register and not reg.is_file():
        sys.exit(f"No Learnings Register at {reg}")
    d = facts(ws, reg if reg.is_file() else None)
    if a.json:
        print(json.dumps(d, indent=1, ensure_ascii=False))
        return
    print("| Fact | Value |\n|---|---|")
    for k, v in d.items():
        if v is None:
            v = "not available (no register)" if k == "p1_by_tier" else "unknown"
        elif isinstance(v, dict):
            v = "; ".join(f"{x}: {', '.join(y) if isinstance(y, list) else y}" for x, y in v.items()) or "none"
        print(f"| {k} | {v} |")
