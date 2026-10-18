"""Engine tests on a small synthetic export (fictional event, no real data)."""
import argparse
import json
import re
import shutil
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

MINI_REG = {"title": "Synthetic register", "source": "export.xlsx", "entries": [
    {"lr_id": "LR-01", "title": "Return to service without a test", "finding_ids": ["FND-0001", "FND-0002"],
     "evidence_ids": ["EVD-0001"], "priority": 1, "owner_entity": "F02 Mechanical Maintenance",
     "hfacs_level": "L3 Supervision Inadequate", "tiers": ["T1", "T2"],
     "lesson": "If a joint is disturbed, test it before service, because untested joints leak (EVD-0001).",
     "precursors": "Earlier seal leaks", "custom_field": "kept as given",
     "tier_messages": {"T1": "Do not pressurise without the test record.", "T2": "Hold point before acceptance."},
     "recommendations": [
         {"what": "Interlock pressurisation on a signed test record", "hoc_tier": "Engineering control: interlock",
          "leading_indicator": "Share of restarts with a test record", "owner_note": "extra key"},
         {"what": "y </script><script>alert(1)</script> & <b>", "hoc_tier": "Administrative (procedure)",
          "leading_indicator": "i"}]}]}


def make_export(d: Path) -> Path:
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
    return x


@pytest.fixture(scope="module")
def ws(tmp_path_factory):
    d = tmp_path_factory.mktemp("pmlc")
    x = make_export(d)
    run("ingest", str(x), "--legacy-out", str(d / "ws"))
    run("classify", str(d / "ws"))
    return d / "ws"


def run(*args):
    r = subprocess.run([sys.executable, str(PMLC), *args], capture_output=True, text=True)
    assert r.returncode == 0, r.stderr + r.stdout
    return r.stdout


def run_fail(*args):
    r = subprocess.run([sys.executable, str(PMLC), *args], capture_output=True, text=True)
    assert r.returncode != 0, r.stdout
    return r


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


def test_overrides_survive_plain_reclassify(tmp_path):
    x = make_export(tmp_path)
    w = tmp_path / "ws"
    run("ingest", str(x), "--legacy-out", str(w))
    run("classify", str(w))
    (w / "role_overrides.json").write_text(
        json.dumps({"Mr Fictional Person": {"F": ["F01"], "T": "T1", "R": "actor"},
                    "Stores/Procurement Officer": {"T": "T1"}}))
    out = run("classify", str(w))  # plain re-run, as training-designer used to do
    assert "Applied 2 override(s) from" in out
    cl = json.loads((w / "clusters.json").read_text())
    assert cl["role_map"]["Mr Fictional Person"]["source"] == "override"
    assert cl["overrides"]["applied"] == 2 and cl["overrides"]["stale"] == []
    assert cl["overrides"]["file"].endswith("role_overrides.json")
    assert not (w / "unresolved_roles.json").exists()
    run("classify", str(w), "--no-overrides")
    cl = json.loads((w / "clusters.json").read_text())
    assert cl["role_map"]["Mr Fictional Person"]["source"] == "rule"
    assert cl["overrides"] == {"file": None, "applied": 0, "stale": []}
    assert (w / "unresolved_roles.json").exists()


def test_overrides_bad_json_and_stale_keys(tmp_path):
    x = make_export(tmp_path)
    w = tmp_path / "ws"
    run("ingest", str(x), "--legacy-out", str(w))
    (w / "role_overrides.json").write_text("{not json")
    r = run_fail("classify", str(w))
    assert "role_overrides.json" in r.stderr and "--no-overrides" in r.stderr
    run("classify", str(w), "--no-overrides")
    (w / "role_overrides.json").write_text(json.dumps({"Nobody Here": {"F": ["F01"]}}))
    out = run("classify", str(w))
    assert "warning: 1 override(s) match no role: Nobody Here" in out
    cl = json.loads((w / "clusters.json").read_text())
    assert cl["overrides"]["stale"] == ["Nobody Here"] and cl["overrides"]["applied"] == 0


def test_explicit_overrides_file_recorded(tmp_path):
    x = make_export(tmp_path)
    w = tmp_path / "ws"
    run("ingest", str(x), "--legacy-out", str(w))
    o = tmp_path / "o.json"
    o.write_text(json.dumps({"Mr Fictional Person": {"F": ["F01"], "T": "T1", "R": "actor"}}))
    run("classify", str(w), "--overrides", str(o))
    cl = json.loads((w / "clusters.json").read_text())
    assert cl["overrides"]["file"] == str(o) and cl["overrides"]["applied"] == 1


