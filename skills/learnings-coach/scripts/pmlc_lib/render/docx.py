"""The docx format (L4-03, L4-20; Rulings P4-26, P4-7, P4-9): a Word document built with the standard library only.

A4 with 2 cm margins; the styles Title, Heading1, Heading2, Normal, TableGrid and Caption. The title, with the status
line directly under it, then the learner banner, the DRAFT line, the handling lines and the reading time; the bottom
line; one Heading1 per section; coverage; gaps and limits. Tables are real tables with the header row repeated, and
every table is followed by an empty paragraph (Word merges adjacent tables). Each item's citations become one
endnote; the footer of every page holds the status phrase, the brand and the page number, and a draft's header holds
DRAFT. With the paper layout, <pack>.paper.docx is also written: a board paper with a cover, "Decisions requested",
numbered paragraphs and annexes.

write_docx(blocks, ctx) is the shared builder (the register renderer calls it too): blocks are (kind, payload, cites)
tuples, see DX_KINDS."""
from __future__ import annotations

import io
import re
import struct
import zipfile
import xml.etree.ElementTree as ET

from .. import BRAND, DRAFT_LABEL, STATUS_PHRASE
from ..handling import is_draft, status_line
from ..pack.markdown import _handling_lines as _dx_handling_lines, _knowable as _dx_knowable
from ..pack.markdown import _pack_incident_date as _dx_incident_date, coverage, event_when, lint_ok_notes, sorted_events
from ..pack.schema import cited_ids, TOP_PRINT_LINE
from ..register.check import norm_hoc
from . import LEARNER_BANNER, Output, output_name, READING_TIME, register, translation_lines
from .fields import item_blocks, reading_minutes
from .labels import label, load_labels, LOCALE_RX, text_dir
from .ooxml import app_props, content_types, core_props, rels, xml_text, zip_bytes

# The block kinds write_docx takes. The first seven are the contract's; "note" (a Caption line) and "pagebreak"
# (payload ignored) are the renderer's own.
#   title, status, heading1, heading2, note: str
#   para: str, or a list of segments; a segment is a str or a (text, fmt) pair, fmt "" | "b" | "i" | "bi"
#   list: a list of entries (str or segments), or {"items": [...], "ordered": bool}
#   table: {"columns": [str], "rows": [[cell]]}; the header row repeats on every page
DX_KINDS = ("title", "status", "heading1", "heading2", "para", "list", "table", "note", "pagebreak")
DX_W = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
DX_R = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
DX_WP = "http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing"
DX_A = "http://schemas.openxmlformats.org/drawingml/2006/main"
DX_PIC = "http://schemas.openxmlformats.org/drawingml/2006/picture"
DX_NS = f'xmlns:w="{DX_W}" xmlns:r="{DX_R}"'
DX_DECL = '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n'
DX_ACCENT = "0077B6"                       # the pack page's --acc
DX_PAGE_W, DX_PAGE_H, DX_MARGIN = 11906, 16838, 1134      # A4 and 2 cm, in twips
DX_TEXT_W = DX_PAGE_W - 2 * DX_MARGIN
DX_DRAFT_COLOUR = '<w:color w:val="A15C00"/>'
DX_LOGO_H = 540000                          # 1.5 cm in EMU
DX_CT = {
    "document": "application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml",
    "styles": "application/vnd.openxmlformats-officedocument.wordprocessingml.styles+xml",
    "settings": "application/vnd.openxmlformats-officedocument.wordprocessingml.settings+xml",
    "numbering": "application/vnd.openxmlformats-officedocument.wordprocessingml.numbering+xml",
    "endnotes": "application/vnd.openxmlformats-officedocument.wordprocessingml.endnotes+xml",
    "header": "application/vnd.openxmlformats-officedocument.wordprocessingml.header+xml",
    "footer": "application/vnd.openxmlformats-officedocument.wordprocessingml.footer+xml",
    "core": "application/vnd.openxmlformats-package.core-properties+xml",
    "app": "application/vnd.openxmlformats-officedocument.extended-properties+xml",
}
DX_TEXT_PARTS_RX = re.compile(r"word/(header\d*|document|endnotes|footer\d*)\.xml")
DX_PART_ORDER = ("header", "document", "endnotes", "footer")


# ----------------------------------------------------------------------------- the builder

def _dx_run(text, fmt="", rtl=False, extra="") -> str:
    """One run (or several, split at line breaks): text escaped, \\n as <w:br/>, \\t as <w:tab/>."""
    props = ("<w:b/>" if "b" in fmt else "") + ("<w:i/>" if "i" in fmt else "") + extra + ("<w:rtl/>" if rtl else "")
    rpr = f"<w:rPr>{props}</w:rPr>" if props else ""
    body = []
    for n, line in enumerate(str(text).split("\n")):
        if n:
            body.append("<w:br/>")
        for m, chunk in enumerate(line.split("\t")):
            if m:
                body.append("<w:tab/>")
            if chunk:
                body.append(f'<w:t xml:space="preserve">{xml_text(chunk)}</w:t>')
    return f"<w:r>{rpr}{''.join(body)}</w:r>"


def _dx_segments(payload) -> list:
    if isinstance(payload, (list, tuple)):
        return [(s, "") if isinstance(s, str) else (str(s[0]), s[1] if len(s) > 1 else "") for s in payload]
    return [("" if payload is None else str(payload), "")]


