"""The pptx format (L4-04, Rulings P4-25, P4-9, P4-20): a 16:9 deck built with the standard library. One slide master,
one blank layout and one theme; every slide is text boxes placed in EMU. In order: a title slide, one slide per
bottom-line entry, one per decision, module and question item, one per other section (at most PX_PER_SLIDE item
summaries a slide, then "(continued)" slides), one per graph item drawn as native shapes, and a closing slide with
the coverage lines. Every slide carries the status phrase and the brand (which holds VERSION_STAMP) in a footer, and
DRAFT while the pack is a draft. Each slide's citations and its items' full text go to its notes slide."""
from __future__ import annotations

import html as px_std_html
import io
import json
import math
import re
import xml.etree.ElementTree as px_ET
import zipfile

from .. import BRAND, DRAFT_LABEL, STATUS_PHRASE
from ..handling import is_draft, status_line
from ..pack.graph_layout import layout_graph, NODE_H, NODE_W
from ..pack.markdown import _handling_lines as _px_handling_lines, coverage, event_when, sorted_events
from ..pack.schema import ID_RX, TOP_PRINT_LINE
from ..workspace import incident_date
from . import LEARNER_BANNER, Output, output_name, register, translation_lines
from .fields import item_blocks, item_text
from .labels import label, load_labels, LOCALE_RX, text_dir
from .ooxml import app_props, content_types, core_props, rels, XML_DECL, xml_text, zip_bytes

PX_SLIDE_W, PX_SLIDE_H = 12192000, 6858000              # 16:9, in EMU (P4-25)
PX_NOTES_W, PX_NOTES_H = 6858000, 9144000
PX_EMU_PT = 12700
PX_MARGIN = 457200                                        # 0.5 in
PX_TITLE = (PX_MARGIN, 274320, PX_SLIDE_W - 2 * PX_MARGIN - 1645920, 868680)
PX_BODY = (PX_MARGIN, 1234440, PX_SLIDE_W - 2 * PX_MARGIN, 4846320)
PX_FOOTER = (PX_MARGIN, 6172200, PX_SLIDE_W - 2 * PX_MARGIN, 548640)
PX_DRAFT = (PX_SLIDE_W - PX_MARGIN - 1463040, 365760, 1463040, 457200)
PX_COVER_TITLE = (PX_MARGIN, 1188720, PX_SLIDE_W - 2 * PX_MARGIN, 1554480)
PX_COVER_BODY = (PX_MARGIN, 2834640, PX_SLIDE_W - 2 * PX_MARGIN, 3246120)
PX_LOGO_BOX = (PX_MARGIN, 274320, 2286000, 777240)         # at most 2.5 x 0.85 in, top left of the title slide
PX_PER_SLIDE = 6
PX_SUMMARY_MAX = 180
PX_OWN_SLIDE = ("decision", "module", "question")
PX_NOTES_ONLY = ("answer", "good_evidence")                # on a question slide these stay in the notes
PX_DEFAULT_ACCENT = "0077B6"
PX_TEXT = "1F2328"
PX_MUTED = "57606A"
PX_WARN = "C2410C"
PX_MAX_SCALE = 19050                                      # EMU per layout pixel: a small graph is not blown up
PX_HEX_RX = re.compile(r"^#?([0-9A-Fa-f]{6})$")
PX_CITE_GROUP_RX = re.compile(r"\s*[\[(]\s*(?:(?:FND-[0-9A-Za-z]{4,}|EVD-\d{3,})\s*[;,]?\s*)+[\])]")
PX_NODE_RX = re.compile(r'<g class="node"[^>]*aria-label="([^"]*)" transform="translate\((-?\d+),(-?\d+)\)">')
PX_EDGE_RX = re.compile(r'<path class="(edge[^"]*)" d="([^"]*)"')

NS_A = "http://schemas.openxmlformats.org/drawingml/2006/main"
NS_R = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
NS_P = "http://schemas.openxmlformats.org/presentationml/2006/main"
PX_NS = f'xmlns:a="{NS_A}" xmlns:r="{NS_R}" xmlns:p="{NS_P}"'
PX_CT = "application/vnd.openxmlformats-officedocument.presentationml"
PX_CLR_MAP = ('bg1="lt1" tx1="dk1" bg2="lt2" tx2="dk2" accent1="accent1" accent2="accent2" accent3="accent3" '
              'accent4="accent4" accent5="accent5" accent6="accent6" hlink="hlink" folHlink="folHlink"')
PX_GRP = ('<p:nvGrpSpPr><p:cNvPr id="1" name=""/><p:cNvGrpSpPr/><p:nvPr/></p:nvGrpSpPr><p:grpSpPr><a:xfrm>'
          '<a:off x="0" y="0"/><a:ext cx="0" cy="0"/><a:chOff x="0" y="0"/><a:chExt cx="0" cy="0"/></a:xfrm></p:grpSpPr>')


# ----------------------------------------------------------------------------- text

class _PxStyle:
    """What every paragraph needs: the language tag, the direction and the accent colour."""

    def __init__(self, lang: str, rtl: bool, accent: str):
        self.lang, self.rtl, self.accent = lang, rtl, accent


def _px_strip_cites(s) -> str:
    """Slide text: inline [FND-…; EVD-…] groups go to the notes, not the slide."""
    return PX_CITE_GROUP_RX.sub("", str(s))


def _px_clip(s: str, n: int = PX_SUMMARY_MAX) -> str:
    s = " ".join(s.split())
    if len(s) <= n:
        return s
    cut = s[: n - 1]
    return (cut.rsplit(" ", 1)[0] if " " in cut else cut).rstrip(" ,;:") + "…"


