"""The `srt` and `narration` data formats (L4-19): from each `script` item, `<pack>.<item-id>.srt` (subtitles for the
video) and `<pack>.<item-id>.narration.txt` (the words for a voice-over or a PA reader). Both hold the narration
only: no title, no visual, no citations, and no status line, because whatever is in them is shown on screen or
spoken aloud (Ruling P4-20). The shooting script in html, md and docx carries the status for them."""
from __future__ import annotations

import re
import textwrap

from ..pack.schema import ID_RX
from . import NOTHING_TO_WRITE, Output, output_name, register

SRT_WIDTH = 42                    # characters per subtitle line
SRT_LINES = 2                     # lines per cue
SC_BRACKET_RX = re.compile(r"\s*\[\s*(?:FND-[0-9A-Za-z]{4,}|EVD-\d{3,})(?:\s*[;,]\s*(?:FND-[0-9A-Za-z]{4,}|EVD-\d{3,}))*\s*\]")
SC_SPACE_RX = re.compile(r"\s+([,.;:!?])")


def spoken(text) -> str:
    """The narration as it is said: inline citations ([FND-…; EVD-…] and bare IDs) removed, whitespace collapsed."""
    s = ID_RX.sub("", SC_BRACKET_RX.sub("", str(text)))
    return SC_SPACE_RX.sub(r"\1", " ".join(s.split()))


def srt_time(ms: int) -> str:
    """Milliseconds as an SRT timestamp, HH:MM:SS,mmm."""
    h, rest = divmod(int(ms), 3_600_000)
    m, rest = divmod(rest, 60_000)
    s, ms_ = divmod(rest, 1000)
    return f"{h:02d}:{m:02d}:{s:02d},{ms_:03d}"


def srt_ms(stamp: str) -> int:
    """An SRT timestamp back to milliseconds."""
    hms, ms = stamp.split(",")
    h, m, s = (int(x) for x in hms.split(":"))
    return ((h * 60 + m) * 60 + s) * 1000 + int(ms)


def srt_cues(text, duration_ms: int, start: int = 0) -> list:
    """[(start_ms, end_ms, lines)]: the text wrapped at SRT_WIDTH, SRT_LINES lines a cue; a longer text becomes
    consecutive cues that share duration_ms evenly. [] for text with no words."""
    lines = textwrap.wrap(str(text), SRT_WIDTH, break_long_words=True, break_on_hyphens=False)
    chunks = [lines[i:i + SRT_LINES] for i in range(0, len(lines), SRT_LINES)]
    n = len(chunks)
    return [(start + i * duration_ms // n, start + (i + 1) * duration_ms // n, c) for i, c in enumerate(chunks)]


def _sc_scripts(pack) -> list:
    return [it for s in pack.get("sections") or [] for it in s.get("items") or []
            if isinstance(it, dict) and it.get("kind") == "script" and isinstance(it.get("segments"), list)]


def _sc_segments(it) -> list:
    return [sg for sg in it["segments"] if isinstance(sg, dict)]


def _sc_seconds(sg) -> int:
    s = sg.get("seconds")
    return s if isinstance(s, int) and not isinstance(s, bool) and s > 0 else 0


def _sc_srt(it) -> str:
    """One cue per segment, timed cumulatively from 00:00:00,000; a long narration splits evenly over its segment."""
    cues, t0 = [], 0
    for sg in _sc_segments(it):
        dur = _sc_seconds(sg) * 1000
        cues += srt_cues(spoken(sg.get("narration") or ""), dur, t0)
        t0 += dur
    return "".join(f"{n}\n{srt_time(a)} --> {srt_time(b)}\n" + "\n".join(lines) + "\n\n"
                   for n, (a, b, lines) in enumerate(cues, 1))


def _sc_narration(it) -> str:
    """The narration only: one paragraph per segment, blank lines between."""
    paras = [spoken(sg.get("narration") or "") for sg in _sc_segments(it)]
    return "\n\n".join(p for p in paras if p) + "\n"


def _sc_render(ctx, fmt, ext, build) -> list:
    items = _sc_scripts(ctx.pack)
    if not items:
        ctx.notes.append(NOTHING_TO_WRITE.format(fmt=fmt, why="no script items"))
        return []
    out = []
    for it in items:
        text = build(it)
        out.append(Output(output_name(ctx.pack["pack"], ext, item_id=it.get("id")), text, text))
    return out


def render_srt(ctx) -> list:
    """`<pack>.<item-id>.srt` for each script item (SubRip, UTF-8)."""
    return _sc_render(ctx, "srt", "srt", _sc_srt)


def render_narration(ctx) -> list:
    """`<pack>.<item-id>.narration.txt` for each script item: the narration only."""
    return _sc_render(ctx, "narration", "narration.txt", _sc_narration)


register("srt", render_srt, kind="data", help="<pack>.<item-id>.srt: subtitles from each script item's narration")
register("narration", render_narration, kind="data",
         help="<pack>.<item-id>.narration.txt: each script item's narration only, for a voice-over or a PA reader")
