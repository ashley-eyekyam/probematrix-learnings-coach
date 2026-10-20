#!/usr/bin/env python3
"""Prepare a ProbeMatrix findings export for publication as a public sample.

What it does
  1. Keeps only the sheets the Learnings Coach reads (Incident Summary, Identified Findings,
     Evidence Links, Causal Chain, Analysis Statistics). Reference, collaboration and personnel
     sheets are dropped.
  2. Optionally overrides Incident Summary fields (e.g. a wrong date or type): --set "Date=2024-03-20".
  3. Strips metadata: resets the core and app properties (creator, lastModifiedBy, title, company), removes
     comments, hyperlinks, headers and footers, unhides hidden rows, columns and sheets (so the scan sees them) and drops
     defined names. Blanks Investigating Officer, Supervisor at Time and Investigation Team (keep one with
     --keep-field NAME, repeatable) and drops narrative lines that start with To:, From: or Cc:.
  4. Optionally runs a deterministic name scan (--names) against a names file you keep OUTSIDE the repo
     (one name or identifier per line); with --names it exits non-zero, and writes nothing, on any hit.
     Without --names the scan is skipped: committed samples may include ProbeMatrix material unmodified.
     Use --names for an organisation's own runs.

Usage
  python3 tools/make-public-sample.py export.xlsx --slug 2020-09-24-hazira-gas-release-fire \
      --set "Date=2020-09-24" --set "Incident Type=fire"
  # writes samples/2020-09-24-hazira-gas-release-fire/2020-09-24-hazira-gas-release-fire_probematrix-findings.xlsx

Only publish exports of incidents that are public record and that you have the right to publish.
"""
import argparse
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "skills" / "learnings-coach" / "scripts"))
from pmlc_lib import privacy  # noqa: E402
from pmlc_lib.workspace import valid_run_slug  # noqa: E402

MEMO_RX = re.compile(r"^\s*(?:To|From|Cc)\s*:", re.I)
PERSONAL_FIELDS = ("Investigating Officer", "Supervisor at Time", "Investigation Team")
KEEP = ["Incident Summary", "Identified Findings", "Evidence Links", "Causal Chain", "Analysis Statistics"]


def strip_metadata(wb, keep_fields=()) -> None:
    """Remove what a workbook carries besides cell text: properties, comments, hyperlinks, headers and footers, hidden state,
    defined names; blank the personal fields and drop memo header lines from the Incident Summary."""
    from openpyxl.packaging.core import DocumentProperties
    wb.properties = DocumentProperties(creator="", lastModifiedBy=None, title=None, subject=None, description=None,
                                       keywords=None, category=None, contentStatus=None, identifier=None,
                                       language=None, revision=None, version=None)
    if hasattr(wb, "custom_doc_props"):
        wb.custom_doc_props.props.clear()
    for n in list(wb.defined_names):
        del wb.defined_names[n]
    keep = {k.strip().lower() for k in keep_fields}
    fields = {f.lower() for f in PERSONAL_FIELDS}
    for k in sorted(keep - fields):
        print(f"warning: --keep-field {k!r} matches none of {', '.join(PERSONAL_FIELDS)}", file=sys.stderr)
    for ws in wb.worksheets:
        ws.sheet_state = "visible"
        for d in ws.row_dimensions.values():
            d.hidden = False
        for d in ws.column_dimensions.values():
            d.hidden = False
        for n in list(ws.defined_names):
            del ws.defined_names[n]
        for hf in (ws.oddHeader, ws.oddFooter, ws.evenHeader, ws.evenFooter, ws.firstHeader, ws.firstFooter):
            hf.left.text = hf.center.text = hf.right.text = None
        for row in ws.iter_rows():
            for c in row:
                if c.comment is not None:
                    c.comment = None
                if c.hyperlink is not None:
                    c.hyperlink = None
        if ws.title == "Incident Summary":
            for row in ws.iter_rows():
                if len(row) > 1 and str(row[0].value or "").strip().lower() in fields and \
                        str(row[0].value).strip().lower() not in keep:
                    row[1].value = None
                for c in row:
                    if isinstance(c.value, str) and re.search(r"(?im)^\s*(?:To|From|Cc)\s*:", c.value):
                        c.value = "\n".join(ln for ln in c.value.split("\n") if not MEMO_RX.match(ln)) or None


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("src")
    p.add_argument("dst", nargs="?", help="output .xlsx (omit when --slug is given)")
    p.add_argument("--slug", help="run slug YYYY-MM-DD-<site>-<event>; writes <samples-root>/<slug>/<slug>_probematrix-findings.xlsx")
    p.add_argument("--samples-root", default=str(REPO / "samples"), help="default: the repo's samples/ folder")
    p.add_argument("--names", help="optional file with names/identifiers that must not appear (scan skipped without it)")
    p.add_argument("--keep-field", action="append", default=[], metavar="NAME",
                   help="keep this personal Incident Summary field instead of blanking it (repeatable)")
    p.add_argument("--set", action="append", default=[], help='Incident Summary override "Field=Value"')
    a = p.parse_args()
    if a.slug:
        if not valid_run_slug(a.slug):
            sys.exit(f"--slug must look like 2020-09-24-hazira-gas-release-fire (got {a.slug!r})")
        dst = Path(a.samples_root) / a.slug / f"{a.slug}_probematrix-findings.xlsx"
    elif a.dst:
        dst = Path(a.dst)
    else:
        sys.exit("Give --slug <YYYY-MM-DD-site-event> (recommended) or an output path.")
    try:
        import openpyxl
    except ImportError:
        sys.exit("pip install openpyxl")
    wb = openpyxl.load_workbook(a.src)
    for name in list(wb.sheetnames):
        if name not in KEEP:
            del wb[name]
    strip_metadata(wb, a.keep_field)
    overrides = dict(s.split("=", 1) for s in a.set)
    if overrides and "Incident Summary" in wb.sheetnames:
        for row in wb["Incident Summary"].iter_rows():
            if row and row[0].value in overrides and len(row) > 1:
                row[1].value = overrides[row[0].value]
    names = []
    if a.names:
        names = privacy.load_names(a.names)
    else:
        print("No names file given: name scan skipped (samples may include ProbeMatrix material unmodified, per the sample rules).")
    rx = privacy.name_pattern(names)
    hits = 0
    if rx:
        for ws in wb.worksheets:
            for row in ws.iter_rows():
                for c in row:
                    if isinstance(c.value, str):
                        for m in rx.finditer(c.value):
                            hits += 1
                            print(f"HIT {ws.title}!{c.coordinate}: {m.group(0)!r} … {c.value[max(0, m.start()-40):m.end()+40]!r}")
    if hits:
        sys.exit(f"{hits} hit(s). Nothing written. Edit the source export and re-run.")
    scan_note = (f"Name scan passed (optional for public-record samples, D3): {len(names)} name(s) checked. "
                 if a.names else "")
    dst.parent.mkdir(parents=True, exist_ok=True)
    wb.save(dst)
    print(f"{scan_note}Kept sheets: {wb.sheetnames}. Wrote {dst}")


if __name__ == "__main__":
    main()
