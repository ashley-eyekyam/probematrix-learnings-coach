"""Learning packs: the HTML renderer (the pack command is in pack/command.py)."""
from __future__ import annotations

import html
import json
import re

from .. import BRAND, brand_payload, STATUS_PHRASE
from ..dashboard.data import (
    DASHBOARD_ASSETS, EMBED_DEFAULT, embed_json, embedded_records
)
from ..dashboard.render import PAGE_TOKENS_CSS, WIDE_CSS
from ..handling import (
    effective_handling, HANDLING_CSS, is_draft, public_records, RIBBON_HTML, status_line
)
from ..pack.graph_layout import layout_graph
from ..pack.markdown import (
    _handling_lines, _knowable, _pack_incident_date, _pm_clock, coverage, event_when, lint_ok_notes, sorted_events
)
from ..pack.schema import (
    cited_ids, embedded_ids, excluded_ids, FOLLOW_UP_KEYS, ID_RX, relevant_findings,
    TOP_PRINT_LINE, UNCOVERED_PRINT_LINE, with_item_ids
)
from ..register.check import norm_hoc
from ..util import write_json
from ..workspace import outputs_dir


# ----------------------------------------------------------------------------- HTML

GRID_KINDS = {"card", "indicator", "test_point", "module"}
PFOOT = f'<p class="pfoot">{html.escape(STATUS_PHRASE)}</p>'  # print-only status on each card
STRONG_HOC = {"elimination", "substitution", "engineering"}


def _h(s) -> str:
    return html.escape("" if s is None else str(s), quote=True)


def _chip(x) -> str:
    return f'<button type="button" class="cite" data-id="{_h(x)}" aria-expanded="false">{_h(x)}</button>'


def _chips(cites) -> str:
    return '<span class="cites">' + "".join(_chip(x) for x in cites) + "</span>" if cites else ""


def _inline(s) -> str:
    """Escaped text in which Finding and Evidence IDs become citation buttons."""
    s, out, last = str(s), [], 0
    for m in ID_RX.finditer(s):
        out += [_h(s[last:m.start()]), _chip(m.group(1))]
        last = m.end()
    return "".join(out) + _h(s[last:])


def _rich(text) -> str:
    return "".join(f"<p>{_inline(p)}</p>" for p in re.split(r"\n\s*\n", str(text)) if p.strip())


def _labelled(label, value) -> str:
    return f'<span class="label">{_h(label)}</span><p>{_inline(value)}</p>' if value else ""


def _list(xs, tag="ul") -> str:
    return f"<{tag}>" + "".join(f"<li>{_inline(x)}</li>" for x in xs) + f"</{tag}>" if xs else ""


def _typed_options(it, f, t) -> str:
    """A typed question's options (P4-10): choices with the correct ones marked when the key is present (the learner
    view has none), or the accepted answers of a short question. Options without a type are ignored."""
    ops = it.get("options")
    if not it.get("type") or not isinstance(ops, list) or not all(isinstance(o, dict) for o in ops):
        return ""
    short = it["type"] == "short"
    mark = f' <b>({_h(t("ui.quiz.correct"))})</b>'
    lis = "".join("<li class=\"correct\">" + _inline(o["text"]) + ("" if short else mark) + "</li>" if o.get("correct")
                  else "<li>" + _inline(o["text"]) + "</li>" for o in ops)
    return f'<span class="label">{_h(t("ui.quiz.accepted") if short else f("options"))}</span><ul>{lis}</ul>'


def _badges(pairs) -> str:
    return "".join(f'<span class="badge">{_h(k)}: {_h(v)}</span>' for k, v in pairs if v)


def _ph_labels(labels=None, pack=None) -> dict:
    """labels as given, else the labels of the pack's lang (English without a pack). Imported late: render/ imports
    this module (Ruling P4-15)."""
    if labels is not None:
        return labels
    from ..render.labels import load_labels
    return load_labels((pack or {}).get("lang") or "en")


