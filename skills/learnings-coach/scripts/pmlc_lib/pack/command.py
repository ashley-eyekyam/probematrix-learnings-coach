"""The pack command (moved from pack/html.py, Ruling P4-4): check the pack, run each --format through the render
registry, run the name guard over every output, then write them (shared copies under their own names)."""
from __future__ import annotations

import json
import sys
from pathlib import Path

from ..dashboard.data import embedded_records, print_witness_note, resolve_embed
from ..ninem_session import NINE_M_MAP_FILE, NINE_M_PACK, nine_m_map, read_session
from ..handling import (effective_handling, name_guard, share_ctx, share_gate, share_mode, shared_copy, SHARED_LINE,
                        shared_name)
from ..pack.html import follow_up, update_gaps
from ..pack.profiles import BANNERS
from ..pack.schema import _checked as _pack_checked, embedded_ids, record_check, with_item_ids
from ..render import build_date, DEFAULT_FORMATS, render, RenderContext
from ..render.brand import load_brand, shared_brand
from ..render.exports import follow_up_csv, KEEP_FORMATS, OQ_FOLLOW_UP_FILE, open_questions_csv, refuse_existing
from ..util import _abs, write_json
from ..workspace import is_standard_ws, outputs_dir, warn_stale

PAPER_IGNORED = "--paper applies to --layout cards only; ignored"
WRITTEN_AS = {"html": "HTML", "md": "Markdown"}          # the v1 "<what> written to <path>" lines
INDUSTRY_NEEDS_PUBLIC = "an industry alert is shared with --share public"
REVIEW_COPY_ID = "alert-review-copy"


def review_copy_needed(pack, share_mode) -> bool:
    """P6-4: a sister-site pack written without --share external|public, or an industry pack written without --share
    public, is a review copy: every format opens with BANNERS["alert-review-copy"]."""
    mode = pack.get("mode") if isinstance(pack, dict) else None
    if mode == "sister-site":
        return share_mode not in ("external", "public")
    if mode == "industry":
        return share_mode != "public"
    return False


def with_review_copy(pack) -> dict:
    """The render copy of a pack with the review-copy banner as the first item of its first section. The caller passes
    a copy (with_item_ids makes one): the pack JSON on disk is never changed."""
    secs = pack.get("sections") or []
    if secs:
        secs[0]["items"].insert(0, {"kind": "para", "id": REVIEW_COPY_ID, "text": BANNERS["alert-review-copy"]})
    return pack


def pack_formats(a) -> list:
    """The formats to write: --format (default html,md), less md under --no-md."""
    fmts = list(getattr(a, "format", None) or DEFAULT_FORMATS)
    return [f for f in fmts if not (f == "md" and getattr(a, "no_md", False))]


