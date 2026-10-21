"""The SCORM 1.2 package (Ruling P4-11): `<pack>.scorm.zip` holds `imsmanifest.xml` (ADL SCORM 1.2 CAM), `index.html`
(the learner view of the pack, then the quiz) and `scorm.js` (dashboard_assets/scorm.js), which finds the LMS API,
grades the quiz in the browser and reports `cmi.core.score.raw` (0 to 100) and `cmi.core.lesson_status`.

The pass mark is 80% of the scored questions; with none the status is `completed`. Typed questions are scored; a
question without a type is shown as "reflect", unscored (P4-10). SCORM always builds from the learner view (P4-9),
so --view does not change it, but the answer keys travel inside index.html as data, as in any client-graded SCORM
quiz: render() hands this format the full pack (OWN_LEARNER_VIEW)."""
from __future__ import annotations

import dataclasses
import html
import json
import re

from .. import BRAND, DRAFT_LABEL
from ..dashboard.data import DASHBOARD_ASSETS
from ..handling import handling_lines, is_draft, status_line
from . import Output, output_name, register, RenderContext
from .fields import item_blocks, learner_view
from .labels import label, load_labels, text_dir
from .layouts import page, page_css
from .ooxml import xml_text, zip_bytes

SM_PASS = 80                                  # percent of the scored questions (P4-11)
SM_TYPES = ("single", "multi", "truefalse", "short")
SM_JS = DASHBOARD_ASSETS / "scorm.js"
_SM_CP_NS = "http://www.imsproject.org/xsd/imscp_rootv1p1p2"
_SM_ADLCP_NS = "http://www.adlnet.org/xsd/adlcp_rootv1p2"
_SM_MD_NS = "http://www.imsglobal.org/xsd/imsmd_rootv1p2p1"
_SM_JS_LABELS = ("ui.scorm.result", "ui.scorm.passed", "ui.scorm.failed", "ui.scorm.completed", "ui.scorm.no_lms")
_SM_CSS = """
.quiz fieldset,.quiz .q{border:1px solid var(--line);border-radius:4px;margin:0 0 10pt;padding:6pt 10pt}
.quiz legend,.quiz .qs{font-weight:600;padding:0 4pt}
.quiz .opt{display:flex;gap:6pt;align-items:baseline;margin:3pt 0}
.quiz input[type=text],.quiz textarea{width:100%;font:inherit;padding:3pt 4pt;border:1px solid var(--mut);border-radius:3px}
.quiz button{font:inherit;font-weight:600;color:#fff;background:var(--accent);border:0;border-radius:4px;padding:6pt 14pt;cursor:pointer}
.quiz button:disabled{background:var(--mut);cursor:default}
.quiz :focus-visible{outline:3px solid var(--accent);outline-offset:2px}
.quiz .result{font-weight:700;margin-top:8pt}
"""


def _sm_h(s) -> str:
    return html.escape("" if s is None else str(s), quote=True)


def _sm_line(s) -> str:
    return " ".join(("" if s is None else str(s)).split())


def _sm_labels(ctx: RenderContext) -> dict:
    return ctx.labels or load_labels(ctx.pack.get("lang") or "en")


# ----------------------------------------------------------------------------- the questions and the key

def _sm_question(full: dict, learn: dict, n: int) -> dict:
    """One quiz question: its scoring type (None for reflect), the options the learner sees and its key entry."""
    typ = full.get("type") if full.get("type") in SM_TYPES else None
    ops = [o for o in full.get("options") or [] if isinstance(o, dict)] if isinstance(full.get("options"), list) else []
    key = None
    if typ == "short":
        accept = [_sm_line(o.get("text")) for o in ops if _sm_line(o.get("text"))]
        key = {"accept": accept} if accept else None
    elif typ:
        right = [i for i, o in enumerate(ops) if o.get("correct")]
        key = {"correct": right} if right else None
    if key is None:
        typ = None                                    # nothing to score it against: a reflect question
    shown = [o for o in learn.get("options") or [] if isinstance(o, dict)] if isinstance(learn.get("options"), list) else []
    qid = str(full.get("id") or f"q{n}")
    return {"id": qid, "n": n, "type": typ, "stem": _sm_line(full.get("question")),
            "options": [_sm_line(o.get("text")) for o in shown], "key": dict({"id": qid, "type": typ}, **(key or {}))}


