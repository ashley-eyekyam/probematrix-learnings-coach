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
    "learning": {"lesson": "l", "cites": ["FND-0002"]},
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


def test_fifteen_kinds():
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
    assert "follow-up.rows[0][0]: must be one or more Finding IDs" in got


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


G_NODES = [{"id": "a", "label": "Seal bought locally"}, {"id": "b", "label": "No return-to-service check"},
           {"id": "c", "label": "Pump restarted untested"}, {"id": "d", "label": "Leak & fire"}]
G_EDGES = [{"from": "a", "to": "b"}, {"from": "b", "to": "c"}, {"from": "a", "to": "c", "label": "enabled"},
           {"from": "c", "to": "d"}, {"from": "d", "to": "a", "label": "feedback"}]


def test_layout_graph_is_deterministic_and_layered():
    g1 = pp.layout_graph(G_NODES, G_EDGES, uid="g1")
    assert g1 == pp.layout_graph(copy.deepcopy(G_NODES), copy.deepcopy(G_EDGES), uid="g1")
    assert g1["omitted"] == 0 and g1["shown"] == 4 and g1["svg"].startswith('<svg class="graph"')
    xs = [int(m) for m in re.findall(r'transform="translate\((\d+),', g1["svg"])]
    assert xs == sorted(xs) and len(set(xs)) == 4            # a, b, c, d sit in four successive layers
    assert 'class="edge back"' in g1["svg"]                  # d -> a closes a cycle
    assert "Leak &amp; fire" in g1["svg"] and "Leak & fire" not in g1["svg"]
    assert 'marker-end="url(#arr-g1)"' in g1["svg"] and 'id="arr-g1"' in g1["svg"]
    assert "http" not in g1["svg"]


def test_layout_graph_caps_nodes_and_ignores_self_loops():
    nodes = [{"id": f"n{i}", "label": f"Node {i}"} for i in range(61)]
    edges = [{"from": "n0", "to": f"n{i}"} for i in range(1, 60)]          # n60 has no links
    g = pp.layout_graph(nodes, edges, uid="big")
    assert g["omitted"] == 1 and g["shown"] == 60 and "Node 60<" not in g["svg"]
    assert pp.layout_graph([{"id": "x", "label": "X"}], [{"from": "x", "to": "x"}], uid="s")["shown"] == 1


WAVE1 = ["board-brief", "supervisor-coach", "investigator-coach"]
WAVE2 = ["frontline-learning-cards", "manager-coach", "site-leadership-coach", "top-management-brief",
         "auditor-assurance-pack", "training-designer", "emergency-response-learnings",
         "engineering-integrity-learnings", "supply-chain-contractor-learnings", "safety-committee-guide"]
WAVE3 = ["causal-map", "precursor-timeline", "interface-learnings", "barrier-learnings", "learning-clusters",
         "cluster-learning-dossier", "report-comparison", "organisation-learning-map"]
PACK_OF = {"cluster-learning-dossier": "dossier-F02", "organisation-learning-map": "organisation-learning-plan"}
DOC_NAME = {"cluster-learning-dossier": "dossier-<F-id>"}          # how SKILL.md writes the pack file name
DONE_WAVES = {"wave 1": WAVE1, "wave 2": WAVE2}                                     # tasks 15 and 24 add waves 2 and 3
VERSION = "0.3.2"                                                  # tasks 15 and 24 bump it


def pack_fixtures() -> list:
    """Every per-skill fixture pack (tests/fixtures/packs/<pack>.json), all-kinds excepted."""
    return sorted(p.stem for p in FIX.glob("*.json") if p.stem != "all-kinds")


def skill_of(pack) -> str:
    return {v: k for k, v in PACK_OF.items()}.get(pack, pack)


def fixture(name):
    return json.loads((FIX / f"{name}.json").read_text(encoding="utf-8"))


@pytest.mark.parametrize("name", pack_fixtures() + ["all-kinds"])
def test_fixtures_are_valid(w, name):
    r = pp.check_pack(fixture(name), w)
    assert r.problems == [], r.problems
    assert not [x for x in r.warnings if "unknown field" in x or "plain text" in x], r.warnings


def test_coverage_lists_uncited_relevant_findings(w):
    p = pack_with(item("para", cites=["FND-0002"]))
    cov = pp.coverage(w, p)
    assert cov["relevant"] == 2 and cov["cited"] == 1
    assert cov["uncovered"] == [{"id": "FND-0003", "label": "Seals bought locally without specification", "rating": 4,
                                 "level": 4, "reason": "not cited in this pack"}]
    w2 = dict(w, incident=dict(w["incident"], review_votes=[{"finding": "FND-0003", "vote": "downgrade"}]))
    assert pp.coverage(w2, p)["uncovered"][0]["reason"] == "reviewer downgrade vote"


