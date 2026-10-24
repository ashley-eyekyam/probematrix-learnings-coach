"""Learning-pack tests on the synthetic export from test_pmlc.py (fictional event, no real data)."""
import copy
import html
import json
import os
import re
import subprocess
import sys
from pathlib import Path

import pytest

from test_pmlc import MINI_REG, ROOT, make_export, run, run_fail, ws  # noqa: F401  (ws is a module-scoped fixture)
import pmlc  # noqa: E402  (test_pmlc put the engine folder on sys.path)
import pmlc_pack as pp  # noqa: E402

sys.path.insert(0, str(ROOT / "tools"))
import release  # noqa: E402  (tools/release.py: the PEP 440 -> semver mapping the manifests use)

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
    "toolbox": {"opening_question": "o", "story": "s", "warning_signs": ["a", "b"], "one_change": "c",
                "crew_question": "q", "cites": ["FND-0001"]},
    "script": {"title": "t", "segments": [{"visual": "v", "narration": "n", "seconds": 30}], "cites": ["FND-0001"]},
    "risk_change": {"risk": "r", "change_type": "kri", "current_assumption": "a", "evidence_says": "e",
                    "proposed_change": "p", "cites": ["FND-0001"]},
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
def w(ws):  # noqa: F811
    return pmlc.load_ws(ws)


def problems(p, w):
    return pp.check_pack(p, w).problems


def test_eighteen_kinds():
    assert len(pp.KINDS) == 18 and sorted(pp.KINDS) == sorted(MIN)


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
    assert any(x.startswith("scope: tiers, entities and tags need clusters.json") for x in got)


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


def test_check_pack_cli(ws, tmp_path):  # noqa: F811
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


def fixture_skills() -> dict:
    """fixture name -> its top-level `skill` (Ruling P4-22), for the fixtures that carry one: the packs named after
    something other than their skill, and the variants."""
    out = {}
    for p in sorted(FIX.glob("*.json")):
        d = json.loads(p.read_text(encoding="utf-8"))
        if isinstance(d, dict) and isinstance(d.get("skill"), str):
            out[p.stem] = d["skill"]
    return out


# skill -> its fixture, where the pack is not named after the skill and is not a <skill>-<variant> pack
PACK_OF = {s: n for n, s in fixture_skills().items() if n != s and not n.startswith(s + "-")}
DOC_NAME = {"cluster-learning-dossier": "dossier-<F-id>"}          # how SKILL.md writes the pack file name
WAVE4 = ["latent-conditions-profile", "failure-to-learn-review",   # Phase 5: each new-skill task (13-19, 22, 23)
         "people-workforce-learnings", "compliance-crosswalk",      # adds its skill here
         "risk-register-update", "open-questions-register",
         "evidence-strength-scorecard", "nine-m-analysis",
         "recommendation-strength-review"]
DONE_WAVES = {"wave 1": WAVE1, "wave 2": WAVE2, "wave 3": WAVE3, "wave 4": WAVE4}
ALL_WAVES = WAVE1 + WAVE2 + WAVE3 + WAVE4
VERSION = pmlc.__version__


def pack_fixtures() -> list:
    """Every per-skill fixture pack (tests/fixtures/packs/<pack>.json): all-kinds, the bad L3-01 pack and the
    html-golden.json table excepted."""
    return sorted(p.stem for p in FIX.glob("*.json") if p.stem not in ("all-kinds", "bad-l3-01", "html-golden"))


def skill_of(pack) -> str:
    """The skill a fixture belongs to: its `skill` field, else its own name."""
    return fixture_skills().get(pack, pack)


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
        "# All kinds: Synthetic pump fire\n\n**DRAFT**\n\nReview: draft · Classification: internal · Version 1.0\n\n"
        "Draft because: no finding is marked as edited by a person\n\n*Learning purposes: not a statutory document · "
        "Learnings drafted by an AI agent from AI-assisted findings*\n\n*About 2 min read*\n\n**Audience:** Test readers",
        "## Bottom line\n\n- Test before service. [FND-0002]",
        "## Every item kind\n\nOne of each kind.",
        "- [ ] **Hold point:** Leak-test record attached. *(before return to service)* [FND-0001]",
        "**Q: Who approved local purchase?** [FND-0003]\n- Why it matters: The records do not show the decision.\n"
        "- Good evidence looks like: Signed approvals\n- Put to: Stores/procurement officer",
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
        "- 2022-03 (24 months before): Local seal purchases begin *(weak signal)* [FND-0003]\n- 2024-03-12: Seal changed [FND-0001]",
        "Graph: 2 nodes, 1 links [FND-0003]\n\n- Seal bought locally → Pump restarted untested (enabled)",
        "---\n\nThis pack cites 2 of 2 relevant findings.\n\n2 of 2 top-rated relevant findings cited.\n\n> "
        + pmlc.BRAND + "\n",
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


GOLDEN_EPOCH = "1600905600"                       # 2020-09-24: SOURCE_DATE_EPOCH for every golden render (P4-3)
HTML_GOLDEN = FIX / "html-golden.json"
RUN = "2024-03-20-pump-fire"


_GOLDEN_WS = []


def golden_ws():
    """A workspace built once per session from the synthetic export (the same steps as the ws fixture), so the
    golden helper needs no pytest fixture."""
    if not _GOLDEN_WS:
        import atexit
        import shutil
        import tempfile
        d = Path(tempfile.mkdtemp(prefix="pmlc-golden-"))
        atexit.register(shutil.rmtree, d, True)
        run("ingest", str(make_export(d)), "--legacy-out", str(d / "ws"))
        run("classify", str(d / "ws"))
        _GOLDEN_WS.append(d / "ws")
    return _GOLDEN_WS[0]


def render_fixture(name, fmt="html", **ctx_overrides) -> list:
    """The Outputs of fixture <name> in format fmt, rendered through the registry with SOURCE_DATE_EPOCH=1600905600
    (the golden helper, P4-3). ctx_overrides set RenderContext fields (w defaults to the golden workspace)."""
    from pmlc_lib import render as R
    from pmlc_lib.handling import effective_handling
    old = os.environ.get("SOURCE_DATE_EPOCH")
    os.environ["SOURCE_DATE_EPOCH"] = GOLDEN_EPOCH
    try:
        w_ = ctx_overrides.pop("w", None) or pmlc.load_ws(golden_ws())
        pack = ctx_overrides.pop("pack", None) or fixture(name)
        ctx = R.RenderContext(**{"w": w_, "pack": pp.with_item_ids(pack), "run": RUN, "generated": R.build_date(),
                                 "embed": "cited", "eh": effective_handling(pack, w_), **ctx_overrides})
        return R.render(fmt, ctx)
    finally:
        if old is None:
            os.environ.pop("SOURCE_DATE_EPOCH", None)
        else:
            os.environ["SOURCE_DATE_EPOCH"] = old


@pytest.mark.parametrize("name", pack_fixtures() + ["all-kinds"])
def test_fixture_html_matches_golden(name):
    import hashlib
    data = render_fixture(name, "html")[0].data
    got = hashlib.sha256(data.encode("utf-8")).hexdigest()
    table = json.loads(HTML_GOLDEN.read_text(encoding="utf-8")) if HTML_GOLDEN.exists() else {}
    if os.environ.get("PMLC_UPDATE_GOLDEN"):
        table[name] = got
        HTML_GOLDEN.write_text(json.dumps(dict(sorted(table.items())), indent=1) + "\n", encoding="utf-8")
    assert table.get(name) == got, f"{name}: HTML differs from html-golden.json (PMLC_UPDATE_GOLDEN=1, then review)"


@pytest.mark.parametrize("name", pack_fixtures())
def test_fixture_belongs_to_a_skill(name):
    assert fixture(name)["pack"] == name
    assert skill_of(name) in ALL_WAVES, f"{name}: add its skill to a wave list, or a `skill` field to the fixture"


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
    assert f'<p class="status">{STATUS}' in t and f"<footer>{html.escape(pmlc.BRAND)}</footer>" in t   # A14: in place
    assert "This pack cites 2 of 2 relevant findings." in t and 'class="trail"' in t
    assert pmlc.PAGE_TOKENS_CSS in t and pmlc.WIDE_CSS in t and "function init()" in t and ".rail{" in t
    assert "Synthetic pump fire" in t and "2024-03-20" in t and "generated 2026-10-16" in t


def test_pack_brand_in_pack_data(w):
    t = pp.render_pack_html(w, pack_with(item("para")), "r", "2026-10-16")
    assert _pack_data(t)["brand"]["status_phrase"] == pmlc.STATUS_PHRASE == STATUS


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


def test_pack_cli_refuses_a_failing_pack(ws, tmp_path):  # noqa: F811
    bad = tmp_path / "b.json"
    bad.write_text(json.dumps(pack_with(item("para"), status="Draft")), encoding="utf-8")
    r = run_fail("pack", str(ws), str(bad), "--out", str(tmp_path / "o"))
    assert "status: must contain" in r.stderr and "Nothing written." in r.stderr
    assert not (tmp_path / "o").exists()


