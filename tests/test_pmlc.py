"""Engine tests on a small synthetic export (fictional event, no real data)."""
import json
import subprocess
import sys
from pathlib import Path

import pytest

openpyxl = pytest.importorskip("openpyxl")
ROOT = Path(__file__).resolve().parents[1]
PMLC = ROOT / "skills" / "learnings-coach" / "scripts" / "pmlc.py"
sys.path.insert(0, str(PMLC.parent))
import pmlc  # noqa: E402  (engine module; standard-library imports only)

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
     "Delayed response; see OR 2.2.", "Control Room Operators, Emergency Response planners, Mr Fictional Person",
     "EVD-0002", None, None, None, None, "No", None, None],
]


@pytest.fixture(scope="module")
def ws(tmp_path_factory):
    d = tmp_path_factory.mktemp("pmlc")
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
    c.append(["Link ID", "From Code", "From Level", "To Code"])
    c.append(["No causal links found", None, None, None])
    x = d / "export.xlsx"
    wb.save(x)
    run("ingest", str(x), "--out", str(d / "ws"))
    run("classify", str(d / "ws"))
    return d / "ws"


def run(*args):
    r = subprocess.run([sys.executable, str(PMLC), *args], capture_output=True, text=True)
    assert r.returncode == 0, r.stderr + r.stdout
    return r.stdout


def test_ingest(ws):
    F = json.loads((ws / "findings.json").read_text())
    assert len(F) == 4
    assert F[0]["roles"] == ["Pump Technician (seal change crew)", "Maintenance Supervisor (return-to-service approval)"]
    E = json.loads((ws / "evidence.json").read_text())
    assert set(E) == {"EVD-0001", "EVD-0002", "EVD-0003"}
    inc = json.loads((ws / "incident.json").read_text())
    assert inc["fields"]["Incident Title"] == "Synthetic pump fire"
    assert inc["causal_chain_sheet"] == []


def test_classify(ws):
    cl = json.loads((ws / "clusters.json").read_text())
    rm = cl["role_map"]
    assert "F02" in rm["Pump Technician (seal change crew)"]["F"]
    assert rm["Maintenance Supervisor (return-to-service approval)"]["T"] == "T2"
    assert rm["Maintenance Supervisor (return-to-service approval)"]["R"] == "approver"
    assert rm["Reliability Engineer (absent)"]["R"] == "absent"
    assert "F06" in rm["Stores/Procurement Officer"]["F"]
    assert "F09b" in rm["Emergency Response planners"]["F"]
    assert "Mr Fictional Person" in cl["unresolved_roles"]


def test_overrides(ws, tmp_path):
    o = tmp_path / "o.json"
    o.write_text(json.dumps({"Mr Fictional Person": {"F": ["F01"], "T": "T1", "R": "actor"}}))
    run("classify", str(ws), "--overrides", str(o))
    cl = json.loads((ws / "clusters.json").read_text())
    assert "Mr Fictional Person" not in cl["unresolved_roles"]


def test_causal(ws):
    out = run("causal", str(ws))
    g = json.loads((ws / "causal_graph.json").read_text())
    pairs = {(e["from"], e["to"]) for e in g["edges"]}
    assert ("SV 1.4", "AB 1.1") in pairs
    assert ("OR 2.2", "SV 1.4") in pairs
    assert (ws / "causal_graph.mmd").read_text().startswith("flowchart")
    assert "distinct links" in out


def test_select_and_timeline(ws):
    out = run("select", str(ws), "--entity", "F02", "--brief")
    assert "FND-0001" in out
    out = run("select", str(ws), "--level", "4", "--format", "json")
    assert json.loads(out)[0]["id"] == "FND-0003"
    run("timeline", str(ws), "--before", "2024-03-20")
    t = json.loads((ws / "timeline_candidates.json").read_text())
    assert any(x["date"] == "2024-03-12" for x in t)


