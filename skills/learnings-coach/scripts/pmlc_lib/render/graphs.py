"""Graph items as stand-alone files (L4-24, Rulings P4-18, P4-20, owner decision OD4-2): one <pack>.<item-id>.svg per
graph item with every label whole, a PNG of it through a Chromium-family browser, and a GraphML file for yEd and
other graph tools. The status phrase and the brand sit in the <desc> of each file."""
from __future__ import annotations

import html
import os
import re
import subprocess
import tempfile
from pathlib import Path

from .. import BRAND
from ..handling import status_line
from ..pack.graph_layout import layout_graph
from . import find_browser, NOTHING_TO_WRITE, Output, output_name, PNG_NO_BROWSER, register
from .ooxml import XML_INVALID_RX, xml_text

_GX_CSS = ("svg{color:#4a5568}.node rect{fill:#fff;stroke:#1f3a5f;stroke-width:1.5}"
           ".node text{font-family:Arial,Helvetica,sans-serif;font-size:13px;fill:#111}"
           ".edge{fill:none;stroke:#4a5568;stroke-width:1.5}.edge.back{stroke-dasharray:5 4}"
           ".edge.skip{stroke-dasharray:2 3}")
_GX_SIZE_RX = re.compile(r'viewBox="0 0 (\d+) (\d+)"')
GX_PNG_TIMEOUT = 60


def _gx_items(ctx) -> list:
    return [it for s in ctx.pack["sections"] for it in s["items"] if it.get("kind") == "graph"]


def _gx_desc(ctx) -> str:
    return f"{status_line(ctx.pack['status'])} · {BRAND}"


def _gx_svg(ctx, it) -> str:
    """The standalone SVG of one graph item: the layout of the page, without the page's CSS, with nothing clipped."""
    nodes = [dict(n, label=XML_INVALID_RX.sub("", str(n["label"]))) for n in it["nodes"]]      # control characters
    g = layout_graph(nodes, it["edges"], uid=it["id"], max_nodes=max(60, len(nodes)), label_max=None)
    body = g["svg"]
    title = f"{ctx.pack.get('title') or ctx.pack['pack']}: {it['id']}"
    head = (f"<title>{xml_text(title)}</title><desc>{xml_text(_gx_desc(ctx))}</desc><style>{_GX_CSS}</style>"
            '<rect width="100%" height="100%" fill="#fff"/>')
    body = body.replace('<svg class="graph"', '<svg xmlns="http://www.w3.org/2000/svg" class="graph"', 1)
    end = body.index(">") + 1
    return '<?xml version="1.0" encoding="UTF-8"?>\n' + body[:end] + head + body[end:] + "\n"


def _gx_text(markup: str) -> str:
    """The words in a piece of markup (for the name guard)."""
    return " ".join(html.unescape(re.sub(r"<[^>]+>", " ", markup)).split())


def _gx_size(svg: str) -> tuple:
    m = _GX_SIZE_RX.search(svg)
    return int(m.group(1)), int(m.group(2))


def render_svg(ctx) -> list:
    items = _gx_items(ctx)
    if not items:
        ctx.notes.append(NOTHING_TO_WRITE.format(fmt="svg", why="the pack has no graph item"))
    outs = []
    for it in items:
        svg = _gx_svg(ctx, it)
        outs.append(Output(output_name(ctx.pack["pack"], "svg", item_id=it["id"]), svg, _gx_text(svg)))
    return outs


def _gx_png(browser: str, svg: str) -> tuple:
    """(png bytes, None) or (None, reason): the browser's screenshot of the SVG on a blank page."""
    w, h = _gx_size(svg)
    page = ('<!doctype html><meta charset="utf-8"><body style="margin:0">'
            + svg.split("?>", 1)[1].strip() + "</body>")
    with tempfile.TemporaryDirectory(prefix="pmlc-png-") as d:
        src, png = Path(d) / "graph.html", Path(d) / "graph.png"
        src.write_text(page, encoding="utf-8")
        cmd = [browser, "--headless", "--disable-gpu", "--hide-scrollbars", f"--screenshot={png}",
               f"--window-size={w},{h}", src.as_uri()]
        if hasattr(os, "geteuid") and os.geteuid() == 0:                  # Chromium refuses to run as root otherwise
            cmd.insert(2, "--no-sandbox")
        try:
            r = subprocess.run(cmd, capture_output=True, timeout=GX_PNG_TIMEOUT, stdin=subprocess.DEVNULL)
        except (OSError, subprocess.TimeoutExpired) as e:
            return None, type(e).__name__ if not isinstance(e, OSError) else str(e)
        if r.returncode != 0:
            return None, f"exit {r.returncode}"
        if not png.is_file() or png.stat().st_size == 0:
            return None, "no file written"
        return png.read_bytes(), None


def render_png(ctx) -> list:
    items = _gx_items(ctx)
    if not items:
        ctx.notes.append(NOTHING_TO_WRITE.format(fmt="png", why="the pack has no graph item"))
        return []
    browser = find_browser()
    if not browser:
        ctx.notes.append(PNG_NO_BROWSER)
        return []
    outs = []
    for it in items:
        svg = _gx_svg(ctx, it)
        data, why = _gx_png(browser, svg)
        if data is None:
            ctx.notes.append(f"png: the browser did not produce an image ({why})")
            continue
        outs.append(Output(output_name(ctx.pack["pack"], "png", item_id=it["id"]), data,
                           _gx_text(svg)))
    return outs


def _gx_graphml(ctx, it) -> str:
    x = xml_text
    out = ['<?xml version="1.0" encoding="UTF-8"?>',
           '<graphml xmlns="http://graphml.graphdrawing.org/xmlns" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"'
           ' xsi:schemaLocation="http://graphml.graphdrawing.org/xmlns http://graphml.graphdrawing.org/xmlns/1.0/graphml.xsd">',
           f"<desc>{x(_gx_desc(ctx))}</desc>",
           '<key id="label" for="node" attr.name="label" attr.type="string"/>',
           '<key id="elabel" for="edge" attr.name="label" attr.type="string"/>',
           f'<graph id="{x(it["id"])}" edgedefault="directed">']
    for n in it["nodes"]:
        out.append(f'<node id="{x(n["id"])}"><data key="label">{x(n["label"])}</data></node>')
    for k, e in enumerate(it["edges"]):
        lab = f'<data key="elabel">{x(e["label"])}</data>' if e.get("label") else ""
        out.append(f'<edge id="e{k}" source="{x(e["from"])}" target="{x(e["to"])}">{lab}</edge>')
    out += ["</graph>", "</graphml>", ""]
    return "\n".join(out)


def render_graphml(ctx) -> list:
    """One <pack>.<item-id>.graphml for each graph item (the name does not change with the item count)."""
    items = _gx_items(ctx)
    if not items:
        ctx.notes.append(NOTHING_TO_WRITE.format(fmt="graphml", why="the pack has no graph item"))
    outs = []
    for it in items:
        text = _gx_graphml(ctx, it)
        name = output_name(ctx.pack["pack"], "graphml", item_id=it["id"])
        outs.append(Output(name, text, _gx_text(text)))
    return outs


register("svg", render_svg, kind="data", help="<pack>.<item-id>.svg: each graph item as a stand-alone SVG, "
         "no label clipped")
register("png", render_png, kind="data", help="<pack>.<item-id>.png: the same through a Chromium-family browser "
         "(PMLC_BROWSER, chromium, google-chrome, microsoft-edge)")
register("graphml", render_graphml, kind="data", help="<pack>.<item-id>.graphml: the graph for yEd and other graph tools")