def _px_p(text, st: _PxStyle, *, sz: int = 1800, b: bool = False, color: str = None, bullet: bool = False,
          algn: str = None, after: int = 600) -> str:
    """One <a:p> per line of text. Every paragraph has a pPr, which carries rtl="1" for a right-to-left pack."""
    out = []
    for line in str(text if text is not None else "").split("\n"):
        attrs = (['marL="342900" indent="-342900"'] if bullet else []) + (['rtl="1"'] if st.rtl else [])
        al = algn or ("r" if st.rtl else None)
        attrs += [f'algn="{al}"'] if al else []
        bu = '<a:buFont typeface="Arial"/><a:buChar char="•"/>' if bullet else "<a:buNone/>"
        ppr = f'<a:pPr {" ".join(attrs)}><a:spcAft><a:spcPts val="{after}"/></a:spcAft>{bu}</a:pPr>'
        rpr = (f'lang="{st.lang}" sz="{sz}"' + (' b="1"' if b else "") + ' dirty="0"')
        fill = f'<a:solidFill><a:srgbClr val="{color or PX_TEXT}"/></a:solidFill>'
        t = xml_text(line)
        run = f"<a:r><a:rPr {rpr}>{fill}</a:rPr><a:t>{t}</a:t></a:r>" if t else ""
        out.append(f'<a:p>{ppr}{run}<a:endParaRPr lang="{st.lang}" sz="{sz}" dirty="0"/></a:p>')
    return "".join(out)


def _px_sp(sid: int, name: str, box, paras: str, *, anchor: str = "t", geom: str = "rect", fill: str = None,
           line: str = None, autofit: bool = True, inset: int = 91440) -> str:
    """A text shape (a text box, or a rounded rectangle for a graph node) placed at box = (x, y, cx, cy) in EMU."""
    x, y, cx, cy = (int(v) for v in box)
    fill_xml = f'<a:solidFill><a:srgbClr val="{fill}"/></a:solidFill>' if fill else "<a:noFill/>"
    line_xml = (f'<a:ln w="19050"><a:solidFill><a:srgbClr val="{line}"/></a:solidFill></a:ln>' if line
                else "<a:ln><a:noFill/></a:ln>")
    txbox = ' txBox="1"' if geom == "rect" else ""
    fit = "<a:normAutofit/>" if autofit else "<a:noAutofit/>"
    paras = paras or _px_p("", _PxStyle("en", False, PX_DEFAULT_ACCENT))
    return (f'<p:sp><p:nvSpPr><p:cNvPr id="{sid}" name="{xml_text(name)}"/><p:cNvSpPr{txbox}/><p:nvPr/></p:nvSpPr>'
            f'<p:spPr><a:xfrm><a:off x="{x}" y="{y}"/><a:ext cx="{cx}" cy="{cy}"/></a:xfrm>'
            f'<a:prstGeom prst="{geom}"><a:avLst/></a:prstGeom>{fill_xml}{line_xml}</p:spPr>'
            f'<p:txBody><a:bodyPr wrap="square" lIns="{inset}" tIns="{inset // 2}" rIns="{inset}" bIns="{inset // 2}" '
            f'anchor="{anchor}" rtlCol="0">{fit}</a:bodyPr><a:lstStyle/>{paras}</p:txBody></p:sp>')


# ----------------------------------------------------------------------------- what goes on the slides and notes

def _px_kind_label(L, kind) -> str:
    return L.get(f"k.{kind}", str(kind))


def _px_summary(it: dict, L: dict) -> str:
    """An item's one-line summary for a section slide: its title or body field, else its kind and first value."""
    t = item_text(it)
    if not t:
        first = ""
        for blk in item_blocks(it, L):
            v = blk.value
            if isinstance(v, str) and v.strip():
                first = v
            elif isinstance(v, list) and v and all(isinstance(x, str) for x in v):
                first = ", ".join(v)
            elif isinstance(v, list) and v:
                first = label(L, "ui.pptx.entries", n=len(v))
            if first:
                break
        kind = _px_kind_label(L, it.get("kind"))
        t = f"{kind}: {first}" if first else kind
    return _px_clip(_px_strip_cites(t))


def _px_yes_no(L, v) -> str:
    return label(L, "ui.yes" if v else "ui.no")


def _px_value_lines(blk, L, inc_date, it) -> list:
    """The full text of one block, as note lines."""
    v, lab = blk.value, blk.label
    if isinstance(v, bool):
        return [f"{lab}: {_px_yes_no(L, v)}"]
    if isinstance(v, (str, int, float)):
        return [f"{lab}: {v}"]
    if isinstance(v, dict):
        return [f"{lab}:"] + [f"- {k}: {x}" for k, x in v.items()]
    if not isinstance(v, list):
        return [f"{lab}: {v}"]
    if blk.role == "events":
        evs = [e for e in v if isinstance(e, dict) and isinstance(e.get("date"), str)]
        out = []
        for e in sorted_events(evs):
            cites = f" [{'; '.join(e['cites'])}]" if e.get("cites") else ""
            out.append(f"- {event_when(e, inc_date, L)}: {e.get('text', '')}{cites}")
        return out
    if blk.role == "graph" and blk.field == "nodes":
        return [f"{lab}: " + "; ".join(str(n.get("label") or n.get("id")) for n in v if isinstance(n, dict))]
    if blk.role == "graph" and blk.field == "edges":
        names = {n.get("id"): n.get("label") or n.get("id") for n in it.get("nodes") or [] if isinstance(n, dict)}
        return [f"- {names.get(e.get('from'), e.get('from'))} → {names.get(e.get('to'), e.get('to'))}"
                + (f" ({e['label']})" if e.get("label") else "") for e in v if isinstance(e, dict)]
    out = [f"{lab}:"]
    for x in v:
        if isinstance(x, list):
            out.append("- " + " | ".join(str(c) for c in x))
        elif isinstance(x, dict):
            text = x.get("text", json.dumps(x, ensure_ascii=False))
            out.append(f"- {text}" + (" ✓" if x.get("correct") is True else ""))
        else:
            out.append(f"- {x}")
    return out


