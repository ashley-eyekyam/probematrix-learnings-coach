#!/usr/bin/env python3
"""Write the UAT input files into docs/uat/inputs/ (fictional event, no real data).

Run from the repository root:  python3 tools/make-uat-inputs.py [--out DIR]   (default: docs/uat/inputs)

It writes three synthetic ProbeMatrix findings exports, each testing one ingest or check path:
  uat-votes.xlsx           Collaboration Data VOTES with a reviewer downgrade on FND-0004
  uat-renamed-header.xlsx  the Identified Findings column "Rating" renamed to "Score"
  uat-capa-planner.xlsx    Corrective Actions and Preventive Actions sheets (a CAPA Planner export)
and two small learning packs to check against the uat-votes workspace:
  uat-votes-pack.json      cites the downgraded FND-0004 without a data_quality note (check-pack fails)
  uat-unlinked-pack.json   cites EVD-0003 next to FND-0002, which does not link it (check-pack warns)

The export shape follows tests/test_pmlc.py (FIND_COLS, ROWS, make_export), duplicated here so this tool
needs only the standard library and openpyxl. The workbooks are rebuilt from scratch on every run.
"""
import argparse
import json
import sys
from pathlib import Path

try:
    import openpyxl
except ImportError:
    sys.exit("openpyxl is required: pip install openpyxl")

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "docs" / "uat" / "inputs"
STATUS = "Learning purposes: not a statutory document"

FIND_COLS = ["Finding ID", "Nanocode", "Name", "Level", "Level Name", "Category", "Subcategory", "Classification",
             "Rating", "Instance ID", "Instance Label", "Short Description", "AI Justification", "Causal Explanation",
             "Individuals Involved", "Linked Evidence", "Evidence to Collect", "Key Questions", "Suggested Interviews",
             "Causal Hypothesis", "User Edited", "Created At", "Updated At"]

ROWS = [
    ["FND-0001", "AB 1.1", "Step Omitted", 1, "Unsafe Acts", "Unsafe Acts", "Errors", "substantiated", 3, 1,
     "Pump restarted without leak test", "Pump restarted without leak test after seal change on 12/03/2024.",
     "Work order shows no test [EVD-0001].", "Enabled by SV 1.4 and OR 2.2.",
     "Pump Technician (seal change crew), Maintenance Supervisor (return-to-service approval)", "EVD-0001",
     None, None, None, None, "No", None, None],
    ["FND-0002", "SV 1.4", "No Guidance Provided", 3, "Supervision", "Supervision", "Supervision Inadequate",
     "substantiated", 4, 1, "No return-to-service checklist", "No checklist for return to service.",
     "Procedure index has no entry [EVD-0002].", "Led to AB 1.1.",
     "Maintenance Supervisor, Maintenance Manager (procedure owner)", "EVD-0002", None, None, None, None, "No",
     None, None],
    ["FND-0003", "OR 2.2", "Spares Programme Failure", 4, "Organisational Influences", "Organisational Influences",
     "Resource Management", "substantiated", 4, 1, "Seals bought locally without specification",
     "Local seals without specification since March 2022.", "Purchase records [EVD-0003].",
     "This condition enabled SV 1.4 and AB 1.1.",
     "Stores/Procurement Officer, Plant Manager (budget owner), Reliability Engineer (absent)", "EVD-0003, EVD-0001",
     None, None, None, None, "No", None, None],
    ["FND-0004", "PE 2.1", "Alarm Not Configured", 2, "Preconditions", "Preconditions", "Technological Environment",
     "substantiated", 2, 1, "Gas alarm display-only", "Gas detector alarm had no shutdown.", "DCS list [EVD-0002].",
     "Delayed response; see OR 2.2.", "Control Room Operators, Emergency Response planners", "EVD-0002",
     None, None, None, None, "No", None, None],
]


def base_workbook():
    wb = openpyxl.Workbook()
    s = wb.active
    s.title = "Incident Summary"
    for r in [("INCIDENT SUMMARY", None), (None, None), ("Field", "Value"), ("Incident Title", "Synthetic pump fire"),
              ("Date", "2024-03-20"), ("Investigation Status", "completed")]:
        s.append(r)
    f = wb.create_sheet("Identified Findings")
    f.append(FIND_COLS)
    for r in ROWS:
        f.append(r)
    e = wb.create_sheet("Evidence Links")
    e.append(["Finding Code", "Finding Name", "Evidence ID", "Evidence Type", "Relevance", "Specific Reference",
              "Evidence Description"])
    e.append(["AB 1.1", "Step Omitted", "EVD-0001", "document", "Shows no test", "no leak test recorded", "Work order"])
    e.append(["SV 1.4", "No Guidance Provided", "EVD-0002", "document", "No checklist", "index has no entry", "Index"])
    e.append(["OR 2.2", "Spares Programme Failure", "EVD-0003", "log_record", "Local buys", "bought locally", "PO list"])
    c = wb.create_sheet("Causal Chain")
    c.append(["Link ID", "From Code", "From Level", "To Code", "To Level", "Relationship", "Confidence", "Basis",
              "Evidence Support", "User Confirmed", "Notes"])
    c.append(["No causal links found"] + [None] * 10)
    return wb


def votes(wb):
    c = wb.create_sheet("Collaboration Data")
    for r in [("VOTES",), ("Finding ID", "Vote", "Reason"), ("FND-0004", "downgrade", "weak evidence")]:
        c.append(r)


def renamed_header(wb):
    for c in wb["Identified Findings"][1]:
        if c.value == "Rating":
            c.value = "Score"


def capa_planner(wb):
    wb.create_sheet("Corrective Actions")
    wb.create_sheet("Preventive Actions")


WORKBOOKS = {"uat-votes.xlsx": votes, "uat-renamed-header.xlsx": renamed_header, "uat-capa-planner.xlsx": capa_planner}


def pack(name, title, items, **top):
    p = {"pack": name, "schema": 1, "title": title, "audience": "UAT testers", "status": STATUS,
         "bottom_line": [{"text": "No check stopped an untested pump returning to service.", "cites": ["FND-0002"]}],
         "sections": [{"id": "learnings", "heading": "Learnings", "items": items}]}
    p.update(top)
    return p


PACKS = {
    "uat-votes-pack.json": pack("uat-votes-pack", "UAT votes pack: synthetic pump fire", [
        {"kind": "learning", "lesson": "A gas alarm that only displays does not stop the release.",
         "cites": ["FND-0004"]}]),
    "uat-unlinked-pack.json": pack("uat-unlinked-pack", "UAT unlinked evidence pack: synthetic pump fire", [
        {"kind": "learning", "lesson": "Return to service needs a checklist with a hold point.",
         "cites": ["FND-0002", "EVD-0003"]}]),
}


def main():
    ap = argparse.ArgumentParser(description="Write the UAT input files.")
    ap.add_argument("--out", type=Path, default=OUT, help="output folder (default: docs/uat/inputs)")
    out = ap.parse_args().out
    out.mkdir(parents=True, exist_ok=True)
    for name, edit in WORKBOOKS.items():
        wb = base_workbook()
        edit(wb)
        wb.save(out / name)
        print(f"wrote {out / name}")
    for name, p in PACKS.items():
        (out / name).write_text(json.dumps(p, indent=1) + "\n", encoding="utf-8")
        print(f"wrote {out / name}")


if __name__ == "__main__":
    main()
