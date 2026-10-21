"""Organisation-filled templates, their loaders and export-actions (Phase 3, Task 9)."""
import copy
import csv
import json
import subprocess
import sys

import pytest

from test_pmlc import MINI_REG, PMLC, make_export, run
from pmlc_lib.pack.schema import KINDS
from pmlc_lib.templates import OrgFileError, load_adoption, load_distribution, load_verification

PACK = json.loads(json.dumps({
    "pack": "board-brief", "schema": 1, "title": "Board Brief: synthetic", "audience": "Board",
    "status": "Learning purposes: not a statutory document",
    "bottom_line": [{"text": "Test before service.", "cites": ["FND-0002"]}],
    "sections": [{"id": "actions", "heading": "Actions", "items": [
        {"kind": "recommendation", "change": "Add a hold point", "indicator": "Share tested", "hoc_tier":
         "Administrative (procedure)", "cites": ["FND-0001", "EVD-0001"], "evidence_strength": "direct",
         "owner": "Someone", "by_when": "2030-01-01"},
        {"kind": "decision", "decision": "Fund the interlock", "cites": ["FND-0003"]},
        {"kind": "indicator", "id": "ind-x", "name": "Restarts tested", "measure": "Percent", "cites": ["FND-0001"]},
        {"kind": "para", "text": "Not an action."}]}]}))


@pytest.fixture()
def rund(tmp_path):
    d = tmp_path / "exp"
    d.mkdir()
    x = make_export(d)
    run("ingest", str(x), "--slug", "test-pump", "--date", "2024-03-12")
    ws = d / "pmlc-runs" / "2024-03-12-test-pump" / "workspace"
    out = ws.parent / "outputs"
    out.mkdir(exist_ok=True)
    (out / "learnings-register.json").write_text(json.dumps(MINI_REG), encoding="utf-8")
    (out / "board-brief.json").write_text(json.dumps(PACK), encoding="utf-8")
    return ws


def cli(*args):
    return subprocess.run([sys.executable, str(PMLC), *args], capture_output=True, text=True)


def test_templates_write_blank_org_columns(rund):
    out = rund.parent / "outputs"
    for m in ("adoption", "distribution", "verification"):
        assert cli("templates", str(rund), m).returncode == 0
    rows = list(csv.DictReader(open(out / "adoption.csv", encoding="utf-8", newline="")))
    assert len(rows) == 1 and rows[0]["lr_id"] == "LR-01" and rows[0]["title"]
    assert all(rows[0][c] == "" for c in ("response", "reason", "owning_role", "target_window"))
    dist = list(csv.DictReader(open(out / "distribution.csv", encoding="utf-8", newline="")))
    assert [r["pack"] for r in dist] == ["board-brief"] and dist[0]["audience"] == "Board"
    lines = (out / "verification.jsonl").read_text(encoding="utf-8").splitlines()
    assert [json.loads(x) for x in lines] == [{"lr_id": "LR-01", "check_date": None, "level": None,
                                               "evidence": None, "assessed_by_role": None}]
    assert load_adoption(rund)[0]["lr_id"] == "LR-01" and load_verification(rund)[0]["level"] is None
    assert load_distribution(rund.parent)[0]["pack"] == "board-brief"


def test_templates_need_register_and_refuse_overwrite(rund):
    out = rund.parent / "outputs"
    assert cli("templates", str(rund), "adoption").returncode == 0
    before = (out / "adoption.csv").read_bytes()
    r = cli("templates", str(rund), "adoption")
    assert r.returncode == 1
    assert "already exists and may hold your organisation's entries; move it or pass a new --out" in r.stderr
    assert (out / "adoption.csv").read_bytes() == before
    (out / "learnings-register.json").unlink()
    r = cli("templates", str(rund), "verification")
    assert r.returncode == 1 and "Learnings Register" in r.stderr
    assert load_adoption(rund.parent / "nowhere") == []


