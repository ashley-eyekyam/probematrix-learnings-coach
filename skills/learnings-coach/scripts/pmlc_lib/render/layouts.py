"""Print layouts (Rulings P4-7, P4-8; P3-15's printable delivery record): `pack --layout cards|toolbox|poster|
checklist|paper|field` writes <pack>.<layout>.html beside the normal outputs, never changing <pack>.html. Each
printed page block (<section class="page">) carries the status phrase, the short footer and, for a draft, the DRAFT
label (page()). The pages are plain print-first HTML: no script, no citation buttons."""
from __future__ import annotations

import base64
import dataclasses
import html
import re
from urllib.parse import quote

from .. import DRAFT_LABEL, VERSION_STAMP
from ..dashboard.data import DASHBOARD_ASSETS
from ..handling import is_draft, PAGE_FOOTER_CSS, status_line
from ..pack.markdown import _handling_lines, _pack_incident_date, event_when, sorted_events
from ..pack.schema import ID_RX
from ..templates import DISTRIBUTION_COLUMNS
from . import (
    CHECK_LINE, LEARNER_BANNER, MORE_IN_PACK, NOTHING_TO_WRITE, Output, output_name, READING_TIME, RenderContext,
    translation_lines
)
from .fields import item_blocks, learner_view, reading_minutes
from .labels import label, load_labels, text_dir

LAYOUTS = ("cards", "toolbox", "poster", "checklist", "paper", "field")
PAPERS = ("A4", "A5")
LAYOUT_FOOTER = f"{VERSION_STAMP} · ProbeMatrix by Eyekyam"           # the short footer on every printed page
QR_TOO_LONG = "{layout}: QR codes left out: the link is too long for a QR code ({chars} characters)"
LY_CARD_KINDS = ("card", "toolbox", "test_point")                         # one printed page each (and scenario injects)
LY_CHECK_KINDS = ("check", "test_point")
LY_TOOLBOX_PARTS = (("opening_question", "ui.layout.toolbox_opening"), ("story", "ui.layout.toolbox_story"),
                 ("warning_signs", "ui.layout.toolbox_signs"), ("one_change", "ui.layout.toolbox_change"),
                 ("crew_question", "ui.layout.toolbox_ask"))
DELIVERY_COLUMNS = DISTRIBUTION_COLUMNS[2:]          # distribution.csv after pack and audience (P4-8)
DELIVERY_ROWS = 10
POSTER_MAX = 6
POSTER_EVENTS = 8
# A run of inline citations, "[FND-…; EVD-…]" or "[EVD-1] [EVD-2]", with the space before it.
_LY_ID = r"(?:FND-[0-9A-Za-z]{4,}|EVD-\d{3,})"
LY_BRACKET_RX = re.compile(rf"\s*\[\s*({_LY_ID}(?:\s*[;,]\s*{_LY_ID})*)\s*\]")


# ----------------------------------------------------------------------------- shared helpers

def _ly_h(s) -> str:
    return html.escape("" if s is None else str(s), quote=True)


def _ly_labels(ctx: RenderContext) -> dict:
    return ctx.labels or load_labels(ctx.pack.get("lang") or "en")


class _LyNotes:
    """Numbered end-notes (the field layout): one number per cited ID, in first-cited order."""

    def __init__(self):
        self.ids = {}

    def mark(self, ids) -> str:
        nums = [self.ids.setdefault(x, len(self.ids) + 1) for x in dict.fromkeys(ids)]
        return f'<sup class="en">{",".join(map(str, nums))}</sup>' if nums else ""


def _ly_text(s, notes=None) -> str:
    """Escaped text. With end-notes, inline citations become note numbers (no IDs left in the text)."""
    s = "" if s is None else str(s)
    if notes is None:
        return _ly_h(s)
    out, last = [], 0
    for m in LY_BRACKET_RX.finditer(s):
        out += [_ly_bare(s[last:m.start()], notes), notes.mark(ID_RX.findall(m.group(1)))]
        last = m.end()
    return "".join(out) + _ly_bare(s[last:], notes)


def _ly_bare(s, notes) -> str:
    out, last = [], 0
    for m in ID_RX.finditer(s):
        out += [_ly_h(s[last:m.start()]), notes.mark([m.group(1)])]
        last = m.end()
    return "".join(out) + _ly_h(s[last:])


