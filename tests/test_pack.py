"""Learning-pack tests on the synthetic export from test_pmlc.py (fictional event, no real data)."""
import copy
import json
import os
import re
from pathlib import Path

import pytest

from test_pmlc import ROOT, make_export, run, run_fail, ws  # noqa: F401  (ws is a module-scoped fixture)
import pmlc  # noqa: E402  (test_pmlc put the engine folder on sys.path)
import pmlc_pack as pp  # noqa: E402

FIX = Path(__file__).resolve().parent / "fixtures" / "packs"
STATUS = "Learning purposes: not a statutory document"

MIN = {
    "para": {"text": "t"},
    "check": {"text": "t"},
    "question": {"question": "q", "why": "w"},
    "recommendation": {"change": "c", "indicator": "i", "hoc_tier": "engineering", "cites": ["FND-0001"]},
    "decision": {"decision": "d"},
    "indicator": {"name": "n", "measure": "m"},
    "card": {"title": "t", "what_happened": "w", "warning_signs": ["s"], "good_looks_like": "g", "cites": ["FND-0001"]},
    "scenario": {"situation": "s", "prompts": ["p"]},
    "table": {"columns": ["a"], "rows": [["1"]]},
    "test_point": {"requirement": "r", "sample": "s", "conformity_evidence": "c", "cites": ["EVD-0001"]},
    "module": {"title": "t", "objective": "o", "content": ["c"]},
    "barrier": {"barrier": "b", "failure_mode": "f", "hoc_tier": "administrative", "cites": ["FND-0002"]},
    "timeline": {"events": [{"date": "2024-03-12", "text": "seal change"}]},
    "graph": {"nodes": [{"id": "a", "label": "A"}, {"id": "b", "label": "B"}], "edges": [{"from": "a", "to": "b"}]},
}


def item(kind, **over):
    d = copy.deepcopy(MIN[kind])
    d.update(over)
    d["kind"] = kind
    return d


def pack_with(*items, **top):
    p = {"pack": "test-pack", "schema": 1, "title": "Test pack: synthetic pump fire", "audience": "Testers",
         "status": STATUS, "bottom_line": [{"text": "Test before service.", "cites": ["FND-0002"]}],
         "sections": [{"id": "s1", "heading": "Section one", "items": [copy.deepcopy(i) for i in items]}]}
    p.update(top)
    return p


@pytest.fixture(scope="module")
def w(ws):
    return pmlc.load_ws(ws)


def problems(p, w):
    return pp.check_pack(p, w).problems


def test_fourteen_kinds():
    assert sorted(pp.KINDS) == sorted(MIN)


@pytest.mark.parametrize("kind", sorted(MIN))
def test_minimal_item_of_each_kind_passes(w, kind):
    assert problems(pack_with(item(kind)), w) == []


@pytest.mark.parametrize("kind,field", [(k, f) for k in sorted(MIN) for f in pp.KINDS[k]["req"]])
def test_missing_required_field_is_reported_with_its_path(w, kind, field):
    it = item(kind)
    del it[field]
    assert f"sections[0].items[0].{field}: required for {kind}" in problems(pack_with(it), w)


@pytest.mark.parametrize("kind", [k for k in sorted(MIN) if pp.KINDS[k].get("cite")])
def test_kinds_that_must_cite(w, kind):
    it = item(kind)
    del it["cites"]
    assert any(x.startswith("sections[0].items[0].cites: a ") for x in problems(pack_with(it), w))


def _add(p, it):
    p["sections"][0]["items"].append(it)


@pytest.mark.parametrize("mutate, expected", [
    (lambda p: p.pop("title"), "title: required"),
    (lambda p: p.update(schema=2), "schema: must be 1"),
    (lambda p: p.update(pack="Supervisor Coach"), "pack: must be lowercase words"),
    (lambda p: p.update(status="Draft"), 'status: must contain "Learning purposes: not a statutory document"'),
    (lambda p: p.update(bottom_line=[]), "bottom_line: must be a non-empty list"),
    (lambda p: p.update(bottom_line=[{"text": "x", "cites": ["FND-0001"]}] * 8), "bottom_line: at most 7 entries (got 8)"),
    (lambda p: p.update(bottom_line=[{"text": "x"}]), "bottom_line[0].cites: every bottom-line entry needs"),
    (lambda p: p["sections"].append(copy.deepcopy(p["sections"][0])), "sections[1].id: duplicate id 's1'"),
    (lambda p: _add(p, {"kind": "poem", "text": "x"}), "sections[0].items[1].kind: unknown kind 'poem'"),
    (lambda p: _add(p, item("para", text="see FND-9999")), "sections[0].items[1].text: FND-9999 is not in this workspace"),
    (lambda p: _add(p, item("para", cites=["EVD-0404"])), "sections[0].items[1].cites[0]: EVD-0404 is not in this workspace"),
    (lambda p: _add(p, item("table", rows=[["1", "2"]])), "sections[0].items[1].rows[0]: must have 1 cells like columns"),
    (lambda p: _add(p, item("graph", edges=[{"from": "a", "to": "zz"}])), "sections[0].items[1].edges[0].to: 'zz' is not a node id"),
    (lambda p: _add(p, item("timeline", events=[{"date": "12/03/2024", "text": "x"}])), "sections[0].items[1].events[0].date: must be YYYY-MM-DD"),
    (lambda p: _add(p, item("timeline", events=[{"date": "2024-02-30", "text": "x"}])), "sections[0].items[1].events[0].date: must be YYYY-MM-DD"),
    (lambda p: _add(p, item("recommendation", hoc_tier="be careful")), "sections[0].items[1].hoc_tier: must name a hierarchy-of-controls tier"),
    (lambda p: _add(p, item("check", hold_point="yes")), "sections[0].items[1].hold_point: must be true or false"),
    (lambda p: _add(p, item("para", id="Bad Id")), "sections[0].items[1].id: must be lowercase words"),
    (lambda p: p.update(scope={"tiers": ["T9"]}), "scope.tiers: a list of T1"),
])
def test_rejections(w, mutate, expected):
    p = pack_with(item("para"))
    mutate(p)
    got = problems(p, w)
    assert any(x.startswith(expected) for x in got), got


