"""The data exports (L4-10, L4-25): `--format csv` writes <pack>.actions.csv (the same rows and columns as
export-actions, owner and due blank), and follow_up_csv builds the follow-up.csv that an internal investigator-coach
pack writes beside follow-up.json. Neither carries the status line: import files must stay clean (P4-20)."""
from __future__ import annotations

import csv
import io
import sys
from pathlib import Path

from .. import actions
from ..pack.schema import FOLLOW_UP_KEYS
from . import NOTHING_TO_WRITE, Output, output_name, register

FOLLOW_UP_HEADER = ["Finding ID", "Evidence to Collect", "Key Questions", "Suggested Interviews", "Causal Hypothesis"]
EXISTS = "{file} already exists and may hold your organisation's entries; move it or pass a new --out"
KEEP_FORMATS = ("csv",)          # formats whose files the organisation fills in: never replaced (P3-9)


def _ex_csv_text(header, rows) -> str:
    buf = io.StringIO(newline="")
    w = csv.writer(buf, lineterminator="\r\n")
    w.writerow(header)
    for r in rows:
        w.writerow(r)
    return buf.getvalue()


def render_actions_csv(ctx) -> list:
    """<pack>.actions.csv: every recommendation, decision and indicator item, in export-actions' generic columns."""
    rows = actions.collect_actions(ctx.run, [ctx.pack], [])
    if not rows:
        ctx.notes.append(NOTHING_TO_WRITE.format(fmt="csv", why="the pack has no recommendation, decision or "
                                                                 "indicator items"))
        return []
    text = _ex_csv_text(actions.ACTION_COLUMNS, ([actions._csv_cell(r[c]) for c in actions.ACTION_COLUMNS]
                                                  for r in rows))
    return [Output(output_name(ctx.pack["pack"], "actions.csv"), text, text)]


def refuse_existing(path) -> None:
    """Exit 1 when `path` exists and the organisation may have filled it in (P3-9 pattern)."""
    if Path(path).exists():
        sys.exit(EXISTS.format(file=path))


def follow_up_csv(pack) -> str:
    """The investigator-coach follow-up table as CSV, with the export's own column names. Cells that start with
    = + - @ tab or CR get a leading single quote, as in the actions CSV."""
    from ..pack.html import follow_up
    fu = follow_up(pack)
    return _ex_csv_text(FOLLOW_UP_HEADER, ([fid] + [actions._csv_cell(fields.get(k, "")) for k in FOLLOW_UP_KEYS]
                                           for fid, fields in fu.items()))


register("csv", render_actions_csv, kind="data", help="<pack>.actions.csv: the actions for an action-tracking system")