def test_training_designer_never_classifies():
    assert "PMLC classify" not in (ROOT / "skills/training-designer/SKILL.md").read_text()


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


def test_scan_names_reports_files_it_cannot_read(tmp_path):
    n = tmp_path / "names.txt"
    n.write_text("Fictional Person\n")
    d = tmp_path / "out"
    d.mkdir()
    (d / "notes.md").write_text("roles only\n")
    (d / "report.pdf").write_bytes(b"%PDF-1.4 Fictional Person")
    r = subprocess.run([sys.executable, str(PMLC), "scan-names", str(n), str(d)], capture_output=True, text=True)
    assert r.returncode == 2 and "0 hit(s)" in r.stdout and "report.pdf" in r.stdout and "not scanned" in r.stdout
    assert "pdftotext" in r.stdout                                    # tells you how to scan it
    (d / "report.pdf").unlink()
    r = subprocess.run([sys.executable, str(PMLC), "scan-names", str(n), str(d)], capture_output=True, text=True)
    assert r.returncode == 0 and "not scanned" not in r.stdout


def test_slug_rules():
    assert pmlc.run_slug("2020-09-24", "hazira-gas-release-fire") == "2020-09-24-hazira-gas-release-fire"
    assert pmlc.run_slug("2020-09-24 00:00:00", "a1") == "2020-09-24-a1"
    for bad in ["Hazira", "gas_fire", "-fire", "fire-", "gas--fire", "", None]:
        with pytest.raises(ValueError):
            pmlc.run_slug("2020-09-24", bad)
    for bad_date in ["24/09/2020", "2020-13-01", "2024-03-211", "", None]:
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


def test_ingest_standard_layout(tmp_path):
    x = make_export(tmp_path)
    out = run("ingest", str(x), "--slug", "pump-fire")
    run_dir = tmp_path / "pmlc-runs" / "2024-03-20-pump-fire"
    assert (run_dir / "workspace" / "findings.json").exists()
    assert (run_dir / "outputs").is_dir()
    assert "outputs:" in out
    r = run_fail("ingest", str(x), "--slug", "pump-fire")
    assert "already holds a workspace" in r.stderr
    run("ingest", str(x), "--slug", "pump-fire", "--force")


def test_ingest_date_override_and_root(tmp_path):
    x = make_export(tmp_path)
    root = tmp_path / "elsewhere"
    run("ingest", str(x), "--slug", "pump-fire", "--date", "2024-03-21", "--root", str(root))
    assert (root / "pmlc-runs" / "2024-03-21-pump-fire" / "workspace" / "findings.json").exists()


def test_ingest_explicit_standard_out(tmp_path):
    x = make_export(tmp_path)
    ws = tmp_path / "pmlc-runs" / "2024-03-20-pump-fire" / "workspace"
    run("ingest", str(x), "--out", str(ws))
    assert (ws / "findings.json").exists() and (ws.parent / "outputs").is_dir()


@pytest.mark.parametrize("args, msg", [
    ([], "--slug"),
    (["--slug", "Pump Fire"], "lowercase"),
    (["--slug", "pump-fire", "--date", "20/03/2024"], "--date"),
    (["--out", "somewhere/ws"], "pmlc-runs"),
])
def test_ingest_refusals(tmp_path, args, msg):
    x = make_export(tmp_path)
    r = run_fail("ingest", str(x), *args)
    assert msg in r.stderr
    assert not (tmp_path / "pmlc-runs").exists()


def test_default_output_paths(tmp_path):
    x = make_export(tmp_path)
    run("ingest", str(x), "--slug", "pump-fire")
    run_dir = tmp_path / "pmlc-runs" / "2024-03-20-pump-fire"
    ws = run_dir / "workspace"
    run("classify", str(ws))
    run("dashboard", str(ws))
    assert (run_dir / "outputs" / "organisation-learning-map.html").exists()
    reg = run_dir / "outputs" / "learnings-register.json"
    reg.write_text(json.dumps(MINI_REG))
    run("register-xlsx", str(reg))
    assert (run_dir / "outputs" / "learnings-register.xlsx").exists()
    out = run("run-path", str(ws))
    assert "slug:      2024-03-20-pump-fire" in out
    assert f"outputs:   {(run_dir / 'outputs').resolve()}" in out
    assert "legacy layout" in run("run-path", str(tmp_path))


