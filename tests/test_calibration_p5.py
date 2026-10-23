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


# --- Task 5: nine-m-seed (P5-12). The split is what references/nine-m-map.json gives; R6's lost prototype split
# (110/95/72/59/38/27/14/12/9) is a sanity reference only, and the differences are in the Task 5 report.
NINE_M_PRIMARY = {"M1": 72, "M2": 13, "M3": 95, "M4": 40, "M5": 13, "M6": 130, "M7": 37, "M8": 9, "M9": 27}


@pytest.fixture(scope="module")
def hazira_seed(hazira_ws):
    run("nine-m-seed", str(hazira_ws))
    import json
    return json.loads((hazira_ws / "nine_m_seed.json").read_text(encoding="utf-8"))


def test_hazira_nine_m_all_mapped(hazira_seed):
    """Nanocodes mapped to an M: 436 of 436, 0 unmapped (rule: nine-m-seed; spec §7.7 item 3)."""
    assert len(hazira_seed["findings"]) == 436
    assert hazira_seed["unmapped"] == []
    assert all(v["m_primary"] for v in hazira_seed["findings"].values())


def test_hazira_nine_m_primary_split(hazira_seed):
    assert {m: p["findings"] for m, p in hazira_seed["profile"].items()} == NINE_M_PRIMARY
    assert sum(NINE_M_PRIMARY.values()) == 436


def test_m8_m9_reachable_by_keywords(hazira_ws):
    """§7.3: Material and Maintenance are under-coded, but the wording reaches them: at least 50 findings each carry
    an M8 keyword hit and an M9 one (label and short description)."""
    from pmlc_lib import ninem
    w = pmlc.load_ws(hazira_ws)
    mp = ninem.load_map()
    hits = {"M8": 0, "M9": 0}
    for f in w["findings"]:
        kw = ninem.keyword_ms(f, mp)
        for m in hits:
            hits[m] += m in kw
    assert hits["M8"] >= 50 and hits["M9"] >= 50, hits
