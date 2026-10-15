"""Engine tests on a small synthetic export (fictional event, no real data)."""
import json
import re
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