def test_downgraded_findings():
    w = {"incident": {"review_votes": [{"finding": "FND-1", "vote": "Downgrade"},
                                       {"finding": "FND-2", "vote": "upgrade"},
                                       {"finding": "FND-3", "vote": "remove"}]}}
    assert pmlc.downgraded_findings(w) == {"FND-1", "FND-3"}
    assert pmlc.downgraded_findings({}) == set()


def test_detail_data(ws):
    w = pmlc.load_ws(ws)
    d = pmlc.build_detail_data(w, MINI_REG)
    assert d["register"] == {"title": "Synthetic register", "source": "export.xlsx"}
    assert d["entries"][0]["custom_field"] == "kept as given"
    assert d["entries"][0]["recommendations"][0]["owner_note"] == "extra key"
    assert set(d["findings"]) == {"FND-0001", "FND-0002", "FND-0003", "FND-0004"}
    assert d["findings"]["FND-0001"]["clusters"]["F"]
    assert d["findings"]["FND-0001"]["votes"] == []
    assert set(d["evidence"]) == {"EVD-0001", "EVD-0002", "EVD-0003"}
    assert {u["id"]: u["reason"] for u in d["uncovered"]} == {
        "FND-0003": "not covered by any learning", "FND-0004": "not covered by any learning"}
    assert d["derived"]["LR-01"] == {"level": "L3 Supervision", "entity": "F02",
                                     "hoc": ["engineering", "administrative"], "strongest": "engineering"}
    assert d["totals"] == {"findings": 4, "evidence": 3}
    assert d["tier_labels"]["T5"] == "Corporate / board"
    assert d["labels"]["worst_case"] == "Credible worst case"
    w2 = dict(w, incident=dict(w["incident"], review_votes=[{"finding": "FND-0004", "vote": "downgrade", "reason": "r"}]))
    d2 = pmlc.build_detail_data(w2, MINI_REG)
    assert {u["id"]: u["reason"] for u in d2["uncovered"]}["FND-0004"] == "reviewer downgrade vote"
    assert d2["findings"]["FND-0004"]["votes"][0]["vote"] == "downgrade"


def test_detail_data_minimal_workspace(ws):
    w = {"findings": pmlc.load_ws(ws)["findings"]}
    d = pmlc.build_detail_data(w, [{"lr_id": "LR-09", "finding_ids": ["FND-0001", "FND-9999"]}])
    assert d["register"] == {} and d["evidence"] == {}
    assert "FND-9999" not in d["findings"] and d["findings"]["FND-0001"]["clusters"] == {}
    assert d["derived"]["LR-09"]["strongest"] == "unclassified"


def test_embed_json_is_script_safe():
    s = pmlc.embed_json({"t": "</script><b>&"})
    assert "<" not in s and ">" not in s and "&" not in s
    assert json.loads(s) == {"t": "</script><b>&"}


def test_sample_folders(tmp_path):
    tracked = subprocess.run(["git", "ls-files", "samples"], cwd=ROOT, capture_output=True, text=True).stdout.split()
    tracked_dirs = {Path(x).parts[1] for x in tracked if len(Path(x).parts) > 2}
    assert [p for p in pmlc.sample_folder_problems(ROOT / "samples") if p.split(":")[0] in tracked_dirs] == []
    (tmp_path / "Hazira_2020").mkdir()
    good = tmp_path / "2020-09-24-hazira-gas-release-fire"
    good.mkdir()
    probs = pmlc.sample_folder_problems(tmp_path)
    assert any("Hazira_2020" in p and "folder name" in p for p in probs)
    assert any(good.name in p and "README.md" in p for p in probs)
    (good / "README.md").write_text("x")
    (good / f"{good.name}_probematrix-findings.xlsx").write_bytes(b"x")
    assert [p for p in pmlc.sample_folder_problems(tmp_path) if good.name in p] == []
    r = subprocess.run([sys.executable, str(PMLC), "check-samples", str(tmp_path)], capture_output=True, text=True)
    assert r.returncode == 1 and "Hazira_2020" in r.stdout


