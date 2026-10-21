"""The email digest (L4-16, Ruling P4-24): <pack>.email.html and its plain-text twin <pack>.email.txt. The HTML is
styled by inline `style=` attributes only: no <script>, <style>, <link> or <img>, no class names, and no URL except
--base-url. Both files are built from one list of lines, so they carry the same words; the sections' items are
added in order while the page stays under EM_BUDGET bytes, and each section says how many it left out."""
from __future__ import annotations

import html as std_html
import re
import textwrap

from .. import BRAND, DRAFT_LABEL
from ..handling import is_draft, status_line
from ..pack.markdown import (_handling_lines as _em_handling, _pack_incident_date as _em_incident_date, coverage,
                             event_when, sorted_events)
from ..pack.schema import cited_ids, TOP_PRINT_LINE
from . import LEARNER_BANNER, MORE_IN_PACK, Output, output_name, READING_TIME, register, translation_lines
from .fields import item_blocks, reading_minutes
from .labels import label, load_labels, text_dir

EM_BUDGET = 90_000                  # bytes of HTML the sections may fill (P4-24); the hard limit is 100,000
EM_WIDTH = 78                       # columns of the plain-text twin
EM_RESERVE = 600                    # bytes kept for one section's heading and its "more items" line
EM_FONT = "font-family:Arial,Helvetica,sans-serif;"
EM_INK, EM_MUTED, EM_ACCENT, EM_LINE = "#1a1a1a", "#555555", "#0b5c8a", "#cfd8dc"
EM_CTRL_RX = re.compile(r"[\x00-\x08\x0e-\x1f\x7f]")
EM_URL_RX = re.compile(r"^https?://[^\s<>\"']+$", re.I)

# One line of the digest, before it becomes HTML or text:
#   ("h", text)  an item heading        ("p", text)    a paragraph        ("kv", label, text)  a labelled value
#   ("ul", [text, ...]) a list          ("tbl", cols, rows)  a table      ("cite", text)  the sources of an item


def _em_clean(v) -> str:
    """One string: control characters dropped, every run of white space (even \\x0b) one space."""
    return " ".join(EM_CTRL_RX.sub("", str(v)).split())


def _em_cites(cites) -> str:
    return f" [{'; '.join(cites)}]" if cites else ""


def _em_value_texts(v) -> list:
    """A field value as a list of one-line strings (list of texts, rows joined with ' | ', dicts as 'k: v')."""
    if isinstance(v, str):
        return [_em_clean(v)]
    if isinstance(v, dict):
        return [_em_clean(f"{k}: {x}") for k, x in v.items()]
    out = []
    for x in v if isinstance(v, list) else [v]:
        if isinstance(x, list):
            out.append(_em_clean(" | ".join(map(str, x))))
        elif isinstance(x, dict):
            out.append(_em_clean("; ".join(f"{k}: {y}" for k, y in x.items() if k != "cites")))
        else:
            out.append(_em_clean(x))
    return out


def _em_item_lines(it: dict, L: dict, inc_date, view: str) -> list:
    """The digest lines of one item. The kinds with a plain reading (para, check, table, timeline, graph) have their
    own; every other kind, known or not, reads from its field roles (P4-5)."""
    def t(key, **fmt):
        return label(L, key, **fmt)

    k, cites = it.get("kind"), it.get("cites") or []
    src = _em_cites(cites)
    if k == "para":
        return [("p", _em_clean(it.get("text", "")) + src)]
    if k == "check":
        when = f" ({_em_clean(it['when'])})" if it.get("when") else ""
        return [("p", f"[ ] {_em_clean(it.get('text', ''))}{when}{src}")]
    out = []
    if k == "table" and isinstance(it.get("columns"), list) and isinstance(it.get("rows"), list):
        out.append(("tbl", [_em_clean(c) for c in it["columns"]],
                    [[_em_clean(c) for c in r] for r in it["rows"] if isinstance(r, list)]))
    elif k == "timeline" and isinstance(it.get("events"), list):
        out.append(("ul", [_em_clean(f"{event_when(e, inc_date, L)}: {e['text']}") for e in sorted_events(it["events"])]))
    elif k == "graph" and isinstance(it.get("nodes"), list) and isinstance(it.get("edges"), list):
        lab = {n["id"]: n["label"] for n in it["nodes"]}
        out.append(("p", t("ui.graph_summary", nodes=len(it["nodes"]), links=len(it["edges"]))))
        out.append(("ul", [_em_clean(f"{lab.get(e['from'], e['from'])} -> {lab.get(e['to'], e['to'])}"
                                    + (f" ({e['label']})" if e.get("label") else "")) for e in it["edges"]]))
    else:
        for b in item_blocks(it, L, view=view):
            if b.role == "title" and isinstance(b.value, str):
                out.append(("h", _em_clean(b.value)))
            elif isinstance(b.value, str):
                out.append(("kv", b.label, _em_clean(b.value)))
            else:
                out += [("kv", b.label, ""), ("ul", _em_value_texts(b.value))]
    if cites:
        out.append(("cite", f"{t('ui.sources')}: {'; '.join(cites)}"))
    return out


