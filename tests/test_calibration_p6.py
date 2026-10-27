"""Phase 6 Hazira calibration (P3-20 still in force): the numbers the Phase 6 engine commands give on the public
Hazira sample, each with its rule (plan, Global Constraints table). Task 1 creates the file and the workspace
fixture; each engine task (2 to 6) appends its own numbers. A number that moves needs a ruling."""
import json

import pytest

from test_pmlc import ROOT, run
import pmlc  # noqa: E402

pytest.importorskip("openpyxl")
SAMPLE = ROOT / "samples" / "2020-09-24-hazira-gas-release-fire"
EXPORT = SAMPLE / "2020-09-24-hazira-gas-release-fire_probematrix-findings.xlsx"
REGISTER = SAMPLE / "outputs" / "learnings-register.json"


@pytest.fixture(scope="module")
def hazira_ws(tmp_path_factory):
    """The Hazira workspace, built once per module with the India process-site overlay (as test_calibration_p5)."""
    root = tmp_path_factory.mktemp("hazira-p6")
    run("setup", str(EXPORT), "--slug", "hazira-gas-release-fire", "--date", "2020-09-24", "--root", str(root),
        "--overlay", "india-process-site")
    return root / "pmlc-runs" / "2020-09-24-hazira-gas-release-fire" / "workspace"


def test_hazira_workspace_and_register(hazira_ws):
    w = pmlc.load_ws(hazira_ws)
    assert len(w["findings"]) == 436
    assert len(w["evidence"]) == 46
    reg = json.loads(REGISTER.read_text(encoding="utf-8"))
    assert len(reg["entries"]) == 25


# ----------------------------------------------------------------------------- Task 2: alert-grade (P6-3)

def test_hazira_alert_grade_numbers():
    """priority-1 learnings: register priority == 1 (11 of 25). Suggested grades: the P6-3 rule applied to each of the
    25 learnings on its own (priority 1 with other sites or industry-wide -> alert; priority 1 at the same site, or
    priority 2 -> notice; otherwise information), whatever urgency the register gives. The default choice is the top 3
    priority-1 rows by transferability, then evidence strength, then LR-ID."""
    from collections import Counter
    from pmlc_lib import alert
    entries = json.loads(REGISTER.read_text(encoding="utf-8"))["entries"]
    assert sum(1 for e in entries if e.get("priority") == 1) == 11
    assert Counter(alert.suggest_grade(e) for e in entries) == {"alert": 11, "notice": 12, "information": 2}
    assert alert.default_choice(entries) == ["LR-01", "LR-02", "LR-03"]


def test_effect_plan_rows(hazira_ws):
    """Effectiveness schedule rows: 11 priority-1 learnings x 5 checks + 14 others x 3 = 97 (P6-8)."""
    d = json.loads(run("effect-plan", str(hazira_ws), "--register", str(REGISTER), "--json"))
    assert len(d["rows"]) == 97
    assert len(d["learnings"]) == 25
    assert sum(1 for r in d["rows"] if r["priority"] == 1) == 55
    assert d["notes"] == []


# ----------------------------------------------------------------------------- Task 5: accimap (P6-7)

def test_hazira_accimap_levels_and_gaps(hazira_ws):
    run("accimap", str(hazira_ws))
    d = json.loads((hazira_ws / "accimap.json").read_text(encoding="utf-8"))
    assert {k: len(v["findings"]) for k, v in d["levels"].items()} == {
        "1": 0, "2": 0, "3": 143, "4": 166, "5": 76, "6": 51}
    assert d["gaps"] == [1, 2]
    assert len(d["placements"]) == 436
    assert d["levels"]["3"]["inferred"] is True and d["levels"]["4"]["inferred"] is False
    assert sum(1 for p in d["placements"].values() if p.get("tag") == "contractor") == 7
    it = json.loads(run("accimap", str(hazira_ws), "--graph-item"))
    assert it["kind"] == "graph" and it["edges"] and it["cites"]
    assert sum(1 for n in it["nodes"] if n["id"].startswith("L")) >= 6