def test_make_public_sample_slug(tmp_path):
    x = make_export(tmp_path)
    names = tmp_path / "names.txt"
    names.write_text("Nobody Here\n")
    tool = ROOT / "tools" / "make-public-sample.py"
    r = subprocess.run([sys.executable, str(tool), str(x), "--slug", "Bad_Slug", "--names", str(names)],
                       capture_output=True, text=True)
    assert r.returncode != 0 and "--slug" in r.stderr
    root = tmp_path / "samples"
    r = subprocess.run([sys.executable, str(tool), str(x), "--slug", "2024-03-20-pump-fire", "--names", str(names),
                        "--samples-root", str(root)], capture_output=True, text=True)
    assert r.returncode == 0, r.stderr + r.stdout
    assert (root / "2024-03-20-pump-fire" / "2024-03-20-pump-fire_probematrix-findings.xlsx").exists()


def test_ingest_review_fixes(tmp_path):
    x = make_export(tmp_path)
    ws = tmp_path / "pmlc-runs" / "2024-03-20-pump-fire" / "workspace"
    run("ingest", str(x), "--out", str(ws))
    assert "already holds a workspace" in run_fail("ingest", str(x), "--out", str(ws)).stderr
    assert "not allowed with" in run_fail("ingest", str(x), "--slug", "a", "--legacy-out", str(tmp_path / "lw")).stderr
    r = subprocess.run([sys.executable, str(PMLC), "ingest", str(x), "--legacy-out", str(ws), "--force"],
                       capture_output=True, text=True)
    assert r.returncode == 0 and "Warning" not in r.stderr
    assert "No such folder" in run_fail("check-samples", str(tmp_path / "nope")).stderr


def test_ingest_excel_datetime_date(tmp_path):
    import datetime as _dt
    x = make_export(tmp_path)
    wb = openpyxl.load_workbook(x)
    for row in wb["Incident Summary"].iter_rows():
        if row[0].value == "Date":
            row[1].value = _dt.datetime(2024, 3, 20, 0, 0)
    wb.save(x)
    run("ingest", str(x), "--slug", "pump-fire")
    assert (tmp_path / "pmlc-runs" / "2024-03-20-pump-fire" / "workspace" / "findings.json").exists()


def test_check_register_flags_downgraded_citation(ws, tmp_path):
    import shutil as _sh
    w2 = tmp_path / "w2"
    _sh.copytree(ws, w2)
    inc = json.loads((w2 / "incident.json").read_text())
    inc["review_votes"] = [{"finding": "FND-0001", "vote": "downgrade", "reason": "r"}, {"finding": "FND-0002"}]
    (w2 / "incident.json").write_text(json.dumps(inc))
    reg = tmp_path / "r.json"
    reg.write_text(json.dumps(MINI_REG))
    r = subprocess.run([sys.executable, str(PMLC), "check-register", str(w2), str(reg)], capture_output=True, text=True)
    assert "cites FND-0001, which has a reviewer downgrade vote" in r.stdout
    assert "FND-0001 (r)" in run("profile", str(w2))


def test_make_public_sample_dst_and_missing(tmp_path):
    x = make_export(tmp_path)
    names = tmp_path / "names.txt"
    names.write_text("Nobody Here\n")
    tool = ROOT / "tools" / "make-public-sample.py"
    out = tmp_path / "plain.xlsx"
    r = subprocess.run([sys.executable, str(tool), str(x), str(out), "--names", str(names)], capture_output=True, text=True)
    assert r.returncode == 0 and out.exists(), r.stderr
    r = subprocess.run([sys.executable, str(tool), str(x), "--names", str(names)], capture_output=True, text=True)
    assert r.returncode != 0 and "--slug" in r.stderr


def _data_block(t):
    m = re.search(r'<script type="application/json" id="pmlc-data">(.*?)</script>', t, re.S)
    assert m, "no pmlc-data block"
    return json.loads(m.group(1))


def test_dashboard_two_tabs(ws, tmp_path):
    reg = tmp_path / "r.json"
    reg.write_text(json.dumps(MINI_REG))
    out = tmp_path / "d.html"
    run("dashboard", str(ws), "--register", str(reg), "--out", str(out))
    t = out.read_text(encoding="utf-8")
    assert 'role="tablist"' in t and 'id="tab-overview"' in t and 'id="tab-detail"' in t
    assert 'href="#detail/LR-01"' in t
    assert "Learning plan by level" in t and "Who learns, at which level" in t
    d = _data_block(t)
    assert d["entries"][0]["recommendations"][1]["what"].startswith("y </script>")
    assert set(d["findings"]) == {"FND-0001", "FND-0002", "FND-0003", "FND-0004"}
    assert t.count("</script>") == 2
    assert not re.search(r'<(script|link)[^>]+(src|href)="https?:', t)
    assert "function init()" in t and ".tabbar{" in t
    assert "ProbeMatrix Learnings Coach" in t