def cmd_pack(a):
    """Render a checked pack. --share external|public: the share gate first (P2-9), then every format is rendered from
    masked copies of the pack and the workspace. In any mode the name guard runs over every output before anything
    is written."""
    w, pack, res = _pack_checked(a, record_ok=False)
    if pack.get("mode") == "industry" and share_mode(a) == "external":      # P6-4: before the share gate's reasons
        sys.exit(INDUSTRY_NEEDS_PUBLIC)
    warn_stale(a.ws)
    mode = share_gate(pack, w, a, src=a.pack, ws=a.ws)
    record_check(a, pack, res, w)                                  # only now: a refused share records nothing
    ws = _abs(a.ws)
    run = ws.parent.name if is_standard_ws(ws) else ws.name
    embed = resolve_embed(a)
    eh = effective_handling(pack, w, src=a.pack, ws=a.ws)        # on the unmasked pack, before ids are filled in
    share = share_ctx(a, w, mode) if mode != "internal" else None
    rw, rpack = (shared_copy(w, share, w), shared_copy(pack, share, w)) if share else (w, pack)
    rp = with_item_ids(rpack)
    ctx = RenderContext(w=rw, pack=with_review_copy(rp) if review_copy_needed(pack, mode) else rp, run=run, generated=build_date(), embed=embed, eh=eh,
                        share=share, brand=shared_brand(load_brand(a.brand), share) if getattr(a, "brand", None) else None,
                        view=getattr(a, "view", None) or "full", src=Path(a.pack),
                        start=getattr(a, "start", None))
    ctx.layout, ctx.paper = getattr(a, "layout", None), getattr(a, "paper", None) or "A4"     # Task 13 (P4-7)
    ctx.base_url = getattr(a, "base_url", None)
    if getattr(a, "paper", None) and ctx.layout != "cards":
        ctx.notes.append(PAPER_IGNORED)
    outs = [(fmt, o) for fmt in pack_formats(a) for o in render(fmt, ctx)]
    if ctx.layout:                                                 # print layouts (P4-7): beside the formats
        from ..render.layouts import render_layout
        outs += [(f"{ctx.layout} layout", o) for o in render_layout(ctx)]
    coach = pack["pack"] == "investigator-coach" and mode == "internal"   # interview plans never leave the team
    fu_csv = follow_up_csv(pack) if coach else ""
    oq_csv = open_questions_csv(rpack) if pack["pack"] == "open-questions-register" else ""    # any mode, from the masked pack
    nm_map = ""                                                      # the 9M side output (Task 12), from the masked pack
    if pack["pack"] == NINE_M_PACK:
        nm_map = json.dumps(nine_m_map(ctx.pack, read_session(ws)), indent=1, ensure_ascii=False, sort_keys=True)
    name_guard([o.guard_text or "" for _, o in outs] + [fu_csv, oq_csv, nm_map], a)
    for note in ctx.notes:
        print(note, file=sys.stderr)
    out = Path(a.out) if a.out else outputs_dir(ws)
    if outs:
        out.mkdir(parents=True, exist_ok=True)
    for fmt, o in outs:                                            # files the organisation fills in: refuse first
        if fmt in KEEP_FORMATS:
            refuse_existing(shared_name(out / o.name, mode))
    for fmt, o in outs:
        path = shared_name(out / o.name, mode)
        if fmt in KEEP_FORMATS:                                      # keep \r\n rows as they are on every platform
            path.write_bytes(o.data.encode("utf-8"))
        elif isinstance(o.data, bytes):
            path.write_bytes(o.data)
        else:
            path.write_text(o.data, encoding="utf-8")
        if fmt == "html" and embed != "summary":                  # summary drops the text the note is about
            print_witness_note(embedded_records(rw, *embedded_ids(pack), (), embed, linked=False)[1], embed)
        print(f"{WRITTEN_AS.get(fmt, fmt)} written to {path}")
    if mode != "internal":
        print(SHARED_LINE.format(mode=mode))
    gj = update_gaps(ws, pack)
    if gj:
        print(f"Gaps written to {gj}")
    if nm_map:
        out.mkdir(parents=True, exist_ok=True)
        nm = shared_name(out / NINE_M_MAP_FILE, mode)
        nm.write_text(nm_map, encoding="utf-8")
        print(f"{NINE_M_MAP_FILE} written to {nm}")
    if oq_csv:                                                       # the organisation fills this in: never overwrite
        out.mkdir(parents=True, exist_ok=True)
        fu = shared_name(out / OQ_FOLLOW_UP_FILE, mode)
        if fu.exists():
            print(f"note: {fu} exists and was left as it is (the organisation may have filled it in)", file=sys.stderr)
        else:
            fu.write_bytes(oq_csv.encode("utf-8"))
            print(f"{OQ_FOLLOW_UP_FILE} written to {fu}")
    if coach:
        fu = out / "follow-up.json"
        out.mkdir(parents=True, exist_ok=True)
        write_json(fu, follow_up(pack))
        print(f"Follow-up fields written to {fu}")
        (out / "follow-up.csv").write_bytes(fu_csv.encode("utf-8"))
        print(f"follow-up.csv written to {out / 'follow-up.csv'}")
