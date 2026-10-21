"""The question exports (Rulings P4-10 and P4-12): GIFT (`<pack>.gift.txt`), QTI 2.1 (`<pack>.qti.zip`) and the quiz CSV
(`<pack>.quiz.csv`). They are data formats: they keep the answer keys the LMS needs, whatever the view.

A typed question (`single`, `multi`, `truefalse`, `short`) is graded. A question without a type is a discussion question:
an essay in GIFT, an ungraded extended-text item in QTI, and the type `discussion` in the CSV."""
from __future__ import annotations

import csv
import io
import re

from .. import BRAND, DRAFT_LABEL
from ..handling import handling_lines, is_draft, status_line
from . import Output, output_name, register
from .labels import label, load_labels
from .ooxml import xml_text, zip_bytes

_QZ_GIFT_SPECIAL = re.compile(r"([\\~=#{}:])")
_QZ_CSV_OPTIONS = 6
_QZ_CSV_HEADER = ["id", "type", "question", "option_1", "option_2", "option_3", "option_4", "option_5", "option_6",
                  "correct", "why", "cites"]
_QZ_TRUE = ("true", "t", "yes", "y")
_QZ_FALSE = ("false", "f", "no", "n")
_QZ_QTI_NS = "http://www.imsglobal.org/xsd/imsqti_v2p1"
_QZ_CP_NS = "http://www.imsglobal.org/xsd/imscp_v1p1"
_QZ_LOM_NS = "http://ltsc.ieee.org/xsd/LOM"
_QZ_XSI = "http://www.w3.org/2001/XMLSchema-instance"


def gift_escape(s) -> str:
    """s with the GIFT special characters `~ = # { } :` (and the backslash itself) escaped with a backslash."""
    t = _QZ_GIFT_SPECIAL.sub(r"\\\1", "" if s is None else str(s))
    return "\\" + t if t.startswith("%") else t                 # a leading % would read as an answer weight


def _qz_line(s) -> str:
    """One line of text: every run of whitespace collapsed to a single space."""
    return " ".join(("" if s is None else str(s)).split())


def _qz_questions(pack: dict) -> list:
    """Every `question` item of the pack, in order. `ops` is the typed options (empty for a discussion question)."""
    out = []
    for s in pack.get("sections") or []:
        for it in s.get("items") or [] if isinstance(s, dict) else []:
            if not (isinstance(it, dict) and it.get("kind") == "question"):
                continue
            typ = it.get("type") if it.get("type") in ("single", "multi", "truefalse", "short") else None
            ops = [o for o in it.get("options") or [] if isinstance(o, dict)] if typ else []
            if typ and not ops:
                typ = None                              # a typed question with no usable options exports as discussion
            out.append({"id": it.get("id") or f"q{len(out) + 1}", "type": typ, "stem": _qz_line(it.get("question")),
                        "ops": ops, "why": _qz_line(it.get("why")), "cites": list(it.get("cites") or [])})
    return out


def _qz_labels(ctx) -> dict:
    return ctx.labels or load_labels(ctx.pack.get("lang") or "en")


def _qz_questions_or_note(ctx, fmt: str):
    qs = _qz_questions(ctx.pack)
    if not qs:
        ctx.notes.append(label(_qz_labels(ctx), "ui.quiz.none", format=fmt))
    return qs


def _qz_head(ctx) -> list:
    """The status, handling, DRAFT and BRAND lines every export carries."""
    lines = [status_line(ctx.pack["status"])]
    if ctx.eh:
        if is_draft(ctx.eh):
            lines.append(DRAFT_LABEL)
        lines += handling_lines(ctx.eh)
    lines.append(BRAND)
    return [_qz_line(x) for x in lines]


# ----------------------------------------------------------------------------------------------------------- GIFT

def _qz_pct(x: float) -> str:
    return f"{x:.5f}".rstrip("0").rstrip(".")


