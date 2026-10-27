"""The safety alert's grade (spec §6.2, Ruling P6-3, owner decision OD6-1): alert-grade reads a Learnings Register and
says which learnings an alert carries by default and what its grade is.

- The grade is the highest `urgency` (alert > notice > information) among the chosen learnings, with grade_source
  "register urgency".
- When none of them has `urgency`, the engine suggests one and says so with grade_source "suggested": priority 1 with
  other sites or industry-wide -> alert; priority 1 at the same site, or priority 2 -> notice; otherwise information.
  The skill then asks the user, and the pack records "chosen by the user". "suggested" never appears in a pack.
- The default choice is the priority-1 rows ordered by transferability (industry-wide, other sites, same site), then
  evidence_strength (corroborated, direct, inferred), then LR-ID, top 3. --lr overrides it.

It reads the register only and writes nothing; it never sets an owner, a date or a grade in a pack (D7)."""
from __future__ import annotations

import json
import sys
from pathlib import Path

# Fixed copy (Phase 6, verbatim): where a pack's grade came from. "suggested" is the engine's own word for a grade it
# proposes and never appears in a pack: the skill asks the user, and the pack records "chosen by the user".
GRADE_SOURCES = ("register urgency", "chosen by the user")
GRADES = ("alert", "notice", "information")                       # highest first
ALERT_SUGGESTED = "suggested"
ALERT_DEFAULT_TOP = 3
ALERT_TRANSFER_RANK = {"industry-wide": 0, "other sites": 1, "same site": 2}
ALERT_STRENGTH_RANK = {"corroborated": 0, "direct": 1, "inferred": 2}
ALERT_NO_P1 = "no priority-1 learning: choose with --lr"
ALERT_RULE = ("priority 1 with other sites or industry-wide -> alert; priority 1 at the same site, or priority 2 -> "
              "notice; otherwise information")
ALERT_GRADE_WORDS = "alert, notice or information"
ALERT_ASK = 'ask the user; the pack records grade_source "chosen by the user"'


def _alert_s(v) -> str:
    return v.strip().lower() if isinstance(v, str) else ""


def _alert_priority(e):
    p = e.get("priority")
    if isinstance(p, bool):
        return None
    if isinstance(p, int):
        return p
    if isinstance(p, str) and p.strip().isdigit():
        return int(p.strip())
    return None


def suggest_grade(e: dict) -> str:
    """The P6-3 suggestion for one register entry, from its priority and transferability (its urgency is ignored)."""
    p, t = _alert_priority(e), _alert_s(e.get("transferability"))
    if p == 1:
        return "alert" if t in ("other sites", "industry-wide") else "notice"
    return "notice" if p == 2 else "information"


def default_choice(entries, top: int = ALERT_DEFAULT_TOP) -> list:
    """The LR-IDs an alert carries by default: the priority-1 rows, by transferability, evidence strength, LR-ID."""
    p1 = [e for e in entries if isinstance(e, dict) and _alert_priority(e) == 1 and e.get("lr_id")]
    p1.sort(key=lambda e: (ALERT_TRANSFER_RANK.get(_alert_s(e.get("transferability")), 9),
                           ALERT_STRENGTH_RANK.get(_alert_s(e.get("evidence_strength")), 9), str(e["lr_id"])))
    return [str(e["lr_id"]) for e in p1[:top]]


def grade(entries, lr_ids=None) -> dict:
    """{"grade", "grade_source", "suggested", "learnings", "notes"} for the chosen learnings (lr_ids, or the default
    choice). An unknown LR-ID raises KeyError (the command checks first)."""
    by_id = {str(e.get("lr_id")): e for e in entries if isinstance(e, dict) and e.get("lr_id")}
    chosen = list(dict.fromkeys(lr_ids)) if lr_ids else default_choice(entries)
    if not chosen:
        return {"grade": None, "grade_source": None, "suggested": None, "learnings": [], "notes": [ALERT_NO_P1]}
    rows = [by_id[lr] for lr in chosen]
    urg = {lr: _alert_s(e.get("urgency")) for lr, e in zip(chosen, rows) if _alert_s(e.get("urgency")) in GRADES}
    odd = [(lr, e.get("urgency")) for lr, e in zip(chosen, rows)
           if e.get("urgency") not in (None, "") and lr not in urg]
    notes = [f"{lr} has urgency {str(u)!r}, not one of {ALERT_GRADE_WORDS}: it is ignored" for lr, u in odd]
    if lr_ids:
        notes += [f"{lr} is priority {_alert_priority(e) if _alert_priority(e) is not None else 'unknown'}; "
                  f"the safety-alert check needs priority 1" for lr, e in zip(chosen, rows) if _alert_priority(e) != 1]
    if urg:
        missing = [lr for lr in chosen if lr not in urg and lr not in dict(odd)]
        notes = ([f"no urgency in the register for {', '.join(missing)}"] if missing else []) + notes
        return {"grade": min(urg.values(), key=GRADES.index), "grade_source": "register urgency", "suggested": None,
                "learnings": chosen, "notes": notes}
    by_learning = {lr: suggest_grade(e) for lr, e in zip(chosen, rows)}
    g = min(by_learning.values(), key=GRADES.index)
    return {"grade": g, "grade_source": ALERT_SUGGESTED, "learnings": chosen, "notes": notes,
            "suggested": {"grade": g, "by_learning": by_learning, "rule": ALERT_RULE}}


def _alert_fail(msg):
    print(msg, file=sys.stderr)
    sys.exit(2)


def _alert_entries(path: Path) -> list:
    """The register's entries, or exit 2 with one sentence naming the file (a pack, a missing file, bad JSON).
    The plan named templates.load_register_entries here; that loader does not validate and would traceback on a pack,
    so alert-grade validates with its own (Task 2 review m4)."""
    if not path.is_file():
        _alert_fail(f"alert-grade: no Learnings Register at {path}: write it first, or pass --register FILE")
    try:
        d = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        _alert_fail(f"alert-grade reads a learnings register, and {path} is not one")
    entries = d.get("entries") if isinstance(d, dict) else d
    if (not isinstance(entries, list) or (isinstance(d, dict) and "sections" in d)
            or not all(isinstance(e, dict) and e.get("lr_id") for e in entries)):
        _alert_fail(f"alert-grade reads a learnings register, and {path} is not one")
    return entries


def cmd_alert_grade(a):
    from .pack.items import _default_register
    from .util import _abs
    reg = Path(a.register) if a.register else _default_register(_abs(a.ws))
    entries = _alert_entries(reg)
    known = {str(e["lr_id"]) for e in entries}
    for lr in a.lr or []:
        if lr not in known:
            _alert_fail(f"alert-grade: {lr} is not in the register {reg}")
    g = grade(entries, a.lr)
    if a.json:
        print(json.dumps(g, indent=1, sort_keys=True, ensure_ascii=False))
        return
    lrs = ", ".join(g["learnings"])
    if g["grade"] is None:
        print("alert-grade: no learnings chosen")
    elif g["grade_source"] == ALERT_SUGGESTED:
        print(f"alert-grade: suggested {g['grade']} for {lrs} (no urgency in the register)")
        print(f"rule: {ALERT_RULE}")
        print(ALERT_ASK)
    else:
        print(f'alert-grade: {g["grade"]} for {lrs} (grade_source "{g["grade_source"]}")')
    for n in g["notes"]:
        print(f"note: {n}")