def test_markdown_per_kind(w):
    md = pp.render_pack_md(fixture("all-kinds"), w)
    for expected in [
        "# All kinds: Synthetic pump fire\n\n*Learning purposes: not a statutory document*\n\n**Audience:** Test readers",
        "## Bottom line\n\n- Test before service. [FND-0002]",
        "## Every item kind\n\nOne of each kind.",
        "- [ ] **Hold point:** Leak-test record attached. *(before return to service)* [FND-0001]",
        "**Q: Who approved local purchase?** [FND-0003]\n- Why it matters: The records do not show the decision.\n"
        "- Good evidence looks like: Signed approvals\n- Ask: Stores/procurement officer",
        "**Recommendation:** Interlock restart on a test record [FND-0001]\n- Control tier: engineering\n"
        "- Owner: Maintenance manager\n- Leading indicator: % of restarts with a test record",
        "**Decision:** Fund a site-wide spares review [FND-0003]\n- Options: This year; Next year",
        "**Indicator:** Spares to specification [FND-0003]\n- Measure: % of orders with a specification",
        "### Test what you disturb [FND-0001]\n\n**What happened:** A pump restarted untested.",
        "**Warning signs:**\n- No test record\n- Unfamiliar seal",
        "**Scenario:** Asked to skip the test. [FND-0001]\n\n1. What do you say?",
        "| Finding | Note | Cites |\n|---|---|---|\n| FND-0002 | a \\| b | FND-0002 |",
        "**Test point:** Return-to-service tests are recorded [FND-0002]\n- What to sample: 10 recent restarts",
        "### Module: Return to service [FND-0002]\n\n- Objective: Apply the hold point\n- Audience: Fitters\n- Duration: 45 min",
        "**Barrier:** Leak test [FND-0001]\n- Failure mode: Skipped\n- Type: prevention\n- Control tier: administrative\n- Fix: Interlock",
        "- 2022-03: Local seal purchases begin *(weak signal)* [FND-0003]\n- 2024-03-12: Seal changed [FND-0001]",
        "Graph: 2 nodes, 1 links [FND-0003]\n\n- Seal bought locally → Pump restarted untested (enabled)",
        "---\n\nThis pack cites 2 of 2 relevant findings.\n\n> " + pmlc.BRAND + "\n",
    ]:
        assert expected in md, expected
    assert md.endswith(pmlc.BRAND + "\n")


@pytest.mark.parametrize("name", pack_fixtures())
def test_fixture_markdown_matches_golden(w, name):
    md = pp.render_pack_md(fixture(name), w)
    golden = FIX / f"{name}.md"
    if os.environ.get("PMLC_UPDATE_GOLDEN"):
        golden.write_text(md, encoding="utf-8")
    assert golden.exists(), f"no golden {golden.name}: run with PMLC_UPDATE_GOLDEN=1, then review it"
    assert md == golden.read_text(encoding="utf-8")


@pytest.mark.parametrize("name", pack_fixtures())
def test_fixture_html_renders(w, name):
    pack = fixture(name)
    t = pp.render_pack_html(w, pack, "2024-03-20-pump-fire", "2026-10-16")
    assert not re.search(r'(src|href)="(https?:)?//', t)
    assert t.count('id="pmlc-pack-data"') == 1 and STATUS in t and pmlc.BRAND in t
    for kind in {it["kind"] for s in pack["sections"] for it in s["items"]}:
        assert f'class="item k-{kind}"' in t, kind


@pytest.mark.parametrize("name", pack_fixtures())
def test_fixture_belongs_to_a_skill(name):
    assert fixture(name)["pack"] == name
    assert skill_of(name) in WAVE1 + WAVE2 + WAVE3, f"{name}: add its skill to a wave list or PACK_OF"


def _pack_data(t):
    m = re.search(r'<script type="application/json" id="pmlc-pack-data">(.*?)</script>', t, re.S)
    assert m, "no pmlc-pack-data block"
    return json.loads(m.group(1))


def test_render_pack_html_all_kinds(w):
    pack = fixture("all-kinds")
    t = pp.render_pack_html(w, pack, "2024-03-20-pump-fire", "2026-10-16")
    assert not re.search(r'(src|href)="(https?:)?//', t)
    assert t.count('id="pmlc-pack-data"') == 1 and t.count("</script>") == 2
    assert "&lt;/script&gt;&lt;script&gt;alert(1)&lt;/script&gt; &amp; &lt;b&gt;" in t
    d = _pack_data(t)
    fids, eids = pp.cited_ids(pack)
    assert set(fids) <= set(d["findings"]) and set(eids) <= set(d["evidence"])
    assert d["pack"] == "all-kinds" and d["run"] == "2024-03-20-pump-fire"
    for kind in pp.KINDS:
        assert f'class="item k-{kind}"' in t, kind
    assert 'id="i-leak-test"' in t and 'id="s-all"' in t and 'href="#s/all"' in t and 'id="i-all-1"' in t
    assert 'data-key="leak-test"' in t and 'id="clear-ticks"' in t
    assert '<svg class="graph"' in t and "url(#arr-causes)" in t
    assert 'data-id="FND-0001"' in t and 'aria-expanded="false"' in t
    assert "Learning purposes: not a statutory document" in t and pmlc.BRAND in t
    assert "This pack cites 2 of 2 relevant findings." in t and 'class="trail"' in t
    assert pmlc.PAGE_TOKENS_CSS in t and pmlc.WIDE_CSS in t and "function init()" in t and ".rail{" in t
    assert "Synthetic pump fire" in t and "2024-03-20" in t and "generated 2026-10-16" in t