class _DxWriter:
    """The state of one document: the direction, the endnotes and the ordered-list numbering instances."""

    def __init__(self, ctx, cite_line):
        self.rtl = _dx_dir(ctx) == "rtl"
        self.cite_line = cite_line
        self.notes = []                      # [(id, [lines])]
        self.ordered = 0                     # ordered lists so far (each gets its own numbering instance)

    def ppr(self, style=None, num=None, extra="") -> str:
        bits = (f'<w:pStyle w:val="{style}"/>' if style else "") + extra
        bits += (f'<w:numPr><w:ilvl w:val="0"/><w:numId w:val="{num}"/></w:numPr>' if num else "")
        bits += "<w:bidi/>" if self.rtl else ""
        return f"<w:pPr>{bits}</w:pPr>" if bits else ""

    def note_ref(self, cites) -> str:
        """The endnote reference run for these IDs ("" when there are none)."""
        ids = list(dict.fromkeys(x for x in cites or [] if isinstance(x, str) and x))
        if not ids:
            return ""
        nid = len(self.notes) + 1
        self.notes.append((nid, [self.cite_line(x) for x in ids]))
        return (f'<w:r><w:rPr><w:vertAlign w:val="superscript"/>{"<w:rtl/>" if self.rtl else ""}</w:rPr>'
                f'<w:endnoteReference w:id="{nid}"/></w:r>')

    def para(self, payload, style=None, cites=None, num=None, extra_ppr="") -> str:
        runs = "".join(_dx_run(t, f, self.rtl) for t, f in _dx_segments(payload) if t != "")
        return f"<w:p>{self.ppr(style, num, extra_ppr)}{runs}{self.note_ref(cites)}</w:p>"

    def list(self, payload, cites) -> str:
        items = payload.get("items", []) if isinstance(payload, dict) else list(payload or [])
        num = 1
        if isinstance(payload, dict) and payload.get("ordered"):
            self.ordered += 1
            num = 1 + self.ordered
        out = [self.para(x, cites=cites if n == len(items) - 1 else None, num=num) for n, x in enumerate(items)]
        return "".join(out)

    def cell(self, v, width, bold=False, cites=None) -> str:
        text = "; ".join(map(str, v)) if isinstance(v, list) else ("" if v is None else str(v))
        return (f'<w:tc><w:tcPr><w:tcW w:w="{width}" w:type="dxa"/></w:tcPr>'
                f'{self.para([(text, "b" if bold else "")], cites=cites)}</w:tc>')

    def table(self, payload, cites) -> str:
        cols = [str(c) for c in payload.get("columns") or []]
        rows = [list(r) if isinstance(r, (list, tuple)) else [r] for r in payload.get("rows") or []]
        n = max([len(cols)] + [len(r) for r in rows] + [1])
        cols += [""] * (n - len(cols))
        width = DX_TEXT_W // n
        grid = "".join(f'<w:gridCol w:w="{width}"/>' for _ in range(n))
        head = "".join(self.cell(c, width, True, cites if i == 0 else None) for i, c in enumerate(cols))
        body = "".join("<w:tr>" + "".join(self.cell(c, width) for c in r + [""] * (n - len(r))) + "</w:tr>"
                       for r in rows)
        bidi = "<w:bidiVisual/>" if self.rtl else ""
        return (f'<w:tbl><w:tblPr><w:tblStyle w:val="TableGrid"/>{bidi}<w:tblW w:w="5000" w:type="pct"/>'
                f'<w:tblLook w:val="04A0" w:firstRow="1" w:lastRow="0" w:firstColumn="0" w:lastColumn="0" '
                f'w:noHBand="0" w:noVBand="1"/></w:tblPr><w:tblGrid>{grid}</w:tblGrid>'
                f"<w:tr><w:trPr><w:tblHeader/></w:trPr>{head}</w:tr>{body}</w:tbl><w:p/>")

    def block(self, kind, payload, cites) -> str:
        if kind == "title":
            return self.para(payload, "Title", cites)
        if kind in ("status", "note"):
            return self.para(payload, "Caption", cites)
        if kind in ("heading1", "heading2"):
            return self.para(payload, "Heading1" if kind == "heading1" else "Heading2", cites)
        if kind == "para":
            return self.para(payload, None, cites)
        if kind == "list":
            return self.list(payload, cites)
        if kind == "table":
            return self.table(payload if isinstance(payload, dict) else {"rows": payload}, cites)
        if kind == "pagebreak":
            return '<w:p><w:r><w:br w:type="page"/></w:r></w:p>'
        raise ValueError(f"docx block kind must be one of {', '.join(DX_KINDS)}, not {kind!r}")


def _dx_dir(ctx) -> str:
    pack = ctx.pack or {}
    if pack.get("dir") in ("ltr", "rtl"):
        return pack["dir"]
    return text_dir(_dx_labels(ctx))


def _dx_labels(ctx) -> dict:
    if ctx.labels is not None:
        return ctx.labels
    try:
        return load_labels((ctx.pack or {}).get("lang") or "en")
    except ValueError:                                          # check-pack reports a bad lang
        return load_labels("en")


