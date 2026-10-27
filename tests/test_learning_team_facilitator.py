"""Phase 6 Task 10: the learning-team-facilitator skill (interactive, P6-2). Its manifest and profile (banner
learning-team; JC3 and JC4 as errors), the session plan whose minutes add up to 60-90, prompts that are questions,
facilitator notes that follow Conklin, the guarded investigation-quality step, and the Hazira golden pack."""
import copy
import json

import pytest

from test_pmlc import ROOT, run, run_fail, ws  # noqa: F401  (ws is a module-scoped fixture)
import pmlc  # noqa: E402
import pmlc_pack as pp  # noqa: E402
from pmlc_lib.pack import profiles  # noqa: E402

SKILL = "learning-team-facilitator"
FIX = ROOT / "tests" / "fixtures" / "packs" / f"{SKILL}.json"
SAMPLE = ROOT / "samples" / "2020-09-24-hazira-gas-release-fire"
GOLDEN = SAMPLE / "outputs" / f"{SKILL}.json"
REGISTER = SAMPLE / "outputs" / "learnings-register.json"
REFS = ROOT / "skills" / "learnings-coach" / "references"
PLAN_COLUMNS = ["Minutes", "Activity", "Purpose"]


def load(p):
    return json.loads(p.read_text(encoding="utf-8"))


def items(pack, sid=None, kind=None):
    return [it for s in pack["sections"] if sid in (None, s["id"]) for it in s["items"]
            if kind in (None, it["kind"])]


@pytest.fixture(scope="module")
def w(ws):  # noqa: F811
    return pmlc.load_ws(ws)


@pytest.fixture(scope="module")
def hz(tmp_path_factory):
    pytest.importorskip("openpyxl")
    root = tmp_path_factory.mktemp("ltf-hazira")
    run("setup", str(SAMPLE / "2020-09-24-hazira-gas-release-fire_probematrix-findings.xlsx"), "--slug",
        "hazira-gas-release-fire", "--date", "2020-09-24", "--root", str(root), "--overlay", "india-process-site")
    w = root / "pmlc-runs" / "2020-09-24-hazira-gas-release-fire" / "workspace"
    run("wai-wad", str(w))
    return w


def test_manifest():
    m = load(ROOT / "skills" / SKILL / "skill.json")
    assert (m["kind"], m["interactive"], m["audiences"]) == ("interactive", True, [])
    assert m["requires"] == ["workspace", "wai-wad"] and m["optional_inputs"] == ["register"]
    assert (m["formats"], m["share_default"], m["embed_default"], m["since"]) == (["docx"], "internal", "cited",
                                                                                   "2.0.0")
    assert m["produces"]["pack"] == SKILL
    qs = m["questions"]
    assert len(qs) == 2
    assert qs[0].startswith("What is the session's scope?") and "cluster" in qs[0] and "activity" in qs[0]
    assert qs[1].startswith("Who will be in the room") and "roles only" in qs[1]


def test_profile():
    prof = profiles.load()[SKILL]
    got = [(s["id"], s["kinds"], s["min"], s["max"]) for s in prof["sections"]]
    assert got == [("banner", ["para"], 1, 1), ("wai-wad", ["table"], 1, 1), ("prompts", ["question"], 4, 12),
                   ("session-plan", ["table"], 1, 1), ("facilitator-notes", ["check"], 3, 6)]
    assert prof["bottom_line"] == {"min": 1, "max": 3}
    assert prof["rules"] == ["no-owner-due", "banner:learning-team"]
    assert prof["lint_errors"] == ["JC3", "JC4"]


def minutes(pack) -> int:
    (table,) = items(pack, "session-plan", "table")
    assert table["columns"] == PLAN_COLUMNS
    assert all(len(r) == 3 and str(r[0]).isdigit() for r in table["rows"]), table["rows"]
    return sum(int(r[0]) for r in table["rows"])


def check_session_plan(pack):
    total = minutes(pack)
    assert 60 <= total <= 90, f"the session plan adds up to {total} minutes, not 60-90"


def check_shape(pack):
    (banner,) = items(pack, "banner", "para")
    assert banner["text"] == profiles.BANNERS["learning-team"]
    check_session_plan(pack)
    prompts = items(pack, "prompts")
    assert prompts and all(it["kind"] == "question" and it["cites"] for it in prompts)
    assert not [it for it in items(pack) if it.get("owner") or it.get("by_when")]


def test_fixture_shape_and_strict(w):
    pack = load(FIX)
    check_shape(pack)
    r = pp.check_pack(pack, w, strict=True)
    assert r.problems == [], r.problems


