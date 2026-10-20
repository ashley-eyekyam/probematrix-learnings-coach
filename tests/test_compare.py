"""Comparator inventory, pmlc compare, select --in-evidence and check-pack comparator_refs (synthetic data only)."""
import copy
import json
import shutil
from pathlib import Path

import pytest

from test_pmlc import MINI_REG, ROOT, run, run_fail, ws  # noqa: F401
import pmlc  # noqa: E402
import pmlc_pack as pp  # noqa: E402
from test_pack import pack_with  # noqa: E402

FIX = Path(__file__).resolve().parent / "fixtures" / "comparator"


@pytest.fixture()
def cws(ws, tmp_path):  # noqa: F811
    d = tmp_path / "ws"
    shutil.copytree(ws, d)
    shutil.copy(FIX / "comparator.json", d / "comparator.json")
    shutil.copy(FIX / "comparison-map.json", d / "comparison-map.json")
    return d


@pytest.fixture()
def reg(tmp_path):
    r = copy.deepcopy(MINI_REG)
    r["entries"].append({**copy.deepcopy(r["entries"][0]), "lr_id": "LR-02", "owner_entity": "F09 Operations"})
    r["entries"].append({**copy.deepcopy(r["entries"][0]), "lr_id": "LR-03", "owner_entity": "F09 Operations"})
    p = tmp_path / "reg.json"
    p.write_text(json.dumps(r), encoding="utf-8")
    return p


def items(out):
    return json.loads(out)


def rows_of(its, first_col):
    return next(i["rows"] for i in its if i.get("kind") == "table" and i["columns"][0] == first_col)


def test_compare_counts_and_coverage(cws, reg):
    its = items(run("compare", str(cws), "--register", str(reg), "--json"))
    assert all(i["kind"] in ("table", "para") for i in its)
    inv = dict((r[0], r[1]) for r in rows_of(its, "Item type"))
    assert inv == {"observation": 1, "root_cause": 1, "recommendation": 3, "action": 0}
    cov = {r[0]: r[1:] for r in rows_of(its, "Direction")}
    # LR -> comparator: LR-01 yes, LR-02 partial, LR-03 none ; comparator -> LR: REC-01 yes, RC-01 partial,
    # REC-03 partial, REC-02 none (mapped none), OBS-01 unmapped (none)
    assert cov["Learnings against comparator items"] == [1, 1, 1]
    assert cov["Comparator items against learnings"] == [1, 2, 2]
    tiers = dict((r[0], r[1]) for r in rows_of(its, "Control tier"))
    assert tiers["engineering"] == 1 and tiers["training"] == 1 and tiers["administrative"] == 1
    cross = rows_of(its, "Comparator group")
    assert ["Maintenance", "F02", 2] in cross and ["Operations", "F09", 1] in cross


def test_compare_default_output_is_readable(cws, reg):
    out = run("compare", str(cws), "--register", str(reg))
    assert "Synthetic review panel report" in out and "|" in out


def test_compare_rejects_bad_ids(cws):
    c = json.loads((cws / "comparator.json").read_text())
    c["items"][0]["id"] = "OBS-1"
    c["items"].append(copy.deepcopy(c["items"][2]))
    (cws / "comparator.json").write_text(json.dumps(c))
    r = run_fail("compare", str(cws))
    assert "OBS-1" in r.stderr and "duplicate" in r.stderr.lower()


def test_compare_rejects_bad_mapping(cws):
    (cws / "comparison-map.json").write_text(json.dumps([{"lr_id": "LR-01", "ref": "REC-99", "match": "maybe"}]))
    r = run_fail("compare", str(cws))
    assert "REC-99" in r.stderr and "maybe" in r.stderr


def test_compare_rejects_type_prefix_mismatch(cws):
    c = json.loads((cws / "comparator.json").read_text())
    c["items"][0]["type"] = "recommendation"
    (cws / "comparator.json").write_text(json.dumps(c))
    assert "OBS-01" in run_fail("compare", str(cws)).stderr


def test_compare_client_safe_section_mismatch(cws, tmp_path):
    main = pack_with(pack="board-brief")
    main["sections"] = [{"id": "a", "heading": "A", "items": [{"kind": "para", "text": "t"}]},
                        {"id": "b", "heading": "B", "items": [{"kind": "para", "text": "t"}]}]
    same = copy.deepcopy(main)
    other = copy.deepcopy(main)
    other["sections"][1]["id"] = "c"
    for n, p in (("main", main), ("same", same), ("other", other)):
        (tmp_path / f"{n}.json").write_text(json.dumps(p))
    run("compare", str(cws), "--client-safe", str(tmp_path / "same.json"), "--main", str(tmp_path / "main.json"))
    r = run_fail("compare", str(cws), "--client-safe", str(tmp_path / "other.json"), "--main",
                 str(tmp_path / "main.json"))
    assert "section" in r.stderr and "c" in r.stderr
    assert "--main" in run_fail("compare", str(cws), "--client-safe", str(tmp_path / "same.json")).stderr


