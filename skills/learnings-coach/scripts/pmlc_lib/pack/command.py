"""The pack command (moved from pack/html.py, Ruling P4-4): check the pack, run each --format through the render
registry, run the name guard over every output, then write them (shared copies under their own names)."""
from __future__ import annotations

import sys
from pathlib import Path

from ..dashboard.data import embedded_records, print_witness_note, resolve_embed
from ..handling import effective_handling, name_guard, share_ctx, share_gate, shared_copy, SHARED_LINE, shared_name
from ..pack.html import follow_up, update_gaps
from ..pack.schema import _checked as _pack_checked, embedded_ids, record_check, with_item_ids
from ..render import build_date, DEFAULT_FORMATS, render, RenderContext
from ..render.exports import follow_up_csv, KEEP_FORMATS, refuse_existing
from ..util import _abs, write_json
from ..workspace import is_standard_ws, outputs_dir, warn_stale

WRITTEN_AS = {"html": "HTML", "md": "Markdown"}          # the v1 "<what> written to <path>" lines


def pack_formats(a) -> list:
    """The formats to write: --format (default html,md), less md under --no-md."""
    fmts = list(getattr(a, "format", None) or DEFAULT_FORMATS)
    return [f for f in fmts if not (f == "md" and getattr(a, "no_md", False))]


def cmd_pack(a):
    """Render a checked pack. --share external|public: the share gate first (P2-9), then every format is rendered from
    masked copies of the pack and the workspace. In any mode the name guard runs over every output before anything
    is written."""
    w, pack, res = _pack_checked(a, record_ok=False)
    warn_stale(a.ws)
    mode = share_gate(pack, w, a, src=a.pack, ws=a.ws)
    record_check(a, pack, res, w)                                  # only now: a refused share records nothing
    ws = _abs(a.ws)
    run = ws.parent.name if is_standard_ws(ws) else ws.name
    embed = resolve_embed(a)
    eh = effective_handling(pack, w, src=a.pack, ws=a.ws)        # on the unmasked pack, before ids are filled in
    share = share_ctx(a, w, mode) if mode != "internal" else None
    rw, rpack = (shared_copy(w, share, w), shared_copy(pack, share, w)) if share else (w, pack)
    ctx = RenderContext(w=rw, pack=with_item_ids(rpack), run=run, generated=build_date(), embed=embed, eh=eh,
                        share=share, view=getattr(a, "view", None) or "full", src=Path(a.pack))
    outs = [(fmt, o) for fmt in pack_formats(a) for o in render(fmt, ctx)]
    coach = pack["pack"] == "investigator-coach" and mode == "internal"   # interview plans never leave the team
    fu_csv = follow_up_csv(pack) if coach else ""
    name_guard([o.guard_text or "" for _, o in outs] + [fu_csv], a)
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
    if coach:
        fu = out / "follow-up.json"
        out.mkdir(parents=True, exist_ok=True)
        write_json(fu, follow_up(pack))
        print(f"Follow-up fields written to {fu}")
        (out / "follow-up.csv").write_bytes(fu_csv.encode("utf-8"))
        print(f"follow-up.csv written to {out / 'follow-up.csv'}")
