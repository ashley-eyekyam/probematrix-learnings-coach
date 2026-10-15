#!/usr/bin/env python3
"""Prepare a ProbeMatrix findings export for publication as a public sample.

What it does
  1. Keeps only the sheets the Learnings Coach reads (Incident Summary, Identified Findings,
     Evidence Links, Causal Chain, Analysis Statistics). Reference, collaboration and personnel
     sheets are dropped.
  2. Optionally overrides Incident Summary fields (e.g. a wrong date or type): --set "Date=2024-03-20".
  3. Runs a deterministic name scan against a names file you keep OUTSIDE the repo
     (one name or identifier per line). Exits non-zero, and writes nothing, unless the scan is zero-hit.

Usage
  python3 tools/make-public-sample.py export.xlsx samples/<slug>/<slug>_probematrix-findings.xlsx \
      --names ~/private/names-to-remove.txt --set "Date=2024-03-20" --set "Incident Type=fire"

Only publish exports of incidents that are public record, de-identified to roles, and that you have the
right to publish.
"""
import argparse
import re
import sys

KEEP = ["Incident Summary", "Identified Findings", "Evidence Links", "Causal Chain", "Analysis Statistics"]


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("src")
    p.add_argument("dst")
    p.add_argument("--names", required=True, help="file with names/identifiers that must not appear")
    p.add_argument("--set", action="append", default=[], help='Incident Summary override "Field=Value"')
    a = p.parse_args()
    try:
        import openpyxl
    except ImportError:
        sys.exit("pip install openpyxl")
    wb = openpyxl.load_workbook(a.src)
    for name in list(wb.sheetnames):
        if name not in KEEP:
            del wb[name]
    overrides = dict(s.split("=", 1) for s in a.set)
    if overrides and "Incident Summary" in wb.sheetnames:
        for row in wb["Incident Summary"].iter_rows():
            if row and row[0].value in overrides and len(row) > 1:
                row[1].value = overrides[row[0].value]
    names = [n.strip() for n in open(a.names, encoding="utf-8") if n.strip() and not n.startswith("#")]
    rx = re.compile(r"\b(" + "|".join(re.escape(n) for n in names) + r")\b", re.I) if names else None
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
    wb.save(a.dst)
    print(f"Zero-hit scan passed ({len(names)} names). Kept sheets: {wb.sheetnames}. Wrote {a.dst}")


if __name__ == "__main__":
    main()