def _dx_cite_line(w):
    """ID -> its endnote line: 'ID: label · L<level> · rating <r>' for a finding, 'ID: type' for evidence."""
    F = {f["id"]: f for f in (w or {}).get("findings") or [] if isinstance(f, dict) and "id" in f}
    E = (w or {}).get("evidence") or {}

    def line(x):
        if x in F:
            f = F[x]
            return f"{x}: {f.get('label', '')} · L{f.get('level', '?')} · rating {f.get('rating', '?')}"
        if x in E and isinstance(E[x], dict):
            return f"{x}: {E[x].get('type', '')}"
        return x
    return line


def _dx_image_size(data: bytes, mime: str) -> tuple:
    """(width, height) in pixels of a PNG or JPEG, or (1, 1) when it cannot be read."""
    try:
        if data[:8] == b"\x89PNG\r\n\x1a\n":
            return struct.unpack(">II", data[16:24])
        if data[:2] == b"\xff\xd8":
            i = 2
            while i + 9 < len(data):
                if data[i] != 0xFF:
                    i += 1
                    continue
                marker, size = data[i + 1], struct.unpack(">H", data[i + 2:i + 4])[0]
                if marker in (0xC0, 0xC1, 0xC2):
                    h, w = struct.unpack(">HH", data[i + 5:i + 9])
                    return w, h
                i += 2 + size
    except struct.error:
        pass
    return 1, 1


def _dx_logo(brand, alt: str = "Organisation logo") -> tuple:
    """(paragraph XML, media part name, bytes, extension) for the brand's logo, or None. alt: its description."""
    if not brand or not getattr(brand, "logo_bytes", None):
        return None
    ext = "jpeg" if "jp" in (brand.logo_mime or "") else "png"
    w, h = _dx_image_size(brand.logo_bytes, brand.logo_mime or "")
    cy = DX_LOGO_H
    cx = max(1, int(cy * (w or 1) / (h or 1)))
    name = f"logo.{ext}"
    drawing = (f'<w:r><w:drawing><wp:inline distT="0" distB="0" distL="0" distR="0"><wp:extent cx="{cx}" cy="{cy}"/>'
               f'<wp:docPr id="1" name="Logo" descr="{xml_text(alt)}"/><wp:cNvGraphicFramePr>'
               f'<a:graphicFrameLocks xmlns:a="{DX_A}" noChangeAspect="1"/></wp:cNvGraphicFramePr>'
               f'<a:graphic xmlns:a="{DX_A}"><a:graphicData uri="{DX_PIC}"><pic:pic xmlns:pic="{DX_PIC}">'
               f'<pic:nvPicPr><pic:cNvPr id="0" name="{name}"/><pic:cNvPicPr/></pic:nvPicPr>'
               '<pic:blipFill><a:blip r:embed="rIdLogo"/><a:stretch><a:fillRect/></a:stretch></pic:blipFill>'
               f'<pic:spPr><a:xfrm><a:off x="0" y="0"/><a:ext cx="{cx}" cy="{cy}"/></a:xfrm>'
               '<a:prstGeom prst="rect"><a:avLst/></a:prstGeom></pic:spPr></pic:pic></a:graphicData></a:graphic>'
               "</wp:inline></w:drawing></w:r>")
    return drawing, f"media/{name}", brand.logo_bytes, ext


def _dx_lang(ctx) -> str:
    """The w:lang element of the document defaults: the pack's lang (en-GB without a valid one); an rtl pack's
    lang is also its complex-script (w:bidi) language."""
    lang = (ctx.pack or {}).get("lang")
    if not (isinstance(lang, str) and LOCALE_RX.fullmatch(lang)):
        return '<w:lang w:val="en-GB"/>'
    bidi = f' w:bidi="{xml_text(lang)}"' if _dx_dir(ctx) == "rtl" else ""
    return f'<w:lang w:val="{xml_text(lang)}"{bidi}/>'


def _dx_styles(accent: str, lang_xml: str = '<w:lang w:val="en-GB"/>') -> str:
    def para_style(sid, name, ppr, rpr, based="Normal"):
        base = f'<w:basedOn w:val="{based}"/><w:next w:val="Normal"/>' if based else ""
        return (f'<w:style w:type="paragraph" w:styleId="{sid}"><w:name w:val="{name}"/>{base}<w:qFormat/>'
                f"<w:pPr>{ppr}</w:pPr><w:rPr>{rpr}</w:rPr></w:style>")
    return (DX_DECL + f'<w:styles {DX_NS}><w:docDefaults><w:rPrDefault><w:rPr>'
            '<w:rFonts w:ascii="Calibri" w:hAnsi="Calibri" w:eastAsia="Calibri" w:cs="Arial"/>'
            '<w:sz w:val="22"/><w:szCs w:val="22"/>' + lang_xml + '</w:rPr></w:rPrDefault>'
            '<w:pPrDefault><w:pPr><w:spacing w:after="120" w:line="264" w:lineRule="auto"/></w:pPr></w:pPrDefault>'
            "</w:docDefaults>"
            + para_style("Normal", "Normal", "", "", based=None).replace("<w:style ", '<w:style w:default="1" ', 1)
            + para_style("Title", "Title", '<w:spacing w:after="80"/>',
                         f'<w:b/><w:color w:val="{accent}"/><w:sz w:val="40"/><w:szCs w:val="40"/>')
            + para_style("Heading1", "heading 1", '<w:keepNext/><w:spacing w:before="320" w:after="120"/>'
                         '<w:outlineLvl w:val="0"/>',
                         f'<w:b/><w:color w:val="{accent}"/><w:sz w:val="30"/><w:szCs w:val="30"/>')
            + para_style("Heading2", "heading 2", '<w:keepNext/><w:spacing w:before="200" w:after="80"/>'
                         '<w:outlineLvl w:val="1"/>', '<w:b/><w:sz w:val="25"/><w:szCs w:val="25"/>')
            + para_style("Caption", "caption", '<w:spacing w:after="80"/>',
                         '<w:i/><w:color w:val="44546A"/><w:sz w:val="19"/><w:szCs w:val="19"/>')
            + '<w:style w:type="table" w:styleId="TableGrid"><w:name w:val="Table Grid"/><w:tblPr>'
            '<w:tblBorders><w:top w:val="single" w:sz="4" w:space="0" w:color="A6A6A6"/>'
            '<w:left w:val="single" w:sz="4" w:space="0" w:color="A6A6A6"/>'
            '<w:bottom w:val="single" w:sz="4" w:space="0" w:color="A6A6A6"/>'
            '<w:right w:val="single" w:sz="4" w:space="0" w:color="A6A6A6"/>'
            '<w:insideH w:val="single" w:sz="4" w:space="0" w:color="A6A6A6"/>'
            '<w:insideV w:val="single" w:sz="4" w:space="0" w:color="A6A6A6"/></w:tblBorders>'
            '<w:tblCellMar><w:left w:w="85" w:type="dxa"/><w:right w:w="85" w:type="dxa"/></w:tblCellMar>'
            "</w:tblPr></w:style></w:styles>")


