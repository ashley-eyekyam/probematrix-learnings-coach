"""The output format registry (Rulings P4-1 to P4-6, P4-9): every format `pack --format` can write registers here
as a function of a RenderContext that returns Outputs. pack/command.py runs the formats, the name guard and the
writes; a format module only builds text or bytes. The fixed copy of Phase 4 lives here."""
from __future__ import annotations

import argparse
import collections
import dataclasses
import datetime as dt
import importlib
import os
import pathlib
import re
import shutil
import sys

READING_TIME = "About {n} min read"
TRANSLATION_NOTE = "Translated with AI assistance: have a fluent speaker check it before use"
CHECK_LINE = "Checked by (role): ________   Date: ________   Shift: ________"
NOTHING_TO_WRITE = "{fmt}: nothing to write ({why})"
PNG_NO_BROWSER = ("png: no Chromium-family browser found; open the .svg in a browser and export it, "
                  "or set PMLC_BROWSER")
ICS_NEEDS_START = "ics: needs --start YYYY-MM-DD; nothing written (the coach never sets dates by itself)"
MORE_IN_PACK = "{n} more items are in the full pack"
LEARNER_BANNER = "Learner view: answers are hidden"

Output = collections.namedtuple("Output", "name data guard_text")   # name: file name in the out dir;
#                                                                      data: str (written UTF-8) or bytes
Brand = collections.namedtuple("Brand", "organisation accent logo_bytes logo_mime")   # any field may be None
Format = collections.namedtuple("Format", "name fn kind help")         # kind: "document" | "data"
FORMATS = {}                       # name -> Format, in registration order
DEFAULT_FORMATS = ("html", "md")
FORMAT_KINDS = ("document", "data")
# Document formats that build their own learner view, because they also need the answer key: SCORM grades in the
# browser (P4-9, P4-11). render() hands them the full pack whatever --view says.
OWN_LEARNER_VIEW = {"scorm"}
BROWSERS = ("chromium", "chromium-browser", "google-chrome", "google-chrome-stable", "microsoft-edge", "msedge")


@dataclasses.dataclass
class RenderContext:
    w: dict
    pack: dict
    run: str
    generated: str
    embed: str
    eh: dict
    share: object = None
    labels: dict = None
    brand: Brand = None
    layout: str = None
    view: str = "full"
    base_url: str = None
    start: dt.date = None
    paper: str = "A4"
    src: pathlib.Path = None
    notes: list = dataclasses.field(default_factory=list)


def register(name: str, fn, *, kind: str = "document", help: str = "") -> None:  # noqa: A002 (the contract's name)
    """Add format `name`; a document format is read by a person, a data format is imported by a tool (P4-2)."""
    if kind not in FORMAT_KINDS:
        raise ValueError(f"format kind must be one of {', '.join(FORMAT_KINDS)}")
    old = FORMATS.get(name)
    if old is not None and old.fn is not fn:
        raise ValueError(f"format {name!r} is already registered by another function")
    FORMATS[name] = Format(name, fn, kind, help)


def render(name: str, ctx: RenderContext) -> list:
    """The Outputs of format `name`: [] (with a ctx.notes entry) when the format has nothing to write. The learner
    view (P4-9) is applied here, for document formats only; data formats keep the answer keys."""
    fmt = FORMATS[name]
    if ctx.view == "learner" and fmt.kind == "document" and name not in OWN_LEARNER_VIEW:
        from .fields import learner_view
        ctx = dataclasses.replace(ctx, pack=learner_view(ctx.pack))          # the same notes list
    return list(fmt.fn(ctx) or [])


def parse_formats(text: str) -> list:
    """argparse type for --format: a comma-separated list of registered names, duplicates dropped (P4-1)."""
    names = [x.strip() for x in str(text).split(",")]
    bad = [x for x in names if x not in FORMATS]
    if bad or not names:
        shown = ", ".join(repr(x) for x in bad) or "(none)"
        raise argparse.ArgumentTypeError(f"unknown format {shown}; choose from: {', '.join(FORMATS)}")
    return list(dict.fromkeys(names))