def _sm_walk(full: dict, learn: dict):
    """(sections, questions): the learner sections with every question item taken out, and the questions in order.
    learner_view keeps the order of sections and items, so the full and learner packs walk in step."""
    sections, qs = [], []
    for fs, ls in zip(full.get("sections") or [], learn.get("sections") or []):
        if not (isinstance(fs, dict) and isinstance(ls, dict)):
            continue
        items = []
        for fi, li in zip(fs.get("items") or [], ls.get("items") or []):
            if not (isinstance(fi, dict) and isinstance(li, dict)):
                continue
            if fi.get("kind") == "question":
                qs.append(_sm_question(fi, li, len(qs) + 1))
            else:
                items.append(li)
        sections.append((ls.get("heading") or "", items))
    return sections, qs


def _sm_json(obj) -> str:
    """JSON safe inside a script element: no <, > or & can close it or open a comment."""
    t = json.dumps(obj, ensure_ascii=False, sort_keys=True)
    return t.replace("<", "\\u003c").replace(">", "\\u003e").replace("&", "\\u0026")


# ----------------------------------------------------------------------------- the page

def _sm_value(v) -> str:
    if isinstance(v, list):
        if v and all(isinstance(r, list) for r in v):
            return "<table><tbody>" + "".join("<tr>" + "".join(f"<td>{_sm_h(x)}</td>" for x in r) + "</tr>"
                                              for r in v) + "</tbody></table>"
        return "<ul>" + "".join(f"<li>{_sm_value(x)}</li>" for x in v) + "</ul>"
    if isinstance(v, dict):
        main = next((v[k] for k in ("text", "label", "narration", "title") if isinstance(v.get(k), str)), None)
        if main is not None:
            pre = " ".join(str(v[k]) for k in ("offset", "date", "time") if v.get(k))
            return (f"<b>{_sm_h(pre)}</b> " if pre else "") + _sm_h(main)
        return "; ".join(f"{_sm_h(k)}: {_sm_h(x)}" for k, x in v.items() if not isinstance(x, (list, dict)))
    if isinstance(v, bool):
        return "✓" if v else ""
    return _sm_h(v)


def _sm_item(it: dict, L: dict) -> str:
    out = []
    for b in item_blocks(it, L, view="learner"):
        if b.role == "title":
            out.append(f"<h3>{_sm_h(b.value)}</h3>")
        elif b.role == "graph" or b.field in ("nodes", "edges", "columns"):    # columns: the header of rows' table
            continue
        elif b.role == "table" and isinstance(b.value, list):
            head = "".join(f'<th scope="col">{_sm_h(c)}</th>' for c in it.get("columns") or [])
            rows = "".join("<tr>" + "".join(f"<td>{_sm_h(x)}</td>" for x in r) + "</tr>"
                           for r in b.value if isinstance(r, list))
            out.append(f"<table><thead><tr>{head}</tr></thead><tbody>{rows}</tbody></table>")
        else:
            val = _sm_value(b.value)
            out.append(f'<div class="blk"><p class="lab">{_sm_h(b.label)}</p>'
                       + (val if isinstance(b.value, list) else f"<p>{val}</p>") + "</div>")
    cites = it.get("cites") if isinstance(it.get("cites"), list) else []
    if cites:
        out.append(f'<p class="src"><span class="lab">{_sm_h(label(L, "ui.sources"))}</span> '
                   f'{_sm_h(", ".join(map(str, cites)))}</p>')
    return f'<div class="item">{"".join(out)}</div>'