def _dx_numbering(ordered: int) -> str:
    bullet = ('<w:abstractNum w:abstractNumId="0"><w:multiLevelType w:val="singleLevel"/><w:lvl w:ilvl="0">'
              '<w:start w:val="1"/><w:numFmt w:val="bullet"/><w:lvlText w:val="•"/><w:lvlJc w:val="left"/>'
              '<w:pPr><w:ind w:left="567" w:hanging="283"/></w:pPr></w:lvl></w:abstractNum>')
    decimal = ('<w:abstractNum w:abstractNumId="1"><w:multiLevelType w:val="singleLevel"/><w:lvl w:ilvl="0">'
               '<w:start w:val="1"/><w:numFmt w:val="decimal"/><w:lvlText w:val="%1."/><w:lvlJc w:val="left"/>'
               '<w:pPr><w:ind w:left="567" w:hanging="425"/></w:pPr></w:lvl></w:abstractNum>')
    nums = '<w:num w:numId="1"><w:abstractNumId w:val="0"/></w:num>'
    nums += "".join(f'<w:num w:numId="{n}"><w:abstractNumId w:val="1"/><w:lvlOverride w:ilvl="0">'
                    '<w:startOverride w:val="1"/></w:lvlOverride></w:num>' for n in range(2, ordered + 2))
    return DX_DECL + f"<w:numbering {DX_NS}>{bullet}{decimal}{nums}</w:numbering>"


def _dx_endnotes(wr) -> str:
    sep = ('<w:endnote w:type="separator" w:id="-1"><w:p><w:r><w:separator/></w:r></w:p></w:endnote>'
           '<w:endnote w:type="continuationSeparator" w:id="0"><w:p><w:r><w:continuationSeparator/></w:r></w:p>'
           "</w:endnote>")
    body = []
    for nid, lines in wr.notes:
        ref = (f'<w:r><w:rPr><w:vertAlign w:val="superscript"/>{"<w:rtl/>" if wr.rtl else ""}</w:rPr>'
               "<w:endnoteRef/></w:r>")
        ps = [f"<w:p>{wr.ppr('Caption')}{ref if i == 0 else ''}{_dx_run((' ' if i == 0 else '') + x, '', wr.rtl)}</w:p>"
              for i, x in enumerate(lines)]
        body.append(f'<w:endnote w:id="{nid}">{"".join(ps)}</w:endnote>')
    return DX_DECL + f"<w:endnotes {DX_NS}>{sep}{''.join(body)}</w:endnotes>"


def _dx_footer(wr) -> str:
    page = '<w:fldSimple w:instr=" PAGE "><w:r><w:t>1</w:t></w:r></w:fldSimple>'
    text = _dx_run(f"{STATUS_PHRASE} · {BRAND} · ", "", wr.rtl)
    return DX_DECL + f'<w:ftr {DX_NS}><w:p>{wr.ppr("Caption")}{text}{page}</w:p></w:ftr>'


def _dx_header(wr, organisation, draft) -> str:
    """The header part: the brand's organisation name, and DRAFT_LABEL when the document is a draft."""
    ps = f"<w:p>{wr.ppr('Caption')}{_dx_run(organisation, '', wr.rtl)}</w:p>" if organisation else ""
    if draft:
        ps += f"<w:p>{wr.ppr()}{_dx_run(DRAFT_LABEL, 'b', wr.rtl, DX_DRAFT_COLOUR)}</w:p>"
    return DX_DECL + f"<w:hdr {DX_NS}>{ps}</w:hdr>"


