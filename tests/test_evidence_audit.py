"""evidence-audit (Phase 5, Task 2): the engine-computed evidence strength, the audit artefact, its table items and
the register check that holds a learning's evidence_strength to the engine's value."""
import copy
import json
import subprocess
import sys

import pytest

from test_pmlc import MINI_REG, PMLC, make_export, make_thin_export, run
from pmlc_lib.evidence_audit import audit, finding_strength, learning_strength
from pmlc_lib.workspace import load_ws


def _ev(**types):
    return {k: {"id": k, "type": t} for k, t in types.items()}


def test_strength_rules():
    ev = _ev(A="document", B="document", C="log_record")
    assert finding_strength({"evidence": []}, ev) == "inferred"
    assert finding_strength({"evidence": ["A"]}, ev) == "direct"
    assert finding_strength({"evidence": ["A", "B"]}, ev) == "direct"        # two items, one type
    assert finding_strength({"evidence": ["A", "C"]}, ev) == "corroborated"  # two items, two types
    assert finding_strength({"evidence": ["A", "A"]}, ev) == "direct"        # a repeated id is one item
    assert finding_strength({"evidence": ["ZZ"]}, ev) == "direct"            # an item the sheet does not list


def test_learning_strength_pools_cited_findings():
    w = {"findings": [{"id": "F1", "evidence": ["A"]}, {"id": "F2", "evidence": ["C"]}, {"id": "F3", "evidence": []}],
         "evidence": _ev(A="document", C="log_record")}
    assert learning_strength(["F1"], w) == "direct"
    assert learning_strength(["F1", "F2"], w) == "corroborated"
    assert learning_strength(["F3"], w) == "inferred"
    assert learning_strength(["F9"], w) == "inferred"


@pytest.fixture(scope="module")
def wsd(tmp_path_factory):
    d = tmp_path_factory.mktemp("ea")
    x = make_export(d)
    run("ingest", str(x), "--legacy-out", str(d / "ws"))
    run("classify", str(d / "ws"))
    return d / "ws"


def test_audit_shape_and_artefact(wsd):
    out = run("evidence-audit", str(wsd))
    p = wsd / "evidence_audit.json"
    first = p.read_bytes()
    d = json.loads(first)
    assert d["version"] == 1
    assert set(d) == {"version", "findings", "levels", "single_source", "document_only", "concentration",
                      "justification_only", "unknown_codes", "notes"}
    assert set(d["levels"]) == {"1", "2", "3", "4"}
    assert all(set(v) == {"strength", "sources", "types"} for v in d["findings"].values())
    assert "single-source" in out.lower() or "single" in out.lower()
    run("evidence-audit", str(wsd))
    assert p.read_bytes() == first                       # re-run: byte-identical


def test_audit_json_flag(wsd):
    d = json.loads(run("evidence-audit", str(wsd), "--json"))
    assert d["ok"] is True and "findings" in d["audit"]


@pytest.mark.parametrize("which", ["scorecard", "concentration", "levels"])
def test_table_items_have_row_cites(wsd, which):
    it = json.loads(run("evidence-audit", str(wsd), "--table-item", which))
    assert it["kind"] == "table"
    assert it["rows"] or which == "concentration"      # a small export has no item supporting 10 findings
    assert len(it["row_cites"]) == len(it["rows"])
    assert all(isinstance(c, list) for c in it["row_cites"])
    assert it["cites"] == sorted({x for c in it["row_cites"] for x in c})


def test_evidence_audit_thin_export(tmp_path):
    x = make_thin_export(tmp_path)
    run("ingest", str(x), "--legacy-out", str(tmp_path / "ws"))
    run("evidence-audit", str(tmp_path / "ws"))
    d = json.loads((tmp_path / "ws" / "evidence_audit.json").read_text())
    assert d["findings"] and all(v["strength"] == "inferred" for v in d["findings"].values())
    assert any("no evidence" in n.lower() for n in d["notes"])
    assert d["concentration"] == []
    for which in ("scorecard", "concentration", "levels"):
        run("evidence-audit", str(tmp_path / "ws"), "--table-item", which)   # exits 0 on a thin export


def test_unknown_codes_and_justification_only():
    w = {"findings": [{"id": "F1", "code": "SV 1.4", "level": 3, "evidence": ["A"], "justification": "",
                       "causal": "SV 1.4 enabled ZZ 9.9 and OR 2.2"},
                      {"id": "F2", "code": "OR 2.2", "level": 4, "evidence": [], "justification": "",
                       "causal": ""}],
         "evidence": _ev(A="witness_statement")}
    a = audit(w)
    assert a["unknown_codes"] == ["ZZ 9.9"]
    assert a["justification_only"] == ["F2"]
    assert a["levels"]["3"] == {"findings": 1, "single_source": 1, "document_only": 0, "witness": 1}
    assert a["levels"]["4"]["findings"] == 1 and a["levels"]["4"]["single_source"] == 0


def _reg(strength):
    reg = copy.deepcopy(MINI_REG)
    reg["entries"][0]["evidence_strength"] = strength
    return reg


def _check(ws, reg, tmp_path):
    p = tmp_path / "r.json"
    p.write_text(json.dumps(reg), encoding="utf-8")
    r = subprocess.run([sys.executable, str(PMLC), "check-register", str(ws), str(p), "--json"],
                       capture_output=True, text=True)
    return json.loads(r.stdout)["problems"]


def test_check_register_engine_strength(tmp_path):
    x = make_export(tmp_path)
    ws = tmp_path / "ws"
    run("ingest", str(x), "--legacy-out", str(ws))
    run("classify", str(ws))
    assert not [p for p in _check(ws, _reg("inferred"), tmp_path) if "computed by the engine" in p]  # no file: silent
    run("evidence-audit", str(ws))
    w = load_ws(ws)
    want = learning_strength(MINI_REG["entries"][0]["finding_ids"], w)
    bad = "inferred" if want != "inferred" else "corroborated"
    probs = [p for p in _check(ws, _reg(bad), tmp_path) if "computed by the engine" in p]
    assert probs == [f"LR-01: evidence_strength is computed by the engine ('{want}'); run evidence-audit and copy it"]
    assert not [p for p in _check(ws, _reg(want), tmp_path) if "computed by the engine" in p]
    reg = _reg(want)
    del reg["entries"][0]["evidence_strength"]                 # an absent value is not a mismatch
    assert not [p for p in _check(ws, reg, tmp_path) if "computed by the engine" in p]