def test_org_files_read_excel_saved_csv(rund):
    out = rund.parent / "outputs"
    text = ("﻿title,extra,lr_id,response,target_window\r\nFirst,x,LR-01,Accepted,Q1\r\n"
            "Second,y,LR-02,,\r\n,,,,\r\n,,,,\r\n")
    (out / "adoption.csv").write_bytes(text.encode("utf-8"))
    rows = load_adoption(rund)
    assert [r["lr_id"] for r in rows] == ["LR-01", "LR-02"]
    assert rows[0]["response"] == "accepted" and rows[0]["target_window"] == "Q1" and rows[0]["extra"] == "x"
    assert rows[1]["reason"] == "" and rows[1]["response"] == ""
    (out / "distribution.csv").write_text("pack,audience,contractors_included\nb,Board,YES\n", encoding="utf-8")
    assert load_distribution(rund)[0]["contractors_included"] == "yes"


def test_org_files_bad_value_named_by_row(rund):
    out = rund.parent / "outputs"
    (out / "adoption.csv").write_text("lr_id,title,response\nLR-01,a,accepted\nLR-02,b,maybe\n", encoding="utf-8")
    with pytest.raises(OrgFileError, match=r"adoption\.csv row 3: response"):
        load_adoption(rund)
    (out / "verification.jsonl").write_text('{"lr_id": "LR-01", "level": "known"}\n', encoding="utf-8")
    with pytest.raises(OrgFileError, match=r"verification\.jsonl line 1: level"):
        load_verification(rund)
    (out / "verification.jsonl").write_text('{"lr_id": "LR-01"\n', encoding="utf-8")
    with pytest.raises(OrgFileError, match="not valid JSON"):
        load_verification(rund)
    (out / "verification.jsonl").write_text('[1]\n\n{"level": null}\n', encoding="utf-8")
    with pytest.raises(OrgFileError, match="JSON object"):
        load_verification(rund)
    (out / "verification.jsonl").write_text('{"level": null}\n', encoding="utf-8")
    with pytest.raises(OrgFileError, match="lr_id is required"):
        load_verification(rund)
    (out / "distribution.csv").write_text("pack,contractors_included\nb,perhaps\n", encoding="utf-8")
    with pytest.raises(OrgFileError, match=r"distribution\.csv row 2: contractors_included"):
        load_distribution(rund)


def test_org_files_keep_good_rows_and_report_all(rund):
    """M-4: every row is read first; one OrgFileError names every bad row and carries the good rows."""
    out = rund.parent / "outputs"
    (out / "adoption.csv").write_text("lr_id,title,response\nLR-01,a,maybe\nLR-02,b,Accepted\nLR-03,c,perhaps\n"
                                      "LR-04,d,\n", encoding="utf-8")
    with pytest.raises(OrgFileError) as ei:
        load_adoption(rund)
    e = ei.value
    assert len(e.problems) == 2
    assert "adoption.csv row 2: response 'maybe'" in str(e) and "adoption.csv row 4: response 'perhaps'" in str(e)
    assert [r["lr_id"] for r in e.rows] == ["LR-02", "LR-04"] and e.rows[0]["response"] == "accepted"
    assert isinstance(e.rows, list)
    (out / "distribution.csv").write_text("pack,contractors_included\nb,Y\nc,n\nd,perhaps\ne,\nf,sometimes\n",
                                          encoding="utf-8")
    with pytest.raises(OrgFileError) as ei:
        load_distribution(rund)
    e = ei.value
    assert len(e.problems) == 2 and "row 4" in str(e) and "row 6" in str(e)
    assert [(r["pack"], r["contractors_included"]) for r in e.rows] == [("b", "yes"), ("c", "no"), ("e", "")]
    (out / "distribution.csv").write_text("pack,contractors_included\nb,y\nc,N\n", encoding="utf-8")
    assert [r["contractors_included"] for r in load_distribution(rund)] == ["yes", "no"]
    (out / "verification.jsonl").write_text('{"lr_id": "LR-01", "level": "known"}\n{"lr_id": "LR-02", "level": '
                                            '"Applied"}\nnot json\n[1]\n{"level": null}\n{"lr_id": "LR-03"}\n',
                                            encoding="utf-8")
    with pytest.raises(OrgFileError) as ei:
        load_verification(rund)
    e = ei.value
    assert len(e.problems) == 4
    for n in (1, 3, 4, 5):
        assert f"verification.jsonl line {n}:" in str(e)
    assert [(r["lr_id"], r["level"]) for r in e.rows] == [("LR-02", "applied"), ("LR-03", None)]

