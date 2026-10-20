"""Learning packs: the HTML renderer and the pack command."""
from __future__ import annotations

import datetime as dt
import html
import re
from pathlib import Path

from .. import BRAND, brand_payload, STATUS_PHRASE
from ..dashboard.data import (
    DASHBOARD_ASSETS, EMBED_DEFAULT, embed_json, embedded_records, print_witness_note, resolve_embed
)
from ..dashboard.render import PAGE_TOKENS_CSS, WIDE_CSS
from ..handling import (
    effective_handling, HANDLING_CSS, is_draft, name_guard, public_records, RIBBON_HTML, share_ctx, share_gate,
    shared_copy, SHARED_LINE, shared_name, status_line
)
from ..pack.graph_layout import layout_graph
from ..pack.markdown import (
    _handling_lines, _knowable, _pack_incident_date, coverage, event_when, lint_ok_notes, render_pack_md,
    sorted_events
)
from ..pack.schema import (
    _checked, cited_ids, excluded_ids, FOLLOW_UP_KEYS, ID_RX, relevant_findings, TOP_PRINT_LINE, UNCOVERED_PRINT_LINE,
    with_item_ids
)
from ..register.check import norm_hoc
from ..util import _abs, write_json
from ..workspace import is_standard_ws, outputs_dir, warn_stale


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


def _badges(pairs) -> str:
    return "".join(f'<span class="badge">{_h(k)}: {_h(v)}</span>' for k, v in pairs if v)


def _hoc(v) -> str:
    t = norm_hoc(v)
    cls = "badge strong" if t in STRONG_HOC else "badge"
    return f'<span class="{cls}">Control: {_h(t)}</span>'


def _extras(d) -> str:
    s = d.get("evidence_strength")
    badge = f' <span class="badge strength">Evidence: {_h(s)}</span>' if s else ""
    sup = d.get("supporting_cites") or []
    more = f'<details class="more"><summary>+{len(sup)} supporting</summary>{_chips(sup)}</details>' if sup else ""
    return badge + more


def _lint_ok_html(d) -> str:
    return "".join(f'<p class="lint-ok">{_h(n)}</p>' for n in lint_ok_notes(d))