def test_dashboard_without_register_has_no_tabs(ws, tmp_path):
    out = tmp_path / "d.html"
    run("dashboard", str(ws), "--out", str(out))
    t = out.read_text(encoding="utf-8")
    assert 'role="tablist"' not in t and "pmlc-data" not in t and "<script" not in t
    assert "--register" in t and "Who learns, at which level" in t


def test_citation_records(ws):
    w = pmlc.load_ws(ws)
    w = dict(w, incident=dict(w["incident"], review_votes=[{"finding": "FND-0003", "vote": "downgrade", "reason": "r"}]))
    f, e = pmlc.citation_records(w, ["FND-0003", "FND-9999", "FND-0003"], ["EVD-0002", "EVD-0404"])
    assert list(f) == ["FND-0003"]
    assert f["FND-0003"]["votes"][0]["vote"] == "downgrade" and f["FND-0003"]["clusters"]["F"]
    assert list(e) == ["EVD-0002", "EVD-0003", "EVD-0001"]
    assert pmlc.citation_records({"findings": []}, ["FND-0001"]) == ({}, {})


def test_map_uses_shared_tokens_and_wide_rule(ws, tmp_path):
    out = tmp_path / "d.html"
    run("dashboard", str(ws), "--out", str(out))
    t = out.read_text(encoding="utf-8")
    assert pmlc.PAGE_TOKENS_CSS in t
    assert pmlc.WIDE_CSS in t and "@media (min-width:1400px)" in t
    assert t.index("main{max-width:1180px") < t.index(pmlc.WIDE_CSS)


def test_version_single_source():
    assert re.fullmatch(r"\d+\.\d+\.\d+((a|rc)\d+)?", pmlc.__version__)
    assert f"v{pmlc.__version__}" in pmlc.BRAND
    assert run("--version").strip() == f"pmlc {pmlc.__version__}"


def test_build_parser_has_every_subcommand():
    sub = next(a for a in pmlc.build_parser()._actions if isinstance(a, argparse._SubParsersAction))
    assert {"ingest", "classify", "select", "check-register", "check-pack", "pack"} <= set(sub.choices)


def test_release_script_bumps_all_three(tmp_path):
    files = ["skills/learnings-coach/scripts/pmlc.py", ".claude-plugin/plugin.json", ".claude-plugin/marketplace.json"]
    for f in files:
        (tmp_path / f).parent.mkdir(parents=True, exist_ok=True)
        shutil.copy(ROOT / f, tmp_path / f)
    r = subprocess.run([sys.executable, str(ROOT / "tools" / "release.py"), "2.0.0a1", "--root", str(tmp_path)],
                       capture_output=True, text=True)
    assert r.returncode == 0, r.stderr + r.stdout
    assert '__version__ = "2.0.0a1"' in (tmp_path / files[0]).read_text(encoding="utf-8")
    for f in files[1:]:
        assert '"version": "2.0.0a1"' in (tmp_path / f).read_text(encoding="utf-8"), f
    assert "git tag -a v2.0.0-alpha.1" in r.stdout
    bad = subprocess.run([sys.executable, str(ROOT / "tools" / "release.py"), "banana", "--root", str(tmp_path)],
                         capture_output=True, text=True)
    assert bad.returncode != 0


# ----------------------------------------------------------------------------- taxonomy v2.0: tags, F14 split, overlays

def test_sign_no_longer_matches_design():
    tax = pmlc._load_taxonomy()
    assert pmlc.map_role("F&G System Designers", tax)["R"] != "approver"
    assert pmlc.map_role("Permit signatory", tax)["R"] == "approver"
    assert pmlc.map_role("Supervisors who signed the permit", tax)["R"] == "approver"
    assert pmlc.map_role("Supervisor (calibration sign-off)", tax)["R"] == "approver"
    assert pmlc.map_role("Line Supervisors who assigned them", tax)["R"] != "approver"