def write_docx(doc_blocks, ctx) -> bytes:
    """The docx of doc_blocks ((kind, payload, cites) tuples, kinds in DX_KINDS) for ctx: the footer (status phrase,
    brand, page number) on every page, DRAFT in the header when ctx.eh is not an approval, the brand's logo and
    organisation above the title, and the citations as endnotes read from ctx.w."""
    wr = _DxWriter(ctx, _dx_cite_line(ctx.w))
    brand = ctx.brand
    accent = (brand.accent.lstrip("#").upper() if brand and getattr(brand, "accent", None) else DX_ACCENT)
    body = []
    logo = _dx_logo(brand, _dx_labels(ctx).get("ui.docx.logo_alt", "Organisation logo"))
    if logo:
        body.append(f"<w:p>{wr.ppr()}{logo[0]}</w:p>")
    for blk in doc_blocks:
        kind, payload, cites = (tuple(blk) + (None, None))[:3]
        body.append(wr.block(kind, payload, cites))
    draft = is_draft(ctx.eh) if ctx.eh else True
    org = getattr(brand, "organisation", None) if brand else None
    hdr_rel = []
    sect_refs = ""
    parts = {}
    if draft or org:
        parts["word/header1.xml"] = _dx_header(wr, org, draft)
        hdr_rel = [("rIdHeader", "header", "header1.xml")]
        sect_refs += '<w:headerReference w:type="default" r:id="rIdHeader"/>'
    sect_refs += '<w:footerReference w:type="default" r:id="rIdFooter"/>'
    sect = (f'<w:sectPr>{sect_refs}<w:endnotePr><w:numFmt w:val="decimal"/></w:endnotePr>'
            f'<w:pgSz w:w="{DX_PAGE_W}" w:h="{DX_PAGE_H}"/>'
            f'<w:pgMar w:top="{DX_MARGIN}" w:right="{DX_MARGIN}" w:bottom="{DX_MARGIN}" w:left="{DX_MARGIN}" '
            f'w:header="567" w:footer="567" w:gutter="0"/>{"<w:bidi/>" if wr.rtl else ""}</w:sectPr>')
    doc = (DX_DECL + f'<w:document {DX_NS} xmlns:wp="{DX_WP}"><w:body>{"".join(body)}{sect}</w:body></w:document>')
    title = next((p for k, p, *_ in doc_blocks if k == "title"), "") if doc_blocks else ""
    created = ctx.generated or "1980-01-01"
    doc_rels = [("rIdStyles", "styles", "styles.xml"), ("rIdSettings", "settings", "settings.xml"),
                ("rIdNumbering", "numbering", "numbering.xml"), ("rIdEndnotes", "endnotes", "endnotes.xml"),
                ("rIdFooter", "footer", "footer1.xml")] + hdr_rel
    overrides = {"word/document.xml": DX_CT["document"], "word/styles.xml": DX_CT["styles"],
                 "word/settings.xml": DX_CT["settings"], "word/numbering.xml": DX_CT["numbering"],
                 "word/endnotes.xml": DX_CT["endnotes"], "word/footer1.xml": DX_CT["footer"],
                 "docProps/core.xml": DX_CT["core"], "docProps/app.xml": DX_CT["app"]}
    if hdr_rel:
        overrides["word/header1.xml"] = DX_CT["header"]
    defaults = {"rels": "application/vnd.openxmlformats-package.relationships+xml", "xml": "application/xml"}
    if logo:
        doc_rels.append(("rIdLogo", "image", logo[1]))
        parts[f"word/{logo[1]}"] = logo[2]
        defaults[logo[3]] = f"image/{logo[3]}"
    settings = (DX_DECL + f'<w:settings {DX_NS}><w:defaultTabStop w:val="708"/><w:characterSpacingControl '
                'w:val="doNotCompress"/><w:endnotePr><w:endnote w:id="-1"/><w:endnote w:id="0"/></w:endnotePr>'
                "<w:compat><w:compatSetting w:name=\"compatibilityMode\" w:uri=\"http://schemas.microsoft.com/office/"
                'word" w:val="15"/></w:compat></w:settings>')
    parts.update({
        "[Content_Types].xml": content_types(defaults, overrides),
        "_rels/.rels": rels([("rId1", "officeDocument", "word/document.xml"),
                             ("rId2", "core-properties", "docProps/core.xml"),
                             ("rId3", "extended-properties", "docProps/app.xml")]),
        "docProps/core.xml": core_props(title if isinstance(title, str) else "", created),
        "docProps/app.xml": app_props(),
        "word/document.xml": doc,
        "word/_rels/document.xml.rels": rels(doc_rels),
        "word/styles.xml": _dx_styles(accent, _dx_lang(ctx)),
        "word/settings.xml": settings,
        "word/numbering.xml": _dx_numbering(wr.ordered),
        "word/endnotes.xml": _dx_endnotes(wr),
        "word/footer1.xml": _dx_footer(wr),
    })
    return zip_bytes(parts)


def docx_text(data: bytes) -> str:
    """All the visible text of a docx, in order: the header, the body, the endnotes, then the footer; one line per
    paragraph ("" for something that is not a docx)."""
    try:
        z = zipfile.ZipFile(io.BytesIO(data))
    except (zipfile.BadZipFile, TypeError, ValueError):
        return ""
    names = [n for n in z.namelist() if DX_TEXT_PARTS_RX.fullmatch(n)]
    names.sort(key=lambda n: (DX_PART_ORDER.index(re.sub(r"\d+$", "", n[5:-4])), n))
    w = f"{{{DX_W}}}"
    out = []
    for n in names:
        try:
            root = ET.fromstring(z.read(n))
        except ET.ParseError:
            continue
        for p in root.iter(f"{w}p"):
            bits = []
            for el in p.iter():
                if el.tag == f"{w}t":
                    bits.append(el.text or "")
                elif el.tag == f"{w}tab":
                    bits.append("\t")
                elif el.tag == f"{w}br" and el.get(f"{w}type") != "page":
                    bits.append("\n")
            if bits:
                out.append("".join(bits))
    return "\n".join(out)