@pytest.mark.parametrize("rows,ok", [([["30", "a", "b"], ["30", "c", "d"]], True),
                                     ([["45", "a", "b"], ["45", "c", "d"]], True),
                                     ([["20", "a", "b"], ["30", "c", "d"]], False),
                                     ([["60", "a", "b"], ["40", "c", "d"]], False)])
def test_session_plan_minutes_add_up_to_60_to_90(rows, ok):
    pack = load(FIX)
    items(pack, "session-plan", "table")[0]["rows"] = rows
    if ok:
        check_session_plan(pack)
    else:
        with pytest.raises(AssertionError, match="adds up to"):
            check_session_plan(pack)


def test_banner_is_required(w):
    pack = load(FIX)
    items(pack, "banner", "para")[0]["text"] = "Questions for the team."
    assert [x for x in pp.check_pack(pack, w).problems + pp.check_pack(pack, w, strict=True).problems
            if "learning-team" in x or "banner" in x]


def test_owner_is_refused(w):
    pack = load(FIX)
    items(pack, "facilitator-notes", "check")[0]["owner"] = "Shift supervisor"
    assert [x for x in pp.check_pack(pack, w).problems if "owner" in x]


def test_hindsight_wording_is_an_error_here(w):
    """JC3 and JC4 are errors in this pack (P5-5), even without --strict; elsewhere they stay warnings."""
    pack2 = load(FIX)
    items(pack2, "prompts", "question")[0]["question"] = "The operator should have tested the seal: why not?"
    assert [x for x in pp.check_pack(pack2, w).problems if "JC3" in x]
    pack3 = load(FIX)
    items(pack3, "facilitator-notes", "check")[0]["text"] = "It was obviously unsafe, so start there."
    assert [x for x in pp.check_pack(pack3, w).problems if "JC4" in x]
    other = copy.deepcopy(pack3)
    other["pack"] = "supervisor-coach"
    assert not [x for x in pp.check_pack(other, w).problems if "JC4" in x]


def test_check_language_escalates_for_this_pack(ws, tmp_path):  # noqa: F811
    pack = load(FIX)
    items(pack, "facilitator-notes", "check")[0]["text"] = "Ask why the crew should have stopped the job."
    f = tmp_path / f"{SKILL}.json"
    f.write_text(json.dumps(pack), encoding="utf-8")
    r = run_fail("check-language", str(ws), str(f))
    assert "JC3" in r.stdout + r.stderr


def test_conklin_is_in_the_principles():
    text = (REFS / "learning-principles.md").read_text(encoding="utf-8")
    line = next((x for x in text.splitlines() if "Conklin" in x), "")
    assert "learning team" in line.lower() and "unverified" in line and SKILL in text


def test_workflow_step_is_guarded_after_investigator_coach():
    steps = load(REFS / "workflows.json")["investigation-quality"]["steps"]
    names = [s["skill"] for s in steps]
    assert names.index(SKILL) > names.index("investigator-coach")
    (step,) = [s for s in steps if s["skill"] == SKILL]
    assert step == {"skill": SKILL, "when": "the user asks for a learning team or work-as-done session"}


def test_hazira_golden(hz):
    pack = load(GOLDEN)
    assert pack["pack"] == pack["skill"] == SKILL and "handling" not in pack
    check_shape(pack)
    ww = load(hz / "wai_wad.json")
    gap_codes = {g["code"] for g in ww["gaps"]}
    (table,) = items(pack, "wai-wad", "table")
    assert table["rows"] and {r[0] for r in table["rows"]} <= gap_codes      # rows from the engine's gaps table
    counterfactual = set(ww["counterfactual"])
    for q in items(pack, "prompts"):
        assert set(q["cites"]) & counterfactual, q["question"]               # each prompt is from --items prompts
        assert q["question"].startswith("What made sense at the time"), q["question"]
    out = run("check-pack", str(hz), str(GOLDEN), "--strict", "--register", str(REGISTER))
    assert "OK:" in out, out
    lang = run("check-language", str(hz), str(GOLDEN))
    assert "check-language: 0 errors" in lang, lang


def test_golden_is_render_pending():
    """Phase 6 checklist item 6: the golden lands as JSON only; Task 18 renders it."""
    from pmlc_lib.samples import RENDER_PENDING
    out = SAMPLE / "outputs"
    assert f"{SKILL}.json" in RENDER_PENDING
    assert not (out / f"{SKILL}.html").exists() and not (out / f"{SKILL}.md").exists()