def _ph_t(L, key, **fmt) -> str:
    from ..render.labels import label
    return label(_ph_labels(L), key, **fmt)


def _hoc(v, labels=None) -> str:
    t = norm_hoc(v)
    cls = "badge strong" if t in STRONG_HOC else "badge"
    return f'<span class="{cls}">{_h(_ph_t(labels, "ui.control", tier=t))}</span>'


def _links(d, labels=None) -> str:
    """The learning chip (a button that searches the pack for its LR id, pack.js) and the clauses badge."""
    L = _ph_labels(labels)
    lr, cl = d.get("learning"), d.get("clauses")
    chip = (f' <button type="button" class="pm-learning" data-lr="{_h(lr)}">{_h(_ph_t(L, "ui.learning_chip", id=lr))}</button>'
            if isinstance(lr, str) and lr else "")
    return chip + (f' <span class="badge pm-clauses">{_h(_ph_t(L, "f.clauses"))}: {_h(", ".join(cl))}</span>' if cl else "")


def _ph_more(sup, L) -> str:
    """The '+N supporting' disclosure of supporting citations."""
    return (f'<details class="more"><summary>{_h(_ph_t(L, "ui.supporting", n=len(sup)))}</summary>{_chips(sup)}</details>'
            if sup else "")


def _extras(d, labels=None) -> str:
    L = _ph_labels(labels)
    s = d.get("evidence_strength")
    badge = f' <span class="badge strength">{_h(_ph_t(L, "f.evidence_strength"))}: {_h(s)}</span>' if s else ""
    return _links(d, L) + badge + _ph_more(d.get("supporting_cites") or [], L)


def _lint_ok_html(d, labels=None) -> str:
    return "".join(f'<p class="lint-ok">{_h(n)}</p>' for n in lint_ok_notes(d, labels))


