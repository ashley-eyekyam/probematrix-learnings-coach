"""The register-md command: the Learnings Register as Markdown, generated and never hand-written."""
from __future__ import annotations

import json
from pathlib import Path

from .. import BRAND, DRAFT_LABEL
from ..handling import effective_handling, handling_lines, is_draft, status_line
from ..register.xlsx import refuse_pack_as_register, summary_groups
from ..util import _flat
from ..workspace import load_ws, outputs_dir


def _cell(v) -> str:
    return _flat(v).replace("|", "\\|").replace("\n", " ")


def _table(head, rows) -> str:
    return "\n".join(["| " + " | ".join(head) + " |", "|" + "---|" * len(head)]
                     + ["| " + " | ".join(_cell(c) for c in r) + " |" for r in rows])


def _full(e: dict) -> str:
    out = [f"### {e.get('lr_id', '?')}: {_flat(e.get('title'))}"]
    for key, label in (("lesson", "Lesson"), ("context", "Context")):
        if _flat(e.get(key)):
            out.append(f"**{label}:** {_flat(e[key])}")
    meta = [f"{label}: {_flat(e.get(k))}" for k, label in (
        ("owner_entity", "Owner entity"), ("hfacs_level", "HFACS level"), ("urgency", "Urgency"),
        ("recommendation_class", "Class"), ("recipient_role", "Recipient"),
        ("regulatory_touchpoint", "Regulatory touchpoint")) if _flat(e.get(k))]
    if meta:
        out.append(" · ".join(meta))
    recs = [r for r in (e.get("recommendations") or []) if isinstance(r, dict)]
    if recs:
        out.append(_table(["What should change", "Control tier", "Leading indicator"],
                          [[r.get("what"), r.get("hoc_tier"), r.get("leading_indicator")] for r in recs]))
    if e.get("why_not_stronger"):
        out.append(f"**Why no stronger fix:** {_flat(e['why_not_stronger'])}")
    out.append(f"**Findings:** {_flat(e.get('finding_ids'))} · **Evidence:** {_flat(e.get('evidence_ids'))}")
    if e.get("tier_messages"):
        out.append("**Tiers:** " + "; ".join(f"{k}: {_flat(v)}" for k, v in e["tier_messages"].items()))
    return "\n\n".join(out)


def register_markdown(reg, w, handling) -> str:
    """The register as Markdown. handling is the effective handling (effective_handling); w is unused beyond that
    but kept so a later section can cite the workspace."""
    entries = reg["entries"] if isinstance(reg, dict) else reg
    title = reg.get("title", "Learnings Register") if isinstance(reg, dict) else "Learnings Register"
    recs = [dict(r, lr_id=e.get("lr_id")) for e in entries for r in (e.get("recommendations") or [])
            if isinstance(r, dict)]
    out = [f"# {title}"] + ([f"**{DRAFT_LABEL}**"] if is_draft(handling) else [])
    out += handling_lines(handling) + [f"*{status_line(reg.get('status', '') if isinstance(reg, dict) else '')}*"]
    groups, strong = summary_groups(entries, recs)
    out.append("## Summary")
    out.append(f"{len(entries)} learning(s) and {len(recs)} recommendation(s); {strong} of {len(recs)} "
               f"recommendation(s) above the administrative tier.")
    for lab, cnt in groups:
        out.append(f"**{lab}**\n\n" + _table(["Value", "Count"], [[k, v] for k, v in sorted(cnt.items(), key=lambda kv: str(kv[0]))]))
    flagged = sum(1 for e in entries if _flat(e.get("regulatory_touchpoint")))
    if flagged:
        out.append(f"{flagged} learning(s) flagged for legal or compliance review.")
    p1 = [e for e in entries if _flat(e.get("priority")) == "1"]
    out.append("## Priority 1 learnings")
    out += [_full(e) for e in p1] or ["None."]
    out.append("## All learnings")
    out.append(_table(["LR-ID", "Title", "Priority", "HFACS level", "Owner entity", "Tiers"],
                      [[e.get("lr_id"), e.get("title"), e.get("priority"), e.get("hfacs_level"),
                        e.get("owner_entity"), e.get("tiers")] for e in entries]))
    out += ["---", f"> {BRAND}"]
    return "\n\n".join(out) + "\n"


def cmd_register_md(a):
    reg = json.loads(Path(a.register).read_text(encoding="utf-8"))
    refuse_pack_as_register(reg, a.register)
    w = load_ws(a.ws)
    eh = effective_handling(reg if isinstance(reg, dict) else {}, w, src=a.register, ws=a.ws)
    out = Path(a.out) if a.out else outputs_dir(a.ws) / "learnings-register.md"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(register_markdown(reg, w, eh), encoding="utf-8")
    print(f"Register markdown written to {out}")