def _ly_cites(it, L, notes=None) -> str:
    cites = list(it.get("cites") or []) if isinstance(it.get("cites"), list) else []
    if not cites:
        return ""
    if notes is not None:
        return f'<p class="src">{notes.mark(cites)}</p>'
    return f'<p class="src"><span class="lab">{_ly_h(label(L, "ui.sources"))}</span> {_ly_h(", ".join(cites))}</p>'


def _ly_value(v, notes=None) -> str:
    """A field value of any shape as HTML: text, a list, a table (list of lists) or a mapping."""
    if isinstance(v, list):
        if v and all(isinstance(r, list) for r in v):
            rows = "".join("<tr>" + "".join(f"<td>{_ly_text(x, notes)}</td>" for x in r) + "</tr>" for r in v)
            return f"<table><tbody>{rows}</tbody></table>"
        return "<ul>" + "".join(f"<li>{_ly_value(x, notes)}</li>" for x in v) + "</ul>"
    if isinstance(v, dict):
        main = next((v[k] for k in ("text", "label", "narration", "title") if isinstance(v.get(k), str)), None)
        if main is not None:
            pre = " ".join(str(v[k]) for k in ("offset", "date", "time") if v.get(k))
            return (f"<b>{_ly_h(pre)}</b> " if pre else "") + _ly_text(main, notes)
        return "; ".join(f"{_ly_h(k)}: {_ly_text(x, notes)}" for k, x in v.items() if not isinstance(x, (list, dict)))
    if isinstance(v, bool):
        return "✓" if v else ""
    return _ly_text(v, notes)


def _ly_blocks(it, L, notes=None, view="full", skip=()) -> str:
    """An item as labelled blocks in its kind's field order (P4-5): the title as a heading, the rest labelled."""
    out = []
    for b in item_blocks(it, L, view=view):
        if b.field in skip:
            continue
        if b.role == "title":
            out.append(f"<h2>{_ly_text(b.value, notes)}</h2>")
        elif b.role == "table" and isinstance(b.value, list):
            out.append(_ly_table(it, L, notes))
        elif b.role == "graph":
            continue
        elif b.field in ("edges", "nodes"):
            continue
        else:
            out.append(f'<div class="blk"><p class="lab">{_ly_h(b.label)}</p>{_ly_para(b.value, notes)}</div>')
    if it.get("kind") == "graph":
        out.append(_ly_graph_text(it))
    return "".join(out)


def _ly_para(v, notes=None) -> str:
    return _ly_value(v, notes) if isinstance(v, (list, dict)) else f"<p>{_ly_value(v, notes)}</p>"


def _ly_graph_text(it) -> str:
    names = {n.get("id"): n.get("label") for n in it.get("nodes") or [] if isinstance(n, dict)}
    links = [f'{_ly_h(names.get(e.get("from"), e.get("from")))} → {_ly_h(names.get(e.get("to"), e.get("to")))}'
             + (f' ({_ly_h(e["label"])})' if e.get("label") else "")
             for e in it.get("edges") or [] if isinstance(e, dict)]
    return "<ul>" + "".join(f"<li>{x}</li>" for x in links) + "</ul>" if links else ""


def _ly_table(it, L, notes=None) -> str:
    cols = it.get("columns") or []
    head = "".join(f'<th scope="col">{_ly_h(c)}</th>' for c in cols)
    rows = "".join("<tr>" + "".join(f"<td>{_ly_text(x, notes)}</td>" for x in r) + "</tr>"
                   for r in it.get("rows") or [] if isinstance(r, list))
    return f'<table><thead><tr>{head}</tr></thead><tbody>{rows}</tbody></table>'


def _ly_qr(ctx: RenderContext, url: str) -> str:
    """The QR code for url, or "" and one note in ctx.notes when the link is too long for any QR version."""
    from .qr import qr_svg
    try:
        return f'<figure class="qr">{qr_svg(url, module_px=2)}</figure>'
    except ValueError:                    # qrcodegen's DataTooLongError
        note = QR_TOO_LONG.format(layout=ctx.layout, chars=len(url))
        if not any(n.startswith(note.split(":", 2)[0] + ": QR codes left out") for n in ctx.notes):
            ctx.notes.append(note)
        return ""


def _ly_item_url(ctx: RenderContext, item_id: str) -> str:
    return f'{ctx.base_url.split("#", 1)[0]}#i/{quote(str(item_id), safe="-_.")}'


