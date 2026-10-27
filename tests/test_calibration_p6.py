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


def test_hazira_transferable_learnings():
    """Task 3: transferable learnings = 25, by the rule `transferability` in `other sites`, `industry-wide` (the
    learnings a could-it-happen-here pack draws its self-checks from)."""
    reg = json.loads(REGISTER.read_text(encoding="utf-8"))
    assert sum(1 for e in reg["entries"] if e.get("transferability") in ("other sites", "industry-wide")) == 25


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
