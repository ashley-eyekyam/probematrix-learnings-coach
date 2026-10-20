"""Learning packs: coverage and the Markdown renderer."""
from __future__ import annotations

import datetime as dt

from .. import BRAND, DRAFT_LABEL
from ..analysis.timeline import months_between
from ..handling import effective_handling, handling_lines, is_draft, SHARED_LINE, status_line
from ..pack.schema import _text, cited_ids, relevant_findings
from ..register.check import norm_hoc
from ..workspace import downgraded_findings, incident_date
from .. import privacy


# ----------------------------------------------------------------------------- coverage and Markdown

GAPS_HEADING = "## Gaps in the evidence"
LIMITS_HEADING = "## Limits of this pack"

def coverage(w, pack) -> dict:
    """How many of the pack's relevant findings it cites, which it leaves out, and which it excludes on purpose."""
    fids = set(cited_ids(pack)[0])
    F = {f["id"]: f for f in w["findings"]}
    reasons = {e["id"]: e.get("reason", "") for e in (pack.get("exclusions") or [])
               if isinstance(e, dict) and e.get("id") in F}
    rel = [x for x in relevant_findings(w, pack.get("scope")) if x not in reasons]
    downs = downgraded_findings(w)
    unc = [{"id": x, "label": F[x].get("label", ""), "rating": F[x].get("rating"), "level": F[x].get("level"),
            "reason": "reviewer downgrade vote" if x in downs else "not cited in this pack"} for x in rel if x not in fids]
    excl = [{"id": x, "label": F[x].get("label", ""), "reason": r} for x, r in reasons.items()]
    return {"relevant": len(rel), "cited": len(rel) - len(unc), "uncovered": unc, "excluded": excl}


def _knowable(v) -> str:
    """How a timeline event's knowable_then reads: text as written, or yes / no for a bool."""
    return ("yes" if v else "no") if isinstance(v, bool) else str(v)


def sorted_events(events) -> list:
    """By date, then time; events with the same date and no time keep the author's order (sorted is stable)."""
    return sorted(events, key=lambda e: (e["date"], e.get("time") or ""))


def event_when(ev: dict, incident_date: str | None) -> str:
    """How a timeline event's date reads: 'c. 2015' (year only), '2019-03', '2019-03-04 14:05'. A date before the incident
    adds ' (N months before)', or ' (about N years before)' for a year-only date."""
    d = ev["date"]
    when = f"c. {d}" if len(d) == 4 else d + (f" {ev['time']}" if ev.get("time") else "")
    if incident_date:
        try:
            y, m, day = (list(map(int, d.split("-"))) + [1, 1])[:3]
            if len(d) == 4:
                n, unit = int(incident_date[:4]) - y, "years"
            else:
                n, unit = months_between(dt.date(y, m, day), dt.date.fromisoformat(incident_date)), "months"
        except ValueError:
            return when
        if n > 0:
            when += f" (about {n} {'year' if n == 1 else 'years'} before)" if unit == "years" else f" ({n} months before)"
    return when


def _pack_incident_date(pack, w):
    return (pack.get("incident") or {}).get("date") or incident_date(w)


def _c(cites):
    return f" [{'; '.join(cites)}]" if cites else ""


def _numbered(xs):
    return "\n".join(f"{i}. {x}" for i, x in enumerate(xs, 1))


def _lines(pairs):
    return "\n".join(f"- {k}: {v}" for k, v in pairs if v)


def _md_cell(v):
    return str(v).replace("|", "\\|").replace("\n", " ")


def _cites_cell(cites, sup) -> str:
    """The Markdown Cites cell of one table row: key IDs, then '+N supporting'."""
    s = "; ".join(cites)
    if not sup:
        return s
    more = f"+{len(sup)} supporting"
    return f"{s} ({more})" if s else more