def _ly_brand(ctx: RenderContext) -> str:
    b = ctx.brand
    if not b:
        return ""
    logo = (f'<img class="logo" alt="" src="data:{_ly_h(b.logo_mime)};base64,'
            f'{base64.b64encode(b.logo_bytes).decode("ascii")}">' if b.logo_bytes and b.logo_mime else "")
    org = f'<span class="org">{_ly_h(b.organisation)}</span>' if b.organisation else ""
    return f'<span class="brand">{logo}{org}</span>' if logo or org else ""


# ----------------------------------------------------------------------------- the page frame

def page(html_body: str, ctx: RenderContext, cls: str = "") -> str:
    """One printed page block: the pack title, the status phrase, the DRAFT label for a draft (and the learner
    banner and translation note when they apply), the body, then the short footer. Task 21 reuses it."""
    pack = ctx.pack
    status = _ly_h(status_line(pack.get("status") or ""))
    draft = f'<p class="draft" role="note">{DRAFT_LABEL}</p>' if is_draft(ctx.eh) else ""
    extra = ([LEARNER_BANNER] if ctx.view == "learner" else []) + translation_lines(pack)
    notes = "".join(f'<p class="status">{_ly_h(x)}</p>' for x in extra)
    return (f'<section class="page{" " + cls if cls else ""}"><header class="ph">{_ly_brand(ctx)}'
            f'<p class="ptitle">{_ly_h(pack.get("title"))}</p>{draft}<p class="status">{status}</p>{notes}</header>'
            f'<div class="pbody">{html_body}</div>'
            f'<footer class="pf"><p>{status} · {_ly_h(LAYOUT_FOOTER)}</p></footer></section>')


def _ly_doc(ctx: RenderContext, pages: list, size: str, L: dict) -> str:
    pack = ctx.pack
    lang = pack.get("lang") or "en"
    tdir = pack.get("dir") or text_dir(L)
    open_tag = f'<html lang="{_ly_h(lang)}">' if tdir == "ltr" else f'<html lang="{_ly_h(lang)}" dir="{_ly_h(tdir)}">'
    css = (DASHBOARD_ASSETS / "layouts.css").read_text(encoding="utf-8")
    title = _ly_h(pack.get("title"))
    hint = _ly_h(label(L, "ui.layout.print_hint"))
    return (f'<!doctype html>{open_tag}<head><meta charset="utf-8">'
            f'<meta name="viewport" content="width=device-width,initial-scale=1">\n<title>{title}</title>\n<style>\n'
            f'@page{{size:{size}}}\n{PAGE_FOOTER_CSS}\n{css}</style></head>\n'
            f'<body class="ly-{_ly_h(ctx.layout)} size-{size.split()[0]}"><main>\n'
            f'<header class="doc noprint"><h1>{title}</h1><p>{hint}</p></header>\n'
            + "\n".join(pages) + "\n</main></body></html>\n")


# ----------------------------------------------------------------------------- the printed items

def _ly_card_pages(ctx, L, notes=None, kinds=LY_CARD_KINDS):
    """(pages, other): a page per card, toolbox and test point and per scenario inject; other counts the rest."""
    pages, other = [], 0
    for s in ctx.pack.get("sections") or []:
        for it in s.get("items") or []:
            k = it.get("kind")
            injects = it.get("injects") if k == "scenario" and isinstance(it.get("injects"), list) else []
            if k in kinds:
                body = _ly_toolbox_body(it, L, notes) if k == "toolbox" else _ly_blocks(it, L, notes, ctx.view)
                bodies = [body + _ly_cites(it, L, notes)]
            elif injects:
                bodies = [_ly_inject_body(it, inj, L, notes) for inj in injects if isinstance(inj, dict)]
            else:
                other += 1
                continue
            for b in bodies:
                qr = _ly_qr(ctx, _ly_item_url(ctx, it["id"])) if ctx.base_url else ""
                pages.append(page(f'<article class="lcard" id="i-{_ly_h(it["id"])}">{b}{qr}</article>', ctx))
    return pages, other


def _ly_toolbox_body(it, L, notes) -> str:
    """The five parts of a toolbox talk, in order (Task 16's kind)."""
    dur = (f'<p class="badge">{_ly_h(label(L, "f.duration"))}: {_ly_h(it["duration"])}</p>'
           if it.get("duration") else "")
    parts = "".join(f'<div class="blk"><h2 class="part">{n}. {_ly_h(label(L, key))}</h2>'
                    f'{_ly_para(it.get(f), notes)}</div>'
                    for n, (f, key) in enumerate(LY_TOOLBOX_PARTS, 1) if it.get(f))
    return dur + parts


