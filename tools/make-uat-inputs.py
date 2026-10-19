#!/usr/bin/env python3
"""Write the UAT input files into docs/uat/inputs/ (fictional event, no real data).

Run from the repository root:  python3 tools/make-uat-inputs.py [--out DIR]   (default: docs/uat/inputs)

It writes four synthetic ProbeMatrix findings exports, each testing one ingest, check or sign-off path:
  uat-votes.xlsx           Collaboration Data VOTES with a reviewer downgrade on FND-0004
  uat-renamed-header.xlsx  the Identified Findings column "Rating" renamed to "Score"
  uat-capa-planner.xlsx    Corrective Actions and Preventive Actions sheets (a CAPA Planner export)
  uat-approvable.xlsx      Phase 2: completed, FND-0001 edited by a person (so sign-off is allowed), with fictional
                           names, an organisation, a tag, a clock time, a full date, a numbered role, an email and a
                           staff number for the privacy and sharing tests
two small learning packs to check against the uat-votes workspace:
  uat-votes-pack.json      cites the downgraded FND-0004 without a data_quality note (check-pack fails)
  uat-unlinked-pack.json   cites EVD-0003 next to FND-0002, which does not link it (check-pack warns)
and, for Phase 2, against the uat-approvable workspace:
  uat-bad-pack.json        the L3-01 test pack (tests/fixtures/packs/bad-l3-01.json): fails the language check
  uat-shareable-pack.json  a clean pack that can be signed off and shared
  uat-register.json        a clean two-learning register that can be signed off and shared
  uat-names.txt, uat-orgs.txt, uat-redact.json  names, organisations and a redaction map (all fictional)

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
sys.path.insert(0, str(ROOT / "skills" / "learnings-coach" / "scripts"))
from pmlc import STATUS_PHRASE as STATUS  # noqa: E402

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


def base_workbook(summary=(), narrative=None):
    wb = openpyxl.Workbook()
    s = wb.active
    s.title = "Incident Summary"
    for r in [("INCIDENT SUMMARY", None), (None, None), ("Field", "Value"), ("Incident Title", "Synthetic pump fire"),
              ("Date", "2024-03-20"), ("Investigation Status", "completed"), *summary]:
        s.append(r)
    if narrative:
        s.append(("INCIDENT NARRATIVE", None))
        s.append((narrative, None))
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


# Fictional people (no real person, and no one connected with the Hazira incident). The redaction map gives each a role.
NAMES = ["Fictional Officer", "Ms Jane Placeholder"]
REDACT = {"Fictional Officer": "Investigating Officer", "Ms Jane Placeholder": "Document Controller"}
ORGS = ["Acme Contractors Pvt Ltd", "Acme Contractors"]
APPROVABLE_SUMMARY = [("Investigating Officer", "Fictional Officer")]
APPROVABLE_NARRATIVE = (  # over 200 characters, so ingest reads it as the narrative
    "A seal on a transfer pump was changed on the night shift. The pump was restarted without a leak test, the new "
    "seal leaked, and the vapour found an ignition source near the pump. The fire was put out by the site fire team. "
    "The regulator was told the same morning.")


def approvable(wb):
    """Completed, FND-0001 edited by a person, plus the fictional identifying details the Phase 2 tests mask."""
    f = wb["Identified Findings"]
    col = {c.value: c.column for c in f[1]}
    rows = {f.cell(r, 1).value: r for r in range(2, f.max_row + 1)}
    f.cell(rows["FND-0001"], col["User Edited"]).value = "Yes"
    f.cell(rows["FND-0001"], col["AI Justification"]).value = (
        "Work order from Acme Contractors Pvt Ltd shows pump P-101 restarted at 03:12 on 2024-03-20 with no leak "
        "test recorded [EVD-0001].")
    f.cell(rows["FND-0002"], col["AI Justification"]).value = (
        "Procedure index has no entry [EVD-0002]; Ms Jane Placeholder confirmed the gap.")
    f.cell(rows["FND-0004"], col["Individuals Involved"]).value = (
        "Control Room Operators, Emergency Response planners, Security Guard - Gate 3")
    e = wb["Evidence Links"]
    e.cell(3, 7).value = "Index; queries to docs.control@example.com, staff no. 4471"


WORKBOOKS = {"uat-votes.xlsx": votes, "uat-renamed-header.xlsx": renamed_header, "uat-capa-planner.xlsx": capa_planner,
             "uat-approvable.xlsx": approvable}
SUMMARY = {"uat-approvable.xlsx": (APPROVABLE_SUMMARY, APPROVABLE_NARRATIVE)}


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

# The L3-01 test pack, as tests/fixtures/packs/bad-l3-01.json: a name, blame words, an outside fact, a percentage
# and a retraining fix.
BAD_PACK = {
    "pack": "uat-bad-pack", "schema": 1, "title": "UAT bad pack: the L3-01 test pack", "audience": "Site leadership",
    "status": STATUS,
    "bottom_line": [{"text": "John Smith was careless and should be disciplined", "cites": ["FND-0001"]}],
    "sections": [{"id": "what-to-change", "heading": "What to change", "items": [
        {"kind": "para", "text": "As at the Northfield refinery fire, 80% of such fires start at flanges",
         "cites": ["FND-0001"]},
        {"kind": "recommendation", "change": "Retrain the fitter and hold him accountable",
         "indicator": "Share of fitters retrained", "hoc_tier": "training", "cites": ["FND-0002"]}]}]}

SHAREABLE_PACK = {
    "pack": "uat-shareable-pack", "schema": 1, "title": "UAT shareable pack: synthetic pump fire",
    "audience": "Site leadership", "status": STATUS,
    "bottom_line": [
        {"text": "A pump went back into service after a seal change with no leak test.", "cites": ["FND-0001"]},
        {"text": "No return-to-service checklist set a hold point for the test.", "cites": ["FND-0002"]}],
    "sections": [{"id": "learnings", "heading": "Learnings", "items": [
        {"kind": "learning", "lesson": "When a joint is disturbed, a leak test before restart is the barrier.",
         "cites": ["FND-0001", "EVD-0001"]},
        {"kind": "learning", "lesson": "Seals bought without a specification weaken every joint they go into.",
         "cites": ["FND-0003", "EVD-0003"]},
        {"kind": "learning", "lesson": "A gas alarm that only displays leaves the response to whoever sees it.",
         "cites": ["FND-0004"]},
        {"kind": "recommendation", "change": "Block restart until a signed leak-test record is attached.",
         "indicator": "Share of restarts with a leak-test record", "hoc_tier": "engineering",
         "cites": ["FND-0001", "FND-0002"]}]}]}

REGISTER = {"title": "UAT register: synthetic pump fire", "source": "uat-approvable.xlsx", "status": STATUS,
            "entries": [
    {"lr_id": "LR-01", "title": "Return to service without a leak test", "finding_ids": ["FND-0001", "FND-0002"],
     "evidence_ids": ["EVD-0001", "EVD-0002"], "priority": 1, "owner_entity": "F02 Mechanical Maintenance",
     "hfacs_level": "L3 Supervision Inadequate", "tiers": ["T1", "T2"],
     "lesson": "When a joint is disturbed, a leak test before restart is the barrier, and a checklist holds it.",
     "context": "A pump went back into service after a seal change with no leak test recorded.",
     "tier_messages": {"T1": "Do not restart without the leak-test record.", "T2": "Hold point before acceptance."},
     "recommendations": [{"what": "Block restart until a signed leak-test record is attached",
                          "hoc_tier": "engineering", "leading_indicator": "Share of restarts with a leak-test record"}]},
    {"lr_id": "LR-02", "title": "Seals without a specification", "finding_ids": ["FND-0003"],
     "evidence_ids": ["EVD-0003"], "priority": 2, "owner_entity": "F06 Materials Management",
     "hfacs_level": "L4 Resource Management", "tiers": ["T3"],
     "lesson": "Spares bought without a specification weaken every joint they go into.",
     "context": "Seals were bought locally without a specification.",
     "tier_messages": {"T3": "Stock only seals that match the specification."},
     "recommendations": [{"what": "Stock only specification-approved seals, so a local substitute cannot be issued",
                          "hoc_tier": "substitution", "leading_indicator": "Share of seal issues that match the specification"}]}]}

PHASE2_JSON = {"uat-bad-pack.json": BAD_PACK, "uat-shareable-pack.json": SHAREABLE_PACK, "uat-register.json": REGISTER,
               "uat-redact.json": REDACT}
TEXT_FILES = {
    "uat-names.txt": "# Fictional names for the UAT (no real person). One name per line; # starts a comment.\n"
                     + "\n".join(NAMES) + "\n",
    "uat-orgs.txt": "# Fictional organisation names for the UAT. One per line.\n" + "\n".join(ORGS) + "\n",
}


def main():
    ap = argparse.ArgumentParser(description="Write the UAT input files.")
    ap.add_argument("--out", type=Path, default=OUT, help="output folder (default: docs/uat/inputs)")
    out = ap.parse_args().out
    out.mkdir(parents=True, exist_ok=True)
    for name, edit in WORKBOOKS.items():
        wb = base_workbook(*SUMMARY.get(name, ()))
        edit(wb)
        wb.save(out / name)
        print(f"wrote {out / name}")
    for name, p in {**PACKS, **PHASE2_JSON}.items():
        (out / name).write_text(json.dumps(p, indent=1) + "\n", encoding="utf-8")
        print(f"wrote {out / name}")
    for name, text in TEXT_FILES.items():
        (out / name).write_text(text, encoding="utf-8")
        print(f"wrote {out / name}")


if __name__ == "__main__":
    main()