def _md_item(it, inc_date=None) -> str:
    k, c, g = it["kind"], _c(it.get("cites")), it.get
    if k == "para":
        return it["text"] + c
    if k == "check":
        hold = "**Hold point:** " if g("hold_point") else ""
        when = f" *({it['when']})*" if g("when") else ""
        return f"- [ ] {hold}{it['text']}{when}{c}"
    if k == "question":
        return (f"**Q: {it['question']}**{c}\n"
                + _lines([("Why it matters", it["why"]), ("Answer", g("answer")),
                          ("Good evidence looks like", g("good_evidence")), ("Put to", g("to"))]))
    if k == "recommendation":
        return (f"**Recommendation:** {it['change']}{c}\n"
                + _lines([("Control tier", norm_hoc(it["hoc_tier"])), ("Barrier", g("barrier")),
                          ("Barrier ID", g("barrier_id")), ("Owner", g("owner")),
                          ("By when", g("by_when")), ("Leading indicator", it["indicator"]),
                          ("Why not stronger", g("why_not_stronger"))]))
    if k == "decision":
        return (f"**Decision:** {it['decision']}{c}\n"
                + _lines([("Options", "; ".join(g("options") or [])), ("Trade-offs", g("trade_offs")),
                          ("Owner", g("owner")), ("By when", g("by_when"))]))
    if k == "indicator":
        return (f"**Indicator:** {it['name']}{c}\n"
                + _lines([("Measure", it["measure"]), ("Deterioration looks like", g("deterioration")), ("Owner", g("owner"))]))
    if k == "card":
        parts = [f"### {it['title']}{c}", f"**What happened:** {it['what_happened']}"]
        if g("why_made_sense"):
            parts.append(f"**Why it made sense at the time:** {it['why_made_sense']}")
        if g("organisation_changing"):
            parts.append(f"**What the organisation is changing:** {it['organisation_changing']}")
        parts.append("**Warning signs:**\n" + "\n".join(f"- {x}" for x in it["warning_signs"]))
        parts.append(f"**What good looks like:** {it['good_looks_like']}")
        if g("discussion"):
            parts.append("**Questions for discussion:**\n" + _numbered(it["discussion"]))
        return "\n\n".join(parts)
    if k == "scenario":
        return f"**Scenario:** {it['situation']}{c}\n\n" + _numbered(it["prompts"])
    if k == "table":
        cols, rows = list(it["columns"]), [list(r) for r in it["rows"]]
        rc, rs = g("row_cites"), g("row_supporting_cites")
        if rc or rs:
            cols.append("Cites")
            rows = [r + [_cites_cell(rc[i] if rc else [], rs[i] if rs else [])] for i, r in enumerate(rows)]
        out = ["| " + " | ".join(_md_cell(x) for x in cols) + " |", "|" + "---|" * len(cols)]
        out += ["| " + " | ".join(_md_cell(x) for x in r) + " |" for r in rows]
        md = "\n".join(out) + (f"\n\nSources:{c}" if c else "")
        if g("finding_notes"):
            md += "\n\nNotes per finding:\n" + "\n".join(f"- {x}: {v}" for x, v in it["finding_notes"].items())
        return md
    if k == "test_point":
        return (f"**Test point:** {it['requirement']}{c}\n"
                + _lines([("Clause", g("clause")), ("What to sample", it["sample"]),
                          ("Evidence of conformity", it["conformity_evidence"]),
                          ("Red flags", "; ".join(g("red_flags") or []))]))
    if k == "module":
        out = (f"### Module: {it['title']}{c}\n\n"
               + _lines([("Objective", it["objective"]), ("Audience", g("audience")), ("Duration", g("duration"))])
               + "\n\n**Content:**\n" + _numbered(it["content"]))
        return out + ("\n\n**Assessment:**\n" + _numbered(it["assessment"]) if g("assessment") else "")
    if k == "barrier":
        return (f"**Barrier:** {it['barrier']}{c}\n"
                + _lines([("Failure mode", it["failure_mode"]), ("Barrier ID", g("barrier_id")), ("Type", g("type")),
                          ("State on the day", g("state")),
                          ("Owner", g("owner")), ("Control tier", norm_hoc(it["hoc_tier"])), ("Fix", g("fix")),
                          ("Leading indicator", g("indicator"))]))
    if k == "timeline":
        lines = []
        for e in sorted_events(it["events"]):
            when = event_when(e, inc_date)
            lines.append(f"- {when}: {e['text']}{' *(weak signal)*' if e.get('signal') else ''}{_c(e.get('cites'))}")
            lines += [f"  - {lab}: {e[f]}" for f, lab in (("received_by", "Received by"), ("response", "Response"))
                      if e.get(f)]
            if "knowable_then" in e:
                lines.append(f"  - Knowable then: {_knowable(e['knowable_then'])}")
        return (f"Sources:{c}\n\n" if c else "") + "\n".join(lines)
    if k == "graph":
        lab = {n["id"]: n["label"] for n in it["nodes"]}
        lines = [f"- {lab[e['from']]} → {lab[e['to']]}" + (f" ({e['label']})" if e.get("label") else "") for e in it["edges"]]
        return f"Graph: {len(it['nodes'])} nodes, {len(it['edges'])} links{c}\n\n" + "\n".join(lines)
    if k == "learning":
        out = f"**Learning:** {it['lesson']}{c}"
        if g("explanation"):
            out += f"\n\n{it['explanation']}"
        return out + (f"\n\n- Owner: {it['owner']}" if g("owner") else "")
    raise ValueError(f"unknown kind {k!r}")


def lint_ok_notes(d) -> list:
    """'Language check JCn accepted: <reason>' for each well-formed lint_ok on an item or bottom-line entry (the
    spec renders the reason on the page). A malformed one is a check-pack problem, so it is not shown."""
    ok = d.get("lint_ok") if isinstance(d, dict) else None
    out = []
    for x in ok if isinstance(ok, list) else [ok]:
        if isinstance(x, dict) and _text(x.get("rule")) and _text(x.get("reason")):
            out.append(f"Language check {x['rule']} accepted: {x['reason'].strip()}")
    return out


