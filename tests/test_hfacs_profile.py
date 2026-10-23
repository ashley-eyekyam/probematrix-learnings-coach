"""hfacs-profile (Phase 5 Task 3): the level x subcategory heat map, recurrence and causal feed counts."""
import json

import pytest

import pmlc  # noqa: E402
from test_calibration_p5 import hazira_ws  # noqa: F401  (module fixture, re-used)
from test_pmlc import make_export, make_thin_export, run

pytest.importorskip("openpyxl")


def _prof(ws):
    run("hfacs-profile", str(ws))
    return json.loads((ws / "hfacs_profile.json").read_text(encoding="utf-8"))


def test_every_prefix_resolves(hazira_ws):  # noqa: F811
    prof = _prof(hazira_ws)
    assert prof["unresolved"] == []
    assert prof["version"] == 1
    assert sum(prof["levels"].values()) == 436
    assert prof["share_l34"] == round((prof["levels"]["3"] + prof["levels"]["4"]) / 436, 3)
    assert sum(r["top"] + r["other"] for r in prof["matrix"]) == 436


def test_feeds_match_causal_graph(hazira_ws):  # noqa: F811
    prof = _prof(hazira_ws)
    g = json.loads((hazira_ws / "causal_graph.json").read_text(encoding="utf-8"))
    feeds = {r["code"]: r for r in prof["feeds"]}
    for node in g["nodes"]:
        out = sum(1 for e in g["edges"] if e["from"] == node["code"])
        inn = sum(1 for e in g["edges"] if e["to"] == node["code"])
        if out or inn:
            assert feeds[node["code"]]["out"] == out
            assert feeds[node["code"]]["in"] == inn
        else:
            assert node["code"] not in feeds


def test_heatmap_rows_cite(hazira_ws):  # noqa: F811
    prof = _prof(hazira_ws)
    for which in ("heatmap", "feeds", "recurrence"):
        out = json.loads(run("hfacs-profile", str(hazira_ws), "--table-item", which))
        assert out["kind"] == "table"
        assert len(out["row_cites"]) == len(out["rows"]) > 0
        assert all(c and all(x.startswith("FND-") for x in c) for c in out["row_cites"])
        assert out["cites"] == sorted({x for c in out["row_cites"] for x in c})
    heat = json.loads(run("hfacs-profile", str(hazira_ws), "--table-item", "heatmap"))
    assert len(heat["rows"]) == len(prof["matrix"])


def test_hfacs_profile_thin_export(tmp_path):
    x = make_thin_export(tmp_path)
    d = tmp_path / "ws"
    run("ingest", str(x), "--legacy-out", str(d))
    prof = _prof(d)                                  # no causal run at all
    assert prof["feeds"] == []
    assert any("causal" in n for n in prof["notes"])
    run("causal", str(d))                            # a causal run with no links
    prof = _prof(d)
    assert prof["feeds"] == []
    assert prof["notes"]


def test_unknown_prefix_reported():
    w = {"findings": [
        {"id": "FND-0001", "code": "ZZZ 1.1", "name": "Odd", "level": 2, "subcategory": "Odd things", "rating": 3},
        {"id": "FND-0002", "code": "AJDE 1.1", "name": "Wrong choice", "level": 1, "subcategory": "Violations",
         "rating": 2}]}
    from pmlc_lib.hfacs_profile import profile
    prof = profile(w, None)
    assert prof["unresolved"] == ["ZZZ"]
    assert prof["levels"]["2"] == 1


def test_profile_cli_json_and_rerun_identical(tmp_path):
    x = make_export(tmp_path, causal_rows=True)
    d = tmp_path / "ws"
    run("ingest", str(x), "--legacy-out", str(d))
    run("classify", str(d))
    run("causal", str(d))
    out = json.loads(run("hfacs-profile", str(d), "--json"))
    first = (d / "hfacs_profile.json").read_bytes()
    run("hfacs-profile", str(d))
    assert (d / "hfacs_profile.json").read_bytes() == first
    assert out["feeds"]
    assert pmlc.stale_files(d) == []
