"""Learning packs: coverage and the Markdown renderer."""
from __future__ import annotations

import datetime as dt

from .. import BRAND, DRAFT_LABEL
from ..analysis.timeline import months_between
from ..handling import effective_handling, handling_lines, is_draft, md_escape, SHARED_LINE, status_line
from ..pack.schema import _text, cited_ids, LENSES, relevant_findings, TOP_PRINT_LINE, top_rated_of
from ..register.check import norm_hoc
from ..workspace import downgraded_findings, incident_date
from .. import privacy


# ----------------------------------------------------------------------------- coverage and Markdown

GAPS_HEADING = "## Gaps in the evidence"      # the English headings; a page takes ui.gaps and ui.limits
LIMITS_HEADING = "## Limits of this pack"


def _pm_labels(labels=None, pack=None) -> dict:
    """labels as given, else the labels of the pack's lang (English without a pack). Imported late: render/ imports
    this module (Ruling P4-15)."""
    if labels is not None:
        return labels
    from ..render.labels import load_labels
    return load_labels((pack or {}).get("lang") or "en")


def _pm_t(L, key, **fmt) -> str:
    from ..render.labels import label
    return label(_pm_labels(L), key, **fmt)


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
    top = top_rated_of(w, rel)
    return {"relevant": len(rel), "cited": len(rel) - len(unc), "uncovered": unc, "excluded": excl,
            "top_relevant": len(top), "top_cited": sum(1 for x in top if x in fids)}


def _knowable(v, labels=None) -> str:
    """How a timeline event's knowable_then reads: text as written, or yes / no for a bool."""
    return _pm_t(labels, "ui.yes" if v else "ui.no") if isinstance(v, bool) else str(v)


def sorted_events(events) -> list:
    """By date, then time; events with the same date and no time keep the author's order (sorted is stable)."""
    return sorted(events, key=lambda e: (e["date"], e.get("time") or ""))


def event_when(ev: dict, incident_date: str | None, labels=None) -> str:
    """How a timeline event's date reads: 'c. 2015' (year only), '2019-03', '2019-03-04 14:05'. A date before the incident
    adds ' (N months before)', or ' (about N years before)' for a year-only date. labels: the page's (English)."""
    L = _pm_labels(labels)
    d = ev["date"]
    when = _pm_t(L, "ui.circa", year=d) if len(d) == 4 else d + (f" {ev['time']}" if ev.get("time") else "")
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
            key = ("ui.about_year_before" if n == 1 else "ui.about_years_before") if unit == "years" else "ui.months_before"
            when += f" ({_pm_t(L, key, n=n)})"
    return when


def _pack_incident_date(pack, w):
    return (pack.get("incident") or {}).get("date") or incident_date(w)


def _c(cites):
    return f" [{'; '.join(cites)}]" if cites else ""


def _numbered(xs):
    return "\n".join(f"{i}. {x}" for i, x in enumerate(xs, 1))


def _typed_options_md(it, f, t) -> str:
    """A typed question's options as a list, the correct ones marked when the key is present (P4-10)."""
    ops = it.get("options")
    if not it.get("type") or not isinstance(ops, list) or not all(isinstance(o, dict) for o in ops):
        return ""
    short = it["type"] == "short"
    rows = [f"  - {o['text']}" + (f" **({t('ui.quiz.correct')})**" if o.get("correct") and not short else "") for o in ops]
    return f"- {t('ui.quiz.accepted') if short else f('options')}:\n" + "\n".join(rows) + "\n"


def _lines(pairs):
    return "\n".join(f"- {k}: {v}" for k, v in pairs if v)


def _md_cell(v):
    return str(v).replace("|", "\\|").replace("\n", " ")


def _cites_cell(cites, sup, labels=None) -> str:
    """The Markdown Cites cell of one table row: key IDs, then '+N supporting'."""
    s = "; ".join(cites)
    if not sup:
        return s
    more = _pm_t(labels, "ui.supporting", n=len(sup))
    return f"{s} ({more})" if s else more