# ----------------------------------------------------------------------------- the pack as blocks

def _dx_ids(d) -> list:
    """The finding then evidence IDs an item (or bottom-line entry) cites: its cite lists and inline IDs."""
    if not isinstance(d, dict):
        return []
    if "kind" in d:
        fids, eids = cited_ids({"sections": [{"items": [d]}]})
    else:
        fids, eids = cited_ids({"bottom_line": [d]})
    return fids + eids


def _dx_str(v, L) -> str:
    if isinstance(v, bool):
        return label(L, "ui.yes" if v else "ui.no")
    if isinstance(v, dict):
        return "; ".join(f"{k}: {_dx_str(x, L)}" for k, x in v.items())
    if isinstance(v, list):
        return " | ".join(_dx_str(x, L) for x in v)
    return "" if v is None else str(v)


def _dx_entries(v, L, field="") -> list:
    """A list field as list entries. A question option {text, correct} reads 'text (correct)' in the full view."""
    out = []
    for x in v if isinstance(v, list) else [v]:
        if isinstance(x, dict) and field == "options" and "text" in x:
            out.append(str(x["text"]) + (f" ({label(L, 'ui.docx.correct')})" if x.get("correct") else ""))
        else:
            out.append(_dx_str(x, L))
    return out


def _dx_extras(it, L) -> list:
    """The note lines under an item: evidence strength, supporting citations, learning, clauses, lint_ok notes."""
    bits = ([label(L, "ui.evidence_md", strength=it["evidence_strength"])] if it.get("evidence_strength") else []) + \
           ([label(L, "ui.supporting", n=len(it["supporting_cites"]))] if it.get("supporting_cites") else []) + \
           ([label(L, "ui.learning_md", id=it["learning"])] if it.get("learning") else []) + \
           ([f"{label(L, 'f.clauses')}: {', '.join(map(str, it['clauses']))}"] if it.get("clauses") else [])
    out = [("note", "; ".join(bits), None)] if bits else []
    return out + [("note", n, None) for n in lint_ok_notes(it, L)]


def _dx_generic(it, L, cites, lead="") -> list:
    """An item laid out by its field roles (P4-5): the title in bold, badges on one note line, body fields as
    'Label: text', lists as bullets. The item's citations go on its first paragraph."""
    kind = it.get("kind")
    klabel = L.get(f"k.{kind}", str(kind))
    blocks, badges = [], []
    bl = item_blocks(it, L)
    has_title = any(b.role == "title" for b in bl)
    first_body = True
    for b in bl:
        v = b.value
        if b.role == "badge":
            if isinstance(v, bool):
                if v:
                    badges.append(b.label)
                continue
            badges.append(f"{b.label}: {norm_hoc(v) if b.field == 'hoc_tier' else _dx_str(v, L)}")
            continue
        if b.role == "title":
            blocks.append(("para", [(lead, "b"), (f"{klabel}: ", "b"), (_dx_str(v, L), "b")], None))
        elif isinstance(v, (list, dict)) and b.role not in ("body", "indicator", "title"):
            if isinstance(v, dict):
                entries = [f"{k}: {_dx_str(x, L)}" for k, x in v.items()]
            else:
                entries = _dx_entries(v, L, b.field)
            blocks.append(("para", [(lead if not blocks else "", "b"), (f"{b.label}:", "b")], None))
            blocks.append(("list", entries, None))
        elif not has_title and first_body and kind == "para":
            blocks.append(("para", [(lead, "b"), (_dx_str(v, L), "")], None))
        elif not has_title and first_body:
            blocks.append(("para", [(lead, "b"), (f"{klabel}: ", "b"), (_dx_str(v, L), "")], None))
        else:
            blocks.append(("para", [(lead if not blocks else "", "b"), (f"{b.label}: ", "b"), (_dx_str(v, L), "")],
                           None))
        if b.role in ("body", "indicator"):
            first_body = False
    if badges:
        pos = 1 if blocks and has_title else 0
        blocks.insert(pos, ("note", " · ".join(badges), None))
    if not blocks:
        blocks.append(("para", [(lead, "b"), (klabel, "b")], None))
    k, p, _ = blocks[0]
    blocks[0] = (k, p, cites)
    return blocks


