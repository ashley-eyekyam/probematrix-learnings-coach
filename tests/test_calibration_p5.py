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


def test_profile_counts(hazira_ws):
    """SVI 1.4 recurs 21 times; OIC 2.1 has 36 links out in causal_graph.json (Task 3)."""
    run("hfacs-profile", str(hazira_ws))
    prof = json.loads((hazira_ws / "hfacs_profile.json").read_text(encoding="utf-8"))
    assert {r["code"]: r["n"] for r in prof["recurrence"]}["SVI 1.4"] == 21
    assert {r["code"]: r["out"] for r in prof["feeds"]}["OIC 2.1"] == 36


# ----------------------------------------------------------------------------- Task 4: open-questions

def test_hazira_open_questions_numbers(hazira_ws):
    """Blank summary fields 21 of 30; 4 empty follow-up columns; absence 240 and hedged 193 are what the lexicons in
    references/open-questions.json give on `justification` (P5-7). The spec's 236 and 185 are superseded: R1 never
    recorded its word lists, so they cannot be reproduced."""
    run("open-questions", str(hazira_ws))
    oq = json.loads((hazira_ws / "open_questions.json").read_text(encoding="utf-8"))
    assert (len(oq["blank_summary_fields"]), oq["summary_fields"]) == (21, 30)
    assert len(oq["empty_follow_up_columns"]) == 4
    assert (len(oq["absence"]), len(oq["hedged"])) == (240, 193)
    assert 0 < len(json.loads(run("open-questions", str(hazira_ws), "--items"))) <= 30


# ----------------------------------------------------------------------------- Task 6: rec-review

def test_rec_review_bands(hazira_ws):
    """Task 6: RCA2 bands over the 44 Hazira recommendations (rule: references/rec-review.json)."""
    from pmlc_lib.rec_review import review
    reg = json.loads((SAMPLE / "outputs" / "learnings-register.json").read_text(encoding="utf-8"))
    assert review(reg)["bands"] == {"stronger": 24, "intermediate": 15, "weaker": 5, "unrated": 0}
