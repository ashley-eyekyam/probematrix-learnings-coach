"""effect-plan: the effectiveness schedule, Jacobsson spread/depth/duration, indicators (synthetic; Hazira in the calibration)."""
import json
import re

import pytest

from test_pmlc import MINI_REG, run, run_fail, ws  # noqa: F401
import pmlc  # noqa: E402


def entry(n, priority=1, transferability="other sites", hoc="engineering", ind="Share of restarts with a test record", **kw):
    e = {"lr_id": f"LR-{n:02d}", "finding_ids": ["FND-0001"], "transferability": transferability,
         "recommendations": [{"what": "Interlock pressurisation on a signed test record", "hoc_tier": hoc,
                              "leading_indicator": ind}]}
    if priority is not None:
        e["priority"] = priority
    e.update(kw)
    return e


def write(tmp_path, name, obj):
    p = tmp_path / name
    p.write_text(json.dumps(obj), encoding="utf-8")
    return p


def test_schedule_priority_1():
    d = pmlc.schedule([entry(1)])
    rows = d["rows"]
    assert [r["offset"] for r in rows] == ["30 days", "60 days", "90 days", "6 months", "12 months"]
    assert [r["kirkpatrick"] for r in rows] == ["L1", "L2", "L3", "L3", "L4"]
    assert [r["check"] for r in rows] == ["communicated", "understood", "applied", "applied", "effective"]
    assert all(r["lr_id"] == "LR-01" and r["priority"] == 1 and r["lagging"] == "" for r in rows)
    assert rows[0]["leading"] == "Share of restarts with a test record"


@pytest.mark.parametrize("prio", [2, 3, "2"])
def test_schedule_priority_2(prio):
    rows = pmlc.schedule([entry(1, priority=prio)])["rows"]
    assert [r["offset"] for r in rows] == ["3 months", "6 months", "12 months"]
    assert [r["kirkpatrick"] for r in rows] == ["L1-L2", "L3", "L4"]
    assert [r["check"] for r in rows] == ["communicated and understood", "applied", "effective"]


@pytest.mark.parametrize("tr,hoc,spread,depth", [
    ("same site", "elimination", "site", "system"),
    ("other sites", "substitution", "organisation", "system"),
    ("industry-wide", "engineering", "industry", "system"),
    ("other sites", "administrative", "organisation", "procedure"),
    ("same site", "training", "site", "individual"),
    ("same site", "ppe", "site", "individual"),
    ("same site", "", "site", "unknown"),
    ("", "engineering", "unknown", "system"),
])
def test_jacobsson(tr, hoc, spread, depth):
    d = pmlc.schedule([entry(1, transferability=tr, hoc=hoc)])
    assert d["learnings"]["LR-01"] == {"spread": spread, "depth": depth, "duration": "12 months"}


def test_jacobsson_strongest_recommendation_sets_depth():
    e = entry(1)
    e["recommendations"] = [{"what": "Train everyone on the seal standard", "hoc_tier": "training"},
                            {"what": "Fit an interlock on the test record", "hoc_tier": "engineering"}]
    assert pmlc.schedule([e])["learnings"]["LR-01"]["depth"] == "system"


def test_indicator_prefers_verification():
    e = entry(1, verification={"indicator": "Open seal deviations per quarter"})
    assert pmlc.schedule([e])["rows"][0]["leading"] == "Open seal deviations per quarter"
    e = entry(1, ind="")
    e["recommendations"][0]["indicator"] = "Fallback indicator"
    assert pmlc.schedule([e])["rows"][0]["leading"] == "Fallback indicator"
    e["recommendations"][0]["indicator"] = ""
    assert pmlc.schedule([e])["rows"][0]["leading"] == ""


def test_effect_plan_offsets_only(ws, tmp_path):  # noqa: F811
    reg = write(tmp_path, "reg.json", MINI_REG)
    text = run("effect-plan", str(ws), "--register", str(reg), "--json")
    for kind in ("schedule", "levels", "indicators"):
        text += run("effect-plan", str(ws), "--register", str(reg), "--table-item", kind)
    text += run("effect-plan", str(ws), "--register", str(reg), "--items", "audit")
    text += (ws / "effect_plan.json").read_text(encoding="utf-8")
    import pmlc_privacy as pv
    for rx in (pv.ISO_DATE_RX, pv.DMY_TEXT_RX, pv.MDY_TEXT_RX):
        assert not rx.search(text)
    assert "30 days after adoption" in text


def test_effect_plan_v03_register(ws, tmp_path):  # noqa: F811
    e = {k: v for k, v in MINI_REG["entries"][0].items() if k != "priority"}
    reg = write(tmp_path, "v03.json", {"entries": [e]})
    d = json.loads(run("effect-plan", str(ws), "--register", str(reg), "--json"))
    assert [r["offset"] for r in d["rows"]] == ["3 months", "6 months", "12 months"]
    assert any("LR-01" in n and "no priority" in n for n in d["notes"])


def test_effect_plan_refuses_pack(ws, tmp_path):  # noqa: F811
    pack = write(tmp_path, "pack.json", {"schema": "pmlc-pack", "sections": []})
    res = run_fail("effect-plan", str(ws), "--register", str(pack))
    assert res.returncode == 2 and "not a pack" in res.stderr
    res = run_fail("effect-plan", str(ws), "--register", str(write(tmp_path, "e.json", {"entries": []})))
    assert res.returncode == 2 and "no entries" in res.stderr
    res = run_fail("effect-plan", str(ws), "--register", str(tmp_path / "missing.json"))
    assert res.returncode == 2 and "Traceback" not in res.stderr


def test_effect_plan_table_items_and_audit(ws, tmp_path):  # noqa: F811
    reg = write(tmp_path, "reg.json", MINI_REG)
    sch = json.loads(run("effect-plan", str(ws), "--register", str(reg), "--table-item", "schedule"))
    assert sch["kind"] == "table" and len(sch["rows"]) == 5 and sch["cites"] == ["FND-0001", "FND-0002"]
    ind = json.loads(run("effect-plan", str(ws), "--register", str(reg), "--table-item", "indicators"))
    assert ind["columns"] == ["LR", "Leading", "Lagging"] and ind["rows"][0][2] == ""
    lev = json.loads(run("effect-plan", str(ws), "--register", str(reg), "--table-item", "levels"))
    assert [r[0] for r in lev["rows"]] == ["L1", "L2", "L3", "L4"]
    items = json.loads(run("effect-plan", str(ws), "--register", str(reg), "--items", "audit"))
    assert len(items) == 1 and items[0]["kind"] == "question"
    assert items[0]["question"] == "What would an auditor see that shows LR-01 is applied?"
    a = run("effect-plan", str(ws), "--register", str(reg), "--json")
    assert a == run("effect-plan", str(ws), "--register", str(reg), "--json")
    assert re.search(r"effect-plan", run("effect-plan", str(ws), "--register", str(reg)))
