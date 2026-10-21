"""The register-render command (L4-27, L4-03): the Learnings Register as a Word document and an email digest. The
sections follow register-md; the docx is built by render.docx.write_docx and the email by render.email.render_email
from a pack-shaped view of the register, so the status, handling, DRAFT and footer rules are those of the packs. md
and xlsx stay with register-md and register-xlsx."""
from __future__ import annotations

import json
import sys
from pathlib import Path

from .. import BRAND, DRAFT_LABEL
from ..handling import (
    effective_handling, is_draft, name_guard, share_ctx, share_gate, shared_copy, shared_name, SHARED_LINE,
    SHARED_SOURCE, status_line
)
from ..pack.markdown import _handling_lines as _rr_handling_lines
from ..register.xlsx import refuse_pack_as_register, summary_groups
from ..render import build_date, Output, RenderContext
from ..render.docx import docx_text, write_docx
from ..render.email import render_email
from ..util import _flat
from ..workspace import is_standard_ws, load_ws, outputs_dir

RR_FORMATS = ("docx", "email")
RR_REFUSED = ("md", "xlsx")
RR_USE_OTHER = "use register-md / register-xlsx"
RR_NAME = "learnings-register"
RR_ROWS_PER_TABLE = 8              # the email adds items in order, so the all-learnings table is cut into small ones
RR_META = (("owner_entity", "Owner entity"), ("hfacs_level", "HFACS level"), ("urgency", "Urgency"),
           ("recommendation_class", "Class"), ("recipient_role", "Recipient"),
           ("regulatory_touchpoint", "Regulatory touchpoint"))
RR_REC_COLS = ["What should change", "Control tier", "Leading indicator"]
RR_ALL_COLS = ["LR-ID", "Title", "Priority", "HFACS level", "Owner entity", "Tiers"]


def _rr_recs(entries) -> list:
    return [dict(r, lr_id=e.get("lr_id")) for e in entries for r in (e.get("recommendations") or [])
            if isinstance(r, dict)]


def _rr_cites(e) -> list:
    return [x for x in list(e.get("finding_ids") or []) + list(e.get("evidence_ids") or []) if isinstance(x, str)]


def _rr_summary(entries) -> tuple:
    """(sentence, [(label, [[value, count], ...])], flagged line or "") of the Summary section."""
    recs = _rr_recs(entries)
    groups, strong = summary_groups(entries, recs)
    sentence = (f"{len(entries)} learning(s) and {len(recs)} recommendation(s); {strong} of {len(recs)} "
                f"recommendation(s) above the administrative tier.")
    tables = [(lab, [[k, v] for k, v in sorted(cnt.items(), key=lambda kv: str(kv[0]))]) for lab, cnt in groups]
    flagged = sum(1 for e in entries if _flat(e.get("regulatory_touchpoint")))
    return sentence, tables, (f"{flagged} learning(s) flagged for legal or compliance review." if flagged else "")


def _rr_meta(e) -> str:
    return " · ".join(f"{label}: {_flat(e.get(k))}" for k, label in RR_META if _flat(e.get(k)))


def _rr_rec_rows(e) -> list:
    return [[_flat(r.get("what")), _flat(r.get("hoc_tier")), _flat(r.get("leading_indicator"))]
            for r in (e.get("recommendations") or []) if isinstance(r, dict)]


def _rr_all_rows(entries) -> list:
    return [[_flat(e.get(k)) for k in ("lr_id", "title", "priority", "hfacs_level", "owner_entity", "tiers")]
            for e in entries]


def _rr_full_paras(e) -> list:
    """The labelled paragraphs of one learning, as (label, text) pairs, in register-md's order."""
    out = [(label, _flat(e[k])) for k, label in (("lesson", "Lesson"), ("context", "Context")) if _flat(e.get(k))]
    if _meta := _rr_meta(e):
        out.append(("", _meta))
    return out