def _dx_item(it, L, inc_date, lead="") -> list:
    """One item as blocks. table, test_point, timeline and graph have their own layouts; check gets a box; every
    other kind (an unknown one too) is laid out by its field roles. lead is the paper's paragraph number."""
    kind = it.get("kind")
    cites = _dx_ids(it)
    out = []
    if kind == "para":
        out = [("para", [(lead, "b"), (str(it.get("text", "")), "")], cites)]
    elif kind == "check":
        hold = [(f"{label(L, 'f.hold_point')}: ", "b")] if it.get("hold_point") else []
        when = [(f" ({it['when']})", "i")] if it.get("when") else []
        out = [("para", [(lead, "b"), ("☐ ", "")] + hold + [(str(it.get("text", "")), "")] + when, cites)]
    elif kind == "table" and isinstance(it.get("columns"), list) and isinstance(it.get("rows"), list):
        cols, rows = [str(c) for c in it["columns"]], [list(r) if isinstance(r, list) else [r] for r in it["rows"]]
        rc, rs = it.get("row_cites"), it.get("row_supporting_cites")
        if rc or rs:
            cols.append(label(L, "f.cites"))
            for i, r in enumerate(rows):
                own = rc[i] if isinstance(rc, list) and i < len(rc) and isinstance(rc[i], list) else []
                sup = rs[i] if isinstance(rs, list) and i < len(rs) and isinstance(rs[i], list) else []
                r.append("; ".join(own) + (f" ({label(L, 'ui.supporting', n=len(sup))})" if sup else ""))
        if lead:
            out.append(("para", [(lead.strip(), "b")], None))
        out.append(("table", {"columns": cols, "rows": rows}, cites))
        if isinstance(it.get("finding_notes"), dict) and it["finding_notes"]:
            out += [("para", [(f"{label(L, 'f.finding_notes')}:", "b")], None),
                    ("list", [f"{k}: {v}" for k, v in it["finding_notes"].items()], None)]
    elif kind == "test_point":
        bl = item_blocks(it, L)
        head = next((b for b in bl if b.field == "requirement"), None)
        rows = [[b.label, _dx_str(b.value, L) if not isinstance(b.value, list) else "; ".join(map(str, b.value))]
                for b in bl if b is not head]
        if lead:
            out.append(("para", [(lead.strip(), "b")], None))
        out.append(("table", {"columns": [label(L, "k.test_point"), _dx_str(head.value, L) if head else ""],
                              "rows": rows}, cites))
    elif kind == "timeline" and isinstance(it.get("events"), list):
        evs = [e for e in it["events"] if isinstance(e, dict) and e.get("date")]
        extra = [(f, k) for f, k in (("received_by", "ui.received_by"), ("response", "ui.response"),
                                     ("knowable_then", "ui.knowable_then")) if any(f in e for e in evs)]
        rows = []
        for e in sorted_events(evs):
            what = str(e.get("text", "")) + (f" ({label(L, 'ui.weak_signal_md')})" if e.get("signal") else "")
            rows.append([event_when(e, inc_date, L), what] +
                        [(_dx_knowable(e[f], L) if f == "knowable_then" else str(e[f])) if f in e else ""
                         for f, _ in extra])
        if lead:
            out.append(("para", [(lead.strip(), "b")], None))
        out.append(("table", {"columns": [label(L, "ui.docx.when"), label(L, "ui.docx.what")]
                              + [label(L, k) for _, k in extra], "rows": rows}, cites))
    elif kind == "graph" and isinstance(it.get("nodes"), list) and isinstance(it.get("edges"), list):
        lab = {n.get("id"): n.get("label", n.get("id")) for n in it["nodes"] if isinstance(n, dict)}
        links = [f"{lab.get(e.get('from'), e.get('from'))} → {lab.get(e.get('to'), e.get('to'))}"
                 + (f" ({e['label']})" if e.get("label") else "") for e in it["edges"] if isinstance(e, dict)]
        out = [("para", [(lead, "b"), (label(L, "ui.graph_summary", nodes=len(it["nodes"]), links=len(links)), "")],
                cites),
               ("para", [(label(L, "ui.links_as_text", n=len(links)), "b")], None), ("list", links, None)]
    else:
        out = _dx_generic(it, L, cites, lead)
    return out + _dx_extras(it, L)


def _dx_head(ctx, L, pack) -> list:
    """The title block: title, status line, learner banner, translation note, DRAFT, handling lines, reading time,
    audience and incident."""
    out = [("title", str(pack.get("title", pack.get("pack", ""))), None),
           ("status", status_line(pack.get("status", "")), None)]
    if ctx.view == "learner":
        out.append(("status", LEARNER_BANNER, None))
    out += [("status", x, None) for x in translation_lines(pack)]
    if is_draft(ctx.eh):
        out.append(("para", [(DRAFT_LABEL, "b")], None))
    out += [("status", x, None) for x in _dx_handling_lines(ctx.eh, ctx.share, markdown=False)]
    out.append(("status", L.get("ui.reading_time", READING_TIME).format(n=reading_minutes(pack)), None))
    if pack.get("audience"):
        out.append(("para", [(f"{label(L, 'f.audience')}: ", "b"), (str(pack["audience"]), "")], None))
    fields, inc = (ctx.w or {}).get("incident", {}).get("fields", {}), pack.get("incident") or {}
    shown = [str(x) for x in (inc.get("title") or fields.get("Incident Title"), inc.get("date") or fields.get("Date"))
             if x]
    if shown:
        out.append(("para", [(f"{label(L, 'ui.incident')}: ", "b"), (" · ".join(shown), "")], None))
    return out


def _dx_bottom_line(pack) -> list:
    return [("list", [str(b.get("text", ""))], _dx_ids(b)) for b in pack.get("bottom_line") or []
            if isinstance(b, dict)]


