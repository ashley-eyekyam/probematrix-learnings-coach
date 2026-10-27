"""effect-plan: the effectiveness schedule of a Learnings Register (plan ruling P6-8). For each learning it sets out what
to check and when, as offsets counted from adoption (never a calendar date, D7), with the Kirkpatrick level of each check
and the Jacobsson spread, depth and duration. It reads a register only. It never writes an owner, a date or a status."""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

from .register.check import HOC_TIERS, norm_hoc
from .rec_review import REC_REVIEW_REFUSAL, rr_is_register
from .util import _s

EFFECT_PLAN_FILE = "effect_plan.json"
EFFECT_AUDIT_Q = "What would an auditor see that shows {lr} is applied?"
EFFECT_TABLE_KINDS = ("schedule", "levels", "indicators")
EFFECT_PLAN_REFUSAL = REC_REVIEW_REFUSAL.replace("rec-review", "effect-plan")
_EP_CACHE = {}


def _ep_rules() -> dict:
    if "r" not in _EP_CACHE:
        p = Path(__file__).resolve().parents[2] / "references" / "effectiveness.json"
        _EP_CACHE["r"] = json.loads(p.read_text(encoding="utf-8"))
    return _EP_CACHE["r"]


def _ep_recs(e) -> list:
    return [r for r in (e.get("recommendations") or []) if isinstance(r, dict)]


def _ep_priority(e):
    m = re.search(r"\d", _s(e.get("priority")))
    return int(m.group(0)) if m else None


def _ep_indicator(e) -> str:
    v = e.get("verification")
    ind = _s(v.get("indicator")) if isinstance(v, dict) else ""
    if ind:
        return ind
    r = _ep_recs(e)
    return _s(r[0].get("leading_indicator") or r[0].get("indicator")) if r else ""


def _ep_depth(e) -> str:
    R = _ep_rules()
    tiers = {norm_hoc(r.get("hoc_tier")) for r in _ep_recs(e)}
    for t in HOC_TIERS:          # strongest first
        if t in tiers:
            return R["depth"][t]
    return R["unknown"]


def schedule(entries) -> dict:
    """The effect_plan.json shape: one row per check, and the Jacobsson spread, depth and duration per learning."""
    R = _ep_rules()
    rows, learnings, notes = [], {}, []
    for e in entries:
        lid = _s(e.get("lr_id"))
        prio = _ep_priority(e)
        if prio is None:
            notes.append(f"{lid} has no priority: the priority-2 schedule is used.")
        steps = R["schedules"]["1" if prio == 1 else R["default_priority"]]
        leading = _ep_indicator(e)
        for s in steps:
            rows.append({"lr_id": lid, "priority": prio, "offset": s["offset"], "check": s["check"],
                         "kirkpatrick": s["kirkpatrick"], "leading": leading, "lagging": ""})
        learnings[lid] = {"spread": R["spread"].get(_s(e.get("transferability")).lower(), R["unknown"]),
                          "depth": _ep_depth(e), "duration": steps[-1]["offset"]}
    return {"version": 1, "rows": rows, "learnings": learnings, "notes": notes}


def _ep_when(offset) -> str:
    return f"{offset} {_ep_rules()['suffix']}"


def _ep_table(item_id, columns, rows, row_cites) -> dict:
    return {"kind": "table", "id": item_id, "columns": columns, "rows": rows, "row_cites": row_cites,
            "cites": sorted({x for c in row_cites for x in c})}


def _ep_cites(entries) -> dict:
    return {_s(e.get("lr_id")): [x for x in (e.get("finding_ids") or []) if _s(x)][:5] for e in entries}


def effect_table_item(d: dict, entries, which: str) -> dict:
    cites = _ep_cites(entries)
    if which == "schedule":
        rows = [[r["lr_id"], r["priority"] if r["priority"] is not None else "", _ep_when(r["offset"]), r["check"],
                 r["kirkpatrick"]] for r in d["rows"]]
        return _ep_table("effect-schedule", ["LR", "Priority", "When", "Check", "Kirkpatrick"], rows,
                         [cites.get(r["lr_id"], []) for r in d["rows"]])
    if which == "indicators":
        seen, rows = set(), []
        for r in d["rows"]:
            if r["lr_id"] not in seen:
                seen.add(r["lr_id"])
                rows.append([r["lr_id"], r["leading"], r["lagging"]])
        return _ep_table("effect-indicators", ["LR", "Leading", "Lagging"], rows, [cites.get(r[0], []) for r in rows])
    rows, rc = [], []
    for lv, name in _ep_rules()["levels"]:
        lrs = sorted({r["lr_id"] for r in d["rows"] if lv in r["kirkpatrick"].split("-") or r["kirkpatrick"] == lv})
        rows.append([lv, name, len(lrs)])
        rc.append(sorted({x for lr in lrs for x in cites.get(lr, [])})[:5])
    return _ep_table("effect-levels", ["Level", "Check", "Learnings"], rows, rc)


def effect_audit_items(d: dict, entries=None) -> list:
    cites = _ep_cites(entries or [])
    items = []
    for lr in d["learnings"]:
        it = {"kind": "question", "question": EFFECT_AUDIT_Q.format(lr=lr),
              "why": "An auditor checks that the learning is applied, by what they can see or hear, not by what is written."}
        if cites.get(lr):
            it["cites"] = cites[lr]
        items.append(it)
    return items


def _ep_fail(msg):
    print(msg, file=sys.stderr)
    sys.exit(2)


def cmd_effect_plan(a):
    from .workspace import load_ws, record_derived, file_sha256
    ws = Path(a.ws).resolve()
    load_ws(ws)
    p = Path(a.register)
    try:
        reg = json.loads(p.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        _ep_fail(f"effect-plan: cannot read {p} as a learnings register (JSON)")
    if isinstance(reg, dict) and reg.get("entries") == []:
        _ep_fail("effect-plan: the register has no entries, so there is nothing to plan")
    if not rr_is_register(reg):
        _ep_fail(EFFECT_PLAN_REFUSAL)
    entries = reg["entries"] if isinstance(reg, dict) else reg
    d = schedule(entries)
    (ws / EFFECT_PLAN_FILE).write_text(json.dumps(d, indent=1, ensure_ascii=False, sort_keys=True), encoding="utf-8")
    record_derived(ws, EFFECT_PLAN_FILE, {n: file_sha256(ws / n) for n in ("findings.json",) if (ws / n).exists()})
    if a.table_item:
        print(json.dumps(effect_table_item(d, entries, a.table_item), indent=1, ensure_ascii=False))
    elif a.items:
        print(json.dumps(effect_audit_items(d, entries), indent=1, ensure_ascii=False))
    elif a.json:
        print(json.dumps(d, indent=1, ensure_ascii=False, sort_keys=True))
    else:
        print(f"effect-plan: {len(d['rows'])} checks for {len(d['learnings'])} learning(s) written to {ws / EFFECT_PLAN_FILE}.")
        print("Every check is counted from adoption; the organisation sets owners, dates and statuses.")
        for n in d["notes"]:
            print(f"Note: {n}")