# ----------------------------------------------------------------------------- HTML

def _em_h(s) -> str:
    return std_html.escape(str(s), quote=True)


def _em_html_line(ln: tuple) -> str:
    k = ln[0]
    base = f"{EM_FONT}color:{EM_INK};"
    if k == "h":
        return f'<h3 style="{base}font-size:16px;margin:16px 0 4px 0;">{_em_h(ln[1])}</h3>'
    if k == "p":
        return f'<p style="{base}font-size:15px;line-height:1.5;margin:0 0 8px 0;">{_em_h(ln[1])}</p>'
    if k == "cite":
        return f'<p style="{EM_FONT}color:{EM_MUTED};font-size:12px;margin:0 0 10px 0;">{_em_h(ln[1])}</p>'
    if k == "kv":
        val = f" {_em_h(ln[2])}" if ln[2] else ""
        return (f'<p style="{base}font-size:14px;line-height:1.5;margin:0 0 4px 0;"><strong style="{base}">'
                f'{_em_h(ln[1])}:</strong>{val}</p>')
    if k == "ul":
        lis = "".join(f'<li style="{base}font-size:14px;line-height:1.5;margin:0 0 2px 0;">{_em_h(x)}</li>' for x in ln[1])
        return f'<ul style="margin:0 0 8px 0;padding:0 0 0 20px;">{lis}</ul>'
    cell = f"{base}font-size:13px;border:1px solid {EM_LINE};padding:4px 6px;text-align:left;vertical-align:top;"
    head = "".join(f'<th style="{cell}background-color:#eef3f6;">{_em_h(c)}</th>' for c in ln[1])
    rows = "".join("<tr>" + "".join(f'<td style="{cell}">{_em_h(c)}</td>' for c in r) + "</tr>" for r in ln[2])
    return (f'<table style="border-collapse:collapse;width:100%;margin:0 0 10px 0;"><tr>{head}</tr>{rows}</table>')


def _em_html_h2(text: str) -> str:
    return (f'<h2 style="{EM_FONT}color:{EM_ACCENT};font-size:19px;margin:24px 0 8px 0;'
            f'border-bottom:2px solid {EM_ACCENT};padding-bottom:4px;">{_em_h(text)}</h2>')


def _em_html_p(text: str, *, muted=False, bold=False, size=14) -> str:
    colour = EM_MUTED if muted else EM_INK
    weight = "font-weight:bold;" if bold else ""
    return f'<p style="{EM_FONT}color:{colour};font-size:{size}px;{weight}line-height:1.5;margin:0 0 6px 0;">{_em_h(text)}</p>'


# ----------------------------------------------------------------------------- plain text

def _em_wrap(text: str, first: str = "", rest: str = None) -> list:
    rest = first if rest is None else rest
    return textwrap.wrap(text, EM_WIDTH, initial_indent=first, subsequent_indent=rest, break_long_words=True,
                         break_on_hyphens=False) or [first.rstrip()]