def test_export_actions_ids_and_blank_owner(rund):
    assert cli("export-actions", str(rund)).returncode == 0
    out = rund.parent / "outputs"
    rows = json.loads((out / "actions.json").read_text(encoding="utf-8"))
    csv_rows = list(csv.DictReader(open(out / "actions.csv", encoding="utf-8", newline="")))
    assert len(rows) == len(csv_rows) == 5  # 3 pack items + 2 register recommendations
    ids = [r["id"] for r in rows]
    slug = "2024-03-12-test-pump"
    assert ids == [f"{slug}/board-brief/actions-1", f"{slug}/board-brief/actions-2", f"{slug}/board-brief/ind-x",
                   f"{slug}/register/LR-01/R1", f"{slug}/register/LR-01/R2"]
    for r in rows:
        assert all(r[c] == "" for c in ("owner", "due", "status", "capa_ref", "effectiveness_check"))
    assert (out / "actions.csv").read_bytes().startswith(b"id,") and b"\r\n" in (out / "actions.csv").read_bytes()
    assert rows[0]["evidence_strength"] == "direct" and rows[0]["cites"] == ["FND-0001", "EVD-0001"]
    assert rows[1]["change"] == "Fund the interlock"
    assert rows[3]["lr_id"] == "LR-01" and rows[3]["indicator"] == "Share of restarts with a test record"


def test_export_actions_round_trip(rund, tmp_path):
    d = tmp_path / "elsewhere"
    assert cli("export-actions", str(rund), "--packs", "board-brief", "--out-dir", str(d)).returncode == 0
    rows = json.loads((d / "actions.json").read_text(encoding="utf-8"))
    back = list(csv.DictReader(open(d / "actions.csv", encoding="utf-8", newline="")))
    flat = [{k: "; ".join(v) if isinstance(v, list) else v for k, v in r.items()} for r in rows]
    assert back == flat and len(rows) == 5  # the default register's two recommendations are added


def test_export_actions_profile_rename_and_unverified_warning(rund, tmp_path):
    r = cli("export-actions", str(rund), "--profile", "enablon")
    assert r.returncode == 0
    assert ("profile 'enablon' is an unverified mapping: check the column names against your system before "
            "importing") in r.stderr
    head = (rund.parent / "outputs" / "actions.csv").read_text(encoding="utf-8").splitlines()[0]
    assert head != "id,lr_id" and "Action Owner" in head and "owner" not in head.split(",")
    g = cli("export-actions", str(rund), "--out-dir", str(tmp_path / "generic"))
    assert g.stderr == ""


def test_export_actions_names_guard(rund, tmp_path):
    pk = copy.deepcopy(PACK)
    pk["sections"][0]["items"][0]["change"] = "Ask Zanthor Quillfeather to add a hold point"
    (rund.parent / "outputs" / "board-brief.json").write_text(json.dumps(pk), encoding="utf-8")
    names = tmp_path / "names.txt"
    names.write_text("Zanthor Quillfeather\n", encoding="utf-8")
    r = cli("export-actions", str(rund), "--names", str(names))
    assert r.returncode == 1 and "nothing written" in r.stderr
    assert not (rund.parent / "outputs" / "actions.csv").exists()
    assert not (rund.parent / "outputs" / "actions.json").exists()


def test_export_actions_missing_pack_and_register(rund):
    assert cli("export-actions", str(rund), "--packs", "nope").returncode == 1
    assert cli("export-actions", str(rund), "--register", "nope.json").returncode == 1