def test_partial_iso_dates_and_dossier_name_pass(w):
    p = pack_with(item("timeline", events=[{"date": "2022-03", "text": "x"}, {"date": "2022", "text": "y"}]),
                  pack="dossier-F02")
    assert problems(p, w) == []


@pytest.mark.parametrize("p", [
    [], "x", {"pack": 3, "schema": "1", "title": [], "audience": None, "status": 7, "bottom_line": "x", "sections": {}},
    {"sections": [None, "x", {"id": "s", "heading": "h", "items": [None, 3, {"kind": "table", "columns": "a", "rows": "b"},
                                                                     {"kind": "graph", "nodes": [1], "edges": [2]},
                                                                     {"kind": "timeline", "events": "e"},
                                                                     {"kind": "para", "text": 5, "cites": "FND-0001"}]}]},
])
def test_wrong_types_never_crash(w, p):
    r = pp.check_pack(p, w)
    assert r.problems and all(re.match(r"^[\w\[\]().\-]+: ", x) for x in r.problems), r.problems


def test_scope_needs_clusters(w):
    w2 = {k: v for k, v in w.items() if k != "clusters"}
    got = problems(pack_with(item("para"), scope={"tiers": ["T2"]}), w2)
    assert any(x.startswith("scope: tiers and entities need clusters.json") for x in got)


def test_relevant_findings(w):
    assert pp.relevant_findings(w) == ["FND-0002", "FND-0003"]          # rating 4 is the workspace maximum
    assert pp.relevant_findings(w, {"levels": [1]}) == ["FND-0001"]
    assert "FND-0001" in pp.relevant_findings(w, {"tiers": ["T2"]})
    assert pp.relevant_findings({"findings": []}) == []


def test_warnings_do_not_fail(w):
    p = pack_with(item("para", txet="typo"), bottom_line=[{"text": "x", "cites": ["FND-0001"]}])
    r = pp.check_pack(p, w)
    assert r.problems == []
    assert "sections[0].items[0]: no Finding or Evidence ID cited" in r.warnings
    assert "sections[0].items[0].txet: unknown field for para (ignored)" in r.warnings
    assert any(x.startswith("coverage: cites 0 of 2 relevant findings") for x in r.warnings)
    assert not any(x.startswith("coverage") for x in pp.check_pack(pack_with(item("para", cites=["FND-0002"])), w).warnings)


def test_investigator_pack_needs_follow_up_table(w):
    got = problems(pack_with(item("para"), pack="investigator-coach"), w)
    assert any(x.startswith("investigator-coach: needs a table item with id follow-up") for x in got)
    t = item("table", id="follow-up", columns=pp.FOLLOW_UP_COLUMNS, rows=[["not an id", "a", "b", "c", "d"]])
    got = problems(pack_with(t, pack="investigator-coach"), w)
    assert "follow-up.rows[0][0]: must be a Finding ID" in got


def test_cited_ids_and_item_ids():
    p = pack_with(item("para", text="see EVD-0002 and FND-0001"), item("check", id="keep-me", cites=["FND-0003"]))
    assert pp.cited_ids(p) == (["FND-0002", "FND-0001", "FND-0003"], ["EVD-0002"])
    q = pp.with_item_ids(p)
    assert [i["id"] for i in q["sections"][0]["items"]] == ["s1-1", "keep-me"]
    assert "id" not in p["sections"][0]["items"][0]


def test_check_pack_cli(ws, tmp_path):
    good = tmp_path / "p.json"
    good.write_text(json.dumps(pack_with(item("para", cites=["FND-0002"]))), encoding="utf-8")
    assert run("check-pack", str(ws), str(good)).strip().endswith("OK: 1 sections, 1 items, 1 cited IDs")
    bad = tmp_path / "b.json"
    bad.write_text("{not json", encoding="utf-8")
    r = run_fail("check-pack", str(ws), str(bad))
    assert "(json): invalid JSON at line 1" in r.stderr
    r = run_fail("check-pack", str(ws), str(tmp_path / "missing.json"))
    assert "not found" in r.stderr