def _sm_content(pack: dict, sections: list, L: dict) -> str:
    out = []
    bl = [b for b in pack.get("bottom_line") or [] if isinstance(b, dict) and b.get("text")]
    if bl:
        out.append(f'<h2>{_sm_h(label(L, "ui.bottom_line"))}</h2><ul>'
                   + "".join(f"<li>{_sm_h(b['text'])}</li>" for b in bl) + "</ul>")
    for heading, items in sections:
        if items:
            out.append(f"<h2>{_sm_h(heading)}</h2>" + "".join(_sm_item(it, L) for it in items))
    return "".join(out)


def _sm_quiz_q(q: dict, L: dict) -> str:
    n, qid = q["n"], _sm_h(q["id"])
    stem = f"{n}. {_sm_h(q['stem'])}"
    if q["type"] is None:
        return (f'<div class="q reflect"><label class="qs" for="sm-{n}">{stem}</label>'
                f'<p class="m" id="sm-{n}-hint">{_sm_h(label(L, "ui.scorm.reflect"))}</p>'
                f'<textarea id="sm-{n}" name="sm-{n}" rows="4" aria-describedby="sm-{n}-hint"></textarea></div>')
    head = f'<fieldset data-q="{qid}" data-type="{q["type"]}"><legend>{stem}</legend>'
    if q["type"] == "short":
        return (head + f'<label for="sm-{n}">{_sm_h(label(L, "ui.scorm.your_answer"))}</label>'
                f'<input type="text" id="sm-{n}" name="sm-{n}" autocomplete="off"></fieldset>')
    kind = "checkbox" if q["type"] == "multi" else "radio"
    hint = label(L, "ui.scorm.choose_any" if kind == "checkbox" else "ui.scorm.choose_one")
    opts = "".join(f'<div class="opt"><input type="{kind}" name="sm-{n}" id="sm-{n}-{j}" value="{j}">'
                   f'<label for="sm-{n}-{j}">{_sm_h(t)}</label></div>' for j, t in enumerate(q["options"]))
    return head + f'<p class="m">{_sm_h(hint)}</p>{opts}</fieldset>'


def _sm_quiz(qs: list, L: dict) -> str:
    scored = any(q["type"] for q in qs)
    intro = label(L, "ui.scorm.intro", **{"pass": SM_PASS}) if scored else label(L, "ui.scorm.no_questions")
    button = (f'<button type="button" id="sm-submit">{_sm_h(label(L, "ui.scorm.submit"))}</button>' if scored else
              f'<button type="button" id="sm-finish">{_sm_h(label(L, "ui.scorm.finish"))}</button>')
    return (f'<div class="quiz"><h2 id="sm-quiz-h">{_sm_h(label(L, "ui.scorm.quiz"))}</h2><p>{_sm_h(intro)}</p>'
            f'<form id="sm-form" aria-labelledby="sm-quiz-h">{"".join(_sm_quiz_q(q, L) for q in qs)}{button}</form>'
            '<p id="sm-result" class="result" role="status" aria-live="polite"></p></div>')


def _sm_page(ctx: RenderContext, lctx: RenderContext, sections: list, qs: list, L: dict) -> str:
    pack = lctx.pack
    pages = [page(_sm_content(pack, sections, L), lctx), page(_sm_quiz(qs, L), lctx, "flow")]
    last, tail = pages[-1].rsplit("</footer></section>", 1)                      # BRAND once, at the end (P4-20)
    pages[-1] = f'{last}<p class="brandline">{_sm_h(BRAND)}</p></footer></section>{tail}'
    lang = pack.get("lang") or "en"
    tdir = pack.get("dir") or text_dir(L)
    dir_attr = "" if tdir == "ltr" else f' dir="{_sm_h(tdir)}"'
    css = (DASHBOARD_ASSETS / "layouts.css").read_text(encoding="utf-8")
    data = {"pass": SM_PASS, "questions": [q["key"] for q in qs if q["type"]],
            "labels": {k: L[k] for k in _SM_JS_LABELS}}
    title = _sm_h(pack.get("title"))
    return (f'<!doctype html><html lang="{_sm_h(lang)}"{dir_attr}><head><meta charset="utf-8">'
            f'<meta name="viewport" content="width=device-width,initial-scale=1">\n<title>{title}</title>\n<style>\n'
            f'{page_css(ctx, "A4")}\n{css}{_SM_CSS}</style></head>\n<body class="scorm size-A4"><main>\n'
            f'<header class="doc"><h1>{title}</h1></header>\n' + "\n".join(pages) + "\n</main>\n"
            f'<script type="application/json" id="sm-key">{_sm_json(data)}</script>\n'
            '<script src="scorm.js"></script>\n</body></html>\n')


