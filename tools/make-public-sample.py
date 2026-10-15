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
  python3 tools/make-public-sample.py export.xlsx --slug 2020-09-24-hazira-gas-release-fire \
      --names ~/private/names-to-remove.txt --set "Date=2020-09-24" --set "Incident Type=fire"
  # writes samples/2020-09-24-hazira-gas-release-fire/2020-09-24-hazira-gas-release-fire_probematrix-findings.xlsx

Only publish exports of incidents that are public record, de-identified to roles, and that you have the
right to publish.
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
    p.add_argument("--names", required=True, help="file with names/identifiers that must not appear")
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
    dst.parent.mkdir(parents=True, exist_ok=True)
    wb.save(dst)
    print(f"Zero-hit scan passed ({len(names)} names). Kept sheets: {wb.sheetnames}. Wrote {dst}")


if __name__ == "__main__":
    main()