def _html_item(it, graphs, inc_date=None) -> str:
    k, g, c = it["kind"], it.get, _chips(it.get("cites"))
    if k == "para":
        body = _rich(it["text"]) + c
    elif k == "check":
        key = _h(it["id"])
        hold = '<span class="badge hold">Hold point</span> ' if g("hold_point") else ""
        when = f' <span class="badge">{_h(g("when"))}</span>' if g("when") else ""
        body = (f'<div class="check"><input type="checkbox" class="tick" id="t-{key}" data-key="{key}" '
                f'aria-labelledby="tl-{key}"><span id="tl-{key}">{hold}{_inline(it["text"])}{when}</span></div>{c}')
    elif k == "question":
        to = f' <span class="badge">Put to: {_h(g("to"))}</span>' if g("to") else ""
        body = (f'<p><b>{_inline(it["question"])}</b>{to}</p>' + _labelled("Why it matters", it["why"])
                + _labelled("Answer", g("answer"))
                + _labelled("Good evidence looks like", g("good_evidence")) + c)
    elif k == "recommendation":
        meta = _hoc(it["hoc_tier"]) + _badges([("Barrier", g("barrier")), ("Owner", g("owner")), ("By", g("by_when"))])
        body = (f'<p><b>{_inline(it["change"])}</b></p><p>{meta}</p><p class="indicator-line">'
                f'<span class="label">Leading indicator</span>{_inline(it["indicator"])}</p>{c}')
    elif k == "decision":
        opts = '<span class="label">Options</span>' + _list(g("options")) if g("options") else ""
        body = (f'<p><b>{_inline(it["decision"])}</b></p>{opts}' + _labelled("Trade-offs", g("trade_offs"))
                + f'<p>{_badges([("Owner", g("owner")), ("By", g("by_when"))])}</p>{c}')
    elif k == "indicator":
        body = (f'<div class="card"><p><b>{_inline(it["name"])}</b></p>' + _labelled("Measure", it["measure"])
                + _labelled("Deterioration looks like", g("deterioration")) + _labelled("Owner", g("owner")) + c + "</div>")
    elif k == "card":
        disc = '<span class="label">Questions for discussion</span>' + _list(g("discussion"), "ol") if g("discussion") else ""
        body = (f'<div class="card"><h3>{_h(it["title"])}</h3>' + _labelled("What happened", it["what_happened"])
                + _labelled("Why it made sense at the time", g("why_made_sense"))
                + _labelled("What the organisation is changing", g("organisation_changing"))
                + '<span class="label">Warning signs</span>' + _list(it["warning_signs"])
                + _labelled("What good looks like", it["good_looks_like"]) + disc + c + PFOOT + "</div>")
    elif k == "scenario":
        body = (f'<p><b>Scenario.</b> {_inline(it["situation"])}</p><details><summary>Discussion prompts</summary>'
                + _list(it["prompts"], "ol") + f"</details>{c}")
    elif k == "table":
        rc, rs = g("row_cites"), g("row_supporting_cites")
        cols = list(it["columns"]) + (["Cites"] if rc or rs else [])
        head = "".join(f'<th scope="col">{_h(x)}</th>' for x in cols)
        rows = []
        for r, row in enumerate(it["rows"]):
            cites = ""
            if rc or rs:
                sup = rs[r] if rs else []
                more = (f'<details class="more"><summary>+{len(sup)} supporting</summary>{_chips(sup)}</details>'
                        if sup else "")
                cites = f'<td class="cites-cell">{_chips(rc[r]) if rc else ""}{more}</td>'
            rows.append("<tr>" + "".join(f"<td>{_inline(x)}</td>" for x in row) + cites + "</tr>")
        notes = g("finding_notes")
        note_html = ('<span class="label">Notes per finding</span><ul class="notes">'
                     + "".join(f"<li>{_chip(x)} {_h(v)}</li>" for x, v in notes.items()) + "</ul>") if notes else ""
        body = (f'<div class="tablewrap" tabindex="0"><table><thead><tr>{head}</tr></thead>'
                f'<tbody>{"".join(rows)}</tbody></table></div>{note_html}{c}')
    elif k == "test_point":
        flags = ('<span class="label">Red flags seen in this investigation</span>' + _list(g("red_flags"))
                 if g("red_flags") else "")
        body = (f'<div class="card"><p><b>{_inline(it["requirement"])}</b></p>' + _labelled("What to sample", it["sample"])
                + _labelled("Evidence of conformity", it["conformity_evidence"]) + flags + c + PFOOT + "</div>")
    elif k == "module":
        meta = "".join(f'<span class="badge">{_h(g(f))}</span>' for f in ("audience", "duration") if g(f))
        assess = ("<details><summary>Assessment</summary>" + _list(g("assessment"), "ol") + "</details>"
                  if g("assessment") else "")
        body = (f'<div class="card"><h3>Module: {_h(it["title"])}</h3><p>{meta}</p>' + _labelled("Objective", it["objective"])
                + '<span class="label">Content</span>' + _list(it["content"], "ol") + assess + c + "</div>")
    elif k == "barrier":
        meta = _hoc(it["hoc_tier"]) + _badges([("Type", g("type")), ("State", g("state")), ("Owner", g("owner"))])
        body = (f'<p><b>{_inline(it["barrier"])}</b></p><p>{meta}</p>' + _labelled("Failure mode", it["failure_mode"])
                + _labelled("Fix", g("fix")) + _labelled("Leading indicator", g("indicator")) + c)
    elif k == "timeline":
        lis = []
        for e in sorted_events(it["events"]):
            sig = '<span class="badge hold">Weak signal</span> ' if e.get("signal") else ""
            when = _h(event_when(e, inc_date))
            more = "".join(f'<p class="m">{lab}: {_h(e[f])}</p>'
                           for f, lab in (("received_by", "Received by"), ("response", "Response")) if e.get(f))
            if "knowable_then" in e:
                more += f'<p class="m">Knowable then: {_h(_knowable(e["knowable_then"]))}</p>'
            lis.append(f'<li><time>{when}</time>{sig}{_inline(e["text"])} {_chips(e.get("cites"))}{more}</li>')
        body = f'<ol class="timeline">{"".join(lis)}</ol>{c}'
    elif k == "graph":
        gr = graphs[it["id"]]
        lab = {n["id"]: n["label"] for n in it["nodes"]}
        note = (f'<p class="m">{gr["omitted"]} nodes with the fewest links are not drawn; every link is listed below.</p>'
                if gr["omitted"] else "")
        links = "".join(f'<li>{_h(lab[e["from"]])} → {_h(lab[e["to"]])}'
                        + (f' ({_h(e["label"])})' if e.get("label") else "") + "</li>" for e in it["edges"])
        body = (f'<div class="graphwrap">{gr["svg"]}</div>{note}<details><summary>Links as text ({len(it["edges"])})'
                f'</summary><ul>{links}</ul></details>{c}')
    elif k == "learning":
        body = (f'<p><b>{_inline(it["lesson"])}</b> {_badges([("Owner", g("owner"))])}</p>'
                + (_rich(it["explanation"]) if g("explanation") else "") + c)
    else:
        raise ValueError(f"unknown kind {k!r}")
    return f'<div class="item k-{k}" id="i-{_h(it["id"])}">{body}{_extras(it)}{_lint_ok_html(it)}</div>'


