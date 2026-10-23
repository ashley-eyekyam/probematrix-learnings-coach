"""rec-review: strength bands, level match, loops, SMART gaps, 9M spread (synthetic data; Hazira in the calibration)."""
import json

import pytest

from test_calibration_p5 import hazira_ws  # noqa: F401
from test_pmlc import MINI_REG, run, run_fail, ws  # noqa: F401
import pmlc  # noqa: E402


def rec(what="Fit an interlock that blocks pressurisation without a signed test record", hoc="engineering",
        ind="Share of restarts with a test record", basis="EVD-0001"):
    return {"what": what, "hoc_tier": hoc, "leading_indicator": ind, "evidence_basis": basis}


@pytest.mark.parametrize("hoc,what,expected", [
    ("elimination", "Remove the legacy flange from service entirely", "stronger"),
    ("substitution", "Replace the solvent with a water-based product", "stronger"),
    ("engineering", "Fit an interlock on the test record", "stronger"),
    ("administrative", "Add a second isolation authority role to the shift roster", "intermediate"),
    ("administrative", "Update the procedure for seal replacement", "weaker"),
    ("administrative", "Issue a policy on spare parts", "weaker"),
    ("administrative", "Send a reminder to all crews", "weaker"),
    ("administrative", "Circulate a memo on gasket types", "weaker"),
    ("administrative", "Add a warning to the work order template", "weaker"),
    ("administrative", "Put a sign on the flange", "weaker"),
    ("administrative", "Post a poster in the workshop", "weaker"),
    ("administrative", "Add a double-check by a second technician", "weaker"),
    ("administrative", "Hold a re-brief at shift start", "weaker"),
    ("training", "Train every technician on seal selection", "weaker"),
    ("ppe", "Issue vapour-rated masks", "weaker"),
    ("", "Something unclear", "unrated"),
])
def test_bands(hoc, what, expected):
    assert pmlc.band({"what": what, "hoc_tier": hoc}) == expected


def test_signal_is_no_sign_cue():
    assert pmlc.band({"what": "Add a second flame signal to the panel", "hoc_tier": "administrative"}) == "intermediate"


def reg_with(*entries):
    return {"title": "t", "entries": list(entries)}


def lr(n, level, recs, **kw):
    return {"lr_id": f"LR-{n:02d}", "hfacs_level": level, "finding_ids": ["FND-0001"], "recommendations": recs, **kw}


def test_level_match_flag():
    r = pmlc.review(reg_with(
        lr(1, "L4 Organizational Influences", [rec("Train all technicians on the new standard of work", "training")]),
        lr(2, "L4 Resource Management", [rec()]),
        lr(3, "L1 Unsafe Acts", [rec("Train all technicians on the new standard of work", "training")]),
        lr(4, "L3 Inadequate Supervision", [rec("Add a second isolation authority role to the roster", "administrative")])))
    c = {x["lr"]: x for x in r["causes"]}
    assert c["LR-01"]["flag"] == "weak fix for a deep cause" and not c["LR-01"]["level_match"]
    assert c["LR-01"]["levels"] == [4] and c["LR-01"]["strongest_band"] == "weaker"
    assert c["LR-02"]["level_match"] and c["LR-02"]["flag"] == ""
    assert c["LR-03"]["level_match"]            # a level-1 cause is not a deep cause
    assert c["LR-04"]["level_match"] and c["LR-04"]["strongest_band"] == "intermediate"
    assert r["bands"] == {"stronger": 1, "intermediate": 1, "weaker": 2, "unrated": 0}
    assert r["reviewed"] == "register" and r["spread"] is None


def test_double_loop_cue():
    r = pmlc.review(reg_with(lr(1, "L4 X", [
        rec("Re-examine the design basis for the condensate line every five years"),
        rec("Fit an interlock on the test record before pressurisation"),
        rec("Review the incentive that rewards throughput over inspection", "administrative")])))
    assert r["loops"] == {"double": ["LR-01-R1", "LR-01-R3"], "single": ["LR-01-R2"]}


def test_smart_without_dates():
    r = pmlc.review(reg_with(lr(1, "L2 X", [
        rec("Fit interlock", ind=""),
        rec(basis=""),
        rec("Fit an interlock that blocks pressurisation without a signed test record")]),))
    assert r["smart"] == [{"rec": "LR-01-R1", "missing": ["specific", "measurable"]},
                          {"rec": "LR-01-R2", "missing": ["relevant"]}]
    # time-bound is never checked: a recommendation with no date is complete
    assert not any("time" in m for s in r["smart"] for m in s["missing"])


