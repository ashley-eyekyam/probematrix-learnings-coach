#!/usr/bin/env python3
"""Prepare a ProbeMatrix findings export for publication as a public sample.

What it does
  1. Keeps only the sheets the Learnings Coach reads (Incident Summary, Identified Findings,
     Evidence Links, Causal Chain, Analysis Statistics). Reference, collaboration and personnel
     sheets are dropped.
  2. Optionally overrides Incident Summary fields (e.g. a wrong date or type): --set "Date=2024-03-20".
  3. Optionally runs a deterministic name scan (--names) against a names file you keep OUTSIDE the repo
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
from pmlc import valid_run_slug  # noqa: E402

KEEP = ["Incident Summary", "Identified Findings", "Evidence Links", "Causal Chain", "Analysis Statistics"]


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("src")
    p.add_argument("dst", nargs="?", help="output .xlsx (omit when --slug is given)")
    p.add_argument("--slug", help="run slug YYYY-MM-DD-<site>-<event>; writes <samples-root>/<slug>/<slug>_probematrix-findings.xlsx")
    p.add_argument("--samples-root", default=str(REPO / "samples"), help="default: the repo's samples/ folder")
    p.add_argument("--names", help="optional file with names/identifiers that must not appear (scan skipped without it)")
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
    overrides = dict(s.split("=", 1) for s in a.set)
    if overrides and "Incident Summary" in wb.sheetnames:
        for row in wb["Incident Summary"].iter_rows():
            if row and row[0].value in overrides and len(row) > 1:
                row[1].value = overrides[row[0].value]
    names = []
    if a.names:
        names = [n.strip() for n in open(a.names, encoding="utf-8") if n.strip() and not n.startswith("#")]
    else:
        print("No names file given: name scan skipped (samples may include ProbeMatrix material unmodified, per the sample rules).")
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
    scan_note = f"Name scan passed ({len(names)} names). " if a.names else ""
    dst.parent.mkdir(parents=True, exist_ok=True)
    wb.save(dst)
    print(f"{scan_note}Kept sheets: {wb.sheetnames}. Wrote {dst}")


if __name__ == "__main__":
    main()