def _rr_tail_paras(e) -> list:
    out = []
    if e.get("why_not_stronger"):
        out.append(("Why no stronger fix", _flat(e["why_not_stronger"])))
    out.append(("Findings", _flat(e.get("finding_ids"))))
    out.append(("Evidence", _flat(e.get("evidence_ids"))))
    if e.get("tier_messages"):
        out.append(("Tiers", "; ".join(f"{k}: {_flat(v)}" for k, v in e["tier_messages"].items())))
    return out


def register_blocks(entries, eh, title="Learnings Register", status="", share=None) -> list:
    """The blocks for write_docx, in the order of register-md's sections: title, DRAFT, handling, status, Summary,
    Priority 1 learnings, All learnings, then the brand line. A learning's finding and evidence IDs become its
    endnote."""
    entries = [e for e in entries if isinstance(e, dict)]
    out = [("title", title, None)]
    if is_draft(eh):
        out.append(("para", [(DRAFT_LABEL, "b")], None))
    out += [("status", x, None) for x in _rr_handling_lines(eh, share, markdown=False)]
    out.append(("status", status_line(status), None))
    sentence, tables, flagged = _rr_summary(entries)
    out += [("heading1", "Summary", None), ("para", sentence, None)]
    for lab, rows in tables:
        out += [("para", [(lab, "b")], None), ("table", {"columns": ["Value", "Count"], "rows": rows}, None)]
    if flagged:
        out.append(("para", flagged, None))
    out.append(("heading1", "Priority 1 learnings", None))
    p1 = [e for e in entries if _flat(e.get("priority")) == "1"]
    for e in p1:
        out.append(("heading2", f"{e.get('lr_id', '?')}: {_flat(e.get('title'))}", None))
        for label, text in _rr_full_paras(e):
            out.append(("para", [(f"{label}: ", "b"), (text, "")] if label else text, None))
        rows = _rr_rec_rows(e)
        if rows:
            out.append(("table", {"columns": RR_REC_COLS, "rows": rows}, None))
        tail = _rr_tail_paras(e)
        for n, (label, text) in enumerate(tail):
            out.append(("para", [(f"{label}: ", "b"), (text, "")], _rr_cites(e) if n == len(tail) - 1 else None))
    if not p1:
        out.append(("para", "None.", None))
    out += [("heading1", "All learnings", None),
            ("table", {"columns": RR_ALL_COLS, "rows": _rr_all_rows(entries)}, None),
            ("note", BRAND, None)]
    return out


def _rr_pack(entries, title, status) -> dict:
    """The register as a pack-shaped dict, so the email module assembles it: Summary, Priority 1 learnings (one
    group per learning) and All learnings (small tables)."""
    entries = [e for e in entries if isinstance(e, dict)]
    sentence, tables, flagged = _rr_summary(entries)
    summary = [{"kind": "para", "text": sentence}]
    for lab, rows in tables:
        summary.append({"kind": "table", "title": lab, "columns": [lab, "Count"], "rows": [[str(a), str(b)] for a, b in rows]})
    if flagged:
        summary.append({"kind": "para", "text": flagged})
    p1_items = []
    for e in (e for e in entries if _flat(e.get("priority")) == "1"):
        group = f"{e.get('lr_id', '?')}: {_flat(e.get('title'))}"
        paras = [f"{label}: {text}" if label else text for label, text in _rr_full_paras(e) + _rr_tail_paras(e)]
        p1_items.append({"kind": "para", "text": paras[0], "group": group, "cites": _rr_cites(e)})
        p1_items += [{"kind": "para", "text": t, "group": group} for t in paras[1:]]
        rows = _rr_rec_rows(e)
        if rows:
            p1_items.append({"kind": "table", "columns": RR_REC_COLS, "rows": rows, "group": group})
    if not p1_items:
        p1_items = [{"kind": "para", "text": "None."}]
    rows = _rr_all_rows(entries)
    all_items = [{"kind": "table", "columns": RR_ALL_COLS, "rows": rows[i:i + RR_ROWS_PER_TABLE]}
                 for i in range(0, len(rows), RR_ROWS_PER_TABLE)] or [{"kind": "para", "text": "None."}]
    return {"pack": RR_NAME, "title": title, "status": status, "lang": "en", "bottom_line": [
            {"text": sentence, "cites": []}], "sections": [
            {"heading": "Summary", "items": summary}, {"heading": "Priority 1 learnings", "items": p1_items},
            {"heading": "All learnings", "items": all_items}]}


