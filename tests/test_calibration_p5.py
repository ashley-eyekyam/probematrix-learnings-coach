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


# ----------------------------------------------------------------------------- Task 3: hfacs-profile

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


def test_risk_coded_findings_68(hazira_ws):
    """Task 8: findings whose code name contains "risk" (six codes) = 68."""
    w = pmlc.load_ws(hazira_ws)
    hits = [f for f in w["findings"] if "risk" in f["name"].lower()]
    assert len(hits) == 68
    assert len({f["code"].split()[0] for f in hits}) == 6


# ----------------------------------------------------------------------------- Task 7: missed opportunities, event day

def test_hazira_missed_opportunity_sets(hazira_ws):
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
    import re
    narrative = pmlc.load_ws(hazira_ws)["incident"]["narrative"]
    stamps = [f"{int(m.group(1)):02d}:{m.group(2)}"
              for m in re.finditer(r"\b([01]?\d|2[0-3])[:.]([0-5]\d)\b", narrative)]
    assert (len(stamps), len(set(stamps))) == (52, 26)
    it = json.loads(run("timeline-item", str(hazira_ws), "--event-day"))
    times = [e["time"] for e in it["events"]]
    assert len(times) == 26 and sorted(times) == sorted(set(stamps))
    assert [(e["date"], e["time"]) for e in it["events"]][:2] == [("2020-09-23", "20:00"), ("2020-09-24", "02:11")]
    assert all(e["date"] == "2020-09-24" for e in it["events"][1:])
    assert all(e["knowable_then"] is True for e in it["events"])
    run("timeline", str(hazira_ws), "--on", "incident")
    assert len(json.loads((hazira_ws / "timeline_event_day.json").read_text(encoding="utf-8"))) == 29


# ----------------------------------------------------------------------------- Task 20: engineering alarms-automation

def test_hazira_pte_findings_48(hazira_ws):
    """Task 20: the alarms-automation section gathers with select --prefix PTE: 48 findings (prefix PTE)."""
    w = pmlc.load_ws(hazira_ws)
    assert sum(f["code"].split()[0] == "PTE" for f in w["findings"]) == 48
    assert len(json.loads(run("select", str(hazira_ws), "--prefix", "PTE", "--json"))) == 48