def test_rank_beats_policy():
    tax = pmlc._load_taxonomy()
    assert pmlc.map_role("Plant Management (policy owner)", tax)["T"] == "T4"
    assert pmlc.map_role("Corporate policy owner", tax)["T"] == "T5"
    assert pmlc.map_role("HR/Training Supervisor", tax)["T"] == "T2"
    assert pmlc.map_role("Policy owner", tax)["T"] == "T3"          # 'owner' is a T3 match
    assert pmlc.map_role("Policy", tax)["T"] == "T5"                # weak: only when no tier matches
    assert pmlc.map_role("Plant management responsible for MOC governance", tax)["T"] == "T4"
    assert pmlc.map_role("Governance", tax)["T"] == "T5"            # governance is weak T5 (ruling R6)


def test_f07_document_token_is_narrow():
    tax = pmlc._load_taxonomy()
    assert "F07" not in pmlc.map_role("Supervisors who signed incomplete calibration documents", tax)["F"]
    assert "F07" not in pmlc.map_role("Maintenance documentation supervision", tax)["F"]
    for r in ("Document control", "Engineering Document Control", "Engineering documentation control",
              "Document control supervisors", "Engineering/Document Control Team"):
        assert "F07" in pmlc.map_role(r, tax)["F"], r


def test_f14_split():
    tax = pmlc._load_taxonomy()
    assert pmlc.map_role("Corporate Director", tax)["F"] == ["F14"]
    assert pmlc.map_role("Statutory inspectorate", tax)["F"] == ["F15"]
    assert pmlc.map_role("OEM / seal manufacturer", tax)["F"] == ["F16"]
    assert pmlc.map_role("Contractor crew", tax)["F"][-1] == "F17"
    tags = {e["id"]: e["tags"] for e in tax["entities"]}
    assert tags["F17"] == ["contractor", "supply"] and tags["F16"] == ["supply"] and tags["F15"] == ["external"]
    assert all(tags[e] for e in tags)


def test_site_tokens_need_the_overlay():
    assert "F10" not in pmlc.map_role("CISF constable", pmlc._load_taxonomy())["F"]
    assert "F10" in pmlc.map_role("CISF constable", pmlc._load_taxonomy(overlays=["india-process-site"]))["F"]
    ov = pmlc._load_taxonomy(overlays=["india-process-site"])
    assert pmlc.map_role("CISF constable", ov)["T"] == "T1"
    assert pmlc.map_role("Resident Engineer", ov)["T"] == "T4"
    assert pmlc.map_role("SIC", ov)["F"] == ["F09b"]
    assert pmlc.map_role("SIC", pmlc._load_taxonomy())["F"] == []


def test_overlay_errors(tmp_path):
    with pytest.raises(SystemExit, match="not found"):
        pmlc._load_taxonomy(overlays=["no-such-overlay"])
    bad = tmp_path / "bad.json"
    bad.write_text(json.dumps({"name": "bad", "extend": {"entities": {"F77": "x"}}}), encoding="utf-8")
    with pytest.raises(SystemExit, match="F77"):
        pmlc._load_taxonomy(overlays=[str(bad)])


def test_classify_records_taxonomy_and_warns_on_change(tmp_path):
    x = make_export(tmp_path)
    w = tmp_path / "ws"
    run("ingest", str(x), "--legacy-out", str(w))
    out = run("classify", str(w))
    assert "warning: previous classify" not in out
    cl = json.loads((w / "clusters.json").read_text())
    assert cl["taxonomy"]["file"] == "taxonomy.json" and cl["taxonomy"]["overlays"] == []
    assert cl["taxonomy"]["tags"]["F09b"] == ["emergency"]
    out = run("classify", str(w), "--overlay", "india-process-site")
    assert "warning: previous classify used taxonomy.json; this run uses taxonomy.json + india-process-site" in out
    cl = json.loads((w / "clusters.json").read_text())
    assert cl["taxonomy"]["overlays"] == ["india-process-site"]
    assert "warning: previous classify" not in run("classify", str(w), "--overlay", "india-process-site")


def test_select_by_tag_and_unknown_tag(ws):
    ids = {d["id"] for d in json.loads(run("select", str(ws), "--tag", "emergency", "--format", "json"))}
    assert "FND-0004" in ids
    both = {d["id"] for d in json.loads(run("select", str(ws), "--tag", "emergency", "--entity", "F02",
                                            "--format", "json"))}
    f02 = {d["id"] for d in json.loads(run("select", str(ws), "--entity", "F02", "--format", "json"))}
    assert both == ids | f02
    r = run_fail("select", str(ws), "--tag", "nonsense")
    assert "nonsense" in r.stderr and "Tags in use" in r.stderr