def _ly_inject_body(it, inj, L, notes) -> str:
    dec = (f'<div class="blk"><p class="lab">{_ly_h(label(L, "ui.layout.inject_decision"))}</p>'
           f'<p class="big">{_ly_text(inj["decision"], notes)}</p></div>' if inj.get("decision") else "")
    return (f'<h2>{_ly_h(label(L, "ui.layout.inject", offset=inj.get("offset") or ""))}</h2>'
            f'<div class="blk"><p class="lab">{_ly_h(label(L, "f.situation"))}</p>'
            f'<p>{_ly_text(it.get("situation"), notes)}</p></div>'
            f'<p class="big">{_ly_text(inj.get("text"), notes)}</p>{dec}')


def _ly_closing(ctx, other, L) -> list:
    if not other:
        return []
    bottom = "".join(f"<li>{_ly_text(b.get('text'))}</li>" for b in ctx.pack.get("bottom_line") or []
                     if isinstance(b, dict))
    qr = _ly_qr(ctx, ctx.base_url) if ctx.base_url else ""
    return [page(f'<h2>{_ly_h(label(L, "ui.bottom_line"))}</h2><ul>{bottom}</ul>'
                 f'<p class="more">{_ly_h(MORE_IN_PACK.format(n=other))}</p>{qr}', ctx, "closing")]


def _ly_endnotes(ctx, notes, L) -> list:
    F = {f.get("id"): f for f in ctx.w.get("findings") or [] if isinstance(f, dict)}
    E = ctx.w.get("evidence") or {}
    lis = []
    for x, n in notes.ids.items():
        if x in F:
            f = F[x]
            text = (f'{x}: {f.get("label") or ""} · L{f.get("level") or ""} · '
                    f'{label(L, "ui.rating", rating="" if f.get("rating") is None else f.get("rating"))}')
        elif x in E:
            text = f'{x}: {(E[x] or {}).get("type") or ""}'
        else:
            text = x
        lis.append(f'<li id="en-{n}">{_ly_h(text)}</li>')
    if not lis:
        return []
    return [page(f'<h2>{_ly_h(label(L, "ui.layout.endnotes"))}</h2><ol class="endnotes">{"".join(lis)}</ol>', ctx)]


def delivery_record_html(ctx: RenderContext) -> str:
    """The printable delivery record (P3-15): the distribution.csv columns after pack and audience, with blank rows
    for the organisation to fill in by hand. Roles only: there is no column for a personal name."""
    L = _ly_labels(ctx)
    head = "".join(f'<th scope="col">{_ly_h(c)}</th>' for c in DELIVERY_COLUMNS)
    rows = ("<tr>" + "<td></td>" * len(DELIVERY_COLUMNS) + "</tr>") * DELIVERY_ROWS
    return (f'<h2>{_ly_h(label(L, "ui.layout.delivery_record"))}</h2>'
            f'<p>{_ly_h(label(L, "ui.layout.delivery_for", pack=ctx.pack.get("pack"), audience=ctx.pack.get("audience")))}</p>'
            f'<p class="m">{_ly_h(label(L, "ui.layout.delivery_note"))}</p>'
            f'<table class="record"><thead><tr>{head}</tr></thead><tbody>{rows}</tbody></table>')


# ----------------------------------------------------------------------------- the six layouts

def _ly_cards(ctx, L):
    pages, other = _ly_card_pages(ctx, L)
    if not pages and not other:
        pages = [page("", ctx)]
    return pages + _ly_closing(ctx, other, L), ctx.paper if ctx.paper in PAPERS else "A4"


def _ly_field(ctx, L):
    notes = _LyNotes()
    pages, other = _ly_card_pages(ctx, L, notes)
    return (pages + _ly_closing(ctx, other, L) + _ly_endnotes(ctx, notes, L)
            + [page(delivery_record_html(ctx), ctx, "record")]), "A4"


def _ly_toolbox(ctx, L):
    pages, _ = _ly_card_pages(ctx, L, kinds=("toolbox",))
    pages = [p for p in pages if 'class="part"' in p]          # injects are not toolbox talks
    if not pages:
        return None, "no toolbox items"
    return pages + [page(delivery_record_html(ctx), ctx, "record")], "A4"