def test_compare_own_action_plan_kind(cws, reg):
    c = json.loads((cws / "comparator.json").read_text())
    c["source"]["kind"] = "own-action-plan"
    (cws / "comparator.json").write_text(json.dumps(c))
    out = run("compare", str(cws), "--register", str(reg), "--json")
    assert "against the organisation's action plan" in out
    assert "against the organisation's action plan" not in run(
        "compare", str(cws), "--register", str(reg), "--comparator", str(FIX / "comparator.json"), "--json")


def test_select_in_evidence_finds_specific_reference(ws):  # noqa: F811
    assert "FND-0001" not in run("select", str(ws), "--text", "no leak test recorded")
    out = run("select", str(ws), "--text", "no leak test recorded", "--in-evidence", "--brief")
    assert "FND-0001" in out and "FND-0002" not in out
    assert "FND-0003" not in run("select", str(ws), "--text", "PO list", "--brief")
    out = run("select", str(ws), "--text", "PO list", "--in-evidence", "--brief")   # evidence description
    assert "FND-0003" in out


def test_select_in_evidence_needs_text(ws):  # noqa: F811
    assert "--text" in run_fail("select", str(ws), "--in-evidence").stderr


def test_check_pack_comparator_refs(cws, ws):  # noqa: F811
    w = pmlc.load_ws(cws)
    p = pack_with({"kind": "para", "text": "t", "cites": ["FND-0002"], "comparator_refs": ["REC-01"]})
    r = pp.check_pack(p, w)
    assert r.problems == []
    p["sections"][0]["items"][0]["comparator_refs"] = ["REC-77"]
    assert any("REC-77" in x and "comparator_refs" in x for x in pp.check_pack(p, w).problems)
    p["sections"][0]["items"][0]["comparator_refs"] = ["bogus"]
    assert any("comparator_refs" in x for x in pp.check_pack(p, w).problems)
    # no comparator.json: warning, not a problem
    r = pp.check_pack(pack_with({"kind": "para", "text": "t", "cites": ["FND-0002"], "comparator_refs": ["REC-77"]}),
                      pmlc.load_ws(ws))
    assert r.problems == [] and any("REC-77" in x for x in r.warnings)


def test_compare_tables_pass_check_pack(cws, reg, tmp_path):
    its = items(run("compare", str(cws), "--register", str(reg), "--json"))
    p = pack_with(*its)
    f = tmp_path / "p.json"
    f.write_text(json.dumps(p))
    run("check-pack", str(cws), str(f))


MALFORMED = {
    "not-json": "{not json",
    "list": "[]",
    "items-not-list": '{"source": {}, "items": 5}',
    "no-id": '{"items": [{"type": "observation"}]}',
    "bad-id": '{"items": [{"id": "X-1"}]}',
    "duplicate-id": '{"items": [{"id": "REC-01"}, {"id": "REC-01"}]}',
    "non-dict-item": '{"items": ["REC-01", 3, null]}',
}


@pytest.mark.parametrize("name", sorted(MALFORMED))
def test_malformed_comparator_never_breaks_the_workspace(ws, tmp_path, name):  # noqa: F811
    d = tmp_path / "ws"
    shutil.copytree(ws, d)
    pack = pack_with({"kind": "para", "text": "t", "cites": ["FND-0002"], "comparator_refs": ["REC-01"]})
    pf = tmp_path / "p.json"
    pf.write_text(json.dumps(pack))
    base = run("check-pack", str(d), str(pf))
    run("status", str(d))
    (d / "comparator.json").write_text(MALFORMED[name], encoding="utf-8")
    run("status", str(d))
    run("select", str(d), "--max", "1")
    import subprocess
    import sys
    r = subprocess.run([sys.executable, str(ROOT / "skills" / "learnings-coach" / "scripts" / "pmlc.py"),
                        "check-pack", str(d), str(pf)], capture_output=True, text=True)
    out = r.stdout + r.stderr
    assert "Traceback" not in out
    assert "no comparator.json in the workspace" in base
    if name in ("not-json", "list", "items-not-list"):
        assert r.returncode == 0   # same exit code as with no comparator
        assert "comparator.json is not valid" in out and "no comparator.json in the workspace" not in out
        assert "comparator_refs not verified" in out
    elif name == "duplicate-id":
        assert r.returncode == 0
    else:   # a readable inventory that lacks REC-01: a clean problem line, not a crash
        assert r.returncode == 1 and "REC-01 is not in comparator.json" in out