def _px_ids(obj) -> list:
    """Every Finding and Evidence ID in obj (cite fields and inline brackets), in order, once each."""
    return list(dict.fromkeys(ID_RX.findall(json.dumps(obj, ensure_ascii=False))))


def _px_item_notes(it: dict, L: dict, inc_date) -> list:
    out = []
    for blk in item_blocks(it, L):
        out += _px_value_lines(blk, L, inc_date, it)
    ids = _px_ids(it)
    if ids:
        out.append(f"{label(L, 'f.cites')}: {'; '.join(ids)}")
    return out


def _px_records(ids, w, L) -> list:
    """'ID: label · L<level> · rating <r>' for a cited finding and 'ID: type' for cited evidence (the masked
    workspace in a shared copy)."""
    F = {f.get("id"): f for f in w.get("findings") or [] if isinstance(f, dict)}
    E = w.get("evidence") or {}
    out = []
    for x in ids:
        if x in F:
            f = F[x]
            bits = [f"{x}: {f.get('label') or ''}".rstrip()]
            if f.get("level") is not None:
                bits.append(f"L{f['level']}")
            if f.get("rating") is not None:
                bits.append(label(L, "ui.rating", rating=f["rating"]))
            out.append(" · ".join(bits))
        elif isinstance(E, dict) and x in E and isinstance(E[x], dict):
            out.append(f"{x}: {E[x].get('type') or ''}".rstrip())
    return out


# ----------------------------------------------------------------------------- slides

class _PxDeck:
    """The slides and notes as they are built: each slide is (shape XML, notes lines, extra relationships)."""

    def __init__(self, ctx, L, st: _PxStyle):
        self.ctx, self.L, self.st = ctx, L, st
        self.draft = is_draft(ctx.eh)
        self.slides = []

    def add(self, title: str, body: str, notes: list, *, cover: bool = False, shapes: str = "",
            rels_extra: tuple = ()) -> None:
        st = self.st
        tbox = PX_COVER_TITLE if cover else PX_TITLE
        title_xml = _px_p(_px_strip_cites(title), st, sz=4000 if cover else 2800, b=True, color=st.accent,
                          algn="ctr" if cover else None, after=0)
        sp = [_px_sp(2, "Title", tbox, title_xml, anchor="b" if cover else "ctr")]
        if body:
            sp.append(_px_sp(3, "Body", PX_COVER_BODY if cover else PX_BODY, body))
        foot = _px_p(f"{STATUS_PHRASE} · {BRAND}", st, sz=900, color=PX_MUTED, after=0)
        sp.append(_px_sp(4, "Footer", PX_FOOTER, foot, anchor="b", autofit=False, inset=0))
        if self.draft:
            sp.append(_px_sp(5, "Draft", PX_DRAFT, _px_p(DRAFT_LABEL, st, sz=2000, b=True, color=PX_WARN, algn="ctr",
                                                          after=0), anchor="ctr", line=PX_WARN, autofit=False))
        self.slides.append(("".join(sp) + shapes, notes, rels_extra))

    def body(self, items) -> str:
        """items: (text, kind) pairs; kind is big, bold, line, bullet or muted."""
        st, out = self.st, []
        for text, kind in items:
            text = _px_strip_cites(text)
            if kind == "big":
                out.append(_px_p(text, st, sz=2800, after=1200))
            elif kind == "bold":
                out.append(_px_p(text, st, sz=2400, b=True, after=1000))
            elif kind == "bullet":
                out.append(_px_p(text, st, sz=1800, bullet=True))
            elif kind == "muted":
                out.append(_px_p(text, st, sz=1400, color=PX_MUTED, after=300))
            else:
                out.append(_px_p(text, st, sz=1800))
        return "".join(out)


def _px_cover(deck: _PxDeck, pack: dict) -> None:
    ctx, L = deck.ctx, deck.L
    w = ctx.w
    lines = []
    brand = ctx.brand
    if brand is not None and brand.organisation:
        lines.append((brand.organisation, "bold"))
    lines.append((f"{label(L, 'f.audience')}: {pack.get('audience', '')}", "line"))
    fields, inc = (w.get("incident") or {}).get("fields") or {}, pack.get("incident") or {}
    shown = [str(x) for x in (inc.get("title") or fields.get("Incident Title"), inc.get("date") or fields.get("Date"))
             if x]
    if shown:
        lines.append((f"{label(L, 'ui.incident')}: " + " · ".join(shown), "line"))
    lines.append((status_line(pack.get("status", "")), "muted"))
    lines += [(x, "muted") for x in translation_lines(pack)]
    if ctx.view == "learner":
        lines.append((LEARNER_BANNER, "muted"))
    if deck.draft:
        lines.append((DRAFT_LABEL, "muted"))
    lines += [(x, "muted") for x in _px_handling_lines(ctx.eh, ctx.share, markdown=False)]
    notes = [x for x, _ in lines]
    if pack.get("data_quality"):
        notes += ["", label(L, "ui.data_quality") + ":"]
        notes += [f"- {n.get('text', '')}" + (f" [{'; '.join(n['cites'])}]" if n.get("cites") else "")
                  for n in pack["data_quality"] if isinstance(n, dict)]
    shapes, extra = "", ()
    if brand is not None and brand.logo_bytes and brand.logo_mime in ("image/png", "image/jpeg"):
        shapes = _px_pic(brand)
        extra = (("rId3", "image", f"../media/image1.{_px_logo_ext(brand)}"),)
    deck.add(pack.get("title", ""), deck.body(lines), notes, cover=True, shapes=shapes, rels_extra=extra)