def _md_lint_ok(d, sep) -> str:
    return "".join(f"{sep}*{n}*" for n in lint_ok_notes(d))


def _md_extras(d) -> str:
    bits = ([f"evidence: {d['evidence_strength']}"] if d.get("evidence_strength") else []) + \
           ([f"+{len(d['supporting_cites'])} supporting"] if d.get("supporting_cites") else []) + \
           ([f"learning: {d['learning']}"] if d.get("learning") else []) + \
           ([f"Clauses: {', '.join(d['clauses'])}"] if d.get("clauses") else [])
    return f"*({'; '.join(bits)})*" if bits else ""


def _md_block(it, inc_date=None) -> str:
    x = _md_extras(it)
    out = _md_item(it, inc_date)
    if x:
        out += " " + x if it["kind"] in ("para", "check") else "\n\n" + x
    return out + _md_lint_ok(it, "\n  " if it["kind"] == "check" else "\n\n")


def _handling_lines(eh, share):
    """The handling lines, masked for a shared copy, then the 'Shared <mode>' line."""
    if not share:
        return handling_lines(eh)
    return [privacy.share_text(x, share) for x in handling_lines(eh)] + [SHARED_LINE.format(mode=share.mode)]


def render_pack_md(pack, w, eh=None, share=None) -> str:
    """The pack as Markdown: generated, never hand-written, so it always agrees with the HTML. eh is the effective
    handling when the caller computed it on the unmasked pack; share is the ShareCtx of a shared copy (pack and w
    are then already masked)."""
    inc_date = _pack_incident_date(pack, w)
    eh = eh or effective_handling(pack, w)
    cov = coverage(w, pack)
    out = [f"# {pack['title']}"] + ([f"**{DRAFT_LABEL}**"] if is_draft(eh) else [])
    out += _handling_lines(eh, share) + [f"*{status_line(pack['status'])}*", f"**Audience:** {pack['audience']}"]
    fields, inc = w.get("incident", {}).get("fields", {}), pack.get("incident") or {}
    shown = [str(x) for x in (inc.get("title") or fields.get("Incident Title"), inc.get("date") or fields.get("Date")) if x]
    if shown:
        out.append("**Incident:** " + " · ".join(shown))
    if pack.get("data_quality"):
        out += ["## Data quality and limits",
                "\n".join(f"- {n['text']}{_c(n.get('cites'))}" for n in pack["data_quality"])]
    out += ["## Bottom line",
           "\n".join(f"- {b['text']}{_c(b.get('cites'))}" + (" " + _md_extras(b) if _md_extras(b) else "")
                     + _md_lint_ok(b, "\n  ") for b in pack["bottom_line"])]
    for s in pack["sections"]:
        out.append(f"## {s['heading']}")
        if s.get("intro"):
            out.append(s["intro"])
        prev, tick = None, False
        for it in s["items"]:
            g = it.get("group")
            head = bool(g and g != prev)
            if head:
                out.append(f"### {g}")
            prev = g
            if tick and it["kind"] == "check" and not head:       # consecutive checks: one tight list
                out[-1] += "\n" + _md_block(it, inc_date)
            else:
                out.append(_md_block(it, inc_date))
            tick = it["kind"] == "check"
    sup = [f"- Bottom line › {i}: {'; '.join(b['supporting_cites'])}"
           for i, b in enumerate(pack["bottom_line"], 1) if b.get("supporting_cites")]
    sup += [f"- {s['heading']} › {n}: {'; '.join(it['supporting_cites'])}"
            for s in pack["sections"] for n, it in enumerate(s["items"], 1) if it.get("supporting_cites")]
    sup += [f"- {s['heading']} › {n}, row {r}: {'; '.join(x)}"
            for s in pack["sections"] for n, it in enumerate(s["items"], 1)
            for r, x in enumerate(it.get("row_supporting_cites") or [], 1) if x]
    if pack.get("gaps"):
        out += [GAPS_HEADING, "\n".join(f"- {x['text']}{_c(x.get('cites'))}\n  - Evidence needed: {x['evidence_needed']}"
                                        for x in pack["gaps"])]
    if pack.get("limits"):
        out += [LIMITS_HEADING, "\n".join(f"- {x}" for x in pack["limits"])]
    if sup:
        out += ["## Supporting citations", "\n".join(sup)]
    tail = ["---", f"This pack cites {cov['cited']} of {cov['relevant']} relevant findings."]
    if cov["excluded"]:
        tail.append("Left out on purpose:\n" + "\n".join(f"- {e['id']}: {e['reason']}" for e in cov["excluded"]))
    out += tail + [f"> {BRAND}"]
    return "\n\n".join(out) + "\n"
