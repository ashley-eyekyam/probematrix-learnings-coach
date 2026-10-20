"""The export schema: expected columns, the schema report and the Analysis Statistics check."""
from __future__ import annotations

import hashlib

from ..util import _int, _s


def find_sheet(wb, *candidates):
    for c in candidates:
        for n in wb.sheetnames:
            if n.strip().lower() == c.lower():
                return wb[n]
    for c in candidates:
        for n in wb.sheetnames:
            if c.lower() in n.lower():
                return wb[n]
    return None


def rows_as_dicts(ws):
    rows = list(ws.iter_rows(values_only=True))
    if not rows:
        return []
    header = [_s(h) for h in rows[0]]
    return [dict(zip(header, r)) for r in rows[1:] if any(c is not None for c in r)]


# ----------------------------------------------------------------------------- export schema

KNOWN_COLUMNS = {
    "Identified Findings": ["Finding ID", "Nanocode", "Name", "Level", "Level Name", "Category", "Subcategory",
                            "Classification", "Rating", "Instance ID", "Instance Label", "Short Description",
                            "AI Justification", "Causal Explanation", "Individuals Involved", "Linked Evidence",
                            "Evidence to Collect", "Key Questions", "Suggested Interviews", "Causal Hypothesis",
                            "User Edited", "Created At", "Updated At"],
    "Evidence Links": ["Finding Code", "Finding Name", "Evidence ID", "Evidence Type", "Relevance",
                       "Specific Reference", "Evidence Description"],
    "Causal Chain": ["Link ID", "From Code", "From Level", "To Code", "To Level", "Relationship", "Confidence",
                     "Basis", "Evidence Support", "User Confirmed", "Notes"],
}
KNOWN_SUMMARY_FIELDS = [
    "Incident Number", "Incident Title", "Incident Type", "Date", "Time", "Location", "Severity", "Outcome",
    "Investigation Status", "Investigating Officer", "Consequence Type", "Persons Affected", "Fatalities",
    "Injuries", "Risk Rating", "Potential Severity", "Likelihood of Recurrence", "Reportable to Regulator",
    "Regulatory Bodies", "Regulatory Reference", "Department", "Area/Zone", "Shift", "Weather Conditions",
    "Lighting Conditions", "Supervisor at Time", "Investigation Team", "Due Date", "Completed Date",
    "Verification Required",
]
REQUIRED_COLUMNS = ["Finding ID", "Level", "Rating", "Individuals Involved", "Linked Evidence"]
CAPA_PLANNER_SHEETS = ("Chapter Headers", "Corrective Actions", "Preventive Actions", "Residual Risks")


def _header(ws) -> list[str]:
    if ws is None:
        return []
    for row in ws.iter_rows(values_only=True):
        return [h for h in (_s(c) for c in row) if h]
    return []


def _known_sheet(wb, name):
    """The sheet for a KNOWN_COLUMNS key, accepting the alias ingest accepts for the findings sheet."""
    return find_sheet(wb, name, "Findings") if name == "Identified Findings" else find_sheet(wb, name)


def schema_report(wb) -> dict:
    """Fingerprint plus missing and unknown columns for the three columnar sheets."""
    headers = {n: _header(_known_sheet(wb, n)) for n in KNOWN_COLUMNS}
    canon = "\n".join(list(wb.sheetnames) + ["\t".join(headers[n]) for n in KNOWN_COLUMNS])
    missing, unknown = {}, {}
    for n, known in KNOWN_COLUMNS.items():
        if _known_sheet(wb, n) is None:
            continue
        m = [c for c in known if c not in headers[n]]
        u = [c for c in headers[n] if c not in known]
        if m:
            missing[n] = m
        if u:
            unknown[n] = u
    return {"fingerprint": hashlib.sha256(canon.encode("utf-8")).hexdigest()[:12],
            "missing": missing, "unknown": unknown}


def analysis_stats(ws):
    """Read the `Level | Level Name | Total Findings` block and its Total row, or None."""
    if ws is None:
        return None
    by_level, total, in_block = {}, None, False
    for row in ws.iter_rows(values_only=True):
        cells = list(row) + [None] * 3
        if not in_block:
            in_block = (_s(cells[0]) == "Level" and _s(cells[1]) == "Level Name"
                        and _s(cells[2]) == "Total Findings")
            continue
        first = cells[0]
        if _s(first).lower() == "total":
            total = _int(cells[2])
            break
        lvl, n = _int(first), _int(cells[2])
        if lvl is not None and n is not None:
            by_level[lvl] = n
    if total is None:
        return None
    return {"total": total, "by_level": by_level}


def _fmt_cols(d: dict) -> str:
    return "; ".join(f"{s}: {', '.join(c)}" for s, c in d.items()) or "none"
