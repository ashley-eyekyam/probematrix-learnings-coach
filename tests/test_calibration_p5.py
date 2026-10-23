"""Phase 5 Hazira calibration (P3-20 still in force): the numbers the Phase 5 engine commands give on the public
Hazira sample, each with its rule (plan, Global Constraints table). Task 1 creates the file and the workspace
fixture; each engine task appends its own numbers. A number that moves needs a ruling."""
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


# ----------------------------------------------------------------------------- Task 7: missed opportunities, event day

def test_hazira_missed_opportunity_sets(hazira_ws):
    import json
    import re
    w = pmlc.load_ws(hazira_ws)
    prior = [f["id"] for f in w["findings"] if re.search(r"\brecommend", f["justification"], re.I)]
    svf = [f["id"] for f in w["findings"] if f["code"].split()[0] == "SVF"]
    assert (len(prior), len(svf)) == (107, 40)
    run("missed-opportunities", str(hazira_ws))
    m = json.loads((hazira_ws / "missed_opportunities.json").read_text(encoding="utf-8"))
    assert (len(m["prior_recommendation"]), len(m["failure_to_correct"])) == (107, 40)
    assert sorted(prior) == m["prior_recommendation"] and sorted(svf) == m["failure_to_correct"]
    assert m["dated"] and all(d["date"] < "2020-09-24" for d in m["dated"])


def test_hazira_event_day_52_stamps_26_times(hazira_ws):
    import json
    import re
    narrative = pmlc.load_ws(hazira_ws)["incident"]["narrative"]
    stamps = [f"{int(m.group(1)):02d}:{m.group(2)}"
              for m in re.finditer(r"\b([01]?\d|2[0-3])[:.]([0-5]\d)\b", narrative)]
    assert (len(stamps), len(set(stamps))) == (52, 26)
    it = json.loads(run("timeline-item", str(hazira_ws), "--event-day"))
    times = [e["time"] for e in it["events"]]
    assert len(times) == 26 and times == sorted(set(stamps))
    assert all(e["date"] == "2020-09-24" and e["knowable_then"] is True for e in it["events"])
    run("timeline", str(hazira_ws), "--on", "incident")
    assert len(json.loads((hazira_ws / "timeline_event_day.json").read_text(encoding="utf-8"))) == 29