def test_render_pack_html_lists_uncovered_findings(w):
    t = pp.render_pack_html(w, pack_with(item("para", cites=["FND-0002"])), "r", "2026-10-16")
    assert "This pack cites 1 of 2 relevant findings." in t and "Not covered here (1)" in t
    assert 'data-id="FND-0003"' in t and "FND-0003" in _pack_data(t)["findings"]
    assert 'id="clear-ticks"' not in t                     # no checks, no clear button


def test_follow_up_from_investigator_pack():
    fu = pp.follow_up(fixture("investigator-coach"))
    assert list(fu) == ["FND-0002", "FND-0003"]
    assert fu["FND-0003"] == {"evidence_to_collect": "Purchase orders since 2022",
                              "key_questions": "Who approved local purchase?",
                              "suggested_interviews": "Stores/procurement officer",
                              "causal_hypothesis": "Budget pressure drove local buying"}


def test_pack_cli_writes_html_md_and_follow_up(tmp_path):
    x = make_export(tmp_path)
    run("ingest", str(x), "--slug", "pump-fire")
    ws_ = tmp_path / "pmlc-runs" / "2024-03-20-pump-fire" / "workspace"
    run("classify", str(ws_))
    outd = ws_.parent / "outputs"
    src = outd / "investigator-coach.json"
    src.write_text((FIX / "investigator-coach.json").read_text(encoding="utf-8"), encoding="utf-8")
    run("pack", str(ws_), str(src))
    run("pack", str(ws_), str(src))                       # re-running overwrites cleanly
    t = (outd / "investigator-coach.html").read_text(encoding="utf-8")
    assert "run 2024-03-20-pump-fire" in t
    assert (outd / "investigator-coach.md").read_text(encoding="utf-8") == (FIX / "investigator-coach.md").read_text(encoding="utf-8")
    assert list(json.loads((outd / "follow-up.json").read_text(encoding="utf-8"))) == ["FND-0002", "FND-0003"]


def test_pack_cli_refuses_a_failing_pack(ws, tmp_path):
    bad = tmp_path / "b.json"
    bad.write_text(json.dumps(pack_with(item("para"), status="Draft")), encoding="utf-8")
    r = run_fail("pack", str(ws), str(bad), "--out", str(tmp_path / "o"))
    assert "status: must contain" in r.stderr and "Nothing written." in r.stderr
    assert not (tmp_path / "o").exists()


def test_pack_cli_no_md(ws, tmp_path):
    good = tmp_path / "p.json"
    good.write_text(json.dumps(pack_with(item("para", cites=["FND-0002"]))), encoding="utf-8")
    run("pack", str(ws), str(good), "--out", str(tmp_path / "o"), "--no-md")
    assert (tmp_path / "o" / "test-pack.html").exists() and not (tmp_path / "o" / "test-pack.md").exists()


def test_pack_on_minimal_workspace(ws, tmp_path):
    lone = tmp_path / "lone"
    lone.mkdir()
    (lone / "findings.json").write_text((ws / "findings.json").read_text(encoding="utf-8"), encoding="utf-8")
    good = tmp_path / "p.json"
    good.write_text(json.dumps(pack_with(item("para", cites=["FND-0002"]))), encoding="utf-8")
    run("pack", str(lone), str(good))
    assert (lone / "outputs" / "test-pack.html").exists()   # default folder for a legacy workspace


@pytest.mark.parametrize("skill", [s for s in WAVE1 + WAVE2 + WAVE3 if PACK_OF.get(s, s) in pack_fixtures()])
def test_skill_documents_its_pack(skill):
    t = (ROOT / "skills" / skill / "SKILL.md").read_text(encoding="utf-8")
    name = DOC_NAME.get(skill, PACK_OF.get(skill, skill))
    assert f"<run>/outputs/{name}.json" in t and "PMLC check-pack" in t and "PMLC pack" in t
    assert "pack-schema.md" in t
    assert len(t.splitlines()) <= 150


@pytest.mark.parametrize("wave", sorted(DONE_WAVES))
def test_wave_is_complete(wave):
    missing = [s for s in DONE_WAVES[wave] if PACK_OF.get(s, s) not in pack_fixtures()]
    assert missing == [], f"{wave}: no fixture pack for {missing}"