def _md_item(it, inc_date=None, labels=None) -> str:
    L = _pm_labels(labels)
    k, c, g = it["kind"], _c(it.get("cites")), it.get

    def t(key, **fmt):
        return _pm_t(L, key, **fmt)

    def f(name):
        return t("f." + name)

    if k == "para":
        return it["text"] + c
    if k == "check":
        hold = f"**{f('hold_point')}:** " if g("hold_point") else ""
        when = f" *({it['when']})*" if g("when") else ""
        return f"- [ ] {hold}{it['text']}{when}{c}"
    if k == "question":
        return (f"**{t('ui.q')}: {it['question']}**{c}\n" + _typed_options_md(it, f, t)
                + _lines([(f("why"), it["why"]), (f("answer"), g("answer")),
                          (f("good_evidence"), g("good_evidence")), (f("to"), g("to"))]))
    if k == "recommendation":
        return (f"**{t('k.recommendation')}:** {it['change']}{c}\n"
                + _lines([(f("hoc_tier"), norm_hoc(it["hoc_tier"])), (f("barrier"), g("barrier")),
                          (f("barrier_id"), g("barrier_id")), (f("owner"), g("owner")),
                          (f("co_owner"), g("co_owner")), (f("by_when"), g("by_when")), (f("indicator"), it["indicator"]),
                          (f("why_not_stronger"), g("why_not_stronger"))]))
    if k == "decision":
        return (f"**{t('k.decision')}:** {it['decision']}{c}\n"
                + _lines([(f("options"), "; ".join(g("options") or [])), (f("trade_offs"), g("trade_offs")),
                          (f("owner"), g("owner")), (f("by_when"), g("by_when"))]))
    if k == "indicator":
        return (f"**{t('k.indicator')}:** {it['name']}{c}\n"
                + _lines([(f("measure"), it["measure"]), (f("deterioration"), g("deterioration")), (f("owner"), g("owner"))]))
    if k == "card":
        parts = [f"### {it['title']}{c}", f"**{f('what_happened')}:** {it['what_happened']}"]
        if g("why_made_sense"):
            parts.append(f"**{f('why_made_sense')}:** {it['why_made_sense']}")
        if g("organisation_changing"):
            parts.append(f"**{f('organisation_changing')}:** {it['organisation_changing']}")
        parts.append(f"**{f('warning_signs')}:**\n" + "\n".join(f"- {x}" for x in it["warning_signs"]))
        parts.append(f"**{f('good_looks_like')}:** {it['good_looks_like']}")
        parts += [f"**{f(x)}**\n" + "\n".join(f"- {y}" for y in it[x]) for x in ("did_you_know", "what_you_can_do")
                  if g(x)]                                     # the labels end in "?" (R3)
        if g("discussion"):
            parts.append(f"**{f('discussion')}:**\n" + _numbered(it["discussion"]))
        return "\n\n".join(parts)
    if k == "scenario":
        return f"**{t('k.scenario')}:** {it['situation']}{c}\n\n" + _numbered(it["prompts"]) + _pm_injects(g("injects"), L)
    if k == "table":
        cols, rows = list(it["columns"]), [list(r) for r in it["rows"]]
        rc, rs = g("row_cites"), g("row_supporting_cites")
        if rc or rs:
            cols.append(f("cites"))
            rows = [r + [_cites_cell(rc[i] if rc else [], rs[i] if rs else [], L)] for i, r in enumerate(rows)]
        out = ["| " + " | ".join(_md_cell(x) for x in cols) + " |", "|" + "---|" * len(cols)]
        out += ["| " + " | ".join(_md_cell(x) for x in r) + " |" for r in rows]
        md = "\n".join(out) + (f"\n\n{t('ui.sources')}:{c}" if c else "")
        if g("finding_notes"):
            md += f"\n\n{f('finding_notes')}:\n" + "\n".join(f"- {x}: {v}" for x, v in it["finding_notes"].items())
        return md
    if k == "test_point":
        return (f"**{t('k.test_point')}:** {it['requirement']}{c}\n"
                + _lines([(f("clause"), g("clause")), (f("sample"), it["sample"]),
                          (f("conformity_evidence"), it["conformity_evidence"]),
                          (t("ui.red_flags"), "; ".join(g("red_flags") or []))]))
    if k == "module":
        out = (f"### {t('ui.module_title', title=it['title'])}{c}\n\n"
               + _lines([(f("objective"), it["objective"]), (f("audience"), g("audience")), (f("duration"), g("duration"))])
               + f"\n\n**{f('content')}:**\n" + _numbered(it["content"]))
        return out + (f"\n\n**{f('assessment')}:**\n" + _numbered(it["assessment"]) if g("assessment") else "")
    if k == "barrier":
        return (f"**{t('k.barrier')}:** {it['barrier']}{c}\n"
                + _lines([(f("failure_mode"), it["failure_mode"]), (f("barrier_id"), g("barrier_id")), (f("type"), g("type")),
                          (f("state"), g("state")),
                          (f("owner"), g("owner")), (f("hoc_tier"), norm_hoc(it["hoc_tier"])), (f("fix"), g("fix")),
                          (f("indicator"), g("indicator"))]))
    if k == "timeline":
        lines = []
        for e in sorted_events(it["events"]):
            when = event_when(e, inc_date, L)
            weak = f" *({t('ui.weak_signal_md')})*" if e.get("signal") else ""
            lines.append(f"- {when}: {e['text']}{weak}{_c(e.get('cites'))}")
            lines += [f"  - {t(lab)}: {e[fl]}" for fl, lab in (("received_by", "ui.received_by"), ("response", "ui.response"))
                      if e.get(fl)]
            if "knowable_then" in e:
                lines.append(f"  - {t('ui.knowable_then')}: {_knowable(e['knowable_then'], L)}")
        return (f"{t('ui.sources')}:{c}\n\n" if c else "") + "\n".join(lines)
    if k == "graph":
        lab = {n["id"]: n["label"] for n in it["nodes"]}
        lines = [f"- {lab[e['from']]} → {lab[e['to']]}" + (f" ({e['label']})" if e.get("label") else "") for e in it["edges"]]
        return t("ui.graph_summary", nodes=len(it["nodes"]), links=len(it["edges"])) + f"{c}\n\n" + "\n".join(lines)
    if k == "learning":
        out = f"**{t('k.learning')}:** {it['lesson']}{c}"
        if g("explanation"):
            out += f"\n\n{it['explanation']}"
        return out + (f"\n\n- {f('owner')}: {it['owner']}" if g("owner") else "")
    if k == "toolbox":
        return _pm_toolbox(it, c, L)
    if k == "script":
        return _pm_script(it, c, L)
    return _md_fields(it, L) + c