def _html_item(it, graphs, inc_date=None, labels=None) -> str:
    L = _ph_labels(labels)
    k, g, c = it["kind"], it.get, _chips(it.get("cites"))

    def t(key, **fmt):
        return _ph_t(L, key, **fmt)

    def f(name):
        return t("f." + name)

    def lab(name, value):
        return _labelled(f(name), value)

    if k == "para":
        body = _rich(it["text"]) + c
    elif k == "check":
        key = _h(it["id"])
        hold = f'<span class="badge hold">{_h(f("hold_point"))}</span> ' if g("hold_point") else ""
        when = f' <span class="badge">{_h(g("when"))}</span>' if g("when") else ""
        body = (f'<div class="check"><input type="checkbox" class="tick" id="t-{key}" data-key="{key}" '
                f'aria-labelledby="tl-{key}"><span id="tl-{key}">{hold}{_inline(it["text"])}{when}</span></div>{c}')
    elif k == "question":
        to = f' <span class="badge">{_h(f("to"))}: {_h(g("to"))}</span>' if g("to") else ""
        ops = _typed_options(it, f, t)
        body = (f'<p><b>{_inline(it["question"])}</b>{to}</p>' + ops + lab("why", it["why"])
                + lab("answer", g("answer"))
                + lab("good_evidence", g("good_evidence")) + c)
    elif k == "recommendation":
        meta = _hoc(it["hoc_tier"], L) + _badges([(f("barrier"), g("barrier")), (f("barrier_id"), g("barrier_id")),
                                                  (f("owner"), g("owner")), (f("co_owner"), g("co_owner")),
                                                  (t("ui.by"), g("by_when"))])
        body = (f'<p><b>{_inline(it["change"])}</b></p><p>{meta}</p><p class="indicator-line">'
                f'<span class="label">{_h(f("indicator"))}</span>{_inline(it["indicator"])}</p>'
                + lab("why_not_stronger", g("why_not_stronger")) + c)
    elif k == "decision":
        opts = f'<span class="label">{_h(f("options"))}</span>' + _list(g("options")) if g("options") else ""
        body = (f'<p><b>{_inline(it["decision"])}</b></p>{opts}' + lab("trade_offs", g("trade_offs"))
                + f'<p>{_badges([(f("owner"), g("owner")), (t("ui.by"), g("by_when"))])}</p>{c}')
    elif k == "indicator":
        body = (f'<div class="card"><p><b>{_inline(it["name"])}</b></p>' + lab("measure", it["measure"])
                + lab("deterioration", g("deterioration")) + lab("owner", g("owner")) + c + "</div>")
    elif k == "card":
        disc = f'<span class="label">{_h(f("discussion"))}</span>' + _list(g("discussion"), "ol") if g("discussion") else ""
        body = (f'<div class="card"><h3>{_h(it["title"])}</h3>' + lab("what_happened", it["what_happened"])
                + lab("why_made_sense", g("why_made_sense"))
                + lab("organisation_changing", g("organisation_changing"))
                + f'<span class="label">{_h(f("warning_signs"))}</span>' + _list(it["warning_signs"])
                + lab("good_looks_like", it["good_looks_like"]) + _ph_lablist(f("did_you_know"), g("did_you_know"))
                + _ph_lablist(f("what_you_can_do"), g("what_you_can_do")) + disc + c + PFOOT + "</div>")
    elif k == "scenario":
        body = (f'<p><b>{_h(t("ui.scenario_lead"))}</b> {_inline(it["situation"])}</p><details><summary>'
                f'{_h(f("prompts"))}</summary>' + _list(it["prompts"], "ol") + f"</details>{_ph_injects(g('injects'), L)}{c}")
    elif k == "table":
        rc, rs = g("row_cites"), g("row_supporting_cites")
        cols = list(it["columns"]) + ([f("cites")] if rc or rs else [])
        head = "".join(f'<th scope="col">{_h(x)}</th>' for x in cols)
        rows = []
        for r, row in enumerate(it["rows"]):
            cites = ""
            if rc or rs:
                more = _ph_more(rs[r] if rs else [], L)
                cites = f'<td class="cites-cell">{_chips(rc[r]) if rc else ""}{more}</td>'
            rows.append("<tr>" + "".join(f"<td>{_inline(x)}</td>" for x in row) + cites + "</tr>")
        notes = g("finding_notes")
        note_html = (f'<span class="label">{_h(f("finding_notes"))}</span><ul class="notes">'
                     + "".join(f"<li>{_chip(x)} {_h(v)}</li>" for x, v in notes.items()) + "</ul>") if notes else ""
        body = (f'<div class="tablewrap" tabindex="0"><table><thead><tr>{head}</tr></thead>'
                f'<tbody>{"".join(rows)}</tbody></table></div>{note_html}{c}')
    elif k == "test_point":
        flags = (f'<span class="label">{_h(f("red_flags"))}</span>' + _list(g("red_flags"))
                 if g("red_flags") else "")
        clause = (f'<p><span class="badge pm-clause">{_h(f("clause"))}: {_h(g("clause"))}</span></p>'
                  if g("clause") else "")
        body = (f'<div class="card"><p><b>{_inline(it["requirement"])}</b></p>{clause}'
                + lab("sample", it["sample"])
                + lab("conformity_evidence", it["conformity_evidence"]) + flags + c + PFOOT + "</div>")
    elif k == "module":
        meta = "".join(f'<span class="badge">{_h(g(x))}</span>' for x in ("audience", "duration") if g(x))
        assess = (f"<details><summary>{_h(f('assessment'))}</summary>" + _list(g("assessment"), "ol") + "</details>"
                  if g("assessment") else "")
        body = (f'<div class="card"><h3>{_h(t("ui.module_title", title=it["title"]))}</h3><p>{meta}</p>'
                + lab("objective", it["objective"])
                + f'<span class="label">{_h(f("content"))}</span>' + _list(it["content"], "ol") + assess + c + "</div>")
    elif k == "barrier":
        meta = _hoc(it["hoc_tier"], L) + _badges([(f("barrier_id"), g("barrier_id")), (f("type"), g("type")),
                                                  (t("ui.state"), g("state")), (f("owner"), g("owner"))])
        body = (f'<p><b>{_inline(it["barrier"])}</b></p><p>{meta}</p>' + lab("failure_mode", it["failure_mode"])
                + lab("fix", g("fix")) + lab("indicator", g("indicator")) + c)
    elif k == "timeline":
        lis = []
        for e in sorted_events(it["events"]):
            sig = f'<span class="badge hold">{_h(t("ui.weak_signal"))}</span> ' if e.get("signal") else ""
            when = _h(event_when(e, inc_date, L))
            more = "".join(f'<p class="m">{_h(t(key))}: {_h(e[fl])}</p>'
                           for fl, key in (("received_by", "ui.received_by"), ("response", "ui.response")) if e.get(fl))
            if "knowable_then" in e:
                more += f'<p class="m">{_h(t("ui.knowable_then"))}: {_h(_knowable(e["knowable_then"], L))}</p>'
            lis.append(f'<li><time>{when}</time>{sig}{_inline(e["text"])} {_chips(e.get("cites"))}{more}</li>')
        body = f'<ol class="timeline">{"".join(lis)}</ol>{c}'
    elif k == "graph":
        gr = graphs[it["id"]]
        names = {n["id"]: n["label"] for n in it["nodes"]}
        note = f'<p class="m">{_h(t("ui.graph_omitted", n=gr["omitted"]))}</p>' if gr["omitted"] else ""
        links = "".join(f'<li>{_h(names[e["from"]])} → {_h(names[e["to"]])}'
                        + (f' ({_h(e["label"])})' if e.get("label") else "") + "</li>" for e in it["edges"])
        body = (f'<div class="graphwrap">{gr["svg"]}</div>{note}<details><summary>'
                f'{_h(t("ui.links_as_text", n=len(it["edges"])))}</summary><ul>{links}</ul></details>{c}')
    elif k == "learning":
        body = (f'<p><b>{_inline(it["lesson"])}</b> {_badges([(f("owner"), g("owner"))])}</p>'
                + (_rich(it["explanation"]) if g("explanation") else "") + c)
    elif k == "toolbox":
        body = _ph_toolbox(it, L) + c + PFOOT + "</div>"
    elif k == "script":
        body = _ph_script(it, L) + c
    else:
        body = _html_fields(it, L) + c
    return f'<div class="item k-{k}" id="i-{_h(it["id"])}">{body}{_extras(it, L)}{_lint_ok_html(it, L)}</div>'