def test_custom_taxonomy_renamed_ids_still_select_by_tag(tmp_path, ws):
    tax = json.loads((pmlc.REFS / "taxonomy.json").read_text(encoding="utf-8"))
    for i, e in enumerate(tax["entities"]):
        e["id"] = f"X{i}"
    p = tmp_path / "renamed.json"
    p.write_text(json.dumps(tax), encoding="utf-8")
    w2 = tmp_path / "ws2"
    shutil.copytree(ws, w2)
    run("classify", str(w2), "--taxonomy", str(p))
    cl = json.loads((w2 / "clusters.json").read_text())
    assert "F09b" not in cl["entities"] and cl["taxonomy"]["file"] == str(p)
    sel = lambda d: {x["id"] for x in json.loads(run("select", str(d), "--tag", "emergency", "--format", "json"))}  # noqa: E731
    assert sel(w2) == sel(ws)


def test_old_clusters_without_tags(ws, tmp_path):
    w2 = tmp_path / "old"
    shutil.copytree(ws, w2)
    cl = json.loads((w2 / "clusters.json").read_text())
    del cl["taxonomy"]["tags"]
    (w2 / "clusters.json").write_text(json.dumps(cl), encoding="utf-8")
    r = run_fail("select", str(w2), "--tag", "emergency")
    assert "Re-run classify" in r.stderr


def test_entities_for_tags():
    cl = {"taxonomy": {"file": "t.json", "tags": {"A": ["x"], "B": ["y", "x"], "C": ["z"]}}}
    assert pmlc.entities_for_tags(cl, ["x"]) == ["A", "B"]
    assert pmlc.entities_for_tags(cl, ["z", "y"]) == ["B", "C"]
    with pytest.raises(SystemExit, match=r"No entity has tag\(s\) \['q'\] in taxonomy t.json"):
        pmlc.entities_for_tags(cl, ["x", "q"])


def _ids(*args):
    return {f["id"] for f in json.loads(run(*args, "--format", "json"))}


def test_top_rated_and_run_path(ws):
    assert _ids("select", str(ws), "--top-rated") == {"FND-0002", "FND-0003"}
    out = run("run-path", str(ws))
    assert "top_rating: 4" in out and "incident_date: 2024-03-20" in out


def test_ingest_records_incident_date(tmp_path):
    x = make_export(tmp_path)
    run("ingest", str(x), "--legacy-out", str(tmp_path / "w1"), "--date", "2024-03-21")
    assert json.loads((tmp_path / "w1" / "incident.json").read_text())["date"] == "2024-03-21"
    run("ingest", str(x), "--legacy-out", str(tmp_path / "w2"))
    assert json.loads((tmp_path / "w2" / "incident.json").read_text())["date"] == "2024-03-20"


def test_subcategory_prefix_exclude_downgraded(tmp_path):
    x = make_export(tmp_path)
    wb = openpyxl.load_workbook(x)
    c = wb.create_sheet("Collaboration Data")
    for r in [("VOTES",), ("Finding ID", "Vote", "Reason"), ("FND-0004", "downgrade", "weak evidence")]:
        c.append(r)
    wb.save(x)
    w = tmp_path / "w"
    run("ingest", str(x), "--legacy-out", str(w))
    run("classify", str(w))
    assert _ids("select", str(w)) == {"FND-0001", "FND-0002", "FND-0003", "FND-0004"}
    assert _ids("select", str(w), "--exclude-downgraded") == {"FND-0001", "FND-0002", "FND-0003"}
    md = run("select", str(w), "--exclude-downgraded", "--brief")
    assert md.rstrip().splitlines()[-1] == "Excluded (reviewer downgrade): FND-0004"
    r = subprocess.run([sys.executable, str(PMLC), "select", str(w), "--exclude-downgraded", "--format", "json"],
                       capture_output=True, text=True)
    assert "Excluded (reviewer downgrade): FND-0004" in r.stderr
    assert json.loads(r.stdout)
    assert _ids("select", str(w), "--subcategory", "errors") == {"FND-0001"}
    assert _ids("select", str(w), "--prefix", "SV", "OR") == {"FND-0002", "FND-0003"}


def test_entity_mode_all_and_tags_synthetic(ws):
    both = _ids("select", str(ws), "--entity", "F02", "F06", "--entity-mode", "all")
    anyof = _ids("select", str(ws), "--entity", "F02", "F06")
    assert both <= anyof


