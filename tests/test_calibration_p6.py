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


# ----------------------------------------------------------------------------- Task 4: wai-wad (P6-6)

def test_wai_wad_hazira_numbers(hazira_ws):
    """Codes with both document and work-as-done evidence 68 of 94; findings with both 92; findings with any
    work-as-done evidence 210; counterfactual findings 337 by the P6-6 list in references/learning-team.json
    (this supersedes the spec's 353, whose word list was never recorded)."""
    run("wai-wad", str(hazira_ws))
    c = json.loads((hazira_ws / "wai_wad.json").read_text(encoding="utf-8"))["counts"]
    assert c == {"codes": 94, "codes_both": 68, "findings_both": 92, "findings_wad": 210, "counterfactual": 337}


def test_wai_wad_hazira_prompts_are_clean(hazira_ws):
    """Every Hazira prompt is a question, cites one finding, and repeats none of the export's counterfactual words."""
    from pmlc_lib import waiwad
    items = json.loads(run("wai-wad", str(hazira_ws), "--items", "prompts"))
    assert len(items) == 30
    for it in items:
        assert it["kind"] == "question" and len(it["cites"]) == 1
        assert not waiwad.counterfactual_hits(it["question"])


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