def _pm_clock(seconds) -> str:
    """Seconds as m:ss (75 -> 1:15), for a script's segment times and total duration."""
    return f"{seconds // 60}:{seconds % 60:02d}"


def _pm_injects(injects, L) -> str:
    """A scenario's injects (L4-30) as a numbered list after its prompts: **+HH:MM** text, then its decision point."""
    if not injects:
        return ""
    out = []
    for n, x in enumerate(injects, 1):
        out.append(f"{n}. **{x['offset']}** {x['text']}")
        if x.get("decision"):
            out.append(f"   - **{_pm_t(L, 'ui.decision_point')}:** {x['decision']}")
    return f"\n\n**{_pm_t(L, 'f.injects')}:**\n" + "\n".join(out)


def _pm_toolbox(it, c, L) -> str:
    """A toolbox talk (L2-18) in the five parts of output-style.md, numbered in order."""
    def f(name):
        return _pm_t(L, "f." + name)

    head = f"### {_pm_t(L, 'k.toolbox')}{c}" + (f"\n\n*{f('duration')}: {it['duration']}*" if it.get("duration") else "")
    signs = "\n".join(f"   - {x}" for x in it["warning_signs"])
    return head + "\n\n" + "\n".join([
        f"1. **{f('opening_question')}:** {it['opening_question']}", f"2. **{f('story')}:** {it['story']}",
        f"3. **{f('warning_signs')}:**\n{signs}", f"4. **{f('one_change')}:** {it['one_change']}",
        f"5. **{f('crew_question')}:** {it['crew_question']}"])