def test_pack_schema_reference_names_every_kind():
    t = (ROOT / "skills" / "learnings-coach" / "references" / "pack-schema.md").read_text(encoding="utf-8")
    for kind, spec in pp.KINDS.items():
        assert f"`{kind}`" in t, kind
        for f in spec["req"]:
            assert f in t, (kind, f)
    assert pp.STATUS_PHRASE in t and "check-pack" in t
    for f in ("incident", "data_quality", "exclusions", "supporting_cites", "evidence_strength", "group", "Cites"):
        assert f in t, f


def test_version():
    for p in (".claude-plugin/plugin.json", ".claude-plugin/marketplace.json"):
        assert f'"version": "{VERSION}"' in (ROOT / p).read_text(encoding="utf-8"), p


# ---- wave-1 review fixes

def test_scope_with_nested_lists_is_a_problem_not_a_crash(w):                       # review 1
    got = problems(pack_with(item("para"), scope={"tiers": [["T1"]], "entities": [["F02"]]}), w)
    assert any(x.startswith("scope.tiers: a list of T1") for x in got)


@pytest.mark.parametrize("label", [5, ["x"], ""])
def test_graph_edge_label_must_be_text(w, label):                                   # review 2
    it = item("graph", edges=[{"from": "a", "to": "b", "label": label}])
    assert "sections[0].items[0].edges[0].label: must be text" in problems(pack_with(it), w)


@pytest.mark.parametrize("over", [{"pack": "a\n"}, {"sections": [{"id": "s1\n", "heading": "h", "items": [MIN["para"] | {"kind": "para"}]}]}])
def test_trailing_newline_ids_are_rejected(w, over):                                # review 5
    assert problems(pack_with(item("para"), **over), w)


def test_ids_outside_citable_fields_do_not_count_and_warn(w):                       # review 6
    p = pack_with(item("para", cites=["FND-0001"]), bottom_line=[{"text": "x", "cites": ["FND-0001"]}])
    p["sections"][0]["heading"] = "About FND-0002 and FND-0003"
    p["sections"][0]["items"].append(item("check", when="see FND-0003", cites=["FND-0001"]))
    r = pp.check_pack(p, w)
    assert r.problems == []
    assert "sections[0].heading: FND-0002 is shown as plain text, not a citation; put it in cites" in r.warnings
    assert "sections[0].items[1].when: FND-0003 is shown as plain text, not a citation; put it in cites" in r.warnings
    assert pp.cited_ids(p) == (["FND-0001"], [])
    assert pp.coverage(w, p)["cited"] == 0
    p["sections"][0]["heading"] = "About FND-9999"                                   # plain text: not checked against the workspace
    assert pp.check_pack(p, w).problems == []


@pytest.mark.parametrize("make", [
    lambda d: (d / "u16.json").write_text('{"pack": "x"}', encoding="utf-16") and d / "u16.json",
    lambda d: d,
])
def test_unreadable_pack_file_is_a_problem(tmp_path, make):                         # review 7
    obj, err = pp.load_pack(make(tmp_path))
    assert obj is None and err.startswith("(file): ")


def test_check_label_does_not_wrap_citations(w):                                    # review 8
    t = pp.render_pack_html(w, pack_with(item("check", id="c1", text="Test record [FND-0001]")), "r", "d")
    m = re.search(r'<div class="item k-check" id="i-c1">(.*?)</div></div>', t, re.S)
    assert m and "<label" not in m.group(1)
    assert 'aria-labelledby="tl-c1"' in m.group(1) and 'id="tl-c1"' in m.group(1)
    assert 'data-id="FND-0001"' in m.group(1)


def test_duplicate_follow_up_rows_are_a_problem(w):                                 # review 10
    rows = [["FND-0002", "a", "b", "c", "d"], ["FND-0002", "e", "f", "g", "h"]]
    t = item("table", id="follow-up", columns=pp.FOLLOW_UP_COLUMNS, rows=rows)
    assert "follow-up.rows[1][0]: FND-0002 already has a row" in problems(pack_with(t, pack="investigator-coach"), w)


# ---- v1.1: checkpoint amendment

def _meta(t):
    return re.search(r'<p class="m">(.*?)</p>', t, re.S).group(1)


def test_incident_override_in_header(w):
    p = pack_with(item("para", cites=["FND-0002"]), incident={"title": "Corrected pump fire", "date": "2024-03-19"})
    assert pp.check_pack(p, w).problems == []
    m = _meta(pp.render_pack_html(w, p, "r", "d"))
    assert "Corrected pump fire" in m and "2024-03-19" in m and "2024-03-20" not in m


@pytest.mark.parametrize("inc, expected", [
    ("x", "incident: must be an object"), ({"date": "20/03/2024"}, "incident.date: must be YYYY-MM-DD"),
    ({"date": "2024-03"}, "incident.date: must be YYYY-MM-DD"), ({"place": "x"}, "incident.place: unknown key"),
    ({"title": 5}, "incident.title: must be non-empty text")])
