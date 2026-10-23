"""Phase 5 Hazira calibration (P3-20 still in force): the numbers the Phase 5 engine commands give on the public
Hazira sample, each with its rule (plan, Global Constraints table). Task 1 creates the file and the workspace
fixture; each engine task appends its own numbers. A number that moves needs a ruling."""
import json

import pytest

from test_pmlc import ROOT, run
import pmlc  # noqa: E402

pytest.importorskip("openpyxl")
SAMPLE = ROOT / "samples" / "2020-09-24-hazira-gas-release-fire"
EXPORT = SAMPLE / "2020-09-24-hazira-gas-release-fire_probematrix-findings.xlsx"


@pytest.fixture(scope="module")
def hazira_ws(tmp_path_factory):
    """The Hazira workspace, built once per module with the India process-site overlay."""
    root = tmp_path_factory.mktemp("hazira-p5")
    run("setup", str(EXPORT), "--slug", "hazira-gas-release-fire", "--date", "2020-09-24", "--root", str(root),
        "--overlay", "india-process-site")
    return root / "pmlc-runs" / "2020-09-24-hazira-gas-release-fire" / "workspace"


def test_hazira_436_findings_46_evidence(hazira_ws):
    w = pmlc.load_ws(hazira_ws)
    assert len(w["findings"]) == 436
    assert len(w["evidence"]) == 46


def test_evidence_counts(hazira_ws):
    """Task 2: single-source 203, document-only 195, level-3 167 with a witness 11, EVD-8645 supports 67."""
    run("evidence-audit", str(hazira_ws))
    w = pmlc.load_ws(hazira_ws)
    ev, F = w["evidence"], w["findings"]
    assert sum(len(f["evidence"]) == 1 for f in F) == 203
    assert sum(bool(f["evidence"]) and all(ev[e]["type"] == "document" for e in f["evidence"]) for f in F) == 195
    l3 = [f for f in F if f["level"] == 3]
    assert len(l3) == 167
    assert sum(any(ev[e]["type"] == "witness_statement" for e in f["evidence"]) for f in l3) == 11
    assert sum("EVD-8645" in f["evidence"] for f in F) == 67
    a = json.loads((hazira_ws / "evidence_audit.json").read_text(encoding="utf-8"))
    # Single-source is the raw Linked Evidence column rule (len == 1), as the plan and spec state: 203.
    assert len(a["single_source"]) == 203 and len(a["document_only"]) == 195
    assert a["levels"]["3"]["findings"] == 167 and a["levels"]["3"]["witness"] == 11
    reg = run("check-register", str(hazira_ws), str(SAMPLE / "outputs" / "learnings-register.json"))
    assert "0 problem(s)" in reg, reg
    top = a["concentration"][0]
    assert top["evidence"] == "EVD-8645" and top["findings"] == 67