def test_interfaces_dashboard_register(ws, tmp_path):
    run("interfaces", str(ws))
    assert json.loads((ws / "interfaces.json").read_text())["pairs"]
    html = tmp_path / "d.html"
    run("dashboard", str(ws), "--out", str(html))
    assert "ProbeMatrix Learnings Coach" in html.read_text()
    reg = tmp_path / "r.json"
    reg.write_text(json.dumps({"entries": [
        {"lr_id": "LR-01", "title": "Return to service without a test", "finding_ids": ["FND-0001"], "priority": 1,
         "owner_entity": "F02 Mechanical Maintenance", "hfacs_level": "L3 Supervision Inadequate",
         "tier_messages": {"T1": "Do not pressurise without the test record.", "T2": "Hold point before acceptance."},
         "recommendations": [{"what": "x", "hoc_tier": "Engineering control: interlock"},
                             {"what": "y", "hoc_tier": "Administrative (procedure)"}]}]}))
    out = tmp_path / "r.xlsx"
    run("register-xlsx", str(reg), "--out", str(out))
    wb = openpyxl.load_workbook(out)
    assert wb.sheetnames == ["Learnings Register", "Recommendations", "Learning Plan", "Summary", "About"]
    summary = [tuple(r) for r in wb["Summary"].iter_rows(values_only=True)]
    assert ("Recommendations by control tier", "engineering", 1) in summary
    assert ("Learnings by HFACS level", "L3 Supervision", 1) in summary
    assert ("Learnings by cluster", "F02", 1) in summary
    assert wb["Learning Plan"]["D2"].value == "Do not pressurise without the test record."
    html2 = tmp_path / "d2.html"
    run("dashboard", str(ws), "--out", str(html2), "--register", str(reg))
    t = html2.read_text()
    assert "Learning plan by level" in t and "Hold point before acceptance." in t and "50%" in t


def test_check_register_and_overrides(ws, tmp_path):
    good = {"entries": [{"lr_id": "LR-01", "finding_ids": ["FND-0001", "FND-0002"], "evidence_ids": ["EVD-0001"],
                         "hfacs_level": "L3 x", "priority": 1, "owner_entity": "F02 Mechanical Maintenance",
                         "tier_messages": {"T2": "m"},
                         "recommendations": [{"what": "w", "hoc_tier": "engineering", "leading_indicator": "i"}]}]}
    p = tmp_path / "g.json"
    p.write_text(json.dumps(good))
    out = run("check-register", str(ws), str(p))
    assert "0 problem" in out and "2 of 4 findings covered" in out
    bad = {"entries": [{"lr_id": "LR-02", "finding_ids": ["FND-9999"], "recommendations": [{"hoc_tier": "maybe"}]}]}
    p.write_text(json.dumps(bad))
    r = subprocess.run([sys.executable, str(PMLC), "check-register", str(ws), str(p)], capture_output=True, text=True)
    assert r.returncode == 1 and "unknown finding FND-9999" in r.stdout and "no leading_indicator" in r.stdout
    h = tmp_path / "d.html"
    run("dashboard", str(ws), "--out", str(h), "--date", "2024-03-21", "--title", "Pump fire")
    assert "2024-03-21" in h.read_text() and "Pump fire" in h.read_text()


def test_scan_names(ws, tmp_path):
    n = tmp_path / "names.txt"
    n.write_text("Fictional Person\n")
    r = subprocess.run([sys.executable, str(PMLC), "scan-names", str(n), str(ws / "findings.json")],
                       capture_output=True, text=True)
    assert r.returncode == 1 and "1 hit" in r.stdout


def test_slug_rules():
    assert pmlc.run_slug("2020-09-24", "hazira-gas-release-fire") == "2020-09-24-hazira-gas-release-fire"
    assert pmlc.run_slug("2020-09-24 00:00:00", "a1") == "2020-09-24-a1"
    for bad in ["Hazira", "gas_fire", "-fire", "fire-", "gas--fire", "", None]:
        with pytest.raises(ValueError):
            pmlc.run_slug("2020-09-24", bad)
    for bad_date in ["24/09/2020", "2020-13-01", "", None]:
        with pytest.raises(ValueError):
            pmlc.run_slug(bad_date, "fire")
    assert pmlc.valid_run_slug("2020-09-24-hazira-fire")
    assert not pmlc.valid_run_slug("2020-02-30-x")
    assert not pmlc.valid_run_slug("hazira-2020")
    assert not pmlc.valid_run_slug("2020-09-24")


def test_outputs_dir(tmp_path):
    std = tmp_path / "pmlc-runs" / "2020-09-24-hazira-fire" / "workspace"
    assert pmlc.is_standard_ws(std)
    assert pmlc.outputs_dir(std) == (tmp_path / "pmlc-runs" / "2020-09-24-hazira-fire" / "outputs").resolve()
    legacy = tmp_path / "pmlc-hazira2020"
    assert not pmlc.is_standard_ws(legacy)
    assert pmlc.outputs_dir(legacy) == legacy.resolve() / "outputs"
    assert not pmlc.is_standard_ws(tmp_path / "runs" / "2020-09-24-x" / "workspace")
    assert not pmlc.is_standard_ws(tmp_path / "pmlc-runs" / "Bad" / "workspace")