def _px_logo_ext(brand) -> str:
    return "png" if brand.logo_mime == "image/png" else "jpeg"


def _px_img_size(data: bytes, mime: str):
    """(width, height) in pixels of a PNG or JPEG, or None when it cannot be read."""
    if mime == "image/png" and len(data) >= 24 and data[12:16] == b"IHDR":
        return int.from_bytes(data[16:20], "big"), int.from_bytes(data[20:24], "big")
    i = 2
    while mime == "image/jpeg" and i + 9 < len(data):
        if data[i] != 0xFF:
            return None
        marker, size = data[i + 1], int.from_bytes(data[i + 2:i + 4], "big")
        if marker in (0xC0, 0xC1, 0xC2):
            return int.from_bytes(data[i + 7:i + 9], "big"), int.from_bytes(data[i + 5:i + 7], "big")
        i += 2 + size
    return None


def _px_pic(brand) -> str:
    x, y, bw, bh = PX_LOGO_BOX
    size = _px_img_size(brand.logo_bytes, brand.logo_mime)
    if size and size[0] > 0 and size[1] > 0:
        s = min(bw / size[0], bh / size[1])
        cx, cy = int(size[0] * s), int(size[1] * s)
    else:
        cx = cy = bh
    descr = xml_text(brand.organisation or "")
    return (f'<p:pic><p:nvPicPr><p:cNvPr id="6" name="Logo" descr="{descr}"/><p:cNvPicPr><a:picLocks '
            f'noChangeAspect="1"/></p:cNvPicPr><p:nvPr/></p:nvPicPr><p:blipFill><a:blip r:embed="rId3"/><a:stretch>'
            f'<a:fillRect/></a:stretch></p:blipFill><p:spPr><a:xfrm><a:off x="{x}" y="{y}"/><a:ext cx="{cx}" '
            f'cy="{cy}"/></a:xfrm><a:prstGeom prst="rect"><a:avLst/></a:prstGeom></p:spPr></p:pic>')


def _px_own_slide(deck: _PxDeck, heading: str, it: dict, inc_date) -> None:
    """A decision, module or question: its title field large, its other fields as lines and bullets; a question's
    answer and good evidence stay in the notes."""
    L, rows = deck.L, []
    for blk in item_blocks(it, L):
        v = blk.value
        if blk.field in PX_NOTES_ONLY or v is None:
            continue
        if blk.role == "title" and isinstance(v, str):
            rows.append((v, "bold"))
        elif isinstance(v, bool):
            rows.append((f"{blk.label}: {_px_yes_no(L, v)}", "line"))
        elif isinstance(v, (str, int, float)):
            rows.append((f"{blk.label}: {v}", "line"))
        elif isinstance(v, list):
            rows.append((f"{blk.label}:", "line"))
            rows += [(x.get("text", "") if isinstance(x, dict) else " | ".join(map(str, x)) if isinstance(x, list)
                      else str(x), "bullet") for x in v]
    notes = _px_item_notes(it, L, inc_date)
    deck.add(heading, deck.body(rows), notes + _px_records_block(deck, _px_ids(it)))


def _px_records_block(deck: _PxDeck, ids) -> list:
    recs = _px_records(ids, deck.ctx.w, deck.L)
    return ["", label(deck.L, "ui.pptx.cited_records") + ":"] + recs if recs else []


def _px_section_slides(deck: _PxDeck, s: dict, inc_date) -> None:
    L = deck.L
    items = [it for it in s.get("items") or [] if isinstance(it, dict)]
    rest = [it for it in items if it.get("kind") not in PX_OWN_SLIDE and it.get("kind") != "graph"]
    if items and not rest:
        return                                                   # every item has a slide of its own
    heading = s.get("heading", "")
    chunks = [rest[i:i + PX_PER_SLIDE] for i in range(0, len(rest), PX_PER_SLIDE)] or [[]]
    for k, chunk in enumerate(chunks):
        rows = [(s["intro"], "line")] if k == 0 and s.get("intro") else []
        rows += [(_px_summary(it, L), "bullet") for it in chunk]
        notes = [str(s["intro"])] if k == 0 and s.get("intro") else []
        ids = _px_ids(s.get("intro") or "") if k == 0 else []
        for n, it in enumerate(chunk, k * PX_PER_SLIDE + 1):
            notes += ([""] if notes else []) + [f"{n}. {_px_summary(it, L)}"] + _px_item_notes(it, L, inc_date)
            ids += _px_ids(it)
        title = heading if k == 0 else label(L, "ui.pptx.continued", heading=heading)
        deck.add(title, deck.body(rows), notes + _px_records_block(deck, list(dict.fromkeys(ids))))


def _px_graph_layout(it: dict) -> dict:
    """The drawn nodes (full label and layout position) and links (end positions and kind) of a graph item, read
    from layout_graph's drawing, plus the layout size and the omitted count."""
    nodes = [n for n in it.get("nodes") or [] if isinstance(n, dict) and "id" in n]
    edges = [e for e in it.get("edges") or [] if isinstance(e, dict) and "from" in e and "to" in e]
    res = layout_graph(nodes, edges, str(it.get("id") or "g"))
    svg = res["svg"]
    vb = re.search(r'viewBox="0 0 (\d+) (\d+)"', svg)
    drawn = [(px_std_html.unescape(lab), int(x), int(y)) for lab, x, y in PX_NODE_RX.findall(svg)]
    links = []
    for cls, d in PX_EDGE_RX.findall(svg):
        nums = [int(v) for v in re.findall(r"-?\d+", d)]
        links.append((cls, (nums[0], nums[1]), (nums[-2], nums[-1])))
    return {"nodes": drawn, "links": links, "width": int(vb.group(1)), "height": int(vb.group(2)),
            "omitted": res["omitted"]}