def _ly_checklist(ctx, L):
    groups = []
    hold = _ly_h(label(L, "f.hold_point"))
    for s in ctx.pack.get("sections") or []:
        lis = []
        for it in s.get("items") or []:
            k = it.get("kind")
            if k not in LY_CHECK_KINDS:
                continue
            text = it.get("text") if k == "check" else it.get("requirement")
            hp = f'<span class="hold">{hold}</span> ' if it.get("hold_point") else ""
            when = f' <span class="when">({_ly_h(it["when"])})</span>' if it.get("when") else ""
            more = (f'<p class="m">{_ly_h(label(L, "f.sample"))}: {_ly_text(it.get("sample"))}</p>'
                    if k == "test_point" and it.get("sample") else "")
            lis.append(f'<li class="ck"><span class="box" aria-hidden="true">☐</span> '
                       f'<span>{hp}{_ly_text(text)}{when}{more}</span></li>')
        if lis:
            groups.append(f'<div class="group"><h2>{_ly_h(s.get("heading"))}</h2><ul class="checks">{"".join(lis)}'
                          f'</ul><p class="checkline">{_ly_h(CHECK_LINE)}</p></div>')
    if not groups:
        return None, "no check or test_point items"
    return [page("".join(groups), ctx, "flow")], "A4"


def _ly_poster(ctx, L):
    pack = ctx.pack
    bottom = "".join(f"<li>{_ly_text(b.get('text'))}</li>" for b in pack.get("bottom_line") or [] if isinstance(b, dict))
    tiles = []
    for s in pack.get("sections") or []:
        for it in s.get("items") or []:
            if it.get("kind") == "card" and len(tiles) < POSTER_MAX:
                tiles.append(f'<div class="tile"><h3>{_ly_text(it.get("title"))}</h3>'
                             f'<p>{_ly_text(it.get("good_looks_like"))}</p></div>')
            elif it.get("kind") == "learning" and len(tiles) < POSTER_MAX:
                tiles.append(f'<div class="tile"><h3>{_ly_text(it.get("lesson"))}</h3></div>')
    evs = sorted_events([e for s in pack.get("sections") or [] for it in s.get("items") or []
                         if it.get("kind") == "timeline" and isinstance(it.get("events"), list)
                         for e in it["events"] if isinstance(e, dict) and isinstance(e.get("date"), str)])
    tl_html = ""
    if evs:                                 # every timeline item of the pack, as one horizontal line
        inc = _pack_incident_date(pack, ctx.w)
        lis = "".join(f'<li class="ev"><time>{_ly_h(event_when(e, inc, L))}</time><p>{_ly_text(e.get("text"))}</p></li>'
                      for e in evs[:POSTER_EVENTS])
        rest = (f'<p class="m">{_ly_h(label(L, "ui.layout.more_events", n=len(evs) - POSTER_EVENTS))}</p>'
                if len(evs) > POSTER_EVENTS else "")
        tl_html = f'<ol class="htl">{lis}</ol>{rest}'
    qr = _ly_qr(ctx, ctx.base_url) if ctx.base_url else ""
    body = (f'<h2 class="ptitle-big">{_ly_h(pack.get("title"))}</h2><div class="bl"><h3>'
            f'{_ly_h(label(L, "ui.bottom_line"))}</h3><ul>{bottom}</ul>{qr}</div>'
            f'<div class="tiles">{"".join(tiles)}</div>{tl_html}')
    return [page(body, ctx, "poster")], "A3 landscape"