def _em_txt_line(ln: tuple) -> list:
    k = ln[0]
    if k == "h":
        return [""] + _em_wrap(ln[1], "* ", "  ")
    if k in ("p", "cite"):
        return _em_wrap(ln[1]) + ([""] if k == "cite" else [])
    if k == "kv":
        return _em_wrap(f"{ln[1]}: {ln[2]}".rstrip(), "", "  ")
    if k == "ul":
        return [x for t in ln[1] for x in _em_wrap(t, "  - ", "    ")]
    rows = [ln[1]] + ln[2]
    return [x for r in rows for x in _em_wrap(" | ".join(r), "  - ", "    ")] + [""]


def _em_txt_h2(text: str) -> list:
    return ["", *_em_wrap(text), "-" * min(EM_WIDTH, max(3, len(text)))]


# ----------------------------------------------------------------------------- the digest

def _em_head_lines(ctx, pack, L, eh) -> tuple:
    """(plain lines for the header block in order, the reading-time text). Each plain line is (text, kind) with
    kind "title", "draft", "handling" or "meta"."""
    mins = reading_minutes(pack)
    rt = label(L, "ui.reading_time", n=mins) if "ui.reading_time" in L else READING_TIME.format(n=mins)
    rows = [(pack["title"], "title")]
    if is_draft(eh):
        rows.append((DRAFT_LABEL, "draft"))
    rows += [(x, "handling") for x in _em_handling(eh, ctx.share, markdown=False)]
    rows.append((status_line(pack["status"]), "meta"))
    rows += [(x, "meta") for x in translation_lines(pack)]
    if ctx.view == "learner":
        rows.append((LEARNER_BANNER, "meta"))
    inc = pack.get("incident") or {}
    fields = ctx.w.get("incident", {}).get("fields", {})
    rows.append((" - ".join(str(x) for x in (pack.get("audience"), inc.get("title") or fields.get("Incident Title"),
                                             inc.get("date") or fields.get("Date")) if x), "meta"))
    rows.append((rt, "meta"))
    return [(_em_clean(t), k) for t, k in rows if t], rt