def _px_node_size(label_text: str, cx: int, cy: int) -> int:
    """The largest font size (hundredths of a point, 6 to 14 pt) at which the whole label fits the node box."""
    w_pt, h_pt = max(cx - 91440, 1) / PX_EMU_PT, max(cy - 36576, 1) / PX_EMU_PT
    n = max(len(label_text), 1)
    for half in range(28, 11, -1):
        sz = half / 2
        lines = math.ceil(n * 0.55 * sz / w_pt)
        if lines * 1.2 * sz <= h_pt:
            return int(sz * 100)
    return 600


def _px_graph_slide(deck: _PxDeck, heading: str, it: dict, inc_date) -> None:
    """A graph as rounded rectangles (one per drawn node, the label in full) and straight connectors (one per link),
    scaled from layout_graph's coordinates into the slide body. Back links are dashed, bottom to bottom."""
    st, L = deck.st, deck.L
    g = _px_graph_layout(it)
    bx, by, bw, bh = PX_BODY
    s = min(bw / max(g["width"], 1), bh / max(g["height"], 1), PX_MAX_SCALE)
    ox, oy = bx + (bw - g["width"] * s) / 2, by + (bh - g["height"] * s) / 2
    cx, cy = NODE_W * s, NODE_H * s
    nodes, at, sid = [], {}, 10
    sz = min((_px_node_size(lab, cx, cy) for lab, _x, _y in g["nodes"]), default=1200)   # one size per graph
    for k, (lab, x, y) in enumerate(g["nodes"]):
        at[(x, y)] = sid
        paras = _px_p(lab, st, sz=sz, algn="ctr", after=0)
        nodes.append(_px_sp(sid, f"Node {k + 1}", (ox + x * s, oy + y * s, cx, cy), paras, anchor="ctr",
                            geom="roundRect", fill="FFFFFF", line=st.accent, inset=45720))
        sid += 1
    shapes = []                                          # links first, so the nodes are drawn over their ends
    for cls, (sx, sy), (ex, ey) in g["links"]:
        if "back" in cls:
            u, v, a, b = (sx - NODE_W // 2, sy - NODE_H), (ex - NODE_W // 2, ey - NODE_H), 2, 2
            p1 = (u[0] + NODE_W / 2, u[1] + NODE_H)
            p2 = (v[0] + NODE_W / 2, v[1] + NODE_H)
        else:
            if "skip" in cls:
                u, v = (sx - NODE_W // 2, sy), (ex - NODE_W // 2, ey)
            else:
                u, v = (sx - NODE_W, sy - NODE_H // 2), (ex, ey - NODE_H // 2)
            a, b = 3, 1
            p1, p2 = (u[0] + NODE_W, u[1] + NODE_H / 2), (v[0], v[1] + NODE_H / 2)
        shapes.append(_px_cxn(sid, at.get(u), at.get(v), a, b, (ox + p1[0] * s, oy + p1[1] * s),
                              (ox + p2[0] * s, oy + p2[1] * s), st.accent, dashed="back" in cls))
        sid += 1
    notes = []
    if g["omitted"]:
        notes.append(label(L, "ui.graph_omitted", n=g["omitted"]))
    notes += _px_item_notes(it, L, inc_date)
    deck.add(heading, "", notes + _px_records_block(deck, _px_ids(it)), shapes="".join(shapes + nodes))


def _px_cxn(sid, start, end, a, b, p1, p2, color, dashed=False) -> str:
    """A straight connector from p1 to p2 (EMU), glued to the node shapes' connection sites when they are known."""
    x, y = min(p1[0], p2[0]), min(p1[1], p2[1])
    cx, cy = abs(p2[0] - p1[0]), abs(p2[1] - p1[1])
    flip = (' flipH="1"' if p2[0] < p1[0] else "") + (' flipV="1"' if p2[1] < p1[1] else "")
    glue = (f'<a:stCxn id="{start}" idx="{a}"/>' if start else "") + (f'<a:endCxn id="{end}" idx="{b}"/>' if end else "")
    dash = '<a:prstDash val="dash"/>' if dashed else ""
    return (f'<p:cxnSp><p:nvCxnSpPr><p:cNvPr id="{sid}" name="Link {sid}"/><p:cNvCxnSpPr>{glue}</p:cNvCxnSpPr><p:nvPr/>'
            f'</p:nvCxnSpPr><p:spPr><a:xfrm{flip}><a:off x="{int(x)}" y="{int(y)}"/><a:ext cx="{int(cx)}" '
            f'cy="{int(cy)}"/></a:xfrm><a:prstGeom prst="straightConnector1"><a:avLst/></a:prstGeom>'
            f'<a:ln w="15875"><a:solidFill><a:srgbClr val="{color}"/></a:solidFill>{dash}<a:tailEnd type="triangle"/>'
            f'</a:ln></p:spPr></p:cxnSp>')


def _px_closing(deck: _PxDeck, pack: dict) -> None:
    ctx, L = deck.ctx, deck.L
    cov = coverage(ctx.w, pack)
    lines = [(f"This pack cites {cov['cited']} of {cov['relevant']} relevant findings.", "line"),
             (TOP_PRINT_LINE.format(x=cov["top_cited"], y=cov["top_relevant"]) + ".", "line"),
             (status_line(pack.get("status", "")), "muted"), (BRAND, "muted")]
    notes = [x for x, _ in lines]
    if cov["excluded"]:
        notes += ["", label(L, "ui.left_out") + ":"] + [f"- {e['id']}: {e['reason']}" for e in cov["excluded"]]
    if pack.get("gaps"):
        notes += ["", label(L, "ui.gaps") + ":"]
        for g in pack["gaps"]:
            if isinstance(g, dict):
                cites = f" [{'; '.join(g['cites'])}]" if g.get("cites") else ""
                notes.append(f"- {g.get('text', '')}{cites}")
                if g.get("evidence_needed"):
                    notes.append(f"  {label(L, 'ui.evidence_needed')}: {g['evidence_needed']}")
    if pack.get("limits"):
        notes += ["", label(L, "ui.limits") + ":"] + [f"- {x}" for x in pack["limits"]]
    deck.add(label(L, "ui.coverage"), deck.body(lines), notes)


def _px_slides(ctx, L, st) -> _PxDeck:
    pack = ctx.pack
    deck = _PxDeck(ctx, L, st)
    inc_date = (pack.get("incident") or {}).get("date") or incident_date(ctx.w)
    _px_cover(deck, pack)
    bl = [b for b in pack.get("bottom_line") or [] if isinstance(b, dict)]
    for n, b in enumerate(bl, 1):
        notes = [str(b.get("text", ""))]
        ids = _px_ids(b)
        if ids:
            notes.append(f"{label(L, 'f.cites')}: {'; '.join(ids)}")
        deck.add(f"{label(L, 'ui.bottom_line')} {n}/{len(bl)}", deck.body([(b.get("text", ""), "big")]),
                 notes + _px_records_block(deck, ids))
    sections = [s for s in pack.get("sections") or [] if isinstance(s, dict)]
    for s in sections:
        for it in s.get("items") or []:
            if isinstance(it, dict) and it.get("kind") in PX_OWN_SLIDE:
                _px_own_slide(deck, s.get("heading", ""), it, inc_date)
    for s in sections:
        _px_section_slides(deck, s, inc_date)
    for s in sections:
        for it in s.get("items") or []:
            if isinstance(it, dict) and it.get("kind") == "graph":
                _px_graph_slide(deck, s.get("heading", ""), it, inc_date)
    _px_closing(deck, pack)
    return deck


# ----------------------------------------------------------------------------- the package

def _px_theme(accent: str) -> str:
    def clr(tag, val):
        return f"<a:{tag}><a:srgbClr val=\"{val}\"/></a:{tag}>"
    scheme = "".join([clr("dk1", PX_TEXT), clr("lt1", "FFFFFF"), clr("dk2", "1F3A4D"), clr("lt2", "EEF2F5"),
                      clr("accent1", accent), clr("accent2", "C2410C"), clr("accent3", "2E7D32"),
                      clr("accent4", "6A4C93"), clr("accent5", "8A6D00"), clr("accent6", "57606A"),
                      clr("hlink", "0563C1"), clr("folHlink", "954F72")])
    font = '<a:latin typeface="Calibri"/><a:ea typeface=""/><a:cs typeface=""/>'
    solid = '<a:solidFill><a:schemeClr val="phClr"/></a:solidFill>'
    ln = f'<a:ln w="6350">{solid}</a:ln>'
    return (XML_DECL + f'<a:theme xmlns:a="{NS_A}" name="ProbeMatrix"><a:themeElements>'
            f'<a:clrScheme name="ProbeMatrix">{scheme}</a:clrScheme>'
            f'<a:fontScheme name="ProbeMatrix"><a:majorFont>{font}</a:majorFont><a:minorFont>{font}</a:minorFont>'
            f'</a:fontScheme><a:fmtScheme name="ProbeMatrix"><a:fillStyleLst>{solid * 3}</a:fillStyleLst>'
            f'<a:lnStyleLst>{ln * 3}</a:lnStyleLst>'
            f'<a:effectStyleLst>{"<a:effectStyle><a:effectLst/></a:effectStyle>" * 3}</a:effectStyleLst>'
            f'<a:bgFillStyleLst>{solid * 3}</a:bgFillStyleLst></a:fmtScheme></a:themeElements>'
            f'<a:objectDefaults/><a:extraClrSchemeLst/></a:theme>')


def _px_lvl1(sz: int) -> str:
    return (f'<a:lvl1pPr marL="0" algn="l" defTabSz="914400" eaLnBrk="1" hangingPunct="1"><a:defRPr sz="{sz}" '
            f'kern="1200"><a:solidFill><a:schemeClr val="tx1"/></a:solidFill><a:latin typeface="+mn-lt"/>'
            f'<a:ea typeface="+mn-ea"/><a:cs typeface="+mn-cs"/></a:defRPr></a:lvl1pPr>')


def _px_master() -> str:
    return (XML_DECL + f'<p:sldMaster {PX_NS}><p:cSld><p:bg><p:bgRef idx="1001"><a:schemeClr val="bg1"/></p:bgRef>'
            f'</p:bg><p:spTree>{PX_GRP}</p:spTree></p:cSld><p:clrMap {PX_CLR_MAP}/>'
            '<p:sldLayoutIdLst><p:sldLayoutId id="2147483649" r:id="rId1"/></p:sldLayoutIdLst>'
            f'<p:txStyles><p:titleStyle>{_px_lvl1(3200)}</p:titleStyle><p:bodyStyle>{_px_lvl1(1800)}</p:bodyStyle>'
            f'<p:otherStyle>{_px_lvl1(1800)}</p:otherStyle></p:txStyles></p:sldMaster>')


def _px_layout() -> str:
    return (XML_DECL + f'<p:sldLayout {PX_NS} type="blank" preserve="1"><p:cSld name="Blank"><p:spTree>{PX_GRP}'
            '</p:spTree></p:cSld><p:clrMapOvr><a:masterClrMapping/></p:clrMapOvr></p:sldLayout>')


def _px_ph_sp(sid, name, ph, box, body=False) -> str:
    tx = ('<p:txBody><a:bodyPr/><a:lstStyle/><a:p><a:endParaRPr lang="en-GB"/></a:p></p:txBody>' if body else "")
    lock = '<a:spLocks noGrp="1" noRot="1" noChangeAspect="1"/>' if ph.startswith('type="sldImg"') else \
        '<a:spLocks noGrp="1"/>'
    xfrm = (f'<a:xfrm><a:off x="{box[0]}" y="{box[1]}"/><a:ext cx="{box[2]}" cy="{box[3]}"/></a:xfrm>'
            '<a:prstGeom prst="rect"><a:avLst/></a:prstGeom>') if box else ""
    return (f'<p:sp><p:nvSpPr><p:cNvPr id="{sid}" name="{name}"/><p:cNvSpPr>{lock}</p:cNvSpPr><p:nvPr><p:ph {ph}/>'
            f'</p:nvPr></p:nvSpPr><p:spPr>{xfrm}</p:spPr>{tx}</p:sp>')


def _px_notes_master() -> str:
    img = _px_ph_sp(2, "Slide Image", 'type="sldImg" idx="2"', (381000, 685800, 6096000, 3429000))
    body = _px_ph_sp(3, "Notes", 'type="body" sz="quarter" idx="3"', (685800, 4343400, 5486400, 4114800), body=True)
    return (XML_DECL + f'<p:notesMaster {PX_NS}><p:cSld><p:bg><p:bgRef idx="1001"><a:schemeClr val="bg1"/>'
            f'</p:bgRef></p:bg><p:spTree>{PX_GRP}{img}{body}</p:spTree></p:cSld><p:clrMap {PX_CLR_MAP}/>'
            f'<p:notesStyle>{_px_lvl1(1200)}</p:notesStyle></p:notesMaster>')


def _px_notes_slide(lines: list, st: _PxStyle) -> str:
    img = _px_ph_sp(2, "Slide Image", 'type="sldImg"', None)
    paras = _px_p("\n".join(lines) if lines else "", st, sz=1200, after=0)
    body = (f'<p:sp><p:nvSpPr><p:cNvPr id="3" name="Notes"/><p:cNvSpPr><a:spLocks noGrp="1"/></p:cNvSpPr>'
            f'<p:nvPr><p:ph type="body" idx="1"/></p:nvPr></p:nvSpPr><p:spPr/><p:txBody><a:bodyPr/><a:lstStyle/>'
            f'{paras}</p:txBody></p:sp>')
    return (XML_DECL + f'<p:notes {PX_NS}><p:cSld><p:spTree>{PX_GRP}{img}{body}</p:spTree></p:cSld>'
            '<p:clrMapOvr><a:masterClrMapping/></p:clrMapOvr></p:notes>')


def _px_package(deck: _PxDeck, title: str, created: str) -> bytes:
    st, brand = deck.st, deck.ctx.brand
    parts = {
        "_rels/.rels": rels([("rId1", "officeDocument", "ppt/presentation.xml"),
                             ("rId2", "core-properties", "docProps/core.xml"),
                             ("rId3", "extended-properties", "docProps/app.xml")]),
        "docProps/core.xml": core_props(title, created),
        "docProps/app.xml": app_props(),
        "ppt/slideMasters/slideMaster1.xml": _px_master(),
        "ppt/slideMasters/_rels/slideMaster1.xml.rels": rels([("rId1", "slideLayout", "../slideLayouts/slideLayout1.xml"),
                                                              ("rId2", "theme", "../theme/theme1.xml")]),
        "ppt/slideLayouts/slideLayout1.xml": _px_layout(),
        "ppt/slideLayouts/_rels/slideLayout1.xml.rels": rels([("rId1", "slideMaster",
                                                               "../slideMasters/slideMaster1.xml")]),
        "ppt/theme/theme1.xml": _px_theme(st.accent),
        "ppt/theme/theme2.xml": _px_theme(st.accent),
        "ppt/notesMasters/notesMaster1.xml": _px_notes_master(),
        "ppt/notesMasters/_rels/notesMaster1.xml.rels": rels([("rId1", "theme", "../theme/theme2.xml")]),
        "ppt/presProps.xml": XML_DECL + f"<p:presentationPr {PX_NS}/>",
        "ppt/viewProps.xml": XML_DECL + f'<p:viewPr {PX_NS}><p:gridSpacing cx="76200" cy="76200"/></p:viewPr>',
        "ppt/tableStyles.xml": XML_DECL + f'<a:tblStyleLst xmlns:a="{NS_A}" '
                                          'def="{5C22544A-7EE6-4342-B048-85BDC9FD1C3A}"/>',
    }
    over = {"ppt/presentation.xml": f"{PX_CT}.presentation.main+xml",
            "ppt/slideMasters/slideMaster1.xml": f"{PX_CT}.slideMaster+xml",
            "ppt/slideLayouts/slideLayout1.xml": f"{PX_CT}.slideLayout+xml",
            "ppt/notesMasters/notesMaster1.xml": f"{PX_CT}.notesMaster+xml",
            "ppt/theme/theme1.xml": "application/vnd.openxmlformats-officedocument.theme+xml",
            "ppt/theme/theme2.xml": "application/vnd.openxmlformats-officedocument.theme+xml",
            "ppt/presProps.xml": f"{PX_CT}.presProps+xml", "ppt/viewProps.xml": f"{PX_CT}.viewProps+xml",
            "ppt/tableStyles.xml": f"{PX_CT}.tableStyles+xml",
            "docProps/core.xml": "application/vnd.openxmlformats-package.core-properties+xml",
            "docProps/app.xml": "application/vnd.openxmlformats-officedocument.extended-properties+xml"}
    pres_rels = [("rId1", "slideMaster", "slideMasters/slideMaster1.xml"),
                 ("rId2", "notesMaster", "notesMasters/notesMaster1.xml"), ("rId3", "theme", "theme/theme1.xml"),
                 ("rId4", "presProps", "presProps.xml"), ("rId5", "viewProps", "viewProps.xml"),
                 ("rId6", "tableStyles", "tableStyles.xml")]
    sld_ids = []
    for k, (shapes, notes, extra) in enumerate(deck.slides, 1):
        parts[f"ppt/slides/slide{k}.xml"] = (XML_DECL + f'<p:sld {PX_NS}><p:cSld><p:spTree>{PX_GRP}{shapes}'
                                             '</p:spTree></p:cSld><p:clrMapOvr><a:masterClrMapping/></p:clrMapOvr>'
                                             '</p:sld>')
        parts[f"ppt/slides/_rels/slide{k}.xml.rels"] = rels(
            [("rId1", "slideLayout", "../slideLayouts/slideLayout1.xml"),
             ("rId2", "notesSlide", f"../notesSlides/notesSlide{k}.xml"), *extra])
        parts[f"ppt/notesSlides/notesSlide{k}.xml"] = _px_notes_slide(notes, st)
        parts[f"ppt/notesSlides/_rels/notesSlide{k}.xml.rels"] = rels(
            [("rId1", "notesMaster", "../notesMasters/notesMaster1.xml"), ("rId2", "slide", f"../slides/slide{k}.xml")])
        over[f"ppt/slides/slide{k}.xml"] = f"{PX_CT}.slide+xml"
        over[f"ppt/notesSlides/notesSlide{k}.xml"] = f"{PX_CT}.notesSlide+xml"
        pres_rels.append((f"rId{6 + k}", "slide", f"slides/slide{k}.xml"))
        sld_ids.append(f'<p:sldId id="{255 + k}" r:id="rId{6 + k}"/>')
        for _rid, _typ, target in extra:
            parts["ppt/media/" + target.rsplit("/", 1)[-1]] = brand.logo_bytes
    parts["ppt/presentation.xml"] = (
        XML_DECL + f'<p:presentation {PX_NS} saveSubsetFonts="1"><p:sldMasterIdLst><p:sldMasterId id="2147483648" '
        'r:id="rId1"/></p:sldMasterIdLst><p:notesMasterIdLst><p:notesMasterId r:id="rId2"/></p:notesMasterIdLst>'
        f'<p:sldIdLst>{"".join(sld_ids)}</p:sldIdLst><p:sldSz cx="{PX_SLIDE_W}" cy="{PX_SLIDE_H}"/>'
        f'<p:notesSz cx="{PX_NOTES_W}" cy="{PX_NOTES_H}"/></p:presentation>')
    parts["ppt/_rels/presentation.xml.rels"] = rels(pres_rels)
    parts["[Content_Types].xml"] = content_types(
        {"rels": "application/vnd.openxmlformats-package.relationships+xml", "xml": "application/xml",
         "png": "image/png", "jpeg": "image/jpeg"}, over)
    return zip_bytes(parts)


# ----------------------------------------------------------------------------- reading a deck back

def _px_text_of(xml: bytes) -> str:
    """The text of a slide or notes part: the a:t runs of each a:p joined, one line per paragraph."""
    root = px_ET.fromstring(xml)
    lines = []
    for p in root.iter(f"{{{NS_A}}}p"):
        lines.append("".join(t.text or "" for t in p.iter(f"{{{NS_A}}}t")))
    return "\n".join(lines)


def _px_numbered(data: bytes, rx: str) -> list:
    z = zipfile.ZipFile(io.BytesIO(data))
    names = [n for n in z.namelist() if re.fullmatch(rx, n)]
    names.sort(key=lambda n: int(re.search(r"(\d+)\.xml$", n).group(1)))
    return [_px_text_of(z.read(n)) for n in names]


def pptx_slides_text(data: bytes) -> list:
    """The visible text of each slide, in slide order (paragraphs on separate lines)."""
    return _px_numbered(data, r"ppt/slides/slide\d+\.xml")


def pptx_notes_text(data: bytes) -> list:
    """The text of each slide's notes, in slide order."""
    return _px_numbered(data, r"ppt/notesSlides/notesSlide\d+\.xml")


# ----------------------------------------------------------------------------- the format

def _px_labels(ctx) -> dict:
    if ctx.labels:
        return ctx.labels
    try:
        return load_labels(ctx.pack.get("lang") or "en")
    except ValueError:                                         # check-pack reports a bad lang
        return load_labels("en")


def render_pptx(ctx) -> list:
    """<pack>.pptx (<pack>.learner.pptx for the learner view): the deck as bytes; guard_text is every slide's and
    every note's text."""
    pack = ctx.pack
    L = _px_labels(ctx)
    lang = pack.get("lang") if isinstance(pack.get("lang"), str) and LOCALE_RX.fullmatch(pack["lang"]) else "en"
    rtl = (pack.get("dir") or text_dir(L)) == "rtl"
    m = PX_HEX_RX.match(str((ctx.brand.accent if ctx.brand is not None else None) or ""))
    st = _PxStyle(lang, rtl, m.group(1).upper() if m else PX_DEFAULT_ACCENT)
    deck = _px_slides(ctx, L, st)
    data = _px_package(deck, str(pack.get("title", "")), ctx.generated)
    guard = "\n".join(pptx_slides_text(data) + pptx_notes_text(data))
    return [Output(output_name(pack["pack"], "pptx", view=ctx.view), data, guard)]


register("pptx", render_pptx, help="<pack>.pptx: a 16:9 slide deck, with citations and full text in the notes")