def _ph_lablist(label, xs) -> str:
    """A labelled bullet list (the card's R3 fields), or "" when there is nothing to list."""
    return f'<span class="label">{_h(label)}</span>' + _list(xs) if xs else ""


def _ph_injects(injects, L) -> str:
    """A scenario's injects (L4-30): an ordered list, each with its +HH:MM offset and any decision point."""
    if not injects:
        return ""
    lis = "".join(f'<li><time>{_h(x["offset"])}</time>{_inline(x["text"])}'
                  + (f'<p class="m"><span class="badge hold">{_h(_ph_t(L, "ui.decision_point"))}</span> '
                     f'{_inline(x["decision"])}</p>' if x.get("decision") else "") + "</li>" for x in injects)
    return f'<span class="label">{_h(_ph_t(L, "f.injects"))}</span><ol class="timeline injects">{lis}</ol>'


def _ph_toolbox(it, L) -> str:
    """A toolbox talk (L2-18): the five parts of output-style.md, in order, as an ordered list on a card. The caller
    closes the card after the citations and the print footer."""
    dur = it.get("duration")
    meta = f'<p><span class="badge">{_h(_ph_t(L, "f.duration"))}: {_h(dur)}</span></p>' if dur else ""
    parts = [("opening_question", f'<p>{_inline(it["opening_question"])}</p>'), ("story", _rich(it["story"])),
             ("warning_signs", _list(it["warning_signs"])), ("one_change", f'<p>{_inline(it["one_change"])}</p>'),
             ("crew_question", f'<p>{_inline(it["crew_question"])}</p>')]
    lis = "".join(f'<li><span class="label">{_h(_ph_t(L, "f." + n))}</span>{v}</li>' for n, v in parts)
    return f'<div class="card"><h3>{_h(_ph_t(L, "k.toolbox"))}</h3>{meta}<ol>{lis}</ol>'