def render_email(ctx) -> list:
    """The email digest of ctx.pack: [<pack>.email.html, <pack>.email.txt]. A shared copy is built from ctx.pack and
    ctx.w, which are already masked, and shows no run slug."""
    pack, L = ctx.pack, ctx.labels or load_labels(ctx.pack.get("lang") or "en")
    eh = ctx.eh
    url = ctx.base_url
    if url and not EM_URL_RX.match(url):
        ctx.notes.append("email: --base-url must be an http:// or https:// address; the link is left out")
        url = None
    head, _ = _em_head_lines(ctx, pack, L, eh)
    cov = coverage(ctx.w, pack)
    fids, eids = cited_ids(pack)
    cited_text = ", ".join(fids + eids)
    cov_lines = [f"This pack cites {cov['cited']} of {cov['relevant']} relevant findings.",
                 TOP_PRINT_LINE.format(x=cov["top_cited"], y=cov["top_relevant"]) + "."]
    inc_date = _em_incident_date(pack, ctx.w)
    lang = pack.get("lang") or "en"
    tdir = pack.get("dir") or text_dir(L)
    t_bottom, t_cited, t_cov = label(L, "ui.bottom_line"), label(L, "ui.email.cited"), label(L, "ui.coverage")
    t_full = label(L, "ui.email.full_pack")

    bottom = [_em_clean(b["text"]) + _em_cites(b.get("cites")) for b in pack["bottom_line"]]
    # the part of the page that is always shown: its size sets how many items the sections may add
    fixed_html = (len(_em_html_p(pack["title"])) + sum(len(_em_html_p(x)) for x in bottom) + len(cited_text)
                  + len(_em_html_h2(t_cited)) + 3000 + len(url or "") * 2)
    budget = EM_BUDGET - fixed_html - EM_RESERVE * len(pack["sections"])
    used = 0

    sec_html, sec_txt = [], []
    for s in pack["sections"]:
        h, tx = [_em_html_h2(s["heading"])], _em_txt_h2(_em_clean(s["heading"]))
        if s.get("intro"):
            h.append(_em_html_p(_em_clean(s["intro"]), muted=True))
            tx += _em_wrap(_em_clean(s["intro"]))
        shown, prev, full = 0, None, True
        for it in s["items"]:
            lines = ([("h", _em_clean(it["group"]))] if it.get("group") and it["group"] != prev else [])
            lines += _em_item_lines(it, L, inc_date, ctx.view)
            html_part = "".join(_em_html_line(x) for x in lines)
            if full and used + len(html_part.encode("utf-8")) <= budget:
                used += len(html_part.encode("utf-8"))
                h.append(html_part)
                tx += [y for x in lines for y in _em_txt_line(x)]
                shown += 1
                prev = it.get("group")
            else:
                full = False                                          # items stay in order: no gaps in the middle
        left = len(s["items"]) - shown
        if left:
            more = MORE_IN_PACK.format(n=left)
            h.append(_em_html_p(more, muted=True))
            tx += ["", *_em_wrap(more)]
        sec_html.append("".join(h))
        sec_txt += tx

    # ---- HTML
    top = []
    for text, kind in head:
        if kind == "title":
            top.append(f'<h1 style="{EM_FONT}color:{EM_INK};font-size:24px;line-height:1.25;margin:0 0 8px 0;">{_em_h(text)}</h1>')
        elif kind == "draft":
            top.append(f'<p style="{EM_FONT}background-color:#fff3cd;color:#5c4400;font-size:14px;font-weight:bold;'
                       f'padding:6px 10px;margin:0 0 8px 0;border:1px solid #e0c36a;">{_em_h(text)}</p>')
        else:
            top.append(_em_html_p(text, muted=True, size=13))
    if url:
        top.append(f'<p style="{EM_FONT}font-size:15px;margin:8px 0 0 0;"><a href="{_em_h(url)}" '
                   f'style="color:{EM_ACCENT};font-weight:bold;">{_em_h(t_full)}</a></p>')
    body = "".join(top) + _em_html_h2(t_bottom)
    body += '<ul style="margin:0 0 8px 0;padding:0 0 0 20px;">' + "".join(
        f'<li style="{EM_FONT}color:{EM_INK};font-size:15px;line-height:1.5;margin:0 0 6px 0;">{_em_h(b)}</li>'
        for b in bottom) + "</ul>"
    body += "".join(sec_html)
    body += _em_html_h2(t_cited) + _em_html_p(cited_text, muted=True, size=12)
    body += _em_html_h2(t_cov) + "".join(_em_html_p(x) for x in cov_lines)
    body += (f'<p style="{EM_FONT}color:{EM_MUTED};font-size:12px;border-top:1px solid {EM_LINE};padding-top:10px;'
             f'margin:24px 0 0 0;">{_em_h(BRAND)}</p>')
    page = (f'<!doctype html><html lang="{_em_h(lang)}" dir="{_em_h(tdir)}"><head><meta charset="utf-8">'
            f'<meta name="viewport" content="width=device-width,initial-scale=1"><title>{_em_h(_em_clean(pack["title"]))}'
            f'</title></head><body style="margin:0;padding:0;background-color:#f4f6f8;">'
            f'<table role="presentation" width="100%" style="border-collapse:collapse;background-color:#f4f6f8;">'
            f'<tr><td align="center" style="padding:16px;"><table role="presentation" width="640" '
            f'style="border-collapse:collapse;max-width:640px;width:100%;background-color:#ffffff;">'
            f'<tr><td style="padding:24px;">{body}</td></tr></table></td></tr></table></body></html>\n')

    # ---- plain text
    txt = []
    for text, kind in head:
        txt += _em_wrap(text) + ([""] if kind == "title" else [])
    if url:
        txt += ["", f"{t_full}:", url]
    txt += _em_txt_h2(t_bottom)
    txt += [x for b in bottom for x in _em_wrap(b, "- ", "  ")]
    txt += sec_txt
    txt += _em_txt_h2(t_cited) + _em_wrap(cited_text)
    txt += _em_txt_h2(t_cov) + [x for c in cov_lines for x in _em_wrap(c)]
    txt += ["", *_em_wrap(BRAND)]
    text = "\n".join(txt) + "\n"
    return [Output(output_name(pack["pack"], "email.html", view=ctx.view), page, text),
            Output(output_name(pack["pack"], "email.txt", view=ctx.view), text, text)]


register("email", render_email, help="<pack>.email.html (inline styles, no images, under 100 KB) and "
         "<pack>.email.txt (78 columns)")