def _dx_tail(ctx, L, pack) -> list:
    """Coverage, then gaps and limits."""
    cov = coverage(ctx.w, pack)
    out = [("heading1", label(L, "ui.coverage"), None),
           ("para", f"This pack cites {cov['cited']} of {cov['relevant']} relevant findings.", None),
           ("para", TOP_PRINT_LINE.format(x=cov["top_cited"], y=cov["top_relevant"]) + ".", None)]
    if cov["excluded"]:
        out += [("para", [(f"{label(L, 'ui.left_out')}:", "b")], None),
                ("list", [f"{e['id']}: {e['reason']}" for e in cov["excluded"]], None)]
    gaps = [g for g in pack.get("gaps") or [] if isinstance(g, dict)]
    if gaps:
        out.append(("heading1", label(L, "ui.gaps"), None))
        out += [("list", [f"{g.get('text', '')} ({label(L, 'ui.evidence_needed')}: {g.get('evidence_needed', '')})"],
                 [x for x in g.get("cites") or [] if isinstance(x, str)]) for g in gaps]
    if pack.get("limits"):
        out += [("heading1", label(L, "ui.limits"), None), ("list", [str(x) for x in pack["limits"]], None)]
    return out


def _dx_sections(pack) -> list:
    return [s for s in pack.get("sections") or [] if isinstance(s, dict)]


def _dx_section_items(s) -> list:
    return [it for it in s.get("items") or [] if isinstance(it, dict)]


def _dx_body(ctx, L, pack, inc_date) -> list:
    out = []
    if pack.get("data_quality"):
        out.append(("heading1", label(L, "ui.data_quality"), None))
        out += [("list", [str(n.get("text", ""))], _dx_ids(n)) for n in pack["data_quality"] if isinstance(n, dict)]
    out += [("heading1", label(L, "ui.bottom_line"), None)] + _dx_bottom_line(pack)
    for s in _dx_sections(pack):
        out.append(("heading1", str(s.get("heading", "")), None))
        if s.get("intro"):
            out.append(("para", str(s["intro"]), _dx_ids({"text": s["intro"]})))
        prev = None
        for it in _dx_section_items(s):
            g = it.get("group")
            if g and g != prev:
                out.append(("heading2", str(g), None))
            prev = g
            out += _dx_item(it, L, inc_date)
    return out


DX_PAPER_ANNEX_A = ("question",)
DX_PAPER_ANNEX_B = ("table", "indicator")


def _dx_paper_body(ctx, L, pack, inc_date) -> list:
    """The board paper (P4-8): a cover page, then "Decisions requested" (decision items, then the bottom line),
    numbered paragraphs for every other item, Annex A for questions and Annex B for tables and indicators."""
    items = [(s, it) for s in _dx_sections(pack) for it in _dx_section_items(s)]
    out = [("pagebreak", None, None), ("heading1", label(L, "ui.docx.decisions_requested"), None)]
    for n, (_, it) in enumerate([x for x in items if x[1].get("kind") == "decision"], 1):
        out += _dx_item(it, L, inc_date, lead=f"{n}. ")
    out += [("heading2", label(L, "ui.bottom_line"), None)] + _dx_bottom_line(pack)
    if pack.get("data_quality"):
        out.append(("heading2", label(L, "ui.data_quality"), None))
        out += [("list", [str(n.get("text", ""))], _dx_ids(n)) for n in pack["data_quality"] if isinstance(n, dict)]
    moved = DX_PAPER_ANNEX_A + DX_PAPER_ANNEX_B + ("decision",)
    num = 0
    for s in _dx_sections(pack):
        rest = [it for it in _dx_section_items(s) if it.get("kind") not in moved]
        if not rest and not s.get("intro"):
            continue
        num += 1
        out.append(("heading1", f"{num}. {s.get('heading', '')}", None))
        if s.get("intro"):
            out.append(("para", str(s["intro"]), _dx_ids({"text": s["intro"]})))
        for m, it in enumerate(rest, 1):
            out += _dx_item(it, L, inc_date, lead=f"{num}.{m} ")
    for key, kinds, letter in (("ui.docx.annex_a", DX_PAPER_ANNEX_A, "A"), ("ui.docx.annex_b", DX_PAPER_ANNEX_B, "B")):
        picked = [(s, it) for s, it in items if it.get("kind") in kinds]
        if not picked:
            continue
        out.append(("heading1", label(L, key), None))
        prev = None
        for m, (s, it) in enumerate(picked, 1):
            if s is not prev:
                out.append(("heading2", str(s.get("heading", "")), None))
            prev = s
            out += _dx_item(it, L, inc_date, lead=f"{letter}.{m} ")
    return out


def pack_docx_blocks(ctx, paper: bool = False) -> list:
    """The pack of ctx as write_docx blocks: the normal document, or the board paper."""
    L = _dx_labels(ctx)
    pack = ctx.pack
    inc_date = _dx_incident_date(pack, ctx.w)
    body = _dx_paper_body(ctx, L, pack, inc_date) if paper else _dx_body(ctx, L, pack, inc_date)
    return _dx_head(ctx, L, pack) + body + _dx_tail(ctx, L, pack)


def render_docx(ctx) -> list:
    """<pack>.docx, and with the paper layout also <pack>.paper.docx (P4-7). The learner view is applied by
    render(); this adds the banner and the .learner name."""
    name = ctx.pack["pack"]
    outs = []
    for layout in (None, "paper") if ctx.layout == "paper" else (None,):
        data = write_docx(pack_docx_blocks(ctx, paper=layout == "paper"), ctx)
        outs.append(Output(output_name(name, "docx", layout=layout, view=ctx.view), data, docx_text(data)))
    return outs


register("docx", render_docx, help="<pack>.docx: a Word document (with the paper layout, also <pack>.paper.docx)")