def _ph_script(it, L) -> str:
    """A shooting script (L4-19): the two-column Visual | Narration table, each visual led by its time, then the
    total duration."""
    rows, t0 = [], 0
    for sg in it["segments"]:
        t1 = t0 + sg["seconds"]
        shown = (f'<p class="m">{_h(_ph_t(L, "f.on_screen"))}: {_inline(sg["on_screen"])}</p>'
                 if sg.get("on_screen") else "")
        rows.append(f'<tr><td><time>{_pm_clock(t0)}–{_pm_clock(t1)}</time><p>{_inline(sg["visual"])}</p>{shown}</td>'
                    f'<td><p>{_inline(sg["narration"])}</p>{_chips(sg.get("cites"))}</td></tr>')
        t0 = t1
    head = "".join(f'<th scope="col">{_h(_ph_t(L, "f." + x))}</th>' for x in ("visual", "narration"))
    meta = "".join(f'<span class="badge">{_h(_ph_t(L, "f." + x))}: {_h(it[x])}</span>' for x in ("channel",) if it.get(x))
    purpose = _labelled(_ph_t(L, "f.purpose"), it.get("purpose"))
    return (f'<p><b>{_h(it["title"])}</b> <span class="badge">{_h(_ph_t(L, "k.script"))}</span>{meta}</p>{purpose}'
            f'<div class="tablewrap" tabindex="0"><table><thead><tr>{head}</tr></thead><tbody>{"".join(rows)}</tbody>'
            f'</table></div><p class="m">{_h(_ph_t(L, "ui.total_duration", time=_pm_clock(t0)))}</p>')


def _html_block_value(v) -> str:
    if isinstance(v, list):
        return _list([" | ".join(map(str, x)) if isinstance(x, list) else x for x in v])
    if isinstance(v, dict):
        return _list([f"{k}: {x}" for k, x in v.items()])
    return _inline(v)


def _html_fields(it, labels=None) -> str:
    """A kind this renderer has no layout for: its fields as a labelled list, in KINDS field order (P4-5)."""
    from ..render.fields import item_blocks
    rows = "".join(f"<dt>{_h(b.label)}</dt><dd>{_html_block_value(b.value)}</dd>"
                   for b in item_blocks(it, _ph_labels(labels)))
    return f'<dl class="fields">{rows}</dl>'


def _section_items(items, graphs, inc_date=None, labels=None) -> str:
    out, run, prev = [], [], None

    def flush():
        if run:
            out.append('<div class="grid">' + "".join(run) + "</div>")
            run.clear()

    for it in items:
        g = it.get("group")
        if g and g != prev:
            flush()
            out.append(f'<h3 class="group">{_h(g)}</h3>')
        prev = g
        h = _html_item(it, graphs, inc_date, labels)
        if it["kind"] in GRID_KINDS:
            run.append(h)
            continue
        flush()
        out.append(h)
    flush()
    return "".join(out)


