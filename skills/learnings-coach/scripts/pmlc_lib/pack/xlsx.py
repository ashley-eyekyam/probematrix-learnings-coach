"""The pack-xlsx command: the test points or questions of a pack as one Excel sheet."""
from __future__ import annotations

import sys
from pathlib import Path

from .. import BRAND, DRAFT_LABEL, STATUS_PHRASE
from ..handling import (
    effective_handling, is_draft, name_guard, refuse_internal_overwrite, share_ctx, share_gate, shared_copy, shared_name,
    SHARED_LINE,
)
from ..register.xlsx import reset_docprops, SHARED_EPOCH, text_cells
from ..util import _abs, _flat, _need_openpyxl
from ..workspace import outputs_dir
from .schema import _checked, KINDS, record_check

XLSX_KINDS = {"test_point": ("Test points", "test-points"), "question": ("Questions", "questions")}


def cmd_pack_xlsx(a):
    openpyxl = _need_openpyxl()
    from openpyxl.styles import Alignment, Font, PatternFill
    from openpyxl.packaging.core import DocumentProperties
    from openpyxl.utils import get_column_letter
    w, pack, res = _checked(a, record_ok=False)
    mode = share_gate(pack, w, a, embeds=False, src=a.pack, ws=a.ws)   # same gate as pack and register-xlsx
    record_check(a, pack, res, w)                                      # only now: a refused share records nothing
    eh = effective_handling(pack, w, src=a.pack, ws=a.ws)   # before masking: the sign-off hash is of the real pack
    share = share_ctx(a, w, mode) if mode != "internal" else None
    if share:
        pack = shared_copy(pack, share, w)
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
    name_guard([str(c.value) for row in sh.iter_rows() for c in row if c.value is not None], a)   # any mode
    sh.oddHeader.center.text = (STATUS_PHRASE + (f" · {DRAFT_LABEL}" if is_draft(eh) else "")
                                + (f" · {SHARED_LINE.format(mode=mode)}" if share else ""))
    sh.oddFooter.center.text = BRAND                  # BRAND holds the version stamp (P4-20)
    internal = outputs_dir(_abs(a.ws)) / f"{pack['pack']}-{slug}.xlsx"
    out = Path(a.out) if a.out else shared_name(internal, mode)
    refuse_internal_overwrite(out, internal, mode)
    out.parent.mkdir(parents=True, exist_ok=True)
    if share:
        wb.properties = DocumentProperties(creator="", lastModifiedBy=None, created=SHARED_EPOCH, modified=SHARED_EPOCH)
    text_cells(wb)
    wb.save(out)
    if share:
        reset_docprops(out)
        print(SHARED_LINE.format(mode=mode))
    print(f"{len(items)} {a.kind} item{'s' if len(items) != 1 else ''} written to {out}")