def test_export_actions_register_barrier_and_evidence(rund):
    reg = copy.deepcopy(MINI_REG)
    e = reg["entries"][0]
    e["barrier"] = "Entry barrier"
    e["evidence_strength"] = "corroborated"
    e["recommendations"][0]["level_barrier"] = "L3 / return-to-service check"
    e["recommendations"][0]["evidence_strength"] = "direct"
    (rund.parent / "outputs" / "learnings-register.json").write_text(json.dumps(reg), encoding="utf-8")
    assert cli("export-actions", str(rund)).returncode == 0
    rows = json.loads((rund.parent / "outputs" / "actions.json").read_text(encoding="utf-8"))
    r1, r2 = rows[-2], rows[-1]
    assert (r1["barrier"], r1["evidence_strength"]) == ("L3 / return-to-service check", "direct")
    assert (r2["barrier"], r2["evidence_strength"]) == ("Entry barrier", "corroborated")


def test_export_actions_neutralises_formula_cells(rund):
    pk = copy.deepcopy(PACK)
    pk["sections"][0]["items"][0]["change"] = "=HYPERLINK(\"http://x\")"
    pk["sections"][0]["items"][1]["decision"] = "-2+3"
    (rund.parent / "outputs" / "board-brief.json").write_text(json.dumps(pk), encoding="utf-8")
    assert cli("export-actions", str(rund)).returncode == 0
    out = rund.parent / "outputs"
    back = list(csv.DictReader(open(out / "actions.csv", encoding="utf-8", newline="")))
    assert back[0]["change"] == "'=HYPERLINK(\"http://x\")" and back[1]["change"] == "'-2+3"
    rows = json.loads((out / "actions.json").read_text(encoding="utf-8"))
    assert rows[0]["change"] == "=HYPERLINK(\"http://x\")"


def test_export_actions_rejects_non_pack_and_accepts_co_owner(rund, tmp_path):
    bad = tmp_path / "other.json"
    bad.write_text('{"entries": []}', encoding="utf-8")
    r = cli("export-actions", str(rund), "--packs", str(bad))
    assert r.returncode == 1 and "not a learning pack" in r.stderr and "Traceback" not in r.stderr
    bad.write_text("nonsense", encoding="utf-8")
    assert "Traceback" not in cli("export-actions", str(rund), "--packs", str(bad)).stderr
    assert "co_owner" in KINDS["recommendation"]["opt"]
    pk = copy.deepcopy(PACK)
    pk["sections"][0]["items"][0]["co_owner"] = "Maintenance Manager"
    p = tmp_path / "pk.json"
    p.write_text(json.dumps(pk), encoding="utf-8")
    assert "unknown field" not in cli("check-pack", str(rund), str(p)).stdout.lower()


def test_export_actions_refuses_overwrite(rund, tmp_path):
    """I-4 (ruling X38): the actions files are the organisation's to fill in, so a second run never overwrites them."""
    out = rund.parent / "outputs"
    assert cli("export-actions", str(rund)).returncode == 0
    filled = (out / "actions.csv").read_bytes().replace(b",,,,,", b",Maintenance Manager,2030-01-01,,,", 1)
    (out / "actions.csv").write_bytes(filled)
    before = {n: (out / n).read_bytes() for n in ("actions.csv", "actions.json")}
    r = cli("export-actions", str(rund))
    assert r.returncode == 1 and "Traceback" not in r.stderr
    assert (f"{out / 'actions.csv'} already exists and may hold your organisation's entries; move it or pass a new "
            "--out-dir") in r.stderr
    assert {n: (out / n).read_bytes() for n in before} == before
    (out / "actions.csv").unlink()                         # the JSON alone is refused too
    r = cli("export-actions", str(rund))
    assert r.returncode == 1 and f"{out / 'actions.json'} already exists" in r.stderr
    assert not (out / "actions.csv").exists() and (out / "actions.json").read_bytes() == before["actions.json"]
    assert cli("export-actions", str(rund), "--out-dir", str(tmp_path / "new")).returncode == 0
    assert (tmp_path / "new" / "actions.csv").is_file()