def _qz_gift_answer(q: dict) -> str:
    typ, ops = q["type"], q["ops"]
    if typ is None:
        return ""
    if typ == "truefalse":
        right = next((o for o in ops if o.get("correct")), ops[0])
        txt = _qz_line(right.get("text")).lower()
        wanted_true = txt in _QZ_TRUE or (txt not in _QZ_FALSE and right is ops[0])
        return "T" if wanted_true else "F"
    if typ == "short":
        return "\n".join("=" + gift_escape(_qz_line(o["text"])) for o in ops)
    if typ == "single":
        return "\n".join(("=" if o.get("correct") else "~") + gift_escape(_qz_line(o["text"])) for o in ops)
    n = sum(1 for o in ops if o.get("correct")) or 1                          # multi: weighted, summing to 100
    return "\n".join("~%" + (_qz_pct(100 / n) if o.get("correct") else "-100") + "%" + gift_escape(_qz_line(o["text"]))
                     for o in ops)


def render_gift(ctx) -> list:
    qs = _qz_questions_or_note(ctx, "gift")
    if not qs:
        return []
    out = ["// " + x for x in _qz_head(ctx)] + [""]
    for q in qs:
        ans = _qz_gift_answer(q)
        fb = ("####" + gift_escape(q["why"])) if q["why"] else ""
        inner = (ans + fb) if ans in ("", "T", "F") else "\n" + ans + ("\n" + fb if fb else "") + "\n"
        out.append(f"::{gift_escape(q['id'])}:: {gift_escape(q['stem'])} {{{inner}}}")
        out.append("")
    text = "\n".join(out)
    return [Output(output_name(ctx.pack["pack"], "gift.txt"), text, text)]


# ------------------------------------------------------------------------------------------------------------ QTI

def _qz_ident(raw: str, used: set) -> str:
    """An XML NCName that is unique in the package."""
    base = re.sub(r"[^A-Za-z0-9_.-]", "_", raw or "q")
    if not re.match(r"[A-Za-z_]", base):
        base = "q" + base
    ident, n = base, 2
    while ident in used:
        ident, n = f"{base}_{n}", n + 1
    used.add(ident)
    return ident


def _qz_comment(lines: list) -> str:
    """An XML comment; `--` may not appear inside one."""
    return "<!-- " + xml_text(" | ".join(lines)).replace("--", "- -") + " -->"


def _qz_qti_item(q: dict, ident: str, head: list, draft: bool) -> str:
    typ, ops = q["type"], q["ops"]
    title = ("DRAFT: " if draft else "") + (q["stem"][:80] or ident)
    decl, body, proc = "", "", ""
    stem = xml_text(q["stem"])
    if typ in ("single", "truefalse", "multi"):
        ids = [f"{ident}_c{i}" for i in range(1, len(ops) + 1)]
        right = [i for i, o in zip(ids, ops) if o.get("correct")]
        multiple = typ == "multi"
        decl = (f'<responseDeclaration identifier="RESPONSE" cardinality="{"multiple" if multiple else "single"}" '
                'baseType="identifier"><correctResponse>'
                + "".join(f"<value>{i}</value>" for i in right) + "</correctResponse></responseDeclaration>")
        choices = "".join(f'<simpleChoice identifier="{i}">{xml_text(_qz_line(o["text"]))}</simpleChoice>'
                          for i, o in zip(ids, ops))
        body = (f'<choiceInteraction responseIdentifier="RESPONSE" shuffle="false" '
                f'maxChoices="{0 if multiple else 1}"><prompt>{stem}</prompt>{choices}</choiceInteraction>')
        proc = '<responseProcessing template="http://www.imsglobal.org/question/qti_v2p1/rptemplates/match_correct"/>'
    elif typ == "short":
        answers = [_qz_line(o["text"]) for o in ops]
        decl = ('<responseDeclaration identifier="RESPONSE" cardinality="single" baseType="string"><correctResponse>'
                f"<value>{xml_text(answers[0])}</value></correctResponse><mapping defaultValue=\"0\">"
                + "".join(f'<mapEntry mapKey="{xml_text(a)}" mappedValue="1"/>' for a in answers)
                + "</mapping></responseDeclaration>")
        body = f'<p>{stem}</p><p><textEntryInteraction responseIdentifier="RESPONSE" expectedLength="30"/></p>'
        proc = '<responseProcessing template="http://www.imsglobal.org/question/qti_v2p1/rptemplates/map_response"/>'
    else:                                                       # a discussion question: ungraded extended text
        decl = '<responseDeclaration identifier="RESPONSE" cardinality="single" baseType="string"/>'
        body = f'<p>{stem}</p><extendedTextInteraction responseIdentifier="RESPONSE" expectedLines="6"/>'
    outcome = '<outcomeDeclaration identifier="SCORE" cardinality="single" baseType="float"/>' if typ else ""
    return ('<?xml version="1.0" encoding="UTF-8"?>\n' + _qz_comment(head) + "\n"
            f'<assessmentItem xmlns="{_QZ_QTI_NS}" xmlns:xsi="{_QZ_XSI}" '
            f'xsi:schemaLocation="{_QZ_QTI_NS} http://www.imsglobal.org/xsd/qti/qtiv2p1/imsqti_v2p1.xsd" '
            f'identifier="{ident}" title="{xml_text(title)}" adaptive="false" timeDependent="false">\n'
            f"{decl}{outcome}<itemBody>{body}</itemBody>{proc}</assessmentItem>\n")