def test_incident_override_validation(w, inc, expected):
    got = problems(pack_with(item("para"), incident=inc), w)
    assert any(x.startswith(expected) for x in got), got


def test_row_cites_column_is_labelled_cites(w):
    p = pack_with(item("table", columns=["Finding"], rows=[["FND-0002"]], row_cites=[["FND-0002"]]))
    assert "| Finding | Cites |" in pp.render_pack_md(p, w)
    t = pp.render_pack_html(w, p, "r", "d")
    assert '<th scope="col">Cites</th>' in t and '<td class="cites-cell">' in t


DQ = [{"text": "The summary sheet date is wrong.", "cites": ["EVD-0002"]}]
EX = [{"id": "FND-0003", "reason": "Reviewer downgrade vote: not substantiated"}]


def test_data_quality_notes(w):
    p = pack_with(item("para", cites=["FND-0002"]), data_quality=DQ)
    assert pp.check_pack(p, w).problems == []
    assert "EVD-0002" in pp.cited_ids(p)[1]
    assert "## Data quality and limits\n\n- The summary sheet date is wrong. [EVD-0002]" in pp.render_pack_md(p, w)
    t = pp.render_pack_html(w, p, "r", "d")
    assert '<section class="dq"><h2>Data quality and limits</h2>' in t
    assert t.index('class="status"') < t.index('class="dq"') < t.index('class="bottom"')


@pytest.mark.parametrize("dq, expected", [
    ([], "data_quality: must be a non-empty list"), ("x", "data_quality: must be a non-empty list"),
    ([{"cites": ["EVD-0002"]}], "data_quality[0].text: required"),
    ([{"text": "x", "cites": "EVD-0002"}], "data_quality[0].cites: must be a list"),
    ([{"text": "x", "cites": ["EVD-0404"]}], "data_quality[0].cites[0]: EVD-0404 is not in this workspace")])
def test_data_quality_validation(w, dq, expected):
    got = problems(pack_with(item("para"), data_quality=dq), w)
    assert any(x.startswith(expected) for x in got), got


def test_exclusions_leave_coverage_and_show_reason(w):
    p = pack_with(item("para", cites=["FND-0002"]), exclusions=EX)
    r = pp.check_pack(p, w)
    assert r.problems == [] and not any(x.startswith("coverage") for x in r.warnings)
    cov = pp.coverage(w, p)
    assert (cov["relevant"], cov["cited"], cov["uncovered"]) == (1, 1, [])
    assert cov["excluded"] == [{"id": "FND-0003", "label": "Seals bought locally without specification",
                                "reason": "Reviewer downgrade vote: not substantiated"}]
    md = pp.render_pack_md(p, w)
    assert ("This pack cites 1 of 1 relevant findings.\n\nLeft out on purpose:\n"
            "- FND-0003: Reviewer downgrade vote: not substantiated") in md
    t = pp.render_pack_html(w, p, "r", "d")
    assert "Left out on purpose (1)" in t and "Reviewer downgrade vote: not substantiated" in t
    assert "FND-0003" in pp.build_pack_data(w, p, "r")["findings"] and "FND-0003" not in pp.cited_ids(p)[0]


@pytest.mark.parametrize("ex, expected", [
    ([{"id": "FND-0002", "reason": "x"}], "exclusions[0].id: FND-0002 is also cited"),
    ([{"id": "FND-9999", "reason": "x"}], "exclusions[0].id: FND-9999 is not in this workspace"),
    ([{"id": "EVD-0001", "reason": "x"}], "exclusions[0].id: must be a Finding ID"),
    ([{"id": "FND-0003"}], "exclusions[0].reason: required"),
    ([EX[0], EX[0]], "exclusions[1].id: FND-0003 is listed twice"),
    ([3], "exclusions[0]: must be an object"),
    ("FND-0003", "exclusions: must be a non-empty list")])
def test_exclusions_validation(w, ex, expected):
    got = problems(pack_with(item("para"), exclusions=ex), w)          # the bottom line cites FND-0002
    assert any(x.startswith(expected) for x in got), got


def test_extras_validation(w):
    got = problems(pack_with(item("para", supporting_cites="FND-0003", evidence_strength="strong", group="")), w)
    for e in ["sections[0].items[0].supporting_cites: must be a list",
              "sections[0].items[0].evidence_strength: must be one of direct, corroborated, inferred",
              "sections[0].items[0].group: must be non-empty text"]:
        assert any(x.startswith(e) for x in got), (e, got)
    got = problems(pack_with(item("para"), bottom_line=[{"text": "x", "cites": ["FND-0002"], "evidence_strength": "maybe"}]), w)
    assert any(x.startswith("bottom_line[0].evidence_strength: must be one of") for x in got)
    got = problems(pack_with(item("para", supporting_cites=["FND-9999"])), w)
    assert "sections[0].items[0].supporting_cites[0]: FND-9999 is not in this workspace" in got


