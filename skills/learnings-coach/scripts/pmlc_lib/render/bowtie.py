"""The barrier items of a pack as a generic bow-tie CSV (L4-22, Ruling P4-21): <pack>.bowtie.csv, one row per barrier,
for a bow-tie tool or a spreadsheet. Prevention barriers sit on the threat side and mitigation or recovery barriers on
the consequence side. The file is an import file, so it carries no status line (Ruling P4-20)."""
from __future__ import annotations

import csv
import io

from . import NOTHING_TO_WRITE, Output, output_name, register

BOWTIE_COLUMNS = ("side", "barrier", "barrier_id", "state", "type", "hoc_tier", "failure_mode", "fix", "owner_role",
                  "indicator", "cites")
_BT_FORMULA_LEAD = ("=", "+", "-", "@", "\t", "\r")


def _bt_side(group) -> str:
    """threat for a group that starts with "prevent", consequence for "mitigat" or "recover", else blank."""
    g = str(group or "").strip().casefold()
    if g.startswith("prevent"):
        return "threat"
    return "consequence" if g.startswith(("mitigat", "recover")) else ""


def _bt_cell(v) -> str:
    """A cell as text; one that starts with = + - @ tab or CR gets a leading quote, so a spreadsheet never runs it."""
    s = ";".join(str(x) for x in v) if isinstance(v, list) else ("" if v is None else str(v))
    return "'" + s if s.startswith(_BT_FORMULA_LEAD) else s


def render_bowtie_csv(ctx) -> list:
    barriers = [it for s in ctx.pack["sections"] for it in s["items"] if it.get("kind") == "barrier"]
    if not barriers:
        ctx.notes.append(NOTHING_TO_WRITE.format(fmt="bowtie-csv", why="the pack has no barrier item"))
        return []
    buf = io.StringIO()
    wr = csv.writer(buf, lineterminator="\r\n")
    wr.writerow(BOWTIE_COLUMNS)
    for b in barriers:
        row = dict(b, side=_bt_side(b.get("group")), owner_role=b.get("owner"))
        wr.writerow([_bt_cell(row.get(c)) for c in BOWTIE_COLUMNS])
    text = buf.getvalue()
    return [Output(output_name(ctx.pack["pack"], "bowtie.csv"), text, text)]


register("bowtie-csv", render_bowtie_csv, kind="data", help="<pack>.bowtie.csv: one row per barrier, threat or "
         "consequence side, for a bow-tie tool")
