"""Follow-up dates as a calendar file (L4-23, Ruling P4-20): <pack>.ics, one all-day event for each check, decision or
recommendation whose time is a plain offset ("30 days", "Day 14", "2 weeks"). The coach never sets a date by itself:
the offsets count from --start. No attendee and no organiser are written, so importing the file invites nobody."""
from __future__ import annotations

import datetime as dt
import re

from .. import BRAND, STATUS_PHRASE
from ..handling import status_line
from . import build_date, ICS_NEEDS_START, NOTHING_TO_WRITE, Output, output_name, register
from .fields import item_text

_IC_OFFSET_RXS = ((re.compile(r"^(\d{1,3}) days?$"), 1), (re.compile(r"^day (\d{1,3})$"), 1),
                  (re.compile(r"^(\d{1,2}) weeks?$"), 7))
_IC_WHEN_FIELD = {"check": "when", "decision": "by_when", "recommendation": "by_when"}
IC_SUMMARY_MAX = 70


def _ic_offset(when):
    """The offset in days of a "<n> days", "day <n>" or "<n> weeks" time (any case), else None."""
    if not isinstance(when, str):
        return None
    t = " ".join(when.split()).lower()
    for rx, mult in _IC_OFFSET_RXS:
        m = rx.match(t)
        if m:
            return int(m.group(1)) * mult
    return None


def _ic_esc(s) -> str:
    """TEXT value escaping (RFC 5545): backslash, semicolon and comma escaped, line breaks as \\n."""
    s = " ".join(str(s).split()) if "\n" in str(s) or "\r" in str(s) else str(s)
    return s.replace("\\", "\\\\").replace(";", "\\;").replace(",", "\\,")


def _ic_fold(line: str) -> str:
    """Lines of at most 75 octets: the rest follows after CRLF and a space, never inside a UTF-8 character."""
    out, cur, n = [], "", 0
    for ch in line:
        k = len(ch.encode("utf-8"))
        if n + k > (75 if not out else 74):
            out.append(cur)
            cur, n = "", 0
        cur, n = cur + ch, n + k
    out.append(cur)
    return "\r\n ".join(out)


def _ic_cut(s: str, n: int = IC_SUMMARY_MAX) -> str:
    s = " ".join(str(s).split())
    return s if len(s) <= n else s[: n - 1].rstrip() + "…"


def _ic_events(ctx) -> list:
    """[(item, days)] in pack order."""
    out = []
    for s in ctx.pack["sections"]:
        for it in s["items"]:
            f = _IC_WHEN_FIELD.get(it.get("kind"))
            days = _ic_offset(it.get(f)) if f else None
            if days is not None:
                out.append((it, days))
    return out


def render_ics(ctx) -> list:
    if ctx.start is None:
        ctx.notes.append(ICS_NEEDS_START)
        return []
    events = _ic_events(ctx)
    if not events:
        ctx.notes.append(NOTHING_TO_WRITE.format(fmt="ics", why="no check, decision or recommendation has a time "
                                                 "like '30 days', 'Day 14' or '2 weeks'"))
        return []
    pack = ctx.pack["pack"]
    stamp = build_date().replace("-", "") + "T000000Z"
    lead = "" if ctx.share else f"{ctx.run}-"                  # a shared copy carries no run slug
    lines = ["BEGIN:VCALENDAR", "VERSION:2.0", "PRODID:-//ProbeMatrix Learnings Coach//pmlc//EN", "CALSCALE:GREGORIAN",
             f"X-PMLC-STATUS:{_ic_esc(status_line(ctx.pack['status']))}", f"X-PMLC-BRAND:{_ic_esc(BRAND)}"]
    guard = []
    for it, days in events:
        day = ctx.start + dt.timedelta(days=days)
        summary = _ic_cut(item_text(it))
        cites = ", ".join(it.get("cites") or [])
        desc = (f"Cites: {cites}. " if cites else "") + STATUS_PHRASE
        guard += [summary, desc]
        lines += ["BEGIN:VEVENT", f"UID:{lead}{pack}-{it['id']}@pmlc", f"DTSTAMP:{stamp}",
                  f"DTSTART;VALUE=DATE:{day.strftime('%Y%m%d')}", f"SUMMARY:{_ic_esc(summary)}",
                  f"DESCRIPTION:{_ic_esc(desc)}", "END:VEVENT"]
    lines.append("END:VCALENDAR")
    data = ("\r\n".join(_ic_fold(x) for x in lines) + "\r\n").encode("utf-8")      # bytes: CRLF stays CRLF
    return [Output(output_name(pack, "ics"), data, "\n".join(guard))]


register("ics", render_ics, kind="data", help="<pack>.ics: all-day follow-up events from checks, decisions and "
         "recommendations with a time like '30 days'; needs --start")