def test_supporting_cites_count_and_render(w):
    p = pack_with(item("para", text="Key point.", cites=["FND-0002"], supporting_cites=["FND-0003", "EVD-0003"],
                       evidence_strength="corroborated"),
                  bottom_line=[{"text": "Test before service.", "cites": ["FND-0002"], "supporting_cites": ["FND-0001"],
                                "evidence_strength": "direct"}])
    r = pp.check_pack(p, w)
    assert r.problems == [] and not any("unknown field" in x for x in r.warnings)
    assert pp.coverage(w, p)["cited"] == 2
    t = pp.render_pack_html(w, p, "r", "d")
    assert "<summary>+2 supporting</summary>" in t and "Evidence: corroborated" in t
    assert "<summary>+1 supporting</summary>" in t and "Evidence: direct" in t
    md = pp.render_pack_md(p, w)
    assert "Key point. [FND-0002] *(evidence: corroborated; +2 supporting)*" in md
    assert "- Test before service. [FND-0002] *(evidence: direct; +1 supporting)*" in md
    assert "## Supporting citations\n\n- Bottom line › 1: FND-0001\n- Section one › 1: FND-0003; EVD-0003" in md


def test_groups_render_as_subheadings(w):
    p = pack_with(item("check", group="Oversee"), item("check", group="Oversee"), item("check", group="Plan"),
                  item("check"), item("check", group="Plan"), item("para", group="<b>x</b>"))
    t = pp.render_pack_html(w, p, "r", "d")
    assert t.count('<h3 class="group">Oversee</h3>') == 1 and t.count('<h3 class="group">Plan</h3>') == 2
    assert '<h3 class="group">&lt;b&gt;x&lt;/b&gt;</h3>' in t
    md = pp.render_pack_md(p, w)
    assert md.count("### Oversee") == 1 and md.count("### Plan") == 2


FU_COLS = pp.FOLLOW_UP_COLUMNS


def test_follow_up_rows_may_group_findings(w):
    rows = [["FND-0002, ,FND-0003;", "a", "b", "c", "d"]]
    p = pack_with(item("table", id="follow-up", columns=FU_COLS, rows=rows), pack="investigator-coach")
    assert problems(p, w) == []
    fu = pp.follow_up(p)
    assert list(fu) == ["FND-0002", "FND-0003"] and fu["FND-0003"]["causal_hypothesis"] == "d"
    p2 = pack_with(item("table", id="follow-up", columns=FU_COLS, rows=rows + [["FND-0003", "e", "f", "g", "h"]]),
                   pack="investigator-coach")
    assert "follow-up.rows[1][0]: FND-0003 already has a row" in problems(p2, w)


def test_coverage_warns_only_under_a_quarter(w):
    p = pack_with(item("para"), scope={"levels": [1, 2, 3, 4]})          # 4 relevant, bottom line cites 1
    assert not any(x.startswith("coverage") for x in pp.check_pack(p, w).warnings)


# ---- waves 2/3, task 1: pilot friction fixes

def test_markdown_shows_the_incident(w):
    md = pp.render_pack_md(pack_with(item("para", cites=["FND-0002"])), w)
    assert "**Audience:** Testers\n\n**Incident:** Synthetic pump fire · 2024-03-20\n\n" in md
    p = pack_with(item("para", cites=["FND-0002"]), incident={"title": "Corrected pump fire", "date": "2024-03-19"})
    md = pp.render_pack_md(p, w)
    assert "**Incident:** Corrected pump fire · 2024-03-19" in md and "2024-03-20" not in md


def test_table_rows_may_carry_supporting_cites(w):
    t_ = item("table", columns=["Finding"], rows=[["Spares"], ["Checklist"]], row_cites=[["FND-0003"], ["FND-0002"]],
              row_supporting_cites=[["EVD-0003", "FND-0001"], []])
    p = pack_with(t_)
    r = pp.check_pack(p, w)
    assert r.problems == [] and not any("unknown field" in x for x in r.warnings)
    assert "FND-0001" in pp.cited_ids(p)[0]
    md = pp.render_pack_md(p, w)
    assert "| Spares | FND-0003 (+2 supporting) |" in md and "| Checklist | FND-0002 |" in md
    assert "- Section one › 1, row 1: EVD-0003; FND-0001" in md
    assert pp.render_pack_html(w, p, "r", "d").count("<summary>+2 supporting</summary>") == 1
    only = pack_with(item("table", columns=["a"], rows=[["x"]], row_supporting_cites=[["FND-0002"]]))
    assert problems(only, w) == [] and "| a | Cites |" in pp.render_pack_md(only, w)
    assert "| x | +1 supporting |" in pp.render_pack_md(only, w)
    got = problems(pack_with(item("table", columns=["a"], rows=[["x"]], row_supporting_cites=[["FND-0002"], []])), w)
    assert any(x.startswith("sections[0].items[0].row_supporting_cites: must hold one list of IDs per row") for x in got)