def _pm_script(it, c, L) -> str:
    """A shooting script (L4-19): the two-column Visual | Narration table, each visual led by its time, then the
    total duration. The SRT and narration files (render/script.py) carry the narration alone."""
    def f(name):
        return _pm_t(L, "f." + name)

    rows, t0 = [], 0
    for sg in it["segments"]:
        t1 = t0 + sg["seconds"]
        vis = f"{_pm_clock(t0)}–{_pm_clock(t1)} · {sg['visual']}" + (
            f" ({f('on_screen')}: {sg['on_screen']})" if sg.get("on_screen") else "")
        rows.append(f"| {_md_cell(vis)} | {_md_cell(sg['narration'] + _c(sg.get('cites')))} |")
        t0 = t1
    out = f"**{_pm_t(L, 'k.script')}:** {it['title']}{c}"
    meta = _lines([(f("channel"), it.get("channel")), (f("purpose"), it.get("purpose"))])
    table = "\n".join([f"| {f('visual')} | {f('narration')} |", "|---|---|", *rows])
    return out + (f"\n{meta}" if meta else "") + f"\n\n{table}\n\n{_pm_t(L, 'ui.total_duration', time=_pm_clock(t0))}"


def _md_fields(it, labels=None) -> str:
    """A kind this renderer has no layout for: **Label:** value lines, in KINDS field order (P4-5)."""
    from ..render.fields import item_blocks
    out = []
    for b in item_blocks(it, _pm_labels(labels)):
        v = b.value
        if isinstance(v, list):
            out.append(f"**{b.label}:**\n" + "\n".join(f"- {' | '.join(map(str, x)) if isinstance(x, list) else x}"
                                                       for x in v))
        elif isinstance(v, dict):
            out.append(f"**{b.label}:**\n" + "\n".join(f"- {k}: {x}" for k, x in v.items()))
        else:
            out.append(f"**{b.label}:** {v}")
    return "\n".join(out)


def lint_ok_notes(d, labels=None) -> list:
    """'Language check JCn accepted: <reason>' for each well-formed lint_ok on an item or bottom-line entry (the
    spec renders the reason on the page). A malformed one is a check-pack problem, so it is not shown."""
    ok = d.get("lint_ok") if isinstance(d, dict) else None
    out = []
    for x in ok if isinstance(ok, list) else [ok]:
        if isinstance(x, dict) and _text(x.get("rule")) and _text(x.get("reason")):
            out.append(_pm_t(labels, "ui.lint_ok", rule=x["rule"], reason=x["reason"].strip()))
    return out


def _md_lint_ok(d, sep, labels=None) -> str:
    return "".join(f"{sep}*{md_escape(n)}*" for n in lint_ok_notes(d, labels))


def _md_extras(d, labels=None) -> str:
    L = _pm_labels(labels)
    bits = ([_pm_t(L, "ui.evidence_md", strength=d["evidence_strength"])] if d.get("evidence_strength") else []) + \
           ([_pm_t(L, "ui.supporting", n=len(d["supporting_cites"]))] if d.get("supporting_cites") else []) + \
           ([_pm_t(L, "ui.learning_md", id=d["learning"])] if d.get("learning") else []) + \
           ([f"{_pm_t(L, 'f.clauses')}: {', '.join(d['clauses'])}"] if d.get("clauses") else [])
    return f"*({'; '.join(bits)})*" if bits else ""


def _md_block(it, inc_date=None, labels=None) -> str:
    L = _pm_labels(labels)
    x = _md_extras(it, L)
    out = _md_item(it, inc_date, L)
    if x:
        out += " " + x if it["kind"] in ("para", "check") else "\n\n" + x
    return out + _md_lint_ok(it, "\n  " if it["kind"] == "check" else "\n\n", L)


def _handling_lines(eh, share, markdown=True):
    """The handling lines, masked for a shared copy, then the 'Shared <mode>' line. markdown=False for the HTML pack,
    which escapes the lines itself."""
    lines = handling_lines(eh, markdown=markdown)
    if not share:
        return lines
    return [privacy.share_text(x, share) for x in lines] + [SHARED_LINE.format(mode=share.mode)]


