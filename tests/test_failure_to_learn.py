"""Phase 5 Task 16: the failure-to-learn-review skill. Its manifest and profile (knowable-then; JC3 and JC4 as errors),
the five-phase learning-cycle table, and the rule that every `learnings` item cites at least one level-4 finding, on
the synthetic fixture and on the Hazira golden pack."""
import copy
import json

import pytest

from test_pmlc import ROOT, run, run_fail, ws  # noqa: F401  (ws is a module-scoped fixture)
import pmlc  # noqa: E402
import pmlc_pack as pp  # noqa: E402
from pmlc_lib.pack import profiles  # noqa: E402

SKILL = "failure-to-learn-review"
FIX = ROOT / "tests" / "fixtures" / "packs" / f"{SKILL}.json"
SAMPLE = ROOT / "samples" / "2020-09-24-hazira-gas-release-fire"
GOLDEN = SAMPLE / "outputs" / f"{SKILL}.json"
REGISTER = SAMPLE / "outputs" / "learnings-register.json"
# Drupsteen's five-phase learning-from-incidents cycle, in order (plan, Task 16)
PHASES = ["Reporting", "Investigation and analysis", "Planning interventions", "Intervening", "Evaluating"]


def load(p):
    return json.loads(p.read_text(encoding="utf-8"))


def items(pack, sid=None, kind=None):
    return [it for s in pack["sections"] if sid in (None, s["id"]) for it in s["items"]
            if kind in (None, it["kind"])]


def levels(ws_dir) -> dict:  # noqa: F811
    return {f["id"]: f["level"] for f in load(ws_dir / "findings.json")}


@pytest.fixture(scope="module")
def w(ws):  # noqa: F811
    return pmlc.load_ws(ws)


@pytest.fixture(scope="module")
def hz(tmp_path_factory):
    pytest.importorskip("openpyxl")
    root = tmp_path_factory.mktemp("ftl-hazira")
    run("setup", str(SAMPLE / "2020-09-24-hazira-gas-release-fire_probematrix-findings.xlsx"), "--slug",
        "hazira-gas-release-fire", "--date", "2020-09-24", "--root", str(root), "--overlay", "india-process-site")
    return root / "pmlc-runs" / "2020-09-24-hazira-gas-release-fire" / "workspace"


def test_manifest():
    m = load(ROOT / "skills" / SKILL / "skill.json")
    assert (m["kind"], m["audiences"], m["scope"]["levels"]) == ("analysis", [], [3, 4])
    assert m["requires"] == ["workspace", "timeline", "missed-opportunities"]
    assert m["optional_inputs"] == ["register"]
    assert (m["formats"], m["share_default"], m["embed_default"], m["since"]) == (["docx", "pptx"], "internal",
                                                                                   "cited", "2.0.0")
    assert m["produces"]["pack"] == SKILL


def test_profile():
    prof = profiles.load()[SKILL]
    got = [(s["id"], s["kinds"], s["min"], s["max"]) for s in prof["sections"]]
    assert got == [("cycle", ["table"], 1, 1), ("missed", ["timeline"], 1, 1), ("drift", ["para"], 1, 3),
                   ("learnings", ["learning"], 1, 6), ("hindsight", ["para"], 1, 1)]
    assert prof["bottom_line"] == {"min": 1, "max": 5}
    assert prof["rules"] == ["knowable-then"] and prof["lint_errors"] == ["JC3", "JC4"]


def check_cycle(pack):
    (table,) = items(pack, "cycle", "table")
    assert table["columns"] == ["Phase", "What the export shows"]       # the renderer adds the Cites column
    assert [r[0] for r in table["rows"]] == PHASES
    assert len(table["row_cites"]) == 5


def check_learnings_cite_level_4(pack, level_of):
    learnings = items(pack, "learnings", "learning")
    assert learnings
    for it in learnings:
        assert any(level_of.get(c) == 4 for c in it["cites"]), f"{it['lesson']}: cites no level-4 finding"


def test_fixture_cycle_and_level_4(ws):  # noqa: F811
    pack = load(FIX)
    check_cycle(pack)
    check_learnings_cite_level_4(pack, levels(ws))


def test_level_4_check_catches_a_lower_level_learning(ws):  # noqa: F811
    pack = load(FIX)
    items(pack, "learnings", "learning")[0]["cites"] = ["FND-0002"]   # level 3 only
    with pytest.raises(AssertionError, match="cites no level-4 finding"):
        check_learnings_cite_level_4(pack, levels(ws))


def test_fixture_passes_strict(w):
    r = pp.check_pack(load(FIX), w, strict=True)
    assert r.problems == [], r.problems


def test_hindsight_wording_is_an_error_here(w):
    """JC3 and JC4 are errors in this pack (P5-5), even without --strict; elsewhere they stay warnings."""
    pack = load(FIX)
    items(pack, "learnings", "learning")[0]["explanation"] = "The supervisor failed to escalate the repeat leak."
    assert [x for x in pp.check_pack(pack, w).problems if "JC3" in x]
    pack = load(FIX)
    items(pack, "drift", "para")[0]["text"] = "It was obviously unsafe."
    assert [x for x in pp.check_pack(pack, w).problems if "JC4" in x]
    other = copy.deepcopy(pack)
    other["pack"] = "precursor-timeline"
    assert not [x for x in pp.check_pack(other, w).problems if "JC4" in x]


def test_event_without_knowable_then_fails_strict(w):
    pack = load(FIX)
    items(pack, "missed", "timeline")[0]["events"][0].pop("knowable_then")
    assert [x for x in pp.check_pack(pack, w, strict=True).problems if "knowable_then" in x]


def test_check_language_escalates_for_this_pack(ws, tmp_path):  # noqa: F811
    pack = load(FIX)
    items(pack, "drift", "para")[0]["text"] = "The repeat leak should have been escalated."
    f = tmp_path / f"{SKILL}.json"
    f.write_text(json.dumps(pack), encoding="utf-8")
    r = run_fail("check-language", str(ws), str(f))
    assert "JC3" in r.stdout + r.stderr


def test_hazira_golden(hz):
    pack = load(GOLDEN)
    assert pack["pack"] == pack["skill"] == SKILL and "handling" not in pack
    check_cycle(pack)
    check_learnings_cite_level_4(pack, levels(hz))
    (tl,) = items(pack, "missed", "timeline")
    assert tl["events"] and all("knowable_then" in e for e in tl["events"])
    out = run("check-pack", str(hz), str(GOLDEN), "--strict", "--register", str(REGISTER))
    assert "OK:" in out, out
    lang = run("check-language", str(hz), str(GOLDEN))
    assert "check-language: 0 errors" in lang, lang


def test_render_pending_only_names_unrendered_packs():
    """The Phase 5 staging set (pmlc_lib.samples.RENDER_PENDING) cannot hide a rendered or missing pack: each entry is
    a pack JSON in the Hazira outputs with no HTML and no MD yet. Task 24 rendered them and emptied the set."""
    from pmlc_lib.samples import RENDER_PENDING, sample_folder_problems
    out = SAMPLE / "outputs"
    assert f"{SKILL}.json" not in RENDER_PENDING and (out / f"{SKILL}.html").is_file()     # Task 24 rendered it
    for name in RENDER_PENDING:
        stem = name[: -len(".json")]
        assert "pack" in load(out / name), name
        assert not (out / f"{stem}.html").exists() and not (out / f"{stem}.md").exists(), name
    assert sample_folder_problems(ROOT / "samples") == []