def output_name(pack_name: str, ext: str, *, layout=None, view="full", item_id=None) -> str:
    """<pack>[.<item_id>][.<layout>][.learner].<ext>; ext may hold a dot ("email.html")."""
    bits = [pack_name] + ([item_id] if item_id else []) + ([layout] if layout else [])
    return ".".join(bits + (["learner"] if view == "learner" else []) + [ext])


def epoch_date():
    """The UTC date of SOURCE_DATE_EPOCH, or None when it is unset or not a whole number."""
    v = os.environ.get("SOURCE_DATE_EPOCH")
    try:
        return dt.datetime.fromtimestamp(int(v), dt.timezone.utc).date() if v else None
    except (ValueError, OverflowError, OSError):
        return None


def build_date() -> str:
    """SOURCE_DATE_EPOCH as an ISO date when it is set, else today (P4-6)."""
    return (epoch_date() or dt.date.today()).isoformat()


def translation_lines(pack: dict) -> list:
    """[TRANSLATION_NOTE] for a pack that is a translation (translation_of), else [] (P4-13)."""
    return [TRANSLATION_NOTE] if isinstance(pack, dict) and pack.get("translation_of") else []


def find_browser():
    """A Chromium-family browser for --format png (P4-18): $PMLC_BROWSER when it names an executable, else the first
    of BROWSERS on PATH; None when there is none."""
    env = os.environ.get("PMLC_BROWSER")
    if env:
        hit = env if os.path.isfile(env) and os.access(env, os.X_OK) else shutil.which(env)
        if hit:
            return hit
        print(f"warning: PMLC_BROWSER={env} is not an executable; looking for a browser on PATH", file=sys.stderr)
    for n in BROWSERS:
        hit = shutil.which(n)
        if hit:
            return hit
    return None


# ----------------------------------------------------------------------------- html and md (the v1 renderers)

def _rn_html(ctx: RenderContext) -> list:
    from ..pack.html import render_pack_html
    page = render_pack_html(ctx.w, ctx.pack, ctx.run, ctx.generated, ctx.embed, eh=ctx.eh, share=ctx.share,
                            labels=ctx.labels, brand=ctx.brand)
    if ctx.view == "learner":
        banner = f'<p class="status learner">{LEARNER_BANNER}</p>'
        page, n = re.subn(r'(<p class="status">.*?</p>)', lambda m: m.group(1) + "\n" + banner, page, count=1, flags=re.S)
        if not n:                                       # no status line to sit under: the banner still shows
            page = page.replace("</h1>", "</h1>\n" + banner, 1)
    return [Output(output_name(ctx.pack["pack"], "html", view=ctx.view), page, page)]


def _rn_esc(s) -> str:
    import html as std_html
    return std_html.escape(str(s), quote=True)


def _rn_md(ctx: RenderContext) -> list:
    from ..handling import status_line
    from ..pack.markdown import render_pack_md
    text = render_pack_md(ctx.pack, ctx.w, eh=ctx.eh, share=ctx.share, labels=ctx.labels)
    if ctx.view == "learner":
        status = f"*{status_line(ctx.pack['status'])}*"
        banner = f"*{LEARNER_BANNER}*"
        text = text.replace(status, f"{status}\n\n{banner}", 1) if status in text else banner + "\n\n" + text
    return [Output(output_name(ctx.pack["pack"], "md", view=ctx.view), text, text)]


register("html", _rn_html, help="<pack>.html: the offline page")
register("md", _rn_md, help="<pack>.md: the same content as Markdown")


def _load() -> None:
    """Import every format module; each registers itself, so FORMATS is complete once this package is imported."""
    for mod in (
        "normalise",
        "graphs",
        "bowtie",
        "ics",
        "quiz",
        "email",
        "exports",
        "docx",
        "script",
        "pptx",
        "scorm",
    ):
        importlib.import_module(f"{__name__}.{mod}")


_load()
del _load              # not exported: the shims would rebind contracts._load (Ruling X4)