def build_pack_data(w, pack, run, embed=EMBED_DEFAULT, share=None) -> dict:
    """What the page script needs, as --embed says (embedded_records). cited: full records of the cited
    findings and evidence, and the relevant findings the pack leaves uncited or excludes as {id, label, rating},
    so the coverage list can still expand them. summary: cited without quotes. full: full records of all of them
    plus the evidence the cited findings link."""
    uncited = [x for x in relevant_findings(w, pack.get("scope")) if x not in cited_ids(pack)[0]]
    fids, eids = embedded_ids(pack)                    # gap cites too, so every citation button opens its record
    findings, evidence = embedded_records(w, fids, eids, uncited + excluded_ids(pack), embed, linked=False)
    if share and share.mode == "public":
        findings = public_records(findings)
    data = {"pack": pack["pack"], "run": run, "findings": findings, "evidence": evidence, "brand": brand_payload()}
    if share:
        data.pop("run")              # a shared copy carries no run slug (share_doc drops the key anywhere else)
    return data


def _trail(data, pack, labels=None) -> str:
    """The print-only evidence trail: the cited findings and evidence only (L4-01), in citation order."""
    L = _ph_labels(labels, pack)
    fids, eids = cited_ids(pack)
    rows = [f'<dt>{_h(i)}</dt><dd>{_h(f.get("label") or f.get("name"))} · L{_h(f.get("level"))} · '
            f'{_h(_ph_t(L, "ui.rating", rating=_ph_blank(f.get("rating"))))}. {_h(f.get("short"))}</dd>'
            for i, f in ((x, data["findings"].get(x)) for x in fids) if f]
    rows += [f'<dt>{_h(i)}</dt><dd>{_h(e.get("type"))}' + (f': {_h(e["description"])}' if e.get("description") else "")
             + "</dd>" for i, e in ((x, data["evidence"].get(x)) for x in eids) if e]
    return f'<section class="trail"><h2>{_h(_ph_t(L, "ui.evidence_trail"))}</h2><dl>{"".join(rows)}</dl></section>'


def _ph_blank(v):
    """None as an empty string, as _h shows it."""
    return "" if v is None else v


def _ph_reason(r, L) -> str:
    """An uncovered finding's reason from coverage(), in the page's language."""
    en = {"reviewer downgrade vote": "ui.reason_downgrade", "not cited in this pack": "ui.reason_uncited"}
    return _ph_t(L, en[r]) if r in en else r