def render_qti(ctx) -> list:
    qs = _qz_questions_or_note(ctx, "qti")
    if not qs:
        return []
    lang = ctx.pack.get("lang") or "en"
    head, draft, used = _qz_head(ctx), bool(ctx.eh and is_draft(ctx.eh)), set()
    parts, resources = {}, []
    for q in qs:
        ident = _qz_ident(q["id"], used)
        href = f"items/{ident}.xml"
        parts[href] = _qz_qti_item(q, ident, head, draft)
        resources.append(f'<resource identifier="RES_{ident}" type="imsqti_item_xmlv2p1" href="{href}">'
                         f'<file href="{href}"/></resource>')
    parts["imsmanifest.xml"] = (
        '<?xml version="1.0" encoding="UTF-8"?>\n' + _qz_comment(head) + "\n"
        f'<manifest xmlns="{_QZ_CP_NS}" identifier="MANIFEST_{_qz_ident(ctx.pack["pack"], set())}">'
        "<metadata><schema>QTIv2.1 Package</schema><schemaversion>1.0.0</schemaversion>"
        f'<lom:lom xmlns:lom="{_QZ_LOM_NS}"><lom:general><lom:description><lom:string language="{xml_text(lang)}">'
        + xml_text(" | ".join(head)) + "</lom:string></lom:description></lom:general></lom:lom></metadata>"
        "<organizations/><resources>" + "".join(resources) + "</resources></manifest>\n")
    guard = "\n".join(head + [t for q in qs for t in [q["stem"], q["why"]] + [_qz_line(o["text"]) for o in q["ops"]]])
    return [Output(output_name(ctx.pack["pack"], "qti.zip"), zip_bytes(parts), guard)]


# ------------------------------------------------------------------------------------------------------- quiz CSV

def render_quiz_csv(ctx) -> list:
    from ..actions import _csv_cell                           # the formula-led-cell guard of the actions export (X20)
    qs = _qz_questions_or_note(ctx, "quiz-csv")
    if not qs:
        return []
    buf = io.StringIO()
    wr = csv.writer(buf, lineterminator="\n")
    wr.writerow(_QZ_CSV_HEADER)
    for q in qs:
        ops = q["ops"]
        if len(ops) > _QZ_CSV_OPTIONS:
            ctx.notes.append(label(_qz_labels(ctx), "ui.quiz.cut", id=q["id"], n=_QZ_CSV_OPTIONS))
        shown = [_qz_line(o["text"]) for o in ops[:_QZ_CSV_OPTIONS]]
        correct = [str(i) for i, o in enumerate(ops[:_QZ_CSV_OPTIONS], 1) if o.get("correct")]
        row = [q["id"], q["type"] or "discussion", q["stem"]] + shown + [""] * (_QZ_CSV_OPTIONS - len(shown)) \
            + [";".join(correct), q["why"], "; ".join(q["cites"])]
        wr.writerow([_csv_cell(c) for c in row])
    text = buf.getvalue()
    return [Output(output_name(ctx.pack["pack"], "quiz.csv"), text, text)]


register("gift", render_gift, kind="data", help="<pack>.gift.txt: the questions as GIFT, for Moodle")
register("qti", render_qti, kind="data", help="<pack>.qti.zip: the questions as an IMS QTI 2.1 package")
register("quiz-csv", render_quiz_csv, kind="data", help="<pack>.quiz.csv: one row per question, answer key included")