def test_follow_up_notes_per_finding(w):
    rows = [["FND-0002, FND-0003", "a", "b", "c", "d"]]
    notes = {"FND-0003": "Ask who approved local buying first."}
    p = pack_with(item("table", id="follow-up", columns=FU_COLS, rows=rows, finding_notes=notes), pack="investigator-coach")
    r = pp.check_pack(p, w)
    assert r.problems == [] and not any("unknown field" in x for x in r.warnings)
    fu = pp.follow_up(p)
    assert fu["FND-0003"]["note"] == notes["FND-0003"] and "note" not in fu["FND-0002"]
    assert "Notes per finding:\n- FND-0003: Ask who approved local buying first." in pp.render_pack_md(p, w)
    assert '<ul class="notes"><li>' in pp.render_pack_html(w, p, "r", "d")


@pytest.mark.parametrize("notes, expected", [
    ("x", "finding_notes: must be an object"),
    ({"FND-0001": "not in a row"}, "finding_notes.FND-0001: not a Finding ID in this table's first column"),
    ({"FND-0002": ""}, "finding_notes.FND-0002: must be non-empty text"),
])
def test_follow_up_notes_validation(w, notes, expected):                              # review focus 5
    p = pack_with(item("table", id="follow-up", columns=FU_COLS, rows=[["FND-0002", "a", "b", "c", "d"]],
                       finding_notes=notes), pack="investigator-coach")
    got = problems(p, w)
    assert any(x.startswith("sections[0].items[0]." + expected) for x in got), got


def test_finding_notes_only_on_the_follow_up_table(w):
    got = problems(pack_with(item("table", finding_notes={"FND-0002": "x"})), w)
    assert any(x.startswith("sections[0].items[0].finding_notes: only on the investigator-coach follow-up table")
               for x in got), got


def test_dossier_pack_name_for_a_lettered_entity(w):                                  # review focus 1
    assert problems(pack_with(item("para"), pack="dossier-F09b"), w) == []
    assert any(x.startswith("pack: must be lowercase") for x in problems(pack_with(item("para"), pack="dossier-F09B"), w))


def test_scope_entities_must_exist(w):                                                # review focus 2
    assert "scope.entities: F2 is not an entity in clusters.json" in problems(pack_with(item("para"), scope={"entities": ["F2"]}), w)
    assert problems(pack_with(item("para"), scope={"entities": ["F09b"]}), w) == []


def test_summary_boxes_fit_their_text():
    css = (pmlc.DASHBOARD_ASSETS / "pack.css").read_text(encoding="utf-8")
    assert ".bottom,.dq{width:fit-content;max-width:100%;box-sizing:border-box}" in css


def test_schema_reference_covers_the_friction_fixes():
    t = (ROOT / "skills" / "learnings-coach" / "references" / "pack-schema.md").read_text(encoding="utf-8")
    assert "rates the evidence for the condition the item describes, not how well a proposed fix will work" in t
    for f in ("row_supporting_cites", "finding_notes", "dossier-F09b", "**Incident:**"):
        assert f in t, f


# ---- waves 2/3, task 2: learning kind, barrier and timeline fields

def test_learning_item(w):
    it = item("learning", lesson="Test what you disturb.", explanation="The seal was changed and not tested [EVD-0001].",
              owner="Maintenance supervision", cites=["FND-0001"])
    p = pack_with(it)
    assert pp.check_pack(p, w).problems == []
    assert "EVD-0001" in pp.cited_ids(p)[1]
    md = pp.render_pack_md(p, w)
    assert ("**Learning:** Test what you disturb. [FND-0001]\n\nThe seal was changed and not tested [EVD-0001]."
            "\n\n- Owner: Maintenance supervision") in md
    h = pp.render_pack_html(w, p, "r", "d")
    assert 'class="item k-learning"' in h and "<b>Test what you disturb.</b>" in h
    assert '<span class="badge">Owner: Maintenance supervision</span>' in h and 'data-id="EVD-0001"' in h


def test_barrier_owner_state_and_indicator(w):
    p = pack_with(item("barrier", owner="Maintenance (T2)", state="degraded", indicator="% of restarts with a test record"))
    r = pp.check_pack(p, w)
    assert r.problems == [] and not any("unknown field" in x for x in r.warnings)
    md = pp.render_pack_md(p, w)
    assert "- State on the day: degraded\n- Owner: Maintenance (T2)\n- Control tier: administrative" in md
    assert "- Leading indicator: % of restarts with a test record" in md
    h = pp.render_pack_html(w, p, "r", "d")
    assert "State: degraded" in h and "Owner: Maintenance (T2)" in h and ">Leading indicator<" in h
    got = problems(pack_with(item("barrier", state="broken")), w)
    assert any(x.startswith("sections[0].items[0].state: must be one of absent, degraded, defeated, worked partly, worked")
               for x in got), got