def render_pack_html(w, pack, run, generated, embed=EMBED_DEFAULT, eh=None, share=None, labels=None, brand=None) -> str:
    """One self-contained offline page: server-rendered content, with pack.js adding behaviour. embed: see
    build_pack_data. eh and share: see render_pack_md; a shared copy shows no run slug or generated date. labels:
    the page labels, else those of the pack's lang; a page in another language than English carries them in its
    payload for pack.js, and its <html> names its lang and dir (Ruling P4-15). brand: the organisation brand
    (Ruling P4-16): its accent, logo and name; the footer and status line never change."""
    from ..render.brand import brand_css, brand_header
    from ..render.fields import reading_minutes
    from ..render.labels import text_dir
    L = _ph_labels(labels, pack)

    def t(key, **fmt):
        return _h(_ph_t(L, key, **fmt))

    lang = pack.get("lang") or "en"
    tdir = pack.get("dir") or text_dir(L)
    html_open = f'<html lang="{_h(lang)}">' if lang == "en" and tdir == "ltr" else f'<html lang="{_h(lang)}" dir="{_h(tdir)}">'
    inc_date = _pack_incident_date(pack, w)
    eh = eh or effective_handling(pack, w)  # before with_item_ids, which would change the content hash
    pack = with_item_ids(pack)
    fields = w.get("incident", {}).get("fields", {})
    data = build_pack_data(w, pack, run, embed, share)
    if lang != "en":
        data["labels"] = L
    cov = coverage(w, pack)
    graphs = {it["id"]: layout_graph(it["nodes"], it["edges"], uid=it["id"])
              for s in pack["sections"] for it in s["items"] if it["kind"] == "graph"}
    has_checks = any(it["kind"] == "check" for s in pack["sections"] for it in s["items"])

    rail = "".join(f'<li><a href="#s/{_h(s["id"])}"><span>{_h(s["heading"])}</span>'
                   f'<span class="n">{len(s["items"])}</span></a></li>' for s in pack["sections"])
    secs = []
    for s in pack["sections"]:
        intro = f'<div class="intro">{_rich(s["intro"])}</div>' if s.get("intro") else ""
        secs.append(f'<details class="sec" id="s-{_h(s["id"])}" open><summary><h2>{_h(s["heading"])}</h2>'
                    f'<span class="n">{len(s["items"])}</span></summary><div class="sec-body">{intro}'
                    f'{_section_items(s["items"], graphs, inc_date, L)}</div></details>')
    dq = pack.get("data_quality") or []
    dq_html = (f'<section class="dq"><h2>{t("ui.data_quality")}</h2><ul>'
               + "".join(f'<li>{_inline(n["text"])} {_chips(n.get("cites"))}</li>' for n in dq) + "</ul></section>") if dq else ""
    gaps = pack.get("gaps") or []
    gaps_html = (f'<section class="gaps"><h2>{t("ui.gaps")}</h2><ul>'
                 + "".join(f'<li>{_h(x["text"])} {_chips(x.get("cites"))}<p class="m">{t("ui.evidence_needed")}: '
                           f'{_h(x["evidence_needed"])}</p></li>' for x in gaps) + "</ul></section>") if gaps else ""
    limits = pack.get("limits") or []
    limits_html = (f'<section class="limits"><h2>{t("ui.limits")}</h2><ul>'
                   + "".join(f"<li>{_h(x)}</li>" for x in limits) + "</ul></section>") if limits else ""
    exc = "".join(f'<li>{_chip(e["id"])} {_h(e["label"])} · {_h(e["reason"])}</li>' for e in cov["excluded"])
    unc = "".join(f'<li>{_chip(u["id"])} {_h(u["label"])} · {t("ui.rating", rating=_ph_blank(u["rating"]))} · L{_h(u["level"])} · '
                  f'{_h(_ph_reason(u["reason"], L))}</li>' for u in cov["uncovered"])
    cov_html = (f'<section class="coverage"><h2>{t("ui.coverage")}</h2>'
                f'<p class="noprint">This pack cites {cov["cited"]} of {cov["relevant"]} relevant findings.</p>'
                f'<p class="printonly">{_h(UNCOVERED_PRINT_LINE.format(x=cov["cited"], y=cov["relevant"]))}</p>'
                f'<p class="top-rated">{_h(TOP_PRINT_LINE.format(x=cov["top_cited"], y=cov["top_relevant"]))}</p>'
                + (f'<details class="noprint"><summary>Not covered here ({len(cov["uncovered"])})</summary>'
                   f'<ul>{unc}</ul></details>' if unc else "")
                + (f'<details><summary>{t("ui.left_out")} ({len(cov["excluded"])})</summary><ul>{exc}</ul></details>'
                   if exc else "") + "</section>")
    bottom = "".join(f'<li>{_inline(b["text"])} {_chips(b.get("cites"))}{_extras(b, L)}{_lint_ok_html(b, L)}</li>'
                     for b in pack["bottom_line"])
    clear = f'<button type="button" id="clear-ticks">{t("ui.clear_ticks")}</button>' if has_checks else ""
    inc = pack.get("incident") or {}
    trace = () if share else (_ph_t(L, "ui.run", run=run), _ph_t(L, "ui.generated", date=generated))
    meta = " · ".join(_h(x) for x in (pack["audience"], inc.get("title") or fields.get("Incident Title"),
                                      inc.get("date") or fields.get("Date"), *trace) if x)
    title = _h(pack["title"])
    status = _h(status_line(pack["status"]))
    ribbon = RIBBON_HTML + "\n" if is_draft(eh) else ""
    handling = "".join(f'<p class="handling">{_h(x)}</p>' for x in _handling_lines(eh, share, markdown=False))
    css = (DASHBOARD_ASSETS / "pack.css").read_text(encoding="utf-8")
    js = (DASHBOARD_ASSETS / "pack.js").read_text(encoding="utf-8")
    payload = embed_json(data)
    footer_brand = _h(BRAND)
    tokens, wide = PAGE_TOKENS_CSS, WIDE_CSS
    bcss = brand_css(brand)
    brand_style = "\n" + bcss if bcss else ""
    brand_id = brand_header(brand)
    reading = t("ui.reading_time", n=reading_minutes(pack))
    body = "".join(secs) + gaps_html + limits_html + cov_html + _trail(data, pack, L)
    return f"""<!doctype html>{html_open}<head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{title}</title>
<style>
{tokens}
main{{max-width:1180px;margin:0 auto;padding:24px 16px 48px}}
{wide}
h1{{font-size:24px;margin:0 0 4px}} p.m{{color:var(--mut);margin:0 0 8px}}
footer{{margin-top:40px;color:var(--mut);font-size:12px;border-top:1px solid var(--line);padding-top:12px}}
{HANDLING_CSS}
{css}{brand_style}
</style></head><body><main>
{ribbon}{brand_id}<h1>{title}</h1>
<p class="m">{meta}</p>
<p class="m reading">{reading}</p>
<p class="status">{status}</p>
{handling}
{dq_html}
<section class="bottom"><h2>{t("ui.bottom_line")}</h2><ul>{bottom}</ul></section>
<div class="toolbar" role="search"><input id="q" type="search" placeholder="{t("ui.search")}" aria-label="{t("ui.search")}">
<button type="button" id="expand-all">{t("ui.expand_all")}</button><button type="button" id="collapse-all">{t("ui.collapse_all")}</button>
<button type="button" id="print">{t("ui.print")}</button>{clear}<span id="showing" aria-live="polite"></span></div>
<div class="layout"><details class="rail" open><summary>{t("ui.contents")}</summary><ol>{rail}</ol></details>
<div class="content">{body}</div></div>
<footer>{footer_brand}</footer>
</main>
<script type="application/json" id="pmlc-pack-data">{payload}</script>
<script>
{js}
</script>
</body></html>"""


