"""Task 12 (Phase 6): the systemic-accimap skill. Its Hazira golden pack pastes the engine's AcciMap graph item and
levels table unchanged, carries the inferred-placements banner first, names every empty level (government included)
in `gaps`, asks a person to confirm each inferred level in `confirm`, and passes check-pack --strict with the register
and check-language with no errors."""
import json
import shutil

import pytest

from test_pmlc import ROOT, run, ws  # noqa: F401  (ws is a module-scoped fixture)
from pmlc_lib.pack.profiles import BANNERS

pytest.importorskip("openpyxl")
SKILL = "systemic-accimap"
SAMPLE = ROOT / "samples" / "2020-09-24-hazira-gas-release-fire"
EXPORT = SAMPLE / "2020-09-24-hazira-gas-release-fire_probematrix-findings.xlsx"
GOLDEN = SAMPLE / "outputs" / f"{SKILL}.json"
REGISTER = SAMPLE / "outputs" / "learnings-register.json"
FIXTURE = ROOT / "tests" / "fixtures" / "packs" / f"{SKILL}.json"


@pytest.fixture(scope="module")
def hz(tmp_path_factory):
    root = tmp_path_factory.mktemp("hazira-accimap")
    run("setup", str(EXPORT), "--slug", "hazira-gas-release-fire", "--date", "2020-09-24", "--root", str(root),
        "--overlay", "india-process-site")
    hw = root / "pmlc-runs" / "2020-09-24-hazira-gas-release-fire" / "workspace"
    run("accimap", str(hw))
    shutil.copy(REGISTER, hw.parent / "outputs" / REGISTER.name)
    shutil.copy(GOLDEN, hw.parent / "outputs" / GOLDEN.name)
    return hw


def _pack():
    return json.loads(GOLDEN.read_text(encoding="utf-8"))


def _section(pack, sid):
    return next(s for s in pack["sections"] if s["id"] == sid)


def test_manifest():
    m = json.loads((ROOT / "skills" / SKILL / "skill.json").read_text(encoding="utf-8"))
    assert (m["kind"], m["requires"], m["optional_inputs"]) == ("analysis", ["workspace", "accimap"], ["register"])
    assert (m["formats"], m["share_default"], m["embed_default"], m["since"]) == \
        (["docx", "pptx", "svg", "graphml"], "internal", "cited", "2.0.0")
    assert m["produces"]["pack"] == SKILL


def test_profile_entry():
    prof = json.loads((ROOT / "skills" / "learnings-coach" / "references" / "pack-profiles.json")
                      .read_text(encoding="utf-8"))[SKILL]
    got = [(s["id"], s["kinds"], s["min"], s["max"]) for s in prof["sections"]]
    assert got == [("banner", ["para"], 1, 1), ("map", ["graph"], 1, 1), ("levels", ["table"], 1, 1),
                   ("gaps", ["para"], 1, 2), ("learnings", ["learning"], 1, 5), ("confirm", ["question"], 1, 6)]
    assert prof["rules"] == ["no-owner-due", "inferred-banner"] and prof["bottom_line"] == {"min": 1, "max": 3}


def test_leadership_step_is_last_guarded():
    wf = json.loads((ROOT / "skills" / "learnings-coach" / "references" / "workflows.json")
                    .read_text(encoding="utf-8"))["leadership"]["steps"]
    assert wf[-1] == {"skill": SKILL, "when": "the user asks for patterns or latent conditions"}
    plan = json.loads((ROOT / "tests" / "fixtures" / "plans" / "leadership.json").read_text(encoding="utf-8"))
    assert [s["skill"] for s in plan["steps"][-2:]] == ["engine:accimap", SKILL]       # the engine step feeds it


def test_golden_pastes_engine_items(hz):
    pack = _pack()
    graph = dict(_section(pack, "map")["items"][0])
    assert graph.pop("lint_ok")["rule"] == "JC3"                                   # code names quoted verbatim
    assert graph == json.loads(run("accimap", str(hz), "--graph-item"))          # pasted whole, never retyped
    table = _section(pack, "levels")["items"][0]
    assert table == json.loads(run("accimap", str(hz), "--table-item", "levels"))
    am = json.loads((hz / "accimap.json").read_text(encoding="utf-8"))
    assert am["gaps"] == [1, 2]                                                    # Hazira: government and regulators


