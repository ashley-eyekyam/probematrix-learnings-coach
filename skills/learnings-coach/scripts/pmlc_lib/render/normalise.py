"""The normalised pack (L4-11, Ruling P4-23): <pack>.normalised.json, a data format for other tools. It holds the
pack's content with every item id filled in, plus what a reader of the page would otherwise have to work out:
the status line, the brand, the effective status, the word count, the coverage counts and the cited records."""
from __future__ import annotations

import json

from .. import BRAND, VERSION_STAMP
from ..handling import status_line
from ..pack.markdown import coverage
from ..pack.schema import cited_ids, with_item_ids
from . import build_date, Output, output_name, register
from .fields import pack_words, reading_minutes
from .labels import load_labels, text_dir

NORMALISED_VERSION = 1


def _nm_dir(lang) -> str:
    try:
        return text_dir(load_labels(lang))
    except ValueError:                                           # check-pack reports a bad lang
        return "ltr"


def normalise(w: dict, pack: dict, *, eh: dict, run: str = None, share=None, generated: str = None) -> dict:
    """The normalised pack as a dict. A shared copy (share given) carries no run slug."""
    pack = with_item_ids(pack)
    cov = coverage(w, pack)
    fids, eids = cited_ids(pack)
    F = {f["id"]: f for f in w["findings"]}
    E = w.get("evidence", {})
    cites = {x: {"label": F[x].get("label"), "level": F[x].get("level"), "rating": F[x].get("rating")}
             for x in fids if x in F}
    cites.update({x: {"type": E[x].get("type")} for x in eids if x in E})
    lang = pack.get("lang") or "en"
    out = {"normalised_version": NORMALISED_VERSION, "schema": pack.get("schema"), "generator": VERSION_STAMP,
           "generated": generated or build_date(), "pack": pack["pack"], "skill": pack.get("skill"), "lang": lang,
           "dir": pack.get("dir") or _nm_dir(lang), "status": status_line(pack["status"]),
           "brand": BRAND, "effective_status": eh.get("effective_status", "draft"), "words": pack_words(pack),
           "reading_minutes": reading_minutes(pack),
           "coverage": {k: cov[k] for k in ("cited", "relevant", "top_cited", "top_relevant")},
           "citations": cites, "bottom_line": pack["bottom_line"], "sections": pack["sections"]}
    if share is None and run:
        out["run"] = run
    return out


def _nm_render(ctx) -> list:
    d = normalise(ctx.w, ctx.pack, eh=ctx.eh, run=ctx.run, share=ctx.share, generated=ctx.generated)
    text = json.dumps(d, indent=1, ensure_ascii=False) + "\n"
    return [Output(output_name(ctx.pack["pack"], "normalised.json"), text, text)]


register("normalised", _nm_render, kind="data", help="<pack>.normalised.json: the pack with ids, coverage and "
         "the cited records, for other tools")
