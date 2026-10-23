"""The risk_change items of a pack as a CSV for a risk register (Task 8, D7): <pack>.risk-changes.csv, one row per
item. The last column, risk_owner_decision, is always blank: the risk owner decides, never the coach. The file is an
import file, so it carries no status line (Ruling P4-20)."""
from __future__ import annotations

import csv
import io

from . import NOTHING_TO_WRITE, Output, output_name, register

RISK_COLUMNS = ("id", "risk", "change_type", "current_assumption", "evidence_says", "proposed_change", "cites",
                "risk_owner_decision")
_RC_FORMULA_LEAD = ("=", "+", "-", "@", "\t", "\r")


def _rc_cell(v) -> str:
    """A cell as text; one that starts with = + - @ tab or CR gets a leading quote, so a spreadsheet never runs it."""
    s = ";".join(str(x) for x in v) if isinstance(v, list) else ("" if v is None else str(v))
    return "'" + s if s.startswith(_RC_FORMULA_LEAD) else s


def render_risk_csv(ctx) -> list:
    items = [it for s in ctx.pack["sections"] for it in s["items"] if it.get("kind") == "risk_change"]
    if not items:
        ctx.notes.append(NOTHING_TO_WRITE.format(fmt="risk-csv", why="the pack has no risk_change item"))
        return []
    buf = io.StringIO()
    wr = csv.writer(buf, lineterminator="\r\n")
    wr.writerow(RISK_COLUMNS)
    for it in items:
        wr.writerow([_rc_cell(it.get(c)) if c != "risk_owner_decision" else "" for c in RISK_COLUMNS])
    text = buf.getvalue()
    return [Output(output_name(ctx.pack["pack"], "risk-changes.csv"), text, text)]


register("risk-csv", render_risk_csv, kind="data", help="<pack>.risk-changes.csv: one row per risk_change item, with "
         "the risk owner's decision column left blank")
