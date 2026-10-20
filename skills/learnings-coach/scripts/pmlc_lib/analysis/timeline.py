"""The timeline command: dated precursor candidates."""
from __future__ import annotations

import collections
import datetime as dt
import re
import sys
from pathlib import Path

from ..util import iso_date, write_json
from ..workspace import file_sha256, incident_date, load_ws, record_derived


# ----------------------------------------------------------------------------- timeline

MONTHS = "jan|feb|mar|apr|may|jun|jul|aug|sep|sept|oct|nov|dec"
DATE_RXS = [
    re.compile(r"\b(\d{1,2})[./-](\d{1,2})[./-](\d{4})\b"),
    re.compile(rf"\b(\d{{1,2}})[ -]({MONTHS})[a-z]*[ -,]*(\d{{4}})\b", re.I),
    re.compile(rf"\b({MONTHS})[a-z]*\.?\s+(\d{{4}})\b", re.I),
    re.compile(r"\b(19[5-9]\d|20[0-4]\d)\b"),
]
MIDX = {m: i + 1 for i, m in enumerate(["jan", "feb", "mar", "apr", "may", "jun", "jul", "aug", "sep", "oct", "nov", "dec"])}


def _parse_dates(text):
    hits, spans = [], []
    for i, rx in enumerate(DATE_RXS):
        for m in rx.finditer(text):
            if any(s <= m.start() < e for s, e in spans):
                continue
            try:
                if i == 0:
                    d = dt.date(int(m.group(3)), int(m.group(2)), int(m.group(1)))
                elif i == 1:
                    d = dt.date(int(m.group(3)), MIDX[m.group(2).lower()[:3]], int(m.group(1)))
                elif i == 2:
                    d = dt.date(int(m.group(2)), MIDX[m.group(1).lower()[:3]], 1)
                else:
                    d = dt.date(int(m.group(1)), 1, 1)
            except (ValueError, KeyError):
                continue
            spans.append((m.start(), m.end()))
            hits.append((d, i, m.start(), m.end()))
    return hits


CLOCK_RX = re.compile(r"\b([01]?\d|2[0-3])[:.]([0-5]\d)(?::[0-5]\d)?\s*(?:hours?\b|hrs?\b|h\b)?")
PRECISION_RANK = {"day": 0, "month": 1, "year": 2}


def months_between(a: dt.date, b: dt.date) -> int:
    """Whole months from a to b (negative when a is after b)."""
    return (b.year - a.year) * 12 + b.month - a.month - (b.day < a.day)


def _clock_times(text, start=0, end=None):
    """Clock times in text[start:end] as (match start, match end, 'HH:MM'). A '.' separator needs an hrs/h suffix, so
    decimals and dd.mm.yyyy dates are not read as times."""
    out = []
    for m in CLOCK_RX.finditer(text, start, len(text) if end is None else end):
        if text[m.end(1)] == "." and not re.search(r"h(ours?|rs?)?$", m.group(0).rstrip()):
            continue
        out.append((m.start(), m.end(), f"{int(m.group(1)):02d}:{m.group(2)}"))
    return out


NARRATIVE_SOURCE = "narrative"


def _event_day_sequence(w, day, sources):
    """One entry per minute: {time, mentions, sources, snippets}, sorted by time. `sources` holds citable Finding and
    Evidence IDs only; a time the narrative mentions sets `narrative: true` instead.

    A time counts when its sentence holds no day-precision date other than `day`. A sentence with no date at all
    counts only when `day` is the incident date, since undated times in an export describe the incident day."""
    found = {}
    undated_ok = day == incident_date(w)
    for sid, text in sources:
        cuts = [0] + [m.end() for m in re.finditer(r"\. |\n", text)] + [len(text)]
        for s, e, hhmm in _clock_times(text):
            i = max(j for j in range(len(cuts) - 1) if cuts[j] <= s)
            sentence = text[cuts[i]: cuts[i + 1]]
            days = [d.isoformat() for d, prec, _, _ in _parse_dates(sentence) if prec <= 1]
            if any(d != day for d in days) or (not days and not undated_ok):
                continue
            ev = found.setdefault(hhmm, {"time": hhmm, "mentions": 0, "sources": [], "snippets": []})
            ev["mentions"] += 1
            if sid == NARRATIVE_SOURCE:       # the narrative has no FND/EVD id to cite: flag it, never list it
                ev["narrative"] = True
            elif sid not in ev["sources"]:
                ev["sources"].append(sid)
            snip = re.sub(r"\s+", " ", text[max(0, s - 100): e + 100]).strip()
            if len(ev["snippets"]) < 3 and snip not in ev["snippets"]:
                ev["snippets"].append(snip)
    return sorted(found.values(), key=lambda x: x["time"])