def _section_items(items, graphs, inc_date=None) -> str:
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
        h = _html_item(it, graphs, inc_date)
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
    fids, eids = cited_ids(pack)
    uncited = [x for x in relevant_findings(w, pack.get("scope")) if x not in fids]
    findings, evidence = embedded_records(w, fids, eids, uncited + excluded_ids(pack), embed, linked=False)
    if share and share.mode == "public":
        findings = public_records(findings)
    data = {"pack": pack["pack"], "run": run, "findings": findings, "evidence": evidence, "brand": brand_payload()}
    if share:
        data.pop("run")              # a shared copy carries no run slug (share_doc drops the key anywhere else)
    return data


def _trail(data, pack) -> str:
    """The print-only evidence trail: the cited findings and evidence only (L4-01), in citation order."""
    fids, eids = cited_ids(pack)
    rows = [f'<dt>{_h(i)}</dt><dd>{_h(f.get("label") or f.get("name"))} · L{_h(f.get("level"))} · '
            f'rating {_h(f.get("rating"))}. {_h(f.get("short"))}</dd>'
            for i, f in ((x, data["findings"].get(x)) for x in fids) if f]
    rows += [f'<dt>{_h(i)}</dt><dd>{_h(e.get("type"))}' + (f': {_h(e["description"])}' if e.get("description") else "")
             + "</dd>" for i, e in ((x, data["evidence"].get(x)) for x in eids) if e]
    return f'<section class="trail"><h2>Evidence trail</h2><dl>{"".join(rows)}</dl></section>'