def _ly_paper(ctx, L):
    pack, eh = ctx.pack, ctx.eh
    inc = pack.get("incident") or {}
    fields = (ctx.w.get("incident") or {}).get("fields") or {}
    incident = " · ".join(str(x) for x in (inc.get("title") or fields.get("Incident Title"),
                                           inc.get("date") or fields.get("Date")) if x)
    reading = L.get("ui.reading_time", READING_TIME).format(n=reading_minutes(pack))
    handling = "".join(f"<p>{_ly_h(x)}</p>" for x in _handling_lines(eh, ctx.share, markdown=False))
    cover = (f'<h2 class="cover-title">{_ly_h(pack.get("title"))}</h2>'
             f'<p><span class="lab">{_ly_h(label(L, "f.audience"))}</span> {_ly_h(pack.get("audience"))}</p>'
             + (f'<p><span class="lab">{_ly_h(label(L, "ui.incident"))}</span> {_ly_h(incident)}</p>' if incident else "")
             + f'<div class="handling">{handling}</div><p class="reading">{_ly_h(reading)}</p>')
    secs = pack.get("sections") or []
    items = [it for s in secs for it in s.get("items") or []]
    decisions = "".join(f'<div class="decision">{_ly_blocks(it, L, view=ctx.view)}{_ly_cites(it, L)}</div>'
                        for it in items if it.get("kind") == "decision")
    bottom = "".join(f"<li>{_ly_text(b.get('text'))}</li>" for b in pack.get("bottom_line") or [] if isinstance(b, dict))
    body = [f'<h2>{_ly_h(label(L, "ui.layout.decisions_requested"))}</h2>{decisions}'
            f'<h3>{_ly_h(label(L, "ui.bottom_line"))}</h3><ul>{bottom}</ul>']
    annex_kinds = ("decision", "question", "table", "indicator")
    n = 0
    for s in secs:
        rest = [it for it in s.get("items") or [] if it.get("kind") not in annex_kinds]
        if not rest:
            continue
        n += 1
        intro = f"<p>{_ly_text(s['intro'])}</p>" if s.get("intro") else ""
        paras = "".join(f'<div class="np"><span class="num">{n}.{j}</span><div>{_ly_paper_item(it, L, ctx.view)}'
                        f'{_ly_cites(it, L)}</div></div>' for j, it in enumerate(rest, 1))
        body.append(f'<h3 class="np-head"><span class="num">{n}.</span> {_ly_h(s.get("heading"))}</h3>{intro}{paras}')
    pages = [page(cover, ctx, "cover"), page("".join(body), ctx, "flow")]
    qs = [it for it in items if it.get("kind") == "question"]
    if qs:
        qh = "".join(f'<div class="np"><span class="num">A.{j}</span><div>{_ly_blocks(it, L, view=ctx.view)}'
                     f'{_ly_cites(it, L)}</div></div>' for j, it in enumerate(qs, 1))
        pages.append(page(f'<h2>{_ly_h(label(L, "ui.layout.annex_a"))}</h2>{qh}', ctx, "flow"))
    tb = [it for it in items if it.get("kind") in ("table", "indicator")]
    if tb:
        th = "".join(f'<div class="np"><span class="num">B.{j}</span><div>'
                     + (_ly_table(it, L) if it.get("kind") == "table" else _ly_blocks(it, L, view=ctx.view))
                     + f'{_ly_cites(it, L)}</div></div>' for j, it in enumerate(tb, 1))
        pages.append(page(f'<h2>{_ly_h(label(L, "ui.layout.annex_b"))}</h2>{th}', ctx, "flow"))
    return pages, "A4"


def _ly_paper_item(it, L, view) -> str:
    if it.get("kind") == "para":
        return "".join(f"<p>{_ly_text(p)}</p>" for p in re.split(r"\n\s*\n", str(it.get("text") or "")) if p.strip())
    if it.get("kind") == "timeline":
        evs = sorted_events([e for e in it.get("events") or [] if isinstance(e, dict) and e.get("date")])
        return "<ul>" + "".join(f'<li><b>{_ly_h(e["date"])}</b> {_ly_text(e.get("text"))}</li>' for e in evs) + "</ul>"
    return _ly_blocks(it, L, view=view)


LAYOUT_BUILDERS = {"cards": _ly_cards, "field": _ly_field, "toolbox": _ly_toolbox, "checklist": _ly_checklist,
            "poster": _ly_poster, "paper": _ly_paper}


def render_layout(ctx: RenderContext) -> list:
    """The Output of ctx.layout: [<pack>.<layout>[.learner].html], or [] plus a NOTHING_TO_WRITE note in ctx.notes
    when the pack has nothing that layout prints. The learner view (P4-9) is applied here."""
    if ctx.layout not in LAYOUT_BUILDERS:
        raise ValueError(f"layout must be one of {', '.join(LAYOUTS)}, not {ctx.layout!r}")
    if ctx.view == "learner":
        ctx = dataclasses.replace(ctx, pack=learner_view(ctx.pack))          # the same notes list
    L = _ly_labels(ctx)
    pages, size = LAYOUT_BUILDERS[ctx.layout](ctx, L)
    if pages is None:
        ctx.notes.append(NOTHING_TO_WRITE.format(fmt=ctx.layout, why=size))
        return []
    doc = _ly_doc(ctx, pages, size, L)
    return [Output(output_name(ctx.pack["pack"], "html", layout=ctx.layout, view=ctx.view), doc, doc)]


def base_url_arg(text: str) -> str:
    """argparse type for --base-url: an http(s) URL, the published pack page the QR codes link to."""
    import argparse
    t = str(text).strip()
    if not re.match(r"^https?://[^\s/]+", t, re.I) or any(c.isspace() for c in t):
        raise argparse.ArgumentTypeError(f"needs an http:// or https:// URL, not {text!r}")
    return t
