"""Organisation events for `library publish` (spec §8.1, Ruling P6-11): site assessments, verification readings and
adoption responses, read from the files the organisation filled in and appended to events.jsonl.

- `cihh-events.jsonl` (from `consolidate`)  -> `site_assessment` events.
- `verification.jsonl` (`templates verification`) -> `verification` events, `month` from `check_date`.
- `adoption.csv` (`templates adoption`)     -> `status` events whose data holds the response as `adoption`.

Each event is built unmasked; publish runs it through deid.deidentify (its `data.site` becomes a site code) before it
is hashed. A file the organisation filled in wrongly refuses the publish (OrgFileError, naming the file and row). An
event for an lr_id the register does not hold is skipped with a note."""
from __future__ import annotations

import json
import re

from ..templates import OrgFileError, _outputs, load_adoption, load_verification

EVENTS_CIHH = "cihh-events.jsonl"
EVENTS_ANSWERS = ("present", "partly", "absent", "n/a")
EVENTS_MONTH_RX = re.compile(r"^(\d{4}-(0[1-9]|1[0-2]))")


def _events_clean(v):
    return " ".join(str(v).split()) if v is not None else ""


def _events_cihh(run, problems) -> list:
    f = _outputs(run) / EVENTS_CIHH
    if not f.is_file():
        return []
    rows = []
    for n, line in enumerate(f.read_text(encoding="utf-8-sig").splitlines(), 1):
        if not line.strip():
            continue
        try:
            d = json.loads(line)
        except ValueError:
            problems.append(f"{EVENTS_CIHH} line {n}: not valid JSON")
            continue
        if (not isinstance(d, dict) or d.get("type") != "site_assessment" or not d.get("lr_id")
                or not _events_clean(d.get("site")) or not _events_clean(d.get("answer"))):
            problems.append(f"{EVENTS_CIHH} line {n}: not a site assessment (needs lr_id, site and answer)")
            continue
        if _events_clean(d["answer"]) not in EVENTS_ANSWERS:
            problems.append(f"{EVENTS_CIHH} line {n}: answer '{_events_clean(d['answer'])}' must be one of "
                            + ", ".join(EVENTS_ANSWERS))
            continue
        rows.append(d)
    return rows


def collect_events(run, lib, codes, month: str = "", notes=None) -> list:
    """The organisation events of a run, as [{"type", "ll_id", "incident_key", "month", "source": "organisation",
    "data"}] (no event_hash yet), in file order: site assessments, verification readings, adoption.

    run: a workspace or run folder. lib: the opened Library (not read here; kept for the publish seam). codes:
    {lr_id: (ll_id, incident_key)} for the learnings of this publish. month: the publish month, used when a row
    carries no date. notes: a list that gets one line per skipped event. Raises OrgFileError when an organisation
    file is invalid; the problems name the file and the row."""
    notes = notes if notes is not None else []
    problems, out = [], []

    def add(etype, lr, mon, data, undated=False):
        if lr not in codes:
            notes.append(f"skipped an event for {lr}: the register has no such learning")
            return
        ll, ikey = codes[lr]
        ev = {"type": etype, "ll_id": ll, "incident_key": ikey, "month": mon or month,
              "source": "organisation", "data": data}
        if undated:
            ev["undated"] = True          # publish strips this; it lets a re-publish skip an unchanged undated reading
        out.append(ev)

    for d in _events_cihh(run, problems):
        data = {"lr_id": str(d["lr_id"]), "site": _events_clean(d["site"]), "answer": _events_clean(d["answer"])}
        if _events_clean(d.get("site_response")):
            data["site_response"] = _events_clean(d["site_response"])
        add("site_assessment", str(d["lr_id"]), month, data)
    try:
        ver = load_verification(run)
    except OrgFileError as e:
        problems += e.problems
        ver = []
    for r in ver:
        cd = _events_clean(r.get("check_date"))
        m = EVENTS_MONTH_RX.match(cd)
        if cd and not m:
            problems.append(f"verification.jsonl line {r['_row']}: check_date '{cd}' must start YYYY-MM-DD (or be null)")
            continue
        data = {"lr_id": str(r["lr_id"])}
        for k in ("level", "evidence", "assessed_by_role"):
            if _events_clean(r.get(k)):
                data[k] = _events_clean(r[k])
        if len(data) == 1:
            continue                       # a blank template row: no reading was made, so nothing is recorded
        add("verification", str(r["lr_id"]), m.group(1) if m else month, data, undated=not m)
    try:
        ado = load_adoption(run)
    except OrgFileError as e:
        problems += e.problems
        ado = []
    for r in ado:
        if not r.get("response"):
            continue                       # no response yet: nothing to record
        data = {"lr_id": str(r["lr_id"]), "adoption": r["response"]}
        for k in ("reason", "owning_role", "target_window"):
            if _events_clean(r.get(k)):
                data[k] = _events_clean(r[k])
        add("status", str(r["lr_id"]), month, data)
    if problems:
        raise OrgFileError(problems, out)
    # Rows that name the same reading (event_key) are one reading: the later row wins, so a file with two rows for
    # one slot never alternates between them on re-publish.
    last = {}
    for i, ev in enumerate(out):
        last[event_key(ev)] = i
    return [ev for i, ev in enumerate(out) if last[event_key(ev)] == i]


def event_key(ev: dict) -> tuple:
    """What identifies 'the same reading' for de-duplication: a later publish appends only when the latest event with
    this key differs (so a site that changes its answer back and forth keeps each change)."""
    data = ev.get("data") if isinstance(ev.get("data"), dict) else {}
    t = ev.get("type")
    if t == "site_assessment":
        return (t, ev.get("ll_id"), data.get("site"))
    if t == "verification":
        return (t, ev.get("ll_id"), ev.get("month"), data.get("level"))
    return (t, ev.get("ll_id"), "adoption")