def render_pack_html(w, pack, run, generated, embed=EMBED_DEFAULT, eh=None, share=None) -> str:
    """One self-contained offline page: server-rendered content, with pack.js adding behaviour. embed: see
    build_pack_data. eh and share: see render_pack_md; a shared copy shows no run slug or generated date."""
    inc_date = _pack_incident_date(pack, w)
    eh = eh or effective_handling(pack, w)  # before with_item_ids, which would change the content hash
    pack = with_item_ids(pack)
    fields = w.get("incident", {}).get("fields", {})
    data = build_pack_data(w, pack, run, embed, share)
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
                    f'{_section_items(s["items"], graphs, inc_date)}</div></details>')
    dq = pack.get("data_quality") or []
    dq_html = ('<section class="dq"><h2>Data quality and limits</h2><ul>'
               + "".join(f'<li>{_inline(n["text"])} {_chips(n.get("cites"))}</li>' for n in dq) + "</ul></section>") if dq else ""
    exc = "".join(f'<li>{_chip(e["id"])} {_h(e["label"])} · {_h(e["reason"])}</li>' for e in cov["excluded"])
    unc = "".join(f'<li>{_chip(u["id"])} {_h(u["label"])} · rating {_h(u["rating"])} · L{_h(u["level"])} · '
                  f'{_h(u["reason"])}</li>' for u in cov["uncovered"])
    cov_html = ('<section class="coverage"><h2>Coverage</h2>'
                f'<p class="noprint">This pack cites {cov["cited"]} of {cov["relevant"]} relevant findings.</p>'
                f'<p class="printonly">{_h(UNCOVERED_PRINT_LINE.format(x=cov["cited"], y=cov["relevant"]))}</p>'
                f'<p class="top-rated">{_h(TOP_PRINT_LINE.format(x=cov["top_cited"], y=cov["top_relevant"]))}</p>'
                + (f'<details class="noprint"><summary>Not covered here ({len(cov["uncovered"])})</summary>'
                   f'<ul>{unc}</ul></details>' if unc else "")
                + (f'<details><summary>Left out on purpose ({len(cov["excluded"])})</summary><ul>{exc}</ul></details>'
                   if exc else "") + "</section>")
    bottom = "".join(f'<li>{_inline(b["text"])} {_chips(b.get("cites"))}{_extras(b)}{_lint_ok_html(b)}</li>'
                     for b in pack["bottom_line"])
    clear = '<button type="button" id="clear-ticks">Clear ticks</button>' if has_checks else ""
    inc = pack.get("incident") or {}
    trace = () if share else (f"run {run}", f"generated {generated}")
    meta = " · ".join(_h(x) for x in (pack["audience"], inc.get("title") or fields.get("Incident Title"),
                                      inc.get("date") or fields.get("Date"), *trace) if x)
    title = _h(pack["title"])
    status = _h(status_line(pack["status"]))
    ribbon = RIBBON_HTML + "\n" if is_draft(eh) else ""
    handling = "".join(f'<p class="handling">{_h(x)}</p>' for x in _handling_lines(eh, share))
    css = (DASHBOARD_ASSETS / "pack.css").read_text(encoding="utf-8")
    js = (DASHBOARD_ASSETS / "pack.js").read_text(encoding="utf-8")
    payload = embed_json(data)
    brand = _h(BRAND)
    tokens, wide = PAGE_TOKENS_CSS, WIDE_CSS
    body = "".join(secs) + cov_html + _trail(data, pack)
    return f"""<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{title}</title>
<style>
{tokens}
main{{max-width:1180px;margin:0 auto;padding:24px 16px 48px}}
{wide}
h1{{font-size:24px;margin:0 0 4px}} p.m{{color:var(--mut);margin:0 0 8px}}
footer{{margin-top:40px;color:var(--mut);font-size:12px;border-top:1px solid var(--line);padding-top:12px}}
{HANDLING_CSS}
{css}
</style></head><body><main>
{ribbon}<h1>{title}</h1>
<p class="m">{meta}</p>
<p class="status">{status}</p>
{handling}
{dq_html}
<section class="bottom"><h2>Bottom line</h2><ul>{bottom}</ul></section>
<div class="toolbar" role="search"><input id="q" type="search" placeholder="Search this pack" aria-label="Search this pack">
<button type="button" id="expand-all">Expand all</button><button type="button" id="collapse-all">Collapse all</button>
<button type="button" id="print">Print</button>{clear}<span id="showing" aria-live="polite"></span></div>
<div class="layout"><details class="rail" open><summary>Contents</summary><ol>{rail}</ol></details>
<div class="content">{body}</div></div>
<footer>{brand}</footer>
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


def cmd_pack(a):
    """Render a checked pack. --share external|public: the share gate first (P2-9), then the page is rendered from
    masked copies of the pack and the workspace. In any mode the render name guard runs before anything is written."""
    w, pack, _ = _checked(a)
    warn_stale(a.ws)
    mode = share_gate(pack, w, a, src=a.pack, ws=a.ws)
    ws = _abs(a.ws)
    run = ws.parent.name if is_standard_ws(ws) else ws.name
    embed = resolve_embed(a)
    eh = effective_handling(pack, w, src=a.pack, ws=a.ws)
    share = share_ctx(a, w, mode) if mode != "internal" else None
    rw, rpack = (shared_copy(w, share, w), shared_copy(pack, share, w)) if share else (w, pack)
    page_html = render_pack_html(rw, rpack, run, dt.date.today().isoformat(), embed, eh=eh, share=share)
    md_text = None if a.no_md else render_pack_md(rpack, rw, eh=eh, share=share)
    name_guard([page_html, md_text or ""], a)
    out = Path(a.out) if a.out else outputs_dir(ws)
    out.mkdir(parents=True, exist_ok=True)
    page = shared_name(out / f"{pack['pack']}.html", mode)
    page.write_text(page_html, encoding="utf-8")
    print_witness_note(embedded_records(rw, *cited_ids(pack), (), embed, linked=False)[1], embed)
    print(f"HTML written to {page}")
    if md_text is not None:
        md = shared_name(out / f"{pack['pack']}.md", mode)
        md.write_text(md_text, encoding="utf-8")
        print(f"Markdown written to {md}")
    if mode != "internal":
        print(SHARED_LINE.format(mode=mode))
    if pack["pack"] == "investigator-coach" and mode == "internal":   # interview plans never leave the team
        fu = out / "follow-up.json"
        write_json(fu, follow_up(pack))
        print(f"Follow-up fields written to {fu}")
