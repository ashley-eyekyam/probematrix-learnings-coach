"""The pack-xlsx command: the test points or questions of a pack as one Excel sheet."""
from __future__ import annotations

import sys
from pathlib import Path

from .. import DRAFT_LABEL, STATUS_PHRASE, VERSION_STAMP
from ..handling import effective_handling, is_draft
from ..register.xlsx import text_cells
from ..util import _abs, _flat, _need_openpyxl
from ..workspace import outputs_dir
from .schema import _checked, KINDS

XLSX_KINDS = {"test_point": ("Test points", "test-points"), "question": ("Questions", "questions")}


def cmd_pack_xlsx(a):
    openpyxl = _need_openpyxl()
    from openpyxl.styles import Alignment, Font, PatternFill
    from openpyxl.utils import get_column_letter
    w, pack, _ = _checked(a)
    items = [(s["heading"], it) for s in pack["sections"] for it in s["items"] if it.get("kind") == a.kind]
    if not items:
        sys.exit(f"{a.pack} has no {a.kind} items")
    title, slug = XLSX_KINDS[a.kind]
    fields = KINDS[a.kind]["req"] + [f for f in KINDS[a.kind]["opt"] if any(f in it for _, it in items)]
    wb = openpyxl.Workbook()
    sh = wb.active
    sh.title = title
    sh.append(["section"] + fields + ["cites"])
    for heading, it in items:
        sh.append([heading] + [_flat(it.get(f)) for f in fields] + [", ".join(it.get("cites") or [])])
    fill, font = PatternFill("solid", fgColor="0B3954"), Font(color="FFFFFF", bold=True)
    for i, c in enumerate(sh[1], 1):
        c.fill, c.font = fill, font
        sh.column_dimensions[get_column_letter(i)].width = 34
    for row in sh.iter_rows(min_row=2):
        for c in row:
            c.alignment = Alignment(wrap_text=True, vertical="top")
    sh.freeze_panes = "A2"
    eh = effective_handling(pack, w, src=a.pack, ws=a.ws)
    sh.oddHeader.center.text = STATUS_PHRASE + (f" · {DRAFT_LABEL}" if is_draft(eh) else "")
    sh.oddFooter.center.text = VERSION_STAMP
    out = Path(a.out) if a.out else outputs_dir(_abs(a.ws)) / f"{pack['pack']}-{slug}.xlsx"
    out.parent.mkdir(parents=True, exist_ok=True)
    text_cells(wb)
    wb.save(out)
    print(f"{len(items)} {a.kind} item{'s' if len(items) != 1 else ''} written to {out}")