def render_pack_md(pack, w, eh=None, share=None, labels=None) -> str:
    """The pack as Markdown: generated, never hand-written, so it always agrees with the HTML. eh is the effective
    handling when the caller computed it on the unmasked pack; share is the ShareCtx of a shared copy (pack and w
    are then already masked). labels: the page labels, else those of the pack's lang (P4-15)."""
    from ..render.fields import reading_minutes
    L = _pm_labels(labels, pack)

    def t(key, **fmt):
        return _pm_t(L, key, **fmt)

    inc_date = _pack_incident_date(pack, w)
    eh = eh or effective_handling(pack, w)
    cov = coverage(w, pack)
    out = [f"# {pack['title']}"] + ([f"**{DRAFT_LABEL}**"] if is_draft(eh) else [])
    from ..render import translation_lines                     # late: render imports this module's renderer
    out += _handling_lines(eh, share) + [f"*{status_line(pack['status'])}*"] + [f"*{x}*" for x in translation_lines(pack)]
    out += [f"*{t('ui.reading_time', n=reading_minutes(pack))}*", f"**{t('f.audience')}:** {pack['audience']}"]
    if pack.get("lens") in LENSES:                             # P5-17: who the assurance is for
        out.append(f"**{t('f.lens')}:** {t('ui.lens.' + pack['lens'])}")
    fields, inc = w.get("incident", {}).get("fields", {}), pack.get("incident") or {}
    shown = [str(x) for x in (inc.get("title") or fields.get("Incident Title"), inc.get("date") or fields.get("Date")) if x]
    if shown:
        out.append(f"**{t('ui.incident')}:** " + " · ".join(shown))
    if pack.get("data_quality"):
        out += [f"## {t('ui.data_quality')}",
                "\n".join(f"- {n['text']}{_c(n.get('cites'))}" for n in pack["data_quality"])]
    out += [f"## {t('ui.bottom_line')}",
           "\n".join(f"- {b['text']}{_c(b.get('cites'))}" + (" " + _md_extras(b, L) if _md_extras(b, L) else "")
                     + _md_lint_ok(b, "\n  ", L) for b in pack["bottom_line"])]
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
                out[-1] += "\n" + _md_block(it, inc_date, L)
            else:
                out.append(_md_block(it, inc_date, L))
            tick = it["kind"] == "check"
    sup = [f"- {t('ui.bottom_line')} › {i}: {'; '.join(b['supporting_cites'])}"
           for i, b in enumerate(pack["bottom_line"], 1) if b.get("supporting_cites")]
    sup += [f"- {s['heading']} › {n}: {'; '.join(it['supporting_cites'])}"
            for s in pack["sections"] for n, it in enumerate(s["items"], 1) if it.get("supporting_cites")]
    sup += [f"- {s['heading']} › {n}, {t('ui.row', r=r)}: {'; '.join(x)}"
            for s in pack["sections"] for n, it in enumerate(s["items"], 1)
            for r, x in enumerate(it.get("row_supporting_cites") or [], 1) if x]
    if pack.get("gaps"):
        out += [f"## {t('ui.gaps')}",
                "\n".join(f"- {x['text']}{_c(x.get('cites'))}\n  - {t('ui.evidence_needed')}: {x['evidence_needed']}"
                          for x in pack["gaps"])]
    if pack.get("limits"):
        out += [f"## {t('ui.limits')}", "\n".join(f"- {x}" for x in pack["limits"])]
    if sup:
        out += [f"## {t('f.supporting_cites')}", "\n".join(sup)]
    tail = ["---", f"This pack cites {cov['cited']} of {cov['relevant']} relevant findings.",
            TOP_PRINT_LINE.format(x=cov["top_cited"], y=cov["top_relevant"]) + "."]
    if cov["excluded"]:
        tail.append(f"{t('ui.left_out')}:\n" + "\n".join(f"- {e['id']}: {e['reason']}" for e in cov["excluded"]))
    out += tail + [f"> {BRAND}"]
    return "\n\n".join(out) + "\n"