# ----------------------------------------------------------------------------- the manifest

def _sm_head(ctx: RenderContext) -> list:
    lines = [status_line(ctx.pack["status"])]
    if ctx.eh:
        if is_draft(ctx.eh):
            lines.append(DRAFT_LABEL)
        lines += handling_lines(ctx.eh)
    return [_sm_line(x) for x in lines + [BRAND]]


def _sm_manifest(ctx: RenderContext, scored: bool) -> str:
    pack = ctx.pack
    ident = re.sub(r"[^A-Za-z0-9_.-]", "_", str(pack["pack"]))
    lang = xml_text(pack.get("lang") or "en")
    title = xml_text(_sm_line(pack.get("title")) or pack["pack"])
    mastery = f"<adlcp:masteryscore>{SM_PASS}</adlcp:masteryscore>" if scored else ""
    return ('<?xml version="1.0" encoding="UTF-8"?>\n'
            f'<manifest identifier="MANIFEST-{ident}" version="1.0" xmlns="{_SM_CP_NS}" '
            f'xmlns:adlcp="{_SM_ADLCP_NS}" xmlns:imsmd="{_SM_MD_NS}">\n'
            "<metadata><schema>ADL SCORM</schema><schemaversion>1.2</schemaversion>"
            f'<imsmd:lom><imsmd:general><imsmd:title><imsmd:langstring xml:lang="{lang}">{title}</imsmd:langstring>'
            f'</imsmd:title><imsmd:description><imsmd:langstring xml:lang="{lang}">'
            + xml_text(" | ".join(_sm_head(ctx))) + "</imsmd:langstring></imsmd:description></imsmd:general>"
            "</imsmd:lom></metadata>\n"
            '<organizations default="ORG-1"><organization identifier="ORG-1">'
            f'<title>{title}</title><item identifier="ITEM-1" identifierref="RES-1" isvisible="true">'
            f"<title>{title}</title>{mastery}</item></organization></organizations>\n"
            '<resources><resource identifier="RES-1" type="webcontent" adlcp:scormtype="sco" href="index.html">'
            '<file href="index.html"/><file href="scorm.js"/></resource></resources>\n</manifest>\n')


def render_scorm(ctx: RenderContext) -> list:
    """[<pack>.scorm.zip]. ctx.pack is the full pack (render() leaves it whole for this format): the page shows its
    learner view, and the key comes from the full one."""
    L = _sm_labels(ctx)
    lctx = dataclasses.replace(ctx, pack=learner_view(ctx.pack), view="learner")     # the same notes list
    sections, qs = _sm_walk(ctx.pack, lctx.pack)
    index = _sm_page(ctx, lctx, sections, qs, L)
    manifest = _sm_manifest(ctx, any(q["type"] for q in qs))
    seen = html.unescape(re.sub(r"<[^>]+>", " ", re.sub(r"<script\b.*?</script>", " ", index, flags=re.S)))
    keys = [a for q in qs for a in q["key"].get("accept", [])]
    guard = "\n".join([" ".join(seen.split())] + keys + _sm_head(ctx))
    parts = {"imsmanifest.xml": manifest, "index.html": index, "scorm.js": SM_JS.read_bytes()}
    return [Output(output_name(ctx.pack["pack"], "scorm.zip"), zip_bytes(parts), guard)]


register("scorm", render_scorm,
         help="<pack>.scorm.zip: a SCORM 1.2 package (learner view and a quiz graded in the browser) for an LMS")