def render_register(entries, ctx, formats=RR_FORMATS, title="Learnings Register", status="") -> list:
    """The Outputs of the register in each format of `formats` (docx, email)."""
    outs = []
    if "docx" in formats:
        data = write_docx(register_blocks(entries, ctx.eh, title, status, ctx.share), ctx)
        outs.append(("docx", Output(f"{RR_NAME}.docx", data, docx_text(data))))
    if "email" in formats:
        pctx = RenderContext(**{**ctx.__dict__, "pack": _rr_pack(entries, title, status)})
        outs += [("email", o) for o in render_email(pctx)]
        ctx.notes.extend(pctx.notes)
    return outs


def _rr_formats(text) -> list:
    """--format as a list of docx and email; md and xlsx exit 2 with RR_USE_OTHER, a name no format has exits 2 too."""
    names = list(dict.fromkeys(x.strip() for x in str(text or ",".join(RR_FORMATS)).split(",") if x.strip()))
    if any(x in RR_REFUSED for x in names):
        print(RR_USE_OTHER, file=sys.stderr)
        sys.exit(2)
    bad = [x for x in names if x not in RR_FORMATS]
    if bad or not names:
        print(f"unknown format {', '.join(map(repr, bad)) or '(none)'}; choose from: {', '.join(RR_FORMATS)}",
              file=sys.stderr)
        sys.exit(2)
    return names


def cmd_register_render(a):
    formats = _rr_formats(getattr(a, "format", None))
    reg = json.loads(Path(a.register).read_text(encoding="utf-8"))
    refuse_pack_as_register(reg, a.register)
    w = load_ws(a.ws)
    hdoc = reg if isinstance(reg, dict) else {}
    mode = share_gate(hdoc, w, a, embeds=False, src=a.register, ws=a.ws)
    eh = effective_handling(hdoc, w, src=a.register, ws=a.ws)
    share = share_ctx(a, w, mode) if mode != "internal" else None
    rw = w
    if share:
        rw, reg = shared_copy(w, share, w), shared_copy(reg, share, w)
        if isinstance(reg, dict) and reg.get("source"):
            reg["source"] = SHARED_SOURCE
    hdoc = reg if isinstance(reg, dict) else {}
    entries = reg["entries"] if isinstance(reg, dict) else reg
    ws = Path(a.ws).resolve()
    ctx = RenderContext(w=rw, pack={"pack": RR_NAME, "title": hdoc.get("title", "Learnings Register"), "lang": "en"},
                        run=ws.parent.name if is_standard_ws(ws) else ws.name, generated=build_date(),
                        embed="summary", eh=eh, share=share)
    outs = render_register(entries, ctx, formats, hdoc.get("title", "Learnings Register"), hdoc.get("status", ""))
    name_guard([o.guard_text or "" for _, o in outs], a)
    for note in ctx.notes:
        print(note, file=sys.stderr)
    out = Path(a.out) if a.out else outputs_dir(a.ws)
    out.mkdir(parents=True, exist_ok=True)
    for fmt, o in outs:
        path = shared_name(out / o.name, mode)
        path.write_bytes(o.data) if isinstance(o.data, bytes) else path.write_text(o.data, encoding="utf-8")
        print(f"{fmt} written to {path}")
    if mode != "internal":
        print(SHARED_LINE.format(mode=mode))