def test_timeline_before_incident(ws):
    run("timeline", str(ws), "--before", "incident")
    a = (ws / "timeline_candidates.json").read_text()
    run("timeline", str(ws), "--before", "2024-03-20")
    assert (ws / "timeline_candidates.json").read_text() == a


def test_timeline_before_incident_without_date(tmp_path):
    x = make_export(tmp_path)
    run("ingest", str(x), "--legacy-out", str(tmp_path / "w"))
    p = tmp_path / "w" / "incident.json"
    d = json.loads(p.read_text())
    d.pop("date")
    d["fields"].pop("Date")
    p.write_text(json.dumps(d))
    r = run_fail("timeline", str(tmp_path / "w"), "--before", "incident")
    assert "No incident date in this workspace; pass --date to ingest." in r.stderr


def test_select_args_rejects_unknown_filter():
    assert pmlc.select_args(tag=["x"]).tag == ["x"] and pmlc.select_args().entity_mode == "any"
    with pytest.raises(TypeError):
        pmlc.select_args(bogus=1)


def test_no_placeholders_left():
    for p in (ROOT / "skills").glob("*/SKILL.md"):
        t = p.read_text(encoding="utf-8")
        assert "<top" not in t and "<incident date" not in t, p


def _select_proc(*args):
    r = subprocess.run([sys.executable, str(PMLC), "select", *map(str, args)], capture_output=True, text=True)
    assert r.returncode == 0, r.stderr
    return r


def test_budget_too_small_keeps_none(ws):
    r = _select_proc(ws, "--budget-chars", "10")
    assert "# Selected findings (0)" in r.stdout and "### FND" not in r.stdout and "## FND" not in r.stdout
    assert "Dropped for budget: 4 findings (lowest kept rating none): FND-0003, FND-0002, FND-0001, FND-0004" in r.stdout
    m = re.search(r"below the minimum output \((\d+) chars\); no findings kept", r.stderr)
    assert m and "select: budget 10 is below" in r.stderr and len(r.stdout) == int(m.group(1))
    assert "Dropped for budget: 4 findings" in r.stderr
    j = _select_proc(ws, "--budget-chars", "10", "--format", "json")
    assert json.loads(j.stdout) == [] and "Dropped for budget: 4 findings" in j.stderr


def test_budget_keeps_rating_order_and_counts_footers(ws):
    full = _select_proc(ws, "--brief").stdout
    r = _select_proc(ws, "--brief", "--budget-chars", str(len(full) - 1))
    assert len(r.stdout) <= len(full) - 1
    assert "Dropped for budget: " in r.stdout and "Dropped for budget: " in r.stderr
    assert "below the minimum" not in r.stderr
    assert re.search(r"select: \d+ findings, %d chars" % len(r.stdout), r.stderr)
    ok = _select_proc(ws, "--brief", "--budget-chars", str(len(full)))
    assert ok.stdout == full and "Dropped" not in ok.stdout


def test_fields_group_count(ws):
    items = json.loads(run("select", str(ws), "--fields", "id,short", "--format", "json"))
    assert items and all(set(d) == {"id", "short"} for d in items)
    r = run_fail("select", str(ws), "--fields", "id,bogus")
    assert "label, short, justification" in r.stderr
    md = run("select", str(ws), "--fields", "short")
    assert "**Short:**" in md and "**Justification:**" not in md and "## FND-0002" in md
    cl = json.loads((ws / "clusters.json").read_text())["findings"]
    want = {}
    for c in cl.values():
        for e in c["F"]:
            want[e] = want.get(e, 0) + 1
    assert json.loads(run("select", str(ws), "--count-by", "entity", "--format", "json")) == want
    assert "| F02 |" in run("select", str(ws), "--count-by", "entity")
    md = run("select", str(ws), "--group-by", "level")
    assert md.index("\n## L3") < md.index("### FND-0002")
    g = json.loads(run("select", str(ws), "--group-by", "level", "--format", "json"))
    assert {d["id"] for d in g["L3"]} == {"FND-0002"}
    r = _select_proc(ws, "--count-by", "tier", "--budget-chars", "5")
    assert "ignores --budget-chars" in r.stderr


def test_size_report_on_stderr(ws):
    r = _select_proc(ws)
    m = re.search(r"select: (\d+) findings, (\d+) chars", r.stderr)
    assert m and int(m.group(2)) == len(r.stdout)