def test_timeline_times_and_signal_handling(w):
    ev = [{"date": "2024-03-20", "time": "14:20", "text": "Isolation valve closed", "cites": ["FND-0004"]},
          {"date": "2024-03-20", "time": "14:05", "text": "Gas alarm on the display", "cites": ["FND-0004"]},
          {"date": "2022-03", "text": "Local seal purchases begin", "signal": True, "received_by": "Stores (T1)",
           "response": "None recorded", "cites": ["FND-0003"]}]
    p = pack_with(item("timeline", events=ev))
    assert pp.check_pack(p, w).problems == []
    md = pp.render_pack_md(p, w)
    assert ("- 2022-03: Local seal purchases begin *(weak signal)* [FND-0003]\n  - Received by: Stores (T1)\n"
            "  - Response: None recorded\n- 2024-03-20 14:05: Gas alarm on the display [FND-0004]\n"
            "- 2024-03-20 14:20: Isolation valve closed [FND-0004]") in md
    h = pp.render_pack_html(w, p, "r", "d")
    assert "<time>2024-03-20 14:05</time>" in h and "Received by: Stores (T1)" in h and "Response: None recorded" in h
    assert h.index("14:05</time>") < h.index("14:20</time>")


def test_same_day_events_without_times_keep_their_order(w):                          # review focus 3
    ev = [{"date": "2024-03-20", "text": "Alarm"}, {"date": "2024-03-20", "text": "Phone call"},
          {"date": "2024-03-20", "text": "Isolation"}]
    md = pp.render_pack_md(pack_with(item("timeline", events=ev)), w)
    assert md.index("Alarm") < md.index("Phone call") < md.index("Isolation")


@pytest.mark.parametrize("extra, expected", [
    ({"time": "2pm"}, "events[0].time: must be HH:MM"), ({"time": "24:00"}, "events[0].time: must be HH:MM"),
    ({"time": "14:05\n"}, "events[0].time: must be HH:MM"),
    ({"received_by": ""}, "events[0].received_by: must be non-empty text"),
    ({"response": 3}, "events[0].response: must be non-empty text")])
def test_timeline_event_extras_validation(w, extra, expected):
    ev = dict({"date": "2024-03-20", "text": "x"}, **extra)
    got = problems(pack_with(item("timeline", events=[ev])), w)
    assert any(x.startswith("sections[0].items[0]." + expected) for x in got), got


# ---- waves 2/3, task 3: causal-item

CG = {"nodes": [{"code": "OR 2.2", "name": "Spares Programme Failure", "level": 4},
                {"code": "SV 1.4", "name": "No Guidance Provided", "level": 3},
                {"code": "AB 1.1", "name": "Step Omitted", "level": 1}],
      "edges": [{"from": "SV 1.4", "to": "AB 1.1", "mentions": 1, "findings": ["FND-0002"]},
                {"from": "OR 2.2", "to": "AB 1.1", "mentions": 2, "findings": ["FND-0003", "FND-0001"]},
                {"from": "OR 2.2", "to": "SV 1.4", "mentions": 1, "findings": ["FND-0003"]}]}


def test_causal_graph_item():
    it = pp.causal_graph_item(CG, top=2)
    assert it["kind"] == "graph" and it["id"] == "causal-map"
    assert it["edges"] == [{"from": "OR 2.2", "to": "AB 1.1", "label": "2 mentions"},
                           {"from": "OR 2.2", "to": "SV 1.4", "label": "1 mention"}]
    assert it["nodes"] == [{"id": "OR 2.2", "label": "L4 OR 2.2 Spares Programme Failure"},
                           {"id": "AB 1.1", "label": "L1 AB 1.1 Step Omitted"},
                           {"id": "SV 1.4", "label": "L3 SV 1.4 No Guidance Provided"}]
    assert it["cites"] == ["FND-0001", "FND-0003"]
    assert pp.causal_graph_item(CG, top=10) == pp.causal_graph_item(CG, top=10)          # deterministic


def test_causal_item_cli(ws, tmp_path):                                                  # review focus 4
    run("causal", str(ws))
    it = json.loads(run("causal-item", str(ws), "--top", "3"))
    assert len(it["edges"]) == 3 and problems(pack_with(it), pmlc.load_ws(ws)) == []
    lone = tmp_path / "lone"
    lone.mkdir()
    for f in ("findings.json", "evidence.json", "incident.json"):
        (lone / f).write_bytes((ws / f).read_bytes())
    assert "Run: pmlc.py causal" in run_fail("causal-item", str(lone)).stderr
    (lone / "causal_graph.json").write_text('{"nodes": [], "edges": []}', encoding="utf-8")
    r = run_fail("causal-item", str(lone))
    assert "no links" in r.stderr and r.stdout == ""