def test_golden_banner_gaps_and_confirm(hz):
    pack = _pack()
    banner = _section(pack, "banner")["items"]
    assert [it["text"] for it in banner] == [BANNERS["accimap-inferred"]] and "cites" not in banner[0]
    am = json.loads((hz / "accimap.json").read_text(encoding="utf-8"))
    gaps = " ".join(it["text"] for it in _section(pack, "gaps")["items"])
    for g in am["gaps"]:
        assert f"level {g}" in gaps.lower() and am["levels"][str(g)]["name"] in gaps, g
    assert "Government" in gaps
    inferred = [k for k, lv in am["levels"].items() if lv["inferred"]]
    qs = " ".join(it["question"] for it in _section(pack, "confirm")["items"])
    for k in inferred:
        assert f"level {k}" in qs.lower(), k                                       # each inferred level is confirmed
    assert all(not it.get("owner") and not it.get("by_when") for s in pack["sections"] for it in s["items"])
    assert all(it.get("cites") for s in pack["sections"] if s["id"] != "banner" for it in s["items"])


def test_golden_learnings_carry_register_ids():
    reg = {e["lr_id"] for e in json.loads(REGISTER.read_text(encoding="utf-8"))["entries"]}
    ls = _section(_pack(), "learnings")["items"]
    assert 1 <= len(ls) <= 5 and all(it.get("learning") in reg for it in ls)


def test_golden_passes_strict_and_language(hz):
    out = run("check-pack", str(hz), str(hz.parent / "outputs" / GOLDEN.name), "--strict", "--register", str(REGISTER))
    assert "OK:" in out and "problem" not in out, out                 # run() also asserts exit 0
    lang = run("check-language", str(hz), str(hz.parent / "outputs" / GOLDEN.name))
    assert "check-language: 0 errors" in lang, lang


def test_fixture_needs_the_banner(tmp_path):
    """The synthetic fixture has inferred nodes, so dropping its banner is a problem even without --strict."""
    from pmlc_lib.pack import profiles
    pack = json.loads(FIXTURE.read_text(encoding="utf-8"))
    prof = profiles.load()[SKILL]
    assert profiles.hard(pack, prof) == []
    pack["sections"] = [s for s in pack["sections"] if s["id"] != "banner"]
    assert any(m.startswith("inferred-banner:") for m in profiles.hard(pack, prof))


def test_standalone_graph_files_mark_inferred(ws, tmp_path):  # noqa: F811
    """Final review I2 (spec §6.2): the stand-alone SVG and GraphML mark each inferred node, and carry the inferred
    banner in their <desc>, so a map pasted on its own still says its upper placements are inferred."""
    import re
    pack = json.loads(FIXTURE.read_text(encoding="utf-8"))
    graph = next(it for s in pack["sections"] for it in s["items"] if it.get("kind") == "graph")
    inferred = [n for n in graph["nodes"] if n.get("inferred") is True]
    plain = [n for n in graph["nodes"] if n.get("inferred") is not True]
    assert inferred and plain
    p = tmp_path / f"{SKILL}.json"
    p.write_text(json.dumps(pack), encoding="utf-8")
    out = tmp_path / "out"
    run("pack", str(ws), str(p), "--out", str(out), "--format", "svg,graphml")
    svg = (out / f"{SKILL}.{graph['id']}.svg").read_text(encoding="utf-8")
    gml = (out / f"{SKILL}.{graph['id']}.graphml").read_text(encoding="utf-8")
    banner = BANNERS["accimap-inferred"]
    for text in (svg, gml):
        desc = re.search(r"<desc>(.*?)</desc>", text, re.S).group(1)
        assert desc.startswith(banner), desc
    assert svg.count("(inferred)") >= len(inferred)
    assert '<key id="inferred" for="node" attr.name="inferred" attr.type="boolean">' in gml
    for n in inferred:
        node = re.search(rf'<node id="{re.escape(n["id"])}">(.*?)</node>', gml).group(1)
        assert '<data key="inferred">true</data>' in node and "(inferred)" in node, node
    for n in plain:
        node = re.search(rf'<node id="{re.escape(n["id"])}">(.*?)</node>', gml).group(1)
        assert "inferred" not in node, node