def follow_up(pack) -> dict:
    """investigator-coach: finding ID -> the export's four follow-up fields, read from the table with id follow-up.
    A row may name several findings (one row per condition); each gets the row's fields, plus its own note if
    finding_notes gives one."""
    for s in pack["sections"]:
        for it in s["items"]:
            if it.get("id") == "follow-up" and it.get("kind") == "table":
                out, notes = {}, it.get("finding_notes") or {}
                for row in it["rows"]:
                    fields = dict(zip(FOLLOW_UP_KEYS, (str(x) for x in row[1:5])))
                    for x in re.split(r"[\s,;]+", str(row[0])):
                        if x:
                            out[x] = dict(fields, **({"note": notes[x]} if x in notes else {}))
                return out
    return {}


def update_gaps(ws, pack):
    """Rewrite <run>/outputs/gaps.json for this pack (L3-14): its entries are replaced by its current gaps, other
    packs' entries are kept. Always the run's outputs folder (artefacts.json), whatever --out says; the file is
    written only when the pack has gaps or the file already exists. Returns the path written, or None."""
    path = outputs_dir(ws) / "gaps.json"
    mine = [{"pack": pack["pack"], "text": g["text"], "cites": list(g.get("cites") or []),
             "evidence_needed": g["evidence_needed"]} for g in pack.get("gaps") or []]
    if not mine and not path.is_file():
        return None
    try:
        old = json.loads(path.read_text(encoding="utf-8")).get("gaps", []) if path.is_file() else []
    except (OSError, UnicodeDecodeError, json.JSONDecodeError, AttributeError):
        old = []
    keep = [g for g in old if isinstance(g, dict) and g.get("pack") != pack["pack"]] if isinstance(old, list) else []
    write_json(path, {"gaps": keep + mine})
    return path