def test_pack_cli_no_md(ws, tmp_path):  # noqa: F811
    good = tmp_path / "p.json"
    good.write_text(json.dumps(pack_with(item("para", cites=["FND-0002"]))), encoding="utf-8")
    run("pack", str(ws), str(good), "--out", str(tmp_path / "o"), "--no-md")
    assert (tmp_path / "o" / "test-pack.html").exists() and not (tmp_path / "o" / "test-pack.md").exists()


def test_pack_on_minimal_workspace(ws, tmp_path):  # noqa: F811
    lone = tmp_path / "lone"
    lone.mkdir()
    (lone / "findings.json").write_text((ws / "findings.json").read_text(encoding="utf-8"), encoding="utf-8")
    good = tmp_path / "p.json"
    good.write_text(json.dumps(pack_with(item("para", cites=["FND-0002"]))), encoding="utf-8")
    run("pack", str(lone), str(good))
    assert (lone / "outputs" / "test-pack.html").exists()   # default folder for a legacy workspace


@pytest.mark.parametrize("skill", [s for s in ALL_WAVES if PACK_OF.get(s, s) in pack_fixtures()])
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
    sem = release.semver(VERSION)  # the manifests carry the semver form of the PEP 440 __version__ (ruling 25)
    for p in (".claude-plugin/plugin.json", ".claude-plugin/marketplace.json"):
        assert f'"version": "{sem}"' in (ROOT / p).read_text(encoding="utf-8"), p


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
    assert ("This pack cites 1 of 1 relevant findings.\n\n1 of 1 top-rated relevant findings cited.\n\n"
            "Left out on purpose:\n"
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
    assert ("- 2022-03 (24 months before): Local seal purchases begin *(weak signal)* [FND-0003]\n  - Received by: Stores (T1)\n"
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


def test_causal_item_cli(ws, tmp_path):  # noqa: F811                                                  # review focus 4
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


def test_every_skill_but_the_router_and_register_has_a_pack():
    skills = {p.parent.name for p in (ROOT / "skills").glob("*/SKILL.md")} - {"learnings-coach", "learnings-register"}
    assert skills == set(ALL_WAVES)
    assert [s for s in skills if PACK_OF.get(s, s) not in pack_fixtures()] == []


def test_docs_no_longer_describe_markdown_only_skills():
    for p in ("AGENTS.md", "skills/learnings-coach/SKILL.md", "skills/learnings-coach/references/output-style.md"):
        t = (ROOT / p).read_text(encoding="utf-8")
        assert "write Markdown there" not in t and "save Markdown under" not in t, p
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    assert "(Mermaid)" not in readme and "follow in 0.3.3" not in readme
    # "so far" is allowed only once: in the v2.0 heading (guards stale "so far only write Markdown" wording)
    assert readme.count("so far") == 1
    assert [ln for ln in readme.splitlines() if "so far" in ln] == ["## What's new in v2.0 so far"]


# ----------------------------------------------------------------------------- 0.3.4 polish

def test_question_answer_and_put_to(w):
    q = item("question", why="Tests whether the cause is placed at the right level.", answer="L3 supervision.",
             good_evidence="Names supervision", to="Chief Executive", cites=["FND-0002"])
    assert problems(pack_with(q), w) == []
    md = pp.render_pack_md(pack_with(q), w)
    assert ("- Why it matters: Tests whether the cause is placed at the right level.\n- Answer: L3 supervision.\n"
            "- Good evidence looks like: Names supervision\n- Put to: Chief Executive") in md
    t = pp.render_pack_html(w, pack_with(q), "2024-03-20-pump-fire", "2026-10-16")
    assert '<span class="badge">Put to: Chief Executive</span>' in t
    assert '<span class="label">Answer</span><p>L3 supervision.</p>' in t
    assert "Ask:" not in md and "Ask:" not in t


def test_layout_graph_curves_skip_level_links_above_the_nodes():
    nodes = [{"id": "l4", "label": "L4"}, {"id": "l3", "label": "L3"}, {"id": "l1", "label": "L1"}]
    g = pp.layout_graph(nodes, [{"from": "l4", "to": "l3"}, {"from": "l3", "to": "l1"}, {"from": "l4", "to": "l1"}],
                        uid="s")["svg"]
    skips = re.findall(r'<path class="edge skip" d="M(\d+),(\d+) C\d+,(\d+) ', g)
    assert len(skips) == 1                                        # only l4 -> l1 skips a layer
    top = min(int(y) for y in re.findall(r'transform="translate\(\d+,(\d+)\)', g))
    sx, sy, cy = map(int, skips[0])
    assert sy == top and cy < top                                 # leaves the node's top edge and arcs above it
    assert len(re.findall(r'<path class="edge" ', g)) == 2        # the chain stays straight
    plain = pp.layout_graph(nodes[:2], [{"from": "l4", "to": "l3"}], uid="p")["svg"]
    assert "skip" not in plain and f'translate({pp.PAD},{pp.PAD})' in plain   # no extra room without a skip


def test_consecutive_checks_form_one_tight_list(w):
    p = pack_with(item("check", text="Isolate the pump."), item("check", text="Record the test.", when="before restart"),
                  item("para", text="Then hand over."), item("check", text="Sign the permit."))
    md = pp.render_pack_md(p, w)
    assert "- [ ] Isolate the pump.\n- [ ] Record the test. *(before restart)*\n\nThen hand over.\n\n- [ ] Sign" in md


def test_scope_tags(w):
    assert problems(pack_with(item("para"), scope={"tags": ["emergency"]}), w) == []
    assert "scope.tags: nonsense is not a tag in clusters.json" in problems(
        pack_with(item("para"), scope={"tags": ["nonsense"]}), w)
    assert any(x.startswith("scope.tags: a list of tags") for x in problems(pack_with(item("para"), scope={"tags": "x"}), w))
    assert "FND-0004" in pp.relevant_findings(w, {"tags": ["emergency"]})
    w2 = dict(w)
    del w2["clusters"]
    got = problems(pack_with(item("para"), scope={"tags": ["emergency"]}), w2)
    assert any(x.startswith("scope: tiers, entities and tags need clusters.json") for x in got)
    w3 = copy.deepcopy(w)
    del w3["clusters"]["taxonomy"]["tags"]
    got = problems(pack_with(item("para"), scope={"tags": ["emergency"]}), w3)
    assert any("Re-run classify" in x for x in got)


def test_scope_top_and_relations(w):
    top = {f["id"] for f in w["findings"] if f["rating"] == 4}
    assert set(pp.relevant_findings(w, {"min_rating": "top"})) == top
    assert problems(pack_with(item("para"), scope={"min_rating": "top"}), w) == []
    got = problems(pack_with(item("para"), scope={"relations": ["nonsense"]}), w)
    assert any(x.startswith("scope.relations") for x in got)
    assert problems(pack_with(item("para"), scope={"relations": ["owner"], "entity_mode": "all"}), w) == []
    got = problems(pack_with(item("para"), scope={"entity_mode": "both"}), w)
    assert any(x.startswith("scope.entity_mode") for x in got)


def test_event_when():
    assert pp.event_when({"date": "2015"}, None) == "c. 2015"
    assert pp.event_when({"date": "2019-03"}, None) == "2019-03"
    assert pp.event_when({"date": "2019-03-04", "time": "14:05"}, None) == "2019-03-04 14:05"
    assert pp.event_when({"date": "2019-03"}, "2020-09-24") == "2019-03 (18 months before)"
    assert pp.event_when({"date": "2015"}, "2020-09-24") == "c. 2015 (about 5 years before)"
    assert pp.event_when({"date": "2019"}, "2020-09-24") == "c. 2019 (about 1 year before)"
    assert pp.event_when({"date": "2020"}, "2020-09-24") == "c. 2020"
    assert pp.event_when({"date": "2020-09-10"}, "2020-09-24") == "2020-09-10"
    assert pp.event_when({"date": "2021-01-01"}, "2020-09-24") == "2021-01-01"


def test_pack_renders_months_before(w):
    ev = [{"date": "2022", "text": "Year only"}, {"date": "2024-03-20", "time": "14:05", "text": "Alarm"}]
    p = pack_with(item("timeline", events=ev))
    md = pp.render_pack_md(p, w)
    assert "- c. 2022 (about 2 years before): Year only" in md and "- 2024-03-20 14:05: Alarm" in md
    assert "<time>c. 2022 (about 2 years before)</time>" in pp.render_pack_html(w, p, "r", "d")
    p["incident"] = {"date": "2024-05-20"}
    assert "- 2024-03-20 14:05 (2 months before): Alarm" in pp.render_pack_md(p, w)


def test_pack_unlinked_evidence_warns(w):
    r = pp.check_pack(pack_with(item("card", cites=["FND-0002", "EVD-0003"])), w)
    assert any("EVD-0003 is not linked to any finding this item cites" in x for x in r.warnings)
    assert not r.problems
    ok = pp.check_pack(pack_with(item("card", cites=["FND-0003", "EVD-0003"])), w)
    assert not any("is not linked" in x for x in ok.warnings)
    only_evd = pp.check_pack(pack_with(item("test_point")), w)
    assert not any("is not linked" in x for x in only_evd.warnings)


def test_pack_downgraded_needs_note(w):
    w2 = dict(w, incident=dict(w["incident"], review_votes=[{"finding": "FND-0004", "vote": "downgrade"}]))
    p = pack_with(item("learning", cites=["FND-0004"]))
    r = pp.check_pack(p, w2)
    assert any("cites FND-0004, which has a reviewer downgrade vote; add a data_quality note" in x for x in r.problems)
    p["data_quality"] = [{"text": "Reviewer doubted this finding.", "cites": ["FND-0004"]}]
    assert not any("downgrade vote" in x for x in pp.check_pack(p, w2).problems)
    p2 = pack_with(item("learning"), bottom_line=[{"text": "x", "cites": ["FND-0004"]}])
    assert any("bottom_line" in x and "downgrade vote" in x for x in pp.check_pack(p2, w2).problems)
    # A27: every citation route counts, not only cites
    dv = lambda pk: [x for x in pp.check_pack(pk, w2).problems if "downgrade vote" in x]   # noqa: E731
    sup = pack_with(item("para", supporting_cites=["FND-0004"]))
    assert any("supporting_cites" in x for x in dv(sup)), dv(sup)
    rows = pack_with(item("table", row_cites=[["FND-0004"]]))
    assert any("row_cites" in x for x in dv(rows)), dv(rows)
    inline = pack_with(item("para", text="See [FND-0004] for the seal."))
    assert any("FND-0004" in x for x in dv(inline)), dv(inline)
    ev = pack_with(item("para", text="Seal photo [EVD-0001] shows wear."))
    assert pp.cited_ids(ev)[1] == ["EVD-0001"]
    assert not any("EVD-0001" in x for x in pp.check_pack(ev, w2).problems)
    rows["data_quality"] = [{"text": "Reviewer doubted this finding.", "cites": ["FND-0004"]}]
    assert dv(rows) == []


# ---- phase 2, task 11: wording and the two new optional fields
SKILLS = ROOT / "skills"


def test_card_organisation_changing_warning(w):
    t1 = pack_with(item("card"), scope={"tiers": ["T1"]})
    res = pp.check_pack(t1, w)
    assert res.problems == []
    assert any(x.startswith("card ") and x.endswith(": add organisation_changing (what the organisation is changing)")
               for x in res.warnings), res.warnings
    ok = pack_with(item("card", organisation_changing="Procedures now require a design-pressure test."),
                   scope={"tiers": ["T1"]})
    assert not any("organisation_changing" in x for x in pp.check_pack(ok, w).warnings)
    t2 = pack_with(item("card"), scope={"tiers": ["T2"]})
    assert not any("organisation_changing" in x for x in pp.check_pack(t2, w).warnings)
    assert problems(pack_with(item("card", organisation_changing="")), w)
    md = pp.render_pack_md(ok, w)
    assert "**What the organisation is changing:** Procedures now require a design-pressure test." in md
    assert "What the organisation is changing" in pp.render_pack_html(w, ok, "r", "d")


def test_timeline_knowable_then_accepted_and_rendered(w):
    ev = [{"date": "2022-03", "text": "Local seal purchases begin", "knowable_then": "Stores held the purchase record.",
           "cites": ["FND-0003"]},
          {"date": "2024-03-12", "text": "Seal changed", "knowable_then": False, "cites": ["FND-0003"]}]
    p = pack_with(item("timeline", events=ev))
    assert pp.check_pack(p, w).problems == []
    md = pp.render_pack_md(p, w)
    assert "Knowable then: Stores held the purchase record." in md and "Knowable then: no" in md
    h = pp.render_pack_html(w, p, "r", "d")
    assert "Knowable then: Stores held the purchase record." in h and "Knowable then: no" in h
    for bad_v in ("", 3):
        q = pack_with(item("timeline", events=[{"date": "2022", "text": "x", "knowable_then": bad_v}]))
        assert any("events[0].knowable_then: must be true, false or text" in x for x in problems(q, w))


def test_register_trigger_no_regulator_invite():
    t = (SKILLS / "learnings-register" / "SKILL.md").read_text(encoding="utf-8")
    desc = re.search(r"^description:\s*(.+)$", t, re.M).group(1)
    assert not re.search(r"(?i)share with .*regulator", desc)
    assert "regulator" not in desc.lower()
    assert "Sharing outside the organisation" in t


def test_hub_sign_off_rule():
    t = (SKILLS / "learnings-coach" / "SKILL.md").read_text(encoding="utf-8")
    assert "never run sign-off unless" in t
    assert "check-language" in t and "--share" in t and "--embed cited|full" in t


def test_principles_sections():
    t = (SKILLS / "learnings-coach" / "references" / "learning-principles.md").read_text(encoding="utf-8")
    for h in ("1a. Hindsight", "Interviews in a just culture"):
        assert re.search(rf"^#+ .*{re.escape(h)}", t, re.M), h
    assert '"failed to X" | "X was not done; the system did not require or support X"' in t
    assert "owns the change" in t
    heads = re.findall(r"^## (.+)$", t, re.M)
    assert "7. Review status and draft learnings" in heads
    i = heads.index("7. Review status and draft learnings")
    assert heads[i - 1].startswith("6. ") and heads[i + 1:] == ["Interviews in a just culture", "Quasi-identifiers"]
    common = (SKILLS / "learnings-coach" / "references" / "skill-common.md").read_text(encoding="utf-8")
    sec = common.split("## 7. Sharing outside the organisation", 1)[1].split("\n## ", 1)[0]   # moved here (P2-13)
    for x in ("legal review", "--share external", "--embed summary", "client-safe", "privilege"):
        assert x in sec, x


def test_supervisor_no_enforce_habit():
    t = (SKILLS / "supervisor-coach" / "SKILL.md").read_text(encoding="utf-8")
    assert not re.search(r"(?i)\benforce\b", t)
    assert "Make the safe way the easy way" in t


# ----------------------------------------------------------------------------- Task 7: --embed and print only cited

STUB_KEYS = {"id", "label", "rating"}


def _trail_ids(t):
    m = re.search(r'<section class="trail">(.*?)</section>', t, re.S)
    assert m, "no print trail"
    return re.findall(r"<dt>([^<]+)</dt>", m.group(1))


def test_embed_default_is_cited(w):
    p = pack_with(item("para", cites=["FND-0002"]), exclusions=[{"id": "FND-0004", "reason": "out of scope"}])
    d = pp.build_pack_data(w, p, "r")
    assert d == pp.build_pack_data(w, p, "r", embed="cited")
    assert list(d["findings"]) == ["FND-0002", "FND-0003", "FND-0004"]
    assert "short" in d["findings"]["FND-0002"] and "clusters" in d["findings"]["FND-0002"]
    for x in ("FND-0003", "FND-0004"):                    # uncovered and excluded: label-only stubs
        assert set(d["findings"][x]) == STUB_KEYS, d["findings"][x]
    assert d["findings"]["FND-0003"]["label"] == "Seals bought locally without specification"
    assert list(d["evidence"]) == []                      # nothing cited, nothing embedded
    q = pack_with(item("para", cites=["FND-0002", "EVD-0001"]))
    assert list(pp.build_pack_data(w, q, "r")["evidence"]) == ["EVD-0001"]
    assert _pack_data(pp.render_pack_html(w, p, "r", "d"))["findings"]["FND-0003"].keys() == STUB_KEYS


def test_embed_full_matches_previous_behaviour(w):
    p = pack_with(item("para", cites=["FND-0002", "EVD-0001"]), exclusions=[{"id": "FND-0004", "reason": "x"}])
    fids, eids = pp.cited_ids(p)
    uncited = [x for x in pp.relevant_findings(w, p.get("scope")) if x not in fids]
    f, e = pmlc.citation_records(w, fids + uncited + pp.excluded_ids(p), eids)
    assert pp.build_pack_data(w, p, "r", embed="full") == {"pack": "test-pack", "run": "r", "findings": f,
                                                          "evidence": e, "brand": pmlc.brand_payload()}
    with pytest.raises(ValueError):
        pp.build_pack_data(w, p, "r", embed="everything")


def _marked(w):
    """A copy of the workspace with unique markers in every field --embed summary must drop."""
    w2 = copy.deepcopy(w)
    for e in w2["evidence"].values():
        e["description"] = f"MARK-DESC-{e['id']}"
        for n, ln in enumerate(e["links"]):
            ln["reference"] = f"MARK-REF-{e['id']}-{n}"
        e["Specific Reference"] = f"MARK-SR-{e['id']}"
    for f in w2["findings"]:
        f["key_questions"], f["suggested_interviews"] = f"MARK-KQ-{f['id']}", f"MARK-SI-{f['id']}"
        f["specific_reference"] = f"MARK-SR-{f['id']}"
        f["justification"] += " Source: MARK-REF-EVD-0001-0 (p.3)."     # AI justifications quote the evidence
    w2["incident"]["review_votes"] = [{"finding": "FND-0002", "vote": "upgrade", "reason": "MARK-VOTE-reason"}]
    return w2


def test_embed_summary_leaks_no_quotes(w):
    """Review Focus 5: the whole HTML string (JSON payload, print trail, title) holds no description or quote."""
    w2 = _marked(w)
    p = pack_with(item("para", cites=["FND-0002", "EVD-0001", "EVD-0002"]),
                  item("card", cites=["FND-0001", "EVD-0001"]))
    cited = pp.render_pack_html(w2, p, "r", "d")
    assert "MARK-DESC-EVD-0001" in cited and "MARK-REF-EVD-0001-0" in cited and "MARK-VOTE-reason" in cited
    assert "MARK-KQ-FND-0002" in cited                    # cited mode keeps them: the markers are reachable
    t = pp.render_pack_html(w2, p, "r", "d", embed="summary")
    assert "MARK-" not in t, re.findall(r"MARK-[\w-]+", t)
    d = _pack_data(t)
    assert set(d["evidence"]) == {"EVD-0001", "EVD-0002"} and d["evidence"]["EVD-0001"]["type"] == "document"
    assert d["findings"]["FND-0002"]["votes"] == [{"finding": "FND-0002", "vote": "upgrade"}]
    assert "MARK-" not in pp.render_pack_md(p, w2)
    assert d["findings"]["FND-0002"]["justification"].endswith(f"Source: {pmlc.QUOTE_OMITTED} (p.3).")
    assert set(_trail_ids(t)) == {"FND-0002", "FND-0001", "EVD-0001", "EVD-0002"}


def test_print_trail_only_cited(w):
    p = pack_with(item("para", cites=["FND-0002", "EVD-0002"]), exclusions=[{"id": "FND-0004", "reason": "x"}])
    for mode in pp.EMBED_MODES:
        t = pp.render_pack_html(w, p, "r", "d", embed=mode)
        assert _trail_ids(t) == ["FND-0002", "EVD-0002"], mode


def test_uncovered_print_line(w):
    t = pp.render_pack_html(w, pack_with(item("para", cites=["FND-0002"])), "r", "d")
    assert '<p class="printonly">1 of 2 relevant findings cited</p>' in t
    assert '<details class="noprint"><summary>Not covered here (1)</summary>' in t     # the screen keeps the list
    assert '<p class="noprint">This pack cites 1 of 2 relevant findings.</p>' in t
    js = (pmlc.DASHBOARD_ASSETS / "pack.js").read_text(encoding="utf-8")
    assert 'querySelectorAll("main details:not(.rail):not(.noprint)")' in js
    css = (pmlc.DASHBOARD_ASSETS / "pack.css").read_text(encoding="utf-8")
    assert ".printonly{display:none}" in css and ".noprint{display:none!important}" in css
    assert "1 of 1 relevant findings cited" in pp.render_pack_html(w, pack_with(item("para", cites=["FND-0002"]),
                                                                              exclusions=EX), "r", "d")


def _run_with_evidence_type(tmp_path, etype, *flags):
    tmp_path.mkdir(parents=True)
    x = make_export(tmp_path)
    run("ingest", str(x), "--slug", "pump-fire")
    ws_ = tmp_path / "pmlc-runs" / "2024-03-20-pump-fire" / "workspace"
    run("classify", str(ws_))
    ev = json.loads((ws_ / "evidence.json").read_text(encoding="utf-8"))
    ev["EVD-0001"]["type"] = etype
    (ws_ / "evidence.json").write_text(json.dumps(ev), encoding="utf-8")
    src = tmp_path / "p.json"
    src.write_text(json.dumps(pack_with(item("para", cites=["FND-0001", "EVD-0001"]))), encoding="utf-8")
    return subprocess.run([sys.executable, str(ROOT / "skills" / "learnings-coach" / "scripts" / "pmlc.py"), "pack",
                           str(ws_), str(src), "--no-md", *flags], capture_output=True, text=True)


WITNESS_NOTE = "note: embedded evidence includes witness statements; consider --embed summary"


def test_witness_note(tmp_path):
    r = _run_with_evidence_type(tmp_path / "a", "Witness_Statement")
    assert r.returncode == 0, r.stderr
    assert WITNESS_NOTE in r.stderr
    r = _run_with_evidence_type(tmp_path / "b", "document")
    assert r.returncode == 0 and WITNESS_NOTE not in r.stderr
    r = _run_with_evidence_type(tmp_path / "c", "witness statement", "--embed", "summary")
    assert r.returncode == 0 and WITNESS_NOTE not in r.stderr     # summary drops the statements' text
    assert pmlc.witness_note({"E": {"type": "WITNESS"}}) and not pmlc.witness_note({"E": {"type": None}})


def test_pack_cli_embed_flag(ws, tmp_path):  # noqa: F811
    good = tmp_path / "p.json"
    good.write_text(json.dumps(pack_with(item("para", cites=["FND-0002"]))), encoding="utf-8")
    run("pack", str(ws), str(good), "--out", str(tmp_path / "o"), "--no-md", "--embed", "full")
    d = _pack_data((tmp_path / "o" / "test-pack.html").read_text(encoding="utf-8"))
    assert "short" in d["findings"]["FND-0003"]
    run("pack", str(ws), str(good), "--out", str(tmp_path / "o"), "--no-md")
    d = _pack_data((tmp_path / "o" / "test-pack.html").read_text(encoding="utf-8"))
    assert set(d["findings"]["FND-0003"]) == STUB_KEYS
    r = run_fail("pack", str(ws), str(good), "--embed", "all")
    assert "invalid choice" in r.stderr


def test_lint_ok_reason_is_rendered(w):
    it = item("para", text="The restart was unlawful under the plant rules.", cites=["FND-0002"],
              lint_ok={"rule": "JC5", "reason": "quoting the <b>rule</b> title & number"})
    p = pack_with(it)
    r = pp.check_pack(p, w)
    assert r.problems == [] and not [x for x in r.warnings if "unknown field" in x], r
    t = pp.render_pack_html(w, p, "r", "d")
    assert ('<p class="lint-ok">Language check JC5 accepted: quoting the &lt;b&gt;rule&lt;/b&gt; title &amp; number</p>'
            in t)
    md = pp.render_pack_md(p, w)
    assert "*Language check JC5 accepted: quoting the \\<b\\>rule\\</b\\> title & number*" in md      # A42: escaped
    two = pack_with(item("para", text="x", cites=["FND-0002"], lint_ok=[{"rule": "JC5", "reason": "a"},
                                                                       {"rule": "JC1", "reason": "b"}]))
    t2 = pp.render_pack_html(w, two, "r", "d")
    assert "Language check JC5 accepted: a" in t2 and "Language check JC1 accepted: b" in t2
    bl = pack_with(item("para", cites=["FND-0002"]),
                   bottom_line=[{"text": "t", "cites": ["FND-0002"], "lint_ok": {"rule": "JC5", "reason": "why"}}])
    assert "Language check JC5 accepted: why" in pp.render_pack_html(w, bl, "r", "d")
    assert "Language check JC5 accepted: why" in pp.render_pack_md(bl, w)


def test_readme_alpha_pin():
    """M5: the alpha notice also says how to stay on the tested alpha.3."""
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    head = readme.split("\n\n", 2)[1]
    assert "#v0.3.5" in head
    assert "/plugin marketplace add ashley-eyekyam/probematrix-learnings-coach#v2.0.0-alpha.3" in head


# ---- phase 3, task 18: tiers_in_scope branches (A19)
def test_tiers_in_scope_branches():
    assert pp.tiers_in_scope({"scope": {"tiers": ["T1", "T2"]}}) == ["T1", "T2"]
    for bad in (None, [], "x", {}, {"scope": None}, {"scope": "T1"}, {"scope": {}}, {"scope": {"tiers": "T1"}},
                {"scope": {"tiers": None}}):
        assert pp.tiers_in_scope(bad) == [], bad


def test_tiers_in_scope_drives_the_t1_card_warning(w):
    card = item("card")
    assert any("organisation_changing" in x for x in pp.check_pack(pack_with(card, scope={"tiers": ["T1"]}), w).warnings)
    for sc in ({"tiers": "T1"}, "T1", None):
        assert not any("organisation_changing" in x for x in pp.check_pack(pack_with(item("card"), scope=sc), w).warnings)


# ---- v2.0 phase 3, task 10: pack profiles, --strict, top-rated coverage, padding, scope drift (P3-5, P3-7)

import pmlc_lib.pack.profiles as profiles  # noqa: E402


def _board_with_questions(n):
    p = fixture("board-brief")
    pool = [["FND-0002"], ["FND-0003"], ["FND-0002", "EVD-0002"], ["FND-0003", "EVD-0003"], ["FND-0002", "FND-0003"],
            ["FND-0003", "EVD-0001"], ["FND-0001", "FND-0002"]]
    qs = [dict(MIN["question"], kind="question", question=f"Question {i}?", cites=pool[i % len(pool)]) for i in range(n)]
    next(s for s in p["sections"] if s["id"] == "questions")["items"] = qs
    return p


def test_profile_violation_warns_then_strict_fails(w, ws, tmp_path):  # noqa: F811
    p = _board_with_questions(13)                           # ruling X25 (L2-17): up to 12, at least 1
    msg = "section questions: 13 question items, expected 1-12"
    r = pp.check_pack(p, w)
    assert msg in r.warnings and msg not in r.problems
    assert msg in pp.check_pack(p, w, strict=True).problems
    f = tmp_path / "board-brief.json"
    f.write_text(json.dumps(p), encoding="utf-8")
    assert f"warning: {msg}" in run("check-pack", str(ws), str(f))
    r = run_fail("check-pack", str(ws), str(f), "--strict")
    assert r.returncode == 1 and msg in r.stderr


def seeded(w, name):
    """The workspace a fixture's strict check needs: a skill that requires nine-m-seed (nine-m-analysis, whose
    nine-m-cites rule reads it) gets the seed of the synthetic workspace, as `nine-m-seed <ws>` writes it."""
    m = json.loads((ROOT / "skills" / skill_of(name) / "skill.json").read_text(encoding="utf-8"))
    if "nine-m-seed" not in m["requires"]:
        return w
    from pmlc_lib.ninem import seed
    return dict(w, nine_m_seed=seed(w))


@pytest.mark.parametrize("name", pack_fixtures())
def test_all_fixtures_pass_strict(w, name):
    r = pp.check_pack(fixture(name), seeded(w, name), strict=True)
    assert r.problems == [], r.problems


def test_coverage_counts_top_rated(w):
    p = pack_with(item("para", cites=["FND-0002"]), scope={"levels": [1, 2, 3, 4]})
    rel = pp.relevant_findings(w, p["scope"])
    top = max(f["rating"] for f in w["findings"] if f["id"] in rel)
    n_top = sum(1 for f in w["findings"] if f["id"] in rel and f["rating"] == top)
    cov = pp.coverage(w, p)
    assert cov["top_relevant"] == n_top == 2 and cov["top_cited"] == 1
    md = pp.render_pack_md(p, w)
    t = pp.render_pack_html(w, p, "r", "d")
    for doc in (md, t):
        assert "1 of 2 top-rated relevant findings cited" in doc
    assert "This pack cites 1 of 4 relevant findings." in md
    assert '<p class="printonly">1 of 4 relevant findings cited</p>' in t


def test_coverage_warning_uses_top_rated(w):
    p = pack_with(item("para", cites=["FND-0002", "FND-0003"]), scope={"levels": [1, 2, 3, 4]},
                  bottom_line=[{"text": "Test before service.", "cites": ["FND-0002"]}])
    assert pp.coverage(w, p)["cited"] == 2 and pp.coverage(w, p)["relevant"] == 4
    assert not any(x.startswith("coverage") for x in pp.check_pack(p, w).warnings)
    thin = pack_with(item("para", cites=["FND-0001"]), scope={"levels": [1, 2, 3, 4]},
                     bottom_line=[{"text": "Test before service.", "cites": ["FND-0001"]}])
    assert any("under a quarter of the top-rated relevant findings are cited" in x
               for x in pp.check_pack(thin, w).warnings)


def test_coverage_floor_comes_from_the_profile(w, monkeypatch):
    p = pack_with(item("para", cites=["FND-0002"]))                  # 1 of 2 top-rated: half
    assert not any(x.startswith("coverage") for x in pp.check_pack(p, w).warnings)
    monkeypatch.setattr(profiles, "profile_for", lambda name, profiles=None: {"coverage_floor": 0.75})
    assert any("under 75% of the top-rated relevant findings are cited (1 of 2)" in x
               for x in pp.check_pack(p, w).warnings)


def test_padding_warning(w):
    three = pack_with(*[item("para", text=f"t{i}", cites=["FND-0002", "FND-0001"]) for i in range(3)])
    msg = "items: 3 items share the same cites (FND-0001, FND-0002): possible padding"
    assert msg in pp.check_pack(three, w).warnings
    assert msg in pp.check_pack(three, w, strict=True).problems
    two = pack_with(*[item("para", text=f"t{i}", cites=["FND-0002", "FND-0001"]) for i in range(2)])
    assert not any("possible padding" in x for x in pp.check_pack(two, w).warnings)


def test_padding_counts_a_group_once_and_stays_in_one_section(w):                  # rulings X24, X26
    c = ["FND-0003"]
    triplet = [item("learning", group="Spares", cites=c), item("barrier", group="Spares", cites=c),
               item("recommendation", group="Spares", cites=c)]
    assert not any("possible padding" in x for x in pp.check_pack(pack_with(*triplet), w, strict=True).problems)
    three_groups = [item("para", text=f"t{g}", group=g, cites=c) for g in ("A", "B", "C")]
    assert "items: 3 items share the same cites (FND-0003): possible padding" in pp.check_pack(
        pack_with(*three_groups), w).warnings
    mixed = triplet + [item("para", text="u1", cites=c), item("para", text="u2", cites=c)]   # 1 group + 2 ungrouped
    assert "items: 5 items share the same cites (FND-0003): possible padding" in pp.check_pack(pack_with(*mixed), w).warnings
    across = pack_with(item("para", text="a", cites=c))
    across["sections"] += [{"id": f"s{k}", "heading": f"S{k}", "items": [item("para", text=f"x{k}", cites=c)]}
                           for k in (2, 3)]
    assert not any("possible padding" in x for x in pp.check_pack(across, w, strict=True).problems)
    e = fixture("engineering-integrity-learnings")                  # SKILL.md triplet, all citing FND-0003
    th = e["sections"][0]["items"]
    assert {tuple(it["cites"]) for it in th} == {("FND-0003",)} and len({it["group"] for it in th}) == 1
    assert pp.check_pack(e, w, strict=True).problems == []


def test_scope_drift_warning(w):
    p = fixture("supervisor-coach")
    msg = "scope: scope differs from the supervisor audience default (T2)"
    assert not any("scope differs" in x for x in pp.check_pack(p, w).warnings)
    for scope in ({"tiers": ["T1"]}, {"levels": [2]}, None):
        q = copy.deepcopy(p)
        if scope is None:
            del q["scope"]
        else:
            q["scope"] = scope
        assert msg in pp.check_pack(q, w).warnings, scope
        assert msg in pp.check_pack(q, w, strict=True).problems
    q = dict(copy.deepcopy(p), scope={"tiers": ["T2", "T3"]})       # widening keeps the default: no drift
    assert not any("scope differs" in x for x in pp.check_pack(q, w).warnings)
    b = fixture("board-brief")                                       # SKILL.md sets levels, audiences.json also T5
    assert not any("scope differs" in x for x in pp.check_pack(b, w).warnings)


def test_every_profile_names_a_fixture():
    assert sorted(profiles.load()) == pack_fixtures()


def test_profiles_have_the_contract_shape():
    for name, prof in profiles.load().items():
        assert set(prof) <= {"sections", "required_scope", "bottom_line", "word_limits", "coverage_floor", "rules",
                           "max_words", "lint_errors"}, name
        assert all(re.fullmatch(r"JC([1-9]|1[0-2])", x) for x in prof.get("lint_errors", [])), name
        for e in prof["sections"]:
            assert set(e) == {"id", "kinds", "min", "max"} and 0 <= e["min"] <= e["max"], (name, e)
            assert all(k in pp.KINDS for k in e["kinds"]), (name, e)
        assert all(r in profiles.RULES and not r.endswith(":") or r.startswith("same-sections-as:")
                   or r.startswith("banner:") and r.split(":", 1)[1] in profiles.BANNERS
                   for r in prof.get("rules", [])), name
    assert profiles.profile_for("dossier-F09b") is profiles.load()["dossier-F02"]
    assert profiles.profile_for("test-pack") is None and profiles.profile_for(None) is None


def _strict(p, w):
    return pp.check_pack(p, w, strict=True).problems


def test_profile_sections_kinds_and_bottom_line(w):
    p = fixture("supervisor-coach")
    p["sections"].append({"id": "extra", "heading": "Extra", "items": [item("para", cites=["FND-0002"])]})
    p["sections"][0]["items"].append(item("decision", cites=["FND-0003"]))
    p["sections"] = [s for s in p["sections"] if s["id"] != "coaching"]
    p["bottom_line"] = [{"text": f"b{i}", "cites": ["FND-0002"]} for i in range(6)]
    got = _strict(p, w)
    for m in ["section extra: not a section of the supervisor-coach profile",
              "section before-work: decision items do not belong here (expected check)",
              "section coaching: missing (scenario items, expected 1-3)",
              "bottom_line: 6 entries, expected 1-5"]:
        assert m in got, got
    m = fixture("manager-coach")
    m["sections"] = [s for s in m["sections"] if s["id"] == "summary"]
    assert "a section matching *: missing (learning items, expected 1-6)" in _strict(m, w)
    assert not any("expected" in x for x in _strict(_board_with_questions(1), w))     # one question is enough


def test_profile_required_scope_and_word_limit(w):
    p = fixture("frontline-learning-cards")
    del p["scope"]
    card = next(s for s in p["sections"] if s["id"] == "cards")["items"][0]
    card["what_happened"] = " ".join(["word"] * 260)
    got = _strict(p, w)
    assert "scope.tiers: required by the frontline-learning-cards profile" in got
    assert any(x.startswith(f"card {card.get('id', 'cards-1')}: ") and x.endswith("words, at most 250") for x in got)


def test_profile_rules(w):
    e = fixture("engineering-integrity-learnings")
    e["sections"][0]["items"] = [it for it in e["sections"][0]["items"] if it["kind"] != "barrier"]
    e["sections"][0]["items"][0].pop("group")
    got = _strict(e, w)
    assert any("a learning needs a group shared with its learning, barrier and recommendation" in x for x in got)
    assert any(x.startswith("group ") and "(missing learning, barrier)" in x for x in got), got
    t = fixture("training-designer")
    q = next(s for s in t["sections"] if s["id"] == "assessment")["items"][0]
    q.pop("answer")
    q.pop("cites")
    got = _strict(t, w)
    assert any("an assessment question needs an answer" in x for x in got)
    assert any("an assessment question needs cites" in x for x in got)
    i = fixture("investigator-coach")
    fu = next(it for s in i["sections"] for it in s["items"] if it.get("id") == "follow-up")
    fu["rows"], fu["row_cites"] = fu["rows"][:1], fu["row_cites"][:1]
    assert "follow-up: no row for top-rated finding(s) FND-0003" in _strict(i, w)
    assert profiles.check(i, profiles.load()["investigator-coach"]) == []         # no workspace: rule skipped


def test_profile_same_sections_rule_and_unknown_rule(w):
    base = {"sections": [{"id": "basis", "kinds": ["para"], "min": 1, "max": 99}]}
    prof = {"rules": ["same-sections-as:base", "same-sections-as:nope", "frobnicate"], "sections": base["sections"]}
    p = pack_with(item("para", cites=["FND-0002"]))
    got = profiles.check(p, prof, w, profiles={"base": base})
    assert "sections: must be the same sections as base (basis), got s1" in got
    assert "rules: same-sections-as:nope names no profile" in got
    assert "rules: unknown profile rule 'frobnicate'" in got
    p["sections"][0]["id"] = "basis"
    assert not any(x.startswith("sections:") for x in profiles.check(p, prof, w, profiles={"base": base}))
    assert profiles.check("not a pack", prof) == [] and profiles.check(p, None) == []


def test_comparison_variants_keep_the_main_sections(w):
    """Task 21 (L7-12; Task 10 M-8): the client-safe and regulator-safe copies have report-comparison's sections, in
    order (same-sections-as), and pass check-pack --share external --strict."""
    main = [s["id"] for s in fixture("report-comparison")["sections"]]
    for v in ("report-comparison-client-safe", "report-comparison-regulator-safe"):
        p = fixture(v)
        assert [s["id"] for s in p["sections"]] == main, v
        assert pp.check_pack(p, w, share="external", strict=True).problems == [], v
        p["sections"] = p["sections"][1:]
        assert any(x.startswith("sections: must be the same sections as report-comparison")
                   for x in _strict(p, w)), v
    t = json.dumps(fixture("report-comparison-regulator-safe")).lower()
    assert "additional learning" in t and "statutory" in t and "legal review" in t
    assert "missed" not in t and "deficien" not in t


def test_recommendation_co_owner_is_rendered(w):
    """Task 21 (interface-learnings): a joint fix's co_owner shows in the Markdown and the HTML."""
    p = fixture("interface-learnings")
    assert "- Owner: Materials Management (F06)\n- Co-owner: Mechanical Maintenance (F02)\n" in pp.render_pack_md(p, w)
    t = pp.render_pack_html(w, p, "2024-03-20-pump-fire", "2026-10-16")
    assert "Co-owner" in t and "Emergency Planning &amp; Command (F09b)" in t


def test_check_pack_manual_documents_strict():
    doc = (ROOT / "docs" / "manual" / "commands" / "check-pack.md").read_text(encoding="utf-8")
    assert "--strict" in doc and "pack-profiles.json" in doc and "top-rated relevant findings cited" in doc


@pytest.mark.parametrize("bad", [{"kind": ["para"]}, "x", {"kind": "para", "cites": "FND-0002"}])
def test_profile_checks_never_crash_on_wrong_types(w, bad):
    p = fixture("engineering-integrity-learnings")
    p["sections"][0]["items"].append(bad)
    p["sections"].append({"id": "x", "heading": "h", "items": "nope"})
    p["scope"] = {"tags": "engineering"}
    r = pp.check_pack(p, w, strict=True)
    assert r.problems


# ---- v2.0 phase 3, task 11: LR ids, clauses, gaps and limits, why-not-stronger (P3-12, P3-13, L3-14)

MINI_REGISTER = {"entries": [{"lr_id": "LR-01", "title": "Test what you disturb"},
                             {"lr_id": "LR-02", "title": "Specify critical spares"}]}


def _fresh_run(tmp_path):
    x = make_export(tmp_path)
    run("ingest", str(x), "--slug", "pump-fire")
    ws_ = tmp_path / "pmlc-runs" / "2024-03-20-pump-fire" / "workspace"
    run("classify", str(ws_))
    return ws_, ws_.parent / "outputs"


def alpha4_copy(p):
    """The pack as alpha.4 wrote it: the Phase 3 optional ids (item and bottom-line `learning` and `clauses`) removed,
    since audience fixtures now carry register learnings (Tasks 21-23)."""
    p = copy.deepcopy(p)
    for x in [*(p.get("bottom_line") or []), *(it for s in p.get("sections") or [] for it in s.get("items") or [])]:
        if isinstance(x, dict):
            if isinstance(x.get("learning"), str):
                del x["learning"]
            x.pop("clauses", None)
    return p


@pytest.mark.parametrize("name", pack_fixtures() + ["all-kinds"])
def test_alpha4_pack_passes_without_new_fields(w, name):
    r = pp.check_pack(alpha4_copy(fixture(name)), w)
    assert r.problems == [], r.problems
    assert not [x for x in r.warnings if "learning ids not verified" in x or "unknown clause" in x]


MINI_REGISTER_FILE = ROOT / "tests" / "fixtures" / "registers" / "mini-register.json"


@pytest.mark.parametrize("name", pack_fixtures())
def test_fixture_learning_ids_in_mini_register(w, name):
    """Fixture `learning` values name learnings of the mini register (skill-common.md section 3) and strict checks
    pass with no learning warning (Tasks 21 and 23, merged)."""
    reg = json.loads(MINI_REGISTER_FILE.read_text(encoding="utf-8"))
    r = pp.check_pack(fixture(name), seeded(w, name), register=reg, strict=True)
    assert r.problems == [], r.problems
    assert not [x for x in r.warnings if "learning" in x], r.warnings


def test_learning_id_checked_against_register(w):
    p = pack_with(item("para", cites=["FND-0002"], learning="LR-99"))
    r = pp.check_pack(p, w, register=MINI_REGISTER)
    assert r.problems == [] and "sections[0].items[0].learning: unknown learning LR-99" in r.warnings, r
    r = pp.check_pack(p, w, register=MINI_REGISTER, strict=True)
    assert "sections[0].items[0].learning: unknown learning LR-99" in r.problems
    ok = pack_with(item("para", cites=["FND-0002"], learning="LR-01"))
    r = pp.check_pack(ok, w, register=MINI_REGISTER, strict=True)
    assert r.problems == [] and not [x for x in r.warnings if "learning" in x], r
    two = pack_with(item("para", cites=["FND-0002"], learning="LR-01"), item("para", cites=["FND-0002"], learning="LR-02"))
    r = pp.check_pack(two, w)
    assert [x for x in r.warnings if "learning ids not verified" in x] == ["learning ids not verified: no register"]
    assert pp.check_pack(two, w, strict=True).problems == []          # no register: a warning even when strict
    assert pp.check_pack(two, w, register=[{"lr_id": "LR-01"}, {"lr_id": "LR-02"}], strict=True).problems == []


def test_learning_id_shape(w):
    for bad in ("LR-1", "lr-01", "LR-01 ", 7):
        got = problems(pack_with(item("para", cites=["FND-0002"], learning=bad)), w)
        assert any(x.startswith("sections[0].items[0].learning: must be LR-") for x in got), (bad, got)
    bl = pack_with(item("para", cites=["FND-0002"]), bottom_line=[{"text": "t", "cites": ["FND-0002"], "learning": "LR-x"}])
    assert any(x.startswith("bottom_line[0].learning: must be LR-") for x in problems(bl, w))


def test_clauses_validated(w):
    ok = pack_with(item("para", cites=["FND-0002"], clauses=["ISO45001-10.2"]))
    r = pp.check_pack(ok, w, strict=True)
    assert r.problems == [] and not [x for x in r.warnings if "clause" in x], r
    unk = pack_with(item("para", cites=["FND-0002"], clauses=["ISO45001-99"]))
    r = pp.check_pack(unk, w)
    assert r.problems == [] and "sections[0].items[0].clauses[0]: unknown clause ISO45001-99" in r.warnings
    assert "sections[0].items[0].clauses[0]: unknown clause ISO45001-99" in pp.check_pack(unk, w, strict=True).problems
    for bad in ("ISO45001-10.2", [], [""], [3]):
        got = problems(pack_with(item("para", cites=["FND-0002"], clauses=bad)), w)
        assert any(x.startswith("sections[0].items[0].clauses") for x in got), (bad, got)
    t = pp.render_pack_html(w, ok, "r", "d")
    assert "Clauses: ISO45001-10.2" in t and "Clauses: ISO45001-10.2" in pp.render_pack_md(ok, w)


def test_comparator_refs_field_is_allowed(w):
    r = pp.check_pack(pack_with(item("para", cites=["FND-0002"], comparator_refs=["REC-01"])), w)
    assert r.problems == [] and not [x for x in r.warnings if "unknown field" in x], r


def test_test_point_clause_badge(w):
    p = pack_with(item("test_point", clause="ISO 45001 8.1.3; OSHA 1910.119(l)"))
    r = pp.check_pack(p, w)
    assert r.problems == [] and not [x for x in r.warnings if "unknown field" in x], r
    t = pp.render_pack_html(w, p, "r", "d")
    assert re.search(r'<span class="[^"]*\bpm-clause\b[^"]*">Clause: ISO 45001 8\.1\.3; OSHA 1910\.119\(l\)</span>', t)
    assert "Clause: ISO 45001 8.1.3; OSHA 1910.119(l)" in pp.render_pack_md(p, w)
    assert any(x.startswith("sections[0].items[0].clause: must be non-empty text")
               for x in problems(pack_with(item("test_point", clause="")), w))


def test_why_not_stronger_warning(w):
    msg = "recommendation {} is administrative or training only: say why_not_stronger"
    for tier in ("administrative", "Training of fitters"):
        r = pp.check_pack(pack_with(item("recommendation", hoc_tier=tier, id="r1")), w)
        assert r.problems == [] and any(x.endswith(msg.format("r1")) for x in r.warnings), r.warnings
    r = pp.check_pack(pack_with(item("recommendation", hoc_tier="training")), w)
    assert any(x.endswith(msg.format("s1-1")) for x in r.warnings), r.warnings
    p = pack_with(item("recommendation", hoc_tier="administrative", id="r1", barrier_id="BR-07",
                       why_not_stronger="The pump cannot be interlocked until the next shutdown."))
    r = pp.check_pack(p, w)
    assert r.problems == [] and not [x for x in r.warnings if "why_not_stronger" in x or "unknown field" in x], r
    assert not [x for x in pp.check_pack(pack_with(item("recommendation")), w).warnings if "why_not_stronger" in x]
    md, t = pp.render_pack_md(p, w), pp.render_pack_html(w, p, "r", "d")
    assert "- Why not stronger: The pump cannot be interlocked until the next shutdown." in md
    assert "- Barrier ID: BR-07" in md
    assert "Why not stronger" in t and "Barrier ID: BR-07" in t
    b = pack_with(item("barrier", barrier_id="CC-3"))
    assert pp.check_pack(b, w).problems == [] and "Barrier ID: CC-3" in pp.render_pack_md(b, w)
    assert any(x.startswith("sections[0].items[0].barrier_id: must be non-empty text")
               for x in problems(pack_with(item("barrier", barrier_id=" ")), w))


GAPS = [{"text": "No record shows who approved the local purchase.", "cites": ["FND-0003"],
         "evidence_needed": "The stores approval log for 2022 to 2024."}]


def test_gaps_validation(w):
    assert problems(pack_with(item("para", cites=["FND-0002"]), gaps=GAPS), w) == []
    for gaps, expected in [("x", "gaps: must be a non-empty list"), ([], "gaps: must be a non-empty list"),
                           (["x"], "gaps[0]: must be an object"),
                           ([{"evidence_needed": "e"}], "gaps[0].text: required"),
                           ([{"text": "t"}], "gaps[0].evidence_needed: required"),
                           ([{"text": "t", "evidence_needed": "e", "cites": "FND-0003"}], "gaps[0].cites: must be a list"),
                           ([{"text": "t", "evidence_needed": "e", "cites": ["FND-9999"]}],
                            "gaps[0].cites[0]: FND-9999 is not in this workspace")]:
        got = problems(pack_with(item("para", cites=["FND-0002"]), gaps=gaps), w)
        assert any(x.startswith(expected) for x in got), (gaps, got)


def test_gaps_box_and_gaps_json(tmp_path):
    ws_, outd = _fresh_run(tmp_path)
    w_ = pmlc.load_ws(ws_)
    a = pack_with(item("para", cites=["FND-0002"]), gaps=GAPS)
    t, md = pp.render_pack_html(w_, a, "r", "d"), pp.render_pack_md(a, w_)
    assert "<h2>Gaps in the evidence</h2>" in t and "The stores approval log for 2022 to 2024." in t
    assert "## Gaps in the evidence\n\n- No record shows who approved the local purchase. [FND-0003]" in md
    assert "Evidence needed: The stores approval log for 2022 to 2024." in md
    src = outd / "test-pack.json"
    src.write_text(json.dumps(a), encoding="utf-8")
    run("pack", str(ws_), str(src))
    gj = outd / "gaps.json"
    assert json.loads(gj.read_text(encoding="utf-8")) == {"gaps": [dict(GAPS[0], pack="test-pack")]}
    b = pack_with(item("para", cites=["FND-0002"]), pack="other-pack",
                  gaps=[{"text": "Shift log missing", "evidence_needed": "The night shift log"}])
    srcb = outd / "other-pack.json"
    srcb.write_text(json.dumps(b), encoding="utf-8")
    run("pack", str(ws_), str(srcb), "--out", str(tmp_path / "elsewhere"))   # gaps.json stays in the run's outputs
    got = json.loads(gj.read_text(encoding="utf-8"))["gaps"]
    assert [g["pack"] for g in got] == ["test-pack", "other-pack"] and got[1]["cites"] == []
    a["gaps"] = [{"text": "Replaced gap", "cites": [], "evidence_needed": "x"}]
    src.write_text(json.dumps(a), encoding="utf-8")
    run("pack", str(ws_), str(src))
    got = json.loads(gj.read_text(encoding="utf-8"))["gaps"]
    assert [(g["pack"], g["text"]) for g in got] == [("other-pack", "Shift log missing"), ("test-pack", "Replaced gap")]
    del a["gaps"]
    src.write_text(json.dumps(a), encoding="utf-8")
    run("pack", str(ws_), str(src))                                  # no gaps any more: its entries go
    assert [g["pack"] for g in json.loads(gj.read_text(encoding="utf-8"))["gaps"]] == ["other-pack"]


def test_pack_without_gaps_writes_no_gaps_json(tmp_path):
    ws_, outd = _fresh_run(tmp_path)
    src = outd / "test-pack.json"
    src.write_text(json.dumps(pack_with(item("para", cites=["FND-0002"]))), encoding="utf-8")
    run("pack", str(ws_), str(src))
    assert not (outd / "gaps.json").exists()


def test_limits_rendered(w):
    p = pack_with(item("para", cites=["FND-0002"]), limits=["The export has no maintenance history before 2022."])
    assert problems(p, w) == []
    t, md = pp.render_pack_html(w, p, "r", "d"), pp.render_pack_md(p, w)
    assert "<h2>Limits of this pack</h2>" in t and "<li>The export has no maintenance history before 2022.</li>" in t
    assert "## Limits of this pack\n\n- The export has no maintenance history before 2022." in md
    for bad in ("x", [], [""], [1]):
        got = problems(pack_with(item("para", cites=["FND-0002"]), limits=bad), w)
        assert any(x.startswith("limits") for x in got), (bad, got)


def test_learning_chip_rendered(w):
    p = pack_with(item("para", cites=["FND-0002"], learning="LR-01"))
    t = pp.render_pack_html(w, p, "r", "d")
    assert '<button type="button" class="pm-learning" data-lr="LR-01">Learning LR-01</button>' in t
    assert "*(learning: LR-01)*" in pp.render_pack_md(p, w)


def test_check_pack_register_flag(tmp_path):
    ws_, outd = _fresh_run(tmp_path)
    src = outd / "test-pack.json"
    src.write_text(json.dumps(pack_with(item("para", cites=["FND-0002"], learning="LR-99"))), encoding="utf-8")
    out = run("check-pack", str(ws_), str(src))
    assert "warning: learning ids not verified: no register" in out
    reg = tmp_path / "reg.json"
    reg.write_text(json.dumps(MINI_REGISTER), encoding="utf-8")
    out = run("check-pack", str(ws_), str(src), "--register", str(reg))
    assert "warning: sections[0].items[0].learning: unknown learning LR-99" in out
    (outd / "learnings-register.json").write_text(json.dumps(MINI_REGISTER), encoding="utf-8")   # auto-detected
    assert "unknown learning LR-99" in run("check-pack", str(ws_), str(src))
    r = run_fail("check-pack", str(ws_), str(src), "--register", str(tmp_path / "missing.json"))
    assert "(register):" in r.stderr and "missing.json" in r.stderr
    (outd / "learnings-register.json").write_text("{bad", encoding="utf-8")       # a broken auto-detected file
    out = run("check-pack", str(ws_), str(src))                                   # never blocks: warned, ignored
    assert "warning: (register):" in out and "ignored" in out and "learning ids not verified: no register" in out


def test_pack_schema_reference_covers_task_11():
    t = (ROOT / "skills" / "learnings-coach" / "references" / "pack-schema.md").read_text(encoding="utf-8")
    for f in ("`learning`", "`clauses`", "`comparator_refs`", "`why_not_stronger`", "`barrier_id`", "`clause`",
              "`gaps`", "`limits`", "gaps.json", "--register", "organisation-learning-plan", "dossier-index",
              "report-comparison-client-safe", "What check-pack does not check", "investigator-coach/SKILL.md"):
        assert f in t, f


@pytest.mark.parametrize("embed", ["cited", "summary"])
def test_gap_cites_are_embedded(w, embed):
    """Task 11 fix 2: a gap's citation buttons open their records (cited and summary embed cited records)."""
    p = pack_with(item("para", cites=["FND-0002"]),
                  gaps=[{"text": "t", "cites": ["FND-0004", "EVD-0003"], "evidence_needed": "e"}])
    d = _pack_data(pp.render_pack_html(w, p, "r", "d", embed=embed))
    assert "EVD-0003" in d["evidence"] and "FND-0004" in d["findings"]
    assert set(d["findings"]["FND-0004"]) != STUB_KEYS                    # a full record, not a label stub
    assert pp.coverage(w, p)["cited"] == 1                                 # gap cites still do not count
    assert pp.embedded_ids(p) == (["FND-0002", "FND-0004"], ["EVD-0003"])


# ----------------------------------------------------------------------------- Task 19: markdown escaping, ribbon

def _eh(status="approved", role="HSE manager"):
    return {"effective_status": status, "reviewer_role": role, "reviewed_on": "2026-10-19", "classification": "internal",
            "version": "1", "draft_reasons": [], "legal_review": "not set", "distribution": []}


def test_handling_lines_escape_the_reviewer_role_in_markdown_only():
    role = "HSE *lead* <b>[x]</b>"
    assert role in pmlc.handling_lines(_eh(role=role))[0]                      # HTML escapes it itself
    md = pmlc.handling_lines(_eh(role=role), markdown=True)[0]
    assert "HSE \\*lead\\* \\<b\\>\\[x\\]\\</b\\>" in md and role not in md


def test_markdown_pack_shows_the_escaped_reviewer(w):
    md = pp.render_pack_md(pack_with(item("para", cites=["FND-0001"])), w, eh=_eh(role="HSE *lead*"))
    assert "approved by HSE \\*lead\\* on 2026-10-19" in md


def test_html_pack_shows_the_reviewer_unescaped(w):
    t = pp.render_pack_html(w, pack_with(item("para", cites=["FND-0001"])), "r", "d", eh=_eh(role="HSE_lead <ops>"))
    assert "approved by HSE_lead &lt;ops&gt; on 2026-10-19" in t and "HSE\\_lead" not in t


def test_lint_ok_note_is_escaped_in_markdown(w):
    p = pack_with(item("para", text="The restart was unlawful.", cites=["FND-0001"],
                       lint_ok={"rule": "JC5", "reason": "quotes the *title* of <the> rule"}))
    md = pp.render_pack_md(p, w)
    assert "*Language check JC5 accepted: quotes the \\*title\\* of \\<the\\> rule*" in md


def test_reviewed_status_still_shows_the_ribbon(w):
    """A34: only an effective approval hides the DRAFT ribbon; a 'reviewed' document is not approved."""
    p = pack_with(item("para", cites=["FND-0001"]))
    for st, ribbon in (("reviewed", True), ("draft", True), ("approved", False)):
        page = pp.render_pack_html(w, p, "r", "d", eh=_eh(status=st))
        assert ('class="ribbon"' in page) is ribbon, st
    assert pmlc.is_draft(_eh("reviewed")) and not pmlc.is_draft(_eh("approved"))


def test_register_xlsx_about_column_a_fits_the_brand_line(ws, tmp_path):  # noqa: F811
    import openpyxl
    reg = tmp_path / "reg.json"
    reg.write_text(json.dumps(MINI_REG))
    out = tmp_path / "r.xlsx"
    run("register-xlsx", str(reg), "--ws", str(ws), "--out", str(out))
    about = openpyxl.load_workbook(out)["About"]
    longest = max(len(str(c.value)) for c in about["A"] if c.value)
    assert about.column_dimensions["A"].width >= min(longest, 200)


# ---- v2.0 phase 3, task 22: leadership, assurance and investigation fixtures carry register learnings (P3-12)

T22_AUDIENCE = ["board-brief", "top-management-brief", "site-leadership-coach", "manager-coach",
                "auditor-assurance-pack", "investigator-coach"]


@pytest.mark.parametrize("name", T22_AUDIENCE)
def test_t22_fixture_learning_ids_in_mini_register(w, name):
    p = fixture(name)
    ids = [x["learning"] for x in [*p.get("bottom_line", []), *(it for s in p["sections"] for it in s["items"])]
           if isinstance(x.get("learning"), str)]
    assert ids, f"{name}: no item carries a register learning"
    r = pp.check_pack(p, w, register=json.loads(MINI_REGISTER_FILE.read_text(encoding="utf-8")), strict=True)
    assert r.problems == [], r.problems
    assert not [x for x in r.warnings if "unknown learning" in x or "not verified" in x], r.warnings


def test_board_brief_follow_up_check_is_cited(w):
    """The board brief's `follow-up` check cites the findings behind the questions it tracks, so a board brief
    built to the SKILL.md table draws no uncited-item warning (integration fix, Ruling X35)."""
    p = fixture("board-brief")
    check = next(s for s in p["sections"] if s["id"] == "follow-up")["items"][0]
    assert check["kind"] == "check" and check["cites"]
    r = pp.check_pack(p, w, register=json.loads(MINI_REGISTER_FILE.read_text(encoding="utf-8")), strict=True)
    assert r.problems == [] and not [x for x in r.warnings if "no Finding or Evidence ID cited" in x], r.warnings


def test_p4h_coverage_warning_tells_top_rated_from_all_relevant(w):
    """Task 10 minor (M-3): 16 relevant findings, 2 of them top-rated. Citing both top-rated ones is under a quarter of
    the relevant findings (2 of 16) yet draws no warning; citing 8 lower-rated ones and neither top-rated one is half of
    them yet does."""
    import copy
    w2 = copy.deepcopy(w)
    base = next(f for f in w2["findings"] if f["id"] == "FND-0001")
    for n in range(5, 17):
        w2["findings"].append(dict(copy.deepcopy(base), id=f"FND-{n:04d}", rating=1))
    for f in w2["findings"]:
        f["rating"] = 3 if f["id"] in ("FND-0002", "FND-0003") else 1
    scope = {"levels": [1, 2, 3, 4]}
    rel = pp.relevant_findings(w2, scope)
    assert len(rel) == 16
    tops_only = pack_with(item("para", cites=["FND-0002", "FND-0003"]), scope=scope,
                          bottom_line=[{"text": "Test before service.", "cites": ["FND-0002"]}])
    assert pp.coverage(w2, tops_only)["cited"] == 2 and pp.coverage(w2, tops_only)["top_cited"] == 2
    assert not any(x.startswith("coverage") for x in pp.check_pack(tops_only, w2).warnings)
    lows = [f"FND-{n:04d}" for n in range(5, 13)]
    no_top = pack_with(item("para", cites=lows), scope=scope,
                       bottom_line=[{"text": "Test before service.", "cites": [lows[0]]}])
    assert pp.coverage(w2, no_top)["cited"] == 8 and pp.coverage(w2, no_top)["top_cited"] == 0
    assert any("under a quarter of the top-rated relevant findings are cited (0 of 2)" in x
               for x in pp.check_pack(no_top, w2).warnings)


def test_interview_plan_holds_six_roles_and_the_validation_question(w):
    """Final review m2 (T26 m2): the investigator-coach plan is up to six roles of five questions, plus the one
    question for validating the account; a full plan (31) passes --strict, one more does not."""
    roles = ["Stores officer", "Shift supervisor", "Maintenance planner", "Control room operator", "Area manager",
             "Contract crew lead"]
    pool = [["FND-0002"], ["FND-0003"], ["FND-0002", "EVD-0002"], ["FND-0003", "EVD-0003"], ["FND-0001", "FND-0002"]]
    qs = [{"kind": "question", "question": f"What did the {r.lower()} see at step {i + 1}?", "why": f"Reason {i} for {r}.",
           "to": r, "group": r, "cites": pool[i]} for r in roles for i in range(5)]
    qs.append({"kind": "question", "question": "Does this account match what you remember, before it is published?",
               "why": "Validation with the people involved.", "to": "Shift supervisor", "group": "Validation",
               "cites": ["FND-0002"]})
    p = fixture("investigator-coach")
    sec = next(s for s in p["sections"] if s["id"] == "interview-plan")
    sec["items"] = qs
    assert not [m for m in _strict(p, w) if m.startswith("section interview-plan")], _strict(p, w)
    sec["items"] = qs + [dict(qs[0], question="One question too many?")]
    assert "section interview-plan: 32 question items, expected 1-31" in _strict(p, w)