def cmd_timeline(a):
    ws = Path(a.ws)
    w = load_ws(ws)
    inc_date = incident_date(w)
    before = a.before
    if before and before != "incident" and not iso_date(before):
        print('--before: use YYYY-MM-DD or "incident"', file=sys.stderr)
        sys.exit(2)
    if before == "incident":
        before = inc_date
        if not before:
            sys.exit("No incident date in this workspace; pass --date to ingest.")
    day = a.on
    if day == "incident":
        day = inc_date
        if not day:
            sys.exit("No incident date in this workspace; pass --date to ingest.")
    elif day:
        try:
            dt.date.fromisoformat(day)
        except ValueError:
            sys.exit("--on takes a YYYY-MM-DD date or the word incident.")
    findings = w["findings"]
    evidence = w.get("evidence", {})
    if a.entity:
        cl = w.get("clusters", {}).get("findings")
        if cl is None:
            sys.exit("Needs clusters.json. Run: pmlc.py classify <ws>")
        keep = {f["id"] for f in findings if set(a.entity) & set(cl.get(f["id"], {}).get("F", []))}
        keep_ev = {e for f in findings if f["id"] in keep for e in f["evidence"]}
        findings = [f for f in findings if f["id"] in keep]
        evidence = {k: v for k, v in evidence.items() if v["id"] in keep_ev}
    events = collections.OrderedDict()
    sources = [(f["id"], f["code"], " ".join([f["label"], f["short"], f["justification"], f["causal"]]))
               for f in findings]
    sources += [(e["id"], e["type"], e["description"]) for e in evidence.values()]
    min_rank = PRECISION_RANK[a.min_precision]
    for sid, kind, text in sources:
        for d, prec, s, e in _parse_dates(text):
            if before and d.isoformat() > before:
                continue
            precision = ["day", "day", "month", "year"][prec]
            if PRECISION_RANK[precision] > min_rank:
                continue
            snippet = text[max(0, s - 140): e + 140].replace("\n", " ").strip()
            key = (d.isoformat(), prec, re.sub(r"\W+", " ", text[max(0, s - 40): e + 40]).lower()[:60])
            ev = events.setdefault(key, {"date": d.isoformat(), "precision": precision,
                                         "snippet": snippet, "sources": []})
            if precision == "day" and "time" not in ev:
                times = _clock_times(text, e, e + 40)
                if times:
                    ev["time"] = times[0][2]
            if sid not in ev["sources"]:
                ev["sources"].append(sid)
    items = sorted(events.values(), key=lambda x: (x["date"], x["precision"]))
    # collapse near-duplicate snippets per date
    merged = collections.OrderedDict()
    for it in items:
        k = (it["date"], it["precision"])
        if k in merged and len(merged[k]) >= a.per_date:
            continue
        merged.setdefault(k, []).append(it)
    flat = [x for v in merged.values() for x in v]
    inc = dt.date.fromisoformat(inc_date) if inc_date else None
    for it in flat:
        d = dt.date.fromisoformat(it["date"])
        if it["precision"] == "year":
            it["months_before"] = None
            it["years_before"] = inc.year - d.year if inc else None
        else:
            it["months_before"] = months_between(d, inc) if inc else None
    write_json(ws / "timeline_candidates.json", flat)
    record_derived(ws, "timeline_candidates.json",
                   {n: file_sha256(ws / n) for n in ("findings.json", "evidence.json") if (ws / n).exists()})
    print(f"{len(flat)} dated precursor candidates written to {ws/'timeline_candidates.json'} "
          f"(the precursor-timeline skill curates these).\n")
    print("| Date | Precision | Sources | Snippet |\n|---|---|---|---|")
    for it in flat[: a.show]:
        when = it["date"] + (f" {it['time']}" if it.get("time") else "")
        print(f"| {when} | {it['precision']} | {', '.join(it['sources'][:4])} | {it['snippet'][:160]} |")
    if day:
        texts = [(x[0], x[2]) for x in sources]
        texts.append((NARRATIVE_SOURCE, w.get("incident", {}).get("narrative", "")))
        seq = _event_day_sequence(w, day, texts)
        write_json(ws / "timeline_event_day.json", seq)
        record_derived(ws, "timeline_event_day.json",
                       {n: file_sha256(ws / n) for n in ("findings.json", "evidence.json", "incident.json")
                        if (ws / n).exists()})
        print(f"\n{len(seq)} clock times on {day} written to {ws/'timeline_event_day.json'}.\n")
        print("| Time | Mentions | Sources | Snippet |\n|---|---:|---|---|")
        for it in seq[: a.show]:
            print(f"| {it['time']} | {it['mentions']} | {', '.join(it['sources'][:4])} | {it['snippets'][0][:160]} |")