def test_recipients():
    r = pmlc.review(reg_with(lr(1, "L2 X", [rec(), rec()], recipient_role="maintenance supervisor"),
                             lr(2, "L2 X", [rec()], audiences=["stores", "maintenance supervisor"])))
    assert r["recipients"] == [{"role": "maintenance supervisor", "n": 3}, {"role": "stores", "n": 1}]


def test_nine_m_spread():
    reg = reg_with(lr(1, "L2 X", [rec(), rec()]), lr(2, "L2 X", [rec()]))
    nm = {"findings": {}, "conditions": {"c1": {"m": "M3", "learning_id": "LR-01", "recommendation_ids": ["LR-01-R1"]},
                                         "c2": {"m": "M3", "learning_id": "LR-02"},
                                         "c3": {"m": "M7", "learning_id": "LR-01"}}}
    r = pmlc.review(reg, nm)
    assert r["reviewed"] == "register+9M"
    assert r["spread"]["M3"] == 2 and r["spread"]["M7"] == 2 and r["spread"]["M1"] == 0 and len(r["spread"]) == 9


def write(tmp_path, name, obj):
    p = tmp_path / name
    p.write_text(json.dumps(obj), encoding="utf-8")
    return p


def test_rec_review_refuses_pack(ws, tmp_path):  # noqa: F811
    pack = write(tmp_path, "pack.json", {"schema": "pmlc-pack", "sections": []})
    res = run_fail("rec-review", str(ws), str(pack))
    assert res.returncode == 2 and "rec-review reads a learnings register (check-register passes on it), not a pack" in res.stderr
    assert "Traceback" not in res.stderr
    res = run_fail("rec-review", str(ws), str(write(tmp_path, "nolr.json", {"entries": [{"title": "x"}]})))
    assert res.returncode == 2 and "not a pack" in res.stderr


def test_rec_review_cli_and_items(ws, tmp_path):  # noqa: F811
    reg = write(tmp_path, "reg.json", MINI_REG)
    out = run("rec-review", str(ws), str(reg))
    assert "stronger 1; intermediate 1; weaker 0" in out
    first = run("rec-review", str(ws), str(reg), "--json")
    assert first == run("rec-review", str(ws), str(reg), "--json")          # byte-identical re-run
    assert json.loads(first)["bands"]["stronger"] == 1
    it = json.loads(run("rec-review", str(ws), str(reg), "--table-item", "strength"))
    assert it["kind"] == "table" and len(it["row_cites"]) == len(it["rows"]) == 1 and it["cites"] == ["FND-0001", "FND-0002"]
    sm = json.loads(run("rec-review", str(ws), str(reg), "--table-item", "smart"))
    assert sm["kind"] == "table" and len(sm["row_cites"]) == len(sm["rows"])
    run_fail("rec-review", str(ws), str(reg), "--table-item", "spread")


def test_rec_review_nine_m_needs_the_map(ws, tmp_path):  # noqa: F811
    reg = write(tmp_path, "reg.json", MINI_REG)
    res = run_fail("rec-review", str(ws), str(reg), "--nine-m")
    assert res.returncode == 2 and "nine-m-map.json" in res.stderr
    out = pmlc.outputs_dir(ws)
    out.mkdir(parents=True, exist_ok=True)
    (out / "nine-m-map.json").write_text(json.dumps({"conditions": {"c": {"m": "M2", "learning_id": "LR-01"}}}))
    d = json.loads(run("rec-review", str(ws), str(reg), "--nine-m", "--json"))
    assert d["reviewed"] == "register+9M" and d["spread"]["M2"] == 2
    sp = json.loads(run("rec-review", str(ws), str(reg), "--nine-m", "--table-item", "spread"))
    assert sp["rows"][1] == ["M2", 2]


def test_rec_review_hazira(hazira_ws):  # noqa: F811
    from test_calibration_p5 import SAMPLE
    reg = SAMPLE / "outputs" / "learnings-register.json"
    d = json.loads(run("rec-review", str(hazira_ws), str(reg), "--json"))
    print("Hazira bands:", d["bands"])
    assert d["bands"] == {"stronger": 24, "intermediate": 15, "weaker": 5, "unrated": 0}
    assert sum(d["bands"].values()) == 44
    assert [c["lr"] for c in d["causes"] if not c["level_match"]] == []
    assert (len(d["loops"]["double"]), len(d["loops"]["single"])) == (0, 44)
    assert d["smart"] == []
    assert d["recipients"][0] == {"role": "plant leadership", "n": 21}
